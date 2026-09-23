#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成批次 JSON 骨架（结构字段全部从分配表/词表自动填充，杜绝手抄错误）。

用法：
  python3 make_batch_stub.py --batch 1          # 写出 sentences/batches/batch01-days001-010.json
  python3 make_batch_stub.py --batch 1 --stdout # 打印到屏幕，不落盘
  python3 make_batch_stub.py --day 7            # 打印 Day 7 的骨架

骨架里已填好：id / ext_groups（组说明·锚词·成员，复习旧词带 from）/ covered_ids。
写句者只需填：sentence_en / sentence_zh / grammar / new_words（按词在句中**出现顺序**）/
              phrases / repeats。new_words 集合必须等于该天分配表的 sent 集合（校验器会查）。
"""
import csv, json, argparse, importlib, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ALLOC_DIR = Path(__file__).resolve().parent / "allocation"
VOCAB = BASE / "1500-KET.csv"
BATCH_DIR = BASE / "sentences" / "batches"


def load_vocab():
    out = {}
    with open(VOCAB, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if i:
                out[row[0]] = i
    return out


def load_days():
    days = {}
    for f in sorted(ALLOC_DIR.glob("act*.py")):
        for d in importlib.import_module(f"allocation.{f.stem}").DAYS:
            days[d["day"]] = d
    return days


def stub(day, days, vid):
    d = days[day]
    ext_groups = []
    for note, anchor, members in d.get("ext", []):
        ms = [m if isinstance(m, str) else {"rev": m["rev"], "from": m["from"]} for m in members]
        ext_groups.append({"note": note, "anchor": anchor, "members": ms})
    covered = sorted({vid[w] for w in d["sent"]}
                     | {vid[m if isinstance(m, str) else m["rev"]] for g in ext_groups for m in g["members"]
                        if isinstance(m, str)})
    return {
        "id": day,
        "sentence_en": "",
        "sentence_zh": "",
        "grammar": "",
        "new_words": [],
        "ext_groups": ext_groups,
        "phrases": [],
        "repeats": "",
        "covered_ids": covered,
        "_hint_sent": d["sent"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int)
    ap.add_argument("--day", type=int)
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args()
    vid, days = load_vocab(), load_days()

    if a.day:
        print(json.dumps(stub(a.day, days, vid), ensure_ascii=False, indent=2))
        return 0
    if not a.batch:
        ap.error("需要 --batch 或 --day")

    lo, hi = (a.batch - 1) * 10 + 1, a.batch * 10
    data = {"batch": a.batch, "days": [lo, hi],
            "sentences": [stub(d, days, vid) for d in range(lo, hi + 1)]}
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if a.stdout:
        print(text)
        return 0
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    dest = BATCH_DIR / f"batch{a.batch:02d}-days{lo:03d}-{hi:03d}.json"
    if dest.exists():
        sys.exit(f"已存在，未覆盖：{dest}")
    dest.write_text(text + "\n", encoding="utf-8")
    print(f"已写出骨架 -> {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
