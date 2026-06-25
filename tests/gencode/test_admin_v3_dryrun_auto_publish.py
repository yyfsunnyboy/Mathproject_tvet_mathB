# -*- coding: utf-8 -*-
"""Closed-loop admin V3 dryrun + auto-publish tests."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import (
    run_admin_v3_dryrun_publish_closed_loop_for_skill,
)
from core.gencode.services.v3_skill_coverage_service import get_v3_skill_component_coverage
from core.gencode.v3_production_publish_service import ALLOWED_PRODUCTION_SKILL_ID

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = ALLOWED_PRODUCTION_SKILL_ID
V2_LEGACY_CODE = "V2_LEGACY_CODE"


@pytest.fixture
def memory_conn() -> Iterator[sqlite3.Connection]:
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
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def isolated_roots() -> Iterator[tuple[Path, Path]]:
    base = SANDBOX_ROOT / f"pytest_admin_auto_publish_{uuid.uuid4().hex}"
    project_root = base / "project"
    staging_root = base / "staging"
    (project_root / "skills").mkdir(parents=True, exist_ok=True)
    (project_root / "agent_skills_v3").mkdir(parents=True, exist_ok=True)
    staging_root.mkdir(parents=True, exist_ok=True)
    (project_root / "skills" / f"{SKILL_ID}.py").write_text(V2_LEGACY_CODE, encoding="utf-8")
    try:
        yield project_root, staging_root
    finally:
        shutil.rmtree(base, ignore_errors=True)


def _payload(example_id: int) -> str:
    return json.dumps(
        {
            "source_kind": f"ex_{example_id}",
            "presentation_mode": "short_answer",
            "line_type": "point_slope",
            "problem_type_id": "line_equation_general_form",
            "display_order": example_id,
            "source_order": example_id,
            "sampling_weight": 1,
            "integrity_gate_passed": True,
            "integrity_gate_version": "v1",
        },
        ensure_ascii=False,
    )


def _insert_examples(
    conn: sqlite3.Connection,
    count: int,
    *,
    status: str = "verified",
    missing_tracker_ids: set[int] | None = None,
) -> None:
    missing_tracker_ids = set(missing_tracker_ids or set())
    for example_id in range(1, count + 1):
        conn.execute(
            "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
            (example_id, SKILL_ID),
        )
        if example_id in missing_tracker_ids:
            continue
        conn.execute(
            """
            INSERT INTO gencode_component_tracker (
                textbook_example_id,
                skill_id,
                component_id,
                gencode_status,
                induced_spec_payload,
                gencode_error_log
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                example_id,
                SKILL_ID,
                f"src_{example_id}",
                status,
                _payload(example_id) if status == "verified" else None,
                "forced failure" if status == "failed" else None,
            ),
        )
    conn.commit()


def _dryrun_root(staging_root: Path) -> Path:
    return staging_root.parent / "dryrun"


def _seed_dryrun_components(dryrun_root: Path, count: int) -> None:
    for example_id in range(1, count + 1):
        component_id = f"src_{example_id}"
        component_dir = dryrun_root / SKILL_ID / "components" / component_id
        component_dir.mkdir(parents=True, exist_ok=True)
        (component_dir / "metadata.py").write_text(
            f'COMPONENT_ID = "{component_id}"\n',
            encoding="utf-8",
        )
        (component_dir / "generate.py").write_text(
            f'''from __future__ import annotations

from typing import Any


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return {{
        "question_text": "mock question {example_id}",
        "answer": "mock answer",
        "correct_answer": "mock answer",
        "component_id": "{component_id}",
        "metadata": {{"component_id": "{component_id}"}},
    }}


def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> bool:
    return str(user_answer) == str(correct_answer)
''',
            encoding="utf-8",
        )
        (component_dir / "get_hint.py").write_text(
            '''from __future__ import annotations

from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return f"hint step {step}"
''',
            encoding="utf-8",
        )


def _stub_successful_publish(monkeypatch: pytest.MonkeyPatch) -> None:
    def _publish(*, conn, skill_id, project_root, **_kwargs):
        count = conn.execute(
            """
            SELECT COUNT(*) FROM gencode_component_tracker
            WHERE skill_id = ? AND gencode_status = 'verified'
            """,
            (skill_id,),
        ).fetchone()[0]
        facade = Path(str(project_root)) / "skills" / f"{skill_id}.py"
        facade.parent.mkdir(parents=True, exist_ok=True)
        facade.write_text(
            """
def generate(seed=42, **kwargs):
    return {
        "question_text": "mock question",
        "answer": "mock answer",
        "correct_answer": "mock answer",
        "metadata": {},
    }

def check(user_answer, correct_answer, question_payload=None):
    return str(user_answer) == str(correct_answer)

def get_hint(level, question_payload):
    return "hint"
""",
            encoding="utf-8",
        )
        components_root = Path(str(project_root)) / "agent_skills_v3" / skill_id / "components"
        for index in range(1, int(count) + 1):
            (components_root / f"src_{index}").mkdir(parents=True, exist_ok=True)
        return {
            "status": "production_published",
            "component_count": int(count),
            "production_smoke_status": "passed",
            "compile": {
                "generator_specs": [
                    {"component_id": f"src_{index}"} for index in range(1, int(count) + 1)
                ]
            },
        }

    monkeypatch.setattr(
        "core.gencode.v3_production_publish_service.publish_single_v3_skill_to_production",
        _publish,
    )
    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service._record_published_component_evidence",
        lambda *args, **kwargs: [],
    )


