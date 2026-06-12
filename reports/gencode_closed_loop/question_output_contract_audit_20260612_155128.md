# Gencode Question Output Contract Audit

## 1. Scope

- **模式**：本輪只檢查、不修改（read-only audit）
- **檢查時間**：2026-06-12 15:51:28 (UTC+8)
- **專案根目錄**：`D:\Python\Mathproject_tvet_mathB`
- **Git branch**：`main`
- **Git commit**：`7bc33b6`
- **遵循 SOP**：
  - `docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md`
  - `docs/系統SOP/Gencode_AgentSkillV2整合/AgentSkillV2_ProblemType規格包設計_v0.3.md`
  - `docs/系統SOP/Gencode_AgentSkillV2整合/AnswerContract_EquivalenceType_Gate_v0.3.md`

---

## 2. SOP Compliance

| 條款 | 結論 | 說明 |
|------|------|------|
| Thin Facade 原則（v0.3 §13 / ProblemType §1.5） | **符合** | `skills/vh_數學B1_QuadraticFunctionGraph.py` 與 draft 均僅委託 `generate_for_skill` / `check_answer`，無實體數學邏輯 |
| ProblemTypeSpec 唯一權威來源 | **部分符合** | induced spec 存在且被 `load_problem_type_spec` 讀取；但 9/18 slot 無法對應 induced spec，audit 跳過 |
| 反特例化原則 | **符合（架構層）** | 未發現 skill_id 硬編碼放行/阻擋；問題集中在 slot 模板本身 |
| Layer 6 雙表註冊（TASK_FAMILY_TO_SLOT + SLOT_REGISTRY） | **部分符合** | 22 個 target_task 均有 slot 映射；18 個 SLOT_REGISTRY 均有 callable；無 hollow registration |
| Localization Quality Gate | **未通過（runtime）** | 5 個二次函數 slot 全部 `localization_violation`；format validator 已能攔截 |
| 未修改 DB schema | **是** | 本輪無任何 schema 變更 |
| 未修改任何 skill 補丁 | **是** | 本輪無 skill 檔修改 |

---

## 3. File Inventory

| 檔案 | 存在 | Import 狀態 |
|------|------|-------------|
| `core/gencode/generated_question_format_validator.py` | ✅ (15,994 B) | OK |
| `core/gencode/runtime_skill_wrapper.py` | ✅ (11,510 B) | OK |
| `core/gencode/runtime_smoke.py` | ✅ (26,442 B) | OK |
| `core/gencode/slot_generators.py` | ✅ (43,603 B) | OK |
| `core/gencode/template_slot_resolver.py` | ✅ (13,243 B) | OK |
| `core/gencode/validators/__init__.py` | ✅ (1,436 B) | OK |
| `core/gencode/validators/answer_contract_validator.py` | ✅ (5,257 B) | OK |
| `core/gencode/validators/semantic_validator.py` | ✅ (3,080 B) | OK |
| `core/gencode/validators/condition_target_dependency.py` | ✅ (7,465 B) | OK |
| `tests/gencode/test_generated_question_format_validator.py` | ✅ (19,305 B) | OK |

- **整體 import**：`imports_ok = true`，無 import error
- **Circular import 風險**：低。`generated_question_format_validator` 不依賴 `runtime_skill_wrapper` / `slot_generators`；`validators/__init__.py` 僅委派 `answer_contract_validator`、`semantic_validator`、`condition_target_dependency`
- **`validate_generator_payload` 匯出來源**：`core.gencode.validators`（`validators/__init__.py`）

---

## 4. Validator Integration Check

