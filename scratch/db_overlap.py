# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

conn = sqlite3.connect(Path(r"D:\Python\Mathproject_tvet_mathB\instance\kumon_math.db"))
c = conn.cursor()

print("=== vocational skill_curriculum sample ===")
for row in c.execute(
    "SELECT skill_id, volume, chapter, section FROM skill_curriculum WHERE curriculum='vocational' LIMIT 12"
):
    print(row)

print("\n=== vocational distinct volume/chapter ===")
for row in c.execute(
    "SELECT DISTINCT volume, chapter FROM skill_curriculum WHERE curriculum='vocational' ORDER BY volume, chapter"
):
    print(row)

print("\n=== class student practice overlap ===")
print(
    c.execute(
        """
SELECT
  COUNT(DISTINCT cs.student_id),
  COUNT(DISTINCT CASE WHEN al.student_id IS NOT NULL THEN cs.student_id END),
  COUNT(DISTINCT CASE WHEN b4.student_id IS NOT NULL THEN cs.student_id END),
  COUNT(DISTINCT CASE WHEN pr.user_id IS NOT NULL THEN cs.student_id END)
FROM class_students cs
LEFT JOIN (SELECT DISTINCT student_id FROM adaptive_learning_logs) al ON al.student_id=cs.student_id
LEFT JOIN (SELECT DISTINCT student_id FROM b4_chap2_visibility_audit_logs WHERE record_kind='deterministic_answer') b4 ON b4.student_id=cs.student_id
LEFT JOIN (SELECT DISTINCT user_id FROM progress WHERE questions_solved>0) pr ON pr.user_id=cs.student_id
WHERE cs.class_id=1
"""
    ).fetchone()
)

print("\n=== execution_latency distribution (adaptive) ===")
print(
    c.execute(
        "SELECT MIN(execution_latency), MAX(execution_latency), AVG(execution_latency), COUNT(*) FROM adaptive_learning_logs"
    ).fetchone()
)

print("\n=== progress: can we get correct/wrong? ===")
print(c.execute("PRAGMA table_info(progress)").fetchall())

print("\n=== map b4 skill to curriculum unit ===")
for row in c.execute(
    """
SELECT b.skill_id, sc.chapter, sc.section, si.skill_ch_name, COUNT(*) cnt
FROM b4_chap2_visibility_audit_logs b
LEFT JOIN skill_curriculum sc ON sc.skill_id=b.skill_id AND sc.curriculum='vocational'
LEFT JOIN skills_info si ON si.skill_id=b.skill_id
WHERE b.record_kind='deterministic_answer'
GROUP BY b.skill_id, sc.chapter, sc.section, si.skill_ch_name
ORDER BY cnt DESC LIMIT 10
"""
):
    print(row)

print("\n=== adaptive family -> skill bridge ===")
for row in c.execute(
    """
SELECT al.target_family_id, sfb.skill_id, sfb.family_name, COUNT(*) cnt
FROM adaptive_learning_logs al
LEFT JOIN skill_family_bridge sfb ON sfb.family_id=al.target_family_id
GROUP BY al.target_family_id, sfb.skill_id, sfb.family_name
ORDER BY cnt DESC LIMIT 10
"""
):
    print(row)

print("\n=== teachers and classes ===")
for row in c.execute(
    "SELECT u.id, u.username, u.role, c.id, c.name FROM users u LEFT JOIN classes c ON c.teacher_id=u.id WHERE u.role='teacher'"
):
    print(row)

conn.close()
