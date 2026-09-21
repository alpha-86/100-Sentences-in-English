# 420 小学必会单词 · 60 句

60 个句子覆盖 420 个小学必会单词：**每句 7 个新词**、句子 8-16 词、一天一句、60 天学完。配一本 A4 打印手册（32 页：书名 + Howto 两页 + 60 张每日卡片）与滚动艾宾浩斯回读。

- 原始需求：[`../prompts/1-420-primary-school-001.md`](../prompts/1-420-primary-school-001.md)
- 全书主题：借用哈利·波特的角色名与霍格沃茨场景（此主题只属于本项目，其他词表项目各有主题，见[顶层 README](../README.md)）

## 目录内容

| 文件 | 说明 |
|---|---|
| `420-primary-school.csv` | 词表：420 个单词（`英文,音标,词性,中文`），**单词 id = 数据行号** |
| `420-primary-school-sentences.csv` | 最终学习数据：60 行 × 8 列，UTF-8 带 BOM、CRLF |
| `420-primary-school-sentences.pdf` | 成品手册：第 1 页书名（约 35%）+ Howto，第 2 页 Howto 续，Day 1 卡片从第 3 页开始，共 32 页、每页约两张卡片 |
| `plan/plan.md` | 第一版执行计划：词分配表、分幕故事线、语法进阶表、CSV 列设计 |
| `plan/plan2-revision.md` | 修订计划：滚动复习 / S32 改写 / PDF 字号加大 |
| `plan/validate.py` | 一条命令全量校验（7 项，见下） |
| `plan/render_pdf.py` | weasyprint 渲染脚本，同时输出 `plan/sentences.html` 供检查 |
| `plan/sentences.html` | 渲染中间产物，可在浏览器里直接看版式 |
| `batches/batch1-6.csv` | 分批生成时的中间快照（每批 10 句）。**与最终 CSV 冲突时一律以 `420-primary-school-sentences.csv` 为准** |
| `worklog.md` | 生成过程、选择逻辑、踩坑、五次修订记录、世界观与称谓检查表 |

## 学习数据列（8 列）

| 列 | 内容 |
|---|---|
| `id` | 1-60，= 第几天学习 |
| `sentence_en` | 英文句子 |
| `sentence_zh` | 中文意思 |
| `grammar` | 语法/句型讲解（中文，1-3 句，只讲本句实际出现的点） |
| `new_words` | 本句 7 个新词：`词\|音标\|词性\|中文`，多个用 `; ` 分隔 |
| `phrases` | 1-3 个短语：`短语\|中文`，`; ` 分隔 |
| `review_note` | "今日回读：…"（脚本生成）+ 本句自然复现的旧词说明 |
| `covered_ids` | 本句新词 id，逗号分隔 |

## 三条硬约束

1. **词覆盖**：句子 s 覆盖单词 id `(s-1)*7+1` 到 `s*7`，420 词恰好各出现一次；词表本身按主题顺切（问候 → 文具颜色 → 衣物家具 → 动物农场 → 家庭爱好 → 学校科目 → 活动三餐 → 时间购物 → 数词 → 序数词 → 月份 → 星期）。
2. **用词顺序**：每句只允许「本句 7 个新词 + id 更小的旧词 + 闭类功能词 + 白名单专名」。白名单＝角色名 `Harry / Ron / Hermione / Hagrid / Dumbledore / Hedwig / Hogwarts`，以及表外专名 `Smith`（Ms Smith / Mr Smith，第五次修订为满足"称谓 + 姓氏"引入，全书仅此一个）。
3. **滚动回读**：第 d 天的回读任务 = { d-1, d-2, d-4, d-7, d-15, d-30 } 中 ≥ 1 的天，写在 `review_note` 开头；每句恰好被后续 6 天回读，由脚本生成、机器校验，不手写。

## 故事线与语法进阶

