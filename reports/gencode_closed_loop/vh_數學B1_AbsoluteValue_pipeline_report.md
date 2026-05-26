# Skill Gencode Pipeline Report: vh_數學B1_AbsoluteValue

## Summary
```json
{
  "success": true,
  "final_status": "PASS",
  "verified_problem_types": [
    "absolute_value_distance_between_two_points",
    "absolute_value_distance_from_zero",
    "absolute_value_equation_basic",
    "absolute_value_numeric_evaluation"
  ],
  "pending_implementation": [],
  "failed_problem_types": [],
  "manual_review": [],
  "visual_or_handwriting": [],
  "blocking_reasons": [],
  "coverage_status": "FULL_OBSERVED_COVERAGE",
  "full_skill_coverage": true,
  "full_observed_coverage": true,
  "semantic_audit_summary": {
    "examples_total": 4,
    "examples_covered": 4,
    "required_fields_missing_count": 0,
    "audit_pass_count": 4,
    "audit_review_required_count": 0,
    "examples_with_risk_flags": [],
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
      "absolute_value_distance_between_two_points": {
        "answer_type": "integer",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "order_matters": true,
        "accepted_format_notes": [
          "single integer distance"
        ],
        "canonical_answer_schema": "int"
      },
      "absolute_value_distance_from_zero": {
        "answer_type": "choice",
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker",
        "order_matters": true,
        "accepted_format_notes": [
          "A/a/(A)/A./1/choice text aliases accepted by label checker"
        ],
        "canonical_answer_schema": "choice_label"
      },
      "absolute_value_equation_basic": {
        "answer_type": "solution_set",
        "equivalence_type": "unordered_solution_set",
        "checker_key": "solution_set_checker",
        "order_matters": false,
        "accepted_format_notes": [
          "17,-17",
          "-17,17",
          "x=17 或 x=-17",
          "x=-17 或 x=17",
          "±17"
        ],
        "canonical_answer_schema": "set[int]"
      },
      "absolute_value_numeric_evaluation": {
        "answer_type": "integer",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "order_matters": true,
        "accepted_format_notes": [
          "single integer answer"
        ],
        "canonical_answer_schema": "int"
      }
    },
    "missing_answer_contract_problem_types": [],
    "missing_checker_key_problem_types": [],
    "invalid_equivalence_type_problem_types": [],
    "equivalence_test_required_problem_types": [
      "absolute_value_distance_from_zero",
      "absolute_value_equation_basic"
    ]
  },
  "runtime_problem_type_coverage": {
    "expected_problem_types": [
      "absolute_value_distance_between_two_points",
      "absolute_value_distance_from_zero",
      "absolute_value_equation_basic",
      "absolute_value_numeric_evaluation"
    ],
    "observed_problem_types": [
      "absolute_value_distance_between_two_points",
      "absolute_value_distance_from_zero",
      "absolute_value_equation_basic",
      "absolute_value_numeric_evaluation"
    ],
    "missing_problem_types": [],
    "sample_count": 30,
    "status": "pass"
  },
  "report": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValue_pipeline_report.md"
}
```

## Semantic Audit Summary
```json
{
  "examples_total": 4,
  "examples_covered": 4,
  "required_fields_missing_count": 0,
  "audit_pass_count": 4,
  "audit_review_required_count": 0,
  "examples_with_risk_flags": [],
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
    "absolute_value_distance_between_two_points": {
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "single integer distance"
      ],
      "canonical_answer_schema": "int"
    },
    "absolute_value_distance_from_zero": {
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "A/a/(A)/A./1/choice text aliases accepted by label checker"
      ],
      "canonical_answer_schema": "choice_label"
    },
    "absolute_value_equation_basic": {
      "answer_type": "solution_set",
      "equivalence_type": "unordered_solution_set",
      "checker_key": "solution_set_checker",
      "order_matters": false,
      "accepted_format_notes": [
        "17,-17",
        "-17,17",
        "x=17 或 x=-17",
        "x=-17 或 x=17",
        "±17"
      ],
      "canonical_answer_schema": "set[int]"
    },
    "absolute_value_numeric_evaluation": {
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "single integer answer"
      ],
      "canonical_answer_schema": "int"
    }
  },
  "missing_answer_contract_problem_types": [],
  "missing_checker_key_problem_types": [],
  "invalid_equivalence_type_problem_types": [],
  "equivalence_test_required_problem_types": [
    "absolute_value_distance_from_zero",
    "absolute_value_equation_basic"
  ]
}
```

