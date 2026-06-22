"""V3 Component Spec Service."""

from __future__ import annotations

from typing import Any

from core.gencode.answer_schema_registry import resolve_answer_schema_key
from core.gencode.induced_spec_contract import migrate_induced_spec_payload
from core.gencode.services.v3_example_semantic_classifier import TextbookExampleSource
from core.gencode.source_kind_resolver import resolve_source_kind_from_textbook_row
from core.registry.taxonomy_registry import resolve_domain_for_skill


def _resolve_checker_bundle(
    *,
    presentation_mode: str,
    problem_type_id: str,
    answer_type: str,
) -> tuple[str, str, str]:
    if presentation_mode == "single_choice":
        return (
            "choice_label_checker",
            "choice_label",
            "core.checkers.choice_label_checker",
        )
    if problem_type_id == "slope_intercept_find_x_intercept":
        return (
            "rational_checker",
            "rational_equivalent",
            "core.checkers.structured_text_checker",
        )
    if problem_type_id == "slope_intercept_read_slope_and_intercept":
        return (
            "text_short_checker",
            "exact_string",
            "core.checkers.structured_text_checker",
        )
    if problem_type_id in {
        "distance_from_point_to_line_parameter",
        "distance_from_point_to_line_parameter_single_choice_scalar",
        "compare_point_to_line_distances",
    }:
        return (
            "text_short_checker",
            "exact_string",
            "core.checkers.structured_text_checker",
        )
    if answer_type == "text_short":
        return (
            "text_short_checker",
            "exact_string",
            "core.checkers.structured_text_checker",
        )
    if problem_type_id == "intercept_form_triangle_area":
        return (
            "rational_checker",
            "rational_equivalent",
            "core.gencode.runtime_skill_wrapper",
        )
    if problem_type_id == "intercept_form_equation_and_triangle_area":
        return (
            "multi_part_answer_checker",
            "multi_part_answer",
            "core.checkers.multi_part_answer_checker",
        )
    if problem_type_id == "distance_from_point_to_line":
        return (
            "rational_checker",
            "rational_equivalent",
            "core.checkers.structured_text_checker",
        )
    if answer_type in ("rational", "numeric_or_undefined"):
        return (
            "rational_checker",
            "rational_equivalent",
            "core.checkers.structured_text_checker",
        )
    return (
        "linear_equation_equivalent_checker",
        "linear_equation_equivalent",
        "core.checkers.linear_equation_equivalent_checker",
    )


def build_v3_component_spec(
    source: TextbookExampleSource,
    classification: dict[str, Any],
    *,
    textbook_row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a complete component specification for a textbook example."""
    problem_type_id = str(classification["problem_type_id"])
    presentation_mode = str(classification["presentation_mode"])
    answer_type = str(classification["answer_type"])
    domain_operation = str(
        classification.get("domain_operation") or problem_type_id
    ).strip()
    checker_key, equivalence_type, checker_module = _resolve_checker_bundle(
        presentation_mode=presentation_mode,
        problem_type_id=problem_type_id,
        answer_type=answer_type,
    )
    domain_profile = resolve_domain_for_skill(source.skill_id)
    domain = str(domain_profile.get("domain") or "coordinate_geometry")
    answer_schema_key = resolve_answer_schema_key(
        answer_schema_key=classification.get("answer_schema_key"),
        domain_operation=domain_operation,
        problem_type_id=problem_type_id,
    )
    source_kind = resolve_source_kind_from_textbook_row(
        textbook_row
        or {
            "source_description": source.source_label,
            "problem_type": source.source_type,
        }
    )

    spec = {
        "component_id": f"src_{source.textbook_example_id}",
        "skill_id": source.skill_id,
        "domain": domain,
        "domain_operation": domain_operation,
        "problem_type_id": problem_type_id,
        "answer_schema_key": answer_schema_key or "",
        "presentation_mode": presentation_mode,
        "checker_key": checker_key,
        "domain_params": {},
        "source_template": source.question_text,
        "textbook_example_id": source.textbook_example_id,
        "source_kind": source_kind,
        "source_hash": source.source_hash,
        "semantic_classification": classification,
        "parameter_schema": {
            "coord_bounds": [-8, 8],
            "rng_seed_independent": True,
        },
        "question_template_schema": {
            "source_text": source.question_text,
            "has_choices": presentation_mode == "single_choice",
        },
        "answer_contract": {
            "presentation_mode": presentation_mode,
            "answer_type": answer_type,
            "checker_key": checker_key,
            "equivalence_type": equivalence_type,
            "checker_module": checker_module,
        },
        "hint_strategy": "three_stage_lead",
        "generation_strategy": "random_bounded",
        "trace": classification.get("trace", {}),
    }
    return migrate_induced_spec_payload(spec)
