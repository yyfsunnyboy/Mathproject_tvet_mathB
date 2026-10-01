# -*- coding: utf-8 -*-
"""Verification Script to output real GeneralFormOfLinearEquation sorting sequences."""

import sqlite3
import sys
from pathlib import Path
from core.gencode.services.v3_curriculum_ordering_service import get_sorted_component_ids_for_skill

# Force stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path("instance/kumon_math.db")

def main():
    if not DB_PATH.exists():
        print("DB not found")
        return
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # 17 textbook example IDs for vh_數學B1_GeneralFormOfLinearEquation
    ids = [4565, 4566, 4567, 4572, 4573, 4574, 4581, 4582, 4585, 4592, 4593, 4594, 4595, 4596, 4597, 4598, 4599]
    verified = [f"src_{x}" for x in ids]
    
    # General Form
    sorted_ids = get_sorted_component_ids_for_skill(conn, "vh_數學B1_GeneralFormOfLinearEquation", verified)
    print("vh_數學B1_GeneralFormOfLinearEquation:")
    for idx, cid in enumerate(sorted_ids, 1):
        eid = int(cid.split("_")[1])
        r = conn.execute("SELECT source_description FROM textbook_examples WHERE id=?", (eid,)).fetchone()
        print(f"  {idx}. {cid} ({r['source_description']})")

    # Let's print 3 skills for evidence:
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT skill_id FROM textbook_examples")
    skills = [row[0] for row in cursor.fetchall()]
    
    count = 0
    for sk in skills:
        cursor.execute("SELECT id, source_description FROM textbook_examples WHERE skill_id=?", (sk,))
        rows = cursor.fetchall()
        if len(rows) >= 3:
            v_list = [f"src_{r[0]}" for r in rows]
            s_ids = get_sorted_component_ids_for_skill(conn, sk, v_list)
            print(f"\n{sk}:")
            for i, cid in enumerate(s_ids, 1):
                eid = int(cid.split("_")[1])
                r = conn.execute("SELECT source_description FROM textbook_examples WHERE id=?", (eid,)).fetchone()
                print(f"  {i}. {cid} ({r['source_description']})")
            count += 1
            if count >= 3:
                break

    conn.close()

if __name__ == "__main__":
    main()
