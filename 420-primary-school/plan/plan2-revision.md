# 修订计划 plan2：滚动复习 / S32 内容修正 / PDF 字号加大

针对用户反馈的三点修订。基础产物：`420-primary-school-sentences.csv`、`420-primary-school-sentences.pdf`（见 plan.md 的第一版计划）。

## 需求 1：复习逻辑改为滚动式（艾宾浩斯遗忘曲线）

现状问题：回读任务固定钉在 Day 3/7/14/21/30/45 六个"复习句"上，其他天没有回读任务，不符合遗忘曲线的滚动复习原理。

改法：
- 采用经典艾宾浩斯复习间隔：**学习后第 1、2、4、7、15、30 天**各复习一次。
- 对每一天 d（d ≥ 2），当日回读任务 = 集合 { d-1, d-2, d-4, d-7, d-15, d-30 } 中 ≥ 1 的天。
  - 例：Day 2 回读 Day 1；Day 8 回读 Day 7、6、4、1；Day 16 回读 Day 15、14、12、9、1；Day 45 回读 Day 44、43、41、38、30、15。
- 这样每个句子都会被后续恰好 6 天回读（第 46 天以后学习的句子复习次数自然收尾），复习是每天滚动的，不再有"复习句/非复习句"之分。
- review_note 列改造：
  - 每行开头统一为"今日回读：请重新朗读第 X、Y、Z 天的句子。"（Day 1 无回读，保留原说明）；
  - 删除原来六个固定复习句里的旧回读句（"今日回读：请重新朗读第 1-2 天的句子"等）以及与旧固定区间绑定的"重点回顾/重点复习…"从句；
  - 保留各行原有的"重现旧词：…"自然复现说明（这是句子层面的词汇循环，仍然成立）。
- PDF 排版同步：原来只有 6 天有"今日回读"徽章；改为**每天**卡片上都显示"今日回读：Day X / Y / Z"信息条（醒目小色块），Day 1 显示"第 1 天，大声朗读 3 遍"。

## 需求 2：S32 "pink football" 内容修正

现状：S32 "…put their pink football under the bed." —— 粉红色足球不合常理，且"全体学生共放一个足球"语义别扭。

改法（保持 S32 的 7 个新词 pink/always/night/think/all/listen/football 不变，只用旧词改写）：
- 新句："At night, all the students always listen and think, and Ron puts his football and pink socks under the bed."
- pink 改修饰 sock（旧词，id 72；罗恩的粉红袜子符合韦斯莱家的幽默感），football 单独作宾语。
- 同步更新 sentence_zh、grammar（保留"频率副词 always 位置 / at night / 并列动词"讲解）、phrases（at night、under the bed、pink socks）、review_note（按新滚动规则 + 重现旧词 sock/put/his/under/bed）。
- 校验：改写后 7 个新词仍全部真实出现在句中，covered_ids 不变。

## 需求 3：PDF 字号加大

现状：英文句 14pt、中文/正文 10.5pt、语法 9.5pt、生词 9.5-10.5pt、复习说明 9pt —— 对孩子偏小。

改法（plan/render_pdf.py 的 CSS，整体放大约 15-20%）：
- 英文句 14pt → 17pt；中文 10.5pt → 12pt
- Day 标题 12pt → 13.5pt；语法区 9.5pt → 11pt
- 生词/短语词条 9.5pt → 11pt（英文词 10.5pt → 12pt，词性 8pt → 9pt）
- 复习/回读说明 9pt → 10.5pt；页眉页脚 9pt → 10pt
- 行高、卡片间距微调保持不拥挤；页数会从 30 页增加（预计 35-40 页），可接受，仍要求无大面积空白、卡片不被页切断开。
- 重新渲染后用 PyMuPDF 转图抽查首页、中间页、末页。

## 执行与提交顺序（每步落盘即 commit + push）

1. ✅ worklog.md（第一版，已提交 d6cee18）
2. ✅ 本计划文件 plan/plan2-revision.md → commit push（b740401）
3. ✅ 改 420-primary-school-sentences.csv（滚动 review_note 60 行 + S32 改写），跑全量校验（420 覆盖、新词在句中、8 列格式、回读天数正确性，全部通过）→ commit push（7d98ef6）；batches/ 已按修订后内容重新拆分保持一致
4. ✅ 改 render_pdf.py 字号与每日回读条，重渲染 420-primary-school-sentences.pdf，转图抽查（30 页，每页两卡，页底留白 10-21%）→ commit push（074a94b）
5. ✅ 更新 worklog.md（记录本次修订的决策与新逻辑）→ commit push（f9f3c15）
