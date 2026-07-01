# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_DistanceBetweenTwoPointsInPlane
- 階段狀態: AUDIT_PASS
- 建議下一步: phase2_build
- 題庫例題總數: 4
- 已分類例題數: 4
- 來源覆蓋判定: FULL_OBSERVED_COVERAGE_CANDIDATE

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |
| short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2 | deterministic_expression | 4436 | short_answer | algebraic_equivalent | expression_equivalence_checker | classified |
| short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2 | deterministic_expression | 4419, 4432, 4437 | short_answer | unordered_solution_set | solution_set_checker | classified |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4419 | short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2 | deterministic_expression | high |  | 設$A\left( k,-5 \right)$、$B\left( 2,7 \right)$為坐標平面上兩點，且$\overline{AB}=13$，試求k值。 |
| 4432 | short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2 | deterministic_expression | high |  | 設$P\left( 2,-3 \right)$、$Q\left( 6,k \right)$為坐標平面上兩點，且$\overline{PQ}=5$，試求k值。 |
| 4436 | short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2 | deterministic_expression | high |  | 試求坐標平面上$A\left( 3,-1 \right)$、$B(4,2)$ 兩點間的距離。 |
| 4437 | short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2 | deterministic_expression | high |  | 設$A\left( -2,-6 \right)$、$B\left( k,2 \right)$為坐標平面上兩點，且$\overline{AB}=10$，試求k值。 |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: 無
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2, short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2

## 5. 人工審查與風險標記
- manual_review_problem_types: 無
- risk_flags: 無

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: False
- proposal_status: SKIPPED
- reason: 
- proposal_path: E:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_DistanceBetweenTwoPointsInPlane_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_DistanceBetweenTwoPointsInPlane

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
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_DistanceBetweenTwoPointsInPlane
