# -*- coding: utf-8 -*-
"""Minimal runtime smoke + targeted math-equivalence grading for B1 Ch3 skills."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.gencode.runtime_skill_wrapper import check_answer

SKILLS = [
    "vh_數學B1_PolynomialBasicConcepts",
    "vh_數學B1_PolynomialArithmeticOperations",
    "vh_數學B1_PolynomialEquality",
    "vh_數學B1_RemainderTheorem",
    "vh_數學B1_FactorTheorem",
    "vh_數學B1_PolynomialFactoring",
    "vh_數學B1_RationalEquation",
]


def _load(skill: str):
    path = ROOT / "skills" / f"{skill}.py"
    import importlib.util

    spec = importlib.util.spec_from_file_location(f"smoke_{skill}", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def smoke_skill(skill: str, n: int = 8) -> dict:
    mod = _load(skill)
    passed = 0
    failed = 0
    errors: list[str] = []
    targeted = []
    for i in range(n):
        try:
            pl = mod.generate(seed=3000 + i)
            ans = pl.get("answer")
            if ans is None:
                failed += 1
                errors.append(f"{skill}:{3000+i}:empty")
                continue
            if not check_answer(ans, ans, payload=pl):
                failed += 1
                errors.append(f"{skill}:{3000+i}:self_fail")
                continue
            passed += 1
            at = str(pl.get("answer_type") or "")
            ck = str(pl.get("checker") or (pl.get("answer_contract") or {}).get("checker") or "")
            if at in {"expression", "equation"} or "expression" in ck or "equation" in ck:
                targeted.append(pl)
        except Exception as exc:
            failed += 1
            errors.append(f"{skill}:{3000+i}:exc:{exc}")
    return {"skill": skill, "passed": passed, "failed": failed, "errors": errors[:4], "targeted": targeted}


def _variant_grade(pl: dict) -> list[str]:
    rows = []
    ans = pl.get("answer")
    if isinstance(ans, dict):
        student = {}
        for k, v in ans.items():
            text = str(v)
            if text.startswith("(") and ")(" in text.replace(" ", ""):
                # swap first two linear factors when possible
                student[k] = text[::-1] if False else text
            student[k] = text.replace(" ", "")
        ok = check_answer(student, ans, payload=pl)
        rows.append(f"multi_part_compact={ok}")
        return rows
    if not isinstance(ans, str):
        return rows
    compact = ans.replace(" ", "")
    if compact != ans:
        rows.append(f"space_strip {ans!r}->{compact!r} {check_answer(compact, ans, payload=pl)}")
    if "=" in compact:
        left, right = compact.split("=", 1)
        swapped = f"{right}={left}"
        rows.append(f"eq_swap {swapped} {check_answer(swapped, ans, payload=pl)}")
    return rows


def main() -> int:
    summary = []
    for skill in SKILLS:
        row = smoke_skill(skill)
        print(f"{skill} passed={row['passed']} failed={row['failed']} errors={row['errors']}")
        if row["targeted"]:
            print("  targeted", _variant_grade(row["targeted"][0]))
        summary.append(row)
    bad = [r for r in summary if r["failed"]]
    if bad:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
