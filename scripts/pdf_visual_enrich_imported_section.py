#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PDF visual enrich (local-only, no Gemini)."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PLACEHOLDER_RE = re.compile(r"\[FORMULA_IMAGE_(\d+)\]|\[FORMULA_MISSING\]")
MOJIBAKE_CHARS = "�蝧蝯葫憿箇鞈摨隢貊詨撠"
MOJIBAKE_RE = re.compile("[" + re.escape(MOJIBAKE_CHARS) + r"]")


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    sys.path.insert(0, str(project_root()))
    from config import Config  # pylint: disable=import-outside-toplevel

    return Path(Config.db_path)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def norm_title(text: str) -> str:
    t = str(text or "").strip()
    t = re.sub(r"\s*\[source_type=.*$", "", t)
    t = re.sub(r"\s+", "", t)
    t = t.replace("例題", "例")
    t = t.replace("統測", "統測")
    t = re.sub(r"^例(\d+)$", lambda m: f"例{int(m.group(1))}", t)
    t = re.sub(r"^隨堂練習(\d+)$", lambda m: f"隨堂練習{int(m.group(1))}", t)
    t = re.sub(r"^(\d{2,3})統測([A-Za-z])$", lambda m: f"{m.group(1)}統測{m.group(2).upper()}", t)
    m = re.match(r"^(1-1習題)基礎題(\d+)$", t)
    if m:
        return f"{m.group(1)}基礎題{int(m.group(2))}"
    return t


def build_output_dirs() -> tuple[Path, Path, str]:
    base = (
        project_root()
        / "uploads"
        / "question_assets"
        / "longteng_mathB1"
        / "CH1"
        / "1-1_numberline_absolute_value"
        / "pdf_visual_enrich"
    )
    pages = base / "pages"
    crops = base / "crops"
    pages.mkdir(parents=True, exist_ok=True)
    crops.mkdir(parents=True, exist_ok=True)
    return pages, crops, "ascii_forced"


def render_pages(pdf_path: Path, pages_dir: Path) -> tuple[list[Path], list[str]]:
    import fitz  # pylint: disable=import-outside-toplevel

    doc = fitz.open(str(pdf_path))
    images: list[Path] = []
    texts: list[str] = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        out = pages_dir / f"page_{i+1:03d}.png"
        pix.save(str(out))
        images.append(out)
        texts.append(page.get_text("text") or "")
    doc.close()
    return images, texts


def page_fallback_map_for_b1_11(title_norm: str) -> int | None:
    mapping = {
        "例1": 9,
        "例2": 11,
        "例3": 12,
        "動動手1": 13,
        "動動手2": 13,
        "例4": 15,
        "111統測B": 16,
    }
    if title_norm in mapping:
        return mapping[title_norm]
    m = re.match(r"^1-1習題基礎題(\d+)$", title_norm)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 4:
            return 17
        if 5 <= n <= 10:
            return 18
    return None


def find_page_for_title(target: str, volume: str, section: str) -> tuple[int | None, str]:
    t = norm_title(target)
    if str(volume).strip() == "數學B1" and str(section).strip().startswith("1-1"):
        p = page_fallback_map_for_b1_11(t)
        if p:
            return p, "b1_1-1_fallback_map"
    return None, "locate_failed"


def make_crop(page_img: Path, crops_dir: Path, title_norm: str, page_index: int) -> tuple[str, str, str]:
    from PIL import Image  # pylint: disable=import-outside-toplevel

    try:
        with Image.open(page_img) as img:
            w, h = img.size
            x0, y0, x1, y1 = 0, int(h * 0.12), w, int(h * 0.72)
            reason = "generic_fallback_crop"
            if page_index == 9 and title_norm == "例1":
                x0, y0, x1, y1 = int(w * 0.05), int(h * 0.10), int(w * 0.95), int(h * 0.52)
                reason = "fixed_crop_例1_page9"
            elif page_index == 11 and title_norm == "例2":
                x0, y0, x1, y1 = int(w * 0.05), int(h * 0.35), int(w * 0.95), int(h * 0.82)
                reason = "fixed_crop_例2_page11"
            elif page_index == 18 and title_norm == "1-1習題基礎題5":
                x0, y0, x1, y1 = int(w * 0.05), int(h * 0.08), int(w * 0.95), int(h * 0.48)
                reason = "fixed_crop_基礎題5_page18"
            elif page_index == 16 and title_norm == "111統測B":
                x0, y0, x1, y1 = int(w * 0.05), int(h * 0.20), int(w * 0.95), int(h * 0.72)
                reason = "fixed_crop_111統測B_page16"
            crop = img.crop((x0, y0, x1, y1))
            safe = re.sub(r"[^A-Za-z0-9_-]+", "_", title_norm)
            out = crops_dir / f"{safe}_page_{page_index:03d}.png"
            crop.save(out)
        return "cropped", out.as_posix(), reason
    except Exception as exc:
        return "page_only", page_img.as_posix(), f"crop_failed:{exc}"


