"""Minimal screenshot-only bug report intake for authenticated students."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path

from flask import current_app, jsonify, request
from flask_login import current_user, login_required
from PIL import Image, UnidentifiedImageError

from config import Config
from . import core_bp


MAX_BUG_REPORT_IMAGE_BYTES = 10 * 1024 * 1024
_IMAGE_EXTENSIONS = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp"}


def _bug_report_basename(directory: Path, user_id: int) -> str:
    stem = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_u{user_id}"
    suffix = 0
    while any(directory.glob(f"{stem}{'' if suffix == 0 else f'_{suffix:02d}'}.*")):
        suffix += 1
    return f"{stem}{'' if suffix == 0 else f'_{suffix:02d}'}"


@core_bp.route("/api/bug-report", methods=["POST"])
@login_required
def submit_bug_report():
    screenshot = request.files.get("screenshot")
    if screenshot is None or not screenshot.filename:
        return jsonify({"success": False, "message": "請先選擇截圖。"}), 400

    image_bytes = screenshot.read(MAX_BUG_REPORT_IMAGE_BYTES + 1)
    if not image_bytes:
        return jsonify({"success": False, "message": "請先選擇截圖。"}), 400
    if len(image_bytes) > MAX_BUG_REPORT_IMAGE_BYTES:
        return jsonify({"success": False, "message": "截圖不得超過 10 MB。"}), 413

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image.verify()
            extension = _IMAGE_EXTENSIONS.get(str(image.format or "").upper())
    except (UnidentifiedImageError, OSError, ValueError):
        extension = None
    if extension is None:
        return jsonify({"success": False, "message": "只接受 PNG、JPG 或 WebP 圖片。"}), 400

    page_url = request.form.get("page_url")
    if not isinstance(page_url, str) or not page_url:
        return jsonify({"success": False, "message": "缺少頁面網址。"}), 400

    upload_root = Path(current_app.config.get("UPLOAD_FOLDER") or Config.UPLOAD_FOLDER)
    report_dir = upload_root / "bug_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    basename = _bug_report_basename(report_dir, int(current_user.id))
    image_path = report_dir / f"{basename}.{extension}"
    sidecar_path = report_dir / f"{basename}.txt"
    image_path.write_bytes(image_bytes)
    sidecar_path.write_text(f"page_url={page_url}\n", encoding="utf-8")

    return jsonify({"success": True})