def _stub_publish_eligible(monkeypatch: pytest.MonkeyPatch) -> None:
    from core.gencode.skill_wrapper_compiler import _fetch_verified_components

    monkeypatch.setattr(
        "core.gencode.v3_production_publish_service._fetch_publish_eligible_components",
        _fetch_verified_components,
    )


def _stub_publish_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "core.gencode.v3_production_publish_service.run_v3_per_component_smoke",
        lambda *_args, **_kwargs: None,
    )


def _stub_eligibility(monkeypatch: pytest.MonkeyPatch) -> None:
    def _eligible(conn, skill_id, coverage=None):
        verified = int((coverage or {}).get("verified_count") or 0)
        return {
            "allowed": True,
            "full_coverage": True,
            "reason": "eligible",
            "skill_id": skill_id,
            "eligible_component_count": verified,
        }

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.evaluate_v3_publish_eligibility",
        _eligible,
    )
    monkeypatch.setattr(
        "core.gencode.services.v3_question_integrity_validator.validate_skill_samples",
        lambda *args, **kwargs: {"passed": True, "blockers_summary": []},
    )


def _stub_generation(monkeypatch: pytest.MonkeyPatch, *, rebuilt_count: int | None = None) -> None:
    def _already_generated(conn, skill_id, **_kwargs):
        coverage = get_v3_skill_component_coverage(conn, skill_id)
        total = int(coverage["total_examples"] or 0)
        rebuilt = total if rebuilt_count is None else rebuilt_count
        return {
            "success": bool(coverage["failed_count"] == 0 and rebuilt > 0),
            "skill_id": skill_id,
            "total_examples": total,
            "requested_count": total,
            "processed_count": rebuilt,
            "rebuilt_count": rebuilt,
            "skipped_count": max(0, total - rebuilt),
            "failed_count": coverage["failed_count"],
            "unsupported_count": coverage["unsupported_count"],
            "verified_count": coverage["verified_count"],
            "missing_tracker_count": coverage["missing_tracker_count"],
            "publish_ready": coverage["publish_ready"],
            "coverage": coverage,
            "results": [],
            "per_example_results": [],
            "component_results": [],
        }

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_skill",
        _already_generated,
    )


def _run_closed_loop(conn: sqlite3.Connection, project_root: Path, staging_root: Path):
    return run_admin_v3_dryrun_publish_closed_loop_for_skill(
        conn,
        SKILL_ID,
        project_root=str(project_root),
        staging_root=str(staging_root),
        smoke=True,
        verify=True,
        force=False,
        dryrun_base_dir=str(_dryrun_root(staging_root)),
    )


