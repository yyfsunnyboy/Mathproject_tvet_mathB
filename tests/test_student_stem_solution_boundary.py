# -*- coding: utf-8 -*-
"""Student stems must stop at a solution marker, including Word EQ badges."""

from core.textbook_solution_boundary import split_student_stem_at_solution_marker

_EXAMPLE_12231 = (
    r"已知\(log2\approx 0.3010\)，則\(2 ^ { 100 }\)為幾位數？"
    "\n"
    r"\(\o\ac(○,解)\) 因為\(log2 ^ { 100 } =100\times log2\approx 100\times 0.3010=30.10=30+0.10\)"
)
_EXAMPLE_12231_STEM = r"已知\(log2\approx 0.3010\)，則\(2 ^ { 100 }\)為幾位數？"

_REPRESENTATIVE_STEMS = [
    r"解方程式 \(2x+1=7\)",
    r"下列哪一個數是方程式 \(x^2-1=0\) 的解？",
    r"若此式無解，試說明理由。",
    r"已知 \(\log 2 \approx 0.3010\)，利用對數性質求 \(\log 20\)。",
    r"利用換底公式求 \(\log_3 27\) 的值。",
    r"計算 \(\frac{2}{3}+\frac{1}{6}\)。",
    r"化簡 \(\sqrt{12}+2^{100}\)。",
    r"試利用對數表查出 \(log4.58\) 的近似值。",
    "解析幾何中，兩直線的交點為何？",
]


def test_student_stem_no_solution_marker_or_eq_field_residue():
    stem, solution = split_student_stem_at_solution_marker(_EXAMPLE_12231)
    assert stem == _EXAMPLE_12231_STEM
    assert r"\o" not in stem
    assert r"\ac" not in stem
    assert "○解" not in stem
    assert "因為" not in stem
    assert "因為" in solution
    for sample in _REPRESENTATIVE_STEMS:
        assert split_student_stem_at_solution_marker(sample) is None


def test_eq_badge_and_solution_labels_open_the_solution_region():
    assert split_student_stem_at_solution_marker(r"eq \o\ac(○,解)因為") == ("", "因為")
    assert split_student_stem_at_solution_marker("題幹？\n解：因為 a=1") == ("題幹？", "因為 a=1")
    assert split_student_stem_at_solution_marker("題幹？\n詳解\n移項")[0] == "題幹？"
    assert split_student_stem_at_solution_marker("題幹○解所以") == ("題幹", "所以")
