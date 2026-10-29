"""Stage the two Unit 5 proof rows (例題9 12838, 隨堂練習10 12845, gh_BinomialTheorem) as ``ungraded`` self-check practice, Unit 2 style.

Writes only ``reports/gh_math2_unit5_fixed/staged_proof_entries.json``; the live ``configs/fixed_textbook_practice.json`` is merged only at the
authorized release.  Each entry is bound to the formal Stage 1 stem by SHA-256 (read-only on a private snapshot of the formal DB) and its
reference proof is checked: the identity symbolically (sympy) and numerically for n = 1..39, and the proof step itself (substituting
x = y = 1, resp. x = 1, y = -1, into the expanded (x+y)^n) for n = 1..12.
"""
from __future__ import annotations

import json
import math
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

import sympy as sp  # noqa: E402

from agent_domains_candidate.combinations.build_sandbox import isolated_db  # noqa: E402
from core.fixed_textbook_practice import stem_sha256  # noqa: E402

SKILL = "gh_BinomialTheorem"
EXPANSION = r"$\left(x+y\right)^{n}=C_{0}^{n}x^{n}+C_{1}^{n}x^{n-1}y+C_{2}^{n}x^{n-2}y^{2}+\cdots +C_{n}^{n}y^{n}$"

ENTRIES = {
    12838: {
        "label": "例題9 二項式係數和的證明（自評）",
        "practice_scaffold": ["寫出 (x+y)^n 的展開式", "以 x=1、y=1 代入", "整理得證"],
        "reference_solution": [
            "【寫出展開式】由二項式定理，" + EXPANSION + "。",
            r"【以 $x=1$、$y=1$ 代入】$\left(1+1\right)^{n}=C_{0}^{n}+C_{1}^{n}+C_{2}^{n}+\cdots +C_{n}^{n}$。",
            r"【整理得證】左式 $=2^{n}$，所以 $C_{0}^{n}+C_{1}^{n}+C_{2}^{n}+\cdots +C_{n}^{n}=2^{n}$，故得證。",
        ],
        "sign": 1,
    },
    12845: {
        "label": "隨堂練習10 二項式係數交錯和的證明（自評）",
        "practice_scaffold": ["寫出 (x+y)^n 的展開式", "以 x=1、y=−1 代入", "整理得證"],
        "reference_solution": [
            "【寫出展開式】由二項式定理，" + EXPANSION + "。",
            r"【以 $x=1$、$y=-1$ 代入】$\left(1-1\right)^{n}=C_{0}^{n}-C_{1}^{n}+C_{2}^{n}-C_{3}^{n}+\cdots +\left(-1\right)^{n}C_{n}^{n}$。",
            r"【整理得證】因為 $n$ 為正整數，左式 $=0^{n}=0$，所以 $C_{0}^{n}-C_{1}^{n}+C_{2}^{n}-\cdots +\left(-1\right)^{n}C_{n}^{n}=0$，故得證。",
        ],
        "sign": -1,
    },
}


def verify(sign: int) -> str:
    n, k = sp.symbols("n k", integer=True, positive=True)
    total = sp.simplify(sp.summation(sign ** k * sp.binomial(n, k), (k, 0, n)))
    target = 2 ** n if sign == 1 else 0
    symbolic = sp.simplify(sp.piecewise_fold(total) - target) == 0 if not isinstance(total, sp.Piecewise) else None
    for m in range(1, 40):
        assert sum(sign ** j * math.comb(m, j) for j in range(m + 1)) == (2 ** m if sign == 1 else 0), m
    x, y = sp.symbols("x y")
    for m in range(1, 13):
        expanded = sp.expand((x + y) ** m)
        assert expanded.subs({x: 1, y: sign}) == (2 ** m if sign == 1 else 0)
        assert expanded.subs({x: 1, y: sign}) == sum(sign ** j * math.comb(m, j) for j in range(m + 1))
    return f"sympy summation={'2^n' if sign == 1 else '0'} ({'symbolic ok' if symbolic else 'piecewise, checked numerically'}) + n=1..39 numeric + substitution into expanded (x+y)^n, n=1..12"


ANCHORS = {12838: "general_2_section_example_009_018", 12845: "general_2_section_in_class_practice_010_019"}


def build_entries(db: Path) -> dict:
    """Bind each entry to the row carrying its Stage 1 anchor in ``db`` (snapshot when staging, the formal DB at release)."""
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    try:
        rows = {}
        for rid, skill, text, notes in con.execute("select id, skill_id, problem_text, notes from textbook_examples "
                                                   "where source_curriculum='general' and source_chapter='單元5 組合'"):
            anchor = (json.loads(notes or "{}").get("question_anchor") or {}).get("anchor_id")
            if anchor in ANCHORS.values():
                rows.setdefault(anchor, []).append((rid, skill, text))
    finally:
        con.close()
    out = {}
    for rid, spec in ENTRIES.items():
        hits = rows.get(ANCHORS[rid]) or []
        assert len(hits) == 1 and hits[0][0] == rid, (rid, hits)
        _rid, skill, text = hits[0]
        assert skill == SKILL and "證明" in text, rid
        out[str(rid)] = {
            "skill_id": SKILL, "label": spec["label"], "mode": "ungraded",
            "practice_scaffold": spec["practice_scaffold"], "reference_solution": spec["reference_solution"],
            "problem_text_sha256": stem_sha256(text),
            "oracle": {"verified": verify(spec["sign"]), "script": "reports/gh_math2_unit5_fixed/build_proof_entries.py"},
        }
    return out


def main() -> None:
    out = build_entries(isolated_db())
    path = HERE / "staged_proof_entries.json"
    path.write_text(json.dumps({"schema": "fixed_textbook_practice.v1", "staged_for": "release of 普高數學2 Unit 5 GenCode (merge into configs/fixed_textbook_practice.json)",
                                "entries": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: (v["label"], v["oracle"]["verified"]) for k, v in out.items()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
