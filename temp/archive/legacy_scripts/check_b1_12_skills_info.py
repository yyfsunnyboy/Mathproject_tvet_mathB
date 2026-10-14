import sqlite3

db = r"D:\Python\Mathproject_tvet_mathB\instance\kumon_math.db"
con = sqlite3.connect(db)
cur = con.cursor()

ids = [
    "outline_vocational_數學B1_12",
    "vh_數學B1_DistanceBetweenTwoPointsInPlane",
    "vh_數學B1_LinearFunction",
    "vh_數學B1_MidpointCoordinates",
]

sql = """
SELECT skill_id, skill_en_name, skill_ch_name, category, is_active
FROM skills_info
WHERE skill_id IN ({})
""".format(",".join(["?"] * len(ids)))

rows = cur.execute(sql, ids).fetchall()

print("skills_info rows =", len(rows))
for r in rows:
    print(r)

con.close()
