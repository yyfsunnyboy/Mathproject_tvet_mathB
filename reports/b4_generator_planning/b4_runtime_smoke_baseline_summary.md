# B4 Runtime Smoke Baseline Summary

**Status:** B4 runtime baseline smoke summarized
**Date:** 2026-05-12
**Scope:** B4 全章節（Ch1 / Ch2 / Ch3）runtime smoke baseline

---

## Current Passed Areas

| 驗收項目 | 結果 | Smoke Script |
|---|---|---|
| Ch1 choices policy | ✅ PASS（所有代表 skill choices_count = 0） | `scripts/smoke_b4_ch1_choices_policy.py` |
| Ch2 choices policy | ✅ PASS（Ch2 數值/機率/集合題型不再出現 choices） | 透過 question_router normalizer 驗收 |
| Ch3 statistics runtime quality | ✅ PASS 20/20，FAIL/ERROR 0 | `scripts/smoke_b4_ch3_statistics_runtime_quality.py` |

---

## Runtime Payload Policy

### ALLOW_MULTIPLE_CHOICE_PROBLEM_TYPES 白名單機制

位置：`core/vocational_math_b4/services/question_router.py`，函數 `_normalize_output_payload()`

**核心規則：**
1. 所有 generator 產出的 payload，在 router 輸出前都會經過 `_normalize_output_payload()` 正規化。
2. 只有 `problem_type_id` 明確列入 `ALLOW_MULTIPLE_CHOICE_PROBLEM_TYPES` 的題型，才可保留 `choices` 陣列。
3. 其他所有題型，`choices` 一律清空為 `[]`，前端自動顯示數值輸入框。

**白名單包含的題型類別：**

| 類型 | 說明 |
|---|---|
| 概念選擇題 | `statistical_basic_concepts_choice`、`sampling_methods_classification_choice` 等 |
| 統計抽樣選擇題 | `sampling_survey_foundation_identification`、`sampling_survey_bias_review` 等 |
| 圖表判讀選擇題 | `chart_type_by_purpose`、`chart_interpretation_caution`、`chart_match_data_type` 等 |
| 資料整理選擇題 | `chart_type_selection_by_purpose`、`data_organization_first_step`、`chart_usage_identification` 等 |
| 常態分配選擇題 | `empirical_rule_within_1sd`、`empirical_rule_within_2sd`、`empirical_rule_within_3sd`、`empirical_rule_interval_percentage`、`normal_interval_percentage` |

**未列入白名單（即強制 input 作答）：**
- Ch1 所有 deterministic numeric 題型（計數、排列、組合、階乘、二項式等）
- Ch2 所有 probability / fraction / integer 類型（古典機率、補事件、聯集、條件機率、期望值等）
- Ch3 中的數值計算題（mean、median、mode、variance、percentile 等）

### 前端變動

**前端未修改。** 前端依照 `choices` 陣列是否為空來決定渲染方式：
- `choices.length > 0` → 選擇題 UI
- `choices.length === 0` → 數值輸入框（預設行為）

---

## Ch3 Runtime Notes

| skill_id suffix | 狀態 | 說明 |
|---|---|---|
| `Statisticalchartreading` | ✅ runtime-ready | 修復 mojibake，四選一中文選擇題，含趨勢/比較/比例/分布/注意事項等多種題型 |
| `FrequencyDistributionTableConstruction` | ✅ runtime-ready（精簡版）<br>⚠️ 完整版 deferred | 精簡版：單一組距次數 integer 問答，附 `table_data`。<br>完整版：標記 `FREE_RESPONSE_OR_TABLE_INPUT_REQUIRED`。 |
| `OpinionPollInterpretation` | ✅ runtime-ready（teacher_review） | 隨機樣本數、百分比、調查方式、問題焦點，5 題均不同 |
| `NormalDistributionAndEmpiricalRule` | ✅ runtime-ready | 5 種 problem_type 覆蓋：±1/2/3σ 基本題、區間識別、區間百分比 |

---

## Known Limitations / Deferred

| 項目 | 類別 | 說明 |
|---|---|---|
| Tree diagram listing / 手寫過程 | AI-judged free-response | 屬於 `free_response` 路徑，使用 `tree_diagram_judge.py` 批改，不走 deterministic choices |
| 完整次數分配表填寫 | Table input required | 需前端 table-input 元件就緒才能上線，目前以精簡版過渡 |
| 累積次數分配表補全 | AI-judged / teacher_review | `cumulative_frequency_table_completion_review` 目前標記 teacher_review |
| 圖表真實渲染 | Chart rendering | 統計圖表判讀題目前為文字描述，後續可升級為 chart_data 實際圖形渲染 |
| OpinionPollInterpretation 評分 | Teacher review | 解釋性題目無法 auto-check，需 rubric-based AI judging 或教師評分 |

---

## Next Recommended Gate

### B4 Full-Volume Runtime Smoke

**目標：** 抽測 Ch1、Ch2、Ch3 全部代表 skill，確認 payload 品質與 choices policy 一致。

**建議作法：**
1. 建立 `scripts/smoke_b4_full_volume_runtime.py`：
   - 涵蓋 Ch1 代表 skill（Counting、Permutation、Combination、BinomialTheorem 等）
   - 涵蓋 Ch2 代表 skill（Probability、ConditionalProbability、ExpectedValue、BasicConceptsOfSets 等）
   - 涵蓋 Ch3 代表 skill（CentralTendency、DispersionMeasures、NormalDistribution、SamplingMethods 等）
2. 每個 skill 各抽 3～5 題，seed 固定，確保可重現。
3. 檢查項目：
   - 數值題 `choices_count == 0`
   - 概念選擇題 `choices_count >= 2`
   - `question_text` 無 `?????` 或 `[MISSING]`
   - `answer` 與 `answer_type` 存在且合理

**不再人工逐題點全部 skill：**
以 smoke script + policy report 驗收，取代手動瀏覽每個 `/practice?skill_id=...` 頁面。

---

## Smoke Scripts Index

| script | 說明 | 報告 |
|---|---|---|
| `scripts/smoke_b4_ch1_choices_policy.py` | Ch1 choices 清除驗收 | `reports/b4_generator_planning/b4_ch1_choices_policy_smoke.md` |
| `scripts/smoke_b4_ch3_statistics_runtime_quality.py` | Ch3 統計題型品質驗收 | `reports/b4_generator_planning/b4_ch3_statistics_runtime_quality_smoke.md` |

---

## Closure Reference

| 文件 | 路徑 |
|---|---|
| Ch3 統計修復 closure | `reports/b4_generator_planning/b4_ch3_statistics_runtime_quality_closure_summary.md` |
| Ch3 smoke 原始報告 | `reports/b4_generator_planning/b4_ch3_statistics_runtime_quality_smoke.md` |
| Ch1 smoke 原始報告 | `reports/b4_generator_planning/b4_ch1_choices_policy_smoke.md` |
