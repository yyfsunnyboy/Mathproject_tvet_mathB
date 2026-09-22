from __future__ import annotations

import copy
import shutil
import sys
from pathlib import Path

import pytest
from flask import Flask

from core.textbook_importer_v3_pipeline import run_v3_pair_pipeline
from core.textbook_importer_v3_scope import analyze_scoped_conversion
from core.textbook_mathtype_converter import convert_docx_mathtype_to_latex_docx


TARGETS = {"textbook_example", "in_class_practice", "self_assessment", "exam_practice"}
SOURCE = (
    Path(__file__).resolve().parents[1]
    / "textbook_import/source/vocational/math_B2/第二章 2-1 正弦定理與餘弦定理-課本.docx"
)
INFO = {
    "curriculum": "vocational", "volume": "數學B2",
    "chapter": "第二章", "section": "2-1 正弦定理與餘弦定理",
    "section_code": "2-1", "source_scope": "section_textbook",
}


@pytest.fixture(scope="module")
def converted(tmp_path_factory):
    if not SOURCE.is_file():
        pytest.skip("B2 2-1 source DOCX unavailable")
    output = tmp_path_factory.mktemp("b2_scoped") / "converted.docx"
    report = convert_docx_mathtype_to_latex_docx(SOURCE, output)
    return output, report


def _scope(converted, report=None):
    output, original_report = converted
    return analyze_scoped_conversion(
        SOURCE, output, INFO, report or original_report, TARGETS
    )


def test_b2_scope_uses_existing_source_types_and_read_only_parser(converted):
    result = _scope(converted)
    assert result["question_count"] == 21
    assert result["target_count"] == 11
    assert result["target_source_type_counts"] == {
        "textbook_example": 5, "in_class_practice": 5,
        "self_assessment": 0, "exam_practice": 1,
    }
    assert sum(q["would_write"] == "NO" for q in result["questions"]) == 10
    assert result["would_write_count"] == 11
    assert result["unresolved"] == []


def test_required_formulas_include_example_solution_continuation(converted):
    result = _scope(converted)
    assert result["counts"]["required_formula_count"] == 73
    assert result["counts"]["required_formula_success"] == 73
    assert result["counts"]["required_formula_failed"] == 0
    assert result["counts"]["non_required_formula_count"] == 117
    assert result["questions"][2]["formula_count"] == 13  # 例2 includes its solution continuation.


def test_non_target_formula_failure_is_non_blocking(converted):
    report = copy.deepcopy(converted[1])
    non_target = next(f for f in report["formulas"] if f["location"]["paragraph_index"] == 1)
    non_target.update(status="failed", error="simulated", latex="[MATH_PARSE_FAILED_test]")
    result = _scope(converted, report)
    assert result["counts"]["non_required_formula_failed"] == 1
    assert result["counts"]["required_formula_failed"] == 0
    assert result["would_write_count"] == 11


def test_target_formula_failure_blocks_its_question(converted):
    report = copy.deepcopy(converted[1])
    target = next(f for f in report["formulas"] if f["location"]["paragraph_index"] == 22)
    target.update(status="failed", error="simulated", latex="[MATH_PARSE_FAILED_test]")
    result = _scope(converted, report)
    assert result["counts"]["required_formula_failed"] == 1
    assert result["questions"][0]["would_write"] == "BLOCKED_FORMULA"


def test_unresolved_formula_location_is_reported(converted):
    report = copy.deepcopy(converted[1])
    report["formulas"][0]["location"] = {"paragraph_index": 999999}
    result = _scope(converted, report)
    assert result["unresolved"]
    assert result["unresolved"][0]["reason"] == "formula_location_missing"


def test_images_are_candidates_with_review_metadata(converted):
    result = _scope(converted)
    assert result["image_candidate_count"] == 5
    assert result["image_needs_review_count"] == 5
    assert all(
        not image["filename"].lower().endswith((".wmf", ".emf"))
        for question in result["questions"] for image in question["image_candidates"]
    )


def test_runtime_uses_application_interpreter_and_converter(converted):
    result = _scope(converted)
    assert result["runtime"]["sys_executable"] == sys.executable
    assert result["runtime"]["olefile"]
    assert result["runtime"]["converter"].endswith("textbook_mathtype_converter.py")


def test_scoped_pipeline_dry_run_does_not_reach_db_write(tmp_path, converted, monkeypatch):
    import core.textbook_importer_v3_pipeline as pipeline

    source = tmp_path / SOURCE.name
    shutil.copyfile(SOURCE, source)

    def fake_convert(_source, output):
        shutil.copyfile(converted[0], output)
        return copy.deepcopy(converted[1])

    monkeypatch.setattr(pipeline, "convert_docx_mathtype_to_latex_docx", fake_convert)
    monkeypatch.setattr(pipeline, "ensure_db_backup", lambda **_kwargs: pytest.fail("DB path reached"))
    result = run_v3_pair_pipeline(
        project_root=tmp_path, docx_path=source, pdf_path=None,
        curriculum="vocational", volume="數學B2", allow_phase4=False,
        target_source_types=TARGETS, app=Flask("scoped_dry_run_test"),
    )
    assert result["ok"] is True
    assert result["would_write"] == 11
    assert "db_write" not in result["metrics"]


