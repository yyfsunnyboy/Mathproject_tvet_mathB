"""Question payload contracts for algebra.exponent_laws.

Every payload is graded by a shared checker registered in ``CHECKER_CAPABILITIES``; the
expected answers always come from the domain matrix, never from this adapter.
"""

from __future__ import annotations

from typing import Any, Callable

from .exponent_laws_domain import DOMAIN_KEY
from .expr_tree import to_latex

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})

_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_RADICAL = ("expression_equivalence_checker", "radical_equivalence", "numeric_or_radical")
_EXPRESSION = ("expression_equivalence_checker", "algebraic_equivalent", "expression")


# --- contracts (same shape as the other promoted adapters) ---------------------------

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


def _value_part(index: int, record: dict[str, Any]) -> dict[str, Any]:
    kind = record["kind"]
    if kind == "radical":
        return _part(index, record["canonical"], *_RADICAL)
    if kind == "expression":
        return _part(index, record["canonical"], *_EXPRESSION)
    extra: dict[str, Any] = {}
    if "." in record["canonical"]:
        extra = {"allow_decimal": True, "required_form": "decimal"}
    return _part(index, record["canonical"], *_RATIONAL, **extra)


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
        "math_core": {
            "givens": matrix["givens"],
            "target": matrix["answer"],
            "validation_facts": matrix["validation_facts"],
        },
    }


def _parts_payload(matrix, *, question, parts, display_answer, explanation_steps, shape) -> dict[str, Any]:
    return _payload(
        matrix,
        question=question,
        answer={part["key"]: part["expected_answer"] for part in parts},
        display_answer=display_answer,
        contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer",
                           answer_shape=shape, parts=parts),
        explanation_steps=explanation_steps,
    )


def _single_payload(matrix, *, question, part, display_answer, explanation_steps, shape) -> dict[str, Any]:
    extra = {k: v for k, v in part.items() if k not in (
        "key", "label", "checker", "checker_key", "equivalence_type", "answer_type", "expected_answer")}
    return _payload(
        matrix,
        question=question,
        answer=part["expected_answer"],
        display_answer=display_answer,
        contract=_contract(part["answer_type"], "short_answer", part["checker"], part["equivalence_type"],
                           answer_shape=shape, **extra),
        explanation_steps=explanation_steps,
    )


def _choice_payload(matrix, *, question, choices, answer, display_answer, explanation_steps) -> dict[str, Any]:
    return _payload(
        matrix,
        question=question,
        answer=answer,
        display_answer=display_answer,
        contract=_contract("single_choice", "single_choice", "choice_label_checker", "choice_label",
                           answer_shape="single_choice", choices=[dict(c) for c in choices]),
        explanation_steps=explanation_steps,
        choices=choices,
    )


def _numbered(texts: list[str]) -> str:
    return "\n".join(f"({i}) {text}" for i, text in enumerate(texts, start=1))


def _items_payload(matrix, *, stem: str, texts: list[str], records: list[dict[str, Any]], steps: list[str], shape: str) -> dict[str, Any]:
    display = "，".join(f"({i}) ${r['display']}$" if len(records) > 1 else f"${r['display']}$"
                      for i, r in enumerate(records, start=1))
    if len(records) == 1:
        return _single_payload(matrix, question=f"{stem}{texts[0]}", part=_value_part(1, records[0]),
                               display_answer=display, explanation_steps=steps, shape=shape)
    parts = [_value_part(i, r) for i, r in enumerate(records, start=1)]
    return _parts_payload(matrix, question=f"{stem}\n{_numbered(texts)}", parts=parts,
                          display_answer=display, explanation_steps=steps, shape=shape)


# --- payload builders ---------------------------------------------------------------

