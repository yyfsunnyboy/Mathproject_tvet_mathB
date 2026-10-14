"""Shared student-visible quality invariants for vocational B1–B4 runtime payloads.

Every check here works only from the delivered payload (stem, choices, visual
payload, answer contract), never from skill ids or component ids, so the same
rules apply to every generator family.
"""
from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Iterable

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

_MATH_SEGMENT_RE = re.compile(
    r"\$\$(.+?)\$\$|\$(.+?)\$|\\\((.+?)\\\)|\\\[(.+?)\\\]",
    re.S,
)
_TEXT_COMMAND_RE = re.compile(r"\\(?:text|mathrm|textrm|operatorname|mbox|textbf)\s*\{[^{}]*\}")
_LATEX_COMMAND_RE = re.compile(r"\\[A-Za-z]+")
_LOWER_RUN_RE = re.compile(r"(?<![A-Za-z\\_.])([a-z]+)(?![A-Za-z_])")
_LABEL_BEFORE_EQUALS_RE = re.compile(r"(?<![A-Za-z\\])([a-z])\s*=")
# Lowercase words that are function names, constants or units rather than products of symbols.
_MATH_WORDS = frozenset(
    {
        "sin", "cos", "tan", "cot", "sec", "csc", "log", "ln", "lg", "exp", "lim",
        "max", "min", "mod", "gcd", "lcm", "deg", "rad", "cm", "mm", "km", "kg",
        "mg", "ml", "sqrt", "frac", "or", "and", "inf", "pi", "abs", "oo",
        "asin", "acos", "atan", "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh",
    }
)
# Spelled-out Greek symbols (SymPy / plain answers) and the glyph used in stems.
_GREEK_WORDS = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "theta": "θ",
    "phi": "φ", "lambda": "λ", "mu": "μ", "sigma": "σ", "omega": "ω",
}
# Internal representations that must never reach a student-visible answer.
_INTERNAL_TOKEN_RE = re.compile(
    r"Interval(?:\.(?:open|Lopen|Ropen))?\s*\(|Union\s*\(|FiniteSet|EmptySet|Complement\s*\("
    r"|(?<![A-Za-z0-9\\])[a-z]+_[a-z]+(?![A-Za-z0-9])"
)
_RAW_MAPPING_RE = re.compile(r"^\s*\{\s*['\"][^'\"]*['\"]\s*:")
# Conventional coordinate-plane symbols that may appear in an answer form
# (line or curve equations) without being introduced in the stem.
_IMPLICIT_ANSWER_SYMBOLS = frozenset({"x", "y"})
_ASKED_CLAUSE_RE = re.compile(r"(?:試求|求|則)")
_RELATION_RE = re.compile(r"[=<>≤≥≠]|\\(?:le|ge|leq|geq|neq|lt|gt|in)\b")
_TRIANGLE_CONTEXT_RE = re.compile(r"△|三角形|\\triangle")
# Lowercase side names conventionally opposite the angles of triangle ABC.
_TRIANGLE_SIDE_SYMBOLS = frozenset({"a", "b", "c"})
_STALE_TOKEN_RE = re.compile(r"(?<![A-Za-z])(None|nan|NaN|undefined|null)(?![A-Za-z])")
_PLACEHOLDER_RE = re.compile(r"\{\{\s*[A-Za-z_][A-Za-z0-9_]*\s*\}\}|<<\s*[A-Za-z_]+\s*>>")

_EXPLANATION_KEYS = (
    "explanation",
    "solution",
    "solution_text",
    "worked_solution",
    "detailed_solution",
)
_VISUAL_KEYS = (
    "visual",
    "visual_spec",
    "visual_aids",
    "visual_payload",
    "diagram",
    "diagram_spec",
    "graph",
    "figure",
    "chart",
    "chart_spec",
    "table",
    "table_spec",
)


def _math_segments(text: str) -> list[str]:
    segments: list[str] = []
    for match in _MATH_SEGMENT_RE.finditer(text or ""):
        segments.append(next(group for group in match.groups() if group is not None))
    return segments


def _strip_latex_commands(segment: str) -> str:
    out = _TEXT_COMMAND_RE.sub(" ", segment)
    return _LATEX_COMMAND_RE.sub(" ", out)


def _symbols_in(fragment: str) -> list[str]:
    """Split implicit products (`kx`, `ax`) into symbols; keep known words out."""
    found: list[str] = []
    for run in _LOWER_RUN_RE.findall(fragment):
        if run in _MATH_WORDS:
            continue
        if run in _GREEK_WORDS:
            found.append(_GREEK_WORDS[run])
            continue
        found.extend(run)
    return found


