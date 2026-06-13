# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_VertexFormOfQuadraticFunction
- 階段狀態: AUDIT_PARTIAL
- 建議下一步: review_classifier_proposal
- 題庫例題總數: 5
- 已分類例題數: 5
- 來源覆蓋判定: INSUFFICIENT_SOURCE_EXAMPLES

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4451 | unknown | manual_review | low | possible_missing_problem_type,weak_classifier_match | (1)$y=-3{{\left( x+2 \right)}^{2}}-5$的圖形，是由$y=-3{{x}^{2}}$，水平向左平移① 個單位，然後再鉛直向下平移② 個單位，且其對稱軸為直線③ ，頂點為④ 。 (2)... |
| 4452 | unknown | manual_review | low | possible_missing_problem_type,weak_classifier_match | 試求下列函數平移到新頂點後的新函數。 函數 新頂點 新函數 (1)$y={{x}^{2}}$ $(1,-2)$ (2)$y=-3{{x}^{2}}$ $\left( -2,-1 \right)$ |
| 4453 | unknown | manual_review | low | possible_missing_problem_type,weak_classifier_match | 畫出下列函數的概略圖形，並求其開口方向、頂點坐標、對稱軸、最大值或最小值。 (1)$y=3{{\left( x-2 \right)}^{2}}+5$ (2)$y=-2{{\left( x+4 \right)}^{2... |
| 4456 | unknown | manual_review | low | possible_missing_problem_type,weak_classifier_match | 已知$y=f\left( x \right)={{x}^{2}}+px+q$圖形最低點的坐標為$\left( 2,5 \right)$，試求p + q之值。 |
| 4504 | unknown | manual_review | low | possible_missing_problem_type,weak_classifier_match | 設二次函數$y=f\left( x \right)=a{{x}^{2}}+bx+c$圖形的頂點為$\left( 1,3 \right)$且交y軸於點$\left( 0,1 \right)$，則$f\left( 3 ... |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: 無
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: 無

## 5. 人工審查與風險標記
- manual_review_problem_types: unknown
- risk_flags: possible_missing_problem_type, weak_classifier_match
- example 4451: Skill-specific classifier/rule pack is missing.
- example 4452: Skill-specific classifier/rule pack is missing.
- example 4453: Skill-specific classifier/rule pack is missing.
- example 4456: Skill-specific classifier/rule pack is missing.
- example 4504: Skill-specific classifier/rule pack is missing.

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: True
- proposal_status: GENERATED
- reason: fallback_unknown_majority
- proposal_path: E:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_VertexFormOfQuadraticFunction_classifier_proposal.json
- promote_ready: True
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_VertexFormOfQuadraticFunction

## 7. Auto Review Summary
- proposal_count: 1
- unknown_examples_total: 5
- auto_approve_safe_eligible: True
- split_or_merge_recommendation: recommend_single_type
- classifier_gate: {'status': 'classifier_auto_pending_promote', 'allowed': True, 'warnings': []}
- generator_draft_gate: {'status': 'generator_draft_allowed', 'allowed': True, 'warnings': []}
- runtime_ready_gate: {'status': 'blocked_quality_gates', 'allowed': False, 'blockers': ['blocked_checker_smoke_not_passed', 'blocked_dynamic_sampling_not_passed']}
- per_candidate_promote_gate: [{'problem_type_id': 'absolute_value_inequality_malformed_source_review', 'promote_recommendation': 'recommend_with_warning', 'promote_blockers': []}]
- next_action: ready_for_safe_promote

| problem_type_id | name_zh | matched_example_ids | matched_count | unmatched_example_ids | representative_example_id | confidence | checker_key | equivalence_type | recommendation | blockers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| absolute_value_inequality_malformed_source_review |  | 4451, 4452, 4453, 4456, 4504 | 5 |  | 4451 | medium | manual_review_checker | manual_review_or_ai_judged | recommend_with_warning |  |

### Candidate-to-Example Mapping

| example_id | title/source | detected_problem_type_id | answer_shape | classification_reason | risk_flags |
| --- | --- | --- | --- | --- | --- |
| 4451 | textbook_example | absolute_value_inequality_malformed_source_review | manual_review_or_free_response | heuristic_pattern_match | manual_review_candidate_in_proposal, possible_missing_problem_type, weak_classifier_match |
| 4452 | textbook_example | absolute_value_inequality_malformed_source_review | manual_review_or_free_response | heuristic_pattern_match | manual_review_candidate_in_proposal, possible_missing_problem_type, weak_classifier_match |
| 4453 | textbook_example | absolute_value_inequality_malformed_source_review | manual_review_or_free_response | heuristic_pattern_match | manual_review_candidate_in_proposal, possible_missing_problem_type, weak_classifier_match |
| 4456 | textbook_example | absolute_value_inequality_malformed_source_review | manual_review_or_free_response | heuristic_pattern_match | manual_review_candidate_in_proposal, possible_missing_problem_type, weak_classifier_match |
| 4504 | textbook_example | absolute_value_inequality_malformed_source_review | manual_review_or_free_response | heuristic_pattern_match | manual_review_candidate_in_proposal, possible_missing_problem_type, weak_classifier_match |
- promote_precheck: {'proposed_problem_type_id_not_unknown': True, 'matched_example_ids_not_empty': True, 'answer_contract_not_empty': True, 'checker_key_not_empty': True, 'equivalence_type_not_empty': True, 'recommendation_not_reject': True, 'no_fatal_risk_flags': True}
- workflow_commands: {'audit': 'python scripts\\gencode_pipeline_phase1_audit.py --skill-id vh_數學B1_VertexFormOfQuadraticFunction', 'review': 'python scripts\\gencode_pipeline_phase1_audit.py --skill-id vh_數學B1_VertexFormOfQuadraticFunction --json', 'promote': 'python scripts\\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_VertexFormOfQuadraticFunction', 'auto_approve_safe': 'python scripts\\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_VertexFormOfQuadraticFunction --auto-approve-safe'}
- next_command_suggestions: {'audit': 'python scripts\\gencode_pipeline_phase1_audit.py --skill-id vh_數學B1_VertexFormOfQuadraticFunction', 'review': 'python scripts\\gencode_pipeline_phase1_audit.py --skill-id vh_數學B1_VertexFormOfQuadraticFunction --json', 'promote': 'python scripts\\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_VertexFormOfQuadraticFunction', 'auto_approve_safe': 'python scripts\\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_VertexFormOfQuadraticFunction --auto-approve-safe'}

## 8. 下一步建議
請先審核 classifier proposal，再執行 promote。
Auto Review Summary:
1. proposed_problem_type_id: absolute_value_inequality_malformed_source_review
   - proposed_problem_type_name_zh: 
   - matched_example_ids: 4451, 4452, 4453, 4456, 4504
   - classification_confidence: medium
   - answer_contract_proposal: {"answer_type": "manual_review", "equivalence_type": "manual_review_or_ai_judged", "checker_key": "manual_review_checker", "order_matters": false, "accepted_format_notes": ["requires source text correction before deterministic generation"], "canonical_answer_schema": {"type": "manual_review"}}
   - checker_key_proposal: manual_review_checker
   - equivalence_type_proposal: manual_review_or_ai_judged
   - promote_recommendation: recommend_with_warning
   - promote_blockers: 無
- auto_approve_safe_eligible: true

