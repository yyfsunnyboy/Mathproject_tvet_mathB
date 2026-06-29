from __future__ import annotations

import pytest

from core.domain.absolute_value_domain import (
    number_line_distance,
    solve_abs_equation,
    build_absolute_value_matrix,
)
from core.gencode.skill_fixed_domain_authority import (
    DOMAIN_PROVIDERS,
    DOMAIN_CAPABILITY_UNRESOLVED,
    SkillFixedDomainError,
    _select_provider_by_capability_coverage,
    merge_resolver_extra_with_induced_constraints,
    resolve_dynamic_fixed_domain_context,
)
from core.registry.domain_operation_registry import (
    check_registry_consistency,
    get_domain_spec,
)


@pytest.mark.parametrize(
    ("rhs", "expected"),
    [
        (8, [-8, 8]),
        (1, [-1, 1]),
        (0, [0]),
        (-3, []),
    ],
)
def test_solve_abs_equation(rhs: int, expected: list[int]) -> None:
    assert solve_abs_equation(rhs) == expected


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (-3, 7, 10),
        (7, -3, 10),
        (5, 5, 0),
        (-5, -2, 3),
    ],
)
def test_number_line_distance(a: int, b: int, expected: int) -> None:
    assert number_line_distance(a, b) == expected


@pytest.mark.parametrize(
    "capability",
    [
        "solve_basic_absolute_value_equation",
        "solve_basic_absolute_value_equation_no_solution",
        "number_line_distance_between_two_points",
    ],
)
def test_capability_resolver_selects_absolute_value_provider(capability: str) -> None:
    extra = merge_resolver_extra_with_induced_constraints(
        {},
        {
            "problem_type_id": capability,
            "required_capabilities": [capability],
            "classification_source": "deterministic_structural",
        },
    )

    ctx = resolve_dynamic_fixed_domain_context(
        "future_unregistered_math_skill",
        original_exc=ValueError("unregistered skill"),
        extra=extra,
    )

    assert ctx.fixed_domain_key == "algebra.absolute_value"
    assert capability in ctx.allowed_operations


def test_unknown_capability_remains_unresolved() -> None:
    extra = merge_resolver_extra_with_induced_constraints(
        {},
        {
            "problem_type_id": "unknown_absolute_value_capability",
            "required_capabilities": ["unknown_absolute_value_capability"],
            "classification_source": "test",
        },
    )

    with pytest.raises(SkillFixedDomainError) as exc_info:
        resolve_dynamic_fixed_domain_context(
            "future_unregistered_math_skill",
            original_exc=ValueError("unregistered skill"),
            extra=extra,
        )

    assert exc_info.value.code == DOMAIN_CAPABILITY_UNRESOLVED
    assert exc_info.value.details["matched_capabilities"] == []
    assert exc_info.value.details["missing_capabilities"] == [
        "unknown_absolute_value_capability"
    ]


def test_provider_registry_contract_is_complete() -> None:
    spec = get_domain_spec("algebra.absolute_value")

    assert spec is not None
    assert spec.domain_module == "core.domain.absolute_value_domain"
    assert set(spec.allowed_operations) == set(spec.capabilities)
    assert not [
        issue
        for issue in check_registry_consistency()
        if issue.get("domain_key") == "algebra.absolute_value"
    ]


def test_full_capability_coverage_trace_is_complete() -> None:
    required = {
        "solve_basic_absolute_value_equation",
        "solve_basic_absolute_value_equation_no_solution",
        "number_line_distance_between_two_points",
    }

    selected, candidates, meta = _select_provider_by_capability_coverage(
        required=required,
        problem_type_id="solve_basic_absolute_value_equation",
        providers=DOMAIN_PROVIDERS,
    )

    candidate = next(
        row for row in candidates if row["domain_key"] == "algebra.absolute_value"
    )
    assert selected == "algebra.absolute_value"
    assert meta["best_provider"] == "algebra.absolute_value"
    assert set(meta["matched_capabilities"]) == required
    assert meta["missing_capabilities"] == []
    assert candidate["coverage_ratio"] == 1.0


