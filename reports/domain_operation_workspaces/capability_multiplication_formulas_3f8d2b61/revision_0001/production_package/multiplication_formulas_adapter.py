"""Question payload contracts for algebra.multiplication_formulas.

Every payload is graded by a checker registered in ``CHECKER_CAPABILITIES``; the
expected answer always comes from the domain matrix.  Algebraic answers use
mathematical equivalence plus the contract-driven required form the task asks
for (expanded / fully factorized / simplest radical).
"""

from __future__ import annotations

from typing import Any, Callable

from .multiplication_formulas_domain import (
    DOMAIN_KEY,
    canonical_rational,
    ordered_terms,
    parse_exact_rational,
    parse_polynomial,
    polynomial_plain,
)


def rational_latex(value: Any) -> str:
    exact = parse_exact_rational(value)
    if exact.denominator == 1:
        return str(exact.numerator)
    body = f"\\frac{{{abs(exact.numerator)}}}{{{exact.denominator}}}"
    return f"-{body}" if exact < 0 else body


def _monomial_latex(key: tuple[tuple[str, int], ...]) -> str:
    return "".join(v if e == 1 else f"{v}^{{{e}}}" for v, e in key)


def polynomial_latex(terms: list[list[Any]]) -> str:
    """Textbook rendering, e.g. ``\\frac{a^{2}}{4}+\\frac{ab}{6}-2b``."""
    poly = parse_polynomial(terms)
    text = ""
    for coefficient, key in ordered_terms(poly):
        magnitude, mono = abs(coefficient), _monomial_latex(key)
        if not mono:
            body = rational_latex(magnitude)
        elif magnitude.denominator != 1:
            numerator = "" if magnitude.numerator == 1 else str(magnitude.numerator)
            body = f"\\frac{{{numerator}{mono}}}{{{magnitude.denominator}}}"
        else:
            body = ("" if magnitude == 1 else str(magnitude.numerator)) + mono
        text += ("-" if coefficient < 0 else ("+" if text else "")) + body
    return text or "0"


def _polynomial_plain(terms: list[list[Any]]) -> str:
    return polynomial_plain(parse_polynomial(terms))


def _factor_latex(terms: list[list[Any]], power: int, *, wrap: bool) -> str:
    body = polynomial_latex(terms)
    if len(terms) > 1 and (wrap or power != 1):
        body = f"\\left({body}\\right)"
    return body if power == 1 else f"{body}^{{{power}}}"


def expression_latex(expression: list[dict[str, Any]]) -> str:
    text = ""
    for product in expression:
        coefficient = parse_exact_rational(product["coefficient"])
        factors = product["factors"]
        body = "".join(_factor_latex(terms, power, wrap=len(factors) > 1 or coefficient != 1) for terms, power in factors)
        magnitude = abs(coefficient)
        if magnitude != 1:
            body = rational_latex(magnitude) + body
        text += ("-" if coefficient < 0 else ("+" if text else "")) + body
    return text


def factored_plain(factors: list[list[Any]]) -> str:
    out = ""
    for terms, power in factors:
        body = _polynomial_plain(terms)
        if len(terms) > 1:
            body = f"({body})"
        out += body if power == 1 else f"{body}^{power}"
    return out


def factored_latex(factors: list[list[Any]]) -> str:
    return "".join(_factor_latex(terms, power, wrap=True) for terms, power in factors)


def _radicand_latex(radicand: Any) -> str:
    exact = parse_exact_rational(radicand)
    return f"\\sqrt{{{rational_latex(exact)}}}"


def radical_term_latex(coefficient: Any, radicand: Any) -> tuple[str, bool]:
    c, r = parse_exact_rational(coefficient), parse_exact_rational(radicand)
    magnitude = abs(c)
    if r == 1:
        return rational_latex(magnitude), c < 0
    root = _radicand_latex(r)
    if magnitude.denominator != 1:
        numerator = "" if magnitude.numerator == 1 else str(magnitude.numerator)
        return f"\\frac{{{numerator}{root}}}{{{magnitude.denominator}}}", c < 0
    return ("" if magnitude == 1 else str(magnitude.numerator)) + root, c < 0


def radical_sum_latex(terms: list[list[Any]]) -> str:
    text = ""
    for coefficient, radicand in terms:
        body, negative = radical_term_latex(coefficient, radicand)
        text += ("-" if negative else ("+" if text else "")) + body
    return text or "0"


