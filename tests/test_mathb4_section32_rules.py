from flask import Flask

import core.textbook_processor as processor


class DummyQueue:
    def __init__(self):
        self.messages = []

    def put(self, msg):
        self.messages.append(msg)


def test_mathb32_remap_rules():
    ex1 = {"problem_text": "已知全距、組距與組中點，完成次數分配表"}
    ex2 = {"problem_text": "依次數分配表畫直方圖與次數分配折線圖"}
    ex3 = {"problem_text": "完成以下累積次數分配表，並畫以上累積次數分配折線圖"}
    ex4 = {"problem_text": "由長條圖判讀至少幾人與區間人數"}
    assert processor.remap_mathb32_non_skill_examples("3-2 統計資料整理", "綜合題", "review", ex1) == "DataOrganizationAndTables"
    assert processor.remap_mathb32_non_skill_examples("3-2 統計資料整理", "綜合題", "review", ex2) == "FrequencyDistributionGraphs"
    assert processor.remap_mathb32_non_skill_examples("3-2 統計資料整理", "綜合題", "review", ex3) == "CumulativeFrequencyDistribution"
    assert processor.remap_mathb32_non_skill_examples("3-2 統計資料整理", "綜合題", "review", ex4) == "StatisticalChartReading"


def test_section32_exercises_fully_kept():
    payload = {
        "chapters": [
            {
                "chapter_title": "第4章 統計",
                "sections": [
                    {
                        "section_title": "3-2 統計資料整理",
                        "concepts": [
                            {
                                "concept_name": "綜合",
                                "concept_en_id": "review",
                                "examples": [],
                                "exercises": [
                                    {"source_description": f"3-2習題 基礎題{i}", "problem_text": f"基礎題{i} 題幹", "source_type": "basic_exercise"}
                                    for i in range(1, 9)
                                ]
                                + [
                                    {"source_description": "3-2習題 進階題9", "problem_text": "如下圖，請判讀資料", "source_type": "advanced_exercise"},
                                    {"source_description": "3-2習題 進階題10", "problem_text": "如下圖，請判讀資料", "source_type": "advanced_exercise"},
                                ],
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
    practice = concept.get("practice_questions", [])
    assert len(practice) >= 10
    titles = {str(x.get("source_description", "")) for x in practice}
    for i in range(1, 9):
        assert f"3-2習題 基礎題{i}" in titles
    assert "3-2習題 進階題9" in titles
    assert "3-2習題 進階題10" in titles
