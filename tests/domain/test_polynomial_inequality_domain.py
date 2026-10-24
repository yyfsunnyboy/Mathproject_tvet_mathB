"""Domain contract for inequality.polynomial (普高數學1 Unit 11): exact answers, independent validators, refusals."""

from __future__ import annotations

import copy
from fractions import Fraction

import pytest

from agent_domains_candidate.polynomial_inequality import polynomial_inequality_domain as D
from agent_domains_candidate.polynomial_inequality import polynomial_inequality_specs as S


def _matrix(op: str, givens: dict) -> dict:
    return D.build_polynomial_inequality_matrix(domain_operation=op, constraints=copy.deepcopy(givens))


def _validate(matrix: dict) -> bool:
    return getattr(D, f"validate_{matrix['domain_operation']}_matrix")(matrix)


SOURCES = {cid: (OP, src) for cid, (_skill, OP, src, _sampler) in {**S.COMPONENTS, **S.REV2_COMPONENTS}.items()}


@pytest.mark.parametrize("cid", sorted(SOURCES))
def test_source_matrix_passes_its_independent_validator(cid):
    op, givens = SOURCES[cid]
    assert _validate(_matrix(op, givens)) is True


@pytest.mark.parametrize("cid", sorted(SOURCES))
def test_validator_rejects_a_tampered_answer(cid):
    op, givens = SOURCES[cid]
    matrix = _matrix(op, givens)
    bad = copy.deepcopy(matrix)
    rec = bad["answer"].get("items", [None])[0] if "items" in bad["answer"] else None
    if op == "polynomial_statements":
        bad["answer"]["truths"][0] = not bad["answer"]["truths"][0]
        bad["answer"]["selected"] = [i for i, t in enumerate(bad["answer"]["truths"], start=1) if t]
    elif op == "polynomial_graph_solutions":
        rec["gt"], rec["lt"] = rec["lt"], rec["gt"]
    elif op == "polynomial_inequality_parameters":
        kind = givens["items"][0]["kind"]
        if kind in ("quad_from_solution", "cubic_from_solution", "quad_factor_param"):
            rec["a"] = {"canonical": str(Fraction(rec["a"]["canonical"]) + 1), "latex": "x"}
        elif kind == "always_true":
            rec["k"] = {"canonical": "-1<=x<=9", "latex": ""}
        else:
            rec["solution"] = {"canonical": "x<-9", "latex": ""}
    elif op == "polynomial_applications":
        rec["solution"] = {"canonical": "k>100" if givens["items"][0]["kind"] == "projectile_ceiling" else "x>100", "latex": ""}
    else:
        rec["solution"] = {"canonical": "x>1234", "latex": ""} if rec["solution"]["canonical"] != "x>1234" else {"canonical": "無解", "latex": ""}
    assert _validate(bad) is False


def test_validator_rejects_wrong_operation_and_unknown_operation_is_refused():
    op, givens = SOURCES[12631]
    matrix = _matrix(op, givens)
    assert D.validate_polynomial_applications_matrix(matrix) is False
    with pytest.raises(ValueError):
        _matrix("not_an_operation", givens)
    with pytest.raises(ValueError):
        D.build_polynomial_inequality_matrix(domain_operation=op, constraints={})


def test_degenerate_inputs_are_refused():
    with pytest.raises(ValueError):  # a relation that contradicts the stated solution shape
        _matrix("polynomial_inequality_parameters", {"items": [{"kind": "quad_from_solution", "p": 2, "roots": [-3, 1], "rel": ">", "shape": "between"}]})
    with pytest.raises(ValueError):  # a root list with a repeated value cannot be a graph with separately labelled zeros
        _matrix("polynomial_graph_solutions", {"items": [{"roots": [[1, 1], [1, 2]], "lead": 1}]})
    with pytest.raises(ValueError):  # identical sides
        _matrix("solve_polynomial_inequality", {"items": [{"left": {"poly": [1, 0]}, "rel": ">", "right": {"poly": [1, 0]}}]})


def test_endpoint_and_strictness_rules():
    sol = lambda left, rel: _matrix("solve_polynomial_inequality", {"items": [{"left": left, "rel": rel}]})["answer"]["items"][0]["solution"]["canonical"]  # noqa: E731
    sq = {"poly": [1, -4, 4]}
    assert sol(sq, ">") == "x<2 or x>2" and sol(sq, ">=") == "全體實數" and sol(sq, "<") == "無解" and sol(sq, "<=") == "x=2"
    assert sol({"poly": [1, -3, 2]}, "<=") == "1<=x<=2" and sol({"poly": [1, -3, 2]}, "<") == "1<x<2"
    assert sol({"poly": [1, 0, 1]}, ">") == "全體實數" and sol({"poly": [1, 0, 1]}, "<") == "無解"
    assert sol({"poly": [-1, 0, 4]}, ">=") == "-2<=x<=2"


def test_double_root_changes_no_sign_and_odd_root_does():
    sol = lambda factors, rel: _matrix("solve_polynomial_inequality", {"items": [{"left": {"coef": 1, "factors": factors}, "rel": rel}]})["answer"]["items"][0]["solution"]["canonical"]  # noqa: E731
    f = [{"lin": [1, -1]}, {"lin": [1, -3], "mult": 2}, {"lin": [1, -5]}]
    assert sol(f, ">") == "x<1 or x>5"            # no sign change at the double root 3 (and 3 itself is excluded? f(3)=0 so it is not > 0)
    assert sol(f, "<") == "1<x<3 or 3<x<5"
    assert sol(f, ">=") == "x<=1 or x=3 or x>=5"
    assert sol(f, "<=") == "1<=x<=5"


def test_revision_two_refusals_and_answers():
    with pytest.raises(ValueError):  # a first factor that has real roots would add sign changes of its own
        _matrix("polynomial_inequality_parameters", {"items": [{"kind": "quad_factor_param", "pos": [1, 0, -1], "roots": [-1, 3], "rel": "<=", "shape": "between"}]})
    with pytest.raises(ValueError):  # <= with a "between" solution is fine, >= with it is not
        _matrix("polynomial_inequality_parameters", {"items": [{"kind": "quad_factor_param", "pos": [1, 0, 1], "roots": [-1, 3], "rel": ">=", "shape": "between"}]})
    with pytest.raises(ValueError):  # not a right triangle
        _matrix("polynomial_applications", {"items": [{"kind": "tent_prism", "triple": [3, 4, 6], "L": 168, "V": 1728}]})
    rec = _matrix("polynomial_applications", {"items": [{"kind": "projectile_ceiling", "T": 6, "H": 18}]})["answer"]["items"][0]
    assert rec["solution"]["canonical"] == "0<k<2"  # the peak k*T^2/4 = 9k stays below 18 only for k < 2
