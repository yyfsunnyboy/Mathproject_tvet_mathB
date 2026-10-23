"""Gate checks shared by the sandbox test and the deployment rehearsal (not part of the promoted package).

``verify_payload`` returns a list of problems for one generated payload; an empty list means the
canonical answer is graded correct, every wrong value is graded incorrect, equivalent forms are
accepted and the contract / integrity validators pass.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

FIGURE_CUES = ("如圖", "右圖", "下圖")


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
    if checker == "expression_equivalence_checker":
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
    if checker == "rational_checker" and Fraction(expected).denominator in (2, 4, 5):
        return str(float(Fraction(expected)))
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
    parts = parts_of(payload)
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
