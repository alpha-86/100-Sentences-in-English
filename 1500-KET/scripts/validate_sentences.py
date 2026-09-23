#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1500-KET 句子校验器（plan002 §8 第 3 步硬门禁）。

用法：
  python3 validate_sentences.py                    # 全量：10 个批次 JSON + 合并后的 CSV（若已存在）
  python3 validate_sentences.py --batch 3          # 只校验 batch03（其余批次缺席不算错）
  python3 validate_sentences.py --words 3          # 打印第 3 天可用的内容词（写句时查用）
  python3 validate_sentences.py --check "句子" --day 3   # 单句体检：只查用词范围/长度/数字

校验项（对应 plan002 §8 第 3 步与需求 §5）：
  1 结构：批次/CSV 100 行 × 10 列、id 1-100 连续、UTF-8 带 BOM、LF
  2 覆盖：1500 词每个恰好一次（new_words + 扩展组新词），无遗漏/重复/表外词；每天 12-18；句中 8-15
  3 出现性：每个 new_words 词（含变形表）真实出现在英文句中
  4 一致性：new_words / extend_words 的 词|音标|词性|中文 与原词表逐字一致（按 covered_ids 取词条）
  5 扩展块：整句条目 ≤10、组数 = extend_note 条数、锚词 ∈ 本句 new_words、复习旧词属更早天且不在 covered_ids、每组说明 ≤20 字
  6 用词顺序：句中内容词 ∈ {本句新词} ∪ {更早天数已分配词} ∪ {闭类功能词} ∪ {白名单专名}
  7 回读：review_note 开头与滚动规则 {d-1,d-2,d-4,d-7,d-15,d-30} 逐字一致（脚本重算比对）
  8 与分配表一致：每天的 new_words 集合 == allocation/act*.py 的 sent

设计要点（防止"按 ; 或 || 盲切"这一已知陷阱）：
  * covered_ids 是解析权威。本脚本**从不**按 `; ` / ` || ` 切分 new_words / extend_words；
    改用"整条目子串精确匹配"——对每个 covered_id 取原词表词条串 `词|音标|词性|中文`，
    断言它出现在对应单元格里，并按出现位置还原顺序。
