# B4 Chapter 2 Deterministic Mainline Closure

**狀態：CLOSED（deterministic mainline）**
**最終 runtime status：MANUAL_SMOKE_PASSED（11 個 problem_type 全數通過）**

---

## 0. Scope and Guardrails

本輪僅為 **closure report**，不做任何 implementation。

| 項目 | 確認 |
|---|---|
| 是否新增任何題型 | ❌ 否 |
| 是否修改 production code | ❌ 否 |
| 是否修改 tests | ❌ 否 |
| 是否修改 routes | ❌ 否 |
| 是否修改 templates | ❌ 否 |
| 是否修改 generators | ❌ 否 |
| 是否修改 validators | ❌ 否 |
| 是否修改 question_router | ❌ 否 |
| 是否修改 allowlist | ❌ 否 |
| 是否修改 database | ❌ 否 |
| 是否修改 coverage matrix | ❌ 否 |
| 是否修改 adaptive scoring / mastery / APR / remediation | ❌ 否 |
| 是否處理 handwriting / free-response 題型 | ❌ 否 |
| 是否處理 BasicConceptsOfSets | ❌ 否 |
| 是否處理 ApplicationsOfExpectation | ❌ 否 |
| 是否處理 MathematicalExpectation 自評題 | ❌ 否 |
| 是否啟動下一 phase | ❌ 否 |

唯一新增檔案：
- `reports/b4_generator_planning/b4_chap2_deterministic_mainline_closure.md`（本報告）

---

## 1. Completed Deterministic Mainline

### 1.1 已完成 11 個 problem_type

| phase | problem_type | skill_id | answer_type | checker | runtime status |
|---|---|---|---|---|---|
| 6C | `classical_probability_fraction` | `vh_數學B4_ProbabilityDefinition` | `rational_fraction` | `check_rational_answer` flexible | **MANUAL_SMOKE_PASSED** |
| 6C | `complement_probability` | `vh_數學B4_ProbabilityProperties` | `rational_fraction` | `check_rational_answer` flexible | **MANUAL_SMOKE_PASSED** |
| 6C | `sample_space_count_numeric` | `vh_數學B4_SampleSpaceAndEvents` | `integer` | `check_integer_answer` strict | **MANUAL_SMOKE_PASSED** |
| 6C | `union_intersection_probability` | `vh_數學B4_ProbabilityProperties` | `rational_fraction` | `check_rational_answer` flexible | **MANUAL_SMOKE_PASSED** |
| 6C | `dice_coin_probability_count` | `vh_數學B4_ProbabilityDefinition` | `rational_fraction` | `check_rational_answer` flexible | **MANUAL_SMOKE_PASSED** |
| 6D | `conditional_probability_basic` | `vh_數學B4_ConditionalProbability` | `rational_fraction` | `check_rational_answer` flexible | **MANUAL_SMOKE_PASSED** |
| 6D | `without_replacement_conditional_probability` | `vh_數學B4_ConditionalProbability` | `rational_fraction` | `check_rational_answer` flexible | **MANUAL_SMOKE_PASSED** |
| 6E | `independent_joint_probability` | `vh_數學B4_IndependentEvents` | `rational_fraction` | `check_rational_answer` flexible | **MANUAL_SMOKE_PASSED** |
| 6E | `independent_at_least_one_probability` | `vh_數學B4_IndependentEvents` | `rational_fraction` | `check_rational_answer` flexible | **MANUAL_SMOKE_PASSED** |
| 6F / 6F-R | `expectation_discrete_basic` | `vh_數學B4_MathematicalExpectationDefinition` | `expected_value` | `check_expected_value_answer` | **MANUAL_SMOKE_PASSED** |
| 6F / 6F-R | `expectation_from_distribution` | `vh_數學B4_MathematicalExpectationDefinition` | `expected_value` | `check_expected_value_answer` | **MANUAL_SMOKE_PASSED** |

### 1.2 章節分佈

