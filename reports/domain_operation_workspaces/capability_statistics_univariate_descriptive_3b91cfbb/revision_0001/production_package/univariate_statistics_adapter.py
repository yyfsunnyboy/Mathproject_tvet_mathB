"""Question payload contracts for statistics.univariate_descriptive (普高數學2 Unit 8)."""

from __future__ import annotations

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


def _array(headers: list[str], rows: list[list[str]]) -> str:
    cols = len(headers)
    spec = "|".join(["c"] * cols)
    lines = [" & ".join(_t(r"@text{" + h + "}") if not h.startswith("$") else h for h in headers)]
    for row in rows:
        lines.append(" & ".join(row))
    body = r" @hline ".join(lines)
    return _t(rf"@begin{{array}}{{|{spec}|}}@hline {body} @hline @end{{array}}")


def _list_text(values) -> str:
    return ", ".join(_n(v) for v in values)


def _arithmetic_mean(matrix):
    g = matrix["givens"]
    q = f"已知一組數據為\n{_list_text(g['values'])}，\n求其算術平均數。"
    return _from_parts(matrix, q, [("算術平均數", lambda i, item: _value_part(i, item, "算術平均數"))], "arithmetic_mean")


def _weighted_mean(matrix):
    g = matrix["givens"]
    if g.get("scene") == "insurance":
        premium, payout = g["premium"], g["payout"]
        p = g["weights"][0]
        table = _array(["顧客狀況", "被隔離", "不被隔離"], [["機率", _n(p), _n(g["weights"][1])]])
        q = (f"某保險公司推出一年期保單：投保人年繳保費 {_n(premium)} 元，若被隔離可獲理賠 {_n(payout)} 元。"
             f"隔離與否的機率如下。\n{table}\n試以機率為權數，計算平均每份保單的利潤。")
    else:
        headers = ["", "項目一", "項目二", "項目三", "項目四"]
        scores = ["分數"] + [_n(v) for v in g["values"]]
        weights = ["比重"] + [(_pct(w) if Fraction_ok(w) else _n(w)) for w in g["weights"]]
        # show weights as percent when they look like decimals summing to 1
        table = _array(["", "一", "二", "三", "四"], [scores, ["比重"] + [_weight_cell(w) for w in g["weights"]]])
        q = f"某生成績與比重如下。\n{table}\n試以比重為權數，計算學期成績。"
    return _from_parts(matrix, q, [("成績", lambda i, item: _value_part(i, item, "成績"))], "weighted_mean")


def Fraction_ok(w):
    try:
        from fractions import Fraction
        Fraction(str(w))
        return True
    except Exception:
        return False


def _weight_cell(w) -> str:
    from fractions import Fraction
    f = Fraction(str(w))
    if f.denominator in (1, 2, 4, 5, 10, 20, 25, 50, 100) and 0 < f <= 1:
        return _t(str(int(f * 100)) + r"@%") if (f * 100).denominator == 1 else _n(w)
    return _n(w)


def _weighted_mean_unknown(matrix):
    g = matrix["givens"]
    vals = [(_n(v) if v != "x" else _t("x")) for v in g["values"]]
    table = _array(["", "一", "二", "三", "四"], [["分數"] + vals, ["比重"] + [_weight_cell(w) for w in g["weights"]]])
    q = f"某生成績與比重如下。\n{table}\n已知學期成績為 {_n(g['known_mean'])} 分，求 {_t('x')} 的值。"
    return _from_parts(matrix, q, [("x", lambda i, item: _value_part(i, item, "x"))], "weighted_mean_unknown")


def _geometric_growth_mean(matrix):
    g = matrix["givens"]
    rates = "、".join(_pct(r) for r in g["rates"])
    q = f"已知連續 { _n(len(g['rates'])) } 年的年成長率依序為 {rates}，求這段期間的平均成長率（以小數表示）。"
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


def _percentile_frequency(matrix):
    g = matrix["givens"]
    headers = ["數值"] + [_n(v) for v in g["values"]]
    row = ["次數"] + [_n(c) for c in g["counts"]]
    # rebuild as 2-row table with first column labels — use values as header
    table = _array(["數值"] + [str(v) for v in g["values"]], [["次數"] + [_n(c) for c in g["counts"]]])
    items = [f"第 {_n(p)} 百分位數 {_t('P_{' + str(p) + '}')}" for p in g["percentiles"]]
    return _from_parts(matrix, (f"次數分配如下。\n{table}\n求下列百分位數。", items),
                       [("百分位數", lambda i, item: _value_part(i, item, "百分位數")) for _ in g["percentiles"]],
                       "percentile_frequency")


def _quartile_frequency(matrix):
    g = matrix["givens"]
    table = _array(["數值"] + [str(v) for v in g["values"]], [["次數"] + [_n(c) for c in g["counts"]]])
    items = [_t("Q_1"), _t("Q_2"), _t("Q_3")]
    return _from_parts(matrix, (f"次數分配如下。\n{table}\n求四分位數。", items),
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
         f"若每個數據經 {_t('y=' + str(g['a']) + 'x+' + str(g['b']))} 變換，求新的平均數與標準差。")
    return _from_parts(matrix, (q, ["平均數", "標準差"]),
                       [("平均數", lambda i, item: _value_part(i, item, "平均數")),
                        ("標準差", lambda i, item: _value_part(i, item, "標準差"))],
                       "linear_mean_sd")


def _linear_find_scale_sd(matrix):
    g = matrix["givens"]
    q = (f"全班平均 {_n(g['old_mean'])} 分、標準差 {_n(g['old_sd'])} 分、最高分 {_n(g['old_max'])} 分。"
         f"經 {_t('y=ax+b')} 後最高分變為 {_n(g['new_max'])}、平均變為 {_n(g['new_mean'])}，求新標準差。")
    return _from_parts(matrix, q, [("標準差", lambda i, item: _value_part(i, item, "標準差"))], "linear_find_scale_sd")


