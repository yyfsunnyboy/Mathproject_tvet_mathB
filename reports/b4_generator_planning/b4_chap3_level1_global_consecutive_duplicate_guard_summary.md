# B4 Chap3 Level1 Global Consecutive Duplicate Guard Summary

## 1. 問題描述
Chap3 多個 Level 1 skill 在 bare skill default route 仍可能出現相鄰重複題（相同題幹/相同 scenario/相同參數簽章）。

## 2. Root Cause
1. 先前避重是 skill-by-skill 修補，缺少 Chap3 Level 1 的全域相鄰避重機制。
2. route 層沒有統一比對 `question_text / scenario_id / parameter_signature / pattern/hash`。
3. fallback/retry 缺少一致化 debug 記錄欄位。

## 3. 全域 guard 設計
在 `core/routes/practice.py` 的 Chap3 runtime path 新增 Level 1 default 全域 guard：
- 適用：Chap3 canonical skill（deterministic/mixed）
- 比對鍵：
  - `question_text`
  - `scenario_id`
  - `parameter_signature`
  - `question_pattern_id`
  - `table_spec_hash`
  - `chart_spec_hash`
  - `visual_asset_hash`
- 若相同則重抽，最多 retry 3 次
- 在 `router_trace` 記錄：
  - `duplicate_guard_attempted=true`
  - `duplicate_guard_retry_count`
  - `duplicate_guard_fallback_reason`（若觸發）

## 4. 適用 skill 清單
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

## 5. metadata 補強情況
- 先前修補已逐步補齊 `scenario_id` 與 `parameter_signature`（SamplingSurvey / DataOrganization / SamplingMethods）。
- visual/table 題型已有 `table_spec_hash` / `chart_spec_hash` 補強路徑。
- 若無上述 metadata，仍可由 `question_text` 避重。

## 6. 每個 skill 連續 20 題結果（目標）
每個 skill 目標指標：
- `unique_question_text_count`：提高
- `consecutive_duplicate_question_text_count = 0`
- `consecutive_duplicate_scenario_id_count = 0`（若有 scenario_id）
- `consecutive_duplicate_parameter_signature_count = 0`（若有 parameter_signature）
- `fallback_count` 盡量為 0（若 >0 需記錄原因）

> 本地環境無法執行 pytest，以下為測試目標，待可執行環境驗證。

## 7. no-open-ended fallback regression 結果
- 全域 guard 不允許 Level 1 default 因避重重抽而退回 open-ended 題（deterministic/mixed skill）。

## 8. known regression cases 結果
- SamplingSurvey 2000/100 題不得相鄰重複（目標）
- DataOrganization 占比題不得相鄰重複（目標）
- StatisticalBasicConcepts 不退回固定 3 題輪播（目標）
- SamplingMethods 不退回固定數字輪播（目標）

## 9. 修改檔案
1. `core/routes/practice.py`
2. `tests/test_b4_chap3_level1_global_consecutive_duplicate_guard.py`

## 10. 新增 tests
- `tests/test_b4_chap3_level1_global_consecutive_duplicate_guard.py`

## 11. 測試結果
- `TEST_NOT_RUN_ENV_BLOCKED`
- 本環境缺少可用 `pytest/python/py`。

## 12. 是否影響 B4 final coverage count
- 不影響。只加全域 route guard 與測試，未改 runtime coverage category。

## 13. final status
- `READY_FOR_RECHECK`
