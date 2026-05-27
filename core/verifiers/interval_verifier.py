from __future__ import annotations

from core.checkers.interval_checker import check_interval_answer


def verify_interval_checker_cases() -> dict:
    cases = [
        ("-8 <= x <= 8", "[-8,8]", True),
        ("-7 < x < 7", "(-7,7)", True),
        ("x < -10 或 x > 10", "(-∞,-10) ∪ (10,∞)", True),
        ("x <= -12 或 x >= 12", "(-∞,-12] ∪ [12,∞)", True),
        ("-8 < x < 8", "[-8,8]", False),
        ("x < -10 或 x > 9", "x < -10 或 x > 10", False),
    ]
    failed = []
    passed = 0
    for u, c, expect in cases:
        got = check_interval_answer(u, c)
        if got == expect:
            passed += 1
        else:
            failed.append({"user_answer": u, "correct_answer": c, "expect": expect, "got": got})
    return {"success": len(failed) == 0, "cases_total": len(cases), "cases_passed": passed, "failed_cases": failed}


def verify() -> dict:
    return verify_interval_checker_cases()

