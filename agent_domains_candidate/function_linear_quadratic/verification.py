"""Gate checks shared by the sandbox test and the deployment rehearsal (not part of the promoted package).

``verify_payload`` returns a list of problems for one generated payload; an empty list means the
canonical answer is graded correct, every wrong value is graded incorrect, equivalent forms are
accepted and the contract / integrity validators pass.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

FIGURE_CUES = ("如圖", "右圖", "下圖", "在圖(a)")


def _bump_last_number(text: str) -> str:
    matches = list(re.finditer(r"-?\d+(?:/\d+)?", text))
    last = matches[-1]
    return text[:last.start()] + str(Fraction(last.group()) + 1) + text[last.end():]


_FLIP = {"<=": ">=", ">=": "<=", "<": ">", ">": "<"}


def _reverse_inequality(text: str) -> str:
    """``a<k<=b`` -> ``b>=k>a``; ``k<a or k>b`` -> ``k>b or k<a``."""
    if " or " in text:
        return " or ".join(reversed(text.split(" or ")))
    tokens = re.split(r"(<=|>=|<|>)", text)
    out = [tokens[-1]]
    for i in range(len(tokens) - 2, 0, -2):
        out += [_FLIP[tokens[i]], tokens[i - 1]]
    return "".join(out)


def _equivalent_expression(expected: str, required_form: str | None) -> str | None:
    """Same polynomial with its terms (or factors) written in another order."""
    if required_form == "fully_factorized":
        factors = re.findall(r"\([^()]*\)", expected)
        return "".join(reversed(factors)) if len(factors) > 1 else None
    import sympy as sp
    from sympy.parsing.sympy_parser import convert_xor, implicit_multiplication_application, parse_expr, standard_transformations

    expr = sp.expand(parse_expr(expected, transformations=standard_transformations + (implicit_multiplication_application, convert_xor)))
    text = sp.sstr(expr, order="rev-lex").replace("**", "^")
    return text if text != expected else None


def wrong_value(part: dict) -> Any:
    expected, checker = part["expected_answer"], part["checker"]
    if checker == "choice_label_checker":
        labels = [str(c["label"]) for c in part["choices"]]
        if str(expected) in labels:
            return next(label for label in labels if label != str(expected))
        return next(str(c["value"]) for c in part["choices"] if str(c["value"]) != str(expected))
    if checker == "rational_checker":
        return str(Fraction(expected) + 1)
    if checker == "equation_checker":
        left, right = str(expected).split("=")
        return f"{left}={right}+1"
    if checker == "linear_equation_equivalent_checker":
        return str(expected)[:-2] + "+1=0"
    if checker == "linear_relation_set_checker":
        members = [m.strip() for m in str(expected).split(",")]
        return ", ".join(members[:-1] + [members[-1][:-2] + "+1=0"])
    if checker == "coordinate_pair_checker":
        x, y = str(expected).strip("()").split(",")
        return f"({Fraction(x) + 1},{y})"
    if checker == "text_short_checker":
        return "(0,0)"
    if checker in ("expression_equivalence_checker", "expression_checker"):
        return f"({expected})+1"
    if checker == "inequality_solution_checker":
        return _bump_last_number(str(expected))
    if checker == "solution_set_checker":
        return list(expected) + ["99"]
    raise AssertionError(f"no wrong-value rule for {checker}")


def equivalent_value(part: dict) -> Any:
    """A different but mathematically equal rendering, when the checker supports one."""
    expected, checker = part["expected_answer"], part["checker"]
    if checker == "equation_checker":
        left, right = str(expected).split("=")
        return f"2*({left})=2*({right})"
    if checker == "linear_equation_equivalent_checker":
        return f"2({str(expected)[:-2]})=0"
    if checker == "linear_relation_set_checker":
        members = [m.strip() for m in str(expected).split(",")]
        return "，".join(f"2({m[:-2]})=0" for m in reversed(members))
    if checker == "rational_checker" and Fraction(expected).denominator in (1, 2, 4, 5):
        return str(float(Fraction(expected)))
    if checker == "expression_checker":
        return _equivalent_expression(expected, part.get("required_form"))
    if checker == "expression_equivalence_checker" and "sqrt(" in str(expected):
        return re.sub(r"\*?sqrt\((\d+)\)", r"√\1", str(expected))
    if checker == "inequality_solution_checker":
        return _reverse_inequality(str(expected))
    if checker == "coordinate_pair_checker":
        x, y = str(expected).strip("()").split(",")
        return f"( {x} , {y} )"
    if checker == "solution_set_checker":
        return list(reversed(expected))
    return None


def parts_of(payload: dict) -> list[dict]:
    contract = payload["answer_contract"]
    if contract["answer_type"] in {"multi_part", "table_fill"}:
        return contract["parts"]
    return [{**contract, "key": None, "expected_answer": payload["correct_answer"]}]


def grade(payload: dict, answer: Any, skill_id: str) -> bool:
    from core.gencode.runtime_skill_wrapper import check_answer

    return bool(check_answer(answer, payload["correct_answer"], payload=payload,
                             answer_contract=payload["answer_contract"], skill_id=skill_id))


def figure_problems(payload: dict) -> list[str]:
    """A figure is shipped exactly when the stem points to one, and it must be renderable data."""
    text = payload["question_text"]
    cue = any(c in text for c in FIGURE_CUES)
    spec = payload.get("visual_spec")
    if spec and spec.get("kind") == "cartesian_canvas":
        return []  # the blank answer canvas of a drawing question is not a figure the stem points to
    if cue and not spec:
        return ["figure_missing"]
    if spec and not cue:
        return ["figure_without_cue"]
    if spec:
        problems = []
        if spec.get("kind") != "coordinate_plane" or not spec.get("render_required"):
            problems.append("figure_not_renderable")
        if spec.get("show_grid") is not False:
            problems.append("figure_grid_reveals_lengths")
        return problems
    return []


def verify_payload(payload: dict, skill_id: str, component_id: str) -> list[str]:
    from core.gencode.answer_payload import validate_answer_contract_consistency
    from core.gencode.checker_registry import validate_answer_contract_capability
    from core.gencode.services.v3_question_integrity_validator import validate_component_payload

    problems: list[str] = figure_problems(payload)
    contract = payload["answer_contract"]
    if validate_answer_contract_capability(contract)["checker_capability_status"] != "ok":
        problems.append("checker_capability")
    if validate_answer_contract_consistency(payload) or validate_answer_contract_consistency(contract):
        problems.append("contract_consistency")
    integrity = validate_component_payload(payload, component_id=component_id)
    if not integrity["passed"]:
        problems.append(f"integrity:{integrity['blockers']}")
    if contract["answer_type"] == "drawing":
        spec = contract.get("expected_drawing_spec") or {}
        ui = contract.get("ui_contract") or {}
        if not (spec and ui.get("drawing_required") and ui.get("ai_check_required") and not ui.get("text_answer_enabled")
                and not ui.get("submit_button_enabled")):
            problems.append("drawing_contract")
        return problems + _evaluator_problems("canvas", spec)
    parts = parts_of(payload)
    if contract["answer_type"] == "multi_part" and any(p.get("answer_type") == "drawing" for p in parts):
        return problems + verify_drawing_parts(payload, skill_id)
    if not grade(payload, payload["correct_answer"], skill_id):
        problems.append("canonical_rejected")
        return problems
    if contract["answer_type"] in {"multi_part", "table_fill"}:
        for part in parts:
            bad = dict(payload["correct_answer"])
            bad[part["key"]] = wrong_value(part)
            if grade(payload, bad, skill_id):
                problems.append(f"wrong_accepted:{part['key']}")
            equivalent = equivalent_value(part)
            if equivalent is not None:
                good = dict(payload["correct_answer"])
                good[part["key"]] = equivalent
                if not grade(payload, good, skill_id):
                    problems.append(f"equivalent_rejected:{part['key']}")
    else:
        if grade(payload, wrong_value(parts[0]), skill_id):
            problems.append("wrong_accepted")
        equivalent = equivalent_value(parts[0])
        if equivalent is not None and not grade(payload, equivalent, skill_id):
            problems.append("equivalent_rejected")
    return problems


def _drawing_value(tag: str) -> str:
    import json

    return json.dumps({"composite": f"data:image/png;base64,{tag}", "strokes": "data:image/png;base64,STROKES"})


def verify_drawing_parts(payload: dict, skill_id: str) -> list[str]:
    """multi_part with an independent canvas (line_graph): merge logic with a deterministic stand-in for the vision
    analyzer, plus the formal ``evaluate_line_graph`` evaluator against the expected drawing spec."""
    from unittest import mock

    from core.services import drawing_answer_analysis_service as svc

    contract = payload["answer_contract"]
    problems: list[str] = []

    def fake(*, image_data_url, expected_drawing_spec, **_kw):
        if not image_data_url:
            return {"is_correct": None, "system_error": True, "status": "missing_image"}
        if "SYSTEM" in image_data_url:
            return {"is_correct": None, "system_error": True, "status": "analysis_failed"}
        return {"is_correct": "GOOD" in image_data_url, "system_error": False, "status": "success"}

    def good_answer() -> dict:
        return {p["key"]: (_drawing_value("GOOD") if p.get("answer_type") == "drawing" else p["expected_answer"]) for p in contract["parts"]}

    with mock.patch("core.checkers.free_response_drawing_checker.check_drawing_answer", side_effect=fake):
        if not grade(payload, good_answer(), skill_id):
            problems.append("canonical_rejected")
        for part in contract["parts"]:
            bad = good_answer()
            if part.get("answer_type") == "drawing":
                bad[part["key"]] = _drawing_value("BAD")
                if grade(payload, bad, skill_id):
                    problems.append(f"wrong_drawing_accepted:{part['key']}")
                missing = good_answer()
                missing[part["key"]] = ""
                if grade(payload, missing, skill_id):
                    problems.append(f"missing_drawing_accepted:{part['key']}")
                sysfail = good_answer()
                sysfail[part["key"]] = _drawing_value("SYSTEM")
                try:
                    verdict = grade(payload, sysfail, skill_id)
                except RuntimeError:
                    verdict = None
                if verdict:
                    problems.append(f"system_error_accepted:{part['key']}")
            else:
                bad[part["key"]] = wrong_value(part)
                if grade(payload, bad, skill_id):
                    problems.append(f"wrong_accepted:{part['key']}")
                equivalent = equivalent_value(part)
                if equivalent is not None:
                    good = good_answer()
                    good[part["key"]] = equivalent
                    if not grade(payload, good, skill_id):
                        problems.append(f"equivalent_rejected:{part['key']}")
    for part in contract["parts"]:
        if part.get("answer_type") != "drawing":
            continue
        spec = part["expected_drawing_spec"]
        if part.get("input_type") != "canvas" or part.get("canvas", {}).get("axis_range") != spec["axis_range"]:
            problems.append(f"canvas_contract:{part['key']}")
        problems += _evaluator_problems(part["key"], spec)
    return problems


def _parabola_features(expected: dict, *, shift=(0.0, 0.0), flip=False) -> dict:
    a = float(expected["a"]) * (-1 if flip else 1)
    h, k = (float(v) for v in expected["vertex"])
    pts = [[x + shift[0], a * (x - h) ** 2 + k + shift[1]] for x in (h - 2, h - 1, h, h + 1, h + 2)]
    return {"detected": True, "shape": "parabola", "opens": "up" if a > 0 else "down", "vertex": [h + shift[0], k + shift[1]],
            "points_on_curve": pts, "label_text": ""}


def _evaluator_problems(tag: str, spec: dict) -> list[str]:
    """The formal evaluator against canonical / mirrored / displaced / incomplete synthetic analyzer features."""
    from core.services import drawing_answer_analysis_service as svc

    problems: list[str] = []
    if spec.get("drawing_type") == "parabola_graph":
        expected = spec["expected_parabolas"]
        wrap = lambda curves: {"required_elements": {"x_axis": True, "y_axis": True, "curve": True}, "curves": curves, "confidence": 0.95}  # noqa: E731
        good = [_parabola_features(e) for e in expected]
        if svc.evaluate_parabola_graph(wrap(good), spec)["is_correct"] is not True:
            problems.append(f"evaluator_rejects_canonical:{tag}")
        if svc.evaluate_parabola_graph(wrap([_parabola_features(e, flip=True) for e in expected]), spec)["is_correct"] is not False:
            problems.append(f"evaluator_accepts_mirror:{tag}")
        if svc.evaluate_parabola_graph(wrap([_parabola_features(e, shift=(3.0, 2.0)) for e in expected]), spec)["is_correct"] is not False:
            problems.append(f"evaluator_accepts_displaced:{tag}")
        if len(expected) > 1 and svc.evaluate_parabola_graph(wrap(good[:-1]), spec)["is_correct"] is not False:
            problems.append(f"evaluator_accepts_missing_curve:{tag}")
        if len(expected) > 1 and svc.evaluate_parabola_graph(wrap([good[0]] * len(expected)), spec)["is_correct"] is not False:
            problems.append(f"evaluator_accepts_repeated_curve:{tag}")
        return problems
    (x1, y1), (x2, y2) = spec["expected_line"]["points"][0], spec["expected_line"]["points"][-1]
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1
    xs = [spec["axis_range"]["x_min"] + 1, (x1 + x2) / 2 + 0.01, spec["axis_range"]["x_max"] - 1]
    line = {"detected": True, "is_straight": True, "points_on_line": [[x, slope * x + intercept] for x in xs], "slope": slope, "y_intercept": intercept}
    features = {"required_elements": {"x_axis": True, "y_axis": True, "function_line": True}, "line": line, "confidence": 0.95}
    if svc.evaluate_line_graph(features, spec)["is_correct"] is not True:
        problems.append(f"evaluator_rejects_canonical:{tag}")
    mirrored = {**line, "points_on_line": [[x, -slope * x + intercept] for x in xs], "slope": -slope}
    if svc.evaluate_line_graph({**features, "line": mirrored}, spec)["is_correct"] is not False:
        problems.append(f"evaluator_accepts_mirror:{tag}")
    return problems
