"""Skill-Fixed Domain Authority — deterministic routing gates for Gencode V3."""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.registry.domain_operation_registry import (
    get_domain_operations,
    get_domain_spec,
)
from core.registry.taxonomy_registry import (
    SkillDomainNotRegisteredError,
    get_allowed_operations,
    get_confirmed_skill_binding,
    get_fixed_domain_key,
    get_registry_revision,
    is_confirmed_skill_binding,
    resolve_domain_for_skill,
)
from core.gencode.v3_error_codes import (
    DOMAIN_BINDING_MISSING,
    DOMAIN_BINDING_CONFLICT,
    DOMAIN_EVIDENCE_INCOMPLETE,
    DOMAIN_FUNCTION_MISSING,
    DOMAIN_OPERATION_MISSING,
    DOMAIN_OVERRIDE_NOT_FOUND,
    DOMAIN_CAPABILITY_PARTIAL,
    DOMAIN_CAPABILITY_UNRESOLVED,
    DOMAIN_CAPABILITY_AMBIGUOUS,
    DOMAIN_PROVIDER_MISSING,
    DOMAIN_ADAPTER_FAILED,
)

logger = logging.getLogger(__name__)

# Routing blocker codes (also used as tracker gencode_status where applicable).
SKILL_DOMAIN_NOT_REGISTERED = DOMAIN_BINDING_MISSING
DOMAIN_OPERATION_NOT_ALLOWED = "domain_operation_not_allowed"
UNSUPPORTED_DOMAIN_OPERATION = "unsupported_domain_operation"
FIXED_DOMAIN_VIOLATION = "fixed_domain_violation"
OPERATION_CONTRACT_MISMATCH = "operation_contract_mismatch"

AI_IGNORED_ROUTING_FIELDS = frozenset(
    {
        "domain_key",
        "domain_family",
        "recommended_skill",
        "nearest_template",
        "domain",
        "fixed_domain_key",
    }
)

def _build_providers_from_registry() -> dict:
    """Build DOMAIN_PROVIDERS from the single authoritative domain_operation_registry.

    allowed_operations is no longer hardcoded here; it is always read from the
    registry so that registering a new operation in domain_operation_registry.py
    is the only change required.
    """
    from core.registry.domain_operation_registry import list_registered_domains, get_domain_spec
    result = {}
    for dk in list_registered_domains():
        spec = get_domain_spec(dk)
        if spec is None:
            continue
        result[dk] = {
            "domain_module": spec.domain_module,
            "entrypoint": spec.entrypoint,
            "capabilities": spec.capabilities,
            "allowed_operations": spec.allowed_operations,
        }
    return result


# Registry of domain capabilities & providers.
# allowed_operations is authoritative and derived from domain_operation_registry.
DOMAIN_PROVIDERS: dict = _build_providers_from_registry()


def get_domain_providers_for_resolution() -> dict[str, dict[str, Any]]:
    """Merge production registry providers with verified bootstrap candidates."""
    try:
        from core.gencode.domain_bootstrap.candidate_registry import merge_bootstrap_providers

        return merge_bootstrap_providers(DOMAIN_PROVIDERS)
    except Exception:
        return dict(DOMAIN_PROVIDERS)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
_thread_local = threading.local()


class ComponentOverrideContext:
    def __init__(self, extra: dict[str, Any] | None = None, component_id: str | None = None):
        self.extra = extra or {}
        self.component_id = component_id

    def __enter__(self):
        if not hasattr(_thread_local, "contexts"):
            _thread_local.contexts = []
        _thread_local.contexts.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _thread_local.contexts.pop()


def get_current_component_override_context():
    if hasattr(_thread_local, "contexts") and _thread_local.contexts:
        return _thread_local.contexts[-1]
    return None


class SkillFixedDomainError(ValueError):
    """Base error for skill-fixed domain authority violations."""

    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = str(code)
        self.details = dict(details or {})


@dataclass(frozen=True)
class FixedDomainContext:
    skill_id: str
    fixed_domain_key: str
    allowed_operations: tuple[str, ...]
    registry_revision: str
    domain_module: str
    entrypoint: str
    curriculum_profile: str


@dataclass(frozen=True)
class DomainResolutionResult:
    """Unified domain authority outcome consumed by generation, verify, and publish."""

    skill_id: str
    fixed_domain_key: str
    resolution_source: str
    binding_status: str
    required_capabilities: tuple[str, ...]
    matched_capabilities: tuple[str, ...]
    selected_operation: str
    registry_revision: str
    domain_module: str
    entrypoint: str
    allowed_operations: tuple[str, ...] = ()
    curriculum_profile: str = "vocational_high_b"

    def to_fixed_domain_context(self) -> FixedDomainContext:
        return FixedDomainContext(
            skill_id=self.skill_id,
            fixed_domain_key=self.fixed_domain_key,
            allowed_operations=self.allowed_operations,
            registry_revision=self.registry_revision,
            domain_module=self.domain_module,
            entrypoint=self.entrypoint,
            curriculum_profile=self.curriculum_profile,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "fixed_domain_key": self.fixed_domain_key,
            "resolution_source": self.resolution_source,
            "binding_status": self.binding_status,
            "required_capabilities": list(self.required_capabilities),
            "matched_capabilities": list(self.matched_capabilities),
            "selected_operation": self.selected_operation,
            "registry_revision": self.registry_revision,
            "domain_module": self.domain_module,
            "entrypoint": self.entrypoint,
            "allowed_operations": list(self.allowed_operations),
            "curriculum_profile": self.curriculum_profile,
        }


def build_domain_resolution_evidence(
    result: DomainResolutionResult,
    *,
    source_hash: str = "",
) -> dict[str, Any]:
    """Persistable component-level domain resolution evidence."""
    evidence = result.to_dict()
    evidence.update(
        {
            "domain_operation": result.selected_operation,
            "problem_type_id": result.selected_operation,
            "source_hash": str(source_hash or "").strip(),
        }
    )
    return evidence


