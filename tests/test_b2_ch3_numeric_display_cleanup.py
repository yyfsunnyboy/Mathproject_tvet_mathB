# -*- coding: utf-8 -*-
"""Student-facing numeric / vector display cleanup regressions."""

from __future__ import annotations

from core.domain.vector_plane_domain import canonical_exact, format_pair, latex_pair
from core.gencode.resources.rational_display import (
    compact_float_noise_token,
    latex_coeff_times_symbol,
    latex_difference_of_scaled_symbols,
    sanitize_student_math_display_text,
)


def test_display_compacts_integer_floats():
    assert canonical_exact(4.0) == "4"
    assert canonical_exact(-0.0) == "0"
    assert compact_float_noise_token("4.000000000000000") == "4"
    assert compact_float_noise_token("-0.000000000000000") == "0"


def test_display_exact_half():
    assert canonical_exact(2.5) in {"5/2", "2.5"}
    assert canonical_exact(2.500000000000000) == "5/2"
    assert format_pair(4.0, -2.5) == "(4, -5/2)"
    assert "000000" not in latex_pair(4.0, -2.5)


def test_ordinary_short_decimals_not_banned():
    # Short classroom decimals must remain readable; only long tails are sanitized.
    assert sanitize_student_math_display_text("2.5") == "2.5"
    assert sanitize_student_math_display_text("0.75") == "0.75"
    assert "000000" not in sanitize_student_math_display_text("2.500000000000000")


def test_trivial_vector_coefficients_removed():
    assert latex_coeff_times_symbol(1, r"\vec{a}") == r"\vec{a}"
    assert latex_coeff_times_symbol(-1, r"\vec{a}") == r"-\vec{a}"
    assert latex_difference_of_scaled_symbols(1, r"\vec{a}", "1/2", r"\vec{b}") == r"\vec{a}-\frac{1}{2}\vec{b}"
    cleaned = sanitize_student_math_display_text(r"1\vec{a}-1\vec{b}")
    assert cleaned == r"\vec{a}-\vec{b}"


def test_construct_combo_mcq_has_no_float_noise_and_keeps_label_answer():
    from skills import vh_數學B2_SubSection_3_1_4 as m

    payload = m.generate(seed=7, component_id="src_11749")
    blob = (payload.get("question_text") or "") + "".join(
        str(c.get("text") or "") + str(c.get("value") or "") for c in (payload.get("choices") or [])
    )
    assert "000000" not in blob
    assert payload.get("answer") in {"A", "B", "C", "D"}
    assert len(payload.get("choices") or []) == 4


def test_internal_math_objects_unchanged_by_display_helpers():
    import sympy as sp

    c1 = sp.Rational(1, 2)
    ax = 4.0
    # Display path must not mutate the symbolic coefficient used for math.
    _ = latex_difference_of_scaled_symbols(c1, r"\vec{a}", c1, r"\vec{b}")
    assert c1 == sp.Rational(1, 2)
    assert ax == 4.0
    rx = c1 * ax
    assert abs(float(rx) - 2.0) < 1e-12
