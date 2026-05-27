# Skill Gencode Pipeline Report: vh_數學B1_AbsoluteValueInequality

## Summary
```json
{
  "success": false,
  "final_status": "FAIL",
  "verified_problem_types": [],
  "pending_implementation": [],
  "failed_problem_types": [
    "absolute_value_inequality_integer_solution_count_choice",
    "absolute_value_inequality_linear_expression_basic",
    "absolute_value_inequality_shifted_basic",
    "absolute_value_inequality_zero_center_basic"
  ],
  "manual_review": [],
  "visual_or_handwriting": [],
  "blocking_reasons": [
    "failed_problem_type_not_empty",
    "manual_review_not_resolved",
    "missing_answer_contract_problem_types",
    "runtime_missing_verified_problem_types",
    "skill_verify_failed",
    "unverified_observed_problem_type"
  ],
  "coverage_status": "INCOMPLETE_PROBLEM_TYPE_COVERAGE",
  "full_skill_coverage": false,
  "full_observed_coverage": false,
  "semantic_audit_summary": {
    "examples_total": 10,
    "examples_covered": 10,
    "required_fields_missing_count": 0,
    "audit_pass_count": 9,
    "audit_review_required_count": 1,
    "examples_with_risk_flags": [
      {
        "example_id": 4409,
        "flags": [
          "source_text_malformed",
          "needs_import_review"
        ]
      }
    ],
    "possible_missing_problem_types": [],
    "answer_contract_equivalence_type_whitelist": [
      "algebraic_equivalent",
      "choice_label",
      "exact_string",
      "interval_set",
      "manual_review_or_ai_judged",
      "numeric_exact",
      "rational_equivalent",
      "unordered_solution_set"
    ],
    "observed_problem_type_answer_contracts": {
      "absolute_value_inequality_integer_solution_count_choice": null,
      "absolute_value_inequality_linear_expression_basic": null,
      "absolute_value_inequality_shifted_basic": null,
      "absolute_value_inequality_zero_center_basic": null
    },
    "missing_answer_contract_problem_types": [
      "absolute_value_inequality_integer_solution_count_choice",
      "absolute_value_inequality_linear_expression_basic",
      "absolute_value_inequality_shifted_basic",
      "absolute_value_inequality_zero_center_basic"
    ],
    "missing_checker_key_problem_types": [],
    "invalid_equivalence_type_problem_types": [],
    "equivalence_test_required_problem_types": []
  },
  "runtime_problem_type_coverage": {
    "expected_problem_types": [],
    "observed_problem_types": [],
    "missing_problem_types": [],
    "sample_count": 30,
    "status": "fail"
  },
  "report": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_pipeline_report.md"
}
```

## Semantic Audit Summary
```json
{
  "examples_total": 10,
  "examples_covered": 10,
  "required_fields_missing_count": 0,
  "audit_pass_count": 9,
  "audit_review_required_count": 1,
  "examples_with_risk_flags": [
    {
      "example_id": 4409,
      "flags": [
        "source_text_malformed",
        "needs_import_review"
      ]
    }
  ],
  "possible_missing_problem_types": [],
  "answer_contract_equivalence_type_whitelist": [
    "algebraic_equivalent",
    "choice_label",
    "exact_string",
    "interval_set",
    "manual_review_or_ai_judged",
    "numeric_exact",
    "rational_equivalent",
    "unordered_solution_set"
  ],
  "observed_problem_type_answer_contracts": {
    "absolute_value_inequality_integer_solution_count_choice": null,
    "absolute_value_inequality_linear_expression_basic": null,
    "absolute_value_inequality_shifted_basic": null,
    "absolute_value_inequality_zero_center_basic": null
  },
  "missing_answer_contract_problem_types": [
    "absolute_value_inequality_integer_solution_count_choice",
    "absolute_value_inequality_linear_expression_basic",
    "absolute_value_inequality_shifted_basic",
    "absolute_value_inequality_zero_center_basic"
  ],
  "missing_checker_key_problem_types": [],
  "invalid_equivalence_type_problem_types": [],
  "equivalence_test_required_problem_types": []
}
```

## Problem Type Closed Loop
- absolute_value_inequality_integer_solution_count_choice: status=failed, reason=closed_loop_failed
- absolute_value_inequality_linear_expression_basic: status=failed, reason=closed_loop_failed
- absolute_value_inequality_shifted_basic: status=failed, reason=closed_loop_failed
- absolute_value_inequality_zero_center_basic: status=failed, reason=closed_loop_failed

## Answer Contract Coverage
```json
{
  "equivalence_type_whitelist": [
    "algebraic_equivalent",
    "choice_label",
    "exact_string",
    "interval_set",
    "manual_review_or_ai_judged",
    "numeric_exact",
    "rational_equivalent",
    "unordered_solution_set"
  ],
  "observed_problem_type_answer_contracts": {
    "absolute_value_inequality_integer_solution_count_choice": null,
    "absolute_value_inequality_linear_expression_basic": null,
    "absolute_value_inequality_shifted_basic": null,
    "absolute_value_inequality_zero_center_basic": null
  },
  "missing_answer_contract_problem_types": [
    "absolute_value_inequality_integer_solution_count_choice",
    "absolute_value_inequality_linear_expression_basic",
    "absolute_value_inequality_shifted_basic",
    "absolute_value_inequality_zero_center_basic"
  ],
  "missing_checker_key_problem_types": [],
  "invalid_equivalence_type_problem_types": [],
  "equivalence_test_required_problem_types": []
}
```

## Runtime ProblemType Coverage
```json
{
  "expected_problem_types": [],
  "observed_problem_types": [],
  "missing_problem_types": [],
  "sample_count": 30,
  "status": "fail"
}
```

## Inventory
```json
{
  "stdout": "{\"success\": true, \"examples_count\": 10, \"report\": \"C:\\\\Python\\\\Mathproject_tvet_mathB\\\\reports\\\\gencode_closed_loop\\\\vh_數學B1_AbsoluteValueInequality_inventory_report.md\", \"package_dir\": \"C:\\\\Python\\\\Mathproject_tvet_mathB\\\\agent_skills_v2\\\\_generated\\\\vh_數學B1_AbsoluteValueInequality\"}\n",
  "stderr": "",
  "parsed": {
    "success": true,
    "examples_count": 10,
    "report": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_inventory_report.md",
    "package_dir": "C:\\Python\\Mathproject_tvet_mathB\\agent_skills_v2\\_generated\\vh_數學B1_AbsoluteValueInequality"
  }
}
```

## Verify
```json
{
  "stdout": "{\"success\": false, \"report\": \"C:\\\\Python\\\\Mathproject_tvet_mathB\\\\reports\\\\gencode_closed_loop\\\\vh_數學B1_AbsoluteValueInequality_verify_report.md\", \"first_error\": \"registry has no verified candidate for skill\", \"runtime_problem_type_coverage\": {\"expected_problem_types\": [], \"observed_problem_types\": [], \"missing_problem_types\": [], \"sample_count\": 30, \"status\": \"fail\"}}\n",
  "stderr": "",
  "parsed": {
    "success": false,
    "report": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_verify_report.md",
    "first_error": "registry has no verified candidate for skill",
    "runtime_problem_type_coverage": {
      "expected_problem_types": [],
      "observed_problem_types": [],
      "missing_problem_types": [],
      "sample_count": 30,
      "status": "fail"
    }
  }
}
```
