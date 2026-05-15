#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dry-run conversion for B1 1-1 formula vector assets (WMF/EMF -> PNG)."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


VECTOR_FORMATS = {"wmf", "emf"}
DEFAULT_REPORT_PATH = Path("reports/b1_import_debug/b1_1_1_formula_asset_conversion_dry_run_report.md")
DEFAULT_CONVERTED_DIR = Path("uploads/tmp_formula_asset_conversion")


@dataclass
class ConversionRow:
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


def _load_metadata(notes: str) -> dict[str, Any]:
    if not str(notes or "").strip():
        return {}
    try:
        parsed = json.loads(notes)
        return parsed if isinstance(parsed, dict) else {"raw": notes}
    except Exception:
        return {}


def _dump_metadata(meta: dict[str, Any]) -> str:
    return json.dumps(meta, ensure_ascii=False, sort_keys=True)


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
    if "wmf" in ctype:
        return "wmf"
    if "emf" in ctype:
        return "emf"
    return original or "unknown"


def _is_vector_asset(asset: dict[str, Any]) -> bool:
    return _asset_format(asset) in VECTOR_FORMATS


def _is_tmp_path(path_value: str) -> bool:
    return "tmp_docx_media" in str(path_value or "").replace("\\", "/").lower()


def _asset_dedupe_key(asset: dict[str, Any]) -> str:
    h = str(asset.get("asset_hash") or "").strip()
    if h:
        return f"hash:{h}"
    token = str(asset.get("placeholder_token") or "").strip()
    rid = str(asset.get("rid") or "").strip()
    base = os.path.basename(str(asset.get("path") or asset.get("original_path") or "")).strip()
    fmt = str(asset.get("original_format") or "").strip().lower()
    return f"fallback:{token}|{rid}|{base}|{fmt}"


def _asset_priority(asset: dict[str, Any]) -> int:
    score = 0
    if str(asset.get("persist_status") or "").lower() == "persisted":
        score += 100
    src_candidates = [str(asset.get(k) or "") for k in ("path", "original_path", "display_path")]
    non_tmp_count = sum(1 for p in src_candidates if p and not _is_tmp_path(p))
    tmp_count = sum(1 for p in src_candidates if p and _is_tmp_path(p))
    score += 30 * non_tmp_count
    score -= 30 * tmp_count
    if str(asset.get("path") or ""):
        score += 5
    return score


