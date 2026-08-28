# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

db = Path("instance/kumon_math.db")
sid = "vh_數學B1_SubSection332"
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute(
    "SELECT skill_id, skill_ch_name, is_active FROM skills_info WHERE skill_id=?",
    (sid,),
)
print(cur.fetchone())
con.close()
