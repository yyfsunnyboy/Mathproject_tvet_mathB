"""analytic_geometry.line_equations: oracle answers are the textbook's own worked solutions (PDF pp.3-30,
DB ``detailed_solution``) or hand calculations written out in the comments, never the domain output."""
from __future__ import annotations

import random

import pytest

from agent_domains_candidate.analytic_geometry_lines import line_equations_domain as D
from agent_domains_candidate.analytic_geometry_lines import line_geometry as G
from agent_domains_candidate.analytic_geometry_lines.unit5_specs import COMPONENTS


def run(op, **givens):
    matrix = D.build_line_equations_matrix(domain_operation=op, constraints=givens)
    assert getattr(D, f"validate_{op}_matrix")(matrix), op
    return matrix["answer"]


def texts(answer):
    return [v["text"] for v in answer["values"]]


# --- textbook examples (solutions printed in the book) ---------------------------------------------------

def test_example1_slopes_and_order():
    pivot = [1, 1]
    lines = [{"index": i, "p": pivot, "q": q} for i, q in enumerate([[2, 2], [3, 2], [3, 1], [3, 0], [2, 0]], 1)]
    a = run("rank_line_slopes", lines=lines)
    assert [r["slope"] for r in a["slopes"]] == ["1", "1/2", "0", "-1/2", "-1"]
    assert a["order_text"] == "m1>m2>m3>m4>m5"


def test_example2_example3_example4_equations_and_slope():
    a = run("solve_line_equations", items=[
        {"kind": "point_slope", "p": [-2, 1], "m": "-3"}, {"kind": "two_points", "p": [1, 2], "q": [4, 1]}])
    assert texts(a) == ["3x+y+5=0", "x+3y-7=0"]                       # 例題2
    a = run("solve_line_equations", items=[{"kind": "slope_y_intercept", "m": "-2", "b": 3}, {"kind": "intercepts", "a": 4, "b": -3}])
    assert texts(a) == ["2x+y-3=0", "3x-4y-12=0"]                     # 例題3
    assert run("slope_of_line_from_equation", line=[3, -2, -5])["values"][0]["canonical"] == "3/2"   # 例題4


def test_example5_translation_and_practice_inverse():
    assert texts(run("translate_line_equation", line=[2, 3, 6], dx=-1, dy=2)) == ["2x+3y+2=0"]        # 例題5
    # 隨堂練習: result 3x-4y=0 after (+3,-2); original: 3(x-3)... hand: L: 3(x+3)... -> 3x-4y+17=0
    assert texts(run("translate_line_equation", line=[3, -4, 0], dx=3, dy=-2, direction="inverse")) == ["3x-4y+17=0"]


def test_example6_parallel_and_perpendicular():
    a = run("solve_line_equations", items=[
        {"kind": "parallel_through", "p": [3, 1], "line": [1, 2, 4]}, {"kind": "perpendicular_through", "p": [3, 1], "line": [1, 2, 4]}])
    assert texts(a) == ["x+2y-5=0", "2x-y-5=0"]


def test_example7_perpendicular_bisectors_and_station():
    a = run("solve_line_constructions", items=[
        {"kind": "perp_bisector", "p": [5, 7], "q": [1, 1]}, {"kind": "perp_bisector", "p": [1, 1], "q": [7, 1]},
        {"kind": "intersect_items", "a": 0, "b": 1}])
    assert [v.get("text") for v in a["values"]] == ["2x+3y-18=0", "x-4=0", "(4,10/3)"]


def test_example8_and_practice_reflection():
    assert run("solve_line_constructions", items=[{"kind": "reflect_point", "p": [3, 1], "line": [1, -1, 0]}])["values"][0]["text"] == "(1,3)"
    # 隨堂練習: point (2,4) about x+y=0 -> (-y,-x) = (-4,-2)  (book's rule (3) family)
    assert run("solve_line_constructions", items=[{"kind": "reflect_point", "p": [2, 4], "line": [1, 1, 0]}])["values"][0]["text"] == "(-4,-2)"


def test_examples9_10_distances():
    assert run("compute_line_distances", items=[{"kind": "point_to_line", "p": [3, 1], "line": [3, -4, 5]}])["values"][0]["canonical"] == "2"
    assert run("compute_line_distances", items=[{"kind": "parallel_lines", "l1": [3, 4, 11], "l2": [6, 8, -9]}])["values"][0]["canonical"] == "31/10"


