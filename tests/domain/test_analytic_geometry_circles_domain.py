"""Domain gate for analytic_geometry.circle_equations: hand-derived oracles (textbook worked solutions),
independent validators that reject tampered answers, and refusal of degenerate inputs."""

from __future__ import annotations

import copy
import json

import pytest

from agent_domains_candidate.analytic_geometry_circles import circle_equations_domain as D
from agent_domains_candidate.analytic_geometry_circles.unit6_specs import COMPONENTS


def run(op: str, **givens):
    matrix = D.build_circle_equations_matrix(domain_operation=op, constraints=givens)
    check = D._OPERATIONS[op][1]
    assert check(matrix["givens"], matrix["answer"]), "validator rejects the canonical answer"
    return matrix


def texts(matrix):
    return [v.get("text") or v.get("canonical") or v.get("point") or v.get("value") or v.get("values") for v in matrix["answer"]["values"]]


# --- hand-derived source oracles ---------------------------------------------------------------------------------

def test_write_circle_equations_textbook_examples():
    m = run("write_circle_equations", items=[
        {"kind": "center_radius", "center": [2, -3], "r2": 16},
        {"kind": "center_point", "center": [2, -3], "point": [5, 1]},
        {"kind": "diameter", "a": [-2, 3], "b": [6, -3]},
        {"kind": "concentric_through", "ref": {"d": 2, "e": -4, "f": -1}, "point": [3, 5]},
        {"kind": "axis_center_through_points", "points": [[1, 4], [0, 3]]},
        {"kind": "axis_center_through_point_radius", "point": [7, 3], "r": 5},
        {"kind": "circumcircle", "a": [5, 10], "b": [6, 9], "c": [-2, 3]},
        {"kind": "perp_bisector", "p": [5, 10], "q": [6, 9]},
        {"kind": "perp_bisector", "p": [6, 9], "q": [-2, 3]},
        {"kind": "origin_circle_k", "x_sqrt": 3, "point": [0, -1]},
        {"kind": "diameter_param_k", "center": [4, 1], "a": [2, 3]},
    ])
    assert texts(m) == [
        "(x-2)^2+(y+3)^2=16", "(x-2)^2+(y+3)^2=25", "(x-2)^2+y^2=25", "(x+1)^2+(y-2)^2=25", "(x-4)^2+y^2=25",
        "(x-3)^2+y^2=25", "(x-11)^2+y^2=25", "(x-2)^2+(y-6)^2=25", "x-y+4=0", "4x+3y-26=0", "4", "8", "(6,-1)",
    ]


def test_analyze_general_circle_textbook_examples():
    m = run("analyze_general_circle", items=[
        {"kind": "center_radius", "d": -2, "e": 6, "f": 6},
        {"kind": "center_radius", "form": "root", "h": 1, "k": 0, "rhs": 2},
        {"kind": "center_radius", "a": 9, "d": -6, "e": 0, "f": -35},
        {"kind": "standard_and_classify", "d": 2, "e": -4, "f": 5},
        {"kind": "standard_and_classify", "d": 2, "e": -4, "f": 10},
        {"kind": "classify", "d": -4, "e": 6, "f": -12},
        {"kind": "classify", "d": -4, "e": 6, "f": 13},
        {"kind": "classify", "d": -4, "e": 6, "f": 17},
        {"kind": "param_range", "d": -4, "e": 2, "f1": 1},
        {"kind": "param_range", "d": 2, "e": 2, "f0": 7, "f1": -1},
        {"kind": "param_from_radius", "d": -4, "e": 2, "f1": 1, "r2": 9},
        {"kind": "param_radius_center", "d": 2, "e1": -2, "f1": 2, "r2": 9},
        {"kind": "coefficients_from_center", "h": 1, "k": -3, "f": -6},
    ])
    assert texts(m) == [
        "(1,-3)", "2", "(1,0)", "2", "(1/3,0)", "2",
        "(x+1)^2+(y-2)^2=0", "point", "(x+1)^2+(y-2)^2=-5", "none",
        "circle", "point", "none", "k<5", "k>5", "-4",
        ["-2", "4"], "(-1,4)", "(-1,-2)", "-2", "6", "4",
    ]


