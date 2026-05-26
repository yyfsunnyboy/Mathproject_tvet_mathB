# Phase3 Publish Gate: vh_數學B1_AbsoluteValue

## summary
```json
{
  "skill_id": "vh_數學B1_AbsoluteValue",
  "phase": "phase3_publish_gate",
  "final_status": "PASS",
  "publish_ready": true,
  "full_observed_coverage": true,
  "source_coverage_status": "FULL_OBSERVED_COVERAGE_CANDIDATE",
  "bootstrap_summary": {
    "bootstrap_mode": false,
    "bootstrap_source_skill_id": "",
    "source_coverage_status": "",
    "allowed_problem_types": [],
    "bootstrap_runtime_status": "FAIL"
  },
  "examples_total": 4,
  "examples_covered": 4,
  "observed_problem_types": [
    "absolute_value_distance_between_two_points",
    "absolute_value_equation_basic"
  ],
  "verified_problem_types": [
    "absolute_value_distance_between_two_points",
    "absolute_value_distance_from_zero",
    "absolute_value_equation_basic",
    "absolute_value_numeric_evaluation"
  ],
  "pending_implementation": [],
  "manual_review_problem_types": [],
  "future_ai_judged_problem_types": [],
  "answer_contract_summary": {
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
    }
  },
  "missing_answer_contract_problem_types": [],
  "missing_checker_key_problem_types": [],
  "equivalence_test_required_problem_types": [
    "absolute_value_equation_basic"
  ],
  "runtime_problem_type_coverage": {
    "expected_problem_types": [
      "absolute_value_distance_between_two_points",
      "absolute_value_equation_basic"
    ],
    "observed_problem_types": [
      "absolute_value_distance_between_two_points",
      "absolute_value_distance_from_zero",
      "absolute_value_equation_basic",
      "absolute_value_numeric_evaluation"
    ],
    "missing_problem_types": [],
    "status": "pass"
  },
  "blocking_reasons": [],
  "warnings": [],
  "artifact_paths": {
    "phase1_json": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValue_phase1_audit.json",
    "phase2_json": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValue_phase2_build.json",
    "final_json": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValue_pipeline_final.json",
    "final_md": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValue_pipeline_final.md"
  },
  "timestamp": "2026-05-26T04:15:12.343838+00:00"
}
```
