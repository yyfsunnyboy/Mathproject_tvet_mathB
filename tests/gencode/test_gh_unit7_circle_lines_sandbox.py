"""Sandbox gate for 普高數學1 Unit 7 (圓與直線的關係): per-component contract, oracle, grading and figure checks.

Runs against ``tmp/gh_unit7_sandbox_dryrun`` with the candidate domain registered in memory only.
Source oracles are the textbook's own worked solutions (hand-derived, independent of the domain code).
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest

from agent_domains_candidate.analytic_geometry_circle_lines.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.analytic_geometry_circle_lines.unit7_specs import COMPONENTS, DEFERRED, OP, SKILLS, STATIC_COMPONENTS
from agent_domains_candidate.analytic_geometry_circle_lines.verification import grade as _grade
from agent_domains_candidate.analytic_geometry_circle_lines.verification import verify_payload
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = PROJECT_ROOT / "tmp" / "gh_unit7_sandbox_dryrun"
DB = PROJECT_ROOT / "instance" / "kumon_math.db"
SEEDS = range(20)
SURFACE_FLOOR = 18
FIGURE_COMPONENTS = {12503, 12507, 12514, 12516}
POINT_OR_NONE = {"coordinate_pair_checker", "text_short_checker"}
register_candidate_in_memory()

CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]


def _load(skill_id: str, cid: int, filename: str):
    path = DRYRUN / skill_id / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"u7_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("cid", "skill_id", "operation"), CASES)
def test_component_contract_oracle_grading_and_figure(cid, skill_id, operation):
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
        assert payload["fixed_domain_key"] == "analytic_geometry.circle_line_relations"
        text = payload["question_text"]
        assert "$$" not in text and "\\\\(" not in text and "承例題" not in text
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], (seed, text[:60])
        assert bool(payload.get("visual_spec")) == (cid in FIGURE_COMPONENTS)
        surfaces.add(json.dumps([text, payload.get("visual_spec"), payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
        contract = payload["answer_contract"]
        assert all("input_type" not in p for p in contract.get("parts", []))  # one widget kind: no answer leak
        # A varied relation may turn a point field into a 「無」 field; any other checker change is a topology change.
        shapes.add((contract["answer_type"], contract.get("checker"),
                    tuple((p["key"], "point_or_none" if p["checker"] in POINT_OR_NONE else p["checker"])
                          for p in contract.get("parts", []))))
    assert len(shapes) == 1, shapes
    assert len(surfaces) >= (1 if cid in STATIC_COMPONENTS else SURFACE_FLOOR)


def test_nothing_is_deferred_and_all_36_rows_are_covered():
    assert DEFERRED == {}
    assert set(COMPONENTS) == set(range(12481, 12517))
    counts = {key: sum(1 for spec in COMPONENTS.values() if spec[0] == key) for key in SKILLS}
    assert counts == {"judge": 21, "tangent": 15}


def test_skill_bindings_follow_the_formal_database():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = dict(con.execute("select id, skill_id from textbook_examples where id between 12481 and 12516").fetchall())
    finally:
        con.close()
    assert {cid: SKILLS[spec[0]] for cid, spec in COMPONENTS.items()} == rows
    assert rows[12513] == rows[12515] == "gh_JudgingTheRelationshipOfCircleAndLine"


def _source(cid: int) -> dict:
    return _load(SKILLS[COMPONENTS[cid][0]], cid, "generate.py").generate(seed=0)


def _answers(cid: int):
    return _source(cid)["correct_answer"]


# --- source oracles: the textbook's worked solutions, written out by hand -------------------------------------------

def test_source_oracles_from_the_textbook_solutions():
    secant, tangent, disjoint = "1", "2", "3"
    assert _answers(12481) == {"part_1": secant, "part_2": "(-2,-1)", "part_3": "(1,2)"}
    assert sorted(_answers(12482)) == ["-5", "3"]
    assert _answers(12483) == {"part_1": secant, "part_2": tangent}
    assert _answers(12484) == "8"
    a = _answers(12485)
    assert sorted(a["part_1"]) == ["-26", "4"] and a["part_3"] == "-26<k<4"
    assert set(a["part_2"].split(", ")) == {"3x+4y+4=0", "3x+4y-26=0"}
    assert _answers(12486) == {"part_1": tangent, "part_2": "(2,3)", "part_3": "無", "part_4": disjoint, "part_5": "無", "part_6": "無"}
    assert _answers(12487) == "1/2<k<1"
    assert _answers(12488) == disjoint
    assert sorted(_answers(12489)) == ["-30", "20"]
    assert set(_answers(12490).split(", ")) == {"3x-y-3=0", "3x-y-23=0"}
    assert [_answers(c) for c in (12491, 12492, 12493, 12494, 12508)] == ["B", "A", "A", "A", "A"]
    assert _answers(12495) == {"part_1": secant, "part_2": "(1,4)", "part_3": "(3,-2)"}
    assert _answers(12496) == "k<=4/5"
    assert _answers(12497) == disjoint
    assert _answers(12498) == ["-4"]
    assert _answers(12499) == {"part_1": "3+sqrt(5)", "part_2": "3-sqrt(5)"}
    assert _answers(12500) == "4x+3y-27=0"
    assert set(_answers(12501).split(", ")) == {"x-y-3=0", "x+y-7=0"}
    assert set(_answers(12502).split(", ")) == {"x-2=0", "4x-3y+10=0"}
    assert _answers(12503) == {"part_1": "-3/2", "part_2": "3x+2y-38=0", "part_3": "(38/3,0)"}
    assert _answers(12504) == {"part_1": "2", "part_2": "-20"}
    assert set(_answers(12505).split(", ")) == {"x-2y-2=0", "x+2y-2=0"}
    assert set(_answers(12506).split(", ")) == {"x=0", "3x-4y+8=0"}
    assert _answers(12507) == {"part_1": "2*sqrt(13)", "part_2": "x^2+(y-6)^2=52", "part_3": "8"}
    assert set(_answers(12509).split(", ")) == {"2x+3y+16=0", "2x+3y-10=0"}
    assert _answers(12510) == "x-3y-15=0"
    assert set(_answers(12511).split(", ")) == {"y-3=0", "5x-12y+6=0"}
    assert sorted(_answers(12512)) == ["-1", "7"]
    assert _answers(12513) == {"part_1": "4", "part_2": "0"}
    assert _answers(12514) == "15"
    assert _answers(12515) == {"part_1": "4", "part_2": "x+2y-10=0"}
    assert _answers(12516) == {"part_1": "3", "part_2": "7"}


def test_stems_carry_the_source_numbers_at_variant_zero():
    assert "x-y+1=0" in _source(12481)["question_text"] and "x^{2}+y^{2}=5" in _source(12481)["question_text"]
    assert "y=mx-3" in _source(12512)["question_text"] and "y=x+m" in _source(12513)["question_text"]
    assert "3x+y=7" in _source(12495)["question_text"] and "4^{2}" in _source(12488)["question_text"]
    building = _source(12507)
    assert "M\\left(0,\\ 6\\right)" in building["question_text"] and "P\\left(6,\\ 10\\right)" in building["question_text"]
    labels = {p.get("label") for p in building["visual_spec"]["points"]}
    assert {"A", "B", "Q", "M(0,6)", "P(6,10)"} <= labels
    light = _source(12514)["visual_spec"]
    assert {p.get("label") for p in light["points"]} >= {"A(1,6)", "P", "Q"} and light["circles"][0]["r"] == pytest.approx(5 ** 0.5)
    badge = _source(12516)["visual_spec"]
    assert {p.get("label") for p in badge["points"]} == {"O", "A", "B", "C", "D", "E"}


def test_figures_follow_the_varied_parameters():
    """Every variant's figure is rebuilt from its own givens: labels and geometry match the stem numbers."""
    for cid in FIGURE_COMPONENTS:
        generator = _load(SKILLS[COMPONENTS[cid][0]], cid, "generate.py")
        figures = set()
        for seed in SEEDS:
            payload = generator.generate(seed=seed)
            spec = payload["visual_spec"]
            assert spec["show_grid"] is False and spec["render_required"] is True
            for point in spec["points"]:
                label = point.get("label", "")
                if "(" in label:  # labelled coordinates must be the ones printed in the stem
                    name, coords = label.split("(", 1)
                    x, y = coords.rstrip(")").split(",")
                    assert f"{name}\\left({x},\\ {y}\\right)" in payload["question_text"], (cid, label)
                    assert (point["x"], point["y"]) == (float(x), float(y))
            figures.add(json.dumps(spec, sort_keys=True))
        assert len(figures) >= SURFACE_FLOOR, cid


