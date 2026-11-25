# -*- coding: utf-8 -*-
"""P0 round-1 checker flexibility + rational-equation oracle consistency."""

from __future__ import annotations

import random

import pytest

from core.checkers.expression_equivalence_checker import (
    check_equation_equivalence_answer,
    check_expression_equivalence_answer,
)
from core.domain.polynomial_ch3_source_builders import _simple_prop_eq


@pytest.mark.parametrize(
    ("user", "correct"),
    [
        ("sqrt(41)", r"\sqrt{41}"),
        (r"\sqrt{41}", "sqrt(41)"),
        ("√41", r"\sqrt{41}"),
        ("2", "x=2"),
        ("x=2", "2"),
        ("1", "a=1"),
        ("a=1", "1"),
        ("2(x+1)^2-3", "y=2(x+1)^2-3"),
        ("y=2(x+1)^2-3", "2(x+1)^2-3"),
        ("5公尺", "5"),
        ("5m", "5"),
        ("3次", "3"),
        ("30度", "30"),
        ("30", "30度"),
        ("(x+4)²+(y-4)²=16", "(x+4)^2+(y-4)^2=16"),
        ("(x+4)^{2}+(y-4)^{2}=16", "(x+4)^2+(y-4)^2=16"),
    ],
)
def test_textbox_legal_forms_accepted(user: str, correct: str) -> None:
    assert check_expression_equivalence_answer(user, correct)


@pytest.mark.parametrize(
    ("user", "correct"),
    [
        ("3", "x=2"),
        ("b=1", "a=1"),
        ("y=2(x+1)^2-3", "2(x+1)^2-4"),
        ("5公尺", "6"),
        ("(x+4)^2+(y-4)^2=9", "(x+4)^2+(y-4)^2=16"),
    ],
)
def test_textbox_illegal_or_wrong_rejected(user: str, correct: str) -> None:
    assert not check_expression_equivalence_answer(user, correct)


def test_circle_general_form_equivalent() -> None:
    # Expanded general form of (x+4)^2+(y-4)^2=16
    assert check_equation_equivalence_answer(
        "x^2+y^2+8x-8y+16=0",
        "(x+4)^2+(y-4)^2=16",
    )


def _verify_simple_prop(bundle: dict) -> None:
    import re

    from sympy import Eq, solve, symbols

    q = str((bundle.get("givens") or {}).get("question_text") or bundle.get("question") or "")
    ans = str(
        (bundle.get("answer") or {}).get("canonical_form")
        or (bundle.get("answer") or {}).get("value")
        or ""
    )
    m = re.search(
        r"\\dfrac\{([^}]+)\}\{([^}]+)\}=\{?(-?\d+)\}?",
        q.replace(" ", ""),
    )
    assert m, q
    num_tex, den_tex, k = m.group(1), m.group(2), int(m.group(3))

    def _lin(tex: str):
        # x+5 / x-3 / x
        tex = tex.replace(" ", "")
        if tex == "x":
            return symbols("x"), 0
        mm = re.fullmatch(r"x([+-]\d+)", tex)
        assert mm, tex
        return symbols("x"), int(mm.group(1))

    x = symbols("x")
    _, a_const = _lin(num_tex)  # num = x + a_const with a_const = -a
    _, b_const = _lin(den_tex)
    # num/den = k → num - k*den = 0
    eq = Eq(x + a_const, k * (x + b_const))
    sols = [s for s in solve(eq, x) if s != -b_const]
    assert sols, (q, ans)
    assert sols[0] == int(ans) or str(sols[0]) == str(ans)


def test_simple_prop_eq_oracle_matches_stem_many_seeds() -> None:
    for seed in range(80):
        _verify_simple_prop(_simple_prop_eq(random.Random(seed)))


def test_seed86_no_longer_returns_mismatched_minus_one_for_plus5_stem() -> None:
    bundle = _simple_prop_eq(random.Random(86))
    q = str((bundle.get("givens") or {}).get("question_text") or "")
    ans = str((bundle.get("answer") or {}).get("canonical_form") or "")
    # After fix: stem and answer are consistent; the old broken pair must not recur.
    assert not (r"\dfrac{x+5}{x+3}=-2" in q.replace(" ", "") and ans == "-1")
    _verify_simple_prop(bundle)
