"""Post-submit inequality answers are shown as relations in x, not interval notation."""
from __future__ import annotations

import pytest

from core.checkers.inequality_solution_checker import check_inequality_solution_answer
from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.gencode.answer_grading import build_correct_answer_display, format_correct_answer_display
from core.gencode.answer_payload import refresh_runtime_question_session
from core.gencode.question_quality_gate import inequality_answer_latex_display

SCREENSHOT_CASES = [
    ("$\\left|x+3\\right|\\ge 9$", "(-∞,-12]∪[6,∞)", "$x \\le -12$ 或 $x \\ge 6$"),
    ("$\\left|-x+6\\right|\\le 5$", "[1,11]", "$1 \\le x \\le 11$"),
    ("$\\left|3x+3\\right|>4$", "(-∞,-7/3)∪(1/3,∞)", "$x < -\\frac{7}{3}$ 或 $x > \\frac{1}{3}$"),
]


def _ineq_part(key: str, expected: str, **extra) -> dict:
    return {
        "key": key,
        "label": f"({key[-1]})",
        "checker": "inequality_solution_checker",
        "checker_key": "inequality_solution_checker",
        "answer_type": "inequality_solution",
        "equivalence_type": "inequality_solution_equivalence",
        "expected_answer": expected,
        **extra,
    }


def _multi_part_payload(stems: list[str], parts: list[dict], question_prefix: str = "解下列各不等式：") -> dict:
    question = question_prefix + "\n" + "\n".join(f"({i + 1}) {stem}。" for i, stem in enumerate(stems))
    return {
        "skill_id": "gh_LinearInequalitiesWithAbsoluteValue",
        "problem_type_id": "solve_absolute_value_inequalities",
        "question_text": question,
        "answer_type": "multi_part",
        "correct_answer": {part["key"]: part["expected_answer"] for part in parts},
        "answer_contract": {
            "answer_type": "multi_part",
            "checker": "multi_part_answer_checker",
            "parts": parts,
        },
    }


def _single_payload(question: str, canonical: str) -> dict:
    return {
        "skill_id": "vh_數學B1_AbsoluteValueInequality",
        "question_text": question,
        "problem_type_id": "absolute_value_inequality_ge",
        "answer_type": "inequality_solution",
        "correct_answer": canonical,
        "display_answer": canonical,
        "answer_contract": {
            "answer_type": "inequality_solution",
            "checker": "inequality_solution_checker",
            "canonical_answer": canonical,
        },
    }


def _items(payload: dict) -> list[str]:
    display = build_correct_answer_display(payload)
    assert display is not None
    return [item["value"] for item in display["items"]]


def test_screenshot_cases_display_as_relations_in_x() -> None:
    parts = [_ineq_part(f"part_{i + 1}", expected) for i, (_, expected, _) in enumerate(SCREENSHOT_CASES)]
    payload = _multi_part_payload([stem for stem, _, _ in SCREENSHOT_CASES], parts)
    assert _items(payload) == [shown for _, _, shown in SCREENSHOT_CASES]


@pytest.mark.parametrize("_stem, expected, shown", SCREENSHOT_CASES)
def test_display_is_equivalent_to_canonical_answer(_stem: str, expected: str, shown: str) -> None:
    assert check_inequality_solution_answer(shown, expected) is True


@pytest.mark.parametrize(
    "expected, shown",
    [
        ("(2,5]", "$2 < x \\le 5$"),
        ("[-3/2,4)", "$-\\frac{3}{2} \\le x < 4$"),
        ("(-∞,-1/2]", "$x \\le -\\frac{1}{2}$"),
        ("(7,∞)", "$x > 7$"),
        ("[0,∞)", "$x \\ge 0$"),
        ("(-∞,-2)∪[3,∞)", "$x < -2$ 或 $x \\ge 3$"),
        ("[6,∞)∪(-∞,-12]", "$x \\le -12$ 或 $x \\ge 6$"),
        ("x>-1 且 x<=5", "$-1 < x \\le 5$"),
        ("(-∞,∞)", "全體實數"),
        ("無解", "無解"),
    ],
)
def test_endpoint_semantics_and_special_sets(expected: str, shown: str) -> None:
    payload = _multi_part_payload(["$|x|<1$"], [_ineq_part("part_1", expected)])
    assert _items(payload) == [shown]


