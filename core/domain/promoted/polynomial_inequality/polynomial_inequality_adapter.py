"""Question payload contracts for inequality.polynomial (普高數學1 Unit 11, 多項式不等式).

Every expected answer comes from the domain matrix, never from this adapter.  Stems and figures are rebuilt from the
same givens, so a varied question never shows a stale picture: the schematic figures (triangle leather, square, plot
with path, box frame) carry the numbers of the variant, and the function graphs are the sampled curve of the domain.
"""

from __future__ import annotations

from typing import Any, Callable

import sympy as sp

from core.domain.promoted.analytic_geometry_lines import figures as FG

from .polynomial_inequality_domain import DOMAIN_KEY, _claim_set, _q, graph_curve, set_latex

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
_INEQ = ("inequality_solution_checker", "inequality_solution_equivalence", "inequality")
_EXPR = ("expression_checker", "algebraic_equivalent", "expression")
_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_SET = ("solution_set_checker", "unordered_solution_set", "solution_set")
_EQUATION = ("equation_checker", "equation_equivalent", "equation")
_REL_TEX = {">": ">", "<": "<", ">=": "\\ge ", "<=": "\\le "}
_DEGREE_WORD = {3: "三", 4: "四", 5: "五", 6: "六"}
_CURVE_COLOR = "#1565c0"
# LaTeX tokens are module constants: a backslash may not appear inside an f-string expression on Python 3.11
_LE, _GE, _OR, _TIMES, _FRAC = "\\le ", "\\ge ", "\\text{ 或 }", "\\times ", "\\frac"
_LEFT, _RIGHT, _CDOT = "\\left(", "\\right)", "\\cdot "


# --- contracts (same shape as the other general-high adapters) ------------------------------------

def _contract(answer_type: str, presentation_mode: str, checker: str, equivalence: str, **extra: Any) -> dict[str, Any]:
    return {
        "presentation_mode": presentation_mode, "answer_type": answer_type, "checker": checker, "checker_key": checker,
        "answer_equivalence": equivalence, "equivalence": equivalence, "equivalence_type": equivalence, **extra,
    }


def _part(index: int, expected: Any, checker: str, equivalence: str, answer_type: str, **extra: Any) -> dict[str, Any]:
    return {"key": f"part_{index}", "label": f"({index})", "checker": checker, "checker_key": checker, "equivalence_type": equivalence,
            "answer_type": answer_type, "expected_answer": expected, **extra}


def _payload(matrix, *, question, answer, display_answer, contract, explanation_steps, choices=(), visual_spec=None) -> dict[str, Any]:
    operation = matrix["domain_operation"]
    payload = {
        "question_text": question, "question": question, "answer": answer, "correct_answer": answer, "display_answer": display_answer,
        "semantic_answer": matrix["answer"], "answer_type": contract["answer_type"], "presentation_mode": contract["presentation_mode"],
        "problem_type_id": operation, "domain_operation": operation, "fixed_domain_key": DOMAIN_KEY,
        "answer_contract": {**contract, "semantic_answer": matrix["answer"]}, "explanation_steps": explanation_steps,
        "choices": [dict(c) for c in choices], "options": [dict(c) for c in choices],
        "math_core": {"givens": matrix["givens"], "target": matrix["answer"], "validation_facts": matrix["validation_facts"]},
    }
    if visual_spec:
        payload["visual_spec"] = visual_spec
        payload["visual_backed"] = bool(visual_spec.get("render_required"))
    return payload


def _single_payload(matrix, *, question, part, display_answer, explanation_steps, shape, visual_spec=None) -> dict[str, Any]:
    skip = ("key", "label", "checker", "checker_key", "equivalence_type", "answer_type", "expected_answer", "prompt")
    extra = {k: v for k, v in part.items() if k not in skip}
    if part["answer_type"] == "single_choice":
        return _payload(matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
                        contract=_contract("single_choice", "single_choice", "choice_label_checker", "choice_label",
                                           answer_shape="single_choice", choices=[dict(c) for c in part["choices"]]),
                        explanation_steps=explanation_steps, choices=part["choices"], visual_spec=visual_spec)
    return _payload(matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
                    contract=_contract(part["answer_type"], "short_answer", part["checker"], part["equivalence_type"], answer_shape=shape, **extra),
                    explanation_steps=explanation_steps, visual_spec=visual_spec)


def _parts_payload(matrix, *, question, parts, display_answer, explanation_steps, shape, visual_spec=None) -> dict[str, Any]:
    if len(parts) == 1:
        return _single_payload(matrix, question=question, part=parts[0], display_answer=display_answer,
                               explanation_steps=explanation_steps, shape=shape, visual_spec=visual_spec)
    return _payload(matrix, question=question, answer={p["key"]: p["expected_answer"] for p in parts}, display_answer=display_answer,
                    contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer", answer_shape=shape, parts=parts),
                    explanation_steps=explanation_steps, visual_spec=visual_spec)


def _t(text: str) -> str:
    return f"${text}$"


def _ineq_part(index: int, canonical: str, label: str = "") -> dict[str, Any]:
    extra = {"label": label, "prompt": label} if label else {}
    return _part(index, canonical, *_INEQ, **extra)


def _num_part(index: int, canonical: str, label: str) -> dict[str, Any]:
    return _part(index, canonical, *_RATIONAL, label=label, prompt=label)


def _choice_part(index: int, expected_label: str, choices: list[dict[str, str]], label: str = "") -> dict[str, Any]:
    extra = {"label": label, "prompt": label} if label else {}
    return _part(index, expected_label, "choice_label_checker", "choice_label", "single_choice", choices=[dict(c) for c in choices], **extra)


# --- LaTeX helpers -------------------------------------------------------------------------------