def test_build_absolute_value_matrix_signature_and_reproducibility() -> None:
    # Test identical seed produces identical results
    m1 = build_absolute_value_matrix(
        seed=42,
        line_type="solve_basic_absolute_value_equation",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={},
    )
    m2 = build_absolute_value_matrix(
        seed=42,
        domain_operation="solve_basic_absolute_value_equation",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={},
    )
    assert m1 == m2
    assert "rhs" in m1["givens"]
    assert m1["answer"]["canonical_form"] is not None

    # Test different seeds produce different outputs
    m3 = build_absolute_value_matrix(
        seed=43,
        line_type="solve_basic_absolute_value_equation",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={},
    )
    # Check if we generated different rhs values
    assert m1["givens"]["rhs"] != m3["givens"]["rhs"] or m1 != m3


@pytest.mark.parametrize(
    "op",
    [
        "solve_basic_absolute_value_equation",
        "solve_basic_absolute_value_equation_no_solution",
        "number_line_distance_between_two_points",
    ],
)
def test_build_absolute_value_matrix_schemas(op: str) -> None:
    m = build_absolute_value_matrix(
        seed=100,
        domain_operation=op,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={},
    )
    # Check required top-level fields
    assert "givens" in m
    assert "answer" in m
    assert "distractors" in m
    assert "explanation_steps" in m
    assert "validation_facts" in m
    assert "visual_spec" in m

    # Check validation_facts
    assert m["validation_facts"]["domain_operation"] == op
    assert m["validation_facts"]["task_type"] == op
    assert m["validation_facts"]["line_type"] == op

    # Check answer format
    assert "canonical_form" in m["answer"]
    assert "general_form" in m["answer"]
    assert "coefficients" in m["answer"]

    # Specific math verifications
    if op == "solve_basic_absolute_value_equation":
        rhs = m["givens"]["rhs"]
        assert rhs > 0
        assert m["answer"]["coefficients"] == [-rhs, rhs]
    elif op == "solve_basic_absolute_value_equation_no_solution":
        rhs = m["givens"]["rhs"]
        assert rhs < 0
        assert m["answer"]["coefficients"] == []
        assert m["answer"]["canonical_form"] == "無解"
    elif op == "number_line_distance_between_two_points":
        a = m["givens"]["a"]
        b = m["givens"]["b"]
        dist = abs(a - b)
        assert m["answer"]["coefficients"] == [dist]
        assert m["answer"]["canonical_form"] == str(dist)


def test_absolute_value_supremacy_resolves_correctly() -> None:
    # 1. AbsoluteValue skill with confirmed binding resolves to algebra.absolute_value
    # 2. Point/distance/line keywords in text do NOT hijack domain routing
    row = {
        "id": 4399,
        "skill_id": "vh_數學B1_AbsoluteValue",
        "problem_text": "已知數線上兩點A(-3)、B(7)，試求A、B兩點的距離。點、距離、直線",
        "correct_answer": "10",
        "problem_type": "textbook_exercise",
    }
    
    res = resolve_dynamic_fixed_domain_context(
        "vh_數學B1_AbsoluteValue",
        original_exc=ValueError("unregistered"),
        textbook_example=row,
        problem_type_id="number_line_distance_between_two_points",
        extra={},
    )
    
    assert res.fixed_domain_key == "algebra.absolute_value"
    assert "number_line_distance_between_two_points" in res.allowed_operations
    # Assert cross-domain operations are not included
    assert "distance_from_point_to_line" not in res.allowed_operations


def test_true_point_line_distance_skill_resolves_correctly() -> None:
    # 3. True point-to-line skill resolves correctly to its coordinate geometry domain
    row = {
        "id": 9999,
        "skill_id": "vh_數學B1_DistanceBetweenPointAndLine",
        "problem_text": "求點P(1, 2)到直線L的距離",
        "correct_answer": "5",
        "problem_type": "textbook_exercise",
    }
    
    res = resolve_dynamic_fixed_domain_context(
        "vh_數學B1_DistanceBetweenPointAndLine",
        original_exc=ValueError("unregistered"),
        textbook_example=row,
        problem_type_id="distance_from_point_to_line",
        extra={},
    )
    
    assert res.fixed_domain_key == "coordinate_geometry.point_line_distance"
    assert "distance_from_point_to_line" in res.allowed_operations


