"""Payload contracts for the recurrence operations of sequence.progression (普高數學2 Unit 1, 遞迴關係式).

The recurrence is answered as the missing pieces of a template (框內的值): free-form recurrence equations cannot be graded
soundly by any shared checker, while a first term, a ratio / increment or an expression in ``n`` can.
"""

from __future__ import annotations

from typing import Any

from .sequence_progression_adapter import (
    _EXPR,
    _LANGLE,
    _RANGLE,
    _RATIONAL,
    _a,
    _choice_part,
    _disp,
    _parts_payload,
    _part,
    _recurrence_tex,
    _single_payload,
    _t,
    _value_part,
    TRUE_FALSE_CHOICES,
)
from .sequence_progression_domain import num, tex

_BOX = "\\boxed{\\ }"
_GE2 = "\\ge 2"
_GE1 = "\\ge 1"
_TIMES = "\\times "
_SEQ = _t(_LANGLE + "a_{n}" + _RANGLE)


def _expr_part(index: int, expected: str, label: str) -> dict[str, Any]:
    return _part(index, expected, *_EXPR, label=label, prompt=label)


def _int_part(index: int, value: Any, label: str) -> dict[str, Any]:
    return _part(index, str(value), *_RATIONAL, label=label, prompt=label)


# --- recurrence_from_process --------------------------------------------------------------------------------------------

_SHAPES = {
    "triangle": ("正三角形", "小正三角形", "塗成黑色", "白色三角形"),
    "square": ("正方形", "小正方形", "塗成藍色", "白色正方形"),
    "segment": ("線段", "線段", "刪除", "線段"),
}