def test_example11_window():
    a = run("solve_window_decorative_lines", width=34, height=44, edge_point=[34, 5], delta_c=6, asks=["l1_equation", "l2_equation"])
    assert texts(a) == ["x+y-39=0", "x+y-33=0"]
    assert a["spacing"]["canonical"] == "3*sqrt(2)"


def test_example14_triangle_region():
    a = run("solve_triangle_region_system", vertices={"A": [3, 0], "B": [1, 4], "C": [0, 1]},
            choice_points=[{"point": [3, 0]}, {"point": [1, 4]}, {"point": [0, 1]}, {"point": [0, 0]}, {"point": [1, 1]}], family_point=[0, 1])
    assert a["inequality_texts"] == ["2x+y-6≤0", "3x-y+1≥0", "x+3y-3≥0"]
    assert a["fixed_point_choice"] == 2 and a["m"]["canonical"] == "1/2"


# --- practice / exercises: hand calculations ---------------------------------------------------------------

def test_slope_signs_practice():
    # m1=AB=(0-2)/(4-1)=-2/3, m2=BC=3/1=3, m3=AC=(3-2)/(5-1)=1/4 -> m2>0 and m1+m2+m3>0 only
    a = run("evaluate_slope_sign_statements", points={"A": [1, 2], "B": [4, 0], "C": [5, 3]},
            segments=[["A", "B"], ["B", "C"], ["A", "C"]],
            statements=[{"kind": "sign", "index": 1, "op": ">"}, {"kind": "sign", "index": 2, "op": ">"}, {"kind": "product", "op": ">"},
                        {"kind": "sum", "op": ">"}, {"kind": "chain", "order": [3, 2, 1]}])
    assert a["selected"] == [2, 4]


def test_table_fill_practice():
    # 2x+y-4=0: m=-2, x-int 2, y-int 4 | m=3,y-int -2: 3x-y-2=0, x-int 2/3 | m=-2,x-int 3: 2x+y-6=0, y-int 6
    a = run("fill_line_property_table", rows=[{"given": "equation", "line": [2, 1, -4]},
            {"given": "slope_y_intercept", "m": "3", "b": -2}, {"given": "slope_x_intercept", "m": "-2", "a": 3}])
    assert [(r["equation"], r["slope"], r["x_intercept"], r["y_intercept"]) for r in a["rows"]] == [
        ("2x+y-4=0", "-2", "2", "4"), ("3x-y-2=0", "3", "2/3", "-2"), ("2x+y-6=0", "-2", "3", "6")]


def test_supermarket_practice():
    # SA slope (3-1)/(9+1)=1/5 -> x-5y+6=0 ; midpoint AB (6,5), AB slope 4/-6=-2/3 -> perp slope 3/2: 3x-2y-8=0 ; x-5y+6=0 & 3x-2y-8=0 -> (4,2)
    a = run("solve_line_constructions", items=[
        {"kind": "line_through", "p": [-1, 1], "q": [9, 3]}, {"kind": "perp_bisector", "p": [9, 3], "q": [3, 7]},
        {"kind": "intersect_items", "a": 0, "b": 1}])
    assert [v["text"] for v in a["values"]] == ["x-5y+6=0", "3x-2y-8=0", "(4,2)"]


def test_parameters_practice_and_exercise():
    # AB slope 2/3 so L slope -3/2 = -a -> a=3/2 ; A on L: 3+1+c=0 -> c=-4
    a = run("solve_line_parameters", unknowns=["a", "c"], lines={"L": ["a", "1", "c"]},
            conditions=[{"kind": "on_line", "point": [2, 1], "line": "L"}, {"kind": "perpendicular_to_segment", "p": [2, 1], "q": [5, 3], "line": "L"}],
            targets=[{"name": "a", "expr": "a"}, {"name": "c", "expr": "c"}])
    assert [t["values"] for t in a["targets"]] == [["3/2"], ["-4"]]
    # (3,2) on L1: 3a+6=12 -> a=2, slope -2/3; L2 slope 3/2 = -6/b -> b=-4; (3,2) on L2: 18-8=c=10; a+b+c=8
    a = run("solve_line_parameters", unknowns=["a", "b", "c"], lines={"L1": ["a", "3", "-12"], "L2": ["6", "b", "-c"]},
            conditions=[{"kind": "on_line", "point": [3, 2], "line": "L1"}, {"kind": "on_line", "point": [3, 2], "line": "L2"},
                        {"kind": "perpendicular", "l1": "L1", "l2": "L2"}], targets=[{"name": "s", "expr": "a+b+c"}])
    assert a["targets"][0]["values"] == ["8"]
    # |12(-2)-5(1)+k|/13=2 -> |k-29|=26 -> k=3 or 55
    a = run("solve_line_parameters", unknowns=["k"], lines={"L": ["12", "-5", "k"]},
            conditions=[{"kind": "point_line_distance", "point": [-2, 1], "line": "L", "distance": "2"}], targets=[{"name": "k", "expr": "k"}])
    assert a["targets"][0]["values"] == ["3", "55"]


