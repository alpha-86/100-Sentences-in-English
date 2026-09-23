# plan002：1500 KET 词 → 100 句生成执行计划

> 输入：`1500-KET/1500-KET.csv`（v2，2026-09-22 定稿，1500 词，validate_vocab.py 全绿）
> 上游 plan：`plan/001-vocab-review-and-fix-plan.md`（词表修复，已完成）
> 本 plan 覆盖：`prompts/2-1500-KET-001.md` 第 1-7 节的执行方案——词分配表、分幕故事线、语法进阶表、白名单、CSV/复习规则、分批生成与校验流程。
> 词分配数据与校验器：`scripts/allocate_words.py` + `scripts/allocation/act01-10.py`（分配表由脚本渲染，改数据后重跑，**禁止手改分配表**）。

---

## 1. 数量口径与硬约束（摘自需求，执行中不得突破）

- 100 句、1500 词、每天新学 **12-18** 词（句中 8-15 + 扩展必背 ≤10），100 天合计恰好 1500，每个词恰好分配一次。
- 句中新词必须真实出现在英文句中（变形允许，列记原形）；扩展必背词不要求出现在句中，但**锚词必须在句中**。
- 句中内容词 ∈ {本句新词} ∪ {更早天数的词} ∪ {闭类功能词} ∪ {白名单专名}；不得引入词表外实词。
- 单句词数与相邻句 ±1 微调允许，但必须记入 plan/worklog，总覆盖不变（当前分配已平衡，预计无需微调）。

---

## 2. 分幕故事线：《露西的百天日记》（原创，10 幕）

**原创故事，不借用任何现成作品的角色/世界观**（吸取上一版哈利·波特设定冲突的教训：孤儿写妈妈、课程写错、角色年龄错位）。主角是 12 岁的 Lucy Carter，故事以她的日记视角贯穿 100 天，季节线与词家族排布对齐。

| 幕 | 天数 | 时间 | 剧情 | 语法主线 |
|---|---|---|---|---|
| 1 | 1-10 | 九月初 | Carter 一家搬到海边小镇 Seaview，看新家、数房间、认家人、拜访邻居、买文具 | be、there be、祈使句、介词、人称代词 |
| 2 | 11-20 | 九月中 | Seaview School 开学：科目表、作息、星期月份、结交同桌 Lily 和足球迷 Sam | 一般现在时、疑问句、疑问词 |
| 3 | 21-30 | 九月下 | 新朋友与日常：课外活动、校园规则、农场与动物园（Bingo 登场）、食物、时间表达 | 现在进行时、can/could、must/have to |
| 4 | 31-40 | 十月 | 秋天与购物：秋叶、天气、衣橱、逛街、钱币价格、日期序数、方位介词 | must/have to 深化、否定、祈使强化 |
| 5 | 41-50 | 十月底-十一月 | 秋季运动会（过去时上线讲述赛果）、万圣节派对、身体与健康、情绪与想法 | **一般过去时上线**、时间表达 |
| 6 | 51-60 | 十一月-十二月初 | 入冬（室内冰场）、居家与做饭、餐厅、做家务、邮局银行、职业认知 | 一般过去时核心、will 预告 |
| 7 | 61-70 | 十二月 | 圣诞与新年：贺卡、祖孙同堂、学校音乐会、比较级上线、现在完成时入门 | 将来时 will/shall、比较级入门、现在完成时入门 |
| 8 | 71-80 | 圣诞假期 | 全家飞澳大利亚（南半球夏天！）：海滩、雨林露营、悉尼观光、国家地理、电子媒体 | 比较级/最高级巩固、现在完成时巩固、被动入门 |
| 9 | 81-90 | 一月末 | 返校：考试周、学校演出、状语从句主题日（because/when/if）、转述与通信、材质时尚、梦想未来 | because/when/while/until/if 从句、宾语从句 |
| 10 | 91-100 | 二月 | 尾声与展望：度量衡、健康生活、冬季运动回味、综合复习，Day 100 百天收官 | 间接引语入门、综合复习 |

**角色圣经（设定一致性基准）**

- **Lucy Carter**：12 岁，叙述者，喜欢画画和游泳；日记体贯穿。
- **Tom Carter**：7 岁弟弟，调皮，爱恐龙和足球。
- **Mr Carter / Dad**：工程师（engineer，词表）；Mrs Carter / Mum：医生（doctor，词表），十二月底有学术会议在悉尼 → 全家同行度假（剧情桥）。
- **Bingo**：家养小狗（dog），第 25 天前后登场。
- **Miss Green**：班主任；**Lily**：Lucy 同桌、好友；**Sam**：同班足球迷。
- **Grandpa & Grandma Carter**：圣诞来访；**Aunt Kate & cousin Ella**：通信/明信片戏份（pen-friend 日）。
- 季节校验锚点：九月开学（教师节日前后）、十月底 Halloween、十二月圣诞、圣诞假期赴澳（南半球夏季解决 summer/beach/swimming 词族的时令冲突）、一月末返校、二月初春将至（spring 词上线不违和）。

**内容校验清单（每批生成后必查，需求 §2.4/§2.5）**
1. 搭配自然（反例：pink football）；
2. 人物关系一致（谁在说话、对谁、符合角色圣经）；
3. 时间/季节/场景一致（反例：生日在夏天出现滑冰课；本剧用"室内冰场"化解十一月冰雪词）；
4. 前后句情节衔接自洽（每批 10 句要与上一批末句接得上）；
5. 扩展组确实同类/反义/同族（反例：red 与 Monday 同组）。

---

## 3. 语法进阶表与"依赖词先上线"校验

句型与学习顺序冲突时**服从词分配表**（需求 §3.3，上一版 there be 早于 there 的教训）。分配脚本内置软门禁 `DEADLINE`（`allocate_words.py`），关键依赖词的最晚上线天：

| 依赖词 | 上线天 | 服务的语法/幕 |
|---|---|---|
| be, there | D1 | 幕 1 there be |
| have / have got | D2 | 幕 1 拥有句 |
| do, 疑问词 what/where/when/who/whose/which/how/why | D11/D14 | 幕 2 疑问句 |
| because | D19 | 幕 2 起因表达、幕 9 because 从句 |
| can / could | D23 | 幕 3 能力 |
| must / have to / should | D24 | 幕 3-4 规则与义务 |
| ago / yesterday / last | D16/D46 | 幕 5 一般过去时 |
| will | D57 | 幕 6-7 将来时（shall D65 同幕呼应） |
| than / more / most / better / less | D64 | 幕 7-8 比较级 |
| ever / already / yet / since | D66 | 幕 7-8 现在完成时 |
| while / until / till | D83 | 幕 9 时间状语从句 |
| if | D84 | 幕 9 条件句 |
| would | D90 | 幕 9 委婉表达 |

