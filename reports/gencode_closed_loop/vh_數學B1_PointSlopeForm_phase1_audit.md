# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_PointSlopeForm
- 階段狀態: AUDIT_FAIL
- 建議下一步: phase2_build
- 題庫例題總數: 14
- 已分類例題數: 14
- 來源覆蓋判定: INSUFFICIENT_SOURCE_EXAMPLES

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |
| write_line_equation_from_point_slope | rule_only | 4540, 4541, 4543, 4546, 4549, 4550, 4551, 4556, 4560, 4606 |  |  |  | classified |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4540 | write_line_equation_from_point_slope | rule_only | medium |  | 試求過點$\left( 2,-1 \right)$且斜率為$\frac{1}{2}$的直線方程式。 |
| 4541 | write_line_equation_from_point_slope | rule_only | medium |  | 試求過點$\left( 1,-2 \right)$且斜率為−3的直線方程式。 |
| 4542 | unknown | manual_review | low | possible_missing_problem_type,weak_classifier_match | 設$A\left( -1,1 \right)$、$B\left( 3,-1 \right)$，求$\overline{AB}$之垂直平分線方程式。 |
| 4543 | write_line_equation_from_point_slope | rule_only | medium |  | 試求過點$A\left( 2,-1 \right)$與$B\left( 0,3 \right)$之直線方程式。 |
| 4546 | write_line_equation_from_point_slope | rule_only | medium |  | 試求斜率為3且x截距為5的直線方程式。 |
| 4549 | write_line_equation_from_point_slope | rule_only | medium |  | (1)試求過點$\left( 2,-3 \right)$，且斜率為$-\frac{1}{2}$的直線方程式。 (2)試求過點$\left( -1,4 \right)$，且斜率為2的直線方程式。 |
| 4550 | write_line_equation_from_point_slope | rule_only | medium |  | 如圖，已知平面上兩鄉鎮的位置為、，今兩鄉鎮市民希望在鐵路沿線上設立一車站，此車站位於與兩鄉鎮距離相同的直線道路上，試求此車站所在的直線道路方程式。 |
| 4551 | write_line_equation_from_point_slope | rule_only | medium |  | 試求通過$A\left( 3,-1 \right)$、$B\left( 2,1 \right)$兩點的直線方程式。 |
| 4552 | unknown | manual_review | low | possible_missing_problem_type,weak_classifier_match | 某農夫有塊三角形農地ABC，如圖所示，在平面上的坐標位置為$A\left( 8,-4 \right)$、$B\left( 4,2 \right)$、$C\left( 2,-2 \right)$。今農夫欲將農地沿著過... |
| 4556 | write_line_equation_from_point_slope | rule_only | medium |  | (1)試求過點$\left( -5,1 \right)$，且斜率為3的直線方程式。 (2)試求過點$\left( 1,-3 \right)$，且斜率為$-\frac{2}{3}$的直線方程式。. |
| 4557 | unknown | manual_review | low | possible_missing_problem_type,weak_classifier_match | 設、，試求之垂直平分線方程式。 |
| 4560 | write_line_equation_from_point_slope | rule_only | medium |  | 試求通過$A\left( -3,1 \right)$、$B\left( 2,4 \right)$兩點的直線方程式。 |
| 4561 | unknown | manual_review | low | possible_missing_problem_type,weak_classifier_match | 已知△ABC三頂點坐標分別為、、$C\left( -2,-4 \right)$，試求$\overline{BC}$邊上之中線方程式。 |
| 4606 | write_line_equation_from_point_slope | rule_only | medium |  | 已知a、b為實數，若直線ax + by + 2 = 0通過點${{k}_{1}}$且斜率為$\frac{2}{3}$，則a + b = (A) −3 (B) −1 (C) 1 (D) 3。 |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: write_line_equation_from_point_slope
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: 無

## 5. 人工審查與風險標記
- manual_review_problem_types: unknown
- risk_flags: possible_missing_problem_type, weak_classifier_match
- example 4542: Skill-specific classifier/rule pack is missing.
- example 4552: Skill-specific classifier/rule pack is missing.
- example 4557: Skill-specific classifier/rule pack is missing.
- example 4561: Skill-specific classifier/rule pack is missing.

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: False
- proposal_status: SKIPPED
- reason: 
- proposal_path: D:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_PointSlopeForm_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_PointSlopeForm

## 7. Auto Review Summary
- proposal_count: 0
- unknown_examples_total: 0
- auto_approve_safe_eligible: False
- split_or_merge_recommendation: 
- classifier_gate: {}
- generator_draft_gate: {}
- runtime_ready_gate: {}
- per_candidate_promote_gate: []
- next_action: 

## 8. 下一步建議
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_PointSlopeForm
