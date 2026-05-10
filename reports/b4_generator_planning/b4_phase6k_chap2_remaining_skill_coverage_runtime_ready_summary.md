# B4 Phase 6K — Chap2 Remaining Deterministic Skill Coverage Runtime-ready Summary

Status: **READY_FOR_MANUAL_SMOKE**
Template applied: B4 Phase Prompt Templates v0.1 — Template B (Runtime-ready Deterministic Batch)

## 1. Scope and guardrails

### 1.1 Scope
補齊 Chap2 尚未開放的四個主要 skill，使第二章每個主要單元都有至少一批
deterministic runtime-ready 題型。本輪只新增 6 個 deterministic problem types
與 4 個 skill 的 router/allowlist 開放，並新增 generator/checker 對應與整合測試。

### 1.2 Guardrails strictly enforced
| 項目 | 狀態 |
| --- | --- |
| 不修改 adaptive scoring / mastery / APR / fail_streak / remediation | OK — 未動 |
| 不新增 handwriting / free-response scoring | OK — 全部 deterministic answer types |
| 不把 sample_space_listing / event_set_listing / subset_listing / tree_diagram_listing 加入 deterministic allowlist | OK — 仍維持 hard-excluded |
| 不修改 coverage matrix | OK — 未動 |
| 不大改 routes | OK — `practice.py` 完全未修改 |
| 不重構 templates | OK — 未動 |
| 不啟動下一章 / Phase 7A / scoring implementation | OK — 完成後立即停下 |
| 不做全專案重構 | OK — 範圍限縮在 Chap2 generator + allowlist + tests |

## 2. Textbook evidence summary

### 2.1 vh_數學B4_ApplicationsOfExpectation
透過 `scripts/_phase6k_evidence_check.py` 對 `textbook_examples` 表查詢
`source_chapter = 2 機率`，`source_section = 2-3 數學期望值` 範圍下與
`vh_數學B4_ApplicationsOfExpectation` 對應之題目。
Evidence 結果：

- 課本與隨堂練習中，「抽彩券／抽獎得失金額期望值」屬於課本主流情境，
  `source_description` 含 `textbook_example` / `in_class_practice` 風格。
- 採用乾淨整數元獎額、總張數為分母的最簡情境，避開保險精算、投資報酬等
  超出課綱題型。

結論：**evidence 充足**，採用 `lottery_payoff` 系列模板（5 個 context）作為
Phase 6K `expectation_word_problem_profit_fairness` 的唯一允許情境。

### 2.2 vh_數學B4_MathematicalExpectation
查詢 `textbook_examples` 結果顯示此 skill 多為「自評綜合題」與「整理過後的
得分／獎額分布」題。`needs_review` 比例偏高的情境（求未知 x 使期望值為 0、
複雜抽球組合）刻意排除。

結論：**evidence 充足**，採用以「卡片抽獎」與「圓盤抽獎」為情境的 5 個簡單
分布模板，作為 Phase 6K `expectation_assessment_numeric` 的允許情境，
與 6F 的 `expectation_discrete_basic`（硬幣／骰子）和
`expectation_from_distribution`（markdown 表格）情境刻意區隔，避免重疊。

註：DB 查詢腳本與輸出檔在 evidence check 完成後即刪除，不留下臨時檔案。

## 3. Files changed

### 3.1 New generator modules
- `core/vocational_math_b4/generators/chap2_probability_operations.py`
  — `event_operation_probability`, `probability_algebra_mixed`
- `core/vocational_math_b4/generators/chap2_basic_sets.py`
  — `set_operation_count`, `inclusion_exclusion_count`
- `core/vocational_math_b4/generators/chap2_expectation_extensions.py`
  — `expectation_word_problem_profit_fairness`, `expectation_assessment_numeric`

### 3.2 Router / allowlist updates (minimal)
- `core/vocational_math_b4/services/question_router.py`
  — 新增三個 generator module import 與四個 skill 的 `_CHAP2_PHASE6C1_REGISTRY` 條目
  — `generate_for_chap2_skill` docstring 同步補上 Phase 6K 內容
- `core/vocational_math_b4/adaptive/b4_chapter2_phase6c1_allowlist.py`
  — `B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST`：6 → 10 skills
  — `B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES`：11 → 17 types
  — `B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES`：補上 `tree_diagram_listing`
  — `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS`：4 → 0（Chap2 已無 gated runtime skill）
  — `B4_CHAPTER_2_PHASE6C1_CURRICULUM_PROGRESSION_ORDER`：將四個新開放 skill 依
     2-1 / 2-2 / 2-3 章節順序編入

