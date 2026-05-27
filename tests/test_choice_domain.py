from __future__ import annotations

import pytest

from core.domain.choices_unique_validator import build_choice_payload, validate_answer_in_choices, validate_choices_unique


def test_validate_choices_unique_pass() -> None:
    assert validate_choices_unique(["1", "2", "3", "4"]) is True


def test_validate_choices_unique_fail() -> None:
    assert validate_choices_unique(["1", "2", "2", "4"]) is False


def test_validate_answer_in_choices() -> None:
    assert validate_answer_in_choices("A", ["A", "B", "C", "D"]) is True
    assert validate_answer_in_choices("E", ["A", "B", "C", "D"]) is False


def test_build_choice_payload() -> None:
    payload = build_choice_payload("正解", ["錯1", "錯2", "錯3"])
    assert len(payload["choices"]) == 4
    assert payload["answer_label"] == "A"
    assert payload["choices"][0]["text"] == "正解"


def test_build_choice_payload_duplicate_raises() -> None:
    with pytest.raises(ValueError):
        build_choice_payload("正解", ["錯1", "錯1", "錯3"])
