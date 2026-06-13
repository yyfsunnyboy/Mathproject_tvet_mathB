# QuadraticFunctionGraph Phase1 Anchor Audit

## 1. Scope

| 項目 | 值 |
|------|-----|
| 模式 | **只讀檢查**（未修改 production code / DB / skill 檔） |
| skill_id | `vh_數學B1_QuadraticFunctionGraph` |
| 執行時間 | 2026-06-13 11:22:04 (UTC+8 本地時間) |
| 專案根目錄 | `e:\Python\Mathproject_tvet_mathB` |
| 參考 SOP | Gencode v0.3 總體設計、ProblemType 規格包 v0.3、AnswerContract Gate v0.3 |

---

## 2. DB Skill Mapping

### 2.1 `skills_info`

| 欄位 | 值 |
|------|-----|
| skill_id | `vh_數學B1_QuadraticFunctionGraph` |
| skill_en_name | `QuadraticFunctionGraph` |
| skill_ch_name | 二次函數的圖形 |
| category | `1-3 二次函數` |
| description | 數學B1 1 坐標系與函數圖形 1-3 二次函數 - 二次函數的圖形 |
| input_type | `text` |
| is_active | `1`（啟用） |
| consecutive_correct_required | 3 |
| order_index | 0 |

### 2.2 `skill_curriculum`

**查詢結果：0 列。** 此 skill 在 `skill_curriculum` 中無對應列（僅 `skills_info.description` 與 `textbook_examples` 提供章節語意）。

### 2.3 `textbook_examples`

| 項目 | 值 |
|------|-----|
| 總筆數（Python UTF-8 查詢） | **4** |
| example id 清單 | 4450, 4460, 4466, 4503 |
| 全部 skill_id | `vh_數學B1_QuadraticFunctionGraph` ✓ |
| source_volume | 數學B1 |
| source_chapter | 1 坐標系與函數圖形 |
| source_section | 1-3 二次函數 |

> **備註：** PowerShell `sqlite3` CLI 以錯誤編碼查 `skill_id` 時 COUNT 回傳 0；Python `sqlite3` 以 UTF-8 參數查詢確認 4 筆皆存在且 mapping 正確。

### 2.4 各例題摘要

| id | source_description | problem_type (DB) | correct_answer | subskill_id / problem_type_id (DB) |
|----|-------------------|-------------------|----------------|-------------------------------------|
| 4450 | 1-3習題 基礎題 1 | textbook_exercise | （空） | 無 |
| 4460 | 例1 | textbook_example | ①右 ②2 ③上 ④1 ⑤x=2 ⑥(2,1) | 無 |
| 4466 | 隨堂練習1 | in_class_practice | （空） | 無 |
| 4503 | CH1自我評量 題13 | self_assessment | （空，選擇題無標準答案欄） | 無 |

DB schema 無 `example_id`、`subskill_id`、`problem_type_id` 欄位；主鍵為 `id`，外鍵為 `skill_id`。

---

## 3. Source Examples Content

### 4450 — 二次函數圖形平移（填空）

**題幹：**
- (1) $y=-2x^2+3$ 的圖形，是由 $y=-2x^2$ 的圖形**向上平移** ___ 個單位而得。
- (2) $y=-2(x+7)^2$ 的圖形，是由 $y=-2x^2$ 的圖形**向左平移** ___ 個單位而得。

**判定：** ✅ **是二次函數圖形題**（頂點式平移、鉛直/水平平移）。

### 4460 — 例1 頂點式平移與對稱軸/頂點

**題幹：** $y=\frac{1}{2}(x-2)^2+1$ 的圖形，是由 $y=\frac{1}{2}x^2$ 水平向①平移②個單位，再鉛直向③平移④個單位，且其對稱軸為直線⑤，頂點為⑥。

**答案摘要：** 右、2、上、1、x=2、(2,1)

**判定：** ✅ **是二次函數圖形題**（頂點式、平移、對稱軸、頂點）。

### 4466 — 隨堂練習1（同型）

**題幹：** $y=-2(x+1)^2-2$ 的圖形，是由 $y=-2x^2$ 水平/鉛直平移，求對稱軸與頂點。

**判定：** ✅ **是二次函數圖形題**。

### 4503 — 自我評量選擇題（圖形性質判斷）

