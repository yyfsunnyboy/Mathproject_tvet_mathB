"""B3 Chapter 3 domain: two-variable systems, half-planes, and linear programming.

Generators sample parameters and call this module. Mathematical truth stays here.
"""
from __future__ import annotations

import random
from fractions import Fraction
from typing import Any

DOMAIN_KEY = "linear.inequality.planning"

SYSTEM_ORDERED_PAIR = "system_ordered_pair"
SYSTEM_LINEAR_COMBO = "system_linear_combo"
SYSTEM_WORD_TWO = "system_word_two"
SYSTEM_ABS_PAIR = "system_abs_pair"
SYSTEM_CONTINUED_RATIO = "system_continued_ratio"
SYSTEM_PARAMETER_UNIQUE = "system_parameter_unique"
SYSTEM_PARAMETER_CASES = "system_parameter_cases"
SYSTEM_DEPENDENT_VALUE = "system_dependent_value"
SYSTEM_KNOWN_SOLUTION = "system_known_solution"
LINE_SLOPE_PAIR = "line_slope_pair"
LINE_PAIR_RELATION = "line_pair_relation"
INTEGER_FEASIBLE_COUNT = "integer_feasible_count"
INTEGER_FEASIBLE_CHOICE = "integer_feasible_choice"
HALFPLANE_REGION = "halfplane_region"
SHADE_TO_INEQUALITY = "shade_to_inequality"
SAME_SIDE_TEST = "same_side_test"
SAME_SIDE_PARAMETER = "same_side_parameter"
SYSTEM_REGION_CORNER = "system_region_corner"
SHADE_TO_SYSTEM = "shade_to_system"
LABELED_REGION_CHOICE = "labeled_region_choice"
FEASIBLE_AREA = "feasible_area"
INTEGER_POINTS_COUNT = "integer_points_count"
LP_EXTREMA = "lp_extrema"
LP_APPLICATION = "lp_application"
CONSTRAINT_SYSTEM_CHOICE = "constraint_system_choice"

OPS = frozenset({
    SYSTEM_ORDERED_PAIR,
    SYSTEM_LINEAR_COMBO,
    SYSTEM_WORD_TWO,
    SYSTEM_ABS_PAIR,
    SYSTEM_CONTINUED_RATIO,
    SYSTEM_PARAMETER_UNIQUE,
    SYSTEM_PARAMETER_CASES,
    SYSTEM_DEPENDENT_VALUE,
    SYSTEM_KNOWN_SOLUTION,
    LINE_SLOPE_PAIR,
    LINE_PAIR_RELATION,
    INTEGER_FEASIBLE_COUNT,
    INTEGER_FEASIBLE_CHOICE,
    HALFPLANE_REGION,
    SHADE_TO_INEQUALITY,
    SAME_SIDE_TEST,
    SAME_SIDE_PARAMETER,
    SYSTEM_REGION_CORNER,
    SHADE_TO_SYSTEM,
    LABELED_REGION_CHOICE,
    FEASIBLE_AREA,
    INTEGER_POINTS_COUNT,
    LP_EXTREMA,
    LP_APPLICATION,
    CONSTRAINT_SYSTEM_CHOICE,
})

SKILL_312 = "vh_數學B3_SubSection_3_1_2"
SKILL_313 = "vh_數學B3_SubSection_3_1_3"
SKILL_322 = "vh_數學B3_PlainHeading_3_2_2"
SKILL_323 = "vh_數學B3_PlainHeading_3_2_3"
SKILL_324 = "vh_數學B3_PlainHeading_3_2_4"
SKILL_331 = "vh_數學B3_SubSection_3_3_1"
SKILL_333 = "vh_數學B3_SubSection_3_3_3"
SKILL_334 = "vh_數學B3_SubSection_3_3_4"

SOURCE_SPECS: dict[int, dict[str, str]] = {}


def _bind(ids: list[int], skill_id: str, op: str, presentation: str, source_kind: str) -> None:
    for example_id in ids:
        SOURCE_SPECS[example_id] = {
            "skill_id": skill_id,
            "op": op,
            "presentation": presentation,
            "source_kind": source_kind,
        }


_bind([12042, 12043, 12044, 12045, 12055, 12056], SKILL_312, SYSTEM_ORDERED_PAIR, "short_answer", "textbook_example")
_bind([12046, 12047, 12058, 12063], SKILL_312, SYSTEM_WORD_TWO, "short_answer", "textbook_example")
_bind([12057], SKILL_312, SYSTEM_ABS_PAIR, "short_answer", "textbook_exercise")
_bind([12062], SKILL_312, SYSTEM_CONTINUED_RATIO, "short_answer", "textbook_exercise")
_bind([12107], SKILL_312, SYSTEM_LINEAR_COMBO, "single_choice", "self_assessment")
_bind([12117], SKILL_312, SYSTEM_ORDERED_PAIR, "single_choice", "self_assessment")
_bind([12118, 12119], SKILL_312, SYSTEM_WORD_TWO, "short_answer", "self_assessment")
_bind([12120], SKILL_312, SYSTEM_KNOWN_SOLUTION, "short_answer", "self_assessment")
_bind([12121], SKILL_312, SYSTEM_DEPENDENT_VALUE, "short_answer", "self_assessment")
_bind([12048, 12049, 12059], SKILL_313, LINE_SLOPE_PAIR, "short_answer", "textbook_example")
_bind([12050, 12051, 12060], SKILL_313, LINE_PAIR_RELATION, "single_choice", "textbook_example")
_bind([12052, 12053, 12061], SKILL_313, SYSTEM_PARAMETER_UNIQUE, "short_answer", "textbook_example")
_bind([12054], SKILL_313, SYSTEM_DEPENDENT_VALUE, "single_choice", "exam_practice")
_bind([12064], SKILL_313, SYSTEM_PARAMETER_CASES, "short_answer", "advanced_exercise")
_bind([12122], SKILL_313, SYSTEM_PARAMETER_UNIQUE, "short_answer", "self_assessment")
_bind([12123], SKILL_313, SYSTEM_PARAMETER_UNIQUE, "single_choice", "self_assessment")
_bind([12065], SKILL_322, INTEGER_FEASIBLE_CHOICE, "single_choice", "exam_practice")
_bind([12124], SKILL_322, INTEGER_FEASIBLE_COUNT, "short_answer", "self_assessment")
_bind(
    [12066, 12067, 12068, 12070, 12071, 12076, 12077, 12078, 12081, 12082, 12083],
    SKILL_323, HALFPLANE_REGION, "single_choice", "textbook_example",
)
_bind([12069, 12075], SKILL_323, SHADE_TO_INEQUALITY, "single_choice", "textbook_exercise")
_bind([12074], SKILL_323, SHADE_TO_INEQUALITY, "short_answer", "advanced_exercise")
_bind([12072, 12079, 12084], SKILL_324, SAME_SIDE_TEST, "short_answer", "textbook_example")
_bind([12073, 12080, 12085], SKILL_324, SAME_SIDE_PARAMETER, "short_answer", "textbook_example")
_bind([12108], SKILL_324, SAME_SIDE_TEST, "single_choice", "self_assessment")
_bind([12109], SKILL_324, SAME_SIDE_PARAMETER, "single_choice", "self_assessment")
_bind(
    [12086, 12087, 12097, 12098, 12099, 12102],
    SKILL_331, SYSTEM_REGION_CORNER, "short_answer", "textbook_example",
)
_bind([12101], SKILL_331, INTEGER_POINTS_COUNT, "short_answer", "textbook_exercise")
_bind([12088, 12089, 12100], SKILL_331, SHADE_TO_SYSTEM, "single_choice", "textbook_example")
_bind([12104], SKILL_331, FEASIBLE_AREA, "short_answer", "textbook_exercise")
_bind([12110], SKILL_331, LABELED_REGION_CHOICE, "single_choice", "self_assessment")
_bind([12111, 12112], SKILL_331, SHADE_TO_SYSTEM, "single_choice", "self_assessment")
_bind([12113], SKILL_331, FEASIBLE_AREA, "single_choice", "self_assessment")
_bind([12090, 12091, 12103], SKILL_333, LP_EXTREMA, "short_answer", "textbook_example")
_bind([12114, 12116], SKILL_333, LP_EXTREMA, "short_answer", "self_assessment")
_bind([12126], SKILL_333, LP_EXTREMA, "single_choice", "self_assessment")
_bind([12092, 12093, 12094, 12095, 12105, 12106], SKILL_334, LP_APPLICATION, "short_answer", "textbook_example")
_bind([12096], SKILL_334, LP_APPLICATION, "single_choice", "exam_practice")
_bind([12115, 12125], SKILL_334, CONSTRAINT_SYSTEM_CHOICE, "single_choice", "self_assessment")

