from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import sympy
from sympy.parsing.sympy_parser import implicit_multiplication_application, parse_expr, standard_transformations

from core.checkers.expression_equivalence_checker import check_expression_equivalence_answer


COMPONENTS = [
    "src_4570",
    "src_4571",
    "src_4577",
    "src_4578",
    "src_4579",
    "src_4580",
    "src_4583",
    "src_4584",
    "src_4588",
    "src_4589",
    "src_4608",
]


def _skill_component_root() -> Path:
    return next(Path("agent_skills_v3").glob("*DistanceBetweenTwoParallelLines")) / "components"


def _load_component(component_id: str) -> Any:
    path = _skill_component_root() / component_id / "generate.py"
    spec = importlib.util.spec_from_file_location(f"parallel_lines_{component_id}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _parse_expr(text: Any, *, local_dict: dict[str, Any] | None = None) -> Any:
    return parse_expr(
        str(text).replace("^", "**").strip(),
        local_dict=local_dict or {},
        transformations=standard_transformations + (implicit_multiplication_application,),
    )


def _line_coefficients(equation: str, *, local_dict: dict[str, Any] | None = None) -> tuple[Any, Any, Any]:
    lhs, rhs = str(equation).split("=", 1)
    expr = _parse_expr(lhs, local_dict=local_dict) - _parse_expr(rhs, local_dict=local_dict)
    x, y = sympy.symbols("x y")
    return sympy.expand(expr).coeff(x), sympy.expand(expr).coeff(y), sympy.expand(expr).subs({x: 0, y: 0})


def _normalize(a: Any, b: Any, c: Any) -> tuple[Any, Any, Any]:
    gcd_ab = sympy.gcd(int(a), int(b))
    if a < 0 or (a == 0 and b < 0):
        gcd_ab = -gcd_ab
    return sympy.Rational(a, gcd_ab), sympy.Rational(b, gcd_ab), sympy.simplify(c / gcd_ab)


def _distance_between(line_1: str, line_2: str) -> Any:
    a1, b1, c1 = _line_coefficients(line_1)
    a2, b2, c2 = _line_coefficients(line_2)
    na1, nb1, nc1 = _normalize(a1, b1, c1)
    na2, nb2, nc2 = _normalize(a2, b2, c2)
    assert (na1, nb1) == (na2, nb2)
    assert nc1 != nc2
    return sympy.simplify(abs(nc1 - nc2) / sympy.sqrt(na1**2 + nb1**2))


def _assert_no_bare_sqrt(payload: dict[str, Any]) -> None:
    visible = [payload.get("question_text"), payload.get("question"), payload.get("display_answer")]
    visible.extend(choice.get("text") for choice in payload.get("choices") or [])
    assert not any("sqrt(" in str(item) for item in visible)


def _assert_choice_payload_consistent(payload: dict[str, Any]) -> None:
    assert payload["answer"] == payload["correct_answer"] == payload["display_answer"] == payload["semantic_answer"]
    labels = [choice["label"] for choice in payload["choices"]]
    texts = [choice["text"] for choice in payload["choices"]]
    assert payload["answer"] in labels
    assert len(labels) == len(set(labels)) == 4
    assert len(texts) == len(set(texts)) == 4


def _validate_payload(payload: dict[str, Any]) -> None:
    _assert_no_bare_sqrt(payload)
    task_type = payload["problem_type_id"]
    givens = payload["math_core"]["raw_givens"]

    if task_type == "distance_between_parallel_lines":
        expected = _distance_between(givens["line_1"], givens["line_2"])
        assert expected > 0
        assert check_expression_equivalence_answer(payload["correct_answer"], str(expected))
    elif task_type == "solve_parameter_from_parallel_distance":
        k = sympy.symbols("k", real=True)
        a1, b1, c1 = _line_coefficients(givens["line_1"], local_dict={"k": k})
        a2, b2, c2 = _line_coefficients(givens["line_2"], local_dict={"k": k})
        na1, nb1, nc1 = _normalize(a1, b1, c1)
        na2, nb2, nc2 = _normalize(a2, b2, c2)
        assert (na1, nb1) == (na2, nb2)
        distance = _parse_expr(givens["target_distance"])
        answer = _parse_expr(payload["correct_answer"])
        equation_value = sympy.simplify(abs(nc1.subs(k, answer) - nc2) / sympy.sqrt(na1**2 + nb1**2))
        assert sympy.simplify(equation_value - distance) == 0
        condition = str(givens["parameter_condition"])
        bound = _parse_expr(condition.split(">", 1)[1] if ">" in condition else condition.split("<", 1)[1])
        assert (answer > bound) if ">" in condition else (answer < bound)
    elif task_type == "area_using_parallel_distance":
        a, b, c = _line_coefficients(givens["line"])
        x0, y0 = givens["point_a"]
        height = sympy.simplify(abs(a * x0 + b * y0 + c) / sympy.sqrt(a**2 + b**2))
        expected = sympy.simplify(sympy.Rational(givens["segment_length"], 2) * height)
        assert expected > 0
        assert check_expression_equivalence_answer(payload["correct_answer"], str(expected))
    elif task_type == "parallel_lines_distance_single_choice":
        _assert_choice_payload_consistent(payload)
        question = payload["question_text"]
        a = int(givens["a"])
        b = int(givens["b"])
        k = int(givens["k"])
        slope = sympy.Rational(str(givens["slope"]))
        distance_squared = sympy.Rational(str(givens["origin_distance_squared"]))
        solved_a = -slope * b
        assert solved_a.q == 1
        assert int(solved_a) == a
        assert b != 0
        assert k > 0
        assert sympy.simplify(distance_squared * (a * a + b * b) - k * k) == 0
        expected = str(a + k)
        choice = next(choice for choice in payload["choices"] if choice["label"] == payload["correct_answer"])
        assert choice["text"] == expected
        assert "L:" in question
        assert "a>0" not in question
        assert "a=" not in question
        assert "ax+2ay+k=0" not in question


def test_parallel_lines_distance_components_generate_valid_math() -> None:
    for component_id in COMPONENTS:
        module = _load_component(component_id)
        for seed in range(20):
            payload = module.generate(seed=seed, component_id=component_id)
            _validate_payload(payload)
