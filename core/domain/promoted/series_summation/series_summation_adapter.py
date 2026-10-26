"""Question payload contracts for sequence.series_sums (普高數學2 Unit 2 級數).

Every expected answer comes from the domain matrix, never from this adapter.  Stems are rebuilt from the same stated data the
domain solved, so a varied question always carries its own numbers.  Figures: the textbook picture is the reviewed crop reused by the
practice route (``reuse_textbook_image``); nothing is drawn here.
"""

from __future__ import annotations

from typing import Any, Callable

from .series_summation_domain import DOMAIN_KEY, is_rational, num, text, tex

TRUE_FALSE_CHOICES = ({"label": "A", "value": "○"}, {"label": "B", "value": "×"})
_RATIONAL = ("rational_checker", "rational_equivalent", "rational")
_EXPR = ("expression_checker", "algebraic_equivalent", "expression")
_RADICAL = ("expression_checker", "radical_equivalence", "numeric_or_radical")
_SET = ("solution_set_checker", "unordered_solution_set", "solution_set")
_LANGLE, _RANGLE = "\\left\\langle ", "\\right\\rangle"
_CDOTS, _TIMES, _FRAC = "\\cdots ", "\\times ", "\\frac{"
_CIRCLED = "①②③④⑤"
_SET_EXAMPLES = ("2, 5", "3, 8", "-1, 4", "6, 11", "-3, 7", "10, 13")


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


def _value_part(index: int, value: str, label: str) -> dict[str, Any]:
    checker = _RATIONAL if is_rational(value) else _RADICAL
    return _part(index, value, *checker, label=label, prompt=label)


def _expr_part(index: int, expected: str, label: str) -> dict[str, Any]:
    return _part(index, expected, *_EXPR, label=label, prompt=label)


def _set_part(index: int, members: list[str], label: str) -> dict[str, Any]:
    """A value set.  The format hint is shown before submitting, so it is a fixed illustration sharing no value with the answer."""
    answer = {num(m) for m in members}
    shown = next(e for e in _SET_EXAMPLES if not ({num(x.strip()) for x in e.split(",")} & answer))
    return _part(index, list(members), *_SET, solution_members="exact_rational", answer_format_example=shown, label=label, prompt=label)


def _choice_part(index: int, expected_label: str, choices: list[dict[str, str]], label: str = "") -> dict[str, Any]:
    extra = {"label": label, "prompt": label} if label else {}
    return _part(index, expected_label, "choice_label_checker", "choice_label", "single_choice", choices=[dict(c) for c in choices], **extra)


def _neg(v: Any) -> str:
    """A term inside a printed series: negatives are parenthesised, as the textbook does."""
    return f"({tex(v)})" if num(v) < 0 else tex(v)


def _series_tex(first: Any, step: Any, last_text: str, show: int, power: int | None = None) -> str:
    def term(t: Any) -> str:
        base = _neg(t)
        return base if power is None else f"{base}^{{{power}}}"

    shown = [term(num(first) + i * num(step)) for i in range(show)]
    return "+".join(shown) + "+" + _CDOTS + "+" + last_text


def _list_tex(terms: list[Any], last_text: str) -> str:
    return "+".join(_neg(t) for t in terms) + "+" + _CDOTS + "+" + last_text


def _a(k: Any) -> str:
    return f"a_{{{k}}}"


def _disp(v: Any) -> str:
    import re

    return re.sub(r"sqrt[(](\d+)[)]", lambda m: "√" + m.group(1), str(v)).replace("*", "")


def _pretty(expr: str) -> str:
    """Display form of a canonical expression: 2*n -> 2n, 2*3**(n-1) -> 2·3^(n-1)."""
    import re

    out = re.sub(r"(\d)\*([a-z])", r"\1\2", expr).replace("**", "^")
    return out.replace("*", "·")


def _bullet(parts: list[str]) -> str:
    return "\n".join(f"({i})" + p for i, p in enumerate(parts, 1))


def _seq(name: str = "a_{n}") -> str:
    return _t(_LANGLE + name + _RANGLE)


# --- 1. arithmetic_series_items ---------------------------------------------------------------------------------------------

