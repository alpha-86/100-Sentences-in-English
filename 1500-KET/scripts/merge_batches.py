#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 sentences/batches/*.json 合并为 1500-KET-sentences.csv（10 列，UTF-8 带 BOM）。

规则（plan002 §8）：
  * 批次文件只存"词名 + 组结构"；new_words / extend_words / extend_note 单元格与 review_note
    一律由本脚本按 covered_ids 回查原词表拼装 —— 强制执行"音标/词性/中文逐字照抄"，杜绝手抄。
  * review_note = 滚动回读前缀（脚本生成，间隔 {1,2,4,7,15,30}）+ 批次里的 repeats 复现说明。
  * Day 1 无回读，review_note 仅含 repeats。
用法：
  python3 merge_batches.py            # 全部 10 批 -> 1500-KET-sentences.csv
  python3 merge_batches.py --dry-run  # 只打印统计，不落盘
"""
import csv, json, sys, argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
VOCAB = BASE / "1500-KET.csv"
BATCH_DIR = BASE / "sentences" / "batches"
CSV_OUT = BASE / "1500-KET-sentences.csv"
HEADER = ["id", "sentence_en", "sentence_zh", "grammar", "new_words",
          "extend_words", "extend_note", "phrases", "review_note", "covered_ids"]


def load_vocab():
    words = {}
    with open(VOCAB, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if i == 0:
                continue
            words[row[0]] = dict(id=i, en=row[0], ipa=row[1], pos=row[2], zh=row[3],
                                 entry=f"{row[0]}|{row[1]}|{row[2]}|{row[3]}")
    return words


def review_prefix(d):
    ds = sorted(x for x in (d - 1, d - 2, d - 4, d - 7, d - 15, d - 30) if x >= 1)
    if not ds:
        return ""
    return "今日回读：请重新朗读背诵第 " + "、".join(str(x) for x in ds) + " 天的句子。"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    vocab = load_vocab()
    files = sorted(BATCH_DIR.glob("batch*.json"))
    if not files:
        sys.exit(f"未找到批次文件：{BATCH_DIR}")

    rows, seen = [], {}
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        items = data["sentences"] if isinstance(data, dict) else data
        for s in items:
            d = s["id"]
            if d in seen:
                sys.exit(f"Day {d} 重复（{seen[d]} 与 {f.name}）")
            seen[d] = f.name
            nw = s["new_words"]
            ext_groups = s.get("ext_groups") or []
            ext_new = [m for g in ext_groups for m in g.get("members", []) if isinstance(m, str)]
            covered = sorted({vocab[w]["id"] for w in list(nw) + ext_new})

            cell_nw = "; ".join(vocab[w]["entry"] for w in nw)
            cell_ew = " || ".join(
                "; ".join(vocab[m if isinstance(m, str) else m["rev"]]["entry"] for m in g.get("members", []))
                for g in ext_groups)
            note = "；".join(g["note"] for g in ext_groups)
            pref = review_prefix(d)
            repeats = (s.get("repeats") or "").strip()
            review = (pref + repeats) if pref else repeats

            rows.append({
                "id": d,
                "sentence_en": s["sentence_en"],
                "sentence_zh": s["sentence_zh"],
                "grammar": s["grammar"],
                "new_words": cell_nw,
                "extend_words": cell_ew,
                "extend_note": note,
                "phrases": "; ".join(s.get("phrases") or []),
                "review_note": review,
                "covered_ids": ",".join(str(i) for i in covered),
            })

    rows.sort(key=lambda r: r["id"])
    days = [r["id"] for r in rows]
    print(f"批次文件 {len(files)} 个，句子 {len(rows)} 条，Day {min(days)}-{max(days)}")
    if days != list(range(1, len(days) + 1)):
        miss = sorted(set(range(1, 101)) - set(days))
        print(f"WARN: id 不连续/不完整，缺 {miss}")

    if a.dry_run:
        print("dry-run，未落盘")
        return 0

    with open(CSV_OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"已写出 {CSV_OUT}（{len(rows)} 行 × {len(HEADER)} 列，UTF-8 BOM + LF）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
