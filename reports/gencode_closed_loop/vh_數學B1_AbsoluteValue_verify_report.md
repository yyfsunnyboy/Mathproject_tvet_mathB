# Verify Report: vh_數學B1_AbsoluteValue

- python: C:\Users\yehiv\AppData\Local\Programs\Python\Python311\python.exe
- registry: C:\Python\Mathproject_tvet_mathB\configs\generated_registry\b1_section_1_1_verified_registry.v0.1.yaml
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
.....                                                                    [100%]
5 passed in 0.14s
```

## Samples
```json
[
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|13|$ 的值。",
    "answer": 13,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|13|=13$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s1",
      "parameter_signature": "absolute_value_numeric_evaluation:n=13:difficulty=easy",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|13|$ 的值。",
    "correct_answer": 13,
    "explanation": "絕對值表示與 0 的距離。\n$|13|=13$。",
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
      "scenario_id": "s9",
      "parameter_signature": "absolute_value_distance_from_zero:n=-13:pattern=meaning",
      "question_pattern_id": "p4",
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
    "question_text": "已知數線上兩點 $A(-2)$、$B(0)$，試求 A、B 兩點的距離。",
    "answer": 2,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|0-(-2)|=|2|=2$。",
      "所以 A、B 兩點的距離為 $2$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s5",
      "parameter_signature": "absolute_value_distance_between_two_points:a=-2:b=0:difficulty=easy",
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
    "question": "已知數線上兩點 $A(-2)$、$B(0)$，試求 A、B 兩點的距離。",
    "correct_answer": 2,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|0-(-2)|=|2|=2$。\n所以 A、B 兩點的距離為 $2$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_equation_basic",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_equation_basic",
    "question_text": "解方程式 $|x|=16$。",
    "answer": "x=-16 或 x=16",
    "answer_type": "text",
    "checker_type": "exact_string_checker",
    "solution_steps": [
      "$|x|=16$ 表示 $x$ 到 $0$ 的距離為 $16$。",
      "因此 $x=-16$ 或 $x=16$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_equation_basic",
      "scenario_id": "s8",
      "parameter_signature": "absolute_value_equation_basic:n=16:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_equation",
        "two_solutions"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "解方程式 $|x|=16$。",
    "correct_answer": "x=-16 或 x=16",
    "explanation": "$|x|=16$ 表示 $x$ 到 $0$ 的距離為 $16$。\n因此 $x=-16$ 或 $x=16$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|12|$ 的值。",
    "answer": 12,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|12|=12$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s4",
      "parameter_signature": "absolute_value_numeric_evaluation:n=12:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|12|$ 的值。",
    "correct_answer": 12,
    "explanation": "絕對值表示與 0 的距離。\n$|12|=12$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-5|$ 的正確意義？",
    "choices": [
      "數線上 $-5$ 到 $0$ 的距離",
      "數線上 $5$ 到 $-5$ 的距離",
      "$-5$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-5$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-5|$ 表示 $-5$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s3",
      "parameter_signature": "absolute_value_distance_from_zero:n=-5:pattern=meaning",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-5|$ 的正確意義？",
    "correct_answer": "數線上 $-5$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-5|$ 表示 $-5$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(4)$、$B(-9)$，試求 A、B 兩點的距離。",
    "answer": 13,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|-9-(4)|=|-13|=13$。",
      "所以 A、B 兩點的距離為 $13$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s3",
      "parameter_signature": "absolute_value_distance_between_two_points:a=4:b=-9:difficulty=easy",
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
    "question": "已知數線上兩點 $A(4)$、$B(-9)$，試求 A、B 兩點的距離。",
    "correct_answer": 13,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|-9-(4)|=|-13|=13$。\n所以 A、B 兩點的距離為 $13$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_equation_basic",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_equation_basic",
    "question_text": "解方程式 $|x|=9$。",
    "answer": "x=-9 或 x=9",
    "answer_type": "text",
    "checker_type": "exact_string_checker",
    "solution_steps": [
      "$|x|=9$ 表示 $x$ 到 $0$ 的距離為 $9$。",
      "因此 $x=-9$ 或 $x=9$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_equation_basic",
      "scenario_id": "s5",
      "parameter_signature": "absolute_value_equation_basic:n=9:difficulty=easy",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_equation",
        "two_solutions"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "解方程式 $|x|=9$。",
    "correct_answer": "x=-9 或 x=9",
    "explanation": "$|x|=9$ 表示 $x$ 到 $0$ 的距離為 $9$。\n因此 $x=-9$ 或 $x=9$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|6|$ 的值。",
    "answer": 6,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|6|=6$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s1",
      "parameter_signature": "absolute_value_numeric_evaluation:n=6:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|6|$ 的值。",
    "correct_answer": 6,
    "explanation": "絕對值表示與 0 的距離。\n$|6|=6$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-7|$ 的正確意義？",
    "choices": [
      "數線上 $-7$ 到 $0$ 的距離",
      "數線上 $7$ 到 $-7$ 的距離",
      "$-7$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-7$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-7|$ 表示 $-7$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s2",
      "parameter_signature": "absolute_value_distance_from_zero:n=-7:pattern=meaning",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-7|$ 的正確意義？",
    "correct_answer": "數線上 $-7$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-7|$ 表示 $-7$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(-4)$、$B(-10)$，試求 A、B 兩點的距離。",
    "answer": 6,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|-10-(-4)|=|-6|=6$。",
      "所以 A、B 兩點的距離為 $6$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s1",
      "parameter_signature": "absolute_value_distance_between_two_points:a=-4:b=-10:difficulty=easy",
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
    "question": "已知數線上兩點 $A(-4)$、$B(-10)$，試求 A、B 兩點的距離。",
    "correct_answer": 6,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|-10-(-4)|=|-6|=6$。\n所以 A、B 兩點的距離為 $6$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_equation_basic",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_equation_basic",
    "question_text": "解方程式 $|x|=18$。",
    "answer": "x=-18 或 x=18",
    "answer_type": "text",
    "checker_type": "exact_string_checker",
    "solution_steps": [
      "$|x|=18$ 表示 $x$ 到 $0$ 的距離為 $18$。",
      "因此 $x=-18$ 或 $x=18$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_equation_basic",
      "scenario_id": "s4",
      "parameter_signature": "absolute_value_equation_basic:n=18:difficulty=easy",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "absolute_value_equation",
        "two_solutions"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "解方程式 $|x|=18$。",
    "correct_answer": "x=-18 或 x=18",
    "explanation": "$|x|=18$ 表示 $x$ 到 $0$ 的距離為 $18$。\n因此 $x=-18$ 或 $x=18$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|-15|$ 的值。",
    "answer": 15,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|-15|=15$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s6",
      "parameter_signature": "absolute_value_numeric_evaluation:n=-15:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|-15|$ 的值。",
    "correct_answer": 15,
    "explanation": "絕對值表示與 0 的距離。\n$|-15|=15$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-4|$ 的正確意義？",
    "choices": [
      "數線上 $-4$ 到 $0$ 的距離",
      "數線上 $4$ 到 $-4$ 的距離",
      "$-4$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-4$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-4|$ 表示 $-4$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s5",
      "parameter_signature": "absolute_value_distance_from_zero:n=-4:pattern=meaning",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-4|$ 的正確意義？",
    "correct_answer": "數線上 $-4$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-4|$ 表示 $-4$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(-4)$、$B(-1)$，試求 A、B 兩點的距離。",
    "answer": 3,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|-1-(-4)|=|3|=3$。",
      "所以 A、B 兩點的距離為 $3$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s1",
      "parameter_signature": "absolute_value_distance_between_two_points:a=-4:b=-1:difficulty=easy",
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
    "question": "已知數線上兩點 $A(-4)$、$B(-1)$，試求 A、B 兩點的距離。",
    "correct_answer": 3,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|-1-(-4)|=|3|=3$。\n所以 A、B 兩點的距離為 $3$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_equation_basic",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_equation_basic",
    "question_text": "解方程式 $|x|=10$。",
    "answer": "x=-10 或 x=10",
    "answer_type": "text",
    "checker_type": "exact_string_checker",
    "solution_steps": [
      "$|x|=10$ 表示 $x$ 到 $0$ 的距離為 $10$。",
      "因此 $x=-10$ 或 $x=10$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_equation_basic",
      "scenario_id": "s5",
      "parameter_signature": "absolute_value_equation_basic:n=10:difficulty=easy",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "absolute_value_equation",
        "two_solutions"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ]
    },
    "question": "解方程式 $|x|=10$。",
    "correct_answer": "x=-10 或 x=10",
    "explanation": "$|x|=10$ 表示 $x$ 到 $0$ 的距離為 $10$。\n因此 $x=-10$ 或 $x=10$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|2|$ 的值。",
    "answer": 2,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|2|=2$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s9",
      "parameter_signature": "absolute_value_numeric_evaluation:n=2:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|2|$ 的值。",
    "correct_answer": 2,
    "explanation": "絕對值表示與 0 的距離。\n$|2|=2$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-9|$ 的正確意義？",
    "choices": [
      "數線上 $-9$ 到 $0$ 的距離",
      "數線上 $9$ 到 $-9$ 的距離",
      "$-9$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-9$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-9|$ 表示 $-9$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s9",
      "parameter_signature": "absolute_value_distance_from_zero:n=-9:pattern=meaning",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-9|$ 的正確意義？",
    "correct_answer": "數線上 $-9$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-9|$ 表示 $-9$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(-5)$、$B(-10)$，試求 A、B 兩點的距離。",
    "answer": 5,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|-10-(-5)|=|-5|=5$。",
      "所以 A、B 兩點的距離為 $5$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s3",
      "parameter_signature": "absolute_value_distance_between_two_points:a=-5:b=-10:difficulty=easy",
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
    "question": "已知數線上兩點 $A(-5)$、$B(-10)$，試求 A、B 兩點的距離。",
    "correct_answer": 5,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|-10-(-5)|=|-5|=5$。\n所以 A、B 兩點的距離為 $5$。",
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
      "scenario_id": "s5",
      "parameter_signature": "absolute_value_equation_basic:n=8:difficulty=easy",
      "question_pattern_id": "p4",
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
    "question_text": "求 $|6|$ 的值。",
    "answer": 6,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|6|=6$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s6",
      "parameter_signature": "absolute_value_numeric_evaluation:n=6:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|6|$ 的值。",
    "correct_answer": 6,
    "explanation": "絕對值表示與 0 的距離。\n$|6|=6$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-18|$ 的正確意義？",
    "choices": [
      "數線上 $-18$ 到 $0$ 的距離",
      "數線上 $18$ 到 $-18$ 的距離",
      "$-18$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-18$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-18|$ 表示 $-18$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s1",
      "parameter_signature": "absolute_value_distance_from_zero:n=-18:pattern=meaning",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-18|$ 的正確意義？",
    "correct_answer": "數線上 $-18$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-18|$ 表示 $-18$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(2)$、$B(10)$，試求 A、B 兩點的距離。",
    "answer": 8,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|10-(2)|=|8|=8$。",
      "所以 A、B 兩點的距離為 $8$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s8",
      "parameter_signature": "absolute_value_distance_between_two_points:a=2:b=10:difficulty=easy",
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
    "question": "已知數線上兩點 $A(2)$、$B(10)$，試求 A、B 兩點的距離。",
    "correct_answer": 8,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|10-(2)|=|8|=8$。\n所以 A、B 兩點的距離為 $8$。",
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
      "scenario_id": "s3",
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
    "question_text": "求 $|0|$ 的值。",
    "answer": 0,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|0|=0$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s6",
      "parameter_signature": "absolute_value_numeric_evaluation:n=0:difficulty=easy",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|0|$ 的值。",
    "correct_answer": 0,
    "explanation": "絕對值表示與 0 的距離。\n$|0|=0$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-15|$ 的正確意義？",
    "choices": [
      "數線上 $-15$ 到 $0$ 的距離",
      "數線上 $15$ 到 $-15$ 的距離",
      "$-15$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-15$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-15|$ 表示 $-15$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s1",
      "parameter_signature": "absolute_value_distance_from_zero:n=-15:pattern=meaning",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-15|$ 的正確意義？",
    "correct_answer": "數線上 $-15$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-15|$ 表示 $-15$ 到 $0$ 的距離。"
  },
  {
    "problem_type_id": "absolute_value_distance_between_two_points",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_between_two_points",
    "question_text": "已知數線上兩點 $A(-5)$、$B(-3)$，試求 A、B 兩點的距離。",
    "answer": 2,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "數線上兩點距離等於兩坐標差的絕對值。",
      "$|-3-(-5)|=|2|=2$。",
      "所以 A、B 兩點的距離為 $2$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_between_two_points",
      "scenario_id": "s2",
      "parameter_signature": "absolute_value_distance_between_two_points:a=-5:b=-3:difficulty=easy",
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
    "question": "已知數線上兩點 $A(-5)$、$B(-3)$，試求 A、B 兩點的距離。",
    "correct_answer": 2,
    "explanation": "數線上兩點距離等於兩坐標差的絕對值。\n$|-3-(-5)|=|2|=2$。\n所以 A、B 兩點的距離為 $2$。",
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
      "question_pattern_id": "p4",
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
    "question_text": "求 $|-17|$ 的值。",
    "answer": 17,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示與 0 的距離。",
      "$|-17|=17$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s7",
      "parameter_signature": "absolute_value_numeric_evaluation:n=-17:difficulty=easy",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|-17|$ 的值。",
    "correct_answer": 17,
    "explanation": "絕對值表示與 0 的距離。\n$|-17|=17$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_distance_from_zero",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_distance_from_zero",
    "question_text": "下列哪一項是 $|-7|$ 的正確意義？",
    "choices": [
      "數線上 $-7$ 到 $0$ 的距離",
      "數線上 $7$ 到 $-7$ 的距離",
      "$-7$ 本身",
      "一個負數"
    ],
    "answer": "數線上 $-7$ 到 $0$ 的距離",
    "answer_type": "choice",
    "checker_type": "choice_checker",
    "solution_steps": [
      "絕對值表示數線上該數到 $0$ 的距離。",
      "因此 $|-7|$ 表示 $-7$ 到 $0$ 的距離。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_distance_from_zero",
      "scenario_id": "s9",
      "parameter_signature": "absolute_value_distance_from_zero:n=-7:pattern=meaning",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_meaning",
        "distance_from_zero"
      ],
      "prerequisite_subskills": [
        "number_line_basic_position"
      ]
    },
    "question": "下列哪一項是 $|-7|$ 的正確意義？",
    "correct_answer": "數線上 $-7$ 到 $0$ 的距離",
    "explanation": "絕對值表示數線上該數到 $0$ 的距離。\n因此 $|-7|$ 表示 $-7$ 到 $0$ 的距離。"
  }
]
```