def test_distance_with_fractional_form_and_window_metrics():
    # L2: x/2-y=1 -> x-2y-2=0 ; |3-(-2)|/sqrt(5)=sqrt(5)
    a = run("compute_line_distances", items=[{"kind": "parallel_lines", "l1": [1, -2, 3], "l2": ["1/2", "-1", "-1"]}])
    assert a["values"][0]["canonical"] == "sqrt(5)"
    # origin to x+y-39=0 : 39/sqrt2 = 39sqrt2/2 ; lines x+y=39+6t strictly inside 0<x+y<78 : t=-6..6 -> 13
    a = run("solve_window_decorative_lines", width=34, height=44, edge_point=[34, 5], delta_c=6, asks=["distance_origin_l1", "line_count"])
    assert a["values"][0]["canonical"] == "39*sqrt(2)/2" and a["values"][1]["canonical"] == "13"


def test_centers_of_triangle_exercise():
    # right angle at B (BA.BC = 8*(-2)+(-4)(-4) = 0): circumcentre = midpoint of AC = (2,1), orthocentre = B = (7,1)
    a = run("solve_line_constructions", items=[{"kind": "circumcenter", "pts": [[-1, 5], [7, 1], [5, -3]]},
                                               {"kind": "orthocenter", "pts": [[-1, 5], [7, 1], [5, -3]]}])
    assert [v["text"] for v in a["values"]] == ["(2,1)", "(7,1)"]


def test_shortest_path_exercise():
    # reflect A(2,3) in the x-axis: A'(2,-3); A'B slope 12/4=3 meets y=0 at x=3 ; |A'B|=sqrt(16+144)=4sqrt10
    a = run("solve_line_constructions", items=[{"kind": "shortest_path_point_on_axis", "a": [2, 3], "b": [6, 9]},
                                               {"kind": "shortest_path_length", "a": [2, 3], "b": [6, 9]}])
    assert a["values"][0]["text"] == "(3,0)" and a["values"][1]["canonical"] == "4*sqrt(10)"


def test_rectangle_diagonals_exercise():
    # B(0,0) D(2+a,2) C(2+a,0) E(2,2): slope BD * slope CE = 2/(2+a) * (-2/a) = -1 -> a^2+2a-4=0 -> a=-1+sqrt5
    assert run("solve_rectangle_perpendicular_diagonals", ab=2, bf=2)["values"][0]["canonical"] == "-1+sqrt(5)"


def test_axis_triangle_area_exercise():
    # x/a+y/b=1 through (4,1), |ab|=2 -> (a,b)=(-4,1/2) or (2,-1)  -> x-8y+4=0 and x-2y-2=0
    assert texts(run("solve_axis_triangle_area_line", point=[4, 1], area=1)) == ["x-8y+4=0", "x-2y-2=0"]


def test_parallel_family_exercise():
    # AB: 3x+4y-12=0 ; P(35,43): |105+172-12|/5=53 ; 3*17=51<53<54 -> n=18 ; L18: 3x+4y-12=5*54 -> 3x+4y-282=0
    a = run("solve_parallel_line_family", a_point=[4, 0], b_point=[0, 3], p_point=[35, 43], spacing=3)
    assert [a["values"][0]["canonical"], a["values"][1]["canonical"], a["values"][2]["text"]] == ["53", "18", "3x+4y-282=0"]


def test_translation_parameter_exercise():
    assert run("solve_translation_parameter", line=[3, 4, 1], result_line=[3, 4, -14], axis="right")["values"][0]["canonical"] == "5"


def test_half_plane_exercise():
    # 2x-3y+4: (1,2)->0 on L; (2,3)->-1; (3,4)->-2; (4,3)->3; (3,2)->4 ; origin ->4 (>0): same side = (4),(5)
    a = run("select_points_same_side", line=[2, -3, 4], reference=[0, 0], points=[[1, 2], [2, 3], [3, 4], [4, 3], [3, 2]])
    assert a["selected"] == [4, 5] and a["sides"][0] == 0


def test_region_coefficients_exercise():
    # OA: x+ay=0 through (2,6) -> a=-1/3 ; AB: bx+cy=5 through (2,6),(5,0) -> b=1, c=1/2
    a = run("solve_region_coefficients_from_figure", a_point=[2, 6], b_point=[5, 0], bound=5)
    assert [v["canonical"] for v in a["values"]] == ["-1/3", "1", "1/2"]


