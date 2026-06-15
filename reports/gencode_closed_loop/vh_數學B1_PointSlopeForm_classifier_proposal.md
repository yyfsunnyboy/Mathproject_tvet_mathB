# Classifier Proposal: vh_數學B1_PointSlopeForm

## proposal
```json
{
  "skill_id": "vh_數學B1_PointSlopeForm",
  "proposed_problem_types": [
    "absolute_value_inequality_malformed_source_review"
  ],
  "proposed_example_map": [
    {
      "example_id": 4540,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "試求過點$<=ft( 2,-1 \\right)$且斜率為$\\frac{1}{2}$的直線方程式。"
    },
    {
      "example_id": 4541,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "試求過點$<=ft( 1,-2 \\right)$且斜率為−3的直線方程式。"
    },
    {
      "example_id": 4542,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "設$A<=ft( -1,1 \\right)$、$B<=ft( 3,-1 \\right)$，求$\\overline{AB}$之垂直平分線方程式。"
    },
    {
      "example_id": 4543,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "試求過點$A<=ft( 2,-1 \\right)$與$B<=ft( 0,3 \\right)$之直線方程式。"
    },
    {
      "example_id": 4546,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "試求斜率為3且x截距為5的直線方程式。"
    },
    {
      "example_id": 4549,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "(1)試求過點$<=ft( 2,-3 \\right)$，且斜率為$-\\frac{1}{2}$的直線方程式。\n(2)試求過點$<=ft( -1,4 \\right)$，且斜率為2的直線方程式。"
    },
    {
      "example_id": 4550,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "如圖，已知平面上兩鄉鎮的位置為、，今兩鄉鎮市民希望在鐵路沿線上設立一車站，此車站位於與兩鄉鎮距離相同的直線道路上，試求此車站所在的直線道路方程式。"
    },
    {
      "example_id": 4551,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "試求通過$A<=ft( 3,-1 \\right)$、$B<=ft( 2,1 \\right)$兩點的直線方程式。"
    },
    {
      "example_id": 4552,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "某農夫有塊三角形農地ABC，如圖所示，在平面上的坐標位置為$A<=ft( 8,-4 \\right)$、$B<=ft( 4,2 \\right)$、$C<=ft( 2,-2 \\right)$。今農夫欲將農地沿著過B點的直線平均分給兩個兒子耕種，試求平分農地的直線方程式為何？"
    },
    {
      "example_id": 4556,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "(1)試求過點$<=ft( -5,1 \\right)$，且斜率為3的直線方程式。\n(2)試求過點$<=ft( 1,-3 \\right)$，且斜率為$-\\frac{2}{3}$的直線方程式。."
    },
    {
      "example_id": 4557,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "設、，試求之垂直平分線方程式。"
    },
    {
      "example_id": 4560,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "試求通過$A<=ft( -3,1 \\right)$、$B<=ft( 2,4 \\right)$兩點的直線方程式。"
    },
    {
      "example_id": 4561,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "已知△ABC三頂點坐標分別為、、$C<=ft( -2,-4 \\right)$，試求$\\overline{BC}$邊上之中線方程式。"
    },
    {
      "example_id": 4606,
      "proposed_problem_type_id": "absolute_value_inequality_malformed_source_review",
      "reason": "heuristic_pattern_match",
      "problem_preview": "已知a、b為實數，若直線ax + by + 2 = 0通過點${{k}_{1}}$且斜率為$\\frac{2}{3}$，則a + b = (A) −3 (B) −1 (C) 1 (D) 3。"
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
    4540,
    4541,
    4542,
    4543,
    4546,
    4549,
    4550,
    4551,
    4552,
    4556,
    4557,
    4560,
    4561,
    4606
  ],
  "risk_flags": [
    "contains_malformed_or_unclassified_examples"
  ]
}
```
