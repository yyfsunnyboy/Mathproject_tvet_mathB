"""Question payload contracts for statistics.univariate_descriptive (普高數學2 Unit 8)."""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Any, Callable

from core.gencode.multipart_stem_contract import build_stem_structure, stem_structure_to_question_text

from .univariate_statistics_domain import DOMAIN_KEY, SUBJECTS, TRUE_FALSE

_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_SET = ("solution_set_checker", "unordered_solution_set", "solution_set")
_EXPR = ("expression_checker", "algebraic_equivalent", "expression")
_TF_HEAD = "下列敘述對的打「○」，錯的打「×」。\n"
_ZH_MONTH = "一二三四五六七八九十十一十二"


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


def _t(s: str) -> str:
    return "$" + s.replace("@", "\\") + "$"


def _n(v: Any) -> str:
    return _t(str(v))


def _pct(v: Any) -> str:
    from fractions import Fraction
    f = Fraction(str(v))
    return f"{_show_pct(f)}%"


def _show_pct(f) -> str:
    from fractions import Fraction
    f = Fraction(f) * 100
    if f.denominator == 1:
        return str(f.numerator)
    text = f"{float(f):.4f}".rstrip("0").rstrip(".")
    return text


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
    """A rational in LaTeX: integer, terminating decimal, or \\frac (never a bare a/b)."""
    text = str(v).strip()
    f = Fraction(text)
    if f.denominator == 1:
        return str(f.numerator) if "." not in text else text
    if _terminating(f):
        return text if "." in text else format(Decimal(f.numerator) / Decimal(f.denominator), "f")
    sign = "-" if f < 0 else ""
    return rf"{sign}\frac{{{abs(f.numerator)}}}{{{f.denominator}}}"


def _coef_tex(a: Fraction) -> str:
    if a.denominator == 1:
        return {1: "", -1: "-"}.get(a.numerator, str(a.numerator))
    sign = "-" if a < 0 else ""
    return rf"{sign}\frac{{{abs(a.numerator)}}}{{{a.denominator}}}"


def _linear_tex(var: str, a: Any, b: Any) -> str:
    fa, fb = Fraction(str(a)), Fraction(str(b))
    text = _coef_tex(fa) + var
    if fb > 0:
        text += "+" + _num_tex(fb)
    elif fb < 0:
        text += "-" + _num_tex(-fb)
    return text


def _pct_cell(w: Any) -> str:
    return _show_pct(Fraction(str(w))) + r"\%"


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


def _value_part(index: int, item: dict, label: str) -> dict[str, Any]:
    if item["kind"] == "radical":
        return _part(index, item["value"], *_EXPR, label=label, prompt=label)
    return _part(index, str(item["value"]), *_RATIONAL, label=label, prompt=label)


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
    return str(item["value"])


def _from_parts(matrix, question: str | tuple[str, list[str]], builders: list[tuple[str, Callable]], shape: str) -> dict[str, Any]:
    raw = matrix["answer"]["parts"]
    if len(raw) != len(builders):
        raise ValueError("part_count")
    stem = None
    if isinstance(question, tuple) and len(question[1]) == 1:
        question = f"{question[0]}\n{question[1][0]}"
    elif isinstance(question, tuple):
        prompt, items = question
        stem = build_stem_structure(prompt, [{"group_label": f"({i})", "text": text} for i, text in enumerate(items, 1)])
        question = stem_structure_to_question_text(stem)
    parts = [build(i, item) for i, ((label, build), item) in enumerate(zip(builders, raw), 1)]
    if len(raw) == 1:
        display, steps = _show(raw[0]), [raw[0]["work"]]
    else:
        display = "；".join(f"({i}){_show(item)}" for i, item in enumerate(raw, 1))
        steps = [f"({i}) {item['work']}" for i, item in enumerate(raw, 1)]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps, shape=shape, stem=stem)


def _builder_for(item_kind_hint: str | None = None):
    def build(i, item, label="答案"):
        if item["kind"] == "choice":
            return _choice_part(i, item, label)
        if item["kind"] == "selected":
            return _selected_part(i, item, label)
        return _value_part(i, item, label)

    return "答案", build


