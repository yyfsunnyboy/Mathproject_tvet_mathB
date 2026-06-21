# -*- coding: utf-8 -*-
"""Tests for admin skill-level V3 production repackage action."""

from __future__ import annotations

import json
import shutil
import time
import uuid
import hashlib
from collections.abc import Iterator
from pathlib import Path
from unittest import mock

import pytest
from flask import render_template

from app import app
from core.gencode.v3_production_publish_service import ALLOWED_PRODUCTION_SKILL_ID

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SKILL_ID = ALLOWED_PRODUCTION_SKILL_ID
COMPONENT_ID = "src_1"

STUB_METADATA_PY = '''from __future__ import annotations
COMPONENT_ID = "src_1"
'''

STUB_GENERATE_PY = '''from __future__ import annotations
from typing import Any

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "question": "mock question text",
        "answer": "mock answer",
        "correct_answer": "mock answer",
        "component_id": "src_1",
        "metadata": {"component_id": "src_1"},
    }

def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> bool:
    return str(user_answer) == str(correct_answer)
'''

STUB_GET_HINT_PY = '''from __future__ import annotations
from typing import Any

def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return f"hint step {step}"
'''


@pytest.fixture
def isolated_publish_roots() -> Iterator[tuple[Path, Path]]:
    base = SANDBOX_ROOT / f"pytest_admin_repackage_{uuid.uuid4().hex}"
    project_root = base / "project"
    staging_root = base / "staging"
    (project_root / "skills").mkdir(parents=True, exist_ok=True)
    (project_root / "agent_skills_v3").mkdir(parents=True, exist_ok=True)
    staging_root.mkdir(parents=True, exist_ok=True)
    try:
        yield project_root, staging_root
    finally:
        shutil.rmtree(base, ignore_errors=True)

# Helper to clean whitespaces for HTML assertions
def clean_html(html: str) -> str:
    return "".join(html.split())

# ----------------- UI Button Display Tests -----------------

def test_ui_none_generated_shows_fixed_v3_actions():
    """1. 尚未生成技能也固定顯示三個 V3 操作。"""
    with app.test_request_context():
        gencode = {
            "total_examples": 5,
            "verified_count": 0,
            "failed_count": 0,
            "unsupported_count": 0,
            "component_count": 0,
            "production_wrapper_exists": False,
            "v3_package_exists": False,
            "publish_ready": False,
            "publish_eligible": False,
            "teacher_status": {
                "icon": "⚪",
                "label": "尚未生成",
                "badge_class": "teacher-v3-not-generated"
            }
        }
        skill = {
            "skill_id": SKILL_ID,
            "skill_ch_name": "Test Skill",
            "is_active": True,
            "curriculum": "junior_high",
            "grade": 7,
            "volume": "1",
            "chapter": "1",
            "section": "1",
        }
        
        rendered = render_template(
            "admin_skills.html",
            skills=[skill],
            v3_gencode_status_map={SKILL_ID: gencode},
            gencode_status_map={},
            filters={"curricula": [], "grades": [], "volumes": [], "chapters": [], "sections": []},
            selected_filters={"f_curriculum": "all", "f_grade": "all", "f_volume": "all", "f_chapter": "all", "f_section": "all"},
            grade_map={},
            curriculum_map={},
            username="admin",
        )
        
        compact = clean_html(rendered)
        assert "重新生成本技能題目</button>" in compact
        assert "更新到學生端</button>" not in compact
        assert "查看組件</a>" not in compact

def test_ui_has_package_shows_fixed_v3_actions():
    """2. 已有 V3 package 仍固定顯示三個 V3 操作。"""
    with app.test_request_context():
        gencode = {
            "total_examples": 5,
            "verified_count": 3,
            "failed_count": 0,
            "unsupported_count": 0,
            "component_count": 3,
            "production_wrapper_exists": True,
            "v3_package_exists": True,
            "publish_ready": False,
            "publish_eligible": False,
            "teacher_status": {
                "icon": "🟡",
                "label": "尚未上線",
                "badge_class": "teacher-v3-generated-not-packaged"
            }
        }
        skill = {
            "skill_id": SKILL_ID,
            "skill_ch_name": "Test Skill",
            "is_active": True,
            "curriculum": "junior_high",
            "grade": 7,
            "volume": "1",
            "chapter": "1",
            "section": "1",
        }
        
        rendered = render_template(
            "admin_skills.html",
            skills=[skill],
            v3_gencode_status_map={SKILL_ID: gencode},
            gencode_status_map={},
            filters={"curricula": [], "grades": [], "volumes": [], "chapters": [], "sections": []},
            selected_filters={"f_curriculum": "all", "f_grade": "all", "f_volume": "all", "f_chapter": "all", "f_section": "all"},
            grade_map={},
            curriculum_map={},
            username="admin",
        )
        
        compact = clean_html(rendered)
        assert "重新生成本技能題目</button>" in compact
        assert "更新到學生端</button>" not in compact
        assert "查看組件</a>" in compact

