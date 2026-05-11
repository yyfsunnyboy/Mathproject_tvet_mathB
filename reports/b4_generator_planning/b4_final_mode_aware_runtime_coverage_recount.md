# B4 Final Mode-aware Runtime Coverage Recount

## A. Final B4 Skill Coverage Matrix

| chapter | section | skill_id | skill_ch_name | primary_runtime_category | runtime_mode | check_mode | grading_mode | released_family_or_problem_type | secondary_tags | evidence_source | tests_or_report_evidence | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 排列組合 | 1-1 加法原理與乘法原理 | vh_數學B4_AdditionPrinciple | 加法原理 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | add_principle_mutually_exclusive_choice | deterministic_released | question_router chap1 registry | b4_ch1_runtime_closure_report.md | 主線 deterministic |
| 1 排列組合 | 1-1 加法原理與乘法原理 | vh_數學B4_FactorialNotation | 階乘記法 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | factorial_evaluation/factorial_equation_solve_n | deterministic_released | question_router chap1 registry | b4_ch1_runtime_closure_report.md | 主線 deterministic |
| 1 排列組合 | 1-1 加法原理與乘法原理 | vh_數學B4_MultiplicationPrinciple | 乘法原理 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | mult_principle_independent_choices | deterministic_released | question_router chap1 registry | b4_ch1_runtime_closure_report.md | 主線 deterministic |
| 1 排列組合 | 1-1 加法原理與乘法原理 | vh_數學B4_TreeDiagramCounting | 樹狀圖 | VISUAL_OR_HANDWRITING_AI_CHECKED | visual_or_handwriting_ai_checked | handwriting_ai_checked | ai_judged_free_response | tree_diagram_listing/tree_diagram_completion_or_listing | handwriting_candidate,review_shell_released | practice runtime payload + chap3 router | test_b4_fullruntime_remaining_skills_mode_aware_paths.py | 不走 deterministic |
| 1 排列組合 | 1-2 直線排列 | vh_數學B4_PermutationOfDistinctObjects | 相異物的排列 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | permutation_role_assignment 等 | deterministic_released | question_router chap1 registry | b4_ch1_runtime_closure_report.md | 主線 deterministic |
| 1 排列組合 | 1-2 直線排列 | vh_數學B4_PermutationOfNonDistinctObjects | 不盡相異物的排列 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | non_distinct_objects_arrangement | deterministic_released | question_router chap1 registry | b4_phase4e_postcheck_d2_fix_non_distinct_objects_generator_summary.md | 主線 deterministic |
| 1 排列組合 | 1-3 重複排列 | vh_數學B4_PermutationWithRepetition | 重複排列 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | repeated_choice_basic/repeated_permutation_assignment | deterministic_released | question_router chap1 registry | b4_ch1_runtime_closure_report.md | 主線 deterministic |
| 1 排列組合 | 1-3 重複排列 | vh_數學B4_RepeatedPermutation | 重複排列 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | repeated_permutation_digits | deterministic_released | question_router chap1 registry | b4_ch1_runtime_closure_report.md | 主線 deterministic |
| 1 排列組合 | 1-4 組合 | vh_數學B4_Combination | 組合 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | combination_basic_selection 等 | deterministic_released | question_router chap1 registry | b4_ch1_runtime_closure_report.md | 主線 deterministic |
| 1 排列組合 | 1-4 組合 | vh_數學B4_CombinationApplications | 組合的應用 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | combination_polygon_count 等 | deterministic_released | question_router chap1 registry | b4_ch1_runtime_closure_report.md | 主線 deterministic |
| 1 排列組合 | 1-4 組合 | vh_數學B4_CombinationDefinition | 組合的定義與計算 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | combination_definition_basic | deterministic_released | question_router chap1 registry | b4_ch1_runtime_closure_report.md | 主線 deterministic |
| 1 排列組合 | 1-4 組合 | vh_數學B4_CombinationProperties | 組合的性質 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | combination_properties_simplification | deterministic_released | question_router chap1 registry | b4_ch1_runtime_closure_report.md | 主線 deterministic |
| 1 排列組合 | 1-5 二項式定理 | vh_數學B4_BinomialCoefficientIdentities | 二項式係數性質 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | binomial_coefficient_sum 等 | deterministic_released | question_router chap1 registry | b4_ch1_runtime_closure_report.md | 主線 deterministic |
| 1 排列組合 | 1-5 二項式定理 | vh_數學B4_BinomialTheorem | 二項式定理 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | binomial_specific_term_coefficient 等 | deterministic_released | question_router chap1 registry | b4_ch1_runtime_closure_report.md | 主線 deterministic |
| 1 排列組合 | 1-5 二項式定理 | vh_數學B4_PascalTriangle | 巴斯卡三角形 | VISUAL_OR_HANDWRITING_AI_CHECKED | visual_or_handwriting_ai_checked | handwriting_ai_checked | ai_assisted_review | pascal_triangle_handwriting | handwriting_candidate,review_shell_released | practice runtime payload | test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py | 不硬做 deterministic |
| 2 機率 | 2-1 樣本空間與事件 | vh_數學B4_BasicConceptsOfSets | 集合的基本概念 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | set_operation_count/inclusion_exclusion_count | deterministic_released | chap2 registry | b4_chap2_deterministic_mainline_closure.md | 主線 deterministic |
| 2 機率 | 2-1 樣本空間與事件 | vh_數學B4_SampleSpaceAndEvents | 樣本空間與事件 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | sample_space_count_numeric | deterministic_released | chap2 registry | b4_chap2_deterministic_mainline_closure.md | 主線 deterministic |
| 2 機率 | 2-2 機率的運算 | vh_數學B4_ConditionalProbability | 條件機率 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | conditional_probability_basic 等 | deterministic_released | chap2 registry | b4_phase6d_conditional_probability_runtime_ready_summary.md | 主線 deterministic |
| 2 機率 | 2-2 機率的運算 | vh_數學B4_IndependentEvents | 獨立事件 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | independent_joint_probability 等 | deterministic_released | chap2 registry | b4_phase6e_independent_events_runtime_ready_summary.md | 主線 deterministic |
| 2 機率 | 2-2 機率的運算 | vh_數學B4_ProbabilityDefinition | 機率的定義 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | classical_probability_fraction 等 | deterministic_released | chap2 registry | b4_phase6c2_second_deterministic_probability_summary.md | 主線 deterministic |
| 2 機率 | 2-2 機率的運算 | vh_數學B4_ProbabilityOperations | 機率的運算 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | event_operation_probability 等 | deterministic_released | chap2 registry | b4_phase6k_chap2_remaining_skill_coverage_runtime_ready_summary.md | 主線 deterministic |
| 2 機率 | 2-2 機率的運算 | vh_數學B4_ProbabilityProperties | 機率的性質 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | complement_probability/union_intersection_probability | deterministic_released | chap2 registry | b4_phase6c2_second_deterministic_probability_summary.md | 主線 deterministic |
| 2 機率 | 2-3 數學期望值 | vh_數學B4_ApplicationsOfExpectation | 數學期望值的應用 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | expectation_word_problem_profit_fairness | deterministic_released | chap2 registry | b4_phase6k_chap2_remaining_skill_coverage_runtime_ready_summary.md | 主線 deterministic |
| 2 機率 | 2-3 數學期望值 | vh_數學B4_MathematicalExpectation | 數學期望值 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | expectation_assessment_numeric | deterministic_released | chap2 registry | b4_phase6k_chap2_remaining_skill_coverage_runtime_ready_summary.md | 主線 deterministic |
| 2 機率 | 2-3 數學期望值 | vh_數學B4_MathematicalExpectationDefinition | 數學期望值的定義與計算 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | expectation_discrete_basic/expectation_from_distribution | deterministic_released | chap2 registry | b4_phase6f_expected_value_runtime_ready_summary.md | 主線 deterministic |
| 3 統計 | 3-1 統計的基本概念 | vh_數學B4_SamplingMethods | 抽樣方法 | DETERMINISTIC_AUTO_CHECKED | deterministic_choice | deterministic_auto_checked | deterministic | sampling_methods_classification_choice | deterministic_released | chap3 generator/router | test_b4_fullruntime_remaining_skills_mode_aware_paths.py | 已實作選擇判定 |
| 3 統計 | 3-1 統計的基本概念 | vh_數學B4_SamplingSurvey | 抽樣調查 | TEACHER_REVIEW | teacher_review | review_mode | teacher_review | sampling_survey_bias_review | review_shell_released,teacher_review_candidate | chap3 generator/router | test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py | review path |
| 3 統計 | 3-1 統計的基本概念 | vh_數學B4_StatisticalBasicConcepts | 統計的基本概念 | DETERMINISTIC_AUTO_CHECKED | deterministic_choice | deterministic_auto_checked | deterministic | statistical_basic_concepts_choice | deterministic_released | chap3 generator/router | test_b4_fullruntime_remaining_skills_mode_aware_paths.py | 已實作選擇判定 |
| 3 統計 | 3-2 統計資料整理 | vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | VISUAL_OR_HANDWRITING_AI_CHECKED | visual_or_handwriting_ai_checked | review_mode | teacher_review | cumulative_frequency_table_completion_review | blocked_by_textbook_fidelity,review_shell_released,future_ai_checked | chap3 generator/router + graph5 policy | test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py + test_b4_graph5_cumulative_or_next_visual_runtime_closed_loop.py | deterministic cumulative graph 仍 blocked |
| 3 統計 | 3-2 統計資料整理 | vh_數學B4_DataOrganizationAndCharts | 資料整理與圖表編製 | TEACHER_REVIEW | teacher_review | review_mode | teacher_review | data_organization_chart_selection_review | review_shell_released,teacher_review_candidate | chap3 generator/router | test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py | review path |
| 3 統計 | 3-2 統計資料整理 | vh_數學B4_FrequencyDistributionTableConstruction | 統計資料的次數分配表編製步驟 | VISUAL_OR_HANDWRITING_AI_CHECKED | visual_or_handwriting_ai_checked | handwriting_ai_checked | ai_assisted_review | table_completion_handwriting | handwriting_candidate,review_shell_released | chap3 generator/router | test_b4_fullruntime_remaining_skills_mode_aware_paths.py | 補表手寫題 |
| 3 統計 | 3-2 統計資料整理 | vh_數學B4_HistogramsAndFrequencyPolygons | 次數分配直方圖與次數分配折線圖的繪製 | PARTIAL_RUNTIME | visual_reading_with_short_answer | deterministic_auto_checked | deterministic | histogram_reading | partial_family_blocked,blocked_by_textbook_fidelity,deterministic_released | graph3 released + graph4 blocked | test_b4_graph3_histogram_runtime_closed_loop.py + test_b4_graph4_frequency_polygon_runtime_closed_loop.py | released: histogram / blocked: frequency_polygon |
| 3 統計 | 3-2 統計資料整理 | vh_數學B4_StatisticalChartReading | 統計圖表判讀 | VISIBILITY_ONLY | visibility_only | review_mode | visibility_only | statistical_chart_reading_visibility_review | blocked_by_textbook_fidelity,visibility_only_candidate,review_shell_released | chap3 generator/router + graph5 policy | test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py + test_b4_graph5_cumulative_or_next_visual_runtime_closed_loop.py | mixed_chart deterministic blocked |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_CentralTendencyMeasures | 集中趨勢量數 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | mean/median/mode + chart_mode_bar_reading + frequency_table_mean_reading | deterministic_released | chap3 registry | b4_phase7b_chap3_first_deterministic_runtime_ready_summary.md | 主線 deterministic |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_DispersionMeasures | 離散趨勢量數 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | range/percentile/quartile/iqr + chart_range_line_reading + frequency_table_range_reading | deterministic_released | chap3 registry | b4_phase7d_chap3_dispersion_measures_runtime_ready_summary.md | 主線 deterministic |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_LinearTransformationOfData | 資料的線性變換 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | linear_transform_mean/linear_transform_std_variance | deterministic_released | chap3 registry | b4_phase7b_chap3_first_deterministic_runtime_ready_summary.md | 主線 deterministic |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_NormalDistributionAndEmpiricalRule | 常態分配與經驗法則 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer | deterministic_auto_checked | deterministic | empirical_rule_interval_percentage | deterministic_released | chap3 generator/router | test_b4_fullruntime_remaining_skills_mode_aware_paths.py | FullRuntime-1 已實作 |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_OpinionPollInterpretation | 民意調查的解讀 | TEACHER_REVIEW | teacher_review | review_mode | teacher_review | opinion_poll_interpretation_review | teacher_review_candidate,review_shell_released | chap3 generator/router | test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py | review path |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_VarianceAndStandardDeviation | 變異數與標準差 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | variance_basic_numeric/standard_deviation_basic_numeric | deterministic_released | chap3 registry | b4_phase7b_chap3_first_deterministic_runtime_ready_summary.md | 主線 deterministic |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_WeightedMean | 加權平均數 | DETERMINISTIC_AUTO_CHECKED | deterministic_short_answer_or_choice | deterministic_auto_checked | deterministic | weighted_mean_basic | deterministic_released | chap3 registry | b4_phase7b_chap3_first_deterministic_runtime_ready_summary.md | 主線 deterministic |

