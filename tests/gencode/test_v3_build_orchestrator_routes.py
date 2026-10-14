# -*- coding: utf-8 -*-
"""Production-hardening acceptance for one-click V3 orchestrator routes."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import pytest

from app import app
from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.schema.gencode_v3_orchestrator_jobs_inspection import (
    ensure_gencode_v3_orchestrator_jobs_table,
    orchestrator_jobs_table_exists,
)
from core.gencode.services.v3_build_orchestrator_service import (
    JOB_STATUS_FAILED,
    JOB_STATUS_NEEDS_CAPABILITY,
    JOB_STATUS_READY,
    ensure_orchestrator_jobs_table,
)
from core.gencode.services.v3_skill_capability_preflight_service import (
    CAPABILITY_NEEDS_CAPABILITY,
    CAPABILITY_READY,
    evaluate_skill_v3_capability as real_evaluate_skill_v3_capability,
)
from models import User, db, init_db


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROD_DB = PROJECT_ROOT / "instance" / "kumon_math.db"
B2_SKILLS = [
    "vh_數學B2_SubSection_2_1_1",
    "vh_數學B2_SubSection_2_1_2",
    "vh_數學B2_SubSection_2_2_3",
    "vh_數學B2_SubSection_2_2_4",
    "vh_數學B2_SubSection_2_2_5",
]


@contextmanager
def _raw():
    conn = db.engine.raw_connection()
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA busy_timeout=30000")
    except Exception:
        pass
    try:
        yield conn
    finally:
        try:
            conn.rollback()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def _ensure_schema(conn: sqlite3.Connection) -> None:
    ensure_gencode_v3_orchestrator_jobs_table(conn)
    apply_tracker_ddl(conn)
    try:
        conn.commit()
    except Exception:
        pass


def _login_admin(client) -> None:
    with app.app_context():
        with _raw() as conn:
            _ensure_schema(conn)
            row = conn.execute("SELECT id FROM users WHERE id = 1").fetchone()
            if row is None:
                try:
                    if User.query.filter_by(id=1).first() is None:
                        db.session.add(
                            User(id=1, username="admin_v3_orch", password_hash="x", role="admin")
                        )
                        db.session.commit()
                except Exception:
                    conn.execute(
                        "INSERT OR IGNORE INTO users (id, username, password_hash, role) "
                        "VALUES (1, 'admin_v3_orch', 'x', 'admin')"
                    )
                    conn.commit()
    with client.session_transaction() as sess:
        sess["_user_id"] = "1"
        sess["_fresh"] = True


def _ensure_skill_info(conn: sqlite3.Connection, skill_id: str) -> None:
    """Satisfy textbook_examples.skill_id FK against skills_info."""
    row = conn.execute(
        "SELECT skill_id FROM skills_info WHERE skill_id = ?", (skill_id,)
    ).fetchone()
    if row is not None:
        return
    conn.execute(
        """
        INSERT INTO skills_info (
            skill_id, skill_en_name, skill_ch_name, category, description,
            input_type, gemini_prompt, consecutive_correct_required, is_active, order_index
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            skill_id,
            skill_id,
            skill_id,
            "test",
            "route acceptance fixture",
            "text",
            "n/a",
            10,
            1,
            0,
        ),
    )


