# -*- coding: utf-8 -*-
"""从 ket.pdf 重新解析 KET 主字母表词条（栏位感知 + 例句过滤 + 形态规范化）。

输出: ket-mainlist-v2.csv  (word, pos)  —— 无音标/中文，骨架文件
"""
import re, csv, sys
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextLine

BULLET = ''  #  私有区子弹符

def walk(obj):
    yield obj
    for c in getattr(obj, '__iter__', lambda: iter([]))():
        yield from walk(c)

def page_lines(page):
    out = []
    for el in walk(page):
        if isinstance(el, LTTextLine):
            t = el.get_text().strip()
            if t:
                out.append((el.x0, el.y0, t))
    return out

def extract_ordered(path):
    buf = []
    for page in extract_pages(path):
        ls = page_lines(page)
        left = sorted((l for l in ls if l[0] < 300), key=lambda v: -v[1])
        right = sorted((l for l in ls if l[0] >= 300), key=lambda v: -v[1])
        buf.extend(l[2] for l in left)
        buf.extend(l[2] for l in right)
    return buf

# ---------- 过滤规则 ----------
# 大写开头的真实词条白名单（其余大写开头行 = 例句）
UPPER_OK = {'CD', 'CD player', 'DVD', 'DVD player', 'MP3 player', 'I',
            'Miss', 'Mr', 'Mrs', 'Ms', 'T-shirt', 'OK/okay', 'TV'}
# 带句读结尾的真实词条白名单
PUNCT_END_OK = {'a.m.', 'p.m.', 'cheers!', 'congratulations!', 'hallo/hello!'}
# 含数字的真实词条白名单
DIGIT_OK = {'MP3 player'}
# 带子弹符但确实是词条的（PDF 排版把 of course 排成了例样式式）
BULLET_OK = {'of course (not)'}

ENTRY_PAT = re.compile(r"^(?P<w>.+?)\s*\((?P<pos>[a-z][a-z ,&'/]*)\)\s*$")

def is_example(w, line):
    if line.replace(BULLET, '').strip() in BULLET_OK:
        return False                     # 白名单：带子弹但是真词条
    if BULLET in line:
        return True                      # 子弹与文本同一行 = 例句
    if w[0].isupper() and w not in UPPER_OK:
        return True                      # 大写开头 = 句子
    if (w.endswith('.') or w.endswith('?') or w.endswith('!')) and w not in PUNCT_END_OK:
        return True                      # 句读结尾 = 句子
    low = w.lower()
    if low.startswith(('to ', 'a ', 'an ', 'the ', 'i ', 'he ', 'she ', 'it ',
                       'you ', 'they ', 'we ', 'my ', 'your ', 'his ', 'her ',
                       'its ', 'our ', 'their ')):
        return True                      # 主语/不定式/限定词开头 = 例句碎片
    if any(ch.isdigit() for ch in w) and w not in DIGIT_OK:
        return True                      # 含数字 = 例句（over 60 people）
    if len(w.split()) > 4:
        return True                      # 超 4 词必为例句
    return False

# ---------- 形态规范化（plan Step 1） ----------
CANON = {
    '(a)round': 'around',
    'blond(e)': 'blonde',
    'dad(dy)': 'dad',
    'mum(my)': 'mummy',
    'grand(d)ad': 'granddad',
    'gram(me)': 'gram',
    'holiday(s)': 'holidays',
    'certainly (not)': 'certainly',
    'full (of)': 'full of',
    'of course (not)': 'of course',
    'all right/alright': 'all right',
    'cafe/café': 'cafe',
    'hallo/hello!': 'hello',
    'OK/okay': 'OK',
    'kilo(gram[me]) / kg': 'kilogram',
    'kilometre / km': 'kilometre',
    'examination/exam': 'exam',
    'photo(graph)': 'photo',
    'laptop (computer)': 'laptop',
    'mobile (phone)': 'mobile phone',
    "will ('ll)": 'will',
    'pound (£)': 'pound',
    'cheers!': 'cheers',
    'congratulations!': 'congratulations',
}
DROP = {'at / @', 'v / versus'}          # 符号词条，剔除

def normalize(w):
    w = w.strip()
    if w in CANON:
        return CANON[w]
    w = w.replace('(!)', '').strip()
    return w

def main():
    lines = extract_ordered('ket.pdf')
    # 主表范围：a, an (art) 之后、Appendix 1 之前（跨页栏位标记已不在文本里）
    start = next(i for i, l in enumerate(lines) if l.startswith('a, an (art)'))
    end = next(i for i, l in enumerate(lines) if l.startswith('Appendix 1'))
    body = lines[start:end]

    entries, dropped, seen = [], [], set()
    for line in body:
        s = line.strip()
        if not s or s in BULLET or re.fullmatch(r'[A-Z]', s):
            continue
        m = ENTRY_PAT.match(s)
        if not m:
            continue
        w_raw, pos = m.group('w').strip(), m.group('pos').strip()
        w_raw = w_raw.replace(BULLET, '').strip()
        if w_raw == 'of course' and pos == 'not':
            pos = 'adv'                      # of course (not)：括号里不是词性
        pos = pos.replace(' and ', ' & ').replace('prom', 'pron')
        if is_example(w_raw, s):
            dropped.append(s)
            continue
        w = normalize(w_raw)
        if w in DROP:
            dropped.append(s + '   [DROP symbol entry]')
            continue
        if w in seen:
            dropped.append(s + '   [DROP dup]')
            continue
        seen.add(w)
        entries.append((w, pos, w_raw))

    with open('ket-mainlist-v2.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['word', 'pos', 'raw'])
        for e in entries:
            w.writerow(e)
    print(f'entries: {len(entries)}')
    print('distinct pos values:', sorted({p for _, p, _ in entries}))
    print(f'\n--- dropped {len(dropped)} ---')
    for d in dropped:
        print('  ', d)

if __name__ == '__main__':
    main()
