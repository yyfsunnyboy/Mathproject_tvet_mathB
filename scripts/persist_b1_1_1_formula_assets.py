#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Persist B1 1-1 formula assets from DOCX extraction output."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import shutil
import sqlite3
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_REPORT_PATH = Path("reports/b1_import_debug/b1_1_1_formula_asset_persist_dry_run_report.md")
DEFAULT_PERSIST_DIR = Path("uploads/question_assets/longteng_數學B1/CH1/1-1/formula_assets")
READABLE_FORMATS = {"png", "jpg", "jpeg"}


@dataclass
class PersistRow:
    id: int
    source_description: str
    problem_text: str
    notes: str


class _Queue:
    def put(self, _msg):
        return None


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_db_path() -> Path:
    sys.path.insert(0, str(project_root()))
    from config import Config  # pylint: disable=import-outside-toplevel

    return Path(Config.db_path)


def _load_metadata(notes: str) -> dict[str, Any]:
    if not str(notes or "").strip():
        return {}
    try:
        parsed = json.loads(notes)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _dump_metadata(meta: dict[str, Any]) -> str:
    return json.dumps(meta, ensure_ascii=False, sort_keys=True)


def _title_from_source_description(source_description: str) -> str:
    text = str(source_description or "")
    idx = text.find(" [source_type=")
    return text[:idx].strip() if idx >= 0 else text.strip()


def _asset_format(asset: dict[str, Any]) -> str:
    original = str(asset.get("original_format") or "").lower().lstrip(".")
    if original == "jpg":
        original = "jpeg"
    for key in ("original_path", "path", "display_path", "converted_path"):
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


def _is_formula_asset(asset: dict[str, Any]) -> bool:
    kind = str(asset.get("media_kind") or asset.get("asset_type") or "").lower()
    if kind == "formula_asset":
        return True
    token = str(asset.get("placeholder_token") or "")
    return bool(re.search(r"\[FORMULA_IMAGE_\d+\]", token))


def _candidate_source_rel(asset: dict[str, Any]) -> str:
    for key in ("original_path", "path", "display_path", "converted_path"):
        rel = str(asset.get(key) or "").strip()
        if rel:
            return rel
    return ""


def _load_docx_media_bytes(docx_path: str | Path, target_ref: str) -> tuple[bytes | None, str]:
    """Load media bytes from original docx using relationship target_ref."""
    try:
        docx = Path(docx_path)
        if not docx.exists():
            return None, f"docx_not_found: {docx.as_posix()}"
        rel = str(target_ref or "").replace("\\", "/").strip()
        if not rel:
            return None, "missing_target_ref"
        while rel.startswith("../"):
            rel = rel[3:]
        zip_member = rel if rel.startswith("word/") else f"word/{rel.lstrip('/')}"
        with zipfile.ZipFile(docx, "r") as zf:
            return zf.read(zip_member), ""
    except KeyError:
        return None, f"target_ref_not_found_in_docx: {target_ref}"
    except Exception as exc:
        return None, str(exc)


def _build_persistent_asset(
    *,
    record_id: int,
    asset_index: int,
    source_asset: dict[str, Any],
    source_rel: str,
    persisted_rel: str,
) -> dict[str, Any]:
    fmt = _asset_format(source_asset)
    guessed_content_type = mimetypes.guess_type(persisted_rel)[0] or str(source_asset.get("content_type") or "")
    next_asset = dict(source_asset)
    next_asset["old_original_path"] = source_rel
    next_asset["original_path_persistent"] = persisted_rel
    next_asset["path"] = persisted_rel
    next_asset["persist_status"] = "success"
    next_asset["content_type"] = guessed_content_type
    next_asset["original_format"] = fmt
    next_asset["record_id"] = int(record_id)
    next_asset["placeholder_index"] = int(source_asset.get("placeholder_index") or asset_index)
    if fmt in READABLE_FORMATS:
        next_asset["display_path"] = persisted_rel
    return next_asset


