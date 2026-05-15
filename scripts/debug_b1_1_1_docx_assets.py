#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B1 1-1 DOCX asset dry-run checker (no Gemini / no DB write)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import create_app
import core.textbook_processor as processor


TARGET_TITLES = [
    "例題1",
    "例題 1",
    "例1",
    "隨堂練習1",
    "隨堂練習 1",
    "1-1習題 基礎題5",
    "1-1習題 基礎題10",
]


class _Queue:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def put(self, msg: str) -> None:
        self.messages.append(str(msg))


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", str(s or "").strip())


def _collect_lookup_result(title: str, q_assets: dict, formula_blocks: dict) -> dict:
    assets = processor._lookup_docx_question_assets(title, q_assets) or []
    formula_assets = [a for a in assets if str(a.get("media_kind", "")) == "formula_asset"]
    raw_block = processor._lookup_docx_formula_block(title, formula_blocks)
    sample = formula_assets[0] if formula_assets else (assets[0] if assets else {})

    placeholder_token = str(sample.get("placeholder_token") or "")
    if not placeholder_token:
        m = re.search(r"\[FORMULA_IMAGE_\d+\]", str(raw_block or ""))
        placeholder_token = m.group(0) if m else ""

    return {
        "title": title,
        "found_assets_count": len(assets),
        "formula_assets_count": len(formula_assets),
        "mapping_status": str(sample.get("mapping_status") or ("lookup_failed" if not assets else "exact_or_default")),
        "sample_original_path": str(sample.get("original_path") or sample.get("path") or ""),
        "sample_original_format": str(sample.get("original_format") or ""),
        "sample_placeholder_token": placeholder_token,
        "raw_block_found": bool(str(raw_block or "").strip()),
    }