被动语态入门（幕 8）：用 be（D1）+ 过去分词（taught/done/seen 等变形允许），无生词依赖。
间接引语（幕 10）：say/tell（D74 已学）+ 宾语从句语序，天然衔接。

---

## 4. 词分配总表（100 天）

分配设计要点：

1. **家族同日/相邻**：星期（D15）、月份（D16）、基数 1-10/11-20（D8/D9）、整十与单位（D36-37）、序数（D37-39，借价格与日期场景）、颜色（D10/D89）、身体（D44）、职业（D59-60）、国家国籍（D75-77）、运动（D22/D51/D96）等成组落位。
2. **扩展必背词组的三种形态**（详见每日块）：
   - 同类家族：句中出现锚词，其余成员进扩展（如 D15 Monday 在句，Tuesday-Sunday 进"星期名"组）；
   - 词族/短语族：look 短语（D21）、listen to（D21）、邮政复习（D97）；
   - 反义/对比复习：混入**更早天数的已学词**（标注"复习·D N"，不计入 covered_ids），如 D50 反义形容词复习、D99 方位复习。
3. **语法词前置**：功能词/情态词/从句引导词按 §3 表提前铺到对应幕之前。
4. **来源天标注**：扩展组内复习旧词一律标"（复习·D N）"，与 review_note 复现说明呼应。
5. 每日块格式：`句中新词 N 个`（必须全部真实出现在英文句中）+ `扩展必背词`（组说明（锚词：X）：成员）。

## 第 1 幕词分配（Day 1-10）

### Day 1｜第 1 幕｜搬家日：抵达新家
句中新词 14 个：**a, an**、**be**、**the**、**and**、**in**、**on**、**I**、**we**、**our**、**new**、**home**、**house**、**town**、**there**
扩展必背词 3 个：
- 房屋与院落（锚词：house）：garden、gate、wall

### Day 2｜第 1 幕｜看新家：there be 数房间
句中新词 15 个：**have**、**have got**、**here**、**room**、**door**、**window**、**floor**、**bedroom**、**kitchen**、**big**、**small**、**it**、**you**、**your**、**this**
扩展必背词 3 个：
- 更多房间（锚词：room）：bathroom、toilet、hall

### Day 3｜第 1 幕｜家庭成员
句中新词 11 个：**family**、**father**、**mother**、**brother**、**sister**、**baby**、**parent**、**son**、**they**、**he**、**she**
扩展必背词 6 个：
- 家庭称呼（锚词：father）：dad、mummy、grandpa、grandma
- 女儿与姑姨（锚词：sister）：daughter、aunt

### Day 4｜第 1 幕｜搬家具
句中新词 12 个：**furniture**、**table**、**chair**、**desk**、**bed**、**sofa**、**lamp**、**clock**、**fridge**、**cupboard**、**my**、**me**
扩展必背词 4 个：
- 收纳与床品（锚词：bed）：bookshelf、shelf、pillow、blanket

### Day 5｜第 1 幕｜整理箱子
句中新词 12 个：**box**、**bag**、**put**、**carry**、**open**、**close**、**thing**、**heavy**、**empty**、**with**、**for**、**from**
扩展必背词 3 个：
- 随身小物（锚词：bag）：wallet、purse、key

### Day 6｜第 1 幕｜镇上初探
句中新词 11 个：**shop**、**supermarket**、**park**、**road**、**bridge**、**river**、**hill**、**place**、**near**、**old**、**us**
扩展必背词 2 个：
- 更多场所（锚词：shop）：market、bookshop

### Day 7｜第 1 幕｜拜访邻居
句中新词 13 个：**neighbour**、**meet**、**name**、**nice**、**welcome**、**glad**、**hello**、**goodbye**、**at**、**to**、**of**、**Mr**、**Mrs**
扩展必背词 5 个：
- 礼貌用语（锚词：hello）：please、thank、sorry、cheers、pardon

### Day 8｜第 1 幕｜数新家：数字 1-10
句中新词 10 个：**three**、**five**、**eight**、**boy**、**girl**、**dog**、**cat**、**age**、**by**、**not**
扩展必背词 7 个：
- 基数词 1-10（锚词：five）：one、two、four、six、seven、nine、ten

### Day 9｜第 1 幕｜数字 11-20
句中新词 9 个：**twelve**、**fifteen**、**twenty**、**zero**、**man**、**woman**、**child**、**adult**、**no**
扩展必背词 7 个：
- 基数词 11-20（锚词：twelve）：eleven、thirteen、fourteen、sixteen、seventeen、eighteen、nineteen

### Day 10｜第 1 幕｜买文具：颜色
句中新词 10 个：**colour**、**red**、**blue**、**yellow**、**schoolbag**、**pen**、**pencil**、**ruler**、**rubber**、**sharpener**
扩展必背词 6 个：
- 常见颜色（锚词：blue）：green、black、white、grey、pink、purple


## 第 2 幕词分配（Day 11-20）

### Day 11｜第 2 幕｜开学第一天
句中新词 13 个：**school**、**classroom**、**class**、**classmate**、**teacher**、**pupil**、**lesson**、**book**、**notebook**、**dictionary**、**crayon**、**scissors**、**do**
扩展必背词 4 个：
- 书籍与纸页（锚词：book）：text book、page、diary
- 同班同学（锚词：classmate）：class member

### Day 12｜第 2 幕｜科目表
句中新词 11 个：**subject**、**mathematics**、**science**、**geography**、**history**、**art**、**music**、**Chinese**、**difficult**、**easy**、**favourite**
扩展必背词 3 个：
- 学期与课程（锚词：subject）：term、course、studies

### Day 13｜第 2 幕｜每日作息
句中新词 12 个：**go**、**get**、**get up**、**up**、**morning**、**breakfast**、**eat**、**hungry**、**thirsty**、**down**、**out**、**but**
扩展必背词 4 个：
- 一日三餐（锚词：breakfast）：lunch、dinner、supper、meal

### Day 14｜第 2 幕｜疑问词大扫除
句中新词 10 个：**what**、**where**、**when**、**who**、**whose**、**which**、**how**、**why**、**question**、**answer**
扩展必背词 8 个：
- any- 不定代词（锚词：who）：anybody、anyone、anything、anywhere
- some- 不定代词（锚词：who）：somebody、someone、something、somewhere

