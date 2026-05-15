#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Backfill Gemini Vision metadata for DOCX formula assets.

Default mode is dry-run and OCR is disabled unless the app config enables
ENABLE_DOCX_FORMULA_OCR_FALLBACK or --force-ocr is passed.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


OCR_PROMPT = (
    "請只轉錄圖片中的數學式，輸出 LaTeX 或清楚純文字。"
    "不要解題，不要補題目，不要猜看不清楚的內容。"
    "若看不清楚，輸出 [UNREADABLE_FORMULA]。只輸出公式本身。"
)

READABLE_FORMATS = {"png", "jpg", "jpeg"}
VECTOR_FORMATS = {"wmf", "emf"}
DEFAULT_REPORT_PATH = Path("reports/b1_import_debug/b1_1_1_formula_vision_dry_run_report.md")


@dataclass
class BackfillRow:
    id: int
    source_description: str
    problem_text: str
    notes: str


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    sys.path.insert(0, str(project_root()))
    from config import Config  # pylint: disable=import-outside-toplevel

    return Path(Config.db_path)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_metadata(notes: str) -> dict[str, Any]:
    if not str(notes or "").strip():
        return {}
    try:
        parsed = json.loads(notes)
        return parsed if isinstance(parsed, dict) else {"raw": notes}
    except Exception:
        return {"raw": notes}


def _dump_metadata(meta: dict[str, Any]) -> str:
    return json.dumps(meta, ensure_ascii=False, sort_keys=True)


def _asset_format(asset: dict[str, Any]) -> str:
    original = str(asset.get("original_format") or "").lower().lstrip(".")
    if original == "jpg":
        original = "jpeg"
    for key in ("converted_path", "display_path", "path"):
        p = str(asset.get(key) or "")
        ext = os.path.splitext(p)[1].lower().lstrip(".")
        if ext:
            return "jpeg" if ext == "jpg" else ext
    ctype = str(asset.get("content_type") or "").lower()
    if "png" in ctype:
        return "png"
    if "jpeg" in ctype or "jpg" in ctype:
        return "jpeg"
    if "wmf" in ctype:
        return "wmf"
    if "emf" in ctype:
        return "emf"
    return original or "unknown"


def _readable_asset_path(asset: dict[str, Any], root_path: Path) -> tuple[str | None, str | None]:
    """Pick readable image path by priority: display > converted > path."""
    candidates = [
        str(asset.get("display_path") or ""),
        str(asset.get("converted_path") or ""),
        str(asset.get("path") or ""),
    ]
    for rel in candidates:
        if not rel:
            continue
        fmt = os.path.splitext(rel)[1].lower().lstrip(".")
        if fmt == "jpg":
            fmt = "jpeg"
        if not fmt:
            fmt = _asset_format(asset)
        if fmt not in READABLE_FORMATS:
            continue
        abs_path = Path(rel) if os.path.isabs(rel) else root_path / rel
        if not abs_path.exists():
            continue
        return str(abs_path), rel.replace("\\", "/")
    return None, None


def _default_ocr_callable(image_path: str, prompt: str) -> tuple[str, str]:
    sys.path.insert(0, str(project_root()))
    from PIL import Image  # pylint: disable=import-outside-toplevel
    from core.ai_analyzer import get_model  # pylint: disable=import-outside-toplevel

    model = get_model("vision_analyzer")
    with Image.open(image_path) as img:
        resp = model.generate_content(
            [prompt, img],
            generation_config={"temperature": 0.0, "max_output_tokens": 512},
        )
    text = str(getattr(resp, "text", "") or "").strip()
    model_name = str(getattr(model, "model_name", "") or getattr(model, "_model_name", "") or "vision_analyzer")
    return text, model_name


def _init_summary(total_assets: int) -> dict[str, int]:
    return {
        "total_assets": int(total_assets),
        "success_count": 0,
        "failed_count": 0,
        "skipped_count": 0,
        "unreadable_count": 0,
    }