def test_ui_verified_full_shows_repackage():
    """3. verified 全滿顯示 V3 重新包裝。"""
    with app.test_request_context():
        gencode = {
            "total_examples": 5,
            "verified_count": 5,
            "failed_count": 0,
            "unsupported_count": 0,
            "component_count": 5,
            "production_wrapper_exists": True,
            "v3_package_exists": True,
            "publish_ready": True,
            "publish_eligible": False,
        }
        skill = {
            "skill_id": SKILL_ID,
            "skill_ch_name": "Test Skill",
            "is_active": True,
            "curriculum": "junior_high",
            "grade": 7,
            "volume": "1",
            "chapter": "1",
            "section": "1",
        }
        
        rendered = render_template(
            "admin_skills.html",
            skills=[skill],
            v3_gencode_status_map={SKILL_ID: gencode},
            gencode_status_map={},
            filters={"curricula": [], "grades": [], "volumes": [], "chapters": [], "sections": []},
            selected_filters={"f_curriculum": "all", "f_grade": "all", "f_volume": "all", "f_chapter": "all", "f_section": "all"},
            grade_map={},
            curriculum_map={},
            username="admin",
        )
        
        compact = clean_html(rendered)
        assert "更新到學生端</button>" in compact

def test_ui_legacy_vs_v3_wrapper_button_displays():
    """9. V3 skill 不以舊版重建作為主要操作。
    10. legacy skill 仍保留 V2 舊版重建。"""
    with app.test_request_context():
        gencode_v3 = {
            "total_examples": 5,
            "verified_count": 5,
            "failed_count": 0,
            "unsupported_count": 0,
            "component_count": 5,
            "production_wrapper_exists": True,
            "v3_package_exists": True,
            "publish_ready": True,
            "publish_eligible": True,
        }
        skill_v3 = {
            "skill_id": "v3_skill",
            "skill_ch_name": "V3 Skill",
            "is_active": True,
            "curriculum": "junior_high",
            "grade": 7,
            "volume": "1",
            "chapter": "1",
            "section": "1",
        }

        gencode_legacy = {
            "total_examples": 0,
            "verified_count": 0,
            "failed_count": 0,
            "unsupported_count": 0,
            "component_count": 0,
            "production_wrapper_exists": False,
            "v3_package_exists": False,
            "publish_ready": False,
            "publish_eligible": False,
        }
        skill_legacy = {
            "skill_id": "legacy_skill",
            "skill_ch_name": "Legacy Skill",
            "is_active": True,
            "curriculum": "junior_high",
            "grade": 7,
            "volume": "1",
            "chapter": "1",
            "section": "1",
        }

        rendered = render_template(
            "admin_skills.html",
            skills=[skill_v3, skill_legacy],
            v3_gencode_status_map={"v3_skill": gencode_v3, "legacy_skill": gencode_legacy},
            gencode_status_map={},
            filters={"curricula": [], "grades": [], "volumes": [], "chapters": [], "sections": []},
            selected_filters={"f_curriculum": "all", "f_grade": "all", "f_volume": "all", "f_chapter": "all", "f_section": "all"},
            grade_map={},
            curriculum_map={},
            username="admin",
        )

        compact = clean_html(rendered)
        assert compact.count("V2舊版重建") == 1


# ----------------- Endpoint API Behavior Tests -----------------

