"""Sandbox gate for 普高數學1 Unit 10 (三次函數的圖形特徵): per-component contract, oracle, grading and figure checks.

Builds ``tmp/gh_unit10_sandbox_dryrun`` (build_sandbox.build_all) with the candidate domain registered in memory
only.  Source oracles are hand-derived values (independent of the domain code).  Every figure is checked against
the generated numbers: a curve is the function the answer says it is, in the colour the stem names.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from fractions import Fraction
from pathlib import Path

import pytest
import sympy as sp
from sympy.parsing.sympy_parser import convert_xor, implicit_multiplication_application, parse_expr, standard_transformations

from agent_domains_candidate.function_cubic import build_sandbox as B
from agent_domains_candidate.function_cubic.cubic_adapter import COLORS
from agent_domains_candidate.function_cubic.cubic_specs import COMPONENTS, DEFERRED, OP, SKILLS
from agent_domains_candidate.function_cubic.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.function_cubic.verification import verify_payload
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = B.DRYRUN
DB = PROJECT_ROOT / "instance" / "kumon_math.db"
SEEDS = range(20)
SURFACE_FLOOR = 18
FIGURE_COMPONENTS = {12609, 12610, 12611, 12621, 12628}
register_candidate_in_memory()
B.build_all()

CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]
_T = standard_transformations + (implicit_multiplication_application, convert_xor)


def _load(skill_id: str, cid: int, filename: str):
    path = DRYRUN / skill_id / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"u10_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gen(cid: int, seed: int = 0) -> dict:
    return _load(SKILLS[COMPONENTS[cid][0]], cid, "generate.py").generate(seed=seed)


def _answers(cid: int):
    return _gen(cid)["correct_answer"]


def _same(a: str, b: str) -> bool:
    return sp.simplify(parse_expr(a, transformations=_T) - parse_expr(b, transformations=_T)) == 0


@pytest.mark.parametrize(("cid", "skill_id", "operation"), CASES)
def test_component_contract_oracle_and_grading(cid, skill_id, operation):
    directory = DRYRUN / skill_id / "components" / f"src_{cid}"
    assert {p.name for p in directory.iterdir() if p.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    assert (directory / "get_hint.py").read_text(encoding="utf-8") == _build_get_hint_py()
    generator = _load(skill_id, cid, "generate.py")
    metadata = _load(skill_id, cid, "metadata.py")
    assert metadata.TEXTBOOK_EXAMPLE_ID == cid and metadata.DOMAIN_OPERATION == operation

    surfaces, shapes = set(), set()
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        assert payload == generator.generate(seed=seed)  # deterministic
        assert payload["domain_operation"] == operation and payload["textbook_example_id"] == cid
        assert payload["fixed_domain_key"] == "function.cubic_graph"
        text = payload["question_text"]
        assert "$$" not in text and "承例題" not in text and "MATH_PARSE_FAILED" not in text
        assert bool(payload.get("visual_spec")) == (cid in FIGURE_COMPONENTS)
        assert not payload.get("image_assets")  # no stale static picture is ever attached to a varied question
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], (seed, text[:60])
        surfaces.add(json.dumps([text, payload.get("visual_spec"), payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
        contract = payload["answer_contract"]
        shapes.add((contract["answer_type"], contract.get("checker"), tuple((p["key"], p["checker"]) for p in contract.get("parts", []))))
    assert len(shapes) <= 2, shapes  # the only shape change is the 12612 "cannot overlap" variant (one part instead of three)
    assert len(surfaces) >= SURFACE_FLOOR


def test_coverage_and_deferred_items_are_explicit():
    assert set(COMPONENTS) | set(DEFERRED) == set(range(12603, 12629))
    assert not set(COMPONENTS) & set(DEFERRED)
    assert set(DEFERRED) == {12603, 12604, 12605, 12606, 12607, 12613, 12626}
    assert len(COMPONENTS) == 19


def test_skill_bindings_follow_the_formal_database():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = dict(con.execute("select id, skill_id from textbook_examples where id between 12603 and 12628").fetchall())
    finally:
        con.close()
    assert {cid: SKILLS[spec[0]] for cid, spec in COMPONENTS.items()} == {cid: rows[cid] for cid in COMPONENTS}
    assert all(rows[cid] == "gh_GraphsOfCubicFunctions" for cid in DEFERRED)


# --- source oracles: hand-derived values --------------------------------------------------------------------------

def test_source_oracles_forms_and_conditions():
    a = _answers(12608)
    assert a["part_1"] == "(4,2)" and _same(a["part_2"], "-x^3/16+3*x^2/8")
    a = _answers(12614)
    assert a["part_1"] == "(4,16)" and _same(a["part_2"], "x^3-12*x^2+36*x") and a["part_3"] == "81"
    assert _answers(12616) == {"part_1": "-2", "part_2": "5", "part_3": "-2"}
    a = _answers(12622)
    assert [a[f"part_{i}"] for i in range(1, 9)] == ["-1", "14", "-2", "-23", "1", "-4/3", "-1/3", "38/27"]
    assert _answers(12623) == "10" and _answers(12624) == {"part_1": "-2", "part_2": "5"} and _answers(12625) == "(-1,3)"
    assert _answers(12612) == {"part_1": "A", "part_2": "-2", "part_3": "-3"}


def test_source_oracles_statements_and_matching():
    assert _answers(12615) == [1, 2, 4, 5] and _answers(12627) == [4, 5]
    assert [_answers(c) for c in (12617, 12618, 12619, 12620)] == ["B", "A", "B", "A"]
    assert _answers(12609) == {"part_1": "C", "part_2": "A", "part_3": "B"}  # -x^3 -> Γ3 (green), 2x^3 -> Γ1 (red), -2x^3 -> Γ2 (blue)
    assert _answers(12610) == {"part_1": "B", "part_2": "A"} and _answers(12611) == {"part_1": "B", "part_2": "A"}
    assert _answers(12628) == {"part_1": "B", "part_2": "A", "part_3": "C", "part_4": "D"}
    assert _answers(12621) == "F"  # a3 > a2 > a1 is the sixth ordering listed


# --- figures follow the generated numbers -------------------------------------------------------------------------

def _poly(coeffs: list, x: float) -> float:
    c3, c2, c1, c0 = (float(Fraction(str(c))) for c in coeffs)
    return ((c3 * x + c2) * x + c1) * x + c0


@pytest.mark.parametrize("cid", sorted(FIGURE_COMPONENTS))
@pytest.mark.parametrize("seed", SEEDS)
def test_figure_curves_are_the_functions_the_answer_names_in_the_colours_the_stem_names(cid, seed):
    p = _gen(cid, seed)
    givens, answer = p["math_core"]["givens"], p["math_core"]["target"]
    funcs, colors = givens["functions"], givens["colors"]
    text = p["question_text"]
    curves = [c for c in p["visual_spec"]["curves"] if c.get("label", "").startswith("Γ")]
    assert len(curves) == len(funcs) and p["visual_spec"]["show_grid"] is False
    for g in range(1, len(funcs) + 1):
        curve = next(c for c in curves if c["label"] == {1: "Γ₁", 2: "Γ₂", 3: "Γ₃", 4: "Γ₄"}[g])
        assert curve["color"] == COLORS[colors[g - 1]]
        if cid != 12621:
            assert f"（{colors[g - 1]}曲線）" in text
        function = funcs[answer["assignment"].index(g)]  # the function the answer says is drawn as Γ_g
        assert all(abs(q[1] - _poly(function["coeffs"], q[0])) < 2e-3 for q in curve["points"]) and len(curve["points"]) >= 14
        others = [f for f in funcs if f is not function]
        for o in others:  # the picture can be told apart from every other function of the question
            assert max(abs(q[1] - _poly(o["coeffs"], q[0])) for q in curve["points"]) > 0.5
    if cid == 12621:
        ordering = sorted(range(1, 4), key=lambda g: -_poly(funcs[answer["assignment"].index(g)]["coeffs"], 1.0))
        assert ordering == answer["ranking"] and p["display_answer"] == "$" + ">".join(f"a_{{{g}}}" for g in ordering) + "$"
    if cid == 12609:  # the black reference curve is y = x^3 and is labelled
        ref = next(c for c in p["visual_spec"]["curves"] if c.get("label") == "y=x³")
        assert all(abs(q[1] - q[0] ** 3) < 2e-3 for q in ref["points"])


@pytest.mark.parametrize("seed", SEEDS)
def test_12628_shifts_follow_the_stem(seed):
    p = _gen(12628, seed)
    funcs = p["math_core"]["givens"]["functions"]
    base, up, right, rightdown = (f["coeffs"] for f in funcs)
    for x in (-1.5, 0.0, 0.7, 2.0):
        dy = _poly(up, x) - _poly(base, x)
        dx = _dx(base, right)
        assert abs(_poly(right, x) - _poly(base, x - dx)) < 1e-9
        assert abs(_poly(rightdown, x) - (_poly(base, x - dx) - dy)) < 1e-9
        assert dy != 0 and dx != 0
        assert f"f\\left(x{'-' if dx > 0 else '+'}{abs(int(dx))}\\right)" in p["question_text"]


def _dx(base: list, shifted: list) -> float:
    c3, c2 = float(Fraction(str(base[0]))), float(Fraction(str(base[1])))
    return -(float(Fraction(str(shifted[1]))) - c2) / (3 * c3)


# --- the two textbook worked-example checks ------------------------------------------------------------------------

@pytest.mark.parametrize("seed", SEEDS)
def test_12614_route_is_symmetric_and_passes_through_the_given_points(seed):
    p = _gen(seed=seed, cid=12614)
    item = p["math_core"]["givens"]["items"][0]
    f = parse_expr(p["correct_answer"]["part_2"], transformations=_T)
    x = sp.Symbol("x")
    (ax, ay), (bx, by) = item["A"], item["B"]
    assert f.subs(x, 0) == 0 and f.subs(x, ax) == ay and f.subs(x, bx) == by
    cx, cy = (sp.Rational(v) for v in p["correct_answer"]["part_1"].strip("()").split(","))
    assert (cx, cy) == (sp.Rational(ax + bx, 2), sp.Rational(ay + by, 2))
    assert f.subs(x, 2 * cx - 3) + f.subs(x, 3) == 2 * cy  # point symmetry about the centre
    assert sp.Rational(p["correct_answer"]["part_3"]) == f.subs(x, item["C_x"])


@pytest.mark.parametrize("seed", SEEDS)
def test_12608_flight_path_has_zero_linear_term_and_the_given_centre(seed):
    p = _gen(12608, seed)
    (cx, cy) = p["math_core"]["givens"]["items"][0]["center"]
    f = parse_expr(p["correct_answer"]["part_2"], transformations=_T)
    x = sp.Symbol("x")
    assert sp.Poly(f, x).coeff_monomial(x) == 0 and f.subs(x, 0) == 0 and f.subs(x, cx) == cy and sp.diff(f, x, 2).subs(x, cx) == 0
    assert p["correct_answer"]["part_1"] == f"({2 * cx},{2 * cy})" and f.subs(x, 2 * cx) == 2 * cy
