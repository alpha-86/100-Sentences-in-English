# -*- coding: utf-8 -*-
"""validate_vocab.py — 1500-KET.csv 硬门禁校验（plan Step 5）。全部通过 exit 0。"""
import csv, re, sys, unicodedata

PATH = '../1500-KET.csv'
POS_OK = {'n', 'v', 'adj', 'adv', 'prep', 'conj', 'pron', 'det', 'num', 'art',
          'exclam', 'phr v', 'prep phr', 'n & v', 'v & n', 'n & adj', 'adj & n',
          'n & adv', 'adv & n', 'n & pron', 'n pl', 'adj & adv', 'adv & adj',
          'adj & pron', 'pron & det', 'det & pron', 'det & adj', 'det & exclam',
          'det & n', 'pron & num', 'pron, det & num', 'conj & adv', 'prep & adv',
          'adv & prep', 'prep & conj', 'v & adj', 'adj & v', 'v & exclam',
          'n, adj & adv', 'n, adv & adj', 'adj, det & pron', 'adj, det, pron & adv',
          'det, adj & pron', 'v, prep & adv', 'n, adj & pron'}
PUNCT_END_OK = {'a.m.', 'p.m.'}                    # 句读结尾白名单
PHON_EMPTY_OK = set()                               # 音标空白白名单（现无）
BLACKLIST = ['性爱', '尸体', '赌博', '枪击', '政治权力', '痛饮', '性交',
             '春药', '阴茎', '阴道', '嫖', '妓', '乳房', '乳头', '堕胎',
             '避孕', '赌注', '海洛因', '可卡因', '吗啡', '自杀', '死刑']
CYRILLIC = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюяєії')
# IPA 允许的字符（宽口径：可打印 ASCII + 常见 IPA 扩展）
IPA_ALLOWED = re.compile(r"^[a-zA-Z0-9ˈˌ()/:;,.əɜʌɒɑɔɪʊʃʒθðŋæɛɡxrwiupbtdkfvszmnlhctæː: \-]*$")

def ipa_bad_chars(phon):
    return [c for c in phon if c in CYRILLIC or
            (unicodedata.category(c).startswith('L') and not IPA_ALLOWED.match(c))]

fails = []
def check(cond, msg):
    if not cond:
        fails.append(msg)

raw = open(PATH, 'rb').read()
check(raw.startswith(b'\xef\xbb\xbf'), '缺少 UTF-8 BOM')
check(b'\r\n' not in raw, '存在 CRLF 换行')

with open(PATH, encoding='utf-8-sig', newline='') as f:
    rows = list(csv.reader(f))
hdr, data = rows[0], rows[1:]
check(hdr == ['英文', '音标', '词性', '中文'], f'表头错误: {hdr}')
check(len(data) == 1500, f'数据行数 {len(data)} != 1500')
check(all(len(r) == 4 for r in data), '存在非 4 列的行')

words = [r[0].strip() for r in data]
check(len(set(words)) == len(words), '存在重复词条')

for i, (w, phon, pos, cn) in enumerate(data, 2):   # i=实际行号(含表头)
    tag = f'行{i} [{w}]'
    # 例句污染
    if (w.endswith(('.', '?', '!')) and w not in PUNCT_END_OK) or w.count(' ') > 4:
        fails.append(f'{tag} 疑似例句/过长词条')
    if w[0].isupper() and w not in {'CD', 'CD player', 'DVD', 'DVD player',
            'MP3 player', 'I', 'Miss', 'Mr', 'Mrs', 'Ms', 'T-shirt', 'TV',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December',
            'Africa', 'Asia', 'Europe', 'Australia', 'Antarctica', 'America',
            'American', 'Brazil', 'Brazilian', 'Canada', 'Canadian', 'China',
            'Chinese', 'France', 'French', 'Ireland', 'Irish', 'India', 'Indian',
            'Italy', 'Italian', 'Spain', 'Spanish', 'Britain', 'British',
            'Japan', 'Japanese', 'Germany', 'German', 'Russia', 'Russian', 'Australian', 'OK',
            'Korea', 'Korean', 'Mexico', 'Mexican', 'New Year', 'Christmas',
            'Easter', 'Halloween', 'North America', 'South America'}:
        fails.append(f'{tag} 大写开头但不在白名单')
    # 词性
    if pos not in POS_OK:
        fails.append(f'{tag} 词性非法: {pos}')
    # 音标
    if not phon:
        if w not in PHON_EMPTY_OK:
            fails.append(f'{tag} 缺音标')
    else:
        bad = ipa_bad_chars(phon)
        check(not bad, f'{tag} 音标含非法字符: {bad}')
        check(phon.startswith('/') and phon.endswith('/'), f'{tag} 音标未用 /…/ 包裹')
    # 翻译质量门
    if re.search(r'\[[^\]]*\]', cn):
        fails.append(f'{tag} 翻译含领域标签: {cn}')
    if any(b in cn for b in BLACKLIST):
        fails.append(f'{tag} 翻译含黑名单词: {cn}')
    if len([s for s in re.split(r'[，,；;]', cn) if s.strip()]) > 3:
        fails.append(f'{tag} 义项数 >3: {cn}')
    if '【待补】' in cn:
        fails.append(f'{tag} 翻译未补')

# 覆盖门：家族齐全
fam = {
    '星期': ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
    '月份': ['January','February','March','April','May','June','July','August',
            'September','October','November','December'],
    '基数词': ['two','three','four','five','six','seven','eight','nine','ten',
             'eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen',
             'eighteen','nineteen','twenty','thirty','forty','fifty','sixty',
             'seventy','eighty','ninety','hundred','thousand'],
    '序数词': ['first','second','third','fourth','fifth','sixth','seventh','eighth',
             'ninth','tenth','eleventh','twelfth','thirteenth','fourteenth','fifteenth',
             'sixteenth','seventeenth','eighteenth','nineteenth','twentieth',
             'twenty-first','twenty-second','twenty-third','twenty-fourth',
             'twenty-fifth','twenty-sixth','twenty-seventh','twenty-eighth',
             'twenty-ninth','thirtieth','thirty-first'],
    '季节': ['spring','summer','autumn','winter'],
    '大洲': ['Africa','Asia','Europe','Australia','Antarctica','North America','South America'],
    '学科': ['geography','history','mathematics','science'],
}
wset = set(words)
for name, members in fam.items():
    missing = [m for m in members if m not in wset]
    check(not missing, f'家族缺失 [{name}]: {missing}')

if fails:
    print(f'校验失败 {len(fails)} 项：')
    for m in fails[:60]:
        print('  ✗', m)
    sys.exit(1)
print(f'全部通过：1500 行 4 列、词性/音标/翻译/覆盖门禁全绿 ✓')
