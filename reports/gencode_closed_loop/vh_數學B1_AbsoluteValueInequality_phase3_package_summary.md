# Gencode Phase3 Package Summary: vh_數學B1_AbsoluteValueInequality

## phase3
```json
{
  "ok": false,
  "phase": "phase3",
  "skill_id": "vh_數學B1_AbsoluteValueInequality",
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
  "skill_file_path": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_AbsoluteValueInequality.py",
  "package_status": "blocked_no_usable_generators",
  "py_compile_status": "not_run_no_usable_generators",
  "runtime_smoke_status": "failed",
  "runtime_smoke_raw": {
    "status": "failed",
    "blockers": [
      "draft_skill_file_missing"
    ],
    "payload_preview": {},
    "interface_check": {},
    "py_compile_status": "not_run",
    "samples_tested": 0
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
      "draft_skill_file_missing"
    ],
    "py_compile_status": "not_run",
    "interface_check": {},
    "runtime_smoke_status": "failed",
    "runtime_smoke_raw": {
      "status": "failed",
      "blockers": [
        "draft_skill_file_missing"
      ],
      "payload_preview": {},
      "interface_check": {},
      "py_compile_status": "not_run",
      "samples_tested": 0
    },
    "summary_message": "Draft is not ready for publish yet. Please resolve blockers first."
  },
  "generator_specs": [],
  "packaging_usable_count": 0,
  "packaging_diagnostics": {
    "candidate_count": 2,
    "included_count": 0,
    "excluded_count": 2,
    "included": [],
    "excluded": [
      {
        "problem_type_id": "text_short_contextual_application",
        "generator_key": "vh_數學B1_AbsoluteValueInequality:text_short_contextual_application:draft_v1",
        "generator_status": "pending_problem_type_induction",
        "checker_smoke_status": "skipped_with_blockers",
        "dynamic_sampling_status": "skipped_with_blockers",
        "blockers": [
          "generic_fallback_blocked_by_source_skill_binding"
        ],
        "warnings": [],
        "reasons": [
          "status_not_packaging_ready:pending_problem_type_induction",
          "checker_smoke_status_not_passed",
          "dynamic_sampling_status_not_passed",
          "blockers:generic_fallback_blocked_by_source_skill_binding",
          "requires_human_action",
          "usable_for_phase3_false"
        ]
      },
      {
        "problem_type_id": "choice_contextual_application",
        "generator_key": "vh_數學B1_AbsoluteValueInequality:choice_contextual_application:draft_v1",
        "generator_status": "pending_problem_type_induction",
        "checker_smoke_status": "skipped_with_blockers",
        "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
        "blockers": [
          "generic_fallback_blocked_by_source_skill_binding"
        ],
        "warnings": [
          "low_sample_diversity_tolerance_applied",
          "low_source_examples"
        ],
        "reasons": [
          "choice_prefix_on_non_choice_slot",
          "status_not_packaging_ready:pending_problem_type_induction",
          "checker_smoke_status_not_passed",
          "blockers:generic_fallback_blocked_by_source_skill_binding",
          "requires_human_action",
          "usable_for_phase3_false"
        ]
      }
    ],
    "phase2_summary_exists": true,
    "generator_draft_spec_exists": true,
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase2_generator_summary.json",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_AbsoluteValueInequality_generator_draft_spec.json",
    "runtime_spec_alignment": {
      "status": "skipped_no_aligned_draft_specs",
      "synced_spec_count": 0,
      "synced_problem_type_ids": [],
      "purged_induced_spec_path": "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_AbsoluteValueInequality.json",
      "purged_induced_spec_paths": [
        "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_AbsoluteValueInequality.json"
      ],
      "runtime_usable_problem_type_ids": [],
      "downgraded_historical_problem_type_ids": [],
      "canonical_filter_applied": true
    }
  },
  "reports": {
    "phase3_package_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase3_package_summary.json",
    "phase3_package_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase3_package_summary.md",
    "phase3_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase3_package_summary.json",
    "phase3_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase3_package_summary.md",
    "final_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase3_package_summary.json",
    "final_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase3_package_summary.md",
    "draft_skill_file": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_AbsoluteValueInequality.py"
  },
  "next_action": "review_phase2_blockers_before_phase3",
  "error": "",
  "dry_run": true,
  "timestamp": "2026-06-30T15:11:38.962659+00:00",
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
      "skill_scoped_unresolved_problem_type",
      "skill_scoped_unresolved_problem_type_2"
    ],
    "underrepresented_runtime_forms": [
      "skill_scoped_unresolved_problem_type",
      "skill_scoped_unresolved_problem_type_2"
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
  "summary_message": "Phase 3 blocked: no usable generators for packaging (candidates=2, included=0).\n  - text_short_contextual_application: status_not_packaging_ready:pending_problem_type_induction;checker_smoke_status_not_passed;dynamic_sampling_status_not_passed;blockers:generic_fallback_blocked_by_source_skill_binding;requires_human_action;usable_for_phase3_false\n  - choice_contextual_application: choice_prefix_on_non_choice_slot;status_not_packaging_ready:pending_problem_type_induction;checker_smoke_status_not_passed;blockers:generic_fallback_blocked_by_source_skill_binding;requires_human_action;usable_for_phase3_false",
  "packaging_diagnostic_message": "Phase 3 blocked: no usable generators for packaging (candidates=2, included=0).\n  - text_short_contextual_application: status_not_packaging_ready:pending_problem_type_induction;checker_smoke_status_not_passed;dynamic_sampling_status_not_passed;blockers:generic_fallback_blocked_by_source_skill_binding;requires_human_action;usable_for_phase3_false\n  - choice_contextual_application: choice_prefix_on_non_choice_slot;status_not_packaging_ready:pending_problem_type_induction;checker_smoke_status_not_passed;blockers:generic_fallback_blocked_by_source_skill_binding;requires_human_action;usable_for_phase3_false"
}
```
