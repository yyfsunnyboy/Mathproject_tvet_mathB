# -*- coding: utf-8 -*-
"""Post-implementation audit helper."""
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from models import User

DB = r"D:\Python\Mathproject_tvet_mathB\instance\kumon_math.db"

print("=== A. DB student overlap b4 + adaptive ===")
cur = sqlite3.connect(DB).cursor()
rows = cur.execute(
    """
SELECT b.student_id, COUNT(DISTINCT b.id), COUNT(DISTINCT a.log_id)
FROM b4_chap2_visibility_audit_logs b
INNER JOIN adaptive_learning_logs a ON a.student_id = b.student_id
WHERE b.record_kind = 'deterministic_answer'
GROUP BY b.student_id
"""
).fetchall()
print("students_in_both:", len(rows))
for r in rows[:8]:
    print(r)

print("\n=== same-minute heuristic ===")
rows2 = cur.execute(
    """
SELECT b.student_id, strftime('%Y-%m-%d %H:%M', b.created_at) AS minute,
       COUNT(*) AS b4_n,
       (SELECT COUNT(*) FROM adaptive_learning_logs a
        WHERE a.student_id = b.student_id
          AND strftime('%Y-%m-%d %H:%M', a.created_at) = strftime('%Y-%m-%d %H:%M', b.created_at)) AS adp_n
FROM b4_chap2_visibility_audit_logs b
WHERE b.record_kind = 'deterministic_answer'
GROUP BY b.student_id, minute
HAVING adp_n > 0
LIMIT 15
"""
).fetchall()
print("same_minute_pairs:", len(rows2))
for r in rows2[:8]:
    print(r)

print("\n=== C. HTML smoke audit ===")
app = create_app()
with app.app_context():
    admin = User.query.filter_by(username="admin").first()
    client = app.test_client()
    with client.session_transaction() as s:
        s["_user_id"] = str(admin.id)
        s["_fresh"] = True

    urls = [
        "/teacher/analysis",
        "/teacher/analysis?class_id=1",
        "/teacher/analysis?class_id=1&student_id=2555",
    ]
    for url in urls:
        resp = client.get(url)
        text = resp.get_data(as_text=True)
        issues = []
        if re.search(r">\s*None\s*<", text) or " None " in text:
            issues.append("None")
        if "NaN" in text:
            issues.append("NaN")
        if "mistakeChart" in text:
            issues.append("old_mistake_chart")
        if ">0%<" in text.replace(" ", ""):
            issues.append("zero_percent")
        no_data = text.count("尚無資料") if "class_id=1" in url else None
        no_practice = text.count("尚無練習紀錄") if "student_id" in url else None
        print(f"{resp.status_code} {url}")
        print(f"  issues={issues or 'none'} no_data={no_data} no_practice={no_practice}")

    r = client.get("/teacher/analysis?class_id=1")
    t = r.get_data(as_text=True)
    student_links = len(re.findall(r"student_id=\d+", t))
    print(f"class page student_id links: {student_links}")
