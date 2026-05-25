# Verify Report: vh_數學B1_AbsoluteValue

- python: C:\Python314\python.exe
- registry: E:\Python\Mathproject_tvet_mathB\configs\generated_registry\b1_section_1_1_verified_registry.v0.1.yaml
- registry_verified_count: 4
- pytest_exit_code: 0
- unique_problem_type_count: 4
- PASS: True

## Runtime ProblemType Coverage
```json
{
  "expected_problem_types": [
    "absolute_value_distance_between_two_points",
    "absolute_value_distance_from_zero",
    "absolute_value_equation_basic",
    "absolute_value_numeric_evaluation"
  ],
  "observed_problem_types": [
    "absolute_value_distance_between_two_points",
    "absolute_value_distance_from_zero",
    "absolute_value_equation_basic",
    "absolute_value_numeric_evaluation"
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
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_numeric_evaluation/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "integer",
    "checker_type": "integer_checker"
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_distance_from_zero/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "choice",
    "checker_type": "choice_checker"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_distance_between_two_points/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "integer",
    "checker_type": "integer_checker"
  },
  {
    "problem_type_id": "absolute_value_equation_basic",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_equation_basic",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_equation_basic/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "text",
    "checker_type": "exact_string_checker"
  }
]
```

## Pytest Output
```text
...                                                                      [100%]
3 passed in 0.20s
```

