# Verify Report: vh_數學B1_PropertiesOfPerpendicularLines

- python: C:\Python314\python.exe
- registry: E:\Python\Mathproject_tvet_mathB\configs\generated_registry\b1_section_1_1_verified_registry.v0.1.yaml
- registry_verified_count: 1
- pytest_exit_code: 0
- unique_problem_type_count: 1
- PASS: True

## Runtime ProblemType Coverage
```json
{
  "expected_problem_types": [
    "perpendicular_lines_properties"
  ],
  "observed_problem_types": [
    "perpendicular_lines_properties"
  ],
  "missing_problem_types": [],
  "sample_count": 30,
  "status": "pass"
}
```

## Verified Entries
```json
[
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_2_1/perpendicular_lines_properties/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "rational",
    "checker_type": "rational_checker"
  }
]
```

## Pytest Output
```text
.....                                                                    [100%]
5 passed in 0.08s
```

## Samples
```json
[
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 2,4 \\right)$、$B\\left( 3,1 \\right)$與$C\\left( -5,4 \\right)$、$D\\left( -2,k \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "5",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{1 - (4)}{3 - (2)} = -3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{k - (4)}{-2 - (-5)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-3 \\cdot \\frac{k - (4)}{3} = -1$，",
      "解得 k = 5。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s4",
      "parameter_signature": "m1=-3:template=1:answer=5",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 2,4 \\right)$、$B\\left( 3,1 \\right)$與$C\\left( -5,4 \\right)$、$D\\left( -2,k \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "5",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{1 - (4)}{3 - (2)} = -3$。\n直線CD的斜率為 $m_{CD} = \\frac{k - (4)}{-2 - (-5)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-3 \\cdot \\frac{k - (4)}{3} = -1$，\n解得 k = 5。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "5"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 3,-4 \\right)$、$B\\left( 2,-1 \\right)$與$C\\left( -3,4 \\right)$、$D\\left( 0,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "5",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-1 - (-4)}{2 - (3)} = -3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - (4)}{0 - (-3)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-3 \\cdot \\frac{a - (4)}{3} = -1$，",
      "解得 a = 5。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s2",
      "parameter_signature": "m1=-3:template=1:answer=5",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 3,-4 \\right)$、$B\\left( 2,-1 \\right)$與$C\\left( -3,4 \\right)$、$D\\left( 0,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "5",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-1 - (-4)}{2 - (3)} = -3$。\n直線CD的斜率為 $m_{CD} = \\frac{a - (4)}{0 - (-3)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-3 \\cdot \\frac{a - (4)}{3} = -1$，\n解得 a = 5。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "5"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 0,0 \\right)$、$B\\left( -1,2 \\right)$與$C\\left( -2,-1 \\right)$、$D\\left( x,0 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "answer": "0",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{2 - (0)}{-1 - (0)} = -2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{0 - (-1)}{x - (-2)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2 \\cdot \\frac{1}{x - (-2)} = -1$，",
      "解得 x = 0。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s6",
      "parameter_signature": "m1=-2:template=2:answer=0",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 0,0 \\right)$、$B\\left( -1,2 \\right)$與$C\\left( -2,-1 \\right)$、$D\\left( x,0 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "correct_answer": "0",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{2 - (0)}{-1 - (0)} = -2$。\n直線CD的斜率為 $m_{CD} = \\frac{0 - (-1)}{x - (-2)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2 \\cdot \\frac{1}{x - (-2)} = -1$，\n解得 x = 0。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "0"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -1,0 \\right)$、$B\\left( -3,1 \\right)$與$C\\left( -4,-3 \\right)$、$D\\left( x,-1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "answer": "-3",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{1 - (0)}{-3 - (-1)} = -1/2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-1 - (-3)}{x - (-4)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/2 \\cdot \\frac{2}{x - (-4)} = -1$，",
      "解得 x = -3。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s7",
      "parameter_signature": "m1=-1/2:template=2:answer=-3",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -1,0 \\right)$、$B\\left( -3,1 \\right)$與$C\\left( -4,-3 \\right)$、$D\\left( x,-1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "correct_answer": "-3",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{1 - (0)}{-3 - (-1)} = -1/2$。\n直線CD的斜率為 $m_{CD} = \\frac{-1 - (-3)}{x - (-4)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/2 \\cdot \\frac{2}{x - (-4)} = -1$，\n解得 x = -3。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-3"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 5,1 \\right)$、$B\\left( 8,-1 \\right)$與$C\\left( -2,4 \\right)$、$D\\left( -4,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "1",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-1 - (1)}{8 - (5)} = -2/3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - (4)}{-4 - (-2)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2/3 \\cdot \\frac{a - (4)}{-2} = -1$，",
      "解得 a = 1。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s3",
      "parameter_signature": "m1=-2/3:template=1:answer=1",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 5,1 \\right)$、$B\\left( 8,-1 \\right)$與$C\\left( -2,4 \\right)$、$D\\left( -4,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "1",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-1 - (1)}{8 - (5)} = -2/3$。\n直線CD的斜率為 $m_{CD} = \\frac{a - (4)}{-4 - (-2)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2/3 \\cdot \\frac{a - (4)}{-2} = -1$，\n解得 a = 1。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "1"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -1,a \\right)$、$B\\left( -2,-5 \\right)$與$C\\left( 3,0 \\right)$、$D\\left( 2,1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "-4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-5 - a}{-2 - (-1)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{1 - (0)}{2 - (3)} = -1$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-5 - a}{-1} \\cdot (-1) = -1，",
      "解得 a = -4。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s3",
      "parameter_signature": "m1=1:template=3:answer=-4",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -1,a \\right)$、$B\\left( -2,-5 \\right)$與$C\\left( 3,0 \\right)$、$D\\left( 2,1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "-4",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-5 - a}{-2 - (-1)}$。\n直線CD的斜率為 $m_{CD} = \\frac{1 - (0)}{2 - (3)} = -1$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-5 - a}{-1} \\cdot (-1) = -1，\n解得 a = -4。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-4"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -4,a \\right)$、$B\\left( -6,-1 \\right)$與$C\\left( 1,2 \\right)$、$D\\left( 4,0 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "2",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-1 - a}{-6 - (-4)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{0 - (2)}{4 - (1)} = -2/3$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-1 - a}{-2} \\cdot (-2/3) = -1，",
      "解得 a = 2。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s8",
      "parameter_signature": "m1=3/2:template=3:answer=2",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -4,a \\right)$、$B\\left( -6,-1 \\right)$與$C\\left( 1,2 \\right)$、$D\\left( 4,0 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "2",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-1 - a}{-6 - (-4)}$。\n直線CD的斜率為 $m_{CD} = \\frac{0 - (2)}{4 - (1)} = -2/3$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-1 - a}{-2} \\cdot (-2/3) = -1，\n解得 a = 2。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "2"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -3,-2 \\right)$、$B\\left( 0,-4 \\right)$與$C\\left( 2,5 \\right)$、$D\\left( k,8 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-4 - (-2)}{0 - (-3)} = -2/3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{8 - (5)}{k - (2)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2/3 \\cdot \\frac{3}{k - (2)} = -1$，",
      "解得 k = 4。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s8",
      "parameter_signature": "m1=-2/3:template=2:answer=4",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -3,-2 \\right)$、$B\\left( 0,-4 \\right)$與$C\\left( 2,5 \\right)$、$D\\left( k,8 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "4",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-4 - (-2)}{0 - (-3)} = -2/3$。\n直線CD的斜率為 $m_{CD} = \\frac{8 - (5)}{k - (2)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2/3 \\cdot \\frac{3}{k - (2)} = -1$，\n解得 k = 4。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "4"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -1,k \\right)$、$B\\left( -3,2 \\right)$與$C\\left( 5,2 \\right)$、$D\\left( 8,0 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "5",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{2 - k}{-3 - (-1)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{0 - (2)}{8 - (5)} = -2/3$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{2 - k}{-2} \\cdot (-2/3) = -1，",
      "解得 k = 5。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s3",
      "parameter_signature": "m1=3/2:template=3:answer=5",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -1,k \\right)$、$B\\left( -3,2 \\right)$與$C\\left( 5,2 \\right)$、$D\\left( 8,0 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "5",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{2 - k}{-3 - (-1)}$。\n直線CD的斜率為 $m_{CD} = \\frac{0 - (2)}{8 - (5)} = -2/3$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{2 - k}{-2} \\cdot (-2/3) = -1，\n解得 k = 5。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "5"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 5,0 \\right)$、$B\\left( 4,-1 \\right)$與$C\\left( 2,-2 \\right)$、$D\\left( 3,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "-3",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-1 - (0)}{4 - (5)} = 1$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - (-2)}{3 - (2)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$1 \\cdot \\frac{a - (-2)}{1} = -1$，",
      "解得 a = -3。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s8",
      "parameter_signature": "m1=1:template=1:answer=-3",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 5,0 \\right)$、$B\\left( 4,-1 \\right)$與$C\\left( 2,-2 \\right)$、$D\\left( 3,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "-3",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-1 - (0)}{4 - (5)} = 1$。\n直線CD的斜率為 $m_{CD} = \\frac{a - (-2)}{3 - (2)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$1 \\cdot \\frac{a - (-2)}{1} = -1$，\n解得 a = -3。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-3"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 0,4 \\right)$、$B\\left( -3,6 \\right)$與$C\\left( -1,2 \\right)$、$D\\left( -3,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "answer": "-1",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{6 - (4)}{-3 - (0)} = -2/3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{x - (2)}{-3 - (-1)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2/3 \\cdot \\frac{x - (2)}{-2} = -1$，",
      "解得 x = -1。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s2",
      "parameter_signature": "m1=-2/3:template=1:answer=-1",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 0,4 \\right)$、$B\\left( -3,6 \\right)$與$C\\left( -1,2 \\right)$、$D\\left( -3,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "correct_answer": "-1",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{6 - (4)}{-3 - (0)} = -2/3$。\n直線CD的斜率為 $m_{CD} = \\frac{x - (2)}{-3 - (-1)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2/3 \\cdot \\frac{x - (2)}{-2} = -1$，\n解得 x = -1。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-1"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 0,3 \\right)$、$B\\left( -1,4 \\right)$與$C\\left( 2,-1 \\right)$、$D\\left( 3,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "0",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{4 - (3)}{-1 - (0)} = -1$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - (-1)}{3 - (2)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1 \\cdot \\frac{a - (-1)}{1} = -1$，",
      "解得 a = 0。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s8",
      "parameter_signature": "m1=-1:template=1:answer=0",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 0,3 \\right)$、$B\\left( -1,4 \\right)$與$C\\left( 2,-1 \\right)$、$D\\left( 3,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "0",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{4 - (3)}{-1 - (0)} = -1$。\n直線CD的斜率為 $m_{CD} = \\frac{a - (-1)}{3 - (2)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1 \\cdot \\frac{a - (-1)}{1} = -1$，\n解得 a = 0。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "0"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 5,-5 \\right)$、$B\\left( 8,-3 \\right)$與$C\\left( -4,-1 \\right)$、$D\\left( -2,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "-4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-3 - (-5)}{8 - (5)} = 2/3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - (-1)}{-2 - (-4)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$2/3 \\cdot \\frac{a - (-1)}{2} = -1$，",
      "解得 a = -4。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m1=2/3:template=1:answer=-4",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 5,-5 \\right)$、$B\\left( 8,-3 \\right)$與$C\\left( -4,-1 \\right)$、$D\\left( -2,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "-4",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-3 - (-5)}{8 - (5)} = 2/3$。\n直線CD的斜率為 $m_{CD} = \\frac{a - (-1)}{-2 - (-4)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$2/3 \\cdot \\frac{a - (-1)}{2} = -1$，\n解得 a = -4。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-4"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -3,0 \\right)$、$B\\left( -4,-3 \\right)$與$C\\left( -2,-5 \\right)$、$D\\left( k,-6 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "1",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-3 - (0)}{-4 - (-3)} = 3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-6 - (-5)}{k - (-2)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$3 \\cdot \\frac{-1}{k - (-2)} = -1$，",
      "解得 k = 1。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s6",
      "parameter_signature": "m1=3:template=2:answer=1",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -3,0 \\right)$、$B\\left( -4,-3 \\right)$與$C\\left( -2,-5 \\right)$、$D\\left( k,-6 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "1",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-3 - (0)}{-4 - (-3)} = 3$。\n直線CD的斜率為 $m_{CD} = \\frac{-6 - (-5)}{k - (-2)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$3 \\cdot \\frac{-1}{k - (-2)} = -1$，\n解得 k = 1。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "1"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 0,-3 \\right)$、$B\\left( -1,-1 \\right)$與$C\\left( 4,-2 \\right)$、$D\\left( 6,k \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "-1",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-1 - (-3)}{-1 - (0)} = -2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{k - (-2)}{6 - (4)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2 \\cdot \\frac{k - (-2)}{2} = -1$，",
      "解得 k = -1。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s3",
      "parameter_signature": "m1=-2:template=1:answer=-1",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 0,-3 \\right)$、$B\\left( -1,-1 \\right)$與$C\\left( 4,-2 \\right)$、$D\\left( 6,k \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "-1",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-1 - (-3)}{-1 - (0)} = -2$。\n直線CD的斜率為 $m_{CD} = \\frac{k - (-2)}{6 - (4)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2 \\cdot \\frac{k - (-2)}{2} = -1$，\n解得 k = -1。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-1"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -5,3 \\right)$、$B\\left( -4,6 \\right)$與$C\\left( 4,-1 \\right)$、$D\\left( 1,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "answer": "0",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{6 - (3)}{-4 - (-5)} = 3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{x - (-1)}{1 - (4)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$3 \\cdot \\frac{x - (-1)}{-3} = -1$，",
      "解得 x = 0。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m1=3:template=1:answer=0",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -5,3 \\right)$、$B\\left( -4,6 \\right)$與$C\\left( 4,-1 \\right)$、$D\\left( 1,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "correct_answer": "0",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{6 - (3)}{-4 - (-5)} = 3$。\n直線CD的斜率為 $m_{CD} = \\frac{x - (-1)}{1 - (4)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$3 \\cdot \\frac{x - (-1)}{-3} = -1$，\n解得 x = 0。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "0"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 0,k \\right)$、$B\\left( 1,-2 \\right)$與$C\\left( 5,3 \\right)$、$D\\left( 3,4 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "-4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-2 - k}{1 - (0)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{4 - (3)}{3 - (5)} = -1/2$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-2 - k}{1} \\cdot (-1/2) = -1，",
      "解得 k = -4。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s6",
      "parameter_signature": "m1=2:template=3:answer=-4",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 0,k \\right)$、$B\\left( 1,-2 \\right)$與$C\\left( 5,3 \\right)$、$D\\left( 3,4 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "-4",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-2 - k}{1 - (0)}$。\n直線CD的斜率為 $m_{CD} = \\frac{4 - (3)}{3 - (5)} = -1/2$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-2 - k}{1} \\cdot (-1/2) = -1，\n解得 k = -4。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-4"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 5,k \\right)$、$B\\left( 3,0 \\right)$與$C\\left( -5,-5 \\right)$、$D\\left( -6,-7 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "-1",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{0 - k}{3 - (5)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-7 - (-5)}{-6 - (-5)} = 2$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{0 - k}{-2} \\cdot (2) = -1，",
      "解得 k = -1。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s8",
      "parameter_signature": "m1=-1/2:template=3:answer=-1",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 5,k \\right)$、$B\\left( 3,0 \\right)$與$C\\left( -5,-5 \\right)$、$D\\left( -6,-7 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "-1",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{0 - k}{3 - (5)}$。\n直線CD的斜率為 $m_{CD} = \\frac{-7 - (-5)}{-6 - (-5)} = 2$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{0 - k}{-2} \\cdot (2) = -1，\n解得 k = -1。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-1"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -3,-3 \\right)$、$B\\left( -4,-1 \\right)$與$C\\left( 3,-2 \\right)$、$D\\left( 5,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "-1",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-1 - (-3)}{-4 - (-3)} = -2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - (-2)}{5 - (3)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2 \\cdot \\frac{a - (-2)}{2} = -1$，",
      "解得 a = -1。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s1",
      "parameter_signature": "m1=-2:template=1:answer=-1",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -3,-3 \\right)$、$B\\left( -4,-1 \\right)$與$C\\left( 3,-2 \\right)$、$D\\left( 5,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "-1",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-1 - (-3)}{-4 - (-3)} = -2$。\n直線CD的斜率為 $m_{CD} = \\frac{a - (-2)}{5 - (3)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2 \\cdot \\frac{a - (-2)}{2} = -1$，\n解得 a = -1。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-1"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -4,-5 \\right)$、$B\\left( -7,-4 \\right)$與$C\\left( 0,1 \\right)$、$D\\left( 1,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "answer": "4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-4 - (-5)}{-7 - (-4)} = -1/3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{x - (1)}{1 - (0)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/3 \\cdot \\frac{x - (1)}{1} = -1$，",
      "解得 x = 4。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s4",
      "parameter_signature": "m1=-1/3:template=1:answer=4",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -4,-5 \\right)$、$B\\left( -7,-4 \\right)$與$C\\left( 0,1 \\right)$、$D\\left( 1,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "correct_answer": "4",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-4 - (-5)}{-7 - (-4)} = -1/3$。\n直線CD的斜率為 $m_{CD} = \\frac{x - (1)}{1 - (0)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/3 \\cdot \\frac{x - (1)}{1} = -1$，\n解得 x = 4。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "4"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 4,4 \\right)$、$B\\left( 5,7 \\right)$與$C\\left( -5,-5 \\right)$、$D\\left( k,-6 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "-2",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{7 - (4)}{5 - (4)} = 3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-6 - (-5)}{k - (-5)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$3 \\cdot \\frac{-1}{k - (-5)} = -1$，",
      "解得 k = -2。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s2",
      "parameter_signature": "m1=3:template=2:answer=-2",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 4,4 \\right)$、$B\\left( 5,7 \\right)$與$C\\left( -5,-5 \\right)$、$D\\left( k,-6 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "-2",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{7 - (4)}{5 - (4)} = 3$。\n直線CD的斜率為 $m_{CD} = \\frac{-6 - (-5)}{k - (-5)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$3 \\cdot \\frac{-1}{k - (-5)} = -1$，\n解得 k = -2。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-2"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 1,k \\right)$、$B\\left( 2,4 \\right)$與$C\\left( -5,2 \\right)$、$D\\left( -3,1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "2",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{4 - k}{2 - (1)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{1 - (2)}{-3 - (-5)} = -1/2$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{4 - k}{1} \\cdot (-1/2) = -1，",
      "解得 k = 2。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s8",
      "parameter_signature": "m1=2:template=3:answer=2",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 1,k \\right)$、$B\\left( 2,4 \\right)$與$C\\left( -5,2 \\right)$、$D\\left( -3,1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "2",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{4 - k}{2 - (1)}$。\n直線CD的斜率為 $m_{CD} = \\frac{1 - (2)}{-3 - (-5)} = -1/2$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{4 - k}{1} \\cdot (-1/2) = -1，\n解得 k = 2。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "2"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 4,1 \\right)$、$B\\left( 7,2 \\right)$與$C\\left( -4,-3 \\right)$、$D\\left( -3,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "-6",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{2 - (1)}{7 - (4)} = 1/3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - (-3)}{-3 - (-4)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$1/3 \\cdot \\frac{a - (-3)}{1} = -1$，",
      "解得 a = -6。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s6",
      "parameter_signature": "m1=1/3:template=1:answer=-6",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 4,1 \\right)$、$B\\left( 7,2 \\right)$與$C\\left( -4,-3 \\right)$、$D\\left( -3,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "-6",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{2 - (1)}{7 - (4)} = 1/3$。\n直線CD的斜率為 $m_{CD} = \\frac{a - (-3)}{-3 - (-4)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$1/3 \\cdot \\frac{a - (-3)}{1} = -1$，\n解得 a = -6。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-6"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -3,k \\right)$、$B\\left( 0,3 \\right)$與$C\\left( -4,1 \\right)$、$D\\left( -3,4 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{3 - k}{0 - (-3)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{4 - (1)}{-3 - (-4)} = 3$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{3 - k}{3} \\cdot (3) = -1，",
      "解得 k = 4。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m1=-1/3:template=3:answer=4",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -3,k \\right)$、$B\\left( 0,3 \\right)$與$C\\left( -4,1 \\right)$、$D\\left( -3,4 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "4",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{3 - k}{0 - (-3)}$。\n直線CD的斜率為 $m_{CD} = \\frac{4 - (1)}{-3 - (-4)} = 3$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{3 - k}{3} \\cdot (3) = -1，\n解得 k = 4。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "4"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 1,a \\right)$、$B\\left( 0,-2 \\right)$與$C\\left( -5,4 \\right)$、$D\\left( -3,3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "0",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-2 - a}{0 - (1)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{3 - (4)}{-3 - (-5)} = -1/2$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-2 - a}{-1} \\cdot (-1/2) = -1，",
      "解得 a = 0。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s8",
      "parameter_signature": "m1=2:template=3:answer=0",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 1,a \\right)$、$B\\left( 0,-2 \\right)$與$C\\left( -5,4 \\right)$、$D\\left( -3,3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "0",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-2 - a}{0 - (1)}$。\n直線CD的斜率為 $m_{CD} = \\frac{3 - (4)}{-3 - (-5)} = -1/2$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-2 - a}{-1} \\cdot (-1/2) = -1，\n解得 a = 0。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "0"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 5,x \\right)$、$B\\left( 4,1 \\right)$與$C\\left( 1,5 \\right)$、$D\\left( 3,6 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "answer": "-1",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{1 - x}{4 - (5)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{6 - (5)}{3 - (1)} = 1/2$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{1 - x}{-1} \\cdot (1/2) = -1，",
      "解得 x = -1。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s8",
      "parameter_signature": "m1=-2:template=3:answer=-1",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 5,x \\right)$、$B\\left( 4,1 \\right)$與$C\\left( 1,5 \\right)$、$D\\left( 3,6 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "correct_answer": "-1",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{1 - x}{4 - (5)}$。\n直線CD的斜率為 $m_{CD} = \\frac{6 - (5)}{3 - (1)} = 1/2$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{1 - x}{-1} \\cdot (1/2) = -1，\n解得 x = -1。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-1"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 4,k \\right)$、$B\\left( 1,-4 \\right)$與$C\\left( -1,3 \\right)$、$D\\left( -3,6 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "-2",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-4 - k}{1 - (4)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{6 - (3)}{-3 - (-1)} = -3/2$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-4 - k}{-3} \\cdot (-3/2) = -1，",
      "解得 k = -2。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m1=2/3:template=3:answer=-2",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 4,k \\right)$、$B\\left( 1,-4 \\right)$與$C\\left( -1,3 \\right)$、$D\\left( -3,6 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "-2",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-4 - k}{1 - (4)}$。\n直線CD的斜率為 $m_{CD} = \\frac{6 - (3)}{-3 - (-1)} = -3/2$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-4 - k}{-3} \\cdot (-3/2) = -1，\n解得 k = -2。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-2"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -2,-5 \\right)$、$B\\left( -1,-3 \\right)$與$C\\left( 5,-3 \\right)$、$D\\left( 3,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "answer": "-2",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-3 - (-5)}{-1 - (-2)} = 2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{x - (-3)}{3 - (5)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$2 \\cdot \\frac{x - (-3)}{-2} = -1$，",
      "解得 x = -2。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s3",
      "parameter_signature": "m1=2:template=1:answer=-2",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -2,-5 \\right)$、$B\\left( -1,-3 \\right)$與$C\\left( 5,-3 \\right)$、$D\\left( 3,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "correct_answer": "-2",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-3 - (-5)}{-1 - (-2)} = 2$。\n直線CD的斜率為 $m_{CD} = \\frac{x - (-3)}{3 - (5)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$2 \\cdot \\frac{x - (-3)}{-2} = -1$，\n解得 x = -2。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-2"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -2,k \\right)$、$B\\left( 0,-5 \\right)$與$C\\left( 1,5 \\right)$、$D\\left( 0,3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "-4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-5 - k}{0 - (-2)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{3 - (5)}{0 - (1)} = 2$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-5 - k}{2} \\cdot (2) = -1，",
      "解得 k = -4。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s2",
      "parameter_signature": "m1=-1/2:template=3:answer=-4",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -2,k \\right)$、$B\\left( 0,-5 \\right)$與$C\\left( 1,5 \\right)$、$D\\left( 0,3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "-4",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-5 - k}{0 - (-2)}$。\n直線CD的斜率為 $m_{CD} = \\frac{3 - (5)}{0 - (1)} = 2$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-5 - k}{2} \\cdot (2) = -1，\n解得 k = -4。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-4"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 4,k \\right)$、$B\\left( 5,-4 \\right)$與$C\\left( -3,4 \\right)$、$D\\left( -6,3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "-1",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-4 - k}{5 - (4)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{3 - (4)}{-6 - (-3)} = 1/3$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-4 - k}{1} \\cdot (1/3) = -1，",
      "解得 k = -1。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s1",
      "parameter_signature": "m1=-3:template=3:answer=-1",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "perpendicular_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 4,k \\right)$、$B\\left( 5,-4 \\right)$與$C\\left( -3,4 \\right)$、$D\\left( -6,3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "-1",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-4 - k}{5 - (4)}$。\n直線CD的斜率為 $m_{CD} = \\frac{3 - (4)}{-6 - (-3)} = 1/3$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：\\frac{-4 - k}{1} \\cdot (1/3) = -1，\n解得 k = -1。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "rational",
      "answer_shape": "scalar",
      "answer_equivalence": "rational_equivalent",
      "checker": "rational_checker",
      "accepted_formats": [
        "-1"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  }
]
```
