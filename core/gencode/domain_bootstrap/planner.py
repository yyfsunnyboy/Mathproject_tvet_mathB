# -*- coding: utf-8 -*-
"""Bootstrap cost estimation and planning."""

from __future__ import annotations

from typing import Any

from core.gencode.domain_bootstrap.candidate_store import CandidateStore
from core.gencode.domain_bootstrap.models import DomainGapReport


def estimate_bootstrap_cost(
    *,
    gap_report: DomainGapReport,
    store: CandidateStore,
    allow_ai: bool = False,
) -> dict[str, Any]:
    missing = list(gap_report.missing_capabilities or [])
    affected_components = len(gap_report.affected_component_ids or gap_report.source_example_ids or [])
    existing_candidate = store.candidate_dir(gap_report.gap_id).is_dir() and store.candidate_file_exists(
        gap_report.gap_id,
        "domain_manifest.json",
    )
    can_extend = bool(gap_report.nearby_domains) and gap_report.suggested_action == "extend_existing_domain"

    strategy_order = [
        "existing_verified_provider",
        "existing_candidate_reuse" if existing_candidate else None,
        "extend_existing_domain" if can_extend else None,
        "deterministic_scaffold",
        "ai_bootstrap" if allow_ai else None,
    ]
    strategy_order = [step for step in strategy_order if step]

    estimated_ai_calls = 0 if existing_candidate or not allow_ai else 2
    estimated_tokens = 0 if not allow_ai else estimated_ai_calls * 4000

    return {
        "estimated_model": "mock" if not allow_ai else "gemini-3.1-flash-lite-preview",
        "estimated_ai_calls": estimated_ai_calls,
        "estimated_tokens": estimated_tokens,
        "estimated_domains": 0 if existing_candidate else 1,
        "estimated_operations": max(1, len(missing)),
        "affected_components": affected_components,
        "reuse_existing_candidate": existing_candidate,
        "can_extend_existing_domain": can_extend,
        "strategy_order": strategy_order,
        "requires_explicit_ai_authorization": estimated_ai_calls > 0,
        "allow_ai": bool(allow_ai),
    }
