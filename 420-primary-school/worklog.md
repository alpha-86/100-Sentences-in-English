# 生成过程与选择逻辑 Worklog

记录 `420-primary-school-sentences.csv`（60 句）与 `420-primary-school-sentences.pdf` 的生成过程，以及单词、句子、短语、语法的选择逻辑。原始需求见 `prompts/1-420-primary-school-001.md`，执行计划见 `plan/plan.md`（第一版）与 `plan/plan2-revision.md`（修订版，当前生效）。

## 一、整体流程

1. **读需求 + 制定计划**：确认核心约束是"60 句覆盖 420 词"（420 = 60 × 7，即每句恰好 7 个新词），并把故事线、语法进阶、复习节奏一次性写进 `plan/plan.md`，作为后续所有批次的统一契约。
2. **6 个并行子代理分批生成**：每个代理负责 10 句（连续的 70 个词），各自写入独立的 `batches/batchN.csv`，避免并发写同一文件。每个代理只读取自己负责的 CSV 行区间（单词 id = 行号 - 1），并自检"70 词各出现一次、每词真实出现在句中、格式 8 列"。
3. **合并 + 机器校验**：合并 6 个批次为 `420-primary-school-sentences.csv`（加表头，UTF-8 带 BOM），跑校验脚本确认：
   - 60 行 × 8 列，id 1-60 连续；
   - 420 个词每个恰好被覆盖一次，无遗漏、无重复、无表外词；
   - 每个新词（含复数/-ing/三单等变形）真实出现在对应英文句中；
   - new_words 的音标/词性/中文与原词表逐字一致；
   - 每一天的回读任务与滚动艾宾浩斯规则 {d-1, d-2, d-4, d-7, d-15, d-30} 完全一致（plan2 后）；
   - 不提前使用未学内容词（本句只允许 7 个新词 + id 更小的旧词 + 闭类功能词 + 角色名）。
   以上检查已固化为 `plan/validate.py`（第五次修订时整理成脚本，一条命令全量校验）。
4. **PDF 排版**：`plan/render_pdf.py`（weasyprint）渲染，PyMuPDF 转图抽查（首页、中间页、末页），确认无乱码（含 IPA 音标）、无大面积空白（页底留白 10-21%）、生词每行两个。
5. **提交推送**：rebase 整合远端需求文档修订后推送 main；此后每次文件生成/修改均单独 commit + push（见第八节提交序列）。

## 二、单词分配逻辑

- **固定映射**：句子 s 覆盖单词 id `(s-1)*7+1` 到 `s*7`，即按原词表行号顺切，每句恰好 7 个新词。词表本身按主题自然分段（问候 → 文具颜色 → 衣物家具 → 动物农场 → 家庭爱好 → 学校科目 → 活动三餐 → 时间购物 → 基数词 → 序数词 → 月份 → 星期），顺切即得主题块。
- **旧词复用**：句子只允许使用"本句 7 个新词 + id 更小的旧词 + 必要功能词 + 角色名（Harry/Ron/Hermione/Hagrid/Dumbledore/Hedwig/Hogwarts）"。这保证孩子每天遇到的生词恰好是当天词表里的 7 个，不会被未学词打断。
- **变形处理**：复数（chickens/tomatoes/sheep）、三单（lives/puts）、-ing（answering/working）、不规则变化（child→children）均允许，new_words 列记原形；词表自带标注的变形（如 `pl. children`）视为合规。
- **已知取舍**：
  - S44/S46 的时间表达用了阿拉伯数字（7 o'clock、half past 7），因为数词 one-nine 是 S49-50 才学的新词，提前用单词拼写会破坏"只学 7 个新词"的约束；
  - `there` 的 id 是 125，所以 there be 句型安排在它成为新词的 S18，S11 改写为 "Some socks are on the chair..." 避免提前使用；
  - S58/S59 要装下多个月份名，句子略长（约 18-20 词，问答双句结构），作为月份密集区的合理弹性；
  - Ms/Mr/Mrs 必须与姓氏连用（词表释义本身就写着"用于……姓氏或姓名前"），为此引入表外专有名词 **Smith**（Ms Smith＝一位女老师、Mr Smith＝哈利入学前的英语老师），全书仅此一个表外专名，详见第九节；
  - S39 的 walk 与 travel 同为当天新词，句子里的"walk and travel home"略显重复，属词块压缩的必然结果，保留。

