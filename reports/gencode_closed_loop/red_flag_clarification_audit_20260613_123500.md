# Red Flag Clarification Audit

## 1. Scope

| 項目 | 值 |
|------|-----|
| 模式 | **只讀檢查**（未修改 production code / 測試 / DB / skill 檔） |
| 執行時間 | 2026-06-13 12:35:00 (UTC+8) |
| git branch | `main` |
| git commit | `1c6bd42` (*gencode程式修改中...) |
| 專案根目錄 | `e:\Python\Mathproject_tvet_mathB` |
| files_modified_count | **1**（本 audit report 僅） |

---

## 2. Red Flag 1 Summary

執行指令：

```bash
python -m pytest tests/gencode/test_slot_generators_question_output_contract.py -q
```

| 項目 | 值 |
|------|-----|
| pytest 總結果 | **56 failed, 0 passed** |
| failed count | 56 |
| passed count | 0 |
| 第一個 failed test | `test_slot_output_contract[quadratic_graph_vertex_axis_choice_seed0]` |
| 失敗類型 | **Collection-time / first-line KeyError**（非 slot generator runtime 失敗） |
| 是否與 Source Skill Binding Supremacy 修改有關 | **否**（見 §4 證據） |
| 是否與 induced spec 污染有關 | **是**（見 §4） |

**結論摘要：** 56 個失敗全部在測試第 102 行 `_SPEC_BY_PT[pt]` 即 KeyError，slot function 從未被呼叫。根因是 `reports/gencode_closed_loop/induced_specs/vh_數學B1_QuadraticFunctionGraph.json` 已被錯誤 Phase 1 重跑污染，不再含測試所需的 5 個 quadratic problem_type_id。

---

## 3. First Failure Detail

### test name

`test_slot_output_contract[quadratic_graph_vertex_axis_choice_seed0]`

### assertion / error

```
KeyError: 'quadratic_graph_vertex_axis_choice'
```

發生位置：`tests/gencode/test_slot_generators_question_output_contract.py:102`

```python
spec = _SPEC_BY_PT[pt]   # pt = 'quadratic_graph_vertex_axis_choice'
```

### blockers

**無。** 測試在取得 spec fixture 前即失敗，未執行 `validate_generated_question_format` 或 `validate_generator_payload`，故無 format/semantic blockers。

### payload preview

**無。** slot function `_slot_quadratic_graph_vertex_axis_choice` 未被呼叫。

### spec fixture

測試在 **module import 時** 從以下路徑載入 induced spec：

```
reports/gencode_closed_loop/induced_specs/vh_數學B1_QuadraticFunctionGraph.json
```

當前 `_SPEC_BY_PT` 僅含：

| problem_type_id | 數量 |
|-----------------|------|
| `text_short_contextual_application` | 2 items（duplicate key，後者覆蓋前者） |

測試期望的 5 個 key **全部缺失**：

- `quadratic_graph_vertex_axis_choice`
- `quadratic_graph_translation_fill_blank`
- `quadratic_graph_translation_short_answer`
- `quadratic_vertex_form_properties`
- `quadratic_standard_to_vertex_properties`

### resolved template_slot

**未執行。** 本測試直接 import slot function 並呼叫，不經 `resolve_template_slot()`。

### called slot function

**未呼叫。** 失敗發生在 `fn(SKILL_ID, pt, spec, seed)` 之前。

### answer_type / checker / equivalence

induced spec 中現有 item（污染後）：

| 欄位 | 值 |
|------|-----|
| problem_type_id | `text_short_contextual_application` |
| target_task | `contextual_application` |
| task_family | `generic_numeric_family` |
| answer_type | `text_short` |
| checker | `text_short_checker` |
| equivalence | `exact_string` |
| template_slots.stem | `linear_function_contextual_word_problem` |

### traceback 摘要

```
tests/gencode/test_slot_generators_question_output_contract.py:102: KeyError
> spec = _SPEC_BY_PT[pt]
E  KeyError: 'quadratic_graph_vertex_axis_choice'
```

所有 56 個失敗均為同一 KeyError 模式（5 slots × 10 seeds + 6 額外測試類別）。

---

## 4. 56 FAIL Root Cause

### 分類（可多選）

