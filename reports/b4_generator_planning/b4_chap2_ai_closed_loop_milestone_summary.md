# B4 Chapter 2 AI Closed-loop Milestone Summary

**類型：** Milestone summary（**僅文件**）  
**狀態：** MILESTONE_DOCUMENTED  
**本輪：** 不執行 implementation、不啟動下一 phase  

**必讀來源（撰寫時皆存在於 repo）：**

| 文件 | 路徑 |
|------|------|
| Chap2 deterministic mainline closure | `reports/b4_generator_planning/b4_chap2_deterministic_mainline_closure.md` |
| Phase 6G-0 | `reports/b4_generator_planning/b4_phase6g0_chap2_skill_availability_ux_cleanup_summary.md` |
| Phase 6H | `reports/b4_generator_planning/b4_phase6h_chap2_adaptive_audit_integration_plan.md` |
| Phase 6I | `reports/b4_generator_planning/b4_phase6i_adaptive_audit_logging_minimal_implementation_summary.md` |
| Phase 6J | `reports/b4_generator_planning/b4_phase6j_teacher_audit_visibility_runtime_ready_summary.md` |
| Runtime Smoke Gate SOP | `docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md` |
| Phase Prompt Templates | `docs/系統SOP/B4_phase_prompt_templates_v0.1.md` |
| AI 閉環與 Runtime-Ready 流程索引 | `docs/系統SOP/B4_AI閉環與RuntimeReady流程索引_v0.1.md` |

**missing：** 無（上表路徑均存在）。

---

## 1. Milestone Overview

B4 **Chapter 2** 已由「單純 deterministic 出題」推進到一個 **可驗收的 AI closed-loop milestone**：在 **deterministic mainline** 範圍內，形成 **出題 → 作答 → 批改 →（visibility-only）稽核寫入 → 教師端可視化** 的最小閉環，並與 **Runtime Smoke Gate（含 v0.1.2 §8.1 UX）**、**Prompt Template A/B/C/D**、**流程索引** 對齊，減少臨場長 prompt 與一次性零碎規格。

**本 milestone 明確不代表：**

- **不代表** Chap2 **全題型／全 skill** 已完成（許多題型仍 **reserved** 或 **deferred**，見 §8）。
- **不代表** **adaptive scoring、mastery、APR、remediation** 已依教學政策完整接入 mainline（目前稽核多為 **visibility-only**；deterministic 答題仍沿用既有 `update_progress` 路徑，見 Phase 6I 報告說明）。

**本 milestone 代表：**

- Chap2 **deterministic mainline**（**11** 個 `problem_type`）已 **CLOSED** 且 **MANUAL_SMOKE_PASSED**。
- 學生端 **runtime**（`/practice`、`/get_next_question`、`/check_answer`）與 **編碼／UX／blocked 路徑** 已達專案約定之 smoke 標準。
- **Skill 可用性 UX**（未開放／保留手寫）已對使用者友善且不外洩內部 phase／legacy／traceback（Phase 6G-0）。
- **稽核寫入**（Phase 6I）與 **教師可視化**（Phase 6J）補上「教學觀測」一環，**但不**將 gated 事件當成正誤分母、**不**把教師頁面當成 scoring 儀表板。

---

## 2. Completed Runtime-ready Problem Types

下列 **11** 題型皆為 **MANUAL_SMOKE_PASSED**（與 closure 報告 §1.1 一致）。

| phase | problem_type | skill_id | answer_type / checker | status |
|---|---|---|---|---|
| 6C | `classical_probability_fraction` | `vh_數學B4_ProbabilityDefinition` | `rational_fraction` / `check_rational_answer`（flexible） | **MANUAL_SMOKE_PASSED** |
| 6C | `complement_probability` | `vh_數學B4_ProbabilityProperties` | `rational_fraction` / `check_rational_answer`（flexible） | **MANUAL_SMOKE_PASSED** |
| 6C | `sample_space_count_numeric` | `vh_數學B4_SampleSpaceAndEvents` | `integer` / `check_integer_answer`（strict） | **MANUAL_SMOKE_PASSED** |
| 6C | `union_intersection_probability` | `vh_數學B4_ProbabilityProperties` | `rational_fraction` / `check_rational_answer`（flexible） | **MANUAL_SMOKE_PASSED** |
| 6C | `dice_coin_probability_count` | `vh_數學B4_ProbabilityDefinition` | `rational_fraction` / `check_rational_answer`（flexible） | **MANUAL_SMOKE_PASSED** |
| 6D | `conditional_probability_basic` | `vh_數學B4_ConditionalProbability` | `rational_fraction` / `check_rational_answer`（flexible） | **MANUAL_SMOKE_PASSED** |
| 6D | `without_replacement_conditional_probability` | `vh_數學B4_ConditionalProbability` | `rational_fraction` / `check_rational_answer`（flexible） | **MANUAL_SMOKE_PASSED** |
| 6E | `independent_joint_probability` | `vh_數學B4_IndependentEvents` | `rational_fraction` / `check_rational_answer`（flexible） | **MANUAL_SMOKE_PASSED** |
| 6E | `independent_at_least_one_probability` | `vh_數學B4_IndependentEvents` | `rational_fraction` / `check_rational_answer`（flexible） | **MANUAL_SMOKE_PASSED** |
| 6F / 6F-R | `expectation_discrete_basic` | `vh_數學B4_MathematicalExpectationDefinition` | `expected_value` / `check_expected_value_answer` | **MANUAL_SMOKE_PASSED** |
| 6F / 6F-R | `expectation_from_distribution` | `vh_數學B4_MathematicalExpectationDefinition` | `expected_value` / `check_expected_value_answer` | **MANUAL_SMOKE_PASSED** |

