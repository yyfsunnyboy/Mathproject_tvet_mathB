from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = 'vh_數學B1_QuadraticFunctionExtremum'
GENERATOR_KEYS = ['src_4454', 'src_4455', 'src_4457', 'src_4458', 'src_4459', 'src_4463', 'src_4464', 'src_4465', 'src_4469', 'src_4470', 'src_4471', 'src_4472', 'src_4502']
GENERATOR_SPECS = [{'textbook_example_id': 4454, 'component_id': 'src_4454', 'generator_key': 'src_4454', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_vertex_or_parameter_computation', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_quadratic_vertex_or_parameter_computation', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4454, 'source_order': 4454, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4455, 'component_id': 'src_4455', 'generator_key': 'src_4455', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_vertex_or_parameter_computation', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_quadratic_vertex_or_parameter_computation', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4455, 'source_order': 4455, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4457, 'component_id': 'src_4457', 'generator_key': 'src_4457', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_quadratic_vertex', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_compute_quadratic_vertex', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4457, 'source_order': 4457, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4458, 'component_id': 'src_4458', 'generator_key': 'src_4458', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_vertex_or_parameter_computation', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_quadratic_vertex_or_parameter_computation', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4458, 'source_order': 4458, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4459, 'component_id': 'src_4459', 'generator_key': 'src_4459', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_quadratic_vertex', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_compute_quadratic_vertex', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4459, 'source_order': 4459, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4463, 'component_id': 'src_4463', 'generator_key': 'src_4463', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_vertex_or_parameter_computation', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_quadratic_vertex_or_parameter_computation', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4463, 'source_order': 4463, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4464, 'component_id': 'src_4464', 'generator_key': 'src_4464', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_vertex_or_parameter_computation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'text_short_quadratic_vertex_or_parameter_computation', 'checker_key': 'rational_checker', 'equivalence_type': 'rational_equivalent', 'display_order': 4464, 'source_order': 4464, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4465, 'component_id': 'src_4465', 'generator_key': 'src_4465', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_extremum_group_buy_multi', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'integer_compute_quadratic_vertex', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 4465, 'source_order': 4465, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4469, 'component_id': 'src_4469', 'generator_key': 'src_4469', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_vertex_or_parameter_computation', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_quadratic_vertex_or_parameter_computation', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4469, 'source_order': 4469, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4470, 'component_id': 'src_4470', 'generator_key': 'src_4470', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_vertex_or_parameter_computation', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'text_short_quadratic_vertex_or_parameter_computation', 'checker_key': 'rational_checker', 'equivalence_type': 'rational_equivalent', 'display_order': 4470, 'source_order': 4470, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4471, 'component_id': 'src_4471', 'generator_key': 'src_4471', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_extremum_tour_revenue_multi', 'answer_type': 'multi_part', 'answer_value_type': 'multi_part', 'problem_type_id': 'integer_compute_quadratic_vertex', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': 'multi_part_answer', 'display_order': 4471, 'source_order': 4471, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4472, 'component_id': 'src_4472', 'generator_key': 'src_4472', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_vertex_or_parameter_computation', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_quadratic_vertex_or_parameter_computation', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4472, 'source_order': 4472, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4502, 'component_id': 'src_4502', 'generator_key': 'src_4502', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'compute_quadratic_vertex', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_compute_quadratic_vertex', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4502, 'source_order': 4502, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}]


def _resolve_v3_package_root() -> str:
    """Resolve V3 house root from this facade location: skills/ -> <root>/agent_skills_v3."""
    return str((Path(__file__).resolve().parent.parent / "agent_skills_v3").resolve())


def generate(
    level: int = 1,
    seed: int | None = None,
    difficulty: int | str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    return dispatch_generate(
        SKILL_ID,
        GENERATOR_KEYS,
        GENERATOR_SPECS,
        v3_package_root=_resolve_v3_package_root(),
        level=level,
        seed=seed,
        difficulty=difficulty,
        **kwargs,
    )


def check(
    user_answer: Any,
    correct_answer: Any,
    question_payload: dict[str, Any] | None = None,
) -> Any:
    return dispatch_check(
        user_answer,
        correct_answer,
        question_payload=question_payload,
        v3_package_root=_resolve_v3_package_root(),
        skill_id=SKILL_ID,
    )


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return dispatch_get_hint(
        step,
        question_payload=question_payload,
        v3_package_root=_resolve_v3_package_root(),
        skill_id=SKILL_ID,
    )
