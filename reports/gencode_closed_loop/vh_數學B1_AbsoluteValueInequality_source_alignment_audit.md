# Gencode Source Alignment Audit

## 1. 摘要
- skill_id: vh_數學B1_AbsoluteValueInequality
- examples_total: 10
- examples_checked: 10
- alignment_status_counts: {'PARTIAL': 6, 'PASS': 4}

## 2. 例題語意分類統計
- source_form_counts: {'multi_part_abs_ineq_solving': 5, 'single_linear_abs_ineq': 5}
- problem_type_counts: {'absolute_value_inequality_zero_center_basic': 3, 'absolute_value_inequality_shifted_basic': 2, 'absolute_value_inequality_linear_expression_basic': 4, 'absolute_value_inequality_integer_solution_count_choice': 1}

## 3. 逐題對照表
- example_id: 4400
  source_form_category: multi_part_abs_ineq_solving
  problem_type_id: absolute_value_inequality_zero_center_basic
  alignment_status: PARTIAL
- example_id: 4402
  source_form_category: multi_part_abs_ineq_solving
  problem_type_id: absolute_value_inequality_shifted_basic
  alignment_status: PARTIAL
- example_id: 4403
  source_form_category: multi_part_abs_ineq_solving
  problem_type_id: absolute_value_inequality_shifted_basic
  alignment_status: PARTIAL
- example_id: 4404
  source_form_category: single_linear_abs_ineq
  problem_type_id: absolute_value_inequality_linear_expression_basic
  alignment_status: PASS
- example_id: 4405
  source_form_category: single_linear_abs_ineq
  problem_type_id: absolute_value_inequality_linear_expression_basic
  alignment_status: PASS
- example_id: 4406
  source_form_category: single_linear_abs_ineq
  problem_type_id: absolute_value_inequality_linear_expression_basic
  alignment_status: PASS
- example_id: 4407
  source_form_category: single_linear_abs_ineq
  problem_type_id: absolute_value_inequality_linear_expression_basic
  alignment_status: PASS
- example_id: 4409
  source_form_category: multi_part_abs_ineq_solving
  problem_type_id: absolute_value_inequality_zero_center_basic
  alignment_status: PARTIAL
- example_id: 4413
  source_form_category: multi_part_abs_ineq_solving
  problem_type_id: absolute_value_inequality_zero_center_basic
  alignment_status: PARTIAL
- example_id: 4499
  source_form_category: single_linear_abs_ineq
  problem_type_id: absolute_value_inequality_integer_solution_count_choice
  alignment_status: PARTIAL

## 4. 疑似分類錯誤

## 5. Runtime 未覆蓋或低覆蓋題型
- multi_part_abs_ineq_solving

## 6. 建議修正
- 新增或擴充 multi-part 絕對值不等式生成能力，避免僅用 single-form 覆蓋。
- 對 underrepresented source form 建立 source-aligned generator 或 wrapper 出題策略。
