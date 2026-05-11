"""Minimal B4 question router for deterministic generators (Phase 4D-1)."""

from __future__ import annotations

import random

from core.vocational_math_b4.generators import binomial as binomial_generators
from core.vocational_math_b4.generators import combination as combination_generators
from core.vocational_math_b4.generators import counting as counting_generators
from core.vocational_math_b4.generators import permutation as permutation_generators


def _combination_definition_basic(**kwargs) -> dict:
    fn = getattr(combination_generators, "combination_definition_basic", combination_generators.generate)
    return fn(**kwargs)


def _permutation_role_assignment(**kwargs) -> dict:
    fn = getattr(permutation_generators, "permutation_role_assignment", permutation_generators.generate)
    return fn(**kwargs)


def _repeated_permutation_digits(**kwargs) -> dict:
    fn = getattr(counting_generators, "repeated_permutation_digits", counting_generators.generate)
    return fn(**kwargs)


def _add_principle_mutually_exclusive_choice(**kwargs) -> dict:
    fn = getattr(
        counting_generators,
        "add_principle_mutually_exclusive_choice",
        counting_generators.generate,
    )
    return fn(**kwargs)


def _combination_properties_simplification(**kwargs) -> dict:
    fn = getattr(
        combination_generators,
        "combination_properties_simplification",
        combination_generators.generate,
    )
    return fn(**kwargs)


def _repeated_choice_basic(**kwargs) -> dict:
    fn = getattr(counting_generators, "repeated_choice_basic", counting_generators.generate)
    return fn(**kwargs)


def _mult_principle_independent_choices(**kwargs) -> dict:
    fn = getattr(
        counting_generators,
        "mult_principle_independent_choices",
        counting_generators.generate,
    )
    return fn(**kwargs)


def _mult_digits_no_repeat(**kwargs) -> dict:
    fn = getattr(counting_generators, "mult_digits_no_repeat", counting_generators.generate)
    return fn(**kwargs)


def _repeated_permutation_assignment(**kwargs) -> dict:
    fn = getattr(
        counting_generators,
        "repeated_permutation_assignment",
        counting_generators.generate,
    )
    return fn(**kwargs)


def _non_distinct_objects_arrangement(**kwargs) -> dict:
    fn = getattr(permutation_generators, "non_distinct_objects_arrangement")
    return fn(**kwargs)


