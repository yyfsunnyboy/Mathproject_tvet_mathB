"""Question payload contracts for algebra.radical_operations.

Every payload is graded by a registered checker; the expected answer always
comes from the domain matrix.  Tasks that ask to 化簡 / 化至最簡 carry the
contract-driven ``simplest_radical`` form; evaluation tasks (求值) only require
mathematical equivalence.
"""

from __future__ import annotations

from typing import Any, Callable

from core.domain.promoted.algebra_multiplication_formulas.multiplication_formulas_adapter import (
    radical_sum_latex,
    rational_latex,
)

from .radical_operations_domain import DOMAIN_KEY, parse_exact_rational


# --- rendering -------------------------------------------------------------------

def _value_latex(value: list[list[Any]]) -> str:
    return radical_sum_latex([[c, m] for c, m in value]) if value else "0"


def _factor_latex(factor: dict[str, Any], *, wrap: bool) -> str:
    body = radical_sum_latex(factor["terms"])
    if len(factor["terms"]) > 1 and (wrap or factor["power"] != 1):
        body = f"\\left({body}\\right)"
    return body if factor["power"] == 1 else f"{body}^{{{factor['power']}}}"


def _product_latex(factors: list[dict[str, Any]], *, wrap: bool) -> str:
    many = len(factors) > 1
    return "".join(_factor_latex(f, wrap=wrap or many) for f in factors)


def term_latex(term: dict[str, Any], *, leading: bool = True) -> tuple[str, bool]:
    """Return (magnitude latex, negative) for one written term."""
    coefficient = parse_exact_rational(term["coefficient"])
    magnitude = abs(coefficient)
    if term["denominator"]:
        body = f"\\frac{{{_product_latex(term['numerator'], wrap=False)}}}{{{_product_latex(term['denominator'], wrap=False)}}}"
    else:
        numerator = term["numerator"]
        body = _product_latex(numerator, wrap=not leading or magnitude != 1)
    if magnitude != 1:
        body = rational_latex(magnitude) + body
    return body, coefficient < 0


def expression_latex(expression: list[dict[str, Any]]) -> str:
    text = ""
    for term in expression:
        body, negative = term_latex(term, leading=not text)
        text += ("-" if negative else ("+" if text else "")) + body
    return text


def nested_root_latex(root: dict[str, Any]) -> str:
    k, q = parse_exact_rational(root["radical"][0]), root["radical"][1]
    inner = rational_latex(root["rational"]) + ("-" if k < 0 else "+")
    inner += ("" if abs(k) == 1 else rational_latex(abs(k))) + f"\\sqrt{{{q}}}"
    return f"\\sqrt{{{inner}}}"


def _nested_inner_latex(root: dict[str, Any]) -> str:
    return nested_root_latex(root)[len("\\sqrt{"):-1]


# --- contracts -------------------------------------------------------------------

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


def _simplest_part(index: int, expected: str, **extra: Any) -> dict[str, Any]:
    return _part(index, expected, "expression_checker", "expression_equivalence", "expression",
                 required_form="simplest_radical", **extra)


def _rational_part(index: int, expected: str, **extra: Any) -> dict[str, Any]:
    return _part(index, expected, "rational_checker", "rational_equivalent", "rational", **extra)


def _payload(matrix, *, question, answer, display_answer, contract, explanation_steps) -> dict[str, Any]:
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


def _multi_part_payload(matrix, *, question, parts, latex_answers, answer_shape, explanation_steps):
    return _payload(
        matrix,
        question=question,
        answer={part["key"]: part["expected_answer"] for part in parts},
        display_answer="　".join(
            f"{part['label']} ${a}$" for part, a in zip(parts, latex_answers)
        ),
        contract=_contract(
            "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer",
            answer_shape=answer_shape, parts=parts,
        ),
        explanation_steps=explanation_steps,
    )


def _listed(intro: str, items: list[str]) -> str:
    return intro + "\n" + "\n".join(f"({i})${item}$。" for i, item in enumerate(items, start=1))


def _single_expression_payload(matrix, *, question, value, explanation_steps, required_form=None, answer_shape):
    extra = {"required_form": required_form} if required_form else {}
    latex = _value_latex(value["value"])
    return _payload(
        matrix,
        question=question,
        answer=value["value_plain"],
        display_answer=f"${latex}$",
        contract=_contract("expression", "short_answer", "expression_checker", "expression_equivalence",
                           answer_shape=answer_shape, **extra),
        explanation_steps=explanation_steps,
    )


