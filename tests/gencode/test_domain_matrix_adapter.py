# -*- coding: utf-8 -*-
"""Tests for domain matrix adapter and V3 component scaffold builder."""

from __future__ import annotations

import json
import re

import pytest

from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
from core.gencode.domain_matrix_adapter import (
    convert_line_equation_matrix_to_question_payload,
    normalize_domain_matrix,
    validate_domain_matrix,
)
from core.gencode.v3_component_scaffold_builder import (
    build_component_files_from_domain_payload,
)
from core.registry.taxonomy_registry import resolve_domain_for_skill

FORBIDDEN_GENERATE_TOKENS = (
    "import sympy",
    "import matplotlib",
    "Flask",
    "db.session",
)

FORBIDDEN_MATH_PATTERNS = (
    r"\bslope\s*=",
    r"\bintercept\s*=",
    r"\(y2\s*-\s*y1\)\s*/\s*\(x2\s*-\s*x1\)",
    r"y2\s*-\s*y1",
    r"x2\s*-\s*x1",
)


def _sample_matrix(**kwargs: object) -> dict[str, object]:
    defaults: dict[str, object] = {
        "seed": 17,
        "line_type": "point_slope",
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
    }
    defaults.update(kwargs)
    return build_line_equation_matrix(**defaults)  # type: ignore[arg-type]


def _domain_and_payload_meta() -> tuple[dict[str, object], dict[str, object]]:
    domain_meta = resolve_domain_for_skill("vh_數學B1_PointSlopeForm")
    payload_meta = {
        "line_type": "point_slope",
        "target_task": "write_line_equation_from_point_slope",
        "template_slot": "line_equation_from_point_slope",
        "presentation_mode": "single_choice",
        "checker_key": "choice_label_checker",
        "equivalence_type": "choice_label",
        "answer_type": "single_choice",
        "semantic_required_concepts": ("斜率", "點斜式"),
        "math_objects": ("coordinate_point", "linear_equation"),
    }
    return domain_meta, payload_meta


def test_taxonomy_registry_resolves_point_slope_form_skill():
    resolved = resolve_domain_for_skill("vh_數學B1_PointSlopeForm")
    assert resolved["domain_module"] == (
        "core.domain.coordinate_geometry.line_equation_domain"
    )
    assert resolved["entrypoint"] == "build_line_equation_matrix"
    assert resolved["default_curriculum_profile"] == "vocational_high_b"


def test_adapter_validates_and_converts_line_equation_matrix():
    matrix = _sample_matrix()
    assert validate_domain_matrix(matrix) is True

    normalized = normalize_domain_matrix(matrix)
    json.dumps(normalized, ensure_ascii=False)

    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
    )
    assert payload["question_text"]
    assert payload["correct_answer"] == payload["answer"]
    assert payload["semantic_answer"] == matrix["answer"]["canonical_form"]
    assert isinstance(payload["choices"], list)
    assert len(payload["choices"]) >= 4
    assert payload["visual_spec"] == matrix["visual_spec"]
    assert isinstance(payload["math_core"], dict)
    assert payload["math_core"]["target"] == matrix["answer"]["canonical_form"]
    assert payload["math_core"]["derivation"] == matrix["explanation_steps"]

    choice_texts = {item["text"] for item in payload["choices"]}
    assert matrix["answer"]["canonical_form"] in choice_texts
    for distractor in matrix["distractors"]:
        assert distractor in choice_texts


def test_legacy_call_without_contract_kwargs_still_works():
    matrix = _sample_matrix()
    payload = convert_line_equation_matrix_to_question_payload(matrix)
    assert payload["presentation_mode"] == "short_answer"
    assert payload["choices"] == []


