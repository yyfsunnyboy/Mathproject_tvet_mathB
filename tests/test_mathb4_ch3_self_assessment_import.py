from flask import Flask

import core.textbook_processor as processor


class DummyQueue:
    def __init__(self):
        self.messages = []

    def put(self, msg):
        self.messages.append(msg)


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


def test_ch3_self_assessment_keeps_1_to_20_and_no_mixed_skill(monkeypatch):
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

    q_items = []
    for i in range(1, 21):
        text = f"自我評量題{i}"
        if i in (16, 18):
            text = ""
        if i == 5:
            text = "已知全距與IQR"
        if i == 6:
            text = "求母體標準差"
        if i == 7:
            text = "資料平移與伸縮後平均變化"
        q_items.append({"practice_title": f"自我評量 題{i}", "source_type": "self_assessment", "problem_text": text})

    payload = {
        "chapters": [
            {
                "chapter_title": "第3章 統計",
                "sections": [
                    {
                        "section_title": "3-3 統計量分析",
                        "concepts": [
                            {
                                "concept_name": "綜合",
                                "concept_en_id": "DispersionAndLinearTransformation",
                                "examples": [],
                                "practice_questions": q_items,
                            }
                        ],
                    }
                ],
            }
        ]
    }
    curriculum_info = {"curriculum": "vocational", "grade": 10, "volume": "數學B4"}

    with app.app_context():
        parsed = processor.parse_ai_response(payload, queue)
        result = processor.save_to_database(parsed, curriculum_info, queue)

    assert result["self_assessments_imported"] == 20
    titles = {r.source_description.split(" [")[0] for r in textbook_rows}
    assert "自我評量 題16" in titles
    assert "自我評量 題18" in titles
    assert all(r.skill_id != "vh_數學B4_DispersionAndLinearTransformation" for r in textbook_rows)
    row1 = next(r for r in textbook_rows if r.source_description.startswith("自我評量 題1 "))
    assert "needs_review=true" not in row1.source_description


def test_self_assessment_without_linked_example_not_auto_review():
    item = {"title": "自我評量 題1", "source_type": "self_assessment"}
    assert processor.normalize_source_type_by_title(item, default_source_type="in_class_practice") == "self_assessment"
