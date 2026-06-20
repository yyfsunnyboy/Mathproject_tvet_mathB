# -*- coding: utf-8 -*-
"""Integration tests for V3 shadow bridge and production directory isolation."""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.pipeline_orchestrator import run_gencode_phase2_v3_shadow_bridge
from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.skill_wrapper_compiler import assert_safe_sandbox_root

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = "vh_數學B1_PointSlopeForm"
COMPONENT_FILES = ("metadata.py", "generate.py", "get_hint.py")


def _snapshot_paths(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            snapshot[str(path.relative_to(root))] = digest
    return snapshot


@pytest.fixture
def memory_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL
        )
        """
    )
    apply_tracker_ddl(conn)
    yield conn
    conn.close()


@pytest.fixture
def dryrun_base_dir() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_shadow_bridge_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_v3_shadow_bridge_writes_tracker_and_dryrun_component(
    memory_conn: sqlite3.Connection,
    dryrun_base_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    production_skills_snapshot = _snapshot_paths(PROJECT_ROOT / "skills")
    production_v3_snapshot = _snapshot_paths(PROJECT_ROOT / "agent_skills_v3")

    def _forbidden_compile(*args: object, **kwargs: object) -> dict[str, object]:
        raise AssertionError("compile_and_double_write_skill must not be called in shadow bridge")

    monkeypatch.setattr(
        "core.gencode.skill_wrapper_compiler.compile_and_double_write_skill",
        _forbidden_compile,
    )

    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    memory_conn.commit()

    result = run_gencode_phase2_v3_shadow_bridge(
        conn=memory_conn,
        skill_id=SKILL_ID,
        textbook_example_id=1,
        source_kind="ex_1",
        seed=42,
        dryrun_base_dir=str(dryrun_base_dir),
    )

    assert result["route"] == "v3_shadow_bridge"
    assert result["v3_activated"] is True
    assert result["tracker_status"] == "draft_written"

    tracker_row = memory_conn.execute(
        """
        SELECT gencode_status, component_id
        FROM gencode_component_tracker
        WHERE textbook_example_id = ?
        """,
        (1,),
    ).fetchone()
    assert tracker_row is not None
    assert tracker_row["gencode_status"] == "draft_written"
    assert tracker_row["component_id"] == "src_1"

    component_dir = dryrun_base_dir / SKILL_ID / "components" / "src_1"
    manifest_path = dryrun_base_dir / SKILL_ID / "component_manifest.json"
    assert component_dir.exists()
    assert manifest_path.exists()
    for filename in COMPONENT_FILES:
        assert (component_dir / filename).exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["publish_status"] == "dryrun_manifest_compiled"
    assert manifest["components"][0]["component_id"] == "src_1"

    assert _snapshot_paths(PROJECT_ROOT / "skills") == production_skills_snapshot
    assert _snapshot_paths(PROJECT_ROOT / "agent_skills_v3") == production_v3_snapshot


def test_non_mvp_skill_passthrough_without_side_effects(
    memory_conn: sqlite3.Connection,
    dryrun_base_dir: Path,
):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, "legacy_skill_not_in_mvp"),
    )
    memory_conn.commit()

    before_files = list(dryrun_base_dir.rglob("*"))

    result = run_gencode_phase2_v3_shadow_bridge(
        conn=memory_conn,
        skill_id="legacy_skill_not_in_mvp",
        textbook_example_id=1,
        source_kind="ex_1",
        dryrun_base_dir=str(dryrun_base_dir),
    )

    assert result["route"] == "v2_legacy_passthrough"
    assert result["v3_activated"] is False
    assert result["message"] == "legacy_skill_not_in_mvp_scope"

    tracker_count = memory_conn.execute(
        "SELECT COUNT(*) FROM gencode_component_tracker"
    ).fetchone()[0]
    assert tracker_count == 0
    assert list(dryrun_base_dir.rglob("*")) == before_files


def test_shadow_bridge_raises_skill_id_mismatch(
    memory_conn: sqlite3.Connection,
    dryrun_base_dir: Path,
):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (2, "A"),
    )
    memory_conn.commit()

    with pytest.raises(ValueError, match="skill_id_mismatch"):
        run_gencode_phase2_v3_shadow_bridge(
            conn=memory_conn,
            skill_id=SKILL_ID,
            textbook_example_id=2,
            source_kind="ex_2",
            dryrun_base_dir=str(dryrun_base_dir),
        )


@pytest.mark.parametrize(
    "unsafe_root",
    ["", ".", "skills", "agent_skills_v3", str(PROJECT_ROOT)],
)
def test_shadow_bridge_rejects_unsafe_dryrun_base_dir(
    memory_conn: sqlite3.Connection,
    unsafe_root: str,
):
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    memory_conn.commit()

    with pytest.raises(ValueError, match="unsafe_sandbox_root"):
        run_gencode_phase2_v3_shadow_bridge(
            conn=memory_conn,
            skill_id=SKILL_ID,
            textbook_example_id=1,
            source_kind="ex_1",
            dryrun_base_dir=unsafe_root,
        )


def test_assert_safe_sandbox_root_blocks_production_paths():
    for unsafe_root in ("", ".", "skills", "agent_skills_v3", str(PROJECT_ROOT)):
        with pytest.raises(ValueError, match="unsafe_sandbox_root"):
            assert_safe_sandbox_root(unsafe_root)


def test_shadow_bridge_validator_failure_blocks_disk_write(
    memory_conn: sqlite3.Connection,
    dryrun_base_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """If the validator fails, it must raise ValueError, save tracker status as 'failed', and not write component to disk."""
    memory_conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, SKILL_ID),
    )
    memory_conn.commit()

    # Mock validate_component_payload to return failed
    from core.gencode.services import v3_question_integrity_validator
    monkeypatch.setattr(
        v3_question_integrity_validator,
        "validate_component_payload",
        lambda payload, component_id=None: {
            "passed": False,
            "component_id": component_id,
            "blockers": ["simulated_failure"],
            "warnings": [],
        }
    )

    # Track if write_v3_component_to_disk is called
    write_called = False
    import core.gencode.pipeline_orchestrator as orchestrator
    original_write = orchestrator.write_v3_component_to_disk
    def mock_write(draft, base_dir):
        nonlocal write_called
        write_called = True
        return original_write(draft, base_dir)
    monkeypatch.setattr(orchestrator, "write_v3_component_to_disk", mock_write)

    # Run and verify it raises ValueError
    with pytest.raises(ValueError, match="source_fidelity_failed: .*simulated_failure"):
        run_gencode_phase2_v3_shadow_bridge(
            conn=memory_conn,
            skill_id=SKILL_ID,
            textbook_example_id=1,
            source_kind="ex_1",
            seed=42,
            dryrun_base_dir=str(dryrun_base_dir),
        )

    # Verify write_v3_component_to_disk was NEVER called
    assert not write_called, "write_v3_component_to_disk was called but validator failed!"

    # Verify component directory was not created/written
    component_dir = dryrun_base_dir / SKILL_ID / "components" / "src_1"
    assert not component_dir.exists(), "Component directory exists on disk despite validator failure!"

    # Verify tracker is updated with 'failed' status and integrity_gate_passed=False
    tracker_row = memory_conn.execute(
        """
        SELECT gencode_status, gencode_error_log, induced_spec_payload
        FROM gencode_component_tracker
        WHERE textbook_example_id = ?
        """,
        (1,),
    ).fetchone()
    assert tracker_row is not None
    assert tracker_row["gencode_status"] == "failed"
    assert "integrity_gate_blocker:simulated_failure" in tracker_row["gencode_error_log"]

    spec = json.loads(tracker_row["induced_spec_payload"])
    assert spec.get("integrity_gate_passed") is False
    assert spec.get("integrity_gate_version") == "v1"
    assert spec.get("integrity_gate_blockers") == ["simulated_failure"]
