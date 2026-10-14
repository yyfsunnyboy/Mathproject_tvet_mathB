# -*- coding: utf-8 -*-
"""required_form = expanded / simplest_radical / fully_factorized on the expression checker."""

from __future__ import annotations

import pytest

from core.checkers.expression_equivalence_checker import check_expression_equivalence_answer as check

E = {"required_form": "expanded"}
R = {"required_form": "simplest_radical"}
F = {"required_form": "fully_factorized"}


@pytest.mark.parametrize(("user", "correct", "contract", "accepted"), [
    ("5a^2+5b^2", "5a^2+5b^2", E, True),
    ("5b^2+5a^2", "5a^2+5b^2", E, True),
    ("5(a^2+b^2)", "5a^2+5b^2", E, False),
    ("(a-2b)^2+(2a+b)^2", "5a^2+5b^2", E, False),
    ("a^2-4ab+4b^2+4a^2+4ab+b^2", "5a^2+5b^2", E, False),
    ("a^2-2ab+b^2-1", "a^2-2ab+b^2-1", E, True),
    ("-1+b^2-2ab+a^2", "a^2-2ab+b^2-1", E, True),
    ("(a-b)^2-1", "a^2-2ab+b^2-1", E, False),
    (r"\frac{a^{3}}{8}-\frac{b^{3}}{27}", "a^3/8-b^3/27", E, True),
    (r"\frac{1}{8}a^{3}-\frac{1}{27}b^{3}", "a^3/8-b^3/27", E, True),
    ("a^3/8+b^3/27", "a^3/8-b^3/27", E, False),
    ("a^{3}+6a^{2}b+12ab^{2}+8b^{3}", "a^3+6a^2b+12ab^2+8b^3", E, True),
    ("8b^3+12ab^2+6a^2b+a^3", "a^3+6a^2b+12ab^2+8b^3", E, True),
    ("(a+2b)^3", "a^3+6a^2b+12ab^2+8b^3", E, False),
    ("a^2+4b^2+9c^2-4ab-12bc+6ac", "a^2-4ab+6ac+4b^2-12bc+9c^2", E, True),
    (r"7\sqrt{3}", "7sqrt(3)", R, True),
    (r"\sqrt{12}+\sqrt{75}", "7sqrt(3)", R, False),
    (r"2\sqrt{3}+5\sqrt{3}", "7sqrt(3)", R, False),
    (r"\sqrt{147}", "7sqrt(3)", R, False),
    ("5", "5", R, True),
    (r"(\sqrt{7}+\sqrt{2})(\sqrt{7}-\sqrt{2})", "5", R, False),
    ("7-2", "5", R, False),
    (r"\frac{\sqrt{6}}{2}", "sqrt(6)/2", R, True),
    ("sqrt(6)/2", "sqrt(6)/2", R, True),
    (r"\frac{1}{2}\sqrt{6}", "sqrt(6)/2", R, True),
    (r"\sqrt{\frac{3}{2}}", "sqrt(6)/2", R, False),
    ("3/sqrt(6)", "sqrt(6)/2", R, False),
    (r"\frac{\sqrt{3}}{\sqrt{2}}", "sqrt(6)/2", R, False),
    ("(x+1)(x^2-x+1)", "(x+1)(x^2-x+1)", F, True),
    ("(x^2-x+1)(x+1)", "(x+1)(x^2-x+1)", F, True),
    ("x^3+1", "(x+1)(x^2-x+1)", F, False),
    ("(x+3)^3", "(x+3)^3", F, True),
    ("(x+3)(x^2+6x+9)", "(x+3)^3", F, False),
    ("(x+3)(x+3)(x+3)", "(x+3)^3", F, True),
    ("(3x-y)(9x^2+3xy+y^2)", "(3x-y)(9x^2+3xy+y^2)", F, True),
    ("(x+1)(x^2+x+1)", "(x+1)(x^2-x+1)", F, False),
])
def test_required_forms(user, correct, contract, accepted):
    assert check(user, correct, answer_contract=contract) is accepted


@pytest.mark.parametrize(("user", "correct"), [
    ("5(a^2+b^2)", "5a^2+5b^2"),
    (r"\sqrt{12}+\sqrt{75}", "7sqrt(3)"),
    ("(x+3)(x^2+6x+9)", "(x+3)^3"),
])
def test_contracts_without_new_forms_keep_plain_equivalence(user, correct):
    assert check(user, correct, answer_contract={}) is True
    assert check(user, correct, answer_contract={"equivalence": "algebraic_equivalent"}) is True


def test_existing_factorized_form_is_not_tightened():
    assert check("(x+3)(x^2+6x+9)", "(x+3)^3", answer_contract={"required_form": "factorized"}) is True
    assert check("x^3+1", "(x+1)(x^2-x+1)", answer_contract={"required_form": "factorized"}) is False


def test_repeated_checks_are_cache_safe():
    for _ in range(3):
        assert check("5(a^2+b^2)", "5a^2+5b^2", answer_contract=E) is False
        assert check("5(a^2+b^2)", "5a^2+5b^2", answer_contract={}) is True
        assert check(r"7\sqrt{3}", "7sqrt(3)", answer_contract=R) is True
