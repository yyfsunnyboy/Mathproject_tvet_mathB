import json
import os
from dataclasses import dataclass

from flask import Flask

import core.textbook_processor as processor
from core.question_image_assets import attach_image_metadata, question_needs_image


class _Q:
    def put(self, _msg):
        return None


class _Row:
    def __init__(self):
        self.notes = None


def test_question_needs_image_strong_keyword():
    assert question_needs_image("如圖所示，求陰影面積。") is True


def test_question_needs_image_pattern_tuxing_ruxia():
    assert question_needs_image("圖形如下，請判斷路徑。") is True


def test_question_needs_image_plain_tu_shi_shuoming_is_false():
    assert question_needs_image("本章圖示說明") is False


def test_attach_metadata_json_image_assets():
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
                    "image_description": "樹狀圖",
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


def test_same_page_two_questions_render_once_and_missing_source_page_flag(monkeypatch):
    app = Flask(__name__)
    tmp_root = os.path.join(os.getcwd(), "tmp_test_question_image_assets")
    os.makedirs(tmp_root, exist_ok=True)
    app.root_path = str(tmp_root)

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

    render_calls = {"n": 0}

    def _fake_render(pdf_path, page_index, output_path, dpi=200):
        render_calls["n"] += 1
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(b"png")
        return output_path

    monkeypatch.setattr(processor, "SkillInfo", FakeSkillInfo)
    monkeypatch.setattr(processor, "SkillCurriculum", FakeSkillCurriculum)
    monkeypatch.setattr(processor, "TextbookExample", FakeTextbookExample)
    monkeypatch.setattr(processor, "db", FakeDB())
    monkeypatch.setattr(processor, "render_pdf_page_to_image", _fake_render)

    parsed = {
        "chapters": [
            {
                "chapter_title": "1 章",
                "sections": [
                    {
                        "section_title": "1-1 節",
                        "concepts": [
                            {
                                "concept_name": "階乘記法",
                                "concept_en_id": "FactorialNotation",
                                "examples": [
                                    {
                                        "source_description": "例題1",
                                        "source_type": "textbook_example",
                                        "skill_id": "vh_數學B4_FactorialNotation",
                                        "problem_text": "如圖所示，求值。",
                                        "correct_answer": "1",
                                        "has_image": True,
                                        "source_page": 4,
                                    },
                                    {
                                        "source_description": "例題2",
                                        "source_type": "textbook_example",
                                        "skill_id": "vh_數學B4_FactorialNotation",
                                        "problem_text": "下圖中路徑長度。",
                                        "correct_answer": "2",
                                        "has_image": True,
                                        "source_page": 4,
                                    },
                                ],
                                "practice_questions": [
                                    {
                                        "practice_title": "隨堂練習1",
                                        "source_type": "in_class_practice",
                                        "skill_id": "vh_數學B4_FactorialNotation",
                                        "problem_text": "如圖求面積。",
                                        "correct_answer": "3",
                                        "has_image": True,
                                        "source_page": None,
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }
    curriculum_info = {"curriculum": "vocational", "publisher": "longteng", "grade": 10, "volume": "數學B4"}

    with app.app_context():
        result = processor.save_to_database(
            parsed,
            curriculum_info,
            queue=_Q(),
            source_file_path=os.path.join(tmp_root, "book.pdf"),
            content_by_page={4: "如圖所示，求值。 下圖中路徑長度。"},
        )

    assert result["examples_imported"] == 2
    assert render_calls["n"] == 1

    row1 = next(r for r in textbook_rows if r.source_description.startswith("例題1"))
    row2 = next(r for r in textbook_rows if r.source_description.startswith("例題2"))
    p1 = next(r for r in textbook_rows if r.source_description.startswith("隨堂練習1"))
    m1 = json.loads(row1.notes)
    m2 = json.loads(row2.notes)
    mp = json.loads(p1.notes)

    assert m1["image_assets"][0]["path"] == m2["image_assets"][0]["path"]
    assert m1["image_assets"][0]["path"].endswith("page_004.png")
    assert mp["needs_image_review"] is True
    assert mp["image_warning"] == "missing_source_page"
