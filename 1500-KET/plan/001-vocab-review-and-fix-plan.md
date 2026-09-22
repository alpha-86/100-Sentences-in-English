# KET 词汇表 Review 与改进 Plan

> 输入：`1500-KET/scripts/KET词汇表.csv`（1292 行数据 + 表头）
> 生成脚本：`scripts/make_ket_csv.py` + `scripts/phrase.py`（从 Cambridge 官方 KET for Schools PDF + ECDICT 词典生成）
> 目标：产出**干净、儿童友好、恰好覆盖需求**的 1500 词输入表（`1500-KET/1500-KET.csv`）

---

## 一、Review 结论：6 类问题

### 问题 1：例句混进词表（脏数据，最高优先级）

约 30 个**完整英文例句**被当成词条写入（音标列空）：

| 行号 | 内容 | 词性列 |
|---|---|---|
| 5 | I have about £3. | adv |
| 143 | Someone's broken the window. | v |
| 302 | There will be a delay of two hours. | n |
| 327 | Can you get these as a download? | n |
| 911 | She raced her brother to the bus stop. | v |
| 1023 | So, I think it's right. | conj |

**根因**：`make_ket_csv.py` 的词条正则 `^(.+?)\s*\((pos)\)\s*$` 把 PDF 中跟在词条后的**例句行**（PDF 例句也带 `(adv)` 等词性标注）一并匹配。phrase.py 又给这些例句行调 MyMemory 机器翻译补中文，双重污染。

### 问题 2：缺失一整批 KET 必考词族（覆盖缺口，与需求的"语义家族分组"直接冲突）

需求要求按星期/月份/数字/序数等家族分组，但词表里**这些家族整体缺失**——官方 PDF 把它们放在 Appendix 用 "Monday, Tuesday, **etc.**" 概括，解析脚本只扫了主字母表：

| 缺失家族 | 数量 | 例 |
|---|---|---|
| 星期 | 7 | Monday … Sunday 全部缺失 |
| 月份 | 12 | January … December 全部缺失 |
| 基数词 | ~13 | two, three, … twelve, twenty, hundred, thousand（只有 one） |
| 序数词 | 3+ | third 及以后（first/second 有） |
| 国家/国籍对 | 8+ | Brazil/Brazilian, Canada/Canadian, China/Chinese … |
| 大洲 | 7 | Africa, Asia, Europe, Australia … |
| 学科 | 5 | geography, history, mathematics, science … |
| -er 职业派生 | 8+ | **teacher**, driver, farmer, cleaner, dancer, painter, photographer |
| 主题词表（Appendix 3） | ~100 | car park, city centre, department store, exam(ination), boots, lights, main course, by post, for sale … |

抽查确认缺失：Monday、January、two–ten、teacher、exam、boots、rainy/snowy（派生自 rain/snow，可接受）。**需求的分组设计（星期、月份、数字与序数）在当前词表上无法执行。**

### 问题 3：翻译不适合儿童（需求场景是小学生 A2 学习）

**3a. 机器翻译错译**（phrase.py 的 MyMemory API 贡献，最离谱的一批）：

| 单词 | 现翻译 | 应为 |
|---|---|---|
| class member | 是类成员（编程义！） | 同班同学 |
| cheers! | 痛饮一杯 | 干杯；再见 |
| at the same time | 同时\ttóngshí（拼音残留） | 同时 |
| internet.（脏词条） | 互联网。 | —（删词条） |
| v / versus | [计] 溢出， 变量， 向量… | （词条本身可疑，建议删） |

**3b. ECDICT 词典义项全量搬运，含成人/不适义项**——只取词典第一行、未按 KET 语义筛选：

- `love` → n. 爱， 恋爱， 爱情， 爱好， **性爱**
- `body` → 身体， 人， **尸体**, …
- `play` → … 比赛， **赌博**, …
- `pop` → … **枪击**, …
- `chips` → …（作赌注用的）圆形筹码…
- `arm` → 手臂， 袖子， 狭长港湾， **武器**
- `free` → … 享受**政治权力**的…

**3c. 词条/词性与翻译张冠李戴**（多义词只取了第一行，恰错）：

- `give` → n. 弹性， 适应性（KET 义是 vt. 给）
- `turn` → 翻译全是名词义项（词条词性标 v）
- `wear` → n. 穿着， 耗损…（词条词性 v）
- `yellow` → n. 黄色（词条词性 adj，应为"黄色的"）
- `yes` → adv. 是（应为 exclam"是，对"）
- `mum(my)` → n. 菊花， 沉默（取了 mum=菊花 义！妈妈义在 mummy）

**3d. 残留领域标签与错别字**：

- `[计]` 标签残留：credit card、download、laptop、online、video recorder 等 8 处；`download` 还错成「**卸载**, **下栽**」（卸载=unload，下栽=错别字）
- laptop → 仅译"膝上型的"（缺核心义"笔记本电脑"）；mobile (phone) → 仅译"移动的"（缺"手机"）