## B. Category Count Summary

| metric | value |
|---|---:|
| total_b4_skills | 40 |
| deterministic_auto_checked_count | 31 |
| visual_or_handwriting_ai_checked_count | 4 |
| teacher_review_count | 3 |
| visibility_only_count | 1 |
| partial_runtime_count | 1 |
| sum_primary_categories | 40 |
| unknown_or_no_runtime_count | 0 |
| blocked_only_count | 0 |

## C. Deterministic Auto-checked Skills

- Chap1 deterministic 主線 13 skills（除 `TreeDiagramCounting`、`PascalTriangle`）
- Chap2 deterministic 主線 10 skills（含機率與期望值）
- Chap3 deterministic 8 skills：
  - `vh_數學B4_SamplingMethods` -> `sampling_methods_classification_choice`
  - `vh_數學B4_StatisticalBasicConcepts` -> `statistical_basic_concepts_choice`
  - `vh_數學B4_CentralTendencyMeasures`
  - `vh_數學B4_DispersionMeasures`
  - `vh_數學B4_LinearTransformationOfData`
  - `vh_數學B4_NormalDistributionAndEmpiricalRule` -> `empirical_rule_interval_percentage`
  - `vh_數學B4_VarianceAndStandardDeviation`
  - `vh_數學B4_WeightedMean`

