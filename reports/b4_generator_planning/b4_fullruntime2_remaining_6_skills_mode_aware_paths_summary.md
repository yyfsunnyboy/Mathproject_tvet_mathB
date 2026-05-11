# B4 FullRuntime-2 Remaining 6 Skills Mode-aware Paths Summary

## 1. final status

`READY_FOR_COVERAGE_RECOUNT`

## 2. Remaining 6 Skill Runtime Matrix

| skill_id | textbook_fidelity_summary | main_question_style | recommended_runtime_mode | check_mode | grading_mode | answer_input_type | needs_visual | needs_handwriting | needs_teacher_review | deterministic_possible | recommended_first_problem_type | release_in_this_phase | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| vh_數學B4_PascalTriangle | 課本主型偏填表/推導/展開建構，非單一步驟短答 | pascal_triangle_handwriting | visual_or_handwriting_ai_checked | handwriting_ai_checked | ai_assisted_review | handwriting | yes | yes | yes | partial | pascal_triangle_handwriting | yes | 保留手寫與 AI 覆核主路徑，不硬轉 deterministic |
| vh_數學B4_SamplingSurvey | 抽樣調查重點是設計合理性與偏誤說明 | sampling_survey_bias_review | teacher_review | review_mode | teacher_review | text_or_handwriting | no | optional | yes | no | sampling_survey_bias_review | yes | 以情境評析題進入 review path |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | Graph-5 已擋 cumulative graph deterministic 讀圖短答 | cumulative_frequency_table_completion_review | visual_or_handwriting_ai_checked | review_mode | teacher_review | handwriting_or_text | yes | yes | yes | no | cumulative_frequency_table_completion_review | yes | 走補表 + 說明路徑，維持 blocked deterministic gate |
| vh_數學B4_DataOrganizationAndCharts | 題型偏資料整理流程與圖表選擇理由 | data_organization_chart_selection_review | teacher_review | review_mode | teacher_review | text_or_handwriting | yes | optional | yes | partial | data_organization_chart_selection_review | yes | 先做 review shell，不強制自動判分 |
| vh_數學B4_StatisticalChartReading | mixed chart 判讀在 Graph-5 曾被拒絕 deterministic 放行 | statistical_chart_reading_visibility_review | visibility_only | review_mode | visibility_only | text_or_handwriting | yes | optional | yes | partial | statistical_chart_reading_visibility_review | yes | 先提供可見與回收作答，不做 deterministic |
| vh_數學B4_OpinionPollInterpretation | 民調解讀偏開放式評析，需看論述完整度 | opinion_poll_interpretation_review | teacher_review | review_mode | teacher_review | text_or_handwriting | no | optional | yes | no | opinion_poll_interpretation_review | yes | 以 review mode 保留教材語意完整性 |

## 3. 本輪實作 skill 清單

- vh_數學B4_PascalTriangle
- vh_數學B4_SamplingSurvey
- vh_數學B4_CumulativeFrequencyTablesAndGraphs
- vh_數學B4_DataOrganizationAndCharts
- vh_數學B4_StatisticalChartReading
- vh_數學B4_OpinionPollInterpretation

## 4. 每個 skill 的 runtime_mode / check_mode / grading_mode

- vh_數學B4_PascalTriangle: `visual_or_handwriting_ai_checked` / `handwriting_ai_checked` / `ai_assisted_review`
- vh_數學B4_SamplingSurvey: `teacher_review` / `review_mode` / `teacher_review`
- vh_數學B4_CumulativeFrequencyTablesAndGraphs: `visual_or_handwriting_ai_checked` / `review_mode` / `teacher_review`
- vh_數學B4_DataOrganizationAndCharts: `teacher_review` / `review_mode` / `teacher_review`
- vh_數學B4_StatisticalChartReading: `visibility_only` / `review_mode` / `visibility_only`
- vh_數學B4_OpinionPollInterpretation: `teacher_review` / `review_mode` / `teacher_review`

## 5. 每個 skill 的 textbook_fidelity_summary

