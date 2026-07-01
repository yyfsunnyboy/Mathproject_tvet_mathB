# Verify Report: vh_數學B1_DistanceBetweenTwoPointsInPlane

- python: C:\Python314\python.exe
- registry: E:\Python\Mathproject_tvet_mathB\configs\generated_registry\b1_section_1_1_verified_registry.v0.1.yaml
- registry_verified_count: 2
- pytest_exit_code: 0
- unique_problem_type_count: 2
- PASS: True

## Runtime ProblemType Coverage
```json
{
  "expected_problem_types": [
    "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
  ],
  "observed_problem_types": [
    "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
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
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "compute_distance_between_two_points",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_1/compute_distance_between_two_points/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "text_short",
    "checker_type": "text_short_checker"
  },
  {
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "solve_unknown_coordinate_from_two_point_distance",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_1/solve_unknown_coordinate_from_two_point_distance/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "solution_set",
    "checker_type": "solution_set_checker"
  }
]
```

## Pytest Output
```text
..                                                                       [100%]
============================== warnings summary ===============================
C:\Python314\Lib\site-packages\google\genai\types.py:43
  C:\Python314\Lib\site-packages\google\genai\types.py:43: DeprecationWarning: '_UnionGenericAlias' is deprecated and slated for removal in Python 3.17
    VersionedUnionType = Union[builtin_types.UnionType, _UnionGenericAlias]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2 passed, 1 warning in 1.31s
```

## Samples
```json
[
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "answer": "sqrt(146)",
    "correct_answer": "sqrt(146)",
    "display_answer": "sqrt(146)",
    "choices": [],
    "options": [],
    "component_id": "src_4436",
    "textbook_example_id": 4436,
    "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "text_short",
    "checker": "integer_checker",
    "checker_key": "integer_checker",
    "equivalence": "numeric_exact",
    "equivalence_type": "numeric_exact",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "checker": "integer_checker",
      "checker_key": "integer_checker",
      "answer_equivalence": "numeric_exact",
      "equivalence": "numeric_exact",
      "equivalence_type": "numeric_exact",
      "semantic_answer": "sqrt(146)",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "text_short",
      "semantic_answer": "sqrt(146)",
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "component_id": "src_4436",
      "textbook_example_id": 4436,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "raw_givens": {
        "x1": 2,
        "y1": 3,
        "x2": -9,
        "y2": -2,
        "point_a": "(2,3)",
        "point_b": "(-9,-2)"
      },
      "target": "sqrt(146)",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "compute_distance_between_two_points",
        "task_type": "compute_distance_between_two_points",
        "line_type": "compute_distance_between_two_points",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "compute_distance_between_two_points",
      "task_type": "compute_distance_between_two_points",
      "line_type": "compute_distance_between_two_points",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4436",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
    "checker_type": "text_short_checker",
    "question": "已知坐標平面上兩點 $A(2, 3)$、$B(-9, -2)$，試求 $A$、$B$ 兩點的距離。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  },
  {
    "question_text": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "answer": "[-6, 4]",
    "correct_answer": "[-6, 4]",
    "display_answer": "[-6, 4]",
    "choices": [],
    "options": [],
    "component_id": "src_4419",
    "textbook_example_id": 4419,
    "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "source_kind": null,
    "presentation_mode": "short_answer",
    "answer_type": "solution_set",
    "checker": "solution_set_checker",
    "checker_key": "solution_set_checker",
    "equivalence": "unordered_solution_set",
    "equivalence_type": "unordered_solution_set",
    "interaction_type": "expression",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "checker": "solution_set_checker",
      "checker_key": "solution_set_checker",
      "answer_equivalence": "unordered_solution_set",
      "equivalence": "unordered_solution_set",
      "equivalence_type": "unordered_solution_set",
      "semantic_answer": "[-6, 4]",
      "ui_contract": null
    },
    "metadata": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "presentation_mode": "short_answer",
      "answer_type": "solution_set",
      "semantic_answer": "[-6, 4]",
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "component_id": "src_4419",
      "textbook_example_id": 4419,
      "interaction_type": "expression",
      "auto_checkable": true,
      "grading_mode": "auto",
      "parameter_signature": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:seed=None",
      "verified_problem_types": [
        "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    },
    "math_core": {
      "givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "raw_givens": {
        "x1": 1,
        "y1": -1,
        "x2": 13,
        "y2": "k",
        "distance": 13,
        "unknown_parameter": "k"
      },
      "target": "[-6, 4]",
      "math_objects": [
        "frequency_table",
        "frequency"
      ],
      "derivation": [
        "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
        "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
      ],
      "validation_facts": {
        "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
        "task_type": "solve_unknown_coordinate_from_two_point_distance",
        "line_type": "solve_unknown_coordinate_from_two_point_distance",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy"
      }
    },
    "visual_spec": null,
    "visual_aids": [],
    "image_base64": "",
    "validation_facts": {
      "domain_operation": "solve_unknown_coordinate_from_two_point_distance",
      "task_type": "solve_unknown_coordinate_from_two_point_distance",
      "line_type": "solve_unknown_coordinate_from_two_point_distance",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy"
    },
    "generator_key": "src_4419",
    "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "subskill_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
    "checker_type": "solution_set_checker",
    "question": "設 $A(1, -1)$、$B(13, k)$ 為坐標平面上兩點，且其距離為 $13$，試求 $k$ 值。",
    "solution_steps": [
      "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
      "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
    ],
    "explanation": "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).\nFor unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
  }
]
```
