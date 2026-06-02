# Gencode Phase3 Package Summary: vh_數學B1_MidpointCoordinates

## phase3
```json
{
  "ok": true,
  "phase": "phase3",
  "skill_id": "vh_數學B1_MidpointCoordinates",
  "sop_reference": {
    "sop_policy_version": "v0.3",
    "highest_sop": "docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md",
    "required_sop_files": [
      {
        "path": "docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md",
        "exists": true,
        "readable": true,
        "mojibake_detected": false
      },
      {
        "path": "docs/系統SOP/Gencode_AgentSkillV2整合/AgentSkillV2_ProblemType規格包設計_v0.3.md",
        "exists": true,
        "readable": true,
        "mojibake_detected": false
      },
      {
        "path": "docs/系統SOP/Gencode_AgentSkillV2整合/AnswerContract_EquivalenceType_Gate_v0.3.md",
        "exists": true,
        "readable": true,
        "mojibake_detected": false
      }
    ],
    "sop_preflight_status": "PASS"
  },
  "remaining_todos": [
    "SOP v0.2 Verification: Verify that if a problem_type is verified, `/practice` must hit it within 50 rounds.",
    "SOP v0.2 Verification: Ensure Gencode runtime audit uses `generated_only` to prevent source_bank_pool masking generator distribution.",
    "SOP v0.2 Wrapper: Ensure wrapper state does not reload / reset state upon importlib.reload."
  ],
  "skill_file_path": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_MidpointCoordinates.py",
  "package_status": "packaged_draft",
  "py_compile_status": "passed",
  "runtime_smoke_status": "passed",
  "runtime_smoke_raw": {
    "status": "passed",
    "blockers": [],
    "payload_preview": {
      "problem_type_id": "ordered_tuple_compute_midpoint_coordinates",
      "answer_type": "coordinate_pair",
      "answer_contract_answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "equivalence": "ordered_tuple_exact",
      "question_text_len": 57,
      "answer": "(6,0)",
      "correct_answer": "(6,0)",
      "choices_count": 0,
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
        "semantic_required_concepts"
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
      "problem_type_id": "ordered_tuple_compute_midpoint_coordinates",
      "answer_type": "coordinate_pair",
      "answer_shape": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "equivalence": "ordered_tuple_exact",
      "answer_repr": "'(6,0)'",
      "answer_python_type": "str",
      "correct_answer_repr": "'(6,0)'",
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
      "expected_answer_shape": "coordinate_pair allows (x,y) string or equivalent formats; answer_shape=coordinate_pair",
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
        "problem_type_id": "ordered_tuple_compute_midpoint_coordinates",
        "answer_type": "coordinate_pair",
        "answer_contract_answer_type": "coordinate_pair",
        "checker": "coordinate_pair_checker",
        "equivalence": "ordered_tuple_exact",
        "question_text_len": 57,
        "answer": "(6,0)",
        "correct_answer": "(6,0)",
        "choices_count": 0,
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
          "semantic_required_concepts"
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
        "problem_type_id": "ordered_tuple_compute_midpoint_coordinates",
        "answer_type": "coordinate_pair",
        "answer_shape": "coordinate_pair",
        "checker": "coordinate_pair_checker",
        "equivalence": "ordered_tuple_exact",
        "answer_repr": "'(6,0)'",
        "answer_python_type": "str",
        "correct_answer_repr": "'(6,0)'",
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
        "expected_answer_shape": "coordinate_pair allows (x,y) string or equivalent formats; answer_shape=coordinate_pair",
        "failed_validator_name": "",
        "validation_reason": ""
      }
    },
    "summary_message": "Draft passed checks and can be formally published; runtime-ready is not marked yet. Run /practice smoke tests first."
  },
  "generator_specs": [
    {
      "problem_type_id": "ordered_tuple_compute_midpoint_coordinates",
      "checker_key": "coordinate_pair_checker",
      "equivalence_type": "ordered_tuple_exact",
      "generator_readiness": "runtime_ready"
    },
    {
      "problem_type_id": "text_short_compute_midpoint_coordinates",
      "checker_key": "coordinate_pair_checker",
      "equivalence_type": "ordered_tuple_exact",
      "generator_readiness": "runtime_ready"
    },
    {
      "problem_type_id": "text_short_compute_centroid_coordinates",
      "checker_key": "coordinate_pair_checker",
      "equivalence_type": "ordered_tuple_exact",
      "generator_readiness": "runtime_ready"
    }
  ],
  "packaging_usable_count": 3,
  "packaging_diagnostics": {
    "candidate_count": 3,
    "included_count": 3,
    "excluded_count": 0,
    "included": [
      {
        "problem_type_id": "ordered_tuple_compute_midpoint_coordinates",
        "generator_key": "vh_數學B1_MidpointCoordinates:ordered_tuple_compute_midpoint_coordinates:draft_v1",
        "generator_status": "runtime_ready_with_warning"
      },
      {
        "problem_type_id": "text_short_compute_midpoint_coordinates",
        "generator_key": "vh_數學B1_MidpointCoordinates:text_short_compute_midpoint_coordinates:draft_v1",
        "generator_status": "runtime_ready"
      },
      {
        "problem_type_id": "text_short_compute_centroid_coordinates",
        "generator_key": "vh_數學B1_MidpointCoordinates:text_short_compute_centroid_coordinates:draft_v1",
        "generator_status": "runtime_ready_with_warning"
      }
    ],
    "excluded": [],
    "phase2_summary_exists": true,
    "generator_draft_spec_exists": true,
    "phase2_generator_summary_json": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_MidpointCoordinates_phase2_generator_summary.json",
    "generator_draft_spec_json": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_MidpointCoordinates_generator_draft_spec.json",
    "runtime_spec_alignment": {
      "status": "synced",
      "synced_spec_count": 3,
      "synced_problem_type_ids": [
        "ordered_tuple_compute_midpoint_coordinates",
        "text_short_compute_midpoint_coordinates",
        "text_short_compute_centroid_coordinates"
      ],
      "induced_spec_path": "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_MidpointCoordinates.json",
      "purged_induced_spec_path": "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_MidpointCoordinates.json",
      "purged_induced_spec_paths": [
        "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_MidpointCoordinates.json"
      ],
      "runtime_usable_problem_type_ids": [
        "ordered_tuple_compute_midpoint_coordinates",
        "text_short_compute_centroid_coordinates",
        "text_short_compute_midpoint_coordinates"
      ],
      "downgraded_historical_problem_type_ids": [
        "single_choice_compute_midpoint_coordinates"
      ],
      "canonical_filter_applied": true
    }
  },
  "reports": {
    "phase3_package_summary_json": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_MidpointCoordinates_phase3_package_summary.json",
    "phase3_package_summary_md": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_MidpointCoordinates_phase3_package_summary.md",
    "phase3_json": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_MidpointCoordinates_phase3_package_summary.json",
    "phase3_md": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_MidpointCoordinates_phase3_package_summary.md",
    "final_json": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_MidpointCoordinates_phase3_package_summary.json",
    "final_md": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_MidpointCoordinates_phase3_package_summary.md",
    "draft_skill_file": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_MidpointCoordinates.py"
  },
  "next_action": "review_phase3_publish_check",
  "error": "",
  "dry_run": true,
  "timestamp": "2026-06-02T15:36:33.805601+00:00",
  "generated_with_warning": true,
  "warnings": [
    "low_sample_diversity_tolerance_applied",
    "low_source_examples"
  ],
  "publish_gate_layers": {
    "technical_closed_loop": "PASS",
    "runtime_quality": "PASS",
    "web_runtime": "PASS",
    "source_alignment": "PARTIAL"
  },
  "source_alignment_audit": {
    "status": "PARTIAL",
    "missing_source_aligned_problem_types": [
      "short_answer_compute_centroid_coordinates",
      "short_answer_compute_midpoint_coordinates",
      "single_choice_compute_midpoint_coordinates"
    ],
    "underrepresented_runtime_forms": [
      "short_answer_compute_centroid_coordinates",
      "short_answer_compute_midpoint_coordinates",
      "single_choice_compute_midpoint_coordinates"
    ]
  },
  "post_phase3_audit_scripts": [
    {
      "script": "gencode_choice_quality_audit.py",
      "exists": true,
      "py_compile_ok": true
    },
    {
      "script": "gencode_runtime_distribution_audit.py",
      "exists": true,
      "py_compile_ok": true
    },
    {
      "script": "gencode_web_runtime_audit.py",
      "exists": true,
      "py_compile_ok": true
    },
    {
      "script": "gencode_source_alignment_audit.py",
      "exists": true,
      "py_compile_ok": true
    }
  ],
  "summary_message": "Draft passed checks and can be formally published; runtime-ready is not marked yet. Run /practice smoke tests first."
}
```