| 根因類型 | 判定 | 證據 |
|----------|------|------|
| `pre_existing_test_failure` | **是（相對於 HEAD 1c6bd42）** | 在 `git stash` 還原 Source Skill Binding 修改後，56 FAIL 仍完全相同 |
| `previous_report_inconsistent` | **是** | 前一輪回報 56/56 PASS 與本輪 56 FAIL 矛盾；git 歷史顯示 induced_specs 在 commit 間發生變化 |
| `test_environment_mismatch` | **否** | 同一 Python 3.14 / pytest 9.0.2 環境；失敗為 deterministic KeyError |
| `induced_spec_pollution` | **是（主因）** | commit `7bc33b6` 的 induced_specs 含 5 個 quadratic pt；commit `1c6bd42` 改為 `text_short_contextual_application` |
| `taxonomy_regression` | **否** | `git diff` 顯示 `slot_generators.py`、`template_slot_resolver.py`、測試檔 **無變更** |
| `resolver_mapping_regression` | **否** | resolver 靜態檢查仍正常映射 5 個 quadratic pt（見 §6） |
| `slot_generator_regression` | **否** | 5 個 slot 均在 SLOT_REGISTRY 且 callable |
| `test_fixture_outdated` | **是（機制性）** | 測試硬依賴 reports artifact，artifact 被污染後測試必 fail |

### 逐項回答

**1. 56 FAIL 是否真的是 pre-existing？**

**是（相對於目前 HEAD `1c6bd42` 與 working tree）。**  
`git diff` 對 `test_slot_generators_question_output_contract.py`、`slot_generators.py`、`template_slot_resolver.py` 均為空。Source Skill Binding Supremacy 的 stash 驗證亦仍 56 FAIL。

**2. 為什麼前一輪曾回報 56/56 PASS？**

git 歷史提供直接證據：

| commit | induced_specs items |
|--------|---------------------|
| `7bc33b6` (*1-3) | 5 個 quadratic problem_type_id ✅ |
| `1c6bd42` (*gencode程式修改中...) | `text_short_contextual_application` only ❌ |

前一輪 slot localization 修正後的 56/56 PASS，極可能是在 **`7bc33b6` 時期**（induced_specs 仍含正確 5 個 quadratic pt）執行。其後錯誤 Phase 1 重跑（coordinate_system → contextual_application）更新了 induced_specs（`1c6bd42`），測試未改但 fixture 已失效，故變成 56 FAIL。

本輪 Source Skill Binding 完成回報將其標為「pre-existing」在 **HEAD 時間點** 正確，但未追溯 induced_specs 的 commit 變化，造成與前一輪 PASS 報告的表面矛盾。

**3. 是否因 git stash / pytest 環境不同？**

否。stash 後仍 56 FAIL；環境一致。

**4. 是否因 test 依賴 reports / induced_specs 污染？**

**是，這是主因。** 測試第 43–56 行在 import 時讀取 induced_specs JSON；當前 JSON 僅含 `text_short_contextual_application`。

**5. 是否因 Source Skill Binding Supremacy 修改造成 regression？**

**否。** 相關 diff 僅涉及 `task_families.py`、`main_skill_anchor.py`、`problem_type_induction.py`、`semantic_alignment.py`、`phase1_report_contract.py`；未觸及 slot_generators、resolver、測試檔。

**6. 是否因 template_slot_resolver 映射問題？**

否（就本測試而言）。本測試不經 resolver，直接呼叫 slot function；失敗在 fixture lookup。

**7. 是否因 test fixture 與新 taxonomy 不一致？**

**是（間接）。** 新 taxonomy 在 `task_families.py` 新增了 `quadratic_graph_translation` 等 target_task，但測試 fixture 期望的是 **induced_specs 中的 5 個 presentation-level problem_type_id**，與 taxonomy target_task 名稱不同。當前失效主因仍是 induced_specs 被替換為 contextual_application，而非 taxonomy 命名本身。

---

## 5. Quadratic SLOT_REGISTRY Status

靜態檢查 `core/gencode/slot_generators.py` → `SLOT_REGISTRY`：