**題幹：** 有關二次函數 $y=-x^2+2x+1$ 的圖形，下列敘述何者**錯誤**？
- (A) 頂點坐標為 (1,2)
- (B) 對稱軸 x = −1
- (C) 在 x=1 時，y=2 是最大值
- (D) 向右平移 2 單位的新函數為 $y=-(x-3)^2+2$

**判定：** ✅ **是二次函數圖形題**（頂點、對稱軸、最值、平移；題幹內嵌 A–D 選項）。

### 綜合結論

**四題皆為「二次函數的圖形」課本原題，DB skill mapping 正確。** 問題不在 DB 錯掛 skill，而在 Phase 1 anchor / 分類管線。

---

## 4. Phase 1 Classification

### 4.1 摘要欄位（`vh_數學B1_QuadraticFunctionGraph_phase1_summary.json`）

| 欄位 | 值 |
|------|-----|
| source_example_count | 4 |
| main_skill_anchor.expected_task_families | `["coordinate_system_family"]` |
| expected_subskill_candidates | `choose_possible_coordinate`, `classify_quadrant`, `compute_axis_distance` |
| skill_anchor_scope | `default` |
| observed_target_task_distribution | `{"contextual_application": 4}` |
| source_family_distribution | `{"generic_numeric_family": 4}` |
| uniform_core_target_task | `contextual_application` |
| alignment_score | 0.8 |
| source_alignment_status | `warn` |
| skill_problem_type_alignment_status | `block` |
| sop_gate_status | `FAIL` |
| classifier_source (top-level) | `rule_pack` |
| spec_mode | `ai_first_induce_from_sources` |
| clause45_escalation_applied | `true` |
| clause45_rescued_example_ids | [4450, 4460, 4466, 4503] |

### 4.2 candidate_problem_types（Phase 1 最終產出）

| problem_type_id | matched_example_ids | answer 型態 |
|-----------------|---------------------|-------------|
| `text_short_contextual_application` | 4450, 4460, 4466 | text_short |
| `choice_contextual_application` | 4503 | single_choice（source_has_choices） |

### 4.3 逐題 final_classification（節錄）

| example_id | final_target_task | final_task_family | classification_source | classification_confidence |
|------------|-------------------|-------------------|----------------------|---------------------------|
| 4450 | compute_numeric → **contextual_application** (clause45) | generic_numeric_family | ai_needs_review → clause45_unclassified_exception | rule_confidence 0.2 |
| 4460 | 同上 | generic_numeric_family | clause45_unclassified_exception | — |
| 4466 | 同上 | generic_numeric_family | clause45_unclassified_exception | — |
| 4503 | contextual_application | generic_numeric_family | clause45_unclassified_exception | — |

AI 分類證據（4460 節錄）：候選 subskill 屬於 `coordinate_system_family`，與拋物線平移/頂點/對稱軸任務不符 → `needs_review`。

### 4.4 blockers / warnings

**invalid_skill_level_blockers（SOP gate）：**
- `majority_needs_review`
- `source_examples_mismatch`

**alignment_warnings：**
- `majority_sources_need_human_subskill_review`
- `uniform_core_target_task_alignment_threshold_relaxed`
- `disallowed_blocker_promoted_to_warning:majority_needs_review`
- `disallowed_blocker_promoted_to_warning:source_examples_mismatch`

### 4.5 四個核心問題的回答

1. **為什麼 `main_skill_anchor` 是 `coordinate_system_family`？**  
   `build_main_skill_anchor()` 從 skill metadata 提取 terms，其中包含章節字串 **「1 坐標系與函數圖形」/「坐標系與函數圖形」**。`infer_skill_families_from_terms()` 在 `FAMILY_SKILL_HINTS_SCORED` 中匹配 hint **「坐標系」**（weight 60），且 taxonomy **不存在** `quadratic_function_graph_family` 或「二次函數」專屬 family。`_is_linear_function_skill()` 的防 hijack 邏輯**僅適用一次函數**，二次函數 skill 未受保護。

2. **從哪個 rule / config / cache 來？**  
   - **Family：** `core/gencode/task_families.py` → `COORDINATE_SYSTEM_FAMILY` hints  
   - **Subskills：** `core/gencode/main_skill_anchor.py` L168–173（當 `COORDINATE_SYSTEM_FAMILY ∈ expected_families` 且非 function_concept 時，注入 `classify_quadrant`, `choose_possible_coordinate`, `compute_axis_distance`）  
   - **非** DB cache；**非** 舊 induced spec 寫回 anchor（anchor 在 induction 入口即時計算）

