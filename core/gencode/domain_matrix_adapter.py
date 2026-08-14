"""Adapter layer between Domain Full Matrix Dictionary and question payloads."""

from __future__ import annotations

import json
import random
import re
from fractions import Fraction
from typing import Any

from core.gencode.resources.rational_display import (
    canonicalize_display_answer,
    canonicalize_multi_part_display,
    canonicalize_part_display_answer,
    fraction_to_plain,
    normalize_fraction_value,
)


def _finalize_question_payload(payload: dict[str, Any]) -> dict[str, Any]:
    from core.gencode.single_choice_payload_normalizer import normalize_single_choice_payload

    return normalize_single_choice_payload(payload)


def _subquestions_from_multi_field_contract(
    answer_contract: dict[str, Any],
    matrix_subquestions: list[Any] | None = None,
) -> list[dict[str, Any]]:
    parts = answer_contract.get("parts") if isinstance(answer_contract.get("parts"), list) else []
    if not parts:
        return [dict(item) for item in (matrix_subquestions or []) if isinstance(item, dict)]
    field_specs = answer_contract.get("field_specs") if isinstance(answer_contract.get("field_specs"), list) else []
    spec_by_key = {
        str(spec.get("field_key") or spec.get("key") or ""): spec
        for spec in field_specs
        if isinstance(spec, dict)
    }
    matrix_by_key = {
        str(sq.get("field_key") or sq.get("key") or ""): sq
        for sq in (matrix_subquestions or [])
        if isinstance(sq, dict)
    }
    subquestions: list[dict[str, Any]] = []
    for part in parts:
        if not isinstance(part, dict):
            continue
        field_key = str(part.get("field_key") or part.get("key") or "").strip()
        spec = spec_by_key.get(field_key, {})
        matrix_sq = matrix_by_key.get(field_key, {})
        subquestions.append(
            {
                "field_key": field_key,
                "part": str(
                    spec.get("group_label")
                    or part.get("group_label")
                    or matrix_sq.get("part")
                    or matrix_sq.get("label")
                    or ""
                ),
                "prompt": str(part.get("label") or spec.get("label") or matrix_sq.get("prompt") or ""),
                "expected_answer": part.get("expected_answer"),
                "input_type": str(part.get("input_type") or spec.get("input_type") or "number"),
            }
        )
    return subquestions

MATRIX_REQUIRED_FIELDS = (
    "givens",
    "answer",
    "distractors",
    "explanation_steps",
    "validation_facts",
    "visual_spec",
)

ANSWER_REQUIRED_FIELDS = (
    "canonical_form",
    "general_form",
    "coefficients",
)

# slope and intercept are only available for slope-bearing line types
# (e.g. two_points, point_slope, slope_intercept_equation, etc.).
# Distance-type matrices (distance_from_point_to_line, compare_point_to_line_distances, etc.)
# do not carry slope/intercept. Do not add them to the universal required set.


def validate_domain_matrix(matrix: dict[str, Any], **kwargs: Any) -> bool:
    """Assert that a domain matrix contains all six required top-level fields.

    Accepts ignored **kwargs (component_id, problem_type_id, domain_operation) for
    forward-compatibility with callers that pass schema context alongside the matrix.
    Raises AnswerSchemaMismatchError for missing answer fields so callers can
    distinguish answer-schema violations from structural errors.
    """
    from core.gencode.answer_schema_registry import AnswerSchemaMismatchError

    if not isinstance(matrix, dict):
        raise ValueError("matrix must be a dict.")

    missing = [field for field in MATRIX_REQUIRED_FIELDS if field not in matrix]
    if missing:
        raise ValueError(f"domain matrix missing required fields: {missing}")

    answer = matrix["answer"]
    if not isinstance(answer, dict):
        raise AnswerSchemaMismatchError("matrix['answer'] must be a dict.")

    from core.gencode.answer_schema_registry import resolve_answer_schema_key, validate_answer_schema

    schema_key = resolve_answer_schema_key(
        answer_schema_key=kwargs.get("answer_schema_key"),
        domain_operation=kwargs.get("domain_operation"),
        problem_type_id=kwargs.get("problem_type_id"),
        task_type=kwargs.get("task_type"),
    )
    if schema_key:
        validate_answer_schema(
            answer,
            answer_schema_key=schema_key,
            component_id=kwargs.get("component_id"),
            problem_type_id=kwargs.get("problem_type_id"),
            domain_operation=kwargs.get("domain_operation"),
        )
    else:
        missing_answer = [field for field in ANSWER_REQUIRED_FIELDS if field not in answer]
        if missing_answer:
            raise AnswerSchemaMismatchError(
                f"matrix['answer'] missing required fields: {missing_answer}"
            )

    if not isinstance(matrix["distractors"], list):
        raise ValueError("matrix['distractors'] must be a list.")
    if not isinstance(matrix["explanation_steps"], list):
        raise ValueError("matrix['explanation_steps'] must be a list.")
    if not isinstance(matrix["validation_facts"], dict):
        raise ValueError("matrix['validation_facts'] must be a dict.")
    if not isinstance(matrix["visual_spec"], dict):
        raise ValueError("matrix['visual_spec'] must be a dict.")
    if not isinstance(matrix["givens"], dict):
        raise ValueError("matrix['givens'] must be a dict.")

    return True


def validate_full_matrix_shell(matrix: dict[str, Any], **kwargs: Any) -> bool:
    """Validate that a matrix contains the required top-level structural fields.

    Unlike validate_domain_matrix, this does NOT inspect the contents of
    matrix['answer'] — it only verifies the six outer shell fields are present
    and correctly typed. Useful for testing broken or partially-constructed answer
    dicts without tripping on the answer-schema gate.
    """
    if not isinstance(matrix, dict):
        raise ValueError("matrix must be a dict.")

    missing = [field for field in MATRIX_REQUIRED_FIELDS if field not in matrix]
    if missing:
        raise ValueError(f"domain matrix missing required fields: {missing}")

    if not isinstance(matrix["answer"], dict):
        raise ValueError("matrix['answer'] must be a dict.")
    if not isinstance(matrix["givens"], dict):
        raise ValueError("matrix['givens'] must be a dict.")
    if not isinstance(matrix["distractors"], list):
        raise ValueError("matrix['distractors'] must be a list.")
    if not isinstance(matrix["explanation_steps"], list):
        raise ValueError("matrix['explanation_steps'] must be a list.")
    if not isinstance(matrix["validation_facts"], dict):
        raise ValueError("matrix['validation_facts'] must be a dict.")
    if not isinstance(matrix["visual_spec"], dict):
        raise ValueError("matrix['visual_spec'] must be a dict.")

    return True


def normalize_domain_matrix(matrix: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Return a JSON-serializable copy of a domain matrix using basic types only.

    Accepts ignored **kwargs (answer_schema_key, component_id, problem_type_id,
    domain_operation) for forward-compatibility with pipeline_orchestrator callers.
    """
    validate_domain_matrix(matrix, **kwargs)
    normalized = _normalize_value(matrix)
    if not isinstance(normalized, dict):
        raise ValueError("normalized matrix must remain a dict.")
    json.dumps(normalized, ensure_ascii=False)
    return normalized


def _build_line_equation_answer_contract(
    *,
    presentation_mode: str,
    answer_type: str,
    semantic_answer: str,
    task_type: str = "",
) -> dict[str, Any]:
    if presentation_mode == "single_choice":
        return {
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": semantic_answer,
        }
    if task_type == "compare_point_to_line_distances":
        if semantic_answer in {"L_1", "L_2"}:
            return {
                "presentation_mode": "short_answer",
                "answer_type": "text_short",
                "checker": "line_label_checker",
                "checker_key": "line_label_checker",
                "answer_equivalence": "normalized_line_label",
                "equivalence": "normalized_line_label",
                "semantic_answer": semantic_answer,
            }
        else:
            return {
                "presentation_mode": "short_answer",
                "answer_type": "text_short",
                "checker": "text_short_checker",
                "checker_key": "text_short_checker",
                "answer_equivalence": "exact_string",
                "equivalence": "exact_string",
                "semantic_answer": semantic_answer,
            }

    if task_type == "slope_intercept_find_x_intercept":
        return {
            "presentation_mode": "short_answer",
            "answer_type": "rational",
            "checker": "rational_checker",
            "checker_key": "rational_checker",
            "answer_equivalence": "rational_equivalent",
            "equivalence": "rational_equivalent",
            "semantic_answer": semantic_answer,
        }
    if task_type == "slope_intercept_read_slope_and_intercept":
        return {
            "presentation_mode": "short_answer",
            "answer_type": "text_short",
            "checker": "text_short_checker",
            "checker_key": "text_short_checker",
            "answer_equivalence": "exact_string",
            "equivalence": "exact_string",
            "semantic_answer": semantic_answer,
        }
    if task_type == "intercept_form_triangle_area":
        return {
            "presentation_mode": presentation_mode,
            "answer_type": "single_choice" if presentation_mode == "single_choice" else "rational",
            "checker": "choice_label_checker" if presentation_mode == "single_choice" else "rational_checker",
            "checker_key": "choice_label_checker" if presentation_mode == "single_choice" else "rational_checker",
            "answer_equivalence": "choice_label" if presentation_mode == "single_choice" else "rational_equivalent",
            "equivalence": "choice_label" if presentation_mode == "single_choice" else "rational_equivalent",
            "semantic_answer": semantic_answer,
        }
    if task_type == "intercept_form_equation_and_triangle_area":
        return {
            "presentation_mode": "short_answer",
            "answer_type": "multi_part",
            "answer_shape": "multi_part",
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "answer_equivalence": "multi_part_answer",
            "equivalence_type": "multi_part_answer",
            "equivalence": "multi_part_answer",
            "semantic_answer": semantic_answer,
            "parts": [
                {
                    "key": "equation",
                    "label": "equation",
                    "checker": "linear_equation_equivalent_checker",
                    "equivalence_type": "linear_equation_equivalent",
                    "expected_answer": semantic_answer.get("equation") if isinstance(semantic_answer, dict) else "",
                    "display_answer": canonicalize_part_display_answer({
                        "checker": "linear_equation_equivalent_checker",
                        "expected_answer": semantic_answer.get("equation") if isinstance(semantic_answer, dict) else "",
                    }),
                },
                {
                    "key": "area",
                    "label": "area",
                    "checker": "rational_checker",
                    "equivalence_type": "rational_equivalent",
                    "expected_answer": semantic_answer.get("area") if isinstance(semantic_answer, dict) else "",
                    "display_answer": canonicalize_part_display_answer({
                        "checker": "rational_checker",
                        "expected_answer": semantic_answer.get("area") if isinstance(semantic_answer, dict) else "",
                    }),
                },
            ],
        }
    if task_type in (
        "slopes_of_named_segments",
        "classify_and_compare_figure_slopes",
        "parallel_and_perpendicular_slopes_from_reference",
    ):
        parts_map = semantic_answer if isinstance(semantic_answer, dict) else {}
        part_rows = []
        for key, expected in parts_map.items():
            expected_text = str(expected)
            uses_class_token = any(
                tok in expected_text for tok in ("m>", "m<", "m=", "m1", "不存在", "無")
            )
            checker = "expression_equivalence_checker" if uses_class_token or expected_text in {"不存在", "無"} else "rational_checker"
            equiv = "algebraic_equivalent" if checker == "expression_equivalence_checker" else "rational_equivalent"
            part_rows.append(
                {
                    "key": key,
                    "label": key,
                    "checker": checker,
                    "equivalence_type": equiv,
                    "expected_answer": expected_text,
                    "display_answer": expected_text,
                }
            )
        return {
            "presentation_mode": "short_answer",
            "answer_type": "multi_part",
            "answer_shape": "multi_part",
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "answer_equivalence": "multi_part_answer",
            "equivalence_type": "multi_part_answer",
            "equivalence": "multi_part_answer",
            "semantic_answer": parts_map,
            "parts": part_rows,
        }
    if answer_type == "numeric_or_radical":
        return {
            "presentation_mode": "short_answer",
            "answer_type": "numeric_or_radical",
            "checker": "expression_equivalence_checker",
            "checker_key": "expression_equivalence_checker",
            "answer_equivalence": "radical_equivalence",
            "equivalence": "radical_equivalence",
            "semantic_answer": semantic_answer,
        }
    if answer_type in ("rational", "numeric_or_undefined"):
        return {
            "presentation_mode": "short_answer",
            "answer_type": answer_type,
            "checker": "rational_checker",
            "checker_key": "rational_checker",
            "answer_equivalence": "rational_equivalent",
            "equivalence": "rational_equivalent",
            "semantic_answer": semantic_answer,
        }
    return {
        "presentation_mode": "short_answer",
        "answer_type": answer_type,
        "checker": "linear_equation_equivalent_checker",
        "checker_key": "linear_equation_equivalent_checker",
        "answer_equivalence": "linear_equation_equivalent",
        "equivalence": "linear_equation_equivalent",
        "semantic_answer": semantic_answer,
    }


def _line_equation_handwriting_ui_contract(presentation_mode: str) -> dict[str, Any]:
    """Shared practice surface for B1 line-equation payloads (non-drawing)."""
    base: dict[str, Any] = {
        "handwriting_enabled": True,
        "canvas_required": True,
        "ai_check_required": False,
        "allow_image_upload": False,
        "allow_text_answer": True,
    }
    if presentation_mode == "single_choice":
        return {
            **base,
            "response_mode": "single_choice",
            "text_input_enabled": False,
            "normal_submit_enabled": True,
        }
    return {
        **base,
        "response_mode": "text",
        "text_input_enabled": True,
        "normal_submit_enabled": True,
    }


def _prepare_line_equation_visual_spec_for_practice(visual_spec: dict[str, Any]) -> dict[str, Any]:
    """Mark coordinate-plane visuals renderable on the practice page."""
    spec = dict(visual_spec or {})
    if not spec or str(spec.get("kind") or "").strip() == "no_visual":
        return spec

    kind = str(spec.get("kind") or spec.get("type") or "").strip()
    if kind == "coordinate_plane_multi_figure":
        figures = spec.get("figures") or []
        comparisons = spec.get("comparisons") or []
        if isinstance(figures, list) and figures and isinstance(comparisons, list) and comparisons:
            spec["render_required"] = True
            spec["kind"] = "coordinate_plane_multi_figure"
            return spec
        return spec

    drawable_keys = ("points", "lines", "segments", "figures", "comparisons")
    if any(isinstance(spec.get(key), list) and spec.get(key) for key in drawable_keys):
        spec["render_required"] = True
        if kind.endswith("_spec") or kind == "coordinate_plane_segments":
            spec["kind"] = "coordinate_plane"
    return spec


def _apply_line_equation_practice_surface(payload: dict[str, Any]) -> dict[str, Any]:
    """Attach handwriting canvas + renderable visuals for line-equation practice."""
    out = dict(payload)
    mode = str(out.get("presentation_mode") or "short_answer").strip()
    ui_contract = _line_equation_handwriting_ui_contract(mode)
    answer_contract = dict(out.get("answer_contract") or {})
    answer_contract["ui_contract"] = {
        **dict(answer_contract.get("ui_contract") or {}),
        **ui_contract,
    }
    out["answer_contract"] = answer_contract
    out["ui_contract"] = ui_contract
    out["requires_handwriting"] = True

    visual_spec = _prepare_line_equation_visual_spec_for_practice(
        dict(out.get("visual_spec") or {})
    )
    if visual_spec:
        out["visual_spec"] = visual_spec
        if visual_spec.get("render_required"):
            out["visual_backed"] = True
    return out


def convert_line_equation_matrix_to_question_payload(
    matrix: dict[str, Any],
    *,
    presentation_mode: str | None = None,
    answer_type: str | None = None,
    problem_type_id: str | None = None,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Map a line-equation domain matrix into a standard outward question payload."""
    domain_operation = str(kwargs.get("domain_operation") or "").strip()
    normalized = normalize_domain_matrix(matrix)
    givens = normalized["givens"]
    answer = normalized["answer"]
    validation_facts = dict(normalized["validation_facts"])
    if domain_operation:
        validation_facts.setdefault("domain_operation", domain_operation)
        validation_facts.setdefault("task_type", domain_operation)
        validation_facts.setdefault("line_type", domain_operation)
    visual_spec = normalized["visual_spec"]
    explanation_steps = normalized["explanation_steps"]
    distractors = normalized["distractors"]

    assert isinstance(givens, dict)
    assert isinstance(answer, dict)
    assert isinstance(validation_facts, dict)
    assert isinstance(visual_spec, dict)
    assert isinstance(explanation_steps, list)
    assert isinstance(distractors, list)

    canonical_raw = answer["canonical_form"]
    canonical = str(canonical_raw)
    semantic_answer: Any = canonical_raw
    question_text = _build_line_equation_question_text(givens, validation_facts)
    mode = str(presentation_mode or "short_answer").strip()
    task_type = str(validation_facts.get("task_type") or validation_facts.get("line_type") or "").strip()
    if task_type in {
        "slopes_of_named_segments",
        "classify_and_compare_figure_slopes",
        "parallel_and_perpendicular_slopes_from_reference",
    }:
        mode = "short_answer"
    elif task_type in {
        "compare_line_slopes",
        "solve_parameter_from_known_slope_choice",
        "collinear_three_points_parameter_choice",
    } or answer.get("choices") or givens.get("choices"):
        mode = "single_choice"
    if mode == "single_choice":
        default_answer_type = "single_choice"
    elif task_type in (
        "slope_from_general_or_intercept_form",
        "slope_of_horizontal_or_vertical_line",
        "slope_from_general_form",
        "parallel_line_slope",
        "perpendicular_line_slope",
        "slope_from_two_points",
    ):
        default_answer_type = "numeric_or_undefined"
    elif task_type in (
        "perpendicular_condition_parameter",
        "parallel_condition_parameter",
        "solve_parameter_from_known_slope",
        "collinear_three_points_parameter",
        "non_triangle_collinear_parameter",
        "parallel_segments_parameter",
        "perpendicular_segments_parameter",
    ):
        default_answer_type = "rational"
    elif task_type in (
        "solve_parameter_from_known_slope_choice",
        "collinear_three_points_parameter_choice",
        "parallel_segments_parameter_choice",
        "parallel_two_point_lines_parameter_choice",
        "perpendicular_slope_quadrant_choice",
    ):
        default_answer_type = "single_choice"
    elif task_type in (
        "slopes_of_named_segments",
        "classify_and_compare_figure_slopes",
        "parallel_and_perpendicular_slopes_from_reference",
    ):
        default_answer_type = "multi_part"
    elif task_type == "intercept_form_triangle_area":
        default_answer_type = "rational"
    elif task_type == "intercept_form_equation_and_triangle_area":
        default_answer_type = "multi_part"
    elif task_type == "slope_intercept_find_x_intercept":
        default_answer_type = "rational"
    elif task_type == "slope_intercept_read_slope_and_intercept":
        default_answer_type = "text_short"
    elif task_type == "distance_from_point_to_line":
        default_answer_type = "rational"
    elif task_type in (
        "distance_from_point_to_line_parameter",
        "compare_point_to_line_distances",
    ):
        default_answer_type = "text_short"
    elif task_type in (
        "distance_between_parallel_lines",
        "solve_parameter_from_parallel_distance",
        "area_using_parallel_distance",
    ):
        default_answer_type = "numeric_or_radical"
    elif task_type == "parallel_lines_distance_single_choice":
        default_answer_type = "single_choice"
    else:
        default_answer_type = "expression"
    resolved_answer_type = str(answer_type or default_answer_type).strip()
    if task_type == "slope_intercept_find_x_intercept" and mode != "single_choice":
        resolved_answer_type = "rational"
    elif task_type == "slope_intercept_read_slope_and_intercept" and mode != "single_choice":
        resolved_answer_type = "text_short"
    elif task_type == "intercept_form_triangle_area" and mode != "single_choice":
        resolved_answer_type = "rational"
    elif task_type == "intercept_form_equation_and_triangle_area":
        resolved_answer_type = "multi_part"
    elif task_type in (
        "slopes_of_named_segments",
        "classify_and_compare_figure_slopes",
        "parallel_and_perpendicular_slopes_from_reference",
    ):
        resolved_answer_type = "multi_part"
        parts_map = answer.get("parts")
        if isinstance(parts_map, dict):
            semantic_answer = parts_map
    elif task_type in (
        "distance_between_parallel_lines",
        "solve_parameter_from_parallel_distance",
        "area_using_parallel_distance",
    ) and mode != "single_choice":
        resolved_answer_type = "numeric_or_radical"

    math_objects = _infer_math_objects(validation_facts)
    math_core: dict[str, Any] = {
        "givens": _format_givens_for_hint(givens),
        "raw_givens": givens,
        "target": canonical,
        "math_objects": math_objects,
        "derivation": [str(step) for step in explanation_steps],
        "validation_facts": validation_facts,
    }

    contract_fields = {
        "problem_type_id": problem_type_id,
        "component_id": component_id,
        "textbook_example_id": textbook_example_id,
        "source_kind": source_kind,
        "generator_key": generator_key or component_id,
    }
    metadata: dict[str, Any] = {
        "givens": math_core["givens"],
        "raw_givens": givens,
        "target": canonical,
        "derivation": math_core["derivation"],
        "coefficients": answer.get("coefficients"),
        "general_form": answer.get("general_form"),
        "line_equation": answer.get("line_equation") or canonical,
        "presentation_mode": mode,
        "answer_type": resolved_answer_type,
        "semantic_answer": semantic_answer,
    }
    for key, value in contract_fields.items():
        if value is not None:
            metadata[key] = value

    if mode == "single_choice":
        if task_type == "compare_line_slopes" or answer.get("choices") or givens.get("choices"):
            choices = _normalize_labeled_choices(answer.get("choices") or givens.get("choices"))
            correct_label = str(answer.get("correct_label") or "").strip()
            correct_choice_text = ""
            for choice in choices:
                if choice["label"] == correct_label:
                    correct_choice_text = str(choice["text"])
                    break
            if task_type == "collinear_three_points_parameter_choice":
                semantic_answer = str(
                    answer.get("semantic_answer")
                    or answer.get("value")
                    or answer.get("parameter")
                    or correct_choice_text
                    or ""
                ).strip()
            else:
                semantic_answer = correct_choice_text
        elif task_type == "parabola_secant_parallel_line_choice":
            choices = _normalize_labeled_choices(answer.get("choices"))
            correct_label = str(answer.get("correct_label") or "").strip()
            if not choices or not correct_label:
                raise ValueError("unsupported_choices_generator:parabola_secant_choices_missing")
        elif task_type == "intercept_form_triangle_area":
            choices, correct_label = _build_area_choice_options(
                str(semantic_answer),
                seed_text=f"{semantic_answer}|{givens.get('x_intercept')}|{givens.get('y_intercept')}",
            )
        elif task_type == "slope_intercept_find_x_intercept":
            choices, correct_label = _build_x_intercept_choice_options(
                canonical,
                givens,
                seed_text=f"{canonical}|{givens.get('slope')}|{givens.get('y_intercept')}",
            )
        else:
            choices, correct_label = _build_choice_options(canonical, distractors, seed_text=canonical)
        payload_answer = correct_label
        payload_correct = correct_label
        if task_type == "parallel_lines_distance_single_choice":
            semantic_answer = correct_label
            display_answer = correct_label
        else:
            display_answer = _format_latex_display_answer(str(semantic_answer), task_type)
        choices = [
            {**choice, "text": _format_latex_display_answer(str(choice["text"]), task_type)}
            for choice in choices
        ]
        options = [str(choice["text"]) for choice in choices]
        answer_contract = _build_line_equation_answer_contract(
            presentation_mode=mode,
            answer_type=resolved_answer_type,
            semantic_answer=semantic_answer,
            task_type=task_type,
        )
    else:
        choices = []
        options = []
        payload_answer = semantic_answer
        payload_correct = semantic_answer
        display_answer = _format_display_answer(semantic_answer, task_type, resolved_answer_type)
        answer_contract = _build_line_equation_answer_contract(
            presentation_mode=mode,
            answer_type=resolved_answer_type,
            semantic_answer=semantic_answer,
            task_type=task_type,
        )

    # Merge comparison-specific fields into the contract for compare_point_to_line_distances.
    # This populates target_direction, closer_line, farther_line, comparison_relation,
    # comparison_result, and distances — required by validate_comparison_contract.
    if task_type == "compare_point_to_line_distances":
        for _cmp_key in (
            "target_direction",
            "closer_line",
            "farther_line",
            "comparison_relation",
            "comparison_result",
            "distances",
        ):
            if _cmp_key in answer and _cmp_key not in answer_contract:
                answer_contract[_cmp_key] = answer[_cmp_key]

    # Merge scalar-topology fields for the single_choice_scalar distance type.
    # validate_single_choice_scalar_topology checks choice_value_shape and solution_cardinality
    # from the answer_contract.
    if task_type == "distance_from_point_to_line_parameter_single_choice_scalar":
        for _sc_key in ("choice_value_shape", "solution_cardinality"):
            if _sc_key in answer and _sc_key not in answer_contract:
                answer_contract[_sc_key] = answer[_sc_key]

    payload: dict[str, Any] = {
        "question_text": question_text,
        "question": question_text,
        "correct_answer": payload_correct,
        "answer": payload_answer,
        "display_answer": display_answer,
        "semantic_answer": semantic_answer,
        "choices": choices,
        "options": options,
        "visual_spec": visual_spec,
        "math_core": math_core,
        "presentation_mode": mode,
        "answer_type": resolved_answer_type,
        "metadata": metadata,
        "answer_contract": answer_contract,
        "checker": answer_contract.get("checker"),
        "checker_type": answer_contract.get("checker"),
        "equivalence": answer_contract.get("answer_equivalence"),
    }
    if problem_type_id:
        payload["problem_type_id"] = problem_type_id
    if component_id:
        payload["component_id"] = component_id
    if textbook_example_id is not None:
        payload["textbook_example_id"] = textbook_example_id
    if source_kind:
        payload["source_kind"] = source_kind
    if generator_key or component_id:
        payload["generator_key"] = generator_key or component_id
    metadata["semantic_answer"] = semantic_answer
    return _apply_line_equation_practice_surface(payload)


def _normalize_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return value.numerator
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): _normalize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_value(item) for item in value]
    if isinstance(value, set):
        return [_normalize_value(item) for item in sorted(value, key=str)]
    raise TypeError(f"Unsupported non-JSON-serializable value type: {type(value)!r}")


