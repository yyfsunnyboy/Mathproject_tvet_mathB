from flask import Flask

import core.textbook_processor as processor


class DummyQueue:
    def __init__(self):
        self.messages = []

    def put(self, msg):
        self.messages.append(msg)


def test_mathb33_remap_rules():
    assert processor.remap_mathb33_non_skill_examples("3-3 統計量分析", "綜合題", "review", {"problem_text": "平均數、中位數、眾數"}) == "CentralTendencyMeasures"
    assert processor.remap_mathb33_non_skill_examples("3-3 統計量分析", "綜合題", "review", {"problem_text": "學分加權平均與權數"}) == "WeightedMean"
    assert processor.remap_mathb33_non_skill_examples("3-3 統計量分析", "綜合題", "review", {"problem_text": "Q_1、Q_3 與 IQR"}) == "DispersionMeasures"
    assert processor.remap_mathb33_non_skill_examples("3-3 統計量分析", "綜合題", "review", {"problem_text": "母體變異數與樣本標準差"}) == "VarianceAndStandardDeviation"
    assert processor.remap_mathb33_non_skill_examples("3-3 統計量分析", "綜合題", "review", {"problem_text": "x'_i = ax_i + b 的平移伸縮"}) == "LinearTransformationOfData"
    assert processor.remap_mathb33_non_skill_examples("3-3 統計量分析", "綜合題", "review", {"problem_text": "常態分配 68-95-99.7 法則"}) == "NormalDistributionAndEmpiricalRule"
    assert processor.remap_mathb33_non_skill_examples("3-3 統計量分析", "綜合題", "review", {"problem_text": "民調信心水準與抽樣誤差"}) == "OpinionPollInterpretation"


def test_section33_exercises_full_retention():
    payload = {
        "chapters": [
            {
                "chapter_title": "第4章 統計",
                "sections": [
                    {
                        "section_title": "3-3 統計量分析",
                        "concepts": [
                            {
                                "concept_name": "綜合",
                                "concept_en_id": "review",
                                "examples": [{"source_description": f"例題{i}", "problem_text": f"例題{i} 題幹"} for i in range(1, 12)],
                                "practice_questions": [{"source_description": f"隨堂練習{i}", "problem_text": f"隨堂{i} 題幹"} for i in range(1, 12)],
                                "exercises": [{"source_description": f"3-3習題 基礎題{i}", "problem_text": f"基礎題{i} 題幹"} for i in range(1, 9)]
                                + [{"source_description": "3-3習題 進階題9", "problem_text": "題幹9"}, {"source_description": "3-3習題 進階題10", "problem_text": "題幹10"}],
                            }
                        ],
                    }
                ],
            }
        ]
    }
    app = Flask(__name__)
    with app.app_context():
        parsed = processor.parse_ai_response(payload, DummyQueue())
    concept = parsed["chapters"][0]["sections"][0]["concepts"][0]
    assert len(concept.get("examples", [])) >= 11
    assert len(concept.get("practice_questions", [])) >= 21