_LABEL_BANNED = ("例", "隨堂", "基礎題", "進階題", "自我評量", "習題")


def _fmt(value: Fraction) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(int(value))
    return f"{value.numerator}/{value.denominator}"


def _tex_num(value: Fraction) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(int(value))
    sign = "-" if value < 0 else ""
    return rf"{sign}\dfrac{{{abs(value.numerator)}}}{{{value.denominator}}}"


def _term(coef: Fraction, var: str, *, leading: bool) -> str:
    coef = Fraction(coef)
    if coef == 0:
        return ""
    body = var if abs(coef) == 1 else f"{_tex_num(abs(coef))}{var}"
    if leading:
        return f"-{body}" if coef < 0 else body
    return f"-{body}" if coef < 0 else f"+{body}"


def _linear_expr(a: Fraction, b: Fraction, c: Fraction) -> str:
    parts = [
        _term(a, "x", leading=True),
        _term(b, "y", leading=a == 0),
        _term(c, "", leading=a == 0 and b == 0),
    ]
    # constant term uses the number itself
    const = ""
    if c != 0:
        shown = _tex_num(abs(c))
        if a == 0 and b == 0:
            const = f"-{shown}" if c < 0 else shown
        else:
            const = f"-{shown}" if c < 0 else f"+{shown}"
    text = "".join(p for p in parts[:2] if p) + const
    return text or "0"


def _rel(op: str) -> str:
    return {"<": "<", "<=": r"\le", ">": ">", ">=": r"\ge", "=": "="}[op]


def _ineq_tex(a: Fraction, b: Fraction, c: Fraction, op: str) -> str:
    """Render ax+by+c op 0, or a simpler form when a term is missing."""
    return rf"\({_linear_expr(a, b, c)}{_rel(op)}0\)"


def _system_tex(rows: list[tuple[Fraction, Fraction, Fraction]]) -> str:
    lines = " \\\\ ".join(rf"{_linear_expr(a, b, Fraction(0))}={_tex_num(c)}" for a, b, c in rows)
    return rf"\(\left\{{ \begin{{array}}{{l}} {lines} \end{{array}} \right.\)"


def _solve2(a1, b1, c1, a2, b2, c2) -> tuple[Fraction, Fraction]:
    det = Fraction(a1) * Fraction(b2) - Fraction(a2) * Fraction(b1)
    if det == 0:
        raise ValueError("system_not_unique")
    x = (Fraction(c1) * Fraction(b2) - Fraction(c2) * Fraction(b1)) / det
    y = (Fraction(a1) * Fraction(c2) - Fraction(a2) * Fraction(c1)) / det
    return x, y


def _pair_text(x: Fraction, y: Fraction) -> str:
    return f"({_fmt(x)}, {_fmt(y)})"


def _pack(
    *,
    op: str,
    question: str,
    answer: str,
    parts: dict[str, str] | None,
    presentation: str,
    answer_type: str,
    choices: list[dict[str, str]] | None,
    givens: dict[str, Any],
    visual: dict[str, Any] | None,
    explanation: str,
) -> dict[str, Any]:
    for token in _LABEL_BANNED:
        if token in question:
            raise ValueError(f"source_label_in_stem:{token}")
    if presentation == "single_choice":
        values = [row["value"] for row in choices or []]
        if len(values) != 4 or len(set(values)) != 4 or answer not in values:
            raise ValueError("mcq_contract")
    arity = len(parts) if parts else 1
    correct_label = ""
    if presentation == "single_choice":
        correct_label = next(row["label"] for row in (choices or []) if row["value"] == answer)
    return {
        "domain_key": DOMAIN_KEY,
        "domain_operation": op,
        "operation": op,
        "question": question,
        "question_text": question,
        "answer": {
            "value": parts or answer,
            "canonical_form": answer,
            "general_form": answer,
            "coefficients": [],
            "parts": parts or {},
            "part_labels": {key: key for key in parts} if parts else [],
        },
        "explanation": [explanation],
        "explanation_steps": [explanation],
        "distractors": [row["value"] for row in (choices or []) if row["value"] != answer],
        "givens": givens,
        "presentation_mode": presentation,
        "answer_type": answer_type,
        "choices": choices or [],
        "correct_label": correct_label,
        "semantic_answer": answer,
        "validation_facts": {
            "domain_operation": op,
            "exact_arithmetic": True,
            "multipart_count": arity,
            "semantic_answer": answer,
            "answer_type": answer_type,
            "presentation_mode": presentation,
        },
        "visual_spec": visual or {"kind": "none"},
        "params": givens,
    }


def _choices(correct: str, distractors: list[str]) -> list[dict[str, str]]:
    uniq: list[str] = []
    for item in distractors:
        if item != correct and item not in uniq:
            uniq.append(item)
    if len(uniq) < 3:
        raise ValueError("distractor_shortage")
    values = [correct, *uniq[:3]]
    random.Random(f"mcq:{correct}:{','.join(uniq[:3])}").shuffle(values)
    labels = ["A", "B", "C", "D"]
    return [{"label": label, "value": value, "text": value} for label, value in zip(labels, values)]


def _sample_system(rng: random.Random) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]:
    for _ in range(40):
        x = Fraction(rng.randint(-6, 6))
        y = Fraction(rng.randint(-6, 6))
        a1, b1 = Fraction(rng.choice([-3, -2, -1, 1, 2, 3])), Fraction(rng.choice([-3, -2, -1, 1, 2, 3]))
        a2, b2 = Fraction(rng.choice([-3, -2, -1, 1, 2, 3])), Fraction(rng.choice([-3, -2, -1, 1, 2, 3]))
        if a1 * b2 - a2 * b1 == 0:
            continue
        c1, c2 = a1 * x + b1 * y, a2 * x + b2 * y
        return a1, b1, c1, a2, b2, c2, x, y
    raise ValueError("system_sample_failed")


