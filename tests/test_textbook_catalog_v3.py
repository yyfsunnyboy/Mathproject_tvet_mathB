# -*- coding: utf-8 -*-
"""Regression tests for the V3 whole-book catalog → outline import flow."""

from __future__ import annotations

import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from app import create_app
from core.textbook_catalog_v3 import (
    CatalogChapter,
    CatalogSection,
    _apply_catalog_to_db,
    _canonical_chapter_display,
    import_catalog_from_pdf_v3,
    import_catalog_from_pdf_v2_text,
    apply_catalog_from_token,
    encode_preview_token,
    decode_preview_token,
    validate_catalog_payload,
)
from core.textbook_section_outline import build_outline_skill_id_for_section
from models import SkillCurriculum, SkillInfo, db


@pytest.fixture()
def app_ctx():
    import config as _cfg

    db_path = Path("reports") / f"pytest_catalog_v3_{uuid.uuid4().hex[:8]}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            db.create_all()
            yield app
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        try:
            if db_path.exists():
                db_path.unlink()
        except OSError:
            pass


def _build_4_chapters() -> list[CatalogChapter]:
    return [
        CatalogChapter(
            chapter_index=1,
            chapter_title="三角函數",
            sections=[
                CatalogSection("1-1", 1, "角度的基本性質"),
                CatalogSection("1-2", 2, "銳角三角函數"),
                CatalogSection("1-3", 3, "任意角的三角函數"),
                CatalogSection("1-4", 4, "正弦、餘弦函數的圖形"),
            ],
        ),
        CatalogChapter(
            chapter_index=2,
            chapter_title="三角函數的應用",
            sections=[
                CatalogSection("2-1", 1, "正弦定理與餘弦定理"),
                CatalogSection("2-2", 2, "三角測量"),
            ],
        ),
        CatalogChapter(
            chapter_index=3,
            chapter_title="向量",
            sections=[
                CatalogSection("3-1", 1, "向量的作圖"),
                CatalogSection("3-2", 2, "向量的坐標表示法"),
                CatalogSection("3-3", 3, "向量的內積"),
            ],
        ),
        CatalogChapter(
            chapter_index=4,
            chapter_title="圓與直線",
            sections=[
                CatalogSection("4-1", 1, "圓方程式"),
                CatalogSection("4-2", 2, "圓與直線的關係"),
            ],
        ),
    ]


def test_apply_catalog_creates_full_4_chapters(app_ctx):
    with app_ctx.app_context():
        chapters = _build_4_chapters()
        report = _apply_catalog_to_db(
            curriculum="vocational",
            volume="數學B2",
            grade=10,
            chapters=chapters,
            dry_run=False,
            commit=True,
        )
        assert report.ok is True
        assert report.sections_created == 11
        assert report.sections_reused == 0
        assert report.chapters_created == 4

        rows = SkillCurriculum.query.filter(
            SkillCurriculum.curriculum == "vocational",
            SkillCurriculum.volume == "數學B2",
            SkillCurriculum.skill_id.startswith("outline_"),
        ).all()
        assert len(rows) == 11

        section_1_2 = next((r for r in rows if r.section.startswith("1-2 ")), None)
        assert section_1_2 is not None
        assert section_1_2.chapter == "第1章 三角函數"
        assert section_1_2.section == "1-2 銳角三角函數"
        assert section_1_2.grade == 10

        skill = db.session.get(SkillInfo, section_1_2.skill_id)
        assert skill is not None
        assert skill.category == "outline"


