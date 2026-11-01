"""Question payload contracts for discrete.mathematical_expectation (普高數學2 Unit 7 數學期望值).

Every expected answer comes from the domain matrix. Stems are rebuilt from the stated data only.
No question points at a figure or a separate table. Format hints are not given an example that copies the answer.
"""

from __future__ import annotations

from typing import Any, Callable

from core.gencode.multipart_stem_contract import build_stem_structure, stem_structure_to_question_text

from .mathematical_expectation_domain import DOMAIN_KEY, FAIR, PARTY, SITES, TRUE_FALSE, YES_NO

_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_WIN_TEXT = {"prime": "為質數", "even": "為偶數", "odd": "為奇數", "high": "大於 $3$"}


def _contract(answer_type: str, presentation_mode: str, checker: str, equivalence: str, **extra: Any) -> dict[str, Any]:
    return {
        "presentation_mode": presentation_mode, "answer_type": answer_type, "checker": checker, "checker_key": checker,
        "answer_equivalence": equivalence, "equivalence": equivalence, "equivalence_type": equivalence, **extra,
    }


def _part(index: int, expected: Any, checker: str, equivalence: str, answer_type: str, **extra: Any) -> dict[str, Any]:
    row = {
        "key": f"part_{index}", "label": f"({index})", "group_label": f"({index})", "answer_order": index - 1,
        "checker": checker, "checker_key": checker,
        "equivalence_type": equivalence, "answer_type": answer_type, "expected_answer": expected, **extra,
    }
    row["display_label"] = row["label"]
    if row["label"] != row["group_label"]:
        row["label"] = f"{row['group_label']} {row['label']}"  # grading feedback names parts by label only
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
    if not stem or len(stem["items"]) != len(parts):
        raise ValueError("multipart_stem_items_must_match_parts")
    return _payload(
        matrix, question=question, answer={p["key"]: p["expected_answer"] for p in parts}, display_answer=display_answer,
        contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer", answer_shape=shape, parts=parts),
        explanation_steps=explanation_steps, stem=stem,
    )


def _t(s: str) -> str:
    """Inline math. ``@`` stands for a backslash so the source stays valid on Python 3.11."""
    return "$" + s.replace("@", "\\") + "$"


def _n(v: Any) -> str:
    return _t(str(v))


def _frac(text: Any) -> str:
    raw = str(text)
    if "/" not in raw:
        return _t(raw)
    num, den = raw.split("/", 1)
    return _t(f"@frac{{{num}}}{{{den}}}")


def _money(v: int) -> str:
    if v >= 10000 and v % 10000 == 0:
        return f"{_n(v // 10000)} 萬元"
    return f"{_n(v)} 元"


def _value_part(index: int, value: Any, label: str) -> dict[str, Any]:
    return _part(index, str(value), *_RATIONAL, label=label, prompt=label)


def _choice_part(index: int, expected_label: str, choices, label: str) -> dict[str, Any]:
    return _part(index, expected_label, "choice_label_checker", "choice_label", "single_choice",
                 choices=[dict(c) for c in choices], input_type="select", label=label, prompt=label)


def _show(part: dict[str, Any]) -> str:
    if part["kind"] == "choice":
        return next(c["value"] for c in part["choices"] if c["label"] == part["label"])
    return str(part["value"])


def _from_parts(matrix, question: str | tuple[str, list[str]], builders: list[tuple[str, Callable[[int, dict], dict]]],
                shape: str) -> dict[str, Any]:
    """``question`` is either a plain stem or ``(prompt, items)``; items become ``stem_structure`` with (1)(2)... labels."""
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
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps, shape=shape,
                          stem=stem)


def _rational_builder(label: str) -> tuple[str, Callable]:
    return label, lambda i, item: _value_part(i, item["value"], label)


def _choice_builder(label: str, choices=None) -> tuple[str, Callable]:
    def build(i, item, label=label, choices=choices):
        return _choice_part(i, item["label"], choices if choices is not None else item["choices"], label)

    return label, build


def _faces_text(faces: list[int]) -> str:
    shown = [_n(f) for f in faces]
    if len(shown) == 1:
        return shown[0]
    return "、".join(shown[:-1]) + " 或 " + shown[-1]


def _gain_text(v: int) -> str:
    if v > 0:
        return f"可得 {_n(v)} 元"
    if v < 0:
        return f"須付出 {_n(-v)} 元"
    return "沒有獎金"


