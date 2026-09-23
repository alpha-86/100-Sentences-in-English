# 1500-KET 词表说明（v2）

> 本目录是 `1500-KET/1500-KET.csv`（需求输入词表）的**生成管线**。
> 旧版 `KET词汇表.csv` 是 v1 存档（脏数据），勿再使用。

## 文件构成

| 文件 | 作用 |
|---|---|
| `../1500-KET.csv` | **产物**：1500 词输入表（列：英文,音标,词性,中文；UTF-8 BOM、LF） |
| `parse_main_list.py` | 从 `ket.pdf`（Cambridge 官方 KET for Schools 词表）重解析主字母表 |
| `ket-mainlist-v2.csv` | 主表骨架（1244 词，PDF 权威词性，已规范化/去例句） |
| `additions.tsv` | 256 个补词（Appendix 词族 + 主题词 + 兜底词，人工 curated 中文/词性） |
| `overrides.tsv` | 784 条翻译人工定稿（5 批全量 review，优先级最高） |
| `build_vocab.py` | 合并 + 音标 + 翻译清洗流水线，产出 `../1500-KET.csv` |
| `validate_vocab.py` | 硬门禁校验（Step 5），全绿才算完成 |
| `KET词汇表.csv` / `make_ket_csv.py` / `phrase.py` | v1 存档（含 ~30 条例句污染与机翻错译，仅留档对照） |
| `ket.pdf` / `stardict.csv` | 官方词表 PDF / ECDICT 词典（构建依赖，65MB 词典不入 git） |

## 词表构成（1500 = 1244 + 256）

1. **主表 1244 词**：官方 PDF 主字母表全量词条（v1 的 1292 行中剔除 47 行例句/符号词条，v1 与 v2 diff 双向确认零漏收）。词性以 PDF 为准，修正 4 处 PDF 笔误（`first name`/`left hand` 的 n 误作 adj、`make up`→phr v、`point`→n & v）。官方短语（bus stop、get up 等 phr v / 复合词）保留在表内，下游分组时按"功能词组"处理。
2. **Appendix 1 词族 124 词**：PDF 用 "Monday, Tuesday, etc." 省略、v1 整体缺失的家族——星期 7、月份 12、基数词 27（two–twenty、thirty…hundred、thousand）、序数词 28（third–thirty-first）、国家/国籍 11 组 22、大洲 6（Australia 计入国家行）、学科 4、-er 职业 8、-ly/-un-/-ing 派生 9。
3. **Appendix 3 主题词表漏收 35 词**：与主表 diff 得出，如 car park、department store、swimming pool、exam、for sale、half past、listen to、delayed、wheel、worker、TV、boots、shoes 等。
4. **兜底补词 97 词**：A2/小学高频且词表分组需要的词（身体 eye/finger/toe/knee、动物 rabbit/snake/duck、食物 noodles/sausage/pie、天气派生 rainy/snowy/stormy、文具 ruler/rubber/notebook/schoolbag/scissors/crayon/sharpener、节日 Christmas/Easter/Halloween、国家 Japan/Germany/Russia/Korea/Mexico 等），全部人工 review。

## 清洗规则（v1 → v2）

### 例句过滤（parse_main_list.py）
PDF 例句行带 `` 子弹符且常伪装成 `I have about £3. (adv)` 形态。过滤规则：行内子弹符、大写开头（白名单 CD/DVD/I/Miss/Mr… 除外）、句读结尾（a.m./p.m. 等除外）、`to/a/an/the/人称/物主` 开头、含数字（MP3 player 除外）、超 4 词；`of course (not)` 为带子弹的真词条，白名单保留。栏位感知解析（按页左右栏重建行序）修复 v1 的栏位错乱（dinner 插在 cross 段等）。

