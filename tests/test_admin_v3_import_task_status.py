# -*- coding: utf-8 -*-
"""Integration test for the V3 import progress status route."""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from app import create_app
from core.textbook_importer_v3_pipeline import V3_IMPORT_TASKS, build_v3_ui_result_payload
from models import User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def app_with_teacher():
    import config as _cfg

    db_path = Path("reports") / f"pytest_v3_task_status_{uuid.uuid4().hex[:8]}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            db.create_all()
            teacher = User(
                username=f"teacher_v3_{uuid.uuid4().hex[:6]}",
                password_hash="x",
                role="teacher",
            )
            db.session.add(teacher)
            db.session.commit()
            yield app, teacher.id
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        try:
            if db_path.exists():
                db_path.unlink()
        except OSError:
            pass


def test_task_status_route_returns_json_for_circular_payload(app_with_teacher):
    app, teacher_id = app_with_teacher

    task_id = f"test-circular-{uuid.uuid4().hex[:8]}"
    batch = {"task_id": task_id, "pairs": [], "ok": False}
    ui_result = build_v3_ui_result_payload(batch)
    # Intentionally create a circular reference to prove the serializer protects
    # the route instead of letting Flask return an HTML 500 traceback page.
    ui_result["self"] = ui_result
    batch["ui_result"] = ui_result

    V3_IMPORT_TASKS[task_id] = {
        "task_id": task_id,
        "status": "success",
        "stages": {},
        "result": batch,
        "error": None,
        "pair_index": 0,
        "pair_total": 0,
        "current_pair": None,
        "updated_at": "2026-01-01T00:00:00",
    }

    try:
        client = app.test_client()
        _login(client, teacher_id)
        response = client.get(f"/textbook_importer_v3/task/{task_id}")

        assert response.status_code == 200
        assert response.content_type.startswith("application/json")
        data = response.get_json()
        assert data["ok"] is True
        assert data["task_id"] == task_id
        # The circular branch should be replaced by the safe marker.
        assert data["result"]["self"] == "[Circular Reference]"
    finally:
        V3_IMPORT_TASKS.pop(task_id, None)
