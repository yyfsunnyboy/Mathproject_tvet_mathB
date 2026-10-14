# -*- coding: utf-8 -*-
"""B1 3-3 source-text routing: factoring / rational ops. No example_id branches."""
from __future__ import annotations

import ast
from fractions import Fraction
from pathlib import Path

from core.domain.polynomial_domain import build_polynomial_matrix, poly_plain
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.runtime_skill_wrapper import check_answer


def _payload(op: str, src: str, *, seed: int = 7, choice: bool = False) -> dict:
    matrix = build_polynomial_matrix(
        seed=seed,
        domain_operation=op,
        constraints={
            "source_problem_text": src,
            "presentation_mode": "single_choice" if choice else "short_answer",
        },
    )
    return convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice" if choice else "short_answer",
        answer_type="single_choice" if choice else "expression",
        problem_type_id=op,
        domain_operation=op,
        seed=seed,
    )


def test_no_example_id_branch_in_ch3_builders():
    text = Path("core/domain/polynomial_ch3_source_builders.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for cmp in node.comparators:
                if isinstance(cmp, ast.Constant) and isinstance(cmp.value, int) and cmp.value in {4680, 4713, 4715, 4723, 4724}:
                    raise AssertionError("example_id branch")


def test_4680_exam_identity_derives_square_sum():
    src = (
        r"已知多項式$Q\left( x \right)=ax+b$，$f\left( x \right)=\left( 2a-b \right){{x}^{2}}+ax-1$，"
        r"$g\left( x \right)=3{{x}^{2}}+x-1$，且$f\left( x \right)=g\left( x \right)$。"
        r"若分式方程式$\frac{x}{Q\left( x \right)}+\frac{5}{x-2}=\frac{-1}{\left( x-2 \right)Q\left( x \right)}$"
        r"的解為$x=c$，則${{a}^{2}}+{{b}^{2}}+{{c}^{2}}=$？ (A) 4 (B) 10 (C) 18 (D) 27"
    )
    matrix = build_polynomial_matrix(
        seed=11,
        domain_operation="rational_equation_solve",
        constraints={"source_problem_text": src, "presentation_mode": "single_choice"},
    )
    g = matrix.get("givens") or {}
    a, b, c = int(g["a"]), int(g["b"]), int(g["c"])
    excluded = set(g.get("excluded") or [])
    assert c not in excluded
    derived = a * a + b * b + c * c
    assert str(matrix["answer"]["value"]) == str(derived)
    assert derived != 0
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="rational_equation_solve",
        domain_operation="rational_equation_solve",
        seed=11,
    )
    assert payload["answer_type"] == "single_choice"
    assert len(payload.get("choices") or []) == 4
    assert check_answer(payload["answer"], payload["answer"], payload=payload)
    texts = [str(x.get("text") if isinstance(x, dict) else x) for x in payload["choices"]]
    assert all("_1" not in t and "_2" not in t and "_3" not in t for t in texts)


def test_4723_quadratic_choice_both_roots_valid():
    src = (
        r"試求方程式$\frac{x}{1-x}=\frac{1}{x}$之解為 "
        r"(A)$x=\frac{-1\pm \sqrt{5}}{2}$ (B)$x=\frac{-2\pm \sqrt{5}}{2}$ "
        r"(C)$x=\frac{-1\pm \sqrt{3}}{2}$ (D)$x=\frac{-2\pm \sqrt{3}}{2}$。"
    )
    matrix = build_polynomial_matrix(
        seed=5,
        domain_operation="rational_equation_solve",
        constraints={"source_problem_text": src, "presentation_mode": "single_choice"},
    )
    g = matrix.get("givens") or {}
    assert g.get("both_roots_valid") is True
    p = int(g["p"])
    disc = int(g["disc"])
    assert disc == 1 + 4 * p
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="rational_equation_solve",
        domain_operation="rational_equation_solve",
        seed=5,
    )
    assert payload["answer_type"] == "single_choice"
    texts = [str(x.get("text") if isinstance(x, dict) else x) for x in payload["choices"]]
    assert len(set(texts)) == 4
    assert check_answer(payload["answer"], payload["answer"], payload=payload)


