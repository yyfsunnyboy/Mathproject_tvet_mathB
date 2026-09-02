# -*- coding: utf-8 -*-
import io

import pytest
from werkzeug.datastructures import FileStorage

from core.textbook_importer_v3_source import (
    build_file_map,
    build_source_pairs,
    classify_textbook_source,
    get_base_name,
    sort_source_pairs,
    validate_textbook_source_batch,
)


def _make_file(filename: str, content: bytes = b"x") -> FileStorage:
    return FileStorage(
        stream=io.BytesIO(content),
        filename=filename,
        content_type="application/octet-stream",
    )


def _metadata():
    return {
        "curriculum": "vocational",
        "publisher": "longteng",
        "grade": 10,
        "volume": "數學B1",
    }


class TestBaseNameAndClassification:
    def test_get_base_name(self):
        assert get_base_name("1-1 角度的基本性質-課本.docx") == "1-1 角度的基本性質-課本"

    def test_classify_section_format_a(self):
        result = classify_textbook_source("1-1 角度的基本性質-課本")
        assert result == {"type": "section", "chapter": 1, "section": 1}

    def test_classify_section_format_b(self):
        result = classify_textbook_source("第一章 1-1 角度的基本性質-課本")
        assert result == {"type": "section", "chapter": 1, "section": 1}

    def test_classify_section_format_b_1_4(self):
        result = classify_textbook_source("第一章 1-4 正弦、餘弦函數的圖形-課本")
        assert result == {"type": "section", "chapter": 1, "section": 4}

    def test_classify_section_format_c_chapter_3(self):
        result = classify_textbook_source("第三章 3-1 向量的作圖-課本")
        assert result == {"type": "section", "chapter": 3, "section": 1}

    def test_classify_section_format_c_chapter_3_section_3(self):
        result = classify_textbook_source("第三章 3-3 向量的內積-課本")
        assert result == {"type": "section", "chapter": 3, "section": 3}

    def test_classify_chapter_assessment_chapter_1(self):
        result = classify_textbook_source("第一章 自我評量-課本")
        assert result == {"type": "chapter_assessment", "chapter": 1, "section": None}

    def test_classify_chapter_assessment_chapter_3(self):
        result = classify_textbook_source("第三章 自我評量-課本")
        assert result == {"type": "chapter_assessment", "chapter": 3, "section": None}

    def test_classify_chapter_mismatch(self):
        result = classify_textbook_source("第一章 2-1 銳角三角函數-課本")
        assert result["type"] == "chapter_mismatch"
        assert result["label_chapter"] == 1
        assert result["section_chapter"] == 2
        assert result["section_number"] == 1

    def test_classify_unknown(self):
        result = classify_textbook_source("隨機教材名稱-課本")
        assert result == {"type": "unknown", "chapter": None, "section": None}

    def test_validate_rejects_chapter_mismatch(self):
        payload, status = validate_textbook_source_batch(
            docx_files=[_make_file("第一章 2-1 銳角三角函數-課本.docx")],
            pdf_files=[_make_file("第一章 2-1 銳角三角函數-課本.pdf")],
            **_metadata(),
        )
        assert status == 400
        assert payload["error"] == "chapter_metadata_mismatch"
        assert payload["mismatches"][0]["base_name"] == "第一章 2-1 銳角三角函數-課本"


