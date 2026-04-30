from core.math_expression_formatter import (
    detect_unwrapped_latex_scripts,
    parse_standard_latex_problem,
    standardize_problem_latex,
)


def test_p_4_2():
    out, _ = standardize_problem_latex("P(4,2)")
    assert out == r"\({}^{4}P_{2}\)"


def test_p_6_3():
    out, _ = standardize_problem_latex("P(6,3)")
    assert out == r"\({}^{6}P_{3}\)"


def test_p_8_8():
    out, _ = standardize_problem_latex("P(8,8)")
    assert out == r"\({}^{8}P_{8}\)"


def test_p_power_sub():
    out, _ = standardize_problem_latex("P^n_4")
    assert out == r"\({}^{n}P_{4}\)"


def test_p_7_3():
    out, _ = standardize_problem_latex("P^7_3")
    assert out == r"\({}^{7}P_{3}\)"


def test_p_sub_power():
    out, _ = standardize_problem_latex("P_4^n")
    assert out == r"\({}^{n}P_{4}\)"


def test_p_braced():
    out, _ = standardize_problem_latex("P^{20}_{2}")
    assert out == r"\({}^{20}P_{2}\)"


def test_p_already_standard():
    out, _ = standardize_problem_latex(r"{}^{20}P_{2}")
    assert out == r"\({}^{20}P_{2}\)"


def test_not_double_wrap():
    out, _ = standardize_problem_latex(r"\({}^{4}P_{2}\)")
    assert out == r"\({}^{4}P_{2}\)"


def test_multiple_perm_in_one_sentence():
    src = "試求下列各式之值：(1) P(4,2) (2) P(6,3) (3) P(8,8)"
    out, _ = standardize_problem_latex(src)
    assert r"(1) \({}^{4}P_{2}\)" in out
    assert r"(2) \({}^{6}P_{3}\)" in out
    assert r"(3) \({}^{8}P_{8}\)" in out


def test_c_5_2():
    out, _ = standardize_problem_latex("C(5,2)")
    assert out == r"\({}^{5}C_{2}\)"


def test_c_power_sub():
    out, _ = standardize_problem_latex("C^n_3")
    assert out == r"\({}^{n}C_{3}\)"


def test_keep_existing_frac():
    out, _ = standardize_problem_latex(r"\(\frac{10!}{8!}\)")
    assert out == r"\(\frac{10!}{8!}\)"


def test_detect_unwrapped_scripts():
    hits = detect_unwrapped_latex_scripts("{}^4P_2 and x^2 and a_1")
    assert any("P_2" in h or "P_2" in h.replace(" ", "") for h in hits)


def test_parse_permutation_equation():
    parsed = parse_standard_latex_problem(r"\({}^{n}P_{4}=20\times{}^{n}P_{2}\)")
    assert parsed["type"] == "permutation_equation"
    assert parsed["left"] == {"n": "n", "r": 4}
    assert parsed["multiplier"] == 20
    assert parsed["right"] == {"n": "n", "r": 2}


def test_sentence_equation_standard():
    src = "設 P^n_4 = 20 × P^n_2，試求自然數 n 的值。"
    out, _ = standardize_problem_latex(src)
    assert r"\({}^{n}P_{4}=20\times{}^{n}P_{2}\)" in out
    assert r"\(n\)" in out


def test_textbook_processor_calls_standardize_before_save():
    src = open("core/textbook_processor.py", "r", encoding="utf-8").read()
    assert "db_problem_text, ex_math_meta = standardize_problem_latex" in src
    assert "practice_problem, practice_math_meta = standardize_problem_latex" in src
