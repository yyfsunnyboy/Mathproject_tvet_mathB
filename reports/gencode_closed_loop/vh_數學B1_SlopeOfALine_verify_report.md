# Verify Report: vh_數學B1_SlopeOfALine

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
    "text_short_slope_of_line_problems"
  ],
  "observed_problem_types": [
    "text_short_slope_of_line_problems"
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_2_1/text_short_slope_of_line_problems/candidate_v1.py",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-9, -2)$ 與 $B(-5, -3)$ 的直線斜率。",
    "answer": "-1/4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-9, -2)$ 與 $B(-5, -3)$ 代入公式中：",
      "$m = \\frac{-3 - (-2)}{-5 - (-9)}$",
      "$m = \\frac{-1}{4} = -1/4$。",
      "因此，直線的斜率為 -1/4。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s7",
      "parameter_signature": "variant=1:answer=-1/4",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-9, -2)$ 與 $B(-5, -3)$ 的直線斜率。",
    "correct_answer": "-1/4",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-9, -2)$ 與 $B(-5, -3)$ 代入公式中：\n$m = \\frac{-3 - (-2)}{-5 - (-9)}$\n$m = \\frac{-1}{4} = -1/4$。\n因此，直線的斜率為 -1/4。",
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
        "-1/4"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-9, -8)$ 與 $B(-8, -3)$ 的直線斜率。",
    "answer": "5",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-9, -8)$ 與 $B(-8, -3)$ 代入公式中：",
      "$m = \\frac{-3 - (-8)}{-8 - (-9)}$",
      "$m = \\frac{5}{1} = 5$。",
      "因此，直線的斜率為 5。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s2",
      "parameter_signature": "variant=0:answer=5",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-9, -8)$ 與 $B(-8, -3)$ 的直線斜率。",
    "correct_answer": "5",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-9, -8)$ 與 $B(-8, -3)$ 代入公式中：\n$m = \\frac{-3 - (-8)}{-8 - (-9)}$\n$m = \\frac{5}{1} = 5$。\n因此，直線的斜率為 5。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-5, -3)$ 與 $B(-2, -5)$ 的直線斜率。",
    "answer": "-2/3",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-5, -3)$ 與 $B(-2, -5)$ 代入公式中：",
      "$m = \\frac{-5 - (-3)}{-2 - (-5)}$",
      "$m = \\frac{-2}{3} = -2/3$。",
      "因此，直線的斜率為 -2/3。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s8",
      "parameter_signature": "variant=1:answer=-2/3",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-5, -3)$ 與 $B(-2, -5)$ 的直線斜率。",
    "correct_answer": "-2/3",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-5, -3)$ 與 $B(-2, -5)$ 代入公式中：\n$m = \\frac{-5 - (-3)}{-2 - (-5)}$\n$m = \\frac{-2}{3} = -2/3$。\n因此，直線的斜率為 -2/3。",
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
        "-2/3"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "若三點 $A(-12, 0)$、$B(0, k)$、$C(8, 5)$ 共線，試求 $k$ 之值。",
    "answer": "3",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{AB} = m_{AC}$)。",
      "首先計算直線 $AC$ 的斜率：",
      "$m_{AC} = \\frac{5 - (0)}{8 - (-12)} = \\frac{5}{20} = 1/4$。",
      "接著利用 $m_{AB} = m_{AC}$ 列出等式：",
      "$\\frac{k - (0)}{0 - (-12)} = 1/4$",
      "$\\frac{k - (0)}{12} = 1/4$",
      "兩邊同乘以 12 得：",
      "$k - (0) = 3$",
      "解得 $k = 3$。",
      "因此，$k$ 的值為 3。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s4",
      "parameter_signature": "variant=3:answer=3",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "若三點 $A(-12, 0)$、$B(0, k)$、$C(8, 5)$ 共線，試求 $k$ 之值。",
    "correct_answer": "3",
    "explanation": "因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{AB} = m_{AC}$)。\n首先計算直線 $AC$ 的斜率：\n$m_{AC} = \\frac{5 - (0)}{8 - (-12)} = \\frac{5}{20} = 1/4$。\n接著利用 $m_{AB} = m_{AC}$ 列出等式：\n$\\frac{k - (0)}{0 - (-12)} = 1/4$\n$\\frac{k - (0)}{12} = 1/4$\n兩邊同乘以 12 得：\n$k - (0) = 3$\n解得 $k = 3$。\n因此，$k$ 的值為 3。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "若直線通過點 $A(-8, a)$ 與 $B(-9, 1)$，且其斜率為 -3，試求 $a$ 之值。",
    "answer": "-2",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "根據直線斜率公式，斜率 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-8, a)$ 與 $B(-9, 1)$ 以及斜率 $m = -3$ 代入：",
      "$-3 = \\frac{1 - a}{-9 - (-8)}$",
      "$-3 = \\frac{1 - a}{-1}$",
      "兩邊同乘以 -1 得：",
      "$3 = 1 - a$",
      "解得 $a = 1 - (3) = -2$。",
      "因此，$a$ 的值為 -2。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s4",
      "parameter_signature": "variant=2:answer=-2",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "若直線通過點 $A(-8, a)$ 與 $B(-9, 1)$，且其斜率為 -3，試求 $a$ 之值。",
    "correct_answer": "-2",
    "explanation": "根據直線斜率公式，斜率 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-8, a)$ 與 $B(-9, 1)$ 以及斜率 $m = -3$ 代入：\n$-3 = \\frac{1 - a}{-9 - (-8)}$\n$-3 = \\frac{1 - a}{-1}$\n兩邊同乘以 -1 得：\n$3 = 1 - a$\n解得 $a = 1 - (3) = -2$。\n因此，$a$ 的值為 -2。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "若直線通過點 $A(2, a)$ 與 $B(1, -10)$，且其斜率為 4，試求 $a$ 之值。",
    "answer": "-6",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "根據直線斜率公式，斜率 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(2, a)$ 與 $B(1, -10)$ 以及斜率 $m = 4$ 代入：",
      "$4 = \\frac{-10 - a}{1 - (2)}$",
      "$4 = \\frac{-10 - a}{-1}$",
      "兩邊同乘以 -1 得：",
      "$-4 = -10 - a$",
      "解得 $a = -10 - (-4) = -6$。",
      "因此，$a$ 的值為 -6。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s7",
      "parameter_signature": "variant=2:answer=-6",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "若直線通過點 $A(2, a)$ 與 $B(1, -10)$，且其斜率為 4，試求 $a$ 之值。",
    "correct_answer": "-6",
    "explanation": "根據直線斜率公式，斜率 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(2, a)$ 與 $B(1, -10)$ 以及斜率 $m = 4$ 代入：\n$4 = \\frac{-10 - a}{1 - (2)}$\n$4 = \\frac{-10 - a}{-1}$\n兩邊同乘以 -1 得：\n$-4 = -10 - a$\n解得 $a = -10 - (-4) = -6$。\n因此，$a$ 的值為 -6。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "若三點 $A(-12, 13)$、$B(-8, k)$、$C(8, -2)$ 共線，試求 $k$ 之值。",
    "answer": "10",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{AB} = m_{AC}$)。",
      "首先計算直線 $AC$ 的斜率：",
      "$m_{AC} = \\frac{-2 - (13)}{8 - (-12)} = \\frac{-15}{20} = -3/4$。",
      "接著利用 $m_{AB} = m_{AC}$ 列出等式：",
      "$\\frac{k - (13)}{-8 - (-12)} = -3/4$",
      "$\\frac{k - (13)}{4} = -3/4$",
      "兩邊同乘以 4 得：",
      "$k - (13) = -3$",
      "解得 $k = 10$。",
      "因此，$k$ 的值為 10。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s2",
      "parameter_signature": "variant=3:answer=10",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "若三點 $A(-12, 13)$、$B(-8, k)$、$C(8, -2)$ 共線，試求 $k$ 之值。",
    "correct_answer": "10",
    "explanation": "因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{AB} = m_{AC}$)。\n首先計算直線 $AC$ 的斜率：\n$m_{AC} = \\frac{-2 - (13)}{8 - (-12)} = \\frac{-15}{20} = -3/4$。\n接著利用 $m_{AB} = m_{AC}$ 列出等式：\n$\\frac{k - (13)}{-8 - (-12)} = -3/4$\n$\\frac{k - (13)}{4} = -3/4$\n兩邊同乘以 4 得：\n$k - (13) = -3$\n解得 $k = 10$。\n因此，$k$ 的值為 10。",
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
        "10"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "若三點 $A(-4, 9)$、$B(-2, k)$、$C(0, 5)$ 共線，試求 $k$ 之值。",
    "answer": "7",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{AB} = m_{AC}$)。",
      "首先計算直線 $AC$ 的斜率：",
      "$m_{AC} = \\frac{5 - (9)}{0 - (-4)} = \\frac{-4}{4} = -1$。",
      "接著利用 $m_{AB} = m_{AC}$ 列出等式：",
      "$\\frac{k - (9)}{-2 - (-4)} = -1$",
      "$\\frac{k - (9)}{2} = -1$",
      "兩邊同乘以 2 得：",
      "$k - (9) = -2$",
      "解得 $k = 7$。",
      "因此，$k$ 的值為 7。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s6",
      "parameter_signature": "variant=3:answer=7",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "若三點 $A(-4, 9)$、$B(-2, k)$、$C(0, 5)$ 共線，試求 $k$ 之值。",
    "correct_answer": "7",
    "explanation": "因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{AB} = m_{AC}$)。\n首先計算直線 $AC$ 的斜率：\n$m_{AC} = \\frac{5 - (9)}{0 - (-4)} = \\frac{-4}{4} = -1$。\n接著利用 $m_{AB} = m_{AC}$ 列出等式：\n$\\frac{k - (9)}{-2 - (-4)} = -1$\n$\\frac{k - (9)}{2} = -1$\n兩邊同乘以 2 得：\n$k - (9) = -2$\n解得 $k = 7$。\n因此，$k$ 的值為 7。",
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
        "7"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "若直線通過點 $A(3, a)$ 與 $B(2, -5)$，且其斜率為 -3，試求 $a$ 之值。",
    "answer": "-8",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "根據直線斜率公式，斜率 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(3, a)$ 與 $B(2, -5)$ 以及斜率 $m = -3$ 代入：",
      "$-3 = \\frac{-5 - a}{2 - (3)}$",
      "$-3 = \\frac{-5 - a}{-1}$",
      "兩邊同乘以 -1 得：",
      "$3 = -5 - a$",
      "解得 $a = -5 - (3) = -8$。",
      "因此，$a$ 的值為 -8。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s7",
      "parameter_signature": "variant=2:answer=-8",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "若直線通過點 $A(3, a)$ 與 $B(2, -5)$，且其斜率為 -3，試求 $a$ 之值。",
    "correct_answer": "-8",
    "explanation": "根據直線斜率公式，斜率 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(3, a)$ 與 $B(2, -5)$ 以及斜率 $m = -3$ 代入：\n$-3 = \\frac{-5 - a}{2 - (3)}$\n$-3 = \\frac{-5 - a}{-1}$\n兩邊同乘以 -1 得：\n$3 = -5 - a$\n解得 $a = -5 - (3) = -8$。\n因此，$a$ 的值為 -8。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "若三點 $A(-6, 9)$、$B(2, k)$、$C(6, -9)$ 共線，試求 $k$ 之值。",
    "answer": "-3",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{AB} = m_{AC}$)。",
      "首先計算直線 $AC$ 的斜率：",
      "$m_{AC} = \\frac{-9 - (9)}{6 - (-6)} = \\frac{-18}{12} = -3/2$。",
      "接著利用 $m_{AB} = m_{AC}$ 列出等式：",
      "$\\frac{k - (9)}{2 - (-6)} = -3/2$",
      "$\\frac{k - (9)}{8} = -3/2$",
      "兩邊同乘以 8 得：",
      "$k - (9) = -12$",
      "解得 $k = -3$。",
      "因此，$k$ 的值為 -3。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s7",
      "parameter_signature": "variant=3:answer=-3",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "若三點 $A(-6, 9)$、$B(2, k)$、$C(6, -9)$ 共線，試求 $k$ 之值。",
    "correct_answer": "-3",
    "explanation": "因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{AB} = m_{AC}$)。\n首先計算直線 $AC$ 的斜率：\n$m_{AC} = \\frac{-9 - (9)}{6 - (-6)} = \\frac{-18}{12} = -3/2$。\n接著利用 $m_{AB} = m_{AC}$ 列出等式：\n$\\frac{k - (9)}{2 - (-6)} = -3/2$\n$\\frac{k - (9)}{8} = -3/2$\n兩邊同乘以 8 得：\n$k - (9) = -12$\n解得 $k = -3$。\n因此，$k$ 的值為 -3。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-10, -5)$ 與 $B(-15, 8)$ 的直線斜率。",
    "answer": "-13/5",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-10, -5)$ 與 $B(-15, 8)$ 代入公式中：",
      "$m = \\frac{8 - (-5)}{-15 - (-10)}$",
      "$m = \\frac{13}{-5} = -13/5$。",
      "因此，直線的斜率為 -13/5。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s8",
      "parameter_signature": "variant=1:answer=-13/5",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-10, -5)$ 與 $B(-15, 8)$ 的直線斜率。",
    "correct_answer": "-13/5",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-10, -5)$ 與 $B(-15, 8)$ 代入公式中：\n$m = \\frac{8 - (-5)}{-15 - (-10)}$\n$m = \\frac{13}{-5} = -13/5$。\n因此，直線的斜率為 -13/5。",
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
        "-13/5"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-4, 4)$ 與 $B(0, 12)$ 的直線斜率。",
    "answer": "2",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-4, 4)$ 與 $B(0, 12)$ 代入公式中：",
      "$m = \\frac{12 - (4)}{0 - (-4)}$",
      "$m = \\frac{8}{4} = 2$。",
      "因此，直線的斜率為 2。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s5",
      "parameter_signature": "variant=0:answer=2",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-4, 4)$ 與 $B(0, 12)$ 的直線斜率。",
    "correct_answer": "2",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-4, 4)$ 與 $B(0, 12)$ 代入公式中：\n$m = \\frac{12 - (4)}{0 - (-4)}$\n$m = \\frac{8}{4} = 2$。\n因此，直線的斜率為 2。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-3, -7)$ 與 $B(-5, -4)$ 的直線斜率。",
    "answer": "-3/2",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-3, -7)$ 與 $B(-5, -4)$ 代入公式中：",
      "$m = \\frac{-4 - (-7)}{-5 - (-3)}$",
      "$m = \\frac{3}{-2} = -3/2$。",
      "因此，直線的斜率為 -3/2。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s1",
      "parameter_signature": "variant=1:answer=-3/2",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-3, -7)$ 與 $B(-5, -4)$ 的直線斜率。",
    "correct_answer": "-3/2",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-3, -7)$ 與 $B(-5, -4)$ 代入公式中：\n$m = \\frac{-4 - (-7)}{-5 - (-3)}$\n$m = \\frac{3}{-2} = -3/2$。\n因此，直線的斜率為 -3/2。",
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
        "-3/2"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(10, -7)$ 與 $B(6, -8)$ 的直線斜率。",
    "answer": "1/4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(10, -7)$ 與 $B(6, -8)$ 代入公式中：",
      "$m = \\frac{-8 - (-7)}{6 - (10)}$",
      "$m = \\frac{-1}{-4} = 1/4$。",
      "因此，直線的斜率為 1/4。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s8",
      "parameter_signature": "variant=1:answer=1/4",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(10, -7)$ 與 $B(6, -8)$ 的直線斜率。",
    "correct_answer": "1/4",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(10, -7)$ 與 $B(6, -8)$ 代入公式中：\n$m = \\frac{-8 - (-7)}{6 - (10)}$\n$m = \\frac{-1}{-4} = 1/4$。\n因此，直線的斜率為 1/4。",
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
        "1/4"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "若三點 $A(-8, -8)$、$B(0, k)$、$C(4, 1)$ 共線，試求 $k$ 之值。",
    "answer": "-2",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{AB} = m_{AC}$)。",
      "首先計算直線 $AC$ 的斜率：",
      "$m_{AC} = \\frac{1 - (-8)}{4 - (-8)} = \\frac{9}{12} = 3/4$。",
      "接著利用 $m_{AB} = m_{AC}$ 列出等式：",
      "$\\frac{k - (-8)}{0 - (-8)} = 3/4$",
      "$\\frac{k - (-8)}{8} = 3/4$",
      "兩邊同乘以 8 得：",
      "$k - (-8) = 6$",
      "解得 $k = -2$。",
      "因此，$k$ 的值為 -2。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s3",
      "parameter_signature": "variant=3:answer=-2",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "若三點 $A(-8, -8)$、$B(0, k)$、$C(4, 1)$ 共線，試求 $k$ 之值。",
    "correct_answer": "-2",
    "explanation": "因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{AB} = m_{AC}$)。\n首先計算直線 $AC$ 的斜率：\n$m_{AC} = \\frac{1 - (-8)}{4 - (-8)} = \\frac{9}{12} = 3/4$。\n接著利用 $m_{AB} = m_{AC}$ 列出等式：\n$\\frac{k - (-8)}{0 - (-8)} = 3/4$\n$\\frac{k - (-8)}{8} = 3/4$\n兩邊同乘以 8 得：\n$k - (-8) = 6$\n解得 $k = -2$。\n因此，$k$ 的值為 -2。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(0, 1)$ 與 $B(4, -4)$ 的直線斜率。",
    "answer": "-5/4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(0, 1)$ 與 $B(4, -4)$ 代入公式中：",
      "$m = \\frac{-4 - (1)}{4 - (0)}$",
      "$m = \\frac{-5}{4} = -5/4$。",
      "因此，直線的斜率為 -5/4。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s8",
      "parameter_signature": "variant=1:answer=-5/4",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(0, 1)$ 與 $B(4, -4)$ 的直線斜率。",
    "correct_answer": "-5/4",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(0, 1)$ 與 $B(4, -4)$ 代入公式中：\n$m = \\frac{-4 - (1)}{4 - (0)}$\n$m = \\frac{-5}{4} = -5/4$。\n因此，直線的斜率為 -5/4。",
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
        "-5/4"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-3, -6)$ 與 $B(-8, 0)$ 的直線斜率。",
    "answer": "-6/5",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-3, -6)$ 與 $B(-8, 0)$ 代入公式中：",
      "$m = \\frac{0 - (-6)}{-8 - (-3)}$",
      "$m = \\frac{6}{-5} = -6/5$。",
      "因此，直線的斜率為 -6/5。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s2",
      "parameter_signature": "variant=1:answer=-6/5",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-3, -6)$ 與 $B(-8, 0)$ 的直線斜率。",
    "correct_answer": "-6/5",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-3, -6)$ 與 $B(-8, 0)$ 代入公式中：\n$m = \\frac{0 - (-6)}{-8 - (-3)}$\n$m = \\frac{6}{-5} = -6/5$。\n因此，直線的斜率為 -6/5。",
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
        "-6/5"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "若三點 $A(-4, 5)$、$B(2, k)$、$C(4, -7)$ 共線，試求 $k$ 之值。",
    "answer": "-4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{AB} = m_{AC}$)。",
      "首先計算直線 $AC$ 的斜率：",
      "$m_{AC} = \\frac{-7 - (5)}{4 - (-4)} = \\frac{-12}{8} = -3/2$。",
      "接著利用 $m_{AB} = m_{AC}$ 列出等式：",
      "$\\frac{k - (5)}{2 - (-4)} = -3/2$",
      "$\\frac{k - (5)}{6} = -3/2$",
      "兩邊同乘以 6 得：",
      "$k - (5) = -9$",
      "解得 $k = -4$。",
      "因此，$k$ 的值為 -4。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s9",
      "parameter_signature": "variant=3:answer=-4",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "若三點 $A(-4, 5)$、$B(2, k)$、$C(4, -7)$ 共線，試求 $k$ 之值。",
    "correct_answer": "-4",
    "explanation": "因為三點 $A$、$B$、$C$ 共線，所以直線 $AB$ 的斜率等於直線 $AC$ 的斜率 ($m_{AB} = m_{AC}$)。\n首先計算直線 $AC$ 的斜率：\n$m_{AC} = \\frac{-7 - (5)}{4 - (-4)} = \\frac{-12}{8} = -3/2$。\n接著利用 $m_{AB} = m_{AC}$ 列出等式：\n$\\frac{k - (5)}{2 - (-4)} = -3/2$\n$\\frac{k - (5)}{6} = -3/2$\n兩邊同乘以 6 得：\n$k - (5) = -9$\n解得 $k = -4$。\n因此，$k$ 的值為 -4。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-4, 10)$ 與 $B(-6, 20)$ 的直線斜率。",
    "answer": "-5",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-4, 10)$ 與 $B(-6, 20)$ 代入公式中：",
      "$m = \\frac{20 - (10)}{-6 - (-4)}$",
      "$m = \\frac{10}{-2} = -5$。",
      "因此，直線的斜率為 -5。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s4",
      "parameter_signature": "variant=0:answer=-5",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-4, 10)$ 與 $B(-6, 20)$ 的直線斜率。",
    "correct_answer": "-5",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-4, 10)$ 與 $B(-6, 20)$ 代入公式中：\n$m = \\frac{20 - (10)}{-6 - (-4)}$\n$m = \\frac{10}{-2} = -5$。\n因此，直線的斜率為 -5。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-9, -1)$ 與 $B(-11, -11)$ 的直線斜率。",
    "answer": "5",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-9, -1)$ 與 $B(-11, -11)$ 代入公式中：",
      "$m = \\frac{-11 - (-1)}{-11 - (-9)}$",
      "$m = \\frac{-10}{-2} = 5$。",
      "因此，直線的斜率為 5。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s1",
      "parameter_signature": "variant=0:answer=5",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-9, -1)$ 與 $B(-11, -11)$ 的直線斜率。",
    "correct_answer": "5",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-9, -1)$ 與 $B(-11, -11)$ 代入公式中：\n$m = \\frac{-11 - (-1)}{-11 - (-9)}$\n$m = \\frac{-10}{-2} = 5$。\n因此，直線的斜率為 5。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(5, 5)$ 與 $B(7, -4)$ 的直線斜率。",
    "answer": "-9/2",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(5, 5)$ 與 $B(7, -4)$ 代入公式中：",
      "$m = \\frac{-4 - (5)}{7 - (5)}$",
      "$m = \\frac{-9}{2} = -9/2$。",
      "因此，直線的斜率為 -9/2。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s8",
      "parameter_signature": "variant=1:answer=-9/2",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(5, 5)$ 與 $B(7, -4)$ 的直線斜率。",
    "correct_answer": "-9/2",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(5, 5)$ 與 $B(7, -4)$ 代入公式中：\n$m = \\frac{-4 - (5)}{7 - (5)}$\n$m = \\frac{-9}{2} = -9/2$。\n因此，直線的斜率為 -9/2。",
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
        "-9/2"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(2, 1)$ 與 $B(-3, 3)$ 的直線斜率。",
    "answer": "-2/5",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(2, 1)$ 與 $B(-3, 3)$ 代入公式中：",
      "$m = \\frac{3 - (1)}{-3 - (2)}$",
      "$m = \\frac{2}{-5} = -2/5$。",
      "因此，直線的斜率為 -2/5。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s9",
      "parameter_signature": "variant=1:answer=-2/5",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(2, 1)$ 與 $B(-3, 3)$ 的直線斜率。",
    "correct_answer": "-2/5",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(2, 1)$ 與 $B(-3, 3)$ 代入公式中：\n$m = \\frac{3 - (1)}{-3 - (2)}$\n$m = \\frac{2}{-5} = -2/5$。\n因此，直線的斜率為 -2/5。",
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
        "-2/5"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-1, -3)$ 與 $B(0, -5)$ 的直線斜率。",
    "answer": "-2",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-1, -3)$ 與 $B(0, -5)$ 代入公式中：",
      "$m = \\frac{-5 - (-3)}{0 - (-1)}$",
      "$m = \\frac{-2}{1} = -2$。",
      "因此，直線的斜率為 -2。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s1",
      "parameter_signature": "variant=0:answer=-2",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-1, -3)$ 與 $B(0, -5)$ 的直線斜率。",
    "correct_answer": "-2",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-1, -3)$ 與 $B(0, -5)$ 代入公式中：\n$m = \\frac{-5 - (-3)}{0 - (-1)}$\n$m = \\frac{-2}{1} = -2$。\n因此，直線的斜率為 -2。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-2, 6)$ 與 $B(1, -10)$ 的直線斜率。",
    "answer": "-16/3",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-2, 6)$ 與 $B(1, -10)$ 代入公式中：",
      "$m = \\frac{-10 - (6)}{1 - (-2)}$",
      "$m = \\frac{-16}{3} = -16/3$。",
      "因此，直線的斜率為 -16/3。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s5",
      "parameter_signature": "variant=1:answer=-16/3",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-2, 6)$ 與 $B(1, -10)$ 的直線斜率。",
    "correct_answer": "-16/3",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-2, 6)$ 與 $B(1, -10)$ 代入公式中：\n$m = \\frac{-10 - (6)}{1 - (-2)}$\n$m = \\frac{-16}{3} = -16/3$。\n因此，直線的斜率為 -16/3。",
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
        "-16/3"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(1, 7)$ 與 $B(4, 19)$ 的直線斜率。",
    "answer": "4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(1, 7)$ 與 $B(4, 19)$ 代入公式中：",
      "$m = \\frac{19 - (7)}{4 - (1)}$",
      "$m = \\frac{12}{3} = 4$。",
      "因此，直線的斜率為 4。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s2",
      "parameter_signature": "variant=0:answer=4",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(1, 7)$ 與 $B(4, 19)$ 的直線斜率。",
    "correct_answer": "4",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(1, 7)$ 與 $B(4, 19)$ 代入公式中：\n$m = \\frac{19 - (7)}{4 - (1)}$\n$m = \\frac{12}{3} = 4$。\n因此，直線的斜率為 4。",
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
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "若直線通過點 $A(5, a)$ 與 $B(0, 4)$，且其斜率為 -4，試求 $a$ 之值。",
    "answer": "-16",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "根據直線斜率公式，斜率 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(5, a)$ 與 $B(0, 4)$ 以及斜率 $m = -4$ 代入：",
      "$-4 = \\frac{4 - a}{0 - (5)}$",
      "$-4 = \\frac{4 - a}{-5}$",
      "兩邊同乘以 -5 得：",
      "$20 = 4 - a$",
      "解得 $a = 4 - (20) = -16$。",
      "因此，$a$ 的值為 -16。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s2",
      "parameter_signature": "variant=2:answer=-16",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "若直線通過點 $A(5, a)$ 與 $B(0, 4)$，且其斜率為 -4，試求 $a$ 之值。",
    "correct_answer": "-16",
    "explanation": "根據直線斜率公式，斜率 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(5, a)$ 與 $B(0, 4)$ 以及斜率 $m = -4$ 代入：\n$-4 = \\frac{4 - a}{0 - (5)}$\n$-4 = \\frac{4 - a}{-5}$\n兩邊同乘以 -5 得：\n$20 = 4 - a$\n解得 $a = 4 - (20) = -16$。\n因此，$a$ 的值為 -16。",
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
        "-16"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-7, 0)$ 與 $B(-3, 3)$ 的直線斜率。",
    "answer": "3/4",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-7, 0)$ 與 $B(-3, 3)$ 代入公式中：",
      "$m = \\frac{3 - (0)}{-3 - (-7)}$",
      "$m = \\frac{3}{4} = 3/4$。",
      "因此，直線的斜率為 3/4。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s9",
      "parameter_signature": "variant=1:answer=3/4",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-7, 0)$ 與 $B(-3, 3)$ 的直線斜率。",
    "correct_answer": "3/4",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-7, 0)$ 與 $B(-3, 3)$ 代入公式中：\n$m = \\frac{3 - (0)}{-3 - (-7)}$\n$m = \\frac{3}{4} = 3/4$。\n因此，直線的斜率為 3/4。",
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
        "3/4"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(4, 4)$ 與 $B(9, -5)$ 的直線斜率。",
    "answer": "-9/5",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(4, 4)$ 與 $B(9, -5)$ 代入公式中：",
      "$m = \\frac{-5 - (4)}{9 - (4)}$",
      "$m = \\frac{-9}{5} = -9/5$。",
      "因此，直線的斜率為 -9/5。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s1",
      "parameter_signature": "variant=1:answer=-9/5",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(4, 4)$ 與 $B(9, -5)$ 的直線斜率。",
    "correct_answer": "-9/5",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(4, 4)$ 與 $B(9, -5)$ 代入公式中：\n$m = \\frac{-5 - (4)}{9 - (4)}$\n$m = \\frac{-9}{5} = -9/5$。\n因此，直線的斜率為 -9/5。",
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
        "-9/5"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "若直線通過點 $A(-9, a)$ 與 $B(-4, -2)$，且其斜率為 1，試求 $a$ 之值。",
    "answer": "-7",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "根據直線斜率公式，斜率 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-9, a)$ 與 $B(-4, -2)$ 以及斜率 $m = 1$ 代入：",
      "$1 = \\frac{-2 - a}{-4 - (-9)}$",
      "$1 = \\frac{-2 - a}{5}$",
      "兩邊同乘以 5 得：",
      "$5 = -2 - a$",
      "解得 $a = -2 - (5) = -7$。",
      "因此，$a$ 的值為 -7。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s6",
      "parameter_signature": "variant=2:answer=-7",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "若直線通過點 $A(-9, a)$ 與 $B(-4, -2)$，且其斜率為 1，試求 $a$ 之值。",
    "correct_answer": "-7",
    "explanation": "根據直線斜率公式，斜率 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-9, a)$ 與 $B(-4, -2)$ 以及斜率 $m = 1$ 代入：\n$1 = \\frac{-2 - a}{-4 - (-9)}$\n$1 = \\frac{-2 - a}{5}$\n兩邊同乘以 5 得：\n$5 = -2 - a$\n解得 $a = -2 - (5) = -7$。\n因此，$a$ 的值為 -7。",
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
        "-7"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  },
  {
    "problem_type_id": "text_short_slope_of_line_problems",
    "skill_id": "vh_數學B1_SlopeOfALine",
    "subskill_id": "text_short_slope_of_line_problems",
    "question_text": "試求過兩點 $A(-8, 7)$ 與 $B(-11, -6)$ 的直線斜率。",
    "answer": "13/3",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "solution_steps": [
      "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。",
      "將點 $A(-8, 7)$ 與 $B(-11, -6)$ 代入公式中：",
      "$m = \\frac{-6 - (7)}{-11 - (-8)}$",
      "$m = \\frac{-13}{-3} = 13/3$。",
      "因此，直線的斜率為 13/3。"
    ],
    "metadata": {
      "scenario_family": "text_short_slope_of_line_problems",
      "scenario_id": "s5",
      "parameter_signature": "variant=1:answer=13/3",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "slope_calculation",
        "collinearity"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "text_short_slope_of_line_problems"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "試求過兩點 $A(-8, 7)$ 與 $B(-11, -6)$ 的直線斜率。",
    "correct_answer": "13/3",
    "explanation": "已知過兩點 $A(x_1, y_1)$ 與 $B(x_2, y_2)$ 的直線斜率公式為 $m = \\frac{y_2 - y_1}{x_2 - x_1}$。\n將點 $A(-8, 7)$ 與 $B(-11, -6)$ 代入公式中：\n$m = \\frac{-6 - (7)}{-11 - (-8)}$\n$m = \\frac{-13}{-3} = 13/3$。\n因此，直線的斜率為 13/3。",
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
        "13/3"
      ],
      "checker_key": "rational_checker",
      "equivalence_type": "rational_equivalent"
    }
  }
]
```