def test_full_verified_17_of_17_auto_publishes(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root, staging_root = isolated_roots
    _insert_examples(memory_conn, 17, status="verified")
    _seed_dryrun_components(_dryrun_root(staging_root), 17)
    _stub_generation(monkeypatch)
    _stub_eligibility(monkeypatch)
    _stub_successful_publish(monkeypatch)
    _stub_publish_eligible(monkeypatch)
    _stub_publish_smoke(monkeypatch)

    result = _run_closed_loop(memory_conn, project_root, staging_root)

    assert result["generation"]["total_examples"] == 17
    assert result["generation"]["verified_count"] == 17
    assert result["publish"]["attempted"] is True
    assert result["publish"]["published"] is True
    assert result["publish"]["partial_publish"] is False
    assert result["publish"]["production_component_count"] == 17
    assert result["publish"]["generator_specs_count"] == 17
    assert result["publish"]["production_wrapper_exists"] is True
    assert result["publish"]["v3_package_exists"] is True
    assert result["publish"]["runtime_ready"] is True


def test_failed_count_blocks_auto_publish(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root, staging_root = isolated_roots
    _insert_examples(memory_conn, 2, status="failed")
    _stub_generation(monkeypatch, rebuilt_count=0)

    result = _run_closed_loop(memory_conn, project_root, staging_root)

    assert result["publish"]["attempted"] is False
    assert result["publish"]["published"] is False
    assert (project_root / "skills" / f"{SKILL_ID}.py").read_text(encoding="utf-8") == V2_LEGACY_CODE


def test_missing_tracker_blocks_auto_publish(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root, staging_root = isolated_roots
    _insert_examples(memory_conn, 2, status="verified", missing_tracker_ids={2})
    _stub_generation(monkeypatch, rebuilt_count=0)

    result = _run_closed_loop(memory_conn, project_root, staging_root)

    assert result["generation"]["missing_tracker_count"] == 1
    assert result["publish"]["attempted"] is False
    assert result["publish"]["published"] is False


def test_wrapper_compile_failure_preserves_previous_production(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root, staging_root = isolated_roots
    _insert_examples(memory_conn, 1, status="verified")
    _seed_dryrun_components(_dryrun_root(staging_root), 1)
    _stub_generation(monkeypatch)
    _stub_eligibility(monkeypatch)
    _stub_publish_eligible(monkeypatch)
    _stub_publish_smoke(monkeypatch)

    def _fail_publish(**_kwargs):
        raise ValueError("wrapper compile failed")

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_publish_for_skill",
        _fail_publish,
    )

    result = _run_closed_loop(memory_conn, project_root, staging_root)

    assert result["publish"]["attempted"] is True
    assert result["publish"]["published"] is False
    assert result["publish"]["failed_stage"] == "wrapper_compile"
    assert result["publish"]["previous_production_preserved"] is True
    assert (project_root / "skills" / f"{SKILL_ID}.py").read_text(encoding="utf-8") == V2_LEGACY_CODE


def test_production_smoke_failure_preserves_previous_production(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root, staging_root = isolated_roots
    _insert_examples(memory_conn, 1, status="verified")
    _seed_dryrun_components(_dryrun_root(staging_root), 1)
    _stub_generation(monkeypatch)
    _stub_eligibility(monkeypatch)
    _stub_publish_eligible(monkeypatch)
    _stub_publish_smoke(monkeypatch)

    def _fail_publish(**_kwargs):
        raise RuntimeError("forced production smoke failure")

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_publish_for_skill",
        _fail_publish,
    )

    result = _run_closed_loop(memory_conn, project_root, staging_root)

    assert result["publish"]["attempted"] is True
    assert result["publish"]["published"] is False
    assert result["publish"]["failed_stage"] == "production_smoke"
    assert result["publish"]["previous_production_preserved"] is True
    assert (project_root / "skills" / f"{SKILL_ID}.py").read_text(encoding="utf-8") == V2_LEGACY_CODE


def test_successful_wrapper_can_be_loaded_by_runtime(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root, staging_root = isolated_roots
    _insert_examples(memory_conn, 1, status="verified")
    _seed_dryrun_components(_dryrun_root(staging_root), 1)
    _stub_generation(monkeypatch)
    _stub_eligibility(monkeypatch)
    _stub_successful_publish(monkeypatch)
    _stub_publish_eligible(monkeypatch)
    _stub_publish_smoke(monkeypatch)

    result = _run_closed_loop(memory_conn, project_root, staging_root)
    assert result["publish"]["published"] is True

    facade_path = project_root / "skills" / f"{SKILL_ID}.py"
    spec = importlib.util.spec_from_file_location(f"runtime_smoke_{uuid.uuid4().hex}", facade_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.generate(seed=42)
    assert isinstance(payload, dict)
    assert module.check("mock answer", "mock answer", question_payload=payload) is True


def test_response_distinguishes_generation_and_publish_success(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root, staging_root = isolated_roots
    _insert_examples(memory_conn, 1, status="verified")
    _seed_dryrun_components(_dryrun_root(staging_root), 1)
    _stub_generation(monkeypatch)
    _stub_eligibility(monkeypatch)
    _stub_successful_publish(monkeypatch)
    _stub_publish_eligible(monkeypatch)
    _stub_publish_smoke(monkeypatch)

    result = _run_closed_loop(memory_conn, project_root, staging_root)

    assert result["generation"]["verified_count"] == 1
    assert result["publish"]["attempted"] is True
    assert result["publish"]["published"] is True
    assert result["success"] is True


def test_repeated_closed_loop_is_idempotent(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root, staging_root = isolated_roots
    _insert_examples(memory_conn, 17, status="verified")
    _seed_dryrun_components(_dryrun_root(staging_root), 17)
    _stub_generation(monkeypatch)
    _stub_eligibility(monkeypatch)
    _stub_successful_publish(monkeypatch)
    _stub_publish_eligible(monkeypatch)
    _stub_publish_smoke(monkeypatch)

    first = _run_closed_loop(memory_conn, project_root, staging_root)
    second = _run_closed_loop(memory_conn, project_root, staging_root)

    assert first["publish"]["published"] is True
    assert second["publish"]["published"] is True
    tracker_count = memory_conn.execute("SELECT COUNT(*) FROM gencode_component_tracker").fetchone()[0]
    assert tracker_count == 17
    component_dirs = list((project_root / "agent_skills_v3" / SKILL_ID / "components").iterdir())
    assert len(component_dirs) == 17
