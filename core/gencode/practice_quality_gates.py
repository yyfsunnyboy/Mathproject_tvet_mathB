"""Reusable practice quality gates for question/answer/visual consistency.

These checks are intentionally payload-driven and use independent mathematical
oracles where possible. They do not write to any student database.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Callable


GATE_CODES = (
    "QUESTION_ANSWER_MISMATCH",
    "VISUAL_GIVENS_MISMATCH",
    "MULTIPART_CONTRACT_MISMATCH",
    "CHECKER_FALSE_NEGATIVE",
    "CHECKER_FALSE_POSITIVE",
    "FEEDBACK_LATEX_RENDER_FAILURE",
)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _payload_points(payload: dict[str, Any]) -> dict[str, list[int]]:
    meta = _as_dict(payload.get("metadata"))
    math_core = _as_dict(payload.get("math_core"))
    givens = (
        _as_dict(meta.get("raw_givens"))
        or _as_dict(math_core.get("raw_givens"))
        or _as_dict(meta.get("givens"))
        or _as_dict(math_core.get("givens"))
        or _as_dict(payload.get("givens"))
    )
    points = givens.get("points")
    if isinstance(points, dict) and points:
        out: dict[str, list[int]] = {}
        for label, coords in points.items():
            if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                out[str(label)] = [int(coords[0]), int(coords[1])]
        if out:
            return out
    visual = _as_dict(payload.get("visual_spec"))
    out = {}
    for item in visual.get("points") or []:
        if isinstance(item, dict) and item.get("label") is not None:
            out[str(item["label"])] = [int(item["x"]), int(item["y"])]
    if out:
        return out
    text = str(payload.get("question_text") or payload.get("question") or "")
    return {
        m.group(1): [int(m.group(2)), int(m.group(3))]
        for m in re.finditer(r"([A-Z])\((-?\d+),(-?\d+)\)", text)
    }


def _payload_segments(payload: dict[str, Any]) -> list[tuple[str, str, str]]:
    meta = _as_dict(payload.get("metadata"))
    math_core = _as_dict(payload.get("math_core"))
    givens = (
        _as_dict(meta.get("raw_givens"))
        or _as_dict(math_core.get("raw_givens"))
        or _as_dict(meta.get("givens"))
        or _as_dict(math_core.get("givens"))
        or _as_dict(payload.get("givens"))
    )
    segments = givens.get("segments")
    out: list[tuple[str, str, str]] = []
    if isinstance(segments, list):
        for seg in segments:
            if not isinstance(seg, dict):
                continue
            a = str(seg.get("from") or "")
            b = str(seg.get("to") or "")
            name = str(seg.get("name") or f"{a}{b}")
            if a and b:
                out.append((name, a, b))
        if out:
            return out
    visual = _as_dict(payload.get("visual_spec"))
    for line in visual.get("lines") or []:
        if not isinstance(line, dict):
            continue
        thr = line.get("through_points") or []
        if len(thr) == 2:
            a, b = str(thr[0]), str(thr[1])
            out.append((str(line.get("label") or f"{a}{b}"), a, b))
    if out:
        return out
    text = str(payload.get("question_text") or payload.get("question") or "")
    return [(name, name[0], name[1]) for name in re.findall(r"直線\$([A-Z]{2})\$", text)]


def _format_slope(p1: list[int], p2: list[int]) -> str:
    x1, y1 = int(p1[0]), int(p1[1])
    x2, y2 = int(p2[0]), int(p2[1])
    if x1 == x2:
        return "不存在"
    value = Fraction(y2 - y1, x2 - x1)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _semantic_parts(payload: dict[str, Any]) -> dict[str, str]:
    for key in ("semantic_answer", "correct_answer", "answer"):
        value = payload.get(key)
        if isinstance(value, dict):
            return {str(k): str(v) for k, v in value.items()}
    contract = _as_dict(payload.get("answer_contract"))
    semantic = contract.get("semantic_answer")
    if isinstance(semantic, dict):
        return {str(k): str(v) for k, v in semantic.items()}
    return {}


def check_question_answer_mismatch(payload: dict[str, Any]) -> list[str]:
    problem_type = str(payload.get("problem_type_id") or "")
    blockers: list[str] = []
    if problem_type == "slopes_of_named_segments":
        points = _payload_points(payload)
        segments = _payload_segments(payload)
        parts = _semantic_parts(payload)
        if not points or not segments or not parts:
            return ["QUESTION_ANSWER_MISMATCH:missing_points_or_answers"]
        for index, (_name, a_lbl, b_lbl) in enumerate(segments):
            if a_lbl not in points or b_lbl not in points:
                blockers.append(f"QUESTION_ANSWER_MISMATCH:missing_endpoint:{a_lbl}{b_lbl}")
                continue
            oracle = _format_slope(points[a_lbl], points[b_lbl])
            key = f"part_{index + 1}"
            claimed = parts.get(key)
            if claimed is None and _name in parts:
                claimed = parts[_name]
            if claimed is None:
                blockers.append(f"QUESTION_ANSWER_MISMATCH:missing_part:{key}")
            elif str(claimed) != oracle:
                blockers.append(
                    f"QUESTION_ANSWER_MISMATCH:{key}:stem={oracle}:answer={claimed}"
                )
    elif problem_type == "slope_intercept_read_slope_and_intercept":
        meta = _as_dict(payload.get("metadata"))
        math_core = _as_dict(payload.get("math_core"))
        givens = (
            _as_dict(meta.get("raw_givens"))
            or _as_dict(math_core.get("raw_givens"))
            or _as_dict(meta.get("givens"))
            or _as_dict(payload.get("givens"))
        )
        parts = _semantic_parts(payload)
        equation = str(givens.get("equation") or "")
        text = str(payload.get("question_text") or "")
        if "y" not in equation.lower() and "y" not in text.lower():
            blockers.append("QUESTION_ANSWER_MISMATCH:missing_slope_intercept_equation")
        if set(parts.keys()) < {"m", "b"}:
            blockers.append("QUESTION_ANSWER_MISMATCH:missing_m_or_b_parts")
    return blockers


def check_visual_givens_mismatch(payload: dict[str, Any]) -> list[str]:
    problem_type = str(payload.get("problem_type_id") or "")
    if problem_type != "slopes_of_named_segments":
        return []
    points = _payload_points(payload)
    visual = _as_dict(payload.get("visual_spec"))
    visual_points = {
        str(item.get("label")): [int(item.get("x")), int(item.get("y"))]
        for item in visual.get("points") or []
        if isinstance(item, dict) and item.get("label") is not None
    }
    blockers: list[str] = []
    if not visual_points:
        return ["VISUAL_GIVENS_MISMATCH:missing_visual_points"]
    for label, coords in points.items():
        if label not in visual_points:
            blockers.append(f"VISUAL_GIVENS_MISMATCH:missing_visual_point:{label}")
        elif visual_points[label] != coords:
            blockers.append(
                f"VISUAL_GIVENS_MISMATCH:point:{label}:givens={coords}:visual={visual_points[label]}"
            )
    for index, line in enumerate(visual.get("lines") or []):
        if not isinstance(line, dict):
            continue
        thr = line.get("through_points") or []
        if len(thr) != 2 or thr[0] not in points or thr[1] not in points:
            blockers.append(f"VISUAL_GIVENS_MISMATCH:line_endpoints:{index}")
            continue
        oracle = _format_slope(points[str(thr[0])], points[str(thr[1])])
        if str(line.get("slope")) != oracle:
            blockers.append(
                f"VISUAL_GIVENS_MISMATCH:line_slope:{thr[0]}{thr[1]}:visual={line.get('slope')}:oracle={oracle}"
            )
    return blockers


def check_multipart_contract_mismatch(payload: dict[str, Any]) -> list[str]:
    contract = _as_dict(payload.get("answer_contract"))
    parts = contract.get("parts")
    semantic = _semantic_parts(payload)
    blockers: list[str] = []
    answer_type = str(
        payload.get("answer_type") or contract.get("answer_type") or ""
    ).strip()
    if answer_type != "multi_part" and not isinstance(parts, list):
        return []
    if not isinstance(parts, list) or not parts:
        return ["MULTIPART_CONTRACT_MISMATCH:missing_parts"]
    keys = [str(row.get("key") or "") for row in parts if isinstance(row, dict)]
    if len(keys) != len(set(keys)):
        blockers.append("MULTIPART_CONTRACT_MISMATCH:duplicate_part_keys")
    for row in parts:
        if not isinstance(row, dict):
            blockers.append("MULTIPART_CONTRACT_MISMATCH:invalid_part_row")
            continue
        key = str(row.get("key") or "")
        expected = str(row.get("expected_answer") if row.get("expected_answer") is not None else "")
        if key not in semantic:
            blockers.append(f"MULTIPART_CONTRACT_MISMATCH:semantic_missing:{key}")
        elif str(semantic[key]) != expected:
            blockers.append(
                f"MULTIPART_CONTRACT_MISMATCH:expected_mismatch:{key}:{semantic[key]}!={expected}"
            )
        if not row.get("checker"):
            blockers.append(f"MULTIPART_CONTRACT_MISMATCH:missing_checker:{key}")
    problem_type = str(payload.get("problem_type_id") or "")
    if problem_type == "slope_intercept_read_slope_and_intercept":
        if set(keys) != {"m", "b"}:
            blockers.append(f"MULTIPART_CONTRACT_MISMATCH:expected_m_b_keys_got:{','.join(keys)}")
        for row in parts:
            if not isinstance(row, dict):
                continue
            if str(row.get("checker")) != "rational_checker":
                blockers.append(
                    f"MULTIPART_CONTRACT_MISMATCH:non_rational_checker:{row.get('key')}"
                )
    return blockers


def check_checker_false_negative(
    payload: dict[str, Any],
    *,
    check_answer: Callable[[Any, Any], bool] | None = None,
) -> list[str]:
    if check_answer is None:
        from core.gencode.runtime_skill_wrapper import check_answer as runtime_check

        check_answer = lambda user, correct: bool(  # noqa: E731
            runtime_check(user, correct, payload=payload)
        )
    semantic = _semantic_parts(payload)
    if not semantic:
        return ["CHECKER_FALSE_NEGATIVE:missing_semantic_answer"]
    if not check_answer(semantic, payload.get("correct_answer")):
        return ["CHECKER_FALSE_NEGATIVE:canonical_rejected"]
    # Equivalent rational forms for slope-intercept multipart.
    if str(payload.get("problem_type_id") or "") == "slope_intercept_read_slope_and_intercept":
        b_text = str(semantic.get("b") or "")
        if "/" in b_text:
            try:
                frac = Fraction(b_text)
                # Only require decimal acceptance for terminating decimals.
                den = abs(frac.denominator)
                while den % 2 == 0:
                    den //= 2
                while den % 5 == 0:
                    den //= 5
                if den == 1:
                    decimal_variant = {
                        "m": semantic.get("m"),
                        "b": format(float(frac), ".12g"),
                    }
                    if not check_answer(decimal_variant, payload.get("correct_answer")):
                        return ["CHECKER_FALSE_NEGATIVE:decimal_equivalent_rejected"]
                latex_variant = {
                    "m": semantic.get("m"),
                    "b": f"\\frac{{{frac.numerator}}}{{{frac.denominator}}}",
                }
                if not check_answer(latex_variant, payload.get("correct_answer")):
                    return ["CHECKER_FALSE_NEGATIVE:latex_equivalent_rejected"]
            except Exception:
                pass
    return []


def check_checker_false_positive(
    payload: dict[str, Any],
    *,
    check_answer: Callable[[Any, Any], bool] | None = None,
) -> list[str]:
    if check_answer is None:
        from core.gencode.runtime_skill_wrapper import check_answer as runtime_check

        check_answer = lambda user, correct: bool(  # noqa: E731
            runtime_check(user, correct, payload=payload)
        )
    semantic = _semantic_parts(payload)
    if not semantic:
        return ["CHECKER_FALSE_POSITIVE:missing_semantic_answer"]
    wrong = dict(semantic)
    first_key = next(iter(wrong))
    wrong[first_key] = "999999"
    if check_answer(wrong, payload.get("correct_answer")):
        return ["CHECKER_FALSE_POSITIVE:wrong_answer_accepted"]
    # Partial credit must not become overall correct for slope-intercept.
    if str(payload.get("problem_type_id") or "") == "slope_intercept_read_slope_and_intercept":
        only_m = {"m": semantic.get("m"), "b": ""}
        if check_answer(only_m, payload.get("correct_answer")):
            return ["CHECKER_FALSE_POSITIVE:partial_m_only_accepted"]
    return []


def check_feedback_latex_render_failure(payload: dict[str, Any]) -> list[str]:
    """Static contract check: feedback values that need MathJax must be normalizable."""
    from core.gencode.answer_grading import build_correct_answer_display

    display = build_correct_answer_display(payload)
    if not display:
        return []
    values: list[str] = []
    if isinstance(display.get("items"), list):
        values.extend(str(item.get("value") or "") for item in display["items"] if isinstance(item, dict))
    if display.get("value") is not None:
        values.append(str(display.get("value")))
    if display.get("option_text") is not None:
        values.append(str(display.get("option_text")))
    blockers: list[str] = []
    for value in values:
        if "\\frac" in value and not re.search(r"(\\\(|\\\[|\$)", value):
            blockers.append(f"FEEDBACK_LATEX_RENDER_FAILURE:bare_frac:{value[:80]}")
        if "\\\\(" in value or "\\\\frac" in value:
            # Double-escaped LaTeX often renders literally in the red feedback box.
            blockers.append(f"FEEDBACK_LATEX_RENDER_FAILURE:double_escaped:{value[:80]}")
    return blockers


def run_practice_quality_gates(
    payload: dict[str, Any],
    *,
    check_answer: Callable[[Any, Any], bool] | None = None,
) -> dict[str, Any]:
    blockers: list[str] = []
    blockers.extend(check_question_answer_mismatch(payload))
    blockers.extend(check_visual_givens_mismatch(payload))
    blockers.extend(check_multipart_contract_mismatch(payload))
    blockers.extend(check_checker_false_negative(payload, check_answer=check_answer))
    blockers.extend(check_checker_false_positive(payload, check_answer=check_answer))
    blockers.extend(check_feedback_latex_render_failure(payload))
    return {
        "passed": not blockers,
        "blockers": blockers,
        "gate_codes": list(GATE_CODES),
    }
