"""Runtime bridge from component-local induced config to domain matrix payload."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.domain.statistics.frequency_distribution_domain import build_cumulative_frequency_matrix
from core.gencode.component_induced_config import build_component_generate_context
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.table_question_contract import normalize_table_question_payload


def generate_cumulative_component_payload(
    component_dir: Path,
    *,
    seed: int | None = None,
    level: int = 1,
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate a practice payload using only component-local induced configuration."""
    del level
    component_dir = Path(component_dir)
    ctx = build_component_generate_context(component_dir)
    domain_operation = str(ctx["domain_operation"])
    matrix = build_cumulative_frequency_matrix(
        seed=seed,
        domain_operation=domain_operation,
        constraints=dict(ctx["constraints"]),
    )
    answer_type = str(matrix.get("answer_type") or "integer")
    presentation_mode = (
        "single_choice"
        if answer_type == "single_choice"
        else str(ctx.get("presentation_mode") or "short_answer")
    )
    component_id = str(kwargs.get("component_id") or component_dir.name)
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=presentation_mode,
        answer_type=answer_type,
        problem_type_id=domain_operation,
        component_id=component_id,
        textbook_example_id=kwargs.get("textbook_example_id"),
        domain_operation=domain_operation,
    )
    if isinstance(matrix.get("validation_facts"), dict):
        payload["validation_facts"] = matrix["validation_facts"]
    payload["component_id"] = component_id
    payload["seed"] = seed
    payload["domain_operation"] = domain_operation
    payload["fixed_domain_key"] = "statistics.frequency_distribution"
    payload["generator_config_sha256"] = ctx.get("generated_config_sha256", "")
    payload["source_artifact_path"] = ctx.get("source_artifact_path", "")
    payload["source_artifact_sha256"] = ctx.get("source_artifact_sha256", "")
    if matrix.get("image_base64"):
        payload["image_base64"] = matrix["image_base64"]
    if matrix.get("table_data"):
        payload["table_data"] = matrix["table_data"]
    if matrix.get("subquestions"):
        payload["subquestions"] = matrix["subquestions"]
    if matrix.get("explanation"):
        payload["explanation"] = matrix["explanation"]
    return normalize_table_question_payload(payload)
