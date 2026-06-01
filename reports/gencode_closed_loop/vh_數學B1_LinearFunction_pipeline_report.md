# Skill Gencode Pipeline Report: vh_數學B1_LinearFunction

## Summary
```json
{
  "success": false,
  "final_status": "FAIL",
  "verified_problem_types": [],
  "pending_implementation": [],
  "failed_problem_types": [],
  "manual_review": [],
  "visual_or_handwriting": [],
  "blocking_reasons": [
    "manual_review_not_resolved",
    "possible_missing_problem_type",
    "runtime_missing_verified_problem_types",
    "skill_verify_failed"
  ],
  "coverage_status": "INCOMPLETE_PROBLEM_TYPE_COVERAGE",
  "full_skill_coverage": false,
  "full_observed_coverage": false,
  "semantic_audit_summary": {
    "examples_total": 17,
    "examples_covered": 17,
    "required_fields_missing_count": 0,
    "audit_pass_count": 0,
    "audit_review_required_count": 17,
    "examples_with_risk_flags": [
      {
        "example_id": 4424,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4425,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4426,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4430,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4431,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4433,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4434,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4441,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4442,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4444,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4445,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4446,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4448,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4449,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4500,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4515,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      },
      {
        "example_id": 4516,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      }
    ],
    "possible_missing_problem_types": [
      4424,
      4425,
      4426,
      4430,
      4431,
      4433,
      4434,
      4441,
      4442,
      4444,
      4445,
      4446,
      4448,
      4449,
      4500,
      4515,
      4516
    ],
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
    "observed_problem_type_answer_contracts": {},
    "missing_answer_contract_problem_types": [],
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
  "report": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_pipeline_report.md"
}
```

## Semantic Audit Summary
```json
{
  "examples_total": 17,
  "examples_covered": 17,
  "required_fields_missing_count": 0,
  "audit_pass_count": 0,
  "audit_review_required_count": 17,
  "examples_with_risk_flags": [
    {
      "example_id": 4424,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4425,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4426,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4430,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4431,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4433,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4434,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4441,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4442,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4444,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4445,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4446,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4448,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4449,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4500,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4515,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    },
    {
      "example_id": 4516,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    }
  ],
  "possible_missing_problem_types": [
    4424,
    4425,
    4426,
    4430,
    4431,
    4433,
    4434,
    4441,
    4442,
    4444,
    4445,
    4446,
    4448,
    4449,
    4500,
    4515,
    4516
  ],
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
  "observed_problem_type_answer_contracts": {},
  "missing_answer_contract_problem_types": [],
  "missing_checker_key_problem_types": [],
  "invalid_equivalence_type_problem_types": [],
  "equivalence_test_required_problem_types": []
}
```

## Problem Type Closed Loop

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
  "observed_problem_type_answer_contracts": {},
  "missing_answer_contract_problem_types": [],
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
  "stdout": "{\"success\": true, \"examples_count\": 17, \"report\": \"D:\\\\Python\\\\Mathproject_tvet_mathB\\\\reports\\\\gencode_closed_loop\\\\vh_數學B1_LinearFunction_inventory_report.md\", \"package_dir\": \"D:\\\\Python\\\\Mathproject_tvet_mathB\\\\agent_skills_v2\\\\_generated\\\\vh_數學B1_LinearFunction\"}\n",
  "stderr": "",
  "parsed": {
    "success": true,
    "examples_count": 17,
    "report": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_inventory_report.md",
    "package_dir": "D:\\Python\\Mathproject_tvet_mathB\\agent_skills_v2\\_generated\\vh_數學B1_LinearFunction"
  }
}
```

## Verify
```json
{
  "stdout": "{\"success\": false, \"report\": \"D:\\\\Python\\\\Mathproject_tvet_mathB\\\\reports\\\\gencode_closed_loop\\\\vh_數學B1_LinearFunction_verify_report.md\", \"first_error\": \"registry has no verified candidate for skill\", \"runtime_problem_type_coverage\": {\"expected_problem_types\": [], \"observed_problem_types\": [], \"missing_problem_types\": [], \"sample_count\": 30, \"status\": \"fail\"}}\n",
  "stderr": "",
  "parsed": {
    "success": false,
    "report": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_verify_report.md",
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