def test_apply_catalog_reuses_existing_section_and_updates_chapter(app_ctx):
    with app_ctx.app_context():
        # Simulate a previously imported section textbook with only a placeholder chapter.
        skill_id, _, section_title = build_outline_skill_id_for_section(
            curriculum="vocational",
            volume="數學B2",
            section_code="1-2",
            section="1-2 銳角三角函數",
        )
        db.session.add(
            SkillInfo(
                skill_id=skill_id,
                skill_en_name=skill_id,
                skill_ch_name=section_title,
                category="outline",
                description="placeholder",
                input_type="text",
                gemini_prompt="",
                consecutive_correct_required=3,
                is_active=False,
                order_index=9999,
            )
        )
        db.session.add(
            SkillCurriculum(
                skill_id=skill_id,
                curriculum="vocational",
                volume="數學B2",
                grade=10,
                chapter="1",
                section=section_title,
                display_order=12,
                difficulty_level=1,
            )
        )
        db.session.commit()

        chapters = _build_4_chapters()
        report = _apply_catalog_to_db(
            curriculum="vocational",
            volume="數學B2",
            grade=10,
            chapters=chapters,
            dry_run=False,
            commit=True,
        )
        assert report.ok is True
        # The existing 1-2 section was found via chapter alias rename (Phase 0)
        # and is treated as update; remaining 10 sections are created.
        assert report.sections_created == 10
        assert report.sections_reused + report.sections_updated >= 1

        row = SkillCurriculum.query.filter_by(skill_id=skill_id).first()
        assert row.chapter == "第1章 三角函數"

        # TextbookExample skill association remains via the same skill_id.
        assert db.session.get(SkillInfo, skill_id) is not None


def test_apply_catalog_conflict_on_different_section_title(app_ctx):
    with app_ctx.app_context():
        skill_id, _, section_title = build_outline_skill_id_for_section(
            curriculum="vocational",
            volume="數學B2",
            section_code="1-2",
            section="1-2 完全不同名稱",
        )
        db.session.add(
            SkillInfo(
                skill_id=skill_id,
                skill_en_name=skill_id,
                skill_ch_name=section_title,
                category="outline",
                description="placeholder",
                input_type="text",
                gemini_prompt="",
                consecutive_correct_required=3,
                is_active=False,
                order_index=9999,
            )
        )
        db.session.add(
            SkillCurriculum(
                skill_id=skill_id,
                curriculum="vocational",
                volume="數學B2",
                grade=10,
                chapter="1 舊章名",
                section=section_title,
                display_order=12,
                difficulty_level=1,
            )
        )
        db.session.commit()

        chapters = _build_4_chapters()
        report = _apply_catalog_to_db(
            curriculum="vocational",
            volume="數學B2",
            grade=10,
            chapters=chapters,
            dry_run=False,
            commit=True,
        )
        assert report.ok is False
        assert len(report.conflicts) == 1
        assert report.conflicts[0]["section_code"] == "1-2"
        assert "完全不同名稱" in report.conflicts[0]["existing_sections"][0]["section"]

        # Existing row must not be overwritten.
        row = SkillCurriculum.query.filter_by(skill_id=skill_id).first()
        assert row.section == section_title


def test_apply_catalog_no_duplicates_when_idempotent(app_ctx):
    with app_ctx.app_context():
        chapters = _build_4_chapters()
        r1 = _apply_catalog_to_db(
            curriculum="vocational",
            volume="數學B2",
            grade=10,
            chapters=chapters,
            dry_run=False,
            commit=True,
        )
        assert r1.sections_created == 11
        assert r1.sections_reused == 0

        r2 = _apply_catalog_to_db(
            curriculum="vocational",
            volume="數學B2",
            grade=10,
            chapters=chapters,
            dry_run=False,
            commit=True,
        )
        assert r2.ok is True
        assert r2.sections_created == 0
        assert r2.sections_reused == 11
        assert r2.sections_updated == 0

        count = SkillCurriculum.query.filter(
            SkillCurriculum.curriculum == "vocational",
            SkillCurriculum.volume == "數學B2",
            SkillCurriculum.skill_id.startswith("outline_"),
        ).count()
        assert count == 11


def test_validate_catalog_payload_valid_4_chapters():
    payload = {
        "volume": "數學B2",
        "chapters": [
            {
                "chapter_index": 1,
                "chapter_title": "三角函數",
                "sections": [
                    {"section_code": "1-1", "section_index": 1, "section_title": "角度的基本性質"},
                    {"section_code": "1-2", "section_index": 2, "section_title": "銳角三角函數"},
                ],
            },
            {
                "chapter_index": 2,
                "chapter_title": "三角函數的應用",
                "sections": [
                    {"section_code": "2-1", "section_index": 1, "section_title": "正弦定理與餘弦定理"},
                ],
            },
        ],
    }
    assert validate_catalog_payload(payload) == []


