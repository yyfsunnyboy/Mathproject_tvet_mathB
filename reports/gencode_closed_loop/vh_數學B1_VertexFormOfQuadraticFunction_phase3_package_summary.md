# Gencode Phase3 Package Summary: vh_數學B1_VertexFormOfQuadraticFunction

## phase3
```json
{
  "ok": true,
  "phase": "phase3",
  "skill_id": "vh_數學B1_VertexFormOfQuadraticFunction",
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
  "skill_file_path": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_VertexFormOfQuadraticFunction.py",
  "package_status": "failed",
  "py_compile_status": "passed",
  "runtime_smoke_status": "failed",
  "runtime_smoke_raw": {
    "status": "failed",
    "blockers": [
      "runtime_smoke_generate_exception"
    ],
    "payload_preview": {
      "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
      "answer_type": "text_short",
      "answer_contract_answer_type": "text_short",
      "checker": "text_short_checker",
      "equivalence": "exact_string",
      "question_text_len": 56,
      "answer": "向右 1、向上 2",
      "correct_answer": "向右 1、向上 2",
      "choices_count": 0,
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
      "generate_returns_dict": false,
      "check_callable": true
    },
    "py_compile_status": "passed",
    "samples_tested": 2,
    "negative_semantic_smoke": "passed",
    "error": "generator_semantically_unsafe:invalid_answer_type: problem_type_id=integer_quadratic_standard_to_vertex_properties answer_type=integer answer_shape=text_short answer='D' answer_type=str checker=integer_checker equivalence=numeric_exact expected=numeric allows int/float/numeric string; answer_shape=text_short",
    "failed_seed": 2,
    "runtime_smoke_raw": {
      "exception_type": "RuntimeError",
      "exception_message": "generator_semantically_unsafe:invalid_answer_type: problem_type_id=integer_quadratic_standard_to_vertex_properties answer_type=integer answer_shape=text_short answer='D' answer_type=str checker=integer_checker equivalence=numeric_exact expected=numeric allows int/float/numeric string; answer_shape=text_short",
      "traceback_preview": "Traceback (most recent call last):\n  File \"E:\\Python\\Mathproject_tvet_mathB\\core\\gencode\\runtime_smoke.py\", line 459, in _run_draft_runtime_smoke_impl\n    payload = gen(level=1, seed=seed)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_VertexFormOfQuadraticFunction.py\", line 12, in generate\n    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\core\\gencode\\runtime_skill_wrapper.py\", line 175, in generate_for_skill\n    payload = generate_from_problem_type_spec(skill_id, problem_type_spec, seed=generation_seed)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\core\\gencode\\slot_generators.py\", line 1181, in generate_from_problem_type_spec\n    raise RuntimeError(f\"generator_semantically_unsafe:{','.join(errors)}\")\nRuntimeError: generator_semantically_unsafe:invalid_answer_type: problem_type_id=integer_quadratic_standard_to_vertex_properties answer_type=integer answer_shape=text_short answer='D' answer_type=str checker=integer_checker equivalence=numeric_exact expected=numeric allows int/float/numeric string; answer_shape=text_short\n",
      "problem_type_id": "integer_quadratic_standard_to_vertex_properties",
      "seed": 2
    },
    "failed_validator_name": "slot_generators.validate_generator_payload",
    "validation_diagnostics": {
      "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "checker": "text_short_checker",
      "equivalence": "exact_string",
      "answer_repr": "'向右 1、向上 2'",
      "answer_python_type": "str",
      "correct_answer_repr": "'向右 1、向上 2'",
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
      "expected_answer_shape": "short_answer allows non-empty string; answer_shape=text_short",
      "failed_validator_name": "",
      "validation_reason": ""
    }
  },
  "publish_check": {
    "draft_check_passed": false,
    "can_publish_draft": false,
    "can_publish_formal": false,
    "can_mark_runtime_ready": false,
    "formal_publish_blockers": [
      "draft_check_not_passed"
    ],
    "runtime_ready_blockers": [
      "runtime_ready_gate_not_allowed_or_not_verified"
    ],
    "warnings": [
      "draft_passed_but_runtime_ready_not_confirmed"
    ],
    "blockers": [
      "runtime_smoke_generate_exception"
    ],
    "py_compile_status": "passed",
    "interface_check": {
      "generate_exists": true,
      "check_exists": true,
      "generate_returns_dict": false,
      "check_callable": true
    },
    "runtime_smoke_status": "failed",
    "runtime_smoke_raw": {
      "status": "failed",
      "blockers": [
        "runtime_smoke_generate_exception"
      ],
      "payload_preview": {
        "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
        "answer_type": "text_short",
        "answer_contract_answer_type": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "question_text_len": 56,
        "answer": "向右 1、向上 2",
        "correct_answer": "向右 1、向上 2",
        "choices_count": 0,
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
        "generate_returns_dict": false,
        "check_callable": true
      },
      "py_compile_status": "passed",
      "samples_tested": 2,
      "negative_semantic_smoke": "passed",
      "error": "generator_semantically_unsafe:invalid_answer_type: problem_type_id=integer_quadratic_standard_to_vertex_properties answer_type=integer answer_shape=text_short answer='D' answer_type=str checker=integer_checker equivalence=numeric_exact expected=numeric allows int/float/numeric string; answer_shape=text_short",
      "failed_seed": 2,
      "runtime_smoke_raw": {
        "exception_type": "RuntimeError",
        "exception_message": "generator_semantically_unsafe:invalid_answer_type: problem_type_id=integer_quadratic_standard_to_vertex_properties answer_type=integer answer_shape=text_short answer='D' answer_type=str checker=integer_checker equivalence=numeric_exact expected=numeric allows int/float/numeric string; answer_shape=text_short",
        "traceback_preview": "Traceback (most recent call last):\n  File \"E:\\Python\\Mathproject_tvet_mathB\\core\\gencode\\runtime_smoke.py\", line 459, in _run_draft_runtime_smoke_impl\n    payload = gen(level=1, seed=seed)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_VertexFormOfQuadraticFunction.py\", line 12, in generate\n    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\core\\gencode\\runtime_skill_wrapper.py\", line 175, in generate_for_skill\n    payload = generate_from_problem_type_spec(skill_id, problem_type_spec, seed=generation_seed)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\core\\gencode\\slot_generators.py\", line 1181, in generate_from_problem_type_spec\n    raise RuntimeError(f\"generator_semantically_unsafe:{','.join(errors)}\")\nRuntimeError: generator_semantically_unsafe:invalid_answer_type: problem_type_id=integer_quadratic_standard_to_vertex_properties answer_type=integer answer_shape=text_short answer='D' answer_type=str checker=integer_checker equivalence=numeric_exact expected=numeric allows int/float/numeric string; answer_shape=text_short\n",
        "problem_type_id": "integer_quadratic_standard_to_vertex_properties",
        "seed": 2
      },
      "failed_validator_name": "slot_generators.validate_generator_payload",
      "validation_diagnostics": {
        "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "answer_repr": "'向右 1、向上 2'",
        "answer_python_type": "str",
        "correct_answer_repr": "'向右 1、向上 2'",
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
        "expected_answer_shape": "short_answer allows non-empty string; answer_shape=text_short",
        "failed_validator_name": "",
        "validation_reason": ""
      }
    },
    "summary_message": "Draft is not ready for publish yet. Please resolve blockers first."
  },
  "generator_specs": [
    {
      "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string",
      "generator_readiness": "runtime_ready",
      "answer_type": "text_short",
      "template_slot": "quadratic_graph_translation_fill_blank",
      "base_problem_type_id": "quadratic_graph_translation_fill_blank",
      "value_type_prefix": "integer",
      "presentation_mode": "short_answer",
      "answer_shape": "text_short"
    },
    {
      "problem_type_id": "rational_quadratic_graph_translation_fill_blank",
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string",
      "generator_readiness": "runtime_ready",
      "answer_type": "text_short",
      "template_slot": "quadratic_graph_translation_fill_blank",
      "base_problem_type_id": "quadratic_graph_translation_fill_blank",
      "value_type_prefix": "rational",
      "presentation_mode": "short_answer",
      "answer_shape": "text_short"
    },
    {
      "problem_type_id": "integer_quadratic_graph_translation",
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact",
      "generator_readiness": "contract_slot_mismatch",
      "answer_type": "integer",
      "template_slot": "quadratic_graph_translation_fill_blank",
      "base_problem_type_id": "quadratic_graph_translation",
      "value_type_prefix": "integer",
      "answer_shape": "text_short"
    },
    {
      "problem_type_id": "integer_quadratic_vertex_form_properties",
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact",
      "generator_readiness": "contract_slot_mismatch",
      "answer_type": "integer",
      "template_slot": "quadratic_vertex_form_properties",
      "base_problem_type_id": "quadratic_vertex_form_properties",
      "value_type_prefix": "integer",
      "answer_shape": "text_short"
    },
    {
      "problem_type_id": "integer_quadratic_standard_to_vertex_properties",
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact",
      "generator_readiness": "contract_slot_mismatch",
      "answer_type": "integer",
      "template_slot": "quadratic_standard_to_vertex_properties",
      "base_problem_type_id": "quadratic_standard_to_vertex_properties",
      "value_type_prefix": "integer",
      "answer_shape": "text_short"
    }
  ],
  "packaging_usable_count": 5,
  "packaging_diagnostics": {
    "candidate_count": 5,
    "included_count": 5,
    "excluded_count": 0,
    "included": [
      {
        "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
        "generator_key": "vh_數學B1_VertexFormOfQuadraticFunction:integer_quadratic_graph_translation_fill_blank:draft_v1",
        "generator_status": "runtime_ready_with_warning"
      },
      {
        "problem_type_id": "rational_quadratic_graph_translation_fill_blank",
        "generator_key": "vh_數學B1_VertexFormOfQuadraticFunction:rational_quadratic_graph_translation_fill_blank:draft_v1",
        "generator_status": "runtime_ready_with_warning"
      },
      {
        "problem_type_id": "integer_quadratic_graph_translation",
        "generator_key": "vh_數學B1_VertexFormOfQuadraticFunction:integer_quadratic_graph_translation:draft_v1",
        "generator_status": "runtime_ready_with_warning"
      },
      {
        "problem_type_id": "integer_quadratic_vertex_form_properties",
        "generator_key": "vh_數學B1_VertexFormOfQuadraticFunction:integer_quadratic_vertex_form_properties:draft_v1",
        "generator_status": "runtime_ready_with_warning"
      },
      {
        "problem_type_id": "integer_quadratic_standard_to_vertex_properties",
        "generator_key": "vh_數學B1_VertexFormOfQuadraticFunction:integer_quadratic_standard_to_vertex_properties:draft_v1",
        "generator_status": "runtime_ready_with_warning"
      }
    ],
    "excluded": [],
    "phase2_summary_exists": true,
    "generator_draft_spec_exists": true,
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_VertexFormOfQuadraticFunction_phase2_generator_summary.json",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_VertexFormOfQuadraticFunction_generator_draft_spec.json",
    "runtime_spec_alignment": {
      "status": "synced",
      "synced_spec_count": 5,
      "synced_problem_type_ids": [
        "integer_quadratic_graph_translation_fill_blank",
        "rational_quadratic_graph_translation_fill_blank",
        "integer_quadratic_graph_translation",
        "integer_quadratic_vertex_form_properties",
        "integer_quadratic_standard_to_vertex_properties"
      ],
      "induced_spec_path": "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_VertexFormOfQuadraticFunction.json",
      "purged_induced_spec_path": "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_VertexFormOfQuadraticFunction.json",
      "purged_induced_spec_paths": [
        "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_VertexFormOfQuadraticFunction.json"
      ],
      "runtime_usable_problem_type_ids": [
        "integer_quadratic_graph_translation",
        "integer_quadratic_graph_translation_fill_blank",
        "integer_quadratic_standard_to_vertex_properties",
        "integer_quadratic_vertex_form_properties",
        "rational_quadratic_graph_translation_fill_blank"
      ],
      "downgraded_historical_problem_type_ids": [],
      "canonical_filter_applied": true
    }
  },
  "reports": {
    "phase3_package_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_VertexFormOfQuadraticFunction_phase3_package_summary.json",
    "phase3_package_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_VertexFormOfQuadraticFunction_phase3_package_summary.md",
    "phase3_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_VertexFormOfQuadraticFunction_phase3_package_summary.json",
    "phase3_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_VertexFormOfQuadraticFunction_phase3_package_summary.md",
    "final_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_VertexFormOfQuadraticFunction_phase3_package_summary.json",
    "final_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_VertexFormOfQuadraticFunction_phase3_package_summary.md",
    "draft_skill_file": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_VertexFormOfQuadraticFunction.py"
  },
  "next_action": "review_phase3_publish_check",
  "error": "",
  "dry_run": true,
  "timestamp": "2026-06-13T05:15:04.295237+00:00",
  "generated_with_warning": true,
  "warnings": [
    "consecutive_same_template_variant",
    "low_sample_diversity_tolerance_applied",
    "low_source_examples"
  ],
  "publish_gate_layers": {
    "technical_closed_loop": "FAIL",
    "runtime_quality": "FAIL",
    "web_runtime": "FAIL",
    "source_alignment": "PARTIAL"
  },
  "source_alignment_audit": {
    "status": "PARTIAL",
    "missing_source_aligned_problem_types": [
      "numeric_quadratic_graph_translation_fill_blank_short_answer",
      "numeric_quadratic_graph_translation_short_answer",
      "numeric_quadratic_standard_to_vertex_properties_short_answer",
      "numeric_quadratic_vertex_form_properties_short_answer",
      "single_choice_evaluate_function_value_fallback_application"
    ],
    "underrepresented_runtime_forms": [
      "numeric_quadratic_graph_translation_fill_blank_short_answer",
      "numeric_quadratic_graph_translation_short_answer",
      "numeric_quadratic_standard_to_vertex_properties_short_answer",
      "numeric_quadratic_vertex_form_properties_short_answer",
      "single_choice_evaluate_function_value_fallback_application"
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
  "summary_message": "Phase 3 packaged draft skill file, but draft runtime smoke did not pass. See publish_check / runtime_smoke_raw. usable_generators=5."
}
```
