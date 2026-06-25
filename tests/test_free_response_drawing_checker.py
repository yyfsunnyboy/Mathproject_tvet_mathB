from __future__ import annotations

from core.checkers.free_response_drawing_checker import (
    check_drawing_answer,
    find_answer_image,
    find_student_strokes_image,
    normalize_answer_image,
)
from core.gencode.answer_grading import should_use_contract_aware_grading
from core.gencode.runtime_skill_wrapper import check_answer


PNG_1X1 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


def _drawing_payload(**overrides):
    payload = {
        "skill_id": "vh_數學B4_HistogramsAndFrequencyPolygons",
        "problem_type_id": "frequency_distribution_chart_construction",
        "question_text": "Draw a histogram and frequency polygon.",
        "correct_answer": "draw the chart",
        "answer_contract": {
            "answer_type": "drawing",
            "checker": "free_response_drawing_checker",
            "answer_equivalence": "drawing_equivalence",
        },
        "expected_drawing_spec": {
            "drawing_type": "histogram_and_frequency_polygon",
            "expected_values": [8, 4, 4, 7],
            "required_elements": ["x_axis", "y_axis", "histogram_bars", "frequency_polygon"],
        },
    }
    payload.update(overrides)
    return payload


def test_normalize_answer_image_accepts_canvas_aliases():
    assert normalize_answer_image({"image_data_url": f"data:image/png;base64,{PNG_1X1}"}) == (
        f"data:image/png;base64,{PNG_1X1}"
    )
    assert normalize_answer_image({"image_base64": PNG_1X1}) == f"data:image/png;base64,{PNG_1X1}"
    assert normalize_answer_image({"canvas_image": PNG_1X1}) == f"data:image/png;base64,{PNG_1X1}"
    assert normalize_answer_image({"drawing_image": PNG_1X1}) == f"data:image/png;base64,{PNG_1X1}"


def test_drawing_image_aliases_prefer_composite_and_strokes():
    image, field = find_answer_image(
        {
            "image_data_url": f"data:image/png;base64,{PNG_1X1}",
            "composite_image_data_url": f"data:image/png;base64,{PNG_1X1}",
            "student_strokes_image_data_url": f"data:image/png;base64,{PNG_1X1}",
        }
    )
    strokes, strokes_field = find_student_strokes_image(
        {"student_strokes_image_data_url": f"data:image/png;base64,{PNG_1X1}"}
    )

    assert field == "composite_image_data_url"
    assert image.startswith("data:image/png;base64,")
    assert strokes_field == "student_strokes_image_data_url"
    assert strokes.startswith("data:image/png;base64,")


def test_drawing_contract_uses_drawing_checker_not_text_or_numeric(monkeypatch):
    calls = []

    def fake_analyze(**kwargs):
        calls.append(kwargs)
        return {
            "is_correct": True,
            "score": 0.93,
            "confidence": 0.9,
            "feedback": "ok",
            "recognized_features": {"bars": {"estimated_values": [8, 4, 4, 7]}},
        }

    monkeypatch.setattr(
        "core.services.drawing_answer_analysis_service.analyze_drawing",
        fake_analyze,
    )
    payload = _drawing_payload(image_base64=PNG_1X1)

    assert check_answer("", "not an integer", payload=payload) is True
    assert calls
    assert calls[0]["image_data_url"].startswith("data:image/png;base64,")
    assert calls[0]["expected_drawing_spec"]["expected_values"] == [8, 4, 4, 7]


def test_missing_drawing_image_stays_in_drawing_path():
    result = check_drawing_answer(
        image_data_url=None,
        question_text="Draw a chart.",
        answer_contract={"checker": "free_response_drawing_checker"},
        metadata={},
        expected_drawing_spec={"drawing_type": "histogram"},
    )

    assert result["checker"] == "free_response_drawing_checker"
    assert result["is_correct"] is None
    assert result["feedback"] == "missing_drawing_image"
    assert result["missing_features"] == ["drawing_image"]


def test_unsupported_drawing_type_does_not_fallback_to_text():
    result = check_drawing_answer(
        image_data_url=f"data:image/png;base64,{PNG_1X1}",
        question_text="Draw something.",
        answer_contract={"checker": "free_response_drawing_checker"},
        metadata={},
        expected_drawing_spec={"drawing_type": "unknown_visual_type"},
    )

    assert result["checker"] == "free_response_drawing_checker"
    assert result["is_correct"] is None
    assert result["feedback"] == "unsupported_drawing_type"
    assert result["incorrect_features"] == ["unknown_visual_type"]


def test_missing_drawing_spec_is_configuration_error():
    result = check_drawing_answer(
        image_data_url=f"data:image/png;base64,{PNG_1X1}",
        question_text="Draw a chart.",
        answer_contract={"checker": "free_response_drawing_checker"},
        metadata={},
        expected_drawing_spec={},
    )

    assert result["is_correct"] is None
    assert result["status"] == "missing_spec"
    assert result["system_error"] is True


def test_analyzer_unavailable_does_not_mark_non_empty_image_correct(monkeypatch):
    monkeypatch.setattr(
        "core.services.drawing_answer_analysis_service._is_blank_png",
        lambda _b: False,
    )
    monkeypatch.setattr(
        "core.services.drawing_answer_analysis_service._resolve_analyzer_role",
        lambda: {"available": False, "analyzer": "vision_analyzer:unavailable"},
    )
    result = check_drawing_answer(
        image_data_url=f"data:image/png;base64,{PNG_1X1}",
        question_text="Draw a chart.",
        answer_contract={"checker": "free_response_drawing_checker"},
        metadata={},
        expected_drawing_spec={"drawing_type": "histogram"},
    )

    assert result["is_correct"] is None
    assert result["status"] == "analysis_unavailable"
    assert result["system_error"] is True


def test_grading_facade_treats_drawing_as_contract_aware():
    assert should_use_contract_aware_grading(_drawing_payload()) is True