### 词条规范化
- 变体合并：`(a)round`→around、`blond(e)`→blonde、`dad(dy)`→dad、`mum(my)`→mummy、`grand(d)ad`→granddad、`gram(me)`→gram、`holiday(s)`→holidays、`certainly (not)`→certainly、`full (of)`→full of、`of course (not)`→of course、`examination/exam`→exam、`photo(graph)`→photo、`laptop (computer)`→laptop、`mobile (phone)`→mobile phone、`kilo(gram[me]) / kg`→kilogram、`kilometre / km`→kilometre、`will ('ll)`→will、`pound (£)`→pound、`hallo/hello!`→hello、`OK/okay`→OK、`cafe/café`→cafe、`all right/alright`→all right、`cheers!`/`congratulations!` 去叹号。
- 删除符号词条：`at / @`、`v / versus`；删除重复脏行 `internet.`。

### 翻译流水线（build_vocab.py）
1. ECDICT 多行翻译按词条词性选义项行（n & v 先 n 后 v），行间**轮转取义**（每行第 1 义优先），避免 v1 "give→弹性"式张冠李戴；
2. 去词典体前缀（n./a./adv.…）与领域标签（`[计][医][法][俚][经]`…）；
3. 黑名单过滤成人/不适义项（性爱/尸体/赌博/枪击/政治权力/痛饮/赌注等）；
4. 义项去重、每词 ≤3、分隔符统一全角逗号；
5. `overrides.tsv` 784 条人工定稿覆盖（含 plan 定位的全部 ~20 条错译：love/give/turn/wear/yellow/yes/mummy/laptop/mobile/download/class member/cheers/of course/pop/play/body/arm/free/at the same time 等）。

### 音标
ECDICT 音标 + 西里尔符号映射（`ә`→`ə`、`є`→`e`）+ `ə:`→`ɜ:` + 全角冒号统一；缺失词单数回退（studies→study，复数尾自动补 z/s）、短语按词合成（get up→/get ʌp/）、仍缺的手工补充（24 个，含 a.m./p.m.、CD/DVD、download、laptop 等）。v1 缺音标的 14 词全部补齐。

## Changelog

### v2（2026-09-22）— 当前版本
- 重解析官方 PDF（栏位感知），主表 1244 词，47 行例句/符号污染全剔除（v1↔v2 diff 双向确认）；
- 补 256 词：Appendix 1 词族 124 + Appendix 3 主题词 35 + 兜底 97，凑齐恰好 1500；
- 词性改以 PDF 为准，修 4 处 PDF 笔误 + v1 的 `of course→not` 解析错误；
- 翻译全量重洗：词性选义 + 轮转取义 + 黑名单 + 784 条人工定稿；机翻错译（"是类成员/痛饮一杯/迈尔"等）全部清除；
- 音标：西里尔字符清零、14 个缺音标词补齐、短语合成音标；
- 换行统一 LF，UTF-8 BOM 保留；新增 `validate_vocab.py` 硬门禁（结构/例句/词性/音标/翻译/家族覆盖 6 组检查）。

### v1（2026-09-21，存档）
- `make_ket_csv.py` 单栏解析 + `phrase.py` MyMemory 机翻补译；
- 1292 行：~30 条例句污染、~90% 翻译带词典体前缀、`[计]` 标签残留、403 行西里尔 `ә`、星期/月份/数字等国家附录词族整体缺失、14 词缺音标、CRLF 换行。

## 复现

所有脚本以脚本文件自身位置定位数据（`Path(__file__)` 锚定），**可从任意工作目录运行**：

```bash
python3 1500-KET/scripts/parse_main_list.py    # PDF -> ket-mainlist-v2.csv
python3 1500-KET/scripts/build_vocab.py        # + additions.tsv + overrides.tsv -> 1500-KET.csv
python3 1500-KET/scripts/validate_vocab.py     # 硬门禁
```

（2026-09-23 起：此前 `parse_main_list.py`/`build_vocab.py`/`validate_vocab.py` 用相对路径，
必须从 `1500-KET/scripts/` 运行，否则 FileNotFoundError；已统一修复。句子侧
`validate_sentences.py`/`merge_batches.py`/`make_batch_stub.py`/`allocate_words.py`
从一开始就锚定脚本位置，本次未改。）