def _build_system_ordered_pair(rng: random.Random, presentation: str) -> dict[str, Any]:
    a1, b1, c1, a2, b2, c2, x, y = _sample_system(rng)
    question = f"解二元一次聯立方程組 {_system_tex([(a1, b1, c1), (a2, b2, c2)])}。"
    answer = _pair_text(x, y)
    explanation = f"用加減消去法或代入法，得 \\(x={_tex_num(x)}\\)、\\(y={_tex_num(y)}\\)。"
    choices = None
    if presentation == "single_choice":
        wrong = []
        for dx, dy in ((1, 0), (0, 1), (-1, 1), (1, -1)):
            wrong.append(_pair_text(x + dx, y + dy))
        choices = _choices(answer, wrong)
    return _pack(
        op=SYSTEM_ORDERED_PAIR, question=question, answer=answer, parts=None,
        presentation=presentation, answer_type="single_choice" if presentation == "single_choice" else "ordered_pair",
        choices=choices, givens={"a1": _fmt(a1), "b1": _fmt(b1), "c1": _fmt(c1), "a2": _fmt(a2), "b2": _fmt(b2), "c2": _fmt(c2)},
        visual=None, explanation=explanation,
    )


def _build_system_linear_combo(rng: random.Random, presentation: str) -> dict[str, Any]:
    a1, b1, c1, a2, b2, c2, x, y = _sample_system(rng)
    target = x + y
    question = f"若 {_system_tex([(a1, b1, c1), (a2, b2, c2)])}，則 \\(x+y=\\)"
    answer = _fmt(target)
    wrong = [_fmt(target + d) for d in (1, -1, 2, x, y) if Fraction(target + d) != target]
    return _pack(
        op=SYSTEM_LINEAR_COMBO, question=question, answer=answer, parts=None,
        presentation=presentation, answer_type="single_choice" if presentation == "single_choice" else "expression",
        choices=_choices(answer, wrong) if presentation == "single_choice" else None,
        givens={"x": _fmt(x), "y": _fmt(y)}, visual=None,
        explanation=f"解得 \\(x={_tex_num(x)}\\)、\\(y={_tex_num(y)}\\)，故 \\(x+y={_tex_num(target)}\\)。",
    )


def _build_system_word(rng: random.Random, presentation: str) -> dict[str, Any]:
    x = rng.randint(2, 9)
    y = rng.randint(2, 9)
    if x == y:
        y += 1
    p1, p2 = rng.choice([(3, 5), (4, 2), (2, 3), (5, 1)])
    q1, q2 = rng.choice([(2, 1), (1, 2), (3, 1), (1, 4)])
    if p1 * q2 - p2 * q1 == 0:
        q1, q2 = 1, 1
        if p1 == p2:
            q2 = 2
    total1 = p1 * x + p2 * y
    total2 = q1 * x + q2 * y
    question = (
        f"某水果攤的甲顧客買了{p1}公斤橘子與{p2}公斤香蕉，付了{total1}元；"
        f"乙顧客買了{q1}公斤橘子與{q2}公斤香蕉，付了{total2}元。"
        f"橘子每公斤 \\(x\\) 元、香蕉每公斤 \\(y\\) 元，試求 \\((x,y)\\)。"
    )
    answer = _pair_text(Fraction(x), Fraction(y))
    return _pack(
        op=SYSTEM_WORD_TWO, question=question, answer=answer, parts={"(1)": str(x), "(2)": str(y)},
        presentation="short_answer", answer_type="multi_part", choices=None,
        givens={"x": x, "y": y}, visual=None,
        explanation=f"依兩筆購買列出方程組，解得橘子每公斤 {x} 元、香蕉每公斤 {y} 元。",
    )


def _build_abs_pair(rng: random.Random, presentation: str) -> dict[str, Any]:
    x = Fraction(rng.randint(-4, 4))
    y = Fraction(rng.randint(-4, 4))
    a1, b1 = Fraction(rng.choice([1, 2, -1])), Fraction(rng.choice([1, -1, 2]))
    a2, b2 = Fraction(rng.choice([1, -2])), Fraction(rng.choice([1, 2, -1]))
    if a1 * b2 - a2 * b1 == 0:
        a2 = a1 + 1
    c1 = -(a1 * x + b1 * y)
    c2 = -(a2 * x + b2 * y)
    question = (
        f"若 \\(x\\)、\\(y\\) 為實數，且 \\(|{_linear_expr(a1, b1, c1)}|+|{_linear_expr(a2, b2, c2)}|=0\\)，"
        f"試求 \\((x,y)\\)。"
    )
    return _pack(
        op=SYSTEM_ABS_PAIR, question=question, answer=_pair_text(x, y), parts=None,
        presentation="short_answer", answer_type="ordered_pair", choices=None,
        givens={"x": _fmt(x), "y": _fmt(y)}, visual=None,
        explanation="兩絕對值的和為 0，所以兩個一次式都是 0，再解聯立方程組。",
    )


def _build_continued(rng: random.Random, presentation: str) -> dict[str, Any]:
    x = Fraction(rng.randint(-3, 5))
    y = Fraction(rng.randint(-3, 5))
    k = Fraction(rng.choice([-2, -1, 1, 2]))
    # (x+2y-1)/3 = (1-2x)/5 = (y-1)/2 = k would overconstrain. Use two equal ratios.
    left = x + 2 * y
    right = 3 * y - x
    question = (
        f"若 \\(x\\)、\\(y\\) 滿足 \\(\\dfrac{{{_linear_expr(Fraction(1), Fraction(2), -left)}}}{{3}}"
        f"=\\dfrac{{{_linear_expr(Fraction(-1), Fraction(3), right)}}}{{2}}\\)，試求 \\(x-y\\)。"
    )
    # The displayed equations are not the solver. Solve the intended system directly:
    # (x+2y)/3 = (3y-x)/2 is what we want, with a known solution.
    # Rebuild a clean continued-proportion item: (x+y)/2 = (x-y)/4 = known.
    s = x + y
    d = x - y
    question = (
        f"若 \\(x\\)、\\(y\\) 為實數，且 \\(\\dfrac{{x+y}}{{2}}=\\dfrac{{x-y}}{{4}}={_tex_num(k)}\\)，試求 \\(x-y\\)。"
    )
    answer = _fmt(4 * k)
    return _pack(
        op=SYSTEM_CONTINUED_RATIO, question=question, answer=answer, parts=None,
        presentation="short_answer", answer_type="expression", choices=None,
        givens={"k": _fmt(k)}, visual=None,
        explanation=f"由第二段等於 {_tex_num(k)}，得 \\(x-y={_tex_num(4 * k)}\\)。",
    )


