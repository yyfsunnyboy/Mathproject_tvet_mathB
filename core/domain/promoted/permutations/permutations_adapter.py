"""Question payload contracts for discrete.permutations (普高數學2 Unit 4 排列).

Every expected answer comes from the domain matrix, never from this adapter.  Stems are rebuilt from the same stated data the domain solved,
so a varied question always carries its own numbers.  Figures: the textbook picture is the reviewed crop reused by the practice route
(``reuse_textbook_image``).  A figure is attached only when the stated data *is* the figure's structure (the two 棋盤街道 grids with their C, D
points, the three balloon strings); any other data is described in words and carries no figure cue, so a figure can never disagree with the answer.
"""

from __future__ import annotations

import math
from typing import Any, Callable

from .permutations_domain import DOMAIN_KEY, _lattice

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_ZH = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九", 10: "十", 11: "十一", 12: "十二"}

# the textbook figures: structure the stated data must equal for the reviewed crop to be attached (read from the figure pixels / dots)
FIGURE_GRIDS = {
    "example7": {"width": 7, "height": 3, "C": (2, 1), "D": (4, 2)},
    "practice7": {"width": 6, "height": 4, "C": (3, 1), "D": (4, 2)},
}
FIGURE_BALLOONS = {"counts": (2, 3, 3), "colors": ("紅", "黃", "藍")}


def _contract(answer_type: str, presentation_mode: str, checker: str, equivalence: str, **extra: Any) -> dict[str, Any]:
    return {
        "presentation_mode": presentation_mode, "answer_type": answer_type, "checker": checker, "checker_key": checker,
        "answer_equivalence": equivalence, "equivalence": equivalence, "equivalence_type": equivalence, **extra,
    }


def _part(index: int, expected: Any, checker: str, equivalence: str, answer_type: str, **extra: Any) -> dict[str, Any]:
    return {"key": f"part_{index}", "label": f"({index})", "checker": checker, "checker_key": checker, "equivalence_type": equivalence,
            "answer_type": answer_type, "expected_answer": expected, **extra}


def _payload(matrix, *, question, answer, display_answer, contract, explanation_steps, choices=()) -> dict[str, Any]:
    operation = matrix["domain_operation"]
    return {
        "question_text": question, "question": question, "answer": answer, "correct_answer": answer, "display_answer": display_answer,
        "semantic_answer": matrix["answer"], "answer_type": contract["answer_type"], "presentation_mode": contract["presentation_mode"],
        "problem_type_id": operation, "domain_operation": operation, "fixed_domain_key": DOMAIN_KEY,
        "answer_contract": {**contract, "semantic_answer": matrix["answer"]}, "explanation_steps": explanation_steps,
        "choices": [dict(c) for c in choices], "options": [dict(c) for c in choices],
        "math_core": {"givens": matrix["givens"], "target": matrix["answer"], "validation_facts": matrix["validation_facts"]},
    }


def _single_payload(matrix, *, question, part, display_answer, explanation_steps, shape) -> dict[str, Any]:
    skip = ("key", "label", "checker", "checker_key", "equivalence_type", "answer_type", "expected_answer", "prompt")
    extra = {k: v for k, v in part.items() if k not in skip}
    if part["answer_type"] == "single_choice":
        return _payload(matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
                        contract=_contract("single_choice", "single_choice", "choice_label_checker", "choice_label",
                                           answer_shape="single_choice", choices=[dict(c) for c in part["choices"]]),
                        explanation_steps=explanation_steps, choices=part["choices"])
    return _payload(matrix, question=question, answer=part["expected_answer"], display_answer=display_answer,
                    contract=_contract(part["answer_type"], "short_answer", part["checker"], part["equivalence_type"], answer_shape=shape, **extra),
                    explanation_steps=explanation_steps)


def _parts_payload(matrix, *, question, parts, display_answer, explanation_steps, shape, figure: bool = False) -> dict[str, Any]:
    if len(parts) == 1:
        payload = _single_payload(matrix, question=question, part=parts[0], display_answer=display_answer, explanation_steps=explanation_steps, shape=shape)
    else:
        payload = _payload(matrix, question=question, answer={p["key"]: p["expected_answer"] for p in parts}, display_answer=display_answer,
                           contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer", answer_shape=shape, parts=parts),
                           explanation_steps=explanation_steps)
    if figure:
        payload["reuse_textbook_image"] = True  # the reviewed crop of the textbook figure, attached by the practice route
    return payload


def _t(s: str) -> str:
    """Inline math.  ``@`` stands for a backslash in short literals (no backslash may sit inside an f-string expression on Python 3.11)."""
    return "$" + s.replace("@", "\\") + "$"


def _n(v: Any) -> str:
    return _t(str(v))


def _zh(n: int) -> str:
    return _ZH[int(n)]


def _value_part(index: int, value: Any, label: str) -> dict[str, Any]:
    return _part(index, str(value), *_RATIONAL, label=label, prompt=label)


def _choice_part(index: int, expected_label: str, choices) -> dict[str, Any]:
    return _part(index, expected_label, "choice_label_checker", "choice_label", "single_choice", choices=[dict(c) for c in choices])


def _numbered(lines: list[str]) -> str:
    return "\n".join(f"({i}){line}" for i, line in enumerate(lines, 1))


def _fact(n: int) -> str:
    return "×".join(str(i) for i in range(int(n), 0, -1)) if n > 1 else "1"


def _falling_expr(n: int, k: int) -> str:
    return "×".join(str(n - i) for i in range(k))


def _p(n: int, k: int) -> str:
    return _t(f"P_{{{k}}}^{{{n}}}")