"""
import csv, re, sys, json, argparse, importlib
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent           # 1500-KET/
ALLOC_DIR = Path(__file__).resolve().parent / "allocation"
VOCAB = BASE / "1500-KET.csv"
BATCH_DIR = BASE / "sentences" / "batches"
CSV_OUT = BASE / "1500-KET-sentences.csv"

HEADER = ["id", "sentence_en", "sentence_zh", "grammar", "new_words",
          "extend_words", "extend_note", "phrases", "review_note", "covered_ids"]

# ---------------------------------------------------------------- 词表 / 分配表

def load_vocab():
    """word -> dict(id, ipa, pos, zh, entry)；id 为数据行号。"""
    words = {}
    with open(VOCAB, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if i == 0:
                continue
            w = dict(id=i, en=row[0], ipa=row[1], pos=row[2], zh=row[3])
            w["entry"] = f"{w['en']}|{w['ipa']}|{w['pos']}|{w['zh']}"
            words[row[0]] = w
    return words


def load_alloc():
    """day -> dict(act, theme, sent, ext)；ext = [(note, anchor, members)]"""
    days = {}
    for f in sorted(ALLOC_DIR.glob("act*.py")):
        mod = importlib.import_module(f"allocation.{f.stem}")
        for d in mod.DAYS:
            days[d["day"]] = d
    assert sorted(days) == list(range(1, 101)), "分配表须覆盖 Day 1-100"
    return days


def alloc_lookup(days, vocab):
    """返回 (word2day, day2info)；day2info[d] = dict(sent=set, ext_new=set, ext_rev={word: from})"""
    word2day, info = {}, {}
    for n in sorted(days):
        d = days[n]
        sent = set(d["sent"])
        ext_new, ext_rev, n_ext = set(), {}, 0
        for note, anchor, members in d.get("ext", []):
            n_ext += len(members)
            for m in members:
                if isinstance(m, str):
                    ext_new.add(m)
                else:
                    ext_rev[m["rev"]] = m["from"]
        for w in sent | ext_new:
            word2day[w] = n
        info[n] = dict(sent=sent, ext_new=ext_new, ext_rev=ext_rev, n_ext=n_ext,
                       covered=sent | ext_new, theme=d.get("theme", ""), act=d.get("act", 0))
    return word2day, info


# ---------------------------------------------------------------- 变形表

IRREG_V = {
    # 原形: (三单, -ing, 过去式, 过去分词)
    "be": ("is", "being", "was", "been"), "have": ("has", "having", "had", "had"),
    "do": ("does", "doing", "did", "done"), "go": ("goes", "going", "went", "gone"),
    "get": ("gets", "getting", "got", "got"), "make": ("makes", "making", "made", "made"),
    "take": ("takes", "taking", "took", "taken"), "come": ("comes", "coming", "came", "come"),
    "see": ("sees", "seeing", "saw", "seen"), "eat": ("eats", "eating", "ate", "eaten"),
    "drink": ("drinks", "drinking", "drank", "drunk"), "give": ("gives", "giving", "gave", "given"),
    "put": ("puts", "putting", "put", "put"), "run": ("runs", "running", "ran", "run"),
    "sit": ("sits", "sitting", "sat", "sat"), "stand": ("stands", "standing", "stood", "stood"),
    "swim": ("swims", "swimming", "swam", "swum"), "sing": ("sings", "singing", "sang", "sung"),
    "write": ("writes", "writing", "wrote", "written"), "speak": ("speaks", "speaking", "spoke", "spoken"),
    "say": ("says", "saying", "said", "said"), "tell": ("tells", "telling", "told", "told"),
    "think": ("thinks", "thinking", "thought", "thought"), "buy": ("buys", "buying", "bought", "bought"),
    "bring": ("brings", "bringing", "brought", "brought"), "catch": ("catches", "catching", "caught", "caught"),
    "teach": ("teaches", "teaching", "taught", "taught"), "find": ("finds", "finding", "found", "found"),
    "leave": ("leaves", "leaving", "left", "left"), "feel": ("feels", "feeling", "felt", "felt"),
    "keep": ("keeps", "keeping", "kept", "kept"), "sleep": ("sleeps", "sleeping", "slept", "slept"),
    "meet": ("meets", "meeting", "met", "met"), "ride": ("rides", "riding", "rode", "ridden"),
    "drive": ("drives", "driving", "drove", "driven"), "fly": ("flies", "flying", "flew", "flown"),
    "grow": ("grows", "growing", "grew", "grown"), "know": ("knows", "knowing", "knew", "known"),
    "throw": ("throws", "throwing", "threw", "thrown"), "wear": ("wears", "wearing", "wore", "worn"),
    "win": ("wins", "winning", "won", "won"), "lose": ("loses", "losing", "lost", "lost"),
    "begin": ("begins", "beginning", "began", "begun"), "break": ("breaks", "breaking", "broke", "broken"),
    "choose": ("chooses", "choosing", "chose", "chosen"), "fall": ("falls", "falling", "fell", "fallen"),
    "forget": ("forgets", "forgetting", "forgot", "forgotten"), "hear": ("hears", "hearing", "heard", "heard"),
    "hold": ("holds", "holding", "held", "held"), "hurt": ("hurts", "hurting", "hurt", "hurt"),
    "learn": ("learns", "learning", "learned", "learned"),
    "lie": ("lies", "lying", "lay", "lain"), "pay": ("pays", "paying", "paid", "paid"),
    "sell": ("sells", "selling", "sold", "sold"), "send": ("sends", "sending", "sent", "sent"),
    "show": ("shows", "showing", "showed", "shown"), "shut": ("shuts", "shutting", "shut", "shut"),
    "spend": ("spends", "spending", "spent", "spent"), "steal": ("steals", "stealing", "stole", "stolen"),
    "understand": ("understands", "understanding", "understood", "understood"),
    "wake": ("wakes", "waking", "woke", "woken"), "cut": ("cuts", "cutting", "cut", "cut"),
    "hit": ("hits", "hitting", "hit", "hit"), "cost": ("costs", "costing", "cost", "cost"),
    "build": ("builds", "building", "built", "built"), "burn": ("burns", "burning", "burned", "burned"),
    "dream": ("dreams", "dreaming", "dreamed", "dreamed"), "draw": ("draws", "drawing", "drew", "drawn"),
    "become": ("becomes", "becoming", "became", "become"), "blow": ("blows", "blowing", "blew", "blown"),
    "beat": ("beats", "beating", "beat", "beaten"), "bite": ("bites", "biting", "bit", "bitten"),
    "hide": ("hides", "hiding", "hid", "hidden"), "ring": ("rings", "ringing", "rang", "rung"),
    "rise": ("rises", "rising", "rose", "risen"), "shake": ("shakes", "shaking", "shook", "shaken"),
    "shine": ("shines", "shining", "shone", "shone"), "shoot": ("shoots", "shooting", "shot", "shot"),
    "lead": ("leads", "leading", "led", "led"), "lend": ("lends", "lending", "lent", "lent"),
    "mean": ("means", "meaning", "meant", "meant"), "read": ("reads", "reading", "read", "read"),
    "ride ": None, "set": ("sets", "setting", "set", "set"), "smell": ("smells", "smelling", "smelled", "smelled"),
    "spell": ("spells", "spelling", "spelled", "spelled"), "spill": ("spills", "spilling", "spilled", "spilled"),
    "split": ("splits", "splitting", "split", "split"), "spread": ("spreads", "spreading", "spread", "spread"),
    "stick": ("sticks", "sticking", "stuck", "stuck"), "strike": ("strikes", "striking", "struck", "struck"),
    "sweep": ("sweeps", "sweeping", "swept", "swept"), "swing": ("swings", "swinging", "swung", "swung"),
    "freeze": ("freezes", "freezing", "froze", "frozen"), "forbid": ("forbids", "forbidding", "forbade", "forbidden"),
}
IRREG_V = {k: v for k, v in IRREG_V.items() if v}

IRREG_N = {
    "child": "children", "man": "men", "woman": "women", "foot": "feet", "tooth": "teeth",
    "mouse": "mice", "person": "people", "goose": "geese", "sheep": "sheep", "fish": "fish",
    "deer": "deer", "knife": "knives", "shelf": "shelves", "leaf": "leaves", "wife": "wives",
    "half": "halves", "wolf": "wolves", "life": "lives", "potato": "potatoes", "tomato": "tomatoes",
    "hero": "heroes", "piano": "pianos", "photo": "photos", "scarf": "scarves", "loaf": "loaves",
    "pence": "pence", "penny": "pence", "aircraft": "aircraft", "series": "series",
}

IRREG_ADJ = {
    "good": ("better", "best"), "bad": ("worse", "worst"), "many": ("more", "most"),
    "much": ("more", "most"), "little": ("less", "least"), "far": ("farther", "farthest"),
    "old": ("older", "oldest"), "ill": ("worse", "worst"),
}

# 需要双写末辅音的词（-ing / -ed / -er / -est）
DOUBLE = {
    "stop", "plan", "shop", "sit", "run", "swim", "get", "put", "cut", "hit", "win", "begin",
    "travel", "prefer", "drop", "fit", "clap", "hug", "nod", "slip", "trip", "dig", "chat",
    "skip", "grab", "mop", "rob", "sad", "big", "hot", "thin", "fat", "wet", "red", "flat",
    "slim", "glad", "mad", "sad", "upset", "sunny", "funny", "happy", "pretty", "tidy",
}

VOWELS = set("aeiou")

# 否定缩写（整体替换该助动词/情态动词）。's/'ve/'ll/'d/'m/'re 属前接词的附着形式，
# 不在此表，由 check_sentence_text 的"附着词拆分"处理（避免造出 have've 这类垃圾形态）。
CONTRACTIONS = {
    "be": ["isn't", "aren't", "wasn't", "weren't"],
    "have": ["haven't", "hasn't", "hadn't"],
    "do": ["don't", "doesn't", "didn't"],
    "will": ["won't"], "would": ["wouldn't"], "can": ["can't", "cannot"],
    "could": ["couldn't"], "shall": ["shan't"], "should": ["shouldn't"],
    "must": ["mustn't"], "may": ["mayn't"], "might": ["mightn't"],
}
# 附着词（clitic）：token 中撇号右侧若为这些，左侧须是已放行的词
CLITICS = {"s", "ve", "d", "ll", "m", "re"}


def _is_cvc(w):
    return len(w) >= 3 and w[-1] not in VOWELS and w[-2] in VOWELS and w[-3] not in VOWELS


def pos_tags(pos):
    return set(re.findall(r"[a-z]+", (pos or "").lower()))


def _plural(w):
    if w in IRREG_N:
        return {IRREG_N[w]}
    out = set()
    if w.endswith(("s", "x", "z", "ch", "sh")):
        out.add(w + "es")
        return out                                  # bus→buses（不再造 buss）
    if w.endswith("o"):
        out.add(w + "es")
    if len(w) > 1 and w.endswith("y") and w[-2] not in VOWELS:
        out.add(w[:-1] + "ies")
    if w.endswith("f"):
        out.add(w[:-1] + "ves")
    if w.endswith("fe"):
        out.add(w[:-2] + "ves")
    out.add(w + "s")
    return out


def _forms_simple(w, tags):
    """按词性生成变形（避免造出 man→manner、write→writer、a→as 这类撞真词的垃圾形态）。

    tags 来自词表词性列的字母标签：v→动词形态；n/pron→复数；adj/adv→比较级最高级。
    """
    is_n = bool(tags & {"n", "pron"}) or not tags
    is_v = "v" in tags or not tags
    is_a = bool(tags & {"adj", "adv"}) or not tags
    out = {w}
    if is_n:
        out |= _plural(w)
        out.add(w + "'s")
        out.add(w + "s'")
    if is_v:
        # 三单
        if w in IRREG_V:
            out.add(IRREG_V[w][0])
        elif w.endswith(("s", "x", "z", "ch", "sh", "o")):
            out.add(w + "es")
        elif len(w) > 1 and w.endswith("y") and w[-2] not in VOWELS:
            out.add(w[:-1] + "ies")
        else:
            out.add(w + "s")
        # -ing
        if w in IRREG_V:
            out.add(IRREG_V[w][1])
        elif w.endswith("ie"):
            out.add(w[:-2] + "ying")
        elif w.endswith("e") and not w.endswith(("ee", "oe", "ye")):
            out.add(w[:-1] + "ing")
        elif w in DOUBLE:
            out.add(w + w[-1] + "ing")
        else:
            out.add(w + "ing")
        # 过去式 / 过去分词
        if w in IRREG_V:
            out.add(IRREG_V[w][2])
            out.add(IRREG_V[w][3])
        elif w.endswith("e"):
            out.add(w + "d")
        elif len(w) > 1 and w.endswith("y") and w[-2] not in VOWELS:
            out.add(w[:-1] + "ied")
        elif w in DOUBLE:
            out.add(w + w[-1] + "ed")
        else:
            out.add(w + "ed")
        # 否定缩写
        out |= set(CONTRACTIONS.get(w, []))
    if is_a:
        # 比较级 / 最高级
        if w in IRREG_ADJ:
            out.add(IRREG_ADJ[w][0])
            out.add(IRREG_ADJ[w][1])
        elif w.endswith("e"):
            out.add(w + "r")
            out.add(w + "st")
        elif len(w) > 1 and w.endswith("y") and w[-2] not in VOWELS:
            out.add(w[:-1] + "ier")
            out.add(w[:-1] + "iest")
        elif w in DOUBLE:
            out.add(w + w[-1] + "er")
            out.add(w + w[-1] + "est")
        else:
            out.add(w + "er")
            out.add(w + "est")
    return out


def word_forms(entry, pos=""):
    """词表词条 -> surface 形态集合（小写，保留撇号）。多词词条按整体匹配（首词变形）。"""
    entry = entry.strip()
    alts = [p.strip() for p in entry.split(",") if p.strip()] if "," in entry else [entry]
    tags = pos_tags(pos)
    out = set()
    for alt in alts:
        parts = alt.split()
        if len(parts) == 1:
            w = parts[0].lower()
            if re.fullmatch(r"[a-z]+", w):
                out |= _forms_simple(w, tags)
            else:                                   # o'clock / a.m. / t-shirt 等
                out.add(w)
                out.add(w + "'s")
        else:                                       # 多词：首词变形，其余照抄
            head, tail = parts[0].lower(), " ".join(parts[1:]).lower()
            heads = _forms_simple(head, tags) if re.fullmatch(r"[a-z]+", head) else {head}
            for h in heads:
                out.add(f"{h} {tail}")
            # 名词短语末尾复数：bus stop -> bus stops（末词为介词/小品词时不加）
            last = parts[-1].lower()
            if (tags & {"n", "pron"}) and last not in {"of", "to", "on", "in", "up", "off",
                                                       "out", "at", "for", "with", "down", "as"}:
                for lp in _plural(last):
                    out.add(head + " " + " ".join(parts[1:-1] + [lp]))
    return out


def normalize(tok):
    """归一化：统一弯撇号为直撇号 + 小写。**保留撇号**（it's 不得等同于 its）。"""
    return tok.replace("’", "'").lower()


TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’.\-][A-Za-z]+)*\.?")


def tokenize(s):
    toks = TOKEN_RE.findall(s)
    return [t.lower().rstrip(".") if t.lower() not in ("a.m.", "p.m.") else t.lower() for t in toks]


# ---------------------------------------------------------------- 闭类功能词 / 白名单

CLOSED = set("""
a an the this that these those some any no every each all both either neither another other
such what which whose who whom whose whoever whatever
i me my mine myself you your yours yourself yourselves he him his himself she her hers herself
it its itself we us our ours ourselves they them their theirs themselves one ones oneself
someone somebody something somewhere anyone anybody anything anywhere everyone everybody
everything everywhere nobody nothing none no-one
and or but nor so yet for because if when while until till since although though unless whether
as than that then thus
about above across after against along among around at before behind below beneath beside
besides between beyond by down during except from in inside into like near of off on onto
opposite out outside over past per round since through throughout toward towards under
until up upon with within without via despite
am is are was were been being have has had having do does did done doing
will would shall should can could may might must ought need dare
not n't no yes ok okay please
there here too also just only even still yet already ever never always often sometimes usually
very quite rather really so such more most less least well now
why how where when what who
else anyway however therefore perhaps maybe
get got getting go going went gone come came coming let us
""".split())

# 白名单专名（plan002 §5）。多词专名用整串短语匹配后吞掉，避免其组成词被误判。
WHITELIST_TOKENS = {"lucy", "tom", "carter", "bingo", "lily", "sam", "kate", "ella",
                    "seaview", "sydney", "opera", "harbour", "bondi", "reef", "barrier",
                    "great"}
