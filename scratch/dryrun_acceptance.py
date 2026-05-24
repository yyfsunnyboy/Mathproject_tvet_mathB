# -*- coding: utf-8 -*-
import os
import re
import sqlite3
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from core.textbook_filename_parser import (
    detect_docx_source_scope_from_content,
    merge_source_scope_detection,
    parse_textbook_filename_metadata,
    resolve_upload_filenames,
)
from core.textbook_processor_v2 import (
    _resolve_import_source_metadata,
    phase1_extract_docx_lines,
    phase2_mathb_chapter_self_assessment_slice,
)

ORIGINAL = "第一章 自我評量-課本_Latex.docx"
SECTION = "第一章 1-1 數線與絕對值-課本_Latex.docx"


def main():
  # 1-2 filename dry-run
    names = resolve_upload_filenames(ORIGINAL, "a1b2c3d4e5f6.docx")
    print("[1] UPLOAD_FILENAME")
    for k in ("original_filename", "saved_filename", "parse_filename"):
        print(f"  {k}={names[k]}")

    meta = parse_textbook_filename_metadata(names["parse_filename"])
    print("[2] FILENAME META")
    for k in ("source_scope", "chapter_index", "section_code", "section_title"):
        print(f"  {k}={meta.get(k)!r}")

    # find docx
    src = None
    for cand in [
        os.path.join(ROOT, "uploads", ORIGINAL),
        os.path.join(ROOT, "scratch", ORIGINAL),
    ]:
        if os.path.isfile(cand):
            src = cand
            break
    if not src:
        with open(os.path.join(ROOT, "scratch", "docx_search.txt"), "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("MATCH "):
                    src = line.strip().split("MATCH ", 1)[1]
                    break

    print(f"[file] src={src!r}")

    if src and os.path.isfile(src):
        lines = phase1_extract_docx_lines(src)
        scope = _resolve_import_source_metadata(
            parse_filename=ORIGINAL,
            lines=lines,
            curriculum_info={"curriculum": "vocational", "volume": "數學B1", "grade": 10},
        )
        print("[3] SCOPE BUNDLE source_scope=", scope.get("source_scope"))
        sa = phase2_mathb_chapter_self_assessment_slice(
            lines,
            curriculum_info=scope["curriculum_info"],
            chapter_index=1,
        )
        print("[4] SECTION CODES")
        by_q = {}
        for k, v in sa.items():
            m = re.search(r"題\s*(\d+)", k)
            if m:
                by_q[int(m.group(1))] = v.get("section_code")
        for q in range(1, 21):
            print(f"  Q{q} -> {by_q.get(q)!r}")
    else:
        ct = detect_docx_source_scope_from_content(
            [
                "CH1自我評量",
                "自我評量",
                "1-1 數線與絕對值",
                "1. 題目",
                "1-2 平面坐標系與線型函數",
                "2. 題目",
            ]
        )
        merged = merge_source_scope_detection(parse_textbook_filename_metadata("-_Latex.docx"), ct)
        print("[3] content fallback demo (no file):", merged)

    sec = parse_textbook_filename_metadata(SECTION)
    print("[8] section_textbook dry-run", sec)


if __name__ == "__main__":
    main()
