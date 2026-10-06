import pytest

from core.mistake_notebook_answer_display import format_mistake_answer


@pytest.mark.parametrize(
    "raw,expected",
    [
        ('{"part_1": "23x"}', "23x"),
        ('{"part_1": "3"}', "3"),
        ('{"part_1": "2x"}', "2x"),
        ('{"part_1":"3","part_2":"2x","part_3":"-5"}', "(1) 3\u3000(2) 2x\u3000(3) -5"),
        ('{"part_2":"2x","part_10":"9","part_1":"3"}', "(1) 3\u3000(2) 2x\u3000(3) 9"),
        ('{"part_1":"3","part_2":""}', "(1) 3\u3000(2) 未作答"),
        ('{"part_1":"\\\\frac{3}{4}"}', "\\(\\frac{3}{4}\\)"),
        ('["1", "2"]', "(1) 1\u3000(2) 2"),
        ("23x", "23x"),
        ("x = 3 或 x = -1", "x = 3 或 x = -1"),
        ("$\\frac{1}{2}$", "$\\frac{1}{2}$"),
        ("5", "5"),
    ],
)
def test_formats_stored_answers_for_students(raw, expected):
    assert format_mistake_answer(raw) == expected


@pytest.mark.parametrize("raw", [None, "", "   ", "{}", "[]", '{"part_1": ""}', '{"part_1": null, "part_2": " "}'])
def test_blank_answers_show_unanswered(raw):
    assert format_mistake_answer(raw) == "未作答"


@pytest.mark.parametrize("raw", ['{"part_1": "3"', "{not json}", "[1, 2"])
def test_malformed_json_falls_back_to_original_text(raw):
    assert format_mistake_answer(raw) == raw
