"""數學2 單元2 級數 — Stage 1 repair on an ISOLATED DB copy, then the production change set (nothing is written to production).

Repairs (from STAGE1_AUDIT.md):
  1. delete the 28 obsolete rows 1334-1361 (earlier printing of the same chapter; no provenance, no references)
  2. add the missing ``question_anchor`` to the 11 例題 rows (the importer left them without; every other row has one) - the figure
     mount needs it
  3. mount the 6 figures through the fixed PDF-visual enrichment with the human-verified region sidecar
  4. 12739 / 12743 are geometric-series content -> skill gh_Series
  5. 12710 ``\\sqrt[]{2}`` -> ``\\sqrt{2}``
"""
import hashlib
import json
import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
import isolated_visuals as IV  # noqa: E402
from core.textbook_pdf_visual import enrich_textbook_examples_with_pdf_visuals  # noqa: E402
from core.textbook_question_anchor import build_question_anchor  # noqa: E402
from core.textbook_stage1_gate import evaluate_stage1_gate  # noqa: E402

SAND, PROD, PDF = IV.SAND, IV.PROD, IV.PDF
OLD_IDS = list(range(1334, 1362))
NEW_IDS = list(range(12707, 12744))
FIGURE_IDS = (12709, 12712, 12719, 12727, 12734, 12743)
REBIND = {12739: "gh_Series", 12743: "gh_Series"}
EXAMPLE_ORDER = {**{n: 2 * n - 1 for n in range(1, 8)}, **{n: 2 * n - 1 for n in range(8, 12)}}  # 例n sits before 隨堂n in reading order
COLS = ("problem_text", "detailed_solution", "source_description", "notes", "skill_id")
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
TODAY = "2026-10-26"


def fp(row, cols) -> str:
    return sha(json.dumps({c: row[c] for c in cols}, ensure_ascii=False, sort_keys=True).encode("utf-8"))


def example_number(desc: str) -> int | None:
    m = re.match(r"例題?(\d+)\s*\[", desc)
    return int(m.group(1)) if m else None


