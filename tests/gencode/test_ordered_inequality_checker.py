from core.checkers.ordered_inequality_checker import check_ordered_inequality_answer

def test_ordered_inequality_accepts_same_and_reversed_semantic_order():
    expected="sin10° < sin50° < sin80°"
    assert check_ordered_inequality_answer("sin10°<sin50°<sin80°",expected)
    assert check_ordered_inequality_answer("sin80° > sin50° > sin10°",expected)
    assert not check_ordered_inequality_answer("sin10° > sin50° > sin80°",expected)

def test_ordered_inequality_rejects_missing_or_non_strict_structure():
    assert not check_ordered_inequality_answer("sin10°,sin50°,sin80°","sin10°<sin50°<sin80°")
    assert not check_ordered_inequality_answer("a<=b","a<b")
