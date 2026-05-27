# Agent Skill v2 ProblemType 閬?身閮?v0.1

## 1. ?辣?桃?
?祆?隞嗅?蝢?Agent Skill v2 銝哨?隞?**ProblemType (憿?)** ?箸?撠憿雿?閬??瑽? JSON / YAML Schema?閬蝣箔? AI ?賢?隞仿?摨衣Ⅱ摰扼??冽扯?蝚血?????皞脰?憿????霅?

## 2. ?詨???
- **YAML ?芸?嚗辣敺?DB ??*嚗 Pipeline 蝛拙???????潔誑 YAML/Markdown ?澆?摮??Git嚗噶?潛??祆?嗉?撖拚??
- **璅姪??*嚗4 Registry ?舀閬閮剛???Reference Implementation嚗??甈????B4 ?曄?靽??澆捆??
- **蝣箏??批??*嚗??拙??芸??憿? deterministic ?寞????憒??鼓????嚗??Ⅱ璅???`manual_review` ??`future_ai_judged`??

## 3. ?? Agent Skill ??v2 撌桃

| ? | ?? Agent Skill | Agent Skill v2 |
|---|---|---|
| ?撠雿?| skill | problem_type |
| 銝餉??辣 | SKILL.md (Markdown) | subskills.yaml + problem_types.yaml + examples_map.yaml + prompt_gencode.md + evals.yaml + prerequisites.yaml |
| ?Ｗ??| `skills/{skill_id}.py` | `generated_candidates/{problem_type_id}/` (憭??? |
| ??恣??| 撘梧??虜?湔銝?嚗?| ?湔??? (candidate / verified / runtime_ready) |
| runtime ?孵? | skill.py ?湔?瑁? | ??Registry 撽?????撠?(Registry-controlled generator) |
| verifier | ?箸 dynamic sampling ?蝷? | ? 12+ ?炎?亦??湔 runtime_ready gate |

---

## 4. 閬??獢??株??桅?蝯?

瘥?`skill` 閬??葉嚗?*?喳?敹??隞乩? 5 ?敹??潭?獢?*嚗?
1. `subskills.yaml`嚗?蝢拙???賢惜蝝????蝷箏?蝔梯??靘???
2. `problem_types.yaml`嚗?蝢抵府??賭????憿???IO 憟???寞撘???閮箸璅惜??
3. `examples_map.yaml`嚗??玨?砌?憿? `problem_type` ??撠?靽?? AI 隞踹神???抒?靘???
4. `prerequisites.yaml`嚗?蝢拙???賢惜蝝??耨靘陷???那?瑚耨敺抵楝敺?
5. `evals.yaml`嚗?蝢抵??撽?????潸?皜祈岫獢???

### ?桅?蝯?
```text
agent_skills_v2/
  _template/
    README.md
    subskills.yaml
    problem_types.yaml
    examples_map.yaml
    prerequisites.yaml
    evals.yaml
    domain_functions.yaml
    prompt_gencode.md
```

---

## 5. ??YAML 瑼?閰喟敦 Schema 閬

### 5.1 subskills.yaml Schema
瘥????(SubSkill) ?喳?敹??隞乩?甈?嚗?
- `subskill_id`: ?典??臭?摮???ID嚗?憒?`absolute_value_numeric_evaluation`嚗?
- `skill_id`: ??蜓???ID嚗?憒?`vh_?詨飛B1_AbsoluteValue`嚗?
- `display_name`: 摮貊???撣怎垢撅內?迂??
- `description`: 閰脣???賣?瘨菔??摮豢?敹菜?餈啜?
- `observed`: ?臬?箏鋡怎蝡?隡啗?皜祉?摮??踝?bool嚗?
- `supporting_example_ids`: ?舀?甇文???賜?隤脫靘? ID 皜嚗ist嚗?
- `prerequisite_subskills`: ???靽桀????ID 皜嚗ist嚗?
- `diagnosis_tags`: ?亥?閮箸?冽?蝐斗??殷?list嚗?
- `runtime_notes`: ???釣?????酉隤芣???

### 5.2 problem_types.yaml Schema
瘥???(ProblemType) ?喳?敹??隞乩?甈?嚗?
- `problem_type_id`: 憿??臭? ID??
- `skill_id`: ?????ID??
- `subskill_id`: ??????ID??
- `display_name`: 憿?憿舐內?迂??
- `runtime_category`: ?????乓?*??閮曹誑銝?6 蝔格???*嚗?
  - `deterministic_numeric`: 蝣箏??扳?潛?獢?靘??湔???詻??賂???
  - `deterministic_expression`: 蝣箏??找誨?詨?蝑?嚗?憒?????LaTeX 隞?銵券?撘???
  - `deterministic_choice`: 蝣箏??批?賊?蝑???
  - `manual_review`: ?閬?撣思犖撌仿?瑞?憿?嚗?銴?蝜芸??陛蝑?嚗?
  - `future_ai_judged`: 敺靘?AI 閬死璅∪??文?????憒撠郊撽?撖怠撘???
  - `visual_or_handwriting`: 閬死蝜芸???撖怨撓?仿???
- `answer_type`: ??蝑??豢?憿?嚗? `integer`, `fraction`, `choice` 蝑???
- `checker_type`: ?寞?券???憒?`integer_checker`, `choice_checker` 蝑???
- `examples_refs`: 撠???textbook examples ??ID 皜??
- `prerequisite_subskills`: 閰脤??????靽桀????ID 皜??
- `diagnosis_tags`: 閮箸?函敦蝎漲璅惜??
- `difficulty_policy`: ??漲?蔭??憿????嗚?
- `output_contract`: ??頛詨??Payload 蝯?閬???
- `status`: ?嗅?????

### 5.3 examples_map.yaml Schema
?粹??AI ?冽???嚗?銝蝑??玨?砌?憿?(textbook_example) 敹?蝎暹?撠?隞乩?甈?嚗?
- `example_id`: ?臭???憿??典?蝺渡? ID??
- `title`: 靘?璅???
- `source_type`: 靘?憿?嚗? `textbook_example` (隤脫靘?), `textbook_practice` (?典?蝺渡?), `self_assessment` (?芣?閰?) 蝑?
- `source_section`: 隤脫靘?蝡???蝣潦?
- `problem_preview`: 憿?汗??批捆嚗??LaTeX嚗?
- `skill_id`: ??蜓???ID??
- `subskill_id`: ??????ID??
- `problem_type_id`: ?????ID??
- `runtime_category`: ?????乓?
- `classification_reason`: ???箸迨憿????亦??琿???隤芣???
- `manual_review_reason` ??`future_ai_judged_reason`: ?亥府靘?鋡急飛憿????粹?嚗??底蝝啗??????脫迫蝖砍??喟Ⅱ摰找誨蝣潦?

### 5.4 prerequisites.yaml Schema
敹??舀摮??賢惜蝝?(Subskill-level) ??靽株?閮箸靘陷??嚗?
- `subskill_id`: ?嗅?摮???ID??
- `prerequisite_subskills`: ?詨惇?蜓??賭?銋?靽桀????ID 皜??
- `prerequisite_skills`: 頝冽??賭??耨憭 Skill ID 皜??
- `reason`: ?耨靘陷?飛蝘?頛航牧??
- `remediation_candidates`: 閮箸甇文???賢仃??嚗?衣?鋆?蝺渡?憿???皞??柴?

---

## 6. Verified Registry Schema (撽?閮餃?瑼?瑽?

?箇Ⅱ靽?雿??冽扯??憯批神?伐?`verified_problem_types` 敹???**dict list (摮?”)** ?澆?嚗?撠??舐蝪∪摮葡?”??

```yaml
verified_problem_types:
  - problem_type_id: absolute_value_numeric_evaluation
    skill_id: vh_?詨飛B1_AbsoluteValue
    subskill_id: absolute_value_numeric_evaluation
    status: verified
    candidate_path: generated_candidates/absolute_value_numeric_evaluation/candidate_v1.py
    function_name: generate
    answer_type: integer
    checker_type: integer_checker

failed_problem_types:
  - problem_type_id: absolute_value_expression_simplification
    skill_id: vh_?詨飛B1_AbsoluteValue
    subskill_id: absolute_value_expression_simplification
    status: failed
    latest_error_summary: "TimeoutException: Generation timed out after 5 seconds"
    preserve_previous_verified: true

manual_review_problem_types:
  - problem_type_id: absolute_value_geometric_graphing
    skill_id: vh_?詨飛B1_AbsoluteValue
    subskill_id: absolute_value_geometric_graphing
    status: manual_review
    reason: "Requires plotting number lines and coordinate system which cannot be evaluated in a deterministic numeric format."

future_ai_judged_problem_types:
  - problem_type_id: absolute_value_proof_derivation
    skill_id: vh_?詨飛B1_AbsoluteValue
    subskill_id: absolute_value_proof_derivation
    status: future_ai_judged
    reason: "Requires multi-step mathematical proof rendering and intermediate step analysis, which currently needs AI-vision based evaluation."
```

---

## 7. Candidate Payload Contract (Candidate ????澆?憟?)

Candidate ??璅∠??撠??`generate()` ?賣嚗??喟?摮 (dict) ?喳?敹??隞乩??箸甈?嚗?

- `problem_type_id`: 憿? ID??
- `skill_id`: 銝餅???ID??
- `subskill_id`: 摮???ID??
- `question_text`: 憿??批捆嚗??璅? LaTeX ?詨飛銵券?撘???
- `answer`: 甇?Ⅱ蝑?嚗??? `answer_type` 撠?嚗?
- `answer_type`: 蝑?憿?憿???
- `checker_type`: ?寞?券???
- `solution_steps`: 閰喟敦?郊閫??????
- `metadata`: 閰桅?鞈?摮嚗?*?喳?敹??隞乩?甈?**嚗?
  - `scenario_family`: ??摰嗆??迂??
  - `scenario_id`: ?? ID??
  - `parameter_signature`: 閰脤璈??桃???孵噩蝪賜?嚗隞仿?霅?璅?改???
  - `question_pattern_id`: 憿?璅?? ID??
  - `diagnosis_tags`: 閮箸璅惜皜??
  - `prerequisite_subskills`: 閰脤璈??桀擃????靽桀???賣??柴?

---

## 8. Verifier Gate 撽???

??Candidate 蝔?蝣潸◤閮餃???Verified Registry ??敹????隞乩? **12 ??Verifier Gate 敹?瑼Ｘ**嚗?

1. **syntax/import/generate exists**嚗?撘Ⅳ??Python 隤??航炊嚗鋡怠????伐?銝???`generate()` 撠?亙?賣??
2. **payload contract**嚗??桃???payload 蝯?摰嚗敹?雿? `metadata` ?蝻箏仃??
3. **dynamic sampling >= 30**嚗銵???⊥見皜祈岫?喳? 30 甈∴?銝?蝔葉?∠撣豢??箝?
4. **answer_type / checker_type**嚗?獢??寞?券??摰對?銝蝟餌絞?賢??桀??
5. **correct answer self-check**嚗??Ｙ??迤蝣箇?獢 Checker嚗?寧?????100% ????
6. **wrong answer rejection**嚗?撱箸??神?舐?蝑?? Checker嚗?寧?????100% 鋡急?蝯摰?胯?
7. **LaTeX safety**嚗??株?閫??銝?LaTeX 隤?蝯?甇?Ⅱ嚗?敺??芷?撠? `$` 蝚西???
8. **no placeholder**嚗??株?閫??銝剔?撠?敺? placeholders嚗? "TBD"??TODO"??..." 蝑?????
9. **duplicate guard**嚗璅?30 甈⊿??格??祇?銴?敹?雿銝?嚗誑?脩???蝭?敺??柴?
10. **parameter_signature diversity**嚗璅?葉 `parameter_signature` ?冽?蝯??詨????潮?潘??脫迫?璈?璅?扼?
11. **timeout**嚗甈⊿??桃????嚗?? 5s ?批?????
12. **choice validator if choice**嚗?粹??嚗??? 4 ??甇?Ⅱ蝑?敹?蝎曄Ⅱ??券?嚗??賊?銝????

---

## 9. B1 AbsoluteValue ?琿?蝭?撠?

隞乩??粹??瑟摮?B1 蝯??潭??賜?撖阡?閬撠?蝭?嚗?

- **skill_id**: `vh_?詨飛B1_AbsoluteValue`
- **subskill_id**: `absolute_value_numeric_evaluation`
- **problem_type_id**: `absolute_value_numeric_evaluation`
- **runtime_category**: `deterministic_numeric`
- **answer_type**: `integer`
- **checker_type**: `integer_checker`
- **prerequisite_subskills**: `[]`
- **example question**: `瘙?$|-5|$ ?潦

---
*?辣?交?: 2026-05-25*
*?: v0.1.1 (SOP 閬??啁?)*

---

## 10. Closure Gate：examples_map / problem_types / registry

### 10.1 examples_map 每筆 example 必要欄位

每一筆教材例題或隨堂練習都必須精準對應到 `subskill_id` 與 `problem_type_id`。

每筆 example 至少必須包含：

- `example_id`
- `title`
- `source_type`
- `source_section`
- `problem_preview`
- `skill_id`
- `subskill_id`
- `problem_type_id`
- `runtime_category`
- `classification_reason`
- `generator_status`

若該 example 被標示為 `manual_review` 或 `future_ai_judged`，必須另含：

- `manual_review_reason`
- `future_ai_judged_reason`

不得默默跳過任何 DB example。

### 10.2 problem_types.yaml 每個 problem_type 必要欄位

每個 problem_type 至少必須包含：

- `problem_type_id`
- `skill_id`
- `subskill_id`
- `runtime_category`
- `answer_type`
- `checker_type`
- `answer_contract`
- `examples_refs`
- `prerequisite_subskills`
- `diagnosis_tags`
- `status`

`answer_contract` 必須描述答案型態、等價判斷、checker key、可接受格式與 canonical answer schema。

### 10.3 registry verified_problem_types 結構要求

`verified_problem_types` 必須是 dict list，不能是簡單字串列表。

每筆 verified entry 至少包含：

- `problem_type_id`
- `skill_id`
- `subskill_id`
- `status`
- `candidate_path`
- `function_name`
- `answer_type`
- `checker_type`
- `answer_contract`

Registry merge 必須採 non-destructive merge：

- 不得刪除既有 verified entries。
- 不得覆蓋其他 skill 的 registry。
- 若同一 problem_type 已存在，只能安全更新目前 skill 的 binding。
- manual_review / future_ai_judged 題型必須保留 exclusion 資訊，不得偽裝為 verified deterministic problem_type。

### 10.4 Final Coverage Gate

Skill Closure 判定必須檢查：

- examples_map 是否涵蓋全部 observed examples。
- 每個 observed deterministic problem_type 是否 verified。
- manual_review / future_ai_judged 是否有明確 reason。
- registry 是否已 non-destructive 綁定。
- wrapper 是否可載入 verified candidates。
- runtime 是否能抽到 verified problem types。
- verify report 是否通過。

輸出至少包含：

- `coverage_status`
- `full_skill_coverage`
- `final_status`
- `blocking_reasons`
- `verified_problem_types`
- `manual_review_problem_types`
- `future_ai_judged_problem_types`

## 11. Phase 3 Publish Gate / Runtime Quality Gate

### 11.1 Phase 3 PASS 的限制

Phase 3 `PASS` 只代表技術發布門檻通過，不代表前台學生頁面一定正常，也不代表課本例題語意已完整貼合。

因此 Phase 3 之後必須再區分：

1. Technical Closed Loop PASS
2. Runtime Quality PASS
3. Web Runtime PASS
4. Source Alignment PASS / PARTIAL

### 11.2 Technical Closed Loop PASS

條件：

- Phase 1 為 `AUDIT_PASS` 或明確可接受狀態。
- Phase 2 為 `BUILD_PASS`。
- Phase 3 為 `PASS` 且 `publish_ready = true`。
- registry binding、wrapper binding、runtime binding 均已完成。
- deterministic runtime coverage 不缺 verified problem types。

### 11.3 Runtime Quality PASS

條件：

- `gencode_choice_quality_audit.py` 通過。
- `gencode_runtime_distribution_audit.py` 通過。
- manual_review 題型沒有外漏。
- choice 題正確答案 label 不固定單一選項。
- expected verified problem types 都有被 wrapper 抽到。

### 11.4 Web Runtime PASS

條件：

- `gencode_web_runtime_audit.py` 通過。
- `/get_next_question` 實際 API 取題時，`route_source = gencode_wrapper`。
- 不應走 DB fallback 或 legacy，除非 wrapper 明確失敗。
- 前台 API 實際 observed problem types 必須涵蓋所有 verified problem types。
- response payload 必須保留 `problem_type_id`、`answer_contract`、`source` 或 `route_source`。

### 11.5 Source Alignment PASS / PARTIAL

`gencode_source_alignment_audit.py` 用於檢查 DB textbook examples 的題型形式是否真的被 runtime generator 語意覆蓋。

若 Phase 3 PASS 但 source alignment 仍有：

- `missing_source_aligned_problem_types`
- `possible_classifier_misclassifications`
- `underrepresented_runtime_forms`

則狀態應記為 `Source Alignment PARTIAL`。

`Source Alignment PARTIAL` 不一定阻擋技術發布，但必須列入 enhancement backlog，不得宣稱完整貼近課本例題。

## 12. Runtime Quality Audit Gate

### 12.1 Choice Quality Gate

所有 choice 題必須符合：

1. `answer` / `correct_answer` 必須是 `A/B/C/D` label。
2. 不得把完整選項文字塞進 `answer` / `correct_answer`。
3. 若需保留正確答案文字，應放在 `correct_text`、`explanation` 或 metadata。
4. choices 不可重複。
5. correct answer 必須存在於 choices。
6. choices shuffle 後，answer label 必須重新計算。
7. `choice_question_count >= 20` 且所有正確答案都是同一 label 時，必須 FAIL。
8. choice checker 必須支援：
   - A/B/C/D
   - a/b/c/d
   - (A)/(B)
   - 1/2/3/4
   - 完整選項文字 normalize

### 12.2 Choice Quality Audit 指令

```powershell
python scripts\gencode_choice_quality_audit.py --skill-id <skill_id> --samples 100
```
