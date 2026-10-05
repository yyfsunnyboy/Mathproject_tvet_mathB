"""The Web importer opts into a safe scope without changing legacy callers."""

from __future__ import annotations

from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from flask import Flask
from werkzeug.datastructures import MultiDict

from core.routes import admin


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TYPES = {
    "textbook_example", "in_class_practice", "textbook_exercise",
    "advanced_exercise", "self_assessment", "exam_practice",
}


class _ScopeInputs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            self.inputs.append(dict(attrs))


def test_web_default_scope_and_formal_mode():
    parser = _ScopeInputs()
    parser.feed((ROOT / "templates/textbook_importer_v3.html").read_text(encoding="utf-8"))
    selected = {
        field["value"] for field in parser.inputs
        if field.get("name") == "target_source_types" and "checked" in field
    }
    assert selected == DEFAULT_TYPES
    assert any(
        field.get("value") == "advanced_exercise" and "disabled" not in field
        for field in parser.inputs
    )
    assert any(field.get("name") == "source_type_scope_present" for field in parser.inputs)
    assert any(field.get("name") == "dry_run" and field.get("value") == "false" for field in parser.inputs)
    modes = {field.get("value"): field for field in parser.inputs if field.get("name") == "import_mode"}
    assert set(modes) == {"update_existing", "insert_missing_only", "replace_section"}
    assert "checked" in modes["insert_missing_only"]
    assert all(field.get("type") == "radio" for field in modes.values())


def test_web_curriculum_options_keep_existing_general_identities():
    template = (ROOT / "templates/textbook_importer_v3.html").read_text(encoding="utf-8")

    assert 'const GENERAL_HIGH_OPTIONS' in template
    assert "general: GENERAL_HIGH_OPTIONS" in template
    assert "longteng: [" in template
    for volume, grade in (
        ("數學1", 10), ("數學2", 10), ("數學3A", 11),
        ("數學4A", 11), ("選修數學甲(上)", 12), ("選修數學甲(下)", 12),
    ):
        assert f"{{ volume: '{volume}', grade: {grade} }}" in template
    assert "gradeInput.readOnly = isGeneral" in template
    assert "applyCurriculumConfiguration();" in template


def test_route_forwards_vocational_ui_payload(monkeypatch):
    captured_upload = []
    captured_enqueue = []
    monkeypatch.setattr(admin, "current_user", SimpleNamespace(is_admin=True, role="teacher"))
    monkeypatch.setattr(admin, "resolve_gemini_api_key", lambda: ("test-key", "test"))
    monkeypatch.setattr(
        admin,
        "upload_textbook_source_batch",
        lambda **kwargs: captured_upload.append(kwargs) or (
            {"ok": True, "pairs": [{}], "batch": {"curriculum": "vocational", "volume": "數學B2", "grade": 10}},
            200,
        ),
    )
    monkeypatch.setattr(
        admin,
        "enqueue_v3_batch_pipeline",
        lambda **kwargs: captured_enqueue.append(kwargs) or "general-test-task",
    )
    monkeypatch.setattr(admin, "url_for", lambda endpoint, **kwargs: "/test")
    app = Flask(__name__)
    app.secret_key = "test"
    data = MultiDict([
        ("curriculum", "vocational"), ("publisher", "longteng"),
        ("grade", "10"), ("volume", "數學B2"),
    ])

    with app.test_request_context("/textbook_importer_v3", method="POST", data=data):
        response, status = admin.admin_textbook_importer_v3.__wrapped__()

    assert status == 200 and response.get_json()["ok"]
    assert "pipeline" not in response.get_json()
    assert {
        key: captured_upload[0][key]
        for key in ("curriculum", "publisher", "grade", "volume")
    } == {
        "curriculum": "vocational", "publisher": "longteng", "grade": "10", "volume": "數學B2"
    }
    assert {
        key: captured_enqueue[0][key]
        for key in ("curriculum", "publisher", "grade", "volume")
    } == {
        "curriculum": "vocational", "publisher": "longteng", "grade": 10, "volume": "數學B2"
    }


