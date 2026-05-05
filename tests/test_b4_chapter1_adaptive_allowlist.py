from __future__ import annotations

import pytest

from core.vocational_math_b4.adaptive import b4_chapter1_deterministic_allowlist as allow


def test_filter_removes_manual_review_skills_but_keeps_allowlisted_b4() -> None:
    mixed = [
        "jh_數學1上_FourArithmeticOperationsOfIntegers",
        "vh_數學B4_TreeDiagramCounting",
        "vh_數學B4_Combination",
        "vh_數學B4_PascalTriangle",
        "vh_數學B4_BinomialTheorem",
        "vh_數學B4_UnknownFutureSkill",
    ]
    out, audits = allow.filter_skill_pool_for_b4_chapter1_deterministic_adaptive(mixed)
    assert "jh_數學1上_FourArithmeticOperationsOfIntegers" in out
    assert "vh_數學B4_Combination" in out
    assert "vh_數學B4_BinomialTheorem" in out
    assert "vh_數學B4_TreeDiagramCounting" not in out
    assert "vh_數學B4_PascalTriangle" not in out
    assert "vh_數學B4_UnknownFutureSkill" not in out
    reasons = {row["skill_id"]: row["reason"] for row in audits}
    assert reasons["vh_數學B4_TreeDiagramCounting"].startswith("manual_review")
    assert reasons["vh_數學B4_PascalTriangle"].startswith("manual_review")
    assert reasons["vh_數學B4_UnknownFutureSkill"] == "not_in_b4_chapter1_deterministic_allowlist"


@pytest.mark.parametrize(
    "problem_type_id",
    sorted(allow.B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES),
)
def test_validate_blocks_excluded_problem_types(problem_type_id: str) -> None:
    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(
        "vh_數學B4_BinomialTheorem",
        {"problem_type_id": problem_type_id, "generator_key": "x"},
    )
    assert ok is False
    assert reason is not None


def test_validate_passes_runtime_binomial_problem_types() -> None:
    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(
        "vh_數學B4_BinomialTheorem",
        {
            "problem_type_id": "binomial_specific_term_coefficient",
            "generator_key": "b4.binomial.binomial_specific_term_coefficient",
            "router_trace": {"selection_reason": "problem_type_id_specified"},
        },
    )
    assert ok is True
    assert reason is None


def test_validate_non_b4_always_ok_even_if_problem_type_missing() -> None:
    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(
        "jh_數學1上_FourArithmeticOperationsOfIntegers",
        {},
    )
    assert ok is True


def test_audit_dict_contains_router_trace_when_present() -> None:
    blob = allow.format_adaptive_question_audit_dict(
        "vh_數學B4_RepeatedPermutation",
        {
            "problem_type_id": "repeated_permutation_digits",
            "generator_key": "b4.counting.repeated_permutation_digits",
            "subskill_id": "x",
            "router_trace": {"selection_reason": "seed_based_selection"},
        },
    )
    assert blob["skill_id"] == "vh_數學B4_RepeatedPermutation"
    assert blob["problem_type_id"] == "repeated_permutation_digits"
    assert blob["generator_key"] == "b4.counting.repeated_permutation_digits"
    assert blob["selection_reason"] == "seed_based_selection"


def test_smoke_router_outputs_validate_across_allowlisted_skills() -> None:
    from core.vocational_math_b4.services.question_router import generate_for_skill

    for sid in sorted(allow.B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST):
        payload = generate_for_skill(skill_id=sid, level=1, seed=11)
        ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(sid, payload)
        assert ok, f"{sid}: {reason}"
