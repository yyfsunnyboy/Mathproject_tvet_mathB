"""Question payload contracts for sequence.progression (普高數學2 Unit 1 數列).

Every expected answer comes from the domain matrix, never from this adapter.  Stems are rebuilt from the same stated
data as the domain solved, so a varied question always carries its own numbers.
"""

from __future__ import annotations

from typing import Any, Callable

import sympy as sp

from .sequence_progression_domain import DOMAIN_KEY, formula_expr, is_rational, num, text, tex

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_EXPR = ("expression_checker", "algebraic_equivalent", "expression")
_RADICAL = ("expression_checker", "radical_equivalence", "numeric_or_radical")
_SET = ("solution_set_checker", "unordered_solution_set", "solution_set")
_LANGLE, _RANGLE, _LDOTS = "\\left\\langle ", "\\right\\rangle", "\\ldots"
_COMMA, _DIV, _SQRT, _FRAC, _GE = ",\\ ", "\\div ", "\\sqrt{", "\\frac{", "\\ge "


# --- contracts (same shape as the other general-high adapters) ------------------------------------

def _contract(answer_type: str, presentation_mode: str, checker: str, equivalence: str, **extra: Any) -> dict[str, Any]:
    return {
        "presentation_mode": presentation_mode, "answer_type": answer_type, "checker": checker, "checker_key": checker,
        "answer_equivalence": equivalence, "equivalence": equivalence, "equivalence_type": equivalence, **extra,
    }


def _part(index: int, expected: Any, checker: str, equivalence: str, answer_type: str, **extra: Any) -> dict[str, Any]:
    return {"key": f"part_{index}", "label": f"({index})", "checker": checker, "checker_key": checker, "equivalence_type": equivalence,
            "answer_type": answer_type, "expected_answer": expected, **extra}


def _payload(matrix, *, question, answer, display_answer, contract, explanation_steps, choices=()) -> dict[str, Any]:
    operation = matrix["domain_operation"]
    return {
        "question_text": question, "question": question, "answer": answer, "correct_answer": answer, "display_answer": display_answer,
        "semantic_answer": matrix["answer"], "answer_type": contract["answer_type"], "presentation_mode": contract["presentation_mode"],
        "problem_type_id": operation, "domain_operation": operation, "fixed_domain_key": DOMAIN_KEY,
        "answer_contract": {**contract, "semantic_answer": matrix["answer"]}, "explanation_steps": explanation_steps,
        "choices": [dict(c) for c in choices], "options": [dict(c) for c in choices],
        "math_core": {"givens": matrix["givens"], "target": matrix["answer"], "validation_facts": matrix["validation_facts"]},
    }


def _single_payload(matrix, *, question, part, display_answer, explanation_steps, shape) -> dict[str, Any]:
    skip = ("key", "label", "checker", "checker_key", "equivalence_type", "answer_type", "expected_answer", "prompt")
    extra = {k: v for k, v in part.items() if k not in skip}
    if part["answer_type"] == "single_choice":
        return _payload(matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
                        contract=_contract("single_choice", "single_choice", "choice_label_checker", "choice_label",
                                           answer_shape="single_choice", choices=[dict(c) for c in part["choices"]]),
                        explanation_steps=explanation_steps, choices=part["choices"])
    return _payload(matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
                    contract=_contract(part["answer_type"], "short_answer", part["checker"], part["equivalence_type"], answer_shape=shape, **extra),
                    explanation_steps=explanation_steps)


def _parts_payload(matrix, *, question, parts, display_answer, explanation_steps, shape) -> dict[str, Any]:
    if len(parts) == 1:
        return _single_payload(matrix, question=question, part=parts[0], display_answer=display_answer,
                               explanation_steps=explanation_steps, shape=shape)
    return _payload(matrix, question=question, answer={p["key"]: p["expected_answer"] for p in parts}, display_answer=display_answer,
                    contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer", answer_shape=shape, parts=parts),
                    explanation_steps=explanation_steps)


def _t(s: str) -> str:
    return f"${s}$"


def _value_part(index: int, value: str, label: str) -> dict[str, Any]:
    """A single number: exact rational, or a radical expression."""
    checker = _RATIONAL if is_rational(value) else _RADICAL
    return _part(index, value, *checker, label=label, prompt=label)


_SET_EXAMPLES = ("2, 5", "3, 8", "-1, 4", "6, 11", "-3, 7", "10, 13")