_REGISTRY: dict[str, list[dict[str, object]]] = {
    "vh_數學B4_CombinationDefinition": [
        {
            "subskill_id": "b4_ch1_comb_def_01",
            "problem_type_id": "combination_definition_basic",
            "generator_key": "b4.combination.combination_definition_basic",
            "generator_fn": _combination_definition_basic,
        }
    ],
    "vh_數學B4_CombinationApplications": [
        {
            "subskill_id": "b4_ch1_comb_app_geom_02",
            "problem_type_id": "combination_polygon_count",
            "generator_key": "b4.combination.combination_polygon_count",
            "generator_fn": combination_generators.combination_polygon_count,
        },
        {
            "subskill_id": "b4_ch1_comb_app_people_01",
            "problem_type_id": "combination_required_excluded_person",
            "generator_key": "b4.combination.combination_required_excluded_person",
            "generator_fn": combination_generators.combination_required_excluded_person,
        },
        {
            "subskill_id": "b4_ch1_comb_group_selection_03",
            "problem_type_id": "combination_group_selection",
            "generator_key": "b4.combination.combination_group_selection",
            "generator_fn": combination_generators.combination_group_selection,
        },
        {
            "subskill_id": "b4_ch1_grid_shortest_path_01",
            "problem_type_id": "grid_shortest_path_count",
            "generator_key": "b4.combination.grid_shortest_path_count",
            "generator_fn": combination_generators.grid_shortest_path_count,
        },
    ],
    "vh_數學B4_Combination": [
        {
            "subskill_id": "b4_ch1_comb_basic_selection_01",
            "problem_type_id": "combination_basic_selection",
            "generator_key": "b4.combination.combination_basic_selection",
            "generator_fn": combination_generators.combination_basic_selection,
        },
        {
            "subskill_id": "b4_ch1_comb_restricted_selection_01",
            "problem_type_id": "combination_restricted_selection",
            "generator_key": "b4.combination.combination_restricted_selection",
            "generator_fn": combination_generators.combination_restricted_selection,
        },
        {
            "subskill_id": "b4_ch1_comb_seat_assignment_01",
            "problem_type_id": "combination_seat_assignment",
            "generator_key": "b4.combination.combination_seat_assignment",
            "generator_fn": combination_generators.combination_seat_assignment,
        },
    ],
    "vh_數學B4_MultiplicationPrinciple": [
        {
            "subskill_id": "b4_ch1_mult_factors_02",
            "problem_type_id": "divisor_count_prime_factorization",
            "generator_key": "b4.counting.divisor_count_prime_factorization",
            "generator_fn": counting_generators.divisor_count_prime_factorization,
        },
        {
            "subskill_id": "b4_ch1_mult_principle_independent_01",
            "problem_type_id": "mult_principle_independent_choices",
            "generator_key": "b4.counting.mult_principle_independent_choices",
            "generator_fn": _mult_principle_independent_choices,
        },
        {
            "subskill_id": "b4_ch1_mult_digits_no_repeat_01",
            "problem_type_id": "mult_digits_no_repeat",
            "generator_key": "b4.counting.mult_digits_no_repeat",
            "generator_fn": _mult_digits_no_repeat,
        },
    ],
    "vh_數學B4_PermutationOfDistinctObjects": [
        {
            "subskill_id": "b4_ch1_perm_select_03",
            "problem_type_id": "permutation_role_assignment",
            "generator_key": "b4.permutation.permutation_role_assignment",
            "generator_fn": _permutation_role_assignment,
        },
        {
            "subskill_id": "b4_ch1_perm_formula_eval_01",
            "problem_type_id": "permutation_formula_evaluation",
            "generator_key": "b4.permutation.permutation_formula_evaluation",
            "generator_fn": permutation_generators.permutation_formula_evaluation,
        },
        {
            "subskill_id": "b4_ch1_perm_full_arrangement_01",
            "problem_type_id": "permutation_full_arrangement",
            "generator_key": "b4.permutation.permutation_full_arrangement",
            "generator_fn": permutation_generators.permutation_full_arrangement,
        },
        {
            "subskill_id": "b4_ch1_perm_adjacent_block_01",
            "problem_type_id": "permutation_adjacent_block",
            "generator_key": "b4.permutation.permutation_adjacent_block",
            "generator_fn": permutation_generators.permutation_adjacent_block,
        },
        {
            "subskill_id": "b4_ch1_perm_digit_parity_01",
            "problem_type_id": "permutation_digit_parity",
            "generator_key": "b4.permutation.permutation_digit_parity",
            "generator_fn": permutation_generators.permutation_digit_parity,
        },
        {
            "subskill_id": "b4_ch1_permutation_non_adjacent_01",
            "problem_type_id": "permutation_non_adjacent_arrangement",
            "generator_key": "b4.permutation.permutation_non_adjacent_arrangement",
            "generator_fn": permutation_generators.permutation_non_adjacent_arrangement,
        },
    ],
    "vh_數學B4_RepeatedPermutation": [
        {
            "subskill_id": "b4_ch1_rep_perm_digits_01",
            "problem_type_id": "repeated_permutation_digits",
            "generator_key": "b4.counting.repeated_permutation_digits",
            "generator_fn": _repeated_permutation_digits,
        }
    ],
    "vh_數學B4_PermutationOfNonDistinctObjects": [
        {
            "subskill_id": "b4_ch1_perm_non_distinct_repeated_digits_01",
            "problem_type_id": "repeated_permutation_digits",
            "generator_key": "b4.counting.repeated_permutation_digits",
            "generator_fn": _repeated_permutation_digits,
        }
    ],
    "vh_數學B4_FactorialNotation": [
        {
            "subskill_id": "b4_ch1_factorial_solve_n_02",
            "problem_type_id": "factorial_equation_solve_n",
            "generator_key": "b4.counting.factorial_equation_solve_n",
            "generator_fn": counting_generators.factorial_equation_solve_n,
        },
        {
            "subskill_id": "b4_ch1_factorial_eval_01",
            "problem_type_id": "factorial_evaluation",
            "generator_key": "b4.counting.factorial_evaluation",
            "generator_fn": counting_generators.factorial_evaluation,
        }
    ],
    "vh_數學B4_AdditionPrinciple": [
        {
            "subskill_id": "b4_ch1_add_principle_01",
            "problem_type_id": "add_principle_mutually_exclusive_choice",
            "generator_key": "b4.counting.add_principle_mutually_exclusive_choice",
            "generator_fn": _add_principle_mutually_exclusive_choice,
        }
    ],
    "vh_數學B4_CombinationProperties": [
        {
            "subskill_id": "b4_ch1_comb_properties_01",
            "problem_type_id": "combination_properties_simplification",
            "generator_key": "b4.combination.combination_properties_simplification",
            "generator_fn": _combination_properties_simplification,
        }
    ],
    "vh_數學B4_PermutationWithRepetition": [
        {
            "subskill_id": "b4_ch1_repeated_choice_01",
            "problem_type_id": "repeated_choice_basic",
            "generator_key": "b4.counting.repeated_choice_basic",
            "generator_fn": _repeated_choice_basic,
        },
        {
            "subskill_id": "b4_ch1_rep_perm_assignment_01",
            "problem_type_id": "repeated_permutation_assignment",
            "generator_key": "b4.counting.repeated_permutation_assignment",
            "generator_fn": _repeated_permutation_assignment,
        },
    ],
    "vh_數學B4_BinomialCoefficientIdentities": [
        {
            "subskill_id": "b4_ch1_binomial_coefficient_sum_01",
            "problem_type_id": "binomial_coefficient_sum",
            "generator_key": "b4.binomial.binomial_coefficient_sum",
            "generator_fn": binomial_generators.binomial_coefficient_sum,
        },
        {
            "subskill_id": "b4_ch1_binomial_equation_solve_n_01",
            "problem_type_id": "binomial_equation_solve_n",
            "generator_key": "b4.binomial.binomial_equation_solve_n",
            "generator_fn": binomial_generators.binomial_equation_solve_n,
        },
        {
            "subskill_id": "b4_ch1_binomial_odd_even_coefficient_sum_01",
            "problem_type_id": "binomial_odd_even_coefficient_sum",
            "generator_key": "b4.binomial.binomial_odd_even_coefficient_sum",
            "generator_fn": binomial_generators.binomial_odd_even_coefficient_sum,
        },
        {
            "subskill_id": "b4_ch1_combination_hockey_stick_sum_01",
            "problem_type_id": "combination_hockey_stick_sum",
            "generator_key": "b4.binomial.combination_hockey_stick_sum",
            "generator_fn": binomial_generators.combination_hockey_stick_sum,
        },
    ],
    "vh_數學B4_BinomialTheorem": [
        {
            "subskill_id": "b4_ch1_binomial_specific_term_coefficient_01",
            "problem_type_id": "binomial_specific_term_coefficient",
            "generator_key": "b4.binomial.binomial_specific_term_coefficient",
            "generator_fn": binomial_generators.binomial_specific_term_coefficient,
        },
        {
            "subskill_id": "b4_ch1_binomial_middle_term_coefficient_01",
            "problem_type_id": "binomial_middle_term_coefficient",
            "generator_key": "b4.binomial.binomial_middle_term_coefficient",
            "generator_fn": binomial_generators.binomial_middle_term_coefficient,
        },
        {
            "subskill_id": "b4_ch1_binomial_specific_coefficient_negative_01",
            "problem_type_id": "binomial_specific_coefficient_with_negative_term",
            "generator_key": "b4.binomial.binomial_specific_coefficient_with_negative_term",
            "generator_fn": binomial_generators.binomial_specific_coefficient_with_negative_term,
        },
        {
            "subskill_id": "b4_ch1_binomial_two_variable_specific_01",
            "problem_type_id": "binomial_two_variable_specific_coefficient",
            "generator_key": "b4.binomial.binomial_two_variable_specific_coefficient",
            "generator_fn": binomial_generators.binomial_two_variable_specific_coefficient,
        },
        {
            "subskill_id": "b4_ch1_binomial_laurent_specific_power_01",
            "problem_type_id": "binomial_laurent_specific_power_coefficient",
            "generator_key": "b4.binomial.binomial_laurent_specific_power_coefficient",
            "generator_fn": binomial_generators.binomial_laurent_specific_power_coefficient,
        },
    ],
}

