# Verify Report: vh_數學B1_DistanceBetweenTwoParallelLines

- python: C:\Users\Owner\anaconda3\python.exe
- registry: D:\Python\Mathproject_tvet_mathB\configs\generated_registry\b1_section_1_1_verified_registry.v0.1.yaml
- registry_verified_count: 4
- pytest_exit_code: 0
- unique_problem_type_count: 4
- PASS: True

## Runtime ProblemType Coverage
```json
{
  "expected_problem_types": [
    "area_using_parallel_distance",
    "distance_between_parallel_lines",
    "parallel_lines_distance_single_choice",
    "solve_parameter_from_parallel_distance"
  ],
  "observed_problem_types": [
    "area_using_parallel_distance",
    "distance_between_parallel_lines",
    "parallel_lines_distance_single_choice",
    "solve_parameter_from_parallel_distance"
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
    "problem_type_id": "distance_between_parallel_lines",
    "skill_id": "vh_數學B1_DistanceBetweenTwoParallelLines",
    "subskill_id": "distance_between_parallel_lines",
    "status": "verified",
    "candidate_path": "skills/vh_數學B1_DistanceBetweenTwoParallelLines.py",
    "function_name": "generate",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "wrapper_path": "skills/vh_數學B1_DistanceBetweenTwoParallelLines.py",
    "source": "gencode_runtime_binding"
  },
  {
    "problem_type_id": "solve_parameter_from_parallel_distance",
    "skill_id": "vh_數學B1_DistanceBetweenTwoParallelLines",
    "subskill_id": "solve_parameter_from_parallel_distance",
    "status": "verified",
    "candidate_path": "skills/vh_數學B1_DistanceBetweenTwoParallelLines.py",
    "function_name": "generate",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "wrapper_path": "skills/vh_數學B1_DistanceBetweenTwoParallelLines.py",
    "source": "gencode_runtime_binding"
  },
  {
    "problem_type_id": "area_using_parallel_distance",
    "skill_id": "vh_數學B1_DistanceBetweenTwoParallelLines",
    "subskill_id": "area_using_parallel_distance",
    "status": "verified",
    "candidate_path": "skills/vh_數學B1_DistanceBetweenTwoParallelLines.py",
    "function_name": "generate",
    "answer_type": "rational",
    "checker_type": "rational_checker",
    "wrapper_path": "skills/vh_數學B1_DistanceBetweenTwoParallelLines.py",
    "source": "gencode_runtime_binding"
  },
  {
    "problem_type_id": "parallel_lines_distance_single_choice",
    "skill_id": "vh_數學B1_DistanceBetweenTwoParallelLines",
    "subskill_id": "parallel_lines_distance_single_choice",
    "status": "verified",
    "candidate_path": "skills/vh_數學B1_DistanceBetweenTwoParallelLines.py",
    "function_name": "generate",
    "answer_type": "choice",
    "checker_type": "choice_label_checker",
    "wrapper_path": "skills/vh_數學B1_DistanceBetweenTwoParallelLines.py",
    "source": "gencode_runtime_binding"
  }
]
```

## Pytest Output
```text
.....                                                                    [100%]
5 passed in 0.29s
```

