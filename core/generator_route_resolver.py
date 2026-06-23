"""Resolve generator invocation mode for practice runtime."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType
from typing import Any


_MODERN_ROUTE_SOURCES = {
    "gencode_wrapper",
    "v3_published",
    "v3_runtime",
    "modern",
}


def _module_file(module: ModuleType | None) -> str:
    return str(getattr(module, "__file__", "") or "")


def _is_plain_skills_module(module: ModuleType | None, skill_id: str) -> bool:
    module_file = _module_file(module)
    if not module_file:
        return False
    path = Path(module_file)
    return path.name == f"{skill_id}.py" and path.parent.name == "skills"


def _has_modern_generator_contract(module: ModuleType | None) -> bool:
    if module is None:
        return False
    if hasattr(module, "GENERATOR_SPECS") or hasattr(module, "GENERATOR_KEYS"):
        return True
    generate = getattr(module, "generate", None)
    if generate is None:
        return False
    module_name = str(getattr(generate, "__module__", ""))
    return module_name.startswith("core.gencode.") or module_name.startswith("agent_skills_v3.")


def resolve_generator_route(
    *,
    skill_id: str,
    loaded_module: ModuleType | None = None,
    existing_route_source: str | None = None,
) -> dict[str, Any]:
    """Classify how a runtime generator should be invoked.

    The resolver is intentionally conservative: explicit modern wrappers win,
    plain junior-high files stay legacy, and missing modules are unavailable.
    """

    if loaded_module is None or not callable(getattr(loaded_module, "generate", None)):
        return {
            "mode": "unavailable",
            "reason": "module_or_generate_missing",
            "module": loaded_module,
        }

    if _has_modern_generator_contract(loaded_module):
        return {
            "mode": "modern",
            "reason": "existing_v3_runtime",
            "module": loaded_module,
        }

    # Authority modern evidence check
    has_authority_evidence = (
        hasattr(loaded_module, "GENERATOR_SPECS") or
        hasattr(loaded_module, "GENERATOR_KEYS") or
        hasattr(loaded_module, "dispatch_generate") or
        (existing_route_source in _MODERN_ROUTE_SOURCES)
    )

    if not has_authority_evidence and skill_id.startswith("jh_") and _is_plain_skills_module(loaded_module, skill_id):
        return {
            "mode": "legacy",
            "reason": "plain_jh_skill_module",
            "module": loaded_module,
        }

    route_source = str(existing_route_source or "").strip()
    if route_source in _MODERN_ROUTE_SOURCES:
        return {
            "mode": "modern",
            "reason": f"existing_route_source:{route_source}",
            "module": loaded_module,
        }

    return {
        "mode": "modern",
        "reason": "default_runtime_module",
        "module": loaded_module,
    }
