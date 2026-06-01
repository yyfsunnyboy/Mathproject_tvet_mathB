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
- blocking=40, major=10, minor=0

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
| vh_數學B4_StatisticalBasicConcepts | statistical_basic_concepts_choice | choice_wrong_marked_correct | BLOCKING | 計算一組資料的平均數、中位數、標準差，用來描述這組資料的特性，屬於何者？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalBasicConcepts | statistical_basic_concepts_choice | choice_wrong_marked_correct | BLOCKING | 根據抽出的 200 位學生資料，推估全校學生平均身高，這屬於敘述統計或推論統計中的何者？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalBasicConcepts | statistical_basic_concepts_choice | choice_wrong_marked_correct | BLOCKING | 統計研究通常包含蒐集、整理、陳示、分析、解釋。取得原始資料屬於哪一步？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalBasicConcepts | statistical_basic_concepts_choice | choice_wrong_marked_correct | BLOCKING | 將問卷得到的原始資料分組並整理成一覽資料，屬於統計研究的哪一步？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalBasicConcepts | statistical_basic_concepts_choice | choice_wrong_marked_correct | BLOCKING | 把整理後資料畫成長條圖或折線圖，屬於統計研究的哪一步？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalBasicConcepts | statistical_basic_concepts_choice | choice_wrong_marked_correct | BLOCKING | 根據平均數與標準差比較兩組資料差異，屬於統計研究的哪一步？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalBasicConcepts | statistical_basic_concepts_choice | choice_wrong_marked_correct | BLOCKING | 根據分析結果說明可能原因並提出結論，屬於統計研究的哪一步？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalBasicConcepts | statistical_basic_concepts_choice | choice_wrong_marked_correct | BLOCKING | 若學校想了解全校學生通勤方式，直接詢問每一位學生，這屬於何者？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalBasicConcepts | statistical_basic_concepts_choice | choice_wrong_marked_correct | BLOCKING | 若學校只訪問部分學生來了解通勤方式，這屬於何者？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalBasicConcepts | statistical_basic_concepts_choice | choice_wrong_marked_correct | BLOCKING | 下列何者最能說明統計研究的主要目的？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_SamplingSurvey | sampling_survey_foundation_identification | choice_guarded_legacy_path | MAJOR | 某工廠共有 1200 件產品，品管抽查其中 80 件。下列何者是樣本數？請輸入選項代號。 | 此題型目前仍沿用 legacy guarded check path。 | 若要全 deterministic，需另行規劃 SamplingSurvey checker path migration。 | no |
| vh_數學B4_SamplingSurvey | sampling_survey_foundation_identification | choice_guarded_legacy_path | MAJOR | 某城市共有 5000 位機車族，研究者抽出其中 250 位填寫問卷。下列何者是樣本？請輸入選項代號。 | 此題型目前仍沿用 legacy guarded check path。 | 若要全 deterministic，需另行規劃 SamplingSurvey checker path migration。 | no |
| vh_數學B4_SamplingSurvey | sampling_survey_foundation_identification | choice_guarded_legacy_path | MAJOR | 某社區共有 3000 位住戶，抽出 150 位進行訪問。下列何者是母群體數？請輸入選項代號。 | 此題型目前仍沿用 legacy guarded check path。 | 若要全 deterministic，需另行規劃 SamplingSurvey checker path migration。 | no |
| vh_數學B4_SamplingSurvey | sampling_survey_foundation_identification | choice_guarded_legacy_path | MAJOR | 某社區共有 3000 位住戶，抽出 150 位進行訪問。下列何者是母群體數？請輸入選項代號。 | 此題型目前仍沿用 legacy guarded check path。 | 若要全 deterministic，需另行規劃 SamplingSurvey checker path migration。 | no |
| vh_數學B4_SamplingSurvey | sampling_survey_foundation_identification | choice_guarded_legacy_path | MAJOR | 某校共有 1800 位學生，研究者抽出 90 位做問卷。下列何者是樣本數？請輸入選項代號。 | 此題型目前仍沿用 legacy guarded check path。 | 若要全 deterministic，需另行規劃 SamplingSurvey checker path migration。 | no |
| vh_數學B4_SamplingSurvey | sampling_survey_foundation_identification | choice_guarded_legacy_path | MAJOR | 某校共有 1800 位學生，研究者抽出 90 位做問卷。下列何者是樣本數？請輸入選項代號。 | 此題型目前仍沿用 legacy guarded check path。 | 若要全 deterministic，需另行規劃 SamplingSurvey checker path migration。 | no |
| vh_數學B4_SamplingSurvey | sampling_survey_foundation_identification | choice_guarded_legacy_path | MAJOR | 學校調查午餐滿意度時，訪問全校每一位學生。這屬於下列何者？請輸入選項代號。 | 此題型目前仍沿用 legacy guarded check path。 | 若要全 deterministic，需另行規劃 SamplingSurvey checker path migration。 | no |
| vh_數學B4_SamplingSurvey | sampling_survey_foundation_identification | choice_guarded_legacy_path | MAJOR | 某社區共有 3000 位住戶，抽出 150 位進行訪問。下列何者是母群體數？請輸入選項代號。 | 此題型目前仍沿用 legacy guarded check path。 | 若要全 deterministic，需另行規劃 SamplingSurvey checker path migration。 | no |
| vh_數學B4_SamplingSurvey | sampling_survey_foundation_identification | choice_guarded_legacy_path | MAJOR | 某食品公司從當日生產的 2000 包餅乾中抽出 100 包檢驗。下列何者是樣本？請輸入選項代號。 | 此題型目前仍沿用 legacy guarded check path。 | 若要全 deterministic，需另行規劃 SamplingSurvey checker path migration。 | no |
| vh_數學B4_SamplingSurvey | sampling_survey_foundation_identification | choice_guarded_legacy_path | MAJOR | 某校共有 1800 位學生，研究者抽出 90 位做問卷。下列何者是樣本數？請輸入選項代號。 | 此題型目前仍沿用 legacy guarded check path。 | 若要全 deterministic，需另行規劃 SamplingSurvey checker path migration。 | no |
| vh_數學B4_SamplingMethods | sampling_methods_classification_choice | choice_wrong_marked_correct | BLOCKING | 學校要抽查學生問卷，先將全校學生編號後以抽籤方式抽出受訪者。這屬於哪一種抽樣方法？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_SamplingMethods | sampling_methods_classification_choice | choice_wrong_marked_correct | BLOCKING | 活動主辦單位把所有參加者名字放入箱中，隨機摸出若干人做滿意度訪談。這屬於哪一種抽樣方法？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_SamplingMethods | sampling_methods_classification_choice | choice_wrong_marked_correct | BLOCKING | 研究者先將名單編號，再用亂數表抽出樣本。這屬於哪一種抽樣方法？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_SamplingMethods | sampling_methods_classification_choice | choice_wrong_marked_correct | BLOCKING | 電話簿調查從第 10 個開始，每隔 5 個抽 1 個電話號碼檢查。這屬於哪一種抽樣方法？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_SamplingMethods | sampling_methods_classification_choice | choice_wrong_marked_correct | BLOCKING | 出版社檢查印刷品質時，從第 12 本開始，每隔 10 本抽 1 本。這屬於哪一種抽樣方法？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_SamplingMethods | sampling_methods_classification_choice | choice_wrong_marked_correct | BLOCKING | 交通調查時，從第 15 輛車開始，每隔 20 輛車攔檢一輛。這屬於哪一種抽樣方法？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_SamplingMethods | sampling_methods_classification_choice | choice_wrong_marked_correct | BLOCKING | 調查學生升學意向時，先按年級分層，再依各層人數比例抽樣。這屬於哪一種抽樣方法？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_SamplingMethods | sampling_methods_classification_choice | choice_wrong_marked_correct | BLOCKING | 調查通勤習慣時，先按性別分層，再依各層比例抽樣。這屬於哪一種抽樣方法？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_SamplingMethods | sampling_methods_classification_choice | choice_wrong_marked_correct | BLOCKING | 調查消費行為時，先按收入層級分層，再做比例抽樣。這屬於哪一種抽樣方法？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_SamplingMethods | sampling_methods_classification_choice | choice_wrong_marked_correct | BLOCKING | 研究者先抽出若干班級，再調查被抽中班級內所有學生。這屬於哪一種抽樣方法？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_DataOrganizationAndCharts | chart_type_selection_by_purpose | choice_wrong_marked_correct | BLOCKING | 某社團記錄一週每日到課人數，想觀察一週變化趨勢，最適合使用哪一種圖表？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_DataOrganizationAndCharts | chart_type_selection_by_purpose | choice_wrong_marked_correct | BLOCKING | 某社團記錄一週每日到課人數，想觀察一週變化趨勢，最適合使用哪一種圖表？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_DataOrganizationAndCharts | chart_type_selection_by_purpose | choice_wrong_marked_correct | BLOCKING | 某社團記錄一週每日到課人數，想觀察一週變化趨勢，最適合使用哪一種圖表？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_DataOrganizationAndCharts | chart_type_selection_by_purpose | choice_wrong_marked_correct | BLOCKING | 某社團記錄一週每日到課人數，想觀察一週變化趨勢，最適合使用哪一種圖表？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_DataOrganizationAndCharts | chart_usage_identification | choice_wrong_marked_correct | BLOCKING | 若資料目的是表達各類別在整體中的占比，最常使用哪一種圖表？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_DataOrganizationAndCharts | chart_usage_identification | choice_wrong_marked_correct | BLOCKING | 若資料目的是表達各類別在整體中的占比，最常使用哪一種圖表？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_DataOrganizationAndCharts | data_organization_first_step | choice_wrong_marked_correct | BLOCKING | 某社團記錄社員每日閱讀分鐘數，想先整理成可比較的資料，第一步應為何？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_DataOrganizationAndCharts | chart_type_selection_by_purpose | choice_wrong_marked_correct | BLOCKING | 某社團記錄一週每日到課人數，想觀察一週變化趨勢，最適合使用哪一種圖表？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_DataOrganizationAndCharts | data_organization_first_step | choice_wrong_marked_correct | BLOCKING | 某社團記錄社員每日閱讀分鐘數，想先整理成可比較的資料，第一步應為何？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_DataOrganizationAndCharts | chart_usage_identification | choice_wrong_marked_correct | BLOCKING | 若資料目的是表達各類別在整體中的占比，最常使用哪一種圖表？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_wrong_marked_correct | BLOCKING | 下列哪一項是閱讀折線圖時最應注意的事項？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_match_data_type | choice_wrong_marked_correct | BLOCKING | 老師記錄各班（甲、乙、丙、丁班）期中考的平均分數，想用圖表呈現各班分數高低的比較。下列哪種圖表最合適？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_type_by_purpose | choice_wrong_marked_correct | BLOCKING | 學校要比較甲、乙、丙三班參加課外活動的人數差異，最適合使用哪一種統計圖表？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_wrong_marked_correct | BLOCKING | 下列哪一項是閱讀折線圖時最應注意的事項？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_match_data_type | choice_wrong_marked_correct | BLOCKING | 學生會統計全校學生最喜愛的社團類型（體育、學術、藝術、服務），想呈現各類型所占的百分比。下列哪種圖表最合適？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_type_by_purpose | choice_wrong_marked_correct | BLOCKING | 某社團記錄一週每日到課人數，想觀察資料隨時間的變化趨勢，最適合使用哪一種統計圖表？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_wrong_marked_correct | BLOCKING | 某調查只詢問了 10 個人的意見就宣稱『多數人喜歡A品牌』。這個結論最可能存在什麼問題？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_match_data_type | choice_wrong_marked_correct | BLOCKING | 老師記錄各班（甲、乙、丙、丁班）期中考的平均分數，想用圖表呈現各班分數高低的比較。下列哪種圖表最合適？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_type_by_purpose | choice_wrong_marked_correct | BLOCKING | 老師想呈現全班段考分數在各分數區間（如 60-69、70-79）的人數分布情形，最適合使用哪一種統計圖表？請輸入選項代號。 | ?????? | ?? checker ????? | no |
| vh_數學B4_StatisticalChartReading | chart_interpretation_caution | choice_wrong_marked_correct | BLOCKING | 統計圖顯示『冰淇淋銷量』與『溺水人數』在夏季都上升。下列推論何者正確？請輸入選項代號。 | ?????? | ?? checker ????? | no |