def _die_payout(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    if g["style"] == "linear":
        c = g["coef"]
        question = (f"擲一粒公正的骰子一次。已知擲出 {_t('k')} 點（{_t('k = 1, 2, 3, 4, 5, 6')}）可得獎金 {_t(f'{c}k')} 元，"
                    "求所得獎金的期望值。")
    else:
        order: list[int] = []
        for v in g["payouts"]:
            if v not in order:
                order.append(v)
        clauses = [f"擲出 {_faces_text([i + 1 for i, p in enumerate(g['payouts']) if p == v])} 點{_gain_text(v)}" for v in order]
        question = f"擲一粒公正骰子。已知{'；'.join(clauses)}，求擲骰子一次所得金額的期望值。"
    return _from_parts(matrix, question, [_rational_builder("期望值")], "die_payout_expectation")


def _coin_clause(k: int, v: int) -> str:
    when = "全無正面時" if k == 0 else f"出現 {_n(k)} 個正面時"
    if v > 0:
        return f"{when}可得 {_n(v)} 元"
    if v < 0:
        return f"{when}須付給莊家 {_n(-v)} 元"
    return f"{when}沒有所得"


def _coin_payout(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    n, scenarios = g["n"], g["scenarios"]
    first = scenarios[0]
    order = list(range(1, n + 1)) + [0]
    intro = f"在丟硬幣的遊戲中，玩家同時丟 {_n(n)} 枚均勻硬幣。" + "；".join(_coin_clause(k, first[k]) for k in order) + "。"
    if len(scenarios) == 1:
        return _from_parts(matrix, intro + "求丟一次所得金額的期望值為多少？", [_rational_builder("期望值")], "coin_payout_expectation")
    second = scenarios[1]
    changed = "；".join(_coin_clause(k, second[k]) for k in order if second[k] != first[k])
    items = ["玩家玩這個遊戲一次的所得金額期望值是多少？", f"若將遊戲規則更改為：{changed}，其餘不變，則玩家玩一次的所得金額期望值是多少？"]
    return _from_parts(matrix, (intro, items), [_rational_builder("期望值"), _rational_builder("期望值")], "coin_payout_expectation")


def _urn(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    groups, k, var, scene = g["groups"], g["draw"], g["variable"], g.get("scene")
    counts = [grp["count"] for grp in groups]
    names = [grp.get("name") or "" for grp in groups]
    if scene == "cards":
        listed = "、".join(f"{_n(grp['value'])} 元商品卡 {_n(grp['count'])} 張" for grp in groups)
        question = f"袋中裝有相同大小的{listed}。從袋中任取 {_n(k)} 張商品卡，求所得金額的期望值。"
    elif scene == "eggs":
        question = (f"盤中裝有 {_n(sum(counts))} 顆滷蛋，它們是由 {_n(counts[0])} 顆{names[0]}及 {_n(counts[1])} 顆{names[1]}所做成。"
                    f"從盤中任取 {_n(k)} 顆滷蛋，求取出由{names[var['index']]}所做成滷蛋的個數之期望值。")
    elif scene == "balls":
        question = (f"袋中有大小相同的{names[0]} {_n(counts[0])} 顆及{names[1]} {_n(counts[1])} 顆。"
                    f"從袋中任取 {_n(k)} 顆球，求取出{names[var['index']]}個數的期望值。")
    elif scene == "tangyuan":
        question = (f"鍋中有{names[0]} {_n(counts[0])} 顆及{names[1]} {_n(counts[1])} 顆，且這兩種湯圓的外部特徵完全相同。"
                    f"從鍋中任意舀取 {_n(k)} 顆湯圓，求舀取到{names[var['index']]}個數的期望值。")
    elif scene == "color_prize":
        if k != 2 or var["kind"] != "payout_by_count" or len(var["payouts"]) != 1 or var["payouts"][0][0] != 1 or var["default"] != 0:
            raise ValueError("color_prize_shape")
        prize = var["payouts"][0][1]
        question = (f"箱中有大小相同的{names[0]} {_n(counts[0])} 顆與{names[1]} {_n(counts[1])} 顆。從箱中同時取出 {_n(2)} 顆球，"
                    f"當取出的 {_n(2)} 球顏色不同時，可得獎金 {_n(prize)} 元；當 {_n(2)} 球顏色相同時，無獎金。求獎金的期望值。")
    elif scene == "melon":
        a = counts[0]
        pays = dict((c, v) for c, v in var["payouts"])
        if counts[1] != a or k != a or var["index"] != 0 or set(pays) != {a, a - 1}:
            raise ValueError("melon_shape")
        question = (f"水果店老闆對一名新聘人員施以一項測驗來決定他的月薪。老闆準備外形相近的{names[0]}與{names[1]}各 {_n(a)} 顆，"
                    f"要求此人從中選出 {_n(a)} 顆{names[0]}。若 {_n(a)} 顆都選對，則月薪 {_n(pays[a])} 元；"
                    f"若選對 {_n(a - 1)} 顆，則月薪 {_n(pays[a - 1])} 元；否則月薪 {_n(var['default'])} 元。"
                    "已知此人對這兩種哈密瓜沒有鑑別能力，完全靠運氣選取，求此人月薪的期望值。")
    else:
        raise ValueError("bad_urn_scene")
    return _from_parts(matrix, question, [_rational_builder("期望值")], "urn_draw_expectation")


def _two_dice(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    m, a = g["multiplier"], g["amount"]
    prompt = (f"甲、乙兩人相約玩遊戲，兩人各擲公正骰子一次，規則如下：當兩人點數相同時，甲須付給乙該點數 {_n(m)} 倍的金額；"
              f"當兩人點數不同時，乙須付給甲 {_n(a)} 元。回答以下問題。")
    items = [
        "玩此遊戲一次，乙所得金額的期望值為多少元？",
        "這個遊戲對誰有利？",
        f"將「點數不同時乙須付給甲 {_n(a)} 元」中的金額改為多少元時，此遊戲對雙方都公平？",
    ]
    builders = [_rational_builder("期望值"), _choice_builder("對誰有利", PARTY), _rational_builder("金額")]
    return _from_parts(matrix, (prompt, items), builders, "two_dice_match_game")


def _single_die(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    prompt = (f"甲、乙兩人相約玩遊戲，由乙擲一粒公正骰子一次，規則如下：當乙擲出的點數{_WIN_TEXT[g['win_set']]}時，"
              f"甲須付給乙該點數 {_n(g['multiplier'])} 倍的金額；當出現其他點數時，乙須付給甲該點數的金額。回答以下問題。")
    items = ["玩此遊戲一次，求乙所得金額的期望值。", f"若玩此遊戲之前乙要先付給甲 {_n(g['fee'])} 元現金，則這個遊戲公平嗎？"]
    return _from_parts(matrix, (prompt, items), [_rational_builder("期望值"), _choice_builder("是否公平", FAIR)], "single_die_game")


def _insurance(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    if g["prob_kind"] == "survive":
        age = g.get("age", 50)
        body = (f"根據統計資料得知，一位 {_n(age)} 歲的人在一年內存活的機率為 {_n(g['stated_prob'])}。"
                f"保險公司針對 {_n(age)} 歲的人推出以下一年期的人壽保險：「投保人若在投保後一年內死亡，"
                f"則可獲理賠金 {_money(g['payout'])}；否則不予理賠。」")
    else:
        body = (f"根據資料顯示，住宅房屋發生火災的機率為 {_n(g['stated_prob'])}。保險公司推出「投保一年期火險，"
                f"在投保期間房屋發生火災，保戶可獲理賠金 {_money(g['payout'])}。」的住宅房屋火險。")
    if g["ask"] == "profit":
        ask = f"已知此一年期保險的保費為 {_n(g['premium'])} 元，求保險公司對於每份保單的利潤期望值。"
        label = "利潤期望值"
    else:
        ask = f"已知保險公司每份保單獲利的期望值為 {_n(g['profit'])} 元，求保戶當年度須繳交的保費金額。"
        label = "保費"
    return _from_parts(matrix, body + ask, [_rational_builder(label)], "insurance_expectation")


def _decision_table(states: list[str], probs: list[str], profits: list[list[int]]) -> str:
    cols = "|c" * (len(states) + 1) + "|"
    rows = [["@text{經濟狀況}"] + [f"@text{{{s}}}" for s in states], ["@text{機率}"] + [str(p) for p in probs],
            ["@text{甲地利潤}"] + [str(v) for v in profits[0]], ["@text{乙地利潤}"] + [str(v) for v in profits[1]]]
    body = " ".join(" & ".join(row) + " @@ @hline" for row in rows)
    return _t(f"@begin{{array}}{{{cols}}}@hline {body} @end{{array}}")


def _decision(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    states = [str(s) for s in g["states"]]
    question = (f"公司想從甲、乙兩地擇一處建設新廠。根據未來一年經濟狀況（{'、'.join(states)}）發生的機率，"
                "公司分別預估在甲、乙兩地建廠的利潤（百萬／年）如下：\n"
                f"{_decision_table(states, g['probs'], g['profits'])}\n"
                "若以一年利潤期望值的大小為判斷準則，則公司應選擇在何地建廠較佳？")
    return _from_parts(matrix, question, [_choice_builder("建廠地點", SITES)], "decision_by_expectation")


def _claim(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    n, stated = g["n"], g["stated"]
    if g["model"] == "coin":
        times = "一次" if n == 1 else f"{_n(n)} 次"
        body = f"丟一枚均勻的硬幣{times}，出現正面次數的期望值為 {_frac(stated)} 次。"
    elif n == 1:
        body = f"擲一粒公正骰子一次，出現點數的期望值為 {_frac(stated)} 點。"
    else:
        body = f"同時擲 {_n(n)} 粒公正骰子一次，出現點數和的期望值為 {_frac(stated)} 點。"
    question = "下列敘述對的打「○」，錯的打「×」。\n" + body
    return _from_parts(matrix, question, [_choice_builder("對或錯", TRUE_FALSE)], "expectation_claim")


def _guess(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    m, k, s = g["options"], g["known"], g["scores"]
    # option numbers stay inside math so the practice page does not read them as sub-question markers
    labels = [_t(f"@left( {i} @right)") for i in range(1, k + 1)]
    known = labels[0] if k == 1 else "、".join(labels[:-1]) + " 與 " + labels[-1]
    question = (
        f"學科能力測驗中，多重選擇題每題有 {_n(m)} 個選項，其中至少有一個選項是正確的。其計分方式為：「所有選項均答對者，得 {_n(s[0])} 分；"
        f"答錯 {_n(1)} 個選項者，得 {_n(s[1])} 分；答錯 {_n(2)} 個選項者，得 {_n(s[2])} 分；"
        f"答錯多於 {_n(2)} 個選項或所有選項均未做答者，該題以零分計算。」"
        f"今有一題某考生已經確定選項 {known} 是正確的，其餘 {_n(m - k)} 個選項則隨意猜測，求此考生在該題得分的期望值。"
    )
    return _from_parts(matrix, question, [_rational_builder("期望值")], "multiple_choice_guess_expectation")


def _lottery(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    total = g["total"]
    issued = f"{_n(total // 10000)} 萬張" if total % 10000 == 0 else f"{_n(total)} 張"
    listed = "；".join(f"{_money(a)}獎 {_n(c)} 張" for a, c in g["prizes"])
    question = f"某城市為了籌措經費發行彩券，共發行 {issued}，其中{listed}。請問當你購買一張彩券時，你預期會得到獎金多少元？"
    return _from_parts(matrix, question, [_rational_builder("期望值")], "lottery_expectation")


def _prize(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    vals = g["values"]
    prompt = (f"公司舉辦摸彩活動，摸彩箱中放置 {_n(len(vals))} 個分別標有數字 {'、'.join(_n(v) for v in vals)} 的球，"
              "摸獎者從箱中隨機取出一球（取後放回），即可獲得與球上數字等額的獎金。回答以下問題。")
    items = [
        "摸獎一次所得獎金的期望值為何？（單選）",
        f"輪到最後一位摸獎者時，主持人將每一獎額的球再各放一顆到摸彩箱中（此時箱中共有 {_n(2 * len(vals))} 顆球），"
        "並將規則改為：從箱中取出二球，獎金為取出二球中所標的最大數字之金額；宣稱這樣的改變可以增加該位摸獎者所得獎金的期望值。"
        "你認為主持人這樣的宣稱正確嗎？",
        "在新規則下，摸獎者所得獎金的期望值比原規則增加多少元？",
    ]
    builders = [_choice_builder("期望值"), _choice_builder("宣稱是否正確", YES_NO), _rational_builder("增加金額")]
    return _from_parts(matrix, (prompt, items), builders, "prize_ball_expectation")


_ADAPT: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "die_payout_expectation": _die_payout,
    "coin_payout_expectation": _coin_payout,
    "urn_draw_expectation": _urn,
    "two_dice_match_game": _two_dice,
    "single_die_game": _single_die,
    "insurance_expectation": _insurance,
    "decision_by_expectation": _decision,
    "expectation_claim": _claim,
    "multiple_choice_guess_expectation": _guess,
    "lottery_expectation": _lottery,
    "prize_ball_expectation": _prize,
}


def adapt_mathematical_expectation_matrix(matrix: dict[str, Any], *, domain_operation: str, seed: int | None = None,
                                          **_: Any) -> dict[str, Any]:
    if matrix.get("domain") != DOMAIN_KEY or matrix.get("domain_operation") != domain_operation:
        raise ValueError("matrix_operation_mismatch")
    return _ADAPT[domain_operation](matrix)
