from __future__ import annotations

import re


def _parse_numeric_token(token: str) -> int | None:
    token = str(token).strip()
    if not token:
        return None
    try:
        num = float(token)
        return int(num) if num.is_integer() else int(num)
    except Exception:
        return None


def parse_solution_set_answer(text: object) -> set[int]:
    if isinstance(text, set):
        text = list(text)
    if isinstance(text, (list, tuple)):
        results: set[int] = set()
        for item in text:
            if isinstance(item, bool):
                continue
            if isinstance(item, int):
                results.add(item)
                continue
            if isinstance(item, float) and item.is_integer():
                results.add(int(item))
                continue
            parsed = _parse_numeric_token(str(item))
            if parsed is not None:
                results.add(parsed)
        if results:
            return results

    raw = str(text or "")
    if not raw.strip():
        return set()

    normalized = raw
    normalized = normalized.replace("，", ",").replace("；", ";").replace("、", ",")
    normalized = re.sub(r"\bor\b", ",", normalized, flags=re.IGNORECASE)
    normalized = normalized.replace("或是", ",").replace("或", ",")
    normalized = normalized.replace("＝", "=")
    normalized = re.sub(r"\s+", "", normalized)
    normalized = re.sub(r"[kK]\s*=", "", normalized)
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

