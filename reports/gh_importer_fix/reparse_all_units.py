"""Impact check: re-parse every stored general-high DOCX with the fixed importer and compare with the stored rows.

Pure parse + read-only DB.  For each unit prints how many stems still equal the stored text (content-normalised) and which
differ, so every change can be traced to one of the four fixed defect classes (or flagged as a regression).
Use --baseline to run the same comparison with the fixes switched off (git-stash-free: monkeypatches the new hooks).
"""
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import core.textbook_processor as tp  # noqa: E402

DATA = Path(os.environ.get("MP_DATA_ROOT") or ROOT)  # code under test may live in another checkout (baseline)
PROD = DATA / "instance/kumon_math.db"
con = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row


def norm(t: str) -> str:
    t = re.sub(r"\\[a-zA-Z]+", "", t or "").replace("−", "-")
    return "".join(ch for ch in t if ch.isalnum() or ch in "+-=<>≤≥≠×÷±")


report = {}
for docx in sorted((DATA / "textbook_import/uploaded_sources/general").glob("*/*.docx")):
    volume = docx.parent.name
    m = re.search(r"單元(\d+)", docx.name)
    chapters = [r[0] for r in con.execute("select distinct source_chapter from textbook_examples where source_curriculum='general' and source_volume=?", (volume,))
                if re.match(rf"單元{int(m.group(1))} ", r[0] or "")]
    if not chapters:
        continue
    chapter = chapters[0]
    content, meta, _ = tp._extract_docx_with_mathtype_conversion(str(docx))
    scan = tp.scan_general_high_layout(content[1], meta.get("body_paragraphs"))
    stored = {}
    for r in con.execute("select source_description, problem_text from textbook_examples where source_curriculum='general' and source_volume=? and source_chapter=?", (volume, chapter)):
        stored[re.sub(r"\s*\[.*$", "", r["source_description"]).replace(" ", "")] = r["problem_text"]
    new = {k.replace(" ", ""): v for k, v in scan["blocks"].items()}
    only_new = sorted(set(new) - set(stored))
    only_old = sorted(set(stored) - set(new))
    diff = [k for k in new if k in stored and norm(new[k]) != norm(stored[k])]
    report[f"{volume}/{chapter}"] = {"parsed": len(new), "stored": len(stored), "only_in_new_parse": only_new, "only_in_stored": only_old, "stem_differs": diff}
    print(f"{volume} {chapter:22s} parsed={len(new):3d} stored={len(stored):3d} identical={len(new) - len(diff) - len(only_new):3d} differs={diff} only_new={only_new} only_stored={only_old}")
tag = "baseline" if "--baseline" in sys.argv else "fixed"
Path(__file__).with_name(f"reparse_all_units_{tag}.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
