import sqlite3

db = r"D:\Python\Mathproject_tvet_mathB\instance\kumon_math.db"
con = sqlite3.connect(db)
cur = con.cursor()

for table in ["skills_info", "skill_curriculum", "textbook_examples"]:
    n = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(table, "count =", n)

rows = cur.execute("""
SELECT skill_id, skill_ch_name, category, is_active
FROM skills_info
ORDER BY skill_id
LIMIT 30
""").fetchall()

print("skills_info sample rows =", len(rows))
for r in rows:
    print(r)

con.close()
