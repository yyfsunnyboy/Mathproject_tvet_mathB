# B4 SamplingSurvey Level1 Choice And Checker Repair Summary

## 1. 問題描述
人工測試發現 `vh_數學B4_SamplingSurvey` 有兩個 blocking：
1. bare skill Level 1 仍會出現開放式論述題。
2. deterministic choice 題在 `/check_answer` 輸入正答（例如 `3`）可能出現判錯或「模組載入錯誤」。

## 2. Root Cause
1. Chap3 router 對 `SamplingSurvey` 在未指定 `problem_type_id` 時，會在 choice/review entry 間隨機抽取，導致 Level 1 預設路徑出現 review 題。
2. `/check_answer` 的 deterministic 判分分流過度依賴 skill allowlist 分類；`SamplingSurvey` 混合 runtime path 情境下，可能落到 legacy module import 分支而出現模組錯誤。
3. SamplingSurvey choice scenario pool 太小，容易重複。

## 3. Level 1 出題策略修正
- `generate_for_chap3_skill` 新增規則：
  - 當 `skill=SamplingSurvey` 且 `level<=1` 且未指定 `problem_type_id`，只保留 deterministic choice entry，不抽 review entry。

## 4. checker / answer normalization 修正
- `/check_answer` 新增 `check_mode == deterministic_auto_checked` 的通用 deterministic 分支：
  - `answer_input_type=choice` 時直接比對正規化後答案（支援 `1/2/3/4` 與 `A/B/C/D` alias）。
  - 不再落入 legacy module import 的「模組載入錯誤」路徑。

## 5. screenshot regression 結果（設計目標）
針對題目：
「某城市共有 5000 位機車族，研究者抽出其中 250 位填寫問卷。下列何者是樣本？」
- `3` -> correct
- `C` -> correct
- `c` -> correct
- `1` -> incorrect
- response 不含「模組載入錯誤」
- response 不含「AI/review 判分路徑」

## 6. 偏誤題保留條件
- `sampling_survey_bias_review` 保留為 explicit review path 題型。
- Level 1 bare skill default route 不主動出該 review 題。
- 另補一題 choice 版偏誤辨識情境（非開放式）。

## 7. 連續 20 題結果（目標門檻）
- `open_ended_review_count = 0`
- `deterministic_choice_count = 20`
- `unique_question_text_count >= 8`
- `unique_scenario_id_count >= 8`
- `consecutive_duplicate_count = 0`

## 8. 修改檔案
1. `core/vocational_math_b4/generators/chap3_statistical_measures.py`
2. `core/vocational_math_b4/services/question_router.py`
3. `core/routes/practice.py`
4. `tests/test_b4_sampling_survey_level1_choice_and_checker_repair.py`

## 9. 新增 tests
- `tests/test_b4_sampling_survey_level1_choice_and_checker_repair.py`

## 10. 測試結果
- `TEST_NOT_RUN_ENV_BLOCKED`
- 本環境無可用 `pytest/python/py`，無法執行指定回歸測試命令。

## 11. 是否影響 B4 final coverage count
- 不影響。僅修正 SamplingSurvey 的 Level 1 路由策略、choice 生成池與 deterministic checker 分流；未新增 skill、未變更 runtime category 計數。

## 12. Final Status
- `READY_FOR_RECHECK`
