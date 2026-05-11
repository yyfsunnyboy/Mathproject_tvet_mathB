# B4 FullRuntime Remaining 11 Skills Mode-Aware Paths Summary

## 1. final status

`READY_FOR_NEXT_BATCH`

## 2. Remaining 11 Skill Runtime Matrix

| skill_id | textbook_fidelity_summary | main_question_style | recommended_runtime_mode | check_mode | grading_mode | answer_input_type | needs_visual | needs_handwriting | needs_teacher_review | deterministic_possible | recommended_first_problem_type | release_in_this_phase | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| vh_數學B4_TreeDiagramCounting | 課本主型偏樹狀圖列舉與路徑建構，屬作圖流程 | tree_diagram_completion_or_listing | visual_or_handwriting_ai_checked | handwriting_ai_checked | ai_assisted_review | handwriting | yes | yes | no | no | tree_diagram_completion_or_listing | yes | 不硬做 deterministic，先提供手寫/AI 檢查 runtime shell |
| vh_數學B4_PascalTriangle | 課本常見推導與列舉建構，非單一短答 | pascal_triangle_handwriting_or_review | visual_or_handwriting_ai_checked | handwriting_ai_checked | ai_assisted_review | handwriting | no | yes | yes | partial | pascal_triangle_handwriting | no | 本輪先保留既有手寫路徑，不新增 deterministic 以維持 textbook fidelity |
| vh_數學B4_SamplingMethods | 有可對齊分類題，可做選擇/代號判斷 | sampling_methods_classification_choice | deterministic_auto_checked | deterministic_auto_checked | deterministic | choice | no | no | no | yes | sampling_methods_classification_choice | yes | 先上最小風險分類題，題意明確可機器判分 |
| vh_數學B4_SamplingSurvey | 偏調查設計與說明，通常需敘述與評估 | survey_design_open_response | teacher_review | review_mode | teacher_review | text_or_handwriting | no | optional | yes | no | survey_plan_review_prompt | no | 保留 review path，不硬轉短答 |
| vh_數學B4_StatisticalBasicConcepts | 有母體/樣本/參數/統計量概念判斷題 | statistical_basic_concepts_choice | deterministic_auto_checked | deterministic_auto_checked | deterministic | choice | no | no | no | yes | statistical_basic_concepts_choice | yes | 概念分類可對齊課本基本定義判別 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | Graph-5 已確認缺 aligned deterministic reading source | cumulative_graph_or_table_completion | visual_or_handwriting_ai_checked | review_mode | teacher_review | handwriting_or_text | yes | optional | yes | no | cumulative_table_completion_review | no | 維持 blocked deterministic gate，先走 review/AI 路徑 |
| vh_數學B4_DataOrganizationAndCharts | 常見整理資料/選圖/製圖，含開放式判讀 | data_organization_chart_review | teacher_review | review_mode | teacher_review | text_or_handwriting | yes | optional | yes | partial | chart_selection_reasoning_review | no | 先以可見與覆核路徑收斂，避免硬拆 deterministic |
| vh_數學B4_FrequencyDistributionTableConstruction | 主型為補表與建表，多格答案不適合一般 deterministic | table_completion_handwriting | visual_or_handwriting_ai_checked | handwriting_ai_checked | ai_assisted_review | handwriting | yes | yes | yes | no | table_completion_handwriting | yes | 先提供 handwritng runtime shell 與 AI guard |
| vh_數學B4_StatisticalChartReading | Graph-5 mixed chart 已拒絕 release | mixed_chart_interpretation_review | visibility_only | review_mode | visibility_only | text_or_handwriting | yes | optional | yes | partial | mixed_chart_interpretation_review | no | 無對齊 deterministic source，先 visibility/review |
| vh_數學B4_NormalDistributionAndEmpiricalRule | 有固定經驗法則 68-95-99 讀值，可短答/選擇 | empirical_rule_interval_percentage | deterministic_auto_checked | deterministic_auto_checked | deterministic | short_answer | no | no | no | yes | empirical_rule_interval_percentage | yes | 先上經驗法則短答，答案明確且可自動判分 |
| vh_數學B4_OpinionPollInterpretation | 民調解讀偏開放式評論，常需文字論述 | opinion_poll_interpretation_review | visibility_only | review_mode | visibility_only | text_or_handwriting | yes | optional | yes | no | opinion_poll_interpretation_review | no | 維持 review/visibility path，避免失真 deterministic |

## 3. 本輪實作 skill 清單

- vh_數學B4_NormalDistributionAndEmpiricalRule
- vh_數學B4_SamplingMethods
- vh_數學B4_StatisticalBasicConcepts
- vh_數學B4_TreeDiagramCounting
- vh_數學B4_FrequencyDistributionTableConstruction

