"""Build per-example source topology for V3 induced specs and isomorphism checks."""

from __future__ import annotations

import json
import re
from typing import Any

from core.gencode.v3_presentation_inference import has_abcd_choice_group, parse_abcd_choices_from_text

_STAT_CHART_SOURCE_TOPOLOGY: dict[int, dict[str, Any]] = {
    3884: {
        "source_example_id": 3884,
        "chart_type": "cumulative_frequency_polygon_above",
        "cumulative_direction": "above",
        "row_column_structure": "score_marks_with_above_cumulative_counts",
        "story_context": "某班英文段考成績",
        "variable_unit": "分",
        "displayed_data_dependencies": [
            "cumulative_polygon_plot",
            "score_class_marks",
            "above_cumulative_counts",
            "total_student_count",
        ],
        "exact_task_operation": "cumulative_above_fail_count",
        "answer_derivation": "total_students - above_cumulative_at_threshold",
        "choice_construction_rule": "integer_distractors_near_fail_count",
        "randomizable_parameters": [
            "total_students",
            "class_marks",
            "class_frequencies",
            "pass_threshold",
        ],
        "invariants": [
            "chart_type=cumulative_frequency_polygon_above",
            "task=fail_count_below_threshold",
            "story_context=exam_scores",
            "presentation_mode=single_choice",
            "choice_topology=four_integer_options",
        ],
        "source_style_ref": "B4_Ch3_self_assessment_5_exam_above_cumulative",
        "threshold": 60,
        "task_kind": "fail_count_below_threshold",
    },
    3885: {
        "source_example_id": 3885,
        "chart_type": "cumulative_frequency_polygon_above",
        "cumulative_direction": "above",
        "row_column_structure": "score_marks_with_above_cumulative_counts",
        "story_context": "某班英文段考成績",
        "variable_unit": "分",
        "displayed_data_dependencies": [
            "cumulative_polygon_plot",
            "score_class_marks",
            "above_cumulative_counts",
        ],
        "exact_task_operation": "cumulative_above_interval_count",
        "answer_derivation": "above_cumulative_at_low - above_cumulative_at_high",
        "choice_construction_rule": "integer_distractors_near_interval_count",
        "randomizable_parameters": [
            "class_marks",
            "class_frequencies",
            "interval_low",
            "interval_high",
        ],
        "invariants": [
            "chart_type=cumulative_frequency_polygon_above",
            "task=interval_count_on_score_range",
            "linked_prior_example=3884",
            "presentation_mode=single_choice",
            "choice_topology=four_integer_options",
        ],
        "source_style_ref": "B4_Ch3_self_assessment_6_exam_interval",
        "interval_low": 70,
        "interval_high": 80,
        "task_kind": "interval_count",
        "linked_source_example_id": 3884,
    },
    3886: {
        "source_example_id": 3886,
        "chart_type": "cumulative_frequency_polygon_below",
        "cumulative_direction": "below",
        "row_column_structure": "age_marks_with_below_cumulative_counts",
        "story_context": "某公司員工年齡",
        "variable_unit": "歲",
        "displayed_data_dependencies": [
            "cumulative_polygon_plot",
            "age_class_marks",
            "below_cumulative_counts",
            "total_employee_count",
        ],
        "exact_task_operation": "cumulative_below_interval_count",
        "answer_derivation": "below_cumulative_at_high - below_cumulative_at_low",
        "choice_construction_rule": "integer_distractors_near_interval_count",
        "randomizable_parameters": [
            "total_population",
            "class_marks",
            "class_frequencies",
            "interval_low",
            "interval_high",
        ],
        "invariants": [
            "chart_type=cumulative_frequency_polygon_below",
            "task=interval_count_on_age_range",
            "total_population_stated_in_stem",
            "presentation_mode=single_choice",
            "choice_topology=four_integer_options",
        ],
        "source_style_ref": "B4_Ch3_self_assessment_7_age_below_cumulative",
        "interval_low": 30,
        "interval_high": 40,
        "total_population": 40,
        "task_kind": "interval_count",
    },
}