def _list_text(values) -> str:
    return ", ".join(_n(v) for v in values)


def _arithmetic_mean(matrix):
    g = matrix["givens"]
    q = f"已知一組數據為\n{_list_text(g['values'])}，\n求其算術平均數。"
    return _from_parts(matrix, q, [("算術平均數", lambda i, item: _value_part(i, item, "算術平均數"))], "arithmetic_mean")


_TERM_HEADERS = ("平常成績", "第一次期中考", "第二次期中考", "期末考")
_TERM_INTRO = "本學期數學科的平常成績、第一次期中考、第二次期中考與期末考的分數與其所占的比重如下表。"


def _term_table(values: list[str], weights: list[Any]) -> str:
    if len(values) != len(_TERM_HEADERS) or len(weights) != len(_TERM_HEADERS):
        raise ValueError("term_table_needs_four_items")
    return _array([""] + [_tx(h) for h in _TERM_HEADERS],
                  [[_tx("分數")] + values, [_tx("比重")] + [_pct_cell(w) for w in weights]])


def _weighted_mean(matrix):
    g = matrix["givens"]
    if g.get("scene") == "insurance":
        premium, payout = g["premium"], g["payout"]
        if [Fraction(str(v)) for v in g["values"]] != [Fraction(premium - payout), Fraction(premium)]:
            raise ValueError("insurance_values_mismatch")
        if sum(Fraction(str(w)) for w in g["weights"]) != 1:
            raise ValueError("insurance_probabilities")
        table = _array([_tx("顧客狀況"), _tx("被隔離"), _tx("不被隔離")],
                       [[_tx("機率")] + [_num_tex(w) for w in g["weights"]]])
        q = (f"財務上常以各事件發生的機率作為權數來求平均利潤。某保險公司推出一年期的防疫險保單：投保人年繳保費 {_n(premium)} 元，"
             f"在符合保單的規定下，若於一年內因疫情被隔離即能獲得理賠 {_n(payout)} 元。該公司推估投保人被隔離與否的機率如下表。\n"
             f"{table}\n試以機率為權數，計算該公司推估平均每份保單的利潤。")
    else:
        table = _term_table([_num_tex(v) for v in g["values"]], g["weights"])
        q = f"甲生{_TERM_INTRO}\n{table}\n試以比重為權數，計算甲生的數學科學期成績。"
    return _from_parts(matrix, q, [("成績", lambda i, item: _value_part(i, item, "成績"))], "weighted_mean")


def _weighted_mean_unknown(matrix):
    g = matrix["givens"]
    if [i for i, v in enumerate(g["values"]) if v == "x"] != [int(g["unknown_index"])]:
        raise ValueError("unknown_cell_mismatch")
    table = _term_table([("x" if v == "x" else _num_tex(v)) for v in g["values"]], g["weights"])
    q = f"某生{_TERM_INTRO}\n{table}\n已知該生的數學科學期成績為 {_m(_num_tex(g['known_mean']))} 分，求 {_m('x')} 的值。"
    return _from_parts(matrix, q, [("x", lambda i, item: _value_part(i, item, "x"))], "weighted_mean_unknown")


def _geometric_growth_mean(matrix):
    g = matrix["givens"]
    rates = "、".join(_pct(r) for r in g["rates"])
    q = (f"已知連續 {_n(len(g['rates']))} 年的年成長率依序為 {rates}，求這段期間的平均成長率"
         f"（以小數表示，四捨五入至小數點後第 {_n(g['decimals'])} 位）。")
    return _from_parts(matrix, q, [("平均成長率", lambda i, item: _value_part(i, item, "平均成長率"))], "geometric_growth_mean")


def _geometric_growth_unknown(matrix):
    g = matrix["givens"]
    shown = []
    for i, r in enumerate(g["rates"]):
        shown.append("未知" if i == g["unknown_index"] else _pct(r))
    q = (f"連續三年的平均漲幅為 {_pct(g['known_mean'])}。已知前兩年漲跌幅分別為 {shown[0]}、{shown[1]}，"
         f"求第三年的漲跌幅（以小數表示）。")
    return _from_parts(matrix, q, [("漲跌幅", lambda i, item: _value_part(i, item, "漲跌幅"))], "geometric_growth_unknown")


