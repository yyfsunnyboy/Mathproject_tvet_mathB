# -*- coding: utf-8 -*-
"""One-off acceptance runner for 第一章 自我評量 V2 import (no code changes)."""
from __future__ import annotations

import io
import logging
import os
import queue
import re
import shutil
import sqlite3
import sys
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

ORIGINAL_FILENAME = "第一章 自我評量-課本_Latex.docx"
SECTION_FILENAME = "第一章 1-1 數線與絕對值-課本_Latex.docx"


class _ListHandler(logging.Handler):
    def __init__(self, buf: list[str]):
        super().__init__()
        self.buf = buf

    def emit(self, record: logging.LogRecord) -> None:
        self.buf.append(self.format(record))


def _find_self_assessment_docx() -> str | None:
    candidates: list[str] = []
    search_roots = [
        os.path.join(ROOT, "uploads"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Desktop"),
    ]
  # optional Google Drive root if present
    gdrive = r"E:\Google Drive"
    if os.path.isdir(gdrive):
        search_roots.append(gdrive)

    import zipfile

    for root in search_roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                d
                for d in dirnames
                if d not in {"venv", "node_modules", ".git", "__pycache__", ".cursor"}
            ]
            for fn in filenames:
                if not fn.lower().endswith(".docx"):
                    continue
                path = os.path.join(dirpath, fn)
                try:
                    with zipfile.ZipFile(path) as z:
                        xml = z.read("word/document.xml").decode("utf-8", "ignore")
                    if "自我評量" in xml and "1-1" in xml and "1-2" in xml and "1-4" in xml:
                        candidates.append(path)
                except Exception:
                    pass
            if len(candidates) >= 5:
                break
    if not candidates:
        return None
    # prefer exact original name
    for p in candidates:
        if os.path.basename(p) == ORIGINAL_FILENAME:
            return p
    for p in candidates:
        if "自我評量" in os.path.basename(p):
            return p
    return candidates[0]


def _query_db() -> dict:
    db = os.path.join(ROOT, "instance", "kumon_math.db")
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    out: dict = {"fallback_skills": {}, "skill_counts": {}}
    cur.execute("SELECT COUNT(*) FROM skills_info")
    out["skill_counts"]["before_total"] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM skill_curriculum")
    out["skill_counts"]["curriculum_total"] = cur.fetchone()[0]
    for pat in ["SelfAssessment", "MixedExercise", "Unknown", "Concept_", "SubSection_"]:
        cur.execute("SELECT skill_id FROM skills_info WHERE skill_id LIKE ?", (f"%{pat}%",))
        out["fallback_skills"][pat] = [r[0] for r in cur.fetchall()]
    conn.close()
    return out


def _section_code_for_question(meta: dict, qnum: int) -> str | None:
    for k, v in meta.items():
        m = re.search(r"題\s*(\d+)\b", str(k))
        if m and int(m.group(1)) == qnum:
            return str(v.get("section_code") or "")
    return None


def main() -> int:
    logs: list[str] = []
    handler = _ListHandler(logs)
    handler.setFormatter(logging.Formatter("%(message)s"))

    src = _find_self_assessment_docx()
    print("=== FILE DISCOVERY ===")
    if src:
        print(f"found_source={src}")
    else:
        print("found_source=NOT_FOUND")
        print("Cannot run full V2 import without DOCX on disk.")
        return 2

    db_before = _query_db()
    print("=== DB BEFORE ===")
    print(db_before)

    saved_filename = f"{uuid.uuid4().hex}.docx"
    saved_path = os.path.join(ROOT, "uploads", saved_filename)
    shutil.copy2(src, saved_path)

    from core.textbook_filename_parser import parse_textbook_filename_metadata, resolve_upload_filenames
    from core.textbook_processor_v2 import (
        _DOCX_BLOCK_META,
        phase2_mathb_chapter_self_assessment_slice,
        phase1_extract_docx_lines,
        _resolve_import_source_metadata,
    )

    upload_names = resolve_upload_filenames(ORIGINAL_FILENAME, saved_filename)
    print("=== UPLOAD FILENAMES ===")
    for k, v in upload_names.items():
        print(f"{k}={v}")

    filename_meta = parse_textbook_filename_metadata(upload_names["parse_filename"])
    print("=== FILENAME META ===")
    print(filename_meta)

    lines = phase1_extract_docx_lines(saved_path)
    curriculum_info = {
        "curriculum": "vocational",
        "publisher": "longteng",
        "grade": 10,
        "volume": "數學B1",
        "original_filename": upload_names["original_filename"],
        "saved_filename": upload_names["saved_filename"],
        "parse_filename": upload_names["parse_filename"],
    }
    scope_bundle = _resolve_import_source_metadata(
        parse_filename=upload_names["parse_filename"],
        lines=lines,
        curriculum_info=curriculum_info,
    )
    print("=== SOURCE SCOPE ===")
    print(scope_bundle)

    sa_meta = phase2_mathb_chapter_self_assessment_slice(
        lines,
        curriculum_info=scope_bundle["curriculum_info"],
        chapter_index=scope_bundle["curriculum_info"].get("chapter_index"),
    )
    print("=== SECTION CODE BY QUESTION ===")
    for q in range(1, 21):
        sc = _section_code_for_question(sa_meta, q)
        print(f"Q{q} section_code={sc}")

    # section textbook dry-run
    sec_meta = parse_textbook_filename_metadata(SECTION_FILENAME)
    print("=== SECTION TEXTBOOK DRY-RUN ===")
    print(f"filename={SECTION_FILENAME}")
    print(sec_meta)

    # Full import if Gemini key available
    from app import create_app

    app = create_app()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    with app.app_context():
        from core.textbook_processor_v2 import process_textbook_file_v2

        q: queue.Queue = queue.Queue()
        try:
            result = process_textbook_file_v2(saved_path, scope_bundle["curriculum_info"], q)
            print("=== IMPORT RESULT ===")
            print(result)
        except Exception as exc:
            print(f"IMPORT FAILED: {type(exc).__name__}: {exc}")
            result = {}

        while not q.empty():
            print("QUEUE:", q.get())

    db_after = _query_db()
    print("=== DB AFTER ===")
    print(db_after)

    print("=== RELEVANT LOGS ===")
    keys = (
        "UPLOAD_FILENAME",
        "FILENAME_META",
        "SOURCE_SCOPE",
        "SELF_ASSESSMENT",
        "NO_NEW_SKILL_GUARD",
        "Import complete",
        "antigravity",
    )
    for line in logs:
        if any(k in line for k in keys):
            print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
