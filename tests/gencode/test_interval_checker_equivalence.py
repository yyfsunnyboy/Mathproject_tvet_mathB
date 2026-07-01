# -*- coding: utf-8 -*-
from __future__ import annotations

import pytest
from core.checkers.interval_checker import check_interval_answer

def test_interval_checker_equivalence_formats() -> None:
    cases = [
        # (user, correct, expected)
        ("[2,5]", "[2,5]", True),
        ("(2,5)", "(2,5)", True),
        ("2<=x<=5", "[2,5]", True),
        ("2<x<5", "(2,5)", True),
        ("2<=x<=5", "2<=x<=5", True),
        ("2<x<5", "2<x<5", True),
        ("1/3<=x<=5/3", "1/3<=x<=5/3", True),
        ("1/3<=x<=5/3", "[1/3,5/3]", True),
        ("2≤x≤5", "[2,5]", True),
        ("2≤x≤5", "2<=x<=5", True),
        ("2<x<5", "2<x<5", True),
    ]

    for user, correct, expected in cases:
        assert check_interval_answer(user, correct) == expected
