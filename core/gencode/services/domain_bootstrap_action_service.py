# -*- coding: utf-8 -*-
"""Admin-facing domain bootstrap action service."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from core.gencode.domain_bootstrap.candidate_store import CandidateStore
from core.gencode.domain_bootstrap.gap_service import detect_or_reuse_domain_gap, is_domain_gap_error_code
from core.gencode.domain_bootstrap.models import BootstrapState
from core.gencode.domain_bootstrap.orchestrator import DomainBootstrapOrchestrator
from core.gencode.domain_bootstrap.planner import estimate_bootstrap_cost
from core.gencode.domain_bootstrap.retry_service import retry_affected_components
from core.gencode.domain_bootstrap.teacher_review import build_teacher_review_package
from core.gencode.skill_fixed_domain_authority import SkillFixedDomainError


def get_domain_gap_report(gap_id: str, *, store_root: str | Path | None = None) -> dict[str, Any]:
    store = CandidateStore(bootstrap_root=store_root) if store_root else CandidateStore()
    report = store.load_gap_report(gap_id)
    session = store.load_session(gap_id)
    if report is None:
        raise ValueError("gap_not_found")
    return {
        "gap_report": report.to_dict(),
        "session": session.to_dict() if session else None,
    }


def estimate_domain_bootstrap_cost(gap_id: str, *, allow_ai: bool = False) -> dict[str, Any]:
    store = CandidateStore()
    report = store.load_gap_report(gap_id)
    if report is None:
        raise ValueError("gap_not_found")
    return estimate_bootstrap_cost(gap_report=report, store=store, allow_ai=allow_ai)


def start_domain_bootstrap(
    gap_id: str,
    *,
    allow_ai: bool = False,
    deliberately_broken: bool = False,
    force_unhealable: bool = False,
) -> dict[str, Any]:
    orchestrator = DomainBootstrapOrchestrator()
    return orchestrator.start_bootstrap(
        gap_id,
        allow_ai=allow_ai,
        deliberately_broken=deliberately_broken,
        force_unhealable=force_unhealable,
    )


def get_bootstrap_status(gap_id: str) -> dict[str, Any]:
    store = CandidateStore()
    session = store.load_session(gap_id)
    if session is None:
        raise ValueError("gap_session_not_found")
    teacher_message = {
        BootstrapState.GAP_DETECTED.value: "偵測到新的數學能力",
        BootstrapState.PLANNING.value: "正在建立可重用出題能力",
        BootstrapState.VALIDATING.value: "自動測試中",
        BootstrapState.HEALING.value: "自動測試與修補中",
        BootstrapState.AWAITING_TEACHER_REVIEW.value: "等待教師確認",
        BootstrapState.VERIFIED.value: "已核准並重新生成",
        BootstrapState.NEEDS_ADMIN_REVIEW.value: "需要管理員協助",
        BootstrapState.REJECTED.value: "已拒絕",
    }.get(session.state.value, session.state.value)

    return {
        "gap_id": gap_id,
        "state": session.state.value,
        "teacher_message": teacher_message,
        "session": session.to_dict(),
    }


def get_candidate_preview(gap_id: str) -> dict[str, Any]:
    store = CandidateStore()
    session = store.load_session(gap_id)
    report = store.load_gap_report(gap_id)
    if session is None or report is None:
        raise ValueError("gap_not_found")
    return build_teacher_review_package(
        store=store,
        gap_report=report,
        validation_summary=session.validation_summary,
    )


def approve_domain_bootstrap(
    gap_id: str,
    *,
    teacher_answers: dict[str, Any],
    registry_store_path: str | Path | None = None,
) -> dict[str, Any]:
    orchestrator = DomainBootstrapOrchestrator()
    return orchestrator.approve_and_promote(
        gap_id,
        teacher_answers=teacher_answers,
        registry_store_path=str(registry_store_path) if registry_store_path else None,
    )


def reject_domain_bootstrap(gap_id: str) -> dict[str, Any]:
    return DomainBootstrapOrchestrator().reject(gap_id)


def retry_gap_affected_components(
    conn: sqlite3.Connection,
    gap_id: str,
    *,
    dryrun_runner: Any,
    dryrun_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    store = CandidateStore()
    report = store.load_gap_report(gap_id)
    if report is None:
        raise ValueError("gap_not_found")
    return retry_affected_components(
        conn,
        gap_report=report,
        dryrun_runner=dryrun_runner,
        dryrun_kwargs=dryrun_kwargs,
    )


def record_gap_from_resolver_exception(
    *,
    exc: SkillFixedDomainError,
    skill_id: str,
    textbook_example_id: int | None,
    component_id: str | None,
    phase1_spec: dict[str, Any] | None = None,
    source_hash: str = "",
) -> dict[str, Any]:
    if not is_domain_gap_error_code(exc.code):
        raise exc
    return DomainBootstrapOrchestrator().handle_resolver_gap(
        exc=exc,
        skill_id=skill_id,
        textbook_example_id=textbook_example_id,
        component_id=component_id,
        phase1_spec=phase1_spec,
        source_hash=source_hash,
    )
