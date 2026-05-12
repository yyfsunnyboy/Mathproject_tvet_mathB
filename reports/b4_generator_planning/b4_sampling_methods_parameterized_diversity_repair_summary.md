# B4 SamplingMethods Parameterized Diversity Repair Summary

## 1. 問題描述

`vh_數學B4_SamplingMethods` 題型雖貼近課本，但人工實測出現固定情境與固定數字重複，常見題幹在少數模板間輪替，無法滿足實際出題多樣性需求。

## 2. root cause

- 原 generator 以少量固定 scenario 為主，數值幾乎不變。
- 系統抽樣間距與分層比例分配沒有參數池，導致數字長期固定。
- scenario metadata 只有基本 `scenario_id`，缺少可用於 QA 的 `parameter_signature`。

## 3. textbook-bounded parameterization 原則

- 僅在 B4 3-1 抽樣方法骨架內做變化：
  - 簡單隨機抽樣
  - 系統抽樣
  - 分層隨機抽樣
  - 部落抽樣
- 不引入課本外新奇題型，不混入民調偏誤評論、SamplingSurvey 細節題、統計量計算題。

## 4. 新增/調整 template_id / scenario_id / parameter pools

- `sampling_methods_classification_choice` 改為參數化版本（覆蓋舊固定題幹）。
- 新增 `template_id`/`scenario_id` 池：
  - classification simple_random（3）
  - classification systematic（3）
  - classification stratified（3）
  - classification cluster（3）
  - systematic interval calculation（1）
  - stratified allocation calculation（1 + numeric pool）
- 新增 numeric pools：
  - `SYSTEMATIC_INTERVAL_NUMERIC_POOL`：7 組
  - `STRATIFIED_ALLOCATION_NUMERIC_POOL`：6 組
- 新增 metadata：
  - `parameter_signature`
  - `parameters.template_id`
  - `parameters.numeric_params`
  - `parameters.context_params`

## 5. 連續 30 題 diversity 結果

- `unique_question_text_count = 18`
- `unique_scenario_id_count = 15`
- `unique_parameter_signature_count = 18`
- `repeated_question_text_ratio = 0.4`
- `consecutive_duplicate_count = 0`

## 6. answer consistency checks

- systematic interval：
  - 檢查樣本數：2 題（30 題樣本內）
  - `N % n == 0`：全部通過
  - `k == N / n`：全部通過
- stratified allocation：
  - 檢查樣本數：2 題（30 題樣本內）
  - `sample_total * layer_count % population_total == 0`：全部通過
  - `answer_people == sample_total * layer_count / population_total`：全部通過
- choice contract：
  - `answer` 均可對應 `choices`
  - distractors 不與正答重複
  - `/check_answer` 正答/錯答與 alias（A/B/C/D）判定通過

## 7. 修改檔案

- `core/vocational_math_b4/generators/chap3_statistical_measures.py`
- `tests/test_b4_sampling_methods_parameterized_diversity_repair.py`
- `tests/test_b4_chap3_global_diversity_repair.py`
- `reports/b4_generator_planning/b4_sampling_methods_parameterized_diversity_repair_summary.md`

## 8. 新增 tests

- `tests/test_b4_sampling_methods_parameterized_diversity_repair.py`
  - pool 規模
  - 30 題 diversity
  - systematic interval 一致性
  - stratified allocation 一致性
  - 四大抽樣法覆蓋
  - 課本邊界
  - choice/check_answer 回歸
- `tests/test_b4_chap3_global_diversity_repair.py`
  - SamplingMethods 全域多樣性回歸
  - StatisticalBasicConcepts 多樣性回歸

## 9. 測試結果

- `tests/test_b4_sampling_methods_parameterized_diversity_repair.py`：8 passed
- `tests/test_b4_chap3_global_diversity_repair.py`：2 passed
- `tests/test_b4_statistical_basic_concepts_diversity_repair.py`：6 passed
- `tests/test_b4_choice_payload_rendering_repair.py`：6 passed
- `tests/test_b4_final_mode_aware_runtime_coverage_recount.py`：8 passed

## 10. 是否影響 B4 final coverage count

否。`tests/test_b4_final_mode_aware_runtime_coverage_recount.py` 通過，coverage count 維持既有基線。

## 11. final status

READY_FOR_RECHECK
