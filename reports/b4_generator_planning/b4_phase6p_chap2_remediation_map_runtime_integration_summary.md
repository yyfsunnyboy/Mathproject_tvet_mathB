# Phase 6P：Chap2 Remediation Map Runtime Integration Summary

## 1. Scope and Guardrails

Phase 6P 目標：將 Phase 6O 的 problem_type-level prerequisite/remediation map 接入 Chap2 session-local remediation target selection，降低補救文不對題。

本輪遵守限制：
- 只調整 Chap2 session-local remediation target selection
- 不改正式 mastery
- 不改 APR / PPO / AKT
- 不改正式 remediation policy
- 不改 generators / validators
- 不改 DB schema
- 不改 coverage matrix
- 不新增題型
- 不啟動下一 phase

## 2. Why Phase 6P is needed

Phase 6N-T / 6N-T-R2 已有觸發與 stage guard，但補救目標仍偏 stage-level bridge。Phase 6P 把選題升級為：
- failed_problem_type_id 優先
- 以 problem_type remediation_candidates 做 map-first selection
- 不可用時才 stage fallback
- 全程保留 forward-stage guard

## 3. Files changed

- `core/vocational_math_b4/services/b4_chap2_chapter_mode.py`
  - 新增 17 題型 `_CHAP2_REMEDIATION_MAP`
  - 新增 `get_chap2_remediation_map()`
  - 新增 `_select_remediation_target(...)`（map-first + fallback）
  - 補救出題改為 failed_problem_type map-first
  - 補救評分改為依 runtime 當前補救題規格（非固定 bridge）
  - 新增 remediation metadata 回傳與 runtime store 持久化
- `tests/test_b4_chap2_phase6p_remediation_map_runtime_integration.py`
  - 新增 Phase 6P 獨立測試
- `tests/test_b4_chap2_phase6n_t_session_local_remediation.py`
  - 最小調整既有 drift 測試斷言，對齊 6P map-first 行為

## 4. Runtime remediation map summary

- map 名稱：`_CHAP2_REMEDIATION_MAP`
- 每筆欄位包含：
  - `problem_type_id`
  - `stage`
  - `direct_prerequisites`
  - `remediation_candidates`
  - `fallback_stage`
  - `scoring_signal_class`
  - 以及 runtime 選題所需 `skill_id` / `answer_type` / `checker`
- 選題優先序：
  1) failed_problem_type_id -> map remediation_candidates
  2) 過濾：allowlist / non-reserved / stage order
  3) 若 map 候選不可用，fallback 同 stage safe bridge
  4) 再 fallback previous-stage safe bridge

## 5. 17 problem_type coverage table

| # | problem_type_id | covered |
|---|---|---|
| 1 | set_operation_count | yes |
| 2 | inclusion_exclusion_count | yes |
| 3 | sample_space_count_numeric | yes |
| 4 | classical_probability_fraction | yes |
| 5 | dice_coin_probability_count | yes |
| 6 | complement_probability | yes |
| 7 | union_intersection_probability | yes |
| 8 | event_operation_probability | yes |
| 9 | probability_algebra_mixed | yes |
| 10 | conditional_probability_basic | yes |
| 11 | without_replacement_conditional_probability | yes |
| 12 | independent_joint_probability | yes |
| 13 | independent_at_least_one_probability | yes |
| 14 | expectation_discrete_basic | yes |
| 15 | expectation_from_distribution | yes |
| 16 | expectation_word_problem_profit_fairness | yes |
| 17 | expectation_assessment_numeric | yes |

## 6. Selection policy

補救 response 新增並保留：
- `failed_stage`
- `failed_skill_id`
- `failed_problem_type_id`
- `remediation_source` (`problem_type_map` / `stage_fallback`)
- `remediation_candidates_considered`
- `selected_remediation_problem_type_id`
- `selected_remediation_skill_id`
- `in_remediation`
- `return_ready`
- `has_returned_to_main`

## 7. Stage order guard confirmation

保留並持續強制：
- `stage_1_sets_and_sample_space = 1`
- `stage_2_basic_probability = 2`
- `stage_3_conditional_independent = 3`
- `stage_4_expectation = 4`

規則：`remediation_stage_order <= failed_stage_order`

驗證重點：
- Stage2 不會補到 Conditional/Independent/Expectation
- Stage3 不會補到 Expectation
- Stage4 可補 Expectation，也可回補 Stage2 基礎機率

## 8. Reserved exclusion confirmation

以下仍硬排除，不可被 map/fallback 選中：
- `sample_space_listing`
- `event_set_listing`
- `subset_listing`
- `tree_diagram_listing`

## 9. Tests run

### Phase 6P new tests
- `tests/test_b4_chap2_phase6p_remediation_map_runtime_integration.py`
  - 34 passed

### Required regressions
- `tests/test_b4_chap2_phase6n_t_session_local_remediation.py`
  - 57 passed
- `tests/test_b4_chap2_phase6n_adaptive_practice_chapter_mode_integration.py`
  - 61 passed
- `tests/test_b4_chap2_phase6i_visibility_audit_logging.py`
  - 4 passed
- `tests/test_b4_chap2_phase6j_teacher_audit_visibility.py`
  - full suite exceeded timeout in current env
  - representative critical subset rerun:
    - `TestTeacherAuditJson::test_limit_param`
    - `TestTeacherAuditJson::test_student_api_forbidden`
    - `TestVisibilityOnlySideEffects::test_get_audit_does_not_touch_progress_or_adaptive_logs`
    - `TestAdminMayAccess::test_admin_html_ok`
    - 4 passed
- `tests/test_b4_chapter1_adaptive_allowlist.py`
  - 24 passed
- `tests/test_vocational_math_b4_question_router_registry_canonical.py`
  - 8 passed

## 10. Regression result

- 新增 6P 測試全綠
- 6N-T / 6N / 6I / Chap1 / router canonical 全綠
- 6J 全檔在本環境 timeout；已補跑代表性關鍵案例且全綠

## 11. Minimal manual smoke checklist

- [ ] Chap2 chapter mode 進入後，Stage2 連錯兩題
  - [ ] 補救題 `selected_remediation_problem_type_id` 來自 map 候選
  - [ ] `remediation_source` 顯示 `problem_type_map` 或 `stage_fallback`
  - [ ] 不出現 Stage3/Stage4 forward-stage 題型
- [ ] Stage3 連錯兩題
  - [ ] 不出現 expectation 題型
- [ ] Stage4 連錯兩題
  - [ ] 可出現 expectation 題型或 Stage2 基礎回補
- [ ] 補救答對後 `return_ready=True` 並返回主線

## 12. Known limitations

- 仍為 session-local remediation
- 尚未接正式 APR / PPO / AKT routing
- 尚未寫入正式 mastery
- 目前為 deterministic_checked 主訊號；AI-judged handwriting/free-response 仍 reserved

## 13. Final confirmation

- 是否把 Phase 6O map 接進 runtime remediation：是
- 是否涵蓋 17/17 problem_type：是
- 是否禁止 forward-stage remediation：是
- 是否保留 reserved exclusion：是
- 是否修改正式 mastery：否
- 是否修改 APR / PPO / AKT：否
- 是否新增題型：否
- 是否修改 DB schema：否
- 是否破壞 Chap1：否
- 是否啟動下一 phase：否

## Status
- READY_FOR_MANUAL_SMOKE
