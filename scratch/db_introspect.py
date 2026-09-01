import sqlite3
from pathlib import Path

db = Path(r"D:\Python\Mathproject_tvet_mathB\instance\kumon_math.db")
conn = sqlite3.connect(db)
c = conn.cursor()

print("=== TABLES ===")
for row in c.execute(
    "SELECT name, type FROM sqlite_master WHERE type IN ('table','index') ORDER BY type, name"
):
    print(row)

print("\n=== TABLE ROW COUNTS ===")
tables = [
    r[0]
    for r in c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
]
for t in tables:
    try:
        cnt = c.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
        print(f"{t}: {cnt}")
    except Exception as e:
        print(f"{t}: ERROR {e}")

key_tables = [
    "users",
    "classes",
    "class_students",
    "quiz_attempts",
    "questions",
    "mistake_logs",
    "adaptive_learning_logs",
    "b4_chap2_visibility_audit_logs",
    "progress",
    "skill_curriculum",
    "skills_info",
    "skill_family_bridge",
    "learning_diagnosis",
    "exam_analysis",
    "student_abilities",
    "node_competency",
]

print("\n=== PRAGMA table_info (key tables) ===")
for t in key_tables:
    try:
        cols = c.execute(f"PRAGMA table_info([{t}])").fetchall()
        if not cols:
            print(f"\n--- {t}: NOT FOUND ---")
            continue
        print(f"\n--- {t} ---")
        for col in cols:
            print(f"  {col[1]} {col[2]} pk={col[5]} notnull={col[3]} default={col[4]}")
    except Exception as e:
        print(f"{t}: {e}")

print("\n=== SAMPLE: users (roles) ===")
for row in c.execute(
    "SELECT id, username, role, created_at FROM users ORDER BY id LIMIT 15"
):
    print(row)
print("role counts:", c.execute("SELECT role, COUNT(*) FROM users GROUP BY role").fetchall())

print("\n=== SAMPLE: classes ===")
for row in c.execute(
    "SELECT c.id, c.name, c.teacher_id, u.username, (SELECT COUNT(*) FROM class_students cs WHERE cs.class_id=c.id) FROM classes c JOIN users u ON u.id=c.teacher_id"
):
    print(row)

print("\n=== SAMPLE: class_students ===")
for row in c.execute(
    "SELECT cs.id, cs.class_id, c.name, cs.student_id, u.username FROM class_students cs JOIN classes c ON c.id=cs.class_id JOIN users u ON u.id=cs.student_id LIMIT 20"
):
    print(row)

print("\n=== SAMPLE: quiz_attempts ===")
for row in c.execute(
    "SELECT id, user_id, question_id, is_correct, duration_seconds, timestamp FROM quiz_attempts ORDER BY timestamp DESC LIMIT 5"
):
    print(row)
print("quiz_attempts stats:", c.execute(
    "SELECT COUNT(*), SUM(CASE WHEN is_correct=1 THEN 1 ELSE 0 END), SUM(CASE WHEN is_correct=0 THEN 1 ELSE 0 END), MIN(timestamp), MAX(timestamp), AVG(duration_seconds), COUNT(duration_seconds) FROM quiz_attempts"
).fetchone())

print("\n=== SAMPLE: questions ===")
for row in c.execute(
    "SELECT id, skill_id, substr(content,1,80), difficulty_level FROM questions LIMIT 5"
):
    print(row)

print("\n=== SAMPLE: adaptive_learning_logs ===")
for row in c.execute(
    "SELECT log_id, student_id, session_id, step_number, target_family_id, is_correct, current_apr, execution_latency, created_at FROM adaptive_learning_logs ORDER BY created_at DESC LIMIT 5"
):
    print(row)
print("adaptive stats:", c.execute(
    "SELECT COUNT(*), SUM(CASE WHEN is_correct=1 THEN 1 ELSE 0 END), MIN(created_at), MAX(created_at), AVG(execution_latency) FROM adaptive_learning_logs"
).fetchone())

