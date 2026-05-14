import pytest

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


# ─── B1 座標幾何保護 regression tests ─────────────────────────────────────────
# 以下所有輸入必須原樣保留（不得被改寫為排列/組合記號形式）


@pytest.mark.parametrize(
    "text",
    [
        "點 C(3,1) 在第一象限。",
        "已知點 P(a,b) 在第一象限內。",
        "試求 Q(b,a) 在第幾象限？",
        "點 R(-b,a^2) 在第幾象限？",
        "A(x_1,y_1), B(x_2,y_2) 兩點距離。",
        "若 C(3,1) 為線段 AB 的中點。",
    ],
)
def test_coordinate_point_notation_unchanged(text: str) -> None:
    """座標點語境下，C/P/Q/R/A/B(...) 必須原樣保留，不被正規化為排列組合記號。"""
    assert normalize_combination_permutation_notation(text) == text
    assert normalize_math_text(text) == text


@pytest.mark.parametrize(
    "text",
    [
        "點 C(3,1) 在第一象限。",
        "已知點 P(a,b) 在第一象限內。",
        "試求 Q(b,a) 在第幾象限？",
        "點 R(-b,a^2) 在第幾象限？",
        "A(x_1,y_1), B(x_2,y_2) 兩點距離。",
        "若 C(3,1) 為線段 AB 的中點。",
    ],
)
def test_coordinate_point_not_suspicious(text: str) -> None:
    """座標點語境下，detect_suspicious_formula 不應回報 suspicious_combination_notation。"""
    result = detect_suspicious_formula(text)
    assert "suspicious_combination_notation" not in result["reasons"], (
        f"誤報 suspicious_combination_notation，輸入: {text!r}"
    )


def test_coordinate_multiple_c_points_no_inconsistent_sum() -> None:
    """多個座標點 C(n,r) 不應觸發 combination_upper_index_inconsistent。"""
    text = "設 C(1,2), C(3,4), C(5,6) 為平面上三點。"
    result = detect_suspicious_formula(text)
    assert "combination_upper_index_inconsistent" not in result["reasons"]
    assert "suspicious_combination_notation" not in result["reasons"]


# ─── 真正的排列/組合記號必須仍可正規化 ────────────────────────────────────────


def test_p_sup_sub_still_normalizes() -> None:
    assert normalize_combination_permutation_notation("P^7_3") == "P(7,3)"


def test_c_sup_sub_still_normalizes() -> None:
    assert normalize_combination_permutation_notation("C^7_3") == "C(7,3)"


@pytest.mark.parametrize(
    "text, expected_suspicious",
    [
        # 有明確排列組合語境 → C(n,r) 視為排列組合，不應被誤判無訊號
        ("從 7 人中任取 3 人，共有 C(7,3) 種。", False),
        ("從 7 人中選 3 人排列，共有 P(7,3) 種。", False),
    ],
)
def test_explicit_comb_perm_context_not_suspicious(text: str, expected_suspicious: bool) -> None:
    """有排列組合關鍵字時，C(n,r)/P(n,r) 不應被誤報為 suspicious_combination_notation。"""
    result = detect_suspicious_formula(text)
    assert ("suspicious_combination_notation" in result["reasons"]) == expected_suspicious


def test_comb_perm_context_c_paren_recognized() -> None:
    """排列組合語境中 C(7,3) 應被提取為有效 combination term。"""
    from core.math_formula_normalizer import _extract_comb_perm_terms
    terms = _extract_comb_perm_terms("共有 C(7,3) 種")
    assert ("C", 7, 3) in terms


def test_coordinate_context_c_paren_excluded_from_terms() -> None:
    """座標語境（無排列組合關鍵字）中 C(3,1) 不得被計為 combination term。"""
    from core.math_formula_normalizer import _extract_comb_perm_terms
    terms = _extract_comb_perm_terms("點 C(3,1) 在第一象限", include_normalized=False)
    assert ("C", 3, 1) not in terms


def test_standalone_cp_without_context_not_suspicious() -> None:
    """無任何語境的 P(a,b) 單獨出現，不應觸發 suspicious_combination_notation。"""
    result = detect_suspicious_formula("P(a,b)")
    assert "suspicious_combination_notation" not in result["reasons"]


def test_ocr_spaced_cp_still_normalizes_outside_coord_context() -> None:
    """非座標語境下，OCR 分割的 'P 3 5' 仍應被正規化（P_3^5 記法 → P(5,3)）。"""
    assert normalize_combination_permutation_notation("P 3 5") == "P(5,3)"


def test_coord_context_spaced_cp_protected() -> None:
    """座標語境中，'C 3 1 在第一象限' 不應被轉成 C(1,3)（防止 OCR 誤轉）。"""
    text = "點 C 3 1 在第一象限"
    result = normalize_combination_permutation_notation(text)
    assert "C(1,3)" not in result


@pytest.mark.parametrize(
    "text",
    [
        "設 A(-1,2), B(3,3), C(1,2) 依序為平行四邊形 ABCD 之三頂點。",
        "設三角形 ABC 的三頂點為 A(2,5), B(-3,2), C(2,4)。",
        "點 P(a,b) 位在第一象限，Q(b,a)、R(-b,a^2) 亦為平面上之點。",
    ],
)
def test_b1_coordinate_samples_not_suspicious(text: str) -> None:
    result = detect_suspicious_formula(text)
    assert "suspicious_combination_notation" not in result["reasons"]
