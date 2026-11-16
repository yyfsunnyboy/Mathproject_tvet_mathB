"""Data-table vs layout-container classification and LaTeX array round-trip."""
from core.docx_data_tables import (
    array_fingerprints,
    cell_to_latex,
    expected_stem_pictures,
    expected_stem_tables,
    grid_fingerprint,
    grid_to_latex,
    stem_retains_table,
)


def test_grid_to_latex_round_trip_fingerprint():
    rows = [
        ["", "平常成績", "第一次期中考", "期末考"],
        ["分數", "83", "68", "x"],
        ["比重", "30%", "20%", "30%"],
    ]
    latex = grid_to_latex(rows)
    assert latex.startswith("\\(\\begin{array}{|c|c|c|c|}")
    assert r"\text{平常成績}" in latex
    assert r"30\%" in latex
    assert stem_retains_table(latex, {"fingerprint": grid_fingerprint(rows)})
    assert grid_fingerprint(rows) in array_fingerprints("題幹\n" + latex + "\n求x的值。")


def test_cell_to_latex_keeps_numbers_and_wraps_labels():
    assert cell_to_latex("83") == "83"
    assert cell_to_latex("30%") == r"30\%"
    assert cell_to_latex("x") == "x"
    assert r"\text{數學}" in cell_to_latex("數學")


def test_expected_stem_filters_ignore_solution_and_keywords():
    ev = {
        "tables": [
            {"fingerprint": "a", "expected": True, "location": "stem"},
            {"fingerprint": "b", "expected": True, "location": "solution"},
            {"fingerprint": "c", "expected": False, "location": "stem"},
        ],
        "pictures": [
            {"sha256": "p1", "expected": True, "location": "stem"},
            {"sha256": "p2", "expected": True, "location": "solution"},
        ],
    }
    assert [t["fingerprint"] for t in expected_stem_tables(ev)] == ["a"]
    assert [p["sha256"] for p in expected_stem_pictures(ev)] == ["p1"]
    assert expected_stem_tables({}) == []
    assert expected_stem_pictures(None) == []
