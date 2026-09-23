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

---

## 2026-09-23 句子生成（plan 002：1500 词 → 100 句）

### 任务
执行 `plan/002-sentence-generation-plan.md`：把 1500 个 KET 词落到 100 个学习句子上，产出
`1500-KET-sentences.csv`（10 列 × 100 行，UTF-8 BOM + LF）。故事为原创 10 幕《露西的百天日记》。
**PDF 排版是下一阶段，本阶段不做。** 分配逻辑见 plan002 §4，此处不重复。

### 工具链（本阶段新建，commit 7e458b5 / 3a36e30 / 81d3ad0）

| 脚本 | 作用 |
|---|---|
| `scripts/validate_sentences.py` | 100 句硬门禁。支持 `--batch N`（整批）、`--words N`（当天可用词）、`--check "句子" --day N`（单句体检） |
| `scripts/merge_batches.py` | 批次 JSON → CSV；`new_words`/`extend_words`/`extend_note` 单元格与 `review_note` 全部脚本生成 |
| `scripts/make_batch_stub.py` | 批次骨架生成器，`ext_groups`/`covered_ids` 从分配表自动填充 |
| `sentences/BATCH-FORMAT.md` | 批次格式、写句硬约束、陷阱清单（执行者操作手册） |

**设计要点**：`covered_ids` 是解析权威，校验器**从不**按 `; ` / ` || ` 盲切 `new_words`/`extend_words`，
改用"整条目子串精确匹配"——对每个 covered_id 取原词表词条串 `词|音标|词性|中文`，断言它出现在
单元格里并按出现位置还原顺序。这样音标里的逗号/分号永远不会误伤。

变形表按**词性列门控**：`v` 才生成动词形态、`n` 才生成复数、`adj/adv` 才生成比较级最高级，
否则会造出 `man→manner`、`write→writer`、`be→best`、`a→as` 这类撞真词的垃圾形态（这些词都是
**别的词表词**，会让表外词混过门禁）。闭类功能词放行清单只对**词表外的词**生效——`near`、`as`、
`well` 等虽是功能词，但它们本身是词表词，仍须等分配到的那天才可用。

### 生成方式：3 个 subagent 按整幕并行

按**整幕**切分（幕是天然场景边界，不会把同一幕切给两人）：Day 1-30 / 31-60 / 61-100。
日内 10 天的连贯性由同一个执行者负责；跨幕是新场景，不必强衔接。
每批落盘后跑 `--batch N` 全绿再开下一批；subagent 不跑 git，提交由主流程统一做（避免并发冲突）。

过程中因低峰期考虑暂停一次（15:48 全部 agent 落盘暂停、等用户通知后恢复），暂停期间的进度
锚点写在临时文件 `sentences/PROGRESS.md`（已并入本 worklog 后删除），恢复后从各自断点续写，
无返工。

### 词分配微调（12 处，均记于此）

写句时发现若干词在当天无法自然入句，按需求允许的 ±1 微调处理：改 `allocation/act*.py` →
重跑 `allocate_words.py`（**1500/1500 PASS**）→ 每日仍在 12-18 总词数、8-15 句中新词门禁内。
每处都是"源天 −1、目标天 +1"，总覆盖不变，锚词关系全部保住（如 `die` 仍是 D66 扩展组锚词、
`paint` 仍是 D86 影像组锚词）。

| 词 | 原分配 | 调整为 | 原因 |
|---|---|---|---|
| guy | D62 | D73 | D62 已挤了 12 个亲属词；挪到营地"那个家伙是个探险家"，变成自然实指 |
| ever | D66 | D68 | D66 词量过载；且 ever 用于现在完成时，D68 语境更顺 |
| still | D66 | D94 | 同上 |
| return | D66 | D71 | "旅行结束后返回"用得上 |
| learn | D66 | D82 | "学会它"用得上 |
| pencil case | D81 | D91 | "二十厘米长的笔袋"顺理成章 |
| against | D82 | D93 | "把球打到墙上"用得上 |
| else | D82 | D84 | "问别人吧"用得上 |
| dancing | D86 | D96 | 健康生活日"跳舞"更自然 |
| picture / drawing | D86 | D90 | 梦想当画家的句子里正好用上 |
| canal | D100 | D97 | D100 是收官句，运河在其中毫无铺垫、显得突兀；挪到 D97 与已在该天的 `path` 合成 `canal path`（运河边的小路），场景自然，收官句得以留给收束 |

