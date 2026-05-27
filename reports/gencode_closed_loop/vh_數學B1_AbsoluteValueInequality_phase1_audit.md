# Gencode 第一階段盤點報告: vh_數學B1_AbsoluteValueInequality

## phase1
```json
{
  "skill_id": "vh_數學B1_AbsoluteValueInequality",
  "phase": "phase1_audit",
  "final_status": "AUDIT_PARTIAL",
  "examples_total": 10,
  "examples_covered": 10,
  "examples_map": [
    {
      "example_id": 4400,
      "title": "",
      "source_type": "textbook_example",
      "source_chapter": "unknown",
      "source_section": "unknown",
      "problem_preview": "試求下列不等式之解：\n(1)$| x |$<= 8 (2)$| x |$> 10 (3)$| x |$< 7 (4)$| x |$>= 12",
      "problem_text_hash": "5034e92b89964a520ce550c86a073519859d5acf",
      "skill_id": "vh_數學B1_AbsoluteValueInequality",
      "subskill_id": "absolute_value_inequality_zero_center_basic",
      "problem_type_id": "absolute_value_inequality_zero_center_basic",
      "runtime_category": "deterministic_expression",
      "classification_rule_id": "absi.rule.zero_center_basic",
      "classification_reason": "|x| 型不等式。",
      "classifier_confidence": "high",
      "semantic_risk_flags": [],
      "semantic_audit_status": "pass",
      "generator_status": "supported_deterministic",
      "manual_review_reason": ""
    },
    {
      "example_id": 4402,
      "title": "",
      "source_type": "textbook_example",
      "source_chapter": "unknown",
      "source_section": "unknown",
      "problem_preview": "解下列不等式：\n(1)$| x-2 |<= 4$ (2)$| x+5 |>1$",
      "problem_text_hash": "e7df2d6a9ca82a4ca5bd765c9a161880187f5710",
      "skill_id": "vh_數學B1_AbsoluteValueInequality",
      "subskill_id": "absolute_value_inequality_shifted_basic",
      "problem_type_id": "absolute_value_inequality_shifted_basic",
      "runtime_category": "deterministic_expression",
      "classification_rule_id": "absi.rule.shifted_basic",
      "classification_reason": "|x-a| / |x+a| 型不等式。",
      "classifier_confidence": "high",
      "semantic_risk_flags": [],
      "semantic_audit_status": "pass",
      "generator_status": "supported_deterministic",
      "manual_review_reason": ""
    },
    {
      "example_id": 4403,
      "title": "",
      "source_type": "textbook_example",
      "source_chapter": "unknown",
      "source_section": "unknown",
      "problem_preview": "解下列不等式：\n(1)$| x-3 |<2$ (2)$| x+5 |>= 4$",
      "problem_text_hash": "e32650392a61a1bf13d8985c7dc6e009acc48533",
      "skill_id": "vh_數學B1_AbsoluteValueInequality",
      "subskill_id": "absolute_value_inequality_shifted_basic",
      "problem_type_id": "absolute_value_inequality_shifted_basic",
      "runtime_category": "deterministic_expression",
      "classification_rule_id": "absi.rule.shifted_basic",
      "classification_reason": "|x-a| / |x+a| 型不等式。",
      "classifier_confidence": "high",
      "semantic_risk_flags": [],
      "semantic_audit_status": "pass",
      "generator_status": "supported_deterministic",
      "manual_review_reason": ""
    },
    {
      "example_id": 4404,
      "title": "",
      "source_type": "textbook_example",
      "source_chapter": "unknown",
      "source_section": "unknown",
      "problem_preview": "解不等式$| 4x+1 |<= 6$。",
      "problem_text_hash": "9d3e0a1f8302636a5e1ae2081922bf4d61aaa5fa",
      "skill_id": "vh_數學B1_AbsoluteValueInequality",
      "subskill_id": "absolute_value_inequality_linear_expression_basic",
      "problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "runtime_category": "deterministic_expression",
      "classification_rule_id": "absi.rule.linear_expression_basic",
      "classification_reason": "|ax+b| 不等式（a 非 1）",
      "classifier_confidence": "high",
      "semantic_risk_flags": [],
      "semantic_audit_status": "pass",
      "generator_status": "supported_deterministic",
      "manual_review_reason": ""
    },
    {
      "example_id": 4405,
      "title": "",
      "source_type": "textbook_example",
      "source_chapter": "unknown",
      "source_section": "unknown",
      "problem_preview": "解不等式$| 2x-3 |>1$。",
      "problem_text_hash": "32ed1d97f162b2623d91cb4dffa3a244c99c4ab0",
      "skill_id": "vh_數學B1_AbsoluteValueInequality",
      "subskill_id": "absolute_value_inequality_linear_expression_basic",
      "problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "runtime_category": "deterministic_expression",
      "classification_rule_id": "absi.rule.linear_expression_basic",
      "classification_reason": "|ax+b| 不等式（a 非 1）",
      "classifier_confidence": "high",
      "semantic_risk_flags": [],
      "semantic_audit_status": "pass",
      "generator_status": "supported_deterministic",
      "manual_review_reason": ""
    },
    {
      "example_id": 4406,
      "title": "",
      "source_type": "textbook_example",
      "source_chapter": "unknown",
      "source_section": "unknown",
      "problem_preview": "解不等式$| 3x-1 |>= 7$。",
      "problem_text_hash": "f3116732a3667451816b044388177d253a2b5f7a",
      "skill_id": "vh_數學B1_AbsoluteValueInequality",
      "subskill_id": "absolute_value_inequality_linear_expression_basic",
      "problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "runtime_category": "deterministic_expression",
      "classification_rule_id": "absi.rule.linear_expression_basic",
      "classification_reason": "|ax+b| 不等式（a 非 1）",
      "classifier_confidence": "high",
      "semantic_risk_flags": [],
      "semantic_audit_status": "pass",
      "generator_status": "supported_deterministic",
      "manual_review_reason": ""
    },
    {
      "example_id": 4407,
      "title": "",
      "source_type": "textbook_example",
      "source_chapter": "unknown",
      "source_section": "unknown",
      "problem_preview": "解不等式$| 5x+3 |<7$。",
      "problem_text_hash": "01450509681b8f4bda1ac29bd6f9c1d962192921",
      "skill_id": "vh_數學B1_AbsoluteValueInequality",
      "subskill_id": "absolute_value_inequality_linear_expression_basic",
      "problem_type_id": "absolute_value_inequality_linear_expression_basic",
      "runtime_category": "deterministic_expression",
      "classification_rule_id": "absi.rule.linear_expression_basic",
      "classification_reason": "|ax+b| 不等式（a 非 1）",
      "classifier_confidence": "high",
      "semantic_risk_flags": [],
      "semantic_audit_status": "pass",
      "generator_status": "supported_deterministic",
      "manual_review_reason": ""
    },
    {
      "example_id": 4409,
      "title": "",
      "source_type": "textbook_example",
      "source_chapter": "unknown",
      "source_section": "unknown",
      "problem_preview": "試求下列不等式之解：(1)$| x |$ <= 3 (2) $| x |$ >= 4",
      "problem_text_hash": "cd0a5e716b3ca2d54dacf05addca22151d278fe7",
      "skill_id": "vh_數學B1_AbsoluteValueInequality",
      "subskill_id": "absolute_value_inequality_zero_center_basic",
      "problem_type_id": "absolute_value_inequality_zero_center_basic",
      "runtime_category": "deterministic_expression",
      "classification_rule_id": "absi.rule.zero_center_basic",
      "classification_reason": "|x| 型不等式。",
      "classifier_confidence": "high",
      "semantic_risk_flags": [],
      "semantic_audit_status": "pass",
      "generator_status": "supported_deterministic",
      "manual_review_reason": ""
    },
    {
      "example_id": 4413,
      "title": "",
      "source_type": "textbook_example",
      "source_chapter": "unknown",
      "source_section": "unknown",
      "problem_preview": "試求下列不等式之解：(1) $| x |$ <= 6 (2) $| x |$> 5",
      "problem_text_hash": "677395353276b8f49e3a56cb115a31562f2e7af7",
      "skill_id": "vh_數學B1_AbsoluteValueInequality",
      "subskill_id": "absolute_value_inequality_zero_center_basic",
      "problem_type_id": "absolute_value_inequality_zero_center_basic",
      "runtime_category": "deterministic_expression",
      "classification_rule_id": "absi.rule.zero_center_basic",
      "classification_reason": "|x| 型不等式。",
      "classifier_confidence": "high",
      "semantic_risk_flags": [],
      "semantic_audit_status": "pass",
      "generator_status": "supported_deterministic",
      "manual_review_reason": ""
    },
    {
      "example_id": 4499,
      "title": "",
      "source_type": "textbook_example",
      "source_chapter": "unknown",
      "source_section": "unknown",
      "problem_preview": "試求滿足不等式$| 3x-2 |<= 8$的整數x共有多少個？ (A) 4 (B) 5 (C) 6 (D) 7。",
      "problem_text_hash": "5cba656a8b6ae30004bf9bcaed601564b5ba7c6b",
      "skill_id": "vh_數學B1_AbsoluteValueInequality",
      "subskill_id": "absolute_value_inequality_integer_solution_count_choice",
      "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
      "runtime_category": "deterministic_choice",
      "classification_rule_id": "absi.rule.integer_solution_count_choice",
      "classification_reason": "整數解個數選擇題。",
      "classifier_confidence": "high",
      "semantic_risk_flags": [],
      "semantic_audit_status": "pass",
      "generator_status": "supported_deterministic",
      "manual_review_reason": ""
    }
  ],
  "auto_review_summary": {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
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
    "proposal_items": [
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
    }
  },
  "recommended_next_phase": "review_classifier_proposal",
  "blocking_reasons": [],
  "warnings": [
    "insufficient_examples",
    "low_source_examples"
  ],
  "artifact_paths": {
    "auto_pipeline_summary_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_auto_pipeline_summary.json",
    "auto_pipeline_summary_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_auto_pipeline_summary.md",
    "classifier_pending_spec_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_classifier_pending_spec.json",
    "generator_draft_spec_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_generator_draft_spec.json",
    "phase1_json": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase1_audit.json",
    "phase1_md": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_AbsoluteValueInequality_phase1_audit.md"
  },
  "timestamp": "2026-05-27T06:17:57.998038+00:00"
}
```
