"""Sandbox gate for 普高數學1 Unit 8 (多項式的除法原理): per-component contract, oracle and grading checks.

Runs against ``tmp/gh_unit8_sandbox_dryrun`` (built by ``build_sandbox.build_all``) with the candidate
domain registered in memory only.  Source oracles are the textbook's worked solutions or hand-derived
values (independent of the domain code).
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest
import sympy as sp
from sympy.parsing.sympy_parser import convert_xor, implicit_multiplication_application, parse_expr, standard_transformations

from agent_domains_candidate.algebra_polynomial_division.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.algebra_polynomial_division.unit8_specs import COMPONENTS, DEFERRED, OP, SKILLS
from agent_domains_candidate.algebra_polynomial_division.verification import verify_payload
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = PROJECT_ROOT / "tmp" / "gh_unit8_sandbox_dryrun"
DB = PROJECT_ROOT / "instance" / "kumon_math.db"
SEEDS = range(20)
SURFACE_FLOOR = 18
register_candidate_in_memory()

CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]
_T = standard_transformations + (implicit_multiplication_application, convert_xor)


def _load(skill_id: str, cid: int, filename: str):
    path = DRYRUN / skill_id / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"u8_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source(cid: int) -> dict:
    return _load(SKILLS[COMPONENTS[cid][0]], cid, "generate.py").generate(seed=0)


def _answers(cid: int):
    return _source(cid)["correct_answer"]


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
        assert payload["fixed_domain_key"] == "algebra.polynomial_division"
        text = payload["question_text"]
        assert "$$" not in text and "\\\\(" not in text and "承例題" not in text
        assert not payload.get("visual_spec")  # polynomial / table content is carried by the LaTeX stem
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], (seed, text[:60])
        surfaces.add(json.dumps([text, payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
        contract = payload["answer_contract"]
        shapes.add((contract["answer_type"], contract.get("checker"), tuple((p["key"], p["checker"]) for p in contract.get("parts", []))))
    assert len(shapes) == 1, shapes
    assert len(surfaces) >= SURFACE_FLOOR


def test_nothing_is_deferred_and_all_43_rows_are_covered():
    assert DEFERRED == {}
    assert set(COMPONENTS) == set(range(12517, 12560))
    counts = {key: sum(1 for spec in COMPONENTS.values() if spec[0] == key) for key in SKILLS}
    assert counts == {"basic": 1, "arith": 18, "remainder": 13, "factor": 11}


def test_skill_bindings_follow_the_formal_database():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = dict(con.execute("select id, skill_id from textbook_examples where id between 12517 and 12559").fetchall())
    finally:
        con.close()
    assert {cid: SKILLS[spec[0]] for cid, spec in COMPONENTS.items()} == rows


# --- source oracles: the textbook's worked solutions / hand-derived values -------------------------------------------

def test_source_oracles_expression_and_numeric():
    a = _answers(12520)
    assert _same(a["part_1"], "3x^3+x^2+7x-4") and _same(a["part_2"], "3x^3-x^2+x-6")
    assert _same(_answers(12521), "6x^3-7x^2+4x-1")
    assert _answers(12522) == {"part_1": "2", "part_2": "3"}
    a = _answers(12523)
    assert _same(a["part_1"], "x^3-x^2+3x-4") and a["part_2"] == "5"
    a = _answers(12524)
    assert [a[f"part_{i}"] for i in range(1, 5)] == ["1", "5", "7", "3"] and a["part_5"] == "2.93"
    assert _answers(12525) == {"part_1": "73", "part_2": "4"}
    a = _answers(12526)
    assert _same(a["part_1"], "4x^3+x^2-3x+3") and _same(a["part_2"], "x^2+3x-5")
    assert _same(_answers(12527), "3x^3-4x^2-x+2")
    a = _answers(12529)
    assert a["part_1"] == "3" and _same(a["part_2"], "2x-1")
    a = _answers(12530)
    assert _same(a["part_1"], "x^2-4x+18") and a["part_2"] == "-73" and _same(a["part_3"], "2x^3+x^2-3x+2") and a["part_4"] == "1"
    a = _answers(12531)
    assert [a[f"part_{i}"] for i in range(1, 5)] == ["2", "1", "2", "6"] and a["part_5"] == "5.98"
    a = _answers(12532)
    assert _same(a["part_1"], "x+1") and _same(a["part_2"], "6x^2+3x-3") and _same(a["part_3"], "-9x^4-9x^3+7x^2+5x-2")
    a = _answers(12533)
    assert a["part_1"] == "-8" and a["part_2"] == "-3" and _same(a["part_3"], "2x+3")
    a = _answers(12534)
    assert _same(a["part_1"], "x^2-2x+1") and a["part_2"] == "-2" and a["part_4"] == "-31"
    assert _same(_answers(12535), "x^2+2x-1")
    assert _answers(12536) == "280"
    a = _answers(12537)
    assert [a[f"part_{i}"] for i in range(1, 5)] == ["8", "16", "6", "7"] and a["part_5"] == "7.03"
    assert _answers(12538) == "-43" and _answers(12540) == "4" and _answers(12541) == "21"


def test_source_oracles_remainder_factor_and_selection():
    assert _same(_answers(12539), "-2x+8") and _same(_answers(12542), "5x+1") and _same(_answers(12545), "2x+4")
    assert _same(_answers(12547), "3x-2") and _same(_answers(12548), "x^3+2x")
    a = _answers(12549)
    assert _same(a["part_1"], "2x-5") and _same(a["part_2"], "2x-5")
    assert _answers(12550) == [2, 3, 4]
    assert _same(_answers(12551), "2x^3-11x^2+19x-10") and _same(_answers(12554), "4x^3-12x^2+8x")
    a = _answers(12552)
    assert _same(a["part_1"], "x^3+3x^2-4x-12") and _same(a["part_2"], "(x-2)(x+2)(x+3)")
    assert _answers(12553) == "-3" and _answers(12555) == "3/256"
    assert _answers(12557) == {"part_1": "-1", "part_2": "4"}
    a = _answers(12558)
    assert a["part_1"] == "1" and _same(a["part_2"], "x^4-x^3+x^2-x+1")
    a = _answers(12559)
    assert _same(a["part_1"], "3x^3+7x^2-4") and _same(a["part_2"], "2x^3+12x^2+22x+17")
    assert _answers(12517) == [1, 2, 4] and _answers(12528) == [1, 4, 5] and _answers(12546) == [3, 5]
    assert [_answers(c) for c in (12518, 12519, 12543, 12544, 12556)] == ["B", "A", "A", "B", "A"]


# --- special-attention components ------------------------------------------------------------------------------------

def test_12537_keeps_both_sub_questions_with_the_rounding_rule():
    p = _source(12537)
    text = p["question_text"]
    assert "(1)" in text and "(2)" in text and "0.505" in text and "第三位四捨五入" in text
    assert p["answer_contract"]["answer_type"] == "multi_part" and len(p["answer_contract"]["parts"]) == 5


@pytest.mark.parametrize("seed", SEEDS)
def test_12552_board_text_matches_the_generated_polynomial(seed):
    p = _load(SKILLS["factor"], 12552, "generate.py").generate(seed=seed)
    sem = p["semantic_answer"]
    known = p["math_core"]["givens"]["known"]
    board = sp.Poly(known + [0], sp.Symbol("x")).as_expr()
    text = p["question_text"]
    assert "\\square" in text and "如圖" not in text
    # the cubic the student must find contains exactly the displayed terms plus the erased constant
    cubic = parse_expr(sem["poly"]["plain"], transformations=_T)
    assert sp.expand(cubic - board - parse_expr(sem["k"])) == 0
    root = p["math_core"]["givens"]["root"]
    assert cubic.subs(sp.Symbol("x"), root) == 0


@pytest.mark.parametrize("seed", SEEDS)
def test_12555_table_matches_the_masked_division(seed):
    p = _load(SKILLS["factor"], 12555, "generate.py").generate(seed=seed)
    g = p["math_core"]["givens"]
    coeffs = [sp.Rational(str(c)) if c is not None else sp.Symbol("m") for c in g["coefficients"]]
    x = sp.Symbol("x")
    f = sum(c * x ** (len(coeffs) - 1 - i) for i, c in enumerate(coeffs))
    solved = sp.solve(sp.Eq(f.subs(x, g["root"]), sp.Rational(str(g["remainder"]))), sp.Symbol("m"))
    assert [sp.Rational(s) for s in solved] == [sp.Rational(p["correct_answer"])]
    text = p["question_text"]
    assert "\\bullet" in text and "\\begin{array}" in text and "如圖" not in text and "下圖" not in text
    n = len(coeffs) - 1
    assert f"{'零一二三四五六七八九'[n]}次多項式" in text
