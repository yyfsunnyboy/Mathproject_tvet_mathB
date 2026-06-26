# -*- coding: utf-8 -*-
"""V3 fixed-domain publish gate tests — no hardcoded skill allowlist."""

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
from core.gencode.skill_wrapper_compiler import compile_and_double_write_skill
from core.gencode.v3_production_publish_service import (
    V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS,
    V3_PRODUCTION_PUBLISH_GLOBALLY_ENABLED,
    assert_production_publish_globally_enabled,
    publish_single_v3_skill_to_production,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
REGISTERED_SKILL = "vh_數學B1_NewRegisteredPublishSkill"
UNREGISTERED_SKILL = "vh_數學B1_UnregisteredDomainSkill"
FIXED_DOMAIN = "coordinate_geometry.line_equation"
OPERATION = "horizontal_line"


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
    base = SANDBOX_ROOT / f"pytest_fixed_domain_publish_{uuid.uuid4().hex}"
    project_root = base / "project"
    staging_root = base / "staging"
    (project_root / "skills").mkdir(parents=True, exist_ok=True)
    (project_root / "agent_skills_v3").mkdir(parents=True, exist_ok=True)
    staging_root.mkdir(parents=True, exist_ok=True)
    try:
        yield project_root, staging_root
    finally:
        shutil.rmtree(base, ignore_errors=True)


@pytest.fixture
def taxonomy_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "core.gencode.services.v3_publish_eligibility._load_v3_taxonomy_mvp_scope",
        lambda _path: {REGISTERED_SKILL},
    )


@pytest.fixture
def registry_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    from core.registry import taxonomy_registry

    monkeypatch.setitem(
        taxonomy_registry.SKILL_TO_DOMAIN,
        REGISTERED_SKILL,
        {
            "fixed_domain_key": FIXED_DOMAIN,
            "domain": "coordinate_geometry",
            "allowed_types": [OPERATION],
        },
    )
    monkeypatch.setitem(
        taxonomy_registry.SKILL_DOMAIN_PROFILE,
        REGISTERED_SKILL,
        {"fixed_domain_key": FIXED_DOMAIN, "registry_revision": "test"},
    )


def _spec(*, fixed_domain_key: str, operation: str, verified: bool = True) -> str:
    return json.dumps(
        {
            "fixed_domain_key": fixed_domain_key,
            "domain_operation": operation,
            "problem_type_id": operation,
            "presentation_mode": "short_answer",
            "integrity_gate_passed": verified,
            "integrity_gate_version": "v1" if verified else "v0",
        },
        ensure_ascii=False,
    )


def _seed_component(
    conn: sqlite3.Connection,
    *,
    example_id: int,
    skill_id: str,
    status: str,
    spec_json: str | None,
) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (example_id, skill_id),
    )
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (example_id, skill_id, f"src_{example_id}", status, spec_json),
    )


def _seed_staging(staging_root: Path, skill_id: str, component_id: str = "src_1") -> None:
    component_dir = staging_root / skill_id / "components" / component_id
    component_dir.mkdir(parents=True, exist_ok=True)
    (component_dir / "metadata.py").write_text(f'COMPONENT_ID = "{component_id}"\n', encoding="utf-8")
    (component_dir / "generate.py").write_text(
        '''from __future__ import annotations
from typing import Any

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "question_text": "test",
        "answer": "y = 1",
        "correct_answer": "y = 1",
        "component_id": "src_1",
        "metadata": {"component_id": "src_1"},
    }
''',
        encoding="utf-8",
    )
    (component_dir / "get_hint.py").write_text(
        "def get_hint(step: int, question_payload=None):\n    return 'hint'\n",
        encoding="utf-8",
    )


def test_no_hardcoded_skill_allowlist_remains() -> None:
    assert V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS == frozenset()