print("\n=== SAMPLE: b4_chap2_visibility_audit_logs ===")
for row in c.execute(
    "SELECT id, student_id, skill_id, problem_type_id, is_correct, user_answer, expected_answer, created_at, record_kind FROM b4_chap2_visibility_audit_logs ORDER BY created_at DESC LIMIT 8"
):
    print(row)
print("b4 audit stats:", c.execute(
    "SELECT COUNT(*), SUM(CASE WHEN is_correct=1 THEN 1 ELSE 0 END), COUNT(DISTINCT student_id), MIN(created_at), MAX(created_at) FROM b4_chap2_visibility_audit_logs WHERE record_kind='deterministic_answer'"
).fetchone())

print("\n=== overlap class students with practice ===")
for row in c.execute("""
SELECT cs.student_id, u.username, u.real_name,
  COALESCE(al.cnt,0) as adaptive_cnt,
  COALESCE(b4.cnt,0) as b4_cnt,
  COALESCE(p.cnt,0) as progress_skills
FROM class_students cs
JOIN users u ON u.id=cs.student_id
LEFT JOIN (SELECT student_id, COUNT(*) cnt FROM adaptive_learning_logs GROUP BY student_id) al ON al.student_id=cs.student_id
LEFT JOIN (SELECT student_id, COUNT(*) cnt FROM b4_chap2_visibility_audit_logs WHERE record_kind='deterministic_answer' GROUP BY student_id) b4 ON b4.student_id=cs.student_id
LEFT JOIN (SELECT user_id, COUNT(*) cnt FROM progress WHERE questions_solved>0 GROUP BY user_id) p ON p.user_id=cs.student_id
WHERE cs.class_id=1
ORDER BY adaptive_cnt DESC, b4_cnt DESC
LIMIT 15
"""):
    print(row)

print("\n=== skill_curriculum distinct units ===")
for row in c.execute(
    "SELECT DISTINCT curriculum, volume, chapter, section FROM skill_curriculum ORDER BY curriculum, volume, chapter, section LIMIT 25"
):
    print(row)

print("\n=== b4 audit skill distribution ===")
for row in c.execute(
    "SELECT skill_id, COUNT(*), SUM(CASE WHEN is_correct=1 THEN 1 ELSE 0 END) FROM b4_chap2_visibility_audit_logs WHERE record_kind='deterministic_answer' GROUP BY skill_id ORDER BY COUNT(*) DESC LIMIT 15"
):
    print(row)

print("\n=== users real_name sample ===")
for row in c.execute("SELECT id, username, real_name FROM users WHERE real_name IS NOT NULL LIMIT 10"):
    print(row)

print("\n=== class name repr ===")
for row in c.execute("SELECT id, name, teacher_id FROM classes"):
    print(repr(row))

print("\n=== SAMPLE: mistake_logs ===")
for row in c.execute(
    "SELECT id, user_id, skill_id, substr(question_content,1,50), created_at FROM mistake_logs ORDER BY created_at DESC LIMIT 5"
):
    print(row)

print("\n=== SAMPLE: skill_curriculum (units) ===")
for row in c.execute(
    "SELECT skill_id, curriculum, grade, volume, chapter, section, paragraph FROM skill_curriculum ORDER BY display_order LIMIT 15"
):
    print(row)
print("distinct sections:", c.execute(
    "SELECT DISTINCT chapter, section FROM skill_curriculum ORDER BY chapter, section LIMIT 20"
).fetchall())

print("\n=== SAMPLE: skills_info ===")
for row in c.execute(
    "SELECT skill_id, skill_ch_name, category FROM skills_info LIMIT 10"
):
    print(row)

print("\n=== SAMPLE: skill_family_bridge ===")
for row in c.execute(
    "SELECT skill_id, family_id, family_name, chapter, section FROM skill_family_bridge LIMIT 10"
):
    print(row)

print("\n=== SAMPLE: progress ===")
for row in c.execute(
    "SELECT user_id, skill_id, questions_solved, consecutive_correct, last_practiced FROM progress LIMIT 10"
):
    print(row)

conn.close()