def _latex_inline(value: Any) -> str:
    return f"\\({_format_latex_math_text(str(value))}\\)"


def _latex_inline_equation(value: Any) -> str:
    return f"\\({_format_latex_math_text(str(value))}\\)"


def _latex_dollar(value: Any) -> str:
    return f"${_format_latex_math_text(str(value))}$"


def _format_latex_display_answer(value: str, task_type: str = "") -> str:
    text = str(value or "").strip()
    if not text:
        return text
    if len(text) == 1 and text.upper() in {"A", "B", "C", "D"}:
        return text.upper()
    if task_type.startswith("slope_intercept"):
        return _latex_inline_equation(canonicalize_display_answer(text))
    if task_type == "intercept_form_triangle_area":
        return _latex_dollar(canonicalize_display_answer(text, answer_type="rational"))
    if task_type == "parabola_secant_parallel_line_choice":
        return _latex_dollar(canonicalize_display_answer(text))
    if _text_needs_math_latex(text):
        return _latex_dollar(text)
    return _format_latex_math_text(text)


def _format_display_answer(value: Any, task_type: str = "", answer_type: str = "") -> Any:
    if str(answer_type or "").strip() == "multi_part" and isinstance(value, dict):
        return canonicalize_multi_part_display(value)
    return _format_latex_display_answer(str(value), task_type)


def _format_latex_math_text(text: str) -> str:
    import re

    normalized = str(text or "").strip().replace("−", "-")
    if normalized.startswith("$") and normalized.endswith("$"):
        normalized = normalized[1:-1].strip()

    def repl_fraction(match: re.Match[str]) -> str:
        return canonicalize_display_answer(match.group(0), answer_type="rational")

    normalized = re.sub(r"(?<![\\\w])[-+]?\d+/\d+", repl_fraction, normalized)
    if "sqrt" in normalized or "*" in normalized:
        try:
            import sympy

            return sympy.latex(sympy.sympify(normalized))
        except Exception:
            normalized = re.sub(r"sqrt\(([^()]+)\)", r"\\sqrt{\1}", normalized)
            normalized = normalized.replace("*", "")
    return normalized


def _text_needs_math_latex(text: str) -> bool:
    return any(token in str(text) for token in ("sqrt(", "\\sqrt", "/", "*"))