def _set_part(index: int, members: list[str], label: str = "", example: str = "") -> dict[str, Any]:
    """A value set.  The format hint is shown before submitting, so it is a fixed illustration sharing no value with the answer."""
    extra = {"label": label, "prompt": label} if label else {}
    answer = {num(m) for m in members}
    shown = next(e for e in _SET_EXAMPLES if not ({num(x.strip()) for x in e.split(",")} & answer))
    return _part(index, list(members), *_SET, solution_members="exact_rational", answer_format_example=shown, **extra)


def _choice_part(index: int, expected_label: str, choices: list[dict[str, str]]) -> dict[str, Any]:
    return _part(index, expected_label, "choice_label_checker", "choice_label", "single_choice", choices=[dict(c) for c in choices])


def _disp(v: Any) -> str:
    import re

    return re.sub(r"sqrt[(](\d+)[)]", lambda m: "√" + m.group(1), str(v)).replace("*", "")


def _words(values: list[str], joiner: str = "、") -> str:
    return joiner.join(_t(tex(v)) for v in values)


def _terms_tex(values: list[Any]) -> str:
    return ",\\ ".join(tex(v) for v in values)


# --- 1. sequence_terms_from_formula --------------------------------------------------------------------------------------

def _lin_tex(a: Any, b: Any) -> str:
    """``an+b`` with the coefficient conventions of the textbook (n, -n, 3n+1, 2n-1)."""
    out = ""
    if num(a) != 0:
        out = {1: "n", -1: "-n"}.get(num(a), tex(a) + "n") if num(a) in (1, -1) else tex(a) + "n"
    if num(b) != 0:
        out += (("+" if num(b) > 0 and out else "") + tex(b))
    return out or "0"


def _quad_tex(a: Any, b: Any, c: Any, ascending: bool = False) -> str:
    terms = [(a, "n^{2}"), (b, "n"), (c, "")]
    if ascending:
        terms = terms[::-1]
    out = ""
    for coef, var in terms:
        q = num(coef)
        if q == 0:
            continue
        body = var if (abs(q) == 1 and var) else tex(abs(q)) + var
        out += ("-" if q < 0 else ("+" if out else "")) + body
    return out or "0"


def _formula_tex(item: dict[str, Any]) -> str:
    kind = item["kind"]
    if kind == "linear":
        return _lin_tex(item["a"], item["b"])
    if kind == "quad":
        return _quad_tex(item["a"], item["b"], item["c"], bool(item.get("ascending")))
    if kind == "frac":
        return _FRAC + _lin_tex(item["p"], item["q"]) + "}{" + _lin_tex(item["r"], item["s"]) + "}"
    sign = "(-1)^{n}" if num(item.get("p", 1)) == 1 else tex(item["p"]) + "(-1)^{n}"
    return _FRAC + sign + "}{" + _lin_tex(item["r"], item["s"]) + "}"


def _sequence_terms_from_formula(matrix: dict[str, Any]) -> dict[str, Any]:
    items, recs = matrix["givens"]["items"], matrix["answer"]["items"]
    count = int(matrix["givens"].get("count", 5))
    word = {5: "五", 4: "四", 6: "六", 3: "三"}.get(count, str(count))
    lines = "\n".join(f"({i}){_t(_LANGLE + _formula_tex(it) + _RANGLE)}。" for i, it in enumerate(items, start=1))
    question = f"寫出下列數列的前{word}項。\n{lines}"
    parts, index, steps, shown = [], 0, [], []
    for i, (it, rec) in enumerate(zip(items, recs), start=1):
        for n, value in enumerate(rec["terms"], start=1):
            index += 1
            parts.append(_part(index, value, *_RATIONAL, label=f"({i}) 第{n}項", prompt=f"({i}) 第{n}項"))
        steps.append(f"({i}) 依序把 $n=1, 2, \\ldots, {count}$ 代入一般項 {_t(_formula_tex(it))}，得 {_words(rec['terms'], '、')}。")
        shown.append(f"({i}) " + ", ".join(rec["terms"]))
    return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(shown), explanation_steps=steps, shape="sequence_first_terms")


# --- 2. geometric_from_terms ----------------------------------------------------------------------------------------------

