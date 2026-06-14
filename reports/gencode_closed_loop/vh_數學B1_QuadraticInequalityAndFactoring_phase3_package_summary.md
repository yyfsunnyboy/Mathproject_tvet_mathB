# Gencode Phase3 Package Summary: vh_數學B1_QuadraticInequalityAndFactoring

## phase3
```json
{
  "ok": true,
  "phase": "phase3",
  "skill_id": "vh_數學B1_QuadraticInequalityAndFactoring",
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
  "skill_file_path": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_QuadraticInequalityAndFactoring.py",
  "package_status": "packaged_draft",
  "py_compile_status": "passed",
  "runtime_smoke_status": "passed",
  "runtime_smoke_raw": {
    "status": "passed",
    "blockers": [],
    "payload_preview": {
      "problem_type_id": "integer_factor_quadratic_by_cross_multiplication",
      "answer_type": "expression",
      "answer_contract_answer_type": "expression",
      "checker": "expression_checker",
      "equivalence": "algebraic_equivalent",
      "question_text_len": 59,
      "answer": "(2x+1)(3x-6)",
      "correct_answer": "(2x+1)(3x-6)",
      "choices_count": 0,
      "metadata_keys": [
        "givens",
        "target",
        "derivation",
        "problem_type_id",
        "template_slot",
        "template_variant",
        "coefficients",
        "semantic_required_concepts",
        "answer_format_suffix"
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
      "problem_type_id": "integer_factor_quadratic_by_cross_multiplication",
      "answer_type": "expression",
      "answer_shape": "scalar",
      "checker": "expression_checker",
      "equivalence": "algebraic_equivalent",
      "answer_repr": "'(2x+1)(3x-6)'",
      "answer_python_type": "str",
      "correct_answer_repr": "'(2x+1)(3x-6)'",
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
        "problem_type_id": "integer_factor_quadratic_by_cross_multiplication",
        "answer_type": "expression",
        "answer_contract_answer_type": "expression",
        "checker": "expression_checker",
        "equivalence": "algebraic_equivalent",
        "question_text_len": 59,
        "answer": "(2x+1)(3x-6)",
        "correct_answer": "(2x+1)(3x-6)",
        "choices_count": 0,
        "metadata_keys": [
          "givens",
          "target",
          "derivation",
          "problem_type_id",
          "template_slot",
          "template_variant",
          "coefficients",
          "semantic_required_concepts",
          "answer_format_suffix"
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
        "problem_type_id": "integer_factor_quadratic_by_cross_multiplication",
        "answer_type": "expression",
        "answer_shape": "scalar",
        "checker": "expression_checker",
        "equivalence": "algebraic_equivalent",
        "answer_repr": "'(2x+1)(3x-6)'",
        "answer_python_type": "str",
        "correct_answer_repr": "'(2x+1)(3x-6)'",
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
        "expected_answer_shape": "numeric_or_radical allows int/float/expression string; answer_shape=scalar",
        "failed_validator_name": "",
        "validation_reason": ""
      }
    },
    "summary_message": "Draft passed checks and can be formally published; runtime-ready is not marked yet. Run /practice smoke tests first."
  },
  "generator_specs": [
    {
      "problem_type_id": "integer_factor_quadratic_by_cross_multiplication",
      "checker_key": "expression_checker",
      "equivalence_type": "algebraic_equivalent",
      "generator_readiness": "runtime_ready",
      "answer_type": "expression",
      "template_slot": "factor_quadratic_by_cross_multiplication",
      "base_problem_type_id": "factor_quadratic_by_cross_multiplication",
      "value_type_prefix": "integer",
      "presentation_mode": "short_answer",
      "answer_shape": "factored_expression"
    }
  ],
  "packaging_usable_count": 1,
  "packaging_diagnostics": {
    "candidate_count": 1,
    "included_count": 1,
    "excluded_count": 0,
    "included": [
      {
        "problem_type_id": "integer_factor_quadratic_by_cross_multiplication",
        "generator_key": "vh_數學B1_QuadraticInequalityAndFactoring:integer_factor_quadratic_by_cross_multiplication:draft_v1",
        "generator_status": "runtime_ready_with_warning"
      }
    ],
    "excluded": [],
    "phase2_summary_exists": true,
    "generator_draft_spec_exists": true,
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticInequalityAndFactoring_phase2_generator_summary.json",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_QuadraticInequalityAndFactoring_generator_draft_spec.json",
    "runtime_spec_alignment": {
      "status": "synced",
      "synced_spec_count": 1,
      "synced_problem_type_ids": [
        "integer_factor_quadratic_by_cross_multiplication"
      ],
      "induced_spec_path": "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_QuadraticInequalityAndFactoring.json",
      "purged_induced_spec_path": "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_QuadraticInequalityAndFactoring.json",
      "purged_induced_spec_paths": [
        "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_QuadraticInequalityAndFactoring.json"
      ],
      "runtime_usable_problem_type_ids": [
        "integer_factor_quadratic_by_cross_multiplication"
      ],
      "downgraded_historical_problem_type_ids": [],
      "canonical_filter_applied": true
    }
  },
  "reports": {
    "phase3_package_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticInequalityAndFactoring_phase3_package_summary.json",
    "phase3_package_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticInequalityAndFactoring_phase3_package_summary.md",
    "phase3_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticInequalityAndFactoring_phase3_package_summary.json",
    "phase3_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticInequalityAndFactoring_phase3_package_summary.md",
    "final_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticInequalityAndFactoring_phase3_package_summary.json",
    "final_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticInequalityAndFactoring_phase3_package_summary.md",
    "draft_skill_file": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_QuadraticInequalityAndFactoring.py"
  },
  "next_action": "review_phase3_publish_check",
  "error": "",
  "dry_run": true,
  "timestamp": "2026-06-13T15:55:06.658466+00:00",
  "generated_with_warning": true,
  "warnings": [
    "consecutive_same_template_variant",
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
      "numeric_factor_quadratic_by_cross_multiplication_short_answer"
    ],
    "underrepresented_runtime_forms": [
      "numeric_factor_quadratic_by_cross_multiplication_short_answer"
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
