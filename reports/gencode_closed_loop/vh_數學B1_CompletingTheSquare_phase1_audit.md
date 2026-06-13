# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_CompletingTheSquare
- 階段狀態: AUDIT_PARTIAL
- 建議下一步: phase2_build
- 題庫例題總數: 2
- 已分類例題數: 2
- 來源覆蓋判定: INSUFFICIENT_SOURCE_EXAMPLES

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4468 | unknown | manual_review | low | possible_missing_problem_type,weak_classifier_match | 利用配方法將下列各式化為$a{{\left( x+m \right)}^{2}}+n$的形式。 (1)${{x}^{2}}-6x$ (2)$4{{x}^{2}}-16x+3$ |
| 4501 | unknown | manual_review | low | possible_missing_problem_type,weak_classifier_match | 試判斷拋物線$y=3{{x}^{2}}+2x+4$的頂點落在哪一象限？ (A)第一象限 (B)第二象限 (C)第三象限 (D)第四象限。 |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: 無
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: 無

## 5. 人工審查與風險標記
- manual_review_problem_types: unknown
- risk_flags: possible_missing_problem_type, weak_classifier_match
- example 4468: Skill-specific classifier/rule pack is missing.
- example 4501: Skill-specific classifier/rule pack is missing.

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: False
- proposal_status: SKIPPED
- reason: 
- proposal_path: E:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_CompletingTheSquare_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_CompletingTheSquare

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
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_CompletingTheSquare
