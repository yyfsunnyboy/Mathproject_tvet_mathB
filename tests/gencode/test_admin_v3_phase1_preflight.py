# -*- coding: utf-8 -*-
"""Admin V3 regenerate must run Phase 1 preflight before Phase 2."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest

from core.gencode.pipeline_orchestrator import (
    PHASE1_CLASSIFICATION_UNRESOLVED,
    _compute_v3_example_source_hash,
    resolve_v3_admin_induced_spec,
    run_v3_no_llm_phase1_for_example,
)
from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_example
from core.gencode.services.component_tracker_service import save_tracker_record

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
REGISTERED_SKILL = "vh_數學B1_HorizontalAndVerticalLineEquations"
UNKNOWN_SKILL = "vh_數學B4_NewSkill_NotInRegistry_Phase1"


def _memory_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            problem_type TEXT,
            problem_type_id TEXT,
            line_type TEXT,
            problem_text TEXT,
            correct_answer TEXT,
            detailed_solution TEXT,
            explanation TEXT,
            source_description TEXT,
            question_type TEXT
        )
        """
    )
    apply_tracker_ddl(conn)


@pytest.fixture
def memory_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    _memory_schema(conn)
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def dryrun_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_phase1_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


def _insert_example(
    conn: sqlite3.Connection,
    *,
    example_id: int,
    skill_id: str,
    problem_text: str,
    correct_answer: str = "3",
    problem_type: str = "mixed_counting",
) -> None:
    conn.execute(
        """
        INSERT INTO textbook_examples
            (id, skill_id, problem_type, problem_text, correct_answer, detailed_solution)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (example_id, skill_id, problem_type, problem_text, correct_answer, ""),
    )
    conn.commit()


def _resolved_spec(example_id: int, skill_id: str, row: dict) -> dict:
    spec = run_v3_no_llm_phase1_for_example(skill_id, row, conn=None)
    assert spec.get("classification_status") == "resolved"
    return spec


def test_admin_regenerate_invokes_phase1_before_phase2(memory_conn, dryrun_root):
    example_id = 990101
    problem_text = "試求下列資料的平均數：1, 3, 2, 5, 4"
    _insert_example(
        memory_conn,
        example_id=example_id,
        skill_id=UNKNOWN_SKILL,
        problem_text=problem_text,
    )
    row = dict(
        memory_conn.execute("SELECT * FROM textbook_examples WHERE id = ?", (example_id,)).fetchone()
    )

    phase2_calls: list[dict] = []

    def _phase2_stub(skill_id, **kwargs):
        phase2_calls.append({"skill_id": skill_id, **kwargs})
        return {
            "phase_status": "V3_SHADOW_BRIDGE",
            "tracker_status": "failed",
            "v3_shadow_bridge": {
                "generation_finished_at": "2026-01-01T00:00:00",
                "model_generation_invoked": True,
            },
        }

    with patch("core.gencode.services.admin_gencode_action_service.run_gencode_phase2_raw", side_effect=_phase2_stub):
        result = run_admin_v3_dryrun_for_example(
            conn=memory_conn,
            textbook_example_id=example_id,
            skill_id=UNKNOWN_SKILL,
            dryrun_base_dir=str(dryrun_root),
            allow_non_mvp_skill=True,
            force_regenerate=True,
        )

    assert result.get("phase1_preflight", {}).get("phase1_invoked") is True
    assert phase2_calls, "Phase 2 must be invoked after Phase 1"
    induced = phase2_calls[0].get("v3_induced_spec")
    assert isinstance(induced, dict)
    assert induced.get("problem_type_id")
    assert induced.get("required_capabilities")
    assert induced.get("classification_source")
    assert induced.get("problem_type_id") != "mixed_counting"


def test_reuses_existing_induced_spec_without_rerunning_phase1(memory_conn, dryrun_root):
    example_id = 990102
    problem_text = "試求下列資料的中位數：5, 7, 2, 8, 3"
    _insert_example(
        memory_conn,
        example_id=example_id,
        skill_id=UNKNOWN_SKILL,
        problem_text=problem_text,
    )
    row = dict(
        memory_conn.execute("SELECT * FROM textbook_examples WHERE id = ?", (example_id,)).fetchone()
    )
    source_hash = _compute_v3_example_source_hash(row)
    cached = {
        "classification_status": "resolved",
        "skill_id": UNKNOWN_SKILL,
        "source_example_id": example_id,
        "textbook_example_id": example_id,
        "source_hash": source_hash,
        "problem_type_id": "median_computation",
        "required_capabilities": ["median"],
        "classification_source": "test_fixture",
        "presentation_mode": "short_answer",
        "answer_contract": {"answer_type": "integer"},
    }
    save_tracker_record(
        memory_conn,
        textbook_example_id=example_id,
        skill_id=UNKNOWN_SKILL,
        gencode_status="failed",
        induced_spec_payload={"phase1_classification": cached},
        gencode_error_log="previous_failure",
    )
    memory_conn.commit()

    phase1_spy = patch(
        "core.gencode.pipeline_orchestrator.run_v3_no_llm_phase1_for_example"
    )
    phase2_stub = patch(
        "core.gencode.services.admin_gencode_action_service.run_gencode_phase2_raw",
        return_value={
            "phase_status": "V3_SHADOW_BRIDGE",
            "tracker_status": "failed",
            "v3_shadow_bridge": {"model_generation_invoked": False},
        },
    )

    with phase1_spy as phase1_mock, phase2_stub as phase2_mock:
        result = run_admin_v3_dryrun_for_example(
            conn=memory_conn,
            textbook_example_id=example_id,
            skill_id=UNKNOWN_SKILL,
            dryrun_base_dir=str(dryrun_root),
            allow_non_mvp_skill=True,
        )
        phase1_mock.assert_not_called()
        assert phase2_mock.called
        induced = phase2_mock.call_args.kwargs.get("v3_induced_spec")
        assert induced["problem_type_id"] == "median_computation"
        assert induced["classification_source"] == "test_fixture"

    assert result["phase1_preflight"]["reused"] is True


def test_source_hash_change_invalidates_cached_spec(memory_conn):
    example_id = 990103
    _insert_example(
        memory_conn,
        example_id=example_id,
        skill_id=UNKNOWN_SKILL,
        problem_text="試求平均數：1, 2, 3",
    )
    row = dict(
        memory_conn.execute("SELECT * FROM textbook_examples WHERE id = ?", (example_id,)).fetchone()
    )
    old_hash = _compute_v3_example_source_hash(row)
    save_tracker_record(
        memory_conn,
        textbook_example_id=example_id,
        skill_id=UNKNOWN_SKILL,
        gencode_status="failed",
        induced_spec_payload={
            "phase1_classification": {
                "classification_status": "resolved",
                "source_hash": old_hash,
                "problem_type_id": "arithmetic_mean_computation",
                "required_capabilities": ["arithmetic_mean"],
                "classification_source": "stale",
            }
        },
        gencode_error_log="stale",
    )
    memory_conn.commit()

    memory_conn.execute(
        "UPDATE textbook_examples SET problem_text = ? WHERE id = ?",
        ("試求下列資料的眾數：1, 2, 2, 3", example_id),
    )
    memory_conn.commit()

    preflight = resolve_v3_admin_induced_spec(
        memory_conn,
        UNKNOWN_SKILL,
        example_id,
        force_regenerate=False,
    )
    assert preflight["ok"] is True
    assert preflight["reused"] is False
    assert preflight["phase1_invoked"] is True
    assert preflight["induced_spec"]["classification_source"] != "stale"
    assert "mode" in preflight["induced_spec"]["problem_type_id"]


def test_phase1_unresolved_blocks_phase2(memory_conn, dryrun_root):
    example_id = 990104
    _insert_example(
        memory_conn,
        example_id=example_id,
        skill_id=UNKNOWN_SKILL,
        problem_text="請閱讀本題敘述並回答。",
        correct_answer="unknown",
    )

    with patch(
        "core.gencode.services.admin_gencode_action_service.run_gencode_phase2_raw"
    ) as phase2_mock:
        result = run_admin_v3_dryrun_for_example(
            conn=memory_conn,
            textbook_example_id=example_id,
            skill_id=UNKNOWN_SKILL,
            dryrun_base_dir=str(dryrun_root),
            allow_non_mvp_skill=True,
        )
        phase2_mock.assert_not_called()

    assert result["status"] == "needs_human_review"
    assert result["error_code"] == PHASE1_CLASSIFICATION_UNRESOLVED
    tracker = memory_conn.execute(
        "SELECT gencode_status, gencode_error_log, induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id = ?",
        (example_id,),
    ).fetchone()
    assert tracker["gencode_status"] == "needs_human_review"
    assert PHASE1_CLASSIFICATION_UNRESOLVED in str(tracker["gencode_error_log"])


def test_no_gemini_calls_during_admin_preflight(memory_conn, dryrun_root):
    example_id = 990105
    _insert_example(
        memory_conn,
        example_id=example_id,
        skill_id=UNKNOWN_SKILL,
        problem_text="計算平均數：10, 20, 30",
    )

    with (
        patch("core.ai_wrapper.call_ai_with_retry") as ai_retry,
        patch("core.ai_wrapper.get_ai_client") as ai_client,
        patch(
            "core.gencode.services.admin_gencode_action_service.run_gencode_phase2_raw",
            return_value={
                "phase_status": "V3_SHADOW_BRIDGE",
                "tracker_status": "failed",
                "v3_shadow_bridge": {"model_generation_invoked": False},
            },
        ),
    ):
        run_admin_v3_dryrun_for_example(
            conn=memory_conn,
            textbook_example_id=example_id,
            skill_id=UNKNOWN_SKILL,
            dryrun_base_dir=str(dryrun_root),
            allow_non_mvp_skill=True,
            force_regenerate=True,
        )
        ai_retry.assert_not_called()
        ai_client.assert_not_called()


def test_registered_skill_still_completes_dryrun(memory_conn, dryrun_root):
    example_id = 4544
    memory_conn.execute(
        """
        INSERT INTO textbook_examples
            (id, skill_id, problem_type_id, line_type, problem_text, correct_answer, detailed_solution)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            example_id,
            REGISTERED_SKILL,
            "vertical_line",
            "vertical_line",
            "過點 (2, 3) 且垂直於 x 軸的直線方程式為何？",
            "x=2",
            "",
        ),
    )
    memory_conn.commit()

    result = run_admin_v3_dryrun_for_example(
        conn=memory_conn,
        textbook_example_id=example_id,
        skill_id=REGISTERED_SKILL,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
        allow_non_mvp_skill=True,
        force_regenerate=True,
    )

    assert result["status"] in {"draft_written", "smoke_passed", "verified", "failed"}
    assert result.get("phase1_preflight", {}).get("induced_spec", {}).get("problem_type_id")
    generate_path = dryrun_root / REGISTERED_SKILL / "components" / f"src_{example_id}" / "generate.py"
    assert generate_path.is_file()