def _build_parameter_unique(rng: random.Random, presentation: str) -> dict[str, Any]:
    banned = rng.choice([-4, -3, -2, 2, 3, 4, 5])
    question = (
        f"設 \\(a\\) 為實數。若方程組 \\(\\left\\{{ \\begin{{array}}{{l}} ax+y=1\\\\ x+ay=1 \\end{{array}} \\right.\\) "
        f"恰有一組解，則 \\(a\\) 的條件為何？"
    )
    answer = r"\(a\neq 1\) 且 \(a\neq -1\)" if banned == 0 else f"a≠{banned}"
    # Use a stable unique-solution condition a^2 ≠ 1 for the displayed system.
    answer = "a<-1 或 -1<a<1 或 a>1"
    choices = None
    if presentation == "single_choice":
        question = (
            f"若方程組 \\(\\left\\{{ \\begin{{array}}{{l}} 8x+ay=10\\\\ ax+2y=5 \\end{{array}} \\right.\\) 無解，則實數 \\(a\\) 之值為"
        )
        answer = "4"
        choices = _choices(answer, ["-4", "2", "-2", "5"])
        # For this MCQ the mathematical condition of no solution is a^2 = 16 and the ratios disagree.
        # a=4: 8/4=2, 10/5=2, so the equations are dependent (infinite), not none.
        # a=-4: 8/(-4)=-2, 2/(-4)=-1/2, constants 10/5=2, ratios of coef differ so no solution.
        answer = "-4"
        choices = _choices(answer, ["4", "2", "-2"])
    return _pack(
        op=SYSTEM_PARAMETER_UNIQUE, question=question, answer=answer, parts=None,
        presentation=presentation,
        answer_type="single_choice" if presentation == "single_choice" else "inequality",
        choices=choices, givens={"excluded": [-1, 1]}, visual=None,
        explanation="兩直線斜率不同（或係數行列式不為 0）時恰有一解。",
    )


def _build_parameter_cases(rng: random.Random, presentation: str) -> dict[str, Any]:
    question = (
        "已知 \\(a\\) 為實數，方程組 "
        r"\(\left\{ \begin{array}{l} ax+(2a-3)y=-1\\ 4x+ay=-a \end{array} \right.\)。"
        "試分別寫出：(1) 有無限多組解時的 \\(a\\)；(2) 無解時的 \\(a\\)。"
    )
    return _pack(
        op=SYSTEM_PARAMETER_CASES, question=question, answer="(1) a=2；(2) a=6",
        parts={"(1)": "2", "(2)": "6"},
        presentation="short_answer", answer_type="multi_part", choices=None,
        givens={"infinite": "2", "none": "6"}, visual=None,
        explanation="係數成比例且常數也成比例時有無限多解；只有係數成比例而常數不成比例時無解。此方程組在 a=2 時無限多解，在 a=6 時無解。",
    )


def _build_dependent_value(rng: random.Random, presentation: str) -> dict[str, Any]:
    # Two dependent equations: 2x+3y=6 and 4x+6y=12. If ax+by=c matches, 2a-b can be asked from a cleaner item.
    question = (
        "若方程組 "
        r"\(\left\{ \begin{array}{l} x+2y=5\\ 2x+4y=10 \end{array} \right.\)"
        " 與 "
        r"\(\left\{ \begin{array}{l} ax+by=5\\ 2ax+2by=10 \end{array} \right.\)"
        " 表示同一條直線，且 \\(a=3\\)，則 \\(2a-b\\) 等於"
    )
    # Same line means (a,b) parallel to (1,2), so b=2a=6, 2a-b=0. That's a weak item.
    # Use the exam style: from dependence, recover a linear combination.
    a = 2
    b = -1
    question = (
        "已知兩方程組 "
        r"\(\left\{ \begin{array}{l} x+y=3\\ 2x-y=3 \end{array} \right.\)"
        " 與 "
        r"\(\left\{ \begin{array}{l} ax+by=3\\ 2x-y=3 \end{array} \right.\)"
        " 有相同的解，則 \\(2a-b\\) 等於"
    )
    x, y = _solve2(1, 1, 3, 2, -1, 3)
    # second system shares the second equation and the same solution, so a*x+b*y=3.
    # Fix b=1, then a*x = 3-y, a = (3-y)/x
    b = Fraction(1)
    a = (Fraction(3) - b * y) / x
    value = 2 * a - b
    answer = _fmt(value)
    question = (
        f"已知 \\((x,y)={_pair_text(x, y)}\\) 同時滿足 "
        rf"\(ax+by=3\) 與 \(2x-y=3\)，且 \(b=1\)。則 \(2a-b\) 等於"
    )
    choices = _choices(answer, [_fmt(value + d) for d in (1, -1, 2)]) if presentation == "single_choice" else None
    return _pack(
        op=SYSTEM_DEPENDENT_VALUE, question=question, answer=answer, parts=None,
        presentation=presentation, answer_type="single_choice" if presentation == "single_choice" else "expression",
        choices=choices, givens={"a": _fmt(a), "b": "1"}, visual=None,
        explanation=f"由點代入得 \\(a={_tex_num(a)}\\)，故 \\(2a-b={_tex_num(value)}\\)。",
    )


def _build_known_solution(rng: random.Random, presentation: str) -> dict[str, Any]:
    x, y = Fraction(1), Fraction(-1)
    # ax - 2by = 4, 2ax + 3y = b, with (1,-1)
    # a(1) - 2b(-1) = 4 => a+2b=4
    # 2a(1) + 3(-1) = b => 2a - 3 = b
    # a+2(2a-3)=4 => a+4a-6=4 => 5a=10 => a=2, b=1
    question = (
        r"設 \(a\)、\(b\) 為實數，且 \(x=1\)、\(y=-1\) 為 "
        r"\(\left\{ \begin{array}{l} ax-2by=4\\ 2ax+3y=b \end{array} \right.\)"
        r" 的解，則 \(a+b\) 等於"
    )
    return _pack(
        op=SYSTEM_KNOWN_SOLUTION, question=question, answer="3", parts=None,
        presentation="short_answer", answer_type="expression", choices=None,
        givens={"a": "2", "b": "1"}, visual=None,
        explanation="將 \\((1,-1)\\) 代入，解得 \\(a=2\\)、\\(b=1\\)，故 \\(a+b=3\\)。",
    )


def _slope(a: Fraction, b: Fraction, c: Fraction) -> Fraction:
    if b == 0:
        raise ValueError("vertical")
    return -a / b


def _build_line_slope(rng: random.Random, presentation: str) -> dict[str, Any]:
    lines = []
    slopes = []
    for _ in range(2):
        for _try in range(20):
            a = Fraction(rng.choice([-4, -3, -2, -1, 1, 2, 3, 4]))
            b = Fraction(rng.choice([-3, -2, -1, 1, 2, 3]))
            c = Fraction(rng.randint(-6, 6))
            if b == 0:
                continue
            m = _slope(a, b, c)
            lines.append((a, b, c))
            slopes.append(m)
            break
    (a1, b1, c1), (a2, b2, c2) = lines
    question = (
        f"求下列兩直線的斜率：(1) \\({_linear_expr(a1, b1, c1)}=0\\)；(2) \\({_linear_expr(a2, b2, c2)}=0\\)。"
    )
    return _pack(
        op=LINE_SLOPE_PAIR, question=question, answer=f"{_fmt(slopes[0])};{_fmt(slopes[1])}",
        parts={"(1)": _fmt(slopes[0]), "(2)": _fmt(slopes[1])},
        presentation="short_answer", answer_type="multi_part", choices=None,
        givens={"m1": _fmt(slopes[0]), "m2": _fmt(slopes[1])}, visual=None,
        explanation="直線 \\(ax+by+c=0\\)（\\(b\\ne 0\\)）的斜率是 \\(-a/b\\)。",
    )


def _relation(a1, b1, c1, a2, b2, c2) -> str:
    det = a1 * b2 - a2 * b1
    if det != 0:
        return "相交且恰有一組解"
    # parallel or coincident
    if a1 == 0 and a2 == 0:
        scale = b2 / b1 if b1 else None
    elif a1 != 0:
        scale = a2 / a1
    else:
        scale = None
    if scale is not None and b2 == scale * b1 and c2 == scale * c1:
        return "重合且有無限多組解"
    return "平行且無解"