def _asset_dedupe_key(asset: dict[str, Any]) -> str:
    h = str(asset.get("asset_hash") or "").strip()
    if h:
        return f"hash:{h}"
    token = str(asset.get("placeholder_token") or "").strip()
    rid = str(asset.get("rid") or "").strip()
    base = os.path.basename(str(asset.get("path") or asset.get("original_path") or "")).strip()
    fmt = str(asset.get("original_format") or "").strip().lower()
    return f"fallback:{token}|{rid}|{base}|{fmt}"


def _merge_formula_assets_prefer_persistent(existing_assets: list[dict[str, Any]], new_assets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for a in existing_assets + new_assets:
        if isinstance(a, dict):
            grouped.setdefault(_asset_dedupe_key(a), []).append(a)
    merged: list[dict[str, Any]] = []
    for _k, group in grouped.items():
        persistent = [g for g in group if str(g.get("persist_status") or "").lower() in ("success", "persisted")]
        chosen = persistent[0] if persistent else group[-1]
        merged.append(dict(chosen))
    merged.sort(key=lambda a: 1 if str(a.get("persist_status") or "").lower() in ("success", "persisted") else 0, reverse=True)
    return merged


def fetch_target_rows(
    conn: sqlite3.Connection,
    *,
    curriculum: str,
    volume: str,
    section: str,
    titles: list[str] | None,
    limit_records: int | None,
) -> list[PersistRow]:
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
    sql += " ORDER BY id"
    if limit_records is not None:
        sql += " LIMIT ?"
        params.append(int(limit_records))
    rows = conn.execute(sql, params).fetchall()
    return [
        PersistRow(
            id=int(r["id"]),
            source_description=str(r["source_description"] or ""),
            problem_text=str(r["problem_text"] or ""),
            notes=str(r["notes"] or ""),
        )
        for r in rows
    ]


def extract_docx_question_assets(docx_path: str | Path) -> tuple[dict[str, list[dict[str, Any]]], str]:
    docx = Path(docx_path)
    if not docx.exists():
        return {}, f"docx_not_found: {docx.as_posix()}"
    sys.path.insert(0, str(project_root()))
    from app import create_app  # pylint: disable=import-outside-toplevel
    import core.textbook_processor as processor  # pylint: disable=import-outside-toplevel

    app = create_app()
    with app.app_context():
        _ = processor.extract_content_from_file(str(docx), _Queue())
        ctx = getattr(processor, "_DOCX_IMPORT_CONTEXT", {}) or {}
    q_assets = ctx.get("question_assets", {}) if isinstance(ctx, dict) else {}
    if not isinstance(q_assets, dict):
        q_assets = {}
    return q_assets, ""


def run_persist(
    *,
    db_path: str | Path,
    docx_path: str | Path,
    root_path: str | Path,
    persist_dir: str | Path = DEFAULT_PERSIST_DIR,
    curriculum: str = "vocational",
    volume: str = "數學B1",
    section: str = "1-1 數線與絕對值",
    titles: list[str] | None = None,
    limit_records: int | None = None,
    dry_run: bool = True,
    write: bool = False,
    docx_question_assets_override: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    sys.path.insert(0, str(project_root()))
    import core.textbook_processor as processor  # pylint: disable=import-outside-toplevel

    q_assets: dict[str, list[dict[str, Any]]]
    docx_error = ""
    if docx_question_assets_override is not None:
        q_assets = docx_question_assets_override
    else:
        q_assets, docx_error = extract_docx_question_assets(docx_path)

    conn = sqlite3.connect(str(db_path))
    try:
        rows = fetch_target_rows(
            conn,
            curriculum=curriculum,
            volume=volume,
            section=section,
            titles=titles,
            limit_records=limit_records,
        )
        persist_root = Path(root_path) / Path(persist_dir)
        if not dry_run:
            persist_root.mkdir(parents=True, exist_ok=True)
        row_results = []
        totals = {
            "processed_records": len(rows),
            "matched_records": 0,
            "copied_assets": 0,
            "source_missing": 0,
            "lookup_failed": 0,
        }

        for row in rows:
            meta = _load_metadata(row.notes)
            existing_assets = meta.get("formula_assets", [])
            if not isinstance(existing_assets, list):
                existing_assets = []
            title = _title_from_source_description(row.source_description)
            matched_docx_assets = []
            errors = []
            if docx_error:
                errors.append(docx_error)
            else:
                looked = processor._lookup_docx_question_assets(title, q_assets) if isinstance(q_assets, dict) else []
                matched_docx_assets = [a for a in (looked or []) if isinstance(a, dict) and _is_formula_asset(a)]
            if not matched_docx_assets:
                totals["lookup_failed"] += 1
            else:
                totals["matched_records"] += 1

            persisted_assets: list[dict[str, Any]] = []
            copied_assets_count = 0
            source_missing_count = 0
            sample_persistent_path = ""

            for idx, src_asset in enumerate(matched_docx_assets, start=1):
                source_rel = _candidate_source_rel(src_asset)

                safe_name = os.path.basename(source_rel).replace(" ", "_")
                target_name = f"b1_1_1_{row.id}_{idx}_{safe_name}"
                target_abs = persist_root / target_name
                target_rel = (Path(persist_dir) / target_name).as_posix()
                copied = False

                if source_rel:
                    source_abs = Path(source_rel) if os.path.isabs(source_rel) else (Path(root_path) / source_rel)
                    if source_abs.exists():
                        if not dry_run:
                            target_abs.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source_abs, target_abs)
                        copied = True
                    else:
                        zip_bytes, zip_err = _load_docx_media_bytes(docx_path, str(src_asset.get("target_ref") or ""))
                        if zip_bytes is not None:
                            if not dry_run:
                                target_abs.parent.mkdir(parents=True, exist_ok=True)
                                target_abs.write_bytes(zip_bytes)
                            copied = True
                        else:
                            source_missing_count += 1
                            errors.append(f"source_not_found: {source_abs.as_posix()}")
                            if zip_err:
                                errors.append(zip_err)
                else:
                    zip_bytes, zip_err = _load_docx_media_bytes(docx_path, str(src_asset.get("target_ref") or ""))
                    if zip_bytes is not None:
                        if not dry_run:
                            target_abs.parent.mkdir(parents=True, exist_ok=True)
                            target_abs.write_bytes(zip_bytes)
                        copied = True
                    else:
                        source_missing_count += 1
                        errors.append("source_path_missing")
                        if zip_err:
                            errors.append(zip_err)

                if copied:
                    copied_assets_count += 1
                    if not sample_persistent_path:
                        sample_persistent_path = target_rel
                    persisted_assets.append(
                        _build_persistent_asset(
                            record_id=row.id,
                            asset_index=idx,
                            source_asset=src_asset,
                            source_rel=source_rel,
                            persisted_rel=target_rel,
                        )
                    )
                else:
                    failed_asset = dict(src_asset)
                    failed_asset["persist_status"] = "source_missing"
                    failed_asset["conversion_error"] = "source_missing"
                    persisted_assets.append(failed_asset)

            totals["copied_assets"] += copied_assets_count
            totals["source_missing"] += source_missing_count

            updated_meta = dict(meta)
            if persisted_assets:
                updated_meta["formula_assets"] = _merge_formula_assets_prefer_persistent(existing_assets, persisted_assets)
            changed = _dump_metadata(updated_meta) != _dump_metadata(meta)
            if write and not dry_run and changed:
                conn.execute(
                    "UPDATE textbook_examples SET notes = ? WHERE id = ?",
                    (_dump_metadata(updated_meta), int(row.id)),
                )

            row_results.append(
                {
                    "row_id": row.id,
                    "source_description": row.source_description,
                    "existing_formula_assets_count": len(existing_assets),
                    "matched_docx_assets_count": len(matched_docx_assets),
                    "copied_assets_count": copied_assets_count,
                    "sample_persistent_path": sample_persistent_path,
                    "errors": errors,
                    "changed": changed,
                }
            )

        if write and not dry_run:
            conn.commit()

        return {
            "scope": {
                "docx": str(docx_path),
                "section": section,
                "titles": titles or [],
                "limit_records": limit_records,
                "persist_dir": str(persist_dir),
            },
            "dry_run": bool(dry_run),
            "write": bool(write),
            "docx_error": docx_error,
            "summary": totals,
            "rows": row_results,
        }
    finally:
        conn.close()


def render_markdown_report(result: dict[str, Any]) -> str:
    scope = result.get("scope", {})
    summary = result.get("summary", {})
    lines = [
        "# B1 1-1 Formula Asset Persist Dry-Run Report",
        "",
        "## Scope",
        f"- docx: `{scope.get('docx', '')}`",
        f"- section: `{scope.get('section', '')}`",
        f"- titles: `{scope.get('titles', [])}`",
        f"- limit_records: `{scope.get('limit_records')}`",
        f"- persist_dir: `{scope.get('persist_dir', '')}`",
        f"- dry_run: `{bool(result.get('dry_run'))}`",
        f"- write: `{bool(result.get('write'))}`",
    ]
    if result.get("docx_error"):
        lines.extend(["", f"- docx_error: `{result.get('docx_error')}`"])
    lines.extend(
        [
            "",
            "## Totals",
            f"- processed_records: {summary.get('processed_records', 0)}",
            f"- matched_records: {summary.get('matched_records', 0)}",
            f"- copied_assets: {summary.get('copied_assets', 0)}",
            f"- source_missing: {summary.get('source_missing', 0)}",
            f"- lookup_failed: {summary.get('lookup_failed', 0)}",
            "",
            "## Per-Record",
        ]
    )
    for row in result.get("rows", []):
        lines.extend(
            [
                f"### id={row.get('row_id')} `{row.get('source_description', '')}`",
                f"- existing_formula_assets_count: {row.get('existing_formula_assets_count', 0)}",
                f"- matched_docx_assets_count: {row.get('matched_docx_assets_count', 0)}",
                f"- copied_assets_count: {row.get('copied_assets_count', 0)}",
                f"- sample_persistent_path: `{row.get('sample_persistent_path', '')}`",
                f"- errors: `{'; '.join(row.get('errors', []))}`",
                "",
            ]
        )
    if not result.get("rows"):
        lines.append("- no matching records")
    return "\n".join(lines)


def write_report(result: dict[str, Any], report_path: str | Path) -> Path:
    path = Path(report_path)
    if not path.is_absolute():
        path = project_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown_report(result), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist B1 1-1 formula assets to stable storage.")
    parser.add_argument("--db", default=str(default_db_path()))
    parser.add_argument("--docx", required=True, help="Path to original B1 1-1 docx file.")
    parser.add_argument("--section", default="1-1 數線與絕對值")
    parser.add_argument("--title", action="append", dest="titles", default=[], help="Filter source_description prefix; repeatable.")
    parser.add_argument("--limit-records", type=int, default=None)
    parser.add_argument("--persist-dir", default=str(DEFAULT_PERSIST_DIR))
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--write", action="store_true", help="Write updated metadata.formula_assets to DB.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    args = parser.parse_args()

    dry_run = not bool(args.write)
    result = run_persist(
        db_path=args.db,
        docx_path=args.docx,
        root_path=project_root(),
        section=args.section,
        titles=list(args.titles or []),
        limit_records=args.limit_records,
        persist_dir=args.persist_dir,
        dry_run=dry_run,
        write=bool(args.write),
    )
    report_path = write_report(result, args.report)
    print(render_markdown_report(result))
    print(f"\nReport written: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
