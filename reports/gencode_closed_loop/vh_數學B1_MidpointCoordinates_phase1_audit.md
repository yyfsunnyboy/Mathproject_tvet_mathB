# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_MidpointCoordinates
- 階段狀態: AUDIT_PASS
- 建議下一步: phase2_build
- 題庫例題總數: 10
- 已分類例題數: 10
- 來源覆蓋判定: FULL_OBSERVED_COVERAGE_CANDIDATE

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |
| compute_centroid_coordinates | deterministic_expression | 4443, 4447, 4514 | coordinate_pair | exact_string | coordinate_pair_checker | classified |
| compute_midpoint_coordinates | deterministic_expression | 4418, 4422, 4428, 4429, 4439, 4440, 4511 | coordinate_pair | exact_string | coordinate_pair_checker | classified |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4418 | compute_midpoint_coordinates | deterministic_expression | high |  | 若P為$A\left( -3,4 \right)$與$B\left( 1,2 \right)$兩點之中點，試求： (1)$\overline{AB}$的長度。 (2) P點與$C\left( 1,1 \right)... |
| 4422 | compute_midpoint_coordinates | deterministic_expression | high |  | 設$A\left( -2,3 \right)$、$B\left( 3,2 \right)$、$C\left( 4,-2 \right)$依序為平行四邊形ABCD之三頂點，試求D點坐標。 |
| 4428 | compute_midpoint_coordinates | deterministic_expression | high |  | 若P為$A\left( -1,4 \right)$與$B\left( 3,-2 \right)$兩點之中點，試求P點與原點的距離。 因為P為A與B兩點之中點 由中點公式知P點坐標為$\left( \frac{-1+... |
| 4429 | compute_midpoint_coordinates | deterministic_expression | high |  | 設$A\left( -1,2 \right)$、$B(2,1)$、$C(3,-2)$依序為平行四邊形ABCD之三頂點， 試求D點坐標。 設$D\left( x,y \right)$ 因為平行四邊形對角線互相平分 所... |
| 4439 | compute_midpoint_coordinates | deterministic_expression | high |  | 若P為$A\left( -5,1 \right)$與$B\left( 3,3 \right)$兩點之中點，試求P點與原點的距離。 |
| 4440 | compute_midpoint_coordinates | deterministic_expression | high |  | 設$A\left( 5,4 \right)$、$B\left( 1,5 \right)$、$C\left( -4,5 \right)$依序為平行四邊形ABCD之三頂點， 試求D點坐標。 |
| 4443 | compute_centroid_coordinates | deterministic_expression | high |  | 設△ABC的三個頂點為$A\left( 3,3 \right)$、$B\left( -1,1 \right)$、$C\left( 4,-1 \right)$，試求△ABC的重心坐標。 設△ABC的重心坐標為$G\l... |
| 4447 | compute_centroid_coordinates | deterministic_expression | high |  | 設$A\left( 1,3 \right)$、$B\left( -2,-2 \right)$、$G\left( 1,-1 \right)$為平面上三點、若G為△ABC的重心， 試求C點坐標。 |
| 4511 | compute_midpoint_coordinates | deterministic_choice | high |  | 已知△ABC的三頂點為$A\left( -1,2 \right)$、$B\left( -3,-3 \right)$、$C\left( 3,-1 \right)$，則$\overline{AB}$邊上的中線長為何？ ... |
| 4514 | compute_centroid_coordinates | deterministic_expression | high |  | 設$A\left( 5,9 \right)$、$B\left( 7,1 \right)$、$C\left( -3,-1 \right)$是△ABC的三頂點，若D、E、F分別是$\overline{AB}$、$\ov... |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: 無
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: 無

## 5. 人工審查與風險標記
- manual_review_problem_types: 無
- risk_flags: 無

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: False
- proposal_status: SKIPPED
- reason: 
- proposal_path: C:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_MidpointCoordinates_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_MidpointCoordinates

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
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_MidpointCoordinates
