#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B1 1-1 import state diagnosis (read-only, no Gemini, no DB write)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from sqlalchemy import or_

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import create_app
import core.textbook_processor as processor
from models import TextbookExample


DEFAULT_DOCX = r"H:\我的雲端硬碟\Python\books\技高\龍騰數B 第一冊(分章節)\第一章 1-1 數線與絕對值-課本.docx"
DEFAULT_REPORT = "reports/b1_import_debug/b1_1_1_import_state_diagnosis.md"

TARGET_LOOKUP_TITLES = [
    "例題1",
    "例題2",
    "例題4",
    "1-1習題 基礎題5",
    "1-1習題 基礎題10",
]

EXPECTED_TITLES = [
    "例題1", "例題2", "例題3", "例題4",
    "隨堂練習1", "隨堂練習2", "隨堂練習3", "隨堂練習4",
    "1-1習題 基礎題1", "1-1習題 基礎題2", "1-1習題 基礎題3", "1-1習題 基礎題4",
    "1-1習題 基礎題5", "1-1習題 基礎題6", "1-1習題 基礎題7", "1-1習題 基礎題8",
    "1-1習題 基礎題9", "1-1習題 基礎題10",
    "111統測B",
    "動動手1", "動動手2",
]


class _Queue:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def put(self, msg: str) -> None:
        self.messages.append(str(msg))


def _norm(text: str) -> str:
    t = re.sub(r"\s+", "", str(text or "").strip())
    t = re.sub(r"^例(?!題)(\d+)$", r"例題\1", t)
    return t


def _title_from_source_description(sd: str) -> str:
    return str(sd or "").split(" [", 1)[0].strip()


def _extract_dedupe_hash(source_description: str) -> str:
    m = re.search(r"dedupe=([0-9a-fA-F]+)", str(source_description or ""))
    return m.group(1) if m else ""


def _load_meta(notes: str) -> dict[str, Any]:
    if isinstance(notes, str) and notes.strip():
        try:
            parsed = json.loads(notes)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {}
    return {}


def _is_target_title(title: str) -> bool:
    nt = _norm(title)
    expect_norm = {_norm(x) for x in EXPECTED_TITLES}
    if nt in expect_norm:
        return True
    if nt.startswith("1-1習題基礎題"):
        m = re.search(r"1-1習題基礎題(\d+)$", nt)
        if m and 1 <= int(m.group(1)) <= 10:
            return True
    return False


def run_docx_layer(app, docx_path: Path) -> dict[str, Any]:
    result = {
        "docx_missing": False,
        "docx_formula_asset_total": 0,
        "docx_question_asset_keys_count": 0,
        "docx_key_startswith_liti1": False,
        "docx_has_key_1_1_exercise": False,
        "lookup": {},
    }
    for title in TARGET_LOOKUP_TITLES:
        result["lookup"][title] = {
            "found_assets_count": 0,
            "formula_assets_count": 0,
            "mapping_status": "lookup_failed",
        }

    if not docx_path.exists():
        result["docx_missing"] = True
        return result

    q = _Queue()
    with app.app_context():
        processor.extract_content_from_file(str(docx_path), q)
        ctx = getattr(processor, "_DOCX_IMPORT_CONTEXT", {}) or {}
        q_assets = ctx.get("question_assets", {}) if isinstance(ctx, dict) else {}
        formula_blocks = ctx.get("question_formula_blocks", {}) if isinstance(ctx, dict) else {}

    keys = list(q_assets.keys()) if isinstance(q_assets, dict) else []
    result["docx_question_asset_keys_count"] = len(keys)
    result["docx_key_startswith_liti1"] = any(_norm(k).startswith("例1") or _norm(k).startswith("例題1") for k in keys)
    result["docx_has_key_1_1_exercise"] = any(_norm(k) == "1-1習題" for k in keys)
    result["docx_formula_asset_total"] = sum(
        1
        for arr in (q_assets.values() if isinstance(q_assets, dict) else [])
        for a in (arr or [])
        if str(a.get("media_kind", "")) == "formula_asset"
    )

    for title in TARGET_LOOKUP_TITLES:
        assets = processor._lookup_docx_question_assets(title, q_assets) or []
        fas = [a for a in assets if str(a.get("media_kind", "")) == "formula_asset"]
        mapping_status = "lookup_failed"
        if assets:
            mapping_status = str(assets[0].get("mapping_status") or "exact_or_default")
        if not fas:
            rb = processor._lookup_docx_formula_block(title, formula_blocks)
            if rb:
                mapping_status = "raw_block_only"
        result["lookup"][title] = {
            "found_assets_count": len(assets),
            "formula_assets_count": len(fas),
            "mapping_status": mapping_status,
        }
    return result