（另有 D88 的 `wake up`/`go out` 一度外移，因 D88 掉到 10 词不合门禁已**回退**，最终无净变化。）

### 脚本缺陷（本阶段自查揪出并修复）

1. **`--batch N` 语义错误**（81d3ad0）：`load_batches` 按 `s["id"] != only` 过滤，导致 `--batch N`
   实际校验的是**第 N 天**而非第 N 批——执行者报告的"批次全绿"实际只覆盖单天。改为按天数区间
   `(N-1)*10+1 .. N*10` 过滤。修正后重跑 `--batch 4` 仍全绿（该批是真的过关）。
2. **长度约束误套到短语**（3a36e30）：15-30 词的约束只针对 `sentence_en`，`phrases` 被误判。
   加 `check_len` 开关。
3. **变形表两处缺口**：`grandchildren` 不认作 `grandchild` 的复数；`skateboard(n)` 这类
   只标名词、但在本书语境中当动词用的词（gardening/planting/showering）不生成 -ing/-ed。
   已补不规则复数表，并放开"只标名词"的词生成动词形态（纯 adj/adv/art/det/prep/conj/num 仍不生成）。

**门禁有效性验证**：用合成批次跑通 merge + 全量校验后做了三类变异测试——篡改音标、
篡改回读日期、删掉句中新词——均被拦下，证明门禁不是空转。

### 词表缺陷（本阶段发现并修复）

ECDICT 源里 6 个词条的 `g` 是坏字 `^`：**grandchild / granddaughter / grandpa / photographer /
reggae / schoolbag**。原样输出会在 PDF 里显示成非 IPA 符号（需求 §6.4/§6.5 要求音标正常显示、
渲染后无乱码）。`IPA_FIX` 表本就有 `'ɡ' → 'g'`，`'^'` 只是漏网；补上后重跑 `build_vocab.py`，
`git diff` 确认**只有这 6 行变化**，其余 1494 行逐字不变（管线确定性得到验证）。
v2 词表（41cec07）的 `validate_vocab.py` 音标字符集门禁未覆盖 `^`，属遗留缺陷。

### 复习设计落实

- 滚动回读文案由 `merge_batches.py` 按 {d-1, d-2, d-4, d-7, d-15, d-30} 统一生成，
  校验器逐行重算比对；例：Day 8 → 第 1、4、6、7 天；Day 16 → 第 1、9、12、14、15 天。
- 每个句子被后续 ≤6 天回读（d+1/d+2/d+4/d+7/d+15/d+30 中 ≤100 的部分）：Day 1-70
  恰好 6 次，Day 71-100 依序递减为 5→0 次（Day 100 收官句零回读）——此为 plan002
  §7.6.5 明示接受的设计，PDF Howto 举例说明滚动回读时须带上该限定，勿写"每句恰好 6 次"。
  Day 1 本身无回读（其句子被后续 6 天正常回读）。
- `repeats` 由执行者写"本句自然复现的旧词及出处天"（含扩展组内复习旧词的来源），
  接在回读文案之后。扩展必背词随所在那天的句子一起进入滚动回读。

### 覆盖与门禁结果

`validate_sentences.py` 全量：**1500/1500 词各恰好一次、100 行 × 10 列、id 1-100 连续、
UTF-8 BOM + LF、0 错**。每天新学 12-18 词、句中新词 8-15 个、扩展词条 ≤10、
锚词均在句中、复习旧词均属更早天且不计入 covered_ids。

### 每批句子/短语/语法选择逻辑