## Samples
```json
[
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4588",
      "textbook_example_id": 4588,
      "generator_key": "src_4588",
      "source_kind": "quiz",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4588",
    "textbook_example_id": 4588,
    "generator_key": "src_4588",
    "seed": null,
    "source_kind": "quiz",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4588,
    "source_order": 4588,
    "sampling_weight": 1.0
  },
  {
    "question_text": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "question": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "correct_answer": "-46/3, 74/3",
    "answer": "-46/3, 74/3",
    "display_answer": "$\\frac{14}{3} \\pm 20$",
    "semantic_answer": "-46/3, 74/3",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "-46/3, 74/3",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "solve_parameter_from_parallel_distance",
        "task_type": "solve_parameter_from_parallel_distance",
        "line_type": "solve_parameter_from_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "-46/3, 74/3",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 4,
        "B": 2,
        "C": 0
      },
      "general_form": "-46/3, 74/3",
      "line_equation": "-46/3, 74/3",
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "-46/3, 74/3",
      "problem_type_id": "solve_parameter_from_parallel_distance",
      "component_id": "src_4571",
      "textbook_example_id": 4571,
      "generator_key": "src_4571",
      "source_kind": "example",
      "line_type": "solve_parameter_from_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "semantic_answer": "-46/3, 74/3"
    },
    "checker": "solution_set_checker",
    "checker_type": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "problem_type_id": "solve_parameter_from_parallel_distance",
    "component_id": "src_4571",
    "textbook_example_id": 4571,
    "generator_key": "src_4571",
    "seed": null,
    "source_kind": "example",
    "line_type": "solve_parameter_from_parallel_distance",
    "display_order": 4571,
    "source_order": 4571,
    "sampling_weight": 1.0
  },
  {
    "question_text": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "question": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "correct_answer": "74/3",
    "answer": "74/3",
    "display_answer": "$\\frac{74}{3}$",
    "semantic_answer": "74/3",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "74/3",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "solve_parameter_from_parallel_distance",
        "task_type": "solve_parameter_from_parallel_distance",
        "line_type": "solve_parameter_from_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "74/3",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 4,
        "B": 2,
        "C": 0
      },
      "general_form": "74/3",
      "line_equation": "74/3",
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "semantic_answer": "74/3",
      "problem_type_id": "solve_parameter_from_parallel_distance",
      "component_id": "src_4589",
      "textbook_example_id": 4589,
      "generator_key": "src_4589",
      "source_kind": "quiz",
      "line_type": "solve_parameter_from_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "checker": "rational_checker",
      "checker_key": "rational_checker",
      "answer_equivalence": "rational_equivalent",
      "equivalence": "rational_equivalent",
      "semantic_answer": "74/3"
    },
    "checker": "rational_checker",
    "checker_type": "rational_checker",
    "equivalence": "rational_equivalent",
    "problem_type_id": "solve_parameter_from_parallel_distance",
    "component_id": "src_4589",
    "textbook_example_id": 4589,
    "generator_key": "src_4589",
    "seed": null,
    "source_kind": "quiz",
    "line_type": "solve_parameter_from_parallel_distance",
    "display_order": 4589,
    "source_order": 4589,
    "sampling_weight": 1.0
  },
  {
    "question_text": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "question": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "correct_answer": "-46/3, 74/3",
    "answer": "-46/3, 74/3",
    "display_answer": "$\\frac{14}{3} \\pm 20$",
    "semantic_answer": "-46/3, 74/3",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "-46/3, 74/3",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "solve_parameter_from_parallel_distance",
        "task_type": "solve_parameter_from_parallel_distance",
        "line_type": "solve_parameter_from_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "-46/3, 74/3",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 4,
        "B": 2,
        "C": 0
      },
      "general_form": "-46/3, 74/3",
      "line_equation": "-46/3, 74/3",
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "-46/3, 74/3",
      "problem_type_id": "solve_parameter_from_parallel_distance",
      "component_id": "src_4571",
      "textbook_example_id": 4571,
      "generator_key": "src_4571",
      "source_kind": "example",
      "line_type": "solve_parameter_from_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "semantic_answer": "-46/3, 74/3"
    },
    "checker": "solution_set_checker",
    "checker_type": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "problem_type_id": "solve_parameter_from_parallel_distance",
    "component_id": "src_4571",
    "textbook_example_id": 4571,
    "generator_key": "src_4571",
    "seed": null,
    "source_kind": "example",
    "line_type": "solve_parameter_from_parallel_distance",
    "display_order": 4571,
    "source_order": 4571,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4577",
      "textbook_example_id": 4577,
      "generator_key": "src_4577",
      "source_kind": "example",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4577",
    "textbook_example_id": 4577,
    "generator_key": "src_4577",
    "seed": null,
    "source_kind": "example",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4577,
    "source_order": 4577,
    "sampling_weight": 1.0
  },
  {
    "question_text": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "question": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "correct_answer": "74/3",
    "answer": "74/3",
    "display_answer": "$\\frac{74}{3}$",
    "semantic_answer": "74/3",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "74/3",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "solve_parameter_from_parallel_distance",
        "task_type": "solve_parameter_from_parallel_distance",
        "line_type": "solve_parameter_from_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "74/3",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 4,
        "B": 2,
        "C": 0
      },
      "general_form": "74/3",
      "line_equation": "74/3",
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "semantic_answer": "74/3",
      "problem_type_id": "solve_parameter_from_parallel_distance",
      "component_id": "src_4580",
      "textbook_example_id": 4580,
      "generator_key": "src_4580",
      "source_kind": "example",
      "line_type": "solve_parameter_from_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "checker": "rational_checker",
      "checker_key": "rational_checker",
      "answer_equivalence": "rational_equivalent",
      "equivalence": "rational_equivalent",
      "semantic_answer": "74/3"
    },
    "checker": "rational_checker",
    "checker_type": "rational_checker",
    "equivalence": "rational_equivalent",
    "problem_type_id": "solve_parameter_from_parallel_distance",
    "component_id": "src_4580",
    "textbook_example_id": 4580,
    "generator_key": "src_4580",
    "seed": null,
    "source_kind": "example",
    "line_type": "solve_parameter_from_parallel_distance",
    "display_order": 4580,
    "source_order": 4580,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "hard"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4608",
      "textbook_example_id": 4608,
      "generator_key": "src_4608",
      "source_kind": "test",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4608",
    "textbook_example_id": 4608,
    "generator_key": "src_4608",
    "seed": null,
    "source_kind": "test",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4608,
    "source_order": 4608,
    "sampling_weight": 1.0
  },
  {
    "question_text": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "question": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "correct_answer": "74/3",
    "answer": "74/3",
    "display_answer": "$\\frac{74}{3}$",
    "semantic_answer": "74/3",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "74/3",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "solve_parameter_from_parallel_distance",
        "task_type": "solve_parameter_from_parallel_distance",
        "line_type": "solve_parameter_from_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "74/3",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 4,
        "B": 2,
        "C": 0
      },
      "general_form": "74/3",
      "line_equation": "74/3",
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "semantic_answer": "74/3",
      "problem_type_id": "solve_parameter_from_parallel_distance",
      "component_id": "src_4589",
      "textbook_example_id": 4589,
      "generator_key": "src_4589",
      "source_kind": "quiz",
      "line_type": "solve_parameter_from_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "checker": "rational_checker",
      "checker_key": "rational_checker",
      "answer_equivalence": "rational_equivalent",
      "equivalence": "rational_equivalent",
      "semantic_answer": "74/3"
    },
    "checker": "rational_checker",
    "checker_type": "rational_checker",
    "equivalence": "rational_equivalent",
    "problem_type_id": "solve_parameter_from_parallel_distance",
    "component_id": "src_4589",
    "textbook_example_id": 4589,
    "generator_key": "src_4589",
    "seed": null,
    "source_kind": "quiz",
    "line_type": "solve_parameter_from_parallel_distance",
    "display_order": 4589,
    "source_order": 4589,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4570",
      "textbook_example_id": 4570,
      "generator_key": "src_4570",
      "source_kind": "example",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4570",
    "textbook_example_id": 4570,
    "generator_key": "src_4570",
    "seed": null,
    "source_kind": "example",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4570,
    "source_order": 4570,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4577",
      "textbook_example_id": 4577,
      "generator_key": "src_4577",
      "source_kind": "example",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4577",
    "textbook_example_id": 4577,
    "generator_key": "src_4577",
    "seed": null,
    "source_kind": "example",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4577,
    "source_order": 4577,
    "sampling_weight": 1.0
  },
  {
    "question_text": "已知 $k>0$。若直線 $2x+6y+k=0$ 的斜率為 $-\\frac{1}{3}$，且點 $(0,0)$ 到直線 L 的距離為 $\\frac{\\sqrt{10}}{2}$，則 $a+k=$？",
    "question": "已知 $k>0$。若直線 $2x+6y+k=0$ 的斜率為 $-\\frac{1}{3}$，且點 $(0,0)$ 到直線 L 的距離為 $\\frac{\\sqrt{10}}{2}$，則 $a+k=$？",
    "correct_answer": "A",
    "answer": "A",
    "display_answer": "A",
    "semantic_answer": "A",
    "choices": [
      {
        "label": "A",
        "text": "A"
      },
      {
        "label": "B",
        "text": "18"
      },
      {
        "label": "C",
        "text": "6"
      },
      {
        "label": "D",
        "text": "8"
      }
    ],
    "options": [
      "A",
      "18",
      "6",
      "8"
    ],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [
        "slope=-1/3"
      ],
      "target": "A",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "parallel_lines_distance_single_choice",
        "task_type": "parallel_lines_distance_single_choice",
        "line_type": "parallel_lines_distance_single_choice",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "single_choice",
    "answer_type": "choice_label",
    "metadata": {
      "givens": [
        "slope=-1/3"
      ],
      "target": "A",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": 6,
        "C": 10
      },
      "general_form": "A",
      "line_equation": "A",
      "presentation_mode": "single_choice",
      "answer_type": "single_choice",
      "semantic_answer": "A",
      "problem_type_id": "parallel_lines_distance_single_choice",
      "component_id": "src_4584",
      "textbook_example_id": 4584,
      "generator_key": "src_4584",
      "source_kind": "example",
      "line_type": "parallel_lines_distance_single_choice"
    },
    "answer_contract": {
      "presentation_mode": "single_choice",
      "answer_type": "single_choice",
      "checker": "choice_label_checker",
      "checker_key": "choice_label_checker",
      "answer_equivalence": "choice_label",
      "equivalence": "choice_label",
      "semantic_answer": "A"
    },
    "checker": "choice_label_checker",
    "checker_type": "choice_label_checker",
    "equivalence": "choice_label",
    "problem_type_id": "parallel_lines_distance_single_choice",
    "component_id": "src_4584",
    "textbook_example_id": 4584,
    "generator_key": "src_4584",
    "seed": null,
    "source_kind": "example",
    "line_type": "parallel_lines_distance_single_choice",
    "display_order": 4584,
    "source_order": 4584,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4588",
      "textbook_example_id": 4588,
      "generator_key": "src_4588",
      "source_kind": "quiz",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4588",
    "textbook_example_id": 4588,
    "generator_key": "src_4588",
    "seed": null,
    "source_kind": "quiz",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4588,
    "source_order": 4588,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4577",
      "textbook_example_id": 4577,
      "generator_key": "src_4577",
      "source_kind": "example",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4577",
    "textbook_example_id": 4577,
    "generator_key": "src_4577",
    "seed": null,
    "source_kind": "example",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4577,
    "source_order": 4577,
    "sampling_weight": 1.0
  },
  {
    "question_text": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "question": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "correct_answer": "-46/3",
    "answer": "-46/3",
    "display_answer": "$-\\frac{46}{3}$",
    "semantic_answer": "-46/3",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "-46/3",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "solve_parameter_from_parallel_distance",
        "task_type": "solve_parameter_from_parallel_distance",
        "line_type": "solve_parameter_from_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "-46/3",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 4,
        "B": 2,
        "C": 0
      },
      "general_form": "-46/3",
      "line_equation": "-46/3",
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "semantic_answer": "-46/3",
      "problem_type_id": "solve_parameter_from_parallel_distance",
      "component_id": "src_4579",
      "textbook_example_id": 4579,
      "generator_key": "src_4579",
      "source_kind": "example",
      "line_type": "solve_parameter_from_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "checker": "rational_checker",
      "checker_key": "rational_checker",
      "answer_equivalence": "rational_equivalent",
      "equivalence": "rational_equivalent",
      "semantic_answer": "-46/3"
    },
    "checker": "rational_checker",
    "checker_type": "rational_checker",
    "equivalence": "rational_equivalent",
    "problem_type_id": "solve_parameter_from_parallel_distance",
    "component_id": "src_4579",
    "textbook_example_id": 4579,
    "generator_key": "src_4579",
    "seed": null,
    "source_kind": "example",
    "line_type": "solve_parameter_from_parallel_distance",
    "display_order": 4579,
    "source_order": 4579,
    "sampling_weight": 1.0
  },
  {
    "question_text": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "question": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "correct_answer": "74/3",
    "answer": "74/3",
    "display_answer": "$\\frac{74}{3}$",
    "semantic_answer": "74/3",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "74/3",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "solve_parameter_from_parallel_distance",
        "task_type": "solve_parameter_from_parallel_distance",
        "line_type": "solve_parameter_from_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "74/3",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 4,
        "B": 2,
        "C": 0
      },
      "general_form": "74/3",
      "line_equation": "74/3",
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "semantic_answer": "74/3",
      "problem_type_id": "solve_parameter_from_parallel_distance",
      "component_id": "src_4589",
      "textbook_example_id": 4589,
      "generator_key": "src_4589",
      "source_kind": "quiz",
      "line_type": "solve_parameter_from_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "checker": "rational_checker",
      "checker_key": "rational_checker",
      "answer_equivalence": "rational_equivalent",
      "equivalence": "rational_equivalent",
      "semantic_answer": "74/3"
    },
    "checker": "rational_checker",
    "checker_type": "rational_checker",
    "equivalence": "rational_equivalent",
    "problem_type_id": "solve_parameter_from_parallel_distance",
    "component_id": "src_4589",
    "textbook_example_id": 4589,
    "generator_key": "src_4589",
    "seed": null,
    "source_kind": "quiz",
    "line_type": "solve_parameter_from_parallel_distance",
    "display_order": 4589,
    "source_order": 4589,
    "sampling_weight": 1.0
  },
  {
    "question_text": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "question": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "correct_answer": "-46/3, 74/3",
    "answer": "-46/3, 74/3",
    "display_answer": "$\\frac{14}{3} \\pm 20$",
    "semantic_answer": "-46/3, 74/3",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "-46/3, 74/3",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "solve_parameter_from_parallel_distance",
        "task_type": "solve_parameter_from_parallel_distance",
        "line_type": "solve_parameter_from_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "-46/3, 74/3",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 4,
        "B": 2,
        "C": 0
      },
      "general_form": "-46/3, 74/3",
      "line_equation": "-46/3, 74/3",
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "-46/3, 74/3",
      "problem_type_id": "solve_parameter_from_parallel_distance",
      "component_id": "src_4571",
      "textbook_example_id": 4571,
      "generator_key": "src_4571",
      "source_kind": "example",
      "line_type": "solve_parameter_from_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "semantic_answer": "-46/3, 74/3"
    },
    "checker": "solution_set_checker",
    "checker_type": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "problem_type_id": "solve_parameter_from_parallel_distance",
    "component_id": "src_4571",
    "textbook_example_id": 4571,
    "generator_key": "src_4571",
    "seed": null,
    "source_kind": "example",
    "line_type": "solve_parameter_from_parallel_distance",
    "display_order": 4571,
    "source_order": 4571,
    "sampling_weight": 1.0
  },
  {
    "question_text": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "question": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "correct_answer": "-46/3, 74/3",
    "answer": "-46/3, 74/3",
    "display_answer": "$\\frac{14}{3} \\pm 20$",
    "semantic_answer": "-46/3, 74/3",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "-46/3, 74/3",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "solve_parameter_from_parallel_distance",
        "task_type": "solve_parameter_from_parallel_distance",
        "line_type": "solve_parameter_from_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "-46/3, 74/3",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 4,
        "B": 2,
        "C": 0
      },
      "general_form": "-46/3, 74/3",
      "line_equation": "-46/3, 74/3",
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "-46/3, 74/3",
      "problem_type_id": "solve_parameter_from_parallel_distance",
      "component_id": "src_4571",
      "textbook_example_id": 4571,
      "generator_key": "src_4571",
      "source_kind": "example",
      "line_type": "solve_parameter_from_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "semantic_answer": "-46/3, 74/3"
    },
    "checker": "solution_set_checker",
    "checker_type": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "problem_type_id": "solve_parameter_from_parallel_distance",
    "component_id": "src_4571",
    "textbook_example_id": 4571,
    "generator_key": "src_4571",
    "seed": null,
    "source_kind": "example",
    "line_type": "solve_parameter_from_parallel_distance",
    "display_order": 4571,
    "source_order": 4571,
    "sampling_weight": 1.0
  },
  {
    "question_text": "設 A 點坐標為 $(5, -7)$，且 B、C 兩點在直線 L: $2x+y+9 = 0$ 上，若 $\\overline{BC}$ 的長為 $4$，試求 △ABC 的面積。",
    "question": "設 A 點坐標為 $(5, -7)$，且 B、C 兩點在直線 L: $2x+y+9 = 0$ 上，若 $\\overline{BC}$ 的長為 $4$，試求 △ABC 的面積。",
    "correct_answer": "24*sqrt(5)/5",
    "answer": "24*sqrt(5)/5",
    "display_answer": "$\\frac{24\\sqrt{5}}{5}$",
    "semantic_answer": "24*sqrt(5)/5",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "24*sqrt(5)/5",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "area_using_parallel_distance",
        "task_type": "area_using_parallel_distance",
        "line_type": "area_using_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "24*sqrt(5)/5",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": 1,
        "C": 9
      },
      "general_form": "24*sqrt(5)/5",
      "line_equation": "24*sqrt(5)/5",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "24*sqrt(5)/5",
      "problem_type_id": "area_using_parallel_distance",
      "component_id": "src_4583",
      "textbook_example_id": 4583,
      "generator_key": "src_4583",
      "source_kind": "example",
      "line_type": "area_using_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "24*sqrt(5)/5"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "area_using_parallel_distance",
    "component_id": "src_4583",
    "textbook_example_id": 4583,
    "generator_key": "src_4583",
    "seed": null,
    "source_kind": "example",
    "line_type": "area_using_parallel_distance",
    "display_order": 4583,
    "source_order": 4583,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4588",
      "textbook_example_id": 4588,
      "generator_key": "src_4588",
      "source_kind": "quiz",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4588",
    "textbook_example_id": 4588,
    "generator_key": "src_4588",
    "seed": null,
    "source_kind": "quiz",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4588,
    "source_order": 4588,
    "sampling_weight": 1.0
  },
  {
    "question_text": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "question": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "correct_answer": "-46/3",
    "answer": "-46/3",
    "display_answer": "$-\\frac{46}{3}$",
    "semantic_answer": "-46/3",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "-46/3",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "solve_parameter_from_parallel_distance",
        "task_type": "solve_parameter_from_parallel_distance",
        "line_type": "solve_parameter_from_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "-46/3",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 4,
        "B": 2,
        "C": 0
      },
      "general_form": "-46/3",
      "line_equation": "-46/3",
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "semantic_answer": "-46/3",
      "problem_type_id": "solve_parameter_from_parallel_distance",
      "component_id": "src_4579",
      "textbook_example_id": 4579,
      "generator_key": "src_4579",
      "source_kind": "example",
      "line_type": "solve_parameter_from_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "checker": "rational_checker",
      "checker_key": "rational_checker",
      "answer_equivalence": "rational_equivalent",
      "equivalence": "rational_equivalent",
      "semantic_answer": "-46/3"
    },
    "checker": "rational_checker",
    "checker_type": "rational_checker",
    "equivalence": "rational_equivalent",
    "problem_type_id": "solve_parameter_from_parallel_distance",
    "component_id": "src_4579",
    "textbook_example_id": 4579,
    "generator_key": "src_4579",
    "seed": null,
    "source_kind": "example",
    "line_type": "solve_parameter_from_parallel_distance",
    "display_order": 4579,
    "source_order": 4579,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4577",
      "textbook_example_id": 4577,
      "generator_key": "src_4577",
      "source_kind": "example",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4577",
    "textbook_example_id": 4577,
    "generator_key": "src_4577",
    "seed": null,
    "source_kind": "example",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4577,
    "source_order": 4577,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4588",
      "textbook_example_id": 4588,
      "generator_key": "src_4588",
      "source_kind": "quiz",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4588",
    "textbook_example_id": 4588,
    "generator_key": "src_4588",
    "seed": null,
    "source_kind": "quiz",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4588,
    "source_order": 4588,
    "sampling_weight": 1.0
  },
  {
    "question_text": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "question": "坐標平面上，若兩平行線 $4x+2y + k = 0$ 與 $-6x-3y-7 = 0$ 的距離為 $2\\sqrt{5}$，試求 k 之值。",
    "correct_answer": "-46/3",
    "answer": "-46/3",
    "display_answer": "$-\\frac{46}{3}$",
    "semantic_answer": "-46/3",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "-46/3",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "solve_parameter_from_parallel_distance",
        "task_type": "solve_parameter_from_parallel_distance",
        "line_type": "solve_parameter_from_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "-46/3",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 4,
        "B": 2,
        "C": 0
      },
      "general_form": "-46/3",
      "line_equation": "-46/3",
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "semantic_answer": "-46/3",
      "problem_type_id": "solve_parameter_from_parallel_distance",
      "component_id": "src_4579",
      "textbook_example_id": 4579,
      "generator_key": "src_4579",
      "source_kind": "example",
      "line_type": "solve_parameter_from_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "rational",
      "checker": "rational_checker",
      "checker_key": "rational_checker",
      "answer_equivalence": "rational_equivalent",
      "equivalence": "rational_equivalent",
      "semantic_answer": "-46/3"
    },
    "checker": "rational_checker",
    "checker_type": "rational_checker",
    "equivalence": "rational_equivalent",
    "problem_type_id": "solve_parameter_from_parallel_distance",
    "component_id": "src_4579",
    "textbook_example_id": 4579,
    "generator_key": "src_4579",
    "seed": null,
    "source_kind": "example",
    "line_type": "solve_parameter_from_parallel_distance",
    "display_order": 4579,
    "source_order": 4579,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4570",
      "textbook_example_id": 4570,
      "generator_key": "src_4570",
      "source_kind": "example",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4570",
    "textbook_example_id": 4570,
    "generator_key": "src_4570",
    "seed": null,
    "source_kind": "example",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4570,
    "source_order": 4570,
    "sampling_weight": 1.0
  },
  {
    "question_text": "設 A 點坐標為 $(5, -7)$，且 B、C 兩點在直線 L: $2x+y+9 = 0$ 上，若 $\\overline{BC}$ 的長為 $4$，試求 △ABC 的面積。",
    "question": "設 A 點坐標為 $(5, -7)$，且 B、C 兩點在直線 L: $2x+y+9 = 0$ 上，若 $\\overline{BC}$ 的長為 $4$，試求 △ABC 的面積。",
    "correct_answer": "24*sqrt(5)/5",
    "answer": "24*sqrt(5)/5",
    "display_answer": "$\\frac{24\\sqrt{5}}{5}$",
    "semantic_answer": "24*sqrt(5)/5",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "24*sqrt(5)/5",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "area_using_parallel_distance",
        "task_type": "area_using_parallel_distance",
        "line_type": "area_using_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "24*sqrt(5)/5",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": 1,
        "C": 9
      },
      "general_form": "24*sqrt(5)/5",
      "line_equation": "24*sqrt(5)/5",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "24*sqrt(5)/5",
      "problem_type_id": "area_using_parallel_distance",
      "component_id": "src_4583",
      "textbook_example_id": 4583,
      "generator_key": "src_4583",
      "source_kind": "example",
      "line_type": "area_using_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "24*sqrt(5)/5"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "area_using_parallel_distance",
    "component_id": "src_4583",
    "textbook_example_id": 4583,
    "generator_key": "src_4583",
    "seed": null,
    "source_kind": "example",
    "line_type": "area_using_parallel_distance",
    "display_order": 4583,
    "source_order": 4583,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4578",
      "textbook_example_id": 4578,
      "generator_key": "src_4578",
      "source_kind": "example",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4578",
    "textbook_example_id": 4578,
    "generator_key": "src_4578",
    "seed": null,
    "source_kind": "example",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4578,
    "source_order": 4578,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4578",
      "textbook_example_id": 4578,
      "generator_key": "src_4578",
      "source_kind": "example",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4578",
    "textbook_example_id": 4578,
    "generator_key": "src_4578",
    "seed": null,
    "source_kind": "example",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4578,
    "source_order": 4578,
    "sampling_weight": 1.0
  },
  {
    "question_text": "設 A 點坐標為 $(5, -7)$，且 B、C 兩點在直線 L: $2x+y+9 = 0$ 上，若 $\\overline{BC}$ 的長為 $4$，試求 △ABC 的面積。",
    "question": "設 A 點坐標為 $(5, -7)$，且 B、C 兩點在直線 L: $2x+y+9 = 0$ 上，若 $\\overline{BC}$ 的長為 $4$，試求 △ABC 的面積。",
    "correct_answer": "24*sqrt(5)/5",
    "answer": "24*sqrt(5)/5",
    "display_answer": "$\\frac{24\\sqrt{5}}{5}$",
    "semantic_answer": "24*sqrt(5)/5",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "24*sqrt(5)/5",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "area_using_parallel_distance",
        "task_type": "area_using_parallel_distance",
        "line_type": "area_using_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "24*sqrt(5)/5",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": 1,
        "C": 9
      },
      "general_form": "24*sqrt(5)/5",
      "line_equation": "24*sqrt(5)/5",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "24*sqrt(5)/5",
      "problem_type_id": "area_using_parallel_distance",
      "component_id": "src_4583",
      "textbook_example_id": 4583,
      "generator_key": "src_4583",
      "source_kind": "example",
      "line_type": "area_using_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "24*sqrt(5)/5"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "area_using_parallel_distance",
    "component_id": "src_4583",
    "textbook_example_id": 4583,
    "generator_key": "src_4583",
    "seed": null,
    "source_kind": "example",
    "line_type": "area_using_parallel_distance",
    "display_order": 4583,
    "source_order": 4583,
    "sampling_weight": 1.0
  },
  {
    "question_text": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "question": "試求兩平行線 $2x-3y+2 = 0$ 與 $-6x+9y-15 = 0$ 之間的距離。",
    "correct_answer": "3*sqrt(13)/13",
    "answer": "3*sqrt(13)/13",
    "display_answer": "$\\frac{3\\sqrt{13}}{13}$",
    "semantic_answer": "3*sqrt(13)/13",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "distance_between_parallel_lines",
        "task_type": "distance_between_parallel_lines",
        "line_type": "distance_between_parallel_lines",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "3*sqrt(13)/13",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": -3,
        "C": 2
      },
      "general_form": "3*sqrt(13)/13",
      "line_equation": "3*sqrt(13)/13",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "3*sqrt(13)/13",
      "problem_type_id": "distance_between_parallel_lines",
      "component_id": "src_4578",
      "textbook_example_id": 4578,
      "generator_key": "src_4578",
      "source_kind": "example",
      "line_type": "distance_between_parallel_lines"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "3*sqrt(13)/13"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "distance_between_parallel_lines",
    "component_id": "src_4578",
    "textbook_example_id": 4578,
    "generator_key": "src_4578",
    "seed": null,
    "source_kind": "example",
    "line_type": "distance_between_parallel_lines",
    "display_order": 4578,
    "source_order": 4578,
    "sampling_weight": 1.0
  },
  {
    "question_text": "設 A 點坐標為 $(5, -7)$，且 B、C 兩點在直線 L: $2x+y+9 = 0$ 上，若 $\\overline{BC}$ 的長為 $4$，試求 △ABC 的面積。",
    "question": "設 A 點坐標為 $(5, -7)$，且 B、C 兩點在直線 L: $2x+y+9 = 0$ 上，若 $\\overline{BC}$ 的長為 $4$，試求 △ABC 的面積。",
    "correct_answer": "24*sqrt(5)/5",
    "answer": "24*sqrt(5)/5",
    "display_answer": "$\\frac{24\\sqrt{5}}{5}$",
    "semantic_answer": "24*sqrt(5)/5",
    "choices": [],
    "options": [],
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -8,
        8
      ],
      "y_range": [
        -8,
        8
      ]
    },
    "math_core": {
      "givens": [],
      "target": "24*sqrt(5)/5",
      "math_objects": [
        "coordinate_point",
        "linear_equation"
      ],
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "validation_facts": {
        "domain_operation": "area_using_parallel_distance",
        "task_type": "area_using_parallel_distance",
        "line_type": "area_using_parallel_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "presentation_mode": "short_answer",
    "answer_type": "rational",
    "metadata": {
      "givens": [],
      "target": "24*sqrt(5)/5",
      "derivation": [
        "確認兩直線平行（法向量成比例）",
        "使用平行線距離公式 |C1-C2|/sqrt(A^2+B^2)",
        "代入計算並化簡"
      ],
      "coefficients": {
        "A": 2,
        "B": 1,
        "C": 9
      },
      "general_form": "24*sqrt(5)/5",
      "line_equation": "24*sqrt(5)/5",
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "semantic_answer": "24*sqrt(5)/5",
      "problem_type_id": "area_using_parallel_distance",
      "component_id": "src_4583",
      "textbook_example_id": 4583,
      "generator_key": "src_4583",
      "source_kind": "example",
      "line_type": "area_using_parallel_distance"
    },
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "symbolic_radical",
      "checker": "symbolic_expression_checker",
      "checker_key": "symbolic_expression_checker",
      "answer_equivalence": "radical_equivalence",
      "equivalence": "radical_equivalence",
      "semantic_answer": "24*sqrt(5)/5"
    },
    "checker": "symbolic_expression_checker",
    "checker_type": "symbolic_expression_checker",
    "equivalence": "radical_equivalence",
    "problem_type_id": "area_using_parallel_distance",
    "component_id": "src_4583",
    "textbook_example_id": 4583,
    "generator_key": "src_4583",
    "seed": null,
    "source_kind": "example",
    "line_type": "area_using_parallel_distance",
    "display_order": 4583,
    "source_order": 4583,
    "sampling_weight": 1.0
  }
]
```
