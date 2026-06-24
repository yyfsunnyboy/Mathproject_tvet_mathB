# Gencode Phase2 Generator Summary: vh_數學B1_PointSlopeForm

## phase2
```json
{
  "ok": true,
  "phase": "phase2",
  "skill_id": "vh_數學B1_PointSlopeForm",
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
      "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "source_example_count": 10,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "source_has_choices": false,
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "answer_semantics": "line_equation",
        "answer_equivalence": "linear_equation_equivalent",
        "equivalence_type": "linear_equation_equivalent",
        "checker": "linear_equation_equivalent_checker",
        "checker_key": "linear_equation_equivalent_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "linear_equation_equivalent_checker",
        "checker_selection_reason": "line_equation_family",
        "accepted_formats": [
          "y - 2 = 3(x - 1)",
          "y = 3x - 1",
          "3x - y - 1 = 0"
        ],
        "fallback_checker": "text_short_checker",
        "fallback_checker_key": "text_short_checker"
      },
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "equivalence_type": "linear_equation_equivalent",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_PointSlopeForm:equation_write_line_equation_from_point_slope_short_answer:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "passed",
      "diversity_sampling": {
        "diversity_sampling_status": "passed",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 30,
        "unique_question_text_count": 25,
        "template_variant_distribution": {
          "given_point_and_slope_find_slope_intercept_form": 11,
          "given_point_and_slope_find_point_slope_form": 11,
          "given_point_and_slope_find_general_form": 8
        },
        "answer_shape_distribution": {
          "linear_equation_unparseable": 30
        },
        "variable_coverage_report": {
          "ratio_forms": [
            "AP:PB=m:n",
            "AP=mPB",
            "mAP=nPB"
          ],
          "coordinate_patterns": [
            "++",
            "+-",
            "-+",
            "--",
            "mixed"
          ],
          "answer_type_modes": [
            ""
          ]
        },
        "repetition_warnings": [],
        "diversity_blockers": [],
        "max_consecutive_same_template": 1,
        "generation_errors": [
          "'list' object has no attribute 'get'",
          "'list' object has no attribute 'get'",
          "'list' object has no attribute 'get'",
          "'list' object has no attribute 'get'",
          "'list' object has no attribute 'get'"
        ],
        "sampling_mode": "contract_simulation"
      },
      "unique_signature_count": 30,
      "template_variant_distribution": {
        "given_point_and_slope_find_slope_intercept_form": 11,
        "given_point_and_slope_find_point_slope_form": 11,
        "given_point_and_slope_find_general_form": 8
      },
      "variable_coverage_report": {
        "ratio_forms": [
          "AP:PB=m:n",
          "AP=mPB",
          "mAP=nPB"
        ],
        "coordinate_patterns": [
          "++",
          "+-",
          "-+",
          "--",
          "mixed"
        ],
        "answer_type_modes": [
          ""
        ]
      },
      "repetition_warnings": [],
      "requires_human_action": false,
      "blockers": [],
      "warnings": [],
      "usable_for_phase3": true,
      "target_task": "write_line_equation_from_point_slope",
      "task_family": "line_equation_family",
      "base_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "value_type_prefix": "",
      "template_slot": "line_equation_from_point_slope",
      "_resolved_template_slot": "line_equation_from_point_slope"
    },
    {
      "problem_type_id": "equation_write_line_equation_from_point_slope_single_choice",
      "source_example_count": 1,
      "answer_contract": {
        "choices_required": true,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": true,
        "source_has_choices": false,
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "answer_semantics": "choice_label",
        "answer_equivalence": "choice_label",
        "equivalence_type": "choice_label",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "presentation_mode": "single_choice",
        "selected_checker": "linear_equation_equivalent_checker",
        "checker_selection_reason": "line_equation_family",
        "accepted_formats": [
          "A",
          "B",
          "C",
          "D"
        ],
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
      "generator_key": "vh_數學B1_PointSlopeForm:equation_write_line_equation_from_point_slope_single_choice:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "skipped_pending_line_equation_mcq_slot",
        "diversity_healthy": false,
        "sample_count": 0,
        "unique_signature_count": 0,
        "unique_question_text_count": 0,
        "template_variant_distribution": {},
        "answer_shape_distribution": {},
        "variable_coverage_report": {},
        "repetition_warnings": [
          "line_equation_single_choice_slot_not_ready"
        ],
        "diversity_blockers": [
          "line_equation_single_choice_slot_not_ready"
        ],
        "max_consecutive_same_template": 0,
        "generation_errors": [],
        "sampling_mode": "skipped_pending_line_equation_mcq_slot"
      },
      "unique_signature_count": 0,
      "template_variant_distribution": {},
      "variable_coverage_report": {},
      "repetition_warnings": [
        "line_equation_single_choice_slot_not_ready",
        "low_sample_diversity_tolerance_applied",
        "low_source_examples"
      ],
      "requires_human_action": true,
      "blockers": [
        "line_equation_single_choice_slot_not_ready"
      ],
      "warnings": [
        "line_equation_single_choice_slot_not_ready",
        "low_sample_diversity_tolerance_applied",
        "low_source_examples"
      ],
      "usable_for_phase3": false,
      "target_task": "write_line_equation_from_point_slope",
      "task_family": "line_equation_family",
      "base_problem_type_id": "equation_write_line_equation_from_point_slope_single_choice",
      "value_type_prefix": "",
      "template_slot": "line_equation_from_point_slope",
      "_resolved_template_slot": "line_equation_from_point_slope"
    }
  ],
  "failed_generators": [
    "vh_數學B1_PointSlopeForm:equation_write_line_equation_from_point_slope_single_choice:draft_v1"
  ],
  "accepted_generators": [
    "vh_數學B1_PointSlopeForm:equation_write_line_equation_from_point_slope_short_answer:draft_v1"
  ],
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
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase2_generator_summary.json",
    "phase2_generator_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase2_generator_summary.md",
    "phase2_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase2_generator_summary.json",
    "phase2_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase2_generator_summary.md",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_PointSlopeForm_generator_draft_spec.json"
  },
  "next_action": "phase3_package_draft",
  "timestamp": "2026-06-24T16:38:36.120892+00:00",
  "dry_run": true
}
```