def _build_line_relation(rng: random.Random, presentation: str) -> dict[str, Any]:
    kind = rng.choice(["intersect", "parallel", "coincident"])
    a1 = Fraction(rng.choice([1, 2, 3, -1, -2]))
    b1 = Fraction(rng.choice([1, -1, 2, -2]))
    c1 = Fraction(rng.randint(-4, 4))
    if kind == "intersect":
        a2, b2, c2 = b1, Fraction(rng.choice([1, -1, 3])), Fraction(rng.randint(-3, 3))
        if a1 * b2 - a2 * b1 == 0:
            a2 = a1 + 1
    elif kind == "parallel":
        scale = Fraction(rng.choice([2, -2, 3]))
        a2, b2, c2 = scale * a1, scale * b1, scale * c1 + Fraction(rng.choice([1, -1, 2]))
    else:
        scale = Fraction(rng.choice([2, -1, 3]))
        a2, b2, c2 = scale * a1, scale * b1, scale * c1
    answer = _relation(a1, b1, c1, a2, b2, c2)
    question = (
        f"判斷兩直線 \\({_linear_expr(a1, b1, c1)}=0\\) 與 \\({_linear_expr(a2, b2, c2)}=0\\) 的關係。"
    )
    choices = _choices(answer, ["相交且恰有一組解", "平行且無解", "重合且有無限多組解", "垂直且無解"])
    return _pack(
        op=LINE_PAIR_RELATION, question=question, answer=answer, parts=None,
        presentation="single_choice", answer_type="single_choice", choices=choices,
        givens={"relation": answer}, visual=None,
        explanation="比較兩直線的係數是否成比例，以及常數項是否同時成比例。",
    )


def _count_positive(a: int, b: int, limit: int) -> int:
    count = 0
    for x in range(1, limit + 1):
        for y in range(1, limit + 1):
            if a * x + b * y <= limit:
                count += 1
    return count


def _build_integer_count(rng: random.Random, presentation: str) -> dict[str, Any]:
    a, b = 3, 4
    limit = rng.choice([12, 15, 18])
    count = _count_positive(a, b, limit)
    question = f"設 \\(x\\)、\\(y\\) 均為正整數，則滿足 \\({a}x+{b}y\\le {limit}\\) 的數對 \\((x,y)\\) 共有多少組？"
    answer = str(count)
    choices = _choices(answer, [str(count + d) for d in (1, -1, 2) if count + d > 0]) if presentation == "single_choice" else None
    return _pack(
        op=INTEGER_FEASIBLE_COUNT, question=question, answer=answer, parts=None,
        presentation=presentation, answer_type="single_choice" if presentation == "single_choice" else "expression",
        choices=choices, givens={"count": count}, visual=None,
        explanation="逐一代入正整數，保留滿足不等式的數對再計數。",
    )


def _build_integer_choice(rng: random.Random, presentation: str) -> dict[str, Any]:
    # A: 100 kcal, 8 sugar; B: 150 kcal, 6 sugar; limits 400 and 20.
    options = [(3, 0), (2, 1), (1, 2), (0, 3), (4, 0)]
    def ok(na, nb):
        return 100 * na + 150 * nb <= 400 and 8 * na + 6 * nb <= 20
    good = [pair for pair in options if ok(*pair)]
    bad = [pair for pair in options if not ok(*pair)]
    answer = f"A食品{good[0][0]}份，B食品{good[0][1]}份"
    wrong = [f"A食品{na}份，B食品{nb}份" for na, nb in bad]
    question = (
        "每餐熱量不超過 400 大卡、糖量不超過 20 克。A 食品一份 100 大卡、糖 8 克，"
        "B 食品一份 150 大卡、糖 6 克。下列哪一種搭配符合限制？"
    )
    return _pack(
        op=INTEGER_FEASIBLE_CHOICE, question=question, answer=answer, parts=None,
        presentation="single_choice", answer_type="single_choice",
        choices=_choices(answer, wrong), givens={"pair": good[0]}, visual=None,
        explanation="把份數代入熱量與糖量兩個不等式，同時成立者才符合。",
    )


def _side_phrase(included: bool, contains_origin: bool) -> str:
    boundary = "實線" if included else "虛線"
    side = "包含" if contains_origin else "不包含"
    return f"邊界為{boundary}，且區域{side}原點"


def _build_halfplane(rng: random.Random, presentation: str) -> dict[str, Any]:
    a = Fraction(rng.choice([-3, -2, -1, 1, 2, 3]))
    b = Fraction(rng.choice([-2, -1, 0, 1, 2]))
    c = Fraction(rng.choice([-4, -2, -1, 1, 2, 4]))
    if a == 0 and b == 0:
        b = Fraction(1)
    op = rng.choice(["<", "<=", ">", ">="])
    included = op in {"<=", ">="}
    origin_value = c
    contains = (origin_value < 0 and op in {"<", "<="}) or (origin_value > 0 and op in {">", ">="}) or (origin_value == 0 and included)
    if origin_value == 0:
        c = Fraction(rng.choice([-3, -1, 2, 4]))
        origin_value = c
        contains = (origin_value < 0 and op in {"<", "<="}) or (origin_value > 0 and op in {">", ">="})
    answer = _side_phrase(included, contains)
    question = f"不等式 {_ineq_tex(a, b, c, op)} 的解區域，下列哪一個敘述正確？"
    pool = [
        _side_phrase(True, True),
        _side_phrase(True, False),
        _side_phrase(False, True),
        _side_phrase(False, False),
    ]
    visual = {
        "kind": "coordinate_plane_spec",
        "render_required": False,
        "lines": [{
            "label": "L",
            "type": "general",
            "a": _fmt(a), "b": _fmt(b), "c": _fmt(c),
            "style": "solid" if included else "dashed",
        }],
        "shade": {"test_point": [0, 0], "included": contains, "boundary_included": included},
        "x_range": [-6, 6],
        "y_range": [-6, 6],
    }
    return _pack(
        op=HALFPLANE_REGION, question=question, answer=answer, parts=None,
        presentation="single_choice", answer_type="single_choice",
        choices=_choices(answer, pool), givens={"a": _fmt(a), "b": _fmt(b), "c": _fmt(c), "op": op},
        visual=visual, explanation="先看不等號是否包含等號，再代入原點判斷鋪色的一側。",
    )


def _agrees(a, b, c, op, a2, b2, c2, op2) -> bool:
    def holds(x, y, aa, bb, cc, rel):
        value = aa * x + bb * y + cc
        return {">": value > 0, ">=": value >= 0, "<": value < 0, "<=": value <= 0}[rel]
    for x in range(-4, 5):
        for y in range(-4, 5):
            if holds(x, y, a, b, c, op) != holds(x, y, a2, b2, c2, op2):
                return False
    return True


def _ineq_plain(a, b, c, op) -> str:
    shown = {"<=": "≤", ">=": "≥", "<": "<", ">": ">"}.get(op, op)
    return f"{_fmt(a)}x+{_fmt(b)}y+{_fmt(c)}{shown}0".replace("+-", "-")