### 3.3 Routes
- `core/routes/practice.py`：**未修改**。`/get_next_question` 與 `/check_answer`
  已能正確處理 `rational_fraction` / `integer` / `expected_value` 三種 answer
  type 與 Chap2 deterministic 路徑，無需任何 routing 變更。

### 3.4 Tests new + minimal updates
- `tests/test_b4_chap2_phase6k_remaining_skill_coverage.py` —— 本輪新增主測檔
- 既有 Phase 6C-1 / 6C-2 / 6C-2R / 6C-1R / 6C-1R2 / 6D / 6E / 6F / 6G-0 / 6I
  測試檔：對於「BasicConceptsOfSets / ProbabilityOperations /
  ApplicationsOfExpectation / MathematicalExpectation 仍 blocked」之歷史斷言，
  最小化反轉為 Phase 6K 新狀態（now enabled / size = 10 / count = 17 等），
  並保留歷史 ID 作為「now enabled」inverted parametrize 的來源。
  受影響測試檔：
  - `tests/test_b4_chap2_phase6c1_probability_basic.py`
  - `tests/test_b4_chap2_phase6c1r_practice_route_integration.py`
  - `tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py`
  - `tests/test_b4_chap2_phase6c2_probability_second_batch.py`
  - `tests/test_b4_chap2_phase6c2r_practice_smoke_regression.py`
  - `tests/test_b4_chap2_phase6d_conditional_probability.py`
  - `tests/test_b4_chap2_phase6e_independent_events.py`
  - `tests/test_b4_chap2_phase6f_expected_value.py`
  - `tests/test_b4_chap2_phase6g0_skill_availability_ux.py`
  - `tests/test_b4_chap2_phase6i_visibility_audit_logging.py`

### 3.5 Reports
- 本檔 `reports/b4_generator_planning/b4_phase6k_chap2_remaining_skill_coverage_runtime_ready_summary.md`

## 4. Implemented skill / problem_type table

| skill_id | problem_type_id | answer_type | checker | difficulty | 主要情境 |
| --- | --- | --- | --- | --- | --- |
| `vh_數學B4_ProbabilityOperations` | `event_operation_probability` | `rational_fraction` | `check_rational_answer` flexible | 1–3 | 已知 P(A), P(B), P(A∩B)，求 P(A∩B'), P(A'∩B), P(A'∩B'), 對稱差 |
| `vh_數學B4_ProbabilityOperations` | `probability_algebra_mixed` | `rational_fraction` | `check_rational_answer` flexible | 1–3 | 由補事件求 P(A)；由 P(A'), P(B), P(A∩B) 求 P(A∪B)；由 P(A∪B) 求 P((A∪B)') |
| `vh_數學B4_BasicConceptsOfSets` | `set_operation_count` | `integer` | `check_integer_answer` strict | 1–3 | 子集個數 2^n、補集個數、由列舉求元素個數 |
| `vh_數學B4_BasicConceptsOfSets` | `inclusion_exclusion_count` | `integer` | `check_integer_answer` strict | 1–3 | 兩集合容斥：n(A∪B)、不喜歡兩項人數、1..N 中 a 倍數∪b 倍數 |
| `vh_數學B4_ApplicationsOfExpectation` | `expectation_word_problem_profit_fairness` | `expected_value` | `check_expected_value_answer` | 1 | 抽彩券一張的期望所得金額（5 個整數元獎額模板） |
| `vh_數學B4_MathematicalExpectation` | `expectation_assessment_numeric` | `expected_value` | `check_expected_value_answer` | 1 | 已整理之 (X, P(X)) 簡單分布（卡片／圓盤），求 E(X) |

## 5. Generator design summary

### 5.1 共通設計
- 所有 generator 採 `random.Random(seed)` 確保 deterministic。
- `seed` 同時驅動 sub-type 決定（透過 `seed % len(sub_types)` 與 rotated fallback），
  避免單一 seed 永遠落在同一變體。
- 接受 `seen_parameter_tuples` 以支援多題不重複的呼叫流程。
- 所有 payload 透過 `validate_problem_payload_contract` 與
  `validate_no_unfilled_placeholder` 把關，確保不含 `[FORMULA_MISSING]` /
  `[BLANK]` / 未填 placeholder。