**3e. 词典体前缀噪音**：1163 行（90%）中文以 `n.` / `a.` / `adv.` 等词典体开头——词性已单列，中文里再带前缀冗余且风格不一（`关于` vs `prep. 在...周围`）。

**3f. 义项堆砌**：256 行义项 ≥5 个（如 `turn` 12 义项、`article` 6 义项），超出 A2 儿童需要。

### 问题 4：词条形态混乱

- **变体括注未规范化**：`(a)round`、`blond(e)`、`dad(dy)`、`mum(my)`、`grand(d)ad`、`gram(me)`、`holiday(s)`、`certainly (not)`、`full (of)`、`exam(ination)`（应统一为 round/blonde/dad/mummy/granddad/gram/holidays/certainly not/full of/exam）
- **多写法合并一格**：`all right/alright`、`cafe/café`、`hallo/hello!`、`OK/okay`、`kilo(gram[me]) / kg`、`kilometre / km`、`examination/exam`——下游按词条匹配/分组时需要唯一形态
- **可疑词条**：`at / @`（@ 是符号不是词）、`v / versus`（搭配 [计] 错译，建议删）、`will ('ll)`（撇号缩略应规范化）
- **重复**：`internet.`（带句号+词性 v）与 `internet`（n）重复
- **词性字段错误**：`of course` 词性是 `not`；`at / @` 词性是 `n`

### 问题 5：音标列问题

- **14 个单词缺音标**（音标空但是单词非短语）：bored, crossroads, download, instructions, online, stairs, studies, theatre, trainers, website, pen-friend, table-tennis（CD/DVD 可接受）
- **IPA 符号混用**：403 行用了 `ә`（西里尔字母，非 IPA）而非 `ə`（IPA schwa）；`aeroplane` 音标 `/'єәrәplein/` 用了西里尔 `є`。PDF 渲染时可能出方框（需求 6.4 明确要求音标正常显示）

### 问题 6：结构性数字缺口

- 现表 **1292 行**，其中：~30 例句 + ~110 短语/例句碎片 + 14 缺音标单词 → **干净单词约 1150**
- 需求是 **1500 词**：清洗后预计只剩 ~1100–1200，**缺口约 300–400 词**
- 全部 1293 行带 CRLF 换行（Windows 风格，建议统一 LF；输出 CSV 需求要求 UTF-8 BOM ✅ 已满足）

---

## 二、改进 Plan

### 总体策略

**不手工逐行修**（1292 行人工不可持续），而是**修生成管线 + 机器批量清洗 + 人工 review 清单**：

1. 修 `make_ket_csv.py` 从官方 PDF 重新生成"骨架"（词条+词性）
2. 补全 Appendix 词族（机器展开 etc. 列表）
3. 翻译改为"ECDICT 精选 + 人工审核批量重写"流水线
4. 机器校验 + 人工抽查 → 锁定 v2 词表

### Step 1：重新解析 PDF，生成干净骨架 `ket-v2-raw.csv`

修改 `make_ket_csv.py`：

- [ ] **排除例句行**：匹配词条前剔除以 `•` 开头、含句末标点（`.?!`）、或含 4+ 空格+大写开头的行（PDF 例句特征）；正则改为要求词形只含 `[a-zA-Z'()\-/ ]` 且**不含句读**
- [ ] **括号变体规范化**：`blond(e)`→`blonde`、`dad(dy)`→`dad`、`grand(d)ad`→`granddad`、`gram(me)`→`gram`；`(a)round`→`around`；多写法词条取第一形态、其余进备注（`all right/alright`→`all right`）
- [ ] **多写法拆分**：`cafe/café`→`cafe`；`OK/okay`→`OK`；`kilometre / km`→`kilometre`
- [ ] **剔除符号词条**：`at / @`、`v / versus`
- [ ] **词性白名单校验**：词性 ∉ {n, v, adj, adv, prep, conj, pron, det, num, art, exclam, phr v, n & v, adj & n, n pl, …} 时告警人工处理（如 `of course` 的 `not`、`at / @` 的 `n`）
- [ ] **输出统一 LF**、UTF-8 带 BOM

### Step 2：补全 Appendix 词族（解决覆盖缺口）

从官方 PDF Appendix 显式展开（脚本里硬编码这些家族，因为 PDF 用 etc. 省略）：

