# -*- coding: utf-8 -*-
"""Regression tests for V3 regenerate false-success fixes."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_skill
from core.gencode.services.component_tracker_service import derive_component_id, save_tracker_record

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B4_CumulativeFrequencyTablesAndGraphs"
EXAMPLE_IDS = [3830, 3831, 3832, 3833, 3834]


@pytest.fixture
def memory_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            problem_text TEXT,
            correct_answer TEXT,
            problem_type TEXT
        )
        """
    )
    apply_tracker_ddl(conn)
    for example_id in EXAMPLE_IDS:
        conn.execute(
            """
            INSERT INTO textbook_examples (id, skill_id, problem_text, correct_answer, problem_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                example_id,
                SKILL_ID,
                f"累積次數分配例題 {example_id}",
                "42",
                "",
            ),
        )
        save_tracker_record(
            conn,
            textbook_example_id=example_id,
            skill_id=SKILL_ID,
            gencode_status="verified",
            induced_spec_payload={
                "generation_run_id": f"old-run-{example_id}",
                "problem_type_id": "frequency_table_construction_review",
            },
        )
    conn.commit()
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def dryrun_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_regen_false_success_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


def _write_minimal_component(root: Path, example_id: int) -> None:
    component_id = derive_component_id(example_id)
    component_dir = root / SKILL_ID / "components" / component_id
    component_dir.mkdir(parents=True, exist_ok=True)
    (component_dir / "metadata.py").write_text(
        f'SKILL_ID = "{SKILL_ID}"\nDOMAIN_OPERATION = "frequency_table_construction_review"\n',
        encoding="utf-8",
    )
    (component_dir / "generate.py").write_text(
        f"""
def generate(seed=42, component_id=None, **kwargs):
    return {{
        "question": f"Q{{seed}}-{{component_id}}-{example_id}",
        "answer": "42",
        "problem_type_id": "frequency_table_construction_review",
        "domain_operation": "frequency_table_construction_review",
        "skill_id": "{SKILL_ID}",
        "component_id": component_id or "{component_id}",
        "metadata": {{"seed": seed}},
    }}
""",
        encoding="utf-8",
    )
    (component_dir / "get_hint.py").write_text(
        "def get_hint(level, payload):\n    return 'hint'\n",
        encoding="utf-8",
    )


def test_regenerate_mode_calls_rebuild_for_all_five_components(memory_conn, dryrun_root, monkeypatch):
    calls: list[int] = []

    def _fake_example(**kwargs):
        example_id = int(kwargs["textbook_example_id"])
        calls.append(example_id)
        _write_minimal_component(dryrun_root, example_id)
        component_id = derive_component_id(example_id)
        return {
            "status": "verified",
            "textbook_example_id": example_id,
            "component_id": component_id,
            "force_regenerate": True,
            "cache_hit": False,
            "generation_run_id": f"new-run-{example_id}",
            "generation_started_at": "2026-06-25T00:00:00",
            "generation_finished_at": "2026-06-25T00:00:01",
            "old_artifact_hash": "old",
            "new_artifact_hash": f"new-{example_id}",
            "model_generation_invoked": True,
        }

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_example",
        _fake_example,
    )

    result = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        smoke=True,
        verify=True,
        mode="regenerate",
    )

    assert set(calls) == set(EXAMPLE_IDS)
    assert result["rebuilt_count"] == 5
    assert result["skipped_count"] == 0
    assert result["success"] is True
    assert all(row["component_id"] for row in result["component_results"])


def test_verify_existing_does_not_rebuild_verified_components(memory_conn, dryrun_root, monkeypatch):
    for example_id in EXAMPLE_IDS:
        _write_minimal_component(dryrun_root, example_id)

    def _forbidden(**_kwargs):
        raise AssertionError("rebuild must not run in verify_existing mode")

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_example",
        _forbidden,
    )

    result = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        smoke=True,
        mode="verify_existing",
    )

    assert result["rebuilt_count"] == 0
    assert result["skipped_count"] == 5
    assert result["user_message"] == "未重新生成；已驗證既有產物"
    assert result["success"] is True
    assert set(result["reused_components"]) == {derive_component_id(e) for e in EXAMPLE_IDS}


def test_old_tracker_verified_does_not_skip_when_mode_regenerate(memory_conn, dryrun_root, monkeypatch):
    calls: list[int] = []

    def _fake_example(**kwargs):
        example_id = int(kwargs["textbook_example_id"])
        calls.append(example_id)
        _write_minimal_component(dryrun_root, example_id)
        return {
            "status": "verified",
            "textbook_example_id": example_id,
            "component_id": derive_component_id(example_id),
            "force_regenerate": True,
            "generation_run_id": uuid.uuid4().hex,
            "model_generation_invoked": True,
        }

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_example",
        _fake_example,
    )

    result = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        smoke=False,
        mode="regenerate",
    )

    assert len(calls) == 5
    assert result["skipped_verified_count"] == 0


def test_no_rebuild_evidence_cannot_report_rebuilt_count_five(memory_conn, dryrun_root):
    for example_id in EXAMPLE_IDS:
        _write_minimal_component(dryrun_root, example_id)

    result = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        smoke=True,
        mode="verify_existing",
    )

    assert result["rebuilt_count"] == 0
    assert result["rebuilt_count"] != result["requested_count"]


def test_smoke_covers_all_components_directly_with_conn(memory_conn, dryrun_root, monkeypatch):
    for example_id in EXAMPLE_IDS:
        _write_minimal_component(dryrun_root, example_id)

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_example",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("no rebuild")),
    )

    result = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        smoke=True,
        mode="verify_existing",
    )

    assert result["smoke_passed_count"] == 5
    assert len({row["component_id"] for row in result["component_results"]}) == 5


def test_component_ids_are_non_empty(memory_conn, dryrun_root, monkeypatch):
    def _fake_example(**kwargs):
        example_id = int(kwargs["textbook_example_id"])
        _write_minimal_component(dryrun_root, example_id)
        return {
            "status": "verified",
            "textbook_example_id": example_id,
            "component_id": derive_component_id(example_id),
            "force_regenerate": True,
            "generation_run_id": uuid.uuid4().hex,
            "model_generation_invoked": True,
        }

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_example",
        _fake_example,
    )

    result = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        smoke=True,
        mode="regenerate",
    )

    for row in result["component_results"]:
        assert row["component_id"] == derive_component_id(int(row["textbook_example_id"]))
        assert str(row["component_id"]).startswith("src_")


def test_response_includes_run_metadata(memory_conn, dryrun_root, monkeypatch):
    def _fake_example(**kwargs):
        example_id = int(kwargs["textbook_example_id"])
        _write_minimal_component(dryrun_root, example_id)
        return {
            "status": "verified",
            "textbook_example_id": example_id,
            "component_id": derive_component_id(example_id),
            "force_regenerate": True,
            "generation_run_id": uuid.uuid4().hex,
            "model_generation_invoked": True,
        }

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_example",
        _fake_example,
    )

    result = run_admin_v3_dryrun_for_skill(
        memory_conn,
        SKILL_ID,
        dryrun_base_dir=str(dryrun_root),
        smoke=True,
        mode="regenerate",
    )

    for key in (
        "run_id",
        "started_at",
        "completed_at",
        "duration_ms",
        "requested_count",
        "rebuilt_count",
        "component_results",
    ):
        assert key in result
    assert result["requested_count"] == 5


def test_frequency_domain_does_not_apply_skill_level_default_operation():
    from core.gencode.pipeline_orchestrator import _v3_resolve_gated_domain_operation

    allowed_ops = [
        "frequency_table_construction_review",
        "frequency_table_single_bin_count",
        "histogram_reading",
        "frequency_polygon_reading",
        "frequency_distribution_chart_construction",
    ]
    rows = []
    for index, example_id in enumerate(EXAMPLE_IDS):
        op = allowed_ops[index % len(allowed_ops)]
        row = {
            "id": example_id,
            "problem_text": f"累積次數分配圖 {example_id}",
            "correct_answer": "42",
            "problem_type": "",
        }
        with patch(
            "core.gencode.services.v3_example_semantic_classifier.classify_textbook_example",
            return_value={
                "selected_operation": op,
                "domain_operation": op,
                "problem_type_id": op,
            },
        ):
            selected, classification, _ctx = _v3_resolve_gated_domain_operation(
                skill_id=SKILL_ID,
                textbook_row=row,
                conn=None,
                extra={},
            )
        rows.append((selected, classification.get("problem_type_id")))

    assert len({item[0] for item in rows}) > 1
    assert all(item[0] in allowed_ops for item in rows)


def test_publish_evidence_does_not_bump_tracker_updated_at(memory_conn, dryrun_root, tmp_path):
    from core.gencode.services.admin_gencode_action_service import _record_published_component_evidence

    example_id = EXAMPLE_IDS[0]
    component_id = derive_component_id(example_id)
    _write_minimal_component(dryrun_root, example_id)
    production_root = tmp_path / "agent_skills_v3" / SKILL_ID / "components" / component_id
    production_root.mkdir(parents=True)
    shutil.copy2(dryrun_root / SKILL_ID / "components" / component_id / "generate.py", production_root / "generate.py")

    before = memory_conn.execute(
        "SELECT updated_at FROM gencode_component_tracker WHERE textbook_example_id = ?",
        (example_id,),
    ).fetchone()["updated_at"]

    with patch(
        "core.gencode.services.gencode_status_query_service.load_v3_skill_generator_specs",
        return_value=[{"component_id": component_id}],
    ):
        _record_published_component_evidence(
            memory_conn,
            skill_id=SKILL_ID,
            project_root=tmp_path,
            dryrun_base_dir=str(dryrun_root),
        )

    after = memory_conn.execute(
        "SELECT updated_at, induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id = ?",
        (example_id,),
    ).fetchone()
    assert after["updated_at"] == before
    payload = json.loads(after["induced_spec_payload"])
    assert payload.get("published_generate_sha256")
