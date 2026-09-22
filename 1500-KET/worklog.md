# 1500-KET worklog

## 2026-09-22 词表修复（plan 001：vocab review & fix）

### 任务
执行 `plan/001-vocab-review-and-fix-plan.md`：把 v1 脏词表修复为干净的 `1500-KET.csv`（1500 词整，列：英文,音标,词性,中文）。

### 执行过程

**Step 1 重解析（parse_main_list.py）**
- pdfminer 直接 `extract_text` 会把 PDF 双栏读乱（v1 的 dinner/quiz 错位根因），改用 `extract_pages` 按坐标分栏重建行序；
- 例句特征归纳：行内带 `` 子弹符（v1 只过滤 `•` 所以漏光）、大写开头、句读结尾（`I have about £3. (adv)` 这类带词性的例句行）、`to/a/an/the/人称` 开头、含数字（over 60 people）、超 4 词；
- 6 个误杀修正：`I`（代词）、`cheers!`/`congratulations!`/`hallo/hello!`（句读结尾白名单）、`of course (not)`（带子弹的真词条，PDF 排版如此）；
- 假 POS 修正：`of course (not)` 的括号被 v1 当成词性 → 改 adv；`many` 的 `det, adj & prom` → pron；
- 结果 1244 词条，与 v1 双向 diff：v1 独有的 47 行全部是例句/符号污染，v2 零漏收。

**Step 2+3 补词（additions.tsv，256 词）**
- Appendix 1 词族 124：星期/月份/基数（到 thousand）/序数（到 thirty-first）/国家国籍 11 组/大洲/学科/-er 职业/-ly/-un-/-ing 派生；
- Appendix 3 主题词 35：car park、department store、swimming pool、exam、for sale、half past、listen to、delayed、wheel、worker 等（与主表 diff 得出；`can`(n)、`enter`、`past`、`exam`、`wheel` 因与主表重复/已在而剔除）；
- 兜底 97：身体/动物/食物/文具/节日/天气派生/国家等小学高频词（review 逐词确认；`seem` 等超龄词、Mexico/Mexican 一对因国家组已足够而未收——后 Mexico/Mexican 又回补以凑整，见下）；
- 凑整过程：1244+124+35+97=1500，期间因剔除重复词两度回补（New Year、fire station、skating、dozen、Mexico/Mexican），最终恰好 1500。

**Step 4 翻译（build_vocab.py + overrides.tsv）**
- 自动清洗按 plan 4a 全实现：词性选义项行、行间轮转取义（修掉 `go→以…打赌` 这类 vt 行抢占）、领域标签清除（`[计]` 等，含中文标签如 `[俚]灾难`）、黑名单过滤、≤3 义项、分隔符统一；
- 5 批人工 review 全部 1500 词（每批 300），共 784 条进 overrides.tsv 定稿；重点错译全修：my→我的、Miss→小姐、OK→好的、next to→紧挨着、weekday→工作日、left hand→左手、hip hop→嘻哈、tram→有轨电车、shorts→短裤、run→跑；
- 音标：西里尔映射（ә/є）+ 单数回退复数补尾（shoes→/ʃu:z/）+ 短语合成（get up→/get ʌp/）+ 24 个手工补充，v1 缺音标 14 词全补齐。

**Step 5 校验（validate_vocab.py）**
- 6 组硬门禁：结构（1500×4/BOM/LF/无重复）、例句污染、词性白名单、音标字符集、翻译质量（无标签/无黑名单/≤3 义项）、家族覆盖（星期/月份/基数/序数/季节/大洲/学科）；
- 首轮 6 项失败（by/play/point/run 义项切分超 3、Australian/OK 大写白名单遗漏），修复后全绿。

**Step 6 抽查**
- 修复行逐条复核 + 每 100 行抽音标 15 个，无残留问题。

### 产出
- `1500-KET/1500-KET.csv`（1500 词，校验全绿）
- `1500-KET/scripts/`：parse_main_list.py、build_vocab.py、validate_vocab.py、additions.tsv、overrides.tsv、README.md（词表逻辑与 changelog）
- `prompts/2-1500-KET-001.md` 第 0 节更新词表版本说明
- v1 文件保留存档：KET词汇表.csv、make_ket_csv.py、phrase.py

### 交付确认

- **产物**：`1500-KET/1500-KET.csv` —— 恰好 1500 词 × 4 列（英文,音标,词性,中文），UTF-8 BOM + LF，单词 id = 数据行号，符合 `prompts/2-1500-KET-001.md` 第 0 节输入约定；
- **校验**：`validate_vocab.py` 六组硬门禁全绿（结构 1500×4/无重复/无 CRLF、例句零污染、词性白名单、音标 IPA 字符集零西里尔、翻译无标签/无黑名单/≤3 义项、星期/月份/基数/序数/季节/大洲/学科家族覆盖齐全）；
- **关键数字**：1292 → 1500；删 47 行污染；增 256 词；翻译 784 条人工定稿；音标 0 缺失；v1 缺音标 14 词全补齐；
- **同步更新**：`prompts/2-1500-KET-001.md` 第 0 节已指向 v2 词表；`scripts/README.md` 含词表逻辑与 changelog；stardict.csv（65MB）已 untrack 并加入 .gitignore（重建时按 README 从 ECDICT 下载）；
- **提交**：main @ `41cec07`（2026-09-22，已 push）；v1 文件（KET词汇表.csv、make_ket_csv.py、phrase.py）保留存档未删。

### 与 v1 的 diff 摘要
1292 → 1500；删 47 行例句/符号；增 256 词（附录家族+主题词+兜底）；词性以 PDF 为准并修 5 处；翻译 784 条人工定稿 + 全量机器清洗；音标西里尔字符 0 残留、0 缺失；CRLF→LF。

### 已知取舍（留给下游句子生成）
- `boot`/`boots`、`shoe`/`shoes`、`class member`/`classmate` 等官方重复词条按原样保留（均出自官方 PDF 主表+Appendix 3）；
- `at the same time` 在官方 PDF 中是 bullet 例句，因 v1 已收且属 KET 常用短语，保留为手工增补（adv）；
- `New Year`/`Christmas`/`Easter`/`Halloween` 为专有名词，已入大写白名单；句子生成的专名白名单需与之对齐；
- 音标采用英式（ECDICT 源），与 KET 考试一致。
