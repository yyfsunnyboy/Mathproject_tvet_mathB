# -*- coding: utf-8 -*-
"""Isolated dry-run tests for V3 component draft hook."""

from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from core.gencode.pipeline_orchestrator import build_v3_component_draft_from_skill

FORBIDDEN_GENERATE_TOKENS = (
    "import sympy",
    "import matplotlib",
    "Flask",
    "db.session",
    "textbook_examples",
    "SkillInfo",
)

FORBIDDEN_MATH_HELPER_TOKENS = (
    "_compute_slope",
    "_build_distractors",
    "gcd(",
    "Fraction(",
)

POINT_SLOPE_TEXTBOOK_ROW = {
    "id": 1,
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_text": "已知點 $(1,2)$ 與斜率 $3$，求直線方程式。",
    "correct_answer": "$y-2=3(x-1)$",
    "source_description": "例題1",
    "problem_type": "point_slope",
}
POINT_SLOPE_CONSTRAINTS = {
    "line_type": "point_slope",
    "problem_type_id": "point_slope",
    "domain_operation": "point_slope",
}

RATIONAL_NUMBERS_ROW = {
    "id": 12280,
    "skill_id": "gh_RationalNumbers",
    "problem_text": "下列何者為有理數？",
    "correct_answer": "",
    "source_description": "基礎題1",
    "problem_type": "identify_rational_numbers",
}

SOURCE_CONSTRAINED_CANDIDATE_VARIANTS = {
    "generation_constraints": {
        "variants": [
            {"constraints": {"candidates": [
                {"kind": "rational", "value": "-1/2"},
                {"kind": "sqrt", "radicand": 2},
            ]}},
            {"constraints": {"candidates": [
                {"kind": "finite_decimal", "value": "3.14"},
                {"kind": "sum", "terms": [
                    {"kind": "rational", "value": "1"},
                    {"kind": "sqrt", "radicand": 3},
                ]},
            ]}},
        ],
    },
}


def test_build_v3_component_draft_from_skill_ex_example():
    result = build_v3_component_draft_from_skill(
        skill_id="vh_數學B1_PointSlopeForm",
        textbook_example_id=1,
        source_kind="ex_1",
        seed=42,
        textbook_row=POINT_SLOPE_TEXTBOOK_ROW,
        constraints=POINT_SLOPE_CONSTRAINTS,
    )

    assert result["status"] == "draft_built"
    assert result["line_type"] == "point_slope"
    assert result["skill_id"] == "vh_數學B1_PointSlopeForm"
    assert result["textbook_example_id"] == 1
    assert result["source_kind"] in {"ex_1", "example"}
    assert result["domain_module"] == (
        "core.domain.coordinate_geometry.line_equation_domain"
    )
    assert result["entrypoint"] == "build_line_equation_matrix"

    files = result["files"]
    assert isinstance(files, dict)
    assert set(files.keys()) == {"metadata.py", "generate.py", "get_hint.py"}
    for content in files.values():
        assert isinstance(content, str)
        assert content.strip()


def test_generate_py_string_is_porter_safe():
    result = build_v3_component_draft_from_skill(
        skill_id="vh_數學B1_PointSlopeForm",
        textbook_example_id=1,
        source_kind="ex_1",
        seed=42,
        textbook_row=POINT_SLOPE_TEXTBOOK_ROW,
        constraints=POINT_SLOPE_CONSTRAINTS,
    )
    generate_source = result["files"]["generate.py"]

    assert "build_line_equation_matrix" in generate_source
    assert "convert_domain_matrix_to_question_payload" in generate_source

    for token in FORBIDDEN_GENERATE_TOKENS:
        assert token not in generate_source

    for token in FORBIDDEN_MATH_HELPER_TOKENS:
        assert token not in generate_source


def test_registered_payload_adapter_scaffolds_through_authority_dispatch():
    result = build_v3_component_draft_from_skill(
        skill_id="gh_RationalNumbers",
        textbook_example_id=12280,
        source_kind="example",
        seed=42,
        textbook_row=RATIONAL_NUMBERS_ROW,
        constraints={"domain_operation": "identify_rational_numbers"},
    )

    assert result["fixed_domain_key"] == "number_system.rational_numbers"
    assert result["presentation_mode"] == "short_answer"
    assert result["answer_type"] == "short_answer"
    assert result["checker_key"] == "solution_set_checker"
    generate_source = result["files"]["generate.py"]
    assert "dispatch_registered_operation" in generate_source
    assert "resolve_domain_authority" in generate_source
    assert "convert_domain_matrix_to_question_payload" not in generate_source
    assert "from core.domain.promoted" not in generate_source