def test_locus_point_circle_and_range_textbook_examples():
    assert texts(run("solve_distance_ratio_locus", a=[0, 0], b=[6, 0], ratio=[2, 1], asks=["equation"])) == ["(x-8)^2+y^2=16"]
    assert texts(run("solve_distance_ratio_locus", a=[0, 0], b=[6, 0], ratio=[1, 2], asks=["equation"])) == ["(x+2)^2+y^2=16"]
    m = run("solve_distance_ratio_locus", a=[0, 0], b=[16, 0], weights=[3, 5], half="upper",
            asks=["ratio_p", "ratio_q", "shape", "center", "radius"])
    assert texts(m) == ["5", "3", "upper_semicircle", "(25,0)", "15"]
    assert texts(run("classify_points_against_circle", circle={"center": [2, -3], "r2": 25}, points=[[6, 0], [-2, -1], [0, 2]])) == ["on", "inside", "outside"]
    assert texts(run("solve_circle_point_distances", circle={"d": 4, "e": -2, "f": 4}, point=[2, 4], asks=["max", "min"])) == ["6", "4"]
    assert texts(run("solve_circle_point_distances", circle={"d": -6, "e": -8, "f": -11}, point=[0, 0], asks=["max", "min"])) == ["11", "1"]
    assert texts(run("solve_circle_point_distances", circle={"center": [0, 2], "r2": 9}, point=[3, -2], asks=["relation", "min"])) == ["outside", "2"]
    assert texts(run("solve_point_position_parameter_range", inside=[[1, -2]], outside=[[-3, 3]])) == ["5<k<18"]


def test_statements_mohr_storm_and_arch():
    truths = [run("evaluate_circle_statement_truth", statement=s)["answer"]["truth"] for s in (
        {"kind": "center_quadrant", "center": [2, -3], "r2": 2, "claimed": 2},
        {"kind": "is_circle", "d": 0, "e": 0, "f": 5},
        {"kind": "may_be_point", "d": -2, "e": 4, "f1": 1},
        {"kind": "origin_inside", "center": [1, 2], "r2": 2},
        {"kind": "area_equals", "r2": 2, "claimed_coef": 2, "with_pi": True},
        {"kind": "area_equals", "r2": 2, "claimed_coef": 2, "with_pi": False},
    )]
    assert truths == [False, False, True, False, True, False]
    m = run("solve_mohr_circles",
            options=[{"d": 0, "e": -6, "f": -16}, {"d": 2, "e": -6, "f": -15}, {"d": 2, "e": 0, "f": -5}, {"d": -2, "e": 0, "f": 5}],
            diameter={"a": [1, 2], "b": [5, -2]}, nested=[{"d": -12, "e": 0, "f": 11}, {"d": -6, "e": 0, "f": 5}, {"d": -16, "e": 0, "f": 55}])
    assert texts(m) == ["3", "(x-3)^2+y^2=8", "12*pi"]
    m = run("solve_storm_entry_time", start_hour=15, distance=460, radius=80, speed=25, options=[18, 23, 30, 35])
    assert m["answer"]["entry_hour"] == "151/5" and texts(m) == ["3"]  # 3pm + 15.2h = 6:12 next day
    assert texts(run("solve_circular_arch_height", width=3, height="9/2", post_offset="3/2")) == ["4"]


# --- validators reject tampering ---------------------------------------------------------------------------------------------

def _tamper(value):
    value = copy.deepcopy(value)
    if value["kind"] in ("equation", "line"):
        value["text"] = value["text"].replace("=", "+1=", 1) if value["kind"] == "equation" else "x+y+9=0"
        if value["kind"] == "line":
            value["line"] = [1, 1, 9]
    elif value["kind"] == "point":
        value["point"] = [str(int(value["point"][0].split("/")[0]) + 1) if "/" not in value["point"][0] else "99", value["point"][1]]
    elif value["kind"] in ("rational", "radical"):
        value["canonical"] = "12345"
        value["coef"], value["radicand"] = "12345", 1
    elif value["kind"] == "choice":
        value["value"] = "zzz"
    elif value["kind"] == "relation":
        value["text"] = "k<12345" if value["text"].startswith("k<") else "12345<k<54321"
    elif value["kind"] == "set":
        value["values"] = ["12345", "54321"]
    elif value["kind"] == "pi_multiple":
        value["canonical"] = "12345*pi"
    return value


