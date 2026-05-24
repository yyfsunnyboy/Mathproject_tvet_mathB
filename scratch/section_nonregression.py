# -*- coding: utf-8 -*-
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from core.textbook_filename_parser import parse_textbook_filename_metadata
from core.textbook_processor_v2 import (
    _resolve_import_source_metadata,
    phase1_extract_docx_lines,
    phase2_deterministic_block_slice,
    phase2_mathb_chapter_self_assessment_slice,
)

section_file = os.path.join(ROOT, "uploads", "1-1_-.docx")
section_name = "第一章 1-1 數線與絕對值-課本_Latex.docx"

print("=== [8] section_textbook non-regression ===")
meta = parse_textbook_filename_metadata(section_name)
print("filename_meta:", meta)
assert meta.get("source_scope") == "section_textbook"
assert meta.get("section_code") == "1-1"

if os.path.isfile(section_file):
    lines = phase1_extract_docx_lines(section_file)
    scope = _resolve_import_source_metadata(
        parse_filename=section_name,
        lines=lines,
        curriculum_info={"curriculum": "vocational", "volume": "數學B1", "grade": 10},
    )
    print("resolved source_scope:", scope.get("source_scope"))
    blocks = phase2_deterministic_block_slice(
        lines,
        source_scope=scope["source_scope"],
        curriculum_info=scope["curriculum_info"],
    )
    print("phase2 block count:", len(blocks))
    print("sample keys:", list(blocks.keys())[:5])
else:
    print("section file missing:", section_file)