def process_row(
    row: BackfillRow,
    *,
    root_path: str | Path,
    ocr_enabled: bool,
    dry_run: bool = True,
    ocr_callable: Callable[[str, str], tuple[str, str] | str] | None = None,
    now_fn: Callable[[], str] = _now_iso,
) -> dict[str, Any]:
    """Return preview/update data for one textbook_examples row."""
    root = Path(root_path)
    meta = _load_metadata(row.notes)
    assets = meta.get("formula_assets", [])
    if not isinstance(assets, list):
        assets = []
    updated_assets: list[dict[str, Any]] = []
    item_summaries: list[dict[str, Any]] = []
    summary = _init_summary(len(assets))
    summary.update(
        {
            "processed_assets": len(assets),
            "readable_assets": 0,
            "skipped_no_readable_image": 0,
            "vision_success": 0,
            "vision_failed": 0,
        }
    )
    callable_fn = ocr_callable or _default_ocr_callable

    for asset in assets:
        if not isinstance(asset, dict):
            continue
        next_asset = dict(asset)
        next_asset["review_required"] = True
        readable_abs, readable_rel = _readable_asset_path(next_asset, root)
        status = ""
        ocr_text = ""
        error = ""

        if not readable_abs:
            status = "skipped_no_readable_image"
            summary["skipped_count"] += 1
            summary["skipped_no_readable_image"] += 1
            next_asset["formula_ocr_status"] = status
            next_asset["formula_ocr_source"] = "gemini_vision"
            next_asset["formula_ocr_updated_at"] = now_fn()
        else:
            summary["readable_assets"] += 1
            if not ocr_enabled:
                status = "skipped_ocr_disabled"
                summary["skipped_count"] += 1
                next_asset["formula_ocr_status"] = status
                next_asset["formula_ocr_source"] = "gemini_vision"
                next_asset["formula_ocr_updated_at"] = now_fn()
            else:
                try:
                    result = callable_fn(readable_abs, OCR_PROMPT)
                    if isinstance(result, tuple):
                        ocr_text, model_name = str(result[0] or "").strip(), str(result[1] or "vision_analyzer")
                    else:
                        ocr_text, model_name = str(result or "").strip(), "vision_analyzer"
                    if not ocr_text or ocr_text == "[UNREADABLE_FORMULA]":
                        status = "unreadable"
                        summary["unreadable_count"] += 1
                    else:
                        status = "success"
                        summary["success_count"] += 1
                        summary["vision_success"] += 1
                    next_asset["formula_ocr_status"] = status
                    next_asset["formula_ocr_text"] = ocr_text
                    next_asset["formula_ocr_source"] = "gemini_vision"
                    next_asset["formula_ocr_model"] = model_name
                    next_asset["review_required"] = True
                    next_asset["formula_ocr_updated_at"] = now_fn()
                except Exception as exc:  # OCR must never block import/backfill.
                    status = "failed"
                    error = str(exc)
                    summary["failed_count"] += 1
                    summary["vision_failed"] += 1
                    next_asset["formula_ocr_status"] = status
                    next_asset["formula_ocr_error"] = error
                    next_asset["formula_ocr_source"] = "gemini_vision"
                    next_asset["review_required"] = True
                    next_asset["formula_ocr_updated_at"] = now_fn()

        updated_assets.append(next_asset)
        item_summaries.append(
            {
                "id": row.id,
                "source_description": row.source_description,
                "problem_text": row.problem_text,
                "placeholder_token": next_asset.get("placeholder_token", ""),
                "asset_path": next_asset.get("path", ""),
                "display_path": next_asset.get("display_path", ""),
                "converted_path": next_asset.get("converted_path", ""),
                "conversion_status": next_asset.get("conversion_status", ""),
                "formula_ocr_status": status,
                "formula_ocr_text": ocr_text,
                "formula_ocr_error": error,
                "formula_ocr_source": next_asset.get("formula_ocr_source", ""),
                "formula_ocr_model": next_asset.get("formula_ocr_model", ""),
                "review_required": bool(next_asset.get("review_required", False)),
            }
        )

    updated_meta = dict(meta)
    updated_meta["formula_assets"] = updated_assets
    updated_meta["formula_ocr_summary"] = summary
    updated_meta["needs_review"] = True
    updated_meta["needs_formula_review"] = True
    return {
        "row_id": row.id,
        "source_description": row.source_description,
        "problem_text": row.problem_text,
        "dry_run": bool(dry_run),
        "changed": _dump_metadata(updated_meta) != _dump_metadata(meta),
        "metadata_before": meta,
        "metadata_after": updated_meta,
        "asset_summaries": item_summaries,
        "summary": summary,
    }