## 三、句子选择逻辑

- **故事性**：60 句构成 6 幕连贯故事——入学第一天 → 宿舍与农场 → 朋友与家人 → 校园生活 → 日常作息与生日会 → 数字日期大综合（毕业庆祝收尾）。每幕内部句与句之间有情节衔接（如 S47 商店女士 → S48 写感谢卡；S58 猜聚会月份 → S59 揭晓在七月，呼应哈利生日）。
- **哈利·波特化用**：采用原著语感改编（分院帽式颜色问答、墙上会说话的画像一家人、飞行课式 PE、魔药课式 science），不照抄原文长句；专有名词限定为角色名、Hogwarts，以及第五次修订引入的教师姓氏 Smith（Ms Smith / Mr Smith）。
- **家庭句归属**：第一人称家庭句（Mum/Dad/grandpa/uncle/mother/grandmother）统一按**罗恩家**理解——原著里罗恩父母健在、有五个哥哥一个妹妹、有舅舅，且家里养鸡有院子，正好承接 S12-S19、S27-S28 的家庭与农场场景；哈利父母双亡、无兄弟姐妹，相关句子不得写成他的家人（第五次修订修正，见第九节）。
- **长度与可背性**：8-16 词为宜，每天 1 句；复习句和大结局句允许略长。
- **主题贴合词块**：每句的情节围绕当天 7 个新词所属的主题块设计（如动物词块安排在 Hagrid 农场场景，三餐词块安排在生日会筹备场景），让词义有画面依托。

## 四、短语选择逻辑

- 每句提取 **1-3 个**实用短语/搭配，格式 `短语|中文`。
- 来源必须是"本句新词 + 已学旧词"的真实搭配，不引入表外成分（如 S1 `How do you do?`、S14 `black cat`、S29 `play the piano`、S45 `get up` / `have dinner`）。
- 优先选择 KET 高频、可迁移到口语写作的搭配（`say thank you to sb.`、`read a lot`、`fly to the front`、`on Monday`）；同一句内新旧词组合的短语优先，兼顾复习价值。

## 五、语法/句型选择逻辑

- **进阶主线**（Think Starter → KET），与词块主题同步推进：
  | 幕 | 句 | 语法重点 |
  |---|---|---|
  | 1 | S1-10 | be 动词 am/is/are；祈使句；自我介绍；what 疑问句；颜色作表语/定语 |
  | 2 | S11-20 | there be；介词 on/under/behind；复数；this/these/those；have got；many+复数 |
  | 3 | S21-30 | 一般现在时（含三单）；频率 often/every day；want to be；who/which 疑问句 |
  | 4 | S31-40 | 现在进行时；物主代词；why/because；between/in front of；动词+宾格 |
  | 5 | S41-50 | can 表能力；o'clock/half past；before/after；will 将来时 |
  | 6 | S51-60 | 基数词/序数词/日期；in/on + 月份星期；when 疑问句；综合复习 |
- 每句的 grammar 列用中文简明讲 1-3 句，聚焦本句实际出现的语法点（如 S29 对比"乐器加 the / 球类不加 the"，S54 讲序数词构成），不泛泛罗列。
- 句型与词表顺序冲突时，服从词表顺序（如前述 there be 后移到 S18）。

## 六、复习设计（艾宾浩斯）——滚动式（plan2 修订后）

- **滚动回读**：采用经典艾宾浩斯复习间隔 **1、2、4、7、15、30 天**。每一天 d（d ≥ 2）的回读任务 = { d-1, d-2, d-4, d-7, d-15, d-30 } 中 ≥ 1 的天，写在 review_note 开头："今日回读：请重新朗读背诵第 X、Y、Z 天的句子。"
  - 例：Day 2 回读 Day 1；Day 8 回读 Day 7、6、4、1；Day 16 回读 Day 15、14、12、9、1；Day 45 回读 Day 44、43、41、38、30、15。
  - 每个句子恰好会被后续 6 天回读（第 46 天起的句子复习次数自然收尾），复习每天都在滚动，不再设固定"复习句"。
  - 由脚本统一生成全部 60 行的回读句并机器校验，杜绝手算错误。
