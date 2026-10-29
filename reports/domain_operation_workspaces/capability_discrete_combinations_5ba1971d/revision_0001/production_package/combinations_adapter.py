"""Question payload contracts for discrete.combinations (普高數學2 Unit 5 組合、二項式定理).

Every expected answer comes from the domain matrix, never from this adapter.  Stems are rebuilt from the same stated data the domain solved,
so a varied question always carries its own numbers.  No question of this domain points to a figure (the only figure row, 進階題12, stays a
fixed textbook item), so no stem may contain a figure cue.  Format hints never show the answer.
"""

from __future__ import annotations

import math
from typing import Any, Callable

from core.domain.promoted.algebra_multiplication_formulas.multiplication_formulas_adapter import polynomial_latex

from .combinations_domain import DOMAIN_KEY

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_SET = ("solution_set_checker", "unordered_solution_set", "solution_set")
_EXPANDED = ("expression_checker", "algebraic_equivalent", "expression")
_ZH = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九", 10: "十", 11: "十一", 12: "十二"}
_COUNT_ZH = {1: "一", 2: "兩", 3: "三", 4: "四"}
_PEOPLE = "甲乙丙丁"
_TF_HEAD = "下列敘述對的打「○」，錯的打「×」。\n"


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


def _parts_payload(matrix, *, question, parts, display_answer, explanation_steps, shape) -> dict[str, Any]:
    if len(parts) == 1:
        return _single_payload(matrix, question=question, part=parts[0], display_answer=display_answer, explanation_steps=explanation_steps, shape=shape)
    return _payload(matrix, question=question, answer={p["key"]: p["expected_answer"] for p in parts}, display_answer=display_answer,
                    contract=_contract("multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer", answer_shape=shape, parts=parts),
                    explanation_steps=explanation_steps)


def _t(s: str) -> str:
    """Inline math.  ``@`` stands for a backslash in short literals (no backslash may sit inside an f-string expression on Python 3.11)."""
    return "$" + s.replace("@", "\\") + "$"


def _n(v: Any) -> str:
    return _t(str(v))


def _zh(n: int) -> str:
    return _ZH[int(n)]


def _c(n: int, k: int) -> str:
    return f"C_{{{k}}}^{{{n}}}"


def _p(n: int, k: int) -> str:
    return f"P_{{{k}}}^{{{n}}}"


def _value_part(index: int, value: Any, label: str) -> dict[str, Any]:
    return _part(index, str(value), *_RATIONAL, label=label, prompt=label)


def _choice_part(index: int, expected_label: str, choices) -> dict[str, Any]:
    return _part(index, expected_label, "choice_label_checker", "choice_label", "single_choice", choices=[dict(c) for c in choices])


def _numbered(lines: list[str]) -> str:
    return "\n".join(f"({i}){line}" for i, line in enumerate(lines, 1))


def _falling_expr(n: int, k: int) -> str:
    return "×".join(str(n - i) for i in range(k))


def _comb_expr(n: int, k: int) -> str:
    """C(n,k) worked out with the smaller of k, n-k, e.g. ``C_{8}^{10} = C_{2}^{10} = (10×9)/(2×1) = 45``."""
    j = min(k, n - k)
    head = _c(n, k) + (f"={_c(n, j)}" if j != k else "")
    if j == 0:
        return f"${head}=1$"
    if j == 1:
        return f"${head}={n}$"
    return f"${head}$ = ({_falling_expr(n, j)})/({_falling_expr(j, j)}) = {math.comb(n, k)}"


def _items_payload(matrix, question, labels, counts, steps, shape) -> dict[str, Any]:
    parts = [_value_part(i, c, label) for i, (c, label) in enumerate(zip(counts, labels), 1)]
    display = "；".join(f"({i}){c}" for i, c in enumerate(counts, 1)) if len(parts) > 1 else str(counts[0])
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps, shape=shape)


def _single_value(matrix, question, count, label, steps, shape) -> dict[str, Any]:
    return _parts_payload(matrix, question=question, parts=[_value_part(1, count, label)], display_answer=str(count), explanation_steps=steps, shape=shape)


def _truth_payload(matrix, question, truth: bool, steps, shape) -> dict[str, Any]:
    part = _choice_part(1, "A" if truth else "B", TRUE_FALSE_CHOICES)
    return _single_payload(matrix, question=question, part=part, display_answer="○" if truth else "×", explanation_steps=steps, shape=shape)


def _prefix(i: int, total: int) -> str:
    return f"({i}) " if total > 1 else ""


def _par(v: int) -> str:
    return f"({v})" if v < 0 else str(v)


def _sum_text(values: list[int]) -> str:
    return " + ".join(_par(v) for v in values)


# --- 1. combination_evaluate ---------------------------------------------------------------------------------------------------------------

def _combination_evaluate(matrix: dict[str, Any]) -> dict[str, Any]:
    items = matrix["answer"]["items"]
    shown, steps = [], []
    for i, it in enumerate(items, 1):
        n, k = it["n"], it["k"]
        if it["kind"] == "comb":
            shown.append(_t(_c(n, k)))
            body = _comb_expr(n, k) + "。"
        else:
            shown.append(_t(f"@frac{{{_p(n, k)}}}{{{_c(n, k)}}}"))
            body = (f"從 {n} 個中選 {k} 個排成一列，可以先選出 {k} 個（{_t(_c(n, k))} 種），再把這 {k} 個排列（{k}! 種），"
                    f"所以 {_t(_p(n, k) + '=' + _c(n, k) + '@times ' + str(k) + '!')}，比值為 {k}! = {it['value']}。")
        steps.append(_prefix(i, len(items)) + body)
    if len(items) > 1:
        question = "求下列各數：\n" + " ".join(f"({i}){s}。" for i, s in enumerate(shown, 1))
    else:
        question = f"求 {shown[0]} 的值。"
    return _items_payload(matrix, question, [f"({i}) 值" for i in range(1, len(items) + 1)], [it["value"] for it in items], steps, "combination_values")


