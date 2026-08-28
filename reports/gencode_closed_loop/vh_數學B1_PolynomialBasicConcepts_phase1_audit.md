# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_PolynomialBasicConcepts
- 階段狀態: AUDIT_FAIL
- 建議下一步: phase2_build
- 題庫例題總數: 9
- 已分類例題數: 9
- 來源覆蓋判定: FULL_OBSERVED_COVERAGE_CANDIDATE

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |
| polynomial_degree_product_sum | deterministic_expression | 4716 |  |  |  | classified |
| polynomial_descending_power_properties | deterministic_expression | 4609 |  |  |  | classified |
| polynomial_descending_power_table | deterministic_expression | 4618, 4629 |  |  |  | classified |
| polynomial_param_degree_constraint | deterministic_expression | 4610, 4619, 4630 |  |  |  | classified |
| zero_polynomial_find_coeffs | deterministic_expression | 4620, 4631 |  |  |  | classified |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4609 | polynomial_descending_power_properties | deterministic_expression | high |  | 設$f\left( x \right)=4{{x}^{2}}-5{{x}^{3}}-x+3$，試求：(1) $f\left( x \right)$依降冪排列 (2)$\deg f\left( x \right)$(... |
| 4610 | polynomial_param_degree_constraint | deterministic_expression | high |  | (1) 設多項式$f\left( x \right)=\left( a-2 \right){{x}^{3}}+\left( b+3 \right){{x}^{2}}-\left( a-b \right)x+3$，且... |
| 4618 | polynomial_descending_power_table | deterministic_expression | high |  | 已知$f\left( x \right)=2{{x}^{2}}+{{x}^{3}}-3x-5$，$g\left( x \right)=-3{{x}^{2}}+{{x}^{4}}-2x+{{x}^{3}}+1$，試按... |
| 4619 | polynomial_param_degree_constraint | deterministic_expression | high |  | 多項式$f\left( x \right)=\left( a-2 \right){{x}^{4}}+\left( b+3 \right){{x}^{3}}+\left( 2a-b \right){{x}^{2}}+... |
| 4620 | zero_polynomial_find_coeffs | deterministic_expression | high |  | 設$f\left( x \right)=\left( a+2 \right){{x}^{3}}+\left( b-1 \right){{x}^{2}}+cx+d-5$為一零多項式，試求a、b、c、d之值。 |
| 4629 | polynomial_descending_power_table | deterministic_expression | high |  | 已知$f\left( x \right)=-5{{x}^{2}}+{{x}^{3}}-1$，$g\left( x \right)=-3{{x}^{2}}-x+2{{x}^{3}}-1$，試按降冪排列完成下表： |
| 4630 | polynomial_param_degree_constraint | deterministic_expression | high |  | 多項式$f\left( x \right)=\left( 2a+2 \right){{x}^{4}}+\left( b-1 \right){{x}^{3}}+\left( a+2b \right){{x}^{2}}... |
| 4631 | zero_polynomial_find_coeffs | deterministic_expression | high |  | 設$g\left( x \right)=\left( a+1 \right){{x}^{2}}+\left( b-2 \right)x+2c-4$為一零多項式，試求a、b、c之值。. |
| 4716 | polynomial_degree_product_sum | deterministic_expression | high |  | 設$f\left( x \right)$為四次多項式，$g\left( x \right)$為五次多項式，$h\left( x \right)=f\left( x \right)\times g\left( x \... |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: polynomial_degree_product_sum, polynomial_descending_power_properties, polynomial_descending_power_table, polynomial_param_degree_constraint, zero_polynomial_find_coeffs
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: 無

## 5. 人工審查與風險標記
- manual_review_problem_types: 無
- risk_flags: 無

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: False
- proposal_status: SKIPPED
- reason: 
- proposal_path: C:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_PolynomialBasicConcepts_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_PolynomialBasicConcepts

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
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_PolynomialBasicConcepts