def _render_report(
    docx_path: Path,
    report_path: Path,
    paragraphs_count: int,
    placeholder_count: int,
    media_total: int,
    formula_asset_total: int,
    q_assets: dict,
    lookup_results: list[dict],
    failed_checks: list[str],
    extra_notes: list[str],
) -> None:
    keys = list(q_assets.keys()) if isinstance(q_assets, dict) else []
    key_counts = []
    for k in keys[:30]:
        key_counts.append((k, len(q_assets.get(k) or [])))

    has_key_prefix_liti1 = any(_norm(k).startswith("例1") or _norm(k).startswith("例題1") for k in keys)
    has_key_11_ex = any(_norm(k) == "1-1習題" for k in keys)

    lines: list[str] = []
    lines.append("# B1 1-1 DOCX Asset Dry-Run Report")
    lines.append("")
    lines.append(f"- Source DOCX: `{docx_path.as_posix()}`")
    lines.append("- Gemini: not called")
    lines.append("- DB write: not performed")
    lines.append("- OCR: disabled / not executed")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- paragraphs count: `{paragraphs_count}`")
    lines.append(f"- equation image placeholder count: `{placeholder_count}`")
    lines.append(f"- media_total: `{media_total}`")
    lines.append(f"- formula_asset total count: `{formula_asset_total}`")
    lines.append(f"- key startswith '例1': `{has_key_prefix_liti1}`")
    lines.append(f"- key equals '1-1習題': `{has_key_11_ex}`")
    lines.append("")
    lines.append("## docx_question_assets Keys (first 30)")
    if not key_counts:
        lines.append("- (none)")
    else:
        for k, c in key_counts:
            lines.append(f"- `{k}`: assets={c}")
    lines.append("")
    lines.append("## Lookup Results")
    for r in lookup_results:
        lines.append(f"### {r['title']}")
        lines.append(f"- found_assets_count: `{r['found_assets_count']}`")
        lines.append(f"- formula_assets_count: `{r['formula_assets_count']}`")
        lines.append(f"- mapping_status: `{r['mapping_status']}`")
        lines.append(f"- sample original_path: `{r['sample_original_path']}`")
        lines.append(f"- sample original_format: `{r['sample_original_format']}`")
        lines.append(f"- sample placeholder_token: `{r['sample_placeholder_token']}`")
        lines.append(f"- raw_block_found: `{r['raw_block_found']}`")
        lines.append("")
    lines.append("## FAILED CHECKS")
    if not failed_checks:
        lines.append("- (none)")
    else:
        for item in failed_checks:
            lines.append(f"- {item}")
    lines.append("")
    if extra_notes:
        lines.append("## Notes")
        for n in extra_notes:
            lines.append(f"- {n}")
        lines.append("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run DOCX asset checker for B1 1-1.")
    parser.add_argument(
        "--docx",
        default="uploads/1-1_-.docx",
        help="Path to DOCX file (default: uploads/1-1_-.docx)",
    )
    parser.add_argument(
        "--report",
        default="reports/b1_import_debug/b1_1_1_docx_asset_dry_run_report.md",
        help="Output markdown report path",
    )
    args = parser.parse_args()

    repo_root = REPO_ROOT
    docx_path = (repo_root / args.docx).resolve()
    report_path = (repo_root / args.report).resolve()
    failed_checks: list[str] = []
    notes: list[str] = []

    q_assets = {}
    formula_blocks = {}
    paragraphs_count = 0
    placeholder_count = 0
    media_total = 0
    formula_asset_total = 0
    lookup_results: list[dict] = []

    if not docx_path.exists():
        failed_checks.append(f"source docx not found: {docx_path.as_posix()}")
        notes.append("Please place target file at uploads/1-1_-.docx or pass --docx.")
        for t in TARGET_TITLES:
            lookup_results.append(
                {
                    "title": t,
                    "found_assets_count": 0,
                    "formula_assets_count": 0,
                    "mapping_status": "lookup_failed",
                    "sample_original_path": "",
                    "sample_original_format": "",
                    "sample_placeholder_token": "",
                    "raw_block_found": False,
                }
            )
    else:
        app = create_app()
        app.config["ENABLE_DOCX_FORMULA_OCR_FALLBACK"] = False
        q = _Queue()
        with app.app_context():
            _ = processor.extract_content_from_file(str(docx_path), q)
            ctx = getattr(processor, "_DOCX_IMPORT_CONTEXT", {}) or {}
            ordered_blocks = ctx.get("ordered_blocks", []) if isinstance(ctx, dict) else []
            q_assets = ctx.get("question_assets", {}) if isinstance(ctx, dict) else {}
            formula_blocks = ctx.get("question_formula_blocks", {}) if isinstance(ctx, dict) else {}
            media_rel_map = ctx.get("media_rel_map", {}) if isinstance(ctx, dict) else {}

        paragraphs = [b for b in ordered_blocks if b.get("type") == "paragraph"]
        paragraphs_count = len(paragraphs)
        placeholder_count = sum(
            len(re.findall(r"\[FORMULA_IMAGE_\d+\]", str(p.get("text", "") or "")))
            for p in paragraphs
        )
        media_total = len(media_rel_map) if isinstance(media_rel_map, dict) else 0
        formula_asset_total = 0
        if isinstance(q_assets, dict):
            for arr in q_assets.values():
                for a in (arr or []):
                    if str(a.get("media_kind", "")) == "formula_asset":
                        formula_asset_total += 1

        for title in TARGET_TITLES:
            lookup_results.append(_collect_lookup_result(title, q_assets, formula_blocks))

    # Required failed checks
    if formula_asset_total == 0:
        failed_checks.append("formula_asset total count == 0")
    liti_results = [r for r in lookup_results if r["title"] in ("例題1", "例題 1", "例1")]
    if liti_results and all(int(r["formula_assets_count"]) == 0 for r in liti_results):
        failed_checks.append("例題1 / 例題 1 / 例1 全部 lookup formula_assets_count == 0")
    j5 = next((r for r in lookup_results if r["title"] == "1-1習題 基礎題5"), None)
    if j5 and int(j5["formula_assets_count"]) == 0:
        failed_checks.append("1-1習題 基礎題5 lookup formula_assets_count == 0")
    j10 = next((r for r in lookup_results if r["title"] == "1-1習題 基礎題10"), None)
    if j10 and int(j10["formula_assets_count"]) == 0:
        failed_checks.append("1-1習題 基礎題10 lookup formula_assets_count == 0")

    _render_report(
        docx_path=docx_path,
        report_path=report_path,
        paragraphs_count=paragraphs_count,
        placeholder_count=placeholder_count,
        media_total=media_total,
        formula_asset_total=formula_asset_total,
        q_assets=q_assets,
        lookup_results=lookup_results,
        failed_checks=failed_checks,
        extra_notes=notes,
    )

    print(f"report={report_path.as_posix()}")
    print(f"formula_asset_total={formula_asset_total}")
    print(f"failed_checks={len(failed_checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
