# -*- coding: utf-8 -*-
"""Tests for authoritative section outline_* ensure helper."""

from __future__ import annotations

import pytest

from core.textbook_section_outline import (
    AUTHORITATIVE_OUTLINE_SOURCES,
    build_outline_skill_id_for_section,
    ensure_section_outline_from_authoritative_metadata_v2,
    outline_display_order_from_section_code,
)


def test_outline_id_normalization_matches_b1_rule():
    sid, code, title = build_outline_skill_id_for_section(
        curriculum="vocational",
        volume="數學B2",
        section_code="1-1",
        section="角度的基本性質",
    )
    assert code == "1-1"
    assert title == "1-1 角度的基本性質"
    assert sid == "outline_vocational_數學B2_11"

    sid12, _, _ = build_outline_skill_id_for_section(
        curriculum="vocational",
        volume="數學B1",
        section="1-2 平面坐標系與線型函數",
    )
    assert sid12 == "outline_vocational_數學B1_12"

    sid21, _, _ = build_outline_skill_id_for_section(
        curriculum="vocational",
        volume="數學B1",
        section_code="2-1",
        section="斜率",
    )
    assert sid21 == "outline_vocational_數學B1_21"

    assert outline_display_order_from_section_code("1-1") == 11
    assert outline_display_order_from_section_code("2-3") == 23


def test_dry_run_would_create_for_missing_b2_11():
    from app import app

    with app.app_context():
        result = ensure_section_outline_from_authoritative_metadata_v2(
            curriculum="vocational",
            volume="數學B2",
            chapter="1 三角函數",
            section="1-1 角度的基本性質",
            section_code="1-1",
            grade=11,
            authority_source="curriculum_info",
            dry_run=True,
        )
        assert result["action"] in ("would_create", "existing")
        assert result["skill_id"] == "outline_vocational_數學B2_11"
        assert result["wrote"] is False
        # Before intentional commit in this round, expect would_create.
        # If a prior run already created it, existing is also acceptable for CI re-runs.
        if result["action"] == "would_create":
            assert result["incoming"]["section"] == "1-1 角度的基本性質"


def test_non_authoritative_metadata_rejected():
    result = ensure_section_outline_from_authoritative_metadata_v2(
        curriculum="vocational",
        volume="數學B2",
        chapter="1 三角函數",
        section="1-1 角度的基本性質",
        authority_source="phase3_gemini",
        dry_run=True,
    )
    assert result["action"] == "invalid_authority"
    assert result["reason"] == "non_authoritative_source"
    assert "phase3_gemini" not in AUTHORITATIVE_OUTLINE_SOURCES

    result2 = ensure_section_outline_from_authoritative_metadata_v2(
        curriculum="vocational",
        volume="數學B2",
        chapter="<chapter_title>",
        section="1-1 角度的基本性質",
        authority_source="curriculum_info",
        dry_run=True,
    )
    assert result2["action"] == "invalid_authority"


def test_create_existing_conflict_and_no_textbook_example():
    from sqlalchemy import delete

    from app import app
    from models import SkillCurriculum, SkillInfo, TextbookExample, db

    test_section = "99-99 單元測試錨點"
    skill_id = "outline_vocational_數學B2_9999"

    def _purge_test_outline() -> None:
        # Avoid ORM cascade lazy-load on SkillGenCodePrompt (schema drift safe).
        db.session.execute(delete(SkillCurriculum).where(SkillCurriculum.skill_id == skill_id))
        db.session.execute(delete(SkillInfo).where(SkillInfo.skill_id == skill_id))
        db.session.commit()

    with app.app_context():
        _purge_test_outline()

        te_before = TextbookExample.query.count()
        b1_outline_before = SkillCurriculum.query.filter(
            SkillCurriculum.skill_id.like("outline_vocational_數學B1_%")
        ).count()

        created = ensure_section_outline_from_authoritative_metadata_v2(
            curriculum="vocational",
            volume="數學B2",
            chapter="99 測試章",
            section=test_section,
            section_code="99-99",
            grade=11,
            authority_source="form_confirmed",
            dry_run=False,
            flush=True,
        )
        assert created["action"] == "created"
        assert created["skill_id"] == skill_id
        assert created["skill_curriculum_created"] is True
        db.session.commit()

        si = db.session.get(SkillInfo, skill_id)
        assert si is not None
        assert si.category == "outline"
        assert si.is_active is False
        assert si.skill_en_name == skill_id
        assert si.gemini_prompt == ""
        assert si.order_index == 9999

        sc = SkillCurriculum.query.filter_by(skill_id=skill_id).one()
        assert sc.paragraph is None
        assert sc.section == test_section
        assert sc.chapter == "99 測試章"
        assert sc.display_order == 9999

        again = ensure_section_outline_from_authoritative_metadata_v2(
            curriculum="vocational",
            volume="數學B2",
            chapter="99 測試章",
            section=test_section,
            section_code="99-99",
            grade=11,
            authority_source="curriculum_info",
            dry_run=False,
        )
        assert again["action"] == "existing"
        assert SkillCurriculum.query.filter_by(skill_id=skill_id).count() == 1

        conflict = ensure_section_outline_from_authoritative_metadata_v2(
            curriculum="vocational",
            volume="數學B2",
            chapter="99 錯誤章名",
            section=test_section,
            section_code="99-99",
            grade=11,
            authority_source="curriculum_info",
            dry_run=False,
        )
        assert conflict["action"] == "conflict"
        assert conflict["existing"]["chapter"] == "99 測試章"
        assert conflict["incoming"]["chapter"] == "99 錯誤章名"
        sc2 = SkillCurriculum.query.filter_by(skill_id=skill_id).one()
        assert sc2.chapter == "99 測試章"

        assert TextbookExample.query.count() == te_before
        assert (
            SkillCurriculum.query.filter(
                SkillCurriculum.skill_id.like("outline_vocational_數學B1_%")
            ).count()
            == b1_outline_before
        )

        _purge_test_outline()
        assert db.session.get(SkillInfo, skill_id) is None
        assert SkillCurriculum.query.filter_by(skill_id=skill_id).count() == 0


def test_no_gemini_import_in_outline_module():
    import core.textbook_section_outline as mod
    import inspect

    src = inspect.getsource(mod)
    assert "get_model" not in src
    assert "_call_gemini" not in src
    assert "generate_content" not in src