def test_registered_scaffold_preserves_component_generation_constraints_without_answer_authority():
    result = build_v3_component_draft_from_skill(
        skill_id="gh_RationalNumbers",
        textbook_example_id=99101,
        source_kind="example",
        seed=42,
        textbook_row={**RATIONAL_NUMBERS_ROW, "id": 99101},
        constraints={
            "domain_operation": "identify_rational_numbers",
            **SOURCE_CONSTRAINED_CANDIDATE_VARIANTS,
        },
    )
    namespace: dict[str, object] = {}
    exec(result["files"]["generate.py"], namespace)
    payload = namespace["generate"](seed=1)  # type: ignore[operator]

    assert payload["math_core"]["givens"]["candidates"] == (  # type: ignore[index]
        SOURCE_CONSTRAINED_CANDIDATE_VARIANTS["generation_constraints"]["variants"][1]["constraints"]["candidates"]
    )
    assert payload["correct_answer"] == [1]  # type: ignore[index]
    assert payload["answer_contract"]["checker_key"] == "solution_set_checker"  # type: ignore[index]


def test_registered_scaffold_without_generation_constraints_keeps_domain_sampling():
    result = build_v3_component_draft_from_skill(
        skill_id="gh_RationalNumbers",
        textbook_example_id=99102,
        source_kind="example",
        seed=42,
        textbook_row={**RATIONAL_NUMBERS_ROW, "id": 99102},
        constraints={"domain_operation": "identify_rational_numbers"},
    )
    namespace: dict[str, object] = {}
    exec(result["files"]["generate.py"], namespace)
    payload = namespace["generate"](seed=1)  # type: ignore[operator]

    assert len(payload["math_core"]["givens"]["candidates"]) == 5  # type: ignore[index]
    assert payload["answer_contract"]["checker_key"] == "solution_set_checker"  # type: ignore[index]


def test_promoted_registered_operation_without_adapter_blocks_before_direct_fallback(monkeypatch: pytest.MonkeyPatch):
    from core.registry.domain_operation_registry import OperationSpec

    monkeypatch.setattr(
        "core.registry.domain_operation_registry.get_operation_spec",
        lambda *_args: OperationSpec(
            operation_key="identify_rational_numbers",
            handler="build_rational_numbers_matrix",
        ),
    )
    with pytest.raises(ValueError, match="registered_payload_adapter_missing"):
        build_v3_component_draft_from_skill(
            skill_id="gh_RationalNumbers",
            textbook_example_id=12280,
            source_kind="example",
            seed=42,
            textbook_row=RATIONAL_NUMBERS_ROW,
            constraints={"domain_operation": "identify_rational_numbers"},
        )


def test_induced_spec_generation_constraints_reach_shadow_bridge_constraints():
    from core.gencode.pipeline_orchestrator import _v3_constraints_from_induced_spec

    induced_spec = {
        "problem_type_id": "identify_rational_numbers",
        "required_capabilities": ["identify_rational_numbers"],
        **SOURCE_CONSTRAINED_CANDIDATE_VARIANTS,
    }
    constraints = _v3_constraints_from_induced_spec(induced_spec)

    assert constraints["generation_constraints"] == SOURCE_CONSTRAINED_CANDIDATE_VARIANTS["generation_constraints"]
    assert constraints["generation_constraints"] is not induced_spec["generation_constraints"]
    without_variants = _v3_constraints_from_induced_spec({"problem_type_id": "point_slope"})
    assert "generation_constraints" not in without_variants


def test_phase1_reuse_restores_persisted_generation_constraints():
    from core.gencode.pipeline_orchestrator import _extract_phase1_induced_spec_from_payload

    payload = {
        "phase1_classification": {"problem_type_id": "identify_rational_numbers"},
        **SOURCE_CONSTRAINED_CANDIDATE_VARIANTS,
    }
    spec = _extract_phase1_induced_spec_from_payload(payload)

    assert spec["generation_constraints"] == SOURCE_CONSTRAINED_CANDIDATE_VARIANTS["generation_constraints"]
    nested_wins = _extract_phase1_induced_spec_from_payload(
        {
            "phase1_classification": {"generation_constraints": {"variants": [{"candidates": []}]}},
            **SOURCE_CONSTRAINED_CANDIDATE_VARIANTS,
        }
    )
    assert nested_wins["generation_constraints"] == {"variants": [{"candidates": []}]}
    assert "generation_constraints" not in _extract_phase1_induced_spec_from_payload(
        {"phase1_classification": {"problem_type_id": "point_slope"}}
    )