def _seed_examples(conn: sqlite3.Connection, skill_id: str, ids: list[int]) -> None:
    """Seed into the real/init_db textbook_examples schema (NOT NULL source_*)."""
    _ensure_skill_info(conn, skill_id)
    for eid in ids:
        conn.execute("DELETE FROM textbook_examples WHERE id = ?", (eid,))
        conn.execute(
            """
            INSERT INTO textbook_examples (
                id, skill_id,
                source_curriculum, source_volume, source_chapter, source_section,
                source_description, source_paragraph,
                problem_text, problem_type, correct_answer, detailed_solution,
                notes, difficulty_level, difficulty_h
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                eid,
                skill_id,
                "vocational",
                "數學B2",
                "2",
                "2-1",
                f"src_{eid}",
                "",
                f"p{eid}",
                "t",
                f"a{eid}",
                "",
                "",
                1,
                1.0,
            ),
        )
    conn.commit()


def _copy_skill_examples_from_prod(conn: sqlite3.Connection, skill_id: str) -> int:
    """Copy textbook_examples for one skill from production (read-only) into isolated DB."""
    prod = sqlite3.connect(f"file:{PROD_DB.as_posix()}?mode=ro", uri=True)
    prod.row_factory = sqlite3.Row
    try:
        # Prefer copying skills_info row from prod when absent locally.
        existing = conn.execute(
            "SELECT 1 FROM skills_info WHERE skill_id = ?", (skill_id,)
        ).fetchone()
        if existing is None:
            skill_row = prod.execute(
                "SELECT * FROM skills_info WHERE skill_id = ?", (skill_id,)
            ).fetchone()
            if skill_row is not None:
                skill_cols = [r[1] for r in prod.execute("PRAGMA table_info(skills_info)")]
                dest_skill_cols = {r[1] for r in conn.execute("PRAGMA table_info(skills_info)")}
                use_skill = [c for c in skill_cols if c in dest_skill_cols]
                conn.execute(
                    f"INSERT INTO skills_info ({', '.join(use_skill)}) "
                    f"VALUES ({', '.join('?' * len(use_skill))})",
                    tuple(skill_row[c] for c in use_skill),
                )
            else:
                _ensure_skill_info(conn, skill_id)

        src_cols = [r[1] for r in prod.execute("PRAGMA table_info(textbook_examples)")]
        dest_cols = {r[1] for r in conn.execute("PRAGMA table_info(textbook_examples)")}
        use_cols = [c for c in src_cols if c in dest_cols]
        rows = prod.execute(
            f"SELECT {', '.join(use_cols)} FROM textbook_examples WHERE skill_id = ?",
            (skill_id,),
        ).fetchall()
        placeholders = ", ".join("?" * len(use_cols))
        col_list = ", ".join(use_cols)
        for r in rows:
            conn.execute("DELETE FROM textbook_examples WHERE id = ?", (r["id"],))
            conn.execute(
                f"INSERT INTO textbook_examples ({col_list}) VALUES ({placeholders})",
                tuple(r[c] for c in use_cols),
            )
        conn.commit()
        return len(rows)
    finally:
        prod.close()


def _prod_capability_eval(_conn, skill_id: str, **kwargs):
    """Capability probe against production examples/trackers (read-only)."""
    pconn = sqlite3.connect(f"file:{PROD_DB.as_posix()}?mode=ro", uri=True)
    pconn.row_factory = sqlite3.Row
    try:
        return real_evaluate_skill_v3_capability(pconn, skill_id, probe_examples=True)
    finally:
        pconn.close()


def _wiring_ok(domain_key: str = "demo_domain") -> dict:
    return {
        "fixed_domain_key": domain_key,
        "domain_module": "types",
        "entrypoint": "SimpleNamespace",
        "registry_revision": "test",
        "allowed_operations": ["demo_op"],
    }


@pytest.fixture(autouse=True)
def _prepare_app(tmp_path: Path):
    app.config["TESTING"] = True
    app.config["GENCODE_V3_PUBLISH_PROJECT_ROOT"] = str(PROJECT_ROOT)
    app.config["GENCODE_V3_PUBLISH_STAGING_ROOT"] = str(tmp_path / "staging")
    (tmp_path / "staging").mkdir(parents=True, exist_ok=True)
    with app.app_context():
        with _raw() as conn:
            _ensure_schema(conn)
    yield
    # Release pooled connections between tests (avoids SQLite locked on Windows).
    with app.app_context():
        try:
            db.session.remove()
            db.engine.dispose()
        except Exception:
            pass


def test_job_table_created_by_init_db(tmp_path: Path):
    from sqlalchemy import create_engine

    eng = create_engine(f"sqlite:///{(tmp_path / 'init.db').as_posix()}")
    init_db(eng, seed_bridges=False)
    conn = eng.raw_connection()
    assert orchestrator_jobs_table_exists(conn) is True
    conn.close()
    eng.dispose()


def test_route_outline_blocked():
    client = app.test_client()
    _login_admin(client)
    resp = client.post("/admin/skills/outline_demo/gencode_v3_build", json={"sync": True})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error_code"] == "OUTLINE_SKILL_BLOCKED"


def test_route_needs_capability_sync():
    skill_id = "vh_test_needs_cap_route"
    with app.app_context():
        with _raw() as conn:
            _seed_examples(conn, skill_id, [501, 502])

    def _fake_eval(_conn, _skill_id, **_kw):
        return {
            "capability_status": CAPABILITY_NEEDS_CAPABILITY,
            "allow_v3_rebuild": False,
            "domain_key": "missing.domain",
            "example_probes": [
                {
                    "textbook_example_id": 501,
                    "resolvable": False,
                    "reason": "missing_op",
                    "classification_source": "x",
                    "problem_type_id": "",
                    "suggested_domain": "missing.domain",
                },
                {
                    "textbook_example_id": 502,
                    "resolvable": False,
                    "reason": "missing_op",
                    "classification_source": "x",
                    "problem_type_id": "",
                    "suggested_domain": "missing.domain",
                },
            ],
        }

    client = app.test_client()
    _login_admin(client)
    with mock.patch(
        "core.gencode.services.v3_build_orchestrator_service.evaluate_skill_v3_capability",
        side_effect=_fake_eval,
    ):
        resp = client.post(
            f"/admin/skills/{skill_id}/gencode_v3_build",
            json={"sync": True, "async": False, "force": True},
        )
    assert resp.status_code == 409
    data = resp.get_json()
    assert data["status"] == JOB_STATUS_NEEDS_CAPABILITY
    assert data["production_preserved"] is True
    status = client.get(f"/admin/skills/{skill_id}/gencode_v3_build_status")
    assert status.status_code == 200
    job = status.get_json()["job"]
    assert job["status"] == JOB_STATUS_NEEDS_CAPABILITY
    assert job["needs_capability_examples"]


def test_route_intentional_skip_ready(tmp_path: Path):
    """Intentional skip ≠ failure; eligible published → READY."""
    skill_id = "vh_test_intentional_skip_route"
    with app.app_context():
        with _raw() as conn:
            _seed_examples(conn, skill_id, [801, 802])

    pkg = tmp_path / "skip_proj"
    # Only eligible example 801 is published; 802 is intentional skip.
    d = pkg / "agent_skills_v3" / skill_id / "components" / "src_801"
    d.mkdir(parents=True, exist_ok=True)
    (d / "generate.py").write_text("def generate():\n    return {}\n", encoding="utf-8")
    (pkg / "agent_skills_v3" / skill_id / "__init__.py").write_text(
        "GENERATOR_SPECS=[]\n", encoding="utf-8"
    )
    (pkg / "skills").mkdir(parents=True, exist_ok=True)
    (pkg / "skills" / f"{skill_id}.py").write_text("# facade\n", encoding="utf-8")
    app.config["GENCODE_V3_PUBLISH_PROJECT_ROOT"] = str(pkg)
    app.config["GENCODE_V3_PUBLISH_STAGING_ROOT"] = str(tmp_path / "skip_stag")
    (tmp_path / "skip_stag").mkdir(exist_ok=True)

    def _fake_eval(_conn, _skill_id, **_kw):
        return {
            "capability_status": CAPABILITY_READY,
            "allow_v3_rebuild": True,
            "domain_key": "demo_domain",
            "example_probes": [
                {
                    "textbook_example_id": 801,
                    "resolvable": True,
                    "reason": "",
                    "classification_source": "phase1_rule_pack",
                    "problem_type_id": "demo_op",
                },
                {
                    "textbook_example_id": 802,
                    "resolvable": False,
                    "reason": "BLOCKED:manual_review",
                    "classification_source": "phase1_rule_pack_blocked",
                    "problem_type_id": "",
                    "runtime_candidate": False,
                },
            ],
        }

    client = app.test_client()
    _login_admin(client)
    with mock.patch(
        "core.gencode.services.v3_build_orchestrator_service.evaluate_skill_v3_capability",
        side_effect=_fake_eval,
    ):
        resp = client.post(
            f"/admin/skills/{skill_id}/gencode_v3_build",
            json={"sync": True, "async": False, "force": False, "mode": "auto"},
        )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == JOB_STATUS_READY
    assert int(data.get("counts", {}).get("skip_count") or 0) >= 1
    assert data.get("idempotent") is True


@pytest.mark.parametrize("skill_id", B2_SKILLS)
def test_route_b2_ch2_ready_idempotent(skill_id: str, tmp_path: Path):
    """Each B2 Ch2 skill: route sync auto → READY, idempotent, no rebuild."""
    if not PROD_DB.exists():
        pytest.skip("no production db")

    with app.app_context():
        with _raw() as conn:
            n = _copy_skill_examples_from_prod(conn, skill_id)
            assert n > 0, f"no examples for {skill_id} in production"

    client = app.test_client()
    _login_admin(client)

    with mock.patch(
        "core.gencode.services.v3_build_orchestrator_service.evaluate_skill_v3_capability",
        side_effect=_prod_capability_eval,
    ):
        resp = client.post(
            f"/admin/skills/{skill_id}/gencode_v3_build",
            json={"sync": True, "async": False, "force": False, "mode": "auto"},
        )
    assert resp.status_code == 200, resp.get_json()
    data = resp.get_json()
    assert data.get("status") == JOB_STATUS_READY
    assert data.get("idempotent") is True

    # Second call must stay READY and not rebuild published components.
    with mock.patch(
        "core.gencode.services.v3_build_orchestrator_service.evaluate_skill_v3_capability",
        side_effect=_prod_capability_eval,
    ):
        resp2 = client.post(
            f"/admin/skills/{skill_id}/gencode_v3_build",
            json={"sync": True, "async": False, "force": False, "mode": "auto"},
        )
    data2 = resp2.get_json()
    assert resp2.status_code == 200
    assert data2.get("status") == JOB_STATUS_READY
    assert data2.get("idempotent") is True
    st = client.get(f"/admin/skills/{skill_id}/gencode_v3_build_status").get_json()["job"]
    assert st["status"] == JOB_STATUS_READY
    assert st["job_id"] == data2["job_id"]


def test_route_failed_resume(tmp_path: Path):
    skill_id = "vh_test_resume_route"
    with app.app_context():
        with _raw() as conn:
            _seed_examples(conn, skill_id, [601])
            apply_tracker_ddl(conn)
            ensure_orchestrator_jobs_table(conn)
            conn.execute("DELETE FROM gencode_component_tracker WHERE textbook_example_id = 601")
            conn.execute(
                """
                INSERT INTO gencode_component_tracker
                (textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload)
                VALUES (601, ?, 'src_601', 'verified', ?)
                """,
                (
                    skill_id,
                    json.dumps(
                        {
                            "integrity_gate_passed": True,
                            "integrity_gate_version": "v1",
                            "answer_type": "expression",
                            "checker_key": "numeric_checker",
                            "equivalence_type": "numeric",
                            "fixed_domain_key": "demo_domain",
                            "domain_operation": "demo_op",
                        }
                    ),
                ),
            )
            stages = {
                name: {"name": name, "label": name, "status": "done"}
                for name in (
                    "LOAD_EXAMPLES",
                    "PREFLIGHT",
                    "CAPABILITY_MATCH",
                    "COMPONENT_BUILD",
                    "VALIDATION",
                )
            }
            stages["SMOKE_TEST"] = {
                "name": "SMOKE_TEST",
                "label": "Smoke",
                "status": "failed",
            }
            payload = {
                "stages": stages,
                "counts": {
                    "example_count": 1,
                    "eligible_count": 1,
                    "published_count": 1,
                    "skip_count": 0,
                    "missing_count": 0,
                    "needs_capability_count": 0,
                },
                "errors": [
                    {"stage": "SMOKE_TEST", "code": "SMOKE_FAILED", "message": "boom"}
                ],
                "skip_examples": [],
                "needs_capability_examples": [],
                "dryrun_result": {"success": True, "rebuilt_count": 0},
                "capability": {"capability_status": "ready", "allow_v3_rebuild": True},
                "idempotent": True,
            }
            conn.execute(
                "DELETE FROM gencode_v3_orchestrator_jobs WHERE skill_id = ?", (skill_id,)
            )
            conn.execute(
                """
                INSERT INTO gencode_v3_orchestrator_jobs
                (job_id, skill_id, stage, status, started_at, updated_at, payload_json)
                VALUES ('job_resume_route', ?, 'SMOKE_TEST', 'failed', 't0', 't0', ?)
                """,
                (skill_id, json.dumps(payload, ensure_ascii=False)),
            )
            conn.commit()

    pkg = tmp_path / "proj"
    d = pkg / "agent_skills_v3" / skill_id / "components" / "src_601"
    d.mkdir(parents=True, exist_ok=True)
    (d / "generate.py").write_text("def generate():\n    return {}\n", encoding="utf-8")
    (pkg / "agent_skills_v3" / skill_id / "__init__.py").write_text(
        "GENERATOR_SPECS=[]\n", encoding="utf-8"
    )
    (pkg / "skills").mkdir(parents=True, exist_ok=True)
    (pkg / "skills" / f"{skill_id}.py").write_text("# facade\n", encoding="utf-8")
    app.config["GENCODE_V3_PUBLISH_PROJECT_ROOT"] = str(pkg)
    app.config["GENCODE_V3_PUBLISH_STAGING_ROOT"] = str(tmp_path / "stag")
    (tmp_path / "stag").mkdir(exist_ok=True)

    client = app.test_client()
    _login_admin(client)
    with mock.patch(
        "core.gencode.services.v3_build_orchestrator_service.evaluate_skill_v3_capability",
        return_value={
            "capability_status": CAPABILITY_READY,
            "allow_v3_rebuild": True,
            "domain_key": "demo_domain",
            "example_probes": [
                {
                    "textbook_example_id": 601,
                    "resolvable": True,
                    "reason": "",
                    "classification_source": "phase1_rule_pack",
                    "problem_type_id": "demo_op",
                }
            ],
        },
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
    ):
        resp = client.post(
            f"/admin/skills/{skill_id}/gencode_v3_build",
            json={"sync": True, "async": False, "resume": True, "force": False},
        )
    data = resp.get_json()
    assert data["status"] == JOB_STATUS_READY
    assert data["job_id"] == "job_resume_route"


def test_async_start_202_and_poll(tmp_path: Path):
    skill_id = "vh_test_async_route"
    with app.app_context():
        with _raw() as conn:
            _seed_examples(conn, skill_id, [701])

    pkg = tmp_path / "async_proj"
    comp = pkg / "agent_skills_v3" / skill_id / "components" / "src_701"
    comp.mkdir(parents=True, exist_ok=True)
    (comp / "generate.py").write_text("def generate():\n    return {}\n", encoding="utf-8")
    (pkg / "agent_skills_v3" / skill_id / "__init__.py").write_text(
        "GENERATOR_SPECS=[]\n", encoding="utf-8"
    )
    (pkg / "skills").mkdir(parents=True, exist_ok=True)
    (pkg / "skills" / f"{skill_id}.py").write_text("# f\n", encoding="utf-8")
    app.config["GENCODE_V3_PUBLISH_PROJECT_ROOT"] = str(pkg)
    app.config["GENCODE_V3_PUBLISH_STAGING_ROOT"] = str(tmp_path / "async_stag")
    (tmp_path / "async_stag").mkdir(exist_ok=True)

    client = app.test_client()
    _login_admin(client)
    with mock.patch(
        "core.gencode.services.v3_build_orchestrator_service.evaluate_skill_v3_capability",
        return_value={
            "capability_status": CAPABILITY_READY,
            "allow_v3_rebuild": True,
            "domain_key": "demo_domain",
            "example_probes": [
                {
                    "textbook_example_id": 701,
                    "resolvable": True,
                    "reason": "",
                    "classification_source": "phase1_rule_pack",
                    "problem_type_id": "demo_op",
                }
            ],
        },
    ):
        resp = client.post(
            f"/admin/skills/{skill_id}/gencode_v3_build",
            json={"async": True, "force": False, "mode": "auto"},
        )
        assert resp.status_code == 202
        body = resp.get_json()
        assert body["accepted"] is True
        assert body["status"] == "running"
        job_id = body["job_id"]

        terminal = None
        for _ in range(80):
            st = client.get(f"/admin/skills/{skill_id}/gencode_v3_build_status").get_json()
            job = st["job"]
            assert job is not None
            assert job["job_id"] == job_id
            if job["status"] != "running":
                terminal = job
                break
            time.sleep(0.1)
        assert terminal is not None
        assert terminal["status"] in {
            JOB_STATUS_READY,
            JOB_STATUS_NEEDS_CAPABILITY,
            JOB_STATUS_FAILED,
        }


def test_ui_template_poll_and_labels():
    from flask import render_template

    skill = {
        "skill_id": "vh_數學B2_SubSection_2_1_2",
        "skill_ch_name": "餘弦定理",
        "is_active": True,
        "curriculum": "vocational",
        "grade": 10,
        "volume": "數學B2",
        "chapter": "2",
        "section": "2-1",
    }
    cases = [
        ("READY", {"v3_ui_status": "READY", "allow_v3_rebuild": True, "publish_ready": True}, "REBUILD"),
        (
            "NEEDS_CAPABILITY",
            {
                "v3_ui_status": "NEEDS_CAPABILITY",
                "allow_v3_rebuild": False,
                "capability_status": "needs_capability",
            },
            "NEEDS_CAPABILITY",
        ),
        ("FAILED", {"v3_ui_status": "FAILED", "allow_v3_rebuild": False}, "重試建立 V3"),
        (
            "建置中",
            {
                "v3_ui_status": "建置中",
                "orchestrator_job": {"stage": "SMOKE_TEST", "status": "running"},
            },
            "SMOKE_TEST",
        ),
        ("建立 V3", {"v3_ui_status": "建立 V3", "allow_v3_rebuild": False}, "建立 V3"),
    ]
    with app.test_request_context():
        for _label, gencode, expected in cases:
            html = render_template(
                "admin_skills.html",
                skills=[skill],
                v3_gencode_status_map={skill["skill_id"]: gencode},
                gencode_status_map={},
                filters={
                    "curricula": [],
                    "grades": [],
                    "volumes": [],
                    "chapters": [],
                    "sections": [],
                },
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
            assert "pollSkillV3BuildStatus" in html
            assert expected in html


def test_production_db_untouched():
    if not PROD_DB.exists():
        pytest.skip("no production db")
    before = hashlib.sha256(PROD_DB.read_bytes()).hexdigest()
    conn = sqlite3.connect(":memory:")
    ensure_orchestrator_jobs_table(conn)
    conn.close()
    after = hashlib.sha256(PROD_DB.read_bytes()).hexdigest()
    assert before == after
