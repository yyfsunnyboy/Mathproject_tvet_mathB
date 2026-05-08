# B4 Chapter 2 Phase 6E：Independent Events Runtime-Ready Batch Summary

## 1. Scope and guardrails

本輪僅處理 Phase 6E 指定兩個 problem_type：

- `independent_joint_probability`
- `independent_at_least_one_probability`

skill_id 僅：

- `vh_數學B4_IndependentEvents`

遵守硬性限制：未處理 ExpectedValue / BasicConceptsOfSets / handwriting-free-response / listing / DB / coverage matrix / adaptive scoring / APR / remediation / Phase 6F。

## 2. Runtime Smoke Gate SOP compliance

依 `docs/系統SOP/B4_deterministic_generator_runtime_smoke_gate_SOP_v0.1.md`（含 v0.1.1 frontend double-encoding guard）完成：

- generator quick smoke
- 分段測試（generator / checker / router+allowlist / route）
- full Phase 6E suite
- Phase 6C/6D + Chap1 regression suites
- encoded/decoded 與 frontend double-encoding regression
- unsupported skill no legacy fallback guard
- handwriting reserved blocked guard

## 3. Files changed

### Production code

- `core/vocational_math_b4/generators/chap2_independent_events.py`（新增）
- `core/vocational_math_b4/services/question_router.py`（新增 6E registry）
- `core/vocational_math_b4/adaptive/b4_chapter2_phase6c1_allowlist.py`（新增 6E skill/problem_types，並更新 not-enabled 集合）

### Tests

- `tests/test_b4_chap2_phase6e_independent_events.py`（新增）
- `tests/test_b4_chap2_phase6d_conditional_probability.py`（隨 6E allowlist 邊界更新）
- `tests/test_b4_chap2_phase6c2_probability_second_batch.py`（隨 6E allowlist 邊界更新）
- `tests/test_b4_chap2_phase6c1_probability_basic.py`（隨 6E allowlist 邊界更新）

## 4. Implemented problem_types

### A. `independent_joint_probability`

- 數學語意：`P(A∩B)=P(A)×P(B)`
- 支援三種直接代入型：
  - 已知 `P(A), P(B)` 求 `P(A∩B)`
  - 已知 `P(A∩B), P(A)` 求 `P(B)`
  - 已知 `P(A∩B), P(B)` 求 `P(A)`
- 題幹明確包含獨立事件語意
- answer 為最簡分數；`answer_type=rational_fraction`

### B. `independent_at_least_one_probability`

- 數學語意：`P(至少一次成功)=1-(1-p)^n`
- 支援簡單重複獨立試驗場景（抽象、命中率、通過率）
- `n` 限在小整數範圍（2~5）
- `p` 使用簡單分數池
- answer 為最簡分數；`answer_type=rational_fraction`

## 5. Generator design summary

- 兩題均沿用 deterministic seed 生成
- payload 均包含：
  - `question_text`, `answer`, `explanation`, `skill_id`, `problem_type_id`, `generator_key`
  - `answer_type`, `difficulty`, `diagnosis_tags`, `remediation_candidates`
- 全部題目保證：
  - 無 `[FORMULA_MISSING]` / `[BLANK]` / placeholder
  - `answer` 在 `[0,1]`
  - 非 handwriting / 非 ai_judged_free_response
- explanation 分別明確展示：
  - `P(A∩B)=P(A)×P(B)`
  - `1-(1-p)^n`

## 6. Router / allowlist changes

- `question_router` 新增 `vh_數學B4_IndependentEvents` registry：
  - `independent_joint_probability`
  - `independent_at_least_one_probability`
- deterministic allowlist 新增：
  - skill：`vh_數學B4_IndependentEvents`
  - problem_types：上述兩題
