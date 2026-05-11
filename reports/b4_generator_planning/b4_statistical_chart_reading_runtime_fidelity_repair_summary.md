# B4 StatisticalChartReading Runtime Fidelity Repair Summary

## 1. ????
`vh_??B4_StatisticalChartReading` ??????? open-ended visibility/review ?????????????? payload ?????expected answer ?????? rubric????????????????????

## 2. Root Cause
1. router ? `StatisticalChartReading` ???? `statistical_chart_reading_visibility_review` entry?
2. generator ?? deterministic choice ?????????????????
3. review payload ??????? visual/rubric contract?
4. skill id ??????????????? `unsupported skill_id`?

## 3. ??? problem_type / scenario_family
?? deterministic_choice ???
1. `chart_type_by_purpose` / `chart_type_by_purpose`
2. `chart_interpretation_caution` / `chart_interpretation_caution`
3. `chart_match_data_type` / `chart_match_data_type`

?? review ???
1. `statistical_chart_reading_visibility_review` / `statistical_chart_reading_visibility_review`

## 4. ??????????????????
??review ???????????payload ???? `visual_aids` ? `chart_spec`???? `visual_backed=true`?

## 5. ???? deterministic_choice ??
????? 3 ? deterministic choice ?????? choice contract?choices>=4?answer ????mode/check/grading ? deterministic path??

## 6. ???? teacher_review ?????
???? `statistical_chart_reading_visibility_review`?????
- `expected_answer_schema` / rubric
- `visual_backed=true`
- `visual_asset_type=chart`
- `check_mode=review_mode`?review guard?

## 7. ????
1. `core/vocational_math_b4/generators/chap3_statistical_measures.py`
2. `core/vocational_math_b4/services/question_router.py`
3. `core/vocational_math_b4/adaptive/b4_chapter3_phase7b_allowlist.py`
4. `tests/test_b4_statistical_chart_reading_runtime_fidelity_repair.py`

## 8. ?? tests
1. `tests/test_b4_statistical_chart_reading_runtime_fidelity_repair.py`

## 9. ????
????
1. `py -m pytest -q tests/test_b4_statistical_chart_reading_runtime_fidelity_repair.py` (6 passed)
2. `py -m pytest -q tests/test_b4_choice_payload_rendering_repair.py` (6 passed)
3. `py -m pytest -q tests/test_b4_3_2_review_payload_repair.py` (3 passed)
4. `py -m pytest -q tests/test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py` (15 passed)
5. `py -m pytest -q tests/test_b4_final_mode_aware_runtime_coverage_recount.py` (8 passed)
6. `py -m pytest -q tests/test_b4_data_organization_and_charts_runtime_fidelity_repair.py` (6 passed)

## 10. ???? B4 final coverage count
????final coverage recount ??????`unknown_or_no_runtime_count` ?? 0?

## 11. Final Status
READY_FOR_RECHECK
