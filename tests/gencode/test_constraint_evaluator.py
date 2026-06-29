from __future__ import annotations

import copy

import pytest

from core.gencode.constraint_evaluator import (
    evaluate_binary_constraint,
    evaluate_hard_constraints,
)


def _constraint(left: object, operator: str = "==", right: object = None) -> dict:
    return {
        "left": left,
        "operator": operator,
        "right": {"value": 3} if right is None else right,
    }


def test_var_operand_with_exact_key_set_is_accepted() -> None:
    assert evaluate_binary_constraint(_constraint({"var": "x"}), {"x": 3})


def test_value_operand_with_exact_key_set_is_accepted() -> None:
    assert evaluate_binary_constraint(_constraint({"value": 3}), {})


@pytest.mark.parametrize(
    "operand",
    [
        {"var": "x", "extra": 1},
        {"var": "x", "label": "test"},
        {"value": 3, "extra": 1},
        {"value": 3, "label": "test"},
    ],
)
def test_operand_with_extra_key_is_rejected(operand: dict) -> None:
    with pytest.raises(ValueError):
        evaluate_binary_constraint(_constraint(operand), {"x": 3})


def test_operand_with_var_and_value_is_rejected() -> None:
    with pytest.raises(ValueError, match="cannot contain both"):
        evaluate_binary_constraint(_constraint({"var": "x", "value": 3}), {"x": 3})


@pytest.mark.parametrize("operand", [{}, {"foo": 1}])
def test_operand_without_var_or_value_is_rejected(operand: dict) -> None:
    with pytest.raises(ValueError, match="must contain either"):
        evaluate_binary_constraint(_constraint(operand), {})


def test_non_dict_operand_is_rejected() -> None:
    with pytest.raises(TypeError, match="must be a dictionary"):
        evaluate_binary_constraint(_constraint("x"), {"x": 3})


@pytest.mark.parametrize(
    ("operator", "left", "right", "expected"),
    [
        (">", 4, 3, True),
        (">=", 3, 3, True),
        ("<", 2, 3, True),
        ("<=", 3, 3, True),
        ("==", 3, 3, True),
        ("!=", 2, 3, True),
    ],
)
def test_six_supported_operators_are_unchanged(
    operator: str,
    left: int,
    right: int,
    expected: bool,
) -> None:
    assert (
        evaluate_binary_constraint(
            _constraint({"value": left}, operator, {"value": right}),
            {},
        )
        is expected
    )


def test_hard_constraints_behavior_and_inputs_are_unchanged() -> None:
    constraints = [
        _constraint({"var": "x"}, ">=", {"value": 3}),
        _constraint({"var": "x"}, "<", {"value": 3}),
    ]
    variables = {"x": 3}
    original_constraints = copy.deepcopy(constraints)
    original_variables = copy.deepcopy(variables)

    ok, failures = evaluate_hard_constraints(constraints, variables)

    assert not ok
    assert failures == [{"index": 1, "constraint": constraints[1]}]
    assert constraints == original_constraints
    assert variables == original_variables
