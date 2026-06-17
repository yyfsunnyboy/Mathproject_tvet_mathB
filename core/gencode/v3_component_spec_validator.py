"""Validate consistency between tracker specs and component metadata."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


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

    metadata_presentation = str(_metadata_value(module, "PRESENTATION_MODE") or "").strip()
    spec_presentation = str(generator_spec.get("presentation_mode") or "").strip()
    if metadata_presentation and spec_presentation and metadata_presentation != spec_presentation:
        errors.append(
            f"{component_id}: presentation_mode mismatch "
            f"(spec={spec_presentation!r}, metadata={metadata_presentation!r})"
        )

    metadata_source_kind = str(_metadata_value(module, "SOURCE_KIND") or "").strip()
    spec_source_kind = str(generator_spec.get("source_kind") or "").strip()
    if metadata_source_kind and spec_source_kind and metadata_source_kind != spec_source_kind:
        errors.append(
            f"{component_id}: source_kind mismatch "
            f"(spec={spec_source_kind!r}, metadata={metadata_source_kind!r})"
        )

    answer_verification = _metadata_value(module, "ANSWER_VERIFICATION_TYPE")
    if isinstance(answer_verification, dict):
        metadata_answer_type = str(answer_verification.get("answer_type") or "").strip()
        spec_answer_type = str(generator_spec.get("answer_type") or "").strip()
        if metadata_answer_type and spec_answer_type and metadata_answer_type != spec_answer_type:
            errors.append(
                f"{component_id}: answer_type mismatch "
                f"(spec={spec_answer_type!r}, metadata={metadata_answer_type!r})"
            )

    metadata_target = str(_metadata_value(module, "TARGET_TASK") or "").strip()
    spec_problem_type = str(generator_spec.get("problem_type_id") or "").strip()
    if metadata_target and spec_problem_type and metadata_target != spec_problem_type:
        errors.append(
            f"{component_id}: problem_type_id mismatch "
            f"(spec={spec_problem_type!r}, metadata TARGET_TASK={metadata_target!r})"
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
