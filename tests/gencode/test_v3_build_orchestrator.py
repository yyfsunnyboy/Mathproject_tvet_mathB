# -*- coding: utf-8 -*-
"""Tests for one-click Gencode V3 build orchestrator + readiness semantics."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from unittest import mock

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.v3_build_orchestrator_service import (
    JOB_STATUS_NEEDS_CAPABILITY,
    JOB_STATUS_READY,
    derive_skill_v3_ui_status,
    ensure_orchestrator_jobs_table,
    get_orchestrator_job,
    run_v3_build_orchestrator,
)
from core.gencode.services.v3_example_disposition import (
    DISPOSITION_INTENTIONAL_SKIP,
    DISPOSITION_NEEDS_CAPABILITY,
    DISPOSITION_RESOLVABLE,
    disposition_from_phase1_probe,
    is_intentional_skip_signal,
)
from core.gencode.services.v3_skill_capability_preflight_service import (
    CAPABILITY_NEEDS_CAPABILITY,
    CAPABILITY_READY,
    evaluate_skill_v3_capability,
)
from core.gencode.services.v3_skill_coverage_service import get_v3_skill_component_coverage


B2_CH2_SKILLS = [
    "vh_數學B2_SubSection_2_1_1",
    "vh_數學B2_SubSection_2_1_2",
    "vh_數學B2_SubSection_2_2_3",
    "vh_數學B2_SubSection_2_2_4",
    "vh_數學B2_SubSection_2_2_5",
]


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            problem_text TEXT,
            correct_answer TEXT,
            detailed_solution TEXT,
            source_description TEXT,
            problem_type TEXT,
            notes TEXT
        )
        """
    )
    apply_tracker_ddl(conn)
    ensure_orchestrator_jobs_table(conn)
    return conn


