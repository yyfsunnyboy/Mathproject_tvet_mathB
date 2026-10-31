"""Question payload contracts for discrete.classical_probability (普高數學2 Unit 6 古典機率).

Every expected answer comes from the domain matrix. Stems are rebuilt from the stated data only.
No question points at a figure. Format hints are not given an example that copies the answer.
"""

from __future__ import annotations

from typing import Any, Callable

from core.gencode.multipart_stem_contract import build_stem_structure, stem_structure_to_question_text

from .classical_probability_domain import DOMAIN_KEY, TRUE_FALSE, YES_NO

_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_SET = ("solution_set_checker", "unordered_solution_set", "solution_set")
_LETTERS = "ABCDEF"
_FACE = {0: "反面", 1: "正面"}


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


def _value_part(index: int, value: Any, label: str) -> dict[str, Any]:
    return _part(index, str(value), *_RATIONAL, label=label, prompt=label)


def _set_part(index: int, values: list[int], label: str) -> dict[str, Any]:
    return _part(index, list(values), *_SET, label=label, prompt=label)


def _choice_part(index: int, expected_label: str, choices, label: str) -> dict[str, Any]:
    return _part(index, expected_label, "choice_label_checker", "choice_label", "single_choice",
                 choices=[dict(c) for c in choices], input_type="select", label=label, prompt=label)


def _show(part: dict[str, Any]) -> str:
    if part["kind"] == "set":
        return "{" + ", ".join(str(v) for v in part["values"]) + "}"
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


def _set_builder(label: str) -> tuple[str, Callable]:
    return label, lambda i, item: _set_part(i, item["values"], label)


def _choice_builder(label: str, choices) -> tuple[str, Callable]:
    return label, lambda i, item, choices=choices, label=label: _choice_part(i, item["label"], choices, label)


def _observable_text(observable: dict[str, Any]) -> str:
    kind = observable["kind"]
    if kind == "head_count":
        return "正面出現的次數"
    if kind == "tail_count":
        return "反面出現的次數"
    if kind == "toss":
        return f"第 {observable['index'] + 1} 次的結果（正面為 {_n(1)}、反面為 {_n(0)}）"
    raise ValueError("bad_observable")


