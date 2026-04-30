import json
import os
import re
from typing import Any

from flask import current_app


STRONG_IMAGE_KEYWORDS = [
    "如圖",
    "下圖",
    "上圖",
    "右圖",
    "左圖",
    "圖中",
    "如右圖",
    "如左圖",
    "如下圖",
    "如上圖",
    "附圖",
]

WEAK_IMAGE_KEYWORDS = [
    "樹狀圖",
    "表格",
    "圓環",
    "著色",
    "路線圖",
    "幾何圖",
    "坐標圖",
]

def question_needs_image(question_text: str, ai_has_image: bool = False) -> bool:
    text = str(question_text or "").strip()
    if not text:
        return False
    if any(k in text for k in STRONG_IMAGE_KEYWORDS):
        return True
    if any(k in text for k in WEAK_IMAGE_KEYWORDS):
        return True
    if ai_has_image and re.search(r"圖\s*\d+|圖[一二三四五六七八九十]|\bfig\.?\s*\d+", text, flags=re.IGNORECASE):
        return True
    if ai_has_image and "圖" in text:
        return True
    if "圖形如下" in text:
        return True
    return False


def detect_image_reason(question_text: str) -> str:
    text = str(question_text or "").strip()
    for k in STRONG_IMAGE_KEYWORDS + WEAK_IMAGE_KEYWORDS:
        if k in text:
            return f"contains {k}"
    return "contains image-related keyword"


def render_pdf_page_to_image(pdf_path, page_index, output_path, dpi=200):
    import fitz

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = fitz.open(pdf_path)
    try:
        page = doc.load_page(int(page_index))
        zoom = float(dpi) / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pix.save(output_path)
    finally:
        doc.close()
    return output_path


def _slug_component(value: Any, default: str = "unknown") -> str:
    text = str(value or "").strip()
    if not text:
        return default
    text = text.replace("\\", "_").replace("/", "_")
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^0-9A-Za-z_\-\u4e00-\u9fff]", "", text)
    return text or default


def _chapter_id(chapter_title: str) -> str:
    m = re.search(r"(\d+)", str(chapter_title or ""))
    if m:
        return f"CH{m.group(1)}"
    return _slug_component(chapter_title, default="CHX")


def _section_id(section_title: str) -> str:
    m = re.search(r"(\d+\s*-\s*\d+)", str(section_title or ""))
    if m:
        return m.group(1).replace(" ", "")
    return _slug_component(section_title, default="section")


def build_question_assets_dir(curriculum_info, chapter_title, section_title):
    curriculum = _slug_component(curriculum_info.get("curriculum", "unknown"))
    publisher = _slug_component(curriculum_info.get("publisher", "unknown"))
    volume = _slug_component(curriculum_info.get("volume", "unknown"))
    chapter_id = _chapter_id(chapter_title)
    section_id = _section_id(section_title)
    rel_dir = os.path.join(
        "uploads",
        "question_assets",
        f"{curriculum}_{publisher}_{volume}",
        chapter_id,
        section_id,
    )
    abs_dir = os.path.join(current_app.root_path, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)
    return rel_dir, abs_dir, chapter_id, section_id


def build_question_code(chapter_id, section_id, kind, index):
    return f"{chapter_id}_{section_id}_{kind}_{index}"


def find_best_page_index(content_by_page, question_text):
    if not isinstance(content_by_page, dict):
        return None
    q = str(question_text or "").strip()
    if not q:
        return None
    lines = [ln.strip() for ln in q.splitlines() if ln.strip()]
    token = lines[0] if lines else q
    token = token[:40]
    for page_no, text in content_by_page.items():
        if token and token in str(text or ""):
            return int(page_no)
    return None


def make_page_image_asset(
    *,
    reason,
    rel_image_path,
    page_index,
):
    return {
        "asset_type": "page_image",
        "path": rel_image_path.replace("\\", "/"),
        "page_index": page_index,
        "source_page": None,
        "bbox": None,
        "needs_crop_review": True,
        "reason": reason,
        "image_description": "",
    }


def attach_image_metadata(record, metadata):
    if not isinstance(metadata, dict):
        return False
    for field in ("metadata_json", "extra_json", "notes", "remarks"):
        if not hasattr(record, field):
            continue
        existing_raw = getattr(record, field, None)
        existing = {}
        if isinstance(existing_raw, str) and existing_raw.strip():
            try:
                existing = json.loads(existing_raw)
            except Exception:
                existing = {"raw": existing_raw}
        merged = dict(existing)
        merged.update(metadata)
        setattr(record, field, json.dumps(merged, ensure_ascii=False))
        return True
    return False
