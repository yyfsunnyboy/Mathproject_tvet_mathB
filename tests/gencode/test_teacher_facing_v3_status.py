# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
import json
import os
import sqlite3

from core.gencode.services.gencode_status_query_service import (
    inspect_component_production_sync,
    resolve_teacher_facing_v3_status,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_teacher_status_not_generated_without_tracker_or_component():
    status = resolve_teacher_facing_v3_status(
        gencode_status="not_created",
        has_tracker=False,
        has_component=False,
    )
    assert status["status_key"] == "not_generated"
    assert status["label"] == "尚未生成"


def test_teacher_status_generating_for_running_state():
    status = resolve_teacher_facing_v3_status(
        gencode_status="generating",
        has_tracker=True,
        has_component=True,
    )
    assert status["status_key"] == "generating"
    assert status["label"] == "生成中"


def test_teacher_status_verified_not_synced_is_generated_not_packaged():
    status = resolve_teacher_facing_v3_status(
        gencode_status="verified",
        has_tracker=True,
        has_component=True,
        production_contains_latest=False,
    )
    assert status["status_key"] == "generated_not_packaged"
    assert status["label"] == "尚未上線"


def test_teacher_status_failed_is_generation_failed():
    status = resolve_teacher_facing_v3_status(
        gencode_status="failed",
        has_tracker=True,
        has_component=True,
    )
    assert status["status_key"] == "failed"
    assert status["label"] == "生成失敗"


def test_teacher_status_published_only_when_latest_component_is_synced():
    status = resolve_teacher_facing_v3_status(
        gencode_status="verified",
        has_tracker=True,
        has_component=True,
        production_contains_latest=True,
    )
    assert status["status_key"] == "published"
    assert status["label"] == "已經上線"


def test_production_sync_requires_matching_component_hash(tmp_path: Path):
    skill_id = "vh_test_skill"
    component_id = "src_1"
    dryrun = tmp_path / "reports" / "gencode_v3_dryrun" / skill_id / "components" / component_id
    production = tmp_path / "agent_skills_v3" / skill_id / "components" / component_id
    dryrun.mkdir(parents=True)
    production.mkdir(parents=True)

    (dryrun / "generate.py").write_text("def generate():\n    return {'v': 1}\n", encoding="utf-8")
    (production / "generate.py").write_text("def generate():\n    return {'v': 1}\n", encoding="utf-8")
    synced = inspect_component_production_sync(
        skill_id=skill_id,
        component_id=component_id,
        project_root=tmp_path,
    )
    assert synced["production_contains_latest"] is True

    (production / "generate.py").write_text("def generate():\n    return {'v': 0}\n", encoding="utf-8")
    stale = inspect_component_production_sync(
        skill_id=skill_id,
        component_id=component_id,
        project_root=tmp_path,
    )
    assert stale["production_contains_latest"] is False


def _write_production_init(root: Path, skill_id: str, specs: list[dict[str, object]]) -> None:
    skill_dir = root / "agent_skills_v3" / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "__init__.py").write_text(
        f"SKILL_ID = {skill_id!r}\nGENERATOR_SPECS = {specs!r}\n",
        encoding="utf-8",
    )


def test_published_hash_matching_current_production_is_published(tmp_path: Path):
    skill_id = "vh_test_skill"
    component_id = "src_4566"
    production = tmp_path / "agent_skills_v3" / skill_id / "components" / component_id
    production.mkdir(parents=True)
    (production / "generate.py").write_text("def generate():\n    return {'v': 1}\n", encoding="utf-8")
    published_hash = inspect_component_production_sync(
        skill_id=skill_id,
        component_id=component_id,
        project_root=tmp_path,
    )["production_component_hash"]

    sync = inspect_component_production_sync(
        skill_id=skill_id,
        component_id=component_id,
        tracker_payload={"published_generate_sha256": published_hash},
        project_root=tmp_path,
    )

    assert sync["production_contains_latest"] is True
    assert sync["production_sync_method"] == "tracker_published_generate_sha256"


def test_verified_hash_different_from_production_is_not_packaged(tmp_path: Path):
    skill_id = "vh_test_skill"
    component_id = "src_4565"
    production = tmp_path / "agent_skills_v3" / skill_id / "components" / component_id
    production.mkdir(parents=True)
    (production / "generate.py").write_text("def generate():\n    return {'v': 1}\n", encoding="utf-8")

    sync = inspect_component_production_sync(
        skill_id=skill_id,
        component_id=component_id,
        tracker_payload={"verified_generate_sha256": "not-the-production-hash"},
        project_root=tmp_path,
    )

    assert sync["production_contains_latest"] is False
    assert sync["production_sync_reason"] in {"hash_mismatch", "production_manifest_missing_component"}


def test_dryrun_artifact_removed_but_published_hash_matches_is_published(tmp_path: Path):
    skill_id = "vh_test_skill"
    component_id = "src_4566"
    production = tmp_path / "agent_skills_v3" / skill_id / "components" / component_id
    production.mkdir(parents=True)
    (production / "generate.py").write_text("def generate():\n    return {'v': 2}\n", encoding="utf-8")
    production_hash = inspect_component_production_sync(
        skill_id=skill_id,
        component_id=component_id,
        project_root=tmp_path,
    )["production_component_hash"]

    sync = inspect_component_production_sync(
        skill_id=skill_id,
        component_id=component_id,
        tracker_payload={"published_generate_sha256": production_hash},
        project_root=tmp_path,
    )

    assert sync["verified_component_hash"] is None
    assert sync["production_contains_latest"] is True


