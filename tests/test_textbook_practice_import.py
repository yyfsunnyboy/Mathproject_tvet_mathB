from dataclasses import dataclass

from flask import Flask

import core.textbook_processor as processor


class DummyQueue:
    def __init__(self):
        self.messages = []

    def put(self, msg):
        self.messages.append(msg)


def _make_item(title, source_type=None):
    item = {"title": title}
    if source_type is not None:
        item["source_type"] = source_type
    return item


def test_normalize_source_type_by_title_rules():
    assert processor.normalize_source_type_by_title(_make_item("隨堂練習4", "textbook_example")) == "in_class_practice"
    assert processor.normalize_source_type_by_title(_make_item("統測補給站 例題3", "textbook_example")) == "exam_practice"
    assert processor.normalize_source_type_by_title(_make_item("統測題")) == "exam_practice"
    assert processor.normalize_source_type_by_title(_make_item("基礎題5")) == "basic_exercise"
    assert processor.normalize_source_type_by_title(_make_item("進階題10")) == "advanced_exercise"
    assert processor.normalize_source_type_by_title(_make_item("1-1 習題 3")) == "chapter_exercise"
    assert processor.normalize_source_type_by_title(_make_item("自我評量第 23 題")) == "self_assessment"
    assert processor.normalize_source_type_by_title(_make_item("例題5")) == "textbook_example"


def test_invalid_source_type_falls_back_to_textbook_practice_and_needs_review():
    item = _make_item("一般題目", "bad_type")
    assert processor.normalize_source_type_by_title(item) == "textbook_practice"
    assert item["needs_review"] is True


def _payload_for_routing():
    return {
        "chapters": [
            {
                "chapter_title": "第1章 排列組合",
                "sections": [
                    {
                        "section_title": "1-1 計數原理",
                        "concepts": [
                            {
                                "concept_name": "階乘",
                                "concept_en_id": "FactorialNotation",
                                "examples": [
                                    {"example_title": "例題5", "problem": "試求下列各式之值：", "source_type": "textbook_example", "sub_questions": [{"label": "1", "problem": "3!", "answer": "6"}]},
                                    {"example_title": "例題12", "problem": "試求", "source_type": "textbook_example"},
                                    {"example_title": "隨堂練習4", "problem": "試求下列各式之值：", "source_type": "textbook_example", "sub_questions": [{"label": "1", "problem": "4!", "answer": "24"}]},
                                    {"example_title": "統測補給站 例題3", "problem": "某題", "source_type": "textbook_example"},
                                ],
                                "practice_questions": [
                                    {"practice_title": "隨堂練習12", "problem": "試求", "source_type": "textbook_example", "sub_questions": [{"label": "1", "problem": "6!", "answer": "720"}]},
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }


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


def test_parse_ai_response_normalizes_and_routes_by_title():
    app = Flask(__name__)
    with app.app_context():
        parsed = processor.parse_ai_response(_payload_for_routing(), DummyQueue())

    concept = parsed["chapters"][0]["sections"][0]["concepts"][0]
    example_titles = [x["source_description"] for x in concept["examples"]]
    practice_titles = [x["source_description"] for x in concept["practice_questions"]]
    assert "例題5" in example_titles
    assert "隨堂練習4" not in example_titles
    assert "隨堂練習4" in practice_titles
    assert "統測補給站 例題3" in practice_titles
    p12 = next(x for x in concept["practice_questions"] if x["source_description"] == "隨堂練習12")
    assert p12["source_type"] == "in_class_practice"


def test_dedupe_and_summary_use_normalized_source_type(monkeypatch):
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

    payload = _payload_for_routing()
    curriculum_info = {"curriculum": "vocational", "grade": 10, "volume": "數學B4"}

    with app.app_context():
        parsed = processor.parse_ai_response(payload, queue)
        result = processor.save_to_database(parsed, curriculum_info, queue)

    assert result["textbook_examples_imported"] == 2
    assert result["in_class_practices_imported"] == 2
    assert result["exam_practices_imported"] == 1
    assert result["chapter_exercises_imported"] == 0
    assert result["self_assessments_imported"] == 0
    assert result["practice_questions_imported"] == 3

    rows_by_title = {r.source_description.split(" [")[0]: r for r in textbook_rows}
    assert "source_type=textbook_example" in rows_by_title["例題5"].source_description
    assert "source_type=textbook_example" in rows_by_title["例題12"].source_description
    assert "source_type=in_class_practice" in rows_by_title["隨堂練習4"].source_description
    assert "source_type=exam_practice" in rows_by_title["統測補給站 例題3"].source_description
    assert "linked_example=例題12" in rows_by_title["隨堂練習12"].source_description


def test_in_class_practice_missing_exact_example_falls_back_previous(monkeypatch):
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

    payload = _payload_for_routing()
    concepts = payload["chapters"][0]["sections"][0]["concepts"][0]
    concepts["examples"] = [e for e in concepts["examples"] if e.get("example_title") != "例題12"]
    curriculum_info = {"curriculum": "vocational", "grade": 10, "volume": "數學B4"}

    with app.app_context():
        parsed = processor.parse_ai_response(payload, queue)
        processor.save_to_database(parsed, curriculum_info, queue)

    rows_by_title = {r.source_description.split(" [")[0]: r for r in textbook_rows}
    assert "linked_example=例題5" in rows_by_title["隨堂練習12"].source_description
    assert "needs_review=true" in rows_by_title["隨堂練習12"].source_description