| 項目 | 結果 |
|------|------|
| `generated_question_format_validator.py` 存在 | ✅ |
| `runtime_skill_wrapper.generate_for_skill()` 呼叫 | ✅（`validate_generator_payload` 之前，fail-fast `generator_format_unsafe:...`） |
| `runtime_smoke._validate_runtime_payload()` 呼叫 | ✅（placeholder 檢查後、answer shape 前；有 format error 則提前 return） |
| `slot_generators.generate_from_problem_type_spec()` 呼叫 | ❌ **未呼叫**（僅呼叫 `validate_generator_payload`） |
| 與 `core/gencode/validators/` 架構一致 | ✅ 語意/契約驗證仍由 validators 包負責；格式/語系由獨立模組負責 |
| 重複邏輯分散風險 | **中等**：`choices_duplicate` 同時出現在 format validator 與 semantic validator；`slot_generators` 路徑在 wrapper 前不經 format gate |

**建議（不修改）**：未來可考慮在 `generate_from_problem_type_spec()` 尾端也委派 `validate_generated_question_format`，或統一由 `runtime_skill_wrapper` 單一路徑出口驗證，避免 slot 直連測試繞過 format gate。

---

## 5. Thin Facade Audit

### `skills/vh_數學B1_QuadraticFunctionGraph.py`

| 檢查項 | 結果 |
|--------|------|
| SKILL_ID / GENERATOR_KEYS / GENERATOR_SPECS | ✅ |
| `generate()` → `generate_for_skill()` | ✅ |
| `check()` → `check_answer()` | ✅ |
| 實體公式 / 題幹模板 / if skill_id 特例 | ❌ 未發現 |
| 自行選 checker / 覆寫 answer_contract | ❌ 未發現 |
| LLM / codegen 註解污染 | ❌ 未發現 |
| **facade_pollution_detected** | **否** |

### `reports/gencode_closed_loop/drafts/vh_數學B1_QuadraticFunctionGraph.py`

- Thin Facade 結構乾淨（`facade_pollution_detected = false`）
- **注意**：draft 的 `GENERATOR_SPECS` 仍指向 `text_short_contextual_application`（2 筆重複），與正式 `skills/` 版（5 個 quadratic problem_type）**不同步** → 屬 **problem-type-level / publish artifact drift**，非 facade 污染

---

## 6. Slot Registry Audit

### SLOT_REGISTRY（18 keys，全部 callable）

`point_quadrant`, `point_quadrant_choice`, `symbolic_quadrant`, `symbolic_quadrant_choice`, `axis_distance_choice`, `symbolic_quadrant_statement_choice`, `two_point_distance_solution_set`, `two_point_distance_compute`, `linear_triangle_median_compute`, `function_value_numeric`, `linear_function_two_point_choice`, `linear_function_contextual_word_problem`, `quadratic_graph_vertex_axis_choice`, `quadratic_graph_translation_fill_blank`, `quadratic_graph_translation_short_answer`, `quadratic_vertex_form_properties`, `quadratic_standard_to_vertex_properties`, `division_point_coordinates`

### TARGET_TASK_GENERATOR_REGISTRY（4 keys）

`compute_internal_division_point_coordinates`, `compute_centroid_coordinates`, `compute_midpoint_coordinates`, `solve_point_from_section_ratio` → 均映射 `division_point_coordinates`

### TASK_FAMILY_TO_SLOT（22 mappings）

全部 target_task 均有 slot 字串；`target_task_slot_missing = []`；`slot_hollow_registration = []`

### Audit 跳過（`audit_skipped_missing_problem_type_spec`，9 slots）

無 induced spec 的 `template_slots.stem` / `target_task` / `problem_type_id` 可對應：

- `linear_function_contextual_word_problem`
- `linear_function_two_point_choice`
- `linear_triangle_median_compute`
- `point_quadrant_choice`
- `symbolic_quadrant`
- `symbolic_quadrant_choice`
- `symbolic_quadrant_statement_choice`
- `two_point_distance_compute`
- `two_point_distance_solution_set`

→ 標記 **`fallback_stub_risk`**：這些 slot 在無 spec 對應時，若走 `generate_from_problem_type_spec` 可能 fallback 至 `_slot_generic_single_choice` / `_slot_generic_short_answer`

### 映射品質問題（audit artifact）

