"""Phase 5C-B4.1: permutation non-adjacent (gap method) generator."""

from __future__ import annotations

import pytest

from core.vocational_math_b4.adaptive import b4_chapter1_deterministic_allowlist as allow
from core.vocational_math_b4.domain.counting_domain_functions import combination, factorial
from core.vocational_math_b4.generators import permutation as permutation_generators
from core.vocational_math_b4.services.question_router import generate_for_skill

PERM_DISTINCT_SKILL = "vh_數學B4_PermutationOfDistinctObjects"
NON_ADJ_PT = "permutation_non_adjacent_arrangement"
EXCLUDED = frozenset(
    {
        "binomial_expansion_basic",
        "tree_diagram_listing",
        "pascal_triangle_derivation",
    }
)


def test_formula_m3_k2() -> None:
    m, k = 3, 2
    expected = factorial(m) * combination(m + 1, k) * factorial(k)
    assert expected == 72
    payload = permutation_generators.permutation_non_adjacent_arrangement(
        skill_id=PERM_DISTINCT_SKILL,
        subskill_id="b4_ch1_permutation_non_adjacent_01",
        difficulty=1,
        seed=1,
        multiple_choice=False,
    )
    assert payload["parameters"]["majority_count"] == m
    assert payload["parameters"]["minority_count"] == k
    assert payload["answer"] == expected


@pytest.mark.parametrize("seed", range(1, 101))
def test_seed_sampling_contract(seed: int) -> None:
    payload = permutation_generators.permutation_non_adjacent_arrangement(
        skill_id=PERM_DISTINCT_SKILL,
        subskill_id="b4_ch1_permutation_non_adjacent_01",
        difficulty=2,
        seed=seed,
        multiple_choice=True,
    )
    assert payload["problem_type_id"] == NON_ADJ_PT
    assert isinstance(payload["answer"], int)
    assert payload["answer"] > 0
    m, k = payload["parameters"]["majority_count"], payload["parameters"]["minority_count"]
    assert m >= k - 1
    assert payload["answer"] == factorial(m) * combination(m + 1, k) * factorial(k)

    qt = payload["question_text"]
    assert "不得相鄰" in qt or "不得彼此相鄰" in qt
    assert "列出所有排列" not in qt or "不必列出" in qt
    assert "畫圖" not in qt
    assert "圖片" not in qt

    ex = payload["explanation"]
    assert "插空法" in ex
    assert "$" in ex or "\\" in ex
    assert "C^{" in ex or "C_" in ex

    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]

    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(PERM_DISTINCT_SKILL, payload)
    assert ok, reason


def test_at_least_three_template_contexts_in_seed_range() -> None:
    ctxs: set[str] = set()
    for seed in range(1, 101):
        payload = permutation_generators.permutation_non_adjacent_arrangement(
            skill_id=PERM_DISTINCT_SKILL,
            subskill_id="b4_ch1_permutation_non_adjacent_01",
            difficulty=2,
            seed=seed,
            multiple_choice=False,
        )
        ctxs.add(payload["parameters"]["template_context"])
    assert len(ctxs) >= 3


def test_router_explicit_problem_type() -> None:
    payload = generate_for_skill(
        skill_id=PERM_DISTINCT_SKILL,
        level=1,
        seed=11,
        problem_type_id=NON_ADJ_PT,
    )
    assert payload["problem_type_id"] == NON_ADJ_PT
    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(PERM_DISTINCT_SKILL, payload)
    assert ok, reason


def test_router_sampling_includes_non_adjacent() -> None:
    seen: set[str] = set()
    for seed in range(1, 2500):
        payload = generate_for_skill(skill_id=PERM_DISTINCT_SKILL, level=1, seed=seed)
        seen.add(payload["problem_type_id"])
        assert payload["problem_type_id"] not in EXCLUDED
    assert NON_ADJ_PT in seen


def test_validator_blocks_excluded_problem_types() -> None:
    for pid in EXCLUDED:
        ok, _ = allow.validate_b4_deterministic_adaptive_generator_payload(
            PERM_DISTINCT_SKILL,
            {"problem_type_id": pid, "generator_key": "x"},
        )
        assert ok is False


def test_adjacent_block_still_works() -> None:
    payload = permutation_generators.permutation_adjacent_block(
        skill_id=PERM_DISTINCT_SKILL,
        subskill_id="b4_ch1_perm_adjacent_block_01",
        difficulty=1,
        seed=1,
        multiple_choice=False,
    )
    assert payload["problem_type_id"] == "permutation_adjacent_block"
    assert isinstance(payload["answer"], int)
