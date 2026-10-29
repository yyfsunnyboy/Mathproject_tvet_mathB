"""Stage the Unit 5 fixed textbook entry (進階題12, FIXED_GRADED multi_part) and prove the merge on a TEMP copy of the live config.

The live ``configs/fixed_textbook_practice.json`` is NOT modified here: the entry is written to ``staged_fixed_entries.json`` and is merged into the
live file only by the authorised release step (``merge_into_live``).  Before that step the entry must be re-bound to the row id of the formal
import (``build_entries(db)`` against the released database): the id below is the isolated rehearsal row, bound by anchor + stem SHA-256.

The parts carry no ``expected_answer``: the answer contract is sent to the browser before submitting, so the reference answer lives only in the
server-side ``answer`` dict (keyed by part, same shape as the promoted multi_part payloads) and the shared multi_part checker reads it from there.

    python reports/gh_math2_unit5_fixed/build_fixed_config.py            # stage + prove on a temp copy
"""
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from core.fixed_textbook_practice import CONFIG_PATH, stem_sha256  # noqa: E402

oracles = json.loads((HERE / "fixed_oracles.json").read_text(encoding="utf-8"))
region = json.loads((HERE / "staged_visual_region.json").read_text(encoding="utf-8"))
STAGED = HERE / "staged_fixed_entries.json"
DB = HERE / "sandbox" / "unit5.db"
ANCHOR = oracles["anchor_id"]
SKILL = "gh_Combination"

CHOICES = [{"label": c["label"], "value": c["text"]} for c in oracles["part_1"]["choices"]]
SPEC = {
    "skill_id": SKILL,
    "label": "習題進階題12（半圓上的點・自動判分）",
    "mode": "graded",
    "answer": {"part_1": oracles["part_1"]["choice"], "part_2": str(oracles["part_2"]["triangles"])},
    "answer_contract": {
        "presentation_mode": "multiple_inputs", "answer_type": "multi_part", "checker": "multi_part_answer_checker",
        "checker_key": "multi_part_answer_checker", "answer_equivalence": "multi_part_answer", "equivalence": "multi_part_answer",
        "equivalence_type": "multi_part_answer", "answer_shape": "fixed_textbook_multi_part",
        "parts": [
            {"key": "part_1", "label": "(1)", "prompt": "(1) 選項", "checker": "choice_label_checker", "checker_key": "choice_label_checker",
             "equivalence_type": "choice_label", "answer_type": "single_choice", "choices": CHOICES},
            {"key": "part_2", "label": "(2)", "prompt": "(2) 三角形個數", "checker": "integer_checker", "checker_key": "integer_checker",
             "equivalence_type": "numeric_exact", "answer_type": "integer"},
        ],
    },
    "reference_solution": [
        "圖中共有 $10$ 個點：直徑上的 $A_1,A_2,A_3,A_4$ 共線，半圓弧上的 $B_1,\\dots ,B_6$ 中任三點不共線，且弧上的點都不在直徑所在直線上。",
        "(1) 任取兩點決定一條直線，共 $C^{10}_{2}=45$ 種取法；但 $A_1,A_2,A_3,A_4$ 中任取兩點都決定同一條直線，"
        "這 $C^{4}_{2}=6$ 種取法只算 $1$ 條。所以直線共有 $45-6+1=40$ 條，答案為③。",
        "(2) 任取三點，共 $C^{10}_{3}=120$ 種取法；三點共線時不能構成三角形，只有從 $A_1,A_2,A_3,A_4$ 中取三點的 $C^{4}_{3}=4$ 種。"
        "所以三角形共有 $120-4=116$ 個。",
    ],
}


def build_entries(db: Path = DB) -> dict:
    """Bind the entry to the row that carries the reviewed anchor in ``db`` (the rehearsal DB now, the released DB at release time)."""
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    try:
        hits = [(rid, skill, text) for rid, skill, text, notes in
                con.execute("select id, skill_id, problem_text, notes from textbook_examples where source_curriculum='general' and source_chapter='單元5 組合'")
                if (json.loads(notes or "{}").get("question_anchor") or {}).get("anchor_id") == ANCHOR]
    finally:
        con.close()
    assert len(hits) == 1, f"anchor {ANCHOR} must map to exactly one row, got {len(hits)}"
    rid, skill, text = hits[0]
    assert skill == SKILL, (rid, skill)
    flat = "".join(ch for ch in text if ch not in "_{} ")
    for label in ("A1", "A2", "A3", "A4", "B1", "B2", "B6", "半圓", "(1)", "(2)", "①", "②", "③", "④", "⑤"):
        assert label in flat, f"stem lacks {label}"
    src = region["source"]
    return {str(rid): {**SPEC, "problem_text_sha256": stem_sha256(text), "question_anchor": ANCHOR,
                       "provenance": {"curriculum": src["curriculum"], "volume": src["volume"], "chapter": src["chapter"],
                                      "pdf_sha256": src["pdf_sha256"], "pdf_page": oracles["page"],
                                      "figure_bbox": src["regions"]["5習題 進階題12"][0]["bbox"],
                                      "figure_region_status": region["status"]},
                       "oracle": {"method": oracles["method"], "page": oracles["page"], "pdf_sha256": oracles["pdf_sha256"],
                                  "figure_vector_bounds": oracles["figure_vector_bounds"], "points_pt": oracles["points_pt"],
                                  "collinear_triples": oracles["collinear_triples"], "lines": oracles["part_1"]["lines"],
                                  "triangles": oracles["part_2"]["triangles"], "script": oracles["script"]}}}


def merge_into(path: Path, entries: dict) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("entries", {}).update(entries)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data


def merge_into_live(released_db: Path) -> dict:
    """Authorised release step only: re-bind to the released row, then merge."""
    return merge_into(CONFIG_PATH, build_entries(released_db))


if __name__ == "__main__":
    assert oracles["part_1"]["lines"] == 40 and oracles["part_1"]["choice"] == "③" and oracles["part_2"]["triangles"] == 116
    entries = build_entries()
    STAGED.write_text(json.dumps({"schema": "fixed_textbook_practice.v1.staged", "bound_to": "isolated rehearsal row (re-bind at release)",
                                  "entries": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    live_bytes = CONFIG_PATH.read_bytes()
    before = json.loads(live_bytes.decode("utf-8"))["entries"]
    assert not set(entries) & set(before), "rehearsal row id collides with a live entry"
    tmp = Path(tempfile.mkdtemp()) / "fixed_textbook_practice.json"
    shutil.copyfile(CONFIG_PATH, tmp)
    merged = merge_into(tmp, entries)["entries"]
    again = merge_into(tmp, entries)["entries"]
    assert merged == again, "merge must be idempotent"
    for k, v in before.items():
        assert merged[k] == v, f"existing entry {k} changed"
    assert set(merged) == set(before) | set(entries)
    assert CONFIG_PATH.read_bytes() == live_bytes, "live config must not change"
    print("staged", sorted(entries), "| live entries untouched:", len(before), "| merged on temp copy:", len(merged))
