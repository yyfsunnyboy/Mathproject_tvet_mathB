# -*- coding: utf-8 -*-
"""Phase 5.5: derived-capability binding E2E for unregistered descriptive-statistics skills."""

from __future__ import annotations

import importlib.util
import json
import py_compile
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import (
    run_admin_v3_dryrun_for_example,
    run_admin_v3_dryrun_for_skill,
    run_admin_v3_dryrun_publish_closed_loop_for_skill,
)
from core.gencode.services.v3_publish_eligibility import evaluate_v3_publish_eligibility
from core.gencode.services.v3_skill_coverage_service import get_v3_skill_component_coverage
from core.gencode.skill_fixed_domain_authority import validate_component_domain_evidence
from core.registry import taxonomy_registry

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"

# Deliberately not present in SKILL_TO_DOMAIN; descriptive stats via capability inference only.
UNREGISTERED_SKILL = "vh_數學B4_UnregisteredDescriptiveMeanE2E"
MEAN_EXAMPLE_ID = 880001
OPAQUE_EXAMPLE_ID = 880002

_FORBIDDEN_PROBLEM_TYPES = {"mixed_counting", "in_class_practice", "statistics_concept"}

_GENCODE_TOUCHED_FILES = (
    "core/gencode/pipeline_orchestrator.py",
    "core/gencode/domain_operation_selector.py",
    "core/gencode/services/admin_gencode_action_service.py",
    "core/gencode/skill_fixed_domain_authority.py",
)