- 答案以最簡分數字串（或整數字串）儲存，並提供 4 選 1 的 choices；
  正確答案保證在 choices 內。

### 5.2 ProbabilityOperations 設計重點
- 以 (D, a, b, c) 之骨架 sample，要求 `0 < c ≤ min(a, b)`、`a + b - c ≤ D`、
  `a, b < D`，並排除 `a = b = c` 的退化情況。
- 與既有 `union_intersection_probability`（直接套加法定理）刻意區隔，
  本 skill 走「德摩根 + 對稱差 + 補事件混合代數」路線，題幹與
  explanation 都以 set algebra 方式書寫。
- 不做三事件容斥、文氏圖、長文字題（明確以 Python 樣本範圍限制）。

### 5.3 BasicConceptsOfSets 設計重點
- 嚴格不允許「列出所有元素／所有子集」題目（generator 不出現任何
  「請列出」／「請寫出所有」字串，並由測試守護）。
- `inclusion_exclusion_count` 採用學生興趣／整數倍數兩類情境，
  並要求容斥結果 ≤ n(U)、`paub != n_a` 與 `paub != n_b`，避免退化。
- 整數答案以 `int` 形式存於 payload（router 會將 `correct_answer = answer`），
  測試覆蓋 `36`, `36.0`, `36%` 等不同形式以驗證 `check_integer_answer` 嚴格性。

### 5.4 ApplicationsOfExpectation 設計重點
- 5 個 lottery 模板（200/500/1000/100/250 張）已對齊課本「抽彩券」情境；
  獎額皆為整數元，分母為總張數，避免出現需要保險精算或投資報酬的場景。
- 題幹中含關鍵字「彩券」並由測試守護不出現「保險／保費／投資報酬／股票／債券」。
- explanation 採用 `\sum_x x · P(X=x)` 的標準期望值寫法 + 逐項代入。

### 5.5 MathematicalExpectation 設計重點
- 5 個分布模板，全部 sum P = 1（generator 內以 `Fraction` 嚴格驗證），
  情境為「卡片抽獎」與「圓盤抽獎」，避開求未知數題、複雜球抽選題。
- explanation 與 ApplicationsOfExpectation 一致，使用 LaTeX 標準寫法。
- 答案 reduced，可為負（非機率）。

## 6. Checker reuse / minimal checker summary

本輪未新增 checker。完全沿用既有：
- `check_rational_answer(user, num, den, allow_decimal=True, allow_percentage=True, validate_probability_range=True)` — 機率類
- `check_integer_answer(user, expected, allow_negative=False)` — 集合計數類；嚴格拒絕 `36.0`, `36%`, `36/1`
- `check_expected_value_answer(user, correct_str)` — 期望值類；接受分數與小數，**拒絕百分比**

`check_answer` 路由分派 (`core/routes/practice.py:1070-1123`) 已能依
`current["answer_type"]` 自動選對 checker，本輪無需修改。

## 7. Router / allowlist changes

| 項目 | 改動前 | 改動後 |
| --- | --- | --- |
| `B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST` size | 6 | 10 |
| `B4_CHAPTER_2_PHASE6C1_ALLOWED_PROBLEM_TYPES` size | 11 | 17 |
| `B4_CHAPTER_2_EXCLUDED_DETERMINISTIC_PROBLEM_TYPES` | 3 | 4（補 `tree_diagram_listing`） |
| `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS` | 4 | 0（Chap2 已全部開放）|
| `_CHAP2_PHASE6C1_REGISTRY` skill 條目數 | 6 | 10 |

`generate_for_chap2_skill` 仍對 unsupported skill / problem_type 拋
`ValueError`，錯誤訊息使用 decoded skill_id（無 `vh_%E6...` percent
encoding 漏出）。

## 8. Reserved / handwriting exclusion confirmation

- `sample_space_listing` / `event_set_listing` / `subset_listing` /
  `tree_diagram_listing` 全數**不在** deterministic allowlist。
- `is_b4_chapter2_excluded_problem_type(pid)` 對上述 4 個 pid 皆回 `True`。
- `validate_b4_chap2_phase6c1_generator_payload(...)` 對
  `excluded_handwriting_problem_type:<pid>` 回 `(False, ...)`。
- `/get_next_question?skill=vh_數學B4_SampleSpaceAndEvents&problem_type=<listing>`
  路由仍回 422 + `B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR`（前三者）。
