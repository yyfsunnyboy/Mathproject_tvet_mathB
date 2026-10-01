"""Shared four-option pack for domains whose answers are exact numeric expressions."""

from __future__ import annotations

import random
from typing import Any, Callable

import sympy as sp

_FILL_FACTORS = (2, sp.Rational(1, 2), 3, sp.Rational(3, 2), 4, sp.Rational(1, 3), 5, 6)


def _value_key(text: str) -> str:
    raw = str(text or "").strip()
    try:
        expr = sp.nsimplify(sp.sympify(raw.replace("^", "**")))
        if expr.is_number:
            return f"num:{sp.N(expr, 12)}"
        return f"expr:{sp.srepr(sp.simplify(expr))}"
    except (sp.SympifyError, TypeError, ValueError, SyntaxError, AttributeError):
        return "text:" + raw.replace(" ", "")


def build_exact_choice_payload(
    canonical: str,
    distractors: list[str],
    rng: random.Random,
    *,
    format_value: Callable[[Any], str],
) -> dict[str, Any]:
    """Four mathematically distinct options; fillers keep the canonical answer's shape."""
    seen = {_value_key(canonical)}
    extras: list[str] = []
    for item in distractors:
        key = _value_key(item)
        if key in seen:
            continue
        seen.add(key)
        extras.append(item)
    rng.shuffle(extras)
    options = [canonical] + extras[:3]
    try:
        base = sp.nsimplify(sp.sympify(str(canonical).replace("^", "**")))
    except (sp.SympifyError, TypeError, ValueError, SyntaxError):
        base = None
    for factor in _FILL_FACTORS:
        if len(options) >= 4 or base is None or base == 0:
            break
        candidate = format_value(sp.simplify(base * factor))
        key = _value_key(candidate)
        if key not in seen:
            seen.add(key)
            options.append(candidate)
    filler = 2
    while len(options) < 4:
        candidate = format_value(sp.Integer(filler))
        filler += 1
        key = _value_key(candidate)
        if key not in seen:
            seen.add(key)
            options.append(candidate)
    rng.shuffle(options)
    labels = ["A", "B", "C", "D"]
    choices = [{"label": labels[i], "text": options[i], "value": options[i]} for i in range(4)]
    correct = next(c["label"] for c in choices if c["value"] == canonical)
    return {"choices": choices, "correct_label": correct, "semantic_answer": canonical}
