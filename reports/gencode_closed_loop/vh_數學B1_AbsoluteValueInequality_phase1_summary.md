# Gencode Phase1 Summary: vh_數學B1_AbsoluteValueInequality

## phase1
```json
{
  "ok": true,
  "phase": "phase1",
  "skill_id": "vh_數學B1_AbsoluteValueInequality",
  "source_example_count": 10,
  "candidate_problem_types": [
    {
      "problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "proposed_problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "matched_example_ids": [
        4404,
        4405,
        4406,
        4407
      ],
      "matched_example_count": 4,
      "unmatched_example_ids": [
        4400,
        4402,
        4403,
        4409,
        4413,
        4499
      ],
      "representative_example_id": 4404,
      "structural_features": [
        "expression"
      ],
      "answer_contract_proposal": {
        "answer_type": "expression",
        "equivalence_type": "exact_string",
        "checker_key": "exact_string_checker"
      },
      "checker_key_proposal": "exact_string_checker",
      "equivalence_type_proposal": "exact_string",
      "answer_shape": "expression",
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": []
    },
    {
      "problem_type_id": "absolute_value_inequality_shifted_basic",
      "proposed_problem_type_id": "absolute_value_inequality_shifted_basic",
      "matched_example_ids": [
        4402,
        4403
      ],
      "matched_example_count": 2,
      "unmatched_example_ids": [
        4400,
        4404,
        4405,
        4406,
        4407,
        4409,
        4413,
        4499
      ],
      "representative_example_id": 4402,
      "structural_features": [
        "expression"
      ],
      "answer_contract_proposal": {
        "answer_type": "expression",
        "equivalence_type": "exact_string",
        "checker_key": "exact_string_checker"
      },
      "checker_key_proposal": "exact_string_checker",
      "equivalence_type_proposal": "exact_string",
      "answer_shape": "expression",
      "confidence": "medium",
      "promote_recommendation": "conservative_hold_for_that_candidate",
      "promote_blockers": [
        "insufficient_examples_for_safe_promote"
      ],
      "risk_flags": []
    },
    {
      "problem_type_id": "absolute_value_inequality_zero_center_basic",
      "proposed_problem_type_id": "absolute_value_inequality_zero_center_basic",
      "matched_example_ids": [
        4400,
        4413
      ],
      "matched_example_count": 2,
      "unmatched_example_ids": [
        4402,
        4403,
        4404,
        4405,
        4406,
        4407,
        4409,
        4499
      ],
      "representative_example_id": 4400,
      "structural_features": [
        "expression"
      ],
      "answer_contract_proposal": {
        "answer_type": "expression",
        "equivalence_type": "exact_string",
        "checker_key": "exact_string_checker"
      },
      "checker_key_proposal": "exact_string_checker",
      "equivalence_type_proposal": "exact_string",
      "answer_shape": "expression",
      "confidence": "medium",
      "promote_recommendation": "conservative_hold_for_that_candidate",
      "promote_blockers": [
        "insufficient_examples_for_safe_promote"
      ],
      "risk_flags": []
    },
    {
      "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
      "proposed_problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
      "matched_example_ids": [
        4499
      ],
      "matched_example_count": 1,
      "unmatched_example_ids": [
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
      "representative_example_id": 4499,
      "structural_features": [
        "choice_label"
      ],
      "answer_contract_proposal": {
        "answer_type": "choice",
        "equivalence_type": "choice_label",
        "checker_key": "choice_label_checker"
      },
      "checker_key_proposal": "choice_label_checker",
      "equivalence_type_proposal": "choice_label",
      "answer_shape": "choice_label",
      "confidence": "medium",
      "promote_recommendation": "conservative_hold_for_that_candidate",
      "promote_blockers": [
        "insufficient_examples_for_safe_promote"
      ],
      "risk_flags": []
    },
    {
      "problem_type_id": "absolute_value_inequality_malformed_source_review",
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "matched_example_ids": [
        4409
      ],
      "matched_example_count": 1,
      "unmatched_example_ids": [
        4400,
        4402,
        4403,
        4404,
        4405,
        4406,
        4407,
        4413,
        4499
      ],
      "representative_example_id": 4409,
      "structural_features": [
        "manual_review_or_free_response"
      ],
      "answer_contract_proposal": {
        "answer_type": "manual_review",
        "equivalence_type": "manual_review_or_ai_judged",
        "checker_key": "manual_review_checker"
      },
      "checker_key_proposal": "manual_review_checker",
      "equivalence_type_proposal": "manual_review_or_ai_judged",
      "answer_shape": "manual_review_or_free_response",
      "confidence": "medium",
      "promote_recommendation": "conservative_hold_for_that_candidate",
      "promote_blockers": [
        "insufficient_examples_for_safe_promote"
      ],
      "risk_flags": []
    }
  ],
  "per_example_classification": [
    {
      "example_id": 4400,
      "detected_problem_type_id": "absolute_value_inequality_zero_center_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4402,
      "detected_problem_type_id": "absolute_value_inequality_shifted_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4403,
      "detected_problem_type_id": "absolute_value_inequality_shifted_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4404,
      "detected_problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4405,
      "detected_problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4406,
      "detected_problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4407,
      "detected_problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4409,
      "detected_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "answer_shape": "manual_review_or_free_response",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [
        "source_text_malformed",
        "needs_import_review"
      ],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4413,
      "detected_problem_type_id": "absolute_value_inequality_zero_center_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4499,
      "detected_problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
      "answer_shape": "choice_label",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    }
  ],
  "source_classifications": [
    {
      "example_id": 4400,
      "detected_problem_type_id": "absolute_value_inequality_zero_center_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4402,
      "detected_problem_type_id": "absolute_value_inequality_shifted_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4403,
      "detected_problem_type_id": "absolute_value_inequality_shifted_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4404,
      "detected_problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4405,
      "detected_problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4406,
      "detected_problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4407,
      "detected_problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4409,
      "detected_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "answer_shape": "manual_review_or_free_response",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [
        "source_text_malformed",
        "needs_import_review"
      ],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4413,
      "detected_problem_type_id": "absolute_value_inequality_zero_center_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    },
    {
      "example_id": 4499,
      "detected_problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
      "answer_shape": "choice_label",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
      "title_or_source_label": "textbook_example"
    }
  ],
  "unclassified_examples": [],
  "risk_examples": [
    4409
  ],
  "split_or_merge_recommendation": "recommend_split_problem_types",
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
    "required": true,
    "reasons": [
      "manual_review_or_free_response_requires_exception_review"
    ]
  },
  "reports": {
    "phase1_summary_json": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase1_summary.json",
    "phase1_summary_md": "C:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase1_summary.md"
  },
  "next_action": "prepare_split_problem_types_then_promote_candidates",
  "timestamp": "2026-05-28T03:40:20.674445+00:00",
  "dry_run": true,
  "auto_review_summary": {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "candidate_problem_types": [
      {
        "problem_type_id": "absolute_value_inequality_linear_expression_basic",
        "proposed_problem_type_id": "absolute_value_inequality_linear_expression_basic",
        "matched_example_ids": [
          4404,
          4405,
          4406,
          4407
        ],
        "matched_example_count": 4,
        "unmatched_example_ids": [
          4400,
          4402,
          4403,
          4409,
          4413,
          4499
        ],
        "representative_example_id": 4404,
        "structural_features": [
          "expression"
        ],
        "answer_contract_proposal": {
          "answer_type": "expression",
          "equivalence_type": "exact_string",
          "checker_key": "exact_string_checker"
        },
        "checker_key_proposal": "exact_string_checker",
        "equivalence_type_proposal": "exact_string",
        "answer_shape": "expression",
        "confidence": "high",
        "promote_recommendation": "recommend_promote_for_that_candidate",
        "promote_blockers": [],
        "risk_flags": []
      },
      {
        "problem_type_id": "absolute_value_inequality_shifted_basic",
        "proposed_problem_type_id": "absolute_value_inequality_shifted_basic",
        "matched_example_ids": [
          4402,
          4403
        ],
        "matched_example_count": 2,
        "unmatched_example_ids": [
          4400,
          4404,
          4405,
          4406,
          4407,
          4409,
          4413,
          4499
        ],
        "representative_example_id": 4402,
        "structural_features": [
          "expression"
        ],
        "answer_contract_proposal": {
          "answer_type": "expression",
          "equivalence_type": "exact_string",
          "checker_key": "exact_string_checker"
        },
        "checker_key_proposal": "exact_string_checker",
        "equivalence_type_proposal": "exact_string",
        "answer_shape": "expression",
        "confidence": "medium",
        "promote_recommendation": "conservative_hold_for_that_candidate",
        "promote_blockers": [
          "insufficient_examples_for_safe_promote"
        ],
        "risk_flags": []
      },
      {
        "problem_type_id": "absolute_value_inequality_zero_center_basic",
        "proposed_problem_type_id": "absolute_value_inequality_zero_center_basic",
        "matched_example_ids": [
          4400,
          4413
        ],
        "matched_example_count": 2,
        "unmatched_example_ids": [
          4402,
          4403,
          4404,
          4405,
          4406,
          4407,
          4409,
          4499
        ],
        "representative_example_id": 4400,
        "structural_features": [
          "expression"
        ],
        "answer_contract_proposal": {
          "answer_type": "expression",
          "equivalence_type": "exact_string",
          "checker_key": "exact_string_checker"
        },
        "checker_key_proposal": "exact_string_checker",
        "equivalence_type_proposal": "exact_string",
        "answer_shape": "expression",
        "confidence": "medium",
        "promote_recommendation": "conservative_hold_for_that_candidate",
        "promote_blockers": [
          "insufficient_examples_for_safe_promote"
        ],
        "risk_flags": []
      },
      {
        "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
        "proposed_problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
        "matched_example_ids": [
          4499
        ],
        "matched_example_count": 1,
        "unmatched_example_ids": [
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
        "representative_example_id": 4499,
        "structural_features": [
          "choice_label"
        ],
        "answer_contract_proposal": {
          "answer_type": "choice",
          "equivalence_type": "choice_label",
          "checker_key": "choice_label_checker"
        },
        "checker_key_proposal": "choice_label_checker",
        "equivalence_type_proposal": "choice_label",
        "answer_shape": "choice_label",
        "confidence": "medium",
        "promote_recommendation": "conservative_hold_for_that_candidate",
        "promote_blockers": [
          "insufficient_examples_for_safe_promote"
        ],
        "risk_flags": []
      },
      {
        "problem_type_id": "absolute_value_inequality_malformed_source_review",
        "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
        "matched_example_ids": [
          4409
        ],
        "matched_example_count": 1,
        "unmatched_example_ids": [
          4400,
          4402,
          4403,
          4404,
          4405,
          4406,
          4407,
          4413,
          4499
        ],
        "representative_example_id": 4409,
        "structural_features": [
          "manual_review_or_free_response"
        ],
        "answer_contract_proposal": {
          "answer_type": "manual_review",
          "equivalence_type": "manual_review_or_ai_judged",
          "checker_key": "manual_review_checker"
        },
        "checker_key_proposal": "manual_review_checker",
        "equivalence_type_proposal": "manual_review_or_ai_judged",
        "answer_shape": "manual_review_or_free_response",
        "confidence": "medium",
        "promote_recommendation": "conservative_hold_for_that_candidate",
        "promote_blockers": [
          "insufficient_examples_for_safe_promote"
        ],
        "risk_flags": []
      }
    ],
    "proposal_items": [
      {
        "problem_type_id": "absolute_value_inequality_linear_expression_basic",
        "proposed_problem_type_id": "absolute_value_inequality_linear_expression_basic",
        "matched_example_ids": [
          4404,
          4405,
          4406,
          4407
        ],
        "matched_example_count": 4,
        "unmatched_example_ids": [
          4400,
          4402,
          4403,
          4409,
          4413,
          4499
        ],
        "representative_example_id": 4404,
        "structural_features": [
          "expression"
        ],
        "answer_contract_proposal": {
          "answer_type": "expression",
          "equivalence_type": "exact_string",
          "checker_key": "exact_string_checker"
        },
        "checker_key_proposal": "exact_string_checker",
        "equivalence_type_proposal": "exact_string",
        "answer_shape": "expression",
        "confidence": "high",
        "promote_recommendation": "recommend_promote_for_that_candidate",
        "promote_blockers": [],
        "risk_flags": []
      },
      {
        "problem_type_id": "absolute_value_inequality_shifted_basic",
        "proposed_problem_type_id": "absolute_value_inequality_shifted_basic",
        "matched_example_ids": [
          4402,
          4403
        ],
        "matched_example_count": 2,
        "unmatched_example_ids": [
          4400,
          4404,
          4405,
          4406,
          4407,
          4409,
          4413,
          4499
        ],
        "representative_example_id": 4402,
        "structural_features": [
          "expression"
        ],
        "answer_contract_proposal": {
          "answer_type": "expression",
          "equivalence_type": "exact_string",
          "checker_key": "exact_string_checker"
        },
        "checker_key_proposal": "exact_string_checker",
        "equivalence_type_proposal": "exact_string",
        "answer_shape": "expression",
        "confidence": "medium",
        "promote_recommendation": "conservative_hold_for_that_candidate",
        "promote_blockers": [
          "insufficient_examples_for_safe_promote"
        ],
        "risk_flags": []
      },
      {
        "problem_type_id": "absolute_value_inequality_zero_center_basic",
        "proposed_problem_type_id": "absolute_value_inequality_zero_center_basic",
        "matched_example_ids": [
          4400,
          4413
        ],
        "matched_example_count": 2,
        "unmatched_example_ids": [
          4402,
          4403,
          4404,
          4405,
          4406,
          4407,
          4409,
          4499
        ],
        "representative_example_id": 4400,
        "structural_features": [
          "expression"
        ],
        "answer_contract_proposal": {
          "answer_type": "expression",
          "equivalence_type": "exact_string",
          "checker_key": "exact_string_checker"
        },
        "checker_key_proposal": "exact_string_checker",
        "equivalence_type_proposal": "exact_string",
        "answer_shape": "expression",
        "confidence": "medium",
        "promote_recommendation": "conservative_hold_for_that_candidate",
        "promote_blockers": [
          "insufficient_examples_for_safe_promote"
        ],
        "risk_flags": []
      },
      {
        "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
        "proposed_problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
        "matched_example_ids": [
          4499
        ],
        "matched_example_count": 1,
        "unmatched_example_ids": [
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
        "representative_example_id": 4499,
        "structural_features": [
          "choice_label"
        ],
        "answer_contract_proposal": {
          "answer_type": "choice",
          "equivalence_type": "choice_label",
          "checker_key": "choice_label_checker"
        },
        "checker_key_proposal": "choice_label_checker",
        "equivalence_type_proposal": "choice_label",
        "answer_shape": "choice_label",
        "confidence": "medium",
        "promote_recommendation": "conservative_hold_for_that_candidate",
        "promote_blockers": [
          "insufficient_examples_for_safe_promote"
        ],
        "risk_flags": []
      },
      {
        "problem_type_id": "absolute_value_inequality_malformed_source_review",
        "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
        "matched_example_ids": [
          4409
        ],
        "matched_example_count": 1,
        "unmatched_example_ids": [
          4400,
          4402,
          4403,
          4404,
          4405,
          4406,
          4407,
          4413,
          4499
        ],
        "representative_example_id": 4409,
        "structural_features": [
          "manual_review_or_free_response"
        ],
        "answer_contract_proposal": {
          "answer_type": "manual_review",
          "equivalence_type": "manual_review_or_ai_judged",
          "checker_key": "manual_review_checker"
        },
        "checker_key_proposal": "manual_review_checker",
        "equivalence_type_proposal": "manual_review_or_ai_judged",
        "answer_shape": "manual_review_or_free_response",
        "confidence": "medium",
        "promote_recommendation": "conservative_hold_for_that_candidate",
        "promote_blockers": [
          "insufficient_examples_for_safe_promote"
        ],
        "risk_flags": []
      }
    ],
    "per_example_classification": [
      {
        "example_id": 4400,
        "detected_problem_type_id": "absolute_value_inequality_zero_center_basic",
        "answer_shape": "expression",
        "classification_confidence": "medium",
        "classification_reason": "classifier_or_proposal_mapping",
        "risk_flags": [],
        "title_or_source_label": "textbook_example"
      },
      {
        "example_id": 4402,
        "detected_problem_type_id": "absolute_value_inequality_shifted_basic",
        "answer_shape": "expression",
        "classification_confidence": "medium",
        "classification_reason": "classifier_or_proposal_mapping",
        "risk_flags": [],
        "title_or_source_label": "textbook_example"
      },
      {
        "example_id": 4403,
        "detected_problem_type_id": "absolute_value_inequality_shifted_basic",
        "answer_shape": "expression",
        "classification_confidence": "medium",
        "classification_reason": "classifier_or_proposal_mapping",
        "risk_flags": [],
        "title_or_source_label": "textbook_example"
      },
      {
        "example_id": 4404,
        "detected_problem_type_id": "absolute_value_inequality_linear_expression_basic",
        "answer_shape": "expression",
        "classification_confidence": "medium",
        "classification_reason": "classifier_or_proposal_mapping",
        "risk_flags": [],
        "title_or_source_label": "textbook_example"
      },
      {
        "example_id": 4405,
        "detected_problem_type_id": "absolute_value_inequality_linear_expression_basic",
        "answer_shape": "expression",
        "classification_confidence": "medium",
        "classification_reason": "classifier_or_proposal_mapping",
        "risk_flags": [],
        "title_or_source_label": "textbook_example"
      },
      {
        "example_id": 4406,
        "detected_problem_type_id": "absolute_value_inequality_linear_expression_basic",
        "answer_shape": "expression",
        "classification_confidence": "medium",
        "classification_reason": "classifier_or_proposal_mapping",
        "risk_flags": [],
        "title_or_source_label": "textbook_example"
      },
      {
        "example_id": 4407,
        "detected_problem_type_id": "absolute_value_inequality_linear_expression_basic",
        "answer_shape": "expression",
        "classification_confidence": "medium",
        "classification_reason": "classifier_or_proposal_mapping",
        "risk_flags": [],
        "title_or_source_label": "textbook_example"
      },
      {
        "example_id": 4409,
        "detected_problem_type_id": "absolute_value_inequality_malformed_source_review",
        "answer_shape": "manual_review_or_free_response",
        "classification_confidence": "medium",
        "classification_reason": "classifier_or_proposal_mapping",
        "risk_flags": [
          "source_text_malformed",
          "needs_import_review"
        ],
        "title_or_source_label": "textbook_example"
      },
      {
        "example_id": 4413,
        "detected_problem_type_id": "absolute_value_inequality_zero_center_basic",
        "answer_shape": "expression",
        "classification_confidence": "medium",
        "classification_reason": "classifier_or_proposal_mapping",
        "risk_flags": [],
        "title_or_source_label": "textbook_example"
      },
      {
        "example_id": 4499,
        "detected_problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
        "answer_shape": "choice_label",
        "classification_confidence": "medium",
        "classification_reason": "classifier_or_proposal_mapping",
        "risk_flags": [],
        "title_or_source_label": "textbook_example"
      }
    ],
    "split_or_merge_recommendation": "recommend_split_problem_types",
    "per_candidate_promote_gate": [
      {
        "problem_type_id": "absolute_value_inequality_linear_expression_basic",
        "promote_recommendation": "recommend_promote_for_that_candidate",
        "promote_blockers": []
      },
      {
        "problem_type_id": "absolute_value_inequality_shifted_basic",
        "promote_recommendation": "conservative_hold_for_that_candidate",
        "promote_blockers": [
          "insufficient_examples_for_safe_promote"
        ]
      },
      {
        "problem_type_id": "absolute_value_inequality_zero_center_basic",
        "promote_recommendation": "conservative_hold_for_that_candidate",
        "promote_blockers": [
          "insufficient_examples_for_safe_promote"
        ]
      },
      {
        "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
        "promote_recommendation": "conservative_hold_for_that_candidate",
        "promote_blockers": [
          "insufficient_examples_for_safe_promote"
        ]
      },
      {
        "problem_type_id": "absolute_value_inequality_malformed_source_review",
        "promote_recommendation": "conservative_hold_for_that_candidate",
        "promote_blockers": [
          "insufficient_examples_for_safe_promote"
        ]
      }
    ],
    "next_action": "prepare_split_problem_types_then_promote_candidates",
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
      "required": true,
      "reasons": [
        "manual_review_or_free_response_requires_exception_review"
      ]
    }
  },
  "classifier_source": "rule_pack",
  "ai_bootstrap_used": false,
  "ai_bootstrap_status": "not_used",
  "ai_bootstrap_confidence_summary": {},
  "inspect_report_note": "",
  "human_review_items": [
    {
      "source_index": 7,
      "display_source_index": 8,
      "example_id": 4409,
      "textbook_example_id": 4409,
      "source_type": "textbook_example",
      "title": "textbook_example#4409",
      "skill_id": "vh_數學B1_AbsoluteValueInequality",
      "skill_ch_name": "vh_數學B1_AbsoluteValueInequality",
      "matched_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "checker": "manual_review_checker",
      "equivalence": "manual_review_or_ai_judged",
      "reason": "Malformed absolute value inequality source text.",
      "review_reason": "Malformed absolute value inequality source text.",
      "question_preview": "試求下列不等式之解：(1)$| x |$3 (2) $| x |$ >= 4"
    }
  ]
}
```

## human_review_items

| source_index | title | example_id | source_type | matched_problem_type_id | checker | equivalence | reason | question_preview |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | textbook_example#4409 | 4409 | textbook_example | absolute_value_inequality_malformed_source_review | manual_review_checker | manual_review_or_ai_judged | Malformed absolute value inequality source text. | 試求下列不等式之解：(1)$\| x \|$3 (2) $\| x \|$ >= 4 |