@pytest.mark.parametrize(
    ("skill_id", "domain_key"),
    [
        ("gh_RationalNumbers", "number_system.rational_numbers"),
        ("vh_數學B1_PointSlopeForm", "coordinate_geometry.line_equation"),
    ],
)
def test_explicit_domain_key_matching_confirmed_binding_keeps_confirmed_evidence(skill_id: str, domain_key: str):
    from core.gencode.skill_fixed_domain_authority import (
        build_domain_resolution_evidence,
        resolve_domain_authority,
        validate_component_domain_evidence,
    )
    from core.registry.taxonomy_registry import get_registry_revision

    result = resolve_domain_authority(
        skill_id,
        extra={"fixed_domain_key": domain_key, "required_capabilities": ["unrelated_capability_label"]},
    )

    assert result.resolution_source == "confirmed_binding"
    assert result.binding_status == "confirmed"
    assert result.fixed_domain_key == domain_key
    assert result.registry_revision == get_registry_revision(skill_id)
    assert "unrelated_capability_label" not in result.required_capabilities
    evidence = build_domain_resolution_evidence(result)
    evidence["selected_operation"] = result.allowed_operations[0]
    assert validate_component_domain_evidence(evidence) == []


def test_explicit_domain_key_different_from_confirmed_binding_stays_override():
    from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

    result = resolve_domain_authority(
        "vh_數學B1_PointSlopeForm",
        extra={"fixed_domain_key": "coordinate_geometry.point_line_distance"},
    )

    assert result.resolution_source == "explicit_override"
    assert result.binding_status == "override"


def test_metadata_py_injects_ex_source_kind_profile():
    result = build_v3_component_draft_from_skill(
        skill_id="vh_數學B1_PointSlopeForm",
        textbook_example_id=1,
        source_kind="ex_1",
        seed=42,
        textbook_row=POINT_SLOPE_TEXTBOOK_ROW,
        constraints=POINT_SLOPE_CONSTRAINTS,
    )
    metadata_source = result["files"]["metadata.py"]
    assert "ORDER_WEIGHT: Final[int] = 10" in metadata_source
    assert 'DIFFICULTY_LEVEL: Final[str] = "easy"' in metadata_source


def test_dry_run_hook_does_not_write_to_disk(monkeypatch: pytest.MonkeyPatch):
    write_calls: list[tuple[str, str]] = []

    def _blocked_open(file, mode="r", *args, **kwargs):  # type: ignore[no-untyped-def]
        mode_text = str(mode)
        if "w" in mode_text or "a" in mode_text or "+" in mode_text:
            write_calls.append((str(file), mode_text))
            raise AssertionError(f"unexpected disk write via open(): {file!r} mode={mode_text!r}")
        return builtins.open(file, mode, *args, **kwargs)

    def _blocked_write_text(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        write_calls.append((str(self), "write_text"))
        raise AssertionError(f"unexpected disk write via Path.write_text(): {self!r}")

    monkeypatch.setattr(builtins, "open", _blocked_open)
    monkeypatch.setattr(Path, "write_text", _blocked_write_text)

    result = build_v3_component_draft_from_skill(
        skill_id="vh_數學B1_PointSlopeForm",
        textbook_example_id=1,
        source_kind="ex_1",
        seed=42,
        textbook_row=POINT_SLOPE_TEXTBOOK_ROW,
        constraints=POINT_SLOPE_CONSTRAINTS,
    )
    assert result["status"] == "draft_built"
    assert write_calls == []


def test_unregistered_skill_raises_domain_unresolved():
    with pytest.raises(ValueError, match="DOMAIN_CAPABILITY_UNRESOLVED|no_required_capabilities|domain_capability|Unregistered"):
        build_v3_component_draft_from_skill(
            skill_id="vh_數學B1_NotRegisteredSkill",
            textbook_example_id=99,
            source_kind="ex_9",
            seed=1,
            textbook_row={
                **POINT_SLOPE_TEXTBOOK_ROW,
                "id": 99,
                "skill_id": "vh_數學B1_NotRegisteredSkill",
            },
        )


@pytest.mark.parametrize(
    ("source_kind", "expected_line_type"),
    [
        ("quiz_3", "two_points"),
        ("test_4", "two_points"),
    ],
)
def test_source_kind_line_type_mapping(source_kind: str, expected_line_type: str):
    result = build_v3_component_draft_from_skill(
        skill_id="vh_數學B1_PointSlopeForm",
        textbook_example_id=2,
        source_kind=source_kind,
        seed=7,
        textbook_row={
            **POINT_SLOPE_TEXTBOOK_ROW,
            "id": 2,
            "problem_text": "已知兩點 $(0,0)$ 與 $(2,4)$，求直線方程式。",
        },
        constraints={
            "line_type": expected_line_type,
            "problem_type_id": expected_line_type,
            "domain_operation": expected_line_type,
        },
    )
    assert result["line_type"] == expected_line_type


def test_constraints_line_type_override():
    result = build_v3_component_draft_from_skill(
        skill_id="vh_數學B1_PointSlopeForm",
        textbook_example_id=3,
        source_kind="quiz_1",
        seed=5,
        constraints={"line_type": "horizontal_line"},
        textbook_row={
            **POINT_SLOPE_TEXTBOOK_ROW,
            "id": 3,
            "problem_text": "求通過點 $(1,2)$ 的水平線方程式。",
        },
    )
    assert result["line_type"] == "horizontal_line"
