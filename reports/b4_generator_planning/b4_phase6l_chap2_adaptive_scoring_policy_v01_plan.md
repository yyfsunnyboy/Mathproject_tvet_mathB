# B4 Chapter 2 Phase 6L：Adaptive Scoring Policy v0.1 Planning

**類型：** Planning-only（`docs/系統SOP/B4_phase_prompt_templates_v0.1.md` → **Template A**）  
**狀態：** PLANNING_COMPLETE（**不**含 implementation）  
**輸出：** 本文件 `reports/b4_generator_planning/b4_phase6l_chap2_adaptive_scoring_policy_v01_plan.md`

**設計原則（本 phase 強制對齊）：**

- **不**將 adaptive 設計成「Chap2 全題型完成後才開始」；**v0.1 僅涵蓋已 closure 之 11 個 deterministic `problem_type`**，其餘 skill／listing／手寫等維持 deferred，**不阻擋** policy 版本演進。
- **Adaptive scoring 必須版本化、可擴充**：以 **政策 ID + 變更日誌** 管理；未來 **v0.2** 以 **附加訊號（additive signal）** 納入 handwriting／free-response／特殊題型，**不重做** v0.1 核心語意。
- **v0.1** 僅規劃 **deterministic** 之 **dry-run／preview** 與 **mastery／APR／fail_streak／remediation** 的安全接軌敘述；**不**納入手寫／開放式評分。

**必讀來源（撰寫時皆存在於 repo）：**

| 文件 | 路徑 |
|------|------|
| B4 Phase Prompt Templates | `docs/系統SOP/B4_phase_prompt_templates_v0.1.md` |
| AI 閉環與 Runtime-Ready 流程索引 | `docs/系統SOP/B4_AI閉環與RuntimeReady流程索引_v0.1.md` |
| Chap2 AI closed-loop milestone | `reports/b4_generator_planning/b4_chap2_ai_closed_loop_milestone_summary.md` |
| Chap2 deterministic mainline closure | `reports/b4_generator_planning/b4_chap2_deterministic_mainline_closure.md` |
| Phase 6H Adaptive Audit Planning | `reports/b4_generator_planning/b4_phase6h_chap2_adaptive_audit_integration_plan.md` |
| Phase 6I Visibility Audit Logging | `reports/b4_generator_planning/b4_phase6i_adaptive_audit_logging_minimal_implementation_summary.md` |
| Phase 6J Teacher Audit Visibility | `reports/b4_generator_planning/b4_phase6j_teacher_audit_visibility_runtime_ready_summary.md` |

**missing：** 無。

---

## 1. Scope and Guardrails

### 1.1 本輪目的

規劃 Chap2 **已完成**之 **11** 個 deterministic `problem_type` 未來如何 **安全** 接入 **mastery／APR／fail_streak／remediation**，並定義 **policy v0.1** 之 **版本字串、事件邊界、dry-run／preview** 策略。**本輪僅文件**。

### 1.2 硬性限制（本輪與本報告邊界）

| 項目 | 確認 |
|------|------|
| 修改 production code | ❌ 否 |
| 修改 tests | ❌ 否 |
| 修改 routes / templates | ❌ 否 |
| 修改 generators / validators | ❌ 否 |
| 修改 database | ❌ 否 |
| 修改 coverage matrix | ❌ 否 |
| 修改 allowlist | ❌ 否 |
| 修改 adaptive scoring / mastery / APR / fail_streak / remediation | ❌ 否 |
| 新增題型 | ❌ 否 |
| 處理 deferred skill generator（未開放 Chap2 skill 之自動出題） | ❌ 否（**不**在本輪擴題） |
| 將 handwriting / free-response 納入 v0.1 scoring | ❌ 否 |
| 啟動 implementation | ❌ 否 |

**唯一允許新增：** 本 planning report。

---

## 2. Current Chap2 Closed-loop Status

### 2.1 已完成（與 milestone／closure 對齊）

| 能力 | 說明 |
|------|------|
| **Deterministic generation** | 11 個 `problem_type` mainline **CLOSED**、**MANUAL_SMOKE_PASSED**。 |
| **`check_answer`** | Runtime 可批改；與 checker 契約見 closure §3。 |
| **Visibility audit logging（6I）** | `b4_chap2_visibility_audit_logs`：`deterministic_answer`、`gated`（not_enabled／reserved）。 |
| **Teacher audit visibility（6J）** | `/teacher/b4-chap2-audit`、`/api/teacher/b4-chap2-audit`；唯讀、teacher/admin。 |
| **Not-enabled UX（6G-0）** | 未開放 skill **422**、固定公開文案；不外洩內部 phase／legacy／traceback。 |
| **Reserved handwriting blocked** | `sample_space_listing` 等保留題型 **422**；**不**進 deterministic allowlist 出題。 |

### 2.2 與「正式 adaptive scoring」的關係（本報告用語）

