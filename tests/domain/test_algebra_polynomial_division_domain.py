"""Domain gate for algebra.polynomial_division (revision_0001): exact arithmetic, operations and refusals."""

from __future__ import annotations

from fractions import Fraction

import pytest

from agent_domains_candidate.algebra_polynomial_division import polynomial_division_domain as D
from agent_domains_candidate.algebra_polynomial_division.polynomial_core import (
    interpolate, pdivmod, pmul, poly, poly_plain, shift_expand, synthetic,
)


def run(op: str, **givens):
    matrix = D.build_polynomial_division_matrix(domain_operation=op, constraints=givens)
    assert getattr(D, f"validate_{op}_matrix")(matrix), (op, matrix["answer"])
    return matrix["answer"]


# --- exact core ---------------------------------------------------------------------------------------------------

def test_synthetic_division_matches_long_division_and_textbook_example_4():
    q, r, rows = synthetic(poly([1, 2, 0, 5, -7]), -3)
    assert poly_plain(q) == "x^3-x^2+3x-4" and r == 5
    assert [str(c) for c in rows[2]] == ["1", "-1", "3", "-4", "5"]
    assert pdivmod(poly([1, 2, 0, 5, -7]), poly([1, 3])) == (q, [Fraction(5)])


def test_long_division_keeps_skipped_powers():
    q, r = pdivmod(poly([1, 0, 0, 0, 1]), poly([1, 0, 1]))
    assert poly_plain(q) == "x^2-1" and poly_plain(r) == "2"
    assert pmul(poly([1, 0, 1]), q) == poly([1, 0, 0, 0, -1])


def test_shift_expansion_textbook_example_5_and_interpolation_example_10():
    assert [str(c) for c in shift_expand(poly([1, -1, -1, 1]), 2)] == ["1", "5", "7", "3"]
    assert poly_plain(interpolate([(1, 0), (2, 0), (3, 2), (4, 18)])) == "2x^3-11x^2+19x-10"


# --- operations: textbook sources + hand-derived values ------------------------------------------------------------

def test_arithmetic_items_and_validator_independence():
    ans = run("polynomial_arithmetic_items", defs={"f": [3, 0, 4, -5], "g": [1, 3, 1]},
              items=[{"op": "add", "f": "f", "g": "g"}, {"op": "sub", "f": "f", "g": "g"}, {"op": "divide", "f": "f", "g": "g"}])
    assert ans["items"][0]["value"]["plain"] == "3x^3+x^2+7x-4"
    assert ans["items"][2]["quotient"]["plain"] == "3x-9" and ans["items"][2]["remainder"]["plain"] == "28x+4"


def test_statements_truth_values():
    ans = run("evaluate_polynomial_statements", subject={"type": "poly", "coeffs": [3, -2, 0, 1, 0, 5]},
              statements=[{"kind": "is_degree_poly", "n": 5}, {"kind": "coeff_is", "power": 2, "value": 0},
                          {"kind": "coeff_is", "power": 3, "value": 0}, {"kind": "value_is", "x": -1, "value": 3}])
    assert ans["selected"] == [1, 3]
    ans = run("evaluate_polynomial_statements", subject={"type": "generic"}, mode="truth",
              statements=[{"kind": "scaled_quotient_same", "divisor": [1, 1], "k": 1}])
    assert ans["truths"] == [True]  # k = 1 changes nothing; k != 1 is the false case
    ans = run("evaluate_polynomial_statements", subject={"type": "generic"}, mode="truth",
              statements=[{"kind": "factor_product_from_zeros", "zeros": [-1, 1], "factors": [[1, 1], [1, 1]]}])
    assert ans["truths"] == [False]  # a repeated factor is not implied by one zero


def test_parameter_solving_identity_and_division():
    ans = run("solve_polynomial_parameters", form="identity", params=["a", "b"], f=[1, 1, ["a", 1], 2], d=[1, 2, ["b", 1]],
              q=[1, -1], r=[1, 5])
    assert ans["params"] == {"a": "2", "b": "3"}
    ans = run("solve_polynomial_parameters", form="division", params=["a", "b"], f=[1, ["a", 3], ["b", 1], -2],
              conditions=[{"divisor": [1, -1], "remainder": []}, {"divisor": [1, -2], "remainder": [2]}])
    assert ans["params"] == {"a": "-1", "b": "4"}