### Day 15｜第 2 幕｜星期与周末
句中新词 11 个：**Monday**、**Friday**、**week**、**weekend**、**weekday**、**today**、**now**、**then**、**daily**、**after**、**before**
扩展必背词 5 个：
- 星期名（锚词：Monday）：Tuesday、Wednesday、Thursday、Saturday、Sunday

### Day 16｜第 2 幕｜月份与生日
句中新词 8 个：**September**、**October**、**month**、**date**、**year**、**birthday**、**soon**、**yesterday**
扩展必背词 10 个：
- 月份名（锚词：September）：January、February、March、April、May、June、July、August、November、December

### Day 17｜第 2 幕｜频率副词
句中新词 15 个：**always**、**usually**、**often**、**sometimes**、**never**、**every**、**each**、**all**、**both**、**many**、**much**、**few**、**very**、**too**、**so**
扩展必背词 3 个：
- 数量词（锚词：many）：lot、lots、little

### Day 18｜第 2 幕｜不定代词与代词收尾
句中新词 12 个：**everybody**、**everyone**、**everything**、**everywhere**、**nobody**、**no one**、**nothing**、**none**、**nowhere**、**them**、**him**、**their**
扩展必背词 5 个：
- 物主代词（锚词：their）：mine、yours、hers、ours、theirs

### Day 19｜第 2 幕｜兴趣爱好
句中新词 15 个：**like**、**love**、**enjoy**、**because**、**hobby**、**game**、**play**、**fun**、**funny**、**interesting**、**boring**、**cartoon**、**doll**、**toy**、**kite**

### Day 20｜第 2 幕｜学校场所
句中新词 12 个：**library**、**playground**、**gym**、**office**、**staff**、**group**、**project**、**meeting**、**computer**、**internet**、**online**、**keyboard**


## 第 3 幕词分配（Day 21-30）

### Day 21｜第 3 幕｜此刻正在进行
句中新词 10 个：**look**、**listen**、**read**、**write**、**sit**、**stand**、**walk**、**watch**、**see**、**make**
扩展必背词 5 个：
- look 短语家族（锚词：look）：look at、look for、look out、look after
- listen 短语（锚词：listen）：listen to

### Day 22｜第 3 幕｜球类运动
句中新词 13 个：**sport**、**football**、**basketball**、**volleyball**、**table-tennis**、**tennis**、**badminton**、**baseball**、**match**、**team**、**player**、**ball**、**club**
扩展必背词 4 个：
- 球类补充（锚词：football）：golf、hockey、bat、racket

### Day 23｜第 3 幕｜我会做的事
句中新词 11 个：**can**、**could**、**swim**、**dance**、**sing**、**draw**、**ride**、**jump**、**kick**、**throw**、**climb**
扩展必背词 3 个：
- 艺术表演者（锚词：dance）：dancer、singer、artist

### Day 24｜第 3 幕｜校园规则
句中新词 12 个：**must**、**have to**、**should**、**hurry**、**wait**、**stop**、**careful**、**quiet**、**slow**、**fast**、**early**、**late**
扩展必背词 3 个：
- 方式副词（锚词：careful）：carefully、quick、quickly

### Day 25｜第 3 幕｜农场动物
句中新词 12 个：**animal**、**bird**、**fish**、**mouse**、**rabbit**、**duck**、**chicken**、**cow**、**horse**、**farm**、**farmer**、**pet**
扩展必背词 3 个：
- 动物补充（锚词：animal）：parrot、bear、camel

### Day 26｜第 3 幕｜动物园
句中新词 13 个：**zoo**、**lion**、**tiger**、**elephant**、**monkey**、**snake**、**dinosaur**、**dolphin**、**whale**、**insect**、**wild**、**huge**、**tiny**
扩展必背词 1 个：
- 昆虫与飞虫（锚词：insect）：fly

### Day 27｜第 3 幕｜主食与调味
句中新词 10 个：**food**、**bread**、**rice**、**noodles**、**egg**、**soup**、**potato**、**meat**、**cheese**、**butter**
扩展必背词 4 个：
- 调味品（锚词：butter）：salt、sugar、oil、pepper

### Day 28｜第 3 幕｜水果蔬菜
句中新词 10 个：**fruit**、**apple**、**banana**、**orange**、**grape**、**strawberry**、**mango**、**lemon**、**vegetable**、**salad**
扩展必背词 4 个：
- 更多果蔬（锚词：fruit）：peach、pear、carrot、onion

### Day 29｜第 3 幕｜饮料与点心
句中新词 11 个：**drink**、**water**、**milk**、**juice**、**tea**、**coffee**、**cola**、**milkshake**、**ice cream**、**chocolate**、**cake**
扩展必背词 4 个：
- 甜味点心（锚词：cake）：biscuit、sweet、honey、jam

### Day 30｜第 3 幕｜时间表达
句中新词 12 个：**o'clock**、**half past**、**quarter**、**a.m.**、**p.m.**、**hour**、**minute**、**second**、**moment**、**time**、**tonight**、**tomorrow**
扩展必背词 2 个：
- 一天中的时刻（锚词：time）：midnight、noon


## 第 4 幕词分配（Day 31-40）

### Day 31｜第 4 幕｜秋天的景色
句中新词 13 个：**autumn**、**wind**、**windy**、**sky**、**fall**、**tree**、**wood**、**forest**、**grass**、**field**、**flower**、**plant**、**grow**
扩展必背词 2 个：
- 云家族（锚词：wind）：cloud、cloudy

### Day 32｜第 4 幕｜天气怎么样
句中新词 11 个：**weather**、**rain**、**rainy**、**sun**、**sunny**、**warm**、**cool**、**hot**、**cold**、**dry**、**wet**
扩展必背词 4 个：
- 天气补充（锚词：rain）：storm、fog、foggy、rainbow

### Day 33｜第 4 幕｜秋季衣橱
句中新词 12 个：**clothes**、**T-shirt**、**jeans**、**sweater**、**jacket**、**coat**、**shirt**、**skirt**、**dress**、**blouse**、**suit**、**tie**
扩展必背词 3 个：
- 下装（锚词：jeans）：trousers、shorts、tights

### Day 34｜第 4 幕｜鞋帽与穿戴
句中新词 10 个：**wear**、**put on**、**try on**、**shoes**、**boots**、**sock**、**hat**、**cap**、**scarf**、**gloves**
扩展必背词 2 个：
- 配饰（锚词：hat）：belt、glasses

### Day 35｜第 4 幕｜逛街购物
句中新词 12 个：**shopping**、**buy**、**sell**、**price**、**cost**、**pay**、**money**、**cheap**、**expensive**、**discount**、**size**、**spend**
扩展必背词 2 个：
- 促销相关（锚词：price）：sale、for sale