def detect_local_ocr_backends() -> dict[str, bool]:
    out = {"pytesseract": False, "tesseract_binary": False, "easyocr": False, "paddleocr": False}
    try:
        import pytesseract  # pylint: disable=import-outside-toplevel

        out["pytesseract"] = True
        try:
            _ = pytesseract.get_tesseract_version()
            out["tesseract_binary"] = True
        except Exception:
            out["tesseract_binary"] = False
    except Exception:
        pass
    try:
        import easyocr  # pylint: disable=unused-import,import-outside-toplevel

        out["easyocr"] = True
    except Exception:
        pass
    try:
        import paddleocr  # pylint: disable=unused-import,import-outside-toplevel

        out["paddleocr"] = True
    except Exception:
        pass
    return out


def detect_formula_ocr_backends() -> dict[str, bool]:
    out = {"torch": False, "pix2tex": False}
    try:
        import torch  # pylint: disable=unused-import,import-outside-toplevel

        out["torch"] = True
    except Exception:
        pass
    try:
        import pix2tex  # pylint: disable=unused-import,import-outside-toplevel

        out["pix2tex"] = True
    except Exception:
        pass
    return out


def choose_backend(name: str, detected: dict[str, bool]) -> str:
    n = str(name or "auto").lower()
    if n in ("tesseract", "pytesseract"):
        return "pytesseract"
    if detected.get("pytesseract") and detected.get("tesseract_binary"):
        return "pytesseract"
    return "none"


OCR_RUNTIME: dict[str, Any] = {"preprocess": "auto", "scale": 3, "dump_variants": False, "psm_list": [6, 7, 11, 13]}


def evaluate_ocr_text_quality(text: str, db_problem_text: str = "", title: str = "") -> dict[str, Any]:
    t = str(text or "").strip()
    math_matches = re.findall(r"[|xX<>=≤≥\-\+\(\)\[\]\\\^_]", t) + re.findall(r"\\frac|\\le|\\ge", t)
    has_math_signal = bool(math_matches)
    mojibake_detected = bool(MOJIBAKE_RE.search(t))
    too_short = len(t) < 6
    pure_digits_or_punct = bool(re.fullmatch(r"[\d\W_]+", t or ""))
    qmark_count = t.count("?")
    mostly_qmark = (qmark_count / max(1, len(t))) > 0.08 or qmark_count >= 3
    noise_ratio = round((sum(1 for c in t if c in "?~`" or c in MOJIBAKE_CHARS)) / max(1, len(t)), 4) if t else 1.0
    before = len(PLACEHOLDER_RE.findall(str(db_problem_text or "")))
    after = len(PLACEHOLDER_RE.findall(t))
    placeholder_reduction = before - after
    solution_like = bool(re.search(r"故|得|解為|所以|答案", t))
    multiline_count = len(re.findall(r"\n", t))
    mixed_multi_problem = bool(multiline_count >= 4 and re.search(r"\(1\)|\(2\)|\d+\.", t))
    math_signal_density = (len(math_matches) / max(1, len(t)))
    too_long_low_math_density = len(t) > 180 and math_signal_density < 0.025

    quality_score = 0.0
    quality_score += 0.35 if has_math_signal else -0.25
    quality_score += 0.20 if placeholder_reduction > 0 else -0.15
    quality_score += -0.45 if mojibake_detected else 0.10
    quality_score += -0.20 if too_short else 0.05
    quality_score += -0.25 if pure_digits_or_punct else 0.05
    quality_score += -0.15 if mostly_qmark else 0.03
    quality_score += -0.12 if solution_like else 0.03
    quality_score += -0.12 if mixed_multi_problem else 0.03
    quality_score += -0.20 if too_long_low_math_density else 0.03

    mostly_garbage = pure_digits_or_punct or mostly_qmark or noise_ratio > 0.04 or too_long_low_math_density
    quality_status = "good" if quality_score >= 0.50 else ("acceptable" if quality_score >= 0.20 else "low_quality")
    if mojibake_detected or too_short or mostly_garbage:
        quality_status = "low_quality"

    return {
        "quality_score": round(quality_score, 4),
        "has_math_signal": has_math_signal,
        "noise_ratio": noise_ratio,
        "mojibake_detected": mojibake_detected,
        "too_short": too_short,
        "mostly_garbage": mostly_garbage,
        "placeholder_reduction": placeholder_reduction,
        "quality_status": quality_status,
    }


