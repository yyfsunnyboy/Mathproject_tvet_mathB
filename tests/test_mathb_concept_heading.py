# -*- coding: utf-8 -*-
"""ConceptHeadingDetector 通用概念標題測試。"""

from unittest.mock import MagicMock

import pytest

from core.mathb_concept_heading import detect_mathb_concept_heading, is_persistable_concept_code
from core.textbook_processor_v2 import (
    _build_anchor_blocks_v2,
    _parse_mathb_concept_line,
)


def test_numbered_compact_heading():
    hit = detect_mathb_concept_heading(
        "3-2.1除法原理",
        current_section_code="3-2",
        next_lines=["被除式=除式×商式+餘式", "例1", "已知"],
        current_source_scope="section_textbook",
    )
    assert hit is not None
    assert hit["concept_name"] == "除法原理"
    assert hit["concept_code"] == "3-2.1"
    assert hit["section_code"] == "3-2"
    assert hit["heading_kind"] == "numbered_compact"


def test_numbered_spaced_heading():
    hit = detect_mathb_concept_heading(
        "2-1.2 兩平行線的性質",
        current_section_code="2-1",
        next_lines=["平行線斜率相同", "例3"],
        current_source_scope="section_textbook",
    )
    assert hit is not None
    assert hit["concept_name"] == "兩平行線的性質"
    assert hit["heading_kind"] == "numbered_spaced"


def test_plain_scoped_heading():
    hit = detect_mathb_concept_heading(
        "除法原理",
        current_section_code="3-2",
        next_lines=["被除式=除式×商式+餘式", "例1"],
        current_source_scope="section_textbook",
    )
    assert hit is not None
    assert hit["heading_kind"] == "plain_scoped"
    assert hit["concept_code"] == "3-2::除法原理"
    assert is_persistable_concept_code(hit["concept_code"])


def test_duplicate_merge_plain_after_numbered():
    first = detect_mathb_concept_heading(
        "3-2.1除法原理",
        current_section_code="3-2",
        next_lines=["定義說明"],
        current_source_scope="section_textbook",
    )
    assert first and not first.get("duplicate_merge")
    second = detect_mathb_concept_heading(
        "除法原理",
        current_section_code="3-2",
        next_lines=["例1"],
        current_source_scope="section_textbook",
        current_concept_name="除法原理",
    )
    assert second is not None
    assert second.get("duplicate_merge") is True


@pytest.mark.parametrize(
    "line",
    [
        "例1",
        "隨堂練習",
        "3-2習題",
        "基礎題",
        "進階題",
        "題目",
        "KEY",
        "▲圖1",
        "160",
        "已知 f(x) 除以 g(x) 的餘式",
    ],
)
def test_excluded_lines_not_concept_heading(line):
    assert (
        detect_mathb_concept_heading(
            line,
            current_section_code="3-2",
            next_lines=["例1", "設"],
            current_source_scope="section_textbook",
        )
        is None
    )


def test_build_anchor_compact_and_plain_merge(monkeypatch):
    monkeypatch.setattr(
        "core.textbook_processor_v2._resolve_formal_concept_en_id_v2",
        lambda **_k: {
            "concept_name": "除法原理",
            "concept_en_id": "DivisionPrinciple",
            "formal_skill_id": "vh_數學B3_DivisionPrinciple",
        },
    )
    persisted: list[str] = []

    def _capture_persist(**kwargs):
        persisted.append(str(kwargs.get("concept_name")))

    monkeypatch.setattr(
        "core.textbook_processor_v2._persist_formal_skill_from_docx_heading",
        _capture_persist,
    )
    lines = [
        "3-2.1除法原理",
        "被除式=除式×商式+餘式",
        "除法原理",
        "例1",
        "題幹內容",
        "解",
        "詳解",
    ]
    _, meta = _build_anchor_blocks_v2(
        lines,
        section_code="3-2",
        curriculum_info={
            "curriculum": "vocational",
            "volume": "數學B3",
            "source_scope": "section_textbook",
        },
    )
    assert meta
    ex_meta = meta.get("例1") or next((v for k, v in meta.items() if k.startswith("例")), {})
    assert ex_meta.get("section_code") == "3-2"
    assert ex_meta.get("concept_name") == "除法原理"
    assert ex_meta.get("formal_skill_id")
    assert persisted.count("除法原理") == 1


def test_full_section_32_three_concepts(monkeypatch):
    en_map = {
        "除法原理": ("DivisionPrinciple", "vh_數學B3_DivisionPrinciple"),
        "餘式定理": ("RemainderTheorem", "vh_數學B3_RemainderTheorem"),
        "因式定理": ("FactorTheorem", "vh_數學B3_FactorTheorem"),
    }

    def _fake_resolve(*, concept_name, **_k):
        en, sid = en_map.get(concept_name, ("X", "vh_數學B3_X"))
        return {"concept_name": concept_name, "concept_en_id": en, "formal_skill_id": sid}

    monkeypatch.setattr("core.textbook_processor_v2._resolve_formal_concept_en_id_v2", _fake_resolve)
    monkeypatch.setattr(
        "core.textbook_processor_v2._persist_formal_skill_from_docx_heading",
        lambda **_k: None,
    )
    lines = [
        "3-2.1除法原理",
        "例1",
        "題1",
        "3-2.2 餘式定理",
        "例3",
        "題3",
        "3-2.3因式定理",
        "例10",
        "題10",
    ]
    _, meta = _build_anchor_blocks_v2(
        lines,
        section_code="3-2",
        curriculum_info={"volume": "數學B3", "source_scope": "section_textbook"},
    )
    names = {m.get("concept_name") for m in meta.values() if m.get("concept_name")}
    assert "除法原理" in names
    assert "餘式定理" in names
    assert "因式定理" in names
    assert meta.get("例1", {}).get("concept_name") == "除法原理"
    assert meta.get("例3", {}).get("concept_name") == "餘式定理"
    assert meta.get("例10", {}).get("concept_name") == "因式定理"
