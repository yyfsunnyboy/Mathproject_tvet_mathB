# -*- coding: utf-8 -*-
"""Regression tests for /skills Gencode V3 status display."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.gencode_status_query_service import (
    TEACHER_V3_STATUS,
    build_admin_skills_gencode_status_map,
)
from models import SkillCurriculum, SkillInfo, TextbookExample, User, db


SKILL_A = "vh_math_b4_frequency_distribution_table"
SKILL_B = "vh_math_b4_histograms_and_frequency_polygons"


def _seed_files(project_root: Path, skill_id: str, example_ids: list[int], *, dryrun_only: list[int] | None = None) -> None:
    dryrun_only = set(dryrun_only or [])
    (project_root / "skills").mkdir(parents=True, exist_ok=True)
    (project_root / "skills" / f"{skill_id}.py").write_text("# wrapper\n", encoding="utf-8")
    skill_dir = project_root / "agent_skills_v3" / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "__init__.py").write_text("GENERATOR_SPECS = []\n", encoding="utf-8")
    for example_id in example_ids:
        component_id = f"src_{example_id}"
        prod_dir = skill_dir / "components" / component_id
        prod_dir.mkdir(parents=True, exist_ok=True)
        (prod_dir / "generate.py").write_text("def generate():\n    return {}\n", encoding="utf-8")
        if example_id in dryrun_only:
            dry_dir = project_root / "reports" / "gencode_v3_dryrun" / skill_id / "components" / component_id
            dry_dir.mkdir(parents=True, exist_ok=True)
            (dry_dir / "generate.py").write_text("def generate():\n    return {'dryrun': True}\n", encoding="utf-8")


def _seed_tracker(conn, skill_id: str, example_ids: list[int], statuses: list[str]) -> None:
    for example_id, status in zip(example_ids, statuses):
        conn.execute(
            """
            INSERT INTO gencode_component_tracker (
                textbook_example_id, skill_id, component_id, gencode_status,
                induced_spec_payload, gencode_error_log, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                example_id,
                skill_id,
                f"src_{example_id}",
                status,
                json.dumps({"integrity_gate_passed": True}, ensure_ascii=False),
                None,
                "2026-06-25 01:00:00",
            ),
        )


@pytest.fixture()
def b4_status_env():
    import config as _cfg
    from app import create_app

    project_root = Path("reports") / f"pytest_v3_status_{uuid.uuid4().hex[:8]}"
    project_root.mkdir(parents=True, exist_ok=True)
    db_path = project_root / "test.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")

    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            teacher = User(username=f"teacher_{uuid.uuid4().hex[:6]}", password_hash="x", role="teacher")
            db.session.add(teacher)
            for skill_id in (SKILL_A, SKILL_B):
                db.session.add(
                    SkillInfo(
                        skill_id=skill_id,
                        skill_en_name=skill_id,
                        skill_ch_name=skill_id,
                        category="test",
                        description="",
                        input_type="text",
                        gemini_prompt="prompt",
                        consecutive_correct_required=3,
                        is_active=True,
                        order_index=1,
                    )
                )
                db.session.add(
                    SkillCurriculum(
                        skill_id=skill_id,
                        curriculum="vocational",
                        grade=11,
                        volume="數學B4",
                        chapter="3 統計",
                        section="3-2 統計資料圖示",
                        display_order=1,
                    )
                )
            db.session.commit()

            for example_id, skill_id in (
                (3822, SKILL_A),
                (3823, SKILL_A),
                (3824, SKILL_A),
                (3825, SKILL_A),
                (3826, SKILL_B),
                (3827, SKILL_B),
                (3828, SKILL_B),
                (3829, SKILL_B),
            ):
                db.session.add(
                    TextbookExample(
                        id=example_id,
                        skill_id=skill_id,
                        source_curriculum="vocational",
                        source_volume="數學B4",
                        source_chapter="3 統計",
                        source_section="3-2 統計資料圖示",
                        source_description=f"example {example_id}",
                        problem_text=f"problem {example_id}",
                    )
                )
            db.session.commit()

            conn = db.engine.raw_connection()
            try:
                apply_tracker_ddl(conn)
                _seed_tracker(conn, SKILL_A, [3822, 3823, 3824, 3825], ["verified"] * 4)
                _seed_tracker(conn, SKILL_B, [3826, 3827, 3828, 3829], ["verified"] * 4)
                conn.commit()
            finally:
                conn.close()

            _seed_files(project_root, SKILL_A, [3822, 3823, 3824, 3825])
            _seed_files(project_root, SKILL_B, [3826, 3827, 3828, 3829], dryrun_only=[3827])

            yield app, teacher.id, project_root
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        import shutil

        shutil.rmtree(project_root, ignore_errors=True)


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def test_verified_tracker_must_not_render_zero_over_zero(b4_status_env):
    app, _, project_root = b4_status_env
    with app.app_context():
        conn = db.engine.raw_connection()
        try:
            status_map = build_admin_skills_gencode_status_map(
                conn,
                [SKILL_A, SKILL_B],
                project_root=project_root,
            )
        finally:
            conn.close()

    for skill_id in (SKILL_A, SKILL_B):
        view = status_map[skill_id]
        assert view["total_examples"] == 4
        assert view["verified_count"] == 4
        assert view["available_count"] == 4
        assert view["teacher_status"]["status_key"] != "not_generated"


