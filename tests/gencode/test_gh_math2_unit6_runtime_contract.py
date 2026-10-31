"""Unit 6 runtime gate: every multi-part item exposes one answer field per stem item (VOCATIONAL_PRACTICE_RUNTIME_CONTRACT §9.4).

Loads the existing staging generators (no rebuild, no DB write) and grades with the shared runtime checker.
The live-route evidence comes from ``reports/gh_math2_unit6_bundle/isolated_server.py api`` (Flask test client on a DB copy).
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from agent_domains_candidate.classical_probability.classical_probability_specs import COMPONENTS, FAMILY, SKILLS
from agent_domains_candidate.classical_probability.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.classical_probability.verification import grade, wrong_value
from core.gencode.multipart_answer_arity import (
    checker_answer_count,
    expected_answer_field_count,
    rendered_answer_field_count,
)
from core.gencode.multipart_stem_contract import extract_stem_structure, stem_structure_to_question_text

ROOT = Path(__file__).resolve().parents[2]
DRYRUN = ROOT / "tmp" / "gh_math2_unit6_sandbox_dryrun"
API_REPORT = ROOT / "reports" / "gh_math2_unit6_bundle" / "runtime_api_report.json"
SEEDS = range(10)

register_candidate_in_memory()
_MODULES: dict[int, object] = {}


def _skill(cid: int) -> str:
    return SKILLS[COMPONENTS[cid][0]]


def _payload(cid: int, seed: int) -> dict:
    if cid not in _MODULES:
        path = DRYRUN / _skill(cid) / "components" / f"src_{cid}" / "generate.py"
        spec = importlib.util.spec_from_file_location(f"u6rt_{cid}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[cid] = module
    return _MODULES[cid].generate(seed=seed)


def _correct_input(part: dict):
    if part.get("input_type") == "select":
        return next(c["value"] for c in part["choices"] if c["label"] == part["expected_answer"])
    return part["expected_answer"]


def test_inventory_is_42_components_over_14_families():
    assert len(COMPONENTS) == 42
    assert len(set(FAMILY.values())) == 14
    assert {_skill(cid) for cid in COMPONENTS} == set(SKILLS.values())


@pytest.mark.parametrize("cid", sorted(COMPONENTS))
def test_answer_fields_match_stem_items_and_grade_per_part(cid):
    skill = _skill(cid)
    for seed in SEEDS:
        payload = _payload(cid, seed)
        contract = payload["answer_contract"]
        n = expected_answer_field_count(payload)
        assert n == rendered_answer_field_count(payload) == checker_answer_count(payload), (cid, seed)
        if contract["answer_type"] != "multi_part":
            assert n == 1 and "stem_structure" not in payload, (cid, seed)
            assert grade(payload, payload["correct_answer"], skill), (cid, seed)
            continue
        parts = contract["parts"]
        stem = extract_stem_structure(payload)
        assert stem is not None and payload["metadata"]["stem_structure"] == stem, (cid, seed)
        labels = [f"({i})" for i in range(1, n + 1)]
        assert [item["group_label"] for item in stem["items"]] == labels, (cid, seed)
        assert all(item["text"].strip() for item in stem["items"]), (cid, seed)
        assert [p["group_label"] for p in parts] == labels, (cid, seed)
        assert [p["answer_order"] for p in parts] == list(range(n)), (cid, seed)
        assert payload["question_text"] == stem_structure_to_question_text(stem), (cid, seed)
        for part in parts:
            if part["checker"] == "choice_label_checker":
                assert part["input_type"] == "select" and part["choices"], (cid, seed, part["key"])
        answer = {p["key"]: _correct_input(p) for p in parts}
        assert grade(payload, answer, skill), (cid, seed)
        for part in parts:
            wrong = {**answer, part["key"]: wrong_value(part)}
            assert not grade(payload, wrong, skill), (cid, seed, part["key"])


def test_isolated_route_evidence_has_no_load_error_or_fallback():
    if not API_REPORT.exists():
        pytest.skip("run reports/gh_math2_unit6_bundle/isolated_server.py api first")
    report = json.loads(API_REPORT.read_text(encoding="utf-8"))
    rows = [row for skill_rows in report["skills"].values() for row in skill_rows.values()]
    assert report["failures"] == 0 and len(rows) == 42
    assert {row["route_mode"] for row in rows} == {"v3"}
    assert not any(row["load_error"] or row["leaks_answer"] for row in rows)
    assert all(row["correct_accepted"] and row["wrong_rejected"] for row in rows)