_ENRICHMENT_REGISTRY: dict[str, list[dict[str, object]]] = {
    "vh_數學B4_PermutationOfNonDistinctObjects": [
        {
            "subskill_id": "b4_ch1_perm_non_distinct_objects_01",
            "problem_type_id": "non_distinct_objects_arrangement",
            "generator_key": "b4.permutation.non_distinct_objects_arrangement",
            "generator_fn": _non_distinct_objects_arrangement,
        }
    ],
}


def _select_entry(
    skill_entries: list[dict[str, object]],
    seed: int | None,
    problem_type_id: str | None,
    *,
    skill_id: str | None = None,
) -> tuple[dict[str, object], str]:
    if problem_type_id is not None:
        for entry in skill_entries:
            if entry["problem_type_id"] == problem_type_id:
                return entry, "problem_type_id_specified"
        raise ValueError("problem_type_id is not supported for this skill_id.")

    if len(skill_entries) == 1:
        return skill_entries[0], "single_entry"

    # Phase 5C-B4: alternate registry vs enrichment for multiset skill so
    # `non_distinct_objects_arrangement` is evenly reachable across seeds.
    if (
        skill_id == "vh_數學B4_PermutationOfNonDistinctObjects"
        and seed is not None
        and len(skill_entries) >= 2
    ):
        idx = int(seed) % len(skill_entries)
        return skill_entries[idx], "seed_mod_router_balance"

    rng = random.Random(seed)
    return rng.choice(skill_entries), "seed_based_selection"


