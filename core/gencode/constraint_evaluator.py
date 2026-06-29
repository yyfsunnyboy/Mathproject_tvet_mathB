from __future__ import annotations

import operator
import re
from typing import Any

OPS = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}


def _resolve_operand(operand: Any, variables: dict[str, Any]) -> Any:
    if not isinstance(operand, dict):
        raise TypeError("Operand must be a dictionary.")

    operand_keys = set(operand)

    if operand_keys == {"var"}:
        var_name = operand["var"]
        if not isinstance(var_name, str) or not var_name.strip():
            raise ValueError("Variable name must be a non-empty string.")
        if var_name not in variables:
            raise ValueError(f"Variable {var_name!r} is not defined in variables.")
        return variables[var_name]

    if operand_keys == {"value"}:
        return operand["value"]

    if "var" in operand_keys and "value" in operand_keys:
        raise ValueError("Operand cannot contain both 'var' and 'value'.")
    if "var" not in operand_keys and "value" not in operand_keys:
        raise ValueError("Operand must contain either 'var' or 'value'.")

    raise ValueError("Operand must not contain keys other than 'var' or 'value'.")


def _check_compatibility(l: Any, r: Any) -> None:
    is_num_l = isinstance(l, (int, float)) and not isinstance(l, bool)
    is_num_r = isinstance(r, (int, float)) and not isinstance(r, bool)

    if is_num_l and is_num_r:
        return
    if type(l) is type(r):
        return

    raise TypeError(
        f"Operand types {type(l).__name__} and {type(r).__name__} are incompatible for comparison."
    )


def evaluate_binary_constraint(constraint: dict[str, Any], variables: dict[str, Any]) -> bool:
    """Evaluate a binary comparison constraint safely against a dictionary of variables.

    Parameters
    ----------
    constraint:         Dict containing 'left', 'operator', and 'right' keys.
    variables:          Dict of defined variables and their values.

    Returns
    -------
    Boolean evaluation result.
    """
    if not isinstance(constraint, dict):
        raise TypeError("Constraint must be a dictionary.")

    for key in ("left", "operator", "right"):
        if key not in constraint:
            raise ValueError(f"Constraint missing required field: {key!r}")

    op = str(constraint["operator"]).strip()
    if op not in OPS:
        raise ValueError(f"Unsupported operator: {op!r}")

    left_val = _resolve_operand(constraint["left"], variables)
    right_val = _resolve_operand(constraint["right"], variables)

    _check_compatibility(left_val, right_val)

    return bool(OPS[op](left_val, right_val))


def evaluate_hard_constraints(
    constraints: list[dict[str, Any]],
    variables: dict[str, Any],
) -> tuple[bool, list[dict[str, Any]]]:
    """Evaluate a list of binary comparison constraints.

    Parameters
    ----------
    constraints:        List of constraint dictionaries.
    variables:          Dict of defined variables and their values.

    Returns
    -------
    Tuple (all_satisfied, list_of_failures) where each failure is a dict with 'index' and 'constraint'.
    """
    if not isinstance(constraints, list):
        raise TypeError("Constraints must be a list.")

    failures = []
    for idx, c in enumerate(constraints):
        satisfied = evaluate_binary_constraint(c, variables)
        if not satisfied:
            failures.append({
                "index": idx,
                "constraint": c,
            })

    return len(failures) == 0, failures
