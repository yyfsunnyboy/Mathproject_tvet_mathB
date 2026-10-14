from __future__ import annotations

import copy
import hashlib

from core.textbook_b2_12 import (
    PDF_VISUAL_REGIONS,
    SOURCE_STEM,
    correct_pdf_visual_regions,
    is_b2_12,
)


def _info():
    return {
        "curriculum": "vocational",
        "volume": "數學B2",
        "section_code": "1-2",
        "source_scope": "section_textbook",
        "parse_filename": SOURCE_STEM + ".docx",
    }


def test_b2_12_profile_is_exact_source_only():
    assert is_b2_12(_info())
    for change in (
        {"section_code": "1-1"},
        {"section_code": "1-3"},
        {"volume": "數學B1"},
        {"parse_filename": "another.docx"},
    ):
        assert not is_b2_12({**_info(), **change})


def test_reviewed_visual_regions_include_five_questions_and_two_page_example6(
    tmp_path, monkeypatch
):
    fake_pdf = tmp_path / "source.pdf"
    fake_pdf.write_bytes(b"audited-edition")
    monkeypatch.setattr(
        "core.textbook_b2_12.B2_12_PDF_SHA256",
        hashlib.sha256(fake_pdf.read_bytes()).hexdigest(),
    )
    rows = [
        {"source_description": label, "match_score": 0.0}
        for label in (*PDF_VISUAL_REGIONS, "隨堂練習3")
    ]
    pages = [{"width": 609.45, "height": 793.70} for _ in range(12)]
    corrected = correct_pdf_visual_regions(copy.deepcopy(rows), pages, fake_pdf, _info())
    changed = [row for row in corrected if row.get("match_method")]
    assert len(changed) == 5
    assert all(row["should_mount"] and row["match_score"] == 1.0 for row in changed)
    example6 = next(row for row in changed if row["source_description"] == "例6")
    assert [crop["page"] for crop in example6["visual_crops"]] == [11, 12]
    assert len(example6["visual_crops"]) == 2
    unchanged = next(row for row in corrected if row["source_description"] == "隨堂練習3")
    assert unchanged == {"source_description": "隨堂練習3", "match_score": 0.0}


def test_wrong_pdf_hash_does_not_apply_regions(tmp_path):
    fake_pdf = tmp_path / "wrong.pdf"
    fake_pdf.write_bytes(b"wrong")
    rows = [{"source_description": "例2", "match_score": 0.0}]
    pages = [{"width": 609.45, "height": 793.70} for _ in range(12)]
    assert correct_pdf_visual_regions(copy.deepcopy(rows), pages, fake_pdf, _info()) == rows
