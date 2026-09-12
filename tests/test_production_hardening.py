from __future__ import annotations

import importlib
import os
import sys
import uuid
from pathlib import Path
from urllib.parse import quote

import pytest
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from config import Config


SAFE_TEST_SECRET = "test-only-production-secret-key-0123456789abcdef"
PRACTICE_SKILL = "vh_數學B1_DivisionPointCoordinates"
PRACTICE_PROBLEM_TYPE = "ordered_pair_compute_internal_division_point_coordinates_short_answer_two_coordi"


@pytest.fixture(scope="module")
def app_module():
    db_path = Path("reports") / "runtime_tests" / f"hardening_{uuid.uuid4().hex}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    previous_uri = Config.SQLALCHEMY_DATABASE_URI
    previous_seed_only = os.environ.get("SEED_DB_ONLY")
    Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + db_path.resolve().as_posix()
    os.environ["SEED_DB_ONLY"] = "1"
    try:
        # Ensure app.py's module-level WSGI object also uses the isolated DB.
        sys.modules.pop("app", None)
        module = importlib.import_module("app")
        yield module
    finally:
        Config.SQLALCHEMY_DATABASE_URI = previous_uri
        if previous_seed_only is None:
            os.environ.pop("SEED_DB_ONLY", None)
        else:
            os.environ["SEED_DB_ONLY"] = previous_seed_only
        for candidate in (db_path, Path(str(db_path) + "-wal"), Path(str(db_path) + "-shm")):
            try:
                candidate.unlink(missing_ok=True)
            except OSError:
                pass


@pytest.fixture()
def hardened_app(app_module, monkeypatch):
    monkeypatch.setenv("SEED_DB_ONLY", "1")
    app = app_module.create_app()
    app.config.update(TESTING=True)
    return app


def test_production_missing_secret_fails(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="requires the SECRET_KEY"):
        Config.resolve_secret_key(production=True)


def test_production_entry_missing_secret_fails(monkeypatch):
    runner = importlib.import_module("scripts.run_production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setattr(runner, "load_dotenv", lambda *_args, **_kwargs: False)
    with pytest.raises(RuntimeError, match="requires the SECRET_KEY"):
        runner.build_production_app()


def test_development_secret_fallback_remains_available(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    assert Config.resolve_secret_key(production=False) == Config.DEV_SECRET_KEY


def test_production_app_disables_debug(app_module, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", SAFE_TEST_SECRET)
    monkeypatch.setenv("SEED_DB_ONLY", "1")
    app = app_module.create_app(production=True)
    assert app.debug is False
    assert app.config["MATHPROJECT_ENV"] == "production"
    assert app.config["SECRET_KEY"] == SAFE_TEST_SECRET


def test_sqlite_pragmas_apply_to_each_connection(hardened_app):
    with hardened_app.app_context():
        engine = hardened_app.extensions["sqlalchemy"].engine
        with engine.connect() as first, engine.connect() as second:
            for connection in (first, second):
                assert connection.exec_driver_sql("PRAGMA journal_mode").scalar().lower() == "wal"
                assert connection.exec_driver_sql("PRAGMA synchronous").scalar() == 1
                assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1
                assert connection.exec_driver_sql("PRAGMA busy_timeout").scalar() == 30_000


def test_healthz_reports_database_ready(hardened_app):
    response = hardened_app.test_client().get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {
        "app": "alive",
        "database": "ok",
        "status": "ok",
    }


def test_diagnose_error_releases_connection_before_ai(hardened_app, monkeypatch):
    analyzer = importlib.import_module("core.ai_analyzer")
    observed = {"called": False}

    class FakeResponse:
        text = '{"error_type":"careless","related_prerequisite_id":null,"prerequisite_explanation":null}'
        candidates = []

    class FakeModel:
        def generate_content(self, *_args, **_kwargs):
            from models import db

            engine = hardened_app.extensions["sqlalchemy"].engine
            assert engine.pool.checkedout() == 0
            assert db.session().in_transaction() is False
            observed["called"] = True
            return FakeResponse()

    monkeypatch.setattr(analyzer, "get_model", lambda: FakeModel())

    with hardened_app.test_request_context("/check_answer"):
        from models import db

        db.session.execute(text("SELECT 1"))
        engine = hardened_app.extensions["sqlalchemy"].engine
        assert engine.pool.checkedout() == 1
        result = analyzer.diagnose_error("1+1", "2", "3", prerequisite_units=[])
        assert observed["called"] is True
        assert result["error_type"] == "careless"


def test_login_practice_and_check_answer_regression(hardened_app):
    from models import SkillCurriculum, SkillInfo, User, db

    username = f"hardening_{uuid.uuid4().hex[:10]}"
    password = "test-password"
    with hardened_app.app_context():
        user = User(
            username=username,
            password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
            role="student",
        )
        if db.session.get(SkillInfo, PRACTICE_SKILL) is None:
            db.session.add(
                SkillInfo(
                    skill_id=PRACTICE_SKILL,
                    skill_en_name="Division point coordinates",
                    skill_ch_name="分點坐標",
                    description="test",
                    gemini_prompt="test",
                    is_active=True,
                )
            )
            db.session.add(
                SkillCurriculum(
                    skill_id=PRACTICE_SKILL,
                    curriculum="vocational",
                    grade=10,
                    volume="數學B1",
                    chapter="第2章 坐標系與直線方程式",
                    section="2-1",
                    display_order=1,
                )
            )
        db.session.add(user)
        db.session.commit()

    client = hardened_app.test_client()
    login_response = client.post(
        "/login",
        data={"username": username, "password": password, "role": "student"},
    )
    assert login_response.status_code == 302
    assert login_response.headers["Location"].endswith("/dashboard")

    practice_response = client.get(f"/practice/{quote(PRACTICE_SKILL)}")
    assert practice_response.status_code == 200

    question_response = client.get(
        f"/get_next_question?skill={quote(PRACTICE_SKILL)}"
        f"&problem_type={PRACTICE_PROBLEM_TYPE}&gen_seed=17&level=1"
    )
    assert question_response.status_code == 200
    question = question_response.get_json() or {}
    assert question.get("question_uid")

    answer_response = client.post(
        "/check_answer",
        json={
            "skill_id": PRACTICE_SKILL,
            "question_uid": question["question_uid"],
            "problem_type_id": question.get("problem_type_id", ""),
            "answer": "__wrong__",
        },
    )
    assert answer_response.status_code == 200
    assert (answer_response.get_json() or {}).get("stale_question") is not True
