#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Render B1 1-1 question page/crop images (dry-run, no DB write)."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_REPORT_PATH = Path("reports/b1_import_debug/b1_1_1_question_crop_dry_run_report.md")
DEFAULT_OUTPUT_DIR = Path("uploads/question_assets/longteng_數學B1/CH1/1-1/vision_crops")


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _title_aliases(title: str) -> list[str]:
    raw = str(title or "").strip()
    aliases = {raw, raw.replace(" ", "")}
    m = re.match(r"^例題\s*(\d+)$", raw)
    if m:
        n = m.group(1)
        aliases.update({f"例題 {n}", f"例題{n}", f"例{n}"})
    m2 = re.match(r"^1-1習題\s*基礎題\s*(\d+)$", raw)
    if m2:
        n = m2.group(1)
        aliases.update({f"1-1習題 基礎題{n}", f"基礎題{n}"})
    return sorted(a for a in aliases if a)


def _convert_docx_to_pdf(docx_path: Path, output_pdf: Path) -> tuple[bool, str]:
    if not docx_path.exists():
        return False, f"docx_not_found: {docx_path.as_posix()}"
    soffice = shutil.which("soffice")
    if not soffice:
        return False, "docx_to_pdf_unavailable: soffice_not_found"
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    try:
        cmd = [
            soffice,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_pdf.parent),
            str(docx_path),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        produced = output_pdf.parent / (docx_path.stem + ".pdf")
        if produced.exists():
            if produced != output_pdf:
                shutil.copy2(produced, output_pdf)
            return True, ""
        return False, "docx_to_pdf_failed: no_pdf_output"
    except Exception as exc:
        return False, f"docx_to_pdf_failed: {exc}"


def _find_title_page_and_rect(doc: Any, title: str) -> tuple[int | None, Any | None]:
    aliases = _title_aliases(title)
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        for alias in aliases:
            rects = page.search_for(alias)
            if rects:
                return page_idx, rects[0]
    return None, None


def _render_page_png(doc: Any, page_idx: int, out_path: Path) -> bool:
    try:
        page = doc[page_idx]
        pix = page.get_pixmap(matrix=None, dpi=180)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(out_path))
        return True
    except Exception:
        return False


def _render_crop_png(doc: Any, page_idx: int, rect: Any, out_path: Path) -> bool:
    try:
        page = doc[page_idx]
        margin_x = max(24, rect.width * 0.2)
        margin_y = max(120, rect.height * 10)
        x0 = max(0, rect.x0 - margin_x)
        y0 = max(0, rect.y0 - margin_y)
        x1 = min(page.rect.width, rect.x1 + margin_x)
        y1 = min(page.rect.height, rect.y1 + margin_y * 2.2)
        clip = type(rect)(x0, y0, x1, y1)
        pix = page.get_pixmap(matrix=None, dpi=180, clip=clip)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(out_path))
        return True
    except Exception:
        return False