### Day 36｜第 4 幕｜钱币与价格
句中新词 11 个：**pound**、**dollar**、**euro**、**penny**、**pence**、**cent**、**cash**、**credit card**、**cheque**、**fifty**、**hundred**
扩展必背词 6 个：
- 整十数（锚词：fifty）：thirty、forty、sixty、seventy、eighty、ninety

### Day 37｜第 4 幕｜数字大单位与序数开头
句中新词 10 个：**thousand**、**million**、**dozen**、**double**、**first**、**third**、**number**、**whole**、**enough**、**certain**
扩展必背词 7 个：
- 序数词 4-10（锚词：third）：fourth、fifth、sixth、seventh、eighth、ninth、tenth

### Day 38｜第 4 幕｜日期里的序数
句中新词 8 个：**eleventh**、**twelfth**、**twentieth**、**several**、**once**、**twice**、**again**、**just**
扩展必背词 7 个：
- 序数词 13-19（锚词：twelfth）：thirteenth、fourteenth、fifteenth、sixteenth、seventeenth、eighteenth、nineteenth

### Day 39｜第 4 幕｜序数收尾
句中新词 8 个：**twenty-first**、**twenty-fifth**、**thirty-first**、**about**、**almost**、**nearly**、**per**、**total**
扩展必背词 8 个：
- 序数词其余（锚词：twenty-first）：twenty-second、twenty-third、twenty-fourth、twenty-sixth、twenty-seventh、twenty-eighth、twenty-ninth、thirtieth

### Day 40｜第 4 幕｜方位介词
句中新词 8 个：**across**、**along**、**through**、**past**、**over**、**under**、**left**、**right**
扩展必背词 5 个：
- 位置介词（锚词：left）：behind、beside、between、above、below


## 第 5 幕词分配（Day 41-50）

### Day 41｜第 5 幕｜出行方位
句中新词 14 个：**into**、**inside**、**outside**、**opposite**、**next to**、**in front of**、**around**、**straight on**、**turn**、**cross**、**corner**、**roundabout**、**street**、**straight**
扩展必背词 3 个：
- 接近类（锚词：next to）：close to
- 路口设施（锚词：cross）：crossing、crossroads

### Day 42｜第 5 幕｜日常交通工具
句中新词 11 个：**bus**、**bus stop**、**bus station**、**taxi**、**car**、**car park**、**bicycle**、**bike**、**drive**、**driver**、**traffic**
扩展必背词 3 个：
- 道路车辆（锚词：car）：lorry、van、motorbike

### Day 43｜第 5 幕｜长途与飞行
句中新词 11 个：**train**、**railway**、**railway station**、**platform**、**station**、**tram**、**underground**、**coach**、**plane**、**aeroplane**、**airport**
扩展必背词 3 个：
- 飞行相关（锚词：plane）：flight、helicopter、pilot

### Day 44｜第 5 幕｜身体部位
句中新词 12 个：**body**、**head**、**hair**、**eye**、**ear**、**nose**、**mouth**、**face**、**tooth**、**neck**、**hand**、**finger**
扩展必背词 6 个：
- 身体收尾（锚词：body）：thumb、toe、back、arm、leg、knee

### Day 45｜第 5 幕｜生病与就医
句中新词 10 个：**ill**、**sick**、**fever**、**cough**、**headache**、**pain**、**hurt**、**medicine**、**dentist**、**doctor**
扩展必背词 2 个：
- 医疗场所（锚词：doctor）：hospital、pharmacy

### Day 46｜第 5 幕｜运动会（过去时上线）
句中新词 11 个：**ago**、**last**、**race**、**score**、**goal**、**win**、**winner**、**take**、**bring**、**competition**、**excited**
扩展必背词 1 个：
- 输赢反义（锚词：win）：lose

### Day 47｜第 5 幕｜万圣节派对
句中新词 10 个：**Halloween**、**costume**、**dark**、**afraid**、**party**、**surprise**、**special**、**shout**、**terrible**、**strange**
扩展必背词 3 个：
- 派对相关（锚词：party）：guest、present、invite

### Day 48｜第 5 幕｜情绪表达
句中新词 12 个：**happy**、**sad**、**angry**、**surprised**、**bored**、**tired**、**alone**、**feel**、**cry**、**hate**、**worry**、**miss**
扩展必背词 1 个：
- un- 反义前缀（锚词：happy）：unhappy

### Day 49｜第 5 幕｜想法与记忆
句中新词 12 个：**think**、**know**、**believe**、**hope**、**wish**、**want**、**need**、**remember**、**forget**、**decide**、**mean**、**understand**
扩展必背词 1 个：
- 想法名词（锚词：think）：idea

### Day 50｜第 5 幕｜形容词反义对
句中新词 12 个：**tall**、**short**、**long**、**good**、**bad**、**beautiful**、**ugly**、**strong**、**weak**、**fat**、**thin**、**young**
扩展必背词 5 个：
- 反义形容词复习（锚词：tall）：big（复习·D2）、small（复习·D2）、old（复习·D6）、hot（复习·D32）、cold（复习·D32）


## 第 6 幕词分配（Day 51-60）

### Day 51｜第 6 幕｜入冬与冰雪运动
句中新词 10 个：**winter**、**ice**、**snow**、**snowy**、**skate**、**ski**、**heating**、**fire**、**degree**、**stormy**
扩展必背词 8 个：
- 冬季运动（锚词：ski）：skiing、ice skating、skating、snowboard、snowboarding
- 风暴家族（锚词：stormy）：thunderstorm、temperature、raincoat

### Day 52｜第 6 幕｜居家与洗浴
句中新词 10 个：**flat**、**apartment**、**stairs**、**upstairs**、**downstairs**、**lift**、**bath**、**shower**、**mirror**、**curtains**
扩展必背词 4 个：
- 洗漱用品（锚词：bath）：soap、towel、toothbrush、shampoo

### Day 53｜第 6 幕｜厨房做饭
句中新词 11 个：**cook**、**cooker**、**bake**、**boil**、**fry**、**grill**、**roast**、**cut**、**dish**、**wash up**、**during**
扩展必背词 2 个：
- 烹饪方式（锚词：fry）：fried、grilled

### Day 54｜第 6 幕｜世界各地的食物
句中新词 12 个：**pasta**、**pie**、**pizza**、**sausage**、**steak**、**chips**、**fast food**、**sandwich**、**omelette**、**pancake**、**toast**、**cereal**

