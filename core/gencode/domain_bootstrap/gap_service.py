# -*- coding: utf-8 -*-
"""Domain gap detection and aggregation."""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from typing import Any

from core.gencode.domain_bootstrap.candidate_store import CandidateStore
from core.gencode.domain_bootstrap.models import DomainGapReport
from core.gencode.v3_error_codes import (
    DOMAIN_CAPABILITY_PARTIAL,
    DOMAIN_CAPABILITY_UNRESOLVED,
)
from core.registry.domain_operation_registry import list_registered_domains

DOMAIN_GAP_ERROR_CODES = frozenset({DOMAIN_CAPABILITY_PARTIAL, DOMAIN_CAPABILITY_UNRESOLVED})


def _normalize_capabilities(values: Any) -> list[str]:
    if not isinstance(values, (list, tuple, set)):
        return []
    out: list[str] = []
    for value in values:
        token = str(value or "").strip()
        if token and token not in out:
            out.append(token)
    return out


def _gap_fingerprint(
    *,
    missing_capabilities: list[str],
    source_hash: str,
    presentation_modes: list[str],
) -> str:
    payload = {
        "missing_capabilities": sorted(missing_capabilities),
        "source_hash": str(source_hash or "").strip(),
        "presentation_modes": sorted(presentation_modes),
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return digest[:24]


def _nearby_domains(required_capabilities: list[str]) -> list[str]:
    from core.registry.domain_operation_registry import get_domain_spec

    nearby: list[str] = []
    required = set(required_capabilities)
    for domain_key in list_registered_domains():
        spec = get_domain_spec(domain_key)
        if spec is None:
            continue
        overlap = required & set(spec.capabilities)
        if overlap:
            nearby.append(domain_key)
    return sorted(nearby)


def build_gap_report_from_resolver_error(
    *,
    error_code: str,
    error_details: dict[str, Any] | None,
    skill_id: str,
    textbook_example_id: int | None,
    component_id: str | None,
    phase1_spec: dict[str, Any] | None = None,
    source_hash: str = "",
) -> DomainGapReport:
    details = dict(error_details or {})
    phase1 = dict(phase1_spec or {})
    required = _normalize_capabilities(
        details.get("required_capabilities")
        or phase1.get("required_capabilities")
        or []
    )
    matched = _normalize_capabilities(details.get("matched_capabilities") or [])
    missing = sorted(set(required) - set(matched))
    if not missing and required:
        missing = list(required)

    problem_type_id = str(
        details.get("problem_type_id")
        or phase1.get("problem_type_id")
        or ""
    ).strip()
    presentation_mode = str(
        phase1.get("presentation_mode")
        or details.get("presentation_mode")
        or "short_answer"
    ).strip()
    answer_contract = phase1.get("answer_contract")
    contracts: list[dict[str, Any]] = []
    if isinstance(answer_contract, dict):
        contracts.append(dict(answer_contract))

    nearby = _nearby_domains(required)
    suggested_action = "extend_existing_domain" if nearby else "create_new_domain"
    fingerprint = _gap_fingerprint(
        missing_capabilities=missing,
        source_hash=source_hash,
        presentation_modes=[presentation_mode],
    )
    gap_id = f"gap_{fingerprint}"

    return DomainGapReport(
        gap_id=gap_id,
        problem_type_ids=[problem_type_id] if problem_type_id else [],
        required_capabilities=required,
        matched_capabilities=matched,
        missing_capabilities=missing,
        affected_skill_ids=[str(skill_id)] if skill_id else [],
        affected_component_ids=[str(component_id)] if component_id else [],
        source_example_ids=[int(textbook_example_id)] if textbook_example_id else [],
        answer_contracts=contracts,
        presentation_modes=[presentation_mode] if presentation_mode else [],
        source_hashes=[str(source_hash)] if source_hash else [],
        nearby_domains=nearby,
        suggested_action=suggested_action,
        gap_fingerprint=fingerprint,
        error_code=str(error_code or ""),
    )


def merge_gap_report(existing: DomainGapReport, incoming: DomainGapReport) -> DomainGapReport:
    def _merge_list(a: list[Any], b: list[Any]) -> list[Any]:
        out: list[Any] = []
        for item in list(a) + list(b):
            if item not in out:
                out.append(item)
        return out

    return DomainGapReport(
        gap_id=existing.gap_id,
        problem_type_ids=_merge_list(existing.problem_type_ids, incoming.problem_type_ids),
        required_capabilities=_merge_list(existing.required_capabilities, incoming.required_capabilities),
        matched_capabilities=_merge_list(existing.matched_capabilities, incoming.matched_capabilities),
        missing_capabilities=_merge_list(existing.missing_capabilities, incoming.missing_capabilities),
        affected_skill_ids=_merge_list(existing.affected_skill_ids, incoming.affected_skill_ids),
        affected_component_ids=_merge_list(existing.affected_component_ids, incoming.affected_component_ids),
        source_example_ids=_merge_list(existing.source_example_ids, incoming.source_example_ids),
        answer_contracts=_merge_list(existing.answer_contracts, incoming.answer_contracts),
        presentation_modes=_merge_list(existing.presentation_modes, incoming.presentation_modes),
        source_hashes=_merge_list(existing.source_hashes, incoming.source_hashes),
        nearby_domains=_merge_list(existing.nearby_domains, incoming.nearby_domains),
        suggested_action=existing.suggested_action or incoming.suggested_action,
        gap_fingerprint=existing.gap_fingerprint or incoming.gap_fingerprint,
        error_code=existing.error_code or incoming.error_code,
    )


def detect_or_reuse_domain_gap(
    *,
    store: CandidateStore,
    error_code: str,
    error_details: dict[str, Any] | None,
    skill_id: str,
    textbook_example_id: int | None,
    component_id: str | None,
    phase1_spec: dict[str, Any] | None = None,
    source_hash: str = "",
) -> DomainGapReport:
    if error_code not in DOMAIN_GAP_ERROR_CODES:
        raise ValueError(f"not_a_domain_gap_error:{error_code}")

    incoming = build_gap_report_from_resolver_error(
        error_code=error_code,
        error_details=error_details,
        skill_id=skill_id,
        textbook_example_id=textbook_example_id,
        component_id=component_id,
        phase1_spec=phase1_spec,
        source_hash=source_hash,
    )
    existing = store.load_gap_report(incoming.gap_id)
    if existing is not None:
        merged = merge_gap_report(existing, incoming)
        store.save_gap_report(merged)
        return merged
    store.save_gap_report(incoming)
    return incoming


def is_domain_gap_error_code(error_code: str) -> bool:
    return str(error_code or "").strip() in DOMAIN_GAP_ERROR_CODES