总体原则：**词分配表是硬约束，句子为它服务**。故事线只提供场景骨架，具体句子按当天新词的
"语义家族"来组织——同类词密集的日子（12-15 个同家族词）必然写成列举式或场景清单句，
这是 30 词上限下的结构性取舍；跨家族的日子尽量写成有起承转合的叙事句。

| 幕 | 天数 | 句子组织逻辑 | 语法主线 |
|---|---|---|---|
| 1 | 1-10 | 搬家动线串场：抵达 → 看房 → 认家人 → 搬家具 → 开箱 → 逛镇 → 访邻居 → 数数 → 买文具。`there be` / `be` 动词反复复现做复习锚 | be、there be、祈使句、介词、物主代词 |
| 2 | 11-20 | 开学线：开学第一天、科目表、作息、疑问词、星期月份、频率副词、不定代词、爱好、学校场所。疑问词日与频率副词日属"词表日"，用课堂问答/家庭早餐的真实场景承载 | 一般现在时、疑问句、疑问词 |
| 3 | 21-30 | 日常线：现在进行时用"此刻正在做"的连续动作画面；球类/农场/动物园/食物用场景列举；Bingo 第 25 天登场承接第一幕的邻居家狗 | 现在进行时、can/could、must/have to |
| 4 | 31-40 | 秋天与购物：天气对比用 `and/but` 并列分句；衣橱/序数/方位介词用清单式；钱币日用"妈妈付钱、我数零钱"的家庭场景 | must/have to 深化、否定、祈使 |
| 5 | 41-50 | **一般过去时 D46 上线**，运动会用过去时讲述赛果（ago/last 做时间标志）；万圣节、情绪、想法用第一人称日记口吻；D50 形容词反义对用美术课作画场景成对呈现 | 一般过去时、时间表达 |
| 6 | 51-60 | 入冬：**冰雪词用"体育馆里的冰面 + 零度"化解季节违和**（plan §11.4）；做饭日用一连串烹饪动词；D57 will 上线后用来预告邮局之行 | 一般过去时核心、will 预告 |
| 7 | 61-70 | 圣诞与新年：贺卡日引号内写祝福语；祖孙同堂日（12 个亲属词）用**家族树 + 同位语**破题；音乐会/赞不绝口/品质形容词属同义密集日，用"演出后满口称赞"的场景串起 | will/shall、比较级入门、现在完成时入门 |
| 8 | 71-80 | 澳洲假期：**南半球夏季化解 summer/beach/swimming 词族的时令冲突**（plan §11.1），海滩、雨林、悉尼观光、国家国籍、电子媒体依次展开；国家国籍两日用"在城里遇见各国的人"叙事 | 比较级/最高级巩固、现在完成时巩固、被动入门 |
| 9 | 81-90 | 返校：考试周、because 说明、when/while/until 时间线、if 条件句、笔友通信、学校演出、汽车道路、开关短语动词、材质时尚、梦想未来 | because/when/while/until/if 从句、宾语从句 |
| 10 | 91-100 | 收尾：度量衡、反身代词、动作动词、居家、自然能源、健康、邮政、商店、**D99-100 用"露西整理百天日记"串成复盘句**，Day 100 以"不再是初学者 + an exciting end"收官 | 间接引语入门、综合复习 |

**短语（phrases）选择逻辑**：优先取"本句新词 + 已学词"构成的**高频固定搭配**，而不是临时组合。
如 `on the garden wall`、`go shopping`、`at a discount price`、`go to the dentist`、`talk about
language`、`a piece of cake`。每个短语都必须通过用词范围校验（仅由已学词 + 本句新词构成）。

**语法讲解（grammar）选择逻辑**：只讲本句**实际出现**的语法点，1-3 句，不泛泛罗列。
同义/近义重复词条（bicycle/bike、telephone/phone、television/TV、plane/aeroplane、
grandfather/granddad）在讲解里点明"是同一个东西的两种说法"，避免学习者以为是两个词。
易错搭配在该天讲解里点明（如"商品用 cheap/expensive，价格说 at a discount price"）。