def test_validate_catalog_payload_chapter_section_mismatch():
    payload = {
        "volume": "數學B2",
        "chapters": [
            {
                "chapter_index": 1,
                "chapter_title": "章",
                "sections": [
                    {"section_code": "2-3", "section_index": 3, "section_title": "錯誤節"},
                ],
            }
        ],
    }
    errors = validate_catalog_payload(payload)
    assert any("does not match chapter_index" in e for e in errors)


def test_validate_catalog_payload_duplicate_section_code():
    payload = {
        "volume": "數學B2",
        "chapters": [
            {
                "chapter_index": 1,
                "chapter_title": "章",
                "sections": [
                    {"section_code": "1-1", "section_index": 1, "section_title": "節 A"},
                    {"section_code": "1-1", "section_index": 1, "section_title": "節 B"},
                ],
            }
        ],
    }
    errors = validate_catalog_payload(payload)
    assert any("duplicate section_code" in e for e in errors)


def test_validate_catalog_payload_empty_title():
    payload = {
        "volume": "數學B2",
        "chapters": [
            {
                "chapter_index": 1,
                "chapter_title": "   ",
                "sections": [
                    {"section_code": "1-1", "section_index": 1, "section_title": "節"},
                ],
            }
        ],
    }
    errors = validate_catalog_payload(payload)
    assert any("missing chapter_title" in e for e in errors)


@patch("core.textbook_catalog_v3._detect_catalog_pages")
@patch("core.textbook_catalog_v3._render_pages_to_images")
@patch("core.textbook_catalog_v3._call_gemini_catalog_vision")
@patch("core.textbook_catalog_v3._parse_catalog_json")
def test_import_catalog_from_pdf_v3_dry_run(
    mock_parse_json, mock_gemini_vision, mock_render, mock_detect, app_ctx
):
    with app_ctx.app_context():
        mock_detect.return_value = [1, 2]
        mock_render.return_value = ["tmp/page_001.png"]
        mock_gemini_vision.return_value = '{"volume": "數學B2", "chapters": ["ignore"]}'
        payload = {
            "volume": "數學B2",
            "chapters": [
                {
                    "chapter_index": 1,
                    "chapter_title": "三角函數",
                    "sections": [
                        {"section_code": "1-1", "section_index": 1, "section_title": "角度的基本性質"},
                    ],
                }
            ],
        }
        mock_parse_json.return_value = payload

        result = import_catalog_from_pdf_v3(
            "dummy.pdf",
            curriculum="vocational",
            volume="數學B2",
            dry_run=True,
            commit=False,
        )
        assert result["ok"] is True
        assert result["dry_run"] is True
        assert result["sections_created"] == 1
        assert result["pages_rendered"] == 2
        assert result["curriculum"] == "vocational"


# ---------------------------------------------------------------------------
# V2-text bridge regression tests
# ---------------------------------------------------------------------------

_V2_NORMALISED_PAYLOAD = {
    "curriculum": "vocational",
    "volume": "數學B2",
    "grade": 10,
    "chapters": [
        {
            "chapter_title": "1 三角函數",
            "sections": [
                {"section_code": "1-1", "section_title": "1-1 角度的基本性質"},
                {"section_code": "1-2", "section_title": "1-2 銳角三角函數"},
            ],
        }
    ],
}


@patch("core.textbook_processor_v2._call_gemini_pdf_outline")
@patch("core.textbook_processor_v2.extract_pdf_directory_text_v2")
def test_import_catalog_v2_text_pdf_parseable(
    mock_extract, mock_gemini, app_ctx
):
    """V2 text bridge: PDF can be parsed and chapters returned."""
    with app_ctx.app_context():
        mock_extract.return_value = ("第1章 三角函數\n1-1 角度的基本性質\n1-2 銳角三角函數", 3)
        mock_gemini.return_value = _V2_NORMALISED_PAYLOAD

        result = import_catalog_from_pdf_v2_text(
            "dummy.pdf",
            curriculum="vocational",
            volume="數學B2",
            dry_run=True,
            commit=False,
        )
        assert result["ok"] is True
        assert result["parse_mode"] == "v2_text"
        assert result["sections_created"] >= 1
        assert result["pages_read"] == 3