@pytest.mark.parametrize("cid", sorted(COMPONENTS))
def test_validator_rejects_a_tampered_answer_for_every_source_component(cid):
    _skill, op, source, _sampler = COMPONENTS[cid]
    matrix = D.build_circle_equations_matrix(domain_operation=op, constraints=dict(source))
    validate = getattr(D, f"validate_{op}_matrix")
    assert validate(matrix) is True
    answer = matrix["answer"]
    if "values" in answer:
        for i in range(len(answer["values"])):
            broken = copy.deepcopy(matrix)
            broken["answer"]["values"][i] = _tamper(answer["values"][i])
            assert validate(broken) is False, (cid, i)
    elif "truth" in answer:
        broken = copy.deepcopy(matrix)
        broken["answer"]["truth"] = not answer["truth"]
        assert validate(broken) is False
    else:
        pytest.fail("unknown answer shape")


def test_validator_never_raises_on_garbage():
    validate = D.validate_write_circle_equations_matrix
    for junk in (None, {}, {"domain": D.DOMAIN_KEY}, {"domain": D.DOMAIN_KEY, "domain_operation": "write_circle_equations",
                                                       "validation_facts": {"domain_operation": "write_circle_equations"},
                                                       "givens": {"items": [{"kind": "diameter"}]}, "answer": {"values": []}}):
        assert validate(junk) is False


# --- degenerate inputs are refused -----------------------------------------------------------------------------------------------

@pytest.mark.parametrize(("op", "givens"), [
    ("write_circle_equations", {"items": [{"kind": "diameter", "a": [1, 1], "b": [1, 1]}]}),
    ("write_circle_equations", {"items": [{"kind": "center_point", "center": [1, 1], "point": [1, 1]}]}),
    ("write_circle_equations", {"items": [{"kind": "axis_center_through_points", "points": [[1, 2], [1, 5]]}]}),
    ("write_circle_equations", {"items": [{"kind": "axis_center_through_point_radius", "point": [0, 5], "r": 5}]}),
    ("write_circle_equations", {"items": [{"kind": "circumcircle", "a": [0, 0], "b": [1, 1], "c": [2, 2]}]}),
    ("analyze_general_circle", {"items": [{"kind": "center_radius", "d": 0, "e": 0, "f": 3}]}),
    ("analyze_general_circle", {"items": [{"kind": "param_range", "d": 2, "e": 2, "f1": 0}]}),
    ("analyze_general_circle", {"items": [{"kind": "param_radius_center", "d": 2, "e1": -2, "f1": 2, "r2": 10}]}),
    ("solve_distance_ratio_locus", {"a": [0, 0], "b": [6, 0], "ratio": [1, 1], "asks": ["equation"]}),
    ("solve_circle_point_distances", {"circle": {"center": [0, 0], "r2": 2}, "point": [3, 4], "asks": ["max"]}),
    ("solve_point_position_parameter_range", {"inside": [[3, 3]], "outside": [[1, 1]]}),
    ("evaluate_circle_statement_truth", {"statement": {"kind": "origin_inside", "center": [3, 4], "r2": 25}}),
    ("solve_storm_entry_time", {"start_hour": 15, "distance": 60, "radius": 80, "speed": 25, "options": [18, 23, 30, 35]}),
    ("solve_storm_entry_time", {"start_hour": 15, "distance": 460, "radius": 80, "speed": 25, "options": [29, 30, 31, 35]}),
    ("solve_circular_arch_height", {"width": 3, "height": "1", "post_offset": "3/2"}),
])
def test_degenerate_inputs_are_refused(op, givens):
    with pytest.raises(ValueError):
        D.build_circle_equations_matrix(domain_operation=op, constraints=givens)


def test_every_component_variant_is_deterministic_json():
    for cid, (_s, op, source, sampler) in COMPONENTS.items():
        import random

        a = sampler(random.Random(f"x:{cid}"))
        b = sampler(random.Random(f"x:{cid}"))
        assert a == b
        json.dumps(a)  # plain JSON givens (no Fraction objects)
        D.build_circle_equations_matrix(domain_operation=op, constraints=a)