def _geometric_from_terms(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    terms, k = g["terms"], int(a["k"])
    shown = _terms_tex(terms)
    style = g.get("style", "list")
    target = tex(g["target"])
    if style == "aperture":
        listing = _t(shown + _COMMA + _LDOTS)
        intro = f"已知相機光圈值\n{listing}\n構成一個等比數列 {_t(_LANGLE + 'a_{n}' + _RANGLE)}。"
        ask = f"(3)試問光圈值 {_t(target)} 出現在該數列的第幾項？"
    else:
        listing = _t(shown + "," + _LDOTS + _COMMA + target)
        intro = f"已知{listing}構成一個等比數列 {_t(_LANGLE + 'a_{n}' + _RANGLE)}。"
        ask = f"(3)試問 {_t(target)} 是第幾項？"
    question = (f"{intro}\n(1)求首項 $a_{{1}}$ 及公比 $r$ 的值。\n(2)求第 ${k}$ 項 $a_{{{k}}}$ 的值。\n{ask}")
    parts = [_value_part(1, a["a1"], "(1) 首項 a1"), _value_part(2, a["r"], "(1) 公比 r"),
             _value_part(3, a["a_k"], f"(2) 第{k}項"), _part(4, str(a["target_index"]), *_RATIONAL, label="(3) 第幾項", prompt="(3) 第幾項")]
    steps = [f"(1) 首項 {_t('a_{1}=' + tex(a['a1']))}，公比 {_t('r=' + tex(a['r']))}（後項除以前項）。",
             f"(2) {_t('a_{n}=a_{1}r^{n-1}')}，所以 {_t(f'a_{{{k}}}=' + tex(a['a_k']))}。",
             f"(3) 令 {_t('a_{n}=' + target)}，解得 {_t('n=' + str(a['target_index']))}，即第 {a['target_index']} 項。"]
    shown_answer = f"(1) a₁={_disp(a['a1'])}, r={_disp(a['r'])}；(2) {_disp(a['a_k'])}；(3) 第{a['target_index']}項"
    return _parts_payload(matrix, question=question, parts=parts, display_answer=shown_answer, explanation_steps=steps, shape="geometric_terms")


# --- 3. geometric_from_relations ------------------------------------------------------------------------------------------

def _a(k: int) -> str:
    return f"a_{{{k}}}"


def _geometric_from_relations(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    kind = a["kind"]
    seq = _t(_LANGLE + "a_{n}" + _RANGLE)
    if kind == "sum_pairs":
        k = int(g["ask_k"])
        question = f"已知等比數列 {seq} 滿足 {_t(_a(1) + '+' + _a(3) + '=' + tex(g['S13']))}、{_t(_a(2) + '+' + _a(4) + '=' + tex(g['S24']))}，求 {_t(_a(k))} 的值。"
        part = _value_part(1, a["members"][0], "")
        steps = [f"設首項 $a_{{1}}$、公比 $r$：兩式相除得 {_t('r=' + tex(a['r']))}，代回 {_t(_a(1) + '(1+r^{2})=' + tex(g['S13']))} 得 {_t(_a(1) + '=' + tex(a['a1']))}。",
                 f"所以 {_t(_a(k) + '=' + _a(1) + 'r^{' + str(k - 1) + '}=' + tex(a['members'][0]))}。"]
        return _single_payload(matrix, question=question, part=part, display_answer=a["members"][0], explanation_steps=steps, shape="geometric_value")
    if kind == "product_positive":
        question = f"已知等比數列 {seq} 的每項均為正數，且滿足 {_t(_a(1) + _a(3) + '=' + tex(g['P13']))}、{_t(_a(4) + '=' + tex(g['a4']))}，求 {_t(_a(1))} 的值。"
        part = _value_part(1, a["a1"], "")
        root_tex = _t(_a(2) + "=" + _SQRT + tex(g["P13"]) + "}")
        a1_tex = _t(_a(1) + "=" + _a(2) + _DIV + "r=" + tex(a["a1"]))
        steps = [f"{_t(_a(1) + _a(3) + '=' + _a(2) + '^{2}')}，每項為正，所以 {root_tex}；再由 {_t(_a(4) + '=' + _a(2) + 'r^{2}')} 得公比 {_t('r=' + tex(a['r']))}。",
                 f"因此 {a1_tex}。"]
        return _single_payload(matrix, question=question, part=part, display_answer=a["a1"], explanation_steps=steps, shape="geometric_value")
    if kind == "two_terms":
        m, n = int(g["m"]), int(g["n"])
        question = f"已知等比數列 {seq} 滿足 {_t(_a(m) + '=' + tex(g['A']))}、{_t(_a(n) + '=' + tex(g['B']))}，求首項 {_t(_a(1))} 及公比 $r$ 的值。"
        parts = [_value_part(1, a["a1"], "首項 a1"), _value_part(2, a["r"], "公比 r")]
        steps = [f"兩式相除得 {_t('r^{' + str(n - m) + '}=' + tex(sp.radsimp(num(g['B']) / num(g['A']))))}，實數解 {_t('r=' + tex(a['r']))}。",
                 f"再由 {_t(_a(m) + '=' + _a(1) + 'r^{' + str(m - 1) + '}')} 得 {_t(_a(1) + '=' + tex(a['a1']))}。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"a₁={_disp(a['a1'])}, r={_disp(a['r'])}", explanation_steps=steps, shape="geometric_two_values")
    k = int(g["ask_k"])
    question = f"已知等比數列 {seq} 滿足 {_t(_a(2) + '-' + _a(1) + '=' + tex(g['D']))}、{_t(_a(1) + '+' + _a(3) + '=' + tex(g['S']))}，求 {_t(_a(k))} 的值。"
    part = _set_part(1, a["members"])
    steps = [f"由 {_t(_a(1) + '(r-1)=' + tex(g['D']))} 與 {_t(_a(1) + '(1+r^{2})=' + tex(g['S']))} 消去 $a_{{1}}$，解出公比 $r$ 有兩個值。",
             f"分別求出 {_t(_a(k))}：{_words(a['members'])}（共兩解，皆須作答）。"]
    return _single_payload(matrix, question=question, part=part, display_answer="、".join(a["members"]), explanation_steps=steps, shape="solution_value_set")


# --- 4. progression_three_numbers ------------------------------------------------------------------------------------------

def _signed(v: Any) -> str:
    q = num(v)
    return ("-" if q < 0 else "+") + tex(abs(q))


def _progression_three_numbers(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    kind = a["kind"]
    members = a["members"] if "members" in a else None
    if kind == "geo_then_arith":
        m, c = g["m"], g["c"]
        question = (f"已知 $a,\\ {tex(m)},\\ b$ 三數成等比數列，且 $a,\\ {tex(m)},\\ b{_signed(c)}$ 三數成等差數列，求 $a$ 的值。")
        steps = [f"等比：{_t('ab=' + tex(num(m) ** 2))}；等差：{_t('a+(b' + _signed(c) + ')=' + tex(2 * num(m)))}，即 {_t('a+b=' + tex(2 * num(m) - num(c)))}。",
                 f"消去 $b$ 得 {_t('a^{2}-' + tex(2 * num(m) - num(c)) + 'a+' + tex(num(m) ** 2) + '=0')}，解得 $a=$ {_words(members, '或')}。"]
    elif kind == "arith_geo_chain":
        p, q = g["p"], g["q"]
        question = f"已知一數列 ${tex(p)},\\ a,\\ b,\\ {tex(q)}$ 滿足前三項成等差數列，且後三項成等比數列，求 $a$ 的值。"
        steps = [f"前三項等差：{_t('2a=' + tex(p) + '+b')}；後三項等比：{_t('b^{2}=' + tex(q) + 'a')}。",
                 f"由 {_t('b=2a' + _signed(-num(p)))} 代入得 {_t('(2a' + _signed(-num(p)) + ')^{2}=' + tex(q) + 'a')}，解得 $a=$ {_words(members, '或')}。"]
    elif kind == "arith_positions":
        A, i, j = g["A"], int(g["i"]), int(g["j"])
        trio = f"{tex(A)},\\ {tex(A)}r,\\ {tex(A)}r^{{2}}" if num(A) != 1 else "1,\\ r,\\ r^{2}"
        question = f"已知成等比的 ${trio}$ 三數恰為另一等差數列之第 ${1},\\ {i},\\ {j}$ 項，求 $r$ 的值。（有兩解）"
        steps = [f"設等差數列公差為 $d$：{_t(tex(A) + 'r-' + tex(A) + '=' + str(i - 1) + 'd')}、{_t(tex(A) + 'r^{2}-' + tex(A) + '=' + str(j - 1) + 'd')}。",
                 f"消去 $d$ 得 {_t('(r-1)[' + str(i - 1) + '(r+1)-' + str(j - 1) + ']=0')}，所以 $r=$ {_words(members, '或')}。"]
    else:
        S, shifts = g["S"], g["shifts"]
        question = (f"設三正數成等差數列且其總和為${tex(S)}$。已知此三數依序分別加上${tex(shifts[0])}, {tex(shifts[1])}, {tex(shifts[2])}$後會成為等比數列，求此三數中最小的數。")
        x = tex(num(S) / 3)
        triple_tex = _t(x + "-d" + _COMMA + x + _COMMA + x + "+d")
        steps = [f"設三數為 {triple_tex}（總和 ${tex(S)}$）。",
                 f"加上 ${tex(shifts[0])}, {tex(shifts[1])}, {tex(shifts[2])}$ 後成等比：{_t('(' + x + '-d' + _signed(shifts[0]) + ')(' + x + '+d' + _signed(shifts[2]) + ')=(' + x + _signed(shifts[1]) + ')^{2}')}，"
                 f"取三數皆為正的解，三數為 {_words(a['triple'])}，最小的是 {_t(tex(a['smallest']))}。"]
        part = _value_part(1, a["smallest"], "")
        return _single_payload(matrix, question=question, part=part, display_answer=a["smallest"], explanation_steps=steps, shape="progression_value")
    part = _set_part(1, members)
    return _single_payload(matrix, question=question, part=part, display_answer="、".join(members), explanation_steps=steps, shape="solution_value_set")


# --- 5. arithmetic_from_terms -------------------------------------------------------------------------------------------------

def _arithmetic_from_terms(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    m, n = int(g["m"]), int(g["n"])
    question = (f"設等差數列 {_t(_LANGLE + 'a_{n}' + _RANGLE)} 滿足 {_t(_a(m) + '=' + tex(g['A']))}、{_t(_a(n) + '=' + tex(g['B']))}。\n"
                "(1)求首項 $a_{1}$ 及公差 $d$ 的值。\n(2)此數列從第幾項開始出現負數？")
    parts = [_value_part(1, a["a1"], "(1) 首項 a1"), _value_part(2, a["d"], "(1) 公差 d"), _part(3, str(a["first_negative"]), *_RATIONAL, label="(2) 第幾項", prompt="(2) 第幾項")]
    d_tex = _t("d=" + _FRAC + tex(g["B"]) + "-" + tex(g["A"]) + "}{" + str(n - m) + "}=" + tex(a["d"]))
    steps = [f"(1) {d_tex}，{_t('a_{1}=' + _a(m) + '-' + str(m - 1) + 'd=' + tex(a['a1']))}。",
             f"(2) {_t('a_{n}=' + tex(a['a1']) + '+(n-1)(' + tex(a['d']) + ')<0')}，解得 $n>{tex(num(a['a1']) / -num(a['d']) + 1)}$，所以從第 {a['first_negative']} 項開始出現負數。"]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"a₁={a['a1']}, d={a['d']}；第{a['first_negative']}項", explanation_steps=steps, shape="arithmetic_terms")


# --- 6. sequence_statements -----------------------------------------------------------------------------------------------------------

def _recurrence_tex(tp: str, a1: Any, c: Any) -> str:
    step = f"a_{{n-1}}{_signed(c)}" if tp == "arithmetic" else (f"{tex(c)}a_{{n-1}}" if num(c) not in (1, -1) else ("a_{n-1}" if num(c) == 1 else "-a_{n-1}"))
    return "\\left\\{\\begin{array}{l} a_{1}=" + tex(a1) + " \\\\ a_{n}=" + step + "\\quad (n\\ge 2) \\end{array}\\right."


def _statement_sentence(st: dict[str, Any]) -> str:
    kind = st["kind"]
    if kind == "term_claim":
        k = int(st["k"])
        formula = _FRAC + _quad_tex(st["p2"], st["p1"], st["p0"]) + "}{" + _lin_tex(st["r"], st["s"]) + "}"
        return f"數列 {_t(_LANGLE + formula + _RANGLE)} 的第 ${k}$ 項為 ${tex(st['value'])}$"
    if kind == "progression_claim":
        word = "等差" if st["claim"] == "arithmetic" else "等比"
        return f"數列 {_t(_terms_tex(st['terms']))} 是{word}數列"
    if kind == "both_claim":
        return f"數列 {_t(_terms_tex(st['terms']))} 既是等差數列也是等比數列"
    word = "等差" if st["type"] == "arithmetic" else "等比"
    par = "公差" if st["type"] == "arithmetic" else "公比"
    return (f"若{word}數列 {_t(_LANGLE + 'a_{n}' + _RANGLE)} 的首項為 ${tex(st['a1'])}$，{par}為 ${tex(st['c'])}$，"
            f"則 {_t(_LANGLE + 'a_{n}' + _RANGLE)} 的遞迴關係式為 {_t(_recurrence_tex(st['shown_type'], st['shown_a1'], st['shown_c']))}")


def _statement_reason(st: dict[str, Any], a: dict[str, Any]) -> str:
    kind = st["kind"]
    if kind == "term_claim":
        return f"代入 $n={st['k']}$ 得第 {st['k']} 項為 {_t(tex(a['actual']))}，所以敘述{'正確' if a['truth'] else '錯誤'}。"
    if kind == "progression_claim":
        return ("相鄰兩項的" + ("差" if st["claim"] == "arithmetic" else "比") + ("相等" if a["truth"] else "不相等") + "，所以敘述" + ("正確" if a["truth"] else "錯誤") + "。")
    if kind == "both_claim":
        return "常數數列公差為 $0$，是等差數列；" + ("各項不為 $0$，公比為 $1$，也是等比數列。" if a["truth"] else "但有項為 $0$，不能當等比數列的項（分母不可為 $0$）。")
    return f"依首項與{'公差' if st['type'] == 'arithmetic' else '公比'}寫出的遞迴關係式{'與敘述相同' if a['truth'] else '與敘述不同'}，所以敘述{'正確' if a['truth'] else '錯誤'}。"


def _sequence_statements(matrix: dict[str, Any]) -> dict[str, Any]:
    st, a = matrix["givens"]["statement"], matrix["answer"]
    truth = bool(a["truth"])
    question = "下列敘述對的打「○」，錯的打「×」。\n" + _statement_sentence(st) + "。"
    part = _choice_part(1, "A" if truth else "B", [dict(c) for c in TRUE_FALSE_CHOICES])
    steps = [f"{_statement_reason(st, a)}此敘述為「{'○' if truth else '×'}」。"]
    return _single_payload(matrix, question=question, part=part, display_answer="○" if truth else "×", explanation_steps=steps, shape="single_choice")


def _three_numbers_dispatch(matrix: dict[str, Any]) -> dict[str, Any]:
    if matrix["answer"].get("kind") == "geo_sum_relation":
        from .sequence_progression_recurrence_adapter import geo_sum_relation_payload

        return geo_sum_relation_payload(matrix)
    return _progression_three_numbers(matrix)


def _statements_dispatch(matrix: dict[str, Any]) -> dict[str, Any]:
    if matrix["givens"]["statement"].get("kind") == "recurrence_term_claim":
        from .sequence_progression_recurrence_adapter import recurrence_term_claim_payload

        return recurrence_term_claim_payload(matrix)
    return _sequence_statements(matrix)


def _recurrence_dispatch(matrix: dict[str, Any]) -> dict[str, Any]:
    from .sequence_progression_recurrence_adapter import recurrence_from_process_payload

    return recurrence_from_process_payload(matrix)


def _figure_path_dispatch(matrix: dict[str, Any]) -> dict[str, Any]:
    from .sequence_progression_pattern_adapter import figure_path_pattern_payload

    return figure_path_pattern_payload(matrix)


def _finger_dispatch(matrix: dict[str, Any]) -> dict[str, Any]:
    from .sequence_progression_pattern_adapter import finger_counting_cycle_payload

    return finger_counting_cycle_payload(matrix)


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "sequence_terms_from_formula": _sequence_terms_from_formula,
    "geometric_from_terms": _geometric_from_terms,
    "geometric_from_relations": _geometric_from_relations,
    "progression_three_numbers": _three_numbers_dispatch,
    "arithmetic_from_terms": _arithmetic_from_terms,
    "sequence_statements": _statements_dispatch,
    "recurrence_from_process": _recurrence_dispatch,
    "figure_path_pattern": _figure_path_dispatch,
    "finger_counting_cycle": _finger_dispatch,
}


def adapt_sequence_progression_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_sequence_progression_operation:{operation}")
    return builder(matrix)
