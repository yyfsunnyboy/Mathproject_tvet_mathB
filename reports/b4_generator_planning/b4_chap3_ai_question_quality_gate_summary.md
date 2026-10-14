# B4 Chap3 AI-assisted Question Quality Gate Summary

## 1. QA scope
- Phase B4-Chap3-QA-1
- Rule-based QA + diversity QA + visual/table artifact QA
- AI judge status: AI_JUDGE_NOT_RUN

## 2. sampled skills
- vh_數學B4_StatisticalBasicConcepts
- vh_數學B4_SamplingSurvey
- vh_數學B4_SamplingMethods
- vh_數學B4_DataOrganizationAndCharts
- vh_數學B4_StatisticalChartReading
- vh_數學B4_CumulativeFrequencyTablesAndGraphs
- vh_數學B4_FrequencyDistributionTableConstruction
- vh_數學B4_HistogramsAndFrequencyPolygons
- vh_數學B4_CentralTendencyMeasures
- vh_數學B4_DispersionMeasures
- vh_數學B4_WeightedMean
- vh_數學B4_VarianceAndStandardDeviation
- vh_數學B4_LinearTransformationOfData
- vh_數學B4_NormalDistributionAndEmpiricalRule

## 3. sample count per skill
| skill_id | sample_count |
|---|---:|
| vh_數學B4_StatisticalBasicConcepts | 10 |
| vh_數學B4_SamplingSurvey | 10 |
| vh_數學B4_SamplingMethods | 10 |
| vh_數學B4_DataOrganizationAndCharts | 10 |
| vh_數學B4_StatisticalChartReading | 10 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 10 |
| vh_數學B4_FrequencyDistributionTableConstruction | 10 |
| vh_數學B4_HistogramsAndFrequencyPolygons | 10 |
| vh_數學B4_CentralTendencyMeasures | 10 |
| vh_數學B4_DispersionMeasures | 10 |
| vh_數學B4_WeightedMean | 10 |
| vh_數學B4_VarianceAndStandardDeviation | 10 |
| vh_數學B4_LinearTransformationOfData | 10 |
| vh_數學B4_NormalDistributionAndEmpiricalRule | 10 |
| TOTAL | 140 |

## 4. rule-based QA summary
- blocking=23, major=9, minor=0

## 5. diversity QA summary
| skill_id | unique problem_type_id | unique scenario_family | unique scenario_id | unique question_pattern_hash | repeated_question_text_ratio |
|---|---:|---:|---:|---:|---:|
| vh_數學B4_StatisticalBasicConcepts | 1 | 1 | 10 | 10 | 0.0 |
| vh_數學B4_SamplingSurvey | 1 | 1 | 6 | 6 | 0.4 |
| vh_數學B4_SamplingMethods | 1 | 1 | 10 | 10 | 0.0 |
| vh_數學B4_DataOrganizationAndCharts | 3 | 3 | 3 | 3 | 0.7 |
| vh_數學B4_StatisticalChartReading | 3 | 3 | 8 | 8 | 0.2 |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 1 | 1 | 9 | 4 | 0.6 |
| vh_數學B4_FrequencyDistributionTableConstruction | 1 | 1 | 9 | 10 | 0.0 |
| vh_數學B4_HistogramsAndFrequencyPolygons | 1 | 1 | 9 | 5 | 0.5 |
| vh_數學B4_CentralTendencyMeasures | 5 | 1 | 0 | 8 | 0.2 |
| vh_數學B4_DispersionMeasures | 5 | 0 | 0 | 8 | 0.2 |
| vh_數學B4_WeightedMean | 1 | 0 | 0 | 10 | 0.0 |
| vh_數學B4_VarianceAndStandardDeviation | 2 | 0 | 0 | 9 | 0.1 |
| vh_數學B4_LinearTransformationOfData | 2 | 0 | 0 | 10 | 0.0 |
| vh_數學B4_NormalDistributionAndEmpiricalRule | 5 | 1 | 5 | 7 | 0.3 |

## 6. AI judge QA summary
- AI_JUDGE_NOT_RUN
- offline rubric fields collected in rule-based/deterministic/review contracts.

