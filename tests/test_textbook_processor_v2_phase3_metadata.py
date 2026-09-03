# -*- coding: utf-8 -*-
"""Unit tests for Phase2/Phase3 metadata fixes (neutral example, auth coords, exercise concept)."""

from core.textbook_processor_v2 import (
    _JSON_EXAMPLE_METADATA_ONLY,
    _build_anchor_blocks_v2,
    _build_metadata_alignment_prompt,
    _force_phase3_authoritative_chapter_section,
    _phase3_authoritative_source_context,
)


def test_phase3_json_example_is_schema_neutral():
    ex = _JSON_EXAMPLE_METADATA_ONLY
    assert "坐標系與函數圖形" not in ex
    assert "數列與級數" not in ex
    assert "三角函數" not in ex
    assert "一元二次不等式" not in ex
    assert "<chapter_title>" in ex
    assert "<section_title>" in ex
    assert "<canonical_title>" in ex


def test_phase3_prompt_includes_authoritative_source_context():
    info = {
        "curriculum": "vocational",
        "volume": "數學B2",
        "chapter": "1 三角函數",
        "chapter_index": 1,
        "section_code": "1-1",
        "section": "1-1 角度的基本性質",
    }
    prompt = _build_metadata_alignment_prompt(["例1", "1-1習題 基礎題 1"], info)
    assert "curriculum=vocational" in prompt
    assert "volume=數學B2" in prompt
    assert "chapter=1" in prompt
    assert "chapter_title=三角函數" in prompt
    assert "section=1-1" in prompt
    assert "section_title=角度的基本性質" in prompt
    assert "不得自行建立其他章節名稱" in prompt
    assert "坐標系與函數圖形" not in prompt
    assert "數列與級數" not in prompt
    # Authoritative chapter name appears as context, not as polluted example semantics alone.
    assert "<chapter_title>" in prompt


def test_phase3_authoritative_context_parse():
    auth = _phase3_authoritative_source_context(
        {
            "curriculum": "vocational",
            "volume": "數學B2",
            "chapter": "1 三角函數",
            "chapter_index": 1,
            "section_code": "1-1",
            "section": "1-1 角度的基本性質",
        }
    )
    assert auth["chapter"] == "1"
    assert auth["chapter_title_name"] == "三角函數"
    assert auth["chapter_title"] == "1 三角函數"
    assert auth["section"] == "1-1"
    assert auth["section_title"] == "角度的基本性質"


def test_force_phase3_overwrites_invented_chapters():
    polluted = {
        "chapters": [
            {
                "chapter_title": "1 數列與級數",
                "sections": [
                    {
                        "section_title": "1-1 數列",
                        "concepts": [
                            {
                                "concept_name": "X",
                                "examples": [],
                                "practice_questions": [
                                    {"title": "1-1習題 基礎題 1", "source_description": "1-1習題 基礎題 1"}
                                ],
                            }
                        ],
                    }
                ],
            },
            {
                "chapter_title": "1 坐標系與函數圖形",
                "sections": [
                    {
                        "section_title": "1-1 直角坐標系",
                        "concepts": [
                            {
                                "concept_name": "Y",
                                "examples": [{"title": "例1", "source_description": "例1"}],
                                "practice_questions": [],
                            }
                        ],
                    }
                ],
            },
        ]
    }
    info = {
        "curriculum": "vocational",
        "volume": "數學B2",
        "chapter": "1 三角函數",
        "section_code": "1-1",
        "section": "1-1 角度的基本性質",
    }
    fixed = _force_phase3_authoritative_chapter_section(polluted, info)
    assert len(fixed["chapters"]) == 1
    assert fixed["chapters"][0]["chapter_title"] == "1 三角函數"
    sec = fixed["chapters"][0]["sections"][0]
    assert sec["section_code"] == "1-1"
    assert sec["section_title"] == "角度的基本性質"
    titles = []
    for con in sec["concepts"]:
        for item in (con.get("examples") or []) + (con.get("practice_questions") or []):
            titles.append(item.get("title"))
    assert "例1" in titles
    assert "1-1習題 基礎題 1" in titles
    blob = str(fixed)
    assert "數列與級數" not in blob
    assert "坐標系與函數圖形" not in blob


def test_section_exercises_do_not_inherit_active_concept(monkeypatch):
    def _fake_resolve(*, concept_name, **_k):
        return {
            "concept_name": concept_name,
            "concept_en_id": "CoterminalAngles",
            "formal_skill_id": "vh_數學B2_CoterminalAngles",
        }

    monkeypatch.setattr("core.textbook_processor_v2._resolve_formal_concept_en_id_v2", _fake_resolve)
    monkeypatch.setattr(
        "core.textbook_processor_v2._persist_formal_skill_from_docx_heading",
        lambda **_k: None,
    )
    monkeypatch.setattr(
        "core.textbook_processor_v2._find_existing_skill_id_by_section_and_ch_name",
        lambda **_k: "",
    )

    lines = [
        "1-1.4 同界角",
        "例3",
        "下列何者與50度互為同界角？",
        "解",
        "詳解內容",
        "1-1 習題",
        "基礎題",
        "1 請完成度與弧度對照表",
        "2 將下列各角化成弧度",
        "進階題",
        "9 進階綜合題",
    ]
    _, meta = _build_anchor_blocks_v2(
        lines,
        section_code="1-1",
        section_title="1-1 角度的基本性質",
        curriculum_info={
            "curriculum": "vocational",
            "volume": "數學B2",
            "source_scope": "section_textbook",
            "chapter": "1 三角函數",
        },
    )
    assert meta.get("例3", {}).get("concept_name") == "同界角"
    assert meta.get("例3", {}).get("formal_skill_id") == "vh_數學B2_CoterminalAngles"

    ex1 = meta.get("1-1習題 基礎題 1") or {}
    ex2 = meta.get("1-1習題 基礎題 2") or {}
    adv = meta.get("1-1習題 進階題 9") or {}
    assert ex1.get("source_type") == "textbook_exercise"
    assert not ex1.get("concept_name")
    assert not ex1.get("concept_code")
    assert not ex1.get("concept_en_id")
    assert not ex1.get("formal_skill_id")
    assert not ex2.get("concept_name")
    assert adv.get("source_type") == "advanced_exercise"
    assert not adv.get("concept_name")
    assert not adv.get("formal_skill_id")
