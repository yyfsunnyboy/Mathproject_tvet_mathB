# Classifier Proposal: vh_數學B1_VertexFormOfQuadraticFunction

## proposal
```json
{
  "skill_id": "vh_數學B1_VertexFormOfQuadraticFunction",
  "proposed_problem_types": [
    "absolute_value_inequality_malformed_source_review"
  ],
  "proposed_example_map": [
    {
      "example_id": 4451,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "(1)$y=-3{{<=ft( x+2 \\right)}^{2}}-5$的圖形，是由$y=-3{{x}^{2}}$，水平向左平移① 個單位，然後再鉛直向下平移② 個單位，且其對稱軸為直線③ ，頂點為④ 。\n(2)$y=\\frac{1}{3}{{<=ft( x-4 \\right)}^{2}}+7$的圖形，是由$y=\\fr"
    },
    {
      "example_id": 4452,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "試求下列函數平移到新頂點後的新函數。\n函數\n新頂點\n新函數\n(1)$y={{x}^{2}}$\n$(1,-2)$\n(2)$y=-3{{x}^{2}}$\n$<=ft( -2,-1 \\right)$"
    },
    {
      "example_id": 4453,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "畫出下列函數的概略圖形，並求其開口方向、頂點坐標、對稱軸、最大值或最小值。\n(1)$y=3{{<=ft( x-2 \\right)}^{2}}+5$\n(2)$y=-2{{<=ft( x+4 \\right)}^{2}}-6$"
    },
    {
      "example_id": 4456,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "已知$y=f<=ft( x \\right)={{x}^{2}}+px+q$圖形最低點的坐標為$<=ft( 2,5 \\right)$，試求p + q之值。"
    },
    {
      "example_id": 4504,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "設二次函數$y=f<=ft( x \\right)=a{{x}^{2}}+bx+c$圖形的頂點為$<=ft( 1,3 \\right)$且交y軸於點$<=ft( 0,1 \\right)$，則$f<=ft( 3 \\right)$之值為何？ (A) −6 (B) −5 (C) −4 (D) −3。"
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
    4451,
    4452,
    4453,
    4456,
    4504
  ],
  "risk_flags": [
    "contains_malformed_or_unclassified_examples"
  ]
}
```
