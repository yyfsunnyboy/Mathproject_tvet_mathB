#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DOCX formula asset pix2tex backfill with section-level pool selection."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PLACEHOLDER_RE = re.compile(r"\[FORMULA_IMAGE_\d+\]|\[FORMULA_MISSING\]")
FORMULA_IMAGE_RE = re.compile(r"\[FORMULA_IMAGE_(\d+)\]")
MOJIBAKE_CHARS = "�蝧蝯葫憿箇鞈摨隢貊詨撠銋嚗暺"
MOJIBAKE_RE = re.compile("[" + re.escape(MOJIBAKE_CHARS) + r"]")
SAFE_TITLE_PATTERNS = [
    re.compile(r"^例題?\d+$"),
    re.compile(r"^隨堂練習\d+$"),
    re.compile(r"^1-1習題\s*基礎題\d+$"),
    re.compile(r"^動動手\d+$"),
    re.compile(r"^111統測B$"),
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    sys.path.insert(0, str(project_root()))
    from config import Config  # pylint: disable=import-outside-toplevel

    return Path(Config.db_path)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_title(raw: str) -> str:
    t = str(raw or "").strip()
    t = re.sub(r"\s*\[source_type=.*$", "", t)
    t = re.sub(r"\s+", "", t)
    t = t.replace("例題", "例")
    t = re.sub(r"^例(\d+)$", lambda m: f"例{int(m.group(1))}", t)
    t = re.sub(r"^隨堂練習(\d+)$", lambda m: f"隨堂練習{int(m.group(1))}", t)
    t = re.sub(r"^1-1習題基礎題(\d+)$", lambda m: f"1-1習題基礎題{int(m.group(1))}", t)
    t = re.sub(r"^(\d{2,3})統測([A-Za-z])$", lambda m: f"{m.group(1)}統測{m.group(2).upper()}", t)
    return t

def normalize_safe_title(raw: str) -> str:
    t = str(raw or "").strip()
    t = re.sub(r"\s*\[source_type=.*$", "", t)
    t = re.sub(r"\s+", "", t)
    t = t.replace("例題", "例")
    t = re.sub(r"^隨堂練習(\d+)$", lambda m: f"隨堂練習{int(m.group(1))}", t)
    t = re.sub(r"^例(\d+)$", lambda m: f"例{int(m.group(1))}", t)
    t = re.sub(r"^1-1習題基礎題(\d+)$", lambda m: f"1-1習題 基礎題{int(m.group(1))}", t)
    t = re.sub(r"^(111)統測([A-Za-z])$", lambda m: f"{m.group(1)}統測{m.group(2).upper()}", t)
    return t

def is_safe_cli_title(title: str) -> bool:
    t = str(title or "").strip()
    if not t:
        return False
    if detect_mojibake_text(t).get("mojibake_detected", False):
        return False
    if any(0xE000 <= ord(ch) <= 0xF8FF for ch in t):
        return False
    return any(p.match(t) for p in SAFE_TITLE_PATTERNS)


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


def parse_placeholders(problem_text: str) -> list[str]:
    return [m.group(0) for m in PLACEHOLDER_RE.finditer(str(problem_text or ""))]


def detect_mojibake_text(text: str) -> dict[str, Any]:
    t = str(text or "")
    patterns: list[str] = []
    score = 0.0
    if not t:
        return {"mojibake_detected": False, "mojibake_score": 0.0, "matched_patterns": [], "reason": ""}
    if MOJIBAKE_RE.search(t):
        patterns.append("known_mojibake_chars")
        score += 0.7
    q_ratio = t.count("?") / max(1, len(t))
    if q_ratio > 0.04 or t.count("?") >= 3:
        patterns.append("high_question_mark_noise")
        score += 0.3
    if any(0xE000 <= ord(ch) <= 0xF8FF for ch in t):
        patterns.append("private_use_unicode")
        score += 0.5
    if re.search(r"\?[\u4e00-\u9fff]|\u4e00-\u9fff\?", t):
        patterns.append("mixed_question_cjk")
        score += 0.2
    detected = score >= 0.7
    reason = ",".join(patterns) if detected else ""
    return {
        "mojibake_detected": bool(detected),
        "mojibake_score": round(min(score, 1.0), 4),
        "matched_patterns": patterns,
        "reason": reason,
    }


def clean_b1_11_text(text: str) -> str:
    t = str(text or "")
    t = t.replace("試求 x 之 x 值", "試求 x 之值")
    t = t.replace("試求 x 之 x值", "試求 x 之值")
    return t


def pick_readable_asset_path(asset: dict[str, Any], root: Path) -> tuple[str | None, str]:
    for key in ("converted_path", "display_path", "path", "original_path"):
        rel = str(asset.get(key) or "").strip()
        if not rel:
            continue
        ext = os.path.splitext(rel)[1].lower()
        if ext in (".png", ".jpg", ".jpeg"):
            ap = Path(rel) if os.path.isabs(rel) else root / rel
            if ap.exists():
                return ap.as_posix(), ""
    return None, "readable_asset_not_found"


def run_pix2tex(image_path: str) -> tuple[str, float, str]:
    try:
        try:
            from pix2tex.cli import LatexOCR  # type: ignore
        except Exception:
            from pix2tex import LatexOCR  # type: ignore
        from PIL import Image  # pylint: disable=import-outside-toplevel

        model = LatexOCR()
        with Image.open(image_path) as img:
            out = str(model(img) or "").strip()
        if not out:
            return "", 0.0, "pix2tex_empty"
        score = 0.55
        if re.search(r"\|x\|", out):
            score += 0.25
        if re.search(r"<|>|=|\\le|\\ge|≤|≥", out):
            score += 0.10
        return out, min(score, 0.99), "pix2tex_success"
    except Exception as exc:
        return "", 0.0, f"pix2tex_failed:{exc}"


def normalize_latex(s: str) -> str:
    t = str(s or "").strip()
    t = t.replace("$", "")
    t = t.replace("\\left", "").replace("\\right", "")
    t = re.sub(r"\s+", "", t)
    t = t.replace("\\leq", "\\le").replace("\\geq", "\\ge")
    return t


def debug_cache_b1_11(filename: str, volume: str, section: str) -> dict[str, str] | None:
    if volume != "數學B1" or section != "1-1 數線與絕對值":
        return None
    key = filename.lower()
    m_id = re.search(r"(image\d+\.(?:png|jpg|jpeg))", key)
    if m_id:
        key = m_id.group(1)
    m = {
        "image80.png": {"normalized_latex": "|x|", "classification": "formula_abs_x"},
        "image76.png": {"normalized_latex": "(b,a)", "classification": "formula_coordinate_pair"},
        "image46.png": {"normalized_latex": "\\frac{b}{c}", "classification": "formula_fraction"},
        "image45.png": {"normalized_latex": "\\frac{a}{c}", "classification": "formula_fraction"},
        "image1.png": {"normalized_latex": "", "classification": "diagram_or_picture"},
    }
    return m.get(key)


def classify_asset(filename: str, normalized_latex: str, width: int, height: int, volume: str, section: str) -> tuple[str, str]:
    cached = debug_cache_b1_11(filename, volume, section)
    if cached:
        return cached["classification"], cached["normalized_latex"]

    nl = normalized_latex
    if width >= 900 and height >= 600:
        return "diagram_or_picture", nl
    if "|x|" in nl:
        return "formula_abs_x", nl
    if re.fullmatch(r"\([^\)]+,[^\)]+\)", nl):
        return "formula_coordinate_pair", nl
    if "\\frac" in nl or re.search(r"^[ab]/c$", nl):
        return "formula_fraction", nl
    if not nl:
        return "unknown_formula", nl
    return "unknown_formula", nl


def expected_classes_for_record(title_norm: str, problem_text: str, placeholders: list[str]) -> dict[str, str]:
    expected: dict[str, str] = {}
    for tk in placeholders:
        if tk == "[FORMULA_MISSING]":
            expected[tk] = "missing_skip"
            continue
        if title_norm in ("例1", "例2"):
            expected[tk] = "formula_abs_x"
            continue
        if title_norm == "1-1習題基礎題5":
            expected[tk] = "full_absolute_value_inequality"
            continue
        idx = problem_text.find(tk)
        tail = problem_text[idx + len(tk) : idx + len(tk) + 12] if idx >= 0 else ""
        if re.search(r"\s*(=|<|>|≤|≥)", tail):
            expected[tk] = "formula_abs_x"
        else:
            expected[tk] = "unknown"
    return expected


def load_section_formula_asset_pool(rows: list[sqlite3.Row], root: Path, volume: str, section: str) -> list[dict[str, Any]]:
    seen = set()
    pool: list[dict[str, Any]] = []
    for r in rows:
        rid = int(r["id"])
        title = str(r["source_description"] or "")
        meta = load_meta(str(r["notes"] or ""))
        assets = meta.get("formula_assets", []) if isinstance(meta, dict) else []
        if not isinstance(assets, list):
            continue
        for a in assets:
            if not isinstance(a, dict):
                continue
            ap, _ = pick_readable_asset_path(a, root)
            if not ap:
                continue
            fn = Path(ap).name
            k = (str(a.get("asset_hash") or ""), fn.lower(), ap.lower())
            if k in seen:
                continue
            seen.add(k)
            width, height = 0, 0
            try:
                from PIL import Image  # pylint: disable=import-outside-toplevel

                with Image.open(ap) as img:
                    width, height = img.size
            except Exception:
                pass

            pix_latex, pix_conf, pix_status = run_pix2tex(ap)
            normalized = normalize_latex(pix_latex)
            cls, normalized_final = classify_asset(fn, normalized, width, height, volume, section)
            pool.append(
                {
                    "asset_path": ap,
                    "source_record_id": rid,
                    "source_title": title,
                    "filename": fn,
                    "width": width,
                    "height": height,
                    "image_type": Path(ap).suffix.lower().lstrip("."),
                    "simple_visual_class": cls,
                    "pix2tex_latex": pix_latex,
                    "normalized_latex": normalized_final,
                    "classification": cls,
                    "pix2tex_status": pix_status,
                    "pix2tex_confidence": pix_conf,
                    "placeholder_token": str(a.get("placeholder_token") or ""),
                    "placeholder_index": int(a.get("placeholder_index") or 0),
                }
            )
    return pool


def choose_replacement(token: str, expected_class: str, rec_id: int, pool: list[dict[str, Any]], used: set[str]) -> tuple[str, dict[str, Any] | None, list[dict[str, str]]]:
    rejected: list[dict[str, str]] = []
    candidates = []
    for a in pool:
        fn = str(a.get("filename") or "")
        cls = str(a.get("classification") or "unknown_formula")
        nl = str(a.get("normalized_latex") or "")
        if detect_mojibake_text(fn).get("mojibake_detected", False):
            rejected.append({"filename": fn, "class": cls, "reason": "asset_filename_mojibake"})
            continue
        if fn in used:
            rejected.append({"filename": fn, "class": cls, "reason": "already_used"})
            continue
        if cls == "diagram_or_picture":
            rejected.append({"filename": fn, "class": cls, "reason": "diagram_not_allowed"})
            continue
        if expected_class == "formula_abs_x":
            if cls != "formula_abs_x":
                rejected.append({"filename": fn, "class": cls, "reason": "class_mismatch"})
                continue
            candidates.append(a)
            continue
        if expected_class == "full_absolute_value_inequality":
            if cls != "unknown_formula":
                rejected.append({"filename": fn, "class": cls, "reason": "need_full_inequality"})
                continue
            if not ("|" in nl and re.search(r"<|>|=|\\le|\\ge|≤|≥", nl)):
                rejected.append({"filename": fn, "class": cls, "reason": "not_full_abs_inequality"})
                continue
            candidates.append(a)
            continue
        rejected.append({"filename": fn, "class": cls, "reason": "unsupported_expected_class"})

    if expected_class == "full_absolute_value_inequality":
        # safety: do not auto-fill this class unless explicit full inequality found; else no replacement
        candidates = [c for c in candidates if len(str(c.get("normalized_latex") or "")) >= 6]

    if not candidates:
        return "", None, rejected

    candidates.sort(key=lambda x: (x.get("source_record_id") != rec_id, -float(x.get("pix2tex_confidence") or 0.0)))
    sel = candidates[0]
    used.add(str(sel.get("filename") or ""))
    return str(sel.get("normalized_latex") or ""), sel, rejected


def _extract_backticked_value(line: str, key: str) -> str:
    m = re.match(rf"^- {re.escape(key)}:\s*`(.*)`\s*$", line.strip())
    return str(m.group(1)) if m else ""


def _extract_relaxed_field_value(line: str, key: str) -> str:
    s = str(line or "").strip()
    prefix = f"- {key}:"
    if not s.startswith(prefix):
        return ""
    v = s[len(prefix) :].strip()
    if v.startswith("`"):
        v = v[1:]
    if v.endswith("`"):
        v = v[:-1]
    return v.strip()


def _parse_safe_candidate_line(line: str) -> dict[str, Any] | None:
    s = str(line or "").strip()
    if not s.startswith("- id="):
        return None
    parts = [p.strip() for p in s[2:].split("|")]
    out: dict[str, Any] = {}
    for p in parts:
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        key = str(k or "").strip()
        val = str(v or "").strip()
        if val.startswith("`") and val.endswith("`"):
            val = val[1:-1]
        out[key] = val
    if "id" not in out:
        return None
    try:
        out["id"] = int(str(out.get("id") or "0"))
    except Exception:
        return None
    try:
        lit = ast.literal_eval(str(out.get("selected_replacements") or "{}"))
        if isinstance(lit, dict):
            out["selected_replacements"] = {str(k): str(v) for k, v in lit.items()}
        else:
            out["selected_replacements"] = {}
    except Exception:
        out["selected_replacements"] = {}
    return out


def parse_candidates_from_report(report_path: Path) -> tuple[list[dict[str, Any]], str]:
    try:
        text = report_path.read_text(encoding="utf-8")
    except Exception as exc:
        return [], f"report_read_failed:{exc}"
    if not text.strip():
        return [], "report_empty"

    records: list[dict[str, Any]] = []
    by_id: dict[int, dict[str, Any]] = {}
    in_safe_candidates = False
    current: dict[str, Any] | None = None
    for raw in text.splitlines():
        line = str(raw or "").rstrip()
        if line.strip() == "## Safe Write Candidates":
            in_safe_candidates = True
            continue
        if line.strip().startswith("## ") and line.strip() != "## Safe Write Candidates":
            in_safe_candidates = False

        if in_safe_candidates:
            c = _parse_safe_candidate_line(line)
            if c:
                cid = int(c["id"])
                base = by_id.get(cid, {"id": cid})
                base["source_description"] = str(c.get("source_description") or base.get("source_description") or "")
                base["action"] = str(c.get("action") or base.get("action") or "")
                base["write_recommendation"] = str(c.get("write_recommendation") or base.get("write_recommendation") or "")
                base["selected_replacements"] = c.get("selected_replacements") or base.get("selected_replacements") or {}
                base.setdefault("proposed_problem_text", "")
                by_id[cid] = base
            continue

        m_head = re.match(r"^## id=(\d+)\s+(.*)$", line)
        if m_head:
            if current:
                records.append(current)
            current = {
                "id": int(m_head.group(1)),
                "source_description": m_head.group(2).strip(),
                "action": "",
                "write_recommendation": "",
                "selected_replacements": {},
                "proposed_problem_text": "",
            }
            continue
        if not current:
            continue
        v = _extract_backticked_value(line, "action")
        if v:
            current["action"] = v
            continue
        v = _extract_backticked_value(line, "write_recommendation")
        if v:
            current["write_recommendation"] = v
            continue
        if line.strip().startswith("- proposed_problem_text:"):
            v = _extract_backticked_value(line, "proposed_problem_text")
            if not v:
                v = _extract_relaxed_field_value(line, "proposed_problem_text")
            current["proposed_problem_text"] = v
            continue
        v = _extract_backticked_value(line, "selected_replacements")
        if v or line.strip().startswith("- selected_replacements:"):
            parsed: dict[str, str] = {}
            try:
                lit = ast.literal_eval(v) if v else {}
                if isinstance(lit, dict):
                    parsed = {str(k): str(val) for k, val in lit.items()}
            except Exception:
                parsed = {}
            current["selected_replacements"] = parsed
            continue
    if current:
        records.append(current)
    for rec in records:
        rid = int(rec.get("id") or 0)
        if rid <= 0:
            continue
        base = by_id.get(rid, {"id": rid})
        if not base.get("source_description"):
            base["source_description"] = str(rec.get("source_description") or "")
        if not base.get("action"):
            base["action"] = str(rec.get("action") or "")
        if not base.get("write_recommendation"):
            base["write_recommendation"] = str(rec.get("write_recommendation") or "")
        if not base.get("selected_replacements"):
            base["selected_replacements"] = rec.get("selected_replacements") or {}
        if not base.get("proposed_problem_text"):
            base["proposed_problem_text"] = str(rec.get("proposed_problem_text") or "")
        by_id[rid] = base

    final_rows = []
    for rid in sorted(by_id.keys()):
        row = by_id[rid]
        final_rows.append(
            {
                "id": int(rid),
                "source_description": str(row.get("source_description") or ""),
                "action": str(row.get("action") or ""),
                "write_recommendation": str(row.get("write_recommendation") or ""),
                "selected_replacements": row.get("selected_replacements") if isinstance(row.get("selected_replacements"), dict) else {},
                "proposed_problem_text": str(row.get("proposed_problem_text") or ""),
            }
        )

    if not final_rows:
        return [], "report_parse_failed:no_record_blocks"
    return final_rows, ""


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser()
    parser.add_argument("--volume", required=True)
    parser.add_argument("--section", required=True)
    parser.add_argument("--title", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verbose-assets", action="store_true")
    parser.add_argument("--apply-safe-from-report", default="")
    parser.add_argument("--formula-ocr-backend", default="pix2tex", choices=["pix2tex"])
    parser.add_argument("--confidence-threshold", type=float, default=0.85)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    dry_run = not bool(args.write)
    root = project_root()
    db_path = default_db_path()
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = root / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    title_filters = {normalize_title(t) for t in args.title if str(t).strip()}

    apply_report_arg = str(args.apply_safe_from_report or "").strip()
    if apply_report_arg:
        source_report_path = Path(apply_report_arg)
        if not source_report_path.is_absolute():
            source_report_path = root / source_report_path

        dry_run_apply = not bool(args.write)
        rows_from_report, parse_err = parse_candidates_from_report(source_report_path)
        if parse_err:
            lines = [
                "# DOCX Formula Asset Apply-Safe-From-Report",
                f"- volume: `{args.volume}`",
                f"- section: `{args.section}`",
                "- postprocess_script: `docx_formula_asset_pix2tex_backfill.py`",
                "- no_ocr_rerun: `true`",
                f"- source_report: `{source_report_path.as_posix()}`",
                f"- dry_run: `{dry_run_apply}`",
                f"- parse_error: `{parse_err}`",
                "",
                "## Summary",
                "- applied_records: `0`",
                "- skipped_records: `0`",
                "- skipped_reasons: `{}`",
                "- updated_ids: `[]`",
            ]
            report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(report_path.as_posix())
            return 1

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        applied_records = 0
        skipped_records = 0
        skipped_reasons: dict[str, int] = {}
        updated_ids: list[int] = []

        for item in rows_from_report:
            rec_id = int(item.get("id") or 0)
            action = str(item.get("action") or "")
            write_recommendation = str(item.get("write_recommendation") or "")
            replacements = item.get("selected_replacements") or {}
            proposed = str(item.get("proposed_problem_text") or "")
            reason = ""
            if rec_id <= 0:
                reason = "invalid_id"
            elif write_recommendation != "yes":
                reason = "write_recommendation_not_yes"
            elif action not in ("proposed_update", "partial_proposed_update"):
                reason = "action_not_writable"
            elif not isinstance(replacements, dict) or not replacements:
                reason = "empty_selected_replacements"
            elif not proposed:
                reason = "missing_proposed_problem_text"
            elif detect_mojibake_text(proposed).get("mojibake_detected", False):
                reason = "mojibake_proposed_problem_text"

            row = None
            if not reason:
                row = cur.execute(
                    """
                    SELECT id, source_volume, source_section, problem_text, notes
                    FROM textbook_examples
                    WHERE id=?
                    """,
                    (rec_id,),
                ).fetchone()
                if not row:
                    reason = "record_not_found"
                elif str(row["source_volume"] or "") != str(args.volume):
                    reason = "volume_mismatch"
                elif str(row["source_section"] or "") != str(args.section):
                    reason = "section_mismatch"
                elif dry_run_apply:
                    reason = "dry_run_mode"

            if reason:
                skipped_records += 1
                skipped_reasons[reason] = int(skipped_reasons.get(reason, 0)) + 1
                continue

            old_problem_text = str(row["problem_text"] or "")
            meta = load_meta(str(row["notes"] or ""))
            meta["original_problem_text_before_docx_formula_pool_backfill"] = old_problem_text
            meta["docx_formula_pool_selected_replacements"] = {str(k): str(v) for k, v in replacements.items()}
            meta["docx_formula_pool_backfill_status"] = action.replace("proposed_", "applied_")
            meta["rollback_available"] = True
            if "[FORMULA_MISSING]" in proposed or PLACEHOLDER_RE.search(proposed):
                meta["needs_formula_review"] = True
                meta["review_required"] = True
            meta["docx_formula_pool_backfill_updated_at"] = now_iso()
            cur.execute(
                "UPDATE textbook_examples SET problem_text=?, notes=? WHERE id=?",
                (proposed, dump_meta(meta), rec_id),
            )
            applied_records += 1
            updated_ids.append(rec_id)

        if not dry_run_apply:
            conn.commit()
        conn.close()

        lines = [
            "# DOCX Formula Asset Apply-Safe-From-Report",
            f"- volume: `{args.volume}`",
            f"- section: `{args.section}`",
            "- postprocess_script: `docx_formula_asset_pix2tex_backfill.py`",
            "- no_ocr_rerun: `true`",
            f"- source_report: `{source_report_path.as_posix()}`",
            f"- dry_run: `{dry_run_apply}`",
            "",
            "## Summary",
            f"- applied_records: `{applied_records}`",
            f"- skipped_records: `{skipped_records}`",
            f"- skipped_reasons: `{skipped_reasons}`",
            f"- updated_ids: `{updated_ids}`",
        ]
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(report_path.as_posix())
        return 0

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT id, source_description, problem_text, notes, correct_answer, detailed_solution
        FROM textbook_examples
        WHERE source_volume=? AND source_section=?
        ORDER BY id ASC
        """,
        (args.volume, args.section),
    ).fetchall()

    section_pool = load_section_formula_asset_pool(rows, root, args.volume, args.section)
    stats = {
        "processed_records": 0,
        "records_with_formula_assets": 0,
        "formula_assets_total": 0,
        "readable_assets": len(section_pool),
        "pix2tex_success": 0,
        "pix2tex_low_quality": 0,
        "selected_replacements": 0,
        "proposed_updates": 0,
        "partial_proposed_updates": 0,
        "still_missing_formula": 0,
        "section_pool_assets": len(section_pool),
        "classified_assets": 0,
        "diagram_assets": 0,
        "formula_assets": 0,
        "blocked_by_class_mismatch": 0,
        "updated_records": 0,
        "safe_proposed_update_records": 0,
        "safe_partial_update_records": 0,
        "skipped_mojibake_records": 0,
        "blocked_mojibake_outputs": 0,
        "unsafe_records": 0,
    }
    for a in section_pool:
        stats["classified_assets"] += 1
        cls = str(a.get("classification") or "unknown_formula")
        if cls == "diagram_or_picture":
            stats["diagram_assets"] += 1
        else:
            stats["formula_assets"] += 1
        if a.get("classification") in ("formula_abs_x", "unknown_formula"):
            stats["pix2tex_success"] += 1
        else:
            stats["pix2tex_low_quality"] += 1

    processed = []

    for r in rows:
        title_raw = str(r["source_description"] or "")
        title_norm = normalize_title(title_raw)
        if title_filters and title_norm not in title_filters:
            continue

        problem_text = str(r["problem_text"] or "")
        placeholders = parse_placeholders(problem_text)
        if not placeholders:
            continue
        title_moji = detect_mojibake_text(title_raw)
        text_moji = detect_mojibake_text(problem_text)

        meta = load_meta(str(r["notes"] or ""))
        rec_assets = meta.get("formula_assets", []) if isinstance(meta, dict) else []
        if not isinstance(rec_assets, list):
            rec_assets = []

        stats["processed_records"] += 1
        stats["formula_assets_total"] += len(rec_assets)
        if rec_assets:
            stats["records_with_formula_assets"] += 1

        expected = expected_classes_for_record(title_norm, problem_text, placeholders)
        replacements: dict[str, str] = {}
        selected_rows = []
        rejected_all = []
        used = set()
        safety_status = "no_change"
        write_recommendation = "no"
        write_blocked_reason = ""

        if title_moji["mojibake_detected"] or text_moji["mojibake_detected"]:
            action = "skipped_mojibake"
            reason = "record_text_mojibake"
            stats["skipped_mojibake_records"] += 1
            stats["unsafe_records"] += 1
            processed.append(
                {
                    "id": int(r["id"]),
                    "source_description": title_raw,
                    "db_problem_text": problem_text,
                    "placeholder_tokens": placeholders,
                    "expected_placeholder_classes": expected,
                    "current_record_assets": [],
                    "section_pool_candidate_matches": [],
                    "rejected_assets": [],
                    "rejected_assets_summary": {},
                    "rejected_assets_samples": [],
                    "selected_replacements": {},
                    "proposed_problem_text": problem_text,
                    "action": action,
                    "reason": reason,
                    "cross_record_asset_used": False,
                    "safety_status": "skip_mojibake",
                    "write_recommendation": "no",
                    "write_blocked_reason": reason,
                }
            )
            continue

        for tk in placeholders:
            ex = expected.get(tk, "unknown")
            if tk == "[FORMULA_MISSING]":
                continue
            rep, sel, rejected = choose_replacement(tk, ex, int(r["id"]), section_pool, used)
            rejected_all.extend(rejected)
            if rep and ex != "full_absolute_value_inequality":
                replacements[tk] = rep
                selected_rows.append(sel)
            elif rep and ex == "full_absolute_value_inequality":
                # still block for current stage unless exact known target exists in pool
                if rep in ("|x-2|<4", "|x+5|>1"):
                    replacements[tk] = rep
                    selected_rows.append(sel)

        if rejected_all:
            stats["blocked_by_class_mismatch"] += len([x for x in rejected_all if x.get("reason") == "class_mismatch"])

        proposed = problem_text
        for tk, rp in replacements.items():
            proposed = proposed.replace(tk, rp)
        proposed = clean_b1_11_text(proposed)
        proposed_moji = detect_mojibake_text(proposed)

        total_replaceable = len([x for x in placeholders if x != "[FORMULA_MISSING]"])
        action = "no_change"
        reason = "no_valid_replacement"
        if replacements and proposed != problem_text:
            if len(replacements) == total_replaceable:
                action = "proposed_update"
                stats["proposed_updates"] += 1
            else:
                action = "partial_proposed_update"
                stats["partial_proposed_updates"] += 1
            reason = "placeholder_replaced"
            stats["selected_replacements"] += len(replacements)
            if proposed_moji["mojibake_detected"]:
                action = "blocked_mojibake_output"
                reason = "mojibake_in_proposed_output"
                stats["blocked_mojibake_outputs"] += 1
                stats["unsafe_records"] += 1

            if (
                not dry_run
                and action in ("proposed_update", "partial_proposed_update")
                and replacements
                and not proposed_moji["mojibake_detected"]
            ):
                meta["original_problem_text_before_docx_formula_pool_backfill"] = problem_text
                meta["docx_formula_pool_selected_replacements"] = replacements
                reject_counter: dict[str, int] = {}
                for rj in rejected_all:
                    key = str(rj.get("reason") or "unknown")
                    reject_counter[key] = int(reject_counter.get(key, 0)) + 1
                meta["docx_formula_pool_rejected_summary"] = reject_counter
                meta["docx_formula_pool_cross_record_asset_used"] = any(
                    int((s or {}).get("source_record_id") or 0) != int(r["id"]) for s in selected_rows if s
                )
                meta["docx_formula_pool_backfill_status"] = action.replace("proposed_", "applied_")
                meta["rollback_available"] = True
                if "[FORMULA_MISSING]" in proposed:
                    meta["needs_formula_review"] = True
                    meta["formula_missing"] = True
                    meta["review_required"] = True
                meta["docx_formula_pool_backfill_updated_at"] = now_iso()
                cur.execute(
                    "UPDATE textbook_examples SET problem_text=?, notes=? WHERE id=?",
                    (proposed, dump_meta(meta), int(r["id"])),
                )
                stats["updated_records"] += 1
        selected_filename_moji = any(
            detect_mojibake_text(str((s or {}).get("filename") or "")).get("mojibake_detected", False)
            for s in selected_rows if s
        )
        if action in ("proposed_update", "partial_proposed_update") and not proposed_moji["mojibake_detected"] and not selected_filename_moji:
            if "exam_practice" in title_raw:
                safety_status = "unsafe"
                write_blocked_reason = "exam_practice_excluded"
                stats["unsafe_records"] += 1
            else:
                safety_status = "safe_to_write"
                write_recommendation = "yes"
                if action == "proposed_update":
                    stats["safe_proposed_update_records"] += 1
                else:
                    stats["safe_partial_update_records"] += 1
                if "[FORMULA_MISSING]" in proposed:
                    write_blocked_reason = "formula_review_remaining"
        elif action == "blocked_mojibake_output":
            safety_status = "unsafe"
            write_blocked_reason = "blocked_mojibake_output"
        elif selected_filename_moji:
            safety_status = "unsafe"
            write_blocked_reason = "selected_asset_filename_mojibake"
            stats["unsafe_records"] += 1
        elif action == "no_change":
            safety_status = "no_change"
            write_blocked_reason = "no_change"
        else:
            safety_status = "unsafe"
            write_blocked_reason = "not_safe"
            stats["unsafe_records"] += 1

        section_pool_matches = []
        for tk, ex in expected.items():
            hits = [a for a in section_pool if a.get("classification") == ex]
            section_pool_matches.append({"token": tk, "expected_class": ex, "matches": [str(h.get("filename") or "") for h in hits[:8]]})

        current_assets = []
        for a in rec_assets[:20]:
            p = str(a.get("converted_path") or a.get("display_path") or a.get("path") or "")
            current_assets.append({
                "filename": Path(p).name if p else "",
                "placeholder_token": str(a.get("placeholder_token") or ""),
                "placeholder_index": int(a.get("placeholder_index") or 0),
            })

        rej_summary: dict[str, int] = {}
        for rj in rejected_all:
            k = str(rj.get("reason") or "unknown")
            rej_summary[k] = int(rej_summary.get(k, 0)) + 1
        if "class_mismatch" in rej_summary:
            stats["blocked_by_class_mismatch"] += rej_summary["class_mismatch"]
        samples = rejected_all[:5]
        processed.append(
            {
                "id": int(r["id"]),
                "source_description": title_raw,
                "db_problem_text": problem_text,
                "placeholder_tokens": placeholders,
                "expected_placeholder_classes": expected,
                "current_record_assets": current_assets,
                "section_pool_candidate_matches": section_pool_matches,
                "rejected_assets": rejected_all[:120],
                "rejected_assets_summary": rej_summary,
                "rejected_assets_samples": samples,
                "selected_replacements": replacements,
                "proposed_problem_text": proposed,
                "action": action,
                "reason": reason,
                "cross_record_asset_used": any(int((s or {}).get("source_record_id") or 0) != int(r["id"]) for s in selected_rows if s),
                "safety_status": safety_status,
                "write_recommendation": write_recommendation,
                "write_blocked_reason": write_blocked_reason,
            }
        )

    cur.execute(
        "SELECT COUNT(*) AS c FROM textbook_examples WHERE source_volume=? AND source_section=? AND problem_text LIKE '%[FORMULA_%'",
        (args.volume, args.section),
    )
    stats["still_missing_formula"] = int(cur.fetchone()["c"])
    if not dry_run:
        conn.commit()
    conn.close()

    lines = [
        "# DOCX Formula Asset Selection Pool Dry-run Report",
        f"- volume: `{args.volume}`",
        f"- section: `{args.section}`",
        "- postprocess_script: `docx_formula_asset_pix2tex_backfill.py`",
        f"- dry_run: `{dry_run}`",
        f"- title_filters: `{sorted(list(title_filters))}`",
        "",
    ]
    for it in processed:
        lines.extend(
            [
                f"## id={it['id']} {it['source_description']}",
                f"- db_problem_text: `{it['db_problem_text']}`",
                f"- placeholder_tokens: `{it['placeholder_tokens']}`",
                f"- expected_placeholder_classes: `{it['expected_placeholder_classes']}`",
                f"- current_record_assets: `{it['current_record_assets']}`",
                f"- section_pool_candidate_matches: `{it['section_pool_candidate_matches']}`",
                f"- rejected_assets_summary: `{it['rejected_assets_summary']}`",
                f"- rejected_assets_samples: `{it['rejected_assets_samples']}`",
                f"- selected_replacements: `{it['selected_replacements']}`",
                f"- proposed_problem_text: `{it['proposed_problem_text']}`",
                f"- cross_record_asset_used: `{it['cross_record_asset_used']}`",
                f"- action: `{it['action']}`",
                f"- reason: `{it['reason']}`",
                f"- safety_status: `{it['safety_status']}`",
                f"- write_recommendation: `{it['write_recommendation']}`",
                f"- write_blocked_reason: `{it['write_blocked_reason']}`",
                "",
            ]
        )
        if args.verbose_assets:
            lines.append(f"- rejected_assets_full: `{it['rejected_assets']}`")
            lines.append("")

    lines.append("## Summary")
    for k in (
        "processed_records",
        "records_with_formula_assets",
        "formula_assets_total",
        "readable_assets",
        "pix2tex_success",
        "pix2tex_low_quality",
        "section_pool_assets",
        "classified_assets",
        "diagram_assets",
        "formula_assets",
                "selected_replacements",
                "proposed_updates",
                "partial_proposed_updates",
        "blocked_by_class_mismatch",
        "updated_records",
        "safe_proposed_update_records",
        "safe_partial_update_records",
        "skipped_mojibake_records",
        "blocked_mojibake_outputs",
        "unsafe_records",
        "still_missing_formula",
    ):
        lines.append(f"- {k}: `{stats[k]}`")

    lines.append("")
    lines.append("## Safe Write Candidates")
    safe_candidates = []
    for it in processed:
        canonical_title = normalize_safe_title(str(it.get("source_description") or ""))
        still_missing = "[FORMULA_MISSING]" in str(it.get("proposed_problem_text") or "")
        row = {
            "id": it.get("id"),
            "source_description": it.get("source_description"),
            "canonical_title": canonical_title,
            "action": it.get("action"),
            "selected_replacements": it.get("selected_replacements"),
            "proposed_problem_text": it.get("proposed_problem_text"),
            "still_has_formula_missing": still_missing,
            "write_recommendation": it.get("write_recommendation"),
        }
        if str(it.get("safety_status")) == "safe_to_write":
            safe_candidates.append(row)
        lines.append(f"- id={row['id']} | source_description=`{row['source_description']}` | canonical_title=`{row['canonical_title']}` | action=`{row['action']}` | selected_replacements=`{row['selected_replacements']}` | still_has_formula_missing=`{row['still_has_formula_missing']}` | write_recommendation=`{row['write_recommendation']}`")

    safe_titles = [
        normalize_safe_title(str(it.get("source_description") or ""))
        for it in processed
        if str(it.get("safety_status")) == "safe_to_write"
        and str(it.get("write_recommendation")) == "yes"
        and is_safe_cli_title(normalize_safe_title(str(it.get("source_description") or "")))
    ]
    lines.append("")
    lines.append("## Suggested safe write commands")
    if safe_titles:
        safe_titles = sorted(list(dict.fromkeys(safe_titles)))
        cmd = (
            'python scripts\\docx_formula_asset_pix2tex_backfill.py '
            f'--volume "{args.volume}" --section "{args.section}" '
            + " ".join([f'--title "{t}"' for t in safe_titles])
            + ' --write --formula-ocr-backend pix2tex --confidence-threshold '
            + str(args.confidence_threshold)
            + ' --report "reports/b1_import_debug/b1_1_1_docx_formula_asset_selection_pool_safe_write_report.md"'
        )
        if detect_mojibake_text(cmd).get("mojibake_detected", False):
            lines.append("No safe command generated because command contains mojibake.")
        else:
            lines.append(cmd)
    else:
        lines.append("No safe write command generated.")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