# --- 2. select_with_members ------------------------------------------------------------------------------------------------------------------

_MEMBER_TEXT = {
    "handball": {
        "exactly_one": "若其中甲、乙兩人定位為守門員，必恰選一人，則共有多少種選法？",
        "at_least_one": "若其中甲、乙兩人定位為守門員，至少要選一人，則共有多少種選法？",
        "neither": "若其中甲、乙兩人因傷都不能上場，則共有多少種選法？",
        "both": "若其中甲、乙兩人是隊長一定都要上場，則共有多少種選法？",
    },
    "basketball": {
        "both": "若其中甲、乙兩人是主力選手一定都要上場，則共有多少種選法？",
        "neither": "若其中甲、乙兩人因傷都不能上場，則共有多少種選法？",
        "exactly_one": "若其中甲、乙兩人恰有一人上場，則共有多少種選法？",
        "at_least_one": "若其中甲、乙兩人至少有一人上場，則共有多少種選法？",
    },
}
_PLAYERS = {"handball": "手球選手", "basketball": "籃球隊員"}


def _select_with_members(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    style = g.get("style", "handball")
    if style not in _PLAYERS:
        raise ValueError(f"unsupported_style:{style}")
    n, k = a["n"], a["k"]
    lines, steps = [], []
    for i, it in enumerate(a["items"], 1):
        ask = it["ask"]
        if ask == "total":
            lines.append("共有多少種選法？")
            body = f"從 {n} 人中任選 {k} 人：{_comb_expr(n, k)}（種）。"
        else:
            lines.append(_MEMBER_TEXT[style][ask])
            if ask == "exactly_one":
                body = (f"先從甲、乙兩人選一人，有 {_t(_c(2, 1))} = 2 種；再從其餘 {n - 2} 人中任選 {k - 1} 人，有 {_comb_expr(n - 2, k - 1)} 種。"
                        f"乘法原理：2×{math.comb(n - 2, k - 1)} = {it['count']}（種）。")
            elif ask == "both":
                body = f"甲、乙兩人都選入，只要再從其餘 {n - 2} 人中任選 {k - 2} 人：{_comb_expr(n - 2, k - 2)}（種）。"
            elif ask == "neither":
                body = f"甲、乙兩人都不選，從其餘 {n - 2} 人中任選 {k} 人：{_comb_expr(n - 2, k)}（種）。"
            else:
                body = (f"全部選法 {_t(_c(n, k))} = {math.comb(n, k)} 種，扣除甲、乙都沒選的 {_t(_c(n - 2, k))} = {math.comb(n - 2, k)} 種，"
                        f"得 {it['count']}（種）。")
        steps.append(_prefix(i, len(a["items"])) + body)
    question = f"從 {_n(n)} 位{_PLAYERS[style]}中選出 {_n(k)} 人上場比賽。\n" + _numbered(lines)
    return _items_payload(matrix, question, [f"({i}) 選法數" for i in range(1, len(lines) + 1)], [it["count"] for it in a["items"]], steps,
                          "select_with_members")


# --- 3. mixed_group_ordered ----------------------------------------------------------------------------------------------------------------

def _mixed_group_ordered(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    style, sizes, p = g.get("style", "debate"), a["groups"], a["pick"]
    if style == "debate":
        if len(sizes) != 2 or p != 3 or a["require"] != [0, 1]:
            raise ValueError("debate_style_shape")
        names = ["男", "女"]
        question = (f"辯論社的 {_n(sizes[0])} 位男生與 {_n(sizes[1])} 位女生組隊參加奧瑞岡三人制辯論比賽。從這 {_n(sum(sizes))} 人中，"
                    "選出 3 人分別擔任一辯、二辯與三辯。\n請問出賽名單中既有男生又有女生的安排共有多少種？")
        label = "安排數"
    elif style == "ranking":
        if len(sizes) != 3 or p != 3 or a["require"] != [0, 1]:
            raise ValueError("ranking_style_shape")
        names = ["高一", "高二", "高三"]
        question = (f"全校羽球單打排名賽共有高一 {_n(sizes[0])} 人、高二 {_n(sizes[1])} 人、高三 {_n(sizes[2])} 人參賽。"
                    "若排前三名的三人中，有高一也有高二，則前三名的名單共有多少種情形？")
        label = "名單情形數"
    else:
        raise ValueError(f"unsupported_style:{style}")
    lead = "選出 3 人中既有男生又有女生" if style == "debate" else "前三名中有高一也有高二"
    case_names = ["".join(f"{c}{names[j] if style == 'debate' else names[j] + '生'}" for j, c in enumerate(case["counts"]) if c) for case in a["cases"]]
    steps = [f"{lead}的情形可依各組人數分成 {len(a['cases'])} 類，每一類先選出人，再將選出的 {p} 人作直線排列（{p}! = {math.factorial(p)} 種）："]
    for i, (case, name) in enumerate(zip(a["cases"], case_names), 1):
        chosen = "×".join(_c(s, c) for s, c in zip(sizes, case["counts"]) if c)
        steps.append(f"類別{_zh(i)}「{name}」：{_t('@left(' + chosen + '@right)@times ' + str(p) + '!')} = {case['selections']}×{math.factorial(p)} = {case['ways']}（種）。")
    steps.append("利用加法原理，共有 " + " + ".join(str(c["ways"]) for c in a["cases"]) + f" = {a['count']}（種）。")
    return _single_value(matrix, question, a["count"], label, steps, "mixed_group_ordered")


# --- 4. group_partition ------------------------------------------------------------------------------------------------------------------

def _unlabeled_text(sizes: list[int], noun: str, unit: str, verb: str) -> str:
    """e.g. sizes [4, 1, 1] -> 其中一袋裝 4 本，另兩袋各裝 1 本; [3, 3, 2] -> 其中兩組各有 3 人，另一組有 2 人."""
    order = sorted(set(sizes), reverse=True)
    pieces = []
    for idx, s in enumerate(order):
        m = sizes.count(s)
        lead = "其中" if idx == 0 else "另"
        pieces.append(f"{lead}{_COUNT_ZH[m]}{noun}{'各' if m > 1 else ''}{verb} {_n(s)} {unit}")
    return "，".join(pieces)


def _labeled_text(sizes: list[int], names: list[str], unit: str, verb: str, each: str) -> str:
    if len(set(sizes)) == 1:
        return f"{each} {_n(sizes[0])} {unit}"
    return "，".join(f"{nm}{verb} {_n(s)} {unit}" for nm, s in zip(names, sizes))


def _partition_step(item: dict[str, Any], n: int, noun: str) -> str:
    sizes = item["sizes"]
    chain, left = [], n
    for s in sizes:
        chain.append(_c(left, s))
        left -= s
    product = "@times ".join(chain)
    if item["labeled"]:
        return f"依序為每一{noun}選出成員：{_t(product)} = {item['count']}（種）。"
    repeats = [s for s in sorted(set(sizes), reverse=True) if sizes.count(s) > 1]
    rep = "、".join(f"有 {sizes.count(s)} {noun}的大小都是 {s}" for s in repeats)
    fact = "×".join(f"{sizes.count(s)}!" for s in repeats)
    return (f"先假設各{noun}不同（依序編號），有 {_t(product)} = {item['ordered_count']} 種分法；但{noun}是相同的，{rep}，"
            f"這些{noun}互換只算同 1 種，每 {fact} = {item['repeat_factor']} 種只算 1 種，所以共有 {item['ordered_count']} ÷ {item['repeat_factor']} = {item['count']}（種）。")


def _group_partition(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    style, n, items = g.get("style", "rooms"), a["n"], a["items"]
    lines, steps = [], []
    if style == "rooms":
        it = items[0]
        if len(items) != 1 or not it["labeled"] or len(it["sizes"]) > 3:
            raise ValueError("rooms_style_shape")
        rooms = "ABC"[:len(it["sizes"])]
        alloc = "，".join(f"{r}房住 {_n(s)} 人" for r, s in zip(rooms, it["sizes"]))
        question = f"將 {_n(n)} 人分配住進{', '.join(rooms)}{_COUNT_ZH[len(rooms)]}間房間，{alloc}，共有多少種分配方案？"
        label, noun = ["分配方案數"], "間房"
    elif style == "classes":
        it = items[0]
        if len(items) != 1 or not it["labeled"]:
            raise ValueError("classes_style_shape")
        k = len(it["sizes"])
        classes = [f"{p}班" for p in _PEOPLE[:k]]
        alloc = _labeled_text(it["sizes"], classes, "人", "", "每班各")
        question = f"將 {_n(n)} 位轉學生分發到{'、'.join(_PEOPLE[:k])}{_COUNT_ZH[k]}班，{alloc}，共有多少種分法？"
        label, noun = ["分法數"], "班"
    elif style == "books":
        for it in items:
            k = len(it["sizes"])
            if it["labeled"]:
                names = list(_PEOPLE[:k])
                lines.append(f"分給{'、'.join(names)}{_COUNT_ZH[k]}人，{_labeled_text(it['sizes'], names, '本', '得', '每人各得')}。")
            elif len(set(it["sizes"])) == 1:
                lines.append(f"分裝入{_COUNT_ZH[k]}個相同的袋子，每袋裝 {_n(it['sizes'][0])} 本。")
            else:
                lines.append(f"分裝入{_COUNT_ZH[k]}個相同的袋子，{_unlabeled_text(it['sizes'], '袋', '本', '裝')}。")
        question = f"將 {_n(n)} 本不同的書依下列情形分配，方法各有多少種？\n" + _numbered(lines)
        label, noun = [f"({i}) 分配方法數" for i in range(1, len(items) + 1)], "份"
    elif style == "students":
        for it in items:
            if it["labeled"]:
                raise ValueError("students_style_groups_are_unlabeled")
            k = len(it["sizes"])
            if len(set(it["sizes"])) == 1:
                lines.append(f"平分成{_COUNT_ZH[k]}組。")
            else:
                lines.append(f"分成{_zh(k)}組，{_unlabeled_text(it['sizes'], '組', '人', '有')}。")
        question = f"將 {_n(n)} 位同學依下列情形分組，方法各有多少種？\n" + _numbered(lines)
        label, noun = [f"({i}) 分組方法數" for i in range(1, len(items) + 1)], "組"
    else:
        raise ValueError(f"unsupported_style:{style}")
    for i, it in enumerate(items, 1):
        unit = "袋" if (style == "books" and not it["labeled"]) else ("人" if style == "books" else noun)
        steps.append(_prefix(i, len(items)) + _partition_step(it, n, unit))
    return _items_payload(matrix, question, label, [it["count"] for it in items], steps, "group_partition")


# --- 5. combination_identity_select ------------------------------------------------------------------------------------------------------

def _lhs_latex(lhs: list[list[int]]) -> str:
    out = ""
    for sign, n, k in lhs:
        out += ("-" if sign < 0 else ("+" if out else "")) + _c(n, k)
    return out


_IDENTITY_REASON = {
    "symmetry": "由 {sym}，",
    "pascal": "由巴斯卡公式 {pascal}，",
    "pascal_diff": "由巴斯卡公式 {pascal}，移項得",
    "pascal_chain": "前兩項由巴斯卡公式合併，再與第三項合併，",
    "hockey_stick": "第一項 {first} 改寫為 {first_next}，再由巴斯卡公式逐項合併，",
}


def _combination_identity_select(matrix: dict[str, Any]) -> dict[str, Any]:
    sts = matrix["answer"]["statements"]
    lines, steps = [], []
    for i, st in enumerate(sts, 1):
        rn, rk = st["rhs"]
        big_n, big_k = st["identity"]
        lines.append(_t(_lhs_latex(st["lhs"]) + "=" + _c(rn, rk)))
        first = st["lhs"][0]
        reason = _IDENTITY_REASON[st["form"]].format(
            sym=_t("C_{k}^{n}=C_{n-k}^{n}"), pascal=_t("C_{k}^{n}+C_{k-1}^{n}=C_{k}^{n+1}"),
            first=_t(_c(first[1], first[2])), first_next=_t(_c(first[1] + 1, first[2])))
        if [rn, rk] == [big_n, big_k]:
            verdict = "恰為右式，正確。"
        elif [rn, rk] == [big_n, big_n - big_k]:
            verdict = f"又 {_t(_c(big_n, big_k) + '=' + _c(big_n, big_n - big_k))}，等於右式，正確。"
        else:
            verdict = f"而 {_t(_c(big_n, big_k) + '@neq ' + _c(rn, rk))}，所以錯誤。"
        steps.append(f"({i}) {reason}左式 = {_t(_c(big_n, big_k))}，{verdict}")
    selected = matrix["answer"]["selected"]
    steps.append("正確的選項為 " + "".join(f"({i})" for i in selected) + "。")
    question = "選出正確的選項。（多選題，請以逗號分隔選項編號作答）\n" + "\n".join(f"({i}){s}" for i, s in enumerate(lines, 1))
    part = _part(1, [str(i) for i in selected], *_SET, solution_members="exact_rational")
    return _single_payload(matrix, question=question, part=part, display_answer="".join(f"({i})" for i in selected), explanation_steps=steps,
                           shape="selected_candidate_index_set")


# --- 6. combination_claim ---------------------------------------------------------------------------------------------------------------

def _xy(a: int, b: int) -> str:
    def power(v: str, e: int) -> str:
        return "" if e == 0 else (v if e == 1 else f"{v}^{{{e}}}")
    return power("x", a) + power("y", b)


def _combination_claim(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    s, truth = g["setting"], a["truth"]
    if s["kind"] == "choose":
        n, k, c = s["n"], s["k"], g["claim"]
        shown = _c(c["n"], c["k"]) if c["form"] == "comb" else _p(c["n"], c["k"])
        sentence = f"從 {_n(n)} 個人中選出 {_n(k)} 人的組合數為 {_t(shown)}。"
        steps = [f"從 {n} 個人中選出 {k} 人（不計順序）的組合數為 {_t(_c(n, k))} = {a['left']}。",
                 f"而 {_t(shown)} = {a['right']}，" + ("兩者相等，所以敘述正確（○）。" if truth else
                                                      ("這是選出後再排列的排列數，" if c["form"] == "perm" else "") + "兩者不相等，所以敘述錯誤（×）。")]
    elif s["kind"] == "comb_times_factorial":
        n, k, m = s["n"], s["k"], s["m"]
        sentence = _t(f"{_c(n, k)}@times {m}!={_p(n, k)}") + "。"
        steps = [f"從 {n} 個中選 {k} 個排成一列，可以先選出 {k} 個（{_t(_c(n, k))} 種），再把這 {k} 個排列（{k}! 種），所以 {_t(_p(n, k) + '=' + _c(n, k) + '@times ' + str(k) + '!')}。",
                 ("這正是題中的式子，敘述正確（○）。" if truth else
                  f"題中乘的是 {m}!，而 {m}! = {math.factorial(m)} ≠ {k}! = {math.factorial(k)}，所以敘述錯誤（×）。")]
    elif s["kind"] == "comb_equal":
        n, x, y = s["n"], s["a"], s["b"]
        sentence = _t(f"{_c(n, x)}={_c(n, y)}") + "。"
        if truth:
            steps = [f"由 {_t('C_{k}^{n}=C_{n-k}^{n}')}，{_t(_c(n, x) + '=' + _c(n, n - x))}，而 {n} − {x} = {y}，所以敘述正確（○）。"]
        else:
            steps = [f"由 {_t('C_{k}^{n}=C_{n-k}^{n}')}，{_t(_c(n, x) + '=' + _c(n, n - x))}；組合數 {_t('C_{k}^{n}')} 只有在下標相等或兩下標的和為 {n} 時才會相等，"
                     f"而 {x} ≠ {y} 且 {x} + {y} ≠ {n}，所以敘述錯誤（×）。"]
    else:
        n, x, z = s["n"], s["a"], s["c"]
        sentence = f"在 {_t('@left(x+y@right)^{' + str(n) + '}')} 的展開式中，{_t(_xy(x, n - x))} 項的係數與 {_t(_xy(z, n - z))} 項的係數相等。"
        steps = [f"由二項式定理，{_t(_xy(x, n - x))} 項的係數為 {_t(_c(n, n - x))} = {a['left']}，{_t(_xy(z, n - z))} 項的係數為 {_t(_c(n, n - z))} = {a['right']}。",
                 "兩者相等，所以敘述正確（○）。" if truth else "兩者不相等，所以敘述錯誤（×）。"]
    return _truth_payload(matrix, _TF_HEAD + sentence, truth, steps, "single_choice")


# --- 7. pair_count -------------------------------------------------------------------------------------------------------------------------

def _pair_count(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    style = g.get("style", "faces")
    if a["mode"] == "count":
        n = a["n"]
        if style == "faces":
            question = (f"電腦可以將二張不同的人臉合成為一張新面孔。電視節目「最強大腦」選了 {_n(n)} 位藝人的臉，任意將每二位不同的臉都用電腦合成並印出一張新面孔。"
                        "請問總共印出幾張合成的新面孔？")
            label = "新面孔張數"
        elif style == "handshake":
            question = f"聚會中有 {_n(n)} 個人，若每兩個人都恰好握手一次，則總共握手多少次？"
            label = "握手次數"
        else:
            raise ValueError(f"unsupported_style:{style}")
        steps = [f"每取出兩個不同的對象（不計順序）就對應一次，所以共有 {_t(_c(n, 2))} = ({n}×{n - 1})/(2×1) = {a['count']}。"]
        return _single_value(matrix, question, a["count"], label, steps, "pair_count")
    t, n = a["total"], a["n"]
    if style != "round_robin":
        raise ValueError(f"unsupported_style:{style}")
    question = f"桌球比賽中，若規定參與的選手每人都必須和其他選手各比賽一場，賽程總計為 {_n(t)} 場，則選手共有多少人？"
    steps = [f"設選手有 n 人，每兩人比賽一場，共 {_t('C_{2}^{n}=@frac{n(n-1)}{2}')} 場。",
             f"由 {_t('@frac{n(n-1)}{2}=' + str(t))} 得 n(n − 1) = {2 * t} = {n}×{n - 1}，又 n 為正整數，所以 n = {n}（人）。"]
    return _single_value(matrix, question, n, "選手人數", steps, "pair_count_solve")


# --- 8. sequential_selection -------------------------------------------------------------------------------------------------------------

_TASKS = ("掃地", "拖地", "擦窗戶")


def _sequential_selection(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    n, ks = a["n"], a["ks"]
    if len(ks) > len(_TASKS):
        raise ValueError("too_many_tasks")
    picks = [f"選 {_n(ks[0])} 人{_TASKS[0]}"] + [f"另選 {_n(k)} 人{task}" for k, task in zip(ks[1:], _TASKS[1:])]
    question = f"從 {_n(n)} 人中{'，'.join(picks)}，共有幾種選法？"
    chain = [f"{'先' if i == 0 else '再'}從 {st['from']} 人中選 {st['k']} 人{_TASKS[i]}，有 {_t(_c(st['from'], st['k']))} = {st['ways']} 種"
             for i, st in enumerate(a["steps"])]
    steps = ["；".join(chain) + "。", "乘法原理：" + "×".join(str(st["ways"]) for st in a["steps"]) + f" = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], "選法數", steps, "sequential_selection")


# --- 9. gender_committee -------------------------------------------------------------------------------------------------------------------

def _gender_committee(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    b, g, p = a["boys"], a["girls"], a["pick"]
    lines, steps = [], []
    for i, it in enumerate(a["items"], 1):
        kind = it["kind"]
        if kind == "exact":
            lines.append(f"恰為 {_n(it['boys'])} 男 {_n(it['girls'])} 女。")
            body = f"從男生選 {it['boys']} 人、女生選 {it['girls']} 人：{_t(_c(b, it['boys']) + '@times ' + _c(g, it['girls']))} = {math.comb(b, it['boys'])}×{math.comb(g, it['girls'])} = {it['count']}（種）。"
        elif kind == "at_least_one_girl":
            lines.append(f"至少有 {_n(1)} 名女生。")
            body = f"全部選法 {_t(_c(b + g, p))} = {it['total']}，扣除全為男生 {_t(_c(b, p))} = {it['none']}，得 {it['count']}（種）。"
        elif kind == "at_least_one_boy":
            lines.append(f"至少有 {_n(1)} 名男生。")
            body = f"全部選法 {_t(_c(b + g, p))} = {it['total']}，扣除全為女生 {_t(_c(g, p))} = {it['none']}，得 {it['count']}（種）。"
        else:
            lines.append(f"男女生至少各 {_n(1)} 名。")
            body = (f"全部選法 {_t(_c(b + g, p))} = {it['total']}，扣除全為男生 {_t(_c(b, p))} = {it['only_boys']} 與全為女生 {_t(_c(g, p))} = {it['only_girls']}，"
                    f"得 {it['count']}（種）。")
        steps.append(_prefix(i, len(a["items"])) + body)
    question = f"從 {_n(b)} 位男生、{_n(g)} 位女生中選派 {_n(p)} 人參加社區服務，下列情形的選派方法各有多少種？\n" + _numbered(lines)
    return _items_payload(matrix, question, [f"({i}) 選派方法數" for i in range(1, len(lines) + 1)], [it["count"] for it in a["items"]], steps,
                          "gender_committee")


# --- 10. paired_group_assignment -----------------------------------------------------------------------------------------------------------

def _paired_group_assignment(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    t, s, per = a["teachers"], a["students"], a["per_group"]
    sites = "、".join(_PEOPLE[:t])
    question = (f"將 {_n(t)} 名教師、{_n(s)} 名學生分成 {_n(t)} 組，每組由 {_n(1)} 名教師和 {_n(per)} 名學生組成，"
                f"分別安排到{sites}{_COUNT_ZH[t]}地參加活動，共有多少種分配方法？")
    chain = [f"{_PEOPLE[i]}地：從 {x['teachers']} 名教師選 1 名、從 {x['students_from']} 名學生選 {per} 名，有 {x['teachers']}×{_t(_c(x['students_from'], per))} = {x['ways']} 種"
             for i, x in enumerate(a["sites"])]
    steps = ["依序安排各地：" + "；".join(chain) + "。", "乘法原理：" + "×".join(str(x["ways"]) for x in a["sites"]) + f" = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], "分配方法數", steps, "paired_group_assignment")


# --- 11. surjective_distribution ----------------------------------------------------------------------------------------------------------

def _surjective_distribution(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    n, m = a["people"], a["places"]
    question = f"將 {_n(n)} 名大學生分配到 {_n(m)} 個村落服務，每個村落至少 {_n(1)} 名，共有多少種分配方法？"
    if a["method"] == "bijection":
        steps = [f"人數與村落數相同，每個村落恰 1 名，相當於 {n} 人的直線排列：{n}! = {a['count']}（種）。"]
    elif a["method"] == "pair":
        steps = [f"{n} 人分到 {m} 個村落且每村至少 1 人，必有一村 2 人、其餘各 1 人。",
                 f"先選出同村的 2 人：{_t(_c(n, 2))} = {math.comb(n, 2)} 種；再把這 {m} 組分到 {m} 個村落：{m}! = {math.factorial(m)} 種。",
                 f"乘法原理：{math.comb(n, 2)}×{math.factorial(m)} = {a['count']}（種）。"]
    else:
        expr = " ".join(("+ " if x["sign"] > 0 and x["j"] else ("− " if x["sign"] < 0 else "")) + f"{_t(_c(m, x['j']))}×{m - x['j']}^{n}"
                        for x in a["terms"] if x["j"] < m)
        steps = [f"每人有 {m} 種去處，共 {m}^{n} 種；用取捨原理扣除有村落沒人的情形：{expr} = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], "分配方法數", steps, "surjective_distribution")


# --- 12. parity_sum_selection --------------------------------------------------------------------------------------------------------------

def _parity_sum_selection(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    t, p = a["top"], a["pick"]
    word = "偶數" if a["parity"] == "even" else "奇數"
    listed = ", ".join(str(i) for i in range(1, t + 1))
    question = f"從{listed}這{_zh(t)}個數中，同時取出 {_n(p)} 個不同的數，且其和為{word}，共有多少種取法？"
    cases = "；".join(f"取 {c['odd']} 個奇數、{c['even']} 個偶數：{_t(_c(a['odd_count'], c['odd']) + '@times ' + _c(a['even_count'], c['even']))} = {c['ways']} 種"
                      for c in a["cases"])
    steps = [f"其中奇數有 {a['odd_count']} 個、偶數有 {a['even_count']} 個。和為{word}，取出的奇數個數必須是{'偶數' if a['parity'] == 'even' else '奇數'}。",
             cases + "。", "加法原理：" + " + ".join(str(c["ways"]) for c in a["cases"]) + f" = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], "取法數", steps, "parity_sum_selection")


# --- 13. multiset_select_arrange ----------------------------------------------------------------------------------------------------------

def _pattern_name(pattern: list[int], r: int) -> str:
    if max(pattern) == 1:
        return f"{_zh(r)}個字母皆相異"
    parts = []
    for c in sorted(set(pattern), reverse=True):
        if c > 1:
            parts.append(f"{pattern.count(c)} 種字母各取 {c} 個" if pattern.count(c) > 1 else f"某字母取 {c} 個")
    singles = pattern.count(1)
    return "、".join(parts) + (f"，另 {singles} 個相異字母" if singles else "")


def _multiset_select_arrange(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    w, r = a["word"], a["pick"]
    question = f"從「{w}」一字共 {_n(a['length'])} 個字母中，任選 {_n(r)} 個字母排成一列，共有多少種排法？"
    repeated = "、".join(f"{ch} 有 {c} 個" for ch, c in a["letters"].items() if c > 1)
    singles = ", ".join(ch for ch, c in a["letters"].items() if c == 1)
    steps = [f"字母中{repeated}" + (f"，{singles} 各 1 個" if singles else "") + f"，依選出字母的重複情形分類："]
    for c in a["cases"]:
        steps.append(f"「{_pattern_name(c['pattern'], r)}」：選字母有 {c['selections']} 種，每種的排法有 {c['arrangements_each']} 種，共 {c['ways']} 種。")
    steps.append("加法原理：" + " + ".join(str(c["ways"]) for c in a["cases"]) + f" = {a['count']}（種）。")
    return _single_value(matrix, question, a["count"], "排法數", steps, "multiset_select_arrange")


# --- 14. binomial_expansion ---------------------------------------------------------------------------------------------------------------

def _linear_term(c: int, v: str, lead: bool) -> str:
    mag = "" if abs(c) == 1 else str(abs(c))
    sign = "-" if c < 0 else ("" if lead else "+")
    return f"{sign}{mag}{v}"


def _binomial_expansion(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    x, y = a["vars"]
    n = a["n"]
    base = _linear_term(a["a"], x, True) + _linear_term(a["b"], y, False)
    question = f"寫出 {_t('@left(' + base + '@right)^{' + str(n) + '}')} 的展開式。"
    latex = polynomial_latex(a["terms"])
    first = x if a["a"] == 1 else f"({_linear_term(a['a'], x, True)})"
    second = y if a["b"] == 1 else f"({_linear_term(a['b'], y, True)})"
    general = f"{_t(_c(n, 'r'))}{first}^({n}−r){second}^r"
    steps = [f"利用二項式定理，展開式的每一項為 {general}，r = 0, 1, …, {n}。",
             "依序代入：" + "、".join(f"r={r}：{_t(_c(n, r))}×{_par(a['a'])}^{n - r}×{_par(a['b'])}^{r} = {c}" for r, c in enumerate(a["coefficients"])) + "。",
             f"所以 {_t('@left(' + base + '@right)^{' + str(n) + '}=' + latex)}。"]
    part = _part(1, a["plain"], *_EXPANDED, required_form="expanded", label="展開式", prompt="展開式")
    return _single_payload(matrix, question=question, part=part, display_answer=_t(latex), explanation_steps=steps, shape="expanded_polynomial")


# --- 15. radical_binomial_power ----------------------------------------------------------------------------------------------------------

def _radical_binomial_power(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    p, c, n = a["radicand"], a["constant"], a["n"]
    root = f"@sqrt{{{p}}}"
    base = (f"{root}{'+' if c > 0 else '-'}{abs(c)}" if g.get("order", "root_first") == "root_first"
            else f"{c}+{root}")
    question = f"已知 {_t('@left(' + base + '@right)^{' + str(n) + '}=a+b' + root)}（其中a, b為整數），求a, b的值。"
    terms = " + ".join(f"{_t(_c(n, t['r']))}({_t(root)})^{t['root_power']}({c})^{t['r']}" for t in a["terms"])
    even = _sum_text([t["value"] for t in a["terms"] if not t["radical"]])
    odd = _sum_text([t["value"] for t in a["terms"] if t["radical"]])
    steps = [f"由二項式定理，原式 = {terms}。",
             f"(√{p})^k 中 k 為偶數的項是整數，k 為奇數的項是 √{p} 的整數倍：整數部分 {even} = {a['a']}；√{p} 的係數 {odd} = {a['b']}。",
             f"所以 a = {a['a']}，b = {a['b']}。"]
    parts = [_value_part(1, a["a"], "a"), _value_part(2, a["b"], "b")]
    parts[0]["label"], parts[1]["label"] = "a", "b"
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"a = {a['a']}，b = {a['b']}", explanation_steps=steps,
                          shape="radical_binomial_power")


# --- 16. general_term_coefficient ---------------------------------------------------------------------------------------------------------

def _x_power(e: int) -> str:
    return "" if e == 0 else ("x" if e == 1 else f"x^{{{e}}}")


def _general_term_coefficient(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    c1, p1, c2, p2, n = (int(g[k]) for k in ("c1", "p1", "c2", "p2", "n"))
    t, r = a["target"], a["r"]
    first = ("-" if c1 < 0 else "") + ("" if abs(c1) == 1 else str(abs(c1))) + _x_power(p1)
    second = ("-" if c2 < 0 else "+") + f"@frac{{{abs(c2)}}}{{{_x_power(-p2)}}}"
    expr = f"@left({first}{second}@right)^{{{n}}}"
    if t == 0:
        question = f"求 {_t(expr)} 展開式中的常數項。"
        label, what = "常數項", "常數項"
    else:
        question = f"求 {_t(expr)} 展開式中 {_t(_x_power(t))} 項的係數。"
        label, what = "係數", f"{_t(_x_power(t))} 項的係數"
    top, step = a["general_exponent"]
    steps = [f"展開式的每一項皆形如 {_t(_c(n, 'r'))}({_t(first)})^({n}−r)({_t(second.lstrip('+'))})^r = {_t(_c(n, 'r'))}×({c1})^({n}−r)×({c2})^r×{_t('x^{' + str(top) + '-' + str(step) + 'r}')}。",
             f"令 {top} − {step}r = {t}，得 r = {r}。",
             f"所以{what}為 {_t(_c(n, r))}×({c1})^{n - r}×({c2})^{r} = {math.comb(n, r)}×{_par(c1 ** (n - r))}×{_par(c2 ** r)} = {a['coefficient']}。"]
    return _single_value(matrix, question, a["coefficient"], label, steps, "general_term_coefficient")


# --- 17. at_least_k_selection ----------------------------------------------------------------------------------------------------------------

def _at_least_k_selection(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    n, k = a["n"], a["k"]
    question = f"總經理要求宣傳部的 {_n(n)} 名員工，至少派出 {_n(k)} 人到電影街宣傳新產品，共有多少種選派方案？"
    total = f"{_t(_c(n, 0) + '+' + _c(n, 1) + '+@cdots +' + _c(n, n) + '=2^{' + str(n) + '}')}"
    if a["method"] == "half_even":
        h = n // 2
        steps = [f"派出 j 人與派出 {n} − j 人的方案數相同（{_t('C_{j}^{' + str(n) + '}=C_{' + str(n) + '-j}^{' + str(n) + '}')}），而全部方案數為 {total}。",
                 f"扣除恰派出 {h} 人的 {_t(_c(n, h))} = {math.comb(n, h)} 種後，「多於 {h} 人」與「少於 {h} 人」各占一半。",
                 f"所以至少派出 {k} 人的方案共有 ({2 ** n} − {math.comb(n, h)}) ÷ 2 = {a['count']}（種）。"]
    elif a["method"] == "half":
        steps = [f"派出的人數可為 {k}, {k + 1}, …, {n}，方案數為 {_t(_c(n, k) + '+@cdots +' + _c(n, n))}。",
                 f"由 {_t('C_{j}^{' + str(n) + '}=C_{' + str(n) + '-j}^{' + str(n) + '}')}，此和等於 {_t(_c(n, 0) + '+@cdots +' + _c(n, n - k))}，兩者相加正好是 {total}。",
                 f"所以選派方案共有 2^{n} ÷ 2 = 2^{n - 1} = {a['count']}（種）。"]
    else:
        excluded = " + ".join(str(v) for v in a["excluded"])
        steps = [f"派出 0 到 {n} 人的全部方案數為 {total} = {2 ** n}。",
                 f"扣除派出少於 {k} 人的方案：{_t('+'.join(_c(n, j) for j in range(k)))} = {excluded} = {sum(a['excluded'])}。",
                 f"所以選派方案共有 {2 ** n} − {sum(a['excluded'])} = {a['count']}（種）。"]
    return _single_value(matrix, question, a["count"], "選派方案數", steps, "at_least_k_selection")


# --- 18. binomial_sum_bound ---------------------------------------------------------------------------------------------------------------

def _binomial_sum_bound(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    lo, hi, s, n = a["low"], a["high"], a["start"], a["n"]
    series = "+".join(_c("n", j) for j in range(s, s + 3)) + "+@cdots +" + _c("n", "n")
    question = f"求滿足不等式 {_t(str(lo) + '<' + series + '<' + str(hi))} 的正整數n。"
    value = "2^{n}-1" if s == 1 else "2^{n}"
    steps = [f"由 {_t('C_{0}^{n}+C_{1}^{n}+@cdots +C_{n}^{n}=2^{n}')}，得 {_t(series + '=' + value)}。",
             f"不等式化為 {_t(str(lo) + '<' + value + '<' + str(hi))}。",
             f"因為 2^{n - 1}{' − 1' if s else ''} = {2 ** (n - 1) - s}、2^{n}{' − 1' if s else ''} = {2 ** n - s}、2^{n + 1}{' − 1' if s else ''} = {2 ** (n + 1) - s}，"
             f"只有 n = {n} 符合，所以 n = {n}。"]
    return _single_value(matrix, question, n, "n", steps, "binomial_sum_bound")


# --- 19. coefficient_solve_parameter ----------------------------------------------------------------------------------------------------

def _coefficient_solve_parameter(matrix: dict[str, Any]) -> dict[str, Any]:
    a = matrix["answer"]
    n, m, v = a["n"], a["m"], a["value"]
    question = f"已知 {_t('@left(1+ax@right)@left(1+x@right)^{' + str(n) + '}')} 的展開式中 {_t(_x_power(m))} 項的係數為 {_n(v)}，求實數a的值。"
    steps = [f"{_t('@left(1+x@right)^{' + str(n) + '}')} 中 {_t(_x_power(m))} 項的係數為 {_t(_c(n, m))} = {a['base']}，{_t(_x_power(m - 1) or '1')} 項的係數為 {_t(_c(n, m - 1))} = {a['slope']}。",
             f"相乘後 {_t(_x_power(m))} 項由「1 × {_t(_c(n, m) + _x_power(m))}」與「ax × {_t(_c(n, m - 1) + _x_power(m - 1))}」組成，係數為 {a['base']} + {a['slope']}a。",
             f"由 {a['base']} + {a['slope']}a = {v}，得 a = {a['a']}。"]
    return _single_value(matrix, question, a["a"], "a", steps, "coefficient_solve_parameter")


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "combination_evaluate": _combination_evaluate,
    "select_with_members": _select_with_members,
    "mixed_group_ordered": _mixed_group_ordered,
    "group_partition": _group_partition,
    "combination_identity_select": _combination_identity_select,
    "combination_claim": _combination_claim,
    "pair_count": _pair_count,
    "sequential_selection": _sequential_selection,
    "gender_committee": _gender_committee,
    "paired_group_assignment": _paired_group_assignment,
    "surjective_distribution": _surjective_distribution,
    "parity_sum_selection": _parity_sum_selection,
    "multiset_select_arrange": _multiset_select_arrange,
    "binomial_expansion": _binomial_expansion,
    "radical_binomial_power": _radical_binomial_power,
    "general_term_coefficient": _general_term_coefficient,
    "at_least_k_selection": _at_least_k_selection,
    "binomial_sum_bound": _binomial_sum_bound,
    "coefficient_solve_parameter": _coefficient_solve_parameter,
}


def adapt_combinations_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_combinations_operation:{operation}")
    return builder(matrix)
