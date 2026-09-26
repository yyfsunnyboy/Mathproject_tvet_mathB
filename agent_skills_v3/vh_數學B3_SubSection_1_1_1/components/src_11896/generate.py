from __future__ import annotations

from typing import Any

from core.domain.sequence_series_domain import build_sequence_series_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = 'short_answer'
ANSWER_TYPE = 'multi_part'
PROBLEM_TYPE_ID = 'expand_general_term_first_n'
TEXTBOOK_EXAMPLE_ID = 11896
DEFAULT_COMPONENT_ID = "src_11896"
EXTRA_CONSTRAINTS = {}


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    difficulty_profile = "easy"
    if difficulty := kwargs.get("difficulty"):
        try:
            d = int(difficulty)
            difficulty_profile = "hard" if d >= 3 else ("medium" if d == 2 else "easy")
        except Exception:
            difficulty_profile = str(difficulty)

    norm_context = {
        "skill_id": 'vh_數學B3_SubSection_1_1_1',
        "problem_type_id": PROBLEM_TYPE_ID,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": difficulty_profile,
        "answer_schema_key": "",
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "fixed_domain_key": "sequence.series",
    }

    constraints = {
        "skill_id": 'vh_數學B3_SubSection_1_1_1',
        "problem_type_id": PROBLEM_TYPE_ID,
        "required_capabilities": [PROBLEM_TYPE_ID],
        "source_example_id": TEXTBOOK_EXAMPLE_ID,
        "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
        "domain_resolution": {
            "skill_id": 'vh_數學B3_SubSection_1_1_1',
            "fixed_domain_key": "sequence.series",
            "selected_operation": PROBLEM_TYPE_ID,
            "domain_module": "core.domain.sequence_series_domain",
            "entrypoint": "build_sequence_series_matrix",
        },
    }
    constraints.update(EXTRA_CONSTRAINTS)

    matrix = _v3_invoke_domain_entrypoint(
        build_sequence_series_matrix,
        entrypoint_name="build_sequence_series_matrix",
        domain_operation=PROBLEM_TYPE_ID,
        seed=seed,
        curriculum_profile="vocational_high_b",
        difficulty_profile=difficulty_profile,
        constraints=constraints,
    )
    matrix = normalize_domain_payload_to_v3_matrix(matrix, norm_context)

    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="",
        domain_operation=PROBLEM_TYPE_ID,
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
