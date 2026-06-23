# Skill Gencode Pipeline Report: vh_數學B1_DistanceBetweenTwoParallelLines

## Summary
```json
{
  "success": false,
  "final_status": "FAIL",
  "verified_problem_types": [],
  "pending_implementation": [
    "area_using_parallel_distance",
    "distance_between_parallel_lines",
    "parallel_lines_distance_single_choice",
    "solve_parameter_from_parallel_distance"
  ],
  "failed_problem_types": [],
  "manual_review": [],
  "visual_or_handwriting": [],
  "blocking_reasons": [
    "pending_implementation_not_empty",
    "runtime_missing_verified_problem_types",
    "skill_verify_failed",
    "unverified_observed_problem_type"
  ],
  "coverage_status": "INCOMPLETE_PROBLEM_TYPE_COVERAGE",
  "full_skill_coverage": false,
  "full_observed_coverage": false,
  "semantic_audit_summary": {
    "examples_total": 11,
    "examples_covered": 11,
    "required_fields_missing_count": 0,
    "audit_pass_count": 11,
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
      "area_using_parallel_distance": {
        "answer_type": "rational",
        "equivalence_type": "rational_equivalent",
        "checker_key": "rational_checker",
        "order_matters": true,
        "accepted_format_notes": [
          "rational or radical area"
        ],
        "canonical_answer_schema": {
          "type": "rational"
        }
      },
      "distance_between_parallel_lines": {
        "answer_type": "rational",
        "equivalence_type": "rational_equivalent",
        "checker_key": "rational_checker",
        "order_matters": true,
        "accepted_format_notes": [
          "rational or radical distance"
        ],
        "canonical_answer_schema": {
          "type": "rational"
        }
      },
      "parallel_lines_distance_single_choice": {
        "answer_type": "choice",
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker",
        "order_matters": true,
        "accepted_format_notes": [
          "A/B/C/D choice label"
        ],
        "canonical_answer_schema": {
          "type": "choice_label"
        }
      },
      "solve_parameter_from_parallel_distance": {
        "answer_type": "rational",
        "equivalence_type": "rational_equivalent",
        "checker_key": "rational_checker",
        "order_matters": true,
        "accepted_format_notes": [
          "rational, radical, or solution set parameter"
        ],
        "canonical_answer_schema": {
          "type": "rational"
        }
      }
    },
    "missing_answer_contract_problem_types": [],
    "missing_checker_key_problem_types": [],
    "invalid_equivalence_type_problem_types": [],
    "equivalence_test_required_problem_types": [
      "area_using_parallel_distance",
      "distance_between_parallel_lines",
      "parallel_lines_distance_single_choice",
      "solve_parameter_from_parallel_distance"
    ]
  },
  "runtime_problem_type_coverage": {
    "expected_problem_types": [],
    "observed_problem_types": [],
    "missing_problem_types": [],
    "sample_count": 30,
    "status": "fail"
  },
  "report": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoParallelLines_pipeline_report.md"
}
```

## Semantic Audit Summary
```json
{
  "examples_total": 11,
  "examples_covered": 11,
  "required_fields_missing_count": 0,
  "audit_pass_count": 11,
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
    "area_using_parallel_distance": {
      "answer_type": "rational",
      "equivalence_type": "rational_equivalent",
      "checker_key": "rational_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "rational or radical area"
      ],
      "canonical_answer_schema": {
        "type": "rational"
      }
    },
    "distance_between_parallel_lines": {
      "answer_type": "rational",
      "equivalence_type": "rational_equivalent",
      "checker_key": "rational_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "rational or radical distance"
      ],
      "canonical_answer_schema": {
        "type": "rational"
      }
    },
    "parallel_lines_distance_single_choice": {
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "A/B/C/D choice label"
      ],
      "canonical_answer_schema": {
        "type": "choice_label"
      }
    },
    "solve_parameter_from_parallel_distance": {
      "answer_type": "rational",
      "equivalence_type": "rational_equivalent",
      "checker_key": "rational_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "rational, radical, or solution set parameter"
      ],
      "canonical_answer_schema": {
        "type": "rational"
      }
    }
  },
  "missing_answer_contract_problem_types": [],
  "missing_checker_key_problem_types": [],
  "invalid_equivalence_type_problem_types": [],
  "equivalence_test_required_problem_types": [
    "area_using_parallel_distance",
    "distance_between_parallel_lines",
    "parallel_lines_distance_single_choice",
    "solve_parameter_from_parallel_distance"
  ]
}
```