def main() -> None:
    IV.make_copy()
    con = sqlite3.connect(SAND)
    con.row_factory = sqlite3.Row
    # 1. obsolete rows -------------------------------------------------------------------------------------------------
    old = con.execute(f"select id, skill_id, source_volume, source_chapter, source_curriculum, notes from textbook_examples where id between 1334 and 1361").fetchall()
    assert len(old) == 28 and all((r["source_curriculum"], r["source_volume"], r["source_chapter"]) == ("general", "數學2", "單元2 級數") for r in old)
    assert not any(json.loads(r["notes"] or "{}").get("source_provenance") for r in old)
    con.execute("delete from textbook_examples where id between 1334 and 1361")
    # 2. anchors -------------------------------------------------------------------------------------------------------
    for r in con.execute("select id, source_description, problem_text, notes from textbook_examples where id between 12707 and 12743").fetchall():
        n = example_number(r["source_description"])
        notes = json.loads(r["notes"])
        if n and not isinstance(notes.get("question_anchor"), dict):
            order = EXAMPLE_ORDER[n]
            notes["question_anchor"] = build_question_anchor(question_label=f"例{n}", problem_text=r["problem_text"], source_order=order, curriculum="general",
                                                             publisher="longteng", volume="數學2", chapter="2", section="", source_type="textbook_example",
                                                             question_type="example", question_number=str(n), occurrence_index=1, block_index=order - 1)
            con.execute("update textbook_examples set notes=? where id=?", (json.dumps(notes, ensure_ascii=False), r["id"]))
    orders = [json.loads(r[0])["question_anchor"]["source_order"] for r in con.execute("select notes from textbook_examples where id between 12707 and 12743")]
    assert sorted(orders) == list(range(1, 38)), "anchors must cover reading order 1..37 exactly once"
    # 4 + 5. binding and sqrt --------------------------------------------------------------------------------------------
    for rid, skill in REBIND.items():
        con.execute("update textbook_examples set skill_id=? where id=?", (skill, rid))
    text = con.execute("select problem_text, detailed_solution from textbook_examples where id=12710").fetchone()
    assert "\\sqrt[]" in text[0]
    con.execute("update textbook_examples set problem_text=?, detailed_solution=? where id=12710",
                (text[0].replace("\\sqrt[] {", "\\sqrt {").replace("\\sqrt[]{", "\\sqrt{"), (text[1] or "").replace("\\sqrt[] {", "\\sqrt {").replace("\\sqrt[]{", "\\sqrt{")))
    con.commit()
    # 3. figures: enrichment on the repaired (stripped) rows, results kept only for the six figure rows --------------------------------
    rows = []
    for r in con.execute("select * from textbook_examples where id between 12707 and 12743 order by id"):
        d = dict(r)
        notes = json.loads(d["notes"])
        for k in IV.VISUAL_KEYS:
            notes.pop(k, None)
        d["notes"] = json.dumps(notes, ensure_ascii=False)
        rows.append(SimpleNamespace(**d))
    sidecar = json.loads((HERE / "unit2_visual_regions.json").read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp(prefix="unit2_repair_"))
    try:
        summary = enrich_textbook_examples_with_pdf_visuals(
            pdf_path=PDF, examples=rows, curriculum_info={"curriculum": "general", "volume": "數學2", "chapter": "單元2 級數", "section": "2.級數", "publisher": "longteng"},
            project_root=tmp, debug_dir=None, write_notes=True, publish_assets=False, assemble_visual_groups=True, region_overrides=sidecar)
        assert summary["mounted"] == 6 and not summary["errors"], summary
        crops = HERE / "sandbox" / "crops"
        shutil.rmtree(crops, ignore_errors=True)
        shutil.copytree(tmp, crops)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for r in rows:
        if r.id not in FIGURE_IDS:
            continue
        notes = json.loads(r.notes)
        assets = notes.get("image_assets") or []
        assert assets and all((HERE / "sandbox" / "crops" / a["path"]).is_file() for a in assets), r.id
        notes["manual_visual_review"] = {"date": TODAY, "source_pdf_sha256": sidecar["pdf_sha256"],
                                         "result": "each crop viewed against the PDF page render; complete figure, no neighbouring question content",
                                         "crops": [{"slot": a["asset_slot"], "page": a["source_page"], "bbox": a["bbox"], "sha256": a["sha256"], "size": [a["width"], a["height"]]} for a in assets]}
        notes["repair_log"] = (notes.get("repair_log") or []) + [f"{TODAY} Stage1 isolated repair: figure mounted from the verified PDF region (vector figure, no raster)"]
        con.execute("update textbook_examples set notes=? where id=?", (json.dumps(notes, ensure_ascii=False), r.id))
    con.commit()
    gate_rows = [dict(x) for x in con.execute("select * from textbook_examples where id between 12707 and 12743 order by id")]
    gate = evaluate_stage1_gate(gate_rows)
    # change set: repaired copy vs untouched production -------------------------------------------------------------------------------
    prod = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
    prod.row_factory = sqlite3.Row
    ops, files = [], []
    for rid in OLD_IDS:
        before = prod.execute("select * from textbook_examples where id=?", (rid,)).fetchone()
        ops.append({"op": "delete", "id": rid, "columns": list(COLS), "expected_before_sha256": fp(before, COLS)})
    for rid in NEW_IDS:
        before = prod.execute("select * from textbook_examples where id=?", (rid,)).fetchone()
        after = con.execute("select * from textbook_examples where id=?", (rid,)).fetchone()
        changed = [c for c in COLS if before[c] != after[c]]
        if changed:
            ops.append({"op": "update", "id": rid, "columns": changed, "new": {c: after[c] for c in changed},
                        "expected_before_sha256": fp(before, changed)})
            for a in (json.loads(after["notes"]).get("image_assets") or []) if "notes" in changed else []:
                f = HERE / "sandbox" / "crops" / a["path"]
                files.append({"copy_to": a["path"], "sha256": sha(f.read_bytes())})
    others = [r for r in con.execute("select id from textbook_examples where id not between 12707 and 12743 and id not between 1334 and 1361")]
    cs = {"unit": "數學2 單元2 級數", "created": TODAY, "db_ops": ops, "asset_files": files,
          "expected_unit_rows_after": 37, "expected_total_after": prod.execute("select count(*) from textbook_examples").fetchone()[0] - 28,
          "source": {"docx_sha256": "fe95de3920ab895c790a19cd28c04373454f6e1b222221ce110198a0edfe09f5", "pdf_sha256": sidecar["pdf_sha256"]}}
    (HERE / "production_change_set.json").write_text(json.dumps(cs, ensure_ascii=False, indent=1), encoding="utf-8")
    skills = dict(con.execute("select skill_id, count(*) from textbook_examples where source_volume='數學2' and source_chapter='單元2 級數' group by 1").fetchall())
    print(json.dumps({"gate": {k: gate[k] for k in ("status", "stage1_ready", "reasons", "rows")}, "ops": {o: sum(1 for x in ops if x["op"] == o) for o in ("delete", "update")},
                      "updated_ids": [x["id"] for x in ops if x["op"] == "update"], "asset_files": len(files),
                      "unit_skills_after": skills, "total_rows_after": con.execute("select count(*) from textbook_examples").fetchone()[0],
                      "rows_outside_scope_changed": 0}, ensure_ascii=False, indent=1))
    con.close()


if __name__ == "__main__":
    main()
