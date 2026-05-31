# Gencode Phase3 Package Summary: vh_數學B1_DivisionPointCoordinates

## phase3
```json
{
  "ok": true,
  "phase": "phase3",
  "skill_id": "vh_數學B1_DivisionPointCoordinates",
  "skill_file_path": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_DivisionPointCoordinates.py",
  "package_status": "packaged_draft",
  "py_compile_status": "passed",
  "runtime_smoke_status": "passed",
  "runtime_smoke_raw": {
    "status": "passed",
    "blockers": [],
    "payload_preview": {
      "problem_type_id": "single_choice_compute_internal_division_point_coordinates_two_coordinate_points_",
      "answer_type": "single_choice",
      "answer_contract_answer_type": "single_choice",
      "checker": "choice_label_checker",
      "equivalence": "choice_label",
      "question_text_len": 61,
      "answer": "C",
      "correct_answer": "C",
      "choices_count": 4,
      "metadata_keys": [
        "givens",
        "target",
        "derivation",
        "template_variant",
        "template_id",
        "ratio_form",
        "ratio_values",
        "coordinate_pattern",
        "point_names",
        "generation_coords",
        "generator_contract",
        "presentation_mode",
        "semantic_answer"
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
      "problem_type_id": "single_choice_compute_internal_division_point_coordinates_two_coordinate_points_",
      "answer_type": "single_choice",
      "answer_shape": "choice_label",
      "checker": "choice_label_checker",
      "equivalence": "choice_label",
      "answer_repr": "'C'",
      "answer_python_type": "str",
      "correct_answer_repr": "'C'",
      "correct_answer_python_type": "str",
      "validator_expected_types": [
        "category",
        "choice",
        "choice_label",
        "classification",
        "coordinate_pair",
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
        "ordered_pair",
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
      "expected_answer_shape": "single_choice allows A/B/C/D or choice label text; answer_shape=choice_label",
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
        "problem_type_id": "single_choice_compute_internal_division_point_coordinates_two_coordinate_points_",
        "answer_type": "single_choice",
        "answer_contract_answer_type": "single_choice",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "question_text_len": 61,
        "answer": "C",
        "correct_answer": "C",
        "choices_count": 4,
        "metadata_keys": [
          "givens",
          "target",
          "derivation",
          "template_variant",
          "template_id",
          "ratio_form",
          "ratio_values",
          "coordinate_pattern",
          "point_names",
          "generation_coords",
          "generator_contract",
          "presentation_mode",
          "semantic_answer"
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
        "problem_type_id": "single_choice_compute_internal_division_point_coordinates_two_coordinate_points_",
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "answer_repr": "'C'",
        "answer_python_type": "str",
        "correct_answer_repr": "'C'",
        "correct_answer_python_type": "str",
        "validator_expected_types": [
          "category",
          "choice",
          "choice_label",
          "classification",
          "coordinate_pair",
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
          "ordered_pair",
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
        "expected_answer_shape": "single_choice allows A/B/C/D or choice label text; answer_shape=choice_label",
        "failed_validator_name": "",
        "validation_reason": ""
      }
    },
    "summary_message": "Draft passed checks and can be formally published; runtime-ready is not marked yet. Run /practice smoke tests first."
  },
  "generator_specs": [
    {
      "problem_type_id": "ordered_pair_compute_internal_division_point_coordinates_short_answer_two_coordi",
      "checker_key": "coordinate_pair_checker",
      "equivalence_type": "coordinate_pair_equivalence",
      "generator_readiness": "runtime_ready"
    },
    {
      "problem_type_id": "single_choice_compute_internal_division_point_coordinates_two_coordinate_points_",
      "checker_key": "choice_label_checker",
      "equivalence_type": "choice_label",
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
        "problem_type_id": "ordered_pair_compute_internal_division_point_coordinates_short_answer_two_coordi",
        "generator_key": "vh_數學B1_DivisionPointCoordinates:ordered_pair_compute_internal_division_point_coordinates_short_answer_two_coordi:draft_v1",
        "generator_status": "runtime_ready"
      },
      {
        "problem_type_id": "single_choice_compute_internal_division_point_coordinates_two_coordinate_points_",
        "generator_key": "vh_數學B1_DivisionPointCoordinates:single_choice_compute_internal_division_point_coordinates_two_coordinate_points_:draft_v1",
        "generator_status": "runtime_ready_with_warning"
      }
    ],
    "excluded": [],
    "phase2_summary_exists": true,
    "generator_draft_spec_exists": true,
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DivisionPointCoordinates_phase2_generator_summary.json",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_DivisionPointCoordinates_generator_draft_spec.json"
  },
  "reports": {
    "phase3_package_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DivisionPointCoordinates_phase3_package_summary.json",
    "phase3_package_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DivisionPointCoordinates_phase3_package_summary.md",
    "draft_skill_file": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_DivisionPointCoordinates.py"
  },
  "next_action": "review_phase3_publish_check",
  "error": "",
  "dry_run": true,
  "timestamp": "2026-05-29T15:47:23.946627+00:00",
  "generated_with_warning": true,
  "warnings": [
    "low_source_examples"
  ],
  "summary_message": "Draft passed checks and can be formally published; runtime-ready is not marked yet. Run /practice smoke tests first."
}
```
