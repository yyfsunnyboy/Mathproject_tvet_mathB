from dataclasses import dataclass

from flask import Flask

import core.textbook_processor as processor


class DummyQueue:
    def __init__(self):
        self.messages = []

    def put(self, msg):
        self.messages.append(msg)


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


def test_self_assessment_skill_inference_mathb4_cases():
    sec11 = "1-1"
    sec12 = "1-2"
    assert processor.infer_mathb4_self_assessment_skill(sec11, "題1", "有一社團男生5人、女生8人，大家共推舉一位擔任社長")["clean_en_id"] == "AdditionPrinciple"
    assert processor.infer_mathb4_self_assessment_skill(sec11, "題2", "飲料種類、去冰情況、甜度及是否加珍珠")["clean_en_id"] == "MultiplicationPrinciple"
    assert processor.infer_mathb4_self_assessment_skill(sec11, "題3", "將5位男生與5位女生分組成5對男女混聲二重唱")["clean_en_id"] == "MultiplicationPrinciple"
    assert processor.infer_mathb4_self_assessment_skill(sec11, "題4", "在101到200中，三個數字都不相同者有幾個")["clean_en_id"] == "MultiplicationPrinciple"
    assert processor.infer_mathb4_self_assessment_skill(sec12, "題5", "從1、3、5、7、9五個數字中選出三個相異數字以形成三位數")["clean_en_id"] == "PermutationOfDistinctObjects"
    assert processor.infer_mathb4_self_assessment_skill(sec12, "題6", "將a、b、c、d、e、f等6個字母做直線排列，且a不排首位")["clean_en_id"] == "PermutationOfDistinctObjects"
    assert processor.infer_mathb4_self_assessment_skill(sec12, "題7", "國際歌手巡迴城市路線，先完成甲國，再到乙國")["clean_en_id"] == "PermutationOfDistinctObjects"


def test_self_assessment_import_routes_to_existing_skills_only(monkeypatch):
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
                "chapter_title": "第1章 排列與組合",
                "sections": [
                    {
                        "section_title": "1-1 加法原理與乘法原理",
                        "concepts": [
                            {
                                "concept_name": "綜合練習",
                                "concept_en_id": "MultiplicationPrinciple",
                                "examples": [],
                                "self_assessment_questions": [
                                    {"practice_title": "第1章自我評量 1-1 加法原理與乘法原理", "problem_text": "", "source_type": "self_assessment"},
                                    {"practice_title": "自我評量 題1", "problem_text": "有一社團男生5人、女生8人，大家共推舉一位擔任社長", "source_type": "self_assessment"},
                                    {"practice_title": "自我評量 題2", "problem_text": "決定茶的種類、去冰情況、甜度及是否加珍珠", "source_type": "self_assessment"},
                                    {"practice_title": "自我評量 題3", "problem_text": "將5位男生與5位女生分組成5對男女混聲二重唱", "source_type": "self_assessment"},
                                    {"practice_title": "自我評量 題4", "problem_text": "在101到200中，三個數字都不相同者有幾個", "source_type": "self_assessment"},
                                    {"practice_title": "章末自我評量 1-2 直線排列", "problem_text": "", "source_type": "self_assessment"},
                                    {"practice_title": "自我評量 題5", "problem_text": "從1、3、5、7、9五個數字中選出三個相異數字以形成三位數", "source_type": "self_assessment"},
                                    {"practice_title": "自我評量 題6", "problem_text": "將a、b、c、d、e、f等6個字母做直線排列，且a不排首位", "source_type": "self_assessment"},
                                    {"practice_title": "自我評量 題7", "problem_text": "知名歌手規劃巡迴城市路線，先完成甲國，再到乙國", "source_type": "self_assessment"},
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
        result = processor.save_to_database(parsed, curriculum_info, queue)

    rows = {r.source_description.split(" [")[0]: r for r in textbook_rows}
    assert result["self_assessments_imported"] == 7
    assert rows["自我評量 題1"].skill_id == "vh_數學B4_AdditionPrinciple"
    assert rows["自我評量 題2"].skill_id == "vh_數學B4_MultiplicationPrinciple"
    assert rows["自我評量 題3"].skill_id == "vh_數學B4_MultiplicationPrinciple"
    assert rows["自我評量 題4"].skill_id == "vh_數學B4_MultiplicationPrinciple"
    assert rows["自我評量 題5"].skill_id == "vh_數學B4_PermutationOfDistinctObjects"
    assert rows["自我評量 題6"].skill_id == "vh_數學B4_PermutationOfDistinctObjects"
    assert rows["自我評量 題7"].skill_id == "vh_數學B4_PermutationOfDistinctObjects"
    assert all("source_type=self_assessment" in r.source_description for r in rows.values())
    assert len(skill_rows) == 1
