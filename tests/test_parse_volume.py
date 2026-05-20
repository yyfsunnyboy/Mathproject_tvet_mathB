import re

import pytest

from core.textbook_processor import parse_volume


def test_parse_volume_math_b_numbered():
    assert parse_volume("數學B1") == ("B", 1)
    assert parse_volume("數學B4") == ("B", 4)
    assert parse_volume("數學 b2") == ("B", 2)


def test_parse_volume_short_form():
    assert parse_volume("B1") == ("B", 1)


def test_parse_volume_math_a():
    assert parse_volume("數學A2") == ("A", 2)


def test_parse_volume_empty_and_none():
    assert parse_volume("") == (None, None)
    assert parse_volume(None) == (None, None)


def test_parse_volume_chinese_volume_no_re_error():
    subject, vol = parse_volume("數學B 第一冊")
    assert subject == "B"
    assert vol == 1


def test_parse_volume_no_re_error_on_common_strings():
    samples = [
        "數學B1",
        "1-4_-_Latex",
        "1-4_-_Latex.docx",
        "vh_數學B4_xxx",
        "???",
        "mathB4",
        "普通班",
        "",
    ]
    for s in samples:
        try:
            parse_volume(s)
        except re.error as e:
            pytest.fail(f"parse_volume({s!r}) raised re.error: {e}")
