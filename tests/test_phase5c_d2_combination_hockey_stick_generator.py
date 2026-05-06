# -*- coding: utf-8 -*-
"""Phase 5C-D2: deterministic generator for combination hockey-stick sums."""

from __future__ import annotations

import random

import pytest

from core.routes.practice import _stable_b4_inner_seed
from core.vocational_math_b4.adaptive import b4_chapter1_deterministic_allowlist as allow
from core.vocational_math_b4.domain.counting_domain_functions import combination
from core.vocational_math_b4.generators import binomial as binomial_generators
from core.vocational_math_b4.services.question_router import generate_for_skill

SKILL_ID = "vh_數學B4_BinomialCoefficientIdentities"
PROBLEM_TYPE_ID = "combination_hockey_stick_sum"
EXCLUDED = frozenset(
    {
        "tree_diagram_listing",
        "binomial_expansion_basic",
        "pascal_triangle_derivation",
    }
)


def test_standard_hockey_stick_answer_matches_identity() -> None:
    for seed in range(1, 101):
        payload = binomial_generators.combination_hockey_stick_sum(
            skill_id=SKILL_ID,
            subskill_id="b4_ch1_combination_hockey_stick_sum_01",
            difficulty=2,
            seed=seed,
            multiple_choice=False,
        )
        params = payload["parameters"]
        r = params["r"]
        n = params["n"]
        assert params["variant"] in {"standard_hockey_stick", "shifted_textbook"}
        assert payload["answer"] == combination(n + 1, r + 1)
        assert payload["answer"] == params["answer"]


@pytest.mark.parametrize("seed", range(1, 101))
def test_sampling_contract_and_latex(seed: int) -> None:
    payload = binomial_generators.combination_hockey_stick_sum(
        skill_id=SKILL_ID,
        subskill_id="b4_ch1_combination_hockey_stick_sum_01",
        difficulty=1,
        seed=seed,
        multiple_choice=True,
    )
    assert payload["problem_type_id"] == PROBLEM_TYPE_ID
    assert isinstance(payload["answer"], int)
    assert payload["answer"] > 0
    assert "C(" not in payload["question_text"]
    assert "+" in payload["question_text"]
    assert "證明" not in payload["question_text"]
    assert "hockey-stick" in payload["explanation"]
    assert "$" in payload["explanation"]
    assert "C(" not in payload["explanation"]
    assert "C^{" in payload["question_text"]
    assert payload["problem_type_id"] not in EXCLUDED
    assert len(payload["choices"]) == 4
    assert len(set(payload["choices"])) == 4
    assert payload["answer"] in payload["choices"]
    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(SKILL_ID, payload)
    assert ok, reason


def test_router_can_emit_hockey_stick_with_explicit_problem_type() -> None:
    payload = generate_for_skill(
        skill_id=SKILL_ID,
        level=1,
        seed=11,
        problem_type_id=PROBLEM_TYPE_ID,
    )
    assert payload["problem_type_id"] == PROBLEM_TYPE_ID
    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(SKILL_ID, payload)
    assert ok, reason


def test_router_seed_sampling_can_observe_hockey_stick() -> None:
    seen = set()
    for seed in range(1, 1500):
        payload = generate_for_skill(skill_id=SKILL_ID, level=1, seed=seed)
        seen.add(payload["problem_type_id"])
        if PROBLEM_TYPE_ID in seen:
            break
    assert PROBLEM_TYPE_ID in seen


def test_excluded_problem_types_remain_blocked() -> None:
    for pid in EXCLUDED:
        ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(
            SKILL_ID,
            {"problem_type_id": pid, "generator_key": "x"},
        )
        assert ok is False
        assert reason is not None


def test_d1_fix_seed_derivation_exposure_smoke_for_hockey_stick() -> None:
    pool = sorted(allow.B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST)
    hit_count = 0
    first_seen_seed: int | None = None
    validator_failures = 0
    excluded_hits = 0
    for seed in range(1, 501):
        skill_id = random.Random(seed).choice(pool)
        inner_seed = _stable_b4_inner_seed(skill_id, seed)
        payload = generate_for_skill(
            skill_id=skill_id,
            level=1,
            seed=inner_seed,
            multiple_choice=True,
        )
        if payload["problem_type_id"] == PROBLEM_TYPE_ID:
            hit_count += 1
            if first_seen_seed is None:
                first_seen_seed = seed
        if payload["problem_type_id"] in EXCLUDED:
            excluded_hits += 1
        ok, _ = allow.validate_b4_deterministic_adaptive_generator_payload(skill_id, payload)
        if not ok:
            validator_failures += 1

    assert hit_count > 0
    assert first_seen_seed is not None
    assert validator_failures == 0
    assert excluded_hits == 0