def test_v3_general_reuses_v1_dispatch_without_v3_pipeline(monkeypatch):
    captured = []
    monkeypatch.setattr(admin, "current_user", SimpleNamespace(is_admin=True, role="teacher"))
    monkeypatch.setattr(admin, "resolve_gemini_api_key", lambda: ("test-key", "test"))
    monkeypatch.setattr(
        admin,
        "enqueue_v1_textbook_upload_batch",
        lambda upload_files, curriculum_info, **kwargs: captured.append(
            (upload_files, curriculum_info, kwargs)
        ) or "v1-general-task",
    )
    monkeypatch.setattr(
        admin,
        "upload_textbook_source_batch",
        lambda **kwargs: pytest.fail("general must not enter V3 storage"),
    )
    monkeypatch.setattr(
        admin,
        "enqueue_v3_batch_pipeline",
        lambda **kwargs: pytest.fail("general must not enqueue V3"),
    )
    monkeypatch.setattr(admin, "url_for", lambda endpoint, **kwargs: "/test")
    app = Flask(__name__)
    app.secret_key = "test"
    data = MultiDict([
        ("curriculum", "general"), ("publisher", "longteng"),
        ("grade", "10"), ("volume", "數學1"),
        ("textbook_docx[]", (BytesIO(b"docx"), "1-1.docx")),
        ("textbook_pdf[]", (BytesIO(b"pdf"), "1-1.pdf")),
    ])

    with app.test_request_context("/textbook_importer_v3", method="POST", data=data):
        response, status = admin.admin_textbook_importer_v3.__wrapped__()

    assert status == 200
    payload = response.get_json()
    assert payload["import_path"] == "v1_general"
    assert payload["task_id"] == "v1-general-task"
    assert payload["pipeline"] == "general_v1"
    assert payload["status_url"] == "/test"
    upload_files, curriculum_info, policy = captured[0]
    assert policy["track_general_status"] is True
    assert [file.filename for file in upload_files] == ["1-1.docx", "1-1.pdf"]
    assert curriculum_info == {
        "curriculum": "general", "publisher": "longteng", "grade": "10", "volume": "數學1"
    }
    assert policy["import_policy"]["docx_primary"] is True


def test_route_accepts_exercise_and_preserves_legacy_none(monkeypatch):
    captured = []
    monkeypatch.setattr(admin, "current_user", SimpleNamespace(is_admin=True, role="teacher"))
    monkeypatch.setattr(admin, "resolve_gemini_api_key", lambda: ("test-key", "test"))
    monkeypatch.setattr(admin, "upload_textbook_source_batch", lambda **kwargs: (
        {"ok": True, "pairs": [{}], "batch": {"volume": "數學B2"}}, 200
    ))
    monkeypatch.setattr(admin, "enqueue_v3_batch_pipeline", lambda **kwargs: captured.append(kwargs) or "test-task")
    monkeypatch.setattr(admin, "url_for", lambda endpoint, **kwargs: "/test")
    app = Flask(__name__)
    app.secret_key = "test"

    for data in (
        [("source_type_scope_present", "1"), ("dry_run", "false"), ("import_mode", "insert_missing_only")]
        + [("target_source_types", source_type) for source_type in sorted(DEFAULT_TYPES)],
        [("target_source_types", "textbook_example,textbook_exercise"), ("import_mode", "update_existing")],
        [],
    ):
        with app.test_request_context("/textbook_importer_v3", method="POST", data=MultiDict(data)):
            response, status = admin.admin_textbook_importer_v3.__wrapped__()
            assert status == 200
            assert response.get_json()["ok"]
    assert captured[0]["target_source_types"] == DEFAULT_TYPES
    assert captured[0]["allow_phase4"] is True
    assert captured[0]["import_mode"] == "insert_missing_only"
    assert captured[1]["target_source_types"] == {"textbook_example", "textbook_exercise"}
    assert captured[1]["import_mode"] == "update_existing"
    assert captured[2]["target_source_types"] is None
    assert captured[2]["import_mode"] == "update_existing"

    replace_data = MultiDict([
        ("target_source_types", "textbook_example"), ("import_mode", "replace_section"),
        ("replace_confirmed", "true"), ("textbook_docx[]", (BytesIO(b"docx"), "2-1.docx")),
    ])
    with app.test_request_context("/textbook_importer_v3", method="POST", data=replace_data):
        response, status = admin.admin_textbook_importer_v3.__wrapped__()
        assert status == 200 and response.get_json()["ok"]
    assert captured[3]["import_mode"] == "replace_section"

    for data in (
        [("source_type_scope_present", "1")],
        [("target_source_types", "unknown_type")],
    ):
        with app.test_request_context("/textbook_importer_v3", method="POST", data=MultiDict(data)):
            response, status = admin.admin_textbook_importer_v3.__wrapped__()
            assert status == 400
            assert response.get_json()["error"] == "invalid_target_source_types"
