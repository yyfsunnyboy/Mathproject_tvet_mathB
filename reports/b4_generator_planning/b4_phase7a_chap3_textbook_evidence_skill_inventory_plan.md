# B4 Chapter 3 Phase 7A：Textbook Evidence and Skill Inventory Planning

## 1. Scope and Guardrails
本輪僅做 Chap3 規劃文件，不做 implementation。

- 不改 code
- 不改 tests
- 不改 DB
- 不寫 generator
- 不接 adaptive
- 不新增 SOP

## 2. Chap3 Textbook Evidence Summary
資料來源：
- `reports/b4_generator_planning/b4_skill_source_summary.csv`
- `reports/b4_generator_planning/b4_data_quality_review.md`

| source_chapter | source_section | skill_id | skill_name | source_type evidence (textbook_example / in_class_practice / self_assessment) | textbook_example count | in_class_practice count | self_assessment count | risk summary |
|---|---|---|---|---|---:|---:|---:|---|
| 3 統計 | 3-1 統計的基本概念 | vh_數學B4_SamplingMethods | 抽樣方法 | available | 1 | 1 | 3 | needs_review 比例高；多題含表格語境 |
| 3 統計 | 3-1 統計的基本概念 | vh_數學B4_SamplingSurvey | 抽樣調查 | insufficient (無三類主來源題) | 0 | 0 | 0 | 僅教材練習來源，且缺標準答案風險 |
| 3 統計 | 3-1 統計的基本概念 | vh_數學B4_StatisticalBasicConcepts | 統計的基本概念 | missing | 0 | 0 | 0 | total_question_count=0，需補教材 |
| 3 統計 | 3-2 統計資料整理 | vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | available | 1 | 2 | 0 | 圖片/折線圖/表格依賴高；needs_review 高 |
| 3 統計 | 3-2 統計資料整理 | vh_數學B4_DataOrganizationAndCharts | 資料整理與圖表編製 | insufficient | 0 | 0 | 0 | 主要為圖表判讀語境，主來源不足 |
| 3 統計 | 3-2 統計資料整理 | vh_數學B4_FrequencyDistributionTableConstruction | 統計資料的次數分配表編製步驟 | available | 1 | 1 | 0 | 表格依賴高；needs_review 高 |
| 3 統計 | 3-2 統計資料整理 | vh_數學B4_HistogramsAndFrequencyPolygons | 次數分配直方圖與次數分配折線圖的繪製 | available | 1 | 1 | 0 | 直方圖/折線圖/圖片依賴高 |
| 3 統計 | 3-2 統計資料整理 | vh_數學B4_StatisticalChartReading | 統計圖表判讀 | available (僅 self_assessment) | 0 | 0 | 3 | 圖表依賴高、答案可驗證性低 |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_CentralTendencyMeasures | 集中趨勢量數 | available | 3 | 1 | 4 | 可拆為純數值 deterministic 子題；部分題含表格 |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_DispersionMeasures | 離散趨勢量數 | available | 1 | 1 | 2 | 可拆純數值 deterministic；部分題答案缺漏風險 |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_LinearTransformationOfData | 資料的線性變換 | available | 1 | 1 | 4 | needs_review 高；formula_missing 風險 |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_NormalDistributionAndEmpiricalRule | 常態分配與經驗法則 | available | 1 | 1 | 2 | 部分題依賴圖形語境；可切出純比例推估子題 |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_OpinionPollInterpretation | 民意調查的解讀 | available | 1 | 1 | 0 | 偏語意判讀題，deterministic 需題型限縮 |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_VarianceAndStandardDeviation | 變異數與標準差 | available | 1 | 1 | 1 | 具純數值計算潛力 |
| 3 統計 | 3-3 統計量分析 | vh_數學B4_WeightedMean | 加權平均數 | available | 1 | 1 | 0 | 可直接做 deterministic 計算題 |

## 3. Chap3 Skill Inventory

