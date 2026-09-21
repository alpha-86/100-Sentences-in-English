import csv, re, requests

def translate(text):
    """调用 MyMemory 免费翻译API：中英互译，无需密钥，每天限额约5000字"""
    r = requests.get("https://api.mymemory.translated.net/get",
                     params={"q": text, "langpair": "en|zh-CN"},
                     timeout=15)
    return r.json()["responseData"]["translatedText"]

def clean_cn(t):
    t = re.sub(r"\\n.*", "", t or "")
    return re.sub(r"^\[网络\].*", "", t).strip()

rows = list(csv.reader(open("KET词汇表.csv", encoding="utf-8-sig")))
dic = {r["word"].lower(): r for r in
       csv.DictReader(open("stardict.csv", encoding="utf-8"))}

with open("KET词汇表.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(rows[0])
    for word, phon, pos, cn in rows[1:]:
        if phon or cn:                      # 已有数据，跳过
            w.writerow([word, phon, pos, cn]); continue
        row = dic.get(re.sub(r"\(.*?\)", "", word.lower()).split(",")[0].strip())
        if row:                             # 先从本地词典补音标
            phon = f"/{row['phonetic']}/" if row.get("phonetic") else ""
        try:
            cn = translate(word)
        except Exception as e:
            cn = f"[翻译失败: {e}]"
        w.writerow([word, phon, pos, cn])
        print(f"{word} -> {cn}")
print("补全完成")
