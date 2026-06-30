# Gencode Auto Pipeline Summary: vh_數學B1_AbsoluteValueInequality

## summary
```json
{
  "ok": false,
  "skill_id": "vh_數學B1_AbsoluteValueInequality",
  "pipeline_status": "auto_pipeline_completed_runtime_blocked",
  "source_example_count": 10,
  "candidate_problem_types": [
    {
      "problem_type_id": "text_short_contextual_application",
      "proposed_problem_type_id": "text_short_contextual_application",
      "display_name": "text_short / contextual_application",
      "matched_example_ids": [
        4400,
        4402,
        4403,
        4404,
        4405,
        4406,
        4407,
        4409,
        4413
      ],
      "matched_example_count": 9,
      "unmatched_example_ids": [],
      "representative_example_id": 4400,
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
          "-3"
        ],
        "source_has_choices": false,
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "presentation_mode": "",
        "order_matters": true,
        "accepted_format_notes": [],
        "canonical_answer_schema": "integer"
      },
      "checker_key_proposal": "text_short_checker",
      "equivalence_type_proposal": "exact_string",
      "answer_shape": "scalar",
      "answer_semantics": "scalar",
      "presentation_mode": "short_answer",
      "source_has_choices": false,
      "selected_checker": "integer_checker",
      "checker_selection_reason": "task_family_default",
      "coordinate_pair_presentation_note": "",
      "confidence": "high",
      "promote_recommendation": "hold_pending_problem_type_induction",
      "promote_blockers": [
        "generic_fallback_blocked_by_source_skill_binding"
      ],
      "risk_flags": [
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance",
        "demoted_majority_needs_review_due_to_partial_unavailable",
        "generic_fallback_blocked_by_source_skill_binding",
        "majority_sources_need_human_subskill_review",
        "uniform_core_target_task_alignment_threshold_relaxed"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "short_answer",
        "contextual_application",
        "short_answer",
        [
          "numeric_computation"
        ],
        [],
        "default"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "skill_scoped_unresolved_problem_type",
        "skill_id": "vh_數學B1_AbsoluteValueInequality",
        "target_task": "contextual_application",
        "task_family": "generic_numeric_family",
        "display_name": "short_answer / contextual_application",
        "answer_format_hint": "integer",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          4400,
          4402,
          4403,
          4404,
          4405,
          4406,
          4407,
          4409,
          4413
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
          "source_has_choices": false,
          "equivalence_type": "numeric_exact",
          "checker_key": "integer_checker",
          "presentation_mode": "short_answer"
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [],
          "required_math_objects": [],
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
            "shuffle_choices": false
          },
          "avoid_llm_freeform_math": true,
          "use_domain_functions": true,
          "derivation_steps_required": true,
          "contextual_application": true,
          "template_slots": {
            "stem": "linear_function_contextual_word_problem"
          },
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
          "problem_type_id": "skill_scoped_unresolved_problem_type",
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
          "short_answer",
          "contextual_application",
          "short_answer",
          [
            "numeric_computation"
          ],
          [],
          "default"
        ],
        "canonical_base_problem_type_id": "skill_scoped_unresolved_problem_type",
        "value_type_prefix": "",
        "_resolved_template_slot": "linear_function_contextual_word_problem"
      },
      "generator_readiness": "pending_problem_type_induction",
      "usable_for_phase3": false,
      "template_slot": "linear_function_contextual_word_problem",
      "canonical_base_problem_type_id": "skill_scoped_unresolved_problem_type",
      "value_type_prefix": "",
      "subskill_id": "contextual_application",
      "requires_human_action": true,
      "requires_human_rule_pack": true,
      "pending_problem_type_induction": true,
      "answer_type": "integer",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0312,
        "task_consistent_with_skill": false
      }
    },
    {
      "problem_type_id": "choice_contextual_application",
      "proposed_problem_type_id": "choice_contextual_application",
      "display_name": "choice / contextual_application",
      "matched_example_ids": [
        4499
      ],
      "matched_example_count": 1,
      "unmatched_example_ids": [],
      "representative_example_id": 4499,
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
      "promote_recommendation": "hold_pending_problem_type_induction",
      "promote_blockers": [
        "generic_fallback_blocked_by_source_skill_binding"
      ],
      "risk_flags": [
        "ai_first_mode_fell_back_to_rule_only",
        "ai_partial_unavailable_relaxed_tolerance",
        "demoted_majority_needs_review_due_to_partial_unavailable",
        "generic_fallback_blocked_by_source_skill_binding",
        "majority_sources_need_human_subskill_review",
        "uniform_core_target_task_alignment_threshold_relaxed"
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
        [],
        "default"
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "skill_scoped_unresolved_problem_type_2",
        "skill_id": "vh_數學B1_AbsoluteValueInequality",
        "target_task": "contextual_application",
        "task_family": "generic_numeric_family",
        "display_name": "single_choice / contextual_application",
        "answer_format_hint": "A/B/C/D",
        "answer_fields": null,
        "answer_separator": null,
        "source_example_ids": [
          4499
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
          "allowed_math_objects": [],
          "required_math_objects": [],
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
          "templates": [
            "template_scalar_unknown",
            "template_feature_value"
          ],
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
          [],
          "default"
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
      "requires_human_action": true,
      "requires_human_rule_pack": true,
      "pending_problem_type_induction": true,
      "answer_type": "choice",
      "runtime_status": "runtime_ready_candidate",
      "next_action": "phase2_foundation_preflight",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0,
        "source_problem_type_score": 0.0645,
        "task_consistent_with_skill": false
      }
    }
  ],
  "per_example_classification": [
    {
      "example_id": 4409,
      "detected_problem_type_id": "skill_scoped_unresolved_problem_type",
      "example_feature": {
        "source_example_id": 4409,
        "question_text": "試求下列不等式之解：(1)$\\left| x \\right|$ < 3 (2) $\\left| x \\right|$ ≥ 4",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
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
          "x"
        ],
        "givens": [
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
          "candidate_source": "clause45_fallback_proxy",
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
          "nearby_worked_examples": [],
          "linked_worked_example": null,
          "linked_practices": [],
          "same_section_sequence": [
            {
              "example_id": 4400,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 3"
            },
            {
              "example_id": 4402,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 5"
            },
            {
              "example_id": 4403,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 6"
            },
            {
              "example_id": 4404,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 7"
            },
            {
              "example_id": 4405,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 8"
            },
            {
              "example_id": 4406,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 9"
            },
            {
              "example_id": 4407,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 10"
            },
            {
              "example_id": 4409,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4413,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4499,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題1"
            }
          ]
        },
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_AbsoluteValueInequality",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "needs_rule_pack_or_slot_registration": true,
        "problem_type_id": "skill_scoped_unresolved_problem_type",
        "proxy_problem_type_id": "skill_scoped_unresolved_problem_type",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "requires_human_action": false
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
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
        "candidate_source": "clause45_fallback_proxy",
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
      "subskill_id": "contextual_application",
      "classification_source": "clause45_unclassified_exception",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "excluded",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4400,
      "detected_problem_type_id": "skill_scoped_unresolved_problem_type",
      "example_feature": {
        "source_example_id": 4400,
        "question_text": "試求下列不等式之解：\n(1)$\\left| x \\right|$≤ 8 (2)$\\left| x \\right|$> 10 (3)$\\left| x \\right|$< 7 (4)$\\left| x \\right|$≥ 12",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
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
          "x"
        ],
        "givens": [
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
          "candidate_source": "clause45_fallback_proxy",
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
              "example_id": 4409,
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
              "example_id": 4400,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 3"
            },
            {
              "example_id": 4402,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 5"
            },
            {
              "example_id": 4403,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 6"
            },
            {
              "example_id": 4404,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 7"
            },
            {
              "example_id": 4405,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 8"
            },
            {
              "example_id": 4406,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 9"
            },
            {
              "example_id": 4407,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 10"
            },
            {
              "example_id": 4409,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4413,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4499,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題1"
            }
          ]
        },
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_AbsoluteValueInequality",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "needs_rule_pack_or_slot_registration": true,
        "problem_type_id": "skill_scoped_unresolved_problem_type",
        "proxy_problem_type_id": "skill_scoped_unresolved_problem_type",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "requires_human_action": false
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
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
        "candidate_source": "clause45_fallback_proxy",
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
      "subskill_id": "contextual_application",
      "classification_source": "clause45_unclassified_exception",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "excluded",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4402,
      "detected_problem_type_id": "skill_scoped_unresolved_problem_type",
      "example_feature": {
        "source_example_id": 4402,
        "question_text": "解下列不等式：\n(1)$\\left| x-2 \\right|\\le 4$ (2)$\\left| x+5 \\right|>1$",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
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
          "x"
        ],
        "givens": [
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
          "candidate_source": "clause45_fallback_proxy",
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
              "example_id": 4409,
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
              "example_id": 4400,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 3"
            },
            {
              "example_id": 4402,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 5"
            },
            {
              "example_id": 4403,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 6"
            },
            {
              "example_id": 4404,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 7"
            },
            {
              "example_id": 4405,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 8"
            },
            {
              "example_id": 4406,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 9"
            },
            {
              "example_id": 4407,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 10"
            },
            {
              "example_id": 4409,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4413,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4499,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題1"
            }
          ]
        },
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_AbsoluteValueInequality",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "needs_rule_pack_or_slot_registration": true,
        "problem_type_id": "skill_scoped_unresolved_problem_type",
        "proxy_problem_type_id": "skill_scoped_unresolved_problem_type",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "requires_human_action": false
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
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
        "candidate_source": "clause45_fallback_proxy",
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
      "subskill_id": "contextual_application",
      "classification_source": "clause45_unclassified_exception",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "excluded",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4403,
      "detected_problem_type_id": "skill_scoped_unresolved_problem_type",
      "example_feature": {
        "source_example_id": 4403,
        "question_text": "解下列不等式：\n(1)$\\left| x-3 \\right|<2$ (2)$\\left| x+5 \\right|\\ge 4$",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
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
          "x"
        ],
        "givens": [
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
          "candidate_source": "clause45_fallback_proxy",
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
              "example_id": 4409,
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
              "example_id": 4400,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 3"
            },
            {
              "example_id": 4402,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 5"
            },
            {
              "example_id": 4403,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 6"
            },
            {
              "example_id": 4404,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 7"
            },
            {
              "example_id": 4405,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 8"
            },
            {
              "example_id": 4406,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 9"
            },
            {
              "example_id": 4407,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 10"
            },
            {
              "example_id": 4409,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4413,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4499,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題1"
            }
          ]
        },
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_AbsoluteValueInequality",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "needs_rule_pack_or_slot_registration": true,
        "problem_type_id": "skill_scoped_unresolved_problem_type",
        "proxy_problem_type_id": "skill_scoped_unresolved_problem_type",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "requires_human_action": false
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
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
        "candidate_source": "clause45_fallback_proxy",
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
      "subskill_id": "contextual_application",
      "classification_source": "clause45_unclassified_exception",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "excluded",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4404,
      "detected_problem_type_id": "skill_scoped_unresolved_problem_type",
      "example_feature": {
        "source_example_id": 4404,
        "question_text": "解不等式$\\left| 4x+1 \\right|\\le 6$。",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "contextual_application",
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
          "candidate_source": "clause45_fallback_proxy",
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
              "example_id": 4409,
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
              "example_id": 4400,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 3"
            },
            {
              "example_id": 4402,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 5"
            },
            {
              "example_id": 4403,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 6"
            },
            {
              "example_id": 4404,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 7"
            },
            {
              "example_id": 4405,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 8"
            },
            {
              "example_id": 4406,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 9"
            },
            {
              "example_id": 4407,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 10"
            },
            {
              "example_id": 4409,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4413,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4499,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題1"
            }
          ]
        },
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_AbsoluteValueInequality",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "needs_rule_pack_or_slot_registration": true,
        "problem_type_id": "skill_scoped_unresolved_problem_type",
        "proxy_problem_type_id": "skill_scoped_unresolved_problem_type",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "requires_human_action": false
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
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
        "candidate_source": "clause45_fallback_proxy",
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
      "subskill_id": "contextual_application",
      "classification_source": "clause45_unclassified_exception",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "excluded",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4405,
      "detected_problem_type_id": "skill_scoped_unresolved_problem_type",
      "example_feature": {
        "source_example_id": 4405,
        "question_text": "解不等式$\\left| 2x-3 \\right|>1$。",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "contextual_application",
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
          "candidate_source": "clause45_fallback_proxy",
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
              "example_id": 4409,
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
              "example_id": 4400,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 3"
            },
            {
              "example_id": 4402,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 5"
            },
            {
              "example_id": 4403,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 6"
            },
            {
              "example_id": 4404,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 7"
            },
            {
              "example_id": 4405,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 8"
            },
            {
              "example_id": 4406,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 9"
            },
            {
              "example_id": 4407,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 10"
            },
            {
              "example_id": 4409,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4413,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4499,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題1"
            }
          ]
        },
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_AbsoluteValueInequality",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "needs_rule_pack_or_slot_registration": true,
        "problem_type_id": "skill_scoped_unresolved_problem_type",
        "proxy_problem_type_id": "skill_scoped_unresolved_problem_type",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "requires_human_action": false
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
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
        "candidate_source": "clause45_fallback_proxy",
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
      "subskill_id": "contextual_application",
      "classification_source": "clause45_unclassified_exception",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "excluded",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4406,
      "detected_problem_type_id": "skill_scoped_unresolved_problem_type",
      "example_feature": {
        "source_example_id": 4406,
        "question_text": "解不等式$\\left| 3x-1 \\right|\\ge 7$。",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "contextual_application",
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
          "candidate_source": "clause45_fallback_proxy",
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
              "example_id": 4409,
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
              "example_id": 4400,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 3"
            },
            {
              "example_id": 4402,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 5"
            },
            {
              "example_id": 4403,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 6"
            },
            {
              "example_id": 4404,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 7"
            },
            {
              "example_id": 4405,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 8"
            },
            {
              "example_id": 4406,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 9"
            },
            {
              "example_id": 4407,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 10"
            },
            {
              "example_id": 4409,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4413,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4499,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題1"
            }
          ]
        },
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_AbsoluteValueInequality",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "needs_rule_pack_or_slot_registration": true,
        "problem_type_id": "skill_scoped_unresolved_problem_type",
        "proxy_problem_type_id": "skill_scoped_unresolved_problem_type",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "requires_human_action": false
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
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
        "candidate_source": "clause45_fallback_proxy",
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
      "subskill_id": "contextual_application",
      "classification_source": "clause45_unclassified_exception",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "excluded",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4407,
      "detected_problem_type_id": "skill_scoped_unresolved_problem_type",
      "example_feature": {
        "source_example_id": 4407,
        "question_text": "解不等式$\\left| 5x+3 \\right|<7$。",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
        "target_task": "contextual_application",
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
          "candidate_source": "clause45_fallback_proxy",
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
              "example_id": 4409,
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
              "example_id": 4400,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 3"
            },
            {
              "example_id": 4402,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 5"
            },
            {
              "example_id": 4403,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 6"
            },
            {
              "example_id": 4404,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 7"
            },
            {
              "example_id": 4405,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 8"
            },
            {
              "example_id": 4406,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 9"
            },
            {
              "example_id": 4407,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 10"
            },
            {
              "example_id": 4409,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4413,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4499,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題1"
            }
          ]
        },
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_AbsoluteValueInequality",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "needs_rule_pack_or_slot_registration": true,
        "problem_type_id": "skill_scoped_unresolved_problem_type",
        "proxy_problem_type_id": "skill_scoped_unresolved_problem_type",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "requires_human_action": false
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
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
        "candidate_source": "clause45_fallback_proxy",
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
      "subskill_id": "contextual_application",
      "classification_source": "clause45_unclassified_exception",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "excluded",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4413,
      "detected_problem_type_id": "skill_scoped_unresolved_problem_type",
      "example_feature": {
        "source_example_id": 4413,
        "question_text": "試求下列不等式之解：(1) $\\left| x \\right|$ ≤ 6 (2) $\\left| x \\right|$> 5",
        "answer": "0",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "checker": "text_short_checker",
        "equivalence": "exact_string",
        "math_objects": [],
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
          "x"
        ],
        "givens": [
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
          "candidate_source": "clause45_fallback_proxy",
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
          "confidence_adjustment_reason": "sequence_context_used",
          "possible_structure_mismatch": false,
          "possible_mixed_source_context": false,
          "source_quality_reject": false,
          "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
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
              "example_id": 4409,
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
              "example_id": 4400,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 3"
            },
            {
              "example_id": 4402,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 5"
            },
            {
              "example_id": 4403,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 6"
            },
            {
              "example_id": 4404,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 7"
            },
            {
              "example_id": 4405,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 8"
            },
            {
              "example_id": 4406,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 9"
            },
            {
              "example_id": 4407,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 10"
            },
            {
              "example_id": 4409,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4413,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4499,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題1"
            }
          ]
        },
        "correct_answer": "0",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_AbsoluteValueInequality",
        "generator_readiness": "pending_problem_type_induction",
        "usable_for_phase3": false,
        "needs_rule_pack_or_slot_registration": true,
        "problem_type_id": "skill_scoped_unresolved_problem_type",
        "proxy_problem_type_id": "skill_scoped_unresolved_problem_type",
        "equivalence_type": "exact_string",
        "checker_key": "text_short_checker",
        "requires_human_action": false
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "rule_fallback_ai_unavailable",
      "risk_flags": [
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
        "candidate_source": "clause45_fallback_proxy",
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
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "contextual_application",
      "classification_source": "clause45_unclassified_exception",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
      "induction_eligibility": "excluded",
      "answer_type": "text_short",
      "equivalence_type": "exact_string",
      "checker_key": "text_short_checker",
      "requires_human_action": false
    },
    {
      "example_id": 4499,
      "detected_problem_type_id": "skill_scoped_unresolved_problem_type_2",
      "example_feature": {
        "source_example_id": 4499,
        "question_text": "試求滿足不等式$\\left| 3x-2 \\right|\\le 8$的整數x共有多少個？ (A) 4 (B) 5 (C) 6 (D) 7。",
        "answer": "A",
        "choices": [
          "4",
          "5",
          "6",
          "7。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [],
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
          "D"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D"
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
          "candidate_source": "clause45_fallback_proxy",
          "selected_generator_contract": {},
          "parameter_schema": {},
          "variable_randomization_notes": [],
          "checker_key": "",
          "equivalence_type": "",
          "skill_scope_trusted": true,
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "math_objects": [],
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
              "example_id": 4409,
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
              "example_id": 4400,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 3"
            },
            {
              "example_id": 4402,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 5"
            },
            {
              "example_id": 4403,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 6"
            },
            {
              "example_id": 4404,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 7"
            },
            {
              "example_id": 4405,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 8"
            },
            {
              "example_id": 4406,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 9"
            },
            {
              "example_id": 4407,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "1-1習題 基礎題 10"
            },
            {
              "example_id": 4409,
              "source_type": "worked_example",
              "example_label": "例題2",
              "practice_label": "",
              "section_order": 0,
              "title_head": "例2"
            },
            {
              "example_id": 4413,
              "source_type": "in_class_practice",
              "example_label": "",
              "practice_label": "隨堂練習2",
              "section_order": 0,
              "title_head": "隨堂練習2"
            },
            {
              "example_id": 4499,
              "source_type": "unknown",
              "example_label": "",
              "practice_label": "",
              "section_order": 0,
              "title_head": "CH1自我評量 題1"
            }
          ]
        },
        "correct_answer": "A",
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION",
        "induction_tier": "core",
        "enrichment_reasons": [],
        "included_in_core_induction": true,
        "source_skill_scope_locked": true,
        "skill_mapping_authority": "textbook_examples.skill_id",
        "classification_scope": "within_current_skill",
        "source_skill_id": "vh_數學B1_AbsoluteValueInequality",
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
        "candidate_source": "clause45_fallback_proxy",
        "selected_generator_contract": {},
        "parameter_schema": {},
        "variable_randomization_notes": [],
        "checker_key": "",
        "equivalence_type": "",
        "skill_scope_trusted": true,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "math_objects": [],
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
        "confidence_adjustment_reason": "sequence_context_used",
        "possible_structure_mismatch": false,
        "possible_mixed_source_context": false,
        "source_quality_reject": false,
        "source_quality_status": "FORCE_ALLOWED_FOR_INDUCTION"
      },
      "subskill_id": "contextual_application",
      "classification_source": "clause45_unclassified_exception",
      "source_skill_scope_locked": true,
      "skill_mapping_authority": "textbook_examples.skill_id",
      "classification_scope": "within_current_skill",
      "unresolved_reason": "",
      "requires_human_rule_pack": false,
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
      "ai_partial_unavailable_relaxed_tolerance",
      "demoted_majority_needs_review_due_to_partial_unavailable",
      "generic_fallback_blocked_by_source_skill_binding",
      "majority_sources_need_human_subskill_review",
      "uniform_core_target_task_alignment_threshold_relaxed"
    ]
  },
  "generator_draft_gate": {
    "status": "generator_draft_allowed_with_low_source_warning",
    "allowed": true,
    "warnings": [
      "low_source_examples",
      "ai_first_mode_fell_back_to_rule_only",
      "ai_partial_unavailable_relaxed_tolerance",
      "demoted_majority_needs_review_due_to_partial_unavailable",
      "generic_fallback_blocked_by_source_skill_binding",
      "majority_sources_need_human_subskill_review",
      "uniform_core_target_task_alignment_threshold_relaxed"
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
      "demoted_majority_needs_review_due_to_partial_unavailable",
      "generic_fallback_blocked_by_source_skill_binding",
      "majority_sources_need_human_subskill_review",
      "uniform_core_target_task_alignment_threshold_relaxed"
    ]
  },
  "exception_review_gate": {
    "required": false,
    "reasons": []
  },
  "self_healing_log": [],
  "reports": {
    "auto_pipeline_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_auto_pipeline_summary.json",
    "auto_pipeline_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_auto_pipeline_summary.md",
    "phase1_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase1_summary.json",
    "phase1_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase1_summary.md",
    "phase1_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase1_summary.json",
    "phase1_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase1_summary.md",
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase2_generator_summary.json",
    "phase2_generator_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase2_generator_summary.md",
    "phase2_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase2_generator_summary.json",
    "phase2_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase2_generator_summary.md",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_AbsoluteValueInequality_generator_draft_spec.json",
    "phase3_package_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase3_package_summary.json",
    "phase3_package_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase3_package_summary.md",
    "phase3_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase3_package_summary.json",
    "phase3_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase3_package_summary.md",
    "final_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase3_package_summary.json",
    "final_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase3_package_summary.md",
    "draft_skill_file": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_AbsoluteValueInequality.py"
  },
  "next_action": "review_phase2_blockers_before_phase3",
  "timestamp": "2026-06-30T15:11:39.067275+00:00",
  "dry_run": true
}
```
