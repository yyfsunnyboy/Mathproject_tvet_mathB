# Verify Report: vh_數學B1_PointSlopeForm

- python: C:\Users\Owner\anaconda3\python.exe
- registry: D:\Python\Mathproject_tvet_mathB\configs\generated_registry\b1_section_1_1_verified_registry.v0.1.yaml
- registry_verified_count: 1
- pytest_exit_code: 0
- unique_problem_type_count: 1
- PASS: True

## Runtime ProblemType Coverage
```json
{
  "expected_problem_types": [
    "equation_write_line_equation_from_point_slope_short_answer"
  ],
  "observed_problem_types": [
    "equation_write_line_equation_from_point_slope_short_answer"
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
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "skill_id": "vh_數學B1_PointSlopeForm",
    "subskill_id": "write_line_equation_from_point_slope",
    "status": "verified",
    "candidate_path": "skills/vh_數學B1_PointSlopeForm.py",
    "function_name": "generate",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "wrapper_path": "skills/vh_數學B1_PointSlopeForm.py",
    "manual_review_exclusions": [
      "unknown"
    ],
    "source": "gencode_runtime_binding",
    "phase2_report_path": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_PointSlopeForm_phase2_build.json"
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
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(6, -4)$，斜率為 $-3$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "question": "已知直線過點 $(6, -4)$，斜率為 $-3$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "choices": [],
    "answer": "-3x - y + 14 = 0",
    "correct_answer": "-3x - y + 14 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_general_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - -4 = -3(x - 6)$ 整理，可得一般式 $-3x - y + 14 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_general_form"
    ],
    "metadata": {
      "givens": [
        "point=(6,-4)",
        "slope=-3"
      ],
      "target": "-3x - y + 14 = 0",
      "template_variant": "given_point_and_slope_find_general_form",
      "equation_form": "given_point_and_slope_find_general_form",
      "coefficients": {
        "A": -3,
        "B": -1,
        "C": 14
      },
      "derivation": [
        "y - -4 = -3(x - 6)",
        "-3x - y + 14 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-5, -5)$，斜率為 $5$，求此直線的點斜式方程式。\n（答案範例：5）",
    "question": "已知直線過點 $(-5, -5)$，斜率為 $5$，求此直線的點斜式方程式。\n（答案範例：5）",
    "choices": [],
    "answer": "5x - y + 20 = 0",
    "correct_answer": "5x - y + 20 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_point_slope_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - -5 = 5(x - -5)$ 整理，可得一般式 $5x - y + 20 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_point_slope_form"
    ],
    "metadata": {
      "givens": [
        "point=(-5,-5)",
        "slope=5"
      ],
      "target": "5x - y + 20 = 0",
      "template_variant": "given_point_and_slope_find_point_slope_form",
      "equation_form": "given_point_and_slope_find_point_slope_form",
      "coefficients": {
        "A": 5,
        "B": -1,
        "C": 20
      },
      "derivation": [
        "y - -5 = 5(x - -5)",
        "5x - y + 20 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-3, -1)$，斜率為 $-1$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "question": "已知直線過點 $(-3, -1)$，斜率為 $-1$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "choices": [],
    "answer": "-x - y - 4 = 0",
    "correct_answer": "-x - y - 4 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_slope_intercept_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - -1 = -1(x - -3)$ 整理，可得一般式 $-x - y - 4 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_slope_intercept_form"
    ],
    "metadata": {
      "givens": [
        "point=(-3,-1)",
        "slope=-1"
      ],
      "target": "-x - y - 4 = 0",
      "template_variant": "given_point_and_slope_find_slope_intercept_form",
      "equation_form": "given_point_and_slope_find_slope_intercept_form",
      "coefficients": {
        "A": -1,
        "B": -1,
        "C": -4
      },
      "derivation": [
        "y - -1 = -1(x - -3)",
        "-x - y - 4 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(5, -1)$，斜率為 $-3$，求此直線的點斜式方程式。\n（答案範例：5）",
    "question": "已知直線過點 $(5, -1)$，斜率為 $-3$，求此直線的點斜式方程式。\n（答案範例：5）",
    "choices": [],
    "answer": "-3x - y + 14 = 0",
    "correct_answer": "-3x - y + 14 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_point_slope_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - -1 = -3(x - 5)$ 整理，可得一般式 $-3x - y + 14 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_point_slope_form"
    ],
    "metadata": {
      "givens": [
        "point=(5,-1)",
        "slope=-3"
      ],
      "target": "-3x - y + 14 = 0",
      "template_variant": "given_point_and_slope_find_point_slope_form",
      "equation_form": "given_point_and_slope_find_point_slope_form",
      "coefficients": {
        "A": -3,
        "B": -1,
        "C": 14
      },
      "derivation": [
        "y - -1 = -3(x - 5)",
        "-3x - y + 14 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-3, 3)$，斜率為 $-2$，求此直線的點斜式方程式。\n（答案範例：5）",
    "question": "已知直線過點 $(-3, 3)$，斜率為 $-2$，求此直線的點斜式方程式。\n（答案範例：5）",
    "choices": [],
    "answer": "-2x - y - 3 = 0",
    "correct_answer": "-2x - y - 3 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_point_slope_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 3 = -2(x - -3)$ 整理，可得一般式 $-2x - y - 3 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_point_slope_form"
    ],
    "metadata": {
      "givens": [
        "point=(-3,3)",
        "slope=-2"
      ],
      "target": "-2x - y - 3 = 0",
      "template_variant": "given_point_and_slope_find_point_slope_form",
      "equation_form": "given_point_and_slope_find_point_slope_form",
      "coefficients": {
        "A": -2,
        "B": -1,
        "C": -3
      },
      "derivation": [
        "y - 3 = -2(x - -3)",
        "-2x - y - 3 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-3, -3)$，斜率為 $-5$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "question": "已知直線過點 $(-3, -3)$，斜率為 $-5$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "choices": [],
    "answer": "-5x - y - 18 = 0",
    "correct_answer": "-5x - y - 18 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_slope_intercept_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - -3 = -5(x - -3)$ 整理，可得一般式 $-5x - y - 18 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_slope_intercept_form"
    ],
    "metadata": {
      "givens": [
        "point=(-3,-3)",
        "slope=-5"
      ],
      "target": "-5x - y - 18 = 0",
      "template_variant": "given_point_and_slope_find_slope_intercept_form",
      "equation_form": "given_point_and_slope_find_slope_intercept_form",
      "coefficients": {
        "A": -5,
        "B": -1,
        "C": -18
      },
      "derivation": [
        "y - -3 = -5(x - -3)",
        "-5x - y - 18 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-7, 8)$，斜率為 $-1$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "question": "已知直線過點 $(-7, 8)$，斜率為 $-1$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "choices": [],
    "answer": "-x - y + 1 = 0",
    "correct_answer": "-x - y + 1 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_general_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 8 = -1(x - -7)$ 整理，可得一般式 $-x - y + 1 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_general_form"
    ],
    "metadata": {
      "givens": [
        "point=(-7,8)",
        "slope=-1"
      ],
      "target": "-x - y + 1 = 0",
      "template_variant": "given_point_and_slope_find_general_form",
      "equation_form": "given_point_and_slope_find_general_form",
      "coefficients": {
        "A": -1,
        "B": -1,
        "C": 1
      },
      "derivation": [
        "y - 8 = -1(x - -7)",
        "-x - y + 1 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(7, 8)$，斜率為 $-3/2$，求此直線的點斜式方程式。\n（答案範例：5）",
    "question": "已知直線過點 $(7, 8)$，斜率為 $-3/2$，求此直線的點斜式方程式。\n（答案範例：5）",
    "choices": [],
    "answer": "-3x - 2y + 37 = 0",
    "correct_answer": "-3x - 2y + 37 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_point_slope_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 8 = -3/2(x - 7)$ 整理，可得一般式 $-3x - 2y + 37 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_point_slope_form"
    ],
    "metadata": {
      "givens": [
        "point=(7,8)",
        "slope=-3/2"
      ],
      "target": "-3x - 2y + 37 = 0",
      "template_variant": "given_point_and_slope_find_point_slope_form",
      "equation_form": "given_point_and_slope_find_point_slope_form",
      "coefficients": {
        "A": -3,
        "B": -2,
        "C": 37
      },
      "derivation": [
        "y - 8 = -3/2(x - 7)",
        "-3x - 2y + 37 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-5, 4)$，斜率為 $-2/3$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "question": "已知直線過點 $(-5, 4)$，斜率為 $-2/3$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "choices": [],
    "answer": "-2x - 3y + 2 = 0",
    "correct_answer": "-2x - 3y + 2 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_general_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 4 = -2/3(x - -5)$ 整理，可得一般式 $-2x - 3y + 2 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_general_form"
    ],
    "metadata": {
      "givens": [
        "point=(-5,4)",
        "slope=-2/3"
      ],
      "target": "-2x - 3y + 2 = 0",
      "template_variant": "given_point_and_slope_find_general_form",
      "equation_form": "given_point_and_slope_find_general_form",
      "coefficients": {
        "A": -2,
        "B": -3,
        "C": 2
      },
      "derivation": [
        "y - 4 = -2/3(x - -5)",
        "-2x - 3y + 2 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(2, 2)$，斜率為 $4$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "question": "已知直線過點 $(2, 2)$，斜率為 $4$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "choices": [],
    "answer": "4x - y - 6 = 0",
    "correct_answer": "4x - y - 6 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_slope_intercept_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 2 = 4(x - 2)$ 整理，可得一般式 $4x - y - 6 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_slope_intercept_form"
    ],
    "metadata": {
      "givens": [
        "point=(2,2)",
        "slope=4"
      ],
      "target": "4x - y - 6 = 0",
      "template_variant": "given_point_and_slope_find_slope_intercept_form",
      "equation_form": "given_point_and_slope_find_slope_intercept_form",
      "coefficients": {
        "A": 4,
        "B": -1,
        "C": -6
      },
      "derivation": [
        "y - 2 = 4(x - 2)",
        "4x - y - 6 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(4, 0)$，斜率為 $1/3$，求此直線的點斜式方程式。\n（答案範例：5）",
    "question": "已知直線過點 $(4, 0)$，斜率為 $1/3$，求此直線的點斜式方程式。\n（答案範例：5）",
    "choices": [],
    "answer": "x - 3y - 4 = 0",
    "correct_answer": "x - 3y - 4 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_point_slope_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 0 = 1/3(x - 4)$ 整理，可得一般式 $x - 3y - 4 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_point_slope_form"
    ],
    "metadata": {
      "givens": [
        "point=(4,0)",
        "slope=1/3"
      ],
      "target": "x - 3y - 4 = 0",
      "template_variant": "given_point_and_slope_find_point_slope_form",
      "equation_form": "given_point_and_slope_find_point_slope_form",
      "coefficients": {
        "A": 1,
        "B": -3,
        "C": -4
      },
      "derivation": [
        "y - 0 = 1/3(x - 4)",
        "x - 3y - 4 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-2, -6)$，斜率為 $-1$，求此直線的點斜式方程式。\n（答案範例：5）",
    "question": "已知直線過點 $(-2, -6)$，斜率為 $-1$，求此直線的點斜式方程式。\n（答案範例：5）",
    "choices": [],
    "answer": "-x - y - 8 = 0",
    "correct_answer": "-x - y - 8 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_point_slope_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - -6 = -1(x - -2)$ 整理，可得一般式 $-x - y - 8 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_point_slope_form"
    ],
    "metadata": {
      "givens": [
        "point=(-2,-6)",
        "slope=-1"
      ],
      "target": "-x - y - 8 = 0",
      "template_variant": "given_point_and_slope_find_point_slope_form",
      "equation_form": "given_point_and_slope_find_point_slope_form",
      "coefficients": {
        "A": -1,
        "B": -1,
        "C": -8
      },
      "derivation": [
        "y - -6 = -1(x - -2)",
        "-x - y - 8 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(4, -1)$，斜率為 $-1$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "question": "已知直線過點 $(4, -1)$，斜率為 $-1$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "choices": [],
    "answer": "-x - y + 3 = 0",
    "correct_answer": "-x - y + 3 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_slope_intercept_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - -1 = -1(x - 4)$ 整理，可得一般式 $-x - y + 3 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_slope_intercept_form"
    ],
    "metadata": {
      "givens": [
        "point=(4,-1)",
        "slope=-1"
      ],
      "target": "-x - y + 3 = 0",
      "template_variant": "given_point_and_slope_find_slope_intercept_form",
      "equation_form": "given_point_and_slope_find_slope_intercept_form",
      "coefficients": {
        "A": -1,
        "B": -1,
        "C": 3
      },
      "derivation": [
        "y - -1 = -1(x - 4)",
        "-x - y + 3 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(7, 6)$，斜率為 $1$，求此直線的點斜式方程式。\n（答案範例：5）",
    "question": "已知直線過點 $(7, 6)$，斜率為 $1$，求此直線的點斜式方程式。\n（答案範例：5）",
    "choices": [],
    "answer": "x - y - 1 = 0",
    "correct_answer": "x - y - 1 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_point_slope_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 6 = 1(x - 7)$ 整理，可得一般式 $x - y - 1 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_point_slope_form"
    ],
    "metadata": {
      "givens": [
        "point=(7,6)",
        "slope=1"
      ],
      "target": "x - y - 1 = 0",
      "template_variant": "given_point_and_slope_find_point_slope_form",
      "equation_form": "given_point_and_slope_find_point_slope_form",
      "coefficients": {
        "A": 1,
        "B": -1,
        "C": -1
      },
      "derivation": [
        "y - 6 = 1(x - 7)",
        "x - y - 1 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(5, -5)$，斜率為 $4$，求此直線的點斜式方程式。\n（答案範例：5）",
    "question": "已知直線過點 $(5, -5)$，斜率為 $4$，求此直線的點斜式方程式。\n（答案範例：5）",
    "choices": [],
    "answer": "4x - y - 25 = 0",
    "correct_answer": "4x - y - 25 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_point_slope_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - -5 = 4(x - 5)$ 整理，可得一般式 $4x - y - 25 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_point_slope_form"
    ],
    "metadata": {
      "givens": [
        "point=(5,-5)",
        "slope=4"
      ],
      "target": "4x - y - 25 = 0",
      "template_variant": "given_point_and_slope_find_point_slope_form",
      "equation_form": "given_point_and_slope_find_point_slope_form",
      "coefficients": {
        "A": 4,
        "B": -1,
        "C": -25
      },
      "derivation": [
        "y - -5 = 4(x - 5)",
        "4x - y - 25 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(6, 3)$，斜率為 $-2$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "question": "已知直線過點 $(6, 3)$，斜率為 $-2$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "choices": [],
    "answer": "-2x - y + 15 = 0",
    "correct_answer": "-2x - y + 15 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_slope_intercept_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 3 = -2(x - 6)$ 整理，可得一般式 $-2x - y + 15 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_slope_intercept_form"
    ],
    "metadata": {
      "givens": [
        "point=(6,3)",
        "slope=-2"
      ],
      "target": "-2x - y + 15 = 0",
      "template_variant": "given_point_and_slope_find_slope_intercept_form",
      "equation_form": "given_point_and_slope_find_slope_intercept_form",
      "coefficients": {
        "A": -2,
        "B": -1,
        "C": 15
      },
      "derivation": [
        "y - 3 = -2(x - 6)",
        "-2x - y + 15 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(1, 7)$，斜率為 $5$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "question": "已知直線過點 $(1, 7)$，斜率為 $5$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "choices": [],
    "answer": "5x - y + 2 = 0",
    "correct_answer": "5x - y + 2 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_general_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 7 = 5(x - 1)$ 整理，可得一般式 $5x - y + 2 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_general_form"
    ],
    "metadata": {
      "givens": [
        "point=(1,7)",
        "slope=5"
      ],
      "target": "5x - y + 2 = 0",
      "template_variant": "given_point_and_slope_find_general_form",
      "equation_form": "given_point_and_slope_find_general_form",
      "coefficients": {
        "A": 5,
        "B": -1,
        "C": 2
      },
      "derivation": [
        "y - 7 = 5(x - 1)",
        "5x - y + 2 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-5, 2)$，斜率為 $1/3$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "question": "已知直線過點 $(-5, 2)$，斜率為 $1/3$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "choices": [],
    "answer": "x - 3y + 11 = 0",
    "correct_answer": "x - 3y + 11 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_general_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 2 = 1/3(x - -5)$ 整理，可得一般式 $x - 3y + 11 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_general_form"
    ],
    "metadata": {
      "givens": [
        "point=(-5,2)",
        "slope=1/3"
      ],
      "target": "x - 3y + 11 = 0",
      "template_variant": "given_point_and_slope_find_general_form",
      "equation_form": "given_point_and_slope_find_general_form",
      "coefficients": {
        "A": 1,
        "B": -3,
        "C": 11
      },
      "derivation": [
        "y - 2 = 1/3(x - -5)",
        "x - 3y + 11 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-5, 5)$，斜率為 $-2$，求此直線的點斜式方程式。\n（答案範例：5）",
    "question": "已知直線過點 $(-5, 5)$，斜率為 $-2$，求此直線的點斜式方程式。\n（答案範例：5）",
    "choices": [],
    "answer": "-2x - y - 5 = 0",
    "correct_answer": "-2x - y - 5 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_point_slope_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 5 = -2(x - -5)$ 整理，可得一般式 $-2x - y - 5 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_point_slope_form"
    ],
    "metadata": {
      "givens": [
        "point=(-5,5)",
        "slope=-2"
      ],
      "target": "-2x - y - 5 = 0",
      "template_variant": "given_point_and_slope_find_point_slope_form",
      "equation_form": "given_point_and_slope_find_point_slope_form",
      "coefficients": {
        "A": -2,
        "B": -1,
        "C": -5
      },
      "derivation": [
        "y - 5 = -2(x - -5)",
        "-2x - y - 5 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(5, -7)$，斜率為 $-5$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "question": "已知直線過點 $(5, -7)$，斜率為 $-5$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "choices": [],
    "answer": "-5x - y + 18 = 0",
    "correct_answer": "-5x - y + 18 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_general_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - -7 = -5(x - 5)$ 整理，可得一般式 $-5x - y + 18 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_general_form"
    ],
    "metadata": {
      "givens": [
        "point=(5,-7)",
        "slope=-5"
      ],
      "target": "-5x - y + 18 = 0",
      "template_variant": "given_point_and_slope_find_general_form",
      "equation_form": "given_point_and_slope_find_general_form",
      "coefficients": {
        "A": -5,
        "B": -1,
        "C": 18
      },
      "derivation": [
        "y - -7 = -5(x - 5)",
        "-5x - y + 18 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-3, 4)$，斜率為 $5$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "question": "已知直線過點 $(-3, 4)$，斜率為 $5$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "choices": [],
    "answer": "5x - y + 19 = 0",
    "correct_answer": "5x - y + 19 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_general_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 4 = 5(x - -3)$ 整理，可得一般式 $5x - y + 19 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_general_form"
    ],
    "metadata": {
      "givens": [
        "point=(-3,4)",
        "slope=5"
      ],
      "target": "5x - y + 19 = 0",
      "template_variant": "given_point_and_slope_find_general_form",
      "equation_form": "given_point_and_slope_find_general_form",
      "coefficients": {
        "A": 5,
        "B": -1,
        "C": 19
      },
      "derivation": [
        "y - 4 = 5(x - -3)",
        "5x - y + 19 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(1, 5)$，斜率為 $-1$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "question": "已知直線過點 $(1, 5)$，斜率為 $-1$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "choices": [],
    "answer": "-x - y + 6 = 0",
    "correct_answer": "-x - y + 6 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_slope_intercept_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 5 = -1(x - 1)$ 整理，可得一般式 $-x - y + 6 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_slope_intercept_form"
    ],
    "metadata": {
      "givens": [
        "point=(1,5)",
        "slope=-1"
      ],
      "target": "-x - y + 6 = 0",
      "template_variant": "given_point_and_slope_find_slope_intercept_form",
      "equation_form": "given_point_and_slope_find_slope_intercept_form",
      "coefficients": {
        "A": -1,
        "B": -1,
        "C": 6
      },
      "derivation": [
        "y - 5 = -1(x - 1)",
        "-x - y + 6 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-4, -8)$，斜率為 $-1$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "question": "已知直線過點 $(-4, -8)$，斜率為 $-1$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "choices": [],
    "answer": "-x - y - 12 = 0",
    "correct_answer": "-x - y - 12 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_general_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - -8 = -1(x - -4)$ 整理，可得一般式 $-x - y - 12 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_general_form"
    ],
    "metadata": {
      "givens": [
        "point=(-4,-8)",
        "slope=-1"
      ],
      "target": "-x - y - 12 = 0",
      "template_variant": "given_point_and_slope_find_general_form",
      "equation_form": "given_point_and_slope_find_general_form",
      "coefficients": {
        "A": -1,
        "B": -1,
        "C": -12
      },
      "derivation": [
        "y - -8 = -1(x - -4)",
        "-x - y - 12 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(7, 3)$，斜率為 $-5$，求此直線的點斜式方程式。\n（答案範例：5）",
    "question": "已知直線過點 $(7, 3)$，斜率為 $-5$，求此直線的點斜式方程式。\n（答案範例：5）",
    "choices": [],
    "answer": "-5x - y + 38 = 0",
    "correct_answer": "-5x - y + 38 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_point_slope_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 3 = -5(x - 7)$ 整理，可得一般式 $-5x - y + 38 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_point_slope_form"
    ],
    "metadata": {
      "givens": [
        "point=(7,3)",
        "slope=-5"
      ],
      "target": "-5x - y + 38 = 0",
      "template_variant": "given_point_and_slope_find_point_slope_form",
      "equation_form": "given_point_and_slope_find_point_slope_form",
      "coefficients": {
        "A": -5,
        "B": -1,
        "C": 38
      },
      "derivation": [
        "y - 3 = -5(x - 7)",
        "-5x - y + 38 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-3, 7)$，斜率為 $1$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "question": "已知直線過點 $(-3, 7)$，斜率為 $1$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "choices": [],
    "answer": "x - y + 10 = 0",
    "correct_answer": "x - y + 10 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_slope_intercept_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 7 = 1(x - -3)$ 整理，可得一般式 $x - y + 10 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_slope_intercept_form"
    ],
    "metadata": {
      "givens": [
        "point=(-3,7)",
        "slope=1"
      ],
      "target": "x - y + 10 = 0",
      "template_variant": "given_point_and_slope_find_slope_intercept_form",
      "equation_form": "given_point_and_slope_find_slope_intercept_form",
      "coefficients": {
        "A": 1,
        "B": -1,
        "C": 10
      },
      "derivation": [
        "y - 7 = 1(x - -3)",
        "x - y + 10 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(3, 8)$，斜率為 $-1/2$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "question": "已知直線過點 $(3, 8)$，斜率為 $-1/2$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "choices": [],
    "answer": "-x - 2y + 19 = 0",
    "correct_answer": "-x - 2y + 19 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_general_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 8 = -1/2(x - 3)$ 整理，可得一般式 $-x - 2y + 19 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_general_form"
    ],
    "metadata": {
      "givens": [
        "point=(3,8)",
        "slope=-1/2"
      ],
      "target": "-x - 2y + 19 = 0",
      "template_variant": "given_point_and_slope_find_general_form",
      "equation_form": "given_point_and_slope_find_general_form",
      "coefficients": {
        "A": -1,
        "B": -2,
        "C": 19
      },
      "derivation": [
        "y - 8 = -1/2(x - 3)",
        "-x - 2y + 19 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(3, 0)$，斜率為 $4$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "question": "已知直線過點 $(3, 0)$，斜率為 $4$，求此直線的斜截式方程式（$y = mx + b$）。\n（答案範例：5）",
    "choices": [],
    "answer": "4x - y - 12 = 0",
    "correct_answer": "4x - y - 12 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_slope_intercept_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 0 = 4(x - 3)$ 整理，可得一般式 $4x - y - 12 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_slope_intercept_form"
    ],
    "metadata": {
      "givens": [
        "point=(3,0)",
        "slope=4"
      ],
      "target": "4x - y - 12 = 0",
      "template_variant": "given_point_and_slope_find_slope_intercept_form",
      "equation_form": "given_point_and_slope_find_slope_intercept_form",
      "coefficients": {
        "A": 4,
        "B": -1,
        "C": -12
      },
      "derivation": [
        "y - 0 = 4(x - 3)",
        "4x - y - 12 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(0, -1)$，斜率為 $-5$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "question": "已知直線過點 $(0, -1)$，斜率為 $-5$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "choices": [],
    "answer": "-5x - y - 1 = 0",
    "correct_answer": "-5x - y - 1 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_general_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - -1 = -5(x - 0)$ 整理，可得一般式 $-5x - y - 1 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_general_form"
    ],
    "metadata": {
      "givens": [
        "point=(0,-1)",
        "slope=-5"
      ],
      "target": "-5x - y - 1 = 0",
      "template_variant": "given_point_and_slope_find_general_form",
      "equation_form": "given_point_and_slope_find_general_form",
      "coefficients": {
        "A": -5,
        "B": -1,
        "C": -1
      },
      "derivation": [
        "y - -1 = -5(x - 0)",
        "-5x - y - 1 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(7, 1)$，斜率為 $5$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "question": "已知直線過點 $(7, 1)$，斜率為 $5$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "choices": [],
    "answer": "5x - y - 34 = 0",
    "correct_answer": "5x - y - 34 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_general_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 1 = 5(x - 7)$ 整理，可得一般式 $5x - y - 34 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_general_form"
    ],
    "metadata": {
      "givens": [
        "point=(7,1)",
        "slope=5"
      ],
      "target": "5x - y - 34 = 0",
      "template_variant": "given_point_and_slope_find_general_form",
      "equation_form": "given_point_and_slope_find_general_form",
      "coefficients": {
        "A": 5,
        "B": -1,
        "C": -34
      },
      "derivation": [
        "y - 1 = 5(x - 7)",
        "5x - y - 34 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  },
  {
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_type_id": "equation_write_line_equation_from_point_slope_short_answer",
    "question_text": "已知直線過點 $(-4, 8)$，斜率為 $1/2$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "question": "已知直線過點 $(-4, 8)$，斜率為 $1/2$，求此直線的一般式方程式（$Ax + By + C = 0$）。\n（答案範例：5）",
    "choices": [],
    "answer": "x - 2y + 20 = 0",
    "correct_answer": "x - 2y + 20 = 0",
    "answer_type": "equation",
    "checker_type": "linear_equation_equivalent_checker",
    "checker": "linear_equation_equivalent_checker",
    "checker_key": "linear_equation_equivalent_checker",
    "equivalence": "linear_equation_equivalent",
    "equivalence_type": "linear_equation_equivalent",
    "target_task": "write_line_equation_from_point_slope",
    "task_family": "line_equation_family",
    "template_variant": "given_point_and_slope_find_general_form",
    "answer_contract": {
      "choices_required": false,
      "choice_count": null,
      "correct_choice_count": null,
      "frontend_render_choices": false,
      "source_has_choices": false,
      "answer_type": "equation",
      "answer_shape": "linear_equation",
      "answer_semantics": "line_equation",
      "answer_equivalence": "linear_equation_equivalent",
      "equivalence_type": "linear_equation_equivalent",
      "checker": "linear_equation_equivalent_checker",
      "checker_key": "linear_equation_equivalent_checker",
      "presentation_mode": "short_answer",
      "selected_checker": "linear_equation_equivalent_checker",
      "checker_selection_reason": "line_equation_family",
      "accepted_formats": [
        "y - 2 = 3(x - 1)",
        "y = 3x - 1",
        "3x - y - 1 = 0"
      ],
      "fallback_checker": "text_short_checker",
      "fallback_checker_key": "text_short_checker"
    },
    "presentation_mode": "short_answer",
    "explanation": "由點斜式 $y - 8 = 1/2(x - -4)$ 整理，可得一般式 $x - 2y + 20 = 0$。",
    "diagnosis_tags": [
      "line_equation",
      "point_slope_form",
      "given_point_and_slope_find_general_form"
    ],
    "metadata": {
      "givens": [
        "point=(-4,8)",
        "slope=1/2"
      ],
      "target": "x - 2y + 20 = 0",
      "template_variant": "given_point_and_slope_find_general_form",
      "equation_form": "given_point_and_slope_find_general_form",
      "coefficients": {
        "A": 1,
        "B": -2,
        "C": 20
      },
      "derivation": [
        "y - 8 = 1/2(x - -4)",
        "x - 2y + 20 = 0"
      ],
      "semantic_required_concepts": [],
      "answer_format_suffix": "（答案範例：5）"
    },
    "source": "gencode_slot_generator"
  }
]
```
