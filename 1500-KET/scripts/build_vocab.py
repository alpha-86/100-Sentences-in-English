# -*- coding: utf-8 -*-
"""build_vocab.py — 合并主表+补词，清洗翻译/音标，产出 1500-KET.csv。

数据源：
  ket-mainlist-v2.csv  主表（parse_main_list.py 输出，PDF 权威词性）
  additions.tsv        补词（Appendix 词族/主题词/兜底词，人工 curated 中文）
  overrides.tsv        人工定稿表（plan Step 4b，5 批 review 全量逐条修正）
  KET词汇表.csv        v1（借其音标列；翻译列仅作兜底）
  stardict.csv         ECDICT 英汉词典（按词性选义项）

翻译流水线（plan Step 4a）：
  1. ECDICT 多行翻译按词条词性选义项行（n & v 优先 n 行再 v 行）
  2. 去掉词典体前缀 n. / a. / adv. 与 [计][医][法] 等领域标签
  3. 义项黑名单过滤（成人/不适义项）
  4. 行间轮转取义（每行先取第 1 义）、去重、每词最多 3 个义项
  5. overrides.tsv 人工定稿覆盖
音标：ECDICT 取，西里尔符号映射清洗，单数回退，短语合成，手工补充。
"""
import csv, re, sys
from itertools import zip_longest

def load_overrides(path='overrides.tsv'):
    ov = {}
    for l in open(path, encoding='utf-8'):
        if l.strip() and not l.startswith('#'):
            w, cn = l.rstrip('\n').split('\t')
            ov[w] = cn
    return ov

OVERRIDE = load_overrides()

# PDF 源文件自身的词性笔误修正（review 发现）
POS_FIX = {
    'first name': 'n',      # PDF 误作 (adj)
    'left hand': 'n',       # PDF 误作 (adj)
    'make up': 'phr v',     # PDF 作 (n)，KET 常用作短语动词
    'point': 'n & v',       # PDF 只标 (v)
}

# 音标人工补充（ECDICT 缺失/不合适的词与短语，优先合成，合成不了的手工给）
MANUAL_PHON = {
    'pen-friend': "/'pen frend/",
    'table-tennis': "/'teɪbəl tenɪs/",
    'CD': '/ˌsiː ˈdiː/',
    'DVD': '/ˌdiː viː ˈdiː/',
    'New Year': '/ˌnjuː ˈjɪə/',
    'a.m.': '/ˌeɪ ˈem/',
    'p.m.': '/ˌpiː ˈem/',
    'MP3': '/ˌem piː θriː/',
    'bored': '/bɔ:d/',
    'congratulations': '/kənˌɡrætʃʊˈleɪʃnz/',
    'crossroads': '/ˈkrɒsrəʊdz/',
    'download': '/ˌdaʊnˈləʊd/',
    'granddad': '/ˈɡrændæd/',
    'instructions': '/ɪnˈstrʌkʃnz/',
    'laptop': '/ˈlæptɒp/',
    'online': '/ˌɒnˈlaɪn/',
    'theatre': '/ˈθɪətə/',
    'website': '/ˈwebsaɪt/',
    'milkshake': '/ˈmɪlkʃeɪk/',
    'surfboarding': '/ˈsɜ:fbɔ:dɪŋ/',
}

# 义项黑名单（命中即删除该义项）
BLACKLIST = ['性爱', '尸体', '赌博', '枪击', '政治权力', '痛饮', '性交', '春药',
             '阴茎', '阴道', '嫖', '妓', '乳房', '乳头', '堕胎', '避孕', '裸',
             '淫', '赌注', '海洛因', '可卡因', '吗啡', '自杀', '死刑']

TAG_RE = re.compile(r"^((?:[a-z]+(?: [a-z]+)?\.\s*)+)")   # 词典体前缀: n. / vt. / modal v. ...
NET_RE = re.compile(r"^\[网络\]")
DOM_RE = re.compile(r"\[[^\]]*\]")                         # 领域标签 [计] [医] [法] [俚] ...