### Day 55｜第 6 幕｜去餐厅
句中新词 13 个：**restaurant**、**menu**、**order**、**waiter**、**waitress**、**customer**、**bill**、**fork**、**knife**、**spoon**、**plate**、**bowl**、**main course**
扩展必背词 3 个：
- 餐具补充（锚词：plate）：cup、glass、bottle

### Day 56｜第 6 幕｜做家务
句中新词 11 个：**housework**、**tidy**、**tidy up**、**clean**、**cleaner**、**wash**、**help**、**dirty**、**husband**、**wife**、**single**
扩展必背词 2 个：
- 清洁工具（锚词：clean）：brush、comb

### Day 57｜第 6 幕｜邮局与银行
句中新词 11 个：**bank**、**post office**、**post**、**postman**、**postcard**、**stamp**、**envelope**、**letter**、**police**、**police station**、**will**
扩展必背词 2 个：
- 警察家族（锚词：police）：police officer、police car

### Day 58｜第 6 幕｜城镇地标
句中新词 9 个：**fire station**、**firefighter**、**museum**、**theatre**、**cathedral**、**castle**、**church**、**square**、**stadium**
扩展必背词 3 个：
- 文化场所（锚词：theatre）：cinema、disco、exhibition

### Day 59｜第 6 幕｜职业与工作
句中新词 11 个：**job**、**work**、**worker**、**occupation**、**career**、**boss**、**manager**、**secretary**、**colleague**、**businessman**、**businesswoman**
扩展必背词 3 个：
- 助理与店员（锚词：boss）：assistant、shop assistant、receptionist

### Day 60｜第 6 幕｜各行各业
句中新词 9 个：**nurse**、**writer**、**journalist**、**photographer**、**musician**、**painter**、**footballer**、**tennis player**、**engineer**
扩展必背词 6 个：
- 手艺与服务（锚词：nurse）：mechanic、chemist、hairdresser、gardener、guide、tour guide


## 第 7 幕词分配（Day 61-70）

### Day 61｜第 7 幕｜圣诞节
句中新词 11 个：**Christmas**、**New Year**、**festival**、**wishes**、**card**、**star**、**lights**、**member**、**give**、**congratulations**、**sincerely**
扩展必背词 3 个：
- 节日与庆典（锚词：Christmas）：Easter、wedding
- 贺卡用语（锚词：card）：dear

### Day 62｜第 7 幕｜祖孙同堂
句中新词 12 个：**grandfather**、**grandmother**、**grandparent**、**grandson**、**granddaughter**、**grandchild**、**granddad**、**uncle**、**cousin**、**nephew**、**niece**、**guy**
扩展必背词 3 个：
- 亲属总称（锚词：cousin）：person、people
- 婚姻（锚词：grandmother）：married

### Day 63｜第 7 幕｜音乐会
句中新词 12 个：**band**、**concert**、**drum**、**guitar**、**piano**、**violin**、**song**、**pop**、**rock**、**jazz**、**classical**、**fan**
扩展必背词 6 个：
- 音乐流派（锚词：jazz）：hip hop、rap、reggae、opera
- 乐器与载体（锚词：guitar）：instrument、CD

### Day 64｜第 7 幕｜比较级上线
句中新词 10 个：**than**、**more**、**most**、**better**、**less**、**high**、**low**、**large**、**narrow**、**wide**
扩展必背词 7 个：
- 程度副词（锚词：more）：quite、rather
- 反义复习（锚词：less）：small（复习·D2）、tall（复习·D50）、short（复习·D50）、easy（复习·D12）、difficult（复习·D12）

### Day 65｜第 7 幕｜制定计划
句中新词 15 个：**plan**、**shall**、**suppose**、**maybe**、**perhaps**、**immediately**、**possible**、**impossible**、**sure**、**of course**、**appointment**、**cafe**、**call**、**fine**、**far**
扩展必背词 2 个：
- 预约与地址（锚词：appointment）：address
- 肯定与确定（锚词：sure）：certainly

### Day 66｜第 7 幕｜现在完成时入门
句中新词 14 个：**ever**、**already**、**yet**、**since**、**still**、**happen**、**leave**、**return**、**find**、**begin**、**die**、**dead**、**learn**、**come**
扩展必背词 3 个：
- 生命阶段（锚词：die）：born、life、live

### Day 67｜第 7 幕｜动手动词
句中新词 13 个：**pull**、**push**、**hold**、**check**、**choose**、**collect**、**fill**、**fix**、**together**、**only**、**even**、**point**、**use**
扩展必背词 4 个：
- 拥有与借还（锚词：hold）：own、borrow、belong
- 短语动词（锚词：fill）：fill in

### Day 68｜第 7 幕｜赞不绝口
句中新词 12 个：**amazing**、**brilliant**、**excellent**、**fantastic**、**wonderful**、**perfect**、**pleasant**、**lovely**、**great**、**real**、**really**、**pretty**
扩展必背词 3 个：
- 好极了复习（锚词：brilliant）：nice（复习·D7）、good（复习·D50）、beautiful（复习·D50）

### Day 69｜第 7 幕｜品质形容词
句中新词 13 个：**important**、**clear**、**clever**、**correct**、**wrong**、**simple**、**normal**、**interested**、**famous**、**fair**、**healthy**、**free**、**modern**
扩展必背词 2 个：
- 平常与通常（锚词：normal）：usual
- 正确复习（锚词：correct）：right（复习·D40）

### Day 70｜第 7 幕｜意外与麻烦
句中新词 13 个：**accident**、**ambulance**、**insurance**、**problem**、**trouble**、**danger**、**dangerous**、**safe**、**save**、**repair**、**break**、**change**、**pity**
扩展必背词 2 个：
- 延误（锚词：accident）：delay、delayed


## 第 8 幕词分配（Day 71-80）

### Day 71｜第 8 幕｜打包出发
句中新词 11 个：**suitcase**、**luggage**、**pack**、**passport**、**ticket**、**hotel**、**arrive**、**stay**、**trip**、**journey**、**travel**
扩展必背词 6 个：
- 旅人（锚词：travel）：visit、visitor、tourist、tour
- 旅行服务（锚词：journey）：travel agent、tourist information centre

### Day 72｜第 8 幕｜海滩与泳池
句中新词 11 个：**beach**、**sea**、**summer**、**swimming pool**、**swimming costume**、**swimming**、**pool**、**umbrella**、**wave**、**surfboard**、**surfing**
扩展必背词 4 个：
- 水上运动（锚词：surfing）：surfboarding、windsurfing、sailing、sail

### Day 73｜第 8 幕｜雨林露营
句中新词 10 个：**camp**、**campsite**、**tent**、**barbecue**、**rainforest**、**explore**、**explorer**、**adventure**、**map**、**guidebook**
扩展必背词 2 个：
- 船与航行（锚词：map）：boat、ship