def math_variables(text: str) -> list[str]:
    """Lowercase symbols used inside math segments, in order of appearance."""
    found: list[str] = []
    for segment in _math_segments(str(text or "")):
        found.extend(_symbols_in(_strip_latex_commands(segment)))
    return found


def _plain_variables(text: str) -> list[str]:
    """Lowercase symbols in a plain (non-LaTeX) answer string."""
    return _symbols_in(_strip_latex_commands(str(text or "")))


def _stem_text(payload: dict[str, Any]) -> str:
    parts = [str(payload.get("question_text") or payload.get("question") or "")]
    structure = payload.get("stem_structure")
    if isinstance(structure, dict):
        parts.append(str(structure.get("prompt") or ""))
        for item in structure.get("items") or []:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or ""))
    return "\n".join(part for part in parts if part)


def _walk(value: Any, depth: int = 0) -> Iterable[Any]:
    if depth > 8:
        return
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child, depth + 1)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _walk(child, depth + 1)


def _visual_blobs(payload: dict[str, Any]) -> list[Any]:
    return [payload[key] for key in _VISUAL_KEYS if payload.get(key)]


def _visual_text(payload: dict[str, Any]) -> str:
    chunks: list[str] = []
    for blob in _visual_blobs(payload):
        for node in _walk(blob):
            if isinstance(node, str):
                chunks.append(node)
    return " ".join(chunks)


def _choice_texts(payload: dict[str, Any]) -> list[str]:
    raw = payload.get("choices") or payload.get("options") or []
    texts: list[str] = []
    for choice in raw if isinstance(raw, list) else []:
        if isinstance(choice, dict):
            texts.append(str(choice.get("text") or choice.get("content") or choice.get("value") or ""))
        else:
            texts.append(str(choice))
    return texts


def _correct_answer(payload: dict[str, Any]) -> Any:
    contract = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    canonical = contract.get("canonical_answer")
    if canonical is None:
        canonical = payload.get("correct_answer", payload.get("answer"))
    return canonical


def _is_choice_payload(payload: dict[str, Any]) -> bool:
    contract = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    mode = str(contract.get("presentation_mode") or payload.get("presentation_mode") or "").strip()
    return bool(_choice_texts(payload)) or mode in {"single_choice", "multiple_choice"}


# ---------------------------------------------------------------------------
# Gate: stale values / undefined symbolic variables
# ---------------------------------------------------------------------------


def stale_value_errors(payload: dict[str, Any]) -> list[str]:
    """Student-visible text must not leak unresolved template values."""
    surfaces = {"question_text": _stem_text(payload), "display_answer": str(payload.get("display_answer") or "")}
    for index, text in enumerate(_choice_texts(payload)):
        surfaces[f"choice[{index}]"] = text
    for key in _EXPLANATION_KEYS:
        if payload.get(key):
            surfaces[key] = str(payload.get(key))
    errors: list[str] = []
    for name, text in surfaces.items():
        if _STALE_TOKEN_RE.search(text) or _PLACEHOLDER_RE.search(text):
            errors.append(f"stale_template_value:{name}")
    return errors


def undefined_variable_errors(payload: dict[str, Any]) -> list[str]:
    """Symbols the student is asked about must be defined by the visible stem."""
    stem = _stem_text(payload)
    visual_vars = set(_plain_variables(_visual_text(payload)))
    stem_vars = math_variables(stem)
    errors: list[str] = []

    asked = list(_ASKED_CLAUSE_RE.finditer(stem))
    if asked:
        clause_start = asked[-1].end()
        targets: list[str] = []
        defined_elsewhere: set[str] = set(visual_vars) | _IMPLICIT_ANSWER_SYMBOLS
        if _TRIANGLE_CONTEXT_RE.search(stem):
            defined_elsewhere |= _TRIANGLE_SIDE_SYMBOLS
        for match in _MATH_SEGMENT_RE.finditer(stem):
            segment = next(group for group in match.groups() if group is not None)
            symbols = _symbols_in(_strip_latex_commands(segment))
            if match.start() >= clause_start and not _RELATION_RE.search(segment):
                targets.extend(symbols)
            else:
                defined_elsewhere.update(symbols)
        defined_elsewhere.update(_plain_variables(_MATH_SEGMENT_RE.sub(" ", stem)))
        for name in dict.fromkeys(targets):
            if name not in defined_elsewhere:
                errors.append(f"asked_variable_undefined:{name}")

    if not _is_choice_payload(payload) and not _is_drawing_payload(payload):
        answer = _correct_answer(payload)
        answer_texts = list(answer.values()) if isinstance(answer, dict) else [answer]
        defined = set(stem_vars) | visual_vars | set(_plain_variables(stem)) | _IMPLICIT_ANSWER_SYMBOLS
        defined |= {glyph for word, glyph in _GREEK_WORDS.items() if glyph in stem or f"\\{word}" in stem}
        for text in answer_texts:
            if not isinstance(text, (str, int, float)):
                continue
            plain = str(text)
            labels = set(_LABEL_BEFORE_EQUALS_RE.findall(plain))
            for name in dict.fromkeys(_plain_variables(plain)):
                if name not in defined and name not in labels:
                    errors.append(f"answer_variable_not_in_stem:{name}")
    return errors


