# Skill Gencode Pipeline Report: vh_數學B1_DistanceBetweenTwoPointsInPlane

## Summary
```json
{
  "success": true,
  "final_status": "PASS",
  "verified_problem_types": [
    "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
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
    "audit_pass_count": 0,
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
      "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2": {
        "answer_type": "text_short",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "order_matters": true,
        "accepted_format_notes": [
          "exact string or simplified radical like 5 or sqrt(17)"
        ],
        "canonical_answer_schema": {
          "type": "text_short"
        }
      },
      "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2": {
        "answer_type": "solution_set",
        "equivalence_type": "unordered_solution_set",
        "checker_key": "solution_set_checker",
        "order_matters": false,
        "accepted_format_notes": [
          "unordered solution set like 2,14"
        ],
        "canonical_answer_schema": {
          "type": "solution_set"
        }
      }
    },
    "missing_answer_contract_problem_types": [],
    "missing_checker_key_problem_types": [],
    "invalid_equivalence_type_problem_types": [],
    "equivalence_test_required_problem_types": [
      "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
    ]
  },
  "runtime_problem_type_coverage": {
    "expected_problem_types": [
      "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
    ],
    "observed_problem_types": [
      "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
    ],
    "missing_problem_types": [],
    "sample_count": 30,
    "status": "pass"
  },
  "report": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_pipeline_report.md"
}
```

## Semantic Audit Summary
```json
{
  "examples_total": 4,
  "examples_covered": 4,
  "required_fields_missing_count": 0,
  "audit_pass_count": 0,
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
    "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2": {
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "exact string or simplified radical like 5 or sqrt(17)"
      ],
      "canonical_answer_schema": {
        "type": "text_short"
      }
    },
    "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2": {
      "answer_type": "solution_set",
      "equivalence_type": "unordered_solution_set",
      "checker_key": "solution_set_checker",
      "order_matters": false,
      "accepted_format_notes": [
        "unordered solution set like 2,14"
      ],
      "canonical_answer_schema": {
        "type": "solution_set"
      }
    }
  },
  "missing_answer_contract_problem_types": [],
  "missing_checker_key_problem_types": [],
  "invalid_equivalence_type_problem_types": [],
  "equivalence_test_required_problem_types": [
    "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
  ]
}
```

## Problem Type Closed Loop
- short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2: status=verified
- short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2: status=verified

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
    "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2": {
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "order_matters": true,
      "accepted_format_notes": [
        "exact string or simplified radical like 5 or sqrt(17)"
      ],
      "canonical_answer_schema": {
        "type": "text_short"
      }
    },
    "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2": {
      "answer_type": "solution_set",
      "equivalence_type": "unordered_solution_set",
      "checker_key": "solution_set_checker",
      "order_matters": false,
      "accepted_format_notes": [
        "unordered solution set like 2,14"
      ],
      "canonical_answer_schema": {
        "type": "solution_set"
      }
    }
  },
  "missing_answer_contract_problem_types": [],
  "missing_checker_key_problem_types": [],
  "invalid_equivalence_type_problem_types": [],
  "equivalence_test_required_problem_types": [
    "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
  ]
}
```

## Runtime ProblemType Coverage
```json
{
  "expected_problem_types": [
    "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
  ],
  "observed_problem_types": [
    "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
  ],
  "missing_problem_types": [],
  "sample_count": 30,
  "status": "pass"
}
```

## Inventory
```json
{
  "stdout": "{\"success\": true, \"examples_count\": 4, \"report\": \"E:\\\\Python\\\\Mathproject_tvet_mathB\\\\reports\\\\gencode_closed_loop\\\\vh_數學B1_DistanceBetweenTwoPointsInPlane_inventory_report.md\", \"package_dir\": \"E:\\\\Python\\\\Mathproject_tvet_mathB\\\\agent_skills_v2\\\\_generated\\\\vh_數學B1_DistanceBetweenTwoPointsInPlane\"}\n",
  "stderr": "",
  "parsed": {
    "success": true,
    "examples_count": 4,
    "report": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_inventory_report.md",
    "package_dir": "E:\\Python\\Mathproject_tvet_mathB\\agent_skills_v2\\_generated\\vh_數學B1_DistanceBetweenTwoPointsInPlane"
  }
}
```

## Verify
```json
{
  "stdout": "{\"success\": true, \"report\": \"E:\\\\Python\\\\Mathproject_tvet_mathB\\\\reports\\\\gencode_closed_loop\\\\vh_數學B1_DistanceBetweenTwoPointsInPlane_verify_report.md\", \"first_error\": \"\", \"runtime_problem_type_coverage\": {\"expected_problem_types\": [\"short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2\", \"short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2\"], \"observed_problem_types\": [\"short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2\", \"short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2\"], \"missing_problem_types\": [], \"sample_count\": 30, \"status\": \"pass\"}}\n",
  "stderr": "",
  "parsed": {
    "success": true,
    "report": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_verify_report.md",
    "first_error": "",
    "runtime_problem_type_coverage": {
      "expected_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "observed_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "missing_problem_types": [],
      "sample_count": 30,
      "status": "pass"
    }
  }
}
```
