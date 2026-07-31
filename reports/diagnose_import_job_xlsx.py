# -*- coding: utf-8 -*-
"""Diagnose backup Excel internal FK consistency and classify fatal causes."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

XLSX = Path(r"C:\Users\Owner\Downloads\kumon_math_backup_20260731_1511.xlsx")


def _ids(series):
    out = set()
    for v in series.dropna():
        try:
            if hasattr(v, "item"):
                v = v.item()
            if isinstance(v, float) and v.is_integer():
                v = int(v)
            elif isinstance(v, str) and v.strip().isdigit():
                v = int(v.strip())
            out.add(v)
        except Exception:
            out.add(v)
    return out


def main():
    xls = pd.read_excel(XLSX, sheet_name=None, engine="openpyxl")
    print("sheets", list(xls.keys()))
    print("=== source_rows ===")
    for name, df in xls.items():
        print(f"  {name}: {len(df)}")

    users = xls["users"]
    user_ids = _ids(users["id"])
    print("users count", len(users), "unique ids", len(user_ids))
    print("user id sample", sorted(list(user_ids), key=lambda x: (str(type(x)), str(x)))[:10])
    print("user roles", users["role"].value_counts().to_dict() if "role" in users.columns else None)

    # Account FK checks within Excel
    checks = [
        ("classes", "teacher_id", "users", "id"),
        ("class_students", "class_id", "classes", "id"),
        ("class_students", "student_id", "users", "id"),
        ("progress", "user_id", "users", "id"),
        ("adaptive_learning_logs", "student_id", "users", "id"),
        ("b4_chap2_visibility_audit_logs", "student_id", "users", "id"),
        ("quiz_attempts", "user_id", "users", "id"),
        ("quiz_attempts", "question_id", "questions", "id"),
        ("student_abilities", "user_id", "users", "id"),
    ]
    print("=== Excel-internal orphans (A if >0) ===")
    for child, fk, parent, pk in checks:
        if child not in xls or parent not in xls:
            print(f"  SKIP {child}.{fk} (missing sheet)")
            continue
        cdf, pdf = xls[child], xls[parent]
        if fk not in cdf.columns or pk not in pdf.columns:
            print(f"  SKIP {child}.{fk} (missing col)")
            continue
        parent_keys = _ids(pdf[pk])
        child_keys = []
        missing = []
        for v in cdf[fk].tolist():
            if pd.isna(v):
                continue
            raw = v
            try:
                if hasattr(v, "item"):
                    v = v.item()
                if isinstance(v, float) and float(v).is_integer():
                    v = int(v)
            except Exception:
                pass
            child_keys.append(v)
            if v not in parent_keys:
                missing.append(raw)
        print(f"  {child}.{fk} -> {parent}.{pk}: missing={len(missing)} / child_non_null={len(child_keys)}")
        if missing:
            print(f"    sample missing raw={missing[:5]!r}")
            # type analysis
            types = Counter(type(x).__name__ for x in missing[:50])
            print(f"    missing types={dict(types)}")
            print(f"    parent id types sample={[type(x).__name__ for x in list(parent_keys)[:5]]}")

    # skill_curriculum orphans in Excel
    si = set(xls["skills_info"]["skill_id"].astype(str))
    sc = xls["skill_curriculum"]
    sc_orphan = [s for s in sc["skill_id"].astype(str) if s not in si]
    print("=== skill_curriculum orphans in Excel ===")
    print("count", len(sc_orphan), "unique", len(set(sc_orphan)))
    print("sample", sc_orphan[:10])

    # textbook orphans in Excel
    te = xls["textbook_examples"]
    te_orphan = [s for s in te["skill_id"].astype(str) if s not in si]
    print("=== textbook_examples orphans in Excel ===")
    print("count", len(te_orphan), "unique", len(set(te_orphan)))
    print("sample unique", list(dict.fromkeys(te_orphan))[:10])

    # Compare progress user_ids vs users
    if "progress" in xls:
        pids = _ids(xls["progress"]["user_id"])
        print("progress unique user_ids", len(pids), "intersection", len(pids & user_ids), "only_in_progress", len(pids - user_ids))
        print("only_in_progress sample", list(pids - user_ids)[:10])

    if "adaptive_learning_logs" in xls:
        aids = _ids(xls["adaptive_learning_logs"]["student_id"])
        print("adaptive unique student_ids", len(aids), "intersection", len(aids & user_ids), "only_in_logs", len(aids - user_ids))
        print("only_in_logs sample", list(aids - user_ids)[:10])

    if "b4_chap2_visibility_audit_logs" in xls:
        bids = _ids(xls["b4_chap2_visibility_audit_logs"]["student_id"])
        print("b4 unique student_ids", len(bids), "intersection", len(bids & user_ids), "only_in_b4", len(bids - user_ids))

    # classes teacher
    if "classes" in xls:
        print("classes rows", xls["classes"].to_dict(orient="records"))
        print("teacher_id in users?", _ids(xls["classes"]["teacher_id"]) <= user_ids)

    # class_students
    if "class_students" in xls:
        cs = xls["class_students"]
        print("class_students student_ids", sorted(_ids(cs["student_id"])))
        print("missing students", sorted(_ids(cs["student_id"]) - user_ids))


if __name__ == "__main__":
    main()
