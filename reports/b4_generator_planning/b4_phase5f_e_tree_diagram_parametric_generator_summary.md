# Phase 5F-E: Tree Diagram Parametric Generator Summary

## 1. Problem

B4 Chapter 1 `tree_diagram_listing` had working practice-page handwriting flow, AI rubric grading, and next-question loading, but the next-question sequence only alternated between two fixed stems:

- `early_stopping_game`
- `fixed_stage_binary_tree`

This made the runtime usable but not yet a parametric free-response question source.

## 2. Change

`build_tree_diagram_listing_payload(...)` now supports optional `seed` and `index` arguments:

```python
build_tree_diagram_listing_payload(
    variant: str = "early_stopping_game",
    seed: int | None = None,
    index: int | None = None,
) -> dict
```

Existing calls with only `variant` remain compatible and keep the original representative questions.

## 3. Supported Variants

- `fixed_stage_binary_tree`
- `early_stopping_game`

## 4. Supported Parameters

- `labels`
  - fixed-stage: `正/反`, `成/敗`, `紅/藍`, `甲/乙`
  - early-stopping: `甲/乙`, `紅/藍`, `A/B`
- `stages`
  - fixed-stage binary tree supports 2 or 3 stages.
- `index` / `seed`
  - selects a deterministic label/stage parameter set.

## 5. Expected Paths Rules

- `fixed_stage_binary_tree`
  - Generates all binary sequences of length `stages`.
  - `expected_count = 2 ** stages`.
- `early_stopping_game`
  - Uses first-to-2-wins paths:
    - `AA`
    - `ABA`
    - `ABB`
    - `BAA`
    - `BAB`
    - `BB`
  - `expected_count = 6`.

## 6. Practice Runtime Behavior

For `skill=vh_數學B4_TreeDiagramCounting` and `problem_type=tree_diagram_listing`:

- `tree_diagram_index % 2` selects the variant.
- The same index is mapped to a per-variant parameter index, so later questions change labels or stages inside the same variant.
- Response includes public fields:
  - `problem_type_id`
  - `answer_type`
  - `grading_mode`
  - `variant`
  - `question_text`
  - `expected_count`
  - `path_labels`
  - `requires_listing_or_tree`
- `expected_paths` remains available in session for `/analyze_handwriting` rubric use and is not returned in the public `/get_next_question` JSON.

## 7. QA Commands / Result

```text
python -m pytest -q tests/test_phase5f_b_tree_diagram_text_answer_judge.py -> 13 passed
python -m pytest -q tests/test_phase5f_d_free_response_practice_route.py -> 14 passed
python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py -> 8 passed
```

## 8. Runtime Boundary

- Still does not use deterministic int-answer runtime.
- Still does not add `tree_diagram_listing` to deterministic allowlist.
- Still does not add `skills/vh_數學B4_TreeDiagramCounting.py`.
- Still does not modify `/check_answer`.
- Still does not modify `/api/adaptive/submit_and_get_next`.
- Still does not modify B4 deterministic `question_router` or generators.
- Existing `/analyze_handwriting` tree diagram rubric flow is preserved.
