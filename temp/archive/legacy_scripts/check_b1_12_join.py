import sqlite3

db = r"D:\Python\Mathproject_tvet_mathB\instance\kumon_math.db"
con = sqlite3.connect(db)
cur = con.cursor()

sql = """
SELECT
    sc.skill_id,
    si.skill_ch_name,
    si.skill_en_name,
    si.category,
    si.is_active,
    sc.curriculum,
    sc.grade,
    sc.volume,
    sc.chapter,
    sc.section,
    sc.paragraph
FROM skill_curriculum sc
LEFT JOIN skills_info si ON si.skill_id = sc.skill_id
WHERE sc.curriculum = ?
  AND sc.grade = ?
  AND sc.volume = ?
  AND sc.chapter = ?
  AND sc.section = ?
ORDER BY sc.skill_id
"""

rows = cur.execute(sql, (
    "vocational",
    10,
    "數學B1",
    "1 坐標系與函數圖形",
    "1-2 平面坐標系與線型函數",
)).fetchall()

print("join rows =", len(rows))
for r in rows:
    print(r)

con.close()