def run_formula_ocr_pix2tex(image_path: str, available: bool) -> tuple[str, float, str]:
    if not available:
        return "", 0.0, "pix2tex_unavailable"
    try:
        try:
            from pix2tex.cli import LatexOCR  # type: ignore
        except Exception:
            from pix2tex import LatexOCR  # type: ignore
        from PIL import Image  # pylint: disable=import-outside-toplevel

        model = LatexOCR()
        with Image.open(image_path) as img:
            latex = str(model(img) or "").strip()
        if not latex:
            return "", 0.0, "pix2tex_empty"
        score = 0.55
        if re.search(r"\\frac|\\le|\\ge|\\left|\\right|\^|_", latex):
            score += 0.25
        if re.search(r"[|xX<>=\-\+]", latex):
            score += 0.15
        return latex, min(score, 0.98), "pix2tex_success"
    except Exception as exc:
        return "", 0.0, f"pix2tex_failed:{exc}"


def evaluate_pix2tex_formula_quality(latex: str, expected_context: str | None = None) -> dict[str, Any]:
    s = str(latex or "").strip()
    if not s:
        return {
            "pix2tex_quality_status": "low_quality",
            "pix2tex_hallucination_detected": False,
            "pix2tex_blocked_reason": "pix2tex_empty",
            "pix2tex_usable_as_formula_candidate": False,
        }
    low_context = str(expected_context or "").lower()
    high_risk_tokens = [r"\\Gamma", r"\\partial", r"\\int", r"\\sum", r"\\lim", r"\\mathbf", r"\\mathrm\{inti\}"]
    noisy_patterns = [r"\\begin\{array\}", r"\\qquad\\qquad", r"\\sqrt\{y\|x-y\|\}"]
    too_long = len(s) > 120
    has_core_math = bool(re.search(r"[xX|<>=]|\\le|\\ge", s))
    has_high_risk = any(re.search(p, s) for p in high_risk_tokens)
    has_noisy_pattern = any(re.search(p, s) for p in noisy_patterns)
    b1_11_context = "1-1" in low_context or "絕對值" in low_context
    hallucinated = False
    reason = ""
    if too_long and b1_11_context:
        hallucinated = True
        reason = "pix2tex_too_long_for_context"
    elif has_high_risk and b1_11_context:
        hallucinated = True
        reason = "pix2tex_high_level_symbol_for_b1_1_1"
    elif has_noisy_pattern:
        hallucinated = True
        reason = "pix2tex_noisy_latex_pattern"
    elif b1_11_context and not has_core_math:
        hallucinated = True
        reason = "pix2tex_missing_core_math_signal"
    if hallucinated:
        return {
            "pix2tex_quality_status": "hallucinated",
            "pix2tex_hallucination_detected": True,
            "pix2tex_blocked_reason": reason,
            "pix2tex_usable_as_formula_candidate": False,
        }
    return {
        "pix2tex_quality_status": "good",
        "pix2tex_hallucination_detected": False,
        "pix2tex_blocked_reason": "",
        "pix2tex_usable_as_formula_candidate": True,
    }


def infer_crop_type(crop_status: str, crop_reason: str) -> str:
    if crop_status != "cropped":
        return "page_only"
    if str(crop_reason).startswith("fixed_crop_") or "fallback" in str(crop_reason):
        return "full_question_crop"
    return "formula_crop"