def _simplify_exponent_expressions(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    texts = [f"${to_latex(t)}$" for t in givens["items"]]
    steps = [f"({i}) 依指數律化簡，得 ${to_latex(t)}={r['display']}$。"
             for i, (t, r) in enumerate(zip(givens["items"], answer["values"]), start=1)]
    return _items_payload(matrix, stem=givens["stem"], texts=texts, records=answer["values"], steps=steps,
                          shape="exponent_expression_values")


def _blank_text(item: dict[str, Any]) -> str:
    def b(value: str) -> str:
        return to_latex(["pow", ["n", value], ["n", "1"]]).rsplit("^", 1)[0]

    kind = item["kind"]
    if kind == "product_to_base":
        left = " \\times ".join(f"{b(base)}^{{{exp}}}" for base, exp in item["factors"])
        return f"${left}={b(item['result_base'])}^{{\\square}}$"
    if kind == "power_power":
        inner = "\\square" if item.get("inner") is None else item["inner"]
        outer = "\\square" if item.get("outer") is None else item["outer"]
        return f"$\\left({b(item['base'])}^{{{inner}}}\\right)^{{{outer}}}={b(item['result_base'])}^{{{item['result_exp']}}}$"
    (b1, e1), (b2, e2) = item["factors"]
    return f"${b(b1)}^{{{e1}}} \\times {b(b2)}^{{{e2}}}=\\square^{{{item['common_exponent']}}}$"


def _solve_exponent_blank_equations(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    texts = [_blank_text(item) for item in givens["items"]]
    steps = [f"({i}) 利用指數律，方格內應填 ${r['canonical']}$。" for i, r in enumerate(answer["values"], start=1)]
    return _items_payload(matrix, stem=givens["stem"], texts=texts, records=
                          [{**r, "display": r["canonical"]} for r in answer["values"]], steps=steps,
                          shape="exponent_blank_values")


def _evaluate_conditional_exponent_values(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    condition = f"{to_latex(givens['condition']['lhs'])}={to_latex(givens['condition']['rhs'])}"
    prefix = givens.get("stem_prefix", "已知")
    targets = [to_latex(t) for t in givens["targets"]]
    if len(targets) == 1:
        question_head, texts, stem = f"{prefix}${condition}$，求 ${targets[0]}$ 的值。", [], ""
        records = answer["values"]
        steps = [f"利用指數律與已知條件，得 ${targets[0]}={records[0]['display']}$。"]
        return _single_payload(matrix, question=question_head, part=_value_part(1, records[0]),
                               display_answer=f"${records[0]['display']}$", explanation_steps=steps,
                               shape="conditional_exponent_value")
    stem = f"{prefix}${condition}$，求下列各式的值："
    texts = [f"${t}$" for t in targets]
    steps = [f"({i}) 利用指數律與已知條件，得 ${t}={r['display']}$。"
             for i, (t, r) in enumerate(zip(targets, answer["values"]), start=1)]
    return _items_payload(matrix, stem=stem, texts=texts, records=answer["values"], steps=steps,
                          shape="conditional_exponent_values")


def _evaluate_exponent_statement_truth(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    marks = ["○" if truth else "×" for truth in answer["truth_values"]]
    statements = [f"${to_latex(s['lhs'])}={to_latex(s['rhs'])}$" for s in givens["statements"]]
    definitions = givens.get("definitions") or {}
    intro = ("設 " + "、".join(f"${name}={to_latex(tree)}$" for name, tree in definitions.items()) + "，") if definitions else ""
    header = intro + "下列敘述對的打「○」，錯的打「×」。"
    steps = [f"{text} 依指數律判斷為「{mark}」。" for text, mark in zip(statements, marks)]
    if len(statements) == 1:
        return _choice_payload(matrix, question=f"{header}\n{statements[0]}", choices=TRUE_FALSE_CHOICES,
                               answer=marks[0], display_answer=marks[0], explanation_steps=steps)
    parts = [_part(i, m, "choice_label_checker", "choice_label", "single_choice",
                   choices=[dict(c) for c in TRUE_FALSE_CHOICES]) for i, m in enumerate(marks, start=1)]
    return _parts_payload(matrix, question=header + "\n" + _numbered(statements), parts=parts,
                          display_answer="　".join(f"({i}) {m}" for i, m in enumerate(marks, start=1)),
                          explanation_steps=steps, shape="statement_truth_parts")


def _evaluate_repeated_folding(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    name = givens.get("distance_name", "地球到月球")
    question = (
        f"將一張厚度為{givens['thickness_cm']}公分足夠大的紙，一直對摺。問：\n"
        f"(1) 對摺 ${givens['fold_count']}$ 次後厚度為幾公分？\n"
        f"(2) 在理想的情況下，要摺幾次它的厚度會超過{name}的距離 ${givens['distance_km']}$ 公里呢？"
    )
    records = answer["values"]
    parts = [_value_part(1, records[0]), _value_part(2, records[1])]
    steps = [
        f"(1) 厚度為 ${givens['thickness_cm']}\\times 2^{{{givens['fold_count']}}}={answer['thickness_after_cm']}$ 公分。",
        f"(2) 距離為 ${givens['distance_km']}$ 公里 $=\\,{int(givens['distance_km']) * 100000}$ 公分，"
        f"需 ${answer['min_folds']}$ 次對摺厚度才會超過。",
    ]
    return _parts_payload(matrix, question=question, parts=parts,
                          display_answer=f"(1) ${records[0]['canonical']}$　(2) ${records[1]['canonical']}$",
                          explanation_steps=steps, shape="repeated_folding_values")


def _select_nearest_model_value(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    if givens["model"] == "folding":
        question = (
            f"在理想的情況下，將一張厚度為{givens['thickness_cm']}公分足夠大的紙，一直對摺。"
            f"問：對摺 ${givens['fold_count']}$ 次後，紙張厚度最接近下列哪一個選項？"
        )
        unit = "公尺"
    elif givens["model"] == "benford":
        question = (
            "根據班佛法則，在某銀行裡，帳戶存款數最高位數字是 $a$ 的人數占所有人數的比例為 "
            "$x=\\log\\left(1+\\frac{1}{a}\\right)$。"
            f"求當 $a={givens['leading_digit']}$ 時，$x$ 的值最接近下列哪個選項？"
        )
        unit = "%"
    else:
        question = (
            "海嘯是一種有強大破壞力的海浪，其速度 $V$（公尺／秒）的公式為\n"
            "$V=\\left(10h\\right)^{\\frac{1}{2}}$，\n"
            f"其中 $h$ 為海水深度（公尺）。已知某次海嘯發生於平均水深約 ${givens['depth_m']}$ 公尺的海域，"
            "求此海嘯的速度最接近以下哪一個等級的選項？"
        )
        unit = "公尺／秒"
    choices = [{"label": str(i), "text": opt["text"], "value": opt["text"]} for i, opt in enumerate(givens["options"], start=1)]
    chosen = str(answer["choice"])
    value = f"{float(answer['value']):.4g}"
    return _choice_payload(
        matrix, question=question + "\n" + "\n".join(f"({c['label']}) {c['text']}" for c in choices),
        choices=choices, answer=chosen, display_answer=f"({chosen}) {choices[answer['choice'] - 1]['text']}",
        explanation_steps=[f"計算得約 ${value}$ {unit}，最接近選項 ({chosen})。"],
    )


def _evaluate_power_law_model(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    formula = f"$E={givens['k']}d^{{{givens['exponent']}}}$"
    head = f"設某檯燈與被照明物的距離為 $d$ 公尺時，被照明物表面的照度為 $E$ 勒克斯，且 $E$ 與 $d$ 的關係式為\n{formula}。\n"
    if givens["mode"] == "value":
        question = head + f"已知此檯燈高度為{givens['distance_m']}公尺，求放置於桌面上時，檯燈正下方的照度 $E$ 的值。"
        steps = [f"取 $d={givens['distance_m']}$，得 $E={givens['k']}\\times {givens['distance_m']}^{{{givens['exponent']}}}={answer['value']}$。"]
    else:
        question = head + (
            f"已知此檯燈原先高度為{givens['from_distance_m']}公尺，可將此檯燈調高至{givens['to_distance_m']}公尺，"
            "求調整後的照度 $E_{1}$ 是原先的照度 $E_{2}$ 之幾倍？"
        )
        steps = [f"$\\frac{{E_{{1}}}}{{E_{{2}}}}=\\left(\\frac{{{givens['to_distance_m']}}}{{{givens['from_distance_m']}}}\\right)^{{{givens['exponent']}}}={answer['value']}$。"]
    record = answer["values"][0]
    return _single_payload(matrix, question=question, part=_value_part(1, record),
                           display_answer=f"${record['canonical']}$", explanation_steps=steps, shape="power_law_value")


def _solve_metabolic_scaling(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    e = givens["exponent"]
    frac = f"\\frac{{{e.split('/')[0]}}}{{{e.split('/')[1]}}}" if "/" in e else e
    choices = [{"label": str(i), "text": f"{v}倍", "value": f"{v}倍"} for i, v in enumerate(givens["options"], start=1)]
    question = (
        "生物學家克萊柏發現多數哺乳動物的基礎代謝率 $B$（千卡/天）與其體重 $M$（公斤）會滿足關係式\n"
        f"$B=kM^{{{frac}}}$，\n"
        "其中 $k$ 為大於 $0$ 的常數。設老鼠的基礎代謝率為 $b$（千卡/天），體重為 $m$（公斤）。試回答下列問題：\n"
        f"(1) 設一隻貓的體重約為一隻老鼠的 ${givens['weight_ratio']}$ 倍，試問：貓的基礎代謝率 $B$（千卡/天）約為老鼠的幾倍？"
        "試選出最接近的選項。（單選）\n"
        + "　".join(f"({c['label']}) {c['text']}" for c in choices) + "\n"
        f"(2) 設一頭牛的基礎代謝率約為一隻老鼠的 ${givens['metabolic_ratio']}$ 倍，試問：牛的體重 $M$（公斤）約為老鼠的幾倍？"
    )
    parts = [
        _part(1, str(answer["choice"]), "choice_label_checker", "choice_label", "single_choice",
              choices=[dict(c) for c in choices]),
        _part(2, answer["mass_ratio"], *_RATIONAL),
    ]
    return _parts_payload(
        matrix, question=question, parts=parts,
        display_answer=f"(1) ({answer['choice']}) {choices[answer['choice'] - 1]['text']}　(2) ${answer['mass_ratio']}$ 倍",
        explanation_steps=[f"(1) ${givens['weight_ratio']}^{{{frac}}}\\approx {float(answer['value_1']):.4g}$，最接近選項 ({answer['choice']})。",
                           f"(2) $M$ 的倍數為 ${givens['metabolic_ratio']}^{{{_inverse(e)}}}={answer['mass_ratio']}$。"],
        shape="metabolic_scaling_parts")


def _inverse(exponent: str) -> str:
    num, den = (exponent.split("/") + ["1"])[:2]
    return f"\\frac{{{den}}}{{{num}}}"


def _solve_half_life_model(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    t = givens["half_life_hours"]
    question = (
        f"服用止痛藥經過 $h$ 小時後，殘留在身體裡的量為原來的 $y$ 倍，其中 $y$ 與 $h$ 的關係為\n"
        f"$y=\\left(\\frac{{1}}{{2}}\\right)^{{\\frac{{h}}{{{t}}}}}$。\n問：\n"
        f"(1) 當殘留的藥量為原來的 $\\frac{{1}}{{2^{{{givens['threshold_exponent']}}}}}$ 倍時，才會被認定為代謝完成，"
        "那麼服用一顆止痛藥，至少需要幾個小時才能代謝完成？\n"
        f"(2) 服用一顆止痛藥{givens['days']}天後，殘留在身體裡的量為原來的幾倍？"
    )
    records = answer["values"]
    return _parts_payload(
        matrix, question=question, parts=[_value_part(1, records[0]), _value_part(2, records[1])],
        display_answer=f"(1) ${records[0]['canonical']}$ 小時　(2) ${records[1]['canonical']}$ 倍",
        explanation_steps=[f"(1) $\\frac{{h}}{{{t}}}={givens['threshold_exponent']}$，$h={answer['hours_needed']}$。",
                           f"(2) ${givens['days']}$ 天 $={24 * int(givens['days'])}$ 小時，$y=\\left(\\frac{{1}}{{2}}\\right)^{{{answer['remaining_power']}}}={answer['remaining']}$。"],
        shape="half_life_parts")


def _evaluate_scale_energy_ratio(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    factor = 2 ** int(givens["factor_exponent"])
    question = (
        f"芮氏規模為地震大小的標度，芮氏規模每增加 $1$，釋放的能量約變為 ${factor}$ 倍。\n"
        f"(1) 已知芮氏規模 ${givens['high']}$ 所釋放的能量是芮氏規模 ${givens['low']}$ 的 $2^{{n}}$ 倍，求 $n$ 的值。\n"
        f"(2) 問：芮氏規模{givens['partial_scale']}所釋放的能量是芮氏規模 ${givens['reference']}$ 的幾倍？（四捨五入到整數位）"
    )
    records = answer["values"]
    return _parts_payload(
        matrix, question=question, parts=[_value_part(1, records[0]), _value_part(2, records[1])],
        display_answer=f"(1) $n={records[0]['canonical']}$　(2) ${records[1]['canonical']}$ 倍",
        explanation_steps=[f"(1) ${factor}^{{{int(givens['high']) - int(givens['low'])}}}=2^{{{answer['n']}}}$，故 $n={answer['n']}$。",
                           f"(2) 倍數約為 ${float(answer['exact_value']):.2f}$，四捨五入得 ${answer['rounded']}$。"],
        shape="scale_energy_parts")


def _solve_cooling_coefficient(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    ta, h0 = givens["ambient"], givens["initial"]
    place = {1: "一"}.get(int(givens["decimals"]), str(givens["decimals"]))
    question = (
        f"蛋糕從 ${h0}{{}}^\\circ\\mathrm{{C}}$ 的烤箱拿出來放在 ${ta}{{}}^\\circ\\mathrm{{C}}$ 的室溫下，"
        "經過 $t$ 分鐘後的溫度 $H{}^\\circ\\mathrm{C}$ 符合牛頓提出的冷卻定律，公式為\n"
        f"$H={ta}+\\left({h0}-{ta}\\right)a^{{-t}}$，\n"
        f"其中 $a>0$ 為蛋糕的冷卻係數。已知 ${givens['minutes']}$ 分鐘後測量蛋糕的溫度為${givens['measured']}{{}}^\\circ\\mathrm{{C}}$，"
        f"求蛋糕的冷卻係數 $a$ 的值（四捨五入到小數點以下第{place}位）。"
    )
    record = answer["values"][0]
    part = _value_part(1, record)
    part["decimal_places"] = int(givens["decimals"])
    return _single_payload(
        matrix, question=question, part=part, display_answer=f"$a\\approx {record['canonical']}$",
        explanation_steps=[f"代入得 $a^{{{givens['minutes']}}}={answer['exact_power']}$，故 $a\\approx {record['canonical']}$。"],
        shape="decimal_coefficient")


def _exponent_latex(text: str) -> str:
    text = str(text).strip()
    if "/" in text:
        num, den = text.split("/", 1)
        sign = "-" if num.startswith("-") else ""
        return f"{sign}\\frac{{{num.lstrip('-')}}}{{{den}}}"
    return text


def _express_rational_powers_as_radicals(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    conversions, solve = givens["conversions"], givens.get("solve")
    powers = [f"${item['base']}^{{{_exponent_latex(item['exponent'])}}}$" for item in conversions]
    records = answer["values"]
    parts = []
    for i, rec in enumerate(records[:len(conversions)], start=1):
        part = _part(i, rec["canonical"], *_RADICAL, required_form="radical_notation")
        if solve is not None:
            part["label"] = f"(1) 第{i}式"
        parts.append(part)
    steps = [f"${item['base']}^{{{_exponent_latex(item['exponent'])}}}={rec['display']}$。"
             for item, rec in zip(conversions, records)]
    if solve is None:
        question = "以根式表示下列各數：\n" + _numbered(powers)
        display = "，".join(f"({i}) ${r['display']}$" for i, r in enumerate(records, start=1))
    else:
        r_rec = records[len(conversions)]
        part = _part(len(conversions) + 1, r_rec["canonical"], *_RATIONAL)
        part["label"] = "(2) r"
        parts.append(part)
        rhs = to_latex(solve["rhs"])
        question = ("(1) 以根式表示 " + " 與 ".join(powers) + "。\n"
                    f"(2) 已知 $r$ 為有理數，且 ${solve['base']}^{{r}}={rhs}$，求 $r$ 的值。")
        display = "(1) " + "，".join(f"${r['display']}$" for r in records[:-1]) + f"　(2) $r={r_rec['display']}$"
        steps.append(f"因 ${solve['base']}^{{r}}={rhs}$，故 $r={r_rec['display']}$。")
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display,
                          explanation_steps=steps, shape="radical_notation_values")


def _solve_cooling_initial_temperature(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    ta, base = givens["ambient"], givens["decay_base"]
    question = (
        f"牛頓的冷卻定律提到：麵包出爐的溫度為 $h{{}}^\\circ\\mathrm{{C}}$ 時，在 ${ta}{{}}^\\circ\\mathrm{{C}}$ 的室溫下"
        "經過 $t$ 分鐘後的溫度 $H{}^\\circ\\mathrm{C}$ 會滿足關係式\n"
        f"$H={ta}+\\left(h-{ta}\\right)\\left({base}\\right)^{{-t}}$。\n"
        f"已知 ${givens['minutes']}$ 分鐘後測量麵包的溫度為 ${givens['measured']}{{}}^\\circ\\mathrm{{C}}$，"
        "求麵包出爐時的溫度（四捨五入到整數位）。"
    )
    record = answer["values"][0]
    return _single_payload(
        matrix, question=question, part=_value_part(1, record), display_answer=f"${record['canonical']}{{}}^\\circ\\mathrm{{C}}$",
        explanation_steps=[f"代入 $H={givens['measured']}$、$t={givens['minutes']}$，得 $h\\approx {float(answer['exact']):.2f}$，四捨五入為 ${record['canonical']}$。"],
        shape="integer_temperature")


def _solve_linear_unknowns_from_exponential_table(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    table = givens["table"]
    known = {k["label"]: k["distance"] for k in givens["known"]}
    labels = [row["label"] for row in givens["known"]]
    table_md = ("| 行星 | " + " | ".join(r["label"] for r in table) + " |\n| --- | " + " | ".join("---" for _ in table)
                + " |\n| n | " + " | ".join(str(r["n"]) for r in table) + " |")
    question = (
        "天文學家波德於 $1766$ 年提出有名的「波德法則」：行星與太陽的平均距離 $d$ 天文單位可用數學式子\n"
        f"$d=\\alpha+\\beta \\times {givens['base']}^{{n}}$\n"
        f"表示，其中 $n$ 值與行星的對應表如下：\n{table_md}\n"
        f"已知{labels[0]}與太陽平均距離為{known[labels[0]]}天文單位，且{labels[1]}與太陽的平均距離為{known[labels[1]]}天文單位，"
        "求 $\\alpha$ 及 $\\beta$ 的值。"
    )
    records = answer["values"]
    parts = [{**_value_part(1, records[0]), "label": "α"}, {**_value_part(2, records[1]), "label": "β"}]
    return _parts_payload(
        matrix, question=question, parts=parts,
        display_answer=f"$\\alpha={records[0]['canonical']}$，$\\beta={records[1]['canonical']}$",
        explanation_steps=["代入兩個已知行星的 $n$ 值與距離，得 $\\alpha,\\beta$ 的二元一次方程組，"
                           f"解得 $\\alpha={answer['alpha']}$、$\\beta={answer['beta']}$。"],
        shape="linear_unknown_pair")


def _sci_part(index: int, record: dict[str, Any]) -> dict[str, Any]:
    return _part(index, record["canonical"], "expression_equivalence_checker", "math_expression_equivalence", "expression",
                 required_form="scientific_notation", significant_digits=record["sig"])


def _evaluate_scientific_notation_expression(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    items, records = givens["items"], answer["values"]
    texts = []
    for item in items:
        if item.get("prompt"):
            texts.append(item["prompt"])
        elif item["kind"] == "expr" and item.get("show_expr", True):
            texts.append(f"${to_latex(item['tree'])}$")
        else:
            texts.append("")
    shown = [t for t in texts if t]
    stem = givens.get("stem", "")
    steps = [f"取 ${rec['sig']}$ 位有效數字，得 ${rec['display']}$。" for rec in records]
    display = "，".join(f"({i}) ${r['display']}$" if len(records) > 1 else f"${r['display']}$"
                      for i, r in enumerate(records, start=1))
    if len(records) == 1:
        question = stem + (shown[0] if shown else "")
        return _single_payload(matrix, question=question, part=_sci_part(1, records[0]), display_answer=display,
                               explanation_steps=steps, shape="scientific_notation_values")
    question = stem + ("\n" + _numbered(shown) if shown else "")
    return _parts_payload(matrix, question=question, parts=[_sci_part(i, r) for i, r in enumerate(records, start=1)],
                          display_answer=display, explanation_steps=steps, shape="scientific_notation_values")


_TEN_POWER_WORDS = {4: "1萬", 8: "1億", 12: "1兆"}


def _property_text(number: dict[str, Any], statement: dict[str, Any]) -> str:
    kind, claim = statement["kind"], statement["claim"]
    if kind == "is_scientific_notation":
        return "以上為科學記號表示法。"
    if kind == "digit_count":
        return f"此數為 ${claim}$ 位數。"
    if kind == "zero_count":
        return f"此數共有 ${claim}$ 個0。"
    if kind == "greater_than_power":
        return f"此數大於 {_TEN_POWER_WORDS.get(int(claim), f'$10^{{{claim}}}$')}。"
    if kind == "significant_digits":
        return f"${number['decimal']}$ 的有效位數是 ${claim}$。"
    return f"$10^{{{number['ten_power']}}}$ 的整數部分為 ${claim}$ 位數。"


def _evaluate_number_property_statements(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    number, statements = givens["number"], givens["statements"]
    marks = ["○" if t else "×" for t in answer["truth_values"]]
    texts = [_property_text(number, s) for s in statements]
    intro = f"關於 ${number['mantissa']}\\times 10^{{{number['exponent']}}}$，" if "mantissa" in number else ""
    header = intro + "下列敘述對的打「○」，錯的打「×」。"
    steps = [f"{t} 判斷為「{m}」。" for t, m in zip(texts, marks)]
    if len(texts) == 1:
        return _choice_payload(matrix, question=f"{header}\n{texts[0]}", choices=TRUE_FALSE_CHOICES, answer=marks[0],
                               display_answer=marks[0], explanation_steps=steps)
    parts = [_part(i, m, "choice_label_checker", "choice_label", "single_choice",
                   choices=[dict(c) for c in TRUE_FALSE_CHOICES]) for i, m in enumerate(marks, start=1)]
    return _parts_payload(matrix, question=header + "\n" + _numbered(texts), parts=parts,
                          display_answer="　".join(f"({i}) {m}" for i, m in enumerate(marks, start=1)),
                          explanation_steps=steps, shape="statement_truth_parts")


def _evaluate_common_logarithm_items(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    stem, items, records = givens.get("stem", ""), givens["items"], answer["values"]
    texts, parts = [], []
    for i, (item, rec) in enumerate(zip(items, records), start=1):
        if item["kind"] == "as_power_of_ten":
            texts.append(item.get("prompt") or f"利用常用對數將 ${item['value']}$ 表為「$10$ 的次方」的形式。")
            parts.append(_part(i, rec["canonical"], *_EXPRESSION))
        else:
            tex = to_latex(item["tree"])
            texts.append(item.get("prompt") or (f"${tex}$" if stem else f"求 ${tex}$ 的值。"))
            extra = {"allow_decimal": True, "required_form": "decimal"} if "." in rec["canonical"] else {}
            parts.append(_part(i, rec["canonical"], *_RATIONAL, **extra))
    steps = [f"({i}) 答案為 ${r['display']}$。" for i, r in enumerate(records, start=1)]
    display = "，".join(f"({i}) ${r['display']}$" for i, r in enumerate(records, start=1))
    question = (stem + "\n" if stem else "") + (_numbered(texts) if len(texts) > 1 else texts[0])
    if len(parts) == 1:
        return _single_payload(matrix, question=question, part=parts[0], display_answer=display,
                               explanation_steps=steps, shape="common_logarithm_values")
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps,
                          shape="common_logarithm_values")


def _approximate_common_logarithm(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    record = answer["values"][0]
    part = {**_value_part(1, record), "decimal_places": int(givens["decimals"])}
    return _single_payload(
        matrix, question=f"求 $\\log {givens['value']}$ 的值（四捨五入到小數點以下第 ${givens['decimals']}$ 位）。",
        part=part, display_answer=f"$\\log {givens['value']}\\approx {record['canonical']}$",
        explanation_steps=[f"$\\log {givens['value']}\\approx {float(answer['exact']):.6f}$，四捨五入得 ${record['canonical']}$。"],
        shape="decimal_logarithm")


def _count_digits_of_integer_power(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    offset = int(givens.get("offset", 0))
    number = f"{givens['base']}^{{{givens['exponent']}}}" + (f"{offset:+d}" if offset else "")
    if givens.get("style") == "lucas":
        question = f"盧卡斯證明了 ${number}$ 為質數，問：此質數是幾位數？"
    else:
        question = f"已知 ${number}$ 是質數，求此質數的位數。"
    record = answer["values"][0]
    return _single_payload(
        matrix, question=question, part=_value_part(1, record), display_answer=f"${record['canonical']}$ 位數",
        explanation_steps=[f"${number}$ 的常用對數約為 ${float(mp_log10_text(givens))}$，整數部分加 $1$ 即為位數 ${record['canonical']}$。"],
        shape="digit_count")


def mp_log10_text(givens: dict[str, Any]) -> str:
    import mpmath as mp

    value = mp.power(int(givens["base"]), int(givens["exponent"])) + int(givens.get("offset", 0))
    return mp.nstr(mp.log10(value), 12)


def _solve_power_of_ten_exponent(matrix: dict[str, Any]) -> dict[str, Any]:
    givens, answer = matrix["givens"], matrix["answer"]
    decimals = int(givens.get("decimals", 0))
    place = "整數位" if decimals == 0 else f"小數點後第{ {1: '一', 2: '二', 3: '三'}.get(decimals, decimals) }位"
    if givens.get("tower_n") is not None:
        n = int(givens["tower_n"])
        question = (
            "2019年谷歌的量子AI實驗室負責人尼文提出了未來的量子電腦會依循著「尼文定律」：經過 $1,2,3,\\ldots,n$ 個週期後，"
            "其運算速度會變成原來的 $2^{2^{1}}=2^{2}$、$2^{2^{2}}=2^{4}$、$2^{2^{3}}=2^{8}$, …, $2^{2^{n}}$ 倍。"
            f"設某台量子電腦經過 ${n}$ 個週期後，其運算速度變為原來的 $b$ 倍，且 $b=10^{{k}}$，求 $k$ 的值。（四捨五入到{place}）"
        )
    else:
        question = f"設 ${givens['base']}^{{{givens['exponent']}}}=10^{{k}}$，求 $k$ 的值。（四捨五入到{place}）"
    record = answer["values"][0]
    part = _value_part(1, record)
    part["decimal_places"] = decimals
    return _single_payload(
        matrix, question=question, part=part, display_answer=f"$k\\approx {record['canonical']}$",
        explanation_steps=[f"$k={answer['exponent_used']}\\log {givens['base']}\\approx {float(answer['exact']):.4f}$，四捨五入得 ${record['canonical']}$。"],
        shape="decimal_exponent")


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "evaluate_scientific_notation_expression": _evaluate_scientific_notation_expression,
    "evaluate_number_property_statements": _evaluate_number_property_statements,
    "evaluate_common_logarithm_items": _evaluate_common_logarithm_items,
    "approximate_common_logarithm": _approximate_common_logarithm,
    "count_digits_of_integer_power": _count_digits_of_integer_power,
    "solve_power_of_ten_exponent": _solve_power_of_ten_exponent,
    "express_rational_powers_as_radicals": _express_rational_powers_as_radicals,
    "solve_cooling_initial_temperature": _solve_cooling_initial_temperature,
    "solve_linear_unknowns_from_exponential_table": _solve_linear_unknowns_from_exponential_table,
    "simplify_exponent_expressions": _simplify_exponent_expressions,
    "solve_exponent_blank_equations": _solve_exponent_blank_equations,
    "evaluate_conditional_exponent_values": _evaluate_conditional_exponent_values,
    "evaluate_exponent_statement_truth": _evaluate_exponent_statement_truth,
    "evaluate_repeated_folding": _evaluate_repeated_folding,
    "select_nearest_model_value": _select_nearest_model_value,
    "evaluate_power_law_model": _evaluate_power_law_model,
    "solve_metabolic_scaling": _solve_metabolic_scaling,
    "solve_half_life_model": _solve_half_life_model,
    "evaluate_scale_energy_ratio": _evaluate_scale_energy_ratio,
    "solve_cooling_coefficient": _solve_cooling_coefficient,
}


def adapt_exponent_laws_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_exponent_laws_operation:{operation}")
    return builder(matrix)
