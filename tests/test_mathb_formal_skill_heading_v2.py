# -*- coding: utf-8 -*-
"""Math B formal skill：DOCX concept heading 為中文來源，AI 僅產 en_id。"""

from unittest.mock import MagicMock

import pytest

from core.textbook_processor_v2 import (
    CONCEPT_HEADING_RE,
    _ai_generate_formal_skill_en_id_v2,
    _fallback_en_id_from_concept_code,
    _is_docx_concept_heading_code,
    _make_unique_formal_skill_id_v2,
    _parse_mathb_concept_line,
    _resolve_formal_concept_en_id_v2,
)


def test_concept_heading_re_matches_section_subskills():
    m = CONCEPT_HEADING_RE.match("1-1.1 數線")
    assert m
    assert m.group(1) == "1-1.1"
    assert m.group(2) == "數線"
    assert CONCEPT_HEADING_RE.match("1-1.4 絕對值不等式的展開與幾何意義").group(2) == (
        "絕對值不等式的展開與幾何意義"
    )


def test_parse_mathb_concept_line_returns_chinese_from_heading():
    parsed = _parse_mathb_concept_line("1-1.2 絕對值", section_code="1-1")
    assert parsed == ("1-1.2", "絕對值", True)


def test_parse_mathb_concept_line_register_only_not_formal():
    assert _parse_mathb_concept_line("絕對值方程式", section_code="1-1") is None


def test_is_docx_concept_heading_code():
    assert _is_docx_concept_heading_code("1-1.1")
    assert not _is_docx_concept_heading_code("1-1")


def test_fallback_en_id_avoids_concept_hash():
    en = _fallback_en_id_from_concept_code("1-1.3")
    assert en == "SubSection_1_1_3"
    assert "Concept_" not in en or en.startswith("SubSection_")


def test_ai_generate_ignores_ai_concept_name(monkeypatch):
    class _Model:
        pass

    def _fake_call(_model, _prompt, **_kw):
        return '{"concept_name": "距離公式", "concept_en_id": "DistanceBetweenTwoPoints", "reason": "ok"}'

    monkeypatch.setattr("core.textbook_processor_v2.get_model", lambda _role: _Model())
    monkeypatch.setattr("core.textbook_processor_v2._call_gemini_with_retry", _fake_call)
    monkeypatch.setattr(
        "core.textbook_processor_v2.safe_load_gemini_json",
        lambda raw: __import__("json").loads(raw),
    )
    en = _ai_generate_formal_skill_en_id_v2(concept_name="平面上兩點間的距離")
    assert en == "DistanceBetweenTwoPoints"


def test_make_unique_reuses_same_chinese(monkeypatch):
    class _Row:
        skill_ch_name = "數線"

    monkeypatch.setattr(
        "core.textbook_processor_v2.db.session.get",
        lambda _cls, sid: _Row() if sid == "vh_數學B1_NumberLine" else None,
    )
    monkeypatch.setattr(
        "core.textbook_processor_v2._list_mathb_volume_formal_skill_ids",
        lambda *_a, **_k: [],
    )
    info = {"curriculum": "vocational", "volume": "數學B1", "grade": 10}
    sid, en = _make_unique_formal_skill_id_v2(
        subject="B",
        vol_num=1,
        preferred_en_id="NumberLine",
        concept_name="數線",
        concept_code="1-1.1",
        curriculum_info=info,
    )
    assert sid == "vh_數學B1_NumberLine"
    assert en == "NumberLine"


def test_resolve_formal_concept_keeps_docx_chinese(monkeypatch):
    monkeypatch.setattr(
        "core.textbook_processor_v2._ai_generate_formal_skill_en_id_v2",
        lambda **_: "AbsoluteValue",
    )
    monkeypatch.setattr(
        "core.textbook_processor_v2._list_mathb_volume_formal_skill_ids",
        lambda *_a, **_k: [],
    )
    monkeypatch.setattr("core.textbook_processor_v2.db.session.get", lambda *_a, **_k: None)
    info = {"curriculum": "vocational", "volume": "數學B1", "grade": 10}
    out = _resolve_formal_concept_en_id_v2(
        concept_name="絕對值",
        concept_code="1-1.2",
        curriculum_info=info,
    )
    assert out["concept_name"] == "絕對值"
    assert out["formal_skill_id"] == "vh_數學B1_AbsoluteValue"
    assert out["concept_en_id"] == "AbsoluteValue"
