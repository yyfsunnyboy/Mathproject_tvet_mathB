# Gencode Auto Pipeline Summary: vh_數學B1_DistanceBetweenTwoPointsInPlane

## summary
```json
{
  "ok": false,
  "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
  "pipeline_status": "auto_pipeline_completed_runtime_blocked",
  "source_example_count": 4,
  "candidate_problem_types": [
    {
      "problem_type_id": "integer_solve_unknown_coordinate_from_two_point_distance",
      "proposed_problem_type_id": "integer_solve_unknown_coordinate_from_two_point_distance",
      "display_name": "integer / solve_unknown_coordinate_from_two_point_distance",
      "matched_example_ids": [
        4419,
        4432,
        4437
      ],
      "matched_example_count": 3,
      "unmatched_example_ids": [],
      "representative_example_id": 4419,
      "structural_features": [
        "unordered_set"
      ],
      "answer_contract_proposal": {
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
        "source_has_choices": false,
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "presentation_mode": "",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "solution_set"
      },
      "checker_key_proposal": "integer_checker",
      "equivalence_type_proposal": "numeric_exact",
      "answer_shape": "unordered_set",
      "answer_semantics": "unordered_set",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "solution_set_checker",
      "checker_selection_reason": "task_family_default",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "numeric",
        "solve_unknown_coordinate_from_two_point_distance",
        "short_answer",
        [
          "distance_formula_reasoning"
        ],
        [
          "coordinate_point",
          "distance_formula"
        ],
        "default"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "integer_solve_unknown_coordinate_from_two_point_distance_expression",
        "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
        "target_task": "solve_unknown_coordinate_from_two_point_distance",
        "task_family": "distance_between_two_points_family",
        "display_name": "numeric / solve_unknown_coordinate_from_two_point_distance",
        "answer_format_hint": "solution_set",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          4419,
          4432,
          4437
        ],
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
          "source_has_choices": false,
          "equivalence_type": "numeric_exact",
          "checker_key": "integer_checker",
          "presentation_mode": "short_answer"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "distance_formula",
            "parameter",
            "segment_length",
            "two_coordinate_points",
            "unknown_coordinate"
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
            "context_style",
            "number_variation",
            "template_variant",
            "coordinate_sign_combination",
            "slope_type"
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
            "solve_unknown_coordinate_from_two_point_distance"
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
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "numeric_solve_unknown_coordinate_from_two_point_distance_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [],
          "template_slots": {
            "stem": "two_point_distance_solution_set"
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
          "solve_unknown_coordinate_from_two_point_distance",
          "short_answer",
          [
            "distance_formula_reasoning"
          ],
          [
            "coordinate_point",
            "distance_formula"
          ],
          "default"
        ],
        "canonical_base_problem_type_id": "solve_unknown_coordinate_from_two_point_distance_short_answer",
        "value_type_prefix": "numeric",
        "_resolved_template_slot": "two_point_distance_solution_set",
        "naming_warning": "naming_warning:numeric_prefix_but_hint_is_solution_set"
      },
      "generator_readiness": "runtime_ready",
      "usable_for_phase3": true,
      "template_slot": "two_point_distance_solution_set",
      "canonical_base_problem_type_id": "solve_unknown_coordinate_from_two_point_distance_short_answer",
      "value_type_prefix": "numeric",
      "subskill_id": "solve_unknown_coordinate_from_two_point_distance",
      "answer_type": "integer",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.075,
        "source_problem_type_score": 0.0488,
        "task_consistent_with_skill": true
      }
    },
    {
      "problem_type_id": "integer_compute_distance_between_two_points",
      "proposed_problem_type_id": "integer_compute_distance_between_two_points",
      "display_name": "integer / compute_distance_between_two_points",
      "matched_example_ids": [
        4436
      ],
      "matched_example_count": 1,
      "unmatched_example_ids": [],
      "representative_example_id": 4436,
      "structural_features": [
        "text_short"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "integer",
        "answer_shape": "text_short",
        "answer_equivalence": "numeric_exact",
        "checker": "integer_checker",
        "accepted_formats": [
          "5",
          "5.0",
          "\\sqrt{13}",
          "sqrt(13)",
          "2\\sqrt{5}",
          "2√5"
        ],
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "presentation_mode": "",
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
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "numeric",
        "compute_distance_between_two_points",
        "short_answer",
        [
          "distance_formula_reasoning"
        ],
        [
          "coordinate_point",
          "distance_formula"
        ],
        "default"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "text_short_compute_distance_between_two_points_expression",
        "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "display_name": "numeric / compute_distance_between_two_points",
        "answer_format_hint": "text_short",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          4436
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "text_short",
          "answer_shape": "text_short",
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
          "equivalence_type": "exact_string",
          "checker_key": "text_short_checker",
          "presentation_mode": "short_answer"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "distance_formula",
            "segment_length",
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
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "numeric_compute_distance_between_two_points_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [],
          "template_slots": {
            "stem": "two_point_distance_compute"
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
          "compute_distance_between_two_points",
          "short_answer",
          [
            "distance_formula_reasoning"
          ],
          [
            "coordinate_point",
            "distance_formula"
          ],
          "default"
        ],
        "canonical_base_problem_type_id": "compute_distance_between_two_points_short_answer",
        "value_type_prefix": "numeric",
        "_resolved_template_slot": "two_point_distance_compute",
        "naming_warning": "naming_warning:numeric_prefix_but_hint_is_text_short"
      },
      "generator_readiness": "contract_slot_mismatch",
      "usable_for_phase3": false,
      "template_slot": "two_point_distance_compute",
      "canonical_base_problem_type_id": "compute_distance_between_two_points_short_answer",
      "value_type_prefix": "numeric",
      "subskill_id": "compute_distance_between_two_points",
      "answer_type": "text_short",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.1714,
        "source_problem_type_score": 0.0513,
        "task_consistent_with_skill": true
      }
    },
    {
      "problem_type_id": "evaluate_function_value_2",
      "proposed_problem_type_id": "evaluate_function_value_2",
      "display_name": "evaluate_function_value / anchor bootstrap",
      "matched_example_ids": [],
      "matched_example_count": 0,
      "unmatched_example_ids": [],
      "representative_example_id": null,
      "structural_features": [
        "factored_expression"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "answer_equivalence": "algebraic_equivalent",
        "equivalence_type": "algebraic_equivalent",
        "checker": "expression_checker",
        "checker_key": "expression_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "expression_checker",
        "checker_selection_reason": "quadratic_factoring_expression",
        "accepted_formats": [
          "(x-5)(x+3)",
          "(2x-1)(x+5)",
          "2(x-1)(3x+2)"
        ],
        "answer_semantics": "algebraic_expression",
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
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
            "evaluate_function_value"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
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
            "evaluate_function_value"
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
            "stem": "function_value_numeric"
          },
          "problem_type_id": "evaluate_function_value_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "expression"
      },
      "checker_key_proposal": "expression_checker",
      "equivalence_type_proposal": "algebraic_equivalent",
      "answer_shape": "factored_expression",
      "answer_semantics": "algebraic_expression",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "expression_checker",
      "checker_selection_reason": "quadratic_factoring_expression",
      "confidence": "medium",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance",
        "anchor_slot_bootstrap_zero_source"
      ],
      "checker_contract_warnings": [],
      "spec_source": "anchor_slot_bootstrap",
      "grouping_reason": "anchor_subskill_bootstrap_zero_source",
      "feature_signature": [
        "anchor_slot_bootstrap",
        "evaluate_function_value"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "evaluate_function_value_2",
        "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
        "target_task": "evaluate_function_value",
        "task_family": "function_concept_family",
        "display_name": "evaluate_function_value / anchor bootstrap",
        "answer_format_hint": "expression",
        "source_example_ids": [],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "expression",
          "answer_shape": "factored_expression",
          "answer_equivalence": "algebraic_equivalent",
          "equivalence_type": "algebraic_equivalent",
          "checker": "expression_checker",
          "checker_key": "expression_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "expression_checker",
          "checker_selection_reason": "quadratic_factoring_expression",
          "accepted_formats": [
            "(x-5)(x+3)",
            "(2x-1)(x+5)",
            "2(x-1)(3x+2)"
          ],
          "answer_semantics": "algebraic_expression"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
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
            "evaluate_function_value"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
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
            "evaluate_function_value"
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
            "stem": "function_value_numeric"
          },
          "problem_type_id": "evaluate_function_value_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "anchor_slot_bootstrap",
        "grouping_reason": "anchor_subskill_bootstrap_zero_source",
        "feature_signature": [
          "anchor_slot_bootstrap",
          "evaluate_function_value"
        ],
        "canonical_base_problem_type_id": "evaluate_function_value_2",
        "value_type_prefix": "",
        "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
      },
      "generator_readiness": "runtime_ready",
      "usable_for_phase3": true,
      "template_slot": "function_value_numeric",
      "canonical_base_problem_type_id": "evaluate_function_value_2",
      "value_type_prefix": "",
      "subskill_id": "evaluate_function_value",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0,
        "task_consistent_with_skill": true
      },
      "answer_type": "expression"
    },
    {
      "problem_type_id": "interpret_function_notation_2",
      "proposed_problem_type_id": "interpret_function_notation_2",
      "display_name": "interpret_function_notation / anchor bootstrap",
      "matched_example_ids": [],
      "matched_example_count": 0,
      "unmatched_example_ids": [],
      "representative_example_id": null,
      "structural_features": [
        "factored_expression"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "answer_equivalence": "algebraic_equivalent",
        "equivalence_type": "algebraic_equivalent",
        "checker": "expression_checker",
        "checker_key": "expression_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "expression_checker",
        "checker_selection_reason": "quadratic_factoring_expression",
        "accepted_formats": [
          "(x-5)(x+3)",
          "(2x-1)(x+5)",
          "2(x-1)(3x+2)"
        ],
        "answer_semantics": "algebraic_expression",
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
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
            "interpret_function_notation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
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
            "interpret_function_notation"
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
            "stem": "linear_function_two_point_choice"
          },
          "problem_type_id": "interpret_function_notation_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "expression"
      },
      "checker_key_proposal": "expression_checker",
      "equivalence_type_proposal": "algebraic_equivalent",
      "answer_shape": "factored_expression",
      "answer_semantics": "algebraic_expression",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "expression_checker",
      "checker_selection_reason": "quadratic_factoring_expression",
      "confidence": "medium",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance",
        "anchor_slot_bootstrap_zero_source"
      ],
      "checker_contract_warnings": [],
      "spec_source": "anchor_slot_bootstrap",
      "grouping_reason": "anchor_subskill_bootstrap_zero_source",
      "feature_signature": [
        "anchor_slot_bootstrap",
        "interpret_function_notation"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "interpret_function_notation_2",
        "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
        "target_task": "interpret_function_notation",
        "task_family": "function_concept_family",
        "display_name": "interpret_function_notation / anchor bootstrap",
        "answer_format_hint": "expression",
        "source_example_ids": [],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "expression",
          "answer_shape": "factored_expression",
          "answer_equivalence": "algebraic_equivalent",
          "equivalence_type": "algebraic_equivalent",
          "checker": "expression_checker",
          "checker_key": "expression_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "expression_checker",
          "checker_selection_reason": "quadratic_factoring_expression",
          "accepted_formats": [
            "(x-5)(x+3)",
            "(2x-1)(x+5)",
            "2(x-1)(3x+2)"
          ],
          "answer_semantics": "algebraic_expression"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "quadratic_inequality"
          ],
          "required_math_objects": [
            "quadratic_inequality"
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
            "interpret_function_notation"
          ],
          "reject_if": [
            "unused_condition",
            "ambiguous_answer",
            "answer_not_derivable"
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
            "interpret_function_notation"
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
            "stem": "linear_function_two_point_choice"
          },
          "problem_type_id": "interpret_function_notation_2",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [
            "single_template_variant_only",
            "variation_dimensions_below_recommended_minimum"
          ]
        },
        "validator_contract": {
          "static_checks": [
            "answer_contract_checks"
          ],
          "semantic_checks": [
            "givens_to_target_dependency"
          ],
          "runtime_smoke_count": 30
        },
        "spec_source": "anchor_slot_bootstrap",
        "grouping_reason": "anchor_subskill_bootstrap_zero_source",
        "feature_signature": [
          "anchor_slot_bootstrap",
          "interpret_function_notation"
        ],
        "canonical_base_problem_type_id": "interpret_function_notation_2",
        "value_type_prefix": "",
        "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
      },
      "generator_readiness": "runtime_ready",
      "usable_for_phase3": true,
      "template_slot": "linear_function_two_point_choice",
      "canonical_base_problem_type_id": "interpret_function_notation_2",
      "value_type_prefix": "",
      "subskill_id": "interpret_function_notation",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0,
        "task_consistent_with_skill": true
      },
      "answer_type": "expression"
    }
  ],
  "per_example_classification": [
    {
      "example_id": 4432,
      "detected_problem_type_id": "numeric_solve_unknown_coordinate_from_two_point_distance_short_answer",
      "example_feature": {
        "source_example_id": 4432,
        "question_text": "設$P\\left( 2,-3 \\right)$、$Q\\left( 6,k \\right)$為坐標平面上兩點，且$\\overline{PQ}=5$，試求k值。",
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
          "distance_formula",
          "parameter",
          "segment_length",
          "two_coordinate_points",
          "unknown_coordinate"
        ],
        "target_task": "solve_unknown_coordinate_from_two_point_distance",
        "task_family": "distance_between_two_points_family",
        "reasoning_type": [
          "distance_formula_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "P",
          "Q",
          "k"
        ],
        "givens": [
          "P",
          "Q",
          "k"
        ],
        "target": "solve_unknown_coordinate_from_two_point_distance",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.45,
          "ai_best_candidate_id": "C11",
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
          "rule_target_task": "solve_unknown_coordinate_from_two_point_distance",
          "rule_task_family": "distance_between_two_points_family",
          "rule_confidence": 0.55,
          "final_target_task": "solve_unknown_coordinate_from_two_point_distance",
          "final_task_family": "distance_between_two_points_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compare_distances_between_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compare_distances_between_points",
              "label": "compare_distances_between_points",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "target_task": "compute_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_distance",
              "label": "compute_distance",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C3",
              "target_task": "compute_distance_between_two_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_distance_between_two_points",
              "label": "compute_distance_between_two_points",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C4",
              "target_task": "compute_missing_coordinate_from_two_point_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_missing_coordinate_from_two_point_distance",
              "label": "compute_missing_coordinate_from_two_point_distance",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C5",
              "target_task": "evaluate_function_value",
              "task_family": "function_concept_family",
              "problem_type_id": "evaluate_function_value",
              "label": "evaluate_function_value",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "evaluate_function_value"
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
              "candidate_id": "C6",
              "target_task": "interpret_function_notation",
              "task_family": "function_concept_family",
              "problem_type_id": "interpret_function_notation",
              "label": "interpret_function_notation",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "interpret_function_notation"
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
              "candidate_id": "C7",
              "target_task": "judge_domain_range_basic",
              "task_family": "function_concept_family",
              "problem_type_id": "judge_domain_range_basic",
              "label": "judge_domain_range_basic",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "judge_domain_range_basic"
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
              "candidate_id": "C8",
              "target_task": "judge_function_from_mapping",
              "task_family": "function_concept_family",
              "problem_type_id": "judge_function_from_mapping",
              "label": "judge_function_from_mapping",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "judge_function_from_mapping"
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
              "candidate_id": "C9",
              "target_task": "judge_function_relation",
              "task_family": "function_concept_family",
              "problem_type_id": "judge_function_relation",
              "label": "judge_function_relation",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "judge_function_relation"
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
              "candidate_id": "C10",
              "target_task": "solve_parameter_from_distance_formula",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "solve_parameter_from_distance_formula",
              "label": "solve_parameter_from_distance_formula",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C11",
              "target_task": "solve_unknown_coordinate_from_two_point_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "solve_unknown_coordinate_from_two_point_distance",
              "label": "solve_unknown_coordinate_from_two_point_distance",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C12",
              "target_task": "verify_distance_between_two_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "verify_distance_between_two_points",
              "label": "verify_distance_between_two_points",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
          "selected_subskill": "solve_unknown_coordinate_from_two_point_distance",
          "selected_problem_type": "solve_unknown_coordinate_from_two_point_distance",
          "candidate_source": "anchor",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "solve_unknown_coordinate_from_two_point_distance",
          "task_family": "distance_between_two_points_family",
          "math_objects": [
            "coordinate_point",
            "distance_formula",
            "parameter",
            "segment_length",
            "two_coordinate_points",
            "unknown_coordinate"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
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
              "example_id": 4419,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 3"
            },
            {
              "example_id": 4432,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4436,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4437,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "requires_human_action": false
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.45,
        "ai_best_candidate_id": "C11",
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
        "rule_target_task": "solve_unknown_coordinate_from_two_point_distance",
        "rule_task_family": "distance_between_two_points_family",
        "rule_confidence": 0.55,
        "final_target_task": "solve_unknown_coordinate_from_two_point_distance",
        "final_task_family": "distance_between_two_points_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compare_distances_between_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compare_distances_between_points",
            "label": "compare_distances_between_points",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "target_task": "compute_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_distance",
            "label": "compute_distance",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C3",
            "target_task": "compute_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_distance_between_two_points",
            "label": "compute_distance_between_two_points",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C4",
            "target_task": "compute_missing_coordinate_from_two_point_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_missing_coordinate_from_two_point_distance",
            "label": "compute_missing_coordinate_from_two_point_distance",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C5",
            "target_task": "evaluate_function_value",
            "task_family": "function_concept_family",
            "problem_type_id": "evaluate_function_value",
            "label": "evaluate_function_value",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "evaluate_function_value"
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
            "candidate_id": "C6",
            "target_task": "interpret_function_notation",
            "task_family": "function_concept_family",
            "problem_type_id": "interpret_function_notation",
            "label": "interpret_function_notation",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "interpret_function_notation"
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
            "candidate_id": "C7",
            "target_task": "judge_domain_range_basic",
            "task_family": "function_concept_family",
            "problem_type_id": "judge_domain_range_basic",
            "label": "judge_domain_range_basic",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "judge_domain_range_basic"
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
            "candidate_id": "C8",
            "target_task": "judge_function_from_mapping",
            "task_family": "function_concept_family",
            "problem_type_id": "judge_function_from_mapping",
            "label": "judge_function_from_mapping",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "judge_function_from_mapping"
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
            "candidate_id": "C9",
            "target_task": "judge_function_relation",
            "task_family": "function_concept_family",
            "problem_type_id": "judge_function_relation",
            "label": "judge_function_relation",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "judge_function_relation"
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
            "candidate_id": "C10",
            "target_task": "solve_parameter_from_distance_formula",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "solve_parameter_from_distance_formula",
            "label": "solve_parameter_from_distance_formula",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C11",
            "target_task": "solve_unknown_coordinate_from_two_point_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "solve_unknown_coordinate_from_two_point_distance",
            "label": "solve_unknown_coordinate_from_two_point_distance",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C12",
            "target_task": "verify_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "verify_distance_between_two_points",
            "label": "verify_distance_between_two_points",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
        "selected_subskill": "solve_unknown_coordinate_from_two_point_distance",
        "selected_problem_type": "solve_unknown_coordinate_from_two_point_distance",
        "candidate_source": "anchor",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "solve_unknown_coordinate_from_two_point_distance",
        "task_family": "distance_between_two_points_family",
        "math_objects": [
          "coordinate_point",
          "distance_formula",
          "parameter",
          "segment_length",
          "two_coordinate_points",
          "unknown_coordinate"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
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
      "subskill_id": "solve_unknown_coordinate_from_two_point_distance",
      "classification_source": "rule_fallback_ai_unavailable",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker",
      "alignment_score": 0.8,
      "requires_human_action": false
    },
    {
      "example_id": 4419,
      "detected_problem_type_id": "numeric_solve_unknown_coordinate_from_two_point_distance_short_answer",
      "example_feature": {
        "source_example_id": 4419,
        "question_text": "設$A\\left( k,-5 \\right)$、$B\\left( 2,7 \\right)$為坐標平面上兩點，且$\\overline{AB}=13$，試求k值。",
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
          "distance_formula",
          "parameter",
          "segment_length",
          "two_coordinate_points",
          "unknown_coordinate"
        ],
        "target_task": "solve_unknown_coordinate_from_two_point_distance",
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
          "k"
        ],
        "givens": [
          "A",
          "B",
          "k"
        ],
        "target": "solve_unknown_coordinate_from_two_point_distance",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.45,
          "ai_best_candidate_id": "C11",
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
          "rule_target_task": "solve_unknown_coordinate_from_two_point_distance",
          "rule_task_family": "distance_between_two_points_family",
          "rule_confidence": 0.55,
          "final_target_task": "solve_unknown_coordinate_from_two_point_distance",
          "final_task_family": "distance_between_two_points_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compare_distances_between_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compare_distances_between_points",
              "label": "compare_distances_between_points",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "target_task": "compute_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_distance",
              "label": "compute_distance",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C3",
              "target_task": "compute_distance_between_two_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_distance_between_two_points",
              "label": "compute_distance_between_two_points",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C4",
              "target_task": "compute_missing_coordinate_from_two_point_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_missing_coordinate_from_two_point_distance",
              "label": "compute_missing_coordinate_from_two_point_distance",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C5",
              "target_task": "evaluate_function_value",
              "task_family": "function_concept_family",
              "problem_type_id": "evaluate_function_value",
              "label": "evaluate_function_value",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "evaluate_function_value"
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
              "candidate_id": "C6",
              "target_task": "interpret_function_notation",
              "task_family": "function_concept_family",
              "problem_type_id": "interpret_function_notation",
              "label": "interpret_function_notation",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "interpret_function_notation"
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
              "candidate_id": "C7",
              "target_task": "judge_domain_range_basic",
              "task_family": "function_concept_family",
              "problem_type_id": "judge_domain_range_basic",
              "label": "judge_domain_range_basic",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "judge_domain_range_basic"
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
              "candidate_id": "C8",
              "target_task": "judge_function_from_mapping",
              "task_family": "function_concept_family",
              "problem_type_id": "judge_function_from_mapping",
              "label": "judge_function_from_mapping",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "judge_function_from_mapping"
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
              "candidate_id": "C9",
              "target_task": "judge_function_relation",
              "task_family": "function_concept_family",
              "problem_type_id": "judge_function_relation",
              "label": "judge_function_relation",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "judge_function_relation"
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
              "candidate_id": "C10",
              "target_task": "solve_parameter_from_distance_formula",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "solve_parameter_from_distance_formula",
              "label": "solve_parameter_from_distance_formula",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C11",
              "target_task": "solve_unknown_coordinate_from_two_point_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "solve_unknown_coordinate_from_two_point_distance",
              "label": "solve_unknown_coordinate_from_two_point_distance",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C12",
              "target_task": "verify_distance_between_two_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "verify_distance_between_two_points",
              "label": "verify_distance_between_two_points",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
          "selected_subskill": "solve_unknown_coordinate_from_two_point_distance",
          "selected_problem_type": "solve_unknown_coordinate_from_two_point_distance",
          "candidate_source": "anchor",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "solve_unknown_coordinate_from_two_point_distance",
          "task_family": "distance_between_two_points_family",
          "math_objects": [
            "coordinate_point",
            "distance_formula",
            "parameter",
            "segment_length",
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
              "example_id": 4432,
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
              "example_id": 4419,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 3"
            },
            {
              "example_id": 4432,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4436,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4437,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "requires_human_action": false
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.45,
        "ai_best_candidate_id": "C11",
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
        "rule_target_task": "solve_unknown_coordinate_from_two_point_distance",
        "rule_task_family": "distance_between_two_points_family",
        "rule_confidence": 0.55,
        "final_target_task": "solve_unknown_coordinate_from_two_point_distance",
        "final_task_family": "distance_between_two_points_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compare_distances_between_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compare_distances_between_points",
            "label": "compare_distances_between_points",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "target_task": "compute_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_distance",
            "label": "compute_distance",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C3",
            "target_task": "compute_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_distance_between_two_points",
            "label": "compute_distance_between_two_points",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C4",
            "target_task": "compute_missing_coordinate_from_two_point_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_missing_coordinate_from_two_point_distance",
            "label": "compute_missing_coordinate_from_two_point_distance",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C5",
            "target_task": "evaluate_function_value",
            "task_family": "function_concept_family",
            "problem_type_id": "evaluate_function_value",
            "label": "evaluate_function_value",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "evaluate_function_value"
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
            "candidate_id": "C6",
            "target_task": "interpret_function_notation",
            "task_family": "function_concept_family",
            "problem_type_id": "interpret_function_notation",
            "label": "interpret_function_notation",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "interpret_function_notation"
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
            "candidate_id": "C7",
            "target_task": "judge_domain_range_basic",
            "task_family": "function_concept_family",
            "problem_type_id": "judge_domain_range_basic",
            "label": "judge_domain_range_basic",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "judge_domain_range_basic"
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
            "candidate_id": "C8",
            "target_task": "judge_function_from_mapping",
            "task_family": "function_concept_family",
            "problem_type_id": "judge_function_from_mapping",
            "label": "judge_function_from_mapping",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "judge_function_from_mapping"
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
            "candidate_id": "C9",
            "target_task": "judge_function_relation",
            "task_family": "function_concept_family",
            "problem_type_id": "judge_function_relation",
            "label": "judge_function_relation",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "judge_function_relation"
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
            "candidate_id": "C10",
            "target_task": "solve_parameter_from_distance_formula",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "solve_parameter_from_distance_formula",
            "label": "solve_parameter_from_distance_formula",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C11",
            "target_task": "solve_unknown_coordinate_from_two_point_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "solve_unknown_coordinate_from_two_point_distance",
            "label": "solve_unknown_coordinate_from_two_point_distance",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C12",
            "target_task": "verify_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "verify_distance_between_two_points",
            "label": "verify_distance_between_two_points",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
        "selected_subskill": "solve_unknown_coordinate_from_two_point_distance",
        "selected_problem_type": "solve_unknown_coordinate_from_two_point_distance",
        "candidate_source": "anchor",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "solve_unknown_coordinate_from_two_point_distance",
        "task_family": "distance_between_two_points_family",
        "math_objects": [
          "coordinate_point",
          "distance_formula",
          "parameter",
          "segment_length",
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
      "subskill_id": "solve_unknown_coordinate_from_two_point_distance",
      "classification_source": "rule_fallback_ai_unavailable",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker",
      "alignment_score": 0.8,
      "requires_human_action": false
    },
    {
      "example_id": 4436,
      "detected_problem_type_id": "numeric_compute_distance_between_two_points_short_answer",
      "example_feature": {
        "source_example_id": 4436,
        "question_text": "試求坐標平面上$A\\left( 3,-1 \\right)$、$B(4,2)$\n兩點間的距離。",
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
          "distance_formula",
          "segment_length",
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
          "B"
        ],
        "givens": [
          "A",
          "B"
        ],
        "target": "compute_distance_between_two_points",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.45,
          "ai_best_candidate_id": "C3",
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
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compare_distances_between_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compare_distances_between_points",
              "label": "compare_distances_between_points",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "target_task": "compute_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_distance",
              "label": "compute_distance",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C3",
              "target_task": "compute_distance_between_two_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_distance_between_two_points",
              "label": "compute_distance_between_two_points",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C4",
              "target_task": "compute_missing_coordinate_from_two_point_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_missing_coordinate_from_two_point_distance",
              "label": "compute_missing_coordinate_from_two_point_distance",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C5",
              "target_task": "evaluate_function_value",
              "task_family": "function_concept_family",
              "problem_type_id": "evaluate_function_value",
              "label": "evaluate_function_value",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "evaluate_function_value"
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
              "candidate_id": "C6",
              "target_task": "interpret_function_notation",
              "task_family": "function_concept_family",
              "problem_type_id": "interpret_function_notation",
              "label": "interpret_function_notation",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "interpret_function_notation"
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
              "candidate_id": "C7",
              "target_task": "judge_domain_range_basic",
              "task_family": "function_concept_family",
              "problem_type_id": "judge_domain_range_basic",
              "label": "judge_domain_range_basic",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "judge_domain_range_basic"
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
              "candidate_id": "C8",
              "target_task": "judge_function_from_mapping",
              "task_family": "function_concept_family",
              "problem_type_id": "judge_function_from_mapping",
              "label": "judge_function_from_mapping",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "judge_function_from_mapping"
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
              "candidate_id": "C9",
              "target_task": "judge_function_relation",
              "task_family": "function_concept_family",
              "problem_type_id": "judge_function_relation",
              "label": "judge_function_relation",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "judge_function_relation"
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
              "candidate_id": "C10",
              "target_task": "solve_parameter_from_distance_formula",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "solve_parameter_from_distance_formula",
              "label": "solve_parameter_from_distance_formula",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C11",
              "target_task": "solve_unknown_coordinate_from_two_point_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "solve_unknown_coordinate_from_two_point_distance",
              "label": "solve_unknown_coordinate_from_two_point_distance",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C12",
              "target_task": "verify_distance_between_two_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "verify_distance_between_two_points",
              "label": "verify_distance_between_two_points",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
          "candidate_source": "anchor",
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
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false
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
              "example_id": 4432,
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
              "example_id": 4419,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 3"
            },
            {
              "example_id": 4432,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4436,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4437,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "requires_human_action": false
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.45,
        "ai_best_candidate_id": "C3",
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
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compare_distances_between_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compare_distances_between_points",
            "label": "compare_distances_between_points",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "target_task": "compute_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_distance",
            "label": "compute_distance",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C3",
            "target_task": "compute_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_distance_between_two_points",
            "label": "compute_distance_between_two_points",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C4",
            "target_task": "compute_missing_coordinate_from_two_point_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_missing_coordinate_from_two_point_distance",
            "label": "compute_missing_coordinate_from_two_point_distance",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C5",
            "target_task": "evaluate_function_value",
            "task_family": "function_concept_family",
            "problem_type_id": "evaluate_function_value",
            "label": "evaluate_function_value",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "evaluate_function_value"
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
            "candidate_id": "C6",
            "target_task": "interpret_function_notation",
            "task_family": "function_concept_family",
            "problem_type_id": "interpret_function_notation",
            "label": "interpret_function_notation",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "interpret_function_notation"
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
            "candidate_id": "C7",
            "target_task": "judge_domain_range_basic",
            "task_family": "function_concept_family",
            "problem_type_id": "judge_domain_range_basic",
            "label": "judge_domain_range_basic",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "judge_domain_range_basic"
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
            "candidate_id": "C8",
            "target_task": "judge_function_from_mapping",
            "task_family": "function_concept_family",
            "problem_type_id": "judge_function_from_mapping",
            "label": "judge_function_from_mapping",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "judge_function_from_mapping"
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
            "candidate_id": "C9",
            "target_task": "judge_function_relation",
            "task_family": "function_concept_family",
            "problem_type_id": "judge_function_relation",
            "label": "judge_function_relation",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "judge_function_relation"
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
            "candidate_id": "C10",
            "target_task": "solve_parameter_from_distance_formula",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "solve_parameter_from_distance_formula",
            "label": "solve_parameter_from_distance_formula",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C11",
            "target_task": "solve_unknown_coordinate_from_two_point_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "solve_unknown_coordinate_from_two_point_distance",
            "label": "solve_unknown_coordinate_from_two_point_distance",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C12",
            "target_task": "verify_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "verify_distance_between_two_points",
            "label": "verify_distance_between_two_points",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
        "candidate_source": "anchor",
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
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false
      },
      "subskill_id": "compute_distance_between_two_points",
      "classification_source": "rule_fallback_ai_unavailable",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker",
      "alignment_score": 0.8,
      "requires_human_action": false
    },
    {
      "example_id": 4437,
      "detected_problem_type_id": "numeric_solve_unknown_coordinate_from_two_point_distance_short_answer",
      "example_feature": {
        "source_example_id": 4437,
        "question_text": "設$A\\left( -2,-6 \\right)$、$B\\left( k,2 \\right)$為坐標平面上兩點，且$\\overline{AB}=10$，試求k值。",
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
          "distance_formula",
          "parameter",
          "segment_length",
          "two_coordinate_points",
          "unknown_coordinate"
        ],
        "target_task": "solve_unknown_coordinate_from_two_point_distance",
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
          "k"
        ],
        "givens": [
          "A",
          "B",
          "k"
        ],
        "target": "solve_unknown_coordinate_from_two_point_distance",
        "classifier_source": "rule_fallback_ai_unavailable",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.45,
          "ai_best_candidate_id": "C11",
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
          "rule_target_task": "solve_unknown_coordinate_from_two_point_distance",
          "rule_task_family": "distance_between_two_points_family",
          "rule_confidence": 0.55,
          "final_target_task": "solve_unknown_coordinate_from_two_point_distance",
          "final_task_family": "distance_between_two_points_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "compare_distances_between_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compare_distances_between_points",
              "label": "compare_distances_between_points",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "target_task": "compute_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_distance",
              "label": "compute_distance",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C3",
              "target_task": "compute_distance_between_two_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_distance_between_two_points",
              "label": "compute_distance_between_two_points",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C4",
              "target_task": "compute_missing_coordinate_from_two_point_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "compute_missing_coordinate_from_two_point_distance",
              "label": "compute_missing_coordinate_from_two_point_distance",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C5",
              "target_task": "evaluate_function_value",
              "task_family": "function_concept_family",
              "problem_type_id": "evaluate_function_value",
              "label": "evaluate_function_value",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "evaluate_function_value"
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
              "candidate_id": "C6",
              "target_task": "interpret_function_notation",
              "task_family": "function_concept_family",
              "problem_type_id": "interpret_function_notation",
              "label": "interpret_function_notation",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "interpret_function_notation"
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
              "candidate_id": "C7",
              "target_task": "judge_domain_range_basic",
              "task_family": "function_concept_family",
              "problem_type_id": "judge_domain_range_basic",
              "label": "judge_domain_range_basic",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "judge_domain_range_basic"
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
              "candidate_id": "C8",
              "target_task": "judge_function_from_mapping",
              "task_family": "function_concept_family",
              "problem_type_id": "judge_function_from_mapping",
              "label": "judge_function_from_mapping",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "judge_function_from_mapping"
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
              "candidate_id": "C9",
              "target_task": "judge_function_relation",
              "task_family": "function_concept_family",
              "problem_type_id": "judge_function_relation",
              "label": "judge_function_relation",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
                  "judge_function_relation"
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
              "candidate_id": "C10",
              "target_task": "solve_parameter_from_distance_formula",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "solve_parameter_from_distance_formula",
              "label": "solve_parameter_from_distance_formula",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C11",
              "target_task": "solve_unknown_coordinate_from_two_point_distance",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "solve_unknown_coordinate_from_two_point_distance",
              "label": "solve_unknown_coordinate_from_two_point_distance",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
              "candidate_id": "C12",
              "target_task": "verify_distance_between_two_points",
              "task_family": "distance_between_two_points_family",
              "problem_type_id": "verify_distance_between_two_points",
              "label": "verify_distance_between_two_points",
              "candidate_source": "anchor",
              "in_anchor_scope": true,
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
          "selected_subskill": "solve_unknown_coordinate_from_two_point_distance",
          "selected_problem_type": "solve_unknown_coordinate_from_two_point_distance",
          "candidate_source": "anchor",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "solve_unknown_coordinate_from_two_point_distance",
          "task_family": "distance_between_two_points_family",
          "math_objects": [
            "coordinate_point",
            "distance_formula",
            "parameter",
            "segment_length",
            "two_coordinate_points",
            "unknown_coordinate"
          ],
          "answer_type": "numeric",
          "answer_shape": "numeric",
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
              "example_id": 4432,
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
              "example_id": 4419,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-2習題 基礎題 3"
            },
            {
              "example_id": 4432,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4436,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4437,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "requires_human_action": false
      },
      "answer_shape": "numeric",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.45,
        "ai_best_candidate_id": "C11",
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
        "rule_target_task": "solve_unknown_coordinate_from_two_point_distance",
        "rule_task_family": "distance_between_two_points_family",
        "rule_confidence": 0.55,
        "final_target_task": "solve_unknown_coordinate_from_two_point_distance",
        "final_task_family": "distance_between_two_points_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "compare_distances_between_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compare_distances_between_points",
            "label": "compare_distances_between_points",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "target_task": "compute_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_distance",
            "label": "compute_distance",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C3",
            "target_task": "compute_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_distance_between_two_points",
            "label": "compute_distance_between_two_points",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C4",
            "target_task": "compute_missing_coordinate_from_two_point_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "compute_missing_coordinate_from_two_point_distance",
            "label": "compute_missing_coordinate_from_two_point_distance",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C5",
            "target_task": "evaluate_function_value",
            "task_family": "function_concept_family",
            "problem_type_id": "evaluate_function_value",
            "label": "evaluate_function_value",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "evaluate_function_value"
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
            "candidate_id": "C6",
            "target_task": "interpret_function_notation",
            "task_family": "function_concept_family",
            "problem_type_id": "interpret_function_notation",
            "label": "interpret_function_notation",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "interpret_function_notation"
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
            "candidate_id": "C7",
            "target_task": "judge_domain_range_basic",
            "task_family": "function_concept_family",
            "problem_type_id": "judge_domain_range_basic",
            "label": "judge_domain_range_basic",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "judge_domain_range_basic"
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
            "candidate_id": "C8",
            "target_task": "judge_function_from_mapping",
            "task_family": "function_concept_family",
            "problem_type_id": "judge_function_from_mapping",
            "label": "judge_function_from_mapping",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "judge_function_from_mapping"
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
            "candidate_id": "C9",
            "target_task": "judge_function_relation",
            "task_family": "function_concept_family",
            "problem_type_id": "judge_function_relation",
            "label": "judge_function_relation",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
                "judge_function_relation"
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
            "candidate_id": "C10",
            "target_task": "solve_parameter_from_distance_formula",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "solve_parameter_from_distance_formula",
            "label": "solve_parameter_from_distance_formula",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C11",
            "target_task": "solve_unknown_coordinate_from_two_point_distance",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "solve_unknown_coordinate_from_two_point_distance",
            "label": "solve_unknown_coordinate_from_two_point_distance",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
            "candidate_id": "C12",
            "target_task": "verify_distance_between_two_points",
            "task_family": "distance_between_two_points_family",
            "problem_type_id": "verify_distance_between_two_points",
            "label": "verify_distance_between_two_points",
            "candidate_source": "anchor",
            "in_anchor_scope": true,
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
        "selected_subskill": "solve_unknown_coordinate_from_two_point_distance",
        "selected_problem_type": "solve_unknown_coordinate_from_two_point_distance",
        "candidate_source": "anchor",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "solve_unknown_coordinate_from_two_point_distance",
        "task_family": "distance_between_two_points_family",
        "math_objects": [
          "coordinate_point",
          "distance_formula",
          "parameter",
          "segment_length",
          "two_coordinate_points",
          "unknown_coordinate"
        ],
        "answer_type": "numeric",
        "answer_shape": "numeric",
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
      "subskill_id": "solve_unknown_coordinate_from_two_point_distance",
      "classification_source": "rule_fallback_ai_unavailable",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "integer",
      "equivalence_type": "numeric_exact",
      "checker_key": "integer_checker",
      "alignment_score": 0.8,
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
      "ai_partial_unavailable_relaxed_tolerance",
      "anchor_slot_bootstrap_zero_source"
    ]
  },
  "generator_draft_gate": {
    "status": "generator_draft_allowed_with_low_source_warning",
    "allowed": true,
    "warnings": [
      "low_source_examples",
      "ai_first_mode_fell_back_to_rule_only",
      "ai_partial_unavailable_relaxed_tolerance",
      "anchor_slot_bootstrap_zero_source"
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
      "ai_partial_unavailable_relaxed_tolerance",
      "anchor_slot_bootstrap_zero_source"
    ]
  },
  "exception_review_gate": {
    "required": false,
    "reasons": []
  },
  "self_healing_log": [],
  "reports": {
    "auto_pipeline_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_auto_pipeline_summary.json",
    "auto_pipeline_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_auto_pipeline_summary.md",
    "phase1_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase1_summary.json",
    "phase1_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase1_summary.md",
    "phase1_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase1_summary.json",
    "phase1_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase1_summary.md",
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase2_generator_summary.json",
    "phase2_generator_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase2_generator_summary.md",
    "phase2_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase2_generator_summary.json",
    "phase2_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase2_generator_summary.md",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_DistanceBetweenTwoPointsInPlane_generator_draft_spec.json"
  },
  "next_action": "manual_review_before_runtime_enable",
  "timestamp": "2026-07-01T16:33:37.821024+00:00",
  "dry_run": true
}
```
