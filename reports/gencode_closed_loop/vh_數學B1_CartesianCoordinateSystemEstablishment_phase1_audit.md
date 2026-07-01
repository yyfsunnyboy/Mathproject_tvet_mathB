# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_CartesianCoordinateSystemEstablishment
- 階段狀態: AUDIT_FAIL
- 建議下一步: phase2_build
- 題庫例題總數: 4
- 已分類例題數: 4
- 來源覆蓋判定: FULL_OBSERVED_COVERAGE_CANDIDATE

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |
| cartesian_coordinate_quadrant_symbol_reasoning | deterministic_choice | 4417, 4435, 4509, 4510 |  |  |  | classified |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4417 | cartesian_coordinate_quadrant_symbol_reasoning | deterministic_choice | high |  | 若點$P\left( a,b \right)$位在第一象限且a < b，則$Q\left( a-b,{{a}^{2}}b \right)$位在第幾象限？ |
| 4435 | cartesian_coordinate_quadrant_symbol_reasoning | deterministic_choice | high |  | 設a、b為實數，且a < b < 0，則點$Q\left( ab,a+b \right)$在第幾象限？ |
| 4509 | cartesian_coordinate_quadrant_symbol_reasoning | deterministic_choice | high |  | 設A點為坐標平面上一點，且A點到x軸及y軸之距離分別為3和4，則下列何者可能為A點之坐標？ 　(A)$\left( -4,-3 \right)$　(B)$\left( -3,4 \right)$　_x000D_ (... |
| 4510 | cartesian_coordinate_quadrant_symbol_reasoning | deterministic_choice | high |  | 已知點$P\left( a-b,ab \right)$在坐標平面的第四象限，則下列敘述何者正確？_x000D_ (A)$A\left( -a,b \right)$在第一象限　(B)$B\left( \left\| a... |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: cartesian_coordinate_quadrant_symbol_reasoning
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: 無

## 5. 人工審查與風險標記
- manual_review_problem_types: 無
- risk_flags: 無

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: False
- proposal_status: SKIPPED
- reason: 
- proposal_path: E:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_CartesianCoordinateSystemEstablishment_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_CartesianCoordinateSystemEstablishment

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
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_CartesianCoordinateSystemEstablishment
