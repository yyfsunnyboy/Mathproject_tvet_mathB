"""Isolated rebuild of the unit-1 figure assets through the fixed PDF-visual enrichment.

* Source rows: the repaired sandbox copy, visual state stripped (as after a fresh text import); opened read-only.
* Enrichment runs with write_notes=True on in-memory row objects and a temp project root, so nothing touches the
  production DB or production uploads/.
* Pass A: detector only (shows what is attached / left for review without human regions).
* Pass B: detector + the human-verified region sidecar for the questions the detector cannot place.
Compares every mounted crop with the hand-reviewed crops from the Stage 1 repair (sha256) and prints the Stage 1 gate.
"""
import json
import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from core.textbook_pdf_visual import enrich_textbook_examples_with_pdf_visuals, fingerprint_file  # noqa: E402
from core.textbook_stage1_gate import evaluate_stage1_gate  # noqa: E402

HERE = Path(__file__).resolve().parent
SAND = ROOT / "reports/gh_math2_unit1_stage1/sandbox/kumon_math_copy.db"
PDF = ROOT / "textbook_import/uploaded_sources/general/數學2/f2bef2bd0e2b_單元01-數列與遞迴關係.pdf"
SIDECAR = HERE / "unit1_visual_regions.json"
VISUAL_KEYS = ("image_assets", "pdf_visual_enrichment", "pdf_visual_status", "visual_required_missing", "image_warning", "has_image",
               "needs_review", "visual_status", "needs_image_review", "manual_visual_review", "manual_stem_review",
               "needs_review_before_visual", "image_warning_resolved_by", "review_required_by_confidence")


def build_sidecar() -> dict:
    """Region list the Stage 1 reviewer verified, keyed by question label (no ids)."""
    ns: dict = {"__file__": str(ROOT / "reports/gh_math2_unit1_stage1/stage1_repair.py")}
    src = (ROOT / "reports/gh_math2_unit1_stage1/stage1_repair.py").read_text(encoding="utf-8").split("def make_copy")[0]
    exec(compile(src, "stage1_repair", "exec"), ns)
    con = sqlite3.connect(f"file:{SAND.as_posix()}?mode=ro", uri=True)
    regions = {}
    for qid, specs in ns["IMAGE_FIXES"].items():
        label = re.sub(r"\s*\[.*$", "", con.execute("select source_description from textbook_examples where id=?", (qid,)).fetchone()[0])
        regions[label] = [{"page": p, "bbox": b, "why": w} for _slot, p, b, w in specs]
    return {
        "pdf_sha256": fingerprint_file(PDF), "verified_by": "claude Stage 1 review (pending teacher confirmation)",
        "verified_on": ns["TODAY"], "regions": regions,
    }


def fresh_rows():
    con = sqlite3.connect(f"file:{SAND.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = []
    for r in con.execute("select * from textbook_examples where id between 12667 and 12706 order by id"):
        d = dict(r)
        notes = json.loads(d["notes"])
        for k in VISUAL_KEYS:
            notes.pop(k, None)
        d["notes"] = json.dumps(notes, ensure_ascii=False)
        rows.append(SimpleNamespace(**d))
    return rows


def run(overrides, root: Path):
    rows = fresh_rows()
    summary = enrich_textbook_examples_with_pdf_visuals(
        pdf_path=PDF, examples=rows,
        curriculum_info={"curriculum": "general", "volume": "數學2", "chapter": "單元1 數列與遞迴關係", "section": "1.數列與遞迴關係", "publisher": "longteng"},
        project_root=root, debug_dir=None, write_notes=True, publish_assets=False, assemble_visual_groups=True, region_overrides=overrides)
    return rows, summary


def reviewed_sha() -> dict:
    out = {}
    con = sqlite3.connect(f"file:{SAND.as_posix()}?mode=ro", uri=True)
    for qid, notes in con.execute("select id, notes from textbook_examples where id between 12667 and 12706"):
        for a in json.loads(notes).get("image_assets") or []:
            out[(qid, a["asset_slot"])] = a["sha256"]
    return out


sidecar = build_sidecar()
SIDECAR.write_text(json.dumps(sidecar, ensure_ascii=False, indent=1), encoding="utf-8")
ref = reviewed_sha()
for name, overrides in (("A detector only", {}), ("B detector + verified regions", sidecar)):
    tmp = Path(tempfile.mkdtemp(prefix="unit1_visuals_"))
    try:
        rows, summary = run(overrides if overrides else {"regions": {}}, tmp)
        gate = evaluate_stage1_gate([{"id": r.id, "problem_text": r.problem_text, "detailed_solution": r.detailed_solution,
                                      "problem_type": r.problem_type, "source_description": r.source_description, "notes": r.notes} for r in rows])
        match = diff = 0
        for r in rows:
            for a in json.loads(r.notes).get("image_assets") or []:
                if ref.get((r.id, a["asset_slot"])) == a["sha256"]:
                    match += 1
                else:
                    diff += 1
        print(f"[{name}] mounted={summary['mounted']} overrides_applied={len(summary.get('manual_region_overrides_applied') or [])} "
              f"crops identical to reviewed={match} different={diff} | gate={gate['status']} blocked={len(gate['blocked'])} "
              f"needs_review={len(gate['needs_review'])} reasons={gate['reasons']}")
        print("   production writes: none (temp root", tmp.name, ")")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