## Problem Type Closed Loop
- area_using_parallel_distance: status=pending_implementation, reason=closed_loop_generator_not_implemented
- distance_between_parallel_lines: status=pending_implementation, reason=closed_loop_generator_not_implemented
- parallel_lines_distance_single_choice: status=pending_implementation, reason=closed_loop_generator_not_implemented
- solve_parameter_from_parallel_distance: status=pending_implementation, reason=closed_loop_generator_not_implemented

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
    "area_using_parallel_distance": {
      "answer_type": "rational",
      "equivalence_type": "rational_equivalent",
      "checker_key": "rational_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "rational or radical area"
      ],
      "canonical_answer_schema": {
        "type": "rational"
      }
    },
    "distance_between_parallel_lines": {
      "answer_type": "rational",
      "equivalence_type": "rational_equivalent",
      "checker_key": "rational_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "rational or radical distance"
      ],
      "canonical_answer_schema": {
        "type": "rational"
      }
    },
    "parallel_lines_distance_single_choice": {
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "A/B/C/D choice label"
      ],
      "canonical_answer_schema": {
        "type": "choice_label"
      }
    },
    "solve_parameter_from_parallel_distance": {
      "answer_type": "rational",
      "equivalence_type": "rational_equivalent",
      "checker_key": "rational_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "rational, radical, or solution set parameter"
      ],
      "canonical_answer_schema": {
        "type": "rational"
      }
    }
  },
  "missing_answer_contract_problem_types": [],
  "missing_checker_key_problem_types": [],
  "invalid_equivalence_type_problem_types": [],
  "equivalence_test_required_problem_types": [
    "area_using_parallel_distance",
    "distance_between_parallel_lines",
    "parallel_lines_distance_single_choice",
    "solve_parameter_from_parallel_distance"
  ]
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
  "stdout": "{\"success\": true, \"examples_count\": 11, \"report\": \"D:\\\\Python\\\\Mathproject_tvet_mathB\\\\reports\\\\gencode_closed_loop\\\\vh_數學B1_DistanceBetweenTwoParallelLines_inventory_report.md\", \"package_dir\": \"D:\\\\Python\\\\Mathproject_tvet_mathB\\\\agent_skills_v2\\\\_generated\\\\vh_數學B1_DistanceBetweenTwoParallelLines\"}\n",
  "stderr": "",
  "parsed": {
    "success": true,
    "examples_count": 11,
    "report": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoParallelLines_inventory_report.md",
    "package_dir": "D:\\Python\\Mathproject_tvet_mathB\\agent_skills_v2\\_generated\\vh_數學B1_DistanceBetweenTwoParallelLines"
  }
}
```

## Verify
```json
{
  "stdout": "{\"success\": false, \"report\": \"D:\\\\Python\\\\Mathproject_tvet_mathB\\\\reports\\\\gencode_closed_loop\\\\vh_數學B1_DistanceBetweenTwoParallelLines_verify_report.md\", \"first_error\": \"registry has no verified candidate for skill\", \"runtime_problem_type_coverage\": {\"expected_problem_types\": [], \"observed_problem_types\": [], \"missing_problem_types\": [], \"sample_count\": 30, \"status\": \"fail\"}}\n",
  "stderr": "",
  "parsed": {
    "success": false,
    "report": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoParallelLines_verify_report.md",
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