def generate_for_skill(
    *,
    skill_id: str,
    level: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
    problem_type_id: str | None = None,
    excluded_problem_type_ids: set[str] | None = None,
) -> dict:
    """Generate a payload for a supported B4 skill via the minimal registry."""
    if skill_id not in _REGISTRY:
        raise ValueError("Unsupported skill_id.")

    entries = _REGISTRY[skill_id] + _ENRICHMENT_REGISTRY.get(skill_id, [])
    
    if excluded_problem_type_ids:
        entries = [e for e in entries if e["problem_type_id"] not in excluded_problem_type_ids]
        if not entries:
            raise ValueError(f"No available problem types for skill {skill_id} after exclusions.")

    selected_entry, selection_reason = _select_entry(
        entries, seed, problem_type_id, skill_id=skill_id
    )

    generator_fn = selected_entry.get("generator_fn")
    if not callable(generator_fn):
        raise ValueError("generator_key could not be resolved to a callable generator.")

    payload = generator_fn(
        skill_id=skill_id,
        subskill_id=selected_entry["subskill_id"],
        difficulty=level,
        seed=seed,
        seen_parameter_tuples=seen_parameter_tuples,
        multiple_choice=multiple_choice,
    )

    payload["correct_answer"] = payload["answer"]
    payload["router_trace"] = {
        "input_skill_id": skill_id,
        "selected_subskill_id": selected_entry["subskill_id"],
        "selected_problem_type_id": selected_entry["problem_type_id"],
        "selected_generator_key": selected_entry["generator_key"],
        "selection_reason": selection_reason,
    }

    required_keys = [
        "question_text",
        "answer",
        "correct_answer",
        "choices",
        "explanation",
        "skill_id",
        "subskill_id",
        "problem_type_id",
        "generator_key",
        "difficulty",
        "diagnosis_tags",
        "remediation_candidates",
        "source_style_refs",
        "parameters",
        "router_trace",
    ]
    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise ValueError(f"Router payload missing required keys: {', '.join(missing)}")
    return payload


# ─── Phase 6C through 6F: Chap2 probability / expectation router ────────────
#
# Isolated from the Chap1 _REGISTRY above.
# Adds Phase 6D–6F conditional / independent / expectation generators.
# Handwriting listing types (sample_space_listing, event_set_listing,
# subset_listing) are NOT registered here.

from core.vocational_math_b4.generators import chap2_probability_basic as _chap2_prob
from core.vocational_math_b4.generators import chap2_conditional_probability as _chap2_cond
from core.vocational_math_b4.generators import chap2_independent_events as _chap2_indep
from core.vocational_math_b4.generators import chap2_expected_value as _chap2_exp
# Phase 6K: Chap2 remaining deterministic skill coverage
from core.vocational_math_b4.generators import chap2_probability_operations as _chap2_prob_ops
from core.vocational_math_b4.generators import chap2_basic_sets as _chap2_basic_sets
from core.vocational_math_b4.generators import chap2_expectation_extensions as _chap2_exp_ext

# Phase 7B: Chap3 First Deterministic Runtime-ready Batch
from core.vocational_math_b4.generators import chap3_statistical_measures as _chap3_stat



