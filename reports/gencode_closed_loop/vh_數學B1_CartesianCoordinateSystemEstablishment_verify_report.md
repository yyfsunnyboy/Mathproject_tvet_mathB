# Verify Report: vh_數學B1_CartesianCoordinateSystemEstablishment

- python: C:\Python314\python.exe
- registry: E:\Python\Mathproject_tvet_mathB\configs\generated_registry\b1_section_1_1_verified_registry.v0.1.yaml
- registry_verified_count: 1
- pytest_exit_code: 0
- unique_problem_type_count: 1
- PASS: True

## Runtime ProblemType Coverage
```json
{
  "expected_problem_types": [
    "cartesian_coordinate_quadrant_symbol_reasoning"
  ],
  "observed_problem_types": [
    "cartesian_coordinate_quadrant_symbol_reasoning"
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
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_2/cartesian_coordinate_quadrant_symbol_reasoning/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "choice",
    "checker_type": "choice_label_checker"
  }
]
```

## Pytest Output
```text
.                                                                        [100%]
1 passed in 0.05s
```

## Samples
```json
[
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $m$ 為實數，且滿足條件：m < 0。則平面上的點 $Q(m^2, -m)$ 在第幾象限？",
    "question": "設 $m$ 為實數，且滿足條件：m < 0。則平面上的點 $Q(m^2, -m)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: m < 0.\nDeduce sign of x coordinate: m**2 -> +.\nDeduce sign of y coordinate: -m -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: m < 0.",
      "Deduce sign of x coordinate: m**2 -> +.",
      "Deduce sign of y coordinate: -m -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s38",
      "parameter_signature": "quadrant_reasoning:cond=m < 0:x=m**2:y=-m",
      "question_pattern_id": "p14",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $p$、$q$ 為實數，且滿足條件：p > 0, q < 0。則平面上的點 $Q(-p, q)$ 在第幾象限？",
    "question": "設 $p$、$q$ 為實數，且滿足條件：p > 0, q < 0。則平面上的點 $Q(-p, q)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: p > 0, q < 0.\nDeduce sign of x coordinate: -p -> -.\nDeduce sign of y coordinate: q -> -.\nDetermine the quadrant: 第三象限.",
    "solution_steps": [
      "Analyze variable conditions: p > 0, q < 0.",
      "Deduce sign of x coordinate: -p -> -.",
      "Deduce sign of y coordinate: q -> -.",
      "Determine the quadrant: 第三象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s11",
      "parameter_signature": "quadrant_reasoning:cond=p > 0, q < 0:x=-p:y=q",
      "question_pattern_id": "p98",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $c$、$d$ 為實數，且滿足條件：c > 0, d < 0。則平面上的點 $Q(-c, d)$ 在第幾象限？",
    "question": "設 $c$、$d$ 為實數，且滿足條件：c > 0, d < 0。則平面上的點 $Q(-c, d)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: c > 0, d < 0.\nDeduce sign of x coordinate: -c -> -.\nDeduce sign of y coordinate: d -> -.\nDetermine the quadrant: 第三象限.",
    "solution_steps": [
      "Analyze variable conditions: c > 0, d < 0.",
      "Deduce sign of x coordinate: -c -> -.",
      "Deduce sign of y coordinate: d -> -.",
      "Determine the quadrant: 第三象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s21",
      "parameter_signature": "quadrant_reasoning:cond=c > 0, d < 0:x=-c:y=d",
      "question_pattern_id": "p27",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $a$、$b$ 為實數，且滿足條件：a > 0, b < 0。則平面上的點 $Q(ab, a - b)$ 在第幾象限？",
    "question": "設 $a$、$b$ 為實數，且滿足條件：a > 0, b < 0。則平面上的點 $Q(ab, a - b)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: a > 0, b < 0.\nDeduce sign of x coordinate: a * b -> -.\nDeduce sign of y coordinate: a - b -> +.\nDetermine the quadrant: 第二象限.",
    "solution_steps": [
      "Analyze variable conditions: a > 0, b < 0.",
      "Deduce sign of x coordinate: a * b -> -.",
      "Deduce sign of y coordinate: a - b -> +.",
      "Determine the quadrant: 第二象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s4",
      "parameter_signature": "quadrant_reasoning:cond=a > 0, b < 0:x=a * b:y=a - b",
      "question_pattern_id": "p88",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $u$、$v$ 為實數，且滿足條件：u < 0, v < 0。則平面上的點 $Q(-u, -v)$ 在第幾象限？",
    "question": "設 $u$、$v$ 為實數，且滿足條件：u < 0, v < 0。則平面上的點 $Q(-u, -v)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: u < 0, v < 0.\nDeduce sign of x coordinate: -u -> +.\nDeduce sign of y coordinate: -v -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: u < 0, v < 0.",
      "Deduce sign of x coordinate: -u -> +.",
      "Deduce sign of y coordinate: -v -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s42",
      "parameter_signature": "quadrant_reasoning:cond=u < 0, v < 0:x=-u:y=-v",
      "question_pattern_id": "p51",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $a$、$b$ 為實數，且滿足條件：a > 0, b > 0, b < a。則平面上的點 $Q(b - a, ab)$ 在第幾象限？",
    "question": "設 $a$、$b$ 為實數，且滿足條件：a > 0, b > 0, b < a。則平面上的點 $Q(b - a, ab)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: a > 0, b > 0, b < a.\nDeduce sign of x coordinate: b - a -> -.\nDeduce sign of y coordinate: a * b -> +.\nDetermine the quadrant: 第二象限.",
    "solution_steps": [
      "Analyze variable conditions: a > 0, b > 0, b < a.",
      "Deduce sign of x coordinate: b - a -> -.",
      "Deduce sign of y coordinate: a * b -> +.",
      "Determine the quadrant: 第二象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s1",
      "parameter_signature": "quadrant_reasoning:cond=a > 0, b > 0, b < a:x=b - a:y=a * b",
      "question_pattern_id": "p32",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $c$、$d$ 為實數，且滿足條件：c > 0, d > 0, d < c。則平面上的點 $Q(d - c, cd)$ 在第幾象限？",
    "question": "設 $c$、$d$ 為實數，且滿足條件：c > 0, d > 0, d < c。則平面上的點 $Q(d - c, cd)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: c > 0, d > 0, d < c.\nDeduce sign of x coordinate: d - c -> -.\nDeduce sign of y coordinate: c * d -> +.\nDetermine the quadrant: 第二象限.",
    "solution_steps": [
      "Analyze variable conditions: c > 0, d > 0, d < c.",
      "Deduce sign of x coordinate: d - c -> -.",
      "Deduce sign of y coordinate: c * d -> +.",
      "Determine the quadrant: 第二象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s73",
      "parameter_signature": "quadrant_reasoning:cond=c > 0, d > 0, d < c:x=d - c:y=c * d",
      "question_pattern_id": "p46",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $m$、$n$ 為實數，且滿足條件：m < 0, n < 0。則平面上的點 $Q(-m, -n)$ 在第幾象限？",
    "question": "設 $m$、$n$ 為實數，且滿足條件：m < 0, n < 0。則平面上的點 $Q(-m, -n)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: m < 0, n < 0.\nDeduce sign of x coordinate: -m -> +.\nDeduce sign of y coordinate: -n -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: m < 0, n < 0.",
      "Deduce sign of x coordinate: -m -> +.",
      "Deduce sign of y coordinate: -n -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s29",
      "parameter_signature": "quadrant_reasoning:cond=m < 0, n < 0:x=-m:y=-n",
      "question_pattern_id": "p93",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $m$、$n$ 為實數，且滿足條件：m > 0, n < 0。則平面上的點 $Q(m - n, n^2)$ 在第幾象限？",
    "question": "設 $m$、$n$ 為實數，且滿足條件：m > 0, n < 0。則平面上的點 $Q(m - n, n^2)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: m > 0, n < 0.\nDeduce sign of x coordinate: m - n -> +.\nDeduce sign of y coordinate: n**2 -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: m > 0, n < 0.",
      "Deduce sign of x coordinate: m - n -> +.",
      "Deduce sign of y coordinate: n**2 -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s11",
      "parameter_signature": "quadrant_reasoning:cond=m > 0, n < 0:x=m - n:y=n**2",
      "question_pattern_id": "p3",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $u$、$v$ 為實數，且滿足條件：u < v < 0。則平面上的點 $Q(v - u, uv)$ 在第幾象限？",
    "question": "設 $u$、$v$ 為實數，且滿足條件：u < v < 0。則平面上的點 $Q(v - u, uv)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: u < v < 0.\nDeduce sign of x coordinate: v - u -> +.\nDeduce sign of y coordinate: u * v -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: u < v < 0.",
      "Deduce sign of x coordinate: v - u -> +.",
      "Deduce sign of y coordinate: u * v -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s47",
      "parameter_signature": "quadrant_reasoning:cond=u < v < 0:x=v - u:y=u * v",
      "question_pattern_id": "p76",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $m$、$n$ 為實數，且滿足條件：m < 0, n < 0。則平面上的點 $Q(-m, -n)$ 在第幾象限？",
    "question": "設 $m$、$n$ 為實數，且滿足條件：m < 0, n < 0。則平面上的點 $Q(-m, -n)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: m < 0, n < 0.\nDeduce sign of x coordinate: -m -> +.\nDeduce sign of y coordinate: -n -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: m < 0, n < 0.",
      "Deduce sign of x coordinate: -m -> +.",
      "Deduce sign of y coordinate: -n -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s77",
      "parameter_signature": "quadrant_reasoning:cond=m < 0, n < 0:x=-m:y=-n",
      "question_pattern_id": "p64",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $c$、$d$ 為實數，且滿足條件：c < 0, d < 0。則平面上的點 $Q(-c, -d)$ 在第幾象限？",
    "question": "設 $c$、$d$ 為實數，且滿足條件：c < 0, d < 0。則平面上的點 $Q(-c, -d)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: c < 0, d < 0.\nDeduce sign of x coordinate: -c -> +.\nDeduce sign of y coordinate: -d -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: c < 0, d < 0.",
      "Deduce sign of x coordinate: -c -> +.",
      "Deduce sign of y coordinate: -d -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s97",
      "parameter_signature": "quadrant_reasoning:cond=c < 0, d < 0:x=-c:y=-d",
      "question_pattern_id": "p79",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $a$、$b$ 為實數，且滿足條件：a > 0, b < 0。則平面上的點 $Q(a - b, b^2)$ 在第幾象限？",
    "question": "設 $a$、$b$ 為實數，且滿足條件：a > 0, b < 0。則平面上的點 $Q(a - b, b^2)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: a > 0, b < 0.\nDeduce sign of x coordinate: a - b -> +.\nDeduce sign of y coordinate: b**2 -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: a > 0, b < 0.",
      "Deduce sign of x coordinate: a - b -> +.",
      "Deduce sign of y coordinate: b**2 -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s55",
      "parameter_signature": "quadrant_reasoning:cond=a > 0, b < 0:x=a - b:y=b**2",
      "question_pattern_id": "p71",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $u$ 為實數，且滿足條件：u < 0。則平面上的點 $Q(u^2, -u)$ 在第幾象限？",
    "question": "設 $u$ 為實數，且滿足條件：u < 0。則平面上的點 $Q(u^2, -u)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: u < 0.\nDeduce sign of x coordinate: u**2 -> +.\nDeduce sign of y coordinate: -u -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: u < 0.",
      "Deduce sign of x coordinate: u**2 -> +.",
      "Deduce sign of y coordinate: -u -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s81",
      "parameter_signature": "quadrant_reasoning:cond=u < 0:x=u**2:y=-u",
      "question_pattern_id": "p13",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $p$、$q$ 為實數，且滿足條件：p > 0, q > 0, p < q。則平面上的點 $Q(pq, q - p)$ 在第幾象限？",
    "question": "設 $p$、$q$ 為實數，且滿足條件：p > 0, q > 0, p < q。則平面上的點 $Q(pq, q - p)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: p > 0, q > 0, p < q.\nDeduce sign of x coordinate: p * q -> +.\nDeduce sign of y coordinate: q - p -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: p > 0, q > 0, p < q.",
      "Deduce sign of x coordinate: p * q -> +.",
      "Deduce sign of y coordinate: q - p -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s31",
      "parameter_signature": "quadrant_reasoning:cond=p > 0, q > 0, p < q:x=p * q:y=q - p",
      "question_pattern_id": "p25",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $c$、$d$ 為實數，且滿足條件：c < d < 0。則平面上的點 $Q(cd, c + d)$ 在第幾象限？",
    "question": "設 $c$、$d$ 為實數，且滿足條件：c < d < 0。則平面上的點 $Q(cd, c + d)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: c < d < 0.\nDeduce sign of x coordinate: c * d -> +.\nDeduce sign of y coordinate: c + d -> -.\nDetermine the quadrant: 第四象限.",
    "solution_steps": [
      "Analyze variable conditions: c < d < 0.",
      "Deduce sign of x coordinate: c * d -> +.",
      "Deduce sign of y coordinate: c + d -> -.",
      "Determine the quadrant: 第四象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s98",
      "parameter_signature": "quadrant_reasoning:cond=c < d < 0:x=c * d:y=c + d",
      "question_pattern_id": "p89",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $s$、$t$ 為實數，且滿足條件：s > 0, t > 0, s < t。則平面上的點 $Q(s - t, s^2t)$ 在第幾象限？",
    "question": "設 $s$、$t$ 為實數，且滿足條件：s > 0, t > 0, s < t。則平面上的點 $Q(s - t, s^2t)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: s > 0, t > 0, s < t.\nDeduce sign of x coordinate: s - t -> -.\nDeduce sign of y coordinate: s**2 * t -> +.\nDetermine the quadrant: 第二象限.",
    "solution_steps": [
      "Analyze variable conditions: s > 0, t > 0, s < t.",
      "Deduce sign of x coordinate: s - t -> -.",
      "Deduce sign of y coordinate: s**2 * t -> +.",
      "Determine the quadrant: 第二象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s51",
      "parameter_signature": "quadrant_reasoning:cond=s > 0, t > 0, s < t:x=s - t:y=s**2 * t",
      "question_pattern_id": "p27",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $s$、$t$ 為實數，且滿足條件：s < t < 0。則平面上的點 $Q(st, s + t)$ 在第幾象限？",
    "question": "設 $s$、$t$ 為實數，且滿足條件：s < t < 0。則平面上的點 $Q(st, s + t)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: s < t < 0.\nDeduce sign of x coordinate: s * t -> +.\nDeduce sign of y coordinate: s + t -> -.\nDetermine the quadrant: 第四象限.",
    "solution_steps": [
      "Analyze variable conditions: s < t < 0.",
      "Deduce sign of x coordinate: s * t -> +.",
      "Deduce sign of y coordinate: s + t -> -.",
      "Determine the quadrant: 第四象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s9",
      "parameter_signature": "quadrant_reasoning:cond=s < t < 0:x=s * t:y=s + t",
      "question_pattern_id": "p34",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $a$、$b$ 為實數，且滿足條件：a > 0, b < 0。則平面上的點 $Q(a - b, b^2)$ 在第幾象限？",
    "question": "設 $a$、$b$ 為實數，且滿足條件：a > 0, b < 0。則平面上的點 $Q(a - b, b^2)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: a > 0, b < 0.\nDeduce sign of x coordinate: a - b -> +.\nDeduce sign of y coordinate: b**2 -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: a > 0, b < 0.",
      "Deduce sign of x coordinate: a - b -> +.",
      "Deduce sign of y coordinate: b**2 -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s77",
      "parameter_signature": "quadrant_reasoning:cond=a > 0, b < 0:x=a - b:y=b**2",
      "question_pattern_id": "p9",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $a$ 為實數，且滿足條件：a < 0。則平面上的點 $Q(a^2, -a)$ 在第幾象限？",
    "question": "設 $a$ 為實數，且滿足條件：a < 0。則平面上的點 $Q(a^2, -a)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: a < 0.\nDeduce sign of x coordinate: a**2 -> +.\nDeduce sign of y coordinate: -a -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: a < 0.",
      "Deduce sign of x coordinate: a**2 -> +.",
      "Deduce sign of y coordinate: -a -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s96",
      "parameter_signature": "quadrant_reasoning:cond=a < 0:x=a**2:y=-a",
      "question_pattern_id": "p57",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $c$、$d$ 為實數，且滿足條件：c > 0, d < 0。則平面上的點 $Q(c - d, d^2)$ 在第幾象限？",
    "question": "設 $c$、$d$ 為實數，且滿足條件：c > 0, d < 0。則平面上的點 $Q(c - d, d^2)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: c > 0, d < 0.\nDeduce sign of x coordinate: c - d -> +.\nDeduce sign of y coordinate: d**2 -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: c > 0, d < 0.",
      "Deduce sign of x coordinate: c - d -> +.",
      "Deduce sign of y coordinate: d**2 -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s52",
      "parameter_signature": "quadrant_reasoning:cond=c > 0, d < 0:x=c - d:y=d**2",
      "question_pattern_id": "p92",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $m$、$n$ 為實數，且滿足條件：m > 0, n < 0。則平面上的點 $Q(mn, m - n)$ 在第幾象限？",
    "question": "設 $m$、$n$ 為實數，且滿足條件：m > 0, n < 0。則平面上的點 $Q(mn, m - n)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: m > 0, n < 0.\nDeduce sign of x coordinate: m * n -> -.\nDeduce sign of y coordinate: m - n -> +.\nDetermine the quadrant: 第二象限.",
    "solution_steps": [
      "Analyze variable conditions: m > 0, n < 0.",
      "Deduce sign of x coordinate: m * n -> -.",
      "Deduce sign of y coordinate: m - n -> +.",
      "Determine the quadrant: 第二象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s88",
      "parameter_signature": "quadrant_reasoning:cond=m > 0, n < 0:x=m * n:y=m - n",
      "question_pattern_id": "p41",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $s$、$t$ 為實數，且滿足條件：s > 0, t < 0。則平面上的點 $Q(s - t, t^2)$ 在第幾象限？",
    "question": "設 $s$、$t$ 為實數，且滿足條件：s > 0, t < 0。則平面上的點 $Q(s - t, t^2)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: s > 0, t < 0.\nDeduce sign of x coordinate: s - t -> +.\nDeduce sign of y coordinate: t**2 -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: s > 0, t < 0.",
      "Deduce sign of x coordinate: s - t -> +.",
      "Deduce sign of y coordinate: t**2 -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s98",
      "parameter_signature": "quadrant_reasoning:cond=s > 0, t < 0:x=s - t:y=t**2",
      "question_pattern_id": "p68",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $u$、$v$ 為實數，且滿足條件：u > 0, v > 0, v < u。則平面上的點 $Q(v - u, uv)$ 在第幾象限？",
    "question": "設 $u$、$v$ 為實數，且滿足條件：u > 0, v > 0, v < u。則平面上的點 $Q(v - u, uv)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: u > 0, v > 0, v < u.\nDeduce sign of x coordinate: v - u -> -.\nDeduce sign of y coordinate: u * v -> +.\nDetermine the quadrant: 第二象限.",
    "solution_steps": [
      "Analyze variable conditions: u > 0, v > 0, v < u.",
      "Deduce sign of x coordinate: v - u -> -.",
      "Deduce sign of y coordinate: u * v -> +.",
      "Determine the quadrant: 第二象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s68",
      "parameter_signature": "quadrant_reasoning:cond=u > 0, v > 0, v < u:x=v - u:y=u * v",
      "question_pattern_id": "p37",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $p$、$q$ 為實數，且滿足條件：p < q < 0。則平面上的點 $Q(q - p, pq)$ 在第幾象限？",
    "question": "設 $p$、$q$ 為實數，且滿足條件：p < q < 0。則平面上的點 $Q(q - p, pq)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: p < q < 0.\nDeduce sign of x coordinate: q - p -> +.\nDeduce sign of y coordinate: p * q -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: p < q < 0.",
      "Deduce sign of x coordinate: q - p -> +.",
      "Deduce sign of y coordinate: p * q -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s36",
      "parameter_signature": "quadrant_reasoning:cond=p < q < 0:x=q - p:y=p * q",
      "question_pattern_id": "p18",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $s$、$t$ 為實數，且滿足條件：s < t < 0。則平面上的點 $Q(t - s, st)$ 在第幾象限？",
    "question": "設 $s$、$t$ 為實數，且滿足條件：s < t < 0。則平面上的點 $Q(t - s, st)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: s < t < 0.\nDeduce sign of x coordinate: t - s -> +.\nDeduce sign of y coordinate: s * t -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: s < t < 0.",
      "Deduce sign of x coordinate: t - s -> +.",
      "Deduce sign of y coordinate: s * t -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s10",
      "parameter_signature": "quadrant_reasoning:cond=s < t < 0:x=t - s:y=s * t",
      "question_pattern_id": "p20",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $c$、$d$ 為實數，且滿足條件：c < d < 0。則平面上的點 $Q(d - c, cd)$ 在第幾象限？",
    "question": "設 $c$、$d$ 為實數，且滿足條件：c < d < 0。則平面上的點 $Q(d - c, cd)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: c < d < 0.\nDeduce sign of x coordinate: d - c -> +.\nDeduce sign of y coordinate: c * d -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: c < d < 0.",
      "Deduce sign of x coordinate: d - c -> +.",
      "Deduce sign of y coordinate: c * d -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s8",
      "parameter_signature": "quadrant_reasoning:cond=c < d < 0:x=d - c:y=c * d",
      "question_pattern_id": "p71",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $p$、$q$ 為實數，且滿足條件：p > 0, q > 0, q < p。則平面上的點 $Q(q - p, pq)$ 在第幾象限？",
    "question": "設 $p$、$q$ 為實數，且滿足條件：p > 0, q > 0, q < p。則平面上的點 $Q(q - p, pq)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: p > 0, q > 0, q < p.\nDeduce sign of x coordinate: q - p -> -.\nDeduce sign of y coordinate: p * q -> +.\nDetermine the quadrant: 第二象限.",
    "solution_steps": [
      "Analyze variable conditions: p > 0, q > 0, q < p.",
      "Deduce sign of x coordinate: q - p -> -.",
      "Deduce sign of y coordinate: p * q -> +.",
      "Determine the quadrant: 第二象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s33",
      "parameter_signature": "quadrant_reasoning:cond=p > 0, q > 0, q < p:x=q - p:y=p * q",
      "question_pattern_id": "p42",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $c$、$d$ 為實數，且滿足條件：c > 0, d > 0, c < d。則平面上的點 $Q(cd, d - c)$ 在第幾象限？",
    "question": "設 $c$、$d$ 為實數，且滿足條件：c > 0, d > 0, c < d。則平面上的點 $Q(cd, d - c)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: c > 0, d > 0, c < d.\nDeduce sign of x coordinate: c * d -> +.\nDeduce sign of y coordinate: d - c -> +.\nDetermine the quadrant: 第一象限.",
    "solution_steps": [
      "Analyze variable conditions: c > 0, d > 0, c < d.",
      "Deduce sign of x coordinate: c * d -> +.",
      "Deduce sign of y coordinate: d - c -> +.",
      "Determine the quadrant: 第一象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s85",
      "parameter_signature": "quadrant_reasoning:cond=c > 0, d > 0, c < d:x=c * d:y=d - c",
      "question_pattern_id": "p76",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  },
  {
    "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
    "problem_type_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "subskill_id": "cartesian_coordinate_quadrant_symbol_reasoning",
    "question_text": "設 $p$、$q$ 為實數，且滿足條件：p > 0, q > 0, p < q。則平面上的點 $Q(p - q, p^2q)$ 在第幾象限？",
    "question": "設 $p$、$q$ 為實數，且滿足條件：p > 0, q > 0, p < q。則平面上的點 $Q(p - q, p^2q)$ 在第幾象限？",
    "choices": [
      "第一象限",
      "第三象限",
      "第二象限",
      "第四象限"
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
    "explanation": "Analyze variable conditions: p > 0, q > 0, p < q.\nDeduce sign of x coordinate: p - q -> -.\nDeduce sign of y coordinate: p**2 * q -> +.\nDetermine the quadrant: 第二象限.",
    "solution_steps": [
      "Analyze variable conditions: p > 0, q > 0, p < q.",
      "Deduce sign of x coordinate: p - q -> -.",
      "Deduce sign of y coordinate: p**2 * q -> +.",
      "Determine the quadrant: 第二象限."
    ],
    "difficulty": 1,
    "diagnosis_tags": [
      "coordinate_plane",
      "quadrant",
      "symbolic_reasoning"
    ],
    "source": "gencode_candidate_v1",
    "metadata": {
      "scenario_family": "cartesian_coordinate_quadrant_symbol_reasoning",
      "scenario_id": "s72",
      "parameter_signature": "quadrant_reasoning:cond=p > 0, q > 0, p < q:x=p - q:y=p**2 * q",
      "question_pattern_id": "p49",
      "diagnosis_tags": [
        "coordinate_plane",
        "quadrant",
        "symbolic_reasoning"
      ],
      "prerequisite_subskills": [],
      "verified_problem_types": [
        "cartesian_coordinate_quadrant_symbol_reasoning"
      ],
      "manual_review_exclusions": [],
      "source": "gencode_runtime_binding"
    }
  }
]
```
