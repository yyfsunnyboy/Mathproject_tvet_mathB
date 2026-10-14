"""Skill candidate and Phase 4 read-only decision regression tests."""

from flask import Flask
from sqlalchemy import event

from models import SkillCurriculum, SkillInfo, TextbookExample, db
import core.textbook_processor_v2 as processor
from core.textbook_importer_v3_preflight import preflight_self_assessment_phase4
from core.textbook_importer_v3_pipeline import _textbook_example_scope_query


CHAPTER = "第2章 三角函數的應用"
VOLUME = "數學B2"
INFO = {
    "curriculum": "vocational", "volume": VOLUME, "grade": 11,
    "chapter_index": 2, "source_scope": "chapter_self_assessment",
}


def _skill(skill_id, name):
    db.session.add(SkillInfo(
        skill_id=skill_id, skill_en_name=name, skill_ch_name=name,
        description=name, gemini_prompt=name, is_active=True,
    ))


def _binding(skill_id, section, name, chapter=CHAPTER):
    db.session.add(SkillCurriculum(
        skill_id=skill_id, curriculum="vocational", grade=11,
        volume=VOLUME, chapter=chapter, section=section, paragraph=name,
    ))


def _seed():
    for code in ("2-1", "2-2"):
        sid = f"outline_vocational_數學B2_{code.replace('-', '')}"
        _skill(sid, "outline")
        _binding(sid, f"{code} 測試小節", "outline")
    for code, index, name in (
        ("2-1", 1, "正弦定理"), ("2-1", 2, "餘弦定理"),
        ("2-2", 1, "直角三角形測量"),
    ):
        sid = f"vh_數學B2_SubSection_{code.replace('-', '_')}_{index}"
        _skill(sid, name)
        _binding(sid, f"{code} 測試小節", name)
    _skill("vh_數學B2_SubSection_2_1_3", "無綁定")
    bad = "vh_數學B2_UnknownConcept_SubSection_2_1_4"
    _skill(bad, "舊佔位")
    _binding(bad, "2-1 測試小節", "舊佔位")
    _skill("vh_數學B2_SubSection_2_1_5", "錯章")
    _binding("vh_數學B2_SubSection_2_1_5", "2-1 測試小節", "錯章", "第3章 三角函數的應用")
    db.session.commit()


def _scope():
    return {"questions": [
        {"label": "CH2自我評量 題1", "source_type": "self_assessment",
         "target": True, "formula_count": 2, "image_candidates": []},
        {"label": "CH2自我評量 題2", "source_type": "self_assessment",
         "target": True, "formula_count": 1, "image_candidates": []},
    ]}


def _meta():
    return {
        "CH2自我評量 題1": {"section_code": "2-1", "section_title": "2-1 測試小節",
                           "source_type": "self_assessment", "problem_text": "正弦定理題"},
        "CH2自我評量 題2": {"section_code": "2-2", "section_title": "2-2 測試小節",
                           "source_type": "self_assessment", "problem_text": "測量題"},
    }


def test_chapter_identity_requires_number_and_title():
    assert processor._same_chapter_identity(
        "2 三角函數的應用", "第2章 三角函數的應用"
    )
    assert processor._same_chapter_identity(
        "第 2 章 三角函數的應用", "第2章 三角函數的應用"
    )
    assert not processor._same_chapter_identity(
        "第2章 不同章名", "第2章 三角函數的應用"
    )
    assert not processor._same_chapter_identity(
        "第3章 三角函數的應用", "第2章 三角函數的應用"
    )


def test_bound_subsection_candidates_and_section_isolation(tmp_path):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path / 'skills.db'}"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _seed()
        def candidates(code):
            return processor._get_self_assessment_skill_candidates_v2(
                curriculum="vocational", volume=VOLUME,
                chapter_title="2 三角函數的應用", section_code=code,
            )
        assert [c["skill_id"] for c in candidates("2-1")] == [
            "vh_數學B2_SubSection_2_1_1", "vh_數學B2_SubSection_2_1_2",
        ]
        assert [c["skill_id"] for c in candidates("2-2")] == [
            "vh_數學B2_SubSection_2_2_1",
        ]
        valid, _ = processor.validate_existing_skill_binding_for_import(
            "vh_數學B2_SubSection_2_1_1", source_type="self_assessment",
            section_code="2-1", curriculum_info=INFO,
            chapter_title="第 2 章 三角函數的應用",
        )
        wrong, _ = processor.validate_existing_skill_binding_for_import(
            "vh_數學B2_SubSection_2_1_1", source_type="self_assessment",
            section_code="2-2", curriculum_info=INFO,
            chapter_title=CHAPTER,
        )
        unbound, _ = processor.validate_existing_skill_binding_for_import(
            "vh_數學B2_SubSection_2_1_3", source_type="self_assessment",
            section_code="2-1", curriculum_info=INFO,
            chapter_title=CHAPTER,
        )
        assert valid and not wrong and not unbound


