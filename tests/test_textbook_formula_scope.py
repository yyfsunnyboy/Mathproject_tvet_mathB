"""Regression coverage for formula / question source-scope resolution."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

import core.textbook_processor_v2 as tpv2
from core.textbook_importer_v3_scope import analyze_scoped_conversion
from core.textbook_mathtype_converter import convert_docx_mathtype_to_latex_docx


SELF_ASSESSMENT = (
    Path(__file__).resolve().parents[1]
    / "textbook_import/source/vocational/math_B2/第二章 自我評量-課本.docx"
)
SECTION_INFO = {
    "curriculum": "vocational",
    "volume": "數學B2",
    "section_code": "3-1",
    "source_scope": "section_textbook",
}


def test_formula_scope_matrix(monkeypatch):
    if not SELF_ASSESSMENT.is_file():
        pytest.skip("DOCX fixture unavailable")

    def fake_extract(_path, *, curriculum_info=None, locations=None):
        lines = ["正文定義公式", "例1", "題目內公式", "表格內正文", "例2", "下一題"]
        if locations is not None:
            locations[:] = [10, 20, 20, 30, 40, 40]
        return lines

    def fake_slice(_lines, **_kwargs):
        tpv2._DOCX_BLOCK_META = {
            "例1": {
                "source_type": "textbook_example",
                "source_line_indices": [1, 2],
                "problem_text": "題目內公式",
                "section_title": "3-1",
            },
            "例2": {
                "source_type": "textbook_example",
                "source_line_indices": [4, 5],
                "problem_text": "下一題",
                "section_title": "3-1",
            },
        }
        return dict(tpv2._DOCX_BLOCK_META)

    def fake_parse(_data, **_kwargs):
        return {
            "blocks": [
                {
                    "type": "paragraph",
                    "paragraph_index": paragraph_index,
                    "xml_path": f"/fake/{paragraph_index}",
                    "plain_text": f"para {paragraph_index}",
                }
                for paragraph_index in (10, 20, 30, 40)
            ],
            "mathtype_oles": [],
            "summary": {},
        }

    monkeypatch.setattr(tpv2, "phase1_extract_docx_lines", fake_extract)
    monkeypatch.setattr(tpv2, "phase2_deterministic_block_slice", fake_slice)
    monkeypatch.setattr("core.textbook_importer_v3_scope.parse_docx_structure", fake_parse)

    conversion_report = {
        "formulas": [
            {
                "formula_index": 1,
                "status": "ok",
                "latex": r"\(a\)",
                "prog_id": "Equation.DSMT4",
                "location": {"paragraph_index": 20, "run_index": 1},
            },
            {
                "formula_index": 2,
                "status": "ok",
                "latex": r"\(\vec{a}\)",
                "prog_id": "Equation.DSMT4",
                "location": {"paragraph_index": 10, "run_index": 0},
            },
            {
                "formula_index": 3,
                "status": "ok",
                "latex": r"\(0\)",
                "prog_id": "Equation.DSMT4",
                "location": {
                    "paragraph_index": 30,
                    "table_index": 1,
                    "row": 0,
                    "col": 1,
                    "in_table_cell": True,
                    "run_index": 2,
                },
            },
            {
                "formula_index": 4,
                "status": "not_mtef",
                "classification": "embedded_ooxml",
                "error": "embedded_ooxml_not_mtef",
                "prog_id": "Word.Document.12",
                "location": {"paragraph_index": 20, "run_index": 3},
            },
            {
                "formula_index": 5,
                "status": "failed",
                "error": "empty_latex",
                "prog_id": "Equation.DSMT4",
                "location": {"paragraph_index": 999999},
            },
        ],
        "eq_field_results": [],
    }

    result = analyze_scoped_conversion(
        SELF_ASSESSMENT,
        SELF_ASSESSMENT,
        SECTION_INFO,
        conversion_report,
        {"textbook_example"},
    )

    assert result["counts"]["required_formula_count"] == 1
    assert result["counts"]["required_formula_success"] == 1
    assert result["counts"]["non_required_formula_count"] == 2
    assert result["counts"]["non_required_formula_success"] == 2
    assert result["counts"]["non_formula_object_skipped"] == 1

    body = {item["formula_index"]: item for item in result["body_formula_scopes"]}
    assert body[2]["question_scope"] is None
    assert body[2]["source_scope"]["paragraph_index"] == 10
    assert body[3]["question_scope"] is None
    assert body[3]["source_scope"]["kind"] == "table_cell"

    unresolved_reasons = {item["reason"] for item in result["unresolved"]}
    assert "formula_location_missing" in unresolved_reasons
    assert "target_equation_object_unsupported" not in unresolved_reasons
    assert all(item.get("formula_index") != 4 for item in result["unresolved"])


def test_not_mtef_inside_target_question_is_skipped_not_scope_error(tmp_path):
    if not SELF_ASSESSMENT.is_file():
        pytest.skip("Self-assessment source DOCX unavailable")

    output = tmp_path / "converted.docx"
    report = convert_docx_mathtype_to_latex_docx(SELF_ASSESSMENT, output)
    fake = copy.deepcopy(report)
    assert fake.get("formulas")
    fake["formulas"][0].update({
        "status": "not_mtef",
        "classification": "embedded_ooxml",
        "error": "embedded_ooxml_not_mtef",
        "prog_id": "Word.Document.12",
    })
    result = analyze_scoped_conversion(
        SELF_ASSESSMENT,
        output,
        {
            "curriculum": "vocational",
            "volume": "數學B2",
            "chapter_index": 2,
            "source_scope": "chapter_self_assessment",
        },
        fake,
        {"self_assessment"},
    )
    assert not any(
        item.get("reason") == "target_equation_object_unsupported"
        for item in result["unresolved"]
    )
    assert result["counts"].get("non_formula_object_skipped", 0) >= 1
