"""Sandbox gate for 普高數學1 Unit 6 (圓方程式): per-component contract, oracle and grading checks.

Runs against ``tmp/gh_unit6_sandbox_dryrun`` with the candidate domain registered in memory only.
Source oracles are the textbook's own worked solutions (hand-derived, independent of the domain code).
"""

from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import pytest

from agent_domains_candidate.analytic_geometry_circles.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.analytic_geometry_circles.unit6_specs import COMPONENTS, DEFERRED, OP, SKILLS
from agent_domains_candidate.analytic_geometry_circles.verification import (
    equivalent_value as _equivalent_value,
    grade as _grade,
    parts_of as _parts,
    wrong_value as _wrong_value,
)
from core.gencode.answer_payload import validate_answer_contract_consistency
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.services.v3_question_integrity_validator import validate_component_payload
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = PROJECT_ROOT / "tmp" / "gh_unit6_sandbox_dryrun"
SEEDS = range(20)
register_candidate_in_memory()

CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]
FIGURE_WITHOUT_CUE: set[int] = set()
# 12478 quotes the newspaper box in the stem (the book prints it as a boxed text figure), so no visual is attached
TEXT_FIGURE = {12478}
SURFACE_FLOOR = 18


def _load(skill_id: str, cid: int, filename: str):
    path = DRYRUN / skill_id / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"u6_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("cid", "skill_id", "operation"), CASES)