def test_4724_excludes_denominator_root():
    src = (
        r"試求方程式$\frac{3}{\left( x-2 \right)\left( x+1 \right)}+\frac{x+2}{x+1}=\frac{2}{x-2}$之解為 "
        r"(A) $x=1$ (B) $x=2$ (C) $x=3$ (D) $x=-2$。"
    )
    matrix = build_polynomial_matrix(
        seed=9,
        domain_operation="rational_equation_solve",
        constraints={"source_problem_text": src, "presentation_mode": "single_choice"},
    )
    g = matrix.get("givens") or {}
    sol = str(g.get("solution"))
    excluded = {str(x) for x in (g.get("excluded") or [])}
    assert sol not in excluded
    assert "x=-1" not in str(matrix["answer"]["value"])
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="rational_equation_solve",
        domain_operation="rational_equation_solve",
        seed=9,
    )
    assert payload["answer_type"] == "single_choice"
    assert check_answer(payload["answer"], payload["answer"], payload=payload)
    labels = [str(x.get("label") if isinstance(x, dict) else "") for x in payload["choices"]]
    for lab in labels:
        if lab != str(payload["answer"]):
            assert not check_answer(lab, payload["answer"], payload=payload)


def test_simple_rational_eq_is_not_fake_multipart():
    src = r"解分式方程式$\frac{2x+1}{x-2}=3$。"
    matrix = build_polynomial_matrix(
        seed=3,
        domain_operation="rational_equation_solve",
        constraints={"source_problem_text": src},
    )
    parts = (matrix.get("answer") or {}).get("parts") or {}
    assert len(parts) == 1
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="expression",
        problem_type_id="rational_equation_solve",
        domain_operation="rational_equation_solve",
        seed=3,
    )
    assert payload["answer_type"] != "multi_part"
    assert check_answer(payload["answer"], payload["answer"], payload=payload)


def test_factoring_multi_part_from_numbered_source():
    src = r"因式分解下列多項式：(1)${{x}^{3}}+{{x}^{2}}+x+1$(2)$27{{x}^{3}}-9{{x}^{2}}+3x-1$"
    matrix = build_polynomial_matrix(
        seed=8,
        domain_operation="polynomial_factoring",
        constraints={"source_problem_text": src},
    )
    parts = (matrix.get("answer") or {}).get("parts") or {}
    assert len(parts) == 2
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="multi_part",
        problem_type_id="polynomial_factoring",
        domain_operation="polynomial_factoring",
        seed=8,
    )
    assert payload["answer_type"] == "multi_part"
    assert check_answer(payload["answer"], payload["answer"], payload=payload)
    wrong = {k: "___WRONG___" for k in payload["answer"]}
    assert not check_answer(wrong, payload["answer"], payload=payload)


def test_rational_multiply_from_source():
    src = r"化簡$\frac{{{x}^{2}}-4}{{{x}^{2}}-3x+2}\times \frac{x-1}{x+2}$。"
    payload = _payload("rational_expression_arithmetic", src, seed=4)
    assert payload.get("answer") is not None
    assert payload["answer_type"] != "multi_part"
    assert check_answer(payload["answer"], payload["answer"], payload=payload)