def fetch_target_rows(
    conn: sqlite3.Connection,
    *,
    curriculum: str,
    volume: str,
    section: str,
    titles: list[str] | None,
    limit: int | None,
) -> list[BackfillRow]:
    conn.row_factory = sqlite3.Row
    sql = """
        SELECT id, source_description, problem_text, notes
        FROM textbook_examples
        WHERE source_curriculum = ?
          AND source_volume = ?
          AND source_section LIKE ?
          AND notes LIKE '%formula_assets%'
    """
    params: list[Any] = [curriculum, volume, f"%{section}%"]
    if titles:
        sql += " AND (" + " OR ".join(["source_description LIKE ?"] * len(titles)) + ")"
        params.extend([f"{t}%" for t in titles])
    sql += """
        ORDER BY id
    """
    if limit is not None:
        sql += " LIMIT ?"
        params.append(int(limit))
    rows = conn.execute(sql, params).fetchall()
    return [
        BackfillRow(
            id=int(r["id"]),
            source_description=str(r["source_description"] or ""),
            problem_text=str(r["problem_text"] or ""),
            notes=str(r["notes"] or ""),
        )
        for r in rows
    ]


def run_backfill(
    *,
    db_path: str | Path,
    root_path: str | Path,
    curriculum: str = "vocational",
    volume: str = "數學B1",
    section: str = "1-1 數線與絕對值",
    titles: list[str] | None = None,
    limit: int | None = None,
    dry_run: bool = True,
    ocr_enabled: bool = False,
    ocr_callable: Callable[[str, str], tuple[str, str] | str] | None = None,
) -> dict[str, Any]:
    conn = sqlite3.connect(str(db_path))
    try:
        rows = fetch_target_rows(
            conn,
            curriculum=curriculum,
            volume=volume,
            section=section,
            titles=titles,
            limit=limit,
        )
        row_results = [
            process_row(r, root_path=root_path, ocr_enabled=ocr_enabled, dry_run=dry_run, ocr_callable=ocr_callable)
            for r in rows
        ]
        if not dry_run:
            for result in row_results:
                conn.execute(
                    "UPDATE textbook_examples SET notes = ? WHERE id = ?",
                    (_dump_metadata(result["metadata_after"]), int(result["row_id"])),
                )
            conn.commit()
        totals = _init_summary(sum(r["summary"]["total_assets"] for r in row_results))
        totals.update(
            {
                "processed_records": len(row_results),
                "processed_assets": 0,
                "readable_assets": 0,
                "skipped_no_readable_image": 0,
                "vision_success": 0,
                "vision_failed": 0,
            }
        )
        for result in row_results:
            for key in ("success_count", "failed_count", "skipped_count", "unreadable_count"):
                totals[key] += int(result["summary"].get(key, 0))
            for key in ("processed_assets", "readable_assets", "skipped_no_readable_image", "vision_success", "vision_failed"):
                totals[key] += int(result["summary"].get(key, 0))
        return {
            "scope": {"curriculum": curriculum, "volume": volume, "section": section, "titles": titles or [], "limit": limit},
            "dry_run": bool(dry_run),
            "ocr_enabled": bool(ocr_enabled),
            "question_count": len(row_results),
            "summary": totals,
            "rows": row_results,
        }
    finally:
        conn.close()


def _preview(text: str, width: int = 120) -> str:
    t = str(text or "").replace("\n", " ").strip()
    return t[:width] + ("..." if len(t) > width else "")


