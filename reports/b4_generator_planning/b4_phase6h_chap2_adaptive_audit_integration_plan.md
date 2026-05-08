# Phase 6H：Chap2 Adaptive Audit Integration Planning

**類型：** Planning-only（`docs/系統SOP/B4_phase_prompt_templates_v0.1.md` → **Template A**）  
**狀態：** PLANNING_COMPLETE（**不**含 implementation）  
**輸出：** 本文件 `reports/b4_generator_planning/b4_phase6h_chap2_adaptive_audit_integration_plan.md`

---

## 1. Scope and Guardrails

### 1.1 本輪目的

規劃 Chap2 **已完成**之 **11** 個 deterministic `problem_type`（皆 **MANUAL_SMOKE_PASSED**、mainline **CLOSED**）如何進入 **adaptive audit／教師可見性（visibility）** 與**未來** scoring 銜接路徑。**本輪僅文件**，不寫入任何 runtime 或 DB。

### 1.2 必讀／證據來源（均已存在）

| 文件 | 路徑 |
|------|------|
| B4 Phase Prompt Templates | `docs/系統SOP/B4_phase_prompt_templates_v0.1.md` |
| Runtime Smoke Gate SOP（v0.1.2 §8.1 UX） | `docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md` |
| Chap2 deterministic mainline closure | `reports/b4_generator_planning/b4_chap2_deterministic_mainline_closure.md` |
| Phase 6G-0 Skill Availability UX | `reports/b4_generator_planning/b4_phase6g0_chap2_skill_availability_ux_cleanup_summary.md` |

### 1.3 硬性限制（本輪與本報告邊界）

| 項目 | 確認 |
|------|------|
| 修改 production code | ❌ 否 |
| 修改 tests | ❌ 否 |
| 修改 routes / templates | ❌ 否 |
| 修改 generators / validators / `question_router` | ❌ 否 |
| 修改 database | ❌ 否 |
| 修改 coverage matrix | ❌ 否 |
| 新增 allowlist 成員 | ❌ 否 |
| 修改 adaptive scoring / mastery / APR / remediation | ❌ 否 |
| 新增題型 | ❌ 否 |
| 啟動 implementation | ❌ 否 |

**唯一允許新增：** 本 planning report。

---

## 2. Completed Chap2 deterministic problem_type inventory

下列 **11** 個題型屬 **Chap2 deterministic mainline**，skill／checker／answer 契約見 closure 報告 §1、§3。

| # | problem_type | skill_id | answer_type | checker（摘要） |
|---|--------------|----------|-------------|-----------------|
| 1 | `classical_probability_fraction` | `vh_數學B4_ProbabilityDefinition` | `rational_fraction` | `check_rational_answer` flexible |
| 2 | `complement_probability` | `vh_數學B4_ProbabilityProperties` | `rational_fraction` | `check_rational_answer` flexible |
| 3 | `sample_space_count_numeric` | `vh_數學B4_SampleSpaceAndEvents` | `integer` | `check_integer_answer` strict |
| 4 | `union_intersection_probability` | `vh_數學B4_ProbabilityProperties` | `rational_fraction` | `check_rational_answer` flexible |
| 5 | `dice_coin_probability_count` | `vh_數學B4_ProbabilityDefinition` | `rational_fraction` | `check_rational_answer` flexible |
| 6 | `conditional_probability_basic` | `vh_數學B4_ConditionalProbability` | `rational_fraction` | `check_rational_answer` flexible |
| 7 | `without_replacement_conditional_probability` | `vh_數學B4_ConditionalProbability` | `rational_fraction` | `check_rational_answer` flexible |
| 8 | `independent_joint_probability` | `vh_數學B4_IndependentEvents` | `rational_fraction` | `check_rational_answer` flexible |
| 9 | `independent_at_least_one_probability` | `vh_數學B4_IndependentEvents` | `rational_fraction` | `check_rational_answer` flexible |
| 10 | `expectation_discrete_basic` | `vh_數學B4_MathematicalExpectationDefinition` | `expected_value` | `check_expected_value_answer` |
| 11 | `expectation_from_distribution` | `vh_數學B4_MathematicalExpectationDefinition` | `expected_value` | `check_expected_value_answer` |

