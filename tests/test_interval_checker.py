from core.checkers.interval_checker import check_interval_answer


def test_interval_checker_cases() -> None:
    assert check_interval_answer("-8 <= x <= 8", "[-8,8]")
    assert check_interval_answer("-8 ≤ x ≤ 8", "[-8,8]")
    assert check_interval_answer("-7 < x < 7", "(-7,7)")
    assert check_interval_answer("-4 <= x < 2", "[-4,2)")
    assert check_interval_answer("x < -10 或 x > 10", "(-∞,-10) ∪ (10,∞)")
    assert check_interval_answer("x <= -12 或 x >= 12", "(-∞,-12] ∪ [12,∞)")

    assert not check_interval_answer("-8 < x < 8", "[-8,8]")
    assert not check_interval_answer("x < -10 或 x > 9", "x < -10 或 x > 10")