## D. AI / Handwriting Checked Skills

- `vh_數學B4_TreeDiagramCounting`
- `vh_數學B4_FrequencyDistributionTableConstruction`
- `vh_數學B4_PascalTriangle`
- `vh_數學B4_CumulativeFrequencyTablesAndGraphs`

## E. Teacher Review / Visibility Only Skills

- Teacher review:
  - `vh_數學B4_SamplingSurvey`
  - `vh_數學B4_DataOrganizationAndCharts`
  - `vh_數學B4_OpinionPollInterpretation`
- Visibility only:
  - `vh_數學B4_StatisticalChartReading`

## F. Partial Runtime Skills

- `vh_數學B4_HistogramsAndFrequencyPolygons`
  - released: `histogram_reading`
  - blocked: `frequency_polygon_reading`
  - reason: textbook fidelity gate (`partial_family_blocked`)

## G. Blocked / Fidelity Gate Summary

- Graph-4:
  - `frequency_polygon_reading` blocked
- Graph-5:
  - `cumulative_frequency_graph_reading` deterministic blocked
  - `mixed_chart_interpretation` blocked

以上 blocked 項目皆已分流（future_ai_checked / teacher_review / visibility_only），**不屬於 unknown/no-runtime**。

## H. Final Closure Decision

1. B4 canonical 40 skills 已達 mode-aware runtime coverage（含 deterministic、AI/handwriting、teacher review、visibility、partial）。
2. unknown/no-runtime skill count 可歸零（`unknown_or_no_runtime_count = 0`）。
3. 建議停止 Graph deterministic short-answer 的硬挖掘，維持 textbook fidelity gate。
4. 下一步建議轉向：
   - admin coverage matrix
   - teacher-facing runtime category display
   - AI-checked / teacher-review UX polishing
   - final B4 release smoke

## Machine-readable Snapshot

```json
{
  "total_b4_skills": 40,
  "deterministic_auto_checked_count": 31,
  "visual_or_handwriting_ai_checked_count": 4,
  "teacher_review_count": 3,
  "visibility_only_count": 1,
  "partial_runtime_count": 1,
  "sum_primary_categories": 40,
  "unknown_or_no_runtime_count": 0,
  "blocked_only_count": 0,
  "partial_runtime_skills": [
    "vh_數學B4_HistogramsAndFrequencyPolygons"
  ],
  "blocked_items": [
    "frequency_polygon_reading",
    "cumulative_frequency_graph_reading",
    "mixed_chart_interpretation"
  ]
}
```