def test_taylor_shift_and_rounding():
    ans = run("taylor_shift_expansion", poly_coeffs=[1, -1, -1, 1], center=2, approx_x="1.99")
    assert ans["coefficients"] == ["1", "5", "7", "3"] and ans["approx"] == "293/100"
    with pytest.raises(ValueError):  # first-order truncation would round differently from the exact value
        D.build_polynomial_division_matrix(domain_operation="taylor_shift_expansion",
                                           constraints={"poly_coeffs": [1, 0, 0, 0], "center": 2, "approx_x": "2.4"})


def test_remainder_theorem_operations():
    assert run("evaluate_polynomial_values", items=[{"kind": "remainder_linear", "poly": [128, 0, 0, 0, 0, 4, -2, 3], "divisor": [2, 1]}])["values"][0]["canonical"] == "4"
    ans = run("solve_remainder_from_conditions", conditions=[{"divisor": [1, -4, -5], "remainder": [3, -2]}, {"divisor": [1, -2], "remainder": [4]}],
              target=[1, -1, -2])
    assert ans["remainder"]["plain"] == "3x-2"
    assert run("solve_polynomial_from_remainder_congruences", degree=3,
               conditions=[{"divisor": [1, 1, 2], "remainder": [1, 2]}, {"divisor": [1, 1, -2], "remainder": [5, -2]}])["f"]["plain"] == "x^3+2x"
    assert run("solve_remainder_with_linear_part", roots=[1, 2, 3], k=3, first_value=-3, last_value=7)["g"]["plain"] == "2x-5"


def test_factor_theorem_operations():
    assert run("select_linear_factors", poly_coeffs=[2, -1, 0, -2, 1], candidates=[[1, 1], [1, -1], [2, -1], [6, -3]])["selected"] == [2, 3, 4]
    ans = run("solve_erased_cubic", known=[1, 3, -4], root=2)
    assert ans["k"] == "-12" and ans["roots"] == ["-3", "-2", "2"]
    assert run("solve_masked_synthetic_coefficient", coefficients=[None, 0, 0, 0, 1, 0, 0, 3, -5], mask_index=0, root=-2,
               remainder=8)["value"]["canonical"] == "3/256"
    assert run("interpolate_polynomials", items=[{"degree": 3, "points": [[0, 0], [1, 0], [2, 0], [3, 24]]}])["polys"][0]["plain"] == "4x^3-12x^2+8x"
    assert run("solve_divisor_from_quotient_remainder", dividend=[1, 4, 5, -3], quotient=[1, 2], remainder=[2, -1])["divisor"]["plain"] == "x^2+2x-1"


# --- refusals: invalid inputs never produce an answer ----------------------------------------------------------------

@pytest.mark.parametrize(("op", "givens"), [
    ("solve_erased_cubic", {"known": [1, 3, -4], "root": 5}),                      # completed cubic does not split over Q
    ("solve_masked_synthetic_coefficient", {"coefficients": [None, 1, 2], "mask_index": 0, "root": 0, "remainder": 1}),
    ("solve_divisor_from_quotient_remainder", {"dividend": [1, 0, 1], "quotient": [1, 1], "remainder": [1]}),
    ("interpolate_polynomials", {"items": [{"degree": 3, "points": [[0, 0], [1, 1], [2, 4], [3, 9]]}]}),  # degree drops to 2
    ("solve_remainder_from_conditions", {"conditions": [{"divisor": [1, -1], "remainder": [1]}], "target": [1, -3, 2]}),
    ("polynomial_arithmetic_items", {"defs": {}, "items": [{"op": "synthetic", "f": [1, 2], "g": [2, 1]}]}),
])
def test_invalid_inputs_are_refused(op, givens):
    with pytest.raises(ValueError):
        D.build_polynomial_division_matrix(domain_operation=op, constraints=givens)


def test_unknown_operation_and_missing_givens_are_refused():
    with pytest.raises(ValueError):
        D.build_polynomial_division_matrix(domain_operation="nope", constraints={})
    with pytest.raises(ValueError, match="givens_required"):
        D.build_polynomial_division_matrix(domain_operation="select_linear_factors", constraints={})


def test_validators_reject_a_tampered_answer():
    matrix = D.build_polynomial_division_matrix(domain_operation="evaluate_polynomial_values",
                                                constraints={"items": [{"kind": "value", "poly": [1, 0, 1], "x": 2}]})
    assert D.validate_evaluate_polynomial_values_matrix(matrix)
    matrix["answer"]["values"][0]["canonical"] = "6"
    assert not D.validate_evaluate_polynomial_values_matrix(matrix)