3. **是否與 skill metadata 不一致？**  
   **是。** metadata 明確為「二次函數的圖形 / QuadraticFunctionGraph / 1-3 二次函數」，但 anchor 推成坐標系基礎幾何 subskills。

4. **是否有舊 anchor cache 污染？**  
   **否（anchor 層）。** anchor 為確定性 recompute。  
   **是（artifact 層）：** 本輪 `reports/gencode_closed_loop/induced_specs/vh_數學B1_QuadraticFunctionGraph.json` 已被新一輪錯誤 induction 覆寫為 `text_short_contextual_application`；但 `skills/vh_數學B1_QuadraticFunctionGraph.py`（2026-06-08 publish）仍保留正確的 5 個 quadratic problem types — **draft/formal drift**。

---

## 5. Skill Anchor Source Trace

### 5.1 決定 `coordinate_system_family` 的檔案鏈

```
skill_id + skills_info metadata
  → core/gencode/main_skill_anchor.py::build_main_skill_anchor()
    → extract_skill_terms() 含 chapter "1 坐標系與函數圖形"
    → core/gencode/task_families.py::infer_skill_families_from_terms()
      → 命中 COORDINATE_SYSTEM_FAMILY hint "坐標系" (score 60)
    → infer_expected_subskill_candidates()
      → COORDINATE_SYSTEM_FAMILY 分支注入坐標系 subskills
```

### 5.2 human_confirmed rule pack **存在但未主導 induction**

`configs/gencode/classifiers/phase1_rule_packs.yaml` L86–123 已定義：

- `classifier_source: human_confirmed`
- `problem_type_id: text_short_compute_vertex_and_axis`
- 四題 example_id 4450/4460/4466/4503 皆映射至該題型
- `single_primary_problem_type: true`，禁止自動切選擇題

Phase 1 top-level `classifier_source: "rule_pack"` 表示 rule pack **有載入**，但 `spec_mode: ai_first_induce_from_sources` 使 `induce_problem_types_from_examples()` **覆寫** rule pack 分類結果。Phase 1 JSON 中**完全不出現** `text_short_compute_vertex_and_axis` 或 `matched_registered_yaml_rule_pack`。

### 5.3 fallback / 硬編碼規則

| 機制 | 檔案 | 作用 |
|------|------|------|
| Clause 4.5 未分類強推 | `problem_type_induction.py::apply_clause45_unclassified_exception_escalation` | 4 題 `unclassified_low_confidence` → 強制 `contextual_application` + `fallback_*` proxy |
| `_observed_target_task_for_clause45` 預設 | 同上 L561 | 無有效 task 時 fallback 為 **`contextual_application`** |
| expected_family_relaxation | `problem_type_induction.py` | `uniform_core_target_task_distribution` 放寬 family 對齊門檻 |
| contextual → linear slot | `template_slot_resolver.py` L30 | `contextual_application` → `linear_function_contextual_word_problem` |

### 5.4 關鍵字搜尋摘要

| 關鍵字 | 主要命中 |
|--------|----------|
| `QuadraticFunctionGraph` | skills 檔、rule pack、reports |
| `coordinate_system_family` | phase1 summary、draft spec、main_skill_anchor 推導鏈 |
| `quadratic_*` | **formal skill** + slot_generators（正確路徑）；**未**出現在 phase1 anchor |
| `contextual_application` | phase1/2 錯誤 induction 主路徑 |
| `fallback_contextual_application_2` | phase1 induced_specs、phase2 choice 分支 |

---

## 6. Phase 2 Spec Trace

### 6.1 `text_short_contextual_application`

| 欄位 | 值 |
|------|-----|
| source_example_count | 3（4450, 4460, 4466） |
| answer_type | `text_short` |
| checker | `text_short_checker` |
| equivalence_type | `exact_string` |
| choices_required | false |
| source_has_choices | false |
| presentation_mode | `""`（空） |
| template_families | `["contextual_application"]` |
| target_task | `contextual_application` |
| task_family | `generic_numeric_family` |
| generator_contract.template_slots.stem | **`linear_function_contextual_word_problem`** |
| generator_status | `runtime_ready_with_warning` |
| usable_for_phase3 | **true** |