def test_preflight_blocks_ambiguity_without_any_db_write(tmp_path):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path / 'preflight.db'}"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _seed()
        statements = []
        def record(_conn, _cursor, statement, _params, _context, _many):
            statements.append(statement.strip().upper())
        event.listen(db.engine, "before_cursor_execute", record)
        try:
            report = preflight_self_assessment_phase4(_scope(), _meta(), INFO)
        finally:
            event.remove(db.engine, "before_cursor_execute", record)
        assert [row["decision"] for row in report["questions"]] == [
            "BLOCKED_AMBIGUOUS", "BLOCKED_SKILL",
        ]
        assert report["ai_alignment_required"] is True
        assert report["ready"] is False
        assert report["db_actual_changes"] == 0
        assert not any(s.startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP"))
                       for s in statements)


def test_preflight_reuses_formal_resolution_and_identity_when_ai_returns_choice(
    tmp_path, monkeypatch
):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path / 'identity.db'}"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _seed()
        db.session.add(TextbookExample(
            skill_id="vh_數學B2_SubSection_2_1_1", source_curriculum="vocational",
            source_volume=VOLUME, source_chapter=CHAPTER,
            source_section="2-1 測試小節", source_description="CH2自我評量 題1",
            problem_text="原題", problem_type="self_assessment",
        ))
        db.session.commit()
        monkeypatch.setattr(
            processor, "_ai_select_formal_skill_for_problem_v2",
            lambda **kwargs: {"skill_id": kwargs["available_skills"][0]["skill_id"]},
        )
        before = db.session.query(TextbookExample).count()
        report = preflight_self_assessment_phase4(
            _scope(), _meta(), INFO, allow_ai=True,
        )
        assert [row["decision"] for row in report["questions"]] == [
            "EXISTING_SKIP", "NEW_INSERT",
        ]
        assert db.session.query(TextbookExample).count() == before


def test_final_skill_guard_rejects_empty_outline_and_wrong_scope(tmp_path):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path / 'guard.db'}"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _seed()
        valid = processor.validate_existing_skill_binding_for_import(
            "vh_數學B2_SubSection_2_1_1", source_type="textbook_exercise",
            section_code="2-1", curriculum_info=INFO, chapter_title=CHAPTER,
        )
        empty = processor.validate_existing_skill_binding_for_import(
            "", source_type="textbook_exercise", section_code="2-1",
            curriculum_info=INFO, chapter_title=CHAPTER,
        )
        outline = processor.validate_existing_skill_binding_for_import(
            "outline_vocational_數學B2_21", source_type="textbook_exercise",
            section_code="2-1", curriculum_info=INFO, chapter_title=CHAPTER,
        )
        wrong = processor.validate_existing_skill_binding_for_import(
            "vh_數學B2_SubSection_2_1_1", source_type="textbook_exercise",
            section_code="2-2", curriculum_info=INFO, chapter_title=CHAPTER,
        )
        assert valid == (True, "")
        assert empty == (False, "empty_skill_id")
        assert outline == (False, "outline_skill")
        assert wrong == (False, "section_code_mismatch")


def test_chapter_self_assessment_display_scope_counts_all_sections(tmp_path):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path / 'counts.db'}"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _seed()
        for number in range(1, 16):
            section_code = "2-1" if number <= 6 else "2-2"
            section = f"{section_code} 測試小節"
            skill = (
                "vh_數學B2_SubSection_2_1_1"
                if number <= 6 else "vh_數學B2_SubSection_2_2_1"
            )
            db.session.add(TextbookExample(
                skill_id=skill, source_curriculum="vocational", source_volume=VOLUME,
                source_chapter=CHAPTER, source_section=section,
                source_description=f"CH2自我評量 題{number}",
                problem_text=f"題目 {number}", problem_type="self_assessment",
            ))
        db.session.commit()
        chapter_rows = _textbook_example_scope_query({**INFO, "chapter": CHAPTER}, VOLUME).all()
        assert len(chapter_rows) == 15
        assert sum(row.source_section.startswith("2-1") for row in chapter_rows) == 6
        assert sum(row.source_section.startswith("2-2") for row in chapter_rows) == 9
        section_21 = TextbookExample.query.filter_by(
            source_curriculum="vocational", source_volume=VOLUME,
            source_chapter=CHAPTER, source_section="2-1 測試小節",
            problem_type="self_assessment",
        ).count()
        assert section_21 == 6
        assert all(not row.skill_id.startswith("outline_") for row in chapter_rows)


def test_chapter_scope_requires_chapter_but_not_document_section(tmp_path):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path / 'authority.db'}"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        query = _textbook_example_scope_query({**INFO, "chapter": CHAPTER, "section": ""}, VOLUME)
        assert query.count() == 0
        import pytest
        with pytest.raises(Exception, match="Chapter self-assessment requires chapter authority"):
            _textbook_example_scope_query({**INFO, "chapter": "", "section": ""}, VOLUME)
