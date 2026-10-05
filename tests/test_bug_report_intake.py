# -*- coding: utf-8 -*-
from __future__ import annotations

from io import BytesIO
import re

import pytest
from PIL import Image

from app import app
from models import User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True


def _image_bytes(image_format: str) -> bytes:
    image = Image.new("RGB", (2, 2), "white")
    output = BytesIO()
    image.save(output, format=image_format)
    return output.getvalue()


@pytest.fixture()
def bug_report_client(tmp_path):
    previous_upload_root = app.config.get("UPLOAD_FOLDER")
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    with app.app_context():
        user = User(username=f"bug_report_{tmp_path.name}", password_hash="x", role="student")
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    client = app.test_client()
    _login(client, user_id)
    try:
        yield client, user_id, tmp_path
    finally:
        if previous_upload_root is None:
            app.config.pop("UPLOAD_FOLDER", None)
        else:
            app.config["UPLOAD_FOLDER"] = previous_upload_root


def test_bug_report_requires_login(tmp_path) -> None:
    previous_upload_root = app.config.get("UPLOAD_FOLDER")
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    try:
        response = app.test_client().post(
            "/api/bug-report",
            data={"screenshot": (BytesIO(_image_bytes("PNG")), "screen.png"), "page_url": "http://example.test/practice"},
        )
        assert response.status_code in {302, 401}
        assert not (tmp_path / "bug_reports").exists()
    finally:
        if previous_upload_root is None:
            app.config.pop("UPLOAD_FOLDER", None)
        else:
            app.config["UPLOAD_FOLDER"] = previous_upload_root


@pytest.mark.parametrize(("image_format", "filename", "extension"), [("PNG", "screen.png", "png"), ("JPEG", "screen.jpg", "jpg"), ("WEBP", "screen.webp", "webp")])
def test_bug_report_saves_valid_screenshot_and_url_sidecar(bug_report_client, image_format, filename, extension) -> None:
    client, user_id, upload_root = bug_report_client
    page_url = "http://127.0.0.1:5000/practice/vh_數學B1_Test?level=1"
    with app.app_context():
        before_user_count = User.query.count()

    response = client.post(
        "/api/bug-report",
        data={"screenshot": (BytesIO(_image_bytes(image_format)), filename), "page_url": page_url},
    )
    assert response.status_code == 200
    assert response.get_json() == {"success": True}

    report_dir = upload_root / "bug_reports"
    image_paths = list(report_dir.glob(f"*.{extension}"))
    assert len(image_paths) == 1
    image_path = image_paths[0]
    assert re.fullmatch(rf"\d{{8}}_\d{{6}}_u{user_id}(?:_\d{{2}})?\.{extension}", image_path.name)
    assert image_path.with_suffix(".txt").read_text(encoding="utf-8") == f"page_url={page_url}\n"
    with app.app_context():
        assert User.query.count() == before_user_count


def test_bug_report_rejects_non_image_and_oversize_input(bug_report_client) -> None:
    client, _, upload_root = bug_report_client
    non_image = client.post(
        "/api/bug-report",
        data={"screenshot": (BytesIO(b"not an image"), "screen.png"), "page_url": "http://example.test/practice"},
    )
    assert non_image.status_code == 400
    assert "PNG、JPG 或 WebP" in non_image.get_json()["message"]

    oversize = client.post(
        "/api/bug-report",
        data={"screenshot": (BytesIO(b"x" * (10 * 1024 * 1024 + 1)), "screen.png"), "page_url": "http://example.test/practice"},
    )
    assert oversize.status_code == 413
    assert not (upload_root / "bug_reports").exists()


def test_bug_report_widget_is_limited_to_student_answer_templates() -> None:
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    index_template = (root / "templates" / "index.html").read_text(encoding="utf-8")
    adaptive_template = (root / "templates" / "adaptive_practice_v2.html").read_text(encoding="utf-8")
    assert index_template.count("_bug_report_widget.html") == 1
    assert adaptive_template.count("_bug_report_widget.html") == 1
    assert "_bug_report_trigger.html" in index_template
    assert "_bug_report_trigger.html" in adaptive_template
    assert "_bug_report_widget.html" not in (root / "templates" / "dashboard.html").read_text(encoding="utf-8")


def test_bug_report_widget_supports_clipboard_and_photo_picker_with_one_state() -> None:
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    widget = (root / "templates" / "_bug_report_widget.html").read_text(encoding="utf-8")

    assert 'id="bug-report-photo-input" type="file"' in widget
    assert 'accept="image/png,image/jpeg,image/webp"' in widget
    assert 'capture=' not in widget
    assert 'hidden' in widget.split('id="bug-report-photo-input"')[1].split('>')[0]
    assert "📷 從照片選擇" in widget
    assert "選擇檔案" not in widget
    assert "<img" not in widget
    assert "document.addEventListener('paste'" in widget
    assert "photoPickerButton.addEventListener('click', () => photoInput.click())" in widget
    assert "photoInput.addEventListener('change'" in widget
    assert "setScreenshot(file)" in widget
    assert "function setScreenshot(file)" in widget
    assert "maxImageBytes = 10 * 1024 * 1024" in widget
    assert re.search(r'id="bug-report-submit"[^>]*disabled', widget)
    assert "window.location.href" in widget
    assert "剪貼簿中沒有截圖" in widget
    assert "window.requestAnimationFrame(() => panel.focus())" in widget


def test_bug_report_trigger_is_inline_and_endpoint_is_unchanged() -> None:
    root = __import__("pathlib").Path(__file__).resolve().parents[1]
    trigger = (root / "templates" / "_bug_report_trigger.html").read_text(encoding="utf-8")
    widget = (root / "templates" / "_bug_report_widget.html").read_text(encoding="utf-8")
    trigger_rule = re.search(r"\.bug-report-open\s*\{([^}]*)\}", widget)

    assert trigger.count('id="bug-report-open"') == 1
    assert widget.count('id="bug-report-modal"') == 1
    assert trigger_rule is not None
    assert "position:fixed" not in trigger_rule.group(1).replace(" ", "").lower()
    assert "right:" not in trigger_rule.group(1).lower()
    assert "bottom:" not in trigger_rule.group(1).lower()
    assert "box-shadow" not in trigger_rule.group(1).lower()
    assert "fetch('/api/bug-report'" in widget
