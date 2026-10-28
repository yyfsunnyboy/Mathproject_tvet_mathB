"""Stage the Unit 4 fixed textbook entry (12801, FIXED_GRADED) and prove the merge on a TEMP copy of the live config.

The live ``configs/fixed_textbook_practice.json`` is NOT modified here: the entry is written to ``staged_fixed_entries.json`` and is merged into the live
file only by the authorised release step (``merge_into_live`` below, used by the Unit 4 deploy script).  The merge keeps every existing entry
(Unit 2 / Unit 3 rows) untouched and is idempotent.

    python reports/gh_math2_unit4_fixed/build_fixed_config.py            # stage + prove on a temp copy
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
STAGED = HERE / "staged_fixed_entries.json"
DB = ROOT / "tmp" / "gh_math2_unit4_isolated" / "unit4_snapshot.db"

SPEC = {
    12801: {
        "skill_id": "gh_PermutationWithIdenticalItems",
        "label": "習題基礎題6（街道圖・自動判分）",
        "mode": "graded",
        "answer": oracles["12801"]["answer"],
        "answer_contract": {
            "presentation_mode": "short_answer", "answer_type": "rational", "checker": "rational_checker", "checker_key": "rational_checker",
            "answer_equivalence": "rational_equivalent", "equivalence": "rational_equivalent", "equivalence_type": "rational_equivalent",
            "answer_shape": "fixed_textbook_rational",
        },
        "reference_solution": [
            "走捷徑只能向右或向上；缺少的街道不能走。把每個路口標上「從 A 走捷徑到該路口的方法數」：某路口的方法數＝（左邊路口，若有街道相連）的方法數＋（下方路口，若有街道相連）的方法數。",
            "由下往上，每一排由左至右的方法數依序為：最下排 $1,1,1,1,1,1$；第 2 排 $1,2,3,4,0,1$；第 3 排 $1,3,6,10,10,11$；第 4 排 $1,0,0,10,20,31$；最上排 $1,1,1,11,31,62$。",
            "所以從 A 取捷徑走到 B 共有 $62$ 種方法。",
        ],
    },
}


def build_entries() -> dict:
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        entries = {}
        for rid, spec in SPEC.items():
            skill, text = con.execute("select skill_id, problem_text from textbook_examples where id=?", (rid,)).fetchone()
            assert skill == spec["skill_id"], (rid, skill)
            o = oracles[str(rid)]
            entries[str(rid)] = {**spec, "problem_text_sha256": stem_sha256(text),
                                 "oracle": {"method": o["method"], "page": o["page"], "bbox": o["bbox"], "pdf_sha256": o["pdf_sha256"],
                                            "street_graph": {"width": o["width"], "height": o["height"], "horizontal_edges": o["horizontal_edges"],
                                                             "vertical_edges": o["vertical_edges"]},
                                            "script": "reports/gh_math2_unit4_fixed/derive_fixed_oracles.py"}}
        return entries
    finally:
        con.close()


def merge_into(path: Path, entries: dict) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("entries", {}).update(entries)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data


def merge_into_live() -> dict:
    """Authorised release step only."""
    return merge_into(CONFIG_PATH, json.loads(STAGED.read_text(encoding="utf-8"))["entries"])


if __name__ == "__main__":
    entries = build_entries()
    STAGED.write_text(json.dumps({"schema": "fixed_textbook_practice.v1.staged", "entries": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    before = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))["entries"]
    tmp = Path(tempfile.mkdtemp()) / "fixed_textbook_practice.json"
    shutil.copyfile(CONFIG_PATH, tmp)
    merged = merge_into(tmp, entries)["entries"]
    again = merge_into(tmp, entries)["entries"]
    assert merged == again, "merge must be idempotent"
    for k, v in before.items():
        assert merged[k] == v, f"existing entry {k} changed"
    assert set(merged) == set(before) | set(entries)
    print("staged", sorted(entries), "| live entries untouched:", sorted(before), "| merged on temp copy:", sorted(merged))