### 6.2 `choice_contextual_application`

| 欄位 | 值 |
|------|-----|
| source_example_count | 1（**4503**） |
| answer_type | `single_choice` |
| checker | `choice_label_checker` |
| equivalence_type | `choice_label` |
| choices_required | true |
| source_has_choices | **true** |
| presentation_mode | `single_choice` |
| template_families | `contextual_application` |
| generator_contract.template_slots.stem | `linear_function_contextual_word_problem` |

### 6.3 五個判斷題的回答

1. **`text_short_contextual_application` 為何進 Phase 3？**  
   Phase 2 標記 `usable_for_phase3: true`；alignment blockers 在 phase2 summary 為空陣列（`phase1_alignment_blocked: false`）。SOP 允許帶 warning 推進；Phase 3 未因 semantic misalignment 硬擋。

2. **是否應屬於 QuadraticFunctionGraph？**  
   **否。** 此 ID 為 generic fallback proxy，語意上屬一次函數情境應用槽，與二次函數圖形 skill 不符。human_confirmed rule pack 期望的 `text_short_compute_vertex_and_axis` 才對齊。

3. **`choice_contextual_application` 是否因 4503 有選項而建立？**  
   **是。** 4503 題幹內嵌 (A)(B)(C)(D)；Phase 1 grouping 依 answer contract 差異拆出 choice 變體（`fallback_contextual_application_2` → Phase 2 canonicalize 為 `choice_contextual_application`）。

4. **short_answer 路徑為何 runtime 產出 choice label？**  
   `text_short_contextual_application` 的 `target_task=contextual_application` 經 `resolve_template_slot()` 對應到 **`linear_function_contextual_word_problem`** slot（`template_slot_resolver.py`）。該 slot 設計為產生四選項 + A/B/C/D 答案。`validate_generator_payload()` 偵測到 short_answer contract 卻有 choices → 拋出 `generator_semantically_unsafe:choices_must_be_empty_for_short_answer,short_answer_must_not_be_choice_label`。

5. **answer_contract coercion 還是 classification 錯誤？**  
   **主因：source classification / spec 錯誤**（錯誤 problem_type + 錯誤 slot 綁定）。  
   coercion 非主因：Phase 3 對 `text_short` 並未強制升級為 choice；反而是 **錯誤的 contextual_application 路由** 把簡答 spec 送進 linear choice slot。

---

## 7. Draft/Formal Drift

### 7.1 Formal `GENERATOR_SPECS`（`skills/vh_數學B1_QuadraticFunctionGraph.py`）

| problem_type_id | checker_key | equivalence_type |
|-----------------|-------------|------------------|
| quadratic_graph_vertex_axis_choice | choice_label_checker | choice_label |
| quadratic_graph_translation_fill_blank | text_short_checker | exact_string |
| quadratic_graph_translation_short_answer | text_short_checker | exact_string |
| quadratic_vertex_form_properties | choice_label_checker | choice_label |
| quadratic_standard_to_vertex_properties | choice_label_checker | choice_label |

### 7.2 Draft `GENERATOR_SPECS`（`reports/.../drafts/vh_數學B1_QuadraticFunctionGraph.py`）

| problem_type_id | checker_key | equivalence_type |
|-----------------|-------------|------------------|
| text_short_contextual_application | text_short_checker | exact_string |
| text_short_contextual_application | text_short_checker | exact_string |（**重複列**）

### 7.3 差異摘要

- problem_type_id：**完全不同**（quadratic 專域 vs generic contextual fallback）
- checker：formal 混合 choice/text_short；draft 僅 text_short
- equivalence：formal 有 choice_label；draft 僅 exact_string
- draft 有 **GENERATOR_KEYS 重複** bug

### 7.4 Runtime 使用路徑

| 路徑 | 使用檔案 |
|------|----------|
| 前端 `/practice` | `skills/vh_數學B1_QuadraticFunctionGraph.py`（`core/routes/practice.py` → `importlib.import_module("skills.{skill_id}")`） |
| 網頁 Phase 3 smoke | `reports/gencode_closed_loop/drafts/vh_數學B1_QuadraticFunctionGraph.py`（phase3_package_summary.skill_file_path） |

