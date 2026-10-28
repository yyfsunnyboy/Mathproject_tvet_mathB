"""Question payload contracts for discrete.sets_counting (普高數學2 Unit 3 計數原理).

Every expected answer comes from the domain matrix, never from this adapter.  Stems are rebuilt from the same stated data the domain
solved, so a varied question always carries its own numbers.  Figures: the textbook picture is the reviewed crop reused by the practice
route (``reuse_textbook_image``).  A figure is attached only when the stated data *is* the figure's structure (the path graph of 隨堂練習6,
the L-shaped region of 進階題8); any other data is refused so a figure can never disagree with the answer.
"""

from __future__ import annotations

import math
from typing import Any, Callable

import sympy as sp

from .counting_sets_domain import CLAIMS, DOMAIN_KEY, FACTS, multiples_among_divisors

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
CONDITION_CHOICES = ({"label": "A", "value": "充分"}, {"label": "B", "value": "必要"}, {"label": "C", "value": "充要"})
_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_SET = ("solution_set_checker", "unordered_solution_set", "solution_set")
_INEQ = ("inequality_solution_checker", "inequality_solution_equivalence", "inequality")
_SET_EXAMPLES = ("2, 5", "3, 8", "-1, 4", "6, 11", "-3, 7", "10, 13", "12, 15", "-4, 9", "14, 17", "-6, 20")
_INTERVAL_EXAMPLES = ("0<x<=5", "-2<=x<4", "x<=-3 or x>7", "x>6", "-9<x<-6", "x<-8")
_ZH = {2: "二", 3: "三", 4: "四", 5: "五"}

