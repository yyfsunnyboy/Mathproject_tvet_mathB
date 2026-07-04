from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest

from adapter import adapt_matrix_to_component_payload, check_multi_part_answer
from operation import build_graph_intercepts_and_linear_equation_matrix

from core.gencode.services.v3_question_integrity_validator import (
    validate_component_payload,
)

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SOURCE_SPEC = PROJECT_ROOT / "configs" / "gencode" / "source_graph_specs" / "src_4424.json"
PRODUCTION_FILES = (
    PROJECT_ROOT / "core" / "registry" / "domain_operation_registry.py",
    PROJECT_ROOT / "core" / "domain" / "coordinate_geometry" / "line_equation_domain.py",
    PROJECT_ROOT / "instance" / "kumon_math.db",
)
FIXED_SEEDS = (4424, 4425, 4426, 4427, 4428)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_oblique_horizontal_vertical_and_rational_lines() -> None:
    cases = (
        ({"coefficients": ["1/2", "1", "-2"]}, "oblique", "4", "2"),
        ({"line_kind": "horizontal", "axis_offset": "3/2"}, "horizontal", None, "3/2"),
        ({"line_kind": "vertical", "axis_offset": "-5/3"}, "vertical", "-5/3", None),
    )
    for constraints, kind, expected_x, expected_y in cases:
        matrix = build_graph_intercepts_and_linear_equation_matrix(
            seed=1,
            constraints=constraints,
        )
        assert matrix["validation_facts"]["line_kind"] == kind
        assert matrix["semantic_answer"]["x_intercept"] == expected_x
        assert matrix["semantic_answer"]["y_intercept"] == expected_y


@pytest.mark.parametrize(
    "constraints",
    (
        {"coefficients": [0, 0, 1]},
        {"coefficients": ["bad", 1, 2]},
        {"line_kind": "horizontal", "axis_offset": 0},
        {"line_kind": "vertical", "axis_offset": 0},
        {"line_kind": "curve"},
        {"line_kind": "oblique", "x_intercept": 0, "y_intercept": 2},
    ),
)
def test_illegal_or_degenerate_inputs_are_rejected(
    constraints: dict[str, object],
) -> None:
    with pytest.raises(ValueError):
        build_graph_intercepts_and_linear_equation_matrix(
            seed=1,
            constraints=constraints,
        )


def test_src_4424_fixed_seeds_contract_checker_and_validator() -> None:
    source = json.loads(SOURCE_SPEC.read_text(encoding="utf-8"))
    topology = source["generator_template"]
    required_tags = set(topology["topology_tags"])

    for seed in FIXED_SEEDS:
        matrix = build_graph_intercepts_and_linear_equation_matrix(
            seed=seed,
            constraints={"line_kind": "oblique"},
        )
        payload = adapt_matrix_to_component_payload(
            matrix,
            component_ref=source["source_ref"],
            source_example_ref=source["source_example_id"],
        )
        answer = payload["semantic_answer"]
        slope = Fraction(matrix["validation_facts"]["slope"])
        x_intercept = Fraction(answer["x_intercept"])
        y_intercept = Fraction(answer["y_intercept"])

        assert slope * x_intercept + y_intercept == 0
        assert payload["answer"] == payload["correct_answer"] == answer
        assert topology["answer_schema"].startswith(payload["answer_type"])
        assert payload["presentation_mode"] == topology["presentation_mode"]
        assert required_tags <= set(payload["topology_tags"])
        assert check_multi_part_answer(dict(answer), answer)
        wrong = dict(answer)
        wrong["x_intercept"] = str(x_intercept + 1)
        assert not check_multi_part_answer(wrong, answer)
        integrity = validate_component_payload(payload, component_id=source["source_ref"])
        assert integrity["passed"], integrity["blockers"]


def test_confirmed_src_4424_values_are_reconstructed() -> None:
    source = json.loads(SOURCE_SPEC.read_text(encoding="utf-8"))
    graph = source["source_graph"]
    matrix = build_graph_intercepts_and_linear_equation_matrix(
        constraints={
            "x_intercept": graph["x_intercept"],
            "y_intercept": graph["y_intercept"],
        }
    )
    assert matrix["semantic_answer"] == {
        "x_intercept": "4",
        "y_intercept": "-2",
        "function_equation": "f(x)=1/2x-2",
        "line_equation": "f(x)=1/2x-2",
    }


def test_production_files_are_not_workspace_outputs() -> None:
    before = {str(path): _digest(path) for path in PRODUCTION_FILES}
    build_graph_intercepts_and_linear_equation_matrix(seed=4424)
    after = {str(path): _digest(path) for path in PRODUCTION_FILES}
    assert after == before
