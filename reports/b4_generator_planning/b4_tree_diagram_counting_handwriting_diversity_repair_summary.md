# Phase B4 TreeDiagramCounting Handwriting Diversity Repair Summary

## 1. 問題描述
- `vh_數學B4_TreeDiagramCounting` 人工測試出現高重複，常見為二元事件同骨架僅換名稱。
- 相鄰題目偶爾完全重複，影響練習體驗與 diversity gate 信度。

## 2. Root Cause
1. TreeDiagramCounting default 路徑偏向固定 variant/固定索引。
2. handwriting 題型缺少可檢查的 scenario metadata，route 層較難做有效避重。
3. 「A/B、甲乙、紅藍」同骨架被誤當多樣題，fake diversity 風險高。

## 3. 修正方式
- 保留 handwriting / AI checked runtime，不改 deterministic。
- 擴充 `tree_diagram_judge` payload metadata 與多情境 pool（含 product-rule 兩階段情境）。
- 在 `practice.py` 的 TreeDiagram payload 建構加入相鄰避重重抽（最多 3 次）：
  - 比對 `question_text / scenario_id / scenario_family / parameter_signature / outcome_set_signature`。
- 回傳 payload 補齊：
  - `scenario_family / scenario_id / parameter_signature / outcome_set_signature / tree_depth / branch_counts / context_signature`
  - `expected_answer_schema / rubric / textbook_alignment_note`

## 4. Scenario Pool（摘要）
- scenario_family（至少 5）：
  - `binary_three_trials`
  - `binary_two_trials`
  - `best_of_three_binary_match`
  - `product_rule_two_stage`
  - `mixed_outcome_two_stage`
- scenario_id（至少 8，實作 12）：
  - `coin_toss_three_times`
  - `coin_toss_two_times`
  - `two_color_three_draws_with_replacement`
  - `binary_outcome_two_trials`
  - `meal_choice_two_stage`
  - `clothing_choice_two_stage_2x2`
  - `clothing_choice_two_stage_2x3`
  - `route_choice_two_stage`
  - `digit_or_code_two_stage`
  - `dice_coin_combination`
  - `win_two_games_best_of_three_named_teams`
  - `win_two_games_best_of_three_ab_teams`

## 5. 如何避免 Fake Diversity
- 明確規範 best-of-three 命名差異（A/B、甲乙、紅藍）共享同一 `scenario_family=best_of_three_binary_match`。
- 以 `scenario_family + parameter_signature + outcome_set_signature` 判斷骨架，不以名稱替換充數。

## 6. 連續 20 題 Diversity 結果
- 已新增對應測試與指標檢查：
  - `unique_question_text_count >= 8`
  - `unique_scenario_id_count >= 8`
  - `unique_scenario_family_count >= 5`
  - `unique_parameter_signature_count >= 8`
  - `consecutive_duplicate_question_text_count = 0`
  - `consecutive_duplicate_scenario_id_count = 0`
  - `consecutive_duplicate_parameter_signature_count = 0`

## 7. Handwriting / AI Checked Contract
- 維持：
  - `answer_type=handwriting`
  - `requires_handwriting=true`
  - `runtime_mode=visual_or_handwriting_ai_checked`
  - `check_mode=handwriting_ai_checked`（或 review_mode 相容）
  - `grading_mode=ai_judged_free_response / ai_assisted_review`
- 不硬改為 deterministic checker。

## 8. 修改檔案
- `core/vocational_math_b4/free_response/tree_diagram_judge.py`
- `core/routes/practice.py`
- `core/vocational_math_b4/generators/chap3_statistical_measures.py`（僅小幅 metadata 相關調整）

## 9. 新增測試
- `tests/test_b4_tree_diagram_counting_handwriting_diversity_repair.py`

## 10. 測試結果
- `TEST_NOT_RUN_ENV_BLOCKED`
- 原因：
  - `py -m pytest`：`No installed Python found!`
  - `venv\Scripts\python.exe -m pytest`：venv 指向的 Python 路徑不存在，無法啟動程序。

## 11. 是否影響 B4 final coverage count
- 設計上不影響（未新增 skill、未改 coverage 結構）。
- 但因環境無法跑 regression，需 recheck 驗證。

## 12. Final Status
- `NEEDS_SMALL_REPAIR`（環境阻塞需補跑測試後再確認）
