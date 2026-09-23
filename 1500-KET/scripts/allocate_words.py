#!/usr/bin/env python3
"""1500-KET 词分配校验 + plan002 分配表渲染器。

数据：scripts/allocation/actNN.py，每个文件导出 DAYS = [dict(day, act, theme, sent=[...], ext=[(note, anchor, members)])]
  - sent: 句中新词（必须真实出现在英文句中，8-15 个）
  - ext:  扩展必背词组，(组说明, 锚词, 成员列表)；成员为词表词（新词）或 {"rev": 词, "from": 天数}（更早天复习词）
  - rev 成员不计入 covered_ids、不计入本天 12-18 新词数，但计入扩展 ≤10 上限

校验（任一失败退出码 1）：
  A. 拼写存在于词表（difflib 给近邻提示）
  B. 覆盖：1500 词每个恰好一次（sent + ext 新词），无重复无遗漏
  C. 每天：12 <= 新词总数 <= 18；8 <= len(sent) <= 15；ext 词条总数(含 rev) <= 10
  D. 锚词必须在该天 sent 里
  E. rev 词必须已在更早天分配、且不在本天 covered
  F. 语法依赖词上线期限（WARN 不 FAIL）
"""
import csv, sys, difflib, importlib, re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent          # 1500-KET/
ALLOC_DIR = Path(__file__).resolve().parent / "allocation"
VOCAB = BASE / "1500-KET.csv"

def load_vocab():
    words = {}
    with open(VOCAB, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f), start=0):
            if i == 0:
                continue
            wid, w, ipa, pos, zh = i, row[0], row[1], row[2], row[3]  # id = 数据行号
            words[w] = dict(id=wid, ipa=ipa, pos=pos, zh=zh)
    return words

def load_days():
    days = {}
    for f in sorted(ALLOC_DIR.glob("act*.py")):
        mod = importlib.import_module(f"allocation.{f.stem}")
        for d in mod.DAYS:
            dd = d["day"]
            assert dd not in days, f"day {dd} duplicated ({f.name})"
            days[dd] = d
    return days

# 语法依赖词上线期限（软警告）：词 -> 最晚出现天
DEADLINE = {
    "there": 10, "when": 30, "because": 30, "can": 25, "must": 35,
    "have to": 35, "should": 55, "will": 57, "would": 75, "if": 70,
    "than": 65, "more": 65, "most": 65, "ago": 46, "yesterday": 45,
    "already": 70, "yet": 70, "ever": 70, "while": 83, "until": 83,
    "since": 75, "both": 40, "each": 40, "during": 60, "before": 50,
    "after": 50, "would": 90, "if": 84,
}

def norm_ext(m):
    """成员 -> (kind, word, from_day)；kind: new/rev"""
    if isinstance(m, str):
        return ("new", m, None)
    return ("rev", m["rev"], m["from"])