def _coin_space(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    n = g["n"]
    question = (
        f"擲一枚公正硬幣 {n} 次，依序觀察正反面。正面記為 {_n(1)}、反面記為 {_n(0)}，"
        f"並把這 {n} 次的結果寫成整數，最先擲出的是最高位。",
        [
            "寫出全部樣本點組成的集合。",
            "求這個樣本空間的樣本點個數。",
            f"若改為只記錄{_observable_text(g['observable'])}，寫出此時的樣本空間。",
            "求上一小題的樣本點個數。",
        ],
    )
    return _from_parts(matrix, question, [
        _set_builder("樣本點集合"), _rational_builder("樣本點個數"), _set_builder("觀察值的集合"), _rational_builder("觀察值個數"),
    ], "coin_outcome_space")


def _mode_text(mode: str, k: int) -> str:
    if mode == "ordered_no_replace":
        return f"依序取 {k} 次、每次取出後不放回"
    if mode == "ordered_replace":
        return f"取後放回，依序取 {k} 次"
    if mode == "unordered":
        return f"同時取 {k} 個，不計順序"
    raise ValueError("bad_draw_mode")


def _draw_space(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    n, asks = g["n"], g["asks"]
    shown = "、".join(_n(v) for v in (g.get("labels") or range(1, n + 1)))
    lines = []
    builders = []
    for ask in asks:
        lines.append(f"{_mode_text(ask['mode'], ask['k'])}。把結果依取出順序（不計順序時由小到大）寫成十進位整數，寫出樣本點集合。")
        lines.append("求這個樣本空間的樣本點個數。")
        builders.append(_set_builder("樣本點集合"))
        builders.append(_rational_builder("樣本點個數"))
    question = (f"袋中有標號 {shown} 的球各一顆，每球被取出的機會均等。", lines)
    return _from_parts(matrix, question, builders, "draw_outcome_space")


def _event_phrase(spec: dict[str, Any], zero: str, one: str) -> str:
    kind = spec["kind"]
    if kind == "space":
        return "全部樣本點"
    if kind == "at_least_symbol":
        name = zero if spec["symbol"] == 0 else one
        return f"至少有 {spec['k']} 個{name}"
    if kind == "exactly_symbol":
        name = zero if spec["symbol"] == 0 else one
        return f"恰有 {spec['k']} 個{name}"
    if kind == "bit_is":
        name = one if spec["value"] == 1 else zero
        return f"第 {spec['index'] + 1} 個是{name}"
    if kind == "and":
        return _event_phrase(spec["left"], zero, one) + "，且" + _event_phrase(spec["right"], zero, one)
    if kind == "complement":
        return "「" + _event_phrase(spec["event"], zero, one) + "」的補事件"
    raise ValueError("bad_event")


def _coded(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    story = g.get("story", "coin")
    if story == "gender":
        intro = (
            f"一個家庭有 {g['n']} 個小孩，以出生順序區別，每個小孩是男生或女生的機會均等。"
            f"男生記為 {_n(1)}、女生記為 {_n(0)}，較早出生的是最高位。"
        )
        zero, one = "女生", "男生"
    else:
        intro = (
            f"擲一枚公正硬幣 {g['n']} 次，依序記錄。正面記為 {_n(1)}、反面記為 {_n(0)}，最先擲出的是最高位。"
        )
        zero, one = "反面", "正面"
    lines = [f"寫出「{_event_phrase(ask, zero, one)}」的樣本點集合。" for ask in g["asks"]]
    builders = [_set_builder("樣本點集合") for _ in g["asks"]]
    return _from_parts(matrix, (intro, lines), builders, "coded_event_sets")


def _pred(spec: dict[str, Any]) -> str:
    kind = spec["kind"]
    if kind == "sum_gt":
        return f"點數和大於 {_n(spec['n'])}"
    if kind == "sum_eq":
        return f"點數和等於 {_n(spec['n'])}"
    if kind == "product_eq":
        return f"點數積等於 {_n(spec['n'])}"
    if kind == "faces_equal":
        return "兩粒點數相同"
    if kind == "first_even":
        return "第一粒是偶數"
    if kind == "first_odd":
        return "第一粒是奇數"
    if kind == "second_even":
        return "第二粒是偶數"
    if kind == "sum_odd":
        return "點數和是奇數"
    if kind == "sum_even":
        return "點數和是偶數"
    if kind == "first_gt_second":
        return "第一粒點數大於第二粒"
    if kind == "first_lt_second":
        return "第一粒點數小於第二粒"
    if kind == "diff_eq":
        return f"兩粒點數差的絕對值等於 {_n(spec['n'])}"
    if kind == "both_gt":
        return f"兩粒點數都大於 {_n(spec['n'])}"
    if kind == "exactly_one_face":
        return f"恰有一粒出現 {_n(spec['face'])} 點"
    raise ValueError("bad_predicate")


def _dice_sets(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    question = (
        "同時擲兩粒公正骰子，將兩粒編號區別。把結果寫成兩位數，十位是第一粒的點數、個位是第二粒的點數。設 A 為"
        f"「{_pred(g['a'])}」，B 為「{_pred(g['b'])}」。",
        ["寫出 A 的樣本點集合。", "寫出 B 的樣本點集合。", "寫出 A∩B 的樣本點集合。", "寫出 A∪B 的樣本點集合。"],
    )
    return _from_parts(matrix, question, [
        _set_builder("A"), _set_builder("B"), _set_builder("A∩B"), _set_builder("A∪B"),
    ], "dice_event_sets")


def _relation_event(spec: dict[str, Any]) -> str:
    kind = spec["kind"]
    if kind == "exactly_heads":
        return f"恰有 {spec['k']} 個正面"
    if kind == "at_least_heads":
        return f"至少有 {spec['k']} 個正面"
    raise ValueError("bad_relation_event")


def _relation(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    if g["model"] == "coin":
        question = (
            f"擲一枚公正硬幣 {g['n']} 次，正面記為 {_n(1)}、反面記為 {_n(0)}，最先擲出的是最高位。"
            f"設 A 為「{_relation_event(g['a'])}」，B 為「{_relation_event(g['b'])}」。",
            [
                "寫出 A 的補事件 A' 的樣本點集合。",
                "A 與 B 是否互斥？選擇「是」或「否」。",
                "A 與 A' 是否互斥？選擇「是」或「否」。",
            ],
        )
        return _from_parts(matrix, question, [
            _set_builder("A'"), _choice_builder("A 與 B 是否互斥", YES_NO), _choice_builder("A 與 A' 是否互斥", YES_NO),
        ], "event_relation")
    question = (
        "同時擲兩粒公正骰子，將兩粒編號區別。"
        f"設 A 為「{_pred(g['a'])}」，B 為「{_pred(g['b'])}」。A 與 B 是否互斥？"
    )
    return _from_parts(matrix, question, [_choice_builder("是否互斥", YES_NO)], "event_relation")


def _uniform_line(model: str, g: dict[str, Any], ask: dict[str, Any]) -> str:
    if model == "die":
        if ask["kind"] == "face":
            return f"出現 {_n(ask['face'])} 點的機率。"
        shown = "、".join(_n(v) for v in ask["values"])
        return f"點數屬於 {shown} 的機率。"
    if model == "cards":
        if ask["kind"] == "ranks":
            if ask["count"] == 1:
                rank = ask.get("rank", 6)
                return f"點數為 {_n(rank)} 的機率。"
            return f"點數屬於連續 {ask['count']} 種點數之一的機率。"
        suit = ask.get("suit", "紅心")
        return f"花色為{suit}的機率。"
    divisors = " 或 ".join(_n(v) for v in ask["divisors"])
    return f"取出的數是 {divisors} 的倍數的機率。"


def _uniform(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    model = g["model"]
    if model == "die":
        intro = f"擲一粒公正骰子一次，{g.get('faces', 6)} 面的點數為 1 到 {g.get('faces', 6)}，每面等可能。求下列機率。"
    elif model == "cards":
        intro = "一副撲克牌有 52 張、4 種花色，每張被抽出的機會均等。求下列機率。"
    else:
        intro = f"袋中有標號 1 到 {g['n']} 的球各一顆，從中取出一球，每球機會均等。求下列機率。"
    lines = [_uniform_line(model, g, ask) for ask in g["asks"]]
    builders = [_rational_builder("機率") for _ in g["asks"]]
    return _from_parts(matrix, (intro, lines), builders, "uniform_draw_probability")


def _coin_prob(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    intro = "公正硬幣可區別每次的結果（正面與反面等可能）。求下列事件的機率。"
    if g.get("simultaneous"):
        intro = "同時擲若干枚可區別的公正硬幣（每一種正反序列等可能）。求下列事件的機率。"
    lines = [f"擲 {ask['n']} 次，恰有 {ask['k']} 個正面的機率。" for ask in g["asks"]]
    builders = [_rational_builder("機率") for _ in g["asks"]]
    return _from_parts(matrix, (intro, lines), builders, "coin_count_probability")


def _dice_ask_text(ask: dict[str, Any]) -> str:
    kind = ask["kind"]
    if kind == "sum_eq":
        return f"點數和等於 {_n(ask['n'])} 的機率。"
    if kind == "all_different":
        return "每粒點數都不同的機率。"
    if kind == "all_equal":
        return "每粒點數都相同的機率。"
    if kind == "exactly_two_equal":
        return "恰有兩粒點數相同（另一粒不同）的機率。"
    if kind == "at_least_two_equal":
        return "至少有兩粒點數相同的機率。"
    if kind == "faces_equal":
        return "兩粒點數相同的機率。"
    if kind == "first_gt_second":
        return "第一粒點數大於第二粒的機率。"
    if kind == "diff_eq":
        return f"兩粒點數差的絕對值等於 {_n(ask['n'])} 的機率。"
    if kind == "both_gt":
        return f"兩粒點數都大於 {_n(ask['n'])} 的機率。"
    if kind == "exactly_face_count":
        return f"恰有 {ask['count']} 粒出現 {_n(ask['face'])} 點的機率。"
    if kind == "at_least_face":
        return f"至少有 {ask['count']} 粒出現 {_n(ask['face'])} 點的機率。"
    raise ValueError("bad_dice_ask")


def _dice_prob(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    dice, faces = g["dice"], g["faces"]
    intro = (
        f"同時擲 {dice} 粒各有 {faces} 面（點數 1 到 {faces}）的公正骰子，將骰子編號區別，每一種點數序對等可能。求下列機率。"
    )
    lines = [_dice_ask_text(ask) for ask in g["asks"]]
    builders = [_rational_builder("機率") for _ in g["asks"]]
    return _from_parts(matrix, (intro, lines), builders, "dice_count_probability")


def _urn_ask_text(names: list[str], ask: dict[str, Any], ordered: bool) -> str:
    how = "依序取出、不放回" if ordered else "同時取出"
    kind = ask["kind"]
    if kind == "exact":
        bits = "、".join(f"{names[i]} {ask['counts'][i]} 個" for i in range(len(names)) if ask["counts"][i])
        return f"{how}，其中{bits}的機率。"
    if kind == "same_color":
        return f"{how}，取出的物品屬於同一類的機率。"
    if kind == "not_mono":
        return f"{how}，取出的物品不全屬於同一類的機率。"
    if kind == "at_most":
        return f"{how}，{names[ask['index']]}至多 {ask['count']} 個的機率。"
    raise ValueError("bad_urn_ask")


def _urn(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    names = list(g.get("names") or [f"第{i + 1}類" for i in range(len(g["colors"]))])
    listed = "、".join(f"{names[i]} {g['colors'][i]} 個" for i in range(len(names)))
    intro = f"一批物品有{listed}，每件被取出的機會均等。從中取出 {g['draw']} 件。求下列機率。"
    lines = [_urn_ask_text(names, ask, bool(ask.get("ordered"))) for ask in g["asks"]]
    builders = [_rational_builder("機率") for _ in g["asks"]]
    return _from_parts(matrix, (intro, lines), builders, "urn_draw_probability")


def _repl_line(ask: dict[str, Any]) -> str:
    kind = ask["kind"]
    if kind == "exactly":
        return f"重複 {ask['n']} 次，恰有 {ask['k']} 次出現第 {ask['target']} 種結果的機率。"
    if kind == "at_least":
        return f"重複 {ask['n']} 次，至少有 {ask['k']} 次出現第 {ask['target']} 種結果的機率。"
    if kind == "not_all_different":
        if ask.get("scene_line") == "club":
            return "至少有兩人選擇相同社團的機率。"
        return f"{ask['n']} 次結果中至少有兩次相同的機率。"
    raise ValueError("bad_replacement_ask")


def _repl(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    if g.get("scene") == "club":
        people = g["asks"][0]["n"]
        intro = f"{people} 人各從 {g['sides']} 個社團中任選一個參加，每人的選擇互不影響，每個社團等可能。求下列機率。"
    elif g.get("labels"):
        shown = "、".join(str(v) for v in g["labels"])
        intro = f"袋中有標號 {shown} 的球各一顆。每次取出一球後放回，每球每次被取出的機會均等。求下列機率。"
    else:
        intro = f"每次獨立觀察一個有 {g['sides']} 種等可能結果的試驗（取後放回，或每人各自選擇）。求下列機率。"
    lines = [_repl_line(ask) for ask in g["asks"]]
    builders = [_rational_builder("機率") for _ in g["asks"]]
    return _from_parts(matrix, (intro, lines), builders, "replacement_count_probability")


def _letter(index: int) -> str:
    return _LETTERS[index]


def _algebra(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    names = [_letter(i) for i in range(len(g["probs"]))]
    given = "、".join(f"{_t('P(' + name + ')')} = {_frac(p)}" for name, p in zip(names, g["probs"]))
    extra = "，且這些事件兩兩互斥" if g.get("pairwise_disjoint") else ""
    lines = []
    for ask in g["asks"]:
        if ask["kind"] == "complement":
            lines.append("求 " + _t("P(" + names[ask["index"]] + "')") + "。")
        elif ask["kind"] == "union":
            joined = "@cup ".join(names[i] for i in ask["indices"])
            known = ""
            if "intersection" in ask:
                pair = "@cap ".join(names[i] for i in ask["indices"])
                known = f"已知 {_t('P(' + pair + ')')} = {_frac(ask['intersection'])}，"
            lines.append(f"{known}求 {_t('P(' + joined + ')')}。")
        else:
            pair = "@cap ".join(names[i] for i in ask["indices"])
            union = "@cup ".join(names[i] for i in ask["indices"])
            lines.append(f"已知 {_t('P(' + union + ')')} = {_frac(ask['union'])}，求 {_t('P(' + pair + ')')}。")
    question = (f"設 { '、'.join(names) } 為樣本空間的事件，{given}{extra}。", lines)
    builders = [_rational_builder("機率") for _ in g["asks"]]
    return _from_parts(matrix, question, builders, "probability_algebra")


def _password(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    if g.get("alphabet"):
        shown = "、".join(str(v) for v in g["alphabet"])
        who = f"密碼是由 {shown} 這 {g['symbols']} 個不同數字排成的"
    else:
        who = f"密碼是由 {g['symbols']} 個不同數字排成的"
    question = (
        f"一組密碼{who}，而且每一組排列出現的機會均等。",
        [
            "一次就猜對的機率是多少？",
            f"若連續輸入 {g['wrong_limit']} 次互不相同的錯誤密碼就會被鎖定，求被鎖定的機率。",
        ],
    )
    return _from_parts(matrix, question, [_rational_builder("機率"), _rational_builder("機率")], "password_guess")


def _solve(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    question = (
        f"袋中有 {g['white']} 顆白球和 n 顆黑球。從袋中同時取出兩球，每球被取出的機會均等，"
        f"已知兩球同為白球的機率是 {_frac(g['target'])}，求 n 的值。"
    )
    return _from_parts(matrix, question, [_rational_builder("n")], "solve_urn_count")


def _claim(matrix: dict[str, Any]) -> dict[str, Any]:
    g = matrix["givens"]
    style = g["style"]
    if style == "urn_half":
        if g.get("red") is None:
            body = f"袋中有大小相同的紅球、白球各若干顆。從中取出一球，取到紅球的機率為 {_frac('1/2')}。"
        else:
            body = (
                f"袋中有紅球 {g['red']} 顆、白球 {g['white']} 顆，每球被取出的機會均等。"
                f"從中取出一球，取到紅球的機率為 {_frac('1/2')}。"
            )
    elif style == "dice_sum":
        body = f"同時擲兩粒公正骰子一次，出現點數和為 {_n(g['total'])} 的機率為 {_frac(g['stated'])}。"
    else:
        body = f"擲一粒公正骰子二次，至少出現一次 {_n(6)} 點的機率為 {_t('1')} - {_frac(str(g['stated_miss']) + '/36')}。"
    question = "下列敘述對的打「○」，錯的打「×」。\n" + body
    return _from_parts(matrix, question, [_choice_builder("對或錯", TRUE_FALSE)], "classical_claim")


_ADAPT: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "coin_outcome_space": _coin_space,
    "draw_outcome_space": _draw_space,
    "coded_event_sets": _coded,
    "dice_event_sets": _dice_sets,
    "event_relation": _relation,
    "uniform_draw_probability": _uniform,
    "coin_count_probability": _coin_prob,
    "dice_count_probability": _dice_prob,
    "urn_draw_probability": _urn,
    "replacement_count_probability": _repl,
    "probability_algebra": _algebra,
    "password_guess": _password,
    "solve_urn_count": _solve,
    "classical_claim": _claim,
}


def adapt_classical_probability_matrix(matrix: dict[str, Any], *, domain_operation: str, seed: int | None = None, **_: Any) -> dict[str, Any]:
    if matrix.get("domain") != DOMAIN_KEY or matrix.get("domain_operation") != domain_operation:
        raise ValueError("matrix_operation_mismatch")
    return _ADAPT[domain_operation](matrix)