def _poly_tex(coeffs: list[Any], var: str = "x") -> str:
    n = len(coeffs) - 1
    out = ""
    for i, c in enumerate(coeffs):
        v = _q(c)
        if v == 0:
            continue
        power = n - i
        neg = bool(v < 0)
        mag = -v if neg else v
        coef = "" if (mag == 1 and power > 0) else sp.latex(mag)
        tail = var if power == 1 else (f"{var}^{{{power}}}" if power > 1 else "")
        out += ("-" if neg else ("+" if out else "")) + coef + tail
    return out or "0"


def _factor_tex(factor: dict[str, Any]) -> str:
    base = _poly_tex(factor["lin"] if "lin" in factor else factor["quad"])
    mult = int(factor.get("mult", 1))
    return f"\\left({base}\\right)" + (f"^{{{mult}}}" if mult > 1 else "")


def _side_tex(side: dict[str, Any]) -> str:
    if "poly" in side:
        return _poly_tex(side["poly"])
    coef = _q(side.get("coef", 1))
    body = "".join(_factor_tex(f) for f in side["factors"])
    if coef == 1:
        return body
    return ("-" if coef == -1 else sp.latex(coef)) + body


def _ineq_tex(item: dict[str, Any]) -> str:
    return f"{_side_tex(item['left'])}{_REL_TEX[item['rel']]}{_side_tex(item.get('right', {'poly': [0]}))}"


def _num_tex(v: Any) -> str:
    return sp.latex(_q(v))


def _signed_tex(v: Any) -> str:
    q = _q(v)
    mag = -q if q < 0 else q
    return ("-" if q < 0 else "+") + ("" if mag == 1 else sp.latex(mag))


def _claim_text(claim: str) -> str:
    parsed = _claim_set(claim)
    if parsed == sp.S.Reals:
        return "所有實數"
    if parsed == sp.S.EmptySet:
        return "無解"
    return _t(set_latex(parsed))


def _steps_for_solving(item: dict[str, Any], rec: dict[str, Any], label: str = "") -> str:
    head = f"{label} " if label else ""
    roots = rec["roots"]
    if not roots:
        words = f"{_t(rec['difference_latex'] + '=0')} 沒有實數根，{_t(rec['difference_latex'])} 恆正或恆負（用配方法或判別式判斷），"
    else:
        words = (f"整理成 {_t(rec['difference_latex'] + _REL_TEX[item['rel']] + '0')}，因式分解得 {_t(rec['factored'] + _REL_TEX[item['rel']] + '0')}，"
                 + "各實根為 " + "、".join(_t(r["latex"]) for r in roots) + "，重根不變號、偶次因式不改變符號，畫出正負號表，")
    return f"{head}{words}解為 {_t(rec['solution']['latex'])}。" if rec["solution"]["canonical"] not in ("全體實數", "無解") else \
        f"{head}{words}解為{rec['solution']['canonical']}。"


def _display(rec: dict[str, Any]) -> str:
    return rec["solution"]["canonical"].replace("<=", "≤").replace(">=", "≥").replace(" or ", " 或 ")


# --- A. solve_polynomial_inequality ------------------------------------------------------------------

def _solve_inequalities(matrix: dict[str, Any]) -> dict[str, Any]:
    items, recs = matrix["givens"]["items"], matrix["answer"]["items"]
    many = len(items) > 1
    degrees = {r["degree"] for r in recs}
    kind = {1: "一次", 2: "二次"}.get(next(iter(degrees)) if len(degrees) == 1 else 0, "")
    if many:
        question = f"解下列{kind}不等式：\n" if kind else "解下列不等式：\n"
        question += "\n".join(f"({i}) {_t(_ineq_tex(it))}。" for i, it in enumerate(items, start=1))
    else:
        question = f"解{kind}不等式 {_t(_ineq_tex(items[0]))}。" if kind else f"解不等式 {_t(_ineq_tex(items[0]))}。"
    parts = [_ineq_part(i, r["solution"]["canonical"], f"({i})" if many else "") for i, r in enumerate(recs, start=1)]
    steps = [_steps_for_solving(it, r, f"({i})" if many else "") for i, (it, r) in enumerate(zip(items, recs), start=1)]
    shown = "；".join((f"({i}) " if many else "") + _display(r) for i, r in enumerate(recs, start=1))
    return _parts_payload(matrix, question=question, parts=parts, display_answer=shown, explanation_steps=steps, shape="inequality_solution_set")


# --- B. polynomial_inequality_parameters ----------------------------------------------------------------

def _between_text(r1: Any, r2: Any, strict: bool) -> str:
    op = "<" if strict else "\\le "
    return f"{_num_tex(r1)}{op}x{op}{_num_tex(r2)}"


