# -*- coding: utf-8 -*-
"""Classify the 1078 fatal FK violations from job 20260731080038_dcafc89d."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

JOB = Path(r"D:\Python\Mathproject_tvet_mathB\reports\runtime_jobs\import_20260731080038_dcafc89d.json")
XLSX = Path(r"C:\Users\Owner\Downloads\kumon_math_backup_20260731_1511.xlsx")


def main():
    import json

    msg = json.loads(JOB.read_text(encoding="utf-8"))["result"]["message"]
    # From job summary (ACCOUNT orphans were warnings; fatals = PRAGMA FK rows)
    account_orphans = {
        "classes.teacher_id->users.id": 1,  # remapping C
        "class_students.student_id->users.id": 2,  # A in excel
        "progress.user_id->users.id": 96,  # mostly A + remapping
        "adaptive_learning_logs.student_id->users.id": 338,  # A + remapping of id=1 rows
        "b4_chap2_visibility_audit_logs.student_id->users.id": 220,  # A
    }
    skill_orphans = {
        "skill_curriculum.skill_id->skills_info.skill_id": 24,  # A
        "textbook_examples.skill_id->skills_info.skill_id": 397,  # A
    }
    print("=== Fatal = PRAGMA foreign_key_check (1078) classification ===")
    total = 0
    for k, v in {**skill_orphans, **account_orphans}.items():
        print(f"  {k}: {v}")
        total += v
    print("sum", total, "(expected 1078)")

    xls = pd.read_excel(XLSX, sheet_name=None, engine="openpyxl")
    si = set(xls["skills_info"]["skill_id"].astype(str))
    sc_orph = [s for s in xls["skill_curriculum"]["skill_id"].astype(str) if s not in si]
    te_orph = [s for s in xls["textbook_examples"]["skill_id"].astype(str) if s not in si]
    print("excel curriculum orphan sample ids:", sc_orph[:5])
    print("excel textbook orphan sample skill_ids:", list(dict.fromkeys(te_orph))[:5])

    # categories
    print(
        """
Classification:
  A backup-original orphans: skill_curriculum 24 + textbook 397 + class_students 2
    + progress(~94) + adaptive(~304) + b4(220) ≈ majority of 1078
  B import order: NOT root cause (users/skills before children; restore order logged)
  C PK/identity remap: users.username unique matched leftover admin id=2589,
    so workbook users.id=1 never inserted → classes.teacher_id + adaptive(id=1) orphans
  D missing parent sheets: skills_info incomplete vs curriculum/examples; users incomplete vs logs
  E validator: correct — PRAGMA foreign_key_check properly failed
"""
    )


if __name__ == "__main__":
    main()
