# Gencode Auto Pipeline Summary: vh_數學B1_AbsoluteValueInequality

## summary
```json
{
  "ok": true,
  "skill_id": "vh_數學B1_AbsoluteValueInequality",
  "pipeline_status": "auto_pipeline_completed_runtime_blocked",
  "source_example_count": 10,
  "candidate_problem_types": [
    {
      "problem_type_id": "absolute_value_inequality_linear_expression_basic",
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
      "problem_type_id": "absolute_value_inequality_zero_center_basic",
      "matched_example_ids": [
        4400,
        4409,
        4413
      ],
      "matched_example_count": 3,
      "unmatched_example_ids": [
        4402,
        4403,
        4404,
        4405,
        4406,
        4407,
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
      "confidence": "high",
      "promote_recommendation": "recommend_promote_for_that_candidate",
      "promote_blockers": [],
      "risk_flags": []
    },
    {
      "problem_type_id": "absolute_value_inequality_shifted_basic",
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
      "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
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
      "detected_problem_type_id": "absolute_value_inequality_zero_center_basic",
      "answer_shape": "expression",
      "classification_confidence": "medium",
      "classification_reason": "classifier_or_proposal_mapping",
      "risk_flags": [],
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
    "auto_pipeline_summary_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_auto_pipeline_summary.json",
    "auto_pipeline_summary_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_auto_pipeline_summary.md",
    "classifier_pending_spec_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_classifier_pending_spec.json",
    "generator_draft_spec_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_generator_draft_spec.json",
    "phase1_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase1_audit.json",
    "phase1_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase1_audit.md"
  },
  "next_action": "review_generator_draft_specs",
  "timestamp": "2026-05-27T06:17:57.995044+00:00",
  "dry_run": true
}
```
