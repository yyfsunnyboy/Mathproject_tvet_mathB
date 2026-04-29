from dataclasses import dataclass

from flask import Flask

import core.textbook_processor as processor


class DummyQueue:
    def __init__(self):
        self.messages = []

    def put(self, msg):
        self.messages.append(msg)


def _sample_ai_payload():
    return {
        "chapters": [
            {
                "chapter_title": "1 排列組合",
                "sections": [
                    {
                        "section_title": "1-1 加法原理與乘法原理",
                        "concepts": [
                            {
                                "concept_name": "乘法原理",
                                "concept_en_id": "MultiplicationPrinciple",
                                "concept_description": "乘法原理",
                                "examples": [
                                    {
                                        "example_title": "例題4",
                                        "problem": "試問 600 = 2^3 \\times 3^1 \\times 5^2 的正因數共有幾個？",
                                        "answer": "24",
                                        "solution": "故 600 的正因數共有 4 \\times 2 \\times 3 = 24 個。",
                                        "source_type": "textbook_example",
                                        "skill_id": "vh_數學B4_MultiplicationPrinciple",
                                        "followup_practices": [
                                            {
                                                "practice_title": "隨堂練習4",
                                                "problem": "試問 1080 = 2^3 \\times 3^3 \\times 5^1 的正因數共有幾個？",
                                                "answer": "32",
                                                "solution": "故 1080 的正因數共有 4 \\times 4 \\times 2 = 32 個。",
                                            }
                                        ],
                                    }
                                ],
                                "practice_questions": [
                                    {
                                        "practice_title": "隨堂練習5",
                                        "problem": "試問 720 = 2^4 \\times 3^2 \\times 5^1 的正因數共有幾個？",
                                        "answer": "30",
                                        "solution": "故 720 的正因數共有 5 \\times 3 \\times 2 = 30 個。",
                                        "source_type": "in_class_practice",
                                        "linked_example_title": "例題4",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }


def test_parse_ai_response_splits_practice_questions_and_followups():
    app = Flask(__name__)
    queue = DummyQueue()
    with app.app_context():
        parsed = processor.parse_ai_response(_sample_ai_payload(), queue)

    concept = parsed["chapters"][0]["sections"][0]["concepts"][0]
    assert len(concept["examples"]) == 1
    assert len(concept["practice_questions"]) == 2

    followup = concept["practice_questions"][0]
    assert followup["source_type"] == "in_class_practice"
    assert followup["linked_example_title"] == "例題4"
    assert followup["problem_text"].count("\\times") >= 1


@dataclass
class _FakeRow:
    values: dict

    def __getattr__(self, item):
        return self.values.get(item)

    def __setattr__(self, key, value):
        if key == "values":
            super().__setattr__(key, value)
        else:
            self.values[key] = value


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


def test_save_to_database_imports_independent_practice_and_no_skill_creation(monkeypatch):
    app = Flask(__name__)
    queue = DummyQueue()

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

    curriculum_info = {"curriculum": "vocational", "grade": 10, "volume": "數學B第四冊"}

    with app.app_context():
        parsed = processor.parse_ai_response(_sample_ai_payload(), queue)
        result_first = processor.save_to_database(parsed, curriculum_info, queue)
        result_second = processor.save_to_database(parsed, curriculum_info, queue)

    assert result_first["examples_imported"] == 1
    assert result_first["practice_questions_imported"] == 2
    assert result_first["in_class_practices_imported"] == 2
    assert result_second["practice_questions_skipped"] >= 1

    # example + 2 practices are independent rows in textbook_examples
    assert len(textbook_rows) == 3

    practice_rows = [r for r in textbook_rows if "source_type=in_class_practice" in r.source_description]
    assert len(practice_rows) == 2
    assert all("linked_example=例題4" in r.source_description for r in practice_rows)
    assert all(r.skill_id == "vh_數學B4_MultiplicationPrinciple" for r in practice_rows)

    # No additional skill created from title "隨堂練習"
    assert all("隨堂練習" not in s.skill_id for s in skill_rows)
