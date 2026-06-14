# Verify Report: vh_數學B1_PropertiesOfParallelLines

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
    "parallel_lines_properties"
  ],
  "observed_problem_types": [
    "parallel_lines_properties"
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
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_2_1/parallel_lines_properties/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "integer",
    "checker_type": "integer_checker"
  }
]
```

## Pytest Output
```text
.....                                                                    [100%]
5 passed in 0.12s
```

## Samples
```json
[
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( 3,-4 \\right)$、$B\\left( 5,-8 \\right)$、$C\\left( -4,-4 \\right)$、$D\\left( -5,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "answer": "-2",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{-8 - (-4)}{5 - (3)} = -2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a + 4}{-5 - (-4)} = \\frac{a + 4}{-1}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{a + 4}{-1} = -2$，",
      "所以 $a + 4 = 2$，解得 a = -2。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s2",
      "parameter_signature": "m=-2:template=1:answer=-2",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 3,-4 \\right)$、$B\\left( 5,-8 \\right)$、$C\\left( -4,-4 \\right)$、$D\\left( -5,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "correct_answer": "-2",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{-8 - (-4)}{5 - (3)} = -2$。\n直線CD的斜率為 $m_{CD} = \\frac{a + 4}{-5 - (-4)} = \\frac{a + 4}{-1}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{a + 4}{-1} = -2$，\n所以 $a + 4 = 2$，解得 a = -2。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "-2"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "平面上過兩點$\\left( 0,-4 \\right)$、$\\left( 2,-6 \\right)$的直線和過另兩點$\\left( -5,2 \\right)$、$\\left( -7,x \\right)$的直線平行，則x = ",
    "answer": "4",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為兩直線平行，所以它們的斜率相等。",
      "第一條直線的斜率為 $m_1 = \\frac{-6 - (-4)}{2 - (0)} = -1$。",
      "第二條直線的斜率為 $m_2 = \\frac{x - 2}{-7 - (-5)} = \\frac{x - 2}{-2}$。",
      "由 $m_1 = m_2$ 可得：$\\frac{x - 2}{-2} = -1$，",
      "所以 $x - 2 = 2$，解得 x = 4。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s1",
      "parameter_signature": "m=-1:template=3:answer=4",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "平面上過兩點$\\left( 0,-4 \\right)$、$\\left( 2,-6 \\right)$的直線和過另兩點$\\left( -5,2 \\right)$、$\\left( -7,x \\right)$的直線平行，則x = ",
    "correct_answer": "4",
    "explanation": "因為兩直線平行，所以它們的斜率相等。\n第一條直線的斜率為 $m_1 = \\frac{-6 - (-4)}{2 - (0)} = -1$。\n第二條直線的斜率為 $m_2 = \\frac{x - 2}{-7 - (-5)} = \\frac{x - 2}{-2}$。\n由 $m_1 = m_2$ 可得：$\\frac{x - 2}{-2} = -1$，\n所以 $x - 2 = 2$，解得 x = 4。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "4"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( 1,-2 \\right)$、$B\\left( -2,1 \\right)$、$C\\left( -1,a \\right)$、$D\\left( 1,-2 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "answer": "0",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{1 - (-2)}{-2 - (1)} = -1$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-2 - a}{1 - (-1)} = \\frac{-2 - a}{2}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{-2 - a}{2} = -1$，",
      "所以 $-2 - a = -2$，解得 a = 0。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s3",
      "parameter_signature": "m=-1:template=2:answer=0",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 1,-2 \\right)$、$B\\left( -2,1 \\right)$、$C\\left( -1,a \\right)$、$D\\left( 1,-2 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "correct_answer": "0",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{1 - (-2)}{-2 - (1)} = -1$。\n直線CD的斜率為 $m_{CD} = \\frac{-2 - a}{1 - (-1)} = \\frac{-2 - a}{2}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{-2 - a}{2} = -1$，\n所以 $-2 - a = -2$，解得 a = 0。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "0"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( 2,4 \\right)$、$B\\left( 0,10 \\right)$、$C\\left( -3,2 \\right)$、$D\\left( -5,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "answer": "8",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{10 - (4)}{0 - (2)} = -3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - 2}{-5 - (-3)} = \\frac{a - 2}{-2}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{a - 2}{-2} = -3$，",
      "所以 $a - 2 = 6$，解得 a = 8。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s2",
      "parameter_signature": "m=-3:template=1:answer=8",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 2,4 \\right)$、$B\\left( 0,10 \\right)$、$C\\left( -3,2 \\right)$、$D\\left( -5,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "correct_answer": "8",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{10 - (4)}{0 - (2)} = -3$。\n直線CD的斜率為 $m_{CD} = \\frac{a - 2}{-5 - (-3)} = \\frac{a - 2}{-2}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{a - 2}{-2} = -3$，\n所以 $a - 2 = 6$，解得 a = 8。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "8"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "平面上過兩點$\\left( -3,-4 \\right)$、$\\left( -5,-2 \\right)$的直線和過另兩點$\\left( 1,-4 \\right)$、$\\left( -2,a \\right)$的直線平行，則a = ",
    "answer": "-1",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為兩直線平行，所以它們的斜率相等。",
      "第一條直線的斜率為 $m_1 = \\frac{-2 - (-4)}{-5 - (-3)} = -1$。",
      "第二條直線的斜率為 $m_2 = \\frac{a + 4}{-2 - (1)} = \\frac{a + 4}{-3}$。",
      "由 $m_1 = m_2$ 可得：$\\frac{a + 4}{-3} = -1$，",
      "所以 $a + 4 = 3$，解得 a = -1。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s6",
      "parameter_signature": "m=-1:template=3:answer=-1",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "平面上過兩點$\\left( -3,-4 \\right)$、$\\left( -5,-2 \\right)$的直線和過另兩點$\\left( 1,-4 \\right)$、$\\left( -2,a \\right)$的直線平行，則a = ",
    "correct_answer": "-1",
    "explanation": "因為兩直線平行，所以它們的斜率相等。\n第一條直線的斜率為 $m_1 = \\frac{-2 - (-4)}{-5 - (-3)} = -1$。\n第二條直線的斜率為 $m_2 = \\frac{a + 4}{-2 - (1)} = \\frac{a + 4}{-3}$。\n由 $m_1 = m_2$ 可得：$\\frac{a + 4}{-3} = -1$，\n所以 $a + 4 = 3$，解得 a = -1。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "-1"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( 5,-3 \\right)$、$B\\left( 7,-5 \\right)$、$C\\left( -3,x \\right)$、$D\\left( 0,-3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "answer": "0",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{-5 - (-3)}{7 - (5)} = -1$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-3 - x}{0 - (-3)} = \\frac{-3 - x}{3}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{-3 - x}{3} = -1$，",
      "所以 $-3 - x = -3$，解得 x = 0。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s1",
      "parameter_signature": "m=-1:template=2:answer=0",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 5,-3 \\right)$、$B\\left( 7,-5 \\right)$、$C\\left( -3,x \\right)$、$D\\left( 0,-3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "correct_answer": "0",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{-5 - (-3)}{7 - (5)} = -1$。\n直線CD的斜率為 $m_{CD} = \\frac{-3 - x}{0 - (-3)} = \\frac{-3 - x}{3}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{-3 - x}{3} = -1$，\n所以 $-3 - x = -3$，解得 x = 0。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "0"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( -5,-2 \\right)$、$B\\left( -6,-1 \\right)$、$C\\left( 0,x \\right)$、$D\\left( 1,-3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "answer": "-2",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{-1 - (-2)}{-6 - (-5)} = -1$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-3 - x}{1 - (0)} = \\frac{-3 - x}{1}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{-3 - x}{1} = -1$，",
      "所以 $-3 - x = -1$，解得 x = -2。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s6",
      "parameter_signature": "m=-1:template=2:answer=-2",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -5,-2 \\right)$、$B\\left( -6,-1 \\right)$、$C\\left( 0,x \\right)$、$D\\left( 1,-3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "correct_answer": "-2",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{-1 - (-2)}{-6 - (-5)} = -1$。\n直線CD的斜率為 $m_{CD} = \\frac{-3 - x}{1 - (0)} = \\frac{-3 - x}{1}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{-3 - x}{1} = -1$，\n所以 $-3 - x = -1$，解得 x = -2。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "-2"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "平面上過兩點$\\left( 3,-3 \\right)$、$\\left( 0,6 \\right)$的直線和過另兩點$\\left( -1,-4 \\right)$、$\\left( 1,x \\right)$的直線平行，則x = ",
    "answer": "-10",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為兩直線平行，所以它們的斜率相等。",
      "第一條直線的斜率為 $m_1 = \\frac{6 - (-3)}{0 - (3)} = -3$。",
      "第二條直線的斜率為 $m_2 = \\frac{x + 4}{1 - (-1)} = \\frac{x + 4}{2}$。",
      "由 $m_1 = m_2$ 可得：$\\frac{x + 4}{2} = -3$，",
      "所以 $x + 4 = -6$，解得 x = -10。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m=-3:template=3:answer=-10",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "平面上過兩點$\\left( 3,-3 \\right)$、$\\left( 0,6 \\right)$的直線和過另兩點$\\left( -1,-4 \\right)$、$\\left( 1,x \\right)$的直線平行，則x = ",
    "correct_answer": "-10",
    "explanation": "因為兩直線平行，所以它們的斜率相等。\n第一條直線的斜率為 $m_1 = \\frac{6 - (-3)}{0 - (3)} = -3$。\n第二條直線的斜率為 $m_2 = \\frac{x + 4}{1 - (-1)} = \\frac{x + 4}{2}$。\n由 $m_1 = m_2$ 可得：$\\frac{x + 4}{2} = -3$，\n所以 $x + 4 = -6$，解得 x = -10。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "-10"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( -5,0 \\right)$、$B\\left( -2,6 \\right)$、$C\\left( 0,-2 \\right)$、$D\\left( 3,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "answer": "4",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{6 - (0)}{-2 - (-5)} = 2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{x + 2}{3 - (0)} = \\frac{x + 2}{3}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{x + 2}{3} = 2$，",
      "所以 $x + 2 = 6$，解得 x = 4。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s1",
      "parameter_signature": "m=2:template=1:answer=4",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -5,0 \\right)$、$B\\left( -2,6 \\right)$、$C\\left( 0,-2 \\right)$、$D\\left( 3,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "correct_answer": "4",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{6 - (0)}{-2 - (-5)} = 2$。\n直線CD的斜率為 $m_{CD} = \\frac{x + 2}{3 - (0)} = \\frac{x + 2}{3}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{x + 2}{3} = 2$，\n所以 $x + 2 = 6$，解得 x = 4。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "4"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( 5,-1 \\right)$、$B\\left( 7,-5 \\right)$、$C\\left( 3,x \\right)$、$D\\left( 1,6 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "answer": "2",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{-5 - (-1)}{7 - (5)} = -2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{6 - x}{1 - (3)} = \\frac{6 - x}{-2}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{6 - x}{-2} = -2$，",
      "所以 $6 - x = 4$，解得 x = 2。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m=-2:template=2:answer=2",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 5,-1 \\right)$、$B\\left( 7,-5 \\right)$、$C\\left( 3,x \\right)$、$D\\left( 1,6 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "correct_answer": "2",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{-5 - (-1)}{7 - (5)} = -2$。\n直線CD的斜率為 $m_{CD} = \\frac{6 - x}{1 - (3)} = \\frac{6 - x}{-2}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{6 - x}{-2} = -2$，\n所以 $6 - x = 4$，解得 x = 2。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "2"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( -4,4 \\right)$、$B\\left( -2,6 \\right)$、$C\\left( -1,5 \\right)$、$D\\left( 2,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "answer": "8",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{6 - (4)}{-2 - (-4)} = 1$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - 5}{2 - (-1)} = \\frac{a - 5}{3}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{a - 5}{3} = 1$，",
      "所以 $a - 5 = 3$，解得 a = 8。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s3",
      "parameter_signature": "m=1:template=1:answer=8",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -4,4 \\right)$、$B\\left( -2,6 \\right)$、$C\\left( -1,5 \\right)$、$D\\left( 2,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "correct_answer": "8",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{6 - (4)}{-2 - (-4)} = 1$。\n直線CD的斜率為 $m_{CD} = \\frac{a - 5}{2 - (-1)} = \\frac{a - 5}{3}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{a - 5}{3} = 1$，\n所以 $a - 5 = 3$，解得 a = 8。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "8"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "平面上過兩點$\\left( 4,0 \\right)$、$\\left( 2,4 \\right)$的直線和過另兩點$\\left( 0,2 \\right)$、$\\left( -2,a \\right)$的直線平行，則a = ",
    "answer": "6",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為兩直線平行，所以它們的斜率相等。",
      "第一條直線的斜率為 $m_1 = \\frac{4 - (0)}{2 - (4)} = -2$。",
      "第二條直線的斜率為 $m_2 = \\frac{a - 2}{-2 - (0)} = \\frac{a - 2}{-2}$。",
      "由 $m_1 = m_2$ 可得：$\\frac{a - 2}{-2} = -2$，",
      "所以 $a - 2 = 4$，解得 a = 6。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s2",
      "parameter_signature": "m=-2:template=3:answer=6",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "平面上過兩點$\\left( 4,0 \\right)$、$\\left( 2,4 \\right)$的直線和過另兩點$\\left( 0,2 \\right)$、$\\left( -2,a \\right)$的直線平行，則a = ",
    "correct_answer": "6",
    "explanation": "因為兩直線平行，所以它們的斜率相等。\n第一條直線的斜率為 $m_1 = \\frac{4 - (0)}{2 - (4)} = -2$。\n第二條直線的斜率為 $m_2 = \\frac{a - 2}{-2 - (0)} = \\frac{a - 2}{-2}$。\n由 $m_1 = m_2$ 可得：$\\frac{a - 2}{-2} = -2$，\n所以 $a - 2 = 4$，解得 a = 6。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "6"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( 0,1 \\right)$、$B\\left( -1,4 \\right)$、$C\\left( 2,5 \\right)$、$D\\left( 1,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "answer": "8",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{4 - (1)}{-1 - (0)} = -3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - 5}{1 - (2)} = \\frac{a - 5}{-1}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{a - 5}{-1} = -3$，",
      "所以 $a - 5 = 3$，解得 a = 8。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m=-3:template=1:answer=8",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 0,1 \\right)$、$B\\left( -1,4 \\right)$、$C\\left( 2,5 \\right)$、$D\\left( 1,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "correct_answer": "8",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{4 - (1)}{-1 - (0)} = -3$。\n直線CD的斜率為 $m_{CD} = \\frac{a - 5}{1 - (2)} = \\frac{a - 5}{-1}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{a - 5}{-1} = -3$，\n所以 $a - 5 = 3$，解得 a = 8。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "8"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( -4,-3 \\right)$、$B\\left( -1,6 \\right)$、$C\\left( 5,1 \\right)$、$D\\left( 6,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "answer": "4",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{6 - (-3)}{-1 - (-4)} = 3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - 1}{6 - (5)} = \\frac{a - 1}{1}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{a - 1}{1} = 3$，",
      "所以 $a - 1 = 3$，解得 a = 4。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s4",
      "parameter_signature": "m=3:template=1:answer=4",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -4,-3 \\right)$、$B\\left( -1,6 \\right)$、$C\\left( 5,1 \\right)$、$D\\left( 6,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "correct_answer": "4",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{6 - (-3)}{-1 - (-4)} = 3$。\n直線CD的斜率為 $m_{CD} = \\frac{a - 1}{6 - (5)} = \\frac{a - 1}{1}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{a - 1}{1} = 3$，\n所以 $a - 1 = 3$，解得 a = 4。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "4"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( -2,-3 \\right)$、$B\\left( 1,-9 \\right)$、$C\\left( -3,a \\right)$、$D\\left( -5,1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "answer": "-3",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{-9 - (-3)}{1 - (-2)} = -2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{1 - a}{-5 - (-3)} = \\frac{1 - a}{-2}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{1 - a}{-2} = -2$，",
      "所以 $1 - a = 4$，解得 a = -3。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m=-2:template=2:answer=-3",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -2,-3 \\right)$、$B\\left( 1,-9 \\right)$、$C\\left( -3,a \\right)$、$D\\left( -5,1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "correct_answer": "-3",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{-9 - (-3)}{1 - (-2)} = -2$。\n直線CD的斜率為 $m_{CD} = \\frac{1 - a}{-5 - (-3)} = \\frac{1 - a}{-2}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{1 - a}{-2} = -2$，\n所以 $1 - a = 4$，解得 a = -3。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "-3"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( -3,0 \\right)$、$B\\left( -6,3 \\right)$、$C\\left( 4,x \\right)$、$D\\left( 5,-1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "answer": "0",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{3 - (0)}{-6 - (-3)} = -1$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-1 - x}{5 - (4)} = \\frac{-1 - x}{1}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{-1 - x}{1} = -1$，",
      "所以 $-1 - x = -1$，解得 x = 0。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m=-1:template=2:answer=0",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -3,0 \\right)$、$B\\left( -6,3 \\right)$、$C\\left( 4,x \\right)$、$D\\left( 5,-1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "correct_answer": "0",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{3 - (0)}{-6 - (-3)} = -1$。\n直線CD的斜率為 $m_{CD} = \\frac{-1 - x}{5 - (4)} = \\frac{-1 - x}{1}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{-1 - x}{1} = -1$，\n所以 $-1 - x = -1$，解得 x = 0。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "0"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "平面上過兩點$\\left( -4,0 \\right)$、$\\left( -2,4 \\right)$的直線和過另兩點$\\left( 2,1 \\right)$、$\\left( 0,a \\right)$的直線平行，則a = ",
    "answer": "-3",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為兩直線平行，所以它們的斜率相等。",
      "第一條直線的斜率為 $m_1 = \\frac{4 - (0)}{-2 - (-4)} = 2$。",
      "第二條直線的斜率為 $m_2 = \\frac{a - 1}{0 - (2)} = \\frac{a - 1}{-2}$。",
      "由 $m_1 = m_2$ 可得：$\\frac{a - 1}{-2} = 2$，",
      "所以 $a - 1 = -4$，解得 a = -3。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s1",
      "parameter_signature": "m=2:template=3:answer=-3",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "平面上過兩點$\\left( -4,0 \\right)$、$\\left( -2,4 \\right)$的直線和過另兩點$\\left( 2,1 \\right)$、$\\left( 0,a \\right)$的直線平行，則a = ",
    "correct_answer": "-3",
    "explanation": "因為兩直線平行，所以它們的斜率相等。\n第一條直線的斜率為 $m_1 = \\frac{4 - (0)}{-2 - (-4)} = 2$。\n第二條直線的斜率為 $m_2 = \\frac{a - 1}{0 - (2)} = \\frac{a - 1}{-2}$。\n由 $m_1 = m_2$ 可得：$\\frac{a - 1}{-2} = 2$，\n所以 $a - 1 = -4$，解得 a = -3。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "-3"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( 0,-1 \\right)$、$B\\left( 1,-2 \\right)$、$C\\left( -4,a \\right)$、$D\\left( -2,-2 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "answer": "0",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{-2 - (-1)}{1 - (0)} = -1$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-2 - a}{-2 - (-4)} = \\frac{-2 - a}{2}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{-2 - a}{2} = -1$，",
      "所以 $-2 - a = -2$，解得 a = 0。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s3",
      "parameter_signature": "m=-1:template=2:answer=0",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 0,-1 \\right)$、$B\\left( 1,-2 \\right)$、$C\\left( -4,a \\right)$、$D\\left( -2,-2 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "correct_answer": "0",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{-2 - (-1)}{1 - (0)} = -1$。\n直線CD的斜率為 $m_{CD} = \\frac{-2 - a}{-2 - (-4)} = \\frac{-2 - a}{2}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{-2 - a}{2} = -1$，\n所以 $-2 - a = -2$，解得 a = 0。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "0"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( -5,2 \\right)$、$B\\left( -4,4 \\right)$、$C\\left( 3,-4 \\right)$、$D\\left( 5,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "answer": "0",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{4 - (2)}{-4 - (-5)} = 2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a + 4}{5 - (3)} = \\frac{a + 4}{2}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{a + 4}{2} = 2$，",
      "所以 $a + 4 = 4$，解得 a = 0。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m=2:template=1:answer=0",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -5,2 \\right)$、$B\\left( -4,4 \\right)$、$C\\left( 3,-4 \\right)$、$D\\left( 5,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "correct_answer": "0",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{4 - (2)}{-4 - (-5)} = 2$。\n直線CD的斜率為 $m_{CD} = \\frac{a + 4}{5 - (3)} = \\frac{a + 4}{2}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{a + 4}{2} = 2$，\n所以 $a + 4 = 4$，解得 a = 0。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "0"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( -1,5 \\right)$、$B\\left( 2,14 \\right)$、$C\\left( 3,-3 \\right)$、$D\\left( 6,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "answer": "6",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{14 - (5)}{2 - (-1)} = 3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{x + 3}{6 - (3)} = \\frac{x + 3}{3}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{x + 3}{3} = 3$，",
      "所以 $x + 3 = 9$，解得 x = 6。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s7",
      "parameter_signature": "m=3:template=1:answer=6",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -1,5 \\right)$、$B\\left( 2,14 \\right)$、$C\\left( 3,-3 \\right)$、$D\\left( 6,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "correct_answer": "6",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{14 - (5)}{2 - (-1)} = 3$。\n直線CD的斜率為 $m_{CD} = \\frac{x + 3}{6 - (3)} = \\frac{x + 3}{3}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{x + 3}{3} = 3$，\n所以 $x + 3 = 9$，解得 x = 6。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "6"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( 2,-1 \\right)$、$B\\left( 4,3 \\right)$、$C\\left( -3,3 \\right)$、$D\\left( -4,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "answer": "1",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{3 - (-1)}{4 - (2)} = 2$。",
      "直線CD的斜率為 $m_{CD} = \\frac{a - 3}{-4 - (-3)} = \\frac{a - 3}{-1}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{a - 3}{-1} = 2$，",
      "所以 $a - 3 = -2$，解得 a = 1。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s4",
      "parameter_signature": "m=2:template=1:answer=1",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 2,-1 \\right)$、$B\\left( 4,3 \\right)$、$C\\left( -3,3 \\right)$、$D\\left( -4,a \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求a之值。",
    "correct_answer": "1",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{3 - (-1)}{4 - (2)} = 2$。\n直線CD的斜率為 $m_{CD} = \\frac{a - 3}{-4 - (-3)} = \\frac{a - 3}{-1}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{a - 3}{-1} = 2$，\n所以 $a - 3 = -2$，解得 a = 1。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "1"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( 2,-1 \\right)$、$B\\left( 3,-4 \\right)$、$C\\left( -1,x \\right)$、$D\\left( -3,3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "answer": "-3",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{-4 - (-1)}{3 - (2)} = -3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{3 - x}{-3 - (-1)} = \\frac{3 - x}{-2}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{3 - x}{-2} = -3$，",
      "所以 $3 - x = 6$，解得 x = -3。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s5",
      "parameter_signature": "m=-3:template=2:answer=-3",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 2,-1 \\right)$、$B\\left( 3,-4 \\right)$、$C\\left( -1,x \\right)$、$D\\left( -3,3 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "correct_answer": "-3",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{-4 - (-1)}{3 - (2)} = -3$。\n直線CD的斜率為 $m_{CD} = \\frac{3 - x}{-3 - (-1)} = \\frac{3 - x}{-2}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{3 - x}{-2} = -3$，\n所以 $3 - x = 6$，解得 x = -3。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "-3"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( 3,-3 \\right)$、$B\\left( 1,3 \\right)$、$C\\left( 0,3 \\right)$、$D\\left( -3,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "answer": "12",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{3 - (-3)}{1 - (3)} = -3$。",
      "直線CD的斜率為 $m_{CD} = \\frac{x - 3}{-3 - (0)} = \\frac{x - 3}{-3}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{x - 3}{-3} = -3$，",
      "所以 $x - 3 = 9$，解得 x = 12。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m=-3:template=1:answer=12",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( 3,-3 \\right)$、$B\\left( 1,3 \\right)$、$C\\left( 0,3 \\right)$、$D\\left( -3,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "correct_answer": "12",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{3 - (-3)}{1 - (3)} = -3$。\n直線CD的斜率為 $m_{CD} = \\frac{x - 3}{-3 - (0)} = \\frac{x - 3}{-3}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{x - 3}{-3} = -3$，\n所以 $x - 3 = 9$，解得 x = 12。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "12"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "平面上過兩點$\\left( -1,-2 \\right)$、$\\left( -3,4 \\right)$的直線和過另兩點$\\left( 4,-3 \\right)$、$\\left( 7,a \\right)$的直線平行，則a = ",
    "answer": "-12",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為兩直線平行，所以它們的斜率相等。",
      "第一條直線的斜率為 $m_1 = \\frac{4 - (-2)}{-3 - (-1)} = -3$。",
      "第二條直線的斜率為 $m_2 = \\frac{a + 3}{7 - (4)} = \\frac{a + 3}{3}$。",
      "由 $m_1 = m_2$ 可得：$\\frac{a + 3}{3} = -3$，",
      "所以 $a + 3 = -9$，解得 a = -12。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s8",
      "parameter_signature": "m=-3:template=3:answer=-12",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "平面上過兩點$\\left( -1,-2 \\right)$、$\\left( -3,4 \\right)$的直線和過另兩點$\\left( 4,-3 \\right)$、$\\left( 7,a \\right)$的直線平行，則a = ",
    "correct_answer": "-12",
    "explanation": "因為兩直線平行，所以它們的斜率相等。\n第一條直線的斜率為 $m_1 = \\frac{4 - (-2)}{-3 - (-1)} = -3$。\n第二條直線的斜率為 $m_2 = \\frac{a + 3}{7 - (4)} = \\frac{a + 3}{3}$。\n由 $m_1 = m_2$ 可得：$\\frac{a + 3}{3} = -3$，\n所以 $a + 3 = -9$，解得 a = -12。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "-12"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( -5,3 \\right)$、$B\\left( -7,1 \\right)$、$C\\left( 1,2 \\right)$、$D\\left( -2,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "answer": "-1",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{1 - (3)}{-7 - (-5)} = 1$。",
      "直線CD的斜率為 $m_{CD} = \\frac{x - 2}{-2 - (1)} = \\frac{x - 2}{-3}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{x - 2}{-3} = 1$，",
      "所以 $x - 2 = -3$，解得 x = -1。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s1",
      "parameter_signature": "m=1:template=1:answer=-1",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -5,3 \\right)$、$B\\left( -7,1 \\right)$、$C\\left( 1,2 \\right)$、$D\\left( -2,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "correct_answer": "-1",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{1 - (3)}{-7 - (-5)} = 1$。\n直線CD的斜率為 $m_{CD} = \\frac{x - 2}{-2 - (1)} = \\frac{x - 2}{-3}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{x - 2}{-3} = 1$，\n所以 $x - 2 = -3$，解得 x = -1。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "-1"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( -3,5 \\right)$、$B\\left( -6,2 \\right)$、$C\\left( -2,-1 \\right)$、$D\\left( -5,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "answer": "-4",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{2 - (5)}{-6 - (-3)} = 1$。",
      "直線CD的斜率為 $m_{CD} = \\frac{x + 1}{-5 - (-2)} = \\frac{x + 1}{-3}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{x + 1}{-3} = 1$，",
      "所以 $x + 1 = -3$，解得 x = -4。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s2",
      "parameter_signature": "m=1:template=1:answer=-4",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -3,5 \\right)$、$B\\left( -6,2 \\right)$、$C\\left( -2,-1 \\right)$、$D\\left( -5,x \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "correct_answer": "-4",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{2 - (5)}{-6 - (-3)} = 1$。\n直線CD的斜率為 $m_{CD} = \\frac{x + 1}{-5 - (-2)} = \\frac{x + 1}{-3}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{x + 1}{-3} = 1$，\n所以 $x + 1 = -3$，解得 x = -4。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "-4"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "平面上過兩點$\\left( 1,1 \\right)$、$\\left( 2,-2 \\right)$的直線和過另兩點$\\left( -2,4 \\right)$、$\\left( -4,x \\right)$的直線平行，則x = ",
    "answer": "10",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為兩直線平行，所以它們的斜率相等。",
      "第一條直線的斜率為 $m_1 = \\frac{-2 - (1)}{2 - (1)} = -3$。",
      "第二條直線的斜率為 $m_2 = \\frac{x - 4}{-4 - (-2)} = \\frac{x - 4}{-2}$。",
      "由 $m_1 = m_2$ 可得：$\\frac{x - 4}{-2} = -3$，",
      "所以 $x - 4 = 6$，解得 x = 10。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s5",
      "parameter_signature": "m=-3:template=3:answer=10",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "平面上過兩點$\\left( 1,1 \\right)$、$\\left( 2,-2 \\right)$的直線和過另兩點$\\left( -2,4 \\right)$、$\\left( -4,x \\right)$的直線平行，則x = ",
    "correct_answer": "10",
    "explanation": "因為兩直線平行，所以它們的斜率相等。\n第一條直線的斜率為 $m_1 = \\frac{-2 - (1)}{2 - (1)} = -3$。\n第二條直線的斜率為 $m_2 = \\frac{x - 4}{-4 - (-2)} = \\frac{x - 4}{-2}$。\n由 $m_1 = m_2$ 可得：$\\frac{x - 4}{-2} = -3$，\n所以 $x - 4 = 6$，解得 x = 10。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "10"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "平面上過兩點$\\left( -5,-3 \\right)$、$\\left( -3,-1 \\right)$的直線和過另兩點$\\left( -1,2 \\right)$、$\\left( 2,x \\right)$的直線平行，則x = ",
    "answer": "5",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為兩直線平行，所以它們的斜率相等。",
      "第一條直線的斜率為 $m_1 = \\frac{-1 - (-3)}{-3 - (-5)} = 1$。",
      "第二條直線的斜率為 $m_2 = \\frac{x - 2}{2 - (-1)} = \\frac{x - 2}{3}$。",
      "由 $m_1 = m_2$ 可得：$\\frac{x - 2}{3} = 1$，",
      "所以 $x - 2 = 3$，解得 x = 5。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s9",
      "parameter_signature": "m=1:template=3:answer=5",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "平面上過兩點$\\left( -5,-3 \\right)$、$\\left( -3,-1 \\right)$的直線和過另兩點$\\left( -1,2 \\right)$、$\\left( 2,x \\right)$的直線平行，則x = ",
    "correct_answer": "5",
    "explanation": "因為兩直線平行，所以它們的斜率相等。\n第一條直線的斜率為 $m_1 = \\frac{-1 - (-3)}{-3 - (-5)} = 1$。\n第二條直線的斜率為 $m_2 = \\frac{x - 2}{2 - (-1)} = \\frac{x - 2}{3}$。\n由 $m_1 = m_2$ 可得：$\\frac{x - 2}{3} = 1$，\n所以 $x - 2 = 3$，解得 x = 5。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "5"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "平面上過兩點$\\left( 5,1 \\right)$、$\\left( 7,5 \\right)$的直線和過另兩點$\\left( -5,2 \\right)$、$\\left( -4,a \\right)$的直線平行，則a = ",
    "answer": "4",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為兩直線平行，所以它們的斜率相等。",
      "第一條直線的斜率為 $m_1 = \\frac{5 - (1)}{7 - (5)} = 2$。",
      "第二條直線的斜率為 $m_2 = \\frac{a - 2}{-4 - (-5)} = \\frac{a - 2}{1}$。",
      "由 $m_1 = m_2$ 可得：$\\frac{a - 2}{1} = 2$，",
      "所以 $a - 2 = 2$，解得 a = 4。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s2",
      "parameter_signature": "m=2:template=3:answer=4",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "平面上過兩點$\\left( 5,1 \\right)$、$\\left( 7,5 \\right)$的直線和過另兩點$\\left( -5,2 \\right)$、$\\left( -4,a \\right)$的直線平行，則a = ",
    "correct_answer": "4",
    "explanation": "因為兩直線平行，所以它們的斜率相等。\n第一條直線的斜率為 $m_1 = \\frac{5 - (1)}{7 - (5)} = 2$。\n第二條直線的斜率為 $m_2 = \\frac{a - 2}{-4 - (-5)} = \\frac{a - 2}{1}$。\n由 $m_1 = m_2$ 可得：$\\frac{a - 2}{1} = 2$，\n所以 $a - 2 = 2$，解得 a = 4。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "4"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  },
  {
    "problem_type_id": "parallel_lines_properties",
    "skill_id": "vh_數學B1_PropertiesOfParallelLines",
    "subskill_id": "parallel_lines_properties",
    "question_text": "設$A\\left( -1,5 \\right)$、$B\\left( 2,8 \\right)$、$C\\left( -2,x \\right)$、$D\\left( -5,-1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "answer": "2",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。",
      "直線AB的斜率為 $m_{AB} = \\frac{8 - (5)}{2 - (-1)} = 1$。",
      "直線CD的斜率為 $m_{CD} = \\frac{-1 - x}{-5 - (-2)} = \\frac{-1 - x}{-3}$。",
      "由 $m_{AB} = m_{CD}$ 可得：$\\frac{-1 - x}{-3} = 1$，",
      "所以 $-1 - x = -3$，解得 x = 2。"
    ],
    "metadata": {
      "scenario_family": "parallel_lines_properties",
      "scenario_id": "s5",
      "parameter_signature": "m=1:template=2:answer=2",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "parallel_lines_slope_equality"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "parallel_lines_properties"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "question": "設$A\\left( -1,5 \\right)$、$B\\left( 2,8 \\right)$、$C\\left( -2,x \\right)$、$D\\left( -5,-1 \\right)$，若$\\overline{AB}$與$\\overline{CD}$平行，試求x之值。",
    "correct_answer": "2",
    "explanation": "因為$\\overline{AB}$與$\\overline{CD}$平行，所以它們的斜率相等。\n直線AB的斜率為 $m_{AB} = \\frac{8 - (5)}{2 - (-1)} = 1$。\n直線CD的斜率為 $m_{CD} = \\frac{-1 - x}{-5 - (-2)} = \\frac{-1 - x}{-3}$。\n由 $m_{AB} = m_{CD}$ 可得：$\\frac{-1 - x}{-3} = 1$，\n所以 $-1 - x = -3$，解得 x = 2。",
    "choices": [],
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "answer_type": "integer",
      "answer_shape": "scalar",
      "answer_equivalence": "numeric_exact",
      "checker": "integer_checker",
      "accepted_formats": [
        "2"
      ],
      "checker_key": "integer_checker",
      "equivalence_type": "numeric_exact"
    }
  }
]
```