def _is_drawing_payload(payload: dict[str, Any]) -> bool:
    contract = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    blob = " ".join(
        str(value or "")
        for value in (contract.get("answer_type"), contract.get("checker"), payload.get("answer_type"), payload.get("checker"))
    )
    return "drawing" in blob


# ---------------------------------------------------------------------------
# Gate: multipart contract
# ---------------------------------------------------------------------------


def multipart_contract_errors(payload: dict[str, Any]) -> list[str]:
    contract = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    parts = contract.get("parts")
    answer_type = str(contract.get("answer_type") or payload.get("answer_type") or "").strip().lower()
    if not isinstance(parts, list) or not parts:
        if answer_type in {"multi_part", "table_fill"}:
            return ["multipart_parts_missing"]
        return []
    errors: list[str] = []
    keys: list[str] = []
    for index, part in enumerate(parts):
        if not isinstance(part, dict):
            errors.append(f"multipart_part_not_object:{index}")
            continue
        key = str(part.get("key") or part.get("field_key") or "").strip()
        if not key:
            errors.append(f"multipart_part_key_missing:{index}")
            continue
        keys.append(key)
        if not str(part.get("display_label") or part.get("label") or "").strip():
            errors.append(f"multipart_part_label_missing:{key}")
    if len(set(keys)) != len(keys):
        errors.append("multipart_duplicate_keys")
    canonical = _correct_answer(payload)
    if isinstance(canonical, dict):
        canonical_keys = {str(key) for key in canonical}
        if canonical_keys != set(keys):
            errors.append(
                "multipart_canonical_key_mismatch:"
                f"parts={sorted(keys)} canonical={sorted(canonical_keys)}"
            )
    return errors


# ---------------------------------------------------------------------------
# Gate: visual / stem coordinate synchronisation
# ---------------------------------------------------------------------------

_POINT_IN_TEXT_RE = re.compile(
    r"(?<![A-Za-z])([A-Z])(?:_\{?\d+\}?)?\s*\(\s*(-?\d+(?:\.\d+)?(?:/\d+)?)\s*,\s*(-?\d+(?:\.\d+)?(?:/\d+)?)\s*\)"
)


def _num(value: Any) -> Fraction | None:
    if isinstance(value, bool):
        return None
    try:
        if isinstance(value, (int, float)):
            return Fraction(value).limit_denominator(10_000)
        text = str(value).strip()
        if not text:
            return None
        return Fraction(text).limit_denominator(10_000)
    except (ValueError, ZeroDivisionError, TypeError):
        return None


def stem_points(payload: dict[str, Any]) -> dict[str, tuple[Fraction, Fraction]]:
    from core.checkers.math_input_normalization import latex_to_plain

    plain = latex_to_plain(_stem_text(payload))
    points: dict[str, tuple[Fraction, Fraction]] = {}
    for label, x, y in _POINT_IN_TEXT_RE.findall(plain):
        fx, fy = _num(x), _num(y)
        if fx is not None and fy is not None:
            points.setdefault(label, (fx, fy))
    return points


def visual_points(payload: dict[str, Any]) -> dict[str, tuple[Fraction, Fraction]]:
    points: dict[str, tuple[Fraction, Fraction]] = {}
    for blob in _visual_blobs(payload):
        for node in _walk(blob):
            if not isinstance(node, dict):
                continue
            label = str(node.get("label") or node.get("name") or node.get("id") or "").strip()
            if not re.fullmatch(r"[A-Z]", label):
                continue
            x, y = node.get("x"), node.get("y")
            if x is None or y is None:
                coords = node.get("coords") or node.get("coordinates") or node.get("position")
                if isinstance(coords, (list, tuple)) and len(coords) == 2:
                    x, y = coords
            fx, fy = _num(x), _num(y)
            if fx is not None and fy is not None:
                points.setdefault(label, (fx, fy))
    return points