def _select_assets_for_conversion(assets: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for asset in assets:
        grouped.setdefault(_asset_dedupe_key(asset), []).append(asset)

    selected: list[dict[str, Any]] = []
    duplicate_hash_tmp_vs_persistent = 0
    for _k, group in grouped.items():
        has_tmp = any(_is_tmp_path(str(a.get("path") or a.get("original_path") or "")) for a in group)
        has_persistent = any(not _is_tmp_path(str(a.get("path") or a.get("original_path") or "")) for a in group)
        if has_tmp and has_persistent:
            duplicate_hash_tmp_vs_persistent += 1
        chosen = sorted(group, key=_asset_priority, reverse=True)[0]
        selected.append(chosen)

    stats = {
        "count_tmp_path_assets": sum(1 for a in assets if _is_tmp_path(str(a.get("path") or a.get("original_path") or ""))),
        "count_persistent_assets": sum(1 for a in assets if not _is_tmp_path(str(a.get("path") or a.get("original_path") or ""))),
        "duplicate_hash_tmp_vs_persistent": duplicate_hash_tmp_vs_persistent,
        "selected_persistent_assets": sum(1 for a in selected if not _is_tmp_path(str(a.get("path") or a.get("original_path") or ""))),
        "selected_tmp_assets": sum(1 for a in selected if _is_tmp_path(str(a.get("path") or a.get("original_path") or ""))),
    }
    return selected, stats


def _pick_vector_source_rel(asset: dict[str, Any]) -> str:
    # old_temp_path is debug only and must NOT be a primary source.
    for key in ("path", "original_path", "display_path"):
        rel = str(asset.get(key) or "").strip()
        if rel and not _is_tmp_path(rel):
            return rel
    for key in ("path", "original_path", "display_path"):
        rel = str(asset.get(key) or "").strip()
        if rel:
            return rel
    return ""


def _default_converter(input_path: str, output_path: str) -> tuple[bool, str | None]:
    try:
        sys.path.insert(0, str(project_root()))
        from core.question_image_assets import convert_vector_image_to_png  # pylint: disable=import-outside-toplevel

        return convert_vector_image_to_png(input_path, output_path)
    except Exception as exc:  # Converter import/runtime must not crash dry-run.
        return False, f"converter_unavailable: {exc}"


def _safe_convert(
    *,
    root_path: Path,
    row_id: int,
    asset_index: int,
    source_rel: str,
    converted_dir: Path,
    converter: Callable[[str, str], tuple[bool, str | None]],
) -> tuple[bool, str, str]:
    source_abs = Path(source_rel) if os.path.isabs(source_rel) else (root_path / source_rel)
    if not source_abs.exists():
        return False, "", f"source_not_found: {source_abs.as_posix()}"
    target_dir_abs = root_path / converted_dir
    target_dir_abs.mkdir(parents=True, exist_ok=True)
    source_stem = Path(source_rel).stem or "asset"
    output_name = f"tbex_{row_id}_{source_stem}_{asset_index}.png"
    output_abs = target_dir_abs / output_name
    ok, err = converter(str(source_abs), str(output_abs))
    if ok and output_abs.exists():
        return True, str((converted_dir / output_name).as_posix()), ""
    return False, "", str(err or "conversion_failed")


def process_row(
    row: ConversionRow,
    *,
    root_path: str | Path,
    dry_run: bool,
    remaining_asset_budget: int | None,
    converter: Callable[[str, str], tuple[bool, str | None]] | None = None,
    converted_dir: str | Path = DEFAULT_CONVERTED_DIR,
) -> dict[str, Any]:
    root = Path(root_path)
    convert_fn = converter or _default_converter
    converted_dir_path = Path(converted_dir)

    meta = _load_metadata(row.notes)
    assets = meta.get("formula_assets", [])
    if not isinstance(assets, list):
        assets = []
    selected_assets, select_stats = _select_assets_for_conversion([a for a in assets if isinstance(a, dict)])

    updated_assets: list[dict[str, Any]] = []
    item_summaries: list[dict[str, Any]] = []
    summary = {
        "formula_assets_count": len(assets),
        "selected_assets_count": len(selected_assets),
        "candidate_vector_assets": 0,
        "success_count": 0,
        "failed_count": 0,
        "skipped_non_vector": 0,
        "skipped_missing_path": 0,
        "count_tmp_path_assets": int(select_stats.get("count_tmp_path_assets", 0)),
        "count_persistent_assets": int(select_stats.get("count_persistent_assets", 0)),
        "duplicate_hash_tmp_vs_persistent": int(select_stats.get("duplicate_hash_tmp_vs_persistent", 0)),
        "selected_persistent_assets": int(select_stats.get("selected_persistent_assets", 0)),
        "selected_tmp_assets": int(select_stats.get("selected_tmp_assets", 0)),
        "sample_converted_path": "",
        "sample_error": "",
    }

    local_budget = None if remaining_asset_budget is None else int(max(remaining_asset_budget, 0))
    for idx, next_asset in enumerate(selected_assets, start=1):
        next_asset = dict(next_asset)
        item_status = ""
        converted_path = ""
        conversion_error = ""

        if not _is_vector_asset(next_asset):
            summary["skipped_non_vector"] += 1
            item_status = "skipped_non_vector"
        elif local_budget is not None and local_budget <= 0:
            item_status = "skipped_limit"
        else:
            summary["candidate_vector_assets"] += 1
            if local_budget is not None:
                local_budget -= 1
            source_rel = _pick_vector_source_rel(next_asset)
            if not source_rel:
                summary["failed_count"] += 1
                summary["skipped_missing_path"] += 1
                item_status = "skipped_missing_path"
                conversion_error = "missing_vector_path"
                next_asset["conversion_status"] = "failed"
                next_asset["conversion_error"] = conversion_error
            else:
                ok, converted_rel, err = _safe_convert(
                    root_path=root,
                    row_id=row.id,
                    asset_index=idx,
                    source_rel=source_rel,
                    converted_dir=converted_dir_path,
                    converter=convert_fn,
                )
                if ok:
                    summary["success_count"] += 1
                    item_status = "success"
                    converted_path = converted_rel
                    next_asset["conversion_status"] = "success"
                    next_asset["converted_path"] = converted_rel
                    next_asset["readable_after_conversion"] = True
                    if not summary["sample_converted_path"]:
                        summary["sample_converted_path"] = converted_rel
                else:
                    summary["failed_count"] += 1
                    item_status = "failed"
                    conversion_error = err
                    next_asset["conversion_status"] = "failed"
                    next_asset["conversion_error"] = conversion_error
                    if not summary["sample_error"]:
                        summary["sample_error"] = conversion_error

        updated_assets.append(next_asset)
        item_summaries.append(
            {
                "id": row.id,
                "source_description": row.source_description,
                "placeholder_token": next_asset.get("placeholder_token", ""),
                "asset_path": next_asset.get("path", ""),
                "original_path": next_asset.get("original_path", ""),
                "conversion_status": next_asset.get("conversion_status", item_status),
                "converted_path": next_asset.get("converted_path", converted_path),
                "conversion_error": next_asset.get("conversion_error", conversion_error),
                "item_status": item_status,
            }
        )

    updated_meta = dict(meta)
    updated_meta["formula_assets"] = updated_assets
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
        "consumed_candidates": int(summary["candidate_vector_assets"]),
    }


