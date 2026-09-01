# -*- coding: utf-8 -*-
"""Investigate 315001 practice data flow in production DB."""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "instance" / "kumon_math.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("=" * 60)
print("1. USER IDENTITY")
u = c.execute("SELECT id, username, real_name, role FROM users WHERE username='315001'").fetchone()
if not u:
    print("USER NOT FOUND")
    raise SystemExit(1)
print(dict(u))
uid = u["id"]

print("\nCLASS MEMBERSHIP")
for r in c.execute(
    """
    SELECT cs.class_id, c.name, cs.seat_no
    FROM class_students cs JOIN classes c ON c.id=cs.class_id
    WHERE cs.student_id=?
    """,
    (uid,),
):
    print(dict(r))

print("\n" + "=" * 60)
print("2. B4 AUDIT")
b4_cols = [r[1] for r in c.execute("PRAGMA table_info(b4_chap2_visibility_audit_logs)")]
print("columns:", b4_cols)
b4_rows = c.execute(
    """
    SELECT id, student_id, session_id, skill_id, problem_type_id, is_correct, record_kind, created_at
    FROM b4_chap2_visibility_audit_logs
    WHERE student_id=?
    ORDER BY created_at DESC
    """,
    (uid,),
).fetchall()
print(f"count for student_id={uid}:", len(b4_rows))
for r in b4_rows:
    print(dict(r))
det = [r for r in b4_rows if r["record_kind"] == "deterministic_answer"]
print("deterministic_answer count:", len(det))

print("\n" + "=" * 60)
print("3. ADAPTIVE LEARNING LOGS")
try:
    ad_cols = [r[1] for r in c.execute("PRAGMA table_info(adaptive_learning_logs)")]
    print("columns:", ad_cols)
    ad_rows = c.execute(
        "SELECT * FROM adaptive_learning_logs WHERE student_id=? ORDER BY created_at DESC",
        (uid,),
    ).fetchall()
    print(f"count for student_id={uid}:", len(ad_rows))
    for r in ad_rows[:20]:
        d = dict(r)
        # trim long fields
        for k in list(d.keys()):
            if isinstance(d[k], str) and len(d[k]) > 80:
                d[k] = d[k][:80] + "..."
        print(d)
except Exception as e:
    print("ERROR:", e)

print("\n" + "=" * 60)
print("4. PROGRESS")
prog = c.execute(
    "SELECT * FROM progress WHERE user_id=? ORDER BY last_practiced DESC",
    (uid,),
).fetchall()
print(f"count: {len(prog)}")
for r in prog:
    print(dict(r))

print("\n" + "=" * 60)
print("5. QUIZ_ATTEMPTS")
try:
    qa_cols = [r[1] for r in c.execute("PRAGMA table_info(quiz_attempts)")]
    print("columns:", qa_cols)
    id_cols = [col for col in qa_cols if "user" in col.lower() or "student" in col.lower()]
    print("id-like cols:", id_cols)
    queries = []
    if "student_id" in qa_cols:
        queries.append(("student_id", uid))
    if "user_id" in qa_cols:
        queries.append(("user_id", uid))
    seen = set()
    for col, val in queries:
        for r in c.execute(f"SELECT * FROM quiz_attempts WHERE {col}=? ORDER BY id DESC", (val,)):
            rid = r["id"] if "id" in r.keys() else id(r)
            if rid not in seen:
                seen.add(rid)
                print(dict(r))
    if not queries:
        print("no student/user id column found")
except Exception as e:
    print("table missing or error:", e)

print("\n" + "=" * 60)
print("6. MISTAKE LOGS")
for tname in ["mistake_logs", "mistakes", "user_mistakes"]:
    exists = c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tname,)
    ).fetchone()
    if not exists:
        continue
    cols = [r[1] for r in c.execute(f"PRAGMA table_info({tname})")]
    print(f"{tname} columns:", cols)
    for col in cols:
        if "user" in col.lower() or "student" in col.lower():
            for r in c.execute(f"SELECT * FROM {tname} WHERE {col}=?", (uid,)):
                print(dict(r))

print("\n" + "=" * 60)
print("7. ALL SUSPECT TABLES")
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
keywords = ("attempt", "answer", "practice", "history", "log", "result", "record", "audit", "mistake", "quiz")
suspect = [t for t in tables if any(k in t.lower() for k in keywords)]
for t in suspect:
    cols = [r[1] for r in c.execute(f"PRAGMA table_info({t})")]
    id_cols = [col for col in cols if col in ("student_id", "user_id") or "student" in col.lower() or col == "user_id"]
    if not id_cols:
        continue
    total = 0
    for col in id_cols:
        try:
            n = c.execute(f"SELECT COUNT(*) FROM {t} WHERE {col}=?", (uid,)).fetchone()[0]
            if n:
                print(f"{t}.{col} = {n}")
                total += n
                sample = c.execute(f"SELECT * FROM {t} WHERE {col}=? ORDER BY rowid DESC LIMIT 3", (uid,)).fetchall()
                for r in sample:
                    d = dict(r)
                    for k in list(d.keys()):
                        if isinstance(d[k], str) and len(d[k]) > 100:
                            d[k] = d[k][:100] + "..."
                    print("  sample:", d)
        except Exception:
            pass

print("\n" + "=" * 60)
print("8. RECENT B4/ADAPTIVE BY TIME (any student_id)")
recent_b4 = c.execute(
    """
    SELECT id, student_id, skill_id, is_correct, record_kind, created_at
    FROM b4_chap2_visibility_audit_logs
    ORDER BY created_at DESC LIMIT 15
    """
).fetchall()
print("Recent b4 (all students):")
for r in recent_b4:
    print(dict(r))

recent_ad = c.execute(
    """
    SELECT log_id, student_id, target_family_id, is_correct, created_at
    FROM adaptive_learning_logs
    ORDER BY created_at DESC LIMIT 15
    """
).fetchall()
print("\nRecent adaptive (all students):")
for r in recent_ad:
    print(dict(r))

print("\n" + "=" * 60)
print("9. MISTAKE / QUIZ for uid")
for t in ["mistake_logs", "quiz_attempts"]:
    n = c.execute(f"SELECT COUNT(*) FROM {t} WHERE user_id=?", (uid,)).fetchone()[0]
    print(f"{t}: {n}")

print("\n" + "=" * 60)
print("10. ALL TABLES WITH DATA FOR uid=2554")
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
for t in tables:
    cols = [r[1] for r in c.execute(f"PRAGMA table_info({t})")]
    for col in cols:
        if col in ("student_id", "user_id"):
            try:
                n = c.execute(f"SELECT COUNT(*) FROM {t} WHERE {col}=?", (uid,)).fetchone()[0]
                if n:
                    print(f"  {t}.{col} = {n}")
            except Exception:
                pass

conn.close()
