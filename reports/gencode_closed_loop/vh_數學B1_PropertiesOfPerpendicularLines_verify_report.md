# Verify Report: vh_數學B1_PropertiesOfPerpendicularLines

- python: C:\Users\Owner\anaconda3\python.exe
- registry: D:\Python\Mathproject_tvet_mathB\configs\generated_registry\b1_section_1_1_verified_registry.v0.1.yaml
- registry_verified_count: 3
- pytest_exit_code: 0
- unique_problem_type_count: 3
- PASS: True

## Runtime ProblemType Coverage
```json
{
  "expected_problem_types": [
    "perpendicular_line_equation",
    "perpendicular_lines_properties",
    "triangle_right_angle_verification"
  ],
  "observed_problem_types": [
    "perpendicular_line_equation",
    "perpendicular_lines_properties",
    "triangle_right_angle_verification"
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
  },
  {
    "problem_type_id": "perpendicular_line_equation",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_2_1/perpendicular_line_equation/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "text_short",
    "checker_type": "exact_string_checker"
  },
  {
    "problem_type_id": "triangle_right_angle_verification",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_2_1/triangle_right_angle_verification/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "choice",
    "checker_type": "choice_label_checker"
  }
]
```

## Pytest Output
```text
.....                                                                    [100%]
5 passed in 0.05s
```