def run_db_layer(app) -> dict[str, Any]:
    expected_norm = {_norm(x) for x in EXPECTED_TITLES}
    rows_out = []
    with app.app_context():
        rows = (
            TextbookExample.query
            .filter(
                TextbookExample.source_curriculum == "vocational",
                TextbookExample.source_volume == "數學B1",
                or_(
                    TextbookExample.source_section == "1-1 數線與絕對值",
                    TextbookExample.source_description.like("%1-1習題%"),
                    TextbookExample.source_description.like("%例題%"),
                    TextbookExample.source_description.like("%隨堂練習%"),
                    TextbookExample.source_description.like("%111統測B%"),
                    TextbookExample.source_description.like("%動動手%"),
                ),
            )
            .all()
        )
        for row in rows:
            title = _title_from_source_description(getattr(row, "source_description", ""))
            if not _is_target_title(title):
                continue
            problem_text = str(getattr(row, "problem_text", "") or "")
            meta = _load_meta(getattr(row, "notes", "") or "")
            formula_assets = meta.get("formula_assets", []) if isinstance(meta, dict) else []
            first_keys = []
            if isinstance(formula_assets, list) and formula_assets and isinstance(formula_assets[0], dict):
                first_keys = sorted(list(formula_assets[0].keys()))
            rows_out.append(
                {
                    "id": int(getattr(row, "id", 0) or 0),
                    "skill_id": str(getattr(row, "skill_id", "") or ""),
                    "source_description": str(getattr(row, "source_description", "") or ""),
                    "title": title,
                    "problem_preview": problem_text[:80].replace("\n", " "),
                    "has_formula_image": bool(re.search(r"\[FORMULA_IMAGE_\d+\]", problem_text)),
                    "has_formula_missing": "[FORMULA_MISSING]" in problem_text,
                    "metadata_exists": bool(meta),
                    "formula_assets_count": len(formula_assets) if isinstance(formula_assets, list) else 0,
                    "first_formula_asset_keys": first_keys,
                    "needs_review": bool(meta.get("needs_review") is True),
                    "needs_formula_review": bool(meta.get("needs_formula_review") is True),
                    "formula_missing": bool(meta.get("formula_missing") is True),
                    "dedupe_hash": _extract_dedupe_hash(str(getattr(row, "source_description", "") or "")),
                }
            )

    total_records = len(rows_out)
    records_with_formula_image_placeholder = sum(1 for r in rows_out if r["has_formula_image"])
    records_with_formula_missing = sum(1 for r in rows_out if r["has_formula_missing"])
    records_with_formula_assets = sum(1 for r in rows_out if r["formula_assets_count"] > 0)
    total_formula_assets = sum(int(r["formula_assets_count"]) for r in rows_out)
    records_needing_formula_review = sum(1 for r in rows_out if r["needs_formula_review"])

    present_norm = {_norm(r["title"]) for r in rows_out}
    missing_expected_titles = [t for t in EXPECTED_TITLES if _norm(t) not in present_norm]

    sd_counter = Counter([r["source_description"] for r in rows_out])
    duplicate_source_descriptions = sorted([k for k, v in sd_counter.items() if v > 1])

    # Layer C diagnosis flags
    pt_image_but_meta_missing = [
        r for r in rows_out if r["has_formula_image"] and r["formula_assets_count"] == 0
    ]
    metadata_ok_frontend_not_rendering = [
        r for r in rows_out if r["formula_assets_count"] > 0 and (r["has_formula_image"] or r["has_formula_missing"])
    ]

    return {
        "rows": rows_out,
        "total_records": total_records,
        "expected_title_count": len(EXPECTED_TITLES),
        "missing_expected_titles": missing_expected_titles,
        "duplicate_source_descriptions": duplicate_source_descriptions,
        "records_with_formula_image_placeholder": records_with_formula_image_placeholder,
        "records_with_formula_missing": records_with_formula_missing,
        "records_with_formula_assets": records_with_formula_assets,
        "total_formula_assets": total_formula_assets,
        "records_needing_formula_review": records_needing_formula_review,
        "problem_text_updated_but_metadata_missing": pt_image_but_meta_missing,
        "metadata_ok_frontend_not_rendering": metadata_ok_frontend_not_rendering,
    }


