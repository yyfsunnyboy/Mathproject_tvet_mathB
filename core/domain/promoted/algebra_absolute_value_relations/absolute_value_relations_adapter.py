"""Question payload contracts for algebra.absolute_value_relations.

Every payload is graded by a registered checker and every expected answer comes
from the domain matrix.  Number answers use exact rational equivalence, equation
solution sets use the unordered solution-set checker with exact rational members,
inequality solution sets use the exact real-set checker, and ○/× or option
questions use the choice-label checker.
"""

from __future__ import annotations

from typing import Any, Callable

from core.domain.promoted.algebra_multiplication_formulas.multiplication_formulas_adapter import rational_latex

from .absolute_value_relations_domain import (
    DOMAIN_KEY,
    NEG_INF,
    POS_INF,
    canonical_rational,
    parse_exact_rational,
    parse_intervals,
)

_OP_LATEX = {"=": "=", "<": "<", "<=": "\\le ", ">": ">", ">=": "\\ge "}
_COUNT_WORDS = {1: "一", 2: "兩", 3: "三", 4: "四"}
TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})


# --- rendering -------------------------------------------------------------------

def number_text(value: Any, *, decimal: bool = False) -> str:
    """LaTeX for a rational; terminating values may be written as decimals."""
    exact = parse_exact_rational(value)
    if exact.denominator == 1:
        return str(exact.numerator)
    if decimal:
        for places in range(1, 7):
            scaled = exact * 10 ** places
            if scaled.denominator == 1:
                digits = str(abs(scaled.numerator)).rjust(places + 1, "0")
                return f"{'-' if exact < 0 else ''}{digits[:-places]}.{digits[-places:]}"
    return rational_latex(exact)


def _paren(value: Any) -> str:
    text = number_text(value)
    return f"\\left({text}\\right)" if parse_exact_rational(value) < 0 else text


def _append(text: str, negative: bool, body: str) -> str:
    return text + ("-" if negative else ("+" if text else "")) + body


def _monomial(coefficient: Any, degree: int, variable: str) -> tuple[bool, str]:
    if isinstance(coefficient, dict):
        return coefficient["sign"] < 0, coefficient["param"]
    c = parse_exact_rational(coefficient)
    magnitude = abs(c)
    if degree == 0:
        return c < 0, rational_latex(magnitude)
    return c < 0, variable if magnitude == 1 else rational_latex(magnitude) + variable


def form_latex(form: list[list[Any]], variable: str = "x", text: str = "") -> str:
    for coefficient, degree in form:
        negative, body = _monomial(coefficient, degree, variable)
        text = _append(text, negative, body)
    return text


def side_latex(side: list[dict[str, Any]]) -> str:
    text = ""
    for term in side:
        if "abs" in term:
            k = parse_exact_rational(term["coef"])
            body = ("" if abs(k) == 1 else rational_latex(abs(k))) + f"\\left|{form_latex(term['abs'])}\\right|"
            text = _append(text, k < 0, body)
        else:
            text = form_latex(term["poly"], text=text)
    return text


def relation_latex(relation: dict[str, Any]) -> str:
    return f"{side_latex(relation['lhs'])}{_OP_LATEX[relation['op']]}{side_latex(relation['rhs'])}"


def system_text(system: dict[str, Any]) -> str:
    first = system["relations"][0]
    if system["joiner"] == "chain":
        second = system["relations"][1]
        return (f"${side_latex(first['lhs'])}{_OP_LATEX[first['op']]}{side_latex(first['rhs'])}"
                f"{_OP_LATEX[second['op']]}{side_latex(second['rhs'])}$")
    return " 且 ".join(f"${relation_latex(r)}$" for r in system["relations"])


def _bound_latex(value: Any) -> str:
    if value == NEG_INF:
        return "-\\infty"
    if value == POS_INF:
        return "\\infty"
    return rational_latex(value)


def _bound_plain(value: Any) -> str:
    if value == NEG_INF:
        return "-∞"
    if value == POS_INF:
        return "∞"
    return canonical_rational(value)


def intervals_latex(raw: list[list[Any]]) -> str:
    if not raw:
        return "\\varnothing"
    return "\\cup ".join(
        f"{'[' if lc else '('}{_bound_latex(lo)},{_bound_latex(hi)}{']' if hc else ')'}"
        for lo, hi, lc, hc in parse_intervals(raw)
    )


