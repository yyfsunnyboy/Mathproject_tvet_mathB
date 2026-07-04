from __future__ import annotations

import json
import random
from fractions import Fraction
from pathlib import Path

SPEC_PATH = (
    Path(__file__).resolve().parents[2]
    / "configs"
    / "gencode"
    / "source_graph_specs"
    / "src_4424.json"
)


def _load_spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_source_graph_reconstructs_confirmed_original_line() -> None:
    spec = _load_spec()
    graph = spec["source_graph"]
    assert spec["source_example_id"] == 4424
    assert spec["source_graph_status"] == "source_graph_confirmed"
    assert graph["graph_type"] == "linear_function"
    assert graph["points"] == [[4, 0], [0, -2]]
    assert graph["x_intercept"] == 4
    assert graph["y_intercept"] == -2
    assert Fraction(graph["slope"]) == Fraction(1, 2)
    assert graph["equation"] == "f(x)=1/2*x-2"
    assert graph["display_equation"] == "f(x)=1/2x-2"
    assert Fraction(1, 2) * 4 - 2 == 0
    assert Fraction(1, 2) * 0 - 2 == -2
    assert spec["traceability"]["original_values_recoverable"]
    assert (
        spec["traceability"]["source_provenance"]["kind"]
        == "user_provided_original_textbook_figure"
    )
    assert not spec["generator_template"]["is_source_graph_data"]
    assert not spec["generator_template"]["may_claim_original_values"]


def test_same_topology_template_contract() -> None:
    spec = _load_spec()
    graph = spec["source_graph"]
    template = spec["generator_template"]
    assert graph["requested"] == [
        "x_intercept",
        "y_intercept",
        "function_equation",
    ]
    assert graph["semantic_answer"] == {
        "x_intercept": 4,
        "y_intercept": -2,
        "function_equation": "f(x)=1/2x-2",
    }
    assert graph["answer_schema"] == "multi_part_intercepts_and_expression"
    assert graph["presentation_mode"] == "graph_multi_part"
    assert template["presentation_mode"] == "graph_multi_part"
    assert template["answer_schema"] == "multi_part_intercepts_and_expression"
    assert template["requested_quantity"] == [
        "x_intercept",
        "y_intercept",
        "linear_function_equation",
    ]
    assert template["parameters"]["x_intercept"]["exclude"] == [0]
    assert template["parameters"]["y_intercept"]["exclude"] == [0]
    assert template["parameters"]["slope"]["constraint"] == "nonzero"


def test_generated_intercepts_slope_equation_and_axis_range_are_consistent() -> None:
    rng = random.Random(4424)
    values = [value for value in range(-8, 9) if value != 0]
    for _ in range(20):
        x_intercept = rng.choice(values)
        y_intercept = rng.choice(values)
        slope = Fraction(-y_intercept, x_intercept)
        assert slope != 0
        points = [(x_intercept, 0), (0, y_intercept)]
        for x_value, y_value in points:
            assert slope * x_value + y_intercept == y_value

        axis_range = {
            "x_min": min(-2, x_intercept - 2),
            "x_max": max(2, x_intercept + 2),
            "y_min": min(-2, y_intercept - 2),
            "y_max": max(2, y_intercept + 2),
        }
        assert axis_range["x_min"] < x_intercept < axis_range["x_max"]
        assert axis_range["y_min"] < y_intercept < axis_range["y_max"]
        assert axis_range["x_min"] <= 0 <= axis_range["x_max"]
        assert axis_range["y_min"] <= 0 <= axis_range["y_max"]