### Day 74｜第 8 幕｜在澳大利亚
句中新词 12 个：**Australia**、**Australian**、**foreign**、**language**、**speak**、**tell**、**say**、**talk**、**conversation**、**sentence**、**spell**、**surname**
扩展必背词 2 个：
- 姓名（锚词：surname）：first name
- 语言元素（锚词：language）：article

### Day 75｜第 8 幕｜城镇与乡村
句中新词 10 个：**country**、**city**、**countryside**、**village**、**world**、**area**、**centre**、**crowd**、**crowded**、**city centre**
扩展必背词 6 个：
- 大洲（锚词：world）：Africa、Asia、Europe、North America、South America、Antarctica

### Day 76｜第 8 幕｜国家与国籍 1
句中新词 8 个：**China**、**Japan**、**Japanese**、**India**、**Indian**、**Brazil**、**Brazilian**、**Mexico**
扩展必背词 10 个：
- 国籍对应 1（锚词：Japan）：Korean、Italian、Spanish、French、German
- 国家名 1（锚词：China）：Korea、Italy、Spain、France、Germany

### Day 77｜第 8 幕｜国家与国籍 2
句中新词 13 个：**Britain**、**British**、**America**、**American**、**Canada**、**Canadian**、**Russia**、**Ireland**、**national**、**nationality**、**international**、**popular**、**Mexican**
扩展必背词 2 个：
- 国籍对应 2（锚词：Britain）：Irish、Russian

### Day 78｜第 8 幕｜电子设备
句中新词 11 个：**email**、**message**、**text**、**text message**、**phone**、**telephone**、**screen**、**click**、**download**、**website**、**laptop**
扩展必背词 4 个：
- 设备（锚词：laptop）：mobile phone、printer、digital、hairdryer

### Day 79｜第 8 幕｜媒体与资讯
句中新词 12 个：**television**、**TV**、**radio**、**video**、**DVD**、**channel**、**programme**、**film**、**newsagent**、**advertisement**、**magazine**、**news**
扩展必背词 6 个：
- 播放设备（锚词：DVD）：DVD player、CD player、MP3 player、video recorder
- 纸媒与招贴（锚词：programme）：newspaper、poster

### Day 80｜第 8 幕｜澳洲美食
句中新词 13 个：**burger**、**cream**、**lemonade**、**mineral water**、**slice**、**snack**、**delicious**、**piece**、**piece of cake**、**tomato**、**picnic**、**kind**、**fresh**
扩展必背词 4 个：
- 户内户外（锚词：picnic）：outdoor、outdoors、indoor、indoors


## 第 9 幕词分配（Day 81-90）

### Day 81｜第 9 幕｜考试周
句中新词 15 个：**exam**、**test**、**quiz**、**practice**、**practise**、**study**、**improve**、**mistake**、**fail**、**pass**、**homework**、**ready**、**useful**、**reading**、**pencil case**
扩展必背词 2 个：
- 教与学（锚词：study）：teach、student

### Day 82｜第 9 幕｜because 从句
句中新词 13 个：**agree**、**against**、**among**、**ask**、**describe**、**explain**、**difference**、**different**、**example**、**activity**、**else**、**anyway**、**excuse**
扩展必背词 2 个：
- 说明与信息（锚词：explain）：instructions、information

### Day 83｜第 9 幕｜when/while/until 从句
句中新词 14 个：**while**、**until**、**till**、**afternoon**、**evening**、**night**、**day**、**afterwards**、**later**、**weekly**、**monthly**、**moon**、**well**、**suddenly**
扩展必背词 3 个：
- 时间反义复习（锚词：later）：early（复习·D24）、late（复习·D24）、soon（复习·D16）

### Day 84｜第 9 幕｜if 条件句
句中新词 13 个：**if**、**or**、**any**、**some**、**other**、**another**、**such**、**all right**、**at all**、**without**、**except**、**yes**、**next**

### Day 85｜第 9 幕｜转述与通信
句中新词 14 个：**sound**、**hear**、**matter**、**mind**、**true**、**story**、**note**、**chat**、**chatroom**、**pen-friend**、**heart**、**her**、**his**、**its**
扩展必背词 4 个：
- 通信与记录（锚词：chat）：email（复习·D78）、letter（复习·D57）、postcard（复习·D57）、write down

### Day 86｜第 9 幕｜学校演出
句中新词 15 个：**stage**、**show**、**act**、**actor**、**clown**、**circus**、**dancing**、**picture**、**drawing**、**paint**、**king**、**queen**、**dragon**、**Miss**、**Ms**
扩展必背词 3 个：
- 影像（锚词：paint）：camera、photography、photo

### Day 87｜第 9 幕｜汽车与道路
句中新词 12 个：**brake**、**tyre**、**wheel**、**engine**、**driving licence**、**parking**、**garage**、**petrol**、**petrol station**、**motorway**、**licence**、**cycle**
扩展必背词 6 个：
- 形状与线（锚词：wheel）：round、circle、triangle、dot、line
- 道路设施（锚词：motorway）：traffic lights

### Day 88｜第 9 幕｜开关与上下
句中新词 12 个：**get on**、**get off**、**take off**、**turn on**、**turn off**、**shut**、**exit**、**enter**、**entrance**、**sit down**、**wake up**、**go out**
扩展必背词 2 个：
- 开关反义复习（锚词：shut）：close（复习·D5）、put on（复习·D34）

### Day 89｜第 9 幕｜材质与时尚
句中新词 15 个：**fashion**、**leather**、**wool**、**silver**、**gold**、**blonde**、**plastic**、**metal**、**paper**、**type**、**soft**、**hard**、**brown**、**boot**、**shoe**
扩展必背词 3 个：
- 衣物补充（锚词：fashion）：uniform、pyjamas、trainers

### Day 90｜第 9 幕｜梦想未来
句中新词 12 个：**dream**、**become**、**grow up**、**teenager**、**college**、**university**、**diploma**、**advanced**、**level**、**company**、**would**、**include**
扩展必背词 2 个：
- 成功之路（锚词：dream）：success、prize


## 第 10 幕词分配（Day 91-100）

### Day 91｜第 10 幕｜度量衡
句中新词 13 个：**metre**、**centimetre**、**kilometre**、**kilogram**、**gram**、**litre**、**mile**、**foot**、**add**、**half**、**full of**、**bit**、**extra**

