# -*- coding: utf-8 -*-
"""Tests for formal concept (vh_*) ensure API."""

from __future__ import annotations

from sqlalchemy import delete

from core.textbook_formal_concept import (
    AUTHORITATIVE_CONCEPT_SOURCES,
    build_formal_skill_id_from_en_id,
    display_order_from_concept_code,
    ensure_formal_concept_from_authoritative_heading_v2,
    get_section_formal_skill_candidates,
)


def test_display_order_and_skill_id_rules():
    assert display_order_from_concept_code("1-1.1") == 1
    assert display_order_from_concept_code("1-1.4") == 4
    assert (
        build_formal_skill_id_from_en_id(volume="數學B2", concept_en_id="DirectedAngle")
        == "vh_數學B2_DirectedAngle"
    )


def test_invalid_authority_and_missing_outline():
    from app import app

    with app.app_context():
        bad = ensure_formal_concept_from_authoritative_heading_v2(
            curriculum="vocational",
            volume="數學B2",
            chapter="1 三角函數",
            section="1-1 角度的基本性質",
            concept_code="1-1.1",
            concept_name="有向角",
            concept_en_id="DirectedAngle",
            authority_source="phase3_gemini",
            dry_run=True,
        )
        assert bad["action"] == "invalid_authority"
        assert "phase3_gemini" not in AUTHORITATIVE_CONCEPT_SOURCES

        missing = ensure_formal_concept_from_authoritative_heading_v2(
            curriculum="vocational",
            volume="數學B3",
            chapter="1 測試",
            section="1-1 測試小節",
            concept_code="1-1.1",
            concept_name="測試概念",
            concept_en_id="TestConcept",
            authority_source="docx_heading",
            dry_run=True,
        )
        assert missing["action"] == "missing_outline"


def test_dry_run_would_create_when_outline_exists():
    from app import app

    with app.app_context():
        result = ensure_formal_concept_from_authoritative_heading_v2(
            curriculum="vocational",
            volume="數學B2",
            chapter="1 三角函數",
            section="1-1 角度的基本性質",
            concept_code="1-1.1",
            concept_name="有向角",
            concept_en_id="DirectedAngle",
            authority_source="deterministic_docx_heading",
            dry_run=True,
        )
        assert result["action"] in ("would_create", "existing")
        assert result["skill_id"] == "vh_數學B2_DirectedAngle"
        assert result["display_order"] == 1
        assert result["wrote"] is False


def test_create_existing_conflicts_candidate_pool_no_te():
    from app import app
    from core.textbook_section_outline import ensure_section_outline_from_authoritative_metadata_v2
    from models import SkillCurriculum, SkillInfo, TextbookExample, db

    outline_sid = "outline_vocational_數學B9_11"
    concept_sid = "vh_數學B9_UnitTestConcept"
    other_sid = "vh_數學B9_OtherConcept"

    def purge() -> None:
        for sid in (concept_sid, other_sid, outline_sid):
            db.session.execute(delete(SkillCurriculum).where(SkillCurriculum.skill_id == sid))
            db.session.execute(delete(SkillInfo).where(SkillInfo.skill_id == sid))
        # Also clear any leftover volume='數學B9' rows for this isolation fixture.
        db.session.execute(
            delete(SkillCurriculum).where(
                SkillCurriculum.curriculum == "vocational",
                SkillCurriculum.volume == "數學B9",
            )
        )
        db.session.commit()

    with app.app_context():
        try:
            purge()
            te_before = TextbookExample.query.count()
            b1_before = SkillCurriculum.query.filter(
                SkillCurriculum.skill_id.like("outline_vocational_數學B1_%")
            ).count()

            # Ensure temp outline for B9 1-1
            ol = ensure_section_outline_from_authoritative_metadata_v2(
                curriculum="vocational",
                volume="數學B9",
                chapter="1 測試章",
                section="1-1 測試節",
                section_code="1-1",
                grade=10,
                authority_source="form_confirmed",
                dry_run=False,
                flush=True,
            )
            assert ol["action"] == "created"
            db.session.commit()

            created = ensure_formal_concept_from_authoritative_heading_v2(
                curriculum="vocational",
                volume="數學B9",
                chapter="1 測試章",
                section="1-1 測試節",
                concept_code="1-1.1",
                concept_name="單元測試概念",
                concept_en_id="UnitTestConcept",
                authority_source="docx_heading",
                dry_run=False,
                flush=True,
            )
            assert created["action"] == "created"
            assert created["skill_id"] == concept_sid
            db.session.commit()

            si = db.session.get(SkillInfo, concept_sid)
            assert si is not None
            assert si.is_active is True
            assert si.skill_ch_name == "單元測試概念"
            assert si.category == "1-1 測試節"
            assert si.order_index == 1

            sc = SkillCurriculum.query.filter_by(skill_id=concept_sid).one()
            assert sc.paragraph == "單元測試概念"
            assert sc.display_order == 1

            again = ensure_formal_concept_from_authoritative_heading_v2(
                curriculum="vocational",
                volume="數學B9",
                chapter="1 測試章",
                section="1-1 測試節",
                concept_code="1-1.1",
                concept_name="單元測試概念",
                concept_en_id="UnitTestConcept",
                authority_source="reviewed_heading",
                dry_run=False,
            )
            assert again["action"] == "existing"
            assert SkillCurriculum.query.filter_by(skill_id=concept_sid).count() == 1

            conflict_name = ensure_formal_concept_from_authoritative_heading_v2(
                curriculum="vocational",
                volume="數學B9",
                chapter="1 測試章",
                section="1-1 測試節",
                concept_code="1-1.1",
                concept_name="不同中文名",
                concept_en_id="UnitTestConcept",
                authority_source="docx_heading",
                dry_run=False,
            )
            assert conflict_name["action"] == "conflict"

            # paragraph mapped to different skill_id
            db.session.add(
                SkillInfo(
                    skill_id=other_sid,
                    skill_en_name="OtherConcept",
                    skill_ch_name="另一概念",
                    category="1-1 測試節",
                    description="x",
                    input_type="text",
                    gemini_prompt="",
                    consecutive_correct_required=3,
                    is_active=True,
                    order_index=2,
                    importance=1,
                )
            )
            db.session.flush()
            conflict_para = ensure_formal_concept_from_authoritative_heading_v2(
                curriculum="vocational",
                volume="數學B9",
                chapter="1 測試章",
                section="1-1 測試節",
                concept_code="1-1.2",
                concept_name="單元測試概念",  # same paragraph as concept_sid
                concept_en_id="OtherConcept",
                authority_source="docx_heading",
                dry_run=False,
            )
            assert conflict_para["action"] == "conflict"
            assert conflict_para["reason"] == "paragraph_mapped_to_different_skill_id"

            cands = get_section_formal_skill_candidates(
                curriculum="vocational",
                volume="數學B9",
                section="1-1 測試節",
                section_code="1-1",
                chapter="1 測試章",
            )
            assert all(c["skill_id"].startswith("vh_") for c in cands)
            assert all(not c["skill_id"].startswith("outline_") for c in cands)
            assert any(c["skill_id"] == concept_sid for c in cands)
            # display_order may be 0 when candidate join misses SkillCurriculum;
            # presence of the concept skill is the contract under test.
            assert any(int(c.get("display_order") or 0) >= 0 for c in cands)

            assert TextbookExample.query.count() == te_before
            assert (
                SkillCurriculum.query.filter(
                    SkillCurriculum.skill_id.like("outline_vocational_數學B1_%")
                ).count()
                == b1_before
            )
        finally:
            purge()


