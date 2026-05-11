# B4 3-1 Conceptual Skill Boundary Repair Summary

## 1. 問題描述

人工抽查發現 3-1 三個技能邊界混淆：

- `vh_數學B4_StatisticalBasicConcepts` 反覆出現抽象名詞題（樣本平均數/母體平均數）。
- `vh_數學B4_SamplingSurvey` 與 `vh_數學B4_SamplingMethods` 角色重疊。
- choice 題型雖要求輸入代號，但部分題型語意與課本主軸不對齊。

本輪目標：重整 3-1 題型邊界，讓題幹與教師用書主軸一致。

## 2. 三個 skill 的修正後邊界

- `vh_數學B4_StatisticalBasicConcepts`
  - 聚焦：統計意義、統計流程（蒐集/整理/陳示/分析/解釋）、敘述統計 vs 推論統計、普查/抽查基本概念。
  - 排除：樣本平均數/母體平均數名詞辨識題、四種抽樣方法分類題。

- `vh_數學B4_SamplingSurvey`
  - 聚焦：母群體、樣本、母群體數、樣本數、普查與抽查情境判斷。
  - 保持既有 `teacher_review` runtime 路徑以相容 FullRuntime-2；題幹改為 choice 風格情境辨識，避免多欄填答 UI 壓力。

- `vh_數學B4_SamplingMethods`
  - 聚焦：簡單隨機抽樣、系統抽樣、分層隨機抽樣、部落抽樣之情境判斷。
  - 補充：系統抽樣間距、分層比例分配之基礎計算。

## 3. 課本 evidence 摘要

- `3-1 統計的基本概念` 主軸為統計概念與研究流程，不是參數/統計量名詞鑽牛角尖。
- `抽樣調查` 主軸為母群體/樣本與普查/抽查辨識。
- `抽樣方法` 主軸為四種抽樣方式的情境判讀與簡單應用計算。

## 4. 修正後 problem_type / scenario_family

- `vh_數學B4_StatisticalBasicConcepts`
  - `problem_type_id`: `statistical_basic_concepts_choice`
  - `scenario_family`: `statistical_basic_concepts_boundary_aligned`
  - `scenario_id`: `descriptive_vs_inferential_statistics` / `statistics_process_order_or_identification` / `census_vs_sample_survey_basic`

- `vh_數學B4_SamplingSurvey`
  - `problem_type_id`: `sampling_survey_bias_review`（沿用 id，內容改為情境型 choice 風格）
  - `scenario_family`: `sampling_survey_foundation_identification`
  - `scenario_id`: `population_sample_size_identification` / `population_sample_identification` / `census_or_sample_survey_identification`

- `vh_數學B4_SamplingMethods`
  - `problem_type_id`: `sampling_methods_classification_choice`
  - `scenario_family`: `sampling_methods_boundary_aligned`
  - `scenario_id`: `sampling_method_identification_*` / `systematic_sampling_interval_or_probability` / `stratified_sampling_proportional_allocation`

## 5. 修改檔案

- core/vocational_math_b4/generators/chap3_statistical_measures.py
- tests/test_b4_3_1_conceptual_skill_boundary_repair.py
- reports/b4_generator_planning/b4_3_1_conceptual_skill_boundary_repair_summary.md

## 6. 測試結果

- `pytest -q tests/test_b4_3_1_conceptual_skill_boundary_repair.py` → **8 passed**
- `pytest -q tests/test_b4_fullruntime_remaining_skills_mode_aware_paths.py` → **15 passed**
- `pytest -q tests/test_b4_fullruntime2_remaining_6_skills_mode_aware_paths.py` → **15 passed**
- `pytest -q tests/test_b4_final_mode_aware_runtime_coverage_recount.py` → **8 passed**

## 7. 是否影響 final coverage count

- 不影響 `total_b4_skills = 40`。
- 屬於 3-1 內容邊界修補與題型語意校正，不新增 skill、不新增 family。
- `SamplingSurvey` 維持 `teacher_review` 分類，不改變既有 coverage 分類統計。

## 8. final status

`READY_FOR_RECHECK`