WHITELIST_PHRASES = ["seaview school", "opera house", "harbour bridge", "bondi beach",
                     "great barrier reef", "father christmas", "mr carter", "mrs carter",
                     "miss green", "aunt kate"]


# ---------------------------------------------------------------- 复习规则

def review_days(d):
    return sorted(x for x in (d - 1, d - 2, d - 4, d - 7, d - 15, d - 30) if x >= 1)


def review_prefix(d):
    ds = review_days(d)
    if not ds:
        return ""
    return "今日回读：请重新朗读背诵第 " + "、".join(str(x) for x in ds) + " 天的句子。"


# ---------------------------------------------------------------- 校验核心

class Ctx:
    def __init__(self):
        self.vocab = load_vocab()
        self.days = load_alloc()
        self.word2day, self.info = alloc_lookup(self.days, self.vocab)
        self.forms = {w: word_forms(w, self.vocab[w]["pos"]) for w in self.vocab}
        # 词表里出现过的词名（归一化）——闭类功能词放行仅对"表外词"生效
        self.vocab_norm = {normalize(w) for w in self.vocab}
        for w in self.vocab:
            for f in self.forms[w]:
                self.vocab_norm.add(normalize(f))
        self._allow_cache = {}

    def allowed(self, d):
        """第 d 天可用：单 token 映射 + 多词短语（归一化 token 序列）。"""
        if d in self._allow_cache:
            return self._allow_cache[d]
        single, phrases = {}, {}
        for w, day in self.word2day.items():
            if day > d:
                continue
            for f in self.forms[w] | {w.lower()}:
                nf = normalize(f)
                if " " in nf:
                    phrases.setdefault(" ".join(normalize(p) for p in f.split()), f"D{day}·{w}")
                else:
                    single.setdefault(nf, f"D{day}·{w}")
        for ph in WHITELIST_PHRASES:                  # 多词专名整体吞掉
            phrases.setdefault(" ".join(normalize(p) for p in ph.split()), "白名单专名")
        self._allow_cache[d] = (single, phrases)
        return single, phrases


