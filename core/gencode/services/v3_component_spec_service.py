"""V3 Component Spec Service."""

from __future__ import annotations
from typing import Any
from core.gencode.services.v3_example_semantic_classifier import TextbookExampleSource

def build_v3_component_spec(
    source: TextbookExampleSource,
    classification: dict[str, Any],
) -> dict[str, Any]:
    """Build a complete component specification for a textbook example."""
    problem_type_id = classification["problem_type_id"]
    presentation_mode = classification["presentation_mode"]
    answer_type = classification["answer_type"]
    
    # Map checker_key and checker_module
    if presentation_mode == "single_choice":
        checker_key = "choice_label_checker"
        equivalence_type = "choice_label"
        checker_module = "core.checkers.choice_label_checker"
    elif problem_type_id == "slope_intercept_find_x_intercept":
        checker_key = "rational_checker"
        equivalence_type = "rational_equivalent"
        checker_module = "core.checkers.structured_text_checker"
    elif problem_type_id == "slope_intercept_read_slope_and_intercept":
        checker_key = "text_short_checker"
        equivalence_type = "exact_string"
        checker_module = "core.checkers.structured_text_checker"
    elif problem_type_id == "intercept_form_triangle_area":
        checker_key = "rational_checker"
        equivalence_type = "rational_equivalent"
        checker_module = "core.gencode.runtime_skill_wrapper"
    elif problem_type_id == "intercept_form_equation_and_triangle_area":
        checker_key = "multi_part_answer_checker"
        equivalence_type = "multi_part_answer"
        checker_module = "core.checkers.multi_part_answer_checker"
    elif answer_type in ("rational", "numeric_or_undefined"):
        checker_key = "rational_checker"
        equivalence_type = "rational_equivalent"
        checker_module = "core.checkers.structured_text_checker"
    else:
        checker_key = "linear_equation_equivalent_checker"
        equivalence_type = "linear_equation_equivalent"
        checker_module = "core.checkers.linear_equation_equivalent_checker"

    spec = {
        "component_id": f"src_{source.textbook_example_id}",
        "textbook_example_id": source.textbook_example_id,
        "source_hash": source.source_hash,
        "problem_type_id": problem_type_id,
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
        "checker_key": checker_key,
        "hint_strategy": "three_stage_lead",
        "presentation_mode": presentation_mode,
        "domain_operation": problem_type_id,
        "generation_strategy": "random_bounded",
        "trace": classification.get("trace", {}),
    }
    return spec