| section | skill_id | skill_name | textbook evidence count | likely problem families | deterministic suitability | notes |
|---|---|---|---:|---|---|---|
| 3-1 統計的基本概念 | vh_數學B4_SamplingMethods | 抽樣方法 | 5 | sampling_method_identification | needs_textbook_alignment | 多為分類判斷，需先固定選項語意 |
| 3-1 統計的基本概念 | vh_數學B4_SamplingSurvey | 抽樣調查 | 0 (主來源) | population_sample_mapping | manual_review | 主來源不足，先不進第一批 |
| 3-1 統計的基本概念 | vh_數學B4_StatisticalBasicConcepts | 統計的基本概念 | 0 | terminology_understanding | not_suitable_now | evidence missing |
| 3-2 統計資料整理 | vh_數學B4_CumulativeFrequencyTablesAndGraphs | 累積次數分配表與累積次數分配折線圖 | 3 | cumulative_reading_numeric | future_ai_judged | 圖表依賴高 |
| 3-2 統計資料整理 | vh_數學B4_DataOrganizationAndCharts | 資料整理與圖表編製 | 0 (主來源) | chart_conversion_interpretation | future_ai_judged | 圖表/圖片依賴 |
| 3-2 統計資料整理 | vh_數學B4_FrequencyDistributionTableConstruction | 統計資料的次數分配表編製步驟 | 2 | grouped_table_building | future_ai_judged | 需完整表格輸出 |
| 3-2 統計資料整理 | vh_數學B4_HistogramsAndFrequencyPolygons | 次數分配直方圖與次數分配折線圖的繪製 | 2 | histogram_polygon_drawing | future_ai_judged | 畫圖需求 |
| 3-2 統計資料整理 | vh_數學B4_StatisticalChartReading | 統計圖表判讀 | 0 (textbook/in_class) | chart_reading_multi_step | manual_review | 來源多為 self_assessment 圖題 |
| 3-3 統計量分析 | vh_數學B4_CentralTendencyMeasures | 集中趨勢量數 | 8 | mean_median_mode_numeric | ready_candidate | 可先做純數值題型 |
| 3-3 統計量分析 | vh_數學B4_DispersionMeasures | 離散趨勢量數 | 4 | range_variance_sd_numeric | ready_candidate | 先避開圖表題 |
| 3-3 統計量分析 | vh_數學B4_LinearTransformationOfData | 資料的線性變換 | 6 | linear_transform_mean_sd | ready_candidate | 題幹可模板化；需避免缺公式題 |
| 3-3 統計量分析 | vh_數學B4_NormalDistributionAndEmpiricalRule | 常態分配與經驗法則 | 4 | empirical_rule_percentage | needs_textbook_alignment | 限縮為已給平均與標準差之比例估算 |
| 3-3 統計量分析 | vh_數學B4_OpinionPollInterpretation | 民意調查的解讀 | 2 | poll_error_margin_basic | needs_textbook_alignment | 需明確封閉型問法 |
| 3-3 統計量分析 | vh_數學B4_VarianceAndStandardDeviation | 變異數與標準差 | 3 | variance_sd_computation | ready_candidate | 可做整數/分數答案檢核 |
| 3-3 統計量分析 | vh_數學B4_WeightedMean | 加權平均數 | 2 | weighted_mean_numeric | ready_candidate | 高確定性 deterministic |

## 4. Problem Type Candidate Taxonomy

| skill_id | problem_type_candidate | answer_type | checker_candidate | deterministic_ready | risk | notes |
|---|---|---|---|---|---|---|
| vh_數學B4_SamplingMethods | sampling_method_classification_choice | choice | exact_choice_match | partial | 語意歧義 | 選項需固定術語 |
| vh_數學B4_SamplingSurvey | population_sample_mapping_choice | choice | exact_choice_match | no | evidence不足 | 先保留 |
| vh_數學B4_StatisticalBasicConcepts | stats_term_identification_choice | choice | exact_choice_match | no | 無教材題 | 先保留 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_count_from_table | table_value | numeric_exact | no | 圖表依賴 | 保留給 AI-judged |
| vh_數學B4_DataOrganizationAndCharts | chart_interpretation_ratio | decimal_tolerance | tolerance_checker | no | 圖片依賴 | 保留 |
| vh_數學B4_FrequencyDistributionTableConstruction | grouped_frequency_fill_blank | table_value | table_cell_checker | no | 需整表作答 | reserved |
| vh_數學B4_HistogramsAndFrequencyPolygons | histogram_to_frequency_value | table_value | numeric_exact | no | 需讀圖/作圖 | reserved |
| vh_數學B4_StatisticalChartReading | chart_reading_choice | choice | exact_choice_match | no | 圖片依賴 | reserved |
| vh_數學B4_CentralTendencyMeasures | arithmetic_mean_from_list | rational_fraction | fraction_or_decimal_checker | yes | 低 | 首批候選 |
| vh_數學B4_CentralTendencyMeasures | median_from_ordered_or_unordered_data | integer | numeric_exact | yes | 低 | 首批候選 |
| vh_數學B4_CentralTendencyMeasures | mode_identification_numeric | integer | numeric_exact | yes | 低 | 首批候選 |
| vh_數學B4_DispersionMeasures | range_computation | integer | numeric_exact | yes | 低 | 首批候選 |
| vh_數學B4_DispersionMeasures | standard_deviation_basic_numeric | decimal_tolerance | tolerance_checker | partial | 中 | 先控制數值規模 |
| vh_數學B4_LinearTransformationOfData | transformed_mean_from_linear_rule | decimal_tolerance | tolerance_checker | yes | 中 | 需排除題文不完整 |
| vh_數學B4_LinearTransformationOfData | transformed_sd_from_scaling_rule | decimal_tolerance | tolerance_checker | yes | 中 | 需定義絕對值規則 |
| vh_數學B4_NormalDistributionAndEmpiricalRule | empirical_rule_interval_percentage | expected_value | numeric_exact_or_tolerance | partial | 中 | 限封閉型模板 |
| vh_數學B4_OpinionPollInterpretation | poll_margin_basic_numeric | decimal_tolerance | tolerance_checker | partial | 中 | 需固定題目結構 |
| vh_數學B4_VarianceAndStandardDeviation | variance_from_small_dataset | rational_fraction | fraction_or_decimal_checker | yes | 中 | 控制樣本數 |
| vh_數學B4_VarianceAndStandardDeviation | standard_deviation_from_variance | decimal_tolerance | tolerance_checker | yes | 中 | 小數容忍 |
| vh_數學B4_WeightedMean | weighted_mean_from_frequency_table_numeric | rational_fraction | fraction_or_decimal_checker | yes | 低 | 首批候選 |