| slot_key | function_name | callable | 函式存在 | 中文化 | display/raw formula helper |
|----------|---------------|----------|----------|--------|---------------------------|
| `quadratic_graph_vertex_axis_choice` | `_slot_quadratic_graph_vertex_axis_choice` | ✅ True | ✅ | ✅ 中文 stem/選項 | ✅ `_quadratic_vertex_form_display`, `_make_quadratic_choice_options_zh` |
| `quadratic_graph_translation_fill_blank` | `_slot_quadratic_graph_translation_fill_blank` | ✅ True | ✅ | ✅ `_shift_phrase_zh` | ✅ `_quadratic_vertex_form_display` |
| `quadratic_graph_translation_short_answer` | `_slot_quadratic_graph_translation_short_answer` | ✅ True | ✅ | ✅ `_vertical_shift_phrase_zh` | ✅ display formula |
| `quadratic_vertex_form_properties` | `_slot_quadratic_vertex_form_properties` | ✅ True | ✅ | ✅ 中文選項 | ✅ `_quadratic_vertex_form_display` |
| `quadratic_standard_to_vertex_properties` | `_slot_quadratic_standard_to_vertex_properties` | ✅ True | ✅ | ✅ 中文選項 | ✅ `_quadratic_vertex_form_display` |

**`quadratic_slots_registered=true`**

5 個 key 全部存在於 `SLOT_REGISTRY`，函式 callable，且已中文化並使用 display formula helper。

---

## 6. Template Slot Resolver Mapping

靜態 + runtime 呼叫 `resolve_template_slot()`（skill_id=`vh_數學B1_QuadraticFunctionGraph`, seed=0）：

| input_type | input_value | resolved_slot | slot_exists_in_SLOT_REGISTRY | status |
|------------|-------------|---------------|------------------------------|--------|
| problem_type_id | `quadratic_graph_vertex_axis_choice` | `quadratic_graph_vertex_axis_choice` | ✅ | ok |
| problem_type_id | `quadratic_graph_translation_fill_blank` | `quadratic_graph_translation_fill_blank` | ✅ | ok |
| problem_type_id | `quadratic_graph_translation_short_answer` | `quadratic_graph_translation_short_answer` | ✅ | ok |
| problem_type_id | `quadratic_vertex_form_properties` | `quadratic_vertex_form_properties` | ✅ | ok |
| problem_type_id | `quadratic_standard_to_vertex_properties` | `quadratic_standard_to_vertex_properties` | ✅ | ok |
| problem_type_id | `text_short_compute_vertex_and_axis` | `quadratic_graph_vertex_axis_choice` | ✅ | **coarse default**（見 §7） |
| problem_type_id | `choice_compute_vertex_and_axis` | `quadratic_graph_vertex_axis_choice` | ✅ | coarse default |
| target_task | `quadratic_graph_translation` | `quadratic_graph_vertex_axis_choice` | ✅ | **NOT in TASK_FAMILY_TO_SLOT**；fallback via `_is_quadratic_graph_spec` |
| target_task | `quadratic_vertex_axis_identification` | `quadratic_graph_vertex_axis_choice` | ✅ | same coarse fallback |
| target_task | `quadratic_graph_properties_choice` | `quadratic_graph_vertex_axis_choice` | ✅ | same coarse fallback |
| target_task | `quadratic_standard_to_vertex_properties` | `quadratic_standard_to_vertex_properties` | ✅ | ok（在 `_QUADRATIC_GRAPH_TARGET_TASKS`） |

**TASK_FAMILY_TO_SLOT 直接查詢（未走 resolver guard）：**

| target_task | TASK_FAMILY_TO_SLOT |
|-------------|---------------------|
| `quadratic_graph_translation` | NOT_MAPPED |
| `quadratic_vertex_axis_identification` | NOT_MAPPED |
| `quadratic_graph_properties_choice` | NOT_MAPPED |
| `text_short_compute_vertex_and_axis` | NOT_MAPPED |

taxonomy 新增的 target_task 名稱尚未加入 `TASK_FAMILY_TO_SLOT`；resolver 靠 `_is_quadratic_graph_spec()` + default fallback 勉強落到 `quadratic_graph_vertex_axis_choice`。

---

## 7. Rule Pack ProblemType Mapping

來源：`configs/gencode/classifiers/phase1_rule_packs.yaml` → `vh_數學B1_QuadraticFunctionGraph`