| 課本節次 | 涵蓋 skill_id | 已 deterministic 題型數 |
|---|---|---|
| 2-1 樣本空間與事件 | `vh_數學B4_SampleSpaceAndEvents` | 1（`sample_space_count_numeric`） |
| 2-2 機率的運算 | `vh_數學B4_ProbabilityDefinition`、`vh_數學B4_ProbabilityProperties`、`vh_數學B4_ConditionalProbability`、`vh_數學B4_IndependentEvents` | 8 |
| 2-3 數學期望值 | `vh_數學B4_MathematicalExpectationDefinition` | 2 |
| **總計** | **6 個 skill_id** | **11 個 problem_type** |

未被 mainline 涵蓋的 Chap2 skill_id（仍 reserved，見 §5）：
- `vh_數學B4_BasicConceptsOfSets`
- `vh_數學B4_ProbabilityOperations`
- `vh_數學B4_ApplicationsOfExpectation`
- `vh_數學B4_MathematicalExpectation`（自評題集中）

---

## 2. Runtime Smoke Gate Summary

### 2.1 Phase-by-Phase Smoke Gate 結果

| smoke gate item | Phase 6C | Phase 6D | Phase 6E | Phase 6F | Phase 6F-R |
|---|---|---|---|---|---|
| `/practice` entry（decoded skill） | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/practice` entry（encoded skill） | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/get_next_question`（decoded） | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/get_next_question`（encoded） | ✅ | ✅ | ✅ | ✅ | ✅ |
| `/check_answer`（canonical / equivalent） | ✅ | ✅ | ✅ | ✅ | ✅ |
| URL encoded skill_id decode | ✅ | ✅ | ✅ | ✅ | ✅ |
| decoded skill_id passthrough | ✅ | ✅ | ✅ | ✅ | ✅ |
| frontend double-encoding guard（v0.1.1） | ✅（6C-2R 修正並引入） | ✅ | ✅ | ✅ | ✅ |
| unsupported skill clear error（無 legacy fallback） | ✅ | ✅ | ✅ | ✅ | ✅ |
| no `import skills.<skill_id>` legacy fallback | ✅ | ✅ | ✅ | ✅ | ✅ |
| handwriting reserved blocked | ✅ | ✅ | ✅ | ✅ | ✅ |
| Chap1 regression（Chap1 allowlist size 仍 13） | ✅ | ✅ | ✅ | ✅ | ✅ |
| cross-phase regression（前一批仍可運作） | n/a | ✅（6C） | ✅（6C/6D） | ✅（6C/6D/6E） | ✅（6C/6D/6E/6F） |

### 2.2 SOP Compliance 聲明

> Phase 6C 之後所有 deterministic batch 都遵守 **Runtime Smoke Gate SOP v0.1.1**
> （`docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md`，含 6.1 frontend double-encoding guard）。

具體達成：
- 所有 deterministic phase 提交 phase summary 時，狀態流轉為 `GENERATOR_READY` → `RUNTIME_READY` → `READY_FOR_MANUAL_SMOKE` → `MANUAL_SMOKE_PASSED`，未跳過任一 gate。
- 每一 phase 都通過 `/practice`、`/get_next_question`、`/check_answer` 三條 route，並完成 encoded/decoded skill_id 雙路徑覆蓋。
- 每一 phase 對 unsupported skill 與 handwriting reserved problem_type 都驗證 hard-blocked、無 legacy module fallback。
- 自 Phase 6C-2R 起，前端 `templates/index.html` 的 `getSkillId()` 已加 `decodeURIComponent()` 防護，後續所有 phase 沿用，未再回退此防護。

---

## 3. Checker Coverage Summary

目前 Chap2 deterministic mainline 共三條 checker 線：

### 3.1 `check_rational_answer`（flexible mode）

- **使用題型（共 8 個 problem_type）：**
  - 6C：`classical_probability_fraction`、`complement_probability`、`union_intersection_probability`、`dice_coin_probability_count`
  - 6D：`conditional_probability_basic`、`without_replacement_conditional_probability`
  - 6E：`independent_joint_probability`、`independent_at_least_one_probability`
- **接受形式：**
  - canonical 最簡分數（`1/2`）
  - 未化簡等值分數（`2/4`）
  - 有限小數（`0.5`）
  - 百分比（`50%`）
  - LaTeX 分數（既有 parse 支援）
- **拒絕形式：**
  - 不等值分數（如答案是 `1/2` 卻填 `3/4`）
  - 分母為 0（`1/0`）
  - 超出機率範圍（`5/4`）

### 3.2 `check_integer_answer`（strict mode）

- **使用題型（共 1 個 problem_type）：**
  - 6C：`sample_space_count_numeric`
- **接受形式：**
  - 整數字串（`36`）
  - 前後空白裁切（` 36 `）
  - 全形數字（`３６`，若支援）
- **拒絕形式：**
  - 帶小數點（`36.0` ❌）
  - 帶百分比（`36%` ❌）
  - 帶單位或符號
  - 負整數（除非明確允許）

### 3.3 `check_expected_value_answer`

- **使用題型（共 2 個 problem_type）：**
  - 6F / 6F-R：`expectation_discrete_basic`、`expectation_from_distribution`
- **實作策略：** 內部委派 `check_rational_answer`，但設定：
  - `allow_decimal=True`（接受有限小數）
  - `allow_percentage=False`（**拒絕** 百分比，期望值不應以 `%` 表示）
  - `validate_probability_range=False`（**不限制** `[0, 1]`，期望值可大於 1，未來亦可為負）
- **接受形式：**
  - canonical 最簡分數（`5/2`）
  - 未化簡等值分數（`10/4`）
  - 等值有限小數（`2.5`）
- **拒絕形式：**
  - 百分比輸入（`250%` ❌）
  - 不等值表達式

### 3.4 Checker 邊界一致性

- 機率類題型 → `check_rational_answer`（容許 `%`、限制 `[0, 1]`）
- 純計數題型 → `check_integer_answer`（嚴格整數）
- 期望值題型 → `check_expected_value_answer`（不限 `[0, 1]`、拒 `%`）

三條 checker 各自職責清楚，未交叉污染。

---

## 4. Textbook Alignment Summary

### 4.1 Phase 6F 原始問題（manual smoke 反饋）

Phase 6F 初版生成的「數學期望值」題型：
- 雖然數學上正確、checker 行為正確、route 行為正確
- 但題幹語境偏「抽象離散隨機變數分布」，例如使用 `W`、隨機分割式語句主導
- 不像高職 B4 課本 2-3「數學期望值」常見的例題敘事
- manual smoke 觀感上不貼近課本口吻

### 4.2 Phase 6F-R 修正後語境

Phase 6F-R 僅修正 **既有兩個 problem_type 的題幹語境**，未新增題型、未變動 checker 行為：

| problem_type | 修正後語境 |
|---|---|
| `expectation_discrete_basic` | 課本風格情境：硬幣得失、骰子得失、兩次硬幣得失；題幹用「玩一次所得到金額」「所得金額的期望值」等課本語句；允許正負報酬（付出記負值） |
| `expectation_from_distribution` | 改為「已整理好的 X / P(X) 表格」題幹；表格欄位明確標 `X` 與 `P(X)`；題幹保留課本練習風格 |

兩題 explanation 統一格式：
1. 先列 `E(X)=Σ x·P(X=x)`
2. 再逐項代入
3. 最後化簡得到答案

### 4.3 課本對照證據

DB 中（`textbook_examples`，`skill_id=vh_數學B4_MathematicalExpectationDefinition`，`source_section=2-3 數學期望值`）代表題型語境：
1. 擲骰子一次：1 點得 12 元、2/3/4 點付 20 元、5/6 點得 60 元
2. 袋中 10 元與 5 元硬幣若干枚
3. 擲均勻硬幣一次：正面得 20 元、反面付 10 元
4. 擲公正骰子一次：奇數點得 100 元、偶數點付 50 元
5. 擲均勻硬幣 2 次：2 正面得 400 元、1 正 1 反得 100 元、2 反面付 500 元

修正後生成器之題幹語境與上述課本例題一致。

### 4.4 Phase 6F-R 狀態

> **Phase 6F-R manual smoke passed。**
> 期望值題型（`expectation_discrete_basic`、`expectation_from_distribution`）語境已對齊高職 B4 課本，正負報酬皆可處理，`E(X)=ΣxP(X=x)` 為展開核心。

---

## 5. Still Excluded / Reserved

### 5.1 deterministic but not yet implemented（保留未做）

| problem_type | 對應 skill_id | 排除原因 / 風險 |
|---|---|---|
| `set_operation_count` | `vh_數學B4_BasicConceptsOfSets` | `BasicConceptsOfSets` 仍在 not-enabled 集合，allowlist 邊界與容斥計數策略需先確認 |
| `inclusion_exclusion_count` | `vh_數學B4_BasicConceptsOfSets` | 同上，可與 `set_operation_count` 共用 generator |
| `expectation_word_problem_profit_fairness` | `vh_數學B4_ApplicationsOfExpectation` | 文字情境長、解析風險高，需 textbook evidence 先做語境凍結 |
| `probability_algebra_mixed` | `vh_數學B4_ProbabilityOperations` | DB 對應 self_assessment 9 筆全 `needs_review`，未經人工確認 |
| `expectation_assessment_numeric` | `vh_數學B4_MathematicalExpectation` | DB 對應 self_assessment 5 筆全 `needs_review`，未經人工確認 |
| `event_operation_probability` | `vh_數學B4_ProbabilityOperations` | 同 `probability_algebra_mixed`，需先處理 needs_review 品質 |

對應的「未開放 skill」目前仍在 `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS`：
- `vh_數學B4_BasicConceptsOfSets`
- `vh_數學B4_ProbabilityOperations`
- `vh_數學B4_ApplicationsOfExpectation`
- `vh_數學B4_MathematicalExpectation`（自評題集中）

### 5.2 handwriting / free-response reserved（不得進 deterministic）

以下題型 **不得加入 deterministic allowlist**，**不更新** mastery / APR / fail_streak / remediation；僅可作 `visibility-only` / `deferred_teacher_review`：

| problem_type | 對應 skill_id | 政策 |
|---|---|---|
| `sample_space_listing` | `vh_數學B4_SampleSpaceAndEvents` | hard-excluded；答案為集合列舉，非單一整數 |
| `event_set_listing` | `vh_數學B4_SampleSpaceAndEvents`、`vh_數學B4_BasicConceptsOfSets` | hard-excluded；事件子集合表示 |
| `subset_listing` | `vh_數學B4_BasicConceptsOfSets` | hard-excluded；子集合之集合 |
| `tree_diagram_listing`（如相關） | （Chap1 已有 handwriting 流程；Chap2 若涉及，沿用同政策） | hard-excluded for deterministic |

### 5.3 政策聲明（重申）

> 上述 reserved 題型 **不得加入 deterministic allowlist**，**不更新 mastery / APR / fail_streak / remediation**。
> 若未來要進入 AI-judged handwriting 流程，須另開 phase 並參照 TreeDiagram / Pascal handwriting SOP，本輪不進行。

---

## 6. Adaptive / Scoring Status

### 6.1 目前狀態（明確）

- **本階段尚未** 把 Chap2 deterministic 答題結果接入 adaptive scoring / mastery / APR / remediation。
- **目前僅完成** runtime-ready deterministic generation（generator + checker + router + allowlist + route + smoke）。
- 11 個 problem_type 雖已 manual smoke passed，但其答對/答錯事件尚未進入 adaptive 路徑。

### 6.2 未來若要接 adaptive scoring

需另開 phase，並至少確認：
1. **logging policy**：Chap2 deterministic 答題事件的儲存欄位、time-series schema
2. **mastery update rule**：哪些 problem_type 對哪個 skill_id 的 mastery 有貢獻
3. **fail_streak policy**：連錯多少次觸發 remediation hint
4. **APR contribution**：deterministic 結果在 APR 計算中的權重
5. **Chap1 既有 adaptive 行為不被破壞**（regression）

### 6.3 建議

> deterministic mainline 已可用，下一步應進入 **學習導航與資料收集** 規劃，而非無止境擴題型。
> 詳見 §8。

---

## 7. Known Limitations

| # | 限制 | 說明 |
|---|---|---|
| L1 | DB `textbook_examples` 仍有 `needs_review` 品質問題 | Chap2 87 題全部 `needs_review=true`；本輪 generator 採獨立參數化生成，未直接依賴 DB 題目，但 DB 清理仍是另一條獨立工作 |
| L2 | image-related 題仍排除 | `ProbabilityDefinition` 有 2 筆 image-related 題，目前 generator 不生成此類；未來另處理 |
| L3 | handwriting listing 題型尚未處理 | `sample_space_listing` / `event_set_listing` / `subset_listing` 仍 hard-excluded，需另開 AI-judged phase |
| L4 | `BasicConceptsOfSets` 尚未開放 | 集合計數類（`set_operation_count`、`inclusion_exclusion_count`）需先決定 allowlist 邊界 |
| L5 | `ApplicationsOfExpectation` 尚未開放 | 期望值應用題（`expectation_word_problem_profit_fairness`）情境長，需先 textbook evidence 凍結 |
| L6 | `MathematicalExpectation` 自評題尚未開放 | 5 筆全 `needs_review`，須先人工品質確認 |
| L7 | adaptive scoring integration 尚未完成 | 11 個 deterministic 題型尚未接入 mastery / APR / fail_streak / remediation |
| L8 | route smoke 仍依賴既有測試與人工 smoke | 未另建 full HTTP shared fixture，目前依 phase-level pytest + manual smoke checklist 兩條軌道 |
| L9 | `validate_b4_chap2_phase6c1_generator_payload` 命名沿用歷史 | 函式名仍含 `phase6c1`，但語意已涵蓋至 6F；命名重整不在本輪 closure 範圍 |
| L10 | route error 訊息字串仍含 `Phase 6C-1` 字樣 | 行為正確但文案未調整；屬於後續 cleanup，不影響 mainline |

---

## 8. Recommended Next Phase Options

> 本節僅列出選項，**不執行**、**不啟動**、**不變動任何 production code / tests / allowlist / DB**。

### Option A — Phase 6G：Applications of Expectation Minimal Batch

| 項目 | 內容 |
|---|---|
| scope | `expectation_word_problem_profit_fairness`（限課本風格簡單得失應用） |
| skill_id | `vh_數學B4_ApplicationsOfExpectation` |
| 風險 | **高**。文字情境長、語境變異大，需 textbook evidence freeze 後再生成 |
| 前置 | 需先做 textbook evidence 證據凍結（類似 Phase 6F-R 課本對齊流程） |
| 收益 | 完成 2-3 課本主線最後一塊應用題 |

### Option B — Phase 6C-3：Basic Set Count Batch

| 項目 | 內容 |
|---|---|
| scope | `set_operation_count`、`inclusion_exclusion_count` |
| skill_id | `vh_數學B4_BasicConceptsOfSets` |
| 風險 | **中**。需先解開 `BasicConceptsOfSets` 的 not-enabled 限制與 allowlist 邊界策略 |
| 前置 | 需先處理 `BasicConceptsOfSets` 的 allowlist + handwriting reserved（`subset_listing`）的隔離策略 |
| 收益 | 補齊 2-1 樣本空間/集合的計數型 deterministic 覆蓋 |

### Option C — Chap2 Adaptive Audit Integration

| 項目 | 內容 |
|---|---|
| scope | 將已完成 11 個 deterministic problem_type 加入 adaptive audit / visibility |
| 動作 | logging exposure、audit trace、不一定立刻更新 mastery |
| 風險 | **低-中**。不影響 generator、不破壞既有 Chap1 adaptive 行為 |
| 前置 | 需先設計 Chap2 deterministic 與既有 Chap1 adaptive logging 的相容路徑 |
| 收益 | 開始累積 Chap2 真實答題資料，為後續 mastery / remediation 整合打底 |

### 建議優先順序

1. **先做 Option C（Chap2 Adaptive Audit Integration）或 closure-to-adaptive 的規劃 phase**
   - deterministic mainline 已可用且穩定
   - 下一步價值最高的不是擴題型，而是進入「學習導航與資料收集」
   - 即使僅做 logging exposure，也能讓系統開始累積真實使用資料
2. **再做 Option A（應用題）或 Option B（BasicConceptsOfSets）**
   - 兩者皆屬「擴題型」，可在 adaptive 路徑明確後再選擇
   - 若強排，Option B 風險較低（純計數，無語境變異），Option A 需更多課本 evidence

### 建議理由

> deterministic mainline 已可用，下一步應思考如何進入 **學習導航與資料收集**，而不是無止境擴題型。
> 11 個 problem_type 已涵蓋 2-1 / 2-2 / 2-3 三節主要 deterministic 題型，足以支撐基本練習；
> 若沒有 adaptive 整合，再多題型也只是孤立的 generator。

---

## 9. Final Confirmation

| 項目 | 確認 |
|---|---|
| 是否只新增 / 更新 closure report | **是** |
| 是否修改 production code | **否** |
| 是否修改 tests | **否** |
| 是否修改 routes | **否** |
| 是否修改 templates | **否** |
| 是否修改 generators | **否** |
| 是否修改 validators | **否** |
| 是否修改 database | **否** |
| 是否修改 coverage matrix | **否** |
| 是否新增 allowlist | **否** |
| 是否加入 handwriting / free-response 題型 | **否** |
| 是否修改 adaptive scoring / mastery / APR / remediation | **否** |
| 是否啟動下一 phase | **否** |

---

## 10. 必讀文件對照（本輪 closure 引用來源）

| 文件 | 路徑 | 是否存在 |
|---|---|---|
| Runtime Smoke Gate SOP v0.1（含 v0.1.1 frontend double-encoding guard） | `docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md` | ✅ |
| Phase 6C P0 Deterministic Closure | `reports/b4_generator_planning/b4_phase6c_postcheck_chap2_p0_deterministic_closure.md` | ✅ |
| Phase 6D Conditional Probability Runtime-Ready Summary | `reports/b4_generator_planning/b4_phase6d_conditional_probability_runtime_ready_summary.md` | ✅ |
| Phase 6E Independent Events Runtime-Ready Summary | `reports/b4_generator_planning/b4_phase6e_independent_events_runtime_ready_summary.md` | ✅ |
| Phase 6F Expected Value Runtime-Ready Summary | `reports/b4_generator_planning/b4_phase6f_expected_value_runtime_ready_summary.md` | ✅ |
| Phase 6F-R Expected Value Textbook Alignment Repair Summary | `reports/b4_generator_planning/b4_phase6f_expected_value_textbook_alignment_repair_summary.md` | ✅ |
| Phase 6A Chap2 Problem Type Taxonomy Freeze | `reports/b4_generator_planning/b4_phase6a_chap2_problem_type_taxonomy.md` | ✅ |
| Phase 6B Probability Validator Plan | `reports/b4_generator_planning/b4_phase6b_probability_validator_plan.md` | ✅ |

> 全部必讀文件皆存在；本 closure report 引用其結論時不擴大搜尋、不修改任何 code。

---

*B4 Chapter 2 Deterministic Mainline Closure 完成。*
*狀態：**CLOSED**（11 個 problem_type 全數 MANUAL_SMOKE_PASSED；Phase 6F-R 課本對齊已通過）。*
*下一 phase 由人工選擇 Option A / B / C 後另開規劃；本輪不啟動任何下一 phase。*
