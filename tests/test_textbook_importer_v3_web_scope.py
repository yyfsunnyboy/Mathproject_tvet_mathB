"""The Web importer opts into a safe scope without changing legacy callers."""

from __future__ import annotations

from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

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