---

## 3. Runtime Integration Achieved

Chap2 deterministic mainline 已具備並通過各 phase 約定之整合與迴歸（詳見 closure §2 與各 phase summary），摘要如下：

- **`/practice`**：可進入練習（含 encoded / decoded `skill_id`）。
- **`/get_next_question`**：可取得題目 payload（雙重編碼路徑）。
- **`/check_answer`**：可批改（canonical／等值／invalid 等依各題型契約）。
- **Encoded / decoded `skill_id`**：後端解碼與傳遞路徑可測、可 smoke。
- **Frontend double-encoding guard**：對齊 Smoke Gate SOP **v0.1.1**（closure 記載自 6C-2R 起 `templates/index.html` `getSkillId()` 防護沿用）。
- **No legacy `skills.<skill_id>` fallback**：未開放 skill 不應跌回舊式 import。
- **Unsupported skill — friendly not-enabled**：清楚 **422**，對外文案不暴露內部 phase 或 traceback（**v0.1.2 §8.1**）。
- **Reserved handwriting / free-response blocked**：listing 等保留題型 hard-block，不進 deterministic allowlist runtime。
- **Chap1 regression preserved**：慣例以 allowlist 筆數等測試守護 Chap1（closure 記載 allowlist **13**）。

---

## 4. Textbook Alignment Result（Phase 6F-R）

Phase **6F-R**（期望值課本語境修補，見 `b4_phase6f_expected_value_textbook_alignment_repair_summary.md`）將 Phase 6F 原先偏抽象的「離散隨機變數」敘事，調整為 **高職 B4 課本 2-3 節**常見語境：

- **擲硬幣／擲骰子**「一次所得金額」「玩一次所得到金額」等 wording。
- **得失金額**可含 **正負報酬**（付出以負值呈現），符合課本例題感。
- **`expectation_from_distribution`**：改為課本風格 **已整理分布表**（`X`／`P(X)`），並以 **`E(X)=Σ x·P(X=x)`** 引導 explanation（逐項代入、化簡）。
- 抽卡／得分表類敘事納入「課本練習」式呈現（證據摘要见 6F-R 報告對 `textbook_examples` 之整理）。
- **manual smoke** 已依該輪報告完成驗收敘述；與本 milestone 一併視為 **Chap2 mainline 教學可信度**之一環。

---

## 5. Skill Availability / UX Cleanup（Phase 6G-0）

Phase **6G-0**（見 `b4_phase6g0_chap2_skill_availability_ux_cleanup_summary.md`）收斂 **未開放 skill** 與 **reserved listing** 的對外體驗：

- **已開放 skill**：正常 **200** 出題（與 allowlist 一致）。
- **未開放 skill**：**422**，`error` 為固定公開字串 ——  
  `此技能尚未開放自動出題。 Chap2 skill not enabled in current deterministic runtime.`
- **Reserved listing**（`sample_space_listing` / `event_set_listing` / `subset_listing`）：**422**，  
  `此題型保留為手寫／開放式作答，尚未於自動出題中開放。 This problem type is reserved for handwriting/free-response review.`
- **不再對使用者外洩**：內部 **Phase 6C-1** 代號、**legacy import**／**No module named**、**traceback**、raw **encoded / double-encoded** `skill_id` 等（以 6G-0 測試與報告為準）。

---

## 6. Adaptive Audit Visibility Loop（Phase 6H / 6I / 6J）

### Phase 6H（Planning，ACCEPTED）

- **Visibility-only audit** 路線圖：**不**在該輪接入 **mastery / APR / remediation**；產出為單一 planning report。

### Phase 6I（Implementation，MANUAL_SMOKE_PASSED）

- 新增資料表／ORM：**`b4_chap2_visibility_audit_logs`**（詳見 6I 報告）。
- **`record_kind=deterministic_answer`**：記錄 checker、正誤、答案類型等（**visibility**；與既有 `update_progress` 關係見 6I §1.2）。
- **`record_kind=gated`**：  
  - **`not_enabled_skill`**  
  - **`reserved_problem_type`**  
- **Gated 事件不進正誤分母**（不當成 scoring 統計用途）。

### Phase 6J（Implementation，MANUAL_SMOKE_PASSED）

- **Teacher audit visibility**：唯讀呈現 6I 稽核列。
- **`GET /teacher/b4-chap2-audit`**（HTML）、**`GET /api/teacher/b4-chap2-audit`**（JSON）。
- 查詢參數：**`limit`**、**`record_kind`**、**`skill_id`**、**`problem_type_id`**。
- **Teacher / admin** 可檢視；**student** 不可（HTML 導向 dashboard、API **403**）。
- **Visibility-only**：不影響成績、不影響出題、不觸發 remediation。