- **回读要求：朗读 → 背诵 → 背写**（第三次修订起明确强调）：回读不是"再读一遍"就算完——先朗读，再合上书**背诵**整句，有时间就把整句**默写（背写）**一遍，写错的词重点练。新学句子的每日流程也同样以背诵 + 背写收尾（见 PDF Howto 的"学习步骤"第 5 步与"给家长的小建议"）。
- **自然复现**（句子层面的第二层循环，保持不变）：每句尽量编入旧词（如 S54 重现 fly/front、S60 重现 every/day/school/sing/dance/all），review_note 在回读句之后记录本句实际复现的词及出处天数。
- 首要原则始终是句子本身的合理性与故事性，复习复现在此基础上尽量安排。
- （plan2 前旧方案：回读任务固定钉在 Day 3/7/14/21/30/45 六个复习句上，已被滚动方案取代。）

## 七、踩过的坑（供下游维护参考）

1. **音标内含 `; `**（如 `/duː; də/`），与 new_words 的词条分隔符冲突：任何解析都不能按 `; ` 简单切分，应按 covered_ids 对照原词表取词条（`plan/render_pdf.py` 就是这么做的）。
2. **CSV 转义**：covered_ids 含英文逗号，写出/读回统一用 python csv 模块；420-primary-school-sentences.csv 带 BOM 方便 Excel 直接打开。
3. **配额中断**：首批并行代理因 5 小时用量限制 403 失败，恢复（resume）后全部完成；批次落盘到独立文件的设计让断点续跑没有产生任何冲突或重写。
4. **渲染环境**：无 poppler/pdftoppm，用 PyMuPDF 等效渲染检查；IPA 字符需 DejaVu Sans 字体回退，否则音标会变方框。
5. **字号与空白的平衡**（plan2）：字号整体放大 15-20% 后卡片变高，一度一句一页、页底留白约 50%；通过压缩页边距/卡片内边距/行高（而不是缩字号）把排版拉回每页两张卡片，全页底留白稳定在 10-21%。

## 八、修订记录 plan2（滚动复习 / S32 修正 / 字号加大）

计划文件：`plan/plan2-revision.md`。三项修订：

1. **复习逻辑改滚动式**：见第六节。删除原六个固定复习句的旧回读指令及绑定固定区间的"重点回顾"从句，保留各行"重现旧词"说明；PDF 上改为每天卡片都显示蓝色"今日回读"条（原来只有 6 天有橙色复习徽章）。
2. **S32 内容修正**：原句 "…put their pink football under the bed." 中 pink football 不合常理、且"全体学生共放一个足球"语义别扭。改写为 "At night, all the students always listen and think, and Ron puts his football and pink socks under the bed." —— pink 改修饰旧词 sock（罗恩的粉红袜子，符合韦斯莱家的幽默感），7 个新词（pink/always/night/think/all/listen/football）与 covered_ids 不变，中文、语法、短语、复习说明同步更新，改写后重新跑全量校验通过。
3. **PDF 字号加大**：英文句 14pt→16.5pt、正文 10.5pt→12pt、语法/生词/短语 9.5pt→11pt、英文单词 10.5pt→12pt、页眉页脚 9pt→10pt；配合间距压缩保持每页两张卡片、无大面积空白，最终 30 页。
4. **新增 Howto 首页**（后续追加）：把本 worklog 第一至六节提炼成使用说明，放在 PDF 前两页——第 1 页约 35% 为书名标题区（大标题 + 副标题 + 420 词/60 句/6 幕/60 天关键信息），其余 65% 与第 2 页为 Howto（这本书怎么用 / 每天回读 / 单词安排 / 故事与句子 / 语法进阶 / 一张卡片里有什么 / 给家长的小建议 / 给小朋友的话），`break-after: page` 让 Day 1 卡片从第 3 页开始；全书 32 页。
5. **强调背诵与背写**（第三次修订）：review_note 回读文案从"请重新朗读第 X 天的句子"统一改为"请重新朗读背诵第 X 天的句子"（59 行，脚本替换 + 机器校验）；PDF Howto 同步强化——学习步骤新增第 5 步"背诵（合上书背出整句）+ 背写（默写整句，错词红笔改 3 遍）"，每天回读、卡片结构说明、给家长的小建议、给小朋友的话各节均补上背诵/背写要求。
6. **产物改名（第四次修订）**：`sentences.csv` → `420-primary-school-sentences.csv`、`sentences.pdf` → `420-primary-school-sentences.pdf`（git mv）。原因：仓库将容纳多个词表项目（420 小学词、1500 KET 词……），通用名 `sentences.*` 无法区分归属，统一改为"项目名-用途"命名。同步更新了 `plan/render_pdf.py` 的路径常量、`plan/plan.md`、`plan/plan2-revision.md`、本 worklog 的全部引用；`prompts/2-1500-KET-001.md` 也已采用同款命名约定（`1500-KET-sentences.csv/.pdf`）。重渲染验证 32 页不变。

