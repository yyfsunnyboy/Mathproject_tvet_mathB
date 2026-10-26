"""Dry (no write) PDF-visual enrichment on every stored general-high PDF, with and without the new extent audit.

Shows which previously accepted figures the audit would send back to review. Read-only: production DB opened
mode=ro, enrichment write_notes=False publish_assets=False, no debug dir.
"""
import json
import re
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import core.textbook_pdf_visual as tv  # noqa: E402
import core.textbook_pdf_visual_acceptance as acc  # noqa: E402

con = sqlite3.connect("file:" + (ROOT / "instance/kumon_math.db").as_posix() + "?mode=ro", uri=True)
con.row_factory = sqlite3.Row
orig = acc.crop_extent_reasons


def run(pdf: Path, volume: str, chapter: str, rows, audit: bool):
    acc.crop_extent_reasons = orig if audit else (lambda *a, **k: [])
    s = tv.enrich_textbook_examples_with_pdf_visuals(
        pdf_path=pdf, examples=rows, curriculum_info={"curriculum": "general", "volume": volume, "chapter": chapter, "section": "", "publisher": "longteng"},
        project_root=ROOT, debug_dir=None, write_notes=False, publish_assets=False, assemble_visual_groups=True)
    return {r["id"]: (r.get("status"), r.get("visual_status"), r.get("visual_reason")) for r in s["rows"]}


total_acc = flips = 0
for pdf in sorted((ROOT / "textbook_import/uploaded_sources/general").glob("*/*.pdf")):
    volume = pdf.parent.name
    m = re.search(r"單元(\d+)", pdf.name)
    chapters = [r[0] for r in con.execute("select distinct source_chapter from textbook_examples where source_curriculum='general' and source_volume=?", (volume,))
                if re.match(rf"單元{int(m.group(1))} ", r[0] or "")]
    if not chapters:
        continue
    rows = [SimpleNamespace(**dict(r)) for r in con.execute(
        "select * from textbook_examples where source_curriculum='general' and source_volume=? and source_chapter=?", (volume, chapters[0]))]
    base, new = run(pdf, volume, chapters[0], rows, False), run(pdf, volume, chapters[0], rows, True)
    a = sum(1 for v in base.values() if v[0] == "mounted")
    f = [(i, base[i][2], new[i][2]) for i in base if base[i][0] == "mounted" and new[i][0] != "mounted"]
    total_acc += a
    flips += len(f)
    print(f"{volume} {chapters[0]:24s} rows={len(rows):3d} mounted_before={a:2d} flipped_by_audit={len(f)}", [(i, (n or "")[-40:]) for i, _, n in f])
print("TOTAL mounted_before", total_acc, "flipped", flips)
