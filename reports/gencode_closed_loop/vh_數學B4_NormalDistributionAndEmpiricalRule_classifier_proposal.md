# Classifier Proposal: vh_數學B4_NormalDistributionAndEmpiricalRule

## proposal
```json
{
  "skill_id": "vh_數學B4_NormalDistributionAndEmpiricalRule",
  "proposed_problem_types": [
    "absolute_value_inequality_malformed_source_review"
  ],
  "proposed_example_map": [
    {
      "example_id": 3856,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "某校 2000 個學生，英文成績呈常態分配，平均 55 分，標準差 5 分。求：(1) 50~60 分人數；(2) 60 分以上人數；(3) 低於 40 分人數。"
    },
    {
      "example_id": 3857,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "某校 1000 個學生，英文成績呈常態分配，平均 60 分，標準差 10 分。求：(1) 高於 60 分人數；(2) 50 分以下人數；(3) 50~70 分人數。"
    },
    {
      "example_id": 3858,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "某校 2000 個學生，英文成績呈常態分配，平均 55 分，標準差 5 分。求：(1) 45~65 分人數；(2) 50 分以下人數。"
    },
    {
      "example_id": 3859,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "某年統測，甲、乙兩科成績直方圖如圖所示，下列敘述何者正確？(A)甲平均比乙大；(B)甲中位數比乙大；(C)甲全距比乙大；(D)甲標準差比乙大。"
    },
    {
      "example_id": 3897,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "某校500位新生第一次數學段考成績平均分數是58分，標準差是4分，若成績呈常態分配，則成績介於62到54分的學生約有多少人？(A) 170 (B) 250 (C) 340 (D) 400。"
    },
    {
      "example_id": 3898,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "某次數學考試共有1000人參加。若成績呈常態分配，且平均數為62分，標準差為8分，則成績低於70分的人數為何？ (A)介於581人與660人之間 (B)介於661人與740人之間 (C)介於741人與820人之間 (D)介於821人與900人之間。"
    }
  ],
  "proposed_answer_contracts": {
    "absolute_value_inequality_malformed_source_review": {
      "answer_type": "manual_review",
      "equivalence_type": "manual_review_or_ai_judged",
      "checker_key": "manual_review_checker",
      "order_matters": false,
      "accepted_format_notes": [
        "requires source text correction before deterministic generation"
      ],
      "canonical_answer_schema": {
        "type": "manual_review"
      }
    }
  },
  "manual_review_candidates": [
    3856,
    3857,
    3858,
    3859,
    3897,
    3898
  ],
  "risk_flags": [
    "contains_malformed_or_unclassified_examples"
  ]
}
```