_CHAP2_PHASE6C1_REGISTRY: dict[str, list[dict[str, object]]] = {
    "vh_數學B4_ProbabilityDefinition": [
        {
            "subskill_id": "b4_ch2_prob_def_classical_01",
            "problem_type_id": "classical_probability_fraction",
            "generator_key": "b4.chap2.classical_probability_fraction",
            "generator_fn": _chap2_prob.classical_probability_fraction,
        },
        # Phase 6C-2
        {
            "subskill_id": "b4_ch2_prob_def_dice_coin_01",
            "problem_type_id": "dice_coin_probability_count",
            "generator_key": "b4.chap2.dice_coin_probability_count",
            "generator_fn": _chap2_prob.dice_coin_probability_count,
        },
    ],
    "vh_數學B4_ProbabilityProperties": [
        {
            "subskill_id": "b4_ch2_prob_prop_complement_01",
            "problem_type_id": "complement_probability",
            "generator_key": "b4.chap2.complement_probability",
            "generator_fn": _chap2_prob.complement_probability,
        },
        # Phase 6C-2
        {
            "subskill_id": "b4_ch2_prob_prop_union_01",
            "problem_type_id": "union_intersection_probability",
            "generator_key": "b4.chap2.union_intersection_probability",
            "generator_fn": _chap2_prob.union_intersection_probability,
        },
    ],
    "vh_數學B4_SampleSpaceAndEvents": [
        {
            "subskill_id": "b4_ch2_sample_space_count_01",
            "problem_type_id": "sample_space_count_numeric",
            "generator_key": "b4.chap2.sample_space_count_numeric",
            "generator_fn": _chap2_prob.sample_space_count_numeric,
        }
    ],
    # Phase 6D: Conditional Probability
    "vh_數學B4_ConditionalProbability": [
        {
            "subskill_id": "b4_ch2_cond_prob_basic_01",
            "problem_type_id": "conditional_probability_basic",
            "generator_key": "b4.chap2.conditional_probability_basic",
            "generator_fn": _chap2_cond.conditional_probability_basic,
        },
        {
            "subskill_id": "b4_ch2_cond_prob_wor_01",
            "problem_type_id": "without_replacement_conditional_probability",
            "generator_key": "b4.chap2.without_replacement_conditional_probability",
            "generator_fn": _chap2_cond.without_replacement_conditional_probability,
        },
    ],
    # Phase 6E: Independent Events
    "vh_數學B4_IndependentEvents": [
        {
            "subskill_id": "b4_ch2_indep_joint_01",
            "problem_type_id": "independent_joint_probability",
            "generator_key": "b4.chap2.independent_joint_probability",
            "generator_fn": _chap2_indep.independent_joint_probability,
        },
        {
            "subskill_id": "b4_ch2_indep_at_least_one_01",
            "problem_type_id": "independent_at_least_one_probability",
            "generator_key": "b4.chap2.independent_at_least_one_probability",
            "generator_fn": _chap2_indep.independent_at_least_one_probability,
        },
    ],
    # Phase 6F: Expected value (definition skill)
    "vh_數學B4_MathematicalExpectationDefinition": [
        {
            "subskill_id": "b4_ch2_exp_disc_01",
            "problem_type_id": "expectation_discrete_basic",
            "generator_key": "b4.chap2.expectation_discrete_basic",
            "generator_fn": _chap2_exp.expectation_discrete_basic,
        },
        {
            "subskill_id": "b4_ch2_exp_table_01",
            "problem_type_id": "expectation_from_distribution",
            "generator_key": "b4.chap2.expectation_from_distribution",
            "generator_fn": _chap2_exp.expectation_from_distribution,
        },
    ],
    # Phase 6K: Chap2 remaining deterministic skill coverage
    "vh_數學B4_ProbabilityOperations": [
        {
            "subskill_id": "b4_ch2_prob_ops_event_op_01",
            "problem_type_id": "event_operation_probability",
            "generator_key": "b4.chap2.event_operation_probability",
            "generator_fn": _chap2_prob_ops.event_operation_probability,
        },
        {
            "subskill_id": "b4_ch2_prob_ops_algebra_mixed_01",
            "problem_type_id": "probability_algebra_mixed",
            "generator_key": "b4.chap2.probability_algebra_mixed",
            "generator_fn": _chap2_prob_ops.probability_algebra_mixed,
        },
    ],
    "vh_數學B4_BasicConceptsOfSets": [
        {
            "subskill_id": "b4_ch2_basic_sets_op_count_01",
            "problem_type_id": "set_operation_count",
            "generator_key": "b4.chap2.set_operation_count",
            "generator_fn": _chap2_basic_sets.set_operation_count,
        },
        {
            "subskill_id": "b4_ch2_basic_sets_inex_count_01",
            "problem_type_id": "inclusion_exclusion_count",
            "generator_key": "b4.chap2.inclusion_exclusion_count",
            "generator_fn": _chap2_basic_sets.inclusion_exclusion_count,
        },
    ],
    "vh_數學B4_ApplicationsOfExpectation": [
        {
            "subskill_id": "b4_ch2_app_exp_lottery_01",
            "problem_type_id": "expectation_word_problem_profit_fairness",
            "generator_key": "b4.chap2.expectation_word_problem_profit_fairness",
            "generator_fn": _chap2_exp_ext.expectation_word_problem_profit_fairness,
        },
    ],
    "vh_數學B4_MathematicalExpectation": [
        {
            "subskill_id": "b4_ch2_math_exp_assess_numeric_01",
            "problem_type_id": "expectation_assessment_numeric",
            "generator_key": "b4.chap2.expectation_assessment_numeric",
            "generator_fn": _chap2_exp_ext.expectation_assessment_numeric,
        },
    ],
}