def test_repackage_endpoint_allows_partial_coverage_repackage(isolated_publish_roots):
    """6. coverage 不完整時仍允許重新包裝已 verified components。"""
    project_root, staging_root = isolated_publish_roots
    app.config["TESTING"] = True
    app.config["GENCODE_V3_PUBLISH_PROJECT_ROOT"] = str(project_root)
    app.config["GENCODE_V3_PUBLISH_STAGING_ROOT"] = str(staging_root)
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True

        mock_coverage = {
            "total_examples": 5,
            "verified_count": 4,
            "failed_count": 0,
            "unsupported_count": 0,
            "missing_tracker_count": 1,
            "publish_ready": False,
        }

        with mock.patch("core.gencode.services.v3_skill_coverage_service.get_v3_skill_component_coverage", return_value=mock_coverage), \
             mock.patch("core.gencode.services.admin_gencode_action_service._prepare_publish_staging_components") as mock_prep, \
             mock.patch("core.gencode.services.admin_gencode_action_service.run_admin_v3_publish_for_skill") as mock_pub:
            mock_pub.return_value = {
                "status": "production_published",
                "component_count": 4,
                "compile": {"generator_specs": [{"component_id": COMPONENT_ID}] * 4},
                "promote": {"thin_facade_path": str(project_root / "skills" / f"{SKILL_ID}.py")},
            }

            response = client.post(f"/admin/skills/{SKILL_ID}/v3_repackage")

            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "success"
            assert data["publish_eligible"] is True
            assert data["publish_reason"] == "partial_coverage_repackaged"
            assert data["verified_component_count"] == 4
            assert data["total_component_count"] == 5
            mock_prep.assert_called_once()
            mock_pub.assert_called_once()
            assert mock_pub.call_args.kwargs["strict_coverage"] is False

def test_repackage_endpoint_does_not_call_generator(isolated_publish_roots):
    """4. 重新包裝 endpoint 不呼叫 component generator。"""
    project_root, staging_root = isolated_publish_roots
    app.config["TESTING"] = True
    app.config["GENCODE_V3_PUBLISH_PROJECT_ROOT"] = str(project_root)
    app.config["GENCODE_V3_PUBLISH_STAGING_ROOT"] = str(staging_root)

    # Set up stubs in staging/dryrun
    dryrun_dir = project_root / "reports" / "gencode_v3_dryrun" / SKILL_ID / "components" / COMPONENT_ID
    dryrun_dir.mkdir(parents=True, exist_ok=True)
    (dryrun_dir / "generate.py").write_text(STUB_GENERATE_PY, encoding="utf-8")
    (dryrun_dir / "metadata.py").write_text(STUB_METADATA_PY, encoding="utf-8")
    (dryrun_dir / "get_hint.py").write_text(STUB_GET_HINT_PY, encoding="utf-8")

    mock_coverage = {
        "total_examples": 1,
        "verified_count": 1,
        "failed_count": 0,
        "unsupported_count": 0,
        "missing_tracker_count": 0,
        "publish_ready": True,
    }

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True

        with mock.patch("core.gencode.services.v3_skill_coverage_service.get_v3_skill_component_coverage", return_value=mock_coverage), \
             mock.patch("core.gencode.services.v3_publish_eligibility.evaluate_v3_publish_eligibility") as mock_eval, \
             mock.patch("core.gencode.services.admin_gencode_action_service._prepare_publish_staging_components") as mock_prep, \
             mock.patch("core.gencode.services.admin_gencode_action_service.run_admin_v3_publish_for_skill") as mock_pub:
             
             mock_eval.return_value = {
                 "allowed": True,
                 "reason": "eligible",
                 "integrity_gate_component_count": 1,
             }
             mock_pub.return_value = {
                 "status": "production_published",
                 "component_count": 1,
                 "compile": {"generator_specs": [{"component_id": COMPONENT_ID}]},
                 "promote": {"thin_facade_path": str(project_root / "skills" / f"{SKILL_ID}.py")}
             }

             with mock.patch("core.gencode.services.admin_gencode_action_service.run_admin_v3_dryrun_for_example") as mock_gen:
                 response = client.post(f"/admin/skills/{SKILL_ID}/v3_repackage")
                 assert response.status_code == 200
                 mock_gen.assert_not_called()
                 mock_prep.assert_called_once()
                 mock_pub.assert_called_once()