def run_render(
    *,
    docx_path: str | Path,
    pdf_path: str | Path | None,
    titles: list[str],
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    dry_run: bool = True,
) -> dict[str, Any]:
    root = project_root()
    output_rel = Path(output_dir)
    output_abs = output_rel if output_rel.is_absolute() else (root / output_rel)
    output_abs.mkdir(parents=True, exist_ok=True)

    pdf_abs = None
    failures: list[str] = []
    temp_pdf = output_abs / "_tmp_docx_render.pdf"
    if pdf_path:
        cand = Path(pdf_path)
        pdf_abs = cand if cand.is_absolute() else (root / cand)
        if not pdf_abs.exists():
            failures.append(f"pdf_not_found: {pdf_abs.as_posix()}")
            pdf_abs = None
    if pdf_abs is None:
        ok, err = _convert_docx_to_pdf(Path(docx_path), temp_pdf)
        if ok:
            pdf_abs = temp_pdf
        else:
            failures.append(err)

    if pdf_abs is None:
        return {
            "dry_run": bool(dry_run),
            "rendered_pages": 0,
            "crops_created": 0,
            "crop_status": "page_render_unavailable",
            "failures": failures,
            "rows": [],
        }

    try:
        import fitz  # pylint: disable=import-outside-toplevel

        doc = fitz.open(str(pdf_abs))
    except Exception as exc:
        failures.append(f"pdf_open_failed: {exc}")
        return {
            "dry_run": bool(dry_run),
            "rendered_pages": 0,
            "crops_created": 0,
            "crop_status": "page_render_unavailable",
            "failures": failures,
            "rows": [],
        }

    rendered_pages: set[int] = set()
    crops_created = 0
    rows = []
    for idx, title in enumerate(titles, start=1):
        page_idx, rect = _find_title_page_and_rect(doc, title)
        if page_idx is None:
            page_idx = 0 if len(doc) > 0 else None

        if page_idx is None:
            rows.append(
                {
                    "title": title,
                    "crop_status": "page_render_unavailable",
                    "crop_path": "",
                    "page_image_path": "",
                    "page_image_available": False,
                    "failures": ["no_page_available"],
                }
            )
            continue

        page_img_name = f"b1_1_1_page_{page_idx + 1:03d}.png"
        page_img_abs = output_abs / page_img_name
        page_img_rel = (output_rel / page_img_name).as_posix()
        page_ok = _render_page_png(doc, page_idx, page_img_abs)
        if page_ok:
            rendered_pages.add(page_idx)

        crop_status = "page_only"
        crop_rel = page_img_rel if page_ok else ""
        item_failures: list[str] = []
        if rect is not None and page_ok:
            crop_name = f"b1_1_1_crop_{idx:02d}_{page_idx + 1:03d}.png"
            crop_abs = output_abs / crop_name
            crop_rel_candidate = (output_rel / crop_name).as_posix()
            if _render_crop_png(doc, page_idx, rect, crop_abs):
                crop_status = "cropped"
                crop_rel = crop_rel_candidate
                crops_created += 1
            else:
                item_failures.append("crop_render_failed")
        elif not page_ok:
            crop_status = "page_render_unavailable"
            item_failures.append("page_render_failed")

        rows.append(
            {
                "title": title,
                "crop_status": crop_status,
                "crop_path": crop_rel,
                "page_image_path": page_img_rel if page_ok else "",
                "page_image_available": bool(page_ok),
                "failures": item_failures,
            }
        )

    doc.close()
    return {
        "dry_run": bool(dry_run),
        "rendered_pages": len(rendered_pages),
        "crops_created": int(crops_created),
        "crop_status": "ok" if rows else "page_render_unavailable",
        "failures": failures,
        "rows": rows,
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# B1 1-1 Question Crop Dry-Run Report",
        "",
        f"- dry_run: `{bool(result.get('dry_run'))}`",
        f"- rendered_pages: {result.get('rendered_pages', 0)}",
        f"- crops_created: {result.get('crops_created', 0)}",
        f"- crop_status: `{result.get('crop_status', '')}`",
        f"- failures: `{' ; '.join(result.get('failures', []))}`",
        "",
        "## Per-Title",
    ]
    rows = result.get("rows", [])
    if not rows:
        lines.append("- no title rows")
    for row in rows:
        lines.extend(
            [
                f"### {row.get('title', '')}",
                f"- crop_status: `{row.get('crop_status', '')}`",
                f"- crop_path: `{row.get('crop_path', '')}`",
                f"- page_image_path: `{row.get('page_image_path', '')}`",
                f"- page_image_available: `{bool(row.get('page_image_available'))}`",
                f"- failures: `{' ; '.join(row.get('failures', []))}`",
                "",
            ]
        )
    return "\n".join(lines)


def write_report(result: dict[str, Any], report_path: str | Path) -> Path:
    path = Path(report_path)
    if not path.is_absolute():
        path = project_root() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_report(result), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render B1 1-1 question crops from DOCX/PDF (no OCR).")
    parser.add_argument("--docx", required=True)
    parser.add_argument("--pdf", default="")
    parser.add_argument("--section", default="1-1 數線與絕對值")
    parser.add_argument("--title", action="append", dest="titles", default=[])
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    args = parser.parse_args()

    titles = list(args.titles or ["例題1", "例題2", "1-1習題 基礎題5"])
    result = run_render(
        docx_path=args.docx,
        pdf_path=args.pdf or None,
        titles=titles,
        output_dir=args.output_dir,
        dry_run=bool(args.dry_run),
    )
    report = write_report(result, args.report)
    print(render_report(result))
    print(f"\nReport written: {report.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
