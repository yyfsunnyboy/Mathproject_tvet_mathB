# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pytest

from core.textbook_importer_v3_phase3_dryrun import (
    GeminiUsageTracker,
    build_b2_11_curriculum_info,
    build_dryrun_questions,
    ensure_b2_11_latex_docx,
    run_b2_11_phase3_dryrun,
)


def test_build_b2_11_curriculum_info():
    info = build_b2_11_curriculum_info(
        "第一章 1-1 角度的基本性質-課本_Latex.docx",
        "第一章 1-1 角度的基本性質-課本.docx",
    )
    assert info["curriculum"] == "vocational"
    assert info["publisher"] == "longteng"
    assert info["volume"] == "數學B2"
    assert info["section_code"] == "1-1"
    assert info["chapter_index"] == 1
    assert info["source_scope"] == "section_textbook"


def test_build_dryrun_questions_prefers_phase2_identity():
    block_meta = {
        "例1": {
            "anchor": "例1",
            "source_type": "textbook_example",
            "problem_text": "已知角 A",
            "section_code": "1-1",
            "concept_name": "角的定義",
            "formal_skill_id": "vh_數學B2_AngleDefinition",
            "detailed_solution": "解法A",
        },
        "隨堂練習1": {
            "anchor": "隨堂練習1",
            "source_type": "in_class_practice",
            "problem_text": "練習題幹",
            "section_code": "1-1",
            "formal_skill_id": "",
        },
    }
    phase3 = {
        "chapters": [
            {
                "chapter_title": "1 三角函數",
                "sections": [
                    {
                        "section_title": "1-1 角度的基本性質",
                        "concepts": [
                            {
                                "concept_name": "GeminiConcept",
                                "examples": [
                                    {
                                        "title": "例1",
                                        "correct_answer": "90",
                                        "detailed_solution": "Gemini解",
                                    }
                                ],
                                "practice_questions": [
                                    {
                                        "title": "隨堂練習1",
                                        "correct_answer": "45",
                                        "detailed_solution": "",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }
    joined = build_dryrun_questions(
        block_meta,
        phase3,
        {"curriculum": "vocational", "publisher": "longteng", "volume": "數學B2", "section_code": "1-1", "chapter_index": 1},
    )
    q0 = joined["questions"][0]
    assert q0["anchor"] == "例1"
    assert q0["source_type"] == "textbook_example"
    assert q0["problem_text"] == "已知角 A"
    assert q0["correct_answer"] == "90"
    # Phase2 solution wins over Gemini when present
    assert q0["detailed_solution"] == "解法A"
    assert q0["concept_name"] == "角的定義"
    assert q0["anchor_id"].startswith("vocational_math_B2_1-1_example_001_")
    assert joined["stats"]["anchor_collisions"] == 0
    assert joined["stats"]["no_answer"] == 0


def test_gemini_usage_tracker_records_chars_and_optional_tokens():
    tracker = GeminiUsageTracker()

    class FakeUsage:
        prompt_token_count = 11
        candidates_token_count = 7
        total_token_count = 18

    class FakeResponse:
        text = '{"ok": true}'
        usage_metadata = FakeUsage()

    class FakeModel:
        def generate_content(self, prompt, **kwargs):
            return FakeResponse()

    model = FakeModel()
    tracker.wrap_model(model)
    model.generate_content("hello world")
    summary = tracker.summary()
    assert summary["request_count"] == 1
    assert summary["input_character_count_total"] == len("hello world")
    assert summary["prompt_token_count_total"] == 11
    assert summary["total_token_count_total"] == 18
    tracker.restore()


def test_ensure_b2_11_reports_missing_when_empty(tmp_path: Path):
    result = ensure_b2_11_latex_docx(tmp_path)
    assert result["status"] == "missing_original_docx"


@pytest.mark.integration
def test_b2_11_phase3_dryrun_if_ready():
    from dotenv import load_dotenv

    load_dotenv()
    from core.ai_wrapper import resolve_gemini_api_key

    api_key, _src = resolve_gemini_api_key()
    if not api_key:
        pytest.skip("GEMINI_API_KEY / GOOGLE_API_KEY not configured")

    project_root = Path(__file__).resolve().parents[1]
    ensure = ensure_b2_11_latex_docx(project_root)
    if ensure.get("status") != "ok":
        pytest.skip(f"B2 1-1 latex unavailable: {ensure.get('status')}")

    try:
        from app import app as flask_app
    except Exception as exc:
        pytest.skip(f"Flask app unavailable: {exc}")

    result = run_b2_11_phase3_dryrun(project_root, app=flask_app)
    print(result.get("human_summary") or result)
    assert result.get("status") == "ok", result
    assert result.get("phase4_executed") is False
    assert result.get("db_committed") is False
    assert (result.get("stats") or {}).get("dryrun_questions", 0) > 0
    path = Path(result["dryrun_json_path"])
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "questions" in data
    assert data["questions"][0]["anchor_id"]