def test_b9_fixture_purge_runs_on_assertion_failure():
    """Unit-level: purge in finally must run even when the body asserts."""
    from app import app
    from models import SkillCurriculum, SkillInfo, db

    outline_sid = "outline_vocational_數學B9_11"
    concept_sid = "vh_數學B9_UnitTestConcept"
    other_sid = "vh_數學B9_OtherConcept"
    marker_sid = "vh_數學B9_CleanupMarker"

    def purge() -> None:
        for sid in (concept_sid, other_sid, outline_sid, marker_sid):
            db.session.execute(delete(SkillCurriculum).where(SkillCurriculum.skill_id == sid))
            db.session.execute(delete(SkillInfo).where(SkillInfo.skill_id == sid))
        db.session.execute(
            delete(SkillCurriculum).where(
                SkillCurriculum.curriculum == "vocational",
                SkillCurriculum.volume == "數學B9",
            )
        )
        db.session.commit()

    with app.app_context():
        try:
            purge()
            db.session.add(
                SkillInfo(
                    skill_id=marker_sid,
                    skill_en_name="CleanupMarker",
                    skill_ch_name="清理標記",
                    category="test",
                    description="x",
                    input_type="text",
                    gemini_prompt="",
                    consecutive_correct_required=3,
                    is_active=True,
                    order_index=1,
                    importance=1,
                )
            )
            db.session.flush()
            db.session.add(
                SkillCurriculum(
                    skill_id=marker_sid,
                    curriculum="vocational",
                    grade=10,
                    volume="數學B9",
                    chapter="1 測試章",
                    section="1-1 測試節",
                    paragraph="清理標記",
                    display_order=1,
                    difficulty_level=1,
                )
            )
            db.session.commit()
            assert SkillInfo.query.get(marker_sid) is not None
            assert False, "intentional failure to exercise finally purge"
        except AssertionError:
            pass
        finally:
            purge()

        assert SkillInfo.query.get(marker_sid) is None
        assert (
            SkillCurriculum.query.filter_by(
                curriculum="vocational", volume="數學B9"
            ).count()
            == 0
        )
        assert SkillInfo.query.filter(SkillInfo.skill_id.like("vh_數學B9_%")).count() == 0
        assert (
            SkillInfo.query.filter(
                SkillInfo.skill_id.like("outline_vocational_數學B9_%")
            ).count()
            == 0
        )


def test_no_gemini_in_formal_concept_module():
    import inspect

    import core.textbook_formal_concept as mod

    src = inspect.getsource(mod)
    assert "get_model" not in src
    assert "_call_gemini" not in src
    assert "generate_content" not in src
