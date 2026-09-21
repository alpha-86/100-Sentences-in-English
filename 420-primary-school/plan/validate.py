"""校验 420-primary-school-sentences.csv 与词表/计划的一致性。

用法：python3 plan/validate.py
检查项：
  1. 结构：60 行 × 8 列、id 1-60 连续、列名顺序正确；
  2. 覆盖：420 个词每个恰好被覆盖一次，无表外词 id；
  3. new_words：音标/词性/中文与原词表逐字一致；
  4. 词形：每个新词（含复数/-ing/三单等变形）真实出现在对应英文句中；
  5. 复习：每一天的回读任务与滚动艾宾浩斯规则 {d-1, d-2, d-4, d-7, d-15, d-30} 一致；
  6. 用词顺序：不出现"尚未学到的内容词"（闭类功能词除外）；
  7. 文件格式：UTF-8 带 BOM、CRLF。
"""
import csv
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENT_CSV = os.path.join(BASE, "420-primary-school-sentences.csv")
VOCAB_CSV = os.path.join(BASE, "420-primary-school.csv")
COLS = ["id", "sentence_en", "sentence_zh", "grammar", "new_words", "phrases", "review_note", "covered_ids"]
GAPS = (1, 2, 4, 7, 15, 30)

# 允许提前使用的闭类功能词（代词/介词/助动词/连词/疑问词等）
FUNCTION_WORDS = set("""a an the i you he she it we they me him her us them my your his its our their
this that these those am is are was were be been do does did have has had and or but so if then
to of in on at by for with from under behind between before after up down out here there please
what who which when where why how can may will let us""".split())

# 词表未列出、但属于不规则变形的情况
IRREGULAR = {
    "child": "children", "shoe": "shoes", "glasses": "glasses", "potato": "potatoes",
    "tomato": "tomatoes", "sheep": "sheep", "fish": "fish", "mouse": "mice",
    "man": "men", "woman": "women",
}


def tokens(text):
    """切词：连字符词（ping-pong、o'clock）保持整体，避免拆成 ping/pong。"""
    return set(w.lower() for w in re.findall(r"[A-Za-z]+(?:['-][A-Za-z]+)*", text))


def forms(word):
    """词表中词条的常见变形。全大写缩写（PE）只按原样匹配。"""
    w = word.lower()
    if word.isupper():
        return {w}
    out = {w, w + "s", w + "es", w + "'s", w + "ing", w + "ed", IRREGULAR.get(w, "")}
    if w.endswith("y"):
        out.add(w[:-1] + "ies")
    if w.endswith("e") and len(w) > 3:
        out.add(w[:-1] + "ing")
    return {f for f in out if f}


def main():
    vocab = list(csv.DictReader(open(VOCAB_CSV, encoding="utf-8-sig")))
    rows = list(csv.DictReader(open(SENT_CSV, encoding="utf-8-sig")))
    by_id = {i + 1: r for i, r in enumerate(vocab)}
    err = []

    # 1. 结构
    if len(rows) != 60:
        err.append(f"行数应为 60，实际 {len(rows)}")
    if [int(r["id"]) for r in rows] != list(range(1, 61)):
        err.append("id 必须为 1-60 且连续")
    if list(rows[0].keys()) != COLS:
        err.append(f"列名/顺序不符：{list(rows[0].keys())}")

    # 2. 覆盖
    covered = []
    for r in rows:
        covered += [int(x) for x in r["covered_ids"].split(",")]
    if sorted(covered) != list(range(1, len(vocab) + 1)):
        err.append("420 个词未做到恰好覆盖一次")

    # 3-4. new_words 逐字一致 + 词形出现在句中
    for r in rows:
        sid = int(r["id"])
        toks = tokens(r["sentence_en"])
        if "cannot" in r["sentence_en"].lower():
            toks.add("not")  # cannot 视为包含 not
        for vid in r["covered_ids"].split(","):
            v = by_id[int(vid)]
            expect = f"{v['英文']}|{v['音标']}|{v['词性']}|{v['中文']}"
            if expect not in r["new_words"]:
                err.append(f"S{sid} new_words 与原词表不一致：{v['英文']}")
            if not forms(v["英文"]) & toks:
                err.append(f"S{sid} 新词未出现在句中：{v['英文']}")

    # 5. 滚动艾宾浩斯
    for i, r in enumerate(rows, start=1):
        if i == 1:
            if "回读" in r["review_note"]:
                err.append("S1 不应有回读任务")
            continue
        expect = sorted({i - d for d in GAPS if i - d >= 1}, reverse=True)
        m = re.search(r"第 ([\d、]+) 天", r["review_note"])
        got = [int(x) for x in m.group(1).split("、")] if m else []
        if got != expect:
            err.append(f"S{i} 回读不符：期望 {expect}，实际 {got}")

    # 6. 用词顺序：不得提前使用未学到的内容词
    for r in rows:
        sid = int(r["id"])
        toks = tokens(r["sentence_en"])
        for vid, v in by_id.items():
            if vid <= sid * 7 or v["英文"].lower() in FUNCTION_WORDS:
                continue
            if forms(v["英文"]) & toks:
                err.append(f"S{sid} 提前使用未学词：{v['英文']}(id{vid})")

    # 7. 文件格式
    raw = open(SENT_CSV, "rb").read()
    if not raw.startswith(b"\xef\xbb\xbf"):
        err.append("缺少 UTF-8 BOM")
    if raw.count(bytes([13, 10])) != 61:
        err.append("行尾应为 CRLF，共 61 行")

    if err:
        print("发现问题：")
        print("\n".join("  - " + e for e in err))
        return 1
    print("校验通过：结构 ✓ 覆盖 ✓ new_words ✓ 词形 ✓ 回读 ✓ 用词顺序 ✓ 格式 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
