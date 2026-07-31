# -*- coding: utf-8 -*-
"""DELETE_CORE success must not be visually overridden by a prior failed import job."""
from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app import create_app
from core.routes.admin import CORE_CLEAR_CONFIRM_TOKEN
from core.session_safety import SERVER_RESULT_DIR, put_large_result_in_server_store
from models import User, db

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = PROJECT_ROOT / "reports" / "pytest_db_maintenance_status_ui"


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def app_ctx(monkeypatch):
    import config as _cfg

    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    run_dir = TEST_ROOT / uuid.uuid4().hex[:10]
    run_dir.mkdir(parents=True, exist_ok=True)
    jobs_dir = run_dir / "runtime_jobs"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    db_path = run_dir / "ui.db"

    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    monkeypatch.setattr("core.session_safety.SERVER_RESULT_DIR", jobs_dir)
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            admin = User(username=f"admin_{uuid.uuid4().hex[:6]}", password_hash="x", role="admin")
            db.session.add(admin)
            db.session.commit()
            yield app, admin.id, jobs_dir
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        shutil.rmtree(run_dir, ignore_errors=True)


def test_delete_core_success_not_overridden_by_failed_import_job(app_ctx):
    app, admin_id, jobs_dir = app_ctx
    with app.app_context():
        failed_job_id = put_large_result_in_server_store(
            {
                "route": "upload_db",
                "filename": "broken.xlsx",
                "mode": "core",
                "success": False,
                "message": "final_status: failed\nfinal_status_reason: post_import_validation_failed\nfatal_errors: 1078",
                "summary": {
                    "success": False,
                    "status": "failed",
                    "final_status": "failed",
                    "final_status_reason": "post_import_validation_failed",
                    "table_count": 21,
                    "source_rows": 6126,
                    "imported_rows": 6126,
                    "failed_rows": 0,
                    "fatal_errors": 1078,
                    "warning_count": 1759,
                    "error_count": 1078,
                    "orphan_skill_curriculum_count": 24,
                },
            },
            kind="import",
            job_id="20260731080038_dcafc89d",
        )
        assert (jobs_dir / f"import_{failed_job_id}.json").exists()

        client = app.test_client()
        _login(client, admin_id)
        with client.session_transaction() as sess:
            sess["last_import_job_id"] = failed_job_id
            sess["last_db_maintenance_op"] = "import"

        # Baseline: visiting after failed import still can show import as current.
        baseline = client.get("/db_maintenance", follow_redirects=True)
        baseline_body = baseline.get_data(as_text=True)
        assert baseline.status_code == 200
        assert "本次匯入結果" in baseline_body or "Import failed" in baseline_body
        assert failed_job_id in baseline_body

        r = client.post(
            "/db_maintenance",
            data={
                "action": "clear_all_data",
                "mode": "core",
                "core_scope_mode": "all",
                "core_clear_confirm": CORE_CLEAR_CONFIRM_TOKEN,
            },
            follow_redirects=True,
        )
        body = r.get_data(as_text=True)
        assert r.status_code == 200
        assert "DELETE_CORE 完成" in body
        assert "alert-success" in body

        # Top current-op zone must not present the old failed import as current status.
        assert 'data-current-op="import"' not in body
        assert "本次匯入結果" not in body
        assert "Import failed" not in body.split("最近匯入紀錄")[0]

        # Failed job remains only in history section.
        assert 'id="recent-import-history"' in body
        history = body.split("最近匯入紀錄", 1)[1]
        assert failed_job_id in history
        assert 'data-import-job-id="20260731080038_dcafc89d"' in history

        with client.session_transaction() as sess:
            assert sess.get("last_db_maintenance_op") == "clear"
            assert sess.get("last_import_job_id") == failed_job_id
