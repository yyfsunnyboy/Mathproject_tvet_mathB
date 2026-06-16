# -*- coding: utf-8 -*-
"""Minimal tests for line equation domain operators and taxonomy registry."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from core.registry.taxonomy_registry import resolve_domain_for_skill

MATRIX_FIELDS = (
    "givens",
    "answer",
    "distractors",
    "explanation_steps",
    "validation_facts",
    "visual_spec",
)

DOMAIN_SOURCE = (
    Path(__file__).resolve().parents[2]
    / "core"
    / "domain"
    / "coordinate_geometry"
    / "line_equation_domain.py"
)

FORBIDDEN_DOMAIN_TOKENS = ("vh_", "jh_", "skill_id")


def _build(**kwargs: object) -> dict[str, object]:
    from core.domain.coordinate_geometry.line_equation_domain import (
        build_line_equation_matrix,
    )

    defaults: dict[str, object] = {
        "seed": 42,
        "line_type": "point_slope",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
    }
    defaults.update(kwargs)
    return build_line_equation_matrix(**defaults)  # type: ignore[arg-type]


def _assert_json_serializable(obj: object) -> None:
    json.dumps(obj, ensure_ascii=False)


def _gcd3(a: int, b: int, c: int) -> int:
    return math.gcd(math.gcd(abs(a), abs(b)), abs(c))


def test_matrix_has_six_json_serializable_fields():
    matrix = _build(line_type="two_points")
    assert set(matrix.keys()) >= set(MATRIX_FIELDS)
    for field in MATRIX_FIELDS:
        _assert_json_serializable(matrix[field])
    _assert_json_serializable(matrix)


def test_general_form_normalization_rules():
    for line_type in (
        "two_points",
        "point_slope",
        "horizontal_line",
        "vertical_line",
        "oblique_line",
    ):
        matrix = _build(seed=7, line_type=line_type)
        answer = matrix["answer"]
        assert isinstance(answer, dict)
        coeffs = answer["coefficients"]
        assert isinstance(coeffs, dict)
        a_val = int(coeffs["A"])
        b_val = int(coeffs["B"])
        c_val = int(coeffs["C"])
        assert a_val >= 0
        if a_val == 0:
            assert b_val > 0
        assert _gcd3(a_val, b_val, c_val) == 1
        general = str(answer["general_form"])
        assert general.endswith("= 0")
        assert "canonical_form" in answer
        assert "slope" in answer
        assert "intercept" in answer


def test_two_points_supports_oblique_horizontal_and_vertical_without_division_by_zero():
    cases = [
        {"point_a": [0, 0], "point_b": [2, 4]},
        {"point_a": [1, 3], "point_b": [1, -2]},
        {"point_a": [-2, 5], "point_b": [4, 5]},
    ]
    for constraints in cases:
        matrix = _build(
            line_type="two_points",
            seed=11,
            constraints=constraints,
        )
        facts = matrix["validation_facts"]
        assert isinstance(facts, dict)
        assert facts["points_satisfy_line"]
        coeffs = facts["coefficients"]
        assert isinstance(coeffs, dict)
        a_val = int(coeffs["A"])
        b_val = int(coeffs["B"])
        c_val = int(coeffs["C"])
        for pt in facts["points_satisfy_line"]:
            assert a_val * pt[0] + b_val * pt[1] + c_val == 0


def test_horizontal_line_canonical_form():
    matrix = _build(
        line_type="horizontal_line",
        seed=3,
        constraints={"y_intercept": 4},
    )
    answer = matrix["answer"]
    assert isinstance(answer, dict)
    assert answer["canonical_form"] == "y = 4"
    facts = matrix["validation_facts"]
    assert isinstance(facts, dict)
    assert facts["is_horizontal"] is True
    assert facts["is_vertical"] is False


def test_vertical_line_canonical_form():
    matrix = _build(
        line_type="vertical_line",
        seed=3,
        constraints={"x_intercept": -2},
    )
    answer = matrix["answer"]
    assert isinstance(answer, dict)
    assert answer["canonical_form"] == "x = -2"
    facts = matrix["validation_facts"]
    assert isinstance(facts, dict)
    assert facts["is_vertical"] is True
    assert facts["is_horizontal"] is False


def test_deterministic_for_same_seed_and_parameters():
    from core.domain.coordinate_geometry.line_equation_domain import (
        build_line_equation_matrix,
    )

    kwargs = {
        "seed": 99,
        "line_type": "oblique_line",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "medium",
    }
    first = build_line_equation_matrix(**kwargs)
    second = build_line_equation_matrix(**kwargs)
    assert first == second


def test_distractors_are_unique_and_exclude_canonical_form():
    matrix = _build(line_type="point_slope", seed=21)
    answer = matrix["answer"]
    assert isinstance(answer, dict)
    canonical = str(answer["canonical_form"])
    distractors = matrix["distractors"]
    assert isinstance(distractors, list)
    assert len(distractors) >= 3
    assert len(set(distractors)) >= 3
    assert canonical not in distractors


def test_visual_spec_is_coordinate_plane_data_only():
    matrix = _build(line_type="two_points", seed=5)
    visual = matrix["visual_spec"]
    assert isinstance(visual, dict)
    assert visual["kind"] == "coordinate_plane_spec"
    assert "points" in visual
    assert "lines" in visual
    assert "x_range" in visual
    assert "y_range" in visual
    serialized = json.dumps(visual, ensure_ascii=False)
    for forbidden in ("<svg", "<canvas", "matplotlib", "plot("):
        assert forbidden not in serialized.lower()


def test_domain_source_has_no_administrative_tokens():
    source = DOMAIN_SOURCE.read_text(encoding="utf-8")
    for token in FORBIDDEN_DOMAIN_TOKENS:
        assert token not in source


def test_resolve_domain_for_skill_returns_mapping_without_dynamic_import():
    registry_path = (
        Path(__file__).resolve().parents[2]
        / "core"
        / "registry"
        / "taxonomy_registry.py"
    )
    registry_source = registry_path.read_text(encoding="utf-8")
    assert "importlib.import_module" not in registry_source
    assert "from core.domain" not in registry_source

    resolved = resolve_domain_for_skill("vh_數學B1_PointSlopeForm")
    assert resolved["domain_module"] == (
        "core.domain.coordinate_geometry.line_equation_domain"
    )
    assert resolved["entrypoint"] == "build_line_equation_matrix"
    assert resolved["default_curriculum_profile"] == "vocational_high_b"
    assert set(resolved.keys()) == {
        "domain_module",
        "entrypoint",
        "default_curriculum_profile",
    }


def test_unknown_line_type_raises_value_error():
    from core.domain.coordinate_geometry.line_equation_domain import (
        build_line_equation_matrix,
    )

    with pytest.raises(ValueError, match="Unsupported line_type"):
        build_line_equation_matrix(
            seed=1,
            line_type="unknown_type",
            curriculum_profile="vocational_high_b",
            difficulty_profile="easy",
        )


def test_unregistered_skill_raises_key_error():
    with pytest.raises(KeyError, match="Unregistered skill_id"):
        resolve_domain_for_skill("not_a_real_skill")
