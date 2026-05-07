# Phase 5E-A-Fix: Guided Progression Order Summary

## 1. Teacher QA Observation

- Phase 5D-A teacher QA observed that B4 Chapter 1 unit practice could jump across distant topics.
- The main issue was sequence quality: first-entry practice could move from foundation topics to binomial topics before students had followed the textbook progression.
- Phase 5E-A fixes only early guided progression order. It does not change generator math, problem type coverage, remediation ontology, or adaptive policy architecture.

## 2. Changes Made

- Added `B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER`.
- Added `B4_CHAPTER_1_GUIDED_PROGRESSION_STEPS = 10`.
- Added `ordered_b4_chapter1_skills(...)` for curriculum-order sorting.
- Changed B4 Chapter 1 adaptive entry injection so `unit_skill_ids` follows the teacher-designed progression order.
- Added minimal session-engine guided progression selection for full B4 Chapter 1 unit practice during early steps.
- Kept D1-Fix inner router seed derivation unchanged.
- Kept deterministic excluded problem types blocked:
  - `tree_diagram_listing`
  - `binomial_expansion_basic`
  - `pascal_triangle_derivation`

## 3. Curriculum Progression Order

1. `vh_數學B4_AdditionPrinciple`
2. `vh_數學B4_MultiplicationPrinciple`
3. `vh_數學B4_FactorialNotation`
4. `vh_數學B4_PermutationOfDistinctObjects`
5. `vh_數學B4_RepeatedPermutation`
6. `vh_數學B4_PermutationWithRepetition`
7. `vh_數學B4_PermutationOfNonDistinctObjects`
8. `vh_數學B4_CombinationDefinition`
9. `vh_數學B4_Combination`
10. `vh_數學B4_CombinationProperties`
11. `vh_數學B4_CombinationApplications`
12. `vh_數學B4_BinomialCoefficientIdentities`
13. `vh_數學B4_BinomialTheorem`

## 4. Guided Progression Rule

- Applies only to B4 Chapter 1 teaching `unit_practice`.
- Applies only when the active pool is the full 13-skill Chapter 1 deterministic allowlist.
- Applies only before `B4_CHAPTER_1_GUIDED_PROGRESSION_STEPS` (`10`) is reached.
- Selects one skill per step by curriculum order.
- Skips guided selection after a wrong-answer submission so remediation routing can take priority.
- Skips guided selection when routing state or payload indicates remediation.
- After the guided window, selection returns to existing mixed/adaptive behavior.

## 5. Audit / Log Fields

The generated question `adaptive_audit` and selection debug can expose:

- `progression_mode`
- `progression_step`
- `guided_progression_limit`
- `selected_skill_order_index`
- `selected_skill_id`
- `selection_reason`

Expected reasons include:

- `b4_guided_progression_order`
- `b4_adaptive_mixed_after_guided_progression`
- `b4_guided_progression_skipped_remediation`
- `b4_guided_progression_skipped_after_wrong_answer`
- `b4_guided_progression_skipped_non_full_chapter_pool`

## 6. QA Commands / Result

- `python -m pytest -q tests/test_phase5e_a_fix_guided_progression_order.py` -> `9 passed`
- `python -m pytest -q tests/test_phase5c_d1_fix_b4_router_sampling_exposure.py` -> `4 passed`
- `python -m pytest -q tests/test_phase5d_a_fix1_binomial_coefficient_sum_wording.py` -> `1 passed`
- `python -m pytest -q tests/test_phase5d_a_fix2_hockey_stick_latex_shifted_variant.py` -> `5 passed`
- `python -m pytest -q tests/test_phase5c_d2_combination_hockey_stick_generator.py` -> `105 passed`
- `python -m pytest -q tests/test_b4_chapter1_adaptive_allowlist.py` -> `8 passed`
- `python -m pytest -q tests/test_phase5b_fix_a_b4_chapter_adaptive_entry_bridge.py` -> `13 passed`
- `python -m pytest -q tests/test_phase5b_fix_e1_b4_remediation_bridge.py` -> `4 passed`
- `python -m pytest -q tests/test_vocational_math_b4_question_router_registry_canonical.py` -> `24 passed`

## 7. Not Covered In This Phase

- Full B4 remediation map is not implemented in this phase.
- `return_to_mainline` target refinement remains for Phase 5E-B / Phase 5E-D.
- Formal B4 YAML subskill ontology remains future work.
- No Phase 4E coverage matrix changes were made.
- No B4 generator math logic or `problem_type_id` additions were made.
