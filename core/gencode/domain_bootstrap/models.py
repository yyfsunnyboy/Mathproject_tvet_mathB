# -*- coding: utf-8 -*-
"""Domain bootstrap data models and state machine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class BootstrapState(str, Enum):
    GAP_DETECTED = "gap_detected"
    PLANNING = "planning"
    DRAFT = "draft"
    VALIDATING = "validating"
    HEALING = "healing"
    CANDIDATE = "candidate"
    AWAITING_TEACHER_REVIEW = "awaiting_teacher_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_ADMIN_REVIEW = "needs_admin_review"


VALID_TRANSITIONS: dict[BootstrapState, frozenset[BootstrapState]] = {
    BootstrapState.GAP_DETECTED: frozenset({BootstrapState.PLANNING, BootstrapState.REJECTED}),
    BootstrapState.PLANNING: frozenset({BootstrapState.DRAFT, BootstrapState.REJECTED}),
    BootstrapState.DRAFT: frozenset({BootstrapState.VALIDATING, BootstrapState.REJECTED}),
    BootstrapState.VALIDATING: frozenset(
        {BootstrapState.CANDIDATE, BootstrapState.HEALING, BootstrapState.NEEDS_ADMIN_REVIEW}
    ),
    BootstrapState.HEALING: frozenset(
        {BootstrapState.VALIDATING, BootstrapState.CANDIDATE, BootstrapState.NEEDS_ADMIN_REVIEW, BootstrapState.REJECTED}
    ),
    BootstrapState.CANDIDATE: frozenset({BootstrapState.AWAITING_TEACHER_REVIEW, BootstrapState.REJECTED}),
    BootstrapState.AWAITING_TEACHER_REVIEW: frozenset(
        {BootstrapState.VERIFIED, BootstrapState.REJECTED, BootstrapState.NEEDS_ADMIN_REVIEW}
    ),
    BootstrapState.VERIFIED: frozenset(),
    BootstrapState.REJECTED: frozenset(),
    BootstrapState.NEEDS_ADMIN_REVIEW: frozenset(
        {BootstrapState.PLANNING, BootstrapState.REJECTED, BootstrapState.HEALING}
    ),
}

MAX_HEALER_ROUNDS = 3


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class DomainGapReport:
    gap_id: str
    problem_type_ids: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    matched_capabilities: list[str] = field(default_factory=list)
    missing_capabilities: list[str] = field(default_factory=list)
    affected_skill_ids: list[str] = field(default_factory=list)
    affected_component_ids: list[str] = field(default_factory=list)
    source_example_ids: list[int] = field(default_factory=list)
    answer_contracts: list[dict[str, Any]] = field(default_factory=list)
    presentation_modes: list[str] = field(default_factory=list)
    source_hashes: list[str] = field(default_factory=list)
    nearby_domains: list[str] = field(default_factory=list)
    suggested_action: str = "create_new_domain"
    gap_fingerprint: str = ""
    error_code: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StateTransitionRecord:
    from_state: str
    to_state: str
    actor: str
    timestamp: str
    source_hash: str = ""
    artifact_hash: str = ""
    ai_model: str = ""
    token_usage: int = 0
    validation_summary: dict[str, Any] = field(default_factory=dict)
    repair_history: list[dict[str, Any]] = field(default_factory=list)
    error_code: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BootstrapSession:
    gap_id: str
    state: BootstrapState = BootstrapState.GAP_DETECTED
    gap_report: DomainGapReport | None = None
    cost_estimate: dict[str, Any] = field(default_factory=dict)
    artifact_hash: str = ""
    source_hash: str = ""
    repair_rounds: int = 0
    teacher_answers: dict[str, Any] = field(default_factory=dict)
    transitions: list[StateTransitionRecord] = field(default_factory=list)
    validation_summary: dict[str, Any] = field(default_factory=dict)
    promoted_domain_key: str = ""
    registry_revision: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "state": self.state.value,
            "gap_report": self.gap_report.to_dict() if self.gap_report else None,
            "cost_estimate": self.cost_estimate,
            "artifact_hash": self.artifact_hash,
            "source_hash": self.source_hash,
            "repair_rounds": self.repair_rounds,
            "teacher_answers": self.teacher_answers,
            "transitions": [t.to_dict() for t in self.transitions],
            "validation_summary": self.validation_summary,
            "promoted_domain_key": self.promoted_domain_key,
            "registry_revision": self.registry_revision,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BootstrapSession:
        gap_raw = data.get("gap_report")
        gap_report = DomainGapReport(**gap_raw) if isinstance(gap_raw, dict) else None
        transitions = [
            StateTransitionRecord(**row)
            for row in (data.get("transitions") or [])
            if isinstance(row, dict)
        ]
        return cls(
            gap_id=str(data.get("gap_id") or ""),
            state=BootstrapState(str(data.get("state") or BootstrapState.GAP_DETECTED.value)),
            gap_report=gap_report,
            cost_estimate=dict(data.get("cost_estimate") or {}),
            artifact_hash=str(data.get("artifact_hash") or ""),
            source_hash=str(data.get("source_hash") or ""),
            repair_rounds=int(data.get("repair_rounds") or 0),
            teacher_answers=dict(data.get("teacher_answers") or {}),
            transitions=transitions,
            validation_summary=dict(data.get("validation_summary") or {}),
            promoted_domain_key=str(data.get("promoted_domain_key") or ""),
            registry_revision=str(data.get("registry_revision") or ""),
        )