def test_4695_diff_squares_two_parts_algebraic_equivalent():
    src = (
        r"利用乘法公式因式分解下列各式："
        r"(1)${{x}^{2}}-4$ (2)${{\left( a+b \right)}^{2}}-25$。"
    )
    matrix = build_polynomial_matrix(
        seed=12,
        domain_operation="polynomial_factoring",
        constraints={"source_problem_text": src},
    )
    parts = (matrix.get("answer") or {}).get("parts") or {}
    assert set(parts) == {"part_1", "part_2"}
    g = matrix.get("givens") or {}
    k, m = int(g["k"]), int(g["m"])
    assert parts["part_1"] == f"(x-{k})(x+{k})"
    assert parts["part_2"] == f"(a+b-{m})(a+b+{m})"
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="short_answer",
        answer_type="multi_part",
        problem_type_id="polynomial_factoring",
        domain_operation="polynomial_factoring",
        seed=12,
    )
    assert payload["answer_type"] == "multi_part"
    assert isinstance(payload["answer"], dict)
    assert len(payload["answer"]) == 2
    assert check_answer(payload["answer"], payload["answer"], payload=payload)
    swapped = {
        "part_1": f"(x+{k})(x-{k})",
        "part_2": f"(a+b+{m})(a+b-{m})",
    }
    assert check_answer(swapped, payload["answer"], payload=payload)
    one_wrong = dict(payload["answer"])
    one_wrong["part_2"] = "(a+b-1)(a+b-1)"
    assert not check_answer(one_wrong, payload["answer"], payload=payload)


def test_rect_diff_squares_perimeter_choice():
    src = (
        r"已知一長方形的面積為$9{{x}^{2}}+6x+1-{{y}^{2}}$平方單位，"
        r"若其長、寬均為x、y的一次式且x、y項的係數均為整數，"
        r"則此長方形的周長為？ (A) $6x+4$ (B) $6x-4$ (C) $12x-4$ (D) $12x+4$"
    )
    matrix = build_polynomial_matrix(
        seed=16,
        domain_operation="polynomial_factoring",
        constraints={"source_problem_text": src, "presentation_mode": "single_choice"},
    )
    g = matrix.get("givens") or {}
    k, m = int(g["k"]), int(g["m"])
    derived = poly_plain({1: Fraction(4 * k), 0: Fraction(4 * m)})
    assert str(g["perimeter"]) == derived
    assert str(matrix["answer"]["value"]) == derived
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="polynomial_factoring",
        domain_operation="polynomial_factoring",
        seed=16,
    )
    assert payload["answer_type"] == "single_choice"
    texts = [str(x.get("text") if isinstance(x, dict) else x) for x in payload["choices"]]
    assert len(texts) == 4
    assert len(set(texts)) == 4
    assert all("_1" not in t and "_2" not in t and "_3" not in t for t in texts)
    assert check_answer(payload["answer"], payload["answer"], payload=payload)
    for item in payload["choices"]:
        lab = str(item.get("label") if isinstance(item, dict) else "")
        if lab != str(payload["answer"]):
            assert not check_answer(lab, payload["answer"], payload=payload)


def test_which_factor_substitution_choice():
    src = (
        r"下列何者為多項式${{\left( {{x}^{2}}-2x \right)}^{2}}-8\left( {{x}^{2}}-2x \right)+15$之因式？"
        r" (A) $x+3$ (B) $x-3$ (C) $x+2$ (D) $x-2$"
    )
    matrix = build_polynomial_matrix(
        seed=18,
        domain_operation="polynomial_factoring",
        constraints={"source_problem_text": src, "presentation_mode": "single_choice"},
    )
    g = matrix.get("givens") or {}
    r = int(g["correct_root"])
    s = int(g["pair_root"])
    a = int(g["u_shift"])
    p = int(g["p"])
    q = int(g["q"])
    assert a == r + s
    assert p == -r * s

    def _eval(x: int) -> int:
        u = x * x - a * x
        return (u - p) * (u - q)

    assert _eval(r) == 0
    assert _eval(s) == 0
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="polynomial_factoring",
        domain_operation="polynomial_factoring",
        seed=18,
    )
    assert payload["answer_type"] == "single_choice"
    texts = [str(x.get("text") if isinstance(x, dict) else x).replace(" ", "") for x in payload["choices"]]
    assert len(texts) == 4
    assert len(set(texts)) == 4
    assert all("_1" not in t and "_2" not in t and "_3" not in t for t in texts)
    assert check_answer(payload["answer"], payload["answer"], payload=payload)
    for item in payload["choices"]:
        lab = str(item.get("label") if isinstance(item, dict) else "")
        if lab != str(payload["answer"]):
            assert not check_answer(lab, payload["answer"], payload=payload)
