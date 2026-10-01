from __future__ import annotations

import base64
import importlib
import io
import json

import pytest
from PIL import Image, ImageDraw


CENTRAL_SKILL = "vh_數學B4_CentralTendencyMeasures"
CUMULATIVE_SKILL = "vh_數學B4_CumulativeFrequencyTablesAndGraphs"
LINEAR_SKILL = "vh_數學B4_LinearTransformationOfData"
DRAWING_SKILL = "vh_數學B4_HistogramsAndFrequencyPolygons"

CENTRAL_COMPONENTS = ("src_3835", "src_3838", "src_3839", "src_3840")
DRAWING_COMPONENTS = ("src_3826", "src_3827", "src_3828")
REGRESSION_SEEDS = tuple(range(20)) + (42, 137, 256, 999)


def _wrapper(skill_id: str):
    return importlib.import_module(f"skills.{skill_id}")


@pytest.mark.parametrize("component_id", CENTRAL_COMPONENTS)
@pytest.mark.parametrize("seed", REGRESSION_SEEDS)
def test_central_tendency_generated_oracle_matches_checker(component_id: str, seed: int) -> None:
    wrapper = _wrapper(CENTRAL_SKILL)
    payload = wrapper.generate(seed=seed, component_id=component_id)
    correct = payload["correct_answer"]

    assert payload["answer"] == correct
    assert str(correct) == str(payload["answer_contract"]["canonical_answer"])
    assert wrapper.check(correct, correct, payload) is True
    assert wrapper.check(str(float(correct) + 1), correct, payload) is False


@pytest.mark.parametrize("seed", REGRESSION_SEEDS)
def test_cumulative_table_generated_oracle_uses_student_field_keys(seed: int) -> None:
    wrapper = _wrapper(CUMULATIVE_SKILL)
    payload = wrapper.generate(seed=seed, component_id="src_3831")
    correct = payload["correct_answer"]
    part_keys = [part["key"] for part in payload["answer_contract"]["parts"]]

    assert payload["answer_type"] == "multi_part"
    assert list(correct) == part_keys
    assert wrapper.check(correct, correct, payload) is True
    wrong = dict(correct)
    wrong[part_keys[0]] = int(wrong[part_keys[0]]) + 1
    assert wrapper.check(wrong, correct, payload) is False


@pytest.mark.parametrize("seed", REGRESSION_SEEDS)
def test_src_3893_manifest_dispatch_and_runtime_resolution(seed: int) -> None:
    package = importlib.import_module(f"agent_skills_v3.{LINEAR_SKILL}")
    wrapper = _wrapper(LINEAR_SKILL)

    assert "src_3893" in package.GENERATOR_KEYS
    assert "src_3893" in wrapper.GENERATOR_KEYS
    assert any(spec["component_id"] == "src_3893" for spec in package.GENERATOR_SPECS)
    assert any(spec["component_id"] == "src_3893" for spec in wrapper.GENERATOR_SPECS)
    payload = wrapper.generate(seed=seed, component_id="src_3893")
    assert payload["component_id"] == "src_3893"
    assert wrapper.check(payload["correct_answer"], payload["correct_answer"], payload) is True


def _drawing_data_url(*, blank: bool, correct_shape: bool = True) -> str:
    image = Image.new("RGBA", (420, 280), "white")
    draw = ImageDraw.Draw(image)
    if not blank:
        if correct_shape:
            draw.line((45, 235, 385, 235), fill="black", width=3)
            draw.line((45, 235, 45, 25), fill="black", width=3)
            heights = (110, 85, 135, 175)
            points = []
            for index, height in enumerate(heights):
                left = 65 + index * 70
                right = left + 70
                top = 235 - height
                draw.rectangle((left, top, right, 235), outline="black", width=3)
                points.append(((left + right) // 2, top))
            draw.line(points, fill="blue", width=4)
        else:
            draw.line((60, 60, 360, 210), fill="red", width=8)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def _analysis(values: list[int], *, correct: bool) -> str:
    return json.dumps(
        {
            "drawing_detected": True,
            "recognized_type": "histogram_and_frequency_polygon",
            "required_elements": {
                "x_axis": correct,
                "y_axis": correct,
                "histogram_bars": correct,
                "frequency_polygon": correct,
            },
            "histogram": {
                "detected": correct,
                "bar_count": len(values) if correct else 0,
                "estimated_values": values if correct else [],
                "category_order_correct": correct,
                "baseline_correct": correct,
            },
            "frequency_polygon": {
                "detected": correct,
                "point_count": len(values) if correct else 0,
                "estimated_values": values if correct else [],
                "connected_in_order": correct,
                "points_near_category_centers": correct,
            },
            "missing_features": [] if correct else ["histogram_bars", "frequency_polygon"],
            "incorrect_features": [],
            "score": 0.95 if correct else 0.1,
            "confidence": 0.95,
            "is_correct": correct,
            "feedback": "ok" if correct else "wrong chart",
        }
    )


@pytest.mark.parametrize("component_id", DRAWING_COMPONENTS)
def test_drawing_components_accept_correct_reject_wrong_and_blank(component_id: str, monkeypatch) -> None:
    from core.services import drawing_answer_analysis_service as service

    wrapper = _wrapper(DRAWING_SKILL)
    payload = wrapper.generate(seed=7, component_id=component_id)
    expected = payload["expected_drawing_spec"]["expected_values"]
    correct_image = _drawing_data_url(blank=False, correct_shape=True)
    wrong_image = _drawing_data_url(blank=False, correct_shape=False)
    blank_image = _drawing_data_url(blank=True)

    monkeypatch.setattr(
        service,
        "_resolve_analyzer_role",
        lambda: {"available": True, "role": "vision_analyzer", "analyzer": "test"},
    )
    responses = iter((_analysis(expected, correct=True), _analysis(expected, correct=False)))
    monkeypatch.setattr(service, "_call_vision_analyzer", lambda *_args, **_kwargs: next(responses))

    def submission(image: str) -> dict[str, str]:
        return {
            "answer": "[drawing]",
            "composite_image_data_url": image,
            "student_strokes_image_data_url": image,
        }

    assert wrapper.check(submission(correct_image), payload["correct_answer"], payload) is True
    assert wrapper.check(submission(wrong_image), payload["correct_answer"], payload) is False
    assert wrapper.check(submission(blank_image), payload["correct_answer"], payload) is False
