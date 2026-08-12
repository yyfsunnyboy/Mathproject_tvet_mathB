# -*- coding: utf-8 -*-
"""Focused tests for validation-only V3 artifact reconciliation."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.component_tracker_service import derive_component_id
from core.gencode.services.gencode_status_query_service import (
    resolve_teacher_facing_v3_status,
)
from core.gencode.services.v3_artifact_reconciliation_service import (
    apply_tracker_sync_for_passed_component,
    reconcile_existing_artifacts,
    validate_existing_component,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture()
def recon_env(tmp_path: Path):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            problem_text TEXT
        )
        """
    )
    apply_tracker_ddl(conn)

    skill_id = "vh_test_recon_skill"
    example_id = 9001
    component_id = derive_component_id(example_id)
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id, problem_text) VALUES (?, ?, ?)",
        (example_id, skill_id, "解 $|x|=3$"),
    )
    conn.commit()

    def _write_component(base: Path) -> None:
        base.mkdir(parents=True, exist_ok=True)
        (base / "metadata.py").write_text(
            "\n".join(
                [
                    "COMPONENT_ID = 'src_9001'",
                    f"SKILL_ID = {skill_id!r}",
                    "TEXTBOOK_EXAMPLE_ID = 9001",
                    "PROBLEM_TYPE_ID = 'solve_basic_absolute_value_equation'",
                    "PRESENTATION_MODE = 'short_answer'",
                    "ANSWER_TYPE = 'expression'",
                ]
            ),
            encoding="utf-8",
        )
        (base / "get_hint.py").write_text(
            "def get_hint(step, question_payload=None):\n    return 'hint'\n",
            encoding="utf-8",
        )
        (base / "generate.py").write_text(
            "\n".join(
                [
                    "def generate(level=1, seed=None, component_id=None, **kwargs):",
                    "    return {",
                    "        'question_text': '解 $|x|=3$',",
                    "        'answer': 'x=3或x=-3',",
                    "        'correct_answer': 'x=3或x=-3',",
                    "        'answer_type': 'expression',",
                    "        'presentation_mode': 'short_answer',",
                    "        'problem_type_id': 'solve_basic_absolute_value_equation',",
                    "        'choices': [],",
                    "        'explanation': '',",
                    "        'component_id': component_id or 'src_9001',",
                    "        'answer_contract': {",
                    "            'answer_type': 'expression',",
                    "            'checker_key': 'linear_equation_equivalent_checker',",
                    "            'equivalence_type': 'linear_equation_equivalent',",
                    "        },",
                    "        'metadata': {'semantic_answer': 'x=3或x=-3'},",
                    "    }",
                ]
            ),
            encoding="utf-8",
        )

    dry = tmp_path / "reports" / "gencode_v3_dryrun" / skill_id / "components" / component_id
    prod = tmp_path / "agent_skills_v3" / skill_id / "components" / component_id
    _write_component(dry)
    _write_component(prod)

    yield {
        "conn": conn,
        "root": tmp_path,
        "skill_id": skill_id,
        "example_id": example_id,
        "component_id": component_id,
        "dry_generate": dry / "generate.py",
        "prod_generate": prod / "generate.py",
    }
    conn.close()


def test_validate_existing_does_not_change_hashes(recon_env):
    before_dry = _sha(recon_env["dry_generate"])
    before_prod = _sha(recon_env["prod_generate"])
    report = validate_existing_component(
        conn=recon_env["conn"],
        skill_id=recon_env["skill_id"],
        textbook_example_id=recon_env["example_id"],
        project_root=recon_env["root"],
    )
    assert report["hashes_unchanged"] is True
    assert _sha(recon_env["dry_generate"]) == before_dry
    assert _sha(recon_env["prod_generate"]) == before_prod
    assert report["production_file_changed"] is False


def test_reconcile_report_only_does_not_write_tracker(recon_env):
    result = reconcile_existing_artifacts(
        conn=recon_env["conn"],
        targets={recon_env["skill_id"]: [recon_env["example_id"]]},
        project_root=recon_env["root"],
        commit=False,
    )
    assert result["commit"] is False
    row = recon_env["conn"].execute(
        "SELECT COUNT(*) AS c FROM gencode_component_tracker"
    ).fetchone()
    assert int(row["c"]) == 0
    assert result["synced_count"] == 0


def test_reconcile_commit_writes_verified_only_when_passed(recon_env):
    result = reconcile_existing_artifacts(
        conn=recon_env["conn"],
        targets={recon_env["skill_id"]: [recon_env["example_id"]]},
        project_root=recon_env["root"],
        commit=True,
    )
    assert result["passed_count"] == 1
    assert result["synced_count"] == 1
    row = recon_env["conn"].execute(
        """
        SELECT gencode_status, induced_spec_payload
        FROM gencode_component_tracker
        WHERE textbook_example_id = ?
        """,
        (recon_env["example_id"],),
    ).fetchone()
    assert row["gencode_status"] == "verified"
    payload = json.loads(row["induced_spec_payload"])
    assert payload["validation_passed"] is True
    assert payload["verified_generate_sha256"] == _sha(recon_env["dry_generate"])
    assert payload["published_generate_sha256"] == _sha(recon_env["prod_generate"])
    assert payload["reconciliation"]["regenerate"] is False


def test_failed_validation_does_not_write_verified(recon_env):
    # Break production to force failure while leaving dryrun intact.
    recon_env["prod_generate"].write_text("def generate(**kwargs):\n    return 1\n", encoding="utf-8")
    result = reconcile_existing_artifacts(
        conn=recon_env["conn"],
        targets={recon_env["skill_id"]: [recon_env["example_id"]]},
        project_root=recon_env["root"],
        commit=True,
    )
    assert result["passed_count"] == 0
    assert result["synced_count"] == 0
    row = recon_env["conn"].execute(
        "SELECT COUNT(*) AS c FROM gencode_component_tracker"
    ).fetchone()
    assert int(row["c"]) == 0


def test_apply_sync_rejects_failed_report(recon_env):
    report = {
        "passed": False,
        "hashes_unchanged": True,
        "skill_id": recon_env["skill_id"],
        "textbook_example_id": recon_env["example_id"],
        "component_id": recon_env["component_id"],
    }
    with pytest.raises(ValueError, match="cannot_sync_failed_validation"):
        apply_tracker_sync_for_passed_component(
            conn=recon_env["conn"],
            validation_report=report,
            project_root=recon_env["root"],
        )


def test_teacher_status_deployed_pending_revalidation():
    status = resolve_teacher_facing_v3_status(
        gencode_status="verified",
        has_tracker=True,
        has_component=True,
        has_generated_artifact=True,
        production_contains_latest=True,
        hash_evidence_stale=True,
    )
    assert status["status_key"] == "deployed_pending_revalidation"
    assert status["label"] == "已部署，待重新驗證"


def test_teacher_status_generating_only_for_active_jobs():
    status = resolve_teacher_facing_v3_status(
        gencode_status="pending",
        has_tracker=True,
        has_component=True,
        has_generated_artifact=True,
        production_contains_latest=True,
        active_generation_job=False,
    )
    assert status["status_key"] != "generating"

    active = resolve_teacher_facing_v3_status(
        gencode_status="generating",
        has_tracker=True,
        has_component=True,
        active_generation_job=True,
    )
    assert active["status_key"] == "generating"
