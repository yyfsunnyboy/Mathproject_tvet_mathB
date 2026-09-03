# -*- coding: utf-8 -*-
"""Generic PDF visual enrichment for V3 textbook import.

Authority: paired PDF from the current V3 job + TextbookExample rows after DB_WRITE.
PDF is visual-only (no OCR / pix2tex / formula rebuild / Gemini).

Policy: prefer fewer images over wrong images.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.question_image_assets import (
    build_question_asset_dir,
    build_question_asset_filename,
    question_needs_image,
)
from core.textbook_question_anchor import normalize_question_label

logger = logging.getLogger(__name__)

ASSET_SLOT = "pdf_visual_01"
DEFAULT_DPI = 200
HIGH_CONFIDENCE = 0.90
LOW_CONFIDENCE = 0.75

_STRONG_FIGURE_KEYS = ("如圖", "下圖", "上圖", "右圖", "左圖", "圖中", "附圖", "如下圖", "如上圖")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_pdf_text(text: str) -> str:
    t = unicodedata.normalize("NFKC", str(text or ""))
    t = t.replace("°", "c").replace("˚", "c").replace("º", "c")
    t = t.replace("−", "-").replace("–", "-").replace("—", "-")
    t = t.replace("π", "r")
    # Drop punctuation so DOCX stems match PDF text layer without labels/colons.
    t = re.sub(r"[:：,，.。;；!！?？、\[\]()（）【】「」『』\"']+", "", t)
    t = re.sub(r"\s+", "", t)
    return t


def normalize_query_text(text: str) -> str:
    t = unicodedata.normalize("NFKC", str(text or ""))
    t = re.sub(r"\\\((.*?)\\\)", r"\1", t)
    t = re.sub(r"\\\[(.*?)\\\]", r"\1", t)
    t = re.sub(r"[{}^_\\]", "", t)
    return normalize_pdf_text(t)


def pdf_text_layer_usable(
    pages: list[dict[str, Any]], *, min_chars: int = 50, min_ratio: float = 0.6
) -> bool:
    if not pages:
        return False
    usable = sum(1 for p in pages if int(p.get("char_count") or 0) >= min_chars)
    return (usable / max(1, len(pages))) >= min_ratio


def build_page_index(doc) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    for i, page in enumerate(doc):
        text = page.get_text("text") or ""
        words = page.get_text("words") or []
        images: list[dict[str, Any]] = []
        for info in page.get_images(full=True) or []:
            xref = info[0]
            try:
                rects = page.get_image_rects(xref) or []
            except Exception:
                rects = []
            for rect in rects:
                images.append(
                    {
                        "xref": xref,
                        "bbox": [float(rect.x0), float(rect.y0), float(rect.x1), float(rect.y1)],
                        "area": float(abs((rect.x1 - rect.x0) * (rect.y1 - rect.y0))),
                    }
                )
        drawings: list[dict[str, Any]] = []
        try:
            raw_draws = page.get_drawings() or []
        except Exception:
            raw_draws = []
        for d in raw_draws:
            r = d.get("rect")
            if r is None:
                continue
            x0, y0, x1, y1 = float(r.x0), float(r.y0), float(r.x1), float(r.y1)
            area = abs((x1 - x0) * (y1 - y0))
            if area < 80:
                continue
            drawings.append({"bbox": [x0, y0, x1, y1], "area": area})
        pages.append(
            {
                "page": i + 1,
                "width": float(page.rect.width),
                "height": float(page.rect.height),
                "text": text,
                "norm_text": normalize_pdf_text(text),
                "words": words,
                "images": images,
                "drawings": drawings,
                "char_count": len(text),
            }
        )
    return pages


def intersect_area(a: list[float], b: list[float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return float((x1 - x0) * (y1 - y0))


def union_bbox(boxes: list[list[float]]) -> list[float] | None:
    if not boxes:
        return None
    return [
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    ]


def find_phrase_y(page: dict[str, Any], phrase: str) -> float | None:
    if not phrase:
        return None
    words = page.get("words") or []
    candidates = [phrase]
    for n in (12, 8, 6, 4):
        if len(phrase) > n:
            candidates.append(phrase[:n])
    for target in candidates:
        if not words:
            if target in page.get("norm_text", ""):
                return 0.0
            continue
        for w in words:
            nw = normalize_pdf_text(str(w[4]))
            if target in nw:
                return float(w[1])
        for i in range(len(words)):
            acc = ""
            y0 = float(words[i][1])
            for j in range(i, min(i + 16, len(words))):
                if abs(float(words[j][1]) - y0) > 18:
                    break
                acc += normalize_pdf_text(str(words[j][4]))
                if target in acc:
                    return y0
    return None


def extract_match_phrases(problem_text: str, label: str = "") -> list[str]:
    """Build unique-ish phrases from problem text (and optional label). No section hardcodes."""
    raw = normalize_query_text(problem_text)
    phrases: list[str] = []
    seen: set[str] = set()

    def add(p: str) -> None:
        p = normalize_pdf_text(p)
        if len(p) < 6:
            return
        if p in seen:
            return
        seen.add(p)
        phrases.append(p)

    chunks = re.split(r"[。；;！？\n]", str(problem_text or ""))
    for chunk in chunks:
        n = normalize_query_text(chunk)
        if len(n) >= 8:
            add(n[:24])
        if len(n) >= 12:
            add(n[:16])
        if len(n) >= 6:
            add(n[:12])

    if raw:
        add(raw[:28])
        add(raw[:18])
        add(raw[:12])

    label_n = normalize_pdf_text(normalize_question_label(label))
    if label_n and len(label_n) >= 3:
        add(label_n)
        add(f"【{label_n}】")

    phrases.sort(key=len, reverse=True)
    return phrases[:12]


def _phrase_page_frequency(pages: list[dict[str, Any]], phrase: str) -> int:
    if not phrase:
        return 0
    return sum(1 for p in pages if phrase in (p.get("norm_text") or ""))


def match_questions_to_pdf(
    items: list[dict[str, Any]],
    pages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Match TE/items to PDF via normalized problem-text phrases + source_order continuity."""
    results: list[dict[str, Any]] = []
    last_page = 0
    last_y = -1.0

    for idx, item in enumerate(items):
        label = normalize_question_label(
            str(item.get("source_description") or item.get("title") or "")
        )
        phrases = extract_match_phrases(str(item.get("problem_text") or ""), label)
        usable = []
        for ph in phrases:
            freq = _phrase_page_frequency(pages, ph)
            if freq == 0:
                continue
            if freq > max(2, len(pages) // 3) and len(ph) < 10:
                continue
            usable.append((ph, freq))

        best = None
        for page in pages:
            hits = [ph for ph, _freq in usable if ph in page["norm_text"]]
            if not hits:
                continue
            longest = max(hits, key=len)
            y = find_phrase_y(page, longest)
            if y is None:
                y = 40.0
            score = 0.82
            if len(longest) >= 8:
                score = 0.90
            if len(longest) >= 12:
                score = 0.94
            if len(longest) >= 16:
                score = 0.97
            freq = _phrase_page_frequency(pages, longest)
            if freq == 1:
                score = min(0.99, score + 0.02)
                method = "unique_phrase+order"
            else:
                score = min(score, 0.88)
                method = "shared_phrase+order"
            if last_page and page["page"] < last_page - 1:
                score -= 0.35
            elif last_page and page["page"] == last_page and y + 6 < last_y:
                if y < last_y - 20:
                    score -= 0.12
            if score <= 0:
                continue
            cand = (score, page["page"], float(y), hits[:5], method)
            if best is None or cand[0] > best[0]:
                best = cand
            elif best is not None and cand[0] == best[0]:
                if last_page and abs(cand[1] - last_page) < abs(best[1] - last_page):
                    best = cand

        if best is None:
            results.append(
                {
                    **item,
                    "source_description": label or item.get("source_description"),
                    "pdf_match": None,
                    "match_method": "unmatched",
                    "match_score": 0.0,
                    "needs_review": True,
                    "reason": "no_unique_phrase_hit",
                }
            )
            continue

        score, page_no, y, hits, method = best
        last_page, last_y = page_no, y
        results.append(
            {
                **item,
                "source_description": label or item.get("source_description"),
                "pdf_match": {
                    "page": page_no,
                    "question_start_y": y,
                    "hits": hits,
                },
                "match_method": method,
                "match_score": round(float(score), 3),
                "needs_review": bool(score < LOW_CONFIDENCE),
                "reason": "matched_via_text_layer",
                "source_order": item.get("source_order") or (idx + 1),
            }
        )
    return results


def assign_question_regions(
    matches: list[dict[str, Any]],
    pages: list[dict[str, Any]],
    *,
    x_margin: float = 36.0,
    bottom_margin: float = 36.0,
) -> list[dict[str, Any]]:
    for i, row in enumerate(matches):
        pm = row.get("pdf_match")
        if not pm:
            row["regions"] = []
            row["question_bbox"] = None
            row["cross_page_suspected"] = False
            continue
        page_no = int(pm["page"])
        y0 = float(pm.get("question_start_y") or 0)
        page = pages[page_no - 1]
        y1 = page["height"] - bottom_margin
        cross_page_suspected = False
        next_row = matches[i + 1] if i + 1 < len(matches) else None
        if next_row and next_row.get("pdf_match"):
            np = next_row["pdf_match"]
            if int(np["page"]) == page_no:
                y1 = max(y0 + 36, float(np.get("question_start_y") or y1) - 4)
            elif int(np["page"]) > page_no:
                y1 = page["height"] - bottom_margin
                if int(np["page"]) - page_no >= 2:
                    cross_page_suspected = True
        bbox = [
            x_margin,
            max(0.0, y0 - 8),
            page["width"] - x_margin,
            y1,
        ]
        bbox = [
            max(0.0, min(bbox[0], page["width"])),
            max(0.0, min(bbox[1], page["height"])),
            max(0.0, min(bbox[2], page["width"])),
            max(0.0, min(bbox[3], page["height"])),
        ]
        regions = [{"page": page_no, "bbox": bbox}]
        row["regions"] = regions
        row["question_bbox"] = bbox
        row["cross_page_suspected"] = cross_page_suspected
        pm["question_bbox"] = bbox
        pm["regions"] = regions
    return matches


def _text_has_strong_figure_cue(problem_text: str) -> bool:
    t = str(problem_text or "")
    return any(k in t for k in _STRONG_FIGURE_KEYS)


def classify_and_detect_visuals(
    matches: list[dict[str, Any]],
    pages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Detect visuals and classify: required|helpful|decorative|skipped_low_confidence|none."""
    for row in matches:
        score = float(row.get("match_score") or 0.0)
        regions = row.get("regions") or []
        problem_text = str(row.get("problem_text") or "")
        text_flag = question_needs_image(problem_text)
        strong_cue = _text_has_strong_figure_cue(problem_text)

        row["visual_classification"] = "none"
        row["should_mount"] = False
        row["visual_type"] = None
        row["visual_bbox"] = None
        row["visual_reason"] = "no_visual"

        if not regions or score < HIGH_CONFIDENCE:
            row["visual_classification"] = "skipped_low_confidence"
            row["should_mount"] = False
            row["visual_reason"] = "low_match_confidence" if regions else "unmatched"
            row["needs_review"] = True
            continue

        img_hits: list[dict[str, Any]] = []
        draw_hits: list[dict[str, Any]] = []
        for reg in regions:
            page = pages[reg["page"] - 1]
            qb = reg["bbox"]
            qarea = max(1.0, abs((qb[2] - qb[0]) * (qb[3] - qb[1])))
            for im in page["images"]:
                inter = intersect_area(qb, im["bbox"])
                if inter <= 0:
                    continue
                if im["area"] < 1200:
                    continue
                if inter / max(im["area"], 1) < 0.25 and inter / qarea < 0.02:
                    continue
                img_hits.append({"page": reg["page"], **im, "intersect": inter})
            for d in page["drawings"]:
                inter = intersect_area(qb, d["bbox"])
                if inter <= 0:
                    continue
                if d["area"] < 2500:
                    continue
                if d["area"] > 0.55 * page["width"] * page["height"]:
                    continue
                draw_hits.append({"page": reg["page"], **d, "intersect": inter})

        significant_draws = [
            d
            for d in draw_hits
            if d["area"] >= 15000
            and (d["bbox"][2] - d["bbox"][0]) >= 100
            and (d["bbox"][3] - d["bbox"][1]) >= 70
        ]
        soft_draws = [
            d
            for d in draw_hits
            if d["area"] >= 6000
            and (d["bbox"][2] - d["bbox"][0]) >= 60
            and (d["bbox"][3] - d["bbox"][1]) >= 50
        ]
        significant_imgs: list[dict[str, Any]] = []
        for im in img_hits:
            if im["area"] < 5000:
                continue
            cy = (im["bbox"][1] + im["bbox"][3]) / 2.0
            page_h = pages[im["page"] - 1]["height"]
            if cy < 55 or cy > page_h - 40:
                continue
            for reg in regions:
                if reg["page"] != im["page"]:
                    continue
                qb = reg["bbox"]
                if qb[1] - 10 <= cy <= qb[3] + 10:
                    significant_imgs.append(im)
                    break

        preferred_draws = significant_draws or (soft_draws if (strong_cue or text_flag or significant_imgs) else [])
        visual_bbox = None
        visual_type = None
        classification = "none"
        reason = "text_and_formula_only"
        should_mount = False

        # AI_REFERENCE policy: prefer keeping a usable figure over decorative skips.
        # Accept leftover photo/layout if ownership (high-confidence region) is clear.
        photo_and_diagram = bool(significant_imgs) and bool(significant_draws or soft_draws)

        if strong_cue and (preferred_draws or soft_draws or significant_imgs):
            if preferred_draws or soft_draws:
                top = sorted((preferred_draws or soft_draws), key=lambda d: -d["area"])[:10]
                visual_bbox = union_bbox([d["bbox"] for d in top])
                visual_type = "diagram"
            else:
                visual_bbox = union_bbox([i["bbox"] for i in significant_imgs])
                visual_type = "embedded_image"
            classification = "required"
            reason = "figure_keyword_and_visual_in_region"
            should_mount = True
        elif text_flag and (preferred_draws or soft_draws or significant_imgs):
            if preferred_draws or soft_draws:
                top = sorted((preferred_draws or soft_draws), key=lambda d: -d["area"])[:10]
                visual_bbox = union_bbox([d["bbox"] for d in top])
                visual_type = "diagram"
            else:
                visual_bbox = union_bbox([i["bbox"] for i in significant_imgs])
                visual_type = "embedded_image"
            classification = "helpful"
            reason = "figure_hint_and_visual_in_region"
            should_mount = True
        elif photo_and_diagram:
            draws = significant_draws or soft_draws
            top = sorted(draws, key=lambda d: -d["area"])[:10]
            # Include co-located image so key labels/values in the figure pack remain.
            boxes = [d["bbox"] for d in top] + [i["bbox"] for i in significant_imgs]
            visual_bbox = union_bbox(boxes)
            visual_type = "diagram"
            classification = "helpful"
            reason = "photo_and_diagram_ai_reference"
            should_mount = True
        elif significant_imgs:
            # High-confidence ownership already gated; keep as AI reference even if photo-like.
            visual_bbox = union_bbox([i["bbox"] for i in significant_imgs])
            visual_type = "embedded_image"
            classification = "helpful"
            reason = "embedded_image_ai_reference"
            should_mount = True
        elif preferred_draws or soft_draws:
            # Mount only when soft/significant draws look like a compact figure, not page frames.
            draws = preferred_draws or soft_draws
            compact = [
                d
                for d in draws
                if d["area"] < 0.35 * pages[regions[0]["page"] - 1]["width"] * pages[regions[0]["page"] - 1]["height"]
            ]
            if compact and (strong_cue or text_flag):
                top = sorted(compact, key=lambda d: -d["area"])[:10]
                visual_bbox = union_bbox([d["bbox"] for d in top])
                visual_type = "diagram"
                classification = "helpful"
                reason = "compact_vector_with_figure_cue"
                should_mount = True
            else:
                classification = "none"
                reason = "formula_or_decoration_vectors_only"
                should_mount = False
        elif strong_cue or text_flag:
            classification = "skipped_low_confidence"
            reason = "text_says_figure_but_no_clear_image_or_drawing_cluster"
            should_mount = False
            row["needs_review"] = True
        else:
            classification = "none"
            reason = "text_and_formula_only"
            should_mount = False

        if visual_bbox and regions:
            rb = regions[0]["bbox"]
            inter = intersect_area(visual_bbox, rb)
            varea = max(
                1.0,
                abs((visual_bbox[2] - visual_bbox[0]) * (visual_bbox[3] - visual_bbox[1])),
            )
            if inter < 0.15 * varea:
                clipped = [
                    max(visual_bbox[0], rb[0]),
                    max(visual_bbox[1], rb[1]),
                    min(visual_bbox[2], rb[2]),
                    min(visual_bbox[3], rb[3]),
                ]
                if clipped[2] > clipped[0] + 5 and clipped[3] > clipped[1] + 5:
                    visual_bbox = clipped
                else:
                    should_mount = False
                    classification = "skipped_low_confidence"
                    reason = "visual_bbox_outside_question_region"
                    visual_bbox = None

        row["visual_classification"] = classification
        row["should_mount"] = bool(should_mount and visual_bbox)
        row["visual_type"] = visual_type
        row["visual_bbox"] = visual_bbox
        row["visual_reason"] = reason
        row["visual_page"] = regions[0]["page"] if regions else None
    return matches


def fingerprint_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def crop_pdf_bbox(
    pdf_path: str | Path,
    page_1based: int,
    bbox: list[float],
    dest: str | Path,
    *,
    dpi: int = DEFAULT_DPI,
    pad_pt: float = 4.0,
) -> dict[str, Any]:
    import fitz
    from PIL import Image

    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    try:
        page = doc.load_page(int(page_1based) - 1)
        zoom = float(dpi) / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        x0, y0, x1, y1 = [int(round(v * zoom)) for v in bbox]
        pad = int(round(pad_pt * zoom / 2.5))
        x0 = max(0, x0 - pad)
        y0 = max(0, y0 - pad)
        x1 = min(img.width, x1 + pad)
        y1 = min(img.height, y1 + pad)
        crop = img.crop((x0, y0, x1, y1))
        crop.save(dest_path, format="PNG", optimize=True)
        return {
            "width": crop.width,
            "height": crop.height,
            "file_size": dest_path.stat().st_size,
            "sha256": fingerprint_file(dest_path),
            "dpi": dpi,
        }
    finally:
        doc.close()


def parse_notes_dict(notes: Any) -> dict[str, Any]:
    if notes is None:
        return {}
    if isinstance(notes, dict):
        return dict(notes)
    if not isinstance(notes, str) or not notes.strip():
        return {}
    try:
        parsed = json.loads(notes)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def merge_notes_preserve_image_assets(existing_notes: Any, incoming_notes: Any) -> str:
    """Merge notes JSON; preserve existing image_assets unless incoming provides them."""
    base = parse_notes_dict(existing_notes)
    incoming = parse_notes_dict(incoming_notes)
    merged = dict(base)
    merged.update(incoming)
    inc_assets = incoming.get("image_assets")
    if not isinstance(inc_assets, list) or not inc_assets:
        if isinstance(base.get("image_assets"), list) and base.get("image_assets"):
            merged["image_assets"] = base["image_assets"]
            if "has_image" in base:
                merged["has_image"] = base["has_image"]
    return json.dumps(merged, ensure_ascii=False)


def upsert_notes_image_asset(
    notes: dict[str, Any], asset: dict[str, Any], *, slot: str = ASSET_SLOT
) -> dict[str, Any]:
    assets = notes.get("image_assets")
    if not isinstance(assets, list):
        assets = []
    new_assets: list[dict[str, Any]] = []
    replaced = False
    for a in assets:
        if not isinstance(a, dict):
            continue
        same_slot = a.get("asset_slot") == slot and a.get("source") == "pdf"
        same_path = a.get("path") == asset.get("path")
        if same_slot or same_path:
            new_assets.append(asset)
            replaced = True
        else:
            new_assets.append(a)
    if not replaced:
        new_assets.append(asset)
    notes["image_assets"] = new_assets
    notes["has_image"] = True
    notes["needs_image_review"] = False
    return notes


def build_pdf_visual_asset_record(
    *,
    rel_path: str,
    page_1based: int,
    bbox: list[float],
    classification: str,
    visual_type: str | None,
    match_method: str | None,
    match_score: float | None,
    reason: str,
    image_meta: dict[str, Any],
    anchor_id: str,
    asset_slot: str = ASSET_SLOT,
) -> dict[str, Any]:
    return {
        "asset_type": "pdf_visual_crop",
        "asset_slot": asset_slot,
        "source": "pdf",
        "path": rel_path,
        "display_path": rel_path,
        "page_index": int(page_1based) - 1,
        "source_page": int(page_1based),
        "bbox": list(bbox),
        "needs_crop_review": False,
        "needs_image_conversion": False,
        "reason": reason,
        "image_description": classification,
        "visual_type": visual_type,
        "visual_classification": classification,
        "match_method": match_method,
        "match_score": match_score,
        "question_anchor": anchor_id,
        "width": image_meta.get("width"),
        "height": image_meta.get("height"),
        "file_size": image_meta.get("file_size"),
        "sha256": image_meta.get("sha256"),
        "dpi": image_meta.get("dpi"),
    }


def _example_to_item(row: Any) -> dict[str, Any]:
    notes = parse_notes_dict(getattr(row, "notes", None))
    anchor = notes.get("question_anchor") if isinstance(notes.get("question_anchor"), dict) else {}
    return {
        "id": getattr(row, "id", None),
        "skill_id": getattr(row, "skill_id", None),
        "source_description": getattr(row, "source_description", "") or "",
        "problem_text": getattr(row, "problem_text", "") or "",
        "problem_type": getattr(row, "problem_type", "") or "",
        "source_curriculum": getattr(row, "source_curriculum", "") or "",
        "source_volume": getattr(row, "source_volume", "") or "",
        "source_chapter": getattr(row, "source_chapter", "") or "",
        "source_section": getattr(row, "source_section", "") or "",
        "notes": notes,
        "anchor_id": str(anchor.get("anchor_id") or ""),
        "source_order": anchor.get("source_order"),
        "source_type": anchor.get("source_type") or getattr(row, "problem_type", "") or "",
    }


def enrich_textbook_examples_with_pdf_visuals(
    *,
    pdf_path: str | Path,
    examples: list[Any],
    curriculum_info: dict[str, Any],
    project_root: str | Path | None = None,
    debug_dir: str | Path | None = None,
    write_notes: bool = True,
    dpi: int = DEFAULT_DPI,
) -> dict[str, Any]:
    """Match/detect/crop/link PDF visuals for TextbookExample rows. Non-fatal per question."""
    import fitz

    root = Path(project_root) if project_root else Path.cwd()
    pdf = Path(pdf_path)
    summary: dict[str, Any] = {
        "ok": True,
        "pdf_path": str(pdf),
        "questions_scanned": 0,
        "questions_matched": 0,
        "high_confidence": 0,
        "visual_candidates": 0,
        "mounted": 0,
        "linked_count": 0,
        "reused_count": 0,
        "skipped_decorative": 0,
        "skipped_low_confidence": 0,
        "skipped_none": 0,
        "errors": 0,
        "text_layer_usable": False,
        "rows": [],
        "warnings": [],
    }

    if not pdf.is_file():
        summary["ok"] = False
        summary["warnings"].append("pdf_missing")
        return summary
    if not examples:
        summary["warnings"].append("no_examples")
        return summary

    items = [_example_to_item(r) for r in examples]
    items.sort(key=lambda x: (int(x.get("source_order") or 10**9), int(x.get("id") or 0)))
    summary["questions_scanned"] = len(items)

    try:
        doc = fitz.open(str(pdf))
    except Exception as exc:
        summary["ok"] = False
        summary["warnings"].append(f"pdf_open_failed:{type(exc).__name__}")
        logger.warning("PDF open failed: %s", exc)
        return summary

    try:
        pages = build_page_index(doc)
    finally:
        doc.close()

    summary["text_layer_usable"] = pdf_text_layer_usable(pages)
    if not summary["text_layer_usable"]:
        summary["warnings"].append("pdf_text_layer_unusable")
        return summary

    matched = match_questions_to_pdf(items, pages)
    matched = assign_question_regions(matched, pages)
    matched = classify_and_detect_visuals(matched, pages)

    curriculum = str(curriculum_info.get("curriculum") or "vocational")
    publisher = str(curriculum_info.get("publisher") or "longteng")
    volume = str(curriculum_info.get("volume") or "")
    chapter_title = str(curriculum_info.get("chapter") or "")
    section_title = str(curriculum_info.get("section") or "")
    by_id = {getattr(r, "id", None): r for r in examples}

    for row in matched:
        pub = {
            "id": row.get("id"),
            "source_description": row.get("source_description"),
            "anchor_id": row.get("anchor_id"),
            "match_score": row.get("match_score"),
            "match_method": row.get("match_method"),
            "page": (row.get("pdf_match") or {}).get("page") if row.get("pdf_match") else None,
            "classification": row.get("visual_classification"),
            "should_mount": row.get("should_mount"),
            "visual_reason": row.get("visual_reason"),
            "asset_path": None,
            "status": "scanned",
        }
        score = float(row.get("match_score") or 0.0)
        if row.get("pdf_match"):
            summary["questions_matched"] += 1
        if score >= HIGH_CONFIDENCE:
            summary["high_confidence"] += 1

        classification = str(row.get("visual_classification") or "none")
        if classification in ("required", "helpful") and row.get("should_mount"):
            summary["visual_candidates"] += 1
        elif classification == "decorative":
            summary["skipped_decorative"] += 1
            pub["status"] = "skipped_decorative"
            summary["rows"].append(pub)
            continue
        elif classification == "skipped_low_confidence":
            summary["skipped_low_confidence"] += 1
            pub["status"] = "skipped_low_confidence"
            summary["rows"].append(pub)
            continue
        elif not row.get("should_mount"):
            summary["skipped_none"] += 1
            pub["status"] = "skipped_none"
            summary["rows"].append(pub)
            continue

        te = by_id.get(row.get("id"))
        if te is None:
            summary["errors"] += 1
            pub["status"] = "error"
            pub["error"] = "row_missing"
            summary["rows"].append(pub)
            continue

        notes = parse_notes_dict(getattr(te, "notes", None))
        anchor = notes.get("question_anchor") if isinstance(notes.get("question_anchor"), dict) else {}
        anchor_id = str(anchor.get("anchor_id") or row.get("anchor_id") or "")
        if not anchor_id:
            summary["skipped_low_confidence"] += 1
            pub["status"] = "skipped_missing_anchor"
            summary["rows"].append(pub)
            continue

        label = normalize_question_label(str(row.get("source_description") or ""))
        source_type = str(row.get("source_type") or row.get("problem_type") or "textbook_exercise")
        rel_dir = build_question_asset_dir(curriculum, publisher, volume, chapter_title, section_title)
        filename = build_question_asset_filename(
            source_type=source_type,
            question_title=label,
            question_id_or_dedupe=anchor_id,
            fig_index=1,
            ext="png",
        )
        rel_path = f"{rel_dir}/{filename}".replace("\\", "/")
        abs_path = root / rel_path
        page_no = int(row.get("visual_page") or (row.get("pdf_match") or {}).get("page") or 0)
        bbox = row.get("visual_bbox")
        if not page_no or not bbox:
            summary["errors"] += 1
            pub["status"] = "error"
            pub["error"] = "missing_bbox"
            summary["rows"].append(pub)
            continue

        try:
            reused = abs_path.is_file()
            meta_img = crop_pdf_bbox(pdf, page_no, list(bbox), abs_path, dpi=dpi)
            if reused:
                summary["reused_count"] += 1
            asset = build_pdf_visual_asset_record(
                rel_path=rel_path,
                page_1based=page_no,
                bbox=list(bbox),
                classification=classification,
                visual_type=row.get("visual_type"),
                match_method=row.get("match_method"),
                match_score=row.get("match_score"),
                reason=str(row.get("visual_reason") or ""),
                image_meta=meta_img,
                anchor_id=anchor_id,
            )
            if write_notes:
                notes = upsert_notes_image_asset(notes, asset)
                te.notes = json.dumps(notes, ensure_ascii=False)
            summary["mounted"] += 1
            summary["linked_count"] += 1
            pub["status"] = "mounted"
            pub["asset_path"] = rel_path
            pub["sha256"] = meta_img.get("sha256")
        except Exception as exc:
            summary["errors"] += 1
            pub["status"] = "error"
            pub["error"] = f"{type(exc).__name__}: {exc}"
            logger.warning("PDF visual mount failed id=%s: %s", row.get("id"), exc)
        summary["rows"].append(pub)

    if debug_dir:
        try:
            ddir = Path(debug_dir)
            ddir.mkdir(parents=True, exist_ok=True)
            out = ddir / f"pdf_visual_{_now_iso().replace(':', '')}.json"
            out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
            summary["debug_path"] = str(out)
        except Exception as exc:
            summary["warnings"].append(f"debug_write_failed:{exc}")

    return summary
