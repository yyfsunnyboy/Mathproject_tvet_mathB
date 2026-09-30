# Gencode Phase3 Package Summary: mock_packaging_phase3

## phase3
```json
{
  "ok": false,
  "phase": "phase3",
  "skill_id": "mock_packaging_phase3",
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
  "skill_file_path": "C:\\Projects\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\mock_packaging_phase3.py",
  "package_status": "blocked_no_usable_generators",
  "py_compile_status": "not_run_no_usable_generators",
  "runtime_smoke_status": "failed",
  "runtime_smoke_raw": {
    "status": "failed",
    "blockers": [
      "runtime_smoke_failed_at_seed_0",
      "semantic_drifting_fatal"
    ],
    "payload_preview": {
      "problem_type_id": "absolute_value_distance_between_two_points",
      "answer_type": "integer",
      "answer_contract_answer_type": null,
      "checker": null,
      "equivalence": null,
      "question_text_len": 38,
      "answer": 5,
      "correct_answer": 5,
      "choices_count": 0,
      "metadata_keys": [
        "scenario_family",
        "scenario_id",
        "parameter_signature",
        "question_pattern_id",
        "diagnosis_tags",
        "prerequisite_subskills"
      ]
    },
    "interface_check": {
      "generate_exists": true,
      "check_exists": true,
      "generate_returns_dict": true,
      "check_callable": true
    },
    "py_compile_status": "passed",
    "samples_tested": 0,
    "negative_semantic_smoke": "passed",
    "validation_diagnostics": {}
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
      "runtime_smoke_failed_at_seed_0",
      "semantic_drifting_fatal"
    ],
    "py_compile_status": "passed",
    "interface_check": {
      "generate_exists": true,
      "check_exists": true,
      "generate_returns_dict": true,
      "check_callable": true
    },
    "runtime_smoke_status": "failed",
    "runtime_smoke_raw": {
      "status": "failed",
      "blockers": [
        "runtime_smoke_failed_at_seed_0",
        "semantic_drifting_fatal"
      ],
      "payload_preview": {
        "problem_type_id": "absolute_value_distance_between_two_points",
        "answer_type": "integer",
        "answer_contract_answer_type": null,
        "checker": null,
        "equivalence": null,
        "question_text_len": 38,
        "answer": 5,
        "correct_answer": 5,
        "choices_count": 0,
        "metadata_keys": [
          "scenario_family",
          "scenario_id",
          "parameter_signature",
          "question_pattern_id",
          "diagnosis_tags",
          "prerequisite_subskills"
        ]
      },
      "interface_check": {
        "generate_exists": true,
        "check_exists": true,
        "generate_returns_dict": true,
        "check_callable": true
      },
      "py_compile_status": "passed",
      "samples_tested": 0,
      "negative_semantic_smoke": "passed",
      "validation_diagnostics": {}
    },
    "summary_message": "Draft is not ready for publish yet. Please resolve blockers first."
  },
  "generator_specs": [],
  "packaging_usable_count": 0,
  "packaging_diagnostics": {
    "candidate_count": 0,
    "included_count": 0,
    "excluded_count": 0,
    "included": [],
    "excluded": [],
    "phase2_summary_exists": true,
    "generator_draft_spec_exists": false,
    "phase2_generator_summary_json": "C:\\Projects\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\mock_packaging_phase3_phase2_generator_summary.json",
    "generator_draft_spec_json": "C:\\Projects\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\mock_packaging_phase3_generator_draft_spec.json",
    "runtime_spec_alignment": {
      "status": "skipped_no_aligned_draft_specs",
      "synced_spec_count": 0,
      "synced_problem_type_ids": [],
      "purged_induced_spec_path": "reports\\gencode_closed_loop\\induced_specs\\mock_packaging_phase3.json",
      "purged_induced_spec_paths": [],
      "runtime_usable_problem_type_ids": [],
      "downgraded_historical_problem_type_ids": [],
      "canonical_filter_applied": false
    }
  },
  "reports": {
    "phase3_package_summary_json": "C:\\Projects\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\mock_packaging_phase3_phase3_package_summary.json",
    "phase3_package_summary_md": "C:\\Projects\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\mock_packaging_phase3_phase3_package_summary.md",
    "phase3_json": "C:\\Projects\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\mock_packaging_phase3_phase3_package_summary.json",
    "phase3_md": "C:\\Projects\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\mock_packaging_phase3_phase3_package_summary.md",
    "final_json": "C:\\Projects\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\mock_packaging_phase3_phase3_package_summary.json",
    "final_md": "C:\\Projects\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\mock_packaging_phase3_phase3_package_summary.md",
    "draft_skill_file": "C:\\Projects\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\mock_packaging_phase3.py"
  },
  "next_action": "review_phase2_blockers_before_phase3",
  "error": "",
  "dry_run": true,
  "timestamp": "2026-09-29T15:09:07.770793+00:00",
  "generated_with_warning": false,
  "warnings": [],
  "publish_gate_layers": {
    "technical_closed_loop": "FAIL",
    "runtime_quality": "FAIL",
    "web_runtime": "FAIL",
    "source_alignment": "PASS"
  },
  "source_alignment_audit": {
    "status": "PASS",
    "missing_source_aligned_problem_types": [],
    "underrepresented_runtime_forms": []
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
  "summary_message": "Phase 3 blocked: no usable generators for packaging (candidates=0, included=0).",
  "packaging_diagnostic_message": "Phase 3 blocked: no usable generators for packaging (candidates=0, included=0)."
}
```
