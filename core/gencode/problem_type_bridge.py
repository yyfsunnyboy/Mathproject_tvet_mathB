"""
core/gencode/problem_type_bridge.py
=====================================
ProblemType Bridge: maps semantic primary problem_type_ids (e.g. from
human_confirmed rule packs) to runtime presentation variants backed by
registered slot generators.

Rules (enforced here, not in callers):
  - No skill_id hardcodes.  Bridge is problem_type-level / taxonomy-level.
  - If a problem_type_id matches a bridge entry, Phase 2 must expand to
    runtime_variants rather than packaging the primary as a runtime generator.
  - single_primary_problem_type means source classification converges; it does
    NOT mean only one runtime generator is allowed.
  - If a bridge lookup fails, return BRIDGE_MISSING status — callers must NOT
    fall back to contextual_application.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_BRIDGE_PATH = Path(__file__).resolve().parents[2] / "configs" / "gencode" / "problem_type_bridges.yaml"
_BRIDGE_CACHE: dict[str, dict[str, Any]] | None = None

BRIDGE_MISSING = "problem_type_bridge_missing"
BRIDGE_PENDING_READINESS = "pending_template"


def _load_bridges() -> dict[str, dict[str, Any]]:
    global _BRIDGE_CACHE
    if _BRIDGE_CACHE is not None:
        return _BRIDGE_CACHE
    if not _BRIDGE_PATH.exists():
        _BRIDGE_CACHE = {}
        return _BRIDGE_CACHE
    try:
        with _BRIDGE_PATH.open("r", encoding="utf-8") as fh:
            root = yaml.safe_load(fh) or {}
    except Exception:
        _BRIDGE_CACHE = {}
        return _BRIDGE_CACHE
    _BRIDGE_CACHE = dict(root.get("bridges") or {})
    return _BRIDGE_CACHE


def reset_bridge_cache() -> None:
    """For use in tests only."""
    global _BRIDGE_CACHE
    _BRIDGE_CACHE = None


def get_bridge(primary_problem_type_id: str) -> dict[str, Any] | None:
    """Return the bridge entry for *primary_problem_type_id*, or None if not found."""
    pid = str(primary_problem_type_id or "").strip()
    if not pid:
        return None
    return _load_bridges().get(pid)


def has_bridge(primary_problem_type_id: str) -> bool:
    """Return True if a bridge exists for *primary_problem_type_id*."""
    return get_bridge(primary_problem_type_id) is not None


def get_runtime_variants(primary_problem_type_id: str) -> list[dict[str, Any]]:
    """Return the runtime_variants list for *primary_problem_type_id*.

    Returns an empty list if the bridge is not found.
    """
    bridge = get_bridge(primary_problem_type_id)
    if not isinstance(bridge, dict):
        return []
    variants = bridge.get("runtime_variants") or []
    return [v for v in variants if isinstance(v, dict) and v.get("problem_type_id")]


def expand_primary_to_runtime_variants(
    skill_id: str,
    primary_problem_type_id: str,
    source_example_ids: list[int] | None = None,
) -> tuple[list[dict[str, Any]], str]:
    """Expand a semantic primary problem_type_id to runtime presentation variants.

    Returns (variants, status).
    - status = "ok" when bridge found and variants produced.
    - status = BRIDGE_MISSING when no bridge exists.

    Each returned variant dict has:
      problem_type_id, presentation_mode, answer_type, checker_key,
      equivalence_type, template_slot, skill_id, semantic_primary_problem_type_id,
      source_bridge_problem_type_id, source_example_ids, spec_source,
      generator_readiness, usable_for_phase3, answer_contract, generator_contract.
    """
    pid = str(primary_problem_type_id or "").strip()
    sid = str(skill_id or "").strip()
    variants_raw = get_runtime_variants(pid)
    if not variants_raw:
        return [], BRIDGE_MISSING

    ex_ids = list(source_example_ids or [])
    result: list[dict[str, Any]] = []
    for v in variants_raw:
        pt_id = str(v.get("problem_type_id", "")).strip()
        template_slot = str(v.get("template_slot", "")).strip()
        answer_type = str(v.get("answer_type", "text_short")).strip()
        checker_key = str(v.get("checker_key", "text_short_checker")).strip()
        equivalence_type = str(v.get("equivalence_type", "exact_string")).strip()
        presentation_mode = str(v.get("presentation_mode", "short_answer")).strip()

        # Normalise legacy answer_type tokens.
        if answer_type == "single_choice":
            answer_type = "choice"
        is_choice = presentation_mode == "single_choice" or answer_type in {"choice", "single_choice"}

        result.append(
            {
                "problem_type_id": pt_id,
                "skill_id": sid,
                "target_task": pt_id,
                "task_family": _load_bridges().get(pid, {}).get("semantic_family", ""),
                "display_name": pt_id.replace("_", " "),
                "presentation_mode": presentation_mode,
                "semantic_primary_problem_type_id": pid,
                "source_bridge_problem_type_id": pid,
                "source_example_ids": ex_ids,
                "spec_source": "problem_type_bridge_expansion",
                "generator_readiness": "runtime_ready",
                "usable_for_phase3": True,
                "answer_contract": {
                    "answer_type": "single_choice" if is_choice else answer_type,
                    "checker_key": checker_key,
                    "checker": checker_key,
                    "equivalence_type": equivalence_type,
                    "choices_required": is_choice,
                    "frontend_render_choices": is_choice,
                    "presentation_mode": presentation_mode,
                },
                "generator_contract": {
                    "template_slots": {"stem": template_slot},
                    "template_families": [pt_id],
                },
            }
        )
    return result, "ok"


def is_bridge_primary(problem_type_id: str) -> bool:
    """True when *problem_type_id* is a semantic bridge primary (not a runtime variant)."""
    return has_bridge(problem_type_id)


def all_bridge_primary_ids() -> list[str]:
    """Return all registered semantic primary problem_type_ids."""
    return list(_load_bridges().keys())
