# Verify Report: vh_數學B1_MidpointCoordinates

- python: C:\Python311\python.exe
- registry: C:\Python\Mathproject_tvet_mathB\configs\generated_registry\b1_section_1_1_verified_registry.v0.1.yaml
- registry_verified_count: 2
- pytest_exit_code: 0
- unique_problem_type_count: 2
- PASS: True

## Runtime ProblemType Coverage
```json
{
  "expected_problem_types": [
    "compute_centroid_coordinates",
    "compute_midpoint_coordinates"
  ],
  "observed_problem_types": [
    "compute_centroid_coordinates",
    "compute_midpoint_coordinates"
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
    "problem_type_id": "compute_centroid_coordinates",
    "skill_id": "vh_數學B1_MidpointCoordinates",
    "subskill_id": "compute_centroid_coordinates",
    "status": "verified",
    "candidate_path": "agent_skills_v3/vh_數學B1_MidpointCoordinates/components",
    "function_name": "generate",
    "answer_type": "coordinate_pair",
    "checker_type": "coordinate_pair_checker"
  },
  {
    "problem_type_id": "compute_midpoint_coordinates",
    "skill_id": "vh_數學B1_MidpointCoordinates",
    "subskill_id": "compute_midpoint_coordinates",
    "status": "verified",
    "candidate_path": "agent_skills_v3/vh_數學B1_MidpointCoordinates/components",
    "function_name": "generate",
    "answer_type": "coordinate_pair",
    "checker_type": "coordinate_pair_checker"
  }
]
```

## Pytest Output
```text
.                                                                        [100%]
============================== warnings summary ===============================
core\ai_wrapper.py:37
  C:\Python\Mathproject_tvet_mathB\core\ai_wrapper.py:37: FutureWarning: 
  
  All support for the `google.generativeai` package has ended. It will no longer be receiving 
  updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
  See README for more details:
  
  https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md
  
    import google.generativeai as old_genai

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1 passed, 1 warning in 1.66s
```

