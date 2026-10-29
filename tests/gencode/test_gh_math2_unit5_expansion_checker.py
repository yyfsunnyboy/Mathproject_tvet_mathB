"""Pre-build gate for the binomial-theorem expansions (普高數學2 Unit 5): the existing ``expression_checker`` with
``algebraic_equivalent`` / ``required_form=expanded`` must judge two-variable polynomials by mathematical equivalence — expanded answers
in any term order, implicit or explicit products, superscript digits, fractional and decimal coefficients are accepted; wrong coefficients,
missing or extra terms, an unexpanded power and non-answers are rejected.  Graded through the student-side ``check_answer`` path.
"""

from __future__ import annotations

import pytest

from core.gencode.runtime_skill_wrapper import check_answer


def _contract() -> dict:
    return {"presentation_mode": "short_answer", "answer_type": "expression", "checker": "expression_checker", "checker_key": "expression_checker",
            "answer_equivalence": "algebraic_equivalent", "equivalence": "algebraic_equivalent", "equivalence_type": "algebraic_equivalent",
            "required_form": "expanded"}


def _grade(answer: str, expected: str) -> bool:
    contract = _contract()
    return bool(check_answer(answer, expected, payload={"answer_contract": contract, "correct_answer": expected}, answer_contract=contract,
                             skill_id="gh_BinomialTheorem"))


X5 = "x^5+5x^4y+10x^3y^2+10x^2y^3+5xy^4+y^5"
X4 = "16x^4-32x^3y+24x^2y^2-8xy^3+y^4"
FRAC = "1/2x^2+3/4xy-y^2"
AB = "a^3-6a^2b+12ab^2-8b^3"


@pytest.mark.parametrize(("expected", "answer"), [
    (X5, X5),
    (X5, "y^5+5xy^4+10x^2y^3+10x^3y^2+5x^4y+x^5"),  # terms reversed
    (X5, "5yx^4+x^5+10y^2x^3+10x^2y^3+5xy^4+y^5"),  # factors inside a term reordered
    (X5, "x^5+5x^4*y+10x^3*y^2+10x^2*y^3+5x*y^4+y^5"),  # explicit products
    (X5, "x⁵+5x⁴y+10x³y²+10x²y³+5xy⁴+y⁵"),  # superscript digits
    (X4, "y^4-8xy^3+24x^2y^2-32x^3y+16x^4"),
    (FRAC, "x^2/2+3xy/4-y^2"),
    (FRAC, "0.5x^2+0.75xy-y^2"),
    (FRAC, "-y^2+(3/4)xy+(1/2)x^2"),
    (AB, "-8b^3+12ab^2-6a^2b+a^3"),
])
def test_equivalent_expanded_forms_are_accepted(expected, answer):
    assert _grade(answer, expected)


@pytest.mark.parametrize(("expected", "answer"), [
    (X5, "(x+y)^5"),  # mathematically equal but not the requested expanded form
    (X5, "x^5+5x^4y+10x^3y^2+10x^2y^3+5xy^4"),  # a term missing
    (X5, "x^5+5x^4y+10x^3y^2+10x^2y^3+5xy^4+y^5+1"),  # an extra term
    (X5, "x^5+y^5"),
    (X5, ""),
    (X5, "abc"),
    (X4, "16x^4-32x^3y+24x^2y^2-8xy^3-y^4"),  # one sign wrong
    (X4, "(2x-y)^4"),
    (X4, "16x^4+32x^3y+24x^2y^2+8xy^3+y^4"),  # (2x+y)^4
    (FRAC, "1/2x^2+3/4xy+y^2"),
    (FRAC, "x^2+3/4xy-y^2"),  # fractional coefficient dropped
    (AB, "a^3-6ab^2+12a^2b-8b^3"),  # exponents swapped between terms
])
def test_wrong_or_unexpanded_answers_are_rejected(expected, answer):
    assert not _grade(answer, expected)
