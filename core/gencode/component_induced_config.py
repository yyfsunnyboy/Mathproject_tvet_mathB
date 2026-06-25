"""Load component-local induced specs into domain generator constraints."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_text(path.read_text(encoding="utf-8"))


def load_component_induced_config(component_dir: Path) -> dict[str, Any]:
    """Load component-local induced configuration (no example_id routing)."""
    component_dir = Path(component_dir)
    for name in ("generator_config.json", "induced_spec.json"):
        path = component_dir / name
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError(f"invalid_component_config:{path}")
            data["_config_path"] = str(path)
            data["_config_sha256"] = sha256_file(path)
            return data
    raise FileNotFoundError(f"component_induced_config_missing:{component_dir}")


def induced_constraints_from_config(config: dict[str, Any]) -> dict[str, Any]:
    """Flatten component induced config into domain matrix constraints."""
    spec = config.get("induced_spec")
    if not isinstance(spec, dict):
        spec = config

    constraints: dict[str, Any] = dict(spec.get("domain_constraints") or {})
    for key in (
        "task_topology",
        "cumulative_table_blank_fill",
        "render_mode",
        "presentation_mode",
        "cumulative_direction",
        "sub_questions",
        "table_columns",
        "table_rows",
        "blank_fields",
        "question_text",
        "story_context",
        "variable_unit",
        "threshold",
        "thresholds",
        "interval_low",
        "interval_high",
        "low_bound",
        "high_bound",
    ):
        if key in spec and spec.get(key) is not None:
            constraints[key] = spec[key]

    if spec.get("data_points") and not constraints.get("graph_points"):
        constraints["graph_points"] = [
            {"class_bound": p.get("x"), "cumulative_count": p.get("y"), "x": p.get("x"), "y": p.get("y")}
            for p in spec["data_points"]
        ]

    if config.get("question_text"):
        constraints["question_text"] = config["question_text"]
    if config.get("domain_operation"):
        constraints["domain_operation_hint"] = config["domain_operation"]

    return constraints


def resolve_domain_operation(config: dict[str, Any]) -> str:
    op = str(
        config.get("domain_operation")
        or (config.get("induced_spec") or {}).get("suggested_domain_operation")
        or ""
    ).strip()
    if not op:
        raise ValueError("domain_operation_missing_in_component_config")
    return op


def build_component_generate_context(component_dir: Path) -> dict[str, Any]:
    """Return config metadata used by component generate.py (no example_id in domain)."""
    config = load_component_induced_config(component_dir)
    source_path = str(config.get("source_artifact_path") or config.get("_config_path") or "")
    return {
        "config": config,
        "domain_operation": resolve_domain_operation(config),
        "constraints": induced_constraints_from_config(config),
        "presentation_mode": str(config.get("presentation_mode") or "short_answer"),
        "source_artifact_path": source_path,
        "source_artifact_sha256": str(config.get("source_artifact_sha256") or config.get("_config_sha256") or ""),
        "generated_config_sha256": str(config.get("_config_sha256") or ""),
    }