def _subdivision(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    shape, parts, removed, ratio = g["shape"], int(g["parts"]), int(g["removed"]), int(a["ratio"])
    obj, piece, act, count = _SHAPES[shape]
    where = g.get("where", "")
    if removed == 1 and where:
        phrase = f"將{where}的{piece if shape != 'segment' else '那一段'}{act}"
        phrase = phrase.replace("的那一段", "那一段") if shape == "segment" else phrase
    else:
        phrase = f"將其中 ${removed}$ 個{piece if shape != 'segment' else '線段'}{act}"
    head = "白色" if shape != "segment" else ""
    intro = (f"取一個{head}{obj}，將其等分成 ${parts}$ 個相同的{piece}，然後{phrase}；接著再將剩下的 ${ratio}$ 個{head}{piece}，分別等分成 ${parts}$ 個相同的"
             f"更小的{obj}，並{phrase}。重複這樣的步驟。\n"
             f"第 $1$ 圖是最初的{head}{obj}，第 $2$ 圖是第一次{act}後的圖形，依此規律可畫第 $3$ 圖、第 $4$ 圖、……，並設 $a_{{n}}$ 為第 $n$ 圖中{count}的總數。")
    template = _t("a_{1}=" + _BOX + ",\\ a_{n}=" + _BOX + _TIMES + "a_{n-1}\\ (n" + _GE2 + ")")
    if a["ask"] == "value":
        k = int(a["k"])
        second, tail = f"(2)求 {_t(_a(k))} 的值。", _value_part(3, a["a_k"], f"(2) a{k}")
    else:
        second, tail = f"(2)從第幾個圖開始，{count}的總數會超過 ${a['limit']}$ 個？", _int_part(3, a["first_n"], "(2) 第幾個圖")
    question = f"{intro}\n(1)寫出數列 {_SEQ} 的遞迴關係式 {template}，請分別填入兩個框內的值。\n{second}"
    parts_ = [_int_part(1, a["a1"], "(1) 第一個框（首項 a1）"), _int_part(2, a["ratio"], "(1) 第二個框（乘以 a_{n-1} 的倍數）"), tail]
    relation = _t("a_{1}=" + a["a1"] + _COMMA + "a_{n}=" + a["ratio"] + "a_{n-1}")
    steps = [f"每一個白色{'線段' if shape == 'segment' else '圖形'}分成 ${parts}$ 份後有 ${removed}$ 份被{act}，所以每次剩下的個數變成原來的 ${ratio}$ 倍：{relation}。"]
    steps.append(f"所以 {_t('a_{n}=' + a['a1'] + _TIMES + a['ratio'] + '^{n-1}')}，" + (f"{_t(_a(int(a['k'])) + '=' + a['a_k'])}。" if a["ask"] == "value"
                 else f"當 {_t('n=' + str(a['first_n']))} 時 {_t('a_{n}=' + str(int(a['a1']) * int(a['ratio']) ** (a['first_n'] - 1)))} 首次超過 ${a['limit']}$。"))
    shown = f"(1) a₁={a['a1']}，倍數 {a['ratio']}；(2) " + (a["a_k"] if a["ask"] == "value" else f"第{a['first_n']}個圖")
    return _parts_payload(matrix, question=question, parts=parts_, display_answer=shown, explanation_steps=steps, shape="recurrence_process")


_COMMA = ",\\ "


def _tearing(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    s, q, k, T = g["start"], g["pieces"], int(a["k"]), g["target"]
    template = _t("a_{n}=a_{n-1}+" + _BOX + "\\ (n" + _GE1 + ")")
    question = (f"桌上有 ${s}$ 張紙，每一次操作都把其中一張紙撕成 ${q}$ 張。設 $a_{{n}}$ 代表經過 $n$ 次操作後，桌面上大小不同紙張的總數（$a_{{0}}={s}$）。\n"
                f"(1)求 {_t(_a(k))} 的值。\n(2)寫出數列 {_SEQ} 的遞迴關係式 {template}，請填入框內的值。\n(3)經幾次操作後，桌面上剛好有 ${T}$ 張紙？")
    parts = [_int_part(1, a["a_k"], f"(1) a{k}"), _int_part(2, a["d"], "(2) 框內的值"), _int_part(3, a["n"], "(3) 操作次數")]
    steps = [f"每次操作少 $1$ 張、多 ${q}$ 張，淨增加 ${a['d']}$ 張：{_t('a_{n}=a_{n-1}+' + a['d'])}。",
             f"{_t(_a(k) + '=' + str(s) + '+' + str(k) + _TIMES + a['d'] + '=' + a['a_k'])}。",
             f"令 {_t(str(s) + '+n' + _TIMES + a['d'] + '=' + str(T))}，得 {_t('n=' + str(a['n']))}。"]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1) {a['a_k']}；(2) {a['d']}；(3) {a['n']} 次", explanation_steps=steps, shape="recurrence_process")


def _row_sums(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    f, s, k = int(g["first"]), int(g["step"]), int(a["k"])
    template = _t("a_{n}=a_{n-1}+" + _BOX + "\\ (n" + _GE2 + ")")
    question = (f"古代陣法中，「魚鱗陣」的將領位於陣形的正後方，士兵依序排列：第 $1$ 列有 ${f}$ 人、第 $2$ 列有 ${f + s}$ 人、第 $3$ 列有 ${f + 2 * s}$ 人、……，以此類推。"
                f"設 $a_{{n}}$ 是前 $n$ 列士兵的總人數。\n(1)求 $a_{{1}}$、$a_{{2}}$、$a_{{3}}$、$a_{{4}}$ 的值。\n"
                f"(2)寫出數列 {_SEQ} 的遞迴關係式 {template}，框內是 $n$ 的式子，請填入。\n(3)求 {_t(_a(k))} 的值。")
    parts = [_int_part(i, v, f"(1) a{i}") for i, v in enumerate(a["first_terms"], start=1)]
    parts += [_expr_part(5, a["increment"], "(2) 框內的式子"), _int_part(6, a["a_k"], f"(3) a{k}")]
    steps = [f"(1) 前 $n$ 列人數累加：{_t(', '.join(a['first_terms']))}。",
             f"(2) 第 $n$ 列有 {_t(tex(a['increment']))} 人，所以 {_t('a_{n}=a_{n-1}+(' + tex(a['increment']) + ')')}。", f"(3) {_t(_a(k) + '=' + a['a_k'])}。"]
    shown = f"(1) {', '.join(a['first_terms'])}；(2) {a['increment']}；(3) {a['a_k']}"
    return _parts_payload(matrix, question=question, parts=parts, display_answer=shown, explanation_steps=steps, shape="recurrence_process")


def _array_row_end(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    st, f, k = int(g["start"]), int(g["first_row"]), int(a["k"])
    nums = "所有的正整數" if st == 1 else f"從 ${st}$ 開始的所有正整數"
    template = _t("a_{n}=a_{n-1}+" + _BOX + "\\ (n" + _GE2 + ")")
    question = (f"將{nums}依序排列如下：第一列有 ${f}$ 個數字，第二列有 ${f + 1}$ 個數字，第三列有 ${f + 2}$ 個數字，……；下一列都比上一列增加 $1$ 個數字，以此類推。"
                f"設 $a_{{n}}$ 代表第 $n$ 列最右邊的數字（$a_{{1}}={a['shown_terms'][0]}$、$a_{{2}}={a['shown_terms'][1]}$、$a_{{3}}={a['shown_terms'][2]}$,…）。\n"
                f"(1)寫出數列 {_SEQ} 的遞迴關係式 {template}，框內是 $n$ 的式子，請填入。\n(2)求 {_t(_a(k))} 的值。")
    parts = [_expr_part(1, a["increment"], "(1) 框內的式子"), _int_part(2, a["a_k"], f"(2) a{k}")]
    steps = [f"第 $n$ 列有 {_t(tex(a['increment']))} 個數字，第 $n$ 列最右邊的數字比第 $n-1$ 列最右邊的數字多這麼多個：{_t('a_{n}=a_{n-1}+(' + tex(a['increment']) + ')')}。",
             f"依序算出 {_t(_a(k) + '=' + a['a_k'])}。"]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1) {a['increment']}；(2) {a['a_k']}", explanation_steps=steps, shape="recurrence_process")


def _nested_polygon(matrix: dict[str, Any]) -> dict[str, Any]:
    g, a = matrix["givens"], matrix["answer"]
    P, k, square = g["P"], int(a["k"]), g["shape"] == "square"
    if square:
        intro = ("以正方形 $T_{1}$ 各邊中點為頂點連成四邊形 $T_{2}$，再以 $T_{2}$ 各邊中點為頂點連成四邊形 $T_{3}$，如此繼續下去，可得到一系列的正方形 $T_{1}$、$T_{2}$、$T_{3}$,…。"
                 f"設 $T_{{1}}$ 的周長為 ${tex(P)}$，並令 $a_{{n}}$ 表正方形 $T_{{n}}$ 的周長。")
    else:
        intro = ("以正三角形 $T_{1}$ 各邊中點為頂點連成三角形 $T_{2}$，再以 $T_{2}$ 各邊中點為頂點連成三角形 $T_{3}$，如此繼續下去，可得到一系列的正三角形 $T_{1}$、$T_{2}$、$T_{3}$,…。"
                 f"設 $T_{{1}}$ 的周長為 ${tex(P)}$，並令 $a_{{n}}$ 表正三角形 $T_{{n}}$ 的周長。")
    template = _t("a_{n}=" + _BOX + _TIMES + "a_{n-1}\\ (n" + _GE2 + ")")
    question = f"{intro}\n(1)寫出數列 {_SEQ} 的遞迴關係式 {template}，請填入框內的值。\n(2)求 {_t(_a(k))} 的值。"
    parts = [_value_part(1, a["ratio"], "(1) 框內的值"), _value_part(2, a["a_k"], f"(2) a{k}")]
    why = "新正方形的邊長是原邊長的 $\\frac{\\sqrt{2}}{2}$ 倍（中點連線是直角邊為原邊一半的斜邊）" if square else "新三角形的邊長是原邊長的 $\\frac{1}{2}$（中點連線）"
    steps = [f"{why}，周長也變為 {_t(tex(a['ratio']))} 倍：{_t('a_{n}=' + tex(a['ratio']) + 'a_{n-1}')}。",
             f"{_t(_a(k) + '=' + tex(P) + '(' + tex(a['ratio']) + ')^{' + str(k - 1) + '}=' + tex(a['a_k']))}。"]
    return _parts_payload(matrix, question=question, parts=parts, display_answer=f"(1) {_disp(a['ratio'])}；(2) {_disp(a['a_k'])}", explanation_steps=steps, shape="recurrence_process")


_BUILDERS = {"subdivision": _subdivision, "tearing": _tearing, "row_sums": _row_sums, "array_row_end": _array_row_end, "nested_polygon": _nested_polygon}


def recurrence_from_process_payload(matrix: dict[str, Any]) -> dict[str, Any]:
    return _BUILDERS[matrix["answer"]["kind"]](matrix)


# --- geometric numbers with a sum relation ---------------------------------------------------------------------------------

def geo_sum_relation_payload(matrix: dict[str, Any]) -> dict[str, Any]:
    c, a = matrix["givens"]["c"], matrix["answer"]
    rel = "a_{3}=a_{2}+a_{1}" if num(c) == 1 else "a_{3}=a_{2}+" + tex(c) + "a_{1}"
    if num(c) == 1:
        question = ("人類的大拇指自指尖到腕骨是由三塊骨頭所組成的，令自指尖到腕骨的這三塊骨頭的長度分別為 $a_{1}$、$a_{2}$、$a_{3}$。"
                    f"據統計，當 $a_{{1}}$、$a_{{2}}$、$a_{{3}}$ 成等比數列且滿足 {_t(rel)} 時，大拇指的型態被認為是最完美的。試求完美大拇指三塊骨頭長度的公比。")
    else:
        question = f"已知三個正數 $a_{{1}}$、$a_{{2}}$、$a_{{3}}$ 成等比數列且滿足 {_t(rel)}，求公比。"
    part = _value_part(1, a["ratio"], "")
    powers = _t("a_{2}=a_{1}r" + _COMMA + "a_{3}=a_{1}r^{2}")
    steps = [f"設公比為 $r$，則 {powers}，代入 {_t(rel)} 得 {_t('r^{2}=r+' + tex(c))}。",
             f"解 {_t('r^{2}-r-' + tex(c) + '=0')}，取正根 {_t('r=' + tex(a['ratio']))}（公比為正）。"]
    return _single_payload(matrix, question=question, part=part, display_answer=_disp(a["ratio"]), explanation_steps=steps, shape="progression_value")


# --- ○× on a stated recurrence ---------------------------------------------------------------------------------------------------

def recurrence_term_claim_payload(matrix: dict[str, Any]) -> dict[str, Any]:
    st, a = matrix["givens"]["statement"], matrix["answer"]
    truth, k = bool(a["truth"]), int(st["k"])
    sentence = (f"若數列 {_SEQ} 遞迴關係式為 {_t(_recurrence_tex(st['type'], st['a1'], st['c']))}，則 {_t(_a(k) + '=' + tex(st['value']))}")
    question = "下列敘述對的打「○」，錯的打「×」。\n" + sentence + "。"
    steps = [f"依遞迴關係式逐項算出 {_t(_a(k) + '=' + tex(a['actual']))}，所以敘述{'正確' if truth else '錯誤'}。此敘述為「{'○' if truth else '×'}」。"]
    return _single_payload(matrix, question=question, part=_choice_part(1, "A" if truth else "B", [dict(c) for c in TRUE_FALSE_CHOICES]),
                           display_answer="○" if truth else "×", explanation_steps=steps, shape="single_choice")