def test_domain_failure_preserves_phase1_trace(memory_conn, dryrun_root):
    example_id = 990106
    _insert_example(
        memory_conn,
        example_id=example_id,
        skill_id=UNKNOWN_SKILL,
        problem_text="試求平均數：4, 5, 6, 7",
    )

    def _phase2_domain_failure(skill_id, **kwargs):
        phase1 = kwargs["v3_induced_spec"]
        save_tracker_record(
            memory_conn,
            textbook_example_id=example_id,
            skill_id=skill_id,
            gencode_status="failed",
            induced_spec_payload={
                "phase1_classification": phase1,
                "failure_stage": "domain_resolution",
                "failure_code": "DOMAIN_FUNCTION_MISSING",
            },
            gencode_error_log="DOMAIN_FUNCTION_MISSING: injected domain failure",
        )
        return {
            "phase_status": "V3_SHADOW_BRIDGE",
            "tracker_status": "failed",
            "v3_shadow_bridge": {"model_generation_invoked": False},
        }

    with patch(
        "core.gencode.services.admin_gencode_action_service.run_gencode_phase2_raw",
        side_effect=_phase2_domain_failure,
    ) as phase2_mock:
        result = run_admin_v3_dryrun_for_example(
            conn=memory_conn,
            textbook_example_id=example_id,
            skill_id=UNKNOWN_SKILL,
            dryrun_base_dir=str(dryrun_root),
            allow_non_mvp_skill=True,
            force_regenerate=True,
        )
        phase2_mock.assert_called_once()

    assert result["status"] == "failed"
    tracker = memory_conn.execute(
        "SELECT induced_spec_payload, gencode_error_log FROM gencode_component_tracker WHERE textbook_example_id = ?",
        (example_id,),
    ).fetchone()
    payload = json.loads(tracker["induced_spec_payload"])
    phase1 = payload.get("phase1_classification") or payload
    assert phase1.get("problem_type_id")
    assert phase1.get("required_capabilities")
    assert phase1.get("classification_source")
    assert phase1.get("problem_type_id") != "mixed_counting"
    assert payload["failure_stage"] == "domain_resolution"
    assert payload["failure_code"] == "DOMAIN_FUNCTION_MISSING"
