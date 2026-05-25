# Verify Report: vh_數學B1_AbsoluteValue

- python: C:\Python\Mathproject_tvet_mathB\venv\Scripts\python.exe
- registry: C:\Python\Mathproject_tvet_mathB\configs\generated_registry\b1_section_1_1_verified_registry.v0.1.yaml
- registry_verified_count: 1
- pytest_exit_code: 0
- unique_problem_type_count: 1
- PASS: True

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
  }
]
```

## Pytest Output
```text
...                                                                      [100%]
3 passed in 0.12s
```

## Samples
```json
[
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|-1|$ 的值。",
    "answer": 1,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示到 0 的距離。",
      "因此 $|-1|=1$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s9",
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
    "explanation": "絕對值表示到 0 的距離。\n因此 $|-1|=1$。",
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
      "絕對值表示到 0 的距離。",
      "因此 $|-19|=19$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s7",
      "parameter_signature": "absolute_value_numeric_evaluation:n=-19:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|-19|$ 的值。",
    "correct_answer": 19,
    "explanation": "絕對值表示到 0 的距離。\n因此 $|-19|=19$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|-2|$ 的值。",
    "answer": 2,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示到 0 的距離。",
      "因此 $|-2|=2$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s1",
      "parameter_signature": "absolute_value_numeric_evaluation:n=-2:difficulty=easy",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|-2|$ 的值。",
    "correct_answer": 2,
    "explanation": "絕對值表示到 0 的距離。\n因此 $|-2|=2$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|5|$ 的值。",
    "answer": 5,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示到 0 的距離。",
      "因此 $|5|=5$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s6",
      "parameter_signature": "absolute_value_numeric_evaluation:n=5:difficulty=easy",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|5|$ 的值。",
    "correct_answer": 5,
    "explanation": "絕對值表示到 0 的距離。\n因此 $|5|=5$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|-2|$ 的值。",
    "answer": 2,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示到 0 的距離。",
      "因此 $|-2|=2$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s7",
      "parameter_signature": "absolute_value_numeric_evaluation:n=-2:difficulty=easy",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|-2|$ 的值。",
    "correct_answer": 2,
    "explanation": "絕對值表示到 0 的距離。\n因此 $|-2|=2$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|-18|$ 的值。",
    "answer": 18,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示到 0 的距離。",
      "因此 $|-18|=18$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s3",
      "parameter_signature": "absolute_value_numeric_evaluation:n=-18:difficulty=easy",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|-18|$ 的值。",
    "correct_answer": 18,
    "explanation": "絕對值表示到 0 的距離。\n因此 $|-18|=18$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|4|$ 的值。",
    "answer": 4,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示到 0 的距離。",
      "因此 $|4|=4$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s9",
      "parameter_signature": "absolute_value_numeric_evaluation:n=4:difficulty=easy",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|4|$ 的值。",
    "correct_answer": 4,
    "explanation": "絕對值表示到 0 的距離。\n因此 $|4|=4$。",
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
      "絕對值表示到 0 的距離。",
      "因此 $|0|=0$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s4",
      "parameter_signature": "absolute_value_numeric_evaluation:n=0:difficulty=easy",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|0|$ 的值。",
    "correct_answer": 0,
    "explanation": "絕對值表示到 0 的距離。\n因此 $|0|=0$。",
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
      "絕對值表示到 0 的距離。",
      "因此 $|3|=3$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s9",
      "parameter_signature": "absolute_value_numeric_evaluation:n=3:difficulty=easy",
      "question_pattern_id": "p4",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|3|$ 的值。",
    "correct_answer": 3,
    "explanation": "絕對值表示到 0 的距離。\n因此 $|3|=3$。",
    "choices": []
  },
  {
    "problem_type_id": "absolute_value_numeric_evaluation",
    "skill_id": "vh_數學B1_AbsoluteValue",
    "subskill_id": "absolute_value_numeric_evaluation",
    "question_text": "求 $|16|$ 的值。",
    "answer": 16,
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "solution_steps": [
      "絕對值表示到 0 的距離。",
      "因此 $|16|=16$。"
    ],
    "metadata": {
      "scenario_family": "absolute_value_numeric_evaluation",
      "scenario_id": "s3",
      "parameter_signature": "absolute_value_numeric_evaluation:n=16:difficulty=easy",
      "question_pattern_id": "p2",
      "diagnosis_tags": [
        "absolute_value_definition",
        "sign_error"
      ],
      "prerequisite_subskills": []
    },
    "question": "求 $|16|$ 的值。",
    "correct_answer": 16,
    "explanation": "絕對值表示到 0 的距離。\n因此 $|16|=16$。",
    "choices": []
  }
]
```
