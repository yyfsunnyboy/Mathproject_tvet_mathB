# -*- coding: utf-8 -*-
"""Domain bootstrap orchestrator — coordinates gap → verified promotion."""

from __future__ import annotations

from typing import Any

from core.gencode.domain_bootstrap.candidate_store import CandidateStore
from core.gencode.domain_bootstrap.gap_service import detect_or_reuse_domain_gap, is_domain_gap_error_code
from core.gencode.domain_bootstrap.healer import MockBootstrapAIClient, run_healer_loop
from core.gencode.domain_bootstrap.models import (
    BootstrapSession,
    BootstrapState,
    StateTransitionRecord,
    VALID_TRANSITIONS,
    utc_now_iso,
)
from core.gencode.domain_bootstrap.planner import estimate_bootstrap_cost
from core.gencode.domain_bootstrap.promotion_service import promote_candidate_to_verified
from core.gencode.domain_bootstrap.scaffold_builder import build_candidate_scaffold
from core.gencode.domain_bootstrap.teacher_review import (
    build_teacher_review_package,
    validate_teacher_answers,
)
from core.gencode.domain_bootstrap.validation_runner import validate_candidate_domain
from core.gencode.skill_fixed_domain_authority import SkillFixedDomainError


def _transition(
    session: BootstrapSession,
    new_state: BootstrapState,
    *,
    actor: str,
    error_code: str = "",
    validation_summary: dict[str, Any] | None = None,
    artifact_hash: str = "",
    ai_model: str = "mock",
    token_usage: int = 0,
) -> BootstrapSession:
    if new_state not in VALID_TRANSITIONS.get(session.state, frozenset()):
        raise ValueError(f"invalid_bootstrap_transition:{session.state.value}->{new_state.value}")
    session.transitions.append(
        StateTransitionRecord(
            from_state=session.state.value,
            to_state=new_state.value,
            actor=actor,
            timestamp=utc_now_iso(),
            source_hash=session.source_hash,
            artifact_hash=artifact_hash or session.artifact_hash,
            ai_model=ai_model,
            token_usage=token_usage,
            validation_summary=dict(validation_summary or {}),
            error_code=error_code,
        )
    )
    session.state = new_state
    return session


