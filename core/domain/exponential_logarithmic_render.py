# -*- coding: utf-8 -*-
"""TeX rendering and matrix packing shared by the B3 Chapter 4 builders.

Rendering only. Mathematical values arrive already computed by
``exponential_logarithmic_math``.
"""

from __future__ import annotations

import hashlib
import random
import re
from decimal import Decimal
from fractions import Fraction
from typing import Any, Iterable, Mapping

from core.domain.exponential_logarithmic_math import (
    as_fraction,
    decimal_plain,
    fraction_plain,
)
from core.gencode.choice_contract_validator import choice_semantic_key, infer_choice_answer_shape
from core.gencode.multipart_stem_contract import build_stem_structure, stem_structure_to_question_text

DOMAIN_KEY = "exponential.logarithmic"

SOURCE_LABEL_RE = re.compile(r"例\s*\d|隨堂|習題|基礎題|進階題|自我評量|統測|〔|〕|CH4")
SOLUTION_MARKER_RE = re.compile(r"○解|〇解|解：|解:|詳解|\\o\b|\\ac\b|\\o\\ac|所以|因為|故得")
EQ_RESIDUE_RE = re.compile(r"[\ue000-\uf8ff]|[\x00-\x08\x0b\x0c\x0e-\x1f]|MERGEFORMAT|EQ \\")
BARE_LOG_RE = re.compile(r"\\log(?!_)")
HTML_TAG_RE = re.compile(r"<[A-Za-z/!]")


def tex_num(value: object, *, small: bool = False) -> str:
    v = as_fraction(value)
    if v.denominator == 1:
        return str(v.numerator)
    frac = r"\frac" if small else r"\dfrac"
    sign = "-" if v < 0 else ""
    return rf"{sign}{frac}{{{abs(v.numerator)}}}{{{v.denominator}}}"


def tex_exp(exponent: object, *, decimal: str | None = None) -> str:
    if decimal is not None:
        return decimal
    e = as_fraction(exponent)
    if e.denominator == 1:
        return str(e.numerator)
    sign = "-" if e < 0 else ""
    return rf"{sign}\frac{{{abs(e.numerator)}}}{{{e.denominator}}}"


def tex_base(value: object, *, decimal: str | None = None, mixed: bool = False) -> str:
    if decimal is not None:
        return rf"\left({decimal}\right)"
    v = as_fraction(value)
    if v.denominator == 1 and v >= 0:
        return str(v.numerator)
    if v.denominator == 1:
        return rf"\left({v.numerator}\right)"
    if mixed and v > 1:
        whole, rest = divmod(v.numerator, v.denominator)
        return rf"\left({whole}\dfrac{{{rest}}}{{{v.denominator}}}\right)"
    return rf"\left({tex_num(v)}\right)"


def tex_power(base: object, exponent: object, *, base_decimal: str | None = None,
              exp_decimal: str | None = None, mixed: bool = False) -> str:
    return f"{tex_base(base, decimal=base_decimal, mixed=mixed)}^{{{tex_exp(exponent, decimal=exp_decimal)}}}"


def tex_radical(radicand: str, index: int) -> str:
    if index == 2:
        return rf"\sqrt{{{radicand}}}"
    return rf"\sqrt[{index}]{{{radicand}}}"


def tex_prime_power(p: int, exponent: object, *, small: bool = False) -> str:
    """Readable TeX for p**exponent: 8, 1/8, sqrt{8}, 1/sqrt[3]{9}, ..."""
    e = as_fraction(exponent)
    frac = r"\frac" if small else r"\dfrac"
    if e == 0:
        return "1"
    negative = e < 0
    e = abs(e)
    if e.denominator == 1:
        body = str(p ** e.numerator)
    else:
        body = tex_radical(str(p ** e.numerator), e.denominator)
    if negative:
        return rf"{frac}{{1}}{{{body}}}"
    return body