def test_repackage_endpoint_preserves_generate_mtime_and_hash(isolated_publish_roots):
    """5. 重新包裝不修改 generate.py mtime/hash。"""
    project_root, staging_root = isolated_publish_roots
    app.config["TESTING"] = True
    app.config["GENCODE_V3_PUBLISH_PROJECT_ROOT"] = str(project_root)
    app.config["GENCODE_V3_PUBLISH_STAGING_ROOT"] = str(staging_root)

    dryrun_base = project_root / "reports" / "gencode_v3_dryrun"
    dryrun_dir = dryrun_base / SKILL_ID / "components" / COMPONENT_ID
    dryrun_dir.mkdir(parents=True, exist_ok=True)
    gen_file = dryrun_dir / "generate.py"
    gen_file.write_text(STUB_GENERATE_PY, encoding="utf-8")
    (dryrun_dir / "metadata.py").write_text(STUB_METADATA_PY, encoding="utf-8")
    (dryrun_dir / "get_hint.py").write_text(STUB_GET_HINT_PY, encoding="utf-8")

    init_mtime = gen_file.stat().st_mtime
    init_hash = hashlib.sha256(gen_file.read_bytes()).hexdigest()

    time.sleep(0.1)

    mock_coverage = {
        "total_examples": 1,
        "verified_count": 1,
        "failed_count": 0,
        "unsupported_count": 0,
        "missing_tracker_count": 0,
        "publish_ready": True,
    }

    mock_components = [{
        "textbook_example_id": 1,
        "component_id": COMPONENT_ID,
        "induced_spec_payload": {
            "source_kind": "ex_1",
            "presentation_mode": "short_answer",
            "line_type": "point_slope",
            "problem_type_id": "line_equation_general_form",
            "integrity_gate_passed": True,
            "integrity_gate_version": "v1",
        }
    }]

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True

        with mock.patch("core.gencode.services.v3_skill_coverage_service.get_v3_skill_component_coverage", return_value=mock_coverage), \
             mock.patch("core.gencode.services.v3_publish_eligibility.evaluate_v3_publish_eligibility") as mock_eval, \
             mock.patch("core.gencode.services.admin_gencode_action_service.get_v3_skill_component_coverage", return_value=mock_coverage), \
             mock.patch("core.gencode.services.admin_gencode_action_service.evaluate_v3_publish_eligibility") as mock_eval_service, \
             mock.patch("core.gencode.services.admin_gencode_action_service._count_verified_components_for_skill", return_value=1), \
             mock.patch("core.gencode.v3_production_publish_service._fetch_verified_components", return_value=mock_components), \
             mock.patch("core.gencode.skill_wrapper_compiler._fetch_verified_components", return_value=mock_components), \
             mock.patch("core.gencode.services.v3_question_integrity_validator.validate_skill_samples", return_value={"passed": True}), \
             mock.patch("core.gencode.services.v3_variation_audit_service.audit_skill_variation", return_value={"status": "passed", "dynamic_count": 1, "static_count": 0}):
             
             mock_eval.return_value = {
                 "allowed": True,
                 "reason": "eligible",
                 "integrity_gate_component_count": 1,
             }
             mock_eval_service.return_value = {
                 "allowed": True,
                 "reason": "eligible",
                 "integrity_gate_component_count": 1,
             }

             response = client.post(f"/admin/skills/{SKILL_ID}/v3_repackage")
             assert response.status_code == 200
             data = response.get_json()
             assert data["status"] == "success", data

    assert gen_file.stat().st_mtime == init_mtime
    assert hashlib.sha256(gen_file.read_bytes()).hexdigest() == init_hash