`point_quadrant` 被 audit 映射到 `vh_數學B1_DistanceBetweenTwoPoints` 的 `solution_set` spec（因 target_task `compute_numeric` 碰撞），導致語意 blocker `invalid_answer_type`。**這是 spec-slot 對應歧義，非 slot 本身設計錯誤**，但顯示 induced spec 覆蓋不完整。

---

## 7. Slot Sample Format Audit

Seeds: `0,1,2,3,4`；每 slot 呼叫 `validate_generated_question_format` + `validate_generator_payload`

| slot_key | function | samples | pass | fail | blockers | first_failed_seed | question_preview |
|----------|----------|---------|------|------|----------|-------------------|------------------|
| axis_distance_choice | `_slot_axis_distance_choice` | 5 | 4 | 1 | `formula_not_wrapped` | 0 | 點 P(4,5) 到 x 軸的距離為何？ |
| division_point_coordinates | `_slot_division_point_coordinates` | 5 | 5 | 0 | — | — | — |
| function_value_numeric | `_slot_function_value_numeric` | 5 | 5 | 0 | — | — | — |
| linear_function_contextual_word_problem | — | 0 | — | — | `audit_skipped_missing_problem_type_spec` | — | — |
| linear_function_two_point_choice | — | 0 | — | — | `audit_skipped_missing_problem_type_spec` | — | — |
| linear_triangle_median_compute | — | 0 | — | — | `audit_skipped_missing_problem_type_spec` | — | — |
| point_quadrant | `_slot_point_quadrant` | 5 | 0 | 5 | `formula_not_wrapped`, `invalid_answer_type` (spec 錯配) | 0 | 點 P(4,5) 位於第幾象限？ |
| point_quadrant_choice | — | 0 | — | — | `audit_skipped_missing_problem_type_spec` | — | — |
| quadratic_graph_translation_fill_blank | `_slot_quadratic_graph_translation_fill_blank` | 5 | 0 | 5 | `formula_not_wrapped`, `localization_violation` | 0 | Relative to y=3x^2, the graph of y=3(x+2)^2+3 is shifted how? … |
| quadratic_graph_translation_short_answer | `_slot_quadratic_graph_translation_short_answer` | 5 | 0 | 5 | `formula_not_wrapped`, `localization_violation` | 0 | Compared with y=3x^2, how is the graph of y=3x^2+5 shifted vertically? |
| quadratic_graph_vertex_axis_choice | `_slot_quadratic_graph_vertex_axis_choice` | 5 | 0 | 5 | `formula_not_wrapped`, `localization_violation`, `choices_duplicate` | 0 | Given y=3(x+4)^2+4, which option correctly states … |
| quadratic_standard_to_vertex_properties | `_slot_quadratic_standard_to_vertex_properties` | 5 | 0 | 5 | `formula_not_wrapped`, `localization_violation` | 0 | Rewrite y=1x^2+4x+4 in vertex form … |
| quadratic_vertex_form_properties | `_slot_quadratic_vertex_form_properties` | 5 | 0 | 5 | `formula_not_wrapped`, `localization_violation`, `choices_duplicate` | 0 | For y=-3(x-1)^2+3, choose the correct graph property statement. |
| symbolic_quadrant | — | 0 | — | — | `audit_skipped_missing_problem_type_spec` | — | — |
| symbolic_quadrant_choice | — | 0 | — | — | `audit_skipped_missing_problem_type_spec` | — | — |
| symbolic_quadrant_statement_choice | — | 0 | — | — | `audit_skipped_missing_problem_type_spec` | — | — |
| two_point_distance_compute | — | 0 | — | — | `audit_skipped_missing_problem_type_spec` | — | — |
| two_point_distance_solution_set | — | 0 | — | — | `audit_skipped_missing_problem_type_spec` | — | — |

**統計**：registry 18 slots；可執行 audit 9；跳過 9；失敗 7；通過 2（`division_point_coordinates`, `function_value_numeric`）

---

## 8. English Template Pollution