## 7. visual/table sample artifact paths
- reports/b4_generator_planning/chap3_quality_samples/CentralTendencyMeasures_sample_01.json
- reports/b4_generator_planning/chap3_quality_samples/CentralTendencyMeasures_sample_01.png
- reports/b4_generator_planning/chap3_quality_samples/CentralTendencyMeasures_sample_03.json
- reports/b4_generator_planning/chap3_quality_samples/CentralTendencyMeasures_sample_03.png
- reports/b4_generator_planning/chap3_quality_samples/CumulativeFrequencyTablesAndGraphs_sample_01.json
- reports/b4_generator_planning/chap3_quality_samples/CumulativeFrequencyTablesAndGraphs_sample_01.png
- reports/b4_generator_planning/chap3_quality_samples/CumulativeFrequencyTablesAndGraphs_sample_03.json
- reports/b4_generator_planning/chap3_quality_samples/CumulativeFrequencyTablesAndGraphs_sample_03.png
- reports/b4_generator_planning/chap3_quality_samples/DispersionMeasures_sample_01.json
- reports/b4_generator_planning/chap3_quality_samples/DispersionMeasures_sample_01.png
- reports/b4_generator_planning/chap3_quality_samples/DispersionMeasures_sample_03.json
- reports/b4_generator_planning/chap3_quality_samples/DispersionMeasures_sample_03.png
- reports/b4_generator_planning/chap3_quality_samples/HistogramsAndFrequencyPolygons_sample_01.json
- reports/b4_generator_planning/chap3_quality_samples/HistogramsAndFrequencyPolygons_sample_01.png
- reports/b4_generator_planning/chap3_quality_samples/HistogramsAndFrequencyPolygons_sample_03.json
- reports/b4_generator_planning/chap3_quality_samples/HistogramsAndFrequencyPolygons_sample_03.png

