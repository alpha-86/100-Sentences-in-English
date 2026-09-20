# 420词 → 60句 生成计划

## 目标与约束（来自 prompts/1-420-primary-school-001.md）

- 60 个句子，尽可能覆盖 420 个单词（420 = 60 × 7，每句约 7 个新词）
- 句外单词尽量少用（只允许多少必要的功能词：the/a/of 等已在表内，放心用）
- 哈利·波特主题，角色名：Harry, Ron, Hermione, Hagrid, Dumbledore, Hedwig（ owl 不在词表，用 bird 代替提及）
- 60 句有连贯性：6 幕故事线（见下）
- KET / Think Starter 语法句型，循序渐进
- 艾宾浩斯回顾：S3、S7、S14、S21、S30、S45 标记为复习句，句中自然重現前面学过的词；词汇在后续句子中重复出现 2-3 次
- 产出：`420-primary-school/sentences.csv` → 然后排版 PDF（weasyprint 已装好，Noto CJK 字体已装好）

## 工作方式（防卡死约定）

1. 每批生成 10 句，**写完立即追加落盘** sentences.csv，再开下一批
2. 单次思考不超过 10 句的规划量
3. 生词的音标/词性/中文：每批用 grep 从原 CSV 只查该批用到的词，不整读
4. 全部 6 批完成后：跑覆盖率校验脚本 → 补漏 → 再排版 PDF

## CSV 列设计（sentences.csv）

| 列 | 内容 |
|---|---|
| id | 1-60（=第几天学习） |
| sentence_en | 英文句子 |
| sentence_zh | 中文意思 |
| grammar | 语法/句型讲解（中文，简明） |
| new_words | 本句新词：`词|音标|词性|中文`，多个用 `; ` 分隔 |
| phrases | 短语：`短语|中文`，多个用 `; ` 分隔 |
| review_note | 复习标记：本句回顾了哪些旧词/句（复习句写"今日回读"提示） |
| covered_ids | 本句新覆盖的 420 词编号（逗号分隔） |

## 词分配表（每句 7 词，按原表行号；个别句 ±1 可调）

词表按行号自然分主题，直接顺切：

| 句 | 词编号 | 主题 |
|---|---|---|
| S1-S7 | 1-49 | 问候/课堂用语（hello…in） |
| S8-S9 | 50-63 | 书包文具+颜色（schoolbag…trousers） |
| S10-S13 | 64-91 | 衣物/房间/家具（they…head） |
| S14-S19 | 92-133 | 动物/农场/家（welcome…we） |
| S20-S28 | 134-196 | 朋友/家庭/爱好（make…father） |
| S29-S36 | 197-252 | 学校生活/科目（lot…way） |
| S37-S44 | 253-308 | 描述/活动/一日三餐（clean…breakfast） |
| S45-S49 | 309-343 | 时间/生日/购物（before…two） |
| S50-S53 | 344-372 | 基数词 three…first |
| S54-S57 | 373-400 | 序数词 second…thousandth |
| S58-S59 | 401-413 | 月份 millionth…December |
| S60 | 414-420 | 星期 Monday…Sunday |

## 语法进阶（Think Starter → KET）

| 幕 | 句 | 语法重点 |
|---|---|---|
| 1 | S1-10 | be 动词 am/is/are；祈使句 sit down / let us；自我介绍 My name is… / Nice to meet you；what 疑问句；颜色作表语/定语 |
| 2 | S11-20 | there be 句型；介词 on/under/behind；复数；this/these/those；have got；many + 复数 |
| 3 | S21-30 | 一般现在时 like/live/play/speak；频率 often/every day；want to be；who/which 疑问句 |
| 4 | S31-40 | 现在进行时；物主代词 their/his/her；why/because；between/in front of；help him |
| 5 | S41-50 | can 表能力；时间表达 o'clock/half past；before/after/begin；will 将来时；buy/ask/write |
| 6 | S51-60 | 数词/序数词/日期；月份星期；when 疑问句；综合复习 |

## 故事线（6 幕，哈利·波特主题）

1. **S1-10 入学第一天**：Harry 到 Hogwarts，师生问候、自我介绍、认识同学；分院帽颜色、书包文具
2. **S11-20 宿舍与农场**：宿舍房间里物品的位置；周末去 Hagrid 的小屋和农场看动物
3. **S21-30 朋友与家人**：Ron 一家、Hermione；宠物；日常爱好（运动、音乐、阅读）
4. **S31-40 校园生活**：图书馆、教室、课程（science→魔药课式表述、maths、PE→飞行课）、提问与回答
5. **S41-50 日常作息与生日会**：早餐晚餐时间、唱歌游泳、筹备生日派对、购物买礼物
6. **S51-60 数字与日期大综合**：数票数、名次（序数词）、生日日期、月份星期，毕业式收尾

## 复习句设计（艾宾浩斯）

| 复习句 | 回顾内容 |
|---|---|
| S3 | 回顾 S1-2（问候语：hello/good/morning） |
| S7 | 回顾 S1-6（自我介绍类词句） |
| S14 | 回顾 S8-13（颜色/物品词），今日回读提示 |
| S21 | 回顾 S14-20（动物/家庭词） |
| S30 | 回顾 S21-29（爱好/日常词） |
| S45 | 回顾 S37-44（三餐/活动词） |

每句的 review_note 列写明具体回顾了哪些词；非复习句也尽量自然重現旧词。

## 执行顺序

1. ✅ 本 plan 文件
2. ✅ 批 1：S1-10 → `batches/batch1.csv`
3. ✅ 批 2：S11-20 → `batches/batch2.csv`
4. ✅ 批 3：S21-30 → `batches/batch3.csv`
5. ✅ 批 4：S31-40 → `batches/batch4.csv`
6. ✅ 批 5：S41-50 → `batches/batch5.csv`
7. ✅ 批 6：S51-60 → `batches/batch6.csv`
8. ✅ 覆盖率校验：420 词全覆盖、无重复无遗漏；每个新词真实出现在句中；new_words 与原表逐字一致；6 个复习句（S3/7/14/21/30/45）均含"今日回读"→ 合并为 `sentences.csv`（60 行 × 8 列，UTF-8 带 BOM）
9. ✅ PDF：`plan/render_pdf.py`（weasyprint）→ `sentences.pdf`（30 页 A4，句子大号深紫、语法区淡黄底、生词短语每行两个、复习句橙色徽章、页眉页码齐全；IPA 用 DejaVu Sans 回退，无乱码无大面积空白）

> 注意：new_words 的音标内部可能含 `; `，下游解析须按 covered_ids 对照原词表取词条，不能按 `; ` 简单切分。
