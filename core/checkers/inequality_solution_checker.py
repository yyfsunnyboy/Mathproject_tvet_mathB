from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

from sympy import EmptySet, Interval, Intersection, Rational, S, Union, oo
from sympy.sets.sets import Set

_REL_OPS = ("<=", ">=", "<", ">")
_VAR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_NUM_RE = re.compile(
    r"^[+-]?(?:(?:\d+\.\d+|\d+/\d+|\d+)(?:e[+-]?\d+)?|inf|infinity|oo|infty)$",
    re.I,
)


def _normalize_solution_text(text: object) -> str:
    s = str(text or "").strip()
    if not s:
        return ""
    s = s.replace("\u2212", "-").replace("–", "-").replace("—", "-")
    s = s.replace("（", "(").replace("）", ")").replace("【", "[").replace("】", "]")
    s = s.replace("，", ",").replace("。", "")
    s = s.replace("＜", "<").replace("＞", ">")
    s = s.replace("≤", "<=").replace("≦", "<=").replace("≥", ">=").replace("≧", ">=")
    s = s.replace("=>", ">=").replace("=<", "<=")
    s = s.replace("$", "")
    s = re.sub(r"\\left", "", s)
    s = re.sub(r"\\right", "", s)
    s = re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1)/(\2)", s)
    s = s.replace(r"\leq", "<=").replace(r"\le", "<=")
    s = s.replace(r"\geq", ">=").replace(r"\ge", ">=")
    s = s.replace(r"\lt", "<").replace(r"\gt", ">")
    s = s.replace(r"\in", "∈").replace(r"\cup", "∪").replace(r"\cap", "∩")
    s = s.replace(r"\infty", "∞").replace(r"\emptyset", "∅")
    s = s.replace(r"\varnothing", "∅")
    s = s.replace(r"\mathbb{R}", "ℝ").replace(r"\mathbf{R}", "ℝ")
    s = s.replace(r"\ ", "").replace("~", "")
    s = s.replace("∞", "inf")
    s = re.sub(r"belongs\s+to", "∈", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(
        r"^[A-Za-z_][A-Za-z0-9_]*\s*(?:∈|in)\s*",
        "",
        s,
        flags=re.I,
    )
    return s


def _is_reals_phrase(s: str) -> bool:
    t = re.sub(r"\s+", "", s.lower())
    t = t.replace("ℝ", "r")
    return t in {
        "r",
        "reals",
        "allreals",
        "allrealnumbers",
        "realnumbers",
        "(-inf,inf)",
        "(-inf,+inf)",
        "任意實數",
        "所有實數",
        "全體實數",
        "實數",
    }


def _is_empty_phrase(s: str) -> bool:
    t = re.sub(r"\s+", "", s.lower())
    t = t.replace("∅", "empty")
    return t in {
        "empty",
        "emptyset",
        "empty_set",
        "nullset",
        "{}",
        "無解",
        "空集合",
        "空集",
        "沒有解",
    }


def _parse_num(token: str) -> Any:
    t = token.strip().replace(" ", "")
    t = t.replace("(+", "(")
    while len(t) >= 2 and t[0] == "(" and t[-1] == ")" and t.count("(") == t.count(")"):
        inner = t[1:-1]
        if inner.count("(") == inner.count(")"):
            t = inner
        else:
            break
    low = t.lower()
    if low in {"inf", "+inf", "infinity", "+infinity", "oo", "+oo", "infty", "+infty"}:
        return oo
    if low in {"-inf", "-infinity", "-oo", "-infty"}:
        return -oo
    if not t:
        raise ValueError("empty numeric token")
    frac = Fraction(t)
    if frac.denominator == 1:
        return Rational(frac.numerator, 1)
    return Rational(frac.numerator, frac.denominator)


def _is_var(token: str) -> bool:
    return bool(_VAR_RE.match(token.strip()))


def _is_num_token(token: str) -> bool:
    t = token.strip().replace(" ", "")
    if t.startswith("(") and t.endswith(")") and "/" in t:
        t = t[1:-1]
    return bool(_NUM_RE.match(t)) or t.lower() in {"+inf", "-inf", "+oo", "-oo"}


def _split_top_level(text: str, separators: tuple[str, ...]) -> list[str] | None:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in "([{":
            depth += 1
            buf.append(ch)
            i += 1
            continue
        if ch in ")]}":
            depth = max(0, depth - 1)
            buf.append(ch)
            i += 1
            continue
        if depth == 0:
            matched = None
            for sep in separators:
                if sep.startswith("\\b"):
                    continue
                if text.startswith(sep, i):
                    matched = sep
                    break
            if matched is None:
                for sep in separators:
                    if not sep.startswith("(?") and not sep.startswith("\\b"):
                        continue
            if matched:
                part = "".join(buf).strip()
                if part:
                    parts.append(part)
                buf = []
                i += len(matched)
                continue
            or_word = re.match(r"(?i)\bor\b", text[i:])
            and_word = re.match(r"(?i)\band\b", text[i:])
            if "\bor\b" in separators and or_word:
                part = "".join(buf).strip()
                if part:
                    parts.append(part)
                buf = []
                i += or_word.end()
                continue
            if "\band\b" in separators and and_word:
                part = "".join(buf).strip()
                if part:
                    parts.append(part)
                buf = []
                i += and_word.end()
                continue
        buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    if len(parts) <= 1:
        return None
    return parts


def _split_or(text: str) -> list[str]:
    s = text.replace("∪", "∪").replace(" U ", "∪").replace(" u ", "∪")
    s = s.replace("或是", "或").replace("或", "∪")
    parts = _split_top_level(s, ("∪", "\bor\b"))
    if parts:
        return parts
    return [text.strip()] if text.strip() else []


def _split_and(text: str) -> list[str]:
    s = text.replace("∩", "∩").replace("且", "∩")
    parts = _split_top_level(s, ("∩", "\band\b"))
    if parts:
        return parts
    return [text.strip()] if text.strip() else []


def _rel_set(op: str, bound: Any, *, var_on_left: bool) -> Set:
    if var_on_left:
        if op == "<":
            return Interval(-oo, bound, True, True)
        if op == "<=":
            return Interval(-oo, bound, True, False)
        if op == ">":
            return Interval(bound, oo, True, True)
        if op == ">=":
            return Interval(bound, oo, False, True)
    else:
        if op == "<":
            return Interval(bound, oo, True, True)
        if op == "<=":
            return Interval(bound, oo, False, True)
        if op == ">":
            return Interval(-oo, bound, True, True)
        if op == ">=":
            return Interval(-oo, bound, True, False)
    raise ValueError(f"unsupported rel {op}")


def _find_rel_ops(expr: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    i = 0
    while i < len(expr):
        hit = None
        for op in _REL_OPS:
            if expr.startswith(op, i):
                hit = op
                break
        if hit:
            found.append((i, hit))
            i += len(hit)
        else:
            i += 1
    return found


def _parse_bracket_interval(part: str) -> Set | None:
    m = re.match(
        r"^([\[\(])\s*([^,]+)\s*,\s*([^\]\)]+)\s*([\]\)])$",
        part.strip(),
    )
    if not m:
        return None
    lbr, lo_s, hi_s, rbr = m.groups()
    try:
        lo = _parse_num(lo_s)
        hi = _parse_num(hi_s)
    except Exception:
        return None
    left_open = lbr == "("
    right_open = rbr == ")"
    if lo == oo or hi == -oo:
        return S.EmptySet
    interval = Interval(lo, hi, left_open, right_open)
    return interval


def _parse_relational(part: str) -> Set | None:
    expr = part.replace(" ", "")
    if not expr:
        return None
    ops = _find_rel_ops(expr)
    if not ops:
        return None
    if len(ops) == 1:
        idx, op = ops[0]
        left = expr[:idx]
        right = expr[idx + len(op) :]
        if _is_var(left) and _is_num_token(right):
            return _rel_set(op, _parse_num(right), var_on_left=True)
        if _is_num_token(left) and _is_var(right):
            return _rel_set(op, _parse_num(left), var_on_left=False)
        return None
    if len(ops) == 2:
        i1, op1 = ops[0]
        i2, op2 = ops[1]
        a = expr[:i1]
        b = expr[i1 + len(op1) : i2]
        c = expr[i2 + len(op2) :]
        pieces = [(a, None), (b, op1), (c, op2)]
        tokens = [a, b, c]
        var_idx = [i for i, tok in enumerate(tokens) if _is_var(tok)]
        num_ok = all(_is_num_token(tok) or _is_var(tok) for tok in tokens)
        if not num_ok or len(var_idx) != 1:
            return None
        vi = var_idx[0]
        try:
            if vi == 1:
                left_set = _rel_set(op1, _parse_num(a), var_on_left=False)
                right_set = _rel_set(op2, _parse_num(c), var_on_left=True)
                return Intersection(left_set, right_set)
            if vi == 0:
                return Intersection(
                    _rel_set(op1, _parse_num(b), var_on_left=True),
                    _rel_set(op2, _parse_num(c), var_on_left=True),
                )
            return Intersection(
                _rel_set(op1, _parse_num(a), var_on_left=False),
                _rel_set(op2, _parse_num(b), var_on_left=False),
            )
        except Exception:
            return None
        _ = pieces
    return None


def _parse_atom(part: str) -> Set | None:
    raw = part.strip()
    if not raw:
        return None
    if _is_empty_phrase(raw):
        return S.EmptySet
    if _is_reals_phrase(raw):
        return S.Reals
    got = _parse_bracket_interval(raw)
    if got is not None:
        return got
    got = _parse_relational(raw)
    if got is not None:
        return got
    return None


def _combine_and(parts: list[str]) -> Set | None:
    sets: list[Set] = []
    for part in parts:
        parsed = _parse_atom(part)
        if parsed is None:
            return None
        sets.append(parsed)
    if not sets:
        return None
    acc: Set = sets[0]
    for item in sets[1:]:
        acc = Intersection(acc, item)
    return acc


def parse_real_solution_set(text: object) -> Set | None:
    """Parse a univariate real solution-set answer into a SymPy Set.

    Returns None when the text is not a supported solution-set form.
    """
    if isinstance(text, Set):
        return text
    if isinstance(text, (list, tuple, set, dict, bool)):
        return None
    raw = _normalize_solution_text(text)
    if not raw:
        return None
    compact = re.sub(r"\s+", "", raw)
    if _is_empty_phrase(compact) or _is_empty_phrase(raw):
        return S.EmptySet
    if _is_reals_phrase(compact) or _is_reals_phrase(raw):
        return S.Reals
    or_parts = _split_or(raw)
    acc: Set | None = None
    for part in or_parts:
        and_parts = _split_and(part)
        parsed = _combine_and(and_parts)
        if parsed is None:
            return None
        acc = parsed if acc is None else Union(acc, parsed)
    return acc


def real_solution_sets_equal(left: Set | None, right: Set | None) -> bool:
    if left is None or right is None:
        return False
    try:
        return bool(left.is_subset(right) and right.is_subset(left))
    except Exception:
        return bool(left == right)


def check_inequality_solution_answer(user_answer: object, correct_answer: object) -> bool | None:
    """Return True/False when both sides parse; None when parser cannot apply."""
    user_set = parse_real_solution_set(user_answer)
    correct_set = parse_real_solution_set(correct_answer)
    if user_set is None or correct_set is None:
        return None
    return real_solution_sets_equal(user_set, correct_set)


def check(user_answer: object, correct_answer: object) -> dict:
    verdict = check_inequality_solution_answer(user_answer, correct_answer)
    if verdict is True:
        return {"correct": True, "result": "答對了"}
    return {"correct": False, "result": f"答錯了，正確答案是 {correct_answer}"}
