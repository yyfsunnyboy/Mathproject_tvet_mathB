import sqlite3

db = r"D:\Python\Mathproject_tvet_mathB\instance\kumon_math.db"
con = sqlite3.connect(db)
cur = con.cursor()

sql = """
SELECT skill_id, curriculum, grade, volume, chapter, section, paragraph
FROM skill_curriculum
WHERE curriculum = ?
  AND volume = ?
  AND section LIKE ?
ORDER BY skill_id
"""

rows = cur.execute(sql, ("vocational", "數學B1", "1-2%")).fetchall()

print("DB =", db)
print("rows =", len(rows))
for r in rows:
    print(r)

con.close()