def ocr_local(image_path: str, backend: str, detected: dict[str, bool]) -> tuple[str, float, str, str, list[dict[str, Any]], str, int]:
    def _bonus(text: str) -> float:
        t = str(text or "").strip()
        b = 0.0
        if re.search(r"[|xX<>=≤≥\-\+]", t):
            b += 0.15
        if re.fullmatch(r"\d+", t):
            b -= 0.2
        if not t:
            b -= 0.4
        return b

    if backend != "pytesseract":
        return "", 0.0, "local_ocr_unavailable", backend, [], "", 0
    if not detected.get("pytesseract"):
        return "", 0.0, "local_ocr_unavailable", backend, [], "", 0
    if not detected.get("tesseract_binary"):
        return "", 0.0, "tesseract_binary_missing", backend, [], "", 0

    try:
        import pytesseract  # pylint: disable=import-outside-toplevel
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps  # pylint: disable=import-outside-toplevel

        variants: list[tuple[str, Any]] = []
        with Image.open(image_path) as base:
            rgb = base.convert("RGB")
            variants.append(("original", rgb))
            if OCR_RUNTIME["preprocess"] != "none":
                gray = ImageOps.grayscale(rgb)
                variants.append(("grayscale", gray))
                if OCR_RUNTIME["scale"] >= 2:
                    variants.append(("upscale_2x", gray.resize((gray.width * 2, gray.height * 2), Image.Resampling.LANCZOS)))
                if OCR_RUNTIME["scale"] >= 3:
                    variants.append(("upscale_3x", gray.resize((gray.width * 3, gray.height * 3), Image.Resampling.LANCZOS)))
                variants.append(("threshold_binary", gray.point(lambda p: 255 if p > 170 else 0)))
                variants.append(("adaptive_threshold", ImageOps.autocontrast(gray).point(lambda p: 255 if p > 140 else 0)))
                variants.append(("sharpen", gray.filter(ImageFilter.SHARPEN)))
                variants.append(("high_contrast", ImageEnhance.Contrast(gray).enhance(2.2)))
        if OCR_RUNTIME["dump_variants"]:
            dump_dir = Path(image_path).with_suffix("")
            dump_dir = dump_dir.parent / (dump_dir.name + "_ocr_variants")
            dump_dir.mkdir(parents=True, exist_ok=True)
            for vn, vi in variants:
                try:
                    vi.save(str(dump_dir / f"{vn}.png"))
                except Exception:
                    pass

        results: list[dict[str, Any]] = []
        best = {"score": -999.0, "text": "", "conf": 0.0, "variant": "", "psm": 0}
        for vname, vimg in variants:
            for psm in OCR_RUNTIME["psm_list"]:
                data = pytesseract.image_to_data(
                    vimg, lang="chi_tra+eng", config=f"--psm {int(psm)}", output_type=pytesseract.Output.DICT
                )
                txt = " ".join([str(x).strip() for x in data.get("text", []) if str(x).strip()])
                confs = []
                for c in data.get("conf", []):
                    try:
                        cv = float(c)
                    except Exception:
                        continue
                    if cv >= 0:
                        confs.append(cv / 100.0)
                conf = sum(confs) / max(1, len(confs)) if confs else 0.0
                score = conf + _bonus(txt)
                row = {
                    "variant_name": vname,
                    "psm": int(psm),
                    "text": txt,
                    "confidence": round(conf, 4),
                    "score": round(score, 4),
                }
                results.append(row)
                if score > best["score"]:
                    best = {"score": score, "text": txt, "conf": conf, "variant": vname, "psm": int(psm)}

        status = "success" if best["text"] else "empty"
        return best["text"], float(best["conf"]), status, backend, results, str(best["variant"]), int(best["psm"])
    except Exception as exc:
        return "", 0.0, f"failed:{exc}", backend, [], "", 0


