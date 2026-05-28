from __future__ import annotations

import json
from pathlib import Path

from core.gencode.example_feature_extractor import extract_example_feature

FIXTURE = Path(__file__).parent / "fixtures" / "cartesian_source_examples.json"


def _examples() -> list[dict]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_embedded_choices_detected_as_single_choice():
    ex = _examples()[2]
    feat = extract_example_feature(ex)
    assert feat["answer_type"] == "single_choice"
    assert feat["has_choices"] is True
    assert feat["stem_embeds_choices"] is True


def test_no_choices_short_answer():
    ex = _examples()[0]
    feat = extract_example_feature(ex)
    assert feat["answer_type"] == "short_answer"
    assert feat["has_choices"] is False


def test_axis_distance_math_object():
    ex = _examples()[2]
    feat = extract_example_feature(ex)
    assert "axis_distance" in feat["math_objects"]


def test_coordinate_and_symbolic_objects():
    ex0 = extract_example_feature(_examples()[0])
    ex1 = extract_example_feature(_examples()[1])
    assert "coordinate_point" in ex0["math_objects"]
    assert "symbolic_condition" in ex0["math_objects"] or "coordinate_point" in ex0["math_objects"]
    assert "coordinate_point" in ex1["math_objects"]
    assert "symbolic_condition" in ex1["math_objects"]
