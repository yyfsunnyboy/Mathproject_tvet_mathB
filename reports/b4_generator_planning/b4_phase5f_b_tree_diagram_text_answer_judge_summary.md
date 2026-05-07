# Phase 5F-B: Tree Diagram Text-Answer Judge Summary

## 1. Purpose

Phase 5F-B creates an isolated text-answer free-response prototype for `tree_diagram_listing`.

The goal is to judge complete text listings for tree diagram questions without connecting the problem type to deterministic int-answer runtime.

## 2. Scope

- Implemented text-listing payload helper, parser, and rule-based judge.
- Supported text answers only.
- Did not implement handwriting, image upload, canvas recognition, or frontend UI.
- Did not modify `/check_answer`, adaptive routing, B4 deterministic allowlist, question router, generators, or coverage matrix.

## 3. Supported Variants

- `fixed_stage_binary_tree`
  - Coin tossed 3 times.
  - Expected paths: 正正正、正正反、正反正、正反反、反正正、反正反、反反正、反反反.
- `early_stopping_game`
  - 甲、乙 teams play until one side wins two games.
  - Expected paths: 甲甲、甲乙甲、甲乙乙、乙甲甲、乙甲乙、乙乙.

## 4. Parser / Judge Rules

- Parser extracts path labels from text using the configured `path_labels`.
- Supports Chinese punctuation, commas, semicolons, whitespace, and newlines.
- Detects listed paths, duplicate paths, and count-only answers.
- Judge compares `detected_paths` with `expected_paths`.
- Count-only answers are `partial`, not `correct`.
- Missing expected paths are `partial` when the answer direction is otherwise valid.
- In `early_stopping_game`, fixed-three-round answers are not correct because they ignore the stop-after-two-wins rule.
- Empty or unparseable text returns `needs_review`.

## 5. Output Schema

The judge returns:

```json
{
  "status": "correct | partial | incorrect | needs_review",
  "score": 0.0,
  "expected_count": 6,
  "detected_count": 0,
  "expected_paths": [],
  "detected_paths": [],
  "missing_paths": [],
  "extra_paths": [],
  "duplicated_paths": [],
  "count_only_answer": false,
  "main_issue": "",
  "feedback": "",
  "teacher_review_needed": false,
  "confidence": 0.0
}
```

## 6. Test Cases / Result

Command:

```text
python -m pytest -q tests/test_phase5f_b_tree_diagram_text_answer_judge.py
```

Result:

```text
10 passed
```

Regression checks:

```text
python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py -> 8 passed
python -m pytest -q tests/test_vocational_math_b4_question_router_registry_canonical.py -> 24 passed
```

Covered cases:

- fixed-stage coin tree correct listing
- fixed-stage count-only partial
- fixed-stage missing one path
- early-stopping game correct listing
- early-stopping count-only partial
- early-stopping common four-path mistake
- fixed-three-round misconception in early-stopping game
- duplicated paths
- newline and punctuation parsing
- empty answer needs review

## 7. Runtime Boundary

- `tree_diagram_listing` still does not enter deterministic int-answer runtime.
- `tree_diagram_listing` was not added to `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`.
- No frontend UI is connected yet.
- No adaptive routing path is connected yet.
- No handwriting or image support is implemented.

## 8. Next Steps

- Phase 5F-C: AI judge prompt / hybrid judge.
- Phase 5F-D: free-response UI.
- Phase 5F-E: handwriting / image support.
- Phase 5F-F: teacher review / override / audit log.
