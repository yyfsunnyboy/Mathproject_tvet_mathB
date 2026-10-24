"""Isolated sandbox gate for the five Unit 9 parabola-drawing items (revision-2 candidate, parabola_graph grader).

Builds into ``tmp/gh_unit9_drawing_dryrun`` only.  Grading of the canvases uses the formal evaluator on synthetic
analyzer features / a deterministic vision stand-in; the real vision model is reported separately.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from unittest import mock

import pytest

from agent_domains_candidate.function_linear_quadratic import build_sandbox as B
from agent_domains_candidate.function_linear_quadratic.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.function_linear_quadratic.unit9_specs import DRAWING_COMPONENTS, HELD_UNTIL_REAL_AI, OP, SKILLS
from agent_domains_candidate.function_linear_quadratic.verification import _drawing_value, equivalent_value, grade, verify_payload, wrong_value
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = PROJECT_ROOT / "tmp" / "gh_unit9_drawing_dryrun"
SEEDS = range(20)
register_candidate_in_memory()
B.build_all(components=DRAWING_COMPONENTS, dryrun=DRYRUN)
SKILL = SKILLS["quad"]
SHAPES = {  # component -> (answer_type, canvases, text parts)
    12567: ("drawing", 1, 0), 12568: ("drawing", 1, 0), 12570: ("multi_part", 1, 2), 12576: ("multi_part", 2, 0), 12587: ("multi_part", 2, 4),
}


def _load(cid: int, filename: str):
    path = DRYRUN / SKILL / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"u9d_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gen(cid: int, seed: int = 0) -> dict:
    return _load(cid, "generate.py").generate(seed=seed)


@pytest.mark.parametrize("cid", sorted(DRAWING_COMPONENTS))
def test_component_contract_canvases_and_parts(cid):
    directory = DRYRUN / SKILL / "components" / f"src_{cid}"
    assert {p.name for p in directory.iterdir() if p.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    assert (directory / "get_hint.py").read_text(encoding="utf-8") == _build_get_hint_py()
    answer_type, canvases, text_parts = SHAPES[cid]
    surfaces = set()
    for seed in SEEDS:
        payload = _gen(cid, seed)
        assert payload == _gen(cid, seed) and payload["fixed_domain_key"] == "function.linear_quadratic"
        contract = payload["answer_contract"]
        assert contract["answer_type"] == answer_type
        assert verify_payload(payload, SKILL, f"src_{cid}") == [], (seed, payload["question_text"][:50])
        parts = contract.get("parts") or []
        drawing_parts = [p for p in parts if p["answer_type"] == "drawing"] if parts else [contract]
        assert len(drawing_parts) == canvases and len(parts) - (len(drawing_parts) if parts else 0) == text_parts
        for part in drawing_parts:
            spec = part["expected_drawing_spec"]
            assert spec["drawing_type"] == "parabola_graph" and spec["expected_parabolas"]
            rng = spec["axis_range"]
            for e in spec["expected_parabolas"]:  # the canvas shows every expected vertex
                assert rng["x_min"] <= e["vertex"][0] <= rng["x_max"] and rng["y_min"] <= e["vertex"][1] <= rng["y_max"]
                assert all(abs(y - (e["a"] * (x - e["vertex"][0]) ** 2 + e["vertex"][1])) < 1e-9 for x, y in e["points"])
        surfaces.add(json.dumps([payload["question_text"], payload["correct_answer"]], sort_keys=True, ensure_ascii=False, default=str))
    assert len(surfaces) >= 18


def test_spec_counts_follow_the_source_layout():
    assert len(_gen(12568)["answer_contract"]["expected_drawing_spec"]["expected_parabolas"]) == 3      # three curves, one canvas
    assert [len(p["expected_drawing_spec"]["expected_parabolas"]) for p in _gen(12576)["answer_contract"]["parts"]] == [1, 1]  # (a) and (b)
    labels = [p["label"] for p in _gen(12587)["answer_contract"]["parts"]]
    assert labels == ["(1) 圖形", "(1) 頂點", "(1) 對稱軸", "(2) 圖形", "(2) 頂點", "(2) 對稱軸"]


def _fake(*, image_data_url, expected_drawing_spec, **_kw):
    if not image_data_url:
        return {"is_correct": None, "system_error": True, "status": "missing_image"}
    return {"is_correct": "GOOD" in image_data_url, "system_error": False, "status": "success"}


@pytest.mark.parametrize("cid", [12570, 12587])
def test_graph_and_text_answers_are_both_required(cid):
    payload = _gen(cid)
    contract = payload["answer_contract"]
    good = {p["key"]: (_drawing_value("GOOD") if p["answer_type"] == "drawing" else p["expected_answer"]) for p in contract["parts"]}
    with mock.patch("core.checkers.free_response_drawing_checker.check_drawing_answer", side_effect=_fake):
        assert grade(payload, good, SKILL)
        for part in contract["parts"]:
            bad = dict(good)
            bad[part["key"]] = _drawing_value("BAD") if part["answer_type"] == "drawing" else wrong_value(part)
            assert not grade(payload, bad, SKILL), part["key"]       # right graph + wrong text, or wrong graph + right text
        for part in contract["parts"]:
            if part["answer_type"] != "drawing" and equivalent_value(part) is not None:
                alt = dict(good)
                alt[part["key"]] = equivalent_value(part)
                assert grade(payload, alt, SKILL)                      # equivalent vertex / axis renderings are accepted


def test_12568_stays_held_until_the_real_model_is_shown_to_read_three_curves():
    assert 12568 in HELD_UNTIL_REAL_AI and 12568 in DRAWING_COMPONENTS
