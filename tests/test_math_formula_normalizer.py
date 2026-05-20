from core.math_formula_normalizer import normalize_converted_docx_latex_text, normalize_math_text


def test_display_coordinates_a_p_to_inline():
    text = r"在直角坐標平面上，醫院位置為點\[A\left( 1,0 \right)\]，學校的位置在\(B(-3,4)\)，小恩的家位於線段\(AB\)上，且已知小恩家到醫院的距離等於小恩家到學校距離的3倍，試求小恩家在坐標平面上的位置\[P\left( x,y \right)\]。"
    expected = r"在直角坐標平面上，醫院位置為點 \(A\left(1,0\right)\)，學校的位置在 \(B\left(-3,4\right)\)，小恩的家位於線段 \(AB\) 上，且已知小恩家到醫院的距離等於小恩家到學校距離的 \(3\) 倍，試求小恩家在坐標平面上的位置 \(P\left(x,y\right)\)。"
    out = normalize_converted_docx_latex_text(text)
    assert out["text"] == expected


def test_a_b_p_segment_case():
    text = r"坐標平面上兩點\[A\left( -3,0 \right)\]、\(B(9,6)\)，若點\(P\)在\(\overline{AB}\)上，且\(\overline{AP}=2\overline{PB}\)，試求\(P\)點坐標。"
    expected = r"坐標平面上兩點 \(A\left(-3,0\right)\)、\(B\left(9,6\right)\)，若點 \(P\) 在 \(\overline{AB}\) 上，且 \(\overline{AP}=2\overline{PB}\)，試求 \(P\) 點坐標。"
    out = normalize_converted_docx_latex_text(text)
    assert out["text"] == expected


def test_a_b_split_and_q_coordinate():
    text = r"設\(a、b\)為實數，且\(a < b < 0\)，則點\[Q\left( ab,a+b \right)\]在第幾象限？"
    expected = r"設 \(a\)、\(b\) 為實數，且 \(a<b<0\)，則點 \(Q\left(ab,a+b\right)\) 在第幾象限？"
    out = normalize_converted_docx_latex_text(text)
    assert out["text"] == expected


def test_c_coordinate_with_fraction():
    text = r"已知點\(A\left( a,b \right)\)在第二象限內，試求：(1)點\(B\left( b,a \right)\)在第幾象限？(2)點\[C\left( -b,\frac{a}{b} \right)\]在第幾象限？"
    expected = "已知點 \\(A\\left(a,b\\right)\\) 在第二象限內，試求：\n(1) 點 \\(B\\left(b,a\\right)\\) 在第幾象限？\n(2) 點 \\(C\\left(-b,\\frac{a}{b}\\right)\\) 在第幾象限？"
    out = normalize_converted_docx_latex_text(text)
    assert out["text"] == expected


def test_midpoint_distance_case():
    text = r"若\(P\)為\(A\left( -1,4 \right)\)與\[B\left( 3,-2 \right)\]兩點之中點，試求\(P\)點與原點的距離。"
    expected = r"若 \(P\) 為 \(A\left(-1,4\right)\) 與 \(B\left(3,-2\right)\) 兩點之中點，試求 \(P\) 點與原點的距離。"
    out = normalize_converted_docx_latex_text(text)
    assert out["text"] == expected


def test_standalone_display_math_not_converted():
    text = "解：\n\\[\n\\frac{x_1+x_2+x_3}{3}\n\\]\n所以..."
    out = normalize_converted_docx_latex_text(text)
    assert out["text"] == text


def test_cases_array_aligned_not_converted():
    text = "\\[\n\\begin{cases}\nx+y=1\n\\end{cases}\n\\]"
    out = normalize_converted_docx_latex_text(text)
    assert out["text"] == text


def test_existing_inline_not_duplicated():
    text = r"設 \(A\left(1,3\right)\) 為平面上一點。"
    out = normalize_converted_docx_latex_text(text)
    assert out["text"] == text


def test_dollar_math_not_processed():
    text = r"試求 $|x|<3$ 的解。"
    out = normalize_converted_docx_latex_text(text)
    assert out["text"] == text


def test_converted_latex_text_preserves_readable_inline():
    text = r"\(y=\frac{1}{2}(x-2)^{2}+1\) 的圖形，是由 \(y=\frac{1}{2}x^{2}\)，水平向①平移②個單位。"
    out = normalize_converted_docx_latex_text(text)
    assert r"\frac{1}{2}" in out["text"]
    assert "f? r? a? c" not in out["text"]
    assert "? \\? (? y? =?" not in out["text"]


def test_safe_fix_display_short_formula_to_inline():
    text = r"設\[A\left( 1,3 \right)\]為一點"
    out = normalize_converted_docx_latex_text(text)
    assert out["text"] == r"設 \(A\left(1,3\right)\) 為一點"


def test_legacy_normalize_math_text_corrupts_latex():
    text = r"\(y=\frac{1}{2}(x-2)^{2}+1\)"
    corrupted = normalize_math_text(text)
    assert "f? r? a? c" in corrupted or "? \\? (? y? =?" in corrupted


def test_converted_normalizer_preserves_quadratic_latex():
    text = r"\(y=\frac{1}{2}(x-2)^{2}+1\) 的圖形"
    out = normalize_converted_docx_latex_text(text)
    assert r"\frac{1}{2}" in out["text"]
    assert "f? r? a? c" not in out["text"]
