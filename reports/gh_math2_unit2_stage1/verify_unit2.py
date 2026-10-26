"""Stage 1 verification of 數學2 單元2 on a DB (read-only) + its uploads root: gate, counts, bindings, assets on disk, unit 1 untouched."""
import hashlib, json, sqlite3, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from core.textbook_stage1_gate import evaluate_stage1_gate
db, root = Path(sys.argv[1]), Path(sys.argv[2])
c = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True); c.row_factory = sqlite3.Row
rows = [dict(r) for r in c.execute("select * from textbook_examples where source_curriculum='general' and source_volume='數學2' and source_chapter='單元2 級數' order by id")]
gate = evaluate_stage1_gate(rows)
out = {"unit_rows": len(rows), "ids": [rows[0]["id"], rows[-1]["id"]], "gate": gate["status"], "stage1_ready": gate["stage1_ready"],
       "skills": dict(c.execute("select skill_id, count(*) from textbook_examples where source_volume='數學2' and source_chapter='單元2 級數' group by 1").fetchall()),
       "obsolete_left": c.execute("select count(*) from textbook_examples where id between 1334 and 1361").fetchone()[0],
       "no_anchor": [r["id"] for r in rows if not (json.loads(r["notes"]).get("question_anchor") or {}).get("anchor_id")],
       "bindings": [tuple(r) for r in c.execute("select skill_id, section, paragraph from skill_curriculum where volume='數學2' and chapter='單元2 級數' order by id")],
       "unit1_rows": c.execute("select count(*) from textbook_examples where source_chapter='單元1 數列與遞迴關係'").fetchone()[0],
       "total_rows": c.execute("select count(*) from textbook_examples").fetchone()[0]}
missing, bad = [], []
for r in rows:
    for a in json.loads(r["notes"]).get("image_assets") or []:
        f = root / a["path"]
        if not f.is_file(): missing.append(a["path"][-50:])
        elif hashlib.sha256(f.read_bytes()).hexdigest() != a["sha256"]: bad.append(a["path"][-50:])
out["assets"] = {"rows_with_assets": [r["id"] for r in rows if json.loads(r["notes"]).get("image_assets")], "missing": missing, "hash_mismatch": bad}
out["math"] = {"sqrt_empty_index": [r["id"] for r in rows if "\sqrt[]" in r["problem_text"]], "12739_12743_skill": [r["skill_id"] for r in rows if r["id"] in (12739, 12743)]}
print(json.dumps(out, ensure_ascii=False, indent=1))