| 欄位 | 值 |
|------|-----|
| classifier_source | `human_confirmed` |
| problem_type_id | `text_short_compute_vertex_and_axis` |
| display_name | 二次函數圖形平移與頂點特徵 |
| checker | `coordinate_pair_checker` |
| equivalence | `ordered_tuple_exact` |
| target_task | （未明示；由 classification_rules 推 `prefer_problem_type_id`） |
| task_family | （未明示） |
| template_family | （未明示） |
| single_primary_problem_type | `true`（在 `source_policy` 下） |
| matched example ids | 4450, 4460, 4466, 4503 |
| merge_policy | `single_primary_problem_type` |
| runtime_candidate | `true` |

### Q1: `text_short_compute_vertex_and_axis` 是否已有 Layer 6 slot 對應？

**部分有，但 presentation 不匹配。**

- resolver 可 resolve 到 `quadratic_graph_vertex_axis_choice`（single_choice slot）
- rule pack 宣告 `answer_type` 語意為 text_short + `coordinate_pair_checker` + `ordered_tuple_exact`
- 實際落點 slot 產出 **single_choice**（A/B/C/D），非 text_short 平移/頂點簡答
- 較合理的 slot 應為 `quadratic_graph_translation_fill_blank` 或 `quadratic_graph_translation_short_answer`

### Q2: 若沒有，應屬於哪類？

| 類型 | 判定 |
|------|------|
| `rulepack_problem_type_unmapped_to_slot` | **否**（有映射，但是 coarse default） |
| `template_slot_resolver_missing_mapping` | **是**（rule pack pt → 正確 presentation slot 的精確映射缺失） |
| `slot_registry_missing` | **否** |
| `test_fixture_mismatch` | **是**（測試期望 5 formal pt，rule pack 用不同 pt id） |

### Q3: 是否解釋「slot_generators 未登錄 5 個 quadratic slots」？

**是。** 上一輪完成回報的「slot_generators 未登錄 5 個 quadratic slots」表述 **不準確**。  
實際狀況：

- SLOT_REGISTRY：**已登錄 5 個** ✅
- induced_specs / Phase 1 輸出：**未產生 5 個 formal pt** ❌
- rule pack `text_short_compute_vertex_and_axis`：**未精確 bridge 到對應 presentation slot** ❌
- 測試 fixture：**依賴已污染的 induced_specs** ❌

---

## 8. Formal Skill vs Rule Pack Drift

### Formal skill `GENERATOR_SPECS`（`skills/vh_數學B1_QuadraticFunctionGraph.py`）

| problem_type_id | checker_key | equivalence_type | generator_readiness |
|-----------------|-------------|------------------|---------------------|
| `quadratic_graph_vertex_axis_choice` | `choice_label_checker` | `choice_label` | `runtime_ready` |
| `quadratic_graph_translation_fill_blank` | `text_short_checker` | `exact_string` | `runtime_ready` |
| `quadratic_graph_translation_short_answer` | `text_short_checker` | `exact_string` | `runtime_ready` |
| `quadratic_vertex_form_properties` | `choice_label_checker` | `choice_label` | `runtime_ready` |
| `quadratic_standard_to_vertex_properties` | `choice_label_checker` | `choice_label` | `runtime_ready` |

### Rule pack primary problem type

| problem_type_id | checker | equivalence |
|-----------------|---------|-------------|
| `text_short_compute_vertex_and_axis` | `coordinate_pair_checker` | `ordered_tuple_exact` |

### 差異分析

1. **Formal skill 用 5 個 presentation-variant problem types**（3 choice + 2 text_short）。
2. **Rule pack 用 1 個 primary problem type**（`text_short_compute_vertex_and_axis`），強制收斂所有 source examples。
3. **兩者缺少 normalization / bridge：**
   - rule pack pt id 不在 formal `GENERATOR_SPECS` 中
   - checker/equivalence 不一致（coordinate_pair vs choice_label/text_short）
   - resolver 對 rule pack pt 的 default 落到 choice slot，與 rule pack 的 text_short 語意衝突
4. **若 single_primary_problem_type 要對應多 presentation variants：**
   - 應在 **Phase 2 展開**（依 answer_contract / has_choices 拆成 5 個 pt），或
   - 在 **resolver 增加精確映射**（依 pt 名稱 / target_task / answer_type 選 slot）
   - 目前兩者皆未完整實作
