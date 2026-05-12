# B4 StatisticalBasicConcepts Diversity Repair Summary

## 1. 問題描述

`vh_數學B4_StatisticalBasicConcepts` 在連續抽題時重複性過高，實測常在 3 個固定題幹之間輪替，甚至可能連續兩題完全相同。這會讓 Chap3 QA gate 的抽樣統計不足以反映 active practice 中的連續重複問題。

## 2. root cause

- `statistical_basic_concepts_choice` 原本只有 3 個 scenario。
- router 對此 skill 只有單一 `problem_type_id`，無法靠 problem type rotation 提升題幹多樣性。
- `/get_next_question` 回傳 payload 原本沒有 `scenario_id`，QA 與 session 層難以統計或避開上一題 scenario。

## 3. 新增 / 擴充 scenario_id 清單

目前 scenario pool 共 12 個：

- `descriptive_statistics_identification`
- `inferential_statistics_identification`
- `statistics_process_collect_data`
- `statistics_process_organize_data`
- `statistics_process_present_data`
- `statistics_process_analyze_data`
- `statistics_process_interpret_data`
- `census_vs_sample_survey_census`
- `census_vs_sample_survey_sample`
- `statistics_purpose_identification`
- `descriptive_not_generalized`
- `inferential_generalized_to_population`

## 4. diversity 測試結果

- 連續 generate 20 題：`unique question_text = 12`
- 連續 generate 20 題：`unique scenario_id = 12`
- `repeated_question_text_ratio = 0.4`
- 連續相鄰 `question_text` 完全相同：否

## 5. 是否已避免連續同題

是。

- generator 在 `seed=None` 時會排除上一個 StatisticalBasicConcepts scenario。
- route 層在 session 已有上一題 `scenario_id` 時，若同 skill 重抽到相同 `scenario_id`，會用最小 retry 改取下一個 scenario。
- `/get_next_question` response 已帶出 `scenario_id` 與 `scenario_family`。

## 6. 是否仍符合 3-1 skill 邊界

是。題目仍限於：

- 統計的意義與目的
- 蒐集、整理、陳示、分析、解釋
- 敘述統計
- 推論統計
- 普查 / 抽查基本概念

未混入四種抽樣方法分類、母群體 / 樣本數細節、樣本平均數 / 母體平均數名詞背誦，或統計量計算題。

## 7. 修改檔案

- `core/vocational_math_b4/generators/chap3_statistical_measures.py`
- `core/routes/practice.py`
- `tests/test_b4_statistical_basic_concepts_diversity_repair.py`
- `reports/b4_generator_planning/b4_statistical_basic_concepts_diversity_repair_summary.md`
- `reports/b4_generator_planning/b4_chap3_ai_question_quality_gate_summary.md`（QA gate 重新產生）

## 8. 新增 tests

- `tests/test_b4_statistical_basic_concepts_diversity_repair.py`
  - scenario pool size / required scenario ids
  - 20 連抽 diversity
  - 3-1 skill boundary
  - choice contract + `/check_answer`
  - route session 避免同 scenario
  - Chap3 QA gate repetition regression

## 9. 測試結果

- `pytest -q tests/test_b4_statistical_basic_concepts_diversity_repair.py` -> 6 passed
- `pytest -q tests/test_b4_choice_payload_rendering_repair.py` -> 6 passed
- `pytest -q tests/test_b4_3_1_conceptual_skill_boundary_repair.py` -> 8 passed
- `pytest -q tests/test_b4_chap3_question_quality_gate.py` -> 1 passed
- `pytest -q tests/test_b4_final_mode_aware_runtime_coverage_recount.py` -> 8 passed

## 10. 是否影響 B4 final coverage count

否。`test_b4_final_mode_aware_runtime_coverage_recount.py` 通過，B4 final coverage count 維持：

- `total_b4_skills = 40`
- `sum_primary_categories = 40`
- `unknown_or_no_runtime_count = 0`

## 11. final status

READY_FOR_RECHECK
