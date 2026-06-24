"""Resolve generator invocation mode for practice runtime."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import importlib.util
from pathlib import Path
import sys
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


@dataclass(frozen=True)
class RuntimeRouteDecision:
    mode: str
    skill_id: str
    module: ModuleType | None = None
    reason: str = ""
    wrapper_path: str = ""
    module_file: str = ""
    wrapper_loaded: bool = False
    legacy_fallback_used: bool = False
    legacy_fallback_reason: str = ""
    error_type: str = ""
    error_message: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "skill_id": self.skill_id,
            "module": self.module,
            "reason": self.reason,
            "wrapper_path": self.wrapper_path,
            "module_file": self.module_file,
            "wrapper_loaded": self.wrapper_loaded,
            "legacy_fallback_used": self.legacy_fallback_used,
            "legacy_fallback_reason": self.legacy_fallback_reason,
            "error_type": self.error_type,
            "error_message": self.error_message,
        }


def resolve_runtime_route_decision(
    *,
    skill_id: str,
    reload_module: bool = False,
    is_b4_phase7b_runtime_skill: bool = False,
    legacy_module_loader: Any | None = None,
) -> RuntimeRouteDecision:
    """Resolve student runtime routing with published V3 facade precedence."""

    wrapper_path = f"skills.{skill_id}"
    if str(skill_id).startswith("jh_") and legacy_module_loader is not None:
        legacy_module = legacy_module_loader(skill_id, reload_module=reload_module)
        if legacy_module is not None and callable(getattr(legacy_module, "generate", None)):
            legacy_route = resolve_generator_route(skill_id=skill_id, loaded_module=legacy_module)
            legacy_mode = "v3" if legacy_route.get("mode") == "modern" else "legacy"
            return RuntimeRouteDecision(
                mode=legacy_mode,
                skill_id=skill_id,
                module=legacy_module,
                reason=(
                    "published_v3_runtime_available"
                    if legacy_mode == "v3"
                    else "legacy_runtime_available"
                ),
                wrapper_path=wrapper_path,
                module_file=_module_file(legacy_module),
                wrapper_loaded=legacy_mode == "v3",
            )

    spec = None
    try:
        spec = importlib.util.find_spec(wrapper_path)
    except (ImportError, AttributeError, ValueError) as exc:
        return RuntimeRouteDecision(
            mode="b4_phase7b" if is_b4_phase7b_runtime_skill else "unavailable",
            skill_id=skill_id,
            reason="v3_facade_import_failed",
            wrapper_path=wrapper_path,
            legacy_fallback_used=is_b4_phase7b_runtime_skill,
            legacy_fallback_reason="v3_facade_import_failed" if is_b4_phase7b_runtime_skill else "",
            error_type=type(exc).__name__,
            error_message=str(exc),
        )

    if spec is None:
        if legacy_module_loader is not None:
            legacy_module = legacy_module_loader(skill_id, reload_module=reload_module)
            if legacy_module is not None and callable(getattr(legacy_module, "generate", None)):
                legacy_route = resolve_generator_route(skill_id=skill_id, loaded_module=legacy_module)
                legacy_mode = "v3" if legacy_route.get("mode") == "modern" else "legacy"
                return RuntimeRouteDecision(
                    mode=legacy_mode,
                    skill_id=skill_id,
                    module=legacy_module,
                    reason=(
                        "published_v3_runtime_available"
                        if legacy_mode == "v3"
                        else "legacy_runtime_available"
                    ),
                    wrapper_path=wrapper_path,
                    module_file=_module_file(legacy_module),
                    wrapper_loaded=legacy_mode == "v3",
                )
        return RuntimeRouteDecision(
            mode="b4_phase7b" if is_b4_phase7b_runtime_skill else "unavailable",
            skill_id=skill_id,
            reason="b4_phase7b_legacy_available" if is_b4_phase7b_runtime_skill else "v3_facade_missing",
            wrapper_path=wrapper_path,
            legacy_fallback_used=is_b4_phase7b_runtime_skill,
            legacy_fallback_reason="v3_facade_missing" if is_b4_phase7b_runtime_skill else "",
        )

    try:
        if reload_module and wrapper_path in sys.modules:
            module = importlib.reload(sys.modules[wrapper_path])
        else:
            module = importlib.import_module(wrapper_path)
    except Exception as exc:
        return RuntimeRouteDecision(
            mode="b4_phase7b" if is_b4_phase7b_runtime_skill else "unavailable",
            skill_id=skill_id,
            reason="v3_facade_import_failed",
            wrapper_path=wrapper_path,
            legacy_fallback_used=is_b4_phase7b_runtime_skill,
            legacy_fallback_reason="v3_facade_import_failed" if is_b4_phase7b_runtime_skill else "",
            error_type=type(exc).__name__,
            error_message=str(exc),
        )

    module_file = _module_file(module)
    generate = getattr(module, "generate", None)
    if not callable(generate):
        return RuntimeRouteDecision(
            mode="b4_phase7b" if is_b4_phase7b_runtime_skill else "unavailable",
            skill_id=skill_id,
            module=module,
            reason="v3_facade_missing_generate",
            wrapper_path=wrapper_path,
            module_file=module_file,
            legacy_fallback_used=is_b4_phase7b_runtime_skill,
            legacy_fallback_reason="v3_facade_missing_generate" if is_b4_phase7b_runtime_skill else "",
        )

    route = resolve_generator_route(skill_id=skill_id, loaded_module=module)
    if route.get("mode") == "modern":
        return RuntimeRouteDecision(
            mode="v3",
            skill_id=skill_id,
            module=module,
            reason="published_v3_runtime_available",
            wrapper_path=wrapper_path,
            module_file=module_file,
            wrapper_loaded=True,
        )

    if route.get("mode") == "legacy":
        return RuntimeRouteDecision(
            mode="legacy",
            skill_id=skill_id,
            module=module,
            reason="legacy_runtime_available",
            wrapper_path=wrapper_path,
            module_file=module_file,
        )

    return RuntimeRouteDecision(
        mode="b4_phase7b" if is_b4_phase7b_runtime_skill else "unavailable",
        skill_id=skill_id,
        module=module,
        reason="b4_phase7b_legacy_available" if is_b4_phase7b_runtime_skill else "runtime_unavailable",
        wrapper_path=wrapper_path,
        module_file=module_file,
        legacy_fallback_used=is_b4_phase7b_runtime_skill,
        legacy_fallback_reason=str(route.get("reason", "runtime_unavailable")) if is_b4_phase7b_runtime_skill else "",
    )


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