def intervals_plain(raw: list[list[Any]]) -> str:
    if not raw:
        return "無解"
    return "∪".join(
        f"{'[' if lc else '('}{_bound_plain(lo)},{_bound_plain(hi)}{']' if hc else ')'}"
        for lo, hi, lc, hc in parse_intervals(raw)
    )


def inequality_text(raw: list[list[Any]], variable: str = "x", *, decimal: bool = False) -> str:
    if not raw:
        return "無解"
    le, lt = "\\le ", "<"
    pieces = []
    for lo, hi, lc, hc in parse_intervals(raw):
        if lo == hi:
            pieces.append(f"{variable}={number_text(lo, decimal=decimal)}")
        elif lo == NEG_INF and hi == POS_INF:
            pieces.append(f"{variable}\\in\\mathbb{{R}}")
        elif lo == NEG_INF:
            pieces.append(f"{variable}{le if hc else lt}{number_text(hi, decimal=decimal)}")
        elif hi == POS_INF:
            pieces.append(f"{variable}{'\\ge ' if lc else '>'}{number_text(lo, decimal=decimal)}")
        else:
            pieces.append(f"{number_text(lo, decimal=decimal)}{le if lc else lt}{variable}"
                          f"{le if hc else lt}{number_text(hi, decimal=decimal)}")
    return " 或 ".join(f"${p}$" for p in pieces)


def weighted_latex(weights: list[int]) -> str:
    p, q = weights
    numerator = ("a" if p == 1 else f"{p}a") + "+" + ("b" if q == 1 else f"{q}b")
    return f"\\frac{{{numerator}}}{{{p + q}}}"


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


_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_SOLUTION_SET = ("solution_set_checker", "unordered_solution_set", "short_answer")
_INTERVAL_SET = ("inequality_solution_checker", "interval_equivalence", "inequality_solution")


def _payload(matrix, *, question, answer, display_answer, contract, explanation_steps, choices=()) -> dict[str, Any]:
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
        "choices": [dict(c) for c in choices],
        "options": [dict(c) for c in choices],
        "math_core": {
            "givens": matrix["givens"],
            "target": matrix["answer"],
            "validation_facts": matrix["validation_facts"],
        },
    }


def _parts_payload(matrix, *, question, parts, display_answer, explanation_steps, shape) -> dict[str, Any]:
    return _payload(
        matrix,
        question=question,
        answer={part["key"]: part["expected_answer"] for part in parts},
        display_answer=display_answer,
        contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer",
                           answer_shape=shape, parts=parts),
        explanation_steps=explanation_steps,
    )


def _single_payload(matrix, *, question, part, display_answer, explanation_steps, shape) -> dict[str, Any]:
    extra = {k: v for k, v in part.items() if k not in ("key", "label", "checker", "checker_key", "equivalence_type",
                                                       "answer_type", "expected_answer")}
    return _payload(
        matrix,
        question=question,
        answer=part["expected_answer"],
        display_answer=display_answer,
        contract=_contract(part["answer_type"], "short_answer", part["checker"], part["equivalence_type"],
                           answer_shape=shape, **extra),
        explanation_steps=explanation_steps,
    )


def _choice_payload(matrix, *, question, choices, answer, display_answer, explanation_steps) -> dict[str, Any]:
    return _payload(
        matrix,
        question=question,
        answer=answer,
        display_answer=display_answer,
        contract=_contract("single_choice", "single_choice", "choice_label_checker", "choice_label",
                           answer_shape="single_choice", choices=[dict(c) for c in choices]),
        explanation_steps=explanation_steps,
        choices=choices,
    )


def _numbered(items: list[str]) -> str:
    return "\n".join(f"({i}) {text}" for i, text in enumerate(items, start=1))


# --- payload builders ------------------------------------------------------------

