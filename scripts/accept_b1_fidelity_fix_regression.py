# -*- coding: utf-8 -*-
"""Offline regression for B1 fidelity fixes (no formal DB writes)."""
from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "gencode_closed_loop"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _ok(result) -> bool:
    if isinstance(result, dict):
        return bool(result.get("correct") or result.get("is_correct") or result.get("overall_correct"))
    return bool(result)


def _reload(skill: str):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    for name in list(sys.modules):
        if skill in name or name == "core.gencode.slot_generators":
            del sys.modules[name]
    return importlib.import_module(f"skills.{skill}")


def check_component(skill: str, component_id: str, seed: int, expect_substr=None, expect_answer_type=None):
    mod = _reload(skill)
    payload = mod.generate(level=1, seed=seed, component_id=component_id)
    q = str(payload.get("question") or payload.get("question_text") or "")
    ans = payload.get("semantic_answer")
    if ans is None:
        ans = payload.get("correct_answer")
    if ans is None:
        ans = payload.get("answer")
    ac = payload.get("answer_contract") or {}
    row = {
        "skill_id": skill,
        "component_id": component_id,
        "problem_type_id": payload.get("problem_type_id"),
        "answer_type": payload.get("answer_type") or ac.get("answer_type"),
        "checker": ac.get("checker") or ac.get("checker_key") or payload.get("checker"),
        "question_preview": q[:140],
        "self_check": False,
        "wrong_rejected": False,
        "notes": [],
    }
    if expect_substr and expect_substr not in q:
        row["notes"].append(f"missing_substr:{expect_substr}")
    if expect_answer_type and str(row["answer_type"]) != expect_answer_type:
        row["notes"].append(f"answer_type_got:{row['answer_type']}")
    if row["answer_type"] in {"integer", "text_short"} and "（答案範例：任意實數" in q:
        row["notes"].append("leaked_interval_format_example")
    row["self_check"] = _ok(mod.check(ans, ans, payload))
    wrong = "__bad__"
    if isinstance(ans, dict):
        wrong = {k: "__bad__" for k in ans}
    elif isinstance(ans, (int, float)) or (isinstance(ans, str) and str(ans).lstrip("-").isdigit()):
        try:
            wrong = str(int(str(ans)) + 99)
        except Exception:
            wrong = "__bad__"
    row["wrong_rejected"] = not _ok(mod.check(wrong, ans, payload))
    row["status"] = (
        "PASS"
        if row["self_check"] and row["wrong_rejected"] and not row["notes"]
        else ("WARN" if row["self_check"] and row["wrong_rejected"] else "FAIL")
    )
    return row


def main() -> int:
    rows = []
    rows.append(check_component("vh_數學B1_QuadraticFunctionExtremum", "src_4457", 12))
    rows.append(check_component("vh_數學B1_QuadraticFunctionExtremum", "src_4465", 11))
    rows.append(check_component("vh_數學B1_QuadraticFunctionExtremum", "src_4471", 10))
    rows.append(
        check_component(
            "vh_數學B1_QuadraticInequalitySolution",
            "src_4476",
            17,
            expect_substr="最少要製作",
            expect_answer_type="integer",
        )
    )
    rows.append(
        check_component(
            "vh_數學B1_QuadraticInequalitySolution",
            "src_4484",
            19,
            expect_substr="連續正整數",
            expect_answer_type="text_short",
        )
    )
    rows.append(
        check_component(
            "vh_數學B1_QuadraticInequalitySolution",
            "src_4488",
            21,
            expect_substr="最少要製作",
            expect_answer_type="integer",
        )
    )
    rows.append(check_component("vh_數學B1_QuadraticInequalitySolution", "src_4517", 23))
    rows.append(
        check_component(
            "vh_數學B1_PolynomialBasicConcepts",
            "src_4618",
            5,
            expect_substr="降冪排列",
        )
    )
    rows.append(
        check_component(
            "vh_數學B1_PolynomialBasicConcepts",
            "src_4629",
            7,
            expect_substr="降冪排列",
        )
    )
    # prior regressions
    rows.append(check_component("vh_數學B1_QuadraticInequalitySolution", "src_4474", 17, expect_answer_type="integer"))
    rows.append(check_component("vh_數學B1_DistanceBetweenPointAndLine", "src_4584", 19))
    rows.append(check_component("vh_數學B1_DistanceBetweenTwoParallelLines", "src_4570", 21))
    rows.append(check_component("vh_數學B1_SlopeOfALine", "src_4519", 23))

    summary = {
        "PASS": sum(1 for r in rows if r["status"] == "PASS"),
        "WARN": sum(1 for r in rows if r["status"] == "WARN"),
        "FAIL": sum(1 for r in rows if r["status"] == "FAIL"),
    }
    payload = {"generated_at": STAMP, "summary": summary, "rows": rows}
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"b1_fidelity_fix_regression_{STAMP}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "b1_fidelity_fix_regression_latest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"wrote": str(path), "summary": summary}, ensure_ascii=False))
    for r in rows:
        print(r["status"], r["component_id"], r.get("answer_type"), r.get("notes"), r["question_preview"][:60])
    return 0 if summary["FAIL"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