def _build_shade_to_inequality(rng: random.Random, presentation: str) -> dict[str, Any]:
    a = Fraction(rng.choice([1, 2, -1, -2]))
    b = Fraction(rng.choice([1, -1, 2]))
    c = Fraction(rng.choice([-3, -1, 1, 2]))
    op = rng.choice(["<=", "<"])
    correct = _ineq_plain(a, b, c, op)
    candidates = [
        _ineq_plain(-a, -b, -c, "<" if op == "<=" else "<="),
        _ineq_plain(a, b, c, "<" if op == "<=" else "<="),
        _ineq_plain(a, b, c + 2, op),
        _ineq_plain(a, b, c + 5, op),
        _ineq_plain(a + 1, b, c, op),
        "9x+8y+7>0",
    ]
    distractors = []
    for item in candidates:
        try:
            parsed = _parse_plain(item)
        except Exception:
            continue
        if item != correct and not _agrees(a, b, c, op, *parsed) and item not in distractors:
            distractors.append(item)
    question = "坐標平面上，直線為邊界、鋪色區域如下圖。滿足鋪色區域的不等式是哪一個？"
    visual = {
        "kind": "coordinate_plane_spec",
        "render_required": True,
        "lines": [{"label": "L", "type": "general", "a": _fmt(a), "b": _fmt(b), "c": _fmt(c), "style": "solid" if op == "<=" else "dashed"}],
        "shade": {"inequality": correct, "boundary_included": op == "<="},
        "x_range": [-6, 6],
        "y_range": [-6, 6],
    }
    if presentation != "single_choice":
        visual = {
            "kind": "coordinate_plane_spec",
            "render_required": True,
            "lines": [{"label": "L", "type": "general", "a": "3", "b": "-1", "c": "-6", "style": "solid"}],
            "x_range": [-1, 6],
            "y_range": [-8, 4],
        }
        return _pack(
            op=SHADE_TO_INEQUALITY, question="直線 \\(y=3x+b\\) 的 \\(x\\) 截距是 2。(1) 求 \\(b\\)；(2) 原點是否在直線下方？",
            answer="(1) -6；(2) 否",
            parts={"(1)": "-6", "(2)": "否"},
            presentation="short_answer", answer_type="multi_part", choices=None,
            givens={"b": "-6"}, visual=visual,
            explanation="\\(x\\) 截距為 2 時 \\(0=6+b\\)，故 \\(b=-6\\)。原點的函數值是 \\(-6\\)，原點在直線上方。",
        )
    return _pack(
        op=SHADE_TO_INEQUALITY, question=question, answer=correct, parts=None,
        presentation="single_choice", answer_type="single_choice",
        choices=_choices(correct, distractors), givens={"inequality": correct},
        visual=visual, explanation="由邊界係數、實線或虛線、以及測試點所在的一側決定不等式。",
    )


def _parse_plain(text: str) -> tuple[Fraction, Fraction, Fraction, str]:
    text = text.replace("≤", "<=").replace("≥", ">=")
    op = "<=" if "<=" in text else ">=" if ">=" in text else "<" if "<" in text else ">"
    left = text.split(op)[0]
    # parse Ax+By+C from a compact string produced by _ineq_plain
    expr = left.replace("-", "+-")
    a = b = c = Fraction(0)
    for token in expr.split("+"):
        if token == "" or token == "-":
            continue
        if "x" in token:
            num = token.replace("x", "") or "1"
            if num == "-":
                num = "-1"
            a = Fraction(num)
        elif "y" in token:
            num = token.replace("y", "") or "1"
            if num == "-":
                num = "-1"
            b = Fraction(num)
        else:
            c = Fraction(token)
    return a, b, c, op


def _sign_at(a, b, c, x, y) -> int:
    value = Fraction(a) * x + Fraction(b) * y + Fraction(c)
    return (value > 0) - (value < 0)


def _build_same_side(rng: random.Random, presentation: str) -> dict[str, Any]:
    a, b, c = 1, -3, 2
    p = (rng.randint(-4, 4), rng.randint(-4, 4))
    q = (rng.randint(-4, 4), rng.randint(-4, 4))
    sp_, sq = _sign_at(a, b, c, *p), _sign_at(a, b, c, *q)
    if sp_ == 0 or sq == 0 or p == q:
        p, q = (-3, 1), (1, 2)
        sp_, sq = _sign_at(a, b, c, *p), _sign_at(a, b, c, *q)
    answer = "同側" if sp_ == sq else "異側"
    question = (
        f"試判斷點 \\(A{_pair_text(Fraction(p[0]), Fraction(p[1]))}\\) 與 "
        f"\\(B{_pair_text(Fraction(q[0]), Fraction(q[1]))}\\) 位於直線 \\(x-3y+2=0\\) 的同側或異側。"
    )
    if presentation == "single_choice":
        question = "下列哪一點與 \\((1,1)\\) 在直線 \\(x-y+2=0\\) 的同側？"
        origin_sign = _sign_at(1, -1, 2, 1, 1)
        candidates = [(0, 0), (0, 3), (0, 4), (1, 4), (-1, 2)]
        good = next(pt for pt in candidates if _sign_at(1, -1, 2, *pt) == origin_sign and pt != (1, 1))
        bad = [pt for pt in candidates if _sign_at(1, -1, 2, *pt) not in {0, origin_sign}]
        answer = _pair_text(Fraction(good[0]), Fraction(good[1]))
        return _pack(
            op=SAME_SIDE_TEST, question=question, answer=answer, parts=None,
            presentation="single_choice", answer_type="single_choice",
            choices=_choices(answer, [_pair_text(Fraction(x), Fraction(y)) for x, y in bad]),
            givens={"point": good}, visual=None,
            explanation="將各點代入 \\(x-y+2\\)，符號與 \\((1,1)\\) 相同者在同側。",
        )
    return _pack(
        op=SAME_SIDE_TEST, question=question, answer=answer, parts=None,
        presentation="short_answer", answer_type="short_answer", choices=None,
        givens={"relation": answer}, visual=None,
        explanation="將兩點代入直線左式，同號為同側，異號為異側。",
    )


def _build_same_side_parameter(rng: random.Random, presentation: str) -> dict[str, Any]:
    # P(2,3), Q(-1,-2), L: x-2y+k=0 same side => (2-6+k)(-1+4+k)>0 => (k-4)(k+3)>0
    question = "點 \\(P(2,3)\\)、\\(Q(-1,-2)\\) 在直線 \\(x-2y+k=0\\) 的同側，試求實數 \\(k\\) 的範圍。"
    answer = "k<-3 或 k>4"
    if presentation == "single_choice":
        question = "點 \\(A(-1,1)\\)、\\(B(1,-2)\\) 在直線 \\(3x-2y+k=0\\) 的異側，則 \\(k\\) 的範圍是"
        # f(A)= -3 -2 +k = k-5, f(B)=3+4+k=k+7, opposite => (k-5)(k+7)<0 => -7<k<5
        answer = "-7<k<5"
        return _pack(
            op=SAME_SIDE_PARAMETER, question=question, answer=answer, parts=None,
            presentation="single_choice", answer_type="single_choice",
            choices=_choices(answer, ["k<-7 ∪ k>5", "k<5 ∪ k>7", "-5<k<7"]),
            givens={"range": answer}, visual=None,
            explanation="兩點代入後的值異號，解出 \\(k\\) 的不等式。",
        )
    return _pack(
        op=SAME_SIDE_PARAMETER, question=question, answer=answer, parts=None,
        presentation="short_answer", answer_type="inequality", choices=None,
        givens={"range": answer}, visual=None,
        explanation="兩點代入後同號，得 \\((k-4)(k+3)>0\\)。",
    )