TAGMAP = {  # 词条词性 -> ECDICT 行首标签
    'n': ['n.', 'pl.'], 'v': ['v.', 'vt.', 'vi.'],
    'adj': ['a.', 'adj.'], 'adv': ['ad.', 'adv.'],
    'prep': ['prep.'], 'conj': ['conj.'], 'pron': ['pron.'],
    'art': ['art.'], 'exclam': ['exclam.', 'int.'], 'num': ['num.'],
    'det': ['det.'], 'phr': ['phr.'],
}

# '^' 是 ECDICT 源里少数词条 g 的坏字（grandchild/granddaughter/grandpa/photographer/
# reggae/schoolbag 共 6 例），原样输出会在 PDF 里显示成非 IPA 符号，统一并回 g。
IPA_FIX = {'ә': 'ə', 'є': 'e', 'ӕ': 'æ', '：': ':', 'ː': ':', 'ɡ': 'g', '^': 'g'}

def fix_ipa(p):
    for a, b in IPA_FIX.items():
        p = p.replace(a, b)
    return p.replace('ə:', 'ɜ:')

def clean_translation(text, pos):
    """按词性选行 -> 去前缀/标签 -> 黑名单过滤 -> 去重 -> 最多 3 个义项"""
    if not text:
        return ''
    lines = [l.strip() for l in text.split('\\n') if l.strip()]
    lines = [l for l in lines if not NET_RE.match(l)]
    # 解析每行的标签
    parsed, untagged = [], []
    for l in lines:
        m = TAG_RE.match(l)
        if m:
            tags = [t.strip() for t in m.group(1).split() if t.strip().endswith('.')]
            parsed.append((tags, TAG_RE.sub('', l).strip()))
        else:
            untagged.append(l)
    # 词条词性组件，按序取标签
    comps = [c.strip() for c in re.split(r'[&,,]', pos) if c.strip()]
    if pos == 'phr v':
        comps = ['v']
    wanted = []
    for c in comps:
        wanted.extend(TAGMAP.get(c, []))
    selected = []
    for tag in wanted:                       # 按主词性优先收集
        for tags, cn in parsed:
            if tag in tags and (tags, cn) not in selected:
                selected.append((tags, cn))
    if not selected and untagged:
        selected = [([], l) for l in untagged]
    if not selected:                         # 兜底：优先无领域标签的行
        clean = [(t, c) for t, c in parsed if not DOM_RE.search(c)]
        selected = clean if clean else parsed + [([], l) for l in untagged]
    # 每行拆义项，行间轮转取义（每行第 1 义优先），黑名单过滤
    per_line = []
    for _, cn in selected:
        cn = DOM_RE.sub('', cn)              # 删 [计] 类标签
        ss = []
        for s in re.split(r'[,，;；]', cn):
            s = s.strip().strip('.').strip()
            if not s or any(b in s for b in BLACKLIST):
                continue
            ss.append(s)
        per_line.append(ss)
    senses = []
    for grp in zip_longest(*per_line):
        for s in grp:
            if s and s not in senses:
                senses.append(s)
            if len(senses) >= 3:
                break
        if len(senses) >= 3:
            break
    return ', '.join(senses[:3])