- `vh_數學B4_PascalTriangle`: 以填列/推導/展開為主，維持手寫與 review 判分。
- `vh_數學B4_SamplingSurvey`: 重點在抽樣設計與偏誤辨識，適合 review。
- `vh_數學B4_CumulativeFrequencyTablesAndGraphs`: 累積次數圖表維持 blocked deterministic，先補表 review。
- `vh_數學B4_DataOrganizationAndCharts`: 重點在整理流程與圖表選擇理由，不硬做短答。
- `vh_數學B4_StatisticalChartReading`: 混合圖表解讀先 visibility/review，避免失真 deterministic。
- `vh_數學B4_OpinionPollInterpretation`: 民調解讀屬論述題，維持 review。

## 6. 每個 skill 的 future path

- deterministic_auto_checked: `vh_數學B4_PascalTriangle`（僅限未來有對齊讀值小題時）
- visual_or_handwriting_ai_checked: `vh_數學B4_PascalTriangle`、`vh_數學B4_CumulativeFrequencyTablesAndGraphs`
- teacher_review: `vh_數學B4_SamplingSurvey`、`vh_數學B4_DataOrganizationAndCharts`、`vh_數學B4_OpinionPollInterpretation`
- visibility_only: `vh_數學B4_StatisticalChartReading`

## 7. 修改檔案清單

- core/vocational_math_b4/generators/chap3_statistical_measures.py
- core/vocational_math_b4/services/question_router.py
- core/vocational_math_b4/adaptive/b4_chapter3_phase7b_allowlist.py
- core/routes/practice.py
- tests/test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py
- reports/b4_generator_planning/b4_fullruntime2_remaining_6_skills_mode_aware_paths_summary.md

## 8. 測試結果

- `pytest -q tests/test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py` -> `15 passed`
- `pytest -q tests/test_b4_fullruntime_remaining_skills_mode_aware_paths.py` -> `15 passed`
- `pytest -q tests/test_b4_graph5_cumulative_or_next_visual_runtime_closed_loop.py` -> `6 passed`
- `pytest -q tests/test_b4_graph4_frequency_polygon_runtime_closed_loop.py` -> `4 passed`
- `pytest -q tests/test_b4_graph3_histogram_runtime_closed_loop.py` -> `10 passed`
- `pytest -q tests/test_b4_graph2_visual_runtime_closed_loop.py` -> `14 passed`
- `pytest -q tests/test_b4_graph1_visual_runtime_first_batch.py` -> `8 passed`
- `pytest -q tests/test_b4_chap3_phase7d_dispersion_measures_runtime_ready.py::test_get_next_question_and_check_answer` -> `1 passed`

## 9. sample artifact paths

- reports/b4_generator_planning/fullruntime2_samples/pascal_triangle_sample_01.json
- reports/b4_generator_planning/fullruntime2_samples/sampling_survey_sample_01.json
- reports/b4_generator_planning/fullruntime2_samples/cumulative_frequency_tables_and_graphs_sample_01.json
- reports/b4_generator_planning/fullruntime2_samples/data_organization_and_charts_sample_01.json
- reports/b4_generator_planning/fullruntime2_samples/statistical_chart_reading_sample_01.json
- reports/b4_generator_planning/fullruntime2_samples/opinion_poll_interpretation_sample_01.json

## 10. closed-loop repair 紀錄

- Round 1:
  - 症狀：`tests/test_b4_graph1_visual_runtime_first_batch.py::test_not_enabled_reserved_ux_not_regressed` 失敗，因 `vh_數學B4_StatisticalChartReading` 改為 runtime 可進入後，舊測試預期 422 not-enabled。
  - 修補：在 `core/routes/practice.py` 增加最小相容規則：`vh_數學B4_StatisticalChartReading` 若未指定 `problem_type` 則維持 422；指定新 review `problem_type` 則走 FullRuntime-2 路徑。
  - 結果：Graph1 回歸恢復通過，FullRuntime-2 測試仍通過。
- Round 2: 未使用。
- Round 3: 未使用。

## 11. known limitations

- `vh_數學B4_StatisticalChartReading` 目前為 visibility_only，尚未開放 deterministic 判分。
- `vh_數學B4_CumulativeFrequencyTablesAndGraphs` 仍維持 cumulative graph deterministic blocked gate。

## 12. 下一步建議

1. 進行 B4 coverage recount，重新統計 `NO_RUNTIME_GENERATOR` 是否降為 `0`。
2. 建立 final coverage matrix（含 deterministic / AI checked / teacher review / visibility 分層）。
3. 若要開放更高自動化，優先從具體且可驗證的小型 choice/short-answer 子題開始。