def _insert_examples(conn: sqlite3.Connection, skill_id: str, ids: list[int]) -> None:
    for eid in ids:
        conn.execute(
            """
            INSERT INTO textbook_examples (
                id, skill_id, problem_text, correct_answer, detailed_solution,
                source_description, problem_type, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (eid, skill_id, f"p{eid}", f"a{eid}", "", f"src_{eid}", "t", ""),
        )
    conn.commit()


def _wiring_ok() -> dict:
    return {
        "fixed_domain_key": "demo_domain",
        "domain_module": "types",
        "entrypoint": "SimpleNamespace",
        "registry_revision": "test",
        "allowed_operations": ["demo_op"],
    }


def test_intentional_skip_signal_detects_blocked():
    assert is_intentional_skip_signal(reason="BLOCKED:manual_review")
    assert is_intentional_skip_signal(classification_source="phase1_rule_pack_blocked")
    assert not is_intentional_skip_signal(reason="unresolved_other")


def test_disposition_maps_blocked_to_intentional_skip():
    d = disposition_from_phase1_probe(
        {
            "textbook_example_id": 11706,
            "resolvable": False,
            "reason": "BLOCKED:outer_circle_radius",
            "classification_source": "phase1_rule_pack_blocked",
        }
    )
    assert d["disposition"] == DISPOSITION_INTENTIONAL_SKIP


def test_all_eligible_published_plus_intentional_skip_is_ready():
    """Case 1+2: intentional skip does not block READY / rebuild."""
    skill_id = "vh_test_ready_with_skip"
    conn = _conn()
    _insert_examples(conn, skill_id, [1, 2, 3])

    def _probe(**kwargs):
        eid = int(kwargs["row"]["id"])
        if eid == 3:
            return {
                "textbook_example_id": eid,
                "resolvable": False,
                "reason": "BLOCKED:too_complex",
                "classification_source": "phase1_rule_pack_blocked",
                "problem_type_id": "",
            }
        return {
            "textbook_example_id": eid,
            "resolvable": True,
            "reason": "",
            "classification_source": "phase1_rule_pack",
            "problem_type_id": "demo_op",
        }

    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        return_value=_wiring_ok(),
    ), mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service._probe_example_resolvable",
        side_effect=_probe,
    ):
        preflight = evaluate_skill_v3_capability(conn, skill_id)

    assert preflight["capability_status"] == CAPABILITY_READY
    assert preflight["allow_v3_rebuild"] is True
    assert preflight["intentional_skip_count"] == 1
    assert preflight["eligible_example_count"] == 2
    assert preflight["needs_capability_count"] == 0

    # Tracker: 2 verified + 1 intentional skip
    for eid in (1, 2):
        conn.execute(
            """
            INSERT INTO gencode_component_tracker
            (textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload)
            VALUES (?, ?, ?, 'verified', ?)
            """,
            (eid, skill_id, f"src_{eid}", '{"integrity_gate_passed": true, "integrity_gate_version": "v1", "answer_type": "expression", "checker_key": "numeric_checker", "equivalence_type": "numeric", "fixed_domain_key": "demo_domain", "domain_operation": "demo_op"}'),
        )
    conn.execute(
        """
        INSERT INTO gencode_component_tracker
        (textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload, gencode_error_log)
        VALUES (?, ?, ?, 'needs_human_review', ?, ?)
        """,
        (
            3,
            skill_id,
            "src_3",
            '{"classification_status":"unresolved","phase1_classification":{"reason":"BLOCKED:too_complex","classification_source":"phase1_rule_pack_blocked"}}',
            "PHASE1_CLASSIFICATION_UNRESOLVED: BLOCKED:too_complex",
        ),
    )
    conn.commit()
    coverage = get_v3_skill_component_coverage(conn, skill_id)
    assert coverage["intentional_skip_count"] == 1
    assert coverage["eligible_count"] == 2
    assert coverage["verified_count"] == 2
    assert coverage["publish_ready"] is True

    ui = derive_skill_v3_ui_status(
        capability_status=CAPABILITY_READY,
        coverage=coverage,
        job=None,
    )
    assert ui["ui_status"] == "READY"
    assert ui["allow_v3_rebuild"] is True


def test_truly_missing_domain_stops_as_needs_capability(tmp_path: Path):
    """Case 4: NEEDS_CAPABILITY does not write production."""
    skill_id = "vh_test_needs_cap"
    conn = _conn()
    _insert_examples(conn, skill_id, [10, 11])
    prod_before = tmp_path / "skills" / f"{skill_id}.py"
    (tmp_path / "skills").mkdir(parents=True, exist_ok=True)
    prod_before.write_text("# old healthy\n", encoding="utf-8")
    before_hash = hashlib.sha256(prod_before.read_bytes()).hexdigest()

    def _probe(**kwargs):
        eid = int(kwargs["row"]["id"])
        return {
            "textbook_example_id": eid,
            "resolvable": False,
            "reason": "no_matching_operation",
            "classification_source": "phase1_unresolved",
            "problem_type_id": "",
            "suggested_domain": "missing.op",
        }

    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        return_value=_wiring_ok(),
    ), mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service._probe_example_resolvable",
        side_effect=_probe,
    ), mock.patch(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_skill"
    ) as dryrun_mock, mock.patch(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_publish_for_skill"
    ) as publish_mock:
        result = run_v3_build_orchestrator(
            conn,
            skill_id,
            project_root=str(tmp_path),
            staging_root=str(tmp_path / "staging"),
        )

    assert result["status"] == JOB_STATUS_NEEDS_CAPABILITY
    assert result["counts"]["needs_capability_count"] == 2
    assert result["production_preserved"] is True
    dryrun_mock.assert_not_called()
    publish_mock.assert_not_called()
    assert hashlib.sha256(prod_before.read_bytes()).hexdigest() == before_hash
    job = get_orchestrator_job(conn, skill_id)
    assert job is not None
    assert job["status"] == JOB_STATUS_NEEDS_CAPABILITY


def test_unregistered_domain_soft_stops_as_needs_capability_not_failed_missing(tmp_path: Path):
    """B2 Ch3-class failure: skill has examples but taxonomy registry has no binding.

    Must soft-stop as needs_capability with non-zero needs_capability_count.
    Must NOT Finalize as failed CAPABILITY_MATCH: missing with zeroed counts.
    """
    from core.registry.taxonomy_registry import SkillDomainNotRegisteredError

    skill_id = "vh_test_unregistered_domain"
    conn = _conn()
    _insert_examples(conn, skill_id, [11754, 11755])
    prod_before = tmp_path / "skills" / f"{skill_id}.py"
    (tmp_path / "skills").mkdir(parents=True, exist_ok=True)
    prod_before.write_text("# preserve me\n", encoding="utf-8")
    before_hash = hashlib.sha256(prod_before.read_bytes()).hexdigest()

    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        side_effect=SkillDomainNotRegisteredError(
            f"skill_domain_not_registered: {skill_id!r}"
        ),
    ), mock.patch(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_skill"
    ) as dryrun_mock, mock.patch(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_publish_for_skill"
    ) as publish_mock:
        result = run_v3_build_orchestrator(
            conn,
            skill_id,
            project_root=str(tmp_path),
            staging_root=str(tmp_path / "staging"),
        )

    assert result["status"] == JOB_STATUS_NEEDS_CAPABILITY
    assert result["counts"]["example_count"] == 2
    assert result["counts"]["needs_capability_count"] == 2
    assert result["counts"]["published_count"] == 0
    assert len(result["needs_capability_examples"]) == 2
    assert all(
        str(item.get("reason") or "") == "domain_registry_missing"
        for item in result["needs_capability_examples"]
    )
    assert result["production_preserved"] is True
    assert str(result["final_status"]).lower() == JOB_STATUS_NEEDS_CAPABILITY
    assert not any(
        str((err or {}).get("code") or "") == "CAPABILITY_NOT_READY"
        for err in (result.get("errors") or [])
    )
    dryrun_mock.assert_not_called()
    publish_mock.assert_not_called()
    assert hashlib.sha256(prod_before.read_bytes()).hexdigest() == before_hash
    stages = {str(s.get("name")): s for s in (result.get("stages") or [])}
    assert stages.get("CAPABILITY_MATCH", {}).get("status") == "done"
    assert stages.get("FINALIZE", {}).get("status") == "needs_capability"
    assert stages.get("COMPONENT_BUILD", {}).get("status") == "skipped"
    job = get_orchestrator_job(conn, skill_id)
    assert job is not None
    # capability detail lives in durable job payload
    row = conn.execute(
        "SELECT payload_json FROM gencode_v3_orchestrator_jobs WHERE skill_id = ?",
        (skill_id,),
    ).fetchone()
    payload = json.loads(row[0] if not hasattr(row, "keys") else row["payload_json"])
    assert payload["capability"]["capability_status"] == "missing"
    assert "domain_registry_binding" in (payload["capability"].get("missing_layers") or [])


def test_orchestrator_auto_matches_existing_capability_and_is_idempotent(tmp_path: Path):
    """Case 3+5: existing capability matched; rerun does not rebuild published."""
    skill_id = "vh_test_idempotent"
    conn = _conn()
    _insert_examples(conn, skill_id, [21, 22])
    for eid in (21, 22):
        conn.execute(
            """
            INSERT INTO gencode_component_tracker
            (textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload)
            VALUES (?, ?, ?, 'verified', ?)
            """,
            (
                eid,
                skill_id,
                f"src_{eid}",
                '{"integrity_gate_passed": true, "integrity_gate_version": "v1", "answer_type": "expression", "checker_key": "numeric_checker", "equivalence_type": "numeric", "fixed_domain_key": "demo_domain", "domain_operation": "demo_op"}',
            ),
        )
    conn.commit()

    def _probe(**kwargs):
        eid = int(kwargs["row"]["id"])
        return {
            "textbook_example_id": eid,
            "resolvable": True,
            "reason": "",
            "classification_source": "phase1_rule_pack",
            "problem_type_id": "demo_op",
        }

    dryrun_calls = {"n": 0}

    def _dryrun(*args, **kwargs):
        dryrun_calls["n"] += 1
        return {
            "success": True,
            "rebuilt_count": 0,
            "skipped_count": 2,
            "intentional_skip_count": 0,
            "failed_count": 0,
            "user_message": "idempotent",
        }

    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        return_value=_wiring_ok(),
    ), mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service._probe_example_resolvable",
        side_effect=_probe,
    ), mock.patch(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_skill",
        side_effect=_dryrun,
    ), mock.patch(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_publish_for_skill"
    ) as publish_mock, mock.patch(
        "core.gencode.services.admin_gencode_action_service._prepare_publish_staging_components"
    ), mock.patch(
        "core.gencode.services.v3_publish_eligibility.evaluate_v3_publish_eligibility",
        return_value={"allowed": True, "reason": "eligible", "full_coverage": True},
    ):
        result1 = run_v3_build_orchestrator(
            conn,
            skill_id,
            project_root=str(tmp_path),
            staging_root=str(tmp_path / "staging"),
            force=False,
        )
        result2 = run_v3_build_orchestrator(
            conn,
            skill_id,
            project_root=str(tmp_path),
            staging_root=str(tmp_path / "staging"),
            force=False,
        )

    assert result1["status"] == JOB_STATUS_READY
    assert result1["allow_v3_rebuild"] is True
    assert result1.get("idempotent") is True
    assert result2["status"] == JOB_STATUS_READY
    assert result2.get("idempotent") is True
    publish_mock.assert_not_called()
    assert dryrun_calls["n"] >= 1


def test_resume_from_smoke_stage(tmp_path: Path):
    """Case 6: partial previous job resumes from later stage path."""
    skill_id = "vh_test_resume"
    conn = _conn()
    _insert_examples(conn, skill_id, [31])
    conn.execute(
        """
        INSERT INTO gencode_component_tracker
        (textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload)
        VALUES (31, ?, 'src_31', 'verified', ?)
        """,
        (
            skill_id,
            '{"integrity_gate_passed": true, "integrity_gate_version": "v1", "answer_type": "expression", "checker_key": "numeric_checker", "equivalence_type": "numeric", "fixed_domain_key": "demo_domain", "domain_operation": "demo_op"}',
        ),
    )
    # Seed a failed job stuck at SMOKE_TEST
    ensure_orchestrator_jobs_table(conn)
    conn.execute(
        """
        INSERT INTO gencode_v3_orchestrator_jobs
        (job_id, skill_id, stage, status, started_at, updated_at, payload_json)
        VALUES ('job_resume', ?, 'SMOKE_TEST', 'failed', 't0', 't0', ?)
        """,
        (
            skill_id,
            '{"stages":{},"counts":{"example_count":1,"eligible_count":1},"errors":[{"stage":"SMOKE_TEST","code":"SMOKE_FAILED","message":"boom"}],"skip_examples":[],"needs_capability_examples":[]}',
        ),
    )
    conn.commit()

    def _probe(**kwargs):
        return {
            "textbook_example_id": 31,
            "resolvable": True,
            "reason": "",
            "classification_source": "phase1_rule_pack",
            "problem_type_id": "demo_op",
        }

    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        return_value=_wiring_ok(),
    ), mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service._probe_example_resolvable",
        side_effect=_probe,
    ), mock.patch(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_skill",
        return_value={
            "success": True,
            "rebuilt_count": 0,
            "skipped_count": 1,
            "intentional_skip_count": 0,
            "failed_count": 0,
        },
    ), mock.patch(
        "core.gencode.services.v3_publish_eligibility.evaluate_v3_publish_eligibility",
        return_value={"allowed": True, "reason": "eligible", "full_coverage": True},
    ), mock.patch(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_publish_for_skill"
    ):
        result = run_v3_build_orchestrator(
            conn,
            skill_id,
            project_root=str(tmp_path),
            staging_root=str(tmp_path / "staging"),
            resume=True,
        )

    assert result["status"] == JOB_STATUS_READY
    assert result["job_id"] == "job_resume"


def test_smoke_failure_preserves_production(tmp_path: Path):
    """Case 7: smoke failure keeps previous production package."""
    skill_id = "vh_test_smoke_fail"
    conn = _conn()
    _insert_examples(conn, skill_id, [41])
    conn.execute(
        """
        INSERT INTO gencode_component_tracker
        (textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload)
        VALUES (41, ?, 'src_41', 'verified', ?)
        """,
        (
            skill_id,
            '{"integrity_gate_passed": true, "integrity_gate_version": "v1", "answer_type": "expression", "checker_key": "numeric_checker", "equivalence_type": "numeric", "fixed_domain_key": "demo_domain", "domain_operation": "demo_op"}',
        ),
    )
    conn.commit()
    (tmp_path / "skills").mkdir(parents=True, exist_ok=True)
    prod = tmp_path / "skills" / f"{skill_id}.py"
    prod.write_text("# healthy production\n", encoding="utf-8")
    before = prod.read_text(encoding="utf-8")

    def _probe(**kwargs):
        return {
            "textbook_example_id": 41,
            "resolvable": True,
            "reason": "",
            "classification_source": "phase1_rule_pack",
            "problem_type_id": "demo_op",
        }

    def _dryrun(*args, **kwargs):
        if kwargs.get("smoke"):
            return {"success": False, "rebuilt_count": 0, "failed_count": 1, "user_message": "smoke_failed"}
        return {"success": True, "rebuilt_count": 1, "skipped_count": 0, "intentional_skip_count": 0, "failed_count": 0}

    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        return_value=_wiring_ok(),
    ), mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service._probe_example_resolvable",
        side_effect=_probe,
    ), mock.patch(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_skill",
        side_effect=_dryrun,
    ), mock.patch(
        "core.gencode.services.v3_publish_eligibility.evaluate_v3_publish_eligibility",
        return_value={"allowed": True, "reason": "eligible", "full_coverage": True},
    ), mock.patch(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_publish_for_skill"
    ) as publish_mock:
        result = run_v3_build_orchestrator(
            conn,
            skill_id,
            project_root=str(tmp_path),
            staging_root=str(tmp_path / "staging"),
            smoke=True,
        )

    assert result["status"] == "failed"
    assert result["stage"] == "SMOKE_TEST"
    assert result["production_preserved"] is True
    publish_mock.assert_not_called()
    assert prod.read_text(encoding="utf-8") == before


def test_production_package_reuse_is_idempotent(tmp_path: Path):
    """Existing production package + intentional skip → READY without rebuild."""
    skill_id = "vh_test_pkg_ready"
    conn = _conn()
    _insert_examples(conn, skill_id, [61, 62, 63])
    # Production package for eligible only
    for eid in (61, 62):
        d = tmp_path / "agent_skills_v3" / skill_id / "components" / f"src_{eid}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "generate.py").write_text("def generate():\n    return {}\n", encoding="utf-8")
    (tmp_path / "agent_skills_v3" / skill_id).mkdir(parents=True, exist_ok=True)
    (tmp_path / "agent_skills_v3" / skill_id / "__init__.py").write_text("GENERATOR_SPECS=[]\n", encoding="utf-8")
    (tmp_path / "skills").mkdir(parents=True, exist_ok=True)
    (tmp_path / "skills" / f"{skill_id}.py").write_text("# facade\n", encoding="utf-8")

    def _probe(**kwargs):
        eid = int(kwargs["row"]["id"])
        if eid == 63:
            return {
                "textbook_example_id": eid,
                "resolvable": False,
                "reason": "BLOCKED:skip",
                "classification_source": "phase1_rule_pack_blocked",
                "problem_type_id": "",
            }
        return {
            "textbook_example_id": eid,
            "resolvable": True,
            "reason": "",
            "classification_source": "phase1_rule_pack",
            "problem_type_id": "demo_op",
        }

    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        return_value=_wiring_ok(),
    ), mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service._probe_example_resolvable",
        side_effect=_probe,
    ), mock.patch(
        "core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_skill"
    ) as dryrun_mock:
        result = run_v3_build_orchestrator(
            conn,
            skill_id,
            project_root=str(tmp_path),
            staging_root=str(tmp_path / "staging"),
            force=False,
            mode="auto",
        )

    assert result["status"] == JOB_STATUS_READY
    assert result["idempotent"] is True
    assert result["counts"]["skip_count"] == 1
    assert result["counts"]["published_count"] == 2
    dryrun_mock.assert_not_called()


def test_production_db_not_touched_by_unit_suite():
    """Case 9: unit tests must not mutate production DB bytes."""
    prod = Path("instance/kumon_math.db")
    if not prod.exists():
        pytest.skip("production db missing")
    before = hashlib.sha256(prod.read_bytes()).hexdigest()
    # Run a tiny in-memory orchestrator path
    conn = _conn()
    _insert_examples(conn, "vh_mem_only", [99])
    after = hashlib.sha256(prod.read_bytes()).hexdigest()
    assert before == after


def test_outline_skill_cannot_start_v3(tmp_path: Path):
    """Case 8."""
    conn = _conn()
    with pytest.raises(ValueError, match="outline_skill"):
        run_v3_build_orchestrator(
            conn,
            "outline_section_demo",
            project_root=str(tmp_path),
            staging_root=str(tmp_path / "staging"),
        )


def test_preflight_missing_capability_status():
    skill_id = "vh_test_nc"
    conn = _conn()
    _insert_examples(conn, skill_id, [51, 52])

    def _probe(**kwargs):
        eid = int(kwargs["row"]["id"])
        if eid == 52:
            return {
                "textbook_example_id": eid,
                "resolvable": False,
                "reason": "missing_op",
                "classification_source": "x",
                "problem_type_id": "",
            }
        return {
            "textbook_example_id": eid,
            "resolvable": True,
            "reason": "",
            "classification_source": "phase1_rule_pack",
            "problem_type_id": "demo_op",
        }

    with mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service.resolve_domain_for_skill",
        return_value=_wiring_ok(),
    ), mock.patch(
        "core.gencode.services.v3_skill_capability_preflight_service._probe_example_resolvable",
        side_effect=_probe,
    ):
        preflight = evaluate_skill_v3_capability(conn, skill_id)
    assert preflight["capability_status"] == CAPABILITY_NEEDS_CAPABILITY
    assert preflight["allow_v3_rebuild"] is False


@pytest.mark.parametrize("skill_id", B2_CH2_SKILLS)
def test_b2_ch2_regression_fixture_ready(skill_id: str):
    """Case 10: B2 Chapter 2 skills are READY with intentional skips allowed."""
    inventory_path = Path("reports/b2_ch2_v3_final_acceptance_inventory.json")
    if not inventory_path.exists():
        pytest.skip("B2 Ch2 acceptance inventory not present")
    import json

    inv = json.loads(inventory_path.read_text(encoding="utf-8"))
    skill = inv["skills"][skill_id]
    eligible = int(skill["example_count"]) - int(skill["skipped_count"])
    assert int(skill["published_count"]) == eligible
    assert int(skill["missing"]) if not isinstance(skill["missing"], list) else len(skill["missing"]) == 0
    assert skill["equation_ok"] is True

    ui = derive_skill_v3_ui_status(
        capability_status=CAPABILITY_READY,
        coverage={
            "eligible_count": eligible,
            "verified_count": int(skill["published_count"]),
            "published_count": int(skill["published_count"]),
            "missing_tracker_count": 0,
            "publish_ready": True,
            "intentional_skip_count": int(skill["skipped_count"]),
        },
    )
    assert ui["ui_status"] == "READY"
    assert ui["allow_v3_rebuild"] is True


def test_v3_entry_visibility_uses_build_cta():
    """UI shows 建立 V3 / REBUILD / NEEDS_CAPABILITY; outline hidden."""
    from flask import render_template
    import re
    from app import app

    cases = [
        ("vh_數學B2_SubSection_2_1_1", "READY", True, "REBUILD"),
        ("vh_數學B2_SubSection_2_1_2", "建立 V3", False, "建立 V3"),
        ("vh_test_leaf", "NEEDS_CAPABILITY", False, "NEEDS_CAPABILITY"),
        ("outline_test_section", "建立 V3", False, None),
    ]
    for skill_id, v3_ui, allow_rebuild, expected in cases:
        skill = {
            "skill_id": skill_id,
            "skill_ch_name": "Test",
            "is_active": True,
            "curriculum": "vocational",
            "grade": 10,
            "volume": "數學B2",
            "chapter": "2",
            "section": "2-1",
        }
        gencode = {
            "capability_status": "ready" if v3_ui == "READY" else ("needs_capability" if v3_ui == "NEEDS_CAPABILITY" else "missing"),
            "allow_v3_rebuild": allow_rebuild,
            "v3_ui_status": v3_ui,
            "v3_cta_label": expected or "",
            "publish_ready": v3_ui == "READY",
            "production_wrapper_exists": False,
            "v3_package_exists": False,
        }
        with app.test_request_context():
            html = render_template(
                "admin_skills.html",
                skills=[skill],
                v3_gencode_status_map={skill_id: gencode},
                gencode_status_map={},
                filters={"curricula": [], "grades": [], "volumes": [], "chapters": [], "sections": []},
                selected_filters={
                    "f_curriculum": "all",
                    "f_grade": "all",
                    "f_volume": "all",
                    "f_chapter": "all",
                    "f_section": "all",
                },
                grade_map={},
                curriculum_map={},
                username="admin",
            )
        row = html.split('<td class="v3-cell">', 1)[1].split("</tr>", 1)[0]
        actions = row.split('class="v3-actions"', 1)[-1] if 'class="v3-actions"' in row else row
        if expected is None:
            assert "建立 V3" not in actions
            assert "REBUILD" not in actions
            assert "NEEDS_CAPABILITY" not in actions
            assert "outline skill" in row
        else:
            assert expected in actions
