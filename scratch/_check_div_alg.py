# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

conn = sqlite3.connect(str(Path(__file__).resolve().parents[1] / "instance" / "kumon_math.db"))
conn.row_factory = sqlite3.Row
for skill in (
    "vh_數學B1_DivisionAlgorithm",
    "vh_數學B1_SubSection322",
    "vh_數學B1_RemainderTheorem",
    "vh_數學B1_FactorTheorem",
):
    n = conn.execute("SELECT COUNT(*) c FROM textbook_examples WHERE skill_id=?", (skill,)).fetchone()["c"]
    print(skill, n)