def generate_for_chap2_skill(
    *,
    skill_id: str,
    level: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
    problem_type_id: str | None = None,
) -> dict:
    """Generate a payload for a supported B4 Chapter 2 skill (Phase 6C through 6K).

    Supported skills and problem types:
      Phase 6C-1:
        - vh_數學B4_ProbabilityDefinition   → classical_probability_fraction
        - vh_數學B4_ProbabilityProperties   → complement_probability
        - vh_數學B4_SampleSpaceAndEvents    → sample_space_count_numeric
      Phase 6C-2:
        - vh_數學B4_ProbabilityDefinition   → dice_coin_probability_count
        - vh_數學B4_ProbabilityProperties   → union_intersection_probability
      Phase 6D:
        - vh_數學B4_ConditionalProbability  → conditional_probability_basic
        - vh_數學B4_ConditionalProbability  → without_replacement_conditional_probability
      Phase 6E:
        - vh_數學B4_IndependentEvents       → independent_joint_probability
        - vh_數學B4_IndependentEvents       → independent_at_least_one_probability
      Phase 6F:
        - vh_數學B4_MathematicalExpectationDefinition → expectation_discrete_basic
        - vh_數學B4_MathematicalExpectationDefinition → expectation_from_distribution
      Phase 6K (remaining deterministic skill coverage):
        - vh_數學B4_ProbabilityOperations   → event_operation_probability
        - vh_數學B4_ProbabilityOperations   → probability_algebra_mixed
        - vh_數學B4_BasicConceptsOfSets     → set_operation_count
        - vh_數學B4_BasicConceptsOfSets     → inclusion_exclusion_count
        - vh_數學B4_ApplicationsOfExpectation → expectation_word_problem_profit_fairness
        - vh_數學B4_MathematicalExpectation   → expectation_assessment_numeric

    Handwriting listing types (sample_space_listing, event_set_listing,
    subset_listing, tree_diagram_listing) are intentionally NOT registered.

    If problem_type_id is specified, only that entry is selected.
    Raises ValueError for unsupported skill_ids or problem_type_ids.
    """
    if skill_id not in _CHAP2_PHASE6C1_REGISTRY:
        raise ValueError(f"generate_for_chap2_skill: unsupported skill_id '{skill_id}'.")

    entries = _CHAP2_PHASE6C1_REGISTRY[skill_id]

    selected_entry, selection_reason = _select_entry(
        entries, seed, problem_type_id, skill_id=skill_id
    )

    generator_fn = selected_entry.get("generator_fn")
    if not callable(generator_fn):
        raise ValueError("generate_for_chap2_skill: generator_key could not be resolved.")

    payload = generator_fn(
        skill_id=skill_id,
        subskill_id=selected_entry["subskill_id"],
        difficulty=level,
        seed=seed,
        seen_parameter_tuples=seen_parameter_tuples,
        multiple_choice=multiple_choice,
    )

    payload["correct_answer"] = payload["answer"]
    payload["router_trace"] = {
        "input_skill_id": skill_id,
        "selected_subskill_id": selected_entry["subskill_id"],
        "selected_problem_type_id": selected_entry["problem_type_id"],
        "selected_generator_key": selected_entry["generator_key"],
        "selection_reason": selection_reason,
        "router": "chap2_phase6c1",
    }

    required_keys = [
        "question_text",
        "answer",
        "correct_answer",
        "choices",
        "explanation",
        "skill_id",
        "subskill_id",
        "problem_type_id",
        "generator_key",
        "difficulty",
        "diagnosis_tags",
        "remediation_candidates",
        "source_style_refs",
        "parameters",
        "router_trace",
    ]
    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise ValueError(
            f"generate_for_chap2_skill: payload missing required keys: {', '.join(missing)}"
        )
    return payload


# ─── Phase 7B: Chap3 Statistical Measures ────────────
#
# Isolated from Chap1 and Chap2 registries.

