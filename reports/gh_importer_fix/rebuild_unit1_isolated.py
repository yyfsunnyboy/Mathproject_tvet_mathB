"""Re-parse the stored unit-1 DOCX with the fixed importer and compare with the stored rows.

Isolated: pure parse (no Flask app context, no DB writes, no uploads); production DB and the repaired sandbox copy are
opened read-only.  Prints, per question, whether the new parse equals (a) the production row (unaffected rows must be
identical) and (b) the hand-repaired sandbox row (defect rows must now match without any per-question patch).
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import core.textbook_processor as tp  # noqa: E402

DOCX = ROOT / "textbook_import/uploaded_sources/general/數學2/742ea24d3d43_單元01-數列與遞迴關係.docx"
PROD = ROOT / "instance/kumon_math.db"
SANDBOX = ROOT / "reports/gh_math2_unit1_stage1/sandbox/kumon_math_copy.db"


def norm(t: str) -> str:
    """Compare content, not typesetting: drop LaTeX commands, punctuation and spacing the persist step re-flows."""
    t = re.sub(r"\\[a-zA-Z]+", "", t or "")
    t = t.replace("−", "-")
    return "".join(ch for ch in t if ch.isalnum() or ch in "+-=<>≤≥≠×÷±")


def rows(db: Path):
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    out = {}
    for r in con.execute("select * from textbook_examples where source_curriculum='general' and source_volume='數學2' and source_chapter='單元1 數列與遞迴關係'"):
        label = re.sub(r"\s*\[.*$", "", r["source_description"]).replace(" ", "")
        out[label] = dict(r)
    return out


content, meta, _ = tp._extract_docx_with_mathtype_conversion(str(DOCX))
scan = tp.scan_general_high_layout(content[1], meta.get("body_paragraphs"))
new_blocks, new_sol = scan["blocks"], scan["solutions"]
prod, sand = rows(PROD), rows(SANDBOX)


def key(title: str) -> str:
    return title.replace(" ", "").replace("例題", "例題")


print(f"parsed items={len(scan['items'])}  prod rows={len(prod)}  sandbox rows={len(sand)}")
titles = [it["canonical_title"].replace(" ", "") for it in scan["items"]]
print("new vs sandbox titles identical:", sorted(titles) == sorted(sand))
same_prod = same_sand = 0
diff_prod, diff_sand = [], []
for t in titles:
    stem = new_blocks.get(next(x["canonical_title"] for x in scan["items"] if x["canonical_title"].replace(" ", "") == t), "")
    p = prod.get(t)
    s = sand.get(t)
    if s is not None and norm(stem) == norm(s["problem_text"]):
        same_sand += 1
    else:
        diff_sand.append(t)
    if p is not None and norm(stem) == norm(p["problem_text"]):
        same_prod += 1
    else:
        diff_prod.append(t)
print(f"new parse == sandbox(repaired) stems: {same_sand}/{len(titles)}   differs: {diff_sand}")
print(f"new parse == production stems: {same_prod}/{len(titles)}  differs: {diff_prod}")
print("solutions recovered:", len(new_sol), sorted(new_sol))
json.dump({"titles": titles, "diff_vs_sandbox": diff_sand, "diff_vs_prod": diff_prod, "solutions": sorted(new_sol)},
          open(Path(__file__).with_name("rebuild_unit1_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
