# Gencode 第二階段建置報告

## 1. 摘要
- skill_id: vh_數學B1_AbsoluteValueInequality
- final_status: FOUNDATION_REPAIR_REQUIRED
- build_mode: normal
- input_phase1_report: C:\Python\Mathproject_tvet_mathB\reports\gencode_closed_loop\vh_數學B1_AbsoluteValueInequality_phase1_audit.json

## 2. Build Dependency Plan
- foundation_ready: false
- required_checkers: choice_label_checker, interval_checker
- missing_checkers: 無
- required_verifiers: choice_verifier, interval_verifier
- missing_verifiers: 無
- required_domain_functions: choices_unique_validator, interval_domain_function, interval_formatter
- missing_domain_functions: choices_unique_validator, interval_domain_function, interval_formatter
- required_generators: absolute_value_inequality_integer_solution_count_choice, absolute_value_inequality_linear_expression_basic, absolute_value_inequality_shifted_basic, absolute_value_inequality_zero_center_basic
- missing_generators: absolute_value_inequality_integer_solution_count_choice, absolute_value_inequality_linear_expression_basic, absolute_value_inequality_shifted_basic, absolute_value_inequality_zero_center_basic
- excluded_manual_review_problem_types: absolute_value_inequality_malformed_source_review

## 3. Preflight Result
- preflight_status: REPAIR_REQUIRED

## 4. Build Execution Status
- build_execution_status: SKIPPED

## 8. 建置缺口分析
- has_build_gaps: true
- gap_types: manual_review_unresolved, missing_domain_function, missing_generator

## 9. 修復計畫

| problem_type_id | gap_types | recommended_components | suggested_next_actions | severity |
| --- | --- | --- | --- | --- |
| absolute_value_inequality_integer_solution_count_choice | missing_generator | choice_label_checker, choice_verifier, choices_unique_validator | 建立 deterministic generator | high |
| absolute_value_inequality_linear_expression_basic | missing_domain_function, missing_generator | interval_checker, interval_verifier, interval_domain_function, interval_formatter | 建立 deterministic generator, 建立 domain solver / formatter | high |
| absolute_value_inequality_malformed_source_review | manual_review_unresolved | manual_review_marker, future_ai_judged_path | 保留 manual_review 或先修正來源題庫 | medium |
| absolute_value_inequality_shifted_basic | missing_domain_function, missing_generator | interval_checker, interval_verifier, interval_domain_function, interval_formatter | 建立 deterministic generator, 建立 domain solver / formatter | high |
| absolute_value_inequality_zero_center_basic | missing_domain_function, missing_generator | interval_checker, interval_verifier, interval_domain_function, interval_formatter | 建立 deterministic generator, 建立 domain solver / formatter | high |

本輪未執行 generator build，因 foundation 缺口尚未修復。