def _single_rational_payload(matrix, *, question, value, explanation_steps, answer_shape, unit=""):
    return _payload(
        matrix,
        question=question,
        answer=str(value),
        display_answer=f"${rational_latex(value)}${unit}",
        contract=_contract("rational", "short_answer", "rational_checker", "rational_equivalent", answer_shape=answer_shape),
        explanation_steps=explanation_steps,
    )


# --- operations --------------------------------------------------------------------

def _rationalize_step(term: dict[str, Any], result: dict[str, Any]) -> str | None:
    if result["conjugate"] is None or result["conjugate"] == [["1", 1]]:
        return None
    conjugate = _value_latex(result["conjugate"])
    return (f"${term_latex(term)[0]}$ 的分子、分母同乘 ${conjugate}$，"
            f"分母化為 ${rational_latex(result['norm'])}$，得 ${_value_latex(result['value'])}$")


def _simplify_radical_fraction_expressions(matrix: dict[str, Any]) -> dict[str, Any]:
    expressions, results = matrix["givens"]["expressions"], matrix["answer"]["parts"]
    items = [expression_latex(e) for e in expressions]
    answers = [_value_latex(r["value"]) for r in results]
    steps = []
    for index, (expression, item, result, answer) in enumerate(zip(expressions, items, results, answers), start=1):
        notes = [s for s in (_rationalize_step(t, r) for t, r in zip(expression, result["terms"])) if s]
        prefix = "；".join(notes) + "；" if notes else ""
        steps.append(f"({index}) {prefix}合併同類根式：${item}={answer}$。")
    parts = [_simplest_part(i, r["value_plain"]) for i, r in enumerate(results, start=1)]
    return _multi_part_payload(
        matrix, question=_listed("化簡下列各式：", items), parts=parts, latex_answers=answers,
        answer_shape="simplest_radicals", explanation_steps=steps,
    )


def _denest_step(root: dict[str, Any], part: dict[str, Any]) -> str:
    x, y = rational_latex(part["x"]), rational_latex(part["y"])
    sign = "+" if part["sign"] > 0 else "-"
    return (f"${nested_root_latex(root)}=\\sqrt{{\\left({x}+{y}\\right){sign}2\\sqrt{{{x}\\times {y}}}}}"
            f"=\\sqrt{{{x}}}{sign}\\sqrt{{{y}}}={_value_latex(part['value'])}$")