_CHAP3_PHASE7B_REGISTRY: dict[str, list[dict[str, object]]] = {
    "vh_數學B4_CentralTendencyMeasures": [
        {
            "subskill_id": "b4_ch3_mean_basic_01",
            "problem_type_id": "mean_basic_numeric",
            "generator_key": "b4.chap3.mean_basic_numeric",
            "generator_fn": _chap3_stat.mean_basic_numeric,
        },
        {
            "subskill_id": "b4_ch3_median_basic_01",
            "problem_type_id": "median_basic_numeric",
            "generator_key": "b4.chap3.median_basic_numeric",
            "generator_fn": _chap3_stat.median_basic_numeric,
        },
        {
            "subskill_id": "b4_ch3_mode_basic_01",
            "problem_type_id": "mode_basic_numeric",
            "generator_key": "b4.chap3.mode_basic_numeric",
            "generator_fn": _chap3_stat.mode_basic_numeric,
        },
        {
            "subskill_id": "b4_ch3_chart_mode_bar_01",
            "problem_type_id": "chart_mode_bar_reading",
            "generator_key": "b4.chap3.chart_mode_bar_reading",
            "generator_fn": _chap3_stat.chart_mode_bar_reading,
        },
        {
            "subskill_id": "b4_ch3_frequency_table_mean_01",
            "problem_type_id": "frequency_table_mean_reading",
            "generator_key": "b4.chap3.frequency_table_mean_reading",
            "generator_fn": _chap3_stat.frequency_table_mean_reading,
        },
    ],
    "vh_數學B4_WeightedMean": [
        {
            "subskill_id": "b4_ch3_weighted_mean_01",
            "problem_type_id": "weighted_mean_basic",
            "generator_key": "b4.chap3.weighted_mean_basic",
            "generator_fn": _chap3_stat.weighted_mean_basic,
        },
    ],
    "vh_數學B4_VarianceAndStandardDeviation": [
        {
            "subskill_id": "b4_ch3_variance_basic_01",
            "problem_type_id": "variance_basic_numeric",
            "generator_key": "b4.chap3.variance_basic_numeric",
            "generator_fn": _chap3_stat.variance_basic_numeric,
        },
        {
            "subskill_id": "b4_ch3_std_dev_basic_01",
            "problem_type_id": "standard_deviation_basic_numeric",
            "generator_key": "b4.chap3.standard_deviation_basic_numeric",
            "generator_fn": _chap3_stat.standard_deviation_basic_numeric,
        },
    ],
    "vh_數學B4_LinearTransformationOfData": [
        {
            "subskill_id": "b4_ch3_linear_transform_mean_01",
            "problem_type_id": "linear_transform_mean",
            "generator_key": "b4.chap3.linear_transform_mean",
            "generator_fn": _chap3_stat.linear_transform_mean,
        },
        {
            "subskill_id": "b4_ch3_linear_transform_std_var_01",
            "problem_type_id": "linear_transform_std_variance",
            "generator_key": "b4.chap3.linear_transform_std_variance",
            "generator_fn": _chap3_stat.linear_transform_std_variance,
        },
    ],
    "vh_數學B4_DispersionMeasures": [
        {
            "subskill_id": "b4_ch3_dispersion_range_01",
            "problem_type_id": "range_basic_numeric",
            "generator_key": "b4.chap3.range_basic_numeric",
            "generator_fn": _chap3_stat.range_basic_numeric,
        },
        {
            "subskill_id": "b4_ch3_dispersion_percentile_01",
            "problem_type_id": "percentile_basic_numeric",
            "generator_key": "b4.chap3.percentile_basic_numeric",
            "generator_fn": _chap3_stat.percentile_basic_numeric,
        },
        {
            "subskill_id": "b4_ch3_dispersion_quartile_01",
            "problem_type_id": "quartile_basic_numeric",
            "generator_key": "b4.chap3.quartile_basic_numeric",
            "generator_fn": _chap3_stat.quartile_basic_numeric,
        },
        {
            "subskill_id": "b4_ch3_dispersion_iqr_01",
            "problem_type_id": "interquartile_range_basic",
            "generator_key": "b4.chap3.interquartile_range_basic",
            "generator_fn": _chap3_stat.interquartile_range_basic,
        },
        {
            "subskill_id": "b4_ch3_chart_range_line_01",
            "problem_type_id": "chart_range_line_reading",
            "generator_key": "b4.chap3.chart_range_line_reading",
            "generator_fn": _chap3_stat.chart_range_line_reading,
        },
        {
            "subskill_id": "b4_ch3_frequency_table_range_01",
            "problem_type_id": "frequency_table_range_reading",
            "generator_key": "b4.chap3.frequency_table_range_reading",
            "generator_fn": _chap3_stat.frequency_table_range_reading,
        },
    ],
    "vh_數學B4_HistogramsAndFrequencyPolygons": [
        {
            "subskill_id": "b4_ch3_histogram_reading_01",
            "problem_type_id": "histogram_reading",
            "generator_key": "b4.chap3.histogram_reading",
            "generator_fn": _chap3_stat.histogram_reading,
        },
    ],
    "vh_數學B4_NormalDistributionAndEmpiricalRule": [
        {
            "subskill_id": "b4_ch3_normal_distribution_empirical_rule_01",
            "problem_type_id": "empirical_rule_interval_percentage",
            "generator_key": "b4.chap3.empirical_rule_interval_percentage",
            "generator_fn": _chap3_stat.normal_distribution_empirical_rule_basic,
        },
    ],
    "vh_數學B4_SamplingMethods": [
        {
            "subskill_id": "b4_ch3_sampling_methods_classification_01",
            "problem_type_id": "sampling_methods_classification_choice",
            "generator_key": "b4.chap3.sampling_methods_classification_choice",
            "generator_fn": _chap3_stat.sampling_methods_classification_choice,
        },
    ],
    "vh_數學B4_StatisticalBasicConcepts": [
        {
            "subskill_id": "b4_ch3_statistical_basic_concepts_choice_01",
            "problem_type_id": "statistical_basic_concepts_choice",
            "generator_key": "b4.chap3.statistical_basic_concepts_choice",
            "generator_fn": _chap3_stat.statistical_basic_concepts_choice,
        },
    ],
    "vh_數學B4_TreeDiagramCounting": [
        {
            "subskill_id": "b4_ch3_tree_diagram_runtime_shell_01",
            "problem_type_id": "tree_diagram_completion_or_listing",
            "generator_key": "b4.chap3.tree_diagram_counting_runtime_shell",
            "generator_fn": _chap3_stat.tree_diagram_counting_runtime_shell,
        },
    ],
    "vh_數學B4_FrequencyDistributionTableConstruction": [
        {
            "subskill_id": "b4_ch3_frequency_distribution_table_shell_01",
            "problem_type_id": "table_completion_handwriting",
            "generator_key": "b4.chap3.frequency_distribution_table_construction_shell",
            "generator_fn": _chap3_stat.frequency_distribution_table_construction_shell,
        },
    ],
    "vh_數學B4_SamplingSurvey": [
        {
            "subskill_id": "b4_ch3_sampling_survey_review_01",
            "problem_type_id": "sampling_survey_bias_review",
            "generator_key": "b4.chap3.sampling_survey_review_shell",
            "generator_fn": _chap3_stat.sampling_survey_review_shell,
        },
    ],
    "vh_數學B4_CumulativeFrequencyTablesAndGraphs": [
        {
            "subskill_id": "b4_ch3_cumulative_frequency_review_01",
            "problem_type_id": "cumulative_frequency_table_completion_review",
            "generator_key": "b4.chap3.cumulative_frequency_tables_graphs_review_shell",
            "generator_fn": _chap3_stat.cumulative_frequency_tables_graphs_review_shell,
        },
    ],
    "vh_數學B4_DataOrganizationAndCharts": [
        {
            "subskill_id": "b4_ch3_data_organization_review_01",
            "problem_type_id": "data_organization_chart_selection_review",
            "generator_key": "b4.chap3.data_organization_charts_review_shell",
            "generator_fn": _chap3_stat.data_organization_charts_review_shell,
        },
    ],
    "vh_數學B4_StatisticalChartReading": [
        {
            "subskill_id": "b4_ch3_statistical_chart_visibility_01",
            "problem_type_id": "statistical_chart_reading_visibility_review",
            "generator_key": "b4.chap3.statistical_chart_reading_visibility_shell",
            "generator_fn": _chap3_stat.statistical_chart_reading_visibility_shell,
        },
    ],
    "vh_數學B4_OpinionPollInterpretation": [
        {
            "subskill_id": "b4_ch3_opinion_poll_review_01",
            "problem_type_id": "opinion_poll_interpretation_review",
            "generator_key": "b4.chap3.opinion_poll_interpretation_review_shell",
            "generator_fn": _chap3_stat.opinion_poll_interpretation_review_shell,
        },
    ],
}