def build_verdict(db_layer: dict[str, Any]) -> tuple[str, str]:
    if db_layer["problem_text_updated_but_metadata_missing"]:
        return (
            "CASE 1: metadata missing",
            "修 _merge_duplicate_existing_record 的 metadata 寫入/attach_image_metadata 流程",
        )
    if db_layer["duplicate_source_descriptions"]:
        return (
            "CASE 3: duplicate records exist",
            "先修 scoped clear 或 dedupe key 清理策略，避免同 source_description 多筆常駐",
        )
    if db_layer["missing_expected_titles"]:
        return (
            "CASE 4: expected titles missing",
            "修 intra-import dedupe/parse validation，先保證 1-1 目標題全數存在",
        )
    if db_layer["records_with_formula_assets"] > 0 and db_layer["records_with_formula_missing"] > 0:
        return (
            "CASE 5: placeholders remain but metadata exists",
            "importer 先不動，下一步走 OCR/backfill 或前台輔助顯示 metadata",
        )
    if db_layer["records_with_formula_assets"] > 0:
        return (
            "CASE 2: metadata exists but frontend not showing",
            "修 /examples 前台 metadata badge/render（非 importer）",
        )
    return (
        "CASE 1: metadata missing",
        "優先修 metadata merge 寫入路徑",
    )


