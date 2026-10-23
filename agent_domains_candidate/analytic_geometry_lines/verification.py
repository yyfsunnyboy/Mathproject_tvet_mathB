"""Gate checks shared by the sandbox test and the deployment rehearsal (not part of the promoted package).

``verify_payload`` returns a list of problems for one generated payload; an empty list means the
canonical answer is graded correct, every wrong value is graded incorrect, equivalent forms are
accepted and the contract / integrity validators pass.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any


def wrong_value(part: dict) -> Any:
    expected, checker = part["expected_answer"], part["checker"]
    if checker == "choice_label_checker":
        labels = [str(c["label"]) for c in part["choices"]]
        if str(expected) in labels:
            return next(label for label in labels if label != str(expected))
        return next(str(c["value"]) for c in part["choices"] if str(c["value"]) != str(expected))
    if checker == "rational_checker":
        return str(Fraction(expected) + 1)
    if checker == "linear_equation_equivalent_checker":
        return str(expected)[:-2] + "+1=0"
    if checker == "coordinate_pair_checker":
        x, y = str(expected).strip("()").split(",")
        return f"({Fraction(x) + 1},{y})"
    if checker == "expression_equivalence_checker":
        return f"({expected})+1"
    if checker == "solution_set_checker":
        return list(expected) + ["99"]
    if checker == "linear_relation_set_checker":
        return ", ".join(str(expected).split(", ")[:-1]) or "x+y=1"
    if checker == "ordered_inequality_checker":
        terms = str(expected).split(">")
        terms[0], terms[1] = terms[1], terms[0]
        return ">".join(terms)
    raise AssertionError(f"no wrong-value rule for {checker}")


def equivalent_value(part: dict) -> Any:
    """A different but mathematically equal rendering, when the checker supports one."""
    expected, checker = part["expected_answer"], part["checker"]
    if checker == "linear_equation_equivalent_checker":
        return f"2({str(expected)[:-2]})=0"
    if checker == "rational_checker" and Fraction(expected).denominator in (2, 4, 5):
        return str(float(Fraction(expected)))
    if checker == "linear_relation_set_checker":
        return ", ".join(reversed(str(expected).split(", ")))
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


def verify_payload(payload: dict, skill_id: str, component_id: str) -> list[str]:
    from core.gencode.answer_payload import validate_answer_contract_consistency
    from core.gencode.checker_registry import validate_answer_contract_capability
    from core.gencode.services.v3_question_integrity_validator import validate_component_payload

    problems: list[str] = []
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
        return problems
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
    """multi_part with independent canvases: each part is graded on its own and merged into the overall verdict.

    The vision grader is replaced by a deterministic stand-in (tag GOOD / BAD in the image value) so the merge
    logic, the missing-image rule and the system-error rule are exercised without an AI call; the local
    evaluator is exercised separately against the expected drawing spec.
    """
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
    for part in contract["parts"]:
        if part.get("answer_type") != "drawing":
            continue
        spec = part["expected_drawing_spec"]
        if part.get("input_type") != "canvas" or part.get("canvas", {}).get("axis_range") != spec["axis_range"]:
            problems.append(f"canvas_contract:{part['key']}")
        probes = svc.inequality_region_probe_points(spec)
        features = {
            "required_elements": {"x_axis": True, "y_axis": True},
            "lines": [{"points_on_line": _line_points(r["line"]), "style": r["boundary"]} for r in spec["relations"]],
            "shaded_region_detected": True, "confidence": 0.95,
            "probe_points": [{"x": p["x"], "y": p["y"], "shaded": p["expected"]} for p in probes],
        }
        if svc.evaluate_linear_inequality_region(features, spec)["is_correct"] is not True:
            problems.append(f"evaluator_rejects_canonical:{part['key']}")
        features["probe_points"] = [{**p, "shaded": not p["shaded"]} for p in features["probe_points"]]
        if svc.evaluate_linear_inequality_region(features, spec)["is_correct"] is not False:
            problems.append(f"evaluator_accepts_mirror:{part['key']}")
    return problems


def _line_points(line) -> list:
    a, b, c = line
    if b != 0:
        return [[x, (-a * x - c) / b] for x in (-3.0, 0.0, 3.0)]
    return [[-c / a, y] for y in (-3.0, 0.0, 3.0)]
