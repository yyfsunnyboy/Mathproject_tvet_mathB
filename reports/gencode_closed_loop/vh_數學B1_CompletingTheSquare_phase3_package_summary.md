# Gencode Phase3 Package Summary: vh_數學B1_CompletingTheSquare

## phase3
```json
{
  "ok": true,
  "phase": "phase3",
  "skill_id": "vh_數學B1_CompletingTheSquare",
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
  "skill_file_path": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_CompletingTheSquare.py",
  "package_status": "packaged_draft",
  "py_compile_status": "passed",
  "runtime_smoke_status": "passed",
  "runtime_smoke_raw": {
    "status": "passed",
    "blockers": [],
    "payload_preview": {
      "problem_type_id": "integer_quadratic_graph_vertex_axis_choice",
      "answer_type": "single_choice",
      "answer_contract_answer_type": "single_choice",
      "checker": "choice_label_checker",
      "equivalence": "choice_label",
      "question_text_len": 43,
      "answer": "D",
      "correct_answer": "D",
      "choices_count": 4,
      "metadata_keys": [
        "givens",
        "target",
        "derivation",
        "template_slot",
        "problem_type_id",
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
      "problem_type_id": "integer_quadratic_graph_vertex_axis_choice",
      "answer_type": "single_choice",
      "answer_shape": "single_choice",
      "checker": "choice_label_checker",
      "equivalence": "choice_label",
      "answer_repr": "'D'",
      "answer_python_type": "str",
      "correct_answer_repr": "'D'",
      "correct_answer_python_type": "str",
      "validator_expected_types": [
        "case_insensitive_string",
        "category",
        "choice",
        "choice_label",
        "classification",
        "coordinate_pair",
        "decimal",
        "exact_string",
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
        "rational",
        "rational_fraction",
        "set",
        "short_answer",
        "single_choice",
        "solution_set",
        "table",
        "text",
        "text_label",
        "text_short",
        "union_of_intervals"
      ],
      "expected_answer_shape": "single_choice allows A/B/C/D or choice label text; answer_shape=single_choice",
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
        "problem_type_id": "integer_quadratic_graph_vertex_axis_choice",
        "answer_type": "single_choice",
        "answer_contract_answer_type": "single_choice",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "question_text_len": 43,
        "answer": "D",
        "correct_answer": "D",
        "choices_count": 4,
        "metadata_keys": [
          "givens",
          "target",
          "derivation",
          "template_slot",
          "problem_type_id",
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
        "problem_type_id": "integer_quadratic_graph_vertex_axis_choice",
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "answer_repr": "'D'",
        "answer_python_type": "str",
        "correct_answer_repr": "'D'",
        "correct_answer_python_type": "str",
        "validator_expected_types": [
          "case_insensitive_string",
          "category",
          "choice",
          "choice_label",
          "classification",
          "coordinate_pair",
          "decimal",
          "exact_string",
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
          "rational",
          "rational_fraction",
          "set",
          "short_answer",
          "single_choice",
          "solution_set",
          "table",
          "text",
          "text_label",
          "text_short",
          "union_of_intervals"
        ],
        "expected_answer_shape": "single_choice allows A/B/C/D or choice label text; answer_shape=single_choice",
        "failed_validator_name": "",
        "validation_reason": ""
      }
    },
    "summary_message": "Draft passed checks and can be formally published; runtime-ready is not marked yet. Run /practice smoke tests first."
  },
  "generator_specs": [
    {
      "problem_type_id": "quadratic_vertex_or_parameter_computation",
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent",
      "generator_readiness": "contract_slot_mismatch",
      "answer_type": "rational",
      "template_slot": "quadratic_vertex_or_parameter_computation",
      "base_problem_type_id": "quadratic_vertex_or_parameter_computation",
      "value_type_prefix": "integer",
      "presentation_mode": "short_answer",
      "answer_shape": "scalar"
    },
    {
      "problem_type_id": "integer_quadratic_graph_vertex_axis_choice",
      "checker_key": "choice_label_checker",
      "equivalence_type": "choice_label",
      "generator_readiness": "runtime_ready",
      "answer_type": "single_choice",
      "template_slot": "quadratic_graph_vertex_axis_choice",
      "base_problem_type_id": "quadratic_graph_vertex_axis_choice",
      "value_type_prefix": "integer",
      "presentation_mode": "single_choice",
      "answer_shape": "single_choice"
    }
  ],
  "packaging_usable_count": 2,
  "packaging_diagnostics": {
    "candidate_count": 2,
    "included_count": 2,
    "excluded_count": 0,
    "included": [
      {
        "problem_type_id": "integer_quadratic_vertex_or_parameter_computation",
        "generator_key": "vh_數學B1_CompletingTheSquare:integer_quadratic_vertex_or_parameter_computation:draft_v1",
        "generator_status": "runtime_ready_with_warning"
      },
      {
        "problem_type_id": "integer_quadratic_graph_vertex_axis_choice",
        "generator_key": "vh_數學B1_CompletingTheSquare:integer_quadratic_graph_vertex_axis_choice:draft_v1",
        "generator_status": "runtime_ready_with_warning"
      }
    ],
    "excluded": [],
    "phase2_summary_exists": true,
    "generator_draft_spec_exists": true,
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CompletingTheSquare_phase2_generator_summary.json",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_CompletingTheSquare_generator_draft_spec.json",
    "runtime_spec_alignment": {
      "status": "synced",
      "synced_spec_count": 2,
      "synced_problem_type_ids": [
        "integer_quadratic_vertex_or_parameter_computation",
        "integer_quadratic_graph_vertex_axis_choice"
      ],
      "induced_spec_path": "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_CompletingTheSquare.json",
      "purged_induced_spec_path": "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_CompletingTheSquare.json",
      "purged_induced_spec_paths": [
        "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_CompletingTheSquare.json"
      ],
      "runtime_usable_problem_type_ids": [
        "integer_quadratic_graph_vertex_axis_choice",
        "integer_quadratic_vertex_or_parameter_computation"
      ],
      "downgraded_historical_problem_type_ids": [],
      "canonical_filter_applied": true
    }
  },
  "reports": {
    "phase3_package_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CompletingTheSquare_phase3_package_summary.json",
    "phase3_package_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CompletingTheSquare_phase3_package_summary.md",
    "phase3_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CompletingTheSquare_phase3_package_summary.json",
    "phase3_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CompletingTheSquare_phase3_package_summary.md",
    "final_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CompletingTheSquare_phase3_package_summary.json",
    "final_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CompletingTheSquare_phase3_package_summary.md",
    "draft_skill_file": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_CompletingTheSquare.py"
  },
  "next_action": "review_phase3_publish_check",
  "error": "",
  "dry_run": true,
  "timestamp": "2026-06-13T13:48:23.274629+00:00",
  "generated_with_warning": true,
  "warnings": [
    "consecutive_same_template_variant",
    "low_sample_diversity_tolerance_applied",
    "low_source_examples",
    "low_unique_signature_count"
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
      "quadratic_graph_vertex_axis_choice_single_choice",
      "quadratic_vertex_or_parameter_computation"
    ],
    "underrepresented_runtime_forms": [
      "quadratic_graph_vertex_axis_choice_single_choice",
      "quadratic_vertex_or_parameter_computation"
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