# the textbook figures: structure the stated data must equal for the reviewed crop to be attached
FIGURE_GRAPH_VERTICES = ("A", "B", "C", "D")
FIGURE_GRAPH_EDGES = frozenset(frozenset(e) for e in ("AB", "AD", "BC", "CD", "BD"))
FIGURE_REGION_CELLS = frozenset([(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (0, 1)])

_ITEM_TEX = {"intersection": "A@cap B", "union": "A@cup B", "a_minus_b": "A-B", "b_minus_a": "B-A", "a_complement": "A'", "b_complement": "B'"}
_ITEM_TEXT = {"intersection": "A∩B", "union": "A∪B", "a_minus_b": "A−B", "b_minus_a": "B−A", "a_complement": "A′", "b_complement": "B′"}


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


def _value_part(index: int, value: Any, label: str) -> dict[str, Any]:
    return _part(index, str(value), *_RATIONAL, label=label, prompt=label)


def _set_part(index: int, members: list[int], label: str, avoid=()) -> dict[str, Any]:
    """A value set.  The format hint is shown before submitting, so it is a fixed illustration sharing no value with the answer and, when
    ``avoid`` is given (the stated universe / sets / option numbers), none with anything the student is choosing from: it never eliminates a candidate."""
    answer = {int(m) for m in members}
    pool = answer | {int(v) for v in avoid}
    shown = next((e for e in _SET_EXAMPLES if not ({int(x) for x in e.split(",")} & pool)), None) \
        or next(e for e in _SET_EXAMPLES if not ({int(x) for x in e.split(",")} & answer))
    return _part(index, [str(m) for m in members], *_SET, solution_members="exact_rational", answer_format_example=shown, label=label, prompt=label)


def _choice_part(index: int, expected_label: str, choices, label: str = "") -> dict[str, Any]:
    extra = {"label": label, "prompt": label} if label else {}
    return _part(index, expected_label, "choice_label_checker", "choice_label", "single_choice", choices=[dict(c) for c in choices], **extra)


def _ineq_parts(canonicals: list[str], labels: list[str]) -> list[dict[str, Any]]:
    shown = next(e for e in _INTERVAL_EXAMPLES if e not in canonicals)
    return [_part(i, c, *_INEQ, answer_format_example=shown, label=label, prompt=label) for i, (c, label) in enumerate(zip(canonicals, labels), 1)]


def _pretty(canonical: str) -> str:
    return canonical.replace("<=", "≤").replace(">=", "≥").replace(" or ", " 或 ")


def _set_text(members: list[int]) -> str:
    return "{" + ", ".join(str(m) for m in members) + "}"


def _numbered(lines: list[str]) -> str:
    return "\n".join(f"({i}){line}" for i, line in enumerate(lines, 1))


# --- 1. interval_set_operations -------------------------------------------------------------------------------------------------

def _interval_cond(spec: dict[str, Any]) -> str:
    left = "@le " if spec.get("lc", True) else "<"
    right = "@le " if spec.get("hc", True) else "<"
    return str(spec["lo"]) + left + "x" + right + str(spec["hi"])


def _interval_set_operations(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    def declare(name: str) -> str:
        return _t(name + "=@{x@mid " + _interval_cond(g[name]) + ",@ x@in @mathbb{R}@}")
    items = [it["item"] for it in a["items"]]
    question = ("已知宇集為實數 " + _t("@mathbb{R}") + "、" + declare("A") + "、" + declare("B") + "，求下列各集合。（以不等式表示答案）\n"
                + "\n".join(f"({i}) {_t(_ITEM_TEX[item])}。" for i, item in enumerate(items, 1)))
    parts = _ineq_parts([it["canonical"] for it in a["items"]], [f"({i}) {_ITEM_TEXT[item]}" for i, item in enumerate(items, 1)])
    steps = ["在數線上標示 A 與 B 的範圍，再依集合運算的定義逐項求解（交集取共同部分、聯集取全部、差集取屬於前者而不屬於後者、補集取宇集中不屬於它的部分）。"]
    steps += [f"({i}) {_ITEM_TEXT[it['item']]} = {{x | {_pretty(it['canonical'])}, x∈ℝ}}。" for i, it in enumerate(a["items"], 1)]
    return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(f"({i}){_pretty(it['canonical'])}" for i, it in enumerate(a["items"], 1)),
                          explanation_steps=steps, shape="interval_set_operations")


# --- 2. finite_set_operations ---------------------------------------------------------------------------------------------------

def _finite_set_operations(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    items = [it["item"] for it in a["items"]]
    if g.get("universe") is not None:
        question = ("已知宇集 " + _t("U=@{" + ",@ ".join(str(v) for v in g["universe"]) + "@}") + "、" + _t("A=@{" + ",@ ".join(str(v) for v in g["A"]) + "@}")
                    + "、" + _t("B=@{" + ",@ ".join(str(v) for v in g["B"]) + "@}") + "，求下列各集合。\n"
                    + "\n".join(f"({i}) {_t(_ITEM_TEX[item])}。" for i, item in enumerate(items, 1)))
    else:
        names = "、".join(_t(_ITEM_TEX[item]) for item in items[:-1]) + " 及 " + _t(_ITEM_TEX[items[-1]])
        question = ("已知集合 " + _t("A=@{" + ",@ ".join(str(v) for v in g["A"]) + "@}") + "、" + _t("B=@{" + ",@ ".join(str(v) for v in g["B"]) + "@}")
                    + "，求 " + names + "。")
    stated = [*g["A"], *g["B"], *(g.get("universe") or [])]
    parts = [_set_part(i, it["members"], f"({i}) {_ITEM_TEXT[it['item']]}（元素用逗號分開）", avoid=stated) for i, it in enumerate(a["items"], 1)]
    steps = [f"({i}) {_ITEM_TEXT[it['item']]} = {_set_text(it['members'])}。" for i, it in enumerate(a["items"], 1)]
    return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(f"({i}){_set_text(it['members'])}" for i, it in enumerate(a["items"], 1)),
                          explanation_steps=steps, shape="finite_set_operations")


# --- 3. equation_root_sets ------------------------------------------------------------------------------------------------------

def _equation_text(spec: dict[str, Any]) -> str:
    if spec["kind"] == "square":
        return "x^{2}=" + str(spec["rhs"])
    b, c = int(spec["b"]), int(spec["c"])
    middle = "" if b == 0 else ("+" if b > 0 else "-") + ("" if abs(b) == 1 else str(abs(b))) + "x"
    tail = "" if c == 0 else ("+" if c > 0 else "-") + str(abs(c))
    return "x^{2}" + middle + tail + "=0"


def _equation_root_sets(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    def declare(name: str) -> str:
        return _t(name + "=@{x@mid " + _equation_text(g[name]) + ",@ x@in @mathbb{R}@}")
    items = [it["item"] for it in a["items"]]
    question = "已知集合 " + declare("A") + "、" + declare("B") + "，求 " + " 與 ".join(_t(_ITEM_TEX[item]) for item in items) + "。"
    parts = [_set_part(i, it["members"], f"({i}) {_ITEM_TEXT[it['item']]}（元素用逗號分開）", avoid=[*a["A"], *a["B"]]) for i, it in enumerate(a["items"], 1)]
    steps = [f"解方程式：A = {_set_text(a['A'])}、B = {_set_text(a['B'])}。"]
    steps += [f"({i}) {_ITEM_TEXT[it['item']]} = {_set_text(it['members'])}。" for i, it in enumerate(a["items"], 1)]
    return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(f"({i}){_set_text(it['members'])}" for i, it in enumerate(a["items"], 1)),
                          explanation_steps=steps, shape="equation_root_sets")


# --- 4. proposition_truth ----------------------------------------------------------------------------------------------------------

_REL_TEX = {">": ">", "<": "<", ">=": "@ge ", "<=": "@le ", "=": "="}
_NAMES = "PQR"


def _atom_text(atom: dict[str, Any]) -> str:
    kind = atom["kind"]
    if kind == "fact":
        return FACTS[atom["id"]][0]
    if kind == "compare":
        return _t(str(atom["a"]) + _REL_TEX[atom["op"]] + str(atom["b"]))
    prop = atom["prop"]
    if prop == "multiple_of":
        return f"{_n(atom['n'])} 是 {_n(atom['k'])} 的倍數"
    return f"{_n(atom['n'])} 是" + {"prime": "質數", "even": "偶數", "odd": "奇數"}[prop]


def _atom_reason(atom: dict[str, Any], truth: bool) -> str:
    return f"{_atom_text(atom)}（{'真' if truth else '假'}）"


def _option_text(option: list[Any], names: list[str]) -> str:
    kind = option[0]
    if kind == "atom":
        return names[option[1]]
    if kind == "not":
        return "非" + names[option[1]]
    return names[option[1]] + ("且" if kind == "and" else "或") + names[option[2]]


def _proposition_truth(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    atoms, options = g["atoms"], g["options"]
    if g["mode"] == "truth":
        option = options[0]
        joiner = {"and": " 且 ", "or": " 或 "}[option[0]]
        sentence = "「" + joiner.join(_atom_text(atoms[i]) for i in option[1:]) + "」是正確的命題。"
        truth = a["truths"][0]
        question = "下列敘述對的打「○」，錯的打「×」。\n" + sentence
        why = "；".join(_atom_reason(atoms[i], a["atom_truths"][i]) for i in option[1:])
        rule = "「且」要兩個都為真才為真" if option[0] == "and" else "「或」只要有一個為真就為真"
        steps = [f"{why}。{rule}，所以這個命題為{'真' if truth else '假'}，敘述為「{'○' if truth else '×'}」。"]
        return _single_payload(matrix, question=question, part=_choice_part(1, "A" if truth else "B", TRUE_FALSE_CHOICES),
                               display_answer="○" if truth else "×", explanation_steps=steps, shape="single_choice")
    names = list(_NAMES[:len(atoms)])
    defs = "，".join(f"{n}：{_atom_text(at)}" for n, at in zip(names, atoms))
    question = (f"設 {_t(', '.join(names))} 為{'三' if len(atoms) == 3 else str(len(atoms))}個命題：\n{defs}。\n在下列選項中，選出正確的命題。\n"
                + " ".join(f"({i}) {_option_text(o, names)}" for i, o in enumerate(options, 1)) + "。")
    steps = ["；".join(f"{n}（{'真' if t else '假'}）" for n, t in zip(names, a["atom_truths"])) + "。"]
    steps += [f"({i}) {_option_text(o, names)}：{'正確' if t else '錯誤'}。" for i, (o, t) in enumerate(zip(options, a["truths"]), 1)]
    part = _set_part(1, a["selected"], "正確的選項編號（用逗號分開）", avoid=range(1, len(options) + 1))  # the hint never names an option
    return _single_payload(matrix, question=question, part=part, display_answer="".join(f"({i})" for i in a["selected"]),
                           explanation_steps=steps, shape="selected_option_index_set")


# --- 5. implication_truth ---------------------------------------------------------------------------------------------------------

_CLAIM_WHY = {
    "ab0_or": "兩個實數的乘積為 0，其中至少有一個為 0。", "sq_pm": "由 a²=b² 得 (a−b)(a+b)=0，所以 a=b 或 a=−b。",
    "sum_pos_or": "若 a、b 都不大於 0，則 a+b 不大於 0；所以 a+b>0 時至少有一個大於 0。", "both_pos_prod": "正數乘正數仍是正數。",
    "sq_sum_zero": "實數的平方不小於 0，兩個平方和為 0 只有兩個平方都為 0。", "prod_nonzero": "乘積不為 0，則任何一個因數都不為 0。",
    "eq_sq": "a=b 時兩邊同時平方，得 a²=b²。",
}


def _claim_tex(text: str) -> str:
    out, buf = [], ""
    for ch in text:
        if ch in "且或":
            out.append(_t(buf))
            out.append(" " + ch + " ")
            buf = ""
        else:
            buf += ch
    out.append(_t(buf))
    return "".join(out)


def _implication_truth(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    claim = CLAIMS[g["claim"]]
    truth = a["truth"]
    question = "下列敘述對的打「○」，錯的打「×」。\n若實數 " + _t("a,@ b") + " 滿足 " + _claim_tex(claim["hyp"]) + "，則 " + _claim_tex(claim["concl"]) + "。"
    if truth:
        reason = _CLAIM_WHY[g["claim"]]
    else:
        ca, cb = a["counterexample"]
        reason = f"取 a={ca}、b={cb}，條件成立但結論不成立（反例），所以敘述錯誤。"
    steps = [f"{reason}此敘述為「{'○' if truth else '×'}」。"]
    return _single_payload(matrix, question=question, part=_choice_part(1, "A" if truth else "B", TRUE_FALSE_CHOICES),
                           display_answer="○" if truth else "×", explanation_steps=steps, shape="single_choice")


# --- 6. condition_relation ----------------------------------------------------------------------------------------------------------

def _cond_tex(cond: dict[str, Any]) -> str:
    v = cond["c"]
    return {"eq": f"x={v}", "abs_eq": f"|x|={v}", "sq_eq": f"x^{{2}}={v}", "gt": f"x>{v}", "ge": f"x@ge {v}", "lt": f"x<{v}", "le": f"x@le {v}"}[cond["kind"]]


def _cond_solution(cond: dict[str, Any]) -> str:
    v = int(cond["c"])
    return {"eq": "{" + str(v) + "}", "abs_eq": "{" + (f"-{v}, {v}" if v > 0 else "0") + "}", "sq_eq": "{" + f"-{math.isqrt(v)}, {math.isqrt(v)}" + "}",
            "gt": f"x>{v}", "ge": f"x≥{v}", "lt": f"x<{v}", "le": f"x≤{v}"}[cond["kind"]]


def _condition_relation(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    p, q = _cond_tex(g["cond"]), _cond_tex(g["target"])
    question = f"「{_t(p)}」是「{_t(q)}」的 ＿＿ 條件。（選出充分、必要或充要）"
    sp_, sq_ = _cond_solution(g["cond"]), _cond_solution(g["target"])
    rel = {"sufficient": f"前者的解 {sp_} 完全包含在後者的解 {sq_} 之內，前者成立時後者必成立，但反過來不一定，所以是充分條件。",
           "necessary": f"後者的解 {sq_} 完全包含在前者的解 {sp_} 之內，後者成立時前者必成立，但反過來不一定，所以是必要條件。",
           "iff": f"兩者的解相同（{sp_}），互為充分也互為必要，所以是充要條件。"}[a["relation"]]
    label = {"sufficient": "A", "necessary": "B", "iff": "C"}[a["relation"]]
    return _single_payload(matrix, question=question, part=_choice_part(1, label, CONDITION_CHOICES), display_answer=a["label"],
                           explanation_steps=[rel], shape="single_choice")


# --- 7. choice_product / grade_selection -----------------------------------------------------------------------------------------------

_MENU_NAMES = {"主菜": ["牛排", "豬排", "雞排", "羊排", "魚排", "鴨排"], "湯": ["玉米湯", "海鮮湯", "蔬菜湯", "南瓜湯", "酸辣湯"], "飲料": ["咖啡", "紅茶", "奶茶", "果汁"]}


def _join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else "、".join(names[:-1]) + "與" + names[-1]


def _product_expr(counts: list[int]) -> str:
    return "×".join(str(c) for c in counts)


def _choice_product(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    groups, style = g["groups"], g.get("style", "menu")
    counts = a["counts"]
    if style == "menu":
        labels = [grp["label"] for grp in groups]
        clauses = []
        for grp in groups:
            bank = _MENU_NAMES[grp["label"]]
            if grp["count"] > len(bank) or grp["count"] < 2:
                raise ValueError("menu_group_size")
            clauses.append(f"{grp['label']}有{_join(bank[:grp['count']])} {_n(grp['count'])} 種")
        question = "餐廳的" + "；".join(clauses) + "。每位客人須從" + "、".join(labels[:-1]) + "及" + labels[-1] + "各任選一種。請問共有多少種點餐方式？"
        steps = [f"分 {len(groups)} 個步驟點餐：" + "；".join(f"第 {i} 步驟選{grp['label']}，有 {grp['count']} 種選法" for i, grp in enumerate(groups, 1))
                 + f"。利用乘法原理，點餐方式共有 {_product_expr(counts)} = {a['total']}（種）。"]
    elif style == "staff":
        first, second = groups
        question = (f"醫院有{first['label']} {_n(first['count'])} 名，{second['label']} {_n(second['count'])} 名。若要{first['label'][:2]}與{second['label'][:2]}各推派一位醫師參加義診，"
                    "則共有多少種推派方案？")
        steps = [f"分兩個步驟推派：{first['label']}有 {first['count']} 種選法，{second['label']}有 {second['count']} 種選法。利用乘法原理，共有 {_product_expr(counts)} = {a['total']}（種）。"]
    else:
        raise ValueError(f"unsupported_style:{style}")
    return _parts_payload(matrix, question=question, parts=[_value_part(1, a["total"], "方法數")], display_answer=str(a["total"]), explanation_steps=steps, shape="choice_product")


def _grade_selection(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    s = a["sizes"]
    question = ("某校羽球校隊是由 " + _n(s[0]) + " 位高一學生、" + _n(s[1]) + " 位高二學生及 " + _n(s[2]) + " 位高三學生所組成。\n"
                "(1)每年級各選出一名當小組長，共有多少種情形？\n(2)教練要從校隊中選二名來自不同年級的學生參加雙打比賽，共有多少種選法？")
    pair_terms = [f"{s[i]}×{s[j]}" for i in range(3) for j in range(i + 1, 3)]
    steps = [f"(1) 高一、高二、高三各選一名，乘法原理：{_product_expr(s)} = {a['one_each']}（種）。",
             f"(2) 兩名來自不同年級，分成高一高二、高一高三、高二高三三類（加法原理）：{' + '.join(pair_terms)} = {a['different_pairs']}（種）。"]
    parts = [_value_part(1, a["one_each"], "(1) 情形數"), _value_part(2, a["different_pairs"], "(2) 選法數")]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1){a['one_each']}；(2){a['different_pairs']}", explanation_steps=steps, shape="grade_selection")


# --- 8. divisor_counting -----------------------------------------------------------------------------------------------------------

def _factor_tex(f: dict[str, int]) -> str:
    return "@times ".join(f"{p}^{{{e}}}" for p, e in f.items())


def _divisor_counting(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    n, m, k = int(g["n"]), g.get("multiple_of"), g.get("exclude_multiple_of")
    fact = {int(p): e for p, e in a["factorization"].items()}
    cond = f"是 {_n(m)} 的倍數" if k is None else f"是 {_n(m)} 的倍數但不是 {_n(k)} 的倍數"
    question = f"關於 {_n(n)} 的正因數，回答下列問題。\n(1)共有多少個？\n(2)有多少個{cond}？"
    exps = [e + 1 for e in fact.values()]
    steps = [f"{_t(str(n) + '=' + _factor_tex({str(p): e for p, e in fact.items()}))}，正因數的形式是各質因數的指數從 0 取到原指數，"
             f"所以共有 {_product_expr(exps)} = {a['total']} 個。"]
    mult = multiples_among_divisors(n, int(m))
    need = {p: sp.multiplicity(p, int(m)) for p in fact}
    choose = [fact[p] - need[p] + 1 for p in fact]
    steps.append(f"(2) {m} 的倍數：各質因數的指數至少要是 {m} 的指數，各有 " + "、".join(str(c) for c in choose) + f" 種選擇，乘法原理得 {_product_expr(choose)} = {mult} 個。")
    if k is not None:
        common = math.lcm(int(m), int(k))
        both = multiples_among_divisors(n, common)
        steps.append(f"其中同時是 {k} 的倍數（即 {common} 的倍數）者有 {both} 個，所以 {mult} − {both} = {a['filtered']} 個。")
    parts = [_value_part(1, a["total"], "(1) 個數"), _value_part(2, a["filtered"], "(2) 個數")]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1){a['total']}；(2){a['filtered']}", explanation_steps=steps, shape="divisor_counting")


# --- 9. at_least_one_pairing / ordered_at_least_one ------------------------------------------------------------------------------------

def _at_least_one_pairing(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    h, t = g["head"], g["tail"]
    question = ("醒獅團的 " + _n(h["total"]) + " 個獅頭手中有 " + _n(h["vet"]) + " 個老手 " + _n(h["total"] - h["vet"]) + " 個新手，" + _n(t["total"])
                + " 個獅尾手中有 " + _n(t["vet"]) + " 個老手 " + _n(t["total"] - t["vet"]) + " 個新手。今想選派獅頭手與獅尾手各一人表演一段舞獅秀，"
                "若選出的兩人中，至少要有一人是老手，則共有多少種選派方案？")
    c = a["cases"]
    steps = ["至少要有一人是老手，所以選派方案可分成三類：",
             f"(1) 獅頭是老手，獅尾是新手：有 {h['vet']}×{t['total'] - t['vet']} = {c[0]} 種。",
             f"(2) 獅頭是新手，獅尾是老手：有 {h['total'] - h['vet']}×{t['vet']} = {c[1]} 種。",
             f"(3) 獅頭是老手，獅尾是老手：有 {h['vet']}×{t['vet']} = {c[2]} 種。",
             f"利用加法原理，選派方案共有 {c[0]} + {c[1]} + {c[2]} = {a['count']} 種。"]
    return _parts_payload(matrix, question=question, parts=[_value_part(1, a["count"], "方案數")], display_answer=str(a["count"]), explanation_steps=steps, shape="at_least_one_pairing")


def _ordered_at_least_one(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    o, s, k = int(g["others"]), int(g["special"]), int(g["picks"])
    question = (f"圍棋排名賽共有男生 {_n(o)} 人、女生 {_n(s)} 人參賽。若至少有一位女生排在前{_ZH[k]}名，則前{_ZH[k]}名的名單共有多少種情形？")
    all_expr = "×".join(str(o + s - i) for i in range(k))
    plain_expr = "×".join(str(o - i) for i in range(k))
    steps = [f"不限性別，前{_ZH[k]}名的名單有 {all_expr} = {a['all']} 種。",
             f"其中完全沒有女生（全是男生）的名單有 {plain_expr} = {a['without_special']} 種。",
             f"至少有一位女生的名單共有 {a['all']} − {a['without_special']} = {a['count']} 種。"]
    return _parts_payload(matrix, question=question, parts=[_value_part(1, a["count"], "名單數")], display_answer=str(a["count"]), explanation_steps=steps, shape="ordered_at_least_one")


# --- 10. two_set_counting -----------------------------------------------------------------------------------------------------------------

def _two_set_counting(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    kind = g["kind"]
    if kind == "union_and_none":
        question = (f"全班 {_n(g['U'])} 人中，{_n(g['A'])} 人有手機，{_n(g['B'])} 人有平板電腦，{_n(g['AB'])} 人同時有手機與平板電腦。關於全班 {_n(g['U'])} 人，回答下列問題。\n"
                    "(1)手機與平板電腦至少有一種者有多少人？\n(2)沒有手機，也沒有平板電腦者有多少人？")
        steps = [f"(1) 取捨原理：{g['A']} + {g['B']} − {g['AB']} = {a['union']}，至少有一種者有 {a['union']} 人。",
                 f"(2) 全班 {g['U']} 人減去至少有一種者：{g['U']} − {a['union']} = {a['none']}，兩種都沒有者有 {a['none']} 人。"]
        parts = [_value_part(1, a["union"], "(1) 人數"), _value_part(2, a["none"], "(2) 人數")]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1){a['union']}；(2){a['none']}", explanation_steps=steps, shape=kind)
    if kind == "union":
        question = (f"某班舉行親師會，已知班上 {_n(g['U'])} 位同學中，父親出席者有 {_n(g['A'])} 位，母親出席者有 {_n(g['B'])} 位，父母親皆出席者有 {_n(g['AB'])} 位。"
                    "請問班上有家長出席親師會的同學共有多少位？")
        steps = [f"至少有一位家長出席者：{g['A']} + {g['B']} − {g['AB']} = {a['union']}（位）。（全班 {g['U']} 人只是範圍，不影響取捨原理的計算。）"]
        return _parts_payload(matrix, question=question, parts=[_value_part(1, a["union"], "人數")], display_answer=str(a["union"]), explanation_steps=steps, shape=kind)
    if kind == "missing_set":
        question = (f"學校舉辦桌球及羽球比賽，某班有 {_n(g['union'])} 人參賽，其中參加桌球比賽者有 {_n(g['A'])} 人，兩種球賽都參加者有 {_n(g['AB'])} 人。"
                    "請問這班有多少人參加羽球比賽？")
        steps = [f"參賽者都至少參加一種：{g['union']} = {g['A']} + n(羽球) − {g['AB']}，所以羽球有 {g['union']} − {g['A']} + {g['AB']} = {a['missing']} 人。"]
        return _parts_payload(matrix, question=question, parts=[_value_part(1, a["missing"], "人數")], display_answer=str(a["missing"]), explanation_steps=steps, shape=kind)
    question = (f"對全班 {_n(g['U'])} 人作喝飲料習慣的調查，發現習慣半糖（糖份減半）的有 {_n(g['A'])} 人，習慣去冰（不加冰塊）的有 {_n(g['B'])} 人。"
                "請問該班喝飲料的習慣是半糖且去冰者最多有多少人？最少又有多少人？")
    steps = [f"兩個條件都符合的人數不會超過人數較少的一邊，最多是 {a['max']} 人（人數較少的一邊全部包含在另一邊）。",
             f"最少時兩邊要盡量分開，但全班只有 {g['U']} 人，至少重疊 {g['A']} + {g['B']} − {g['U']} = {a['min']} 人。"]
    parts = [_value_part(1, a["max"], "(1) 最多"), _value_part(2, a["min"], "(2) 最少")]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"最多 {a['max']}；最少 {a['min']}", explanation_steps=steps, shape=kind)


# --- 11. three_set_counting ----------------------------------------------------------------------------------------------------------------

def _three_set_counting(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    formula = f"{g['A']} + {g['B']} + {g['C']} − {g['AB']} − {g['BC']} − {g['CA']} + {g['ABC']} = {a['union']}"
    if a["kind"] == "union_and_none":
        question = (f"全班 {_n(g['U'])} 人作測驗，測驗題分A, B, C三題，結果答對A題者有 {_n(g['A'])} 人，答對B題者有 {_n(g['B'])} 人，答對C題者有 {_n(g['C'])} 人，"
                    f"其中A, B兩題都答對者有 {_n(g['AB'])} 人；B, C兩題都答對者有 {_n(g['BC'])} 人；C, A兩題都答對者有 {_n(g['CA'])} 人；三題都答對者有 {_n(g['ABC'])} 人。"
                    "請回答下列問題。\n(1)全班同學中，至少答對一題者有多少人？\n(2)全班同學中，三題都答錯者有多少人？")
        steps = [f"(1) 取捨原理：{formula}，至少答對一題者有 {a['union']} 人。", f"(2) {g['U']} − {a['union']} = {a['none']}，三題都答錯者有 {a['none']} 人。"]
        parts = [_value_part(1, a["union"], "(1) 人數"), _value_part(2, a["none"], "(2) 人數")]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1){a['union']}；(2){a['none']}", explanation_steps=steps, shape="union_and_none")
    question = (f"學校共開設日語、法語與西班牙語等三種第二外語。某班調查學生選修第二外語的情形，已知選修過日語、法語及西班牙語者分別有 {_n(g['A'])}、{_n(g['B'])} 及 {_n(g['C'])} 人，"
                f"且其中選修過日語及法語者有 {_n(g['AB'])} 人；選修過法語及西班牙語者有 {_n(g['BC'])} 人；選修過日語及西班牙語者有 {_n(g['CA'])} 人；"
                f"而恰有 {_n(g['ABC'])} 人曾選修過上述三種外語。請問班上至少選修過一種第二外語的同學共有多少位？")
    steps = [f"取捨原理：{formula}，至少選修過一種者有 {a['union']} 位。"]
    return _parts_payload(matrix, question=question, parts=[_value_part(1, a["union"], "人數")], display_answer=str(a["union"]), explanation_steps=steps, shape="union")


# --- 12. multiples_counting -----------------------------------------------------------------------------------------------------------------

def _multiples_counting(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    ds, n = [int(d) for d in g["divisors"]], int(g["limit"])
    either = ", ".join(str(d) for d in ds[:-1]) + " 或 " + str(ds[-1])
    question = (f"關於 {_n(1)} 到 {_n(n)} 的正整數，回答下列問題。\n(1)有多少個是 {either} 的倍數？"
                f"\n(2)有多少個不是 {', '.join(str(d) for d in ds)} 中任一數的倍數？")
    singles = " + ".join(f"{n // d}" for d in ds)
    steps = [f"(1) 取捨原理：先加各自的倍數個數 {singles}，再減去兩兩公倍數的個數，最後加回三者公倍數的個數，得 {a['any']} 個。",
             f"(2) 不是任何一個的倍數：{n} − {a['any']} = {a['none']} 個。"]
    parts = [_value_part(1, a["any"], "(1) 個數"), _value_part(2, a["none"], "(2) 個數")]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1){a['any']}；(2){a['none']}", explanation_steps=steps, shape="multiples_counting")


# --- 13. coin_payment / dice_sum_multiples ----------------------------------------------------------------------------------------------------

def _coin_payment(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    c1, c2 = g["coins"]
    question = f"只用 {_n(c1)} 元硬幣或 {_n(c2)} 元硬幣支付 {_n(g['total'])} 元貨款，共有多少種支付方法？"
    steps = [f"依 {c2} 元硬幣的個數分類（加法原理）："
             + "；".join(f"{c2} 元 {b} 個、{c1} 元 {x} 個" for x, b in a["combos"]) + f"，共 {a['ways']} 種。"]
    return _parts_payload(matrix, question=question, parts=[_value_part(1, a["ways"], "支付方法數")], display_answer=str(a["ways"]), explanation_steps=steps, shape="coin_payment")


def _dice_sum_multiples(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    k, s = int(g["modulus"]), int(g.get("sides", 6))
    question = f"同時擲兩粒大小不同的骰子，點數和為 {_n(k)} 的倍數之情形共有多少種？"
    ways = {t: min(t - 1, 2 * s + 1 - t) for t in a["sums"]}
    steps = ["點數和只可能是 " + f"2 到 {2 * s}" + f"，其中是 {k} 的倍數的有 " + "、".join(str(t) for t in a["sums"]) + "。",
             "；".join(f"和為 {t} 有 {w} 種" for t, w in ways.items()) + f"。利用加法原理，共 {' + '.join(str(w) for w in ways.values())} = {a['count']} 種。"]
    return _parts_payload(matrix, question=question, parts=[_value_part(1, a["count"], "情形數")], display_answer=str(a["count"]), explanation_steps=steps, shape="dice_sum_multiples")


# --- 14. race_outcomes / coin_toss_sequences ----------------------------------------------------------------------------------------------------

def _race_sequences(n: int, first: str, second: str) -> list[str]:
    done: list[str] = []

    def play(seq: str) -> None:
        if seq.count(first) == n or seq.count(second) == n:
            done.append(seq)
            return
        play(seq + first)
        play(seq + second)

    play("")
    return done


def _race_outcomes(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    n, winner = int(g["wins_needed"]), g.get("winner", "甲")
    sport = g.get("sport", "桌球")
    question = (f"甲、乙兩人比賽{sport}，約定每局比賽必分出勝負，先勝{_ZH[n]}局者贏得比賽。（可先利用樹狀圖列出比賽的所有可能情形。）\n"
                f"(1)共有多少種可能的情形？\n(2)其中{winner}贏得比賽的情形有多少種？")
    seqs = _race_sequences(n, "甲", "乙")
    mine = [s for s in seqs if s.count(winner) == n]
    if len(seqs) != a["total"] or len(mine) != a["winner_wins"]:
        raise ValueError("tree_listing_disagrees_with_the_domain")
    steps = [f"由樹狀圖，每一局的勝者依序為（甲＝甲勝、乙＝乙勝）：{'、'.join(seqs)}，共 {a['total']} 種可能的情形。",
             f"其中{winner}贏得比賽的有 {'、'.join(mine)}，共 {a['winner_wins']} 種。"]
    parts = [_value_part(1, a["total"], "(1) 情形數"), _value_part(2, a["winner_wins"], f"(2) {winner}贏的情形數")]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1){a['total']}；(2){a['winner_wins']}", explanation_steps=steps, shape="race_outcomes")


def _coin_toss_sequences(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    n, r = int(g["max_tosses"]), int(g.get("run", 2))
    done: list[str] = []

    def toss(seq: str) -> None:
        if len(seq) >= r and len(set(seq[-r:])) == 1 or len(seq) == n:
            done.append(seq)
            return
        toss(seq + "正")
        toss(seq + "反")

    toss("")
    if len(done) != a["count"]:
        raise ValueError("tree_listing_disagrees_with_the_domain")
    question = (f"丟一硬幣不超過 {_n(n)} 次，且丟出連續 {_n(r)} 個正面或連續 {_n(r)} 個反面就提前結束，利用樹狀圖，求丟硬幣的過程共有多少種可能的情形？")
    steps = ["畫出樹狀圖（正＝正面、反＝反面），每一條到結束的路徑是一種情形：" + "、".join(done) + f"，共 {a['count']} 種。"]
    return _parts_payload(matrix, question=question, parts=[_value_part(1, a["count"], "情形數")], display_answer=str(a["count"]), explanation_steps=steps, shape="coin_toss_sequences")


# --- 15. graph_paths (figure) -----------------------------------------------------------------------------------------------------------------------

def _graph_paths(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    if tuple(g["vertices"]) != FIGURE_GRAPH_VERTICES or {frozenset(e) for e in g["edges"]} != FIGURE_GRAPH_EDGES:
        raise ValueError("graph_differs_from_the_textbook_figure")
    s, e = g["start"], g["end"]
    question = (f"如圖，在每個頂點不得通過兩次的限制下，由 {_n(s)} 點出發走到 {_n(e)} 點。（可先利用樹狀圖列出所有路徑。）\n共有多少種路徑？")
    steps = [f"從 {s} 出發的每一步，只能走到有線段相連而且還沒經過的頂點，畫出樹狀圖，到達 {e} 的路徑有：" + "、".join("→".join(p) for p in a["paths"]) + f"，共 {a['count']} 種。"]
    return _parts_payload(matrix, question=question, parts=[_value_part(1, a["count"], "路徑數")], display_answer=str(a["count"]), explanation_steps=steps, shape="graph_paths", figure=True)


# --- 16. tiling_count (figure) -----------------------------------------------------------------------------------------------------------------------

def _tiling_count(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    if {tuple(c) for c in g["cells"]} != FIGURE_REGION_CELLS:
        raise ValueError("region_differs_from_the_textbook_figure")
    ask = g["ask"]
    base = "使用 " + _t("1@times 1") + " 與 " + _t("1@times 2") + " 兩種磁磚，鋪滿由六個 " + _t("1@times 1") + " 正方形連接而成的 L 形區域，如右圖所示，"
    if ask["kind"] == "total":
        question = base + "共有多少種方法？（可以只使用一種磁磚）"
    elif ask["kind"] == "exactly":
        question = base + f"其中恰好使用 {_n(ask['k'])} 塊 " + _t("1@times 2") + " 磁磚的方法有多少種？"
    else:
        question = base + f"其中至少使用 {_n(ask['k'])} 塊 " + _t("1@times 2") + " 磁磚的方法有多少種？"
    dist = a["distribution"]
    steps = ["依使用 1×2 磁磚（可橫放或直放）的塊數分類，再用加法原理：" + "；".join(f"{u} 塊有 {v} 種" for u, v in dist.items()) + f"，全部合計 {sum(dist.values())} 種。",
             f"本題要求的方法數為 {a['value']} 種。"]
    return _parts_payload(matrix, question=question, parts=[_value_part(1, a["value"], "方法數")], display_answer=str(a["value"]), explanation_steps=steps, shape="tiling_count", figure=True)


# --- 17. region_pairs_claim ----------------------------------------------------------------------------------------------------------------------------

def _region_pairs_claim(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    s, n, claimed = int(g["south"]), int(g["north"]), int(g["claimed"])
    relation = g.get("relation", "same_region")
    where = "是同一區的" if relation == "same_region" else "來自不同區的"
    question = f"下列敘述對的打「○」，錯的打「×」。\n足球賽有南區 {_n(s)} 隊、北區 {_n(n)} 隊參賽，進入決賽的 {_n(2)} 隊{where}情形，共有 {_n(claimed)} 種。"
    if relation == "same_region":
        calc = f"南區 {s} 隊中選 2 隊有 {s}×{s - 1}÷2 = {s * (s - 1) // 2} 種，北區 {n} 隊中選 2 隊有 {n}×{n - 1}÷2 = {n * (n - 1) // 2} 種，加法原理共 {a['actual']} 種。"
    else:
        calc = f"南區選 1 隊有 {s} 種，北區選 1 隊有 {n} 種，乘法原理共 {s}×{n} = {a['actual']} 種。"
    steps = [f"{calc}敘述說共有 {claimed} 種，{'正確' if a['truth'] else '錯誤'}，所以為「{'○' if a['truth'] else '×'}」。"]
    return _single_payload(matrix, question=question, part=_choice_part(1, "A" if a["truth"] else "B", TRUE_FALSE_CHOICES),
                           display_answer="○" if a["truth"] else "×", explanation_steps=steps, shape="single_choice")


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "interval_set_operations": _interval_set_operations,
    "finite_set_operations": _finite_set_operations,
    "equation_root_sets": _equation_root_sets,
    "proposition_truth": _proposition_truth,
    "implication_truth": _implication_truth,
    "condition_relation": _condition_relation,
    "choice_product": _choice_product,
    "grade_selection": _grade_selection,
    "divisor_counting": _divisor_counting,
    "at_least_one_pairing": _at_least_one_pairing,
    "ordered_at_least_one": _ordered_at_least_one,
    "two_set_counting": _two_set_counting,
    "three_set_counting": _three_set_counting,
    "multiples_counting": _multiples_counting,
    "coin_payment": _coin_payment,
    "dice_sum_multiples": _dice_sum_multiples,
    "race_outcomes": _race_outcomes,
    "graph_paths": _graph_paths,
    "coin_toss_sequences": _coin_toss_sequences,
    "tiling_count": _tiling_count,
    "region_pairs_claim": _region_pairs_claim,
}


def adapt_counting_sets_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_counting_sets_operation:{operation}")
    return builder(matrix)