def _polynomial_inequality_parameters(matrix: dict[str, Any]) -> dict[str, Any]:
    it, rec = matrix["givens"]["items"][0], matrix["answer"]["items"][0]
    kind = it["kind"]
    if kind == "quad_from_solution":
        strict = it["rel"] in (">", "<")
        r1, r2 = sorted((_q(r) for r in it["roots"]), key=float)
        lo_op, hi_op = ("<", ">") if strict else (_LE, _GE)
        sol = _between_text(r1, r2, strict) if it["shape"] == "between" else f"x{lo_op}{_num_tex(r1)}{_OR}x{hi_op}{_num_tex(r2)}"
        ineq = f"ax^{{2}}{_signed_tex(it['p'])}x+b{_REL_TEX[it['rel']]}0"
        question = f"已知不等式 {_t(ineq)} 的解為 {_t(sol)}，求實數 {_t('a, b')} 的值。"
        parts = [_num_part(1, rec["a"]["canonical"], "a"), _num_part(2, rec["b"]["canonical"], "b")]
        eq_tex = _t("ax^{2}" + _signed_tex(it["p"]) + "x+b=0")
        sum_tex = _t(_num_tex(r1 + r2) + "=-" + _FRAC + "{" + _signed_tex(it["p"]) + "}{a}")
        prod_tex = _t(_num_tex(r1 * r2) + "=" + _FRAC + "{b}{a}")
        steps = [f"解為 {_t(sol)}，表示 {_t(_num_tex(r1))}、{_t(_num_tex(r2))} 是 {eq_tex} 的兩根。",
                 f"根與係數：兩根和 {sum_tex}，得 $a={rec['a']['latex']}$；",
                 f"兩根積 {prod_tex}，得 $b={rec['b']['latex']}$。"]
        shown = f"a={rec['a']['canonical']}，b={rec['b']['canonical']}"
    elif kind == "cubic_from_solution":
        strict = it["rel"] in (">", "<")
        r1, r2, r3 = sorted((_q(r) for r in it["roots"]), key=float)
        le, ge, lt, gt = ("<", ">", "<", ">") if strict else ("\\le ", "\\ge ", "\\le ", "\\ge ")
        if it["form"] == "low":
            sol = f"x{lt}{_num_tex(r1)}\\text{{ 或 }}{_num_tex(r2)}{le}x{le}{_num_tex(r3)}"
        else:
            sol = f"{_num_tex(r1)}{le}x{le}{_num_tex(r2)}\\text{{ 或 }}x{gt}{_num_tex(r3)}"
        ineq = f"ax^{{3}}+bx^{{2}}+cx{_signed_tex(it['d'])}{_REL_TEX[it['rel']]}0"
        question = f"已知三次不等式 {_t(ineq)} 的解為 {_t(sol)}，求實數 {_t('a, b, c')} 的值。"
        parts = [_num_part(1, rec["a"]["canonical"], "a"), _num_part(2, rec["b"]["canonical"], "b"), _num_part(3, rec["c"]["canonical"], "c")]
        steps = [f"解的端點 {_t(_num_tex(r1))}、{_t(_num_tex(r2))}、{_t(_num_tex(r3))} 是三次方程式的三根，所以可設 "
                 + _t(f"a\\left(x{_signed_tex(-r1)}\\right)\\left(x{_signed_tex(-r2)}\\right)\\left(x{_signed_tex(-r3)}\\right)"),
                 f"常數項 {_t('-a(' + _num_tex(r1 * r2 * r3) + ')=' + _num_tex(it['d']))}，得 $a={rec['a']['latex']}$；",
                 f"展開比較係數得 $b={rec['b']['latex']}$、$c={rec['c']['latex']}$。"]
        shown = f"a={rec['a']['canonical']}，b={rec['b']['canonical']}，c={rec['c']['canonical']}"
    elif kind == "always_true":
        a = _q(it["a"])
        lin = _lin_k_tex(it["b1"], it["b0"])
        con = _lin_k_tex(it["c1"], it["c0"])
        poly = ("" if a == 1 else sp.latex(a)) + "x^{2}" + _coef_x(lin) + _const_term(con)
        ge0 = _t(poly + _GE + "0")
        d_le0 = _t("D" + _LE + "0")
        question = f"已知二次不等式 {ge0} 的解為全體實數，求實數 {_t('k')} 的範圍。"
        parts = [_ineq_part(1, rec["k"]["canonical"])]
        parts[0]["answer_format_example"] = "1<=k<=4"
        steps = [f"二次項係數 $a={sp.latex(a)}>0$，圖形開口向上，要使 {ge0} 對所有實數 $x$ 都成立，判別式需 $D\\le 0$。",
                 f"解 {d_le0}，得 {_t(rec['k']['latex'])}。"]
        shown = rec["k"]["canonical"].replace("<=", "≤").replace(">=", "≥").replace(" or ", " 或 ")
    elif kind == "quad_factor_param":
        strict = it["rel"] in (">", "<")
        r1, r2 = sorted((_q(r) for r in it["roots"]), key=float)
        lo_op, hi_op = ("<", ">") if strict else (_LE, _GE)
        sol = _between_text(r1, r2, strict) if it["shape"] == "between" else f"x{lo_op}{_num_tex(r1)}{_OR}x{hi_op}{_num_tex(r2)}"
        pos_tex = _LEFT + _poly_tex(it["pos"]) + _RIGHT
        ineq_tex = _t(pos_tex + _LEFT + "x^{2}+ax+b" + _RIGHT + _REL_TEX[it["rel"]] + "0")
        question = f"已知 {_t('a, b')} 為實數，且不等式 {ineq_tex} 的解為 {_t(sol)}，求 {_t('a, b')} 的值。"
        factored_tex = _t("x^{2}+ax+b=" + _LEFT + "x" + _signed_tex(-r1) + _RIGHT + _LEFT + "x" + _signed_tex(-r2) + _RIGHT)
        parts = [_num_part(1, rec["a"]["canonical"], "a"), _num_part(2, rec["b"]["canonical"], "b")]
        disc = _q(it["pos"][1]) ** 2 - 4 * _q(it["pos"][0]) * _q(it["pos"][2])
        steps = [f"{_t(_poly_tex(it['pos']))} 的判別式 {_t('D=' + _num_tex(disc) + '<0')} 且領先係數為正，恆為正數，所以不等式的正負只由 {_t('x^{2}+ax+b')} 決定。",
                 f"因此 {_t('x^{2}+ax+b' + _REL_TEX[it['rel']] + '0')} 的解為 {_t(sol)}，兩根為 {_t(_num_tex(r1))}、{_t(_num_tex(r2))}，"
                 f"{factored_tex}。",
                 f"展開比較係數得 $a={rec['a']['latex']}$、$b={rec['b']['latex']}$。"]
        shown = f"a={rec['a']['canonical']}，b={rec['b']['canonical']}"
    else:  # monic_compare
        f_pos = rec["f_positive"]
        g = it["g"]
        question = (f"已知 {_t('f(x)')} 是首項係數為 $1$ 的三次多項式，且不等式 {_t('f(x)>0')} 的解為 {_t(f_pos['latex'])}，"
                    f"求不等式 {_t('f(x)' + _REL_TEX[it['rel']] + _poly_tex(g))} 的解。")
        parts = [_ineq_part(1, rec["solution"]["canonical"])]
        pairs = [(_q(r), int(m)) for r, m in it["roots"]]
        fact = "".join(f"\\left(x{_signed_tex(-r)}\\right)" + (f"^{{{m}}}" if m > 1 else "") if r != 0 else ("x" + (f"^{{{m}}}" if m > 1 else "")) for r, m in pairs)
        steps = [f"由 {_t('f(x)>0')} 的解知 {_t('f(x)=' + fact)}（有重根的根不改變 $f$ 的正負號）。",
                 f"{_t('f(x)' + _REL_TEX[it['rel']] + _poly_tex(g))} 移項整理並因式分解，畫正負號表，得解為 {_t(rec['solution']['latex'])}。"]
        shown = rec["solution"]["canonical"].replace("<=", "≤").replace(">=", "≥").replace(" or ", " 或 ")
    return _parts_payload(matrix, question=question, parts=parts, display_answer=shown, explanation_steps=steps, shape="polynomial_inequality_parameters")