def fetch_target_rows(
    conn: sqlite3.Connection,
    *,
    curriculum: str,
    volume: str,
    section: str,
    titles: list[str] | None,
    limit_records: int | None,
) -> list[ConversionRow]:
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
        ConversionRow(
            id=int(r["id"]),
            source_description=str(r["source_description"] or ""),
            problem_text=str(r["problem_text"] or ""),
            notes=str(r["notes"] or ""),
        )
        for r in rows
    ]


def run_conversion(
    *,
    db_path: str | Path,
    root_path: str | Path,
    curriculum: str = "vocational",
    volume: str = "數學B1",
    section: str = "1-1 數線與絕對值",
    titles: list[str] | None = None,
    limit_records: int | None = None,
    limit_assets: int | None = None,
    dry_run: bool = True,
    write_converted_path: bool = False,
    converter: Callable[[str, str], tuple[bool, str | None]] | None = None,
    converted_dir: str | Path = DEFAULT_CONVERTED_DIR,
) -> dict[str, Any]:
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
        remaining = None if limit_assets is None else int(max(limit_assets, 0))
        row_results = []
        for row in rows:
            row_result = process_row(
                row,
                root_path=root_path,
                dry_run=dry_run,
                remaining_asset_budget=remaining,
                converter=converter,
                converted_dir=converted_dir,
            )
            row_results.append(row_result)
            if remaining is not None:
                remaining = max(0, remaining - int(row_result.get("consumed_candidates", 0)))

        if write_converted_path and not dry_run:
            for result in row_results:
                conn.execute(
                    "UPDATE textbook_examples SET notes = ? WHERE id = ?",
                    (_dump_metadata(result["metadata_after"]), int(result["row_id"])),
                )
            conn.commit()

        totals = {
            "processed_records": len(row_results),
            "candidate_assets": 0,
            "conversion_success": 0,
            "conversion_failed": 0,
            "skipped_non_vector": 0,
            "skipped_missing_path": 0,
            "count_tmp_path_assets": 0,
            "count_persistent_assets": 0,
            "duplicate_hash_tmp_vs_persistent": 0,
            "selected_persistent_assets": 0,
            "selected_tmp_assets": 0,
        }
        for result in row_results:
            s = result.get("summary", {})
            totals["candidate_assets"] += int(s.get("candidate_vector_assets", 0))
            totals["conversion_success"] += int(s.get("success_count", 0))
            totals["conversion_failed"] += int(s.get("failed_count", 0))
            totals["skipped_non_vector"] += int(s.get("skipped_non_vector", 0))
            totals["skipped_missing_path"] += int(s.get("skipped_missing_path", 0))
            totals["count_tmp_path_assets"] += int(s.get("count_tmp_path_assets", 0))
            totals["count_persistent_assets"] += int(s.get("count_persistent_assets", 0))
            totals["duplicate_hash_tmp_vs_persistent"] += int(s.get("duplicate_hash_tmp_vs_persistent", 0))
            totals["selected_persistent_assets"] += int(s.get("selected_persistent_assets", 0))
            totals["selected_tmp_assets"] += int(s.get("selected_tmp_assets", 0))

        return {
            "scope": {
                "curriculum": curriculum,
                "volume": volume,
                "section": section,
                "titles": titles or [],
                "limit_records": limit_records,
                "limit_assets": limit_assets,
            },
            "dry_run": bool(dry_run),
            "write_converted_path": bool(write_converted_path),
            "summary": totals,
            "rows": row_results,
        }
    finally:
        conn.close()