def test_registered_skill_publishable_without_manual_allowlist(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    taxonomy_registered: None,
    registry_registered: None,
) -> None:
    project_root, staging_root = isolated_roots
    _seed_component(
        memory_conn,
        example_id=1,
        skill_id=REGISTERED_SKILL,
        status="verified",
        spec_json=_spec(fixed_domain_key=FIXED_DOMAIN, operation=OPERATION),
    )
    memory_conn.commit()
    _seed_staging(staging_root, REGISTERED_SKILL)

    eligibility = evaluate_v3_publish_eligibility(memory_conn, REGISTERED_SKILL)
    assert eligibility["allowed"] is True
    assert REGISTERED_SKILL not in V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS

    result = publish_single_v3_skill_to_production(
        conn=memory_conn,
        skill_id=REGISTERED_SKILL,
        project_root=str(project_root),
        staging_root=str(staging_root),
    )
    assert result["status"] == "production_published"
    assert result["component_count"] == 1


def test_unregistered_domain_skill_blocked(
    memory_conn: sqlite3.Connection,
    taxonomy_registered: None,
) -> None:
    _seed_component(
        memory_conn,
        example_id=1,
        skill_id=REGISTERED_SKILL,
        status="verified",
        spec_json=_spec(fixed_domain_key=FIXED_DOMAIN, operation=OPERATION),
    )
    memory_conn.commit()
    eligibility = evaluate_v3_publish_eligibility(memory_conn, REGISTERED_SKILL)
    assert eligibility["allowed"] is False
    assert eligibility["reason"] == "DOMAIN_EVIDENCE_INCOMPLETE"


def test_domain_mismatch_component_excluded_from_generator_specs(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    taxonomy_registered: None,
    registry_registered: None,
) -> None:
    project_root, staging_root = isolated_roots
    _seed_component(
        memory_conn,
        example_id=1,
        skill_id=REGISTERED_SKILL,
        status="verified",
        spec_json=_spec(fixed_domain_key=FIXED_DOMAIN, operation=OPERATION),
    )
    _seed_component(
        memory_conn,
        example_id=2,
        skill_id=REGISTERED_SKILL,
        status="verified",
        spec_json=_spec(fixed_domain_key="coordinate_geometry.point_line_distance", operation=OPERATION),
    )
    memory_conn.commit()

    compile_result = compile_and_double_write_skill(memory_conn, REGISTERED_SKILL, str(staging_root))
    assert compile_result["component_count"] == 1
    specs = compile_result["generator_specs"]
    assert isinstance(specs, list)
    assert len(specs) == 1
    assert specs[0]["component_id"] == "src_1"


def test_non_publishable_status_does_not_block_partial_publish(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
    taxonomy_registered: None,
    registry_registered: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "core.gencode.services.v3_question_integrity_validator.validate_skill_samples",
        lambda *args, **kwargs: {"passed": True, "blockers_summary": []},
    )
    project_root, staging_root = isolated_roots
    _seed_component(
        memory_conn,
        example_id=1,
        skill_id=REGISTERED_SKILL,
        status="verified",
        spec_json=_spec(fixed_domain_key=FIXED_DOMAIN, operation=OPERATION),
    )
    _seed_component(
        memory_conn,
        example_id=2,
        skill_id=REGISTERED_SKILL,
        status="needs_human_review",
        spec_json=None,
    )
    memory_conn.commit()
    _seed_staging(staging_root, REGISTERED_SKILL)

    eligibility = evaluate_v3_publish_eligibility(memory_conn, REGISTERED_SKILL)
    assert eligibility["allowed"] is True
    assert eligibility["full_coverage"] is False

    result = run_admin_v3_publish_for_skill(
        conn=memory_conn,
        skill_id=REGISTERED_SKILL,
        project_root=str(project_root),
        staging_root=str(staging_root),
        force_publish=True,
        strict_coverage=False,
    )
    assert result["component_count"] == 1


def test_global_publish_disabled_uses_distinct_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "core.gencode.v3_production_publish_service.V3_PRODUCTION_PUBLISH_GLOBALLY_ENABLED",
        False,
    )
    with pytest.raises(ValueError, match="production_publish_globally_disabled"):
        assert_production_publish_globally_enabled()


def test_empty_fixed_domain_key_inherits_registry_for_verified_component() -> None:
    from core.gencode.skill_fixed_domain_authority import validate_publish_component_record

    blockers = validate_publish_component_record(
        skill_id="vh_數學B1_DistanceBetweenTwoParallelLines",
        component_skill_id="vh_數學B1_DistanceBetweenTwoParallelLines",
        component_fixed_domain_key="",
        component_operation="distance_between_parallel_lines",
        component_status="verified",
    )
    assert blockers == []
