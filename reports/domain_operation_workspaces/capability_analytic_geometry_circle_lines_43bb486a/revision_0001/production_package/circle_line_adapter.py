"""Question payload contracts for analytic_geometry.circle_line_relations.

Every payload is graded by a shared checker registered in ``CHECKER_CAPABILITIES``; the expected
answers always come from the domain matrix, never from this adapter.  Figures are plain
``visual_spec`` data for the shared coordinate-plane renderer and are rebuilt from the same givens as
the stem, so a varied question never shows a stale picture.  Measured figures switch the unit grid
off (``show_grid: false``) so lengths cannot be read off the squares.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable

from core.domain.promoted.analytic_geometry_lines import figures as FG

from .circle_line_domain import DOMAIN_KEY
from .circle_line_geometry import G, circle_of, fr, frac_latex, frac_text, pdeg, poly, pt, radical_of_fraction

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
RELATION_CHOICES = (("secant", "相交於兩點"), ("tangent", "相切（交於一點）"), ("disjoint", "不相交"))
RELATION_ZH = dict(RELATION_CHOICES)
NONE_MARK = "無"

_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_RADICAL = ("expression_equivalence_checker", "radical_equivalence", "numeric_or_radical")
_POINT = ("coordinate_pair_checker", "coordinate_pair_equivalence", "coordinate_pair")
_NONE = ("text_short_checker", "normalized_text_equivalence", "short_answer")
_EQUATION = ("equation_checker", "equation_equivalent", "equation")
_LINE = ("linear_equation_equivalent_checker", "linear_equation_equivalent", "equation")
_LINES = ("linear_relation_set_checker", "linear_relation_set", "short_answer")
_REGION = ("inequality_solution_checker", "inequality_solution_equivalence", "inequality")
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


def _payload(matrix, *, question, answer, display_answer, contract, explanation_steps, choices=(), visual_spec=None) -> dict[str, Any]:
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
        "math_core": {
            "givens": matrix["givens"],
            "target": matrix["answer"],
            "validation_facts": matrix["validation_facts"],
        },
    }
    if visual_spec:
        payload["visual_spec"] = visual_spec
        payload["visual_backed"] = bool(visual_spec.get("render_required"))
    return payload


def _parts_payload(matrix, *, question, parts, display_answer, explanation_steps, shape, visual_spec=None) -> dict[str, Any]:
    if len(parts) == 1:
        return _single_payload(matrix, question=question, part=parts[0], display_answer=display_answer,
                               explanation_steps=explanation_steps, shape=shape, visual_spec=visual_spec)
    return _payload(
        matrix,
        question=question,
        answer={part["key"]: part["expected_answer"] for part in parts},
        display_answer=display_answer,
        contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer",
                           answer_shape=shape, parts=parts),
        explanation_steps=explanation_steps,
        visual_spec=visual_spec,
    )


def _single_payload(matrix, *, question, part, display_answer, explanation_steps, shape, visual_spec=None) -> dict[str, Any]:
    skip = ("key", "label", "checker", "checker_key", "equivalence_type", "answer_type", "expected_answer", "prompt")
    contract_extra = {k: v for k, v in part.items() if k not in skip}
    if part["answer_type"] == "single_choice":
        return _payload(
            matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
            contract=_contract("single_choice", "single_choice", "choice_label_checker", "choice_label",
                               answer_shape="single_choice", choices=[dict(c) for c in part["choices"]]),
            explanation_steps=explanation_steps, choices=part["choices"], visual_spec=visual_spec,
        )
    return _payload(
        matrix,
        question=question,
        answer=part["expected_answer"],
        display_answer=display_answer,
        contract=_contract(part["answer_type"], "short_answer", part["checker"], part["equivalence_type"],
                           answer_shape=shape, **contract_extra),
        explanation_steps=explanation_steps,
        visual_spec=visual_spec,
    )


def _choice_part(index: int, key: str, options: tuple[tuple[str, str], ...], prompt: str) -> dict[str, Any]:
    """Select part: the expected answer is the 1-based position label of ``key`` in ``options``."""
    choices = [{"label": str(i), "value": text, "text": text} for i, (_k, text) in enumerate(options, start=1)]
    position = [k for k, _t in options].index(key) + 1
    return _part(index, str(position), "choice_label_checker", "choice_label", "single_choice", choices=choices, prompt=prompt)


# --- LaTeX rendering of the givens -------------------------------------------------------------

def _t(text: str) -> str:
    return f"${text}$"


def _num(v: Any) -> str:
    return frac_latex(fr(v))


def _coef_tex(p: list, param: str) -> tuple[int, str]:
    """(sign, magnitude text) of a coefficient polynomial ``c0 + c1 * param``; sign 0 means zero."""
    if pdeg(p) < 0:
        return 0, ""
    if pdeg(p) == 0:
        c = p[0]
        return (1 if c > 0 else -1), frac_latex(abs(c))
    c0, c1 = (p + [Fraction(0)])[:2]
    if pdeg(p) > 1:
        raise ValueError("display_supports_linear_parameters_only")
    if c0 == 0:
        return (1 if c1 > 0 else -1), ("" if abs(c1) == 1 else frac_latex(abs(c1))) + param
    inner = f"{frac_latex(c0)}{'+' if c1 > 0 else '-'}{'' if abs(c1) == 1 else frac_latex(abs(c1))}{param}"
    return 1, f"\\left({inner}\\right)"


def _terms_tex(terms: list[tuple[Any, str]], param: str) -> str:
    out = ""
    for value, symbol in terms:
        sign, mag = _coef_tex(poly(value), param)
        if sign == 0:
            continue
        if symbol and mag == "1":
            mag = ""
        out += ("-" if sign < 0 else ("+" if out else "")) + mag + symbol
    return out or "0"


def _shift(var: str, centre: Any) -> str:
    c = fr(centre)
    if c == 0:
        return f"{var}^{{2}}"
    return f"\\left({var}{'-' if c > 0 else '+'}{frac_latex(abs(c))}\\right)^{{2}}"


def circle_tex(spec: dict[str, Any], param: str = "k", show_r: bool = False) -> str:
    if "d" in spec:
        return "x^{2}+y^{2}" + _general_tail(spec, param)
    h, k, r2 = circle_of(spec)
    rhs = frac_latex(r2)
    if show_r:
        root = radical_of_fraction(r2)
        if root.is_rational():
            rhs = f"{frac_latex(root.coef)}^{{2}}"
    return f"{_shift('x', h)}+{_shift('y', k)}={rhs}"


def _general_tail(spec: dict[str, Any], param: str) -> str:
    tail = _terms_tex([(spec["d"], "x"), (spec["e"], "y"), (spec["f"], "")], param)
    if tail == "0":
        return "=0"
    return ("" if tail.startswith("-") else "+") + tail + "=0"


def line_tex(spec: Any, form: str = "general", param: str = "k") -> str:
    a, b, c = (spec["a"], spec["b"], spec["c"]) if isinstance(spec, dict) else spec
    if form == "slope":
        pb = poly(b)
        if pdeg(pb) != 0:
            raise ValueError("slope_form_needs_a_constant_y_coefficient")
        inv = -1 / pb[0]
        slope = [v * inv for v in poly(a)]
        icpt = [v * inv for v in poly(c)]
        return "y=" + _terms_tex([(slope, "x"), (icpt, "")], param)
    if form == "rhs":
        return _terms_tex([(a, "x"), (b, "y")], param) + "=" + _terms_tex([([-v for v in poly(c)], "")], param)
    return _terms_tex([(a, "x"), (b, "y"), (c, "")], param) + "=0"


def _line_display(line: list[int]) -> str:
    a, b, c = line
    if b == 0:
        return f"x={frac_latex(Fraction(-c, a))}"
    if a == 0:
        return f"y={frac_latex(Fraction(-c, b))}"
    return G.line_text(tuple(line))


def _point_tex(p: Any, name: str = "") -> str:
    return G.point_latex(pt(p), name)


def _point_display(rec: dict[str, Any]) -> str:
    x, y = rec["point"]
    return _t(f"\\left({_num(x)},\\ {_num(y)}\\right)")


def _value_display(rec: dict[str, Any]) -> str:
    kind = rec["kind"]
    if kind == "radical":
        return _t(rec["latex"])
    if kind == "rational":
        return _t(_num(rec["canonical"]))
    if kind == "point":
        return _point_display(rec)
    if kind == "line":
        return _t(_line_display(rec["line"]))
    if kind == "lines":
        return "、".join(_t(_line_display(ln)) for ln in rec["lines"])
    if kind == "equation":
        return _t(rec["latex"])
    if kind == "set":
        return "、".join(_t(_num(v)) for v in rec["values"])
    if kind == "region":
        return _t(rec["latex"])
    raise ValueError(f"unknown_record_kind:{kind}")


def _value_part(index: int, rec: dict[str, Any], prompt: str) -> dict[str, Any]:
    kind = rec["kind"]
    if kind == "radical":
        return _part(index, rec["canonical"], *_RADICAL, prompt=prompt, answer_format_example="3+√5")
    if kind == "rational":
        return _part(index, rec["canonical"], *_RATIONAL, prompt=prompt)
    if kind == "point":
        return _part(index, rec["text"], *_POINT, prompt=prompt)
    if kind == "line":
        return _part(index, rec["text"], *_LINE, prompt=prompt)
    if kind == "lines":
        if len(rec["lines"]) == 1:
            return _part(index, G.line_text(tuple(rec["lines"][0])), *_LINE, prompt=prompt)
        return _part(index, rec["text"], *_LINES, prompt=prompt, required_form="linear_relation_set",
                     answer_format_example="x-y-3=0, x+y-7=0")
    if kind == "equation":
        return _part(index, rec["text"], *_EQUATION, prompt=prompt, answer_format_example="x^2+(y-6)^2=52")
    if kind == "set":
        return _part(index, list(rec["values"]), *_SET, prompt=prompt, solution_members="exact_rational",
                     answer_format_example="3, -5")
    if kind == "region":
        return _part(index, rec["text"], *_REGION, prompt=prompt, answer_format_example="-26<k<4")
    raise ValueError(f"unknown_record_kind:{kind}")


def _with_prompts(question: str, parts: list[dict[str, Any]]) -> str:
    if len(parts) == 1:
        return question
    return question + "\n" + "\n".join(f"{p['label']} {p['prompt']}" for p in parts)


# --- figures -----------------------------------------------------------------------------------

def _f(v: Any) -> float:
    return float(fr(v))


def _arc_curves(h: float, k: float, r: float, y_floor: float, color: str = "#1565c0", samples: int = 90) -> list[dict[str, Any]]:
    """Part of a circle above ``y = y_floor`` as polylines sampled at uniform x (renderer gap rule)."""
    curves = []
    upper = [[h - r + 2 * r * i / samples, 0.0] for i in range(samples + 1)]
    for p in upper:
        p[1] = k + max(0.0, r * r - (p[0] - h) ** 2) ** 0.5
    curves.append({"points": upper, "color": color})
    if y_floor < k:
        half = max(0.0, r * r - (y_floor - k) ** 2) ** 0.5  # x-offset of the floor intersections
        for sign in (-1, 1):
            lo, hi = sorted((h + sign * half, h + sign * r))
            side = [[lo + (hi - lo) * i / 40, 0.0] for i in range(41)]
            for p in side:
                p[1] = k - max(0.0, r * r - (p[0] - h) ** 2) ** 0.5
            curves.append({"points": side, "color": color})
    return curves


def _plane(points: list[dict[str, Any]], lines: list[dict[str, Any]], extent: list[Any], extra: dict[str, Any], pad: int = 1) -> dict[str, Any]:
    view = FG.fit_view(extent, pad=pad, include_origin=True)
    return FG.plane(points=points, lines=lines, view=view, extra={"show_grid": False, **extra})


def _building_figure(center_y: Any, point: Any, answer: dict[str, Any]) -> dict[str, Any]:
    k = fr(center_y)
    p = pt(point)
    r2 = fr(answer["r2"])
    r = radical_of_fraction(r2).value()
    half = (float(r2) - float(k) ** 2) ** 0.5
    q = (_f(answer["q"][0]), 0.0) if "q" in answer else (_f(answer["values"][2]["point"][0]), 0.0)
    a, b = (-half, 0.0), (half, 0.0)
    beyond_p = (float(p[0]) - (q[0] - float(p[0])) * 0.35, float(p[1]) + float(p[1]) * 0.35)
    beyond_q = (q[0] + (q[0] - float(p[0])) * 0.12, -float(p[1]) * 0.12)
    points = [FG.point_entry(a, "A"), FG.point_entry(b, "B"), FG.point_entry((0, 0), "O"),
              FG.point_entry((0, k), f"M({frac_text(Fraction(0))},{frac_text(k)})"),
              FG.point_entry(p, f"P({frac_text(p[0])},{frac_text(p[1])})"), FG.point_entry(q, "Q")]
    lines = [FG.through_line(a, b, extend=False), FG.through_line(beyond_p, beyond_q, extend=False)]
    extent = [a, b, q, beyond_p, beyond_q, (-r, float(k) + r), (r, float(k) + r)]
    return _plane(points, lines, extent, {"curves": _arc_curves(0.0, float(k), r, 0.0)})


def _light_figure(givens: dict[str, Any], answer: dict[str, Any]) -> dict[str, Any]:
    h, k, r2 = circle_of(givens["circle"])
    light = pt(givens["light"])
    xp, xq = (_f(v) for v in answer["feet"])
    points = [FG.point_entry(light, f"A({frac_text(light[0])},{frac_text(light[1])})"), FG.point_entry((xp, 0), "P"),
              FG.point_entry((xq, 0), "Q"), FG.point_entry((0, 0), "O")]
    lines = [FG.through_line(light, (xp, 0), extend=False), FG.through_line(light, (xq, 0), extend=False)]
    r = radical_of_fraction(r2).value()
    circles = [{"h": float(h), "k": float(k), "r": r, "label": "", "show_center": False}]
    extent = [light, (xp, 0), (xq, 0), (float(h) - r, float(k) - r), (float(h) + r, float(k) + r)]
    return _plane(points, lines, extent, {"circles": circles})


def _badge_figure(givens: dict[str, Any], answer: dict[str, Any]) -> dict[str, Any]:
    w, cy, od = fr(givens["width"]), fr(givens["center_height"]), fr(givens["od"])
    e_y, top = (fr(rec["canonical"]) for rec in answer["values"])
    o, a, b, c, d, e = (0, 0), (w, 0), (w, top), (0, top), (od, 0), (w, e_y)
    points = [FG.point_entry(o, "O"), FG.point_entry(a, "A"), FG.point_entry(b, "B"), FG.point_entry(c, "C"),
              FG.point_entry(d, "D"), FG.point_entry(e, "E")]
    lines = [FG.through_line(o, a, extend=False), FG.through_line(c, d, extend=False), FG.through_line(a, b, extend=False),
             FG.through_line(d, e, extend=False), FG.through_line(b, c, extend=False), FG.through_line(c, o, extend=False)]
    r = radical_of_fraction(fr(givens["r2"])).value()
    circles = [{"h": float(w) / 2, "k": float(cy), "r": r, "label": "", "show_center": False}]
    return _plane(points, lines, [o, a, b, c], {"circles": circles})


# --- 1. classify_circle_line_relations ---------------------------------------------------------

def _line_names(count: int) -> list[str]:
    return ["L"] if count == 1 else [f"L_{{{i}}}" for i in range(1, count + 1)]


def _classify_circle_line_relations(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    lines, items = givens["lines"], answer["lines"]
    form = givens.get("line_form", "general")
    names = _line_names(len(lines))
    c_tex = circle_tex(givens["circle"], show_r=bool(givens.get("show_r")))
    ask_points = bool(givens.get("ask_points"))
    style = givens.get("style", "")
    clause = "（若相交，求出它們的交點）" if ask_points else ("（相交於兩點、相切或不相交）" if style == "three_cases" else "")
    if len(lines) == 1:
        if style == "given_pair":
            question = (f"已知圓 $C$ 和直線 $L$ 的方程式如下：\n{_t('C:' + c_tex)}、{_t('L:' + line_tex(lines[0], form))}。\n"
                        f"判斷圓 $C$ 和直線 $L$ 的相交情形{clause}。")
        else:
            question = f"判斷圓 {_t('C:' + c_tex)} 與直線 {_t('L:' + line_tex(lines[0], form))} 的相交情形{clause}。"
    else:
        listed = " ".join(f"({i}){_t(n + ':' + line_tex(ln, form))}。" for i, (n, ln) in enumerate(zip(names, lines), start=1))
        question = f"分別判斷圓 {_t('C:' + c_tex)} 與下列直線的相交情形{clause}：\n{listed}"
    parts: list[dict[str, Any]] = []
    steps, display = [], []
    r_tex = radical_of_fraction(fr(answer["r2"])).latex()
    for no, (name, item) in enumerate(zip(names, items), start=1):
        who = f"圓 $C$ 與直線 ${name}$ " if len(lines) > 1 else "圓 $C$ 與直線 $L$ "
        parts.append(_choice_part(len(parts) + 1, item["relation"], RELATION_CHOICES, f"{who}的相交情形"))
        d = G.radical_of_ratio(fr(item["side"]), int(item["normal2"]))
        cmp = {"secant": "<", "tangent": "=", "disjoint": ">"}[item["relation"]]
        step = f"圓心到 ${name}$ 的距離為 ${d.latex()}$，與半徑 ${r_tex}$ 比較：${d.latex()}{cmp}{r_tex}$，所以{RELATION_ZH[item['relation']]}。"
        shown = RELATION_ZH[item["relation"]]
        if ask_points:
            pts = item["points"]
            first = _part(len(parts) + 1, pts[0]["text"], *_POINT, prompt=f"{who}的交點坐標（$x$ 坐標較小者；若不相交填「{NONE_MARK}」）") \
                if pts else _part(len(parts) + 1, NONE_MARK, *_NONE, prompt=f"{who}的交點坐標（$x$ 坐標較小者；若不相交填「{NONE_MARK}」）")
            parts.append(first)
            second_prompt = f"{who}的另一個交點坐標（若只有一個交點或不相交填「{NONE_MARK}」）"
            parts.append(_part(len(parts) + 1, pts[1]["text"], *_POINT, prompt=second_prompt) if len(pts) == 2
                         else _part(len(parts) + 1, NONE_MARK, *_NONE, prompt=second_prompt))
            if pts:
                step += "將直線代入圓方程式解聯立，得交點 " + "、".join(_point_display(p) for p in pts) + "。"
                shown += "，交點 " + "、".join(_point_display(p) for p in pts)
        steps.append((f"({no}) " if len(lines) > 1 else "") + step)
        display.append((f"({no}) " if len(lines) > 1 else "") + shown)
    return _parts_payload(matrix, question=_with_prompts(question, parts), parts=parts, display_answer="；".join(display),
                          explanation_steps=steps, shape="circle_line_relations")


# --- 2. solve_circle_line_parameter ----------------------------------------------------------

_CONDITION_ZH = {"tangent": "相切", "secant": "交於相異兩點", "disjoint": "不相交", "intersect": "相交"}


def _solve_circle_line_parameter(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    param = givens.get("param", "k")
    asks, values = givens["asks"], answer["values"]
    form = givens.get("line_form", "general")
    c_tex = circle_tex(givens["circle"], param=param, show_r=bool(givens.get("show_r")))
    l_tex = line_tex(givens["line"], form, param)
    first = asks[0]
    parts: list[dict[str, Any]] = []
    steps: list[str] = []
    if first["condition"] == "quarter_arcs":
        names = givens.get("names", ["m", "n"])
        other = line_tex(givens["line"], form, names[1])
        question = (f"已知兩平行線 {_t(line_tex(givens['line'], form, names[0]))} 與 {_t(other)} 將圓 {_t('C:' + c_tex)} 的圓周四等分，"
                    f"其中 ${names[0]}>{names[1]}$，求實數 ${names[0]}, {names[1]}$ 的值。")
        big, small = values[0]["values"]
        parts = [_part(1, big, *_RATIONAL, prompt=f"${names[0]}$ 的值"), _part(2, small, *_RATIONAL, prompt=f"${names[1]}$ 的值")]
        steps = ["每條直線截出的弦所對圓心角為 $90^{\\circ}$，所以圓心到直線的距離等於半徑的 $\\frac{\\sqrt{2}}{2}$ 倍。",
                 f"列式解出兩個值，較大者為 ${names[0]}={_num(big)}$，較小者為 ${names[1]}={_num(small)}$。"]
        display = f"${names[0]}={_num(big)}$，${names[1]}={_num(small)}$"
        return _parts_payload(matrix, question=_with_prompts(question, parts), parts=parts, display_answer=display,
                              explanation_steps=steps, shape="circle_line_parameter")
    groups: list[list[tuple[dict[str, Any], dict[str, Any]]]] = []
    for ask, rec in zip(asks, values):
        if groups and groups[-1][0][0]["condition"] == ask["condition"]:
            groups[-1].append((ask, rec))
        else:
            groups.append([(ask, rec)])

    def sentence(ask: dict[str, Any], recs: list[dict[str, Any]]) -> str:
        if ask["condition"] == "chord":
            cond = f"交於 $A, B$ 兩相異點，且 $\\overline{{AB}}={_num(ask['chord'])}$"
        else:
            cond = _CONDITION_ZH[ask["condition"]]
        wants = []
        for rec in recs:
            if rec["kind"] == "region":
                wants.append(f"實數 ${param}$ 的範圍")
            elif rec["kind"] == "lines":
                wants.append("直線 $L$ 的方程式")
            else:
                wants.append(f"實數 ${param}$ 的值")
        two = any(r["kind"] in ("set", "lines") and len(r.get("values", r.get("lines", []))) == 2 for r in recs)
        hint = "（有兩解）" if two and givens.get("two_solution_hint") else ""
        return f"已知圓 $C$ 與直線 $L$ {cond}，求" + "與".join(wants) + f"。{hint}"

    if len(groups) == 1:
        ask0 = groups[0][0][0]
        recs0 = [rec for _a, rec in groups[0]]
        question = sentence(ask0, recs0).replace("已知圓 $C$ 與直線 $L$", f"已知圓 {_t('C:' + c_tex)} 與直線 {_t('L:' + l_tex)}", 1)
    else:
        question = f"設圓 {_t('C:' + c_tex)} 與直線 {_t('L:' + l_tex)}。\n" + "\n".join(
            f"({i}){sentence(g[0][0], [rec for _a, rec in g])}" for i, g in enumerate(groups, start=1))
    display_bits = []
    for gi, group in enumerate(groups, start=1):
        for ask, rec in group:
            if rec["kind"] == "region":
                prompt = f"${param}$ 的範圍"
            elif rec["kind"] == "lines":
                prompt = "直線 $L$ 的方程式"
            else:
                prompt = f"${param}$ 的值（全部列出）"
            part = _value_part(len(parts) + 1, rec, prompt)
            if len(groups) > 1:
                part["label"] = f"({gi})" if len(group) == 1 else f"({gi}-{group.index((ask, rec)) + 1})"
            parts.append(part)
            display_bits.append(_value_display(rec))
        ask = group[0][0]
        if ask["condition"] == "chord":
            steps.append(f"弦長 ${_num(ask['chord'])}$ 的一半、圓心到直線的距離與半徑構成直角三角形，"
                         f"由 $\\left(\\frac{{{_num(ask['chord'])}}}{{2}}\\right)^{{2}}+d^{{2}}=r^{{2}}$ 列式。")
        elif ask["condition"] == "tangent":
            steps.append("相切時圓心到直線的距離等於半徑（或代入後判別式 $D=0$），列式求解。")
        else:
            rel = {"secant": "<", "disjoint": ">", "intersect": "\\le"}[ask["condition"]]
            steps.append(f"{_CONDITION_ZH[ask['condition']]}時圓心到直線的距離 $d{rel}r$，並保證方程式的圖形為圓（$r^{{2}}>0$），列不等式求解。")
        steps.append("得 " + "；".join(_value_display(rec) for _a, rec in group) + "。")
    return _parts_payload(matrix, question=_with_prompts(question, parts), parts=parts, display_answer="；".join(display_bits),
                          explanation_steps=steps, shape="circle_line_parameter")


# --- 3. write_circle_tangent_lines -------------------------------------------------------------

def _write_circle_tangent_lines(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    c_tex = circle_tex(givens["circle"], show_r=bool(givens.get("show_r")))
    kind = givens["kind"]
    rec = answer["values"][0]
    two = len(rec["lines"]) == 2
    if kind == "through_point":
        wording = givens.get("wording", "named")
        named = wording == "named"
        where = "點" if wording == "neutral" else {"on": "圓上一點", "outside": "圓外一點"}[answer["position"]]
        shown = _point_tex(givens["point"], "P" if named else "")
        question = f"已知圓 {_t(('C:' if named else '') + c_tex)}，求過{where} {_t(shown)} 的切線方程式。"
        if answer["position"] == "on":
            steps = ["切線與過切點的半徑垂直：先求圓心與切點連線的斜率，再取其負倒數作為切線斜率，以點斜式寫出切線。"]
        else:
            steps = ["先檢查過該點的鉛直線是否為切線（圓心到該直線的距離是否等於半徑）。",
                     "再設切線斜率為 $m$，令圓心到切線的距離等於半徑，解出 $m$。"]
    elif kind == "with_slope":
        slope = _num(givens["slope"])
        question = f"設圓 {_t('C:' + c_tex)}，且直線 $L$ 為圓 $C$ 的切線。已知 $L$ 的斜率為 ${slope}$，求 $L$ 的方程式。（有兩解）"
        steps = [f"設 $L:y={slope}x+b$，令圓心到 $L$ 的距離等於半徑，解出兩個 $b$。"]
    else:
        ref = line_tex(givens["parallel_to"], givens.get("line_form", "rhs"))
        question = f"求平行於直線 {_t(ref)} 且與圓 {_t(c_tex)} 相切的直線方程式。"
        a, b, _c = givens["parallel_to"]
        steps = [f"平行線可設為 ${_terms_tex([(a, 'x'), (b, 'y')], 'k')}+c=0$，令圓心到直線的距離等於半徑，解出兩個 $c$。"]
    part = _value_part(1, rec, "切線方程式")
    if two:
        part["answer_format_example"] = "x=2, 4x-3y+10=0"
    steps.append("切線方程式為 " + _value_display(rec) + "。")
    return _single_payload(matrix, question=question, part=part, display_answer=_value_display(rec),
                           explanation_steps=steps, shape="tangent_lines")


# --- 4. solve_chord_and_distance ---------------------------------------------------------------

def _solve_chord_and_distance(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    c_tex = circle_tex(givens["circle"], show_r=bool(givens.get("show_r")))
    asks, values = givens["asks"], answer["values"]
    form = givens.get("line_form", "general")
    parts: list[dict[str, Any]] = []
    steps: list[str] = []
    if asks == ["chord"]:
        question = (f"已知圓 {_t('C:' + c_tex)} 與直線 {_t('L:' + line_tex(givens['line'], form))} 交於 $A, B$ 兩相異點，"
                    "求 $\\overline{AB}$ 的長。")
        parts = [_value_part(1, values[0], "$\\overline{AB}$ 的長")]
        steps = ["先求圓心 $M$ 到直線的距離 $\\overline{MH}$，由畢氏定理 $\\overline{AH}=\\sqrt{r^{2}-\\overline{MH}^{2}}$，"
                 f"再由 $\\overline{{AB}}=2\\overline{{AH}}$ 得 {_value_display(values[0])}。"]
    elif "max_distance" in asks:
        question = (f"已知 {_t('C:' + c_tex)} 與直線 {_t('L:' + line_tex(givens['line'], form))}，"
                    "求圓上各點與直線 $L$ 距離的最大值與最小值。")
        parts = [_value_part(1, values[0], "最大值"), _value_part(2, values[1], "最小值")]
        steps = [f"圓心到 $L$ 的距離為 ${answer['distance_latex']}$，大於半徑 ${answer['radius_latex']}$，所以 $L$ 與圓不相交。",
                 f"最大值為距離加半徑：{_value_display(values[0])}；最小值為距離減半徑：{_value_display(values[1])}。"]
    else:
        p = givens["point"]
        question = (f"已知圓 {_t('C:' + c_tex)}，且過圓 $C$ 內一點 {_t(_point_tex(p, 'P'))} 的所有弦中，最短的弦為 $\\overline{{AB}}$。")
        parts = [_value_part(1, values[0], "$\\overline{AB}$ 的長"), _value_part(2, values[1], "直線 $AB$ 的方程式")]
        steps = [f"最短的弦與 $\\overline{{MP}}$ 垂直，$\\overline{{MP}}^{{2}}={_num(answer['mp2'])}$，"
                 f"所以 $\\overline{{AB}}=2\\sqrt{{r^{{2}}-\\overline{{MP}}^{{2}}}}$，得 {_value_display(values[0])}。",
                 f"直線 $AB$ 過 $P$ 且以 $\\overrightarrow{{MP}}$ 為法向量，得 {_value_display(values[1])}。"]
    display = "；".join(_value_display(v) for v in values)
    return _parts_payload(matrix, question=_with_prompts(question, parts), parts=parts, display_answer=display,
                          explanation_steps=steps, shape="chord_and_distance")


# --- 5. solve_circle_from_tangent_point --------------------------------------------------------

def _solve_circle_from_tangent_point(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    names = givens.get("names", ["m", "n"])
    d = fr(givens["d"])
    d_term = "" if d == 0 else f"{'-' if d < 0 else '+'}{'' if abs(d) == 1 else frac_latex(abs(d))}x"
    circle = f"C:x^{{2}}+y^{{2}}{d_term}+{names[0]}y+{names[1]}=0"
    question = (f"已知過圓 {_t(circle)} 上一點 {_t(_point_tex(givens['point']))} 的切線為 "
                f"{_t(line_tex(givens['tangent']))}，求實數 ${names[0]}, {names[1]}$ 的值。")
    e, f = answer["values"]
    parts = [_value_part(1, e, f"${names[0]}$ 的值"), _value_part(2, f, f"${names[1]}$ 的值")]
    h, k = answer["center"]
    steps = [f"圓心為 $\\left({_num(h)},\\ -\\frac{{{names[0]}}}{{2}}\\right)$，切點與圓心的連線垂直於切線，解得 ${names[0]}={_num(e['canonical'])}$。",
             f"再將切點代入圓方程式，得 ${names[1]}={_num(f['canonical'])}$。"]
    display = f"${names[0]}={_num(e['canonical'])}$，${names[1]}={_num(f['canonical'])}$"
    return _parts_payload(matrix, question=_with_prompts(question, parts), parts=parts, display_answer=display,
                          explanation_steps=steps, shape="circle_from_tangent")


# --- 6. evaluate_circle_line_statement_truth ---------------------------------------------------

def _statement_sentence(s: dict[str, Any]) -> str:
    kind = s["kind"]
    if kind == "line_through_point_on_circle_is_tangent":
        return "過圓上某一點的直線必為此圓的切線。"
    if kind == "disjoint_distance_bound":
        return f"若直線 $L$ 與圓 {_t('C:x^{2}+y^{2}=' + _num(s['r2']))} 不相交，則原點到 $L$ 的距離必大於 ${_num(s['bound'])}$。"
    if kind == "tangent_to_both_axes":
        return f"圓 {_t(circle_tex(s))} 與 $x$ 軸、$y$ 軸都相切。"
    if kind == "tangent_slope_exists":
        return f"給定一圓，則必有斜率為 ${_num(s['slope'])}$ 的直線與此圓相切。"
    if kind == "two_tangents_through_point":
        return f"過 {_t(_point_tex(s['point']))} 且與圓 {_t('C:' + circle_tex(s))} 相切的直線必有兩條。"
    raise ValueError(f"unknown_statement_kind:{kind}")


def _statement_reason(s: dict[str, Any], answer: dict[str, Any]) -> str:
    kind = s["kind"]
    if kind == "line_through_point_on_circle_is_tangent":
        return "過圓上一點的直線中，只有與該點半徑垂直的直線是切線，其餘直線都與圓交於兩點。"
    if kind == "disjoint_distance_bound":
        r = radical_of_fraction(fr(s["r2"])).latex()
        return f"直線與圓不相交時，圓心（原點）到直線的距離大於半徑 ${r}$。"
    if kind == "tangent_to_both_axes":
        h, k, r2 = circle_of(s)
        r = radical_of_fraction(r2).latex()
        return (f"圓心 $\\left({_num(h)},\\ {_num(k)}\\right)$ 到 $x$ 軸的距離為 ${frac_latex(abs(k))}$、到 $y$ 軸的距離為 "
                f"${frac_latex(abs(h))}$，與半徑 ${r}$ 比較。")
    if kind == "tangent_slope_exists":
        return "對任意斜率，與圓心距離等於半徑的兩條該斜率直線都是切線。"
    pos = {"outside": "在圓外，過該點的切線有兩條", "on": "在圓上，過該點的切線只有一條", "inside": "在圓內，過該點沒有切線"}[answer["position"]]
    return f"比較該點到圓心的距離與半徑：該點{pos}。"


def _evaluate_circle_line_statement_truth(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    statement = givens["statement"]
    mark = "○" if answer["truth"] else "×"
    question = "下列敘述對的打「○」，錯的打「×」。\n" + _statement_sentence(statement)
    part = _part(1, "A" if answer["truth"] else "B", "choice_label_checker", "choice_label", "single_choice",
                 choices=[dict(c) for c in TRUE_FALSE_CHOICES])
    return _single_payload(matrix, question=question, part=part, display_answer=mark, shape="single_choice",
                           explanation_steps=[f"{_statement_reason(statement, answer)}此敘述為「{mark}」。"])


# --- 7. solve_circle_tangent_scenarios ---------------------------------------------------------

_BUILDING_INTRO = "圓弧形大廈從正面看過去，其輪廓由圓弧形與一段底座組成。右圖為某一圓弧形大廈的輪廓畫在坐標平面上之設計圖，"


def _solve_circle_tangent_scenarios(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    scenario, values = givens["scenario"], answer["values"]
    if scenario in ("building_view", "building_dimensions"):
        k, p = fr(givens["center_y"]), pt(givens["point"])
        m_tex, p_tex = _point_tex((0, k), "M"), _point_tex(p, "P")
        base = (f"{_BUILDING_INTRO}其中 {_t(m_tex)} 為圓心，弦 $\\overline{{AB}}$ 為圓弧形大廈的底座。"
                f"已知從 $x$ 軸正向上一點 $Q$ 仰望圓弧形大廈所能看到的最高點為 {_t(p_tex)}，試回答下列問題：")
        if scenario == "building_view":
            parts = [_value_part(1, values[0], "直線 $PQ$ 的斜率"), _value_part(2, values[1], "直線 $PQ$ 的方程式"),
                     _value_part(3, values[2], "$Q$ 點的坐標")]
            steps = ["$P$ 是從 $Q$ 仰望所能看到的最高點，所以直線 $PQ$ 是圓弧在 $P$ 的切線，與 $\\overline{MP}$ 垂直。",
                     f"$\\overline{{MP}}$ 的斜率的負倒數即為 $PQ$ 的斜率 {_value_display(values[0])}；由點斜式得 {_value_display(values[1])}。",
                     f"令 $y=0$ 得 $Q$ 點坐標 {_value_display(values[2])}。"]
        else:
            parts = [_value_part(1, values[0], "圓弧形大廈的半徑"), _value_part(2, values[1], "圓弧形大廈所在的圓方程式"),
                     _value_part(3, values[2], "底座 $\\overline{AB}$ 的長度")]
            steps = [f"半徑為 $\\overline{{MP}}$ 的長，得 {_value_display(values[0])}；圓方程式為 {_value_display(values[1])}。",
                     f"令 $y=0$ 求出 $A$、$B$ 的 $x$ 坐標，得 $\\overline{{AB}}$ 的長為 {_value_display(values[2])}。"]
        figure = _building_figure(givens["center_y"], givens["point"], answer)
        question = _with_prompts(base, parts)
    elif scenario == "light_shadow":
        light = pt(givens["light"])
        question = (f"在坐標平面上 {_t(_point_tex(light, 'A'))} 處有一光源，將圓 {_t(circle_tex(givens['circle']))} 投射到 $x$ 軸上，"
                    "如右圖所示，求其在 $x$ 軸上的影子 $\\overline{PQ}$ 長。")
        parts = [_value_part(1, values[0], "$\\overline{PQ}$ 的長")]
        xp, xq = answer["feet"]
        steps = ["影子的兩端是過光源 $A$ 的兩條切線與 $x$ 軸的交點。",
                 "設切線斜率為 $m$，令圓心到切線的距離等於半徑，解出兩個斜率，再分別令 $y=0$。",
                 f"得 $P\\left({_num(xp)},\\ 0\\right)$、$Q\\left({_num(xq)},\\ 0\\right)$，所以 $\\overline{{PQ}}={_num(values[0]['canonical'])}$。"]
        figure = _light_figure(givens, answer)
    else:
        w, cy, od = (_num(givens[k]) for k in ("width", "center_height", "od"))
        r = radical_of_fraction(fr(givens["r2"])).latex()
        question = (f"小明利用半徑 ${r}$ 的圓形圖案來設計右圖的長方形徽章 $OABC$，徽章左右寬度為 ${w}$，"
                    f"圓形圖案的圓心與長方形左右兩側（$\\overline{{OC}}$ 和 $\\overline{{AB}}$）等距離且與 $\\overline{{OA}}$ 的距離為 ${cy}$。"
                    f"已知 $\\overline{{OD}}={od}$，$\\overline{{CD}}$ 與 $\\overline{{DE}}$ 都和圓相切，求 $\\overline{{AE}}$ 與 $\\overline{{OC}}$ 的長度。")
        parts = [_value_part(1, values[0], "$\\overline{AE}$ 的長度"), _value_part(2, values[1], "$\\overline{OC}$ 的長度")]
        s1, s2 = answer["slopes"]
        steps = [f"以 $O$ 為原點、$\\overline{{OA}}$ 為 $x$ 軸，圓心為 $\\left(\\frac{{{w}}}{{2}},\\ {cy}\\right)$，$D\\left({od},\\ 0\\right)$。",
                 f"設過 $D$ 的切線斜率為 $m$，令圓心到切線的距離等於半徑，得 $m={_num(s1)}$ 或 ${_num(s2)}$。",
                 f"斜率 ${_num(s2)}$ 的切線交 $\\overline{{AB}}$ 於 $E$，得 $\\overline{{AE}}={_num(values[0]['canonical'])}$；"
                 f"斜率 ${_num(s1)}$ 的切線交 $y$ 軸於 $C$，得 $\\overline{{OC}}={_num(values[1]['canonical'])}$。"]
        figure = _badge_figure(givens, answer)
        question = _with_prompts(question, parts)
    display = "；".join(_value_display(v) for v in values)
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps,
                          shape="tangent_scenario", visual_spec=figure)


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "classify_circle_line_relations": _classify_circle_line_relations,
    "solve_circle_line_parameter": _solve_circle_line_parameter,
    "write_circle_tangent_lines": _write_circle_tangent_lines,
    "solve_chord_and_distance": _solve_chord_and_distance,
    "solve_circle_from_tangent_point": _solve_circle_from_tangent_point,
    "evaluate_circle_line_statement_truth": _evaluate_circle_line_statement_truth,
    "solve_circle_tangent_scenarios": _solve_circle_tangent_scenarios,
}


def adapt_circle_line_relations_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_circle_line_relations_operation:{operation}")
    return builder(matrix)