---

## 7. SOP / Prompt Template Consolidation

本 milestone 與下列 **文件收斂**一併完成「可複製工作流」：

- **Runtime Smoke Gate SOP**（**v0.1.2**：含 **§8.1** 未開放／保留題型 **UX**）：作為 **deterministic batch** 與 **manual smoke** 的權威檢查清單來源。
- **`B4_phase_prompt_templates_v0.1.md`**：**Template A**（planning）、**B**（runtime-ready batch）、**C**（closure）、**D**（small repair）— 後續 phase **不應**每次從零撰寫長篇 prompt，**應優先**複製對應模板欄位並引用既有 SOP 章節。
- **`B4_AI閉環與RuntimeReady流程索引_v0.1.md`**：說明 **SOP 閱讀順序** 與 **A/B/C/D 選用規則**、何時只更新 changelog／phase report。

---

## 8. Still Not Done / Explicitly Deferred

以下項目 **不是 bug**，而是 **明確 deferred scope**（與 closure §5／各 phase guardrails 一致，並含產品層未承諾能力）：

| 類別 | 項目 |
|------|------|
| Skill / 題型未開放 | `vh_數學B4_ProbabilityOperations`、`vh_數學B4_BasicConceptsOfSets`、`vh_數學B4_ApplicationsOfExpectation`、`vh_數學B4_MathematicalExpectation`（自評／綜合） |
| Reserved listing | `sample_space_listing`、`event_set_listing`、`subset_listing`（手寫／開放式保留） |
|  scoring / AI 批改 | handwriting / free-response **自動評分**（非本 milestone） |
| Adaptive 深度接入 | **adaptive scoring、mastery、APR、remediation** 之政策化整合（6H 規劃外之 implementation） |
| 測試基建 | **full HTTP shared smoke fixture**（若未來要統一跨測試之瀏覽器級迴歸） |
| 產品化儀表 | **Dashboard analytics / charts**（6J 為最小列表，非分析平台） |

---

## 9. Why This Matters

### 工程面

- **可複製**：Runtime-ready **batch**（generator → checker → router → allowlist → route → tests → report）已可在 Chap2 驗證；後續章節可套用 **同一 SOP + Template B** 節奏。
- **可減少一問一答**：Guardrails 集中在 SOP 與 **Template A–D**，避免每輪重貼相同限制。
- **可回滾／可測試**：每 phase 以 pytest 與 smoke checklist 收口；closure 與 milestone 文件提供 **決策錨點**。

### 教學面

- **題幹貼近高職 B4**（尤其 6F-R 期望值語境），降低「像 AI 習題不像課本」的摩擦。
- **教師可看** Chap2 deterministic 作答稽核與 **gated** 狀態（6I／6J），利於課堂觀摩與品質確認，**不**把 gated 當成「學生做錯」。
- **未開放／保留題型** 以清楚中文釋義替代「系統壞掉」體感（6G-0）。
- **為未來自適應資料**打底：visibility 軌跡已可留存，**待政策決定**後再接 scoring（6L 類規劃），避免一步到位失控。

---

## 10. Recommended Next Steps（不執行）

| Option | 內容 | 建議模板 |
|--------|------|----------|
| **A — Phase 6K** | **Teacher Audit Visibility Refinement**：測試資料／雜訊列過濾策略、簡單篩選或排序 UX；**不做** scoring | 視範圍選 **B**（小功能）或 **A**（若先規劃） |
| **B — Phase 6L** | **Adaptive Scoring Policy Planning**：哪些 deterministic `problem_type` 可進 **mastery／APR**、邊界與風險；**僅 planning** | **Template A** |
| **C — Phase 7A** | **Next Chapter Planning Package**：將本 milestone 流程複製到下一章／下一冊 | **Template A**（先行）→ 再 **Template B** 批次 |

**優先順序建議：**

1. 若近期目標是 **對外展示完整「學—教—稽核」閉環**：優先 **6K**（體驗拋光）或 **6L**（Scoring 政策與路線圖，仍先 planning）。
2. 若目標是 **大量教材與多章擴張**：優先 **7A**，避免在單章上過度堆疊儀表功能而延誤章節推進。

---

## 11. Final Confirmation

| 項目 | 是/否 |
|------|------|
| 是否只新增 milestone summary | **是** |
| 是否修改 production code | **否** |
| 是否修改 tests | **否** |
| 是否修改 routes | **否** |
| 是否修改 templates | **否** |
| 是否修改 generators | **否** |
| 是否修改 validators | **否** |
| 是否修改 database | **否** |
| 是否修改 coverage matrix | **否** |
| 是否修改 allowlist | **否** |
| 是否修改 adaptive scoring / mastery / APR / remediation | **否** |
| 是否新增題型 | **否** |
| 是否啟動下一 phase | **否** |

---

*本文件僅總結 Chap2 已達成之 AI closed-loop milestone，細節與證據仍以各 phase report 與 SOP 正文為準。*
