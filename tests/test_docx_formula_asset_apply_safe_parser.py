from pathlib import Path

from scripts.docx_formula_asset_pix2tex_backfill import parse_candidates_from_report


def test_parse_safe_write_candidates_and_blocks(tmp_path: Path):
    report = tmp_path / "r.md"
    report.write_text(
        "\n".join(
            [
                "# X",
                "## id=3901 隨堂練習1 [source_type=in_class_practice]",
                "- selected_replacements: `{'[FORMULA_IMAGE_1]': '|x|'}`",
                "- proposed_problem_text: `題目 |x| = 4`",
                "- action: `partial_proposed_update`",
                "- write_recommendation: `yes`",
                "",
                "## id=3902 1-1習題 基礎題1 [source_type=basic_exercise]",
                "- selected_replacements: `{}`",
                "- proposed_problem_text: `題目 [FORMULA_IMAGE_1]`",
                "- action: `no_change`",
                "- write_recommendation: `no`",
                "",
                "## Safe Write Candidates",
                "- id=3901 | source_description=`隨堂練習1 ...` | canonical_title=`隨堂練習1` | action=`partial_proposed_update` | selected_replacements=`{'[FORMULA_IMAGE_1]': '|x|'}` | still_has_formula_missing=`False` | write_recommendation=`yes`",
                "- id=3902 | source_description=`1-1習題 基礎題1 ...` | canonical_title=`1-1習題 基礎題1` | action=`no_change` | selected_replacements=`{}` | still_has_formula_missing=`False` | write_recommendation=`no`",
            ]
        ),
        encoding="utf-8",
    )
    rows, err = parse_candidates_from_report(report)
    assert not err
    assert len(rows) == 2
    row1 = [r for r in rows if r["id"] == 3901][0]
    assert row1["action"] == "partial_proposed_update"
    assert row1["write_recommendation"] == "yes"
    assert row1["selected_replacements"] == {"[FORMULA_IMAGE_1]": "|x|"}
    assert row1["proposed_problem_text"] == "題目 |x| = 4"
    row2 = [r for r in rows if r["id"] == 3902][0]
    assert row2["action"] == "no_change"
    assert row2["selected_replacements"] == {}

