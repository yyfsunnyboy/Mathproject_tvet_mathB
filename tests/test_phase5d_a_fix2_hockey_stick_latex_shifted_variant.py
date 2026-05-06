# -*- coding: utf-8 -*-
"""Phase 5D-A Fix-2: hockey-stick LaTeX + shifted textbook variant."""

from __future__ import annotations

import re

from core.vocational_math_b4.domain.counting_domain_functions import combination
from core.vocational_math_b4.generators import binomial as binomial_generators
from core.vocational_math_b4.services.question_router import generate_for_skill


SKILL_ID = "vh_數學B4_BinomialCoefficientIdentities"
PROBLEM_TYPE_ID = "combination_hockey_stick_sum"


def _has_cn_r_latex(s: str) -> bool:
    return bool(re.search(r"\$.*C\^\{[0-9]+\}_\{[0-9]+\}.*\$", s))


def _has_shifted_term_m_m_minus_r_latex(s: str) -> bool:
    # Look for at least one explicit C^{m}_{m-r} shape; e.g. C^{7}_{5}
    # We keep it simple: require some C^{m}_{k} in question_text AND ensure it is not only C^{m}_{r}.
    return bool(re.search(r"C\^\{[0-9]+\}_\{[0-9]+\}", s)) and bool(re.search(r"C\^\{[0-9]+\}_\{0\}", s))


def test_standard_and_shifted_do_not_emit_plain_C_parentheses() -> None:
    for seed in range(1, 101):
        payload = binomial_generators.combination_hockey_stick_sum(
            skill_id=SKILL_ID,
            subskill_id="b4_ch1_combination_hockey_stick_sum_01",
            difficulty=2,
            seed=seed,
            multiple_choice=False,
        )
        assert payload["problem_type_id"] == PROBLEM_TYPE_ID
        assert "C(" not in payload["question_text"]
        assert "C(" not in payload["explanation"]
        assert _has_cn_r_latex(payload["question_text"])
        assert "$" in payload["explanation"]


def test_shifted_textbook_has_staggered_terms_and_correct_answer() -> None:
    # Seeds with (seed % 2 == 1) should produce shifted_textbook.
    for seed in range(1, 101, 2):
        payload = binomial_generators.combination_hockey_stick_sum(
            skill_id=SKILL_ID,
            subskill_id="b4_ch1_combination_hockey_stick_sum_01",
            difficulty=2,
            seed=seed,
            multiple_choice=False,
        )
        params = payload["parameters"]
        assert params["variant"] == "shifted_textbook"
        r = params["r"]
        n = params["n"]
        assert payload["answer"] == combination(n + 1, r + 1)
        assert "C(" not in payload["question_text"]
        assert _has_shifted_term_m_m_minus_r_latex(payload["question_text"])
        assert "$" in payload["question_text"]
        assert "$" in payload["explanation"]


def test_standard_hockey_stick_has_normal_terms_and_correct_answer() -> None:
    # Seeds with (seed % 2 == 0) should produce standard_hockey_stick.
    for seed in range(2, 101, 2):
        payload = binomial_generators.combination_hockey_stick_sum(
            skill_id=SKILL_ID,
            subskill_id="b4_ch1_combination_hockey_stick_sum_01",
            difficulty=2,
            seed=seed,
            multiple_choice=False,
        )
        params = payload["parameters"]
        assert params["variant"] == "standard_hockey_stick"
        r = params["r"]
        n = params["n"]
        assert payload["answer"] == combination(n + 1, r + 1)
        assert "C(" not in payload["question_text"]
        assert "C^{" in payload["question_text"]


def test_seed_1_to_100_sampling_observes_both_variants() -> None:
    seen = set()
    for seed in range(1, 101):
        payload = binomial_generators.combination_hockey_stick_sum(
            skill_id=SKILL_ID,
            subskill_id="b4_ch1_combination_hockey_stick_sum_01",
            difficulty=2,
            seed=seed,
            multiple_choice=False,
        )
        seen.add(payload["parameters"]["variant"])
    assert "standard_hockey_stick" in seen
    assert "shifted_textbook" in seen


def test_router_can_emit_hockey_stick_sum_and_validator_passes() -> None:
    payload = generate_for_skill(
        skill_id=SKILL_ID,
        level=1,
        seed=11,
        problem_type_id=PROBLEM_TYPE_ID,
    )
    assert payload["problem_type_id"] == PROBLEM_TYPE_ID
    assert "C(" not in payload["question_text"]
    assert "C(" not in payload["explanation"]

