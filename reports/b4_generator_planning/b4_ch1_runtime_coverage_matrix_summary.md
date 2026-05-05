# B4 Chapter 1 Runtime Coverage Matrix Summary

## 1. Summary Purpose

This report summarizes B4 Chapter 1 runtime coverage across problem types, generators, question router entries, skill wrappers, and web smoke status.

Phase 4E-16B updates only coverage documentation. It does not modify Python code, tests, routes, frontend files, `app.py`, generators, or wrappers.

## 2. Coverage Snapshot

- problem_type total: 28
- runtime_ready: 25
- implemented_not_web_tested: 0
- generator_ready_no_wrapper: 0
- planned_only: 0
- excluded: 3
- manual_review / excluded-like: 3
- has_generator=yes: 26
- in_question_router=yes: 25
- has_skill_wrapper=yes: 25
- web_smoke_tested=yes: 25

Notes:
- The CSV currently uses `coverage_status=excluded` for non-runtime/manual-review items.
- `binomial_expansion_basic` is recorded as `excluded`, with `manual_review / future_ai_judged / future_free_response / normalization_required` in notes.
- `tree_diagram_listing` remains `excluded`, with `manual_review / future visualization` in notes.
- `pascal_triangle_derivation` remains an excluded/manual-review item.
- `has_generator=yes` is 26 because `binomial_expansion_basic` has a generator, but it is not runtime-ready and is not connected to router/wrapper.

## 3. Reconciliation Notes

- Phase 4E-7B reconciled prior runtime entries where generators and wrappers already existed, including `combination_group_selection` and `factorial_equation_solve_n`.
- Phase 4E-9 added three runtime-ready problem types and confirmed web smoke coverage for related B4 practice pages.
- Phase 4E-11 added three counting/permutation runtime problem types and verified targeted tests and web smoke behavior.
- Phase 4E-12C added three more runtime-ready problem types for permutation and combination cases.
- Phase 4E-13C added three binomial int-answer runtime problem types:
  - `binomial_coefficient_sum`
  - `binomial_specific_term_coefficient`
  - `binomial_equation_solve_n`
- Phase 4E-13C intentionally left `binomial_expansion_basic` out of runtime because expansion answers are not a simple int-answer path.
- Phase 4E-14B added two permutation runtime-ready problem types:
  - `permutation_adjacent_block`
  - `permutation_digit_parity`
- Phase 4E-14B brought Chapter 1 runtime coverage to 25 / 28, with two `planned_only` items and one excluded/manual-review item.
- Phase 4E-15A decided that `tree_diagram_listing` should not be directly connected to the current general practice runtime.
- Phase 4E-15A reason: tree diagrams assess visualization and complete listing ability; converting the task into an int-answer question would collapse it into multiplication-principle counting.
- Phase 4E-15B moved `tree_diagram_listing` out of `planned_only` and marked it as manual_review / future visualization through the existing excluded-style CSV status.
- Phase 4E-16A decided that `binomial_expansion_basic` should not be directly connected to the current general practice runtime.
- Phase 4E-16A reason: answer is `list[int]`, and students may enter coefficient lists or full polynomials; without normalization this would cause non-mathematical false negatives.
- This type may later follow handwriting AI checked, AI-judged free-response, or polynomial normalization paths.
- Phase 4E-16B moves `binomial_expansion_basic` out of `planned_only` and marks it as excluded-style manual_review / future_ai_judged.
- Chapter 1 general runtime `planned_only` is now zero.
- Chapter 1 general runtime can be treated as a practical 25 / 28 closure.

## 4. runtime_ready List

The following 25 problem types remain `runtime_ready`:

1. `combination_definition_basic`
2. `combination_polygon_count`
3. `combination_group_selection`
4. `combination_properties_simplification`
5. `combination_required_excluded_person`
6. `add_principle_mutually_exclusive_choice`
7. `divisor_count_prime_factorization`
8. `factorial_equation_solve_n`
9. `repeated_permutation_digits`
10. `repeated_choice_basic`
11. `permutation_role_assignment`
12. `combination_basic_selection`
13. `permutation_formula_evaluation`
14. `factorial_evaluation`
15. `mult_principle_independent_choices`
16. `mult_digits_no_repeat`
17. `repeated_permutation_assignment`
18. `permutation_full_arrangement`
19. `permutation_adjacent_block`
20. `permutation_digit_parity`
21. `combination_restricted_selection`
22. `combination_seat_assignment`
23. `binomial_coefficient_sum`
24. `binomial_specific_term_coefficient`
25. `binomial_equation_solve_n`

## 5. planned_only List

There are currently no `planned_only` problem types.

## 6. manual_review / excluded-like List

The following three problem types are outside the current deterministic int-answer general practice runtime target:

1. `binomial_expansion_basic`
   - CSV status: `excluded`
   - Manual-review reason: full expansion answers are coefficient lists or polynomial free responses; current runtime is not prepared for required normalization.
   - Future path: handwriting AI checked, AI-judged free-response, coefficient-list normalization, or polynomial normalization.

2. `tree_diagram_listing`
   - CSV status: `excluded`
   - Manual-review reason: tree diagrams are visualization/listing tasks; current runtime is strongest for int-answer and choices.
   - Future path: visualization support, structured-answer listing, or teacher-only/manual review material.

3. `pascal_triangle_derivation`
   - CSV status: `excluded`
   - Manual-review reason: derivation-style content is not a current deterministic int-answer runtime target.
   - Future path: teacher review, AI-judged derivation, or future structured proof/derivation workflow.

## 7. Current Closure View

- Chapter 1 stable runtime coverage remains 25 / 28.
- Chapter 1 general runtime `planned_only` is now 0.
- `binomial_expansion_basic`, `tree_diagram_listing`, and `pascal_triangle_derivation` are not counted as runtime-ready and are not treated as missing generator/router/wrapper tasks for the current runtime closure.
- No Python, tests, router, frontend, `app.py`, generator, or wrapper changes are part of Phase 4E-16B.

