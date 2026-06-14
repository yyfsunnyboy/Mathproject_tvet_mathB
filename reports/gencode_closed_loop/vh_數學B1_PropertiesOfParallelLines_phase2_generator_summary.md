# Gencode Phase2 Generator Summary: vh_數學B1_PropertiesOfParallelLines

## phase2
```json
{
  "ok": true,
  "phase": "phase2",
  "skill_id": "vh_數學B1_PropertiesOfParallelLines",
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
      "problem_type_id": "text_short_compute_distance_between_two_points",
      "source_example_count": 2,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "answer_equivalence": "algebraic_equivalent",
        "checker": "expression_checker",
        "accepted_formats": [
          "(x-5)(x+3)",
          "(2x-1)(x+5)",
          "2(x-1)(3x+2)"
        ],
        "equivalence_type": "algebraic_equivalent",
        "checker_key": "expression_checker",
        "answer_semantics": "algebraic_expression",
        "presentation_mode": "short_answer"
      },
      "answer_type": "expression",
      "answer_shape": "factored_expression",
      "equivalence_type": "algebraic_equivalent",
      "selected_checker": "expression_checker",
      "checker_key": "expression_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_PropertiesOfParallelLines:text_short_compute_distance_between_two_points:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "passed",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 28,
        "unique_question_text_count": 25,
        "template_variant_distribution": {
          "word_context_distance": 7,
          "direct_distance": 8,
          "missing_coordinate": 6,
          "compare_distance": 4,
          "live": 5
        },
        "answer_shape_distribution": {
          "(-1,-1)": 1,
          "(-5,-9)": 1,
          "(-2,6)": 1,
          "(11,-6)": 1,
          "(8,11)": 1,
          "9": 1,
          "1": 3,
          "(13,7)": 1,
          "(11,5)": 1,
          "(10,10)": 1,
          "(0,14)": 1,
          "(6,-3)": 1,
          "(4,-1)": 1,
          "(13,12)": 1,
          "(-8,-3)": 1,
          "(-2,12)": 1,
          "(-1,-2)": 1,
          "(-3,6)": 1,
          "(3,11)": 1,
          "(5,7)": 1,
          "(10,0)": 1,
          "(9,13)": 1,
          "(6,4)": 1,
          "(6,9)": 1,
          "(6,3)": 1,
          "(-4,-2)": 1,
          "4": 1,
          "(3,-4)": 1
        },
        "variable_coverage_report": {
          "ratio_forms": [
            "AP:PB=m:n",
            "AP=mPB",
            "mAP=nPB"
          ],
          "coordinate_patterns": [
            "",
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
        "max_consecutive_same_template": 3,
        "generation_errors": [
          "generator_semantically_unsafe:generator_semantically_unsafe:{\"can_continue\": false, \"error_type\": \"parse_error\", \"expect",
          "generator_semantically_unsafe:generator_semantically_unsafe:{\"can_continue\": false, \"error_type\": \"parse_error\", \"expect",
          "generator_semantically_unsafe:generator_semantically_unsafe:{\"can_continue\": false, \"error_type\": \"parse_error\", \"expect",
          "generator_semantically_unsafe:generator_semantically_unsafe:{\"can_continue\": false, \"error_type\": \"parse_error\", \"expect",
          "generator_semantically_unsafe:generator_semantically_unsafe:{\"can_continue\": false, \"error_type\": \"parse_error\", \"expect"
        ],
        "sampling_mode": "contract_simulation"
      },
      "unique_signature_count": 28,
      "template_variant_distribution": {
        "word_context_distance": 7,
        "direct_distance": 8,
        "missing_coordinate": 6,
        "compare_distance": 4,
        "live": 5
      },
      "variable_coverage_report": {
        "ratio_forms": [
          "AP:PB=m:n",
          "AP=mPB",
          "mAP=nPB"
        ],
        "coordinate_patterns": [
          "",
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
      "repetition_warnings": [
        "low_sample_diversity_tolerance_applied",
        "low_source_examples"
      ],
      "requires_human_action": false,
      "blockers": [],
      "warnings": [
        "low_sample_diversity_tolerance_applied",
        "low_source_examples"
      ],
      "usable_for_phase3": true,
      "target_task": "compute_distance_between_two_points",
      "base_problem_type_id": "compute_distance_between_two_points",
      "value_type_prefix": "text_short",
      "template_slot": "two_point_distance_compute",
      "_resolved_template_slot": "two_point_distance_compute"
    },
    {
      "problem_type_id": "choice_contextual_application",
      "source_example_count": 2,
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
      "generator_key": "vh_數學B1_PropertiesOfParallelLines:choice_contextual_application:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "runtime_ready_with_diversity_warning",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 30,
        "unique_question_text_count": 14,
        "template_variant_distribution": {
          "default": 30
        },
        "answer_shape_distribution": {
          "(-8,-2)": 1,
          "(9,8)": 1,
          "(-4,12)": 1,
          "(2,12)": 1,
          "(-1,-6)": 2,
          "(8,-2)": 1,
          "(7,2)": 1,
          "(10,7)": 1,
          "(3,0)": 1,
          "(4,-1)": 1,
          "(0,1)": 1,
          "(-2,1)": 1,
          "(-2,5)": 1,
          "(1,15)": 1,
          "(9,6)": 1,
          "(10,9)": 1,
          "(7,-4)": 1,
          "(-9,8)": 1,
          "(0,5)": 1,
          "(-1,8)": 1,
          "(7,-9)": 1,
          "(15,9)": 1,
          "(-5,-5)": 1,
          "(1,-4)": 1,
          "(3,-5)": 1,
          "(12,2)": 1,
          "(0,-8)": 1,
          "(3,6)": 1,
          "(1,-6)": 1
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
        "repetition_warnings": [
          "consecutive_same_template_variant"
        ],
        "diversity_blockers": [],
        "max_consecutive_same_template": 30,
        "generation_errors": [
          "generator_semantically_unsafe:answer_not_in_choices,choice_count_mismatch,choices_missing,generator_semantically_unsafe:",
          "generator_semantically_unsafe:answer_not_in_choices,choice_count_mismatch,choices_missing,generator_semantically_unsafe:",
          "generator_semantically_unsafe:answer_not_in_choices,choice_count_mismatch,choices_missing,generator_semantically_unsafe:",
          "generator_semantically_unsafe:answer_not_in_choices,choice_count_mismatch,choices_missing,generator_semantically_unsafe:",
          "generator_semantically_unsafe:answer_not_in_choices,choice_count_mismatch,choices_missing,generator_semantically_unsafe:"
        ],
        "sampling_mode": "contract_simulation"
      },
      "unique_signature_count": 30,
      "template_variant_distribution": {
        "default": 30
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
      "repetition_warnings": [
        "consecutive_same_template_variant",
        "low_sample_diversity_tolerance_applied",
        "low_source_examples"
      ],
      "requires_human_action": false,
      "blockers": [],
      "warnings": [
        "consecutive_same_template_variant",
        "low_sample_diversity_tolerance_applied",
        "low_source_examples"
      ],
      "usable_for_phase3": true,
      "target_task": "contextual_application",
      "base_problem_type_id": "contextual_application",
      "value_type_prefix": "choice",
      "template_slot": "linear_function_contextual_word_problem",
      "_resolved_template_slot": "linear_function_contextual_word_problem"
    }
  ],
  "failed_generators": [],
  "accepted_generators": [
    "vh_數學B1_PropertiesOfParallelLines:choice_contextual_application:draft_v1",
    "vh_數學B1_PropertiesOfParallelLines:text_short_compute_distance_between_two_points:draft_v1"
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
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfParallelLines_phase2_generator_summary.json",
    "phase2_generator_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfParallelLines_phase2_generator_summary.md",
    "phase2_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfParallelLines_phase2_generator_summary.json",
    "phase2_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfParallelLines_phase2_generator_summary.md",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_PropertiesOfParallelLines_generator_draft_spec.json"
  },
  "next_action": "phase3_package_draft",
  "timestamp": "2026-06-14T14:24:15.510017+00:00",
  "dry_run": true
}
```
