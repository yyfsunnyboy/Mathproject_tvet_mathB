# Gencode Phase2 Generator Summary: vh_數學B1_QuadraticInequalitySolution

## phase2
```json
{
  "ok": true,
  "phase": "phase2",
  "skill_id": "vh_數學B1_QuadraticInequalitySolution",
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
      "problem_type_id": "integer_reverse_quadratic_inequality_coefficients",
      "source_example_count": 3,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "source_has_choices": false,
        "answer_type": "integer",
        "answer_shape": "scalar",
        "answer_semantics": "numeric_exact",
        "answer_equivalence": "numeric_exact",
        "equivalence_type": "numeric_exact",
        "checker": "integer_checker",
        "checker_key": "integer_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "integer_checker",
        "checker_selection_reason": "quadratic_inequality_reverse_coefficient",
        "accepted_formats": [
          "2",
          "-3",
          "5"
        ]
      },
      "answer_type": "integer",
      "answer_shape": "scalar",
      "equivalence_type": "numeric_exact",
      "selected_checker": "integer_checker",
      "checker_key": "integer_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_QuadraticInequalitySolution:integer_reverse_quadratic_inequality_coefficients:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "runtime_ready_with_diversity_warning",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 17,
        "unique_question_text_count": 29,
        "template_variant_distribution": {
          "ask_a": 11,
          "ask_a_plus_b": 13,
          "ask_b": 6
        },
        "answer_shape_distribution": {
          "1": 6,
          "3": 4,
          "-2": 2,
          "-1": 2,
          "-4": 2,
          "4": 1,
          "-6": 3,
          "2": 4,
          "6": 1,
          "-3": 4,
          "12": 1
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
        "max_consecutive_same_template": 5,
        "generation_errors": [],
        "sampling_mode": "live"
      },
      "unique_signature_count": 17,
      "template_variant_distribution": {
        "ask_a": 11,
        "ask_a_plus_b": 13,
        "ask_b": 6
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
      "usable_for_phase3": true,
      "target_task": "reverse_quadratic_inequality_coefficients",
      "base_problem_type_id": "reverse_quadratic_inequality_coefficients",
      "value_type_prefix": "integer",
      "template_slot": "reverse_quadratic_inequality_coefficients",
      "_resolved_template_slot": "reverse_quadratic_inequality_coefficients"
    },
    {
      "problem_type_id": "integer_solve_quadratic_inequality",
      "source_example_count": 8,
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
      "generator_key": "vh_數學B1_QuadraticInequalitySolution:integer_solve_quadratic_inequality:draft_v1",
      "generator_status": "runtime_ready",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "passed",
      "diversity_sampling": {
        "diversity_sampling_status": "passed",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 30,
        "unique_question_text_count": 30,
        "template_variant_distribution": {
          "factored_leading_negative": 10,
          "factored_strict": 9,
          "expanded_strict": 11
        },
        "answer_shape_distribution": {
          "x<=-1 or x>=5": 2,
          "-8<x<7": 1,
          "-3<=x<=1": 1,
          "-1<x<9": 1,
          "x<-6 or x>3": 1,
          "x<0 or x>4": 1,
          "x<=-7 or x>=9": 1,
          "x<-5 or x>5": 1,
          "-6<=x<=-2": 1,
          "x<-5 or x>-2": 1,
          "x<-7 or x>6": 1,
          "x<-2 or x>0": 1,
          "1<x<5": 1,
          "-3<x<9": 1,
          "x<-8 or x>5": 1,
          "x<=-2 or x>=0": 1,
          "-2<x<8": 1,
          "x<2 or x>7": 1,
          "x<-7 or x>5": 1,
          "-3<x<6": 1,
          "-1<=x<=6": 1,
          "1<=x<=9": 1,
          "-8<=x<=2": 1,
          "-7<x<-1": 1,
          "x<=-6 or x>=-2": 1,
          "x<1 or x>6": 1,
          "x<2 or x>4": 1,
          "-4<x<1": 1,
          "-8<x<4": 1
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
        "repetition_warnings": [],
        "diversity_blockers": [],
        "max_consecutive_same_template": 4,
        "generation_errors": [],
        "sampling_mode": "live"
      },
      "unique_signature_count": 30,
      "template_variant_distribution": {
        "factored_leading_negative": 10,
        "factored_strict": 9,
        "expanded_strict": 11
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
      "repetition_warnings": [],
      "requires_human_action": false,
      "blockers": [],
      "warnings": [],
      "usable_for_phase3": true,
      "target_task": "solve_quadratic_inequality",
      "base_problem_type_id": "solve_quadratic_inequality",
      "value_type_prefix": "integer",
      "template_slot": "solve_quadratic_inequality",
      "_resolved_template_slot": "solve_quadratic_inequality"
    },
    {
      "problem_type_id": "rational_solve_quadratic_inequality",
      "source_example_count": 4,
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
      "generator_key": "vh_數學B1_QuadraticInequalitySolution:rational_solve_quadratic_inequality:draft_v1",
      "generator_status": "runtime_ready",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "passed",
      "diversity_sampling": {
        "diversity_sampling_status": "passed",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 30,
        "unique_question_text_count": 30,
        "template_variant_distribution": {
          "factored_leading_negative": 10,
          "factored_strict": 9,
          "expanded_strict": 11
        },
        "answer_shape_distribution": {
          "x<=-1 or x>=5": 2,
          "-8<x<7": 1,
          "-3<=x<=1": 1,
          "-1<x<9": 1,
          "x<-6 or x>3": 1,
          "x<0 or x>4": 1,
          "x<=-7 or x>=9": 1,
          "x<-5 or x>5": 1,
          "-6<=x<=-2": 1,
          "x<-5 or x>-2": 1,
          "x<-7 or x>6": 1,
          "x<-2 or x>0": 1,
          "1<x<5": 1,
          "-3<x<9": 1,
          "x<-8 or x>5": 1,
          "x<=-2 or x>=0": 1,
          "-2<x<8": 1,
          "x<2 or x>7": 1,
          "x<-7 or x>5": 1,
          "-3<x<6": 1,
          "-1<=x<=6": 1,
          "1<=x<=9": 1,
          "-8<=x<=2": 1,
          "-7<x<-1": 1,
          "x<=-6 or x>=-2": 1,
          "x<1 or x>6": 1,
          "x<2 or x>4": 1,
          "-4<x<1": 1,
          "-8<x<4": 1
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
        "repetition_warnings": [],
        "diversity_blockers": [],
        "max_consecutive_same_template": 4,
        "generation_errors": [],
        "sampling_mode": "live"
      },
      "unique_signature_count": 30,
      "template_variant_distribution": {
        "factored_leading_negative": 10,
        "factored_strict": 9,
        "expanded_strict": 11
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
      "repetition_warnings": [],
      "requires_human_action": false,
      "blockers": [],
      "warnings": [],
      "usable_for_phase3": true,
      "target_task": "solve_quadratic_inequality",
      "base_problem_type_id": "solve_quadratic_inequality",
      "value_type_prefix": "rational",
      "template_slot": "solve_quadratic_inequality",
      "_resolved_template_slot": "solve_quadratic_inequality"
    },
    {
      "problem_type_id": "integer_applied_quadratic_inequality_problem",
      "source_example_count": 3,
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
      "generator_key": "vh_數學B1_QuadraticInequalitySolution:integer_applied_quadratic_inequality_problem:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "runtime_ready_with_diversity_warning",
        "diversity_healthy": false,
        "sample_count": 30,
        "unique_signature_count": 14,
        "unique_question_text_count": 14,
        "template_variant_distribution": {
          "triangle_side": 16,
          "coffee_profit": 14
        },
        "answer_shape_distribution": {
          "x<4 or x>8": 5,
          "1<x<7": 3,
          "1<x<4": 1,
          "2<x<5": 1,
          "x<4 or x>7": 3,
          "x<3 or x>6": 5,
          "3<x<10": 1,
          "1<x<6": 3,
          "3<x<11": 1,
          "1<x<9": 1,
          "2<x<10": 1,
          "3<x<9": 1,
          "x<3 or x>5": 3,
          "2<x<9": 1
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
        "diversity_blockers": [],
        "max_consecutive_same_template": 5,
        "generation_errors": [],
        "sampling_mode": "live"
      },
      "unique_signature_count": 14,
      "template_variant_distribution": {
        "triangle_side": 16,
        "coffee_profit": 14
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
      "usable_for_phase3": true,
      "target_task": "applied_quadratic_inequality_problem",
      "base_problem_type_id": "applied_quadratic_inequality_problem",
      "value_type_prefix": "integer",
      "template_slot": "applied_quadratic_inequality_problem",
      "_resolved_template_slot": "applied_quadratic_inequality_problem"
    },
    {
      "problem_type_id": "integer_solve_quadratic_inequality_parameter_range",
      "source_example_count": 3,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "source_has_choices": false,
        "answer_type": "interval",
        "answer_shape": "parameter_interval",
        "answer_semantics": "parameter_range",
        "answer_equivalence": "interval_equivalence",
        "equivalence_type": "interval_equivalence",
        "checker": "interval_checker",
        "checker_key": "interval_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "interval_checker",
        "checker_selection_reason": "quadratic_inequality_parameter_range",
        "accepted_formats": [
          "m>1",
          "k<-2",
          "m>=1",
          "k<=-2",
          "a>3/2"
        ],
        "answer_format_example": "m>1"
      },
      "answer_type": "interval",
      "answer_shape": "parameter_interval",
      "equivalence_type": "interval_equivalence",
      "selected_checker": "interval_checker",
      "checker_key": "interval_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_QuadraticInequalitySolution:integer_solve_quadratic_inequality_parameter_range:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "generator_diversity_blocked",
        "diversity_healthy": false,
        "sample_count": 30,
        "unique_signature_count": 4,
        "unique_question_text_count": 6,
        "template_variant_distribution": {
          "always_negative_k": 20,
          "always_positive_m": 10
        },
        "answer_shape_distribution": {
          "k<=-2": 10,
          "m>1": 5,
          "m>=1": 5,
          "k<-2": 10
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
          "generator_diversity_blocked"
        ],
        "max_consecutive_same_template": 9,
        "generation_errors": [],
        "sampling_mode": "live"
      },
      "unique_signature_count": 4,
      "template_variant_distribution": {
        "always_negative_k": 20,
        "always_positive_m": 10
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
      "usable_for_phase3": true,
      "target_task": "solve_quadratic_inequality_parameter_range",
      "base_problem_type_id": "solve_quadratic_inequality_parameter_range",
      "value_type_prefix": "integer",
      "template_slot": "solve_quadratic_inequality_parameter_range",
      "_resolved_template_slot": "solve_quadratic_inequality_parameter_range"
    },
    {
      "problem_type_id": "rational_solve_quadratic_inequality_special_cases",
      "source_example_count": 1,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "source_has_choices": false,
        "answer_type": "text_short",
        "answer_shape": "text_short",
        "answer_semantics": "special_case_solution_label",
        "answer_equivalence": "exact_string",
        "equivalence_type": "exact_string",
        "checker": "text_short_checker",
        "checker_key": "text_short_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "text_short_checker",
        "checker_selection_reason": "quadratic_inequality_special_case",
        "accepted_formats": [
          "無解",
          "任意實數"
        ],
        "answer_format_example": "任意實數"
      },
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "equivalence_type": "exact_string",
      "selected_checker": "text_short_checker",
      "checker_key": "text_short_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_QuadraticInequalitySolution:rational_solve_quadratic_inequality_special_cases:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "generator_diversity_blocked",
        "diversity_healthy": false,
        "sample_count": 30,
        "unique_signature_count": 2,
        "unique_question_text_count": 30,
        "template_variant_distribution": {
          "discriminant_negative": 30
        },
        "answer_shape_distribution": {
          "任意實數": 21,
          "無解": 9
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
      "unique_signature_count": 2,
      "template_variant_distribution": {
        "discriminant_negative": 30
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
      "usable_for_phase3": true,
      "target_task": "solve_quadratic_inequality_special_cases",
      "base_problem_type_id": "solve_quadratic_inequality_special_cases",
      "value_type_prefix": "rational",
      "template_slot": "solve_quadratic_inequality_special_cases",
      "_resolved_template_slot": "solve_quadratic_inequality_special_cases"
    },
    {
      "problem_type_id": "text_short_factor_quadratic_by_cross_multiplication",
      "source_example_count": 1,
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
        "source_has_choices": false,
        "answer_semantics": "algebraic_expression"
      },
      "answer_type": "expression",
      "answer_shape": "factored_expression",
      "equivalence_type": "algebraic_equivalent",
      "selected_checker": "expression_checker",
      "checker_key": "expression_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_QuadraticInequalitySolution:text_short_factor_quadratic_by_cross_multiplication:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "passed",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 30,
        "unique_question_text_count": 30,
        "template_variant_distribution": {
          "leading_negative": 11,
          "monic": 10,
          "general": 9
        },
        "answer_shape_distribution": {
          "(-2x+7)(2x-2)": 1,
          "(x+5)(x-8)": 1,
          "(3x+4)(x+3)": 1,
          "(2x+2)(2x+1)": 1,
          "(4x-6)(3x-3)": 1,
          "(-2x-2)(3x-1)": 1,
          "(-2x+3)(3x-4)": 1,
          "(x+3)(x+7)": 1,
          "(-2x-5)(3x+3)": 1,
          "(4x+4)(3x+6)": 1,
          "(x-1)(x+1)": 1,
          "(4x-4)(2x+2)": 1,
          "(-x+1)(3x-7)": 1,
          "(2x-5)(x+2)": 1,
          "(2x-5)(3x-5)": 1,
          "(x-1)(x-9)": 1,
          "(-3x-5)(2x+7)": 1,
          "(-2x-6)(x+4)": 1,
          "(x-7)(x+2)": 1,
          "(x+3)(x-4)": 1,
          "(x-1)(x-3)": 1,
          "(3x+4)(x+4)": 1,
          "(x-5)(x+8)": 1,
          "(-3x+6)(3x-4)": 1,
          "(-3x+2)(x-4)": 1,
          "(2x-7)(3x+1)": 1,
          "(x+4)(x-8)": 1,
          "(x-5)(x-2)": 1,
          "(-x+4)(2x+1)": 1,
          "(-3x+1)(2x-4)": 1
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
        "repetition_warnings": [],
        "diversity_blockers": [],
        "max_consecutive_same_template": 3,
        "generation_errors": [],
        "sampling_mode": "live"
      },
      "unique_signature_count": 30,
      "template_variant_distribution": {
        "leading_negative": 11,
        "monic": 10,
        "general": 9
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
      "target_task": "factor_quadratic_by_cross_multiplication",
      "base_problem_type_id": "factor_quadratic_by_cross_multiplication",
      "value_type_prefix": "text_short",
      "template_slot": "factor_quadratic_by_cross_multiplication",
      "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
    }
  ],
  "failed_generators": [],
  "accepted_generators": [
    "vh_數學B1_QuadraticInequalitySolution:integer_applied_quadratic_inequality_problem:draft_v1",
    "vh_數學B1_QuadraticInequalitySolution:integer_reverse_quadratic_inequality_coefficients:draft_v1",
    "vh_數學B1_QuadraticInequalitySolution:integer_solve_quadratic_inequality:draft_v1",
    "vh_數學B1_QuadraticInequalitySolution:integer_solve_quadratic_inequality_parameter_range:draft_v1",
    "vh_數學B1_QuadraticInequalitySolution:rational_solve_quadratic_inequality:draft_v1",
    "vh_數學B1_QuadraticInequalitySolution:rational_solve_quadratic_inequality_special_cases:draft_v1",
    "vh_數學B1_QuadraticInequalitySolution:text_short_factor_quadratic_by_cross_multiplication:draft_v1"
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
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticInequalitySolution_phase2_generator_summary.json",
    "phase2_generator_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticInequalitySolution_phase2_generator_summary.md",
    "phase2_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticInequalitySolution_phase2_generator_summary.json",
    "phase2_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_QuadraticInequalitySolution_phase2_generator_summary.md",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_QuadraticInequalitySolution_generator_draft_spec.json"
  },
  "next_action": "phase3_package_draft",
  "timestamp": "2026-06-14T05:19:53.351042+00:00",
  "dry_run": true
}
```
