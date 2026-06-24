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
    assert status["label"] == "尚待驗證或尚未生成"


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
    assert status["label"] == "已驗證／尚未封裝"


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


def test_regression_skill_partial_publishing_states(tmp_path: Path):
    # Setup sqlite connection & mock tracker data
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
    # Four textbook examples: 3826 (published/synced), 3827 (verified/not packaged), 3828 (draft/not generated), 3829 (failed)
    # 3826 is verified and production_contains_latest = True
    conn.execute(
        "INSERT INTO gencode_component_tracker (textbook_example_id, skill_id, component_id, gencode_status) VALUES (3826, 'vh_math', 'src_3826', 'verified')"
    )
    conn.execute(
        "INSERT INTO gencode_component_tracker (textbook_example_id, skill_id, component_id, gencode_status) VALUES (3827, 'vh_math', 'src_3827', 'verified')"
    )
    conn.execute(
        "INSERT INTO gencode_component_tracker (textbook_example_id, skill_id, component_id, gencode_status) VALUES (3828, 'vh_math', 'src_3828', 'draft')"
    )
    conn.execute(
        "INSERT INTO gencode_component_tracker (textbook_example_id, skill_id, component_id, gencode_status) VALUES (3829, 'vh_math', 'src_3829', 'failed')"
    )
    
    # 3826 production contains latest
    # Mock file system: create reports (dryrun) and agent_skills_v3 (production) dirs
    skill_id = "vh_math"
    (tmp_path / "reports" / "gencode_v3_dryrun" / skill_id / "components").mkdir(parents=True)
    (tmp_path / "agent_skills_v3" / skill_id / "components").mkdir(parents=True)

    # 3826 exists on both dryrun and production with same content
    p_3826_dry = tmp_path / "reports" / "gencode_v3_dryrun" / skill_id / "components" / "src_3826"
    p_3826_prod = tmp_path / "agent_skills_v3" / skill_id / "components" / "src_3826"
    p_3826_dry.mkdir()
    p_3826_prod.mkdir()
    (p_3826_dry / "generate.py").write_text("def gen(): pass")
    (p_3826_prod / "generate.py").write_text("def gen(): pass")

    # 3827 exists on dryrun only
    p_3827_dry = tmp_path / "reports" / "gencode_v3_dryrun" / skill_id / "components" / "src_3827"
    p_3827_dry.mkdir()
    (p_3827_dry / "generate.py").write_text("def gen(): pass")

    from core.gencode.services.gencode_status_query_service import (
        build_admin_examples_gencode_status_map,
        build_admin_skill_gencode_status_view,
    )

    status_map = build_admin_examples_gencode_status_map(
        conn,
        [(3826, skill_id), (3827, skill_id), (3828, skill_id), (3829, skill_id)],
        project_root=tmp_path,
    )

    # Individual status checks
    assert status_map[3826]["teacher_status"]["status_key"] == "published"
    assert status_map[3827]["teacher_status"]["status_key"] == "generated_not_packaged"
    assert status_map[3828]["teacher_status"]["status_key"] == "not_generated"
    assert status_map[3829]["teacher_status"]["status_key"] == "failed"

    # Skill-level status checks (mock outline coverage payload structure)
    outline_coverage = {
        "skill_id": skill_id,
        "total_examples": 4,
        "verified_count": 2,
        "failed_count": 1,
        "unsupported_count": 0,
        "publish_ready": False,
        "examples": [
            {"textbook_example_id": 3826, "component_id": "src_3826", "status": "verified"},
            {"textbook_example_id": 3827, "component_id": "src_3827", "status": "verified"},
            {"textbook_example_id": 3828, "component_id": "src_3828", "status": "draft"},
            {"textbook_example_id": 3829, "component_id": "src_3829", "status": "failed"},
        ]
    }
    
    # We must patch get_v3_skill_component_coverage to return this mock coverage
    import core.gencode.services.v3_skill_coverage_service as coverage_module
    old_func = coverage_module.get_v3_skill_component_coverage
    coverage_module.get_v3_skill_component_coverage = lambda *args, **kwargs: outline_coverage
    
    try:
        # Mock production init so it says we have v3_package_exists
        (tmp_path / "agent_skills_v3" / skill_id / "__init__.py").write_text("GENERATOR_SPECS = [1,2,3,4]")
        (tmp_path / "skills").mkdir(parents=True, exist_ok=True)
        (tmp_path / "skills" / f"{skill_id}.py").write_text("")
        
        skill_status = build_admin_skill_gencode_status_view(
            conn,
            skill_id=skill_id,
            project_root=tmp_path,
        )
        assert skill_status["teacher_status"]["status_key"] == "partially_published"
        assert "部分上線" in skill_status["teacher_status"]["label"]
        assert skill_status["published_count"] == 1
        assert skill_status["generated_not_packaged_count"] == 1
    finally:
        coverage_module.get_v3_skill_component_coverage = old_func
        conn.close()


def test_src_3829_production_consistency():
    import hashlib
    # 1. Verify dryrun reports and production agent_skills_v3 generate.py match
    root = Path(__file__).resolve().parents[2]
    dryrun_generate = root / "reports" / "gencode_v3_dryrun" / "vh_數學B4_HistogramsAndFrequencyPolygons" / "components" / "src_3829" / "generate.py"
    prod_generate = root / "agent_skills_v3" / "vh_數學B4_HistogramsAndFrequencyPolygons" / "components" / "src_3829" / "generate.py"
    
    assert dryrun_generate.is_file(), "Dryrun src_3829 generate.py must exist"
    assert prod_generate.is_file(), "Production src_3829 generate.py must exist"
    
    dryrun_hash = hashlib.sha256(dryrun_generate.read_bytes()).hexdigest()
    prod_hash = hashlib.sha256(prod_generate.read_bytes()).hexdigest()
    assert dryrun_hash == prod_hash, "Dryrun and Production generate.py files must be identical"

    # 2. Check metadata vs wrapper specs consistency
    import importlib.util
    meta_path = root / "agent_skills_v3" / "vh_數學B4_HistogramsAndFrequencyPolygons" / "components" / "src_3829" / "metadata.py"
    assert meta_path.is_file(), "Metadata file must exist"
    spec = importlib.util.spec_from_file_location("test_meta_3829", meta_path)
    meta_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(meta_mod)
    
    from agent_skills_v3.vh_數學B4_HistogramsAndFrequencyPolygons import GENERATOR_SPECS
    matching_spec = None
    for row in GENERATOR_SPECS:
        if row.get("component_id") == "src_3829":
            matching_spec = row
            break
            
    assert matching_spec is not None, "Wrapper GENERATOR_SPECS must contain src_3829"
    assert matching_spec["problem_type_id"] == meta_mod.PROBLEM_TYPE_ID
    assert matching_spec["line_type"] == meta_mod.LINE_TYPE
    assert matching_spec["answer_type"] == meta_mod.ANSWER_TYPE
    assert matching_spec["problem_type_id"] == "histogram_distribution_update"

    # 3. Reload module check
    import skills.vh_數學B4_HistogramsAndFrequencyPolygons as facade
    p = facade.generate(seed=100, component_id="src_3829")
    assert p["problem_type_id"] == "histogram_distribution_update"
    assert p["answer_contract"]["checker"] == "free_response_drawing_checker"


