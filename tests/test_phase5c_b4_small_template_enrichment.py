"""Phase 5C-B4: small template enrichment smoke + seed sampling for B4 Chapter 1 skills."""

from __future__ import annotations

import pytest

from core.vocational_math_b4.adaptive import b4_chapter1_deterministic_allowlist as allow
from core.vocational_math_b4.services.question_router import generate_for_skill

EXCLUDED_PROBLEM_TYPES = frozenset(
    {
        "binomial_expansion_basic",
        "tree_diagram_listing",
        "pascal_triangle_derivation",
    }
)

SKILL_TEMPLATE_SKILLS: dict[str, str] = {
    "vh_數學B4_RepeatedPermutation": "template_context",
    "vh_數學B4_CombinationDefinition": "template_context",
    "vh_數學B4_CombinationProperties": "variant",
    "vh_數學B4_AdditionPrinciple": "template_context",
}


@pytest.mark.parametrize("skill_id", list(SKILL_TEMPLATE_SKILLS))
def test_seed_sampling_int_answer_and_not_excluded(skill_id: str) -> None:
    param_key = SKILL_TEMPLATE_SKILLS[skill_id]
    contexts: set[str] = set()
    for seed in range(1, 51):
        payload = generate_for_skill(skill_id=skill_id, level=1, seed=seed)
        assert isinstance(payload["answer"], int)
        assert payload["problem_type_id"] not in EXCLUDED_PROBLEM_TYPES
        ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(skill_id, payload)
        assert ok, f"{skill_id} seed={seed}: {reason}"
        assert len(payload["choices"]) == 4
        assert payload["answer"] in payload["choices"]
        assert "\\" in payload["explanation"] or "$" in payload["explanation"]
        ctx = payload["parameters"].get(param_key)
        if isinstance(ctx, str):
            contexts.add(ctx)
    assert len(contexts) >= 2, f"{skill_id} expected multiple {param_key}, got {contexts}"


def test_permutation_non_distinct_router_balances_problem_types() -> None:
    skill_id = "vh_數學B4_PermutationOfNonDistinctObjects"
    pids = {generate_for_skill(skill_id=skill_id, level=1, seed=s)["problem_type_id"] for s in range(1, 51)}
    assert "non_distinct_objects_arrangement" in pids
    assert "repeated_permutation_digits" in pids


def test_non_distinct_template_contexts_from_generator_directly() -> None:
    from core.vocational_math_b4.generators import permutation as perm_gen

    ctxs: set[str] = set()
    for seed in range(1, 80):
        payload = perm_gen.non_distinct_objects_arrangement(
            skill_id="vh_數學B4_PermutationOfNonDistinctObjects",
            subskill_id="b4_ch1_perm_non_distinct_objects_01",
            difficulty=1,
            seed=seed,
        )
        ctx = str(payload["parameters"].get("context") or "")
        if ctx:
            ctxs.add(ctx)
    assert "word_tiles" in ctxs or "badge_strip" in ctxs or len(ctxs) >= 3


def test_combination_properties_two_term_sum_appears() -> None:
    from core.vocational_math_b4.generators.combination import combination_properties_simplification

    found = False
    for seed in range(0, 400):
        payload = combination_properties_simplification(
            skill_id="vh_數學B4_CombinationProperties",
            subskill_id="b4_ch1_comb_properties_01",
            seed=seed,
        )
        if payload["parameters"].get("variant") == "two_term_sum":
            assert "+" in payload["question_text"]
            assert isinstance(payload["answer"], int)
            found = True
            break
    assert found, "expected at least one two_term_sum variant in reasonable seed range"
