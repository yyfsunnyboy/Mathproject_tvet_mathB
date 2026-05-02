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


def test_ch2_mapping_set_probability_expectation():
    set_case = processor.infer_mathb4_ch2_self_assessment_skill(
        "第2章 機率", "2-1 樣本空間與事件", "自我評量 題1", "已知 A \\subset B，求 A \\cap B"
    )
    assert set_case["skill_id"] in ("vh_數學B4_BasicConceptsOfSets", "vh_數學B4_SetOperations")

    prob_case = processor.infer_mathb4_ch2_self_assessment_skill(
        "第2章 機率", "2-2 機率的運算", "自我評量 題2", "已知 P(A \\cup B)，求其值"
    )
    assert prob_case["skill_id"] == "vh_數學B4_ProbabilityProperties"

    exp_case = processor.infer_mathb4_ch2_self_assessment_skill(
        "第2章 機率", "2-4 期望值", "自我評量 題3", "某遊戲平均獲利與公平性判斷"
    )
    assert exp_case["skill_id"] in ("vh_數學B4_ApplicationsOfExpectation", "vh_數學B4_MathematicalExpectation")


def test_probability_notation_wrap_and_permutation_unchanged():
    fixed, _ = processor.normalize_probability_event_notation("P(A \\cap B)")
    assert fixed == "\\(P(A \\cap B)\\)"
    p_fixed, _ = processor.normalize_probability_event_notation("P^{5}_{3}")
    assert p_fixed == "P^{5}_{3}"


def test_self_assessment_without_linked_example_not_forced_needs_review(monkeypatch):
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

    payload = {
        "chapters": [
            {
                "chapter_title": "第2章 機率",
                "sections": [
                    {
                        "section_title": "2-2 機率的運算",
                        "concepts": [
                            {
                                "concept_name": "機率",
                                "concept_en_id": "ProbabilityProperties",
                                "examples": [],
                                "practice_questions": [
                                    {
                                        "practice_title": "自我評量 題1",
                                        "source_type": "self_assessment",
                                        "problem_text": "設A、B為兩事件，已知 P(A \\cap B)=0.2，求 P(A \\cup B)",
                                    }
                                ],
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
        processor.save_to_database(parsed, curriculum_info, queue)

    assert len(textbook_rows) == 1
    row = textbook_rows[0]
    assert "source_type=self_assessment" in row.source_description
    assert "needs_review=true" not in row.source_description
