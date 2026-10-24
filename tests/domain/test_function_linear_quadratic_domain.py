"""Domain gate for function.linear_quadratic (revision_0001): exact operations, independent validators and refusals."""

from __future__ import annotations

import pytest

from agent_domains_candidate.function_linear_quadratic import function_models_domain as D


def run(op: str, **givens):
    matrix = D.build_function_models_matrix(domain_operation=op, constraints=givens)
    assert getattr(D, f"validate_{op}_matrix")(matrix), (op, matrix["answer"])
    return matrix["answer"]


def test_linear_functions_textbook_examples():
    a = run("solve_linear_functions", items=[{"kind": "two_points", "p1": [2, 1], "p2": [4, 5], "dx": 3}])["items"][0]
    assert a["f"]["plain"] == "2x-3" and a["delta"]["canonical"] == "6"
    assert run("solve_linear_functions", items=[{"kind": "value_at", "p1": ["1.23", 2], "p2": ["9.71", 18], "x": "3.35"}])["items"][0]["value"]["canonical"] == "6"
    assert run("solve_linear_functions", items=[{"kind": "value_at", "p1": [{"pow": [3, 8]}, 2], "p2": [{"pow": [3, 10]}, 7], "x": {"pow": [3, 9]}}])["items"][0]["value"]["canonical"] == "13/4"
    x = run("solve_linear_functions", items=[{"kind": "solve_x", "p1": [{"sqrt": 2}, 2], "p2": [{"sqrt": 5}, 5], "y": 3}])["items"][0]["x"]
    assert abs(float(__import__("sympy").N(__import__("sympy").sympify(x["canonical_text"]))) - (2 * 2 ** 0.5 + 5 ** 0.5) / 3) < 1e-12


def test_statement_truth_values():
    sub = {"type": "linear_points", "p1": [1, -2], "p2": [2, -5]}
    a = run("evaluate_function_statements", subject=sub, statements=[{"kind": "value_is", "x": 3, "value": 8}, {"kind": "intercept_is", "value": 1},
                                                                      {"kind": "slope_is_quotient", "xa": 9, "xb": 7}, {"kind": "rate_is", "dx": 1, "dy": 3}])
    assert a["selected"] == [2, 3]
    para = {"type": "parabola", "a": -1, "root1": -2, "root2": "1/2"}
    a = run("evaluate_function_statements", subject=para, statements=[{"kind": "negative_quantity", "expr": e} for e in ("a", "b", "c", "D", "a-b+c")])
    assert a["selected"] == [1, 2] and a["abc"] == ["-1", "-3/2", "1"]
    for statement, truth in (({"kind": "linear_slope_claim", "a": 2, "claimed": 3}, False),
                             ({"kind": "translation_claim", "a": 2, "direction": "left", "amount": 1, "claim_h": 1, "claim_k": 0}, False),
                             ({"kind": "axis_claim", "p": 2, "q": 1, "p2": 1, "q2": 1}, False),
                             ({"kind": "interval_max_claim", "a": -1, "h": 1, "k": 5, "lo": 2, "hi": 4, "claim_x": 4}, False),
                             ({"kind": "intercept_claim", "always": "x"}, False)):
        assert run("evaluate_function_statements", subject={"type": "generic"}, statements=[statement], mode="truth")["truths"] == [truth]


def test_vertex_form_extrema_and_transformations():
    a = run("complete_square_items", items=[{"coeffs": [-2, -3, 1]}])["items"][0]
    assert (a["a"]["canonical"], a["h"]["canonical"], a["k"]["canonical"]) == ("-2", "-3/4", "17/8")
    assert run("quadratic_vertex_axis", coeffs=[3, 18, 29])["vertex"]["text"] == "(-3,2)"
    e = run("quadratic_extrema", items=[{"f": [2, -4, -1], "interval": [-1, 2], "asks": ["max_value", "min_value", "min_x"]}])["items"][0]["values"]
    assert [v["canonical"] for v in e] == ["5", "-3", "1"]
    t = run("quadratic_graph_transformations", items=[{"kind": "find_translation", "f": [4, -8, 0], "g": [4, 8, 9]}])["items"][0]
    assert (t["left"]["canonical"], t["up"]["canonical"]) == ("2", "9")


def test_always_sign_regions():
    assert run("quadratic_always_sign", a=1, b=-6, c={"k": 1}, sign="positive")["region"]["text"] == "k>9"
    assert run("quadratic_always_sign", a=-2, b=8, c={"k": 1, "c": -3}, sign="negative")["region"]["text"] == "k<-5"
    assert run("quadratic_always_sign", a={"k": 1}, b=2, c=-1, sign="negative")["region"]["text"] == "k<-1"