| 敘述 | 說明 |
|------|------|
| **審計與可視化已就緒** | 6H→6I→6J 形成 visibility 閉環；**gated 事件不當成正誤分母**（6H／6I 政策）。 |
| **Progress 路徑仍存在** | 依 6I 報告：Chap2 **`check_answer` 仍呼叫既有 `update_progress(...)`**（Phase 6C 以來）。即 **mastery 狀態已有程式路徑**，但 **尚未** 以 **顯式 `scoring_policy_version`** 與 **dry-run／preview／APR·remediation 統一政策** 於文件與實作對齊。 |
| **APR／remediation 尚未按本 policy 版本銜接** | 本輪將 **v0.1** 定義為「**僅 deterministic 答題事件**可進入政策演算之候選」；**不**在本 planning 輪宣稱已完成端到端 policy rollout。 |

**結論：** 目前已具 **出題→批改→稽核→教師可視**；**尚未**完成「**版本化 v0.1 scoring policy**」之 **正式產品化接入**（含 dry-run／preview 與 APR／fail_streak／remediation 的一致性治理）。

---

## 3. Scoring Policy Versioning

### 3.1 版本識別（v0.1）

本規劃採 **符號化政策 ID**，便於程式與報告對照、與未來 **v0.2+** 並存：

```text
scoring_policy_version = chap2_v0.1_deterministic_only
```

| 欄位（建議未來 implementation 携带） | 說明 |
|--------------------------------------|------|
| `scoring_policy_version` | 固定字串 `chap2_v0.1_deterministic_only`。 |
| `scoring_policy_scope` | `problem_type ∈ Chap2_mainline_11`（下 §4 清單）；**不含** gated、**不含** listing、**不含** 未開放 skill 之出題。 |
| `signal_class` | `deterministic_checked`（僅接受 checker 已判定 `is_correct` boolean 之列）。 |

### 3.2 相容與擴充：v0.2 additive signal（本輪僅定方向、不實作）

| 原則 | 說明 |
|------|------|
| **不重做 v0.1** | v0.1 之 **事件篩選與 skill 維度** 維持有效；新訊號 **附加** 於管線，而非取代。 |
| **新資料通路** | 建議未來 `scoring_policy_version = chap2_v0.2_...` 或 `global_v0.2_handwriting_addon`，以 **獨立 `signal_class`**（例如 `handwriting_ai_judged`、`free_response_rubric`）寫入 **同一套 mastery／APR 抽象** 之 **加總或加權模組**，由 **policy registry** 選擇啟用組合。 |
| **不阻塞 v0.1** | handwriting／free-response **成熟後**再開 v0.2；**Chap2 不需等全章題型** 即可啟用 v0.1。 |

### 3.3 版本變更治理（建議）

- **Changelog**：每次 policy 調整需記 **變更原因、影響 skill、`problem_type` 列表、是否破壞 dry-run 比對**。
- **Rollback**：保留 `scoring_policy_version` 於 log／實驗標記，便於還原與 A/B。

---

## 4. v0.1 in-scope：`problem_type` 與 `skill_id`

**僅**下列 **11** 者屬 `chap2_v0.1_deterministic_only` 之 **scoring 候選**（與 closure／milestone 一致）：

| # | `problem_type` | `skill_id` |
|---|----------------|------------|
| 1 | `classical_probability_fraction` | `vh_數學B4_ProbabilityDefinition` |
| 2 | `complement_probability` | `vh_數學B4_ProbabilityProperties` |
| 3 | `sample_space_count_numeric` | `vh_數學B4_SampleSpaceAndEvents` |
| 4 | `union_intersection_probability` | `vh_數學B4_ProbabilityProperties` |
| 5 | `dice_coin_probability_count` | `vh_數學B4_ProbabilityDefinition` |
| 6 | `conditional_probability_basic` | `vh_數學B4_ConditionalProbability` |
| 7 | `without_replacement_conditional_probability` | `vh_數學B4_ConditionalProbability` |
| 8 | `independent_joint_probability` | `vh_數學B4_IndependentEvents` |
| 9 | `independent_at_least_one_probability` | `vh_數學B4_IndependentEvents` |
| 10 | `expectation_discrete_basic` | `vh_數學B4_MathematicalExpectationDefinition` |
| 11 | `expectation_from_distribution` | `vh_數學B4_MathematicalExpectationDefinition` |

**明確排除（v0.1 不視為 scoring 事件來源）：**

- `record_kind=gated`（`not_enabled_skill`、`reserved_problem_type`）。
- 任何 **未** 列於上表之 `problem_type` 或 **未開放 skill** 請求結果（僅 audit，不進 policy 分母）。

---

## 5. Event → Mastery／fail_streak（v0.1 規劃語意）

### 5.1 觸發條件（候選「一次嘗試」）

建議未來 implementation 定義 **單次 scoring 事件** 須同時滿足：

1. HTTP **`/check_answer` 成功走完 checker**（`is_correct` 為 bool）。
2. `problem_type_id` ∈ §4 清單，且 `skill_id` 與 allowlist 一致。
3. 可選：payload 帶 `scoring_policy_version=chap2_v0.1_deterministic_only`（或由伺服端依日期強制）。

