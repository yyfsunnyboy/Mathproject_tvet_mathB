"""Domain gate for analytic_geometry.circle_line_relations: hand-derived oracles (textbook worked solutions),
independent validators that reject tampered answers, and refusal of degenerate inputs."""

from __future__ import annotations

import copy

import pytest

from agent_domains_candidate.analytic_geometry_circle_lines import circle_line_domain as D


def run(op: str, **givens):
    matrix = D.build_circle_line_relations_matrix(domain_operation=op, constraints=givens)
    validator = getattr(D, f"validate_{op}_matrix")
    assert validator(matrix), "validator rejects the canonical answer"
    return matrix


def vals(matrix):
    out = []
    for v in matrix["answer"]["values"]:
        out.append(v.get("text") or v.get("canonical") or v.get("values"))
    return out


# --- hand-derived source oracles ---------------------------------------------------------------------------------

def test_classify_relations_and_common_points():
    m = run("classify_circle_line_relations", circle={"center": [0, 0], "r2": 5}, lines=[[1, -1, 1]], ask_points=True)
    item = m["answer"]["lines"][0]
    assert item["relation"] == "secant" and [p["text"] for p in item["points"]] == ["(-2,-1)", "(1,2)"]
    m = run("classify_circle_line_relations", circle={"center": [1, -2], "r2": 9}, lines=[[12, 5, 11], [4, -3, 5]])
    assert [i["relation"] for i in m["answer"]["lines"]] == ["secant", "tangent"]
    m = run("classify_circle_line_relations", circle={"center": [0, 1], "r2": 8}, lines=[[1, 1, -5], [1, 1, -6]], ask_points=True)
    assert [i["relation"] for i in m["answer"]["lines"]] == ["tangent", "disjoint"]
    assert [p["text"] for p in m["answer"]["lines"][0]["points"]] == ["(2,3)"]
    m = run("classify_circle_line_relations", circle={"center": [-1, 0], "r2": 20}, lines=[[3, 1, -7]], ask_points=True)
    assert [p["text"] for p in m["answer"]["lines"][0]["points"]] == ["(1,4)", "(3,-2)"]
    assert run("classify_circle_line_relations", circle={"center": [2, 3], "r2": 16}, lines=[[3, 4, 7]])["answer"]["lines"][0]["relation"] == "disjoint"
    assert run("classify_circle_line_relations", circle={"center": [1, -2], "r2": 13}, lines=[[2, 3, -10]])["answer"]["lines"][0]["relation"] == "disjoint"


def test_parameter_conditions():
    tangent = [{"condition": "tangent", "output": "set"}]
    assert vals(run("solve_circle_line_parameter", circle={"d": 1, "e": [0, 1], "f": 2}, line={"a": 1, "b": -1, "c": 0}, asks=tangent)) == [["-5", "3"]]
    m = run("solve_circle_line_parameter", circle={"center": [1, 2], "r2": 9}, line={"a": 3, "b": 4, "c": [0, 1]},
            asks=[{"condition": "tangent", "output": "set"}, {"condition": "tangent", "output": "lines"}, {"condition": "secant", "output": "region"}])
    assert vals(m) == [["-26", "4"], "3x+4y-26=0, 3x+4y+4=0", "-26<k<4"]
    assert vals(run("solve_circle_line_parameter", circle={"d": 2, "e": 0, "f": [0, 1]}, line={"a": 1, "b": 1, "c": 0},
                    asks=[{"condition": "disjoint", "output": "region"}])) == ["1/2<k<1"]
    assert vals(run("solve_circle_line_parameter", circle={"d": 0, "e": -4, "f": [0, 1]}, line={"a": 1, "b": -2, "c": 0},
                    asks=[{"condition": "intersect", "output": "region"}])) == ["k<=4/5"]
    assert vals(run("solve_circle_line_parameter", circle={"center": [-1, 2], "r2": 169}, line={"a": 3, "b": 4, "c": [0, 1]},
                    asks=[{"condition": "chord", "chord": 24, "output": "set"}])) == [["-30", "20"]]
    assert vals(run("solve_circle_line_parameter", circle={"d": 2, "e": 0, "f": [0, 1]}, line={"a": 15, "b": -8, "c": -2},
                    asks=[{"condition": "chord", "chord": 4, "output": "set"}])) == [["-4"]]
    assert vals(run("solve_circle_line_parameter", circle={"center": [-1, 0], "r2": 2}, line={"a": [0, 1], "b": -1, "c": -3},
                    asks=tangent, param="m")) == [["-1", "7"]]
    assert vals(run("solve_circle_line_parameter", circle={"center": [0, 2], "r2": 4}, line={"a": 1, "b": -1, "c": [0, 1]},
                    asks=[{"condition": "quarter_arcs", "output": "ordered"}], param="m")) == [["4", "0"]]


