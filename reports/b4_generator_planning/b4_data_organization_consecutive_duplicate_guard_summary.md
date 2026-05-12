# B4 DataOrganizationAndCharts Consecutive Duplicate Guard Summary

## 1. 問題描述
DataOrganizationAndCharts 在 Level 1 default 已改為 deterministic_choice，但人工測試仍觀察到相鄰或短時間重複題。

## 2. Root Cause
1. Level 1 default 路徑缺少 DataOrganization 專屬的相鄰避重重抽。
2. 雖已有多個 deterministic scenario，但 route 未比對上一題 `question_text/scenario_id/parameter_signature`。
3. generator 在非固定 seed 情境下未主動避開上一個 scenario。

## 3. 修正方式
1. **generator 層**
- DataOrganization v2 題型新增 module-level 上一題 scenario 避重（seed=None）。
- 保留 `scenario_id + parameter_signature` 供 route 比對。

2. **route 層**
- 在 `/get_next_question` 的 Chap3 runtime 分支新增 DataOrganization Level 1 default guard：
  - 避免 same `question_text`
  - 避免 same `scenario_id`
  - 避免 same `parameter_signature`
  - 最多 retry 3 次，並記錄 fallback flag 到 `router_trace`

3. **策略約束保持不變**
- Level 1 default 仍禁止 open-ended review 題。
- review 題仍僅在 explicit problem_type_id/review path 才出現。

## 4. 是否在 generator / router / route 層避重
- generator：是（seed=None 上一題 scenario 避重）
- router：Level 1 no-open-ended gate 維持
- route：是（DataOrganization 相鄰重複 guard + retry）

## 5. 連續 20 題結果（目標）
- deterministic_choice_count >= 20
- open_ended_review_count = 0
- choices_missing_count = 0
- unique_question_text_count >= 8
- unique_scenario_id_count >= 6
- consecutive_duplicate_count = 0

> 本環境無法執行 pytest，以上為測試門檻與目標值。

## 6. 修改檔案
1. `core/vocational_math_b4/generators/chap3_statistical_measures.py`
2. `core/routes/practice.py`
3. `tests/test_b4_data_organization_consecutive_duplicate_guard.py`

## 7. 新增 tests
- `tests/test_b4_data_organization_consecutive_duplicate_guard.py`

## 8. 測試結果
- `TEST_NOT_RUN_ENV_BLOCKED`
- 原因：目前 shell 環境無可用 `pytest/python/py` 可執行。

## 9. 是否影響 B4 final coverage count
- 不影響。本輪僅做同 skill 內的抽題避重小修，未更動 runtime coverage 類別計數。

## 10. final status
- `READY_FOR_RECHECK`
