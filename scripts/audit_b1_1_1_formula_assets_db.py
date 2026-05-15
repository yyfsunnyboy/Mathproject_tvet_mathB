#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit B1 1-1 textbook_examples formula-asset metadata (read-only)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import create_app
from models import TextbookExample


EXPECTED_TITLES = [
    "例題1",
    "例題2",
    "例題3",
    "例題4",
    "隨堂練習1",
    "隨堂練習2",
    "隨堂練習3",
    "隨堂練習4",
    "1-1習題 基礎題1",
    "1-1習題 基礎題2",
    "1-1習題 基礎題3",
    "1-1習題 基礎題4",
    "1-1習題 基礎題5",
    "1-1習題 基礎題6",
    "1-1習題 基礎題7",
    "1-1習題 基礎題8",
    "1-1習題 基礎題9",
    "1-1習題 基礎題10",
    "111統測B",
    "動動手1",
    "動動手2",
]


def _norm(text: str) -> str:
    t = re.sub(r"\s+", "", str(text or "").strip())
    t = re.sub(r"^例(?!題)(\d+)$", r"例題\1", t)
    return t


def _title_from_source_description(sd: str) -> str:
    return str(sd or "").split(" [", 1)[0].strip()


def _load_meta(notes: str):
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
    expected_norm = {_norm(x) for x in EXPECTED_TITLES}
    if nt in expected_norm:
        return True
    if nt.startswith("1-1習題基礎題"):
        m = re.search(r"1-1習題基礎題(\d+)$", nt)
        if m and 1 <= int(m.group(1)) <= 10:
            return True
    return False


def _bool(v) -> bool:
    return bool(v is True)


def main() -> int:
    report_path = REPO_ROOT / "reports" / "b1_import_debug" / "b1_1_1_formula_assets_db_audit.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    app = create_app()
    rows_out = []
    with app.app_context():
        all_rows = (
            TextbookExample.query
            .filter_by(source_curriculum="vocational", source_volume="數學B1", source_section="1-1 數線與絕對值")
            .all()
        )
        for row in all_rows:
            title = _title_from_source_description(getattr(row, "source_description", ""))
            if not _is_target_title(title):
                continue
            problem_text = str(getattr(row, "problem_text", "") or "")
            meta = _load_meta(getattr(row, "notes", "") or "")
            formula_assets = meta.get("formula_assets", []) if isinstance(meta, dict) else []
            rows_out.append(
                {
                    "id": row.id,
                    "skill_id": str(getattr(row, "skill_id", "") or ""),
                    "source_description": str(getattr(row, "source_description", "") or ""),
                    "title": title,
                    "has_formula_image_placeholder": bool(re.search(r"\[FORMULA_IMAGE_\d+\]", problem_text)),
                    "has_formula_missing": "[FORMULA_MISSING]" in problem_text,
                    "has_metadata": bool(meta),
                    "formula_assets_count": len(formula_assets) if isinstance(formula_assets, list) else 0,
                    "needs_review": _bool(meta.get("needs_review")) if isinstance(meta, dict) else False,
                    "needs_formula_review": _bool(meta.get("needs_formula_review")) if isinstance(meta, dict) else False,
                    "formula_missing": _bool(meta.get("formula_missing")) if isinstance(meta, dict) else False,
                }
            )

    total_records = len(rows_out)
    records_with_formula_image_placeholder = sum(1 for r in rows_out if r["has_formula_image_placeholder"])
    records_with_formula_missing = sum(1 for r in rows_out if r["has_formula_missing"])
    records_with_formula_assets = sum(1 for r in rows_out if r["formula_assets_count"] > 0)
    total_formula_assets = sum(int(r["formula_assets_count"]) for r in rows_out)
    records_needing_formula_review = sum(1 for r in rows_out if r["needs_formula_review"])

    present_titles_norm = {_norm(r["title"]) for r in rows_out}
    missing_expected_titles = [t for t in EXPECTED_TITLES if _norm(t) not in present_titles_norm]

    lines = []
    lines.append("# B1 1-1 textbook_examples Formula Assets DB Audit")
    lines.append("")
    lines.append("- Gemini: not called")
    lines.append("- DB write: not performed")
    lines.append("- DB schema: unchanged")
    lines.append("")
    lines.append("## Statistics")
    lines.append(f"- total_records: `{total_records}`")
    lines.append(f"- records_with_formula_image_placeholder: `{records_with_formula_image_placeholder}`")
    lines.append(f"- records_with_formula_missing: `{records_with_formula_missing}`")
    lines.append(f"- records_with_formula_assets: `{records_with_formula_assets}`")
    lines.append(f"- total_formula_assets: `{total_formula_assets}`")
    lines.append(f"- records_needing_formula_review: `{records_needing_formula_review}`")
    lines.append(f"- missing_expected_titles: `{missing_expected_titles}`")
    lines.append("")
    lines.append("## Rows")
    if not rows_out:
        lines.append("- (no matched records)")
    else:
        for r in sorted(rows_out, key=lambda x: (x["title"], x["id"])):
            lines.append(
                "- id={id}, skill_id=`{skill_id}`, source_description=`{source_description}`, "
                "has_formula_image={has_formula_image_placeholder}, has_formula_missing={has_formula_missing}, "
                "has_metadata={has_metadata}, formula_assets_count={formula_assets_count}, "
                "needs_review={needs_review}, needs_formula_review={needs_formula_review}, formula_missing={formula_missing}".format(**r)
            )
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"report={report_path.as_posix()}")
    print(f"total_records={total_records}")
    print(f"records_with_formula_assets={records_with_formula_assets}")
    print(f"total_formula_assets={total_formula_assets}")
    print(f"records_with_formula_missing={records_with_formula_missing}")
    print(f"missing_expected_titles={missing_expected_titles}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
