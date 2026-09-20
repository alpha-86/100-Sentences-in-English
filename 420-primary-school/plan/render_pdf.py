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
.title-block {
  height: 88mm;
  text-align: center;
  border: 2px solid #7a6fb0;
  border-radius: 12px;
  background: #f6f3fc;
  padding: 14mm 8mm 0;
  margin-bottom: 7mm;
}
.howto-title {
  color: #4a3b8c;
  font-size: 30pt;
  margin: 0 0 3mm;
}
.howto-sub {
  color: #777;
  font-size: 13pt;
  margin: 0 0 7mm;
}
.title-facts {
  font-size: 12pt;
  color: #4a3b8c;
  font-weight: bold;
}
.title-facts span { margin: 0 4mm; }
.howto h2 {
  font-size: 14pt;
  color: #4a3b8c;
  border-left: 4px solid #7a6fb0;
  padding-left: 8px;
  margin: 7mm 0 2.5mm;
}
.howto p, .howto li {
  font-size: 12pt;
  line-height: 1.65;
  color: #333;
  margin: 1mm 0;
}
.howto ul { margin: 1mm 0; padding-left: 7mm; }
.howto .hl {
  background: #fdf6dd;
  border-radius: 4px;
  padding: 6px 10px;
}
.howto .blue {
  background: #e8f0fe;
  border-radius: 4px;
  padding: 6px 10px;
}
"""


HOWTO = """
<div class="howto">
  <div class="title-block">
    <h1 class="howto-title">420 必会单词 · 60 句计划</h1>
    <p class="howto-sub">哈利·波特主题例句 · 小学生每日一句背诵手册</p>
    <p class="title-facts"><span>420 个必会单词</span><span>60 个例句</span><span>6 幕故事</span><span>60 天学完</span></p>
  </div>

  <h2>这本书怎么用</h2>
  <p>每天学 1 句，从 Day 1 学到 Day 60，每天大约 10-15 分钟。学习步骤：</p>
  <ul>
    <li>第 1 步：看着英文句，大声朗读 3 遍；</li>
    <li>第 2 步：看中文意思，确认自己读懂了；</li>
    <li>第 3 步：读「语法 · 句型」讲解，明白这句话为什么这样说；</li>
    <li>第 4 步：记 7 个生词和 1-3 个短语，合上书试着背出整句。</li>
  </ul>

  <h2>每天回读（艾宾浩斯遗忘曲线）</h2>
  <p class="blue">每张卡片底部有一条蓝色的「今日回读」，写着今天要重新朗读的旧句子。它按照艾宾浩斯遗忘曲线设计：学完一句后，在第 1、2、4、7、15、30 天各复习一次，每句话一共复习 6 次。</p>
  <p>举个例子：Day 8 的回读任务是 Day 7、6、4、1；Day 16 的回读任务是 Day 15、14、12、9、1。复习每天都在滚动，只要跟着回读条走，学过的句子就不容易忘记。</p>

  <h2>单词是怎么安排的</h2>
  <ul>
    <li>60 句 × 每句 7 个新词 ＝ 420 个小学必会单词，全部覆盖，一个不落；</li>
    <li>每天只遇到 7 个新词，句子里其余单词都是前几天学过的，越往后读越轻松；</li>
    <li>生词带音标、词性和中文，每行两个，方便孩子用手指指着读；</li>
    <li>旧词会在后面的句子里自然重复出现，读新句子的时候也在复习旧单词。</li>
  </ul>

  <h2>故事与句子</h2>
  <p>60 个句子连起来是一个完整的哈利·波特故事，共 6 幕：入学第一天 → 宿舍与农场 → 朋友与家人 → 校园生活 → 日常作息与生日会 → 数字与日期大综合。每句 8-16 个词，好读、好背、有画面感，孩子可以跟着 Harry、Ron 和 Hermione 一起学完整个学年。</p>

  <h2>语法进阶</h2>
  <p>语法由浅入深，覆盖 KET / Think Starter 的主要句型：</p>
  <ul>
    <li>Day 1-10：be 动词、祈使句、自我介绍、what 疑问句；</li>
    <li>Day 11-20：there be 句型、介词、名词复数、this / these / those；</li>
    <li>Day 21-30：一般现在时、频率副词、want to be、who / which 疑问句；</li>
    <li>Day 31-40：现在进行时、物主代词、why / because、方位表达；</li>
    <li>Day 41-50：can 表能力、时间表达、before / after、will 将来时；</li>
    <li>Day 51-60：基数词、序数词、日期、月份与星期、when 疑问句。</li>
  </ul>

  <h2>一张卡片里有什么</h2>
  <ul>
    <li>英文句：紫色大字，先读它；中文意思：帮助理解；</li>
    <li>语法 · 句型：淡黄色底，讲清这句话的语法点；</li>
    <li>本句生词：7 个新词，带音标、词性、中文，每行两个；</li>
    <li>短语：1-3 个高频搭配（如 play the piano、get up、on Monday），可以直接用在口语和写话里；</li>
    <li>今日回读：蓝色条，今天需要重新朗读的旧句子；</li>
    <li>最下面一行小字：这句话里重现了哪些学过的旧词。</li>
  </ul>

  <h2>给家长的小建议</h2>
  <ul>
    <li>每天固定一个时间学习（比如晚饭后），10-15 分钟就够，贵在坚持；</li>
    <li>让孩子指着单词大声读出来，读比看记得牢；</li>
    <li>不要赶进度，一天一句就好；某天状态不好，只做「今日回读」也可以；</li>
    <li>鼓励孩子把句子演出来：学问候句就和家人打招呼，学生日句就给家人唱数蜡烛。</li>
  </ul>

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