## 5. Reserved / Future AI-judged 題型
以下題型本階段不應進 deterministic：

- 需要畫圖（直方圖、折線圖、頻率多邊形）
- 需要完整填表（次數分配表、累積次數表）
- 需要手寫過程
- 需要圖表判讀（圖片依賴）
- 需要開放式說明
- textbook image/chart dependent 題目

政策：
- reserved
- visibility-only
- 不進 deterministic allowlist
- 不進 mastery / APR
- 未來 AI-judged 再另開 phase

## 6. First Runtime-ready Batch Proposal
建議第一批：只做高確定性純數值統計量題型。

| proposed_phase | skill_id | problem_type | reason | risk |
|---|---|---|---|---|
| Phase 7B：Chap3 First Deterministic Runtime-ready Batch | vh_數學B4_CentralTendencyMeasures | arithmetic_mean_from_list | 題型穩定、檢核明確 | 低 |
| Phase 7B：Chap3 First Deterministic Runtime-ready Batch | vh_數學B4_CentralTendencyMeasures | median_from_ordered_or_unordered_data | 可 deterministic 檢核 | 低 |
| Phase 7B：Chap3 First Deterministic Runtime-ready Batch | vh_數學B4_CentralTendencyMeasures | mode_identification_numeric | 可 deterministic 檢核 | 低 |
| Phase 7B：Chap3 First Deterministic Runtime-ready Batch | vh_數學B4_WeightedMean | weighted_mean_from_frequency_table_numeric | 核心技能且可公式化 | 低 |
| Phase 7B：Chap3 First Deterministic Runtime-ready Batch | vh_數學B4_VarianceAndStandardDeviation | variance_from_small_dataset | 可控資料規模 | 中 |
| Phase 7B：Chap3 First Deterministic Runtime-ready Batch | vh_數學B4_VarianceAndStandardDeviation | standard_deviation_from_variance | checker 明確 | 中 |
| Phase 7B：Chap3 First Deterministic Runtime-ready Batch | vh_數學B4_LinearTransformationOfData | transformed_mean_from_linear_rule | 與既有教材語境一致 | 中 |
| Phase 7B：Chap3 First Deterministic Runtime-ready Batch | vh_數學B4_LinearTransformationOfData | transformed_sd_from_scaling_rule | 可封閉型檢核 | 中 |

## 7. Testing / Smoke Gate Plan
Phase 7B 預計測試：

- generator tests（題幹結構、答案可解性）
- checker tests（整數/分數/小數容忍）
- router / allowlist tests（僅啟用 7B 題型）
- `/practice` integration
- `/get_next_question`
- `/check_answer`
- encoded / decoded skill_id
- not-enabled UX
- reserved blocked
- Chap2 regression
- Chap1 regression

本輪不新增 tests。

## 8. Relation to Adaptive Practice
Chap3 本輪僅規劃 deterministic coverage，不接 adaptive_practice。
待 Chap3 deterministic runtime-ready mainline 穩定後，再開新 phase 規劃 chapter mode adaptive integration。

## 9. Recommended Next Phase
建議下一步：`Phase 7B：Chap3 First Deterministic Runtime-ready Batch`

- 使用 Template B
- 直接 runtime-ready implementation batch
- 優先做高確定性純數值題型
- 若執行前發現 textbook evidence 對應不足或題幹不可封閉檢核，則依 SOP BLOCK

## 10. Final Confirmation

- 是否只新增 planning report：是
- 是否修改 production code：否
- 是否修改 tests：否
- 是否修改 DB：否
- 是否新增 generator：否
- 是否修改 adaptive scoring / mastery / APR / PPO：否
- 是否啟動 implementation：否
- 是否新增 SOP：否