def radical_expression_latex(expression: list[dict[str, Any]]) -> str:
    text = ""
    for product in expression:
        coefficient = parse_exact_rational(product["coefficient"])
        factors = product["factors"]
        wrap = len(factors) > 1 or coefficient != 1
        body = "".join(
            f"\\left({radical_sum_latex(f)}\\right)" if wrap and len(f) > 1 else radical_sum_latex(f) for f in factors
        )
        magnitude = abs(coefficient)
        if magnitude != 1:
            body = rational_latex(magnitude) + body
        text += ("-" if coefficient < 0 else ("+" if text else "")) + body
    return text


def _reciprocal_latex(power: int, sign: int) -> str:
    x = "x" if power == 1 else f"x^{{{power}}}"
    return f"{x}{'+' if sign == 1 else '-'}\\frac{{1}}{{{x}}}"


def _radical_number_latex(rational: Any, radical: Any, radicand: int) -> str:
    return radical_sum_latex([[t, r] for t, r in ((rational, 1), (radical, radicand)) if parse_exact_rational(t) != 0])


def _contract(answer_type: str, presentation_mode: str, checker: str, equivalence: str, **extra: Any) -> dict[str, Any]:
    return {
        "presentation_mode": presentation_mode,
        "answer_type": answer_type,
        "checker": checker,
        "checker_key": checker,
        "answer_equivalence": equivalence,
        "equivalence": equivalence,
        "equivalence_type": equivalence,
        **extra,
    }


def _part(index: int, expected: str, checker: str, equivalence: str, answer_type: str, **extra: Any) -> dict[str, Any]:
    return {
        "key": f"part_{index}",
        "label": f"({index})",
        "checker": checker,
        "checker_key": checker,
        "equivalence_type": equivalence,
        "answer_type": answer_type,
        "expected_answer": expected,
        **extra,
    }


def _payload(
    matrix: dict[str, Any],
    *,
    question: str,
    answer: Any,
    display_answer: str,
    contract: dict[str, Any],
    explanation_steps: list[str],
) -> dict[str, Any]:
    operation = matrix["domain_operation"]
    return {
        "question_text": question,
        "question": question,
        "answer": answer,
        "correct_answer": answer,
        "display_answer": display_answer,
        "semantic_answer": matrix["answer"],
        "answer_type": contract["answer_type"],
        "presentation_mode": contract["presentation_mode"],
        "problem_type_id": operation,
        "domain_operation": operation,
        "fixed_domain_key": DOMAIN_KEY,
        "answer_contract": {**contract, "semantic_answer": matrix["answer"]},
        "explanation_steps": explanation_steps,
        "choices": [],
        "options": [],
        "math_core": {
            "givens": matrix["givens"],
            "target": matrix["answer"],
            "validation_facts": matrix["validation_facts"],
        },
    }


def _multi_part_payload(matrix, *, intro, items, parts, latex_answers, answer_shape, explanation_steps):
    listed = "\n".join(f"({i})${item}$。" for i, item in enumerate(items, start=1))
    return _payload(
        matrix,
        question=f"{intro}\n{listed}",
        answer={part["key"]: part["expected_answer"] for part in parts},
        display_answer="　".join(f"({i}) ${a}$" for i, a in enumerate(latex_answers, start=1)),
        contract=_contract(
            "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer",
            answer_shape=answer_shape, parts=parts,
        ),
        explanation_steps=explanation_steps,
    )


def _expand_polynomial_expressions(matrix: dict[str, Any]) -> dict[str, Any]:
    expressions, results = matrix["givens"]["expressions"], matrix["answer"]["parts"]
    items = [expression_latex(e) for e in expressions]
    answers = [polynomial_latex(r["expanded"]) for r in results]
    steps = []
    for index, (item, result, answer) in enumerate(zip(items, results, answers), start=1):
        pieces = result["product_expansions"]
        middle = "+".join(f"\\left({polynomial_latex(p)}\\right)" for p in pieces) if len(pieces) > 1 else ""
        chain = f"{item}=" + (f"{middle}=" if middle else "") + answer
        steps.append(f"({index}) ${chain}$。")
    parts = [
        _part(i, r["expanded_plain"], "expression_checker", "algebraic_equivalent", "expression", required_form="expanded")
        for i, r in enumerate(results, start=1)
    ]
    return _multi_part_payload(
        matrix, intro="利用乘法公式，展開下列各式：", items=items, parts=parts, latex_answers=answers,
        answer_shape="expanded_polynomials", explanation_steps=steps,
    )


