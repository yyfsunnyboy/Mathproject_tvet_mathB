"""Read-only inventory of 普高數學2 Unit 5 rows in the formal DB (opened with mode=ro)."""
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "instance" / "kumon_math.db"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
cols = [r[1] for r in con.execute("pragma table_info(textbook_examples)")]
print("cols:", cols)
rows = con.execute("select id, skill_id, source_curriculum, source_volume, source_chapter, source_section, source_description, notes "
                   "from textbook_examples where source_curriculum='general' and (source_chapter like '%組合%' or source_chapter like '%單元5%')").fetchall()
print("unit5 rows in formal DB:", len(rows))
for r in rows[:50]:
    n = json.loads(r[7] or "{}")
    print(r[0], r[1], r[3], r[4], r[6], (n.get("question_anchor") or {}).get("anchor_id"), len(n.get("image_assets") or []), n.get("pdf_visual_status"))
print(con.execute("select source_volume, source_chapter, count(*) from textbook_examples where source_curriculum='general' group by 1,2").fetchall())
