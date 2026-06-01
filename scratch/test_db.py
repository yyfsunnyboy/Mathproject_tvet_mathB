import sqlite3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
db_path = root / "instance" / "kumon_math.db"

con = sqlite3.connect(str(db_path))
cur = con.cursor()

# Get distinct skill_ids
skill_ids = [r[0] for r in cur.execute("SELECT DISTINCT skill_id FROM textbook_examples").fetchall()]
print("Distinct skill_ids:")
for sid in sorted(skill_ids):
    if "LinearFunction" in sid:
        print(f" - {sid!r} (length: {len(sid)})")

# Count for specific queries
target_exact = "vh_數學B1_LinearFunction"
count_exact = cur.execute("SELECT count(*) FROM textbook_examples WHERE skill_id=?", (target_exact,)).fetchone()[0]
print(f"\nCount with exact key {target_exact!r}: {count_exact}")

con.close()