def test_unregistered_skill_fallback_remains_active() -> None:
    # 4. Unknown/unregistered skill without binding still resolves dynamically
    row = {
        "id": 99999,
        "skill_id": "vh_數學B1_UnknownSkill",
        "problem_text": "求點P(1, 2)到直線L的距離",
        "correct_answer": "5",
        "problem_type": "textbook_exercise",
    }
    
    res = resolve_dynamic_fixed_domain_context(
        "vh_數學B1_UnknownSkill",
        original_exc=ValueError("unregistered"),
        textbook_example=row,
        problem_type_id="distance_from_point_to_line",
        extra={},
    )
    
    assert res.fixed_domain_key == "coordinate_geometry.point_line_distance"
    assert "distance_from_point_to_line" in res.allowed_operations


def test_scaffold_contract_preservation() -> None:
    from models import db
    from core.gencode.pipeline_orchestrator import _v3_resolve_gated_domain_operation
    from core.gencode.v3_presentation_inference import fetch_textbook_example_row
    from core.gencode.v3_component_scaffold_builder import build_component_files_from_domain_payload
    from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

    # Using example 4398
    row = {
        "id": 4398,
        "skill_id": "vh_數學B1_AbsoluteValue",
        "problem_text": "數線上，若|x|= 8，試求x之值。",
        "correct_answer": "-8, 8",
        "problem_type": "textbook_exercise",
    }
    
    extra = {
        "problem_type_id": "solve_basic_absolute_value_equation",
        "required_capabilities": ["solve_basic_absolute_value_equation"],
        "classification_source": "deterministic_structural",
        "presentation_mode": "multiple_inputs",
        "answer_type": "solution_set",
        "answer_contract": {
            "answer_type": "solution_set",
            "checker_key": "solution_set_checker",
            "equivalence_type": "unordered_solution_set"
        }
    }

    # Verify _v3_resolve_gated_domain_operation preserves extra fields
    selected, classification, ctx = _v3_resolve_gated_domain_operation(
        skill_id="vh_數學B1_AbsoluteValue",
        textbook_row=row,
        conn=None,
        extra=extra
    )
    
    assert classification.get("presentation_mode") == "multiple_inputs"
    assert classification.get("answer_type") == "solution_set"
    assert classification.get("answer_contract", {}).get("checker_key") == "solution_set_checker"

    # Test file scaffold generation retains metadata
    payload_meta = {
        "fixed_domain_key": "algebra.absolute_value",
        "presentation_mode": "multiple_inputs",
        "answer_type": "solution_set",
        "problem_type_id": "solve_basic_absolute_value_equation",
        "checker_key": "solution_set_checker",
        "equivalence_type": "unordered_solution_set",
        "checker_module": "core.checkers.solution_set_checker",
    }
    files = build_component_files_from_domain_payload(
        skill_id="vh_數學B1_AbsoluteValue",
        component_id="src_4398",
        source_kind="example",
        domain_meta={
            "domain_module": "core.domain.absolute_value_domain",
            "entrypoint": "build_absolute_value_matrix",
        },
        payload_meta=payload_meta,
    )
    
    metadata_content = files["metadata.py"]
    assert "PRESENTATION_MODE: Final[str] = \"multiple_inputs\"" in metadata_content
    assert "ANSWER_TYPE: Final[str] = \"solution_set\"" in metadata_content
    assert "\"checker_key\": \"solution_set_checker\"" in metadata_content
    assert "\"equivalence_type\": \"unordered_solution_set\"" in metadata_content
    assert "\"module\": \"core.checkers.solution_set_checker\"" in metadata_content
    # Confirm coordinate geometry defaults are removed
    assert "斜率" not in metadata_content

    # Verify visual_spec=None is set for pure text questions
    matrix = {
        "givens": {"rhs": 8},
        "answer": {"canonical_form": "-8, 8", "general_form": "-8, 8", "coefficients": [-8, 8]},
        "distractors": [],
        "explanation_steps": [],
        "validation_facts": {"domain_operation": "solve_basic_absolute_value_equation"},
        "visual_spec": {
            "points": [],
            "lines": [],
            "x_range": [-10, 10],
            "y_range": [-10, 10],
        }
    }
    
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="multiple_inputs",
        answer_type="solution_set",
        domain_operation="solve_basic_absolute_value_equation",
    )
    assert payload["visual_spec"] is None