### Day 92｜第 10 幕｜副词与功能词收尾
句中新词 14 个：**actually**、**also**、**as well**、**away**、**these**、**those**、**instead**、**itself**、**ourselves**、**themselves**、**herself**、**himself**、**yourself**、**myself**
扩展必背词 3 个：
- 也的家族（锚词：also）：as well as、at the same time
- 替代（锚词：instead）：instead of

### Day 93｜第 10 幕｜动作动词收尾
句中新词 13 个：**off**、**keep**、**let**、**try**、**start**、**finish**、**join**、**follow**、**rest**、**move**、**hit**、**lie down**、**catch**
扩展必背词 1 个：
- 休息与停止（锚词：rest）：stop（复习·D24）

### Day 94｜第 10 幕｜居家收尾
句中新词 12 个：**carpet**、**sheet**、**board**、**roof**、**light**、**living room**、**sitting room**、**dining room**、**comfortable**、**make up**、**part**、**pair**

### Day 95｜第 10 幕｜自然与能源
句中新词 15 个：**island**、**lake**、**mountain**、**space**、**air**、**alive**、**season**、**spring**、**burn**、**gas**、**electric**、**electricity**、**nature**、**east**、**west**
扩展必背词 1 个：
- 燃烧（锚词：burn）：smoke

### Day 96｜第 10 幕｜健康生活
句中新词 13 个：**exercise**、**fit**、**health**、**sleep**、**sleepy**、**shoulder**、**stomach**、**laugh**、**smile**、**fishing**、**riding**、**skateboard**、**sports centre**
扩展必背词 1 个：
- 健身（锚词：exercise）：get fit

### Day 97｜第 10 幕｜出行与邮政收尾
句中新词 13 个：**scooter**、**passenger**、**path**、**way**、**seat**、**holidays**、**rich**、**poor**、**same**、**luck**、**lucky**、**run**、**send**
扩展必背词 4 个：
- 邮政（锚词：way）：by post、postcard（复习·D57）、stamp（复习·D57）
- 住宿（锚词：holidays）：guest-house

### Day 98｜第 10 幕｜工作与商店收尾
句中新词 14 个：**earn**、**rent**、**working hours**、**shopper**、**department store**、**department**、**store**、**closed**、**build**、**building**、**business**、**machine**、**factory**、**form**
扩展必背词 7 个：
- 商店复习（锚词：store）：shop（复习·D6）、supermarket（复习·D6）、market（复习·D6）
- 金钱复习（锚词：earn）：money（复习·D35）、cash（复习·D36）、cheque（复习·D36）、credit card（复习·D36）

### Day 99｜第 10 幕｜综合复习 1：方位与杂项
句中新词 13 个：**front**、**side**、**end**、**top**、**bottom**、**middle**、**as**、**steal**、**busy**、**pocket**、**century**、**north**、**south**
扩展必背词 5 个：
- 方位复习（锚词：front）：behind（复习·D40）、above（复习·D40）、below（复习·D40）、left（复习·D40）、right（复习·D40）

### Day 100｜第 10 幕｜综合复习 2：百天收官
句中新词 13 个：**OK**、**able**、**prefer**、**exciting**、**loud**、**noisy**、**slowly**、**beginner**、**variety**、**canal**、**left hand**、**friend**、**friendly**

---

## 5. 白名单（专有名词，显式清单）

**人物**：Lucy, Tom, Carter（姓）, Mr Carter, Mrs Carter, Bingo（狗）, Miss Green（Green 为姓）, Lily, Sam, Aunt Kate, Ella
**地点**：Seaview（小镇）, Seaview School, Sydney, Opera House（悉尼歌剧院）, Harbour Bridge, Bondi Beach, the Great Barrier Reef
**其他专名**：Father Christmas

规则：
- 白名单仅含**专有名词**；普通名词（kangaroo、koala 等）一律禁止——澳洲动物戏份只用词表内动物（dolphin, whale, snake, bird…）。
- 词表自带大写词条（Christmas, Easter, Halloween, New Year, Monday-Sunday, January-December, Mr, Mrs, Miss, Ms, OK 等）按普通词处理，占用各自分配位，不重复入白名单。
- 人名与 the 连用、's 所有格（Lucy's diary）视为专名形态的合规变化。
- 新增白名单词必须先在 plan 中显式补充并记录理由（worklog）。

---

## 6. CSV 格式与已知陷阱（需求 §5）

- 编码 UTF-8 **带 BOM**、LF；python csv 模块读写；含逗号/引号/换行的字段必须正确加引号。
- 表头 + 100 行 × 10 列：`id, sentence_en, sentence_zh, grammar, new_words, extend_words, extend_note, phrases, review_note, covered_ids`。
- `new_words` 条目格式 `词|音标|词性|中文`，多词 `; ` 分隔；音标/词性/中文**逐字照抄原词表**（按 covered_ids 对照原词表取词条，禁止手抄）。
- `extend_words`：组内 `; ` 分隔，组间 ` || `；整句 ≤10 条；非空时 `extend_note` 必填，组数与组一一对应、每组说明 ≤20 字。
- `covered_ids`：本句新词（句中+扩展新词）id，逗号分隔；扩展组内复习旧词**不计入**。
- **已知陷阱（v2 词表实测）**：
  1. 音标含逗号 5 例（centimetre, grandpa, holidays, reggae, T-shirt）——CSV 字段必须加引号；
  2. 词性列含逗号/连接符（如 `back` 的 `n, adv & adj`；`many` 为 `det, adj & pron`）——绝不能按 `,` 切分词性；
  3. v2 音标当前**无** `; `，但任何下游解析**禁止按 `; ` 或 ` || ` 盲切** `new_words`/`extend_words`：必须以 `covered_ids` 为权威 id 列表，回查原词表取词条（需求硬要求，防未来词表变更引入分号）；
  4. 变形标注视为合规（boot/boots、shoe/shoes、classmate/class member 官方重复词条均各占一个分配位）。

---

## 7. 复习设计（需求 §4，硬约束）

1. **滚动回读**：间隔 {1,2,4,7,15,30}。第 d 天回读集合 = {d-1, d-2, d-4, d-7, d-15, d-30} 中 ≥1 的天，文案固定为"今日回读：请重新朗读背诵第 X、Y、Z 天的句子。"（按天序排列）——**由脚本统一生成，禁止手写**，合并 CSV 时由 `scripts/merge_batches.py` 填入 review_note 开头并逐行校验与滚动规则完全一致。
2. **回读要求：朗读 → 背诵 → 背写**：写进 PDF Howto 与新学句的每日流程，标注"背诵+背写"为最重要一步。
3. **扩展必背词随卡片一起回读**：PDF 卡片上扩展块与生词表同版式待遇。
4. **自然复现**：review_note 回读句之后记录本句实际复现的旧词及出处天（含扩展组内的复习旧词来源）；生成时每句自查"旧词复现 ≥3 个"作为软目标（不牺牲句子自然度）。
5. 每个句子恰好被后续 6 天回读（d+1, d+2, d+4, d+7, d+15, d+30 ≤100 的部分）；禁止把回读钉在固定"复习日"。

