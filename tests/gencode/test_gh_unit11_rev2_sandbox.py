"""Sandbox gate for the three Unit 11 items added in revision 2 (12650 tent frame, 12662 parameter back-solving,
12664 cannon ceiling).  Same harness and checks as the revision-1 gate; the 35 published components are not rebuilt here."""

from __future__ import annotations

import importlib.util
import json
from fractions import Fraction

import pytest
import sympy as sp

from agent_domains_candidate.polynomial_inequality import build_sandbox as B
from agent_domains_candidate.polynomial_inequality.polynomial_inequality_specs import OP, REV2_COMPONENTS, SKILLS
from agent_domains_candidate.polynomial_inequality.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.polynomial_inequality.verification import verify_payload
from core.checkers.inequality_solution_checker import parse_real_solution_set, real_solution_sets_equal

SEEDS = range(20)
DRYRUN = B.DRYRUN
register_candidate_in_memory()
B.build_all(components=REV2_COMPONENTS)
CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in REV2_COMPONENTS.items()]


def _load(skill_id: str, cid: int):
    path = DRYRUN / skill_id / "components" / f"src_{cid}" / "generate.py"
    spec = importlib.util.spec_from_file_location(f"u11r2_{cid}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gen(cid: int, seed: int = 0) -> dict:
    return _load(SKILLS[REV2_COMPONENTS[cid][0]], cid).generate(seed=seed)


def _is(text: str, expected: sp.Set, var: str = "x") -> bool:
    got = parse_real_solution_set(text.replace(var, "x"))
    return got is not None and real_solution_sets_equal(got, expected)


@pytest.mark.parametrize(("cid", "skill_id", "operation"), CASES)
def test_component_contract_and_grading(cid, skill_id, operation):
    generator = _load(skill_id, cid)
    surfaces = set()
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        assert payload == generator.generate(seed=seed)
        assert payload["domain_operation"] == operation and payload["textbook_example_id"] == cid
        assert payload["fixed_domain_key"] == "inequality.polynomial" and not payload.get("image_assets")
        assert bool(payload.get("visual_spec")) == (cid == 12650)
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], (seed, payload["question_text"][:60])
        surfaces.add(json.dumps([payload["question_text"], payload.get("visual_spec"), payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
    assert len(surfaces) >= 18


def test_source_oracles():
    a = _gen(12650)["correct_answer"]
    assert a["part_1"] == "24*x+3*y=168" and a["part_3"] == "B"  # x + 2 divides f(x) - 1728
    assert sp.simplify(sp.sympify(a["part_2"].replace("^", "**")) - (-48 * sp.Symbol("x") ** 3 + 336 * sp.Symbol("x") ** 2)) == 0
    assert _is(a["part_4"], sp.Interval(3, 6))
    assert _gen(12662)["correct_answer"] == {"part_1": "-2", "part_2": "-3"}  # (x+1)(x-3) = x^2 - 2x - 3
    assert _is(_gen(12664)["correct_answer"], sp.Interval.open(0, 4), "k")


@pytest.mark.parametrize("seed", SEEDS)
def test_12650_figure_labels_follow_the_triple(seed):
    p = _gen(12650, seed)
    p3, q3, r3 = p["math_core"]["givens"]["items"][0]["triple"]
    labels = sorted(line["label"] for line in p["visual_spec"]["lines"] if line.get("label"))
    assert labels == sorted([f"{p3}x", f"{q3}x", f"{r3}x", "y"]) and len(p["visual_spec"]["lines"]) == 9
    assert f"${p3}x$" in p["question_text"] and f"${r3}x$" in p["question_text"]
    assert p3 ** 2 + q3 ** 2 == r3 ** 2


@pytest.mark.parametrize("seed", SEEDS)
def test_12650_numbers_satisfy_the_stem(seed):
    p = _gen(12650, seed)
    g = p["math_core"]["givens"]["items"][0]
    P = sum(g["triple"])
    x, y = sp.symbols("x y")
    eq = sp.sympify(p["correct_answer"]["part_1"].replace("=", "-(") + ")")
    assert sp.simplify(eq.subs({x: 1, y: 0}) - (2 * P - g["L"])) == 0  # 2(p+q+r)x + 3y = L
    f = sp.sympify(p["correct_answer"]["part_2"].replace("^", "**"))
    root = {"A": -1, "B": -2, "C": -3, "D": -4, "E": 0}[p["correct_answer"]["part_3"]]
    assert sp.simplify(f.subs(sp.Symbol("x"), root) - g["V"]) == 0  # the chosen factor really divides f(x) - V
    assert f"${g['L']}$" in p["question_text"] and f"${g['V']}$" in p["question_text"]


@pytest.mark.parametrize("seed", SEEDS)
def test_12664_peak_stays_below_the_ceiling_only_inside_the_range(seed):
    p = _gen(12664, seed)
    g = p["math_core"]["givens"]["items"][0]
    t, k = sp.symbols("t k", positive=True)
    top = sp.maximum(k * t * (g["T"] - t), t, sp.Interval(-sp.oo, sp.oo))
    bound = sp.solve(sp.Eq(top, g["H"]), k)[0]
    assert _is(p["correct_answer"], sp.Interval.open(0, bound), "k")
    assert f"${g['H']}$" in p["question_text"]


@pytest.mark.parametrize("seed", SEEDS)
def test_12662_back_solved_factor_gives_the_stated_solution(seed):
    p = _gen(12662, seed)
    g = p["math_core"]["givens"]["items"][0]
    a, b = (Fraction(p["correct_answer"][f"part_{i}"]) for i in (1, 2))
    x = sp.Symbol("x", real=True)
    pos = sum(c * x ** (2 - i) for i, c in enumerate(g["pos"]))
    product = sp.expand(pos * (x ** 2 + sp.Rational(a.numerator, a.denominator) * x + sp.Rational(b.numerator, b.denominator)))
    rel = {">": product > 0, "<": product < 0, ">=": product >= 0, "<=": product <= 0}[g["rel"]]
    got = sp.solve_univariate_inequality(rel, x, relational=False)
    r1, r2 = sorted(g["roots"])
    closed = g["rel"] in (">=", "<=")
    want = sp.Interval(r1, r2, not closed, not closed) if g["shape"] == "between" else sp.Union(
        sp.Interval(-sp.oo, r1, True, not closed), sp.Interval(r2, sp.oo, not closed, True))
    assert real_solution_sets_equal(got, want)
