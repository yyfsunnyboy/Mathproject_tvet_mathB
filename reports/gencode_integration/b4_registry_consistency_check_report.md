# B4 Generator Registry Consistency Check Report v0.1

## 1. 任務目的
本檢查器用來偵測 YAML registry 與 production code 間的 drift，確保盤點資訊準確。

## 2. 檢查來源
- configs/b4_generator_registry.v0.1.yaml
- core/vocational_math_b4/services/question_router.py
- core/vocational_math_b4/adaptive/allowlist.py
- core/routes/practice.py
- core/vocational_math_b4/domain/b4_validators.py

## 3. 總體統計
| metric | count |
|---|---|
| yaml_items | 87 |
| router_items | 86 |
| matched_items | 86 |
| missing_in_yaml | 0 |
| missing_in_router | 0 |
| adaptive_mismatch | 32 |
| manual_review_mismatch | 6 |
| suspicious_id | 0 |
| critical_errors | 0 |
| warnings | 38 |

## 4. Router 對照結果
所有 YAML 項目皆與 Router 一致。

## 5. Status 對照結果
| status | count |
|---|---|
| runtime_ready | 79 |
| manual_review | 7 |
| future_ai_judged | 1 |

## 6. Adaptive Allowlist 對照結果
| skill_id | chapter | yaml | actual |
|---|---|---|---|
| vh_數學B4_CentralTendencyMeasures | 3 | True | False |
| vh_數學B4_CentralTendencyMeasures | 3 | True | False |
| vh_數學B4_CentralTendencyMeasures | 3 | True | False |
| vh_數學B4_CentralTendencyMeasures | 3 | True | False |
| vh_數學B4_CentralTendencyMeasures | 3 | True | False |
| vh_數學B4_WeightedMean | 3 | True | False |
| vh_數學B4_VarianceAndStandardDeviation | 3 | True | False |
| vh_數學B4_VarianceAndStandardDeviation | 3 | True | False |
| vh_數學B4_LinearTransformationOfData | 3 | True | False |
| vh_數學B4_LinearTransformationOfData | 3 | True | False |
| vh_數學B4_DispersionMeasures | 3 | True | False |
| vh_數學B4_DispersionMeasures | 3 | True | False |
| vh_數學B4_DispersionMeasures | 3 | True | False |
| vh_數學B4_DispersionMeasures | 3 | True | False |
| vh_數學B4_DispersionMeasures | 3 | True | False |
| vh_數學B4_DispersionMeasures | 3 | True | False |
| vh_數學B4_HistogramsAndFrequencyPolygons | 3 | True | False |
| vh_數學B4_NormalDistributionAndEmpiricalRule | 3 | True | False |
| vh_數學B4_SamplingMethods | 3 | True | False |
| vh_數學B4_StatisticalBasicConcepts | 3 | True | False |
| vh_數學B4_FrequencyDistributionTableConstruction | 3 | True | False |
| vh_數學B4_SamplingSurvey | 3 | True | False |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | 3 | True | False |
| vh_數學B4_DataOrganizationAndCharts | 3 | True | False |
| vh_數學B4_DataOrganizationAndCharts | 3 | True | False |
| vh_數學B4_DataOrganizationAndCharts | 3 | True | False |
| vh_數學B4_DataOrganizationAndCharts | 3 | True | False |
| vh_數學B4_StatisticalChartReading | 3 | True | False |
| vh_數學B4_StatisticalChartReading | 3 | True | False |
| vh_數學B4_StatisticalChartReading | 3 | True | False |
| vh_數學B4_StatisticalChartReading | 3 | True | False |
| vh_數學B4_OpinionPollInterpretation | 3 | True | False |

## 7. Manual Review 對照結果
| skill_id | yaml | actual |
|---|---|---|---|
| vh_數學B4_FrequencyDistributionTableConstruction | True | False |
| vh_數學B4_SamplingSurvey | True | False |
| vh_數學B4_CumulativeFrequencyTablesAndGraphs | True | False |
| vh_數學B4_DataOrganizationAndCharts | True | False |
| vh_數學B4_StatisticalChartReading | True | False |
| vh_數學B4_OpinionPollInterpretation | True | False |

## 8. Suspicious ID / Typo 檢查
未偵測到可疑 ID。

## 9. 結論
### RESULT: PASS
可進 Phase 2。

## 10. 下一步建議
建議進 Phase 2：Agent Skill v2 規格包設計。