def _build_line_equation_question_text(
    givens: dict[str, Any],
    validation_facts: dict[str, Any],
) -> str:
    task_type = str(validation_facts.get("task_type") or validation_facts.get("line_type") or "").strip()
    if not task_type:
        task_type = "point_slope"

    registered_task_types = {
        "point_slope",
        "two_points",
        "horizontal_line",
        "vertical_line",
        "oblique_line",
        "slope_intercept_equation",
        "slope_intercept_find_x_intercept",
        "slope_intercept_read_slope_and_intercept",
        "intercept_form_equation",
        "intercept_form_triangle_area",
        "intercept_form_equation_and_triangle_area",
        "intercept_form_from_intercept_sum_and_slope",
        "parabola_secant_parallel_line_choice",
        "triangle_area_bisector_line_equation",
        "slope_from_general_or_intercept_form",
        "line_through_point_parallel_to_line",
        "line_through_point_perpendicular_to_line",
        "slope_of_horizontal_or_vertical_line",
        "slope_from_general_form",
        "parallel_line_slope",
        "perpendicular_condition_parameter",
        "parallel_condition_parameter",
        "compare_line_slopes",
        "perpendicular_line_slope",
        "line_through_intersection_parallel_to_line",
        "perpendicular_bisector_application",
        "line_through_point_perpendicular_to_segment",
        "slope_from_two_points",
        "solve_parameter_from_known_slope",
        "solve_parameter_from_known_slope_choice",
        "collinear_three_points_parameter",
        "non_triangle_collinear_parameter",
        "parallel_segments_parameter",
        "perpendicular_segments_parameter",
        "perpendicular_two_point_lines_parameter",
        "triangle_right_angle_verification",
        "collinear_three_points_parameter_choice",
        "parallel_segments_parameter_choice",
        "parallel_two_point_lines_parameter_choice",
        "parallel_and_perpendicular_slopes_from_reference",
        "perpendicular_slope_quadrant_choice",
        "slopes_of_named_segments",
        "classify_and_compare_figure_slopes",
        "distance_from_point_to_line",
        "distance_from_point_to_line_parameter",
        "distance_from_point_to_line_parameter_single_choice_scalar",
        "compare_point_to_line_distances",
        "distance_between_parallel_lines",
        "solve_parameter_from_parallel_distance",
        "construct_parallel_line_at_distance",
        "parallel_lines_distance_single_choice",
        "area_using_parallel_distance",
    }

    if task_type not in registered_task_types:
        raise ValueError(f"unsupported_line_equation_task_type:{task_type}")

    if task_type == "distance_between_parallel_lines":
        line_1 = _format_latex_math_text(givens.get("line_1") or givens.get("equation_1"))
        line_2 = _format_latex_math_text(givens.get("line_2") or givens.get("equation_2"))
        if not line_1 or not line_2:
            raise ValueError("required_line_task_slot_missing:distance_between_parallel_lines:parallel_line_pair")
        return f"試求兩平行線 ${line_1}$ 與 ${line_2}$ 之間的距離。"

    if task_type == "solve_parameter_from_parallel_distance":
        line_1 = _format_latex_math_text(givens.get("line_1"))
        line_2 = _format_latex_math_text(givens.get("line_2"))
        target_distance = _format_latex_math_text(givens.get("target_distance") or "")
        param_name = givens.get("parameter_name") or "k"
        parameter_condition = _format_latex_math_text(givens.get("parameter_condition") or "")
        if not line_1 or not line_2:
            raise ValueError("required_line_task_slot_missing:solve_parameter_from_parallel_distance:parallel_line_pair")
        return (
            f"坐標平面上，若兩平行線 ${line_1}$ 與 ${line_2}$ 的距離為 ${target_distance}$，"
            f"且 ${parameter_condition}$，試求 ${param_name}$ 之值。"
        )

    if task_type == "area_using_parallel_distance":
        point_a = givens.get("point_a")
        line = _format_latex_math_text(givens.get("line"))
        segment_length = _format_latex_math_text(givens.get("segment_length"))
        if point_a is None or not line or segment_length is None:
            raise ValueError("required_line_task_slot_missing:area_using_parallel_distance:givens")
        pt = _format_point_for_question(point_a)
        return (
            f"設 A 點坐標為 {pt}，且 B、C 兩點在直線 $L: {line}$ 上，"
            f"若 $\\overline{{BC}}$ 的長為 ${segment_length}$，試求 △ABC 的面積。"
        )

    if task_type == "parallel_lines_distance_single_choice":
        line_expr = _format_latex_math_text(givens.get("line_expression") or "")
        slope = _format_latex_math_text(givens.get("slope") or "")
        origin_distance = _format_latex_math_text(givens.get("origin_distance") or "")
        a_value = givens.get("a_value")
        return (
            f"已知 $a>0$、$k>0$，且本題 $a={a_value}$。若直線 $L: {line_expr}$ 的斜率為 ${slope}$，"
            f"且點 $(0,0)$ 到直線 $L$ 的距離為 ${origin_distance}$，則 $a+k=$？"
        )

    if task_type == "construct_parallel_line_at_distance":
        line_1 = givens.get("line_1")
        line_2 = givens.get("line_2")
        if not line_1 or not line_2:
            raise ValueError("required_line_task_slot_missing:construct_parallel_line_at_distance:parallel_line_pair")
        return f"試求與 ${line_1}$ 平行且與 ${line_2}$ 相距離的直線方程式。"

    # 1. Slope-Intercept Forms
    if task_type == "slope_intercept_equation":
        if "slope" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_intercept_equation:slope")
        if "y_intercept" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_intercept_equation:y_intercept")
        slope = givens.get("slope")
        y_intercept = givens.get("y_intercept")
        return (
            f"已知直線的斜率為 {_latex_inline(slope)}，且 y 截距為 {_latex_inline(y_intercept)}，"
            "試求此直線方程式。"
        )

    if task_type == "slope_intercept_find_x_intercept":
        if "slope" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_intercept_find_x_intercept:slope")
        if "y_intercept" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_intercept_find_x_intercept:y_intercept")
        slope = givens.get("slope")
        y_intercept = givens.get("y_intercept")
        return (
            f"設直線 L 的斜率為 {_latex_inline(slope)}，且 y 截距為 {_latex_inline(y_intercept)}，"
            "求 L 的 x 截距。"
        )

    if task_type == "slope_intercept_read_slope_and_intercept":
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_intercept_read_slope_and_intercept:equation")
        equation = givens.get("equation")
        return f"已知直線方程式為 {_latex_inline_equation(equation)}，判斷其斜率與 y 截距。"

    # 2. Intercept Forms & Word Problems
    if task_type in {
        "intercept_form_equation",
        "intercept_form_triangle_area",
        "intercept_form_equation_and_triangle_area",
        "intercept_form_from_intercept_sum_and_slope",
        "parabola_secant_parallel_line_choice",
        "triangle_area_bisector_line_equation",
    }:
        equation = givens.get("equation")
        x_intercept = givens.get("x_intercept")
        y_intercept = givens.get("y_intercept")
        if task_type == "triangle_area_bisector_line_equation":
            for slot in ("vertex", "edge_p1", "edge_p2", "midpoint"):
                if slot not in givens:
                    raise ValueError(f"required_line_task_slot_missing:triangle_area_bisector_line_equation:{slot}")
            vertex = _format_point_for_question(givens.get("vertex"))
            edge_p1 = _format_point_for_question(givens.get("edge_p1"))
            edge_p2 = _format_point_for_question(givens.get("edge_p2"))
            midpoint = _format_point_for_question(givens.get("midpoint"))
            return (
                f"已知三角形 ABC 中，A={edge_p1}、B={vertex}、C={edge_p2}。"
                f"若直線通過 B 並通過 AC 的中點 D={midpoint}，求此平分三角形 ABC 面積的直線方程式。"
            )
        if task_type == "parabola_secant_parallel_line_choice":
            if "p" not in givens or "q" not in givens:
                raise ValueError("required_line_task_slot_missing:parabola_secant_parallel_line_choice:interval_bounds")
            p = givens.get("p")
            q = givens.get("q")
            return (
                f"若 A、B 兩點分別是拋物線 $y=x^2$ 與直線 $x={p}$、$x={q}$ 的交點，"
                "則直線 AB 與下列哪一條直線平行？"
            )
        if task_type == "intercept_form_from_intercept_sum_and_slope":
            if "intercept_sum" not in givens or "slope" not in givens:
                raise ValueError("required_line_task_slot_missing:intercept_form_from_intercept_sum_and_slope:givens")
            intercept_sum = givens.get("intercept_sum")
            slope = givens.get("slope")
            return (
                f"已知直線 L 在兩坐標軸上的截距和為 {_latex_dollar(intercept_sum)}，"
                f"且 L 的斜率為 {_latex_dollar(slope)}，求 L 的方程式。"
            )
        if task_type == "intercept_form_triangle_area":
            if equation:
                return (
                    f"已知直線方程式為 {_latex_dollar(equation)}，求它與 x 軸及 y 軸"
                    "所圍成的三角形面積。"
                )
            return (
                f"已知一直線的 x 截距為 {_latex_dollar(x_intercept)}，y 截距為 "
                f"{_latex_dollar(y_intercept)}，求它與兩坐標軸所圍成的三角形面積。"
            )
        if equation:
            return (
                f"已知直線方程式為 {_latex_dollar(equation)}，將此直線化成截距式，"
                "並求與兩坐標軸所圍成的三角形面積。"
            )
        return (
            f"已知一直線 L 的 x 截距為 {_latex_dollar(x_intercept)}，y 截距為 "
            f"{_latex_dollar(y_intercept)}，試求直線 L 的方程式與兩坐標軸所圍成的三角形面積。"
        )

    # 3. V3 General Form Line types
    if task_type == "slope_from_general_or_intercept_form":
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_from_general_or_intercept_form:equation")
        eq = givens["equation"]
        return f"試求直線的斜率：{_latex_dollar(eq)}。"

    if task_type == "line_through_point_parallel_to_line":
        if "point" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_parallel_to_line:point")
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_parallel_to_line:reference_line")
        pt = _format_point_for_question(givens["point"])
        eq = givens["equation"]
        return f"已知直線 $L_2$ 通過點 {pt} 且與直線 $L_1: {eq}$ 平行，試求 $L_2$ 的直線方程式。"

    if task_type == "line_through_point_perpendicular_to_line":
        if "point" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_perpendicular_to_line:point")
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_perpendicular_to_line:reference_line")
        pt = _format_point_for_question(givens["point"])
        eq = givens["equation"]
        return f"已知直線 $L_2$ 通過點 {pt} 且與直線 $L_1: {eq}$ 垂直，試求 $L_2$ 的直線方程式。"

    if task_type == "slope_of_horizontal_or_vertical_line":
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_of_horizontal_or_vertical_line:equation")
        eq = givens["equation"]
        return f"試求直線的斜率：{_latex_dollar(eq)}。"

    if task_type == "slope_from_general_form":
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_from_general_form:equation")
        eq = givens["equation"]
        return f"試求直線的斜率：{_latex_dollar(eq)}。"

    if task_type == "parallel_line_slope":
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:parallel_line_slope:reference_line")
        eq = givens["equation"]
        return f"試求與直線 {_latex_dollar(eq)} 平行之直線斜率。"

    if task_type == "perpendicular_condition_parameter":
        if "equation_1" not in givens:
            raise ValueError("required_line_task_slot_missing:perpendicular_condition_parameter:line_1")
        if "equation_2" not in givens:
            raise ValueError("required_line_task_slot_missing:perpendicular_condition_parameter:line_2")
        eq1 = givens["equation_1"]
        eq2 = givens["equation_2"]
        if "a" not in eq1 and "k" not in eq1:
            raise ValueError("required_line_task_slot_missing:perpendicular_condition_parameter:parameter")
        return f"設兩直線 $L_1: {eq1}$、$L_2: {eq2}$，若 $L_1 \\bot L_2$，則 $a =$"

    if task_type == "parallel_condition_parameter":
        if "equation_1" not in givens:
            raise ValueError("required_line_task_slot_missing:parallel_condition_parameter:line_1")
        if "equation_2" not in givens:
            raise ValueError("required_line_task_slot_missing:parallel_condition_parameter:line_2")
        eq1 = givens["equation_1"]
        eq2 = givens["equation_2"]
        if "a" not in eq1 and "k" not in eq1:
            raise ValueError("required_line_task_slot_missing:parallel_condition_parameter:parameter")
        return f"設兩直線 $L_1: {eq1}$、$L_2: {eq2}$，若 $L_1 \\parallel L_2$，則 $a =$"

    if task_type == "compare_line_slopes":
        if "choices" not in givens:
            raise ValueError("required_line_task_slot_missing:compare_line_slopes:lines")
        return "下列各直線方程式中，具有最大斜率的直線為"

    if task_type == "slope_from_two_points":
        if "point_a" not in givens or "point_b" not in givens:
            raise ValueError("required_line_task_slot_missing:slope_from_two_points:points")
        pa = givens.get("point_a_display") or _format_point_for_question(givens["point_a"])
        pb = givens.get("point_b_display") or _format_point_for_question(givens["point_b"])
        return f"試求過兩點 A{pa}、B{pb} 的直線斜率。"

    if task_type in ("solve_parameter_from_known_slope", "solve_parameter_from_known_slope_choice"):
        if "slope" not in givens:
            raise ValueError("required_line_task_slot_missing:solve_parameter_from_known_slope:slope")
        pa = givens.get("point_a_display") or _format_point_for_question(givens.get("point_a"))
        pb = givens.get("point_b_display") or _format_point_for_question(givens.get("point_b"))
        slope = givens["slope"]
        param = givens.get("parameter_name") or "a"
        return (
            f"若直線通過點 {pa} 與 {pb}，且其斜率為 {_latex_dollar(str(slope))}，"
            f"試求 {param} 之值。"
        )

    if task_type == "collinear_three_points_parameter":
        pa = givens.get("point_a_display") or _format_point_for_question(givens.get("point_a"))
        pb = givens.get("point_b_display") or _format_point_for_question(givens.get("point_b"))
        pc = givens.get("point_c_display") or _format_point_for_question(givens.get("point_c"))
        param = givens.get("parameter_name") or "k"
        return f"若 A{pa}、B{pb}、C{pc} 三點共線，試求 {param} 之值。"

    if task_type == "non_triangle_collinear_parameter":
        pa = givens.get("point_a_display") or _format_point_for_question(givens.get("point_a"))
        pb = givens.get("point_b_display") or _format_point_for_question(givens.get("point_b"))
        pc = givens.get("point_c_display") or _format_point_for_question(givens.get("point_c"))
        param = givens.get("parameter_name") or "k"
        return f"若 A{pa}、B{pb}、C{pc} 三點無法連結成一個三角形，試求 {param} 之值。"

    if task_type == "parallel_segments_parameter":
        pa = givens.get("point_a_display") or _format_point_for_question(givens.get("point_a"))
        pb = givens.get("point_b_display") or _format_point_for_question(givens.get("point_b"))
        pc = givens.get("point_c_display") or _format_point_for_question(givens.get("point_c"))
        pd = givens.get("point_d_display") or _format_point_for_question(givens.get("point_d"))
        param = givens.get("parameter_name") or "a"
        return (
            f"設 A{pa}、B{pb}、C{pc}、D{pd}，若線段 AB 與 CD 平行，試求 {param} 之值。"
        )

    if task_type == "perpendicular_segments_parameter":
        pa = givens.get("point_a_display") or _format_point_for_question(givens.get("point_a"))
        pb = givens.get("point_b_display") or _format_point_for_question(givens.get("point_b"))
        pc = givens.get("point_c_display") or _format_point_for_question(givens.get("point_c"))
        pd = givens.get("point_d_display") or _format_point_for_question(givens.get("point_d"))
        param = givens.get("parameter_name") or "x"
        return (
            f"設 A{pa}、B{pb}、C{pc}、D{pd}，若線段 AB 與 CD 垂直，試求 {param} 之值。"
        )

    if task_type == "parallel_segments_parameter_choice":
        pa = givens.get("point_a_display") or _format_point_for_question(givens.get("point_a"))
        pb = givens.get("point_b_display") or _format_point_for_question(givens.get("point_b"))
        pc = givens.get("point_c_display") or _format_point_for_question(givens.get("point_c"))
        pd = givens.get("point_d_display") or _format_point_for_question(givens.get("point_d"))
        param = givens.get("parameter_name") or "x"
        return (
            f"已知平面上四點 A{pa}、B{pb}、C{pc}、D{pd}。"
            f"若直線 AB 與直線 CD 平行，則 {param} ="
        )

    if task_type == "parallel_two_point_lines_parameter_choice":
        l1 = givens.get("line_1_display") or ""
        l2 = givens.get("line_2_display") or ""
        param = givens.get("parameter_name") or "a"
        return (
            f"平面上過兩點 ${l1}$ 的直線和過另兩點 ${l2}$ 的直線平行，"
            f"則 {param} ="
        )

    if task_type == "parallel_and_perpendicular_slopes_from_reference":
        m1 = givens.get("reference_slope") or "m1"
        return (
            f"已知直線 L1 的斜率為 {_latex_dollar(str(m1))}，試問："
            f"(1) 若直線 L2 平行 L1，試求 L2 的斜率。"
            f"(2) 若直線 L3 垂直 L1，試求 L3 的斜率。"
        )

    if task_type == "triangle_right_angle_verification":
        pa = givens.get("point_a_display") or _format_point_for_question(givens.get("point_a"))
        pb = givens.get("point_b_display") or _format_point_for_question(givens.get("point_b"))
        pc = givens.get("point_c_display") or _format_point_for_question(givens.get("point_c"))
        return (
            f"已知坐標平面上三點 A{pa}、B{pb} 及 C{pc}，"
            f"試問 △ABC 是否為直角三角形？"
        )

    if task_type == "perpendicular_two_point_lines_parameter":
        l1 = givens.get("line_1_display") or ""
        l2 = givens.get("line_2_display") or ""
        param = givens.get("parameter_name") or "k"
        return (
            f"設直線 L1 通過 {l1} 兩點，直線 L2 通過 {l2} 兩點，"
            f"若直線 L1 垂直 L2，試求 {param} 之值。"
        )

    if task_type == "perpendicular_slope_quadrant_choice":
        return (
            "已知 m1 與 m2 分別為直線 L1 與直線 L2 的斜率，且 m1、m2 皆不為 0。"
            "若直線 L1 通過第一、三象限，而直線 L2 與直線 L1 垂直，"
            "則點 (m1, m2) 落在第幾象限？"
        )

    if task_type == "slopes_of_named_segments":
        points = givens.get("points") if isinstance(givens.get("points"), dict) else {}
        segments = givens.get("segments") if isinstance(givens.get("segments"), list) else []
        point_bits = []
        for label, coords in points.items():
            point_bits.append(f"{label}{_format_point_for_question(coords)}")
        seg_bits = []
        for idx, seg in enumerate(segments):
            if not isinstance(seg, dict):
                continue
            name = str(seg.get("name") or f"L{idx + 1}")
            seg_bits.append(f"({idx + 1})直線{name}")
        joined_points = "、".join(point_bits) if point_bits else "已知各點"
        joined_segs = " ".join(seg_bits) if seg_bits else "各線段"
        return f"設{joined_points}，試求下列直線的斜率。{joined_segs}。"

    if task_type == "classify_and_compare_figure_slopes":
        return (
            "(1) 請將 m = 0、m不存在、m > 0、m < 0，填入下列各圖形的斜率。"
            "(2) 設 m1、m2 分別為直線 L1、L2 的斜率，試比較各圖中 m1 與 m2 的大小。"
        )

    if task_type == "collinear_three_points_parameter_choice":
        pa = givens.get("point_a_display") or _format_point_for_question(givens.get("point_a"))
        pb = givens.get("point_b_display") or _format_point_for_question(givens.get("point_b"))
        pc = givens.get("point_c_display") or _format_point_for_question(givens.get("point_c"))
        param = givens.get("parameter_name") or "a"
        return f"設 {pa}、{pb}、{pc} 為共線之三點，則 {param} ="

    if task_type == "perpendicular_line_slope":
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:perpendicular_line_slope:reference_line")
        eq = givens["equation"]
        return f"與直線 {_latex_dollar(eq)} 垂直的直線之斜率為"

    if task_type == "line_through_intersection_parallel_to_line":
        if "equation_1" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_intersection_parallel_to_line:line_1")
        if "equation_2" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_intersection_parallel_to_line:line_2")
        if "equation_3" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_intersection_parallel_to_line:reference_line")
        eq1 = givens["equation_1"]
        eq2 = givens["equation_2"]
        eq3 = givens["equation_3"]
        return f"通過兩直線 {_latex_dollar(eq1)} 與 {_latex_dollar(eq2)} 的交點，並與直線 {_latex_dollar(eq3)} 平行的直線方程式為："

    if task_type == "perpendicular_bisector_application":
        if "point_a" not in givens:
            raise ValueError("required_line_task_slot_missing:perpendicular_bisector_application:point_a")
        if "point_b" not in givens:
            raise ValueError("required_line_task_slot_missing:perpendicular_bisector_application:point_b")
        pa = _format_point_for_question(givens["point_a"])
        pb = _format_point_for_question(givens["point_b"])
        return f"已知平面上兩點 A{pa}、B{pb}，求線段 AB 的垂直平分線（中垂線）方程式。"

    if task_type == "line_through_point_perpendicular_to_segment":
        if "point_b" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_perpendicular_to_segment:point_b")
        if "point_a" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_perpendicular_to_segment:point_a")
        if "point_c" not in givens:
            raise ValueError("required_line_task_slot_missing:line_through_point_perpendicular_to_segment:point_c")
        pb = _format_point_for_question(givens["point_b"])
        pa = _format_point_for_question(givens["point_a"])
        pc = _format_point_for_question(givens["point_c"])
        return f"若 A{pa}、B{pb}、C{pc} 為平面上三點，則過點 B 且與直線 AC 垂直的直線方程式為何？"

    if task_type == "distance_from_point_to_line":
        if "point" not in givens:
            raise ValueError("required_line_task_slot_missing:distance_from_point_to_line:point")
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:distance_from_point_to_line:equation")
        pt = _format_point_for_question(givens["point"])
        eq = givens["equation"]
        return f"試求平面上一點 {pt} 到直線 L : {eq} 的距離。"

    if task_type in (
        "distance_from_point_to_line_parameter",
        "distance_from_point_to_line_parameter_single_choice_scalar",
    ):
        if "point" not in givens:
            raise ValueError("required_line_task_slot_missing:distance_from_point_to_line_parameter:point")
        if "equation" not in givens:
            raise ValueError("required_line_task_slot_missing:distance_from_point_to_line_parameter:equation")
        if "distance" not in givens:
            raise ValueError("required_line_task_slot_missing:distance_from_point_to_line_parameter:distance")
        pt = _format_point_for_question(givens["point"])
        eq = givens["equation"]
        dist = givens["distance"]
        var_name = "k"
        if "a" in eq or "a" in str(givens.get("point")):
            var_name = "a"
        return f"若點 {pt} 到直線 L : {eq} 的距離為 {dist}，試求 {var_name} 的值。"

    if task_type == "compare_point_to_line_distances":
        if "point" not in givens:
            raise ValueError("required_line_task_slot_missing:compare_point_to_line_distances:point")
        if "equation_1" not in givens:
            raise ValueError("required_line_task_slot_missing:compare_point_to_line_distances:equation_1")
        if "equation_2" not in givens:
            raise ValueError("required_line_task_slot_missing:compare_point_to_line_distances:equation_2")
        pt = _format_point_for_question(givens["point"])
        eq1 = givens["equation_1"]
        eq2 = givens["equation_2"]
        target_direction = str(givens.get("target_direction") or "closer").strip().lower()
        if target_direction == "closer":
            return f"已知平面上一點 P{pt} 及兩直線 $L_1: {eq1}$、$L_2: {eq2}$，試問點 P 到哪一條直線的距離較近？"
        elif target_direction == "farther":
            return f"已知平面上一點 P{pt} 及兩直線 $L_1: {eq1}$、$L_2: {eq2}$，試問點 P 到哪一條直線的距離較遠？"
        else:
            return f"已知平面有一點 P{pt} 及兩直線 $L_1: {eq1}$ 與 $L_2: {eq2}$，試比較該點到兩直線的距離關係。"

    # 4. Fallbacks for standard Point-Slope / Two-Points / Horizontal / Vertical
    if task_type == "two_points" or ("point_a" in givens and "point_b" in givens):
        pa = givens["point_a"]
        pb = givens["point_b"]
        ax, ay = int(pa[0]), int(pa[1])
        bx, by = int(pb[0]), int(pb[1])
        if ax == bx:
            return (
                f"試求通過 $C({ax},\\,{ay})$ 與 $D({bx},\\,{by})$ 兩點之直線方程式。"
            )
        if ay == by:
            return (
                f"試求通過 $A({ax},\\,{ay})$ 與 $B({bx},\\,{by})$ 兩點之直線方程式。"
            )
        return (
            f"試求通過 $A({ax},\\,{ay})$ 與 $B({bx},\\,{by})$ 兩點之直線方程式。"
        )

    if task_type == "point_slope" or ("point" in givens and "slope" in givens):
        if "point" not in givens or "slope" not in givens:
            raise ValueError("required_line_task_slot_missing:point_slope:point_or_slope")
        point = givens["point"]
        slope = givens["slope"]
        px, py = int(point[0]), int(point[1])
        return (
            f"已知直線過點 $({px},\\,{py})$，斜率為 ${slope}$，求此直線方程式。"
        )

    if task_type == "horizontal_line" or line_type == "horizontal_line" or "y_intercept" in givens:
        y_val = givens.get("y_intercept")
        return f"寫出斜率為 0 且通過 y 軸上 {y_val} 的水平線方程式。"

    if task_type == "vertical_line" or line_type == "vertical_line" or "x_intercept" in givens:
        x_val = givens.get("x_intercept")
        return f"寫出鉛直且通過 x = {x_val} 的直線方程式。"

    raise ValueError(f"unsupported_line_equation_task_type:{task_type}")


