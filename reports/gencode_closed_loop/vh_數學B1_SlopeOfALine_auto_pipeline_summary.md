# Gencode Auto Pipeline Summary: vh_數學B1_SlopeOfALine

## summary
```json
{
  "ok": false,
  "skill_id": "vh_數學B1_SlopeOfALine",
  "pipeline_status": "auto_pipeline_completed_runtime_blocked",
  "source_example_count": 12,
  "candidate_problem_types": [
    {
      "problem_type_id": "integer_compute_numeric",
      "proposed_problem_type_id": "integer_compute_numeric",
      "display_name": "integer / compute_numeric",
      "matched_example_ids": [
        4529
      ],
      "matched_example_count": 1,
      "unmatched_example_ids": [],
      "representative_example_id": 4529,
      "structural_features": [
        "text_short"
      ],
      "answer_contract_proposal": {
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
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "required_math_objects": [
            "coordinate_point",
            "three_coordinate_points"
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
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
          "problem_type_id": "numeric_compute_numeric_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ],
          "template_slots": {
            "stem": "point_quadrant"
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
      "checker_key_proposal": "integer_checker",
      "equivalence_type_proposal": "numeric_exact",
      "answer_shape": "text_short",
      "answer_semantics": "text_short",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "text_short_checker",
      "checker_selection_reason": "task_family_default",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "alignment_score_below_recommended_threshold",
        "majority_sources_need_human_subskill_review",
        "skill_scoped_classification_low_confidence",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "numeric",
        "compute_numeric",
        "short_answer",
        [
          "numeric_computation"
        ],
        [
          "coordinate_point",
          "three_coordinate_points"
        ]
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "text_short_compute_text_short_expression",
        "skill_id": "vh_數學B1_SlopeOfALine",
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "display_name": "numeric / compute_numeric",
        "answer_format_hint": "",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          4529
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "source_has_choices": false,
          "answer_type": "text_short",
          "answer_shape": "text_short",
          "answer_semantics": "text_short",
          "answer_equivalence": "exact_string",
          "equivalence_type": "exact_string",
          "checker": "text_short_checker",
          "checker_key": "text_short_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "text_short_checker"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "required_math_objects": [
            "coordinate_point",
            "three_coordinate_points"
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
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
          "problem_type_id": "numeric_compute_numeric_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ],
          "template_slots": {
            "stem": "point_quadrant"
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
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "numeric",
          "compute_numeric",
          "short_answer",
          [
            "numeric_computation"
          ],
          [
            "coordinate_point",
            "three_coordinate_points"
          ]
        ],
        "canonical_base_problem_type_id": "compute_numeric_short_answer",
        "value_type_prefix": "numeric",
        "_resolved_template_slot": "point_quadrant"
      },
      "generator_readiness": "runtime_ready",
      "usable_for_phase3": true,
      "template_slot": "point_quadrant",
      "canonical_base_problem_type_id": "compute_numeric_short_answer",
      "value_type_prefix": "numeric",
      "subskill_id": "compute_numeric",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0312,
        "task_consistent_with_skill": true
      },
      "answer_type": "text_short"
    },
    {
      "problem_type_id": "integer_applied_quadratic_inequality_problem",
      "proposed_problem_type_id": "integer_applied_quadratic_inequality_problem",
      "display_name": "integer / applied_quadratic_inequality_problem",
      "matched_example_ids": [
        4524,
        4534
      ],
      "matched_example_count": 2,
      "unmatched_example_ids": [],
      "representative_example_id": 4524,
      "structural_features": [
        "interval_or_union"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "source_has_choices": false,
        "answer_type": "integer",
        "answer_shape": "interval_or_union",
        "answer_semantics": "interval_union",
        "answer_equivalence": "numeric_exact",
        "equivalence_type": "numeric_exact",
        "checker": "integer_checker",
        "checker_key": "integer_checker",
        "presentation_mode": "",
        "selected_checker": "interval_checker",
        "checker_selection_reason": "quadratic_inequality_interval_solution",
        "accepted_formats": [
          "-5 <= x <= 1",
          "(-5, 1]",
          "x in [-5,1]",
          "x<-2 or x>5",
          "-2<x<5",
          "x<=-2 or x>=5"
        ],
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "required_math_objects": [
            "coordinate_point",
            "three_coordinate_points"
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
            "quadratic_factoring_reasoning"
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
              "routing_track",
              "scenario_type",
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
            "applied_quadratic_inequality_problem"
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
          "template_slots": {
            "stem": "applied_quadratic_inequality_problem"
          },
          "problem_type_id": "numeric_applied_quadratic_inequality_problem_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
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
        "canonical_answer_schema": "interval"
      },
      "checker_key_proposal": "integer_checker",
      "equivalence_type_proposal": "numeric_exact",
      "answer_shape": "interval_or_union",
      "answer_semantics": "interval_union",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "interval_checker",
      "checker_selection_reason": "quadratic_inequality_interval_solution",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "alignment_score_below_recommended_threshold",
        "majority_sources_need_human_subskill_review",
        "skill_scoped_classification_low_confidence",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "merged_by_canonical_contract",
      "feature_signature": [
        "canonical_contract_merge",
        "applied_quadratic_inequality_problem",
        "numeric",
        "short_answer"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "interval_applied_quadratic_inequality_problem_expression",
        "skill_id": "vh_數學B1_SlopeOfALine",
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "display_name": "numeric / applied_quadratic_inequality_problem",
        "answer_format_hint": "interval",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          4524,
          4534
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "source_has_choices": false,
          "answer_type": "interval",
          "answer_shape": "interval_or_union",
          "answer_semantics": "interval_union",
          "answer_equivalence": "interval_set",
          "equivalence_type": "interval_set",
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
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "required_math_objects": [
            "coordinate_point",
            "three_coordinate_points"
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
            "quadratic_factoring_reasoning"
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
              "routing_track",
              "scenario_type",
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
            "applied_quadratic_inequality_problem"
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
          "template_slots": {
            "stem": "applied_quadratic_inequality_problem"
          },
          "problem_type_id": "numeric_applied_quadratic_inequality_problem_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
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
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "merged_by_canonical_contract",
        "feature_signature": [
          "canonical_contract_merge",
          "applied_quadratic_inequality_problem",
          "numeric",
          "short_answer"
        ],
        "canonical_base_problem_type_id": "applied_quadratic_inequality_problem_short_answer",
        "value_type_prefix": "numeric",
        "_resolved_template_slot": "applied_quadratic_inequality_problem",
        "naming_warning": "naming_warning:interval_task_value_prefix_ignored"
      },
      "generator_readiness": "runtime_ready",
      "usable_for_phase3": true,
      "template_slot": "applied_quadratic_inequality_problem",
      "canonical_base_problem_type_id": "applied_quadratic_inequality_problem_short_answer",
      "value_type_prefix": "numeric",
      "subskill_id": "applied_quadratic_inequality_problem",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0448,
        "task_consistent_with_skill": true
      },
      "answer_type": "interval"
    },
    {
      "problem_type_id": "integer_evaluate_function_value",
      "proposed_problem_type_id": "integer_evaluate_function_value",
      "display_name": "integer / evaluate_function_value",
      "matched_example_ids": [
        4519,
        4520,
        4521,
        4522,
        4523,
        4525,
        4533
      ],
      "matched_example_count": 7,
      "unmatched_example_ids": [],
      "representative_example_id": 4519,
      "structural_features": [
        "scalar"
      ],
      "answer_contract_proposal": {
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
        "checker_key": "integer_checker",
        "equivalence_type": "numeric_exact",
        "selected_checker": "numeric_checker",
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "required_math_objects": [
            "coordinate_point",
            "three_coordinate_points"
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
            "numeric_computation",
            "distance_formula_reasoning"
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
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
          "contextual_application": true,
          "template_slots": {
            "stem": "function_value_numeric"
          },
          "problem_type_id": "numeric_evaluate_function_value_fallback_application",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
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
        "canonical_answer_schema": "numeric",
        "presentation_mode": ""
      },
      "checker_key_proposal": "integer_checker",
      "equivalence_type_proposal": "numeric_exact",
      "answer_shape": "scalar",
      "answer_semantics": "scalar",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "numeric_checker",
      "checker_selection_reason": "task_family_default",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "alignment_score_below_recommended_threshold",
        "majority_sources_need_human_subskill_review",
        "skill_scoped_classification_low_confidence",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "merged_by_canonical_contract",
      "feature_signature": [
        "canonical_contract_merge",
        "evaluate_function_value",
        "numeric",
        "short_answer"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "integer_evaluate_function_value_fallback_application",
        "skill_id": "vh_數學B1_SlopeOfALine",
        "target_task": "evaluate_function_value",
        "task_family": "function_concept_family",
        "display_name": "numeric / evaluate_function_value",
        "answer_format_hint": "",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          4519,
          4520,
          4521,
          4522,
          4523,
          4525,
          4533
        ],
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
          "equivalence_type": "numeric_exact",
          "checker_key": "integer_checker"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "required_math_objects": [
            "coordinate_point",
            "three_coordinate_points"
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
            "numeric_computation",
            "distance_formula_reasoning"
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
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
          "contextual_application": true,
          "template_slots": {
            "stem": "function_value_numeric"
          },
          "problem_type_id": "numeric_evaluate_function_value_fallback_application",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
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
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "merged_by_canonical_contract",
        "feature_signature": [
          "canonical_contract_merge",
          "evaluate_function_value",
          "numeric",
          "short_answer"
        ],
        "canonical_base_problem_type_id": "evaluate_function_value_fallback_application",
        "value_type_prefix": "numeric",
        "_resolved_template_slot": "function_value_numeric"
      },
      "generator_readiness": "runtime_ready",
      "usable_for_phase3": true,
      "template_slot": "function_value_numeric",
      "canonical_base_problem_type_id": "evaluate_function_value_fallback_application",
      "value_type_prefix": "numeric",
      "subskill_id": "evaluate_function_value",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0476,
        "task_consistent_with_skill": true
      },
      "answer_type": "integer"
    },
    {
      "problem_type_id": "integer_evaluate_function_value",
      "proposed_problem_type_id": "integer_evaluate_function_value",
      "display_name": "integer / evaluate_function_value",
      "matched_example_ids": [
        4590,
        4601
      ],
      "matched_example_count": 2,
      "unmatched_example_ids": [],
      "representative_example_id": 4590,
      "structural_features": [
        "single_choice"
      ],
      "answer_contract_proposal": {
        "choices_required": true,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": true,
        "answer_type": "integer",
        "answer_shape": "single_choice",
        "answer_equivalence": "choice_label",
        "checker": "choice_label_checker",
        "accepted_formats": [
          "A",
          "B",
          "C",
          "D"
        ],
        "source_has_choices": true,
        "answer_semantics": "choice_label",
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker",
        "presentation_mode": "",
        "selected_checker": "choice_label_checker",
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "two_coordinate_points",
            "three_coordinate_points",
            "triangle"
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
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
          "contextual_application": true,
          "template_slots": {
            "stem": "function_value_numeric"
          },
          "problem_type_id": "numeric_evaluate_function_value_fallback_application",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
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
        "canonical_answer_schema": "single_choice"
      },
      "checker_key_proposal": "choice_label_checker",
      "equivalence_type_proposal": "choice_label",
      "answer_shape": "single_choice",
      "answer_semantics": "choice_label",
      "presentation_mode": "single_choice",
      "source_has_choices": true,
      "selected_checker": "choice_label_checker",
      "checker_selection_reason": "explicit_single_choice",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "alignment_score_below_recommended_threshold",
        "majority_sources_need_human_subskill_review",
        "skill_scoped_classification_low_confidence",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "merged_by_canonical_contract",
      "feature_signature": [
        "canonical_contract_merge",
        "evaluate_function_value",
        "numeric",
        "single_choice"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "choice_evaluate_function_value_fallback_application",
        "skill_id": "vh_數學B1_SlopeOfALine",
        "target_task": "evaluate_function_value",
        "task_family": "function_concept_family",
        "display_name": "numeric / evaluate_function_value",
        "answer_format_hint": "A/B/C/D",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          4590,
          4601
        ],
        "answer_contract": {
          "choices_required": true,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": true,
          "answer_type": "choice",
          "answer_shape": "single_choice",
          "answer_equivalence": "choice_label",
          "checker": "choice_label_checker",
          "accepted_formats": [
            "A",
            "B",
            "C",
            "D"
          ],
          "source_has_choices": true,
          "answer_semantics": "choice_label",
          "equivalence_type": "choice_label",
          "checker_key": "choice_label_checker",
          "presentation_mode": "single_choice"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "two_coordinate_points",
            "three_coordinate_points",
            "triangle"
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
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
          "contextual_application": true,
          "template_slots": {
            "stem": "function_value_numeric"
          },
          "problem_type_id": "numeric_evaluate_function_value_fallback_application",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
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
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "merged_by_canonical_contract",
        "feature_signature": [
          "canonical_contract_merge",
          "evaluate_function_value",
          "numeric",
          "single_choice"
        ],
        "canonical_base_problem_type_id": "evaluate_function_value_fallback_application",
        "value_type_prefix": "numeric",
        "_resolved_template_slot": "function_value_numeric",
        "naming_warning": "naming_warning:numeric_prefix_but_hint_is_A/B/C/D"
      },
      "generator_readiness": "contract_slot_mismatch",
      "usable_for_phase3": false,
      "template_slot": "function_value_numeric",
      "canonical_base_problem_type_id": "evaluate_function_value_fallback_application",
      "value_type_prefix": "numeric",
      "subskill_id": "evaluate_function_value",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0476,
        "task_consistent_with_skill": true
      },
      "answer_type": "choice"
    }
  ],
  "per_example_classification": [
    {
      "example_id": 4529,
      "detected_problem_type_id": "numeric_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 4529,
        "question_text": "若$A\\left( -2,0 \\right)$、$B\\left( -1,1 \\right)$、$C\\left( k,4 \\right)$三點在同一直線上，試求k之值。",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "C",
          "k"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "k"
        ],
        "target": "compute_numeric",
        "classifier_source": "ai_outsider_candidate",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目給定三點 A(-2,0), B(-1,1), C(k,4) 共線，求 k 的值。",
            "此題利用 AB 斜率等於 BC 斜率的觀念來列式求解，屬於數值計算。"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目清晰且與斜率單元完全契合，無須送審。"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "ai_outsider_candidate",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
          "requires_human_action": true,
          "ai_notes": "根據強制合約，此題屬於直線的斜率單元，利用斜率相等求解 k，選擇 compute_numeric。",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [
            "C1"
          ],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "outsider",
          "selected_generator_contract": {
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
                "routing_track",
                "scenario_type",
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
              "compute_numeric"
            ]
          },
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
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "worked_example",
          "example_label": "例題2",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "worked_example",
          "example_label": "例題2",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": 2,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4519,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 1"
            },
            {
              "example_id": 4520,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 2"
            },
            {
              "example_id": 4521,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 3"
            },
            {
              "example_id": 4522,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 4"
            },
            {
              "example_id": 4523,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 5"
            },
            {
              "example_id": 4524,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 6"
            },
            {
              "example_id": 4525,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 7"
            },
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4533,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4534,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4590,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4601,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題4"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai_outsider_candidate",
      "risk_flags": [
        "outsider_candidate_within_confirmed_skill",
        "requires_human_action"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目給定三點 A(-2,0), B(-1,1), C(k,4) 共線，求 k 的值。",
          "此題利用 AB 斜率等於 BC 斜率的觀念來列式求解，屬於數值計算。"
        ],
        "ai_rejected_candidates": {
          "needs_review": "題目清晰且與斜率單元完全契合，無須送審。"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "ai_outsider_candidate",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
        "requires_human_action": true,
        "ai_notes": "根據強制合約，此題屬於直線的斜率單元，利用斜率相等求解 k，選擇 compute_numeric。",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [
          "C1"
        ],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "outsider",
        "selected_generator_contract": {
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
          ]
        },
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
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "worked_example",
        "example_label": "例題2",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "compute_numeric",
      "classification_source": "ai_outsider_candidate",
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 4519,
      "detected_problem_type_id": "numeric_evaluate_function_value_fallback_application",
      "example_feature": {
        "source_example_id": 4519,
        "question_text": "設、、$C\\left( 5,2 \\right)$、$D\\left( 3,4 \\right)$，試求下列直線的斜率並在坐標平面上畫出圖形。\n(1)直線AB (2)直線BC\n(3)直線AC (4)直線BD。",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "evaluate_function_value",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "C",
          "D"
        ],
        "givens": [
          "C",
          "D"
        ],
        "target": "evaluate_function_value",
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 0.9,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "The question asks to find the slopes of lines AB, BC, AC, and BD, which is a numeric computation task."
          ],
          "ai_rejected_candidates": {
            "needs_review": "The stem has a typo where coordinates for A and B are missing, but the task type is clearly numeric computation, and needs_review is forbidden unless the stem is completely unreadable."
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "evaluate_function_value",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "fallback_application_induct",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "The task is to compute the slope of lines given points, which corresponds to compute_numeric.",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "fallback_application",
          "selected_generator_contract": {
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
                "routing_track",
                "scenario_type",
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
              "compute_numeric"
            ]
          },
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
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4519,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 1"
            },
            {
              "example_id": 4520,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 2"
            },
            {
              "example_id": 4521,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 3"
            },
            {
              "example_id": 4522,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 4"
            },
            {
              "example_id": 4523,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 5"
            },
            {
              "example_id": 4524,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 6"
            },
            {
              "example_id": 4525,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 7"
            },
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4533,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4534,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4590,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4601,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題4"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "problem_type_id": "numeric_evaluate_function_value_fallback_application",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 0.9,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "The question asks to find the slopes of lines AB, BC, AC, and BD, which is a numeric computation task."
        ],
        "ai_rejected_candidates": {
          "needs_review": "The stem has a typo where coordinates for A and B are missing, but the task type is clearly numeric computation, and needs_review is forbidden unless the stem is completely unreadable."
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "evaluate_function_value",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "fallback_application_induct",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "The task is to compute the slope of lines given points, which corresponds to compute_numeric.",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "fallback_application",
        "selected_generator_contract": {
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
          ]
        },
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
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "evaluate_function_value",
      "classification_source": "fallback_application_induct",
      "induction_eligibility": "excluded",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 4520,
      "detected_problem_type_id": "numeric_evaluate_function_value_fallback_application",
      "example_feature": {
        "source_example_id": 4520,
        "question_text": "(1) 請將m = 0、m不存在、m > 0、m < 0，填入下列各圖形的斜率。\n①②③④\n(2) 設${{m}_{1}}$、${{m}_{2}}$分別為直線${{L}_{1}}$、${{L}_{2}}$的斜率，試比較圖①、圖②中${{m}_{1}}$與${{m}_{2}}$的大小。\n① ②",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
        "math_objects": [],
        "target_task": "evaluate_function_value",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "L",
          "m"
        ],
        "givens": [
          "L",
          "m"
        ],
        "target": "evaluate_function_value",
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目要求根據圖形判斷斜率的正負、零或不存在，並比較斜率大小，屬於直線斜率的基本觀念。",
            "依據規定，題目清晰可讀時禁止選擇 needs_review，因此選擇唯一的候選者 C1。"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目語意清晰、圖形描述完整，不符合 needs_review 的選取條件。"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "evaluate_function_value",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "fallback_application_induct",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "本題為直線斜率的觀念判定與大小比較。因 needs_review 僅在題目無法閱讀時使用，故選擇 C1。",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "fallback_application",
          "selected_generator_contract": {
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
                "routing_track",
                "scenario_type",
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
              "compute_numeric"
            ]
          },
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
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4519,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 1"
            },
            {
              "example_id": 4520,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 2"
            },
            {
              "example_id": 4521,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 3"
            },
            {
              "example_id": 4522,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 4"
            },
            {
              "example_id": 4523,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 5"
            },
            {
              "example_id": 4524,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 6"
            },
            {
              "example_id": 4525,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 7"
            },
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4533,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4534,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4590,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4601,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題4"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "problem_type_id": "numeric_evaluate_function_value_fallback_application",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目要求根據圖形判斷斜率的正負、零或不存在，並比較斜率大小，屬於直線斜率的基本觀念。",
          "依據規定，題目清晰可讀時禁止選擇 needs_review，因此選擇唯一的候選者 C1。"
        ],
        "ai_rejected_candidates": {
          "needs_review": "題目語意清晰、圖形描述完整，不符合 needs_review 的選取條件。"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "evaluate_function_value",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "fallback_application_induct",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "本題為直線斜率的觀念判定與大小比較。因 needs_review 僅在題目無法閱讀時使用，故選擇 C1。",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "fallback_application",
        "selected_generator_contract": {
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
          ]
        },
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
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "evaluate_function_value",
      "classification_source": "fallback_application_induct",
      "induction_eligibility": "excluded",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 4521,
      "detected_problem_type_id": "numeric_evaluate_function_value_fallback_application",
      "example_feature": {
        "source_example_id": 4521,
        "question_text": "試求過下列各組A、B兩點的直線斜率：\n(1)$A\\left( 5,-2 \\right)$、$B\\left( -7,4 \\right)$ (2)$A\\left( 3,1 \\right)$、$B\\left( 3,5 \\right)$。",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "evaluate_function_value",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B"
        ],
        "givens": [
          "A",
          "B"
        ],
        "target": "evaluate_function_value",
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目要求計算過兩點 A 與 B 的直線斜率，屬於基礎數值計算。"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目語意清晰且完整，無須送審。"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "evaluate_function_value",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "fallback_application_induct",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "此題為給定兩點求斜率的標準計算題，對應到 compute_numeric 子技能。",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "fallback_application",
          "selected_generator_contract": {
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
                "routing_track",
                "scenario_type",
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
              "compute_numeric"
            ]
          },
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
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4519,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 1"
            },
            {
              "example_id": 4520,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 2"
            },
            {
              "example_id": 4521,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 3"
            },
            {
              "example_id": 4522,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 4"
            },
            {
              "example_id": 4523,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 5"
            },
            {
              "example_id": 4524,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 6"
            },
            {
              "example_id": 4525,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 7"
            },
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4533,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4534,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4590,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4601,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題4"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "problem_type_id": "numeric_evaluate_function_value_fallback_application",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目要求計算過兩點 A 與 B 的直線斜率，屬於基礎數值計算。"
        ],
        "ai_rejected_candidates": {
          "needs_review": "題目語意清晰且完整，無須送審。"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "evaluate_function_value",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "fallback_application_induct",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "此題為給定兩點求斜率的標準計算題，對應到 compute_numeric 子技能。",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "fallback_application",
        "selected_generator_contract": {
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
          ]
        },
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
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "evaluate_function_value",
      "classification_source": "fallback_application_induct",
      "induction_eligibility": "excluded",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 4522,
      "detected_problem_type_id": "numeric_evaluate_function_value_fallback_application",
      "example_feature": {
        "source_example_id": 4522,
        "question_text": "若直線通過點$\\left( 2,a \\right)$與$\\left( 1-a,5 \\right)$，且其斜率為2，試求a之值。",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
        "math_objects": [
          "coordinate_point",
          "two_coordinate_points"
        ],
        "target_task": "evaluate_function_value",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "a"
        ],
        "givens": [
          "a"
        ],
        "target": "evaluate_function_value",
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目給定兩點座標 (2, a) 與 (1-a, 5) 且斜率為 2，要求解未知數 a 的值。",
            "此題屬於直線斜率公式的數值計算應用。"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目清晰且完全符合直線斜率的教學範疇，無須人工審查。"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "evaluate_function_value",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "fallback_application_induct",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "依據強制合約，此題與直線的斜率技能 100% 對齊，且題幹清晰，故選擇 C1。",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "fallback_application",
          "selected_generator_contract": {
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
                "routing_track",
                "scenario_type",
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
              "compute_numeric"
            ]
          },
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
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "two_coordinate_points"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4519,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 1"
            },
            {
              "example_id": 4520,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 2"
            },
            {
              "example_id": 4521,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 3"
            },
            {
              "example_id": 4522,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 4"
            },
            {
              "example_id": 4523,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 5"
            },
            {
              "example_id": 4524,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 6"
            },
            {
              "example_id": 4525,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 7"
            },
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4533,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4534,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4590,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4601,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題4"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "problem_type_id": "numeric_evaluate_function_value_fallback_application",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目給定兩點座標 (2, a) 與 (1-a, 5) 且斜率為 2，要求解未知數 a 的值。",
          "此題屬於直線斜率公式的數值計算應用。"
        ],
        "ai_rejected_candidates": {
          "needs_review": "題目清晰且完全符合直線斜率的教學範疇，無須人工審查。"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "evaluate_function_value",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "fallback_application_induct",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "依據強制合約，此題與直線的斜率技能 100% 對齊，且題幹清晰，故選擇 C1。",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "fallback_application",
        "selected_generator_contract": {
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
          ]
        },
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
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "two_coordinate_points"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "evaluate_function_value",
      "classification_source": "fallback_application_induct",
      "induction_eligibility": "excluded",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 4523,
      "detected_problem_type_id": "numeric_evaluate_function_value_fallback_application",
      "example_feature": {
        "source_example_id": 4523,
        "question_text": "若$A\\left( -1,-1 \\right)$、$B\\left( 2,k \\right)$、$C\\left( 8,5 \\right)$三點共線，試求k之值。",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "evaluate_function_value",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "C",
          "k"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "k"
        ],
        "target": "evaluate_function_value",
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目給定三點 A(-1, -1)、B(2, k)、C(8, 5) 共線，要求未知數 k 的值。",
            "此題利用 AB 斜率等於 AC 斜率的觀念來建立方程式並求解，屬於直線斜率的數值計算。"
          ],
          "ai_rejected_candidates": {
            "needs_review": "題目語意清晰完整，且與直線斜率的核心概念完全符合，不需送審。"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "evaluate_function_value",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "fallback_application_induct",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "透過三點共線斜率相等的性質求解未知數，選擇 compute_numeric。",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "fallback_application",
          "selected_generator_contract": {
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
                "routing_track",
                "scenario_type",
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
              "compute_numeric"
            ]
          },
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
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4519,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 1"
            },
            {
              "example_id": 4520,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 2"
            },
            {
              "example_id": 4521,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 3"
            },
            {
              "example_id": 4522,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 4"
            },
            {
              "example_id": 4523,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 5"
            },
            {
              "example_id": 4524,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 6"
            },
            {
              "example_id": 4525,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 7"
            },
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4533,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4534,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4590,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4601,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題4"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "problem_type_id": "numeric_evaluate_function_value_fallback_application",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目給定三點 A(-1, -1)、B(2, k)、C(8, 5) 共線，要求未知數 k 的值。",
          "此題利用 AB 斜率等於 AC 斜率的觀念來建立方程式並求解，屬於直線斜率的數值計算。"
        ],
        "ai_rejected_candidates": {
          "needs_review": "題目語意清晰完整，且與直線斜率的核心概念完全符合，不需送審。"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "evaluate_function_value",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "fallback_application_induct",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "透過三點共線斜率相等的性質求解未知數，選擇 compute_numeric。",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "fallback_application",
        "selected_generator_contract": {
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
          ]
        },
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
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "evaluate_function_value",
      "classification_source": "fallback_application_induct",
      "induction_eligibility": "excluded",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 4524,
      "detected_problem_type_id": "numeric_applied_quadratic_inequality_problem_short_answer",
      "example_feature": {
        "source_example_id": 4524,
        "question_text": "在坐標平面上，設k為實數，若$P\\left( 2,3 \\right)$、$Q\\left( 4,-5 \\right)$、$R\\left( k,-3 \\right)$三點無法連結成一個三角形，試求k之值。",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "reasoning_type": [
          "quadratic_factoring_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "P",
          "Q",
          "R",
          "k"
        ],
        "givens": [
          "P",
          "Q",
          "R",
          "k"
        ],
        "target": "applied_quadratic_inequality_problem",
        "classifier_source": "ai_outsider_candidate",
        "math_meta_tags": [
          "[Task: Applied_Context]"
        ],
        "forced_target_task": "applied_quadratic_inequality_problem",
        "meta_answer_format_hint": "interval",
        "semantic_classification": {
          "ai_target_task": "applied_quadratic_inequality_problem",
          "ai_task_family": "quadratic_inequality_family",
          "ai_confidence": 0.92,
          "ai_best_candidate_id": "C2",
          "ai_evidence": [
            "The Python math meta preflight instructions explicitly mandate selecting the candidate whose target_task equals forced_target_task (applied_quadratic_inequality_problem).",
            "Candidate C2 has the target_task applied_quadratic_inequality_problem."
          ],
          "ai_rejected_candidates": {
            "C1": "Rejected because C2 is forced by the mandatory preflight instructions.",
            "needs_review": "Rejected because choosing needs_review is forbidden when the stem is readable and a candidate is forced."
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "applied_quadratic_inequality_problem",
          "rule_task_family": "quadratic_inequality_family",
          "rule_confidence": 0.5,
          "final_target_task": "applied_quadratic_inequality_problem",
          "final_task_family": "quadratic_inequality_family",
          "classifier_source": "ai_outsider_candidate",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
          "requires_human_action": true,
          "ai_notes": "Selected C2 as mandated by the forced_target_task rule in the preflight instructions.",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "C2",
              "target_task": "applied_quadratic_inequality_problem",
              "task_family": "quadratic_inequality_family",
              "problem_type_id": "applied_quadratic_inequality_problem",
              "label": "applied_quadratic_inequality_problem",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "applied_quadratic_inequality_problem"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [
            "C2"
          ],
          "selected_subskill": "applied_quadratic_inequality_problem",
          "selected_problem_type": "applied_quadratic_inequality_problem",
          "candidate_source": "outsider",
          "selected_generator_contract": {
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
                "routing_track",
                "scenario_type",
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
              "applied_quadratic_inequality_problem"
            ]
          },
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
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "applied_quadratic_inequality_problem",
          "task_family": "quadratic_inequality_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
          "possible_structure_mismatch": true,
          "possible_mixed_source_context": true
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4519,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 1"
            },
            {
              "example_id": 4520,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 2"
            },
            {
              "example_id": 4521,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 3"
            },
            {
              "example_id": 4522,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 4"
            },
            {
              "example_id": 4523,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 5"
            },
            {
              "example_id": 4524,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 6"
            },
            {
              "example_id": 4525,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 7"
            },
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4533,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4534,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4590,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4601,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題4"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai_outsider_candidate",
      "risk_flags": [
        "outsider_candidate_within_confirmed_skill",
        "requires_human_action"
      ],
      "semantic_classification": {
        "ai_target_task": "applied_quadratic_inequality_problem",
        "ai_task_family": "quadratic_inequality_family",
        "ai_confidence": 0.92,
        "ai_best_candidate_id": "C2",
        "ai_evidence": [
          "The Python math meta preflight instructions explicitly mandate selecting the candidate whose target_task equals forced_target_task (applied_quadratic_inequality_problem).",
          "Candidate C2 has the target_task applied_quadratic_inequality_problem."
        ],
        "ai_rejected_candidates": {
          "C1": "Rejected because C2 is forced by the mandatory preflight instructions.",
          "needs_review": "Rejected because choosing needs_review is forbidden when the stem is readable and a candidate is forced."
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "applied_quadratic_inequality_problem",
        "rule_task_family": "quadratic_inequality_family",
        "rule_confidence": 0.5,
        "final_target_task": "applied_quadratic_inequality_problem",
        "final_task_family": "quadratic_inequality_family",
        "classifier_source": "ai_outsider_candidate",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
        "requires_human_action": true,
        "ai_notes": "Selected C2 as mandated by the forced_target_task rule in the preflight instructions.",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "C2",
            "target_task": "applied_quadratic_inequality_problem",
            "task_family": "quadratic_inequality_family",
            "problem_type_id": "applied_quadratic_inequality_problem",
            "label": "applied_quadratic_inequality_problem",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "applied_quadratic_inequality_problem"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [
          "C2"
        ],
        "selected_subskill": "applied_quadratic_inequality_problem",
        "selected_problem_type": "applied_quadratic_inequality_problem",
        "candidate_source": "outsider",
        "selected_generator_contract": {
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
              "routing_track",
              "scenario_type",
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
            "applied_quadratic_inequality_problem"
          ]
        },
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
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
        "possible_structure_mismatch": true,
        "possible_mixed_source_context": true
      },
      "subskill_id": "applied_quadratic_inequality_problem",
      "classification_source": "ai_outsider_candidate",
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 4525,
      "detected_problem_type_id": "numeric_evaluate_function_value_fallback_application",
      "example_feature": {
        "source_example_id": 4525,
        "question_text": "(1) 設$A\\left( -3,4 \\right)$、$B\\left( a,1 \\right)$、$C\\left( -4,-2 \\right)$、$D\\left( 2,8 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。\n(2) 設$A\\left( 1,-5 \\right)$、$B\\left( 4,1 \\right)$、$C\\left( -1,x \\right)$、$D\\left( -4,-3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "evaluate_function_value",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "distance_formula_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "C",
          "D",
          "a",
          "x"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "a",
          "x"
        ],
        "target": "evaluate_function_value",
        "classifier_source": "ai_overrode_rule",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 0.9,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目要求利用線段 AB 與線段 CD 平行，以及線段 AB 與線段 CD 垂直的條件，求出未知數 a 與 x 的值。",
            "此題涉及斜率相等與斜率相乘等於 -1 的計算，在提供的候選清單中，C1 (compute_numeric) 作為通用數值計算最為合適。"
          ],
          "ai_rejected_candidates": {
            "C2": "此題並非利用兩點距離公式求未知坐標，而是利用平行與垂直的斜率關係，故排除 C2。",
            "needs_review": "題目清晰可讀，且依合約規定禁止輕易選擇 needs_review。"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "solve_unknown_coordinate_from_two_point_distance",
          "rule_task_family": "distance_between_two_points_family",
          "rule_confidence": 0.55,
          "final_target_task": "evaluate_function_value",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "fallback_application_induct",
          "classification_decision": "",
          "conflict_reason": "rule_family=distance_between_two_points_family; ai_subskill=compute_numeric",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "由於候選清單中沒有專門針對斜率平行或垂直的子技能，故歸類於通用的數值計算 (compute_numeric)。",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "C2",
              "target_task": "solve_unknown_coordinate_from_two_point_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "solve_unknown_coordinate_from_two_point_distance",
              "label": "solve_unknown_coordinate_from_two_point_distance",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
              "generator_contract": {
                "template_variants": [
                  {
                    "id": "direct_distance",
                    "label": "直接求距離",
                    "stem_pattern": "求 {A}({ax},{ay}) 與 {B}({bx},{by}) 的距離。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "missing_coordinate",
                    "label": "反求坐標",
                    "stem_pattern": "已知 {A}({ax},{ay})、{B}({bx},{by}) 與距離 {d}，求未知坐標。",
                    "weight": 0.6,
                    "enabled": true
                  },
                  {
                    "id": "word_context_distance",
                    "label": "語境距離",
                    "stem_pattern": "平面上兩地坐標如下，求兩地距離。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "compare_distance",
                    "label": "比較距離",
                    "stem_pattern": "比較 {A} 到 {B} 與 {A} 到 {C} 的距離大小。",
                    "weight": 0.4,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_names": {
                    "choices": [
                      [
                        "A",
                        "B",
                        "P"
                      ],
                      [
                        "P",
                        "Q",
                        "R"
                      ],
                      [
                        "M",
                        "N",
                        "T"
                      ],
                      [
                        "C",
                        "D",
                        "E"
                      ]
                    ],
                    "randomize": true
                  },
                  "coordinate_range": {
                    "x_min": -10,
                    "x_max": 10,
                    "y_min": -10,
                    "y_max": 10,
                    "exclude_zero_probability": 0.2
                  },
                  "distance_result_type": {
                    "choices": [
                      "integer",
                      "radical"
                    ],
                    "weights": [
                      0.55,
                      0.45
                    ]
                  },
                  "coordinate_delta_pattern": {
                    "choices": [
                      "axis_aligned",
                      "mixed_sign",
                      "general"
                    ],
                    "weights": [
                      0.3,
                      0.4,
                      0.3
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_names",
                  "coordinate_sign_pattern",
                  "distance_result_type",
                  "coordinate_delta_pattern",
                  "ask_target",
                  "context_style"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_distance_only": true
                  },
                  "level_2": {
                    "coordinate_range": [
                      -10,
                      10
                    ],
                    "allow_radical": true
                  },
                  "level_3": {
                    "word_context_enabled": true,
                    "missing_coordinate_enabled": true
                  }
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
                    "routing_track",
                    "scenario_type",
                    "ratio_form",
                    "ratio_values",
                    "coordinate_pattern",
                    "answer"
                  ]
                },
                "validity_constraints": [
                  "A != B",
                  "distance > 0",
                  "if integer answer desired, dx^2+dy^2 must be perfect square",
                  "if radical answer desired, simplify radical form"
                ],
                "answer_shape": "numeric_or_radical",
                "explanation_variants": [
                  "distance_formula",
                  "pythagorean_step"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_names": {
                  "choices": [
                    [
                      "A",
                      "B",
                      "P"
                    ],
                    [
                      "P",
                      "Q",
                      "R"
                    ],
                    [
                      "M",
                      "N",
                      "T"
                    ],
                    [
                      "C",
                      "D",
                      "E"
                    ]
                  ],
                  "randomize": true
                },
                "coordinate_range": {
                  "x_min": -10,
                  "x_max": 10,
                  "y_min": -10,
                  "y_max": 10,
                  "exclude_zero_probability": 0.2
                },
                "distance_result_type": {
                  "choices": [
                    "integer",
                    "radical"
                  ],
                  "weights": [
                    0.55,
                    0.45
                  ]
                },
                "coordinate_delta_pattern": {
                  "choices": [
                    "axis_aligned",
                    "mixed_sign",
                    "general"
                  ],
                  "weights": [
                    0.3,
                    0.4,
                    0.3
                  ]
                }
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [
            "C2"
          ],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "fallback_application",
          "selected_generator_contract": {
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
                "routing_track",
                "scenario_type",
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
              "compute_numeric"
            ]
          },
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
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "distance_formula",
            "parameter",
            "segment_length",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points",
            "unknown_coordinate"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4519,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 1"
            },
            {
              "example_id": 4520,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 2"
            },
            {
              "example_id": 4521,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 3"
            },
            {
              "example_id": 4522,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 4"
            },
            {
              "example_id": 4523,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 5"
            },
            {
              "example_id": 4524,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 6"
            },
            {
              "example_id": 4525,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 7"
            },
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4533,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4534,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4590,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4601,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題4"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "problem_type_id": "numeric_evaluate_function_value_fallback_application",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "requires_human_action": false
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai_overrode_rule",
      "risk_flags": [
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 0.9,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目要求利用線段 AB 與線段 CD 平行，以及線段 AB 與線段 CD 垂直的條件，求出未知數 a 與 x 的值。",
          "此題涉及斜率相等與斜率相乘等於 -1 的計算，在提供的候選清單中，C1 (compute_numeric) 作為通用數值計算最為合適。"
        ],
        "ai_rejected_candidates": {
          "C2": "此題並非利用兩點距離公式求未知坐標，而是利用平行與垂直的斜率關係，故排除 C2。",
          "needs_review": "題目清晰可讀，且依合約規定禁止輕易選擇 needs_review。"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "solve_unknown_coordinate_from_two_point_distance",
        "rule_task_family": "distance_between_two_points_family",
        "rule_confidence": 0.55,
        "final_target_task": "evaluate_function_value",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "fallback_application_induct",
        "classification_decision": "",
        "conflict_reason": "rule_family=distance_between_two_points_family; ai_subskill=compute_numeric",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "由於候選清單中沒有專門針對斜率平行或垂直的子技能，故歸類於通用的數值計算 (compute_numeric)。",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "C2",
            "target_task": "solve_unknown_coordinate_from_two_point_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "solve_unknown_coordinate_from_two_point_distance",
            "label": "solve_unknown_coordinate_from_two_point_distance",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
            "generator_contract": {
              "template_variants": [
                {
                  "id": "direct_distance",
                  "label": "直接求距離",
                  "stem_pattern": "求 {A}({ax},{ay}) 與 {B}({bx},{by}) 的距離。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "missing_coordinate",
                  "label": "反求坐標",
                  "stem_pattern": "已知 {A}({ax},{ay})、{B}({bx},{by}) 與距離 {d}，求未知坐標。",
                  "weight": 0.6,
                  "enabled": true
                },
                {
                  "id": "word_context_distance",
                  "label": "語境距離",
                  "stem_pattern": "平面上兩地坐標如下，求兩地距離。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "compare_distance",
                  "label": "比較距離",
                  "stem_pattern": "比較 {A} 到 {B} 與 {A} 到 {C} 的距離大小。",
                  "weight": 0.4,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_names": {
                  "choices": [
                    [
                      "A",
                      "B",
                      "P"
                    ],
                    [
                      "P",
                      "Q",
                      "R"
                    ],
                    [
                      "M",
                      "N",
                      "T"
                    ],
                    [
                      "C",
                      "D",
                      "E"
                    ]
                  ],
                  "randomize": true
                },
                "coordinate_range": {
                  "x_min": -10,
                  "x_max": 10,
                  "y_min": -10,
                  "y_max": 10,
                  "exclude_zero_probability": 0.2
                },
                "distance_result_type": {
                  "choices": [
                    "integer",
                    "radical"
                  ],
                  "weights": [
                    0.55,
                    0.45
                  ]
                },
                "coordinate_delta_pattern": {
                  "choices": [
                    "axis_aligned",
                    "mixed_sign",
                    "general"
                  ],
                  "weights": [
                    0.3,
                    0.4,
                    0.3
                  ]
                }
              },
              "variation_dimensions": [
                "point_names",
                "coordinate_sign_pattern",
                "distance_result_type",
                "coordinate_delta_pattern",
                "ask_target",
                "context_style"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_distance_only": true
                },
                "level_2": {
                  "coordinate_range": [
                    -10,
                    10
                  ],
                  "allow_radical": true
                },
                "level_3": {
                  "word_context_enabled": true,
                  "missing_coordinate_enabled": true
                }
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
                  "routing_track",
                  "scenario_type",
                  "ratio_form",
                  "ratio_values",
                  "coordinate_pattern",
                  "answer"
                ]
              },
              "validity_constraints": [
                "A != B",
                "distance > 0",
                "if integer answer desired, dx^2+dy^2 must be perfect square",
                "if radical answer desired, simplify radical form"
              ],
              "answer_shape": "numeric_or_radical",
              "explanation_variants": [
                "distance_formula",
                "pythagorean_step"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_names": {
                "choices": [
                  [
                    "A",
                    "B",
                    "P"
                  ],
                  [
                    "P",
                    "Q",
                    "R"
                  ],
                  [
                    "M",
                    "N",
                    "T"
                  ],
                  [
                    "C",
                    "D",
                    "E"
                  ]
                ],
                "randomize": true
              },
              "coordinate_range": {
                "x_min": -10,
                "x_max": 10,
                "y_min": -10,
                "y_max": 10,
                "exclude_zero_probability": 0.2
              },
              "distance_result_type": {
                "choices": [
                  "integer",
                  "radical"
                ],
                "weights": [
                  0.55,
                  0.45
                ]
              },
              "coordinate_delta_pattern": {
                "choices": [
                  "axis_aligned",
                  "mixed_sign",
                  "general"
                ],
                "weights": [
                  0.3,
                  0.4,
                  0.3
                ]
              }
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [
          "C2"
        ],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "fallback_application",
        "selected_generator_contract": {
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
          ]
        },
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
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "distance_formula",
          "parameter",
          "segment_length",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points",
          "unknown_coordinate"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "evaluate_function_value",
      "classification_source": "fallback_application_induct",
      "induction_eligibility": "excluded",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4533,
      "detected_problem_type_id": "numeric_evaluate_function_value_fallback_application",
      "example_feature": {
        "source_example_id": 4533,
        "question_text": "如圖所示$A\\left( -1,4 \\right)$、$B\\left( 2,-1 \\right)$、\n$$、$D\\left( -3,-1 \\right)$、$P\\left( 2,2 \\right)$，\n試求下列直線的斜率。\n(1)直線AP (2)直線BP\n(3)直線CP (4)直線DP。",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "evaluate_function_value",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "D",
          "P"
        ],
        "givens": [
          "A",
          "B",
          "D",
          "P"
        ],
        "target": "evaluate_function_value",
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 0.95,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "題目給定數個點的座標，要求計算直線 AP、BP、CP、DP 的斜率，屬於數值計算。"
          ],
          "ai_rejected_candidates": {
            "needs_review": "雖然題目文字中 C 點座標因格式問題顯示為雙錢字號，但整體題意極為明確，為標準的斜率計算，不需設為 needs_review。"
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "evaluate_function_value",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "fallback_application_induct",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "此題為給定點座標求直線斜率，符合 compute_numeric 的定義。",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "fallback_application",
          "selected_generator_contract": {
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
                "routing_track",
                "scenario_type",
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
              "compute_numeric"
            ]
          },
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
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "unknown",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
        },
        "source_structure_context": {
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習1",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": 1,
          "nearby_worked_examples": [
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4519,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 1"
            },
            {
              "example_id": 4520,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 2"
            },
            {
              "example_id": 4521,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 3"
            },
            {
              "example_id": 4522,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 4"
            },
            {
              "example_id": 4523,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 5"
            },
            {
              "example_id": 4524,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 6"
            },
            {
              "example_id": 4525,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 7"
            },
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4533,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4534,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4590,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4601,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題4"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "problem_type_id": "numeric_evaluate_function_value_fallback_application",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 0.95,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "題目給定數個點的座標，要求計算直線 AP、BP、CP、DP 的斜率，屬於數值計算。"
        ],
        "ai_rejected_candidates": {
          "needs_review": "雖然題目文字中 C 點座標因格式問題顯示為雙錢字號，但整體題意極為明確，為標準的斜率計算，不需設為 needs_review。"
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "evaluate_function_value",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "fallback_application_induct",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "此題為給定點座標求直線斜率，符合 compute_numeric 的定義。",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "fallback_application",
        "selected_generator_contract": {
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
          ]
        },
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
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習1",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "unknown",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "evaluate_function_value",
      "classification_source": "fallback_application_induct",
      "induction_eligibility": "excluded",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 4534,
      "detected_problem_type_id": "numeric_applied_quadratic_inequality_problem_short_answer",
      "example_feature": {
        "source_example_id": 4534,
        "question_text": "若$A\\left( -3,k \\right)$、$$、$C\\left( 3,-2 \\right)$三點無法連結成一個三角形，試求k之值。",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "integer_checker",
        "equivalence": "numeric_exact",
        "math_objects": [
          "coordinate_point",
          "two_coordinate_points"
        ],
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "reasoning_type": [
          "quadratic_factoring_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "C",
          "k"
        ],
        "givens": [
          "A",
          "C",
          "k"
        ],
        "target": "applied_quadratic_inequality_problem",
        "classifier_source": "ai_outsider_candidate",
        "math_meta_tags": [
          "[Task: Applied_Context]"
        ],
        "forced_target_task": "applied_quadratic_inequality_problem",
        "meta_answer_format_hint": "interval",
        "semantic_classification": {
          "ai_target_task": "applied_quadratic_inequality_problem",
          "ai_task_family": "quadratic_inequality_family",
          "ai_confidence": 0.92,
          "ai_best_candidate_id": "C2",
          "ai_evidence": [
            "The Python math meta preflight MANDATORY instruction forces the selection of the candidate with target_task equal to applied_quadratic_inequality_problem.",
            "Candidate C2 matches this forced target task."
          ],
          "ai_rejected_candidates": {
            "C1": "Rejected because C2 is forced by the preflight instruction.",
            "needs_review": "Rejected because C2 is forced by the preflight instruction."
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "applied_quadratic_inequality_problem",
          "rule_task_family": "quadratic_inequality_family",
          "rule_confidence": 0.5,
          "final_target_task": "applied_quadratic_inequality_problem",
          "final_task_family": "quadratic_inequality_family",
          "classifier_source": "ai_outsider_candidate",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
          "requires_human_action": true,
          "ai_notes": "Forced selection of C2 based on the mandatory preflight instruction.",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "C2",
              "target_task": "applied_quadratic_inequality_problem",
              "task_family": "quadratic_inequality_family",
              "problem_type_id": "applied_quadratic_inequality_problem",
              "label": "applied_quadratic_inequality_problem",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "applied_quadratic_inequality_problem"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [
            "C2"
          ],
          "selected_subskill": "applied_quadratic_inequality_problem",
          "selected_problem_type": "applied_quadratic_inequality_problem",
          "candidate_source": "outsider",
          "selected_generator_contract": {
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
                "routing_track",
                "scenario_type",
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
              "applied_quadratic_inequality_problem"
            ]
          },
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
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "applied_quadratic_inequality_problem",
          "task_family": "quadratic_inequality_family",
          "math_objects": [
            "coordinate_point",
            "two_coordinate_points"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習2",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "unknown",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
          "possible_structure_mismatch": true,
          "possible_mixed_source_context": true
        },
        "source_structure_context": {
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習2",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": 2,
          "nearby_worked_examples": [
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4519,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 1"
            },
            {
              "example_id": 4520,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 2"
            },
            {
              "example_id": 4521,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 3"
            },
            {
              "example_id": 4522,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 4"
            },
            {
              "example_id": 4523,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 5"
            },
            {
              "example_id": 4524,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 6"
            },
            {
              "example_id": 4525,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 7"
            },
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4533,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4534,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4590,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4601,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題4"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai_outsider_candidate",
      "risk_flags": [
        "outsider_candidate_within_confirmed_skill",
        "requires_human_action"
      ],
      "semantic_classification": {
        "ai_target_task": "applied_quadratic_inequality_problem",
        "ai_task_family": "quadratic_inequality_family",
        "ai_confidence": 0.92,
        "ai_best_candidate_id": "C2",
        "ai_evidence": [
          "The Python math meta preflight MANDATORY instruction forces the selection of the candidate with target_task equal to applied_quadratic_inequality_problem.",
          "Candidate C2 matches this forced target task."
        ],
        "ai_rejected_candidates": {
          "C1": "Rejected because C2 is forced by the preflight instruction.",
          "needs_review": "Rejected because C2 is forced by the preflight instruction."
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "applied_quadratic_inequality_problem",
        "rule_task_family": "quadratic_inequality_family",
        "rule_confidence": 0.5,
        "final_target_task": "applied_quadratic_inequality_problem",
        "final_task_family": "quadratic_inequality_family",
        "classifier_source": "ai_outsider_candidate",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "outsider_candidate_within_confirmed_skill",
        "requires_human_action": true,
        "ai_notes": "Forced selection of C2 based on the mandatory preflight instruction.",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "C2",
            "target_task": "applied_quadratic_inequality_problem",
            "task_family": "quadratic_inequality_family",
            "problem_type_id": "applied_quadratic_inequality_problem",
            "label": "applied_quadratic_inequality_problem",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "applied_quadratic_inequality_problem"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [
          "C2"
        ],
        "selected_subskill": "applied_quadratic_inequality_problem",
        "selected_problem_type": "applied_quadratic_inequality_problem",
        "candidate_source": "outsider",
        "selected_generator_contract": {
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
              "routing_track",
              "scenario_type",
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
            "applied_quadratic_inequality_problem"
          ]
        },
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
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "applied_quadratic_inequality_problem",
        "task_family": "quadratic_inequality_family",
        "math_objects": [
          "coordinate_point",
          "two_coordinate_points"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習2",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "unknown",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "possible_structure_mismatch_penalty; sequence_context_used",
        "possible_structure_mismatch": true,
        "possible_mixed_source_context": true
      },
      "subskill_id": "applied_quadratic_inequality_problem",
      "classification_source": "ai_outsider_candidate",
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker"
    },
    {
      "example_id": 4590,
      "detected_problem_type_id": "numeric_evaluate_function_value_fallback_application",
      "example_feature": {
        "source_example_id": 4590,
        "question_text": "在坐標平面上，若直線L通過兩點$A\\left( 2,a \\right)$、$B\\left( a,8 \\right)$，且直線L的斜率為2，則a = (A) −2 (B) 1 (C) 2 (D) 4。",
        "answer": "A",
        "choices": [
          "−2",
          "1",
          "2",
          "4。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "coordinate_point",
          "two_coordinate_points"
        ],
        "target_task": "evaluate_function_value",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "C",
          "D",
          "a"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "a"
        ],
        "target": "evaluate_function_value",
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "The question asks to find the value of a given two points A(2, a) and B(a, 8) on line L with slope 2.",
            "This is a numeric computation task based on the definition of the slope of a line.",
            "The candidate C1 (compute_numeric) is the only valid non-needs_review candidate provided."
          ],
          "ai_rejected_candidates": {
            "needs_review": "The stem is perfectly readable and aligned with the skill of finding the slope of a line, so needs_review is rejected."
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "evaluate_function_value",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "fallback_application_induct",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "The problem requires solving for the parameter a using the slope formula (8 - a) / (a - 2) = 2, which is a numeric computation task.",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "fallback_application",
          "selected_generator_contract": {
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
                "routing_track",
                "scenario_type",
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
              "compute_numeric"
            ]
          },
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
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "two_coordinate_points"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4519,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 1"
            },
            {
              "example_id": 4520,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 2"
            },
            {
              "example_id": 4521,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 3"
            },
            {
              "example_id": 4522,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 4"
            },
            {
              "example_id": 4523,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 5"
            },
            {
              "example_id": 4524,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 6"
            },
            {
              "example_id": 4525,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 7"
            },
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4533,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4534,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4590,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4601,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題4"
            }
          ]
        },
        "correct_answer": "A",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "problem_type_id": "numeric_evaluate_function_value_fallback_application",
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "stem_embeds_choices",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "The question asks to find the value of a given two points A(2, a) and B(a, 8) on line L with slope 2.",
          "This is a numeric computation task based on the definition of the slope of a line.",
          "The candidate C1 (compute_numeric) is the only valid non-needs_review candidate provided."
        ],
        "ai_rejected_candidates": {
          "needs_review": "The stem is perfectly readable and aligned with the skill of finding the slope of a line, so needs_review is rejected."
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "evaluate_function_value",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "fallback_application_induct",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "The problem requires solving for the parameter a using the slope formula (8 - a) / (a - 2) = 2, which is a numeric computation task.",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "fallback_application",
        "selected_generator_contract": {
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
          ]
        },
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
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "two_coordinate_points"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "evaluate_function_value",
      "classification_source": "fallback_application_induct",
      "induction_eligibility": "excluded",
      "answer_type": "integer",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker"
    },
    {
      "example_id": 4601,
      "detected_problem_type_id": "numeric_evaluate_function_value_fallback_application",
      "example_feature": {
        "source_example_id": 4601,
        "question_text": "設$P\\left( 4,2 \\right)$、$Q\\left( 0,a \\right)$、$B\\left( -1,0 \\right)R\\left( 8,-2 \\right)$為共線之三點，則a = (A) 5 (B) 6 (C) 7 (D) 8。",
        "answer": "A",
        "choices": [
          "5",
          "6",
          "7",
          "8。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "integer",
        "answer_shape": "numeric",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "evaluate_function_value",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "Q",
          "R",
          "a"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "Q",
          "R",
          "a"
        ],
        "target": "evaluate_function_value",
        "classifier_source": "ai",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "compute_numeric",
          "ai_task_family": "generic_numeric_family",
          "ai_confidence": 1.0,
          "ai_best_candidate_id": "C1",
          "ai_evidence": [
            "The problem asks to find the value of 'a' given that three points are collinear, which is solved by setting the slope of PQ equal to the slope of PR.",
            "Since C1 (compute_numeric) is the only non-review candidate provided, and the stem is readable, C1 is the correct choice."
          ],
          "ai_rejected_candidates": {
            "needs_review": "The stem is readable and represents a standard collinearity problem using slopes, so needs_review is rejected."
          },
          "ai_available": true,
          "ai_error": "",
          "ai_unavailable_reason": "",
          "ai_semantic_status": "ok",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "evaluate_function_value",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "fallback_application_induct",
          "classification_decision": "",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "The text contains a minor typo 'B(-1,0)R(8,-2)' but the mathematical intent of collinear points P, Q, and R is clear and solvable.",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_numeric",
              "task_family": "generic_numeric_family",
              "problem_type_id": "compute_numeric",
              "label": "compute_numeric",
              "candidate_source": "structure",
              "in_anchor_scope": false,
              "answer_type": "numeric",
              "answer_shape": "numeric",
              "math_objects": [],
              "checker_key": "numeric_checker",
              "equivalence_type": "numeric_equivalence",
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
                    "routing_track",
                    "scenario_type",
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
                  "compute_numeric"
                ]
              },
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
              }
            },
            {
              "candidate_id": "needs_review",
              "target_task": "",
              "task_family": "",
              "problem_type_id": "needs_review",
              "label": "needs_review",
              "candidate_source": "needs_review",
              "in_anchor_scope": false,
              "answer_type": "",
              "answer_shape": "",
              "math_objects": [],
              "checker_key": "manual_review_checker",
              "equivalence_type": "manual_review_or_ai_judged",
              "generator_contract": {},
              "parameter_schema": {}
            }
          ],
          "outsider_candidates": [],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "fallback_application",
          "selected_generator_contract": {
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
                "routing_track",
                "scenario_type",
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
              "compute_numeric"
            ]
          },
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
          "variable_randomization_notes": [],
          "checker_key": "numeric_checker",
          "equivalence_type": "numeric_equivalence",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "linked_example_id": null,
          "linked_example_task_family": "",
          "structure_consistency": "not_applicable",
          "sequence_context_used": true,
          "structure_context_used": true,
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
        },
        "source_structure_context": {
          "source_type": "unknown",
          "example_label": "",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4519,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 1"
            },
            {
              "example_id": 4520,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 2"
            },
            {
              "example_id": 4521,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 3"
            },
            {
              "example_id": 4522,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 4"
            },
            {
              "example_id": 4523,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 5"
            },
            {
              "example_id": 4524,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 6"
            },
            {
              "example_id": 4525,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-1習題 基礎題 7"
            },
            {
              "example_id": 4529,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4533,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4534,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4590,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題2"
            },
            {
              "example_id": 4601,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題4"
            }
          ]
        },
        "correct_answer": "A",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "problem_type_id": "numeric_evaluate_function_value_fallback_application",
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker"
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "ai",
      "risk_flags": [
        "stem_embeds_choices",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "compute_numeric",
        "ai_task_family": "generic_numeric_family",
        "ai_confidence": 1.0,
        "ai_best_candidate_id": "C1",
        "ai_evidence": [
          "The problem asks to find the value of 'a' given that three points are collinear, which is solved by setting the slope of PQ equal to the slope of PR.",
          "Since C1 (compute_numeric) is the only non-review candidate provided, and the stem is readable, C1 is the correct choice."
        ],
        "ai_rejected_candidates": {
          "needs_review": "The stem is readable and represents a standard collinearity problem using slopes, so needs_review is rejected."
        },
        "ai_available": true,
        "ai_error": "",
        "ai_unavailable_reason": "",
        "ai_semantic_status": "ok",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "evaluate_function_value",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "fallback_application_induct",
        "classification_decision": "",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "The text contains a minor typo 'B(-1,0)R(8,-2)' but the mathematical intent of collinear points P, Q, and R is clear and solvable.",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_numeric",
            "task_family": "generic_numeric_family",
            "problem_type_id": "compute_numeric",
            "label": "compute_numeric",
            "candidate_source": "structure",
            "in_anchor_scope": false,
            "answer_type": "numeric",
            "answer_shape": "numeric",
            "math_objects": [],
            "checker_key": "numeric_checker",
            "equivalence_type": "numeric_equivalence",
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
                  "routing_track",
                  "scenario_type",
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
                "compute_numeric"
              ]
            },
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
            }
          },
          {
            "candidate_id": "needs_review",
            "target_task": "",
            "task_family": "",
            "problem_type_id": "needs_review",
            "label": "needs_review",
            "candidate_source": "needs_review",
            "in_anchor_scope": false,
            "answer_type": "",
            "answer_shape": "",
            "math_objects": [],
            "checker_key": "manual_review_checker",
            "equivalence_type": "manual_review_or_ai_judged",
            "generator_contract": {},
            "parameter_schema": {}
          }
        ],
        "outsider_candidates": [],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "fallback_application",
        "selected_generator_contract": {
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
              "routing_track",
              "scenario_type",
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
            "compute_numeric"
          ]
        },
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
        "variable_randomization_notes": [],
        "checker_key": "numeric_checker",
        "equivalence_type": "numeric_equivalence",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
        "source_type": "unknown",
        "example_label": "",
        "practice_label": "",
        "linked_example": "",
        "linked_example_id": null,
        "linked_example_task_family": "",
        "structure_consistency": "not_applicable",
        "sequence_context_used": true,
        "structure_context_used": true,
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "evaluate_function_value",
      "classification_source": "fallback_application_induct",
      "induction_eligibility": "excluded",
      "answer_type": "integer",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker"
    }
  ],
  "split_or_merge_recommendation": "induced_from_source_features",
  "classifier_gate": {
    "status": "classifier_auto_pending_promote_with_warning",
    "allowed": true,
    "warnings": [
      "insufficient_examples",
      "alignment_score_below_recommended_threshold",
      "majority_sources_need_human_subskill_review",
      "skill_scoped_classification_low_confidence",
      "source_skill_scope_locked_demoted_blockers_to_warnings"
    ]
  },
  "generator_draft_gate": {
    "status": "generator_draft_allowed_with_low_source_warning",
    "allowed": true,
    "warnings": [
      "low_source_examples",
      "alignment_score_below_recommended_threshold",
      "majority_sources_need_human_subskill_review",
      "skill_scoped_classification_low_confidence",
      "source_skill_scope_locked_demoted_blockers_to_warnings"
    ]
  },
  "runtime_ready_gate": {
    "status": "blocked_insufficient_examples",
    "allowed": false,
    "blockers": [
      "runtime_smoke_failed",
      "dynamic_sampling_failed"
    ],
    "warnings": [
      "alignment_score_below_recommended_threshold",
      "majority_sources_need_human_subskill_review",
      "skill_scoped_classification_low_confidence",
      "source_skill_scope_locked_demoted_blockers_to_warnings"
    ]
  },
  "exception_review_gate": {
    "required": false,
    "reasons": []
  },
  "self_healing_log": [
    {
      "status": "HEALED_AND_RETRIED",
      "phase": "phase3",
      "skill_id": "vh_數學B1_SlopeOfALine"
    }
  ],
  "reports": {
    "auto_pipeline_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_SlopeOfALine_auto_pipeline_summary.json",
    "auto_pipeline_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_SlopeOfALine_auto_pipeline_summary.md",
    "phase1_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_SlopeOfALine_phase1_summary.json",
    "phase1_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_SlopeOfALine_phase1_summary.md",
    "phase1_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_SlopeOfALine_phase1_summary.json",
    "phase1_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_SlopeOfALine_phase1_summary.md",
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_SlopeOfALine_phase2_generator_summary.json",
    "phase2_generator_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_SlopeOfALine_phase2_generator_summary.md",
    "phase2_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_SlopeOfALine_phase2_generator_summary.json",
    "phase2_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_SlopeOfALine_phase2_generator_summary.md",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_SlopeOfALine_generator_draft_spec.json"
  },
  "next_action": "manual_review_before_runtime_enable",
  "timestamp": "2026-06-14T09:06:02.293732+00:00",
  "dry_run": true
}
```