def test_interval_notation_requested_by_question_is_kept() -> None:
    payload = _multi_part_payload(
        ["$\\left|x+3\\right|\\ge 9$"],
        [_ineq_part("part_1", "(-∞,-12]∪[6,∞)")],
        question_prefix="解下列各不等式，並以區間表示：",
    )
    assert _items(payload) == ["(-∞,-12]∪[6,∞)"]


def test_interval_required_form_on_part_is_kept() -> None:
    part = _ineq_part("part_1", "[1,11]", required_form="interval_notation")
    payload = _multi_part_payload(["$\\left|-x+6\\right|\\le 5$"], [part])
    assert _items(payload) == ["[1,11]"]


def test_non_inequality_parts_are_untouched() -> None:
    parts = [
        _ineq_part("part_1", "[1,11]"),
        {"key": "part_2", "label": "(2)", "checker": "solution_set_checker", "answer_type": "solution_set",
         "expected_answer": "-1, 9"},
        {"key": "part_3", "label": "(3)", "checker": "numeric_checker", "answer_type": "numeric",
         "expected_answer": "-7/2"},
        {"key": "part_4", "label": "(4)", "checker": "ordered_inequality_checker",
         "answer_type": "ordered_inequality", "expected_answer": "R<Q<P"},
    ]
    payload = _multi_part_payload(["a", "b", "c", "d"], parts)
    assert _items(payload) == ["$1 \\le x \\le 11$", "-1, 9", "-7/2", "R<Q<P"]


def test_single_answer_inequality_feedback_uses_relations() -> None:
    raw = _single_payload("解不等式 $|x|\\ge 15$。", "(-∞,-15] ∪ [15,∞)")
    payload = refresh_runtime_question_session(raw, skill_id=raw["skill_id"])
    assert payload["display_answer"] == "x <= -15 或 x >= 15"
    assert format_correct_answer_display(payload["correct_answer"], payload) == "$x \\le -15$ 或 $x \\ge 15$"
    display = build_correct_answer_display(payload)
    assert display == {"answer_type": "inequality_solution", "value": "$x \\le -15$ 或 $x \\ge 15$"}


def test_single_answer_interval_question_keeps_interval() -> None:
    payload = _single_payload("解不等式 $|x|\\ge 15$，以區間表示解。", "(-∞,-15] ∪ [15,∞)")
    assert format_correct_answer_display(payload["correct_answer"], payload) == "(-∞,-15] ∪ [15,∞)"


@pytest.mark.parametrize(
    "payload",
    [
        {"question_text": "求 $2x+1=5$ 的解。", "answer_type": "numeric", "correct_answer": "2",
         "answer_contract": {"answer_type": "numeric", "checker": "numeric_checker", "canonical_answer": "2"}},
        {"question_text": "求點座標。", "answer_type": "coordinate_pair", "correct_answer": "(-4,3)",
         "answer_contract": {"answer_type": "coordinate_pair", "checker": "coordinate_pair_checker",
                             "canonical_answer": "(-4,3)"}},
        {"question_text": "選出正確者。", "answer_type": "single_choice", "correct_answer": "B",
         "choices": ["$x<1$", "$[1,2]$"],
         "answer_contract": {"answer_type": "single_choice", "checker": "choice_label_checker",
                             "canonical_answer": "B"}},
    ],
)
def test_other_answer_types_have_no_relational_display(payload: dict) -> None:
    assert inequality_answer_latex_display(payload, payload["correct_answer"]) is None


@pytest.mark.parametrize(
    "student, correct",
    [
        ("x<=-12 or x>=6", True),
        ("x>=6 or x<=-12", True),
        ("(-∞,-12]∪[6,∞)", True),
        ("x≤-12 或 x≥6", True),
        ("$x \\le -12$ 或 $x \\ge 6$", True),
        ("x<-12 or x>6", False),
        ("x<=-12 or x>=7", False),
        ("-12<=x<=6", False),
    ],
)
def test_multi_part_grading_accepts_equivalent_forms_only(student: str, correct: bool) -> None:
    parts = [_ineq_part("part_1", "(-∞,-12]∪[6,∞)"), _ineq_part("part_2", "(-∞,-7/3)∪(1/3,∞)")]
    payload = _multi_part_payload(["$\\left|x+3\\right|\\ge 9$", "$\\left|3x+3\\right|>4$"], parts)
    result = check_multi_part_answer(
        {"part_1": student, "part_2": "x<-7/3 或 x>1/3"},
        payload["correct_answer"],
        answer_contract=payload["answer_contract"],
        payload=payload,
    )
    assert result["overall_correct"] is correct