def _standardize_scores(matrix):
    g = matrix["givens"]
    table = _array(["", "第一科", "第二科"],
                   [["平均數", _n(g["means"][0]), _n(g["means"][1])],
                    ["標準差", _n(g["sds"][0]), _n(g["sds"][1])]])
    items = [f"將分數 {_n(g['scores'][0])} 與 {_n(g['scores'][1])} 標準化", "哪一科相對表現較好？"]
    # three parts: z1, z2, choice — rebuild builders to match
    raw = matrix["answer"]["parts"]
    builders = [
        ("標準化", lambda i, item: _value_part(i, item, "標準化")),
        ("標準化", lambda i, item: _value_part(i, item, "標準化")),
        ("科目", lambda i, item: _choice_part(i, item, "科目")),
    ]
    q0 = f"兩科平均數與標準差如下。\n{table}\n已知分數為 {_n(g['scores'][0])} 與 {_n(g['scores'][1])}。"
    return _from_parts(matrix, (q0, ["第一科標準化分數", "第二科標準化分數", "相對表現較佳的科目"]), builders, "standardize_scores")


def _monthly_mean_sd(matrix):
    g = matrix["givens"]
    months = list("一二三四五六七八九十") + ["十一", "十二"]
    table = _array(["月份"] + months[: len(g["values"])],
                   [["數值"] + [_n(v) for v in g["values"]]])
    q = f"下列為十二筆數據。\n{table}\n求平均數與標準差（四捨五入到小數點以下第 {_n(g.get('places', 1))} 位）。"
    return _from_parts(matrix, (q, ["平均數", "標準差"]),
                       [("平均數", lambda i, item: _value_part(i, item, "平均數")),
                        ("標準差", lambda i, item: _value_part(i, item, "標準差"))],
                       "monthly_mean_sd")


def _true_false_stat(matrix):
    claim = matrix["givens"]["claim"]
    kind = claim["kind"]
    if kind == "adding_value_raises_mean_by":
        body = f"在十個數據中加入一個新的數據 {_n(claim['added'])} 後，所得的算術平均數會增加 {_n(claim['delta'])}。"
    elif kind == "equal_values_sd_zero":
        body = "若所有數據的值都相等，則其標準差為0。"
    elif kind == "scaled_sd_signed":
        body = (f"若數據 {_t('y_i=' + str(claim['a']) + 'x_i+b')}，則 "
                f"{_t(r'@sigma_y=' + str(claim['stated_factor']) + r'@sigma_x')}。")
    elif kind == "median_ge_mean_always":
        body = "一組數據的中位數一定大於或等於它的平均數。"
    else:
        body = str(kind)
    q = _TF_HEAD + body
    return _from_parts(matrix, q, [("判斷", lambda i, item: _choice_part(i, item, "判斷"))], "true_false_stat")


_STATEMENT_TEXT = {
    "q1_le_median_le_q3": "第1四分位數 ≤ 中位數 ≤ 第3四分位數",
    "about_n_over_q3": "約有四分之一的數據超過第3四分位數",
    "at_least_three_quarters_ge_q1": "至少有四分之三的數據大於或等於第1四分位數",
    "total_exceeds": "全班總和超過給定門檻",
    "percentile_scales_by_factor": "每個數據乘以正常數後，百分位數也乘以同一常數",
    "percentile_shifts_by_constant": "每個數據加常數後，百分位數也加同一常數",
    "percentile_of_merge_is_sum": "兩組資料百分位數之和等於合併後的百分位數",
    "percentile_lt_mean_always": "百分位數必小於算術平均數",
    "original_mean_below": "原平均低於給定門檻",
    "original_sd_is": "原標準差為所述值",
    "five_below_maps": "低於調整門檻者對應所述原分數門檻",
    "nobody_over": "沒有人的原分數超過由 y≥x 推出的上界",
}


def _statement_selection(matrix):
    g = matrix["givens"]
    lines = []
    for i, st in enumerate(g["statements"], 1):
        lines.append(f"({i}) {_STATEMENT_TEXT.get(st['kind'], st['kind'])}")
    q = "選出所有正確的選項。（多選題，請以逗號分隔選項編號作答）\n" + "\n".join(lines)
    return _from_parts(matrix, q, [("選項", lambda i, item: _selected_part(i, item, "選項"))], "statement_selection")


def _grade_distribution_read(matrix):
    g = matrix["givens"]
    # present as two percentage rows (data table; no rendered figure required)
    grades = [str(i) for i in range(16)]
    table = _array(["級分"] + grades,
                   [["國文%"] + [_n(v) for v in g["cn_pct"]],
                    ["數學%"] + [_n(v) for v in g["math_pct"]]])
    asks = g["asks"]
    builders = []
    items = []
    for ask in asks:
        if ask == "multi_select_basic":
            items.append("下列敘述何者正確？（多選，以逗號分隔編號）①數學15級分最多 ②兩科0級分比例都<5% ③國文≥12級分超過一半 ④國文標準差較小")
            builders.append(("選項", lambda i, item: _selected_part(i, item, "選項")))
        elif ask.startswith("higher_mark_"):
            p = ask.split("_")[-1]
            items.append(f"第 {_n(p)} 百分位數級分（頂標/前標）哪一科較高？")
            builders.append(("科目", lambda i, item: _choice_part(i, item, "科目")))
    return _from_parts(matrix, (f"下列為國文與數學級分人數百分比。\n{table}", items), builders, "grade_distribution_read")


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