def _lin_k_tex(m: Any, n: Any) -> str:
    return _poly_tex([m, n], "k")


def _coef_x(lin: str) -> str:
    if lin in ("0",):
        return ""
    if lin == "1":
        return "+x"
    if lin == "-1":
        return "-x"
    two_term = ("+" in lin[1:]) or ("-" in lin[1:])
    inner = f"\\left({lin}\\right)" if two_term else lin
    return ("+" if not inner.startswith("-") else "") + inner + "x"


def _const_term(lin: str) -> str:
    if lin == "0":
        return ""
    return lin if lin.startswith("-") else "+" + lin


# --- C. polynomial_statements ------------------------------------------------------------------------

def _statement_sentence(st: dict[str, Any]) -> str:
    kind = st["kind"]
    if kind == "solution_claim":
        return f"不等式 {_t(_ineq_tex(st['ineq']))} 的解為 {_claim_text(st['claim'])}"
    if kind == "same_solution":
        return f"不等式 {_t(_ineq_tex(st['a']))} 與 {_t(_ineq_tex(st['b']))} 有相同的解"
    if kind == "coefficient_sign":
        return _t(f"{st['name']}{'>' if st['sign'] == '+' else '<'}0")
    return _t("a+b+c+d>0")


def _statement_reason(st: dict[str, Any], truth: bool, answer: dict[str, Any]) -> str:
    kind = st["kind"]
    if kind == "solution_claim":
        return "把不等式因式分解後畫正負號表，所得的解與敘述比較，" + ("相同。" if truth else "不同。")
    if kind == "same_solution":
        return "兩個不等式各自解出解集合再比較（兩邊同乘負數要改變不等號方向，恆正的因式可約去），" + ("解集合相同。" if truth else "解集合不同。")
    table = answer["coefficients"]
    if kind == "coefficient_sign":
        return f"由三個根與圖形開口得 $f(x)=a(x-r_1)(x-r_2)(x-r_3)$，展開後 ${st['name']}={table[st['name']]}$。"
    return f"$a+b+c+d=f(1)={table['sum']}$。"


def _roots_figure(roots: list[Any], lead: Any, mult: list[int] | None = None, label_roots: bool = True) -> dict[str, Any]:
    pairs = [[r, (mult[i] if mult else 1)] for i, r in enumerate(roots)]
    curve, window = graph_curve(pairs, lead)
    xs = [float(_q(r)) for r in roots]
    view = FG.fit_view([(window["x"][0], -window["y"]), (window["x"][1], window["y"])], pad=0, include_origin=True)
    points = [FG.point_entry((x, 0), (f"{sp.latex(_q(r))}".replace("\\frac", "") if label_roots else "")) for x, r in zip(xs, roots)]
    if label_roots:
        points = [FG.point_entry((x, 0), str(_q(r))) for x, r in zip(xs, roots)]
    return FG.plane(points=points, lines=[], view=view, extra={"show_grid": False, "curves": [{"points": curve, "color": _CURVE_COLOR}]})


