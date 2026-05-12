# B4 SamplingSurvey Consecutive Duplicate Guard Summary

## 1. 問題描述
`vh_數學B4_SamplingSurvey` 在 Level 1 bare skill 已回到 deterministic_choice 後，人工觀察仍出現相鄰完全重複題（同題幹連續出現）。

## 2. Root Cause
1. SamplingSurvey 雖已修為 choice 主路徑，但 default 抽題在相鄰請求時未做上一題避重。
2. 路由層原先只對 `StatisticalBasicConcepts` 做 scenario 避重，未覆蓋 `SamplingSurvey`。
3. SamplingSurvey payload 先前缺乏可用於 route 層避重的 `parameter_signature`。

## 3. 修正方式
1. **generator 層**
   - 在 `sampling_survey_foundation_choice_v2` 補上 `parameter_signature`。
   - 增加 seed=None 時的上一題 scenario 輕量避重（不改題型骨架）。

2. **route 層（/get_next_question）**
   - 針對 `SamplingSurvey` + `level<=1` + default route：
     - 比對上一題 `question_text` / `scenario_id` / `parameter_signature`
     - 若相同，最多 retry 3 次重抽
     - 在 `router_trace` 記錄 retry 次數與 fallback flag

3. **策略不變**
   - Level 1 default 仍僅 deterministic_choice
   - 不重新放出 open-ended review 題到 Level 1 default

## 4. 是否在 generator / router / route 層避重
- generator：是（seed=None 時 scenario 避重 + parameter_signature）
- router：沿用既有 Level 1 choice-only gate（SamplingSurvey）
- route：是（新增 SamplingSurvey 相鄰重複 guard + retry）

## 5. 連續 20 題結果（目標）
- deterministic_choice_count = 20
- open_ended_review_count = 0
- unique_question_text_count >= 8
- unique_scenario_id_count >= 8
- consecutive_duplicate_count = 0

> 本環境無法執行 pytest，以下為測試目標；待可用環境驗證最終數值。

## 6. 5000/250 screenshot regression 結果（目標）
- `3` / `C` / `c` 判正確
- `1`（以及其他錯誤選項）判錯
- 不得出現「模組載入錯誤」
- 不得出現「AI/review 判分路徑」

## 7. 修改檔案
1. `core/vocational_math_b4/generators/chap3_statistical_measures.py`
2. `core/routes/practice.py`
3. `tests/test_b4_sampling_survey_consecutive_duplicate_guard.py`

## 8. 新增 tests
- `tests/test_b4_sampling_survey_consecutive_duplicate_guard.py`

## 9. 測試結果
- `TEST_NOT_RUN_ENV_BLOCKED`
- 本環境缺少可執行 `pytest/python/py`。

## 10. 是否影響 B4 final coverage count
- 不影響。僅做 SamplingSurvey 既有 skill 內避重小修，不涉及 skill/runtime category 變更。

## 11. final status
- `READY_FOR_RECHECK`