def render_markdown_report(result: dict[str, Any]) -> str:
    scope = result.get("scope", {})
    summary = result.get("summary", {})
    lines = [
        "# B1 1-1 Formula Asset Conversion Dry-Run Report",
        "",
        "## Scope",
        f"- section: `{scope.get('section', '')}`",
        f"- titles: `{scope.get('titles', [])}`",
        f"- limit_records: `{scope.get('limit_records')}`",
        f"- limit_assets: `{scope.get('limit_assets')}`",
        f"- dry_run: `{bool(result.get('dry_run'))}`",
        f"- write_converted_path: `{bool(result.get('write_converted_path'))}`",
        "",
        "## Totals",
        f"- processed_records: {summary.get('processed_records', 0)}",
        f"- candidate_assets: {summary.get('candidate_assets', 0)}",
        f"- conversion_success: {summary.get('conversion_success', 0)}",
        f"- conversion_failed: {summary.get('conversion_failed', 0)}",
        f"- skipped_non_vector: {summary.get('skipped_non_vector', 0)}",
        f"- skipped_missing_path: {summary.get('skipped_missing_path', 0)}",
        f"- count_tmp_path_assets: {summary.get('count_tmp_path_assets', 0)}",
        f"- count_persistent_assets: {summary.get('count_persistent_assets', 0)}",
        f"- duplicate_hash_tmp_vs_persistent: {summary.get('duplicate_hash_tmp_vs_persistent', 0)}",
        f"- selected_persistent_assets: {summary.get('selected_persistent_assets', 0)}",
        f"- selected_tmp_assets: {summary.get('selected_tmp_assets', 0)}",
        "",
        "## Per-Record",
    ]
    rows = result.get("rows", [])
    if not rows:
        lines.append("- no matching records")
        return "\n".join(lines) + "\n"
    for row in rows:
        s = row.get("summary", {})
        lines.extend(
            [
                f"### id={row.get('row_id')} `{row.get('source_description', '')}`",
                f"- formula_assets_count: {s.get('formula_assets_count', 0)}",
                f"- selected_assets_count: {s.get('selected_assets_count', 0)}",
                f"- candidate_vector_assets: {s.get('candidate_vector_assets', 0)}",
                f"- selected_persistent_assets: {s.get('selected_persistent_assets', 0)}",
                f"- selected_tmp_assets: {s.get('selected_tmp_assets', 0)}",
                f"- success_count: {s.get('success_count', 0)}",
                f"- failed_count: {s.get('failed_count', 0)}",
                f"- sample_converted_path: `{s.get('sample_converted_path', '')}`",
                f"- sample_error: `{s.get('sample_error', '')}`",
                "",
            ]
        )
    return "\n".join(lines)


def write_report(result: dict[str, Any], report_path: str | Path) -> Path:
    path = Path(report_path)
    if not path.is_absolute():
        path = project_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown_report(result), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run convert B1 1-1 formula vector assets to PNG.")
    parser.add_argument("--db", default=str(default_db_path()))
    parser.add_argument("--curriculum", default="vocational")
    parser.add_argument("--volume", default="數學B1")
    parser.add_argument("--section", default="1-1 數線與絕對值")
    parser.add_argument("--title", action="append", dest="titles", default=[], help="Filter source_description prefix; repeatable.")
    parser.add_argument("--limit-records", type=int, default=None)
    parser.add_argument("--limit-assets", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--write-converted-path", action="store_true", help="Write conversion metadata to DB notes.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    args = parser.parse_args()

    dry_run = not bool(args.write_converted_path)
    result = run_conversion(
        db_path=args.db,
        root_path=project_root(),
        curriculum=args.curriculum,
        volume=args.volume,
        section=args.section,
        titles=list(args.titles or []),
        limit_records=args.limit_records,
        limit_assets=args.limit_assets,
        dry_run=dry_run,
        write_converted_path=bool(args.write_converted_path),
    )
    report_path = write_report(result, args.report)
    print(render_markdown_report(result))
    print(f"\nReport written: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
