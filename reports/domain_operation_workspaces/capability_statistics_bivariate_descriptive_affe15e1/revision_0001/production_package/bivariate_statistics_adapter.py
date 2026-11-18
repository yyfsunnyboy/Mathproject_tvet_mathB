"""Question payload contracts for statistics.bivariate_descriptive (普高數學2 Unit 9 二維數據分析).

Drawing sub-questions (散布圖) are never graded: stems ask only for the numeric / choice part. Figure-only
textbook items are deferred (see ``VISUAL_CAPABILITY_GAP`` in the specs).
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Any, Callable

from core.gencode.multipart_stem_contract import build_stem_structure, stem_structure_to_question_text

from .bivariate_statistics_domain import DOMAIN_KEY, TRUE_FALSE, UP_DOWN  # noqa: F401

_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_SET = ("solution_set_checker", "unordered_solution_set", "solution_set")
_EQUATION = ("linear_equation_equivalent_checker", "linear_equation_equivalent", "equation")
_TF_HEAD = "下列敘述對的打「○」，錯的打「×」。\n"
_MULTI_HINT = "（多選題，請以逗號分隔選項編號作答）"
_NUMBER_HINT = "（可用最簡分數或小數表示）"
_ZH = "零一二三四五六七八九十十一十二"
_MONTHS = ("一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二")
_PEOPLE = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")


def _zh(n: int) -> str:
    if n <= 10:
        return _ZH[n]
    return "十" + _ZH[n - 10] if n < 20 else str(n)


# --- contracts (same shape as the Unit 8 adapter) ----------------------------------------------------------------------


def _contract(answer_type: str, presentation_mode: str, checker: str, equivalence: str, **extra: Any) -> dict[str, Any]:
    return {
        "presentation_mode": presentation_mode, "answer_type": answer_type, "checker": checker, "checker_key": checker,
        "answer_equivalence": equivalence, "equivalence": equivalence, "equivalence_type": equivalence, **extra,
    }


def _part(index: int, expected: Any, checker: str, equivalence: str, answer_type: str, **extra: Any) -> dict[str, Any]:
    row = {
        "key": f"part_{index}", "label": f"({index})", "group_label": f"({index})", "answer_order": index - 1,
        "checker": checker, "checker_key": checker, "equivalence_type": equivalence, "answer_type": answer_type,
        "expected_answer": expected, **extra,
    }
    row["display_label"] = row["label"]
    return row


def _payload(matrix, *, question, answer, display_answer, contract, explanation_steps, choices=(), stem=None) -> dict[str, Any]:
    operation = matrix["domain_operation"]
    out = {
        "question_text": question, "question": question, "answer": answer, "correct_answer": answer,
        "display_answer": display_answer, "semantic_answer": matrix["answer"], "answer_type": contract["answer_type"],
        "presentation_mode": contract["presentation_mode"], "problem_type_id": operation, "domain_operation": operation,
        "fixed_domain_key": DOMAIN_KEY, "answer_contract": {**contract, "semantic_answer": matrix["answer"]},
        "explanation_steps": explanation_steps, "choices": [dict(c) for c in choices], "options": [dict(c) for c in choices],
        "math_core": {"givens": matrix["givens"], "target": matrix["answer"], "validation_facts": matrix["validation_facts"]},
    }
    if stem:
        out["stem_structure"] = stem
        out["metadata"] = {"stem_structure": stem}
    return out


def _single_payload(matrix, *, question, part, display_answer, explanation_steps, shape, stem=None) -> dict[str, Any]:
    skip = ("key", "label", "display_label", "group_label", "answer_order", "input_type", "checker", "checker_key",
            "equivalence_type", "answer_type", "expected_answer", "prompt")
    extra = {k: v for k, v in part.items() if k not in skip}
    if part["answer_type"] == "single_choice":
        return _payload(
            matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
            contract=_contract("single_choice", "single_choice", "choice_label_checker", "choice_label",
                               answer_shape="single_choice", choices=[dict(c) for c in part["choices"]]),
            explanation_steps=explanation_steps, choices=part["choices"], stem=stem,
        )
    return _payload(
        matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
        contract=_contract(part["answer_type"], "short_answer", part["checker"], part["equivalence_type"], answer_shape=shape, **extra),
        explanation_steps=explanation_steps, stem=stem,
    )


def _parts_payload(matrix, *, question, parts, display_answer, explanation_steps, shape, stem=None) -> dict[str, Any]:
    if len(parts) == 1:
        return _single_payload(matrix, question=question, part=parts[0], display_answer=display_answer,
                               explanation_steps=explanation_steps, shape=shape, stem=stem)
    if stem and len(stem["items"]) != len(parts):
        raise ValueError("multipart_stem_items_must_match_parts")
    return _payload(
        matrix, question=question, answer={p["key"]: p["expected_answer"] for p in parts}, display_answer=display_answer,
        contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer", answer_shape=shape, parts=parts),
        explanation_steps=explanation_steps, stem=stem,
    )


# --- text / table helpers --------------------------------------------------------------------------------------------


def _m(latex: str) -> str:
    return "$" + latex + "$"


def _tx(text: str) -> str:
    return r"\text{" + text + "}"


def _terminating(f: Fraction) -> bool:
    d = f.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def _num_tex(v: Any) -> str:
    """A rational in LaTeX: integer, terminating decimal as stated, or \\frac (never a bare a/b)."""
    text = str(v).strip()
    f = Fraction(text)
    if f.denominator == 1 or "/" not in text and _terminating(f):
        return text
    if _terminating(f):
        return format(Decimal(f.numerator) / Decimal(f.denominator), "f")
    sign = "-" if f < 0 else ""
    return rf"{sign}\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"


def _n(v: Any) -> str:
    return _m(_num_tex(v))


def _coef_tex(a: Fraction) -> str:
    if a.denominator == 1:
        return {1: "", -1: "-"}.get(a.numerator, str(a.numerator))
    sign = "-" if a < 0 else ""
    return rf"{sign}\frac{{{abs(a.numerator)}}}{{{a.denominator}}}"


def _array(headers: list[str], rows: list[list[str]]) -> str:
    """Table in the formal-bank form: one \\(...\\) block, rows ended by \\\\, cells are bare LaTeX."""
    cols = len(headers)
    table = [headers, *rows]
    if any(len(row) != cols for row in rows):
        raise ValueError("table_shape")
    if any("$" in cell or r"\(" in cell or r"\)" in cell for row in table for cell in row):
        raise ValueError("nested_math_delimiter")
    spec = "|" + "|".join(["c"] * cols) + "|"
    body = r" \\ \hline ".join(" & ".join(row) for row in table)
    return r"\(\begin{array}{" + spec + r"}\hline " + body + r" \\ \hline \end{array}\)"


def _xy_table(xs: list[Any], ys: list[Any], xlabel: str | None, ylabel: str | None, id_label: str | None = None, ids: list[str] | None = None) -> str:
    """x-over-y table: plain ``x``/``y`` row labels, or text labels such as 最高氣溫x（℃）."""
    x_cell = _tx(xlabel) if xlabel else "x"
    y_cell = _tx(ylabel) if ylabel else "y"
    xv, yv = [_num_tex(v) for v in xs], [_num_tex(v) for v in ys]
    if id_label:
        return _array([_tx(id_label)] + [_tx(i) for i in ids], [[x_cell] + xv, [y_cell] + yv])
    return _array([x_cell] + xv, [[y_cell] + yv])


def _point_tex(x: Any, y: Any) -> str:
    return rf"\left({_num_tex(x)},{_num_tex(y)}\right)"


# --- parts ------------------------------------------------------------------------------------------------------------


def _value_part(index: int, item: dict, label: str) -> dict[str, Any]:
    return _part(index, str(item["value"]), *_RATIONAL, label=label, prompt=label)


def _equation_part(index: int, item: dict, label: str) -> dict[str, Any]:
    return _part(index, item["value"], *_EQUATION, label=label, prompt=label)


def _choice_part(index: int, item: dict, label: str) -> dict[str, Any]:
    return _part(index, item["label"], "choice_label_checker", "choice_label", "single_choice",
                 choices=[dict(c) for c in item["choices"]], input_type="select", label=label, prompt=label)


def _selected_part(index: int, item: dict, label: str) -> dict[str, Any]:
    return _part(index, [str(i) for i in item["selected"]], *_SET, label=label, prompt=label, solution_members="exact_rational")


def _show(item: dict[str, Any]) -> str:
    if item["kind"] == "choice":
        return next(c["value"] for c in item["choices"] if c["label"] == item["label"])
    if item["kind"] == "selected":
        return "".join(f"({i})" for i in item["selected"])
    if item["kind"] == "equation":
        return item["display"]
    from .bivariate_statistics_domain import _show as show_value

    return show_value(Fraction(item["value"]))


def _builder(item: dict, label: str):
    def build(i, it):
        if it["kind"] == "choice":
            return _choice_part(i, it, label)
        if it["kind"] == "selected":
            return _selected_part(i, it, label)
        if it["kind"] == "equation":
            return _equation_part(i, it, label)
        return _value_part(i, it, label)
    return label, build


def _from_parts(matrix, question: str | tuple[str, list[str]], labels: list[str], shape: str) -> dict[str, Any]:
    raw = matrix["answer"]["parts"]
    if len(raw) != len(labels):
        raise ValueError("part_count")
    builders = [_builder(item, label) for item, label in zip(raw, labels)]
    stem = None
    if isinstance(question, tuple) and len(question[1]) == 1:
        question = f"{question[0]}\n{question[1][0]}"
    elif isinstance(question, tuple):
        prompt, items = question
        stem = build_stem_structure(prompt, [{"group_label": f"({i})", "text": text} for i, text in enumerate(items, 1)])
        question = stem_structure_to_question_text(stem)
    parts = [build(i, item) for i, ((_label, build), item) in enumerate(zip(builders, raw), 1)]
    if len(raw) == 1:
        display, steps = _show(raw[0]), [raw[0]["work"]]
    else:
        display = "；".join(f"({i}){_show(item)}" for i, item in enumerate(raw, 1))
        steps = [f"({i}) {item['work']}" for i, item in enumerate(raw, 1)]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps, shape=shape, stem=stem)


# --- scenes (wording of the textbook rows; numbers come from the givens) ----------------------------------------------

CORRELATION_SCENES: dict[str, dict[str, Any]] = {
    "plain": {"intro": "兩變量x與y的數據如下表。", "xlabel": None, "ylabel": None},
    "aptitude": {"intro": "{n}位同學的性向測驗x（分）與成就測驗y（分）的成績對照如下表。",
                 "xlabel": "性向測驗x（分）", "ylabel": "成就測驗y（分）"},
}
REGRESSION_SCENES: dict[str, dict[str, Any]] = {
    "temp_sales": {
        "intro": "飲料店調閱上個月某{n}天的當日最高氣溫x（℃）與銷售金額y（千元）之對照如下表。",
        "xlabel": "最高氣溫x（℃）", "ylabel": "銷售金額y（千元）", "ids": None, "scale": 1,
        "predict": "已知某天的當日最高氣溫為 {x0}℃，利用迴歸直線估計當日的銷售金額（單位：千元）。",
    },
    "eq_achievement": {
        "intro": "某機構研究{n}位成人的EQ（情緒商數）測驗分數x（分）與職場成就測驗分數y（分）之對照如下表。",
        "xlabel": "EQ測驗分數x（分）", "ylabel": "職場成就測驗分數y（分）", "ids": "成人代號", "scale": 1,
        "predict": "已知某人的EQ測驗分數為 {x0} 分，利用迴歸直線估計其職場成就測驗分數（單位：分）。",
    },
    "price_demand": {
        "intro": "某公司在推出一款新電腦前，調查單價x（千元）與市場需求量y（十萬臺）的對照如下表。",
        "xlabel": "單價x（千元）", "ylabel": "市場需求量y（十萬臺）", "ids": None, "scale": 1000,
        "predict": "已知電腦上市的單價為 {x0} 元，利用迴歸直線預估市場的需求量（單位：十萬臺）。",
    },
}
FOREARM_INTRO = "某人測量{n}位女性的前臂長度x（公分）與身高y（公分）之對照如下表。"
FOREARM_LABELS = ("前臂長度x（公分）", "身高y（公分）")


def _fixed(v: Any, places: int) -> str:
    from .bivariate_statistics_domain import _fixed as fixed

    return fixed(Fraction(str(v)), places)


# --- operations -------------------------------------------------------------------------------------------------------


def _correlation_from_table(matrix):
    g = matrix["givens"]
    scene = CORRELATION_SCENES[g.get("scene", "plain")]
    n = len(g["x"])
    intro = scene["intro"].format(n=_zh(n))
    table = _xy_table(g["x"], g["y"], scene["xlabel"], scene["ylabel"])
    q = f"{intro}\n{table}\n求x與y的相關係數。{_NUMBER_HINT}"
    return _from_parts(matrix, q, ["相關係數"], "correlation_from_table")


def _correlation_remove_point(matrix):
    g = matrix["givens"]
    table = _xy_table(g["x"], g["y"], None, None, "代號", list(g["labels"]))
    q = f"有{_zh(len(g['x']))}筆數據資料如下表。\n{table}\n試問去掉哪一筆數據後，剩下來{_zh(len(g['x']) - 1)}筆數據的相關係數最大？"
    return _from_parts(matrix, q, ["去掉的數據"], "correlation_remove_point")


def _correlation_change_add_point(matrix):
    g = matrix["givens"]
    table = _xy_table(g["x"], g["y"], *FOREARM_LABELS)
    q = (f"{FOREARM_INTRO.format(n=_zh(len(g['x'])))}\n{table}\n"
         f"若今新增一筆資料 {_m(_point_tex(*g['new_point']))}，試問x與y的相關係數會變大還是變小？")
    return _from_parts(matrix, q, ["變化"], "correlation_change_add_point")


def _correlation_rescale(matrix):
    g = matrix["givens"]
    n, old, new = int(g["n_questions"]), int(g["old_per"]), int(g["new_per"])
    prompt = (f"段考數學考題共有 {_n(n)} 題，每題 {_n(old)} 分，總分 {_n(n * old)} 分。經統計：全校數學最高分 {_n(g['top'])} 分，"
              f"且數學成績與英文成績的相關係數為 {_n(g['r'])}。\n已知老師將數學每題 {_n(old)} 分的配分更改為每題 {_n(new)} 分，"
              f"藉以調高數學成績，求")
    return _from_parts(matrix, (prompt, ["調高後的數學成績與英文成績的相關係數。", "調高後的數學成績與原數學成績的相關係數。"]),
                       ["相關係數", "相關係數"], "correlation_rescale")


_SYMBOL = {"mx": r"\mu_{x}", "my": r"\mu_{y}", "sx": r"\sigma_{x}", "sy": r"\sigma_{y}", "r": "r"}


def _sym(name: str, value: Any) -> str:
    return _m(_SYMBOL[name] + "=" + _num_tex(value))


def _regression_from_summary(matrix):
    g = matrix["givens"]
    q = (f"已知兩變量x與y的平均數分別為 {_sym('mx', g['mx'])} 與 {_sym('my', g['my'])}，"
         f"標準差分別為 {_sym('sx', g['sx'])} 與 {_sym('sy', g['sy'])}，"
         f"且x與y的相關係數為 {_n(g['r'])}，求y對x的迴歸直線方程式。")
    return _from_parts(matrix, q, ["迴歸直線方程式"], "regression_from_summary")


def _regression_from_table(matrix):
    g = matrix["givens"]
    scene = REGRESSION_SCENES[g["scene"]]
    n = len(g["x"])
    ids = list(_PEOPLE[:n]) if scene["ids"] else None
    table = _xy_table(g["x"], g["y"], scene["xlabel"], scene["ylabel"], scene["ids"], ids)
    prompt = f"{scene['intro'].format(n=_zh(n))}\n{table}"
    from .bivariate_statistics_domain import _show as show_value

    shown_x0 = show_value(Fraction(str(g["x0"])) * scene["scale"])
    items = ["求y對x的迴歸直線方程式。", scene["predict"].format(x0=_m(shown_x0))]
    return _from_parts(matrix, (prompt, items), ["迴歸直線方程式", "估計值"], "regression_from_table")


def _regression_rounded_from_table(matrix):
    g = matrix["givens"]
    if len(g["x"]) != len(_MONTHS):
        raise ValueError("need_twelve_months")
    table = _array([_tx("月份")] + [_tx(m) for m in _MONTHS],
                   [[_tx("2022年氣溫x（℃）")] + [_num_tex(v) for v in g["x"]], [_tx("2023年氣溫y（℃）")] + [_num_tex(v) for v in g["y"]]])
    prompt = (f"玉山觀測站提供的 {_n(2022)} 年每月平均氣溫x（℃）與 {_n(2023)} 年每月平均氣溫y（℃）之對照如下表。\n{table}\n"
              f"利用電腦軟體 Excel 或計算機，求")
    line = _m("y=mx+b")
    items = [f"這兩年氣溫的相關係數。（四捨五入到小數點以下第 {_n(g['r_places'])} 位）",
             f"y對x的迴歸直線方程式 {line} 的斜率 {_m('m')}。（四捨五入到小數點以下第 {_n(g['coef_places'])} 位）",
             f"y對x的迴歸直線方程式 {line} 的 {_m('y')} 截距 {_m('b')}。（四捨五入到小數點以下第 {_n(g['coef_places'])} 位）"]
    return _from_parts(matrix, (prompt, items), ["相關係數", "斜率", "截距"], "regression_rounded_from_table")


def _regression_predict_given_line(matrix):
    g = matrix["givens"]
    table = _xy_table(g["x"], g["y"], *FOREARM_LABELS)
    ep = int(g["eq_places"])
    m_txt, b = _fixed(g["m_r"], ep), Fraction(str(g["b_r"]))
    eq = f"y={m_txt}x{'+' if b >= 0 else '-'}{_fixed(abs(b), ep)}"
    q = (f"{FOREARM_INTRO.format(n=_zh(len(g['x'])))}\n{table}\n"
         f"將以上資料輸入電腦後，得y對x的迴歸直線方程式為 {_m(eq)}。已知某位女性的前臂長度為 {_n(g['x0'])} 公分，"
         f"利用迴歸直線估計其身高。（四捨五入到整數位）")
    if int(g["places"]) != 0:
        raise ValueError("textbook_rounds_to_integer")
    return _from_parts(matrix, q, ["身高估計值"], "regression_predict_given_line")


def _correlation_from_regression_point(matrix):
    g = matrix["givens"]
    q = (f"已知兩變量x與y的平均數分別為 {_sym('mx', g['mx'])} 與 {_sym('my', g['my'])}，"
         f"標準差分別為 {_sym('sx', g['sx'])} 與 {_sym('sy', g['sy'])}，"
         f"且點 {_m(_point_tex(*g['point']))} 在y對x的迴歸直線上，求x與y的相關係數。{_NUMBER_HINT}")
    return _from_parts(matrix, q, ["相關係數"], "correlation_from_regression_point")


def _regression_line_unknown_intercept(matrix):
    g = matrix["givens"]
    slope = _coef_tex(Fraction(str(g["slope"])))
    prompt = (f"已知變量x的平均數為 {_n(g['mx'])}，標準差為 {_n(g['sx'])}；變量y的平均數為 {_n(g['my'])}，標準差為 {_n(g['sy'])}，"
              f"且y對x的迴歸直線方程式為 {_m('y=' + slope + 'x+k')}，求")
    return _from_parts(matrix, (prompt, ["實數 $k$ 的值。", f"x與y的相關係數。{_NUMBER_HINT}"]), ["k", "相關係數"],
                       "regression_line_unknown_intercept")


_PAIR_I = "$" + r"\left(x_{i},\ y_{i}\right)" + "$"
_INDEX_RANGE = r"i=1,2,\ldots,"


def _statement_lines(g: dict[str, Any]) -> list[str]:
    lines = []
    for st in g["statements"]:
        kind = st["kind"]
        if kind == "passes_point":
            lines.append(f"迴歸直線通過點 {_m(_point_tex(st['x'], st['y']))}")
        elif kind == "slope_is":
            lines.append(f"迴歸直線的斜率為 {_n(st['stated'])}")
        elif kind == "sigma_less":
            lines.append(f"{st['first']}的標準差小於{st['second']}的標準差")
        else:
            raise ValueError(f"no_statement_text:{kind}")
    return lines


def _regression_statement_selection(matrix):
    g = matrix["givens"]
    n = int(g["n"])
    intro = (f"有 {_n(n)} 筆數據 {_PAIR_I}，{_m(_INDEX_RANGE + str(n))}，"
             f"其平均數 {_sym('mx', g['mx'])}、{_sym('my', g['my'])}，"
             f"變量x與y的相關係數 {_sym('r', g['r'])}，且y對x的迴歸直線通過點 {_m(_point_tex(*g['line_point']))}。"
             f"選出正確的選項：{_MULTI_HINT}")
    q = intro + "\n" + "\n".join(f"({i}) {line}" for i, line in enumerate(_statement_lines(g), 1))
    return _from_parts(matrix, q, ["選項"], "regression_statement_selection")


def _range_text(claim: dict[str, Any]) -> str:
    def num(v: Any) -> str:
        f = Fraction(str(v))
        return ("−" if f < 0 else "") + _num_tex(abs(f))

    lo_op = "≤" if claim["lo_closed"] else "<"
    hi_op = "≤" if claim["hi_closed"] else "<"
    return f"相關係數r滿足{num(claim['lo'])} {lo_op} r {hi_op} {num(claim['hi'])}。"


def _true_false_bivariate(matrix):
    claim = matrix["givens"]["claim"]
    kind = claim["kind"]
    if kind == "points_vs_correlation":
        body = {"higher": "散布圖上的點愈多，其相關程度愈高。", "lower": "散布圖上的點愈多，其相關程度愈低。",
                "unrelated": "散布圖上點的多寡，並不能決定其相關程度的高低。"}[claim["stated"]]
    elif kind == "slope_sign":
        sym = {">": ">", "<": "<", "=": "="}
        body = (f"若x與y的相關係數 {_m('r' + sym[claim['r_rel']] + '0')}，則y對x的迴歸直線的斜率 {_m('m' + sym[claim['m_rel']] + '0')}。")
    elif kind == "slope_sigma":
        k, c = Fraction(str(claim["k"])), Fraction(str(claim["c"]))
        if k == 1 and c == 1:
            body = "若x與y的標準差相等，則其相關係數與y對x迴歸直線的斜率也相等。"
        elif k == 1:
            body = f"若x與y的標準差相等，則y對x迴歸直線的斜率為相關係數的 {_n(c)} 倍。"
        else:
            body = f"若y的標準差為x的標準差的 {_n(k)} 倍，則y對x迴歸直線的斜率為相關係數的 {_n(c)} 倍。"
    elif kind == "r_range":
        body = _range_text(claim)
    elif kind == "points_on_line":
        a, b = Fraction(str(claim["a"])), Fraction(str(claim["b"]))
        line = _m("y=" + _coef_tex(a) + "x" + ("" if b == 0 else ("+" if b > 0 else "-") + _num_tex(abs(b))))
        stated = Fraction(str(claim["stated"]))
        body = f"若散布圖的所有點都在直線 {line} 上，則相關係數為{'' if stated >= 0 else '−'}{abs(stated.numerator)}。"
    else:
        raise ValueError(f"no_claim_text:{kind}")
    return _from_parts(matrix, _TF_HEAD + body, ["判斷"], "true_false_bivariate")


_ADAPTERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "correlation_from_table": _correlation_from_table,
    "correlation_remove_point": _correlation_remove_point,
    "correlation_change_add_point": _correlation_change_add_point,
    "correlation_rescale": _correlation_rescale,
    "regression_from_summary": _regression_from_summary,
    "regression_from_table": _regression_from_table,
    "regression_rounded_from_table": _regression_rounded_from_table,
    "regression_predict_given_line": _regression_predict_given_line,
    "correlation_from_regression_point": _correlation_from_regression_point,
    "regression_line_unknown_intercept": _regression_line_unknown_intercept,
    "regression_statement_selection": _regression_statement_selection,
    "true_false_bivariate": _true_false_bivariate,
}


def adapt_bivariate_statistics_matrix(
    matrix: dict[str, Any], *, domain_operation: str, seed: int | None = None, **_: Any
) -> dict[str, Any]:
    op = str(domain_operation or matrix.get("domain_operation") or "").strip()
    if op not in _ADAPTERS:
        raise ValueError(f"no_adapter:{op}")
    return _ADAPTERS[op](matrix)