## 4. 未實作但已分流 skill 清單

- vh_數學B4_PascalTriangle
- vh_數學B4_SamplingSurvey
- vh_數學B4_CumulativeFrequencyTablesAndGraphs
- vh_數學B4_DataOrganizationAndCharts
- vh_數學B4_StatisticalChartReading
- vh_數學B4_OpinionPollInterpretation

## 5. 每個 skill 的 future path

- deterministic_auto_checked: `vh_數學B4_NormalDistributionAndEmpiricalRule`, `vh_數學B4_SamplingMethods`, `vh_數學B4_StatisticalBasicConcepts`
- visual_or_handwriting_ai_checked: `vh_數學B4_TreeDiagramCounting`, `vh_數學B4_FrequencyDistributionTableConstruction`, `vh_數學B4_PascalTriangle`, `vh_數學B4_CumulativeFrequencyTablesAndGraphs`
- teacher_review: `vh_數學B4_SamplingSurvey`, `vh_數學B4_DataOrganizationAndCharts`
- visibility_only: `vh_數學B4_StatisticalChartReading`, `vh_數學B4_OpinionPollInterpretation`

## 6. 修改檔案清單

- core/vocational_math_b4/generators/chap3_statistical_measures.py
- core/vocational_math_b4/services/question_router.py
- core/vocational_math_b4/adaptive/b4_chapter3_phase7b_allowlist.py
- core/routes/practice.py

## 7. 測試結果

- `pytest -q tests/test_b4_fullruntime_remaining_skills_mode_aware_paths.py` -> `15 passed`
- `pytest -q tests/test_b4_graph5_cumulative_or_next_visual_runtime_closed_loop.py` -> `6 passed`
- `pytest -q tests/test_b4_graph4_frequency_polygon_runtime_closed_loop.py` -> `4 passed`
- `pytest -q tests/test_b4_graph3_histogram_runtime_closed_loop.py` -> `10 passed`
- `pytest -q tests/test_b4_graph2_visual_runtime_closed_loop.py` -> `14 passed`
- `pytest -q tests/test_b4_graph1_visual_runtime_first_batch.py` -> `8 passed`
- `pytest -q tests/test_b4_chap3_phase7d_dispersion_measures_runtime_ready.py::test_get_next_question_and_check_answer` -> `1 passed`

## 8. sample artifact paths

- reports/b4_generator_planning/fullruntime_samples/normal_distribution_empirical_rule_sample_01.json
- reports/b4_generator_planning/fullruntime_samples/sampling_methods_sample_01.json
- reports/b4_generator_planning/fullruntime_samples/statistical_basic_concepts_sample_01.json
- reports/b4_generator_planning/fullruntime_samples/tree_diagram_counting_sample_01.json
- reports/b4_generator_planning/fullruntime_samples/frequency_distribution_table_construction_sample_01.json

## 9. closed-loop repair 紀錄

- Round 1:
  - 症狀：新測試中 `TreeDiagramCounting` 的 `problem_type_id` 與 route guard metadata 不一致。
  - 修補：在 `core/routes/practice.py` 的 `_build_b4_tree_diagram_runtime_payload` 補上 `runtime_mode/check_mode/grading_mode/requires_handwriting`。
  - 結果：`tests/test_b4_fullruntime_remaining_skills_mode_aware_paths.py` 由 fail 轉 pass。
- Round 2:
  - 症狀：Graph1/Graph2 既有回歸測試要求 `tree_diagram_listing` 的 `grading_mode=ai_judged_free_response`。
  - 修補：保留新 `check_mode` guard，並把 tree runtime payload 的 `grading_mode` 回復為 `ai_judged_free_response`；同時在 allowlist 保留 `B4_CHAPTER3_PHASE7B_ALLOWLIST` 相容別名。
  - 結果：Graph1/Graph2 回歸皆 pass。
- Round 3: 未使用（保留）。

## 10. known limitations

- 本輪僅完成 5 個 skill 的 runtime path/shell，未擴張至 Graph-4 / Graph-5 blocked family。
- teacher_review / visibility_only 類 skill 目前先以 matrix 與 future path 鎖定，未新增新 generator family。

## 11. 下一批建議

1. 針對 `vh_數學B4_PascalTriangle` 補一個可選 deterministic 讀值小題（若教材 evidence 支持）與保留手寫路徑並存。
2. 針對 `vh_數學B4_SamplingSurvey`、`vh_數學B4_OpinionPollInterpretation` 建立 review_mode payload shell 與教師端可見欄位。
3. 對 `vh_數學B4_CumulativeFrequencyTablesAndGraphs`、`vh_數學B4_StatisticalChartReading` 持續維持 blocked gate，僅在有 aligned source 時再開 deterministic。
