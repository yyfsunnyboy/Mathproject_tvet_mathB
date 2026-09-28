# -*- coding: utf-8 -*-
"""Curriculum binding stays independent of missing structural concept headings."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

from core.mathb_concept_heading import section_identities_match
from core.textbook_importer_v3_docx import extract_docx_skill_headings
from core.textbook_importer_v3_pipeline import (
    STRUCTURAL_SKILL_NONE,
    STRUCTURAL_SKILL_NUMBERED_FOUND,
    STRUCTURAL_SKILL_PLAIN_FOUND,
    STRUCTURAL_SKILL_UNRESOLVED,
    resolve_v3_curriculum_binding,
)

ROOT = Path(__file__).resolve().parents[1]
B3 = ROOT / "textbook_import" / "source" / "vocational" / "math_B3"
B2 = ROOT / "textbook_import" / "source" / "vocational" / "math_B2"


def _original_docx(folder: Path, fragment: str) -> Path:
    hits = [
        path
        for path in folder.glob("*.docx")
        if fragment in path.name and not path.name.endswith("_Latex.docx")
    ]
    assert len(hits) == 1, [path.name for path in hits]
    return hits[0]


def _styles_named(path: Path, style_name: str) -> list[str]:
    doc = Document(str(path))
    texts = []
    for element in doc.element.body.iter(qn("w:p")):
        paragraph = Paragraph(element, doc)
        text = paragraph.text.strip()
        if text and paragraph.style is not None and paragraph.style.name == style_name:
            texts.append(text)
    return texts


def _bind(audit: dict, **overrides):
    heading = audit.get("section_heading")
    payload = dict(
        section_heading=heading,
        same_section=True,
        candidate_count=int(audit.get("candidate_count") or 0),
        unresolved_heading_count=int(audit.get("unresolved_heading_count") or 0),
        plain_source_heading_count=int(audit.get("plain_source_heading_count") or 0),
        plain_source_sequence_ok=audit.get("plain_source_sequence_ok"),
        outline_action="existing",
        chapter="第3章 二元一次不等式及其應用",
        section="3-2 二元一次不等式",
        section_code="3-2",
    )
    payload.update(overrides)
    return resolve_v3_curriculum_binding(**payload)


def test_b3_3_2_plain_source_headings_are_not_printed_codes():
    path = _original_docx(B3, "3-2")
    audit = extract_docx_skill_headings(str(path), section_code="3-2", volume="數學B3")
    heading = audit["section_heading"]
    assert heading["source_heading_text"] == "3-2二元一次不等式"
    assert audit["candidate_count"] == 0
    assert audit["skill_candidates"] == []
    assert audit["unresolved_heading_count"] == 0
    assert _styles_named(path, "01-1-1.1") == []
    names = [item["concept_name"] for item in audit["plain_source_headings"]]
    assert names == [
        "二元一次不等式的定義",
        "二元一次不等式的解",
        "邊界、半平面",
        "相異兩點在直線的同側、異側",
    ]
    assert [item["internal_coordinate"] for item in audit["plain_source_headings"]] == [
        "3-2#1", "3-2#2", "3-2#3", "3-2#4",
    ]
    assert [item["formal_skill_id"] for item in audit["plain_source_headings"]] == [
        "vh_數學B3_PlainHeading_3_2_1",
        "vh_數學B3_PlainHeading_3_2_2",
        "vh_數學B3_PlainHeading_3_2_3",
        "vh_數學B3_PlainHeading_3_2_4",
    ]
    assert all(item["printed_concept_code"] is None for item in audit["plain_source_headings"])
    assert all(item["authority_source"] == "source_authored_plain_heading" for item in audit["plain_source_headings"])
    assert section_identities_match(heading, "3-2 二元一次不等式", expected_section_code="3-2")
    decision = _bind(audit)
    assert decision["curriculum_binding"] == "PASS"
    assert decision["structural_skill_status"] == STRUCTURAL_SKILL_PLAIN_FOUND


def test_zero_candidates_fail_when_section_does_not_match():
    audit = extract_docx_skill_headings(str(_original_docx(B3, "3-2")), section_code="3-2")
    decision = _bind(audit, same_section=False)
    assert decision["curriculum_binding"] == "FAIL"
    assert decision["structural_skill_status"] == STRUCTURAL_SKILL_PLAIN_FOUND


def test_zero_candidates_fail_on_outline_conflict():
    audit = extract_docx_skill_headings(str(_original_docx(B3, "3-2")), section_code="3-2")
    decision = _bind(audit, outline_action="conflict")
    assert decision["curriculum_binding"] == "FAIL"
    assert decision["structural_skill_status"] == STRUCTURAL_SKILL_PLAIN_FOUND


def test_zero_candidates_fail_when_headings_are_unresolved():
    audit = extract_docx_skill_headings(str(_original_docx(B3, "3-2")), section_code="3-2")
    decision = _bind(audit, unresolved_heading_count=1)
    assert decision["curriculum_binding"] == "FAIL"
    assert decision["structural_skill_status"] == STRUCTURAL_SKILL_UNRESOLVED


def test_missing_section_heading_is_not_released_by_zero_candidates():
    decision = resolve_v3_curriculum_binding(
        section_heading=None,
        same_section=False,
        candidate_count=0,
        unresolved_heading_count=0,
        outline_action="existing",
        chapter="第3章 二元一次不等式及其應用",
        section="3-2 二元一次不等式",
        section_code="3-2",
    )
    assert decision["curriculum_binding"] == "FAIL"
    assert decision["structural_skill_status"] == STRUCTURAL_SKILL_NONE


def test_incomplete_chapter_authority_fails_with_zero_candidates():
    audit = extract_docx_skill_headings(str(_original_docx(B3, "3-2")), section_code="3-2")
    decision = _bind(audit, chapter="", section="", section_code="")
    assert decision["curriculum_binding"] == "FAIL"


def test_known_good_b3_sections_still_find_structural_skills():
    expected = {
        "1-1": ["1-1.1", "1-1.2", "1-1.3", "1-1.4", "1-1.5"],
        "2-1": ["2-1.1", "2-1.2"],
    }
    for code, concepts in expected.items():
        audit = extract_docx_skill_headings(str(_original_docx(B3, code)), section_code=code)
        assert [item["concept_code"] for item in audit["skill_candidates"]] == concepts
        assert {item["style"] for item in audit["skill_candidates"]} == {"01-1-1.1"}
        assert audit["unresolved_heading_count"] == 0
        decision = _bind(
            audit,
            chapter="第1章" if code.startswith("1-") else "第2章",
            section=audit["section_heading"]["source_heading_text"],
            section_code=code,
        )
        assert decision["curriculum_binding"] == "PASS"
        assert decision["structural_skill_status"] == STRUCTURAL_SKILL_NUMBERED_FOUND
        assert audit["plain_source_heading_count"] == 0


def test_b2_structural_extraction_unchanged():
    audit = extract_docx_skill_headings(str(_original_docx(B2, "4-2")), section_code="4-2")
    assert [item["concept_code"] for item in audit["skill_candidates"]] == [
        "4-2.1",
        "4-2.2",
        "4-2.3",
        "4-2.4",
    ]
    assert audit["unresolved_heading_count"] == 0
    decision = _bind(
        audit,
        chapter="第4章",
        section=audit["section_heading"]["source_heading_text"],
        section_code="4-2",
    )
    assert decision["curriculum_binding"] == "PASS"
    assert decision["structural_skill_status"] == STRUCTURAL_SKILL_NUMBERED_FOUND
    assert audit["plain_source_heading_count"] == 0
