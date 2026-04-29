from core.math_formula_normalizer import (
    detect_suspicious_formula,
    normalize_combination_permutation_notation,
    normalize_math_text,
    normalize_operator_artifacts,
)


def test_combination_subscript_superscript_normalizes_to_stable_form():
    assert normalize_combination_permutation_notation("C_0^5") == "C(5,0)"


def test_combination_superscript_subscript_normalizes_to_stable_form():
    assert normalize_combination_permutation_notation("C^5_0") == "C(5,0)"


def test_permutation_subscript_superscript_normalizes_to_stable_form():
    assert normalize_combination_permutation_notation("P_3^5") == "P(5,3)"


def test_permutation_superscript_subscript_normalizes_to_stable_form():
    assert normalize_combination_permutation_notation("P^5_3") == "P(5,3)"


def test_hash_operator_artifact_normalizes_to_multiplication_sign():
    assert normalize_operator_artifacts("3 # 3 # 5 # 2") == "3 × 3 × 5 × 2"


def test_inconsistent_combination_sum_is_suspicious():
    check = detect_suspicious_formula("C_0^5 + C_1^5 + C_2^6 + C_3^7 + C_4^8")
    assert check["is_suspicious"] is True
    assert "combination_upper_index_inconsistent" in check["reasons"]


def test_consistent_combination_sum_is_not_suspicious():
    check = detect_suspicious_formula("C_0^5 + C_1^5 + C_2^5 + C_3^5 + C_4^5 + C_5^5")
    assert check["is_suspicious"] is False


def test_pdf_artifacts_are_suspicious():
    check = detect_suspicious_formula("公式殘留 _ i、^ h、g，並出現 # # #")
    assert check["is_suspicious"] is True
    assert "suspicious_pdf_artifact" in check["reasons"]


def test_broken_factorial_is_suspicious():
    check = detect_suspicious_formula("排列總數為 5 1 ! 種")
    assert check["is_suspicious"] is True
    assert "suspicious_factorial" in check["reasons"]


def test_normalize_math_text_combines_operator_and_cp_normalization():
    assert normalize_math_text("P_3^5 # C_2^5") == "P(5,3) × C(5,2)"
