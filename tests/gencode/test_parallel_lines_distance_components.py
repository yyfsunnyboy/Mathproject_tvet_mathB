from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import sympy
from sympy.parsing.sympy_parser import implicit_multiplication_application, parse_expr, standard_transformations

from core.checkers.expression_equivalence_checker import check_expression_equivalence_answer
from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.checkers.solution_set_checker import check_solution_set_answer


COMPONENTS = [
    "src_4570",
    "src_4571",
    "src_4577",
    "src_4578",
    "src_4579",
    "src_4580",
    "src_4583",
    "src_4588",
    "src_4589",
    "src_4608",
]

MULTIPART_COMPONENTS = {"src_4570", "src_4588"}
LIFE_CONTEXT_COMPONENTS = {"src_4577"}
SOLUTION_SET_COMPONENTS = {"src_4571"}
POSITIVE_K_COMPONENTS = {"src_4580", "src_4589"}
NEGATIVE_K_COMPONENTS = {"src_4579"}


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


def _validate_payload(payload: dict[str, Any], *, component_id: str) -> None:
    _assert_no_bare_sqrt(payload)
    task_type = payload["problem_type_id"]
    givens = payload["math_core"]["raw_givens"]
    contract = payload.get("answer_contract") or {}

    if task_type == "distance_between_parallel_lines":
        if component_id in MULTIPART_COMPONENTS:
            assert payload.get("answer_type") == "multi_part"
            assert str(contract.get("checker") or "") == "multi_part_answer_checker"
            parts = contract.get("parts") or []
            assert len(parts) == 2
            items = givens.get("items") or []
            assert len(items) == 2
            stem = str(payload.get("question_text") or "")
            assert "試求下列各組平行線之間的距離" in stem
            assert "(1)" in stem and "(2)" in stem
            semantic = payload.get("semantic_answer")
            assert isinstance(semantic, dict)
            for item, part in zip(items, parts):
                expected = _distance_between(item["line_1"], item["line_2"])
                assert expected > 0
                assert check_expression_equivalence_answer(part["expected_answer"], str(expected))
            ok = check_multi_part_answer(semantic, semantic, answer_contract=contract)
            assert (ok is True) or (isinstance(ok, dict) and ok.get("is_correct") is True)
            wrong = dict(semantic)
            first_key = next(iter(wrong))
            wrong[first_key] = "0"
            bad = check_multi_part_answer(wrong, semantic, answer_contract=contract)
            assert (bad is False) or (isinstance(bad, dict) and bad.get("is_correct") is False)
        else:
            expected = _distance_between(givens["line_1"], givens["line_2"])
            assert expected > 0
            assert check_expression_equivalence_answer(payload["correct_answer"], str(expected))
            if component_id in LIFE_CONTEXT_COMPONENTS:
                stem = str(payload.get("question_text") or "")
                assert "最短距離" in stem
                assert givens.get("road_a") and givens.get("road_b")
                assert str(givens.get("road_a")) in stem
                assert str(givens.get("road_b")) in stem
                assert givens["line_1"].replace(" ", "") in stem.replace(" ", "") or "L_1" in stem or "L1" in stem
    elif task_type == "solve_parameter_from_parallel_distance":
        k = sympy.symbols("k", real=True)
        a1, b1, c1 = _line_coefficients(givens["line_1"], local_dict={"k": k})
        a2, b2, c2 = _line_coefficients(givens["line_2"], local_dict={"k": k})
        na1, nb1, nc1 = _normalize(a1, b1, c1)
        na2, nb2, nc2 = _normalize(a2, b2, c2)
        assert (na1, nb1) == (na2, nb2)
        distance = _parse_expr(givens["target_distance"])
        condition = str(givens.get("parameter_condition") or "")
        if component_id in SOLUTION_SET_COMPONENTS:
            assert payload.get("answer_type") == "solution_set"
            assert not condition
            assert "且 $" not in str(payload.get("question_text") or "")
            values = givens.get("solution_values") or []
            assert len(values) == 2
            for value in values:
                answer = _parse_expr(value)
                equation_value = sympy.simplify(abs(nc1.subs(k, answer) - nc2) / sympy.sqrt(na1**2 + nb1**2))
                assert sympy.simplify(equation_value - distance) == 0
            assert check_solution_set_answer(payload["correct_answer"], " 或 ".join(values)) is True
        else:
            answer = _parse_expr(payload["correct_answer"])
            equation_value = sympy.simplify(abs(nc1.subs(k, answer) - nc2) / sympy.sqrt(na1**2 + nb1**2))
            assert sympy.simplify(equation_value - distance) == 0
            assert condition
            if component_id in POSITIVE_K_COMPONENTS:
                assert condition.replace(" ", "") == "k>0"
                assert answer > 0
            elif component_id in NEGATIVE_K_COMPONENTS:
                assert condition.replace(" ", "") == "k<0"
                assert answer < 0
            else:
                bound = _parse_expr(condition.split(">", 1)[1] if ">" in condition else condition.split("<", 1)[1])
                assert (answer > bound) if ">" in condition else (answer < bound)
    elif task_type == "area_using_parallel_distance":
        a, b, c = _line_coefficients(givens["line"])
        x0, y0 = givens["point_a"]
        height = sympy.simplify(abs(a * x0 + b * y0 + c) / sympy.sqrt(a**2 + b**2))
        expected = sympy.simplify(sympy.Rational(givens["segment_length"], 2) * height)
        assert expected > 0
        assert check_expression_equivalence_answer(payload["correct_answer"], str(expected))
    else:
        raise AssertionError(f"unexpected parallel-lines task_type: {task_type}")


def test_parallel_lines_distance_components_generate_valid_math() -> None:
    for component_id in COMPONENTS:
        module = _load_component(component_id)
        for seed in range(20):
            payload = module.generate(seed=seed, component_id=component_id)
            _validate_payload(payload, component_id=component_id)


def test_parallel_lines_presentation_variants_are_distinct() -> None:
    skill_root = next(Path("agent_skills_v3").glob("*DistanceBetweenTwoParallelLines"))
    spec = importlib.util.spec_from_file_location("parallel_lines_skill", skill_root / "__init__.py")
    assert spec and spec.loader
    skill = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(skill)

    single = skill.generate(seed=11, component_id="src_4578")
    multipart = skill.generate(seed=11, component_id="src_4570")
    life = skill.generate(seed=11, component_id="src_4577")
    both = skill.generate(seed=11, component_id="src_4571")
    pos = skill.generate(seed=11, component_id="src_4580")
    neg = skill.generate(seed=11, component_id="src_4579")

    assert "試求兩平行線" in str(single.get("question_text") or "")
    assert "試求下列各組平行線之間的距離" in str(multipart.get("question_text") or "")
    assert multipart.get("answer_type") == "multi_part"
    assert "最短距離" in str(life.get("question_text") or "")
    assert both.get("answer_type") == "solution_set"
    assert "k > 0" in str(pos.get("question_text") or "") or "k>0" in str(pos.get("question_text") or "").replace(" ", "")
    assert "k < 0" in str(neg.get("question_text") or "") or "k<0" in str(neg.get("question_text") or "").replace(" ", "")
    # Same seed must not collapse presentation variants into identical stems.
    stems = {
        str(single.get("question_text")),
        str(multipart.get("question_text")),
        str(life.get("question_text")),
        str(both.get("question_text")),
    }
    assert len(stems) == 4
