# Gencode Phase1 Summary: vh_數學B1_CartesianCoordinateSystemEstablishment

- spec_mode: `induce_from_sources`

## Example features

| example_id | answer_type | target_task | has_choices | stem_embeds_choices | math_objects |
| --- | --- | --- | --- | --- | --- |
| 4417 | short_answer | classify_quadrant | False | False | coordinate_point, symbolic_condition |
| 4435 | short_answer | classify_quadrant | False | False | coordinate_point, symbolic_condition |
| 4509 | single_choice | choose_possible_coordinate | True | True | axis_distance, coordinate_point |
| 4510 | single_choice | choose_correct_statement | True | True | coordinate_point |

## Induction clusters

### Cluster 1
- answer_type: `short_answer`
- source_example_ids: [4417, 4435]
- grouping_reason: single_signature_group
- feature_signature: `['short_answer', 'classify_quadrant', ('sign_reasoning',), ('symbolic_condition', 'coordinate_point')]`

### Cluster 2
- answer_type: `single_choice`
- source_example_ids: [4509, 4510]
- grouping_reason: merged_compatible_single_choice_tasks_with_template_families
- feature_signature: `['merged_single_choice', 'single_choice', ('choose_correct_statement', 'choose_possible_coordinate')]`


## Candidate problem types

| problem_type_id | display_name | answer_type | source_examples | grouping_reason |
| --- | --- | --- | --- | --- |
| short_answer_classify_quadrant_symbolic_condition_coordinate_point | 象限判斷短答 | short_answer | [4417, 4435] | single_signature_group |
| single_choice_choose_correct_statement_axis_distance_coordinate_point | 象限敘述選擇 | single_choice | [4509, 4510] | merged_compatible_single_choice_tasks_with_template_families |