@patch("core.textbook_processor_v2._call_gemini_pdf_outline")
@patch("core.textbook_processor_v2.extract_pdf_directory_text_v2")
def test_import_catalog_v2_text_result_reachable_by_apply_db(
    mock_extract, mock_gemini, app_ctx
):
    """V3 catalog _apply_catalog_to_db receives chapters from V2 bridge (dry_run)."""
    with app_ctx.app_context():
        mock_extract.return_value = ("第1章 三角函數\n1-1 ...\n1-2 ...", 2)
        mock_gemini.return_value = _V2_NORMALISED_PAYLOAD

        result = import_catalog_from_pdf_v2_text(
            "dummy.pdf",
            curriculum="vocational",
            volume="數學B2",
            dry_run=True,
            commit=False,
        )
        # Both sections should be reported as created (dry_run, so not written)
        assert result["sections_created"] == 2
        assert result["chapters_created"] == 1
        assert result["ok"] is True


@patch("core.textbook_processor_v2._call_gemini_pdf_outline")
@patch("core.textbook_processor_v2.extract_pdf_directory_text_v2")
def test_import_catalog_v2_text_reuses_existing_section(
    mock_extract, mock_gemini, app_ctx
):
    """Existing section 1-2 must be reused, not recreated."""
    with app_ctx.app_context():
        mock_extract.return_value = ("第1章 三角函數\n1-2 銳角三角函數", 2)
        mock_gemini.return_value = {
            "curriculum": "vocational",
            "volume": "數學B2",
            "grade": 10,
            "chapters": [
                {
                    "chapter_title": "1 三角函數",
                    "sections": [
                        {"section_code": "1-2", "section_title": "1-2 銳角三角函數"},
                    ],
                }
            ],
        }

        # First import: create the section (commit=True so it persists in test DB)
        result1 = import_catalog_from_pdf_v2_text(
            "dummy.pdf",
            curriculum="vocational",
            volume="數學B2",
            dry_run=False,
            commit=True,
        )
        assert result1["sections_created"] == 1

        # Second import: must reuse, not create again
        result2 = import_catalog_from_pdf_v2_text(
            "dummy.pdf",
            curriculum="vocational",
            volume="數學B2",
            dry_run=False,
            commit=True,
        )
        assert result2["sections_created"] == 0
        assert result2["sections_reused"] + result2["sections_updated"] >= 1


# ---------------------------------------------------------------------------
# Two-stage preview / confirm tests
# ---------------------------------------------------------------------------

def test_chapter_display_bare_title():
    assert _canonical_chapter_display(1, "三角函數") == "第1章 三角函數"


def test_chapter_display_already_has_prefix():
    assert _canonical_chapter_display(1, "第1章 三角函數") == "第1章 三角函數"


def test_chapter_display_numeric_prefix():
    assert _canonical_chapter_display(2, "2 三角函數的應用") == "第2章 三角函數的應用"


def test_chapter_display_no_double_prefix():
    result = _canonical_chapter_display(1, "第1章 三角函數")
    assert result.count("第1章") == 1


def test_preview_token_roundtrip(app_ctx):
    with app_ctx.app_context():
        payload = {"curriculum": "vocational", "volume": "數學B2", "grade": 10,
                   "chapters": [{"chapter_index": 1, "chapter_title": "三角函數",
                                  "sections": [{"section_code": "1-1", "section_index": 1,
                                                "section_title": "角度", "page": None}]}]}
        token = encode_preview_token(payload)
        decoded = decode_preview_token(token)
        assert decoded["volume"] == "數學B2"
        assert decoded["chapters"][0]["chapter_index"] == 1


def test_invalid_preview_token_rejected(app_ctx):
    with app_ctx.app_context():
        import pytest
        with pytest.raises(ValueError):
            decode_preview_token("invalid.token.here")


@patch("core.textbook_processor_v2._call_gemini_pdf_outline")
@patch("core.textbook_processor_v2.extract_pdf_directory_text_v2")
def test_preview_does_not_write_db(mock_extract, mock_gemini, app_ctx):
    """Preview (dry_run=True) must not write to DB."""
    with app_ctx.app_context():
        mock_extract.return_value = ("第1章 三角函數\n1-1 角度\n1-2 銳角", 2)
        mock_gemini.return_value = _V2_NORMALISED_PAYLOAD

        result = import_catalog_from_pdf_v2_text(
            "dummy.pdf", curriculum="vocational", volume="數學B2",
            dry_run=True, commit=False,
        )
        assert result["ok"] is True
        assert result["dry_run"] is True
        # DB must have no rows
        from models import SkillCurriculum
        rows = SkillCurriculum.query.filter_by(curriculum="vocational", volume="數學B2").all()
        assert rows == []