def test_application_models():
    items = [{"kind": "tile_cost", "side": 4, "costs": [30, 20, 10]}, {"kind": "circle_areas", "diameter": 6}, {"kind": "fenced_pens", "pens": 3, "fence": 48},
             {"kind": "ball", "a": 5, "b": 20, "height": 15}, {"kind": "basket", "apex_x": "2.5", "apex_y": "3.5", "start_y": "2.25", "hoop_x": 4},
             {"kind": "fountain", "nozzle": 2, "land": 3, "radius": 1}, {"kind": "roots_intercept", "root1": -1, "root2": -9, "y_intercept": 9},
             {"kind": "max_condition", "apex_x": 3, "max_value": 8}]
    out = [run("solve_quadratic_applications", items=[it])["items"][0] for it in items]
    assert out[0]["cost"]["plain"] == "10x^2-20x+240" and out[0]["min"]["canonical"] == "230"
    assert out[1]["min_over_pi"]["canonical"] == "3" and out[2]["max_area"]["canonical"] == "144"
    assert [t["canonical"] for t in out[3]["times"]] == ["1", "3"] and out[4]["hoop_height"]["canonical"] == "61/20"
    assert out[5]["above_nozzle"]["canonical"] == "2/3" and out[6]["f"]["plain"] == "x^2+10x+9" and (out[7]["a"]["canonical"], out[7]["b"]["canonical"]) == ("-1", "6")
    p = run("solve_quadratic_applications", items=[{"kind": "profit", "cost": [5, 2], "revenue": {"mode": "table", "points": [[5, 45], [10, 80]]}}])["items"][0]
    assert (p["a"]["canonical"], p["b"]["canonical"], p["x"]["canonical"], p["max"]["canonical"]) == ("-1/5", "10", "20", "75")


@pytest.mark.parametrize(("op", "givens"), [
    ("solve_linear_functions", {"items": [{"kind": "two_points", "p1": [1, 2], "p2": [3, 2], "dx": 1}]}),              # constant: not linear
    ("solve_linear_functions", {"items": [{"kind": "two_points", "p1": [1, 2], "p2": [1, 5], "dx": 1}]}),              # vertical
    ("complete_square_items", {"items": [{"coeffs": [0, 2, 1]}]}),                                                    # not quadratic
    ("quadratic_extrema", {"items": [{"f": [1, 0, 0], "asks": ["max_value"]}]}),                                       # no maximum on R
    ("quadratic_extrema", {"items": [{"f": [1, 0, 0], "interval": [3, 3], "asks": ["max_value"]}]}),                   # empty interval
    ("quadratic_always_sign", {"a": {"k": 1}, "b": 0, "c": {"k": 1}, "sign": "positive"}),                           # parameter in a and c
    ("quadratic_always_sign", {"a": 1, "b": 0, "c": 1, "sign": "positive"}),                                          # unbounded
    ("solve_quadratic_applications", {"items": [{"kind": "tile_cost", "side": 4, "costs": [10, 20, 40]}]}),            # minimum leaves (0, side)
    ("solve_quadratic_applications", {"items": [{"kind": "fountain", "nozzle": 2, "land": 2, "radius": 1}]}),          # disc beyond the landing point
    ("solve_quadratic_applications", {"items": [{"kind": "ball", "a": 5, "b": 20, "height": 25}]}),                    # never reaches that height
    ("solve_quadratic_applications", {"items": [{"kind": "nope"}]}),
])
def test_invalid_inputs_are_refused(op, givens):
    with pytest.raises(ValueError):
        D.build_function_models_matrix(domain_operation=op, constraints=givens)


def test_unknown_operation_missing_givens_and_tampered_answers_are_refused():
    with pytest.raises(ValueError):
        D.build_function_models_matrix(domain_operation="nope", constraints={})
    with pytest.raises(ValueError, match="givens_required"):
        D.build_function_models_matrix(domain_operation="quadratic_vertex_axis", constraints={})
    matrix = D.build_function_models_matrix(domain_operation="quadratic_vertex_axis", constraints={"coeffs": [1, -2, 3]})
    assert D.validate_quadratic_vertex_axis_matrix(matrix)
    matrix["answer"]["vertex"]["y"] = "99"
    assert not D.validate_quadratic_vertex_axis_matrix(matrix)