def load_meta(notes: str) -> dict[str, Any]:
    if not str(notes or "").strip():
        return {}
    try:
        obj = json.loads(notes)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def dump_meta(meta: dict[str, Any]) -> str:
    return json.dumps(meta, ensure_ascii=False, sort_keys=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--volume", required=True)
    parser.add_argument("--section", required=True)
    parser.add_argument("--title", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--ocr-mode", default="local_only", choices=["local_only"])
    parser.add_argument("--ocr-backend", default="auto", choices=["auto", "pytesseract"])
    parser.add_argument("--formula-ocr-backend", default="none", choices=["auto", "pix2tex", "none"])
    parser.add_argument("--compare-ocr-backends", action="store_true")
    parser.add_argument("--formula-only", action="store_true")
    parser.add_argument("--ocr-preprocess", default="auto", choices=["auto", "none"])
    parser.add_argument("--ocr-scale", type=int, default=3, choices=[2, 3])
    parser.add_argument("--dump-ocr-variants", action="store_true")
    parser.add_argument("--tesseract-psm", type=int, default=0, choices=[0, 6, 7, 11, 13])
    parser.add_argument("--no-gemini", action="store_true", default=True)
    parser.add_argument("--allow-gemini-fallback", action="store_true")
    parser.add_argument("--confidence-threshold", type=float, default=0.85)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    dry_run = not bool(args.write)
    root = project_root()
    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        pdf_path = root / pdf_path
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = root / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)

    OCR_RUNTIME["preprocess"] = str(args.ocr_preprocess)
    OCR_RUNTIME["scale"] = int(args.ocr_scale)
    OCR_RUNTIME["dump_variants"] = bool(args.dump_ocr_variants)
    OCR_RUNTIME["psm_list"] = [int(args.tesseract_psm)] if int(args.tesseract_psm) in (6, 7, 11, 13) else [6, 7, 11, 13]

    titles = [str(t).strip() for t in args.title if str(t).strip()]
    norm_filters = {norm_title(t) for t in titles}
    pages_dir, crops_dir, path_status = build_output_dirs()
    page_images, _ = render_pages(pdf_path, pages_dir)

    detected = detect_local_ocr_backends()
    formula_detected = detect_formula_ocr_backends()
    backend = choose_backend(args.ocr_backend, detected)

    conn = sqlite3.connect(str(default_db_path()))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, source_description, source_volume, source_section, problem_text, notes, correct_answer, detailed_solution
        FROM textbook_examples
        WHERE source_volume=? AND source_section=?
        ORDER BY id ASC
        """,
        (args.volume, args.section),
    )
    rows = [r for r in cur.fetchall() if (not norm_filters or norm_title(r["source_description"]) in norm_filters)]

    stats = {
        "requested_volume": args.volume,
        "requested_section": args.section,
        "safe_output_dir": pages_dir.parent.as_posix(),
        "path_encoding_status": path_status,
        "rendered_pages": len(page_images),
        "crops_created": 0,
        "local_ocr_requests": 0,
        "local_ocr_success": 0,
        "local_ocr_failed": 0,
        "local_ocr_empty": 0,
        "local_ocr_unavailable": 0,
        "gemini_called": 0,
        "proposed_updates": 0,
        "low_confidence": 0,
        "still_missing_formula": 0,
    }

    lines = [
        "# PDF Visual Enrich Local-only Report",
        f"- requested_volume: `{args.volume}`",
        f"- requested_section: `{args.section}`",
        f"- safe_output_dir: `{pages_dir.parent.as_posix()}`",
        f"- path_encoding_status: `{path_status}`",
        f"- dry_run: `{dry_run}`",
        f"- ocr_mode: `{args.ocr_mode}`",
        f"- ocr_backend_request: `{args.ocr_backend}`",
        f"- formula_ocr_backend_request: `{args.formula_ocr_backend}`",
        f"- compare_ocr_backends: `{bool(args.compare_ocr_backends)}`",
        f"- formula_only: `{bool(args.formula_only)}`",
        f"- local_ocr_backend_selected: `{backend}`",
        "",
    ]

    for r in rows:
        title_raw = str(r["source_description"] or "")
        title_norm = norm_title(title_raw)
        db_text = str(r["problem_text"] or "")
        meta = load_meta(r["notes"])
        if not (PLACEHOLDER_RE.search(db_text) or meta.get("needs_formula_review", False)):
            continue

        mapped_page, mapping_used = find_page_for_title(title_raw, args.volume, args.section)
        page_image_path = ""
        crop_status = "locate_failed"
        crop_path = ""
        crop_reason = "locate_failed"

        local_text = ""
        local_conf = 0.0
        local_status = "not_run"
        local_backend = backend
        variant_results: list[dict[str, Any]] = []
        best_variant, best_psm = "", 0

        pix2tex_latex, pix2tex_score, pix2tex_status = "", 0.0, "not_run"
        pix2tex_quality = {
            "pix2tex_quality_status": "low_quality",
            "pix2tex_hallucination_detected": False,
            "pix2tex_blocked_reason": "not_run",
            "pix2tex_usable_as_formula_candidate": False,
        }
        selected_text_backend, selected_formula_backend = local_backend, "none"
        selected_candidate, selected_candidate_quality = "", 0.0
        final_candidate_source = "none"
        quality = evaluate_ocr_text_quality("", db_text, title_raw)
        action, reason, blocked = "low_confidence", "locate_failed", "locate_failed"

        if mapped_page is not None and 1 <= mapped_page <= len(page_images):
            page_image_path = page_images[mapped_page - 1].as_posix()
            crop_status, crop_path, crop_reason = make_crop(page_images[mapped_page - 1], crops_dir, title_norm, mapped_page)
            crop_type = infer_crop_type(crop_status, crop_reason)
            if crop_status == "cropped":
                stats["crops_created"] += 1
                stats["local_ocr_requests"] += 1
                local_text, local_conf, local_status, local_backend, variant_results, best_variant, best_psm = ocr_local(
                    crop_path, backend, detected
                )

                if local_status == "success":
                    stats["local_ocr_success"] += 1
                elif local_status == "empty":
                    stats["local_ocr_empty"] += 1
                elif local_status in ("local_ocr_unavailable", "tesseract_binary_missing"):
                    stats["local_ocr_unavailable"] += 1
                else:
                    stats["local_ocr_failed"] += 1

                selected_candidate = local_text
                selected_text_backend = local_backend
                final_candidate_source = "pytesseract_text"

                formula_allowed = args.formula_ocr_backend in ("auto", "pix2tex") or bool(args.compare_ocr_backends)
                if formula_allowed:
                    pix2tex_latex, pix2tex_score, pix2tex_status = run_formula_ocr_pix2tex(
                        crop_path, formula_detected.get("pix2tex", False)
                    )
                    pix2tex_quality = evaluate_pix2tex_formula_quality(
                        pix2tex_latex,
                        expected_context=f"{args.volume} {args.section} {title_raw} {db_text[:120]}",
                    )
                    if pix2tex_quality["pix2tex_usable_as_formula_candidate"]:
                        selected_formula_backend = "pix2tex"
                    if args.formula_only and crop_type == "formula_crop" and pix2tex_quality["pix2tex_usable_as_formula_candidate"]:
                        selected_candidate = pix2tex_latex
                        final_candidate_source = "pix2tex_formula_only"

                quality = evaluate_ocr_text_quality(selected_candidate, db_text, title_raw)
                selected_candidate_quality = quality["quality_score"]

                gate_conf = local_conf if final_candidate_source != "pix2tex_formula_only" else pix2tex_score

                if local_status != "success" and final_candidate_source != "pix2tex_formula_only":
                    reason = local_status
                    blocked = local_status
                    stats["low_confidence"] += 1
                elif pix2tex_quality["pix2tex_hallucination_detected"]:
                    reason = "pix2tex_hallucinated"
                    blocked = f"pix2tex_hallucinated:{pix2tex_quality['pix2tex_blocked_reason']}"
                    stats["low_confidence"] += 1
                elif gate_conf < float(args.confidence_threshold):
                    reason = "confidence_below_threshold"
                    blocked = "confidence_below_threshold"
                    stats["low_confidence"] += 1
                elif quality["quality_status"] == "low_quality":
                    reason = "text_quality_low"
                    blocked = "text_quality_low"
                    stats["low_confidence"] += 1
                elif not quality["has_math_signal"]:
                    reason = "missing_math_signal"
                    blocked = "missing_math_signal"
                    stats["low_confidence"] += 1
                elif quality["placeholder_reduction"] <= 0:
                    reason = "no_placeholder_reduction"
                    blocked = "no_placeholder_reduction"
                    stats["low_confidence"] += 1
                elif quality["mojibake_detected"]:
                    reason = "mojibake_detected"
                    blocked = "mojibake_detected"
                    stats["low_confidence"] += 1
                elif PLACEHOLDER_RE.search(selected_candidate):
                    reason = "candidate_still_contains_placeholders"
                    blocked = "candidate_still_contains_placeholders"
                    stats["low_confidence"] += 1
                else:
                    action = "proposed_update"
                    reason = "quality_gate_passed"
                    blocked = ""
                    stats["proposed_updates"] += 1
                    if not dry_run:
                        meta["original_problem_text_before_pdf_visual_enrich"] = db_text
                        meta["pdf_visual_enrich_candidate_text"] = selected_candidate
                        meta["pdf_visual_enrich_confidence"] = gate_conf
                        meta["pdf_visual_enrich_crop_path"] = crop_path
                        meta["pdf_visual_enrich_ocr_backend"] = selected_text_backend
                        meta["pdf_visual_enrich_status"] = "applied"
                        meta["pdf_visual_enrich_updated_at"] = now_iso()
                        cur.execute(
                            "UPDATE textbook_examples SET problem_text=?, notes=? WHERE id=?",
                            (selected_candidate or db_text, dump_meta(meta), int(r["id"])),
                        )
            else:
                stats["low_confidence"] += 1
                reason = "page_only_not_writable"
                blocked = reason
        else:
            crop_type = "page_only"
            stats["low_confidence"] += 1

        db_preview = db_text[:300].replace("`", "'")
        pyt_preview = local_text[:300].replace("`", "'")
        sel_preview = selected_candidate[:300].replace("`", "'")
        lines.extend(
            [
                f"## id={r['id']} {title_raw}",
                f"- db_problem_text: `{db_preview}`",
                f"- mapped_page: `{mapped_page}`",
                f"- page_mapping_used: `{mapping_used}`",
                f"- page_image_path: `{page_image_path}`",
                f"- crop_status: `{crop_status}`",
                f"- crop_type: `{crop_type}`",
                f"- crop_path: `{crop_path}`",
                f"- crop_reason: `{crop_reason}`",
                f"- local_ocr_backend: `{local_backend}`",
                f"- local_ocr_status: `{local_status}`",
                f"- preprocess_variants_count: `{len(variant_results)}`",
                f"- best_preprocess_variant: `{best_variant}`",
                f"- best_tesseract_psm: `{best_psm}`",
                f"- variant_results: `{variant_results}`",
                f"- selected_local_ocr_text: `{sel_preview}`",
                f"- selected_local_ocr_confidence: `{local_conf}`",
                f"- ocr_quality_score: `{quality.get('quality_score')}`",
                f"- ocr_quality_status: `{quality.get('quality_status')}`",
                f"- has_math_signal: `{quality.get('has_math_signal')}`",
                f"- noise_ratio: `{quality.get('noise_ratio')}`",
                f"- mojibake_detected: `{quality.get('mojibake_detected')}`",
                f"- placeholder_reduction: `{quality.get('placeholder_reduction')}`",
                f"- proposed_update_blocked_reason: `{blocked}`",
                f"- pytesseract_text: `{pyt_preview}`",
                f"- pytesseract_confidence: `{local_conf}`",
                f"- pix2tex_available: `{formula_detected.get('pix2tex', False)}`",
                f"- pix2tex_latex: `{pix2tex_latex}`",
                f"- pix2tex_quality_score: `{pix2tex_score}`",
                f"- pix2tex_quality_status: `{pix2tex_quality.get('pix2tex_quality_status')}`",
                f"- pix2tex_hallucination_detected: `{pix2tex_quality.get('pix2tex_hallucination_detected')}`",
                f"- pix2tex_blocked_reason: `{pix2tex_quality.get('pix2tex_blocked_reason')}`",
                f"- pix2tex_usable_as_formula_candidate: `{pix2tex_quality.get('pix2tex_usable_as_formula_candidate')}`",
                f"- selected_text_backend: `{selected_text_backend}`",
                f"- selected_formula_backend: `{selected_formula_backend}`",
                f"- final_candidate_source: `{final_candidate_source}`",
                f"- selected_candidate: `{sel_preview}`",
                f"- selected_candidate_quality: `{selected_candidate_quality}`",
                "- gemini_called: `0`",
                f"- action: `{action}`",
                f"- reason: `{reason}`",
                "",
            ]
        )

    cur.execute(
        "SELECT COUNT(*) AS c FROM textbook_examples WHERE source_volume=? AND source_section=? AND problem_text LIKE '%[FORMULA_%'",
        (args.volume, args.section),
    )
    stats["still_missing_formula"] = int(cur.fetchone()["c"])
    if not dry_run:
        conn.commit()
    conn.close()

    lines.append("## Summary")
    for k in (
        "requested_volume",
        "requested_section",
        "safe_output_dir",
        "path_encoding_status",
        "rendered_pages",
        "crops_created",
        "local_ocr_requests",
        "local_ocr_success",
        "local_ocr_failed",
        "local_ocr_empty",
        "local_ocr_unavailable",
        "gemini_called",
        "proposed_updates",
        "low_confidence",
        "still_missing_formula",
    ):
        lines.append(f"- {k}: `{stats[k]}`")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