def load_stardict(path):
    dic = {}
    with open(path, encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            w = row['word'].lower()
            if w not in dic:                 # 保留首条（词频最高）
                dic[w] = row
    return dic

def lookup(dic, word):
    cands = [word.lower(),
             re.sub(r'\(.*?\)', '', word.lower()).strip(),
             re.split(r'[,/]', word.lower())[0].strip(),
             word.lower().replace(' ', '-'),          # online -> on-line
             word.lower().replace('-', ' ')]
    for c in cands:
        if c in dic:
            return dic[c]
    return None

def phon_of(dic, word):
    """单词音标：ECDICT -> 单数回退(-s/-ies) -> 手工表。取第一个备选（分号截断）。"""
    if word in MANUAL_PHON:
        return MANUAL_PHON[word]
    e = lookup(dic, word)
    if e and e.get('phonetic'):
        return fix_ipa(e['phonetic'].strip().split(';')[0].split(';')[0].strip())
    VOICE_END = 'bdgvðzʒmnŋlrəɜʌɒɑɔɪʊiuæe'
    for singular in ([word[:-3] + 'y'] if word.endswith('ies') and len(word) > 3 else []) + \
                    ([word[:-1]] if word.endswith('s') and len(word) > 3 else []):
        e = lookup(dic, singular)
        if e and e.get('phonetic'):
            ph = fix_ipa(e['phonetic'].strip().split(';')[0].strip())
            if singular != word and word.endswith('s'):
                tail = ph[-2] if ph[-1] == ':' and len(ph) > 1 else ph[-1]
                ph += 'z' if tail in VOICE_END else 's'
            return ph
    return None

def synth_phrase_phon(dic, word):
    """短语音标合成：按空格/连字符拆词，逐词取音标拼接。"""
    parts = [p for p in re.split(r'[\s\-]+', word) if p]
    if len(parts) < 2:
        return None
    phons = []
    for p in parts:
        ph = phon_of(dic, p)
        if not ph:
            return None
        phons.append(ph.strip('/'))
    return '/' + ' '.join(phons) + '/'

def main():
    rows_v1 = {}
    with open('KET词汇表.csv', encoding='utf-8-sig', newline='') as f:
        for r in csv.reader(f):
            rows_v1[r[0].strip()] = (r[1].strip(), r[3].strip())

    main_list = []
    with open('ket-mainlist-v2.csv', encoding='utf-8', newline='') as f:
        for r in csv.reader(f):
            if r[0] != 'word':
                w, p = r[0].strip(), r[1].strip()
                main_list.append((w, POS_FIX.get(w, p)))

    additions = []
    for l in open('additions.tsv', encoding='utf-8'):
        if l.strip() and not l.startswith('#'):
            w, p, cn = l.rstrip('\n').split('\t')
            additions.append((w, p, cn))

    dic = load_stardict('stardict.csv')

    # 手工增补：at the same time（v1 有、官方例句短语，保留并修翻译）
    extra = [('at the same time', 'adv', OVERRIDE.get('at the same time', '同时'))]
    allwords = main_list + additions + extra

    # 去重检查
    seen, dups = set(), []
    for w, *_ in allwords:
        if w in seen:
            dups.append(w)
        seen.add(w)
    if dups:
        sys.exit(f'重复词条: {dups}')

    out, missing_phon, fallback_cn = [], [], []
    for w, pos, *cn_curated in allwords:
        curated = cn_curated[0] if cn_curated else None
        entry = lookup(dic, w)
        # 音标
        phon = ''
        if entry and entry.get('phonetic'):
            phon = '/' + fix_ipa(entry['phonetic'].strip()) + '/'
        elif not phon:
            ph = phon_of(dic, w)             # 手工表 + 单数回退
            phon = '/' + ph + '/' if ph and not ph.startswith('/') else (ph or '')
        if not phon:
            ph = synth_phrase_phon(dic, w)   # 短语合成
            phon = ph or ''
        if not phon and w in rows_v1 and rows_v1[w][0]:
            phon = fix_ipa(rows_v1[w][0])
        if not phon and w not in {'CD', 'DVD'}:
            missing_phon.append(w)
        # 中文
        if curated is not None:
            cn = curated
        elif w in OVERRIDE:
            cn = OVERRIDE[w]
        else:
            src = entry.get('translation', '') if entry else ''
            cn = clean_translation(src, pos)
            if not cn and w in rows_v1:
                cn = clean_translation(rows_v1[w][1].replace(', ', '\\n'), pos)
            if not cn:
                fallback_cn.append(w)
                cn = '【待补】'
        cn = cn.replace(', ', '，')            # 统一义项分隔符为全角逗号
        out.append((w, phon, pos, cn))

    # 排序：字母序（忽略大小写与非字母），稳定
    out.sort(key=lambda r: re.sub(r'[^a-z0-9]', '', r[0].lower()))

    with open('../1500-KET.csv', 'w', newline='', encoding='utf-8-sig') as f:
        wtr = csv.writer(f, lineterminator='\n')
        wtr.writerow(['英文', '音标', '词性', '中文'])
        wtr.writerows(out)
    print(f'共 {len(out)} 词 -> 1500-KET.csv')
    print(f'缺音标 {len(missing_phon)}: {missing_phon}')
    print(f'翻译待补 {len(fallback_cn)}: {fallback_cn}')

if __name__ == '__main__':
    main()
