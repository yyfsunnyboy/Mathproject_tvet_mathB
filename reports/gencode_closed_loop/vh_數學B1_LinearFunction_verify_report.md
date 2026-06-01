# Verify Report: vh_數學B1_LinearFunction

- python: C:\Users\Owner\anaconda3\python.exe
- registry: D:\Python\Mathproject_tvet_mathB\configs\generated_registry\b1_section_1_1_verified_registry.v0.1.yaml
- registry_verified_count: 1
- pytest_exit_code: 0
- unique_problem_type_count: 0
- PASS: False
- first_blocking_error: wrapper generate failed: generator_semantically_unsafe:invalid_answer_type: problem_type_id=numeric_numeric_evaluate_function_notation_short_answer answer_type=numeric answer_shape=scalar answer='\\sqrt{128}' answer_type=str checker=numeric_checker equivalence=numeric_equivalence expected=numeric allows int/float/numeric string; answer_shape=scalar,numeric_equivalence_invalid

## Runtime ProblemType Coverage
```json
{
  "expected_problem_types": [
    "integer_numeric_evaluate_function_notation"
  ],
  "observed_problem_types": [],
  "missing_problem_types": [
    "integer_numeric_evaluate_function_notation"
  ],
  "sample_count": 30,
  "status": "fail"
}
```

## Verified Entries
```json
[
  {
    "problem_type_id": "integer_numeric_evaluate_function_notation",
    "skill_id": "vh_數學B1_LinearFunction",
    "subskill_id": "integer_numeric_evaluate_function_notation",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_2/integer_numeric_evaluate_function_notation/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "wrapper_path": "skills/vh_數學B1_LinearFunction.py",
    "manual_review_exclusions": [
      "unknown"
    ],
    "source": "gencode_runtime_binding",
    "phase2_report_path": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_phase2_build.json"
  }
]
```

## Pytest Output
```text
.....                                                                    [100%]
5 passed in 0.04s
```

## Samples
```json
[]
```
