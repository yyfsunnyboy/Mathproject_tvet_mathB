import json
import os
from dataclasses import dataclass

from flask import Flask

import core.textbook_processor as processor
from core.question_image_assets import (
    attach_image_metadata,
    infer_source_page_for_question,
    question_needs_image,
)


def test_question_needs_image_basic():
    assert question_needs_image("如圖所示，求面積") is True
    assert question_needs_image("使用樹狀圖列出") is True
    assert question_needs_image("試求 3! 之值") is False


def test_infer_source_page_by_problem_text():
    item = {"title": "例題 7", "problem_text": "甲乙兩地最短路徑"}
    pages = {3: "本頁含有甲乙兩地最短路徑與圖示"}
    source_page, reason = infer_source_page_for_question(item, pages)
    assert source_page == 3
    assert reason == "matched_problem_text"


def test_infer_source_page_by_image_description():
    item = {"title": "統測補給站 2", "has_image": True, "image_description": "棋盤式街道圖"}
    pages = {5: "下圖為棋盤式街道圖，請依規則計數"}
    source_page, reason = infer_source_page_for_question(item, pages)
    assert source_page == 5
    assert reason == "matched_image_description"


def test_infer_source_page_by_image_keywords():
    item = {"title": "例題 9", "problem_text": "請依右圖回答"}
    pages = {7: "依右圖可得路徑共有..."}
    source_page, reason = infer_source_page_for_question(item, pages)
    assert source_page == 7
    assert reason == "matched_image_keywords"


def test_infer_source_page_respects_explicit_source_page():
    item = {"title": "例題 1", "source_page": 4, "problem_text": "如圖"}
    pages = {9: "如圖"}
    source_page, reason = infer_source_page_for_question(item, pages)
    assert source_page == 4
    assert reason == "explicit_source_page"


def test_attach_metadata_json_image_assets():
    class _Row:
        notes = None

    row = _Row()
    ok = attach_image_metadata(
        row,
        {
            "has_image": True,
            "needs_image_review": True,
            "image_assets": [
                {
                    "asset_type": "page_image",
                    "path": "uploads/question_assets/a/b/page_004.png",
                    "page_index": 3,
                    "source_page": 4,
                    "bbox": None,
                    "needs_crop_review": True,
                    "reason": "question contains 如圖",
                    "image_description": "棋盤式街道圖",
                }
            ],
        },
    )
    assert ok is True
    data = json.loads(row.notes)
    assert data["has_image"] is True
    assert data["image_assets"][0]["path"].endswith("page_004.png")


@dataclass
class _FakeRow:
    values: dict

    def __getattr__(self, item):
        return self.values.get(item)


class _FakeQuery:
    def __init__(self, rows, key_field=None):
        self.rows = rows
        self.filters = {}
        self.key_field = key_field

    def filter_by(self, **kwargs):
        q = _FakeQuery(self.rows, key_field=self.key_field)
        q.filters = kwargs
        return q

    def first(self):
        for row in self.rows:
            if all(getattr(row, k, None) == v for k, v in self.filters.items()):
                return row
        return None

    def get(self, key):
        if not self.key_field:
            return None
        for row in self.rows:
            if getattr(row, self.key_field, None) == key:
                return row
        return None


class _Q:
    def put(self, _msg):
        return None


def _setup_fake_db(monkeypatch):
    skill_rows = []
    curriculum_rows = []
    textbook_rows = []

    class FakeSkillInfo:
        query = _FakeQuery(skill_rows, key_field="skill_id")

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class FakeSkillCurriculum:
        query = _FakeQuery(curriculum_rows)

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class FakeTextbookExample:
        query = _FakeQuery(textbook_rows)

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.notes = kwargs.get("notes")
            self.id = len(textbook_rows) + 1

    class FakeSession:
        @staticmethod
        def add(obj):
            if isinstance(obj, FakeSkillInfo):
                skill_rows.append(obj)
            elif isinstance(obj, FakeSkillCurriculum):
                curriculum_rows.append(obj)
            elif isinstance(obj, FakeTextbookExample):
                textbook_rows.append(obj)

        @staticmethod
        def commit():
            return None

        @staticmethod
        def rollback():
            return None

    class FakeDB:
        session = FakeSession()

    monkeypatch.setattr(processor, "SkillInfo", FakeSkillInfo)
    monkeypatch.setattr(processor, "SkillCurriculum", FakeSkillCurriculum)
    monkeypatch.setattr(processor, "TextbookExample", FakeTextbookExample)
    monkeypatch.setattr(processor, "db", FakeDB())
    return textbook_rows