def _median_lists(matrix):
    g = matrix["givens"]
    items = [f"數據 {_list_text(row)}" for row in g["lists"]]
    return _from_parts(matrix, ("求下列各數據的中位數。", items),
                       [("中位數", lambda i, item: _value_part(i, item, "中位數")) for _ in g["lists"]], "median_lists")


def _median_consecutive(matrix):
    g = matrix["givens"]
    items = [f"連續整數數據 {_t('1, 2, @ldots, ' + str(n))} 的中位數" for n in g["ends"]]
    return _from_parts(matrix, ("求下列中位數。", items),
                       [("中位數", lambda i, item: _value_part(i, item, "中位數")) for _ in g["ends"]], "median_consecutive")


_FREQ_SCENES = {
    "shots": ("某校有 {N} 位學生，每位各投籃 {shots} 次，他們的進球數如下表。", "進球數（次）", "人數（人）",
              "求這 {N} 筆進球數數據的下列各百分位數。"),
    "breaths": ("{N} 位成人在休息狀態時每分鐘的呼吸次數分配如下表。", "呼吸次數", "人數",
                "求這 {N} 筆呼吸次數數據的下列各百分位數。"),
    "salary": ("某公司 {N} 位員工的薪資分配如下表。", "薪資（千元）", "員工數（人）",
               "對於這 {N} 個數據，分別求這組數據的四分位數。"),
}


def _frequency_stem(g: dict[str, Any]) -> tuple[str, str]:
    intro, value_label, count_label, ask = _FREQ_SCENES[g["scene"]]
    values, counts = list(g["values"]), list(g["counts"])
    if g["scene"] == "shots" and [int(v) for v in values] != list(range(len(values))):
        raise ValueError("shots_must_run_from_zero")
    fill = {"N": _n(sum(int(c) for c in counts)), "shots": _n(values[-1])}
    table = _array([_tx(value_label)] + [_num_tex(v) for v in values], [[_tx(count_label)] + [str(int(c)) for c in counts]])
    return f"{intro.format(**fill)}\n{table}\n{ask.format(**fill)}", ask


def _percentile_frequency(matrix):
    g = matrix["givens"]
    stem, _ask = _frequency_stem(g)
    items = [f"第 {_n(p)} 百分位數 {_m('P_{' + str(p) + '}')}" for p in g["percentiles"]]
    return _from_parts(matrix, (stem, items),
                       [("百分位數", lambda i, item: _value_part(i, item, "百分位數")) for _ in g["percentiles"]],
                       "percentile_frequency")


def _quartile_frequency(matrix):
    g = matrix["givens"]
    stem, _ask = _frequency_stem(g)
    items = [_m("Q_1"), _m("Q_2"), _m("Q_3")]
    return _from_parts(matrix, (stem, items),
                       [("四分位數", lambda i, item: _value_part(i, item, "四分位數")) for _ in range(3)],
                       "quartile_frequency")


def _list_summary_stats(matrix):
    g = matrix["givens"]
    labels = {"mean": "算術平均數", "median": "中位數", "q3": "第3四分位數", "q1": "第1四分位數"}
    items = [labels[s] for s in g["stats"]]
    return _from_parts(matrix, (f"已知數據 {_list_text(g['values'])}，求下列統計量。", items),
                       [(lab, lambda i, item, lab=lab: _value_part(i, item, lab)) for lab in items],
                       "list_summary_stats")


def _mean_variance_sd(matrix):
    g = matrix["givens"]
    items = ["算術平均數", "變異數", "標準差"]
    return _from_parts(matrix, (f"求以下數據的算術平均數、變異數和標準差。\n{_list_text(g['values'])}", items),
                       [(lab, lambda i, item, lab=lab: _value_part(i, item, lab)) for lab in items],
                       "mean_variance_sd")


