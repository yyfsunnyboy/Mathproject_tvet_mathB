# Gencode Auto Pipeline Summary: vh_數學B1_PropertiesOfParallelLines

## summary
```json
{
  "ok": false,
  "skill_id": "vh_數學B1_PropertiesOfParallelLines",
  "pipeline_status": "auto_pipeline_completed_runtime_blocked",
  "source_example_count": 4,
  "candidate_problem_types": [
    {
      "problem_type_id": "text_short_compute_distance_between_two_points",
      "proposed_problem_type_id": "text_short_compute_distance_between_two_points",
      "display_name": "text_short / compute_distance_between_two_points",
      "matched_example_ids": [
        4530,
        4535
      ],
      "matched_example_count": 2,
      "unmatched_example_ids": [],
      "representative_example_id": 4530,
      "structural_features": [
        "scalar"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "text_short",
        "answer_shape": "scalar",
        "answer_equivalence": "exact_string",
        "checker": "text_short_checker",
        "accepted_formats": [
          "5",
          "5.0",
          "\\sqrt{13}",
          "sqrt(13)",
          "2\\sqrt{5}",
          "2√5"
        ],
        "checker_key": "text_short_checker",
        "equivalence_type": "exact_string",
        "selected_checker": "expression_equivalence_checker",
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "distance_formula",
            "segment_length",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "required_math_objects": [
            "coordinate_point",
            "distance_formula"
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
          "sampling_strategy": "weighted_random",
          "template_families": [
            "compute_distance_between_two_points"
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
            "stem": "point_quadrant"
          },
          "problem_type_id": "fallback_compute_distance_between_two_points_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": []
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
        "canonical_answer_schema": "numeric_or_radical",
        "presentation_mode": ""
      },
      "checker_key_proposal": "text_short_checker",
      "equivalence_type_proposal": "exact_string",
      "answer_shape": "scalar",
      "answer_semantics": "scalar",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "expression_equivalence_checker",
      "checker_selection_reason": "task_family_default",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "ai_first_mode_fell_back_to_rule_only",
        "ai_unavailable_fallback_to_same_as_main",
        "alignment_score_below_recommended_threshold",
        "majority_sources_need_human_subskill_review",
        "skill_scoped_classification_low_confidence",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "short_answer",
        "compute_distance_between_two_points",
        "short_answer",
        [
          "distance_formula_reasoning"
        ],
        [
          "coordinate_point",
          "distance_formula"
        ]
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "fallback_compute_distance_between_two_points_2",
        "skill_id": "vh_數學B1_PropertiesOfParallelLines",
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "display_name": "兩點距離計算",
        "answer_format_hint": "",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          4530,
          4535
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "expression",
          "answer_shape": "scalar",
          "answer_equivalence": "algebraic_equivalent",
          "checker": "expression_checker",
          "accepted_formats": [
            "5",
            "5.0",
            "\\sqrt{13}",
            "sqrt(13)",
            "2\\sqrt{5}",
            "2√5"
          ],
          "equivalence_type": "algebraic_equivalent",
          "checker_key": "expression_checker"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "distance_formula",
            "segment_length",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "required_math_objects": [
            "coordinate_point",
            "distance_formula"
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
          "sampling_strategy": "weighted_random",
          "template_families": [
            "compute_distance_between_two_points"
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
            "stem": "point_quadrant"
          },
          "problem_type_id": "fallback_compute_distance_between_two_points_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": []
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
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "short_answer",
          "compute_distance_between_two_points",
          "short_answer",
          [
            "distance_formula_reasoning"
          ],
          [
            "coordinate_point",
            "distance_formula"
          ]
        ],
        "canonical_base_problem_type_id": "fallback_compute_distance_between_two_points_2",
        "value_type_prefix": "",
        "_resolved_template_slot": "two_point_distance_compute"
      },
      "generator_readiness": "runtime_ready",
      "usable_for_phase3": true,
      "template_slot": "point_quadrant",
      "canonical_base_problem_type_id": "fallback_compute_distance_between_two_points_2",
      "value_type_prefix": "",
      "subskill_id": "compute_distance_between_two_points",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.025,
        "task_consistent_with_skill": true
      },
      "answer_type": "expression"
    },
    {
      "problem_type_id": "choice_contextual_application",
      "proposed_problem_type_id": "choice_contextual_application",
      "display_name": "choice / contextual_application",
      "matched_example_ids": [
        4600,
        4602
      ],
      "matched_example_count": 2,
      "unmatched_example_ids": [],
      "representative_example_id": 4600,
      "structural_features": [
        "single_choice"
      ],
      "answer_contract_proposal": {
        "choices_required": true,
        "choice_count": 4,
        "correct_choice_count": 1,
        "frontend_render_choices": true,
        "answer_type": "choice",
        "answer_shape": "single_choice",
        "answer_semantics": "choice_label",
        "answer_equivalence": "choice_label",
        "checker": "choice_label_checker",
        "presentation_mode": "",
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
            "contextual_application"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": true
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "contextual_application": true,
          "template_slots": {
            "stem": "linear_function_contextual_word_problem"
          },
          "problem_type_id": "skill_scoped_unresolved_problem_type_2",
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
        "ai_first_mode_fell_back_to_rule_only",
        "ai_unavailable_fallback_to_same_as_main",
        "alignment_score_below_recommended_threshold",
        "majority_sources_need_human_subskill_review",
        "skill_scoped_classification_low_confidence",
        "source_skill_scope_locked_demoted_blockers_to_warnings"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "single_choice",
        "contextual_application",
        "single_choice",
        [
          "numeric_computation"
        ],
        [
          "coordinate_point",
          "three_coordinate_points"
        ]
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "skill_scoped_unresolved_problem_type_2",
        "skill_id": "vh_數學B1_PropertiesOfParallelLines",
        "target_task": "contextual_application",
        "task_family": "generic_numeric_family",
        "display_name": "single_choice / contextual_application",
        "answer_format_hint": "A/B/C/D",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          4600,
          4602
        ],
        "answer_contract": {
          "choices_required": true,
          "choice_count": 4,
          "correct_choice_count": 1,
          "frontend_render_choices": true,
          "answer_type": "choice",
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
          "checker_key": "choice_label_checker"
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
            "contextual_application"
          ],
          "parameter_slots": {
            "seed": "integer",
            "difficulty": "easy"
          },
          "randomization_rules": {
            "shuffle_choices": true
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "contextual_application": true,
          "template_slots": {
            "stem": "linear_function_contextual_word_problem"
          },
          "problem_type_id": "skill_scoped_unresolved_problem_type_2",
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
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "single_choice",
          "contextual_application",
          "single_choice",
          [
            "numeric_computation"
          ],
          [
            "coordinate_point",
            "three_coordinate_points"
          ]
        ],
        "canonical_base_problem_type_id": "skill_scoped_unresolved_problem_type_2",
        "value_type_prefix": "",
        "_resolved_template_slot": "linear_function_contextual_word_problem"
      },
      "generator_readiness": "pending_problem_type_induction",
      "usable_for_phase3": false,
      "template_slot": "linear_function_contextual_word_problem",
      "canonical_base_problem_type_id": "skill_scoped_unresolved_problem_type_2",
      "value_type_prefix": "",
      "subskill_id": "contextual_application",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0526,
        "task_consistent_with_skill": true
      },
      "answer_type": "choice"
    }
  ],
  "per_example_classification": [
    {
      "example_id": 4530,
      "detected_problem_type_id": "fallback_compute_distance_between_two_points_2",
      "example_feature": {
        "source_example_id": 4530,
        "question_text": "設$A\\left( 2,0 \\right)$、$B\\left( -3,5 \\right)$、$C\\left( -1,-1 \\right)$、$D\\left( 4,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "distance_formula",
          "segment_length",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
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
          "x"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "x"
        ],
        "target": "compute_distance_between_two_points",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_distance_between_two_points",
          "rule_task_family": "distance_between_two_points_family",
          "rule_confidence": 0.55,
          "final_target_task": "compute_distance_between_two_points",
          "final_task_family": "distance_between_two_points_family",
          "classifier_source": "clause45_unclassified_exception",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_distance_between_two_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_distance_between_two_points",
              "label": "compute_distance_between_two_points",
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
            "C1"
          ],
          "selected_subskill": "compute_distance_between_two_points",
          "selected_problem_type": "compute_distance_between_two_points",
          "candidate_source": "clause45_fallback_proxy",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_distance_between_two_points",
          "task_family": "distance_between_two_points_family",
          "math_objects": [
            "coordinate_point",
            "distance_formula",
            "segment_length",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "worked_example",
          "example_label": "例題3",
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
          "example_label": "例題3",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": 3,
          "practice_number": null,
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4530,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4535,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4600,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            },
            {
              "example_id": 4602,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題5"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "problem_type_id": "fallback_compute_distance_between_two_points",
        "proxy_problem_type_id": "fallback_compute_distance_between_two_points",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "requires_human_action": false
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_distance_between_two_points",
        "rule_task_family": "distance_between_two_points_family",
        "rule_confidence": 0.55,
        "final_target_task": "compute_distance_between_two_points",
        "final_task_family": "distance_between_two_points_family",
        "classifier_source": "clause45_unclassified_exception",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_distance_between_two_points",
            "label": "compute_distance_between_two_points",
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
          "C1"
        ],
        "selected_subskill": "compute_distance_between_two_points",
        "selected_problem_type": "compute_distance_between_two_points",
        "candidate_source": "clause45_fallback_proxy",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "math_objects": [
          "coordinate_point",
          "distance_formula",
          "segment_length",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "worked_example",
        "example_label": "例題3",
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
      "subskill_id": "compute_distance_between_two_points",
      "classification_source": "clause45_unclassified_exception",
      "induction_eligibility": "excluded",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4535,
      "detected_problem_type_id": "fallback_compute_distance_between_two_points_2",
      "example_feature": {
        "source_example_id": 4535,
        "question_text": "設$A\\left( 1,-5 \\right)$、$B\\left( 4,1 \\right)$、$C\\left( -1,x \\right)$、$D\\left( -4,-3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "distance_formula",
          "segment_length",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
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
          "x"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "x"
        ],
        "target": "compute_distance_between_two_points",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_distance_between_two_points",
          "rule_task_family": "distance_between_two_points_family",
          "rule_confidence": 0.55,
          "final_target_task": "compute_distance_between_two_points",
          "final_task_family": "distance_between_two_points_family",
          "classifier_source": "clause45_unclassified_exception",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_distance_between_two_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_distance_between_two_points",
              "label": "compute_distance_between_two_points",
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
          "outsider_candidates": [],
          "selected_subskill": "compute_distance_between_two_points",
          "selected_problem_type": "compute_distance_between_two_points",
          "candidate_source": "clause45_fallback_proxy",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_distance_between_two_points",
          "task_family": "distance_between_two_points_family",
          "math_objects": [
            "coordinate_point",
            "distance_formula",
            "segment_length",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習3",
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
          "practice_label": "隨堂練習3",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": 3,
          "nearby_worked_examples": [
            {
              "example_id": 4530,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4530,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4535,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4600,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            },
            {
              "example_id": 4602,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題5"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "problem_type_id": "fallback_compute_distance_between_two_points",
        "proxy_problem_type_id": "fallback_compute_distance_between_two_points",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "requires_human_action": false
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_distance_between_two_points",
        "rule_task_family": "distance_between_two_points_family",
        "rule_confidence": 0.55,
        "final_target_task": "compute_distance_between_two_points",
        "final_task_family": "distance_between_two_points_family",
        "classifier_source": "clause45_unclassified_exception",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_distance_between_two_points",
            "label": "compute_distance_between_two_points",
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
        "outsider_candidates": [],
        "selected_subskill": "compute_distance_between_two_points",
        "selected_problem_type": "compute_distance_between_two_points",
        "candidate_source": "clause45_fallback_proxy",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "math_objects": [
          "coordinate_point",
          "distance_formula",
          "segment_length",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習3",
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
      "subskill_id": "compute_distance_between_two_points",
      "classification_source": "clause45_unclassified_exception",
      "induction_eligibility": "excluded",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4600,
      "detected_problem_type_id": "skill_scoped_unresolved_problem_type_2",
      "example_feature": {
        "source_example_id": 4600,
        "question_text": "已知平面上四點$A\\left( 1,3 \\right)$、$B\\left( 2,5 \\right)$、$C\\left( 3,1 \\right)$、$D\\left( 5,x \\right)$。若直線AB與直線CD平行，則x = (A) 3 (B) 4 (C) 5 (D) 6。",
        "answer": "A",
        "choices": [
          "3",
          "4",
          "5",
          "6。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "contextual_application",
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
          "x"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "x"
        ],
        "target": "contextual_application",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "contextual_application",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "clause45_unclassified_exception",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_distance_between_two_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_distance_between_two_points",
              "label": "compute_distance_between_two_points",
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
              "candidate_id": "C2",
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
            "C2"
          ],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "clause45_fallback_proxy",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "single_choice",
          "answer_shape": "single_choice",
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
          "possible_mixed_source_context": true,
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
              "example_id": 4530,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4530,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4535,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4600,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            },
            {
              "example_id": 4602,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題5"
            }
          ]
        },
        "correct_answer": "A",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "needs_rule_pack_or_slot_registration": true,
        "problem_type_id": "skill_scoped_unresolved_problem_type",
        "proxy_problem_type_id": "skill_scoped_unresolved_problem_type",
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker",
        "requires_human_action": false
      },
      "answer_shape": "single_choice",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "stem_embeds_choices",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "contextual_application",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "clause45_unclassified_exception",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_distance_between_two_points",
            "label": "compute_distance_between_two_points",
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
            "candidate_id": "C2",
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
          "C2"
        ],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "clause45_fallback_proxy",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
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
        "possible_mixed_source_context": true,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "contextual_application",
      "classification_source": "clause45_unclassified_exception",
      "induction_eligibility": "excluded",
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4602,
      "detected_problem_type_id": "skill_scoped_unresolved_problem_type_2",
      "example_feature": {
        "source_example_id": 4602,
        "question_text": "平面上過兩點$\\left( 1,3 \\right)$、$\\left( 3,5 \\right)$的直線和過另兩點$\\left( 2,0 \\right)$、$\\left( 3,a \\right)$的直線平行，則a = (A) 1 (B) 2 (C) 3 (D) 4。",
        "answer": "A",
        "choices": [
          "1",
          "2",
          "3",
          "4。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "contextual_application",
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
        "target": "contextual_application",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "ai_best_candidate_id": "needs_review",
          "ai_evidence": [],
          "ai_rejected_candidates": {},
          "ai_available": false,
          "ai_error": "ai_api_key_missing",
          "ai_unavailable_reason": "missing_api_key",
          "ai_semantic_status": "unavailable",
          "ai_invalid_response_reason": "",
          "parser_error": "",
          "raw_response_preview": "",
          "sanitized_response_preview": "",
          "failed_stage": "",
          "rule_target_task": "compute_numeric",
          "rule_task_family": "generic_numeric_family",
          "rule_confidence": 0.2,
          "final_target_task": "contextual_application",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "clause45_unclassified_exception",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compute_distance_between_two_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_distance_between_two_points",
              "label": "compute_distance_between_two_points",
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
              "candidate_id": "C2",
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
            "C2"
          ],
          "selected_subskill": "compute_numeric",
          "selected_problem_type": "compute_numeric",
          "candidate_source": "clause45_fallback_proxy",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [
            "coordinate_point",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "single_choice",
          "answer_shape": "single_choice",
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
          "possible_mixed_source_context": true,
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
              "example_id": 4530,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4530,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4535,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4600,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題3"
            },
            {
              "example_id": 4602,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題5"
            }
          ]
        },
        "correct_answer": "A",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "needs_rule_pack_or_slot_registration": true,
        "problem_type_id": "skill_scoped_unresolved_problem_type",
        "proxy_problem_type_id": "skill_scoped_unresolved_problem_type",
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker",
        "requires_human_action": false
      },
      "answer_shape": "single_choice",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "stem_embeds_choices",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "ai_best_candidate_id": "needs_review",
        "ai_evidence": [],
        "ai_rejected_candidates": {},
        "ai_available": false,
        "ai_error": "ai_api_key_missing",
        "ai_unavailable_reason": "missing_api_key",
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "parser_error": "",
        "raw_response_preview": "",
        "sanitized_response_preview": "",
        "failed_stage": "",
        "rule_target_task": "compute_numeric",
        "rule_task_family": "generic_numeric_family",
        "rule_confidence": 0.2,
        "final_target_task": "contextual_application",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "clause45_unclassified_exception",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compute_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_distance_between_two_points",
            "label": "compute_distance_between_two_points",
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
            "candidate_id": "C2",
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
          "C2"
        ],
        "selected_subskill": "compute_numeric",
        "selected_problem_type": "compute_numeric",
        "candidate_source": "clause45_fallback_proxy",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [
          "coordinate_point",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
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
        "possible_mixed_source_context": true,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "contextual_application",
      "classification_source": "clause45_unclassified_exception",
      "induction_eligibility": "excluded",
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker",
      "requires_human_action": false
    }
  ],
  "split_or_merge_recommendation": "induced_from_source_features",
  "classifier_gate": {
    "status": "classifier_auto_pending_promote_with_warning",
    "allowed": true,
    "warnings": [
      "insufficient_examples",
      "ai_first_mode_fell_back_to_rule_only",
      "ai_unavailable_fallback_to_same_as_main",
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
      "ai_first_mode_fell_back_to_rule_only",
      "ai_unavailable_fallback_to_same_as_main",
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
      "ai_first_mode_fell_back_to_rule_only",
      "ai_unavailable_fallback_to_same_as_main",
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
      "phase": "phase2",
      "skill_id": "vh_數學B1_PropertiesOfParallelLines"
    }
  ],
  "reports": {
    "auto_pipeline_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfParallelLines_auto_pipeline_summary.json",
    "auto_pipeline_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfParallelLines_auto_pipeline_summary.md",
    "phase1_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfParallelLines_phase1_summary.json",
    "phase1_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfParallelLines_phase1_summary.md",
    "phase1_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfParallelLines_phase1_summary.json",
    "phase1_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PropertiesOfParallelLines_phase1_summary.md"
  },
  "next_action": "manual_review_before_runtime_enable",
  "timestamp": "2026-06-14T14:24:15.519709+00:00",
  "dry_run": true
}
```