## Problem Type Closed Loop
- absolute_value_distance_between_two_points: status=verified
- absolute_value_equation_basic: status=verified

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
    "absolute_value_distance_between_two_points": {
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "single integer distance"
      ],
      "canonical_answer_schema": "int"
    },
    "absolute_value_distance_from_zero": {
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "A/a/(A)/A./1/choice text aliases accepted by label checker"
      ],
      "canonical_answer_schema": "choice_label"
    },
    "absolute_value_equation_basic": {
      "answer_type": "solution_set",
      "equivalence_type": "unordered_solution_set",
      "checker_key": "solution_set_checker",
      "order_matters": false,
      "accepted_format_notes": [
        "17,-17",
        "-17,17",
        "x=17 或 x=-17",
        "x=-17 或 x=17",
        "±17"
      ],
      "canonical_answer_schema": "set[int]"
    },
    "absolute_value_numeric_evaluation": {
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "single integer answer"
      ],
      "canonical_answer_schema": "int"
    }
  },
  "missing_answer_contract_problem_types": [],
  "missing_checker_key_problem_types": [],
  "invalid_equivalence_type_problem_types": [],
  "equivalence_test_required_problem_types": [
    "absolute_value_distance_from_zero",
    "absolute_value_equation_basic"
  ]
}
```

## Runtime ProblemType Coverage
```json
{
  "expected_problem_types": [
    "absolute_value_distance_between_two_points",
    "absolute_value_distance_from_zero",
    "absolute_value_equation_basic",
    "absolute_value_numeric_evaluation"
  ],
  "observed_problem_types": [
    "absolute_value_distance_between_two_points",
    "absolute_value_distance_from_zero",
    "absolute_value_equation_basic",
    "absolute_value_numeric_evaluation"
  ],
  "missing_problem_types": [],
  "sample_count": 30,
  "status": "pass"
}
```

## Inventory
```json
{
  "stdout": "{\"success\": true, \"examples_count\": 4, \"report\": \"C:\\\\Python\\\\Mathproject_tvet_mathB\\\\reports\\\\gencode_closed_loop\\\\vh_數學B1_AbsoluteValue_inventory_report.md\", \"package_dir\": \"C:\\\\Python\\\\Mathproject_tvet_mathB\\\\agent_skills_v2\\\\vocational_math_b1\\\\chapter_1\\\\section_1_1_number_line_absolute_value\"}\n",
  "stderr": "",
  "parsed": {
    "success": true,
    "examples_count": 4,
    "report": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValue_inventory_report.md",
    "package_dir": "C:\\Python\\Mathproject_tvet_mathB\\agent_skills_v2\\vocational_math_b1\\chapter_1\\section_1_1_number_line_absolute_value"
  }
}
```

## Verify
```json
{
  "stdout": "{\"success\": true, \"report\": \"C:\\\\Python\\\\Mathproject_tvet_mathB\\\\reports\\\\gencode_closed_loop\\\\vh_數學B1_AbsoluteValue_verify_report.md\", \"first_error\": \"\", \"runtime_problem_type_coverage\": {\"expected_problem_types\": [\"absolute_value_distance_between_two_points\", \"absolute_value_distance_from_zero\", \"absolute_value_equation_basic\", \"absolute_value_numeric_evaluation\"], \"observed_problem_types\": [\"absolute_value_distance_between_two_points\", \"absolute_value_distance_from_zero\", \"absolute_value_equation_basic\", \"absolute_value_numeric_evaluation\"], \"missing_problem_types\": [], \"sample_count\": 30, \"status\": \"pass\"}}\n",
  "stderr": "",
  "parsed": {
    "success": true,
    "report": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValue_verify_report.md",
    "first_error": "",
    "runtime_problem_type_coverage": {
      "expected_problem_types": [
        "absolute_value_distance_between_two_points",
        "absolute_value_distance_from_zero",
        "absolute_value_equation_basic",
        "absolute_value_numeric_evaluation"
      ],
      "observed_problem_types": [
        "absolute_value_distance_between_two_points",
        "absolute_value_distance_from_zero",
        "absolute_value_equation_basic",
        "absolute_value_numeric_evaluation"
      ],
      "missing_problem_types": [],
      "sample_count": 30,
      "status": "pass"
    }
  }
}
```