_CUBE_FORMULA_TEXT = {
    "sum_of_cubes": "立方和公式",
    "difference_of_cubes": "立方差公式",
    "cube_of_sum": "和的立方公式",
    "cube_of_difference": "差的立方公式",
}


def _factor_by_cube_formulas(matrix: dict[str, Any]) -> dict[str, Any]:
    polynomials, results = matrix["givens"]["polynomials"], matrix["answer"]["parts"]
    items = [polynomial_latex(p) for p in polynomials]
    answers = [factored_latex(r["factors"]) for r in results]
    steps = []
    for index, (item, result, answer) in enumerate(zip(items, results, answers), start=1):
        steps.append(
            f"({index}) 令 $A={polynomial_latex(result['a_term'])}$、$B={polynomial_latex(result['b_term'])}$，"
            f"利用{_CUBE_FORMULA_TEXT[result['formula']]}：${item}={answer}$。"
        )
    parts = [
        _part(i, factored_plain(r["factors"]), "expression_checker", "factorized_form", "expression",
              required_form="fully_factorized")
        for i, r in enumerate(results, start=1)
    ]
    return _multi_part_payload(
        matrix, intro="利用乘法公式，因式分解下列各式：", items=items, parts=parts, latex_answers=answers,
        answer_shape="factored_polynomials", explanation_steps=steps,
    )


def _evaluate_reciprocal_power_expressions(matrix: dict[str, Any]) -> dict[str, Any]:
    base, values = matrix["answer"]["base"], matrix["answer"]["values"]
    if base["kind"] == "relation":
        known = f"{_reciprocal_latex(1, base['sign'])}={rational_latex(base['value'])}"
    else:
        known = f"x={_radical_number_latex(base['rational'], base['radical'], base['radicand'])}"
    items = [_reciprocal_latex(v["power"], v["sign"]) for v in values]
    answers, parts = [], []
    for index, v in enumerate(values, start=1):
        value = v["value"]
        if parse_exact_rational(value["radical"]) == 0:
            answers.append(rational_latex(value["rational"]))
            parts.append(_part(index, value["rational"], "rational_checker", "rational_equivalent", "rational"))
        else:
            latex = _radical_number_latex(value["rational"], value["radical"], base["radicand"])
            answers.append(latex)
            parts.append(_part(index, latex, "expression_checker", "expression_equivalence", "expression",
                               required_form="simplest_radical"))
    steps, known_sum = [], None
    if base["kind"] == "radical":
        norm = parse_exact_rational(matrix["answer"]["norm"])
        conjugate = _radical_number_latex(
            canonical_rational(parse_exact_rational(base["rational"]) / norm),
            canonical_rational(-parse_exact_rational(base["radical"]) / norm),
            base["radicand"],
        )
        steps.append(f"由乘法公式（平方差）有理化：$\\frac{{1}}{{x}}={conjugate}$。")
        if norm == 1:
            known_sum = (1, rational_latex(2 * parse_exact_rational(base["rational"])))
    else:
        known_sum = (base["sign"], rational_latex(base["value"]))
    for i, (v, item, answer) in enumerate(zip(values, items, answers), start=1):
        chain = f"{item}"
        if known_sum is not None:
            sigma, s = known_sum
            grouped = f"\\left({_reciprocal_latex(1, sigma)}\\right)"
            if v["power"] == 1 and v["sign"] == sigma:
                chain += f"=\\left({known[2:]}\\right)+\\left({conjugate}\\right)" if base["kind"] == "radical" else ""
            elif v["power"] == 2 and v["sign"] == 1:
                chain += f"={grouped}^{{2}}{'-' if sigma == 1 else '+'}2=\\left({s}\\right)^{{2}}{'-' if sigma == 1 else '+'}2"
            elif v["power"] == 3 and v["sign"] == sigma:
                chain += (f"={grouped}^{{3}}{'-' if sigma == 1 else '+'}3{grouped}"
                          f"=\\left({s}\\right)^{{3}}{'-' if sigma == 1 else '+'}3\\times\\left({s}\\right)")
        steps.append(f"({i}) ${chain}={answer}$。")
    return _multi_part_payload(
        matrix, intro=f"已知 ${known}$，求下列各式的值：", items=items, parts=parts, latex_answers=answers,
        answer_shape="reciprocal_power_values", explanation_steps=steps,
    )


def _radical_value_latex(value: list[list[Any]]) -> str:
    return radical_sum_latex([[c, m] for c, m in value]) if value else "0"


