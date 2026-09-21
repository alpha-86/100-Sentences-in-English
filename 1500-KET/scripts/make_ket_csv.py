# -*- coding: utf-8 -*-
"""
一键生成 KET 词汇表 CSV（单词、音标、词性、中文）
运行: python make_ket_csv.py
依赖: requests, pdfminer.six   ->  pip install requests pdfminer.six
"""
import re, csv, io, sys

PDF_URLS = [
    "https://www.cambridgeenglish.org/images/23387-ket-schools-vocabulary-list.pdf",
]
DICT_URLS = [  # 英汉词典镜像（优先国内CDN）
    "https://cdn.jsdelivr.net/gh/skywind3000/ECDICT@master/ecdict.csv",
    "https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv",
    "https://ghproxy.com/https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv",
]
OUT = "KET词汇表.csv"

# ---------- 1. 下载 KET 官方词汇表 PDF ----------
import requests
def download(urls, dest, kind):
    for u in urls:
        try:
            print(f"[下载{kind}] {u}")
            r = requests.get(u, timeout=60,
                             headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            open(dest, "wb").write(r.content)
            print(f"  成功 ({len(r.content)/1e6:.1f} MB)")
            return True
        except Exception as e:
            print(f"  失败: {e}")
    return False

if not download(PDF_URLS, "ket.pdf", "KET词表PDF"):
    sys.exit("KET词表下载失败，请检查网络后重试")

# ---------- 2. 从 PDF 提取词条 ----------
from pdfminer.high_level import extract_text
print("[解析] 正在从PDF提取词条...")
text = extract_text("ket.pdf")
text = text.replace("\u3000", " ")

start = text.find("a, an (art)")
if start < 0:
    sys.exit("未定位到词表正文，PDF内容可能已更新")
end = text.find("Appendix", start)
lines = text[start:end].split("\n")

entry_pat = re.compile(r"^(?P<w>.+?)\s*\((?P<pos>[a-z][a-z ,&/]*)\)\s*$")
entries, seen = [], set()
for line in lines:
    s = line.strip()
    if not s:
        continue
    for seg in re.split(r"\s{4,}", s):          # PDF为双栏排版
        seg = seg.strip()
        if not seg or re.fullmatch(r"[A-Z]|\d+", seg):
            continue
        if "KET Vocabulary" in seg or seg[0] in "?•":
            continue
        m = entry_pat.match(seg)
        if m:
            w, pos = m.group("w").strip(), m.group("pos").strip()
            if (w, pos) not in seen:
                seen.add((w, pos))
                entries.append((w, pos))
print(f"[解析] 共提取 {len(entries)} 个词条")

# ---------- 3. 加载英汉词典（音标+中文） ----------
if not download(DICT_URLS, "stardict.csv", "英汉词典"):
    sys.exit("词典下载失败")

print("[加载] 英汉词典...")
dic = {}
with open("stardict.csv", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        dic[row["word"].lower()] = row

def clean_cn(t):
    t = re.sub(r"\\n.*", "", t or "")           # 只取第一行释义
    t = re.sub(r"^\[网络\].*", "", t)
    return t.strip()

def lookup(word):
    """依次尝试: 原样 -> 去括号 -> 取第一个词"""
    cands = [word.lower(),
             re.sub(r"\(.*?\)", "", word.lower()).strip(),
             re.split(r"[,/]", word.lower())[0].strip()]
    for c in cands:
        if c in dic:
            return dic[c]
    return None

# ---------- 4. 生成 CSV ----------
miss = 0
with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["单词", "音标", "词性", "中文"])
    for word, pos in entries:
        row = lookup(word)
        if row:
            phon = f"/{row['phonetic']}/" if row.get("phonetic") else ""
            cn = clean_cn(row.get("translation", ""))
        else:
            phon, cn, miss = "", "", miss + 1
        w.writerow([word, phon, pos, cn])

print(f"[完成] 已生成 {OUT}，共 {len(entries)} 词，"
      f"其中 {miss} 个词未查到音标/释义（多为短语，可手工补充）")