def generate_for_chap3_skill(
    *,
    skill_id: str,
    level: int = 1,
    seed: int | None = None,
    seen_parameter_tuples: set[tuple] | None = None,
    multiple_choice: bool = True,
    problem_type_id: str | None = None,
) -> dict:
    """Generate a payload for a supported B4 Chapter 3 skill (Phase 7B)."""
    if skill_id not in _CHAP3_PHASE7B_REGISTRY:
        raise ValueError(f"generate_for_chap3_skill: unsupported skill_id '{skill_id}'.")

    entries = _CHAP3_PHASE7B_REGISTRY[skill_id]

    selected_entry, selection_reason = _select_entry(
        entries, seed, problem_type_id, skill_id=skill_id
    )

    generator_fn = selected_entry.get("generator_fn")
    if not callable(generator_fn):
        raise ValueError("generate_for_chap3_skill: generator_key could not be resolved.")

    payload = generator_fn(
        skill_id=skill_id,
        subskill_id=selected_entry["subskill_id"],
        difficulty=level,
        seed=seed,
        seen_parameter_tuples=seen_parameter_tuples,
        multiple_choice=multiple_choice,
    )

    payload["correct_answer"] = payload["answer"]
    payload["router_trace"] = {
        "input_skill_id": skill_id,
        "selected_subskill_id": selected_entry["subskill_id"],
        "selected_problem_type_id": selected_entry["problem_type_id"],
        "selected_generator_key": selected_entry["generator_key"],
        "selection_reason": selection_reason,
        "router": "chap3_phase7b",
    }

    required_keys = [
        "question_text",
        "answer",
        "correct_answer",
        "choices",
        "explanation",
        "skill_id",
        "subskill_id",
        "problem_type_id",
        "generator_key",
        "difficulty",
        "diagnosis_tags",
        "remediation_candidates",
        "source_style_refs",
        "parameters",
        "router_trace",
    ]
    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise ValueError(
            f"generate_for_chap3_skill: payload missing required keys: {', '.join(missing)}"
        )
    return payload