### 内容修订历史（机器门禁管不了的"通顺／搭配／设定"问题）

机器只能保证**用词合规**，保证不了句子通顺。三批产出后由主流程**逐句通读**（需求 §2.4/§2.5
清单），共退回 12 处修订：

| 天 | 问题 | 处置 |
|---|---|---|
| D1 | `an Opera House is in Sydney` —— 专有地标不用不定冠词、句中大写位置也错；且搬家日突然提悉尼毫无铺垫（悉尼戏份在第 8 幕） | 重写，只用 `a`。根因是误以为 a/an 两形都须入句——词表里 `a, an` 是**一个**词条（id 1），a/an 是其变体标注（同 blonde/blond），需求 §1.4 允许变体；`an` 已在 D6 `near an old bridge` 自然落地 |
| D17 | 频率副词操练句语义不成立："每天早上吃三到五顿"自相矛盾，`never eight` 是为塞词硬凑 | 重写为家庭早餐习惯的真实画面 |
| D35 | `the price is not expensive` —— 英语里价格说 high/low，不与 expensive 搭配（典型中式搭配） | 改为让 expensive 修饰商品 `cheap clothes, not expensive ones`，price 用 `at a discount price` |
| D37 | `writes a certain number: the first is a thousand, the third is a million` —— "某一个数字"后列出互不相同的数，自相矛盾 | 重写为"若干数中的第 1、第 3（隐含第 2 是十二）" |
| D41 | 结尾 `— inside, outside` 突兀、无所指 | 砍掉一个旧词（`walk`）换出词数空间，改为 `— go inside, not outside!`，与前面 `in front of the gym` 衔接 |
| D42 | `my bicycle and bike are at the car park` 读起来像有两辆车 | 讲解中点明 bicycle = bike（与 D43 的 plane/aeroplane 同法处理） |
| D45 | `a pain for the dentist` 读不通 | 改为 `in pain` + `I go to the dentist`，dentist 有了自然落点 |
| D74 | `I am foreign` —— foreign 在英语里几乎只作定语修饰事物（a foreign country/language），不说人 | 改为 `a foreign language` 语境；`our conversation is good` 一并理顺 |
| D86 | `Ms Carter` 与角色圣经冲突：Carter 是露西家姓、妈妈是 **Mrs Carter**，凭空出现的 `Ms Carter` 会让小读者以为妈妈再次出场（称谓还变了） | 换成为 **Ms White**（另一位女老师），见下 |
| D87 | `I cycle with my driving licence` —— 骑车不需要驾照，逻辑别扭 | 驾照归爸爸（开车需要），露西只 `cycle home` |
| D88 | **全书唯一一句完全没有场景的句子**：一串逗号隔开的祈使短语，读起来就是词表 | 重写为一天的作息时间线（早上出门—上车下车—进校坐下脱外套｜晚上开关电视—关门—出去） |
| D100 | 收官句散：`a canal` 全书从未出现、无铺垫；`prefer` 的对比不搭；作为百天末句没有收束感 | canal 挪到 D97；末句改为 `friendly smiles vs loud, noisy ones`，破折号后 `a hundred days, a variety, a friend, and an exciting end` 回望百天并收尾 |

**新增角色备案**：D86 为安置词表词条 `Ms`，引入第二位女老师 **Ms White**（怀特老师）。
未改白名单——`White` 本身是 D10 学过的颜色词，词表已覆盖该 token，校验器接受；但按 plan §5
"新增白名单词须记录理由"的精神在此备案：理由是 `Miss`(D86) 与 `Ms`(D86) 是同一天的两条词表
词条、各自需要落点，而复用 `Carter` 会与露西的妈妈撞姓。

**判定为可接受、不予返工的**：D33/D44/D50/D54/D59/D68/D69/D70/D92/D94/D95 等同家族词密集日
（12-15 个同类词压在同一天）的**列举式句子**——30 词上限下这是结构性必然，已尽量给每句加场景
与起承转合。这是本阶段最主要的品质取舍，若后续要改善需放宽单句长度上限。