def _arithmetic_series_items(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    lines, parts, steps, shown = [], [], [], []
    for i, (item, got) in enumerate(zip(g["items"], a["items"]), 1):
        if item["kind"] == "d_from_sum":
            lines.append(f"求首項為{text(item['a1'])}，前 {_t(str(item['n']))} 項和為 {_t(text(item['S']))} 的等差數列之公差。")
            parts.append(_value_part(i, got["value"], f"({i}) 公差"))
            steps.append(f"({i}) {_t('S_{' + str(item['n']) + '}=' + _FRAC + str(item['n']) + '(2@times ' + text(item['a1']) + '+' + str(int(item['n']) - 1) + 'd)}{2}=' + text(item['S']))}，解得公差 {_t('d=' + tex(got['value']))}。")
        else:
            show = int(item.get("show", 2))
            lines.append(f"求等差級數 {_t(_series_tex(item['first'], item['d'], _neg(item['last']), show))} 的和。")
            parts.append(_value_part(i, got["value"], f"({i}) 和"))
            steps.append(f"({i}) 共有 {got['n']} 項，利用等差級數的和公式 {_t('S_{n}=' + _FRAC + 'n(a_{1}+a_{n})}{2}')}，得和為 {_t(tex(got['value']))}。")
        shown.append(f"{got['value']}")
    question = "\n".join(f"({i}){line}" for i, line in enumerate(lines, 1))
    return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(f"({i}){v}" for i, v in enumerate(shown, 1)),
                          explanation_steps=steps, shape="arithmetic_series_items")


# --- 2. arithmetic_series_relation ----------------------------------------------------------------------------------------------