def tex_mono(item: Mapping[str, Fraction]) -> str:
    parts = []
    for var, e in sorted(item.items()):
        e = as_fraction(e)
        if e == 0:
            continue
        parts.append(var if e == 1 else f"{var}^{{{tex_exp(e)}}}")
    return "".join(parts) if parts else "1"


def tex_log(base_tex: str | None, arg_tex: str) -> str:
    """``\\log_{b} x``; ``base_tex=None`` means a common logarithm ``\\log x``."""
    if base_tex is None:
        return rf"\log {arg_tex}"
    return rf"\log_{{{base_tex}}} {arg_tex}"


def paren(tex: str) -> str:
    return rf"\left({tex}\right)"


def m(tex: str) -> str:
    """Inline math. ``<`` becomes ``\\lt`` because choice text is inserted as HTML."""
    return r"\(" + tex.replace("<", r"\lt ") + r"\)"


def tex_given(pairs: Iterable[tuple[str, Decimal]], *, common: bool = True, base10_tex: bool = False) -> str:
    """Render given approximations, e.g. ``\\(\\log 2\\approx 0.3010\\)``."""
    shown = []
    for arg, value in pairs:
        head = rf"\log_{{10}} {arg}" if base10_tex or not common else rf"\log {arg}"
        shown.append(m(rf"{head}\approx {format(value, 'f')}"))
    return "、".join(shown)


def check_student_stem(text: str) -> None:
    if SOURCE_LABEL_RE.search(text):
        raise ValueError(f"source_label_in_stem:{SOURCE_LABEL_RE.search(text).group(0)}")
    if SOLUTION_MARKER_RE.search(text):
        raise ValueError(f"solution_marker_in_stem:{SOLUTION_MARKER_RE.search(text).group(0)}")
    if EQ_RESIDUE_RE.search(text):
        raise ValueError("eq_field_residue_in_stem")
    outside = re.sub(r"\\\((.*?)\\\)", "", text, flags=re.S)
    if "\\" in outside:
        raise ValueError("raw_latex_outside_math")
    if HTML_TAG_RE.search(text):
        raise ValueError("html_markup_in_stem")


def make_choices(
    rng: random.Random,
    correct: tuple[str, str],
    distractors: Iterable[tuple[str, str]],
    *,
    same: Any = None,
) -> tuple[list[dict[str, str]], str]:
    """Four choices: the correct (value, text) and three distinct distractors.

    ``same(a, b)`` reports mathematical equivalence of two values; equivalent
    distractors are dropped so exactly one choice is correct.
    """
    same = same or (lambda a, b: a == b)
    correct_shape = infer_choice_answer_shape(correct[0])
    allowed = {correct_shape, "number"} if correct_shape == "expression" else {correct_shape}
    keys = {choice_semantic_key(correct[0])}
    picked: list[tuple[str, str]] = []
    for value, text in distractors:
        if same(value, correct[0]) or any(same(value, row[0]) for row in picked):
            continue
        key = choice_semantic_key(value)
        if infer_choice_answer_shape(value) not in allowed or not key or key in keys:
            continue
        keys.add(key)
        picked.append((value, text))
        if len(picked) == 3:
            break
    if len(picked) < 3:
        raise ValueError("distractor_shortage")
    rows = [correct, *picked]
    rng.shuffle(rows)
    labels = ["A", "B", "C", "D"]
    choices = [{"label": lab, "value": value, "text": text} for lab, (value, text) in zip(labels, rows)]
    correct_label = next(row["label"] for row in choices if row["value"] == correct[0])
    return choices, correct_label


def statement_choice(text: str) -> tuple[str, str]:
    """(value, text) for a true/false statement option.

    Statements mix math shapes (``y=2^x ...`` vs plain prose), so the value is a
    stable statement id that keeps every option in one answer-shape class."""
    return "敘述" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:10], text


def same_number(a: str, b: str) -> bool:
    try:
        return as_fraction(a) == as_fraction(b)
    except (ValueError, ZeroDivisionError):
        return a == b