def visual_sync_errors(payload: dict[str, Any]) -> list[str]:
    stem = stem_points(payload)
    visual = visual_points(payload)
    errors: list[str] = []
    for label in sorted(set(stem) & set(visual)):
        if stem[label] != visual[label]:
            errors.append(
                f"visual_stem_point_mismatch:{label}:stem={tuple(map(str, stem[label]))}"
                f":visual={tuple(map(str, visual[label]))}"
            )
    return errors


# ---------------------------------------------------------------------------
# Gate: choices contain the authoritative answer
# ---------------------------------------------------------------------------


def choice_answer_errors(payload: dict[str, Any]) -> list[str]:
    if not _is_choice_payload(payload):
        return []
    texts = _choice_texts(payload)
    if not texts:
        return ["choice_list_missing"]
    answer = str(_correct_answer(payload) or "").strip()
    if not answer:
        return ["choice_answer_missing"]
    labels = [chr(65 + index) for index in range(len(texts))]
    raw = payload.get("choices") or payload.get("options") or []
    for index, choice in enumerate(raw if isinstance(raw, list) else []):
        if isinstance(choice, dict) and str(choice.get("label") or "").strip():
            labels[index] = str(choice.get("label")).strip()
    if answer.upper() in {label.upper() for label in labels}:
        return []
    normalized = {re.sub(r"\s+", "", text) for text in texts}
    if re.sub(r"\s+", "", answer) in normalized:
        return []
    return ["choice_answer_not_in_choices"]


# ---------------------------------------------------------------------------
# Inequality display: natural relational form for students
# ---------------------------------------------------------------------------

_INTERVAL_NOTATION_RE = re.compile(r"[\[\(]\s*[^,\[\]()]*\s*,\s*[^,\[\]()]*\s*[\]\)]|∪|\\cup|∞|\\infty|\binf\b|\{")
_RELATIONAL_RE = re.compile(r"<=|>=|<|>|≤|≥|\\le|\\ge|\\lt|\\gt")
_INTERVAL_TEACHING_RE = re.compile(r"區間|集合|interval|set_notation|set-builder|set_builder", re.I)


def teaches_interval_notation(payload: dict[str, Any]) -> bool:
    blob = " ".join(
        str(payload.get(key) or "")
        for key in ("question_text", "problem_type_id", "line_type", "domain_operation")
    )
    contract = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    blob += " " + str(contract.get("required_form") or contract.get("required_form_hint") or "")
    return bool(_INTERVAL_TEACHING_RE.search(blob))


def _solution_variable(payload: dict[str, Any]) -> str:
    stem = _stem_text(payload)
    counts: dict[str, int] = {}
    for name in math_variables(stem):
        counts[name] = counts.get(name, 0) + 1
    for preferred in ("x", "t", "y", "n", "k", "a"):
        if counts.get(preferred):
            return preferred
    return max(counts, key=counts.get) if counts else "x"


def _format_endpoint(value: Any) -> str | None:
    from sympy import Integer, Rational

    if isinstance(value, Integer):
        return str(int(value))
    if isinstance(value, Rational):
        return f"{value.p}/{value.q}"
    return None


def solution_set_to_natural_text(solution: Any, variable: str = "x") -> str | None:
    """Render a SymPy real solution set as `x <= -15 或 x >= 15` style text.

    Returns None when an endpoint is not a rational number, so callers keep the
    generator's own display rather than producing an awkward rendering.
    """
    from sympy import FiniteSet, Interval, S, Union, oo

    if solution == S.Reals:
        return "全體實數"
    if solution == S.EmptySet:
        return "無解"
    pieces = list(solution.args) if isinstance(solution, Union) else [solution]
    rendered: list[str] = []
    for piece in sorted(pieces, key=lambda item: float(item.inf) if item.inf not in (-oo, oo) else (-1e300 if item.inf == -oo else 1e300)):
        if isinstance(piece, FiniteSet):
            for value in sorted(piece, key=float):
                text = _format_endpoint(value)
                if text is None:
                    return None
                rendered.append(f"{variable} = {text}")
            continue
        if not isinstance(piece, Interval):
            return None
        low, high = piece.start, piece.end
        low_op = "<" if piece.left_open else "<="
        high_op = "<" if piece.right_open else "<="
        if low == -oo and high == oo:
            return "全體實數"
        if low == -oo:
            text = _format_endpoint(high)
            if text is None:
                return None
            rendered.append(f"{variable} {high_op} {text}")
        elif high == oo:
            text = _format_endpoint(low)
            if text is None:
                return None
            rendered.append(f"{variable} {'>' if piece.left_open else '>='} {text}")
        else:
            lo_text, hi_text = _format_endpoint(low), _format_endpoint(high)
            if lo_text is None or hi_text is None:
                return None
            rendered.append(f"{lo_text} {low_op} {variable} {high_op} {hi_text}")
    return " 或 ".join(rendered) if rendered else None