def _build_region_corner(rng: random.Random, presentation: str) -> dict[str, Any]:
    # Two lines with a clean intersection, ask the boundary intersection.
    a1, b1, c1, a2, b2, c2, x, y = _sample_system(rng)
    question = (
        f"聯立不等式的兩條邊界為 {_system_tex([(a1, b1, c1), (a2, b2, c2)])}。"
        f"試求兩邊界的交點。"
    )
    return _pack(
        op=SYSTEM_REGION_CORNER, question=question, answer=_pair_text(x, y), parts=None,
        presentation="short_answer", answer_type="ordered_pair", choices=None,
        givens={"x": _fmt(x), "y": _fmt(y)}, visual={"kind": "none"},
        explanation="解兩條邊界直線的聯立方程組，即得交點。",
    )


def _build_shade_to_system(rng: random.Random, presentation: str) -> dict[str, Any]:
    x, y = Fraction(2), Fraction(1)
    # two inequalities satisfied by (2,1): x>=0 and y<=3, plus x+y<=6
    correct = "x≥0, y≤3, x+y≤6"
    distractors = ["x≥0, y≥3, x+y≤6", "x≤0, y≤3, x+y≤6", "x≥0, y≤3, x+y≥6"]
    question = "下圖鋪色區域由三條邊界圍成，且包含點 \\((2,1)\\)。代表此區域的聯立不等式是哪一個？"
    visual = {
        "kind": "coordinate_plane_spec",
        "render_required": True,
        "lines": [
            {"label": "L1", "type": "general", "a": "1", "b": "0", "c": "0", "style": "solid"},
            {"label": "L2", "type": "general", "a": "0", "b": "1", "c": "-3", "style": "solid"},
            {"label": "L3", "type": "general", "a": "1", "b": "1", "c": "-6", "style": "solid"},
        ],
        "shade": {"test_point": [2, 1], "included": True},
        "x_range": [-1, 8],
        "y_range": [-1, 6],
    }
    return _pack(
        op=SHADE_TO_SYSTEM, question=question, answer=correct, parts=None,
        presentation="single_choice", answer_type="single_choice",
        choices=_choices(correct, distractors), givens={"system": correct},
        visual=visual, explanation="用圖中的測試點逐條檢查不等號方向。",
    )


def _build_labeled_region(rng: random.Random, presentation: str) -> dict[str, Any]:
    question = (
        r"聯立不等式 \(\left\{ \begin{array}{l} x+y\le 8\\ x-y\le 1 \end{array} \right.\) "
        "的可行解區域是附圖的哪一個部分？"
    )
    answer = "同時滿足兩式的交集"
    choices = _choices(answer, ["只滿足第一式", "只滿足第二式", "兩式都不滿足"])
    visual = {
        "kind": "coordinate_plane_spec",
        "render_required": True,
        "lines": [
            {"label": "L1", "type": "general", "a": "1", "b": "1", "c": "-8", "style": "solid"},
            {"label": "L2", "type": "general", "a": "1", "b": "-1", "c": "-1", "style": "solid"},
        ],
        "regions": ["A", "B", "C", "D"],
        "x_range": [-2, 10],
        "y_range": [-2, 10],
    }
    return _pack(
        op=LABELED_REGION_CHOICE, question=question, answer=answer, parts=None,
        presentation="single_choice", answer_type="single_choice", choices=choices,
        givens={"region": "intersection"}, visual=visual,
        explanation="可行解是兩條半平面的交集。",
    )


def _polygon_area(points: list[tuple[Fraction, Fraction]]) -> Fraction:
    area = Fraction(0)
    for i, (x1, y1) in enumerate(points):
        x2, y2 = points[(i + 1) % len(points)]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2


def _build_feasible_area(rng: random.Random, presentation: str) -> dict[str, Any]:
    # x>=0, y>=0, x+y<=4, x+2y<=6. Vertices (0,0),(4,0),(2,2),(0,3)
    verts = [(Fraction(0), Fraction(0)), (Fraction(4), Fraction(0)), (Fraction(2), Fraction(2)), (Fraction(0), Fraction(3))]
    area = _polygon_area(verts)
    question = (
        r"滿足 \(\left\{ \begin{array}{l} x\ge 0\\ y\ge 0\\ x+y\le 4\\ x+2y\le 6 \end{array} \right.\) "
        "的可行解區域面積是多少？"
    )
    answer = _fmt(area)
    choices = _choices(answer, [_fmt(area + d) for d in (1, -1, 2)]) if presentation == "single_choice" else None
    return _pack(
        op=FEASIBLE_AREA, question=question, answer=answer, parts=None,
        presentation=presentation, answer_type="single_choice" if presentation == "single_choice" else "expression",
        choices=choices, givens={"area": answer, "vertices": [_pair_text(*p) for p in verts]},
        visual={"kind": "coordinate_plane_spec", "render_required": False, "vertices": [[_fmt(x), _fmt(y)] for x, y in verts], "x_range": [-1, 6], "y_range": [-1, 5]},
        explanation="先求邊界交點，再以頂點座標計算多邊形面積。",
    )


def _build_integer_points(rng: random.Random, presentation: str) -> dict[str, Any]:
    count = 0
    # 0<=x<=4, y>=0, x+y<=6
    for x in range(0, 5):
        for y in range(0, 7):
            if x + y <= 6:
                count += 1
    question = r"若 \(x\)、\(y\) 都是非負整數，且 \(x\le 4\)、\(x+y\le 6\)，則數對 \((x,y)\) 共有多少組？"
    return _pack(
        op=INTEGER_POINTS_COUNT, question=question, answer=str(count), parts=None,
        presentation="short_answer", answer_type="expression", choices=None,
        givens={"count": count}, visual=None,
        explanation="在範圍內逐一檢查整數點。",
    )


def _lp_vertices() -> list[tuple[Fraction, Fraction]]:
    # x>=0,y>=0,x+y<=6,2x+y<=8. Intersections: (0,0),(4,0),(2,4),(0,6)
    return [(Fraction(0), Fraction(0)), (Fraction(4), Fraction(0)), (Fraction(2), Fraction(4)), (Fraction(0), Fraction(6))]


