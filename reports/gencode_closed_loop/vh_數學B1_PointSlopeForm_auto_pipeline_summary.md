# Gencode Auto Pipeline Summary: vh_數學B1_PointSlopeForm

## summary
```json
{
  "ok": true,
  "skill_id": "vh_數學B1_PointSlopeForm",
  "pipeline_status": "auto_pipeline_completed_runtime_blocked",
  "source_example_count": 14,
  "candidate_problem_types": [
    {
      "problem_type_id": "expression_write_line_equation_from_point_slope",
      "proposed_problem_type_id": "expression_write_line_equation_from_point_slope",
      "display_name": "expression / write_line_equation_from_point_slope",
      "matched_example_ids": [
        4540,
        4541,
        4543,
        4546,
        4549,
        4550,
        4551,
        4552,
        4556,
        4560
      ],
      "matched_example_count": 10,
      "unmatched_example_ids": [],
      "representative_example_id": 4540,
      "structural_features": [
        "linear_equation"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "source_has_choices": false,
        "answer_type": "expression",
        "answer_shape": "linear_equation",
        "answer_semantics": "line_equation",
        "answer_equivalence": "exact_string",
        "equivalence_type": "exact_string",
        "checker": "equation_checker",
        "checker_key": "equation_checker",
        "presentation_mode": "",
        "selected_checker": "linear_equation_equivalent_checker",
        "checker_selection_reason": "line_equation_family",
        "accepted_formats": [
          "y - 2 = 3(x - 1)",
          "y = 3x - 1",
          "3x - y - 1 = 0"
        ],
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "line_equation",
            "two_coordinate_points",
            "three_coordinate_points",
            "triangle"
          ],
          "required_math_objects": [
            "coordinate_point",
            "line_equation"
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
            "line_equation_reasoning"
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
              "id": "given_point_and_slope_find_point_slope_form",
              "label": "點斜式",
              "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
              "weight": 1.0,
              "enabled": true
            },
            {
              "id": "given_point_and_slope_find_slope_intercept_form",
              "label": "斜截式",
              "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
              "weight": 1.0,
              "enabled": true
            },
            {
              "id": "given_point_and_slope_find_general_form",
              "label": "一般式",
              "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "point_coordinates": {
              "x_min": -8,
              "x_max": 8,
              "y_min": -8,
              "y_max": 8,
              "integer_only": true
            },
            "slope": {
              "choices": [
                "integer",
                "simple_fraction"
              ],
              "weights": [
                0.65,
                0.35
              ],
              "integer_range": [
                -5,
                5
              ],
              "exclude_zero": true,
              "fraction_numerators": [
                1,
                2,
                3,
                -1,
                -2,
                -3
              ],
              "fraction_denominators": [
                2,
                3
              ]
            },
            "equation_form": {
              "choices": [
                "point_slope",
                "slope_intercept",
                "general"
              ],
              "weights": [
                0.34,
                0.33,
                0.33
              ]
            }
          },
          "variation_dimensions": [
            "point_coordinates",
            "slope_type",
            "equation_form",
            "integer_or_fraction_slope",
            "coefficient_normalization",
            "number_variation",
            "template_variant",
            "coordinate_sign_combination"
          ],
          "difficulty_controls": {
            "level_1": {
              "coordinate_range": [
                -5,
                5
              ],
              "integer_slope_only": true,
              "equation_form": "point_slope"
            },
            "level_2": {
              "coordinate_range": [
                -8,
                8
              ],
              "allow_fraction_slope": true
            },
            "level_3": {
              "allow_negative_slope": true,
              "require_general_form": true
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
            "slope is finite",
            "point coordinates are integers",
            "generated equation passes through the point",
            "generated equation has the requested slope",
            "equivalent forms normalize to same Ax + By + C = 0"
          ],
          "answer_shape": "linear_equation",
          "explanation_variants": [
            "point_slope_to_general",
            "slope_intercept_to_general"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "write_line_equation_from_point_slope"
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
          "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [],
          "template_slots": {
            "stem": "line_equation_from_point_slope"
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
        "canonical_answer_schema": "equation"
      },
      "checker_key_proposal": "equation_checker",
      "equivalence_type_proposal": "exact_string",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "ai_partial_unavailable_relaxed_tolerance"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "merged_by_canonical_contract",
      "feature_signature": [
        "canonical_contract_merge",
        "write_line_equation_from_point_slope",
        "equation",
        "short_answer"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "equation_write_line_equation_from_point_slope_expression",
        "skill_id": "vh_數學B1_PointSlopeForm",
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "display_name": "equation / write_line_equation_from_point_slope",
        "answer_format_hint": "integer",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          4540,
          4541,
          4543,
          4546,
          4549,
          4550,
          4551,
          4552,
          4556,
          4560
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "source_has_choices": false,
          "answer_type": "expression",
          "answer_shape": "linear_equation",
          "answer_semantics": "line_equation",
          "answer_equivalence": "algebraic_equivalent",
          "equivalence_type": "algebraic_equivalent",
          "checker": "expression_checker",
          "checker_key": "expression_checker",
          "presentation_mode": "short_answer",
          "selected_checker": "linear_equation_equivalent_checker",
          "checker_selection_reason": "line_equation_family",
          "accepted_formats": [
            "y - 2 = 3(x - 1)",
            "y = 3x - 1",
            "3x - y - 1 = 0"
          ]
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "line_equation",
            "two_coordinate_points",
            "three_coordinate_points",
            "triangle"
          ],
          "required_math_objects": [
            "coordinate_point",
            "line_equation"
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
            "line_equation_reasoning"
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
              "id": "given_point_and_slope_find_point_slope_form",
              "label": "點斜式",
              "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
              "weight": 1.0,
              "enabled": true
            },
            {
              "id": "given_point_and_slope_find_slope_intercept_form",
              "label": "斜截式",
              "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
              "weight": 1.0,
              "enabled": true
            },
            {
              "id": "given_point_and_slope_find_general_form",
              "label": "一般式",
              "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "point_coordinates": {
              "x_min": -8,
              "x_max": 8,
              "y_min": -8,
              "y_max": 8,
              "integer_only": true
            },
            "slope": {
              "choices": [
                "integer",
                "simple_fraction"
              ],
              "weights": [
                0.65,
                0.35
              ],
              "integer_range": [
                -5,
                5
              ],
              "exclude_zero": true,
              "fraction_numerators": [
                1,
                2,
                3,
                -1,
                -2,
                -3
              ],
              "fraction_denominators": [
                2,
                3
              ]
            },
            "equation_form": {
              "choices": [
                "point_slope",
                "slope_intercept",
                "general"
              ],
              "weights": [
                0.34,
                0.33,
                0.33
              ]
            }
          },
          "variation_dimensions": [
            "point_coordinates",
            "slope_type",
            "equation_form",
            "integer_or_fraction_slope",
            "coefficient_normalization",
            "number_variation",
            "template_variant",
            "coordinate_sign_combination"
          ],
          "difficulty_controls": {
            "level_1": {
              "coordinate_range": [
                -5,
                5
              ],
              "integer_slope_only": true,
              "equation_form": "point_slope"
            },
            "level_2": {
              "coordinate_range": [
                -8,
                8
              ],
              "allow_fraction_slope": true
            },
            "level_3": {
              "allow_negative_slope": true,
              "require_general_form": true
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
            "slope is finite",
            "point coordinates are integers",
            "generated equation passes through the point",
            "generated equation has the requested slope",
            "equivalent forms normalize to same Ax + By + C = 0"
          ],
          "answer_shape": "linear_equation",
          "explanation_variants": [
            "point_slope_to_general",
            "slope_intercept_to_general"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "write_line_equation_from_point_slope"
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
          "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
          "contract_validation_blockers": [],
          "contract_validation_warnings": [],
          "template_slots": {
            "stem": "line_equation_from_point_slope"
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
        "grouping_reason": "merged_by_canonical_contract",
        "feature_signature": [
          "canonical_contract_merge",
          "write_line_equation_from_point_slope",
          "equation",
          "short_answer"
        ],
        "canonical_base_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
        "value_type_prefix": "",
        "_resolved_template_slot": "line_equation_from_point_slope"
      },
      "generator_readiness": "runtime_ready",
      "usable_for_phase3": true,
      "template_slot": "line_equation_from_point_slope",
      "canonical_base_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "value_type_prefix": "",
      "subskill_id": "write_line_equation_from_point_slope",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0769,
        "source_problem_type_score": 0.027,
        "task_consistent_with_skill": true
      },
      "answer_type": "expression"
    },
    {
      "problem_type_id": "expression_write_line_equation_from_point_slope",
      "proposed_problem_type_id": "expression_write_line_equation_from_point_slope",
      "display_name": "expression / write_line_equation_from_point_slope",
      "matched_example_ids": [
        4606
      ],
      "matched_example_count": 1,
      "unmatched_example_ids": [],
      "representative_example_id": 4606,
      "structural_features": [
        "single_choice"
      ],
      "answer_contract_proposal": {
        "choices_required": true,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": true,
        "source_has_choices": true,
        "answer_type": "expression",
        "answer_shape": "single_choice",
        "answer_semantics": "choice_label",
        "answer_equivalence": "exact_string",
        "equivalence_type": "exact_string",
        "checker": "equation_checker",
        "checker_key": "equation_checker",
        "presentation_mode": "",
        "selected_checker": "choice_label_checker",
        "checker_selection_reason": "line_equation_family",
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
            "line_equation"
          ],
          "required_math_objects": [
            "coordinate_point",
            "line_equation"
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
            "line_equation_reasoning"
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
              "id": "given_point_and_slope_find_point_slope_form",
              "label": "點斜式",
              "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
              "weight": 1.0,
              "enabled": true
            },
            {
              "id": "given_point_and_slope_find_slope_intercept_form",
              "label": "斜截式",
              "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
              "weight": 1.0,
              "enabled": true
            },
            {
              "id": "given_point_and_slope_find_general_form",
              "label": "一般式",
              "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "point_coordinates": {
              "x_min": -8,
              "x_max": 8,
              "y_min": -8,
              "y_max": 8,
              "integer_only": true
            },
            "slope": {
              "choices": [
                "integer",
                "simple_fraction"
              ],
              "weights": [
                0.65,
                0.35
              ],
              "integer_range": [
                -5,
                5
              ],
              "exclude_zero": true,
              "fraction_numerators": [
                1,
                2,
                3,
                -1,
                -2,
                -3
              ],
              "fraction_denominators": [
                2,
                3
              ]
            },
            "equation_form": {
              "choices": [
                "point_slope",
                "slope_intercept",
                "general"
              ],
              "weights": [
                0.34,
                0.33,
                0.33
              ]
            }
          },
          "variation_dimensions": [
            "point_coordinates",
            "slope_type",
            "equation_form",
            "integer_or_fraction_slope",
            "coefficient_normalization",
            "number_variation",
            "template_variant",
            "coordinate_sign_combination"
          ],
          "difficulty_controls": {
            "level_1": {
              "coordinate_range": [
                -5,
                5
              ],
              "integer_slope_only": true,
              "equation_form": "point_slope"
            },
            "level_2": {
              "coordinate_range": [
                -8,
                8
              ],
              "allow_fraction_slope": true
            },
            "level_3": {
              "allow_negative_slope": true,
              "require_general_form": true
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
            "slope is finite",
            "point coordinates are integers",
            "generated equation passes through the point",
            "generated equation has the requested slope",
            "equivalent forms normalize to same Ax + By + C = 0"
          ],
          "answer_shape": "linear_equation",
          "explanation_variants": [
            "point_slope_to_general",
            "slope_intercept_to_general"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "write_line_equation_from_point_slope"
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
          "problem_type_id": "equation_write_line_equation_from_point_slope_single_choice",
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
        "canonical_answer_schema": "single_choice"
      },
      "checker_key_proposal": "equation_checker",
      "equivalence_type_proposal": "exact_string",
      "answer_shape": "single_choice",
      "answer_semantics": "choice_label",
      "presentation_mode": "single_choice",
      "source_has_choices": true,
      "selected_checker": "choice_label_checker",
      "checker_selection_reason": "line_equation_family",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "ai_partial_unavailable_relaxed_tolerance"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "split_by_feature_signature",
      "feature_signature": [
        "equation",
        "write_line_equation_from_point_slope",
        "single_choice",
        [
          "line_equation_reasoning"
        ],
        [
          "coordinate_point",
          "line_equation"
        ],
        "line_equation"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "equation_write_line_equation_from_point_slope_single_choice",
        "skill_id": "vh_數學B1_PointSlopeForm",
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "display_name": "equation / write_line_equation_from_point_slope",
        "answer_format_hint": "A/B/C/D",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          4606
        ],
        "answer_contract": {
          "choices_required": true,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": true,
          "source_has_choices": true,
          "answer_type": "choice",
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
          ]
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "line_equation"
          ],
          "required_math_objects": [
            "coordinate_point",
            "line_equation"
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
            "line_equation_reasoning"
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
              "id": "given_point_and_slope_find_point_slope_form",
              "label": "點斜式",
              "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
              "weight": 1.0,
              "enabled": true
            },
            {
              "id": "given_point_and_slope_find_slope_intercept_form",
              "label": "斜截式",
              "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
              "weight": 1.0,
              "enabled": true
            },
            {
              "id": "given_point_and_slope_find_general_form",
              "label": "一般式",
              "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
              "weight": 1.0,
              "enabled": true
            }
          ],
          "parameter_schema": {
            "point_coordinates": {
              "x_min": -8,
              "x_max": 8,
              "y_min": -8,
              "y_max": 8,
              "integer_only": true
            },
            "slope": {
              "choices": [
                "integer",
                "simple_fraction"
              ],
              "weights": [
                0.65,
                0.35
              ],
              "integer_range": [
                -5,
                5
              ],
              "exclude_zero": true,
              "fraction_numerators": [
                1,
                2,
                3,
                -1,
                -2,
                -3
              ],
              "fraction_denominators": [
                2,
                3
              ]
            },
            "equation_form": {
              "choices": [
                "point_slope",
                "slope_intercept",
                "general"
              ],
              "weights": [
                0.34,
                0.33,
                0.33
              ]
            }
          },
          "variation_dimensions": [
            "point_coordinates",
            "slope_type",
            "equation_form",
            "integer_or_fraction_slope",
            "coefficient_normalization",
            "number_variation",
            "template_variant",
            "coordinate_sign_combination"
          ],
          "difficulty_controls": {
            "level_1": {
              "coordinate_range": [
                -5,
                5
              ],
              "integer_slope_only": true,
              "equation_form": "point_slope"
            },
            "level_2": {
              "coordinate_range": [
                -8,
                8
              ],
              "allow_fraction_slope": true
            },
            "level_3": {
              "allow_negative_slope": true,
              "require_general_form": true
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
            "slope is finite",
            "point coordinates are integers",
            "generated equation passes through the point",
            "generated equation has the requested slope",
            "equivalent forms normalize to same Ax + By + C = 0"
          ],
          "answer_shape": "linear_equation",
          "explanation_variants": [
            "point_slope_to_general",
            "slope_intercept_to_general"
          ],
          "sampling_strategy": "weighted_random",
          "template_families": [
            "write_line_equation_from_point_slope"
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
          "problem_type_id": "equation_write_line_equation_from_point_slope_single_choice",
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
        "grouping_reason": "split_by_feature_signature",
        "feature_signature": [
          "equation",
          "write_line_equation_from_point_slope",
          "single_choice",
          [
            "line_equation_reasoning"
          ],
          [
            "coordinate_point",
            "line_equation"
          ],
          "line_equation"
        ],
        "canonical_base_problem_type_id": "equation_write_line_equation_from_point_slope_single_choice",
        "value_type_prefix": "",
        "_resolved_template_slot": ""
      },
      "generator_readiness": "runtime_ready_with_warning",
      "usable_for_phase3": true,
      "template_slot": "",
      "canonical_base_problem_type_id": "equation_write_line_equation_from_point_slope_single_choice",
      "value_type_prefix": "",
      "subskill_id": "write_line_equation_from_point_slope",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0833,
        "source_problem_type_score": 0.0278,
        "task_consistent_with_skill": true
      },
      "answer_type": "choice"
    }
  ],
  "per_example_classification": [
    {
      "example_id": 4549,
      "detected_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "example_feature": {
        "source_example_id": 4549,
        "question_text": "(1)試求過點$\\left( 2,-3 \\right)$，且斜率為$-\\frac{1}{2}$的直線方程式。\n(2)試求過點$\\left( -1,4 \\right)$，且斜率為2的直線方程式。",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "expression",
        "answer_shape": "linear_equation",
        "checker": "equation_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "line_equation",
          "two_coordinate_points"
        ],
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "reasoning_type": [
          "line_equation_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "write_line_equation_from_point_slope",
        "classifier_source": "line_equation_routing",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "rule_target_task": "write_line_equation_from_point_slope",
          "rule_task_family": "line_equation_family",
          "rule_confidence": 0.7,
          "final_target_task": "write_line_equation_from_point_slope",
          "final_task_family": "line_equation_family",
          "classifier_source": "line_equation_routing",
          "classification_decision": "forced_by_line_equation_routing",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
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
          "selected_subskill": "write_line_equation_from_point_slope",
          "selected_problem_type": "write_line_equation_from_point_slope",
          "candidate_source": "line_equation_routing",
          "skill_scope_trusted": true,
          "target_task": "write_line_equation_from_point_slope",
          "task_family": "line_equation_family",
          "math_objects": [
            "coordinate_point",
            "line_equation",
            "two_coordinate_points"
          ],
          "answer_type": "equation",
          "answer_shape": "linear_equation",
          "classification_confidence": "high",
          "source_type": "worked_example",
          "example_label": "例題1",
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
          "source_type": "worked_example",
          "example_label": "例題1",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": 1,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "classification_confidence": "high",
        "stem_concept": "line_equation",
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "equivalence_type": "exact_string",
        "checker_key": "equation_checker"
      },
      "answer_shape": "linear_equation",
      "classification_confidence": "high",
      "classification_reason": "line_equation_routing",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "rule_target_task": "write_line_equation_from_point_slope",
        "rule_task_family": "line_equation_family",
        "rule_confidence": 0.7,
        "final_target_task": "write_line_equation_from_point_slope",
        "final_task_family": "line_equation_family",
        "classifier_source": "line_equation_routing",
        "classification_decision": "forced_by_line_equation_routing",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
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
        "selected_subskill": "write_line_equation_from_point_slope",
        "selected_problem_type": "write_line_equation_from_point_slope",
        "candidate_source": "line_equation_routing",
        "skill_scope_trusted": true,
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "math_objects": [
          "coordinate_point",
          "line_equation",
          "two_coordinate_points"
        ],
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "classification_confidence": "high",
        "source_type": "worked_example",
        "example_label": "例題1",
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
      "subskill_id": "write_line_equation_from_point_slope",
      "classification_source": "line_equation_routing",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "expression",
      "equivalence_type": "exact_string",
      "checker_key": "equation_checker",
      "alignment_score": 0.8
    },
    {
      "example_id": 4550,
      "detected_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "example_feature": {
        "source_example_id": 4550,
        "question_text": "如圖，已知平面上兩鄉鎮的位置為、，今兩鄉鎮市民希望在鐵路沿線上設立一車站，此車站位於與兩鄉鎮距離相同的直線道路上，試求此車站所在的直線道路方程式。",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "expression",
        "answer_shape": "linear_equation",
        "checker": "equation_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "line_equation"
        ],
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "reasoning_type": [
          "line_equation_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "write_line_equation_from_point_slope",
        "classifier_source": "line_equation_routing",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "rule_target_task": "write_line_equation_from_point_slope",
          "rule_task_family": "line_equation_family",
          "rule_confidence": 0.7,
          "final_target_task": "write_line_equation_from_point_slope",
          "final_task_family": "line_equation_family",
          "classifier_source": "line_equation_routing",
          "classification_decision": "forced_by_line_equation_routing",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
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
          "selected_subskill": "write_line_equation_from_point_slope",
          "selected_problem_type": "write_line_equation_from_point_slope",
          "candidate_source": "line_equation_routing",
          "skill_scope_trusted": true,
          "target_task": "write_line_equation_from_point_slope",
          "task_family": "line_equation_family",
          "math_objects": [
            "line_equation"
          ],
          "answer_type": "equation",
          "answer_shape": "linear_equation",
          "classification_confidence": "medium",
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
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
        },
        "source_structure_context": {
          "source_type": "worked_example",
          "example_label": "例題2",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": 2,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "classification_confidence": "medium",
        "stem_concept": "line_equation",
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "equivalence_type": "exact_string",
        "checker_key": "equation_checker"
      },
      "answer_shape": "linear_equation",
      "classification_confidence": "high",
      "classification_reason": "line_equation_routing",
      "risk_flags": [
        "requires_human_action"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "rule_target_task": "write_line_equation_from_point_slope",
        "rule_task_family": "line_equation_family",
        "rule_confidence": 0.7,
        "final_target_task": "write_line_equation_from_point_slope",
        "final_task_family": "line_equation_family",
        "classifier_source": "line_equation_routing",
        "classification_decision": "forced_by_line_equation_routing",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
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
        "selected_subskill": "write_line_equation_from_point_slope",
        "selected_problem_type": "write_line_equation_from_point_slope",
        "candidate_source": "line_equation_routing",
        "skill_scope_trusted": true,
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "math_objects": [
          "line_equation"
        ],
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "classification_confidence": "medium",
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
        "possible_mixed_source_context": false,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "write_line_equation_from_point_slope",
      "classification_source": "line_equation_routing",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "expression",
      "equivalence_type": "exact_string",
      "checker_key": "equation_checker",
      "alignment_score": 0.8
    },
    {
      "example_id": 4551,
      "detected_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "example_feature": {
        "source_example_id": 4551,
        "question_text": "試求通過$A\\left( 3,-1 \\right)$、$B\\left( 2,1 \\right)$兩點的直線方程式。",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "expression",
        "answer_shape": "linear_equation",
        "checker": "equation_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "line_equation",
          "two_coordinate_points"
        ],
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "reasoning_type": [
          "line_equation_reasoning"
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
        "target": "write_line_equation_from_point_slope",
        "classifier_source": "line_equation_routing",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "rule_target_task": "write_line_equation_from_point_slope",
          "rule_task_family": "line_equation_family",
          "rule_confidence": 0.7,
          "final_target_task": "write_line_equation_from_point_slope",
          "final_task_family": "line_equation_family",
          "classifier_source": "line_equation_routing",
          "classification_decision": "forced_by_line_equation_routing",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
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
          "selected_subskill": "write_line_equation_from_point_slope",
          "selected_problem_type": "write_line_equation_from_point_slope",
          "candidate_source": "line_equation_routing",
          "skill_scope_trusted": true,
          "target_task": "write_line_equation_from_point_slope",
          "task_family": "line_equation_family",
          "math_objects": [
            "coordinate_point",
            "line_equation",
            "two_coordinate_points"
          ],
          "answer_type": "equation",
          "answer_shape": "linear_equation",
          "classification_confidence": "high",
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
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
        },
        "source_structure_context": {
          "source_type": "worked_example",
          "example_label": "例題3",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": 3,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "classification_confidence": "high",
        "stem_concept": "line_equation",
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "equivalence_type": "exact_string",
        "checker_key": "equation_checker"
      },
      "answer_shape": "linear_equation",
      "classification_confidence": "high",
      "classification_reason": "line_equation_routing",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "rule_target_task": "write_line_equation_from_point_slope",
        "rule_task_family": "line_equation_family",
        "rule_confidence": 0.7,
        "final_target_task": "write_line_equation_from_point_slope",
        "final_task_family": "line_equation_family",
        "classifier_source": "line_equation_routing",
        "classification_decision": "forced_by_line_equation_routing",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
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
        "selected_subskill": "write_line_equation_from_point_slope",
        "selected_problem_type": "write_line_equation_from_point_slope",
        "candidate_source": "line_equation_routing",
        "skill_scope_trusted": true,
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "math_objects": [
          "coordinate_point",
          "line_equation",
          "two_coordinate_points"
        ],
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "classification_confidence": "high",
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
        "possible_mixed_source_context": false,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "write_line_equation_from_point_slope",
      "classification_source": "line_equation_routing",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "expression",
      "equivalence_type": "exact_string",
      "checker_key": "equation_checker",
      "alignment_score": 0.8
    },
    {
      "example_id": 4552,
      "detected_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "example_feature": {
        "source_example_id": 4552,
        "question_text": "某農夫有塊三角形農地ABC，如圖所示，在平面上的坐標位置為$A\\left( 8,-4 \\right)$、$B\\left( 4,2 \\right)$、$C\\left( 2,-2 \\right)$。今農夫欲將農地沿著過B點的直線平均分給兩個兒子耕種，試求平分農地的直線方程式為何？",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "expression",
        "answer_shape": "linear_equation",
        "checker": "equation_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "line_equation",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "reasoning_type": [
          "line_equation_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "A",
          "B",
          "C"
        ],
        "givens": [
          "A",
          "B",
          "C"
        ],
        "target": "write_line_equation_from_point_slope",
        "classifier_source": "line_equation_routing",
        "math_meta_tags": [
          "[Task: Applied_Context]"
        ],
        "forced_target_task": "applied_quadratic_inequality_problem",
        "meta_answer_format_hint": "interval",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "rule_target_task": "applied_quadratic_inequality_problem",
          "rule_task_family": "quadratic_inequality_family",
          "rule_confidence": 0.7,
          "final_target_task": "write_line_equation_from_point_slope",
          "final_task_family": "line_equation_family",
          "classifier_source": "line_equation_routing",
          "classification_decision": "forced_by_line_equation_routing",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
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
          "outsider_candidates": [],
          "selected_subskill": "write_line_equation_from_point_slope",
          "selected_problem_type": "write_line_equation_from_point_slope",
          "candidate_source": "line_equation_routing",
          "skill_scope_trusted": true,
          "target_task": "write_line_equation_from_point_slope",
          "task_family": "line_equation_family",
          "math_objects": [
            "coordinate_point",
            "line_equation",
            "three_coordinate_points",
            "triangle",
            "two_coordinate_points"
          ],
          "answer_type": "equation",
          "answer_shape": "linear_equation",
          "classification_confidence": "high",
          "source_type": "worked_example",
          "example_label": "例題4",
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
          "source_type": "worked_example",
          "example_label": "例題4",
          "practice_label": "",
          "linked_example": "",
          "section_order": 0,
          "example_number": 4,
          "practice_number": null,
          "nearby_worked_examples": [
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
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
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "classification_confidence": "high",
        "stem_concept": "line_equation",
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "equivalence_type": "exact_string",
        "checker_key": "equation_checker"
      },
      "answer_shape": "linear_equation",
      "classification_confidence": "high",
      "classification_reason": "line_equation_routing",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "rule_target_task": "applied_quadratic_inequality_problem",
        "rule_task_family": "quadratic_inequality_family",
        "rule_confidence": 0.7,
        "final_target_task": "write_line_equation_from_point_slope",
        "final_task_family": "line_equation_family",
        "classifier_source": "line_equation_routing",
        "classification_decision": "forced_by_line_equation_routing",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
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
        "outsider_candidates": [],
        "selected_subskill": "write_line_equation_from_point_slope",
        "selected_problem_type": "write_line_equation_from_point_slope",
        "candidate_source": "line_equation_routing",
        "skill_scope_trusted": true,
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "math_objects": [
          "coordinate_point",
          "line_equation",
          "three_coordinate_points",
          "triangle",
          "two_coordinate_points"
        ],
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "classification_confidence": "high",
        "source_type": "worked_example",
        "example_label": "例題4",
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
      "subskill_id": "write_line_equation_from_point_slope",
      "classification_source": "line_equation_routing",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "expression",
      "equivalence_type": "exact_string",
      "checker_key": "equation_checker",
      "alignment_score": 0.8
    },
    {
      "example_id": 4540,
      "detected_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "example_feature": {
        "source_example_id": 4540,
        "question_text": "試求過點$\\left( 2,-1 \\right)$且斜率為$\\frac{1}{2}$的直線方程式。",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "expression",
        "answer_shape": "linear_equation",
        "checker": "equation_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "line_equation"
        ],
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "reasoning_type": [
          "line_equation_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "write_line_equation_from_point_slope",
        "classifier_source": "line_equation_routing",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "rule_target_task": "write_line_equation_from_point_slope",
          "rule_task_family": "line_equation_family",
          "rule_confidence": 0.7,
          "final_target_task": "write_line_equation_from_point_slope",
          "final_task_family": "line_equation_family",
          "classifier_source": "line_equation_routing",
          "classification_decision": "forced_by_line_equation_routing",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
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
          "selected_subskill": "write_line_equation_from_point_slope",
          "selected_problem_type": "write_line_equation_from_point_slope",
          "candidate_source": "line_equation_routing",
          "skill_scope_trusted": true,
          "target_task": "write_line_equation_from_point_slope",
          "task_family": "line_equation_family",
          "math_objects": [
            "coordinate_point",
            "line_equation"
          ],
          "answer_type": "equation",
          "answer_shape": "linear_equation",
          "classification_confidence": "high",
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
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "classification_confidence": "high",
        "stem_concept": "line_equation",
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "equivalence_type": "exact_string",
        "checker_key": "equation_checker"
      },
      "answer_shape": "linear_equation",
      "classification_confidence": "high",
      "classification_reason": "line_equation_routing",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "rule_target_task": "write_line_equation_from_point_slope",
        "rule_task_family": "line_equation_family",
        "rule_confidence": 0.7,
        "final_target_task": "write_line_equation_from_point_slope",
        "final_task_family": "line_equation_family",
        "classifier_source": "line_equation_routing",
        "classification_decision": "forced_by_line_equation_routing",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
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
        "selected_subskill": "write_line_equation_from_point_slope",
        "selected_problem_type": "write_line_equation_from_point_slope",
        "candidate_source": "line_equation_routing",
        "skill_scope_trusted": true,
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "math_objects": [
          "coordinate_point",
          "line_equation"
        ],
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "classification_confidence": "high",
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
      "subskill_id": "write_line_equation_from_point_slope",
      "classification_source": "line_equation_routing",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "expression",
      "equivalence_type": "exact_string",
      "checker_key": "equation_checker",
      "alignment_score": 0.8
    },
    {
      "example_id": 4541,
      "detected_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "example_feature": {
        "source_example_id": 4541,
        "question_text": "試求過點$\\left( 1,-2 \\right)$且斜率為−3的直線方程式。",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "expression",
        "answer_shape": "linear_equation",
        "checker": "equation_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "line_equation"
        ],
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "reasoning_type": [
          "line_equation_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "write_line_equation_from_point_slope",
        "classifier_source": "line_equation_routing",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "rule_target_task": "write_line_equation_from_point_slope",
          "rule_task_family": "line_equation_family",
          "rule_confidence": 0.7,
          "final_target_task": "write_line_equation_from_point_slope",
          "final_task_family": "line_equation_family",
          "classifier_source": "line_equation_routing",
          "classification_decision": "forced_by_line_equation_routing",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
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
          "selected_subskill": "write_line_equation_from_point_slope",
          "selected_problem_type": "write_line_equation_from_point_slope",
          "candidate_source": "line_equation_routing",
          "skill_scope_trusted": true,
          "target_task": "write_line_equation_from_point_slope",
          "task_family": "line_equation_family",
          "math_objects": [
            "line_equation"
          ],
          "answer_type": "equation",
          "answer_shape": "linear_equation",
          "classification_confidence": "high",
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
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "classification_confidence": "high",
        "stem_concept": "line_equation",
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "equivalence_type": "exact_string",
        "checker_key": "equation_checker"
      },
      "answer_shape": "linear_equation",
      "classification_confidence": "high",
      "classification_reason": "line_equation_routing",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "rule_target_task": "write_line_equation_from_point_slope",
        "rule_task_family": "line_equation_family",
        "rule_confidence": 0.7,
        "final_target_task": "write_line_equation_from_point_slope",
        "final_task_family": "line_equation_family",
        "classifier_source": "line_equation_routing",
        "classification_decision": "forced_by_line_equation_routing",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
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
        "selected_subskill": "write_line_equation_from_point_slope",
        "selected_problem_type": "write_line_equation_from_point_slope",
        "candidate_source": "line_equation_routing",
        "skill_scope_trusted": true,
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "math_objects": [
          "line_equation"
        ],
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "classification_confidence": "high",
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
      "subskill_id": "write_line_equation_from_point_slope",
      "classification_source": "line_equation_routing",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "expression",
      "equivalence_type": "exact_string",
      "checker_key": "equation_checker",
      "alignment_score": 0.8
    },
    {
      "example_id": 4542,
      "detected_problem_type_id": "short_answer_compute_distance_between_two_points_short_answer",
      "example_feature": {
        "source_example_id": 4542,
        "question_text": "設$A\\left( -1,1 \\right)$、$B\\left( 3,-1 \\right)$，求$\\overline{AB}$之垂直平分線方程式。",
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
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              }
            },
            {
              "candidate_id": "C2",
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
            "C2"
          ],
          "selected_subskill": "compute_distance_between_two_points",
          "selected_problem_type": "compute_distance_between_two_points",
          "candidate_source": "needs_review",
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
          "answer_type": "short_answer",
          "answer_shape": "text_short",
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
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "requires_human_action"
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
        "rule_target_task": "compute_distance_between_two_points",
        "rule_task_family": "distance_between_two_points_family",
        "rule_confidence": 0.55,
        "final_target_task": "compute_distance_between_two_points",
        "final_task_family": "distance_between_two_points_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
                ]
              }
            }
          },
          {
            "candidate_id": "C2",
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
          "C2"
        ],
        "selected_subskill": "compute_distance_between_two_points",
        "selected_problem_type": "compute_distance_between_two_points",
        "candidate_source": "needs_review",
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
        "answer_type": "short_answer",
        "answer_shape": "text_short",
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
      "subskill_id": "compute_distance_between_two_points",
      "classification_source": "rule_fallback_ai_unavailable",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4543,
      "detected_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "example_feature": {
        "source_example_id": 4543,
        "question_text": "試求過點$A\\left( 2,-1 \\right)$與$B\\left( 0,3 \\right)$之直線方程式。",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "expression",
        "answer_shape": "linear_equation",
        "checker": "equation_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "line_equation",
          "two_coordinate_points"
        ],
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "reasoning_type": [
          "line_equation_reasoning"
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
        "target": "write_line_equation_from_point_slope",
        "classifier_source": "line_equation_routing",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "rule_target_task": "write_line_equation_from_point_slope",
          "rule_task_family": "line_equation_family",
          "rule_confidence": 0.7,
          "final_target_task": "write_line_equation_from_point_slope",
          "final_task_family": "line_equation_family",
          "classifier_source": "line_equation_routing",
          "classification_decision": "forced_by_line_equation_routing",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
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
          "selected_subskill": "write_line_equation_from_point_slope",
          "selected_problem_type": "write_line_equation_from_point_slope",
          "candidate_source": "line_equation_routing",
          "skill_scope_trusted": true,
          "target_task": "write_line_equation_from_point_slope",
          "task_family": "line_equation_family",
          "math_objects": [
            "coordinate_point",
            "line_equation",
            "two_coordinate_points"
          ],
          "answer_type": "equation",
          "answer_shape": "linear_equation",
          "classification_confidence": "high",
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
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "classification_confidence": "high",
        "stem_concept": "line_equation",
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "equivalence_type": "exact_string",
        "checker_key": "equation_checker"
      },
      "answer_shape": "linear_equation",
      "classification_confidence": "high",
      "classification_reason": "line_equation_routing",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "rule_target_task": "write_line_equation_from_point_slope",
        "rule_task_family": "line_equation_family",
        "rule_confidence": 0.7,
        "final_target_task": "write_line_equation_from_point_slope",
        "final_task_family": "line_equation_family",
        "classifier_source": "line_equation_routing",
        "classification_decision": "forced_by_line_equation_routing",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
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
        "selected_subskill": "write_line_equation_from_point_slope",
        "selected_problem_type": "write_line_equation_from_point_slope",
        "candidate_source": "line_equation_routing",
        "skill_scope_trusted": true,
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "math_objects": [
          "coordinate_point",
          "line_equation",
          "two_coordinate_points"
        ],
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "classification_confidence": "high",
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
      "subskill_id": "write_line_equation_from_point_slope",
      "classification_source": "line_equation_routing",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "expression",
      "equivalence_type": "exact_string",
      "checker_key": "equation_checker",
      "alignment_score": 0.8
    },
    {
      "example_id": 4546,
      "detected_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "example_feature": {
        "source_example_id": 4546,
        "question_text": "試求斜率為3且x截距為5的直線方程式。",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "expression",
        "answer_shape": "linear_equation",
        "checker": "equation_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "line_equation"
        ],
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "reasoning_type": [
          "line_equation_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "write_line_equation_from_point_slope",
        "classifier_source": "line_equation_routing",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "rule_target_task": "write_line_equation_from_point_slope",
          "rule_task_family": "line_equation_family",
          "rule_confidence": 0.7,
          "final_target_task": "write_line_equation_from_point_slope",
          "final_task_family": "line_equation_family",
          "classifier_source": "line_equation_routing",
          "classification_decision": "forced_by_line_equation_routing",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
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
          "selected_subskill": "write_line_equation_from_point_slope",
          "selected_problem_type": "write_line_equation_from_point_slope",
          "candidate_source": "line_equation_routing",
          "skill_scope_trusted": true,
          "target_task": "write_line_equation_from_point_slope",
          "task_family": "line_equation_family",
          "math_objects": [
            "line_equation"
          ],
          "answer_type": "equation",
          "answer_shape": "linear_equation",
          "classification_confidence": "high",
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
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "classification_confidence": "high",
        "stem_concept": "line_equation",
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "equivalence_type": "exact_string",
        "checker_key": "equation_checker"
      },
      "answer_shape": "linear_equation",
      "classification_confidence": "high",
      "classification_reason": "line_equation_routing",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "rule_target_task": "write_line_equation_from_point_slope",
        "rule_task_family": "line_equation_family",
        "rule_confidence": 0.7,
        "final_target_task": "write_line_equation_from_point_slope",
        "final_task_family": "line_equation_family",
        "classifier_source": "line_equation_routing",
        "classification_decision": "forced_by_line_equation_routing",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
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
        "selected_subskill": "write_line_equation_from_point_slope",
        "selected_problem_type": "write_line_equation_from_point_slope",
        "candidate_source": "line_equation_routing",
        "skill_scope_trusted": true,
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "math_objects": [
          "line_equation"
        ],
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "classification_confidence": "high",
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
      "subskill_id": "write_line_equation_from_point_slope",
      "classification_source": "line_equation_routing",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "expression",
      "equivalence_type": "exact_string",
      "checker_key": "equation_checker",
      "alignment_score": 0.8
    },
    {
      "example_id": 4556,
      "detected_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "example_feature": {
        "source_example_id": 4556,
        "question_text": "(1)試求過點$\\left( -5,1 \\right)$，且斜率為3的直線方程式。\n(2)試求過點$\\left( 1,-3 \\right)$，且斜率為$-\\frac{2}{3}$的直線方程式。.",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "expression",
        "answer_shape": "linear_equation",
        "checker": "equation_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "line_equation",
          "two_coordinate_points"
        ],
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "reasoning_type": [
          "line_equation_reasoning"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "write_line_equation_from_point_slope",
        "classifier_source": "line_equation_routing",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "rule_target_task": "write_line_equation_from_point_slope",
          "rule_task_family": "line_equation_family",
          "rule_confidence": 0.7,
          "final_target_task": "write_line_equation_from_point_slope",
          "final_task_family": "line_equation_family",
          "classifier_source": "line_equation_routing",
          "classification_decision": "forced_by_line_equation_routing",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
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
          "selected_subskill": "write_line_equation_from_point_slope",
          "selected_problem_type": "write_line_equation_from_point_slope",
          "candidate_source": "line_equation_routing",
          "skill_scope_trusted": true,
          "target_task": "write_line_equation_from_point_slope",
          "task_family": "line_equation_family",
          "math_objects": [
            "coordinate_point",
            "line_equation",
            "two_coordinate_points"
          ],
          "answer_type": "equation",
          "answer_shape": "linear_equation",
          "classification_confidence": "high",
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
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
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
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "classification_confidence": "high",
        "stem_concept": "line_equation",
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "equivalence_type": "exact_string",
        "checker_key": "equation_checker"
      },
      "answer_shape": "linear_equation",
      "classification_confidence": "high",
      "classification_reason": "line_equation_routing",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "rule_target_task": "write_line_equation_from_point_slope",
        "rule_task_family": "line_equation_family",
        "rule_confidence": 0.7,
        "final_target_task": "write_line_equation_from_point_slope",
        "final_task_family": "line_equation_family",
        "classifier_source": "line_equation_routing",
        "classification_decision": "forced_by_line_equation_routing",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
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
        "selected_subskill": "write_line_equation_from_point_slope",
        "selected_problem_type": "write_line_equation_from_point_slope",
        "candidate_source": "line_equation_routing",
        "skill_scope_trusted": true,
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "math_objects": [
          "coordinate_point",
          "line_equation",
          "two_coordinate_points"
        ],
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "classification_confidence": "high",
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
        "possible_mixed_source_context": false,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "write_line_equation_from_point_slope",
      "classification_source": "line_equation_routing",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "expression",
      "equivalence_type": "exact_string",
      "checker_key": "equation_checker",
      "alignment_score": 0.8
    },
    {
      "example_id": 4557,
      "detected_problem_type_id": "short_answer_compute_numeric_short_answer",
      "example_feature": {
        "source_example_id": 4557,
        "question_text": "設、，試求之垂直平分線方程式。",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [],
        "givens": [],
        "target": "compute_numeric",
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
          "final_target_task": "compute_numeric",
          "final_task_family": "generic_numeric_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
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
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
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
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "requires_human_action",
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
        "final_target_task": "compute_numeric",
        "final_task_family": "generic_numeric_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
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
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
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
      "subskill_id": "compute_numeric",
      "classification_source": "rule_fallback_ai_unavailable",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4560,
      "detected_problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
      "example_feature": {
        "source_example_id": 4560,
        "question_text": "試求通過$A\\left( -3,1 \\right)$、$B\\left( 2,4 \\right)$兩點的直線方程式。",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "expression",
        "answer_shape": "linear_equation",
        "checker": "equation_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "line_equation",
          "two_coordinate_points"
        ],
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "reasoning_type": [
          "line_equation_reasoning"
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
        "target": "write_line_equation_from_point_slope",
        "classifier_source": "line_equation_routing",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "rule_target_task": "write_line_equation_from_point_slope",
          "rule_task_family": "line_equation_family",
          "rule_confidence": 0.7,
          "final_target_task": "write_line_equation_from_point_slope",
          "final_task_family": "line_equation_family",
          "classifier_source": "line_equation_routing",
          "classification_decision": "forced_by_line_equation_routing",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": false,
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
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
          "selected_subskill": "write_line_equation_from_point_slope",
          "selected_problem_type": "write_line_equation_from_point_slope",
          "candidate_source": "line_equation_routing",
          "skill_scope_trusted": true,
          "target_task": "write_line_equation_from_point_slope",
          "task_family": "line_equation_family",
          "math_objects": [
            "coordinate_point",
            "line_equation",
            "two_coordinate_points"
          ],
          "answer_type": "equation",
          "answer_shape": "linear_equation",
          "classification_confidence": "high",
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
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
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
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "classification_confidence": "high",
        "stem_concept": "line_equation",
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "equivalence_type": "exact_string",
        "checker_key": "equation_checker"
      },
      "answer_shape": "linear_equation",
      "classification_confidence": "high",
      "classification_reason": "line_equation_routing",
      "risk_flags": [],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "rule_target_task": "write_line_equation_from_point_slope",
        "rule_task_family": "line_equation_family",
        "rule_confidence": 0.7,
        "final_target_task": "write_line_equation_from_point_slope",
        "final_task_family": "line_equation_family",
        "classifier_source": "line_equation_routing",
        "classification_decision": "forced_by_line_equation_routing",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": false,
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
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
        "selected_subskill": "write_line_equation_from_point_slope",
        "selected_problem_type": "write_line_equation_from_point_slope",
        "candidate_source": "line_equation_routing",
        "skill_scope_trusted": true,
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "math_objects": [
          "coordinate_point",
          "line_equation",
          "two_coordinate_points"
        ],
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "classification_confidence": "high",
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
        "possible_mixed_source_context": false,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "write_line_equation_from_point_slope",
      "classification_source": "line_equation_routing",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "expression",
      "equivalence_type": "exact_string",
      "checker_key": "equation_checker",
      "alignment_score": 0.8
    },
    {
      "example_id": 4561,
      "detected_problem_type_id": "short_answer_quadratic_vertex_form_properties_short_answer",
      "example_feature": {
        "source_example_id": 4561,
        "question_text": "已知△ABC三頂點坐標分別為、、$C\\left( -2,-4 \\right)$，試求$\\overline{BC}$邊上之中線方程式。",
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
          "quadratic_equation",
          "quadratic_vertex",
          "quadratic_vertex_form",
          "three_coordinate_points",
          "triangle"
        ],
        "target_task": "quadratic_vertex_form_properties",
        "task_family": "quadratic_function_graph_family",
        "reasoning_type": [
          "quadratic_vertex_form_properties"
        ],
        "required_derivation": true,
        "source_quality_issues": [],
        "source_quality_reject": false,
        "candidate_only": false,
        "variables": [
          "C"
        ],
        "givens": [
          "C"
        ],
        "target": "quadratic_vertex_form_properties",
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
          "rule_target_task": "quadratic_vertex_form_properties",
          "rule_task_family": "quadratic_function_graph_family",
          "rule_confidence": 0.5,
          "final_target_task": "quadratic_vertex_form_properties",
          "final_task_family": "quadratic_function_graph_family",
          "classifier_source": "rule_fallback_ai_unavailable",
          "classification_decision": "",
          "conflict_reason": "ai_api_key_missing",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "ai_notes": "",
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              }
            },
            {
              "candidate_id": "C2",
              "target_task": "quadratic_vertex_form_properties",
              "task_family": "quadratic_function_graph_family",
              "problem_type_id": "quadratic_vertex_form_properties",
              "label": "quadratic_vertex_form_properties",
              "candidate_source": "outsider",
              "in_anchor_scope": false,
              "answer_type": "single_choice",
              "answer_shape": "choice_label",
              "math_objects": [
                "quadratic_equation",
                "quadratic_vertex_form"
              ],
              "checker_key": "choice_label_checker",
              "equivalence_type": "choice_label",
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
                  "quadratic_vertex_form_properties"
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
          "selected_subskill": "quadratic_vertex_form_properties",
          "selected_problem_type": "quadratic_vertex_form_properties",
          "candidate_source": "needs_review",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "quadratic_vertex_form_properties",
          "task_family": "quadratic_function_graph_family",
          "math_objects": [
            "coordinate_point",
            "quadratic_equation",
            "quadratic_vertex",
            "quadratic_vertex_form",
            "three_coordinate_points",
            "triangle"
          ],
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "source_type": "in_class_practice",
          "example_label": "",
          "practice_label": "隨堂練習4",
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
          "practice_label": "隨堂練習4",
          "linked_example": "",
          "section_order": 0,
          "example_number": null,
          "practice_number": 4,
          "nearby_worked_examples": [
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "unresolved_within_current_skill": true,
        "pending_problem_type_induction": true,
        "requires_human_rule_pack": true,
        "requires_human_action": false,
        "unresolved_reason": "semantic_score_zero_within_current_skill",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
        "requires_human_action"
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
        "rule_target_task": "quadratic_vertex_form_properties",
        "rule_task_family": "quadratic_function_graph_family",
        "rule_confidence": 0.5,
        "final_target_task": "quadratic_vertex_form_properties",
        "final_task_family": "quadratic_function_graph_family",
        "classifier_source": "rule_fallback_ai_unavailable",
        "classification_decision": "",
        "conflict_reason": "ai_api_key_missing",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "ai_notes": "",
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
                ]
              }
            }
          },
          {
            "candidate_id": "C2",
            "target_task": "quadratic_vertex_form_properties",
            "task_family": "quadratic_function_graph_family",
            "problem_type_id": "quadratic_vertex_form_properties",
            "label": "quadratic_vertex_form_properties",
            "candidate_source": "outsider",
            "in_anchor_scope": false,
            "answer_type": "single_choice",
            "answer_shape": "choice_label",
            "math_objects": [
              "quadratic_equation",
              "quadratic_vertex_form"
            ],
            "checker_key": "choice_label_checker",
            "equivalence_type": "choice_label",
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
                "quadratic_vertex_form_properties"
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
        "selected_subskill": "quadratic_vertex_form_properties",
        "selected_problem_type": "quadratic_vertex_form_properties",
        "candidate_source": "needs_review",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "quadratic_vertex_form_properties",
        "task_family": "quadratic_function_graph_family",
        "math_objects": [
          "coordinate_point",
          "quadratic_equation",
          "quadratic_vertex",
          "quadratic_vertex_form",
          "three_coordinate_points",
          "triangle"
        ],
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "source_type": "in_class_practice",
        "example_label": "",
        "practice_label": "隨堂練習4",
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
      "subskill_id": "quadratic_vertex_form_properties",
      "classification_source": "rule_fallback_ai_unavailable",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "semantic_score_zero_within_current_skill",
      "requires_human_rule_pack": true,
      "induction_eligibility": "eligible",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4606,
      "detected_problem_type_id": "equation_write_line_equation_from_point_slope_single_choice",
      "example_feature": {
        "source_example_id": 4606,
        "question_text": "已知a、b為實數，若直線ax + by + 2 = 0通過點${{k}_{1}}$且斜率為$\\frac{2}{3}$，則a + b = (A) −3 (B) −1 (C) 1 (D) 3。",
        "answer": "A",
        "choices": [
          "−3",
          "−1",
          "1",
          "3。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "expression",
        "answer_shape": "linear_equation",
        "checker": "equation_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "line_equation"
        ],
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "reasoning_type": [
          "line_equation_reasoning"
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
          "b",
          "k"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "b",
          "k"
        ],
        "target": "write_line_equation_from_point_slope",
        "classifier_source": "line_equation_routing",
        "math_meta_tags": [],
        "forced_target_task": "",
        "meta_answer_format_hint": "",
        "semantic_classification": {
          "ai_target_task": "",
          "ai_task_family": "",
          "ai_confidence": 0.0,
          "rule_target_task": "write_line_equation_from_point_slope",
          "rule_task_family": "line_equation_family",
          "rule_confidence": 0.7,
          "final_target_task": "write_line_equation_from_point_slope",
          "final_task_family": "line_equation_family",
          "classifier_source": "line_equation_routing",
          "classification_decision": "forced_by_line_equation_routing",
          "conflict_reason": "",
          "source_mapping_warning": "",
          "requires_human_action": true,
          "skill_scoped_candidates": [
            {
              "candidate_id": "C1",
              "target_task": "write_line_equation_from_point_slope",
              "task_family": "line_equation_family",
              "problem_type_id": "write_line_equation_from_point_slope",
              "label": "write_line_equation_from_point_slope",
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
                    "id": "given_point_and_slope_find_point_slope_form",
                    "label": "點斜式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_slope_intercept_form",
                    "label": "斜截式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                    "weight": 1.0,
                    "enabled": true
                  },
                  {
                    "id": "given_point_and_slope_find_general_form",
                    "label": "一般式",
                    "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                    "weight": 1.0,
                    "enabled": true
                  }
                ],
                "parameter_schema": {
                  "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": true
                  },
                  "slope": {
                    "choices": [
                      "integer",
                      "simple_fraction"
                    ],
                    "weights": [
                      0.65,
                      0.35
                    ],
                    "integer_range": [
                      -5,
                      5
                    ],
                    "exclude_zero": true,
                    "fraction_numerators": [
                      1,
                      2,
                      3,
                      -1,
                      -2,
                      -3
                    ],
                    "fraction_denominators": [
                      2,
                      3
                    ]
                  },
                  "equation_form": {
                    "choices": [
                      "point_slope",
                      "slope_intercept",
                      "general"
                    ],
                    "weights": [
                      0.34,
                      0.33,
                      0.33
                    ]
                  }
                },
                "variation_dimensions": [
                  "point_coordinates",
                  "slope_type",
                  "equation_form",
                  "integer_or_fraction_slope",
                  "coefficient_normalization"
                ],
                "difficulty_controls": {
                  "level_1": {
                    "coordinate_range": [
                      -5,
                      5
                    ],
                    "integer_slope_only": true,
                    "equation_form": "point_slope"
                  },
                  "level_2": {
                    "coordinate_range": [
                      -8,
                      8
                    ],
                    "allow_fraction_slope": true
                  },
                  "level_3": {
                    "allow_negative_slope": true,
                    "require_general_form": true
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
                  "slope is finite",
                  "point coordinates are integers",
                  "generated equation passes through the point",
                  "generated equation has the requested slope",
                  "equivalent forms normalize to same Ax + By + C = 0"
                ],
                "answer_shape": "linear_equation",
                "explanation_variants": [
                  "point_slope_to_general",
                  "slope_intercept_to_general"
                ],
                "sampling_strategy": "weighted_random"
              },
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
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
          "selected_subskill": "write_line_equation_from_point_slope",
          "selected_problem_type": "write_line_equation_from_point_slope",
          "candidate_source": "line_equation_routing",
          "skill_scope_trusted": true,
          "target_task": "write_line_equation_from_point_slope",
          "task_family": "line_equation_family",
          "math_objects": [
            "coordinate_point",
            "line_equation"
          ],
          "answer_type": "equation",
          "answer_shape": "linear_equation",
          "classification_confidence": "medium",
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
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            }
          ],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4540,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 1"
            },
            {
              "example_id": 4541,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 2"
            },
            {
              "example_id": 4542,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 3"
            },
            {
              "example_id": 4543,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 4"
            },
            {
              "example_id": 4546,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "2-2習題 基礎題 7"
            },
            {
              "example_id": 4549,
              "source_type": "worked_example",
              "example_label": "例題1",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例1"
            },
            {
              "example_id": 4550,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4551,
              "source_type": "worked_example",
              "example_label": "例題3",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例3"
            },
            {
              "example_id": 4552,
              "source_type": "worked_example",
              "example_label": "例題4",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例4"
            },
            {
              "example_id": 4556,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習1",
              "section_order": 0,
              "title_head": "隨堂練習1"
            },
            {
              "example_id": 4557,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4560,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習3",
              "section_order": 0,
              "title_head": "隨堂練習3"
            },
            {
              "example_id": 4561,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習4",
              "section_order": 0,
              "title_head": "隨堂練習4"
            },
            {
              "example_id": 4606,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題9"
            }
          ]
        },
        "classification_confidence": "medium",
        "stem_concept": "line_equation",
        "correct_answer": "A",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_PointSlopeForm",
        "equivalence_type": "exact_string",
        "checker_key": "equation_checker"
      },
      "answer_shape": "linear_equation",
      "classification_confidence": "high",
      "classification_reason": "line_equation_routing",
      "risk_flags": [
        "stem_embeds_choices",
        "requires_human_action",
        "candidate_only_problem_type"
      ],
      "semantic_classification": {
        "ai_target_task": "",
        "ai_task_family": "",
        "ai_confidence": 0.0,
        "rule_target_task": "write_line_equation_from_point_slope",
        "rule_task_family": "line_equation_family",
        "rule_confidence": 0.7,
        "final_target_task": "write_line_equation_from_point_slope",
        "final_task_family": "line_equation_family",
        "classifier_source": "line_equation_routing",
        "classification_decision": "forced_by_line_equation_routing",
        "conflict_reason": "",
        "source_mapping_warning": "",
        "requires_human_action": true,
        "skill_scoped_candidates": [
          {
            "candidate_id": "C1",
            "target_task": "write_line_equation_from_point_slope",
            "task_family": "line_equation_family",
            "problem_type_id": "write_line_equation_from_point_slope",
            "label": "write_line_equation_from_point_slope",
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
                  "id": "given_point_and_slope_find_point_slope_form",
                  "label": "點斜式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_slope_intercept_form",
                  "label": "斜截式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
                  "weight": 1.0,
                  "enabled": true
                },
                {
                  "id": "given_point_and_slope_find_general_form",
                  "label": "一般式",
                  "stem_pattern": "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
                  "weight": 1.0,
                  "enabled": true
                }
              ],
              "parameter_schema": {
                "point_coordinates": {
                  "x_min": -8,
                  "x_max": 8,
                  "y_min": -8,
                  "y_max": 8,
                  "integer_only": true
                },
                "slope": {
                  "choices": [
                    "integer",
                    "simple_fraction"
                  ],
                  "weights": [
                    0.65,
                    0.35
                  ],
                  "integer_range": [
                    -5,
                    5
                  ],
                  "exclude_zero": true,
                  "fraction_numerators": [
                    1,
                    2,
                    3,
                    -1,
                    -2,
                    -3
                  ],
                  "fraction_denominators": [
                    2,
                    3
                  ]
                },
                "equation_form": {
                  "choices": [
                    "point_slope",
                    "slope_intercept",
                    "general"
                  ],
                  "weights": [
                    0.34,
                    0.33,
                    0.33
                  ]
                }
              },
              "variation_dimensions": [
                "point_coordinates",
                "slope_type",
                "equation_form",
                "integer_or_fraction_slope",
                "coefficient_normalization"
              ],
              "difficulty_controls": {
                "level_1": {
                  "coordinate_range": [
                    -5,
                    5
                  ],
                  "integer_slope_only": true,
                  "equation_form": "point_slope"
                },
                "level_2": {
                  "coordinate_range": [
                    -8,
                    8
                  ],
                  "allow_fraction_slope": true
                },
                "level_3": {
                  "allow_negative_slope": true,
                  "require_general_form": true
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
                "slope is finite",
                "point coordinates are integers",
                "generated equation passes through the point",
                "generated equation has the requested slope",
                "equivalent forms normalize to same Ax + By + C = 0"
              ],
              "answer_shape": "linear_equation",
              "explanation_variants": [
                "point_slope_to_general",
                "slope_intercept_to_general"
              ],
              "sampling_strategy": "weighted_random"
            },
            "parameter_schema": {
              "point_coordinates": {
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "integer_only": true
              },
              "slope": {
                "choices": [
                  "integer",
                  "simple_fraction"
                ],
                "weights": [
                  0.65,
                  0.35
                ],
                "integer_range": [
                  -5,
                  5
                ],
                "exclude_zero": true,
                "fraction_numerators": [
                  1,
                  2,
                  3,
                  -1,
                  -2,
                  -3
                ],
                "fraction_denominators": [
                  2,
                  3
                ]
              },
              "equation_form": {
                "choices": [
                  "point_slope",
                  "slope_intercept",
                  "general"
                ],
                "weights": [
                  0.34,
                  0.33,
                  0.33
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
        "selected_subskill": "write_line_equation_from_point_slope",
        "selected_problem_type": "write_line_equation_from_point_slope",
        "candidate_source": "line_equation_routing",
        "skill_scope_trusted": true,
        "target_task": "write_line_equation_from_point_slope",
        "task_family": "line_equation_family",
        "math_objects": [
          "coordinate_point",
          "line_equation"
        ],
        "answer_type": "equation",
        "answer_shape": "linear_equation",
        "classification_confidence": "medium",
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
      "subskill_id": "write_line_equation_from_point_slope",
      "classification_source": "line_equation_routing",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "eligible",
      "answer_type": "expression",
      "equivalence_type": "exact_string",
      "checker_key": "equation_checker",
      "alignment_score": 0.8
    }
  ],
  "split_or_merge_recommendation": "induced_from_source_features",
  "classifier_gate": {
    "status": "classifier_auto_pending_promote_with_warning",
    "allowed": true,
    "warnings": [
      "insufficient_examples",
      "ai_partial_unavailable_relaxed_tolerance"
    ]
  },
  "generator_draft_gate": {
    "status": "generator_draft_allowed_with_low_source_warning",
    "allowed": true,
    "warnings": [
      "low_source_examples",
      "ai_partial_unavailable_relaxed_tolerance"
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
      "ai_partial_unavailable_relaxed_tolerance"
    ]
  },
  "exception_review_gate": {
    "required": false,
    "reasons": []
  },
  "self_healing_log": [],
  "reports": {
    "auto_pipeline_summary_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_auto_pipeline_summary.json",
    "auto_pipeline_summary_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_auto_pipeline_summary.md",
    "phase1_summary_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase1_summary.json",
    "phase1_summary_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase1_summary.md",
    "phase1_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase1_summary.json",
    "phase1_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase1_summary.md",
    "phase2_generator_summary_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase2_generator_summary.json",
    "phase2_generator_summary_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase2_generator_summary.md",
    "phase2_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase2_generator_summary.json",
    "phase2_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase2_generator_summary.md",
    "generator_draft_spec_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_PointSlopeForm_generator_draft_spec.json",
    "phase3_package_summary_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase3_package_summary.json",
    "phase3_package_summary_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase3_package_summary.md",
    "phase3_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase3_package_summary.json",
    "phase3_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase3_package_summary.md",
    "final_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase3_package_summary.json",
    "final_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase3_package_summary.md",
    "draft_skill_file": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_PointSlopeForm.py"
  },
  "next_action": "review_phase3_publish_check",
  "timestamp": "2026-06-15T04:33:45.742241+00:00",
  "dry_run": true
}
```