提交序列（每步落盘即 commit + push）：worklog 初版（d6cee18）→ plan2 计划（b740401）→ 420-primary-school-sentences.csv 修订（7d98ef6）→ PDF 重排（074a94b）→ 本 worklog 更新 → Howto 首页（aaabd29 / 6330532）→ 背诵背写强化（4e02de0）→ 新 prompt 2-1500-KET-001（f2150a8）→ 产物改名 → 内容审查修订 + `plan/validate.py`（第五次修订，见第九节）。

## 九、第五次修订（内容审查：称谓 / 世界观 / 场景 / 地道性）

起因：使用者通读 PDF 后指出 3 处硬伤——Day 5 `Are you a Ms?` 场景不成立（问的是"你是女士吗"，答话人却是男性名字）、Day 12 哈利有妈妈、Day 23 海德薇被比作熊猫。复查全部 60 句后，除这 3 处外又找出 30 余处同类问题，分五类一次修正完毕：**改 33 行**（句子、中文、语法、短语、复现说明同步更新），**词表、7 词覆盖区间、句型规划一律未动**，改完 `plan/validate.py` 全量通过，PDF 重渲染仍为 32 页、每页两张卡片。

1. **称谓词必须带姓氏**（4 处）。词表 id10/145/336 的释义自己就写着"用于女子的姓氏或姓名前""用于男子的姓氏或姓名前"，而原句写成了 `good morning, Ms!`（Day 2）、`Are you a Ms?`（Day 5）、`Mr Dumbledore`（Day 21，且邓布利多是 Professor）、`Dear Mrs,`（Day 48）——句子违反了词表自己的释义。改法：Day 2 `Ms Smith`、Day 21 `Mr Smith`、Day 48 `Dear Mrs Weasley`；Day 5 整句重写为 `We are a good class! Please call me Harry — your name is nice too. Goodbye!`（Ms 只是 S2 的旧词，不占 S5 的 7 词名额，删掉不影响覆盖）。为满足"称谓＋姓氏"，引入表外专名 **Smith**：原著没有列全霍格沃茨教职工，也没给哈利的小学老师起名，故不构成冲突；这是全书唯一的表外专名，已在第二节和第三节登记。
2. **哈利·波特世界观**（9 处）。原稿的家庭句（Mum / Dad / Grandpa / Uncle / my mother / my grandmother）按上下文都是哈利的家人，与原著冲突。整组家庭句统一归到**罗恩家**：Day 12 妈妈改口叫"Ron"，Day 13 补 `Welcome to my room, Harry!`（罗恩带哈利参观房间），Day 16 `My grandpa`、Day 18 `my uncle's`、Day 19 `His`＝那头猪、Day 27 改为 `"Is this my mother or my aunt?" says Ron. The children are his brothers, sisters and cousins.`。另三处：Day 21 `our English teacher` 明确为"去年"（入学前的小学，霍格沃茨不设英语课）；Day 49 护士送的蛋糕注明 `from Hagrid`（原著生日蛋糕来自海格）；Day 56 海格从"第 30 名"改为"第三十份礼物送给他"（成年教师不该跟学生一起排名）。
3. **场景 / 逻辑不通**（10 处）。Day 23 猫头鹰海德薇被比作"炎热中国的熊猫"，比喻不成立，改为两个各自独立的事实：`she is cute! Pandas in China are cute too, and China is hot.`；Day 20 把提问移到"交朋友"之前（先问名字再交朋友，原来顺序反了）；Day 25 画像不会打球，改 `we often play sports at Hogwarts`；Day 34 "在图书馆和后墙之间"与"在中间"两个定位打架，改为 `in the middle of the blackboard`；Day 45 `Does lunch begin before the film?` 改为 `Does the film begin before lunch?`（午餐不会"开始"）；Day 46 把"一小时 60 分钟"接进剧情（`a lesson on the ice for an hour — 60 minutes!`）；Day 49 `hears the door` 改为 `hears the door open`；Day 50/51 同一个生日蛋糕蜡烛数自相矛盾（3-9 根 vs 10-16 根），Day 51 改为派对用的蜡烛摆在桌上；Day 55/56 的序数词列表补上落点（"礼物上的名字""第三十份礼物"），Day 57 序数词后补 day。
4. **英文地道性 / 小语法**（12 处）。Day 7 `in Hogwarts`→`at Hogwarts`（in 移到 `in the morning`）；Day 10 单只 `shoe`→`shoes`；Day 12 `can not`→`cannot`；Day 24 删赘余 `at home`；Day 31 `the girl`→`a girl`；Day 33 `in front of class`→`in front of the class`；Day 36 改写"every question is a good exercise and a good way"（问题不是"方法"，改为 `a good way to talk with people`）；Day 42 `cook … cake`→`make a cake`；Day 43 `the open park`→`The park is open — we visit it …`；Day 44 `When do we dress?`→`get dressed`；Day 58 `asks it`→`asks the question`；Day 60 `all the school`→`all the students`。
5. **中英一致**（2 处）。Day 59 中文"赫敏**笑着**说"英文并无"笑着"，中文改回"赫敏说"；Day 10 中文"鞋子"与英文单复数对齐。