- [ ] 星期 7 词、月份 12 词、季节 4 词（spring/summer/autumn/winter——检查主表是否已收）
- [ ] 基数词：one–twenty、thirty、forty…hundred、thousand
- [ ] 序数词：first–thirty-first（至少 first–fifth + 常见）
- [ ] 国家/国籍对 8 组（Brazil/Brazilian、Canada/Canadian、China/Chinese、France/French、Ireland/Irish、India/Indian、Italy/Italian、Spain/Spanish、UK/British、USA/American）
- [ ] 大洲 7 词、学科 5 词（geography, history, mathematics/maths, science, …）
- [ ] -er 职业派生 8 词：teacher, driver, farmer, cleaner, dancer, painter, photographer, footballer
- [ ] Appendix 3 主题词表漏收词（~100 个，从 PDF Appendix 3 全量提取与主表 diff 得到：car park, city centre, department store, exam, boots, lights, main course, by post, for sale, half past, listen to, pay for …）

### Step 3：凑齐 1500 并定稿词条清单

- [ ] 清洗后去重计数，列**缺口清单**（预计缺 200–300）
- [ ] 缺口从以下来源按序补充：① 官方 PDF 主表因解析 bug 漏收的词（与 PDF 全量 diff 找回）② KET 大纲常见补充词（will, future, o'clock 类——核对官方 Language Specifications）③ 小学高频词兜底
- [ ] **补充词须经人工 review**（来源标注进 worklog）
- [ ] 明确短语政策：KET 官方词表本就含短语（get up, as well, bus stop 等 phr v / 复合词）——**保留官方短语，但单独立类**（词性列已是 phr v/prep phr 等，分组时按"功能词组"处理），确保 1500 的主体是单词

### Step 4：翻译流水线（儿童友好化）

**4a. 自动清洗**（脚本批处理，覆盖 ~80%）：

- [ ] 删除词典体前缀：`n. ` / `a. ` / `adv. ` 等（词性已在独立列）
- [ ] 删除 `[计]` `[医]` `[法]` 等领域标签
- [ ] 按词性选 ECDICT 对应义项行：词条词性 n 只留 n. 行、v 只留 vt./vi. 行，解决 give/turn/wear 张冠李戴
- [ ] 义项裁剪：每词最多留 3 个义项，优先 KET 高频义（用 KET 词性 + 简易频率表排序）
- [ ] IPA 符号清洗：`ә`→`ə`、`є`→`e` 等映射表统一
- [ ] 敏感/成人义项黑名单过滤：性爱|尸体|赌博|枪击|政治权力|武器（arm 的）|痛饮 等，命中则删除该义项

**4b. 人工/LLM 批量重写**（覆盖 4a 处理不了的 ~20%）：

- [ ] 错译清单逐条修正（本 review 已定位约 20 条）：love、give、turn、wear、yellow、yes、mum(my)、laptop、mobile、download、class member、cheers、a/an、of course、pop、play、body、arm、free、at the same time …
- [ ] 缺音标 14 词补音标
- [ ] 每条翻译过"儿童友好 + A2 够用"双标准，输出到 `ket-v2-reviewed.csv`

### Step 5：校验脚本 `validate_vocab.py`（硬门禁）

- [ ] 结构：恰好 1500 行 4 列、id 连续、无重复词条、无 CRLF
- [ ] 无例句污染：英文列不得含 `.?!` 结尾的句子（a.m./p.m. 白名单除外）
- [ ] 词性 ∈ 白名单；音标非空（缩写词白名单除外）且只含 IPA 字符
- [ ] 翻译质量门：不含 `[计]` 等领域标签、不含西里尔字符、不含黑名单词（性爱|尸体|赌博|枪击|政治…）、义项数 ≤3
- [ ] 覆盖门：星期/月份/数字/序数家族齐全
- [ ] 全部通过 → 输出 `1500-KET/1500-KET.csv`（需求 0 约定的输入路径）

### Step 6：人工抽查与验收

- [ ] 按字母分 5 批人工过一遍（每批 ~300 词，重点看翻译自然度）
- [ ] 写 worklog：记录清洗规则、错译修正清单、补词来源、与 v1 的 diff 摘要
- [ ] commit + push

### 工作量与顺序

| 步骤 | 方式 | 预计 |
|---|---|---|
| 1 重解析 | 改脚本 + 跑批 | 半天 |
| 2 补词族 | 脚本硬编码 + diff | 半天 |
| 3 凑 1500 | 脚本 + 人工 review 缺口 | 半天 |
| 4 翻译 | 脚本清洗 + 逐条重写 | 1–2 天（主工作量） |
| 5 校验 | 写脚本 | 2 小时 |
| 6 抽查验收 | 人工 | 半天 |

**关键依赖**：Step 4 的翻译质量决定下游 100 句生成的质量（需求 5 规定句子里的音标/词性/中文照抄词表），值得投入最多时间。

### 风险与回退

- PDF 重解析可能仍有漏 → 校验脚本兜底 + 与 v1 的 diff 人工确认无误删
- 补词超 1500 → 优先官方 Appendix 词，超出的进"备选清单"备用（后续句子生成做替换池）
- 翻译批量重写引入新错 → 保留 v1 对照列，review 时逐条比对
