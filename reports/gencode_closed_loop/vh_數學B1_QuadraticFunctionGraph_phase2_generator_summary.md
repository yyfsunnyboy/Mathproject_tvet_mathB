# Gencode Phase2 Generator Summary: vh_數學B1_QuadraticFunctionGraph

## phase2
```json
{
  "ok": true,
  "phase": "phase2",
  "skill_id": "vh_數學B1_QuadraticFunctionGraph",
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
      "problem_type_id": "integer_quadratic_graph_translation_fill_blank",
      "source_example_count": 2,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "source_has_choices": false,
        "answer_type": "integer",
        "answer_shape": "text_short",
        "answer_semantics": "text_short",
        "answer_equivalence": "numeric_exact",
        "equivalence_type": "numeric_exact",
        "checker": "integer_checker",
        "checker_key": "integer_checker",
        "presentation_mode": "",
        "selected_checker": "text_short_checker",
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point"
          ],
          "required_math_objects": [
            "coordinate_point"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "numeric_computation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable",
            "duplicated_choices",
            "no_correct_choice",
            "multiple_correct_choices_when_single_choice"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "quadratic_graph_translation_fill_blank"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "problem_type_id": "numeric_quadratic_graph_translation_fill_blank_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ],
          "template_slots": {
            "stem": "quadratic_graph_translation_fill_blank"
          }
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks",
            "choices_policy"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "text_short"
      },
      "answer_type": "integer",
      "answer_shape": "text_short",
      "equivalence_type": "numeric_exact",
      "selected_checker": "integer_checker",
      "checker_key": "integer_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_QuadraticFunctionGraph:integer_quadratic_graph_translation_fill_blank:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "runtime_ready_with_diversity_warning",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 23,
        "unique_question_text_count": 29,
        "template_variant_distribution": {
          "live": 30
        },
        "answer_shape_distribution": {
          "向左 2、向上 3": 2,
          "向右 2、向上 3": 1,
          "向右 2、向下 2": 1,
          "向左 2、向下 1": 1,
          "向右 1、向上 1": 2,
          "向右 3、向上 1": 1,
          "向左 1、向下 2": 2,
          "向右 2、向上 1": 1,
          "向右 1、向上 2": 2,
          "向右 3、向下 1": 1,
          "向右 1、向上 3": 2,
          "向右 3、向下 2": 2,
          "向左 1、向上 1": 1,
          "向左 3、向上 3": 1,
          "向右 3、向上 3": 1,
          "向左 1、向下 3": 1,
          "向右 1、向下 2": 1,
          "向右 1、向下 3": 2,
          "向右 1、向上 4": 1,
          "向左 1、向上 2": 1,
          "向右 3、向下 3": 1,
          "向左 1、向上 4": 1,
          "向左 1、向上 3": 1
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
        "diversity_blockers": [],
        "max_consecutive_same_template": 30,
        "generation_errors": [],
        "sampling_mode": "live"
      },
      "unique_signature_count": 23,
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
      "usable_for_phase3": true
    },
    {
      "problem_type_id": "rational_quadratic_graph_translation_fill_blank",
      "source_example_count": 1,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "source_has_choices": false,
        "answer_type": "rational",
        "answer_shape": "text_short",
        "answer_semantics": "text_short",
        "answer_equivalence": "rational_equivalent",
        "equivalence_type": "rational_equivalent",
        "checker": "rational_checker",
        "checker_key": "rational_checker",
        "presentation_mode": "",
        "selected_checker": "text_short_checker",
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point"
          ],
          "required_math_objects": [
            "coordinate_point"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "numeric_computation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable",
            "duplicated_choices",
            "no_correct_choice",
            "multiple_correct_choices_when_single_choice"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "quadratic_graph_translation_fill_blank"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "problem_type_id": "numeric_quadratic_graph_translation_fill_blank_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ],
          "template_slots": {
            "stem": "quadratic_graph_translation_fill_blank"
          }
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks",
            "choices_policy"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "text_short"
      },
      "answer_type": "rational",
      "answer_shape": "text_short",
      "equivalence_type": "rational_equivalent",
      "selected_checker": "rational_checker",
      "checker_key": "rational_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_QuadraticFunctionGraph:rational_quadratic_graph_translation_fill_blank:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "runtime_ready_with_diversity_warning",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 23,
        "unique_question_text_count": 29,
        "template_variant_distribution": {
          "live": 30
        },
        "answer_shape_distribution": {
          "向左 2、向上 3": 2,
          "向右 2、向上 3": 1,
          "向右 2、向下 2": 1,
          "向左 2、向下 1": 1,
          "向右 1、向上 1": 2,
          "向右 3、向上 1": 1,
          "向左 1、向下 2": 2,
          "向右 2、向上 1": 1,
          "向右 1、向上 2": 2,
          "向右 3、向下 1": 1,
          "向右 1、向上 3": 2,
          "向右 3、向下 2": 2,
          "向左 1、向上 1": 1,
          "向左 3、向上 3": 1,
          "向右 3、向上 3": 1,
          "向左 1、向下 3": 1,
          "向右 1、向下 2": 1,
          "向右 1、向下 3": 2,
          "向右 1、向上 4": 1,
          "向左 1、向上 2": 1,
          "向右 3、向下 3": 1,
          "向左 1、向上 4": 1,
          "向左 1、向上 3": 1
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
        "diversity_blockers": [],
        "max_consecutive_same_template": 30,
        "generation_errors": [],
        "sampling_mode": "live"
      },
      "unique_signature_count": 23,
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
      "usable_for_phase3": true
    },
    {
      "problem_type_id": "integer_quadratic_graph_properties_choice",
      "source_example_count": 1,
      "answer_contract": {
        "choices_required": true,
        "choice_count": 4,
        "correct_choice_count": 1,
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
        "selected_checker": "choice_label_checker",
        "accepted_formats": [
          "A",
          "B",
          "C",
          "D"
        ],
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "two_coordinate_points"
          ],
          "required_math_objects": [
            "coordinate_point",
            "two_coordinate_points"
          ],
          "forbidden_patterns": [
            "\\(A\\)",
            "\\(B\\)",
            "\\(C\\)",
            "\\(D\\)"
          ]
        },
        "dependency_contract": {
          "givens_must_be_used": true,
          "target_answer_must_depend_on_givens": true,
          "variables_in_conditions_must_appear_in_target": false
        },
        "semantic_contract": {
          "reasoning_type": [
            "numeric_computation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable",
            "duplicated_choices",
            "no_correct_choice",
            "multiple_correct_choices_when_single_choice"
          ]
        },
        "generator_contract": {
          "template_variants": [
            {
              "id": "default",
              "label": "default",
              "stem_pattern": "依題意求解：{stem_hint}。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "seed": {
              "type": "integer",
              "randomize": true
            },
            "difficulty_level": {
              "choices": [
                "level_1",
                "level_2",
                "level_3"
              ],
              "weights": [
                0.4,
                0.4,
                0.2
              ]
            }
          },
          "variation_dimensions": [
            "seed",
            "difficulty_level",
            "context_style"
          ],
          "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {}
          },
          "anti_repetition_rules": {
            "avoid_same_template_consecutive": true,
            "avoid_same_ratio_consecutive": true,
            "avoid_same_point_names_consecutive": true,
            "avoid_same_answer_consecutive": true,
            "recent_history_window": 5,
            "signature_fields": [
              "problem_type_id",
              "template_variant",
              "ratio_form",
              "ratio_values",
              "coordinate_pattern",
              "answer"
            ]
          },
          "validity_constraints": [
            "answer derivable from givens"
          ],
          "answer_shape": "numeric",
          "explanation_variants": [
            "stepwise"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "quadratic_graph_properties_choice"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "problem_type_id": "numeric_quadratic_graph_properties_choice_single_choice",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ],
          "template_slots": {
            "stem": "quadratic_vertex_form_properties"
          }
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks",
            "choices_policy"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "single_choice",
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
      "generator_key": "vh_數學B1_QuadraticFunctionGraph:integer_quadratic_graph_properties_choice:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "generator_diversity_blocked",
        "diversity_healthy": false,
        "sample_count": 30,
        "unique_signature_count": 4,
        "unique_question_text_count": 30,
        "template_variant_distribution": {
          "live": 30
        },
        "answer_shape_distribution": {
          "D": 7,
          "C": 7,
          "A": 10,
          "B": 6
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
          "low_unique_signature_count",
          "consecutive_same_template_variant"
        ],
        "diversity_blockers": [
          "generator_diversity_blocked",
          "consecutive_template_diversity_blocked"
        ],
        "max_consecutive_same_template": 30,
        "generation_errors": [],
        "sampling_mode": "live"
      },
      "unique_signature_count": 4,
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
        "consecutive_same_template_variant",
        "low_sample_diversity_tolerance_applied",
        "low_source_examples",
        "low_unique_signature_count"
      ],
      "requires_human_action": false,
      "blockers": [],
      "warnings": [
        "consecutive_same_template_variant",
        "low_sample_diversity_tolerance_applied",
        "low_source_examples",
        "low_unique_signature_count"
      ],
      "usable_for_phase3": true
    }
  ],
  "failed_generators": [],
  "accepted_generators": [
    "vh_數學B1_QuadraticFunctionGraph:integer_quadratic_graph_translation_fill_blank:draft_v1",
    "vh_數學B1_QuadraticFunctionGraph:rational_quadratic_graph_translation_fill_blank:draft_v1",
    "vh_數學B1_QuadraticFunctionGraph:integer_quadratic_graph_properties_choice:draft_v1"
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
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticFunctionGraph_phase2_generator_summary.json",
    "phase2_generator_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticFunctionGraph_phase2_generator_summary.md",
    "phase2_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticFunctionGraph_phase2_generator_summary.json",
    "phase2_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticFunctionGraph_phase2_generator_summary.md",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_QuadraticFunctionGraph_generator_draft_spec.json"
  },
  "next_action": "phase3_package_draft",
  "timestamp": "2026-06-13T05:06:07.095674+00:00",
  "dry_run": true
}
```