5. **目前失敗最像：**
   - ✅ `problem_type bridge 缺失`（formal 5 pt ↔ rule pack 1 pt ↔ induced spec contextual_application 三者脫節）
   - ✅ `resolver mapping 缺失`（taxonomy target_task 與 rule pack pt 的精確 slot 選擇）
   - ❌ `slot registry 缺失`
   - ✅ `test_fixture_outdated`（induced_specs 污染）

---

## 9. Root Cause Summary

| # | 問題 | 答案 |
|---|------|------|
| 1 | 56 FAIL 是否真的是 pre-existing？ | **是（相對 HEAD 1c6bd42）**；非 Source Skill Binding 造成 |
| 2 | 上一輪 56/56 PASS 與本輪 56 FAIL 為何矛盾？ | induced_specs 在 `7bc33b6→1c6bd42` 被錯誤 Phase 1 重跑污染；前一輪 PASS 時 artifact 仍正確 |
| 3 | 5 個 quadratic slots 是否真的未登錄？ | **否**；`quadratic_slots_registered=true`，5 個全在 SLOT_REGISTRY 且 callable |
| 4 | `text_short_compute_vertex_and_axis` 是否未接 Layer 6？ | **部分接入**：resolver 落到 `quadratic_graph_vertex_axis_choice`，但 presentation/contract 不匹配；精確 bridge 缺失 |
| 5 | 下一步應修什麼？ | 見 §10 |

---

## 10. Recommended Next Action

### must_fix_before_rerun_phase_1_3

1. **清理 / 還原 `induced_specs/vh_數學B1_QuadraticFunctionGraph.json`**  
   從 `7bc33b6` 還原 5 個 quadratic pt，或等 Source Skill Binding 修正後重跑 Phase 1–3 產生正確 spec。
2. **建立 rule pack pt → formal pt / slot 的 bridge**  
   `text_short_compute_vertex_and_axis` 需依 answer_contract 映射到正確 quadratic slot（非一律 default 到 choice）。
3. **在 `TASK_FAMILY_TO_SLOT` 補 taxonomy target_task 精確映射**  
   `quadratic_graph_translation`、`quadratic_vertex_axis_identification`、`quadratic_graph_properties_choice` 目前僅 coarse fallback。
4. **確認 human_confirmed rule pack 在 Phase 1 實際生效**  
   當前 induced_specs 仍為 AI/fallback 的 `text_short_contextual_application`，表示 rule pack 未阻止錯誤分類。

### can_wait

1. **測試 fixture 改為自包含 spec**（不依賴 reports artifact），避免 induced_specs 污染再次造成 56 FAIL。
2. **Phase 2 展開邏輯**：single_primary_problem_type → 多 presentation variant 的自動拆分。

### should_not_fix

1. **slot_generators.py** — 5 個 quadratic slot 已存在且中文化，無需重寫。
2. **不應以 patch `text_short_contextual_application` 通過 smoke** — 根因是 classification/spec bridge，非 slot 本身。
3. **不應針對單一 skill_id 在 resolver 寫 hardcode if/else** — 應做通用 bridge。

---

## 11. Final Status

**`AUDIT_PASS_WITH_RED_FLAG_ROOT_CAUSE`**

兩個紅旗均已釐清：

- **紅旗 1：** 56 FAIL 主因 = `induced_spec_pollution` + `test_fixture_outdated`；非 Source Skill Binding regression；前一輪 PASS 因 artifact 尚未污染。
- **紅旗 2：** 「slot 未登錄」表述錯誤；實際為 resolver/rule-pack/formal-skill bridge 缺失 + induced spec 未產出 formal 5 pt。

---

## Appendix: git diff 摘要（本輪相關檔案）

| 檔案 | diff |
|------|------|
| `tests/gencode/test_slot_generators_question_output_contract.py` | **無變更** |
| `core/gencode/slot_generators.py` | **無變更** |
| `core/gencode/template_slot_resolver.py` | **無變更** |
| `core/gencode/problem_type_induction.py` | 有變更（Source Skill Binding） |
| `core/gencode/main_skill_anchor.py` | 有變更 |
| `core/gencode/task_families.py` | 有變更 |
