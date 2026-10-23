"""Question payload contracts for analytic_geometry.line_equations.

Every payload is graded by a shared checker registered in ``CHECKER_CAPABILITIES``; the expected
answers always come from the domain matrix, never from this adapter.  Figures are plain
``visual_spec`` data for the shared coordinate-plane renderer.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Callable

from . import figures as FG
from . import line_geometry as G
from .line_equations_domain import DOMAIN_KEY
from .line_geometry import fr, frac_latex, frac_text, pt

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
CN = {2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七"}

_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_RADICAL = ("expression_equivalence_checker", "radical_equivalence", "numeric_or_radical")
_EQUATION = ("linear_equation_equivalent_checker", "linear_equation_equivalent", "equation")
_POINT = ("coordinate_pair_checker", "coordinate_pair_equivalence", "coordinate_pair")
_ORDER = ("ordered_inequality_checker", "ordered_inequality", "short_answer")
_RELATION_SET = ("linear_relation_set_checker", "linear_relation_set", "short_answer")


# --- contracts ---------------------------------------------------------------------------

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


def _parts_payload(matrix, *, question, parts, display_answer, explanation_steps, shape, visual_spec=None, extra=None, contract_extra=None) -> dict[str, Any]:
    return _payload(
        matrix,
        question=question,
        answer={part["key"]: part["expected_answer"] for part in parts},
        display_answer=display_answer,
        contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer",
                           answer_shape=shape, parts=parts, **(contract_extra or {})),
        explanation_steps=explanation_steps,
        visual_spec=visual_spec,
        extra=extra,
    )


def _single_payload(matrix, *, question, part, display_answer, explanation_steps, shape, visual_spec=None, extra=None) -> dict[str, Any]:
    skip = ("key", "label", "checker", "checker_key", "equivalence_type", "answer_type", "expected_answer")
    contract_extra = {k: v for k, v in part.items() if k not in skip}
    return _payload(
        matrix,
        question=question,
        answer=part["expected_answer"],
        display_answer=display_answer,
        contract=_contract(part["answer_type"], "short_answer", part["checker"], part["equivalence_type"],
                           answer_shape=shape, **contract_extra),
        explanation_steps=explanation_steps,
        visual_spec=visual_spec,
        extra=extra,
    )


def _choice_payload(matrix, *, question, choices, answer, display_answer, explanation_steps, visual_spec=None) -> dict[str, Any]:
    return _payload(
        matrix,
        question=question,
        answer=answer,
        display_answer=display_answer,
        contract=_contract("single_choice", "single_choice", "choice_label_checker", "choice_label",
                           answer_shape="single_choice", choices=[dict(c) for c in choices]),
        explanation_steps=explanation_steps,
        choices=choices,
        visual_spec=visual_spec,
    )


def _selection_part(index: int, selected: list[int]) -> dict[str, Any]:
    return _part(index, list(selected), "solution_set_checker", "unordered_solution_set", "solution_set",
                 solution_members="exact_rational", answer_format_example="2, 4")


# --- text helpers -------------------------------------------------------------------------

def _t(text: str) -> str:
    return f"${text}$"


def _ptex(p: Any, name: str = "") -> str:
    return G.point_latex(pt(p), name)


def _ltex(line: Any) -> str:
    return G.line_latex(G.norm_line(*line))


def _raw_line_tex(coefficients: Any) -> str:
    a, b, c = (fr(v) for v in coefficients)
    return f"{G.general_expr_latex(a, b, c)}=0"


def _num(value: Any) -> str:
    return frac_latex(fr(value))


def _order_tex(order_text: str) -> str:
    return re.sub(r"m(\d+)", lambda m: "m_{" + m.group(1) + "}", order_text)


def _numbered(texts: list[str]) -> str:
    return "\n".join(f"({i}) {text}" for i, text in enumerate(texts, start=1))


def _system_tex(rows: list[str]) -> str:
    return "\\left\\{\\begin{array}{l} " + " \\\\ ".join(rows) + " \\end{array} \\right."


_OP_TEX = {">=": "\\ge ", "<=": "\\le ", ">": ">", "<": "<"}


def _relation_tex(rel: dict[str, Any]) -> str:
    if rel.get("text"):
        return str(rel["text"])
    a, b, c = rel["coefficients"]
    return f"{G.general_expr_latex(a, b, c)}{_OP_TEX[rel['op']]}0"


def _line_part(index: int, record: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return _part(index, record["text"], *_EQUATION, **extra)


def _record_part(index: int, record: dict[str, Any], **extra: Any) -> dict[str, Any]:
    kind = record["kind"]
    if kind == "line":
        return _part(index, record["text"], *_EQUATION, **extra)
    if kind == "point":
        return _part(index, record["text"], *_POINT, **extra)
    if kind == "radical":
        return _part(index, record["canonical"], *_RADICAL, **{"answer_format_example": "2√5", **extra})
    return _part(index, record["canonical"], *_RATIONAL, **extra)


def _record_display(record: dict[str, Any]) -> str:
    kind = record["kind"]
    if kind == "line":
        return _t(record["text"])
    if kind == "point":
        x, y = record["point"]
        return _t(f"\\left({frac_latex(fr(x))},\\ {frac_latex(fr(y))}\\right)")
    if kind == "radical":
        return _t(record["latex"])
    return _t(frac_latex(fr(record["canonical"])))


def _items_payload(matrix, *, stem: str, prompts: list[str], records: list[dict[str, Any]], steps: list[str], shape: str,
                   visual_spec=None, labels: list[str] | None = None) -> dict[str, Any]:
    display = "　".join(f"({i}) {_record_display(r)}" if len(records) > 1 else _record_display(r)
                        for i, r in enumerate(records, start=1))
    if len(records) == 1:
        question = f"{stem}{prompts[0]}" if stem else prompts[0]
        return _single_payload(matrix, question=question, part=_record_part(1, records[0]), display_answer=display,
                               explanation_steps=steps, shape=shape, visual_spec=visual_spec)
    parts = [_record_part(i, r, **({"label": labels[i - 1]} if labels else {})) for i, r in enumerate(records, start=1)]
    question = (f"{stem}\n" if stem else "") + _numbered(prompts)
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps,
                          shape=shape, visual_spec=visual_spec)


# --- 1. rank_line_slopes ------------------------------------------------------------------

def _rank_line_slopes(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    lines = givens["lines"]
    n = len(lines)
    names = "、".join(_t(f"L_{{{ln['index']}}}") for ln in lines)
    ms = "、".join(_t(f"m_{{{ln['index']}}}") for ln in lines)
    flines = [FG.through_line(ln["p"], ln["q"], f"L_{ln['index']}") for ln in lines]
    pivot = givens.get("pivot")
    points: list[dict[str, Any]] = []
    if pivot:
        points.append(FG.point_entry(pivot["p"], pivot["name"]))
        for ln in lines:
            points.append(FG.point_entry(ln["q"], f"({frac_text(fr(ln['q'][0]))},{frac_text(fr(ln['q'][1]))})"))
    cloud = [ln["p"] for ln in lines] + [ln["q"] for ln in lines]
    view = FG.fit_view(cloud, pad=1)
    spec = FG.plane(points=points, lines=flines, view=view)
    order_text = answer["order_text"]
    steps = [f"$m_{{{r['index']}}}={frac_latex(fr(r['slope']))}$" for r in answer["slopes"]]
    steps.append(f"因此 ${_order_tex(order_text)}$。")
    if answer["ask"] == "order_only":
        question = f"右圖中，{CN.get(n, n)}直線 {names} 之斜率分別為 {ms}，試比較 {ms} 的大小。"
        part = _part(1, order_text, *_ORDER, required_form="ordered_inequality", answer_format_example="m1>m2>m3")
        return _single_payload(matrix, question=question, part=part, display_answer=_t(_order_tex(order_text)),
                               explanation_steps=steps, shape="ordered_slopes", visual_spec=spec)
    question = (f"如圖，已知直線 {names} 均通過點 {_t(_ptex(pivot['p'], pivot['name']))}，"
                f"且各自通過圖中所標示的點，求這 {_t(str(n))} 條直線的斜率並比較它們的大小。")
    parts = [{**_part(i, r["slope"], *_RATIONAL), "label": f"m{r['index']}"} for i, r in enumerate(answer["slopes"], start=1)]
    parts.append({**_part(n + 1, order_text, *_ORDER, required_form="ordered_inequality", answer_format_example="m1>m2>m3"), "label": "大小關係"})
    display = "，".join(f"$m_{{{r['index']}}}={frac_latex(fr(r['slope']))}$" for r in answer["slopes"]) + f"，{_t(_order_tex(order_text))}"
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps,
                          shape="slopes_and_order", visual_spec=spec)


# --- 2. evaluate_slope_sign_statements -----------------------------------------------------------

def _statement_text(s: dict[str, Any], count: int) -> str:
    m = lambda i: f"m_{{{i}}}"  # noqa: E731
    if s["kind"] == "sign":
        return _t(f"{m(s['index'])}{s['op']}0")
    if s["kind"] == "product":
        return _t("".join(m(i) for i in range(1, count + 1)) + f"{s['op']}0")
    if s["kind"] == "sum":
        return _t("+".join(m(i) for i in range(1, count + 1)) + f"{s['op']}0")
    return _t(">".join(m(i) for i in s["order"]))


def _evaluate_slope_sign_statements(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    names = list(givens["points"])
    segments = givens["segments"]
    seg_names = "、".join(f"直線{a}{b}" for a, b in segments)
    ms = ",".join(f"m_{{{i}}}" for i in range(1, len(segments) + 1))
    head = "、".join(_t(_ptex(givens["points"][n], n)) for n in names)
    texts = [_statement_text(s, len(segments)) for s in givens["statements"]]
    question = f"如圖，設 {head} 為坐標平面上{CN.get(len(names), len(names))}點，且{seg_names}的斜率分別為 {_t(ms)}。選出所有正確的選項。\n" + "\n".join(
        f"({i}) {text}" for i, text in enumerate(texts, start=1))
    flines = [FG.through_line(givens["points"][a], givens["points"][b]) for a, b in segments]
    points = [FG.point_entry(givens["points"][n], n) for n in names]
    view = FG.fit_view(list(givens["points"].values()), pad=1)
    selected = answer["selected"]
    steps = [f"{_t('m_{%d}=%s' % (i, frac_latex(fr(m))))}" for i, m in enumerate(answer["slopes"], start=1)]
    steps.append("正確的選項為 " + "".join(f"({i})" for i in selected) + "。")
    return _single_payload(
        matrix, question=question, part=_selection_part(1, selected),
        display_answer="".join(f"({i})" for i in selected), explanation_steps=steps,
        shape="selected_candidate_index_set", visual_spec=FG.plane(points=points, lines=flines, view=view),
    )


# --- 3. solve_line_equations ---------------------------------------------------------------------------

def _line_item_prompt(item: dict[str, Any]) -> str:
    kind = item["kind"]
    names = item.get("names") or {}
    if item.get("prompt"):
        return str(item["prompt"])
    if kind == "point_slope":
        return f"通過點 {_t(_ptex(item['p']))} 且斜率為 {_t(_num(item['m']))} 的直線。"
    if kind == "two_points":
        return f"通過 {_t(_ptex(item['p'], names.get('p', '')))} 與 {_t(_ptex(item['q'], names.get('q', '')))} 兩點的直線。"
    if kind == "slope_y_intercept":
        return f"斜率為 {_t(_num(item['m']))} 且 $y$ 截距為 {_t(_num(item['b']))} 的直線。"
    if kind == "intercepts":
        return f"$x$ 截距為 {_t(_num(item['a']))} 且 $y$ 截距為 {_t(_num(item['b']))} 的直線。"
    if kind == "vertical_through":
        return f"通過點 {_t(_ptex(item['p']))} 且沒有斜率的直線。"
    if kind in {"parallel_through", "perpendicular_through"}:
        relation = "平行" if kind == "parallel_through" else "垂直"
        if names.get("label"):
            return (f"已知直線 {_t(names['label'])} 通過 {_t(names.get('through', 'A'))} 點且與 {_t(names.get('ref', 'L'))} {relation}，"
                    f"求 {_t(names['label'])} 的方程式。")
        display = item.get("line_display") or _raw_line_tex(item["line"])
        return f"通過點 {_t(_ptex(item['p']))} 且與直線 {_t(display)} {relation}的直線。"
    if kind in {"parallel_through_intersection", "perpendicular_through_intersection"}:
        relation = "平行" if kind.startswith("parallel") else "垂直"
        d1 = item.get("l1_display") or _raw_line_tex(item["l1"])
        d2 = item.get("l2_display") or _raw_line_tex(item["l2"])
        d3 = item.get("line_display") or _raw_line_tex(item["line"])
        return f"通過兩直線 {_t(d1)} 和 {_t(d2)} 的交點，且與直線 {_t(d3)} {relation}的直線。"
    raise ValueError(f"unknown_line_item_kind:{kind}")


def _line_item_step(item: dict[str, Any], record: dict[str, Any]) -> str:
    kind = item["kind"]
    how = {
        "point_slope": "利用點斜式",
        "two_points": "先求斜率，再利用點斜式",
        "slope_y_intercept": f"直線通過 {_t(_ptex([0, item.get('b', 0)]))}，利用點斜式" if kind == "slope_y_intercept" else "",
        "intercepts": (f"直線通過 {_t(_ptex([item.get('a', 0), 0]))} 與 {_t(_ptex([0, item.get('b', 0)]))}，先求斜率再利用點斜式"
                       if kind == "intercepts" else ""),
        "vertical_through": "沒有斜率的直線是鉛直線",
        "parallel_through": "平行直線斜率相同，利用點斜式",
        "perpendicular_through": "垂直直線斜率乘積為 $-1$，利用點斜式",
        "parallel_through_intersection": "先解聯立方程式求交點，再由平行得斜率並利用點斜式",
        "perpendicular_through_intersection": "先解聯立方程式求交點，再由垂直得斜率並利用點斜式",
    }[kind]
    return f"{how}，得 {_t(record['text'])}。"


def _solve_line_equations(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    items = givens["items"]
    prompts = [_line_item_prompt(i) for i in items]
    steps = [f"({n}) {_line_item_step(i, r)}" for n, (i, r) in enumerate(zip(items, answer["values"]), start=1)]
    labels = None
    return _items_payload(matrix, stem=str(givens.get("stem", "")), prompts=prompts, records=answer["values"], steps=steps,
                          shape="line_equations", visual_spec=_figure_visual(givens.get("figure")), labels=labels)


# --- 4. slope_of_line_from_equation ----------------------------------------------------------------

def _slope_of_line_from_equation(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    name = givens.get("name", "L")
    display = givens.get("line_display") or _raw_line_tex(givens["line"])
    record = answer["values"][0]
    return _single_payload(
        matrix, question=f"求直線 {_t(name + ':' + display)} 的斜率。", part=_record_part(1, record),
        display_answer=_record_display(record),
        explanation_steps=[f"將方程式改寫為 $y=mx+k$ 的形式，得斜率為 {_record_display(record)}。"],
        shape="line_slope",
    )


# --- 5. fill_line_property_table -----------------------------------------------------------------------------

def _fill_line_property_table(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    columns = ("equation", "slope", "x_intercept", "y_intercept")
    shown = {"equation": {"equation"}, "slope_y_intercept": {"slope", "y_intercept"}, "slope_x_intercept": {"slope", "x_intercept"}}
    rows_display, blank_cells, parts, canonical, steps = [], [], [], {}, []
    for r, (row, rec) in enumerate(zip(givens["rows"], answer["rows"])):
        visible = shown[row["given"]]
        cells = []
        for c, column in enumerate(columns):
            if column in visible:
                cells.append(_t(rec["equation"]) if column == "equation" else _t(frac_latex(fr(rec[column]))))
                continue
            cells.append("")
            key = f"cell_{r}_{c}"
            if column == "equation":
                part = {**_part(len(parts) + 1, rec["equation"], *_EQUATION), "key": key, "field_key": key}
                input_type = "text"
            else:
                part = {**_part(len(parts) + 1, rec[column], *_RATIONAL), "key": key, "field_key": key}
                input_type = "number"
            parts.append(part)
            canonical[key] = part["expected_answer"]
            blank_cells.append({"row": r, "col": c, "field_key": key, "expected_answer": part["expected_answer"], "input_type": input_type})
        rows_display.append(cells)
        steps.append(f"第 {r + 1} 列：{_t(rec['equation'])}，斜率 {_t(frac_latex(fr(rec['slope'])))}，"
                     f"$x$ 截距 {_t(frac_latex(fr(rec['x_intercept'])))}，$y$ 截距 {_t(frac_latex(fr(rec['y_intercept'])))}。")
    table = {"type": "table", "headers": ["直線的方程式", "斜率", "x 截距", "y 截距"], "rows": rows_display, "blank_cells": blank_cells}
    contract = _contract("table_fill", "table_fill", "table_fill_checker", "multi_part_answer",
                         answer_shape="table_fill", parts=parts, blank_cells=blank_cells)
    question = str(givens.get("stem") or "在下列的表格中填入適當的答案：")
    return _payload(
        matrix, question=question, answer=canonical,
        display_answer="；".join(f"({i}) " + p["expected_answer"] for i, p in enumerate(parts, start=1)),
        contract=contract, explanation_steps=steps, extra={"table_data": table, "answer_shape": "table_fill"},
    )


# --- 6/7. translations --------------------------------------------------------------------------------------------

def _move_phrase(axis: str, amount: Fraction) -> str:
    if axis == "x":
        return f"向{'右' if amount > 0 else '左'}平移 {_t(frac_latex(abs(amount)))} 單位"
    return f"向{'上' if amount > 0 else '下'}平移 {_t(frac_latex(abs(amount)))} 單位"


def _translate_line_equation(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    dx, dy = fr(givens["dx"]), fr(givens["dy"])
    first = givens.get("first", "x")
    moves = [(first, dx if first == "x" else dy), ("y" if first == "x" else "x", dy if first == "x" else dx)]
    phrases = [_move_phrase(axis, amount) for axis, amount in moves if amount != 0]
    movement = "，再".join(phrases)
    shown = _raw_line_tex(givens["line"])
    record = answer["values"][0]
    if answer["direction"] == "forward":
        question = f"將直線 {_t(shown)} {movement}。求平移後的直線方程式。"
        steps = [f"平移後 $x$ 換成 $x{'+' if dx < 0 else '-'}{frac_latex(abs(dx))}$、$y$ 換成 $y{'+' if dy < 0 else '-'}{frac_latex(abs(dy))}$，得 {_t(record['text'])}。"]
    else:
        question = f"將直線 $L$ {movement}後，所得的直線為 {_t(shown)}。求直線 $L$ 的方程式。"
        steps = [f"反向平移，得直線 $L$ 為 {_t(record['text'])}。"]
    return _single_payload(matrix, question=question, part=_record_part(1, record), display_answer=_record_display(record),
                           explanation_steps=steps, shape="translated_line")


def _solve_translation_parameter(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    direction = "右" if answer["axis"] == "right" else "上"
    question = (f"將直線 {_t(_raw_line_tex(givens['line']))} 向{direction}平移 $h$ 單位後，"
                f"得到直線方程式為 {_t(_raw_line_tex(givens['result_line']))}，求 $h$ 的值。")
    record = answer["values"][0]
    return _single_payload(matrix, question=question, part=_record_part(1, record), display_answer=_record_display(record),
                           explanation_steps=[f"平移後的常數項改變量決定平移量，得 $h={frac_latex(fr(record['canonical']))}$。"],
                           shape="translation_amount")


# --- 8. solve_line_constructions -----------------------------------------------------------------------------

def _construction_prompt(item: dict[str, Any]) -> str:
    if item.get("prompt"):
        return str(item["prompt"])
    names = item.get("names") or {}
    kind = item["kind"]
    if kind == "line_through":
        return f"求直線 {_t(names.get('p', 'P') + names.get('q', 'Q'))} 的方程式。"
    if kind == "perp_bisector":
        return f"求 {_t('\\overline{' + names.get('p', 'P') + names.get('q', 'Q') + '}')} 的中垂線之方程式。"
    if kind == "circumcenter":
        return f"求△{''.join(names.get('pts', 'ABC'))}的外心坐標。"
    if kind == "orthocenter":
        return f"求△{''.join(names.get('pts', 'ABC'))}的垂心坐標。"
    if kind == "reflect_point":
        display = item.get("line_display") or _raw_line_tex(item["line"])
        return f"求點 {_t(_ptex(item['p'], names.get('p', '')))} 對於直線 {_t('L:' + display)} 的對稱點坐標。"
    raise ValueError(f"construction_prompt_required:{kind}")


def _figure_visual(figure: dict[str, Any] | None) -> dict[str, Any] | None:
    if not figure:
        return None
    pts = figure["points"]
    by_name = {p["name"]: p["p"] for p in pts}
    points = [FG.point_entry(p["p"], p.get("label", p["name"])) for p in pts]
    lines = []
    for ln in figure.get("lines", []):
        a, b = by_name[ln["through"][0]], by_name[ln["through"][1]]
        lines.append(FG.through_line(a, b, ln.get("label", ""), extend=ln.get("extend", True)))
    for coefficients in figure.get("general_lines", []):
        lines.append(FG.general_line(coefficients))
    view = FG.fit_view([p["p"] for p in pts], pad=figure.get("pad", 2), include_origin=figure.get("include_origin", True))
    extra = {"hide_unlabeled_points": True} if figure.get("hide_unlabeled") else None
    return FG.plane(points=points, lines=lines, view=view, extra=extra)


def _construction_step(item: dict[str, Any], record: dict[str, Any]) -> str:
    kind = item["kind"]
    text = _record_display(record)
    return {
        "line_through": f"先求斜率再利用點斜式，得 {text}。",
        "perp_bisector": f"中垂線通過中點且斜率與原線段斜率乘積為 $-1$，得 {text}。",
        "circumcenter": f"外心是中垂線的交點，得 {text}。",
        "orthocenter": f"垂心是三高的交點，得 {text}。",
        "reflect_point": f"對稱點與原點連線垂直於直線且中點在直線上，得 {text}。",
        "intersect_items": f"解兩直線的聯立方程式，得 {text}。",
        "shortest_path_point_on_axis": f"作 $A$ 對 $x$ 軸的對稱點 $A'$，連 $A'B$ 與 $x$ 軸的交點為 {text}。",
        "shortest_path_length": f"最短距離為 $\\overline{{A'B}}$ 的長，得 {text}。",
    }[kind]


def _solve_line_constructions(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    items = givens["items"]
    prompts = [_construction_prompt(i) for i in items]
    steps = [_construction_step(i, r) for i, r in zip(items, answer["values"])]
    if len(steps) > 1:
        steps = [f"({n}) {text}" for n, text in enumerate(steps, start=1)]
    return _items_payload(matrix, stem=str(givens.get("stem", "")), prompts=prompts, records=answer["values"], steps=steps,
                          shape="line_constructions", visual_spec=_figure_visual(givens.get("figure")))


# --- 9. solve_line_parameters ---------------------------------------------------------------------------------

def _solve_line_parameters(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    targets = answer["targets"]
    parts = []
    for index, row in enumerate(targets, start=1):
        if len(row["values"]) == 1:
            parts.append({**_part(index, row["values"][0], *_RATIONAL), "label": row["name"]})
        else:
            parts.append({**_part(index, list(row["values"]), "solution_set_checker", "unordered_solution_set", "solution_set",
                                  solution_members="exact_rational", answer_format_example="3, 55"), "label": row["name"]})
    steps = [f"解條件方程式，得 ${row['name']}=" + "$ 或 $".join(frac_latex(fr(v)) for v in row["values"]) + "$。" for row in targets]
    display = "；".join(f"${row['name']}=" + "$ 或 $".join(frac_latex(fr(v)) for v in row["values"]) + "$" for row in targets)
    question = str(givens["stem"])
    spec = _figure_visual(givens.get("figure"))
    if len(parts) == 1:
        return _single_payload(matrix, question=question, part=parts[0], display_answer=display, explanation_steps=steps,
                               shape="line_parameters", visual_spec=spec)
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps,
                          shape="line_parameters", visual_spec=spec)


# --- 10. compute_line_distances ---------------------------------------------------------------------------------

def _distance_prompt(item: dict[str, Any]) -> str:
    if item["kind"] == "point_to_line":
        display = item.get("line_display") or _raw_line_tex(item["line"])
        return f"求點 {_t(_ptex(item['p'], item.get('name', '')))} 到直線 {_t(item.get('line_name', 'L') + ':' + display)} 的距離。"
    d1 = item.get("l1_display") or _raw_line_tex(item["l1"])
    d2 = item.get("l2_display") or _raw_line_tex(item["l2"])
    return f"求兩平行直線 {_t('L_{1}:' + d1)} 與 {_t('L_{2}:' + d2)} 的距離。"


def _compute_line_distances(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    prompts = [_distance_prompt(i) for i in givens["items"]]
    steps = []
    for item, record in zip(givens["items"], answer["values"]):
        formula = "點到直線的距離公式" if item["kind"] == "point_to_line" else "兩平行直線的距離公式"
        steps.append(f"利用{formula}，得距離為 {_record_display(record)}。")
    steps = [f"({n}) {s}" for n, s in enumerate(steps, start=1)] if len(steps) > 1 else steps
    return _items_payload(matrix, stem=str(givens.get("stem", "")), prompts=prompts, records=answer["values"], steps=steps,
                          shape="line_distances")


# --- 11. solve_window_decorative_lines ----------------------------------------------------------------------------

def _window_setup(givens: dict[str, Any], answer: dict[str, Any]) -> str:
    w, h = fr(givens["width"]), fr(givens["height"])
    cx, cy = w / 2, h / 2
    spacing = answer["spacing"]
    ex, ey = pt(givens["edge_point"])
    return (
        f"設計師設計一款寬 {_t(frac_latex(w))}、高 {_t(frac_latex(h))} 的矩形窗戶，內部的裝飾線是一組以 {_t(spacing['latex'])} 為間隔距離的平行線，"
        f"由右上往左下鋪設裝飾線。右圖是設計師將窗戶坐標化後的示意圖，並僅畫兩條裝飾線為代表，"
        f"其中一條裝飾線通過窗戶的中心點 {_t('\\left(' + frac_latex(cx) + ',' + frac_latex(cy) + '\\right)')}，"
        f"而且這條裝飾線也通過窗邊的點 {_t('\\left(' + frac_latex(ex) + ',' + frac_latex(ey) + '\\right)')}。不考慮裝飾線本身的寬度，"
    )


def _window_visual(givens: dict[str, Any], answer: dict[str, Any]) -> dict[str, Any]:
    w, h = fr(givens["width"]), fr(givens["height"])
    c1 = -(w / 2 + h / 2)
    dc = fr(givens["delta_c"])
    rect = [(0, 0), (w, 0), (w, h), (0, h)]
    lines = [FG.through_line(rect[i], rect[(i + 1) % 4], extend=False) for i in range(4)]
    for label, c in (("L_1", c1), ("L_2", c1 + dc)):
        lines.append(FG.general_line((1, 1, c), label))
    centre, edge = (w / 2, h / 2), pt(givens["edge_point"])
    points = [FG.point_entry(centre, f"({frac_text(centre[0])},{frac_text(centre[1])})"),
              FG.point_entry(edge, f"({frac_text(edge[0])},{frac_text(edge[1])})")]
    view = FG.fit_view(rect + [(0, c1 * -1)], pad=3)
    return FG.plane(points=points, lines=lines, view=view)


def _solve_window_decorative_lines(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    w, h = fr(givens["width"]), fr(givens["height"])
    centre = (w / 2, h / 2)
    centre_tex = _t("\\left(" + frac_latex(centre[0]) + ",\\ " + frac_latex(centre[1]) + "\\right)")
    prompts, records, steps = [], [], []
    for ask, record in zip(answer["asks"], answer["values"]):
        records.append(record)
        if ask == "l1_equation":
            prompts.append(f"已知 $L_1$ 為通過窗戶中心點 {centre_tex} 的裝飾線所在的直線，求 $L_1$ 的方程式。")
            steps.append(f"$L_1$ 通過中心點與窗邊的點，得 {_t(record['text'])}。")
        elif ask == "l2_equation":
            prompts.append(f"已知 $L_2$ 為圖中不通過窗戶中心點 {centre_tex} 的裝飾線所在的直線，求 $L_2$ 的方程式。")
            steps.append(f"$L_2$ 與 $L_1$ 平行且相距 {_t(answer['spacing']['latex'])}，取靠近原點的一條，得 {_t(record['text'])}。")
        elif ask == "distance_origin_l1":
            prompts.append("求原點 $O$ 到直線 $L_1$ 的距離。")
            steps.append(f"由點到直線的距離公式，得 {_record_display(record)}。")
        elif ask == "line_count":
            prompts.append("試問此款窗戶共有幾條裝飾線？")
            steps.append(f"與 $L_1$ 平行且間隔 {_t(answer['spacing']['latex'])} 的直線中，穿過窗戶內部的共 {_record_display(record)} 條。")
    setup = _window_setup(givens, answer)
    asks = answer["asks"]
    if set(asks) == {"l1_equation", "l2_equation"}:
        stem = setup + "回答下列問題。"
    else:
        stem = ("承例題 11：" + setup[:-1] + f"。已知 $L_1$ 為通過窗戶中心點 {centre_tex} 的裝飾線所在的直線。回答下列問題：")
    return _items_payload(matrix, stem=stem, prompts=prompts, records=records, steps=[f"({i}) {s}" for i, s in enumerate(steps, 1)],
                          shape="window_decorative_lines", visual_spec=_window_visual(givens, answer))


# --- 12. solve_triangle_region_system ---------------------------------------------------------------------------------

def _solve_triangle_region_system(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    names = list(givens["vertices"])
    head = ",".join(_ptex(givens["vertices"][n], n) for n in names)
    choices = [{"label": str(i), "value": c["text"], "text": c["text"]} for i, c in enumerate(givens["choice_points"], start=1)]
    marks = "①②③④⑤⑥"
    option_line = "　".join(f"{marks[i]}{_t(c['text'])}" for i, c in enumerate(givens["choice_points"]))
    question = (
        f"設 $R$ 為右圖中的三角形區域（含邊界），且三頂點坐標為 {_t(head)}。\n"
        f"(1) 試以二元一次聯立不等式表示區域 $R$。\n"
        f"(2) 不論 $m$ 為任何實數，直線 $y=mx+1$ 恆過下列哪一點？（單選）\n{option_line}\n"
        f"(3) 已知 $m$ 為實數，且直線 $y=mx+1$ 平分區域 $R$ 的面積，求 $m$ 的值。"
    )
    system_text = ", ".join(answer["inequality_texts"])
    chosen = str(answer["fixed_point_choice"] + 1)
    parts = [
        {**_part(1, system_text, *_RELATION_SET, required_form="linear_relation_set",
                 answer_format_example="x+y-1≤0, x-y≥0, y≥0"), "label": "(1)"},
        {**_part(2, chosen, "choice_label_checker", "choice_label", "single_choice", choices=[dict(c) for c in choices]), "label": "(2)"},
        {**_part(3, answer["m"]["canonical"], *_RATIONAL), "label": "(3)"},
    ]
    verts = [pt(givens["vertices"][n]) for n in names]
    # shaded regions need a/b/c boundary lines: the renderer clips the shade against each of them
    lines = [FG.general_line(G.line_through(verts[i], verts[(i + 1) % 3])) for i in range(3)]
    points = [FG.point_entry(givens["vertices"][n], f"{n}({frac_text(pt(givens['vertices'][n])[0])},{frac_text(pt(givens['vertices'][n])[1])})") for n in names]
    view = FG.fit_view(verts, pad=2)
    spec = FG.plane(points=points, lines=lines, view=view, shade_probe=FG.centroid(verts))
    steps = [
        "(1) 三邊直線方程式分別代入重心判斷不等號方向，得 " + _t(_system_tex([t.replace('≤', '\\le ').replace('≥', '\\ge ') for t in answer["inequality_texts"]])) + "。",
        f"(2) 直線 $y=mx+1$ 的 $y$ 截距恆為 $1$，恆過點 {_t(choices[answer['fixed_point_choice']]['text'])}。",
        f"(3) 直線通過頂點與對邊中點 {_t(_ptex(answer['bisect_point']))}，得 $m={frac_latex(fr(answer['m']['canonical']))}$。",
    ]
    return _parts_payload(matrix, question=question, parts=parts,
                          display_answer=f"(1) {_t(_system_tex(answer['inequality_texts']))}　(2) {marks[answer['fixed_point_choice']]}　(3) {_t(frac_latex(fr(answer['m']['canonical'])))}",
                          explanation_steps=steps, shape="triangle_region_system", visual_spec=spec)


# --- 13. read_region_signs_from_figure ------------------------------------------------------------------------------------

def _read_region_signs_from_figure(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    system = _system_tex(["ax+by+c\\ge 0", "2x-y+d\\ge 0"])
    texts = [_t(f"{s['coef']}{s['op']}0") for s in givens["statements"]]
    question = (f"已知右圖的鋪色區域為二元一次聯立不等式 {_t(system)} 的解，選出所有正確的選項。\n"
                + "　".join(f"({i}) {t}" for i, t in enumerate(texts, start=1)))
    lines = [FG.general_line(ln["line"]) for ln in givens["lines"]]
    view_x0, view_x1, view_y0, view_y1 = (int(fr(v)) for v in givens["view"])
    probe = pt(answer["probe"])
    spec = FG.plane(lines=lines, view=([view_x0, view_x1], [view_y0, view_y1]), shade_probe=probe,
                    extra={"hide_unlabeled_points": True})
    c = answer["coefficients"]
    probe = pt(answer["probe"])

    def facts(letters: tuple[str, str, str], line: tuple[int, int, int]) -> str:
        a, b, k = line
        parts = []
        if b != 0:
            parts.append(f"鋪色區域在直線的{'上方' if b > 0 else '下方'}，所以 ${letters[1]}{'>' if b > 0 else '<'}0$")
        if a != 0:
            parts.append(f"也在直線的{'右側' if a > 0 else '左側'}，所以 ${letters[0]}{'>' if a > 0 else '<'}0$")
        parts.append("原點在鋪色區域內（代入得值為正），所以 $" + letters[2] + ">0$" if k > 0 else
                     ("直線通過原點，所以 $" + letters[2] + "=0$" if k == 0 else "原點不在鋪色區域內，所以 $" + letters[2] + "<0$"))
        return "；".join(parts)

    d_fact = ("原點在鋪色區域內，所以 $d>0$" if c["d"] > 0
              else ("直線通過原點，所以 $d=0$" if c["d"] == 0 else "原點不在鋪色區域內，所以 $d<0$"))
    steps = [f"對 $ax+by+c\\ge 0$：{facts(('a', 'b', 'c'), (c['a'], c['b'], c['c']))}。",
             f"對 $2x-y+d\\ge 0$：鋪色區域在直線的右側，且{d_fact}。",
             "正確的選項為 " + "".join(f"({i})" for i in answer["selected"]) + "。"]
    _ = probe
    return _single_payload(matrix, question=question, part=_selection_part(1, answer["selected"]),
                           display_answer="".join(f"({i})" for i in answer["selected"]), explanation_steps=steps,
                           shape="selected_candidate_index_set", visual_spec=spec)


# --- 14. solve_region_coefficients_from_figure ------------------------------------------------------------------------------

def _solve_region_coefficients_from_figure(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    k = frac_latex(fr(answer["bound"]))
    system = _system_tex(["x+ay\\ge 0", f"bx+cy\\le {k}", "y\\ge 0"])
    question = f"已知右圖為二元一次聯立不等式 {_t(system)} 的解區域，求 {_t('a,\\ b,\\ c')}。"
    ap, bp = pt(givens["a_point"]), pt(givens["b_point"])
    origin = (Fraction(0), Fraction(0))
    points = [FG.point_entry(origin, "O"), FG.point_entry(ap, f"A({frac_text(ap[0])},{frac_text(ap[1])})"),
              FG.point_entry(bp, f"B({frac_text(bp[0])},{frac_text(bp[1])})")]
    lines = [FG.general_line(G.line_through(origin, ap)), FG.general_line(G.line_through(ap, bp)), FG.general_line(G.line_through(origin, bp))]
    view = FG.fit_view([origin, ap, bp], pad=2)
    spec = FG.plane(points=points, lines=lines, view=view, shade_probe=FG.centroid([origin, ap, bp]))
    values = answer["values"]
    parts = [{**_part(i, v["canonical"], *_RATIONAL), "label": name} for i, (v, name) in enumerate(zip(values, ("a", "b", "c")), start=1)]
    steps = [f"直線 $x+ay=0$ 通過 $A$，得 $a={frac_latex(fr(values[0]['canonical']))}$。",
             f"直線 $bx+cy={k}$ 通過 $A$、$B$，得 $b={frac_latex(fr(values[1]['canonical']))}$、$c={frac_latex(fr(values[2]['canonical']))}$。"]
    return _parts_payload(matrix, question=question, parts=parts,
                          display_answer="，".join(f"${n}={frac_latex(fr(v['canonical']))}$" for n, v in zip("abc", values)),
                          explanation_steps=steps, shape="region_coefficients", visual_spec=spec)


# --- 15. evaluate_line_statement_truth ------------------------------------------------------------------------------------------

_SHAPE_ZH = {"rectangle": "矩形", "parallelogram": "平行四邊形", "rhombus": "菱形", "trapezoid": "梯形", "kite": "箏形"}


def _statement_sentence(s: dict[str, Any]) -> str:
    kind = s["kind"]
    if kind == "shape_equal_slopes":
        if s.get("negated"):
            return f"任一個{_SHAPE_ZH[s['shape']]}的四個邊中，任兩個邊所在的直線斜率都不相等。"
        return f"任一個{_SHAPE_ZH[s['shape']]}的四個邊中，至少會有兩個邊所在的直線斜率相等。"
    if kind == "y_intercept_of_line_through_point":
        extra = "且斜率存在，" if s.get("slope_exists") else ""
        return f"若直線 $L$ 通過 {_t('\\left(0,\\ ' + frac_latex(fr(s['through_y'])) + '\\right)')}，{extra}則 $L$ 的 $y$ 截距為 {_t(frac_latex(fr(s['claimed'])))}。"
    if kind == "perpendicular_by_coefficients":
        return f"直線 {_t(_raw_line_tex(s['l1']))} 與 {_t(_raw_line_tex(s['l2']))} 互相垂直。"
    if kind == "parallel_at_distance_count":
        count = CN.get(int(s["claimed_count"]), str(s["claimed_count"]))
        return f"在平面上恰有{count}條直線與直線 {_t(_raw_line_tex(s['line']))} 平行且距離為 {_t(frac_latex(fr(s['distance'])))}。"
    if kind == "opposite_sides":
        return (f"點 {_t(_ptex(s['a'], s.get('a_name', 'A')))} 與點 {_t(_ptex(s['b'], s.get('b_name', 'B')))} "
                f"在直線 {_t(_raw_line_tex(s['line']))} 的相異兩側。")
    raise ValueError(f"unknown_statement_kind:{kind}")


def _statement_explanation(s: dict[str, Any], answer: dict[str, Any]) -> str:
    kind, truth = s["kind"], answer["truth"]
    if kind == "shape_equal_slopes":
        if s.get("negated"):
            return "只要有一組平行的對邊（斜率存在時斜率相等），就不能說任兩邊斜率都不相等；反之若沒有任何平行的邊才成立。"
        if truth:
            return "有兩組對邊平行；平行的對邊斜率相等（鉛直對邊沒有斜率時，另一組對邊必為水平且斜率同為 $0$），故至少有兩邊斜率相等。"
        return "圖形的對邊不一定成對平行，且鉛直的邊沒有斜率，所以不一定有兩邊斜率相等。"
    if kind == "y_intercept_of_line_through_point":
        return "直線與 $y$ 軸交點的縱坐標才是 $y$ 截距；若直線為鉛直線，則沒有 $y$ 截距。" if not truth else "直線過 $(0,k)$ 且斜率存在時，$y$ 截距為 $k$。"
    if kind == "perpendicular_by_coefficients":
        return "兩直線垂直的條件是斜率乘積為 $-1$（或係數滿足 $a_1a_2+b_1b_2=0$）。"
    if kind == "parallel_at_distance_count":
        return "與已知直線平行且距離為正數 $d$ 的直線在兩側各有一條，共二條。"
    return "把兩點代入 $ax+by+c$，異號則在直線兩側，同號則在同側。"


def _evaluate_line_statement_truth(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    statement = givens["statement"]
    mark = "○" if answer["truth"] else "×"
    question = "下列敘述對的打「○」，錯的打「×」。\n" + _statement_sentence(statement)
    return _choice_payload(matrix, question=question, choices=TRUE_FALSE_CHOICES, answer=mark, display_answer=mark,
                           explanation_steps=[f"{_statement_explanation(statement, answer)}此敘述為「{mark}」。"])


# --- 16. select_points_same_side ------------------------------------------------------------------------------------------------------

def _select_points_same_side(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    line_tex = givens.get("line_display") or _raw_line_tex(givens["line"])
    ref = givens["reference"]
    options = "　".join(f"({i}) {_t(_ptex(p))}" for i, p in enumerate(givens["points"], start=1))
    question = (f"已知直線 {_t('L:' + line_tex)} 將坐標平面上 $L$ 以外的部分分成兩個半平面，"
                f"求下列選項中哪些點與{givens.get('reference_name', '原點')} {_t(_ptex(ref))} 位在同一個半平面？\n{options}")
    value = G.side_value(G.norm_line(*givens["line"]), pt(ref))
    steps = []
    for i, (p, side) in enumerate(zip(givens["points"], answer["sides"]), start=1):
        v = G.side_value(G.norm_line(*givens["line"]), pt(p))
        status = "在直線上，不屬於任何半平面" if side == 0 else ("與參考點同側" if side == 1 else "與參考點異側")
        steps.append(f"({i}) 代入得 {_t(frac_latex(v))}，{status}。")
    steps.append(f"參考點代入得 {_t(frac_latex(value))}。")
    return _single_payload(matrix, question=question, part=_selection_part(1, answer["selected"]),
                           display_answer="".join(f"({i})" for i in answer["selected"]) or "無",
                           explanation_steps=steps, shape="selected_candidate_index_set")


# --- 17. graph_inequality_system (drawing) ----------------------------------------------------------------------------------------------

def _graph_inequality_system(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    texts = [_relation_tex(rel) for rel in givens["relations"]]
    if len(texts) == 1:
        question = f"圖示二元一次不等式 {_t(texts[0])} 的解。"
    else:
        question = f"圖示二元一次聯立不等式 {_t(_system_tex(texts))} 的解。"
    view = answer["view"]
    x0, x1, y0, y1 = (int(fr(v)) for v in view)
    spec = {
        "drawing_type": "linear_inequality_region",
        "graph_kind": "linear_inequality_region",
        "relations": [
            {"line": list(rel["line"]), "boundary": rel["boundary"], "shaded_side": "positive_normal"}
            for rel in answer["relations"]
        ],
        "region_polygon": answer["region_polygon"],
        "probe_point": answer["probe"],
        "boundary_intersection": answer["corner"],
        "boundary_intersection_excluded": bool(answer["corner"] and answer["corner_excluded"]),
        "required_elements": ["x_axis", "y_axis", "boundary_lines", "shaded_region"],
        "axis_range": {"x_min": x0, "x_max": x1, "y_min": y0, "y_max": y1},
        "tolerance": {"line_position": 0.5, "slope": 0.12},
    }
    ui_contract = {
        "response_mode": "drawing",
        "drawing_required": True,
        "ai_check_required": True,
        "text_answer_enabled": False,
        "text_input_enabled": False,
        "submit_button_enabled": False,
        "normal_submit_enabled": False,
        "success_dialog_required": True,
        "canvas_required": True,
        "allow_image_upload": False,
        "allow_text_answer": False,
    }
    reference = []
    for rel, text in zip(givens["relations"], texts):
        a, b, _c = (fr(v) for v in rel["coefficients"])
        positive = rel["op"] in (">", ">=")
        if b != 0:
            side = "上方" if (b > 0) == positive else "下方"
        else:
            side = "右側" if (a > 0) == positive else "左側"
        style = "實線" if rel["op"] in (">=", "<=") else "虛線"
        reference.append(f"{_t(text)}：邊界畫{style}，鋪色在直線的{side}")
    steps = ["先畫出各不等式的邊界直線（含等號用實線、不含等號用虛線），再取一個不在直線上的點判斷要塗哪一側，最後取共同部分。"]
    if answer["corner"] and answer["corner_excluded"] and len(answer["relations"]) > 1:
        steps.append("兩邊界直線的交點不屬於解區域。")
    return _payload(
        matrix, question=question, answer=spec, display_answer="；".join(reference) + ("；取共同部分" if len(reference) > 1 else ""),
        contract=_contract("drawing", "canvas", "free_response_drawing_checker", "drawing_equivalence",
                           answer_shape="drawing", expected_drawing_spec=spec, ui_contract=ui_contract),
        explanation_steps=steps, visual_spec=FG.blank_canvas(view),
        extra={
            "answer_shape": "drawing", "interaction_type": "handwriting_drawing", "expected_drawing_spec": spec,
            "metadata": {"expected_drawing_spec": spec, "ui_contract": ui_contract, "answer_type": "drawing", "answer_shape": "drawing"},
        },
    )


# --- 18. solve_rectangle_perpendicular_diagonals -------------------------------------------------------------------------------------------------

def _solve_rectangle_perpendicular_diagonals(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    h, w = fr(givens["ab"]), fr(givens["bf"])
    record = answer["values"][0]
    value = float(fr(record["rational_part"])) + float(fr(record["coef"])) * (record["radicand"] ** 0.5)
    a = value
    corners = {"A": (0, float(h)), "B": (0, 0), "C": (float(w) + a, 0), "D": (float(w) + a, float(h)), "E": (float(w), float(h)), "F": (float(w), 0)}
    points = [FG.point_entry(p, n) for n, p in corners.items()]
    lines = [FG.through_line(corners[x], corners[y], extend=False) for x, y in
             (("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("E", "F"), ("B", "D"), ("C", "E"))]
    view = FG.fit_view(list(corners.values()), pad=1)
    spec = FG.plane(points=points, lines=lines, view=view, extra={"hide_unlabeled_points": True})
    question = (f"如圖，矩形 $ABCD$ 的對角線 $\\overline{{BD}}$ 與矩形 $CDEF$ 的對角線 $\\overline{{CE}}$ 互相垂直，"
                f"已知 $\\overline{{AB}}={frac_latex(h)}$、$\\overline{{BF}}={frac_latex(w)}$、$\\overline{{CF}}=a$，求 $a$ 的值。")
    steps = ["以 $B$ 為原點建立坐標，$\\overline{BD}$ 與 $\\overline{CE}$ 斜率乘積為 $-1$，得 $a^2+" + f"{frac_latex(w)}a-{frac_latex(h * h)}=0$，取正根得 {_t(record['latex'])}。"]
    return _single_payload(matrix, question=question, part=_record_part(1, record), display_answer=_t(record["latex"]),
                           explanation_steps=steps, shape="rectangle_diagonals", visual_spec=spec)


# --- 19. solve_axis_triangle_area_line -------------------------------------------------------------------------------------------------------------

def _solve_axis_triangle_area_line(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    texts = [rec["text"] for rec in answer["values"]]
    question = (f"設直線 $L$ 通過點 {_t(_ptex(givens['point']))} 且與兩軸圍成的三角形面積為 {_t(frac_latex(fr(givens['area'])))}。"
                "求 $L$ 的方程式。（若有多條，請全部寫出，以逗號分隔）")
    part = _part(1, ", ".join(texts), *_RELATION_SET, required_form="linear_relation_set",
                 answer_format_example="x+2y-3=0, x-y+1=0")
    steps = ["設 $x$ 截距為 $a$、$y$ 截距為 $b$，則 $\\frac{x_0}{a}+\\frac{y_0}{b}=1$ 且 $|ab|=2S$，解得截距後得所有直線。"]
    return _single_payload(matrix, question=question, part=part,
                           display_answer="　或　".join(_t(t) for t in texts), explanation_steps=steps, shape="line_set")


# --- 20. solve_parallel_line_family -------------------------------------------------------------------------------------------------------------------

def _solve_parallel_line_family(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    ap, bp, pp = pt(givens["a_point"]), pt(givens["b_point"]), pt(givens["p_point"])
    spacing = fr(givens["spacing"])
    distance, index, line_n = answer["values"]
    base = G.line_through(ap, bp)
    sign = 1 if G.side_value(base, pp) > 0 else -1
    root = G.sqrt_radical(base[0] ** 2 + base[1] ** 2).coef
    n = int(index["canonical"])

    def shifted(k: int) -> G.Line:
        return G.norm_line(base[0], base[1], Fraction(base[2]) - sign * k * spacing * root)

    lines = [FG.general_line(base, "AB")]
    for k, label in ((1, "L_1"), (2, "L_2"), (n - 1, "L_{n-1}"), (n, "L_n")):
        lines.append(FG.general_line(shifted(k), label))
    points = [FG.point_entry(ap, "A"), FG.point_entry(bp, "B"), FG.point_entry(pp, "P")]
    view = FG.fit_view([ap, bp, pp], pad=3)
    spec = FG.plane(points=points, lines=lines, view=view, extra={"hide_unlabeled_points": True})
    question = (
        f"如圖，小明以 {_t(frac_latex(spacing))} 單位為間隔距離，從直線 $AB$ 朝 $P$ 點的方向作一組與直線 $AB$ 平行的平行線 "
        "$L_1$、$L_2$、$\\cdots$、$L_n$，並使 $P$ 點介於直線 $L_{n-1}$ 與 $L_n$ 之間，如圖所示。"
        f"已知 $A$, $B$, $P$ 三點的坐標分別為 {_t(_ptex(ap, 'A'))}、{_t(_ptex(bp, 'B'))}、{_t(_ptex(pp, 'P'))}，回答下列問題：\n"
        "(1) $P$ 點到直線 $AB$ 的距離為________。\n(2) 求正整數 $n$ 的值。\n(3) 求直線 $L_n$ 的方程式。"
    )
    parts = [
        {**_part(1, distance["canonical"], *_RATIONAL), "label": "(1)"},
        {**_part(2, index["canonical"], *_RATIONAL), "label": "(2)"},
        {**_part(3, line_n["text"], *_EQUATION), "label": "(3)"},
    ]
    steps = [
        f"(1) $P$ 到直線 $AB:{G.line_latex(base)}$ 的距離為 {_t(frac_latex(fr(distance['canonical'])))}。",
        f"(2) 距離介於 ${frac_latex(spacing * (n - 1))}$ 與 ${frac_latex(spacing * n)}$ 之間，故 $n={n}$。",
        f"(3) $L_n$ 與 $AB$ 平行且相距 ${frac_latex(spacing * n)}$，得 {_t(line_n['text'])}。",
    ]
    return _parts_payload(matrix, question=question, parts=parts,
                          display_answer=f"(1) {_t(frac_latex(fr(distance['canonical'])))}　(2) {_t(str(n))}　(3) {_t(line_n['text'])}",
                          explanation_steps=steps, shape="parallel_line_family", visual_spec=spec)


# --- 17b/17c. drawing parts inside a multi_part answer (one independent canvas per drawing part) --------------------------

def _region_spec(answer: dict[str, Any]) -> dict[str, Any]:
    x0, x1, y0, y1 = (int(fr(v)) for v in answer["view"])
    return {
        "drawing_type": "linear_inequality_region",
        "graph_kind": "linear_inequality_region",
        "relations": [{"line": list(rel["line"]), "boundary": rel["boundary"], "shaded_side": "positive_normal"}
                      for rel in answer["relations"]],
        "region_polygon": answer["region_polygon"],
        "probe_point": answer["probe"],
        "boundary_intersection": answer["corner"],
        "boundary_intersection_excluded": bool(answer["corner"] and answer["corner_excluded"]),
        "required_elements": ["x_axis", "y_axis", "boundary_lines", "shaded_region"],
        "axis_range": {"x_min": x0, "x_max": x1, "y_min": y0, "y_max": y1},
        "tolerance": {"line_position": 0.5, "slope": 0.12},
    }


def _drawing_part(index: int, answer: dict[str, Any], label: str, prompt: str) -> dict[str, Any]:
    spec = _region_spec(answer)
    return {
        **_part(index, spec, "free_response_drawing_checker", "drawing_equivalence", "drawing"),
        "label": label,
        "prompt": prompt,
        "input_type": "canvas",
        "canvas": {"axis_range": dict(spec["axis_range"]), "show_grid": True},
        "expected_drawing_spec": spec,
        "drawing_required": True,
        "ai_check_required": True,
        "text_answer_enabled": False,
    }


def _drawing_reference(relations: list[dict[str, Any]], texts: list[str]) -> str:
    out = []
    for rel, text in zip(relations, texts):
        a, b, _c = (fr(v) for v in rel["coefficients"])
        positive = rel["op"] in (">", ">=")
        side = ("上方" if (b > 0) == positive else "下方") if b != 0 else ("右側" if (a > 0) == positive else "左側")
        style = "實線" if rel["op"] in (">=", "<=") else "虛線"
        out.append(f"{_t(text)}：邊界畫{style}，鋪色在直線的{side}")
    return "；".join(out)


def _graph_inequality_series(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    texts = [[_relation_tex(rel) for rel in item["relations"]] for item in givens["items"]]
    question = "圖示下列二元一次不等式的解：\n" + "\n".join(
        f"({i}) {_t(t[0]) if len(t) == 1 else _t(_system_tex(t))}" for i, t in enumerate(texts, start=1))
    parts = [_drawing_part(i, drawing, f"({i})", f"圖示第 ({i}) 小題的解")
             for i, drawing in enumerate(answer["drawings"], start=1)]
    reference = [f"({i}) " + _drawing_reference(item["relations"], t) for i, (item, t) in enumerate(zip(givens["items"], texts), start=1)]
    return _parts_payload(
        matrix, question=question, parts=parts, display_answer="　".join(reference),
        explanation_steps=["每一小題各畫在自己的坐標平面上：先畫邊界直線（含等號用實線、不含等號用虛線），再取一點判斷鋪色的一側。"] + reference,
        shape="independent_drawings", contract_extra={"drawing_parts": True},
    )


def _graph_inequality_with_lattice_count(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    texts = [_relation_tex(rel) for rel in givens["relations"]]
    question = (
        "在坐標平面上，當一個點 $\\left(x,\\ y\\right)$ 的 $x$ 坐標與 $y$ 坐標都是整數時，稱此點為格子點。\n"
        f"(1) 圖示二元一次聯立不等式 {_t(_system_tex(texts))} 的解。\n"
        "(2) 求在此解區域內（含邊界）有多少個格子點。"
    )
    count = answer["values"][0]
    parts = [_drawing_part(1, answer["drawing"], "(1)", "圖示聯立不等式的解"),
             {**_part(2, count["canonical"], *_RATIONAL), "label": "(2)"}]
    steps = ["(1) " + _drawing_reference(givens["relations"], texts),
             f"(2) 逐一檢查整數點，解區域（含邊界）內共有 {_t(count['canonical'])} 個格子點。"]
    return _parts_payload(
        matrix, question=question, parts=parts,
        display_answer=f"(1) 見圖解　(2) {_t(count['canonical'])}", explanation_steps=steps,
        shape="drawing_and_count", contract_extra={"drawing_parts": True},
    )


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "rank_line_slopes": _rank_line_slopes,
    "evaluate_slope_sign_statements": _evaluate_slope_sign_statements,
    "solve_line_equations": _solve_line_equations,
    "slope_of_line_from_equation": _slope_of_line_from_equation,
    "fill_line_property_table": _fill_line_property_table,
    "translate_line_equation": _translate_line_equation,
    "solve_translation_parameter": _solve_translation_parameter,
    "solve_line_constructions": _solve_line_constructions,
    "solve_line_parameters": _solve_line_parameters,
    "compute_line_distances": _compute_line_distances,
    "solve_window_decorative_lines": _solve_window_decorative_lines,
    "solve_triangle_region_system": _solve_triangle_region_system,
    "read_region_signs_from_figure": _read_region_signs_from_figure,
    "solve_region_coefficients_from_figure": _solve_region_coefficients_from_figure,
    "evaluate_line_statement_truth": _evaluate_line_statement_truth,
    "select_points_same_side": _select_points_same_side,
    "graph_inequality_system": _graph_inequality_system,
    "graph_inequality_series": _graph_inequality_series,
    "graph_inequality_with_lattice_count": _graph_inequality_with_lattice_count,
    "solve_rectangle_perpendicular_diagonals": _solve_rectangle_perpendicular_diagonals,
    "solve_axis_triangle_area_line": _solve_axis_triangle_area_line,
    "solve_parallel_line_family": _solve_parallel_line_family,
}


def adapt_line_equations_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_line_equations_operation:{operation}")
    return builder(matrix)