def check_sentence_text(ctx, text, d, errs, where):
    """单句文本体检：数字、长度、用词范围（多词词条整体匹配后逐 token 判定）。"""
    if re.search(r"\d", text):
        errs.append(f"{where}: 英文句含数字，须全部拼写（{text[:40]}...）")
    toks = [normalize(t) for t in tokenize(text)]
    if not (15 <= len(toks) <= 30):
        errs.append(f"{where}: 词数 {len(toks)} 不在 15-30")
    single, phrases = ctx.allowed(d)
    maxlen = max((len(p.split()) for p in phrases), default=1)
    unknown, i = [], 0
    while i < len(toks):
        hit = False
        for L in range(min(maxlen, len(toks) - i), 1, -1):     # 先长后短
            if " ".join(toks[i:i + L]) in phrases:
                i += L
                hit = True
                break
        if hit:
            continue
        t = toks[i]
        i += 1
        if t in WHITELIST_TOKENS:
            continue
        if t in single:
            continue
        if t in ctx.vocab_norm:                   # 词表词但未上线 → 必须报错
            unknown.append(t)
            continue
        # 附着词：Lucy's / I've / we're / it's / they'll
        if "'" in t:
            left, right = t.rsplit("'", 1)
            if right in CLITICS and (left in single or left in WHITELIST_TOKENS or left in CLOSED):
                continue
            if left in ctx.vocab_norm:
                unknown.append(t)                 # 左侧是词表词但未上线
                continue
        if t in CLOSED:
            continue
        unknown.append(t)
    if unknown:
        errs.append(f"{where}: 表外/未上线词 {sorted(set(unknown))}"
                    f"（第 {d} 天未学，且不属闭类功能词/白名单）")
    return unknown


