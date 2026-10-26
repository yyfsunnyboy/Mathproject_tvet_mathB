"""Isolated figure mount for 數學2 單元2: DB copy (formal DB opened read-only) + temp project root; writes nothing to production.

Prints what the fixed PDF-visual enrichment mounts with the human-verified region sidecar and the Stage 1 gate afterwards,
and saves the resulting notes / crops under sandbox/ for the change-set builder.
"""
import json
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
from core.textbook_pdf_visual import enrich_textbook_examples_with_pdf_visuals  # noqa: E402
from core.textbook_stage1_gate import evaluate_stage1_gate  # noqa: E402

PROD = ROOT / "instance" / "kumon_math.db"
SAND = HERE / "sandbox" / "kumon_math_copy.db"
PDF = ROOT / "textbook_import/uploaded_sources/general/數學2/9d32c092de77_單元02-級數.pdf"
IDS = (12707, 12743)
VISUAL_KEYS = ("image_assets", "pdf_visual_enrichment", "pdf_visual_status", "visual_required_missing", "image_warning", "has_image",
               "needs_review", "visual_status", "needs_image_review", "manual_visual_review", "manual_stem_review",
               "needs_review_before_visual", "image_warning_resolved_by", "review_required_by_confidence", "needs_image",
               "image_role", "image_dependency_reason")


def make_copy() -> None:
    SAND.parent.mkdir(exist_ok=True)
    if SAND.exists():
        SAND.unlink()
    src = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(SAND)
    src.backup(dst)
    dst.close()
    src.close()


def rows(strip: bool):
    con = sqlite3.connect(f"file:{SAND.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    out = []
    for r in con.execute("select * from textbook_examples where id between ? and ? order by id", IDS):
        d = dict(r)
        notes = json.loads(d["notes"] or "{}")
        if strip:
            for k in VISUAL_KEYS:
                notes.pop(k, None)
        d["notes"] = json.dumps(notes, ensure_ascii=False)
        out.append(SimpleNamespace(**d))
    return out


def gate_of(items):
    return evaluate_stage1_gate([{"id": r.id, "problem_text": r.problem_text, "detailed_solution": r.detailed_solution,
                                  "problem_type": r.problem_type, "source_description": r.source_description, "notes": r.notes} for r in items])


if __name__ == "__main__":
    make_copy()
    sidecar = json.loads((HERE / "unit2_visual_regions.json").read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp(prefix="unit2_visuals_"))
    try:
        items = rows(strip=True)
        summary = enrich_textbook_examples_with_pdf_visuals(
            pdf_path=PDF, examples=items,
            curriculum_info={"curriculum": "general", "volume": "數學2", "chapter": "單元2 級數", "section": "2.級數", "publisher": "longteng"},
            project_root=tmp, debug_dir=None, write_notes=True, publish_assets=False, assemble_visual_groups=True, region_overrides=sidecar)
        gate = gate_of(items)
        mounted = {r.id: [a["path"] for a in json.loads(r.notes).get("image_assets") or []] for r in items if json.loads(r.notes).get("image_assets")}
        print(json.dumps({"mounted": summary.get("mounted"), "overrides": summary.get("manual_region_overrides_applied"),
                          "rows_with_assets": {k: len(v) for k, v in mounted.items()},
                          "gate": {k: gate[k] for k in ("status", "stage1_ready", "reasons")}, "blocked": gate["blocked"], "review": gate["needs_review"]},
                         ensure_ascii=False, indent=1, default=str))
        files = sorted(p for p in tmp.rglob("*.png"))
        print("temp crops:", [str(p.relative_to(tmp))[-90:] for p in files])
        (HERE / "sandbox" / "isolated_notes.json").write_text(json.dumps({r.id: r.notes for r in items}, ensure_ascii=False), encoding="utf-8")
        dest = HERE / "sandbox" / "crops"
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(tmp, dest)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
