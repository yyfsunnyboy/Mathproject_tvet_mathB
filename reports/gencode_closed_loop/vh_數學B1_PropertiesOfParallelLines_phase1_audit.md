# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_PropertiesOfParallelLines
- 階段狀態: AUDIT_PASS
- 建議下一步: phase2_build
- 題庫例題總數: 4
- 已分類例題數: 4
- 來源覆蓋判定: FULL_OBSERVED_COVERAGE_CANDIDATE

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |
| parallel_lines_properties | deterministic_expression | 4530, 4535, 4600, 4602 | integer | numeric_exact | integer_checker | classified |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4530 | parallel_lines_properties | deterministic_expression | high |  | 設$A\left( 2,0 \right)$、$B\left( -3,5 \right)$、$C\left( -1,-1 \right)$、$D\left( 4,x \right)$，若$\overline{AB}... |
| 4535 | parallel_lines_properties | deterministic_expression | high |  | 設$A\left( 1,-5 \right)$、$B\left( 4,1 \right)$、$C\left( -1,x \right)$、$D\left( -4,-3 \right)$，若$\overline{AB... |
| 4600 | parallel_lines_properties | deterministic_expression | high |  | 已知平面上四點$A\left( 1,3 \right)$、$B\left( 2,5 \right)$、$C\left( 3,1 \right)$、$D\left( 5,x \right)$。若直線AB與直線CD平行... |
| 4602 | parallel_lines_properties | deterministic_expression | high |  | 平面上過兩點$\left( 1,3 \right)$、$\left( 3,5 \right)$的直線和過另兩點$\left( 2,0 \right)$、$\left( 3,a \right)$的直線平行，則a = ... |

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
- proposal_path: E:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_PropertiesOfParallelLines_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_PropertiesOfParallelLines

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
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_PropertiesOfParallelLines