def test_component_contract_oracle_and_grading(cid, skill_id, operation):
    directory = DRYRUN / skill_id / "components" / f"src_{cid}"
    assert {p.name for p in directory.iterdir() if p.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    assert (directory / "get_hint.py").read_text(encoding="utf-8") == _build_get_hint_py()
    generator = _load(skill_id, cid, "generate.py")
    metadata = _load(skill_id, cid, "metadata.py")
    assert metadata.TEXTBOOK_EXAMPLE_ID == cid and metadata.DOMAIN_OPERATION == operation

    surfaces = set()
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        assert payload == generator.generate(seed=seed)  # deterministic
        assert payload["domain_operation"] == operation and payload["textbook_example_id"] == cid
        assert payload["fixed_domain_key"] == "analytic_geometry.circle_equations"
        assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
        assert validate_answer_contract_consistency(payload) == []
        assert validate_answer_contract_consistency(payload["answer_contract"]) == []
        integrity = validate_component_payload(payload, component_id=f"src_{cid}")
        assert integrity["passed"], integrity["blockers"]
        surfaces.add(json.dumps([payload["question_text"], payload.get("visual_spec"), payload.get("table_data"), payload["correct_answer"]],
                                sort_keys=True, ensure_ascii=False, default=str))
        text = payload["question_text"]
        assert "$$" not in text and "\\\\(" not in text
        # a figure is rendered exactly when the stem points at one
        mentions_figure = any(k in text for k in ("如圖", "右圖", "如圖所示"))
        assert mentions_figure == bool(payload.get("visual_spec")) or cid in FIGURE_WITHOUT_CUE or cid in TEXT_FIGURE, (cid, text[:40])

        # canonical answer accepted, every wrong part rejected
        assert _grade(payload, payload["correct_answer"], skill_id)
        parts = _parts(payload)
        if payload["answer_contract"]["answer_type"] in {"multi_part", "table_fill"}:
            for part in parts:
                bad = dict(payload["correct_answer"])
                bad[part["key"]] = _wrong_value(part)
                assert not _grade(payload, bad, skill_id), (seed, part["key"], bad)
                equivalent = _equivalent_value(part)
                if equivalent is not None:
                    good = dict(payload["correct_answer"])
                    good[part["key"]] = equivalent
                    assert _grade(payload, good, skill_id), (seed, part["key"], good)
        else:
            assert not _grade(payload, _wrong_value(parts[0]), skill_id)
            equivalent = _equivalent_value(parts[0])
            if equivalent is not None:
                assert _grade(payload, equivalent, skill_id), (seed, equivalent)
    assert len(surfaces) >= SURFACE_FLOOR


def test_nothing_is_deferred():
    assert DEFERRED == {}


def test_all_thirty_two_textbook_rows_are_accounted_for():
    assert set(COMPONENTS) == set(range(12449, 12481))


def _source(cid: int) -> dict:
    return _load(SKILLS[COMPONENTS[cid][0]], cid, "generate.py").generate(seed=0)


def _answers(cid: int) -> dict:
    payload = _source(cid)
    return payload["correct_answer"] if isinstance(payload["correct_answer"], dict) else {"value": payload["correct_answer"]}


# --- source oracles: the textbook's worked solutions, written out by hand -------------------------------------------

def test_source_oracles_from_the_textbook_solutions():
    # 例題1 (x-2)^2+(y+3)^2=16 / =25; 例題2 (x-2)^2+y^2=25
    a = _answers(12449)
    assert a["part_1"] == "(x-2)^2+(y+3)^2=16" and a["part_2"] == "(x-2)^2+(y+3)^2=25"
    assert _answers(12450)["value"] == "(x-2)^2+y^2=25"
    # 隨堂練習1 (x+1)^2+y^2=5, k=4 ; 隨堂練習2 k=8, B(6,-1)
    assert _answers(12451) == {"part_1": "(x+1)^2+y^2=5", "part_2": "4"}
    assert _answers(12452) == {"part_1": "8", "part_2": "(6,-1)"}
    # 例題3 centre (1,-3), r=2 ; 例題4 (x+1)^2+(y-2)^2=0 point / =-5 none
    assert _answers(12453) == {"part_1": "(1,-3)", "part_2": "2"}
    a = _answers(12454)
    assert a["part_1"] == "(x+1)^2+(y-2)^2=0" and a["part_3"] == "(x+1)^2+(y-2)^2=-5"
    # 例題5 k<5 ; 習題基礎5 k>5
    assert _answers(12455)["value"] == "k<5" and _answers(12463)["value"] == "k>5"
    # 例題6 (x-8)^2+y^2=16 ; 隨堂練習6 (x+2)^2+y^2=16
    assert _answers(12456)["value"] == "(x-8)^2+y^2=16" and _answers(12461)["value"] == "(x+2)^2+y^2=16"
    # 例題7: PA:PB=5:3, circle centre (25,0), r=15
    a = _answers(12457)
    assert (a["part_1"], a["part_2"], a["part_4"], a["part_5"]) == ("5", "3", "(25,0)", "15")
    # 隨堂練習3 k=-4 ; 隨堂練習5 k in {4,-2} centres (-1,4),(-1,-2) ; 習題基礎3 a=-2,b=6,r=4
    assert _answers(12458)["value"] == "-4"
    a = _answers(12460)
    assert sorted(a["part_1"]) == ["-2", "4"] and (a["part_2"], a["part_3"]) == ("(-1,4)", "(-1,-2)")
    assert _answers(12462) == {"part_1": "-2", "part_2": "6", "part_3": "4"}
    # 隨堂練習4 circle / point / none
    labels = [c["label"] for c in _source(12459)["answer_contract"]["parts"][0]["choices"]]
    assert [_answers(12459)[f"part_{i}"] for i in (1, 2, 3)] == ["1", "2", "3"] and labels == ["1", "2", "3"]
    # 例題8 on / inside / outside ; 例題9 max 6 min 4 ; 隨堂練習8 max 11 min 1 ; 習題基礎4 outside, min 2
    assert [_answers(12464)[f"part_{i}"] for i in (1, 2, 3)] == ["3", "1", "2"]
    assert _answers(12465) == {"part_1": "6", "part_2": "4"}
    assert _answers(12468) == {"part_1": "11", "part_2": "1"}
    assert _answers(12477) == {"part_1": "2", "part_2": "2"}
    # 例題10: (1) option 3, (2) (x-3)^2+y^2=8, (3) 12 pi ; 隨堂練習7 5<k<18 ; 隨堂練習9 (x-3)^2+y^2=25 / (x-11)^2+y^2=25
    assert _answers(12466) == {"part_1": "3", "part_2": "(x-3)^2+y^2=8", "part_3": "12*pi"}
    assert _answers(12467)["value"] == "5<k<18"
    assert _answers(12469) == {"part_1": "(x-3)^2+y^2=25", "part_2": "(x-11)^2+y^2=25"}
    # 觀念澄清: (1) x (2) x (3) o (4) x (5) o
    assert [_source(c)["correct_answer"] for c in (12470, 12471, 12472, 12473, 12474)] == ["B", "B", "A", "B", "A"]
    # 習題基礎1 (centre, radius) x3 ; 基礎2 ; 進階7 ; 進階8 PR=4 ; 進階6 option 3 (隔天上午6時)
    assert _answers(12475) == {"part_1": "(1,0)", "part_2": "2", "part_3": "(0,2)", "part_4": "1", "part_5": "(1/3,0)", "part_6": "2"}
    assert _answers(12476) == {"part_1": "(x+1)^2+(y+1)^2=13", "part_2": "(x+1)^2+(y-2)^2=25", "part_3": "(x-4)^2+y^2=25"}
    assert _answers(12479) == {"part_1": "x-y+4=0", "part_2": "4x+3y-26=0", "part_3": "(x-2)^2+(y-6)^2=25"}
    assert _answers(12480)["value"] == "4"
    payload = _source(12478)
    assert payload["correct_answer"] == "3" and [c["value"] for c in payload["answer_contract"]["choices"]][2] == "隔天上午6時"


def test_stems_carry_the_source_numbers_at_variant_zero():
    assert "460" in _source(12478)["question_text"] and "80" in _source(12478)["question_text"] and "25" in _source(12478)["question_text"]
    text = _source(12457)["question_text"]
    assert "16" in text and "3" in text and "5" in text and "如圖" in text
    text = _source(12474)["question_text"]
    assert "2\\pi" in text  # the Symbol-font pi that the importer dropped
    arch = _source(12480)
    assert arch["visual_spec"]["circles"] and {p["label"] for p in arch["visual_spec"]["points"]} == {"Q", "A", "P", "B", "R"}


def test_radical_and_pi_answers_accept_equivalent_forms():
    payload = _source(12466)
    skill_id = SKILLS["pc"]
    base = dict(payload["correct_answer"])
    for good in ("12π", "12\\pi", "12*pi"):
        assert _grade(payload, {**base, "part_3": good}, skill_id), good
    for bad in ("12", "24π", "37.7"):
        assert not _grade(payload, {**base, "part_3": bad}, skill_id), bad
    equation = _source(12450)
    for good in ("x^2-4x+y^2-21=0", "(x-2)^2+y^2=25", "25=(x-2)^2+y^2"):
        assert _grade(equation, good, SKILLS["std"]), good
    for bad in ("(x-2)^2+y^2=16", "(x+2)^2+y^2=25", "x^2+y^2=25"):
        assert not _grade(equation, bad, SKILLS["std"]), bad
    ineq = _source(12455)
    for good in ("k<5", "5>k", "k < 5"):
        assert _grade(ineq, good, SKILLS["gen"]), good
    for bad in ("k>5", "k<=5", "k<6"):
        assert not _grade(ineq, bad, SKILLS["gen"]), bad


def test_variants_never_change_the_answer_topology():
    for cid, (skill_key, operation, source, sampler) in COMPONENTS.items():
        generator = _load(SKILLS[skill_key], cid, "generate.py")
        shapes = {json.dumps(sorted((generator.generate(seed=s)["answer_contract"]["answer_type"],
                                     len(generator.generate(seed=s)["answer_contract"].get("parts", [])))
                                    for _ in [0]))
                  for s in SEEDS}
        assert len(shapes) == 1, (cid, shapes)
