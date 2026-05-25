# Repair Prompt

```json
{
  "problem_type_spec": {
    "problem_type_id": "number_line_point_value_reading",
    "skill_id": "vh_數學B1_NumberLine",
    "display_name": "number line point value reading",
    "runtime_category": "deterministic",
    "answer_type": "numeric_or_expression",
    "checker_type": "deterministic_checker",
    "examples_refs": [
      4401
    ],
    "output_contract": {
      "required_keys": [
        "problem_type_id",
        "skill_id",
        "question_text",
        "answer",
        "answer_type",
        "checker_type",
        "solution_steps",
        "metadata"
      ]
    },
    "difficulty_policy": "easy_only_v1",
    "status": "draft"
  },
  "candidate_path": "C:\\Python\\Mathproject_tvet_mathB\\generated_candidates\\vocational_math_b1\\section_1_1\\number_line_point_value_reading\\candidate_v3.py",
  "verifier_errors": [
    "unique_parameter_signature_count_below_6"
  ],
  "failed_samples": [
    {
      "problem_type_id": "number_line_point_value_reading",
      "skill_id": "vh_數學B1_NumberLine",
      "question_text": "數線上點 $P$ 對應到整數 $9$，已知 $P$ 在 $9$，求其數值。",
      "answer": "9",
      "answer_type": "numeric_or_expression",
      "checker_type": "deterministic_checker",
      "solution_steps": [
        "直接讀取數線上點的對應整數。"
      ],
      "metadata": {
        "scenario_family": "number_line_point_value_reading",
        "scenario_id": 4,
        "parameter_signature": "number_line_point_value_reading:4:easy",
        "question_pattern_id": "p4"
      }
    },
    {
      "problem_type_id": "number_line_point_value_reading",
      "skill_id": "vh_數學B1_NumberLine",
      "question_text": "數線上點 $P$ 對應到整數 $3$，已知 $P$ 在 $3$，求其數值。",
      "answer": "3",
      "answer_type": "numeric_or_expression",
      "checker_type": "deterministic_checker",
      "solution_steps": [
        "直接讀取數線上點的對應整數。"
      ],
      "metadata": {
        "scenario_family": "number_line_point_value_reading",
        "scenario_id": 2,
        "parameter_signature": "number_line_point_value_reading:2:easy",
        "question_pattern_id": "p2"
      }
    },
    {
      "problem_type_id": "number_line_point_value_reading",
      "skill_id": "vh_數學B1_NumberLine",
      "question_text": "數線上點 $P$ 對應到整數 $-13$，已知 $P$ 在 $-13$，求其數值。",
      "answer": "-13",
      "answer_type": "numeric_or_expression",
      "checker_type": "deterministic_checker",
      "solution_steps": [
        "直接讀取數線上點的對應整數。"
      ],
      "metadata": {
        "scenario_family": "number_line_point_value_reading",
        "scenario_id": 1,
        "parameter_signature": "number_line_point_value_reading:1:easy",
        "question_pattern_id": "p1"
      }
    }
  ],
  "instruction": "Keep deterministic logic; fix verifier errors only."
}
```
