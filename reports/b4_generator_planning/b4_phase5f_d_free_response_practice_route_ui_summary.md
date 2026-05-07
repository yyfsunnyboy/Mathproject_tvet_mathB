# Phase 5F-D: Free Response Practice Route + Textarea UI Summary

## 1. Purpose

Phase 5F-D connects the Phase 5F-B text-answer judge to an isolated free-response practice route.

This phase does not connect `tree_diagram_listing` to adaptive scoring, `/check_answer`, deterministic int-answer runtime, or `adaptive_practice_v2`.

## 2. Added Route / API

- `GET /free_response_practice`
  - Renders an isolated tree diagram free-response practice page.
  - Supports `variant=early_stopping_game` and `variant=fixed_stage_binary_tree`.
- `GET /api/free_response/tree_diagram/question`
  - Returns public question metadata.
  - Does not expose `expected_paths`.
- `POST /api/free_response/tree_diagram/submit`
  - Calls `judge_tree_diagram_text_answer(...)`.
  - Returns public judge result fields for UI display.

## 3. Added UI

- Added `templates/free_response_practice.html`.
- UI includes:
  - question text
  - instruction text
  - `textarea`
  - submit button
  - result display
  - status text
- UI does not include:
  - handwriting canvas
  - image upload
  - deterministic int-answer submit
  - `correct_answer`
  - raw `expected_paths`

## 4. Dashboard / Skill Card Link

- `templates/dashboard.html` keeps using the normal `practice.practice` skill-card entry pattern.
- The existing B4 Chapter 1 `樹狀圖` skill card therefore links to:
  - `/practice/vh_數學B4_TreeDiagramCounting`
- `core/routes/practice.py` adds a narrow compatibility redirect for that one skill id to:
  - `/free_response_practice?curriculum=vocational&volume=數學B4&chapter_id=1&problem_type=tree_diagram_listing&variant=early_stopping_game`
- The redirect condition is limited to:
  - `skill_id == vh_數學B4_TreeDiagramCounting`
- Other skill cards continue to use the existing `practice.practice` link.
- This does not add `tree_diagram_listing` to adaptive sequencing or deterministic int-answer runtime.

## 5. Supported Variants

- `fixed_stage_binary_tree`
- `early_stopping_game`

## 6. Runtime Boundary

- `tree_diagram_listing` remains outside deterministic int-answer runtime.
- `tree_diagram_listing` was not added to `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`.
- B4 int-answer unit practice is unaffected.
- Adaptive scoring is not connected.
- `/check_answer` is not modified.
- `/api/adaptive/submit_and_get_next` is not modified.
- B4 deterministic `question_router` and generators are not modified.
- Public question API and page do not expose `expected_paths`.

## 7. QA Commands / Result

```text
python -m pytest -q tests/test_phase5f_d_free_response_practice_route.py -> 11 passed
python -m pytest -q tests/test_phase5f_b_tree_diagram_text_answer_judge.py -> 10 passed
python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py -> 8 passed
python -m pytest -q tests/test_vocational_math_b4_question_router_registry_canonical.py -> 24 passed
python -m pytest -q tests/test_phase5e_a_fix_guided_progression_order.py -> 9 passed
```

Notes:

- SQLAlchemy `datetime.utcnow()` deprecation warnings appeared in route tests; no test failures.
- The first 5E-A run used a shorter timeout and was rerun with a longer timeout; final result passed.

## 8. Next Steps

- Phase 5F-E: teacher review log / override schema.
- Phase 5F-F: optional teacher preview/dashboard polish.
- Phase 5F-G: handwriting / image support.
- Phase 5F-H: optional integration into guided learning path.
