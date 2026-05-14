# -*- coding: utf-8 -*-
from __future__ import annotations

import queue
import uuid
from pathlib import Path

import pytest

from app import create_app
from core.globals import TASK_QUEUES
from core.routes.admin import _coerce_progress_message, _format_sse_data
from models import User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def app_ctx(tmp_path):
    import config as _cfg

    db_path = tmp_path / f"db_import_progress_{uuid.uuid4().hex[:8]}.db"
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            admin = User(username=f"admin_{uuid.uuid4().hex[:6]}", password_hash="x", role="admin")
            db.session.add(admin)
            db.session.commit()
            yield app, admin.id
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri


def test_progress_messages_keep_utf8_text():
    m1 = "開始處理任務，共 1 個檔案..."
    m2 = "正在分析: 1-1_-.docx ..."
    m3 = "所有作業完成！"
    assert _coerce_progress_message(m1) == m1
    assert _coerce_progress_message(m2) == m2
    assert _coerce_progress_message(m3) == m3


def test_sse_formatter_handles_dict_without_type_error():
    payload = {"message": "開始處理任務，共 1 個檔案..."}
    text = _coerce_progress_message(payload)
    assert "開始處理任務，共 1 個檔案..." in text
    sse = _format_sse_data(payload)
    assert sse.startswith("data: ")


def test_importer_stream_content_type_has_utf8(app_ctx):
    app, admin_id = app_ctx
    client = app.test_client()
    _login(client, admin_id)

    task_id = f"task_{uuid.uuid4().hex[:6]}"
    q = queue.Queue()
    q.put("INFO: 開始處理任務，共 1 個檔案...")
    q.put("INFO: 正在分析: 1-1_-.docx ...")
    q.put("SUCCESS: 所有作業完成！")
    q.put("END_OF_STREAM")
    TASK_QUEUES[task_id] = q

    resp = client.get(f"/importer/stream/{task_id}")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("Content-Type", "")
    assert "charset=utf-8" in resp.headers.get("Content-Type", "").lower()
    body = resp.get_data(as_text=True)
    assert "開始處理任務，共 1 個檔案..." in body
    assert "正在分析: 1-1_-.docx ..." in body
    assert "所有作業完成！" in body


def test_templates_have_no_mojibake_tokens():
    files = [
        Path("templates/db_maintenance.html"),
        Path("templates/importer_status.html"),
    ]
    bad_tokens = ["鞈", "摨", "蝣", "隢", "嚗", "", "", "?", "甇?", "??"]
    for f in files:
        text = f.read_text(encoding="utf-8")
        for token in bad_tokens:
            assert token not in text