def validate(vocab, days):
    errs, warns = [], []
    if sorted(days) != list(range(1, 101)):
        errs.append(f"day 覆盖应为 1..100，实际缺 {sorted(set(range(1,101))-set(days))} 多 {sorted(set(days)-set(range(1,101)))}")
    assigned = {}   # word -> day
    for n in sorted(days):
        d = days[n]
        sent, ext = d["sent"], d.get("ext", [])
        for w in sent:
            if w not in vocab:
                guess = difflib.get_close_matches(w, vocab, n=2, cutoff=0.6)
                errs.append(f"D{n}: 句中词 '{w}' 不在词表，近邻: {guess}")
                continue
            if w in assigned:
                errs.append(f"D{n}: '{w}' 重复（D{assigned[w]} 已分配）")
            assigned[w] = n
        n_ext = 0
        for note, anchor, members in ext:
            n_ext += len(members)
            if len(note) > 22:
                warns.append(f"D{n}: 组说明超 22 字: {note}")
            if anchor not in sent:
                errs.append(f"D{n}: 锚词 '{anchor}' 不在句中新词中 (组: {note})")
            for m in members:
                kind, w, frm = norm_ext(m)
                if w not in vocab:
                    guess = difflib.get_close_matches(w, vocab, n=2, cutoff=0.6)
                    errs.append(f"D{n}: 扩展词 '{w}' 不在词表，近邻: {guess}")
                    continue
                if kind == "new":
                    if w in assigned:
                        errs.append(f"D{n}: '{w}' 重复（D{assigned[w]} 已分配）")
                    assigned[w] = n
                else:
                    if assigned.get(w) is None:
                        errs.append(f"D{n}: 复习词 '{w}' 尚未在任何天分配")
                    elif assigned[w] >= n:
                        errs.append(f"D{n}: 复习词 '{w}' 来源须更早（现 D{assigned[w]}）")
                    elif frm != assigned[w]:
                        warns.append(f"D{n}: 复习词 '{w}' from={frm} 与实际分配天 D{assigned[w]} 不符")
        tot = len(sent) + sum(1 for _,_,ms in ext for m in ms if norm_ext(m)[0]=="new")
        if not (12 <= tot <= 18):
            errs.append(f"D{n}: 新词总数 {tot} 不在 12-18 (句中 {len(sent)} + 扩展新词)")
        if not (8 <= len(sent) <= 15):
            errs.append(f"D{n}: 句中新词 {len(sent)} 不在 8-15")
        if n_ext > 10:
            errs.append(f"D{n}: 扩展词条 {n_ext} 超 10")
    missing = sorted(set(vocab) - set(assigned))
    if missing:
        warns.append(f"未分配 {len(missing)} 词")
    for w, dl in DEADLINE.items():
        if w in assigned and assigned[w] > dl:
            warns.append(f"'{w}' D{assigned[w]} 超过语法依赖期限 D{dl}")
        elif w not in assigned:
            warns.append(f"语法依赖词 '{w}' 未分配")
    return errs, warns, assigned, missing

def md_day(n, d, vocab):
    sent = d["sent"]
    ext = d.get("ext", [])
    lines = [f"### Day {n}｜第 {d['act']} 幕｜{d['theme']}",
             f"句中新词 {len(sent)} 个：" + "、".join(f"**{w}**" for w in sent)]
    if ext:
        lines.append(f"扩展必背词 {sum(len(ms) for _,_,ms in ext)} 个：")
        for note, anchor, members in ext:
            ms = []
            for m in members:
                kind, w, frm = norm_ext(m)
                ms.append(w if kind == "new" else f"{w}（复习·D{frm}）")
            lines.append(f"- {note}：" + "、".join(ms))
    return "\n".join(lines)

def render(vocab, days, assigned, missing):
    out = ["<!-- 本文件由 scripts/allocate_words.py 生成，请勿手改；改 allocation/act*.py 后重跑 -->"]
    by_act = {}
    for n in sorted(days):
        by_act.setdefault(days[n]["act"], []).append(n)
    for act in sorted(by_act):
        out.append(f"\n## 第 {act} 幕词分配（Day {by_act[act][0]}-{by_act[act][-1]}）\n")
        for n in by_act[act]:
            out.append(md_day(n, days[n], vocab) + "\n")
    if missing:
        out.append("\n## 未分配词（待折入）\n")
        for w in missing:
            v = vocab[w]
            out.append(f"- {w} (id {v['id']}, {v['pos']}, {v['zh']})")
    return "\n".join(out)

if __name__ == "__main__":
    vocab = load_vocab()
    assert len(vocab) == 1500, f"词表应为 1500 词，实际 {len(vocab)}"
    days = load_days()
    errs, warns, assigned, missing = validate(vocab, days)
    for w in warns:
        print(f"WARN: {w}")
    for e in errs:
        print(f"ERROR: {e}")
    ok = not errs
    print(f"\n== {len(assigned)}/1500 已分配, {len(days)}/100 天, "
          f"{'PASS' if ok else 'FAIL'} ==")
    dest = BASE / "plan" / "002-allocation-table.md"
    dest.write_text(render(vocab, days, assigned, missing), encoding="utf-8")
    print(f"rendered -> {dest}")
    sys.exit(0 if ok else 1)