def write_report(path: Path, docx_layer: dict[str, Any], db_layer: dict[str, Any], verdict: str, next_fix: str) -> None:
    lines = []
    lines.append("# B1 1-1 Import State Diagnosis")
    lines.append("")
    lines.append("- Gemini: not called")
    lines.append("- DB write: not performed")
    lines.append("- DB schema: unchanged")
    lines.append("")
    lines.append("## A. DOCX Dry-Run Layer")
    lines.append(f"- docx_missing: `{docx_layer['docx_missing']}`")
    lines.append(f"- docx_formula_asset_total: `{docx_layer['docx_formula_asset_total']}`")
    lines.append(f"- docx_question_asset_keys_count: `{docx_layer['docx_question_asset_keys_count']}`")
    lines.append(f"- has_key_startswith_例1: `{docx_layer['docx_key_startswith_liti1']}`")
    lines.append(f"- has_key_1-1習題: `{docx_layer['docx_has_key_1_1_exercise']}`")
    for t in TARGET_LOOKUP_TITLES:
        r = docx_layer["lookup"][t]
        lines.append(f"- lookup `{t}`: found_assets={r['found_assets_count']}, formula_assets={r['formula_assets_count']}, mapping_status={r['mapping_status']}")
    lines.append("")
    lines.append("## B. DB Layer")
    lines.append(f"- total_records: `{db_layer['total_records']}`")
    lines.append(f"- expected_title_count: `{db_layer['expected_title_count']}`")
    lines.append(f"- missing_expected_titles: `{db_layer['missing_expected_titles']}`")
    lines.append(f"- duplicate_source_descriptions: `{db_layer['duplicate_source_descriptions']}`")
    lines.append(f"- records_with_formula_image_placeholder: `{db_layer['records_with_formula_image_placeholder']}`")
    lines.append(f"- records_with_formula_missing: `{db_layer['records_with_formula_missing']}`")
    lines.append(f"- records_with_formula_assets: `{db_layer['records_with_formula_assets']}`")
    lines.append(f"- total_formula_assets: `{db_layer['total_formula_assets']}`")
    lines.append(f"- records_needing_formula_review: `{db_layer['records_needing_formula_review']}`")
    lines.append("")
    lines.append("### DB Rows")
    if not db_layer["rows"]:
        lines.append("- (no matched records)")
    else:
        for r in sorted(db_layer["rows"], key=lambda x: (x["title"], x["id"])):
            lines.append(
                f"- id={r['id']}, skill_id=`{r['skill_id']}`, source_description=`{r['source_description']}`, "
                f"problem_preview=`{r['problem_preview']}`, has_FORMULA_IMAGE={r['has_formula_image']}, "
                f"has_FORMULA_MISSING={r['has_formula_missing']}, metadata_exists={r['metadata_exists']}, "
                f"formula_assets_count={r['formula_assets_count']}, first_formula_asset_keys={r['first_formula_asset_keys']}, "
                f"needs_review={r['needs_review']}, needs_formula_review={r['needs_formula_review']}, "
                f"formula_missing={r['formula_missing']}, dedupe={r['dedupe_hash']}"
            )
    lines.append("")
    lines.append("## C. Merge Effect Diagnosis")
    lines.append(f"- problem_text_updated_but_metadata_missing: `{len(db_layer['problem_text_updated_but_metadata_missing'])}`")
    lines.append(f"- metadata_ok_frontend_not_rendering: `{len(db_layer['metadata_ok_frontend_not_rendering'])}`")
    lines.append(f"- duplicate_records_still_exist: `{bool(db_layer['duplicate_source_descriptions'])}`")
    lines.append(f"- missing_expected_titles: `{bool(db_layer['missing_expected_titles'])}`")
    lines.append("")
    lines.append("## D. Summary Counter Scope Check")
    if db_layer["records_with_formula_assets"] > 0:
        lines.append("- summary_bug_candidate: `True` (若匯入 log 顯示 formula_assets=0，可能只計 inserted 未計 updated_duplicates)")
    else:
        lines.append("- summary_bug_candidate: `False`")
    lines.append("")
    lines.append("## E. Verdict")
    lines.append(f"- verdict: `{verdict}`")
    lines.append(f"- next_unique_fix_point: `{next_fix}`")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose B1 1-1 import state without Gemini/DB write.")
    parser.add_argument("--docx", default=DEFAULT_DOCX, help="DOCX path for dry-run asset check")
    parser.add_argument("--report", default=DEFAULT_REPORT, help="Markdown report output path")
    args = parser.parse_args()

    app = create_app()
    app.config["ENABLE_DOCX_FORMULA_OCR_FALLBACK"] = False

    docx_layer = run_docx_layer(app, Path(args.docx))
    db_layer = run_db_layer(app)
    verdict, next_fix = build_verdict(db_layer)
    report_path = (REPO_ROOT / args.report).resolve()
    write_report(report_path, docx_layer, db_layer, verdict, next_fix)

    print("DIAGNOSIS RESULT:")
    print(f"- docx_formula_asset_total={docx_layer['docx_formula_asset_total']}")
    print(f"- db_total_records={db_layer['total_records']}")
    print(f"- records_with_formula_assets={db_layer['records_with_formula_assets']}")
    print(f"- total_formula_assets={db_layer['total_formula_assets']}")
    print(f"- records_with_formula_missing={db_layer['records_with_formula_missing']}")
    print(f"- missing_expected_titles={db_layer['missing_expected_titles']}")
    print(f"- duplicate_source_descriptions={db_layer['duplicate_source_descriptions']}")
    print(f"- verdict={verdict}")
    print(f"report={report_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
