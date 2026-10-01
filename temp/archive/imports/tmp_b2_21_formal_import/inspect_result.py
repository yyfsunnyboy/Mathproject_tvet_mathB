# -*- coding: utf-8 -*-
import json
import sqlite3
from pathlib import Path

r = json.loads(Path("reports/b2_2_1_scoped_import_formal_result.json").read_text(encoding="utf-8"))
print("report after sha", r["after"]["sha256"])
print("report before sha", r["before"]["sha256"])
print("image_assoc count", len(r["image_associations"]))
print(json.dumps(r["image_associations"], ensure_ascii=False, indent=2))
print("PRE_FORMULAS")
for q in r["preconfirm"]["would_write"]:
    print(q["index"], q["label"], q["formula_count"], q["image_count"])

conn = sqlite3.connect("instance/kumon_math.db")
for i in (11676, 11678, 11682, 11686):
    notes = conn.execute("SELECT notes FROM textbook_examples WHERE id=?", (i,)).fetchone()[0]
    print("NOTES", i)
    print(notes[:500] if notes else None)
    print("---")

mpf = conn.execute(
    """
    SELECT COUNT(*) FROM textbook_examples
    WHERE id BETWEEN 11676 AND 11686
      AND (problem_text LIKE '%MATH_PARSE_FAILED%'
           OR detailed_solution LIKE '%MATH_PARSE_FAILED%')
    """
).fetchone()[0]
print("MPF", mpf)
print(
    "outline",
    conn.execute(
        """
        SELECT skill_id, chapter, section FROM skill_curriculum
        WHERE volume='數學B2' AND section LIKE '%2-1%' AND skill_id LIKE 'outline%'
        """
    ).fetchall(),
)
# check student tables vs backup
backup = Path(r["backup"]["backup_path"])
bconn = sqlite3.connect(backup)
for t in ("adaptive_learning_logs", "practice_attempts", "class_students"):
    a = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    b = bconn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"{t}: before={b} after={a} same={a==b}")
bconn.close()
conn.close()