- 保留 6C / 6D 已開放題型
- 仍維持不開放：
  - `vh_數學B4_BasicConceptsOfSets`
  - `vh_數學B4_ProbabilityOperations`
  - `vh_數學B4_MathematicalExpectationDefinition`
  - `vh_數學B4_ApplicationsOfExpectation`
  - `vh_數學B4_MathematicalExpectation`
- handwriting reserved 題型仍 hard-excluded

## 7. Checker reuse summary

- 完全重用 `check_rational_answer` flexible
- 覆蓋等值輸入：
  - canonical fraction
  - unreduced fraction
  - decimal（有限小數）
  - percentage
  - LaTeX fraction（由 validator 既有 parse 支援）
- 覆蓋無效輸入：
  - wrong fraction
  - denominator zero
  - out-of-range probability

## 8. Tests run

### Quick smoke

- `python -c "... independent_joint_probability ... independent_at_least_one_probability ..."`
- 結果：PASS

### Phase 6E segmented

- `python -m pytest tests/test_b4_chap2_phase6e_independent_events.py -vv -s -k "generator"`
  - `60 passed`
- `python -m pytest tests/test_b4_chap2_phase6e_independent_events.py -vv -s -k "checker"`
  - `2 passed`
- `python -m pytest tests/test_b4_chap2_phase6e_independent_events.py -vv -s -k "router or allowlist"`
  - `7 passed`
- `python -m pytest tests/test_b4_chap2_phase6e_independent_events.py -vv -s -k "route or practice or check_answer"`
  - `13 passed`

### Full Phase 6E

- `python -m pytest tests/test_b4_chap2_phase6e_independent_events.py -q`
  - `76 passed`

### Required regression

- `python -m pytest tests/test_b4_chap2_phase6d_conditional_probability.py tests/test_b4_chap2_phase6c2_probability_second_batch.py tests/test_b4_chap2_phase6c1_probability_basic.py tests/test_b4_chap2_phase6c1r2_practice_next_question_integration.py tests/test_b4_chapter1_adaptive_allowlist.py tests/test_vocational_math_b4_question_router_registry_canonical.py -q`
  - `437 passed`

## 9. Manual smoke checklist

待人工執行：

- `/practice?skill=vh_數學B4_IndependentEvents`
- `/practice?skill=vh_%E6%95%B8%E5%AD%B8B4_IndependentEvents`
- `/get_next_question?skill=vh_數學B4_IndependentEvents&problem_type=independent_joint_probability`
- `/get_next_question?skill=vh_數學B4_IndependentEvents&problem_type=independent_at_least_one_probability`
- `/check_answer`：fraction / unreduced / decimal / percentage
- unsupported skill：不出現 `skills.vh_數學B4_xxx` missing module import
- frontend double-encoding regression（v0.1.1 guard）
- handwriting reserved blocked

## 10. Risks / known limitations

- 既有 `check_rational_answer` 對循環小數（例如 1/3 的 float 字串）為近似，不保證視為等值；測試已以有限小數情境驗證 decimal/percentage。
- route 層 error 訊息仍沿用歷史字串 `Phase 6C-1`，行為正確但文案名稱未改動（不影響本輪範圍）。

## 11. Final confirmation

- 是否只處理 2 個 problem_type：是
- 是否新增 Phase 6E 題型以外內容：否
- 是否修改 production code：是，限本輪必要檔案
- 是否修改 tests：是，限本輪測試
- 是否修改 routes：否
- 是否修改 templates：否
- 是否修改 generators：是，限 Chap2 independent events generator
- 是否修改 database：否
- 是否修改 coverage matrix：否
- 是否新增 / 修改 deterministic allowlist：是，只限 6E 兩題 + 保留 6C/6D
- 是否加入 handwriting/free-response 題型：否
- 是否處理 ExpectedValue / BasicConceptsOfSets：否
- 是否修改 adaptive scoring / mastery / APR / remediation：否
- 是否啟動 Phase 6F：否

---

**狀態：READY_FOR_MANUAL_SMOKE**