**對照：尚未納入 mainline、本階段 audit 不應當成「缺題」者**（見 §7）：`vh_數學B4_BasicConceptsOfSets`、`vh_數學B4_ProbabilityOperations`、`vh_數學B4_ApplicationsOfExpectation`、`vh_數學B4_MathematicalExpectation`，以及 reserved listing：`sample_space_listing`、`event_set_listing`、`subset_listing`。

---

## 3. Proposed audit log fields

以下欄位建議作為 **Phase 6I**（visibility log）最小實作時之**語意合約**；實際儲存可為 DB 表、append-only 檔、或現有 log 管線之結構化 payload。**本輪不定 schema 遷移**。

| 欄位 | 說明 |
|------|------|
| `student_id` | 答題學生識別（與現有 `User`／session 一致之 ID） |
| `session_id` | 練習連線／瀏覽工作階段（與 Flask session 或前端 trace id 對齊；便於串同一輪多題） |
| `skill_id` | 完整 `vh_數學B4_*`，與 allowlist／router 一致 |
| `problem_type_id` | 上表 11 者之一；reserved／not-enabled 之 gate 事件可另列 `event_type=gated`（見 §4） |
| `generator_key` | generator／路由器可重現來源（與 payload `generator_key` 對齊，若無則 null） |
| `answer_type` | `rational_fraction` / `integer` / `expected_value` 等 |
| `expected_answer` | 標準答案（或 hash／truncated；**實作 phase 需定 PII／安全與長度政策**） |
| `user_answer` | 學生提交原文 |
| `is_correct` | boolean；若 checker 未執行（例如 gated）可為 null |
| `checker_name` | 例如 `check_rational_answer`、`check_integer_answer`、`check_expected_value_answer` 或 `none_gated` |
| `difficulty` | 與 payload／`level` 一致 |
| `diagnosis_tags` | 與 generator payload 之 tags 對齊（JSON 或字串陣列） |
| `timestamp` | UTC 或可追蹤之 server time |
| `source_phase` | 建議常數，例如 `b4_chap2_determin` + optional batch 標籤，**避免**使用過期對外 phase 字串（對齊 SOP §8.1） |

**可選延伸（非本輪強制）：** `request_id`、`route_path`（如 `/check_answer`）、`gen_seed`、`problem_type_rotation_index`，供教師除錯與重現。

---

## 4. Visibility-only policy

**Phase 6H／建議之首個 implementation 子階段（Phase 6I）共同前提：**

| 政策 | 說明 |
|------|------|
| **只進 audit／teacher visibility** | 日誌或儀表可讀、可查、可匯出；不視為正式「成績單」或唯一學習指標 |
| **不更新 mastery** | `Progress`／技能熟練度不因本管道寫入而變動 |
| **不更新 APR** | 診斷／適性報告指標不因本管道寫入而變動 |
| **不更新 fail_streak** | 連錯懲罰或 streak 計數不改寫 |
| **不觸發 remediation** | 不因 log 自動觸發 RAG／補救路徑 |
| **Gated 事件可記錄** | `not-yet-enabled` skill（見 `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS`）與 reserved listing 之 **422** 可記 `event_type=skill_not_enabled`／`problem_type_reserved`，**不**計入正誤統計，避免誤判「缺題」或「全錯」 |

與 **`reports/b4_generator_planning/b4_phase6g0_chap2_skill_availability_ux_cleanup_summary.md`** 一致：對外錯誤為中性文案；audit 內部可使用結構化 `reason_code`，但**不**應把內部 phase 標籤曝露給學生端。

---

## 5. Future scoring policy proposal

本節為**政策建議**，實作需另開 phase 並通過產品／教學核准。

### 5.1 未來可優先納入 mastery／類 scoring 之題型（仍須保守上線）

- **機率 rational 線（8 題）：**  
  `classical_probability_fraction`、`complement_probability`、`union_intersection_probability`、`dice_coin_probability_count`、`conditional_probability_basic`、`without_replacement_conditional_probability`、`independent_joint_probability`、`independent_at_least_one_probability`  
  **理由：** checker 契約成熟、答案在 \([0,1]\) 語意清楚；需注意「對答案≠理解題意」之教學判讀（見 §7）。

- **整數計數（1 題）：**  
  `sample_space_count_numeric`  
  **理由：** `check_integer_answer` strict，誤判型別較少；報表需區分「格式錯」與「概念錯」。

### 5.2 建議保守處理／額外監控