class TestSourcePairValidation:
    def test_case_a_single_pair_success(self):
        payload, status = validate_textbook_source_batch(
            docx_files=[_make_file("1-1 角度的基本性質-課本.docx")],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf")],
            **_metadata(),
        )
        assert status == 200
        assert payload["ok"] is True
        assert payload["batch"]["total_pairs"] == 1
        assert payload["pairs"][0]["base_name"] == "1-1 角度的基本性質-課本"
        assert payload["pairs"][0]["status"] == "ready"

    def test_case_b_four_pairs_sorted(self):
        docx = [
            _make_file("1-3 三角函數-課本.docx"),
            _make_file("1-1 角度的基本性質-課本.docx"),
            _make_file("1-2 三角比-課本.docx"),
            _make_file("第一章 自我評量-課本.docx"),
        ]
        pdf = [
            _make_file("1-2 三角比-課本.pdf"),
            _make_file("第一章 自我評量-課本.pdf"),
            _make_file("1-1 角度的基本性質-課本.pdf"),
            _make_file("1-3 三角函數-課本.pdf"),
        ]
        payload, status = validate_textbook_source_batch(
            docx_files=docx,
            pdf_files=pdf,
            **_metadata(),
        )
        assert status == 200
        assert payload["batch"]["total_pairs"] == 4
        assert [p["base_name"] for p in payload["pairs"]] == [
            "1-1 角度的基本性質-課本",
            "1-2 三角比-課本",
            "1-3 三角函數-課本",
            "第一章 自我評量-課本",
        ]
        assert payload["pairs"][-1]["type"] == "chapter_assessment"

    def test_case_c_missing_pdf(self):
        payload, status = validate_textbook_source_batch(
            docx_files=[
                _make_file("1-1 角度的基本性質-課本.docx"),
                _make_file("1-3 三角函數-課本.docx"),
            ],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf")],
            **_metadata(),
        )
        assert status == 400
        assert payload["ok"] is False
        assert payload["error"] == "source_pair_validation_failed"
        assert "1-3 三角函數-課本" in payload["missing_pdf"]

    def test_case_d_basename_mismatch(self):
        payload, status = validate_textbook_source_batch(
            docx_files=[_make_file("1-1 角度的基本性質-課本.docx")],
            pdf_files=[_make_file("1-2 三角比-課本.pdf")],
            **_metadata(),
        )
        assert status == 400
        assert payload["error"] == "source_pair_validation_failed"
        assert payload["missing_pdf"] == ["1-1 角度的基本性質-課本"]
        assert payload["missing_docx"] == ["1-2 三角比-課本"]

    def test_case_e_duplicate_docx_basename(self):
        payload, status = validate_textbook_source_batch(
            docx_files=[
                _make_file("1-1 角度的基本性質-課本.docx"),
                _make_file("1-1 角度的基本性質-課本.docx"),
            ],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf")],
            **_metadata(),
        )
        assert status == 400
        assert payload["error"] == "duplicate_docx_basename"
        assert payload["basenames"] == ["1-1 角度的基本性質-課本"]

    def test_case_f_chapter_assessment(self):
        payload, status = validate_textbook_source_batch(
            docx_files=[_make_file("第一章 自我評量-課本.docx")],
            pdf_files=[_make_file("第一章 自我評量-課本.pdf")],
            **_metadata(),
        )
        assert status == 200
        assert payload["pairs"][0]["type"] == "chapter_assessment"
        assert payload["pairs"][0]["chapter"] == 1

    def test_case_g_unknown_still_success(self):
        payload, status = validate_textbook_source_batch(
            docx_files=[_make_file("隨機教材名稱-課本.docx")],
            pdf_files=[_make_file("隨機教材名稱-課本.pdf")],
            **_metadata(),
        )
        assert status == 200
        assert payload["pairs"][0]["type"] == "unknown"
        assert payload["pairs"][0]["status"] == "ready"

    def test_missing_docx_collection(self):
        payload, status = validate_textbook_source_batch(
            docx_files=[],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf")],
            **_metadata(),
        )
        assert status == 400
        assert payload["error"] == "missing_docx_collection"

    def test_invalid_pdf_extension(self):
        payload, status = validate_textbook_source_batch(
            docx_files=[_make_file("1-1 角度的基本性質-課本.docx")],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.doc")],
            **_metadata(),
        )
        assert status == 400
        assert payload["error"] == "invalid_pdf_extension"

    def test_missing_required_metadata(self):
        payload, status = validate_textbook_source_batch(
            docx_files=[_make_file("1-1 角度的基本性質-課本.docx")],
            pdf_files=[_make_file("1-1 角度的基本性質-課本.pdf")],
            curriculum="",
            publisher="longteng",
            grade=10,
            volume="數學B1",
        )
        assert status == 400
        assert payload["error"] == "missing_required_metadata"


class TestBuildHelpers:
    def test_build_file_map_duplicate_pdf(self):
        file_map, error = build_file_map(
            [
                _make_file("1-1 角度的基本性質-課本.pdf"),
                _make_file("1-1 角度的基本性質-課本.pdf"),
            ],
            ".pdf",
        )
        assert file_map == {}
        assert error["error"] == "duplicate_pdf_basename"

    def test_build_source_pairs_union(self):
        docx_map, _ = build_file_map([_make_file("1-1 角度的基本性質-課本.docx")], ".docx")
        pdf_map, _ = build_file_map(
            [
                _make_file("1-1 角度的基本性質-課本.pdf"),
                _make_file("1-2 三角比-課本.pdf"),
            ],
            ".pdf",
        )
        pairs = build_source_pairs(docx_map, pdf_map)
        assert len(pairs) == 2
        statuses = {p["base_name"]: p["status"] for p in pairs}
        assert statuses["1-1 角度的基本性質-課本"] == "ready"
        assert statuses["1-2 三角比-課本"] == "missing_docx"

    def test_sort_source_pairs(self):
        pairs = [
            {"base_name": "第一章 自我評量-課本", "classification": classify_textbook_source("第一章 自我評量-課本")},
            {"base_name": "1-2 三角比-課本", "classification": classify_textbook_source("1-2 三角比-課本")},
            {"base_name": "1-1 角度的基本性質-課本", "classification": classify_textbook_source("1-1 角度的基本性質-課本")},
        ]
        sorted_pairs = sort_source_pairs(pairs)
        assert [p["base_name"] for p in sorted_pairs] == [
            "1-1 角度的基本性質-課本",
            "1-2 三角比-課本",
            "第一章 自我評量-課本",
        ]
