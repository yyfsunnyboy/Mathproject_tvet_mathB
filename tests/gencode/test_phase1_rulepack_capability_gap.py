# -*- coding: utf-8 -*-
"""Phase 1 rule packs must surface missing capability as NEEDS_CAPABILITY, never as resolvable or skip."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
import yaml

import core.gencode.pipeline_orchestrator as po
from core.gencode.services.v3_example_disposition import (
    DISPOSITION_INTENTIONAL_SKIP,
    DISPOSITION_NEEDS_CAPABILITY,
    DISPOSITION_RESOLVABLE,
    disposition_from_phase1_probe,
)
from core.gencode.services.v3_skill_capability_preflight_service import evaluate_skill_v3_capability

POINT = "gh_PointDivisionFormulaOnNumberLine"
DIVISION = "evaluate_number_line_division_points"
STATEMENTS = "evaluate_absolute_value_statements"
DRAWING = "number_line_drawing"


def _pt(pid, *, runtime=True):
    return {
        "problem_type_id": pid,
        "display_name": pid,
        "checker": "multi_part_answer_checker" if runtime else "manual_review_checker",
        "equivalence": "rational_exact" if runtime else "manual_review_or_ai_judged",
        "runtime_candidate": runtime,
        "requires_human_action": not runtime,
    }


def _pack(source_examples):
    return {
        "skill_id": POINT,
        "skill_ch_name": "test",
        "classifier_source": "test",
        "problem_types": [_pt(DIVISION), _pt(STATEMENTS), _pt(DRAWING, runtime=False)],
        "classification_rules": [],
        "source_examples": source_examples,
    }


@pytest.fixture()
def rulepack(tmp_path: Path, monkeypatch):
    def install(source_examples):
        path = tmp_path / "phase1_rule_packs.yaml"
        path.write_text(yaml.safe_dump({"version": 1, "skills": [_pack(source_examples)]}, allow_unicode=True),
                        encoding="utf-8")
        monkeypatch.setattr(po, "CLASSIFIER_RULEPACK_PATH", path)
        return path

    return install


def _conn(ids):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE textbook_examples (id INTEGER PRIMARY KEY, skill_id TEXT, problem_text TEXT, correct_answer TEXT, "
        "detailed_solution TEXT, source_description TEXT, problem_type TEXT, notes TEXT)"
    )
    for eid in ids:
        conn.execute(
            "INSERT INTO textbook_examples VALUES (?, ?, ?, '', '', ?, 'basic_exercise', '')",
            (eid, POINT, f"設數線上兩點 A(1)、B({eid})，求 AB 的長。", f"src_{eid}"),
        )
    conn.commit()
    return conn


def _phase1(conn, eid):
    row = dict(conn.execute("SELECT * FROM textbook_examples WHERE id = ?", (eid,)).fetchone())
    return po.run_v3_no_llm_phase1_for_example(POINT, row, conn=conn)


def _probe(result):
    return disposition_from_phase1_probe({
        "textbook_example_id": result["textbook_example_id"],
        "resolvable": result["classification_status"] == "resolved" and bool(result["problem_type_id"]),
        "reason": result.get("reason", ""),
        "classification_source": result.get("classification_source", ""),
        "problem_type_id": result.get("problem_type_id", ""),
    })


def test_bound_operation_resolves(rulepack):
    rulepack([{"example_id": 1, "matched_problem_type_id": DIVISION}])
    result = _phase1(_conn([1]), 1)
    assert result["classification_status"] == "resolved"
    assert result["classification_source"] == "phase1_rule_pack"
    assert _probe(result)["disposition"] == DISPOSITION_RESOLVABLE


def test_operation_not_bound_to_skill_needs_capability(rulepack):
    rulepack([{"example_id": 2, "matched_problem_type_id": STATEMENTS}])
    result = _phase1(_conn([2]), 2)
    assert result["classification_status"] == "unresolved"
    assert result["classification_source"] == "phase1_rule_pack_needs_capability"
    assert result["reason"] == f"NEEDS_CAPABILITY:domain_operation_not_bound_to_skill:{STATEMENTS}"
    assert _probe(result)["disposition"] == DISPOSITION_NEEDS_CAPABILITY


def test_explicit_needs_capability_is_not_an_intentional_skip(rulepack):
    rulepack([{"example_id": 3, "matched_problem_type_id": DIVISION, "needs_capability": "symbolic_point_distance"}])
    result = _phase1(_conn([3]), 3)
    assert result["classification_status"] == "unresolved"
    assert result["reason"] == "NEEDS_CAPABILITY:symbolic_point_distance"
    assert "BLOCKED:" not in result["reason"]
    assert _probe(result)["disposition"] == DISPOSITION_NEEDS_CAPABILITY


def test_blocked_problem_type_stays_intentional_skip(rulepack):
    rulepack([{"example_id": 4, "matched_problem_type_id": DRAWING, "block_reason": "drawing_not_gradable"}])
    result = _phase1(_conn([4]), 4)
    assert result["classification_source"] == "phase1_rule_pack_blocked"
    assert _probe(result)["disposition"] == DISPOSITION_INTENTIONAL_SKIP


def test_binding_gap_ignores_unbound_skills_and_non_operation_types():
    assert po._rulepack_operation_binding_gap("no_such_skill_for_test", STATEMENTS) == ""
    assert po._rulepack_operation_binding_gap(POINT, "some_problem_type_label") == ""
    assert po._rulepack_operation_binding_gap(POINT, DIVISION) == ""


def test_preflight_reports_needs_capability_until_every_eligible_example_resolves(rulepack):
    conn = _conn([11, 12, 13])
    rulepack([
        {"example_id": 11, "matched_problem_type_id": DIVISION},
        {"example_id": 12, "matched_problem_type_id": DRAWING, "block_reason": "drawing_not_gradable"},
        {"example_id": 13, "matched_problem_type_id": STATEMENTS},
    ])
    report = evaluate_skill_v3_capability(conn, POINT)
    assert report["capability_status"] == "needs_capability"
    assert report["allow_v3_rebuild"] is False
    assert report["needs_capability_ids"] == [13]
    assert report["intentional_skip_count"] == 1

    rulepack([
        {"example_id": 11, "matched_problem_type_id": DIVISION},
        {"example_id": 12, "matched_problem_type_id": DRAWING, "block_reason": "drawing_not_gradable"},
        {"example_id": 13, "matched_problem_type_id": DIVISION},
    ])
    assert evaluate_skill_v3_capability(conn, POINT)["capability_status"] == "ready"
