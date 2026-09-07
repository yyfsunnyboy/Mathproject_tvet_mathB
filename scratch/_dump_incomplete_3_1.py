# -*- coding: utf-8 -*-
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
conn.row_factory = sqlite3.Row

ids = [4618, 4628, 4629, 4706, 4716, 4717, 4718, 4719, 4720]
out = []
for eid in ids:
    r = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone()
    if not r:
        out.append({"example_id": eid, "missing": True})
        continue
    d = dict(r)
    t = conn.execute(
        "SELECT gencode_status, gencode_error_log, component_id, induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id=?",
        (eid,),
    ).fetchone()
    tracker = dict(t) if t else None
    payload = None
    if tracker and tracker.get("induced_spec_payload"):
        raw = tracker["induced_spec_payload"]
        try:
            payload = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            payload = {"raw": str(raw)[:500]}
    # also check classification tables
    out.append({
        "example_id": d["id"],
        "skill_id": d["skill_id"],
        "source_curriculum": d.get("source_curriculum"),
        "source_volume": d.get("source_volume"),
        "source_chapter": d.get("source_chapter"),
        "source_section": d.get("source_section"),
        "source_description": d.get("source_description"),
        "source_paragraph": d.get("source_paragraph"),
        "problem_type": d.get("problem_type"),
        "problem_text": d.get("problem_text"),
        "correct_answer": d.get("correct_answer"),
        "detailed_solution": d.get("detailed_solution"),
        "notes": d.get("notes"),
        "tracker_status": (tracker or {}).get("gencode_status"),
        "tracker_error": (tracker or {}).get("gencode_error_log"),
        "induced_problem_type_id": (payload or {}).get("problem_type_id") if isinstance(payload, dict) else None,
        "induced_keys": sorted(list(payload.keys()))[:40] if isinstance(payload, dict) else None,
    })

path = ROOT / "scratch/_b1_3_1_incomplete_db_dump.json"
path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote", path, "n=", len(out))
for row in out:
    print("---", row["example_id"], row.get("source_description"), row.get("problem_type"))
    print((row.get("problem_text") or "")[:180].replace("\n", " "))
    print("answer:", row.get("correct_answer"))