def parse_textbook_notes(notes: str | None) -> dict[str, Any]:
    if not notes:
        return {}
    try:
        parsed = json.loads(notes)
        return parsed if isinstance(parsed, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def build_source_topology_from_textbook_row(row: dict[str, Any]) -> dict[str, Any]:
    """Return enriched topology for a textbook example row."""
    example_id = int(row.get("id") or row.get("textbook_example_id") or 0)
    problem_text = str(row.get("problem_text") or "")
    notes = parse_textbook_notes(row.get("notes"))
    choices = list(row.get("choices") or [])
    if not choices and has_abcd_choice_group(problem_text):
        choices = parse_abcd_choices_from_text(problem_text)
    if str(row.get("skill_id") or "") == "vh_數學B1_MidpointCoordinates":
        from core.gencode.midpoint_source_fidelity import get_source_spec

        source_spec = get_source_spec(example_id)
        return {
            **source_spec,
            "source_example_id": example_id,
            "exact_task_operation": source_spec["problem_type_id"],
            "source_question_text": problem_text,
            "source_choices": choices,
            "source_answer": str(row.get("correct_answer") or ""),
            "source_explanation": str(row.get("detailed_solution") or ""),
            "source_description": str(row.get("source_description") or ""),
            "source_problem_type": str(row.get("problem_type") or ""),
            "source_notes": notes,
        }
    preset = dict(_STAT_CHART_SOURCE_TOPOLOGY.get(example_id) or {})
    if not preset:
        return {
            "source_example_id": example_id,
            "source_question_text": problem_text,
            "source_choices": choices,
            "source_answer": str(row.get("correct_answer") or ""),
            "source_explanation": str(row.get("detailed_solution") or ""),
            "source_notes": notes,
        }

    topology = {
        **preset,
        "source_question_text": problem_text,
        "source_choices": choices,
        "source_answer": str(row.get("correct_answer") or ""),
        "source_explanation": str(row.get("detailed_solution") or ""),
        "source_description": str(row.get("source_description") or ""),
        "source_problem_type": str(row.get("problem_type") or ""),
        "source_notes": notes,
        "missing_docx_image_asset": bool(notes.get("missing_docx_image_asset")),
        "needs_image_review": bool(notes.get("needs_image_review")),
    }
    return topology


def build_domain_params_from_topology(topology: dict[str, Any]) -> dict[str, Any]:
    """Map source topology into domain matrix constraints."""
    if not topology:
        return {}
    params: dict[str, Any] = {}
    for key in (
        "chart_type",
        "cumulative_direction",
        "story_context",
        "variable_unit",
        "threshold",
        "interval_low",
        "interval_high",
        "total_population",
        "task_kind",
        "source_style_ref",
        "linked_source_example_id",
    ):
        if key in topology and topology[key] is not None:
            params[key] = topology[key]
    exact_operation = str(
        topology.get("exact_task_operation") or topology.get("domain_operation") or ""
    ).strip()
    params["exact_task_operation"] = exact_operation
    if exact_operation:
        params["line_type"] = exact_operation
        params["problem_type_id"] = exact_operation
        params["target_task"] = exact_operation
    return params


def enrich_induced_spec_with_source_topology(
    spec: dict[str, Any],
    *,
    textbook_row: dict[str, Any],
) -> dict[str, Any]:
    enriched = dict(spec or {})
    topology = build_source_topology_from_textbook_row(textbook_row)
    if not topology:
        return enriched
    enriched["source_topology"] = topology
    enriched["source_example_id"] = topology.get("source_example_id") or textbook_row.get("id")
    enriched["source_style_ref"] = topology.get("source_style_ref", "")
    domain_params = build_domain_params_from_topology(topology)
    if domain_params:
        enriched["domain_params"] = domain_params
        existing_constraints = enriched.get("constraints")
        if isinstance(existing_constraints, dict):
            merged = dict(existing_constraints)
            merged.update(domain_params)
            enriched["constraints"] = merged
        else:
            enriched["constraints"] = domain_params
    op = str(topology.get("exact_task_operation") or "").strip()
    if op:
        enriched["domain_operation"] = op
        enriched["problem_type_id"] = op
        enriched["line_type"] = op
        enriched["target_task"] = op
        enriched["template_slot"] = op
    return enriched