def _simplify_radical_expressions(matrix: dict[str, Any]) -> dict[str, Any]:
    expressions, results = matrix["givens"]["expressions"], matrix["answer"]["parts"]
    items = [radical_expression_latex(e) for e in expressions]
    answers = [_radical_value_latex(r["value"]) for r in results]
    steps = []
    for index, (expression, item, result, answer) in enumerate(zip(expressions, items, results, answers), start=1):
        simplified = [
            {"coefficient": product["coefficient"], "factors": factors}
            for product, factors in zip(expression, result["simplified_factors"])
        ]
        middle = radical_expression_latex(simplified)
        chain = item + (f"={middle}" if middle not in (item, answer) else "") + f"={answer}"
        steps.append(f"({index}) ${chain}$。")
    parts = [
        _part(i, r["value_plain"], "expression_checker", "expression_equivalence", "expression",
              required_form="simplest_radical")
        for i, r in enumerate(results, start=1)
    ]
    return _multi_part_payload(
        matrix, intro="化簡下列各式：", items=items, parts=parts, latex_answers=answers,
        answer_shape="simplest_radicals", explanation_steps=steps,
    )


def _solve_rational_unknowns_from_squared_radical_identity(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    m = givens["radicand"]
    root = f"\\sqrt{{{m}}}"
    q, r = parse_exact_rational(givens["coefficient"]), parse_exact_rational(givens["rhs_radical"])
    left, right = _radical_number_latex(0, q, m), _radical_number_latex(0, r, m)
    lhs = f"\\left(a{'' if q < 0 else '+'}{left}\\right)^{{2}}"
    rhs = f"b{'' if r < 0 else '+'}{right}"
    question = f"已知有理數 a, b 滿足 ${lhs}={rhs}$，求 a, b 的值。"
    values = answer["values"]
    two_q = parse_exact_rational(answer["radical_part_equation"]["coefficient_of_a"])
    parts = [
        {**_part(i, values[name], "rational_checker", "rational_equivalent", "rational"), "key": name, "label": name,
         "display_label": f"{name} ="}
        for i, name in enumerate(answer["unknowns"], start=1)
    ]
    steps = [
        f"展開左式：${lhs}=a^{{2}}+{rational_latex(answer['rational_part_constant'])}"
        f"{'+' if two_q > 0 else '-'}{rational_latex(abs(two_q))}a{root}$。",
        f"因為 a, b 是有理數而 ${root}$ 是無理數，比較兩邊：${rational_latex(two_q)}a={rational_latex(r)}$，"
        f"$a^{{2}}+{rational_latex(answer['rational_part_constant'])}=b$。",
        f"解得 $a={rational_latex(values['a'])}$，$b={rational_latex(values['b'])}$。",
    ]
    return _payload(
        matrix,
        question=question,
        answer={name: values[name] for name in answer["unknowns"]},
        display_answer="，".join(f"${n}={rational_latex(values[n])}$" for n in answer["unknowns"]),
        contract=_contract(
            "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer",
            answer_shape="rational_unknown_values", parts=parts,
        ),
        explanation_steps=steps,
    )


def _evaluate_product_under_power_relation(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    variable, power = givens["variable"], givens["power"]
    relation = f"{variable}^{{{power}}}={rational_latex(givens['value'])}"
    item = expression_latex(givens["expression"])
    expanded = polynomial_latex(answer["expanded"])
    value = answer["value"]
    return _payload(
        matrix,
        question=f"已知 ${relation}$，求 ${item}$ 的值。",
        answer=value,
        display_answer=f"${rational_latex(value)}$",
        contract=_contract("rational", "short_answer", "rational_checker", "rational_equivalent",
                           answer_shape="relation_evaluated_value"),
        explanation_steps=[
            f"利用乘法公式展開：${item}={expanded}$。",
            f"以 ${relation}$ 代入，得 ${rational_latex(value)}$。",
        ],
    )


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "expand_polynomial_expressions": _expand_polynomial_expressions,
    "factor_by_cube_formulas": _factor_by_cube_formulas,
    "evaluate_reciprocal_power_expressions": _evaluate_reciprocal_power_expressions,
    "simplify_radical_expressions": _simplify_radical_expressions,
    "solve_rational_unknowns_from_squared_radical_identity": _solve_rational_unknowns_from_squared_radical_identity,
    "evaluate_product_under_power_relation": _evaluate_product_under_power_relation,
}


def adapt_multiplication_formulas_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_multiplication_formulas_operation:{operation}")
    return builder(matrix)
