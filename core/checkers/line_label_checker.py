from __future__ import annotations

import re
from typing import Any


def normalize_line_label(value: object) -> str | None:
    s = str(value or "").strip()
    if not s:
        return None
    
    # 移除所有空白，將全形數字轉為半形數字，並轉為小寫
    s = s.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    s = re.sub(r"\s+", "", s).lower()
    
    # 正則匹配規則
    # 支援：L_1, L1, L 1, 1, 第一條, 第一直線, 直線 L1, 直線 L_1, 第一
    if re.match(r"^(l_?1|1|第一條|第一直線|直線l_?1|直線1|第一)$", s):
        return "L_1"
    # 支援：L_2, L2, L 2, 2, 第二條, 第二直線, 直線 L2, 直線 L_2, 第二
    if re.match(r"^(l_?2|2|第二條|第二直線|直線l_?2|直線2|第二)$", s):
        return "L_2"
        
    return None


def check_line_label_answer(user_answer: object, correct_answer: object) -> bool:
    expected = normalize_line_label(correct_answer)
    actual = normalize_line_label(user_answer)
    if expected is None:
        # 如果正確答案本身不是 L_1 或 L_2 類，做一般的字串精確比對
        return str(user_answer or "").strip() == str(correct_answer or "").strip()
    if actual is None:
        return False
    return actual == expected


def check(user_answer: Any, correct_answer: Any) -> bool:
    return check_line_label_answer(user_answer, correct_answer)