def _standard_deviation(matrix):
    g = matrix["givens"]
    if len(g["lists"]) == 1:
        q = f"求以下數據的標準差。\n{_list_text(g['lists'][0])}"
        return _from_parts(matrix, q, [("標準差", lambda i, item: _value_part(i, item, "標準差"))], "standard_deviation")
    items = [f"數據 {_list_text(row)}" for row in g["lists"]]
    return _from_parts(matrix, ("求下列各數據的標準差。", items),
                       [("標準差", lambda i, item: _value_part(i, item, "標準差")) for _ in g["lists"]],
                       "standard_deviation")


def _compare_standard_deviation(matrix):
    g = matrix["givens"]
    lines = "\n".join(f"({i}) {_list_text(row)}" for i, row in enumerate(g["lists"], 1))
    q = f"下列各組數據，何者的標準差最大？\n{lines}"
    return _from_parts(matrix, q, [("選項", lambda i, item: _choice_part(i, item, "選項"))], "compare_standard_deviation")


def _unknown_given_sd(matrix):
    g = matrix["givens"]
    seq = ", ".join([*map(str, g["prefix"]), "x", *map(str, g["suffix"])])
    q = f"已知由小到大排列的數據：{_t(seq)}，它們的標準差為 {_n(g['sd'])}，求 {_t('x')} 的值。"
    return _from_parts(matrix, q, [("x", lambda i, item: _value_part(i, item, "x"))], "unknown_given_sd")


def _linear_mean_sd(matrix):
    g = matrix["givens"]
    q = (f"一組數據的平均數為 {_n(g['mean'])}，標準差為 {_n(g['sd'])}。"
         f"若每個數據經 {_m('y=' + _linear_tex('x', g['a'], g['b']))} 變換，求新的平均數與標準差。")
    return _from_parts(matrix, (q, ["平均數", "標準差"]),
                       [("平均數", lambda i, item: _value_part(i, item, "平均數")),
                        ("標準差", lambda i, item: _value_part(i, item, "標準差"))],
                       "linear_mean_sd")


def _linear_find_scale_sd(matrix):
    g = matrix["givens"]
    q = (f"全班平均 {_n(g['old_mean'])} 分、標準差 {_n(g['old_sd'])} 分、最高分 {_n(g['old_max'])} 分。"
         f"經 {_t('y=ax+b')} 後最高分變為 {_m(_num_tex(g['new_max']))}、平均變為 {_m(_num_tex(g['new_mean']))}，求新標準差。")
    return _from_parts(matrix, q, [("標準差", lambda i, item: _value_part(i, item, "標準差"))], "linear_find_scale_sd")


def _standardize_scores(matrix):
    g = matrix["givens"]
    s1, s2 = g["subjects"]
    table = _array(["", _tx(s1), _tx(s2)],
                   [[_tx("平均數")] + [_num_tex(v) for v in g["means"]],
                    [_tx("標準差")] + [_num_tex(v) for v in g["sds"]]])
    builders = [
        ("標準化", lambda i, item: _value_part(i, item, "標準化")),
        ("標準化", lambda i, item: _value_part(i, item, "標準化")),
        ("科目", lambda i, item: _choice_part(i, item, "科目")),
    ]
    q0 = (f"某班段考的{s1}與{s2}成績之平均數與標準差如下表。\n{table}\n"
          f"已知班上甲生此次段考{s1}成績為 {_n(g['scores'][0])} 分，{s2}成績為 {_n(g['scores'][1])} 分。")
    items = [f"將甲生的{s1}成績標準化", f"將甲生的{s2}成績標準化", "相對於全班，甲生在這兩科中哪一科表現比較好？"]
    return _from_parts(matrix, (q0, items), builders, "standardize_scores")


_MONTHS = ("一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二")


def _monthly_mean_sd(matrix):
    g = matrix["givens"]
    if len(g["values"]) != len(_MONTHS):
        raise ValueError("need_twelve_months")
    table = _array([_tx("月份")] + [_tx(m) for m in _MONTHS],
                   [[_tx("氣溫（°C）")] + [_num_tex(v) for v in g["values"]]])
    q = (f"某觀測站某年每月平均氣溫（°C）如下表。\n{table}\n"
         f"利用計算機或電腦軟體，求該年氣溫的平均數與標準差（四捨五入到小數點以下第 {_n(g['places'])} 位）。")
    return _from_parts(matrix, (q, ["平均數", "標準差"]),
                       [("平均數", lambda i, item: _value_part(i, item, "平均數")),
                        ("標準差", lambda i, item: _value_part(i, item, "標準差"))],
                       "monthly_mean_sd")