### 产出

| 文件 | 说明 |
|---|---|
| `1500-KET-sentences.csv` | **主交付物**：10 列 × 100 行，UTF-8 BOM + LF |
| `sentences/batches/batch01-10-*.json` | 10 个批次源文件（含全部句子文本与组结构；单独重跑 merge 可逐字节复现 CSV） |
| `sentences/BATCH-FORMAT.md` | 批次格式、写句硬约束、陷阱清单（执行者操作手册） |
| `scripts/validate_sentences.py` | 硬门禁（全量 / `--batch N` / `--words N` / `--check`） |
| `scripts/merge_batches.py` | 批次 → CSV，单元格与回读文案统一生成 |
| `scripts/make_batch_stub.py` | 批次骨架生成器 |
| `plan/002-allocation-table.md` | 由 `allocate_words.py` 重新渲染（含 12 处微调） |
| `scripts/allocation/act07-10.py` | 12 处微调的数据改动 |
| 本 worklog | |

### 交付确认

- **产物**：`1500-KET/1500-KET-sentences.csv` —— 100 句 × 10 列（`id, sentence_en, sentence_zh,
  grammar, new_words, extend_words, extend_note, phrases, review_note, covered_ids`），
  UTF-8 BOM + LF，id 1-100 连续，符合需求 §5 与 output 约定；
- **校验**：`validate_sentences.py` 全量 **0 错**，10 个批次各自 `--batch N` 亦全绿；
  `allocate_words.py` 1500/1500 PASS；`validate_vocab.py` 全绿；
- **关键数字**：100 句 / 1500 词 / 10 幕 / 100 天；句中**新词 1179** + **扩展必背词 321** = 1500，
  每个词恰好分配一次；扩展组内另含 **37 个复习旧词**（不计入 covered_ids）；短语共 **299 条**；
  93 句带扩展组；句长 21-30 词（平均 29.2，其中 60 句正好卡在 30 词上限）；
- **提交**：main @ `6a9f03a`（2026-09-23，已 push），本阶段共 19 个提交，每个文件/批次单独提交。

### 当前进展与下一步

**当前**：需求 §8 验收清单中"CSV 100 行 10 列 / 1500 词全覆盖 / 校验全绿"、"分配每天 12-18 词且
扩展组成立"、"滚动回读落到 CSV"、"故事连贯无逻辑硬伤"、"plan 与 worklog 齐全、逐步提交"
五项已满足（内容项靠逐句通读，见"内容修订历史"）。

**未做（按要求留给下一阶段）**：PDF 排版——需求 §6 与 plan002 §9。

**交接给 PDF 阶段的要点**：
1. **中文字体是首要环境风险**：渲染链（HTML+CSS → PDF）与字体回退链要先验证再批量渲染，
   字体需同时覆盖中文与 IPA（如 `"Noto Sans CJK SC", "DejaVu Sans", sans-serif`）；
2. **句长几乎顶格**：平均 29.2 词、60 句正好 30 词。英文句 ≥16pt 时一行放不下，
   卡片要预留 2-3 行，排完需检查"页底留白 ≤20%"与"每页约两张卡片"是否还成立；
3. **单元格解析一律用 `covered_ids` 回查原词表**，禁止按 `; ` 或 ` || ` 切分
   （音标含逗号 5 例已加引号，但分号风险仍在）；
4. 音标曾有 6 处 `^` 坏字（已修 6981fa7），**渲染前确认用的是修正后的词表**。

---

## 2026-09-23 进度审计与修复（交付后独立复核）

### 任务

句子 CSV 交付后，对前两阶段的全部断言做独立复验（重跑校验器、重跑 merge 比对字节、
核对关键数字、抽查修订落地），并修复复核中确认的遗留问题。

### 复核结论（均独立重跑验证，非转述）