@patch("core.textbook_processor_v2._call_gemini_pdf_outline")
@patch("core.textbook_processor_v2.extract_pdf_directory_text_v2")
def test_preview_returns_token_and_chapters(mock_extract, mock_gemini, app_ctx):
    """Preview result must include preview_token and preview_chapters."""
    with app_ctx.app_context():
        mock_extract.return_value = ("第1章 三角函數\n1-1 角度", 2)
        mock_gemini.return_value = _V2_NORMALISED_PAYLOAD

        result = import_catalog_from_pdf_v2_text(
            "dummy.pdf", curriculum="vocational", volume="數學B2",
            dry_run=True, commit=False,
        )
        assert "preview_token" in result
        assert isinstance(result["preview_token"], str)
        assert "preview_chapters" in result
        assert len(result["preview_chapters"]) >= 1


@patch("core.textbook_processor_v2._call_gemini_pdf_outline")
@patch("core.textbook_processor_v2.extract_pdf_directory_text_v2")
def test_confirm_writes_db_without_reparsing(mock_extract, mock_gemini, app_ctx):
    """Confirm step must commit to DB and not re-call AI."""
    with app_ctx.app_context():
        mock_extract.return_value = ("第1章 三角函數\n1-1 角度", 2)
        mock_gemini.return_value = _V2_NORMALISED_PAYLOAD

        # Stage 1: preview
        preview = import_catalog_from_pdf_v2_text(
            "dummy.pdf", curriculum="vocational", volume="數學B2",
            dry_run=True, commit=False,
        )
        token = preview["preview_token"]

        # Stage 2: confirm — AI must NOT be called again
        mock_extract.reset_mock()
        mock_gemini.reset_mock()

        confirmed = apply_catalog_from_token(token, commit=True)
        assert confirmed["confirmed"] is True
        assert confirmed["ok"] is True
        assert confirmed["sections_created"] >= 1

        mock_extract.assert_not_called()
        mock_gemini.assert_not_called()

        # Rows must exist in DB now
        from models import SkillCurriculum
        rows = SkillCurriculum.query.filter_by(curriculum="vocational", volume="數學B2").all()
        assert len(rows) >= 1


def test_confirm_with_invalid_token_rejected(app_ctx):
    """Invalid token must raise ValueError and not write DB."""
    with app_ctx.app_context():
        import pytest
        with pytest.raises(ValueError, match="預覽資料已失效"):
            apply_catalog_from_token("bad.token.here", commit=True)


# ---------------------------------------------------------------------------
# Chapter alias / duplicate chapter regression tests
# ---------------------------------------------------------------------------

from core.textbook_catalog_v3 import _extract_chapter_index


def test_extract_chapter_index_variants():
    assert _extract_chapter_index("第1章 三角函數") == 1
    assert _extract_chapter_index("第1章") == 1
    assert _extract_chapter_index("1 三角函數") == 1
    assert _extract_chapter_index("1") == 1
    assert _extract_chapter_index("2 三角函數的應用") == 2
    assert _extract_chapter_index("第2章") == 2
    assert _extract_chapter_index("") is None


def test_chapter_index_2_not_merged_into_1():
    assert _extract_chapter_index("第2章 三角函數") != _extract_chapter_index("第1章 三角函數")


