from __future__ import annotations

import re
from fractions import Fraction


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

    from core.checkers.math_input_normalization import latex_to_plain

    normalized = latex_to_plain(raw)
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


EXACT_RATIONAL_MEMBERS = "exact_rational"
_EMPTY_SET_TOKENS = frozenset({"無解", "空集合", "∅", "{}", "沒有解", "emptyset"})


def parse_exact_solution_set(text: object) -> frozenset[Fraction] | None:
    """Parse `x=1/3 或 x=-1`, `-1, \\frac{1}{3}`, `無解` into exact rational members; None if unreadable."""
    from core.checkers.math_input_normalization import latex_to_plain, parse_exact_number

    items = list(text) if isinstance(text, (list, tuple, set, frozenset)) else None
    if items is None:
        raw = latex_to_plain(str(text or ""))
        raw = raw.replace("＝", "=").replace("，", ",").replace("；", ",").replace(";", ",").replace("、", ",")
        raw = re.sub(r"\s+", "", raw)
        if not raw:
            return None
        if raw in _EMPTY_SET_TOKENS:
            return frozenset()
        raw = re.sub(r"\bor\b", ",", raw, flags=re.IGNORECASE).replace("或是", ",").replace("或", ",")
        raw = re.sub(r"^\{(.*)\}$", r"\1", raw)
        items = [re.sub(r"^[A-Za-z]=", "", token) for token in raw.split(",")]
    members: set[Fraction] = set()
    for item in items:
        if isinstance(item, bool):
            return None
        value = parse_exact_number(item if isinstance(item, (int, Fraction)) else str(item).strip())
        if value is None:
            return None
        members.add(value)
    return frozenset(members) if members else None


def check_solution_set_answer(
    user_answer: object, correct_answer: object, *, answer_contract: dict | None = None
) -> bool:
    if isinstance(answer_contract, dict) and answer_contract.get("solution_members") == EXACT_RATIONAL_MEMBERS:
        user_exact = parse_exact_solution_set(user_answer)
        correct_exact = parse_exact_solution_set(correct_answer)
        return user_exact is not None and correct_exact is not None and user_exact == correct_exact
    user_set = parse_solution_set_answer(user_answer)
    correct_set = parse_solution_set_answer(correct_answer)
    if not user_set or not correct_set:
        return False
    return user_set == correct_set