def test_accepts_presentation_mode_and_contract_kwargs():
    matrix = _sample_matrix()
    payload = convert_line_equation_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="single_choice",
        problem_type_id="write_line_equation_from_point_slope",
        component_id="src_test",
        textbook_example_id=9999,
        source_kind="ex_test",
        generator_key="src_test",
    )
    assert payload["presentation_mode"] == "single_choice"
    assert payload["problem_type_id"] == "write_line_equation_from_point_slope"
    assert payload["component_id"] == "src_test"
    assert payload["textbook_example_id"] == 9999
    assert payload["source_kind"] == "ex_test"
    assert payload["generator_key"] == "src_test"
    assert payload["metadata"]["presentation_mode"] == "single_choice"
    assert payload["answer_contract"]


def test_adapter_rejects_incomplete_matrix():
    with pytest.raises(ValueError, match="missing required fields"):
        validate_domain_matrix({"givens": {}, "answer": {}})


@pytest.mark.parametrize(
    ("source_kind", "order_weight", "difficulty_level"),
    [
        ("ex_3", 10, "easy"),
        ("quiz_5", 20, "easy"),
        ("test_2", 30, "hard"),
    ],
)
def test_scaffold_metadata_injects_source_kind_difficulty(
    source_kind: str,
    order_weight: int,
    difficulty_level: str,
):
    domain_meta, payload_meta = _domain_and_payload_meta()
    files = build_component_files_from_domain_payload(
        skill_id="vh_數學B1_PointSlopeForm",
        component_id=source_kind,
        source_kind=source_kind,
        domain_meta=domain_meta,
        payload_meta=payload_meta,
    )
    metadata_source = files["metadata.py"]
    assert f"ORDER_WEIGHT: Final[int] = {order_weight}" in metadata_source
    assert f'DIFFICULTY_LEVEL: Final[str] = "{difficulty_level}"' in metadata_source
    assert f'SOURCE_KIND: Final[str] = "{source_kind}"' in metadata_source


def test_scaffold_generate_source_has_no_forbidden_imports_or_db_access():
    domain_meta, payload_meta = _domain_and_payload_meta()
    files = build_component_files_from_domain_payload(
        skill_id="vh_數學B1_PointSlopeForm",
        component_id="ex_1",
        source_kind="ex_1",
        domain_meta=domain_meta,
        payload_meta=payload_meta,
    )
    generate_source = files["generate.py"]
    for token in FORBIDDEN_GENERATE_TOKENS:
        assert token not in generate_source


def test_scaffold_generate_source_has_no_manual_slope_intercept_derivation():
    domain_meta, payload_meta = _domain_and_payload_meta()
    files = build_component_files_from_domain_payload(
        skill_id="vh_數學B1_PointSlopeForm",
        component_id="quiz_2",
        source_kind="quiz_2",
        domain_meta=domain_meta,
        payload_meta=payload_meta,
    )
    generate_source = files["generate.py"]
    for pattern in FORBIDDEN_MATH_PATTERNS:
        assert re.search(pattern, generate_source) is None

    assert "build_line_equation_matrix" in generate_source
    assert "convert_line_equation_matrix_to_question_payload" in generate_source


def test_scaffold_get_hint_has_three_stage_semantic_skeleton():
    domain_meta, payload_meta = _domain_and_payload_meta()
    files = build_component_files_from_domain_payload(
        skill_id="vh_數學B1_PointSlopeForm",
        component_id="test_1",
        source_kind="test_1",
        domain_meta=domain_meta,
        payload_meta=payload_meta,
    )
    hint_source = files["get_hint.py"]
    assert "step=1 閱讀轉譯" in hint_source
    assert "step=2 數學建模" in hint_source
    assert "step=3 算式推導" in hint_source
    assert "if step == 1:" in hint_source
    assert "if step == 2:" in hint_source
    assert "if step == 3:" in hint_source


def test_scaffold_builder_returns_only_string_files_without_disk_write():
    domain_meta, payload_meta = _domain_and_payload_meta()
    files = build_component_files_from_domain_payload(
        skill_id="vh_數學B1_PointSlopeForm",
        component_id="ex_9",
        source_kind="ex_9",
        domain_meta=domain_meta,
        payload_meta=payload_meta,
    )
    assert set(files.keys()) == {"metadata.py", "generate.py", "get_hint.py"}
    for content in files.values():
        assert isinstance(content, str)
        assert content.strip()