---

## 8. 生成流程（分批落盘 → 校验 → 合并 → 排版）

```
1500-KET/sentences/
  batches/batch01-days001-010.json ... batch10-days091-100.json
  (每批结构：[{id, sentence_en, sentence_zh, grammar,
               new_words: [词名...按句中出现顺序],
               ext_groups: [{note, anchor, members: [词名 | {rev: 词名, from: 天}]}],
               phrases, covered_ids}, ...])
```

**批次文件只存词名与组结构**：`new_words`/`extend_words`/`extend_note` 单元格、`review_note` 一律由 `merge_batches.py` 按 covered_ids 查原词表拼写生成（强制执行"逐字照抄"，杜绝手抄音标/词性/中文）。

1. **每批 10 句，写完立即落盘 + commit**（防中断丢失；每批是独立 JSON，可单独重跑）。
2. 每批自查：§2 内容清单 5 条 + §6 陷阱 + 句中新词真实出现 + 旧词均更早 + 短语（1-3 个，`短语|中文`，仅由已学词+本句新词构成）。句子形态：15-30 词、鼓励复合句；**允许"一句 = 两个关联短句"**（需求 §1.7，仍按 1 个 id 计数）。
3. **机器校验 `scripts/validate_sentences.py`**（合并后、排版前必须全绿；脚本须内置两张执行表）：
   - **变形表**：复数、三单、-ing、过去式、过去分词、比较级/最高级、缩写 `n't`、`'s`；多词词条整体匹配（如 `have got`、`ice cream`）。
   - **闭类功能词放行清单**：词表外的功能词（that、may、might、whom 等）与词表情态/助动词（be、have、do、will、would、can、could、shall、should、must、have to）的一切变形一律放行，不作为"表外词"报错。
   - 结构：100 行 × 10 列、id 连续、UTF-8 BOM；
   - 覆盖：1500 词各恰好一次（new_words + 扩展新词对照 covered_ids），无遗漏/重复/表外词；每天 12-18；
   - 出现性：每个 new_words 词（含常见变形表：复数/三单/-ing/过去式/过去分词/比较级/缩写 n't）在对应英文句中真实出现；
   - 一致性：new_words/extend_words 的音标/词性/中文与原词表逐字一致（按 covered_ids 对照）；
   - 扩展块：≤10 条、组数=extend_note 条数、锚词 id ∈ 本句 new_words、复习旧词 id 属更早天且不在 covered_ids；
   - 用词顺序：句中内容词 ∈ {本句新词}∪{更早天}∪{闭类功能词}∪{白名单}；
   - 回读：review_note 开头与滚动规则逐字一致（脚本重算比对）；
   - extend_note 每组 ≤20 字。
4. 内容校验（§2 清单）通过后渲染 PDF，转图目检（§9）。
5. worklog.md 记录：分配逻辑（本 plan §4 要点）、每批句子/短语/语法选择、修订历史、±1 微调（若有）。
6. 每个文件生成/重大修改单独 commit + push。

## 9. PDF 排版规范（需求 §6）

- 第 1 页 ≈35% 标题区（书名+副标题+"1500 词 / 100 句 / 10 幕 / 100 天"）；其余 + 第 2 页为 Howto：每日步骤（**背诵+背写收尾，标最重要**）、扩展必背词用法（成组背、与生词同等重要、随卡片回读）、滚动回读原理+举例、单词安排（先分组、与词表顺序无关）、故事线、语法进阶、卡片结构、给家长的建议。
- Day 1 卡片从第 3 页起；卡片流式翻页 `break-inside: avoid`、每页约两张、页底留白 ≤20%。
- 卡片结构：Day 标题 → 英文句（≥16pt 主题色）→ 中文 → 语法讲解（淡色背景）→ 生词表（每行恰好两个）→ 扩展必背词（另一淡色底、组说明小标题、每行两个、复习旧词标来源天）→ 短语表（每行两个）→ 蓝色回读条 → 复现旧词小字。extend_words 为空则整块省略。
- 正文字号 ≥11.5pt、语法/生词 ≥10.5pt；中文字体回退链含 IPA 支持（如 `"Noto Sans CJK SC", "DejaVu Sans", sans-serif`）。
- 页眉书名 + 页码；渲染后逐页转图抽查首页/Howto/中间/末页：无乱码、无方框、无大面积空白、每行两个、扩展块可区分。
- 工具链实施时选定（HTML+CSS → PDF），中文字体缺失为首要环境风险，先验证再批量渲染。

## 10. 验收清单映射（需求 §8）

| 验收项 | 落实位置 |
|---|---|
| CSV 100×10、1500 全覆盖、校验全绿 | §8 第 3 步 validate_sentences.py |
| 每天 12-18、扩展组成立、≤10 条、锚词在句中 | allocate_words.py（本 plan 已 PASS）+ 句子级校验 |
| 滚动回读 + 朗读/背诵/背写落到 CSV 与 PDF | §7 + §9 Howto |
| 故事连贯、设定一致、无逻辑硬伤 | §2 角色圣经 + 每批内容清单 |
| PDF 两页 Howto + 卡片三块 + 字号 + 无乱码 | §9 |
| plan/worklog 齐全、逐步提交 | 本文件 + §8 第 5-6 步 |

## 11. 风险与取舍记录

1. **澳洲之旅是为了化解时令冲突**：summer/beach/swimming 等 40+ 词若排在九月-二月的北半球剧情里会季节违和；寒假赴澳（南半球夏季）让海滩/冲浪/露营自然落地，同时承载国家地理词族（D75-77）。
2. **boot/boots、shoe/shoes、classmate/class member** 等官方重复词条按词表原样各占一个分配位（D34/D89、D11），生词表同卡出现近重复时，讲解中点明"单数/复数两条都是官方词条"。
3. **that/may/london 等高频词不在 KET 词表**：宾语从句用零 that（"I think he is right"），将来用 will/shall/be going to 的 going to 由 go+to 构成；地名只用白名单内专名。
4. **十一月冰雪词**（D51）通过室内冰场/高山滑雪场场景化解季节违和。
5. **D99/D100 为综合复习日**：收纳方位/杂项词，用"露西整理百天日记"的剧情串成复盘句，兼顾收官仪式感。
