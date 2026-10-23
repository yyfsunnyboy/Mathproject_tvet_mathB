"""Question payload contracts for analytic_geometry.circle_equations.

Every payload is graded by a shared checker registered in ``CHECKER_CAPABILITIES``; the expected
answers always come from the domain matrix, never from this adapter.  Figures are plain
``visual_spec`` data for the shared coordinate-plane renderer (``circles`` primitive included).
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable

from core.domain.promoted.analytic_geometry_lines import figures as FG

from .circle_equations_domain import DOMAIN_KEY
from .circle_geometry import (
    G, circle_from_general, fr, frac_latex, frac_text, general_latex, pt, radical_of_fraction, std_latex,
)

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
QUADRANT_ZH = {1: "一", 2: "二", 3: "三", 4: "四"}

_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_RADICAL = ("expression_equivalence_checker", "radical_equivalence", "numeric_or_radical")
_POINT = ("coordinate_pair_checker", "coordinate_pair_equivalence", "coordinate_pair")
_EQUATION = ("equation_checker", "equation_equivalent", "equation")
_LINE = ("linear_equation_equivalent_checker", "linear_equation_equivalent", "equation")
_RELATION = ("inequality_solution_checker", "inequality_solution_equivalence", "inequality")
_PI = ("expression_equivalence_checker", "algebraic_equivalent", "numeric_or_radical")

GRAPH_CHOICES = (("circle", "一個圓"), ("point", "一個點"), ("none", "圖形不存在"))
RELATION_CHOICES = (("inside", "在圓的內部"), ("outside", "在圓的外部"), ("on", "在圓上"))
SHAPE_CHOICES = (("circle", "整個圓"), ("upper_semicircle", "上半圓（不含兩端點）"),
                 ("lower_semicircle", "下半圓（不含兩端點）"), ("line", "一條直線"))
CHOICE_SETS = {"graph": GRAPH_CHOICES, "relation": RELATION_CHOICES, "shape": SHAPE_CHOICES}


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
        "math_core": {
            "givens": matrix["givens"],
            "target": matrix["answer"],
            "validation_facts": matrix["validation_facts"],
        },
    }
    if visual_spec:
        payload["visual_spec"] = visual_spec
        payload["visual_backed"] = bool(visual_spec.get("render_required"))
    if extra:
        payload.update(extra)
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
    skip = ("key", "label", "checker", "checker_key", "equivalence_type", "answer_type", "expected_answer")
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


def _choice_part(index: int, key: str, options: tuple[tuple[str, str], ...], label: str | None = None) -> dict[str, Any]:
    """Select part: the expected answer is the 1-based position label of ``key`` in ``options``."""
    choices = [{"label": str(i), "value": text, "text": text} for i, (_k, text) in enumerate(options, start=1)]
    position = [k for k, _t in options].index(key) + 1
    part = _part(index, str(position), "choice_label_checker", "choice_label", "single_choice", choices=choices)
    if label:
        part["label"] = label
    return part


def _t(text: str) -> str:
    return f"${text}$"


def _ptex(p: Any, name: str = "") -> str:
    return G.point_latex(pt(p), name)


def _rad(r2: Any) -> str:
    return radical_of_fraction(fr(r2)).latex()


def _circle_tex(spec: dict[str, Any]) -> str:
    if "d" in spec:
        return general_latex(spec["d"], spec["e"], spec["f"], spec.get("a", 1))
    return std_latex(spec["center"][0], spec["center"][1], spec["r2"])


def _numbered(texts: list[str]) -> str:
    return "\n".join(f"({i}) {text}" for i, text in enumerate(texts, start=1))


def _param_terms(d: Any, e0: Any, e1: Any, f0: Any, f1: Any) -> str:
    """``x^2+y^2+dx+(e1 k+e0)y+(f1 k+f0)`` for an equation family with parameter ``k``."""
    d, e0, e1, f0, f1 = (fr(v) for v in (d, e0, e1, f0, f1))

    def linear(c0: Fraction, c1: Fraction) -> str:
        if c1 == 0:
            return frac_latex(c0)
        k_term = ("" if abs(c1) == 1 else frac_latex(abs(c1))) + "k"
        if c0 == 0:
            return ("-" if c1 < 0 else "") + k_term
        return f"{frac_latex(c0)}{'-' if c1 < 0 else '+'}{k_term}"

    out = "x^{2}+y^{2}"
    if d:
        out += f"{'-' if d < 0 else '+'}{'' if abs(d) == 1 else frac_latex(abs(d))}x"
    if e1 == 0:
        if e0:
            out += f"{'-' if e0 < 0 else '+'}{'' if abs(e0) == 1 else frac_latex(abs(e0))}y"
    else:
        coef = linear(e0, e1)
        out += f"+\\left({coef}\\right)y" if e0 else (f"{'-' if e1 < 0 else '+'}{'' if abs(e1) == 1 else frac_latex(abs(e1))}ky")
    if f1 == 0:
        if f0:
            out += f"{'-' if f0 < 0 else '+'}{frac_latex(abs(f0))}"
    elif f0:
        out += f"+\\left({linear(f0, f1)}\\right)"
    else:
        out += f"{'-' if f1 < 0 else '+'}{'' if abs(f1) == 1 else frac_latex(abs(f1))}k"
    return out + "=0"


def _record_display(record: dict[str, Any]) -> str:
    kind = record["kind"]
    if kind in ("equation", "relation"):
        return _t(record["latex"])
    if kind == "line":
        return _t(record["text"])
    if kind == "point":
        x, y = record["point"]
        return _t(f"\\left({frac_latex(fr(x))},\\ {frac_latex(fr(y))}\\right)")
    if kind in ("radical", "rational"):
        return _t(record["latex"] if kind == "radical" else frac_latex(fr(record["canonical"])))
    if kind == "pi_multiple":
        return _t(record["latex"])
    if kind == "set":
        return _t(",\\ ".join(frac_latex(fr(v)) for v in record["values"]))
    raise ValueError(f"unknown_record_kind:{kind}")


def _record_part(index: int, record: dict[str, Any], label: str | None = None, choice_set: str | None = None) -> dict[str, Any]:
    kind = record["kind"]
    if kind == "equation":
        part = _part(index, record["text"], *_EQUATION, answer_format_example="(x-1)^2+(y+2)^2=9")
    elif kind == "line":
        part = _part(index, record["text"], *_LINE)
    elif kind == "point":
        part = _part(index, record["text"], *_POINT)
    elif kind == "radical":
        part = _part(index, record["canonical"], *_RADICAL, answer_format_example="2√5")
    elif kind == "pi_multiple":
        part = _part(index, record["canonical"], *_PI, required_form="pi_form", answer_format_example="12π")
    elif kind == "relation":
        part = _part(index, record["text"], *_RELATION, answer_format_example="k<5")
    elif kind == "set":
        part = _part(index, list(record["values"]), "solution_set_checker", "unordered_solution_set", "solution_set",
                     solution_members="exact_rational", answer_format_example="4, -2")
    elif kind == "choice":
        return _choice_part(index, record["value"], CHOICE_SETS[choice_set], label)
    else:
        part = _part(index, record["canonical"], *_RATIONAL)
    if label:
        part["label"] = label
    return part


def _answer_text(record: dict[str, Any], choice_set: str | None = None) -> str:
    if record["kind"] == "choice":
        return dict(CHOICE_SETS[choice_set])[record["value"]]
    return _record_display(record)


# --- 1. write_circle_equations ----------------------------------------------------------------------

def _name_of(item: dict[str, Any], key: str, default: str = "") -> str:
    return (item.get("names") or {}).get(key, default)


def _item_prompt(item: dict[str, Any], clause: bool) -> str:
    kind = item["kind"]
    if kind == "center_radius":
        body = f"以點 {_t(_ptex(item['center']))} 為圓心，半徑為 {_t(_rad(item['r2']))} 的圓"
        return f"{body}。" if clause else f"求{body}方程式。"
    if kind == "center_point":
        body = (f"以點 {_t(_ptex(item['center'], _name_of(item, 'center')))} 為圓心，又通過點 "
                f"{_t(_ptex(item['point'], _name_of(item, 'point')))} 的圓")
        return f"{body}。" if clause else f"求{body}方程式。"
    if kind == "diameter":
        a, b = _name_of(item, "a", "A"), _name_of(item, "b", "B")
        if clause:
            return f"以 {_t(_ptex(item['a'], a))}、{_t(_ptex(item['b'], b))} 為直徑兩端點的圓。"
        return f"已知 {_t(_ptex(item['a'], a))}、{_t(_ptex(item['b'], b))}，求以 {_t('\\overline{' + a + b + '}')} 為直徑的圓方程式。"
    if kind == "concentric_through":
        body = f"與圓 {_t(_circle_tex(item['ref']))} 同圓心，且通過點 {_t(_ptex(item['point']))} 的圓"
        return f"{body}。" if clause else f"求{body}方程式。"
    if kind == "axis_center_through_points":
        body = f"通過兩點 {_t(_ptex(item['points'][0]))}、{_t(_ptex(item['points'][1]))} 且圓心在 $x$ 軸上的圓"
        return f"{body}。" if clause else f"求{body}方程式。"
    if kind == "axis_center_through_point_radius":
        return (f"已知圓 $C$ 為過點 {_t(_ptex(item['point']))} 且半徑為 {_t(frac_latex(fr(item['r'])))} 的莫爾圓"
                f"（圓心位於 $x$ 軸上的圓），求圓 $C$ 的方程式（有兩解）。")
    if kind == "circumcircle":
        names = "".join(item.get("names", {}).get(k, d) for k, d in (("a", "A"), ("b", "B"), ("c", "C")))
        return f"求 $\\triangle {names}$ 的外接圓方程式。"
    if kind == "perp_bisector":
        p, q = _name_of(item, "p", "P"), _name_of(item, "q", "Q")
        return f"求 {_t('\\overline{' + p + q + '}')} 的中垂線方程式。"
    if kind == "origin_circle_k":
        name = _name_of(item, "point", "A")
        if "x_sqrt" in item:
            shown = f"{name}\\left(\\sqrt{{{item['x_sqrt']}}},\\ {frac_latex(fr(item['point'][1]))}\\right)"
        else:
            shown = _ptex(item["point"], name)
        return f"已知圓 $C:x^{{2}}+y^{{2}}=k$ 通過 {_t(shown)}，求 $k$ 的值。"
    if kind == "diameter_param_k":
        c, a = item["center"], item["a"]
        h, k0 = fr(c[0]), fr(c[1])
        eq = (f"\\left(x{'-' if h > 0 else '+'}{frac_latex(abs(h))}\\right)^{{2}}" if h else "x^{2}") + "+" + (
            f"\\left(y{'-' if k0 > 0 else '+'}{frac_latex(abs(k0))}\\right)^{{2}}" if k0 else "y^{2}") + "=k"
        return (f"已知 $\\overline{{AB}}$ 為圓 {_t(eq)} 的直徑，其中點 {_t(_ptex(a, 'A'))}，求 $k$ 的值及 $B$ 點的坐標。")
    raise ValueError(f"circle_prompt_required:{kind}")


_VALUE_LABELS = {"axis_center_through_point_radius": ("圓心 x 坐標較小的圓", "圓心 x 坐標較大的圓"),
                 "diameter_param_k": ("k 的值", "B 點坐標"), "origin_circle_k": ("k 的值",)}


def _item_steps(item: dict[str, Any], recs: list[dict[str, Any]]) -> list[str]:
    kind = item["kind"]
    shown = [_record_display(r) for r in recs]
    if kind == "center_radius":
        return [f"圓心與半徑已知，由標準式得 {shown[0]}。"]
    if kind == "center_point":
        return [f"半徑為圓心到該點的距離，得 $r^{{2}}={recs[0]['r2']}$，圓方程式為 {shown[0]}。"]
    if kind == "diameter":
        return [f"圓心為直徑兩端點的中點，半徑為直徑長的一半，得 {shown[0]}。"]
    if kind == "concentric_through":
        return [f"同圓心，所以圓心與已知圓相同；半徑為圓心到所給點的距離，得 {shown[0]}。"]
    if kind == "axis_center_through_points":
        return [f"圓心 $(h,0)$ 到兩點等距，解出 $h$，得 {shown[0]}。"]
    if kind == "axis_center_through_point_radius":
        return ["圓心 $(h,0)$ 到所給點的距離等於半徑，解出兩個 $h$，得 " + "、".join(shown) + "。"]
    if kind == "circumcircle":
        return [f"外接圓的圓心是兩條中垂線的交點，半徑是圓心到頂點的距離，得 {shown[0]}。"]
    if kind == "perp_bisector":
        return [f"中垂線通過線段中點且與線段垂直，得 {shown[0]}。"]
    if kind == "origin_circle_k":
        return [f"圓通過該點，代入得 $k=x^{{2}}+y^{{2}}$，即 {shown[0]}。"]
    return [f"直徑的中點為圓心，所以 $r^{{2}}=k$ 為圓心到 $A$ 的距離平方，得 $k$ 為 {shown[0]}；$B$ 與 $A$ 對圓心對稱，得 $B$ 為 {shown[1]}。"]


def _stem_of(givens: dict[str, Any]) -> str:
    return str(givens.get("stem", ""))


def _write_circle_equations(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    items, values = givens["items"], answer["values"]
    stem = _stem_of(givens)
    counts = {"axis_center_through_point_radius": 2, "diameter_param_k": 2}
    prompts, parts, steps, display_bits = [], [], [], []
    index = 0
    for item_no, item in enumerate(items, start=1):
        n = counts.get(item["kind"], 1)
        recs = values[index:index + n]
        index += n
        prompts.append(_item_prompt(item, clause=bool(stem)))
        labels = _VALUE_LABELS.get(item["kind"])
        multi = len(items) > 1
        for j, rec in enumerate(recs):
            label = None
            if labels:
                label = f"({item_no}) {labels[j]}" if multi else labels[j]
            elif multi:
                label = f"({item_no})"
            parts.append(_record_part(len(parts) + 1, rec, label=label))
        steps.extend((f"({item_no}) " if multi else "") + s for s in _item_steps(item, recs))
        display_bits.append("、".join(_record_display(r) for r in recs))
    if len(items) == 1:
        question = f"{stem}\n{prompts[0]}".strip() if stem else prompts[0]
        display = display_bits[0]
    else:
        question = (f"{stem}\n" if stem else "") + _numbered(prompts)
        display = "　".join(f"({i}) {bit}" for i, bit in enumerate(display_bits, start=1))
    spec = _figure(givens)
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps,
                          shape="circle_equations", visual_spec=spec)


def _figure(givens: dict[str, Any]) -> dict[str, Any] | None:
    figure = givens.get("figure")
    if not figure:
        return None
    pts = figure["points"]
    points = [FG.point_entry(p["p"], p.get("label", p.get("name", ""))) for p in pts]
    lines = [FG.through_line(figure["points"][i]["p"], figure["points"][j]["p"], extend=False) for i, j in figure.get("segments", [])]
    circles = [{"h": float(fr(c["center"][0])), "k": float(fr(c["center"][1])), "r": float(fr(c["r"])), "label": c.get("label", ""),
                "show_center": c.get("show_center", True)} for c in figure.get("circles", [])]
    view = FG.fit_view([p["p"] for p in pts] + [[c["center"][0], c["center"][1]] for c in figure.get("circles", [])]
                       + [list(e) for e in figure.get("extent", [])],
                       pad=figure.get("pad", 2), include_origin=figure.get("include_origin", True))
    extra = {"circles": circles} if circles else {}
    if figure.get("hide_unlabeled"):
        extra["hide_unlabeled_points"] = True
    return FG.plane(points=points, lines=lines, view=view, extra=extra or None)


# --- 2. analyze_general_circle -----------------------------------------------------------------------------

def _analyze_prompt(item: dict[str, Any], clause: bool) -> str:
    kind = item["kind"]
    if kind == "center_radius":
        if item.get("form") == "root":
            eq = f"\\sqrt{{{_shift('x', item['h'])}+{_shift('y', item['k'])}}}={frac_latex(fr(item['rhs']))}"
        else:
            eq = general_latex(item["d"], item["e"], item["f"], item.get("a", 1))
        return f"{_t(eq)}。" if clause else f"已知圓 {_t('C:' + eq)}，求圓 $C$ 的圓心與半徑。"
    if kind == "standard_and_classify":
        return f"{_t(general_latex(item['d'], item['e'], item['f'], item.get('a', 1)))}。"
    if kind == "classify":
        return f"{_t(general_latex(item['d'], item['e'], item['f'], item.get('a', 1)))}。"
    if kind == "param_range":
        eq = _param_terms(item["d"], item["e"], 0, item.get("f0", 0), item["f1"])
        return f"已知 {_t(eq)} 的圖形為一圓，求 $k$ 的範圍。"
    if kind == "param_from_radius":
        eq = _param_terms(item["d"], item["e"], 0, item.get("f0", 0), item["f1"])
        return f"已知圓 {_t('C:' + eq)} 的半徑為 {_t(_rad(item['r2']))}，求 $k$ 的值。"
    if kind == "param_radius_center":
        eq = _param_terms(item["d"], item.get("e0", 0), item["e1"], item.get("f0", 0), item["f1"])
        return f"已知 {_t(eq)} 的圖形為半徑是 {_t(_rad(item['r2']))} 的圓，求 $k$ 的值及圓心坐標。"
    if kind == "coefficients_from_center":
        f = fr(item["f"])
        const = f"{'-' if f < 0 else '+'}{frac_latex(abs(f))}" if f else ""
        return (f"已知圓 $C:x^{{2}}+y^{{2}}+ax+by{const}=0$ 的圓心為 {_t(_ptex([item['h'], item['k']]))}，"
                f"求 $a,\\ b$ 的值及圓 $C$ 的半徑。")
    raise ValueError(f"analyze_prompt_required:{kind}")


def _shift(var: str, centre: Any) -> str:
    centre = fr(centre)
    if centre == 0:
        return f"{var}^{{2}}"
    return f"\\left({var}{'-' if centre > 0 else '+'}{frac_latex(abs(centre))}\\right)^{{2}}"


_B_LABELS = {
    "center_radius": (("圓心", None), ("半徑", None)),
    "standard_and_classify": (("化成標準式", None), ("圖形", "graph")),
    "classify": (("圖形", "graph"),),
    "param_range": (("k 的範圍", None),),
    "param_from_radius": (("k 的值", None),),
    "param_radius_center": (("k 的值（兩解）", None), ("k 較大時的圓心", None), ("k 較小時的圓心", None)),
    "coefficients_from_center": (("a 的值", None), ("b 的值", None), ("圓 C 的半徑", None)),
}


def _analyze_steps(item: dict[str, Any], recs: list[dict[str, Any]]) -> str:
    kind = item["kind"]
    shown = [_answer_text(r, "graph") for r in recs]
    if kind == "center_radius":
        return f"配方化成標準式，得圓心 {shown[0]}，半徑 {shown[1]}。"
    if kind in ("standard_and_classify", "classify"):
        graph = recs[-1]["value"]
        verdict = {"circle": "圖形為一個圓", "point": "圖形為一個點", "none": "圖形不存在"}[graph]
        rhs = {"circle": "正數", "point": "零", "none": "負數"}[graph]
        head = f"對 $x,y$ 分別配方，得 {shown[0]}；" if kind == "standard_and_classify" else "對 $x,y$ 分別配方；"
        return f"{head}右邊為{rhs}，所以{verdict}。"
    if kind == "param_range":
        return f"配方後右邊須為正數，解得 {shown[0]}。"
    if kind == "param_from_radius":
        return f"配方後右邊等於半徑的平方，解得 $k$ 為 {shown[0]}。"
    if kind == "param_radius_center":
        return f"配方後右邊等於半徑的平方，解得 $k$ 為 {shown[0]}；圓心為配方後 $x$、$y$ 括號內數值的相反數，依序為 {shown[1]}、{shown[2]}。"
    return f"圓心的坐標為一次項係數一半的相反數，得 $a$、$b$ 為 {shown[0]}、{shown[1]}；再配方求得半徑 {shown[2]}。"


def _analyze_general_circle(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    items, values = givens["items"], answer["values"]
    stem = _stem_of(givens)
    prompts, parts, steps, display_bits = [], [], [], []
    index = 0
    multi = len(items) > 1
    for item_no, item in enumerate(items, start=1):
        spec = _B_LABELS[item["kind"]]
        recs = values[index:index + len(spec)]
        index += len(spec)
        prompts.append(_analyze_prompt(item, clause=bool(stem)))
        for (name, choice_set), rec in zip(spec, recs):
            label = f"({item_no}) {name}" if multi else name
            parts.append(_record_part(len(parts) + 1, rec, label=label, choice_set=choice_set))
        steps.append((f"({item_no}) " if multi else "") + _analyze_steps(item, recs))
        display_bits.append("，".join(_answer_text(r, c) for (_n, c), r in zip(spec, recs)))
    if multi or stem:
        question = (f"{stem}\n" if stem else "") + (_numbered(prompts) if multi else prompts[0])
    else:
        question = prompts[0]
    display = "　".join(f"({i}) {bit}" for i, bit in enumerate(display_bits, start=1)) if multi else display_bits[0]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps,
                          shape="general_circle_analysis")


# --- 3. solve_distance_ratio_locus -------------------------------------------------------------------------------

def _ratio_tex(p: int, q: int) -> str:
    return frac_latex(Fraction(p, q))


def _solve_distance_ratio_locus(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    asks, values = answer["asks"], answer["values"]
    p, q = answer["ratio"]
    a, b = givens["a"], givens["b"]
    labels = {"ratio_p": "PA : PB 的前項", "ratio_q": "PA : PB 的後項", "equation": "圖形的方程式", "shape": "P 點所形成的圖形",
              "center": "圓心坐標", "radius": "半徑"}
    parts = []
    for i, (ask, rec) in enumerate(zip(asks, values), start=1):
        parts.append(_record_part(i, rec, label=labels[ask] if len(asks) > 1 else None, choice_set="shape"))
    if givens.get("scenario") == "garbage":
        wa, wb = (frac_latex(fr(w)) for w in givens["weights"])
        dist = frac_latex(fr(b[0]) - fr(a[0]))
        question = (
            f"如圖，$A,\\ B$ 兩處是垃圾集中場，$B$ 在 $A$ 的正東方 ${dist}$ 公里處。政府預計在直線 $AB$ 的北面 $P$ 處蓋一座焚化廠，"
            f"並規劃「$P$ 與 $A,\\ B$ 的距離」與「去年 $A,\\ B$ 的垃圾總重量」成反比。\n"
            f"(1) 已知去年 $A$ 與 $B$ 的垃圾總重量分別為 ${wa}$ 萬公噸與 ${wb}$ 萬公噸，求 $\\overline{{PA}}:\\overline{{PB}}$（以最簡整數比表示）。\n"
            f"(2) 承 (1)，所有 $P$ 點會形成什麼圖形？以 $A$ 為原點、直線 $AB$ 為 $x$ 軸、$B$ 在正 $x$ 軸方向建立坐標系，"
            f"並回答該圓的圓心坐標與半徑（單位：公里）。"
        )
        shape_text = _answer_text(values[asks.index("shape")], "shape")
        centre_text = _answer_text(values[asks.index("center")])
        radius_text = _answer_text(values[asks.index("radius")])
        steps = [f"(1) 距離與重量成反比，$\\overline{{PA}}:\\overline{{PB}}=\\frac{{1}}{{{wa}}}:\\frac{{1}}{{{wb}}}={p}:{q}$。",
                 f"(2) 設 $P(x,y)$，$y>0$，由 ${q}\\overline{{PA}}={p}\\overline{{PB}}$ 兩邊平方整理並配方，P 點的圖形為{shape_text}，"
                 f"圓心 {centre_text}，半徑 {radius_text}。"]
        display = f"(1) {p}:{q}　(2) {shape_text}，圓心 {centre_text}，半徑 {radius_text}"
        spec = _figure(givens)
        return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps,
                              shape="distance_ratio_locus", visual_spec=spec)
    name_a, name_b = givens.get("names", ["A", "B"])
    question = (f"已知 {_t(_ptex(a, name_a))}、{_t(_ptex(b, name_b))} 及 $P\\left(x,\\ y\\right)$ 三點滿足 "
                f"{_t('\\overline{PA}=' + _ratio_tex(p, q) + '\\overline{PB}')}，求所有 $P$ 點所成圖形的方程式。")
    eq = _record_display(values[asks.index("equation")])
    steps = [f"利用兩點的距離公式，列出 ${q}\\overline{{PA}}={p}\\overline{{PB}}$ 的坐標關係，兩邊平方整理並配方，得 {eq}。"]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=eq, explanation_steps=steps,
                          shape="distance_ratio_locus")


# --- 4. classify_points_against_circle -----------------------------------------------------------------------------

def _classify_points_against_circle(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    names = givens.get("names") or ["P", "Q", "R", "S"][:len(givens["points"])]
    head = "、".join(_t(_ptex(p, n)) for p, n in zip(givens["points"], names))
    count = {2: "兩", 3: "三", 4: "四"}.get(len(names), str(len(names)))
    question = (f"已知圓 $C$ 的方程式為 {_t(_circle_tex(givens['circle']))}，分別判斷 {head} {count}點與圓的關係"
                f"（即點是在內部、外部還是圓上）。")
    parts = [_choice_part(i, rec["value"], RELATION_CHOICES, label=f"{n} 點") for i, (n, rec) in enumerate(zip(names, answer["values"]), start=1)]
    steps = [f"計算 ${n}$ 點與圓心的距離並與半徑比較，{n} 點" + dict(RELATION_CHOICES)[rec["value"]] + "。" for n, rec in zip(names, answer["values"])]
    display = "；".join(f"{n}：{dict(RELATION_CHOICES)[rec['value']]}" for n, rec in zip(names, answer["values"]))
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps,
                          shape="point_circle_relations")


# --- 5. solve_circle_point_distances ------------------------------------------------------------------------------------

def _solve_circle_point_distances(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    asks, values = answer["asks"], answer["values"]
    circle, point = givens["circle"], givens["point"]
    name = givens.get("point_name", "P")
    if asks == ["relation", "min"]:
        question = (f"設圓 {_t('C:' + _circle_tex(circle))}。\n"
                    f"(1) 點 {_t(_ptex(point, name))} 在圓 $C$ 的內部、外部、還是圓上？\n"
                    f"(2) 已知 $P$ 為圓 $C$ 上一點，求 {_t('\\overline{' + name + 'P}')} 的最小值。")
        labels = ["(1) 點的位置", f"(2) 最小值"]
    else:
        if name == "原點":
            question = (f"已知圓 {_t('C:' + _circle_tex(circle))}。求原點與圓 $C$ 上各點距離的最大值與最小值。")
        else:
            question = (f"已知圓 {_t('C:' + _circle_tex(circle))} 及點 {_t(_ptex(point, name))}，"
                        f"求 ${name}$ 點與圓 $C$ 上各點距離的最大值與最小值。")
        labels = ["最大值", "最小值"]
    parts = [_record_part(i, rec, label=label, choice_set="relation") for i, (rec, label) in enumerate(zip(values, labels), start=1)]
    d, r = answer["centre_distance"], answer["radius"]
    steps = [f"圓心到該點的距離為 ${d}$，半徑為 ${r}$。"]
    for ask, rec in zip(asks, values):
        if ask == "relation":
            steps.append(f"距離 ${d}$ 與半徑 ${r}$ 比較，該點{_answer_text(rec, 'relation')}。")
        elif ask == "max":
            steps.append(f"最大距離為圓心距離加半徑，得 {_record_display(rec)}。")
        else:
            steps.append(f"最小距離為圓心距離與半徑的差的絕對值，得 {_record_display(rec)}。")
    display = "，".join(_answer_text(r_, "relation") for r_ in values)
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps,
                          shape="point_circle_distances")


# --- 6. solve_point_position_parameter_range ----------------------------------------------------------------------------------

def _solve_point_position_parameter_range(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    inside, outside = givens["inside"], givens["outside"]
    names = givens.get("names", {"inside": ["P"], "outside": ["Q"]})
    bits = [f"{_t(_ptex(p, n))} 在圓 $C$ 內部" for p, n in zip(inside, names["inside"])]
    bits += [f"{_t(_ptex(q, n))} 在圓 $C$ 外部" for q, n in zip(outside, names["outside"])]
    question = f"設圓 $C$ 的方程式為 $x^{{2}}+y^{{2}}=k$。已知 " + "，".join(bits) + "，求 $k$ 的範圍。"
    rec = answer["values"][0]
    steps = ["圓心為原點，點在圓內部等於距離平方小於 $k$，在外部等於距離平方大於 $k$，聯立得 " + _record_display(rec) + "。"]
    return _single_payload(matrix, question=question, part=_record_part(1, rec), display_answer=_record_display(rec),
                           explanation_steps=steps, shape="parameter_range")


# --- 7. evaluate_circle_statement_truth -------------------------------------------------------------------------------------------

def _statement_sentence(s: dict[str, Any]) -> str:
    kind = s["kind"]
    if kind == "center_quadrant":
        return f"圓 {_t(std_latex(s['center'][0], s['center'][1], s['r2']))} 的圓心在第{QUADRANT_ZH[int(s['claimed'])]}象限。"
    if kind == "is_circle":
        return f"方程式 {_t(general_latex(s['d'], s['e'], s['f'], s.get('a', 1)))} 的圖形為一圓。"
    if kind == "may_be_point":
        return f"方程式 {_t(_param_terms(s['d'], s['e'], 0, s.get('f0', 0), s['f1']))} 的圖形有可能是一個點。"
    if kind == "origin_inside":
        return f"原點在 {_t(std_latex(s['center'][0], s['center'][1], s['r2']))} 的內部。"
    if kind == "area_equals":
        claimed = frac_latex(fr(s["claimed_coef"])) + ("\\pi" if s["with_pi"] else "")
        return f"方程式 {_t('x^{2}+y^{2}=' + frac_latex(fr(s['r2'])))} 的圖形所圍成之面積為 {_t(claimed)}。"
    raise ValueError(f"unknown_statement_kind:{kind}")


def _statement_reason(s: dict[str, Any], answer: dict[str, Any]) -> str:
    kind = s["kind"]
    if kind == "center_quadrant":
        h, k = fr(s["center"][0]), fr(s["center"][1])
        return f"圓心為 $\\left({frac_latex(h)},\\ {frac_latex(k)}\\right)$，在第{QUADRANT_ZH[(1 if h > 0 and k > 0 else 2 if h < 0 < k else 3 if h < 0 and k < 0 else 4)]}象限。"
    if kind == "is_circle":
        return "配方後右邊的值為正才是圓；為零是一點，為負則沒有圖形。"
    if kind == "may_be_point":
        return "配方後選取適當的 $k$ 使右邊等於 $0$，圖形就是一個點。"
    if kind == "origin_inside":
        return "比較原點到圓心的距離與半徑：距離小於半徑才在內部。"
    return "半徑為 $r$ 的圓所圍成的面積為 $\\pi r^{2}$。"


def _evaluate_circle_statement_truth(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    statement = givens["statement"]
    mark = "○" if answer["truth"] else "×"
    question = "下列敘述對的打「○」，錯的打「×」。\n" + _statement_sentence(statement)
    part = _part(1, "A" if answer["truth"] else "B", "choice_label_checker", "choice_label", "single_choice",
                 choices=[dict(c) for c in TRUE_FALSE_CHOICES])
    return _single_payload(matrix, question=question, part=part, display_answer=mark, shape="single_choice",
                           explanation_steps=[f"{_statement_reason(statement, answer)}此敘述為「{mark}」。"])


# --- 8. solve_mohr_circles ----------------------------------------------------------------------------------------------------------

_MARKS = "①②③④⑤⑥"


def _solve_mohr_circles(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    options = givens["options"]
    choice, equation, area = answer["values"]
    option_tex = [o.get("latex") or _circle_tex(o) for o in options]
    option_txt = [o.get("text") or o["latex"] for o in options]
    lines = "　".join(f"{_MARKS[i]} {_t(tex)}" for i, tex in enumerate(option_tex))
    a, b = givens["diameter"]["a"], givens["diameter"]["b"]
    nested = "、".join(_t(_circle_tex(c)) for c in givens["nested"])
    question = (
        "莫爾圓是圓心位於 $x$ 軸上的圓。工程師經常巧妙地找到兩個特別的點 $A$ 與 $B$，使得莫爾圓就是以 $\\overline{AB}$ 為直徑的圓，如右圖所示。"
        "根據莫爾圓的定義，試回答下列問題：\n"
        f"(1) 選出符合莫爾圓定義的圓方程式。（單選）\n{lines}\n"
        f"(2) 試求以 {_t(_ptex(a, 'A'))}、{_t(_ptex(b, 'B'))} 為直徑兩端點的莫爾圓方程式。\n"
        f"(3) 工程學常碰到一個大的莫爾圓內有兩個小一點的莫爾圓之情況，如以下三個莫爾圓：{nested}。"
        "試求大莫爾圓內部、兩個小莫爾圓外部區域的面積。"
    )
    choices = [{"label": str(i), "value": txt, "text": txt} for i, txt in enumerate(option_txt, start=1)]
    parts = [
        {**_part(1, choice["value"], "choice_label_checker", "choice_label", "single_choice", choices=choices), "label": "(1)"},
        {**_record_part(2, equation), "label": "(2)"},
        {**_record_part(3, area), "label": "(3)"},
    ]
    steps = [f"(1) 只有 {_MARKS[int(choice['value']) - 1]} 的圓心在 $x$ 軸上，其他選項的圓心不在 $x$ 軸上或圖形不存在。",
             f"(2) 圓心為 $AB$ 的中點，半徑為 $AB$ 的一半，得 {_record_display(equation)}。",
             f"(3) 大圓面積減去兩個小圓面積，得 {_record_display(area)}。"]
    display = f"(1) {_MARKS[int(choice['value']) - 1]}　(2) {_record_display(equation)}　(3) {_record_display(area)}"
    spec = _figure({"figure": {"points": [{"p": a, "label": "A"}, {"p": b, "label": "B"}], "segments": [[0, 1]], "pad": 2}})
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps,
                          shape="mohr_circles", visual_spec=spec)


# --- 9. solve_storm_entry_time ------------------------------------------------------------------------------------------------------

def clock_text(hour: int) -> str:
    day, hh = divmod(int(hour), 24)
    period = "上午" if hh < 12 else "下午"
    shown = hh if hh <= 12 else hh - 12
    return f"{'當天' if day == 0 else '隔天'}{period}{shown}時"


def _solve_storm_entry_time(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    start = int(givens["start_hour"])
    options = givens["options"]
    d, r, v = (frac_latex(fr(givens[k])) for k in ("distance", "radius", "speed"))
    hh = start % 24
    period, shown = ("下午" if hh >= 12 else "上午"), (hh if hh <= 12 else hh - 12)
    news = (f"天天日報【臺北報導】中央氣象局觀測，米克拉颱風{period} ${shown}$ 時的中心位於金門正南方 ${d}$ 公里的海面上，"
            f"其暴風半徑為 ${r}$ 公里，並以每小時 ${v}$ 公里的速度朝正北方直線前進。")
    texts = [clock_text(o) for o in options]
    question = (f"{news}\n如上述新聞報導，設颱風的暴風半徑、移動方向與速度皆不變，並將颱風視為一個圓 $C$、金門視為一個點 $P$。"
                f"試選出金門進入暴風範圍大約的時間。\n" + "　".join(f"({i}){t}" for i, t in enumerate(texts, start=1)))
    choices = [{"label": str(i), "value": t, "text": t} for i, t in enumerate(texts, start=1)]
    chosen = int(answer["values"][0]["value"])
    hours = frac_latex(fr(answer["hours_after_start"]))
    part = _part(1, str(chosen), "choice_label_checker", "choice_label", "single_choice", choices=choices)
    steps = [f"颱風中心與金門的距離為 ${d}-{v}t$（$t$ 為經過的小時數）；進入暴風範圍時距離等於暴風半徑 ${r}$，得 $t={hours}$ 小時。",
             f"從{clock_text(start)}起算 ${hours}$ 小時，最接近的選項為「{texts[chosen - 1]}」。"]
    return _single_payload(matrix, question=question, part=part, display_answer=f"({chosen}){texts[chosen - 1]}",
                           explanation_steps=steps, shape="single_choice")


# --- 10. solve_circular_arch_height --------------------------------------------------------------------------------------------------------

def _solve_circular_arch_height(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    w, h, off = fr(givens["width"]), fr(givens["height"]), fr(givens["post_offset"])
    question = (f"林園造型中的圓形拱門，門面寬度 $\\overline{{PQ}}={frac_latex(w)}$ 公尺，拱高 $\\overline{{AB}}={frac_latex(h)}$ 公尺，"
                f"在距門面中心線 $\\overline{{AB}}$ 的左右 ${frac_latex(off)}$ 公尺各有一根門柱，如圖所示。求門柱 $\\overline{{PR}}$ 的高度（單位：公尺）。")
    rec = answer["values"][0]
    cy, r2 = fr(answer["centre"][1]), fr(answer["r2"])
    post = fr(rec["canonical"])
    steps = [f"以 $A$ 為原點、$\\overline{{PQ}}$ 為 $x$ 軸建立坐標系，圓心為 $\\left(0,\\ {frac_latex(cy)}\\right)$，圓方程式為 "
             f"$x^{{2}}+\\left(y-{frac_latex(cy)}\\right)^{{2}}={frac_latex(r2)}$。",
             f"門柱在 $x={frac_latex(off)}$，代入圓方程式解出較大的 $y$，得 $\\overline{{PR}}={frac_latex(post)}$ 公尺。"]
    figure = {"points": [{"p": [-w / 2, 0], "label": "Q"}, {"p": [0, 0], "label": "A"}, {"p": [w / 2, 0], "label": "P"},
                         {"p": [0, h], "label": "B"}, {"p": [off, post], "label": "R"}],
              "segments": [[1, 3], [2, 4], [0, 2]], "circles": [{"center": [0, cy], "r": radical_of_fraction(r2).value(), "label": "", "show_center": False}],
              "pad": 1, "include_origin": True}
    return _single_payload(matrix, question=question, part=_part(1, rec["canonical"], *_RATIONAL), display_answer=_record_display(rec),
                           explanation_steps=steps, shape="arch_post_height", visual_spec=_figure({"figure": figure}))


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "write_circle_equations": _write_circle_equations,
    "analyze_general_circle": _analyze_general_circle,
    "solve_distance_ratio_locus": _solve_distance_ratio_locus,
    "classify_points_against_circle": _classify_points_against_circle,
    "solve_circle_point_distances": _solve_circle_point_distances,
    "solve_point_position_parameter_range": _solve_point_position_parameter_range,
    "evaluate_circle_statement_truth": _evaluate_circle_statement_truth,
    "solve_mohr_circles": _solve_mohr_circles,
    "solve_storm_entry_time": _solve_storm_entry_time,
    "solve_circular_arch_height": _solve_circular_arch_height,
}


def adapt_circle_equations_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_circle_equations_operation:{operation}")
    return builder(matrix)
