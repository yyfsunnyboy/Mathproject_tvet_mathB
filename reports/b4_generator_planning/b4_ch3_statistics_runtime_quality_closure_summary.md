# B4 Ch3 Statistics Runtime Quality — Closure Summary

**Status:** CLOSED as initial runtime-quality gate
**Date:** 2026-05-12
**Scope:** Ch3 統計題型 runtime-ready 品質修復

---

## Target Skills

| skill_id suffix | 中文說明 |
|---|---|
| `Statisticalchartreading` | 統計圖表判讀 |
| `FrequencyDistributionTableConstruction` | 次數分配表編製 |
| `OpinionPollInterpretation` | 民意調查的解讀 |
| `NormalDistributionAndEmpiricalRule` | 常態分配與經驗法則 |

---

## Problems Fixed

### 1. Statisticalchartreading — 修復 mojibake / ?????

**問題：** `statistical_chart_type_by_purpose_choice`、`statistical_chart_interpretation_caution_choice`、`statistical_chart_match_data_type_choice` 三個 generator 函數的 scenarios 清單全部為 `?????` mojibake，導致前端出現大量問號，題目完全不可讀。

**修復：**
- 補上完整中文題目、選項與說明。
- `chart_type_by_purpose`：新增趨勢/比較/比例/分布四種情境。
- `chart_interpretation_caution`：新增縱軸起始值、樣本數、相關 vs 因果三類注意事項題。
- `chart_match_data_type`：新增類別比較/連續分布/比例三種資料對應題。
- 修正 `remediation_candidates` 中的亂碼 skill_id（`vh_??B4_` → `vh_數學B4_`）。

**結果：** Statisticalchartreading 所有 problem_type 均輸出正常中文 payload，無 `?????`。

---

### 2. FrequencyDistributionTableConstruction — 完整表格填寫暫不直接上線

**問題：** `frequency_distribution_table_construction_shell_v2` 輸出完整表格填寫題（`answer: ""`、`answer_type: "handwriting"`），前端無對應表格輸入元件，學生只看到一串資料與普通輸入框，無法作答。

**修復策略：**
- 改為 **deterministic 精簡版**：提供資料與明確分組（5 組，每組寬度固定為 10），只問其中一組的次數。
- `problem_type_id` 改為 `frequency_table_single_bin_count`。
- `answer_type` 改為 `integer`，`answer_input_type` 改為 `numeric_input`。
- 同時附上完整的 `table_data`（含所有組別實際次數），供前端輔助顯示。
- 在 payload 保留 `full_table_note: "FREE_RESPONSE_OR_TABLE_INPUT_REQUIRED"` 標記，記錄完整表格填寫版的後續路徑。

**結果：** runtime 版本為 deterministic integer 問答題，學生可正常作答；完整表格填寫延後。

---

### 3. OpinionPollInterpretation — 修復假多樣性

**問題：** 原 generator 硬編碼固定 payload（樣本數 200、贊成比例 58%、調查方式「網路問卷」），每次完全相同，學生重複練習時幾乎沒有差異。

**修復：**
- 新增隨機欄位：
  - **樣本數**：從 `[80, 120, 150, 200, 300, 500]` 隨機選取
  - **百分比**：從 `[42, 48, 52, 55, 58, 63, 67, 71]` 隨機選取
  - **調查方式**：從網路問卷、街頭攔訪、電話訪問、學校問卷、社群媒體投票隨機選取
  - **問題焦點**：5 種不同調查主題，各帶有對應的解讀焦點提示（母體推論限制、抽樣偏差、樣本代表性、百分比解讀、調查方式偏誤）
- Smoke 驗證：5 題中出現 5 種不同題目，多樣性確認。

**結果：** runtime-ready（teacher_review），題目變化豐富。

---

### 4. NormalDistributionAndEmpiricalRule — 擴充 problem_type

**問題：** 原 generator 只有三種幾乎相同的 `within_sigma` 題型，且 `problem_type_id` 全部固定為 `empirical_rule_interval_percentage`，缺乏多樣性。

**修復：** 擴充為 5 種不同 `problem_type_id`：

| problem_type_id | 說明 | 答案格式 |
|---|---|---|
| `empirical_rule_within_1sd` | 問 ±1σ 約占百分之幾 | integer（68） |
| `empirical_rule_within_2sd` | 問 ±2σ 約占百分之幾 | integer（95） |
| `empirical_rule_within_3sd` | 問 ±3σ 約占百分之幾 | integer（99） |
| `normal_interval_identification` | 給平均數、標準差與某數值，問位於正幾個標準差 | integer（1/2/3） |
| `normal_interval_percentage` | 給平均數、標準差與區間，問約占百分之幾 | integer（68/95/99） |

- 每次依 seed 輪流選取不同 subtype，5 題可覆蓋全部 5 種。
- 在 `ALLOW_MULTIPLE_CHOICE_PROBLEM_TYPES` 白名單中加入新 subtype，確保 choices 不被 normalizer 清除。

**結果：** 5 題 smoke 覆蓋全部 5 種 problem_type，均為正確答案與 integer answer_type。

---

## Files Modified

| 檔案 | 修改性質 |
|---|---|
| `core/vocational_math_b4/generators/chap3_statistical_measures.py` | 修復 4 個 generator 函數 |
| `core/vocational_math_b4/services/question_router.py` | 更新 `ALLOW_MULTIPLE_CHOICE_PROBLEM_TYPES` 白名單（加入 empirical_rule 新 subtype） |

**未修改：** 前端、資料庫、Ch1 generator、Ch2 generator、router registry（只更新 allowlist）。

---

## Validation

**Smoke script：** `scripts/smoke_b4_ch3_statistics_runtime_quality.py`
**Report：** `reports/b4_generator_planning/b4_ch3_statistics_runtime_quality_smoke.md`

| 指標 | 結果 |
|---|---|
| 總題數 | 20（每 skill 5 題） |
| PASS | **20** |
| FAIL / ERROR | **0** |
| OpinionPoll 5 題均不同 | ✅ PASS（5 種不同題目） |
| NormalDistribution 覆蓋 problem_type 數 | ✅ PASS（5 種全覆蓋） |
| 任何題目包含 ????? | ✅ 無 |

---

## Remaining Known Limitations

| 項目 | 說明 | 後續路徑 |
|---|---|---|
| FrequencyDistributionTable 完整填寫版 | 需要 table input UI 或 AI-judged free-response | 標記 `FREE_RESPONSE_OR_TABLE_INPUT_REQUIRED`，待前端 table-input 元件就緒後啟用 |
| OpinionPollInterpretation 評分 | 仍需 teacher_review，無法 auto-check | 後續可設計 rubric-based AI judging |
| 統計圖表判讀的圖形渲染 | 目前為純文字 payload，無圖形 | 後續升級為 chart_data 真實渲染（bar/line chart component） |
| NormalDistribution 圖形輔助 | 目前無常態曲線圖示 | 可在題目旁附參考圖，但不強制 |
