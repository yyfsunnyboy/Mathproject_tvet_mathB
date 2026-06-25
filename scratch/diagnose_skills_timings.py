# -*- coding: utf-8 -*-
"""Temporary diagnostic: /skills route phase timings."""
from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import event
from sqlalchemy.engine import Engine

query_count = 0
query_times: list[float] = []
sql_statements: list[tuple[float, str]] = []


@event.listens_for(Engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    global query_count
    query_count += 1
    elapsed = time.time() - conn.info["query_start_time"].pop(-1)
    query_times.append(elapsed)
    sql_statements.append((elapsed, str(statement)[:200]))


def _log(phase: str, elapsed: float, *, count: int | None = None, filters: dict | None = None) -> None:
    parts = [f"[skills_diag] {phase}: {elapsed:.4f}s"]
    if count is not None:
        parts.append(f"count={count}")
    if filters:
        parts.append(f"filters={filters}")
    print(" | ".join(parts))


def run_case(query_string: str) -> None:
    global query_count, query_times, sql_statements
    query_count = 0
    query_times = []
    sql_statements = []

    from app import create_app
    from flask import render_template
    from flask_login import login_user
    from models import SkillInfo, SkillCurriculum, User, db
    from core.utils import get_curriculum_aliases, handle_curriculum_filters

    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(role="teacher").first() or User.query.filter_by(role="admin").first()
        if not admin:
            print("No admin/teacher user found")
            return

        with app.test_request_context(query_string=query_string):
            from flask import request

            login_user(admin)
            t0 = time.time()
            selected, filters_data = handle_curriculum_filters(request)
            _log("parse_filters", time.time() - t0, filters=selected)

            query = db.session.query(SkillInfo, SkillCurriculum).join(
                SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id
            )
            if selected["f_curriculum"] != "all":
                aliases = get_curriculum_aliases(selected["f_curriculum"])
                query = query.filter(SkillCurriculum.curriculum.in_(aliases))
            if selected["f_grade"] != "all" and str(selected["f_grade"]).isdigit():
                query = query.filter(SkillCurriculum.grade == int(selected["f_grade"]))
            if selected["f_volume"] != "all":
                query = query.filter(SkillCurriculum.volume == selected["f_volume"])
            if selected["f_chapter"] != "all":
                query = query.filter(SkillCurriculum.chapter == selected["f_chapter"])
            if selected["f_section"] != "all":
                query = query.filter(SkillCurriculum.section == selected["f_section"])

            t1 = time.time()
            skills_data = (
                query.distinct()
                .order_by(SkillCurriculum.display_order.asc(), SkillInfo.skill_id.asc())
                .all()
            )
            _log("main_skill_query", time.time() - t1, count=len(skills_data), filters=selected)

            t2 = time.time()
            skills = []
            for skill_info, curriculum in skills_data:
                skills.append(
                    {
                        "skill_id": skill_info.skill_id,
                        "skill_en_name": skill_info.skill_en_name,
                        "skill_ch_name": skill_info.skill_ch_name,
                        "category": skill_info.category,
                        "description": skill_info.description,
                        "input_type": skill_info.input_type,
                        "gemini_prompt": skill_info.gemini_prompt,
                        "consecutive_correct_required": skill_info.consecutive_correct_required,
                        "is_active": skill_info.is_active,
                        "order_index": skill_info.order_index,
                        "display_order": curriculum.display_order,
                        "suggested_prompt_1": skill_info.suggested_prompt_1,
                        "suggested_prompt_2": skill_info.suggested_prompt_2,
                        "suggested_prompt_3": skill_info.suggested_prompt_3,
                        "curriculum": curriculum.curriculum,
                        "grade": curriculum.grade,
                        "volume": curriculum.volume,
                        "chapter": curriculum.chapter,
                        "section": curriculum.section,
                    }
                )
            _log("python_dict_assembly", time.time() - t2, count=len(skills), filters=selected)

            t3 = time.time()
            gencode_status_map = {}
            root_candidates = [Path(app.root_path), Path(app.root_path).parent, Path(app.root_path).parent.parent]
            project_root = next((p for p in root_candidates if (p / "skills").exists()), Path(app.root_path))
            skills_dir = project_root / "skills"
            drafts_dir = project_root / "reports" / "gencode_closed_loop" / "drafts"
            for s in skills:
                sid = str(s["skill_id"])
                formal_abs = skills_dir / f"{sid}.py"
                draft_abs = drafts_dir / f"{sid}.py"
                formal_exists = formal_abs.exists()
                draft_exists = draft_abs.exists()
                if formal_exists:
                    gencode_status_map[sid] = {"status": "generated", "formal_exists": True, "draft_exists": draft_exists}
                elif draft_exists:
                    gencode_status_map[sid] = {"status": "draft", "formal_exists": False, "draft_exists": True}
                else:
                    gencode_status_map[sid] = {"status": "missing", "formal_exists": False, "draft_exists": False}
            _log("v2_gencode_file_checks", time.time() - t3, count=len(gencode_status_map), filters=selected)

            t4 = time.time()
            from core.routes.admin import _load_skills_v3_gencode_status_map

            v3_gencode_status_map = _load_skills_v3_gencode_status_map([str(s["skill_id"]) for s in skills])
            _log("v3_gencode_status_map", time.time() - t4, count=len(v3_gencode_status_map), filters=selected)

            t5 = time.time()
            html = render_template(
                "admin_skills.html",
                skills_data=skills_data,
                skills=skills,
                gencode_status_map=gencode_status_map,
                v3_gencode_status_map=v3_gencode_status_map,
                filters=filters_data,
                selected_filters=selected,
                grade_map={str(g): str(g) for g in filters_data["grades"]},
                curriculum_map={
                    "junior_high": "國中",
                    "general": "普高",
                    "vocational": "技高",
                    "vocational_high": "技高",
                    "technical": "技高",
                    "junior": "國中",
                    "senior": "普高",
                    "general_high": "普高",
                    "senior_high": "普高",
                },
                username=admin.username,
            )
            _log("render_template", time.time() - t5, count=len(html), filters=selected)

            print(f"[skills_diag] SQL total: {query_count} queries, {sum(query_times):.4f}s")
            if sql_statements:
                slow = sorted(sql_statements, key=lambda x: x[0], reverse=True)[:5]
                print("[skills_diag] slowest SQL:")
                for sec, stmt in slow:
                    print(f"  {sec:.4f}s {stmt}")

    print()


if __name__ == "__main__":
    cases = [
        "",
        "f_curriculum=all",
        "f_curriculum=junior_high",
        "f_curriculum=vocational_high",
    ]
    for qs in cases:
        print(f"=== CASE ?{qs or '/skills'} ===")
        run_case(qs)
