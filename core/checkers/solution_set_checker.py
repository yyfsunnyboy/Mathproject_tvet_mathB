from __future__ import annotations

import re


def parse_solution_set_answer(text: object) -> set[int]:
    raw = str(text or "")
    if not raw.strip():
        return set()

    normalized = raw
    normalized = normalized.replace("，", ",").replace("；", ";").replace("、", ",")
    normalized = normalized.replace("或是", ",").replace("或", ",")
    normalized = normalized.replace("＝", "=")
    normalized = re.sub(r"\s+", "", normalized)
    normalized = re.sub(r"[xX]\s*=", "", normalized)
    normalized = normalized.replace("{", "").replace("}", "")

    results: set[int] = set()
    for pm in re.finditer(r"(?:±|\+\-)\s*([+-]?\d+)", normalized):
        n = abs(int(pm.group(1)))
        results.add(n)
        results.add(-n)
    normalized = re.sub(r"(?:±|\+\-)\s*[+-]?\d+", "", normalized)

    for num in re.findall(r"[+-]?\d+", normalized):
        results.add(int(num))
    return results


def check_solution_set_answer(user_answer: object, correct_answer: object) -> bool:
    user_set = parse_solution_set_answer(user_answer)
    correct_set = parse_solution_set_answer(correct_answer)
    if not user_set or not correct_set:
        return False
    return user_set == correct_set

