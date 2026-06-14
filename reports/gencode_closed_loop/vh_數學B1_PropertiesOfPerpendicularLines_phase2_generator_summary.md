# Gencode Phase2 Generator Summary: vh_數學B1_PropertiesOfPerpendicularLines

## phase2
```json
{
  "ok": true,
  "phase": "phase2",
  "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
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
      "problem_type_id": "integer_perpendicular_lines_properties",
      "source_example_count": 1,
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
      "generator_key": "vh_數學B1_PropertiesOfPerpendicularLines:integer_perpendicular_lines_properties:draft_v1",
      "generator_status": "validation_failed",
      "checker_smoke_status": "skipped_with_blockers",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {},
      "unique_signature_count": "",
      "template_variant_distribution": {},
      "variable_coverage_report": {},
      "repetition_warnings": [
        "low_sample_diversity_tolerance_applied",
        "low_source_examples"
      ],
      "requires_human_action": false,
      "blockers": [
        "generator_not_ready"
      ],
      "warnings": [
        "low_sample_diversity_tolerance_applied",
        "low_source_examples"
      ],
      "usable_for_phase3": false,
      "target_task": "perpendicular_lines_properties",
      "base_problem_type_id": "perpendicular_lines_properties",
      "value_type_prefix": "integer",
      "template_slot": "",
      "_resolved_template_slot": ""
    },
    {
      "problem_type_id": "text_short_contextual_application",
      "source_example_count": 4,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "answer_equivalence": "exact_string",
        "checker": "text_short_checker",
        "accepted_formats": [],
        "source_has_choices": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "presentation_mode": "short_answer"
      },
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "equivalence_type": "exact_string",
      "selected_checker": "text_short_checker",
      "checker_key": "text_short_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_PropertiesOfPerpendicularLines:text_short_contextual_application:draft_v1",
      "generator_status": "validation_failed",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "generator_diversity_blocked",
      "diversity_sampling": {
        "diversity_sampling_status": "generator_diversity_blocked",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 29,
        "unique_question_text_count": 30,
        "template_variant_distribution": {
          "live": 30
        },
        "answer_shape_distribution": {
          "322": 1,
          "31": 1,
          "579": 1,
          "423": 1,
          "424": 1,
          "70": 1,
          "259": 1,
          "253": 1,
          "39": 1,
          "334": 1,
          "265": 1,
          "361": 1,
          "25": 1,
          "522": 1,
          "559": 2,
          "252": 1,
          "54": 1,
          "274": 1,
          "350": 1,
          "284": 1,
          "41": 1,
          "42": 1,
          "367": 1,
          "50": 1,
          "46": 1,
          "405": 1,
          "316": 1,
          "511": 1,
          "44": 1
        },
        "variable_coverage_report": {
          "ratio_forms": [],
          "coordinate_patterns": [
            ""
          ],
          "answer_type_modes": [
            ""
          ]
        },
        "repetition_warnings": [
          "consecutive_same_template_variant"
        ],
        "diversity_blockers": [
          "checker_answer_mismatch:spec_text_but_payload_numeric"
        ],
        "max_consecutive_same_template": 30,
        "generation_errors": [],
        "sampling_mode": "live",
        "contract_mismatch_blockers": [
          "checker_answer_mismatch:spec_text_but_payload_numeric"
        ]
      },
      "unique_signature_count": 29,
      "template_variant_distribution": {
        "live": 30
      },
      "variable_coverage_report": {
        "ratio_forms": [],
        "coordinate_patterns": [
          ""
        ],
        "answer_type_modes": [
          ""
        ]
      },
      "repetition_warnings": [
        "consecutive_same_template_variant"
      ],
      "requires_human_action": false,
      "blockers": [
        "checker_answer_mismatch:spec_text_but_payload_numeric"
      ],
      "warnings": [
        "consecutive_same_template_variant"
      ],
      "usable_for_phase3": false,
      "target_task": "contextual_application",
      "base_problem_type_id": "contextual_application",
      "value_type_prefix": "text_short",
      "template_slot": "linear_function_contextual_word_problem",
      "_resolved_template_slot": "linear_function_contextual_word_problem"
    },
    {
      "problem_type_id": "text_short_applied_quadratic_inequality_problem",
      "source_example_count": 1,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "source_has_choices": false,
        "answer_type": "interval",
        "answer_shape": "interval_or_union",
        "answer_semantics": "interval_union",
        "answer_equivalence": "interval_equivalence",
        "equivalence_type": "interval_equivalence",
        "checker": "interval_checker",
        "checker_key": "interval_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "interval_checker",
        "checker_selection_reason": "quadratic_inequality_interval_solution",
        "accepted_formats": [
          "-5 <= x <= 1",
          "(-5, 1]",
          "x in [-5,1]",
          "x<-2 or x>5",
          "-2<x<5",
          "x<=-2 or x>=5"
        ]
      },
      "answer_type": "interval",
      "answer_shape": "interval_or_union",
      "equivalence_type": "interval_equivalence",
      "selected_checker": "interval_checker",
      "checker_key": "interval_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_PropertiesOfPerpendicularLines:text_short_applied_quadratic_inequality_problem:draft_v1",
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
          "generator_semantically_unsafe:generator_semantically_unsafe:{\"can_continue\": false, \"error_type\": \"parse_error\", \"expect",
          "generator_semantically_unsafe:generator_semantically_unsafe:{\"can_continue\": false, \"error_type\": \"parse_error\", \"expect",
          "generator_semantically_unsafe:generator_semantically_unsafe:{\"can_continue\": false, \"error_type\": \"parse_error\", \"expect",
          "generator_semantically_unsafe:generator_semantically_unsafe:{\"can_continue\": false, \"error_type\": \"parse_error\", \"expect",
          "generator_semantically_unsafe:generator_semantically_unsafe:{\"can_continue\": false, \"error_type\": \"parse_error\", \"expect"
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
      "target_task": "applied_quadratic_inequality_problem",
      "base_problem_type_id": "applied_quadratic_inequality_problem",
      "value_type_prefix": "text_short",
      "template_slot": "applied_quadratic_inequality_problem",
      "_resolved_template_slot": "applied_quadratic_inequality_problem"
    },
    {
      "problem_type_id": "text_short_solve_unknown_coordinate_from_two_point_distance",
      "source_example_count": 1,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "integer",
        "answer_shape": "unordered_set",
        "answer_equivalence": "numeric_exact",
        "checker": "integer_checker",
        "accepted_formats": [
          "-3, 7",
          "7, -3",
          "{-3, 7}",
          "k=-3 或 k=7",
          "-3 或 7"
        ],
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_type": "integer",
      "answer_shape": "unordered_set",
      "equivalence_type": "numeric_exact",
      "selected_checker": "integer_checker",
      "checker_key": "integer_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_PropertiesOfPerpendicularLines:text_short_solve_unknown_coordinate_from_two_point_distance:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "passed",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 30,
        "unique_question_text_count": 23,
        "template_variant_distribution": {
          "word_context_distance": 8,
          "direct_distance": 10,
          "missing_coordinate": 7,
          "compare_distance": 5
        },
        "answer_shape_distribution": {
          "(-1,-1)": 1,
          "(-5,-9)": 1,
          "(-2,6)": 1,
          "(11,-6)": 1,
          "(8,11)": 1,
          "(-6,-2)": 1,
          "(-4,-3)": 1,
          "(14,-4)": 1,
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
          "(9,13)": 2,
          "(6,4)": 1,
          "(6,9)": 1,
          "(6,3)": 1,
          "(-4,-2)": 1,
          "(1,7)": 1,
          "(3,-4)": 1
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
          "generator_semantically_unsafe:invalid_answer_type: problem_type_id=fallback_solve_unknown_coordinate_from_two_point_dist",
          "generator_semantically_unsafe:invalid_answer_type: problem_type_id=fallback_solve_unknown_coordinate_from_two_point_dist",
          "generator_semantically_unsafe:invalid_answer_type: problem_type_id=fallback_solve_unknown_coordinate_from_two_point_dist",
          "generator_semantically_unsafe:invalid_answer_type: problem_type_id=fallback_solve_unknown_coordinate_from_two_point_dist",
          "generator_semantically_unsafe:invalid_answer_type: problem_type_id=fallback_solve_unknown_coordinate_from_two_point_dist"
        ],
        "sampling_mode": "contract_simulation"
      },
      "unique_signature_count": 30,
      "template_variant_distribution": {
        "word_context_distance": 8,
        "direct_distance": 10,
        "missing_coordinate": 7,
        "compare_distance": 5
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
      "target_task": "solve_unknown_coordinate_from_two_point_distance",
      "base_problem_type_id": "solve_unknown_coordinate_from_two_point_distance",
      "value_type_prefix": "text_short",
      "template_slot": "two_point_distance_solution_set",
      "_resolved_template_slot": "two_point_distance_solution_set"
    }
  ],
  "failed_generators": [
    "vh_數學B1_PropertiesOfPerpendicularLines:integer_perpendicular_lines_properties:draft_v1",
    "vh_數學B1_PropertiesOfPerpendicularLines:text_short_contextual_application:draft_v1"
  ],
  "accepted_generators": [
    "vh_數學B1_PropertiesOfPerpendicularLines:text_short_applied_quadratic_inequality_problem:draft_v1",
    "vh_數學B1_PropertiesOfPerpendicularLines:text_short_solve_unknown_coordinate_from_two_point_distance:draft_v1"
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
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfPerpendicularLines_phase2_generator_summary.json",
    "phase2_generator_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfPerpendicularLines_phase2_generator_summary.md",
    "phase2_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfPerpendicularLines_phase2_generator_summary.json",
    "phase2_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfPerpendicularLines_phase2_generator_summary.md",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_PropertiesOfPerpendicularLines_generator_draft_spec.json"
  },
  "next_action": "phase3_package_draft",
  "timestamp": "2026-06-14T15:28:47.250999+00:00",
  "dry_run": true
}
```
