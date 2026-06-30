# Verify Report: vh_數學B1_AbsoluteValueInequality

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
    "absolute_value_inequality_integer_solution_count_choice",
    "absolute_value_inequality_linear_expression_basic",
    "absolute_value_inequality_shifted_basic",
    "absolute_value_inequality_zero_center_basic"
  ],
  "observed_problem_types": [
    "absolute_value_inequality_integer_solution_count_choice",
    "absolute_value_inequality_linear_expression_basic",
    "absolute_value_inequality_shifted_basic",
    "absolute_value_inequality_zero_center_basic"
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
    "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "subskill_id": "absolute_value_inequality_integer_solution_count_choice",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_inequality_integer_solution_count_choice/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "choice",
    "checker_type": "choice_label_checker"
  },
  {
    "problem_type_id": "absolute_value_inequality_linear_expression_basic",
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "subskill_id": "absolute_value_inequality_linear_expression_basic",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_inequality_linear_expression_basic/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "interval_set",
    "checker_type": "interval_checker"
  },
  {
    "problem_type_id": "absolute_value_inequality_shifted_basic",
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "subskill_id": "absolute_value_inequality_shifted_basic",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_inequality_shifted_basic/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "interval_set",
    "checker_type": "interval_checker"
  },
  {
    "problem_type_id": "absolute_value_inequality_zero_center_basic",
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "subskill_id": "absolute_value_inequality_zero_center_basic",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_inequality_zero_center_basic/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "interval_set",
    "checker_type": "interval_checker"
  }
]
```

## Pytest Output
```text
..                                                                       [100%]
2 passed in 0.07s
```

## Samples
```json
[
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
    "subskill_id": "absolute_value_inequality_integer_solution_count_choice",
    "question_text": "若 $\\left| 1x - 5 \\right| \\le 6$，滿足的整數 $x$ 有幾個？",
    "question": "若 $\\left| 1x - 5 \\right| \\le 6$，滿足的整數 $x$ 有幾個？",
    "choices": [
      "14",
      "13",
      "12",
      "15"
    ],
    "answer": "B",
    "correct_answer": "B",
    "answer_type": "choice",
    "checker_type": "choice_label_checker",
    "answer_contract": {
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker"
    },
    "explanation": "先解得區間 [-1,11]，再計算整數點個數。",
    "solution_steps": [
      "先解得區間 [-1,11]，再計算整數點個數。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "integer_count",
      "choice_label"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_integer_solution_count_choice",
      "scenario_id": "s1",
      "parameter_signature": "solution_count:a=1:b=-5:c=6",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "integer_count",
        "choice_label"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_linear_expression_basic",
    "subskill_id": "absolute_value_inequality_linear_expression_basic",
    "question_text": "解不等式：$\\left| 1x + 2 \\right| > 8$。",
    "question": "解不等式：$\\left| 1x + 2 \\right| > 8$。",
    "answer": "(-∞,-10) ∪ (6,∞)",
    "correct_answer": "(-∞,-10) ∪ (6,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。",
    "solution_steps": [
      "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "linear_expression",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_linear_expression_basic",
      "scenario_id": "s1",
      "parameter_signature": "linear_expression:a=1:b=2:c=8:op=>",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "linear_expression",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_shifted_basic",
    "subskill_id": "absolute_value_inequality_shifted_basic",
    "question_text": "解不等式：$\\left| x - 2 \\right| < 3$。",
    "question": "解不等式：$\\left| x - 2 \\right| < 3$。",
    "answer": "(-1,5)",
    "correct_answer": "(-1,5)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先視為 |x-h| 型，再轉回 x 的區間。",
    "solution_steps": [
      "先視為 |x-h| 型，再轉回 x 的區間。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "shifted",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_shifted_basic",
      "scenario_id": "s1",
      "parameter_signature": "shifted:h=2:a=3:op=<",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "shifted",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_zero_center_basic",
    "subskill_id": "absolute_value_inequality_zero_center_basic",
    "question_text": "解不等式：$\\left| x \\right| > 9$。",
    "question": "解不等式：$\\left| x \\right| > 9$。",
    "answer": "(-∞,-9) ∪ (9,∞)",
    "correct_answer": "(-∞,-9) ∪ (9,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "將絕對值不等式轉為區間端點形式。",
    "solution_steps": [
      "將絕對值不等式轉為區間端點形式。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "inequality",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_zero_center_basic",
      "scenario_id": "s1",
      "parameter_signature": "zero_center:a=9:op=>",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "inequality",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
    "subskill_id": "absolute_value_inequality_integer_solution_count_choice",
    "question_text": "若 $\\left| 2x + 1 \\right| \\le 6$，滿足的整數 $x$ 有幾個？",
    "question": "若 $\\left| 2x + 1 \\right| \\le 6$，滿足的整數 $x$ 有幾個？",
    "choices": [
      "7",
      "5",
      "8",
      "6"
    ],
    "answer": "D",
    "correct_answer": "D",
    "answer_type": "choice",
    "checker_type": "choice_label_checker",
    "answer_contract": {
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker"
    },
    "explanation": "先解得區間 [-3.5,2.5]，再計算整數點個數。",
    "solution_steps": [
      "先解得區間 [-3.5,2.5]，再計算整數點個數。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "integer_count",
      "choice_label"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_integer_solution_count_choice",
      "scenario_id": "s1",
      "parameter_signature": "solution_count:a=2:b=1:c=6",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "integer_count",
        "choice_label"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_linear_expression_basic",
    "subskill_id": "absolute_value_inequality_linear_expression_basic",
    "question_text": "解不等式：$\\left| -2x + 0 \\right| > 4$。",
    "question": "解不等式：$\\left| -2x + 0 \\right| > 4$。",
    "answer": "(-∞,-2) ∪ (2,∞)",
    "correct_answer": "(-∞,-2) ∪ (2,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。",
    "solution_steps": [
      "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "linear_expression",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_linear_expression_basic",
      "scenario_id": "s1",
      "parameter_signature": "linear_expression:a=-2:b=0:c=4:op=>",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "linear_expression",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_shifted_basic",
    "subskill_id": "absolute_value_inequality_shifted_basic",
    "question_text": "解不等式：$\\left| x + 6 \\right| <= 6$。",
    "question": "解不等式：$\\left| x + 6 \\right| <= 6$。",
    "answer": "[-12,0]",
    "correct_answer": "[-12,0]",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先視為 |x-h| 型，再轉回 x 的區間。",
    "solution_steps": [
      "先視為 |x-h| 型，再轉回 x 的區間。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "shifted",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_shifted_basic",
      "scenario_id": "s1",
      "parameter_signature": "shifted:h=-6:a=6:op=<=",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "shifted",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_zero_center_basic",
    "subskill_id": "absolute_value_inequality_zero_center_basic",
    "question_text": "解不等式：$\\left| x \\right| < 3$。",
    "question": "解不等式：$\\left| x \\right| < 3$。",
    "answer": "(-3,3)",
    "correct_answer": "(-3,3)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "將絕對值不等式轉為區間端點形式。",
    "solution_steps": [
      "將絕對值不等式轉為區間端點形式。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "inequality",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_zero_center_basic",
      "scenario_id": "s1",
      "parameter_signature": "zero_center:a=3:op=<",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "inequality",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
    "subskill_id": "absolute_value_inequality_integer_solution_count_choice",
    "question_text": "若 $\\left| 2x + 6 \\right| \\le 4$，滿足的整數 $x$ 有幾個？",
    "question": "若 $\\left| 2x + 6 \\right| \\le 4$，滿足的整數 $x$ 有幾個？",
    "choices": [
      "7",
      "4",
      "5",
      "6"
    ],
    "answer": "C",
    "correct_answer": "C",
    "answer_type": "choice",
    "checker_type": "choice_label_checker",
    "answer_contract": {
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker"
    },
    "explanation": "先解得區間 [-5,-1]，再計算整數點個數。",
    "solution_steps": [
      "先解得區間 [-5,-1]，再計算整數點個數。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "integer_count",
      "choice_label"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_integer_solution_count_choice",
      "scenario_id": "s1",
      "parameter_signature": "solution_count:a=2:b=6:c=4",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "integer_count",
        "choice_label"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_linear_expression_basic",
    "subskill_id": "absolute_value_inequality_linear_expression_basic",
    "question_text": "解不等式：$\\left| -2x + 4 \\right| > 4$。",
    "question": "解不等式：$\\left| -2x + 4 \\right| > 4$。",
    "answer": "(-∞,0) ∪ (4,∞)",
    "correct_answer": "(-∞,0) ∪ (4,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。",
    "solution_steps": [
      "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "linear_expression",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_linear_expression_basic",
      "scenario_id": "s1",
      "parameter_signature": "linear_expression:a=-2:b=4:c=4:op=>",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "linear_expression",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_shifted_basic",
    "subskill_id": "absolute_value_inequality_shifted_basic",
    "question_text": "解不等式：$\\left| x - 3 \\right| > 6$。",
    "question": "解不等式：$\\left| x - 3 \\right| > 6$。",
    "answer": "(-∞,-3) ∪ (9,∞)",
    "correct_answer": "(-∞,-3) ∪ (9,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先視為 |x-h| 型，再轉回 x 的區間。",
    "solution_steps": [
      "先視為 |x-h| 型，再轉回 x 的區間。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "shifted",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_shifted_basic",
      "scenario_id": "s1",
      "parameter_signature": "shifted:h=3:a=6:op=>",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "shifted",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_zero_center_basic",
    "subskill_id": "absolute_value_inequality_zero_center_basic",
    "question_text": "解不等式：$\\left| x \\right| < 7$。",
    "question": "解不等式：$\\left| x \\right| < 7$。",
    "answer": "(-7,7)",
    "correct_answer": "(-7,7)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "將絕對值不等式轉為區間端點形式。",
    "solution_steps": [
      "將絕對值不等式轉為區間端點形式。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "inequality",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_zero_center_basic",
      "scenario_id": "s1",
      "parameter_signature": "zero_center:a=7:op=<",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "inequality",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
    "subskill_id": "absolute_value_inequality_integer_solution_count_choice",
    "question_text": "若 $\\left| 1x - 3 \\right| \\le 7$，滿足的整數 $x$ 有幾個？",
    "question": "若 $\\left| 1x - 3 \\right| \\le 7$，滿足的整數 $x$ 有幾個？",
    "choices": [
      "14",
      "15",
      "16",
      "17"
    ],
    "answer": "B",
    "correct_answer": "B",
    "answer_type": "choice",
    "checker_type": "choice_label_checker",
    "answer_contract": {
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker"
    },
    "explanation": "先解得區間 [-4,10]，再計算整數點個數。",
    "solution_steps": [
      "先解得區間 [-4,10]，再計算整數點個數。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "integer_count",
      "choice_label"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_integer_solution_count_choice",
      "scenario_id": "s1",
      "parameter_signature": "solution_count:a=1:b=-3:c=7",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "integer_count",
        "choice_label"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_linear_expression_basic",
    "subskill_id": "absolute_value_inequality_linear_expression_basic",
    "question_text": "解不等式：$\\left| -2x + 2 \\right| >= 3$。",
    "question": "解不等式：$\\left| -2x + 2 \\right| >= 3$。",
    "answer": "(-∞,-1/2] ∪ [5/2,∞)",
    "correct_answer": "(-∞,-1/2] ∪ [5/2,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。",
    "solution_steps": [
      "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "linear_expression",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_linear_expression_basic",
      "scenario_id": "s1",
      "parameter_signature": "linear_expression:a=-2:b=2:c=3:op=>=",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "linear_expression",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_shifted_basic",
    "subskill_id": "absolute_value_inequality_shifted_basic",
    "question_text": "解不等式：$\\left| x + 6 \\right| > 2$。",
    "question": "解不等式：$\\left| x + 6 \\right| > 2$。",
    "answer": "(-∞,-8) ∪ (-4,∞)",
    "correct_answer": "(-∞,-8) ∪ (-4,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先視為 |x-h| 型，再轉回 x 的區間。",
    "solution_steps": [
      "先視為 |x-h| 型，再轉回 x 的區間。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "shifted",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_shifted_basic",
      "scenario_id": "s1",
      "parameter_signature": "shifted:h=-6:a=2:op=>",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "shifted",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_zero_center_basic",
    "subskill_id": "absolute_value_inequality_zero_center_basic",
    "question_text": "解不等式：$\\left| x \\right| >= 4$。",
    "question": "解不等式：$\\left| x \\right| >= 4$。",
    "answer": "(-∞,-4] ∪ [4,∞)",
    "correct_answer": "(-∞,-4] ∪ [4,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "將絕對值不等式轉為區間端點形式。",
    "solution_steps": [
      "將絕對值不等式轉為區間端點形式。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "inequality",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_zero_center_basic",
      "scenario_id": "s1",
      "parameter_signature": "zero_center:a=4:op=>=",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "inequality",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
    "subskill_id": "absolute_value_inequality_integer_solution_count_choice",
    "question_text": "若 $\\left| 1x + 2 \\right| \\le 4$，滿足的整數 $x$ 有幾個？",
    "question": "若 $\\left| 1x + 2 \\right| \\le 4$，滿足的整數 $x$ 有幾個？",
    "choices": [
      "9",
      "10",
      "11",
      "8"
    ],
    "answer": "A",
    "correct_answer": "A",
    "answer_type": "choice",
    "checker_type": "choice_label_checker",
    "answer_contract": {
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker"
    },
    "explanation": "先解得區間 [-6,2]，再計算整數點個數。",
    "solution_steps": [
      "先解得區間 [-6,2]，再計算整數點個數。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "integer_count",
      "choice_label"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_integer_solution_count_choice",
      "scenario_id": "s1",
      "parameter_signature": "solution_count:a=1:b=2:c=4",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "integer_count",
        "choice_label"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_linear_expression_basic",
    "subskill_id": "absolute_value_inequality_linear_expression_basic",
    "question_text": "解不等式：$\\left| -1x + 1 \\right| < 8$。",
    "question": "解不等式：$\\left| -1x + 1 \\right| < 8$。",
    "answer": "(-7,9)",
    "correct_answer": "(-7,9)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。",
    "solution_steps": [
      "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "linear_expression",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_linear_expression_basic",
      "scenario_id": "s1",
      "parameter_signature": "linear_expression:a=-1:b=1:c=8:op=<",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "linear_expression",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_shifted_basic",
    "subskill_id": "absolute_value_inequality_shifted_basic",
    "question_text": "解不等式：$\\left| x - 1 \\right| > 7$。",
    "question": "解不等式：$\\left| x - 1 \\right| > 7$。",
    "answer": "(-∞,-6) ∪ (8,∞)",
    "correct_answer": "(-∞,-6) ∪ (8,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先視為 |x-h| 型，再轉回 x 的區間。",
    "solution_steps": [
      "先視為 |x-h| 型，再轉回 x 的區間。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "shifted",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_shifted_basic",
      "scenario_id": "s1",
      "parameter_signature": "shifted:h=1:a=7:op=>",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "shifted",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_zero_center_basic",
    "subskill_id": "absolute_value_inequality_zero_center_basic",
    "question_text": "解不等式：$\\left| x \\right| < 9$。",
    "question": "解不等式：$\\left| x \\right| < 9$。",
    "answer": "(-9,9)",
    "correct_answer": "(-9,9)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "將絕對值不等式轉為區間端點形式。",
    "solution_steps": [
      "將絕對值不等式轉為區間端點形式。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "inequality",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_zero_center_basic",
      "scenario_id": "s1",
      "parameter_signature": "zero_center:a=9:op=<",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "inequality",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
    "subskill_id": "absolute_value_inequality_integer_solution_count_choice",
    "question_text": "若 $\\left| 3x - 5 \\right| \\le 7$，滿足的整數 $x$ 有幾個？",
    "question": "若 $\\left| 3x - 5 \\right| \\le 7$，滿足的整數 $x$ 有幾個？",
    "choices": [
      "6",
      "5",
      "7",
      "4"
    ],
    "answer": "B",
    "correct_answer": "B",
    "answer_type": "choice",
    "checker_type": "choice_label_checker",
    "answer_contract": {
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker"
    },
    "explanation": "先解得區間 [-0.6666666667,4]，再計算整數點個數。",
    "solution_steps": [
      "先解得區間 [-0.6666666667,4]，再計算整數點個數。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "integer_count",
      "choice_label"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_integer_solution_count_choice",
      "scenario_id": "s1",
      "parameter_signature": "solution_count:a=3:b=-5:c=7",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "integer_count",
        "choice_label"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_linear_expression_basic",
    "subskill_id": "absolute_value_inequality_linear_expression_basic",
    "question_text": "解不等式：$\\left| -1x - 3 \\right| > 6$。",
    "question": "解不等式：$\\left| -1x - 3 \\right| > 6$。",
    "answer": "(-∞,-9) ∪ (3,∞)",
    "correct_answer": "(-∞,-9) ∪ (3,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。",
    "solution_steps": [
      "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "linear_expression",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_linear_expression_basic",
      "scenario_id": "s1",
      "parameter_signature": "linear_expression:a=-1:b=-3:c=6:op=>",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "linear_expression",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_shifted_basic",
    "subskill_id": "absolute_value_inequality_shifted_basic",
    "question_text": "解不等式：$\\left| x - 3 \\right| > 2$。",
    "question": "解不等式：$\\left| x - 3 \\right| > 2$。",
    "answer": "(-∞,1) ∪ (5,∞)",
    "correct_answer": "(-∞,1) ∪ (5,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先視為 |x-h| 型，再轉回 x 的區間。",
    "solution_steps": [
      "先視為 |x-h| 型，再轉回 x 的區間。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "shifted",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_shifted_basic",
      "scenario_id": "s1",
      "parameter_signature": "shifted:h=3:a=2:op=>",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "shifted",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_zero_center_basic",
    "subskill_id": "absolute_value_inequality_zero_center_basic",
    "question_text": "解不等式：$\\left| x \\right| >= 3$。",
    "question": "解不等式：$\\left| x \\right| >= 3$。",
    "answer": "(-∞,-3] ∪ [3,∞)",
    "correct_answer": "(-∞,-3] ∪ [3,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "將絕對值不等式轉為區間端點形式。",
    "solution_steps": [
      "將絕對值不等式轉為區間端點形式。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "inequality",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_zero_center_basic",
      "scenario_id": "s1",
      "parameter_signature": "zero_center:a=3:op=>=",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "inequality",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
    "subskill_id": "absolute_value_inequality_integer_solution_count_choice",
    "question_text": "若 $\\left| 2x + 2 \\right| \\le 5$，滿足的整數 $x$ 有幾個？",
    "question": "若 $\\left| 2x + 2 \\right| \\le 5$，滿足的整數 $x$ 有幾個？",
    "choices": [
      "5",
      "6",
      "7",
      "4"
    ],
    "answer": "A",
    "correct_answer": "A",
    "answer_type": "choice",
    "checker_type": "choice_label_checker",
    "answer_contract": {
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker"
    },
    "explanation": "先解得區間 [-3.5,1.5]，再計算整數點個數。",
    "solution_steps": [
      "先解得區間 [-3.5,1.5]，再計算整數點個數。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "integer_count",
      "choice_label"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_integer_solution_count_choice",
      "scenario_id": "s1",
      "parameter_signature": "solution_count:a=2:b=2:c=5",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "integer_count",
        "choice_label"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_linear_expression_basic",
    "subskill_id": "absolute_value_inequality_linear_expression_basic",
    "question_text": "解不等式：$\\left| -2x - 3 \\right| <= 2$。",
    "question": "解不等式：$\\left| -2x - 3 \\right| <= 2$。",
    "answer": "[-2.5,-0.5]",
    "correct_answer": "[-2.5,-0.5]",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。",
    "solution_steps": [
      "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "linear_expression",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_linear_expression_basic",
      "scenario_id": "s1",
      "parameter_signature": "linear_expression:a=-2:b=-3:c=2:op=<=",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "linear_expression",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_shifted_basic",
    "subskill_id": "absolute_value_inequality_shifted_basic",
    "question_text": "解不等式：$\\left| x - 7 \\right| <= 2$。",
    "question": "解不等式：$\\left| x - 7 \\right| <= 2$。",
    "answer": "[5,9]",
    "correct_answer": "[5,9]",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先視為 |x-h| 型，再轉回 x 的區間。",
    "solution_steps": [
      "先視為 |x-h| 型，再轉回 x 的區間。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "shifted",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_shifted_basic",
      "scenario_id": "s1",
      "parameter_signature": "shifted:h=7:a=2:op=<=",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "shifted",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_zero_center_basic",
    "subskill_id": "absolute_value_inequality_zero_center_basic",
    "question_text": "解不等式：$\\left| x \\right| <= 9$。",
    "question": "解不等式：$\\left| x \\right| <= 9$。",
    "answer": "[-9,9]",
    "correct_answer": "[-9,9]",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "將絕對值不等式轉為區間端點形式。",
    "solution_steps": [
      "將絕對值不等式轉為區間端點形式。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "inequality",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_zero_center_basic",
      "scenario_id": "s1",
      "parameter_signature": "zero_center:a=9:op=<=",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "inequality",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_integer_solution_count_choice",
    "subskill_id": "absolute_value_inequality_integer_solution_count_choice",
    "question_text": "若 $\\left| 2x - 4 \\right| \\le 4$，滿足的整數 $x$ 有幾個？",
    "question": "若 $\\left| 2x - 4 \\right| \\le 4$，滿足的整數 $x$ 有幾個？",
    "choices": [
      "4",
      "6",
      "7",
      "5"
    ],
    "answer": "D",
    "correct_answer": "D",
    "answer_type": "choice",
    "checker_type": "choice_label_checker",
    "answer_contract": {
      "answer_type": "choice",
      "equivalence_type": "choice_label",
      "checker_key": "choice_label_checker"
    },
    "explanation": "先解得區間 [0,4]，再計算整數點個數。",
    "solution_steps": [
      "先解得區間 [0,4]，再計算整數點個數。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "integer_count",
      "choice_label"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_integer_solution_count_choice",
      "scenario_id": "s1",
      "parameter_signature": "solution_count:a=2:b=-4:c=4",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "integer_count",
        "choice_label"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_AbsoluteValueInequality",
    "problem_type_id": "absolute_value_inequality_linear_expression_basic",
    "subskill_id": "absolute_value_inequality_linear_expression_basic",
    "question_text": "解不等式：$\\left| 3x - 3 \\right| >= 3$。",
    "question": "解不等式：$\\left| 3x - 3 \\right| >= 3$。",
    "answer": "(-∞,0] ∪ [2,∞)",
    "correct_answer": "(-∞,0] ∪ [2,∞)",
    "answer_type": "interval_set",
    "checker_type": "interval_checker",
    "answer_contract": {
      "answer_type": "interval_set",
      "equivalence_type": "interval_set",
      "checker_key": "interval_checker"
    },
    "explanation": "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。",
    "solution_steps": [
      "先解 -c ≤ ax+b ≤ c 或其補集，再換成區間表示。"
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "absolute_value",
      "linear_expression",
      "interval_set"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "absolute_value_inequality_linear_expression_basic",
      "scenario_id": "s1",
      "parameter_signature": "linear_expression:a=3:b=-3:c=3:op=>=",
      "question_pattern_id": "p1",
      "diagnosis_tags": [
        "absolute_value",
        "linear_expression",
        "interval_set"
      ],
      "prerequisite_subskills": [
        "absolute_value_numeric_evaluation"
      ],
      "verified_problem_types": [
        "absolute_value_inequality_integer_solution_count_choice",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic",
        "absolute_value_inequality_zero_center_basic"
      ],
      "manual_review_exclusions": [
        "absolute_value_inequality_malformed_source_review"
      ],
      "source": "gencode_runtime_binding"
    }
  }
]
```