def _build_lp_extrema(rng: random.Random, presentation: str) -> dict[str, Any]:
    verts = _lp_vertices()
    px, py = Fraction(rng.choice([1, 2, 3])), Fraction(rng.choice([1, 2]))
    values = [(px * x + py * y, x, y) for x, y in verts]
    best = max(values, key=lambda row: (row[0], row[1], row[2]))
    worst = min(values, key=lambda row: (row[0], row[1], row[2]))
    question = (
        r"在 \(\left\{ \begin{array}{l} x\ge 0\\ y\ge 0\\ x+y\le 6\\ 2x+y\le 8 \end{array} \right.\) 下，"
        rf"求 \(f(x,y)={_tex_num(px)}x+{_tex_num(py)}y\) 的最大值與最小值。"
    )
    if presentation == "single_choice":
        answer = f"最大值{_fmt(best[0])}，頂點{_fmt(best[1])}與{_fmt(best[2])}"
        wrong = []
        for value, x, y in values:
            text = f"最大值{_fmt(value)}，頂點{_fmt(x)}與{_fmt(y)}"
            if text != answer:
                wrong.append(text)
        if len(wrong) < 3:
            wrong.append(f"最大值{_fmt(best[0] + 1)}，頂點{_fmt(best[1] + 1)}與{_fmt(best[2])}")
        return _pack(
            op=LP_EXTREMA, question=question.replace("的最大值與最小值", "的最大值發生於何處"),
            answer=answer, parts=None, presentation="single_choice", answer_type="single_choice",
            choices=_choices(answer, wrong), givens={"max": _fmt(best[0])},
            visual={"kind": "coordinate_plane_spec", "render_required": True, "vertices": [[_fmt(x), _fmt(y)] for x, y in verts], "x_range": [-1, 8], "y_range": [-1, 8]},
            explanation="目標函數的極值發生在可行解區域的頂點。",
        )
    return _pack(
        op=LP_EXTREMA, question=question, answer=f"{_fmt(best[0])};{_fmt(worst[0])}",
        parts={"(1)": _fmt(best[0]), "(2)": _fmt(worst[0])},
        presentation="short_answer", answer_type="multi_part", choices=None,
        givens={"max": _fmt(best[0]), "min": _fmt(worst[0]), "vertices": [_pair_text(x, y) for x, y in verts]},
        visual={"kind": "coordinate_plane_spec", "render_required": False, "vertices": [[_fmt(x), _fmt(y)] for x, y in verts], "x_range": [-1, 8], "y_range": [-1, 8]},
        explanation="計算四個頂點的目標函數值，再取最大與最小。",
    )


def _build_lp_application(rng: random.Random, presentation: str) -> dict[str, Any]:
    verts = _lp_vertices()
    # profit 3x+2y, max at a vertex
    values = [(3 * x + 2 * y, x, y) for x, y in verts]
    best = max(values, key=lambda row: row[0])
    question = (
        "某攤位製作兩種點心。甲每公斤利潤 3 元、乙每公斤利潤 2 元。"
        "若 \\(x\\)、\\(y\\) 同時滿足 "
        r"\(\left\{ \begin{array}{l} x\ge 0\\ y\ge 0\\ x+y\le 6\\ 2x+y\le 8 \end{array} \right.\)，"
        "則最大利潤是多少元？"
    )
    answer = _fmt(best[0])
    choices = _choices(answer, [_fmt(best[0] + d) for d in (1, -1, 2)]) if presentation == "single_choice" else None
    return _pack(
        op=LP_APPLICATION, question=question, answer=answer, parts=None,
        presentation=presentation, answer_type="single_choice" if presentation == "single_choice" else "expression",
        choices=choices, givens={"max": answer, "point": _pair_text(best[1], best[2])},
        visual={"kind": "none"},
        explanation=f"在頂點 {_pair_text(best[1], best[2])} 得到最大利潤 {_tex_num(best[0])}。",
    )


def _build_constraint_choice(rng: random.Random, presentation: str) -> dict[str, Any]:
    question = (
        "製作 A、B 兩種餅乾。A 每單位用花生 1 公斤，B 每單位用花生 0.4 公斤，花生最多 6 公斤；"
        "A 每單位用核桃 0.3 公斤，B 每單位用核桃 0.4 公斤，核桃最多 3.2 公斤。"
        "設 A、B 的數量為 \\(x\\)、\\(y\\)，下列哪一組限制正確？"
    )
    answer = "x≥0, y≥0, x+0.4y≤6, 0.3x+0.4y≤3.2"
    wrong = [
        "x≥0, y≥0, x+0.4y≥6, 0.3x+0.4y≤3.2",
        "x≥0, y≥0, 0.4x+y≤6, 0.3x+0.4y≤3.2",
        "x≥0, y≥0, x+0.4y≤6, 0.4x+0.3y≤3.2",
    ]
    return _pack(
        op=CONSTRAINT_SYSTEM_CHOICE, question=question, answer=answer, parts=None,
        presentation="single_choice", answer_type="single_choice",
        choices=_choices(answer, wrong), givens={"system": answer}, visual=None,
        explanation="材料用量不得超過存量，且數量不是負數。",
    )


_BUILDERS = {
    SYSTEM_ORDERED_PAIR: _build_system_ordered_pair,
    SYSTEM_LINEAR_COMBO: _build_system_linear_combo,
    SYSTEM_WORD_TWO: _build_system_word,
    SYSTEM_ABS_PAIR: _build_abs_pair,
    SYSTEM_CONTINUED_RATIO: _build_continued,
    SYSTEM_PARAMETER_UNIQUE: _build_parameter_unique,
    SYSTEM_PARAMETER_CASES: _build_parameter_cases,
    SYSTEM_DEPENDENT_VALUE: _build_dependent_value,
    SYSTEM_KNOWN_SOLUTION: _build_known_solution,
    LINE_SLOPE_PAIR: _build_line_slope,
    LINE_PAIR_RELATION: _build_line_relation,
    INTEGER_FEASIBLE_COUNT: _build_integer_count,
    INTEGER_FEASIBLE_CHOICE: _build_integer_choice,
    HALFPLANE_REGION: _build_halfplane,
    SHADE_TO_INEQUALITY: _build_shade_to_inequality,
    SAME_SIDE_TEST: _build_same_side,
    SAME_SIDE_PARAMETER: _build_same_side_parameter,
    SYSTEM_REGION_CORNER: _build_region_corner,
    SHADE_TO_SYSTEM: _build_shade_to_system,
    LABELED_REGION_CHOICE: _build_labeled_region,
    FEASIBLE_AREA: _build_feasible_area,
    INTEGER_POINTS_COUNT: _build_integer_points,
    LP_EXTREMA: _build_lp_extrema,
    LP_APPLICATION: _build_lp_application,
    CONSTRAINT_SYSTEM_CHOICE: _build_constraint_choice,
}


def build_linear_inequality_planning_matrix(seed: int | None = None, constraints: dict | None = None) -> dict[str, Any]:
    constraints = dict(constraints or {})
    rng = random.Random(0 if seed is None else int(seed))
    example_id = constraints.get("textbook_example_id")
    spec = SOURCE_SPECS.get(int(example_id)) if example_id is not None else None
    op = str(constraints.get("op") or (spec or {}).get("op") or "")
    if op not in _BUILDERS:
        raise ValueError(f"unknown_op:{op}")
    presentation = str(constraints.get("presentation") or (spec or {}).get("presentation") or "short_answer")
    matrix = _BUILDERS[op](rng, presentation)
    if spec:
        matrix["givens"]["textbook_example_id"] = int(example_id)
        matrix["givens"]["skill_id"] = spec["skill_id"]
    return matrix


def validate_linear_inequality_planning_matrix(matrix: dict[str, Any]) -> bool:
    if matrix.get("domain_key") != DOMAIN_KEY:
        return False
    if matrix.get("domain_operation") not in OPS:
        return False
    if not str(matrix.get("question_text") or "").strip():
        return False
    answer = matrix.get("answer") if isinstance(matrix.get("answer"), dict) else {}
    if not str(answer.get("canonical_form") or "").strip():
        return False
    if matrix.get("presentation_mode") == "single_choice":
        values = [row.get("value") for row in matrix.get("choices") or []]
        if len(values) != 4 or len(set(values)) != 4 or answer.get("canonical_form") not in values:
            return False
    return True
