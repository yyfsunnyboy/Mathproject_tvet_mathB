# -*- coding: utf-8 -*-
"""Read-only context loader for Qwen Gencode experiments."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from core.gencode.answer_schema_registry import ANSWER_SCHEMAS
from core.gencode.pipeline_orchestrator import _ALLOWED_CHECKERS
from core.gencode.qwen_experiment.constants import GENERATE_INTERFACE_SPEC
from core.gencode.services.component_tracker_service import derive_component_id

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB = PROJECT_ROOT / "instance" / "kumon_math.db"


def load_textbook_example(
    example_id: int,
    *,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    path = Path(db_path) if db_path else DEFAULT_DB
    if not path.is_file():
        raise FileNotFoundError(f"textbook_db_missing:{path}")
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        row = con.execute(
            """
            SELECT id, skill_id, problem_text, correct_answer, detailed_solution,
                   source_description, problem_type, question_type
            FROM textbook_examples
            WHERE id = ?
            """,
            (int(example_id),),
        ).fetchone()
    finally:
        con.close()
    if row is None:
        raise ValueError(f"textbook_example_not_found:{example_id}")
    data = dict(row)
    skill_id = str(data.get("skill_id") or "").strip()
    if not skill_id:
        raise ValueError(f"textbook_example_missing_skill_id:{example_id}")
    component_id = derive_component_id(int(example_id))
    return {
        "textbook_example_id": int(example_id),
        "skill_id": skill_id,
        "component_id": component_id,
        "source_id": component_id,
        "problem_text": str(data.get("problem_text") or ""),
        "correct_answer": str(data.get("correct_answer") or ""),
        "detailed_solution": str(data.get("detailed_solution") or ""),
        "source_description": str(data.get("source_description") or ""),
        "problem_type": str(data.get("problem_type") or ""),
        "question_type": str(data.get("question_type") or ""),
    }


def load_domain_context(skill_id: str) -> dict[str, Any]:
    fixed_domain_key = ""
    allowed_operations: list[str] = []
    domain_module = ""
    entrypoint = ""
    registry_revision = ""
    try:
        from core.registry.taxonomy_registry import resolve_domain_for_skill

        resolved = resolve_domain_for_skill(skill_id)
        fixed_domain_key = str(resolved.get("fixed_domain_key") or "")
        allowed_operations = list(resolved.get("allowed_operations") or [])
        domain_module = str(resolved.get("domain_module") or "")
        entrypoint = str(resolved.get("entrypoint") or "")
        registry_revision = str(resolved.get("registry_revision") or "")
    except Exception as exc:
        return {
            "skill_id": skill_id,
            "fixed_domain_key": "",
            "allowed_operations": [],
            "domain_module": "",
            "entrypoint": "",
            "registry_revision": "",
            "resolve_error": str(exc),
            "candidate_capability_allowed_in_artifact_only": True,
        }
    return {
        "skill_id": skill_id,
        "fixed_domain_key": fixed_domain_key,
        "allowed_operations": allowed_operations,
        "domain_module": domain_module,
        "entrypoint": entrypoint,
        "registry_revision": registry_revision,
        "candidate_capability_allowed_in_artifact_only": True,
    }


def build_experiment_context(
    example_id: int,
    *,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    example = load_textbook_example(example_id, db_path=db_path)
    domain = load_domain_context(example["skill_id"])
    return {
        **example,
        "domain": domain,
        "generate_interface_spec": GENERATE_INTERFACE_SPEC,
        "allowed_checkers": sorted(_ALLOWED_CHECKERS),
        "answer_schema_keys": sorted(ANSWER_SCHEMAS.keys()),
    }