| 幕 | 句 | 故事 | 语法重点 |
|---|---|---|---|
| 1 | S1-10 | 入学第一天：问候、自我介绍、分院、文具 | be 动词；祈使句；what 疑问句；颜色作表语/定语 |
| 2 | S11-20 | 宿舍与农场：物品位置、Hagrid 小屋的动物 | there be；介词 on/under/behind；复数；this/these/those；have got |
| 3 | S21-30 | 朋友与家人：罗恩一家、Hermione、宠物、爱好 | 一般现在时（含三单）；频率副词；want to be；who/which |
| 4 | S31-40 | 校园生活：图书馆、课程、提问回答 | 现在进行时；物主代词；why/because；between/in front of |
| 5 | S41-50 | 日常作息与生日会：三餐、唱歌游泳、买礼物 | can 表能力；o'clock/half past；before/after；will 将来时 |
| 6 | S51-60 | 数字日期大综合：数票数、序数词、生日日期、毕业收尾 | 基数词/序数词/日期；in/on + 月份星期；when 疑问句 |

## 怎么用

**孩子**：每天一张卡片，15-20 分钟——朗读 3 遍 → 看中文 → 读语法 → 记 7 个生词和短语 → **背诵 + 背写**（最重要）；再按卡片底部蓝色"今日回读"条复习旧句（同样先朗读、再背诵、最好背写）。完整说明在 PDF 第 1-2 页的 Howto。

**维护/再生成**：

```bash
cd 420-primary-school

python3 plan/validate.py      # 改完 CSV 必跑，必须全绿
python3 plan/render_pdf.py    # 需要 weasyprint；同时写出 plan/sentences.html
```

改动流程：改 `420-primary-school-sentences.csv` → `validate.py` 全绿 → 重渲染 PDF → 用 PyMuPDF 把首页/Howto/中间页/末页转图抽查（无乱码、无方框、无大面积空白，页底留白 ≤ 20%，生词每行两个）→ 提交。

`validate.py` 检查 7 项：① 60 行 × 8 列、id 连续；② 420 词恰好覆盖一次；③ `new_words` 与原词表逐字一致；④ 每个新词（含变形）真实出现在句中；⑤ 回读任务与滚动规则完全一致；⑥ 不提前使用未学内容词（闭类功能词豁免）；⑦ 文件格式（UTF-8 BOM + CRLF）。注意脚本常量是 420 专用的（60 行 / 每句 7 词），复用到别的词表项目要改。

## 已知坑（改动前先看）

1. **音标内部可能含 `; `**（如 `/duː; də/`），与 `new_words` 的词条分隔符冲突：任何解析都不能按 `; ` 简单切分，必须按 `covered_ids` 对照原词表取词条（`render_pdf.py` 就是这么做的）。
2. **CSV 转义**：`covered_ids` 含英文逗号，读写统一走 python `csv` 模块；文件带 BOM 方便 Excel，行尾 CRLF。
3. **IPA 字体**：音标必须走 DejaVu Sans 回退，否则渲染成方框。
4. **句型服从词表顺序**：`there` 的 id 是 125，所以 there be 句型推迟到 S18；S44/S46 的时间用阿拉伯数字（7 o'clock），因为数词 one-nine 是 S49-50 才学的新词。
5. **命名**：产出文件一律带 `420-primary-school-` 前缀，别退回 `sentences.csv/.pdf`（会与其他词表项目撞名）。
6. **世界观类问题**：称谓必须带姓氏、哈利父母双亡不能写"我妈妈"、霍格沃茨不设英语/数学/体育课、画像不会打球、成年教师不跟学生排名……详见 `worklog.md` 第十节的检查表；第五次修订一次改了 33 行，全部出在这一类。

## 修订历史

| 修订 | 内容 |
|---|---|
| 初版 | 6 批并行生成 60 句 → 合并 → 覆盖校验 → PDF 30 页 |
| plan2 | ① 复习改滚动式（原来固定钉在 6 个"复习句"上）② S32 `pink football` → `pink socks` ③ 字号整体放大 15-20% |
| 第三次 | 强调背诵 + 背写：回读文案统一改为"请重新朗读背诵第 X 天的句子"，PDF Howto 同步强化 |
| 第四次 | 产物改名 `sentences.csv/.pdf` → `420-primary-school-sentences.csv/.pdf`；新增 Howto 前两页，全书 32 页 |
| 第五次 | 内容审查：修正称谓 / 世界观 / 场景 / 地道性 / 中英一致共 33 行（词表与 7 词覆盖区间未动），新增 `plan/validate.py` |