## 8. failed items table
| skill_id | problem_type_id | issue_type | severity | sample_question_text | reason | suggested_fix | fixed_in_this_phase |
|---|---|---|---|---|---|---|---|
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_wrong_marked_correct | BLOCKING | 下列哪一項是閱讀折線圖時最應注意的事項？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_match_data_type | choice_correct_not_accepted | BLOCKING | 老師記錄各班（甲、乙、丙、丁班）期中考的平均分數，想用圖表呈現各班分數高低的比較。下列哪種圖表最合適？請輸入選項代號。 | ?????? | ?? deterministic checker ? alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_match_data_type | choice_alias_not_accepted | MAJOR | 老師記錄各班（甲、乙、丙、丁班）期中考的平均分數，想用圖表呈現各班分數高低的比較。下列哪種圖表最合適？請輸入選項代號。 | A/B/C/D alias ????? | ?? choice alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_type_by_purpose | choice_correct_not_accepted | BLOCKING | 學校要比較甲、乙、丙三班參加課外活動的人數差異，最適合使用哪一種統計圖表？請輸入選項代號。 | ?????? | ?? deterministic checker ? alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_type_by_purpose | choice_alias_not_accepted | MAJOR | 學校要比較甲、乙、丙三班參加課外活動的人數差異，最適合使用哪一種統計圖表？請輸入選項代號。 | A/B/C/D alias ????? | ?? choice alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_correct_not_accepted | BLOCKING | 下列哪一項是閱讀折線圖時最應注意的事項？請輸入選項代號。 | ?????? | ?? deterministic checker ? alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_alias_not_accepted | MAJOR | 下列哪一項是閱讀折線圖時最應注意的事項？請輸入選項代號。 | A/B/C/D alias ????? | ?? choice alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_match_data_type | choice_correct_not_accepted | BLOCKING | 學生會統計全校學生最喜愛的社團類型（體育、學術、藝術、服務），想呈現各類型所占的百分比。下列哪種圖表最合適？請輸入選項代號。 | ?????? | ?? deterministic checker ? alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_match_data_type | choice_alias_not_accepted | MAJOR | 學生會統計全校學生最喜愛的社團類型（體育、學術、藝術、服務），想呈現各類型所占的百分比。下列哪種圖表最合適？請輸入選項代號。 | A/B/C/D alias ????? | ?? choice alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_type_by_purpose | choice_correct_not_accepted | BLOCKING | 某社團記錄一週每日到課人數，想觀察資料隨時間的變化趨勢，最適合使用哪一種統計圖表？請輸入選項代號。 | ?????? | ?? deterministic checker ? alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_type_by_purpose | choice_alias_not_accepted | MAJOR | 某社團記錄一週每日到課人數，想觀察資料隨時間的變化趨勢，最適合使用哪一種統計圖表？請輸入選項代號。 | A/B/C/D alias ????? | ?? choice alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_correct_not_accepted | BLOCKING | 某調查只詢問了 10 個人的意見就宣稱『多數人喜歡A品牌』。這個結論最可能存在什麼問題？請輸入選項代號。 | ?????? | ?? deterministic checker ? alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_alias_not_accepted | MAJOR | 某調查只詢問了 10 個人的意見就宣稱『多數人喜歡A品牌』。這個結論最可能存在什麼問題？請輸入選項代號。 | A/B/C/D alias ????? | ?? choice alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_wrong_marked_correct | BLOCKING | 某調查只詢問了 10 個人的意見就宣稱『多數人喜歡A品牌』。這個結論最可能存在什麼問題？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_match_data_type | choice_correct_not_accepted | BLOCKING | 老師記錄各班（甲、乙、丙、丁班）期中考的平均分數，想用圖表呈現各班分數高低的比較。下列哪種圖表最合適？請輸入選項代號。 | ?????? | ?? deterministic checker ? alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_match_data_type | choice_alias_not_accepted | MAJOR | 老師記錄各班（甲、乙、丙、丁班）期中考的平均分數，想用圖表呈現各班分數高低的比較。下列哪種圖表最合適？請輸入選項代號。 | A/B/C/D alias ????? | ?? choice alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_match_data_type | choice_wrong_marked_correct | BLOCKING | 老師記錄各班（甲、乙、丙、丁班）期中考的平均分數，想用圖表呈現各班分數高低的比較。下列哪種圖表最合適？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_type_by_purpose | choice_correct_not_accepted | BLOCKING | 老師想呈現全班段考分數在各分數區間（如 60-69、70-79）的人數分布情形，最適合使用哪一種統計圖表？請輸入選項代號。 | ?????? | ?? deterministic checker ? alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_type_by_purpose | choice_alias_not_accepted | MAJOR | 老師想呈現全班段考分數在各分數區間（如 60-69、70-79）的人數分布情形，最適合使用哪一種統計圖表？請輸入選項代號。 | A/B/C/D alias ????? | ?? choice alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_correct_not_accepted | BLOCKING | 統計圖顯示『冰淇淋銷量』與『溺水人數』在夏季都上升。下列推論何者正確？請輸入選項代號。 | ?????? | ?? deterministic checker ? alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_alias_not_accepted | MAJOR | 統計圖顯示『冰淇淋銷量』與『溺水人數』在夏季都上升。下列推論何者正確？請輸入選項代號。 | A/B/C/D alias ????? | ?? choice alias normalize? | no |
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_wrong_marked_correct | BLOCKING | 統計圖顯示『冰淇淋銷量』與『溺水人數』在夏季都上升。下列推論何者正確？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_table_completion_review | review_guard_missing | BLOCKING | 下表為身高區間（公分）的累積次數分配表，請補上空格中的累積次數，並簡述你的計算方式。 | review 題未被 guard 到 AI/Review。 | 修正 check_mode guard。 | no |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_table_completion_review | review_guard_missing | BLOCKING | 下表為分數區間的累積次數分配表，請補上空格中的累積次數，並簡述你的計算方式。 | review 題未被 guard 到 AI/Review。 | 修正 check_mode guard。 | no |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_table_completion_review | review_guard_missing | BLOCKING | 下表為身高區間（公分）的累積次數分配表，請補上空格中的累積次數，並簡述你的計算方式。 | review 題未被 guard 到 AI/Review。 | 修正 check_mode guard。 | no |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_table_completion_review | review_guard_missing | BLOCKING | 下表為身高區間（公分）的累積次數分配表，請補上空格中的累積次數，並簡述你的計算方式。 | review 題未被 guard 到 AI/Review。 | 修正 check_mode guard。 | no |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_table_completion_review | review_guard_missing | BLOCKING | 下表為時間區間（分鐘）的累積次數分配表，請補上空格中的累積次數，並簡述你的計算方式。 | review 題未被 guard 到 AI/Review。 | 修正 check_mode guard。 | no |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_table_completion_review | review_guard_missing | BLOCKING | 下表為分數區間的累積次數分配表，請補上空格中的累積次數，並簡述你的計算方式。 | review 題未被 guard 到 AI/Review。 | 修正 check_mode guard。 | no |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_table_completion_review | review_guard_missing | BLOCKING | 下表為時間區間（分鐘）的累積次數分配表，請補上空格中的累積次數，並簡述你的計算方式。 | review 題未被 guard 到 AI/Review。 | 修正 check_mode guard。 | no |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_table_completion_review | review_guard_missing | BLOCKING | 下表為身高區間（公分）的累積次數分配表，請補上空格中的累積次數，並簡述你的計算方式。 | review 題未被 guard 到 AI/Review。 | 修正 check_mode guard。 | no |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_table_completion_review | review_guard_missing | BLOCKING | 下表為銷售量區間（件）的累積次數分配表，請補上空格中的累積次數，並簡述你的計算方式。 | review 題未被 guard 到 AI/Review。 | 修正 check_mode guard。 | no |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | cumulative_frequency_table_completion_review | review_guard_missing | BLOCKING | 下表為分數區間的累積次數分配表，請補上空格中的累積次數，並簡述你的計算方式。 | review 題未被 guard 到 AI/Review。 | 修正 check_mode guard。 | no |