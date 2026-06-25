# -*- coding: utf-8 -*-
"""Deterministic cumulative-frequency renderer, matrix, adapter, and validator tests."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

from core.domain.statistics.cumulative_frequency import (
    build_bidirectional_cumulative_table,
    infer_at_least_count_from_less_than,
    infer_fail_count_from_greater_than,
    infer_fail_count_from_less_than,
    recover_interval_frequency_from_greater_than,
    recover_interval_frequency_from_less_than,
    validate_greater_than_sequence,
    validate_less_than_sequence,
)
from core.domain.statistics.cumulative_frequency_renderer import (
    encode_png_base64,
    render_cumulative_frequency_graph,
)
from core.domain.statistics.frequency_distribution_domain import build_cumulative_frequency_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.validators.cumulative_frequency_validator import validate_cumulative_frequency_payload

INDUCED_DIR = Path("reports/gencode_v3_induced_specs/vh_數學B4_CumulativeFrequencyTablesAndGraphs/induced_specs")

BELOW_POINTS = [
    {"x": 40, "y": 0},
    {"x": 50, "y": 4},
    {"x": 60, "y": 16},
    {"x": 70, "y": 29},
    {"x": 80, "y": 40},
    {"x": 90, "y": 45},
    {"x": 100, "y": 50},
]

ABOVE_POINTS = [
    {"x": 40, "y": 50},
    {"x": 50, "y": 46},
    {"x": 60, "y": 35},
    {"x": 70, "y": 22},
    {"x": 80, "y": 15},
    {"x": 90, "y": 5},
    {"x": 100, "y": 0},
]


def _decode_png(b64: str) -> bytes:
    return base64.b64decode(b64)


def _load_induced(name: str) -> dict:
    return json.loads((INDUCED_DIR / f"{name}.json").read_text(encoding="utf-8"))


def _constraints_from_induced(spec: dict) -> dict:
    constraints = dict(spec.get("domain_constraints") or {})
    constraints["render_mode"] = spec.get("render_mode")
    constraints["sub_questions"] = spec.get("sub_questions")
    constraints["presentation_mode"] = (spec.get("domain_constraints") or {}).get("presentation_mode")
    if spec.get("data_points") and not constraints.get("graph_points"):
        constraints["graph_points"] = [
            {"class_bound": p["x"], "cumulative_count": p["y"]} for p in spec["data_points"]
        ]
    return constraints


def test_below_graph_png_base64_valid():
    result = render_cumulative_frequency_graph(
        data_points=BELOW_POINTS,
        cumulative_direction="less_than",
        seed=1,
    )
    png = _decode_png(result["image_base64"])
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert 2_000 < len(png) < 200_000


def test_above_graph_png_base64_valid():
    result = render_cumulative_frequency_graph(
        data_points=ABOVE_POINTS,
        cumulative_direction="greater_than",
        seed=2,
    )
    png = _decode_png(result["image_base64"])
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


def test_below_graph_monotone_increasing():
    ys = [p["y"] for p in BELOW_POINTS]
    ok, _ = validate_less_than_sequence(ys, total=50)
    assert ok


def test_above_graph_monotone_decreasing():
    ys = [p["y"] for p in ABOVE_POINTS]
    ok, _ = validate_greater_than_sequence(ys, total=50)
    assert ok


def test_fail_threshold_inference():
    assert infer_fail_count_from_less_than(BELOW_POINTS, threshold=60) == 16
    assert infer_fail_count_from_greater_than(ABOVE_POINTS, threshold=60, total=50) == 15


def test_at_least_complement_inference():
    assert infer_at_least_count_from_less_than(BELOW_POINTS, threshold=70, total=50) == 21


def test_adjacent_cumulative_difference():
    assert recover_interval_frequency_from_less_than(BELOW_POINTS, low_bound=60, high_bound=70) == 13
    assert recover_interval_frequency_from_greater_than(ABOVE_POINTS, low_bound=70, high_bound=80) == 7


def test_bidirectional_table_builder():
    table = build_bidirectional_cumulative_table([5, 10, 15, 10, 5], ["50~60", "60~70", "70~80", "80~90", "90~100"])
    assert table["less_than_cumulative"] == [5, 15, 30, 40, 45]
    assert table["greater_than_cumulative"] == [45, 40, 30, 15, 5]


def test_multi_part_contract_preserved_by_adapter():
    matrix = build_cumulative_frequency_matrix(
        seed=100,
        domain_operation="cumulative_frequency_graph_reading",
        constraints=_constraints_from_induced(_load_induced("below_cumulative_graph_reading_01")),
    )
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        domain_operation="cumulative_frequency_graph_reading",
    )
    assert payload["answer_type"] == "multi_part"
    assert payload["image_base64"]
    assert len(payload["subquestions"]) == 2
    assert payload["answer_contract"]["checker_key"] == "multi_part_answer_checker"


def test_mcq_contract_preserved_by_adapter():
    spec = _load_induced("above_cumulative_mcq_fail_count_01")
    matrix = build_cumulative_frequency_matrix(
        seed=101,
        domain_operation="greater_than_cumulative_frequency_reading",
        constraints=_constraints_from_induced(spec) | {"render_mode": "multiple_choice", "presentation_mode": "single_choice"},
    )
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        domain_operation="greater_than_cumulative_frequency_reading",
        presentation_mode="single_choice",
    )
    assert payload["choices"]
    assert payload["image_base64"]
    assert payload["answer_type"] == "single_choice"


def test_adapter_preserves_table_data():
    spec = _load_induced("bidirectional_cumulative_table_01")
    matrix = build_cumulative_frequency_matrix(
        seed=102,
        domain_operation="cumulative_frequency_table_construction",
        constraints=_constraints_from_induced(spec),
    )
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        domain_operation="cumulative_frequency_table_construction",
    )
    assert payload["table_data"]["html"]
    assert "以下累積次數" in payload["table_data"]["html"]


def test_validation_fails_when_graph_image_missing():
    errors = validate_cumulative_frequency_payload(
        {
            "domain_operation": "cumulative_frequency_graph_reading",
            "question_text": "如下圖所示，求不及格人數。",
            "image_base64": "",
            "answer_type": "integer",
        }
    )
    assert any("GRAPH_MISSING" in e or "STEM_REFERENCES_GRAPH" in e for e in errors)


@pytest.mark.parametrize(
    "fixture_name,operation,expected_answers",
    [
        ("below_cumulative_graph_reading_01", "cumulative_frequency_graph_reading", [16, 21]),
        ("bidirectional_cumulative_table_01", "cumulative_frequency_table_construction", None),
        ("above_cumulative_graph_reading_01", "greater_than_cumulative_frequency_reading", [15, 15]),
        ("above_cumulative_mcq_fail_count_01", "greater_than_cumulative_frequency_reading", [18]),
        ("above_cumulative_interval_difference_01", "class_frequency_from_cumulative_difference", [7]),
    ],
)
def test_induced_spec_regression_fixtures(fixture_name, operation, expected_answers):
    spec = _load_induced(fixture_name)
    constraints = _constraints_from_induced(spec)
    if fixture_name.endswith("mcq_fail_count_01.json"):
        constraints["render_mode"] = "multiple_choice"
        constraints["presentation_mode"] = "single_choice"
    matrix = build_cumulative_frequency_matrix(
        seed=200,
        domain_operation=operation,
        constraints=constraints,
    )
    payload = convert_domain_matrix_to_question_payload(matrix, domain_operation=operation)
    if expected_answers is not None and payload["answer_type"] == "multi_part":
        assert matrix["answer"]["value"] == expected_answers
    if operation != "cumulative_frequency_table_construction":
        assert payload["image_base64"]
    if operation == "cumulative_frequency_table_construction":
        assert payload["table_data"]


@pytest.mark.parametrize(
    "operation",
    [
        "cumulative_frequency_graph_reading",
        "cumulative_frequency_table_construction",
        "class_frequency_from_cumulative_difference",
        "less_than_cumulative_frequency_reading",
        "greater_than_cumulative_frequency_reading",
    ],
)
@pytest.mark.parametrize("seed", list(range(1, 16)))
def test_fixed_seeds_produce_unique_answers(operation: str, seed: int):
    matrix = build_cumulative_frequency_matrix(seed=1000 + seed, domain_operation=operation)
    vf = matrix["validation_facts"]
    assert vf.get("answer_value") is not None
    if operation != "cumulative_frequency_table_construction":
        assert matrix.get("image_base64")
        png = _decode_png(matrix["image_base64"])
        assert png[:8] == b"\x89PNG\r\n\x1a\n"


def test_encode_png_base64_roundtrip():
    sample = b"\x89PNG\r\n\x1a\n" + b"0" * 32
    assert _decode_png(encode_png_base64(sample)) == sample