def render_markdown_report(result: dict[str, Any]) -> str:
    scope = result.get("scope", {})
    summary = result.get("summary", {})
    lines = [
        "# B1 1-1 Formula Gemini Vision Dry-Run Report",
        "",
        "## Scope",
        f"- curriculum: `{scope.get('curriculum', '')}`",
        f"- volume: `{scope.get('volume', '')}`",
        f"- section filter: `{scope.get('section', '')}`",
        f"- titles: `{scope.get('titles', [])}`",
        f"- limit: `{scope.get('limit')}`",
        f"- mode: `{'dry_run' if result.get('dry_run') else 'write'}`",
        f"- ocr_enabled: `{bool(result.get('ocr_enabled'))}`",
        "",
        "## Totals",
        f"- processed_records: {summary.get('processed_records', result.get('question_count', 0))}",
        f"- questions: {result.get('question_count', 0)}",
        f"- processed_assets: {summary.get('processed_assets', 0)}",
        f"- readable_assets: {summary.get('readable_assets', 0)}",
        f"- skipped_no_readable_image: {summary.get('skipped_no_readable_image', 0)}",
        f"- vision_success: {summary.get('vision_success', 0)}",
        f"- vision_failed: {summary.get('vision_failed', 0)}",
        f"- formula assets: {summary.get('total_assets', 0)}",
        f"- success: {summary.get('success_count', 0)}",
        f"- failed: {summary.get('failed_count', 0)}",
        f"- skipped: {summary.get('skipped_count', 0)}",
        f"- unreadable: {summary.get('unreadable_count', 0)}",
        "",
        "## Per-Question Summary",
    ]
    rows = result.get("rows", [])
    all_items = [item for row in rows for item in row.get("asset_summaries", [])]
    if not rows:
        lines.append("- No matching formula assets found.")
    for row in rows:
        row_summary = row.get("summary", {})
        row_items = row.get("asset_summaries", [])
        lines.extend(
            [
                f"### id={row.get('row_id')} `{_preview(row.get('source_description', ''), 80)}`",
                f"- formula_assets_count: {row_summary.get('processed_assets', 0)}",
                f"- readable_assets_count: {row_summary.get('readable_assets', 0)}",
                f"- skipped_assets_count: {row_summary.get('skipped_no_readable_image', 0)}",
                "- review_required: `True`",
                "- OCR / vision candidates:",
            ]
        )
        if not row_items:
            lines.append("  - none")
            lines.append("")
            continue
        for item in row_items:
            lines.append(
                "  - "
                + f"{item.get('placeholder_token', '')} "
                + f"status=`{item.get('formula_ocr_status', '')}` "
                + f"source=`{item.get('formula_ocr_source', '')}` "
                + f"model=`{item.get('formula_ocr_model', '')}` "
                + f"text=`{_preview(item.get('formula_ocr_text', ''), 80)}` "
                + f"error=`{_preview(item.get('formula_ocr_error', ''), 80)}`"
            )
        lines.append("")
    success = [i for i in all_items if i.get("formula_ocr_status") == "success"][:5]
    unreadable = [i for i in all_items if i.get("formula_ocr_status") == "unreadable"]
    failed = [i for i in all_items if i.get("formula_ocr_status") == "failed"]
    lines.extend(["## Manual Review Suggestions", "", "### Success Sample"])
    lines.extend([f"- id={i.get('id')} {i.get('placeholder_token')} `{_preview(i.get('formula_ocr_text', ''), 80)}`" for i in success] or ["- None"])
    lines.extend(["", "### Unreadable"])
    lines.extend([f"- id={i.get('id')} {i.get('placeholder_token')} `{_preview(i.get('problem_text', ''), 100)}`" for i in unreadable] or ["- None"])
    lines.extend(["", "### Failed"])
    lines.extend([f"- id={i.get('id')} {i.get('placeholder_token')} error=`{_preview(i.get('formula_ocr_error', ''), 100)}`" for i in failed] or ["- None"])
    lines.append("")
    return "\n".join(lines)


def write_report(result: dict[str, Any], report_path: str | Path) -> Path:
    path = Path(report_path)
    if not path.is_absolute():
        path = project_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown_report(result), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill formula OCR metadata for DOCX MathType assets.")
    parser.add_argument("--db", default=str(default_db_path()))
    parser.add_argument("--curriculum", default="vocational")
    parser.add_argument("--volume", default="數學B1")
    parser.add_argument("--section", default="1-1 數線與絕對值")
    parser.add_argument("--title", action="append", dest="titles", default=[], help="Filter source_description prefix; repeatable.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--write", action="store_true", help="Write metadata updates to DB.")
    parser.add_argument("--force-ocr", action="store_true", help="Run OCR even if ENABLE_DOCX_FORMULA_OCR_FALLBACK is false.")
    parser.add_argument("--vision", action="store_true", default=True, help="Use Gemini Vision OCR in dry-run.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    args = parser.parse_args()

    dry_run = not bool(args.write)
    ocr_enabled = bool(args.force_ocr or args.vision)
    app = None
    try:
        sys.path.insert(0, str(project_root()))
        from app import create_app  # pylint: disable=import-outside-toplevel

        app = create_app()
        if not (args.force_ocr or args.vision):
            ocr_enabled = bool(app.config.get("ENABLE_DOCX_FORMULA_OCR_FALLBACK", False))
    except Exception:
        app = None
        if not (args.force_ocr or args.vision):
            ocr_enabled = False

    run_kwargs = {
        "db_path": args.db,
        "root_path": project_root(),
        "curriculum": args.curriculum,
        "volume": args.volume,
        "section": args.section,
        "titles": list(args.titles or []),
        "limit": args.limit,
        "dry_run": dry_run,
        "ocr_enabled": ocr_enabled,
    }
    if app is not None and ocr_enabled:
        with app.app_context():
            result = run_backfill(**run_kwargs)
    else:
        result = run_backfill(**run_kwargs)
    report_path = write_report(result, args.report)
    print(render_markdown_report(result))
    print(f"\nReport written: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
