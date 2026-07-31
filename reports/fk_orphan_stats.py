# -*- coding: utf-8 -*-
"""Read-only: summarize PRAGMA foreign_key_check violations by table."""
import sqlite3
from collections import Counter

con = sqlite3.connect(r"D:\Python\Mathproject_tvet_mathB\instance\kumon_math.db")
c = con.cursor()
c.execute("PRAGMA foreign_keys=ON")
rows = c.execute("PRAGMA foreign_key_check").fetchall()
# row: (table, rowid, parent, fkid)
by_table = Counter(r[0] for r in rows)
by_parent = Counter((r[0], r[2]) for r in rows)
print("total", len(rows))
print("by_table", dict(by_table))
print("by_child_parent", dict(by_parent))
print("=== curriculum totals ===")
for t, sql in [
    ("skill_curriculum", "SELECT curriculum, COUNT(*) FROM skill_curriculum GROUP BY curriculum"),
    ("skills_info prefixes", "SELECT CASE WHEN skill_id LIKE 'jh_%' THEN 'jh' WHEN skill_id LIKE 'gh_%' THEN 'gh' WHEN skill_id LIKE 'vh_%' THEN 'vh' ELSE 'other' END, COUNT(*) FROM skills_info GROUP BY 1"),
    ("textbook by source_curriculum", "SELECT source_curriculum, COUNT(*) FROM textbook_examples GROUP BY source_curriculum"),
    ("bridge by curriculum", "SELECT curriculum, COUNT(*) FROM skill_family_bridge GROUP BY curriculum"),
]:
    print(t, c.execute(sql).fetchall())