def test_production_wrapper_must_not_show_not_generated(b4_status_env):
    app, _, project_root = b4_status_env
    with app.app_context():
        conn = db.engine.raw_connection()
        try:
            view = build_admin_skills_gencode_status_map(conn, [SKILL_A], project_root=project_root)[SKILL_A]
        finally:
            conn.close()

    assert view["production_wrapper_exists"] is True
    assert view["v3_package_exists"] is True
    assert view["teacher_status"]["label"] != TEACHER_V3_STATUS["not_generated"]["label"]


def test_published_evidence_kept_when_dryrun_differs(b4_status_env):
    app, _, project_root = b4_status_env
    with app.app_context():
        conn = db.engine.raw_connection()
        try:
            view = build_admin_skills_gencode_status_map(conn, [SKILL_B], project_root=project_root)[SKILL_B]
        finally:
            conn.close()

    assert view["published_count"] == 4
    assert view["teacher_status"]["status_key"] == "published"


def test_skill_without_v3_data_shows_not_generated(b4_status_env):
    app, _, project_root = b4_status_env
    with app.app_context():
        conn = db.engine.raw_connection()
        try:
            view = build_admin_skills_gencode_status_map(conn, ["missing_skill"], project_root=project_root)[
                "missing_skill"
            ]
        finally:
            conn.close()

    assert view["total_examples"] == 0
    assert view["verified_count"] == 0
    assert view["teacher_status"]["status_key"] == "not_generated"


def test_filtered_skills_route_preserves_v3_status_in_html(b4_status_env, monkeypatch):
    app, teacher_id, project_root = b4_status_env
    from core.routes import admin as admin_routes

    monkeypatch.setattr(admin_routes, "_resolve_admin_project_root", lambda: project_root)

    client = app.test_client()
    _login(client, teacher_id)

    response = client.get("/skills?f_curriculum=vocational&f_volume=%E6%95%B8%E5%AD%B8B4")
    assert response.status_code == 200
    html = response.data.decode("utf-8")

    for skill_id in (SKILL_A, SKILL_B):
        assert skill_id in html
        start = html.index(skill_id)
        snippet = html[start : start + 4000]
        assert "teacher-v3-published" in snippet or "generated-not-packaged" in snippet
        assert "可用題目" in snippet and "/4" in snippet
        assert "尚未生成" not in snippet or "全部上線" in snippet
