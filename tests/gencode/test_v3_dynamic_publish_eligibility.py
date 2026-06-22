# -*- coding: utf-8 -*-
"""Dynamic V3 publish eligibility policy tests."""

from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import run_admin_v3_publish_for_skill
from core.gencode.services.v3_publish_eligibility import evaluate_v3_publish_eligibility
from core.gencode.v3_production_publish_service import (
    publish_single_v3_skill_to_production,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
DYNAMIC_SKILL = "vh_數學B1_DynamicEligibilitySkill"
V2_LEGACY_CODE = "V2_LEGACY_CODE"


@pytest.fixture
def memory_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE skills_info (
            skill_id TEXT PRIMARY KEY,
            skill_en_name TEXT,
            skill_ch_name TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE skill_curriculum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL
        )
        """
    )
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
    base = SANDBOX_ROOT / f"pytest_dynamic_eligibility_{uuid.uuid4().hex}"
    project_root = base / "project"
    staging_root = base / "staging"
    (project_root / "skills").mkdir(parents=True, exist_ok=True)
    (project_root / "agent_skills_v3").mkdir(parents=True, exist_ok=True)
    staging_root.mkdir(parents=True, exist_ok=True)
    (project_root / "skills" / f"{DYNAMIC_SKILL}.py").write_text(V2_LEGACY_CODE, encoding="utf-8")
    try:
        yield project_root, staging_root
    finally:
        shutil.rmtree(base, ignore_errors=True)


@pytest.fixture
def taxonomy_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "core.gencode.services.v3_publish_eligibility._load_v3_taxonomy_mvp_scope",
        lambda _path: {DYNAMIC_SKILL},
    )


@pytest.fixture
def registry_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    from core.registry import taxonomy_registry

    monkeypatch.setitem(
        taxonomy_registry.SKILL_TO_DOMAIN,
        DYNAMIC_SKILL,
        {
            "fixed_domain_key": "coordinate_geometry.line_equation",
            "domain": "coordinate_geometry",
            "allowed_types": ["point_slope"],
        },
    )
    monkeypatch.setitem(
        taxonomy_registry.SKILL_DOMAIN_PROFILE,
        DYNAMIC_SKILL,
        {"fixed_domain_key": "coordinate_geometry.line_equation", "registry_revision": "test"},
    )


def _seed_skill_metadata(conn: sqlite3.Connection, skill_id: str = DYNAMIC_SKILL) -> None:
    conn.execute(
        "INSERT INTO skills_info (skill_id, skill_en_name, skill_ch_name) VALUES (?, ?, ?)",
        (skill_id, skill_id, skill_id),
    )
    conn.execute("INSERT INTO skill_curriculum (skill_id) VALUES (?)", (skill_id,))
    conn.commit()


def _payload(example_id: int) -> str:
    return json.dumps(
        {
            "source_kind": f"ex_{example_id}",
            "presentation_mode": "short_answer",
            "line_type": "general_form",
            "fixed_domain_key": "coordinate_geometry.line_equation",
            "domain_operation": "point_slope",
            "problem_type_id": "point_slope",
            "display_order": example_id,
            "source_order": example_id,
            "sampling_weight": 1,
            "integrity_gate_passed": True,
            "integrity_gate_version": "v1",
        },
        ensure_ascii=False,
    )


def _seed_examples(
    conn: sqlite3.Connection,
    *,
    total: int = 17,
    verified: int = 17,
    failed_ids: set[int] | None = None,
    unsupported_ids: set[int] | None = None,
    missing_tracker_ids: set[int] | None = None,
    skill_id: str = DYNAMIC_SKILL,
) -> None:
    failed_ids = set(failed_ids or set())
    unsupported_ids = set(unsupported_ids or set())
    missing_tracker_ids = set(missing_tracker_ids or set())
    for example_id in range(1, total + 1):
        conn.execute("INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)", (example_id, skill_id))
        if example_id in missing_tracker_ids:
            continue
        if example_id in unsupported_ids:
            status = "failed"
            error = "unsupported_task_type: unsupported"
        elif example_id in failed_ids:
            status = "failed"
            error = "forced failure"
        elif example_id <= verified:
            status = "verified"
            error = None
        else:
            status = "draft_written"
            error = None
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
                skill_id,
                f"src_{example_id}",
                status,
                _payload(example_id) if status == "verified" else None,
                error,
            ),
        )
    conn.commit()


def _seed_staging_components(staging_root: Path, count: int = 17) -> None:
    for example_id in range(1, count + 1):
        component_id = f"src_{example_id}"
        component_dir = staging_root / DYNAMIC_SKILL / "components" / component_id
        component_dir.mkdir(parents=True, exist_ok=True)
        (component_dir / "metadata.py").write_text(f'COMPONENT_ID = "{component_id}"\n', encoding="utf-8")
        (component_dir / "generate.py").write_text(
            f'''from __future__ import annotations

from typing import Any


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return {{
        "question_text": "dynamic question {example_id}",
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


def test_dynamic_taxonomy_concrete_skill_gets_publish_eligibility_and_publishes(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    taxonomy_registered: None,
    registry_registered: None,
) -> None:
    project_root, staging_root = isolated_roots
    _seed_skill_metadata(memory_conn)
    _seed_examples(memory_conn, total=17, verified=17)
    _seed_staging_components(staging_root, 17)

    eligibility = evaluate_v3_publish_eligibility(memory_conn, DYNAMIC_SKILL)
    assert eligibility["allowed"] is True

    result = publish_single_v3_skill_to_production(
        conn=memory_conn,
        skill_id=DYNAMIC_SKILL,
        project_root=str(project_root),
        staging_root=str(staging_root),
    )
    assert result["status"] == "production_published"
    assert result["component_count"] == 17


def test_taxonomy_not_registered_rejected(memory_conn: sqlite3.Connection) -> None:
    _seed_skill_metadata(memory_conn)
    _seed_examples(memory_conn)
    eligibility = evaluate_v3_publish_eligibility(memory_conn, DYNAMIC_SKILL)
    assert eligibility["allowed"] is False
    assert eligibility["reason"] == "taxonomy_not_registered"


def test_outline_skill_rejected(memory_conn: sqlite3.Connection, taxonomy_registered: None) -> None:
    eligibility = evaluate_v3_publish_eligibility(memory_conn, "outline_fake")
    assert eligibility["allowed"] is False
    assert eligibility["reason"] == "not_concrete_skill"


def test_no_textbook_examples_rejected(memory_conn: sqlite3.Connection, taxonomy_registered: None, registry_registered: None) -> None:
    _seed_skill_metadata(memory_conn)
    eligibility = evaluate_v3_publish_eligibility(memory_conn, DYNAMIC_SKILL)
    assert eligibility["allowed"] is False
    assert eligibility["reason"] == "no_textbook_examples"


def test_coverage_incomplete_allows_partial_publish(
    memory_conn: sqlite3.Connection,
    taxonomy_registered: None,
    registry_registered: None,
) -> None:
    _seed_skill_metadata(memory_conn)
    _seed_examples(memory_conn, total=17, verified=16)
    eligibility = evaluate_v3_publish_eligibility(memory_conn, DYNAMIC_SKILL)
    assert eligibility["allowed"] is True
    assert eligibility["full_coverage"] is False


def test_failed_count_allows_partial_publish(
    memory_conn: sqlite3.Connection,
    taxonomy_registered: None,
    registry_registered: None,
) -> None:
    _seed_skill_metadata(memory_conn)
    _seed_examples(memory_conn, total=17, verified=16, failed_ids={17})
    eligibility = evaluate_v3_publish_eligibility(memory_conn, DYNAMIC_SKILL)
    assert eligibility["allowed"] is True
    assert eligibility["full_coverage"] is False


def test_unsupported_count_allows_partial_publish(
    memory_conn: sqlite3.Connection,
    taxonomy_registered: None,
    registry_registered: None,
) -> None:
    _seed_skill_metadata(memory_conn)
    _seed_examples(memory_conn, total=17, verified=16, unsupported_ids={17})
    eligibility = evaluate_v3_publish_eligibility(memory_conn, DYNAMIC_SKILL)
    assert eligibility["allowed"] is True
    assert eligibility["full_coverage"] is False


def test_missing_tracker_allows_partial_publish(
    memory_conn: sqlite3.Connection,
    taxonomy_registered: None,
    registry_registered: None,
) -> None:
    _seed_skill_metadata(memory_conn)
    _seed_examples(memory_conn, total=17, verified=16, missing_tracker_ids={17})
    eligibility = evaluate_v3_publish_eligibility(memory_conn, DYNAMIC_SKILL)
    assert eligibility["allowed"] is True
    assert eligibility["full_coverage"] is False


def test_publish_ready_false_allows_partial_publish(
    memory_conn: sqlite3.Connection,
    taxonomy_registered: None,
    registry_registered: None,
) -> None:
    _seed_skill_metadata(memory_conn)
    _seed_examples(memory_conn, total=17, verified=17)
    coverage = {
        "total_examples": 17,
        "verified_count": 17,
        "failed_count": 0,
        "unsupported_count": 0,
        "missing_tracker_count": 0,
        "publish_ready": False,
    }
    eligibility = evaluate_v3_publish_eligibility(memory_conn, DYNAMIC_SKILL, coverage=coverage)
    assert eligibility["allowed"] is True
    assert eligibility["full_coverage"] is False


def test_admin_and_production_share_same_policy_reason(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    taxonomy_registered: None,
    registry_registered: None,
) -> None:
    project_root, staging_root = isolated_roots
    _seed_skill_metadata(memory_conn)
    _seed_examples(memory_conn, total=1, verified=1)
    conn = memory_conn
    conn.execute(
        "UPDATE gencode_component_tracker SET induced_spec_payload = ? WHERE textbook_example_id = 1",
        (
            json.dumps(
                {
                    "fixed_domain_key": "coordinate_geometry.point_line_distance",
                    "domain_operation": "distance_from_point_to_line",
                    "integrity_gate_passed": True,
                    "integrity_gate_version": "v1",
                },
                ensure_ascii=False,
            ),
        ),
    )
    conn.commit()

    eligibility = evaluate_v3_publish_eligibility(memory_conn, DYNAMIC_SKILL)
    assert eligibility["reason"] == "no_eligible_components"
    with pytest.raises(ValueError, match="no_eligible_components"):
        run_admin_v3_publish_for_skill(
            conn=memory_conn,
            skill_id=DYNAMIC_SKILL,
            project_root=str(project_root),
            staging_root=str(staging_root),
            force_publish=True,
            strict_coverage=True,
        )
    with pytest.raises(ValueError, match="no_eligible_components"):
        publish_single_v3_skill_to_production(
            conn=memory_conn,
            skill_id=DYNAMIC_SKILL,
            project_root=str(project_root),
            staging_root=str(staging_root),
        )


def test_illegal_skill_not_allowed_when_domain_unregistered(memory_conn: sqlite3.Connection, taxonomy_registered: None) -> None:
    _seed_skill_metadata(memory_conn)
    _seed_examples(memory_conn)
    eligibility = evaluate_v3_publish_eligibility(memory_conn, DYNAMIC_SKILL)
    assert eligibility["allowed"] is False
    assert eligibility["reason"] == "skill_domain_not_registered"


def test_eligibility_does_not_skip_production_smoke_rollback(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    taxonomy_registered: None,
    registry_registered: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root, staging_root = isolated_roots
    _seed_skill_metadata(memory_conn)
    _seed_examples(memory_conn, total=17, verified=17)
    _seed_staging_components(staging_root, 17)

    from core.gencode.v3_production_publish_service import run_v3_smoke

    def _fail_production_smoke(root: Path, skill_id: str) -> None:
        if root.resolve() == project_root.resolve():
            raise RuntimeError("forced production smoke failure")
        run_v3_smoke(root, skill_id)

    monkeypatch.setattr(
        "core.gencode.v3_production_publish_service.run_v3_smoke",
        _fail_production_smoke,
    )

    result = publish_single_v3_skill_to_production(
        conn=memory_conn,
        skill_id=DYNAMIC_SKILL,
        project_root=str(project_root),
        staging_root=str(staging_root),
    )
    assert result["status"] == "rolled_back_after_failed_production_smoke"
    assert (project_root / "skills" / f"{DYNAMIC_SKILL}.py").read_text(encoding="utf-8") == V2_LEGACY_CODE
