# -*- coding: utf-8 -*-
"""Batch regression for chapter dynamic practice across B1-B4 (metadata + scheduler only)."""

from __future__ import annotations

import functools
import importlib

import pytest

from core import practice_type_rotation as ptr
from scripts import audit_practice_type_rotation as audit

CURRICULUM_DB = audit.ROOT / "instance" / "kumon_math.db"
pytestmark = pytest.mark.skipif(not CURRICULUM_DB.is_file(), reason="curriculum DB not available")


@functools.lru_cache(maxsize=1)
def _report() -> dict:
    return audit.run_audit(smoke=False, db_path=CURRICULUM_DB)


def _ready_ids() -> list[str]:
    if not CURRICULUM_DB.is_file():
        return []
    return [s["skill_id"] for s in _report()["sections"] if s["status"] == "READY"]


def _section(skill_id: str) -> dict:
    return next(s for s in _report()["sections"] if s["skill_id"] == skill_id)


@pytest.mark.parametrize("skill_id", _ready_ids())
def test_ready_section_pool_matches_problem_type_ids(skill_id: str) -> None:
    module = importlib.import_module(f"skills.{skill_id}")
    specs = ptr._runtime_specs(module)
    problem_types = [str(s.get("problem_type_id") or "").strip() for s in specs]
    assert specs and all(problem_types)

    pool = ptr.load_section_pool(skill_id, module=module)
    assert pool["reliable"]
    types = ptr.get_practice_type_pool(skill_id, module=module)
    assert len(types) == len(set(problem_types))
    assert all(types.values())

    sched = audit.scheduler_smoke(skill_id, types)
    assert sched["ok"], sched["errors"]
    assert sched["first_round_size"] == len(set(problem_types))


def test_first_round_size_is_driven_by_unique_types() -> None:
    ready = [s for s in _report()["sections"] if s["status"] == "READY"]
    assert ready
    sizes = {s["scheduler"]["first_round_size"] for s in ready}
    assert len(sizes) > 2
    for s in ready:
        assert s["scheduler"]["first_round_size"] == s["unique_types"]
        if sum(len(v) for v in s["type_candidates"].values()) > s["unique_types"]:
            assert s["scheduler"]["first_round_size"] < s["components"]


def test_published_ready_components_never_miss_problem_type_id() -> None:
    for s in _report()["sections"]:
        if s["status"] == "READY":
            assert s["missing_problem_type_id"] == 0, s["skill_id"]
            assert set(s["type_key_sources"]) == {"problem_type_id"}, s["skill_id"]


def test_progression_stays_inside_chapter_and_ends_with_completion() -> None:
    report = _report()
    assert not [i for i in report["progression"]["issues"]
                if i["code"] in {"chapter_boundary_leak", "runtime_next_targets_non_ready_section"}]
    chapter_of = {(s["skill_id"]): (s["volume"], s["chapter"]) for s in report["sections"]}
    for ch in report["progression"]["chapters"]:
        for t in ch["transitions"]:
            if t["next"]:
                assert chapter_of[t["next"]] == (ch["volume"], ch["chapter"])
        if ch["ready_sequence"]:
            assert ch["chapter_end_next"] == ""
            assert ch["chapter_completion_reachable"]


@pytest.mark.parametrize(
    "skill_id,component_id",
    [
        ("vh_數學B2_SubSection_3_2_2", "src_11821"),
        ("vh_數學B2_SubSection_3_3_5", "src_11795"),
    ],
)
def test_previously_undeliverable_single_candidate_types_generate(skill_id: str, component_id: str) -> None:
    module = importlib.import_module(f"skills.{skill_id}")
    for seed in range(12):
        payload = module.generate(level=1, seed=seed, component_id=component_id)
        values = [c.get("value") for c in payload.get("choices") or []]
        assert len(values) == 4 and len(set(values)) == 4


def test_sample_variance_and_sd_multi_part_accepts_rounded_answer() -> None:
    import logging

    from core.gencode.answer_grading import grade_answer_for_current_question

    skill_id = "vh_數學B4_VarianceAndStandardDeviation"
    module = importlib.import_module(f"skills.{skill_id}")
    for seed in range(6):
        payload = module.generate(level=1, seed=seed, component_id="src_3851")
        parts = (payload.get("answer_contract") or {}).get("parts") or []
        assert [p["key"] for p in parts] == ["sample_variance", "sample_standard_deviation"]
        answer = {p["key"]: str(p["expected_answer"]) for p in parts}
        assert all(len(v.split(".")[-1]) <= 2 for v in answer.values() if "." in v)
        result = grade_answer_for_current_question(answer, payload, skill_id, log=logging.getLogger(__name__))
        assert result and result.get("correct") is True


@pytest.mark.parametrize(
    "skill_id,component_id",
    [
        ("vh_數學B4_VarianceAndStandardDeviation", "src_3848"),
        ("vh_數學B4_VarianceAndStandardDeviation", "src_3849"),
        ("vh_數學B4_HistogramsAndFrequencyPolygons", "src_3826"),
        ("vh_數學B4_HistogramsAndFrequencyPolygons", "src_3827"),
        ("vh_數學B4_HistogramsAndFrequencyPolygons", "src_3828"),
    ],
)
def test_route_session_delivers_and_accepts_displayed_answer(skill_id: str, component_id: str) -> None:
    module = importlib.import_module(f"skills.{skill_id}")
    for seed in range(6):
        payload = module.generate(level=1, seed=seed, component_id=component_id)
        session, err = audit._route_session(payload, skill_id)
        assert not err, err
        assert audit._self_grade(session, skill_id) == ""


def test_acute_constraint_choice_is_deliverable_and_graded_by_label() -> None:
    skill_id = "vh_數學B2_FundamentalTrigonometricIdentities"
    module = importlib.import_module(f"skills.{skill_id}")
    correct_labels = set()
    for seed in range(8):
        payload = module.generate(level=1, seed=seed, component_id="src_11585")
        session, err = audit._route_session(payload, skill_id)
        assert not err, err
        verdicts = {c["label"]: audit._grade_once(c["label"], session, skill_id) for c in session["choices"]}
        correct = [label for label, e in verdicts.items() if e == ""]
        assert len(correct) == 1
        correct_labels.update(correct)
    assert len(correct_labels) > 1