def test_alias_rename_updates_chapter_preserves_skill_id(app_ctx):
    """DB: chapter='第1章', section 1-2 with real skill_id.
    After catalog import with '第1章 三角函數':
    - chapter updated to '第1章 三角函數'
    - original skill_id unchanged
    - no new duplicate row created
    """
    with app_ctx.app_context():
        real_skill_id = "real_skill_math_b2_ch1_sec12"
        db.session.add(SkillInfo(
            skill_id=real_skill_id, skill_en_name=real_skill_id,
            skill_ch_name="銳角三角函數", category="outline",
            description="real skill", input_type="text", gemini_prompt="",
            consecutive_correct_required=3, is_active=True, order_index=1,
        ))
        db.session.add(SkillCurriculum(
            skill_id=real_skill_id, curriculum="vocational", volume="數學B2",
            grade=10, chapter="第1章", section="1-2 銳角三角函數",
            display_order=2, difficulty_level=1,
        ))
        db.session.commit()

        chapters = [CatalogChapter(
            chapter_index=1, chapter_title="三角函數",
            sections=[CatalogSection(section_code="1-2", section_index=1,
                                     section_title="銳角三角函數")],
        )]
        report = _apply_catalog_to_db(
            curriculum="vocational", volume="數學B2", grade=10,
            chapters=chapters, dry_run=False, commit=True,
        )

        # No new chapter should have been created
        assert report.sections_created == 0
        # Existing row chapter should now be the authoritative display
        rows = SkillCurriculum.query.filter_by(
            curriculum="vocational", volume="數學B2", grade=10
        ).all()
        chapters_found = {r.chapter for r in rows}
        assert "第1章 三角函數" in chapters_found
        assert "第1章" not in chapters_found  # old alias gone
        # skill_id must be preserved
        assert all(r.skill_id == real_skill_id for r in rows)


def test_duplicate_chapter_aliases_converge_on_reimport(app_ctx):
    """DB already has BOTH '第1章' and '第1章 三角函數' rows for section 1-2.
    After a fresh catalog import the two aliases should converge to one.
    Distinct chapter values must be only '第1章 三角函數'.
    """
    with app_ctx.app_context():
        old_skill_id, _, sec_title = build_outline_skill_id_for_section(
            curriculum="vocational", volume="數學B2",
            section_code="1-2", section="1-2 銳角三角函數",
        )
        new_skill_id = old_skill_id  # same code produces same skill_id

        db.session.add(SkillInfo(
            skill_id=old_skill_id, skill_en_name=old_skill_id,
            skill_ch_name="銳角三角函數", category="outline",
            description="old", input_type="text", gemini_prompt="",
            consecutive_correct_required=3, is_active=False, order_index=9999,
        ))
        # Insert two rows with different chapter alias for same section
        db.session.add(SkillCurriculum(
            skill_id=old_skill_id, curriculum="vocational", volume="數學B2",
            grade=10, chapter="第1章", section="1-2 銳角三角函數",
            display_order=2, difficulty_level=1,
        ))
        db.session.add(SkillCurriculum(
            skill_id=old_skill_id, curriculum="vocational", volume="數學B2",
            grade=10, chapter="第1章 三角函數", section="1-2 銳角三角函數",
            display_order=2, difficulty_level=1,
        ))
        db.session.commit()

        chapters = [CatalogChapter(
            chapter_index=1, chapter_title="三角函數",
            sections=[CatalogSection(section_code="1-2", section_index=1,
                                     section_title="銳角三角函數")],
        )]
        _apply_catalog_to_db(
            curriculum="vocational", volume="數學B2", grade=10,
            chapters=chapters, dry_run=False, commit=True,
        )

        rows = SkillCurriculum.query.filter_by(
            curriculum="vocational", volume="數學B2", grade=10
        ).all()
        distinct_chapters = {r.chapter for r in rows}
        # After import, '第1章' alias must be gone
        assert "第1章" not in distinct_chapters
        assert "第1章 三角函數" in distinct_chapters


def test_dry_run_alias_chapter_counts_as_update_not_create(app_ctx):
    """Preview with '第1章' in DB and catalog '第1章 三角函數':
    sections_created should be 0, sections_updated/reused >= 1.
    """
    with app_ctx.app_context():
        skill_id, _, sec_title = build_outline_skill_id_for_section(
            curriculum="vocational", volume="數學B2",
            section_code="1-1", section="1-1 角度的基本性質",
        )
        db.session.add(SkillInfo(
            skill_id=skill_id, skill_en_name=skill_id, skill_ch_name="角度",
            category="outline", description="p", input_type="text", gemini_prompt="",
            consecutive_correct_required=3, is_active=False, order_index=9999,
        ))
        db.session.add(SkillCurriculum(
            skill_id=skill_id, curriculum="vocational", volume="數學B2",
            grade=10, chapter="第1章", section="1-1 角度的基本性質",
            display_order=1, difficulty_level=1,
        ))
        db.session.commit()

        chapters = [CatalogChapter(
            chapter_index=1, chapter_title="三角函數",
            sections=[CatalogSection(section_code="1-1", section_index=1,
                                     section_title="角度的基本性質")],
        )]
        report = _apply_catalog_to_db(
            curriculum="vocational", volume="數學B2", grade=10,
            chapters=chapters, dry_run=True, commit=False,
        )
        assert report.sections_created == 0
        assert report.sections_reused + report.sections_updated >= 1
        # dry_run: DB must still have old value
        row = SkillCurriculum.query.filter_by(skill_id=skill_id).first()
        assert row.chapter == "第1章"  # unchanged because dry_run


