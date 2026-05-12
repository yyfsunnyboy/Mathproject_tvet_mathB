# B4 Chap3 Level1 No-OpenEnded Global Repair Summary

## 1. 問題描述
人工測試發現 `vh_數學B4_DataOrganizationAndCharts` 在 Level 1 bare skill default route 仍會出現開放式論述題，造成：
- 無 choices、作答格式不明確
- 超出 Level 1 一般練習可判分範圍

## 2. Root Cause
1. DataOrganizationAndCharts registry 同時含 deterministic 與 review entry，Level 1 default 可能抽到 review 題。
2. 原 deterministic 題池不足且題幹風格混雜，無法穩定保證 Level 1 no-open-ended。

## 3. DataOrganizationAndCharts 修正方式
1. 新增 deterministic choice v2 題池：
- `chart_type_selection_by_purpose`
- `data_organization_first_step`
- `chart_usage_identification`

2. 每題補齊 choice contract：
- `runtime_mode=deterministic_choice`
- `check_mode=deterministic_auto_checked`
- `grading_mode=deterministic`
- `answer_input_type=choice`
- `choices >= 4`
- `scenario_id` / `parameter_signature` 存在

## 4. Level 1 global no-open-ended gate
在 `generate_for_chap3_skill` 加入 Level 1 default 過濾：
- `SamplingSurvey`：維持 choice-only（既有規則）
- `DataOrganizationAndCharts`：default 不抽 `data_organization_chart_selection_review`
- `StatisticalChartReading`：default 不抽 `statistical_chart_reading_visibility_review`

## 5. review 題保留條件
review 題仍保留，但需 explicit `problem_type_id` 指定：
- DataOrganizationAndCharts: `data_organization_chart_selection_review`
- runtime/check/grading 必須為 `teacher_review/review_mode/teacher_review`
- 並具備 `expected_answer_schema` 或 `rubric`

## 6. DataOrganizationAndCharts 連續 20 題結果（目標）
- `open_ended_default_count = 0`
- `deterministic_choice_count >= 20`
- `choices_missing_count = 0`
- `unique_question_text_count >= 8`
- `unique_scenario_id_count >= 6`
- `consecutive_duplicate_count = 0`

> 本環境無法執行 pytest，以上為測試門檻與驗證目標。

## 7. Chap3 global audit 結果（目標）
針對指定 8 個 Chap3 skill：
- deterministic/conceptual Level 1 practice skill：`open_ended_default_count = 0`
- review/handwriting/visual 題型：須有 review metadata 與 rubric/payload

## 8. 修改檔案
1. `core/vocational_math_b4/generators/chap3_statistical_measures.py`
2. `core/vocational_math_b4/services/question_router.py`
3. `tests/test_b4_chap3_level1_no_open_ended_global_repair.py`

## 9. 新增 tests
- `tests/test_b4_chap3_level1_no_open_ended_global_repair.py`

## 10. 測試結果
- `TEST_NOT_RUN_ENV_BLOCKED`
- 原因：本機環境無可執行 `pytest/python/py`。

## 11. 是否影響 B4 final coverage count
- 不影響。僅調整 Level 1 default 題型選擇與 deterministic 題池，未更動 skill/runtime category 計數模型。

## 12. final status
- `READY_FOR_RECHECK`
