from flask import Flask

import core.textbook_processor as processor


class DummyQueue:
    def __init__(self):
        self.messages = []

    def put(self, msg):
        self.messages.append(msg)


def test_section31_exercises_are_fully_kept_in_practice_questions():
    payload = {
        "chapters": [
            {
                "chapter_title": "第4章 統計",
                "sections": [
                    {
                        "section_title": "3-1 統計的基本概念",
                        "concepts": [
                            {
                                "concept_name": "綜合",
                                "concept_en_id": "review",
                                "examples": [],
                                "exercises": [
                                    {"source_description": f"3-1習題 基礎題{i}", "problem_text": f"基礎題{i} 題幹", "source_type": "basic_exercise"}
                                    for i in range(1, 9)
                                ]
                                + [
                                    {"source_description": "3-1習題 進階題9", "problem_text": "請問下圖是何種抽樣法？", "source_type": "advanced_exercise"},
                                    {"source_description": "3-1習題 進階題10", "problem_text": "請問下圖是何種抽樣法？", "source_type": "advanced_exercise"},
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
        assert f"3-1習題 基礎題{i}" in titles
    assert "3-1習題 進階題9" in titles
    assert "3-1習題 進階題10" in titles