def test_scoped_pipeline_non_target_failure_is_warning(tmp_path, converted, monkeypatch):
    import core.textbook_importer_v3_pipeline as pipeline

    source = tmp_path / SOURCE.name
    shutil.copyfile(SOURCE, source)
    fake_report = copy.deepcopy(converted[1])
    item = next(f for f in fake_report["formulas"] if f["location"]["paragraph_index"] == 1)
    item.update(status="failed", error="simulated", latex="[MATH_PARSE_FAILED_test]")
    fake_report["converted_ok"] -= 1
    fake_report["converted_failed"] += 1

    def fake_convert(_source, output):
        shutil.copyfile(converted[0], output)
        return fake_report

    monkeypatch.setattr(pipeline, "convert_docx_mathtype_to_latex_docx", fake_convert)
    result = run_v3_pair_pipeline(
        project_root=tmp_path, docx_path=source, pdf_path=None,
        curriculum="vocational", volume="數學B2", allow_phase4=False,
        target_source_types=TARGETS, app=Flask("scoped_warning_test"),
    )
    assert result["ok"] is True
    assert result["scoped_import"]["counts"]["non_required_formula_failed"] == 1
    assert result["warnings"] == ["non_required_formula_conversion_failed"]


@pytest.mark.parametrize(
    ("failure_mode", "error_code"),
    [("target_failed", "source_fidelity_formula_failed"),
     ("unresolved", "source_fidelity_scope_unresolved")],
)
def test_scoped_pipeline_gate_fails_before_db(
    tmp_path, converted, monkeypatch, failure_mode, error_code
):
    import core.textbook_importer_v3_pipeline as pipeline

    source = tmp_path / SOURCE.name
    shutil.copyfile(SOURCE, source)
    fake_report = copy.deepcopy(converted[1])
    item = next(f for f in fake_report["formulas"] if f["location"]["paragraph_index"] == 22)
    if failure_mode == "target_failed":
        item.update(status="failed", error="simulated", latex="[MATH_PARSE_FAILED_test]")
    else:
        item["location"] = {"paragraph_index": 999999}

    def fake_convert(_source, output):
        shutil.copyfile(converted[0], output)
        return fake_report

    monkeypatch.setattr(pipeline, "convert_docx_mathtype_to_latex_docx", fake_convert)
    monkeypatch.setattr(pipeline, "ensure_db_backup", lambda **_kwargs: pytest.fail("DB path reached"))
    result = run_v3_pair_pipeline(
        project_root=tmp_path, docx_path=source, pdf_path=None,
        curriculum="vocational", volume="數學B2", allow_phase4=False,
        target_source_types=TARGETS, app=Flask("scoped_gate_test"),
    )
    assert result["ok"] is False
    assert result["error"]["error_code"] == error_code


def test_legacy_call_signature_keeps_default_scope_off():
    import inspect

    import core.textbook_processor_v2 as tpv2
    from core.textbook_processor_v2 import (
        _build_anchor_blocks_v2,
        phase2_deterministic_block_slice,
        phase2_mathb_section_anchor_slice,
        phase4_absolute_hydrate_and_save,
    )

    assert inspect.signature(run_v3_pair_pipeline).parameters["target_source_types"].default is None
    assert inspect.signature(phase2_deterministic_block_slice).parameters["read_only"].default is False
    assert inspect.signature(phase2_mathb_section_anchor_slice).parameters["read_only"].default is False
    assert inspect.signature(_build_anchor_blocks_v2).parameters["read_only"].default is False
    assert inspect.signature(phase4_absolute_hydrate_and_save).parameters["target_source_types"].default is None
    assert inspect.signature(tpv2.phase1_extract_docx_lines).parameters["locations"].default is None


def _heading_probe_lines():
    return ["2-1.1 正弦定理", "例1", "題目內容", "解", "詳解"]


def _heading_probe_info():
    return {
        "curriculum": "vocational",
        "volume": "數學B2",
        "section_code": "2-1",
        "section": "2-1 正弦定理與餘弦定理",
        "chapter": "第二章",
        "source_scope": "section_textbook",
    }