def extract_entries(cell, ids, vocab, errs, where):
    """按 covered_ids 从单元格还原词条顺序：整条目子串精确匹配，禁止按分隔符切分。"""
    found = []
    for wid in ids:
        if not (1 <= wid <= len(vocab)):
            errs.append(f"{where}: covered_id {wid} 越界")
            continue
        w = vocab_by_id(vocab, wid)
        if w is None:
            errs.append(f"{where}: covered_id {wid} 在词表中不存在")
            continue
        idx = cell.find(w["entry"])
        if idx < 0:
            errs.append(f"{where}: id {wid} 的词条与词表不一致或缺失 —— 期望 {w['entry']!r}")
        else:
            found.append((idx, wid))
    found.sort()
    return [wid for _, wid in found]


_VID_CACHE = {}


def vocab_by_id(vocab, wid):
    if not _VID_CACHE:
        for w in vocab.values():
            _VID_CACHE[w["id"]] = w
    return _VID_CACHE.get(wid)


def check_day(ctx, d, s, errs, warns, csv_row=None):
    """校验单天句子 s（批次 JSON 结构）。csv_row 非 None 时同时校验 CSV 单元格一致性。"""
    where = f"Day {d}"
    info = ctx.info[d]
    sent_alloc = info["sent"]

    # --- new_words 与分配表一致
    nw = s.get("new_words") or []
    if set(nw) != sent_alloc:
        errs.append(f"{where}: new_words 与分配表不符；缺 {sorted(sent_alloc - set(nw))} 多 {sorted(set(nw) - sent_alloc)}")
    if len(nw) != len(set(nw)):
        errs.append(f"{where}: new_words 有重复项")

    # --- 扩展组
    ext_groups = s.get("ext_groups") or []
    alloc_ext = ctx.days[d].get("ext", [])
    if len(ext_groups) != len(alloc_ext):
        errs.append(f"{where}: 扩展组数 {len(ext_groups)} != 分配表 {len(alloc_ext)}")
    n_ext_entries = 0
    ext_new_words, rev_words = [], {}
    for g in ext_groups:
        note, anchor = g.get("note", ""), g.get("anchor", "")
        members = g.get("members") or []
        n_ext_entries += len(members)
        if len(note) > 20:
            errs.append(f"{where}: 组说明超 20 字（{len(note)}）：{note}")
        if anchor not in sent_alloc:
            errs.append(f"{where}: 锚词 {anchor!r} 不在本句 new_words")
        for m in members:
            if isinstance(m, str):
                if m in ext_new_words:
                    errs.append(f"{where}: 扩展新词 {m!r} 重复")
                ext_new_words.append(m)
                if ctx.word2day.get(m) != d:
                    errs.append(f"{where}: 扩展新词 {m!r} 的分配天是 D{ctx.word2day.get(m)}，不是本天")
            else:
                rw, frm = m.get("rev"), m.get("from")
                rev_words[rw] = frm
                if ctx.word2day.get(rw) is None:
                    errs.append(f"{where}: 复习词 {rw!r} 未在任何天分配")
                elif ctx.word2day[rw] >= d:
                    errs.append(f"{where}: 复习词 {rw!r} 来源天 D{ctx.word2day[rw]} 不早于本天")
                elif frm != ctx.word2day[rw]:
                    errs.append(f"{where}: 复习词 {rw!r} from={frm} 与实际分配天 D{ctx.word2day[rw]} 不符")
    if n_ext_entries > 10:
        errs.append(f"{where}: 扩展词条 {n_ext_entries} 超 10")
    # 分配表的 ext 成员必须被完整照抄
    alloc_new = [m for _, _, ms in alloc_ext for m in ms if isinstance(m, str)]
    alloc_rev = {m["rev"]: m["from"] for _, _, ms in alloc_ext for m in ms if not isinstance(m, str)}
    if ext_new_words != alloc_new:
        errs.append(f"{where}: 扩展新词与分配表不符 —— 期望 {alloc_new}，实际 {ext_new_words}")
    if rev_words != alloc_rev:
        errs.append(f"{where}: 复习旧词与分配表不符 —— 期望 {alloc_rev}，实际 {rev_words}")
    anchors_alloc = [(n, a) for n, a, _ in alloc_ext]
    if [(g.get("note", ""), g.get("anchor", "")) for g in ext_groups] != anchors_alloc:
        errs.append(f"{where}: 组说明/锚词与分配表不符 —— 期望 {anchors_alloc}")

    # --- visible / covered
    covered = set(sent_alloc) | set(ext_new_words)
    if not (12 <= len(covered) <= 18):
        errs.append(f"{where}: 新词总数 {len(covered)} 不在 12-18")
    if not (8 <= len(nw) <= 15):
        errs.append(f"{where}: 句中新词 {len(nw)} 不在 8-15")

    # --- 出现性
    text = s.get("sentence_en", "")
    toks = tokenize(text)
    joined = " " + " ".join(toks) + " "
    for w in nw:
        fs = ctx.forms.get(w, {w.lower()})
        if not any((" " + f + " ") in joined for f in fs):
            errs.append(f"{where}: 句中新词 {w!r} 未在英文句中出现（已试 {len(fs)} 种变形）")

    # --- 用词范围
    check_sentence_text(ctx, text, d, errs, where)

    # --- 短语
    phrases = s.get("phrases") or []
    if not (1 <= len(phrases) <= 3):
        errs.append(f"{where}: phrases 应为 1-3 个，实际 {len(phrases)}")
    for p in phrases:
        if "|" not in p:
            errs.append(f"{where}: 短语缺 '|' 分隔：{p!r}")
            continue
        en, zh = p.split("|", 1)
        if not zh.strip():
            errs.append(f"{where}: 短语无中文：{p!r}")
        check_sentence_text(ctx, en, d, errs, f"{where}·短语")

    # --- 中文/语法非空
    if len(s.get("sentence_zh", "").strip()) < 4:
        errs.append(f"{where}: sentence_zh 缺失")
    if len(s.get("grammar", "").strip()) < 6:
        errs.append(f"{where}: grammar 缺失")

    # --- covered_ids（若提供）
    ids = s.get("covered_ids")
    exp_ids = sorted(ctx.vocab[w]["id"] for w in covered)
    if ids is not None:
        if sorted(ids) != exp_ids:
            errs.append(f"{where}: covered_ids 与 new_words+扩展新词不符；缺 {sorted(set(exp_ids)-set(ids))} 多 {sorted(set(ids)-set(exp_ids))}")

    # --- CSV 单元格一致性
    if csv_row is not None:
        cell_nw = csv_row["new_words"]
        cell_ew = csv_row["extend_words"]
        cell_ids = [int(x) for x in csv_row["covered_ids"].split(",") if x.strip()]
        if sorted(cell_ids) != exp_ids:
            errs.append(f"{where}: CSV covered_ids 与批次不符")
        # new_words 单元格：条目 = 词表原串，按声明顺序
        exp_cell = "; ".join(ctx.vocab[w]["entry"] for w in nw)
        if cell_nw != exp_cell:
            errs.append(f"{where}: CSV new_words 单元格与词表逐字不符\n  实际 {cell_nw!r}\n  期望 {exp_cell!r}")
        # extend_words：组内 "; "，组间 " || "
        exp_ew = " || ".join(
            "; ".join(ctx.vocab[m if isinstance(m, str) else m["rev"]]["entry"] for m in g.get("members", []))
            for g in ext_groups)
        if cell_ew != exp_ew:
            errs.append(f"{where}: CSV extend_words 单元格与批次不符\n  实际 {cell_ew!r}\n  期望 {exp_ew!r}")
        exp_note = "；".join(g.get("note", "") for g in ext_groups)
        if csv_row["extend_note"] != exp_note:
            errs.append(f"{where}: CSV extend_note 与批次组说明不符\n  实际 {csv_row['extend_note']!r}\n  期望 {exp_note!r}")
        exp_ph = "; ".join(phrases)
        if csv_row["phrases"] != exp_ph:
            errs.append(f"{where}: CSV phrases 与批次不符")
        # 音标/词性/中文逐字一致（按 covered_ids 回查原词表）—— 整条目匹配法
        extract_entries(cell_nw, [ctx.vocab[w]["id"] for w in nw], ctx.vocab, errs, f"{where}·new_words")
        all_ext_ids = [ctx.vocab[m if isinstance(m, str) else m["rev"]]["id"]
                       for g in ext_groups for m in g.get("members", [])]
        extract_entries(cell_ew, all_ext_ids, ctx.vocab, errs, f"{where}·extend_words")

    # --- 回读文案
    pref = review_prefix(d)
    extra = (s.get("repeats") or "").strip()
    exp_review = (pref + extra) if pref else extra
    if csv_row is not None:
        if not csv_row["review_note"].startswith(pref) and pref:
            errs.append(f"{where}: review_note 未以滚动回读文案开头\n  实际 {csv_row['review_note'][:40]!r}\n  期望前缀 {pref!r}")
        if csv_row["review_note"] != exp_review:
            errs.append(f"{where}: review_note 与'回读前缀+复现说明'不符\n  实际 {csv_row['review_note']!r}\n  期望 {exp_review!r}")
    globals().setdefault("EXPECTED_REVIEW", {})[d] = exp_review
    return covered