def _frac(counts: list[int]) -> str:
    return f"{sum(counts)}!/(" + "".join(f"{c}!" for c in counts) + ")"


def _items_payload(matrix, question, labels, a, steps, shape, figure: bool = False) -> dict[str, Any]:
    parts = [_value_part(i, it["count"], label) for i, (it, label) in enumerate(zip(a["items"], labels), 1)]
    display = "；".join(f"({i}){it['count']}" for i, it in enumerate(a["items"], 1)) if len(parts) > 1 else str(a["items"][0]["count"])
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps, shape=shape, figure=figure)


def _single_value(matrix, question, count, label, steps, shape, figure: bool = False) -> dict[str, Any]:
    return _parts_payload(matrix, question=question, parts=[_value_part(1, count, label)], display_answer=str(count), explanation_steps=steps, shape=shape, figure=figure)


# --- 1. selected_arrangement ----------------------------------------------------------------------------------------------------------------

def _selected_arrangement(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    n, k, style = a["n"], a["k"], g.get("style", "songs")
    full = ("lottery_singing", "lottery_election")
    if (style in full) != (k == n):
        raise ValueError("style_needs_full_or_partial_arrangement")
    if style == "lottery_singing":
        question = f"學校獨唱比賽共有 {_n(n)} 位同學報名參加，出場順序由抽籤決定。共有多少種可能的抽籤結果？"
    elif style == "lottery_election":
        question = f"縣長選舉共有 {_n(n)} 人登記參選，參選號次由抽籤決定。共有多少種可能的抽籤結果？"
    elif style == "songs":
        question = f"某歌手想從 {_n(n)} 首歌中，選出 {_n(k)} 首在簽唱會中依序表演，其安排的方案共有多少種？"
    elif style == "sites":
        question = f"學校想從 {_n(n)} 個參觀地點中，選出 {_n(k)} 個依序參訪，其安排的方案共有多少種？"
    elif style == "colors":
        word = str(g["word"])
        if len(word) != k:
            raise ValueError("word_length_differs_from_k")
        if word == "IMO":
            lead = "「IMO」是國際數學奧林匹克的縮寫。"
            question = lead + f"現有 {_n(n)} 種不同的顏色可供選擇，將這 {_n(k)} 個字母分別用不同顏色來寫（一字一色），共有多少種選擇？"
        else:
            question = f"現有 {_n(n)} 種不同的顏色可供選擇，將「{word}」這 {_n(k)} 個字母分別用不同顏色來寫（一字一色），共有多少種選擇？"
    else:
        raise ValueError(f"unsupported_style:{style}")
    if k == n:
        steps = [f"抽籤的結果可視作將 {n} 個人排成一列，共有 {n}! = {_fact(n)} = {a['count']}（種）。"]
    elif style == "colors":
        steps = [f"第一個字母有 {n} 種顏色可選，第二個字母要與前面不同，有 {n - 1} 種……共 {k} 個字母，所以有 {_falling_expr(n, k)} = {a['count']}（種）。"]
    else:
        steps = [f"從 {n} 個中任選 {k} 個排成一列：{_p(n, k)} = {_falling_expr(n, k)} = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], "方案數", steps, "selected_arrangement")


# --- 2. distinct_digit_numbers --------------------------------------------------------------------------------------------------------------

_DIGIT_ASK_TEXT = {"total": "能組成多少個{L}位數？", "not_multiple_of_5": "這些{L}位數中，不是 {five} 的倍數者有多少個？",
                   "multiple_of_5": "這些{L}位數中，是 {five} 的倍數者有多少個？", "even": "這些{L}位數中，偶數有多少個？", "odd": "這些{L}位數中，奇數有多少個？"}
_LAST_COND = {"multiple_of_5": ("5 的倍數", lambda d: d % 5 == 0), "not_multiple_of_5": ("不是 5 的倍數", lambda d: d % 5 != 0),
              "even": ("偶數", lambda d: d % 2 == 0), "odd": ("奇數", lambda d: d % 2 == 1)}


def _distinct_digit_numbers(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    ds, size, items = a["digits"], a["length"], a["items"]
    m, style = len(ds), g.get("style", "pick")
    digits_text = ", ".join(str(d) for d in ds)
    lines = [_DIGIT_ASK_TEXT[it["ask"]].format(L=_zh(size), five=_n(5)) for it in items]
    if style == "pick":
        if len(items) != 1 or items[0]["ask"] != "total":
            raise ValueError("pick_style_asks_total_only")
        question = f"從{digits_text}等{_zh(m)}個數字中，任選 {_n(size)} 個相異數字，共可排出多少個{_zh(size)}位數？"
    else:
        question = f"用{_zh(m)}個數字{digits_text}組成沒有重複數字的{_zh(size)}位數。\n" + (_numbered(lines) if len(lines) > 1 else lines[0])
    nonzero = [d for d in ds if d != 0]
    steps = []
    for i, it in enumerate(items, 1):
        if it["ask"] == "total":
            body = (f"最高位數不可為 0，有 {len(nonzero)} 種選法；其餘 {size - 1} 個位數依序從剩下的 {m - 1} 個數字中選，有 {_p(m - 1, size - 1)} = {math.perm(m - 1, size - 1)} 種。"
                    f"利用乘法原理，共 {len(nonzero)}×{math.perm(m - 1, size - 1)} = {it['count']}（個）。")
        else:
            name, ok = _LAST_COND[it["ask"]]
            terms = []
            for d in ds:
                if ok(d):
                    first = len([x for x in nonzero if x != d])
                    terms.append(f"個位數為 {d}：{first}×{math.perm(m - 2, size - 2)} = {first * math.perm(m - 2, size - 2)}")
            if sum(int(t.rsplit("= ", 1)[1]) for t in terms) != it["count"]:
                raise ValueError("explanation_disagrees_with_the_domain")
            body = f"個位數須{name}，依個位數的值分類（最高位數不可為 0）：" + "；".join(terms) + f"，合計 {it['count']}（個）。"
        steps.append((f"({i}) " if len(items) > 1 else "") + body)
    if len(items) > 1:
        return _items_payload(matrix, question, [f"({i}) 個數" for i in range(1, len(items) + 1)], a, steps, "distinct_digit_numbers")
    return _single_value(matrix, question, items[0]["count"], "個數", steps, "distinct_digit_numbers")


# --- 3. adjacent_separated --------------------------------------------------------------------------------------------------------------------

def _adjacent_separated(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    m, w = a["men"], a["women"]
    question = (f"男生 {_n(m)} 人及女生 {_n(w)} 人排成一列拍照。\n(1)若女生 {_n(w)} 人完全相鄰，則共有多少種排法？\n(2)若女生 {_n(w)} 人完全分開，則共有多少種排法？")
    steps = [f"(1) 將女生 {w} 人看成「1」人，與 {m} 位男生共 {m + 1} 人作排列，排法有 {m + 1}! = {math.factorial(m + 1)} 種；看成「1」人的 {w} 個女生，彼此間有 {w}! = {math.factorial(w)} 種排法。"
             f"乘法原理：{m + 1}!×{w}! = {a['adjacent']}（種）。",
             f"(2) 先將 {m} 位男生排成一列，有 {m}! = {math.factorial(m)} 種；再將 {w} 位女生分開排入兩旁及中間的 {m + 1} 個空隙，有 {_falling_expr(m + 1, w)} = {math.perm(m + 1, w)} 種。"
             f"乘法原理：{math.factorial(m)}×{math.perm(m + 1, w)} = {a['separated']}（種）。"]
    parts = [_value_part(1, a["adjacent"], "(1) 排法數"), _value_part(2, a["separated"], "(2) 排法數")]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1){a['adjacent']}；(2){a['separated']}", explanation_steps=steps, shape="adjacent_separated")


# --- 4. restricted_assignment -----------------------------------------------------------------------------------------------------------------

_UNIVERSITIES = ("臺大", "臺師大", "清大", "陽明交大")
_RUNNERS = "甲乙丙丁戊己庚辛"


def _place_word(q: int, k: int) -> str:
    return "首位" if q == 0 else ("末位" if q == k - 1 else f"第{q + 1}位")


def _restricted_assignment(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    n, k, style = a["n"], a["k"], g.get("style", "universities")
    pairs = [(int(p), int(q)) for p, q in g["forbidden"]]
    names = list(g.get("names") or [])
    if style == "universities":
        if len(pairs) != 2 or k > len(_UNIVERSITIES) or [p for p, _q in pairs] != [0, 1] or n <= k:
            raise ValueError("universities_style_shape")
        unis = _UNIVERSITIES[:k]
        listed = "、".join(unis[:-1]) + "與" + unis[-1]
        question = (f"學校想從 {_n(n)} 名學生中選派 {_n(k)} 人分別到{listed}等{_zh(k)}所大學參加研習，其中甲同學不到{unis[pairs[0][1]]}，乙同學不到{unis[pairs[1][1]]}。"
                    "請問共有多少種選派的方案？")
        word = "選派方案"
    elif style == "relay":
        if len(pairs) != 1 or pairs[0][1] != 0 or n > len(_RUNNERS) or n <= k:
            raise ValueError("relay_style_shape")
        runners = "、".join(_RUNNERS[:n])
        race = "四百公尺接力賽" if k == 4 else "接力賽"
        question = (f"田徑教練想從{runners} {_n(n)} 位選手中，任選 {_n(k)} 人參加{race}，並排定第一棒到第{_zh(k)}棒的名單。"
                    f"若{_RUNNERS[pairs[0][0]]}選手因起跑較慢不適合擔任第一棒，則出賽名單的安排共有多少種？")
        word = "出賽名單"
    elif style == "family":
        if len(pairs) != 2 or len(names) != 2 or n != k:
            raise ValueError("family_style_shape")
        question = (f"全家 {_n(n)} 人排成一列依序上公車，若{names[0]}不排{_place_word(pairs[0][1], k)}，{names[1]}不排{_place_word(pairs[1][1], k)}，則共有多少種排法？")
        word = "排法"
    elif style == "projects":
        if len(pairs) != 2 or n != k:
            raise ValueError("projects_style_shape")
        question = (f"有 {_n(n)} 個工程隊承建 {_n(n)} 個不同的建案，每個工程隊承建一個建案，其中甲工程隊不能承建 {_n(pairs[0][1] + 1)} 號建案，"
                    f"乙工程隊不能承建 {_n(pairs[1][1] + 1)} 號建案，共有多少種承建方案？")
        word = "承建方案"
    else:
        raise ValueError(f"unsupported_style:{style}")
    total, each = a["total"], a["each"]
    if a["both"] is None:
        steps = [f"設 U 為所有{word}的集合，A 為違反限制（那個人排在被禁止的位置）的{word}集合。n(U) = {_p(n, k)} = {total}，n(A) = {_p(n - 1, k - 1)} = {each[0]}。",
                 f"所求 = n(U) − n(A) = {total} − {each[0]} = {a['count']}（種）。"]
    else:
        steps = [f"設 U 為所有{word}的集合，A、B 分別為違反第一個、第二個限制的{word}集合。n(U) = {_p(n, k)} = {total}，n(A) = {_p(n - 1, k - 1)} = {each[0]}，"
                 f"n(B) = {_p(n - 1, k - 1)} = {each[1]}，n(A∩B) = {_p(n - 2, k - 2)} = {a['both']}。",
                 f"由取捨原理，所求 = n(U) − (n(A) + n(B) − n(A∩B)) = {total} − ({each[0]} + {each[1]} − {a['both']}) = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], "方案數", steps, "restricted_assignment")


# --- 5. two_group_line ------------------------------------------------------------------------------------------------------------------------

def _two_group_line(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    x, y, style = a["a"], a["b"], g.get("style", "baseball")
    if style == "baseball":
        if x + y != 9:
            raise ValueError("baseball_lineup_has_nine")
        question = (f"棒球隊的 {_n(9)} 名先發球員中有 {_n(x)} 名左打者，{_n(y)}名右打者。現在要將這 {_n(9)} 人排定一到九棒的打擊順序。"
                    "只考慮從第一棒到第九棒打一輪的情形，回答下列問題。\n(1)若左打者的棒次連排，右打者的棒次也連排，則共有多少種排法？\n(2)若左打者與右打者的棒次相間隔排，則共有多少種排法？")
        first, second = "左打者", "右打者"
    elif style == "club":
        question = (f"合唱團有 {_n(x)} 位男同學與 {_n(y)} 位女同學要排成一列上台表演，回答下列問題。\n(1)若男同學連排，女同學也連排，則共有多少種排法？\n"
                    "(2)若男同學與女同學相間隔排，則共有多少種排法？")
        first, second = "男同學", "女同學"
    else:
        raise ValueError(f"unsupported_style:{style}")
    fa, fb = math.factorial(x), math.factorial(y)
    pattern = ("兩群人可以互相交換，相間隔的排法有「" + first + "先」與「" + second + "先」2 種型態" if x == y
               else f"人數多的一群必須排在兩端，相間隔的型態只有 1 種")
    steps = [f"(1) 先決定{first}與{second}哪一群排前面，有 2 種；{first}內部有 {x}! = {fa} 種，{second}內部有 {y}! = {fb} 種。乘法原理：2×{fa}×{fb} = {a['contiguous']}（種）。",
             f"(2) {pattern}；{first}內部 {x}! = {fa} 種、{second}內部 {y}! = {fb} 種。乘法原理：{2 if x == y else 1}×{fa}×{fb} = {a['alternating']}（種）。"]
    parts = [_value_part(1, a["contiguous"], "(1) 排法數"), _value_part(2, a["alternating"], "(2) 排法數")]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1){a['contiguous']}；(2){a['alternating']}", explanation_steps=steps, shape="two_group_line")


# --- 6. counting_claim ------------------------------------------------------------------------------------------------------------------------

def _claim_tex(claim: dict[str, Any]) -> str:
    form = claim["form"]
    if form == "number":
        return _n(claim["value"])
    if form == "perm":
        return _p(claim["n"], claim["k"])
    if form == "power":
        return _t(f"{claim['base']}^{{{claim['exp']}}}")
    if form == "factorial":
        return _t(f"{claim['n']}!")
    counts = [int(c) for c in claim["counts"]]
    return _t("@frac{" + f"{sum(counts)}!" + "}{" + "".join(f"{c}!" for c in counts) + "}")


def _claim_value_text(claim: dict[str, Any]) -> str:
    form = claim["form"]
    if form == "perm":
        return f"P({claim['n']},{claim['k']})"
    if form == "power":
        return f"{claim['base']}^{claim['exp']}"
    if form == "factorial":
        return f"{claim['n']}!"
    if form == "multinomial":
        return _frac([int(c) for c in claim["counts"]])
    return str(claim["value"])


def _counting_claim(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    setting, claim = g["setting"], g["claim"]
    kind, shown = setting["kind"], _claim_tex(claim)
    head = "下列敘述對的打「○」，錯的打「×」。\n"
    if kind == "arrangement":
        chars = list(setting["chars"])
        if len(chars) != int(setting["n"]):
            raise ValueError("chars_differ_from_n")
        question = head + "將" + "、".join(f"「{c}」" for c in chars) + f"{_zh(len(chars))}個字任意排列，共有 {shown} 種排法。"
        calc = f"{len(chars)} 個不同的字全部排列有 {setting['n']}! = {a['actual']} 種"
    elif kind == "selection":
        question = head + f"從 {_n(setting['n'])} 個人中任選 {_n(setting['k'])} 個人排成一列，共有 {shown} 種排法。"
        calc = f"{_falling_expr(int(setting['n']), int(setting['k']))} = {a['actual']} 種（即 P({setting['n']},{setting['k']})）"
    elif kind == "identical":
        counts = [int(c) for c in setting["counts"]]
        word = str(setting["word"])
        if len(word) != sum(counts):
            raise ValueError("word_differs_from_counts")
        question = head + f"將{_zh(sum(counts))}個字母{word}任意排成一列，共有 {shown} 種排法。"
        calc = f"有相同物的排列 {_frac(counts)} = {a['actual']} 種"
    elif kind == "repeated":
        question = head + f"將 {_n(setting['items'])} 名新生任意分發到 {_n(setting['boxes'])} 個班級，共有 {shown} 種分法。"
        calc = f"每名新生都有 {setting['boxes']} 種分法，共 {setting['boxes']}^{setting['items']} = {a['actual']} 種"
    else:
        raise ValueError(f"unsupported_setting:{kind}")
    truth = a["truth"]
    steps = [f"{calc}。敘述中的 {_claim_value_text(claim)} = {a['claimed']}，{'與實際種數相同' if truth else '與實際種數不同'}，所以敘述為「{'○' if truth else '×'}」。"]
    return _single_payload(matrix, question=question, part=_choice_part(1, "A" if truth else "B", TRUE_FALSE_CHOICES),
                           display_answer="○" if truth else "×", explanation_steps=steps, shape="single_choice")


# --- 7. ends_from_group -----------------------------------------------------------------------------------------------------------------------

def _ends_from_group(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    s, t = a["special"], a["others"]
    question = (f"電視臺將連續播放 {_n(s + t)} 個廣告，其中含有 {_n(t)} 個不同的商業廣告以及 {_n(s)} 個不同的公益廣告。若要求首尾必須播放公益廣告，則共有多少種播放方式？")
    steps = [f"首尾要放公益廣告：先排第一個有 {s} 種，再排最後一個有 {s - 1} 種，即 {_p(s, 2)} = {a['ends']} 種；中間 {s + t - 2} 個位置排剩下的 {s + t - 2} 個廣告，有 {s + t - 2}! = {a['middle']} 種。",
             f"乘法原理：{a['ends']}×{a['middle']} = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], "播放方式數", steps, "ends_from_group")


# --- 8. ends_and_block ----------------------------------------------------------------------------------------------------------------------

def _ends_and_block(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    f, s, b = a["end_group"], a["singles"], a["block"]
    if (f, s, b) == (2, 2, 2):
        question = "兩對夫婦各帶一個小孩到遊樂園玩，六人購票後排成一列依序入園。為安全起見，首尾一定排兩位爸爸，而且兩個小孩一定排在一起，則入園的排隊方法共有多少種？"
    else:
        question = (f"遊樂園入口有 {_n(f)} 位爸爸、{_n(s)} 位媽媽和 {_n(b)} 個小孩排成一列依序入園。為安全起見，首尾一定排爸爸，而且 {_n(b)} 個小孩一定排在一起，"
                    "則入園的排隊方法共有多少種？")
    steps = [f"分三個步驟：①首尾排爸爸：{_p(f, 2)} = {a['ends']} 種。②將 {b} 個小孩看成「1」人，與其餘 {f - 2} 位爸爸、{s} 位媽媽共 {a['units']} 個單位排在中間，有 {a['units']}! = {math.factorial(a['units'])} 種。"
             f"③小孩彼此間有 {b}! = {math.factorial(b)} 種排法。",
             f"乘法原理：{a['ends']}×{math.factorial(a['units'])}×{math.factorial(b)} = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], "排隊方法數", steps, "ends_and_block")


# --- 9. fixed_order_insertion ---------------------------------------------------------------------------------------------------------------------

def _fixed_order_insertion(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    old, new = a["base"], a["added"]
    total = old + new
    question = (f"某班慶生會原訂的 {_n(old)} 個節目已排成節目單。若臨時再增加 {_n(new)} 個新節目，且原有 {_n(old)} 個節目的相對順序保持不變，"
                f"則增加 {_n(new)} 個新節目後的節目單可以有多少種？")
    steps = [f"新舊節目共 {total} 個。先為 {new} 個新節目依序選位置：{_falling_expr(total, new)} 種，剩下的 {old} 個位置依原來的順序放入舊節目，只有 1 種。",
             f"所以節目單共有 {_falling_expr(total, new)} = {a['count']} 種（也等於 {total}!÷{old}!）。"]
    return _single_value(matrix, question, a["count"], "節目單數", steps, "fixed_order_insertion")


# --- 10. relative_order_three --------------------------------------------------------------------------------------------------------------------------

_LETTERS = "ABCDEFGH"


def _relative_order_three(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    n, mode = a["n"], a["mode"]
    first, second = sorted(a["pair"])
    x, y, z = _LETTERS[first], _LETTERS[second], _LETTERS[a["ref"]]
    letters = ", ".join(_LETTERS[:n])
    cond = f"{x}, {y}都須在{z}的同一側" if mode == "same_side" else f"{z}必須排在{x}, {y}之間"
    question = f"將{letters}{_zh(n)}個字母排成一列，若{cond}，則共有多少種排法？"
    if mode == "same_side":
        steps = [f"只看 {x}, {y}, {z} 三個字母的相對順序，共有 3! = 6 種；{x}, {y}都在{z}的同一側（{z}在三者的最左或最右）有 4 種。",
                 f"所以排法共有 {n}!×4/6 = {math.factorial(n)}×4/6 = {a['count']}（種）。"]
    else:
        steps = [f"只看 {x}, {y}, {z} 三個字母的相對順序，共有 3! = 6 種；{z}排在{x}, {y}之間（{x}{z}{y} 或 {y}{z}{x}）有 2 種。",
                 f"所以排法共有 {n}!×2/6 = {math.factorial(n)}×2/6 = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], "排法數", steps, "relative_order_three")


# --- 11. identical_arrangement -------------------------------------------------------------------------------------------------------------------------

def _identical_arrangement(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    counts, style = a["counts"], g.get("style", "duty")
    total = a["total"]
    if style == "duty":
        names = list(g["names"])
        if len(counts) != 2 or len(names) != 2:
            raise ValueError("duty_style_shape")
        question = (f"{names[0]}、{names[1]}兩人負責在 {_n(total)} 天年假期間到公司值班，其中{names[0]}值班 {_n(counts[0])} 天，{names[1]}值班 {_n(counts[1])} 天。"
                    "請問年假值班的安排共有多少種？")
        label = "值班安排數"
        how = f"將 {counts[0]} 個{names[0]}及 {counts[1]} 個{names[1]}在第一天到第{_zh(total)}天底下任意排成一列"
    elif style == "train":
        animals = list(g["animals"])
        if len(counts) != 2 or len(animals) != 2:
            raise ValueError("train_style_shape")
        question = (f"開往動物園的電聯車有 {_n(total)} 節車廂。若打算將其中 {_n(counts[0])} 節車廂漆上相同的{animals[0]}圖樣，{_n(counts[1])}節車廂漆上相同的{animals[1]}圖樣，"
                    f"則此 {_n(total)} 節車廂圖樣的安排共有多少種？")
        label = "圖樣安排數"
        how = f"將 {counts[0]} 個{animals[0]}及 {counts[1]} 個{animals[1]}排成一列"
    elif style == "volunteers":
        if len(counts) != 3:
            raise ValueError("volunteers_style_shape")
        days = f"週一至週六的 {_n(6)} 天" if total == 6 else f"連續 {_n(total)} 天"
        need = f"每人參加{_zh(counts[0])}天" if len(set(counts)) == 1 else f"甲參加 {_n(counts[0])} 天、乙參加 {_n(counts[1])} 天、丙參加 {_n(counts[2])} 天"
        question = f"將甲、乙、丙三名志工安排在{days}中支援園遊會服務的工作。若要求{need}，且每天安排一人，則共有多少種安排的方法？"
        label = "安排方法數"
        how = f"將 {counts[0]} 個甲、{counts[1]} 個乙、{counts[2]} 個丙在這 {total} 天底下任意排成一列"
    else:
        raise ValueError(f"unsupported_style:{style}")
    steps = [f"{how}，每一種排列等同於一種安排。利用有相同物的排列，共有 {_frac(counts)} = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], label, steps, "identical_arrangement")


# --- 12. grid_paths (figure on the textbook structures only) ----------------------------------------------------------------------------------

_GRID_TEXT = {"any": "任意走捷徑。", "via_C": "經C點。", "via_C_or_D": "經C點或經D點。", "avoid_both": "不經C點且不經D點。"}


def _grid_paths(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    w, h = a["width"], a["height"]
    c, d = tuple(g["points"]["C"]), tuple(g["points"]["D"])
    figure = g.get("figure")
    if figure is not None:
        spec = FIGURE_GRIDS.get(figure)
        if spec is None or (spec["width"], spec["height"], spec["C"], spec["D"]) != (w, h, c, d):
            raise ValueError("grid_differs_from_the_textbook_figure")
        lead = ("在右圖的棋盤街道中，從A到B走捷徑（只能向右或向上走的路徑），求下列情形各有多少種方法？" if figure == "example7"
                else "在右圖的棋盤街道中，從A到B走捷徑，求下列情形各有多少種方法？")
    else:
        lead = (f"在橫向 {_n(w)} 個街區、縱向 {_n(h)} 個街區的棋盤街道中，A 點在最左下角，B 點在最右上角，C 點在 A 點向右 {_n(c[0])} 個街區、向上 {_n(c[1])} 個街區處，"
                f"D 點在 A 點向右 {_n(d[0])} 個街區、向上 {_n(d[1])} 個街區處。從A到B走捷徑（只能向右或向上走的路徑），求下列情形各有多少種方法？")
    asks = [it["ask"] for it in a["items"]]
    question = lead + "\n" + _numbered([_GRID_TEXT[k] for k in asks])
    start, end = (0, 0), (w, h)
    ac, cb, ad, db, cd = _lattice(start, c), _lattice(c, end), _lattice(start, d), _lattice(d, end), _lattice(c, d)
    steps = []
    for i, it in enumerate(a["items"], 1):
        k = it["ask"]
        if k == "any":
            body = f"每條捷徑等同於 {w} 個「右」與 {h} 個「上」的一種直線排列，共有 {_frac([w, h])} = {a['total']}（種）。"
        elif k == "via_C":
            body = f"分兩個步驟：從 A 走捷徑到 C 有 {ac} 種，從 C 走捷徑到 B 有 {cb} 種，乘法原理得 {ac}×{cb} = {a['via_C']}（種）。"
        elif k == "via_C_or_D":
            body = (f"經 C 有 {a['via_C']} 種，經 D 有 {ad}×{db} = {a['via_D']} 種，同時經 C 與 D 有 {ac}×{cd}×{db} = {a['via_both']} 種（若兩點不在同一條捷徑上則為 0）。"
                    f"取捨原理：{a['via_C']} + {a['via_D']} − {a['via_both']} = {a['union']}（種）。")
        else:
            body = f"不經 C 且不經 D 的捷徑 = 全部 − (經 C 或經 D) = {a['total']} − {a['union']} = {a['avoid']}（種）。"
        steps.append(f"({i}) {body}")
    return _items_payload(matrix, question, [f"({i}) 方法數" for i in range(1, len(asks) + 1)], a, steps, "grid_paths", figure=figure is not None)


# --- 13. multiset_digit_numbers -------------------------------------------------------------------------------------------------------------------

def _multiset_digit_numbers(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    ds, ask = a["digits"], a["ask"]
    total = len(ds)
    listed = ", ".join(str(d) for d in ds)
    tail = {"number": "共有多少個？", "even": "偶數有多少個？", "odd": "奇數有多少個？"}[ask]
    if ask == "number":
        question = f"由 {_n(total)} 個數字{listed}排成的{_zh(total)}位數，{tail}"
        counter = {d: ds.count(d) for d in sorted(set(ds))}
        lead = (f"{total} 個數字的任意排列數 {_frac(list(counter.values()))} = {a['all_arrangements']}，其中 0 排首位的排列不是{_zh(total)}位數，必須扣除；"
                f"0 排首位時其餘 {total - 1} 個數字任意排列。" if 0 in ds else "首位不會是 0。")
        steps = [f"{lead}所求為 {a['count']}（個）。"]
    else:
        question = f"由 {_n(total)} 個數字{listed}排成的 {_n(total)} 位數中，{tail}"
        cond = "個位數須為偶數" if ask == "even" else "個位數須為奇數"
        steps = [f"{cond}，依個位數的值分類：固定個位數後，其餘 {total - 1} 個數字作有相同物的排列（最高位不為 0），各類相加共 {a['count']}（個）。"]
    return _single_value(matrix, question, a["count"], "個數", steps, "multiset_digit_numbers")


# --- 14. colored_distinct_items ---------------------------------------------------------------------------------------------------------------------

_COLOR_ASK_TEXT = {"each_color_together": "{c1}、{c2}、{c3}三顏色貓各連排在一起。", "last_color_apart": "任二隻{c3}貓不相鄰。"}


def _colored_distinct_items(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    cs, colors = a["counts"], list(g["colors"])
    if len(colors) != 3 or len(set(colors)) != 3:
        raise ValueError("three_colours_needed")
    total, rest = a["total"], a["rest"]
    lines = [_COLOR_ASK_TEXT[it["ask"]].format(c1=colors[0], c2=colors[1], c3=colors[2]) for it in a["items"]]
    question = (f"有{_zh(total)}隻大小不同的貓，其中{_zh(cs[0])}隻{colors[0]}色、{_zh(cs[1])}隻{colors[1]}色及{_zh(cs[2])}隻{colors[2]}色。"
                f"將這{_zh(total)}隻貓排成一列，求下列各排列數。\n" + _numbered(lines))
    steps = []
    for i, it in enumerate(a["items"], 1):
        if it["ask"] == "each_color_together":
            body = (f"三種顏色各看成一組，三組排列有 3! = 6 種；每組內部的貓互不相同，各有 {cs[0]}!、{cs[1]}!、{cs[2]}! 種排法。"
                    f"乘法原理：6×{math.factorial(cs[0])}×{math.factorial(cs[1])}×{math.factorial(cs[2])} = {it['count']}（種）。")
        else:
            body = (f"先排其他顏色的 {rest} 隻貓，有 {rest}! = {math.factorial(rest)} 種；再把 {cs[2]} 隻{colors[2]}貓排入這 {rest} 隻貓形成的 {rest + 1} 個空隙，有 "
                    f"{_falling_expr(rest + 1, cs[2])} = {math.perm(rest + 1, cs[2])} 種。乘法原理：{math.factorial(rest)}×{math.perm(rest + 1, cs[2])} = {it['count']}（種）。")
        steps.append(f"({i}) {body}")
    return _items_payload(matrix, question, [f"({i}) 排列數" for i in range(1, len(lines) + 1)], a, steps, "colored_distinct_items")


# --- 15. column_shooting_order (figure on the textbook structure only) ----------------------------------------------------------------------------

def _column_shooting_order(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    cs, colors, total = a["counts"], list(g["colors"]), a["total"]
    if len(colors) != len(cs):
        raise ValueError("colours_differ_from_strings")
    figure = g.get("figure")
    if figure is not None:
        if figure != "balloons" or (tuple(cs), tuple(colors)) != (FIGURE_BALLOONS["counts"], FIGURE_BALLOONS["colors"]):
            raise ValueError("balloons_differ_from_the_textbook_figure")
        question = (f"用三串分別為 {_n(cs[0])} 個{colors[0]}氣球、{cs[1]}個{colors[1]}氣球和 {_n(cs[2])} 個{colors[2]}氣球來當射擊靶子，如圖所示。"
                    f"若每次射破的氣球，都必須是該串尚未被射破氣球中最低的那一個，則射破全部 {_n(total)} 個氣球可以有多少種次序？")
    else:
        listed = "、".join(f"{_n(c)} 個{col}氣球" for c, col in zip(cs, colors))
        question = (f"用{_zh(len(cs))}串分別為 {listed}來當射擊靶子，每串氣球由上往下排成一直串。"
                    f"若每次射破的氣球，都必須是該串尚未被射破氣球中最低的那一個，則射破全部 {_n(total)} 個氣球可以有多少種次序？")
    steps = [f"每一串只能由下往上射，串內的順序固定，所以射破次序只由「每一次射哪一串」決定，相當於 {'、'.join(f'{c} 個{col}' for c, col in zip(cs, colors))} 的直線排列。",
             f"共有 {_frac(cs)} = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], "次序數", steps, "column_shooting_order", figure=figure is not None)


# --- 16. line_walk ----------------------------------------------------------------------------------------------------------------------------------

def _line_walk(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    s, t = a["steps"], a["target"]
    shown = f"+{t}" if t > 0 else str(t)
    question = (f"在數線上有一個運動物體從原點出發，在此數線上跳動，每次向正方向或負方向跳 {_n(1)} 個單位，跳動過程可重複經過任何一點。"
                f"若經過 {_n(s)} 次跳動後運動物體落在點 {_n(shown)} 處，則此運動物體共有多少種跳動方法？")
    steps = [f"設向正方向跳 x 次、向負方向跳 y 次，則 x + y = {s}，x − y = {t}，得 x = {a['right']}、y = {a['left']}。",
             f"每一種跳法等同於 {a['right']} 個「正」與 {a['left']} 個「負」的一種直線排列，共有 {_frac([a['right'], a['left']])} = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], "跳動方法數", steps, "line_walk")


# --- 17. distribute_distinct --------------------------------------------------------------------------------------------------------------------------

_RECEIVERS = {3: "甲、乙、丙三人", 4: "甲、乙、丙、丁四人"}
_LUNCH = ("雞腿", "排骨", "魚排", "素食")


def _distribute_distinct(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    b, items, style = a["boxes"], a["items"], g.get("style", "rabbit")
    kinds = [it["kind"] for it in items]
    n0 = items[0]["items"]
    if style == "rabbit":
        if kinds != ["any", "onto"] or items[1]["items"] != n0:
            raise ValueError("rabbit_style_shape")
        question = (f"某兔子挖了{_zh(b)}個可以藏身的洞。已知未來的{_zh(n0)}個晚上，該兔子每晚都待在這{_zh(b)}個洞的其中之一來躲避敵人，回答下列問題。\n"
                    f"(1)共有多少種藏身安排？\n(2)若{_zh(b)}個洞都要待過，則共有多少種藏身安排？")
        labels = ["(1) 藏身安排數", "(2) 藏身安排數"]
    elif style == "books":
        if kinds != ["any", "first_at_least", "first_exactly"] or b not in _RECEIVERS or items[1]["k"] != items[2]["k"]:
            raise ValueError("books_style_shape")
        k = items[1]["k"]
        question = (f"將 {_n(n0)} 本不同的書全部分給{_RECEIVERS[b]}，求下列情形各有多少種分法。\n(1)任意分。\n(2)甲至少得 {_n(k)} 本。\n(3)甲恰得 {_n(k)} 本。")
        labels = ["(1) 分法數", "(2) 分法數", "(3) 分法數"]
    elif style == "vending":
        if kinds != ["any", "all_different"]:
            raise ValueError("vending_style_shape")
        question = (f"自動販賣機有 {_n(b)} 種飲料可供選擇，{_zh(n0)}個人運動完後各購買一罐飲料。\n(1)共有多少種選購方法？\n(2)若{_zh(n0)}人約定所選的飲料不可以相同，則共有多少種選購方法？")
        labels = ["(1) 選購方法數", "(2) 選購方法數"]
    elif style == "rooms":
        if kinds != ["each_at_most", "each_at_most"] or items[0]["cap"] != items[1]["cap"]:
            raise ValueError("rooms_style_shape")
        letters = ", ".join("ABCD"[:b])
        question = (f"有{letters}{_zh(b)}間房間可供選擇，每間房間最多可住 {_n(items[0]['cap'])} 人。下列住宿的安排方案各有多少種？\n"
                    f"(1) {_n(items[0]['items'])}人同時住宿。\n(2) {_n(items[1]['items'])}人同時住宿。")
        labels = ["(1) 安排方案數", "(2) 安排方案數"]
    elif style == "lunch":
        if kinds != ["each_at_most"] or b > len(_LUNCH):
            raise ValueError("lunch_style_shape")
        names = "、".join(_LUNCH[:b])
        question = (f"社團幹部 {_n(n0)} 人訂午餐，每人各訂一個便當，有{names} {_n(b)} 種便當可選，但其中任一種便當至多只能作 {_n(items[0]['cap'])} 人份。"
                    f"請問 {_n(n0)} 人共有多少種選購方法？")
        labels = ["選購方法數"]
    elif style == "digits":
        ds = [int(d) for d in g["digits"]]
        if kinds != ["onto"] or len(ds) != b or len(set(ds)) != b or 0 in ds:
            raise ValueError("digits_style_shape")
        listed = ", ".join(str(d) for d in ds)
        question = f"由數字{listed}組成{_zh(n0)}位數，且數字{listed}至少都出現一次，這樣的{_zh(n0)}位數共有多少個？"
        labels = ["個數"]
    else:
        raise ValueError(f"unsupported_style:{style}")
    steps = []
    for i, it in enumerate(items, 1):
        n, k = it["items"], it["kind"]
        if k == "any":
            body = f"{n} 個對象各有 {b} 種選擇，乘法原理：{b}^{n} = {it['count']}（種）。"
        elif k == "onto":
            body = f"每一種都要用到：由取捨原理，{b}^{n} 減去缺少至少一種的情形，共 {it['count']}（種）。"
        elif k == "first_at_least":
            body = f"至少 {it['k']} 個 = 任意分 − 少於 {it['k']} 個，任意分 {b}^{n} = {it['all']}，所以共 {it['count']}（種）。"
        elif k == "first_exactly":
            body = f"先從 {n} 個中選 {it['k']} 個給甲，有 {math.comb(n, it['k'])} 種，其餘 {n - it['k']} 個分給其他 {b - 1} 個對象，有 {b - 1}^{n - it['k']} 種，乘法原理共 {it['count']}（種）。"
        elif k == "all_different":
            body = f"{n} 人所選互不相同：{_falling_expr(b, n)} = {it['count']}（種）。"
        else:
            body = f"任意安排有 {b}^{n} = {it['all']} 種，扣除有一個對象超過上限 {it['cap']} 的情形，共 {it['count']}（種）。"
        steps.append((f"({i}) " if len(items) > 1 else "") + body)
    return _items_payload(matrix, question, labels, a, steps, "distribute_distinct")


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "selected_arrangement": _selected_arrangement,
    "distinct_digit_numbers": _distinct_digit_numbers,
    "adjacent_separated": _adjacent_separated,
    "restricted_assignment": _restricted_assignment,
    "two_group_line": _two_group_line,
    "counting_claim": _counting_claim,
    "ends_from_group": _ends_from_group,
    "ends_and_block": _ends_and_block,
    "fixed_order_insertion": _fixed_order_insertion,
    "relative_order_three": _relative_order_three,
    "identical_arrangement": _identical_arrangement,
    "grid_paths": _grid_paths,
    "multiset_digit_numbers": _multiset_digit_numbers,
    "colored_distinct_items": _colored_distinct_items,
    "column_shooting_order": _column_shooting_order,
    "line_walk": _line_walk,
    "distribute_distinct": _distribute_distinct,
}


def adapt_permutations_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_permutations_operation:{operation}")
    return builder(matrix)