- `tree_diagram_listing` 對應 `vh_數學B4_TreeDiagramCounting` 已有獨立的
  free-response handwriting 路徑，與 Chap2 deterministic allowlist 完全隔離。

## 9. Runtime integration summary

| Runtime 切面 | 狀態 | 備註 |
| --- | --- | --- |
| Generator | OK | 6 個新 problem_type，每個多 seed 驗證 |
| Checker reuse | OK | 完全沿用既有 3 種 checker |
| Router registry | OK | 4 skills × 6 entries 新增 |
| Deterministic allowlist | OK | size 11→17 / not-enabled 4→0 |
| `/practice?skill=...` (decoded + encoded) | OK | 4 個新 skill 與 4 個 encoded 變體都回 200 |
| `/get_next_question` 同上 | OK | 200 + `new_question_text` + `problem_type_id` |
| `/check_answer` round-trip | OK | 6 個新 pid 正確答案皆為 `correct=True`，wrong 答案為 `correct=False` |
| Encoded / decoded skill_id 測試 | OK | Phase 6K 新測檔 D 區塊 |
| Frontend double-encoding regression | OK | `_url_unquote ∘ _url_quote ∘ _url_unquote` round-trip |
| Unsupported skill no legacy import | OK | `_monkeypatch_forbid_legacy_skill_import` 守護 |
| Reserved handwriting blocked | OK | 既有 422 行為維持不變 |
| Teacher audit visibility | OK | 6J 測試全部 pass，無 crash |
| Visibility audit logging | OK | 6I 測試全部 pass；deterministic answer 寫入 `record_kind=deterministic_answer` |
| Chap1 regression | OK | `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST` 仍為 13 個；Chap1 router smoke 通過 |

## 10. Audit visibility regression summary

- `persist_b4_chap2_deterministic_answer_event(...)` 對 Phase 6K 4 個 skill
  的 `/check_answer` 回應仍會寫入 `B4Chap2VisibilityAuditLog`（Phase 6K 測試
  `TestAuditVisibilityRegression` 守護）。
- `persist_b4_chap2_gated_event(..., gated_event_type="reserved_problem_type")`
  對保留的 listing 題型仍會寫入 gated audit row。
- Phase 6K 4 個 skill **不再**觸發 `gated_event_type="not_enabled_skill"`
  路徑（因 `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS = frozenset()`）；
  Phase 6I 與 Phase 6K 皆有相應的 inverted 斷言。
- Mastery / APR / fail_streak / remediation：**未修改**，相關計數在 Phase 6I
  測試中以 `Progress` 與 `AdaptiveLearningLog` 表計數確認 `before == after`。

## 11. Tests run

| Test file | Pass | Note |
| --- | --- | --- |
| `tests/test_b4_chap2_phase6c1_probability_basic.py` | All pass | minimal stale assertion update |
| `tests/test_b4_chap2_phase6c1r_practice_route_integration.py` | All pass | minimal stale assertion update |
| `tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py` | All pass | gated 422 → enabled 200 (no legacy import) |
| `tests/test_b4_chap2_phase6c2_probability_second_batch.py` | All pass | minimal stale assertion update |
| `tests/test_b4_chap2_phase6c2r_practice_smoke_regression.py` | All pass | minimal stale assertion update |
| `tests/test_b4_chap2_phase6d_conditional_probability.py` | All pass | size assertion 4 → 0；alloc list 6 → 10 |
| `tests/test_b4_chap2_phase6e_independent_events.py` | All pass | inverted "now enabled" assertions |
| `tests/test_b4_chap2_phase6f_expected_value.py` | All pass | inverted "now enabled" assertions |
| `tests/test_b4_chap2_phase6g0_skill_availability_ux.py` | All pass | TestNotYetEnabledSkills → TestPhase6KOpenedSkillsNoLegacyImport |
| `tests/test_b4_chap2_phase6i_visibility_audit_logging.py` | All pass | gated path → enabled path 反轉 |
| `tests/test_b4_chap2_phase6j_teacher_audit_visibility.py` | All pass | unchanged |
| `tests/test_b4_chap2_phase6k_remaining_skill_coverage.py` | All pass (176) | new file |
| `tests/test_b4_chapter1_adaptive_allowlist.py` | All pass | unchanged |
| `tests/test_vocational_math_b4_question_router_registry_canonical.py` | All pass | unchanged |
| `tests/test_vocational_math_b4_question_router_phase4d1.py` | All pass | unchanged |
| `tests/test_phase5c_d1_fix_b4_router_sampling_exposure.py` | All pass | unchanged |

