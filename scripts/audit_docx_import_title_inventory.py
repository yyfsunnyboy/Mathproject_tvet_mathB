#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Audit converted DOCX title inventory before import."""

from __future__ import annotations

import argparse
from pathlib import Path

from core.textbook_processor import (
    extract_converted_latex_docx,
    scan_docx_title_inventory,
    build_title_inventory,
    write_title_inventory_report,
)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--docx", required=True)
    p.add_argument("--report", required=True)
    p.add_argument("--volume", default="unknown")
    p.add_argument("--section", default="unknown")
    args = p.parse_args()

    pages, _meta = extract_converted_latex_docx(args.docx)
    text = "\n".join(str(v or "") for _k, v in sorted((pages or {}).items()))
    section_arg = None if args.section == "unknown" else args.section
    inventory_items = scan_docx_title_inventory(text, section_code=section_arg)
    expected = sorted({str(it.get("canonical_title", "")).strip() for it in inventory_items if it.get("canonical_title")})
    inv = build_title_inventory(expected, [], section_code=args.section, inventory_items=inventory_items)
    write_title_inventory_report(
        args.report,
        volume=args.volume,
        section=args.section,
        allow_partial_import=False,
        write_aborted=False,
        inv=inv,
    )
    print(f"expected_titles_count={inv.get('expected_titles_count', 0)}")
    print(f"report={Path(args.report).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