def _arithmetic_series_relation(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    kind = g["kind"]
    if kind == "mid_term":
        m, n = int(g["m"]), int(a["n"])
        question = (f"已知 {_seq()} 為等差數列且 {_t(_a(m) + '=' + tex(g['value']))}。\n(1)求 {_t(_a(1) + '+' + _a(n))} 的值。\n(2)求前 {_t(str(n))} 項的和。")
        parts = [_value_part(1, a["pair_sum"], "(1) 值"), _value_part(2, a["total"], "(2) 和")]
        steps = [f"(1) 等差數列首末兩項的和等於中間項的 2 倍：{_t(_a(1) + '+' + _a(n) + '=2' + _a(m) + '=' + tex(a['pair_sum']))}。",
                 f"(2) {_t('S_{' + str(n) + '}=' + _FRAC + str(n) + '(' + _a(1) + '+' + _a(n) + ')}{2}=' + tex(a['total']))}。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"{a['pair_sum']}；{a['total']}", explanation_steps=steps, shape=kind)
    if kind == "pair_from_sum":
        n = int(g["n"])
        pairs = g["pairs"]
        lines = [f"(1)求 {_t(_a(pairs[0][0]) + '+' + _a(pairs[0][1]))} 的值。", f"(2)求 {_t(_a(pairs[1][0]) + '+' + _a(pairs[1][1]))} 的值。"]
        question = f"已知 {_seq()} 為等差數列，且前 {_t(str(n))} 項的和 {_t('S_{' + str(n) + '}=' + tex(g['S']))}。\n" + "\n".join(lines)
        parts = [_value_part(i + 1, v, f"({i + 1}) 值") for i, v in enumerate(a["values"])]
        steps = [f"首項與第 {n} 項、第 2 項與第 {n - 1} 項……每一對的和都相等，所以每一對的和為 {_t(tex(a['values'][0]))}（{_t('S_{' + str(n) + '}=' + _FRAC + str(n) + '(' + _a(1) + '+' + _a(n) + ')}{2}')}）。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(a["values"]), explanation_steps=steps, shape=kind)
    if kind == "mid_total":
        n, mid, step, middle = int(g["n"]), g["mid"], g["step"], (int(g["n"]) + 1) // 2
        question = (f"某表演廳共有 {_t(str(n))} 排座位，每一排都比其前一排多 {_t(str(step))} 個座位，且正中間的那一排（即第 {_t(str(middle))} 排）"
                    f"有 {_t(str(mid))} 個座位，問此表演廳總共有幾個座位？")
        steps = [f"各排座位數成等差數列，總和 = 項數 × 中間項 = {_t(str(n) + _TIMES + tex(mid) + '=' + tex(a['total']))}。"]
        return _parts_payload(matrix, question=question, parts=[_value_part(1, a["total"], "座位數")], display_answer=a["total"], explanation_steps=steps, shape=kind)
    if kind == "front_back":
        n = int(g["n"])
        question = f"已知一等差數列 {_seq()} 共有 {_t(str(n))} 項，其前兩項的和為{text(g['first2'])}，末兩項的和為{text(g['last2'])}，求所有項的和。"
        steps = [f"前兩項與末兩項的和 = 2(首項 + 末項)，所以 {_t(_a(1) + '+' + _a(n) + '=' + tex(num(g['first2']) / 2 + num(g['last2']) / 2))}，"
                 f"{_t('S_{' + str(n) + '}=' + _FRAC + str(n) + '(' + _a(1) + '+' + _a(n) + ')}{2}=' + tex(a['total']))}。"]
        return _parts_payload(matrix, question=question, parts=[_value_part(1, a["total"], "和")], display_answer=a["total"], explanation_steps=steps, shape=kind)
    if kind == "threshold_count":
        question = (f"寶石收藏家擁有若干重量不等的寶石，其中最重的為 {_t(text(g['last']))} 公克，最輕的為 {_t(text(g['first']))} 公克，所有寶石的重量恰可形成一個等差數列，"
                    f"且總重量超過 {_t(text(g['threshold']))} 公克。問：收藏家最少擁有幾顆寶石？")
        steps = [f"設有 n 顆，總重量 {_t('S_{n}=' + _FRAC + 'n(' + text(g['first']) + '+' + text(g['last']) + ')}{2}>' + text(g['threshold']))}，最小的整數 n 為 {a['count']}。"]
        return _parts_payload(matrix, question=question, parts=[_value_part(1, str(a["count"]), "最少幾顆")], display_answer=str(a["count"]), explanation_steps=steps, shape=kind)
    if kind == "two_walls":
        question = (f"有一面厚 {_t(text(g['thick']))} 公分的木頭牆，大小兩隻老鼠面對面穿牆。第一天大老鼠穿牆 {_t(text(g['big1']))} 公分，小老鼠穿牆 {_t(text(g['small1']))} 公分；"
                    f"接下來，大老鼠每天都比前一天多穿牆 {_t(text(g['bigd']))} 公分，而小老鼠每天僅比前一天多穿牆 {_t(text(g['smalld']))} 公分。問：大小兩隻老鼠最快在第幾天才會將牆穿通？")
        steps = [f"兩鼠每天穿牆的長度各成等差數列，前 n 天合計 {_t('S_{n}=' + _FRAC + 'n(2@times ' + text(g['big1']) + '+(n-1)' + text(g['bigd']) + ')}{2}+' + _FRAC + 'n(2@times ' + text(g['small1']) + '+(n-1)' + text(g['smalld']) + ')}{2}')}，"
                 f"至少要 {_t(text(g['thick']))} 公分，最快第 {a['days']} 天穿通。"]
        return _parts_payload(matrix, question=question, parts=[_value_part(1, str(a["days"]), "第幾天")], display_answer=str(a["days"]), explanation_steps=steps, shape=kind)
    raise ValueError(f"unsupported_kind:{kind}")


# --- 3. geometric_series_items ---------------------------------------------------------------------------------------------------

def _geometric_series_items(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    lines, parts, steps = [], [], []
    for i, (item, got) in enumerate(zip(g["items"], a["items"]), 1):
        if item["kind"] == "ratio_sum":
            lines.append(f"求首項為{text(item['a1'])}，公比為 {_t(tex(item['r']))} 的等比數列前 {_t(str(item['n']))} 項的和。")
            steps.append(f"({i}) {_t('S_{' + str(item['n']) + '}=' + _FRAC + 'a_{1}(1-r^{n})}{1-r}=' + tex(got['value']))}。")
        else:
            last = item.get("last_tex") or _neg(item["last"])
            lines.append(f"求等比級數 {_t(_list_tex(item['terms'], last))} 的和。")
            steps.append(f"({i}) 公比 {_t('r=' + tex(got['ratio']))}，共 {got['n']} 項，和為 {_t(tex(got['value']))}。")
        parts.append(_value_part(i, got["value"], f"({i}) 和"))
    question = "\n".join(f"({i}){line}" for i, line in enumerate(lines, 1))
    return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(_disp(x["value"]) for x in a["items"]), explanation_steps=steps, shape="geometric_series_items")


# --- 4. geometric_series_relation --------------------------------------------------------------------------------------------------

_TURTLE_UNIT = "公斤"


def _geometric_series_relation(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    kind = g["kind"]
    if kind == "two_terms":
        p, q, n = int(g["p"]), int(g["q"]), int(g["n"])
        question = f"已知 {_seq()} 為等比數列，且 {_t(_a(p) + '=' + tex(g['A']))}、{_t(_a(q) + '=' + tex(g['B']))}，求此等比數列前 {_t(str(n))} 項的和。"
        steps = [f"{_t('r^{' + str(q - p) + '}=' + tex(num(g['B']) / num(g['A'])))}，公比 {_t('r=' + ' 或 '.join(tex(r) for r in a['ratios']))}。",
                 "代入等比級數的和公式，前 " + str(n) + " 項的和為 " + "、".join(_t(tex(s)) for s in a["sums"]) + "。"]
        parts = [_set_part(1, a["sums"], "和（若有兩個值請用逗號分開）")]
        return _parts_payload(matrix, question=question, parts=parts, display_answer="、".join(a["sums"]), explanation_steps=steps, shape=kind)
    if kind == "consecutive_triples":
        n = int(g["n"])
        question = (f"已知 {_seq()} 為等比數列，且 {_t(_a(1) + '+' + _a(2) + '+' + _a(3) + '=' + tex(g['A']))}、{_t(_a(2) + '+' + _a(3) + '+' + _a(4) + '=' + tex(g['B']))}，"
                    f"求此等比數列前 {_t(str(n))} 項的和。")
        steps = [f"第二式 = 第一式 × 公比，所以 {_t('r=' + tex(a['ratio']))}，{_t(_a(1) + '=' + tex(a['a1']))}，前 {n} 項的和為 {_t(tex(a['sum']))}。"]
        return _parts_payload(matrix, question=question, parts=[_value_part(1, a["sum"], "和")], display_answer=a["sum"], explanation_steps=steps, shape=kind)
    if kind == "first_last_sum":
        question = f"已知等比數列 {_seq()} 的首項為{text(g['a1'])}，末項為{text(g['last'])}，和為{text(g['S'])}，求此等比數列的公比與項數。"
        parts = [_value_part(1, a["ratio"], "(1) 公比"), _value_part(2, str(a["n"]), "(2) 項數")]
        steps = [f"{_t('S=' + _FRAC + 'a_{1}-r@cdot a_{n}}{1-r}')}，解得公比 {_t('r=' + tex(a['ratio']))}，再由末項求得共 {a['n']} 項。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"公比 {a['ratio']}，項數 {a['n']}", explanation_steps=steps, shape=kind)
    if kind == "layers":
        layers, w, frac = int(g["layers"]), g["W"], g["frac"]
        question = (f"一隻大烏龜背著兩隻中烏龜，這兩隻中烏龜的重量都是大烏龜的 {_t(tex(frac))}，又每隻中烏龜又背著兩隻小烏龜，這兩隻小烏龜的重量也都是中烏龜的 {_t(tex(frac))}，"
                    f"如此堆疊上去，共堆了 {_t(str(layers))} 層。已知大烏龜有 {_t(text(w))} 公斤重，求所有烏龜重量的總和。")
        steps = [f"每一層的總重量是上一層的 {_t('2@times ' + tex(frac) + '=' + tex(a['ratio']))} 倍，成等比級數，首項 {tex(w)}，共 {layers} 項，總和為 {_t(tex(a['total']))} 公斤。"]
        return _parts_payload(matrix, question=question, parts=[_value_part(1, a["total"], "總重量（公斤）")], display_answer=a["total"], explanation_steps=steps, shape=kind)
    if kind == "square_areas":
        k = int(g["k"])
        question = f"右圖中，已知 {_t('@angle A=45{}^@circ')}、{_t('{@overline{AB}}=1')}，且 {_t('T_{1}、T_{2}、T_{3},@ldots')} 都是正方形，求前 {_t(str(k))} 個正方形面積的總和。"
        steps = ["因為 ∠A=45°，每個正方形的邊長都是前一個的 2 倍，邊長 1, 2, 4, … 成等比數列；面積 1, 4, 16, … 成公比 4 的等比數列。",
                 f"前 {k} 個正方形的面積和為 {_t(_FRAC + '1@times (1-4^{' + str(k) + '})}{1-4}=' + tex(a['total']))}。"]
        return _parts_payload(matrix, question=question, parts=[_value_part(1, a["total"], "面積總和")], display_answer=a["total"], explanation_steps=steps, shape=kind, figure=True)
    if kind == "blue_squares":
        side, n = int(g["side"]), int(g["n"])
        question = (f"取一個邊長為 {_t(str(side))} 的白色正方形，將其等分成 {_t('4')} 個相同的正方形，然後將左上及右下的正方形塗成藍色；接著再將剩下的 {_t('2')} 個白色小正方形，"
                    f"分別等分成 {_t('4')} 個相同的更小正方形，並將左上及右下更小的正方形塗成藍色。重複這樣的步驟，如下圖所示。\n依此規律可畫第 {_t('4')} 圖、第 {_t('5')} 圖、……。\n"
                    f"(1)求第 {_t(str(n))} 圖藍色正方形的總數。\n(2)求第 {_t(str(n))} 圖所有藍色正方形的面積和。")
        parts = [_value_part(1, str(a["count"]), "(1) 總數"), _value_part(2, a["area"], "(2) 面積和")]
        steps = [f"第 k 次新增 {_t('2^{k}')} 個藍色正方形，邊長 {_t(str(side) + '@div 2^{k}')}；到第 {n} 圖共 {_t('2+4+@cdots +2^{' + str(n) + '}=' + str(a['count']))} 個。",
                 f"面積和為 {_t(tex(a['area']))}。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"{a['count']}；{a['area']}", explanation_steps=steps, shape=kind, figure=True)
    raise ValueError(f"unsupported_kind:{kind}")


# --- 5. partial_sum_terms ------------------------------------------------------------------------------------------------------------

def _sn_tex(form: dict[str, Any]) -> str:
    if form["kind"] == "exp":
        c, b = num(form["c"]), num(form["base"])
        lead = "" if c == 1 else tex(c)
        return f"{lead}{tex(b)}^{{n}}" + ("-" if c > 0 else "+") + tex(abs(c))
    a_, b_ = num(form["a"]), num(form["b"])
    out = ("-" if a_ < 0 else "") + ("" if abs(a_) == 1 else tex(abs(a_))) + "n^{2}"
    if b_ != 0:
        out += ("+" if b_ > 0 else "-") + ("" if abs(b_) == 1 else tex(abs(b_))) + "n"
    return out


def _partial_sum_terms(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    sn = _sn_tex(g["form"])
    asks = [v["ask"] for v in a["values"]]
    head = f"已知數列 {_seq()} {g.get('style', '前n項和')} {_t('S_{n}=' + sn)}"
    parts, lines, steps = [], [], []
    for i, v in enumerate(a["values"], 1):
        if v["ask"][0] == "a":
            k = v["ask"][1]
            lines.append(f"求 {_t(_a(k))} 的值")
            parts.append(_value_part(i, v["value"], f"({i}) {'a' + str(k)}"))
            steps.append(f"{_t(_a(k) + '=S_{' + str(k) + '}-S_{' + str(k - 1) + '}=' + tex(v['value']))}" if k > 1 else f"{_t(_a(1) + '=S_{1}=' + tex(v['value']))}")
        else:
            lines.append("寫出一般項 " + _t(_a("n")) + " 的公式")
            parts.append(_expr_part(i, v["value"], f"({i}) a_n 的式子"))
            steps.append(f"當 {_t('n@ge 2')} 時 {_t(_a('n') + '=S_{n}-S_{n-1}')}，且 {_t(_a(1) + '=S_{1}')} 也符合，所以 {_t(_a('n') + '=' + sp_tex(v['value']))}。")
    if len(a["values"]) == 2 and asks[0] == ["a", 1] and asks[1] == ["general"]:
        question = head + "，求 " + _t(_a(1)) + " 的值並寫出 " + _t(_a("n")) + " 的一般項。"
    else:
        question = head + "。\n" + "\n".join(f"({i}){line}。" for i, line in enumerate(lines, 1))
    display = "；".join((f"a{v['ask'][1]}={v['value']}" if v["ask"][0] == "a" else f"aₙ={_pretty(v['value'])}") for v in a["values"])
    return _parts_payload(matrix, question=question, parts=parts, display_answer=display, explanation_steps=steps, shape="partial_sum_terms")


def sp_tex(expr: str) -> str:
    import sympy as sp

    return sp.latex(sp.sympify(expr, locals={"n": sp.Symbol("n")}))


# --- 6. power_sums -------------------------------------------------------------------------------------------------------------------------

def _prefix(item: dict[str, Any]) -> str:
    first, step = int(item["first"]), int(item["step"])
    if step == 1:
        return "連續正整數的"
    if step == 2:
        return "連續正偶數的" if first % 2 == 0 else "連續正奇數的"
    if first == step:
        return f"連續 {_t(str(step))} 的倍數之"
    return "下列等差排列整數的"


def _power_series_tex(item: dict[str, Any]) -> str:
    first, step, last, p = int(item["first"]), int(item["step"]), int(item["last"]), int(item["p"])
    return _series_tex(first, step, f"{last}^{{{p}}}", 3, power=p)


def _power_sums(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    kind = g["kind"]
    if kind == "sum_ranges":
        items, layout = g["items"], g.get("layout", "named_items")
        word = {2: "平方和", 3: "立方和"}
        if layout == "intro_items":
            question = f"求下列{_prefix(items[0])}{word[int(items[0]['p'])]}。\n" + "\n".join(f"({i}){_t(_power_series_tex(it))}。" for i, it in enumerate(items, 1))
        elif layout == "single":
            it = items[0]
            question = f"求{_prefix(it)}{word[int(it['p'])]}：{_t(_power_series_tex(it))}。"
        elif layout == "intro_named":
            question = "求下列各級數的和。\n" + "\n".join(f"({i}){_prefix(it)}{word[int(it['p'])]}：{_t(_power_series_tex(it))}。" for i, it in enumerate(items, 1))
        else:
            question = "\n".join(f"({i})求{_prefix(it)}{word[int(it['p'])]}：{_t(_power_series_tex(it))}。" for i, it in enumerate(items, 1))
        parts = [_value_part(i, v, f"({i}) 和" if len(items) > 1 else "和") for i, v in enumerate(a["values"], 1)]
        steps = [f"({i}) 利用 {_t('1^{' + str(it['p']) + '}+2^{' + str(it['p']) + '}+@cdots +n^{' + str(it['p']) + '}')} 的公式（必要時提出公因數或相減），得 {_t(tex(v))}。" for i, (it, v) in enumerate(zip(items, a["values"]), 1)]
        return _parts_payload(matrix, question=question, parts=parts, display_answer="；".join(a["values"]), explanation_steps=steps, shape=kind)
    if kind == "layer_split":
        layers, top = int(g["layers"]), int(g["top"])
        question = (f"兩兄弟將收成的蘋果堆成 {_t(str(layers))} 層的正方形垛，從最下層堆起每一層都是正方形，由上而下各層的個數依次為 {_t('1^{2}')}、{_t('2^{2}')},…,"
                    f"{_t(str(layers - 2) + '^{2}')}、{_t(str(layers - 1) + '^{2}')}、{_t(str(layers) + '^{2}')}。\n若哥哥拿走上面 {_t(str(top))} 層，弟弟拿走下面 {_t(str(layers - top))} 層，試問：弟弟拿走的蘋果比哥哥多幾個？")
        steps = [f"哥哥拿走 {_t('1^{2}+@cdots +' + str(top) + '^{2}=' + tex(a['top']))} 個，弟弟拿走 {_t(str(top + 1) + '^{2}+@cdots +' + str(layers) + '^{2}=' + tex(a['bottom']))} 個，差為 {_t(tex(a['difference']))}。"]
        return _parts_payload(matrix, question=question, parts=[_value_part(1, a["difference"], "多幾個")], display_answer=a["difference"], explanation_steps=steps, shape=kind)
    if kind == "cube_total_inverse":
        question = f"官府每日招兵人數均為立方數，依序為：首日招 {_t('1')} 人，次日招 {_t('8')} 人，第三日招 {_t('27')} 人，……，以此類推。已知總共招兵 {_t(str(a['total']))} 人，求官府招兵的總日數。"
        steps = [f"{_t('1^{3}+2^{3}+@cdots +n^{3}=' + '@left[' + _FRAC + 'n(n+1)}{2}@right]^{2}=' + str(a['total']))}，所以 {_t(_FRAC + 'n(n+1)}{2}=' + str(int(a['total'] ** 0.5)))}，{_t('n=' + str(a['n']))}。"]
        return _parts_payload(matrix, question=question, parts=[_value_part(1, str(a["n"]), "總日數")], display_answer=str(a["n"]), explanation_steps=steps, shape=kind)
    if kind == "tower":
        layers = int(g["layers"])
        question = (f"右圖為使用高腳杯堆疊而成的香檳塔，最頂層有 {_t('1')} 個杯子，往下的每一層都排成正方形，第 {_t('2')} 層每邊有 {_t('2')} 個杯子，第 {_t('3')} 層每邊有 {_t('3')} 個杯子，……，以此類推。"
                    f"仿照上面的方式，堆成 {_t(str(layers))} 層高的香檳塔，試回答下列問題。\n(1)第 {_t(str(layers))} 層有幾個高腳杯？（單選）\n(2)堆成 {_t(str(layers))} 層高的香檳塔需要準備多少個高腳杯？")
        cands = [str(layers), f"{layers}²", "1+2+3+⋯+" + str(layers), "1²+2²+3²+⋯+" + f"{layers}²"]
        choices = [{"label": "ABCD"[pos], "value": _CIRCLED[pos] + cands[idx]} for pos, idx in enumerate(g["order"])]
        parts = [_choice_part(1, a["correct_option"], choices, "(1) 選項"), _value_part(2, a["total"], "(2) 高腳杯數")]
        steps = [f"(1) 第 {layers} 層排成正方形，每邊 {layers} 個，共 {_t(str(layers) + '^{2}')} 個。",
                 f"(2) {_t('1^{2}+2^{2}+@cdots +' + str(layers) + '^{2}=' + _FRAC + str(layers) + '(' + str(layers) + '+1)(2@times ' + str(layers) + '+1)}{6}=' + tex(a['total']))}。"]
        return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1){a['correct_option']}；(2){a['total']}", explanation_steps=steps, shape=kind, figure=True)
    raise ValueError(f"unsupported_kind:{kind}")


# --- 7. series_statements ------------------------------------------------------------------------------------------------------------

_CLAIM_TEX = {"square_of_sum": "\\left(1+2+3+\\cdots +n\\right)^{2}", "quarter_form": "\\frac{n^{2}(n+1)^{2}}{4}",
              "half_form": "\\frac{n^{2}(n+1)^{2}}{2}", "squares_form": "\\frac{n(n+1)(2n+1)}{6}"}


def _series_statements(matrix: dict[str, Any]) -> dict[str, Any]:
    st, a = matrix["givens"]["statement"], matrix["answer"]
    truth = bool(a["truth"])
    if st["kind"] == "ap_center":
        k, c = int(st["k"]), int(st["c"])
        sentence = f"等差數列 {_seq()} 恆有 {_t('+'.join(_a(i) for i in range(1, k + 1)) + '=' + str(k) + _a(c))}。"
        reason = (f"等差數列 {k} 項的和等於項數乘以中間項 {_t(_a((k + 1) // 2))}，所以敘述正確。" if truth
                  else f"{k} 項的和應為 {_t(str(k) + _a((k + 1) // 2))}" + ("" if k % 2 else "（項數為偶數時沒有單一中間項）") + "，敘述錯誤。")
    elif st["kind"] == "gp_formula":
        r, m, e = int(st["r"]), int(st["m"]), int(st["e"])
        sentence = f"等比級數 {_t('1+' + str(r) + '+' + str(r * r) + '+' + _CDOTS + '+' + str(r) + '^{' + str(m) + '}')} 的和為 {_t(_FRAC + str(r) + '^{' + str(e) + '}-1}{' + str(r - 1) + '}')}。"
        reason = ("公式 " + _t(_FRAC + 'r^{m+1}-1}{r-1}') + f" 中 m={m}，指數應為 {m + 1}，所以敘述" + ("正確。" if truth else "錯誤。"))
    else:
        sentence = f"級數 {_t('1^{3}+2^{3}+3^{3}+' + _CDOTS + '+n^{3}=' + _CLAIM_TEX[st['claim']])}。"
        reason = "立方和公式為 " + _t('1^{3}+2^{3}+@cdots +n^{3}=@left[' + _FRAC + 'n(n+1)}{2}@right]^{2}') + "，所以敘述" + ("正確。" if truth else "錯誤。")
    question = "下列敘述對的打「○」，錯的打「×」。\n" + sentence
    return _single_payload(matrix, question=question, part=_choice_part(1, "A" if truth else "B", [dict(c) for c in TRUE_FALSE_CHOICES]),
                           display_answer="○" if truth else "×", explanation_steps=[reason], shape="single_choice")


# --- 8. fish_rows ---------------------------------------------------------------------------------------------------------------------

def _fish_rows(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    k = int(g["k"])
    question = ("古代陣法中，「魚鱗陣」的將領位於陣形的正後方，士兵依右圖排列：第 " + _t("1") + " 列有 " + _t("1") + " 人、第 " + _t("2") + " 列有 " + _t("3") + " 人、第 " + _t("3")
                + " 列有 " + _t("5") + " 人、……，以此類推。\n(1)求前 " + _t(str(k)) + " 列的士兵總人數。\n(2)求前 " + _t("n") + " 列的士兵總人數。")
    steps = [f"各列人數 1, 3, 5, … 是首項 1、公差 2 的等差數列。(1) {_t('S_{' + str(k) + '}=' + _FRAC + str(k) + '(2@times 1+(' + str(k) + '-1)@times 2)}{2}=' + str(k) + '^{2}=' + tex(a['first_k']))}。",
             f"(2) {_t('S_{n}=' + _FRAC + 'n(2@times 1+(n-1)@times 2)}{2}=n^{2}')}。"]
    parts = [_value_part(1, a["first_k"], "(1) 人數"), _expr_part(2, a["general"], "(2) n 列的人數")]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"{a['first_k']}；n²", explanation_steps=steps, shape="fish_rows", figure=True)


_PAYLOAD_BUILDERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "arithmetic_series_items": _arithmetic_series_items,
    "arithmetic_series_relation": _arithmetic_series_relation,
    "geometric_series_items": _geometric_series_items,
    "geometric_series_relation": _geometric_series_relation,
    "partial_sum_terms": _partial_sum_terms,
    "power_sums": _power_sums,
    "series_statements": _series_statements,
    "fish_rows": _fish_rows,
}


def adapt_series_summation_matrix(matrix: dict[str, Any], *, domain_operation: str, **_kwargs: Any) -> dict[str, Any]:
    operation = str(domain_operation or "")
    if matrix.get("domain_operation") != operation:
        raise ValueError(f"domain_operation_mismatch:{matrix.get('domain_operation')}:{operation}")
    builder = _PAYLOAD_BUILDERS.get(operation)
    if builder is None:
        raise ValueError(f"unsupported_series_summation_operation:{operation}")
    return builder(matrix)