def test_repackage_endpoint_success_promotes_wrapper_and_counts_specs(isolated_publish_roots):
    """7. eligibility success 重新編譯 wrapper。
    8. wrapper generator_specs_count 等於 verified component count。"""
    project_root, staging_root = isolated_publish_roots
    app.config["TESTING"] = True
    app.config["GENCODE_V3_PUBLISH_PROJECT_ROOT"] = str(project_root)
    app.config["GENCODE_V3_PUBLISH_STAGING_ROOT"] = str(staging_root)

    # Set up stubs in dryrun
    dryrun_base = project_root / "reports" / "gencode_v3_dryrun"
    dryrun_dir = dryrun_base / SKILL_ID / "components" / COMPONENT_ID
    dryrun_dir.mkdir(parents=True, exist_ok=True)
    (dryrun_dir / "generate.py").write_text(STUB_GENERATE_PY, encoding="utf-8")
    (dryrun_dir / "metadata.py").write_text(STUB_METADATA_PY, encoding="utf-8")
    (dryrun_dir / "get_hint.py").write_text(STUB_GET_HINT_PY, encoding="utf-8")

    mock_coverage = {
        "total_examples": 1,
        "verified_count": 1,
        "failed_count": 0,
        "unsupported_count": 0,
        "missing_tracker_count": 0,
        "publish_ready": True,
    }

    mock_components = [{
        "textbook_example_id": 1,
        "component_id": COMPONENT_ID,
        "induced_spec_payload": {
            "source_kind": "ex_1",
            "presentation_mode": "short_answer",
            "line_type": "point_slope",
            "problem_type_id": "line_equation_general_form",
            "integrity_gate_passed": True,
            "integrity_gate_version": "v1",
        }
    }]

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True

        with mock.patch("core.gencode.services.v3_skill_coverage_service.get_v3_skill_component_coverage", return_value=mock_coverage), \
             mock.patch("core.gencode.services.v3_publish_eligibility.evaluate_v3_publish_eligibility") as mock_eval, \
             mock.patch("core.gencode.services.admin_gencode_action_service.get_v3_skill_component_coverage", return_value=mock_coverage), \
             mock.patch("core.gencode.services.admin_gencode_action_service.evaluate_v3_publish_eligibility") as mock_eval_service, \
             mock.patch("core.gencode.services.admin_gencode_action_service._count_verified_components_for_skill", return_value=1), \
             mock.patch("core.gencode.v3_production_publish_service._fetch_verified_components", return_value=mock_components), \
             mock.patch("core.gencode.skill_wrapper_compiler._fetch_verified_components", return_value=mock_components), \
             mock.patch("core.gencode.services.v3_question_integrity_validator.validate_skill_samples", return_value={"passed": True}), \
             mock.patch("core.gencode.services.v3_variation_audit_service.audit_skill_variation", return_value={"status": "passed", "dynamic_count": 1, "static_count": 0}):
             
             mock_eval.return_value = {
                 "allowed": True,
                 "reason": "eligible",
                 "integrity_gate_component_count": 1,
             }
             mock_eval_service.return_value = {
                 "allowed": True,
                 "reason": "eligible",
                 "integrity_gate_component_count": 1,
             }

             response = client.post(f"/admin/skills/{SKILL_ID}/v3_repackage")
             assert response.status_code == 200
             data = response.get_json()
             
             assert data["status"] == "success", data
             assert data["publish_eligible"] is True, data
             assert data["verified_component_count"] == 1
             assert data["generator_specs_count"] == 1
             assert data["wrapper_path"] is not None
             assert str(data["wrapper_path"]).replace('\\', '/').endswith(f"skills/{SKILL_ID}.py")


def test_repackage_auto_promotes_stale_tracker(isolated_publish_roots):
    """Test that tracker status lagging behind is auto-promoted during repackage."""
    project_root, staging_root = isolated_publish_roots
    
    # We will mock the database and auto-promotion calls
    from core.gencode.v3_production_publish_service import _auto_promote_valid_components
    import sqlite3
    
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE gencode_component_tracker (
            textbook_example_id INTEGER PRIMARY KEY,
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
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT
        )
        """
    )
    conn.execute("INSERT INTO textbook_examples (id, skill_id) VALUES (4565, ?)", (SKILL_ID,))
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (textbook_example_id, skill_id, component_id, gencode_status)
        VALUES (4565, ?, 'src_4565', 'draft_written')
        """,
        (SKILL_ID,)
    )
    conn.commit()

    # Set up files in staging root
    stag_dir = staging_root / SKILL_ID / "components" / "src_4565"
    stag_dir.mkdir(parents=True, exist_ok=True)
    
    metadata_content = '''from __future__ import annotations
COMPONENT_ID = "src_4565"
SKILL_ID = "vh_數學B1_GeneralFormOfLinearEquation"
TEXTBOOK_EXAMPLE_ID = 4565
DIFFICULTY_LEVEL = "easy"
PRESENTATION_MODE = "short_answer"
ANSWER_TYPE = "numeric_or_undefined"
PROBLEM_TYPE_ID = "slope_from_general_or_intercept_form"
'''
    (stag_dir / "metadata.py").write_text(metadata_content, encoding="utf-8")
    (stag_dir / "generate.py").write_text(STUB_GENERATE_PY.replace("src_1", "src_4565"), encoding="utf-8")
    (stag_dir / "get_hint.py").write_text(STUB_GET_HINT_PY, encoding="utf-8")

    # Run auto promote
    _auto_promote_valid_components(conn, SKILL_ID, project_root, staging_root)

    # Check that status was promoted to verified
    row = conn.execute("SELECT gencode_status, induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id = 4565").fetchone()
    assert row["gencode_status"] == "verified"
    payload = json.loads(row["induced_spec_payload"])
    assert payload["integrity_gate_passed"] is True
    assert payload["problem_type_id"] == "slope_from_general_or_intercept_form"
    conn.close()