def test_new_skill_dryrun_does_not_downgrade_legacy_published_component(tmp_path: Path):
    skill_id = "vh_test_skill"
    component_id = "src_4566"
    dryrun = tmp_path / "reports" / "gencode_v3_dryrun" / skill_id / "components" / component_id
    production = tmp_path / "agent_skills_v3" / skill_id / "components" / component_id
    dryrun.mkdir(parents=True)
    production.mkdir(parents=True)
    (dryrun / "generate.py").write_text("def generate():\n    return {'v': 'new'}\n", encoding="utf-8")
    (production / "generate.py").write_text("def generate():\n    return {'v': 'published'}\n", encoding="utf-8")
    _write_production_init(
        tmp_path,
        skill_id,
        [{"component_id": component_id, "textbook_example_id": 4566, "problem_type_id": "p"}],
    )
    old_time = 1_700_000_000
    new_time = 1_800_000_000
    os.utime(production / "generate.py", (new_time, new_time))
    os.utime(tmp_path / "agent_skills_v3" / skill_id / "__init__.py", (new_time, new_time))

    sync = inspect_component_production_sync(
        skill_id=skill_id,
        component_id=component_id,
        textbook_example_id=4566,
        tracker_updated_at="2023-11-14 22:13:20",
        project_root=tmp_path,
    )

    assert old_time < new_time
    assert sync["production_contains_latest"] is True
    assert sync["production_sync_method"] == "legacy_generator_specs_component_match"


def test_production_file_without_verified_or_published_evidence_is_not_published(tmp_path: Path):
    skill_id = "vh_test_skill"
    component_id = "src_9999"
    production = tmp_path / "agent_skills_v3" / skill_id / "components" / component_id
    production.mkdir(parents=True)
    (production / "generate.py").write_text("def generate():\n    return {'v': 1}\n", encoding="utf-8")

    sync = inspect_component_production_sync(
        skill_id=skill_id,
        component_id=component_id,
        project_root=tmp_path,
    )

    assert sync["production_contains_latest"] is False
    assert sync["production_sync_reason"] == "missing_verified_or_published_hash"


def test_draft_written_is_not_teacher_stable_draft_label():
    status = resolve_teacher_facing_v3_status(
        gencode_status="draft_written",
        has_tracker=True,
        has_component=True,
    )
    assert status["status_key"] == "generation_incomplete"
    assert status["label"] == "生成未完成"


def test_draft_written_with_generated_artifact_is_not_packaged():
    status = resolve_teacher_facing_v3_status(
        gencode_status="draft_written",
        has_tracker=True,
        has_component=True,
        has_generated_artifact=True,
    )
    assert status["status_key"] == "generated_not_packaged"


def test_verified_tracker_without_dryrun_files_is_not_packaged():
    status = resolve_teacher_facing_v3_status(
        gencode_status="verified",
        has_tracker=True,
        has_component=False,
        has_generated_artifact=False,
        production_contains_latest=False,
    )
    assert status["status_key"] == "generated_not_packaged"


def test_textbook_integer_id_links_to_src_component_key(tmp_path: Path):
    from core.gencode.services.gencode_status_query_service import build_admin_examples_gencode_status_map

    skill_id = "vh_test_skill"
    component_id = "src_4565"
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """
        CREATE TABLE gencode_component_tracker (
            id INTEGER PRIMARY KEY,
            textbook_example_id INTEGER,
            skill_id TEXT,
            component_id TEXT,
            gencode_status TEXT,
            induced_spec_payload TEXT,
            gencode_error_log TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status,
            induced_spec_payload, updated_at
        ) VALUES (?, ?, ?, 'verified', ?, '2026-06-20 12:00:00')
        """,
        (
            4565,
            skill_id,
            component_id,
            json.dumps({"integrity_gate_passed": True}, ensure_ascii=False),
        ),
    )
    dryrun = tmp_path / "reports" / "gencode_v3_dryrun" / skill_id / "components" / component_id
    dryrun.mkdir(parents=True)
    (dryrun / "generate.py").write_text("def generate():\n    return {}\n", encoding="utf-8")

    status_map = build_admin_examples_gencode_status_map(
        conn,
        [(4565, skill_id)],
        project_root=tmp_path,
    )
    assert status_map[4565]["component_id"] == component_id
    assert status_map[4565]["teacher_status"]["status_key"] == "generated_not_packaged"
    conn.close()


def test_examples_and_skills_templates_use_shared_teacher_status():
    examples = (PROJECT_ROOT / "templates" / "admin_examples.html").read_text(encoding="utf-8")
    skills = (PROJECT_ROOT / "templates" / "admin_skills.html").read_text(encoding="utf-8")

    assert "teacher_status = gencode.get('teacher_status'" in examples
    assert "teacher_status = gencode.get('teacher_status'" in skills
    assert "草稿已產生" not in examples
    assert "草稿已產生" not in skills


def test_teacher_main_operation_areas_hide_engineering_terms():
    examples = (PROJECT_ROOT / "templates" / "admin_examples.html").read_text(encoding="utf-8")
    skills = (PROJECT_ROOT / "templates" / "admin_skills.html").read_text(encoding="utf-8")

    examples_main = examples.split("function renderV3DrawerDetails(data, skillId)", 1)[1].split("<details", 1)[0]
    skills_main = skills.split('<div class="v3-summary-info"', 1)[1].split('<div class="v3-actions"', 1)[0]
    for term in ["Smoke", "Integrity", "Tracker", "publish_ready", "publish_eligible", "production_component_count"]:
        assert term not in examples_main
        assert term not in skills_main


def test_update_to_student_button_keeps_existing_repackage_endpoint():
    skills = (PROJECT_ROOT / "templates" / "admin_skills.html").read_text(encoding="utf-8")

    assert "更新到學生端" in skills
    assert "repackageSkillV3" in skills
    assert "core.admin_run_skill_v3_repackage" in skills