@pytest.fixture
def memory_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            problem_type TEXT,
            problem_text TEXT,
            correct_answer TEXT,
            detailed_solution TEXT,
            source_description TEXT
        )
        """
    )
    apply_tracker_ddl(conn)
    conn.execute(
        """
        INSERT INTO textbook_examples
            (id, skill_id, problem_type, problem_text, correct_answer, detailed_solution, source_description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            MEAN_EXAMPLE_ID,
            UNREGISTERED_SKILL,
            "textbook_example",
            "五人身高為 160、165、170、172、168 公分，求平均身高。",
            "167",
            "將五個身高相加後除以 5。",
            "",
        ),
    )
    conn.execute(
        """
        INSERT INTO textbook_examples
            (id, skill_id, problem_type, problem_text, correct_answer, detailed_solution, source_description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            OPAQUE_EXAMPLE_ID,
            UNREGISTERED_SKILL,
            "textbook_example",
            "請閱讀本單元課文並寫下心得。",
            "",
            "",
            "",
        ),
    )
    conn.commit()
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def dryrun_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_derived_binding_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_unregistered_skill_not_in_skill_to_domain() -> None:
    assert UNREGISTERED_SKILL not in taxonomy_registry.SKILL_TO_DOMAIN


def test_derived_binding_dryrun_produces_verified_component(
    memory_conn: sqlite3.Connection,
    dryrun_root: Path,
) -> None:
    result = run_admin_v3_dryrun_for_example(
        conn=memory_conn,
        textbook_example_id=MEAN_EXAMPLE_ID,
        skill_id=UNREGISTERED_SKILL,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
        allow_non_mvp_skill=True,
    )

    assert result["status"] == "verified"
    component_dir = dryrun_root / UNREGISTERED_SKILL / "components" / f"src_{MEAN_EXAMPLE_ID}"
    for filename in ("metadata.py", "generate.py", "get_hint.py"):
        path = component_dir / filename
        assert path.is_file(), filename
        py_compile.compile(str(path), doraise=True)

    tracker = memory_conn.execute(
        """
        SELECT gencode_status, induced_spec_payload
        FROM gencode_component_tracker
        WHERE textbook_example_id = ?
        """,
        (MEAN_EXAMPLE_ID,),
    ).fetchone()
    assert tracker["gencode_status"] == "verified"
    spec = json.loads(tracker["induced_spec_payload"])
    phase1 = spec.get("phase1_classification") if isinstance(spec.get("phase1_classification"), dict) else {}
    classification_status = str(phase1.get("classification_status") or spec.get("classification_status") or "")
    assert classification_status == "resolved"
    problem_type_id = str(spec.get("problem_type_id") or phase1.get("problem_type_id") or "")
    assert problem_type_id and problem_type_id not in _FORBIDDEN_PROBLEM_TYPES
    required_capabilities = spec.get("required_capabilities") or phase1.get("required_capabilities")
    assert required_capabilities
    assert spec.get("classification_source") or phase1.get("classification_source")

    domain = spec.get("domain_resolution") or {}
    assert domain.get("fixed_domain_key") == "statistics.descriptive_statistics"
    assert domain.get("resolution_source") == "derived_capability_match"
    assert domain.get("binding_status") == "derived"
    assert domain.get("selected_operation")
    assert domain.get("matched_capabilities")
    assert domain.get("domain_module")
    assert domain.get("entrypoint")
    assert not validate_component_domain_evidence(spec)

    for key in (
        "problem_type_id",
        "fixed_domain_key",
        "selected_operation",
        "required_capabilities",
        "matched_capabilities",
        "presentation_mode",
    ):
        assert spec.get(key), key

    assert spec.get("answer_type") or spec.get("answer_contract")


def test_batch_continues_when_one_example_fails(
    memory_conn: sqlite3.Connection,
    dryrun_root: Path,
) -> None:
    batch = run_admin_v3_dryrun_for_skill(
        memory_conn,
        UNREGISTERED_SKILL,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
        mode="regenerate",
        force=True,
    )

    assert batch["total_examples"] == 2
    assert batch["processed_count"] == 2
    assert batch["failed_count"] >= 1
    assert batch["success_count"] >= 1
    statuses = {row["textbook_example_id"]: row["status"] for row in batch["results"]}
    assert MEAN_EXAMPLE_ID in statuses
    assert OPAQUE_EXAMPLE_ID in statuses
    assert statuses[MEAN_EXAMPLE_ID] == "processed"


def test_publish_eligibility_does_not_require_skill_registry(
    memory_conn: sqlite3.Connection,
    dryrun_root: Path,
) -> None:
    run_admin_v3_dryrun_for_example(
        conn=memory_conn,
        textbook_example_id=MEAN_EXAMPLE_ID,
        skill_id=UNREGISTERED_SKILL,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
        allow_non_mvp_skill=True,
    )
    coverage = get_v3_skill_component_coverage(memory_conn, UNREGISTERED_SKILL)
    eligibility = evaluate_v3_publish_eligibility(memory_conn, UNREGISTERED_SKILL, coverage=coverage)

    assert UNREGISTERED_SKILL not in taxonomy_registry.SKILL_TO_DOMAIN
    assert eligibility["reason"] != "DOMAIN_BINDING_MISSING"
    assert int(eligibility.get("eligible_component_count") or 0) >= 1


def test_preview_can_execute_generated_component(
    memory_conn: sqlite3.Connection,
    dryrun_root: Path,
) -> None:
    run_admin_v3_dryrun_for_example(
        conn=memory_conn,
        textbook_example_id=MEAN_EXAMPLE_ID,
        skill_id=UNREGISTERED_SKILL,
        dryrun_base_dir=str(dryrun_root),
        seed=42,
        allow_non_mvp_skill=True,
    )
    generate_path = (
        dryrun_root / UNREGISTERED_SKILL / "components" / f"src_{MEAN_EXAMPLE_ID}" / "generate.py"
    )
    spec = importlib.util.spec_from_file_location("preview_gen", generate_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.generate(seed=42)
    assert isinstance(payload, dict)
    question_text = str(payload.get("question_text") or payload.get("question") or "").strip()
    assert question_text
    assert payload.get("fixed_domain_key") == "statistics.descriptive_statistics"

    hint_path = generate_path.parent / "get_hint.py"
    hint_spec = importlib.util.spec_from_file_location("preview_hint", hint_path)
    assert hint_spec and hint_spec.loader
    hint_mod = importlib.util.module_from_spec(hint_spec)
    hint_spec.loader.exec_module(hint_mod)
    hint = hint_mod.get_hint(step=1, question_payload=payload)
    assert str(hint or "").strip()


def test_closed_loop_service_starts_derived_binding_skill(
    memory_conn: sqlite3.Connection,
    dryrun_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = dryrun_root / "project"
    staging_root = dryrun_root / "staging"
    project_root.mkdir(parents=True, exist_ok=True)
    staging_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(
        "core.gencode.pipeline_orchestrator.V3_PRODUCTION_PUBLISH_ENABLED",
        False,
    )

    result = run_admin_v3_dryrun_publish_closed_loop_for_skill(
        memory_conn,
        UNREGISTERED_SKILL,
        project_root=str(project_root),
        staging_root=str(staging_root),
        smoke=False,
        verify=False,
        force=True,
        mode="regenerate",
        dryrun_base_dir=str(dryrun_root),
        seed=42,
    )

    assert result.get("generation") is not None
    assert int(result["generation"].get("verified_count") or 0) >= 1
    assert result["publish"]["attempted"] is False


def test_admin_route_wires_closed_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def _fake_closed_loop(conn, skill_id, **kwargs):
        calls.append(str(skill_id))
        return {
            "success": True,
            "generation": {"success_count": 1, "verified_count": 1, "total_examples": 1},
            "publish": {"attempted": False, "published": False},
            "publish_eligibility": {"allowed": True, "reason": "eligible"},
        }

    monkeypatch.setattr(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_publish_closed_loop_for_skill",
        _fake_closed_loop,
    )
    monkeypatch.setattr(
        "core.gencode.v3_production_publish_service.resolve_and_validate_v3_publish_roots",
        lambda *_a, **_k: (PROJECT_ROOT, PROJECT_ROOT / "staging_unused"),
    )

    from app import create_app

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True
        response = client.post(
            f"/admin/skills/{UNREGISTERED_SKILL}/gencode_v3_dryrun",
            json={"force": True, "mode": "regenerate", "smoke": False, "verify": False},
        )

    assert response.status_code == 200
    assert calls == [UNREGISTERED_SKILL]


@pytest.mark.parametrize("relative_path", _GENCODE_TOUCHED_FILES)
def test_production_changes_have_no_skill_specific_hacks(relative_path: str) -> None:
    path = PROJECT_ROOT / relative_path
    if not path.is_file():
        pytest.skip(f"missing {relative_path}")
    content = path.read_text(encoding="utf-8")
    assert "CentralTendencyMeasures" not in content
    assert "3835" not in content
    assert "3887" not in content