def test_repackage_no_deduplicate_by_problem_type_id():
    """Test that multiple textbook examples with the same problem_type_id are not deduplicated."""
    from core.gencode.skill_wrapper_compiler import _build_generator_specs
    
    mock_components = [
        {
            "textbook_example_id": 4566,
            "component_id": "src_4566",
            "induced_spec_payload": {
                "presentation_mode": "short_answer",
                "response_mode": "short_answer",
                "interaction_type": "standard",
                "answer_value_type": "expression",
                "problem_type_id": "line_through_point_parallel_to_line",
            }
        },
        {
            "textbook_example_id": 4573,
            "component_id": "src_4573",
            "induced_spec_payload": {
                "presentation_mode": "short_answer",
                "response_mode": "short_answer",
                "interaction_type": "standard",
                "answer_value_type": "expression",
                "problem_type_id": "line_through_point_parallel_to_line",
            }
        }
    ]
    
    keys, specs = _build_generator_specs(mock_components)
    assert len(specs) == 2
    assert specs[0]["component_id"] == "src_4566"
    assert specs[1]["component_id"] == "src_4573"
    assert specs[0]["problem_type_id"] == "line_through_point_parallel_to_line"
    assert specs[1]["problem_type_id"] == "line_through_point_parallel_to_line"


def test_instant_verified_and_failed_rebuild_flow(isolated_publish_roots):
    """Regression: 1. Single example regeneration instantly verified without repackage. 2. Failed generation records failed status."""
    project_root, staging_root = isolated_publish_roots
    from core.gencode.pipeline_orchestrator import run_gencode_phase2_v3_shadow_bridge
    from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
    import sqlite3

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    apply_tracker_ddl(conn)
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT,
            problem_text TEXT,
            correct_answer TEXT,
            detailed_solution TEXT
        )
        """
    )
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id, problem_text, correct_answer) VALUES (4565, ?, 'L: 3x - y + 2 = 0', '3')",
        (SKILL_ID,)
    )
    conn.commit()

    # Run regeneration (we mock or structure it so it passes validation)
    with mock.patch("core.gencode.pipeline_orchestrator.build_v3_component_draft_from_skill") as mock_build:
        mock_build.return_value = {
            "status": "draft_built",
            "skill_id": SKILL_ID,
            "textbook_example_id": 4565,
            "source_kind": "ex_4565",
            "line_type": "slope_from_general_or_intercept_form",
            "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
            "entrypoint": "build_line_equation_matrix",
            "files": {
                "metadata.py": STUB_METADATA_PY.replace("src_1", "src_4565"),
                "generate.py": STUB_GENERATE_PY.replace("src_1", "src_4565"),
                "get_hint.py": STUB_GET_HINT_PY,
            }
        }
        res = run_gencode_phase2_v3_shadow_bridge(
            conn=conn,
            skill_id=SKILL_ID,
            textbook_example_id=4565,
            source_kind="ex_4565",
            dryrun_base_dir=str(project_root / "reports" / "gencode_v3_dryrun"),
        )
        assert res["tracker_status"] == "verified"

        # Check DB tracker is updated immediately without repackage
        row = conn.execute("SELECT gencode_status FROM gencode_component_tracker WHERE textbook_example_id = 4565").fetchone()
        assert row["gencode_status"] == "verified"

        # 2. Assert validator failure transitions to failed
        mock_build.return_value["files"]["generate.py"] = "def generate(seed):\n    return {}" # empty payload fails validator
        with pytest.raises(ValueError):
            run_gencode_phase2_v3_shadow_bridge(
                conn=conn,
                skill_id=SKILL_ID,
                textbook_example_id=4565,
                source_kind="ex_4565",
                dryrun_base_dir=str(project_root / "reports" / "gencode_v3_dryrun"),
            )
        row = conn.execute("SELECT gencode_status FROM gencode_component_tracker WHERE textbook_example_id = 4565").fetchone()
        assert row["gencode_status"] == "failed"

    conn.close()