## Samples
```json
[
  {
    "question_text": "已知 A(1,9)、B(-7,-55)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=1:3$，求 P 坐標。",
    "answer": "(-1,-7)",
    "correct_answer": "(-1,-7)",
    "display_answer": "(-1,-7)",
    "choices": [],
    "options": [],
    "component_id": "src_4514",
    "textbook_example_id": 4514,
    "problem_type_id": "compute_centroid_coordinates",
    "source_kind": "test",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-1,-7)"
    },
    "metadata": {
      "target": "(-1,-7)",
      "domain_operation": "compute_centroid_coordinates",
      "textbook_example_id": 4514,
      "component_id": "src_4514",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_centroid_coordinates",
      "source_kind": "test",
      "line_type": "compute_centroid_coordinates"
    },
    "math_core": {
      "target": "(-1,-7)",
      "domain_operation": "compute_centroid_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_centroid_coordinates",
      "task_type": "compute_centroid_coordinates",
      "line_type": "compute_centroid_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "hard",
      "canonical_answer": "(-1,-7)"
    },
    "generator_key": "src_4514",
    "explanation": "內分點公式：P=((3·A+1·B)/(1+3))，得 P=(-1,-7)。",
    "seed": null,
    "line_type": "compute_centroid_coordinates",
    "display_order": 4514,
    "source_order": 4514,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(-8,-3)、B(1,-3)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=5:4$，求 P 坐標。",
    "answer": "(-3,-3)",
    "correct_answer": "(-3,-3)",
    "display_answer": "(-3,-3)",
    "choices": [],
    "options": [],
    "component_id": "src_4439",
    "textbook_example_id": 4439,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "quiz",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-3,-3)"
    },
    "metadata": {
      "target": "(-3,-3)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4439,
      "component_id": "src_4439",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "quiz",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(-3,-3)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(-3,-3)"
    },
    "generator_key": "src_4439",
    "explanation": "內分點公式：P=((4·A+5·B)/(5+4))，得 P=(-3,-3)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4439,
    "source_order": 4439,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(0,1)、B(14,1)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=4:3$，求 P 坐標。",
    "answer": "(8,1)",
    "correct_answer": "(8,1)",
    "display_answer": "(8,1)",
    "choices": [],
    "options": [],
    "component_id": "src_4422",
    "textbook_example_id": 4422,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(8,1)"
    },
    "metadata": {
      "target": "(8,1)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4422,
      "component_id": "src_4422",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(8,1)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(8,1)"
    },
    "generator_key": "src_4422",
    "explanation": "內分點公式：P=((3·A+4·B)/(4+3))，得 P=(8,1)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4422,
    "source_order": 4422,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(0,5)、B(7,5)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=4:3$，求 P 坐標。",
    "answer": "(4,5)",
    "correct_answer": "(4,5)",
    "display_answer": "(4,5)",
    "choices": [],
    "options": [],
    "component_id": "src_4429",
    "textbook_example_id": 4429,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(4,5)"
    },
    "metadata": {
      "target": "(4,5)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4429,
      "component_id": "src_4429",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(4,5)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(4,5)"
    },
    "generator_key": "src_4429",
    "explanation": "內分點公式：P=((3·A+4·B)/(4+3))，得 P=(4,5)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4429,
    "source_order": 4429,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(10,-5)、B(-35,4)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=4:5$，求 P 坐標。",
    "answer": "(-10,-1)",
    "correct_answer": "(-10,-1)",
    "display_answer": "(-10,-1)",
    "choices": [],
    "options": [],
    "component_id": "src_4418",
    "textbook_example_id": 4418,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-10,-1)"
    },
    "metadata": {
      "target": "(-10,-1)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4418,
      "component_id": "src_4418",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(-10,-1)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(-10,-1)"
    },
    "generator_key": "src_4418",
    "explanation": "內分點公式：P=((5·A+4·B)/(4+5))，得 P=(-10,-1)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4418,
    "source_order": 4418,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(-7,-7)、B(45,-7)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=1:3$，求 P 坐標。",
    "answer": "(6,-7)",
    "correct_answer": "(6,-7)",
    "display_answer": "(6,-7)",
    "choices": [],
    "options": [],
    "component_id": "src_4443",
    "textbook_example_id": 4443,
    "problem_type_id": "compute_centroid_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(6,-7)"
    },
    "metadata": {
      "target": "(6,-7)",
      "domain_operation": "compute_centroid_coordinates",
      "textbook_example_id": 4443,
      "component_id": "src_4443",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_centroid_coordinates",
      "source_kind": "example",
      "line_type": "compute_centroid_coordinates"
    },
    "math_core": {
      "target": "(6,-7)",
      "domain_operation": "compute_centroid_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_centroid_coordinates",
      "task_type": "compute_centroid_coordinates",
      "line_type": "compute_centroid_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(6,-7)"
    },
    "generator_key": "src_4443",
    "explanation": "內分點公式：P=((3·A+1·B)/(1+3))，得 P=(6,-7)。",
    "seed": null,
    "line_type": "compute_centroid_coordinates",
    "display_order": 4443,
    "source_order": 4443,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(0,-8)、B(-12,12)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=3:1$，求 P 坐標。",
    "answer": "(-9,7)",
    "correct_answer": "(-9,7)",
    "display_answer": "(-9,7)",
    "choices": [],
    "options": [],
    "component_id": "src_4429",
    "textbook_example_id": 4429,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-9,7)"
    },
    "metadata": {
      "target": "(-9,7)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4429,
      "component_id": "src_4429",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(-9,7)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(-9,7)"
    },
    "generator_key": "src_4429",
    "explanation": "內分點公式：P=((1·A+3·B)/(3+1))，得 P=(-9,7)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4429,
    "source_order": 4429,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(1,7)、B(31,22)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=1:4$，求 P 坐標。",
    "answer": "(7,10)",
    "correct_answer": "(7,10)",
    "display_answer": "(7,10)",
    "choices": [],
    "options": [],
    "component_id": "src_4428",
    "textbook_example_id": 4428,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(7,10)"
    },
    "metadata": {
      "target": "(7,10)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4428,
      "component_id": "src_4428",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(7,10)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(7,10)"
    },
    "generator_key": "src_4428",
    "explanation": "內分點公式：P=((4·A+1·B)/(1+4))，得 P=(7,10)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4428,
    "source_order": 4428,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(-2,-5)、B(5,2)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=3:4$，求 P 坐標。",
    "answer": "(1,-2)",
    "correct_answer": "(1,-2)",
    "display_answer": "(1,-2)",
    "choices": [],
    "options": [],
    "component_id": "src_4443",
    "textbook_example_id": 4443,
    "problem_type_id": "compute_centroid_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(1,-2)"
    },
    "metadata": {
      "target": "(1,-2)",
      "domain_operation": "compute_centroid_coordinates",
      "textbook_example_id": 4443,
      "component_id": "src_4443",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_centroid_coordinates",
      "source_kind": "example",
      "line_type": "compute_centroid_coordinates"
    },
    "math_core": {
      "target": "(1,-2)",
      "domain_operation": "compute_centroid_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_centroid_coordinates",
      "task_type": "compute_centroid_coordinates",
      "line_type": "compute_centroid_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(1,-2)"
    },
    "generator_key": "src_4443",
    "explanation": "內分點公式：P=((4·A+3·B)/(3+4))，得 P=(1,-2)。",
    "seed": null,
    "line_type": "compute_centroid_coordinates",
    "display_order": 4443,
    "source_order": 4443,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(-10,-4)、B(17,11)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=2:1$，求 P 坐標。",
    "answer": "(8,6)",
    "correct_answer": "(8,6)",
    "display_answer": "(8,6)",
    "choices": [],
    "options": [],
    "component_id": "src_4447",
    "textbook_example_id": 4447,
    "problem_type_id": "compute_centroid_coordinates",
    "source_kind": "quiz",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(8,6)"
    },
    "metadata": {
      "target": "(8,6)",
      "domain_operation": "compute_centroid_coordinates",
      "textbook_example_id": 4447,
      "component_id": "src_4447",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_centroid_coordinates",
      "source_kind": "quiz",
      "line_type": "compute_centroid_coordinates"
    },
    "math_core": {
      "target": "(8,6)",
      "domain_operation": "compute_centroid_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_centroid_coordinates",
      "task_type": "compute_centroid_coordinates",
      "line_type": "compute_centroid_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(8,6)"
    },
    "generator_key": "src_4447",
    "explanation": "內分點公式：P=((1·A+2·B)/(2+1))，得 P=(8,6)。",
    "seed": null,
    "line_type": "compute_centroid_coordinates",
    "display_order": 4447,
    "source_order": 4447,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(0,-3)、B(-8,-3)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=5:3$，求 P 坐標。",
    "answer": "(-5,-3)",
    "correct_answer": "(-5,-3)",
    "display_answer": "(-5,-3)",
    "choices": [],
    "options": [],
    "component_id": "src_4514",
    "textbook_example_id": 4514,
    "problem_type_id": "compute_centroid_coordinates",
    "source_kind": "test",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-5,-3)"
    },
    "metadata": {
      "target": "(-5,-3)",
      "domain_operation": "compute_centroid_coordinates",
      "textbook_example_id": 4514,
      "component_id": "src_4514",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_centroid_coordinates",
      "source_kind": "test",
      "line_type": "compute_centroid_coordinates"
    },
    "math_core": {
      "target": "(-5,-3)",
      "domain_operation": "compute_centroid_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_centroid_coordinates",
      "task_type": "compute_centroid_coordinates",
      "line_type": "compute_centroid_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "hard",
      "canonical_answer": "(-5,-3)"
    },
    "generator_key": "src_4514",
    "explanation": "內分點公式：P=((3·A+5·B)/(5+3))，得 P=(-5,-3)。",
    "seed": null,
    "line_type": "compute_centroid_coordinates",
    "display_order": 4514,
    "source_order": 4514,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(-9,2)、B(16,-13)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=3:2$，求 P 坐標。",
    "answer": "(6,-7)",
    "correct_answer": "(6,-7)",
    "display_answer": "(6,-7)",
    "choices": [],
    "options": [],
    "component_id": "src_4429",
    "textbook_example_id": 4429,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(6,-7)"
    },
    "metadata": {
      "target": "(6,-7)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4429,
      "component_id": "src_4429",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(6,-7)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(6,-7)"
    },
    "generator_key": "src_4429",
    "explanation": "內分點公式：P=((2·A+3·B)/(3+2))，得 P=(6,-7)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4429,
    "source_order": 4429,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(-4,-3)、B(4,1)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=3:1$，求 P 坐標。",
    "answer": "(2,0)",
    "correct_answer": "(2,0)",
    "display_answer": "(2,0)",
    "choices": [],
    "options": [],
    "component_id": "src_4514",
    "textbook_example_id": 4514,
    "problem_type_id": "compute_centroid_coordinates",
    "source_kind": "test",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(2,0)"
    },
    "metadata": {
      "target": "(2,0)",
      "domain_operation": "compute_centroid_coordinates",
      "textbook_example_id": 4514,
      "component_id": "src_4514",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_centroid_coordinates",
      "source_kind": "test",
      "line_type": "compute_centroid_coordinates"
    },
    "math_core": {
      "target": "(2,0)",
      "domain_operation": "compute_centroid_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_centroid_coordinates",
      "task_type": "compute_centroid_coordinates",
      "line_type": "compute_centroid_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "hard",
      "canonical_answer": "(2,0)"
    },
    "generator_key": "src_4514",
    "explanation": "內分點公式：P=((1·A+3·B)/(3+1))，得 P=(2,0)。",
    "seed": null,
    "line_type": "compute_centroid_coordinates",
    "display_order": 4514,
    "source_order": 4514,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(6,0)、B(12,3)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=1:2$，求 P 坐標。",
    "answer": "(8,1)",
    "correct_answer": "(8,1)",
    "display_answer": "(8,1)",
    "choices": [],
    "options": [],
    "component_id": "src_4439",
    "textbook_example_id": 4439,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "quiz",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(8,1)"
    },
    "metadata": {
      "target": "(8,1)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4439,
      "component_id": "src_4439",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "quiz",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(8,1)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(8,1)"
    },
    "generator_key": "src_4439",
    "explanation": "內分點公式：P=((2·A+1·B)/(1+2))，得 P=(8,1)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4439,
    "source_order": 4439,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(5,-6)、B(-16,22)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=3:4$，求 P 坐標。",
    "answer": "(-4,6)",
    "correct_answer": "(-4,6)",
    "display_answer": "(-4,6)",
    "choices": [],
    "options": [],
    "component_id": "src_4429",
    "textbook_example_id": 4429,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-4,6)"
    },
    "metadata": {
      "target": "(-4,6)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4429,
      "component_id": "src_4429",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(-4,6)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(-4,6)"
    },
    "generator_key": "src_4429",
    "explanation": "內分點公式：P=((4·A+3·B)/(3+4))，得 P=(-4,6)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4429,
    "source_order": 4429,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(-5,-10)、B(22,-4)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=1:2$，求 P 坐標。",
    "answer": "B",
    "correct_answer": "B",
    "display_answer": "B",
    "choices": [
      {
        "label": "A",
        "text": "(5,-8)",
        "value": "(5,-8)"
      },
      {
        "label": "B",
        "text": "D",
        "value": "D"
      },
      {
        "label": "C",
        "text": "(4,-7)",
        "value": "(4,-7)"
      },
      {
        "label": "D",
        "text": "(-8,4)",
        "value": "(-8,4)"
      }
    ],
    "options": [
      "(5,-8)",
      "D",
      "(4,-7)",
      "(-8,4)"
    ],
    "component_id": "src_4511",
    "textbook_example_id": 4511,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "test",
    "presentation_mode": "single_choice",
    "answer_type": "choice",
    "checker": "choice_label_checker",
    "checker_key": "choice_label_checker",
    "equivalence": "choice_label",
    "equivalence_type": "choice_label",
    "interaction_type": "single_choice",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "single_choice",
      "answer_type": "single_choice",
      "checker": "choice_label_checker",
      "checker_key": "choice_label_checker",
      "answer_equivalence": "choice_label",
      "equivalence_type": "choice_label",
      "equivalence": "choice_label",
      "semantic_answer": "B"
    },
    "metadata": {
      "target": "D",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4511,
      "component_id": "src_4511",
      "presentation_mode": "single_choice",
      "answer_type": "choice",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "test",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "D",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "hard",
      "canonical_answer": "D"
    },
    "generator_key": "src_4511",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4511,
    "source_order": 4511,
    "sampling_weight": 10.0,
    "checker_type": "choice_label_checker"
  },
  {
    "question_text": "已知 A(-6,-10)、B(1,4)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=4:3$，求 P 坐標。",
    "answer": "(-2,-2)",
    "correct_answer": "(-2,-2)",
    "display_answer": "(-2,-2)",
    "choices": [],
    "options": [],
    "component_id": "src_4443",
    "textbook_example_id": 4443,
    "problem_type_id": "compute_centroid_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-2,-2)"
    },
    "metadata": {
      "target": "(-2,-2)",
      "domain_operation": "compute_centroid_coordinates",
      "textbook_example_id": 4443,
      "component_id": "src_4443",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_centroid_coordinates",
      "source_kind": "example",
      "line_type": "compute_centroid_coordinates"
    },
    "math_core": {
      "target": "(-2,-2)",
      "domain_operation": "compute_centroid_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_centroid_coordinates",
      "task_type": "compute_centroid_coordinates",
      "line_type": "compute_centroid_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(-2,-2)"
    },
    "generator_key": "src_4443",
    "explanation": "內分點公式：P=((3·A+4·B)/(4+3))，得 P=(-2,-2)。",
    "seed": null,
    "line_type": "compute_centroid_coordinates",
    "display_order": 4443,
    "source_order": 4443,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(2,-5)、B(-33,23)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=2:5$，求 P 坐標。",
    "answer": "(-8,3)",
    "correct_answer": "(-8,3)",
    "display_answer": "(-8,3)",
    "choices": [],
    "options": [],
    "component_id": "src_4418",
    "textbook_example_id": 4418,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-8,3)"
    },
    "metadata": {
      "target": "(-8,3)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4418,
      "component_id": "src_4418",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(-8,3)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(-8,3)"
    },
    "generator_key": "src_4418",
    "explanation": "內分點公式：P=((5·A+2·B)/(2+5))，得 P=(-8,3)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4418,
    "source_order": 4418,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(9,9)、B(-36,-39)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=1:2$，求 P 坐標。",
    "answer": "(-6,-7)",
    "correct_answer": "(-6,-7)",
    "display_answer": "(-6,-7)",
    "choices": [],
    "options": [],
    "component_id": "src_4429",
    "textbook_example_id": 4429,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-6,-7)"
    },
    "metadata": {
      "target": "(-6,-7)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4429,
      "component_id": "src_4429",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(-6,-7)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(-6,-7)"
    },
    "generator_key": "src_4429",
    "explanation": "內分點公式：P=((2·A+1·B)/(1+2))，得 P=(-6,-7)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4429,
    "source_order": 4429,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(7,-10)、B(-14,4)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=2:5$，求 P 坐標。",
    "answer": "(1,-6)",
    "correct_answer": "(1,-6)",
    "display_answer": "(1,-6)",
    "choices": [],
    "options": [],
    "component_id": "src_4440",
    "textbook_example_id": 4440,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "quiz",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(1,-6)"
    },
    "metadata": {
      "target": "(1,-6)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4440,
      "component_id": "src_4440",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "quiz",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(1,-6)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(1,-6)"
    },
    "generator_key": "src_4440",
    "explanation": "內分點公式：P=((5·A+2·B)/(2+5))，得 P=(1,-6)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4440,
    "source_order": 4440,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(5,6)、B(-30,1)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=2:3$，求 P 坐標。",
    "answer": "(-9,4)",
    "correct_answer": "(-9,4)",
    "display_answer": "(-9,4)",
    "choices": [],
    "options": [],
    "component_id": "src_4429",
    "textbook_example_id": 4429,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-9,4)"
    },
    "metadata": {
      "target": "(-9,4)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4429,
      "component_id": "src_4429",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(-9,4)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(-9,4)"
    },
    "generator_key": "src_4429",
    "explanation": "內分點公式：P=((3·A+2·B)/(2+3))，得 P=(-9,4)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4429,
    "source_order": 4429,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(-6,-3)、B(30,-15)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=1:3$，求 P 坐標。",
    "answer": "(3,-6)",
    "correct_answer": "(3,-6)",
    "display_answer": "(3,-6)",
    "choices": [],
    "options": [],
    "component_id": "src_4429",
    "textbook_example_id": 4429,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(3,-6)"
    },
    "metadata": {
      "target": "(3,-6)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4429,
      "component_id": "src_4429",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(3,-6)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(3,-6)"
    },
    "generator_key": "src_4429",
    "explanation": "內分點公式：P=((3·A+1·B)/(1+3))，得 P=(3,-6)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4429,
    "source_order": 4429,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(-8,10)、B(6,3)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=3:4$，求 P 坐標。",
    "answer": "(-2,7)",
    "correct_answer": "(-2,7)",
    "display_answer": "(-2,7)",
    "choices": [],
    "options": [],
    "component_id": "src_4439",
    "textbook_example_id": 4439,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "quiz",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-2,7)"
    },
    "metadata": {
      "target": "(-2,7)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4439,
      "component_id": "src_4439",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "quiz",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(-2,7)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(-2,7)"
    },
    "generator_key": "src_4439",
    "explanation": "內分點公式：P=((4·A+3·B)/(3+4))，得 P=(-2,7)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4439,
    "source_order": 4439,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(9,5)、B(-71,-40)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=1:4$，求 P 坐標。",
    "answer": "(-7,-4)",
    "correct_answer": "(-7,-4)",
    "display_answer": "(-7,-4)",
    "choices": [],
    "options": [],
    "component_id": "src_4422",
    "textbook_example_id": 4422,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-7,-4)"
    },
    "metadata": {
      "target": "(-7,-4)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4422,
      "component_id": "src_4422",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(-7,-4)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(-7,-4)"
    },
    "generator_key": "src_4422",
    "explanation": "內分點公式：P=((4·A+1·B)/(1+4))，得 P=(-7,-4)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4422,
    "source_order": 4422,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(-2,3)、B(-9,-4)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=5:2$，求 P 坐標。",
    "answer": "(-7,-2)",
    "correct_answer": "(-7,-2)",
    "display_answer": "(-7,-2)",
    "choices": [],
    "options": [],
    "component_id": "src_4447",
    "textbook_example_id": 4447,
    "problem_type_id": "compute_centroid_coordinates",
    "source_kind": "quiz",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-7,-2)"
    },
    "metadata": {
      "target": "(-7,-2)",
      "domain_operation": "compute_centroid_coordinates",
      "textbook_example_id": 4447,
      "component_id": "src_4447",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_centroid_coordinates",
      "source_kind": "quiz",
      "line_type": "compute_centroid_coordinates"
    },
    "math_core": {
      "target": "(-7,-2)",
      "domain_operation": "compute_centroid_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_centroid_coordinates",
      "task_type": "compute_centroid_coordinates",
      "line_type": "compute_centroid_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(-7,-2)"
    },
    "generator_key": "src_4447",
    "explanation": "內分點公式：P=((2·A+5·B)/(5+2))，得 P=(-7,-2)。",
    "seed": null,
    "line_type": "compute_centroid_coordinates",
    "display_order": 4447,
    "source_order": 4447,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(-3,-1)、B(9,5)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=5:1$，求 P 坐標。",
    "answer": "(7,4)",
    "correct_answer": "(7,4)",
    "display_answer": "(7,4)",
    "choices": [],
    "options": [],
    "component_id": "src_4439",
    "textbook_example_id": 4439,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "quiz",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(7,4)"
    },
    "metadata": {
      "target": "(7,4)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4439,
      "component_id": "src_4439",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "quiz",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(7,4)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(7,4)"
    },
    "generator_key": "src_4439",
    "explanation": "內分點公式：P=((1·A+5·B)/(5+1))，得 P=(7,4)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4439,
    "source_order": 4439,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(5,0)、B(0,10)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=4:1$，求 P 坐標。",
    "answer": "(1,8)",
    "correct_answer": "(1,8)",
    "display_answer": "(1,8)",
    "choices": [],
    "options": [],
    "component_id": "src_4418",
    "textbook_example_id": 4418,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(1,8)"
    },
    "metadata": {
      "target": "(1,8)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4418,
      "component_id": "src_4418",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(1,8)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(1,8)"
    },
    "generator_key": "src_4418",
    "explanation": "內分點公式：P=((1·A+4·B)/(4+1))，得 P=(1,8)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4418,
    "source_order": 4418,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(7,-9)、B(-29,59)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=1:3$，求 P 坐標。",
    "answer": "(-2,8)",
    "correct_answer": "(-2,8)",
    "display_answer": "(-2,8)",
    "choices": [],
    "options": [],
    "component_id": "src_4422",
    "textbook_example_id": 4422,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(-2,8)"
    },
    "metadata": {
      "target": "(-2,8)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4422,
      "component_id": "src_4422",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(-2,8)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(-2,8)"
    },
    "generator_key": "src_4422",
    "explanation": "內分點公式：P=((3·A+1·B)/(1+3))，得 P=(-2,8)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4422,
    "source_order": 4422,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(-5,-4)、B(15,-14)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=3:2$，求 P 坐標。",
    "answer": "(7,-10)",
    "correct_answer": "(7,-10)",
    "display_answer": "(7,-10)",
    "choices": [],
    "options": [],
    "component_id": "src_4514",
    "textbook_example_id": 4514,
    "problem_type_id": "compute_centroid_coordinates",
    "source_kind": "test",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(7,-10)"
    },
    "metadata": {
      "target": "(7,-10)",
      "domain_operation": "compute_centroid_coordinates",
      "textbook_example_id": 4514,
      "component_id": "src_4514",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_centroid_coordinates",
      "source_kind": "test",
      "line_type": "compute_centroid_coordinates"
    },
    "math_core": {
      "target": "(7,-10)",
      "domain_operation": "compute_centroid_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_centroid_coordinates",
      "task_type": "compute_centroid_coordinates",
      "line_type": "compute_centroid_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "hard",
      "canonical_answer": "(7,-10)"
    },
    "generator_key": "src_4514",
    "explanation": "內分點公式：P=((2·A+3·B)/(3+2))，得 P=(7,-10)。",
    "seed": null,
    "line_type": "compute_centroid_coordinates",
    "display_order": 4514,
    "source_order": 4514,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  },
  {
    "question_text": "已知 A(10,-5)、B(-8,25)，P 在線段 $\\overline{AB}$ 上，且 $\\overline{AP}:\\overline{PB}=1:2$，求 P 坐標。",
    "answer": "(4,5)",
    "correct_answer": "(4,5)",
    "display_answer": "(4,5)",
    "choices": [],
    "options": [],
    "component_id": "src_4422",
    "textbook_example_id": 4422,
    "problem_type_id": "compute_midpoint_coordinates",
    "source_kind": "example",
    "presentation_mode": "short_answer",
    "answer_type": "coordinate_pair",
    "checker": "coordinate_pair_checker",
    "checker_key": "coordinate_pair_checker",
    "equivalence": "coordinate_pair_equivalence",
    "equivalence_type": "coordinate_pair_equivalence",
    "interaction_type": "short_answer",
    "auto_checkable": true,
    "grading_mode": "auto",
    "answer_contract": {
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "checker": "coordinate_pair_checker",
      "checker_key": "coordinate_pair_checker",
      "answer_equivalence": "coordinate_pair_equivalence",
      "equivalence_type": "coordinate_pair_equivalence",
      "equivalence": "coordinate_pair_equivalence",
      "semantic_answer": "(4,5)"
    },
    "metadata": {
      "target": "(4,5)",
      "domain_operation": "compute_midpoint_coordinates",
      "textbook_example_id": 4422,
      "component_id": "src_4422",
      "presentation_mode": "short_answer",
      "answer_type": "coordinate_pair",
      "problem_type_id": "compute_midpoint_coordinates",
      "source_kind": "example",
      "line_type": "compute_midpoint_coordinates"
    },
    "math_core": {
      "target": "(4,5)",
      "domain_operation": "compute_midpoint_coordinates"
    },
    "visual_spec": {
      "kind": "coordinate_plane_spec",
      "points": [],
      "lines": [],
      "x_range": [
        -10,
        10
      ],
      "y_range": [
        -10,
        10
      ]
    },
    "visual_aids": [],
    "image_base64": null,
    "validation_facts": {
      "domain_operation": "compute_midpoint_coordinates",
      "task_type": "compute_midpoint_coordinates",
      "line_type": "compute_midpoint_coordinates",
      "curriculum_profile": "vocational_high_b",
      "difficulty_profile": "easy",
      "canonical_answer": "(4,5)"
    },
    "generator_key": "src_4422",
    "explanation": "內分點公式：P=((2·A+1·B)/(1+2))，得 P=(4,5)。",
    "seed": null,
    "line_type": "compute_midpoint_coordinates",
    "display_order": 4422,
    "source_order": 4422,
    "sampling_weight": 10.0,
    "checker_type": "coordinate_pair_checker"
  }
]
```