def _denest_square_roots(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, results = matrix["givens"], matrix["answer"]["parts"]
    roots = givens["roots"]
    if givens.get("context") == "square_area" and len(roots) == 1:
        root, part = roots[0], results[0]
        question = f"已知正方形面積為 ${_nested_inner_latex(root)}$，求正方形的邊長（將其化至最簡）。"
        return _single_expression_payload(
            matrix, question=question, value=part, required_form="simplest_radical",
            answer_shape="denested_square_root",
            explanation_steps=[f"邊長為 ${nested_root_latex(root)}$。", f"{_denest_step(root, part)}。"],
        )
    items = [nested_root_latex(r) for r in roots]
    answers = [_value_latex(p["value"]) for p in results]
    steps = [f"({i}) {_denest_step(r, p)}。" for i, (r, p) in enumerate(zip(roots, results), start=1)]
    parts = [_simplest_part(i, p["value_plain"]) for i, p in enumerate(results, start=1)]
    return _multi_part_payload(
        matrix, question=_listed("化簡下列各式：", items), parts=parts, latex_answers=answers,
        answer_shape="denested_square_roots", explanation_steps=steps,
    )


def _evaluate_integer_fraction_part_expression(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    root, sign = givens["root"], givens["sign"]
    target = f"a{'+' if sign > 0 else '-'}\\frac{{1}}{{b}}"
    question = f"已知 ${nested_root_latex(root)}$ 的整數部分為a，小數部分為b，求 ${target}$ 的值。"
    a = answer["integer_part"]
    steps = [
        f"{_denest_step(root, answer['denested'])}。",
        f"因為 ${a}<{_value_latex(answer['denested']['value'])}<{a + 1}$，所以 $a={a}$，"
        f"$b={_value_latex(answer['fractional_part'])}$。",
        f"分母有理化：$\\frac{{1}}{{b}}={_value_latex(answer['reciprocal'])}$。",
        f"故 ${target}={_value_latex(answer['value'])}$。",
    ]
    return _single_expression_payload(
        matrix, question=question, value=answer, answer_shape="integer_fraction_part_value", explanation_steps=steps,
    )


def _order_radical_numbers(matrix: dict[str, Any]) -> dict[str, Any]:
    numbers, answer = matrix["givens"]["numbers"], matrix["answer"]
    listed = "、".join(f"${n['label']}={term_latex(n['term'])[0]}$" for n in numbers)
    question = f"比較下列各數的大小：\n{listed}。"
    order = answer["order_plain"]
    steps = []
    for row in answer["values"]:
        if row["conjugate"] is not None and row["conjugate"] != [["1", 1]]:
            steps.append(f"分母有理化：${row['label']}={_value_latex(row['value'])}$。")
    steps += [f"${row['label']}^{{2}}={_value_latex(row['square'])}$" for row in answer["values"]]
    steps.append(f"各數皆為正數，比較平方的大小，得 ${order}$。")
    part = {**_part(1, order, "ordered_inequality_checker", "ordered_inequality", "short_answer"), "label": "大小關係"}
    return _payload(
        matrix,
        question=question,
        answer={part["key"]: order},
        display_answer=f"${order}$",
        contract=_contract(
            "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer",
            answer_shape="ordered_radical_numbers", parts=[part],
        ),
        explanation_steps=steps,
    )


_DILATION_PREMISE = (
    "愛因斯坦認為極大的飛行速度會使得飛行物體的時間減慢，並提出：「太空人以光速的 $x$ 倍（$0<x<1$）"
    "進行 $t$ 年的太空旅行（太空人老了t歲）；旅行結束後返回地球，地球上已經過了 "
    "$\\frac{t}{\\sqrt{1-x^{2}}}$ 年（地球上的人老了 $\\frac{t}{\\sqrt{1-x^{2}}}$ 歲）。」"
)


def _dilation_item(relation: dict[str, Any]) -> str:
    find = relation["find"]
    if find == "earth_years":
        return (f"某太空人以光速的 ${rational_latex(relation['speed_ratio'])}$ 倍進行 ${rational_latex(relation['traveler_years'])}$ "
                "年的太空旅行，旅行結束後返回地球，地球上過了__________年。")
    if find == "travel_years_from_age_match":
        return (f"某年，一太空人 ${rational_latex(relation['traveler_age'])}$ 歲，他有位 ${rational_latex(relation['child_age'])}$ "
                f"歲的兒子。此年，該太空人以光速的 ${rational_latex(relation['speed_ratio'])}$ 倍進行t年的太空旅行；"
                "旅行結束後返回地球，太空人發現他跟兒子的年紀竟然一樣。試問：太空人旅行了多少年？")
    return (f"某太空人想進行 ${rational_latex(relation['traveler_years'])}$ 年的太空旅行，並希望旅行結束後返回地球時，"
            f"地球上已經過了 ${rational_latex(relation['earth_years'])}$ 年，試問此次太空旅行的速度應該要達到光速的幾倍？")


def _dilation_step(relation: dict[str, Any], result: dict[str, Any]) -> str:
    find = result["find"]
    if find == "earth_years":
        return (f"$\\frac{{t}}{{\\sqrt{{1-x^{{2}}}}}}=\\frac{{{rational_latex(relation['traveler_years'])}}}"
                f"{{\\sqrt{{1-\\left({rational_latex(relation['speed_ratio'])}\\right)^{{2}}}}}}={rational_latex(result['value'])}$（年）")
    if find == "travel_years_from_age_match":
        gamma = rational_latex(result["gamma"])
        return (f"地球上過了 ${gamma}t$ 年，由 ${rational_latex(relation['traveler_age'])}+t="
                f"{rational_latex(relation['child_age'])}+{gamma}t$ 得 $t={rational_latex(result['value'])}$（年）")
    ratio = parse_exact_rational(relation["traveler_years"]) / parse_exact_rational(relation["earth_years"])
    return (f"由 $\\frac{{{rational_latex(relation['traveler_years'])}}}{{\\sqrt{{1-x^{{2}}}}}}={rational_latex(relation['earth_years'])}$ "
            f"得 $\\sqrt{{1-x^{{2}}}}={rational_latex(ratio)}$，即 $x^{{2}}={rational_latex(result['speed_ratio_squared'])}$，"
            f"又 $x>0$，故 $x={_value_latex(result['value'])}$")


def _evaluate_time_dilation_relations(matrix: dict[str, Any]) -> dict[str, Any]:
    relations, results = matrix["givens"]["relations"], matrix["answer"]["relations"]
    if len(relations) == 1:
        relation, result = relations[0], results[0]
        question = f"{_DILATION_PREMISE}根據上述理論，{_dilation_item(relation)}"
        steps = [f"{_dilation_step(relation, result)}。"]
        if result["kind"] == "radical":
            return _single_expression_payload(matrix, question=question, value=result,
                                              answer_shape="time_dilation_value", explanation_steps=steps)
        return _single_rational_payload(matrix, question=question, value=result["value"],
                                        answer_shape="time_dilation_value", explanation_steps=steps)
    items = [_dilation_item(r) for r in relations]
    question = f"{_DILATION_PREMISE}根據上述理論，試回答下列問題：\n" + "\n".join(
        f"({i}){item}" for i, item in enumerate(items, start=1))
    parts, answers = [], []
    for i, result in enumerate(results, start=1):
        if result["kind"] == "radical":
            parts.append(_part(i, result["value_plain"], "expression_checker", "expression_equivalence", "expression"))
            answers.append(_value_latex(result["value"]))
        else:
            parts.append(_rational_part(i, result["value"]))
            answers.append(rational_latex(result["value"]))
    steps = [f"({i}) {_dilation_step(r, res)}。" for i, (r, res) in enumerate(zip(relations, results), start=1)]
    return _multi_part_payload(matrix, question=question, parts=parts, latex_answers=answers,
                               answer_shape="time_dilation_values", explanation_steps=steps)


def _linear_latex(p: Any, variable: str) -> str:
    return ("" if parse_exact_rational(p) == 1 else rational_latex(p)) + variable


def _optimize_by_am_gm(matrix: dict[str, Any]) -> dict[str, Any]:
    problem, answer = matrix["givens"]["problem"], matrix["answer"]
    kind, context = answer["kind"], problem.get("context")
    x, y, optimum = answer["x"], answer["y"], answer["optimum"]
    if kind == "max_product_linear_sum" and context == "river_fence":
        total = rational_latex(problem["total"])
        question = (f"用圍籬沿著筆直的河岸圍一個矩形菜圃，其中靠河岸一邊不圍，只圍三邊。已知圍籬的總長為 ${total}$ 公尺，"
                    "求此菜圃的最大面積為多少平方公尺？又此時的長、寬分別為多少公尺？")
        steps = [
            f"設垂直河岸的兩邊各為 $x$ 公尺，平行河岸的一邊為 $y$ 公尺，則 $2x+y={total}$，面積為 $xy$。",
            f"由算幾不等式 $\\frac{{2x+y}}{{2}}\\ge \\sqrt{{2xy}}$，得 $xy\\le {rational_latex(optimum)}$。",
            f"等號成立於 $2x=y$，即 $x={rational_latex(x)}$、$y={rational_latex(y)}$。",
        ]
        parts = [
            {**_rational_part(1, optimum), "key": "area", "label": "最大面積", "unit": "平方公尺"},
            {**_rational_part(2, y), "key": "length", "label": "長", "unit": "公尺"},
            {**_rational_part(3, x), "key": "width", "label": "寬", "unit": "公尺"},
        ]
        return _multi_part_payload(matrix, question=question, parts=parts,
                                   latex_answers=[rational_latex(v) for v in (optimum, y, x)],
                                   answer_shape="am_gm_optimum_with_dimensions", explanation_steps=steps)
    if kind == "min_box_surface":
        height, volume = rational_latex(problem["height"]), rational_latex(problem["volume"])
        question = (f"王師傅想為公司設計一個長方體紙盒。已知長方體的高為 ${height}$ 公分，體積為 ${volume}$ 立方公分，"
                    "若想用紙最少，則長方體的底面之長與寬應設計為多少公分？")
        base = rational_latex(parse_exact_rational(problem["volume"]) / parse_exact_rational(problem["height"]))
        steps = [
            f"設底面之長、寬為 $a$、$b$ 公分，則 ${height}ab={volume}$，即 $ab={base}$。",
            f"表面積 $2ab+2\\times {height}\\left(a+b\\right)$，由算幾不等式 $a+b\\ge 2\\sqrt{{ab}}$，等號成立於 $a=b$。",
            f"故 $a=b={rational_latex(x)}$，此時表面積最小為 ${rational_latex(optimum)}$ 平方公分。",
        ]
        parts = [
            {**_rational_part(1, y), "key": "length", "label": "長", "unit": "公分"},
            {**_rational_part(2, x), "key": "width", "label": "寬", "unit": "公分"},
        ]
        return _multi_part_payload(matrix, question=question, parts=parts,
                                   latex_answers=[rational_latex(y), rational_latex(x)],
                                   answer_shape="am_gm_dimensions", explanation_steps=steps)
    if kind == "max_product_linear_sum":
        total = rational_latex(problem["total"])
        half = rational_latex(parse_exact_rational(problem["total"]) / 2)
        question = f"用一條長度為 ${total}$ 公尺的繩子圍成一矩形，求所圍矩形的最大面積。"
        steps = [
            f"設矩形的長、寬為 $a$、$b$ 公尺，則 $2\\left(a+b\\right)={total}$，即 $a+b={half}$。",
            f"由算幾不等式 $\\frac{{a+b}}{{2}}\\ge \\sqrt{{ab}}$，得 $ab\\le {rational_latex(optimum)}$。",
            f"等號成立於 $a=b={rational_latex(x)}$，故最大面積為 ${rational_latex(optimum)}$ 平方公尺。",
        ]
        return _single_rational_payload(matrix, question=question, value=optimum, unit="平方公尺",
                                        answer_shape="am_gm_optimum", explanation_steps=steps)
    p, q, product = problem["p"], problem["q"], problem["product"]
    target = f"{_linear_latex(p, 'a')}+{_linear_latex(q, 'b')}"
    question = f"已知 $a>0$、$b>0$ 且 $ab={rational_latex(product)}$，求 ${target}$ 的最小值。"
    steps = [
        f"由算幾不等式 $\\frac{{{target}}}{{2}}\\ge \\sqrt{{{_linear_latex(parse_exact_rational(p) * parse_exact_rational(q), 'ab')}}}"
        f"=\\sqrt{{{rational_latex(parse_exact_rational(p) * parse_exact_rational(q) * parse_exact_rational(product))}}}$。",
        f"等號成立於 ${_linear_latex(p, 'a')}={_linear_latex(q, 'b')}$，即 $a={rational_latex(x)}$、$b={rational_latex(y)}$，"
        f"最小值為 ${rational_latex(optimum)}$。",
    ]
    return _single_rational_payload(matrix, question=question, value=optimum,
                                    answer_shape="am_gm_optimum", explanation_steps=steps)


def _nearest_integer_from_radical_relation(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    known, rhs = rational_latex(givens["known"]), rational_latex(givens["rhs"])
    sign = "+" if givens["sign"] > 0 else "-"
    question = f"已知a為實數且 $\\sqrt{{a}}{sign}\\sqrt{{{known}}}=\\sqrt{{{rhs}}}$，求最接近a的整數。"
    n = answer["nearest_integer"]
    steps = [
        f"移項得 $\\sqrt{{a}}={_value_latex(answer['sqrt_a'])}$，平方得 $a={_value_latex(answer['a'])}$。",
        f"估算可得 ${n}-\\frac{{1}}{{2}}<a<{n}+\\frac{{1}}{{2}}$，故最接近a的整數為 ${n}$。",
    ]
    return _single_rational_payload(matrix, question=question, value=n,
                                    answer_shape="nearest_integer", explanation_steps=steps)


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "simplify_radical_fraction_expressions": _simplify_radical_fraction_expressions,
    "denest_square_roots": _denest_square_roots,
    "evaluate_integer_fraction_part_expression": _evaluate_integer_fraction_part_expression,
    "order_radical_numbers": _order_radical_numbers,
    "evaluate_time_dilation_relations": _evaluate_time_dilation_relations,
    "optimize_by_am_gm": _optimize_by_am_gm,
    "nearest_integer_from_radical_relation": _nearest_integer_from_radical_relation,
}


def adapt_radical_operations_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_radical_operations_operation:{operation}")
    return builder(matrix)