def test_tangent_lines():
    def lines(**g):
        return vals(run("write_circle_tangent_lines", **g))[0]

    assert lines(circle={"center": [-1, 2], "r2": 25}, kind="through_point", point=[3, 5]) == "4x+3y-27=0"
    assert lines(circle={"center": [2, -1], "r2": 10}, kind="through_point", point=[3, -4]) == "x-3y-15=0"
    assert lines(circle={"center": [1, 2], "r2": 8}, kind="through_point", point=[5, 2]) == "x+y-7=0, x-y-3=0"
    assert lines(circle={"center": [0, 0], "r2": 4}, kind="through_point", point=[2, 6]) == "x-2=0, 4x-3y+10=0"
    assert lines(circle={"d": 6, "e": 0, "f": 4}, kind="through_point", point=[2, 0]) == "x+2y-2=0, x-2y-2=0"
    assert lines(circle={"center": [-1, 0], "r2": 1}, kind="through_point", point=[0, 2]) == "x=0, 3x-4y+8=0"
    assert lines(circle={"center": [1, 2], "r2": 1}, kind="through_point", point=[6, 3]) == "y-3=0, 5x-12y+6=0"
    assert lines(circle={"center": [3, -4], "r2": 10}, kind="with_slope", slope=3) == "3x-y-23=0, 3x-y-3=0"
    assert lines(circle={"d": 0, "e": 2, "f": -12}, kind="parallel_to", parallel_to=[2, 3, 0]) == "2x+3y-10=0, 2x+3y+16=0"
    m = run("write_circle_tangent_lines", circle={"center": [-1, 0], "r2": 1}, kind="through_point", point=[0, 2])
    assert m["answer"]["values"][0]["lines"] == [[1, 0, 0], [3, -4, 8]]


def test_chords_distances_and_tangent_point_circle():
    assert vals(run("solve_chord_and_distance", circle={"center": [2, 3], "r2": 25}, line=[3, -4, 21], asks=["chord"])) == ["8"]
    assert vals(run("solve_chord_and_distance", circle={"center": [0, 3], "r2": 5}, line=[5, -12, -3],
                    asks=["max_distance", "min_distance"])) == ["3+sqrt(5)", "3-sqrt(5)"]
    assert vals(run("solve_chord_and_distance", circle={"center": [1, 2], "r2": 9}, point=[2, 4],
                    asks=["shortest_chord", "shortest_chord_line"])) == ["4", "x+2y-10=0"]
    assert vals(run("solve_circle_from_tangent_point", d=-4, point=[-1, 3], tangent=[3, -4, 15])) == ["2", "-20"]


def test_statements():
    def truth(**s):
        return run("evaluate_circle_line_statement_truth", statement=s)["answer"]["truth"]

    assert truth(kind="line_through_point_on_circle_is_tangent") is False
    assert truth(kind="disjoint_distance_bound", r2=25, bound=5) is True
    assert truth(kind="disjoint_distance_bound", r2=25, bound=6) is False
    assert truth(kind="tangent_to_both_axes", center=[2, -2], r2=4) is True
    assert truth(kind="tangent_to_both_axes", center=[3, -2], r2=4) is False
    assert truth(kind="tangent_slope_exists", slope=100) is True
    assert truth(kind="two_tangents_through_point", center=[0, 0], r2=1, point=[1, 3]) is True
    assert truth(kind="two_tangents_through_point", center=[0, 0], r2=1, point=[1, 0]) is False


def test_tangent_scenarios():
    assert vals(run("solve_circle_tangent_scenarios", scenario="building_view", center_y=6, point=[6, 10])) == ["-3/2", "3x+2y-38=0", "(38/3,0)"]
    assert vals(run("solve_circle_tangent_scenarios", scenario="building_dimensions", center_y=6, point=[6, 10])) == [
        "2*sqrt(13)", "x^2+(y-6)^2=52", "8"]
    assert vals(run("solve_circle_tangent_scenarios", scenario="light_shadow", circle={"center": [0, 3], "r2": 5}, light=[1, 6])) == ["15"]
    assert vals(run("solve_circle_tangent_scenarios", scenario="badge", width=4, r2=2, center_height=3, od=1)) == ["3", "7"]


# --- validators reject tampered answers ----------------------------------------------------------------------------