def _build_choice_options(
    canonical: str,
    distractors: list[Any],
    *,
    seed_text: str,
) -> tuple[list[dict[str, str]], str]:
    unique_wrong: list[str] = []
    seen: set[str] = {canonical}
    for item in distractors:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        unique_wrong.append(text)

    option_texts = [canonical] + unique_wrong[:3]
    rng = random.Random(sum(ord(ch) for ch in seed_text))
    rng.shuffle(option_texts)

    choices: list[dict[str, str]] = []
    correct_label = "A"
    for index, text in enumerate(option_texts):
        label = chr(ord("A") + index)
        choices.append({"label": label, "text": text})
        if text == canonical:
            correct_label = label
    return choices, correct_label


def _prepare_choice_label_matrix_answer(
    matrix: dict[str, Any],
    *,
    domain_operation: str,
    component_id: str | None,
    answer_schema_key: str | None,
    problem_type_id: str | None,
) -> dict[str, Any]:
    """Inject ``correct_label`` before schema validation for choice-label matrices."""
    from core.gencode.answer_schema_registry import resolve_answer_schema_key

    op = str(domain_operation or "").strip()
    schema_key = resolve_answer_schema_key(
        answer_schema_key=answer_schema_key,
        domain_operation=op,
        problem_type_id=problem_type_id,
    )
    if schema_key != "choice_label":
        return matrix
    answer = matrix.get("answer")
    if not isinstance(answer, dict) or answer.get("correct_label"):
        return matrix
    display_answer = str(answer.get("canonical_form", answer.get("value", "")))
    _, correct_label = _build_choice_options(
        display_answer,
        matrix.get("distractors", []),
        seed_text=f"{op}|{display_answer}|{component_id or ''}",
    )
    prepared = dict(matrix)
    prepared["answer"] = dict(answer)
    prepared["answer"]["correct_label"] = correct_label
    return prepared


def _format_point_for_question(value: Any) -> str:
    if isinstance(value, dict):
        return f"$({value.get('x')}, {value.get('y')})$"
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return f"$({value[0]}, {value[1]})$"
    return "$()$"


def _normalize_labeled_choices(raw_choices: Any) -> list[dict[str, str]]:
    if not isinstance(raw_choices, list):
        return []
    choices: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_choices):
        if isinstance(raw, dict):
            label = str(raw.get("label") or chr(ord("A") + index)).strip()
            text = str(raw.get("text") or raw.get("value") or "").strip()
        else:
            label = chr(ord("A") + index)
            text = str(raw or "").strip()
        if not label or not text or text in seen:
            continue
        seen.add(text)
        choices.append({"label": label, "text": text})
    return choices


def _parse_fraction_text(value: Any) -> Fraction:
    if value is None or str(value).strip() == "":
        return Fraction(0, 1)
    return normalize_fraction_value(value)


def _format_fraction_text(value: Fraction) -> str:
    return fraction_to_plain(value)


def _build_x_intercept_choice_options(
    canonical: str,
    givens: dict[str, Any],
    *,
    seed_text: str,
) -> tuple[list[dict[str, str]], str]:
    correct = _parse_fraction_text(canonical)
    slope = _parse_fraction_text(givens.get("slope"))
    y_intercept = _parse_fraction_text(givens.get("y_intercept"))
    rng = random.Random(sum(ord(ch) for ch in seed_text))

    candidate_values: list[Fraction] = [
        correct,
        -correct,
        correct + 1,
        correct - 1,
        correct + Fraction(1, 2),
        correct - Fraction(1, 2),
        y_intercept,
        -y_intercept,
        slope,
        -slope,
    ]
    for offset in range(2, 10):
        candidate_values.append(correct + offset)
        candidate_values.append(correct - offset)

    wrong_values: list[Fraction] = []
    seen: set[Fraction] = {correct}
    for value in candidate_values:
        value = Fraction(value)
        if value in seen:
            continue
        seen.add(value)
        wrong_values.append(value)
        if len(wrong_values) >= 3:
            break
    while len(wrong_values) < 3:
        value = Fraction(rng.randint(-8, 8), rng.choice([1, 2, 3, 4, 5]))
        if value in seen:
            continue
        seen.add(value)
        wrong_values.append(value)

    option_values = [correct] + wrong_values[:3]
    rng.shuffle(option_values)

    choices: list[dict[str, str]] = []
    correct_label = "A"
    for index, value in enumerate(option_values):
        label = chr(ord("A") + index)
        text = _format_fraction_text(value)
        choices.append({"label": label, "text": text})
        if value == correct:
            correct_label = label
    return choices, correct_label


def _build_area_choice_options(
    canonical: str,
    *,
    seed_text: str,
) -> tuple[list[dict[str, str]], str]:
    correct = _parse_fraction_text(canonical)
    rng = random.Random(sum(ord(ch) for ch in seed_text))
    candidate_values: list[Fraction] = [
        correct,
        correct + 1,
        correct + 2,
        correct - 1,
        correct * 2,
        correct / 2 if correct != 0 else Fraction(1, 1),
        -correct,
    ]
    wrong_values: list[Fraction] = []
    seen: set[Fraction] = {correct}
    for value in candidate_values:
        value = Fraction(value)
        if value <= 0 or value in seen:
            continue
        seen.add(value)
        wrong_values.append(value)
        if len(wrong_values) >= 3:
            break
    while len(wrong_values) < 3:
        value = Fraction(rng.randint(1, 24), rng.choice([1, 2]))
        if value in seen:
            continue
        seen.add(value)
        wrong_values.append(value)

    option_values = [correct] + wrong_values[:3]
    rng.shuffle(option_values)
    choices: list[dict[str, str]] = []
    correct_label = "A"
    for index, value in enumerate(option_values):
        label = chr(ord("A") + index)
        text = _format_fraction_text(value)
        choices.append({"label": label, "text": text})
        if value == correct:
            correct_label = label
    return choices, correct_label


def _infer_math_objects(validation_facts: dict[str, Any]) -> list[str]:
    objects = ["coordinate_point", "linear_equation"]
    task_type = str(validation_facts.get("task_type") or "")
    if task_type.startswith("slope_intercept"):
        objects.append("slope_intercept_form")
    if task_type.startswith("intercept_form"):
        objects.append("intercept_form")
    if task_type == "triangle_area_bisector_line_equation":
        objects.extend(["triangle", "midpoint", "area_bisector"])
    if validation_facts.get("is_horizontal"):
        objects.append("horizontal_line")
    if validation_facts.get("is_vertical"):
        objects.append("vertical_line")
    return objects


def _format_givens_for_hint(givens: dict[str, Any]) -> list[str]:
    formatted: list[str] = []
    if "point_a" in givens and "point_b" in givens:
        formatted.append(f"A={tuple(givens['point_a'])}")
        formatted.append(f"B={tuple(givens['point_b'])}")
    if "point" in givens:
        formatted.append(f"point={tuple(givens['point'])}")
    if "slope" in givens:
        formatted.append(f"slope={givens['slope']}")
    if "y_intercept" in givens:
        formatted.append(f"y_intercept={givens['y_intercept']}")
    if "x_intercept" in givens:
        formatted.append(f"x_intercept={givens['x_intercept']}")
    if "equation" in givens:
        formatted.append(f"equation={givens['equation']}")
    return formatted