- **数据与流程全部属实**：`validate_vocab.py` 全绿；`validate_sentences.py` 全量 0 错 +
  10 个批次 `--batch N` 逐批重跑全绿（此前因 `--batch` 语义 bug 修复后只有 batch 4 被
  显式重跑，本次补齐 1-3、5-10 的复跑记录）；`allocate_words.py` 1500/1500 PASS 且
  分配表重渲染无 diff；重跑 `merge_batches.py` 与已提交 CSV **逐字节一致**（12 处内容
  修订全部回灌批次 JSON，可复现性成立）。
- **数字核对**：句中新词 1179 + 扩展必背词 321 = 1500 ✓；短语 299 条 ✓；93 句带扩展组 ✓；
  句长 21-30 词（按校验器 tokenizer 口径，均值 29.2，60 句正好 30 词上限）✓——worklog
  原表述无误，勿用 `split()` 数词（会把独立破折号/斜杠计入，虚高 1-2 词）。
- **12 处内容修订逐条抽查落地**（D1/D35/D42/D45/D74/D86/D87/D97/D100 直接查 CSV，
  D17/D41 在提交史中）✓。
- **两处 worklog 表述修正**（本次已就地改写）：
  1. 复习节原写"每个句子恰好被后续 6 天回读"，漏了 plan002 §7.6.5 的限定
     "d+1,…,d+30 ≤100 的部分"——Day 71-100 实际 5→0 次递减、Day 100 零回读，
     已改写为带限定的准确表述；
  2. 产出表原写批次 JSON"只存词名与组结构"，实际含全部句子文本（这是 merge 可复现
     的前提），已改写。

### 修复内容

1. **`validate_vocab.py` 音标门禁改为封闭字符集**（此前worklog自留的"遗留缺陷"）：
   原实现只拦"西里尔 + 非允许集的**字母**"，`^`（Unicode Sm 符号类）被
   `unicodedata.category` 漏掉，6 处 `^` 坏字当年就是这样混过门禁的。现改为
   **任何不在允许集内的字符一律拦截**，Cyrillic 表随之删除（封闭集已覆盖）。
   允许集顺带清理：去掉重复/冗余字符，**新增 `'`**——审计发现音标列 778 词条用直撇号
   作重音号（ECDICT 源惯例，如 `/'eibl/`），与 `ˈ` 并存；统一改写 778 行属无谓 diff，
   两种记号渲染均无风险，故保留并写入允许集注释。
2. **三个脚本路径锚定脚本位置**：`validate_vocab.py`（`PATH='../1500-KET.csv'`）、
   `parse_main_list.py`（`'ket.pdf'`/`输出`）、`build_vocab.py`（4 输入 + 1 输出的相对路径）
   原先必须从 `1500-KET/scripts/` 运行，否则 FileNotFoundError；现统一
   `Path(__file__).resolve().parent` 锚定，**任意工作目录可跑**。句子侧四个脚本本就锚定，
   未改。README"复现"节同步更新。
3. **`prompts/2-1500-KET-001.md` §8 验收清单**：已完成的 5 项勾选；原第 3 项横跨
   CSV 与 PDF 两侧，拆为"复习（CSV 侧）✓ / 复习（PDF 侧）待 PDF 阶段"。

### 验证

- 变异测试：向音标注入 `^`、注入西里尔 `б` 的临时词表均被新门禁拦下
  （`✗ 音标含非法字符: ['^']` / `['б']`）；真实词表在仓库根、`1500-KET/`、`scripts/`
  三个工作目录运行门禁均全绿；`validate_sentences.py` 全量复跑 PASS。
- 词表与句子 CSV **零数据改动**（本次只改代码与文档）。

### 交付确认

- 修复后全套校验（vocab / sentences 全量 / 10 批 / allocate）全绿，merge 复现仍逐字节一致；
- 遗留事项清零：音标门禁洞已堵、脚本 CWD 陷阱已除、§8 清单已与实际进度同步；
- 命名存照：§8 末项原文写 "plan001.md（含词分配表与扩展组表）"，实际文件为
  `plan/002-sentence-generation-plan.md` + `plan/002-allocation-table.md`，按意图勾选，
  需求文档原文未改。