## Samples
```json
[
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|4|$ 的值。",
    "answer": 4,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|4|=4$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s2",
      "parameter_signature": "absolute_value_numeric_evaluation:n=4:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|4|$ 的值。",
    "correct_answer": 4,
    "explanation": "絕對值表示與 0 的距離。\n$|4|=4$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-6|$ 的正確意義？",
    "choices": [
      "數線上 $-6$ 到 $0$ 的距離",
      "數線上 $6$ 到 $-6$ 的距離",
      "$-6$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-6$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-6|$ 表示 $-6$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s2",
      "parameter_signature": "absolute_value_distance_from_zero:n=-6:pattern=meaning",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-6|$ 的正確意義？",
    "correct_answer": "數線上 $-6$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-6|$ 表示 $-6$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(8)$、$B(7)$，試求 A、B 兩點的距離。",
    "answer": 1,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|7-(8)|=|-1|=1$。",
      "所以 A、B 兩點的距離為 $1$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s3",
      "parameter_signature": "absolute_value_distance_between_two_points:a=8:b=7:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_distance",
        "number_line_distance",
        "coordinate_difference"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position",
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "已知數線上兩點 $A(8)$、$B(7)$，試求 A、B 兩點的距離。",
    "correct_answer": 1,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|7-(8)|=|-1|=1$。\n所以 A、B 兩點的距離為 $1$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_equation_basic",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_equation_basic",
    "question_text": "解方程式 $|x|=15$。",
    "answer": "x=-15 或 x=15",
    "answer_type": "text",
    "checker_type": "exact_string_checker",
    "solution_steps": [
      "$|x|=15$ 表示 $x$ 到 $0$ 的距離為 $15$。",
      "因此 $x=-15$ 或 $x=15$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_equation_basic",
      "scenario_id": "s8",
      "parameter_signature": "absolute_value_equation_basic:n=15:difficulty=easy",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_equation",
        "two_solutions"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "解方程式 $|x|=15$。",
    "correct_answer": "x=-15 或 x=15",
    "explanation": "$|x|=15$ 表示 $x$ 到 $0$ 的距離為 $15$。\n因此 $x=-15$ 或 $x=15$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|-4|$ 的值。",
    "answer": 4,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|-4|=4$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s3",
      "parameter_signature": "absolute_value_numeric_evaluation:n=-4:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|-4|$ 的值。",
    "correct_answer": 4,
    "explanation": "絕對值表示與 0 的距離。\n$|-4|=4$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-19|$ 的正確意義？",
    "choices": [
      "數線上 $-19$ 到 $0$ 的距離",
      "數線上 $19$ 到 $-19$ 的距離",
      "$-19$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-19$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-19|$ 表示 $-19$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s3",
      "parameter_signature": "absolute_value_distance_from_zero:n=-19:pattern=meaning",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-19|$ 的正確意義？",
    "correct_answer": "數線上 $-19$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-19|$ 表示 $-19$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(6)$、$B(4)$，試求 A、B 兩點的距離。",
    "answer": 2,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|4-(6)|=|-2|=2$。",
      "所以 A、B 兩點的距離為 $2$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s4",
      "parameter_signature": "absolute_value_distance_between_two_points:a=6:b=4:difficulty=easy",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "absolute_value_distance",
        "number_line_distance",
        "coordinate_difference"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position",
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "已知數線上兩點 $A(6)$、$B(4)$，試求 A、B 兩點的距離。",
    "correct_answer": 2,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|4-(6)|=|-2|=2$。\n所以 A、B 兩點的距離為 $2$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_equation_basic",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_equation_basic",
    "question_text": "解方程式 $|x|=2$。",
    "answer": "x=-2 或 x=2",
    "answer_type": "text",
    "checker_type": "exact_string_checker",
    "solution_steps": [
      "$|x|=2$ 表示 $x$ 到 $0$ 的距離為 $2$。",
      "因此 $x=-2$ 或 $x=2$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_equation_basic",
      "scenario_id": "s6",
      "parameter_signature": "absolute_value_equation_basic:n=2:difficulty=easy",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_equation",
        "two_solutions"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "解方程式 $|x|=2$。",
    "correct_answer": "x=-2 或 x=2",
    "explanation": "$|x|=2$ 表示 $x$ 到 $0$ 的距離為 $2$。\n因此 $x=-2$ 或 $x=2$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|-5|$ 的值。",
    "answer": 5,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|-5|=5$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s3",
      "parameter_signature": "absolute_value_numeric_evaluation:n=-5:difficulty=easy",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|-5|$ 的值。",
    "correct_answer": 5,
    "explanation": "絕對值表示與 0 的距離。\n$|-5|=5$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-13|$ 的正確意義？",
    "choices": [
      "數線上 $-13$ 到 $0$ 的距離",
      "數線上 $13$ 到 $-13$ 的距離",
      "$-13$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-13$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-13|$ 表示 $-13$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s5",
      "parameter_signature": "absolute_value_distance_from_zero:n=-13:pattern=meaning",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-13|$ 的正確意義？",
    "correct_answer": "數線上 $-13$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-13|$ 表示 $-13$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(6)$、$B(-7)$，試求 A、B 兩點的距離。",
    "answer": 13,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|-7-(6)|=|-13|=13$。",
      "所以 A、B 兩點的距離為 $13$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s5",
      "parameter_signature": "absolute_value_distance_between_two_points:a=6:b=-7:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_distance",
        "number_line_distance",
        "coordinate_difference"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position",
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "已知數線上兩點 $A(6)$、$B(-7)$，試求 A、B 兩點的距離。",
    "correct_answer": 13,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|-7-(6)|=|-13|=13$。\n所以 A、B 兩點的距離為 $13$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_equation_basic",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_equation_basic",
    "question_text": "解方程式 $|x|=14$。",
    "answer": "x=-14 或 x=14",
    "answer_type": "text",
    "checker_type": "exact_string_checker",
    "solution_steps": [
      "$|x|=14$ 表示 $x$ 到 $0$ 的距離為 $14$。",
      "因此 $x=-14$ 或 $x=14$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_equation_basic",
      "scenario_id": "s4",
      "parameter_signature": "absolute_value_equation_basic:n=14:difficulty=easy",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_equation",
        "two_solutions"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "解方程式 $|x|=14$。",
    "correct_answer": "x=-14 或 x=14",
    "explanation": "$|x|=14$ 表示 $x$ 到 $0$ 的距離為 $14$。\n因此 $x=-14$ 或 $x=14$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|-1|$ 的值。",
    "answer": 1,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|-1|=1$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s6",
      "parameter_signature": "absolute_value_numeric_evaluation:n=-1:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|-1|$ 的值。",
    "correct_answer": 1,
    "explanation": "絕對值表示與 0 的距離。\n$|-1|=1$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-6|$ 的正確意義？",
    "choices": [
      "數線上 $-6$ 到 $0$ 的距離",
      "數線上 $6$ 到 $-6$ 的距離",
      "$-6$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-6$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-6|$ 表示 $-6$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s5",
      "parameter_signature": "absolute_value_distance_from_zero:n=-6:pattern=meaning",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-6|$ 的正確意義？",
    "correct_answer": "數線上 $-6$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-6|$ 表示 $-6$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(-5)$、$B(0)$，試求 A、B 兩點的距離。",
    "answer": 5,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|0-(-5)|=|5|=5$。",
      "所以 A、B 兩點的距離為 $5$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s1",
      "parameter_signature": "absolute_value_distance_between_two_points:a=-5:b=0:difficulty=easy",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_distance",
        "number_line_distance",
        "coordinate_difference"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position",
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "已知數線上兩點 $A(-5)$、$B(0)$，試求 A、B 兩點的距離。",
    "correct_answer": 5,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|0-(-5)|=|5|=5$。\n所以 A、B 兩點的距離為 $5$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_equation_basic",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_equation_basic",
    "question_text": "解方程式 $|x|=8$。",
    "answer": "x=-8 或 x=8",
    "answer_type": "text",
    "checker_type": "exact_string_checker",
    "solution_steps": [
      "$|x|=8$ 表示 $x$ 到 $0$ 的距離為 $8$。",
      "因此 $x=-8$ 或 $x=8$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_equation_basic",
      "scenario_id": "s9",
      "parameter_signature": "absolute_value_equation_basic:n=8:difficulty=easy",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "absolute_value_equation",
        "two_solutions"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "解方程式 $|x|=8$。",
    "correct_answer": "x=-8 或 x=8",
    "explanation": "$|x|=8$ 表示 $x$ 到 $0$ 的距離為 $8$。\n因此 $x=-8$ 或 $x=8$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|-10|$ 的值。",
    "answer": 10,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|-10|=10$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s7",
      "parameter_signature": "absolute_value_numeric_evaluation:n=-10:difficulty=easy",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|-10|$ 的值。",
    "correct_answer": 10,
    "explanation": "絕對值表示與 0 的距離。\n$|-10|=10$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-17|$ 的正確意義？",
    "choices": [
      "數線上 $-17$ 到 $0$ 的距離",
      "數線上 $17$ 到 $-17$ 的距離",
      "$-17$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-17$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-17|$ 表示 $-17$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s5",
      "parameter_signature": "absolute_value_distance_from_zero:n=-17:pattern=meaning",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-17|$ 的正確意義？",
    "correct_answer": "數線上 $-17$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-17|$ 表示 $-17$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(-5)$、$B(2)$，試求 A、B 兩點的距離。",
    "answer": 7,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|2-(-5)|=|7|=7$。",
      "所以 A、B 兩點的距離為 $7$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s6",
      "parameter_signature": "absolute_value_distance_between_two_points:a=-5:b=2:difficulty=easy",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_distance",
        "number_line_distance",
        "coordinate_difference"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position",
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "已知數線上兩點 $A(-5)$、$B(2)$，試求 A、B 兩點的距離。",
    "correct_answer": 7,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|2-(-5)|=|7|=7$。\n所以 A、B 兩點的距離為 $7$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_equation_basic",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_equation_basic",
    "question_text": "解方程式 $|x|=3$。",
    "answer": "x=-3 或 x=3",
    "answer_type": "text",
    "checker_type": "exact_string_checker",
    "solution_steps": [
      "$|x|=3$ 表示 $x$ 到 $0$ 的距離為 $3$。",
      "因此 $x=-3$ 或 $x=3$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_equation_basic",
      "scenario_id": "s2",
      "parameter_signature": "absolute_value_equation_basic:n=3:difficulty=easy",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_equation",
        "two_solutions"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "解方程式 $|x|=3$。",
    "correct_answer": "x=-3 或 x=3",
    "explanation": "$|x|=3$ 表示 $x$ 到 $0$ 的距離為 $3$。\n因此 $x=-3$ 或 $x=3$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|-19|$ 的值。",
    "answer": 19,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|-19|=19$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s5",
      "parameter_signature": "absolute_value_numeric_evaluation:n=-19:difficulty=easy",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|-19|$ 的值。",
    "correct_answer": 19,
    "explanation": "絕對值表示與 0 的距離。\n$|-19|=19$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-12|$ 的正確意義？",
    "choices": [
      "數線上 $-12$ 到 $0$ 的距離",
      "數線上 $12$ 到 $-12$ 的距離",
      "$-12$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-12$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-12|$ 表示 $-12$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s1",
      "parameter_signature": "absolute_value_distance_from_zero:n=-12:pattern=meaning",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-12|$ 的正確意義？",
    "correct_answer": "數線上 $-12$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-12|$ 表示 $-12$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(1)$、$B(7)$，試求 A、B 兩點的距離。",
    "answer": 6,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|7-(1)|=|6|=6$。",
      "所以 A、B 兩點的距離為 $6$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s4",
      "parameter_signature": "absolute_value_distance_between_two_points:a=1:b=7:difficulty=easy",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "absolute_value_distance",
        "number_line_distance",
        "coordinate_difference"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position",
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "已知數線上兩點 $A(1)$、$B(7)$，試求 A、B 兩點的距離。",
    "correct_answer": 6,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|7-(1)|=|6|=6$。\n所以 A、B 兩點的距離為 $6$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_equation_basic",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_equation_basic",
    "question_text": "解方程式 $|x|=5$。",
    "answer": "x=-5 或 x=5",
    "answer_type": "text",
    "checker_type": "exact_string_checker",
    "solution_steps": [
      "$|x|=5$ 表示 $x$ 到 $0$ 的距離為 $5$。",
      "因此 $x=-5$ 或 $x=5$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_equation_basic",
      "scenario_id": "s9",
      "parameter_signature": "absolute_value_equation_basic:n=5:difficulty=easy",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "absolute_value_equation",
        "two_solutions"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "解方程式 $|x|=5$。",
    "correct_answer": "x=-5 或 x=5",
    "explanation": "$|x|=5$ 表示 $x$ 到 $0$ 的距離為 $5$。\n因此 $x=-5$ 或 $x=5$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|3|$ 的值。",
    "answer": 3,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|3|=3$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s9",
      "parameter_signature": "absolute_value_numeric_evaluation:n=3:difficulty=easy",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|3|$ 的值。",
    "correct_answer": 3,
    "explanation": "絕對值表示與 0 的距離。\n$|3|=3$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-19|$ 的正確意義？",
    "choices": [
      "數線上 $-19$ 到 $0$ 的距離",
      "數線上 $19$ 到 $-19$ 的距離",
      "$-19$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-19$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-19|$ 表示 $-19$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s8",
      "parameter_signature": "absolute_value_distance_from_zero:n=-19:pattern=meaning",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-19|$ 的正確意義？",
    "correct_answer": "數線上 $-19$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-19|$ 表示 $-19$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(0)$、$B(6)$，試求 A、B 兩點的距離。",
    "answer": 6,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|6-(0)|=|6|=6$。",
      "所以 A、B 兩點的距離為 $6$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s7",
      "parameter_signature": "absolute_value_distance_between_two_points:a=0:b=6:difficulty=easy",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_distance",
        "number_line_distance",
        "coordinate_difference"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position",
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "已知數線上兩點 $A(0)$、$B(6)$，試求 A、B 兩點的距離。",
    "correct_answer": 6,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|6-(0)|=|6|=6$。\n所以 A、B 兩點的距離為 $6$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_equation_basic",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_equation_basic",
    "question_text": "解方程式 $|x|=8$。",
    "answer": "x=-8 或 x=8",
    "answer_type": "text",
    "checker_type": "exact_string_checker",
    "solution_steps": [
      "$|x|=8$ 表示 $x$ 到 $0$ 的距離為 $8$。",
      "因此 $x=-8$ 或 $x=8$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_equation_basic",
      "scenario_id": "s4",
      "parameter_signature": "absolute_value_equation_basic:n=8:difficulty=easy",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "absolute_value_equation",
        "two_solutions"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "解方程式 $|x|=8$。",
    "correct_answer": "x=-8 或 x=8",
    "explanation": "$|x|=8$ 表示 $x$ 到 $0$ 的距離為 $8$。\n因此 $x=-8$ 或 $x=8$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|-9|$ 的值。",
    "answer": 9,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|-9|=9$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s7",
      "parameter_signature": "absolute_value_numeric_evaluation:n=-9:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|-9|$ 的值。",
    "correct_answer": 9,
    "explanation": "絕對值表示與 0 的距離。\n$|-9|=9$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-11|$ 的正確意義？",
    "choices": [
      "數線上 $-11$ 到 $0$ 的距離",
      "數線上 $11$ 到 $-11$ 的距離",
      "$-11$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-11$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-11|$ 表示 $-11$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s6",
      "parameter_signature": "absolute_value_distance_from_zero:n=-11:pattern=meaning",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-11|$ 的正確意義？",
    "correct_answer": "數線上 $-11$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-11|$ 表示 $-11$ 到 $0$ 的距離。"
  }
]
```
