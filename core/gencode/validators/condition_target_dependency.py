from __future__ import annotations

import re
from typing import Any

from core.gencode.problem_type_spec import get_dependency_contract, get_semantic_contract, get_stem_contract

_NUMERIC_LITERAL = re.compile(r"^-?\d+(\.\d+)?$")
_SYMBOLIC_INEQUALITY = re.compile(r"[a-zA-Z]\s*<\s*[a-zA-Z]")
_NUMERIC_COORD_IN_TEXT = re.compile(
    r"[PQ]\s*(?:\\left)?\s*\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*(?:\\right)?\s*\)",
    re.I,
)
_VAR_IN_EXPR = re.compile(r"[a-zA-Z]+")


def _is_numeric_literal(expr: str) -> bool:
    return bool(_NUMERIC_LITERAL.fullmatch(str(expr or "").strip()))


def _variables_from_text(text: str) -> set[str]:
    return {m.group(0) for m in _VAR_IN_EXPR.finditer(str(text or "")) if len(m.group(0)) == 1}


def _normalize_givens(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    raw = metadata.get("givens")
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            gtype = str(item.get("type", "")).strip() or "symbolic_condition"
            text = str(item.get("text", "")).strip()
            variables = item.get("variables")
            if not isinstance(variables, list):
                variables = sorted(_variables_from_text(text))
            out.append({"type": gtype, "text": text, "variables": [str(v) for v in variables]})
        elif isinstance(item, str) and item.strip():
            text = item.strip()
            gtype = "symbolic_condition" if _SYMBOLIC_INEQUALITY.search(text) or re.search(r"象限", text) else "given"
            out.append({"type": gtype, "text": text, "variables": sorted(_variables_from_text(text))})
    return out


def _normalize_target(metadata: dict[str, Any], question_text: str) -> dict[str, Any] | None:
    target = metadata.get("target")
    if isinstance(target, dict):
        x_expr = str(target.get("x_expr", target.get("x", ""))).strip()
        y_expr = str(target.get("y_expr", target.get("y", ""))).strip()
        variables = target.get("variables")
        if not isinstance(variables, list):
            variables = sorted(_variables_from_expr(x_expr, y_expr))
        return {
            "type": str(target.get("type", "coordinate_point")).strip() or "coordinate_point",
            "label": str(target.get("label", "Q")).strip() or "Q",
            "x_expr": x_expr,
            "y_expr": y_expr,
            "variables": [str(v) for v in variables],
        }
    if isinstance(target, str) and target.strip():
        return {"type": "text", "label": "", "x_expr": "", "y_expr": "", "variables": _variables_from_text(target)}
    m = _NUMERIC_COORD_IN_TEXT.search(question_text)
    if m:
        return {
            "type": "coordinate_point",
            "label": "Q",
            "x_expr": m.group(1),
            "y_expr": m.group(2),
            "variables": [],
        }
    return None


def _variables_from_expr(*exprs: str) -> set[str]:
    found: set[str] = set()
    for expr in exprs:
        found.update(_variables_from_text(expr))
    return found


def _question_has_symbolic_condition(question_text: str) -> bool:
    qt = str(question_text or "")
    if _SYMBOLIC_INEQUALITY.search(qt):
        return True
    if re.search(r"P\s*\(\s*a\s*,\s*b\s*\)", qt, re.I) and re.search(r"象限", qt):
        return True
    return False


def validate_condition_target_dependency(payload: dict[str, Any], problem_type_spec: dict[str, Any]) -> list[str]:
    """Generic givens/target dependency check; not skill-specific."""
    errors: list[str] = []
    dependency_contract = get_dependency_contract(problem_type_spec)
    semantic_contract = get_semantic_contract(problem_type_spec)
    stem_contract = get_stem_contract(problem_type_spec)
    required_objects = stem_contract.get("required_math_objects", [])
    if not isinstance(required_objects, list):
        required_objects = []

    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    question_text = str(payload.get("question_text", ""))
    derivation = metadata.get("derivation") if isinstance(metadata.get("derivation"), list) else []
    derivation_text = " ".join(str(x) for x in derivation)

    givens = _normalize_givens(metadata)
    target = _normalize_target(metadata, question_text)

    symbolic_givens = [g for g in givens if g.get("type") == "symbolic_condition"]
    if not symbolic_givens and _question_has_symbolic_condition(question_text):
        symbolic_givens = [
            {
                "type": "symbolic_condition",
                "text": question_text,
                "variables": sorted(_variables_from_text(question_text)),
            }
        ]

    needs_dependency = bool(
        dependency_contract.get("givens_must_be_used", False)
        or dependency_contract.get("target_answer_must_depend_on_givens", False)
        or "symbolic_condition" in required_objects
    )
    if not needs_dependency or not symbolic_givens:
        return errors

    sym_vars: set[str] = set()
    for g in symbolic_givens:
        sym_vars.update(str(v) for v in (g.get("variables") or []))

    target_vars: set[str] = set()
    target_is_numeric_point = False
    if target:
        target_vars = set(str(v) for v in (target.get("variables") or []))
        x_expr = str(target.get("x_expr", ""))
        y_expr = str(target.get("y_expr", ""))
        if target.get("type") == "coordinate_point" and _is_numeric_literal(x_expr) and _is_numeric_literal(y_expr):
            target_is_numeric_point = True

    if _NUMERIC_COORD_IN_TEXT.search(question_text) and sym_vars:
        if not target_vars or target_is_numeric_point:
            errors.append("condition_unused_by_target")

    if sym_vars and target_is_numeric_point:
        errors.append("condition_unused_by_target")

    if sym_vars and target_vars and not (sym_vars & target_vars) and target_is_numeric_point:
        errors.append("condition_unused_by_target")

    if bool(dependency_contract.get("variables_in_conditions_must_appear_in_target", False)) and sym_vars:
        if not target_vars or not (sym_vars & target_vars):
            errors.append("variables_in_conditions_missing_in_target")

    if bool(dependency_contract.get("givens_must_be_used", False)) and symbolic_givens:
        for g in symbolic_givens:
            text = str(g.get("text", "")).strip()
            vars_in_g = set(g.get("variables") or [])
            referenced = any(v in derivation_text for v in vars_in_g) or any(v in str(target) for v in vars_in_g)
            referenced = referenced or text in derivation_text or text in question_text
            if vars_in_g and not referenced and target_is_numeric_point:
                errors.append("given_unused_in_derivation")

    reject_if = semantic_contract.get("reject_if", []) if isinstance(semantic_contract.get("reject_if"), list) else []
    if "unused_condition" in reject_if and "condition_unused_by_target" in errors:
        pass
    elif "unused_condition" in reject_if and target_is_numeric_point and sym_vars:
        errors.append("condition_unused_by_target")

    if "answer_not_derivable" in reject_if and len(derivation) < 1 and symbolic_givens:
        errors.append("ambiguous_answer")

    return sorted(set(errors))
