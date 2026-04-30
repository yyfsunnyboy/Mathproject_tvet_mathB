import json
import os
import re
import hashlib
import shutil
import subprocess
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

INFER_IMAGE_KEYWORDS = [
    "如圖",
    "下圖",
    "上圖",
    "右圖",
    "左圖",
    "圖中",
    "附圖",
    "棋盤式街道圖",
    "著色樣式",
    "著色",
    "圖形",
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


def safe_slug(text: str, max_len: int = 80) -> str:
    s = str(text or "").strip()
    if not s:
        return "unknown"
    s = re.sub(r'[<>:"/\\|?*]', "", s)
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^0-9A-Za-z_\-\u4e00-\u9fff]", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        return "unknown"
    return s[:max_len]


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


def _chapter_slug(chapter_title: str | None) -> str:
    t = str(chapter_title or "").strip()
    if not t:
        return "chapter_unknown"
    n = re.search(r"第?\s*(\d+)\s*章|^\s*(\d+)\b", t)
    num = None
    if n:
        num = n.group(1) or n.group(2)
    if num:
        name = re.sub(r"第?\s*\d+\s*章?", "", t).strip()
        slug_name = safe_slug(name) if name else "unknown"
        return f"ch{int(num):02d}_{slug_name}"
    return f"ch_unknown_{safe_slug(t)}"


def _section_slug(section_title: str | None) -> str:
    t = str(section_title or "").strip()
    if not t:
        return "section_unknown"
    m = re.search(r"(\d+\s*-\s*\d+)", t)
    if m:
        sec_no = m.group(1).replace(" ", "")
        rest = t.replace(m.group(1), "").strip()
        rest_slug = safe_slug(rest) if rest else "unknown"
        return f"sec_{sec_no}_{rest_slug}"
    return f"sec_unknown_{safe_slug(t)}"


def build_question_asset_dir(
    curriculum: str,
    publisher: str,
    volume: str,
    chapter_title: str | None,
    section_title: str | None,
    source_filename: str | None = None,
) -> str:
    _ = source_filename
    curriculum_slug = safe_slug(curriculum or "unknown")
    publisher_slug = safe_slug(publisher or "unknown")
    volume_slug = safe_slug(volume or "unknown")
    ch_slug = _chapter_slug(chapter_title)
    sec_slug = _section_slug(section_title)
    return os.path.join(
        "uploads",
        "question_assets",
        curriculum_slug,
        publisher_slug,
        volume_slug,
        ch_slug,
        sec_slug,
    ).replace("\\", "/")


def build_question_assets_dir(curriculum_info, chapter_title, section_title):
    curriculum = curriculum_info.get("curriculum", "unknown")
    publisher = curriculum_info.get("publisher", "unknown")
    volume = curriculum_info.get("volume", "unknown")
    chapter_id = _chapter_id(chapter_title)
    section_id = _section_id(section_title)
    rel_dir = build_question_asset_dir(curriculum, publisher, volume, chapter_title, section_title)
    abs_dir = os.path.join(current_app.root_path, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)
    return rel_dir, abs_dir, chapter_id, section_id


def build_question_code(chapter_id, section_id, kind, index):
    return f"{chapter_id}_{section_id}_{kind}_{index}"


def build_question_asset_filename(
    source_type: str,
    question_title: str,
    question_id_or_dedupe: str | None,
    fig_index: int,
    ext: str,
) -> str:
    st = safe_slug(source_type or "textbook_practice")
    qtitle = safe_slug(question_title or "untitled")
    qhash = safe_slug(question_id_or_dedupe or "unknown", max_len=16)[:8] or "unknown"
    ex = str(ext or "").lower().lstrip(".")
    ex = ex or "bin"
    return f"{st}_{qtitle}_{qhash}_fig{int(fig_index)}.{ex}"


def convert_vector_image_to_png(input_path, output_path) -> tuple[bool, str | None]:
    tools = [
        ("soffice", ["soffice", "--headless", "--convert-to", "png", "--outdir", os.path.dirname(output_path), input_path]),
        ("magick", ["magick", input_path, output_path]),
        ("inkscape", ["inkscape", input_path, "--export-type=png", f"--export-filename={output_path}"]),
    ]
    for cmd, argv in tools:
        if shutil.which(cmd) is None:
            continue
        try:
            subprocess.run(argv, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if cmd == "soffice":
                base = os.path.splitext(os.path.basename(input_path))[0] + ".png"
                produced = os.path.join(os.path.dirname(output_path), base)
                if os.path.exists(produced) and produced != output_path:
                    shutil.move(produced, output_path)
            if os.path.exists(output_path):
                return True, None
        except Exception as e:
            last = str(e)
    return False, locals().get("last", "no_converter_available")


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


def _extract_explicit_source_page(item: dict) -> int | None:
    source_page = item.get("source_page")
    if source_page is not None:
        try:
            return int(source_page)
        except Exception:
            return None
    page_index = item.get("page_index")
    if page_index is not None:
        try:
            return int(page_index) + 1
        except Exception:
            return None
    return None


def _to_page_map(extracted_pages: list | dict) -> dict[int, str]:
    page_map: dict[int, str] = {}
    if isinstance(extracted_pages, dict):
        for k, v in extracted_pages.items():
            try:
                page_map[int(k)] = str(v or "")
            except Exception:
                continue
        return page_map
    if isinstance(extracted_pages, list):
        for idx, text in enumerate(extracted_pages, start=1):
            page_map[idx] = str(text or "")
    return page_map


def infer_source_page_for_question(
    item: dict,
    extracted_pages: list,
    section_title: str | None = None,
    concept_name: str | None = None,
) -> tuple[int | None, str]:
    if not isinstance(item, dict):
        return None, "missing_source_page"

    explicit = _extract_explicit_source_page(item)
    if explicit is not None:
        return explicit, "explicit_source_page"

    page_map = _to_page_map(extracted_pages)
    if not page_map:
        return None, "missing_source_page"

    title = str(item.get("source_description") or item.get("practice_title") or item.get("example_title") or item.get("title") or "").strip()
    problem_text = str(item.get("problem_text") or item.get("problem") or item.get("question") or "").strip()
    image_description = str(item.get("image_description") or "").strip()

    snippets = []
    for source in (problem_text, title):
        if not source:
            continue
        for ln in re.split(r"[\n。；;]", source):
            s = ln.strip()
            if len(s) >= 6:
                snippets.append(s[:30])
        if source and len(source) >= 6:
            snippets.append(source[:40])
    for snip in snippets:
        for pno, ptxt in page_map.items():
            if snip and snip in ptxt:
                return pno, "matched_problem_text"

    if bool(item.get("has_image")) and image_description:
        for key in [image_description] + INFER_IMAGE_KEYWORDS:
            if not key:
                continue
            for pno, ptxt in page_map.items():
                if key in ptxt:
                    return pno, "matched_image_description"

    combined = f"{title}\n{problem_text}"
    if any(k in combined for k in INFER_IMAGE_KEYWORDS):
        for key in INFER_IMAGE_KEYWORDS:
            if key in combined:
                for pno, ptxt in page_map.items():
                    if key in ptxt:
                        return pno, "matched_image_keywords"

    neighbor_pages = item.get("_neighbor_source_pages")
    if isinstance(neighbor_pages, list):
        valid = []
        for x in neighbor_pages:
            try:
                valid.append(int(x))
            except Exception:
                continue
        if valid:
            return sorted(valid)[0], "neighbor_source_page"

    return None, "missing_source_page"


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
