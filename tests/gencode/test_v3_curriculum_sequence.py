# -*- coding: utf-8 -*-
"""Tests for Global Textbook-Order Sequence Selector."""

from __future__ import annotations

import pytest
import sqlite3
from unittest import mock
from core.gencode.services.v3_curriculum_ordering_service import (
    parse_source_description,
    get_sorted_component_ids_for_skill,
)


def test_parse_source_description():
    # 1. Check priority groups and numbers extraction
    assert parse_source_description("例題1") == {"source_group": "example", "source_number": 1, "source_subnumber": 0}
    assert parse_source_description("隨堂練習2-3") == {"source_group": "in_class", "source_number": 2, "source_subnumber": 3}
    assert parse_source_description("基礎練習4") == {"source_group": "basic_practice", "source_number": 4, "source_subnumber": 0}
    assert parse_source_description("綜合練習 題5") == {"source_group": "comprehensive", "source_number": 5, "source_subnumber": 0}
    assert parse_source_description("自我評量 題1-2") == {"source_group": "self_assessment", "source_number": 1, "source_subnumber": 2}
    assert parse_source_description("歷屆考題 題3") == {"source_group": "past_exam", "source_number": 3, "source_subnumber": 0}


def test_curriculum_sequence_sorting():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT,
            source_description TEXT,
            difficulty_level INTEGER
        )
        """
    )
    cursor.executemany(
        "INSERT INTO textbook_examples (id, skill_id, source_description) VALUES (?, ?, ?)",
        [
            (101, "test_skill", "隨堂練習2"),
            (102, "test_skill", "例題1"),
            (103, "test_skill", "自我評量 題1"),
            (104, "test_skill", "例題2-1"),
        ]
    )
    conn.commit()

    verified = ["src_103", "src_101", "src_104", "src_102"]
    sorted_ids = get_sorted_component_ids_for_skill(conn, "test_skill", verified)
    # Expected order:
    # Phase 0:
    # (0, 1, 0, 0, 102) -> src_102
    # (0, 2, 0, 1, 101) -> src_101 (since subnumber is 0)
    # (0, 2, 1, 0, 104) -> src_104 (since subnumber is 1)
    # Phase 1:
    # (1, 3, 103, 1, 0) -> src_103
    assert sorted_ids == ["src_102", "src_101", "src_104", "src_103"]
    conn.close()


def test_curriculum_sequence_alternating_rules():
    """Test alternating rules: Example 1 -> In Class 1 -> Example 2 -> In Class 2 etc."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT,
            source_description TEXT,
            curriculum_order INTEGER
        )
        """
    )
    cursor.executemany(
        "INSERT INTO textbook_examples (id, skill_id, source_description, curriculum_order) VALUES (?, ?, ?, ?)",
        [
            (201, "skill_alt", "隨堂練習2", 1),
            (202, "skill_alt", "例題1", 2),
            (203, "skill_alt", "隨堂練習1", 3),
            (204, "skill_alt", "例題2", 4),
            (205, "skill_alt", "例題3", 5), # Missing counterpart 隨堂練習3
            (206, "skill_alt", "隨堂練習4", 6), # Missing counterpart 例題4
            (207, "skill_alt", "基礎練習1", 7), # Phase 1 basic_practice
            (208, "skill_alt", "綜合練習1", 8), # Phase 1 comprehensive
            (209, "skill_alt", "例題2-2", 9), # Subnumber 2-2
            (210, "skill_alt", "例題2-1", 10), # Subnumber 2-1
            (211, "skill_alt", "基礎練習0", 11), # Phase 1 basic_practice with small source_number (0), must stay in Phase 1
        ]
    )
    conn.commit()

    verified = ["src_211", "src_210", "src_209", "src_208", "src_207", "src_206", "src_205", "src_204", "src_203", "src_202", "src_201"]
    sorted_ids = get_sorted_component_ids_for_skill(conn, "skill_alt", verified)
    
    # Phase 0: examples & in_class
    # 1. 例題1 (src_202) -> 2. 隨堂1 (src_203)
    # 3. 例題2 (src_204) -> 4. 例題2-1 (src_210) -> 5. 例題2-2 (src_209) -> 6. 隨堂2 (src_201)
    # 7. 例題3 (src_205)
    # 8. 隨堂4 (src_206)
    # Phase 1: practices/assessments/exams (by group_priority: basic_practice (1) -> comprehensive (2))
    # 9. 基礎練習0 (src_211, curriculum_order=11)
    # 10. 基礎練習1 (src_207, curriculum_order=7)
    # 11. 綜合練習1 (src_208, curriculum_order=8)
    expected = [
        "src_202", "src_203", "src_204", "src_201", "src_210", "src_209", "src_205", "src_206",
        # Phase 1: basic_practice (priority 1) sorted by curriculum_order (7 vs 11 -> src_207 first then src_211)
        "src_207", "src_211",
        # Phase 1: comprehensive (priority 2)
        "src_208"
    ]
    assert sorted_ids == expected
    conn.close()


def test_next_question_curriculum_sequence_routing(monkeypatch):
    """Test get_next_question curriculum_sequence routing round-robin states inside flask session."""
    from app import create_app
    from models import db
    
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    with app.test_client() as client:
        # Mock user authentication using Flask-Login keys
        with client.session_transaction() as sess:
            sess["_user_id"] = "1"
            sess["_fresh"] = True
            sess["current_curriculum"] = "general"

        # Mock db queries for TextbookExample
        mock_examples = [
            mock.Mock(id=1, source_description="例題1"),
            mock.Mock(id=2, source_description="隨堂練習1"),
            mock.Mock(id=3, source_description="自我評量 題1"),
        ]

        class CustomProgress:
            def __init__(self):
                self.consecutive_correct = 0

        class CustomCurriculumEntry:
            def __init__(self):
                self.difficulty_level = 1

        # Mock db queries for Progress, prereq_query etc.
        class MockQuery:
            def __init__(self, model_class=None):
                self.model_class = model_class
            def filter_by(self, **kwargs):
                return self
            def join(self, *args, **kwargs):
                return self
            def filter(self, *args, **kwargs):
                return self
            def order_by(self, *args, **kwargs):
                return self
            def first(self):
                from models import SkillCurriculum
                if self.model_class == SkillCurriculum:
                    return CustomCurriculumEntry()
                return CustomProgress()
            def all(self):
                return []

        # Mock get_skill / wrapper module
        mock_mod = mock.Mock()
        mock_mod.GENERATOR_KEYS = ["src_1", "src_2", "src_3"]
        mock_mod.GENERATOR_SPECS = [{"component_id": "src_1"}, {"component_id": "src_2"}, {"component_id": "src_3"}]
        mock_mod.generate.return_value = {
            "question_text": "mock q",
            "correct_answer": "ans",
            "answer_contract": {"answer_type": "expression"},
        }

        monkeypatch.setattr("core.routes.practice.get_skill", lambda *a, **k: mock_mod)
        monkeypatch.setattr("core.routes.practice.db.session.query", lambda model_class, *a, **k: MockQuery(model_class))

        # Simulate database connect return value inside get_sorted_component_ids_for_skill
        monkeypatch.setattr("core.gencode.services.v3_curriculum_ordering_service.get_sorted_component_ids_for_skill", 
                            lambda conn, skill_id, verified_list: ["src_1", "src_2", "src_3"])

        # First request (index 0 -> src_1)
        resp = client.get("/get_next_question?skill=vh_test_skill")
        assert resp.status_code == 200, resp.get_data(as_text=True)
        with client.session_transaction() as sess:
            seq = sess["v3_sequence_vh_test_skill"]
            assert seq["current_component_index"] == 1
            assert seq["completed_component_ids"] == ["src_1"]
            assert seq["current_round"] == 1

        # Second request (index 1 -> src_2)
        resp = client.get("/get_next_question?skill=vh_test_skill")
        assert resp.status_code == 200
        with client.session_transaction() as sess:
            seq = sess["v3_sequence_vh_test_skill"]
            assert seq["current_component_index"] == 2
            assert seq["completed_component_ids"] == ["src_1", "src_2"]

        # Third request (index 2 -> src_3)
        resp = client.get("/get_next_question?skill=vh_test_skill")
        assert resp.status_code == 200
        with client.session_transaction() as sess:
            seq = sess["v3_sequence_vh_test_skill"]
            assert seq["current_component_index"] == 3
            assert seq["completed_component_ids"] == ["src_1", "src_2", "src_3"]

        # Fourth request (returns to index 0, increments round to 2)
        resp = client.get("/get_next_question?skill=vh_test_skill")
        assert resp.status_code == 200
        with client.session_transaction() as sess:
            seq = sess["v3_sequence_vh_test_skill"]
            assert seq["current_component_index"] == 1
            assert seq["current_round"] == 2
            assert seq["completed_component_ids"] == ["src_1"]
