from __future__ import annotations

from core.checkers.choice_label_checker import check_choice_label


def verify_choice_label_cases() -> dict:
    choices = ["數線上 -2 到 0 的距離", "數線上 2 到 -2 的距離", "-2 本身", "一個負數"]
    cases = [
        ("A", "A", True),
        ("a", "A", True),
        ("(A)", "A", True),
        ("A.", "A", True),
        ("1", "A", True),
        ("B", "2", True),
        ("數線上 -2 到 0 的距離", "A", True),
        ("B", "A", False),
    ]
    failed = []
    passed = 0
    for u, c, expect in cases:
        got = check_choice_label(u, c, choices)
        if got == expect:
            passed += 1
        else:
            failed.append({"user_answer": u, "correct_answer": c, "expect": expect, "got": got})
    return {"success": len(failed) == 0, "cases_total": len(cases), "cases_passed": passed, "failed_cases": failed}


def verify() -> dict:
    return verify_choice_label_cases()

