#!/usr/bin/env python3
"""Render 420-primary-school/sentences.csv into an A4 PDF for primary-school kids."""
import csv
import html
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENT_CSV = os.path.join(BASE, "sentences.csv")
VOCAB_CSV = os.path.join(BASE, "420-primary-school.csv")
OUT_PDF = os.path.join(BASE, "sentences.pdf")
OUT_HTML = os.path.join(BASE, "plan", "sentences.html")


def load_vocab():
    """Word id = data row number (1-based), header row carries a BOM."""
    words = {}
    with open(VOCAB_CSV, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f), start=1):
            if i == 1 or not row:
                continue
            en, ipa, pos, zh = row[0], row[1], row[2], row[3]
            words[i - 1] = {"en": en, "ipa": ipa, "pos": pos, "zh": zh}
    return words


def load_sentences():
    with open(SENT_CSV, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def esc(s):
    return html.escape(s, quote=False)


def word_card(w):
    pos = f'<span class="pos">{esc(w["pos"])}</span>' if w["pos"] else ""
    return (
        f'<div class="wc">'
        f'<span class="wen">{esc(w["en"])}</span>'
        f'<span class="wipa">{esc(w["ipa"])}</span>'
        f"{pos}"
        f'<span class="wzh">{esc(w["zh"])}</span>'
        f"</div>"
    )


def phrase_card(p):
    en, _, zh = p.partition("|")
    return (
        f'<div class="pc">'
        f'<span class="pen">{esc(en.strip())}</span>'
        f'<span class="pzh">{esc(zh.strip())}</span>'
        f"</div>"
    )


def two_col(items, cls):
    cells = "".join(f'<div class="cell">{it}</div>' for it in items)
    return f'<div class="grid {cls}">{cells}</div>'


def build_block(row, vocab):
    day = int(row["id"])
    ids = [int(x) for x in row["covered_ids"].split(",") if x.strip()]
    words = [vocab[i] for i in ids]
    # sanity check: every looked-up word must appear in the new_words column
    missing = [w["en"] for w in words if w["en"] not in row["new_words"]]
    assert not missing, f"Day {day}: vocab lookup mismatch {missing}"
    phrases = [p.strip() for p in row["phrases"].split("; ") if p.strip()]

    # rolling Ebbinghaus review: every day shows a re-read bar; the remaining
    # note (old words reused in this sentence) is shown smaller below.
    note = row["review_note"]
    if "今日回读：" in note:
        head, _, rest = note.partition("。")
        reread_bar = f'<div class="reread">{esc(head)}。</div>'
        tail = f'<div class="review-note">{esc(rest.strip())}</div>' if rest.strip() else ""
    else:
        reread_bar = f'<div class="reread">{esc(note)}</div>'
        tail = ""
    return f"""
<div class="day-block">
  <div class="day-head">
    <span class="day-title">Day {day} · 第 {day} 天</span>
    <span class="day-no">句子 {day} / 60</span>
  </div>
  <p class="en">{esc(row['sentence_en'])}</p>
  <p class="zh">{esc(row['sentence_zh'])}</p>
  <div class="grammar"><span class="glabel">语法 · 句型</span>{esc(row['grammar'])}</div>
  <div class="sec-title">本句生词</div>
  {two_col([word_card(w) for w in words], 'words')}
  <div class="sec-title">短语</div>
  {two_col([phrase_card(p) for p in phrases], 'phrases')}
  {reread_bar}
  {tail}
</div>"""


CSS = """
@page {
  size: A4;
  margin: 11mm 13mm 13mm 13mm;
  @top-center {
    content: "420 必会单词 · 60 句计划";
    font-family: "Noto Sans CJK SC";
    font-size: 10pt;
    color: #8a7fb8;
  }
  @bottom-center {
    content: "第 " counter(page) " 页 / 共 " counter(pages) " 页";
    font-family: "Noto Sans CJK SC";
    font-size: 10pt;
    color: #999;
  }
}
* { box-sizing: border-box; }
body {
  font-family: "Noto Sans CJK SC", "DejaVu Sans", sans-serif;
  font-size: 12pt;
  line-height: 1.38;
  color: #333;
  margin: 0;
}
.day-block {
  border: 1px solid #d9d2ee;
  border-radius: 8px;
  padding: 8px 13px 9px;
  margin: 0 0 8px;
  break-inside: avoid;
}
.day-head { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
.day-title {
  font-size: 13.5pt;
  font-weight: bold;
  color: #4a3b8c;
}
.day-no { font-size: 10pt; color: #999; }
p.en {
  font-family: "DejaVu Sans", "Noto Sans CJK SC", sans-serif;
  font-size: 16.5pt;
  font-weight: bold;
  color: #3d2e7a;
  margin: 2px 0 2px;
  line-height: 1.3;
}
p.zh { font-size: 12pt; color: #444; margin: 0 0 4px; }
.grammar {
  background: #fdf6dd;
  border-left: 3px solid #e6c85a;
  border-radius: 4px;
  padding: 4px 10px;
  font-size: 11pt;
  color: #5a4a1a;
  margin: 4px 0;
}
.glabel {
  display: inline-block;
  font-weight: bold;
  color: #a8842a;
  margin-right: 6px;
}
.sec-title {
  font-size: 11pt;
  font-weight: bold;
  color: #4a3b8c;
  margin: 5px 0 2px;
}
.grid { display: table; width: 100%; border-collapse: collapse; }
.grid .cell {
  display: inline-block;
  width: 49%;
  vertical-align: top;
  padding: 2px 6px 2px 0;
}
.wc { font-size: 11pt; }
.wen { font-weight: bold; color: #2b2b2b; font-size: 12pt; margin-right: 5px; }
.wipa {
  font-family: "DejaVu Sans", "Noto Sans CJK SC", sans-serif;
  color: #8c8c8c;
  margin-right: 5px;
}
.pos { font-size: 9pt; color: #7a6fb0; margin-right: 5px; }
.wzh { color: #555; }
.pc { font-size: 11pt; }
.pen {
  font-family: "DejaVu Sans", "Noto Sans CJK SC", sans-serif;
  font-weight: bold;
  color: #2f5a8a;
  margin-right: 6px;
}
.pzh { color: #555; }
.reread {
  margin-top: 5px;
  background: #e8f0fe;
  border-left: 3px solid #5a8ad6;
  border-radius: 4px;
  padding: 3px 10px;
  font-size: 11pt;
  font-weight: bold;
  color: #2f4f8a;
}
.review-note {
  margin-top: 3px;
  font-size: 10.5pt;
  color: #a06a10;
}
.howto {
  break-after: page;
}
.howto-title {
  text-align: center;
  color: #4a3b8c;
  font-size: 26pt;
  margin: 10mm 0 2mm;
}
.howto-sub {
  text-align: center;
  color: #888;
  font-size: 12pt;
  margin: 0 0 8mm;
}
.howto h2 {
  font-size: 13pt;
  color: #4a3b8c;
  border-left: 4px solid #7a6fb0;
  padding-left: 8px;
  margin: 6mm 0 2mm;
}
.howto p, .howto li {
  font-size: 11.5pt;
  line-height: 1.55;
  color: #333;
  margin: 1mm 0;
}
.howto ul { margin: 1mm 0; padding-left: 6mm; }
.howto .hl {
  background: #fdf6dd;
  border-radius: 4px;
  padding: 5px 10px;
}
"""


HOWTO = """
<div class="howto">
  <h1 class="howto-title">420 必会单词 · 60 句计划</h1>
  <p class="howto-sub">哈利·波特主题例句 · 每天一句 · 共 60 天 · KET / Think Starter 适用</p>

  <h2>这本书怎么用</h2>
  <p>每天学 1 句（Day 1 → Day 60），按卡片从上到下的顺序：大声朗读英文句 3 遍 → 看中文意思 → 读语法讲解 → 记 7 个生词和短语。每天约 10-15 分钟。</p>

  <h2>每天回读（艾宾浩斯遗忘曲线）</h2>
  <p class="hl">每张卡片底部的蓝色「今日回读」条，写着今天要重新朗读的旧句子。按学习后第 1、2、4、7、15、30 天滚动复习，每句话一共会复习 6 次——只要跟着回读条走，就不容易忘记。</p>

  <h2>单词是怎么安排的</h2>
  <ul>
    <li>60 句 × 每句 7 个新词 ＝ 420 个小学必会单词，全部覆盖，一个不落。</li>
    <li>每天只遇到 7 个新词，句子里其余都是学过的旧词，越往后读越轻松。</li>
    <li>生词带音标、词性和中文，每行两个，方便指读。</li>
  </ul>

  <h2>故事与句子</h2>
  <p>60 句是一个连贯的哈利·波特故事，共 6 幕：入学第一天 → 宿舍与农场 → 朋友与家人 → 校园生活 → 日常作息与生日会 → 数字与日期大综合。每句 8-16 个词，好读、好背、有画面。</p>

  <h2>语法进阶</h2>
  <p>语法由浅入深：be 动词与祈使句 → there be 与介词 → 一般现在时 → 现在进行时 → can、时间与 will 将来时 → 数词、序数词与日期，覆盖 KET / Think Starter 的主要句型。</p>

  <h2>短语</h2>
  <p>每句配 1-3 个高频短语（如 play the piano、get up、on Monday），全部来自学过的单词，可以直接用在口语和写话里。</p>

  <h2>给小朋友的话</h2>
  <p class="hl">每天一句，跟着「今日回读」复习，60 天后你就会认识全部 420 个单词——和 Harry 一起，从 Hogwarts 顺利毕业吧！</p>
</div>
"""


def main():
    vocab = load_vocab()
    rows = load_sentences()
    assert len(rows) == 60, f"expected 60 rows, got {len(rows)}"
    blocks = "\n".join(build_block(r, vocab) for r in rows)
    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><style>{CSS}</style></head>
<body>
{HOWTO}
{blocks}
</body>
</html>"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    from weasyprint import HTML

    HTML(string=doc, base_url=BASE).write_pdf(OUT_PDF)
    print("wrote", OUT_PDF)


if __name__ == "__main__":
    main()