def _polynomial_statements(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    sts, mode, subject = givens["statements"], answer["mode"], givens.get("subject") or {}
    if mode == "truth":
        truth = answer["truths"][0]
        question = "下列敘述對的打「○」，錯的打「×」。\n" + _statement_sentence(sts[0]) + "。"
        part = _choice_part(1, "A" if truth else "B", [dict(c) for c in TRUE_FALSE_CHOICES])
        steps = [f"{_statement_reason(sts[0], truth, answer)}此敘述為「{'○' if truth else '×'}」。"]
        return _single_payload(matrix, question=question, part=part, display_answer="○" if truth else "×", explanation_steps=steps, shape="single_choice")
    roots = [_q(r) for r in subject["roots"]]
    triple = "、".join(_t(f"({sp.latex(r)},0)") for r in roots[:-1]) + f"與{_t('(' + sp.latex(roots[-1]) + ',0)')}"
    question = (f"如右圖，三次函數 {_t('f(x)=ax^{3}+bx^{2}+cx+d')} 的圖形通過 {triple} 三點，選出所有正確的選項。\n"
                + "\n".join(f"({i}) {_statement_sentence(st)}" + ("。" if i == len(sts) else "") for i, st in enumerate(sts, start=1)))
    steps = [f"({i}) {'正確' if t else '錯誤'}。{_statement_reason(st, t, answer)}" for i, (st, t) in enumerate(zip(sts, answer["truths"]), start=1)]
    steps.append("正確的選項為 " + "".join(f"({i})" for i in answer["selected"]) + "。")
    if not answer["selected"]:
        raise ValueError("selection_needs_at_least_one_correct_option")
    part = _part(1, list(answer["selected"]), *_SET, solution_members="exact_rational", answer_format_example="2, 4")
    return _single_payload(matrix, question=question, part=part, display_answer="".join(f"({i})" for i in answer["selected"]),
                           explanation_steps=steps, shape="selected_candidate_index_set", visual_spec=_roots_figure(roots, subject["lead"], label_roots=False))


# --- D. polynomial_applications ----------------------------------------------------------------------

def _seg(p: Any, q: Any, label: str = "", dashed: bool = False) -> dict[str, Any]:
    return FG.through_line(p, q, label=label, extend=False, dashed=dashed)


def _schematic(points: list[dict[str, Any]], lines: list[dict[str, Any]], corners: list[tuple[float, float]]) -> dict[str, Any]:
    view = FG.fit_view(corners, pad=1, include_origin=True)
    return FG.plane(points=points, lines=lines, view=view, extra={"show_grid": False})


def _box_wire(x0: float, y0: float, a: float, depth: float, h: float, x_label: bool, y_label: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[tuple[float, float]]]:
    """Oblique wire frame of a box with a square base (edge ``a``) and height ``h``; one x edge and one y edge are labelled."""
    f0, f1 = (x0, y0), (x0 + a, y0)
    b0, b1 = (x0 + depth, y0 + depth), (x0 + a + depth, y0 + depth)
    t = lambda p: (p[0], p[1] + h)  # noqa: E731
    lines = [_seg(f0, f1, "x" if x_label else ""), _seg(f1, b1, "x" if x_label else ""), _seg(b1, b0, dashed=True), _seg(b0, f0, dashed=True),
             _seg(t(f0), t(f1)), _seg(t(f1), t(b1)), _seg(t(b1), t(b0)), _seg(t(b0), t(f0)),
             _seg(f0, t(f0), "y" if y_label else ""), _seg(f1, t(f1)), _seg(b1, t(b1)), _seg(b0, t(b0), dashed=True)]
    return [], lines, [f0, t(b1)]


def _application_figure(it: dict[str, Any]) -> dict[str, Any] | None:
    kind = it["kind"]
    if kind == "triangle_rectangle":
        B, H = float(_q(it["B"])), float(_q(it["H"]))
        pts = [FG.point_entry((B / 2, 0), str(_q(it["B"]))), FG.point_entry((B / 2, H / 2), "x")]
        lines = [_seg((0, 0), (B, 0)), _seg((B, 0), (B / 2, H)), _seg((B / 2, H), (0, 0)), _seg((B / 2, 0), (B / 2, H), str(_q(it["H"])), dashed=True),
                 _seg((B / 4, 0), (3 * B / 4, 0)), _seg((3 * B / 4, 0), (3 * B / 4, H / 2)), _seg((3 * B / 4, H / 2), (B / 4, H / 2)), _seg((B / 4, H / 2), (B / 4, 0))]
        return _schematic(pts, lines, [(0, 0), (B, H)])
    if kind == "square_corner":
        s = float(_q(it["s"]))
        pts = [FG.point_entry(p, n) for p, n in (((0, 0), "A"), ((s, 0), "B"), ((s, s), "C"), ((0, s), "D"), ((s / 2, 0), "P"), ((s, s / 2), "Q"))]
        lines = [_seg((0, 0), (s, 0)), _seg((s, 0), (s, s)), _seg((s, s), (0, s)), _seg((0, s), (0, 0)), _seg((s / 2, 0), (s, s / 2)), _seg((s / 2, 0), (0, s))]
        return _schematic(pts, lines, [(0, 0), (s, s)])
    if kind == "path_around_plot":
        W, L = float(_q(it["W"])), float(_q(it["L"]))
        d = min(W, L) / 6
        lines = [_seg((0, 0), (W, 0)), _seg((W, 0), (W, L)), _seg((W, L), (0, L)), _seg((0, L), (0, 0)),
                 _seg((d, d), (W - d, d), dashed=True), _seg((W - d, d), (W - d, L - d), dashed=True), _seg((W - d, L - d), (d, L - d), dashed=True), _seg((d, L - d), (d, d), dashed=True)]
        pts = [FG.point_entry((W / 2, L), str(_q(it["W"]))), FG.point_entry((W, L / 2), str(_q(it["L"]))), FG.point_entry((d / 2, L / 2), "x")]
        return _schematic(pts, lines, [(0, 0), (W, L)])
    if kind in ("frame_box", "open_box"):
        _p, lines, corners = _box_wire(1.0, 1.0, 5.0, 2.0, 3.5, True, True)
        return _schematic([], lines, corners)
    if kind == "tent_prism":
        lines, corners = _tent_wire(*(_num_tex(v) for v in it["triple"]))
        return _schematic([], lines, corners)
    return None


def _tent_wire(p: str, q: str, r: str) -> tuple[list[dict[str, Any]], list[tuple[float, float]]]:
    """Oblique wire frame of a right-triangle prism: sides px (vertical), qx (horizontal), rx (slanted) and three edges y."""
    a, b, c = (1.0, 1.0), (5.0, 1.0), (1.0, 4.0)
    dx, dy = 1.6, 1.2
    a2, b2, c2 = (a[0] + dx, a[1] + dy), (b[0] + dx, b[1] + dy), (c[0] + dx, c[1] + dy)
    lines = [_seg(a, c, f"{p}x"), _seg(a, b, f"{q}x"), _seg(b, c, f"{r}x"),
             _seg(a2, c2, dashed=True), _seg(a2, b2, dashed=True), _seg(b2, c2),
             _seg(a, a2, "y", dashed=True), _seg(b, b2), _seg(c, c2)]
    return lines, [a, b2, c2]


def _inequality_tail(rec: dict[str, Any]) -> tuple[str, str]:
    return rec["solution"]["canonical"], rec["solution"]["latex"]


def _fraction_words(share: Any) -> str:
    q = _q(share)
    return "一半" if q == sp.Rational(1, 2) else _t(sp.latex(q))


def _polynomial_applications(matrix: dict[str, Any]) -> dict[str, Any]:
    it, rec = matrix["givens"]["items"][0], matrix["answer"]["items"][0]
    kind = it["kind"]
    canonical, latex = _inequality_tail(rec)
    figure = _application_figure(it)
    sol_words = _display(rec)
    if kind == "triangle_rectangle":
        B, H, A = (_num_tex(it[k]) for k in ("B", "H", "A"))
        base = f"底邊長與底邊上的高都是 ${B}$" if _q(it["B"]) == _q(it["H"]) else f"底邊長是 ${B}$、底邊上的高是 ${H}$"
        question = (f"右圖是一張{base}的三角形皮革。皮雕師傅想要從這皮革切下一塊面積至少 ${A}$ 的內接矩形（如圖）。"
                    f"已知內接矩形在底邊上的邊長為 $x$（{_t('0<x<' + B)}），求 $x$ 的範圍。")
        frac = _FRAC + "{" + B + "-x}{" + B + "}"
        height_tex = _t(H + _TIMES + frac)
        area_tex = _t("S=x" + _TIMES + H + _TIMES + frac + "=" + rec["area"].replace("*", ""))
        s_ge = _t("S" + _GE + A)
        steps = [f"由相似三角形，內接矩形的高為 {height_tex}，面積 {area_tex}。",
                 f"面積至少 ${A}$：{s_ge}，整理並因式分解後畫正負號表，再配合 {_t('0<x<' + B)}，得 {_t(latex)}。"]
    elif kind == "square_corner":
        s, A = _num_tex(it["s"]), _num_tex(it["A"])
        question = (f"如右圖，正方形 $ABCD$ 的邊長為 ${s}$，在 $\\overline{{AB}}$ 與 $\\overline{{BC}}$ 上分別各取一點 $P, Q$，使得 $\\overline{{AP}}=\\overline{{BQ}}$，"
                    f"且四邊形 $PQCD$ 的面積至少為 ${A}$。已知 $\\overline{{AP}}=x>0$，求 $x$ 的範圍。")
        half = _FRAC + "{1}{2}"
        area_tex = _t("S=" + s + "^{2}-" + half + _TIMES + s + "x-" + half + "(" + s + "-x)x=" + rec["area"].replace("*", ""))
        s_ge = _t("S" + _GE + A)
        steps = [f"四邊形 $PQCD$ 的面積＝正方形面積－$\\triangle APD$－$\\triangle PBQ$，即 {area_tex}。",
                 f"面積至少 ${A}$：{s_ge}，整理並因式分解後畫正負號表，再配合 {_t('0<x<' + s)}，得 {_t(latex)}。"]
    elif kind == "path_around_plot":
        W, L, P0, A0 = (_num_tex(it[k]) for k in ("W", "L", "P0", "A0"))
        question = (f"如圖，有一個寬 ${W}$ 公尺，長 ${L}$ 公尺的矩形土地，今要在土地內的周邊闢一等寬的小路。若內部矩形的周長至少為 ${P0}$ 公尺，"
                    f"且面積不大於 ${A0}$ 平方公尺，則小路寬度 $x$（公尺）的範圍為何？")
        limit_tex = _t("2x<" + str(min(_q(it["W"]), _q(it["L"]))))
        peri_tex = _t("2(" + W + "-2x+" + L + "-2x)" + _GE + P0)
        area_tex = _t("(" + W + "-2x)(" + L + "-2x)" + _LE + A0)
        steps = [f"內部矩形的寬 ${W}-2x$、長 ${L}-2x$（需 $x>0$ 且 {limit_tex}），周長 {peri_tex}，",
                 f"面積 {area_tex}，分別解出再取交集，得 {_t(latex)}。"]
    elif kind == "cube_paint":
        c1, c2, xmax = _num_tex(it["plastic"]), _num_tex(it["paint"]), _num_tex(it["xmax"])
        question = (f"某工廠想設計一個實心的塑膠正立方體，並在表面烤漆出售。塑膠材料每立方單位 ${c1}$ 元，烤漆每平方單位 ${c2}$ 元。"
                    f"若烤漆的費用不可高於塑膠材料費用的{_fraction_words(it['share'])}，且工廠能作的正立方體之最大邊長為 ${xmax}$，則正立方體邊長 $x$ 的範圍為何？")
        plastic_tex = _t(c1 + "x^{3}")
        paint_tex = _t("6" + _TIMES + c2 + "x^{2}")
        diff_tex = _t(rec["difference"].replace("*", "") + _GE + "0")
        max_tex = _t("0<x" + _LE + xmax)
        steps = [f"邊長 $x$ 的正立方體：塑膠費用 {plastic_tex}，烤漆面積 $6x^{{2}}$、烤漆費用 {paint_tex}。",
                 f"烤漆費用不高於塑膠費用的{_fraction_words(it['share'])}：整理成 {diff_tex}，因 $x>0$ 可約去 $x^{{2}}$，再配合 {max_tex}，得 {_t(latex)}。"]
    elif kind == "projectile_ceiling":
        T, H = _num_tex(it["T"]), _num_tex(it["H"])
        question = (f"遊樂場裡有一門大砲，可發射出砲彈供人玩樂。設大砲發射 $t$ 秒後與砲彈高度 $y$ 公尺的關係式為\n{_t('y=kt(' + T + '-t)')}，"
                    f"其中正數 $k$ 為大砲上可調整的變數。為了不讓砲彈打中高 ${H}$ 公尺的天花板，請問：變數 $k$ 應限制在什麼範圍內。")
        mid = _num_tex(_q(it["T"]) / 2)
        peak_tex = _t("y=k" + _CDOT + mid + _LEFT + T + "-" + mid + _RIGHT + "=" + rec["peak"].replace("*", ""))
        steps = [f"{_t('y=kt(' + T + '-t)')} 是開口向下的二次函數，頂點在 $t={mid}$，最高高度 {peak_tex}。",
                 f"砲彈不能打中天花板，最高高度要低於 ${H}$ 公尺：{_t(rec['peak'].replace('*', '') + '<' + H)}，再配合 $k>0$，得 {_t(latex.replace('x', 'k'))}。"]
        canonical = canonical
        part = _ineq_part(1, canonical)
        part["answer_format_example"] = "0<k<4"
        return _single_payload(matrix, question=question, part=part, display_answer=sol_words, explanation_steps=steps, shape="inequality_solution_set")
    else:
        return _boxed_application(matrix, it, rec, figure)
    part = _ineq_part(1, canonical)
    return _single_payload(matrix, question=question, part=part, display_answer=sol_words, explanation_steps=steps, shape="inequality_solution_set", visual_spec=figure)


_FACTOR_OPTIONS = [{"label": chr(ord("A") + i), "value": v} for i, v in enumerate(("$x-1$", "$x-2$", "$x-3$", "$x-4$", "$x$"))]
_FACTOR_ROOT = {1: "A", 2: "B", 3: "C", 4: "D", 0: "E"}
_TENT_OPTIONS = [{"label": chr(ord("A") + i), "value": v} for i, v in enumerate(("$x+1$", "$x+2$", "$x+3$", "$x+4$", "$x$"))]
_TENT_ROOT = {-1: "A", -2: "B", -3: "C", -4: "D", 0: "E"}


def _boxed_application(matrix: dict[str, Any], it: dict[str, Any], rec: dict[str, Any], figure: dict[str, Any] | None) -> dict[str, Any]:
    kind = it["kind"]
    roots = rec["factor_roots"]
    if len(roots) != 1:
        raise ValueError("exactly_one_listed_factor_required")
    V = _num_tex(it["V"])
    f_tex = _poly_tex([_q(c) for c in rec["f_coeffs"]])
    canonical, latex = _inequality_tail(rec)
    if kind == "frame_box":
        L = _num_tex(it["L"])
        intro = (f"將一根長度為 ${L}$（單位）的塑膠管切割成十二段，組成一個底座為正方形的長方體支架，如圖所示。從圖中可以知道，長度 $x$（單位）的有八段，長度 $y$（單位）的有四段。\n請回答下列問題。")
        rel_tex, vol_word, size_word = f"8x+4y={L}", "長方體", "立方單位"
        steps1 = f"(1) 八段長 $x$、四段長 $y$ 合計為 ${L}$，所以 {_t(rel_tex)}（即 {_t('y=' + sp.latex(sp.Rational(str(_q(it['L'])), 4) - 2 * X_SYM))}）。"
        steps2 = f"(2) 體積 {_t('f(x)=x^{2}y=x^{2}(' + sp.latex(sp.Rational(str(_q(it['L'])), 4) - 2 * X_SYM) + ')=' + f_tex)}。"
    elif kind == "tent_prism":
        L = _num_tex(it["L"])
        p, q, r_ = (_num_tex(v) for v in it["triple"])
        perimeter = _q(it["triple"][0]) + _q(it["triple"][1]) + _q(it["triple"][2])
        intro = (f"露營帳棚經常是側邊為三角形的三角柱構造，內部空間越大越好。設計師應客戶要求，想要用一根長度為 ${L}$（單位）的塑鋼管，將它切割成九段，"
                 f"來組成帳棚的支架，如圖所示。從圖中可以發現，長度 ${p}x$, ${q}x$, ${r_}x$（單位）的各兩段，長度 $y$（單位）的有三段。\n請回答下列問題。")
        rel_tex, vol_word, size_word = f"{_num_tex(2 * perimeter)}x+3y={L}", "帳棚", "立方單位"
        base_tex = _t(_FRAC + "{1}{2}" + _TIMES + p + "x" + _TIMES + q + "x=" + _num_tex(_q(it["triple"][0]) * _q(it["triple"][1]) / 2) + "x^{2}")
        steps1 = f"(1) 兩個三角形底面各有 ${p}x, {q}x, {r_}x$ 三段，加上三段 $y$，總長 {_t(rel_tex)}。"
        steps2 = f"(2) 底面直角三角形面積 {base_tex}，體積 {_t('f(x)=' + _num_tex(_q(it['triple'][0]) * _q(it['triple'][1]) / 2) + 'x^{2}y=' + f_tex)}。"
    else:
        S = _num_tex(it["S"])
        intro = (f"陳師傅想為公司設計底面為正方形且沒有蓋子的一個長方體紙盒，裡面白色，外面灰色，如圖所示，其中底面正方形邊長為 $x$ 公分，高為 $y$ 公分。"
                 f"在灰色部分的面積為 ${S}$ 平方公分的要求下，回答下列問題。")
        rel_tex, vol_word, size_word = f"x^{{2}}+4xy={S}", "紙盒", "立方公分"
        steps1 = f"(1) 外面（灰色）面積＝底面＋四個側面，即 {_t(rel_tex)}。"
        y_tex = _t("y=" + _FRAC + "{" + S + "-x^{2}}{4x}")
        steps2 = f"(2) 由 (1) 得 {y_tex}，體積 {_t('f(x)=x^{2}y=' + f_tex)}。"
    question = (f"{intro}\n(1)寫出 $x$ 與 $y$ 的關係式。\n(2)已知{vol_word}的體積為 $x$ 的三次多項式 {_t('f(x)')}，求 {_t('f(x)')}。\n"
                f"(3)下列何者是 {_t('f(x)-' + V)} 的因式？（單選）\n(4)若此{vol_word}的體積至少要 ${V}$（{size_word}），則 $x$ 的範圍為何？")
    parts = [_part(1, rec["relation"], *_EQUATION, label="(1)", prompt="(1)"),
             _part(2, rec["f"], *_EXPR, label="(2)", prompt="(2)", required_form="expanded"),
             _choice_part(3, (_TENT_ROOT if kind == "tent_prism" else _FACTOR_ROOT)[roots[0]], _TENT_OPTIONS if kind == "tent_prism" else _FACTOR_OPTIONS, "(3)"),
             _ineq_part(4, canonical, "(4)")]
    root_text = "$x$" if roots[0] == 0 else _t(f"x{_signed_tex(-roots[0])}")
    domain_note = "$x>0$ 且 $y>0$"
    f_ge = _t("f(x)" + _GE + V)
    steps = [steps1, steps2, f"(3) 令 {_t('x=' + str(roots[0]))}，{_t('f(' + str(roots[0]) + ')=' + V)}，所以 {root_text} 是 {_t('f(x)-' + V)} 的因式。",
             f"(4) {f_ge}，利用 (3) 因式分解後畫正負號表，再配合 {domain_note}，得 {_t(latex)}。"]
    shown = f"(1) {_t(rel_tex)}；(2) {_t('f(x)=' + f_tex)}；(3) {root_text}；(4) {_display(rec)}"
    return _parts_payload(matrix, question=question, parts=parts, display_answer=shown, explanation_steps=steps, shape="polynomial_application_parts", visual_spec=figure)


X_SYM = sp.Symbol("x")


# --- E. polynomial_graph_solutions -----------------------------------------------------------------------

def _polynomial_graph_solutions(matrix: dict[str, Any]) -> dict[str, Any]:
    it, rec = matrix["givens"]["items"][0], matrix["answer"]["items"][0]
    roots = [_q(r) for r, _m in it["roots"]]
    curve, window = rec["curve"], rec["window"]
    view = FG.fit_view([(window["x"][0], -window["y"]), (window["x"][1], window["y"])], pad=0, include_origin=True)
    figure = FG.plane(points=[FG.point_entry((float(r), 0), str(r)) for r in roots], lines=[], view=view,
                      extra={"show_grid": False, "curves": [{"points": curve, "color": _CURVE_COLOR}]})
    word = _DEGREE_WORD[rec["degree"]]
    f_le = _t("f(x)" + _LE + "0")
    question = (f"已知{word}次函數 {_t('y=f(x)')} 的圖形如右圖，求\n(1)滿足 {_t('f(x)=0')} 的實數 $x$。\n(2)滿足 {_t('f(x)>0')} 的實數 $x$。\n"
                f"(3)滿足 {_t('f(x)<0')} 的實數 $x$。\n(4)滿足 {f_le} 的實數 $x$。")
    members = [int(r) if r == int(r) else str(r) for r in roots]
    parts = [_part(1, members, *_SET, solution_members="exact_rational", answer_format_example="1, 3", label="(1)", prompt="(1)"),
             _ineq_part(2, rec["gt"]["canonical"], "(2)"), _ineq_part(3, rec["lt"]["canonical"], "(3)"), _ineq_part(4, rec["le"]["canonical"], "(4)")]
    zero_text = "、".join(_t(sp.latex(r)) for r in roots)
    steps = [f"(1) 圖形與 $x$ 軸的交點（函數值為 $0$）在 $x=$ {zero_text}，所以 $f(x)=0$ 的解為 {zero_text}。",
             f"(2) 圖形在 $x$ 軸上方的部分：{_t(rec['gt']['latex'])}。", f"(3) 圖形在 $x$ 軸下方的部分：{_t(rec['lt']['latex'])}。",
             f"(4) $f(x)\\le 0$ 包含圖形在 $x$ 軸下方與在 $x$ 軸上的點：{_t(rec['le']['latex'])}。"]
    shown = (f"(1) {'、'.join(str(r) for r in roots)}；(2) {rec['gt']['canonical']}；(3) {rec['lt']['canonical']}；(4) {rec['le']['canonical']}"
             ).replace("<=", "≤").replace(">=", "≥").replace(" or ", " 或 ")
    return _parts_payload(matrix, question=question, parts=parts, display_answer=shown, explanation_steps=steps, shape="polynomial_graph_solutions", visual_spec=figure)


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "solve_polynomial_inequality": _solve_inequalities,
    "polynomial_inequality_parameters": _polynomial_inequality_parameters,
    "polynomial_statements": _polynomial_statements,
    "polynomial_applications": _polynomial_applications,
    "polynomial_graph_solutions": _polynomial_graph_solutions,
}


def adapt_polynomial_inequality_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_polynomial_inequality_operation:{operation}")
    return builder(matrix)
