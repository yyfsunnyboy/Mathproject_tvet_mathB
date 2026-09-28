import json
import sqlite3
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
c = sqlite3.connect("file:instance/kumon_math.db?mode=ro", uri=True)
c.row_factory = sqlite3.Row
rows = [
    dict(r)
    for r in c.execute(
        "select * from textbook_examples where source_volume='數學B3' and source_chapter like '第4章%' order by id"
    )
]
skills = {
    r["skill_id"]: dict(r)
    for r in c.execute("select skill_id, skill_ch_name, is_active from skills_info where skill_id like 'vh_數學B3_%_4_%'")
}
print("skills:")
for k, v in sorted(skills.items()):
    print(" ", k, v["skill_ch_name"], v["is_active"])
print("rows", len(rows), "ids", rows[0]["id"], rows[-1]["id"])
print(Counter((r["source_section"], r["skill_id"]) for r in rows))
print(Counter(r["problem_type"] for r in rows))
out = []
for r in rows:
    notes = r["notes"]
    try:
        notes = json.loads(notes) if notes else {}
    except Exception:
        pass
    out.append({
        "id": r["id"],
        "skill": (r["skill_id"] or "").replace("vh_數學B3_", ""),
        "sec": r["source_section"],
        "desc": r["source_description"],
        "para": r["source_paragraph"],
        "ptype": r["problem_type"],
        "q": r["problem_text"],
        "a": r["correct_answer"],
        "notes": notes,
    })
json.dump(out, open("scratch/b3_ch4/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
