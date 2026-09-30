from __future__ import annotations

import re
from typing import Any

from sympy import Interval, Intersection, Rational, S, Union, oo
from sympy.sets.sets import Set

from core.checkers.math_input_normalization import latex_to_plain, parse_exact_number

_REL_OPS = ("<=", ">=", "<", ">")
_VAR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


_SET_BUILDER_RE = re.compile(r"^\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:[|:]|∈\s*ℝ\s*[|:])\s*(.+)\}$")


def _normalize_solution_text(text: object) -> str:
    s = latex_to_plain(text)
    if not s:
        return ""
    s = s.replace("。", "")
    s = s.replace("≤", "<=").replace("≥", ">=")
    s = s.replace("=>", ">=").replace("=<", "<=")
    s = s.replace("~", "")
    s = s.replace("∞", "inf")
    s = re.sub(r"belongs\s+to", "∈", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    builder = _SET_BUILDER_RE.match(s)
    if builder:
        s = builder.group(2).strip()
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


_POS_INF_TOKENS = frozenset({"inf", "+inf", "infinity", "+infinity", "oo", "+oo", "infty", "+infty"})
_NEG_INF_TOKENS = frozenset({"-inf", "-infinity", "-oo", "-infty"})
_RADICAL_ENDPOINT_RE = re.compile(r"^[0-9.+\-*/^()]*$")


def _parse_radical_endpoint(t: str) -> Any:
    if "sqrt" not in t or len(t) > 60 or not _RADICAL_ENDPOINT_RE.match(t.replace("sqrt", "")):
        return None
    from sympy import sqrt
    from sympy.parsing.sympy_parser import (
        convert_xor,
        implicit_multiplication_application,
        parse_expr,
        standard_transformations,
    )

    try:
        value = parse_expr(
            t,
            local_dict={"sqrt": sqrt},
            transformations=standard_transformations + (convert_xor, implicit_multiplication_application),
            evaluate=True,
        )
    except Exception:
        return None
    if getattr(value, "free_symbols", None) or not getattr(value, "is_real", False):
        return None
    if not getattr(value, "is_finite", False):
        return None
    return value


def parse_numeric_endpoint(token: object) -> Any:
    """Parse one interval / inequality endpoint to an exact SymPy value, or None.

    Layers: infinity tokens -> exact rational (int / decimal / fraction / LaTeX
    fraction) -> real radical expression.  Never returns a value containing a
    free symbol, so variables are never mistaken for endpoints.
    """
    t = latex_to_plain(token).replace(" ", "").replace("∞", "inf")
    if not t:
        return None
    low = t.lower()
    wrapped = re.fullmatch(r"\(([+-]?(?:infinity|infty|inf|oo))\)", low)
    if wrapped:
        low = wrapped.group(1)
    if low in _POS_INF_TOKENS:
        return oo
    if low in _NEG_INF_TOKENS:
        return -oo
    frac = parse_exact_number(t)
    if frac is not None:
        return Rational(frac.numerator, frac.denominator)
    return _parse_radical_endpoint(t)


def _parse_num(token: str) -> Any:
    value = parse_numeric_endpoint(token)
    if value is None:
        raise ValueError(f"unsupported numeric token: {token!r}")
    return value


def _is_var(token: str) -> bool:
    t = token.strip()
    return bool(_VAR_RE.match(t)) and t.lower() not in _POS_INF_TOKENS


def _is_num_token(token: str) -> bool:
    if _is_var(token):
        return False
    return parse_numeric_endpoint(token) is not None


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
    text = part.strip()
    if len(text) < 5 or text[0] not in "[(" or text[-1] not in "])":
        return None
    depth = 0
    for pos, ch in enumerate(text):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0 and pos != len(text) - 1:
                return None
    endpoints = _split_top_level(text[1:-1], (",",))
    if not endpoints or len(endpoints) != 2:
        return None
    lbr, rbr = text[0], text[-1]
    lo_s, hi_s = endpoints
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


def _sets_disjoint(a: Set, b: Set) -> bool:
    try:
        return Intersection(a, b) == S.EmptySet
    except Exception:
        return False


def _parse_comma_list(part: str) -> Set | None:
    """Interpret a top-level comma / 、 / ; list of solution pieces.

    Conservative: pairwise-disjoint pieces are alternatives (union), e.g.
    `x<=-4, x>=4` or `(-inf,-4], [4,inf)`.  Exactly two relational half-lines
    whose overlap is a proper bounded part of both are simultaneous
    constraints (intersection), e.g. `x>-1, x<=5`.  Anything else is ambiguous
    and returns None so no verdict is guessed.
    """
    pieces = _split_top_level(part, (",", "、", ";"))
    if not pieces:
        return None
    sets: list[Set] = []
    relational_only = True
    for piece in pieces:
        parsed = _parse_atom(piece)
        if parsed is None:
            return None
        if _parse_relational(piece) is None:
            relational_only = False
        sets.append(parsed)
    if all(_sets_disjoint(a, b) for i, a in enumerate(sets) for b in sets[i + 1 :]):
        acc: Set = sets[0]
        for item in sets[1:]:
            acc = Union(acc, item)
        return acc
    if len(sets) == 2 and relational_only:
        a, b = sets
        both = Intersection(a, b)
        try:
            proper = both != S.EmptySet and not a.is_subset(b) and not b.is_subset(a)
        except Exception:
            proper = False
        if proper:
            return both
    return None


def _parse_piece(part: str) -> Set | None:
    parsed = _parse_atom(part)
    if parsed is not None:
        return parsed
    return _parse_comma_list(part)


def _combine_and(parts: list[str]) -> Set | None:
    sets: list[Set] = []
    for part in parts:
        parsed = _parse_piece(part)
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
