# 批次文件格式与写句规范（1500-KET 句子生成）

> 上游：`prompts/2-1500-KET-001.md`（需求硬约束）、`plan/002-sentence-generation-plan.md`（故事线/角色圣经/词分配/语法表）。
> 分配数据权威：`scripts/allocation/act01-10.py` + `scripts/allocate_words.py`（当前 1500/1500 PASS）。

## 1. 交付物

`sentences/batches/batchNN-days0XX-0YY.json`，每批 10 句（batch01 = Day 1-10 … batch10 = Day 91-100）。
**只写批次 JSON，不要跑 git**（提交由主流程统一做，避免并发冲突）。

## 2. 生成骨架（不要手抄结构字段）

```bash
cd 1500-KET/scripts
python3 make_batch_stub.py --batch 3      # 写出 batch03 骨架（已填好 ext_groups / covered_ids）
```

骨架结构：

```jsonc
{
  "batch": 3, "days": [21, 30],
  "sentences": [
    {
      "id": 21,
      "sentence_en": "…",          // ← 你填：15-30 词，英文
      "sentence_zh": "…",          // ← 你填：中文句意
      "grammar": "…",              // ← 你填：中文 1-3 句，只讲本句实际出现的语法点
      "new_words": [],             // ← 你填：句中新词，**按词在句中首次出现顺序**
      "ext_groups": [ … ],         // ← 骨架已填好，照抄勿改（note/anchor/members）
      "phrases": [],               // ← 你填：1-3 个 "短语|中文"
      "repeats": "",               // ← 你填：本句自然复现的旧词及出处天
      "covered_ids": [ … ]         // ← 骨架已填好，照抄勿改
    }
  ]
}
```

`_hint_sent` 是骨架附带的提示字段（= 该天句中新词集合），**校验器会忽略，合并脚本不读**；可以留着也可以删。

## 3. 每句硬约束

1. **句中内容词** ∈ {本句新词（含扩展新词）} ∪ {更早天数已分配的词} ∪ {闭类功能词} ∪ {白名单专名}。
   更早天数指**分配表的更早天**，与词表 id 无关。扩展必背词从它被分配的那天起就可自由复用。
2. **`new_words` 集合必须等于该天分配表的 sent 集合**，且每个词（含复数/三单/-ing/过去式/过去分词/比较级/`n't`/`'s` 变形）**真实出现在英文句中**。扩展必背词**不必**出现在句中，但锚词必须在。
3. 长度 **15-30 词**，鼓励复合句；允许"一句 = 两个关联短句"（仍按 1 个 id）。**不得出现阿拉伯数字**，数词全拼写。
4. 扩展组、`covered_ids` 照抄骨架；**不得增删分配词**。
5. `phrases` 1-3 个，格式 `短语|中文`；短语的用词同样受第 1 条约束。
6. `repeats`：写在 `review_note` 里、回读文案**之后**，说明本句自然复现了哪些旧词及出处天（含扩展组内复习旧词的来源）。Day 1 写"第 1 天：新学，无回读。"之类即可。
7. 故事与角色一致（见 plan §2 角色圣经），季节/时间一致，句与句情节衔接；一批 10 句内必须自洽。
8. 短语/句子都要过内容自查：搭配自然、人物关系一致、时间季节一致、前后衔接、扩展组同类成立。

## 4. 白名单专名（唯一允许的表外词）

**人物**：Lucy, Tom, Carter, Mr Carter, Mrs Carter, Bingo, Miss Green, Lily, Sam, Aunt Kate, Ella
**地点**：Seaview, Seaview School, Sydney, Opera House, Harbour Bridge, Bondi Beach, the Great Barrier Reef
**其他**：Father Christmas

规则：白名单只含专名；普通名词（kangaroo、koala 等）一律禁止。词表自带的大写词条（Christmas、Monday、Mr、OK…）按普通词处理，占用各自分配位。

## 5. 校验与迭代

```bash
cd 1500-KET/scripts
python3 validate_sentences.py --words 21                  # 看第 21 天可用词表（新词/扩展词/可用旧词）
python3 validate_sentences.py --check "句子" --day 21      # 单句快速体检（用词范围/长度/数字）
python3 validate_sentences.py --batch 3                   # 整批校验（覆盖/出现性/扩展块/回读/一致性）
python3 validate_sentences.py --batch all                 # 全部已落盘批次
```

`--check` 只查单句文本；`--batch` 才是硬门禁。**每批必须 `--batch N` 全绿才算完成。**

## 6. 陷阱清单

1. **常见词上线很晚**（早用会被校验器拦下）：as=D99、until/while/well=D83、if/or/any/some/other/another/next/without/except/yes=D84、than/more/most/less/better/high/low=D64、also/away=D92、off/keep/let/try/start/finish/join/follow/rest/move/hit/catch=D93、back=D44、mean=D49、during=D53、ever/already/yet/since/still=D66、even/only/together=D67、about=D39、over/under/past=D40、again/once/twice/just=D38、both/each/every/all=D17、too=D17、because=D19、like=D19、after/before=D15。
2. **多词词条整体匹配**：`ice cream`(D29) 的组成词 ice(D51)/cream(D80) 更晚上线，但整条短语可用；`in front of`(D41) 里的 front 是 D99；`next to`(D41) 里的 next 是 D84；`wash up`(D53) 里的 wash 是 D56；`text book`(D11 扩展) 里的 text 是 D78；`class member`(D11 扩展) 里的 member 是 D61；`get off/take off/turn on/turn off`(D88) 里的 off 是 D93。校验器按整条短语吞掉，**照写即可**。
3. **`covered_ids` 是解析权威**：禁止按 `; ` 或 ` || ` 切分 `new_words`/`extend_words`；音标可能含逗号（centimetre、grandpa、holidays、reggae、T-shirt）与分号，一律由脚本按 covered_ids 回查原词表拼装。
4. **音标/词性/中文一律照抄原词表**，绝不手写（合并脚本自动生成单元格，你只写词名）。
5. 校验器对"表外词"零容忍；拿不准就先 `--check` 一句。