def _true_false_stat(matrix):
    claim = matrix["givens"]["claim"]
    kind = claim["kind"]
    if kind == "adding_value_raises_mean_by":
        lead = (f"已知 {_n(claim['n'])} 個數據的算術平均數為 {_m(_num_tex(claim['mean']))}，"
                if "mean" in claim else f"在 {_n(claim['n'])} 個數據中")
        body = f"{lead}加入一個新的數據 {_n(claim['added'])} 後，所得的算術平均數會增加 {_n(claim['delta'])}。"
    elif kind == "equal_values_sd_zero":
        body = "若所有數據的值都相等，則其標準差為0。"
    elif kind == "constant_data_sd":
        data = ", ".join([_num_tex(claim["value"])] * int(claim["n"]))
        body = f"數據 {_m(data)} 的標準差為 {_m(_num_tex(claim['stated']))}。"
    elif kind == "scaled_sd_signed":
        relation = _m("y_{i}=" + _linear_tex("x_{i}", claim["a"], claim.get("b", 0)))
        sd_claim = _m(r"\sigma_{y}=" + _coef_tex(Fraction(str(claim["stated_factor"]))) + r"\sigma_{x}")
        body = f"若數據 {_m('x_{i}')} 與數據 {_m('y_{i}')} 的關係式為 {relation}，則 {sd_claim}。"
    elif kind == "median_ge_mean_always":
        body = "一組數據的中位數一定大於或等於它的平均數。"
    elif kind == "median_ge_mean_data":
        body = f"數據 {_list_text(claim['values'])} 的中位數大於或等於它的平均數。"
    else:
        raise ValueError(f"no_claim_text:{kind}")
    q = _TF_HEAD + body
    return _from_parts(matrix, q, [("判斷", lambda i, item: _choice_part(i, item, "判斷"))], "true_false_stat")


_MULTI_HINT = "（多選題，請以逗號分隔選項編號作答）"


def _quartile_statements(sc: dict[str, Any], statements: list[dict]) -> tuple[str, list[str]]:
    n, mean, q1, q3 = sc["n"], sc["mean"], sc["q1"], sc["q3"]
    hours = "每週研讀數學的時數"
    intro = (f"調查某班 {_n(n)} 名學生{hours}，統計結果得算術平均數為 {_m(_num_tex(mean))} 小時，"
             f"第 {_n(1)} 四分位數為 {_m(_num_tex(q1))} 小時，第 {_n(3)} 四分位數為 {_m(_num_tex(q3))} 小時。"
             f"下列何者可由上列結果推斷為正確？{_MULTI_HINT}")
    lines = []
    for st in statements:
        kind = st["kind"]
        if kind == "median_between_quartiles":
            le = _m(r"\le")
            lines.append(f"{_m(_num_tex(q1))} 小時 {le} 中位數 {le} {_m(_num_tex(q3))} 小時")
        elif kind == "median_is_quartile_midpoint":
            lines.append(f"中位數為 {_m(_num_tex((Fraction(str(q1)) + Fraction(str(q3))) / 2))} 小時")
        elif kind == "count_above_q3":
            word = {"about": "約有", "at_most": "至多有"}[st["mode"]]
            lines.append(f"{word} {_n(st['count'])} 名學生{hours}超過 {_m(_num_tex(q3))} 小時")
        elif kind == "count_ge_q1":
            relation = "大於" if st.get("strict") else "大於或等於"
            lines.append(f"至少有 {_n(st['count'])} 名學生{hours}{relation} {_m(_num_tex(q1))} 小時")
        elif kind == "total_exceeds":
            lines.append(f"全班學生每週研讀數學的總時數超過 {_n(st['threshold'])} 小時")
        else:
            raise ValueError(f"no_statement_text:{kind}")
    return intro, lines


