# Gencode 第一階段盤點報告

## 1. 摘要
- skill_id: vh_數學B1_AbsoluteValueInequality
- 階段狀態: AUDIT_PARTIAL
- 建議下一步: phase2_build
- 題庫例題總數: 10
- 已分類例題數: 10
- 來源覆蓋判定: INSUFFICIENT_SOURCE_EXAMPLES

## 2. 題型覆蓋表

| 題型 ID | 執行類型 | 例題 ID | 答案型態 | 等價判分型態 | 判分器 | 狀態 |
| --- | --- | --- | --- | --- | --- | --- |
| absolute_value_inequality_integer_solution_count_choice | deterministic_choice | 4499 | choice | choice_label | choice_label_checker | classified |
| absolute_value_inequality_linear_expression_basic | deterministic_expression | 4404, 4405, 4406, 4407 | interval_set | interval_set | interval_checker | classified |
| absolute_value_inequality_malformed_source_review | manual_review | 4409 | manual_review | manual_review_or_ai_judged | manual_review_checker | manual_review |
| absolute_value_inequality_shifted_basic | deterministic_expression | 4402, 4403 | interval_set | interval_set | interval_checker | classified |
| absolute_value_inequality_zero_center_basic | deterministic_expression | 4400, 4413 | interval_set | interval_set | interval_checker | classified |

## 3. 例題分類表

| 例題 ID | 題型 ID | 執行類型 | 信心 | 風險標記 | 題目預覽 |
| --- | --- | --- | --- | --- | --- |
| 4400 | absolute_value_inequality_zero_center_basic | deterministic_expression | high |  | 試求下列不等式之解： (1)$\| x \|$<= 8 (2)$\| x \|$> 10 (3)$\| x \|$< 7 (4)$\| x \|$>= 12 |
| 4402 | absolute_value_inequality_shifted_basic | deterministic_expression | high |  | 解下列不等式： (1)$\| x-2 \|<= 4$ (2)$\| x+5 \|>1$ |
| 4403 | absolute_value_inequality_shifted_basic | deterministic_expression | high |  | 解下列不等式： (1)$\| x-3 \|<2$ (2)$\| x+5 \|>= 4$ |
| 4404 | absolute_value_inequality_linear_expression_basic | deterministic_expression | high |  | 解不等式$\| 4x+1 \|<= 6$。 |
| 4405 | absolute_value_inequality_linear_expression_basic | deterministic_expression | high |  | 解不等式$\| 2x-3 \|>1$。 |
| 4406 | absolute_value_inequality_linear_expression_basic | deterministic_expression | high |  | 解不等式$\| 3x-1 \|>= 7$。 |
| 4407 | absolute_value_inequality_linear_expression_basic | deterministic_expression | high |  | 解不等式$\| 5x+3 \|<7$。 |
| 4409 | absolute_value_inequality_malformed_source_review | manual_review | medium | source_text_malformed,needs_import_review | 試求下列不等式之解：(1)$\| x \|$3 (2) $\| x \|$ >= 4 |
| 4413 | absolute_value_inequality_zero_center_basic | deterministic_expression | high |  | 試求下列不等式之解：(1) $\| x \|$ <= 6 (2) $\| x \|$> 5 |
| 4499 | absolute_value_inequality_integer_solution_count_choice | deterministic_choice | high |  | 試求滿足不等式$\| 3x-2 \|<= 8$的整數x共有多少個？ (A) 4 (B) 5 (C) 6 (D) 7。 |

## 4. 答案規格檢查
- 缺少 answer_contract 的題型: 無
- 缺少 checker_key 的題型: 無
- 需要等價答案測試的題型: absolute_value_inequality_integer_solution_count_choice, absolute_value_inequality_linear_expression_basic, absolute_value_inequality_malformed_source_review, absolute_value_inequality_shifted_basic, absolute_value_inequality_zero_center_basic

## 5. 人工審查與風險標記
- manual_review_problem_types: absolute_value_inequality_malformed_source_review
- risk_flags: needs_import_review, source_text_malformed
- example 4409: Malformed absolute value inequality source text.

## 6. Classifier Proposal 狀態
- classifier_proposal.enabled: False
- proposal_status: SKIPPED
- reason: 
- proposal_path: C:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_AbsoluteValueInequality_classifier_proposal.json
- promote_ready: False
- promote_command_suggestion: python scripts\gencode_promote_classifier_proposal.py --skill-id vh_數學B1_AbsoluteValueInequality

## 7. 下一步建議
python scripts\gencode_pipeline_phase2_build.py --skill-id vh_數學B1_AbsoluteValueInequality