def _division_points(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    a, b = givens["points"]["A"], givens["points"]["B"]
    if givens["intro"] == "points_first":
        intro = f"設數線上兩點 $A({number_text(a)})$、$B({number_text(b)})$。"
    else:
        intro = f"設 $A({number_text(a)})$、$B({number_text(b)})$ 為數線上兩點。"
    asks, parts, shown, steps = [], [], [], []
    for index, (part, result) in enumerate(zip(givens["parts"], answer["parts"]), start=1):
        value = result["value"]
        if part["find"] == "distance":
            asks.append("求 $\\overline{AB}$ 的長。")
            shown.append(f"$\\overline{{AB}}={number_text(value, decimal=True)}$")
            steps.append(f"$\\overline{{AB}}=\\left|{_paren(b)}-{_paren(a)}\\right|={number_text(value)}$。")
        else:
            label, variable = part["label"], part.get("variable")
            m, n = part["ratio"]
            ask = f"求 ${variable}$ 的值。" if variable else f"求 ${label}$ 的坐標。"
            if part["find"] == "internal":
                second = f"\\overline{{{label}B}}"
                who = f"點 ${label}({variable})$ " if variable else f" ${label}$ 點"
                where = "在 $\\overline{AB}$ 上" if part["position"] == "on_segment" else "在 $A$、$B$ 之間"
                lead = f"已知{who}{where}，且 "
                formula = f"\\frac{{{n}\\times{_paren(a)}+{m}\\times{_paren(b)}}}{{{m}+{n}}}"
                reason = f"${label}$ 在 $\\overline{{AB}}$ 上且 $\\overline{{A{label}}}:\\overline{{{label}B}}={m}:{n}$"
            else:
                second = f"\\overline{{B{label}}}" if part["segment_order"] == "BQ" else f"\\overline{{{label}B}}"
                who = f"一點 ${label}({variable})$" if variable else f"一點 ${label}$"
                lead = f"已知 $\\overline{{AB}}$ 外{who} 滿足 "
                formula = f"\\frac{{{m}\\times{_paren(b)}-{n}\\times{_paren(a)}}}{{{m}-{n}}}"
                reason = f"${label}$ 在 $\\overline{{AB}}$ 外且 $\\overline{{A{label}}}:\\overline{{{label}B}}={m}:{n}$"
            if part["ratio_style"] == "colon":
                ratio = f"$\\overline{{A{label}}}:{second}={m}:{n}$"
            else:
                ratio = f"$\\overline{{A{label}}}={'' if m == 1 else m}{second}$"
            asks.append(f"{lead}{ratio}，{ask}")
            shown.append(f"${variable or label}={number_text(value, decimal=True)}$")
            steps.append(f"{reason}，由分點公式得 ${variable or label}={formula}={number_text(value)}$。")
        parts.append(_part(index, value, *_RATIONAL))
    if len(parts) == 1:
        return _single_payload(matrix, question=f"{intro}{asks[0]}", part=parts[0], display_answer=shown[0],
                               explanation_steps=steps, shape="number_line_coordinate")
    return _parts_payload(matrix, question=f"{intro}\n{_numbered(asks)}", parts=parts,
                          display_answer="　".join(f"({i}) {s}" for i, s in enumerate(shown, start=1)),
                          explanation_steps=steps, shape="number_line_coordinate_parts")


def _solutions_latex(solutions: list[str]) -> str:
    return " 或 ".join(f"$x={number_text(s)}$" for s in solutions) if solutions else "無解"


def _solve_absolute_value_equations(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    equations, results = givens["equations"], answer["parts"]
    parts, steps = [], []
    for index, (equation, result) in enumerate(zip(equations, results), start=1):
        expected = ", ".join(result["solutions"]) if result["solutions"] else "無解"
        parts.append(_part(index, expected, *_SOLUTION_SET, solution_members="exact_rational"))
        cuts = "、".join(f"$x={number_text(p)}$" for p in result["breakpoints"])
        steps.append(f"${relation_latex(equation)}$：以 {cuts} 分段去掉絕對值，逐段解一次方程式並保留落在該段的解，"
                     f"得 {_solutions_latex(result['solutions'])}。")
    if len(parts) == 1:
        body = f"${relation_latex(equations[0])}$"
        if givens["prompt"] == "find_real_x":
            question = f"已知x為實數且 {body}，求x之值。"
            if givens["state_solution_count"]:
                question += f"（x有{_COUNT_WORDS.get(len(results[0]['solutions']), len(results[0]['solutions']))}解）"
        else:
            question = f"解方程式 {body}。"
        return _single_payload(matrix, question=question, part=parts[0],
                               display_answer=_solutions_latex(results[0]["solutions"]),
                               explanation_steps=steps, shape="equation_solution_set")
    question = "解下列各方程式：\n" + _numbered([f"${relation_latex(e)}$。" for e in equations])
    return _parts_payload(matrix, question=question, parts=parts,
                          display_answer="　".join(f"({i}) {_solutions_latex(r['solutions'])}"
                                                  for i, r in enumerate(results, start=1)),
                          explanation_steps=steps, shape="equation_solution_set_parts")


def _solve_absolute_value_inequalities(matrix: dict[str, Any]) -> dict[str, Any]:
    systems, results = matrix["givens"]["systems"], matrix["answer"]["parts"]
    parts, steps, shown = [], [], []
    for index, (system, result) in enumerate(zip(systems, results), start=1):
        parts.append(_part(index, intervals_plain(result["intervals"]), *_INTERVAL_SET))
        shown.append(f"{inequality_text(result['intervals'])}，即 ${intervals_latex(result['intervals'])}$")
        if len(system["relations"]) > 1:
            pieces = "；".join(f"${relation_latex(r)}$ 的解為 {inequality_text(s)}"
                              for r, s in zip(system["relations"], result["relation_solutions"]))
            steps.append(f"{system_text(system)}：{pieces}；取共同範圍得 {inequality_text(result['intervals'])}。")
        else:
            steps.append(f"{system_text(system)}：在絕對值內式子的零點處分段去掉絕對值，逐段解一次不等式後合併，"
                         f"得 {inequality_text(result['intervals'])}。")
    if len(parts) == 1:
        return _single_payload(matrix, question=f"解不等式 {system_text(systems[0])}。", part=parts[0],
                               display_answer=shown[0], explanation_steps=steps, shape="inequality_solution_set")
    question = "解下列各不等式：\n" + _numbered([f"{system_text(s)}。" for s in systems])
    return _parts_payload(matrix, question=question, parts=parts,
                          display_answer="　".join(f"({i}) {s}" for i, s in enumerate(shown, start=1)),
                          explanation_steps=steps, shape="inequality_solution_set_parts")


def _template_latex(relation: dict[str, Any]) -> str:
    bound = relation["bound"]
    bound_text = bound["param"] if isinstance(bound, dict) else number_text(bound)
    return f"\\left|{form_latex(relation['inner'])}\\right|{_OP_LATEX[relation['op']]}{bound_text}"


def _recover_absolute_value_parameters(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    names, target, prompt = givens["parameters"], givens["target"], givens["prompt"]
    relations = [_template_latex(r) for r in givens["relations"]]
    joined_names = ", ".join(names)
    decimal = prompt in ("body_temperature", "pregnancy_weeks")
    if prompt == "body_temperature":
        (_, low, _, _), (high, _, _, _) = target
        question = (f"人體體溫超過{number_text(high, decimal=True)}度稱為發燒，低於{number_text(low, decimal=True)}度稱為失溫。"
                    f"已知人體體溫為x度且發燒或失溫的體溫範圍恰可用 ${relations[0]}$ 來表示，求{joined_names}的值。")
    elif prompt == "pregnancy_weeks":
        low, high, _, _ = target[0]
        question = (f"懷孕的正常生產週數為{number_text(low, decimal=True)}至{number_text(high, decimal=True)}週。"
                    f"已知一孕婦生產週數為x週，其正常生產週數的範圍恰可表示為 ${relations[0]}$，求{joined_names}的值。")
    elif prompt == "system":
        system = "\\begin{cases}" + "\\\\".join(relations) + "\\end{cases}"
        question = f"已知不等式 ${system}$ 的解為 {inequality_text(target)}，求{joined_names}的值。"
    else:
        question = f"設{joined_names}為實數，已知 ${relations[0]}$ 的解為 {inequality_text(target)}，求{joined_names}的值。"
    values = answer["values"]
    parts = [{**_part(i, values[name], *_RATIONAL), "key": name, "label": name} for i, name in enumerate(names, start=1)]
    solved = "、".join(f"${relation_latex(r)}$" for r in answer["relations"])
    steps = [
        f"$|kx+m|$ 與常數比較時，解的端點為 $kx+m$ 等於正負該常數之處；與已知範圍 {inequality_text(target, decimal=decimal)} 的端點比較。",
        "得 " + "，".join(f"${n}={number_text(values[n], decimal=decimal)}$" for n in names) + "。",
        f"代回檢驗：{solved} 的解恰為 {inequality_text(target, decimal=decimal)}。",
    ]
    return _parts_payload(matrix, question=question, parts=parts,
                          display_answer="，".join(f"${n}={number_text(values[n], decimal=decimal)}$" for n in names),
                          explanation_steps=steps, shape="recovered_parameters")


def statement_text(statement: dict[str, Any]) -> str:
    kind = statement["kind"]
    if kind == "distance_expression":
        a, b = statement["points"]["A"], statement["points"]["B"]
        u, operator, v = statement["claim"]
        return (f"數線上 $A({number_text(a)})$ 與 $B({number_text(b)})$ 的距離為 "
                f"$\\left|{_paren(u)}{operator}{_paren(v)}\\right|$。")
    if kind == "weighted_point_order":
        return (f"若 $a<b$，則 ${weighted_latex(statement['left'])}{_OP_LATEX[statement['op']]}"
                f"{weighted_latex(statement['right'])}$。")
    return f"不等式 ${relation_latex(statement['left'])}$ 與 ${relation_latex(statement['right'])}$ 的解相同。"


def _statement_reason(statement: dict[str, Any], detail: dict[str, Any]) -> str:
    kind = statement["kind"]
    if kind == "distance_expression":
        return f"所寫式子的值為 ${number_text(detail['claimed'])}$，兩點距離為 ${number_text(detail['actual'])}$"
    if kind == "weighted_point_order":
        return (f"兩數分別位於 $a$ 到 $b$ 的 ${number_text(detail['left_position'])}$ 與 "
                f"${number_text(detail['right_position'])}$ 處（$a<b$），比較其位置")
    return f"兩不等式的解分別為 ${intervals_latex(detail['left'])}$ 與 ${intervals_latex(detail['right'])}$"


def _evaluate_absolute_value_statements(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    statements, labels = givens["statements"], givens["item_labels"]
    marks = ["○" if t else "×" for t in answer["truth_values"]]
    steps = [f"{statement_text(s)}{_statement_reason(s, d)}，故為「{m}」。"
             for s, d, m in zip(statements, answer["details"], marks)]
    header = "下列敘述對的打「○」，錯的打「×」。"
    if len(statements) == 1:
        prefix = f"{labels[0]} " if labels else ""
        return _choice_payload(matrix, question=f"{header}{prefix}{statement_text(statements[0])}",
                               choices=TRUE_FALSE_CHOICES, answer=marks[0], display_answer=marks[0],
                               explanation_steps=steps)
    parts = [_part(i, m, "choice_label_checker", "choice_label", "single_choice",
                   choices=[dict(c) for c in TRUE_FALSE_CHOICES]) for i, m in enumerate(marks, start=1)]
    items = [f"{labels[i - 1]} {statement_text(s)}" if labels else statement_text(s) for i, s in enumerate(statements, start=1)]
    question = header + "\n" + ("\n".join(items) if labels else _numbered(items))
    return _parts_payload(matrix, question=question, parts=parts,
                          display_answer="　".join(f"({i}) {m}" for i, m in enumerate(marks, start=1)),
                          explanation_steps=steps, shape="statement_truth_parts")


def _select_extreme_weighted_point(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    word = "最大" if givens["extreme"] == "max" else "最小"
    texts = [weighted_latex(w) for w in givens["options"]]
    choices = [{"label": str(i), "value": t} for i, t in enumerate(texts, start=1)]
    question = f"設 $a<b$，下列各數中何者{word}？" + " ".join(f"({i}) ${t}$" for i, t in enumerate(texts, start=1))
    chosen = answer["choice"]
    positions = "、".join(f"({i}) ${number_text(t)}$" for i, t in enumerate(answer["positions"], start=1))
    steps = [
        "$\\frac{pa+qb}{p+q}$ 位於 $a$ 到 $b$ 之間，且越靠近 $b$ 越大；其位置為 $a$ 起算全長的 $\\frac{q}{p+q}$。",
        f"各選項的位置分別為 {positions}，故{word}者為 ({chosen})。",
    ]
    return _choice_payload(matrix, question=question, choices=choices, answer=texts[chosen - 1],
                           display_answer=f"({chosen}) ${texts[chosen - 1]}$", explanation_steps=steps)


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "evaluate_number_line_division_points": _division_points,
    "solve_absolute_value_equations": _solve_absolute_value_equations,
    "solve_absolute_value_inequalities": _solve_absolute_value_inequalities,
    "recover_absolute_value_parameters": _recover_absolute_value_parameters,
    "evaluate_absolute_value_statements": _evaluate_absolute_value_statements,
    "select_extreme_weighted_point": _select_extreme_weighted_point,
}


def adapt_absolute_value_relations_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_absolute_value_relations_operation:{operation}")
    return builder(matrix)