def test_region_signs_from_figure_practice():
    # shaded region lies above 3x+4y-12=0 (a,b>0, c<0) and right of 2x-y+2=0 (d>0)
    a = run("read_region_signs_from_figure", lines=[{"line": [3, 4, -12]}, {"line": [2, -1, 2]}], view=[-5, 5, -5, 5],
            statements=[{"coef": c, "op": ">"} for c in "abcd"])
    assert a["selected"] == [1, 2, 4]


@pytest.mark.parametrize(
    ("statement", "truth"),
    [
        ({"kind": "shape_equal_slopes", "shape": "rectangle"}, True),                      # 觀念澄清(1)
        ({"kind": "y_intercept_of_line_through_point", "through_y": -2, "claimed": 2}, False),   # (2)
        ({"kind": "perpendicular_by_coefficients", "l1": [1, 2, 3], "l2": [1, -2, 3]}, False),  # (3) slopes -1/2 and 1/2
        ({"kind": "parallel_at_distance_count", "line": [1, 2, -5], "distance": 5, "claimed_count": 2}, True),  # (4)
        ({"kind": "opposite_sides", "line": [1, 1, 1], "a": [1, 2], "b": [2, -1]}, False),     # (5) values 4 and 2
    ],
)
def test_concept_clarification_truth(statement, truth):
    assert run("evaluate_line_statement_truth", statement=statement)["truth"] is truth


def test_universal_shape_claims_use_counterexamples():
    assert run("evaluate_line_statement_truth", statement={"kind": "shape_equal_slopes", "shape": "trapezoid"})["truth"] is False
    assert run("evaluate_line_statement_truth", statement={"kind": "shape_equal_slopes", "shape": "kite"})["truth"] is False
    assert run("evaluate_line_statement_truth", statement={"kind": "shape_equal_slopes", "shape": "parallelogram"})["truth"] is True


# --- primitives vs sympy-free spot checks ---------------------------------------------------------------------------

def test_geometry_primitives():
    assert G.line_through((G.fr(1), G.fr(2)), (G.fr(4), G.fr(1))) == (1, 3, -7)
    assert G.norm_line(-2, 4, -6) == (1, -2, 3)
    assert G.reflect_point((G.fr(3), G.fr(1)), (1, -1, 0)) == (G.fr(1), G.fr(3))
    assert G.distance_point_line((G.fr(0), G.fr(0)), (1, 1, -39)).canonical() == "39*sqrt(2)/2"
    assert G.sqrt_radical(160).canonical() == "4*sqrt(10)"


# --- every sandbox sampler input is also valid for the validator (defense in depth) ------------------------------------------------

@pytest.mark.parametrize("cid", sorted(COMPONENTS))
def test_samplers_are_deterministic_inputs_only(cid):
    skill, op, source, sampler = COMPONENTS[cid]
    a, b = sampler(random.Random(7)), sampler(random.Random(7))
    assert a == b
    forbidden = {"answer", "correct_answer", "canonical_answer", "answer_contract", "checker", "checker_key", "values", "truth", "selected"}
    assert not (forbidden & set(a)) and not (forbidden & set(source))


def test_independent_drawings_and_lattice_count():
    # 12428: three separate half-planes, 3x-2y+6>=0 / x+2y>=0 / x-2>=0
    a = run("graph_inequality_series", view=[-6, 6, -6, 6], items=[
        {"relations": [{"coefficients": [3, -2, 6], "op": ">="}]}, {"relations": [{"coefficients": [1, 2, 0], "op": ">="}]},
        {"relations": [{"coefficients": [1, 0, -2], "op": ">="}]}])
    assert [d["relations"][0]["boundary"] for d in a["drawings"]] == ["solid"] * 3
    # 12447: x=0: y 2..6 (5), x=1: y 1..4 (4), x=2: y 0..2 (3), x=3: y 0 (1) -> 13
    a = run("graph_inequality_with_lattice_count", view=[-3, 8, -3, 8], relations=[
        {"coefficients": [2, 1, -6], "op": "<="}, {"coefficients": [1, 1, -2], "op": ">="},
        {"coefficients": [1, 0, 0], "op": ">="}, {"coefficients": [0, 1, 0], "op": ">="}])
    assert a["values"][0]["canonical"] == "13"
    assert sorted(map(tuple, a["polygon_vertices"])) == sorted([("0", "2"), ("0", "6"), ("3", "0"), ("2", "0")])