def test_save_to_database_infers_source_page_and_renders(monkeypatch):
    app = Flask(__name__)
    tmp_root = os.path.join(os.getcwd(), "tmp_test_question_image_assets")
    os.makedirs(tmp_root, exist_ok=True)
    app.root_path = str(tmp_root)
    rows = _setup_fake_db(monkeypatch)

    calls = {"n": 0}

    def _fake_render(_pdf_path, _page_index, output_path, dpi=200):
        calls["n"] += 1
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(b"png")
        return output_path

    monkeypatch.setattr(processor, "render_pdf_page_to_image", _fake_render)

    parsed = {
        "chapters": [
            {
                "chapter_title": "第1章",
                "sections": [
                    {
                        "section_title": "1-2",
                        "concepts": [
                            {
                                "concept_name": "計數",
                                "concept_en_id": "Counting",
                                "examples": [
                                    {
                                        "example_title": "例題 7",
                                        "source_type": "textbook_example",
                                        "skill_id": "vh_數學B4_Counting",
                                        "problem_text": "如圖所示，棋盤式街道圖共有幾條路徑",
                                        "correct_answer": "20",
                                        "has_image": True,
                                        "source_page": None,
                                    }
                                ],
                                "practice_questions": [],
                            }
                        ],
                    }
                ],
            }
        ]
    }

    with app.app_context():
        processor.save_to_database(
            parsed,
            {"curriculum": "vocational", "publisher": "longteng", "grade": 10, "volume": "數學B4"},
            queue=_Q(),
            source_file_path=os.path.join(tmp_root, "book.pdf"),
            content_by_page={6: "如圖所示，棋盤式街道圖共有幾條路徑"},
        )

    row = rows[0]
    meta = json.loads(row.notes)
    assert calls["n"] == 1
    assert meta["image_assets"][0]["path"].endswith("page_006.png")
    assert meta["image_assets"][0]["source_page"] == 6
    assert meta["image_assets"][0]["source_page_inferred"] is True


def test_save_to_database_missing_source_page_keeps_empty_assets(monkeypatch):
    app = Flask(__name__)
    tmp_root = os.path.join(os.getcwd(), "tmp_test_question_image_assets_missing")
    os.makedirs(tmp_root, exist_ok=True)
    app.root_path = str(tmp_root)
    rows = _setup_fake_db(monkeypatch)

    parsed = {
        "chapters": [
            {
                "chapter_title": "第1章",
                "sections": [
                    {
                        "section_title": "1-2",
                        "concepts": [
                            {
                                "concept_name": "計數",
                                "concept_en_id": "Counting",
                                "examples": [
                                    {
                                        "example_title": "例題 8",
                                        "source_type": "textbook_example",
                                        "skill_id": "vh_數學B4_Counting",
                                        "problem_text": "附圖回答問題",
                                        "correct_answer": "10",
                                        "has_image": True,
                                        "source_page": None,
                                    }
                                ],
                                "practice_questions": [],
                            }
                        ],
                    }
                ],
            }
        ]
    }

    with app.app_context():
        processor.save_to_database(
            parsed,
            {"curriculum": "vocational", "publisher": "longteng", "grade": 10, "volume": "數學B4"},
            queue=_Q(),
            source_file_path=os.path.join(tmp_root, "book.pdf"),
            content_by_page={1: "本頁無關內容"},
        )

    meta = json.loads(rows[0].notes)
    assert meta["has_image"] is True
    assert meta["image_warning"] == "missing_source_page"
    assert meta["image_assets"] == []


def test_ui_can_distinguish_has_image_vs_missing_image_asset():
    template = open("templates/admin_examples.html", "r", encoding="utf-8").read()
    route = open("core/routes/admin.py", "r", encoding="utf-8").read()
    assert "_has_real_image_asset" in route
    assert "_missing_image_asset" in route
    assert "有附圖" in template
    assert "附圖待確認" in template
