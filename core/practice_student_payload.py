"""Student-facing view of a served practice question.

The full question (canonical answer, semantic answer, worked solution, checker data) stays in the server-side question store,
where /check_answer, the AI tutor and handwriting analysis read it by question_uid.  The browser only receives what it needs to
show the question and collect an answer: top-level, metadata, answer_contract and answer part fields are allow-listed,
answer-like keys are removed at any depth, and the source rows of a fill-in table lose the values of the cells the student has to fill.
"""
from __future__ import annotations

from typing import Any

PUBLIC_TOP_LEVEL = frozenset({
    "skill_id", "question_uid", "question_text_hash", "question_id", "question_text", "new_question_text", "message",
    "context_string", "inequality_string", "consecutive_correct", "current_level", "mode",
    "choices", "choices_display", "subquestions", "table", "table_title", "table_data", "table_question",
    "image_base64", "image_assets", "visual_spec", "diagram_spec", "visual_aids", "visual_backed", "visual_asset_type",
    "answer_type", "answer_input_type", "answer_contract", "answer_shape", "presentation_mode", "interaction_type",
    "response_mode", "ui_contract", "drawing_check", "question_type", "checker", "checker_type", "equivalence",
    "check_mode", "grading_mode", "graded", "problem_type_id", "component_id", "generator_key", "textbook_example_id",
    "source", "source_kind", "question_source", "reuse_textbook_image", "metadata",
    "route_source", "route_mode", "route_reason", "wrapper_path", "module_file", "wrapper_loaded",
    "legacy_fallback_used", "legacy_fallback_reason", "generator_mode", "runtime_mode",
    "scenario_id", "scenario_family", "parameter_signature", "variant", "n",
    "requires_handwriting", "requires_listing_or_tree", "requires_teacher_review", "practice_type_rotation",
    "fixed_textbook_practice", "practice_scaffold", "manual_review_unavailable", "reason", "future_path",
})

PUBLIC_METADATA = frozenset({
    "stem_structure", "visual_spec", "diagram_spec", "ui_contract", "presentation_mode", "answer_type", "problem_type_id",
    "component_id", "textbook_example_id", "skill_id", "source_kind", "source_description",
})

PUBLIC_CONTRACT = frozenset({
    "answer_type", "answer_shape", "presentation_mode", "response_mode", "ui_contract", "checker", "checker_key",
    "answer_equivalence", "equivalence", "equivalence_type", "parts", "choices", "blank_cells", "drawing_check",
    "drawing_parts", "required_form", "allow_decimal", "decimal_places", "significant_digits",
})

PUBLIC_PART = frozenset({
    "key", "field_key", "label", "display_label", "group_label", "math_label", "aria_label", "prompt", "unit",
    "input_type", "choices", "canvas", "answer_order", "answer_type", "answer_shape", "checker", "checker_key",
    "equivalence_type", "answer_equivalence", "required_form", "allow_decimal", "significant_digits", "precision",
    "drawing_required", "text_answer_enabled", "ai_check_required",
})

PUBLIC_DRAWING_CHECK = frozenset({"enabled", "mode"})

_PRIVATE_EXACT = frozenset({
    "answer", "answers", "correct_answer", "correct_answers", "display_answer", "canonical_answer", "semantic_answer",
    "accepted_answers", "answer_value", "answer_key", "solution", "solutions", "detailed_solution", "reference_solution",
    "worked_solution", "solution_steps", "work", "explanation",
})
_PRIVATE_PREFIXES = ("expected_", "correct_", "canonical_", "semantic_")
_TABLE_KEYS = ("table_data", "table_question")
# practice progress state (counts such as passed / correct per type), not question content
_PROGRESS_KEYS = ("practice_type_rotation",)


def is_private_key(key: Any) -> bool:
    name = str(key).strip().lower()
    return name in _PRIVATE_EXACT or name.startswith(_PRIVATE_PREFIXES)


def _scrub(node: Any) -> Any:
    if isinstance(node, dict):
        return {k: _scrub(v) for k, v in node.items() if not is_private_key(k)}
    if isinstance(node, list):
        return [_scrub(v) for v in node]
    return node


def _blank_table_rows(table: dict[str, Any]) -> None:
    """Blank the cells the student must fill in the source ``rows`` (``display_rows`` / ``visible_table`` already are)."""
    rows, cells = table.get("rows"), table.get("blank_cells")
    if not isinstance(rows, list) or not isinstance(cells, list):
        return
    visible = table.get("visible_table") or table.get("display_rows")
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        r, c = cell.get("row"), cell.get("col")
        if not isinstance(r, int) or not isinstance(c, int) or not (0 <= r < len(rows)) or not isinstance(rows[r], list) or not (0 <= c < len(rows[r])):
            continue
        shown = ""
        if isinstance(visible, list) and r < len(visible) and isinstance(visible[r], list) and c < len(visible[r]):
            shown = visible[r][c]
        rows[r][c] = shown


def _without_choice_flags(choices: Any) -> Any:
    if not isinstance(choices, list):
        return choices
    return [{k: v for k, v in c.items() if k not in ("correct", "is_correct")} if isinstance(c, dict) else c for c in choices]


def _public_drawing_check(check: Any) -> Any:
    return {k: v for k, v in check.items() if k in PUBLIC_DRAWING_CHECK} if isinstance(check, dict) else check


def _public_contract(contract: Any) -> Any:
    if not isinstance(contract, dict):
        return contract
    out = {k: v for k, v in contract.items() if k in PUBLIC_CONTRACT}
    if isinstance(out.get("parts"), list):
        out["parts"] = [
            {k: (_without_choice_flags(v) if k == "choices" else v) for k, v in part.items() if k in PUBLIC_PART}
            if isinstance(part, dict) else part
            for part in out["parts"]
        ]
    if "choices" in out:
        out["choices"] = _without_choice_flags(out["choices"])
    if "drawing_check" in out:
        out["drawing_check"] = _public_drawing_check(out["drawing_check"])
    return out


def student_question_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a new dict safe to send before the student submits; ``payload`` and its nested objects are not modified."""
    source = payload or {}
    out = _scrub({k: v for k, v in source.items() if k in PUBLIC_TOP_LEVEL and k not in _PROGRESS_KEYS})
    out.update({k: source[k] for k in _PROGRESS_KEYS if k in source})
    meta = out.get("metadata")
    if isinstance(meta, dict):
        out["metadata"] = {k: v for k, v in meta.items() if k in PUBLIC_METADATA}
    for key in ("choices", "choices_display"):
        if key in out:
            out[key] = _without_choice_flags(out[key])
    if "answer_contract" in out:
        out["answer_contract"] = _public_contract(out["answer_contract"])
    if "drawing_check" in out:
        out["drawing_check"] = _public_drawing_check(out["drawing_check"])
    for key in _TABLE_KEYS:
        if isinstance(out.get(key), dict):
            _blank_table_rows(out[key])
    return out
