"""Question payload contracts for algebra.polynomial_division.

Every payload is graded by a shared checker registered in ``CHECKER_CAPABILITIES``; the expected
answers always come from the domain matrix, never from this adapter.  Display text (stems, steps)
is rebuilt from the same givens, so a varied question never shows stale content.  The source's
blackboard / masked synthetic-division pictures are reproduced as LaTeX in the stem (they carry no
information beyond the polynomial / the table), so no fixed picture can disagree with the numbers.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable

from .polynomial_core import (
    LinearForm, deg, ev, fr, frac_latex, frac_text, lf_poly, lf_poly_latex, norm, padd, pdivmod, pmul, poly, poly_latex,
    root_of,
)
from .polynomial_division_domain import DOMAIN_KEY

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
SQUARE = "\\square"
CN = {0: "零", 1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九"}

_EXPR = ("expression_checker", "algebraic_equivalent", "expression")
_FACTORED = ("expression_checker", "factorized_form", "expression")
_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_SET = ("solution_set_checker", "unordered_solution_set", "solution_set")


# --- contracts ---------------------------------------------------------------------------------

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


def _part(index: int, expected: Any, checker: str, equivalence: str, answer_type: str, **extra: Any) -> dict[str, Any]:
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
        "math_core": {"givens": matrix["givens"], "target": matrix["answer"], "validation_facts": matrix["validation_facts"]},
    }


def _single_payload(matrix, *, question, part, display_answer, explanation_steps, shape) -> dict[str, Any]:
    skip = ("key", "label", "checker", "checker_key", "equivalence_type", "answer_type", "expected_answer", "prompt")
    extra = {k: v for k, v in part.items() if k not in skip}
    if part["answer_type"] == "single_choice":
        return _payload(
            matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
            contract=_contract("single_choice", "single_choice", "choice_label_checker", "choice_label",
                               answer_shape="single_choice", choices=[dict(c) for c in part["choices"]]),
            explanation_steps=explanation_steps, choices=part["choices"],
        )
    return _payload(
        matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
        contract=_contract(part["answer_type"], "short_answer", part["checker"], part["equivalence_type"], answer_shape=shape, **extra),
        explanation_steps=explanation_steps,
    )


def _parts_payload(matrix, *, question, parts, display_answer, explanation_steps, shape) -> dict[str, Any]:
    if len(parts) == 1:
        return _single_payload(matrix, question=question, part=parts[0], display_answer=display_answer,
                               explanation_steps=explanation_steps, shape=shape)
    return _payload(
        matrix, question=question, answer={p["key"]: p["expected_answer"] for p in parts}, display_answer=display_answer,
        contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer",
                           answer_shape=shape, parts=parts),
        explanation_steps=explanation_steps,
    )


def _t(text: str) -> str:
    return f"${text}$"


def _poly_part(index: int, rec: dict[str, Any], label: str, expanded: bool = True) -> dict[str, Any]:
    extra = {"required_form": "expanded"} if expanded else {}
    return _part(index, rec["plain"], *_EXPR, label=label, prompt=label, **extra)


def _num_part(index: int, canonical: str, label: str, example: str = "") -> dict[str, Any]:
    extra = {"answer_format_example": example} if example else {}
    return _part(index, canonical, *_RATIONAL, label=label, prompt=label, **extra)


def _selection_part(index: int, selected: list[int]) -> dict[str, Any]:
    if not selected:
        raise ValueError("selection_needs_at_least_one_correct_option")
    return _part(index, list(selected), *_SET, solution_members="exact_rational", answer_format_example="2, 4")


def _paren(coeffs: Any) -> str:
    """Operand of a displayed sum / difference / product: always parenthesised."""
    return f"({_px(coeffs)})"


def _dec(q: Fraction) -> str:
    """Terminating decimals are shown as decimals (``1.99``), anything else as a fraction."""
    d = q.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    if d != 1:
        return frac_latex(q)
    text = f"{float(abs(q)):.10f}".rstrip("0").rstrip(".")
    return ("-" if q < 0 else "") + text


def _dec_text(q: Fraction, digits: int = 2) -> str:
    scale = 10 ** digits
    n = int(q * scale)
    sign = "-" if n < 0 else ""
    n = abs(n)
    return f"{sign}{n // scale}.{str(n % scale).zfill(digits)}"


# --- LaTeX helpers -----------------------------------------------------------------------------

def _px(coeffs: Any) -> str:
    return poly_latex(poly(coeffs))


def _wrap(coeffs: Any) -> str:
    p = poly(coeffs)
    text = poly_latex(p)
    return f"({text})" if sum(1 for c in p if c != 0) > 1 else text


def _shift(c: Fraction) -> str:
    """``(x-c)`` as it is written when expanding in powers of x-c."""
    if c.denominator == 1:
        return "x" if c == 0 else (f"x-{c.numerator}" if c > 0 else f"x+{-c.numerator}")
    return f"x-{frac_latex(c)}" if c > 0 else f"x+{frac_latex(-c)}"


def _name(n: str) -> str:
    return f"{n}\\left(x\\right)"


def _ref(defs: dict[str, Any], ref: Any) -> str:
    return _name(ref) if isinstance(ref, str) else _px(ref)


def _rows_array(rows: list[list[str]], root: str) -> str:
    """Synthetic-division table (divisor root on the right, three rows)."""
    n = len(rows[0])
    top = " & ".join(_signed(c, i) for i, c in enumerate(rows[0]))
    mid = " & ".join("" if i == 0 else _signed(c, i) for i, c in enumerate(rows[1]))
    bot = " & ".join(_signed(c, i) for i, c in enumerate(rows[2]))
    return (f"\\begin{{array}}{{c|{'r' * n}}} {_lex(root)} & {top} \\\\ +) & {mid} \\\\ \\hline & {bot} \\end{{array}}")


def _lex(text: str) -> str:
    q = fr(text)
    return frac_latex(q)


def _signed(c: str, i: int) -> str:
    q = fr(c)
    body = frac_latex(abs(q))
    return body if i == 0 and q >= 0 else (f"-{body}" if q < 0 else f"+{body}")


def _synthetic_step(rec: dict[str, Any]) -> str:
    t = rec["table"]
    return f"以綜合除法計算（乘數為 ${_lex(t['root'])}$）：${_rows_array(t['rows'], t['root'])}$"


# --- A. polynomial_arithmetic_items --------------------------------------------------------------

def _item_text(defs: dict[str, Any], it: dict[str, Any]) -> str:
    f, g = _ref(defs, it["f"]), _ref(defs, it["g"])
    kind = it["op"]
    if kind == "add":
        return f"{_t(f + '+' + g)}"
    if kind == "sub":
        return f"{_t(f + '-' + g)}"
    if kind == "mul":
        return f"{_t(f + g)}"
    gf = _px(it["g"]) if not isinstance(it["g"], str) else g
    ff = _px(it["f"]) if not isinstance(it["f"], str) else f
    if it.get("phrase") == "by_into":
        return f"以 {_t(gf)} 除 {_t(ff)}。"
    return f"{_t(ff)} 除以 {_t(gf)} 的商式與餘式。" if kind == "divide" else f"{_t(ff)} 除以 {_t(gf)} 的商式及餘式。"


def _polynomial_arithmetic_items(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    defs, items, results = givens["defs"], givens["items"], answer["items"]
    style = givens.get("style", "defs_then_items")
    head = "、".join(_t(f"{_name(k)}={_px(v)}") for k, v in defs.items())
    multi = len(items) > 1
    lines = [f"({i}){_item_text(defs, it)}" for i, it in enumerate(items, start=1)]
    if style == "product":
        it = items[0]
        question = f"求多項式 {_t(_name(it['f']) + '=' + _px(defs[it['f']]))} 與 {_t(_name(it['g']) + '=' + _px(defs[it['g']]))} 的乘積。"
    elif style == "defs_then_items":
        question = f"已知 {head}，求" + ("\n" + " ".join(lines) if multi else _item_text(defs, items[0]).rstrip("。") + "。")
    elif style == "synthetic_single":
        question = f"使用綜合除法求 {_t(_px(items[0]['f']))} 除以 {_t(_px(items[0]['g']))} 的商式及餘式。"
    elif style == "synthetic_list":
        question = givens.get("intro", "使用綜合除法，求下列各式。") + "\n" + "\n".join(lines)
    else:
        raise ValueError(f"unknown_arithmetic_style:{style}")
    parts: list[dict[str, Any]] = []
    steps: list[str] = []
    answers: list[str] = []
    for i, (it, rec) in enumerate(zip(items, results), start=1):
        tag = f"({i}) " if multi else ""
        kind = it["op"]
        if kind in ("add", "sub", "mul"):
            parts.append(_poly_part(len(parts) + 1, rec["value"], f"({i})" if multi else "結果"))
            symbol = {"add": "+", "sub": "-", "mul": "\\times "}[kind]
            lhs = _paren(it["f"] if not isinstance(it["f"], str) else defs[it["f"]])
            rhs = _paren(it["g"] if not isinstance(it["g"], str) else defs[it["g"]])
            steps.append(f"{tag}${lhs}{symbol}{rhs}={rec['value']['latex']}$。")
            answers.append(f"{tag}${rec['value']['latex']}$")
        else:
            lq, lr = (f"({i}) 商式", f"({i}) 餘式") if multi else ("商式", "餘式")
            parts.append(_poly_part(len(parts) + 1, rec["quotient"], lq))
            parts.append(_poly_part(len(parts) + 1, rec["remainder"], lr))
            if kind == "synthetic":
                steps.append(tag + _synthetic_step(rec))
            steps.append(f"{tag}商式 ${rec['quotient']['latex']}$，餘式 ${rec['remainder']['latex']}$（餘式次數小於除式次數）。")
            answers.append(f"{tag}商式 ${rec['quotient']['latex']}$，餘式 ${rec['remainder']['latex']}$")
    return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(answers),
                          explanation_steps=steps, shape="polynomial_arithmetic")


# --- B. evaluate_polynomial_statements -----------------------------------------------------------

def _subject_expr(subject: dict[str, Any]) -> str:
    if subject["type"] == "poly":
        return _px(subject["coeffs"])
    return f"{_wrap(subject['divisor'])}{_wrap(subject['quotient'])}" + ("" if not poly(subject["remainder"]) else "+" + _px(subject["remainder"]))


def _sentence(st: dict[str, Any], named: bool, f_expr: str) -> str:
    kind = st["kind"]
    F = _t("f(x)")
    if kind == "is_degree_poly":
        return f"{F} 為{CN[int(st['n'])]}次多項式"
    if kind == "deg_equals":
        return _t(f"\\deg f(x)={int(st['n'])}")
    if kind == "coeff_is":
        p = int(st["power"])
        mono = "x" if p == 1 else ("" if p == 0 else f"x^{{{p}}}")
        return f"{_t(mono or '常數項')} 的係數為{_t(frac_latex(fr(st['value'])))}" if mono else f"常數項為{_t(frac_latex(fr(st['value'])))}"
    if kind == "value_is":
        return _t(f"f\\left({frac_latex(fr(st['x']))}\\right)={frac_latex(fr(st['value']))}")
    if kind == "quotient_degree":
        return f"{_t('q(x)')} 為{CN[int(st['n'])]}次多項式"
    if kind == "quotient_integer_coeffs":
        return f"{_t('q(x)')} 的係數都是整數"
    if kind == "remainder_equals":
        if named:
            return _t(f"r(x)={_px(st['claimed'])}")
        return f"{F} 除以 {_t(_px(st['divisor']))} 的餘式為 {_t(_px(st['claimed']))}"
    if kind == "quotient_equals":
        return f"{F} 除以 {_t(_px(st['divisor']))} 的商式為 {_t(_px(st['claimed']))}"
    if kind == "is_factor":
        if st.get("phrase") == "divisible":
            return f"{F} 可被 {_t(_px(st['divisor']))} 整除"
        return f"{_t(_px(st['divisor']))} 是 {F} 的因式"
    if kind == "division_identity":
        return _t("f(x)=g(x)q(x)+r(x)")
    if kind == "fraction_identity":
        return _t("\\frac{f(x)}{g(x)}=q(x)+\\frac{r(x)}{g(x)}")
    if kind in ("scaled_remainder_same", "scaled_quotient_same"):
        what = "餘式" if kind == "scaled_remainder_same" else "商式"
        d = poly(st["divisor"])
        scaled = norm([c * fr(st["k"]) for c in d])
        return f"多項式 {F} 除以 {_t(_px(d))} 的{what}與 {F} 除以 {_t(_px(scaled))} 的{what}相同"
    if kind == "factor_product_from_zeros":
        zeros = "=".join(f"f\\left({frac_latex(fr(z))}\\right)" for z in st["zeros"])
        product = "".join(f"({_px(c)})" for c in st["factors"])
        return f"若多項式 {F} 滿足 {_t(zeros + '=0')}，則 {_t(product)} 是 {F} 的因式"
    raise ValueError(f"unknown_statement_kind:{kind}")


def _statement_detail(f: list[Fraction] | None, st: dict[str, Any], truth: bool) -> str:
    kind = st["kind"]
    if f is not None:
        if kind in ("is_degree_poly", "deg_equals"):
            return f"次數為 ${deg(f)}$"
        if kind == "coeff_is":
            p = int(st["power"])
            return f"該項係數實為 ${frac_latex(f[deg(f) - p] if 0 <= p <= deg(f) else Fraction(0))}$"
        if kind == "value_is":
            return f"$f\\left({frac_latex(fr(st['x']))}\\right)={frac_latex(ev(f, st['x']))}$"
        if "divisor" in st:
            q, r = pdivmod(f, poly(st["divisor"]))
            if kind in ("remainder_equals", "is_factor", "division_identity", "fraction_identity"):
                return f"除以 ${_px(st['divisor'])}$ 的商式為 ${poly_latex(q)}$、餘式為 ${poly_latex(r)}$"
            if kind in ("quotient_equals", "quotient_degree", "quotient_integer_coeffs"):
                return f"商式為 ${poly_latex(q)}$"
    if kind == "scaled_remainder_same":
        return "除式乘以非零常數後，除法原理的餘式不變"
    if kind == "scaled_quotient_same":
        return "除式乘以常數 $k$ 後，商式變為原來的 $\\frac{1}{k}$ 倍"
    if kind == "factor_product_from_zeros":
        return "相異的零點對應互質的一次因式，其乘積整除 $f(x)$"
    return ""


def _evaluate_polynomial_statements(matrix: dict[str, Any]) -> dict[str, Any]:
    from .polynomial_division_domain import _subject  # same exact helper the domain used for the subject polynomial

    givens, answer = matrix["givens"], matrix["answer"]
    subject, statements, mode = givens["subject"], givens["statements"], answer["mode"]
    named = givens.get("intro_kind") == "division_named"
    f = _subject(subject)
    f_expr = "" if f is None else _subject_expr(subject)
    sentences = [_sentence(st, named, f_expr) for st in statements]
    steps = []
    for i, (st, truth) in enumerate(zip(statements, answer["truths"]), start=1):
        detail = _statement_detail(f, st, truth)
        steps.append(f"({i}) {'正確' if truth else '錯誤'}" + (f"：{detail}。" if detail else "。"))
    if mode == "truth":
        prefix = f"若 {_t('f(x)=' + f_expr)}，則 " if f is not None else ""
        question = "下列敘述對的打「○」，錯的打「×」。\n" + prefix + sentences[0] + "。"
        truth = answer["truths"][0]
        part = _part(1, "A" if truth else "B", "choice_label_checker", "choice_label", "single_choice",
                     choices=[dict(c) for c in TRUE_FALSE_CHOICES])
        return _single_payload(matrix, question=question, part=part, display_answer="○" if truth else "×",
                               explanation_steps=[f"{steps[0][4:]}此敘述為「{'○' if truth else '×'}」。"], shape="single_choice")
    kind = givens.get("intro_kind", "about_poly")
    if kind == "about_poly":
        intro = f"關於多項式 {_t('f(x)=' + f_expr)}，選出所有正確的選項。"
    elif kind == "set_expr":
        intro = f"設 {_t('f(x)=' + f_expr)}。選出所有正確的選項。"
    elif kind == "division_named":
        intro = (f"設 {_t('f(x)=' + _px(subject['coeffs']))} 除以 {_t('g(x)=' + _px(givens['named_divisor']))} 的商式為 {_t('q(x)')}，"
                 f"餘式為 {_t('r(x)')}。\n選出所有正確的選項。")
    else:
        raise ValueError(f"unknown_statement_intro:{kind}")
    question = intro + "\n" + "\n".join(f"({i}) {s}" for i, s in enumerate(sentences, start=1))
    selected = answer["selected"]
    steps.append("正確的選項為 " + "".join(f"({i})" for i in selected) + "。")
    return _single_payload(matrix, question=question, part=_selection_part(1, selected),
                           display_answer="".join(f"({i})" for i in selected), explanation_steps=steps,
                           shape="selected_candidate_index_set")


# --- C. solve_polynomial_parameters --------------------------------------------------------------

def _solve_polynomial_parameters(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    names = list(givens["params"])
    F = lf_poly_latex(lf_poly(givens["f"]))
    stem = givens.get("stem", "identity")
    if stem == "identity":
        question = (f"已知 {_t(F)} 除以 {_t(lf_poly_latex(lf_poly(givens['d'])))} 的商式為 {_t(_px(givens['q']))}，"
                    f"餘式為 {_t(_px(givens['r']))}，求實數{', '.join(names)}的值。")
    elif stem == "remainder_quotient":
        cond = givens["conditions"][0]
        question = (f"已知 {_t(F)} 除以 {_t(_px(cond['divisor']))} 的餘式為 {_t(_px(cond['remainder']))}，"
                    f"求實數{', '.join(names)}的值及商式。")
    elif stem == "divisible_quotient":
        question = f"已知 {_t(F)} 可被 {_t(_px(givens['conditions'][0]['divisor']))} 整除，求實數 {', '.join(names)} 的值及商式。"
    elif stem == "factor_of":
        question = f"已知 {_t(_px(givens['conditions'][0]['divisor']))} 是 {_t('f(x)=' + F)} 的因式，求實數{', '.join(names)}的值。"
    elif stem == "two_conditions":
        c1, c2 = givens["conditions"]
        question = (f"已知 {_t('f(x)=' + F)} 可被 {_t(_px(c1['divisor']))} 整除，且 {_t('f(x)')} 除以 {_t(_px(c2['divisor']))} "
                    f"的餘式為 {_t(_px(c2['remainder']))}，求實數{', '.join(names)}的值。")
    elif stem == "product_form":
        question = f"已知多項式 {_t('f(x)')} 滿足 {_t('(' + _px(givens['conditions'][0]['divisor']) + ')f(x)=' + F)}，求實數 {', '.join(names)} 及 {_t('f(x)')}。"
    else:
        raise ValueError(f"unknown_parameter_stem:{stem}")
    parts = [_num_part(i, answer["params"][n], n) for i, n in enumerate(names, start=1)]
    steps = []
    if givens["form"] == "identity":
        steps.append(f"由除法原理 {_t(F + '=(' + lf_poly_latex(lf_poly(givens['d'])) + ')(' + _px(givens['q']) + ')+(' + _px(givens['r']) + ')')}，"
                     "比較等號兩邊同次項係數。")
    else:
        for c in givens["conditions"]:
            steps.append(f"以 {_t(_px(c['divisor']))} 除 {_t(F)}，餘式必為 {_t(_px(c['remainder']) if poly(c['remainder']) else '0')}，比較係數。")
    steps.append("解得 " + "、".join(f"${n}={frac_latex(fr(answer['params'][n]))}$" for n in names) + "。")
    shown = [", ".join(f"{n}={frac_text(fr(answer['params'][n]))}" for n in names)]
    if answer.get("quotient"):
        label = "f(x)" if stem == "product_form" else "商式"
        parts.append(_poly_part(len(parts) + 1, answer["quotient"], label))
        steps.append(f"商式為 ${answer['quotient']['latex']}$。")
        shown.append(f"{label} ${answer['quotient']['latex']}$")
    return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(shown),
                          explanation_steps=steps, shape="polynomial_parameters")


# --- D. taylor_shift_expansion -------------------------------------------------------------------

def _taylor_form(c: Fraction) -> str:
    base = _shift(c)
    return f"a\\left({base}\\right)^{{3}}+b\\left({base}\\right)^{{2}}+c\\left({base}\\right)+d"


def _taylor_shift_expansion(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    f, c = poly(givens["poly_coeffs"]), fr(givens["center"])
    if deg(f) != 3:
        raise ValueError("cubic_expansion_only")
    style = givens.get("style", "single")
    x0 = fr(givens["approx_x"])
    ask = f"求 {_t('f(' + _dec(x0) + ')')} 的近似值到小數點以下第二位（第三位四捨五入）"
    base_text = _shift(c)
    if style == "numbered":
        question = (f"設 {_t('f(x)=' + _px(f))}。\n(1)已知 {_t('f(x)')} 表成 {_t(base_text)} 的多項式之形式為\n"
                    f"{_t('f(x)=' + _taylor_form(c))}，\n求實數 a, b, c, d 的值。\n(2){ask}。")
        labels = ["(1) a", "(1) b", "(1) c", "(1) d", "(2) 近似值"]
    elif style == "synthetic_numbered":
        question = (f"設 {_t('f(x)=' + _px(f))}。\n(1)連續使用綜合除法，將 {_t('f(x)')} 表示成以下的形式：\n"
                    f"{_t('f(x)=' + _taylor_form(c))}，\n求實數 a, b, c, d 的值。\n(2){ask}。")
        labels = ["(1) a", "(1) b", "(1) c", "(1) d", "(2) 近似值"]
    else:
        question = (f"將 {_t('f(x)=' + _px(f))} 表示為 {_t(_taylor_form(c))} 的形式，並計算 {_t('f(' + _dec(x0) + ')')} "
                    f"的近似值到小數點以下第二位（第三位四捨五入）。")
        labels = ["a", "b", "c", "d", "近似值"]
    coeffs = answer["coefficients"]
    parts = [_num_part(i, coeffs[i - 1], labels[i - 1]) for i in range(1, 5)]
    parts.append(_num_part(5, _dec_text(fr(answer["approx"])), labels[4], "2.93"))
    steps = []
    cur = list(f)
    for layer, name in zip(range(4), ("d", "c", "b", "a")):
        from .polynomial_core import synthetic
        q, r, rows = synthetic(cur, c)
        steps.append(f"第 {layer + 1} 層：以 {_t(_shift(c))} 連續除，餘式為 ${name}={frac_latex(r)}$。")
        cur = q
    h = x0 - c
    hd = _dec(h)
    steps.append(f"{_t('f(' + _dec(x0) + ')=a(' + hd + ')^{3}+b(' + hd + ')^{2}+c(' + hd + ')+d')}，"
                 f"高次項數值很小，取 ${coeffs[2]}\\times({hd})+{coeffs[3]}$ 估計，四捨五入到小數點以下第二位得 ${_dec_text(fr(answer['approx']))}$。")
    display = "；".join([", ".join(f"{n}={coeffs[i]}" for i, n in enumerate("abcd")), f"近似值 {_dec_text(fr(answer['approx']))}"])
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps,
                          shape="taylor_shift_coefficients")


# --- E. evaluate_polynomial_values ---------------------------------------------------------------

def _numeric_expression(f: list[Fraction], x: Fraction) -> str:
    base = frac_latex(x) if x >= 0 else f"\\left({frac_latex(x)}\\right)"
    out = ""
    n = deg(f)
    for i, c in enumerate(f):
        if c == 0:
            continue
        power = n - i
        mono = "" if power == 0 else (base if power == 1 else f"{base}^{{{power}}}")
        mag = abs(c)
        term = frac_latex(mag) if power == 0 else (mono if mag == 1 else f"{frac_latex(mag)}\\times {mono}")
        out += ("-" if c < 0 else ("+" if out else "")) + term
    return out


def _evaluate_polynomial_values(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    items, values = givens["items"], answer["values"]
    style = givens.get("style", "value")
    f0 = poly(items[0]["poly"])
    if style == "value":
        question = f"已知 {_t('f(x)=' + poly_latex(f0))}，求 {_t('f(' + frac_latex(fr(items[0]['x'])) + ')')} 的值。"
    elif style == "remainder_single":
        question = f"求 {_t('f(x)=' + poly_latex(f0))} 除以 {_t(_px(items[0]['divisor']))} 的餘式。"
    elif style == "remainder_pair":
        divs = " 與 ".join(_t(_px(it["divisor"])) for it in items)
        question = f"已知 {_t('f(x)=' + poly_latex(f0))}，分別求 {_t('f(x)')} 除以 {divs} 的餘式。"
    elif style == "expression":
        question = f"計算 {_t(_numeric_expression(f0, fr(items[0]['x'])))} 的值。"
    else:
        raise ValueError(f"unknown_value_style:{style}")
    multi = len(items) > 1
    parts, steps, shown = [], [], []
    for i, (it, rec) in enumerate(zip(items, values), start=1):
        tag = f"({i}) " if multi else ""
        parts.append(_num_part(i, rec["canonical"], f"({i})" if multi else "答案"))
        v = fr(rec["canonical"])
        if it["kind"] == "remainder_linear":
            r = root_of(poly(it["divisor"]))
            fx = "f\\left(" + frac_latex(r) + "\\right)"
            steps.append(f"{tag}由餘式定理，餘式為 ${fx}={frac_latex(v)}$。")
        else:
            steps.append(f"{tag}由餘式定理，{_t('f(' + frac_latex(fr(it['x'])) + ')')} 等於 {_t('f(x)')} 除以 "
                         f"{_t(_shift(fr(it['x'])))} 的餘式。以綜合除法計算得 ${frac_latex(v)}$。")
        shown.append(f"{tag}${frac_latex(v)}$")
    return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(shown), explanation_steps=steps,
                          shape="polynomial_values")


# --- F. solve_remainder_from_conditions ----------------------------------------------------------

def _target_text(givens: dict[str, Any], answer: dict[str, Any]) -> str:
    t = poly(givens["target"])
    if givens.get("target_form", "expanded") == "factored":
        roots = [fr(r) for r in answer["roots"]]
        order = [root_of(poly(c["divisor"])) for c in givens["conditions"] if deg(poly(c["divisor"])) == 1]
        roots.sort(key=lambda r: order.index(r) if r in order else len(order))
        return "".join(f"({_shift(r)})" for r in roots)
    return poly_latex(t)


def _solve_remainder_from_conditions(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    joiner = givens.get("joiner", "；")
    clauses = []
    for i, c in enumerate(givens["conditions"]):
        rem = _px(c["remainder"]) if poly(c["remainder"]) else "0"
        lead = "除以" if i else "除以"
        clauses.append(f"{lead} {_t(_px(c['divisor']))} 的餘式為 {_t(rem)}")
    question = f"已知多項式 {_t('f(x)')} " + joiner.join(clauses) + f"，求 {_t('f(x)')} 除以 {_t(_target_text(givens, answer))} 的餘式。"
    if joiner == "，且":
        question = question.replace("，且 除以", "，且除以")
    rec = answer["remainder"]
    steps = []
    for c, v in zip(answer["roots"], answer["values"]):
        steps.append(f"由餘式定理，{_t('f(' + frac_latex(fr(c)) + ')=' + frac_latex(fr(v)))}。")
    steps.append(f"因為除式的次數為 2，所以餘式可設為 $ax+b$，代入上述兩點解得餘式為 ${rec['latex']}$。")
    part = _poly_part(1, rec, "餘式")
    return _single_payload(matrix, question=question, part=part, display_answer=f"${rec['latex']}$",
                           explanation_steps=steps, shape="polynomial_remainder")


# --- G1. solve_polynomial_from_remainder_congruences ---------------------------------------------

def _solve_polynomial_from_remainder_congruences(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    n = int(givens["degree"])
    c1, c2 = givens["conditions"][0], givens["conditions"][-1]
    question = (f"設{CN[n]}次多項式 {_t('f(x)')} 除以 {_t(_px(c1['divisor']))} 的餘式為 {_t(_px(c1['remainder']))}；"
                f"除以 {_t(_px(c2['divisor']))} 的餘式為 {_t(_px(c2['remainder']))}，求 {_t('f(x)')}。")
    rec = answer["f"]
    steps = [f"設 $f(x)$ 為{CN[n]}次多項式，各除法都滿足被除式 $=$ 除式 $\\times$ 商式 $+$ 餘式，比較兩個除法算式的係數。",
             f"解得 $f(x)={rec['latex']}$。"]
    return _single_payload(matrix, question=question, part=_poly_part(1, rec, "f(x)"), display_answer=f"${rec['latex']}$",
                           explanation_steps=steps, shape="polynomial_from_remainders")


# --- G2. solve_remainder_with_linear_part --------------------------------------------------------

def _solve_remainder_with_linear_part(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    r1, r2, r3 = (fr(r) for r in givens["roots"])
    k = fr(givens["k"])
    cubic = "".join(f"({_shift(r)})" for r in (r1, r2, r3))
    quad = "".join(f"({_shift(r)})" for r in (r1, r2))
    kk = "" if k == 1 else frac_latex(k)
    question = (f"已知多項式 {_t('f(x)')} 除以 {_t(cubic)} 的餘式為 {_t(kk + quad + '+g(x)')}，其中 {_t('g(x)')} 為一次多項式，"
                f"且 {_t('f(' + frac_latex(r1) + ')=' + frac_latex(fr(givens['first_value'])))}、"
                f"{_t('f(' + frac_latex(r3) + ')=' + frac_latex(fr(givens['last_value'])))}，求\n(1){_t('g(x)')}。\n"
                f"(2){_t('f(x)')} 除以 {_t(quad)} 的餘式。")
    g, rem = answer["g"], answer["remainder_mod_quadratic"]
    parts = [_poly_part(1, g, "(1) g(x)"), _poly_part(2, rem, "(2) 餘式")]
    steps = [f"令 ${'f(' + frac_latex(r1) + ')=g(' + frac_latex(r1) + ')=' + frac_latex(fr(givens['first_value']))}$。",
             f"${'f(' + frac_latex(r3) + ')=' + kk + '(' + frac_latex(r3 - r1) + ')(' + frac_latex(r3 - r2) + ')+g(' + frac_latex(r3) + ')=' + frac_latex(fr(givens['last_value']))}$，"
             f"解得 $g(x)={g['latex']}$。",
             f"因為 ${kk}{quad}$ 可被 ${quad}$ 整除，所以 $f(x)$ 除以 ${quad}$ 的餘式即 $g(x)$ 除以 ${quad}$ 的餘式 ${rem['latex']}$。"]
    return _parts_payload(matrix, question=question, parts=parts,
                          display_answer=f"(1) ${g['latex']}$；(2) ${rem['latex']}$", explanation_steps=steps, shape="polynomial_remainders")


# --- H. interpolate_polynomials ------------------------------------------------------------------

def _conditions_text(points: list[Any], last: str) -> str:
    groups: list[tuple[list[Fraction], Fraction]] = []
    for x, y in points:
        x, y = fr(x), fr(y)
        if groups and groups[-1][1] == y:
            groups[-1][0].append(x)
        else:
            groups.append(([x], y))
    texts = [_t("=".join(f"f({frac_latex(x)})" for x in xs) + "=" + frac_latex(y)) for xs, y in groups]
    if len(texts) == 1:
        return texts[0]
    return "、".join(texts[:-1]) + f" {last} " + texts[-1]


def _interpolate_polynomials(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    items, polys = givens["items"], answer["polys"]
    style = givens.get("style", "cubic_full")
    word = f"{CN[int(items[0]['degree'])]}次多項式"
    last = givens.get("last", "與")
    if style == "items":
        lines = [f"({i}) 已知 {_conditions_text(it['points'], last)}，求 {_t('f(x)')}。" for i, it in enumerate(items, start=1)]
        question = f"設 {_t('f(x)')} 為{word}。\n" + "\n".join(lines)
    elif style == "is_cubic":
        question = f"已知 {_t('f(x)')} 是{word}，滿足 {_conditions_text(items[0]['points'], last)}，求 {_t('f(x)')}。"
    else:
        question = f"已知{word} {_t('f(x)')} 滿足 {_conditions_text(items[0]['points'], last)}，求 {_t('f(x)')}。"
    multi = len(items) > 1
    parts = [_poly_part(i, rec, f"({i}) f(x)" if multi else "f(x)") for i, rec in enumerate(polys, start=1)]
    steps = []
    for i, (it, rec) in enumerate(zip(items, polys), start=1):
        tag = f"({i}) " if multi else ""
        pts = [(fr(x), fr(y)) for x, y in it["points"]]
        zeros = [x for x, y in pts if y == 0]
        if zeros:
            facs = "".join(f"({_shift(z)})" for z in zeros)
            steps.append(f"{tag}由因式定理，${facs}$ 是 $f(x)$ 的因式，再由其餘條件確定其餘因式的係數。")
        else:
            steps.append(f"{tag}利用各已知點的函數值，逐步由因式定理與除法原理求出各項係數。")
        steps.append(f"{tag}得 $f(x)={rec['latex']}$。")
    return _parts_payload(matrix, question=question, parts=parts,
                          display_answer="；".join(f"${r['latex']}$" for r in polys), explanation_steps=steps,
                          shape="interpolated_polynomials")


# --- I. select_linear_factors --------------------------------------------------------------------

def _select_linear_factors(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    f = poly(givens["poly_coeffs"])
    cands = givens["candidates"]
    question = f"選出 {_t('f(x)=' + poly_latex(f))} 的因式。\n" + " ".join(f"({i}){_t(_px(c))}" for i, c in enumerate(cands, start=1)) + "。"
    steps = ["利用因式定理判定：若 $ax-b$ 是 $f(x)$ 的因式，則 $f\\left(\\frac{b}{a}\\right)=0$。"]
    for i, (c, ok) in enumerate(zip(cands, answer["truths"]), start=1):
        r = root_of(poly(c))
        steps.append(f"({i}) $f\\left({frac_latex(r)}\\right)={frac_latex(ev(f, r))}$，" + ("所以是因式。" if ok else "所以不是因式。"))
    steps.append("正確的選項為 " + "".join(f"({i})" for i in answer["selected"]) + "。")
    return _single_payload(matrix, question=question, part=_selection_part(1, answer["selected"]),
                           display_answer="".join(f"({i})" for i in answer["selected"]), explanation_steps=steps,
                           shape="selected_candidate_index_set")


# --- J. solve_erased_cubic -----------------------------------------------------------------------

def _solve_erased_cubic(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    lead = poly(list(givens["known"]) + [0])
    r = fr(givens["root"])
    board = poly_latex(lead) + "+" + SQUARE
    question = (f"小明上數學課時一時恍神，回神後發現老師已將三次多項式的常數項擦掉了，黑板上寫著「因式分解 "
                f"{_t(board)}」（{_t(SQUARE)} 為被擦掉的常數項）。還好老師邊擦邊提示說：「這多項式有因式 "
                f"{_t(_shift(r))}。」。根據這個提示，請幫小明解決下列問題。\n(1)求該三次多項式。\n(2)解出這道題目。")
    cubic = answer["poly"]
    parts = [
        _poly_part(1, cubic, "(1) 三次多項式"),
        _part(2, answer["factored_plain"], *_FACTORED, label="(2) 因式分解", prompt="(2) 因式分解", required_form="fully_factorized"),
    ]
    k = fr(answer["k"])
    steps = [f"(1) 設該三次多項式為 ${poly_latex(lead)}+k$。利用因式定理，得 $f({frac_latex(r)})=0$，解得 $k={frac_latex(k)}$。"
             f"故該三次多項式為 ${cubic['latex']}$。"]
    from .polynomial_core import synthetic
    q, rem, rows = synthetic(poly(cubic["coeffs"]), r)
    steps.append("(2) 利用綜合除法，計算該多項式除以 " + _t(_shift(r)) + "：" + f"${_rows_array([[frac_text(c) for c in row] for row in rows], frac_text(r))}$"
                 + f"得商式 ${poly_latex(q)}$，再將商式因式分解，得 ${''.join('(' + _shift(fr(x)) + ')' for x in answer['roots'])}$。")
    factored_latex = "".join("(" + _shift(fr(x)) + ")" for x in answer["roots"])
    return _parts_payload(matrix, question=question, parts=parts,
                          display_answer=f"(1) ${cubic['latex']}$；(2) ${factored_latex}$", explanation_steps=steps,
                          shape="erased_cubic")


# --- K. solve_masked_synthetic_coefficient -------------------------------------------------------

def _solve_masked_synthetic_coefficient(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    coeffs = givens["coefficients"]
    n = len(coeffs) - 1
    idx = int(givens["mask_index"])
    r = fr(givens["root"])
    top = " & ".join("\\bullet" if i == idx else _signed(frac_text(fr(c)), i) for i, c in enumerate(coeffs))
    blanks = " & ".join(SQUARE for _ in range(n))
    rem_cell = _signed(frac_text(fr(givens["remainder"])), 1)
    table = (f"\\begin{{array}}{{r{'r' * n}|r|r}} & {top} & {frac_latex(r)} \\\\ +) & & {blanks} & \\\\ \\hline "
             f"& {blanks} & {rem_cell} & \\end{{array}}")
    question = (f"下列為老師使用綜合除法，計算完一個{CN[n]}次多項式除以 {_t(_shift(r))} 的算式後，用立可帶及黑筆遮掉部分算式的有獎徵答題。"
                f"已知老師沒有計算錯誤，請問：黑圈圈蓋掉的數字為何？\n{_t(table)}")
    value = fr(answer["value"]["canonical"])
    rows = answer["rows"]
    steps = [f"由餘式定理，餘式 $f({frac_latex(r)})={frac_latex(fr(givens['remainder']))}$，其中 $f(x)$ 的係數依序為被遮住的數字與其餘各數。",
             f"代入並解一次方程式，得被遮住的數字為 ${frac_latex(value)}$。",
             "完整綜合除法算式如下：$" + _rows_array(rows, frac_text(r)) + "$"]
    return _single_payload(matrix, question=question, part=_num_part(1, answer["value"]["canonical"], "答案"),
                           display_answer=f"${frac_latex(value)}$", explanation_steps=steps, shape="masked_synthetic")


# --- M. solve_divisor_from_quotient_remainder ----------------------------------------------------

def _solve_divisor_from_quotient_remainder(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    question = (f"已知 {_t(_px(givens['dividend']))} 除以 {_t('g(x)')} 的商式為 {_t(_px(givens['quotient']))}，"
                f"餘式為 {_t(_px(givens['remainder']))}，求 {_t('g(x)')}。")
    g = answer["divisor"]
    steps = [f"由除法原理，被除式 $=$ 除式 $\\times$ 商式 $+$ 餘式，所以 $g(x)=\\left({_px(givens['dividend'])}-({_px(givens['remainder'])})\\right)\\div({_px(givens['quotient'])})$。",
             f"計算得 $g(x)={g['latex']}$。"]
    return _single_payload(matrix, question=question, part=_poly_part(1, g, "g(x)"), display_answer=f"${g['latex']}$",
                           explanation_steps=steps, shape="polynomial_divisor")


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "polynomial_arithmetic_items": _polynomial_arithmetic_items,
    "evaluate_polynomial_statements": _evaluate_polynomial_statements,
    "solve_polynomial_parameters": _solve_polynomial_parameters,
    "taylor_shift_expansion": _taylor_shift_expansion,
    "evaluate_polynomial_values": _evaluate_polynomial_values,
    "solve_remainder_from_conditions": _solve_remainder_from_conditions,
    "solve_polynomial_from_remainder_congruences": _solve_polynomial_from_remainder_congruences,
    "solve_remainder_with_linear_part": _solve_remainder_with_linear_part,
    "interpolate_polynomials": _interpolate_polynomials,
    "select_linear_factors": _select_linear_factors,
    "solve_erased_cubic": _solve_erased_cubic,
    "solve_masked_synthetic_coefficient": _solve_masked_synthetic_coefficient,
    "solve_divisor_from_quotient_remainder": _solve_divisor_from_quotient_remainder,
}


def adapt_polynomial_division_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_polynomial_division_operation:{operation}")
    return builder(matrix)