# ---------------------------------------------------------------------------
# Route-level two-stage tests (Flask test client)
# ---------------------------------------------------------------------------

from models import User


def _login_client(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def route_app():
    """App fixture with a teacher user, for route-level tests."""
    import config as _cfg
    db_path = Path("reports") / f"pytest_catalog_route_{uuid.uuid4().hex[:8]}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    prev_uri = _cfg.Config.SQLALCHEMY_DATABASE_URI
    _cfg.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path.resolve()).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            from models import db as _db
            _db.create_all()
            teacher = User(
                username=f"teacher_{uuid.uuid4().hex[:6]}",
                password_hash="x",
                role="teacher",
            )
            _db.session.add(teacher)
            _db.session.commit()
            yield app, teacher.id
    finally:
        _cfg.Config.SQLALCHEMY_DATABASE_URI = prev_uri
        try:
            if db_path.exists():
                db_path.unlink()
        except OSError:
            pass


def test_preview_without_pdf_returns_400(route_app):
    """action=preview without PDF must return 400 missing_catalog_pdf."""
    app, teacher_id = route_app
    client = app.test_client()
    _login_client(client, teacher_id)
    resp = client.post(
        "/admin/textbook_catalog_v3",
        data={"action": "preview", "volume": "數學B2", "curriculum": "vocational"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "missing_catalog_pdf"


@patch("core.textbook_processor_v2._call_gemini_pdf_outline")
@patch("core.textbook_processor_v2.extract_pdf_directory_text_v2")
def test_confirm_with_valid_token_no_pdf_succeeds(mock_extract, mock_gemini, route_app):
    """action=confirm with valid preview_token and NO PDF must succeed."""
    app, teacher_id = route_app
    client = app.test_client()
    _login_client(client, teacher_id)

    with app.app_context():
        mock_extract.return_value = ("第1章 三角函數\n1-2 銳角三角函數", 2)
        mock_gemini.return_value = {
            "curriculum": "vocational", "volume": "數學B2", "grade": 10,
            "chapters": [{"chapter_title": "1 三角函數",
                           "sections": [{"section_code": "1-2", "section_title": "1-2 銳角三角函數"}]}],
        }
        preview = import_catalog_from_pdf_v2_text(
            "dummy.pdf", curriculum="vocational", volume="數學B2",
            dry_run=True, commit=False,
        )
        token = preview["preview_token"]

    # Reset mocks: confirm must NOT call them
    mock_extract.reset_mock()
    mock_gemini.reset_mock()

    resp = client.post(
        "/admin/textbook_catalog_v3",
        data={"action": "confirm", "preview_token": token},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200, resp.data
    data = resp.get_json()
    assert data["ok"] is True
    assert data.get("confirmed") is True

    mock_extract.assert_not_called()
    mock_gemini.assert_not_called()


def test_confirm_missing_token_returns_400(route_app):
    """action=confirm without preview_token must return 400."""
    app, teacher_id = route_app
    client = app.test_client()
    _login_client(client, teacher_id)
    resp = client.post(
        "/admin/textbook_catalog_v3",
        data={"action": "confirm"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "missing_preview_token"


def test_confirm_invalid_token_returns_400(route_app):
    """action=confirm with tampered/invalid token must return 400."""
    app, teacher_id = route_app
    client = app.test_client()
    _login_client(client, teacher_id)
    resp = client.post(
        "/admin/textbook_catalog_v3",
        data={"action": "confirm", "preview_token": "bad.token.abc"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "invalid_preview_token"
