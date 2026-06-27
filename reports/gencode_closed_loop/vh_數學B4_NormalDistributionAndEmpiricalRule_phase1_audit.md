# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B4_NormalDistributionAndEmpiricalRule
- 階段狀態: AUDIT_FAIL
- 建議下一步: phase2_build
- 題庫例題總數: 6
- 已分類例題數: 6
- 來源覆蓋判定: FULL_OBSERVED_COVERAGE_CANDIDATE

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |
| compare_distribution_spread | rule_only | 3859 |  |  |  | classified |
| empirical_rule_population_count | rule_only | 3856, 3857, 3858, 3897, 3898 |  |  |  | classified |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 3856 | empirical_rule_population_count | rule_only | high |  | 某校 2000 個學生，英文成績呈常態分配，平均 55 分，標準差 5 分。求：(1) 50~60 分人數；(2) 60 分以上人數；(3) 低於 40 分人數。 |
| 3857 | empirical_rule_population_count | rule_only | high |  | 某校 1000 個學生，英文成績呈常態分配，平均 60 分，標準差 10 分。求：(1) 高於 60 分人數；(2) 50 分以下人數；(3) 50~70 分人數。 |
| 3858 | empirical_rule_population_count | rule_only | high |  | 某校 2000 個學生，英文成績呈常態分配，平均 55 分，標準差 5 分。求：(1) 45~65 分人數；(2) 50 分以下人數。 |
| 3859 | compare_distribution_spread | rule_only | high |  | 某年統測，甲、乙兩科成績直方圖如圖所示，下列敘述何者正確？(A)甲平均比乙大；(B)甲中位數比乙大；(C)甲全距比乙大；(D)甲標準差比乙大。 |
| 3897 | empirical_rule_population_count | rule_only | high |  | 某校500位新生第一次數學段考成績平均分數是58分，標準差是4分，若成績呈常態分配，則成績介於62到54分的學生約有多少人？(A) 170 (B) 250 (C) 340 (D) 400。 |
| 3898 | empirical_rule_population_count | rule_only | high |  | 某次數學考試共有1000人參加。若成績呈常態分配，且平均數為62分，標準差為8分，則成績低於70分的人數為何？ (A)介於581人與660人之間 (B)介於661人與740人之間 (C)介於741人與820人之間 ... |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: compare_distribution_spread, empirical_rule_population_count
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: 無

## 5. 人工審查與風險標記
- manual_review_problem_types: 無
- risk_flags: 無

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: False
- proposal_status: SKIPPED
- reason: 
- proposal_path: E:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B4_NormalDistributionAndEmpiricalRule_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B4_NormalDistributionAndEmpiricalRule

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
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B4_NormalDistributionAndEmpiricalRule
