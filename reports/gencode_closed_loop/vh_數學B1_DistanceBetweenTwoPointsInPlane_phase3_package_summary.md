# Gencode Phase3 Package Summary: vh_數學B1_DistanceBetweenTwoPointsInPlane

## phase3
```json
{
  "ok": true,
  "phase": "phase3",
  "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
  "skill_file_path": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_DistanceBetweenTwoPointsInPlane.py",
  "package_status": "packaged_draft",
  "py_compile_status": "passed",
  "runtime_smoke_status": "passed",
  "runtime_smoke_raw": {
    "status": "passed",
    "blockers": [],
    "payload_preview": {
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "answer_type": "numeric_or_radical",
      "answer_contract_answer_type": "numeric_or_radical",
      "checker": "expression_equivalence_checker",
      "equivalence": "math_expression_equivalence",
      "question_text_len": 24,
      "answer": "\\sqrt{73}",
      "correct_answer": "\\sqrt{73}",
      "choices_count": 0,
      "metadata_keys": [
        "givens",
        "target",
        "derivation"
      ]
    },
    "interface_check": {
      "generate_exists": true,
      "check_exists": true,
      "generate_returns_dict": true,
      "check_callable": true
    },
    "py_compile_status": "passed",
    "samples_tested": 30,
    "negative_semantic_smoke": "passed",
    "validation_diagnostics": {
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "answer_type": "numeric_or_radical",
      "answer_shape": "scalar",
      "checker": "expression_equivalence_checker",
      "equivalence": "math_expression_equivalence",
      "answer_repr": "'\\\\sqrt{73}'",
      "answer_python_type": "str",
      "correct_answer_repr": "'\\\\sqrt{73}'",
      "correct_answer_python_type": "str",
      "validator_expected_types": [
        "category",
        "choice",
        "choice_label",
        "classification",
        "decimal",
        "expression",
        "fraction",
        "integer",
        "integer_set",
        "interval",
        "interval_set",
        "manual_review",
        "math_expression",
        "multi_choice",
        "number",
        "number_set",
        "numeric",
        "numeric_or_radical",
        "quadrant_label",
        "radical_number",
        "set",
        "short_answer",
        "single_choice",
        "solution_set",
        "table",
        "text_label",
        "union_of_intervals"
      ],
      "expected_answer_shape": "numeric_or_radical allows int/float/expression string; answer_shape=scalar",
      "failed_validator_name": "",
      "validation_reason": ""
    }
  },
  "publish_check": {
    "draft_check_passed": true,
    "can_publish_draft": true,
    "can_publish_formal": true,
    "can_mark_runtime_ready": false,
    "formal_publish_blockers": [],
    "runtime_ready_blockers": [
      "runtime_ready_gate_not_allowed_or_not_verified"
    ],
    "warnings": [
      "draft_passed_but_runtime_ready_not_confirmed"
    ],
    "blockers": [],
    "py_compile_status": "passed",
    "interface_check": {
      "generate_exists": true,
      "check_exists": true,
      "generate_returns_dict": true,
      "check_callable": true
    },
    "runtime_smoke_status": "passed",
    "runtime_smoke_raw": {
      "status": "passed",
      "blockers": [],
      "payload_preview": {
        "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "answer_type": "numeric_or_radical",
        "answer_contract_answer_type": "numeric_or_radical",
        "checker": "expression_equivalence_checker",
        "equivalence": "math_expression_equivalence",
        "question_text_len": 24,
        "answer": "\\sqrt{73}",
        "correct_answer": "\\sqrt{73}",
        "choices_count": 0,
        "metadata_keys": [
          "givens",
          "target",
          "derivation"
        ]
      },
      "interface_check": {
        "generate_exists": true,
        "check_exists": true,
        "generate_returns_dict": true,
        "check_callable": true
      },
      "py_compile_status": "passed",
      "samples_tested": 30,
      "negative_semantic_smoke": "passed",
      "validation_diagnostics": {
        "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "answer_type": "numeric_or_radical",
        "answer_shape": "scalar",
        "checker": "expression_equivalence_checker",
        "equivalence": "math_expression_equivalence",
        "answer_repr": "'\\\\sqrt{73}'",
        "answer_python_type": "str",
        "correct_answer_repr": "'\\\\sqrt{73}'",
        "correct_answer_python_type": "str",
        "validator_expected_types": [
          "category",
          "choice",
          "choice_label",
          "classification",
          "decimal",
          "expression",
          "fraction",
          "integer",
          "integer_set",
          "interval",
          "interval_set",
          "manual_review",
          "math_expression",
          "multi_choice",
          "number",
          "number_set",
          "numeric",
          "numeric_or_radical",
          "quadrant_label",
          "radical_number",
          "set",
          "short_answer",
          "single_choice",
          "solution_set",
          "table",
          "text_label",
          "union_of_intervals"
        ],
        "expected_answer_shape": "numeric_or_radical allows int/float/expression string; answer_shape=scalar",
        "failed_validator_name": "",
        "validation_reason": ""
      }
    },
    "summary_message": "Draft passed checks and can be formally published; runtime-ready is not marked yet. Run /practice smoke tests first."
  },
  "generator_specs": [
    {
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "checker_key": "text_checker",
      "equivalence_type": "exact_string",
      "generator_readiness": "runtime_ready"
    },
    {
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "checker_key": "text_checker",
      "equivalence_type": "exact_string",
      "generator_readiness": "runtime_ready"
    }
  ],
  "packaging_usable_count": 2,
  "packaging_diagnostics": {
    "candidate_count": 2,
    "included_count": 2,
    "excluded_count": 0,
    "included": [
      {
        "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
        "generator_key": "vh_數學B1_DistanceBetweenTwoPointsInPlane:short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:draft_v1",
        "generator_status": "runtime_ready"
      },
      {
        "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "generator_key": "vh_數學B1_DistanceBetweenTwoPointsInPlane:short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:draft_v1",
        "generator_status": "runtime_ready"
      }
    ],
    "excluded": [],
    "phase2_summary_exists": true,
    "generator_draft_spec_exists": true,
    "phase2_generator_summary_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase2_generator_summary.json",
    "generator_draft_spec_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_DistanceBetweenTwoPointsInPlane_generator_draft_spec.json"
  },
  "reports": {
    "phase3_package_summary_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase3_package_summary.json",
    "phase3_package_summary_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase3_package_summary.md",
    "draft_skill_file": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_DistanceBetweenTwoPointsInPlane.py"
  },
  "next_action": "review_phase3_publish_check",
  "error": "",
  "dry_run": true,
  "timestamp": "2026-05-29T06:55:06.781738+00:00",
  "generated_with_warning": true,
  "warnings": [
    "low_source_examples"
  ],
  "summary_message": "Draft passed checks and can be formally published; runtime-ready is not marked yet. Run /practice smoke tests first."
}
```