def is_inequality_solution_payload(payload: dict[str, Any]) -> bool:
    """True only for real-solution-set answers graded as inequalities.

    Coordinate pairs such as `(-4,3)` and root lists such as `[-5, 1]` share
    bracket syntax with intervals and must never be treated as one.
    """
    from core.gencode.answer_payload import (
        answer_type_family,
        is_coordinate_pair_contract,
        is_coordinate_pair_runtime_payload,
    )
    from core.gencode.inequality_solution_routing import is_inequality_solution_context

    contract = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    if is_coordinate_pair_contract(contract) or is_coordinate_pair_runtime_payload(payload):
        return False
    if answer_type_family(str(contract.get("answer_type") or payload.get("answer_type") or "")) in {
        "solution_set",
        "coordinate_pair",
        "multi_part",
        "choice",
    }:
        return False
    return bool(is_inequality_solution_context(payload, contract, _correct_answer(payload)))


def natural_inequality_display(payload: dict[str, Any]) -> str | None:
    """Return the student-facing relational display, or None when not applicable."""
    if _is_choice_payload(payload) or teaches_interval_notation(payload):
        return None
    canonical = _correct_answer(payload)
    if isinstance(canonical, (dict, list, tuple)) or canonical is None:
        return None
    text = str(canonical)
    if not (_INTERVAL_NOTATION_RE.search(text) or _RELATIONAL_RE.search(text)):
        return None
    if not is_inequality_solution_payload(payload):
        return None
    from core.checkers.inequality_solution_checker import parse_real_solution_set

    solution = parse_real_solution_set(text)
    if solution is None:
        return None
    return solution_set_to_natural_text(solution, _solution_variable(payload))


def display_answer_errors(payload: dict[str, Any]) -> list[str]:
    """Interval/set notation must not be the default student display."""
    if _is_choice_payload(payload) or teaches_interval_notation(payload):
        return []
    display = str(payload.get("display_answer") or _correct_answer(payload) or "")
    if not display or not _INTERVAL_NOTATION_RE.search(display):
        return []
    if natural_inequality_display(payload) is None:
        return []
    return ["display_answer_uses_internal_interval_form"]


def internal_representation_errors(payload: dict[str, Any]) -> list[str]:
    """Student-visible answers must not leak SymPy reprs, code tokens or raw mappings."""
    if _is_drawing_payload(payload):
        return []
    surfaces: dict[str, str] = {}
    contract = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    parts = contract.get("parts") if isinstance(contract.get("parts"), list) else []
    canonical = _correct_answer(payload)
    if _is_choice_payload(payload):
        # Post-submit feedback shows the selected option text, not display_answer.
        pass
    elif parts or isinstance(canonical, dict):
        values = dict(canonical) if isinstance(canonical, dict) else {}
        for index, part in enumerate(parts):
            if isinstance(part, dict):
                key = str(part.get("key") or part.get("field_key") or index + 1)
                values.setdefault(key, part.get("canonical_answer", part.get("expected_answer")))
        for key, value in values.items():
            if isinstance(value, str):
                surfaces[f"part[{key}]"] = value
    else:
        display = payload.get("display_answer")
        if isinstance(display, str):
            surfaces["display_answer"] = display
            if _RAW_MAPPING_RE.search(display):
                return ["display_answer_is_raw_mapping"]
    for index, text in enumerate(_choice_texts(payload)):
        surfaces[f"choice[{index}]"] = text
    return [
        f"answer_exposes_internal_representation:{name}"
        for name, text in surfaces.items()
        if _INTERNAL_TOKEN_RE.search(text)
    ]


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------


def question_quality_errors(payload: dict[str, Any]) -> list[str]:
    """Structural student-visible invariants that need no checker execution."""
    if not isinstance(payload, dict):
        return ["payload_not_object"]
    errors: list[str] = []
    errors.extend(stale_value_errors(payload))
    errors.extend(undefined_variable_errors(payload))
    errors.extend(multipart_contract_errors(payload))
    errors.extend(visual_sync_errors(payload))
    errors.extend(choice_answer_errors(payload))
    errors.extend(display_answer_errors(payload))
    errors.extend(internal_representation_errors(payload))
    return errors
