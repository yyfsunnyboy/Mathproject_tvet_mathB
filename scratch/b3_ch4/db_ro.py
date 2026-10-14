import sqlite3
from pathlib import Path

from core.domain.exponential_logarithmic_domain import SOURCE_SPECS

db = Path("instance/kumon_math.db").resolve()
conn = sqlite3.connect("file:" + str(db).replace("\\", "/") + "?mode=ro", uri=True)
cols = [r[1] for r in conn.execute("PRAGMA table_info(textbook_examples)")]
print("te cols:", cols)
rows = conn.execute("SELECT id, skill_id FROM textbook_examples WHERE id BETWEEN 12127 AND 12272").fetchall()
print("rows:", len(rows))
mismatch = [(i, s, SOURCE_SPECS.get(i, {}).get("skill_id")) for i, s in rows if SOURCE_SPECS.get(i, {}).get("skill_id") != s]
print("skill mismatches:", mismatch)
skills = sorted({s for _, s in rows})
print("skills:", skills)
q = "SELECT skill_id, curriculum, volume, chapter, section, display_order FROM skill_curriculum WHERE skill_id LIKE 'vh_數學B3_%4_%'"
for r in conn.execute(q):
    print("curr:", r)
for r in conn.execute("SELECT skill_id, is_active, skill_ch_name FROM skills_info WHERE skill_id LIKE 'vh_數學B3_SubSection_4_%'"):
    print("info:", r)
r = conn.execute("SELECT id, skill_id, substr(problem_text,1,200), correct_answer FROM textbook_examples WHERE id=12231").fetchone()
print("12231:", r)
tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("tracker tables:", [t for t in tables if "track" in t.lower() or "gencode" in t.lower()])
conn.close()
