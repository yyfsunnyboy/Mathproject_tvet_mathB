"""Minimal B4 question router for deterministic generators (Phase 4D-1)."""

from __future__ import annotations

import random

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
    ],
    "vh_數學B4_RepeatedPermutation": [
        {
            "subskill_id": "b4_ch1_rep_perm_digits_01",
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
}


def _select_entry(skill_entries: list[dict[str, object]], seed: int | None, problem_type_id: str | None) -> tuple[dict[str, object], str]:
    if problem_type_id is not None:
        for entry in skill_entries:
            if entry["problem_type_id"] == problem_type_id:
                return entry, "problem_type_id_specified"
        raise ValueError("problem_type_id is not supported for this skill_id.")

    if len(skill_entries) == 1:
        return skill_entries[0], "single_entry"

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
) -> dict:
    """Generate a payload for a supported B4 skill via the minimal registry."""
    if skill_id not in _REGISTRY:
        raise ValueError("Unsupported skill_id.")

    entries = _REGISTRY[skill_id]
    selected_entry, selection_reason = _select_entry(entries, seed, problem_type_id)

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