### 靜態掃描（`core/gencode/slot_generators.py`）

| line | function / slot | 英文片段 | likely blocker |
|------|-----------------|----------|----------------|
| 703 | `_extreme_phrase` | `maximum {k}` / `minimum {k}` | `localization_violation` |
| 707 | `_vertex_axis_option` | `vertex (...), axis x=..., maximum/minimum` | `localization_violation` |
| 724 | `quadratic_graph_vertex_axis_choice` | `Given ... which option correctly states` | `localization_violation` |
| 743 | `quadratic_graph_vertex_axis_choice` | `The vertex is ...` (explanation) | `localization_violation` |
| 757–758 | `quadratic_graph_translation_fill_blank` | `Relative to ... Answer in the form 'left 2, up 3'` | `localization_violation` |
| 772 | `quadratic_graph_translation_fill_blank` | `Inside shift gives ...` (explanation) | `localization_violation` |
| 791–792 | `quadratic_graph_translation_short_answer` | `up`/`down`, `Compared with ... shifted vertically` | `localization_violation` |
| 805 | `quadratic_graph_translation_short_answer` | `Adding ... outside the square shifts` | `localization_violation` |
| 831 | `quadratic_vertex_form_properties` | `For ... choose the correct graph property` | `localization_violation` |
| 848 | `quadratic_vertex_form_properties` | `In y=a(x-h)^2+k, the vertex is` | `localization_violation` |
| 868 | `quadratic_standard_to_vertex_properties` | `Rewrite ... in vertex form` | `localization_violation` |

### Runtime 命中（question_text 進入學生端）

全部 5 個 quadratic slot × 5 seeds = **25/25** 英文題幹或英文答案片語（`up 5`, `left 2, up 3` 等）

**分類**：`slot_template_localization_issue`（非 source-level reject）

---

## 9. LaTeX / Formula Formatting Issues

| slot | 欄位 | 片段 | blocker | 建議分類 |
|------|------|------|---------|----------|
| 全部 5 quadratic slots | `question_text` | `y=3x^2`, `y=3(x+2)^2+3` 未包 `$...$` | `formula_not_wrapped` | `display_formula_needs_latex_wrapping` |
| `axis_distance_choice` | `explanation` | `|y|=5` 在中文句中（可接受） | `formula_not_wrapped`（邊界） | 可能需調整 validator 或改寫 explanation |
| `point_quadrant` | `question_text` | `P(4,5)` 觸發 `formula_not_wrapped` | `formula_not_wrapped` | 可能為 **false positive**（座標點非公式） |
| quadratic helpers | `metadata.givens` | `base=y=3x^2` raw | — | `raw_formula_should_stay_metadata_only`（metadata 可保留 raw，但 question_text 必須 LaTeX） |

未發現：`latex_unbalanced`, `latex_delimiter_not_allowed`, `markdown_code_fence_detected`（在本次 slot sample 中）

---

## 10. Choice Contract Issues

| slot | 問題 | blocker |
|------|------|---------|
| `quadratic_graph_vertex_axis_choice` | 英文 choice text；`maximum`/`minimum` 英文 | `localization_violation`, `choices_duplicate` |
| `quadratic_vertex_form_properties` | 同上 | `localization_violation`, `choices_duplicate` |
| `quadratic_standard_to_vertex_properties` | 英文 choice / stem | `localization_violation` |
| 全部 quadratic choice slots | `checker_type=choice_label_checker` ✅ | 無 `choice_checker_mismatch` |
| 全部 quadratic choice slots | `equivalence_type=choice_label`（spec）✅ | 無 `choice_contract_mismatch` |
| 全部 | question_text 未嵌入 `(A)(B)(C)(D)` | 無 `choices_embedded_in_question_text` |

**choices_duplicate 根因（觀察）**：`_vertex_axis_option` / `_extreme_phrase` 在特定 `(a,h,k)` 組合下產生相同 wrong option 文字；屬 **slot-level generator 多樣性** 問題。