def load_batches(only=None):
    """-> {day: sentence dict}"""
    out = {}
    files = sorted(BATCH_DIR.glob("batch*.json"))
    if not files:
        return out
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        items = data["sentences"] if isinstance(data, dict) else data
        for s in items:
            if only is not None and s["id"] != only:
                continue
            if s["id"] in out:
                raise SystemExit(f"Day {s['id']} 在多个批次文件中重复（{f.name}）")
            out[s["id"]] = s
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", help="只校验某批（1-10）或 all")
    ap.add_argument("--words", type=int, help="打印第 N 天可用的内容词")
    ap.add_argument("--check", help="单句体检")
    ap.add_argument("--day", type=int, help="配合 --check 指定天")
    a = ap.parse_args()
    ctx = Ctx()
    errs, warns = [], []

    if a.words:
        d = a.words
        info = ctx.info[d]
        print(f"=== Day {d}（第 {info['act']} 幕｜{info['theme']}）===")
        print(f"\n[本句新词 {len(info['sent'])}] " + "、".join(sorted(info["sent"])))
        ext_new = sorted(info["ext_new"])
        if ext_new:
            print(f"\n[扩展新词 {len(ext_new)}，不必入句但锚词须在句] " + "、".join(ext_new))
        byd = {}
        for w, day in ctx.word2day.items():
            if day < d:
                byd.setdefault(day, []).append(w)
        old = [w for day in sorted(byd) for w in sorted(byd[day])]
        print(f"\n[可用旧词 {len(old)}（更早天数已分配，可自由复用）]")
        print("、".join(old))
        return 0

    if a.check:
        d = a.day or 1
        check_sentence_text(ctx, a.check, d, errs, f"Day {d}·体检")
        for e in errs:
            print("ERROR:", e)
        print("== PASS ==" if not errs else "== FAIL ==")
        return 0 if not errs else 1

    only = None
    if a.batch and a.batch != "all":
        only = int(a.batch)
    batches = load_batches(only)

    if not batches:
        print("ERROR: 未找到批次文件", BATCH_DIR)
        return 1

    csv_rows = {}
    if CSV_OUT.exists() and only is None:
        with open(CSV_OUT, encoding="utf-8-sig", newline="") as f:
            rd = list(csv.reader(f))
        if rd and rd[0] != HEADER:
            errs.append(f"CSV 表头不符：{rd[0]}")
        for r in rd[1:]:
            if len(r) != 10:
                errs.append(f"CSV 行 {r[:1]} 列数 {len(r)} != 10")
                continue
            csv_rows[int(r[0])] = dict(zip(HEADER, r))
        raw = CSV_OUT.read_bytes()
        if not raw.startswith(b"\xef\xbb\xbf"):
            errs.append("CSV 缺 UTF-8 BOM")
        if b"\r\n" in raw:
            errs.append("CSV 含 CRLF 换行")
        if len(csv_rows) != 100:
            errs.append(f"CSV 行数 {len(csv_rows)} != 100")

    covered_all = {}
    for d in sorted(batches):
        cov = check_day(ctx, d, batches[d], errs, warns, csv_rows.get(d) if only is None else None)
        for w in cov:
            if w in covered_all:
                errs.append(f"覆盖重复：{w!r} 同时出现在 D{covered_all[w]} 与 D{d}")
            covered_all[w] = d

    for d in sorted(csv_rows):
        if d not in batches:
            errs.append(f"CSV 有 Day {d} 行但批次文件缺失")

    if only is None:
        missing = sorted(set(ctx.vocab) - set(covered_all))
        extra = sorted(set(covered_all) - set(ctx.vocab))
        if missing:
            errs.append(f"词表未覆盖 {len(missing)} 词：{missing[:20]}{'...' if len(missing) > 20 else ''}")
        if extra:
            errs.append(f"表外词 {len(extra)}：{extra[:10]}")
        got = len(covered_all)
        print(f"覆盖：{got}/1500 词；批次 {len(batches)}/100 天；CSV {'已校验' if csv_rows else '未生成'}")

    for w in warns:
        print("WARN:", w)
    for e in errs:
        print("ERROR:", e)
    print(f"\n== {'PASS' if not errs else 'FAIL'}（{len(errs)} 错）==")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
