# Gencode Phase1 Summary: vh_數學B1_DivisionPointCoordinates

- spec_mode: `induce_from_sources`

## Source alignment

- source_alignment_status: `warn`
- skill_problem_type_alignment_status: `warn`
- alignment_score: `0.0172`
- alignment_blockers: []
- alignment_warnings: ['alignment_score_below_recommended_threshold']

| example_id | target_task | task_family | alignment_score | included | exclude_reason | stem_preview |
| --- | --- | --- | --- | --- | --- | --- |
| 4420 | compute_distance_between_two_points | distance_between_two_points_family | 0.0294 | True |  | (1) 坐標平面上三點$A(3,4)$、$B\left( 6,-5 \right)$、$C\left( x,y \rig |
| 4421 | compute_distance_between_two_points | distance_between_two_points_family | 0.0294 | True |  | 如圖所示，在直角坐標平面上，醫院位置為點$A\left( 1,0 \right)$，學校的位置在$B(-3,4)$，小恩 |
| 4423 | compute_numeric | generic_numeric_family | 0.0 | False | source_example_skill_mismatch | 已知$A\left( -1,1 \right)$、$B(-3,-3)$、$C\left( 4,-4 \right)$，試 |
| 4427 | compute_distance_between_two_points | distance_between_two_points_family | 0.0312 | True |  | 坐標平面上兩點$A\left( -2,6 \right)$、$B\left( 3,1 \right)$，若點C在$\ov |
| 4438 | compute_distance_between_two_points | distance_between_two_points_family | 0.0312 | True |  | 坐標平面上兩點$A\left( -3,0 \right)$、$B(9,6)$，若點P在$\overline{AB}$上， |
| 4512 | compute_distance_between_two_points | distance_between_two_points_family | 0.0323 | True |  | 若$A\left( 1,1 \right)$、$B\left( -5,4 \right)$、$P\left( x,y \ |
| 4513 | compute_distance_between_two_points | distance_between_two_points_family | 0.0323 | True |  | 設P點介於$A\left( 4,-2 \right)$及$B\left( -2,6 \right)$兩點之間，且$3\o |

## Example features

| example_id | answer_type | target_task | has_choices | stem_embeds_choices | math_objects |
| --- | --- | --- | --- | --- | --- |
| 4420 | short_answer | compute_distance_between_two_points | False | False | coordinate_point, distance_formula, segment_length, two_coordinate_points |
| 4421 | short_answer | compute_distance_between_two_points | False | False | coordinate_point, distance_formula, segment_length, two_coordinate_points |
| 4423 | short_answer | compute_numeric | False | False | coordinate_point, two_coordinate_points |
| 4427 | short_answer | compute_distance_between_two_points | False | False | coordinate_point, distance_formula, segment_length, two_coordinate_points |
| 4438 | short_answer | compute_distance_between_two_points | False | False | coordinate_point, distance_formula, segment_length, two_coordinate_points |
| 4512 | single_choice | compute_distance_between_two_points | True | True | coordinate_point, distance_formula, segment_length, two_coordinate_points |
| 4513 | single_choice | compute_distance_between_two_points | True | True | coordinate_point, distance_formula, segment_length, two_coordinate_points |

## Induction clusters

### Cluster 1
- answer_type: `short_answer`
- source_example_ids: [4420, 4421, 4427, 4438]
- grouping_reason: single_signature_group
- feature_signature: `['short_answer', 'compute_distance_between_two_points', ('distance_formula_reasoning',), ('coordinate_point', 'distance_formula')]`

### Cluster 2
- answer_type: `single_choice`
- source_example_ids: [4512, 4513]
- grouping_reason: single_signature_group
- feature_signature: `['single_choice', 'compute_distance_between_two_points', ('distance_formula_reasoning',), ('coordinate_point', 'distance_formula')]`


## Candidate problem types

| problem_type_id | display_name | answer_type | source_examples | grouping_reason |
| --- | --- | --- | --- | --- |
| short_answer_compute_distance_between_two_points_coordinate_point_distance_formu | 兩點距離計算 | numeric_or_radical | [4420, 4421, 4427, 4438] | single_signature_group |
| single_choice_compute_distance_between_two_points_coordinate_point_distance_form | single_choice / compute_distance_between_two_points | single_choice | [4512, 4513] | single_signature_group |

## phase1
```json
{
  "ok": true,
  "phase": "phase1",
  "skill_id": "vh_數學B1_DivisionPointCoordinates",
  "source_example_count": 7,
  "source_alignment_status": "warn",
  "skill_problem_type_alignment_status": "warn",
  "alignment_score": 0.0172,
  "alignment_warnings": [
    "alignment_score_below_recommended_threshold"
  ],
  "alignment_blockers": [],
  "semantic_alignment": {
    "skill_terms": [
      "1 坐標系與函數圖形",
      "2 平面坐標系與線型函數",
      "coordinates",
      "divi",
      "division",
      "divisionpointcoordinates",
      "ionpointcoordinate",
      "point",
      "solve_unknown_coordinate_from_two_point_distance",
      "vh",
      "vocational",
      "分點坐標",
      "坐標系與函數圖形",
      "平面坐標系與線型函數",
      "數學b",
      "數學b1"
    ],
    "source_terms": [
      "ab",
      "abc的重心坐標",
      "ac",
      "ap",
      "bc",
      "b之間",
      "cb",
      "compute_distance",
      "compute_distance_between_two_points",
      "compute_numeric",
      "coordinate_point",
      "distance_formula",
      "left",
      "overline",
      "pa",
      "pb",
      "right",
      "segment_length",
      "short_answer",
      "single_choice",
      "solve_unknown_coordinate_from_two_point_distance",
      "two_coordinate_points",
      "三點共線",
      "且p介於a",
      "且已知小恩家到醫院的距離等於小恩家到學校距離的3倍",
      "兩點之間",
      "則p點坐標為",
      "則p點與原點o的距離為何",
      "在直角坐標平面上",
      "坐標平面上三點",
      "坐標平面上兩點",
      "如圖所示",
      "學校的位置在",
      "小恩的家位於線段ab",
      "已知",
      "若點c在",
      "若點p在",
      "設p點介於",
      "試求",
      "試求c點坐標",
      "試求p點坐標",
      "試求小恩家在坐標平面上的位置",
      "醫院位置為點"
    ],
    "problem_type_terms": [
      "an",
      "answer",
      "between",
      "choice",
      "compute",
      "compute_distance_between_two_points",
      "compute_numeric",
      "coordinate",
      "di",
      "distance",
      "distance_formula_reasoning",
      "form",
      "formu",
      "hort",
      "ingle",
      "numeric_or_radical",
      "point",
      "point_quadrant",
      "point_quadrant_choice",
      "points",
      "short",
      "single",
      "single_choice",
      "single_choice / compute_distance_between_two_points",
      "solve_unknown_coordinate_from_two_point_distance",
      "tance",
      "two",
      "wer",
      "兩點距離計算"
    ],
    "expected_task_candidates": [
      "choose_possible_coordinate",
      "compare_distances_between_points",
      "compute_distance",
      "compute_distance_between_two_points",
      "compute_missing_coordinate_from_two_point_distance",
      "solve_parameter_from_distance_formula",
      "solve_unknown_coordinate_from_two_point_distance",
      "verify_distance_between_two_points"
    ],
    "expected_skill_families": [
      "distance_between_two_points_family"
    ],
    "source_family_distribution": {
      "distance_between_two_points_family": 6,
      "generic_numeric_family": 1
    },
    "candidate_problem_type_families": [
      "distance_between_two_points_family"
    ],
    "dominant_source_task": "compute_distance_between_two_points",
    "dominant_source_task_ratio": 0.8571,
    "dominant_source_family": [
      "distance_between_two_points_family"
    ],
    "dominant_source_family_ratio": 0.8571,
    "skill_source_score": 0.0172,
    "skill_problem_type_score": 0.0556,
    "source_problem_type_score": 0.0678,
    "per_problem_type_scores": [
      {
        "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "inferred_tasks": [
          "compute_distance",
          "compute_distance_between_two_points"
        ],
        "skill_problem_type_score": 0.0556,
        "source_problem_type_score": 0.0484,
        "task_consistent_with_skill": true,
        "family_consistent_with_skill": true,
        "answer_contract_supported": true
      },
      {
        "problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "inferred_tasks": [
          "compute_distance",
          "compute_distance_between_two_points"
        ],
        "skill_problem_type_score": 0.0588,
        "source_problem_type_score": 0.0678,
        "task_consistent_with_skill": true,
        "family_consistent_with_skill": true,
        "answer_contract_supported": true
      }
    ],
    "decision": "warn",
    "blockers": [],
    "warnings": [
      "alignment_score_below_recommended_threshold"
    ]
  },
  "source_family_distribution": {
    "distance_between_two_points_family": 6,
    "generic_numeric_family": 1
  },
  "candidate_problem_type_families": [
    "distance_between_two_points_family"
  ],
  "expected_skill_families": [
    "distance_between_two_points_family"
  ],
  "excluded_source_examples": [
    {
      "example_id": 4423,
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "alignment_score": 0.0,
      "aligned_with_skill": false,
      "included_in_phase1": false,
      "exclude_reason": "source_example_skill_mismatch",
      "skill_id": "vh_數學B1_DivisionPointCoordinates",
      "title_stem_preview": "已知$A\\left( -1,1 \\right)$、$B(-3,-3)$、$C\\left( 4,-4 \\right)$，試求△ABC的重心坐標。"
    }
  ],
  "source_example_alignment": [
    {
      "example_id": 4420,
      "target_task": "compute_distance_between_two_points",
      "task_family": "distance_between_two_points_family",
      "alignment_score": 0.0294,
      "aligned_with_skill": true,
      "included_in_phase1": true,
      "exclude_reason": "",
      "skill_id": "vh_數學B1_DivisionPointCoordinates",
      "title_stem_preview": "(1) 坐標平面上三點$A(3,4)$、$B\\left( 6,-5 \\right)$、$C\\left( x,y \\right)$，若點C在$\\overline{"
    },
    {
      "example_id": 4421,
      "target_task": "compute_distance_between_two_points",
      "task_family": "distance_between_two_points_family",
      "alignment_score": 0.0294,
      "aligned_with_skill": true,
      "included_in_phase1": true,
      "exclude_reason": "",
      "skill_id": "vh_數學B1_DivisionPointCoordinates",
      "title_stem_preview": "如圖所示，在直角坐標平面上，醫院位置為點$A\\left( 1,0 \\right)$，學校的位置在$B(-3,4)$，小恩的家位於線段AB（$\\overline{"
    },
    {
      "example_id": 4423,
      "target_task": "compute_numeric",
      "task_family": "generic_numeric_family",
      "alignment_score": 0.0,
      "aligned_with_skill": false,
      "included_in_phase1": false,
      "exclude_reason": "source_example_skill_mismatch",
      "skill_id": "vh_數學B1_DivisionPointCoordinates",
      "title_stem_preview": "已知$A\\left( -1,1 \\right)$、$B(-3,-3)$、$C\\left( 4,-4 \\right)$，試求△ABC的重心坐標。"
    },
    {
      "example_id": 4427,
      "target_task": "compute_distance_between_two_points",
      "task_family": "distance_between_two_points_family",
      "alignment_score": 0.0312,
      "aligned_with_skill": true,
      "included_in_phase1": true,
      "exclude_reason": "",
      "skill_id": "vh_數學B1_DivisionPointCoordinates",
      "title_stem_preview": "坐標平面上兩點$A\\left( -2,6 \\right)$、$B\\left( 3,1 \\right)$，若點C在$\\overline{AB}$上，且$2\\ove"
    },
    {
      "example_id": 4438,
      "target_task": "compute_distance_between_two_points",
      "task_family": "distance_between_two_points_family",
      "alignment_score": 0.0312,
      "aligned_with_skill": true,
      "included_in_phase1": true,
      "exclude_reason": "",
      "skill_id": "vh_數學B1_DivisionPointCoordinates",
      "title_stem_preview": "坐標平面上兩點$A\\left( -3,0 \\right)$、$B(9,6)$，若點P在$\\overline{AB}$上，且$\\overline{AP}=2\\ov"
    },
    {
      "example_id": 4512,
      "target_task": "compute_distance_between_two_points",
      "task_family": "distance_between_two_points_family",
      "alignment_score": 0.0323,
      "aligned_with_skill": true,
      "included_in_phase1": true,
      "exclude_reason": "",
      "skill_id": "vh_數學B1_DivisionPointCoordinates",
      "title_stem_preview": "若$A\\left( 1,1 \\right)$、$B\\left( -5,4 \\right)$、$P\\left( x,y \\right)$三點共線，且P介於A、B之"
    },
    {
      "example_id": 4513,
      "target_task": "compute_distance_between_two_points",
      "task_family": "distance_between_two_points_family",
      "alignment_score": 0.0323,
      "aligned_with_skill": true,
      "included_in_phase1": true,
      "exclude_reason": "",
      "skill_id": "vh_數學B1_DivisionPointCoordinates",
      "title_stem_preview": "設P點介於$A\\left( 4,-2 \\right)$及$B\\left( -2,6 \\right)$兩點之間，且$3\\overline{PA}=2\\overli"
    }
  ],
  "candidate_problem_types": [
    {
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
      "proposed_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
      "display_name": "兩點距離計算",
      "matched_example_ids": [
        4420,
        4421,
        4427,
        4438
      ],
      "matched_example_count": 4,
      "unmatched_example_ids": [],
      "representative_example_id": 4420,
      "structural_features": [
        "numeric"
      ],
      "answer_contract_proposal": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "numeric_or_radical",
        "answer_shape": "scalar",
        "answer_equivalence": "math_expression_equivalence",
        "checker": "expression_equivalence_checker",
        "accepted_formats": [
          "5",
          "5.0",
          "\\sqrt{13}",
          "sqrt(13)",
          "2\\sqrt{5}",
          "2√5"
        ],
        "checker_key": "expression_equivalence_checker",
        "equivalence_type": "expression_equivalence",
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
        }
      },
      "checker_key_proposal": "expression_equivalence_checker",
      "equivalence_type_proposal": "expression_equivalence",
      "answer_shape": "numeric",
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": [
        "alignment_score_below_recommended_threshold"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "short_answer",
        "compute_distance_between_two_points",
        [
          "distance_formula_reasoning"
        ],
        [
          "coordinate_point",
          "distance_formula"
        ]
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "display_name": "兩點距離計算",
        "source_example_ids": [
          4420,
          4421,
          4427,
          4438
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "numeric_or_radical",
          "answer_shape": "scalar",
          "answer_equivalence": "math_expression_equivalence",
          "checker": "expression_equivalence_checker",
          "accepted_formats": [
            "5",
            "5.0",
            "\\sqrt{13}",
            "sqrt(13)",
            "2\\sqrt{5}",
            "2√5"
          ]
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
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "short_answer",
          "compute_distance_between_two_points",
          [
            "distance_formula_reasoning"
          ],
          [
            "coordinate_point",
            "distance_formula"
          ]
        ]
      },
      "generator_readiness": "runtime_ready",
      "template_slot": "point_quadrant",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0556,
        "source_problem_type_score": 0.0484,
        "task_consistent_with_skill": true
      }
    },
    {
      "problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
      "proposed_problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
      "display_name": "single_choice / compute_distance_between_two_points",
      "matched_example_ids": [
        4512,
        4513
      ],
      "matched_example_count": 2,
      "unmatched_example_ids": [],
      "representative_example_id": 4512,
      "structural_features": [
        "choice_label"
      ],
      "answer_contract_proposal": {
        "choices_required": true,
        "choice_count": 4,
        "correct_choice_count": 1,
        "frontend_render_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "answer_equivalence": "choice_label",
        "checker": "choice_label_checker",
        "accepted_formats": [
          "A",
          "B",
          "C",
          "D"
        ],
        "checker_key": "choice_label_checker",
        "equivalence_type": "choice_label",
        "selected_checker": "choice_label_checker",
        "checker_capability_status": "ok",
        "checker_contract_blockers": [],
        "checker_contract_warnings": [],
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
          "template_families": [
            "compute_distance_between_two_points"
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
            "stem": "point_quadrant_choice"
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
      "risk_flags": [
        "alignment_score_below_recommended_threshold"
      ],
      "checker_contract_warnings": [],
      "spec_source": "phase1_induced_draft",
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "single_choice",
        "compute_distance_between_two_points",
        [
          "distance_formula_reasoning"
        ],
        [
          "coordinate_point",
          "distance_formula"
        ]
      ],
      "problem_type_spec_draft": {
        "problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "display_name": "single_choice / compute_distance_between_two_points",
        "source_example_ids": [
          4512,
          4513
        ],
        "answer_contract": {
          "choices_required": true,
          "choice_count": 4,
          "correct_choice_count": 1,
          "frontend_render_choices": true,
          "answer_type": "single_choice",
          "answer_shape": "choice_label",
          "answer_equivalence": "choice_label",
          "checker": "choice_label_checker",
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
          "template_families": [
            "compute_distance_between_two_points"
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
            "stem": "point_quadrant_choice"
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
          "single_choice",
          "compute_distance_between_two_points",
          [
            "distance_formula_reasoning"
          ],
          [
            "coordinate_point",
            "distance_formula"
          ]
        ]
      },
      "generator_readiness": "runtime_ready",
      "template_slot": "point_quadrant_choice",
      "semantic_alignment": {
        "skill_problem_type_score": 0.0588,
        "source_problem_type_score": 0.0678,
        "task_consistent_with_skill": true
      }
    }
  ],
  "per_example_classification": [
    {
      "example_id": 4420,
      "detected_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
      "example_feature": {
        "source_example_id": 4420,
        "question_text": "(1) 坐標平面上三點$A(3,4)$、$B\\left( 6,-5 \\right)$、$C\\left( x,y \\right)$，若點C在$\\overline{AB}$上，且\n $\\overline{AC}:\\overline{CB}=2:1$，試求C點坐標。\n(2) 坐標平面上兩點$A(-2,-2)$、$B(5,5)$，若點C在$\\overline{AB}$上，且$4\\overline{AC}=3\\overline{BC}$，\n試求C點坐標。",
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
        "variables": [
          "A",
          "B",
          "C",
          "x",
          "y"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "x",
          "y"
        ],
        "target": "compute_distance_between_two_points"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4421,
      "detected_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
      "example_feature": {
        "source_example_id": 4421,
        "question_text": "如圖所示，在直角坐標平面上，醫院位置為點$A\\left( 1,0 \\right)$，學校的位置在$B(-3,4)$，小恩的家位於線段AB（$\\overline{AB}$）上，且已知小恩家到醫院的距離等於小恩家到學校距離的3倍，試求小恩家在坐標平面上的位置$P\\left( x,y \\right)$。",
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
        "variables": [
          "A",
          "B",
          "P",
          "x",
          "y"
        ],
        "givens": [
          "A",
          "B",
          "P",
          "x",
          "y"
        ],
        "target": "compute_distance_between_two_points"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4423,
      "detected_problem_type_id": "unknown",
      "example_feature": {
        "source_example_id": 4423,
        "question_text": "已知$A\\left( -1,1 \\right)$、$B(-3,-3)$、$C\\left( 4,-4 \\right)$，試求△ABC的重心坐標。",
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
          "two_coordinate_points"
        ],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
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
        "target": "compute_numeric"
      },
      "answer_shape": "text_short",
      "classification_confidence": "low",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4427,
      "detected_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
      "example_feature": {
        "source_example_id": 4427,
        "question_text": "坐標平面上兩點$A\\left( -2,6 \\right)$、$B\\left( 3,1 \\right)$，若點C在$\\overline{AB}$上，且$2\\overline{AC}=3\\overline{BC}$，\n試求C點坐標。",
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
        "variables": [
          "A",
          "B"
        ],
        "givens": [
          "A",
          "B"
        ],
        "target": "compute_distance_between_two_points"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4438,
      "detected_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
      "example_feature": {
        "source_example_id": 4438,
        "question_text": "坐標平面上兩點$A\\left( -3,0 \\right)$、$B(9,6)$，若點P在$\\overline{AB}$上，且$\\overline{AP}=2\\overline{PB}$，\n試求P點坐標。",
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
        "variables": [
          "A",
          "B"
        ],
        "givens": [
          "A",
          "B"
        ],
        "target": "compute_distance_between_two_points"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4512,
      "detected_problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
      "example_feature": {
        "source_example_id": 4512,
        "question_text": "若$A\\left( 1,1 \\right)$、$B\\left( -5,4 \\right)$、$P\\left( x,y \\right)$三點共線，且P介於A、B之間，又$\\overline{AP}:\\overline{PB}=2:1$，則P點坐標為 (A)$\\left( 3,3 \\right)$ (B)$\\left( -3,3 \\right)$ (C)$\\left( 3,-3 \\right)$ (D)$\\left( -3,-3 \\right)$。",
        "answer": "",
        "choices": [
          "$\\left( 3,3 \\right)$",
          "$\\left( -3,3 \\right)$",
          "$\\left( 3,-3 \\right)$",
          "$\\left( -3,-3 \\right)$。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
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
        "variables": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "x",
          "y"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "x",
          "y"
        ],
        "target": "compute_distance_between_two_points"
      },
      "answer_shape": "choice_label",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": [
        "stem_embeds_choices"
      ]
    },
    {
      "example_id": 4513,
      "detected_problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
      "example_feature": {
        "source_example_id": 4513,
        "question_text": "設P點介於$A\\left( 4,-2 \\right)$及$B\\left( -2,6 \\right)$兩點之間，且$3\\overline{PA}=2\\overline{PB}$，則P點與原點O的距離為何？ (A) 2 (B) 3 (C) 4 (D) 5。",
        "answer": "",
        "choices": [
          "2",
          "3",
          "4",
          "5。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
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
        "target": "compute_distance_between_two_points"
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
      "example_id": 4420,
      "detected_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
      "example_feature": {
        "source_example_id": 4420,
        "question_text": "(1) 坐標平面上三點$A(3,4)$、$B\\left( 6,-5 \\right)$、$C\\left( x,y \\right)$，若點C在$\\overline{AB}$上，且\n $\\overline{AC}:\\overline{CB}=2:1$，試求C點坐標。\n(2) 坐標平面上兩點$A(-2,-2)$、$B(5,5)$，若點C在$\\overline{AB}$上，且$4\\overline{AC}=3\\overline{BC}$，\n試求C點坐標。",
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
        "variables": [
          "A",
          "B",
          "C",
          "x",
          "y"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "x",
          "y"
        ],
        "target": "compute_distance_between_two_points"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4421,
      "detected_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
      "example_feature": {
        "source_example_id": 4421,
        "question_text": "如圖所示，在直角坐標平面上，醫院位置為點$A\\left( 1,0 \\right)$，學校的位置在$B(-3,4)$，小恩的家位於線段AB（$\\overline{AB}$）上，且已知小恩家到醫院的距離等於小恩家到學校距離的3倍，試求小恩家在坐標平面上的位置$P\\left( x,y \\right)$。",
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
        "variables": [
          "A",
          "B",
          "P",
          "x",
          "y"
        ],
        "givens": [
          "A",
          "B",
          "P",
          "x",
          "y"
        ],
        "target": "compute_distance_between_two_points"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4423,
      "detected_problem_type_id": "unknown",
      "example_feature": {
        "source_example_id": 4423,
        "question_text": "已知$A\\left( -1,1 \\right)$、$B(-3,-3)$、$C\\left( 4,-4 \\right)$，試求△ABC的重心坐標。",
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
          "two_coordinate_points"
        ],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
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
        "target": "compute_numeric"
      },
      "answer_shape": "text_short",
      "classification_confidence": "low",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4427,
      "detected_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
      "example_feature": {
        "source_example_id": 4427,
        "question_text": "坐標平面上兩點$A\\left( -2,6 \\right)$、$B\\left( 3,1 \\right)$，若點C在$\\overline{AB}$上，且$2\\overline{AC}=3\\overline{BC}$，\n試求C點坐標。",
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
        "variables": [
          "A",
          "B"
        ],
        "givens": [
          "A",
          "B"
        ],
        "target": "compute_distance_between_two_points"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4438,
      "detected_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
      "example_feature": {
        "source_example_id": 4438,
        "question_text": "坐標平面上兩點$A\\left( -3,0 \\right)$、$B(9,6)$，若點P在$\\overline{AB}$上，且$\\overline{AP}=2\\overline{PB}$，\n試求P點坐標。",
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
        "variables": [
          "A",
          "B"
        ],
        "givens": [
          "A",
          "B"
        ],
        "target": "compute_distance_between_two_points"
      },
      "answer_shape": "text_short",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": []
    },
    {
      "example_id": 4512,
      "detected_problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
      "example_feature": {
        "source_example_id": 4512,
        "question_text": "若$A\\left( 1,1 \\right)$、$B\\left( -5,4 \\right)$、$P\\left( x,y \\right)$三點共線，且P介於A、B之間，又$\\overline{AP}:\\overline{PB}=2:1$，則P點坐標為 (A)$\\left( 3,3 \\right)$ (B)$\\left( -3,3 \\right)$ (C)$\\left( 3,-3 \\right)$ (D)$\\left( -3,-3 \\right)$。",
        "answer": "",
        "choices": [
          "$\\left( 3,3 \\right)$",
          "$\\left( -3,3 \\right)$",
          "$\\left( 3,-3 \\right)$",
          "$\\left( -3,-3 \\right)$。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
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
        "variables": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "x",
          "y"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "x",
          "y"
        ],
        "target": "compute_distance_between_two_points"
      },
      "answer_shape": "choice_label",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": [
        "stem_embeds_choices"
      ]
    },
    {
      "example_id": 4513,
      "detected_problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
      "example_feature": {
        "source_example_id": 4513,
        "question_text": "設P點介於$A\\left( 4,-2 \\right)$及$B\\left( -2,6 \\right)$兩點之間，且$3\\overline{PA}=2\\overline{PB}$，則P點與原點O的距離為何？ (A) 2 (B) 3 (C) 4 (D) 5。",
        "answer": "",
        "choices": [
          "2",
          "3",
          "4",
          "5。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
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
        "target": "compute_distance_between_two_points"
      },
      "answer_shape": "choice_label",
      "classification_confidence": "high",
      "classification_reason": "feature_signature_induction",
      "risk_flags": [
        "stem_embeds_choices"
      ]
    }
  ],
  "unclassified_examples": [
    4423
  ],
  "risk_examples": [
    4512,
    4513
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
    "phase1_summary_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DivisionPointCoordinates_phase1_summary.json",
    "phase1_summary_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DivisionPointCoordinates_phase1_summary.md"
  },
  "next_action": "phase2_generate_from_induced_specs",
  "timestamp": "2026-05-29T08:19:13.639618+00:00",
  "dry_run": true,
  "auto_review_summary": {
    "skill_id": "vh_數學B1_DivisionPointCoordinates",
    "spec_mode": "induce_from_sources",
    "example_features": [
      {
        "source_example_id": 4420,
        "question_text": "(1) 坐標平面上三點$A(3,4)$、$B\\left( 6,-5 \\right)$、$C\\left( x,y \\right)$，若點C在$\\overline{AB}$上，且\n $\\overline{AC}:\\overline{CB}=2:1$，試求C點坐標。\n(2) 坐標平面上兩點$A(-2,-2)$、$B(5,5)$，若點C在$\\overline{AB}$上，且$4\\overline{AC}=3\\overline{BC}$，\n試求C點坐標。",
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
        "variables": [
          "A",
          "B",
          "C",
          "x",
          "y"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "x",
          "y"
        ],
        "target": "compute_distance_between_two_points"
      },
      {
        "source_example_id": 4421,
        "question_text": "如圖所示，在直角坐標平面上，醫院位置為點$A\\left( 1,0 \\right)$，學校的位置在$B(-3,4)$，小恩的家位於線段AB（$\\overline{AB}$）上，且已知小恩家到醫院的距離等於小恩家到學校距離的3倍，試求小恩家在坐標平面上的位置$P\\left( x,y \\right)$。",
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
        "variables": [
          "A",
          "B",
          "P",
          "x",
          "y"
        ],
        "givens": [
          "A",
          "B",
          "P",
          "x",
          "y"
        ],
        "target": "compute_distance_between_two_points"
      },
      {
        "source_example_id": 4423,
        "question_text": "已知$A\\left( -1,1 \\right)$、$B(-3,-3)$、$C\\left( 4,-4 \\right)$，試求△ABC的重心坐標。",
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
          "two_coordinate_points"
        ],
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "reasoning_type": [
          "numeric_computation"
        ],
        "required_derivation": true,
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
        "target": "compute_numeric"
      },
      {
        "source_example_id": 4427,
        "question_text": "坐標平面上兩點$A\\left( -2,6 \\right)$、$B\\left( 3,1 \\right)$，若點C在$\\overline{AB}$上，且$2\\overline{AC}=3\\overline{BC}$，\n試求C點坐標。",
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
        "variables": [
          "A",
          "B"
        ],
        "givens": [
          "A",
          "B"
        ],
        "target": "compute_distance_between_two_points"
      },
      {
        "source_example_id": 4438,
        "question_text": "坐標平面上兩點$A\\left( -3,0 \\right)$、$B(9,6)$，若點P在$\\overline{AB}$上，且$\\overline{AP}=2\\overline{PB}$，\n試求P點坐標。",
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
        "variables": [
          "A",
          "B"
        ],
        "givens": [
          "A",
          "B"
        ],
        "target": "compute_distance_between_two_points"
      },
      {
        "source_example_id": 4512,
        "question_text": "若$A\\left( 1,1 \\right)$、$B\\left( -5,4 \\right)$、$P\\left( x,y \\right)$三點共線，且P介於A、B之間，又$\\overline{AP}:\\overline{PB}=2:1$，則P點坐標為 (A)$\\left( 3,3 \\right)$ (B)$\\left( -3,3 \\right)$ (C)$\\left( 3,-3 \\right)$ (D)$\\left( -3,-3 \\right)$。",
        "answer": "",
        "choices": [
          "$\\left( 3,3 \\right)$",
          "$\\left( -3,3 \\right)$",
          "$\\left( 3,-3 \\right)$",
          "$\\left( -3,-3 \\right)$。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
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
        "variables": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "x",
          "y"
        ],
        "givens": [
          "A",
          "B",
          "C",
          "D",
          "P",
          "x",
          "y"
        ],
        "target": "compute_distance_between_two_points"
      },
      {
        "source_example_id": 4513,
        "question_text": "設P點介於$A\\left( 4,-2 \\right)$及$B\\left( -2,6 \\right)$兩點之間，且$3\\overline{PA}=2\\overline{PB}$，則P點與原點O的距離為何？ (A) 2 (B) 3 (C) 4 (D) 5。",
        "answer": "",
        "choices": [
          "2",
          "3",
          "4",
          "5。"
        ],
        "has_choices": true,
        "stem_embeds_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "checker": "choice_label_checker",
        "equivalence": "choice_label",
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
        "target": "compute_distance_between_two_points"
      }
    ],
    "semantic_alignment": {
      "skill_terms": [
        "1 坐標系與函數圖形",
        "2 平面坐標系與線型函數",
        "coordinates",
        "divi",
        "division",
        "divisionpointcoordinates",
        "ionpointcoordinate",
        "point",
        "solve_unknown_coordinate_from_two_point_distance",
        "vh",
        "vocational",
        "分點坐標",
        "坐標系與函數圖形",
        "平面坐標系與線型函數",
        "數學b",
        "數學b1"
      ],
      "source_terms": [
        "ab",
        "abc的重心坐標",
        "ac",
        "ap",
        "bc",
        "b之間",
        "cb",
        "compute_distance",
        "compute_distance_between_two_points",
        "compute_numeric",
        "coordinate_point",
        "distance_formula",
        "left",
        "overline",
        "pa",
        "pb",
        "right",
        "segment_length",
        "short_answer",
        "single_choice",
        "solve_unknown_coordinate_from_two_point_distance",
        "two_coordinate_points",
        "三點共線",
        "且p介於a",
        "且已知小恩家到醫院的距離等於小恩家到學校距離的3倍",
        "兩點之間",
        "則p點坐標為",
        "則p點與原點o的距離為何",
        "在直角坐標平面上",
        "坐標平面上三點",
        "坐標平面上兩點",
        "如圖所示",
        "學校的位置在",
        "小恩的家位於線段ab",
        "已知",
        "若點c在",
        "若點p在",
        "設p點介於",
        "試求",
        "試求c點坐標",
        "試求p點坐標",
        "試求小恩家在坐標平面上的位置",
        "醫院位置為點"
      ],
      "problem_type_terms": [
        "an",
        "answer",
        "between",
        "choice",
        "compute",
        "compute_distance_between_two_points",
        "compute_numeric",
        "coordinate",
        "di",
        "distance",
        "distance_formula_reasoning",
        "form",
        "formu",
        "hort",
        "ingle",
        "numeric_or_radical",
        "point",
        "point_quadrant",
        "point_quadrant_choice",
        "points",
        "short",
        "single",
        "single_choice",
        "single_choice / compute_distance_between_two_points",
        "solve_unknown_coordinate_from_two_point_distance",
        "tance",
        "two",
        "wer",
        "兩點距離計算"
      ],
      "expected_task_candidates": [
        "choose_possible_coordinate",
        "compare_distances_between_points",
        "compute_distance",
        "compute_distance_between_two_points",
        "compute_missing_coordinate_from_two_point_distance",
        "solve_parameter_from_distance_formula",
        "solve_unknown_coordinate_from_two_point_distance",
        "verify_distance_between_two_points"
      ],
      "expected_skill_families": [
        "distance_between_two_points_family"
      ],
      "source_family_distribution": {
        "distance_between_two_points_family": 6,
        "generic_numeric_family": 1
      },
      "candidate_problem_type_families": [
        "distance_between_two_points_family"
      ],
      "dominant_source_task": "compute_distance_between_two_points",
      "dominant_source_task_ratio": 0.8571,
      "dominant_source_family": [
        "distance_between_two_points_family"
      ],
      "dominant_source_family_ratio": 0.8571,
      "skill_source_score": 0.0172,
      "skill_problem_type_score": 0.0556,
      "source_problem_type_score": 0.0678,
      "per_problem_type_scores": [
        {
          "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
          "target_task": "compute_distance_between_two_points",
          "task_family": "distance_between_two_points_family",
          "inferred_tasks": [
            "compute_distance",
            "compute_distance_between_two_points"
          ],
          "skill_problem_type_score": 0.0556,
          "source_problem_type_score": 0.0484,
          "task_consistent_with_skill": true,
          "family_consistent_with_skill": true,
          "answer_contract_supported": true
        },
        {
          "problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
          "target_task": "compute_distance_between_two_points",
          "task_family": "distance_between_two_points_family",
          "inferred_tasks": [
            "compute_distance",
            "compute_distance_between_two_points"
          ],
          "skill_problem_type_score": 0.0588,
          "source_problem_type_score": 0.0678,
          "task_consistent_with_skill": true,
          "family_consistent_with_skill": true,
          "answer_contract_supported": true
        }
      ],
      "decision": "warn",
      "blockers": [],
      "warnings": [
        "alignment_score_below_recommended_threshold"
      ]
    },
    "source_alignment_status": "warn",
    "skill_problem_type_alignment_status": "warn",
    "alignment_score": 0.0172,
    "alignment_warnings": [
      "alignment_score_below_recommended_threshold"
    ],
    "alignment_blockers": [],
    "source_family_distribution": {
      "distance_between_two_points_family": 6,
      "generic_numeric_family": 1
    },
    "candidate_problem_type_families": [
      "distance_between_two_points_family"
    ],
    "expected_skill_families": [
      "distance_between_two_points_family"
    ],
    "excluded_source_examples": [
      {
        "example_id": 4423,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "alignment_score": 0.0,
        "aligned_with_skill": false,
        "included_in_phase1": false,
        "exclude_reason": "source_example_skill_mismatch",
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "title_stem_preview": "已知$A\\left( -1,1 \\right)$、$B(-3,-3)$、$C\\left( 4,-4 \\right)$，試求△ABC的重心坐標。"
      }
    ],
    "source_example_alignment": [
      {
        "example_id": 4420,
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "alignment_score": 0.0294,
        "aligned_with_skill": true,
        "included_in_phase1": true,
        "exclude_reason": "",
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "title_stem_preview": "(1) 坐標平面上三點$A(3,4)$、$B\\left( 6,-5 \\right)$、$C\\left( x,y \\right)$，若點C在$\\overline{"
      },
      {
        "example_id": 4421,
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "alignment_score": 0.0294,
        "aligned_with_skill": true,
        "included_in_phase1": true,
        "exclude_reason": "",
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "title_stem_preview": "如圖所示，在直角坐標平面上，醫院位置為點$A\\left( 1,0 \\right)$，學校的位置在$B(-3,4)$，小恩的家位於線段AB（$\\overline{"
      },
      {
        "example_id": 4423,
        "target_task": "compute_numeric",
        "task_family": "generic_numeric_family",
        "alignment_score": 0.0,
        "aligned_with_skill": false,
        "included_in_phase1": false,
        "exclude_reason": "source_example_skill_mismatch",
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "title_stem_preview": "已知$A\\left( -1,1 \\right)$、$B(-3,-3)$、$C\\left( 4,-4 \\right)$，試求△ABC的重心坐標。"
      },
      {
        "example_id": 4427,
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "alignment_score": 0.0312,
        "aligned_with_skill": true,
        "included_in_phase1": true,
        "exclude_reason": "",
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "title_stem_preview": "坐標平面上兩點$A\\left( -2,6 \\right)$、$B\\left( 3,1 \\right)$，若點C在$\\overline{AB}$上，且$2\\ove"
      },
      {
        "example_id": 4438,
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "alignment_score": 0.0312,
        "aligned_with_skill": true,
        "included_in_phase1": true,
        "exclude_reason": "",
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "title_stem_preview": "坐標平面上兩點$A\\left( -3,0 \\right)$、$B(9,6)$，若點P在$\\overline{AB}$上，且$\\overline{AP}=2\\ov"
      },
      {
        "example_id": 4512,
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "alignment_score": 0.0323,
        "aligned_with_skill": true,
        "included_in_phase1": true,
        "exclude_reason": "",
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "title_stem_preview": "若$A\\left( 1,1 \\right)$、$B\\left( -5,4 \\right)$、$P\\left( x,y \\right)$三點共線，且P介於A、B之"
      },
      {
        "example_id": 4513,
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "alignment_score": 0.0323,
        "aligned_with_skill": true,
        "included_in_phase1": true,
        "exclude_reason": "",
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "title_stem_preview": "設P點介於$A\\left( 4,-2 \\right)$及$B\\left( -2,6 \\right)$兩點之間，且$3\\overline{PA}=2\\overli"
      }
    ],
    "induction_clusters": [
      {
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "short_answer",
          "compute_distance_between_two_points",
          [
            "distance_formula_reasoning"
          ],
          [
            "coordinate_point",
            "distance_formula"
          ]
        ],
        "source_example_ids": [
          4420,
          4421,
          4427,
          4438
        ],
        "answer_type": "short_answer"
      },
      {
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "single_choice",
          "compute_distance_between_two_points",
          [
            "distance_formula_reasoning"
          ],
          [
            "coordinate_point",
            "distance_formula"
          ]
        ],
        "source_example_ids": [
          4512,
          4513
        ],
        "answer_type": "single_choice"
      }
    ],
    "induced_problem_type_specs": [
      {
        "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "display_name": "兩點距離計算",
        "source_example_ids": [
          4420,
          4421,
          4427,
          4438
        ],
        "answer_contract": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "numeric_or_radical",
          "answer_shape": "scalar",
          "answer_equivalence": "math_expression_equivalence",
          "checker": "expression_equivalence_checker",
          "accepted_formats": [
            "5",
            "5.0",
            "\\sqrt{13}",
            "sqrt(13)",
            "2\\sqrt{5}",
            "2√5"
          ]
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
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "short_answer",
          "compute_distance_between_two_points",
          [
            "distance_formula_reasoning"
          ],
          [
            "coordinate_point",
            "distance_formula"
          ]
        ]
      },
      {
        "problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
        "skill_id": "vh_數學B1_DivisionPointCoordinates",
        "target_task": "compute_distance_between_two_points",
        "task_family": "distance_between_two_points_family",
        "display_name": "single_choice / compute_distance_between_two_points",
        "source_example_ids": [
          4512,
          4513
        ],
        "answer_contract": {
          "choices_required": true,
          "choice_count": 4,
          "correct_choice_count": 1,
          "frontend_render_choices": true,
          "answer_type": "single_choice",
          "answer_shape": "choice_label",
          "answer_equivalence": "choice_label",
          "checker": "choice_label_checker",
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
          "template_families": [
            "compute_distance_between_two_points"
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
            "stem": "point_quadrant_choice"
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
          "single_choice",
          "compute_distance_between_two_points",
          [
            "distance_formula_reasoning"
          ],
          [
            "coordinate_point",
            "distance_formula"
          ]
        ]
      }
    ],
    "candidate_problem_types": [
      {
        "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
        "proposed_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
        "display_name": "兩點距離計算",
        "matched_example_ids": [
          4420,
          4421,
          4427,
          4438
        ],
        "matched_example_count": 4,
        "unmatched_example_ids": [],
        "representative_example_id": 4420,
        "structural_features": [
          "numeric"
        ],
        "answer_contract_proposal": {
          "choices_required": false,
          "choice_count": null,
          "correct_choice_count": null,
          "frontend_render_choices": false,
          "answer_type": "numeric_or_radical",
          "answer_shape": "scalar",
          "answer_equivalence": "math_expression_equivalence",
          "checker": "expression_equivalence_checker",
          "accepted_formats": [
            "5",
            "5.0",
            "\\sqrt{13}",
            "sqrt(13)",
            "2\\sqrt{5}",
            "2√5"
          ],
          "checker_key": "expression_equivalence_checker",
          "equivalence_type": "expression_equivalence",
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
          }
        },
        "checker_key_proposal": "expression_equivalence_checker",
        "equivalence_type_proposal": "expression_equivalence",
        "answer_shape": "numeric",
        "confidence": "high",
        "promote_recommendation": "recommend_promote_for_that_candidate",
        "promote_blockers": [],
        "risk_flags": [
          "alignment_score_below_recommended_threshold"
        ],
        "checker_contract_warnings": [],
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "short_answer",
          "compute_distance_between_two_points",
          [
            "distance_formula_reasoning"
          ],
          [
            "coordinate_point",
            "distance_formula"
          ]
        ],
        "problem_type_spec_draft": {
          "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
          "skill_id": "vh_數學B1_DivisionPointCoordinates",
          "target_task": "compute_distance_between_two_points",
          "task_family": "distance_between_two_points_family",
          "display_name": "兩點距離計算",
          "source_example_ids": [
            4420,
            4421,
            4427,
            4438
          ],
          "answer_contract": {
            "choices_required": false,
            "choice_count": null,
            "correct_choice_count": null,
            "frontend_render_choices": false,
            "answer_type": "numeric_or_radical",
            "answer_shape": "scalar",
            "answer_equivalence": "math_expression_equivalence",
            "checker": "expression_equivalence_checker",
            "accepted_formats": [
              "5",
              "5.0",
              "\\sqrt{13}",
              "sqrt(13)",
              "2\\sqrt{5}",
              "2√5"
            ]
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
          "grouping_reason": "single_signature_group",
          "feature_signature": [
            "short_answer",
            "compute_distance_between_two_points",
            [
              "distance_formula_reasoning"
            ],
            [
              "coordinate_point",
              "distance_formula"
            ]
          ]
        },
        "generator_readiness": "runtime_ready",
        "template_slot": "point_quadrant",
        "semantic_alignment": {
          "skill_problem_type_score": 0.0556,
          "source_problem_type_score": 0.0484,
          "task_consistent_with_skill": true
        }
      },
      {
        "problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
        "proposed_problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
        "display_name": "single_choice / compute_distance_between_two_points",
        "matched_example_ids": [
          4512,
          4513
        ],
        "matched_example_count": 2,
        "unmatched_example_ids": [],
        "representative_example_id": 4512,
        "structural_features": [
          "choice_label"
        ],
        "answer_contract_proposal": {
          "choices_required": true,
          "choice_count": 4,
          "correct_choice_count": 1,
          "frontend_render_choices": true,
          "answer_type": "single_choice",
          "answer_shape": "choice_label",
          "answer_equivalence": "choice_label",
          "checker": "choice_label_checker",
          "accepted_formats": [
            "A",
            "B",
            "C",
            "D"
          ],
          "checker_key": "choice_label_checker",
          "equivalence_type": "choice_label",
          "selected_checker": "choice_label_checker",
          "checker_capability_status": "ok",
          "checker_contract_blockers": [],
          "checker_contract_warnings": [],
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
            "template_families": [
              "compute_distance_between_two_points"
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
              "stem": "point_quadrant_choice"
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
        "risk_flags": [
          "alignment_score_below_recommended_threshold"
        ],
        "checker_contract_warnings": [],
        "spec_source": "phase1_induced_draft",
        "grouping_reason": "single_signature_group",
        "feature_signature": [
          "single_choice",
          "compute_distance_between_two_points",
          [
            "distance_formula_reasoning"
          ],
          [
            "coordinate_point",
            "distance_formula"
          ]
        ],
        "problem_type_spec_draft": {
          "problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
          "skill_id": "vh_數學B1_DivisionPointCoordinates",
          "target_task": "compute_distance_between_two_points",
          "task_family": "distance_between_two_points_family",
          "display_name": "single_choice / compute_distance_between_two_points",
          "source_example_ids": [
            4512,
            4513
          ],
          "answer_contract": {
            "choices_required": true,
            "choice_count": 4,
            "correct_choice_count": 1,
            "frontend_render_choices": true,
            "answer_type": "single_choice",
            "answer_shape": "choice_label",
            "answer_equivalence": "choice_label",
            "checker": "choice_label_checker",
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
            "template_families": [
              "compute_distance_between_two_points"
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
              "stem": "point_quadrant_choice"
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
            "single_choice",
            "compute_distance_between_two_points",
            [
              "distance_formula_reasoning"
            ],
            [
              "coordinate_point",
              "distance_formula"
            ]
          ]
        },
        "generator_readiness": "runtime_ready",
        "template_slot": "point_quadrant_choice",
        "semantic_alignment": {
          "skill_problem_type_score": 0.0588,
          "source_problem_type_score": 0.0678,
          "task_consistent_with_skill": true
        }
      }
    ],
    "per_example_classification": [
      {
        "example_id": 4420,
        "detected_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
        "example_feature": {
          "source_example_id": 4420,
          "question_text": "(1) 坐標平面上三點$A(3,4)$、$B\\left( 6,-5 \\right)$、$C\\left( x,y \\right)$，若點C在$\\overline{AB}$上，且\n $\\overline{AC}:\\overline{CB}=2:1$，試求C點坐標。\n(2) 坐標平面上兩點$A(-2,-2)$、$B(5,5)$，若點C在$\\overline{AB}$上，且$4\\overline{AC}=3\\overline{BC}$，\n試求C點坐標。",
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
          "variables": [
            "A",
            "B",
            "C",
            "x",
            "y"
          ],
          "givens": [
            "A",
            "B",
            "C",
            "x",
            "y"
          ],
          "target": "compute_distance_between_two_points"
        },
        "answer_shape": "text_short",
        "classification_confidence": "high",
        "classification_reason": "feature_signature_induction",
        "risk_flags": []
      },
      {
        "example_id": 4421,
        "detected_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
        "example_feature": {
          "source_example_id": 4421,
          "question_text": "如圖所示，在直角坐標平面上，醫院位置為點$A\\left( 1,0 \\right)$，學校的位置在$B(-3,4)$，小恩的家位於線段AB（$\\overline{AB}$）上，且已知小恩家到醫院的距離等於小恩家到學校距離的3倍，試求小恩家在坐標平面上的位置$P\\left( x,y \\right)$。",
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
          "variables": [
            "A",
            "B",
            "P",
            "x",
            "y"
          ],
          "givens": [
            "A",
            "B",
            "P",
            "x",
            "y"
          ],
          "target": "compute_distance_between_two_points"
        },
        "answer_shape": "text_short",
        "classification_confidence": "high",
        "classification_reason": "feature_signature_induction",
        "risk_flags": []
      },
      {
        "example_id": 4423,
        "detected_problem_type_id": "unknown",
        "example_feature": {
          "source_example_id": 4423,
          "question_text": "已知$A\\left( -1,1 \\right)$、$B(-3,-3)$、$C\\left( 4,-4 \\right)$，試求△ABC的重心坐標。",
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
            "two_coordinate_points"
          ],
          "target_task": "compute_numeric",
          "task_family": "generic_numeric_family",
          "reasoning_type": [
            "numeric_computation"
          ],
          "required_derivation": true,
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
          "target": "compute_numeric"
        },
        "answer_shape": "text_short",
        "classification_confidence": "low",
        "classification_reason": "feature_signature_induction",
        "risk_flags": []
      },
      {
        "example_id": 4427,
        "detected_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
        "example_feature": {
          "source_example_id": 4427,
          "question_text": "坐標平面上兩點$A\\left( -2,6 \\right)$、$B\\left( 3,1 \\right)$，若點C在$\\overline{AB}$上，且$2\\overline{AC}=3\\overline{BC}$，\n試求C點坐標。",
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
          "variables": [
            "A",
            "B"
          ],
          "givens": [
            "A",
            "B"
          ],
          "target": "compute_distance_between_two_points"
        },
        "answer_shape": "text_short",
        "classification_confidence": "high",
        "classification_reason": "feature_signature_induction",
        "risk_flags": []
      },
      {
        "example_id": 4438,
        "detected_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
        "example_feature": {
          "source_example_id": 4438,
          "question_text": "坐標平面上兩點$A\\left( -3,0 \\right)$、$B(9,6)$，若點P在$\\overline{AB}$上，且$\\overline{AP}=2\\overline{PB}$，\n試求P點坐標。",
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
          "variables": [
            "A",
            "B"
          ],
          "givens": [
            "A",
            "B"
          ],
          "target": "compute_distance_between_two_points"
        },
        "answer_shape": "text_short",
        "classification_confidence": "high",
        "classification_reason": "feature_signature_induction",
        "risk_flags": []
      },
      {
        "example_id": 4512,
        "detected_problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
        "example_feature": {
          "source_example_id": 4512,
          "question_text": "若$A\\left( 1,1 \\right)$、$B\\left( -5,4 \\right)$、$P\\left( x,y \\right)$三點共線，且P介於A、B之間，又$\\overline{AP}:\\overline{PB}=2:1$，則P點坐標為 (A)$\\left( 3,3 \\right)$ (B)$\\left( -3,3 \\right)$ (C)$\\left( 3,-3 \\right)$ (D)$\\left( -3,-3 \\right)$。",
          "answer": "",
          "choices": [
            "$\\left( 3,3 \\right)$",
            "$\\left( -3,3 \\right)$",
            "$\\left( 3,-3 \\right)$",
            "$\\left( -3,-3 \\right)$。"
          ],
          "has_choices": true,
          "stem_embeds_choices": true,
          "answer_type": "single_choice",
          "answer_shape": "choice_label",
          "checker": "choice_label_checker",
          "equivalence": "choice_label",
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
          "variables": [
            "A",
            "B",
            "C",
            "D",
            "P",
            "x",
            "y"
          ],
          "givens": [
            "A",
            "B",
            "C",
            "D",
            "P",
            "x",
            "y"
          ],
          "target": "compute_distance_between_two_points"
        },
        "answer_shape": "choice_label",
        "classification_confidence": "high",
        "classification_reason": "feature_signature_induction",
        "risk_flags": [
          "stem_embeds_choices"
        ]
      },
      {
        "example_id": 4513,
        "detected_problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
        "example_feature": {
          "source_example_id": 4513,
          "question_text": "設P點介於$A\\left( 4,-2 \\right)$及$B\\left( -2,6 \\right)$兩點之間，且$3\\overline{PA}=2\\overline{PB}$，則P點與原點O的距離為何？ (A) 2 (B) 3 (C) 4 (D) 5。",
          "answer": "",
          "choices": [
            "2",
            "3",
            "4",
            "5。"
          ],
          "has_choices": true,
          "stem_embeds_choices": true,
          "answer_type": "single_choice",
          "answer_shape": "choice_label",
          "checker": "choice_label_checker",
          "equivalence": "choice_label",
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
          "target": "compute_distance_between_two_points"
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
      "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
      "single_choice_compute_distance_between_two_points_coordinate_point_distance_form"
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
    "curated_specs_available": false
  },
  "classifier_source": "ai_bootstrap_with_default_fallback+phase1_induction",
  "ai_bootstrap_used": true,
  "ai_bootstrap_status": "success",
  "ai_bootstrap_confidence_summary": {
    "count": 7,
    "avg": 1.0,
    "low_confidence_count": 0
  },
  "inspect_report_note": "Missing classifier/rule pack, AI bootstrap attempted.",
  "ai_bootstrap_error": "",
  "ai_bootstrap_raw_response_preview": "```json\n{\n  \"skill_id\": \"vh_數學B1_DivisionPointCoordinates\",\n  \"skill_ch_name\": \"vh_數學B1_DivisionPointCoordinates\",\n  \"classifier_source\": \"The problems are classified based on the required answer format and the mathematical task: direct calculation of coordinates (ordered pairs) versus selecting a property or coordinate from multiple choices.\",\n  \"problem_types\": [\n    {\n      \"problem_type_id\": \"division_point_coordinates_calculation\",\n      \"description\": \"Calculate the coordinates of an internal division point on a line segment or the centroid of a triangle given the vertices and ratio.\",\n      \"answer_contract\": {\n        \"type\": \"ordered_pair\"\n      },\n      \"semantic_contract\": {\n        \"x\": \"number\",\n        \"y\": \"number\"\n      },\n      \"checker\": \"ordered_pair_checker\",\n      \"equivalence\": \"ordered_pair\",\n      \"requires_human_action\": false,\n      \"generator_code_preview\": \"async (givens) => {\\n  // For internal division: metadata: { givens: {A: [x1, y1], B: [x2, y2], ratio:",
  "ai_bootstrap_validation_errors": [
    "source_index=1: invalid_problem_type_id=",
    "source_index=1: invalid_checker=",
    "source_index=1: invalid_equivalence=",
    "source_index=1: unrelated_problem_type=",
    "source_index=1: invalid_problem_type_id_style=",
    "source_index=2: invalid_problem_type_id=",
    "source_index=2: invalid_checker=",
    "source_index=2: invalid_equivalence=",
    "source_index=2: unrelated_problem_type=",
    "source_index=2: invalid_problem_type_id_style=",
    "source_index=3: invalid_problem_type_id=",
    "source_index=3: invalid_checker=",
    "source_index=3: invalid_equivalence=",
    "source_index=3: unrelated_problem_type=",
    "source_index=3: invalid_problem_type_id_style=",
    "source_index=4: invalid_problem_type_id=",
    "source_index=4: invalid_checker=",
    "source_index=4: invalid_equivalence=",
    "source_index=4: unrelated_problem_type=",
    "source_index=4: invalid_problem_type_id_style=",
    "source_index=5: invalid_problem_type_id=",
    "source_index=5: invalid_checker=",
    "source_index=5: invalid_equivalence=",
    "source_index=5: unrelated_problem_type=",
    "source_index=5: invalid_problem_type_id_style=",
    "source_index=6: invalid_problem_type_id=",
    "source_index=6: invalid_checker=",
    "source_index=6: invalid_equivalence=",
    "source_index=6: unrelated_problem_type=",
    "source_index=6: invalid_problem_type_id_style=",
    "source_index=7: invalid_problem_type_id=",
    "source_index=7: invalid_checker=",
    "source_index=7: invalid_equivalence=",
    "source_index=7: unrelated_problem_type=",
    "source_index=7: invalid_problem_type_id_style=",
    "ai_bootstrap_all_unclassified_promoted_to_default_problem_type"
  ],
  "ai_bootstrap_prompt_version": "gencode_phase1_ai_bootstrap_v2",
  "ai_bootstrap_model": "gemini-3-flash-preview",
  "ai_bootstrap_provider": "google",
  "ai_bootstrap_config_source": "db_global_selected_model",
  "default_problem_type_used": true,
  "problem_type_spec_first": true,
  "spec_defined_problem_type_ids": [
    "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
    "single_choice_compute_distance_between_two_points_coordinate_point_distance_form"
  ],
  "spec_mode": "induce_from_sources",
  "induced_problem_type_specs": [
    {
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu",
      "skill_id": "vh_數學B1_DivisionPointCoordinates",
      "target_task": "compute_distance_between_two_points",
      "task_family": "distance_between_two_points_family",
      "display_name": "兩點距離計算",
      "source_example_ids": [
        4420,
        4421,
        4427,
        4438
      ],
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "numeric_or_radical",
        "answer_shape": "scalar",
        "answer_equivalence": "math_expression_equivalence",
        "checker": "expression_equivalence_checker",
        "accepted_formats": [
          "5",
          "5.0",
          "\\sqrt{13}",
          "sqrt(13)",
          "2\\sqrt{5}",
          "2√5"
        ]
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
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "short_answer",
        "compute_distance_between_two_points",
        [
          "distance_formula_reasoning"
        ],
        [
          "coordinate_point",
          "distance_formula"
        ]
      ]
    },
    {
      "problem_type_id": "single_choice_compute_distance_between_two_points_coordinate_point_distance_form",
      "skill_id": "vh_數學B1_DivisionPointCoordinates",
      "target_task": "compute_distance_between_two_points",
      "task_family": "distance_between_two_points_family",
      "display_name": "single_choice / compute_distance_between_two_points",
      "source_example_ids": [
        4512,
        4513
      ],
      "answer_contract": {
        "choices_required": true,
        "choice_count": 4,
        "correct_choice_count": 1,
        "frontend_render_choices": true,
        "answer_type": "single_choice",
        "answer_shape": "choice_label",
        "answer_equivalence": "choice_label",
        "checker": "choice_label_checker",
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
        "template_families": [
          "compute_distance_between_two_points"
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
          "stem": "point_quadrant_choice"
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
        "single_choice",
        "compute_distance_between_two_points",
        [
          "distance_formula_reasoning"
        ],
        [
          "coordinate_point",
          "distance_formula"
        ]
      ]
    }
  ],
  "induction_clusters": [
    {
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "short_answer",
        "compute_distance_between_two_points",
        [
          "distance_formula_reasoning"
        ],
        [
          "coordinate_point",
          "distance_formula"
        ]
      ],
      "source_example_ids": [
        4420,
        4421,
        4427,
        4438
      ],
      "answer_type": "short_answer"
    },
    {
      "grouping_reason": "single_signature_group",
      "feature_signature": [
        "single_choice",
        "compute_distance_between_two_points",
        [
          "distance_formula_reasoning"
        ],
        [
          "coordinate_point",
          "distance_formula"
        ]
      ],
      "source_example_ids": [
        4512,
        4513
      ],
      "answer_type": "single_choice"
    }
  ],
  "human_review_items": []
}
```
