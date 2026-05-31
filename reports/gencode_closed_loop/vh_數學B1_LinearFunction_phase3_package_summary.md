# Gencode Phase3 Package Summary: vh_數學B1_LinearFunction

## phase3
```json
{
  "ok": false,
  "phase": "phase3",
  "skill_id": "vh_數學B1_LinearFunction",
  "sop_reference": {
    "sop_policy_version": "v0.2",
    "highest_sop": "docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.2.md",
    "required_sop_files": [
      {
        "path": "docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.2.md",
        "exists": true,
        "readable": true,
        "mojibake_detected": false
      },
      {
        "path": "docs/系統SOP/Gencode_AgentSkillV2整合/AgentSkillV2_ProblemType規格包設計_v0.2.md",
        "exists": true,
        "readable": true,
        "mojibake_detected": false
      },
      {
        "path": "docs/系統SOP/Gencode_AgentSkillV2整合/AnswerContract_EquivalenceType_Gate_v0.2.md",
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
  "skill_file_path": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_LinearFunction.py",
  "package_status": "blocked_no_usable_generators",
  "py_compile_status": "passed",
  "runtime_smoke_status": "failed",
  "runtime_smoke_raw": {
    "status": "failed",
    "blockers": [
      "runtime_smoke_generate_exception"
    ],
    "payload_preview": {
      "problem_type_id": "numeric_numeric_evaluate_function_notation_short_answer",
      "answer_type": "numeric",
      "answer_contract_answer_type": "numeric",
      "checker": "numeric_checker",
      "equivalence": "numeric_equivalence",
      "question_text_len": 23,
      "answer": "12",
      "correct_answer": "12",
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
      "generate_returns_dict": false,
      "check_callable": true
    },
    "py_compile_status": "passed",
    "samples_tested": 1,
    "negative_semantic_smoke": "passed",
    "error": "generator_semantically_unsafe:invalid_answer_type: problem_type_id=numeric_numeric_evaluate_function_notation_short_answer answer_type=numeric answer_shape=scalar answer='\\\\sqrt{109}' answer_type=str checker=numeric_checker equivalence=numeric_equivalence expected=numeric allows int/float/numeric string; answer_shape=scalar,numeric_equivalence_invalid",
    "failed_seed": 1,
    "runtime_smoke_raw": {
      "exception_type": "RuntimeError",
      "exception_message": "generator_semantically_unsafe:invalid_answer_type: problem_type_id=numeric_numeric_evaluate_function_notation_short_answer answer_type=numeric answer_shape=scalar answer='\\\\sqrt{109}' answer_type=str checker=numeric_checker equivalence=numeric_equivalence expected=numeric allows int/float/numeric string; answer_shape=scalar,numeric_equivalence_invalid",
      "traceback_preview": "Traceback (most recent call last):\n  File \"E:\\Python\\Mathproject_tvet_mathB\\core\\gencode\\runtime_smoke.py\", line 255, in run_draft_runtime_smoke\n    payload = gen(level=1, seed=seed)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_LinearFunction.py\", line 12, in generate\n    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\core\\gencode\\runtime_skill_wrapper.py\", line 174, in generate_for_skill\n    payload = generate_from_problem_type_spec(skill_id, problem_type_spec, seed=generation_seed)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\core\\gencode\\slot_generators.py\", line 498, in generate_from_problem_type_spec\n    raise RuntimeError(f\"generator_semantically_unsafe:{','.join(errors)}\")\nRuntimeError: generator_semantically_unsafe:invalid_answer_type: problem_type_id=numeric_numeric_evaluate_function_notation_short_answer answer_type=numeric answer_shape=scalar answer='\\\\sqrt{109}' answer_type=str checker=numeric_checker equivalence=numeric_equivalence expected=numeric allows int/float/numeric string; answer_shape=scalar,numeric_equivalence_invalid\n",
      "problem_type_id": "numeric_numeric_evaluate_function_notation_short_answer",
      "seed": 1
    },
    "failed_validator_name": "slot_generators.validate_generator_payload",
    "validation_diagnostics": {
      "problem_type_id": "numeric_numeric_evaluate_function_notation_short_answer",
      "answer_type": "numeric",
      "answer_shape": "scalar",
      "checker": "numeric_checker",
      "equivalence": "numeric_equivalence",
      "answer_repr": "'12'",
      "answer_python_type": "str",
      "correct_answer_repr": "'12'",
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
      "expected_answer_shape": "numeric allows int/float/numeric string; answer_shape=scalar",
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
        "problem_type_id": "numeric_numeric_evaluate_function_notation_short_answer",
        "answer_type": "numeric",
        "answer_contract_answer_type": "numeric",
        "checker": "numeric_checker",
        "equivalence": "numeric_equivalence",
        "question_text_len": 23,
        "answer": "12",
        "correct_answer": "12",
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
        "generate_returns_dict": false,
        "check_callable": true
      },
      "py_compile_status": "passed",
      "samples_tested": 1,
      "negative_semantic_smoke": "passed",
      "error": "generator_semantically_unsafe:invalid_answer_type: problem_type_id=numeric_numeric_evaluate_function_notation_short_answer answer_type=numeric answer_shape=scalar answer='\\\\sqrt{109}' answer_type=str checker=numeric_checker equivalence=numeric_equivalence expected=numeric allows int/float/numeric string; answer_shape=scalar,numeric_equivalence_invalid",
      "failed_seed": 1,
      "runtime_smoke_raw": {
        "exception_type": "RuntimeError",
        "exception_message": "generator_semantically_unsafe:invalid_answer_type: problem_type_id=numeric_numeric_evaluate_function_notation_short_answer answer_type=numeric answer_shape=scalar answer='\\\\sqrt{109}' answer_type=str checker=numeric_checker equivalence=numeric_equivalence expected=numeric allows int/float/numeric string; answer_shape=scalar,numeric_equivalence_invalid",
        "traceback_preview": "Traceback (most recent call last):\n  File \"E:\\Python\\Mathproject_tvet_mathB\\core\\gencode\\runtime_smoke.py\", line 255, in run_draft_runtime_smoke\n    payload = gen(level=1, seed=seed)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_LinearFunction.py\", line 12, in generate\n    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\core\\gencode\\runtime_skill_wrapper.py\", line 174, in generate_for_skill\n    payload = generate_from_problem_type_spec(skill_id, problem_type_spec, seed=generation_seed)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\core\\gencode\\slot_generators.py\", line 498, in generate_from_problem_type_spec\n    raise RuntimeError(f\"generator_semantically_unsafe:{','.join(errors)}\")\nRuntimeError: generator_semantically_unsafe:invalid_answer_type: problem_type_id=numeric_numeric_evaluate_function_notation_short_answer answer_type=numeric answer_shape=scalar answer='\\\\sqrt{109}' answer_type=str checker=numeric_checker equivalence=numeric_equivalence expected=numeric allows int/float/numeric string; answer_shape=scalar,numeric_equivalence_invalid\n",
        "problem_type_id": "numeric_numeric_evaluate_function_notation_short_answer",
        "seed": 1
      },
      "failed_validator_name": "slot_generators.validate_generator_payload",
      "validation_diagnostics": {
        "problem_type_id": "numeric_numeric_evaluate_function_notation_short_answer",
        "answer_type": "numeric",
        "answer_shape": "scalar",
        "checker": "numeric_checker",
        "equivalence": "numeric_equivalence",
        "answer_repr": "'12'",
        "answer_python_type": "str",
        "correct_answer_repr": "'12'",
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
        "expected_answer_shape": "numeric allows int/float/numeric string; answer_shape=scalar",
        "failed_validator_name": "",
        "validation_reason": ""
      }
    },
    "summary_message": "Draft is not ready for publish yet. Please resolve blockers first."
  },
  "generator_specs": [],
  "packaging_usable_count": 0,
  "packaging_diagnostics": {
    "candidate_count": 1,
    "included_count": 0,
    "excluded_count": 1,
    "included": [],
    "excluded": [
      {
        "problem_type_id": "integer_numeric_evaluate_function_notation",
        "generator_key": "vh_數學B1_LinearFunction:integer_numeric_evaluate_function_notation:draft_v1",
        "generator_status": "validation_failed",
        "checker_smoke_status": "skipped_with_blockers",
        "dynamic_sampling_status": "skipped_with_blockers",
        "blockers": [
          "generator_not_ready"
        ],
        "warnings": [],
        "reasons": [
          "status_not_packaging_ready:validation_failed",
          "checker_smoke_status_not_passed",
          "dynamic_sampling_status_not_passed",
          "blockers:generator_not_ready",
          "usable_for_phase3_false"
        ]
      }
    ],
    "phase2_summary_exists": true,
    "generator_draft_spec_exists": true,
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_phase2_generator_summary.json",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_LinearFunction_generator_draft_spec.json"
  },
  "reports": {
    "phase3_package_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_phase3_package_summary.json",
    "phase3_package_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_phase3_package_summary.md",
    "phase3_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_phase3_package_summary.json",
    "phase3_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_phase3_package_summary.md",
    "final_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_phase3_package_summary.json",
    "final_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_phase3_package_summary.md",
    "draft_skill_file": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_LinearFunction.py"
  },
  "next_action": "review_phase2_blockers_before_phase3",
  "error": "",
  "dry_run": true,
  "timestamp": "2026-05-31T16:08:03.632796+00:00",
  "generated_with_warning": false,
  "warnings": [],
  "publish_gate_layers": {
    "technical_closed_loop": "FAIL",
    "runtime_quality": "FAIL",
    "web_runtime": "FAIL",
    "source_alignment": "PARTIAL"
  },
  "source_alignment_audit": {
    "status": "PARTIAL",
    "missing_source_aligned_problem_types": [
      "numeric_numeric_evaluate_function_notation_short_answer"
    ],
    "underrepresented_runtime_forms": [
      "numeric_numeric_evaluate_function_notation_short_answer"
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
  "summary_message": "Phase 3 blocked: no usable generators for packaging (candidates=1, included=0).\n  - integer_numeric_evaluate_function_notation: status_not_packaging_ready:validation_failed;checker_smoke_status_not_passed;dynamic_sampling_status_not_passed;blockers:generator_not_ready;usable_for_phase3_false",
  "packaging_diagnostic_message": "Phase 3 blocked: no usable generators for packaging (candidates=1, included=0).\n  - integer_numeric_evaluate_function_notation: status_not_packaging_ready:validation_failed;checker_smoke_status_not_passed;dynamic_sampling_status_not_passed;blockers:generator_not_ready;usable_for_phase3_false"
}
```