### 5.2 Mastery（Progress）銜接選項（僅規劃）

| 模式 | 說明 | 風險 |
|------|------|------|
| **A. 維持單一路徑** | 繼續僅由 `update_progress` 更新；audit log **對照** 是否一致。 | 需 **對帳** job 或 test 防 drift。 |
| **B. 政策化封裝** | 將「是否更新、如何更新」收斂到 **policy 模組**，內部仍寫 `Progress`。 | implementation 較大，但利於版本化。 |

**Dry-run／preview**：可先採 **B 的影子分支**：同時計算「若套用 v0.1 規則會得到的 delta」，**不寫** `Progress`（見 §7）。

### 5.3 fail_streak

- **建議**：fail_streak 僅在 **§5.1 觸發條件** 且 `is_correct=False` 時遞增；**gated 不遞增**（與 6I 一致）。
- **preview**：輸出「若納入 fail_streak 規則會否觸發閾值」，供教師儀表或內部除錯。

---

## 6. APR 與 Remediation（v0.1 規劃語意）

### 6.1 APR

- **輸入**：僅 **deterministic_checked** 事件串流（可 aggregation 為 skill 或 `skill_id:family_id` 維度，**須**遵守專案 `skill_id:family_id` 身分規則，見 `AGENTS.md`）。
- **原則**：**不**與 visibility audit 的 **gated** 列混合計算「答對率」。
- **Dry-run**：以 replay audit／log 計算 **APR 預覽曲線**，比對現有 `AdaptiveLearningLog`（若啟用）是否一致。

### 6.2 Remediation

- **觸發**：建議 **遲於** v0.1 首發；或僅在 **preview** 模式標記「將觸發 remediation 閾值」。
- **與 6I／6J 邊界**：remediation **不**應由教師 audit 頁面的 **唯讀查詢** 觸發；僅由 **明確 scoring 管線** 觸發。

---

## 7. Dry-run / Preview Policy（建議架構，非實作）

| 元件 | 職責 |
|------|------|
| **Policy evaluator（read-only）** | 輸入：`problem_type_id`、`skill_id`、`is_correct`、timestamp、可選 `student_id`；輸出：建議 `progress_delta`、**不寫 DB**。 |
| **Source of truth for replay** | 優先 **`b4_chap2_visibility_audit_logs` 中 `record_kind=deterministic_answer`**；與 `Progress` diff 時以 **審計為準** 或 **以 Progress 為準** 須 **implementation phase 二選一並文件化**。 |
| **Preview channel** | teacher/admin 或內部 route：**只讀** 預覽「若啟用 v0.1 後 N 步行為」；**不**影響學生下一題。 |
| **Feature flag** | 建議環境變數或設定：`SCORING_POLICY_CHAP2_V01=off|dry_run|live`（**本輪不實作**）。 |

---

## 8. Risks and Dependencies

| 風險 / 依賴 | 緩解（留在 implementation phase） |
|-------------|-------------------------------------|
| **Audit 與 Progress 不一致** | 對帳 script / 單元測試；明定 **單一 write 路徑** 或 **冪等寫入**。 |
| **與 Chap1 PPO／routing 混線** | 僅在 **Chap2 skill 集合** 啟用 v0.1；Chap1 **行為不變**（延續 AGENTS／專案 guardrails）。 |
| **教師誤解 gated 為「错题」** | 儀表與文案區分 **attempt** vs **gated**；延續 6J **visibility-only** 叙事。 |
| **v0.2 訊號湧入時權重爭議** | 提早預留 **signal_class** 與 **加權表** 設定檔，**不重寫** v0.1 判定函式。 |

---

## 9. Recommended Next Phase（不執行）

| 建議 | 說明 | 建議模板 |
|------|------|----------|
| **Phase 6L-impl（或命名 6M）** | 實作 `scoring_policy_version` 携带、dry-run evaluator、可選 `live` 切換；**小步**、可 rollback。 | **Template B**（若含 code）或拆 **Template D** 極小步 |
| **延後 handwriting** | 待獨立 **chap2_v0.2_* 或 global** additive 規格 | **Template A** 先行 |

**本輪不排程、不啟動上表 implementation。**

---

## 10. Final Confirmation

| 項目 | 是/否 |
|------|------|
| 僅新增／更新本 planning report | **是** |
| 未改 production code | **是** |
| 未改 tests | **是** |
| 未改 database | **是** |
| 未改 adaptive scoring / mastery / APR / fail_streak / remediation | **是** |
| 未新增題型 | **是** |
| v0.1 僅涵蓋 11 個 deterministic `problem_type` | **是** |
| 未將 handwriting / free-response 納入 v0.1 | **是** |
| 未啟動 implementation | **是** |

---

*v0.1 planning：Chap2 deterministic scoring policy 版本化與 dry-run／preview 方向；實作與 schema 以未來獨立 phase 為準。*
