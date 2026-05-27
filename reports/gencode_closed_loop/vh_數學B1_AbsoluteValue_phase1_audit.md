# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_AbsoluteValue
- 階段狀態: AUDIT_PASS
- 建議下一步: phase2_build
- 題庫例題總數: 4
- 已分類例題數: 4
- 來源覆蓋判定: FULL_OBSERVED_COVERAGE_CANDIDATE

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |
| absolute_value_distance_between_two_points | deterministic_numeric | 4399 | integer | numeric_exact | integer_checker | classified |
| absolute_value_equation_basic | deterministic_expression | 4398, 4408, 4412 | solution_set | unordered_solution_set | solution_set_checker | classified |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4398 | absolute_value_equation_basic | deterministic_expression | high |  | 數線上，若$\left\| x \right\|$= 8，試求x之值。 |
| 4399 | absolute_value_distance_between_two_points | deterministic_numeric | high |  | 已知數線上兩點$A\left( -3 \right)$、$B\left( 7 \right)$，試求A、B兩點的距離。 |
| 4408 | absolute_value_equation_basic | deterministic_expression | high |  | 數線上，若$\left\| x \right\|$= 7，試求x之值。 |
| 4412 | absolute_value_equation_basic | deterministic_expression | high |  | 數線上，若$\left\| x \right\|$= 4，試求x之值。 |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: 無
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: absolute_value_equation_basic

## 5. 人工審查與風險標記
- manual_review_problem_types: 無
- risk_flags: 無

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: False
- proposal_status: SKIPPED
- reason: 
- proposal_path: D:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_AbsoluteValue_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_AbsoluteValue

## 7. 下一步建議
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_AbsoluteValue
