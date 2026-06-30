# Gencode Phase2 Generator Summary: vh_數學B1_AbsoluteValueInequality

## phase2
```json
{
  "ok": true,
  "phase": "phase2",
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
  "phase1_alignment_blocked": false,
  "alignment_blockers": [],
  "generator_results": [
    {
      "problem_type_id": "text_short_contextual_application",
      "source_example_count": 9,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "integer",
        "answer_shape": "scalar",
        "answer_equivalence": "numeric_exact",
        "checker": "integer_checker",
        "accepted_formats": [
          "5",
          "5.0",
          "-3"
        ],
        "source_has_choices": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "presentation_mode": "short_answer"
      },
      "answer_type": "integer",
      "answer_shape": "scalar",
      "equivalence_type": "numeric_exact",
      "selected_checker": "integer_checker",
      "checker_key": "integer_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_AbsoluteValueInequality:text_short_contextual_application:draft_v1",
      "generator_status": "pending_problem_type_induction",
      "checker_smoke_status": "skipped_with_blockers",
      "dynamic_sampling_status": "skipped_with_blockers",
      "diversity_sampling": {},
      "unique_signature_count": 0,
      "template_variant_distribution": {},
      "variable_coverage_report": {},
      "repetition_warnings": [],
      "requires_human_action": true,
      "blockers": [
        "generic_fallback_blocked_by_source_skill_binding"
      ],
      "warnings": [],
      "usable_for_phase3": false,
      "target_task": "contextual_application",
      "task_family": "generic_numeric_family",
      "base_problem_type_id": "contextual_application",
      "value_type_prefix": "text_short",
      "template_slot": "linear_function_contextual_word_problem",
      "_resolved_template_slot": "linear_function_contextual_word_problem"
    },
    {
      "problem_type_id": "choice_contextual_application",
      "source_example_count": 1,
      "answer_contract": {
        "choices_required": true,
        "choice_count": 4,
        "correct_choice_count": 1,
        "frontend_render_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "answer_semantics": "choice_label",
        "answer_equivalence": "choice_label",
        "checker": "choice_label_checker",
        "presentation_mode": "single_choice",
        "source_has_choices": true,
        "selected_checker": "choice_label_checker",
        "checker_selection_reason": "explicit_single_choice",
        "accepted_formats": [
          "A",
          "B",
          "C",
          "D"
        ],
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker",
        "fallback_checker": "text_short_checker",
        "fallback_checker_key": "text_short_checker"
      },
      "answer_type": "single_choice",
      "answer_shape": "single_choice",
      "equivalence_type": "choice_label",
      "selected_checker": "choice_label_checker",
      "checker_key": "choice_label_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_AbsoluteValueInequality:choice_contextual_application:draft_v1",
      "generator_status": "pending_problem_type_induction",
      "checker_smoke_status": "skipped_with_blockers",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {},
      "unique_signature_count": 0,
      "template_variant_distribution": {},
      "variable_coverage_report": {},
      "repetition_warnings": [
        "low_sample_diversity_tolerance_applied",
        "low_source_examples"
      ],
      "requires_human_action": true,
      "blockers": [
        "generic_fallback_blocked_by_source_skill_binding"
      ],
      "warnings": [
        "low_sample_diversity_tolerance_applied",
        "low_source_examples"
      ],
      "usable_for_phase3": false,
      "target_task": "contextual_application",
      "task_family": "generic_numeric_family",
      "base_problem_type_id": "contextual_application",
      "value_type_prefix": "choice",
      "template_slot": "linear_function_contextual_word_problem",
      "_resolved_template_slot": "linear_function_contextual_word_problem"
    }
  ],
  "failed_generators": [
    "vh_數學B1_AbsoluteValueInequality:choice_contextual_application:draft_v1",
    "vh_數學B1_AbsoluteValueInequality:text_short_contextual_application:draft_v1"
  ],
  "accepted_generators": [],
  "foundation_preflight": {
    "foundation_ready": true,
    "foundation_status": "PASS",
    "missing_checker": [],
    "missing_verifier": [],
    "missing_domain_function": [],
    "missing_generator": [],
    "missing_runtime_binding": [],
    "missing_registry_binding": [],
    "missing_answer_contract_problem_types": [],
    "repair_plan": [],
    "next_action": "phase3_package_draft"
  },
  "foundation_ready": true,
  "phase2_status": "PASS",
  "repair_plan": [],
  "reports": {
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase2_generator_summary.json",
    "phase2_generator_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase2_generator_summary.md",
    "phase2_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase2_generator_summary.json",
    "phase2_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase2_generator_summary.md",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_AbsoluteValueInequality_generator_draft_spec.json"
  },
  "next_action": "phase3_package_draft",
  "timestamp": "2026-06-30T15:11:48.136942+00:00",
  "dry_run": true
}
```
