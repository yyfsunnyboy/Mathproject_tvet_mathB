# -*- coding: utf-8 -*-
"""Domain healer — localized candidate patches with bounded retries."""

from __future__ import annotations

import json
from typing import Any, Protocol

from core.gencode.domain_bootstrap.candidate_store import CandidateStore
from core.gencode.domain_bootstrap.models import MAX_HEALER_ROUNDS
from core.gencode.domain_bootstrap.validation_runner import validate_candidate_domain
from core.gencode.domain_bootstrap.models import DomainGapReport


class BootstrapAIClient(Protocol):
    def generate_scaffold_patch(
        self,
        *,
        gap_id: str,
        failure_report: dict[str, Any],
    ) -> dict[str, Any]:
        ...


class MockBootstrapAIClient:
    """Deterministic mock AI — never calls external models."""

    calls: int = 0
    tokens_used: int = 0

    def generate_scaffold_patch(
        self,
        *,
        gap_id: str,
        failure_report: dict[str, Any],
    ) -> dict[str, Any]:
        type(self).calls += 1
        type(self).tokens_used += 0
        blockers = list(failure_report.get("blockers") or [])
        if any("oracle_intentionally_broken" in str(b) for b in blockers):
            return {
                "patch_target": "oracle.py",
                "replacement": '''# -*- coding: utf-8 -*-
"""Independent mathematical oracle — must not import domain_module."""

from __future__ import annotations

from typing import Any

ORACLE_MODE = "valid"


def oracle_verify_matrix(matrix: dict[str, Any]) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    values = ((matrix.get("givens") or {}).get("values") or [])
    if not values:
        blockers.append("oracle_missing_values")
    try:
        expected = sum(int(v) for v in values)
    except Exception:
        blockers.append("oracle_invalid_values")
        return False, blockers
    answer = matrix.get("answer")
    if answer != expected:
        blockers.append("oracle_answer_mismatch")
    return len(blockers) == 0, blockers
''',
            }
        if any("unhealable" in str(b) for b in blockers):
            return {"patch_target": "", "replacement": ""}
        return {"patch_target": "", "replacement": ""}


def apply_healer_patch(store: CandidateStore, gap_id: str, patch: dict[str, Any]) -> bool:
    target = str(patch.get("patch_target") or "").strip()
    replacement = str(patch.get("replacement") or "")
    if not target or not replacement:
        return False
    store.write_candidate_file(gap_id, target, replacement)
    return True


def run_healer_loop(
    *,
    store: CandidateStore,
    gap_report: DomainGapReport,
    ai_client: BootstrapAIClient | None = None,
    max_rounds: int = MAX_HEALER_ROUNDS,
    force_unhealable: bool = False,
) -> dict[str, Any]:
    client = ai_client or MockBootstrapAIClient()
    if force_unhealable:
        return {
            "passed": False,
            "rounds": 0,
            "history": [],
            "validation": {
                "passed": False,
                "blockers": ["unhealable_fixture_failure"],
                "checks": {},
            },
            "ai_calls": getattr(client, "calls", MockBootstrapAIClient.calls),
            "needs_admin_review": True,
        }
    history: list[dict[str, Any]] = []
    for round_idx in range(1, max_rounds + 1):
        if force_unhealable:
            validation = {
                "passed": False,
                "blockers": ["unhealable_fixture_failure"],
                "checks": {},
            }
        else:
            validation = validate_candidate_domain(store=store, gap_report=gap_report)
        if validation.get("passed"):
            return {
                "passed": True,
                "rounds": round_idx - 1,
                "history": history,
                "validation": validation,
                "ai_calls": getattr(client, "calls", MockBootstrapAIClient.calls),
            }

        patch = client.generate_scaffold_patch(
            gap_id=gap_report.gap_id,
            failure_report=validation,
        )
        applied = apply_healer_patch(store, gap_report.gap_id, patch)
        history.append(
            {
                "round": round_idx,
                "validation_blockers": validation.get("blockers"),
                "patch_applied": applied,
            }
        )
        if not applied:
            break

    final_validation = validate_candidate_domain(store=store, gap_report=gap_report)
    return {
        "passed": bool(final_validation.get("passed")),
        "rounds": len(history),
        "history": history,
        "validation": final_validation,
        "ai_calls": getattr(client, "calls", MockBootstrapAIClient.calls),
        "needs_admin_review": not final_validation.get("passed"),
    }