## Samples
```json
[
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 2,-3 \\right)$、$B\\left( 3,-6 \\right)$與$C\\left( 1,4 \\right)$、$D\\left( 4,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "5",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-6 - (-3)}{3 - (2)} = -3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - (4)}{4 - (1)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-3 \\cdot \\frac{a - (4)}{3} = -1$，",
      "解得 a = 5。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s7",
      "parameter_signature": "m1=-3:template=1:answer=5",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(2,-3)",
        "B(3,-6)",
        "C(1,4)",
        "D(4,a)",
        "AB垂直CD"
      ],
      "target": "a",
      "derivation": [
        "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
        "直線AB的斜率為 $m_{AB} = \\frac{-6 - (-3)}{3 - (2)} = -3$。",
        "直線CD的斜率為 $m_{CD} = \\frac{a - (4)}{4 - (1)}$。",
        "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-3 \\cdot \\frac{a - (4)}{3} = -1$，",
        "解得 a = 5。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 2,-3 \\right)$、$B\\left( 3,-6 \\right)$與$C\\left( 1,4 \\right)$、$D\\left( 4,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "5",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-6 - (-3)}{3 - (2)} = -3$。\n直線CD的斜率為 $m_{CD} = \\frac{a - (4)}{4 - (1)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-3 \\cdot \\frac{a - (4)}{3} = -1$，\n解得 a = 5。",
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
    "problem_type_id": "perpendicular_line_equation",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，設直線$L$的方程式為$4x-6y+14=0$。試求通過點$P\\left( 5,-6 \\right)$且與直線$L$垂直的直線方程式。",
    "answer": "3x+2y-3=0",
    "answer_type": "text_short",
    "checker_type": "text_short_checker",
    "solution_steps": [
      "已知與直線 $L: 4x-6y+14=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
      "直線 $L$ 的斜率為 $m = -\\frac{4}{-6} = 2/3$。",
      "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-6}{4} = -3/2$。",
      "利用點斜式，通過點 $P(5,-6)$ 且斜率為 $m'$ 的直線方程式為：",
      "$y - (-6) = \\frac{-6}{4} \\cdot (x - (5))$，",
      "整理化簡為一般式後可得：$3x+2y-3=0$。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_line_equation",
      "scenario_id": "s5",
      "parameter_signature": "a=4:b=-6:c=14:answer=3x+2y-3=0",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_line_equation"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "L: 4x-6y+14=0",
        "P(5,-6)"
      ],
      "target": "perpendicular_line_equation",
      "derivation": [
        "已知與直線 $L: 4x-6y+14=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
        "直線 $L$ 的斜率為 $m = -\\frac{4}{-6} = 2/3$。",
        "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-6}{4} = -3/2$。",
        "利用點斜式，通過點 $P(5,-6)$ 且斜率為 $m'$ 的直線方程式為：",
        "$y - (-6) = \\frac{-6}{4} \\cdot (x - (5))$，",
        "整理化簡為一般式後可得：$3x+2y-3=0$。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，設直線$L$的方程式為$4x-6y+14=0$。試求通過點$P\\left( 5,-6 \\right)$且與直線$L$垂直的直線方程式。",
    "correct_answer": "3x+2y-3=0",
    "explanation": "已知與直線 $L: 4x-6y+14=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。\n直線 $L$ 的斜率為 $m = -\\frac{4}{-6} = 2/3$。\n因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-6}{4} = -3/2$。\n利用點斜式，通過點 $P(5,-6)$ 且斜率為 $m'$ 的直線方程式為：\n$y - (-6) = \\frac{-6}{4} \\cdot (x - (5))$，\n整理化簡為一般式後可得：$3x+2y-3=0$。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "answer_equivalence": "exact_string",
      "checker": "text_short_checker",
      "accepted_formats": [
        "3x+2y-3=0"
      ],
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string"
    }
  },
  {
    "problem_type_id": "triangle_right_angle_verification",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( 1,-2 \\right)$、$B\\left( -2,7 \\right)$、$C\\left( 4,1 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $C$ 處為直角？",
    "answer": "A",
    "answer_type": "choice_label",
    "checker_type": "choice_label_checker",
    "solution_steps": [
      "欲驗證 $\\triangle ABC$ 在頂點 $C$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
      "計算與頂點 $C$ 相連的兩條邊的斜率：",
      "邊段 $AC$ 的斜率 $m_{AC} = \\frac{-3}{-3} = 1$，",
      "邊段 $BC$ 的斜率 $m_{BC} = \\frac{6}{-6} = -1$。",
      "計算兩斜率的乘積：$m_{AC} \\cdot m_{BC} = 1 \\cdot \\left( -1 \\right) = -1$。",
      "因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $C$ 處為直角。答案為「是」。"
    ],
    "metadata": {
      "scenario_family": "triangle_right_angle_verification",
      "scenario_id": "s5",
      "parameter_signature": "A=(1,-2):B=(-2,7):C=(4,1):test=C:answer=A",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_right_angle_verification"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(1,-2)",
        "B(-2,7)",
        "C(4,1)",
        "test_vertex=C"
      ],
      "target": "right_angle_verification",
      "derivation": [
        "欲驗證 $\\triangle ABC$ 在頂點 $C$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
        "計算與頂點 $C$ 相連的兩條邊的斜率：",
        "邊段 $AC$ 的斜率 $m_{AC} = \\frac{-3}{-3} = 1$，",
        "邊段 $BC$ 的斜率 $m_{BC} = \\frac{6}{-6} = -1$。",
        "計算兩斜率的乘積：$m_{AC} \\cdot m_{BC} = 1 \\cdot \\left( -1 \\right) = -1$。",
        "因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $C$ 處為直角。答案為「是」。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( 1,-2 \\right)$、$B\\left( -2,7 \\right)$、$C\\left( 4,1 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $C$ 處為直角？",
    "correct_answer": "A",
    "explanation": "欲驗證 $\\triangle ABC$ 在頂點 $C$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。\n計算與頂點 $C$ 相連的兩條邊的斜率：\n邊段 $AC$ 的斜率 $m_{AC} = \\frac{-3}{-3} = 1$，\n邊段 $BC$ 的斜率 $m_{BC} = \\frac{6}{-6} = -1$。\n計算兩斜率的乘積：$m_{AC} \\cdot m_{BC} = 1 \\cdot \\left( -1 \\right) = -1$。\n因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $C$ 處為直角。答案為「是」。",
    "choices": [
      "是",
      "否"
    ],
    "answer_contract": {
      "choices_required": true,
      "choice_count": 2,
      "correct_choice_count": 1,
      "frontend_render_choices": true,
      "answer_type": "choice",
      "answer_shape": "choice_label",
      "answer_equivalence": "choice_label",
      "checker": "choice_label_checker",
      "accepted_formats": [
        "A"
      ],
      "checker_key": "choice_label_checker",
      "equivalence_type": "choice_label"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -5,x \\right)$、$B\\left( -3,4 \\right)$與$C\\left( -1,-5 \\right)$、$D\\left( -4,-3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "answer": "1",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{4 - x}{-3 - (-5)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-3 - (-5)}{-4 - (-1)} = -2/3$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$\\frac{4 - x}{2} \\cdot (-2/3) = -1$，",
      "解得 x = 1。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s1",
      "parameter_signature": "m1=3/2:template=3:answer=1",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(-5,x)",
        "B(-3,4)",
        "C(-1,-5)",
        "D(-4,-3)",
        "AB垂直CD"
      ],
      "target": "x",
      "derivation": [
        "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
        "直線AB的斜率為 $m_{AB} = \\frac{4 - x}{-3 - (-5)}$。",
        "直線CD的斜率為 $m_{CD} = \\frac{-3 - (-5)}{-4 - (-1)} = -2/3$。",
        "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$\\frac{4 - x}{2} \\cdot (-2/3) = -1$，",
        "解得 x = 1。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -5,x \\right)$、$B\\left( -3,4 \\right)$與$C\\left( -1,-5 \\right)$、$D\\left( -4,-3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "correct_answer": "1",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{4 - x}{-3 - (-5)}$。\n直線CD的斜率為 $m_{CD} = \\frac{-3 - (-5)}{-4 - (-1)} = -2/3$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$\\frac{4 - x}{2} \\cdot (-2/3) = -1$，\n解得 x = 1。",
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
    "problem_type_id": "perpendicular_line_equation",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，設直線$L$的方程式為$6x+6y-14=0$。試求通過點$P\\left( 3,-7 \\right)$且與直線$L$垂直的直線方程式。",
    "answer": "x-y-10=0",
    "answer_type": "text_short",
    "checker_type": "text_short_checker",
    "solution_steps": [
      "已知與直線 $L: 6x+6y-14=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
      "直線 $L$ 的斜率為 $m = -\\frac{6}{6} = -1$。",
      "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{6}{6} = 1$。",
      "利用點斜式，通過點 $P(3,-7)$ 且斜率為 $m'$ 的直線方程式為：",
      "$y - (-7) = \\frac{6}{6} \\cdot (x - (3))$，",
      "整理化簡為一般式後可得：$x-y-10=0$。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_line_equation",
      "scenario_id": "s3",
      "parameter_signature": "a=6:b=6:c=-14:answer=x-y-10=0",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "perpendicular_line_equation"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "L: 6x+6y-14=0",
        "P(3,-7)"
      ],
      "target": "perpendicular_line_equation",
      "derivation": [
        "已知與直線 $L: 6x+6y-14=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
        "直線 $L$ 的斜率為 $m = -\\frac{6}{6} = -1$。",
        "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{6}{6} = 1$。",
        "利用點斜式，通過點 $P(3,-7)$ 且斜率為 $m'$ 的直線方程式為：",
        "$y - (-7) = \\frac{6}{6} \\cdot (x - (3))$，",
        "整理化簡為一般式後可得：$x-y-10=0$。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，設直線$L$的方程式為$6x+6y-14=0$。試求通過點$P\\left( 3,-7 \\right)$且與直線$L$垂直的直線方程式。",
    "correct_answer": "x-y-10=0",
    "explanation": "已知與直線 $L: 6x+6y-14=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。\n直線 $L$ 的斜率為 $m = -\\frac{6}{6} = -1$。\n因此，所求直線 $L'$ 的斜率為 $m' = \\frac{6}{6} = 1$。\n利用點斜式，通過點 $P(3,-7)$ 且斜率為 $m'$ 的直線方程式為：\n$y - (-7) = \\frac{6}{6} \\cdot (x - (3))$，\n整理化簡為一般式後可得：$x-y-10=0$。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "answer_equivalence": "exact_string",
      "checker": "text_short_checker",
      "accepted_formats": [
        "x-y-10=0"
      ],
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string"
    }
  },
  {
    "problem_type_id": "triangle_right_angle_verification",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( 2,-2 \\right)$、$B\\left( 10,-8 \\right)$、$C\\left( -4,-11 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $A$ 處為直角？",
    "answer": "B",
    "answer_type": "choice_label",
    "checker_type": "choice_label_checker",
    "solution_steps": [
      "欲驗證 $\\triangle ABC$ 在頂點 $A$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
      "計算與頂點 $A$ 相連的兩條邊的斜率：",
      "邊段 $AB$ 的斜率 $m_{AB} = \\frac{-6}{8} = -3/4$，",
      "邊段 $AC$ 的斜率 $m_{AC} = \\frac{-9}{-6} = 3/2$。",
      "計算兩斜率的乘積：$m_{AB} \\cdot m_{AC} = -3/4 \\cdot \\left( 3/2 \\right) = -9/8$。",
      "因為斜率乘積為 $-9/8 \\ne -1$，故 $\\triangle ABC$ 在頂點 $A$ 處不為直角。答案為「否」。"
    ],
    "metadata": {
      "scenario_family": "triangle_right_angle_verification",
      "scenario_id": "s3",
      "parameter_signature": "A=(2,-2):B=(10,-8):C=(-4,-11):test=A:answer=B",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_right_angle_verification"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(2,-2)",
        "B(10,-8)",
        "C(-4,-11)",
        "test_vertex=A"
      ],
      "target": "right_angle_verification",
      "derivation": [
        "欲驗證 $\\triangle ABC$ 在頂點 $A$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
        "計算與頂點 $A$ 相連的兩條邊的斜率：",
        "邊段 $AB$ 的斜率 $m_{AB} = \\frac{-6}{8} = -3/4$，",
        "邊段 $AC$ 的斜率 $m_{AC} = \\frac{-9}{-6} = 3/2$。",
        "計算兩斜率的乘積：$m_{AB} \\cdot m_{AC} = -3/4 \\cdot \\left( 3/2 \\right) = -9/8$。",
        "因為斜率乘積為 $-9/8 \\ne -1$，故 $\\triangle ABC$ 在頂點 $A$ 處不為直角。答案為「否」。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( 2,-2 \\right)$、$B\\left( 10,-8 \\right)$、$C\\left( -4,-11 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $A$ 處為直角？",
    "correct_answer": "B",
    "explanation": "欲驗證 $\\triangle ABC$ 在頂點 $A$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。\n計算與頂點 $A$ 相連的兩條邊的斜率：\n邊段 $AB$ 的斜率 $m_{AB} = \\frac{-6}{8} = -3/4$，\n邊段 $AC$ 的斜率 $m_{AC} = \\frac{-9}{-6} = 3/2$。\n計算兩斜率的乘積：$m_{AB} \\cdot m_{AC} = -3/4 \\cdot \\left( 3/2 \\right) = -9/8$。\n因為斜率乘積為 $-9/8 \\ne -1$，故 $\\triangle ABC$ 在頂點 $A$ 處不為直角。答案為「否」。",
    "choices": [
      "是",
      "否"
    ],
    "answer_contract": {
      "choices_required": true,
      "choice_count": 2,
      "correct_choice_count": 1,
      "frontend_render_choices": true,
      "answer_type": "choice",
      "answer_shape": "choice_label",
      "answer_equivalence": "choice_label",
      "checker": "choice_label_checker",
      "accepted_formats": [
        "B"
      ],
      "checker_key": "choice_label_checker",
      "equivalence_type": "choice_label"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 2,-5 \\right)$、$B\\left( 5,-4 \\right)$與$C\\left( -5,-5 \\right)$、$D\\left( -4,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "-8",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-4 - (-5)}{5 - (2)} = 1/3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - (-5)}{-4 - (-5)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$1/3 \\cdot \\frac{a - (-5)}{1} = -1$，",
      "解得 a = -8。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s5",
      "parameter_signature": "m1=1/3:template=1:answer=-8",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(2,-5)",
        "B(5,-4)",
        "C(-5,-5)",
        "D(-4,a)",
        "AB垂直CD"
      ],
      "target": "a",
      "derivation": [
        "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
        "直線AB的斜率為 $m_{AB} = \\frac{-4 - (-5)}{5 - (2)} = 1/3$。",
        "直線CD的斜率為 $m_{CD} = \\frac{a - (-5)}{-4 - (-5)}$。",
        "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$1/3 \\cdot \\frac{a - (-5)}{1} = -1$，",
        "解得 a = -8。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 2,-5 \\right)$、$B\\left( 5,-4 \\right)$與$C\\left( -5,-5 \\right)$、$D\\left( -4,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "-8",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-4 - (-5)}{5 - (2)} = 1/3$。\n直線CD的斜率為 $m_{CD} = \\frac{a - (-5)}{-4 - (-5)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$1/3 \\cdot \\frac{a - (-5)}{1} = -1$，\n解得 a = -8。",
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
        "-8"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_line_equation",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，設直線$L$的方程式為$3x-y-1=0$。試求通過點$P\\left( -5,-1 \\right)$且與直線$L$垂直的直線方程式。",
    "answer": "x+3y+8=0",
    "answer_type": "text_short",
    "checker_type": "text_short_checker",
    "solution_steps": [
      "已知與直線 $L: 3x-y-1=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
      "直線 $L$ 的斜率為 $m = -\\frac{3}{-1} = 3$。",
      "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-1}{3} = -1/3$。",
      "利用點斜式，通過點 $P(-5,-1)$ 且斜率為 $m'$ 的直線方程式為：",
      "$y - (-1) = \\frac{-1}{3} \\cdot (x - (-5))$，",
      "整理化簡為一般式後可得：$x+3y+8=0$。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_line_equation",
      "scenario_id": "s3",
      "parameter_signature": "a=3:b=-1:c=-1:answer=x+3y+8=0",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "perpendicular_line_equation"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "L: 3x-y-1=0",
        "P(-5,-1)"
      ],
      "target": "perpendicular_line_equation",
      "derivation": [
        "已知與直線 $L: 3x-y-1=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
        "直線 $L$ 的斜率為 $m = -\\frac{3}{-1} = 3$。",
        "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-1}{3} = -1/3$。",
        "利用點斜式，通過點 $P(-5,-1)$ 且斜率為 $m'$ 的直線方程式為：",
        "$y - (-1) = \\frac{-1}{3} \\cdot (x - (-5))$，",
        "整理化簡為一般式後可得：$x+3y+8=0$。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，設直線$L$的方程式為$3x-y-1=0$。試求通過點$P\\left( -5,-1 \\right)$且與直線$L$垂直的直線方程式。",
    "correct_answer": "x+3y+8=0",
    "explanation": "已知與直線 $L: 3x-y-1=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。\n直線 $L$ 的斜率為 $m = -\\frac{3}{-1} = 3$。\n因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-1}{3} = -1/3$。\n利用點斜式，通過點 $P(-5,-1)$ 且斜率為 $m'$ 的直線方程式為：\n$y - (-1) = \\frac{-1}{3} \\cdot (x - (-5))$，\n整理化簡為一般式後可得：$x+3y+8=0$。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "answer_equivalence": "exact_string",
      "checker": "text_short_checker",
      "accepted_formats": [
        "x+3y+8=0"
      ],
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string"
    }
  },
  {
    "problem_type_id": "triangle_right_angle_verification",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( 2,0 \\right)$、$B\\left( 1,3 \\right)$、$C\\left( 5,1 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $A$ 處為直角？",
    "answer": "A",
    "answer_type": "choice_label",
    "checker_type": "choice_label_checker",
    "solution_steps": [
      "欲驗證 $\\triangle ABC$ 在頂點 $A$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
      "計算與頂點 $A$ 相連的兩條邊的斜率：",
      "邊段 $AB$ 的斜率 $m_{AB} = \\frac{3}{-1} = -3$，",
      "邊段 $AC$ 的斜率 $m_{AC} = \\frac{1}{3} = 1/3$。",
      "計算兩斜率的乘積：$m_{AB} \\cdot m_{AC} = -3 \\cdot \\left( 1/3 \\right) = -1$。",
      "因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $A$ 處為直角。答案為「是」。"
    ],
    "metadata": {
      "scenario_family": "triangle_right_angle_verification",
      "scenario_id": "s5",
      "parameter_signature": "A=(2,0):B=(1,3):C=(5,1):test=A:answer=A",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_lines_right_angle_verification"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(2,0)",
        "B(1,3)",
        "C(5,1)",
        "test_vertex=A"
      ],
      "target": "right_angle_verification",
      "derivation": [
        "欲驗證 $\\triangle ABC$ 在頂點 $A$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
        "計算與頂點 $A$ 相連的兩條邊的斜率：",
        "邊段 $AB$ 的斜率 $m_{AB} = \\frac{3}{-1} = -3$，",
        "邊段 $AC$ 的斜率 $m_{AC} = \\frac{1}{3} = 1/3$。",
        "計算兩斜率的乘積：$m_{AB} \\cdot m_{AC} = -3 \\cdot \\left( 1/3 \\right) = -1$。",
        "因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $A$ 處為直角。答案為「是」。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( 2,0 \\right)$、$B\\left( 1,3 \\right)$、$C\\left( 5,1 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $A$ 處為直角？",
    "correct_answer": "A",
    "explanation": "欲驗證 $\\triangle ABC$ 在頂點 $A$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。\n計算與頂點 $A$ 相連的兩條邊的斜率：\n邊段 $AB$ 的斜率 $m_{AB} = \\frac{3}{-1} = -3$，\n邊段 $AC$ 的斜率 $m_{AC} = \\frac{1}{3} = 1/3$。\n計算兩斜率的乘積：$m_{AB} \\cdot m_{AC} = -3 \\cdot \\left( 1/3 \\right) = -1$。\n因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $A$ 處為直角。答案為「是」。",
    "choices": [
      "是",
      "否"
    ],
    "answer_contract": {
      "choices_required": true,
      "choice_count": 2,
      "correct_choice_count": 1,
      "frontend_render_choices": true,
      "answer_type": "choice",
      "answer_shape": "choice_label",
      "answer_equivalence": "choice_label",
      "checker": "choice_label_checker",
      "accepted_formats": [
        "A"
      ],
      "checker_key": "choice_label_checker",
      "equivalence_type": "choice_label"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 2,4 \\right)$、$B\\left( 0,5 \\right)$與$C\\left( 3,-3 \\right)$、$D\\left( x,-1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "answer": "4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{5 - (4)}{0 - (2)} = -1/2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-1 - (-3)}{x - (3)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/2 \\cdot \\frac{2}{x - (3)} = -1$，",
      "解得 x = 4。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s2",
      "parameter_signature": "m1=-1/2:template=2:answer=4",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(2,4)",
        "B(0,5)",
        "C(3,-3)",
        "D(x,-1)",
        "AB垂直CD"
      ],
      "target": "x",
      "derivation": [
        "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
        "直線AB的斜率為 $m_{AB} = \\frac{5 - (4)}{0 - (2)} = -1/2$。",
        "直線CD的斜率為 $m_{CD} = \\frac{-1 - (-3)}{x - (3)}$。",
        "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/2 \\cdot \\frac{2}{x - (3)} = -1$，",
        "解得 x = 4。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 2,4 \\right)$、$B\\left( 0,5 \\right)$與$C\\left( 3,-3 \\right)$、$D\\left( x,-1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "correct_answer": "4",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{5 - (4)}{0 - (2)} = -1/2$。\n直線CD的斜率為 $m_{CD} = \\frac{-1 - (-3)}{x - (3)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/2 \\cdot \\frac{2}{x - (3)} = -1$，\n解得 x = 4。",
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
    "problem_type_id": "perpendicular_line_equation",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，設直線$L$的方程式為$-2x+2y-14=0$。試求通過點$P\\left( -2,4 \\right)$且與直線$L$垂直的直線方程式。",
    "answer": "x+y-2=0",
    "answer_type": "text_short",
    "checker_type": "text_short_checker",
    "solution_steps": [
      "已知與直線 $L: -2x+2y-14=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
      "直線 $L$ 的斜率為 $m = -\\frac{-2}{2} = 1$。",
      "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{2}{-2} = -1$。",
      "利用點斜式，通過點 $P(-2,4)$ 且斜率為 $m'$ 的直線方程式為：",
      "$y - (4) = \\frac{2}{-2} \\cdot (x - (-2))$，",
      "整理化簡為一般式後可得：$x+y-2=0$。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_line_equation",
      "scenario_id": "s7",
      "parameter_signature": "a=-2:b=2:c=-14:answer=x+y-2=0",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_line_equation"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "L: -2x+2y-14=0",
        "P(-2,4)"
      ],
      "target": "perpendicular_line_equation",
      "derivation": [
        "已知與直線 $L: -2x+2y-14=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
        "直線 $L$ 的斜率為 $m = -\\frac{-2}{2} = 1$。",
        "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{2}{-2} = -1$。",
        "利用點斜式，通過點 $P(-2,4)$ 且斜率為 $m'$ 的直線方程式為：",
        "$y - (4) = \\frac{2}{-2} \\cdot (x - (-2))$，",
        "整理化簡為一般式後可得：$x+y-2=0$。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，設直線$L$的方程式為$-2x+2y-14=0$。試求通過點$P\\left( -2,4 \\right)$且與直線$L$垂直的直線方程式。",
    "correct_answer": "x+y-2=0",
    "explanation": "已知與直線 $L: -2x+2y-14=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。\n直線 $L$ 的斜率為 $m = -\\frac{-2}{2} = 1$。\n因此，所求直線 $L'$ 的斜率為 $m' = \\frac{2}{-2} = -1$。\n利用點斜式，通過點 $P(-2,4)$ 且斜率為 $m'$ 的直線方程式為：\n$y - (4) = \\frac{2}{-2} \\cdot (x - (-2))$，\n整理化簡為一般式後可得：$x+y-2=0$。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "answer_equivalence": "exact_string",
      "checker": "text_short_checker",
      "accepted_formats": [
        "x+y-2=0"
      ],
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string"
    }
  },
  {
    "problem_type_id": "triangle_right_angle_verification",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( 13,-4 \\right)$、$B\\left( 3,-11 \\right)$、$C\\left( 5,-2 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $C$ 處為直角？",
    "answer": "B",
    "answer_type": "choice_label",
    "checker_type": "choice_label_checker",
    "solution_steps": [
      "欲驗證 $\\triangle ABC$ 在頂點 $C$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
      "計算與頂點 $C$ 相連的兩條邊的斜率：",
      "邊段 $AC$ 的斜率 $m_{AC} = \\frac{-2}{8} = -1/4$，",
      "邊段 $BC$ 的斜率 $m_{BC} = \\frac{-9}{-2} = 9/2$。",
      "計算兩斜率的乘積：$m_{AC} \\cdot m_{BC} = -1/4 \\cdot \\left( 9/2 \\right) = -9/8$。",
      "因為斜率乘積為 $-9/8 \\ne -1$，故 $\\triangle ABC$ 在頂點 $C$ 處不為直角。答案為「否」。"
    ],
    "metadata": {
      "scenario_family": "triangle_right_angle_verification",
      "scenario_id": "s2",
      "parameter_signature": "A=(13,-4):B=(3,-11):C=(5,-2):test=C:answer=B",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "perpendicular_lines_right_angle_verification"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(13,-4)",
        "B(3,-11)",
        "C(5,-2)",
        "test_vertex=C"
      ],
      "target": "right_angle_verification",
      "derivation": [
        "欲驗證 $\\triangle ABC$ 在頂點 $C$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
        "計算與頂點 $C$ 相連的兩條邊的斜率：",
        "邊段 $AC$ 的斜率 $m_{AC} = \\frac{-2}{8} = -1/4$，",
        "邊段 $BC$ 的斜率 $m_{BC} = \\frac{-9}{-2} = 9/2$。",
        "計算兩斜率的乘積：$m_{AC} \\cdot m_{BC} = -1/4 \\cdot \\left( 9/2 \\right) = -9/8$。",
        "因為斜率乘積為 $-9/8 \\ne -1$，故 $\\triangle ABC$ 在頂點 $C$ 處不為直角。答案為「否」。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( 13,-4 \\right)$、$B\\left( 3,-11 \\right)$、$C\\left( 5,-2 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $C$ 處為直角？",
    "correct_answer": "B",
    "explanation": "欲驗證 $\\triangle ABC$ 在頂點 $C$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。\n計算與頂點 $C$ 相連的兩條邊的斜率：\n邊段 $AC$ 的斜率 $m_{AC} = \\frac{-2}{8} = -1/4$，\n邊段 $BC$ 的斜率 $m_{BC} = \\frac{-9}{-2} = 9/2$。\n計算兩斜率的乘積：$m_{AC} \\cdot m_{BC} = -1/4 \\cdot \\left( 9/2 \\right) = -9/8$。\n因為斜率乘積為 $-9/8 \\ne -1$，故 $\\triangle ABC$ 在頂點 $C$ 處不為直角。答案為「否」。",
    "choices": [
      "是",
      "否"
    ],
    "answer_contract": {
      "choices_required": true,
      "choice_count": 2,
      "correct_choice_count": 1,
      "frontend_render_choices": true,
      "answer_type": "choice",
      "answer_shape": "choice_label",
      "answer_equivalence": "choice_label",
      "checker": "choice_label_checker",
      "accepted_formats": [
        "B"
      ],
      "checker_key": "choice_label_checker",
      "equivalence_type": "choice_label"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -5,-2 \\right)$、$B\\left( -4,-1 \\right)$與$C\\left( -2,-2 \\right)$、$D\\left( -1,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "-3",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-1 - (-2)}{-4 - (-5)} = 1$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - (-2)}{-1 - (-2)}$。",
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
      "givens": [
        "A(-5,-2)",
        "B(-4,-1)",
        "C(-2,-2)",
        "D(-1,a)",
        "AB垂直CD"
      ],
      "target": "a",
      "derivation": [
        "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
        "直線AB的斜率為 $m_{AB} = \\frac{-1 - (-2)}{-4 - (-5)} = 1$。",
        "直線CD的斜率為 $m_{CD} = \\frac{a - (-2)}{-1 - (-2)}$。",
        "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$1 \\cdot \\frac{a - (-2)}{1} = -1$，",
        "解得 a = -3。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -5,-2 \\right)$、$B\\left( -4,-1 \\right)$與$C\\left( -2,-2 \\right)$、$D\\left( -1,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "-3",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-1 - (-2)}{-4 - (-5)} = 1$。\n直線CD的斜率為 $m_{CD} = \\frac{a - (-2)}{-1 - (-2)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$1 \\cdot \\frac{a - (-2)}{1} = -1$，\n解得 a = -3。",
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
    "problem_type_id": "perpendicular_line_equation",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，設直線$L$的方程式為$-3x+5y+1=0$。試求通過點$P\\left( -8,8 \\right)$且與直線$L$垂直的直線方程式。",
    "answer": "5x+3y+16=0",
    "answer_type": "text_short",
    "checker_type": "text_short_checker",
    "solution_steps": [
      "已知與直線 $L: -3x+5y+1=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
      "直線 $L$ 的斜率為 $m = -\\frac{-3}{5} = 3/5$。",
      "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{5}{-3} = -5/3$。",
      "利用點斜式，通過點 $P(-8,8)$ 且斜率為 $m'$ 的直線方程式為：",
      "$y - (8) = \\frac{5}{-3} \\cdot (x - (-8))$，",
      "整理化簡為一般式後可得：$5x+3y+16=0$。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_line_equation",
      "scenario_id": "s2",
      "parameter_signature": "a=-3:b=5:c=1:answer=5x+3y+16=0",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_line_equation"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "L: -3x+5y+1=0",
        "P(-8,8)"
      ],
      "target": "perpendicular_line_equation",
      "derivation": [
        "已知與直線 $L: -3x+5y+1=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
        "直線 $L$ 的斜率為 $m = -\\frac{-3}{5} = 3/5$。",
        "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{5}{-3} = -5/3$。",
        "利用點斜式，通過點 $P(-8,8)$ 且斜率為 $m'$ 的直線方程式為：",
        "$y - (8) = \\frac{5}{-3} \\cdot (x - (-8))$，",
        "整理化簡為一般式後可得：$5x+3y+16=0$。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，設直線$L$的方程式為$-3x+5y+1=0$。試求通過點$P\\left( -8,8 \\right)$且與直線$L$垂直的直線方程式。",
    "correct_answer": "5x+3y+16=0",
    "explanation": "已知與直線 $L: -3x+5y+1=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。\n直線 $L$ 的斜率為 $m = -\\frac{-3}{5} = 3/5$。\n因此，所求直線 $L'$ 的斜率為 $m' = \\frac{5}{-3} = -5/3$。\n利用點斜式，通過點 $P(-8,8)$ 且斜率為 $m'$ 的直線方程式為：\n$y - (8) = \\frac{5}{-3} \\cdot (x - (-8))$，\n整理化簡為一般式後可得：$5x+3y+16=0$。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "answer_equivalence": "exact_string",
      "checker": "text_short_checker",
      "accepted_formats": [
        "5x+3y+16=0"
      ],
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string"
    }
  },
  {
    "problem_type_id": "triangle_right_angle_verification",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( -3,5 \\right)$、$B\\left( -5,11 \\right)$、$C\\left( 3,6 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $A$ 處為直角？",
    "answer": "B",
    "answer_type": "choice_label",
    "checker_type": "choice_label_checker",
    "solution_steps": [
      "欲驗證 $\\triangle ABC$ 在頂點 $A$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
      "計算與頂點 $A$ 相連的兩條邊的斜率：",
      "邊段 $AB$ 的斜率 $m_{AB} = \\frac{6}{-2} = -3$，",
      "邊段 $AC$ 的斜率 $m_{AC} = \\frac{1}{6} = 1/6$。",
      "計算兩斜率的乘積：$m_{AB} \\cdot m_{AC} = -3 \\cdot \\left( 1/6 \\right) = -1/2$。",
      "因為斜率乘積為 $-1/2 \\ne -1$，故 $\\triangle ABC$ 在頂點 $A$ 處不為直角。答案為「否」。"
    ],
    "metadata": {
      "scenario_family": "triangle_right_angle_verification",
      "scenario_id": "s1",
      "parameter_signature": "A=(-3,5):B=(-5,11):C=(3,6):test=A:answer=B",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "perpendicular_lines_right_angle_verification"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(-3,5)",
        "B(-5,11)",
        "C(3,6)",
        "test_vertex=A"
      ],
      "target": "right_angle_verification",
      "derivation": [
        "欲驗證 $\\triangle ABC$ 在頂點 $A$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
        "計算與頂點 $A$ 相連的兩條邊的斜率：",
        "邊段 $AB$ 的斜率 $m_{AB} = \\frac{6}{-2} = -3$，",
        "邊段 $AC$ 的斜率 $m_{AC} = \\frac{1}{6} = 1/6$。",
        "計算兩斜率的乘積：$m_{AB} \\cdot m_{AC} = -3 \\cdot \\left( 1/6 \\right) = -1/2$。",
        "因為斜率乘積為 $-1/2 \\ne -1$，故 $\\triangle ABC$ 在頂點 $A$ 處不為直角。答案為「否」。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( -3,5 \\right)$、$B\\left( -5,11 \\right)$、$C\\left( 3,6 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $A$ 處為直角？",
    "correct_answer": "B",
    "explanation": "欲驗證 $\\triangle ABC$ 在頂點 $A$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。\n計算與頂點 $A$ 相連的兩條邊的斜率：\n邊段 $AB$ 的斜率 $m_{AB} = \\frac{6}{-2} = -3$，\n邊段 $AC$ 的斜率 $m_{AC} = \\frac{1}{6} = 1/6$。\n計算兩斜率的乘積：$m_{AB} \\cdot m_{AC} = -3 \\cdot \\left( 1/6 \\right) = -1/2$。\n因為斜率乘積為 $-1/2 \\ne -1$，故 $\\triangle ABC$ 在頂點 $A$ 處不為直角。答案為「否」。",
    "choices": [
      "是",
      "否"
    ],
    "answer_contract": {
      "choices_required": true,
      "choice_count": 2,
      "correct_choice_count": 1,
      "frontend_render_choices": true,
      "answer_type": "choice",
      "answer_shape": "choice_label",
      "answer_equivalence": "choice_label",
      "checker": "choice_label_checker",
      "accepted_formats": [
        "B"
      ],
      "checker_key": "choice_label_checker",
      "equivalence_type": "choice_label"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -3,2 \\right)$、$B\\left( 0,1 \\right)$與$C\\left( -4,5 \\right)$、$D\\left( a,8 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "-3",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{1 - (2)}{0 - (-3)} = -1/3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{8 - (5)}{a - (-4)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/3 \\cdot \\frac{3}{a - (-4)} = -1$，",
      "解得 a = -3。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s5",
      "parameter_signature": "m1=-1/3:template=2:answer=-3",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(-3,2)",
        "B(0,1)",
        "C(-4,5)",
        "D(a,8)",
        "AB垂直CD"
      ],
      "target": "a",
      "derivation": [
        "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
        "直線AB的斜率為 $m_{AB} = \\frac{1 - (2)}{0 - (-3)} = -1/3$。",
        "直線CD的斜率為 $m_{CD} = \\frac{8 - (5)}{a - (-4)}$。",
        "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/3 \\cdot \\frac{3}{a - (-4)} = -1$，",
        "解得 a = -3。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -3,2 \\right)$、$B\\left( 0,1 \\right)$與$C\\left( -4,5 \\right)$、$D\\left( a,8 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "-3",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{1 - (2)}{0 - (-3)} = -1/3$。\n直線CD的斜率為 $m_{CD} = \\frac{8 - (5)}{a - (-4)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/3 \\cdot \\frac{3}{a - (-4)} = -1$，\n解得 a = -3。",
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
    "problem_type_id": "perpendicular_line_equation",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，設直線$L$的方程式為$4x+3y-3=0$。試求通過點$P\\left( 6,-5 \\right)$且與直線$L$垂直的直線方程式。",
    "answer": "3x-4y-38=0",
    "answer_type": "text_short",
    "checker_type": "text_short_checker",
    "solution_steps": [
      "已知與直線 $L: 4x+3y-3=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
      "直線 $L$ 的斜率為 $m = -\\frac{4}{3} = -4/3$。",
      "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{3}{4} = 3/4$。",
      "利用點斜式，通過點 $P(6,-5)$ 且斜率為 $m'$ 的直線方程式為：",
      "$y - (-5) = \\frac{3}{4} \\cdot (x - (6))$，",
      "整理化簡為一般式後可得：$3x-4y-38=0$。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_line_equation",
      "scenario_id": "s4",
      "parameter_signature": "a=4:b=3:c=-3:answer=3x-4y-38=0",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "perpendicular_line_equation"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "L: 4x+3y-3=0",
        "P(6,-5)"
      ],
      "target": "perpendicular_line_equation",
      "derivation": [
        "已知與直線 $L: 4x+3y-3=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
        "直線 $L$ 的斜率為 $m = -\\frac{4}{3} = -4/3$。",
        "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{3}{4} = 3/4$。",
        "利用點斜式，通過點 $P(6,-5)$ 且斜率為 $m'$ 的直線方程式為：",
        "$y - (-5) = \\frac{3}{4} \\cdot (x - (6))$，",
        "整理化簡為一般式後可得：$3x-4y-38=0$。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，設直線$L$的方程式為$4x+3y-3=0$。試求通過點$P\\left( 6,-5 \\right)$且與直線$L$垂直的直線方程式。",
    "correct_answer": "3x-4y-38=0",
    "explanation": "已知與直線 $L: 4x+3y-3=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。\n直線 $L$ 的斜率為 $m = -\\frac{4}{3} = -4/3$。\n因此，所求直線 $L'$ 的斜率為 $m' = \\frac{3}{4} = 3/4$。\n利用點斜式，通過點 $P(6,-5)$ 且斜率為 $m'$ 的直線方程式為：\n$y - (-5) = \\frac{3}{4} \\cdot (x - (6))$，\n整理化簡為一般式後可得：$3x-4y-38=0$。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "answer_equivalence": "exact_string",
      "checker": "text_short_checker",
      "accepted_formats": [
        "3x-4y-38=0"
      ],
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string"
    }
  },
  {
    "problem_type_id": "triangle_right_angle_verification",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( 5,-5 \\right)$、$B\\left( 3,3 \\right)$、$C\\left( 7,4 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $B$ 處為直角？",
    "answer": "A",
    "answer_type": "choice_label",
    "checker_type": "choice_label_checker",
    "solution_steps": [
      "欲驗證 $\\triangle ABC$ 在頂點 $B$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
      "計算與頂點 $B$ 相連的兩條邊的斜率：",
      "邊段 $AB$ 的斜率 $m_{AB} = \\frac{-8}{2} = -4$，",
      "邊段 $BC$ 的斜率 $m_{BC} = \\frac{1}{4} = 1/4$。",
      "計算兩斜率的乘積：$m_{AB} \\cdot m_{BC} = -4 \\cdot \\left( 1/4 \\right) = -1$。",
      "因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $B$ 處為直角。答案為「是」。"
    ],
    "metadata": {
      "scenario_family": "triangle_right_angle_verification",
      "scenario_id": "s7",
      "parameter_signature": "A=(5,-5):B=(3,3):C=(7,4):test=B:answer=A",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_right_angle_verification"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(5,-5)",
        "B(3,3)",
        "C(7,4)",
        "test_vertex=B"
      ],
      "target": "right_angle_verification",
      "derivation": [
        "欲驗證 $\\triangle ABC$ 在頂點 $B$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
        "計算與頂點 $B$ 相連的兩條邊的斜率：",
        "邊段 $AB$ 的斜率 $m_{AB} = \\frac{-8}{2} = -4$，",
        "邊段 $BC$ 的斜率 $m_{BC} = \\frac{1}{4} = 1/4$。",
        "計算兩斜率的乘積：$m_{AB} \\cdot m_{BC} = -4 \\cdot \\left( 1/4 \\right) = -1$。",
        "因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $B$ 處為直角。答案為「是」。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( 5,-5 \\right)$、$B\\left( 3,3 \\right)$、$C\\left( 7,4 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $B$ 處為直角？",
    "correct_answer": "A",
    "explanation": "欲驗證 $\\triangle ABC$ 在頂點 $B$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。\n計算與頂點 $B$ 相連的兩條邊的斜率：\n邊段 $AB$ 的斜率 $m_{AB} = \\frac{-8}{2} = -4$，\n邊段 $BC$ 的斜率 $m_{BC} = \\frac{1}{4} = 1/4$。\n計算兩斜率的乘積：$m_{AB} \\cdot m_{BC} = -4 \\cdot \\left( 1/4 \\right) = -1$。\n因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $B$ 處為直角。答案為「是」。",
    "choices": [
      "是",
      "否"
    ],
    "answer_contract": {
      "choices_required": true,
      "choice_count": 2,
      "correct_choice_count": 1,
      "frontend_render_choices": true,
      "answer_type": "choice",
      "answer_shape": "choice_label",
      "answer_equivalence": "choice_label",
      "checker": "choice_label_checker",
      "accepted_formats": [
        "A"
      ],
      "checker_key": "choice_label_checker",
      "equivalence_type": "choice_label"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -2,3 \\right)$、$B\\left( -4,4 \\right)$與$C\\left( -3,0 \\right)$、$D\\left( a,2 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "-2",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{4 - (3)}{-4 - (-2)} = -1/2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{2 - (0)}{a - (-3)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/2 \\cdot \\frac{2}{a - (-3)} = -1$，",
      "解得 a = -2。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m1=-1/2:template=2:answer=-2",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(-2,3)",
        "B(-4,4)",
        "C(-3,0)",
        "D(a,2)",
        "AB垂直CD"
      ],
      "target": "a",
      "derivation": [
        "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
        "直線AB的斜率為 $m_{AB} = \\frac{4 - (3)}{-4 - (-2)} = -1/2$。",
        "直線CD的斜率為 $m_{CD} = \\frac{2 - (0)}{a - (-3)}$。",
        "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/2 \\cdot \\frac{2}{a - (-3)} = -1$，",
        "解得 a = -2。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -2,3 \\right)$、$B\\left( -4,4 \\right)$與$C\\left( -3,0 \\right)$、$D\\left( a,2 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "-2",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{4 - (3)}{-4 - (-2)} = -1/2$。\n直線CD的斜率為 $m_{CD} = \\frac{2 - (0)}{a - (-3)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-1/2 \\cdot \\frac{2}{a - (-3)} = -1$，\n解得 a = -2。",
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
    "problem_type_id": "perpendicular_line_equation",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，設直線$L$的方程式為$-5x+3y+2=0$。試求通過點$P\\left( -6,8 \\right)$且與直線$L$垂直的直線方程式。",
    "answer": "3x+5y-22=0",
    "answer_type": "text_short",
    "checker_type": "text_short_checker",
    "solution_steps": [
      "已知與直線 $L: -5x+3y+2=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
      "直線 $L$ 的斜率為 $m = -\\frac{-5}{3} = 5/3$。",
      "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{3}{-5} = -3/5$。",
      "利用點斜式，通過點 $P(-6,8)$ 且斜率為 $m'$ 的直線方程式為：",
      "$y - (8) = \\frac{3}{-5} \\cdot (x - (-6))$，",
      "整理化簡為一般式後可得：$3x+5y-22=0$。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_line_equation",
      "scenario_id": "s9",
      "parameter_signature": "a=-5:b=3:c=2:answer=3x+5y-22=0",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_line_equation"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "L: -5x+3y+2=0",
        "P(-6,8)"
      ],
      "target": "perpendicular_line_equation",
      "derivation": [
        "已知與直線 $L: -5x+3y+2=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
        "直線 $L$ 的斜率為 $m = -\\frac{-5}{3} = 5/3$。",
        "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{3}{-5} = -3/5$。",
        "利用點斜式，通過點 $P(-6,8)$ 且斜率為 $m'$ 的直線方程式為：",
        "$y - (8) = \\frac{3}{-5} \\cdot (x - (-6))$，",
        "整理化簡為一般式後可得：$3x+5y-22=0$。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，設直線$L$的方程式為$-5x+3y+2=0$。試求通過點$P\\left( -6,8 \\right)$且與直線$L$垂直的直線方程式。",
    "correct_answer": "3x+5y-22=0",
    "explanation": "已知與直線 $L: -5x+3y+2=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。\n直線 $L$ 的斜率為 $m = -\\frac{-5}{3} = 5/3$。\n因此，所求直線 $L'$ 的斜率為 $m' = \\frac{3}{-5} = -3/5$。\n利用點斜式，通過點 $P(-6,8)$ 且斜率為 $m'$ 的直線方程式為：\n$y - (8) = \\frac{3}{-5} \\cdot (x - (-6))$，\n整理化簡為一般式後可得：$3x+5y-22=0$。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "answer_equivalence": "exact_string",
      "checker": "text_short_checker",
      "accepted_formats": [
        "3x+5y-22=0"
      ],
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string"
    }
  },
  {
    "problem_type_id": "triangle_right_angle_verification",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( -5,5 \\right)$、$B\\left( -11,13 \\right)$、$C\\left( -9,2 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $A$ 處為直角？",
    "answer": "A",
    "answer_type": "choice_label",
    "checker_type": "choice_label_checker",
    "solution_steps": [
      "欲驗證 $\\triangle ABC$ 在頂點 $A$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
      "計算與頂點 $A$ 相連的兩條邊的斜率：",
      "邊段 $AB$ 的斜率 $m_{AB} = \\frac{8}{-6} = -4/3$，",
      "邊段 $AC$ 的斜率 $m_{AC} = \\frac{-3}{-4} = 3/4$。",
      "計算兩斜率的乘積：$m_{AB} \\cdot m_{AC} = -4/3 \\cdot \\left( 3/4 \\right) = -1$。",
      "因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $A$ 處為直角。答案為「是」。"
    ],
    "metadata": {
      "scenario_family": "triangle_right_angle_verification",
      "scenario_id": "s3",
      "parameter_signature": "A=(-5,5):B=(-11,13):C=(-9,2):test=A:answer=A",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_lines_right_angle_verification"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(-5,5)",
        "B(-11,13)",
        "C(-9,2)",
        "test_vertex=A"
      ],
      "target": "right_angle_verification",
      "derivation": [
        "欲驗證 $\\triangle ABC$ 在頂點 $A$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
        "計算與頂點 $A$ 相連的兩條邊的斜率：",
        "邊段 $AB$ 的斜率 $m_{AB} = \\frac{8}{-6} = -4/3$，",
        "邊段 $AC$ 的斜率 $m_{AC} = \\frac{-3}{-4} = 3/4$。",
        "計算兩斜率的乘積：$m_{AB} \\cdot m_{AC} = -4/3 \\cdot \\left( 3/4 \\right) = -1$。",
        "因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $A$ 處為直角。答案為「是」。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( -5,5 \\right)$、$B\\left( -11,13 \\right)$、$C\\left( -9,2 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $A$ 處為直角？",
    "correct_answer": "A",
    "explanation": "欲驗證 $\\triangle ABC$ 在頂點 $A$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。\n計算與頂點 $A$ 相連的兩條邊的斜率：\n邊段 $AB$ 的斜率 $m_{AB} = \\frac{8}{-6} = -4/3$，\n邊段 $AC$ 的斜率 $m_{AC} = \\frac{-3}{-4} = 3/4$。\n計算兩斜率的乘積：$m_{AB} \\cdot m_{AC} = -4/3 \\cdot \\left( 3/4 \\right) = -1$。\n因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $A$ 處為直角。答案為「是」。",
    "choices": [
      "是",
      "否"
    ],
    "answer_contract": {
      "choices_required": true,
      "choice_count": 2,
      "correct_choice_count": 1,
      "frontend_render_choices": true,
      "answer_type": "choice",
      "answer_shape": "choice_label",
      "answer_equivalence": "choice_label",
      "checker": "choice_label_checker",
      "accepted_formats": [
        "A"
      ],
      "checker_key": "choice_label_checker",
      "equivalence_type": "choice_label"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -5,5 \\right)$、$B\\left( -4,8 \\right)$與$C\\left( 0,-1 \\right)$、$D\\left( a,-2 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "answer": "3",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{8 - (5)}{-4 - (-5)} = 3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-2 - (-1)}{a - (0)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$3 \\cdot \\frac{-1}{a - (0)} = -1$，",
      "解得 a = 3。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s3",
      "parameter_signature": "m1=3:template=2:answer=3",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(-5,5)",
        "B(-4,8)",
        "C(0,-1)",
        "D(a,-2)",
        "AB垂直CD"
      ],
      "target": "a",
      "derivation": [
        "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
        "直線AB的斜率為 $m_{AB} = \\frac{8 - (5)}{-4 - (-5)} = 3$。",
        "直線CD的斜率為 $m_{CD} = \\frac{-2 - (-1)}{a - (0)}$。",
        "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$3 \\cdot \\frac{-1}{a - (0)} = -1$，",
        "解得 a = 3。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -5,5 \\right)$、$B\\left( -4,8 \\right)$與$C\\left( 0,-1 \\right)$、$D\\left( a,-2 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": "3",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{8 - (5)}{-4 - (-5)} = 3$。\n直線CD的斜率為 $m_{CD} = \\frac{-2 - (-1)}{a - (0)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$3 \\cdot \\frac{-1}{a - (0)} = -1$，\n解得 a = 3。",
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
        "3"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_line_equation",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，設直線$L$的方程式為$-6x-4y-6=0$。試求通過點$P\\left( 4,0 \\right)$且與直線$L$垂直的直線方程式。",
    "answer": "2x-3y-8=0",
    "answer_type": "text_short",
    "checker_type": "text_short_checker",
    "solution_steps": [
      "已知與直線 $L: -6x-4y-6=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
      "直線 $L$ 的斜率為 $m = -\\frac{-6}{-4} = -3/2$。",
      "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-4}{-6} = 2/3$。",
      "利用點斜式，通過點 $P(4,0)$ 且斜率為 $m'$ 的直線方程式為：",
      "$y - (0) = \\frac{-4}{-6} \\cdot (x - (4))$，",
      "整理化簡為一般式後可得：$2x-3y-8=0$。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_line_equation",
      "scenario_id": "s6",
      "parameter_signature": "a=-6:b=-4:c=-6:answer=2x-3y-8=0",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "perpendicular_line_equation"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "L: -6x-4y-6=0",
        "P(4,0)"
      ],
      "target": "perpendicular_line_equation",
      "derivation": [
        "已知與直線 $L: -6x-4y-6=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
        "直線 $L$ 的斜率為 $m = -\\frac{-6}{-4} = -3/2$。",
        "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-4}{-6} = 2/3$。",
        "利用點斜式，通過點 $P(4,0)$ 且斜率為 $m'$ 的直線方程式為：",
        "$y - (0) = \\frac{-4}{-6} \\cdot (x - (4))$，",
        "整理化簡為一般式後可得：$2x-3y-8=0$。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，設直線$L$的方程式為$-6x-4y-6=0$。試求通過點$P\\left( 4,0 \\right)$且與直線$L$垂直的直線方程式。",
    "correct_answer": "2x-3y-8=0",
    "explanation": "已知與直線 $L: -6x-4y-6=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。\n直線 $L$ 的斜率為 $m = -\\frac{-6}{-4} = -3/2$。\n因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-4}{-6} = 2/3$。\n利用點斜式，通過點 $P(4,0)$ 且斜率為 $m'$ 的直線方程式為：\n$y - (0) = \\frac{-4}{-6} \\cdot (x - (4))$，\n整理化簡為一般式後可得：$2x-3y-8=0$。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "answer_equivalence": "exact_string",
      "checker": "text_short_checker",
      "accepted_formats": [
        "2x-3y-8=0"
      ],
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string"
    }
  },
  {
    "problem_type_id": "triangle_right_angle_verification",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( -2,4 \\right)$、$B\\left( -3,-3 \\right)$、$C\\left( -5,2 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $C$ 處為直角？",
    "answer": "B",
    "answer_type": "choice_label",
    "checker_type": "choice_label_checker",
    "solution_steps": [
      "欲驗證 $\\triangle ABC$ 在頂點 $C$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
      "計算與頂點 $C$ 相連的兩條邊的斜率：",
      "邊段 $AC$ 的斜率 $m_{AC} = \\frac{2}{3} = 2/3$，",
      "邊段 $BC$ 的斜率 $m_{BC} = \\frac{-5}{2} = -5/2$。",
      "計算兩斜率的乘積：$m_{AC} \\cdot m_{BC} = 2/3 \\cdot \\left( -5/2 \\right) = -5/3$。",
      "因為斜率乘積為 $-5/3 \\ne -1$，故 $\\triangle ABC$ 在頂點 $C$ 處不為直角。答案為「否」。"
    ],
    "metadata": {
      "scenario_family": "triangle_right_angle_verification",
      "scenario_id": "s8",
      "parameter_signature": "A=(-2,4):B=(-3,-3):C=(-5,2):test=C:answer=B",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_lines_right_angle_verification"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(-2,4)",
        "B(-3,-3)",
        "C(-5,2)",
        "test_vertex=C"
      ],
      "target": "right_angle_verification",
      "derivation": [
        "欲驗證 $\\triangle ABC$ 在頂點 $C$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
        "計算與頂點 $C$ 相連的兩條邊的斜率：",
        "邊段 $AC$ 的斜率 $m_{AC} = \\frac{2}{3} = 2/3$，",
        "邊段 $BC$ 的斜率 $m_{BC} = \\frac{-5}{2} = -5/2$。",
        "計算兩斜率的乘積：$m_{AC} \\cdot m_{BC} = 2/3 \\cdot \\left( -5/2 \\right) = -5/3$。",
        "因為斜率乘積為 $-5/3 \\ne -1$，故 $\\triangle ABC$ 在頂點 $C$ 處不為直角。答案為「否」。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( -2,4 \\right)$、$B\\left( -3,-3 \\right)$、$C\\left( -5,2 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $C$ 處為直角？",
    "correct_answer": "B",
    "explanation": "欲驗證 $\\triangle ABC$ 在頂點 $C$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。\n計算與頂點 $C$ 相連的兩條邊的斜率：\n邊段 $AC$ 的斜率 $m_{AC} = \\frac{2}{3} = 2/3$，\n邊段 $BC$ 的斜率 $m_{BC} = \\frac{-5}{2} = -5/2$。\n計算兩斜率的乘積：$m_{AC} \\cdot m_{BC} = 2/3 \\cdot \\left( -5/2 \\right) = -5/3$。\n因為斜率乘積為 $-5/3 \\ne -1$，故 $\\triangle ABC$ 在頂點 $C$ 處不為直角。答案為「否」。",
    "choices": [
      "是",
      "否"
    ],
    "answer_contract": {
      "choices_required": true,
      "choice_count": 2,
      "correct_choice_count": 1,
      "frontend_render_choices": true,
      "answer_type": "choice",
      "answer_shape": "choice_label",
      "answer_equivalence": "choice_label",
      "checker": "choice_label_checker",
      "accepted_formats": [
        "B"
      ],
      "checker_key": "choice_label_checker",
      "equivalence_type": "choice_label"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( -3,4 \\right)$、$B\\left( -6,6 \\right)$與$C\\left( 2,-5 \\right)$、$D\\left( 0,k \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "answer": "-8",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{6 - (4)}{-6 - (-3)} = -2/3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{k - (-5)}{0 - (2)}$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2/3 \\cdot \\frac{k - (-5)}{-2} = -1$，",
      "解得 k = -8。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s3",
      "parameter_signature": "m1=-2/3:template=1:answer=-8",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(-3,4)",
        "B(-6,6)",
        "C(2,-5)",
        "D(0,k)",
        "AB垂直CD"
      ],
      "target": "k",
      "derivation": [
        "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
        "直線AB的斜率為 $m_{AB} = \\frac{6 - (4)}{-6 - (-3)} = -2/3$。",
        "直線CD的斜率為 $m_{CD} = \\frac{k - (-5)}{0 - (2)}$。",
        "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2/3 \\cdot \\frac{k - (-5)}{-2} = -1$，",
        "解得 k = -8。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -3,4 \\right)$、$B\\left( -6,6 \\right)$與$C\\left( 2,-5 \\right)$、$D\\left( 0,k \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求k之值。",
    "correct_answer": "-8",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{6 - (4)}{-6 - (-3)} = -2/3$。\n直線CD的斜率為 $m_{CD} = \\frac{k - (-5)}{0 - (2)}$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$-2/3 \\cdot \\frac{k - (-5)}{-2} = -1$，\n解得 k = -8。",
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
        "-8"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_line_equation",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，設直線$L$的方程式為$-4x-3y-7=0$。試求通過點$P\\left( 1,7 \\right)$且與直線$L$垂直的直線方程式。",
    "answer": "3x-4y+25=0",
    "answer_type": "text_short",
    "checker_type": "text_short_checker",
    "solution_steps": [
      "已知與直線 $L: -4x-3y-7=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
      "直線 $L$ 的斜率為 $m = -\\frac{-4}{-3} = -4/3$。",
      "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-3}{-4} = 3/4$。",
      "利用點斜式，通過點 $P(1,7)$ 且斜率為 $m'$ 的直線方程式為：",
      "$y - (7) = \\frac{-3}{-4} \\cdot (x - (1))$，",
      "整理化簡為一般式後可得：$3x-4y+25=0$。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_line_equation",
      "scenario_id": "s7",
      "parameter_signature": "a=-4:b=-3:c=-7:answer=3x-4y+25=0",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_line_equation"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "L: -4x-3y-7=0",
        "P(1,7)"
      ],
      "target": "perpendicular_line_equation",
      "derivation": [
        "已知與直線 $L: -4x-3y-7=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
        "直線 $L$ 的斜率為 $m = -\\frac{-4}{-3} = -4/3$。",
        "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-3}{-4} = 3/4$。",
        "利用點斜式，通過點 $P(1,7)$ 且斜率為 $m'$ 的直線方程式為：",
        "$y - (7) = \\frac{-3}{-4} \\cdot (x - (1))$，",
        "整理化簡為一般式後可得：$3x-4y+25=0$。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，設直線$L$的方程式為$-4x-3y-7=0$。試求通過點$P\\left( 1,7 \\right)$且與直線$L$垂直的直線方程式。",
    "correct_answer": "3x-4y+25=0",
    "explanation": "已知與直線 $L: -4x-3y-7=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。\n直線 $L$ 的斜率為 $m = -\\frac{-4}{-3} = -4/3$。\n因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-3}{-4} = 3/4$。\n利用點斜式，通過點 $P(1,7)$ 且斜率為 $m'$ 的直線方程式為：\n$y - (7) = \\frac{-3}{-4} \\cdot (x - (1))$，\n整理化簡為一般式後可得：$3x-4y+25=0$。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "answer_equivalence": "exact_string",
      "checker": "text_short_checker",
      "accepted_formats": [
        "3x-4y+25=0"
      ],
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string"
    }
  },
  {
    "problem_type_id": "triangle_right_angle_verification",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( -1,-5 \\right)$、$B\\left( -5,-3 \\right)$、$C\\left( -3,1 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $B$ 處為直角？",
    "answer": "A",
    "answer_type": "choice_label",
    "checker_type": "choice_label_checker",
    "solution_steps": [
      "欲驗證 $\\triangle ABC$ 在頂點 $B$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
      "計算與頂點 $B$ 相連的兩條邊的斜率：",
      "邊段 $AB$ 的斜率 $m_{AB} = \\frac{-2}{4} = -1/2$，",
      "邊段 $BC$ 的斜率 $m_{BC} = \\frac{4}{2} = 2$。",
      "計算兩斜率的乘積：$m_{AB} \\cdot m_{BC} = -1/2 \\cdot \\left( 2 \\right) = -1$。",
      "因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $B$ 處為直角。答案為「是」。"
    ],
    "metadata": {
      "scenario_family": "triangle_right_angle_verification",
      "scenario_id": "s5",
      "parameter_signature": "A=(-1,-5):B=(-5,-3):C=(-3,1):test=B:answer=A",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_lines_right_angle_verification"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(-1,-5)",
        "B(-5,-3)",
        "C(-3,1)",
        "test_vertex=B"
      ],
      "target": "right_angle_verification",
      "derivation": [
        "欲驗證 $\\triangle ABC$ 在頂點 $B$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
        "計算與頂點 $B$ 相連的兩條邊的斜率：",
        "邊段 $AB$ 的斜率 $m_{AB} = \\frac{-2}{4} = -1/2$，",
        "邊段 $BC$ 的斜率 $m_{BC} = \\frac{4}{2} = 2$。",
        "計算兩斜率的乘積：$m_{AB} \\cdot m_{BC} = -1/2 \\cdot \\left( 2 \\right) = -1$。",
        "因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $B$ 處為直角。答案為「是」。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( -1,-5 \\right)$、$B\\left( -5,-3 \\right)$、$C\\left( -3,1 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $B$ 處為直角？",
    "correct_answer": "A",
    "explanation": "欲驗證 $\\triangle ABC$ 在頂點 $B$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。\n計算與頂點 $B$ 相連的兩條邊的斜率：\n邊段 $AB$ 的斜率 $m_{AB} = \\frac{-2}{4} = -1/2$，\n邊段 $BC$ 的斜率 $m_{BC} = \\frac{4}{2} = 2$。\n計算兩斜率的乘積：$m_{AB} \\cdot m_{BC} = -1/2 \\cdot \\left( 2 \\right) = -1$。\n因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $B$ 處為直角。答案為「是」。",
    "choices": [
      "是",
      "否"
    ],
    "answer_contract": {
      "choices_required": true,
      "choice_count": 2,
      "correct_choice_count": 1,
      "frontend_render_choices": true,
      "answer_type": "choice",
      "answer_shape": "choice_label",
      "answer_equivalence": "choice_label",
      "checker": "choice_label_checker",
      "accepted_formats": [
        "A"
      ],
      "checker_key": "choice_label_checker",
      "equivalence_type": "choice_label"
    }
  },
  {
    "problem_type_id": "perpendicular_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "設$A\\left( 3,x \\right)$、$B\\left( 4,-6 \\right)$與$C\\left( 5,5 \\right)$、$D\\left( 4,4 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "answer": "-5",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
      "直線AB的斜率為 $m_{AB} = \\frac{-6 - x}{4 - (3)}$。",
      "直線CD的斜率為 $m_{CD} = \\frac{4 - (5)}{4 - (5)} = 1$。",
      "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$\\frac{-6 - x}{1} \\cdot (1) = -1$，",
      "解得 x = -5。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_lines_properties",
      "scenario_id": "s3",
      "parameter_signature": "m1=-1:template=3:answer=-5",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_lines_slope_product"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(3,x)",
        "B(4,-6)",
        "C(5,5)",
        "D(4,4)",
        "AB垂直CD"
      ],
      "target": "x",
      "derivation": [
        "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。",
        "直線AB的斜率為 $m_{AB} = \\frac{-6 - x}{4 - (3)}$。",
        "直線CD的斜率為 $m_{CD} = \\frac{4 - (5)}{4 - (5)} = 1$。",
        "由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$\\frac{-6 - x}{1} \\cdot (1) = -1$，",
        "解得 x = -5。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 3,x \\right)$、$B\\left( 4,-6 \\right)$與$C\\left( 5,5 \\right)$、$D\\left( 4,4 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求x之值。",
    "correct_answer": "-5",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$垂直，所以它們的斜率乘積為 $-1$。\n直線AB的斜率為 $m_{AB} = \\frac{-6 - x}{4 - (3)}$。\n直線CD的斜率為 $m_{CD} = \\frac{4 - (5)}{4 - (5)} = 1$。\n由 $m_{AB} \\cdot m_{CD} = -1$ 可得：$\\frac{-6 - x}{1} \\cdot (1) = -1$，\n解得 x = -5。",
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
        "-5"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "perpendicular_line_equation",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，設直線$L$的方程式為$-5x-4y+8=0$。試求通過點$P\\left( 1,0 \\right)$且與直線$L$垂直的直線方程式。",
    "answer": "4x-5y-4=0",
    "answer_type": "text_short",
    "checker_type": "text_short_checker",
    "solution_steps": [
      "已知與直線 $L: -5x-4y+8=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
      "直線 $L$ 的斜率為 $m = -\\frac{-5}{-4} = -5/4$。",
      "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-4}{-5} = 4/5$。",
      "利用點斜式，通過點 $P(1,0)$ 且斜率為 $m'$ 的直線方程式為：",
      "$y - (0) = \\frac{-4}{-5} \\cdot (x - (1))$，",
      "整理化簡為一般式後可得：$4x-5y-4=0$。"
    ],
    "metadata": {
      "scenario_family": "perpendicular_line_equation",
      "scenario_id": "s5",
      "parameter_signature": "a=-5:b=-4:c=8:answer=4x-5y-4=0",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "perpendicular_line_equation"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "L: -5x-4y+8=0",
        "P(1,0)"
      ],
      "target": "perpendicular_line_equation",
      "derivation": [
        "已知與直線 $L: -5x-4y+8=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。",
        "直線 $L$ 的斜率為 $m = -\\frac{-5}{-4} = -5/4$。",
        "因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-4}{-5} = 4/5$。",
        "利用點斜式，通過點 $P(1,0)$ 且斜率為 $m'$ 的直線方程式為：",
        "$y - (0) = \\frac{-4}{-5} \\cdot (x - (1))$，",
        "整理化簡為一般式後可得：$4x-5y-4=0$。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，設直線$L$的方程式為$-5x-4y+8=0$。試求通過點$P\\left( 1,0 \\right)$且與直線$L$垂直的直線方程式。",
    "correct_answer": "4x-5y-4=0",
    "explanation": "已知與直線 $L: -5x-4y+8=0$ 垂直的直線，其斜率與 $L$ 的斜率乘積為 $-1$。\n直線 $L$ 的斜率為 $m = -\\frac{-5}{-4} = -5/4$。\n因此，所求直線 $L'$ 的斜率為 $m' = \\frac{-4}{-5} = 4/5$。\n利用點斜式，通過點 $P(1,0)$ 且斜率為 $m'$ 的直線方程式為：\n$y - (0) = \\frac{-4}{-5} \\cdot (x - (1))$，\n整理化簡為一般式後可得：$4x-5y-4=0$。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "text_short",
      "answer_shape": "text_short",
      "answer_equivalence": "exact_string",
      "checker": "text_short_checker",
      "accepted_formats": [
        "4x-5y-4=0"
      ],
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string"
    }
  },
  {
    "problem_type_id": "triangle_right_angle_verification",
    "skill_id": "vh_數學B1_PropertiesOfPerpendicularLines",
    "subskill_id": "perpendicular_lines_properties",
    "question_text": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( -2,2 \\right)$、$B\\left( -6,4 \\right)$、$C\\left( -5,1 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $C$ 處為直角？",
    "answer": "A",
    "answer_type": "choice_label",
    "checker_type": "choice_label_checker",
    "solution_steps": [
      "欲驗證 $\\triangle ABC$ 在頂點 $C$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
      "計算與頂點 $C$ 相連的兩條邊的斜率：",
      "邊段 $AC$ 的斜率 $m_{AC} = \\frac{1}{3} = 1/3$，",
      "邊段 $BC$ 的斜率 $m_{BC} = \\frac{3}{-1} = -3$。",
      "計算兩斜率的乘積：$m_{AC} \\cdot m_{BC} = 1/3 \\cdot \\left( -3 \\right) = -1$。",
      "因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $C$ 處為直角。答案為「是」。"
    ],
    "metadata": {
      "scenario_family": "triangle_right_angle_verification",
      "scenario_id": "s6",
      "parameter_signature": "A=(-2,2):B=(-6,4):C=(-5,1):test=C:answer=A",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "perpendicular_lines_right_angle_verification"
      ],
      "prerequisite_subskills": [],
      "givens": [
        "A(-2,2)",
        "B(-6,4)",
        "C(-5,1)",
        "test_vertex=C"
      ],
      "target": "right_angle_verification",
      "derivation": [
        "欲驗證 $\\triangle ABC$ 在頂點 $C$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。",
        "計算與頂點 $C$ 相連的兩條邊的斜率：",
        "邊段 $AC$ 的斜率 $m_{AC} = \\frac{1}{3} = 1/3$，",
        "邊段 $BC$ 的斜率 $m_{BC} = \\frac{3}{-1} = -3$。",
        "計算兩斜率的乘積：$m_{AC} \\cdot m_{BC} = 1/3 \\cdot \\left( -3 \\right) = -1$。",
        "因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $C$ 處為直角。答案為「是」。"
      ],
      "verified_problem_types": [
        "perpendicular_lines_properties",
        "perpendicular_line_equation",
        "triangle_right_angle_verification"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "在坐標平面上，已知 $\\triangle ABC$ 的三頂點為 $A\\left( -2,2 \\right)$、$B\\left( -6,4 \\right)$、$C\\left( -5,1 \\right)$。試問 $\\triangle ABC$ 是否在頂點 $C$ 處為直角？",
    "correct_answer": "A",
    "explanation": "欲驗證 $\\triangle ABC$ 在頂點 $C$ 處是否為直角，可利用兩垂直線段的斜率乘積為 $-1$ 的性質。\n計算與頂點 $C$ 相連的兩條邊的斜率：\n邊段 $AC$ 的斜率 $m_{AC} = \\frac{1}{3} = 1/3$，\n邊段 $BC$ 的斜率 $m_{BC} = \\frac{3}{-1} = -3$。\n計算兩斜率的乘積：$m_{AC} \\cdot m_{BC} = 1/3 \\cdot \\left( -3 \\right) = -1$。\n因為斜率乘積等於 $-1$，故 $\\triangle ABC$ 在頂點 $C$ 處為直角。答案為「是」。",
    "choices": [
      "是",
      "否"
    ],
    "answer_contract": {
      "choices_required": true,
      "choice_count": 2,
      "correct_choice_count": 1,
      "frontend_render_choices": true,
      "answer_type": "choice",
      "answer_shape": "choice_label",
      "answer_equivalence": "choice_label",
      "checker": "choice_label_checker",
      "accepted_formats": [
        "A"
      ],
      "checker_key": "choice_label_checker",
      "equivalence_type": "choice_label"
    }
  }
]
```