def same_expression(a: str, b: str) -> bool:
    import sympy as sp

    try:
        ea = sp.sympify(a.replace("^", "**"))
        eb = sp.sympify(b.replace("^", "**"))
        return sp.simplify(ea - eb) == 0
    except (sp.SympifyError, TypeError, SyntaxError):
        return a == b


def num_choice(value: object) -> tuple[str, str]:
    return fraction_plain(value), m(tex_num(value))


def pack(
    op: str,
    *,
    answer: Any,
    explanation: str,
    params: dict[str, Any],
    question: str | None = None,
    prompt: str | None = None,
    items: list[dict[str, str]] | None = None,
    presentation: str = "short_answer",
    answer_type: str | None = None,
    choices: list[dict[str, str]] | None = None,
    correct_label: str | None = None,
    part_labels: dict[str, str] | None = None,
    part_checkers: dict[str, str] | None = None,
    answer_checker: str | None = None,
    visual: dict[str, Any] | None = None,
    given_approximations: dict[str, str] | None = None,
    common_log: bool = False,
    visual_type: str = "TEXT_ONLY",
) -> dict[str, Any]:
    stem = None
    if items:
        stem = build_stem_structure(prompt or "", items)
        question = stem_structure_to_question_text(stem)
    question = str(question or "").strip()
    check_student_stem(question)
    for row in choices or []:
        text = str(row.get("text") or "")
        check_student_stem(text)
        if "<" in text:
            raise ValueError("raw_less_than_in_choice_html")
    if not common_log and BARE_LOG_RE.search(question):
        raise ValueError("log_base_lost")
    parts: dict[str, str] = {}
    if isinstance(answer, dict):
        parts = {str(k): str(v) for k, v in answer.items()}
        if len(parts) < 2:
            raise ValueError("multipart_needs_two_parts")
        answer_value: Any = parts
        resolved_type = "multi_part"
    else:
        answer_value = str(answer)
        resolved_type = answer_type or "expression"
    if presentation == "single_choice":
        values = [row["value"] for row in choices or []]
        if len(values) != 4 or len(set(values)) != 4 or answer_value not in values:
            raise ValueError("mcq_contract")
        resolved_type = "single_choice"
    labels = dict(part_labels or {})
    block = {
        "value": answer_value,
        "canonical_form": answer_value,
        "general_form": answer_value,
        "coefficients": [],
        "parts": parts,
        "part_labels": labels if parts and labels else [],
    }
    matrix: dict[str, Any] = {
        "domain_key": DOMAIN_KEY,
        "domain_operation": op,
        "operation": op,
        "question": question,
        "question_text": question,
        "answer": block,
        "explanation": [explanation],
        "explanation_steps": [explanation],
        "distractors": [],
        "givens": dict(params),
        "params": dict(params),
        "presentation_mode": presentation,
        "answer_type": resolved_type,
        "semantic_answer": answer_value,
        "part_checkers": dict(part_checkers or {}),
        "answer_checker": answer_checker,
        "visual_spec": visual or {"kind": "none"},
        "validation_facts": {
            "domain_operation": op,
            "exact_arithmetic": True,
            "answer_type": resolved_type,
            "presentation_mode": presentation,
            "multipart_count": len(parts) if parts else 1,
            "semantic_answer": answer_value,
            "given_approximations": dict(given_approximations or {}),
            "log_notation": "common" if common_log else "explicit_base",
            "visual_type": visual_type,
        },
    }
    if stem:
        matrix["stem_structure"] = stem
    if presentation == "single_choice":
        matrix["choices"] = choices
        matrix["correct_label"] = correct_label
        matrix["correct_answer"] = correct_label
        matrix["distractors"] = [row["value"] for row in choices or [] if row["label"] != correct_label]
    return matrix


def decimal_answer(value: Decimal) -> str:
    return decimal_plain(value)