def _spy_phase2_skill_side_effects(monkeypatch):
    import core.textbook_processor_v2 as tpv2

    calls = {"lookup": [], "resolve": [], "persist": []}

    def fake_lookup(**kwargs):
        calls["lookup"].append(kwargs)
        return ""

    def fake_resolve(**kwargs):
        calls["resolve"].append(kwargs)
        return {
            "concept_name": kwargs.get("concept_name") or "正弦定理",
            "concept_en_id": "LawOfSines",
            "formal_skill_id": "vh_數學B2_LawOfSines",
        }

    def fake_persist(**kwargs):
        calls["persist"].append(kwargs)

    monkeypatch.setattr(tpv2, "_find_existing_skill_id_by_section_and_ch_name", fake_lookup)
    monkeypatch.setattr(tpv2, "_resolve_formal_concept_en_id_v2", fake_resolve)
    monkeypatch.setattr(tpv2, "_persist_formal_skill_from_docx_heading", fake_persist)
    return calls


def test_legacy_phase2_still_looks_up_and_persists_skills(monkeypatch):
    from core.textbook_processor_v2 import _build_anchor_blocks_v2

    calls = _spy_phase2_skill_side_effects(monkeypatch)
    _, meta = _build_anchor_blocks_v2(
        _heading_probe_lines(),
        section_code="2-1",
        curriculum_info=_heading_probe_info(),
    )
    assert "例1" in meta
    assert "source_line_indices" not in meta["例1"]
    assert calls["lookup"]
    assert calls["resolve"]
    assert calls["persist"]
    assert meta["例1"]["formal_skill_id"] == "vh_數學B2_LawOfSines"


def test_read_only_phase2_is_opt_in_and_skips_skill_concept_persistence(monkeypatch):
    from core.textbook_processor_v2 import _build_anchor_blocks_v2

    calls = _spy_phase2_skill_side_effects(monkeypatch)
    _, meta = _build_anchor_blocks_v2(
        _heading_probe_lines(),
        section_code="2-1",
        curriculum_info=_heading_probe_info(),
        read_only=True,
    )
    assert "例1" in meta
    assert meta["例1"]["source_type"] == "textbook_example"
    assert "source_line_indices" in meta["例1"]
    assert calls["lookup"] == []
    assert calls["resolve"] == []
    assert calls["persist"] == []


def test_scoped_prescan_uses_read_only_and_skips_persistence(converted, monkeypatch):
    import core.textbook_processor_v2 as tpv2

    calls = _spy_phase2_skill_side_effects(monkeypatch)
    read_only_flags = []
    real_phase2 = tpv2.phase2_deterministic_block_slice

    def wrapped_phase2(*args, **kwargs):
        read_only_flags.append(bool(kwargs.get("read_only")))
        return real_phase2(*args, **kwargs)

    monkeypatch.setattr(tpv2, "phase2_deterministic_block_slice", wrapped_phase2)
    result = _scope(converted)
    assert read_only_flags == [True]
    assert calls["lookup"] == []
    assert calls["resolve"] == []
    assert calls["persist"] == []
    assert result["target_count"] == sum(q["target"] for q in result["questions"])
    assert {q["source_type"] for q in result["questions"] if q["target"]} <= TARGETS
    assert all(q["would_write"] == "NO" for q in result["questions"] if not q["target"])


def test_legacy_pipeline_does_not_call_scoped_analyzer_or_read_only(
    tmp_path, converted, monkeypatch
):
    import core.textbook_importer_v3_pipeline as pipeline
    import core.textbook_processor_v2 as tpv2

    source = tmp_path / SOURCE.name
    shutil.copyfile(SOURCE, source)
    phase2_flags = []
    real_phase2 = tpv2.phase2_deterministic_block_slice

    def wrapped_phase2(*args, **kwargs):
        phase2_flags.append(kwargs.get("read_only", False))
        return real_phase2(*args, **kwargs)

    def fake_convert(_source, output):
        shutil.copyfile(converted[0], output)
        report = copy.deepcopy(converted[1])
        failed = next(f for f in report["formulas"] if f["location"]["paragraph_index"] == 1)
        failed.update(status="failed", error="simulated", latex="[MATH_PARSE_FAILED_test]")
        report["converted_ok"] -= 1
        report["converted_failed"] += 1
        return report

    monkeypatch.setattr(pipeline, "convert_docx_mathtype_to_latex_docx", fake_convert)
    monkeypatch.setattr(tpv2, "phase2_deterministic_block_slice", wrapped_phase2)
    monkeypatch.setattr(
        "core.textbook_importer_v3_scope.analyze_scoped_conversion",
        lambda *_args, **_kwargs: pytest.fail("legacy mode must not run scoped pre-scan"),
    )
    result = run_v3_pair_pipeline(
        project_root=tmp_path, docx_path=source, pdf_path=None,
        curriculum="vocational", volume="數學B2", allow_phase4=False,
        app=Flask("legacy_formula_gate_test"),
    )
    assert result["ok"] is False
    assert result["error"]["error_code"] == "source_fidelity_formula_failed"
    assert "scoped_import" not in result
    assert phase2_flags == []