def _convert_cumulative_frequency_distribution_payload(
    matrix: dict[str, Any],
    *,
    op: str,
    presentation_mode: str | None = None,
    answer_type: str | None = None,
    problem_type_id: str | None = None,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Preserve cumulative-frequency contract fields (image, table, multi_part, MCQ)."""
    normalized = normalize_domain_matrix(matrix)
    givens = normalized["givens"]
    answer_obj = normalized["answer"]
    validation_facts = dict(normalized["validation_facts"])
    validation_facts.setdefault("domain_operation", op)

    question_text = str(
        matrix.get("question_text")
        or kwargs.get("question_text")
        or "閱讀下列累積次數分配資料，回答問題。"
    )
    resolved_answer_type = str(matrix.get("answer_type") or answer_type or "integer").strip()
    mode = str(
        presentation_mode
        or ("single_choice" if resolved_answer_type == "single_choice" else "short_answer")
    ).strip()

    contract_answer = matrix.get("answer")
    if isinstance(contract_answer, dict) and "value" in contract_answer:
        semantic_answer = contract_answer["value"]
    elif contract_answer is not None and not isinstance(contract_answer, dict):
        semantic_answer = contract_answer
    else:
        semantic_answer = answer_obj.get("value", answer_obj.get("canonical_form"))

    display_answer = (
        canonicalize_multi_part_display(semantic_answer)
        if resolved_answer_type == "multi_part"
        else str(answer_obj.get("canonical_form", semantic_answer))
    )

    image_base64 = str(matrix.get("image_base64") or normalized.get("image_base64") or "")
    table_data = matrix.get("table_data") if isinstance(matrix.get("table_data"), dict) else {}
    if not table_data and isinstance(normalized.get("table_data"), dict):
        table_data = normalized["table_data"]
    choices = list(matrix.get("choices") or normalized.get("choices") or [])
    subquestions = list(matrix.get("subquestions") or normalized.get("subquestions") or [])
    ui_contract = dict(matrix.get("ui_contract") or {})
    visual_spec = dict(matrix.get("visual_spec") or normalized.get("visual_spec") or {})
    visual_aids = list(matrix.get("visual_aids") or normalized.get("visual_aids") or [])

    payload_answer = semantic_answer
    payload_correct = semantic_answer
    checker = "integer_checker"
    equivalence = "numeric_exact"
    interaction_type = "expression"

    if resolved_answer_type == "multi_part":
        checker = "multi_part_answer_checker"
        equivalence = "multi_part_answer"
        answer_contract = {
            "presentation_mode": "short_answer",
            "answer_type": "multi_part",
            "answer_shape": "multi_part",
            "checker": checker,
            "checker_key": checker,
            "answer_equivalence": equivalence,
            "equivalence": equivalence,
            "semantic_answer": semantic_answer,
            "parts": [
                {
                    "key": str(sq.get("part") or f"part_{idx + 1}"),
                    "label": str(sq.get("part") or f"part_{idx + 1}"),
                    "checker": "integer_checker",
                    "equivalence_type": "numeric_exact",
                    "expected_answer": sq.get("expected_answer"),
                }
                for idx, sq in enumerate(subquestions)
            ],
            "ui_contract": ui_contract or {"response_mode": "multi_part", "text_input_enabled": True},
        }
    elif resolved_answer_type == "single_choice":
        interaction_type = "single_choice"
        correct_label = next(
            (c.get("label") for c in choices if str(c.get("text")) == str(validation_facts.get("semantic_answer", semantic_answer))),
            choices[0].get("label") if choices else "A",
        )
        payload_answer = correct_label
        payload_correct = correct_label
        answer_contract = {
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": validation_facts.get("semantic_answer", semantic_answer),
            "ui_contract": ui_contract or {"response_mode": "single_choice", "text_input_enabled": False},
        }
    else:
        answer_contract = {
            "presentation_mode": mode,
            "answer_type": resolved_answer_type,
            "checker": checker,
            "checker_key": checker,
            "answer_equivalence": equivalence,
            "equivalence": equivalence,
            "semantic_answer": semantic_answer,
            "ui_contract": ui_contract or {"response_mode": "text", "text_input_enabled": True},
        }

    from core.gencode.table_question_contract import normalize_table_question_payload

    cumulative_payload = {
        "question_text": question_text,
        "answer": payload_answer,
        "correct_answer": payload_correct,
        "display_answer": display_answer,
        "semantic_answer": semantic_answer,
        "semantic_answer_type": resolved_answer_type,
        "choices": choices,
        "options": [str(c.get("text", "")) for c in choices],
        "subquestions": subquestions,
        "table_data": table_data,
        "component_id": component_id,
        "textbook_example_id": textbook_example_id,
        "problem_type_id": problem_type_id or op,
        "domain_operation": op,
        "fixed_domain_key": "statistics.frequency_distribution",
        "source_kind": source_kind,
        "presentation_mode": mode,
        "answer_type": resolved_answer_type,
        "interaction_type": interaction_type,
        "auto_checkable": True,
        "grading_mode": "auto",
        "answer_contract": answer_contract,
        "ui_contract": answer_contract.get("ui_contract", ui_contract),
        "metadata": {
            "givens": givens,
            "raw_givens": givens,
            "target": display_answer,
            "derivation": [str(step) for step in normalized["explanation_steps"]],
            "presentation_mode": mode,
            "answer_type": resolved_answer_type,
            "semantic_answer": semantic_answer,
            "problem_type_id": problem_type_id or op,
            "domain_operation": op,
            "fixed_domain_key": "statistics.frequency_distribution",
            "component_id": component_id,
            "textbook_example_id": textbook_example_id,
        },
        "math_core": {
            "givens": givens,
            "raw_givens": givens,
            "target": display_answer,
            "math_objects": ["cumulative_frequency_graph", "cumulative_frequency_table"],
            "derivation": [str(step) for step in normalized["explanation_steps"]],
            "validation_facts": validation_facts,
        },
        "visual_spec": visual_spec,
        "visual_aids": visual_aids,
        "image_base64": image_base64,
        "validation_facts": validation_facts,
        "generator_key": generator_key or component_id,
        "explanation": matrix.get("explanation") or " ".join(str(s) for s in normalized["explanation_steps"]),
    }
    return _finalize_question_payload(normalize_table_question_payload(cumulative_payload))


_CUMULATIVE_FREQ_DIST_OPS = frozenset(
    {
        "cumulative_frequency_table_construction",
        "less_than_cumulative_frequency_reading",
        "greater_than_cumulative_frequency_reading",
        "class_frequency_from_cumulative_difference",
        "cumulative_frequency_graph_reading",
    }
)

_DESCRIPTIVE_STATS_OPS = frozenset(
    {
        "compute_arithmetic_mean_from_raw_values",
        "compute_arithmetic_mean_from_frequency_table",
        "compute_weighted_mean",
        "compute_median_from_raw_values",
        "compute_mode_from_raw_values",
        "compute_mode_from_frequency_table",
        "compute_range",
        "compute_population_variance",
        "compute_population_standard_deviation",
        "compute_sample_variance",
        "compute_sample_standard_deviation",
        "complete_descriptive_statistics_table",
        "compute_quartiles_and_iqr",
        "compare_dispersion",
        "conceptual_dispersion_judgment",
        "compute_linear_transform_median_and_range",
        # Empirical-rule / normal-distribution operations (added for
        # vh_數學B4_NormalDistributionAndEmpiricalRule components)
        "empirical_rule_probability",
        "empirical_rule_population_count",
        "compare_distribution_spread",
    }
)



_DESCRIPTIVE_MATRIX_REQUIRED = (
    "fixed_domain_key",
    "selected_operation",
    "required_capabilities",
    "answer_shape",
)


def _convert_descriptive_statistics_payload(
    matrix: dict[str, Any],
    *,
    op: str,
    presentation_mode: str | None = None,
    answer_type: str | None = None,
    problem_type_id: str | None = None,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
    domain_resolution: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    from core.gencode.descriptive_statistics_answer_contract import (
        DescriptiveStatisticsContractError,
        build_scaffold_payload_meta,
        normalize_answer_contract,
        validate_contract_dispatchable,
    )
    from core.gencode.table_question_contract import normalize_table_question_payload

    normalized = normalize_domain_matrix(matrix)
    missing = [field for field in _DESCRIPTIVE_MATRIX_REQUIRED if not str(matrix.get(field) or "").strip()]
    if missing:
        raise DescriptiveStatisticsContractError(
            f"descriptive_matrix_contract_missing:{','.join(missing)}"
        )

    givens = normalized["givens"]
    answer_obj = normalized["answer"]
    validation_facts = dict(normalized["validation_facts"])
    validation_facts.setdefault("domain_operation", op)
    answer_shape = str(matrix.get("answer_shape") or validation_facts.get("answer_shape") or "single_numeric")
    rounding_policy = dict(givens.get("rounding_policy") or matrix.get("rounding_policy") or {})
    field_specs = list(givens.get("field_specs") or matrix.get("field_specs") or [])
    semantic_answer = answer_obj.get("value", answer_obj.get("canonical_form"))
    question_text = str(givens.get("question_text") or matrix.get("question_text") or "依據資料求指定統計量。")
    ui_contract = dict(matrix.get("ui_contract") or {})
    table_data = dict(matrix.get("table_data") or normalized.get("visual_spec") or {})
    required_caps = list(matrix.get("required_capabilities") or [])
    matched_caps = list(matrix.get("matched_capabilities") or required_caps)
    fixed_domain_key = str(matrix.get("fixed_domain_key") or "statistics.descriptive_statistics")
    selected_operation = str(matrix.get("selected_operation") or op)
    source_data = {
        "raw_values": givens.get("raw_values"),
        "value_frequency_pairs": givens.get("value_frequency_pairs"),
        "grouped_frequency_table": givens.get("grouped_frequency_table"),
        "weights": givens.get("weights"),
    }

    answer_contract = normalize_answer_contract(
        semantic_answer,
        answer_shape,
        rounding_policy=rounding_policy,
        field_specs=field_specs or None,
    )
    dispatch_blockers = validate_contract_dispatchable(answer_contract)
    if dispatch_blockers:
        raise DescriptiveStatisticsContractError(
            f"answer_contract_not_dispatchable:{','.join(dispatch_blockers)}"
        )

    mode = str(
        presentation_mode
        or answer_contract.get("presentation_mode")
        or matrix.get("presentation_mode")
        or "short_answer"
    ).strip()
    resolved_answer_type = str(answer_contract.get("answer_type") or answer_type or "expression").strip()

    choice_bundle: dict[str, Any] | None = None
    if mode == "single_choice":
        from core.gencode.single_choice_contract import build_single_choice_contract

        answer_obj = normalized["answer"]
        semantic_for_choice = answer_obj.get("value", answer_obj.get("canonical_form"))
        canonical_text = str(
            answer_obj.get("canonical_form")
            or __import__(
                "core.domain.statistics.descriptive_statistics_core",
                fromlist=["format_numeric_answer"],
            ).format_numeric_answer(
                semantic_for_choice,
                dict(givens.get("rounding_policy") or rounding_policy or {}),
            )
        )
        distractors = list(
            matrix.get("distractors")
            or validation_facts.get("distractor_candidates")
            or []
        )
        generation_seed = kwargs.get("seed")
        if generation_seed is None and matrix.get("generation_seed") is not None:
            generation_seed = matrix.get("generation_seed")
        source_choices = list(
            kwargs.get("source_choices")
            or givens.get("source_choices")
            or matrix.get("source_choices")
            or []
        )
        source_answer_label = str(
            kwargs.get("source_answer_label")
            or givens.get("source_answer_label")
            or matrix.get("source_answer_label")
            or ""
        ).strip()
        preserve_source = bool(kwargs.get("preserve_source_choices"))
        if (
            not preserve_source
            and mode == "single_choice"
            and source_choices
            and re.fullmatch(r"[A-D]", source_answer_label)
        ):
            preserve_source = True
        choice_bundle = build_single_choice_contract(
            canonical_text,
            distractors,
            source_choices=source_choices or None,
            source_answer_label=source_answer_label or None,
            seed=generation_seed,
            preserve_source_choices=preserve_source,
        )
        resolved_answer_type = "single_choice"
        checker_key = "choice_label_checker"
        answer_contract = {
            "answer_shape": answer_shape,
            "answer_type": "single_choice",
            "checker_key": checker_key,
            "checker": checker_key,
            "equivalence_type": "choice_label",
            "answer_equivalence": "choice_label",
            "canonical_answer": choice_bundle["canonical_answer"],
            "semantic_answer": choice_bundle["canonical_answer"],
            "tolerance": None,
            "rounding_policy": rounding_policy,
            "field_specs": [],
            "presentation_mode": "single_choice",
            "ui_contract": dict(choice_bundle.get("ui_contract") or {}),
        }
        dispatch_blockers = validate_contract_dispatchable(answer_contract)
        if dispatch_blockers:
            raise DescriptiveStatisticsContractError(
                f"answer_contract_not_dispatchable:{','.join(dispatch_blockers)}"
            )
    else:
        checker_key = str(answer_contract.get("checker_key") or "")

    if choice_bundle:
        payload_answer = choice_bundle["correct_answer"]
        payload_correct = choice_bundle["correct_answer"]
        display_text = str(choice_bundle["canonical_answer"])
    else:
        display_answer = answer_contract.get("canonical_answer")
        if isinstance(display_answer, list):
            display_text = ", ".join(str(v) for v in display_answer)
            payload_answer = display_answer
            payload_correct = display_answer
        elif isinstance(display_answer, dict):
            display_text = "; ".join(f"{k}={v}" for k, v in display_answer.items())
            payload_answer = display_answer
            payload_correct = display_answer
        else:
            display_text = str(answer_obj.get("canonical_form") or display_answer or "")
            payload_answer = display_text
            payload_correct = display_text

    answer_contract.update(
        {
            "presentation_mode": mode,
            "answer_type": resolved_answer_type,
            "answer_shape": answer_shape,
            "semantic_answer": semantic_answer,
        }
    )
    if answer_contract.get("ui_contract"):
        ui_contract.update(dict(answer_contract["ui_contract"]))
    matrix_ui = dict(matrix.get("ui_contract") or {})
    if matrix_ui.get("field_groups") and not ui_contract.get("field_groups"):
        ui_contract["field_groups"] = list(matrix_ui.get("field_groups") or [])

    derivation = [str(step) for step in normalized["explanation_steps"]]
    resolution = dict(domain_resolution or matrix.get("domain_resolution") or {})
    resolution.setdefault("fixed_domain_key", fixed_domain_key)
    resolution.setdefault("selected_operation", selected_operation)
    resolution.setdefault("required_capabilities", required_caps)
    resolution.setdefault("matched_capabilities", matched_caps)
    resolution.setdefault("resolution_source", matrix.get("resolution_source") or "derived_capability_match")
    resolution.setdefault("binding_status", matrix.get("binding_status") or "derived")
    try:
        from core.registry.taxonomy_registry import REGISTRY_REVISION

        resolution.setdefault("registry_revision", REGISTRY_REVISION)
    except Exception:
        pass

    payload = {
        "question_text": question_text,
        "answer": payload_answer,
        "correct_answer": payload_correct,
        "display_answer": display_text,
        "choices": list(choice_bundle.get("choices") or []) if choice_bundle else [],
        "options": (
            [str(c.get("text") or "") for c in choice_bundle.get("choices") or []]
            if choice_bundle
            else []
        ),
        "component_id": component_id,
        "textbook_example_id": textbook_example_id,
        "problem_type_id": problem_type_id or selected_operation,
        "domain_operation": selected_operation,
        "selected_operation": selected_operation,
        "fixed_domain_key": fixed_domain_key,
        "source_kind": source_kind,
        "presentation_mode": mode,
        "answer_type": resolved_answer_type,
        "answer_shape": answer_shape,
        "interaction_type": "single_choice" if choice_bundle else mode,
        "auto_checkable": True,
        "grading_mode": "auto",
        "answer_contract": answer_contract,
        "ui_contract": ui_contract,
        "checker_key": checker_key,
        "equivalence_type": str(answer_contract.get("equivalence_type") or ""),
        "rounding_policy": rounding_policy,
        "source_data": source_data,
        "metadata": {
            "givens": givens,
            "raw_givens": givens,
            "target": givens.get("target_measure") or validation_facts.get("target_measure"),
            "derivation": derivation,
            "presentation_mode": mode,
            "answer_type": resolved_answer_type,
            "answer_shape": answer_shape,
            "problem_type_id": problem_type_id or selected_operation,
            "domain_operation": selected_operation,
            "selected_operation": selected_operation,
            "fixed_domain_key": fixed_domain_key,
            "required_capabilities": required_caps,
            "matched_capabilities": matched_caps,
            "component_id": component_id,
            "textbook_example_id": textbook_example_id,
            "rounding_policy": rounding_policy,
            "source_data": source_data,
            "domain_resolution": resolution,
        },
        "math_core": {
            "givens": givens,
            "raw_givens": givens,
            "target": semantic_answer,
            "math_objects": ["descriptive_statistics"],
            "derivation": derivation,
            "validation_facts": validation_facts,
        },
        "visual_spec": table_data,
        "table_data": table_data,
        "validation_facts": validation_facts,
        "generator_key": generator_key or component_id,
        "subquestions": _subquestions_from_multi_field_contract(
            answer_contract,
            list(matrix.get("subquestions") or []),
        )
        if answer_contract.get("parts")
        else list(matrix.get("subquestions") or []),
        "domain_resolution": resolution,
    }
    if choice_bundle:
        payload["checker"] = "choice_label_checker"
        payload["checker_key"] = "choice_label_checker"
        ui_contract.update(dict(choice_bundle.get("ui_contract") or {}))
        payload["ui_contract"] = ui_contract
    if answer_shape == "table_fill" and table_data.get("blank_cells"):
        payload = normalize_table_question_payload(payload)
        payload["answer_contract"] = dict(payload.get("answer_contract") or answer_contract)
        payload["presentation_mode"] = "table_fill"
        payload["answer_type"] = str(payload["answer_contract"].get("answer_type") or "multi_part")
    payload["explanation"] = "\n".join(derivation)
    payload["scaffold_payload_meta"] = build_scaffold_payload_meta(payload)
    return _finalize_question_payload(payload)


def _convert_coordinate_pair_matrix_to_question_payload(
    matrix: dict[str, Any],
    *,
    presentation_mode: str | None = None,
    answer_type: str | None = None,
    problem_type_id: str | None = None,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
    domain_operation: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Convert a coordinate-pair domain matrix (midpoint, centroid, division point) to a question payload."""
    # Extract the coordinate answer from V3 matrix answer dict or legacy raw payload
    answer_raw = matrix.get("answer")
    if isinstance(answer_raw, dict):
        coord = (
            answer_raw.get("point")
            or answer_raw.get("coordinate")
            or answer_raw.get("value")
            or answer_raw.get("canonical_form")
            or answer_raw.get("correct_label")
        )
    else:
        coord = str(answer_raw) if answer_raw is not None else None

    # Fallback to correct_answer / top-level keys
    if not coord:
        coord = matrix.get("correct_answer") or matrix.get("answer")
        if isinstance(coord, dict):
            coord = coord.get("point") or coord.get("coordinate") or coord.get("value")

    coord = str(coord).strip() if coord else ""

    question_text = str(
        matrix.get("question_text") or matrix.get("question")
        or (matrix.get("givens") or {}).get("question_text") or ""
    ).strip()

    mode = str(presentation_mode or matrix.get("presentation_mode") or "short_answer").strip()
    op = str(domain_operation or "").strip()
    validation_facts = dict(matrix.get("validation_facts") or {})
    if op:
        validation_facts.setdefault("domain_operation", op)
        validation_facts.setdefault("task_type", op)
    explanation_steps = matrix.get("explanation_steps") or []

    # Single-choice path
    if mode == "single_choice":
        import random as _random
        choices_raw = matrix.get("distractors") or matrix.get("choices") or []
        labels = ["A", "B", "C", "D"]
        if choices_raw and isinstance(choices_raw, list):
            all_opts = [coord] + [str(x) for x in choices_raw if str(x) != coord]
        else:
            all_opts = [coord]
        _random.shuffle(all_opts)
        correct_label = ""
        choices = []
        for i, opt in enumerate(all_opts[:4]):
            lbl = labels[i]
            choices.append({"label": lbl, "text": opt, "value": opt})
            if opt == coord:
                correct_label = lbl
        answer_contract = {
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence_type": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": correct_label,
        }
        return {
            "question_text": question_text,
            "answer": correct_label,
            "correct_answer": correct_label,
            "display_answer": correct_label,
            "choices": choices,
            "options": [c["text"] for c in choices],
            "component_id": component_id or "",
            "textbook_example_id": textbook_example_id,
            "problem_type_id": problem_type_id or op,
            "source_kind": source_kind or "",
            "presentation_mode": mode,
            "answer_type": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "equivalence": "choice_label",
            "equivalence_type": "choice_label",
            "interaction_type": "single_choice",
            "auto_checkable": True,
            "grading_mode": "auto",
            "answer_contract": answer_contract,
            "metadata": {"target": coord, "domain_operation": op},
            "math_core": {"target": coord, "domain_operation": op},
            "visual_spec": matrix.get("visual_spec") or {"kind": "no_visual"},
            "visual_aids": [],
            "image_base64": None,
            "validation_facts": validation_facts,
            "generator_key": generator_key or component_id or "",
        }

    # Short-answer path
    answer_contract = {
        "presentation_mode": mode,
        "answer_type": "coordinate_pair",
        "checker": "coordinate_pair_checker",
        "checker_key": "coordinate_pair_checker",
        "answer_equivalence": "coordinate_pair_equivalence",
        "equivalence_type": "coordinate_pair_equivalence",
        "equivalence": "coordinate_pair_equivalence",
        "semantic_answer": coord,
    }
    return {
        "question_text": question_text,
        "answer": coord,
        "correct_answer": coord,
        "display_answer": coord,
        "choices": [],
        "options": [],
        "component_id": component_id or "",
        "textbook_example_id": textbook_example_id,
        "problem_type_id": problem_type_id or op,
        "source_kind": source_kind or "",
        "presentation_mode": mode,
        "answer_type": "coordinate_pair",
        "checker": "coordinate_pair_checker",
        "checker_key": "coordinate_pair_checker",
        "equivalence": "coordinate_pair_equivalence",
        "equivalence_type": "coordinate_pair_equivalence",
        "interaction_type": "short_answer",
        "auto_checkable": True,
        "grading_mode": "auto",
        "answer_contract": answer_contract,
        "metadata": {"target": coord, "domain_operation": op},
        "math_core": {"target": coord, "domain_operation": op},
        "visual_spec": matrix.get("visual_spec") or {"kind": "no_visual"},
        "visual_aids": [],
        "image_base64": None,
        "validation_facts": validation_facts,
        "generator_key": generator_key or component_id or "",
        "explanation": "\n".join(str(s) for s in explanation_steps) if explanation_steps else "",
    }


def convert_domain_matrix_to_question_payload(
    matrix: dict[str, Any],
    *,
    presentation_mode: str | None = None,
    answer_type: str | None = None,
    problem_type_id: str | None = None,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
    domain_operation: str | None = None,
    answer_schema_key: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Convert a fixed-domain Full Matrix Dictionary into a runtime payload.

    Coordinate-geometry matrices keep their existing specialized adapter. Other
    domains use a conservative generic adapter that preserves the Full Matrix
    evidence and does not perform cross-domain routing.
    """
    op = str(domain_operation or kwargs.get("domain_operation") or "").strip()
    if op in {"draw_constant_function_graph", "draw_linear_function_graph"}:
        return _finalize_question_payload(
            _convert_line_graph_drawing_payload(
                matrix,
                domain_operation=op,
                component_id=component_id,
                textbook_example_id=textbook_example_id,
                **kwargs,
            )
        )
    if op == "graph_based_linear_application_inverse":
        return _finalize_question_payload(
            _convert_graph_based_linear_application_inverse_payload(
                matrix,
                component_id=component_id,
                textbook_example_id=textbook_example_id,
                source_kind=source_kind,
                generator_key=generator_key,
            )
        )
    if op == "linear_equation_from_two_points_choice":
        return _finalize_question_payload(
            _convert_linear_equation_from_two_points_choice_payload(
                matrix,
                component_id=component_id,
                textbook_example_id=textbook_example_id,
                source_kind=source_kind,
                generator_key=generator_key,
            )
        )
    if op == "linear_graph_feasibility_choice":
        return _finalize_question_payload(
            _convert_linear_graph_feasibility_choice_payload(
                matrix,
                component_id=component_id,
                textbook_example_id=textbook_example_id,
                source_kind=source_kind,
                generator_key=generator_key,
            )
        )
    if op == "robust_budget_feasibility_choice":
        return _finalize_question_payload(
            _convert_robust_budget_feasibility_choice_payload(
                matrix,
                component_id=component_id,
                textbook_example_id=textbook_example_id,
                source_kind=source_kind,
                generator_key=generator_key,
            )
        )
    if op == "graph_based_linear_model_equation":
        return _finalize_question_payload(
            _convert_graph_based_linear_model_equation_payload(
                matrix,
                component_id=component_id,
                textbook_example_id=textbook_example_id,
                source_kind=source_kind,
                generator_key=generator_key,
            )
        )
    if op == "graph_intercepts_and_linear_equation":
        return _finalize_question_payload(
            _convert_graph_intercepts_and_linear_equation_payload(
                matrix,
                component_id=component_id,
                textbook_example_id=textbook_example_id,
                **kwargs
            )
        )
    if op == "graph_based_tiered_linear_application_multi_part":
        return _finalize_question_payload(
            _convert_graph_based_tiered_linear_application_multi_part_payload(
                matrix,
                component_id=component_id,
                textbook_example_id=textbook_example_id,
                **kwargs,
            )
        )
    if op in _DESCRIPTIVE_STATS_OPS:
        # NOTE: _convert_descriptive_statistics_payload already calls
        # _finalize_question_payload internally (at its own return path).
        # Do NOT wrap it again here — double finalize corrupts single_choice
        # choices via the second normalize_single_choice_payload pass.
        return _convert_descriptive_statistics_payload(
            matrix,
            op=op,
            presentation_mode=presentation_mode,
            answer_type=answer_type,
            problem_type_id=problem_type_id,
            component_id=component_id,
            textbook_example_id=textbook_example_id,
            source_kind=source_kind,
            generator_key=generator_key,
            **kwargs,
        )
    if op in _CUMULATIVE_FREQ_DIST_OPS:
        return _finalize_question_payload(
            _convert_cumulative_frequency_distribution_payload(
            matrix,
            op=op,
            presentation_mode=presentation_mode,
            answer_type=answer_type,
            problem_type_id=problem_type_id,
            component_id=component_id,
            textbook_example_id=textbook_example_id,
            source_kind=source_kind,
            generator_key=generator_key,
            **kwargs,
        ))
    _COORDINATE_PAIR_OPS = {
        "compute_midpoint_coordinates",
        "compute_centroid_coordinates",
        "compute_internal_division_point_coordinates",
        "compute_external_division_point_coordinates",
        "compute_division_point_coordinates",
        "compute_section_point_coordinates",
        "collinear_trisection_coordinate",
    }
    if op in _COORDINATE_PAIR_OPS:
        return _finalize_question_payload(
            _convert_coordinate_pair_matrix_to_question_payload(
                matrix,
                presentation_mode=presentation_mode,
                answer_type=answer_type or "coordinate_pair",
                problem_type_id=problem_type_id,
                component_id=component_id,
                textbook_example_id=textbook_example_id,
                source_kind=source_kind,
                generator_key=generator_key,
                domain_operation=op,
                **kwargs,
            )
        )
    if op in {
        "two_points",
        "point_slope",
        "horizontal_line",
        "vertical_line",
        "oblique_line",
        "slope_intercept_equation",
        "slope_intercept_find_x_intercept",
        "slope_intercept_read_slope_and_intercept",
        "intercept_form_equation",
        "intercept_form_triangle_area",
        "intercept_form_equation_and_triangle_area",
        "intercept_form_from_intercept_sum_and_slope",
        "parabola_secant_parallel_line_choice",
        "triangle_area_bisector_line_equation",
        "slope_from_general_or_intercept_form",
        "slope_from_general_form",
        "slope_of_horizontal_or_vertical_line",
        "line_through_point_parallel_to_line",
        "line_through_point_perpendicular_to_line",
        "parallel_line_slope",
        "perpendicular_line_slope",
        "parallel_condition_parameter",
        "perpendicular_condition_parameter",
        "compare_line_slopes",
        "line_through_intersection_parallel_to_line",
        "line_through_point_perpendicular_to_segment",
        "perpendicular_bisector_application",
        "coordinate_geometry_word_problem",
        "slope_from_two_points",
        "solve_parameter_from_known_slope",
        "solve_parameter_from_known_slope_choice",
        "collinear_three_points_parameter",
        "non_triangle_collinear_parameter",
        "parallel_segments_parameter",
        "perpendicular_segments_parameter",
        "perpendicular_two_point_lines_parameter",
        "triangle_right_angle_verification",
        "collinear_three_points_parameter_choice",
        "parallel_segments_parameter_choice",
        "parallel_two_point_lines_parameter_choice",
        "parallel_and_perpendicular_slopes_from_reference",
        "perpendicular_slope_quadrant_choice",
        "slopes_of_named_segments",
        "classify_and_compare_figure_slopes",
        "distance_from_point_to_line",
        "distance_from_point_to_line_parameter",
        "distance_from_point_to_line_parameter_single_choice_scalar",
        "compare_point_to_line_distances",
        "distance_between_parallel_lines",
        "solve_parameter_from_parallel_distance",
        "construct_parallel_line_at_distance",
        "parallel_lines_distance_single_choice",
        "area_using_parallel_distance",
    }:
        return _finalize_question_payload(
            convert_line_equation_matrix_to_question_payload(
            matrix,
            presentation_mode=presentation_mode,
            answer_type=answer_type,
            problem_type_id=problem_type_id,
            component_id=component_id,
            textbook_example_id=textbook_example_id,
            source_kind=source_kind,
            generator_key=generator_key,
            answer_schema_key=answer_schema_key,
            domain_operation=op,
            **kwargs,
        ))

    matrix = _prepare_choice_label_matrix_answer(
        matrix,
        domain_operation=op,
        component_id=component_id,
        answer_schema_key=answer_schema_key,
        problem_type_id=problem_type_id,
    )
    normalized = normalize_domain_matrix(
        matrix,
        answer_schema_key=answer_schema_key,
        domain_operation=op,
        problem_type_id=problem_type_id,
        **kwargs
    )
    answer = normalized["answer"]
    givens = normalized["givens"]
    validation_facts = dict(normalized["validation_facts"])
    if op:
        validation_facts.setdefault("domain_operation", op)
        validation_facts.setdefault("task_type", op)
    semantic_answer = answer.get("value", answer.get("canonical_form"))
    display_answer = str(answer.get("canonical_form", semantic_answer))
    mode = str(presentation_mode or "short_answer").strip()
    resolved_answer_type = str(answer_type or "integer").strip()
    table_chart_ops = {
        "read_category_value",
        "compare_category_values",
        "calculate_total_ratio_percent",
        "validate_chart_statement",
        "cumulative_above_fail_count",
        "cumulative_above_interval_count",
        "cumulative_below_interval_count",
    }
    if op in table_chart_ops or validation_facts.get("domain_operation") in table_chart_ops:
        operation = str(op or validation_facts.get("domain_operation") or problem_type_id or "read_category_value")
        cumulative_ops = {
            "cumulative_above_fail_count",
            "cumulative_above_interval_count",
            "cumulative_below_interval_count",
        }
        if operation in cumulative_ops:
            story = str(givens.get("story_context") or "統計資料")
            unit = str(givens.get("variable_unit") or "")
            direction = str(givens.get("cumulative_direction") or validation_facts.get("cumulative_direction") or "above")
            chart_phrase = "以上累積次數分配折線圖" if direction == "above" else "以下累積次數分配折線圖"
            if operation == "cumulative_above_fail_count":
                threshold = int(validation_facts.get("threshold") or givens.get("threshold") or 60)
                question_text = (
                    f"{story}的{chart_phrase}如下圖所示，試問：以{threshold}{unit}為準，不及格者有多少人？"
                )
            elif operation == "cumulative_above_interval_count":
                low = int(validation_facts.get("interval_low") or givens.get("interval_low") or 70)
                high = int(validation_facts.get("interval_high") or givens.get("interval_high") or 80)
                prefix = "接續上題，" if int(textbook_example_id or 0) == 3885 else ""
                question_text = (
                    f"{prefix}{story}的{chart_phrase}如下圖所示，成績在{low}～{high}{unit}有多少人？"
                )
            else:
                total = int(validation_facts.get("total_population") or givens.get("total_population") or 40)
                low = int(validation_facts.get("interval_low") or givens.get("interval_low") or 30)
                high = int(validation_facts.get("interval_high") or givens.get("interval_high") or 40)
                if "員工" in story or unit == "歲":
                    question_text = (
                        f"依某公司{total}名員工的年齡繪製{chart_phrase}如下圖所示，"
                        f"請問年齡在{low}～{high}{unit}有多少人？"
                    )
                else:
                    question_text = (
                        f"依{story}共{total}名員工繪製{chart_phrase}如下圖所示，"
                        f"請問年齡在{low}～{high}{unit}有多少人？"
                    )
            semantic_answer = answer.get("value", validation_facts.get("answer_value"))
            display_answer = str(semantic_answer)
            resolved_answer_type = "integer"
            rows = normalized.get("visual_spec", {}).get("rows") or []
            choices: list[dict[str, str]] = []
            options: list[str] = []
            payload_answer = semantic_answer
            payload_correct = semantic_answer
            answer_contract = {
                "presentation_mode": mode,
                "answer_type": resolved_answer_type,
                "checker": "integer_checker",
                "checker_key": "integer_checker",
                "answer_equivalence": "numeric_exact",
                "equivalence": "numeric_exact",
                "semantic_answer": semantic_answer,
            }
            if mode == "single_choice":
                choices, correct_label = _build_choice_options(
                    display_answer,
                    normalized.get("distractors", []),
                    seed_text=f"{operation}|{display_answer}|{component_id or ''}",
                )
                options = [str(choice["text"]) for choice in choices]
                payload_answer = correct_label
                payload_correct = correct_label
                answer_contract = {
                    "presentation_mode": "single_choice",
                    "answer_type": "single_choice",
                    "answer_value_type": "choice_label",
                    "semantic_answer_type": resolved_answer_type,
                    "checker": "choice_label_checker",
                    "checker_key": "choice_label_checker",
                    "answer_equivalence": "choice_label",
                    "equivalence": "choice_label",
                    "semantic_answer": semantic_answer,
                }
            canonical_type = "single_choice" if mode == "single_choice" else resolved_answer_type
            canonical_value_type = "choice_label" if mode == "single_choice" else resolved_answer_type
            return _finalize_question_payload({
                "question_text": question_text,
                "answer": payload_answer,
                "correct_answer": payload_correct,
                "display_answer": display_answer,
                "semantic_answer": semantic_answer,
                "semantic_answer_type": resolved_answer_type,
                "choices": choices,
                "options": options,
                "component_id": component_id,
                "textbook_example_id": textbook_example_id,
                "problem_type_id": operation,
                "domain_operation": operation,
                "fixed_domain_key": "statistics.table_chart",
                "source_kind": source_kind,
                "presentation_mode": mode,
                "answer_type": canonical_type,
                "answer_value_type": canonical_value_type,
                "checker": answer_contract["checker"],
                "checker_key": answer_contract["checker_key"],
                "interaction_type": "single_choice" if mode == "single_choice" else "expression",
                "auto_checkable": True,
                "grading_mode": "auto",
                "answer_contract": answer_contract,
                "metadata": {
                    "givens": givens,
                    "raw_givens": givens,
                    "target": display_answer,
                    "derivation": [str(step) for step in normalized["explanation_steps"]],
                    "presentation_mode": mode,
                    "answer_type": canonical_type,
                    "answer_value_type": canonical_value_type,
                    "semantic_answer_type": resolved_answer_type,
                    "semantic_answer": semantic_answer,
                    "problem_type_id": operation,
                    "domain_operation": operation,
                    "fixed_domain_key": "statistics.table_chart",
                    "component_id": component_id,
                    "textbook_example_id": textbook_example_id,
                    "interaction_type": "single_choice" if mode == "single_choice" else "expression",
                    "auto_checkable": True,
                    "grading_mode": "auto",
                },
                "math_core": {
                    "givens": givens,
                    "raw_givens": givens,
                    "target": display_answer,
                    "math_objects": ["cumulative_frequency_polygon", "statistical_chart"],
                    "derivation": [str(step) for step in normalized["explanation_steps"]],
                    "validation_facts": validation_facts,
                },
                "visual_spec": normalized["visual_spec"],
                "visual_aids": normalized.get("visual_aids", matrix.get("visual_aids", [])),
                "image_base64": normalized.get("image_base64", matrix.get("image_base64", "")),
                "validation_facts": validation_facts,
                "generator_key": generator_key or component_id,
                "story_context": story,
            })

        rows = normalized.get("visual_spec", {}).get("rows") or []
        value_map = validation_facts.get("value_map") or givens.get("value_map") or {}
        categories = list(givens.get("categories") or list(value_map.keys()) or [])
        if not value_map and rows:
            value_map = {str(row[0]): int(row[1]) for row in rows if len(row) >= 2}
            categories = list(value_map.keys())
        target_label = str(validation_facts.get("target_label") or givens.get("target_label") or (categories[0] if categories else "A"))
        compare_a = str(validation_facts.get("compare_a") or givens.get("compare_a") or (categories[0] if categories else "A"))
        compare_b = str(validation_facts.get("compare_b") or givens.get("compare_b") or (categories[1] if len(categories) > 1 else compare_a))
        if operation == "compare_category_values":
            question_text = f"閱讀下列統計表，比較 {compare_a} 與 {compare_b} 的數值，兩者相差多少？"
            semantic_answer = answer.get("value", validation_facts.get("answer_value"))
            display_answer = str(semantic_answer)
            resolved_answer_type = "integer" if isinstance(semantic_answer, int) else resolved_answer_type
        elif operation == "calculate_total_ratio_percent":
            question_text = f"閱讀下列統計表，求 {target_label} 佔總量的百分比。"
            semantic_answer = answer.get("value", validation_facts.get("answer_value"))
            display_answer = str(answer.get("canonical_form", semantic_answer))
        elif operation == "validate_chart_statement":
            statement = str(validation_facts.get("statement") or givens.get("statement") or "")
            question_text = f"閱讀下列統計表，判斷敘述「{statement}」是否正確。"
            semantic_answer = bool(answer.get("value", validation_facts.get("answer_value")))
            display_answer = "true" if semantic_answer else "false"
            resolved_answer_type = "boolean"
        else:
            question_text = f"閱讀下列統計表，求 {target_label} 的數值。"
            semantic_answer = answer.get("value", validation_facts.get("answer_value"))
            display_answer = str(semantic_answer)
            resolved_answer_type = "integer" if isinstance(semantic_answer, int) else resolved_answer_type

        choices: list[dict[str, str]] = []
        options: list[str] = []
        payload_answer = semantic_answer
        payload_correct = semantic_answer
        checker = "integer_checker" if resolved_answer_type in {"integer", "numeric"} else "text_short_checker"
        equivalence = "numeric_exact" if checker == "integer_checker" else "exact_string"
        answer_contract = {
            "presentation_mode": mode,
            "answer_type": resolved_answer_type,
            "checker": checker,
            "checker_key": checker,
            "answer_equivalence": equivalence,
            "equivalence": equivalence,
            "semantic_answer": semantic_answer,
        }
        if mode == "single_choice":
            choices, correct_label = _build_choice_options(
                display_answer,
                normalized.get("distractors", []),
                seed_text=f"{operation}|{display_answer}|{component_id or ''}",
            )
            options = [str(choice["text"]) for choice in choices]
            payload_answer = correct_label
            payload_correct = correct_label
            answer_contract = {
                "presentation_mode": "single_choice",
                "answer_type": "single_choice",
                "answer_value_type": "choice_label",
                "semantic_answer_type": resolved_answer_type,
                "checker": "choice_label_checker",
                "checker_key": "choice_label_checker",
                "answer_equivalence": "choice_label",
                "equivalence": "choice_label",
                "semantic_answer": semantic_answer,
            }
        canonical_type = "single_choice" if mode == "single_choice" else resolved_answer_type
        canonical_value_type = "choice_label" if mode == "single_choice" else resolved_answer_type
        return _finalize_question_payload({
            "question_text": question_text,
            "answer": payload_answer,
            "correct_answer": payload_correct,
            "display_answer": display_answer,
            "semantic_answer": semantic_answer,
            "semantic_answer_type": resolved_answer_type,
            "choices": choices,
            "options": options,
            "component_id": component_id,
            "textbook_example_id": textbook_example_id,
            "problem_type_id": operation,
            "domain_operation": operation,
            "fixed_domain_key": "statistics.table_chart",
            "source_kind": source_kind,
            "presentation_mode": mode,
            "answer_type": canonical_type,
            "answer_value_type": canonical_value_type,
            "checker": answer_contract["checker"],
            "checker_key": answer_contract["checker_key"],
            "interaction_type": "single_choice" if mode == "single_choice" else "expression",
            "auto_checkable": True,
            "grading_mode": "auto",
            "answer_contract": answer_contract,
            "metadata": {
                "givens": givens,
                "raw_givens": givens,
                "target": display_answer,
                "derivation": [str(step) for step in normalized["explanation_steps"]],
                "presentation_mode": mode,
                "answer_type": canonical_type,
                "answer_value_type": canonical_value_type,
                "semantic_answer_type": resolved_answer_type,
                "semantic_answer": semantic_answer,
                "problem_type_id": operation,
                "domain_operation": operation,
                "fixed_domain_key": "statistics.table_chart",
                "component_id": component_id,
                "textbook_example_id": textbook_example_id,
                "interaction_type": "single_choice" if mode == "single_choice" else "expression",
                "auto_checkable": True,
                "grading_mode": "auto",
            },
            "math_core": {
                "givens": givens,
                "raw_givens": givens,
                "target": display_answer,
                "math_objects": ["statistical_chart", "category_value"],
                "derivation": [str(step) for step in normalized["explanation_steps"]],
                "validation_facts": validation_facts,
            },
            "visual_spec": normalized["visual_spec"],
            "visual_aids": normalized.get("visual_aids", matrix.get("visual_aids", [])),
            "image_base64": normalized.get("image_base64", matrix.get("image_base64", "")),
            "validation_facts": validation_facts,
            "generator_key": generator_key or component_id,
        })
    question_text = str(kwargs.get("question_text") or "")
    if not question_text:
        if op == "solve_basic_absolute_value_equation":
            rhs = givens.get("rhs", 8)
            question_text = f"數線上，若$\\left| x \\right|={rhs}$，試求x之值。"
        elif op == "solve_basic_absolute_value_equation_no_solution":
            rhs = givens.get("rhs", -3)
            question_text = f"數線上，若$\\left| x \\right|={rhs}$，試求x之值。"
        elif op == "number_line_distance_between_two_points":
            a = givens.get("a", -3)
            b = givens.get("b", 7)
            question_text = f"已知數線上兩點$A\\left( {a} \\right)$、$B\\left( {b} \\right)$，試求A、B兩點的距離。"
        elif op == "absolute_value_inequality_zero_center_basic":
            a = givens.get("a", 1)
            op_sign = givens.get("op", "<")
            c = givens.get("c", 5)
            ax_text = "x" if a == 1 else f"{a}x"
            question_text = f"解不等式：$\\left| {ax_text} \\right| {op_sign} {c}$。"
        elif op == "absolute_value_inequality_shifted_basic":
            b_val = givens.get("b", -3)
            op_sign = givens.get("op", "<")
            c = givens.get("c", 5)
            b_text = f"+ {b_val}" if b_val >= 0 else f"- {abs(b_val)}"
            question_text = f"解不等式：$\\left| x {b_text} \\right| {op_sign} {c}$。"
        elif op == "absolute_value_inequality_linear_expression_basic":
            a = givens.get("a", 1)
            b = givens.get("b", 0)
            op_sign = givens.get("op", "<")
            c = givens.get("c", 5)
            b_text = f"+ {b}" if b >= 0 else f"- {abs(b)}"
            question_text = f"解不等式：$\\left| {a}x {b_text} \\right| {op_sign} {c}$。"
        elif op == "absolute_value_inequality_interval_interpretation":
            d = givens.get("d", 7)
            a = givens.get("a", 0)
            c = givens.get("c", 28)
            e = givens.get("e", 5)
            a_part = f"- {a}" if a >= 0 else f"+ {abs(a)}"
            question_text = f"若不等式 $\\left| {d}x {a_part} \\right| < {c}$ 之解為 $b < x < {e}$，則點 $(b, a)$ 屬於哪一象限？"
        elif op == "compute_distance_between_two_points":
            x1 = givens.get("x1")
            y1 = givens.get("y1")
            x2 = givens.get("x2")
            y2 = givens.get("y2")
            question_text = f"已知坐標平面上兩點 $A({x1}, {y1})$、$B({x2}, {y2})$，試求 $A$、$B$ 兩點的距離。"
        elif op == "solve_unknown_coordinate_from_two_point_distance":
            x1 = givens.get("x1")
            y1 = givens.get("y1")
            x2 = givens.get("x2")
            y2 = givens.get("y2")
            dist = givens.get("distance")
            question_text = f"設 $A({x1}, {y1})$、$B({x2}, {y2})$ 為坐標平面上兩點，且其距離為 ${dist}$，試求 $k$ 值。"
        else:
            question_text = "閱讀下列資料，根據表格回答問題。"

    if problem_type_id == "frequency_distribution_chart_construction":
        pass
    elif problem_type_id == "histogram_distribution_update":
        question_text = "下圖為某幼兒園班上25位小朋友身高分布之直方圖。今班上轉出一位身高117公分的小朋友，轉入一位身高112公分的小朋友，則此時班上小朋友身高分布之直方圖為何？（請說明哪兩組次數改變以及各改變多少）"
    else:
        target_label = validation_facts.get("target_label")
        if target_label and op not in {
            "solve_basic_absolute_value_equation",
            "solve_basic_absolute_value_equation_no_solution",
            "number_line_distance_between_two_points"
        }:
            question_text = f"閱讀下列次數分配表，求 {target_label} 的次數。"

    if problem_type_id == "frequency_distribution_chart_construction":
        x_categories = [row[0] for row in matrix.get("visual_spec", {}).get("rows", [])]
        expected_values = [row[1] for row in matrix.get("visual_spec", {}).get("rows", [])]
        spec = {
            "drawing_type": "histogram_and_frequency_polygon",
            "x_categories": x_categories,
            "expected_values": expected_values,
            "required_elements": [
                "x_axis",
                "y_axis",
                "histogram_bars",
                "frequency_polygon"
            ],
            "grading_rules": {
                "bar_count_matches_categories": True,
                "histogram_bars_touch": True,
                "polygon_connects_category_midpoints_in_order": True
            },
            "bar_rules": {
                "count": len(x_categories),
                "expected_heights": expected_values,
                "touching": True,
                "baseline": 0
            },
            "polygon_rules": {
                "expected_points": [
                    [cat, val] for cat, val in zip(x_categories, expected_values)
                ],
                "connect_in_order": True
            },
            "tolerance": {
                "value": 0.8,
                "position_ratio": 0.12
            }
        }
        return {
            "question_text": question_text,
            "answer": "直方圖與折線圖已繪製於畫布。",
            "correct_answer": "直方圖與折線圖已繪製於畫布。",
            "display_answer": "直方圖與折線圖已繪製於畫布。",
            "choices": [],
            "options": [],
            "component_id": component_id,
            "textbook_example_id": textbook_example_id,
            "problem_type_id": problem_type_id,
            "source_kind": source_kind,
            "presentation_mode": mode,
            "answer_type": "drawing",
            "answer_shape": "drawing",
            "interaction_type": "handwriting_drawing",
            "auto_checkable": False,
            "grading_mode": "manual_or_ai_visual_review",
            "expected_drawing_spec": spec,
            "answer_contract": {
                "presentation_mode": mode,
                "answer_type": "drawing",
                "answer_shape": "drawing",
                "checker": "free_response_drawing_checker",
                "checker_key": "free_response_drawing_checker",
                "answer_equivalence": "drawing_equivalence",
                "equivalence": "drawing_equivalence",
                "semantic_answer": "直方圖與折線圖已繪製於畫布。",
                "expected_drawing_spec": spec,
            },
            "metadata": {
                "givens": givens,
                "raw_givens": givens,
                "target": "直方圖與折線圖已繪製於畫布。",
                "derivation": [str(step) for step in normalized["explanation_steps"]],
                "presentation_mode": mode,
                "answer_type": "drawing",
                "answer_shape": "drawing",
                "semantic_answer": "直方圖與折線圖已繪製於畫布。",
                "problem_type_id": problem_type_id,
                "component_id": component_id,
                "textbook_example_id": textbook_example_id,
                "interaction_type": "handwriting_drawing",
                "auto_checkable": False,
                "grading_mode": "manual_or_ai_visual_review",
                "expected_drawing_spec": spec,
            },
            "math_core": {
                "givens": givens,
                "raw_givens": givens,
                "target": "直方圖與折線圖已繪製於畫布。",
                "math_objects": ["frequency_table", "frequency"],
                "derivation": [str(step) for step in normalized["explanation_steps"]],
                "validation_facts": validation_facts,
            },
            "visual_spec": normalized["visual_spec"],
            "visual_aids": normalized.get("visual_aids", matrix.get("visual_aids", [])),
            "image_base64": normalized.get("image_base64", matrix.get("image_base64", "")),
            "validation_facts": validation_facts,
            "generator_key": generator_key or component_id,
        }

    choices: list[dict[str, str]] = []
    options: list[str] = []
    payload_answer = semantic_answer
    payload_correct = semantic_answer
    if resolved_answer_type == "solution_set":
        chk_key = "solution_set_checker"
        equiv_type = "unordered_solution_set"
    elif resolved_answer_type == "interval_set" or op in {
        "absolute_value_inequality_zero_center_basic",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic"
    } or problem_type_id in {
        "absolute_value_inequality_zero_center_basic",
        "absolute_value_inequality_linear_expression_basic",
        "absolute_value_inequality_shifted_basic"
    }:
        chk_key = "interval_checker"
        equiv_type = "interval_set"
    elif problem_type_id == "histogram_distribution_update":
        chk_key = "text_short_checker"
        equiv_type = "string_equivalence"
    else:
        chk_key = "integer_checker"
        equiv_type = "numeric_exact"

    answer_contract = {
        "presentation_mode": mode,
        "answer_type": resolved_answer_type,
        "checker": chk_key,
        "checker_key": chk_key,
        "answer_equivalence": equiv_type,
        "equivalence": equiv_type,
        "equivalence_type": equiv_type,
        "semantic_answer": semantic_answer,
        "ui_contract": {
            "response_mode": "text",
            "text_input_enabled": True,
            "normal_submit_enabled": True,
            "ai_check_required": False,
            "canvas_required": False,
            "allow_image_upload": False,
            "allow_text_answer": True,
        } if problem_type_id == "histogram_distribution_update" else None,
    }
    if mode == "single_choice":
        choices, correct_label = _build_choice_options(
            display_answer,
            normalized.get("distractors", []),
            seed_text=f"{problem_type_id or op}|{display_answer}",
        )
        options = [str(choice["text"]) for choice in choices]
        payload_answer = correct_label
        payload_correct = correct_label
        answer_contract = {
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": semantic_answer,
        }

    return _finalize_question_payload({
        "question_text": question_text,
        "answer": payload_answer,
        "correct_answer": payload_correct,
        "display_answer": display_answer,
        "choices": choices,
        "options": options,
        "component_id": component_id,
        "textbook_example_id": textbook_example_id,
        "problem_type_id": problem_type_id or op,
        "source_kind": source_kind,
        "presentation_mode": mode,
        "answer_type": resolved_answer_type,
        "checker": answer_contract["checker"],
        "checker_key": answer_contract["checker_key"],
        "equivalence": answer_contract["equivalence"],
        "equivalence_type": answer_contract["answer_equivalence"],
        "interaction_type": "expression",
        "auto_checkable": True,
        "grading_mode": "auto",
        "answer_contract": answer_contract,
        "metadata": {
            "givens": givens,
            "raw_givens": givens,
            "target": display_answer,
            "derivation": [str(step) for step in normalized["explanation_steps"]],
            "presentation_mode": mode,
            "answer_type": resolved_answer_type,
            "semantic_answer": semantic_answer,
            "problem_type_id": problem_type_id or op,
            "component_id": component_id,
            "textbook_example_id": textbook_example_id,
            "interaction_type": "expression",
            "auto_checkable": True,
            "grading_mode": "auto",
        },
        "math_core": {
            "givens": givens,
            "raw_givens": givens,
            "target": display_answer,
            "math_objects": ["frequency_table", "frequency"],
            "derivation": [str(step) for step in normalized["explanation_steps"]],
            "validation_facts": validation_facts,
        },
        "visual_spec": (
            None
            if (
                isinstance(normalized.get("visual_spec"), dict)
                and not normalized["visual_spec"].get("points")
                and not normalized["visual_spec"].get("lines")
            )
            else normalized["visual_spec"]
        ),
        "visual_aids": normalized.get("visual_aids", matrix.get("visual_aids", [])),
        "image_base64": normalized.get("image_base64", matrix.get("image_base64", "")),
        "validation_facts": validation_facts,
        "generator_key": generator_key or component_id,
    })


def normalize_domain_payload_to_v3_matrix(payload: Any, context: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw entrypoint payload into a formal V3 Domain Matrix.

    If the payload is already a valid V3 Matrix, it is returned as-is (preserved).
    Otherwise, a legacy Slot/V2 payload is dynamically mapped to the V3 matrix schema.
    If core semantic fields (like canonical answer) are missing, it raises ValueError.
    """
    if not isinstance(payload, dict):
        raise ValueError("domain_matrix_invalid: payload must be a dict.")

    # 1. Check if it's already a complete V3 matrix
    MATRIX_REQUIRED_FIELDS = ("givens", "answer", "distractors", "explanation_steps", "validation_facts", "visual_spec")
    if all(field in payload for field in MATRIX_REQUIRED_FIELDS):
        return payload

    # 2. Check for missing core question/answer content (should block)
    ans_val = payload.get("correct_answer")
    if ans_val is None:
        ans_val = payload.get("answer")
    if isinstance(ans_val, dict):
        ans_val = ans_val.get("value") or ans_val.get("canonical_form")

    if ans_val is None or str(ans_val).strip() == "":
        raise ValueError("domain_matrix_missing_answer: canonical answer is missing")

    question = payload.get("question_text") or payload.get("question")
    if not question:
        raise ValueError("domain_matrix_missing_question: question content is missing")

    pres_mode = str(context.get("presentation_mode") or payload.get("presentation_mode") or "short_answer").strip()

    # 3. Resolve Answer Schema Key
    from core.gencode.answer_schema_registry import resolve_answer_schema_key, ANSWER_SCHEMAS

    at = str(context.get("answer_type") or payload.get("answer_type") or "").strip()
    ck = str(payload.get("checker_key") or payload.get("checker_type") or payload.get("checker") or "").strip()
    eq = str(payload.get("equivalence") or payload.get("equivalence_type") or payload.get("answer_equivalence") or "").strip()

    if pres_mode == "single_choice" or at == "single_choice":
        schema_key = "choice_label"
    else:
        schema_key = resolve_answer_schema_key(
            answer_schema_key=context.get("answer_schema_key") or payload.get("answer_schema_key"),
            domain_operation=context.get("problem_type_id") or payload.get("problem_type_id"),
            problem_type_id=context.get("problem_type_id") or payload.get("problem_type_id"),
        )

    if not schema_key:
        if at in {"ordered_pair"} or ck in {"coordinate_pair_checker"} or eq in {"coordinate_pair_equivalence"}:
            schema_key = "coordinate_pair"
        elif at in {"rational", "integer", "numeric"} or ck in {"integer_checker", "rational_checker"} or eq in {"numeric_exact", "rational_equivalent"}:
            schema_key = "numeric_scalar"
        elif at in {"linear_equation", "expression"} or ck in {"linear_equation_equivalent_checker"} or eq in {"linear_equation_equivalent", "expression"}:
            if ck in {"linear_equation_equivalent_checker"} or "line_equation" in str(context.get("problem_type_id") or payload.get("problem_type_id")):
                schema_key = "line_equation"
            else:
                schema_key = "numeric_scalar"
        elif at in {"single_choice"} or ck in {"choice_label_checker"} or eq in {"choice_label"}:
            schema_key = "choice_label"
        elif at in {"solution_set"} or ck in {"solution_set_checker"} or eq in {"unordered_solution_set"}:
            schema_key = "parameter_solution_set"
        elif at in {"distance_scalar"} or ck in {"distance_scalar_checker"}:
            schema_key = "distance_scalar"

    if not schema_key:
        raise ValueError("domain_payload_answer_schema_unresolved: Cannot resolve answer schema key")

    schema = ANSWER_SCHEMAS.get(schema_key)
    if not schema:
        raise ValueError(f"domain_payload_answer_schema_unresolved: Unknown schema key {schema_key}")
    required_fields = schema["required_fields"]

    # 4. Extract distractors
    distractors = []
    choices = payload.get("choices")

    ans_text_val = str(ans_val)
    if isinstance(choices, list) and choices:
        for choice in choices:
            if isinstance(choice, dict):
                label = str(choice.get("label") or "").strip()
                if label and label.upper() == ans_text_val.upper():
                    ans_text_val = str(choice.get("text") or choice.get("value") or "")
                    break

    if isinstance(choices, list) and choices:
        for choice in choices:
            if isinstance(choice, dict):
                txt = str(choice.get("text") or choice.get("value") or "")
                if txt and txt != ans_text_val and txt != str(ans_val):
                    distractors.append(txt)
            elif isinstance(choice, str):
                if choice and choice != ans_text_val and choice != str(ans_val):
                    distractors.append(choice)

    if pres_mode == "single_choice" and not distractors:
        raw_distractors = payload.get("distractors")
        if isinstance(raw_distractors, list) and raw_distractors:
            distractors = [str(x) for x in raw_distractors]
        else:
            raise ValueError("domain_matrix_missing_distractors: single_choice requires distractors")

    # 5. Extract givens
    givens = {}
    if isinstance(payload.get("metadata"), dict):
        givens.update(payload["metadata"])
    for key in ["x1", "y1", "x2", "y2", "x3", "y3", "ratio_m", "ratio_n", "point_names", "coordinates", "known_values"]:
        if key in payload:
            givens[key] = payload[key]
    if "question_text" not in givens:
        givens["question_text"] = str(question)

    # 6. Extract explanation_steps
    explanation_steps = []
    exp = payload.get("explanation") or payload.get("explanation_steps") or payload.get("derivation")
    if isinstance(exp, list):
        explanation_steps = [str(s) for s in exp if s]
    elif isinstance(exp, str) and exp.strip():
        explanation_steps = [s.strip() for s in exp.split("\n") if s.strip()]

    # 7. Extract validation_facts
    validation_facts = {}
    if isinstance(payload.get("validation_facts"), dict):
        validation_facts.update(payload["validation_facts"])

    op_name = str(context.get("problem_type_id") or payload.get("problem_type_id") or "").strip()
    if op_name:
        validation_facts.setdefault("domain_operation", op_name)
        validation_facts.setdefault("task_type", op_name)
        validation_facts.setdefault("line_type", op_name)
    validation_facts.setdefault("curriculum_profile", context.get("curriculum_profile") or "vocational_high_b")
    validation_facts.setdefault("difficulty_profile", context.get("difficulty_profile") or "easy")
    validation_facts.setdefault("canonical_answer", str(ans_val))

    # 8. Resolve visual_spec
    domain_key = str(context.get("fixed_domain_key") or payload.get("fixed_domain_key") or "").strip()
    if not domain_key:
        from core.registry.taxonomy_registry import resolve_domain_for_skill
        try:
            domain_key = resolve_domain_for_skill(context.get("skill_id") or payload.get("skill_id")) or ""
        except Exception:
            domain_key = ""

    if domain_key.startswith("coordinate_geometry"):
        visual_spec = {
            "kind": "coordinate_plane_spec",
            "points": [],
            "lines": [],
            "x_range": [-10, 10],
            "y_range": [-10, 10]
        }
    else:
        visual_spec = {
            "kind": "no_visual"
        }

    # 9. Construct the strict schema-adhering answer dict
    answer_dict = {}
    for field in required_fields:
        if field == "solutions":
            if isinstance(ans_val, list):
                answer_dict[field] = ans_val
            else:
                answer_dict[field] = [x.strip() for x in str(ans_val).split(",") if x.strip()]
        elif field == "coefficients":
            answer_dict[field] = payload.get("coefficients") or {}
        elif field == "correct_label":
            answer_dict[field] = str(ans_val)
        else:
            answer_dict[field] = str(ans_val)

    v3_matrix = {
        "givens": givens,
        "answer": answer_dict,
        "distractors": distractors,
        "explanation_steps": explanation_steps,
        "validation_facts": validation_facts,
        "visual_spec": visual_spec,
    }

    for k, v in payload.items():
        if k not in v3_matrix and k not in {"metadata", "answer_contract"}:
            v3_matrix[k] = v

    return v3_matrix


def _convert_graph_intercepts_and_linear_equation_payload(
    matrix: dict[str, Any],
    *,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    canonical = dict(matrix["semantic_answer"])
    parts = [
        {
            "key": key,
            "label": label,
            "checker": checker,
            "expected_answer": canonical.get(key),
        }
        for key, label, checker in (
            ("x_intercept", "x 截距", "rational_checker"),
            ("y_intercept", "y 截距", "rational_checker"),
            ("function_equation", "f(x)", "linear_equation_equivalent_checker"),
        )
    ]
    return {
        "question_text": matrix["question"],
        "answer": canonical,
        "correct_answer": canonical,
        "display_answer": canonical,
        "semantic_answer": canonical,
        "semantic_answer_type": "multi_part",
        "answer_type": "multi_part",
        "presentation_mode": "graph_multi_part",
        "interaction_type": "multi_part",
        "problem_type_id": "graph_intercepts_and_linear_equation",
        "domain_operation": "graph_intercepts_and_linear_equation",
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "component_id": component_id or "",
        "textbook_example_id": textbook_example_id or 0,
        "topology_tags": list(matrix["topology_tags"]),
        "visual_spec": dict(matrix["visual_spec"]),
        "answer_contract": {
            "presentation_mode": "graph_multi_part",
            "answer_type": "multi_part",
            "answer_shape": "multi_part",
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "answer_equivalence": "multi_part_answer",
            "equivalence": "multi_part_answer",
            "semantic_answer": canonical,
            "parts": parts,
            "ui_contract": {
                "response_mode": "multi_part",
                "text_input_enabled": True,
            },
        },
        "metadata": {
            "givens": dict(matrix["givens"]),
            "semantic_answer": canonical,
            "presentation_mode": "graph_multi_part",
            "answer_type": "multi_part",
            "source_example_id": textbook_example_id or 0,
        },
        "math_core": {
            "givens": dict(matrix["givens"]),
            "target": canonical,
            "derivation": list(matrix["explanation_steps"]),
            "validation_facts": dict(matrix["validation_facts"]),
        },
        "choices": [],
        "options": [],
        "auto_checkable": True,
        "grading_mode": "auto",
    }


def _convert_line_graph_drawing_payload(
    matrix: dict[str, Any],
    *,
    domain_operation: str,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    expected_spec = dict(matrix["expected_drawing_spec"])
    semantic_answer = dict(matrix["semantic_answer"])
    ui_contract = {
        "response_mode": "drawing",
        "drawing_required": True,
        "ai_check_required": True,
        "text_answer_enabled": False,
        "text_input_enabled": False,
        "submit_button_enabled": False,
        "normal_submit_enabled": False,
        "success_dialog_required": True,
        "canvas_required": True,
        "allow_image_upload": False,
        "allow_text_answer": False,
    }
    return {
        "question_text": matrix["question"],
        "question": matrix["question"],
        "answer": semantic_answer,
        "correct_answer": semantic_answer,
        "display_answer": expected_spec["equation"],
        "semantic_answer": semantic_answer,
        "answer_type": "drawing",
        "answer_shape": "drawing",
        "presentation_mode": "canvas",
        "interaction_type": "handwriting_drawing",
        "problem_type_id": domain_operation,
        "domain_operation": domain_operation,
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "component_id": component_id or "",
        "textbook_example_id": textbook_example_id or 0,
        "topology_tags": list(matrix["topology_tags"]),
        "visual_spec": dict(matrix["visual_spec"]),
        "expected_drawing_spec": expected_spec,
        "answer_contract": {
            "presentation_mode": "canvas",
            "answer_type": "drawing",
            "answer_shape": "drawing",
            "checker": "free_response_drawing_checker",
            "checker_key": "free_response_drawing_checker",
            "answer_equivalence": "drawing_equivalence",
            "equivalence": "drawing_equivalence",
            "equivalence_type": "drawing_equivalence",
            "semantic_answer": semantic_answer,
            "expected_drawing_spec": expected_spec,
            "ui_contract": ui_contract,
        },
        "metadata": {
            "givens": dict(matrix["givens"]),
            "semantic_answer": semantic_answer,
            "presentation_mode": "canvas",
            "answer_type": "drawing",
            "answer_shape": "drawing",
            "source_example_id": textbook_example_id or 0,
            "answer_dependencies": [],
            "expected_drawing_spec": expected_spec,
            "ui_contract": ui_contract,
        },
        "math_core": {
            "givens": dict(matrix["givens"]),
            "target": semantic_answer,
            "derivation": list(matrix["explanation_steps"]),
            "validation_facts": dict(matrix["validation_facts"]),
        },
        "choices": [],
        "options": [],
        "auto_checkable": False,
        "grading_mode": "manual_or_ai_visual_review",
    }


def _convert_graph_based_tiered_linear_application_multi_part_payload(
    matrix: dict[str, Any],
    *,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    canonical = dict(matrix["semantic_answer"])
    parts = [
        {
            "key": key,
            "label": label,
            "checker": "rational_checker",
            "equivalence_type": "numeric_exact",
            "expected_answer": canonical.get(key),
        }
        for key, label in (
            ("part_1", "第（1）小題"),
            ("part_2", "第（2）小題"),
        )
    ]
    question_text = str(matrix.get("question") or matrix.get("question_text") or "")
    return {
        "question_text": question_text,
        "question": question_text,
        "answer": canonical,
        "correct_answer": canonical,
        "display_answer": canonical,
        "semantic_answer": canonical,
        "semantic_answer_type": "multi_part",
        "answer_type": "multi_part",
        "presentation_mode": "graph_multi_part",
        "interaction_type": "multi_part",
        "problem_type_id": "graph_based_tiered_linear_application_multi_part",
        "domain_operation": "graph_based_tiered_linear_application_multi_part",
        "fixed_domain_key": "coordinate_geometry.division_point_coordinates",
        "component_id": component_id or "",
        "textbook_example_id": textbook_example_id or 0,
        "topology_tags": list(matrix.get("topology_tags") or []),
        "visual_spec": dict(matrix.get("visual_spec") or {}),
        "answer_contract": {
            "presentation_mode": "graph_multi_part",
            "answer_type": "multi_part",
            "answer_shape": "multi_part",
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "answer_equivalence": "multi_part_answer",
            "equivalence": "multi_part_answer",
            "equivalence_type": "multi_part_answer",
            "semantic_answer": canonical,
            "parts": parts,
            "ui_contract": {
                "response_mode": "multi_part",
                "text_input_enabled": True,
            },
        },
        "metadata": {
            "givens": dict(matrix.get("givens") or {}),
            "semantic_answer": canonical,
            "presentation_mode": "graph_multi_part",
            "answer_type": "multi_part",
            "source_example_id": textbook_example_id or 0,
            "answer_dependencies": [],
        },
        "math_core": {
            "givens": dict(matrix.get("givens") or {}),
            "target": canonical,
            "derivation": list(matrix.get("explanation_steps") or []),
            "validation_facts": dict(matrix.get("validation_facts") or {}),
        },
        "choices": [],
        "options": [],
        "auto_checkable": True,
        "grading_mode": "auto",
    }


def _convert_graph_based_linear_application_inverse_payload(
    matrix: dict[str, Any],
    *,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
) -> dict[str, Any]:
    answer = matrix["answer"]["canonical_form"]
    givens = dict(matrix["givens"])
    facts = dict(matrix["validation_facts"])
    question_text = str(matrix.get("question") or matrix.get("question_text") or "")
    contract = {
        "presentation_mode": "graph_short_answer",
        "answer_type": "numeric",
        "checker": "numeric_checker",
        "checker_key": "numeric_checker",
        "answer_equivalence": "numeric_equivalence",
        "equivalence": "numeric_equivalence",
        "equivalence_type": "numeric_equivalence",
        "semantic_answer": answer,
    }
    return {
        "question_text": question_text,
        "question": question_text,
        "answer": answer,
        "correct_answer": answer,
        "display_answer": str(answer),
        "semantic_answer": answer,
        "choices": [],
        "options": [],
        "component_id": component_id or "",
        "textbook_example_id": textbook_example_id or 0,
        "problem_type_id": "graph_based_linear_application_inverse",
        "domain_operation": "graph_based_linear_application_inverse",
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "source_kind": source_kind or "",
        "presentation_mode": "graph_short_answer",
        "answer_type": "numeric",
        "checker": "numeric_checker",
        "checker_key": "numeric_checker",
        "equivalence": "numeric_equivalence",
        "equivalence_type": "numeric_equivalence",
        "interaction_type": "short_answer",
        "auto_checkable": True,
        "grading_mode": "auto",
        "answer_contract": contract,
        "metadata": {
            "givens": givens,
            "semantic_answer": answer,
            "validation_facts": facts,
            "answer_dependencies": [],
        },
        "math_core": {
            "givens": givens,
            "target": answer,
            "derivation": list(matrix["explanation_steps"]),
            "validation_facts": facts,
        },
        "visual_spec": dict(matrix["visual_spec"]),
        "validation_facts": facts,
        "generator_key": generator_key or component_id or "",
    }


def _convert_linear_equation_from_two_points_choice_payload(
    matrix: dict[str, Any],
    *,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
) -> dict[str, Any]:
    choices = [dict(choice) for choice in matrix["choices"]]
    correct_label = str(matrix["answer"]["correct_label"])
    semantic_answer = str(matrix["semantic_answer"])
    givens = dict(matrix["givens"])
    facts = dict(matrix["validation_facts"])
    question_text = str(matrix.get("question") or matrix.get("question_text") or "")
    contract = {
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "answer_equivalence": "choice_label",
        "equivalence": "choice_label",
        "equivalence_type": "choice_label",
        "semantic_answer": semantic_answer,
        "choice_value_to_label": dict(facts["choice_value_to_label"]),
    }
    return {
        "question_text": question_text,
        "question": question_text,
        "answer": correct_label,
        "correct_answer": correct_label,
        "display_answer": semantic_answer,
        "semantic_answer": semantic_answer,
        "choices": choices,
        "options": [choice["text"] for choice in choices],
        "component_id": component_id or "",
        "textbook_example_id": textbook_example_id or 0,
        "problem_type_id": "linear_equation_from_two_points_choice",
        "domain_operation": "linear_equation_from_two_points_choice",
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "source_kind": source_kind or "",
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "equivalence": "choice_label",
        "equivalence_type": "choice_label",
        "interaction_type": "single_choice",
        "auto_checkable": True,
        "grading_mode": "auto",
        "answer_contract": contract,
        "metadata": {
            "givens": givens,
            "semantic_answer": semantic_answer,
            "validation_facts": facts,
            "choice_value_to_label": dict(facts["choice_value_to_label"]),
            "answer_dependencies": [],
        },
        "math_core": {
            "givens": givens,
            "target": semantic_answer,
            "derivation": list(matrix["explanation_steps"]),
            "validation_facts": facts,
        },
        "visual_spec": dict(matrix["visual_spec"]),
        "validation_facts": facts,
        "generator_key": generator_key or component_id or "",
    }


def _convert_linear_graph_feasibility_choice_payload(
    matrix: dict[str, Any],
    *,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
) -> dict[str, Any]:
    choices = [dict(choice) for choice in matrix["choices"]]
    correct_label = str(matrix["answer"]["correct_label"])
    semantic_answer = str(matrix["semantic_answer"])
    givens = dict(matrix["givens"])
    facts = dict(matrix["validation_facts"])
    question_text = str(matrix.get("question") or matrix.get("question_text") or "")
    contract = {
        "presentation_mode": "graph_single_choice",
        "answer_type": "single_choice",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "answer_equivalence": "choice_label",
        "equivalence": "choice_label",
        "equivalence_type": "choice_label",
        "semantic_answer": semantic_answer,
        "choice_value_to_label": dict(facts["choice_value_to_label"]),
    }
    return {
        "question_text": question_text,
        "question": question_text,
        "answer": correct_label,
        "correct_answer": correct_label,
        "display_answer": semantic_answer,
        "semantic_answer": semantic_answer,
        "choices": choices,
        "options": [choice["text"] for choice in choices],
        "component_id": component_id or "",
        "textbook_example_id": textbook_example_id or 0,
        "problem_type_id": "linear_graph_feasibility_choice",
        "domain_operation": "linear_graph_feasibility_choice",
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "source_kind": source_kind or "",
        "presentation_mode": "graph_single_choice",
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "equivalence": "choice_label",
        "equivalence_type": "choice_label",
        "interaction_type": "single_choice",
        "auto_checkable": True,
        "grading_mode": "auto",
        "answer_contract": contract,
        "metadata": {
            "givens": givens,
            "semantic_answer": semantic_answer,
            "validation_facts": facts,
            "choice_value_to_label": dict(facts["choice_value_to_label"]),
            "answer_dependencies": [],
        },
        "math_core": {
            "givens": givens,
            "target": semantic_answer,
            "derivation": list(matrix["explanation_steps"]),
            "validation_facts": facts,
        },
        "visual_spec": dict(matrix["visual_spec"]),
        "validation_facts": facts,
        "generator_key": generator_key or component_id or "",
    }


def _convert_robust_budget_feasibility_choice_payload(
    matrix: dict[str, Any],
    *,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
) -> dict[str, Any]:
    choices = [dict(choice) for choice in matrix["choices"]]
    correct_label = str(matrix["answer"]["correct_label"])
    semantic_answer = str(matrix["semantic_answer"])
    givens = dict(matrix["givens"])
    facts = dict(matrix["validation_facts"])
    question_text = str(matrix.get("question") or matrix.get("question_text") or "")
    value_to_label = dict(facts["choice_value_to_label"])
    contract = {
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "answer_equivalence": "choice_label",
        "equivalence": "choice_label",
        "equivalence_type": "choice_label",
        "semantic_answer": semantic_answer,
        "choice_value_to_label": value_to_label,
    }
    return {
        "question_text": question_text,
        "question": question_text,
        "answer": correct_label,
        "correct_answer": correct_label,
        "display_answer": semantic_answer,
        "semantic_answer": semantic_answer,
        "choices": choices,
        "options": [choice["text"] for choice in choices],
        "component_id": component_id or "",
        "textbook_example_id": textbook_example_id or 0,
        "problem_type_id": "robust_budget_feasibility_choice",
        "domain_operation": "robust_budget_feasibility_choice",
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "source_kind": source_kind or "",
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "equivalence": "choice_label",
        "equivalence_type": "choice_label",
        "interaction_type": "single_choice",
        "auto_checkable": True,
        "grading_mode": "auto",
        "answer_contract": contract,
        "metadata": {
            "givens": givens,
            "semantic_answer": semantic_answer,
            "validation_facts": facts,
            "choice_value_to_label": value_to_label,
            "answer_dependencies": [],
        },
        "math_core": {
            "givens": givens,
            "target": semantic_answer,
            "derivation": list(matrix["explanation_steps"]),
            "validation_facts": facts,
        },
        "visual_spec": dict(matrix["visual_spec"]),
        "validation_facts": facts,
        "generator_key": generator_key or component_id or "",
    }


def _convert_graph_based_linear_model_equation_payload(
    matrix: dict[str, Any],
    *,
    component_id: str | None = None,
    textbook_example_id: int | None = None,
    source_kind: str | None = None,
    generator_key: str | None = None,
) -> dict[str, Any]:
    choices = [dict(choice) for choice in matrix["choices"]]
    correct_label = str(matrix["answer"]["correct_label"])
    semantic_answer = str(matrix["semantic_answer"])
    givens = dict(matrix["givens"])
    facts = dict(matrix["validation_facts"])
    question_text = str(matrix.get("question") or matrix.get("question_text") or "")
    contract = {
        "presentation_mode": "graph_single_choice",
        "answer_type": "single_choice",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "answer_equivalence": "choice_label",
        "equivalence": "choice_label",
        "equivalence_type": "choice_label",
        "semantic_answer": semantic_answer,
        "choice_value_to_label": dict(facts["choice_value_to_label"]),
    }
    return {
        "question_text": question_text,
        "question": question_text,
        "answer": correct_label,
        "correct_answer": correct_label,
        "display_answer": semantic_answer,
        "semantic_answer": semantic_answer,
        "choices": choices,
        "options": [choice["text"] for choice in choices],
        "component_id": component_id or "",
        "textbook_example_id": textbook_example_id or 0,
        "problem_type_id": "graph_based_linear_model_equation",
        "domain_operation": "graph_based_linear_model_equation",
        "fixed_domain_key": "coordinate_geometry.line_equation",
        "source_kind": source_kind or "",
        "presentation_mode": "graph_single_choice",
        "answer_type": "single_choice",
        "answer_shape": "single_choice",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "equivalence": "choice_label",
        "equivalence_type": "choice_label",
        "interaction_type": "single_choice",
        "auto_checkable": True,
        "grading_mode": "auto",
        "answer_contract": contract,
        "metadata": {
            "givens": givens,
            "semantic_answer": semantic_answer,
            "validation_facts": facts,
            "choice_value_to_label": dict(facts["choice_value_to_label"]),
            "answer_dependencies": [],
        },
        "math_core": {
            "givens": givens,
            "target": semantic_answer,
            "derivation": list(matrix["explanation_steps"]),
            "validation_facts": facts,
        },
        "visual_spec": dict(matrix["visual_spec"]),
        "validation_facts": facts,
        "generator_key": generator_key or component_id or "",
    }
