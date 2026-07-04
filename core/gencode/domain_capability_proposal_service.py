"""Review-only proposals for unresolved V3 domain capabilities."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from core.registry.domain_operation_registry import (
    get_domain_spec,
    list_registered_domains,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROPOSAL_ROOT = PROJECT_ROOT / "reports" / "domain_capability_proposals"

_NOISE_TOKENS = frozenset(
    {"compute", "derive", "find", "read", "solve", "calculate", "from", "and", "of"}
)


def _tokens(value: str) -> set[str]:
    aliases = {
        "linear": "line",
        "lines": "line",
        "intercepts": "intercept",
        "graphs": "graph",
        "equations": "equation",
        "coordinates": "coordinate",
    }
    tokens: set[str] = set()
    for token in re.findall(r"[a-z0-9]+", str(value or "").lower()):
        normalized = aliases.get(token, token)
        if normalized and normalized not in _NOISE_TOKENS:
            tokens.add(normalized)
    return tokens


def _proposal_root(root: str | Path | None = None) -> Path:
    configured = str(os.environ.get("DOMAIN_CAPABILITY_PROPOSAL_ROOT") or "").strip()
    return Path(root or configured or DEFAULT_PROPOSAL_ROOT)


def _domain_candidates(required_capabilities: list[str], missing_operation: str) -> list[dict[str, Any]]:
    required_tokens = set().union(*(_tokens(value) for value in required_capabilities))
    operation_tokens = _tokens(missing_operation)
    target_tokens = required_tokens | operation_tokens
    candidates: list[dict[str, Any]] = []

    for domain_key in list_registered_domains():
        spec = get_domain_spec(domain_key)
        if spec is None:
            continue
        capability_aliases = sorted(set(required_capabilities) & set(spec.capabilities))
        reusable_operations: list[str] = []
        best_operation_score = 0.0
        for operation_key, operation_spec in spec.operations.items():
            operation_capabilities = set(operation_spec.provided_capabilities)
            operation_tokens_set = _tokens(operation_key)
            for capability in operation_capabilities:
                operation_tokens_set.update(_tokens(capability))
            overlap = target_tokens & operation_tokens_set
            score = len(overlap) / max(1, len(target_tokens))
            if score > 0:
                reusable_operations.append(operation_key)
                best_operation_score = max(best_operation_score, score)

        domain_tokens = _tokens(domain_key)
        domain_overlap_score = len(target_tokens & domain_tokens) / max(1, len(target_tokens))
        score = max(
            1.0 if capability_aliases else 0.0,
            best_operation_score,
            domain_overlap_score,
        )
        if capability_aliases:
            reuse_mode = "capability_alias"
        elif reusable_operations and best_operation_score >= 0.75:
            reuse_mode = "existing_operation_wrapper"
        elif score > 0:
            reuse_mode = "new_generic_operation"
        else:
            continue
        candidates.append(
            {
                "domain_key": domain_key,
                "score": round(score, 6),
                "reuse_mode": reuse_mode,
                "capability_aliases": capability_aliases,
                "reusable_operations": sorted(set(reusable_operations)),
                "domain_module": spec.domain_module,
                "entrypoint": spec.entrypoint,
            }
        )

    return sorted(
        candidates,
        key=lambda item: (
            -float(item["score"]),
            {"capability_alias": 0, "existing_operation_wrapper": 1, "new_generic_operation": 2}.get(
                str(item["reuse_mode"]), 3
            ),
            str(item["domain_key"]),
        ),
    )


def _fingerprint(required_capabilities: list[str], missing_operation: str) -> str:
    canonical = {
        "required_capabilities": sorted(set(required_capabilities)),
        "missing_operation": str(missing_operation or "").strip(),
    }
    digest = hashlib.sha256(json.dumps(canonical, sort_keys=True).encode("utf-8")).hexdigest()
    return digest[:24]


def _merge_unique(existing: list[Any], incoming: list[Any]) -> list[Any]:
    merged: list[Any] = []
    for item in [*existing, *incoming]:
        if item not in merged:
            merged.append(item)
    return merged


def create_or_reuse_capability_proposal(
    *,
    skill_id: str,
    component_id: str,
    problem_type_id: str,
    required_capabilities: list[str],
    source_example_ids: list[int],
    proposal_root: str | Path | None = None,
) -> dict[str, Any]:
    """Persist one proposed capability artifact without mutating runtime registries."""
    capabilities = [
        str(value).strip()
        for value in required_capabilities
        if str(value or "").strip()
    ]
    missing_operation = str(problem_type_id or (capabilities[0] if capabilities else "")).strip()
    fingerprint = _fingerprint(capabilities, missing_operation)
    proposal_id = f"capability_{fingerprint}"
    root = _proposal_root(proposal_root)
    path = root / f"{proposal_id}.json"
    candidates = _domain_candidates(capabilities, missing_operation)
    best_reuse_domain = candidates[0]["domain_key"] if candidates else None
    recommendation = (
        candidates[0]["reuse_mode"] if candidates else "new_domain"
    )
    proposal: dict[str, Any] = {
        "proposal_schema": "domain_capability_proposal.v1",
        "proposal_id": proposal_id,
        "skill_id": str(skill_id or "").strip(),
        "component_id": str(component_id or "").strip(),
        "problem_type_id": str(problem_type_id or "").strip(),
        "required_capabilities": sorted(set(capabilities)),
        "candidate_domains": candidates,
        "best_reuse_domain": best_reuse_domain,
        "missing_operation": missing_operation,
        "source_example_ids": sorted(set(int(value) for value in source_example_ids)),
        "reuse_priority": [
            "capability_alias",
            "existing_operation_wrapper",
            "new_generic_operation",
            "new_domain",
        ],
        "recommended_action": recommendation,
        "status": "proposed",
        "production_publish_allowed": False,
        "tracker_status_change": None,
    }

    if path.is_file():
        existing = json.loads(path.read_text(encoding="utf-8"))
        proposal["skill_ids"] = _merge_unique(
            list(existing.get("skill_ids") or [existing.get("skill_id")]),
            [proposal["skill_id"]],
        )
        proposal["component_ids"] = _merge_unique(
            list(existing.get("component_ids") or [existing.get("component_id")]),
            [proposal["component_id"]],
        )
        proposal["source_example_ids"] = sorted(
            set(existing.get("source_example_ids") or []) | set(proposal["source_example_ids"])
        )
    else:
        proposal["skill_ids"] = [proposal["skill_id"]] if proposal["skill_id"] else []
        proposal["component_ids"] = [proposal["component_id"]] if proposal["component_id"] else []

    root.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**proposal, "proposal_path": str(path)}
