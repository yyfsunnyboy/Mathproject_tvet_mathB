import sqlite3
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "instance/kumon_math.db"
con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
q = lambda sql, *a: con.execute(sql, a).fetchall()
print("db", path)
print("integrity", q("PRAGMA integrity_check")[0][0])
tables = {r[0] for r in q("SELECT name FROM sqlite_master WHERE type='table'")}
print("tables", len(tables))
for t in ("users", "classes", "progress", "textbook_examples", "skills_info", "skill_curriculum"):
    if t in tables:
        print(" ", t, q(f"SELECT COUNT(*) FROM {t}")[0][0])
rows = q("SELECT id, skill_id FROM textbook_examples WHERE id BETWEEN 12127 AND 12272")
print("ch4 rows", len(rows), "skills", len({r[1] for r in rows}))
print("12231", q("SELECT skill_id, substr(problem_text,1,60), coalesce(correct_answer,'') FROM textbook_examples WHERE id=12231"))
if "skills_info" in tables:
    cols = [r[1] for r in q("PRAGMA table_info(skills_info)")]
    active = "is_active" if "is_active" in cols else None
    if active:
        print("ch4 active", q(f"SELECT skill_id, {active} FROM skills_info WHERE skill_id LIKE 'vh_數學B3_SubSection_4_%' ORDER BY skill_id"))
