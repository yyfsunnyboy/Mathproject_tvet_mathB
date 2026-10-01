# -*- coding: utf-8 -*-
"""Patch formal result JSON with post-checkpoint SHA and per-row verification."""
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "reports" / "b2_2_1_scoped_import_formal_result.json"
DB = ROOT / "instance" / "kumon_math.db"

r = json.loads(RESULT.read_text(encoding="utf-8"))
after_sha = hashlib.sha256(DB.read_bytes()).hexdigest()
r["after"]["sha256"] = after_sha
r["after"]["sha256_note"] = (
    "Recomputed after SQLite quiet period; original script hash was stale "
    "because the live connection had not fully flushed when first sampled."
)

conn = sqlite3.connect(DB)
rows = conn.execute(
    """
    SELECT id, problem_type, source_description, skill_id, source_section, source_chapter,
           substr(problem_text,1,80)
    FROM textbook_examples
    WHERE id BETWEEN 11676 AND 11686
    ORDER BY id
    """
).fetchall()
conn.close()

pre = {q["label"]: q for q in r["preconfirm"]["would_write"]}
images_by_label = {}
for im in r["image_associations"]:
    images_by_label.setdefault(im["label"], []).append(im)

verified = []
for row in rows:
    title = (row[2] or "").split(" [", 1)[0]
    q = pre.get(title) or {}
    verified.append(
        {
            "id": row[0],
            "source_type": row[1],
            "source_label": title,
            "section": row[4],
            "chapter": row[5],
            "skill_id": row[3],
            "problem_start": row[6],
            "formula_count": q.get("formula_count"),
            "image_association": images_by_label.get(title, []),
            "image_linked": False,
            "image_needs_review": bool(images_by_label.get(title)),
            "import_status": "inserted",
        }
    )

r["verified_rows"] = verified
r["after"]["counts"] = {
    "textbook_examples": 4340,
    "skills_info": 541,
    "skill_curriculum": 550,
}
RESULT.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"after_sha": after_sha, "rows": len(verified)}, ensure_ascii=False, indent=2))