class DomainBootstrapOrchestrator:
    def __init__(self, store: CandidateStore | None = None) -> None:
        self.store = store or CandidateStore()
        self.ai_calls = 0

    def handle_resolver_gap(
        self,
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
        gap_report = detect_or_reuse_domain_gap(
            store=self.store,
            error_code=exc.code,
            error_details=dict(exc.details or {}),
            skill_id=skill_id,
            textbook_example_id=textbook_example_id,
            component_id=component_id,
            phase1_spec=phase1_spec,
            source_hash=source_hash,
        )
        session = self.store.load_session(gap_report.gap_id)
        if session is None:
            session = BootstrapSession(
                gap_id=gap_report.gap_id,
                gap_report=gap_report,
                source_hash=source_hash,
            )
        else:
            session.gap_report = gap_report
            if source_hash:
                session.source_hash = source_hash
        if session.state != BootstrapState.GAP_DETECTED:
            session = _transition(session, BootstrapState.GAP_DETECTED, actor="resolver")
        self.store.save_session(session)
        return {
            "gap_report": gap_report.to_dict(),
            "session": session.to_dict(),
            "teacher_message": "偵測到新的數學能力，系統可建立可重用出題能力。",
        }

    def start_bootstrap(
        self,
        gap_id: str,
        *,
        allow_ai: bool = False,
        deliberately_broken: bool = False,
        force_unhealable: bool = False,
    ) -> dict[str, Any]:
        session = self.store.load_session(gap_id)
        if session is None or session.gap_report is None:
            raise ValueError("gap_session_not_found")
        gap_report = session.gap_report

        session = _transition(session, BootstrapState.PLANNING, actor="admin")
        cost = estimate_bootstrap_cost(gap_report=gap_report, store=self.store, allow_ai=allow_ai)
        session.cost_estimate = cost
        if cost.get("requires_explicit_ai_authorization") and not allow_ai:
            self.store.save_session(session)
            return {
                "state": session.state.value,
                "cost_estimate": cost,
                "requires_ai_authorization": True,
            }

        session = _transition(session, BootstrapState.DRAFT, actor="bootstrap")
        scaffold = build_candidate_scaffold(
            store=self.store,
            gap_report=gap_report,
            deliberately_broken=deliberately_broken,
        )
        session.artifact_hash = str(scaffold.get("artifact_hash") or "")

        session = _transition(session, BootstrapState.VALIDATING, actor="bootstrap")
        validation = validate_candidate_domain(store=self.store, gap_report=gap_report)
        session.validation_summary = validation

        if force_unhealable:
            session = _transition(session, BootstrapState.HEALING, actor="healer")
            heal = run_healer_loop(
                store=self.store,
                gap_report=gap_report,
                force_unhealable=True,
            )
            session.repair_rounds = int(heal.get("rounds") or 0)
            session.validation_summary = dict(heal.get("validation") or {})
            session = _transition(
                session,
                BootstrapState.NEEDS_ADMIN_REVIEW,
                actor="healer",
                error_code="HEALER_EXHAUSTED",
                validation_summary=session.validation_summary,
            )
            self.store.save_session(session)
            return {
                "state": session.state.value,
                "teacher_message": "需要管理員協助",
                "validation": session.validation_summary,
                "ai_calls": self.ai_calls,
            }
        elif not validation.get("passed"):
            session = _transition(session, BootstrapState.HEALING, actor="healer")
            heal = run_healer_loop(
                store=self.store,
                gap_report=gap_report,
                force_unhealable=force_unhealable,
            )
            self.ai_calls += int(heal.get("ai_calls") or 0)
            session.repair_rounds = int(heal.get("rounds") or 0)
            session.validation_summary = dict(heal.get("validation") or {})
            if heal.get("passed"):
                session = _transition(
                    session,
                    BootstrapState.CANDIDATE,
                    actor="healer",
                    validation_summary=session.validation_summary,
                )
            elif heal.get("needs_admin_review"):
                session = _transition(
                    session,
                    BootstrapState.NEEDS_ADMIN_REVIEW,
                    actor="healer",
                    error_code="HEALER_EXHAUSTED",
                    validation_summary=session.validation_summary,
                )
                self.store.save_session(session)
                return {
                    "state": session.state.value,
                    "teacher_message": "需要管理員協助",
                    "validation": session.validation_summary,
                    "ai_calls": self.ai_calls,
                }
        else:
            session = _transition(
                session,
                BootstrapState.CANDIDATE,
                actor="validator",
                validation_summary=validation,
            )

        session = _transition(session, BootstrapState.AWAITING_TEACHER_REVIEW, actor="system")
        review = build_teacher_review_package(
            store=self.store,
            gap_report=gap_report,
            validation_summary=session.validation_summary,
        )
        self.store.save_session(session)
        return {
            "state": session.state.value,
            "cost_estimate": cost,
            "scaffold": scaffold,
            "validation": session.validation_summary,
            "teacher_review": review,
            "ai_calls": self.ai_calls,
        }

    def approve_and_promote(
        self,
        gap_id: str,
        *,
        teacher_answers: dict[str, Any],
        registry_store_path: str | None = None,
    ) -> dict[str, Any]:
        session = self.store.load_session(gap_id)
        if session is None or session.gap_report is None:
            raise ValueError("gap_session_not_found")
        ok, blockers = validate_teacher_answers(teacher_answers)
        if not ok:
            return {"approved": False, "blockers": blockers}
        session.teacher_answers = dict(teacher_answers)
        promotion = promote_candidate_to_verified(
            store=self.store,
            gap_report=session.gap_report,
            artifact_hash=session.artifact_hash,
            teacher_approved=True,
            registry_store_path=registry_store_path,
        )
        session.promoted_domain_key = str(promotion.get("domain_key") or "")
        session.registry_revision = str(promotion.get("registry_revision") or "")
        session = _transition(
            session,
            BootstrapState.VERIFIED,
            actor="teacher",
            artifact_hash=session.artifact_hash,
        )
        self.store.save_session(session)
        return {
            "approved": True,
            "promotion": promotion,
            "session": session.to_dict(),
            "teacher_message": "已核准並重新生成",
        }

    def reject(self, gap_id: str, *, actor: str = "teacher") -> dict[str, Any]:
        session = self.store.load_session(gap_id)
        if session is None:
            raise ValueError("gap_session_not_found")
        session = _transition(session, BootstrapState.REJECTED, actor=actor)
        self.store.save_session(session)
        return {"state": session.state.value}
