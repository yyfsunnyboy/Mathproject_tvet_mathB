"""Question payload contracts for function.linear_quadratic.

Every payload is graded by a shared checker registered in ``CHECKER_CAPABILITIES``; the expected answers
always come from the domain matrix, never from this adapter.  Stems, dynamic solutions and figures are
rebuilt from the same givens, so a varied question never shows stale content or a stale picture.  Figures
are plain ``visual_spec`` data for the shared coordinate-plane renderer with the unit grid switched off.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any, Callable

import sympy as sp

from core.domain.promoted.algebra_polynomial_division.polynomial_core import fr, frac_latex, frac_text, poly, poly_latex
from core.domain.promoted.analytic_geometry_lines import figures as FG

from .function_models_domain import DOMAIN_KEY, _vertex

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})

X0_CALL = "f\\left(x_{0}\\right)"
VERTEX_FORM_TEX ="y=a\\left(x-h\\right)^{2}+k"
_EXPR = ("expression_checker", "algebraic_equivalent", "expression")
_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_RADICAL = ("expression_equivalence_checker", "radical_equivalence", "numeric_or_radical")
_PI = ("expression_equivalence_checker", "math_expression_equivalence", "numeric_or_radical")
_SET = ("solution_set_checker", "unordered_solution_set", "solution_set")
_POINT = ("coordinate_pair_checker", "coordinate_pair_equivalence", "coordinate_pair")
_EQUATION = ("equation_checker", "equation_equivalent", "equation")
_REGION = ("inequality_solution_checker", "inequality_solution_equivalence", "inequality")


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


def _payload(matrix, *, question, answer, display_answer, contract, explanation_steps, choices=(), visual_spec=None, extra=None) -> dict[str, Any]:
    operation = matrix["domain_operation"]
    payload = {
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
    if visual_spec:
        payload["visual_spec"] = visual_spec
        payload["visual_backed"] = bool(visual_spec.get("render_required"))
    if extra:
        payload.update(extra)
    return payload


def _single_payload(matrix, *, question, part, display_answer, explanation_steps, shape, visual_spec=None) -> dict[str, Any]:
    skip = ("key", "label", "checker", "checker_key", "equivalence_type", "answer_type", "expected_answer", "prompt")
    extra = {k: v for k, v in part.items() if k not in skip}
    if part["answer_type"] == "single_choice":
        return _payload(
            matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
            contract=_contract("single_choice", "single_choice", "choice_label_checker", "choice_label",
                               answer_shape="single_choice", choices=[dict(c) for c in part["choices"]]),
            explanation_steps=explanation_steps, choices=part["choices"], visual_spec=visual_spec,
        )
    return _payload(
        matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
        contract=_contract(part["answer_type"], "short_answer", part["checker"], part["equivalence_type"], answer_shape=shape, **extra),
        explanation_steps=explanation_steps, visual_spec=visual_spec,
    )


def _parts_payload(matrix, *, question, parts, display_answer, explanation_steps, shape, visual_spec=None, drawing=False) -> dict[str, Any]:
    if len(parts) == 1:
        return _single_payload(matrix, question=question, part=parts[0], display_answer=display_answer,
                               explanation_steps=explanation_steps, shape=shape, visual_spec=visual_spec)
    extra = {"contract_extra": None}
    contract_extra = {"drawing_parts": True} if drawing else {}
    return _payload(
        matrix, question=question, answer={p["key"]: p["expected_answer"] for p in parts}, display_answer=display_answer,
        contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer", answer_shape=shape,
                           parts=parts, **contract_extra),
        explanation_steps=explanation_steps, visual_spec=visual_spec,
    )


def _t(text: str) -> str:
    return f"${text}$"


def _poly_part(index: int, rec: dict[str, Any], label: str) -> dict[str, Any]:
    return _part(index, rec["plain"], *_EXPR, label=label, prompt=label, required_form="expanded")


def _num_part(index: int, canonical: str, label: str, example: str = "") -> dict[str, Any]:
    extra = {"answer_format_example": example} if example else {}
    return _part(index, canonical, *_RATIONAL, label=label, prompt=label, **extra)


def _selection_part(index: int, selected: list[int]) -> dict[str, Any]:
    if not selected:
        raise ValueError("selection_needs_at_least_one_correct_option")
    return _part(index, list(selected), *_SET, solution_members="exact_rational", answer_format_example="2, 4")


def _point_part(index: int, text: str, label: str) -> dict[str, Any]:
    return _part(index, text, *_POINT, label=label, prompt=label)


# --- LaTeX helpers -----------------------------------------------------------------------------

def _n(spec: Any) -> str:
    if isinstance(spec, dict):
        if "sqrt" in spec:
            return f"\\sqrt{{{int(spec['sqrt'])}}}"
        b, e = spec["pow"]
        return f"{int(b)}^{{{int(e)}}}"
    q = fr(spec)
    text = str(spec)
    if "." in text and q.denominator != 1:
        return text
    return frac_latex(q)


def _fx(arg: Any) -> str:
    return f"f\\left({_n(arg)}\\right)"


def _q(coeffs: Any) -> str:
    return poly_latex(poly([fr(v) for v in coeffs]))


def _dec(q: Fraction) -> str:
    d = q.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    if d != 1:
        return frac_latex(q)
    text = f"{float(abs(q)):.10f}".rstrip("0").rstrip(".")
    return ("-" if q < 0 else "") + text


def _vertex_form(a: Fraction, h: Fraction, k: Fraction, var: str = "x") -> str:
    inner = var if h == 0 else (f"{var}-{frac_latex(h)}" if h > 0 else f"{var}+{frac_latex(-h)}")
    lead = "" if a == 1 else ("-" if a == -1 else frac_latex(a))
    head = f"{lead}\\left({inner}\\right)^{{2}}" if h != 0 else f"{lead}{var}^{{2}}"
    if k == 0:
        return head
    return head + ("+" if k > 0 else "-") + frac_latex(abs(k))


def _sgn(q: Fraction) -> str:
    return ("+" if q >= 0 else "-") + frac_latex(abs(q))


def _derivation(a: Fraction, b: Fraction, c: Fraction) -> str:
    """``y=ax^2+bx+c`` completed to the square, one equals sign per textbook step."""
    h, k = _vertex(a, b, c)
    lead = "" if a == 1 else ("-" if a == -1 else frac_latex(a))
    m = b / a
    s = m / 2
    chain = ["y=" + poly_latex(poly([a, b, c]))]
    if m == 0:
        chain.append(_vertex_form(a, h, k))
        return "=".join(chain)
    mterm = ("+" if m > 0 else "-") + ("" if abs(m) == 1 else frac_latex(abs(m))) + "x"
    chain.append(f"{lead}\\left(x^{{2}}{mterm}\\right)" + (_sgn(c) if c != 0 else ""))
    square = f"\\left({frac_latex(abs(s))}\\right)^{{2}}" if s.denominator != 1 else f"{abs(s.numerator)}^{{2}}"
    chain.append(f"{lead}\\left(x^{{2}}{mterm}+{square}\\right)" + _sgn(-a * s * s) + (_sgn(c) if c != 0 else ""))
    chain.append(_vertex_form(a, h, k))
    return "=".join(chain)


def _cost_tex(f0: Any, f1: Any) -> str:
    c1 = fr(f1)
    return f"{_n(f0)}{'+' if c1 > 0 else '-'}{'' if abs(c1) == 1 else _n(abs(c1))}x"


def _shift_words(dx: Fraction, dy: Fraction) -> str:
    parts = []
    if dx != 0:
        parts.append(f"往{'右' if dx > 0 else '左'}平移 ${frac_latex(abs(dx))}$ 單位")
    if dy != 0:
        parts.append(f"向{'上' if dy > 0 else '下'}平移 ${frac_latex(abs(dy))}$ 單位")
    return "，再".join(parts)


def _plane(points: list[dict[str, Any]], lines: list[dict[str, Any]], extent: list[Any], extra: dict[str, Any] | None = None, pad: int = 1) -> dict[str, Any]:
    view = FG.fit_view(extent, pad=pad, include_origin=True)
    return FG.plane(points=points, lines=lines, view=view, extra={"show_grid": False, **(extra or {})})


def _curve(f: Callable[[float], float], lo: float, hi: float, color: str = "#1565c0", samples: int = 80) -> dict[str, Any]:
    return {"points": [[lo + (hi - lo) * i / samples, f(lo + (hi - lo) * i / samples)] for i in range(samples + 1)], "color": color}


def _circle_curves(cx: float, cy: float, r: float, color: str) -> list[dict[str, Any]]:
    upper = [[cx - r + 2 * r * i / 80, 0.0] for i in range(81)]
    lower = [[x, 0.0] for x, _ in upper]
    for p in upper:
        p[1] = cy + max(0.0, r * r - (p[0] - cx) ** 2) ** 0.5
    for p in lower:
        p[1] = cy - max(0.0, r * r - (p[0] - cx) ** 2) ** 0.5
    return [{"points": upper, "color": color}, {"points": lower, "color": color}]


def _f(v: Any) -> float:
    return float(fr(v))


# --- A. solve_linear_functions -------------------------------------------------------------------

def _line_graph_spec(points: list[list[str]], slope: str, intercept: str) -> dict[str, Any]:
    pts = [[_f(p[0]), _f(p[1])] for p in points]
    xs = [p[0] for p in pts] + [0.0]
    ys = [p[1] for p in pts] + [_f(intercept)]
    x0, x1 = math.floor(min(xs)) - 2, math.ceil(max(xs)) + 2
    y0, y1 = math.floor(min(ys)) - 2, math.ceil(max(ys)) + 2
    return {
        "drawing_type": "line_graph", "graph_kind": "line_graph", "expected_line": {"points": pts},
        "slope": _f(slope), "y_intercept": _f(intercept), "required_elements": ["x_axis", "y_axis", "function_line"],
        "axis_range": {"x_min": x0, "x_max": x1, "y_min": y0, "y_max": y1},
    }


def _drawing_part(index: int, spec: dict[str, Any], label: str, prompt: str) -> dict[str, Any]:
    return {
        **_part(index, spec, "free_response_drawing_checker", "drawing_equivalence", "drawing"),
        "label": label, "prompt": prompt, "input_type": "canvas",
        "canvas": {"axis_range": dict(spec["axis_range"]), "show_grid": True},
        "expected_drawing_spec": spec, "drawing_required": True, "ai_check_required": True, "text_answer_enabled": False,
    }


def _solve_linear_functions(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    it, rec = givens["items"][0], answer["items"][0]
    kind = it["kind"]
    if kind == "two_points":
        (x1, y1), (x2, y2) = it["p1"], it["p2"]
        dx = it["dx"]
        question = (f"已知一次函數 {_t('f(x)')} 滿足 {_t(_fx(x1) + '=' + _n(y1))}、{_t(_fx(x2) + '=' + _n(y2))}。\n"
                    f"(1)求 {_t('f(x)')}，並描繪 {_t('y=f(x)')} 的圖形。\n"
                    f"(2)每當x增加 {_t(_n(dx))} 單位時，其相對應的函數值增加或減少多少單位？")
        spec = _line_graph_spec([[rec["points"][0][0], rec["points"][0][1]], [rec["points"][1][0], rec["points"][1][1]]]
                                if "points" in rec else [[x1, y1], [x2, y2]], rec["slope"]["canonical"], rec["y_intercept"]["canonical"])
        m, b = rec["slope"]["canonical"], rec["y_intercept"]["canonical"]
        parts = [_poly_part(1, rec["f"], "(1) f(x)"),
                 _drawing_part(2, spec, "(1) 圖形", "描繪 y=f(x) 的圖形"),
                 _num_part(3, rec["delta"]["canonical"], "(2) 變化量（增加為正、減少為負）")]
        steps = [f"設 $f(x)=ax+b$，代入兩點解得 $a={frac_latex(fr(m))}$、$b={frac_latex(fr(b))}$，即 $f(x)={rec['f']['latex']}$。",
                 f"圖形是斜率為 ${frac_latex(fr(m))}$、$y$ 截距為 ${frac_latex(fr(b))}$ 的直線。",
                 f"斜率為 ${frac_latex(fr(m))}$，所以 $x$ 增加 ${_n(dx)}$ 單位時，函數值改變 ${frac_latex(fr(rec['delta']['canonical']))}$ 單位。"]
        return _parts_payload(matrix, question=question, parts=parts,
                              display_answer=f"(1) ${rec['f']['latex']}$；(2) {frac_text(fr(rec['delta']['canonical']))}", explanation_steps=steps,
                              shape="linear_function_with_graph", drawing=True)
    if kind == "value_at":
        (x1, y1), (x2, y2) = it["p1"], it["p2"]
        question = (f"已知一次函數 {_t('f(x)')} 滿足 {_t(_fx(x1) + '=' + _n(y1))}、{_t(_fx(x2) + '=' + _n(y2))}，"
                    f"求 {_t(_fx(it['x']))} 的值。")
        val = rec["value"]
        steps = ["一次函數的圖形是直線，三點的 $x$ 坐標按比例對應函數值的比例位置（分點公式）。",
                 f"求得 ${_fx(it['x'])}={val['latex']}$。"]
        return _single_payload(matrix, question=question, part=_num_part(1, val["canonical"], "答案"), display_answer=f"${val['latex']}$",
                               explanation_steps=steps, shape="linear_function_value")
    if kind == "rate":
        x0, y0 = it["p"]
        dy = fr(str(it["dy"]))
        word = "增加" if dy > 0 else "減少"
        question = (f"已知 {_t('f(x)')} 為一次函數，{_t(_fx(x0) + '=' + _n(y0))}，且每當x增加 {_t(_n(it['dx']))} 單位時，"
                    f"其相對應的函數值{word} {_t(_n(abs(dy)))} 單位，求 {_t('f(x)')}。")
        steps = [f"斜率 $=\\frac{{{_n(it['dy'])}}}{{{_n(it['dx'])}}}={frac_latex(fr(rec['slope']['canonical']))}$，再由 ${_fx(x0)}={_n(y0)}$ 得 $f(x)={rec['f']['latex']}$。"]
        return _single_payload(matrix, question=question, part=_poly_part(1, rec["f"], "f(x)"), display_answer=f"${rec['f']['latex']}$",
                               explanation_steps=steps, shape="linear_function_rate")
    (x1, y1), (x2, y2) = it["p1"], it["p2"]
    question = (f"已知一次函數 {_t('f(x)')} 滿足 {_t(_fx(x1) + '=' + _n(y1))}、{_t(_fx(x2) + '=' + _n(y2))}、"
                f"{_t(X0_CALL + '=' + _n(it['y']))}，求實數 {_t('x_{0}')} 的值。")
    x = rec["x"]
    part = _part(1, x["canonical_text"], *_RADICAL, label="x₀", prompt="x₀", answer_format_example="3+√5")
    steps = ["函數值的變化量與 $x$ 的變化量成正比（斜率固定）。", f"得 $x_{{0}}={x['latex']}$。"]
    return _single_payload(matrix, question=question, part=part, display_answer=f"${x['latex']}$", explanation_steps=steps,
                           shape="linear_function_solve_x")


# --- B. evaluate_function_statements -------------------------------------------------------------

def _sentence(subject: dict[str, Any], st: dict[str, Any]) -> str:
    kind = st["kind"]
    if kind == "value_is":
        return _t(f"{_fx(st['x'])}={_n(st['value'])}")
    if kind == "slope_positive":
        return f"L的斜率為{'正' if st['positive'] else '負'}"
    if kind == "intercept_is":
        return f"L的{_t('y')}截距為{_t(_n(st['value']))}"
    if kind == "slope_is_quotient":
        return f"L的斜率等於 {_t(chr(92) + 'frac{' + _fx(st['xa']) + '-' + _fx(st['xb']) + '}{' + _n(st['xa']) + '-' + _n(st['xb']) + '}')}"
    if kind == "rate_is":
        return f"每當x增加 {_t(_n(st['dx']))} 單位時，其相對應的函數值{'增加' if fr(st['dy']) > 0 else '減少'} {_t(_n(abs(fr(st['dy']))))} 單位"
    if kind == "slope_sign":
        return _t(f"a_{{{st['i']}}}{'>' if st['sign'] == '+' else '<'}0")
    if kind == "slope_greater":
        return _t(f"a_{{{st['i']}}}>a_{{{st['j']}}}")
    if kind == "intercept_sign":
        return _t(f"b_{{{st['i']}}}{'>' if st['sign'] == '+' else '<'}0")
    if kind == "intercept_greater":
        return _t(f"b_{{{st['i']}}}>b_{{{st['j']}}}")
    if kind == "negative_quantity":
        return _t({"a": "a", "b": "b", "c": "c", "D": "b^{2}-4ac", "a-b+c": "a-b+c", "a+b+c": "a+b+c"}[st["expr"]])
    if kind == "linear_slope_claim":
        return f"一次函數 {_t('y=' + _q([st['a'], st['b']]))} 的圖形是一條斜率為{_t(_n(st['claimed']))}的直線"
    if kind == "translation_claim":
        h, k = fr(st["claim_h"]), fr(st["claim_k"])
        word = f"往{'左' if st['direction'] == 'left' else '右'}平移 {_t(_n(st['amount']))} 單位"
        base = _t("y=" + _vertex_form(fr(st["a"]), Fraction(0), Fraction(0)).replace("\\left(x\\right)", "x"))
        return f"將拋物線 {base} {word}，可得拋物線 {_t('y=' + _vertex_form(fr(st['a']), h, k))}"
    if kind == "axis_claim":
        inner = _q([st["p"], st["q"]])
        r = fr(st.get("r", 0))
        tail = "" if r == 0 else ("+" if r > 0 else "") + frac_latex(r)
        eq = "y=\\left(" + inner + "\\right)^{2}" + tail
        axis = _q([st["p2"], st["q2"]]) + "=0"
        return f"拋物線 {_t(eq)} 的對稱軸為直線 {_t(axis)}"
    if kind == "interval_max_claim":
        f = f"f(x)={_vertex_form(fr(st['a']), fr(st['h']), fr(st['k']))}"
        return (f"在 {_t(_n(st['lo']) + chr(92) + 'le x' + chr(92) + 'le ' + _n(st['hi']))} 的範圍內，函數 {_t(f)} 的最大值為 {_t(_fx(st['claim_x']))}")
    if kind == "intercept_claim":
        a, b = ("y", "x") if st["always"] == "y" else ("x", "y")
        return f"二次函數的圖形與{_t(a)}軸一定有一交點，但與{_t(b)}軸不一定有交點"
    raise ValueError(f"unknown_statement:{kind}")


def _lines_figure(subject: dict[str, Any]) -> dict[str, Any]:
    pts, lines, extent = [], [], []
    for i, (a, b) in enumerate(subject["lines"], start=1):
        a, b = fr(a), fr(b)
        p, q = (Fraction(-3), a * -3 + b), (Fraction(3), a * 3 + b)
        lines.append(FG.through_line(p, q, f"L_{{{i}}}", extend=True))
        extent += [(0, b), (-2, a * -2 + b), (2, a * 2 + b)]
    return _plane(pts, lines, extent, pad=2)


def _parabola_figure(a: Fraction, r1: Fraction, r2: Fraction) -> dict[str, Any]:
    lo, hi = float(min(r1, r2)) - 1.5, float(max(r1, r2)) + 1.5
    af, f1, f2 = float(a), float(r1), float(r2)
    curve = _curve(lambda x: af * (x - f1) * (x - f2), lo, hi)
    vx = (f1 + f2) / 2
    vy = af * (vx - f1) * (vx - f2)
    ys = [p[1] for p in curve["points"]]
    pts = [FG.point_entry((r1, 0), f"({frac_text(r1)},0)"), FG.point_entry((r2, 0), f"({frac_text(r2)},0)")]
    return _plane(pts, [], [(lo, 0), (hi, 0), (0, min(ys)), (0, max(ys)), (vx, vy)], {"curves": [curve]}, pad=1)


def _evaluate_function_statements(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    subject, sts, mode = givens["subject"], givens["statements"], answer["mode"]
    stype = subject["type"]
    sentences = [_sentence(subject, st) for st in sts]
    visual = None
    if stype == "linear_points":
        (x1, y1), (x2, y2) = subject["p1"], subject["p2"]
        intro = (f"設一次函數 {_t('f(x)')} 滿足 {_t(_fx(x1) + '=' + _n(y1))}、{_t(_fx(x2) + '=' + _n(y2))}，"
                 f"且 {_t('f(x)')} 的圖形是直線L，選出所有正確的選項。")
    elif stype == "three_lines":
        names = "、".join(_t(f"L_{{{i}}}") for i in (1, 2, 3))
        eqs = "、".join(_t(f"L_{{{i}}}:y=a_{{{i}}}x+b_{{{i}}}") for i in (1, 2, 3))
        intro = f"如右圖，三直線 {names} 的方程式分別為 {eqs}。選出正確的選項。"
        visual = _lines_figure(subject)
    elif stype == "parabola":
        intro = f"若函數 {_t('f(x)=ax^{2}+bx+c')} 的圖形如右圖，則下列各數哪些為負數？"
        visual = _parabola_figure(fr(subject["a"]), fr(subject["root1"]), fr(subject["root2"]))
    else:
        intro = ""
    if mode == "truth":
        question = "下列敘述對的打「○」，錯的打「×」。\n" + sentences[0] + "。"
        truth = answer["truths"][0]
        part = _part(1, "A" if truth else "B", "choice_label_checker", "choice_label", "single_choice", choices=[dict(c) for c in TRUE_FALSE_CHOICES])
        reason = _reason(subject, sts[0], truth, answer)
        return _single_payload(matrix, question=question, part=part, display_answer="○" if truth else "×",
                               explanation_steps=[f"{reason}此敘述為「{'○' if truth else '×'}」。"], shape="single_choice")
    question = intro + "\n" + "\n".join(f"({i}) {s}" for i, s in enumerate(sentences, start=1))
    steps = [f"({i}) {'正確' if t else '錯誤'}。{_reason(subject, st, t, answer)}" for i, (st, t) in enumerate(zip(sts, answer["truths"]), start=1)]
    steps.append("正確的選項為 " + "".join(f"({i})" for i in answer["selected"]) + "。")
    return _single_payload(matrix, question=question, part=_selection_part(1, answer["selected"]),
                           display_answer="".join(f"({i})" for i in answer["selected"]), explanation_steps=steps,
                           shape="selected_candidate_index_set", visual_spec=visual)


def _reason(subject: dict[str, Any], st: dict[str, Any], truth: bool, answer: dict[str, Any]) -> str:
    kind = st["kind"]
    if subject["type"] == "linear_points":
        (x1, y1), (x2, y2) = (fr(subject["p1"][0]), fr(subject["p1"][1])), (fr(subject["p2"][0]), fr(subject["p2"][1]))
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        if kind == "value_is":
            return f"由兩點得 $f(x)={_q([m, b])}$，$f({_n(st['x'])})={frac_latex(m * fr(st['x']) + b)}$。"
        if kind in ("slope_positive", "rate_is"):
            return f"斜率為 ${frac_latex(m)}$。"
        if kind == "intercept_is":
            return f"$y$ 截距為 ${frac_latex(b)}$。"
        return "直線上任兩點連線的斜率都相同。"
    if subject["type"] == "three_lines":
        ab = [(fr(a), fr(b)) for a, b in subject["lines"]]
        i, j = int(st.get("i", 1)) - 1, int(st.get("j", 1)) - 1
        if kind in ("slope_sign", "slope_greater"):
            return f"斜率 $a_{{{i + 1}}}={frac_latex(ab[i][0])}$" + (f"、$a_{{{j + 1}}}={frac_latex(ab[j][0])}$" if kind == "slope_greater" else "") + "。"
        return f"$y$ 截距 $b_{{{i + 1}}}={frac_latex(ab[i][1])}$" + (f"、$b_{{{j + 1}}}={frac_latex(ab[j][1])}$" if kind == "intercept_greater" else "") + "。"
    if subject["type"] == "parabola":
        a, b, c = (fr(v) for v in answer["abc"])
        value = {"a": a, "b": b, "c": c, "D": b * b - 4 * a * c, "a-b+c": a - b + c, "a+b+c": a + b + c}[st["expr"]]
        name = {"a": "a", "b": "b", "c": "c", "D": "b^{2}-4ac", "a-b+c": "a-b+c", "a+b+c": "a+b+c"}[st["expr"]]
        return f"由圖形（開口方向、與 $x$ 軸的交點）得 $f(x)={_q([a, b, c])}$，${name}={frac_latex(value)}$。"
    return {
        "linear_slope_claim": "一次函數 $y=ax+b$ 的斜率是 $a$。",
        "translation_claim": "平移後的函數為 $y=a(x-h)^2+k$，$h$ 向右為正、向左為負。",
        "axis_claim": "對稱軸通過頂點，頂點的 $x$ 坐標使平方項等於 0。",
        "interval_max_claim": "在範圍內比較頂點（若在範圍內）與兩端點的函數值。",
        "intercept_claim": "每個函數在 $x=0$ 都有唯一函數值，所以必與 $y$ 軸相交；是否與 $x$ 軸相交要看判別式。",
    }[kind]


# --- C. complete_square_items --------------------------------------------------------------------

def _complete_square_items(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    items, recs = givens["items"], answer["items"]
    texts = [_t("y=" + _q(it["coeffs"])) + "。" for it in items]
    if len(items) == 1:
        body = texts[0]
    else:
        body = "\n" + " ".join(f"({i}){t}" for i, t in enumerate(texts, start=1))
    question = f"將下列函數化成 {_t(VERTEX_FORM_TEX)} 的形式：{body}\n（依序填入 a、h、k 的值）"
    parts, steps, shown = [], [], []
    for i, (it, rec) in enumerate(zip(items, recs), start=1):
        a, h, k = (fr(rec[n]["canonical"]) for n in ("a", "h", "k"))
        for name, v in (("a", a), ("h", h), ("k", k)):
            parts.append(_num_part(len(parts) + 1, frac_text(v), f"({i}) {name}" if len(items) > 1 else name))
        a0, b0, c0 = (fr(v) for v in it["coeffs"])
        steps.append(f"({i}) 配方：${_derivation(a0, b0, c0)}$，所以 $a={frac_latex(a)}$、$h={frac_latex(h)}$、$k={frac_latex(k)}$。")
        shown.append(f"({i}) ${_vertex_form(a, h, k)}$")
    return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(shown), explanation_steps=steps, shape="vertex_form")


# --- D. quadratic_vertex_axis --------------------------------------------------------------------

def _quadratic_vertex_axis(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    question = f"求二次函數 {_t('y=' + _q(givens['coeffs']))} 圖形的頂點及對稱軸。"
    parts = [_point_part(1, answer["vertex"]["text"], "頂點"), _part(2, answer["axis"]["text"], *_EQUATION, label="對稱軸", prompt="對稱軸")]
    a, b, c = (fr(v) for v in givens["coeffs"])
    h, k = _vertex(a, b, c)
    steps = [f"配方：${_derivation(a, b, c)}$，頂點為 $({frac_latex(h)},{frac_latex(k)})$，對稱軸為直線 $x={frac_latex(h)}$。"]
    return _parts_payload(matrix, question=question, parts=parts,
                          display_answer=f"頂點 {answer['vertex']['text']}；對稱軸 {answer['axis']['text']}", explanation_steps=steps, shape="vertex_axis")


# --- E. quadratic_extrema ------------------------------------------------------------------------

_ASK_LABEL = {"max_value": "最大值", "min_value": "最小值", "max_x": "發生最大值時的x值", "min_x": "發生最小值時的x值"}


def _fn_tex(it: dict[str, Any], display: str | None) -> str:
    a, b, c = (fr(v) for v in it["f"])
    if display == "vertex":
        h, k = _vertex(a, b, c)
        return "y=" + _vertex_form(a, h, k)
    return "y=" + _q(it["f"])


def _quadratic_extrema(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    items, recs = givens["items"], answer["items"]
    style = givens.get("style", "single")
    display = givens.get("display")
    it0 = items[0]
    ineq = lambda iv: _t(f"{_n(iv[0])}\\le x\\le {_n(iv[1])}")  # noqa: E731
    if style == "single":
        which = "最大" if "max_x" in it0["asks"] else "最小"
        question = f"已知二次函數 {_t(_fn_tex(it0, display))}，求y的{which}值及發生{which}值時之x值。"
    elif style == "interval_single":
        question = f"在 {ineq(it0['interval'])} 的範圍內，求二次函數 {_t(_fn_tex(it0, display))} 的{'最大' if 'max_value' in it0['asks'] else '最小'}值。"
    else:
        lines = " ".join(f"({i}){ineq(it['interval'])}。" for i, it in enumerate(items, start=1))
        question = f"已知二次函數 {_t(_fn_tex(it0, display))}，在下列x的範圍內，求y的最大值{'與' if givens.get('with') == '與' else '及'}最小值：\n{lines}"
    parts, steps, shown = [], [], []
    multi = len(items) > 1
    for i, (it, rec) in enumerate(zip(items, recs), start=1):
        a, b, c = (fr(v) for v in it["f"])
        h, k = _vertex(a, b, c)
        text = []
        for ask, val in zip(it["asks"], rec["values"]):
            label = (f"({i}) " if multi else "") + _ASK_LABEL[ask]
            parts.append(_num_part(len(parts) + 1, val["canonical"], label))
            text.append(f"{_ASK_LABEL[ask]} ${frac_latex(fr(val['canonical']))}$")
        iv = it.get("interval")
        where = f"在 {ineq(iv)} 內，" if iv else ""
        steps.append(f"{'(' + str(i) + ') ' if multi else ''}配方得 ${_derivation(a, b, c)}$，頂點為 $({frac_latex(h)},{frac_latex(k)})$；{where}比較頂點（若在範圍內）與兩端點的函數值，得" + "、".join(text) + "。")
        shown.append(f"{'(' + str(i) + ') ' if multi else ''}" + "、".join(text))
    return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(shown), explanation_steps=steps, shape="quadratic_extrema")


# --- F. quadratic_graph_transformations ----------------------------------------------------------

def _quadratic_graph_transformations(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    it, rec = givens["items"][0], answer["items"][0]
    kind = it["kind"]
    if kind == "translate":
        question = (f"已知 {_t('y=' + _q(it['f']))} 的圖形{_shift_words(fr(it['right']), fr(it['up']))}後，得到函數 {_t('y=f(x)')} 的圖形，求 {_t('f(x)')}。")
        steps = [f"平移後 $f(x)=g\\left(x-({_n(it['right'])})\\right)+({_n(it['up'])})$（$g$ 為原函數），整理得 $f(x)={rec['g']['latex']}$。"]
        return _single_payload(matrix, question=question, part=_poly_part(1, rec["g"], "f(x)"), display_answer=f"${rec['g']['latex']}$",
                               explanation_steps=steps, shape="translated_function")
    if kind == "reflect_x":
        question = f"若圖形 {_t(chr(92) + 'Gamma')} 與 {_t('y=' + _q(it['f']))} 的圖形對稱於x軸，則 {_t(chr(92) + 'Gamma')} 的方程式為何？"
        part = _part(1, "y=" + rec["g"]["plain"], *_EQUATION, label="Γ 的方程式", prompt="Γ 的方程式")
        steps = ["圖形對稱於 $x$ 軸時，同一個 $x$ 對應的 $y$ 值變號，所以方程式為 $y=-(\\text{原式})$。", f"得 $y={rec['g']['latex']}$。"]
        return _single_payload(matrix, question=question, part=part, display_answer=f"$y={rec['g']['latex']}$", explanation_steps=steps, shape="reflected_equation")
    if kind == "find_translation":
        question = (f"已知將 {_t('y=' + _q(it['f']))} 的圖形往左平移h單位，再向上平移k單位後恰與 {_t('y=' + _q(it['g']))} 的圖形重合，求h, k的值。")
        parts = [_num_part(1, rec["left"]["canonical"], "h"), _num_part(2, rec["up"]["canonical"], "k")]
        fa, fb, fc = (fr(v) for v in it["f"])
        ga, gb, gc = (fr(v) for v in it["g"])
        fh, fk = _vertex(fa, fb, fc)
        gh, gk = _vertex(ga, gb, gc)
        steps = [f"配方：${_derivation(fa, fb, fc)}$、${_derivation(ga, gb, gc)}$，頂點分別為 $({frac_latex(fh)},{frac_latex(fk)})$ 與 $({frac_latex(gh)},{frac_latex(gk)})$。",
                 f"頂點由 $({frac_latex(fh)},{frac_latex(fk)})$ 移到 $({frac_latex(gh)},{frac_latex(gk)})$，所以 $h={rec['left']['latex']}$、$k={rec['up']['latex']}$。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"h={frac_text(fr(rec['left']['canonical']))}, k={frac_text(fr(rec['up']['canonical']))}",
                              explanation_steps=steps, shape="translation_amounts")
    fa, fb, fc = (fr(v) for v in it["f"])
    ga, gb, gc = (fr(v) for v in it["g"])
    fh, fk = _vertex(fa, fb, fc)
    gh, gk = _vertex(ga, gb, gc)
    question = (f"在同一坐標平面上，{_t('y=' + _vertex_form(fa, fh, fk))} 與 {_t('y=' + _vertex_form(ga, gh, gk))} 的圖形是否可以經由適當的平移而完全重疊？"
                f"若是可以，如何平移呢？\n（向右、向上為正，向左、向下為負）")
    choices = [{"label": "1", "value": "可以", "text": "可以"}, {"label": "2", "value": "不可以", "text": "不可以"}]
    parts = [_part(1, "1", "choice_label_checker", "choice_label", "single_choice", choices=choices, label="是否可以", prompt="是否可以"),
             _num_part(2, rec["right"]["canonical"], "向右平移"), _num_part(3, rec["up"]["canonical"], "向上平移")]
    steps = [f"兩個函數的二次項係數相同（皆為 ${frac_latex(fa)}$），圖形形狀相同，所以可以經由平移重疊。",
             f"頂點由 $({frac_latex(fh)},{frac_latex(fk)})$ 移到 $({frac_latex(gh)},{frac_latex(gk)})$：向右 ${rec['right']['latex']}$、向上 ${rec['up']['latex']}$。"]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"可以；向右 {frac_text(fr(rec['right']['canonical']))}，向上 {frac_text(fr(rec['up']['canonical']))}",
                          explanation_steps=steps, shape="overlap_translation")


# --- G. quadratic_always_sign --------------------------------------------------------------------

def _coef_tex(spec: Any, power: str, first: bool) -> str:
    if isinstance(spec, dict):
        c, k = fr(spec.get("c", 0)), fr(spec.get("k", 0))
        if k != 0 and c != 0:
            inner = ("" if k == 1 else frac_latex(k)) + "k" + ("+" if c > 0 else "") + frac_latex(c)
            return f"+\\left({inner}\\right)" if not first else f"\\left({inner}\\right){power}"
        if k != 0:
            body = ("" if k == 1 else ("-" if k == -1 else frac_latex(k))) + "k" + power
            return body if first or body.startswith("-") else "+" + body
        spec = c
    q = fr(spec)
    if q == 0:
        return ""
    if power and abs(q) == 1:
        body = ("-" if q < 0 else "") + power
    else:
        body = frac_latex(q) + power
    return body if (first or q < 0) else "+" + body


def _quadratic_always_sign(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    a, b, c = givens["a"], givens["b"], givens["c"]
    text = _coef_tex(a, "x^{2}", True)
    text += _coef_tex(b, "x", not text)
    text += _coef_tex(c, "", not text)
    word = "正" if givens["sign"] == "positive" else "負"
    style = givens.get("style", "plain")
    if style == "named":
        question = f"已知二次函數 {_t('f(x)=' + text)} 的值恆為{word}數，求實數k的範圍。"
    else:
        question = f"已知對任意實數x，{_t(text)} 的值恆為{word}數，求實數k的範圍。"
    rec = answer["region"]
    part = _part(1, rec["text"], *_REGION, label="k 的範圍", prompt="k 的範圍", answer_format_example="k>9")
    d = answer["discriminant"]
    cond = "a>0" if givens["sign"] == "positive" else "a<0"
    steps = [f"函數值恆為{word}數，圖形完全在 $x$ 軸的{'上' if givens['sign'] == 'positive' else '下'}方，所以 ${cond}$ 且 $D<0$。",
             f"判別式 $D=b^{{2}}-4ac={frac_latex(fr(d['d0']))}{'+' if fr(d['d1']) >= 0 else ''}{frac_latex(fr(d['d1']))}k<0$。",
             f"同時滿足兩條件，得 ${rec['text'].replace('<', '<').replace('>', '>')}$。"]
    return _single_payload(matrix, question=question, part=part, display_answer=f"${rec['text']}$", explanation_steps=steps, shape="parameter_range")


# --- H. solve_quadratic_applications -------------------------------------------------------------

def _tile_figure(side: Fraction) -> dict[str, Any]:
    s = float(side)
    x = s / 3
    A, B, C, D, E, F = (0, s), (0, 0), (s, 0), (s, s), (s - x, 0), (s, x)
    pts = [FG.point_entry(p, n) for p, n in ((A, "A"), (B, "B"), (C, "C"), (D, "D"), (E, "E"), (F, "F"))]
    segs = [(A, B), (B, C), (C, D), (D, A), (A, E), (E, F)]
    lines = [FG.through_line(p, q, extend=False) for p, q in segs]
    return _plane(pts, lines, [A, B, C, D], pad=1)


def _circles_figure(d: Fraction) -> dict[str, Any]:
    R = float(d) / 2
    x = float(d) / 6
    curves = _circle_curves(0, 0, R, "#263238")
    curves += _circle_curves(-R + x / 2, 0, x / 2, "#c62828") + _circle_curves(R - x / 2, 0, x / 2, "#c62828")
    mid = R - x
    curves += _circle_curves(0, 0, mid, "#1565c0")
    lines = [FG.through_line((-R, 0), (R, 0), extend=False)]
    return _plane([], lines, [(-R, -R), (R, R)], {"curves": curves}, pad=1)


def _pens_figure(n: int) -> dict[str, Any]:
    w, depth = 2.0, 3.0
    lines = [FG.through_line((0, depth), (n * w, depth), "牆", extend=False)]
    for i in range(n + 1):
        lines.append(FG.through_line((i * w, 0), (i * w, depth), extend=False))
    lines.append(FG.through_line((0, 0), (n * w, 0), extend=False))
    return _plane([], lines, [(0, 0), (n * w, depth)], pad=1)


def _trajectory_figure(a: Fraction, b: Fraction) -> dict[str, Any]:
    hi = float(b / a)
    curve = _curve(lambda x: -float(a) * x * x + float(b) * x, 0.0, hi)
    top = max(p[1] for p in curve["points"])
    lines = [FG.through_line((-0.5, 0), (hi + 0.5, 0), extend=False)]
    return _plane([FG.point_entry((0, 0), "O")], lines, [(0, 0), (hi, top)], {"curves": [curve]}, pad=1)


def _basket_figure(it: dict[str, Any]) -> dict[str, Any]:
    xa, ya, y0, xh = (fr(it[k]) for k in ("apex_x", "apex_y", "start_y", "hoop_x"))
    a = float((y0 - ya) / (xa * xa))
    xs = float(xh)
    curve = _curve(lambda x: a * (x - float(xa)) ** 2 + float(ya), 0.0, xs)
    lines = [FG.through_line((-0.5, 0), (xs + 0.5, 0), extend=False), FG.through_line((xs, 0), (xs, curve["points"][-1][1]), extend=False, dashed=True)]
    return _plane([FG.point_entry((0, float(y0)), "出手點")], lines, [(0, 0), (xs, float(ya) + 0.5)], {"curves": [curve]}, pad=1)


def _fountain_figure(it: dict[str, Any], rec: dict[str, Any]) -> dict[str, Any]:
    n, land, r = (fr(it[k]) for k in ("nozzle", "land", "radius"))
    a = float(fr(rec["a"]["canonical"]))
    k = float(fr(rec["peak"]["canonical"]))
    curve = _curve(lambda x: a * (x - float(r)) ** 2 + k, 0.0, float(land))
    lines = [FG.through_line((0, 0), (0, float(n)), "噴水器", extend=False), FG.through_line((-0.5, 0), (float(land) + 0.5, 0), "水面", extend=False)]
    return _plane([FG.point_entry((0, float(n)), "噴嘴")], lines, [(0, 0), (float(land), k)], {"curves": [curve]}, pad=1)


def _solve_quadratic_applications(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    it, rec = givens["items"][0], answer["items"][0]
    kind = it["kind"]
    R = lambda r: fr(r["canonical"])  # noqa: E731
    if kind == "tile_cost":
        c1, c2, c3 = it["costs"]
        s = fr(it["side"])
        question = (f"在圖(a)中，等腰三角形 {_t('ECF')}、三角形 {_t('ABE')} 與四邊形 {_t('AEFD')} 三款磁磚剛好可以拼成邊長為{_n(s)}（公寸）的正方形 {_t('ABCD')}。\n"
                    f"這種三款一套的磁磚，每四套還可以組成漂亮的宣傳圖案，是年年熱銷的產品。為了節省材料費用，公司每年都會根據材料費的單價，調整三款磁磚的大小。\n"
                    f"已知今年三款磁磚 {_t('ECF')}，{_t('ABE')} 及 {_t('AEFD')} 每平方公寸的材料費分別為{_n(c1)}元，{_n(c2)}元及{_n(c3)}元，"
                    f"且令 {_t(chr(92) + 'overline{EC}=x')}（公寸），回答下列問題：\n(1)求每一套磁磚的總材料費（以 {_t('x')} 表示）。\n"
                    f"(2)當 {_t('x')} 為多少時，每一套磁磚的總材料費最便宜？又此時總材料費為多少？")
        parts = [_poly_part(1, rec["cost"], "(1) 總材料費"), _num_part(2, rec["x"]["canonical"], "(2) x"), _num_part(3, rec["min"]["canonical"], "(2) 最低總材料費")]
        steps = [f"三角形 $ECF$ 的面積為 $\\frac{{x^{{2}}}}{{2}}$，三角形 $ABE$ 的面積為 $\\frac{{{_n(s)}({_n(s)}-x)}}{{2}}$，四邊形 $AEFD$ 的面積為其餘部分。",
                 f"(1) 總材料費 $={rec['cost']['latex']}$（元）。",
                 f"(2) 配方得最小值發生在 $x={rec['x']['latex']}$，此時總材料費為 ${rec['min']['latex']}$ 元。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1) ${rec['cost']['latex']}$；(2) x={frac_text(R(rec['x']))}，最低 {frac_text(R(rec['min']))} 元",
                              explanation_steps=steps, shape="tile_cost_model", visual_spec=_tile_figure(s))
    if kind == "profit":
        f0, f1 = it["cost"]
        rv = it["revenue"]
        if rv["mode"] == "table":
            (x1, y1), (x2, y2) = rv["points"]
            question = (f"某工廠生產一款玩具時，需先依設計圖開模，再大量生產。開模費固定 {_t(_n(f0))} 萬元，每生產一千個玩具的材料費 {_t(_n(f1))} 萬元，由此可建立成本函數\n"
                        f"{_t('f(x)=' + _cost_tex(f0, f1))}（萬元），其中x以千個為單位。\n下表是該工廠過去二筆交易中，訂單數量與收入的關係：\n"
                        f"訂單數量（千個）\t{_n(x1)}\t{_n(x2)}\n收入（萬元）\t{_n(y1)}\t{_n(y2)}\n"
                        f"利用上表及「訂單數量為 {_t('0')} 個，收入就為 {_t('0')} 元」，建立一個二次函數 {_t('g(x)=ax^{2}+bx')}，並以 {_t('g(x)')} 作為此款玩具的收入函數。"
                        f"再根據「利潤＝收入－成本」，建立利潤函數 {_t('h(x)=g(x)-f(x)')}。\n(1)求實數a, b的值。\n(2)根據 {_t('h(x)')}，當訂單數量多少千個時，利潤有最大值？又此最大值為何？")
            parts = [_num_part(1, rec["a"]["canonical"], "(1) a"), _num_part(2, rec["b"]["canonical"], "(1) b"),
                     _num_part(3, rec["x"]["canonical"], "(2) 訂單數量（千個）"), _num_part(4, rec["max"]["canonical"], "(2) 最大利潤（萬元）")]
            steps = [f"(1) 代入 $g({_n(x1)})={_n(y1)}$、$g({_n(x2)})={_n(y2)}$，解得 $a={rec['a']['latex']}$、$b={rec['b']['latex']}$。",
                     f"(2) $h(x)=g(x)-f(x)={rec['profit']['latex']}$，配方得當 $x={rec['x']['latex']}$ 千個時，利潤最大為 ${rec['max']['latex']}$ 萬元。"]
            shown = f"a={frac_text(R(rec['a']))}, b={frac_text(R(rec['b']))}；x={frac_text(R(rec['x']))} 千個，最大 {frac_text(R(rec['max']))} 萬元"
        else:
            a, b = fr(rv["a"]), fr(rv["b"])
            rev = f"x\\left({_n(b)}{'-' if a < 0 else '+'}{_dec(abs(a))}x\\right)"
            question = (f"某成衣工廠生產x千件外套的成本函數為 {_t('f(x)=' + _cost_tex(f0, f1))}（萬元），收入函數為 {_t('g(x)=' + rev)}（萬元）。"
                        f"根據利潤函數 {_t('h(x)=g(x)-f(x)')}，當產量為多少千件時，利潤有最大值？又此最大值為何？")
            parts = [_num_part(1, rec["x"]["canonical"], "產量（千件）"), _num_part(2, rec["max"]["canonical"], "最大利潤（萬元）")]
            steps = [f"$h(x)=g(x)-f(x)={rec['profit']['latex']}$，配方得當 $x={rec['x']['latex']}$ 千件時，利潤有最大值 ${rec['max']['latex']}$ 萬元。"]
            shown = f"x={frac_text(R(rec['x']))} 千件，最大 {frac_text(R(rec['max']))} 萬元"
        return _parts_payload(matrix, question=question, parts=parts, display_answer=shown, explanation_steps=steps, shape="profit_model")
    if kind == "circle_areas":
        d = fr(it["diameter"])
        question = (f"如右圖，將大圓的直徑分成左、中、右三段，其中左、右兩段等長；再分別以左、中、右三段為直徑作三個小圓。"
                    f"已知大圓的直徑長為{_n(d)}，且令左、右兩段的長均為 {_t('x')}，求此三個小圓面積總和的最小值及此時 {_t('x')} 的值。")
        mn = R(rec["min_over_pi"])
        parts = [_part(1, f"{frac_text(mn)}*pi", *_PI, label="最小值", prompt="最小值", answer_format_example="3π"), _num_part(2, rec["x"]["canonical"], "x")]
        steps = [f"三段的直徑為 $x$、${_n(d)}-2x$、$x$，面積總和 $S=\\pi\\left[\\left(\\frac{{x}}{{2}}\\right)^{{2}}\\cdot 2+\\left(\\frac{{{_n(d)}-2x}}{{2}}\\right)^{{2}}\\right]=\\pi\\left({rec['area_over_pi']['latex']}\\right)$。",
                 f"配方得 $x={rec['x']['latex']}$ 時，最小值為 ${rec['min_over_pi']['latex']}\\pi$。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"最小值 {frac_text(mn)}π；x={frac_text(R(rec['x']))}",
                              explanation_steps=steps, shape="circle_area_model", visual_spec=_circles_figure(d))
    if kind == "fenced_pens":
        n, total = int(it["pens"]), fr(it["fence"])
        question = (f"如圖，要從牆邊用圍籬圍出 {_t(str(n))} 間面積相等的矩形豬圈（牆邊不圍）。若圍籬總共用了 {_t(_n(total))} 公尺，"
                    f"則 {_t(str(n))} 間豬圈的最大面積是多少平方公尺？")
        steps = [f"設每間豬圈垂直於牆的邊長為 $w$ 公尺，平行於牆的總長為 $l$ 公尺，則 ${n + 1}w+l={_n(total)}$。",
                 f"總面積 $S=wl=w({_n(total)}-{n + 1}w)$，配方得 $w={rec['width']['latex']}$ 時，最大面積為 ${rec['max_area']['latex']}$ 平方公尺。"]
        return _single_payload(matrix, question=question, part=_num_part(1, rec["max_area"]["canonical"], "最大面積（平方公尺）"),
                               display_answer=f"${rec['max_area']['latex']}$", explanation_steps=steps, shape="fenced_area_model", visual_spec=_pens_figure(n))
    if kind == "ball":
        a, b, h = fr(it["a"]), fr(it["b"]), fr(it["height"])
        question = (f"某人將一顆球置於地上後，再將球擊出，如圖所示。\n假設此球的飛行路線是一條拋物線，且飛行時間x秒與飛行高度y公尺的關係式為\n"
                    f"{_t('y=-' + _n(a) + 'x^{2}+' + _n(b) + 'x')}。\n關於此球的飛行過程，回答下列問題。\n"
                    f"(1)當飛行時間是多少秒時，飛行高度為{_n(h)}公尺？\n(2)從飛出到落地共用了多少時間？\n(3)飛行高度何時最大？又此時高度為多少公尺？")
        parts = [_part(1, [t["canonical"] for t in rec["times"]], *_SET, label="(1) 時間（秒）", prompt="(1) 時間（秒）", solution_members="exact_rational", answer_format_example="1, 3"),
                 _num_part(2, rec["flight"]["canonical"], "(2) 時間（秒）"), _num_part(3, rec["top_time"]["canonical"], "(3) 時間（秒）"),
                 _num_part(4, rec["top_height"]["canonical"], "(3) 高度（公尺）")]
        times = "、".join(frac_text(R(t)) for t in rec["times"])
        steps = [f"(1) 令 $y={_n(h)}$ 解一元二次方程式，得 $x={times}$（秒）。", f"(2) 落地時 $y=0$，得 $x={rec['flight']['latex']}$ 秒。",
                 f"(3) 配方得 $x={rec['top_time']['latex']}$ 秒時高度最大，最大高度為 ${rec['top_height']['latex']}$ 公尺。"]
        return _parts_payload(matrix, question=question, parts=parts,
                              display_answer=f"(1) {times} 秒；(2) {frac_text(R(rec['flight']))} 秒；(3) {frac_text(R(rec['top_time']))} 秒、{frac_text(R(rec['top_height']))} 公尺",
                              explanation_steps=steps, shape="projectile_model", visual_spec=_trajectory_figure(a, b))
    if kind == "basket":
        xa, ya, y0, xh = (fr(it[k]) for k in ("apex_x", "apex_y", "start_y", "hoop_x"))
        question = (f"如圖，距籃下 {_t(_dec(xh))} 公尺處跳起投籃。已知出手時球離地 {_dec(y0)} 公尺，且當球飛行到水平距離 {_dec(xa)} 公尺時，達到最大高度 {_dec(ya)} 公尺，然後空心進籃。"
                    f"請問：籃框有多高？")
        steps = [f"以出手點的水平位置為 $x=0$，球的軌跡為 $y=a(x-{_dec(xa)})^{{2}}+{_dec(ya)}$。", f"代入 $(0,{_dec(y0)})$ 得 $a={rec['a']['latex']}$。",
                 f"籃框在 $x={_dec(xh)}$，高度 $y={rec['hoop_height']['latex']}$ 公尺。"]
        return _single_payload(matrix, question=question, part=_num_part(1, rec["hoop_height"]["canonical"], "籃框高度（公尺）"),
                               display_answer=f"${rec['hoop_height']['latex']}$", explanation_steps=steps, shape="basket_model", visual_spec=_basket_figure(it))
    if kind == "fountain":
        n, land, r = (fr(it[k]) for k in ("nozzle", "land", "radius"))
        question = (f"如圖，公園圓形水池的中央，垂直水面豎立一根旋轉式噴水器，噴水器的噴嘴距離水面 {_t(_n(n))} 公尺，噴出的水落在距噴水器 {_t(_n(land))} 公尺處。"
                    f"今要在噴水器的上方加裝一半徑 {_t(_n(r))} 公尺的圓盤，使得水流的最高點恰在圓盤的邊緣。若設計師以二次函數來設計此噴水器的噴水軌跡，"
                    f"則該圓盤應裝在噴嘴上方多少公尺處？")
        steps = [f"水流最高點與噴水器的水平距離為圓盤半徑 ${_n(r)}$，設軌跡為 $y=a(x-{_n(r)})^{{2}}+k$。",
                 f"代入 $(0,{_n(n)})$ 與 $({_n(land)},0)$ 解得 $a={rec['a']['latex']}$、$k={rec['peak']['latex']}$。",
                 f"圓盤應裝在噴嘴上方 $k-{_n(n)}={rec['above_nozzle']['latex']}$ 公尺處。"]
        return _single_payload(matrix, question=question, part=_num_part(1, rec["above_nozzle"]["canonical"], "高度（公尺）"),
                               display_answer=f"${rec['above_nozzle']['latex']}$", explanation_steps=steps, shape="fountain_model",
                               visual_spec=_fountain_figure(it, rec))
    if kind == "roots_intercept":
        p, q, r = it["root1"], it["root2"], it["y_intercept"]
        pt1, pt2, pt3 = f"({_n(p)},\\ 0)", f"({_n(q)},\\ 0)", f"(0,\\ {_n(r)})"
        question = (f"已知二次函數 {_t('f(x)')} 的圖形與x軸交於 {_t(pt1)} 與 {_t(pt2)}，與y軸交於 {_t(pt3)}，"
                    f"求 {_t('f(x)')} 及其頂點坐標。")
        parts = [_poly_part(1, rec["f"], "f(x)"), _point_part(2, rec["vertex"]["text"], "頂點坐標")]
        steps = [f"設 $f(x)=a(x-({_n(p)}))(x-({_n(q)}))$，代入 $(0,{_n(r)})$ 得 $f(x)={rec['f']['latex']}$。", f"配方得頂點為 ${rec['vertex']['text']}$。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"${rec['f']['latex']}$；頂點 {rec['vertex']['text']}",
                              explanation_steps=steps, shape="parabola_from_roots")
    p, m = it["apex_x"], it["max_value"]
    question = f"已知二次函數 {_t('f(x)=ax^{2}+bx+' + chr(92) + 'frac{1}{a}')} 在 {_t('x=' + _n(p))} 時有最大值{_n(m)}，求實數a, b的值。"
    parts = [_num_part(1, rec["a"]["canonical"], "a"), _num_part(2, rec["b"]["canonical"], "b")]
    steps = [f"對稱軸 $x=-\\frac{{b}}{{2a}}={_n(p)}$，所以 $b=-2a\\cdot {_n(p)}$。", f"最大值 $f({_n(p)})={_n(m)}$，且有最大值時 $a<0$，解得 $a={rec['a']['latex']}$、$b={rec['b']['latex']}$。"]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"a={frac_text(R(rec['a']))}, b={frac_text(R(rec['b']))}",
                          explanation_steps=steps, shape="parabola_max_condition")


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "solve_linear_functions": _solve_linear_functions,
    "evaluate_function_statements": _evaluate_function_statements,
    "complete_square_items": _complete_square_items,
    "quadratic_vertex_axis": _quadratic_vertex_axis,
    "quadratic_extrema": _quadratic_extrema,
    "quadratic_graph_transformations": _quadratic_graph_transformations,
    "quadratic_always_sign": _quadratic_always_sign,
    "solve_quadratic_applications": _solve_quadratic_applications,
}


def adapt_function_models_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_function_models_operation:{operation}")
    return builder(matrix)
