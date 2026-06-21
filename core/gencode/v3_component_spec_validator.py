"""Validate consistency between tracker specs and component metadata."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from core.gencode.v3_component_scaffold_builder import normalize_v3_component_metadata_fields

_RESPONSE_MODE_VALUES = frozenset({
    "expression",
    "single_choice",
    "short_answer",
    "text_short",
    "multi_part",
})


def _load_metadata_module(metadata_path: Path) -> Any:
    module_name = f"v3_metadata_validator_{abs(hash(str(metadata_path)))}"
    spec = importlib.util.spec_from_file_location(module_name, metadata_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"metadata_module_load_failed:{metadata_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _metadata_value(module: Any, name: str) -> str | int | None:
    value = getattr(module, name, None)
    if value is None:
        return None
    return value


def _metadata_response_mode(module: Any) -> str:
    direct = str(
        _metadata_value(module, "RESPONSE_MODE")
        or _metadata_value(module, "INTERACTION_TYPE")
        or ""
    ).strip()
    if direct:
        return direct
    presentation = str(_metadata_value(module, "PRESENTATION_MODE") or "").strip()
    if presentation == "single_choice":
        return "single_choice"
    legacy_answer_type = str(_metadata_value(module, "ANSWER_TYPE") or "").strip()
    if legacy_answer_type in _RESPONSE_MODE_VALUES:
        return legacy_answer_type
    return "expression" if presentation == "short_answer" else presentation


def _metadata_answer_value_type(module: Any) -> str:
    direct = str(_metadata_value(module, "ANSWER_VALUE_TYPE") or "").strip()
    if direct:
        return direct
    answer_verification = _metadata_value(module, "ANSWER_VERIFICATION_TYPE")
    if isinstance(answer_verification, dict):
        direct = str(answer_verification.get("answer_value_type") or "").strip()
        if direct:
            return direct
        legacy = str(answer_verification.get("answer_type") or "").strip()
        if legacy and legacy not in _RESPONSE_MODE_VALUES:
            return legacy
    legacy_answer_type = str(_metadata_value(module, "ANSWER_TYPE") or "").strip()
    if legacy_answer_type and legacy_answer_type not in _RESPONSE_MODE_VALUES:
        return legacy_answer_type
    return ""


def _metadata_problem_type_id(module: Any) -> tuple[str, list[str]]:
    errors: list[str] = []
    problem_type = str(_metadata_value(module, "PROBLEM_TYPE_ID") or "").strip()
    target_task = str(_metadata_value(module, "TARGET_TASK") or "").strip()
    if problem_type and target_task and problem_type != target_task:
        errors.append(
            "problem_type_id alias mismatch "
            f"(metadata PROBLEM_TYPE_ID={problem_type!r}, metadata TARGET_TASK={target_task!r})"
        )
    return problem_type or target_task, errors


def validate_generator_spec_against_metadata(
    generator_spec: dict[str, Any],
    metadata_path: Path,
) -> list[str]:
    """Return validation error messages; empty list means consistent."""
    if not metadata_path.is_file():
        return []

    module = _load_metadata_module(metadata_path)
    errors: list[str] = []
    component_id = str(generator_spec.get("component_id") or "")

    metadata_component_id = str(_metadata_value(module, "COMPONENT_ID") or "").strip()
    if metadata_component_id and component_id and metadata_component_id != component_id:
        errors.append(
            f"{component_id}: component identity mismatch "
            f"(generator_spec.component_id={component_id!r}, metadata COMPONENT_ID={metadata_component_id!r})"
        )

    metadata_presentation = str(_metadata_value(module, "PRESENTATION_MODE") or "").strip()
    spec_presentation = str(generator_spec.get("presentation_mode") or "").strip()
    if metadata_presentation and spec_presentation and metadata_presentation != spec_presentation:
        errors.append(
            f"{component_id}: presentation_mode mismatch "
            f"(spec={spec_presentation!r}, metadata={metadata_presentation!r})"
        )

    normalized_spec = normalize_v3_component_metadata_fields(generator_spec)
    metadata_response = _metadata_response_mode(module)
    spec_response = normalized_spec["response_mode"]
    if metadata_response and spec_response and metadata_response != spec_response:
        errors.append(
            f"{component_id}: response_mode mismatch "
            f"(generator_spec.response_mode={spec_response!r}, metadata response_mode={metadata_response!r})"
        )

    metadata_source_kind = str(_metadata_value(module, "SOURCE_KIND") or "").strip()
    spec_source_kind = str(generator_spec.get("source_kind") or "").strip()
    if metadata_source_kind and spec_source_kind and metadata_source_kind != spec_source_kind:
        errors.append(
            f"{component_id}: source_kind mismatch "
            f"(spec={spec_source_kind!r}, metadata={metadata_source_kind!r})"
        )

    metadata_answer_value = _metadata_answer_value_type(module)
    spec_answer_value = normalized_spec["answer_value_type"]
    if metadata_answer_value and spec_answer_value and metadata_answer_value != spec_answer_value:
        errors.append(
            f"{component_id}: answer_value_type mismatch "
            f"(generator_spec.answer_value_type={spec_answer_value!r}, metadata answer_value_type={metadata_answer_value!r})"
        )

    metadata_problem_type, alias_errors = _metadata_problem_type_id(module)
    for alias_error in alias_errors:
        errors.append(f"{component_id}: {alias_error}")
    spec_problem_type = str(generator_spec.get("problem_type_id") or "").strip()
    if metadata_problem_type and spec_problem_type and metadata_problem_type != spec_problem_type:
        errors.append(
            f"{component_id}: problem_type_id mismatch "
            f"(generator_spec.problem_type_id={spec_problem_type!r}, metadata problem_type_id={metadata_problem_type!r})"
        )

    return errors


def assert_generator_specs_metadata_consistent(
    *,
    sandbox_root: str,
    skill_id: str,
    generator_specs: list[dict[str, Any]],
) -> None:
    """Raise ValueError when any on-disk metadata disagrees with generator specs."""
    root = Path(sandbox_root)
    skill_key = str(skill_id or "").strip()
    candidate_roots = [
        root / "agent_skills_v3" / skill_key / "components",
        root / skill_key / "components",
    ]
    all_errors: list[str] = []
    for spec in generator_specs:
        component_id = str(spec.get("component_id") or "").strip()
        if not component_id:
            continue
        metadata_path = None
        for base in candidate_roots:
            candidate = base / component_id / "metadata.py"
            if candidate.is_file():
                metadata_path = candidate
                break
        if metadata_path is None:
            continue
        all_errors.extend(validate_generator_spec_against_metadata(spec, metadata_path))

    if all_errors:
        raise ValueError("generator_spec_metadata_inconsistent: " + "; ".join(all_errors))