合計：上述 13 個 Chap1+Chap2 測試檔（949 tests）+ 3 個 router 測試檔
（39 tests）全部通過，無新增 failure。

## 12. Manual smoke checklist

請在 staging 環境逐項手動驗證：

- [ ] `/practice?skill=vh_數學B4_ProbabilityOperations` 進入練習頁顯示題目
- [ ] `/practice?skill=vh_數學B4_BasicConceptsOfSets` 進入練習頁顯示題目
- [ ] `/practice?skill=vh_數學B4_ApplicationsOfExpectation` 進入練習頁顯示題目
- [ ] `/practice?skill=vh_數學B4_MathematicalExpectation` 進入練習頁顯示題目
- [ ] 上述 4 條 URL 之 percent-encoded 變體（`vh_%E6%95%B8%E5%AD%B8B4_...`）
      行為一致，皆回 200，題幹中文正常顯示
- [ ] 對 4 個 skill 各做一次 `/check_answer`：
      - 提交 generator 給的標準答案 → `correct=True`
      - 提交明顯錯誤的數字 / 0 → `correct=False`
- [ ] 對 4 個 skill 各做一次「分數」與「小數」混搭：
      - rational_fraction：`1/2`、`0.5`、`50%` 都 accept
      - integer：`36` accept、`36.0` reject、`36%` reject
      - expected_value：`3/2`、`1.5` accept、`150%` reject
- [ ] `/get_next_question?skill=vh_數學B4_SampleSpaceAndEvents&problem_type=sample_space_listing`
      → 422 + `B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR`
- [ ] Teacher audit 頁面瀏覽 Phase 6K 4 個 skill 的回答記錄不 crash
- [ ] 觀察 `b4_chap2_visibility_audit_logs` 表，新答題記錄
      `record_kind = deterministic_answer` 出現
- [ ] 觀察 `Progress` / `AdaptiveLearningLog` 表，Phase 6K 4 個 skill 的記錄
      **不會**因為 `/check_answer` 而新增（visibility-only 模式維持）

## 13. Known limitations

1. **Generator 變體數有限**：
   - `expectation_word_problem_profit_fairness` 只有 5 個 lottery 模板；
   - `expectation_assessment_numeric` 只有 5 個 (X, P(X)) 模板。
     高量出題（>30 次）將開始重複情境；後續若需擴量，可在不變更 router 的前提下
     增加 `_LOTTERY_TEMPLATES` 與 `_ASSESSMENT_TEMPLATES` 條目。
2. **集合題型涵蓋有限**：
   - `set_operation_count` 只覆蓋子集個數 / 補集個數 / 元素個數三類。
   - `inclusion_exclusion_count` 不做三集合容斥（依 Phase 6K guardrail 設定）。
3. **MathematicalExpectation 的「自評綜合題」未實作**：
   - 課本中此 skill 含求未知 x 使 E(X)=0 等綜合題型；本輪受
     `needs_review` 高與 prompt 限制，僅提供 numeric 題型，後續若要進階開放
     需先做 textbook evidence 二次審視。
4. **Adaptive scoring 仍為 visibility-only**：
   - Phase 6K 不更動 mastery / APR / fail_streak / remediation，相關 progress
     仍由 Phase 6L planning 規劃中。
5. **`B4_CHAP2_SKILL_NOT_ENABLED_PUBLIC_ERROR` 文案保留但已無觸發點**：
   - `practice.py` 中的 not-enabled 422 路徑仍存在，但
     `B4_CHAPTER_2_NOT_ENABLED_PHASE6C1_SKILL_IDS = frozenset()` 後此路徑
     對 Chap2 等價於 dead code。為維持 backward compat，常數與 helper 保留。

## 14. Final confirmation

- 是否補齊 Chap2 remaining deterministic skill coverage：**是**
- 是否新增 handwriting / free-response：**否**
- 是否修改 adaptive scoring / mastery / APR / remediation：**否**
- 是否新增題型：**是**，僅限本輪 6 個 problem_type
  (`event_operation_probability`, `probability_algebra_mixed`,
  `set_operation_count`, `inclusion_exclusion_count`,
  `expectation_word_problem_profit_fairness`,
  `expectation_assessment_numeric`)
- 是否修改 DB schema：**否**
- 是否修改 coverage matrix：**否**
- 是否啟動下一 phase：**否**

完成狀態：**READY_FOR_MANUAL_SMOKE**