def test_parameter_tangency_keeps_two_admissible_roots_like_the_source():
    """12482: no variant may silently drop a root that degenerates the circle (the source has two valid k)."""
    generator = _load(SKILLS["judge"], 12482, "generate.py")
    for seed in SEEDS:
        assert len(generator.generate(seed=seed)["correct_answer"]) == 2, seed


def test_equivalent_and_wrong_answers_for_key_forms():
    judge, tangent = SKILLS["judge"], SKILLS["tangent"]
    payload = _source(12499)
    base = dict(payload["correct_answer"])
    for good in ("3+√5", "√5+3", "3+\\sqrt{5}"):
        assert _grade(payload, {**base, "part_1": good}, judge), good
    for bad in ("3-√5", "5.236", "3+√3"):
        assert not _grade(payload, {**base, "part_1": bad}, judge), bad
    lines = _source(12502)
    for good in ("x=2, 4x-3y+10=0", "4x-3y=-10，x=2", "y=4/3x+10/3, x=2"):
        assert _grade(lines, good, tangent), good
    for bad in ("x=2", "4x-3y+10=0", "x=2, 4x+3y+10=0"):
        assert not _grade(lines, bad, tangent), bad
    region = _source(12487)
    for good in ("1/2<k<1", "0.5<k<1", "1>k>1/2"):
        assert _grade(region, good, judge), good
    for bad in ("1/2<=k<1", "k<1", "k>1/2"):
        assert not _grade(region, bad, judge), bad
    values = _source(12482)
    for good in ("3, -5", "-5,3", "k=3或k=-5"):
        assert _grade(values, good, judge), good
    for bad in ("3", "-3, 5", "3, -5, 1"):
        assert not _grade(values, bad, judge), bad
    points = _source(12486)
    base = dict(points["correct_answer"])
    assert not _grade(points, {**base, "part_3": "(2,3)"}, judge)
    assert not _grade(points, {**base, "part_4": "1"}, judge)
