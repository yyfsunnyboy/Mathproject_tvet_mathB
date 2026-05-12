# B4 DataOrganizationAndCharts Runtime Fidelity Repair Summary

## 1. 問題描述
`vh_數學B4_DataOrganizationAndCharts` 在修補前主要落在 review shell，學生端 deterministic 練習題覆蓋不足，且題型重複集中，影響 3-1 課本骨架下的可作答性與穩定性。

## 2. Root Cause
1. Router 對此 skill 的 deterministic problem_type 對應不足。
2. Generator 缺少穩定的 deterministic choice 題型池。
3. 題型 metadata 與 runtime mode contract 不一致，導致題目在 practice 流程中可用性下降。

## 3. 修正後 problem_type / scenario_family
新增並固定可用 deterministic 題型：
1. `chart_type_selection_by_purpose` / `chart_type_selection_by_purpose`
2. `data_organization_first_step` / `data_organization_first_step`

保留 review 題型：
1. `data_organization_chart_selection_review` / `data_organization_review`

## 4. deterministic_choice 題型設計
- 題型聚焦於課本 3-1 的資料整理流程與圖表用途判斷。
- 每題具備明確 `choices` 與唯一正答。
- 合約欄位一致：
  - `runtime_mode=deterministic_choice`
  - `check_mode=deterministic_auto_checked`
  - `grading_mode=deterministic`
  - `answer_input_type=choice`
  - `choices >= 4`
  - `answer` 對應 `choices`

## 5. teacher_review 是否保留
有保留。`data_organization_chart_selection_review` 作為 review/延伸題型，供非 deterministic 路徑使用。

## 6. 修改檔案
1. `core/vocational_math_b4/generators/chap3_statistical_measures.py`
2. `core/vocational_math_b4/services/question_router.py`
3. `core/vocational_math_b4/adaptive/b4_chapter3_phase7b_allowlist.py`
4. `tests/test_b4_data_organization_and_charts_runtime_fidelity_repair.py`

## 7. 新增 tests
1. `tests/test_b4_data_organization_and_charts_runtime_fidelity_repair.py`

## 8. 測試結果
- `pytest -q tests/test_b4_data_organization_and_charts_runtime_fidelity_repair.py`：passed
- `pytest -q tests/test_b4_choice_payload_rendering_repair.py`：passed
- `pytest -q tests/test_b4_3_1_conceptual_skill_boundary_repair.py`：passed
- `pytest -q tests/test_b4_3_2_review_payload_repair.py`：passed
- `pytest -q tests/test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py`：passed
- `pytest -q tests/test_b4_final_mode_aware_runtime_coverage_recount.py`：passed

## 9. 是否影響 B4 final coverage count
不影響。Final coverage recount 維持既有統計，`unknown_or_no_runtime_count` 維持 0。

## 10. Final Status
`READY_FOR_RECHECK`
