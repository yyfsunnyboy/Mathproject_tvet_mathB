"""Read-only fidelity coverage for numbered chapter self-assessment questions."""

import copy
import shutil
from pathlib import Path

import pytest
from flask import Flask

import core.textbook_processor_v2 as processor
import core.textbook_importer_v3_pipeline as pipeline
from core.textbook_import_authority import ImportAuthorityResolver
from core.textbook_importer_v3_scope import analyze_scoped_conversion
from core.textbook_mathtype_converter import convert_docx_mathtype_to_latex_docx


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "textbook_import/source/vocational/math_B2/第二章 自我評量-課本.docx"
)
INFO = {
    "curriculum": "vocational", "volume": "數學B2", "chapter_index": 2,
    "source_scope": "chapter_self_assessment",
}


@pytest.fixture(scope="module")
def converted(tmp_path_factory):
    if not SOURCE.is_file():
        pytest.skip("Self-assessment source DOCX unavailable")
    output = tmp_path_factory.mktemp("self_assessment_scope") / "converted.docx"
    report = convert_docx_mathtype_to_latex_docx(SOURCE, output)
    return output, report


def test_numbered_questions_keep_source_line_provenance_and_section():
    lines = ["自我評量", "2-1 正弦定理", "1. 題目", "公式續行",
             "2-2 三角測量", "2. 下一題", "表格內公式"]
    blocks = processor.phase2_deterministic_block_slice(
        lines, source_scope="chapter_self_assessment",
        curriculum_info=INFO, read_only=True,
    )
    metadata = list(processor._DOCX_BLOCK_META.values())
    assert len(blocks) == len(metadata) == 2
    assert [m["source_line_indices"] for m in metadata] == [[2, 3], [5, 6]]
    assert [m["section_code"] for m in metadata] == ["2-1", "2-2"]
    assert all(m["source_type"] == "self_assessment" for m in metadata)
    assert all(key.startswith("第2章自我評量") for key in blocks)
    for meta in metadata:
        authority = ImportAuthorityResolver.resolve_section_authority(
            source_scope="chapter_self_assessment", curriculum_info=INFO,
            block_meta=meta, gemini_section_code="2-1", phase4=True,
        )
        assert authority["section_code"] == meta["section_code"]


def test_actual_docx_formula_and_image_ownership(converted):
    output, report = converted
    result = analyze_scoped_conversion(SOURCE, output, INFO, report, {"self_assessment"})
    assert result["question_count"] == 15
    assert result["target_count"] == 15
    assert result["unresolved"] == []
    assert result["counts"]["required_formula_count"] == report["mathtype_ole"] == 63
    assert result["counts"]["required_formula_failed"] == 0
    assert result["image_candidate_count"] == result["image_needs_review_count"] == 4
    assert [q["section"].split()[0] for q in result["questions"]] == ["2-1"] * 6 + ["2-2"] * 9
    assert all(q["paragraph_indices"] and q["source_type"] == "self_assessment"
               for q in result["questions"])


def test_unowned_formula_in_subsection_heading_still_fails(converted):
    output, original = converted
    report = copy.deepcopy(original)
    report["formulas"][0]["location"] = {"paragraph_index": 14}
    result = analyze_scoped_conversion(SOURCE, output, INFO, report, {"self_assessment"})
    assert any(item["reason"] == "unresolved_formula_scope"
               for item in result["unresolved"])
    assert result["counts"]["required_formula_count"] == 62


def test_actual_docx_phase2_legacy_metadata_unchanged(converted):
    output, _ = converted
    lines = processor.phase1_extract_docx_lines(str(output), curriculum_info=INFO)
    assert not any("MATH_PARSE_FAILED:symbol" in line for line in lines)
    processor.phase2_deterministic_block_slice(
        lines, source_scope="chapter_self_assessment", curriculum_info=INFO,
    )
    assert all("source_line_indices" not in item
               for item in processor._DOCX_BLOCK_META.values())


def test_actual_docx_pipeline_dry_run_passes_gate_without_db_write(
    tmp_path, converted, monkeypatch
):
    source_copy = tmp_path / SOURCE.name
    shutil.copyfile(SOURCE, source_copy)

    def reuse_conversion(_source, output):
        shutil.copyfile(converted[0], output)
        return copy.deepcopy(converted[1])

    monkeypatch.setattr(pipeline, "convert_docx_mathtype_to_latex_docx", reuse_conversion)
    monkeypatch.setattr(
        pipeline, "ensure_db_backup", lambda **_kwargs: pytest.fail("DB write path reached")
    )
    result = pipeline.run_v3_pair_pipeline(
        project_root=tmp_path, docx_path=source_copy, pdf_path=None,
        curriculum="vocational", volume="數學B2", allow_phase4=False,
        target_source_types={"self_assessment"}, app=Flask("self_assessment_dry_run"),
    )
    assert result["ok"] is True
    assert result["scoped_import"]["unresolved"] == []
    assert result["would_write"] == 15
    assert "db_write" not in result["metrics"]