def _rescale_statements(sc: dict[str, Any], statements: list[dict]) -> tuple[str, list[str]]:
    formula = r"\(" + r"\text{調整分數}=\frac{\text{原分數}}{" + str(sc["div"]) + "}+" + _num_tex(sc["shift"]) + r"\)"
    intro = (f"某次段考後，老師將全班的成績依下列公式調整：\n{formula}。\n"
             f"已知每個人調整後的分數都不低於原分數，且調整後全班的平均為 {_n(sc['mu_y'])} 分，標準差 {_n(sc['sd_y'])} 分，"
             f"有 {_n(sc['k'])} 位同學仍低於 {_n(sc['low_y'])} 分。選出正確的選項。{_MULTI_HINT}")
    text = {
        "orig_mean_below": "學生原分數的平均低於 {s} 分",
        "orig_sd_is": "學生原分數的標準差為 {s} 分",
        "k_orig_below": "有 {k} 位同學的原分數低於 {s} 分",
        "nobody_orig_over": "沒有人的原分數超過 {s} 分",
    }
    lines = [text[st["kind"]].format(s=_n(st["stated"]), k=_n(sc["k"])) for st in statements]
    return intro, lines


def _percentile_statements(sc: dict[str, Any], statements: list[dict]) -> tuple[str, list[str]]:
    p = _n(sc["p"])
    new_p = f"新資料的第 {p} 百分位數"
    lines = []
    for st in statements:
        kind = st["kind"]
        if kind == "pct_scale":
            c = _n(st["c"])
            lines.append(f"若將原資料每個數據分別乘以 {c}，則原資料的第 {p} 百分位數乘以 {c} 也會是{new_p}")
        elif kind == "pct_shift":
            d = Fraction(str(st["d"]))
            verb = "加" if d > 0 else "減"
            amount = _n(abs(d))
            lines.append(f"若將原資料每個數據分別{verb} {amount}，則原資料的第 {p} 百分位數{verb} {amount} 也會是{new_p}")
        elif kind == "pct_square":
            lines.append(f"若將原資料每個數據分別平方，則原資料的第 {p} 百分位數的平方也會是{new_p}")
        elif kind == "pct_merge_sum":
            lines.append(f"若有 A, B 兩組資料且其第 {p} 百分位數分別為 {_m('x_{A}')}、{_m('x_{B}')}，"
                         f"則 {_m('x_{A}+x_{B}')} 也是此兩組資料合併成一組後的第 {p} 百分位數")
        elif kind == "pct_lt_mean":
            lines.append(f"任一組資料的第 {p} 百分位數必小於該組資料的算術平均數")
        elif kind == "pct_within_range":
            lines.append(f"任一組資料的第 {p} 百分位數必介於該組資料的最小值與最大值之間（含端點）")
        else:
            raise ValueError(f"no_statement_text:{kind}")
    return f"關於百分位數的敘述，選出所有正確的選項。{_MULTI_HINT}", lines


def _statement_selection(matrix):
    g = matrix["givens"]
    sc = g["scenario"]
    if {"q1", "q3"} <= set(sc):
        intro, lines = _quartile_statements(sc, g["statements"])
    elif "div" in sc:
        intro, lines = _rescale_statements(sc, g["statements"])
    elif "p" in sc:
        intro, lines = _percentile_statements(sc, g["statements"])
    else:
        raise ValueError("unknown_statement_scenario")
    q = intro + "\n" + "\n".join(f"({i}) {line}" for i, line in enumerate(lines, 1))
    return _from_parts(matrix, q, [("選項", lambda i, item: _selected_part(i, item, "選項"))], "statement_selection")


_DATASET_TEXT = {"gsat_109": f" {_n(109)} 學年度學測", "simulated": "某次學測模擬測驗"}
_MARK_NAME = {"88": "頂標", "75": "前標"}
_CIRCLED = "①②③④"
_ZH_DIGIT = "零一二三四五六七八九十"