## phase1
```json
{
  "ok": true,
  "phase": "phase1",
  "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
  "source_example_count": 4,
  "candidate_problem_types": [
    {
      "problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
      "proposed_problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
      "display_name": "象限判斷短答",
      "matched_example_ids": [
        4417,
        4435
      ],
      "matched_example_count": 2,
      "unmatched_example_ids": [],
      "representative_example_id": 4417,
      "structural_features": [
        "text_short"
      ],
      "answer_contract_proposal": {
        "answer_type": "short_answer",
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "answer_equivalence": "exact_text",
        "frontend_render_choices": false,
        "checker_key": "text_checker",
        "equivalence_type": "exact_string",
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "symbolic_condition"
          ],
          "required_math_objects": [
            "symbolic_condition",
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
          "variables_in_conditions_must_appear_in_target": true
        },
        "semantic_contract": {
          "reasoning_type": [
            "sign_reasoning"
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
          "template_families": [
            "classify_quadrant"
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
            "stem": "symbolic_quadrant"
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
        }
      },
      "checker_key_proposal": "text_checker",
      "equivalence_type_proposal": "exact_string",
      "answer_shape": "text_short",
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "short_answer",
        "classify_quadrant",
        [
          "sign_reasoning"
        ],
        [
          "symbolic_condition",
          "coordinate_point"
        ]
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "display_name": "象限判斷短答",
        "source_example_ids": [
          4417,
          4435
        ],
        "answer_contract": {
          "answer_type": "short_answer",
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "answer_equivalence": "exact_text",
          "frontend_render_choices": false
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "symbolic_condition"
          ],
          "required_math_objects": [
            "symbolic_condition",
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
          "variables_in_conditions_must_appear_in_target": true
        },
        "semantic_contract": {
          "reasoning_type": [
            "sign_reasoning"
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
          "template_families": [
            "classify_quadrant"
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
            "stem": "symbolic_quadrant"
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
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "short_answer",
          "classify_quadrant",
          [
            "sign_reasoning"
          ],
          [
            "symbolic_condition",
            "coordinate_point"
          ]
        ]
      },
      "generator_readiness": "runtime_ready",
      "template_slot": "symbolic_quadrant"
    },
    {
      "problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
      "proposed_problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
      "display_name": "象限敘述選擇",
      "matched_example_ids": [
        4509,
        4510
      ],
      "matched_example_count": 2,
      "unmatched_example_ids": [],
      "representative_example_id": 4509,
      "structural_features": [
        "choice_label"
      ],
      "answer_contract_proposal": {
        "answer_type": "single_choice",
        "choices_required": true,
        "choice_count": 4,
        "correct_choice_count": 1,
        "answer_equivalence": "choice_label",
        "frontend_render_choices": true,
        "checker_key": "choice_label_checker",
        "equivalence_type": "choice_label",
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "axis_distance",
            "coordinate_point"
          ],
          "required_math_objects": [
            "axis_distance",
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
            "axis_distance_reasoning",
            "sign_reasoning"
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
          "template_families": [
            "choose_correct_statement",
            "choose_possible_coordinate"
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
          "template_slots": {
            "stem": "axis_distance_choice"
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
        }
      },
      "checker_key_proposal": "choice_label_checker",
      "equivalence_type_proposal": "choice_label",
      "answer_shape": "choice_label",
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "merged_compatible_single_choice_tasks_with_template_families",
      "feature_signature": [
        "merged_single_choice",
        "single_choice",
        [
          "choose_correct_statement",
          "choose_possible_coordinate"
        ]
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "display_name": "象限敘述選擇",
        "source_example_ids": [
          4509,
          4510
        ],
        "answer_contract": {
          "answer_type": "single_choice",
          "choices_required": true,
          "choice_count": 4,
          "correct_choice_count": 1,
          "answer_equivalence": "choice_label",
          "frontend_render_choices": true
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "axis_distance",
            "coordinate_point"
          ],
          "required_math_objects": [
            "axis_distance",
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
            "axis_distance_reasoning",
            "sign_reasoning"
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
          "template_families": [
            "choose_correct_statement",
            "choose_possible_coordinate"
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
          "template_slots": {
            "stem": "axis_distance_choice"
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
        "grouping_reason": "merged_compatible_single_choice_tasks_with_template_families",
        "feature_signature": [
          "merged_single_choice",
          "single_choice",
          [
            "choose_correct_statement",
            "choose_possible_coordinate"
          ]
        ]
      },
      "generator_readiness": "runtime_ready",
      "template_slot": "axis_distance_choice"
    }
  ],
  "per_example_classification": [
    {
      "example_id": 4417,
      "detected_problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
      "example_feature": {
        "source_example_id": 4417,
        "question_text": "若點$P\\left( a,b \\right)$位在第一象限且a < b，則$Q\\left( a-b,{{a}^{2}}b \\right)$位在第幾象限？",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "checker": "text_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "target_task": "classify_quadrant",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "variables": [
          "P",
          "Q",
          "a",
          "b"
        ],
        "givens": [
          "P",
          "Q",
          "a",
          "b"
        ],
        "target": "classify_quadrant"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4435,
      "detected_problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
      "example_feature": {
        "source_example_id": 4435,
        "question_text": "設a、b為實數，且a < b < 0，則點$Q\\left( ab,a+b \\right)$在第幾象限？",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "checker": "text_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "target_task": "classify_quadrant",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "variables": [
          "Q",
          "a",
          "b"
        ],
        "givens": [
          "Q",
          "a",
          "b"
        ],
        "target": "classify_quadrant"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4509,
      "detected_problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
      "example_feature": {
        "source_example_id": 4509,
        "question_text": "設A點為坐標平面上一點，且A點到x軸及y軸之距離分別為3和4，則下列何者可能為A點之坐標？ 　(A)$\\left( -4,-3 \\right)$　(B)$\\left( -3,4 \\right)$　\r\n(C)$\\left( -3,-4 \\right)$　(D)$\\left( 3,4 \\right)$。",
        "answer": "",
        "choices": [
          "$\\left( -4,-3 \\right)$",
          "$\\left( -3,4 \\right)$",
          "$\\left( -3,-4 \\right)$",
          "$\\left( 3,4 \\right)$。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "axis_distance",
          "coordinate_point"
        ],
        "target_task": "choose_possible_coordinate",
        "reasoning_type": [
          "axis_distance_reasoning"
        ],
        "required_derivation": true,
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
        "target": "choose_possible_coordinate"
      },
      "answer_shape": "choice_label",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": [
        "stem_embeds_choices"
      ]
    },
    {
      "example_id": 4510,
      "detected_problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
      "example_feature": {
        "source_example_id": 4510,
        "question_text": "已知點$P\\left( a-b,ab \\right)$在坐標平面的第四象限，則下列敘述何者正確？\r\n(A)$A\\left( -a,b \\right)$在第一象限　(B)$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限\r\n(C)$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限　(D)$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。",
        "answer": "",
        "choices": [
          "$A\\left( -a,b \\right)$在第一象限",
          "$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限",
          "$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限",
          "$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "coordinate_point"
        ],
        "target_task": "choose_correct_statement",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "variables": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "a",
          "b"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "a",
          "b"
        ],
        "target": "choose_correct_statement"
      },
      "answer_shape": "choice_label",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": [
        "stem_embeds_choices"
      ]
    }
  ],
  "source_classifications": [
    {
      "example_id": 4417,
      "detected_problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
      "example_feature": {
        "source_example_id": 4417,
        "question_text": "若點$P\\left( a,b \\right)$位在第一象限且a < b，則$Q\\left( a-b,{{a}^{2}}b \\right)$位在第幾象限？",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "checker": "text_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "target_task": "classify_quadrant",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "variables": [
          "P",
          "Q",
          "a",
          "b"
        ],
        "givens": [
          "P",
          "Q",
          "a",
          "b"
        ],
        "target": "classify_quadrant"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4435,
      "detected_problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
      "example_feature": {
        "source_example_id": 4435,
        "question_text": "設a、b為實數，且a < b < 0，則點$Q\\left( ab,a+b \\right)$在第幾象限？",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "checker": "text_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "target_task": "classify_quadrant",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "variables": [
          "Q",
          "a",
          "b"
        ],
        "givens": [
          "Q",
          "a",
          "b"
        ],
        "target": "classify_quadrant"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4509,
      "detected_problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
      "example_feature": {
        "source_example_id": 4509,
        "question_text": "設A點為坐標平面上一點，且A點到x軸及y軸之距離分別為3和4，則下列何者可能為A點之坐標？ 　(A)$\\left( -4,-3 \\right)$　(B)$\\left( -3,4 \\right)$　\r\n(C)$\\left( -3,-4 \\right)$　(D)$\\left( 3,4 \\right)$。",
        "answer": "",
        "choices": [
          "$\\left( -4,-3 \\right)$",
          "$\\left( -3,4 \\right)$",
          "$\\left( -3,-4 \\right)$",
          "$\\left( 3,4 \\right)$。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "axis_distance",
          "coordinate_point"
        ],
        "target_task": "choose_possible_coordinate",
        "reasoning_type": [
          "axis_distance_reasoning"
        ],
        "required_derivation": true,
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
        "target": "choose_possible_coordinate"
      },
      "answer_shape": "choice_label",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": [
        "stem_embeds_choices"
      ]
    },
    {
      "example_id": 4510,
      "detected_problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
      "example_feature": {
        "source_example_id": 4510,
        "question_text": "已知點$P\\left( a-b,ab \\right)$在坐標平面的第四象限，則下列敘述何者正確？\r\n(A)$A\\left( -a,b \\right)$在第一象限　(B)$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限\r\n(C)$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限　(D)$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。",
        "answer": "",
        "choices": [
          "$A\\left( -a,b \\right)$在第一象限",
          "$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限",
          "$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限",
          "$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "coordinate_point"
        ],
        "target_task": "choose_correct_statement",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "variables": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "a",
          "b"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "a",
          "b"
        ],
        "target": "choose_correct_statement"
      },
      "answer_shape": "choice_label",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": [
        "stem_embeds_choices"
      ]
    }
  ],
  "unclassified_examples": [],
  "risk_examples": [
    4509,
    4510
  ],
  "split_or_merge_recommendation": "induced_from_source_features",
  "classifier_gate": {
    "status": "classifier_auto_pending_promote_with_warning",
    "allowed": true,
    "warnings": [
      "insufficient_examples"
    ]
  },
  "generator_draft_gate": {
    "status": "generator_draft_allowed_with_low_source_warning",
    "allowed": true,
    "warnings": [
      "low_source_examples"
    ]
  },
  "runtime_ready_gate": {
    "status": "blocked_insufficient_examples",
    "allowed": false,
    "blockers": [
      "blocked_insufficient_examples"
    ]
  },
  "exception_review_gate": {
    "required": false,
    "reasons": []
  },
  "reports": {
    "phase1_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CartesianCoordinateSystemEstablishment_phase1_summary.json",
    "phase1_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CartesianCoordinateSystemEstablishment_phase1_summary.md"
  },
  "next_action": "phase2_generate_from_induced_specs",
  "timestamp": "2026-05-28T15:23:45.101100+00:00",
  "dry_run": true,
  "auto_review_summary": {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "spec_mode": "induce_from_sources",
    "example_features": [
      {
        "source_example_id": 4417,
        "question_text": "若點$P\\left( a,b \\right)$位在第一象限且a < b，則$Q\\left( a-b,{{a}^{2}}b \\right)$位在第幾象限？",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "checker": "text_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "target_task": "classify_quadrant",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "variables": [
          "P",
          "Q",
          "a",
          "b"
        ],
        "givens": [
          "P",
          "Q",
          "a",
          "b"
        ],
        "target": "classify_quadrant"
      },
      {
        "source_example_id": 4435,
        "question_text": "設a、b為實數，且a < b < 0，則點$Q\\left( ab,a+b \\right)$在第幾象限？",
        "answer": "",
        "choices": [],
        "has_choices": false,
        "stem_embeds_choices": false,
        "answer_type": "short_answer",
        "answer_shape": "text_short",
        "checker": "text_checker",
        "equivalence": "exact_string",
        "math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "target_task": "classify_quadrant",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "variables": [
          "Q",
          "a",
          "b"
        ],
        "givens": [
          "Q",
          "a",
          "b"
        ],
        "target": "classify_quadrant"
      },
      {
        "source_example_id": 4509,
        "question_text": "設A點為坐標平面上一點，且A點到x軸及y軸之距離分別為3和4，則下列何者可能為A點之坐標？ 　(A)$\\left( -4,-3 \\right)$　(B)$\\left( -3,4 \\right)$　\r\n(C)$\\left( -3,-4 \\right)$　(D)$\\left( 3,4 \\right)$。",
        "answer": "",
        "choices": [
          "$\\left( -4,-3 \\right)$",
          "$\\left( -3,4 \\right)$",
          "$\\left( -3,-4 \\right)$",
          "$\\left( 3,4 \\right)$。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "axis_distance",
          "coordinate_point"
        ],
        "target_task": "choose_possible_coordinate",
        "reasoning_type": [
          "axis_distance_reasoning"
        ],
        "required_derivation": true,
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
        "target": "choose_possible_coordinate"
      },
      {
        "source_example_id": 4510,
        "question_text": "已知點$P\\left( a-b,ab \\right)$在坐標平面的第四象限，則下列敘述何者正確？\r\n(A)$A\\left( -a,b \\right)$在第一象限　(B)$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限\r\n(C)$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限　(D)$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。",
        "answer": "",
        "choices": [
          "$A\\left( -a,b \\right)$在第一象限",
          "$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限",
          "$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限",
          "$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
        "math_objects": [
          "coordinate_point"
        ],
        "target_task": "choose_correct_statement",
        "reasoning_type": [
          "sign_reasoning"
        ],
        "required_derivation": true,
        "variables": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "a",
          "b"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "a",
          "b"
        ],
        "target": "choose_correct_statement"
      }
    ],
    "induction_clusters": [
      {
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "short_answer",
          "classify_quadrant",
          [
            "sign_reasoning"
          ],
          [
            "symbolic_condition",
            "coordinate_point"
          ]
        ],
        "source_example_ids": [
          4417,
          4435
        ],
        "answer_type": "short_answer"
      },
      {
        "grouping_reason": "merged_compatible_single_choice_tasks_with_template_families",
        "feature_signature": [
          "merged_single_choice",
          "single_choice",
          [
            "choose_correct_statement",
            "choose_possible_coordinate"
          ]
        ],
        "source_example_ids": [
          4509,
          4510
        ],
        "answer_type": "single_choice"
      }
    ],
    "induced_problem_type_specs": [
      {
        "problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "display_name": "象限判斷短答",
        "source_example_ids": [
          4417,
          4435
        ],
        "answer_contract": {
          "answer_type": "short_answer",
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "answer_equivalence": "exact_text",
          "frontend_render_choices": false
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "coordinate_point",
            "symbolic_condition"
          ],
          "required_math_objects": [
            "symbolic_condition",
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
          "variables_in_conditions_must_appear_in_target": true
        },
        "semantic_contract": {
          "reasoning_type": [
            "sign_reasoning"
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
          "template_families": [
            "classify_quadrant"
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
            "stem": "symbolic_quadrant"
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
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "short_answer",
          "classify_quadrant",
          [
            "sign_reasoning"
          ],
          [
            "symbolic_condition",
            "coordinate_point"
          ]
        ]
      },
      {
        "problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
        "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
        "display_name": "象限敘述選擇",
        "source_example_ids": [
          4509,
          4510
        ],
        "answer_contract": {
          "answer_type": "single_choice",
          "choices_required": true,
          "choice_count": 4,
          "correct_choice_count": 1,
          "answer_equivalence": "choice_label",
          "frontend_render_choices": true
        },
        "stem_contract": {
          "stem_must_not_embed_choices": true,
          "allowed_math_objects": [
            "axis_distance",
            "coordinate_point"
          ],
          "required_math_objects": [
            "axis_distance",
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
            "axis_distance_reasoning",
            "sign_reasoning"
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
          "template_families": [
            "choose_correct_statement",
            "choose_possible_coordinate"
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
          "template_slots": {
            "stem": "axis_distance_choice"
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
        "grouping_reason": "merged_compatible_single_choice_tasks_with_template_families",
        "feature_signature": [
          "merged_single_choice",
          "single_choice",
          [
            "choose_correct_statement",
            "choose_possible_coordinate"
          ]
        ]
      }
    ],
    "candidate_problem_types": [
      {
        "problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
        "proposed_problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
        "display_name": "象限判斷短答",
        "matched_example_ids": [
          4417,
          4435
        ],
        "matched_example_count": 2,
        "unmatched_example_ids": [],
        "representative_example_id": 4417,
        "structural_features": [
          "text_short"
        ],
        "answer_contract_proposal": {
          "answer_type": "short_answer",
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "answer_equivalence": "exact_text",
          "frontend_render_choices": false,
          "checker_key": "text_checker",
          "equivalence_type": "exact_string",
          "stem_contract": {
            "stem_must_not_embed_choices": true,
            "allowed_math_objects": [
              "coordinate_point",
              "symbolic_condition"
            ],
            "required_math_objects": [
              "symbolic_condition",
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
            "variables_in_conditions_must_appear_in_target": true
          },
          "semantic_contract": {
            "reasoning_type": [
              "sign_reasoning"
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
            "template_families": [
              "classify_quadrant"
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
              "stem": "symbolic_quadrant"
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
          }
        },
        "checker_key_proposal": "text_checker",
        "equivalence_type_proposal": "exact_string",
        "answer_shape": "text_short",
        "confidence": "high",
        "promote_recommendation": "recommend_promote_for_that_candidate",
        "promote_blockers": [],
        "risk_flags": [],
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "short_answer",
          "classify_quadrant",
          [
            "sign_reasoning"
          ],
          [
            "symbolic_condition",
            "coordinate_point"
          ]
        ],
        "problem_type_spec_draft": {
          "problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
          "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
          "display_name": "象限判斷短答",
          "source_example_ids": [
            4417,
            4435
          ],
          "answer_contract": {
            "answer_type": "short_answer",
            "choices_required": false,
            "choice_count": null,
            "correct_choice_count": null,
            "answer_equivalence": "exact_text",
            "frontend_render_choices": false
          },
          "stem_contract": {
            "stem_must_not_embed_choices": true,
            "allowed_math_objects": [
              "coordinate_point",
              "symbolic_condition"
            ],
            "required_math_objects": [
              "symbolic_condition",
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
            "variables_in_conditions_must_appear_in_target": true
          },
          "semantic_contract": {
            "reasoning_type": [
              "sign_reasoning"
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
            "template_families": [
              "classify_quadrant"
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
              "stem": "symbolic_quadrant"
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
          "grouping_reason": "single_signature_group",
          "feature_signature": [
            "short_answer",
            "classify_quadrant",
            [
              "sign_reasoning"
            ],
            [
              "symbolic_condition",
              "coordinate_point"
            ]
          ]
        },
        "generator_readiness": "runtime_ready",
        "template_slot": "symbolic_quadrant"
      },
      {
        "problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
        "proposed_problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
        "display_name": "象限敘述選擇",
        "matched_example_ids": [
          4509,
          4510
        ],
        "matched_example_count": 2,
        "unmatched_example_ids": [],
        "representative_example_id": 4509,
        "structural_features": [
          "choice_label"
        ],
        "answer_contract_proposal": {
          "answer_type": "single_choice",
          "choices_required": true,
          "choice_count": 4,
          "correct_choice_count": 1,
          "answer_equivalence": "choice_label",
          "frontend_render_choices": true,
          "checker_key": "choice_label_checker",
          "equivalence_type": "choice_label",
          "stem_contract": {
            "stem_must_not_embed_choices": true,
            "allowed_math_objects": [
              "axis_distance",
              "coordinate_point"
            ],
            "required_math_objects": [
              "axis_distance",
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
              "axis_distance_reasoning",
              "sign_reasoning"
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
            "template_families": [
              "choose_correct_statement",
              "choose_possible_coordinate"
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
            "template_slots": {
              "stem": "axis_distance_choice"
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
          }
        },
        "checker_key_proposal": "choice_label_checker",
        "equivalence_type_proposal": "choice_label",
        "answer_shape": "choice_label",
        "confidence": "high",
        "promote_recommendation": "recommend_promote_for_that_candidate",
        "promote_blockers": [],
        "risk_flags": [],
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "merged_compatible_single_choice_tasks_with_template_families",
        "feature_signature": [
          "merged_single_choice",
          "single_choice",
          [
            "choose_correct_statement",
            "choose_possible_coordinate"
          ]
        ],
        "problem_type_spec_draft": {
          "problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
          "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
          "display_name": "象限敘述選擇",
          "source_example_ids": [
            4509,
            4510
          ],
          "answer_contract": {
            "answer_type": "single_choice",
            "choices_required": true,
            "choice_count": 4,
            "correct_choice_count": 1,
            "answer_equivalence": "choice_label",
            "frontend_render_choices": true
          },
          "stem_contract": {
            "stem_must_not_embed_choices": true,
            "allowed_math_objects": [
              "axis_distance",
              "coordinate_point"
            ],
            "required_math_objects": [
              "axis_distance",
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
              "axis_distance_reasoning",
              "sign_reasoning"
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
            "template_families": [
              "choose_correct_statement",
              "choose_possible_coordinate"
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
            "template_slots": {
              "stem": "axis_distance_choice"
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
          "grouping_reason": "merged_compatible_single_choice_tasks_with_template_families",
          "feature_signature": [
            "merged_single_choice",
            "single_choice",
            [
              "choose_correct_statement",
              "choose_possible_coordinate"
            ]
          ]
        },
        "generator_readiness": "runtime_ready",
        "template_slot": "axis_distance_choice"
      }
    ],
    "per_example_classification": [
      {
        "example_id": 4417,
        "detected_problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
        "example_feature": {
          "source_example_id": 4417,
          "question_text": "若點$P\\left( a,b \\right)$位在第一象限且a < b，則$Q\\left( a-b,{{a}^{2}}b \\right)$位在第幾象限？",
          "answer": "",
          "choices": [],
          "has_choices": false,
          "stem_embeds_choices": false,
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "checker": "text_checker",
          "equivalence": "exact_string",
          "math_objects": [
            "coordinate_point",
            "symbolic_condition"
          ],
          "target_task": "classify_quadrant",
          "reasoning_type": [
            "sign_reasoning"
          ],
          "required_derivation": true,
          "variables": [
            "P",
            "Q",
            "a",
            "b"
          ],
          "givens": [
            "P",
            "Q",
            "a",
            "b"
          ],
          "target": "classify_quadrant"
        },
        "answer_shape": "text_short",
        "classification_confidence": "high",
        "classification_reason": "feature_signature_induction",
        "risk_flags": []
      },
      {
        "example_id": 4435,
        "detected_problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
        "example_feature": {
          "source_example_id": 4435,
          "question_text": "設a、b為實數，且a < b < 0，則點$Q\\left( ab,a+b \\right)$在第幾象限？",
          "answer": "",
          "choices": [],
          "has_choices": false,
          "stem_embeds_choices": false,
          "answer_type": "short_answer",
          "answer_shape": "text_short",
          "checker": "text_checker",
          "equivalence": "exact_string",
          "math_objects": [
            "coordinate_point",
            "symbolic_condition"
          ],
          "target_task": "classify_quadrant",
          "reasoning_type": [
            "sign_reasoning"
          ],
          "required_derivation": true,
          "variables": [
            "Q",
            "a",
            "b"
          ],
          "givens": [
            "Q",
            "a",
            "b"
          ],
          "target": "classify_quadrant"
        },
        "answer_shape": "text_short",
        "classification_confidence": "high",
        "classification_reason": "feature_signature_induction",
        "risk_flags": []
      },
      {
        "example_id": 4509,
        "detected_problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
        "example_feature": {
          "source_example_id": 4509,
          "question_text": "設A點為坐標平面上一點，且A點到x軸及y軸之距離分別為3和4，則下列何者可能為A點之坐標？ 　(A)$\\left( -4,-3 \\right)$　(B)$\\left( -3,4 \\right)$　\r\n(C)$\\left( -3,-4 \\right)$　(D)$\\left( 3,4 \\right)$。",
          "answer": "",
          "choices": [
            "$\\left( -4,-3 \\right)$",
            "$\\left( -3,4 \\right)$",
            "$\\left( -3,-4 \\right)$",
            "$\\left( 3,4 \\right)$。"
          ],
          "has_choices": true,
          "stem_embeds_choices": true,
          "answer_type": "single_choice",
          "answer_shape": "choice_label",
          "checker": "choice_label_checker",
          "equivalence": "choice_label",
          "math_objects": [
            "axis_distance",
            "coordinate_point"
          ],
          "target_task": "choose_possible_coordinate",
          "reasoning_type": [
            "axis_distance_reasoning"
          ],
          "required_derivation": true,
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
          "target": "choose_possible_coordinate"
        },
        "answer_shape": "choice_label",
        "classification_confidence": "high",
        "classification_reason": "feature_signature_induction",
        "risk_flags": [
          "stem_embeds_choices"
        ]
      },
      {
        "example_id": 4510,
        "detected_problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
        "example_feature": {
          "source_example_id": 4510,
          "question_text": "已知點$P\\left( a-b,ab \\right)$在坐標平面的第四象限，則下列敘述何者正確？\r\n(A)$A\\left( -a,b \\right)$在第一象限　(B)$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限\r\n(C)$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限　(D)$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。",
          "answer": "",
          "choices": [
            "$A\\left( -a,b \\right)$在第一象限",
            "$B\\left( \\left| ab \\right|,-{{a}^{2}}b \\right)$在第二象限",
            "$C\\left( \\frac{{{a}^{2}}}{b},-b \\right)$在第三象限",
            "$D\\left( a-b,\\frac{a}{b} \\right)$在第四象限。"
          ],
          "has_choices": true,
          "stem_embeds_choices": true,
          "answer_type": "single_choice",
          "answer_shape": "choice_label",
          "checker": "choice_label_checker",
          "equivalence": "choice_label",
          "math_objects": [
            "coordinate_point"
          ],
          "target_task": "choose_correct_statement",
          "reasoning_type": [
            "sign_reasoning"
          ],
          "required_derivation": true,
          "variables": [
            "A",
            "B",
            "C",
            "D",
            "P",
            "a",
            "b"
          ],
          "givens": [
            "A",
            "B",
            "C",
            "D",
            "P",
            "a",
            "b"
          ],
          "target": "choose_correct_statement"
        },
        "answer_shape": "choice_label",
        "classification_confidence": "high",
        "classification_reason": "feature_signature_induction",
        "risk_flags": [
          "stem_embeds_choices"
        ]
      }
    ],
    "split_or_merge_recommendation": "induced_from_source_features",
    "problem_type_spec_first": true,
    "spec_defined_problem_type_ids": [
      "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
      "single_choice_choose_correct_statement_axis_distance_coordinate_point"
    ],
    "classifier_gate": {
      "status": "classifier_auto_pending_promote_with_warning",
      "allowed": true,
      "warnings": [
        "insufficient_examples"
      ]
    },
    "generator_draft_gate": {
      "status": "generator_draft_allowed_with_low_source_warning",
      "allowed": true,
      "warnings": [
        "low_source_examples"
      ]
    },
    "runtime_ready_gate": {
      "status": "blocked_insufficient_examples",
      "allowed": false,
      "blockers": [
        "blocked_insufficient_examples"
      ]
    },
    "exception_review_gate": {
      "required": false,
      "reasons": []
    },
    "next_action": "phase2_generate_from_induced_specs",
    "curated_specs_available": true
  },
  "classifier_source": "rule_pack+phase1_induction",
  "ai_bootstrap_used": false,
  "ai_bootstrap_status": "not_used",
  "ai_bootstrap_confidence_summary": {},
  "inspect_report_note": "",
  "ai_bootstrap_error": "",
  "ai_bootstrap_raw_response_preview": "",
  "ai_bootstrap_validation_errors": [],
  "ai_bootstrap_prompt_version": "",
  "ai_bootstrap_model": "",
  "ai_bootstrap_provider": "",
  "ai_bootstrap_config_source": "",
  "default_problem_type_used": false,
  "problem_type_spec_first": true,
  "spec_defined_problem_type_ids": [
    "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
    "single_choice_choose_correct_statement_axis_distance_coordinate_point"
  ],
  "spec_mode": "induce_from_sources",
  "induced_problem_type_specs": [
    {
      "problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
      "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "display_name": "象限判斷短答",
      "source_example_ids": [
        4417,
        4435
      ],
      "answer_contract": {
        "answer_type": "short_answer",
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "answer_equivalence": "exact_text",
        "frontend_render_choices": false
      },
      "stem_contract": {
        "stem_must_not_embed_choices": true,
        "allowed_math_objects": [
          "coordinate_point",
          "symbolic_condition"
        ],
        "required_math_objects": [
          "symbolic_condition",
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
        "variables_in_conditions_must_appear_in_target": true
      },
      "semantic_contract": {
        "reasoning_type": [
          "sign_reasoning"
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
        "template_families": [
          "classify_quadrant"
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
          "stem": "symbolic_quadrant"
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
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "short_answer",
        "classify_quadrant",
        [
          "sign_reasoning"
        ],
        [
          "symbolic_condition",
          "coordinate_point"
        ]
      ]
    },
    {
      "problem_type_id": "single_choice_choose_correct_statement_axis_distance_coordinate_point",
      "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
      "display_name": "象限敘述選擇",
      "source_example_ids": [
        4509,
        4510
      ],
      "answer_contract": {
        "answer_type": "single_choice",
        "choices_required": true,
        "choice_count": 4,
        "correct_choice_count": 1,
        "answer_equivalence": "choice_label",
        "frontend_render_choices": true
      },
      "stem_contract": {
        "stem_must_not_embed_choices": true,
        "allowed_math_objects": [
          "axis_distance",
          "coordinate_point"
        ],
        "required_math_objects": [
          "axis_distance",
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
          "axis_distance_reasoning",
          "sign_reasoning"
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
        "template_families": [
          "choose_correct_statement",
          "choose_possible_coordinate"
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
        "template_slots": {
          "stem": "axis_distance_choice"
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
      "grouping_reason": "merged_compatible_single_choice_tasks_with_template_families",
      "feature_signature": [
        "merged_single_choice",
        "single_choice",
        [
          "choose_correct_statement",
          "choose_possible_coordinate"
        ]
      ]
    }
  ],
  "induction_clusters": [
    {
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "short_answer",
        "classify_quadrant",
        [
          "sign_reasoning"
        ],
        [
          "symbolic_condition",
          "coordinate_point"
        ]
      ],
      "source_example_ids": [
        4417,
        4435
      ],
      "answer_type": "short_answer"
    },
    {
      "grouping_reason": "merged_compatible_single_choice_tasks_with_template_families",
      "feature_signature": [
        "merged_single_choice",
        "single_choice",
        [
          "choose_correct_statement",
          "choose_possible_coordinate"
        ]
      ],
      "source_example_ids": [
        4509,
        4510
      ],
      "answer_type": "single_choice"
    }
  ],
  "human_review_items": []
}
```