Phase 3 smoke **failed**（seed=0, problem_type=`text_short_contextual_application`）。  
2026-06-08 publish summary 顯示 formal skill 曾 smoke **passed**，但本輪重跑 Phase 1–3 產出錯誤 draft。

**draft_formal_drift: true**

---

## 8. Root Cause Classification

| 類型 | 判定 | 說明 |
|------|------|------|
| `db_skill_mapping_error` | ❌ | 四題 DB mapping 正確，皆為二次函數圖形 |
| `skill_anchor_rule_error` | ✅ **主因** | 章節「坐標系」hint 劫持 anchor；缺 quadratic family / subskill taxonomy |
| `source_classification_error` | ✅ **主因** | ai_first induction 忽略 human_confirmed rule pack；錯誤歸為 contextual_application |
| `legacy_cache_pollution` | ⚠️ 次要 | induced_specs / draft 被本輪錯誤覆寫；formal skill 仍為舊版正確產物 |
| `phase1_fallback_overreach` | ✅ **主因** | Clause 4.5 將 4 題全推成 contextual_application proxy |
| `answer_contract_coercion_error` | ❌ 非主因 | 問題在 slot 路由，非 §4.3 coercion |
| `draft_formal_artifact_drift` | ✅ | 本輪 draft 與 2026-06-08 formal 嚴重分歧 |
| `slot_generator_error` | ❌ | slot 正確拒絕非法 payload；不應修 slot 來「通過」錯誤 spec |

---

## 9. Recommended Next Action

以下僅為建議，**本輪未執行任何修改**。

### 9.1 必須先修 skill anchor rule（優先）

1. 在 `task_families.py` / `main_skill_anchor.py` 新增 **quadratic function graph** family hints（如「二次函數」「quadraticfunctiongraph」「拋物線」「頂點式」），score 應高於 `coordinate_system_family`（60）。
2. 仿 `_is_linear_function_skill()` 增加 **quadratic function skill guard**：當 skill terms 含 quadratic 語意時，**discard** `coordinate_system_family` 的坐標系背景 hijack。
3. 定義 expected subskills：`quadratic_graph_translation`, `quadratic_vertex_axis_identification`, `quadratic_graph_properties_choice` 等（與現有 formal problem types 對齊）。

### 9.2 必須釐清 rule pack vs induction 優先序

1. 對 `human_confirmed` rule pack skills，`ai_first_induce_from_sources` 不應覆寫已確認的 `problem_type_id`。
2. 或 Phase 1 對此 skill 改用 `rule_first_induce_from_sources` / 直接 trust rule pack entries。

### 9.3 必須清 cache / reports（重跑前）

1. 刪除或歸檔本輪錯誤 artifacts：`induced_specs/vh_數學B1_QuadraticFunctionGraph.json`、draft spec、draft skill wrapper。
2. **勿**以本輪 draft 覆寫 formal `skills/vh_數學B1_QuadraticFunctionGraph.py`（目前 formal 仍為可用 quadratic 規格）。

### 9.4 必須重跑 Phase 1–3（anchor 修正後）

1. 確認 Phase 1 產出 `text_short_compute_vertex_and_axis` 或等價 quadratic problem types。
2. Phase 3 smoke 應命中 `quadratic_graph_*` slots，而非 `linear_function_contextual_word_problem`。

### 9.5 不應修改 slot generator

- 現有 `validate_generator_payload` 正確攔截 short_answer + choices 污染。
- **禁止**為 `text_short_contextual_application` 寫補丁通過 smoke（違反 SOP 反特例化）。

### 9.6 DB mapping

- **不需修改 DB** skill/example mapping。
- 可選：補填 `skill_curriculum` 列以強化 metadata（非阻斷項）。

---

## 10. Final Status

**`AUDIT_PASS_WITH_ROOT_CAUSE`**

---

## Terminal Summary（稽核輸出）

```
audit_status=AUDIT_PASS_WITH_ROOT_CAUSE
report_path=e:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\quadratic_function_graph_anchor_audit_20260613_112204.md
root_cause=skill_anchor_rule_error+source_classification_error+phase1_fallback_overreach
examples_are_quadratic_graph_related=true
anchor_family_detected=coordinate_system_family
expected_anchor_family=quadratic_function_graph_family (或 function_concept_family 下之 quadratic 專域 subskills)
draft_formal_drift=true
files_modified_count=1
db_modified=false
skill_modified=false
```