TAMPER = [
    ("classify_circle_line_relations", {"circle": {"center": [1, -2], "r2": 9}, "lines": [[12, 5, 11], [4, -3, 5]]},
     lambda a: a["lines"][1].update(relation="secant")),
    ("classify_circle_line_relations", {"circle": {"center": [0, 0], "r2": 5}, "lines": [[1, -1, 1]], "ask_points": True},
     lambda a: a["lines"][0]["points"][0].update(point=["-2", "1"])),
    ("solve_circle_line_parameter", {"circle": {"d": 1, "e": [0, 1], "f": 2}, "line": {"a": 1, "b": -1, "c": 0},
                                     "asks": [{"condition": "tangent", "output": "set"}]},
     lambda a: a["values"][0].update(values=["-5", "4"])),
    ("solve_circle_line_parameter", {"circle": {"d": 2, "e": 0, "f": [0, 1]}, "line": {"a": 1, "b": 1, "c": 0},
                                     "asks": [{"condition": "disjoint", "output": "region"}]},
     lambda a: a["values"][0].update(segments=[["1/2", "1", True, False]])),
    ("write_circle_tangent_lines", {"circle": {"center": [0, 0], "r2": 4}, "kind": "through_point", "point": [2, 6]},
     lambda a: a["values"][0].update(lines=[[4, -3, 10]])),
    ("solve_chord_and_distance", {"circle": {"center": [0, 3], "r2": 5}, "line": [5, -12, -3], "asks": ["max_distance", "min_distance"]},
     lambda a: a["values"][1].update(canonical="-3+sqrt(5)")),
    ("solve_circle_from_tangent_point", {"d": -4, "point": [-1, 3], "tangent": [3, -4, 15]},
     lambda a: a["values"][1].update(canonical="-19")),
    ("evaluate_circle_line_statement_truth", {"statement": {"kind": "tangent_to_both_axes", "center": [3, -2], "r2": 4}},
     lambda a: a.update(truth=True)),
    ("solve_circle_tangent_scenarios", {"scenario": "badge", "width": 4, "r2": 2, "center_height": 3, "od": 1},
     lambda a: a["values"][1].update(canonical="8")),
    ("solve_circle_tangent_scenarios", {"scenario": "light_shadow", "circle": {"center": [0, 3], "r2": 5}, "light": [1, 6]},
     lambda a: a["values"][0].update(canonical="14")),
]


@pytest.mark.parametrize(("op", "givens", "tamper"), TAMPER)
def test_validators_reject_tampered_answers(op, givens, tamper):
    matrix = run(op, **givens)
    bad = copy.deepcopy(matrix)
    tamper(bad["answer"])
    assert not getattr(D, f"validate_{op}_matrix")(bad)


# --- degenerate inputs are refused -----------------------------------------------------------------------------------

DEGENERATE = [
    ("classify_circle_line_relations", {"circle": {"center": [0, 0], "r2": 0}, "lines": [[1, 1, 0]]}),
    ("classify_circle_line_relations", {"circle": {"center": [0, 0], "r2": 4}, "lines": [[1, 0, 0], [0, 1, 0]]}),  # same relation twice
    ("classify_circle_line_relations", {"circle": {"center": [0, 0], "r2": 2}, "lines": [[1, 2, 0]], "ask_points": True}),  # irrational points
    ("solve_circle_line_parameter", {"circle": {"center": [0, 0], "r2": [0, 1]}, "line": {"a": 1, "b": 0, "c": -1},
                                     "asks": [{"condition": "tangent", "output": "ordered"}]}),  # one root, two names
    ("solve_circle_line_parameter", {"circle": {"center": [0, 0], "r2": 3}, "line": {"a": 1, "b": 1, "c": [0, 1]},
                                     "asks": [{"condition": "tangent", "output": "set"}]}),  # irrational boundary
    ("write_circle_tangent_lines", {"circle": {"center": [0, 0], "r2": 25}, "kind": "through_point", "point": [1, 1]}),
    ("write_circle_tangent_lines", {"circle": {"center": [0, 0], "r2": 4}, "kind": "parallel_to", "parallel_to": [1, 0, -2]}),
    ("solve_chord_and_distance", {"circle": {"center": [0, 0], "r2": 4}, "line": [1, 0, -5], "asks": ["chord"]}),
    ("solve_chord_and_distance", {"circle": {"center": [0, 0], "r2": 4}, "line": [1, 0, -1], "asks": ["max_distance"]}),
    ("solve_chord_and_distance", {"circle": {"center": [0, 0], "r2": 4}, "point": [0, 0], "asks": ["shortest_chord"]}),
    ("solve_circle_from_tangent_point", {"d": -4, "point": [0, 0], "tangent": [3, -4, 15]}),
    ("solve_circle_tangent_scenarios", {"scenario": "building_view", "center_y": 6, "point": [6, 4]}),
    ("solve_circle_tangent_scenarios", {"scenario": "light_shadow", "circle": {"center": [0, 1], "r2": 4}, "light": [1, 6]}),
    ("solve_circle_tangent_scenarios", {"scenario": "badge", "width": 4, "r2": 5, "center_height": 3, "od": 1}),
]


@pytest.mark.parametrize(("op", "givens"), DEGENERATE)
def test_degenerate_inputs_are_refused(op, givens):
    with pytest.raises(ValueError):
        D.build_circle_line_relations_matrix(domain_operation=op, constraints=givens)


def test_validators_never_raise_on_garbage():
    for op in D.OPERATIONS:
        assert getattr(D, f"validate_{op}_matrix")({"domain": D.DOMAIN_KEY, "domain_operation": op}) is False