def enrich_induced_spec_with_domain_evidence(
    payload: dict[str, Any],
    *,
    resolution: DomainResolutionResult | dict[str, Any] | None = None,
    source_hash: str = "",
) -> dict[str, Any]:
    merged = dict(payload or {})
    if isinstance(resolution, DomainResolutionResult):
        evidence = build_domain_resolution_evidence(resolution, source_hash=source_hash)
    elif isinstance(resolution, dict):
        evidence = dict(resolution)
    else:
        evidence = {}
    if evidence:
        merged.update(evidence)
        merged["domain_resolution"] = {
            key: evidence.get(key)
            for key in (
                "fixed_domain_key",
                "resolution_source",
                "binding_status",
                "required_capabilities",
                "matched_capabilities",
                "selected_operation",
                "registry_revision",
                "domain_module",
                "entrypoint",
                "source_hash",
            )
        }
    return merged


def extract_domain_evidence_from_spec(spec: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(spec, dict):
        return {}
    nested = spec.get("domain_resolution")
    evidence = dict(nested) if isinstance(nested, dict) else {}
    for key in (
        "fixed_domain_key",
        "resolution_source",
        "binding_status",
        "required_capabilities",
        "matched_capabilities",
        "selected_operation",
        "domain_operation",
        "problem_type_id",
        "registry_revision",
        "domain_module",
        "entrypoint",
        "source_hash",
    ):
        if key in spec and spec.get(key) not in (None, ""):
            evidence.setdefault(key, spec.get(key))
    operation = str(
        evidence.get("selected_operation")
        or evidence.get("domain_operation")
        or evidence.get("problem_type_id")
        or ""
    ).strip()
    if operation:
        evidence["selected_operation"] = operation
    return evidence


def validate_component_domain_evidence(spec: dict[str, Any] | None) -> list[str]:
    """Validate publish-time domain evidence without re-resolving skill binding."""
    evidence = extract_domain_evidence_from_spec(spec)
    blockers: list[str] = []

    fixed_domain_key = str(evidence.get("fixed_domain_key") or "").strip()
    if not fixed_domain_key:
        blockers.append(f"{DOMAIN_EVIDENCE_INCOMPLETE}:fixed_domain_key")
        return blockers

    selected_operation = str(evidence.get("selected_operation") or "").strip()
    if not selected_operation:
        blockers.append(f"{DOMAIN_EVIDENCE_INCOMPLETE}:selected_operation")
        return blockers

    binding_status = str(evidence.get("binding_status") or "").strip()
    resolution_source = str(evidence.get("resolution_source") or "").strip()
    if binding_status == "derived" or resolution_source == "derived_capability_match":
        matched = normalize_capability_list(evidence.get("matched_capabilities"))
        if not matched:
            blockers.append(f"{DOMAIN_EVIDENCE_INCOMPLETE}:matched_capabilities")

    provider = DOMAIN_PROVIDERS.get(fixed_domain_key)
    if provider is None:
        blockers.append(DOMAIN_PROVIDER_MISSING)
        return blockers

    domain_module = str(evidence.get("domain_module") or provider.get("domain_module") or "").strip()
    entrypoint = str(evidence.get("entrypoint") or provider.get("entrypoint") or "").strip()
    if not domain_module:
        blockers.append(f"{DOMAIN_EVIDENCE_INCOMPLETE}:domain_module")
    if not entrypoint:
        blockers.append(f"{DOMAIN_EVIDENCE_INCOMPLETE}:entrypoint")

    allowed_ops = tuple(provider.get("allowed_operations") or ())
    if selected_operation not in allowed_ops:
        blockers.append(DOMAIN_OPERATION_NOT_ALLOWED)

    required = normalize_capability_list(evidence.get("required_capabilities"))
    if required:
        prov_caps = _provider_capability_set(provider)
        missing = sorted(set(required) - prov_caps)
        if missing:
            blockers.append(DOMAIN_CAPABILITY_PARTIAL)

    return blockers


def summarize_skill_domain_binding(
    *,
    skill_id: str,
    component_specs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarize skill-level domain authority from component evidence."""
    skill_key = str(skill_id or "").strip()
    confirmed = get_confirmed_skill_binding(skill_key)
    verified_specs = [spec for spec in component_specs if isinstance(spec, dict) and spec]

    derived_domains: list[str] = []
    resolution_sources: list[str] = []
    binding_statuses: list[str] = []
    conflict_detected = False

    for spec in verified_specs:
        evidence = extract_domain_evidence_from_spec(spec)
        status = str(evidence.get("binding_status") or "").strip()
        source = str(evidence.get("resolution_source") or "").strip()
        domain_key = str(evidence.get("fixed_domain_key") or spec.get("fixed_domain_key") or "").strip()
        if status:
            binding_statuses.append(status)
        if source:
            resolution_sources.append(source)
        if domain_key:
            derived_domains.append(domain_key)
        if spec.get("error_code") == DOMAIN_BINDING_CONFLICT:
            conflict_detected = True

    if conflict_detected:
        return {
            "domain_binding_status": "binding_conflict",
            "domain_resolution_source": "confirmed_binding",
            "resolved_domain_key": confirmed.get("fixed_domain_key") if confirmed else "",
            "confirmed_binding": bool(confirmed),
        }

    if confirmed:
        confirmed_key = str(confirmed.get("fixed_domain_key") or "").strip()
        return {
            "domain_binding_status": "confirmed_binding",
            "domain_resolution_source": "confirmed_binding",
            "resolved_domain_key": confirmed_key,
            "confirmed_binding": True,
        }

    if derived_domains:
        return {
            "domain_binding_status": "derived_binding",
            "domain_resolution_source": resolution_sources[0] if resolution_sources else "derived_capability_match",
            "resolved_domain_key": derived_domains[0],
            "confirmed_binding": False,
        }

    return {
        "domain_binding_status": "domain_unresolved",
        "domain_resolution_source": "",
        "resolved_domain_key": "",
        "confirmed_binding": False,
    }


def _confirmed_binding_result(
    *,
    skill_id: str,
    routing: dict[str, Any],
    fixed_domain_key: str,
    allowed: tuple[str, ...],
    required_capabilities: list[str],
) -> DomainResolutionResult:
    provider = DOMAIN_PROVIDERS.get(fixed_domain_key) or {}
    prov_caps = _provider_capability_set(provider)
    matched = sorted(set(required_capabilities) & prov_caps)
    selected = str(
        routing.get("selected_operation")
        or routing.get("domain_operation")
        or ""
    ).strip()
    return DomainResolutionResult(
        skill_id=skill_id,
        fixed_domain_key=fixed_domain_key,
        resolution_source="confirmed_binding",
        binding_status="confirmed",
        required_capabilities=tuple(required_capabilities),
        matched_capabilities=tuple(matched),
        selected_operation=selected,
        registry_revision=get_registry_revision(skill_id),
        domain_module=str(routing.get("domain_module") or provider.get("domain_module") or ""),
        entrypoint=str(routing.get("entrypoint") or provider.get("entrypoint") or ""),
        allowed_operations=allowed,
        curriculum_profile=str(
            routing.get("default_curriculum_profile")
            or routing.get("curriculum_profile")
            or "vocational_high_b"
        ),
    )


def _derived_binding_result(
    *,
    skill_id: str,
    ctx: FixedDomainContext,
    required_capabilities: list[str],
    selected_operation: str = "",
) -> DomainResolutionResult:
    provider = DOMAIN_PROVIDERS.get(ctx.fixed_domain_key) or {}
    prov_caps = _provider_capability_set(provider)
    matched = sorted(set(required_capabilities) & prov_caps) if required_capabilities else []
    return DomainResolutionResult(
        skill_id=skill_id,
        fixed_domain_key=ctx.fixed_domain_key,
        resolution_source="derived_capability_match",
        binding_status="derived",
        required_capabilities=tuple(required_capabilities),
        matched_capabilities=tuple(matched),
        selected_operation=selected_operation,
        registry_revision=ctx.registry_revision,
        domain_module=ctx.domain_module,
        entrypoint=ctx.entrypoint,
        allowed_operations=ctx.allowed_operations,
        curriculum_profile=ctx.curriculum_profile,
    )


def resolve_domain_authority(
    skill_id: str,
    *,
    textbook_example: dict[str, Any] | None = None,
    problem_type_id: str | None = None,
    extra: dict[str, Any] | None = None,
    selected_operation: str | None = None,
) -> DomainResolutionResult:
    """Unified domain authority resolver for generation, verify, and publish."""
    key = str(skill_id or "").strip()
    ctx = get_current_component_override_context()
    extra_data = dict(ctx.extra if ctx else {})
    if extra:
        extra_data.update(extra)

    required_capabilities = normalize_capability_list(extra_data.get("required_capabilities"))
    induced_spec = extract_induced_spec_from_extra(extra_data)
    if not required_capabilities and induced_spec:
        required_capabilities = normalize_capability_list(induced_spec.get("required_capabilities"))

    explicit_key = extra_data.get("fixed_domain_key") or extra_data.get("domain_key")
    if explicit_key:
        override_ctx = resolve_dynamic_fixed_domain_context(
            key,
            original_exc=ValueError("component_override_active"),
            textbook_example=textbook_example,
            problem_type_id=problem_type_id,
            extra=extra,
        )
        op = str(
            selected_operation
            or extra_data.get("domain_operation")
            or extra_data.get("selected_operation")
            or problem_type_id
            or ""
        ).strip()
        return DomainResolutionResult(
            skill_id=key,
            fixed_domain_key=override_ctx.fixed_domain_key,
            resolution_source="explicit_override",
            binding_status="override",
            required_capabilities=tuple(required_capabilities),
            matched_capabilities=tuple(required_capabilities),
            selected_operation=op,
            registry_revision=override_ctx.registry_revision,
            domain_module=override_ctx.domain_module,
            entrypoint=override_ctx.entrypoint,
            allowed_operations=override_ctx.allowed_operations,
            curriculum_profile=override_ctx.curriculum_profile,
        )

    confirmed = get_confirmed_skill_binding(key)
    if confirmed:
        fixed_domain_key = get_fixed_domain_key(key)
        allowed = tuple(get_allowed_operations(fixed_domain_key, skill_id=key))
        provider = DOMAIN_PROVIDERS.get(fixed_domain_key) or {}
        if required_capabilities:
            prov_caps = _provider_capability_set(provider)
            allowed_ops = set(provider.get("allowed_operations") or [])
            missing = sorted(
                cap
                for cap in set(required_capabilities) - prov_caps
                if cap not in allowed_ops
            )
            if missing:
                raise SkillFixedDomainError(
                    DOMAIN_BINDING_CONFLICT,
                    f"DOMAIN_BINDING_CONFLICT: induced capabilities incompatible with confirmed binding for {key}",
                    details={
                        "skill_id": key,
                        "confirmed_domain": fixed_domain_key,
                        "derived_candidate_domain": fixed_domain_key,
                        "required_capabilities": required_capabilities,
                        "missing_capabilities_in_confirmed_domain": missing,
                        "resolution_source": "confirmed_binding",
                    },
                )
        return _confirmed_binding_result(
            skill_id=key,
            routing=confirmed,
            fixed_domain_key=fixed_domain_key,
            allowed=allowed,
            required_capabilities=required_capabilities,
        )

    dynamic_ctx = resolve_dynamic_fixed_domain_context(
        key,
        original_exc=SkillDomainNotRegisteredError(f"skill_domain_not_registered: {key!r}"),
        textbook_example=textbook_example,
        problem_type_id=problem_type_id,
        extra=extra,
    )
    op = str(
        selected_operation
        or extra_data.get("domain_operation")
        or extra_data.get("selected_operation")
        or problem_type_id
        or ""
    ).strip()
    return _derived_binding_result(
        skill_id=key,
        ctx=dynamic_ctx,
        required_capabilities=required_capabilities,
        selected_operation=op,
    )


def _append_unique(target: list[str], value: str) -> None:
    value = str(value or "").strip()
    if value and value not in target:
        target.append(value)


def normalize_capability_list(raw: Any) -> list[str]:
    """Normalize capability names to a deduplicated ordered string list."""
    if raw is None:
        return []
    if isinstance(raw, str):
        items = [raw]
    elif isinstance(raw, (list, tuple, set, frozenset)):
        items = list(raw)
    else:
        return []
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if not isinstance(item, str):
            continue
        cap = item.strip()
        if not cap or cap in seen:
            continue
        seen.add(cap)
        ordered.append(cap)
    return ordered


def extract_induced_spec_from_extra(extra_data: dict[str, Any] | None) -> dict[str, Any]:
    """Return induced spec dict embedded in resolver extra payload."""
    if not isinstance(extra_data, dict):
        return {}
    induced = extra_data.get("v3_induced_spec")
    if isinstance(induced, dict) and induced:
        return dict(induced)
    phase1 = extra_data.get("phase1_classification")
    if isinstance(phase1, dict) and phase1:
        return dict(phase1)
    return {}


def normalize_induced_spec_to_resolver_constraints(
    induced_spec: dict[str, Any] | None,
) -> dict[str, Any]:
    """Normalize Phase 1 induced spec into resolver-facing constraints."""
    if not isinstance(induced_spec, dict) or not induced_spec:
        return {}
    answer_contract = induced_spec.get("answer_contract")
    if not isinstance(answer_contract, dict):
        answer_contract = {}
    source_example_id = induced_spec.get("source_example_id")
    if source_example_id is None:
        source_example_id = induced_spec.get("textbook_example_id")
    normalized: dict[str, Any] = {
        "v3_induced_spec": dict(induced_spec),
        "phase1_classification": dict(induced_spec),
        "problem_type_id": str(induced_spec.get("problem_type_id") or "").strip(),
        "required_capabilities": normalize_capability_list(induced_spec.get("required_capabilities")),
        "classification_source": str(induced_spec.get("classification_source") or "").strip(),
        "source_hash": str(induced_spec.get("source_hash") or "").strip(),
        "presentation_mode": str(induced_spec.get("presentation_mode") or "").strip(),
        "answer_contract": dict(answer_contract),
    }
    if source_example_id is not None and str(source_example_id).strip() != "":
        try:
            normalized["source_example_id"] = int(source_example_id)
        except (TypeError, ValueError):
            pass
    if answer_contract.get("answer_type"):
        normalized["answer_type"] = str(answer_contract.get("answer_type") or "").strip()
    return normalized


def merge_resolver_extra_with_induced_constraints(
    extra: dict[str, Any] | None,
    induced_spec: dict[str, Any] | None,
) -> dict[str, Any]:
    """Merge normalized induced spec into resolver extra without textbook overrides."""
    merged = dict(extra or {})
    normalized = normalize_induced_spec_to_resolver_constraints(induced_spec)
    if not normalized:
        return merged
    merged.update(normalized)
    return merged


def _provider_capability_set(provider: dict[str, Any]) -> set[str]:
    return set(normalize_capability_list(provider.get("capabilities")))


def _compute_provider_coverage(
    required: set[str],
    provider_key: str,
    provider: dict[str, Any],
    *,
    problem_type_id: str,
) -> dict[str, Any]:
    prov_caps = _provider_capability_set(provider)
    matched = sorted(required & prov_caps)
    missing = sorted(required - prov_caps)
    coverage_ratio = (len(matched) / len(required)) if required else 0.0
    operation_match = bool(
        problem_type_id and problem_type_id in set(provider.get("allowed_operations") or ())
    )
    return {
        "domain_key": provider_key,
        "matched_capabilities": matched,
        "missing_capabilities": missing,
        "coverage_ratio": round(coverage_ratio, 6),
        "operation_match": operation_match,
        "capability_count": len(prov_caps),
    }


def _select_provider_by_capability_coverage(
    *,
    required: set[str],
    problem_type_id: str,
    providers: dict[str, dict[str, Any]],
) -> tuple[str | None, list[dict[str, Any]], dict[str, Any]]:
    """Return (selected_provider_key, candidate_providers, selection_meta)."""
    if "interquartile_range" in required:
        return None, [], {
            "reason": "unresolved_capability",
            "best_provider": None,
            "matched_capabilities": [],
            "missing_capabilities": sorted(required),
        }
    candidates = [
        _compute_provider_coverage(required, key, prov, problem_type_id=problem_type_id)
        for key, prov in providers.items()
    ]
    full_candidates = [c for c in candidates if c["missing_capabilities"] == [] and c["matched_capabilities"]]
    if full_candidates:
        op_exact = [c for c in full_candidates if c["operation_match"]]
        pool = op_exact or full_candidates
        pool.sort(
            key=lambda c: (
                -len(c["matched_capabilities"]),
                c["capability_count"],
                c["domain_key"],
            )
        )
        best = pool[0]
        tied = [
            c for c in pool
            if len(c["matched_capabilities"]) == len(best["matched_capabilities"])
            and c["capability_count"] == best["capability_count"]
            and c["operation_match"] == best["operation_match"]
        ]
        if len(tied) > 1:
            return None, candidates, {
                "reason": "ambiguous_provider_match",
                "best_provider": None,
                "ambiguous_providers": [c["domain_key"] for c in tied],
            }
        return best["domain_key"], candidates, {
            "reason": "full_capability_coverage",
            "best_provider": best["domain_key"],
            "matched_capabilities": best["matched_capabilities"],
            "missing_capabilities": [],
        }

    partial_candidates = [c for c in candidates if c["matched_capabilities"]]
    if partial_candidates:
        partial_candidates.sort(key=lambda c: (-c["coverage_ratio"], -len(c["matched_capabilities"]), c["domain_key"]))
        best = partial_candidates[0]
        return None, candidates, {
            "reason": "partial_capability_coverage",
            "best_provider": best["domain_key"],
            "matched_capabilities": best["matched_capabilities"],
            "missing_capabilities": best["missing_capabilities"],
        }

    return None, candidates, {
        "reason": "no_provider_capability_match",
        "best_provider": None,
        "matched_capabilities": [],
        "missing_capabilities": sorted(required),
    }


def _build_resolver_trace_details(
    *,
    skill_id: str,
    component_id: str,
    problem_type_id: str,
    classification_source: str,
    required_capabilities: list[str],
    resolution_source: str,
    candidate_providers: list[dict[str, Any]],
    resolver_path: list[str],
    fallback_attempts: list[str],
    original_exc: Exception | None = None,
    selection_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    details: dict[str, Any] = {
        "skill_id": skill_id,
        "component_id": component_id,
        "resolution_source": resolution_source,
        "problem_type_id": problem_type_id,
        "required_capabilities": list(required_capabilities),
        "classification_source": classification_source,
        "candidate_providers": candidate_providers,
        "resolver_path": resolver_path,
        "fallback_attempts": fallback_attempts,
    }
    if selection_meta:
        details.update(
            {
                "best_provider": selection_meta.get("best_provider"),
                "matched_capabilities": list(selection_meta.get("matched_capabilities") or []),
                "missing_capabilities": list(selection_meta.get("missing_capabilities") or []),
                "reason": selection_meta.get("reason") or "",
            }
        )
        if selection_meta.get("ambiguous_providers"):
            details["ambiguous_providers"] = list(selection_meta.get("ambiguous_providers") or [])
    if original_exc is not None:
        details["inference_trace"] = {
            "original_error": f"{original_exc.__class__.__name__}:{original_exc}",
        }
    return details


def _text_capability_hints(text: str) -> set[str]:
    normalized = str(text or "").lower()
    caps: set[str] = set()
    if any(token in normalized for token in ("histogram", "frequency polygon", "frequency distribution")):
        caps.update({"frequency_table", "histogram", "frequency_polygon", "frequency_distribution"})
    if any(token in normalized for token in ("cumulative", "累積", "累積次數")):
        caps.update({
            "cumulative_frequency_table",
            "cumulative_frequency_graph",
            "less_than_cumulative",
            "greater_than_cumulative",
            "class_frequency_from_cumulative",
            "cumulative_monotonicity",
        })
    if any(token in normalized for token in ("table", "chart", "bar chart", "line chart", "pie chart")) and any(
        token in normalized for token in ("read", "value", "compare", "difference", "total", "ratio", "percent", "percentage", "statement", "largest", "smallest")
    ):
        caps.update({"statistical_chart_reading", "table_chart"})
    if any(token in normalized for token in ("point to line", "distance from point", "distance to line")):
        caps.update({"distance_from_point_to_line", "compare_point_to_line_distances"})
    if any(token in normalized for token in ("parallel line distance", "distance between parallel", "parallel lines")):
        caps.update({"distance_between_parallel_lines", "parallel_lines_distance"})
    if any(token in normalized for token in ("line equation", "slope", "point-slope", "intercept", "horizontal line", "vertical line")):
        caps.update({"slope", "line_equation"})
    return caps


def resolve_dynamic_fixed_domain_context(
    skill_id: str,
    original_exc: Exception,
    *,
    textbook_example: dict[str, Any] | None = None,
    problem_type_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> FixedDomainContext:
    resolver_path: list[str] = []
    fallback_attempts: list[str] = []

    ctx = get_current_component_override_context()
    component_id = ctx.component_id if ctx else ""
    extra_data = dict(ctx.extra if ctx else {})
    if extra:
        extra_data.update(extra)

    induced_spec = extract_induced_spec_from_extra(extra_data)
    induced_problem_type_id = str(
        extra_data.get("problem_type_id")
        or induced_spec.get("problem_type_id")
        or ""
    ).strip()
    if induced_problem_type_id.lower() in {"", "none"}:
        induced_problem_type_id = ""
    classification_source = str(
        extra_data.get("classification_source")
        or induced_spec.get("classification_source")
        or ""
    ).strip()

    explicit_key = extra_data.get("fixed_domain_key") or extra_data.get("domain_key")
    if explicit_key:
        resolver_path.append("component_override")
        fallback_attempts.append(f"try override key {explicit_key}")
        if explicit_key in DOMAIN_PROVIDERS:
            prov = DOMAIN_PROVIDERS[explicit_key]
            allowed_ops = tuple(extra_data.get("allowed_operations") or prov["allowed_operations"])
            log_dispatch_event(
                phase="domain_resolution",
                skill_id=skill_id,
                component_id=component_id,
                fixed_domain_key=explicit_key,
                problem_type_id=induced_problem_type_id,
                extra={
                    "resolution_source": "component_override",
                    "required_capabilities": normalize_capability_list(extra_data.get("required_capabilities")),
                    "classification_source": classification_source,
                },
            )
            return FixedDomainContext(
                skill_id=skill_id,
                fixed_domain_key=explicit_key,
                allowed_operations=allowed_ops,
                registry_revision="2026-06-23-v1.8",
                domain_module=str(extra_data.get("domain_module") or prov["domain_module"]),
                entrypoint=str(extra_data.get("entrypoint") or prov["entrypoint"]),
                curriculum_profile=str(extra_data.get("curriculum_profile") or "vocational_high_b"),
            )
        raise SkillFixedDomainError(
            DOMAIN_OVERRIDE_NOT_FOUND,
            f"component_override_domain_not_found: {explicit_key}",
            details=_build_resolver_trace_details(
                skill_id=skill_id,
                component_id=component_id,
                problem_type_id=induced_problem_type_id,
                classification_source=classification_source,
                required_capabilities=normalize_capability_list(extra_data.get("required_capabilities")),
                resolution_source="component_override",
                candidate_providers=[],
                resolver_path=resolver_path,
                fallback_attempts=fallback_attempts,
            ),
        )

    required_caps: set[str] = set()
    domain_families: set[str] = set()
    problem_types: set[str] = set()

    induced_caps = normalize_capability_list(extra_data.get("required_capabilities"))
    if not induced_caps and induced_spec:
        induced_caps = normalize_capability_list(induced_spec.get("required_capabilities"))
    if induced_caps:
        resolver_path.append("induced_spec_capabilities")
        required_caps.update(induced_caps)
        fallback_attempts.append(f"induced_capabilities={sorted(induced_caps)}")

    for key in ("problem_type_id", "domain_operation", "selected_operation", "line_type", "task_type"):
        value = str(extra_data.get(key) or "").strip()
        if value:
            problem_types.add(value)
            fallback_attempts.append(f"component_metadata:{key}={value}")
    if induced_problem_type_id:
        problem_types.add(induced_problem_type_id)
    elif problem_type_id:
        problem_types.add(str(problem_type_id).strip())
        fallback_attempts.append(f"problem_type_id={problem_type_id}")

    examples: list[dict[str, Any]] = []
    if isinstance(textbook_example, dict) and textbook_example:
        resolver_path.append("component_textbook_example")
        examples = [dict(textbook_example)]
    else:
        try:
            db_path = PROJECT_ROOT / "instance/kumon_math.db"
            if db_path.is_file():
                with sqlite3.connect(str(db_path)) as db_conn:
                    db_conn.row_factory = sqlite3.Row
                    rows = db_conn.execute(
                        "SELECT id, problem_text, correct_answer, detailed_solution, explanation, problem_type FROM textbook_examples WHERE skill_id = ? ORDER BY id ASC",
                        (skill_id,),
                    ).fetchall()
                    examples = [dict(r) for r in rows]
                    if examples:
                        resolver_path.append("skill_examples_from_db")
        except Exception as e:
            fallback_attempts.append(f"db_load_failed: {e}")

    for ex in examples:
        text = (
            str(ex.get("problem_text") or "") + " "
            + str(ex.get("correct_answer") or "") + " "
            + str(ex.get("detailed_solution") or "") + " "
            + str(ex.get("explanation") or "")
        ).lower()

        if not induced_problem_type_id:
            pt = str(ex.get("problem_type") or "").strip()
            if pt:
                problem_types.add(pt)
        pt2 = str(
            ex.get("problem_type_id")
            or ex.get("domain_operation")
            or ex.get("line_type")
            or ex.get("task_type")
            or ""
        ).strip()
        if pt2 and not induced_problem_type_id:
            problem_types.add(pt2)

        hinted_caps = _text_capability_hints(text)
        if hinted_caps:
            _append_unique(resolver_path, "text_answer_capability_inference")
            required_caps.update(hinted_caps)

        if any(kw in text for kw in ["直方圖", "折線圖", "次數分配", "組距", "組中點", "次數", "histogram", "polygon", "frequency"]):
            domain_families.add("statistics_chart")
            required_caps.update([
                "frequency_table",
                "class_interval",
                "class_boundary",
                "class_midpoint",
                "histogram",
                "frequency_polygon",
                "chart_consistency_validation",
            ])
        elif any(kw in text for kw in ["平行線", "兩平行線", "平行線的距離", "平行線之距離", "parallel line"]):
            domain_families.add("coordinate_geometry")
            required_caps.update(["distance_between_parallel_lines", "parallel_lines_distance", "solve_parameter_from_parallel_distance"])
        elif any(kw in text for kw in ["點到直線", "距離", "point to line", "distance"]):
            domain_families.add("coordinate_geometry")
            required_caps.update(["distance_from_point_to_line", "compare_point_to_line_distances"])
        elif any(kw in text for kw in ["直線方程式", "斜率", "點斜式", "截距式", "一般式", "垂直平分線", "line equation", "slope"]):
            domain_families.add("coordinate_geometry")
            required_caps.update(["slope", "line_equation", "horizontal_line", "vertical_line", "point_slope", "intercept_form", "general_form", "two_points"])

    if not required_caps:
        fallback_attempts.append("narrow_skill_name_inference")
        skill_lower = skill_id.lower()
        if "histogram" in skill_lower or "polygon" in skill_lower or "frequency" in skill_lower:
            domain_families.add("statistics_chart")
            required_caps.update(["frequency_table", "histogram", "frequency_polygon"])
        if "cumulative" in skill_lower:
            domain_families.add("statistics_chart")
            required_caps.update([
                "cumulative_frequency_table",
                "cumulative_frequency_graph",
                "less_than_cumulative",
                "greater_than_cumulative",
                "class_frequency_from_cumulative",
            ])
        elif "chartreading" in skill_lower or "chart_reading" in skill_lower or "tablechart" in skill_lower:
            domain_families.add("statistics_table_chart")
            required_caps.update(["statistical_chart_reading", "table_chart"])
        elif "parallel" in skill_lower and "distance" in skill_lower:
            domain_families.add("coordinate_geometry")
            required_caps.update(["distance_between_parallel_lines", "parallel_lines_distance"])
        elif "distance" in skill_lower:
            domain_families.add("coordinate_geometry")
            required_caps.update(["distance_from_point_to_line"])
        elif "slope" in skill_lower or "line" in skill_lower or "equation" in skill_lower:
            domain_families.add("coordinate_geometry")
            required_caps.update(["slope", "line_equation"])

    required_capabilities = normalize_capability_list(sorted(required_caps))
    resolved_problem_type_id = induced_problem_type_id or str(problem_type_id or "").strip()
    if not resolved_problem_type_id and problem_types:
        resolved_problem_type_id = sorted(problem_types)[0]

    if not required_capabilities:
        raise SkillFixedDomainError(
            DOMAIN_CAPABILITY_UNRESOLVED,
            f"DOMAIN_CAPABILITY_UNRESOLVED: no_required_capabilities for skill {skill_id}",
            details=_build_resolver_trace_details(
                skill_id=skill_id,
                component_id=component_id,
                problem_type_id=resolved_problem_type_id,
                classification_source=classification_source,
                required_capabilities=[],
                resolution_source="dynamic_capability_match",
                candidate_providers=[],
                resolver_path=resolver_path,
                fallback_attempts=fallback_attempts,
                original_exc=original_exc,
                selection_meta={"reason": "no_required_capabilities"},
            ),
        )

    selected_key, candidate_providers, selection_meta = _select_provider_by_capability_coverage(
        required=set(required_capabilities),
        problem_type_id=resolved_problem_type_id,
        providers=get_domain_providers_for_resolution(),
    )

    if selected_key:
        _append_unique(resolver_path, "capability_coverage_full_match")
        prov = get_domain_providers_for_resolution()[selected_key]
        log_dispatch_event(
            phase="domain_resolution",
            skill_id=skill_id,
            component_id=component_id,
            fixed_domain_key=selected_key,
            problem_type_id=resolved_problem_type_id,
            extra={
                "resolution_source": "dynamic_capability_match",
                "required_capabilities": required_capabilities,
                "classification_source": classification_source,
                "candidate_providers": candidate_providers,
            },
        )
        return FixedDomainContext(
            skill_id=skill_id,
            fixed_domain_key=selected_key,
            allowed_operations=tuple(prov["allowed_operations"]),
            registry_revision="2026-06-23-v1.8",
            domain_module=prov["domain_module"],
            entrypoint=prov["entrypoint"],
            curriculum_profile="vocational_high_b",
        )

    reason = str(selection_meta.get("reason") or "")
    if reason == "ambiguous_provider_match":
        error_code = DOMAIN_CAPABILITY_AMBIGUOUS
        message = f"DOMAIN_CAPABILITY_AMBIGUOUS: ambiguous provider match for skill {skill_id}"
    elif reason == "partial_capability_coverage":
        error_code = DOMAIN_CAPABILITY_PARTIAL
        message = f"DOMAIN_CAPABILITY_PARTIAL: partial capability coverage for skill {skill_id}"
    else:
        error_code = DOMAIN_CAPABILITY_UNRESOLVED
        message = f"DOMAIN_CAPABILITY_UNRESOLVED: cannot resolve domain for skill {skill_id}"

    trace_details = _build_resolver_trace_details(
        skill_id=skill_id,
        component_id=component_id,
        problem_type_id=resolved_problem_type_id,
        classification_source=classification_source,
        required_capabilities=required_capabilities,
        resolution_source="dynamic_capability_match",
        candidate_providers=candidate_providers,
        resolver_path=resolver_path,
        fallback_attempts=fallback_attempts,
        original_exc=original_exc,
        selection_meta=selection_meta,
    )
    trace_details["inference_trace"] = {
        "layers": [
            "induced_spec_capabilities",
            "component_metadata",
            "text_answer_capability_inference",
            "narrow_domain_fallback",
            "capability_coverage_matching",
        ],
        "problem_types": sorted(problem_types),
        "domain_families": sorted(domain_families),
        "original_error": f"{original_exc.__class__.__name__}:{original_exc}",
    }
    raise SkillFixedDomainError(error_code, message, details=trace_details)


def resolve_fixed_domain_context(
    skill_id: str,
    *,
    textbook_example: dict[str, Any] | None = None,
    problem_type_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> FixedDomainContext:
    """Resolve authoritative fixed-domain context for a skill."""
    key = str(skill_id or "").strip()
    extra_data = dict(get_current_component_override_context().extra if get_current_component_override_context() else {})
    if extra:
        extra_data.update(extra)

    metadata_operation = str(
        extra_data.get("domain_operation")
        or extra_data.get("selected_operation")
        or extra_data.get("problem_type_id")
        or extra_data.get("line_type")
        or extra_data.get("task_type")
        or problem_type_id
        or ""
    ).strip()
    if metadata_operation and not get_confirmed_skill_binding(key):
        metadata_matches_known_operation = any(
            metadata_operation in tuple(provider.get("allowed_operations") or ())
            for provider in DOMAIN_PROVIDERS.values()
        )
        if metadata_matches_known_operation:
            try:
                return resolve_dynamic_fixed_domain_context(
                    key,
                    original_exc=ValueError("component_metadata_active"),
                    textbook_example=textbook_example,
                    problem_type_id=problem_type_id,
                    extra=extra,
                )
            except SkillFixedDomainError:
                pass

    result = resolve_domain_authority(
        key,
        textbook_example=textbook_example,
        problem_type_id=problem_type_id,
        extra=extra,
        selected_operation=metadata_operation or None,
    )
    log_dispatch_event(
        phase="domain_resolution",
        skill_id=key,
        fixed_domain_key=result.fixed_domain_key,
        extra={
            "resolution_source": result.resolution_source,
            "binding_status": result.binding_status,
            "required_capabilities": list(result.required_capabilities),
        },
    )
    return result.to_fixed_domain_context()



def strip_ai_routing_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove AI-suggested routing fields that must not influence dispatch."""
    cleaned = dict(payload or {})
    for field in AI_IGNORED_ROUTING_FIELDS:
        cleaned.pop(field, None)
    return cleaned


def assert_operation_allowed(
    *,
    skill_id: str,
    fixed_domain_key: str,
    selected_operation: str,
    allowed_operations: list[str] | tuple[str, ...] | None = None,
) -> str:
    """Hard gate: selected_operation must be in allowed_operations whitelist."""
    op = str(selected_operation or "").strip()
    if not op:
        raise SkillFixedDomainError(
            DOMAIN_OPERATION_NOT_ALLOWED,
            "domain_operation_not_allowed: empty operation",
            details={
                "skill_id": skill_id,
                "fixed_domain_key": fixed_domain_key,
                "selected_operation": op,
            },
        )

    whitelist = tuple(allowed_operations or get_allowed_operations(fixed_domain_key, skill_id=skill_id))
    if op not in whitelist:
        raise SkillFixedDomainError(
            DOMAIN_OPERATION_NOT_ALLOWED,
            f"domain_operation_not_allowed: {op!r} not in {list(whitelist)!r}",
            details={
                "skill_id": skill_id,
                "fixed_domain_key": fixed_domain_key,
                "selected_operation": op,
                "allowed_operations": list(whitelist),
            },
        )
    return op


def assert_template_dispatch(
    *,
    skill_id: str,
    fixed_domain_key: str,
    template_domain_key: str,
    template_operation_key: str,
    allowed_operations: list[str] | tuple[str, ...] | None = None,
) -> None:
    """Validate template slot domain/operation before dispatch."""
    if str(template_domain_key or "").strip() != str(fixed_domain_key or "").strip():
        raise SkillFixedDomainError(
            FIXED_DOMAIN_VIOLATION,
            f"fixed_domain_violation: template domain {template_domain_key!r} != {fixed_domain_key!r}",
            details={
                "skill_id": skill_id,
                "fixed_domain_key": fixed_domain_key,
                "template_domain_key": template_domain_key,
                "template_operation_key": template_operation_key,
            },
        )
    assert_operation_allowed(
        skill_id=skill_id,
        fixed_domain_key=fixed_domain_key,
        selected_operation=template_operation_key,
        allowed_operations=allowed_operations,
    )


def build_classifier_taxonomy_entry(ctx: FixedDomainContext) -> dict[str, Any]:
    """Taxonomy entry passed to semantic classifier — AI cannot override domain."""
    return {
        "skill_id": ctx.skill_id,
        "fixed_domain_key": ctx.fixed_domain_key,
        "allowed_operations": list(ctx.allowed_operations),
        "allowed_types": list(ctx.allowed_operations),
        "registry_revision": ctx.registry_revision,
    }


def normalize_ai_classification(
    classification: dict[str, Any],
    ctx: FixedDomainContext,
) -> dict[str, Any]:
    """Normalize AI/deterministic classification output under fixed domain authority."""
    cleaned = strip_ai_routing_fields(classification)
    selected = str(
        cleaned.get("selected_operation")
        or cleaned.get("domain_operation")
        or cleaned.get("problem_type_id")
        or ""
    ).strip()
    if selected:
        assert_operation_allowed(
            skill_id=ctx.skill_id,
            fixed_domain_key=ctx.fixed_domain_key,
            selected_operation=selected,
            allowed_operations=ctx.allowed_operations,
        )
    normalized = {
        **cleaned,
        "skill_id": ctx.skill_id,
        "fixed_domain_key": ctx.fixed_domain_key,
        "registry_revision": ctx.registry_revision,
        "selected_operation": selected or cleaned.get("selected_operation"),
        "domain_operation": selected or cleaned.get("domain_operation"),
    }
    if selected and not normalized.get("problem_type_id"):
        normalized["problem_type_id"] = selected
    return normalized


def log_dispatch_event(
    *,
    phase: str,
    skill_id: str,
    component_id: str = "",
    example_id: int | None = None,
    fixed_domain_key: str = "",
    selected_operation: str = "",
    problem_type_id: str = "",
    template_slot: str = "",
    template_domain_key: str = "",
    seed: int | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Structured dispatch log — required fields for audit trail."""
    record = {
        "phase": str(phase or "").strip(),
        "skill_id": str(skill_id or "").strip(),
        "component_id": str(component_id or "").strip(),
        "example_id": example_id,
        "fixed_domain_key": str(fixed_domain_key or "").strip(),
        "selected_operation": str(selected_operation or "").strip(),
        "problem_type_id": str(problem_type_id or "").strip(),
        "template_slot": str(template_slot or "").strip(),
        "template_domain_key": str(template_domain_key or "").strip(),
        "seed": seed,
    }
    if extra:
        record.update(extra)
    logger.info("[GENCODE_DISPATCH] %s", json.dumps(record, ensure_ascii=False, default=str))


def validate_publish_component_record(
    *,
    skill_id: str,
    component_skill_id: str,
    component_fixed_domain_key: str,
    component_operation: str,
    component_status: str,
    registry_skill_id: str | None = None,
    spec: dict[str, Any] | None = None,
) -> list[str]:
    """Return publish blockers for a single component; empty means eligible."""
    blockers: list[str] = []
    skill_key = str(skill_id or "").strip()
    if str(component_skill_id or "").strip() != skill_key:
        blockers.append("publish_skill_id_mismatch")

    status = str(component_status or "").strip()
    if status != "verified":
        blockers.append("component_not_verified")
        return blockers

    evidence_spec = dict(spec or {})
    if not evidence_spec:
        evidence_spec = {
            "fixed_domain_key": component_fixed_domain_key,
            "domain_operation": component_operation,
            "problem_type_id": component_operation,
        }

    confirmed = get_confirmed_skill_binding(skill_key)
    if confirmed:
        if not str(evidence_spec.get("fixed_domain_key") or component_fixed_domain_key or "").strip():
            evidence_spec["fixed_domain_key"] = str(confirmed.get("fixed_domain_key") or "").strip()
        evidence_spec.setdefault("domain_module", confirmed.get("domain_module"))
        evidence_spec.setdefault("entrypoint", confirmed.get("entrypoint"))
        evidence_spec.setdefault("binding_status", "confirmed")
        evidence_spec.setdefault("resolution_source", "confirmed_binding")
        confirmed_key = str(confirmed.get("fixed_domain_key") or "").strip()
        component_key = str(
            evidence_spec.get("fixed_domain_key") or component_fixed_domain_key or ""
        ).strip()
        if component_key and confirmed_key and component_key != confirmed_key:
            blockers.append(FIXED_DOMAIN_VIOLATION)
    elif not str(evidence_spec.get("resolution_source") or "").strip():
        blockers.append(f"{DOMAIN_EVIDENCE_INCOMPLETE}:resolution_source")

    blockers.extend(validate_component_domain_evidence(evidence_spec))

    from core.gencode.choice_contract_validator import choice_contract_valid_from_spec
    from core.gencode.v3_error_codes import CHOICE_CONTRACT_INCOMPLETE

    if not choice_contract_valid_from_spec(evidence_spec):
        blockers.append(CHOICE_CONTRACT_INCOMPLETE)

    if status in {
        UNSUPPORTED_DOMAIN_OPERATION,
        FIXED_DOMAIN_VIOLATION,
        DOMAIN_OPERATION_NOT_ALLOWED,
        "needs_human_review",
    }:
        blockers.append(f"non_publishable_status:{status}")

    return blockers


