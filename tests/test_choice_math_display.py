from __future__ import annotations

from core.gencode.choice_contract_validator import normalize_canonical_choices
from core.gencode.choice_math_display import (
    format_choice_math_display,
    normalize_choice_displays,
)
from core.routes.practice import _finalize_practice_question_api_fields


def test_fraction_radical_and_coefficient_radical_display() -> None:
    assert format_choice_math_display("19/2") == r"\(\frac{19}{2}\)"
    assert format_choice_math_display("sqrt(91)") == r"\(\sqrt{91}\)"
    assert format_choice_math_display("6*sqrt(10)") == r"\(6\sqrt{10}\)"
    assert format_choice_math_display("13*sqrt(2)/2") == r"\(\frac{13\sqrt{2}}{2}\)"


def test_integer_decimal_coordinate_and_text_are_unchanged() -> None:
    for value in ("7", "-3", "2.5", "(4,-2)", "以上皆非"):
        assert format_choice_math_display(value) == value


def test_choice_value_and_label_remain_canonical() -> None:
    choices = normalize_choice_displays(
        [
            {"label": "A", "text": "19/2", "value": "19/2"},
            {"label": "B", "text": "sqrt(91)", "value": "sqrt(91)"},
        ]
    )
    assert choices[0]["label"] == "A"
    assert choices[0]["value"] == "19/2"
    assert choices[0]["display"] == r"\(\frac{19}{2}\)"
    assert choices[1]["label"] == "B"
    assert choices[1]["value"] == "sqrt(91)"
    assert choices[1]["display"] == r"\(\sqrt{91}\)"


def test_choice_contract_and_practice_api_include_display_without_changing_values() -> None:
    canonical = normalize_canonical_choices(["19/2", "sqrt(91)", "6*sqrt(10)", "純文字"])
    assert [choice["value"] for choice in canonical] == [
        "19/2",
        "sqrt(91)",
        "6*sqrt(10)",
        "純文字",
    ]
    payload = _finalize_practice_question_api_fields(
        {
            "question_text": "選出正確答案",
            "choices": canonical,
            "correct_answer": "C",
            "answer": "C",
            "presentation_mode": "single_choice",
        }
    )
    assert payload["correct_answer"] == "C"
    assert payload["choices"][2]["value"] == "6*sqrt(10)"
    assert payload["choices"][2]["display"] == r"\(6\sqrt{10}\)"
