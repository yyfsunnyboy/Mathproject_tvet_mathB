"""Semantic checker for Chinese graph-translation descriptions.

"向左 2、向下 4", "向下4,向左2" and "左移2單位，下降4單位" all normalize to
``{"horizontal_left": 2, "vertical_down": 4}``.  The whole answer must be made of
translation items plus connective filler; any leftover text, a repeated axis, or a
missing / extra item makes the answer non-equivalent.  A correct answer that is not a
translation description makes the checker not applicable (``None``).
"""
from __future__ import annotations

import re
from fractions import Fraction

from core.checkers.math_input_normalization import latex_to_plain, parse_exact_number

_DIRECTION_KEYS = {
    "左": "horizontal_left",
    "右": "horizontal_right",
    "上": "vertical_up",
    "下": "vertical_down",
}
_VERB_DIRECTIONS = {"上升": "上", "上揚": "上", "上扬": "上", "下降": "下", "下沉": "下"}

_CN_DIGITS = {"零": 0, "〇": 0, "一": 1, "二": 2, "兩": 2, "两": 2, "三": 3, "四": 4,
              "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_NUMBER = r"(?:\(*\d+(?:\.\d+)?\)*(?:/\(*\d+(?:\.\d+)?\)*)?|[零〇一二兩两三四五六七八九十]+)"

_ITEM = re.compile(
    r"(?:水平|鉛直|铅直|垂直)?(?:方向)?"
    r"(?:(?P<verb>上升|上揚|上扬|下降|下沉)"
    r"|(?:向|往|朝)?(?P<dir>[左右上下])(?:方)?(?:平移|移動|移动|移)?)"
    r"了?"
    r"(?P<num>" + _NUMBER + r")"
    r"(?:個|个)?(?:單位|单位|格)?(?:長|长)?"
)
_FILLER = re.compile(
    r"(?:[,;/:.。、]|以及|並且|并且|然後|然后|接著|接着|同時|同时|再|並|并|且|及|和|與|与|先|後|后"
    r"|圖形|图形|拋物線|抛物线|函數圖形|將|将|把|平移|即可)+"
)
_NO_SHIFT = frozenset({"不移動", "不移动", "不平移", "不需平移", "不用平移", "沒有平移", "没有平移", "無平移", "无平移"})


def _parse_chinese_number(token: str) -> Fraction | None:
    if not token or any(ch not in _CN_DIGITS and ch != "十" for ch in token):
        return None
    if "十" not in token:
        return Fraction(_CN_DIGITS[token]) if len(token) == 1 else None
    tens_part, _, ones_part = token.partition("十")
    if "十" in ones_part or len(tens_part) > 1 or len(ones_part) > 1:
        return None
    tens = _CN_DIGITS.get(tens_part, None) if tens_part else 1
    ones = _CN_DIGITS.get(ones_part, None) if ones_part else 0
    if tens is None or ones is None:
        return None
    return Fraction(tens * 10 + ones)


def _parse_amount(token: str) -> Fraction | None:
    value = parse_exact_number(token)
    if value is None:
        value = _parse_chinese_number(token)
    return value


def parse_translation_description(text: object) -> dict[str, Fraction] | None:
    """Return ``{semantic_key: amount}`` or None when the text is not a clean translation description."""
    s = re.sub(r"\s+", "", latex_to_plain(text))
    if not s:
        return None
    if s.rstrip("。.") in _NO_SHIFT:
        return {}
    items: dict[str, Fraction] = {}
    axes: set[str] = set()
    pos = 0
    while pos < len(s):
        filler = _FILLER.match(s, pos)
        if filler:
            pos = filler.end()
            if pos >= len(s):
                break
        m = _ITEM.match(s, pos)
        if not m:
            return None
        direction = _VERB_DIRECTIONS.get(m.group("verb") or "", m.group("dir"))
        amount = _parse_amount(m.group("num"))
        if direction is None or amount is None:
            return None
        key = _DIRECTION_KEYS[direction]
        axis = key.split("_", 1)[0]
        if axis in axes:
            return None
        axes.add(axis)
        items[key] = amount
        pos = m.end()
    return items or None


def check_translation_description_answer(user_answer: object, correct_answer: object) -> bool | None:
    """Order-insensitive semantic comparison; None when the correct answer is not a translation."""
    expected = parse_translation_description(correct_answer)
    if expected is None:
        return None
    actual = parse_translation_description(user_answer)
    return actual is not None and actual == expected
