"""Question payload contracts for function.cubic_graph (普高數學1 Unit 10).

Every payload is graded by a shared checker registered in ``CHECKER_CAPABILITIES``; the expected answers always
come from the domain matrix, never from this adapter.  Stems and figures are rebuilt from the same givens, so a
varied question never shows a stale picture: the curves of a matching / comparison figure are the sampled
``gammas`` of the domain answer, coloured and labelled exactly as the stem names them.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable

from core.domain.promoted.algebra_polynomial_division.polynomial_core import fr, frac_latex, frac_text, poly, poly_latex
from core.domain.promoted.analytic_geometry_lines import figures as FG

from .cubic_domain import DOMAIN_KEY

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
_EXPR = ("expression_checker", "algebraic_equivalent", "expression")
_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_SET = ("solution_set_checker", "unordered_solution_set", "solution_set")
_POINT = ("coordinate_pair_checker", "coordinate_pair_equivalence", "coordinate_pair")

COLORS = {"紅色": "#c62828", "藍色": "#1565c0", "綠色": "#2e7d32", "黑色": "#212121", "橘色": "#ef6c00"}
GAMMA = {1: "Γ₁", 2: "Γ₂", 3: "Γ₃", 4: "Γ₄"}


# --- contracts ---------------------------------------------------------------------------------

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


def _poly_part(index: int, rec: dict[str, Any], label: str) -> dict[str, Any]:
    return _part(index, rec["plain"], *_EXPR, label=label, prompt=label, required_form="expanded")


def _num_part(index: int, canonical: str, label: str, example: str = "") -> dict[str, Any]:
    extra = {"answer_format_example": example} if example else {}
    return _part(index, canonical, *_RATIONAL, label=label, prompt=label, **extra)


def _point_part(index: int, text: str, label: str) -> dict[str, Any]:
    return _part(index, text, *_POINT, label=label, prompt=label)


def _selection_part(index: int, selected: list[int]) -> dict[str, Any]:
    if not selected:
        raise ValueError("selection_needs_at_least_one_correct_option")
    return _part(index, list(selected), *_SET, solution_members="exact_rational", answer_format_example="2, 4")


def _choice_part(index: int, expected_label: str, choices: list[dict[str, str]], label: str) -> dict[str, Any]:
    return _part(index, expected_label, "choice_label_checker", "choice_label", "single_choice", choices=[dict(c) for c in choices], label=label, prompt=label)


# --- LaTeX helpers -----------------------------------------------------------------------------

def _lat(q: Any) -> str:
    return frac_latex(fr(q))


def _xh(h: Fraction, var: str = "x") -> str:
    return var if h == 0 else (f"{var}-{_lat(h)}" if h > 0 else f"{var}+{_lat(-h)}")


def _coef(c: Fraction, tail: str) -> str:
    sign = "-" if c < 0 else "+"
    mag = abs(c)
    return sign + ("" if mag == 1 else _lat(mag)) + tail


def _form_tex(a: Any, p: Any, h: Any, k: Any) -> str:
    a, p, h, k = fr(a), fr(p), fr(h), fr(k)
    base = "x" if h == 0 else f"\\left({_xh(h)}\\right)"
    lead = "" if a == 1 else ("-" if a == -1 else _lat(a))
    text = f"{lead}{base}^{{3}}"
    if p != 0:
        text += _coef(p, base)
    if k != 0:
        text += ("+" if k > 0 else "-") + _lat(abs(k))
    return text


def _poly_tex(coeffs: list[Any]) -> str:
    return poly_latex(poly([fr(v) for v in coeffs]))


def _shift_words(dx: Fraction, dy: Fraction) -> str:
    parts = []
    if dx != 0:
        parts.append(f"往{'右' if dx > 0 else '左'}平移 ${_lat(abs(dx))}$ 單位")
    if dy != 0:
        parts.append(f"向{'上' if dy > 0 else '下'}平移 ${_lat(abs(dy))}$ 單位")
    return "，再".join(parts)


def _approx_tex(q: Any) -> str:
    q = fr(q)
    d = q.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    if d != 1:
        return _lat(q)
    text = f"{float(abs(q)):.10f}".rstrip("0").rstrip(".")
    return ("-" if q < 0 else "") + text


# --- A. cubic_center_form -----------------------------------------------------------------------

def _cubic_center_form(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    items, recs = givens["items"], answer["items"]
    kind = items[0]["kind"]
    if any(it["kind"] != kind for it in items):
        raise ValueError("one_kind_per_component")
    if kind == "to_form":
        lines = "\n".join(f"({i}) {_t('y=' + _poly_tex(it['coeffs']))}。" for i, it in enumerate(items, start=1))
        target = _t("y=a\\left(x-h\\right)^{3}+p\\left(x-h\\right)+k")
        question = f"將下列函數化成 {target} 的形式：\n" + lines
        parts, steps, shown = [], [], []
        for i, (it, rec) in enumerate(zip(items, recs), start=1):
            prefix = f"({i}) " if len(items) > 1 else ""
            for name in ("a", "p", "h", "k"):
                parts.append(_num_part(len(parts) + 1, rec[name]["canonical"], f"{prefix}{name}"))
            h = fr(rec["h"]["canonical"])
            steps.append(f"{prefix}三次項與二次項係數決定對稱中心的橫坐標：$h=-\\frac{{c_{{2}}}}{{3c_{{3}}}}={rec['h']['latex']}$。")
            steps.append(f"{prefix}把 $x=t+h$ 代入並展開，二次項消去，得 "
                         f"{_t('y=' + _form_tex(rec['a']['canonical'], rec['p']['canonical'], rec['h']['canonical'], rec['k']['canonical']))}，"
                         f"即 $a={rec['a']['latex']}$、$p={rec['p']['latex']}$、$h={rec['h']['latex']}$、$k={rec['k']['latex']}$。")
            shown.append(f"{prefix}a={rec['a']['canonical']}，p={rec['p']['canonical']}，h={rec['h']['canonical']}，k={rec['k']['canonical']}")
        return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(shown), explanation_steps=steps, shape="cubic_center_form_numbers")
    rec = recs[0]
    it = items[0]
    if kind == "center":
        question = f"求三次函數 {_t('y=' + _poly_tex(it['coeffs']))} 圖形的對稱中心。"
        steps = [f"對稱中心的橫坐標為 $h=-\\frac{{c_{{2}}}}{{3c_{{3}}}}={rec['h']['latex']}$。",
                 f"把 $x=t+h$ 代入並展開，得 {_t('y=' + _form_tex(rec['a']['canonical'], rec['p']['canonical'], rec['h']['canonical'], rec['k']['canonical']))}。",
                 f"所以對稱中心為點 ${rec['center']['text']}$。"]
        return _parts_payload(matrix, question=question, parts=[_point_part(1, rec["center"]["text"], "對稱中心")], display_answer=f"${rec['center']['text']}$",
                              explanation_steps=steps, shape="cubic_center_point")
    if kind == "from_center":
        a, p = fr(it["a"]), fr(it["p"])
        question = (f"已知 {_t('y=' + _generic_form_tex(a, p))} "
                    f"圖形的對稱中心為 {_t('(' + _lat(it['center'][0]) + ',' + _lat(it['center'][1]) + ')')}，求實數 {_t('h,k')} 的值。")
        parts = [_num_part(1, rec["h"]["canonical"], "h"), _num_part(2, rec["k"]["canonical"], "k")]
        steps = [f"函數 {_t('y=a(x-h)^{3}+p(x-h)+k')} 的圖形對稱於點 $(h,k)$，所以對稱中心就是 $(h,k)$。",
                 f"因此 $h={rec['h']['latex']}$，$k={rec['k']['latex']}$。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"h={rec['h']['canonical']}，k={rec['k']['canonical']}",
                              explanation_steps=steps, shape="cubic_center_hk")
    if kind == "shift":
        f = it["form"]
        question = (f"將 {_t('f(x)=' + _form_tex(f['a'], f['p'], f['h'], f['k']))} 的圖形{_shift_words(fr(it['dx']), fr(it['dy']))}後，"
                    f"得 {_t('g(x)')} 的圖形，求 {_t('g(x)')} 的{_power_name(rec['asked_power'])}。")
        g = rec["g_coeffs"]["plain"]
        steps = [f"平移後 $g(x)=f(x-({_lat(it['dx'])}))+({_lat(it['dy'])})$，即 {_t('g(x)=' + _form_tex(f['a'], f['p'], rec['g_form']['h']['canonical'], rec['g_form']['k']['canonical']))}。",
                 f"展開得 {_t('g(x)=' + rec['g_coeffs']['latex'])}。",
                 f"所以 {_t('g(x)')} 的{_power_name(rec['asked_power'])}為 ${rec['asked_coeff']['latex']}$。"]
        return _parts_payload(matrix, question=question, parts=[_num_part(1, rec["asked_coeff"]["canonical"], _power_name(rec["asked_power"]))],
                              display_answer=f"${rec['asked_coeff']['latex']}$", explanation_steps=steps, shape="cubic_shift_coefficient")
    if kind == "translation_overlap":
        f, g = it["f"], it["g"]
        question = (f"在同一坐標平面上，{_t('y=' + _form_tex(f['a'], f['p'], f['h'], f['k']))} 與 {_t('y=' + _form_tex(g['a'], g['p'], g['h'], g['k']))} "
                    "的圖形是否可以經由適當的平移而完全重疊？若是可以，如何平移呢？")
        choices = [{"label": "A", "value": "可以"}, {"label": "B", "value": "不可以"}]
        parts = [_choice_part(1, "A" if rec["overlap"] else "B", choices, "是否可以完全重疊")]
        if rec["overlap"]:
            parts.append(_num_part(2, rec["dx"]["canonical"], "向右平移的單位數（向左平移請填負數）"))
            parts.append(_num_part(3, rec["dy"]["canonical"], "向上平移的單位數（向下平移請填負數）"))
        steps = [f"兩個函數的圖形形狀由 $a$ 與 $p$ 決定：$a_{{1}}={_lat(f['a'])}$、$p_{{1}}={_lat(f['p'])}$；$a_{{2}}={_lat(g['a'])}$、$p_{{2}}={_lat(g['p'])}$。"]
        if rec["overlap"]:
            steps.append(f"兩者的 $a$、$p$ 都相同，只有對稱中心不同：由 $({_lat(f['h'])},{_lat(f['k'])})$ 移到 $({_lat(g['h'])},{_lat(g['k'])})$，"
                         f"所以可以完全重疊，需{_shift_words(fr(rec['dx']['canonical']), fr(rec['dy']['canonical']))}。")
        else:
            steps.append("$a$ 或 $p$ 不同，圖形的彎曲程度不同，無法只靠平移完全重疊。")
        shown = "可以；" + _shift_words(fr(rec["dx"]["canonical"]), fr(rec["dy"]["canonical"])) if rec["overlap"] else "不可以"
        return _parts_payload(matrix, question=question, parts=parts, display_answer=shown, explanation_steps=steps, shape="cubic_translation_overlap")
    raise ValueError(kind)


def _generic_form_tex(a: Fraction, p: Fraction) -> str:
    lead = "" if a == 1 else ("-" if a == -1 else _lat(a))
    return f"{lead}\\left(x-h\\right)^{{3}}" + _coef(p, "\\left(x-h\\right)") + "+k"


def _power_name(power: int) -> str:
    return {3: "三次項係數", 2: "二次項係數", 1: "x項係數", 0: "常數項"}[power]


# --- B. cubic_from_conditions -------------------------------------------------------------------

def _cubic_from_conditions(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    it, rec = givens["items"][0], answer["items"][0]
    kind = it["kind"]
    if kind == "symmetric_pair_origin":
        (ax, ay), (bx, by) = it["A"], it["B"]
        cx = it["C_x"]
        question = (f"在平面坐標上，主辦單位設計一個三次函數的圖形作為路跑的路線。已知起跑點為原點 $O$，終點為 {_t('C(' + _lat(cx) + ',s)')}，"
                    f"路線上的兩點 {_t('A(' + _lat(ax) + ',' + _lat(ay) + ')')}、{_t('B(' + _lat(bx) + ',' + _lat(by) + ')')} 為補給站，"
                    "且兩補給站對稱於圖形的對稱中心，求\n(1)圖形的對稱中心。\n(2)此三次函數。\n(3)實數s的值。")
        parts = [_point_part(1, rec["center"]["text"], "對稱中心"), _poly_part(2, rec["f"], "三次函數 f(x)"), _num_part(3, rec["s"]["canonical"], "s")]
        h, k = rec["center"]["x"], rec["center"]["y"]
        steps = [f"(1) A、B 對稱於對稱中心，所以中心是 A、B 的中點 ${rec['center']['text']}$。",
                 f"(2) 設 {_t('f(x)=a(x-' + _lat(h) + ')^{3}+p(x-' + _lat(h) + ')+' + _lat(k))}。圖形通過 $O(0,0)$ 與 $A({_lat(ax)},{_lat(ay)})$，解聯立得 "
                 f"$a={rec['a']['latex']}$、$p={rec['p']['latex']}$，所以 {_t('f(x)=' + rec['f']['latex'])}。",
                 f"(3) $s=f({_lat(cx)})={rec['s']['latex']}$。"]
        return _parts_payload(matrix, question=question, parts=parts,
                              display_answer=f"(1) ${rec['center']['text']}$；(2) ${rec['f']['latex']}$；(3) ${rec['s']['latex']}$", explanation_steps=steps,
                              shape="cubic_route_center_function_value")
    if kind == "center_zero_linear":
        cx, cy = it["center"]
        question = ("起飛及降落是飛機飛行中最危險的時刻，所以這期間的飛行路徑至關重要。假設某飛機由起飛點 $(0,0)$ 起飛的路徑恰與由從起降點降落的路徑相同，"
                    "差別只在起飛與降落是沿著相反的方向進行。\n"
                    f"有一位數學工作者想尋找一個三次函數 {_t('f(x)')}，讓函數 {_t('y=f(x)')} 的圖形在這一段剛好與飛行路徑一致，"
                    f"而且飛行路徑的中間點 ${'(' + _lat(cx) + ',' + _lat(cy) + ')'}$ 剛好是該三次函數圖形的「對稱中心」。"
                    f"為了使起飛更加安全，會進一步要求 {_t('f(x)')} 的一次項係數為零。\n請根據上述描述，回答下列問題：\n(1)求起降點的坐標。\n(2)求三次函數 {_t('f(x)')}。")
        parts = [_point_part(1, rec["landing"]["text"], "起降點坐標"), _poly_part(2, rec["f"], "三次函數 f(x)")]
        steps = [f"(1) 起飛點 $O$ 與起降點對稱於中間點 $({_lat(cx)},{_lat(cy)})$，所以起降點為 ${rec['landing']['text']}$。",
                 f"(2) 設 {_t('f(x)=ax^{3}+bx^{2}+cx+d')}。過原點得 $d=0$，一次項係數為零得 $c=0$；對稱中心的橫坐標 $-\\frac{{b}}{{3a}}={_lat(cx)}$ 且 $f({_lat(cx)})={_lat(cy)}$，"
                 f"解得 {_t('f(x)=' + rec['f']['latex'])}。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1) ${rec['landing']['text']}$；(2) ${rec['f']['latex']}$",
                              explanation_steps=steps, shape="cubic_flight_path")
    if kind == "global_local":
        h = fr(it["h"])
        question = (f"設三次函數 {_t('y=f(x)=a' + _paren_cube(h) + '+b' + _paren(h) + '+c')}。已知廣域看 {_t('y=f(x)')} 的圖形會很接近 "
                    f"{_t('y=' + _lead_cube(it['lead']))} 的圖形，而局部看 {_t('y=f(x)')} 在 {_t('x=' + _lat(h))} 附近的圖形卻近似於直線 "
                    f"{_t('y=' + _line_tex(it['slope'], it['intercept']))}，求實數 {_t('a, b, c')} 的值。")
        parts = [_num_part(1, rec["a"]["canonical"], "a"), _num_part(2, rec["b"]["canonical"], "b"), _num_part(3, rec["c"]["canonical"], "c")]
        steps = [f"廣域看，圖形接近最高次項 $ax^{{3}}$ 所代表的 {_t('y=' + _lead_cube(it['lead']))}，所以 $a={rec['a']['latex']}$。",
                 f"局部看，在 $x={_lat(h)}$ 附近 $f(x)\\approx b(x-({_lat(h)}))+c$，要與直線 {_t('y=' + _line_tex(it['slope'], it['intercept']))} 一致，"
                 f"所以 $b={rec['b']['latex']}$，$c$ 為直線在 $x={_lat(h)}$ 的值：$c={rec['c']['latex']}$。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"a={rec['a']['canonical']}，b={rec['b']['canonical']}，c={rec['c']['canonical']}",
                              explanation_steps=steps, shape="cubic_global_local_abc")
    raise ValueError(kind)


def _paren(h: Fraction) -> str:
    return f"\\left({_xh(fr(h))}\\right)"


def _paren_cube(h: Fraction) -> str:
    return _paren(h) + "^{3}"


def _lead_cube(a: Any) -> str:
    a = fr(a)
    return ("" if a == 1 else ("-" if a == -1 else _lat(a))) + "x^{3}"


def _line_tex(m: Any, n: Any) -> str:
    m, n = fr(m), fr(n)
    text = ("" if m == 1 else ("-" if m == -1 else _lat(m))) + "x"
    return text + ("" if n == 0 else ("+" if n > 0 else "-") + _lat(abs(n)))


# --- C. cubic_statements ------------------------------------------------------------------------

_DECIMAL_WORDS = {1: "一", 2: "二", 3: "三", 4: "四"}


def _sentence(subject: dict[str, Any], st: dict[str, Any]) -> str:
    kind = st["kind"]
    x0call = lambda arg: f"f\\left({arg}\\right)"  # noqa: E731
    if kind == "value_attained":
        v = _lat(st["value"])
        eq = _t("f\\left(x_{0}\\right)=" + v)
        x0 = _t("x_{0}")
        return f"可以找到一個實數 {x0} 滿足 {eq}" if st["claim"] == "exists" else f"不存在任何實數 {x0} 使得 {eq}"
    if kind == "x_axis_meets":
        return f"{_t('y=f(x)')} 的圖形與 $x$ 軸" + ("至少交一點" if st["claim"] == "at_least_one" else "至多交兩點")
    if kind == "axis_of_symmetry":
        return f"{_t('y=f(x)')} 圖形的對稱軸為直線 {_t('x=' + _lat(st['claimed_x']))}"
    if kind == "center_on_curve_at":
        xm = _lat(st["x"])
        centre = _t("\\left(" + xm + ",\\ f\\left(" + xm + "\\right)\\right)")
        return f"{_t('y=f(x)')} 圖形的對稱中心為 {centre}"
    if kind == "center_is":
        return f"點 {_t('(' + _lat(st['x']) + ',' + _lat(st['y']) + ')')} 是圖形的對稱中心"
    if kind == "symmetric_mean":
        xm, x1, x2 = (_lat(st[k]) for k in ("xm", "x1", "x2"))
        return _t(f"f\\left({xm}\\right)=\\frac{{1}}{{2}}\\left(f\\left({x1}\\right)+f\\left({x2}\\right)\\right)")
    if kind == "odd_function":
        return _t("f\\left(-x\\right)=-f\\left(x\\right)")
    if kind == "global_extremum":
        value = f"{_lat(st['value'])}" if "value" in st else ""
        words = {"max": f"函數 {_t('f(x)')} 有最大值{(' ' + _t(value)) if value else ''}", "min": f"函數 {_t('f(x)')} 有最小值{(' ' + _t(value)) if value else ''}",
                 "none": f"函數 {_t('f(x)')} 沒有最大值，也沒有最小值"}
        return words[st["claim"]]
    if kind == "local_line":
        x0, m, n = fr(st["x0"]), fr(st["m"]), fr(st["n"])
        y0 = m * x0 + n
        inner = _xh(x0)
        line = _line_tex(m, n) if st.get("style") == "slope_intercept" else f"{'' if m == 1 else ('-' if m == -1 else _lat(m))}\\left({inner}\\right)" + ("" if y0 == 0 else ("+" if y0 > 0 else "-") + _lat(abs(y0)))
        return f"局部看 {_t('y=f(x)')} 在 {_t('x=' + _lat(x0))} 附近的圖形近似於直線 {_t('y=' + line)}"
    if kind == "value_approx":
        approx = _t("f\\left(" + _approx_tex(st["x"]) + "\\right)\\approx " + _approx_tex(st["approx"]))
        return f"{approx}（四捨五入至小數點以下第{_DECIMAL_WORDS[int(st['decimals'])]}位）"
    if kind == "translate_overlap":
        k = st.get("k", 0)
        return f"{_t('y=f(x)')} 的圖形可經由適當的平移與 {_t('y=' + _poly_tex([st['a'], 0, st['p'], k]))} 的圖形完全重疊"
    if kind == "point_shift_on_graph":
        def off(var: str, d: Any) -> str:
            d = fr(d)
            return var if d == 0 else f"{var}{'+' if d > 0 else '-'}{_lat(abs(d))}"
        return f"若點 {_t('(r,s)')} 在 {_t('y=f(x)')} 的圖形上，則點 {_t('(' + off('r', st['dx']) + ',' + off('s', st['dy']) + ')')} 也在 {_t('y=f(x)')} 的圖形上"
    if kind == "constant_claim":
        return _t(f"k={_lat(st['claimed'])}")
    raise ValueError(f"unknown_statement:{kind}")


def _reason(subject: dict[str, Any], st: dict[str, Any], truth: bool, answer: dict[str, Any]) -> str:
    kind = st["kind"]
    center = answer.get("center", {}).get("text")
    if kind == "value_attained":
        return "三次函數的值域是全體實數，所以每個實數值都可以取到。" if truth else "三次函數的值域是全體實數，任何值都取得到，所以這句話不對。"
    if kind == "x_axis_meets":
        return "三次方程式至少有一個實根，所以圖形至少與 $x$ 軸交一點。" if truth else "圖形與 $x$ 軸的交點數要看實根個數，這個敘述與實根個數不符。"
    if kind == "axis_of_symmetry":
        return "三次函數的圖形是點對稱圖形（對稱中心），沒有對稱軸。"
    if kind == "center_on_curve_at":
        return f"對稱中心的橫坐標為 $-\\frac{{b}}{{3a}}$，該圖形的對稱中心橫坐標是 ${_lat(answer['h']['canonical'])}$。" + ("與敘述一致。" if truth else "與敘述不一致。") if "h" in answer else ""
    if kind == "center_is":
        return f"此函數圖形的對稱中心為 ${center}$。" + ("" if truth else "敘述所給的點不是對稱中心。")
    if kind == "symmetric_mean":
        return "$x_{1}$、$x_{2}$ 對稱於對稱中心的橫坐標，所以 $f$ 在中心的值是兩側對稱兩點函數值的平均。" if truth else "此式與對稱關係不符。"
    if kind == "odd_function":
        return "$f(-x)=-f(x)$ 代表圖形對稱於原點，這個函數的對稱中心不是原點，所以不成立。" if not truth else "圖形對稱於原點，所以成立。"
    if kind == "global_extremum":
        return "三次函數的值向兩端無限增大與減小，沒有最大值也沒有最小值。"
    if kind == "local_line":
        return "在 $x=x_{0}$ 附近的局部圖形近似於過該點的切線 $y=f'(x_{0})(x-x_{0})+f(x_{0})$。" + ("此敘述的直線與切線一致。" if truth else "此敘述的直線與切線不一致。")
    if kind == "value_approx":
        return "展開成 $(x-h)$ 的多項式後，高次項很小可以忽略，再把數值四捨五入至指定位數。" + ("所得結果與敘述一致。" if truth else "所得結果與敘述不符。")
    if kind == "translate_overlap":
        return "兩個三次函數能經由平移重疊，需要 $a$ 與 $p$ 都相同。" + ("兩者相同。" if truth else "兩者不全相同。")
    if kind == "point_shift_on_graph":
        return "三次函數的圖形不會因為一個非零的平移而與自己重合，所以這個敘述不成立。" if not truth else "平移量為零時敘述成立。"
    if kind == "constant_claim":
        return "把對稱中心的坐標代入函數可求得 $k$。" + ("與敘述一致。" if truth else "與敘述不一致。")
    return ""


def _statement_intro(subject: dict[str, Any], mode: str) -> str:
    stype = subject["type"]
    if stype == "free_cd":
        return f"設三次函數 {_t('f(x)=' + _poly_tex(list(subject['coeffs']) + [0, 0]) + '+cx+d')}，其中 $c, d$ 為實數，選出所有正確的選項。"
    if stype == "cubic_with_center":
        c = subject["center"]
        fx = "f(x)=" + _poly_tex(list(subject["coeffs"]) + [0]) + "+k"
        return f"已知三次函數 {_t(fx)} 圖形的對稱中心為 {_t('(' + _lat(c[0]) + ',' + _lat(c[1]) + ')')}，選出所有正確的選項。"
    expr = _form_tex(subject["a"], subject["p"], subject["h"], subject["k"]) if stype == "form" else _poly_tex(subject["coeffs"])
    if mode == "truth":
        return f"關於三次函數 {_t('y=f(x)=' + expr)}。以下各小題對的打「○」，錯的打「×」。"
    return f"設三次函數 {_t('y=f(x)=' + expr)}，選出所有正確的選項。"


def _cubic_statements(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    subject, sts, mode = givens["subject"], givens["statements"], answer["mode"]
    sentences = [_sentence(subject, st) for st in sts]
    intro = _statement_intro(subject, mode)
    if mode == "truth":
        truth = answer["truths"][0]
        question = intro + "\n" + sentences[0] + "。"
        part = _part(1, "A" if truth else "B", "choice_label_checker", "choice_label", "single_choice", choices=[dict(c) for c in TRUE_FALSE_CHOICES])
        steps = [f"{_reason(subject, sts[0], truth, answer)}此敘述為「{'○' if truth else '×'}」。"]
        return _single_payload(matrix, question=question, part=part, display_answer="○" if truth else "×", explanation_steps=steps, shape="single_choice")
    question = intro + "\n" + "\n".join(f"({i}) {s}" for i, s in enumerate(sentences, start=1))
    steps = [f"({i}) {'正確' if t else '錯誤'}。{_reason(subject, st, t, answer)}" for i, (st, t) in enumerate(zip(sts, answer["truths"]), start=1)]
    steps.append("正確的選項為 " + "".join(f"({i})" for i in answer["selected"]) + "。")
    return _single_payload(matrix, question=question, part=_selection_part(1, answer["selected"]),
                           display_answer="".join(f"({i})" for i in answer["selected"]), explanation_steps=steps, shape="selected_candidate_index_set")


# --- D. cubic_curve_matching --------------------------------------------------------------------

def _curve_figure(answer: dict[str, Any], colors: list[str], reference: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    window = answer["window"]
    curves = []
    for g in answer["gammas"]:
        name = colors[g["gamma"] - 1]
        curves.append({"points": g["points"], "color": COLORS[name], "label": GAMMA[g["gamma"]]})
    for ref, given in zip(answer.get("reference") or [], reference or []):
        curve = {"points": ref["points"], "color": COLORS["黑色"]}
        if given.get("label"):
            curve["label"] = given["label"]
        curves.append(curve)
    xr, yl = window["x"], window["y"]
    view = FG.fit_view([(-xr, -yl), (xr, yl)], pad=0, include_origin=True)
    return FG.plane(points=[FG.point_entry((0, 0), "O")], lines=[], view=view, extra={"show_grid": False, "curves": curves})


def _fn_tex(f: dict[str, Any]) -> str:
    return f.get("tex") or "y=" + _poly_tex(f["coeffs"])


def _cubic_curve_matching(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    funcs, colors = givens["functions"], givens["colors"]
    n = len(funcs)
    figure = _curve_figure(answer, colors, givens.get("reference"))
    if answer["kind"] == "compare":
        eqs = "、".join(_t(f"\\Gamma_{{{i}}}:y=a_{{{i}}}x^{{3}}") for i in range(1, n + 1))
        letters = [chr(ord("A") + i) for i in range(6)]
        orders = [list(perm) for perm in _permutations(n)]
        choices = [{"label": letters[i], "value": "$" + ">".join(f"a_{{{g}}}" for g in perm) + "$"} for i, perm in enumerate(orders)]
        question = f"如右圖，已知 {eqs}，\n比較 " + "、".join(_t(f"a_{{{i}}}") for i in range(1, n + 1)) + " 的大小關係。"
        expected = letters[orders.index(answer["ranking"])]
        steps = ["三次函數 $y=ax^{3}$ 在 $x=1$ 時的函數值就是 $a$：在 $x=1$ 處，曲線越高 $a$ 越大。",
                 "依圖形在 $x=1$ 處由高到低排列，得 " + _t(">".join(f"a_{{{g}}}" for g in answer["ranking"])) + "。"]
        part = _part(1, expected, "choice_label_checker", "choice_label", "single_choice", choices=choices)
        return _single_payload(matrix, question=question, part=part, display_answer="$" + ">".join(f"a_{{{g}}}" for g in answer["ranking"]) + "$",
                               explanation_steps=steps, shape="single_choice", visual_spec=figure)
    legend = "、".join(f"{_t(chr(92) + 'Gamma_{' + str(g) + '}')}（{colors[g - 1]}曲線）" for g in range(1, n + 1))
    lines = "\n".join(f"({i}) {_t(_fn_tex(f))}" for i, f in enumerate(funcs, start=1))
    preface = givens.get("preface", "")
    question = f"（連連看）{preface}{'請' if preface else ''}將下列函數連到所對應的函數圖形之代號上，如右圖：\n{lines}\n圖形代號：{legend}。"
    choices = [{"label": chr(ord("A") + g), "value": f"{GAMMA[g + 1]}（{colors[g]}曲線）"} for g in range(n)]
    parts, steps = [], []
    for i, f in enumerate(funcs):
        gamma = answer["assignment"][i]
        parts.append(_choice_part(i + 1, chr(ord("A") + gamma - 1), choices, f"({i + 1}) " + _t(_fn_tex(f))))
        steps.append(f"({i + 1}) {_t(_fn_tex(f))} 的圖形是{GAMMA[gamma]}（{colors[gamma - 1]}曲線）。")
    shown = "；".join(f"({i + 1}) {GAMMA[answer['assignment'][i]]}" for i in range(n))
    return _parts_payload(matrix, question=question, parts=parts, display_answer=shown, explanation_steps=steps, shape="cubic_curve_matching", visual_spec=figure)


def _permutations(n: int) -> list[tuple[int, ...]]:
    import itertools

    return list(itertools.permutations(range(1, n + 1)))


# --- E. graph_cubic_functions (drawing) ----------------------------------------------------------

_UI_CONTRACT = {
    "response_mode": "drawing", "drawing_required": True, "ai_check_required": True, "text_answer_enabled": False,
    "text_input_enabled": False, "submit_button_enabled": False, "normal_submit_enabled": False, "success_dialog_required": True,
    "canvas_required": True, "allow_image_upload": False, "allow_text_answer": False,
}


def _drawing_part(index: int, spec: dict[str, Any], label: str, prompt: str) -> dict[str, Any]:
    return {
        **_part(index, spec, "free_response_drawing_checker", "drawing_equivalence", "drawing"),
        "label": label, "prompt": prompt, "input_type": "canvas",
        "canvas": {"axis_range": dict(spec["axis_range"]), "show_grid": True},
        "expected_drawing_spec": spec, "drawing_required": True, "ai_check_required": True, "text_answer_enabled": False,
    }


def _cubic_spec(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "drawing_type": "cubic_graph", "graph_kind": "cubic_graph",
        "expected_cubics": [{"a": float(fr(rec["a"]["canonical"])), "p": float(fr(rec["p"]["canonical"])),
                             "center": [float(fr(rec["h"]["canonical"])), float(fr(rec["k"]["canonical"]))],
                             "turning_points": [list(t) for t in rec["turning"]], "x_intercepts": list(rec["zeros"]),
                             "points": [[float(fr(x)), float(fr(y))] for x, y in rec["points"]]}],
        "required_elements": ["x_axis", "y_axis", "cubic_curve"], "axis_range": dict(rec["axis_range"]),
    }


def _item_tex(it: dict[str, Any]) -> str:
    if "form" in it:
        f = it["form"]
        return _form_tex(f["a"], f["p"], f["h"], f["k"])
    return _poly_tex(it["coeffs"])


def _graph_cubic_functions(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    it, rec, ask = givens["items"][0], answer["items"][0], answer["ask"]
    expr = _item_tex(it)
    form_tex = _form_tex(rec["a"]["canonical"], rec["p"]["canonical"], rec["h"]["canonical"], rec["k"]["canonical"])
    parts: list[dict[str, Any]] = []
    steps: list[str] = []
    shown: list[str] = []
    if "form" in ask:
        equation = "y=" + expr + "=a\\left(x-h\\right)^{3}+p\\left(x-h\\right)+k"
        question = (f"設三次函數 {_t(equation)}。\n(1)求實數 {_t('a, p, h, k')} 的值。\n"
                    f"(2)描繪 {_t('y=' + expr)} 的圖形" + ("，並求其對稱中心。" if "center" in ask else "。"))
        for name in ("a", "p", "h", "k"):
            parts.append(_num_part(len(parts) + 1, rec[name]["canonical"], f"(1) {name}"))
        steps.append(f"(1) 三次項與二次項係數決定對稱中心的橫坐標 $h={rec['h']['latex']}$；把 $x=t+h$ 代入並展開得 {_t('y=' + form_tex)}，"
                     f"所以 $a={rec['a']['latex']}$、$p={rec['p']['latex']}$、$h={rec['h']['latex']}$、$k={rec['k']['latex']}$。")
        shown.append(f"(1) a={rec['a']['canonical']}，p={rec['p']['canonical']}，h={rec['h']['canonical']}，k={rec['k']['canonical']}")
        drawing_label, center_label = "(2) 圖形", "(2) 對稱中心"
    else:
        question = f"描繪 {_t('y=' + expr)} 的圖形" + ("，並求其對稱中心。" if "center" in ask else "。")
        drawing_label, center_label = "圖形", "對稱中心"
        steps.append(f"把函數寫成 {_t('y=' + form_tex)}，對稱中心為 $({rec['h']['latex']},{rec['k']['latex']})$。")
    spec = _cubic_spec(rec)
    feature_words = []
    if rec["turning"]:
        feature_words.append("有兩個轉折點（極大與極小），曲線先升後降再升（或相反）")
    else:
        feature_words.append("沒有轉折點，曲線一直上升或一直下降")
    steps.append("以對稱中心 $(" + f"{rec['h']['latex']},{rec['k']['latex']}" + ")$ 為中心，列出 $x=" + ",".join(frac_latex(fr(rec['h']['canonical']) + t) for t in (-2, -1, 0, 1, 2))
                 + "$ 的點，用描點法並利用對稱中心把圖形畫成平滑曲線；" + feature_words[0] + "。")
    parts.append(_drawing_part(len(parts) + 1, spec, drawing_label, "描繪三次函數圖形"))
    shown.append("圖形：以 " + rec["center"]["text"] + " 為對稱中心" + ("，有兩個轉折點" if rec["turning"] else "，單調"))
    if "center" in ask:
        parts.append(_point_part(len(parts) + 1, rec["center"]["text"], center_label))
        steps.append(f"對稱中心為點 ${rec['center']['text']}$。")
        shown.append(f"{center_label}：{rec['center']['text']}")
    if len(parts) == 1:
        visual = FG.blank_canvas([rec["axis_range"][k] for k in ("x_min", "x_max", "y_min", "y_max")])
        return _payload(matrix, question=question, answer=spec, display_answer="；".join(shown),
                        contract=_contract("drawing", "canvas", "free_response_drawing_checker", "drawing_equivalence", answer_shape="drawing",
                                           expected_drawing_spec=spec, ui_contract=dict(_UI_CONTRACT)),
                        explanation_steps=steps, visual_spec=visual)\
            | {"answer_shape": "drawing", "interaction_type": "handwriting_drawing", "expected_drawing_spec": spec,
               "metadata": {"expected_drawing_spec": spec, "ui_contract": dict(_UI_CONTRACT), "answer_type": "drawing", "answer_shape": "drawing"}}
    return _payload(matrix, question=question, answer={p["key"]: p["expected_answer"] for p in parts}, display_answer="；".join(shown),
                    contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer", answer_shape="cubic_drawing_with_numbers",
                                       parts=parts, drawing_parts=True),
                    explanation_steps=steps)


# --- F. cubic_option_graph (five option graphs) ---------------------------------------------------

_OPTION_COLOR = "#1565c0"
_SHAPE_WORDS = {"S_up": "由左下往右上、沒有轉折的 S 形", "S_down": "由左上往右下、沒有轉折的 S 形",
                "M_up": "先升後降再升（兩個轉折點，右端向上）", "M_down": "先降後升再降（兩個轉折點，右端向下）",
                "parabola_up": "開口向上的拋物線", "parabola_down": "開口向下的拋物線"}


def _option_figure(answer: dict[str, Any], slope: Fraction, intercept: Fraction) -> dict[str, Any]:
    figures = [{
        "id": "given_line", "label": "已知", "points": [{"x": 0, "y": 0, "label": "O"}],
        "lines": [{"through_points": [[0, float(intercept)], [1, float(slope + intercept)]], "extend": True}],
        "x_range": [-4, 4], "y_range": [-4, 4], "fixed_range": True, "show_grid": False,
    }]
    for panel in answer["panels"]:
        figures.append({"id": f"option_{panel['option']}", "label": f"({panel['option']})", "points": [], "lines": [],
                        "curves": [{"points": panel["points"], "color": _OPTION_COLOR}], "x_range": [2, 8], "y_range": [2, 8],
                        "fixed_range": True, "show_grid": False})
    return {"kind": "coordinate_plane_multi_figure", "figures": figures, "x_range": [-4, 4], "y_range": [-4, 4], "render_required": True, "show_grid": False}


def _cubic_option_graph(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    m, b = fr(givens["slope"]), fr(givens["intercept"])
    letters = "ABCDE"
    choices = [{"label": letters[i], "value": f"圖({i + 1})"} for i in range(5)]
    question = (f"已知一次函數 {_t('y=ax+b')} 的圖形如右圖，下列哪一個選項的圖形最接近三次函數 {_t('y=ax^{3}+bx')} 的圖形？")
    correct = answer["correct_option"]
    sign_a, sign_b = ("正" if m > 0 else "負"), ("正" if b > 0 else "負")
    steps = [f"由一次函數的圖形可知斜率 $a$ 為{sign_a}數，$y$ 截距 $b$ 為{sign_b}數。",
             f"三次函數 {_t('y=ax^{3}+bx')} 的 $a$ 與 $p=b$ 的符號{'相同' if (m > 0) == (b > 0) else '相反'}："
             + ("沒有轉折點，" if (m > 0) == (b > 0) else "有兩個轉折點，")
             + f"右端{'向上' if m > 0 else '向下'}，圖形是{_SHAPE_WORDS[answer['wanted_shape']]}。",
             f"選項 ({correct}) 的圖形符合，其他選項的走向或轉折點個數不符。"]
    part = _part(1, letters[correct - 1], "choice_label_checker", "choice_label", "single_choice", choices=[dict(c) for c in choices])
    return _single_payload(matrix, question=question, part=part, display_answer=f"({correct})", explanation_steps=steps, shape="single_choice",
                           visual_spec=_option_figure(answer, m, b))


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "cubic_center_form": _cubic_center_form,
    "cubic_from_conditions": _cubic_from_conditions,
    "cubic_statements": _cubic_statements,
    "cubic_curve_matching": _cubic_curve_matching,
    "graph_cubic_functions": _graph_cubic_functions,
    "cubic_option_graph": _cubic_option_graph,
}


def adapt_cubic_graph_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_cubic_graph_operation:{operation}")
    return builder(matrix)