附带查出并修掉的**用词顺序泄漏**：Day 5 用了 `no`（id 82，第 12 天才学），是全书唯一的"提前用词"，已随整句重写消除。

新工具 `plan/validate.py`：把原先散在各批次里的自检整理成一条命令，检查结构（60×8、id 连续）、覆盖（420 词恰好一次）、new_words 逐字一致、词形出现（含复数/三单/-ing 变形，`cannot` 视为包含 `not`）、滚动回读规则、用词顺序（不提前使用未学内容词，闭类功能词豁免）、文件格式（BOM + CRLF）。本次修订的 `no` 泄漏即由第 6 项查出；后续 1500-KET 可直接复用。

## 十、世界观与称谓检查表（后续项目复用）

下一册开工前先把这几条写成硬约束，否则多个并行批次各写各的场景，本次这一类问题必然重演：

1. **角色家庭与身份**：逐个角色写明家人是否在世。哈利——父母双亡、无兄弟姐妹、祖父母无在世设定、只有姨父姨妈一家亲戚；罗恩——父母健在、五个哥哥一个妹妹、有舅舅。凡"我妈妈 / 我爷爷"这类第一人称家庭句，要么写明说话人，要么整组归给同一个角色。
2. **称谓词**：Ms / Mrs / Mr / Miss 一律"称谓 + 姓氏"，不能单用、不能加 a；同时分清 Miss（英式小学学生喊女老师）与 Ms。造这类句子前先定好配哪个姓氏（原著姓氏 Weasley / Granger 等，或统一引入一个表外专名并登记）。
3. **学校与课程**：霍格沃茨不设英语课、数学课、体育课；science / PE 走"魔药课 / 飞行课"的化用路线；"我们的英语老师"这类表述必须说明是入学前的小学。
4. **场景自洽**：一句话里只留一个时空和指代；画像不会打球，成年教师不跟学生排名，同一件物品的数量前后一致（生日蛋糕的蜡烛数）。
5. **代词指代**：his / her / they 必须有明确先行词，不能"读者自己猜"。
6. **中英一致**：中文不得出现英文里没有的信息（"笑着说"），单复数两边对齐。
7. **用词顺序**：句子只允许"本句 7 个新词 + id 更小的旧词 + 闭类功能词 + 角色名"，每批写完立刻跑 `plan/validate.py`。
