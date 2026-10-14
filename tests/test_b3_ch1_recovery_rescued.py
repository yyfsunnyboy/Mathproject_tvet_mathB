# -*- coding: utf-8 -*-
"""B3 Ch1 recovery pass: screenshot-rescued locked stems (11901/11952/11918)."""
from __future__ import annotations

from fractions import Fraction

import pytest

from core.domain.sequence_series_domain import (
    arithmetic_diff_from_two,
    arithmetic_partial_sum,
    arithmetic_term_from_two,
    build_sequence_series_matrix,
    canonical_exact,
    validate_sequence_series_matrix,
)

LEAK_MARKERS = ("TODO", "FIXME", "placeholder", "NoneType", "traceback", "DEBUG")


def _assert_clean(matrix: dict) -> None:
    assert validate_sequence_series_matrix(matrix)
    blob = " ".join(
        [
            str(matrix.get("question_text") or ""),
            str(matrix.get("answer") or ""),
            str(matrix.get("explanation") or ""),
            str(matrix.get("choices") or ""),
        ]
    ).lower()
    for m in LEAK_MARKERS:
        assert m.lower() not in blob


def test_pitcher_locked_stem_50_samples():
    fingerprints = set()
    for seed in range(50):
        m = build_sequence_series_matrix(
            operation="arithmetic_from_two_terms",
            seed=seed,
            locked_stem="pitcher_training_days",
        )
        _assert_clean(m)
        g = m["givens"]
        assert "桃太郎" in (m.get("question_text") or "")
        assert "(1)" in (m.get("question_text") or "")
        d = arithmetic_diff_from_two(g["ai"], int(g["i"]), g["aj"], int(g["j"]))
        ak = arithmetic_term_from_two(g["ai"], int(g["i"]), g["aj"], int(g["j"]), int(g["k"]))
        parts = (m.get("answer") or {}).get("parts") or {}
        assert parts["(1)"] == canonical_exact(d)
        assert parts["(2)"] == canonical_exact(ak)
        assert d > 0
        fp = (int(g["i"]), int(g["j"]), canonical_exact(g["ai"]), canonical_exact(g["aj"]), int(g["k"]))
        fingerprints.add(fp)
        assert fp != (5, 13, "41", "73", 10)
    assert len(fingerprints) >= 2


def test_installment_locked_stem_50_samples_mcq():
    for seed in range(50):
        m = build_sequence_series_matrix(
            operation="arithmetic_series_sum_given",
            seed=seed,
            locked_stem="installment_equal_step_ap",
            presentation_mode="single_choice",
            answer_type="single_choice",
        )
        _assert_clean(m)
        g = m["givens"]
        assert "分期付款" in (m.get("question_text") or "")
        sn = arithmetic_partial_sum(g["a1"], g["d"], int(g["n"]))
        assert g["a1"] == g["d"] == g["monthly_base_step"]
        ans_block = m.get("answer") or {}
        assert canonical_exact(ans_block.get("canonical_form") or ans_block.get("value")) == canonical_exact(sn)
        assert (int(g["monthly_base_step"]), int(g["n"])) != (1000, 10)
        choices = m.get("choices") or []
        assert len(choices) == 4
        values = [str(c.get("value") if isinstance(c, dict) else c) for c in choices]
        texts = [str(c.get("text") if isinstance(c, dict) else c) for c in choices]
        assert len(set(values)) == 4
        assert len(set(texts)) == 4
        correct = str(m.get("semantic_answer") or "")
        assert sum(1 for v in values if v == correct) == 1


def test_triangular_stack_text_surrogate_50_samples():
    for seed in range(50):
        m = build_sequence_series_matrix(
            operation="arithmetic_series_sum_given",
            seed=seed,
            locked_stem="triangular_stacking_cups",
        )
        _assert_clean(m)
        g = m["givens"]
        q = m.get("question_text") or ""
        assert "疊杯" in q
        assert "第1層有1個" in q
        assert "image" not in q.lower()
        assert Fraction(g["a1"]) == 1 and Fraction(g["d"]) == 1
        n = int(g["n"])
        sn = arithmetic_partial_sum(1, 1, n)
        assert canonical_exact((m.get("answer") or {}).get("canonical_form") or (m.get("answer") or {}).get("value")) == canonical_exact(sn)
        assert sn == Fraction(n * (n + 1), 2)


def test_pitcher_multipart_accept_reject():
    from skills import vh_數學B3_SubSection_1_1_2 as mod

    payload = mod.generate(seed=7, component_id="src_11901")
    ans = payload.get("answer")
    assert mod.check(ans, ans, question_payload=payload)
    bad = {"(1)": "0", "(2)": "0"}
    assert not mod.check(bad, ans, question_payload=payload)


def test_installment_package_mcq_unique():
    from skills import vh_數學B3_SubSection_1_1_5 as mod

    payload = mod.generate(seed=11, component_id="src_11952")
    choices = payload.get("choices") or []
    assert len(choices) == 4
    texts = []
    for c in choices:
        if isinstance(c, dict):
            texts.append(str(c.get("text") or c.get("value") or ""))
        else:
            texts.append(str(c))
    assert len(set(texts)) == 4
    assert mod.check(payload.get("answer"), payload.get("answer"), question_payload=payload)


def test_stack_package_no_image_dependency():
    from skills import vh_數學B3_SubSection_1_1_5 as mod

    payload = mod.generate(seed=3, component_id="src_11918")
    q = str(payload.get("question") or payload.get("question_text") or "")
    assert "疊杯" in q and "層" in q
    assert not payload.get("visual_spec")
    assert not payload.get("image_url")