def _zh_number(n: int) -> str:
    if n <= 10:
        return _ZH_DIGIT[n]
    return ("十" if n < 20 else _ZH_DIGIT[n // 10] + "十") + (_ZH_DIGIT[n % 10] if n % 10 else "")


def _grade_claim_text(claim: dict[str, Any]) -> str:
    subject = {"cn": "國文科", "math": "數學科"}
    kind = claim["kind"]
    if kind == "mode":
        return f"{subject[claim['subject']]}得 {_n(claim['grade'])} 級分的人數是該科中最多"
    if kind == "share_below":
        return f"兩科 {_n(claim['grade'])} 級分的人數比例都小於百分之{_zh_number(int(claim['threshold']))}"
    if kind == "upper_half":
        return f"{subject[claim['subject']]}得 {_n(claim['grade'])} 級分以上（含）的人數超過該科人數的一半"
    if kind == "sd_less":
        return f"{subject[claim['first']]}的標準差小於{subject[claim['second']]}的標準差"
    raise ValueError(f"no_claim_text:{kind}")


def _grade_distribution_read(matrix):
    from .univariate_statistics_chart import render_grade_charts

    g = matrix["givens"]
    intro = f"以下為{_DATASET_TEXT[g['dataset']]}國文科與數學科級分的人數百分比分布圖。"
    builders, items = [], []
    for ask in g["asks"]:
        if ask == "multi_select_basic":
            lines = [f"{_CIRCLED[i]}{_grade_claim_text(c)}" for i, c in enumerate(g["claims"])]
            items.append(f"下列敘述何者正確？{_MULTI_HINT}\n" + "\n".join(lines))
            builders.append(("選項", lambda i, item: _selected_part(i, item, "選項")))
        else:
            p = ask.rsplit("_", 1)[1]
            items.append(f"成績位於第 {_n(p)} 百分位數的考生級分稱為{_MARK_NAME[p]}，試問哪一科的{_MARK_NAME[p]}比較高？")
            builders.append(("科目", lambda i, item: _choice_part(i, item, "科目")))
    out = _from_parts(matrix, (intro, items), builders, "grade_distribution_read")
    shown = ["".join(_CIRCLED[i - 1] for i in item["selected"]) if item["kind"] == "selected" else _show(item)
             for item in matrix["answer"]["parts"]]
    out["display_answer"] = shown[0] if len(shown) == 1 else "；".join(f"({i}){s}" for i, s in enumerate(shown, 1))
    charts = render_grade_charts({"國文科": [Fraction(str(v)) for v in g["cn_pct"]],
                                  "數學科": [Fraction(str(v)) for v in g["math_pct"]]})
    out["visual_aids"] = [{"type": "image/png", "value": c["png_base64"], "label": c["title"]} for c in charts]
    out["visual_backed"] = True
    out["visual_asset_type"] = "grade_percentage_bar_chart_png"
    out["chart_data"] = {"kind": "grade_percentage_bar_chart", "dataset": g["dataset"],
                         "panels": [{k: v for k, v in c.items() if k != "png_base64"} for c in charts]}
    return out


_ADAPTERS = {
    "arithmetic_mean": _arithmetic_mean,
    "weighted_mean": _weighted_mean,
    "weighted_mean_unknown": _weighted_mean_unknown,
    "geometric_growth_mean": _geometric_growth_mean,
    "geometric_growth_unknown": _geometric_growth_unknown,
    "median_lists": _median_lists,
    "median_consecutive": _median_consecutive,
    "percentile_frequency": _percentile_frequency,
    "quartile_frequency": _quartile_frequency,
    "list_summary_stats": _list_summary_stats,
    "mean_variance_sd": _mean_variance_sd,
    "standard_deviation": _standard_deviation,
    "compare_standard_deviation": _compare_standard_deviation,
    "unknown_given_sd": _unknown_given_sd,
    "linear_mean_sd": _linear_mean_sd,
    "linear_find_scale_sd": _linear_find_scale_sd,
    "standardize_scores": _standardize_scores,
    "monthly_mean_sd": _monthly_mean_sd,
    "true_false_stat": _true_false_stat,
    "statement_selection": _statement_selection,
    "grade_distribution_read": _grade_distribution_read,
}


def adapt_univariate_statistics_matrix(
    matrix: dict[str, Any], *, domain_operation: str, seed: int | None = None, **_: Any
) -> dict[str, Any]:
    op = str(domain_operation or matrix.get("domain_operation") or "").strip()
    if op not in _ADAPTERS:
        raise ValueError(f"no_adapter:{op}")
    return _ADAPTERS[op](matrix)
