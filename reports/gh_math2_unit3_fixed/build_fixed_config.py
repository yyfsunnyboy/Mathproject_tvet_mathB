"""Stage the Unit 3 fixed textbook entry (12746, FIXED_UNGRADED) and prove the merge on a TEMP copy of the live config.

The live ``configs/fixed_textbook_practice.json`` is NOT modified here: the entry is written to ``staged_fixed_entries.json`` and is merged into the live
file only by the authorised release step (``merge_into_live`` below, used by the Unit 3 deploy script).  The merge keeps every existing entry
(the Unit 2 rows 12719 / 12727 / 12731 / 12735) untouched and is idempotent.

    python reports/gh_math2_unit3_fixed/build_fixed_config.py            # stage + prove on a temp copy
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

SPEC = {
    12746: {
        "skill_id": "gh_LogicAndSets",
        "label": "隨堂練習2 複合命題的否定（自評）",
        "mode": "ungraded",
        "practice_scaffold": ["(1) 先找出兩個簡單命題，再用笛摩根定律否定「且」", "(2) 先找出兩個簡單命題，再用笛摩根定律否定「或」"],
        "reference_solution": [
            "「且」的否定要把「且」改成「或」，並把兩個簡單命題各自否定：$\\sim(P\\land Q)\\equiv(\\sim P)\\lor(\\sim Q)$；「或」的否定則把「或」改成「且」：$\\sim(P\\lor Q)\\equiv(\\sim P)\\land(\\sim Q)$。",
            "(1) 原命題「2是偶數且 $2$ 是質數」的否定是「$2$ 不是偶數或 $2$ 不是質數」。原命題為真，否定為假。",
            "(2) 原命題「$\\pi=3$ 或 $\\pi$ 是正數」的否定是「$\\pi\\neq 3$ 且 $\\pi$ 不是正數」，也就是「$\\pi\\neq 3$ 且 $\\pi\\le 0$」。原命題為真，否定為假。",
        ],
    },
}


def build_entries() -> dict:
    con = sqlite3.connect(f"file:{(ROOT / 'instance' / 'kumon_math.db').as_posix()}?mode=ro", uri=True)
    try:
        entries = {}
        for rid, spec in SPEC.items():
            skill, text = con.execute("select skill_id, problem_text from textbook_examples where id=?", (rid,)).fetchone()
            assert skill == spec["skill_id"], (rid, skill)
            entries[str(rid)] = {**spec, "problem_text_sha256": stem_sha256(text),
                                 "oracle": {"verified": oracles[str(rid)]["verified"], "script": "reports/gh_math2_unit3_fixed/derive_fixed_oracles.py"}}
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