- **`expectation_discrete_basic`、`expectation_from_distribution`**  
  **理由：** 已做 **Phase 6F-R** 課本語境對齊，但期望值可為負、可大於 1，且敘事變體多；納入 mastery 前應維持 **textbook alignment** 抽樣與教師 spot-check，並監控 `check_expected_value_answer`（拒絕 `%`）與學生輸入習慣是否扭屈。

### 5.3 仍不可進 deterministic scoring／併入上述 eleven 之 mastery 池

- **Handwriting / free-response reserved：** `sample_space_listing`、`event_set_listing`、`subset_listing`（及 SOP 所列相關類型）— **不**以本 eleven 之 auto-checker 計分；若未來 scoring，須走 **AI-judged／teacher review** 專屬流程（與 Chap1 TreeDiagram／Pascal 路線一致）。

- **Not-yet-enabled skills 之下題型**（未在 mainline 11 內）：不應因「未出現」而扣減 eleven 之覆蓋率。

---

## 6. Teacher dashboard / audit view 建議

| 建議區塊 | 內容 |
|----------|------|
| **篩選** | `skill_id`、`problem_type_id`、日期區間、`is_correct`、可選 `checker_name` |
| **清單欄** | 時間、`student_id`（或匿名化顯示）、`skill_id`、`problem_type_id`、`is_correct`、簡要 `diagnosis_tags` |
| **詳情** | `question_text`（若儲存策略允許）、`user_answer` vs `expected_answer`、generator／seed 資訊（重現用） |
| **分母語意** | 區分 **實際作答** vs **gated 事件**（未開放 skill／reserved）：後者不列入正確率分母 |
| **匯出** | CSV／JSON 供教務備份；欄位對齊 §3 |
| **權限** | 僅教師／管理員；與學生可見介面分離 |

實作時宜與既有 adaptive audit 旗標（若已有 `adaptive_audit=1` 類行為）**命名與語意對齊**，避免重複儀表。

---

## 7. Risks

| 風險 | 說明 |
|------|------|
| **Checker 正確 ≠ 學生理解** | 機率／期望值僅能驗證等值答案；誤用公式仍可能「猜對」。Audit 應支援教師抽樣，不宜單一依 auto 正誤核定診斷。 |
| **期望值題 textbook alignment** | `expectation_discrete_basic`、`expectation_from_distribution` 須持續對齊高職 B4 2-3 語境；生成器變更時 audit 應能對應 `generator_key`／版本。 |
| **Not-enabled skill 不應誤算成缺題** | 學生若誤入 `vh_數學B4_ProbabilityOperations` 等收到 422，日誌應標為 **gate**，不併入「未作答」或「章節覆蓋缺口」。 |
| **Visibility log ≠ adaptive scoring** | 儀表數據若被誤讀為 APR／mastery，將扭曲教學決策；UI 與文件須標 **visibility-only**（對齊 §4）。 |
| **隱私與儲存** | `user_answer`、`question_text` 可能含個資或習慣；實作 phase 需 retention／權限／匿名化政策。 |

---

## 8. Recommended next phase

### Phase 6I：Adaptive Audit Logging Minimal Implementation

| 項目 | 說明 |
|------|------|
| **範圍** | 僅**寫入** §3 定義之 **visibility／audit log**（或最小子集），並可選擇性暴露唯讀 API／簡報頁給教師 |
| **不包含** | 不修改 `update_progress` 行為以寫入 mastery；不改 APR／`fail_streak`／remediation 觸發條件 |
| **DB** | 若需新表，應在 **6I implementation** 內獨立設計 migration 與 rollback；**本 Phase 6H 不預先改 schema** |
| **測試** | 以 route／service 單元或整合測試驗證「有作答則 log、gate 事件分類正確、不呼叫 mastery 更新」 |
| **狀態目標** | `READY_FOR_MANUAL_SMOKE` → 教師／營運 manual 驗收 visibility |

---

## 9. Final confirmation

| 項目 | 確認 |
|------|------|
| 是否只新增 planning report | **是**（本檔） |
| 是否修改 production code | **否** |
| 是否修改 database | **否** |
| 是否修改 adaptive scoring / mastery / APR / remediation | **否** |
| 是否啟動 implementation | **否** |

---

*Phase 6H Planning 完成。下一實作步驟建議：**Phase 6I — Adaptive Audit Logging Minimal Implementation**（僅 visibility log，不接 mastery）。*
