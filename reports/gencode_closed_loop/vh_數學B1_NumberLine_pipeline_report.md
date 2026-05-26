# Skill Gencode Pipeline Report: vh_數學B1_NumberLine

## Summary
```json
{
  "success": true,
  "final_status": "PASS_BOOTSTRAP_ONLY",
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
    "examples_total": 1,
    "examples_covered": 1,
    "required_fields_missing_count": 0,
    "audit_pass_count": 0,
    "audit_review_required_count": 1,
    "examples_with_risk_flags": [
      {
        "example_id": 4401,
        "flags": [
          "possible_missing_problem_type",
          "weak_classifier_match"
        ]
      }
    ],
    "possible_missing_problem_types": [
      4401
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
  "report": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_NumberLine_pipeline_report.md",
  "bootstrap_summary": {
    "bootstrap_mode": true,
    "bootstrap_source_skill_id": "jh_數學1上_NumberLine",
    "bootstrap_runtime_status": "PASS",
    "source_coverage_status": "INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES",
    "full_observed_coverage": false,
    "warning": "Bootstrap-only runtime ready; not full DB observed textbook coverage."
  },
  "bootstrap_mode": true,
  "bootstrap_source_skill_id": "jh_數學1上_NumberLine",
  "bootstrap_runtime_status": "PASS",
  "source_coverage_status": "INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES"
}
```

## Semantic Audit Summary
```json
{
  "examples_total": 1,
  "examples_covered": 1,
  "required_fields_missing_count": 0,
  "audit_pass_count": 0,
  "audit_review_required_count": 1,
  "examples_with_risk_flags": [
    {
      "example_id": 4401,
      "flags": [
        "possible_missing_problem_type",
        "weak_classifier_match"
      ]
    }
  ],
  "possible_missing_problem_types": [
    4401
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
  "stdout": "{\"success\": true, \"examples_count\": 1, \"report\": \"C:\\\\Python\\\\Mathproject_tvet_mathB\\\\reports\\\\gencode_closed_loop\\\\vh_數學B1_NumberLine_inventory_report.md\", \"package_dir\": \"C:\\\\Python\\\\Mathproject_tvet_mathB\\\\agent_skills_v2\\\\_generated\\\\vh_數學B1_NumberLine\"}\n",
  "stderr": "",
  "parsed": {
    "success": true,
    "examples_count": 1,
    "report": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_NumberLine_inventory_report.md",
    "package_dir": "C:\\Python\\Mathproject_tvet_mathB\\agent_skills_v2\\_generated\\vh_數學B1_NumberLine"
  }
}
```

## Verify
```json
{
  "stdout": "{\"success\": false, \"report\": \"C:\\\\Python\\\\Mathproject_tvet_mathB\\\\reports\\\\gencode_closed_loop\\\\vh_數學B1_NumberLine_verify_report.md\", \"first_error\": \"registry has no verified candidate for skill\", \"runtime_problem_type_coverage\": {\"expected_problem_types\": [], \"observed_problem_types\": [], \"missing_problem_types\": [], \"sample_count\": 30, \"status\": \"fail\"}}\n",
  "stderr": "",
  "parsed": {
    "success": false,
    "report": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_NumberLine_verify_report.md",
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