---

## 11. QuadraticFunctionGraph Focus Audit

**Skill**：`vh_數學B1_QuadraticFunctionGraph`

| 檢查 | 結果 |
|------|------|
| py_compile | **pass** |
| `generate(level=1, seed=0..9)` | **0/10 pass** |
| 第一個 failed seed | **0** |
| runtime wrapper | 全部拋出 `RuntimeError: generator_format_unsafe:...` 或 `generator_semantically_unsafe:choices_duplicate` |
| runtime_smoke | `smoke_exception:generator_format_unsafe:formula_not_wrapped`（及 localization 組合） |
| 英文模板 fail | **是**（seeds 3,6,7,9 等含 localization） |
| LaTeX fail | **是**（全部 seeds `formula_not_wrapped`） |
| choice contract fail | **是**（seed 5 `choices_duplicate`） |
| slot fallback fail | **否**（有對應 slot，非 generic stub） |

**結論**：format validator **有效攔截** quadratic runtime 輸出；問題根源在 **slot 模板仍為英文 + raw LaTeX**，非 validator 失效。

---

## 12. Risk Classification

| 層級 | 發現 | 標記 |
|------|------|------|
| source-level | 無 | — |
| problem-type-level | draft `GENERATOR_SPECS` 與 skills 正式版不同步 | `publish_artifact_drift` |
| slot-level | 5 個 quadratic slot 英文模板 + raw `x^2` | `slot_template_localization_issue` |
| slot-level | quadratic choice duplicate distractors | `runtime_quality_issue` |
| runtime-quality | `generate_for_skill` 現已 fail-fast，學生端不會收到壞 payload | **gate 生效** |
| skill-level blocked | **不建議** | 依 SOP §4.C，此為可修復的 slot 模板問題，非整 skill 無 usable core |

---

## 13. Recommended Next Actions

### Global architecture cleanup
- 在 `generate_from_problem_type_spec()` 出口也委派 `validate_generated_question_format`（與 wrapper 對齊），避免測試/直連路徑繞過 format gate
- 釐清 `choices_duplicate` 在 format validator 與 semantic validator 的職責邊界，避免雙重回報

### Validator placement cleanup
- 評估 `P(4,5)` 座標點是否應從 `formula_not_wrapped` 排除（降低 false positive）
- 對 `metadata.givens` 中的 raw `y=...` 維持「僅 metadata 允許 raw」策略並文件化

### Slot template localization
- 將 `_shift_phrase`, `_extreme_phrase`, `_vertex_axis_option` 及 5 個 `_slot_quadratic_*` 的 stem/choices/explanation 全面改為繁體中文（台灣高職語境）
- 答案格式改為「向右 2、向上 3」而非 `left 2, up 3`

### LaTeX display/raw formula separation
- `_quadratic_vertex_form()` / `_quadratic_standard_form_from_vertex()` 回傳值應區分：
  - **display**（含 `$...$`，供 question_text）
  - **raw**（供 metadata / checker）

### Specific follow-up test cases
- 為 5 個 quadratic slot 各加 1 個 integration test（seed 固定，assert 無 `localization_violation` / `formula_not_wrapped`）
- 補齊 9 個 skipped slot 的 induced spec，使 audit 覆蓋率 18/18
- 同步 `reports/gencode_closed_loop/drafts/vh_數學B1_QuadraticFunctionGraph.py` 與 `skills/` 版 GENERATOR_SPECS

---

## 14. Final Status

**`AUDIT_PASS_WITH_FINDINGS`**

- Validator 模組存在、可 import、pytest 17/17 通過
- Runtime path（wrapper + smoke）已接入 format validator 且 **實際攔截** quadratic 壞輸出
- 發現 7/9 可測 slot 有 format/語意問題；二次函數區塊為主要痛點
- 未修改 DB schema；未修改 skill 補丁

---

## Appendix: Pytest

```
17 passed in 0.02s
tests/gencode/test_generated_question_format_validator.py
```
