"""Research-only Healer rule protocol (H1+) / frozen multi-rule provenance (H5).

Defines the unified rule outcome record, pass provenance schema, and the
frozen multi-rule execution policy constants. No transform rules live here.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Mapping

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

RULE_PROTOCOL_FIELDS: tuple[str, ...] = (
    "rule_id",
    "layer",
    "priority",
    "applicable",
    "triggered",
    "changed",
    "guard_results",
    "reason",
    "before_hash",
    "after_hash",
    "validation",
    "stop_reason",
)

# H5 frozen provenance — every pass record must expose these keys.
PROVENANCE_FIELDS: tuple[str, ...] = (
    "pass_index",
    "chain_position",
    "candidate_rules_checked",
    "selected_rule_id",
    "selection_priority",
    "applicable",
    "triggered",
    "changed",
    "guard_results",
    "before_hash",
    "after_hash",
    "validation",
    "stop_reason",
    "stopped_after_change",
    "final_status",
)

# Frozen multi-rule execution policy (H5 + audit). Do not soften without a new milestone.
DEFAULT_MAX_PASSES: int = 1

FROZEN_EXECUTION_POLICY: dict[str, Any] = {
    "policy_id": "ce115_research_healer_execution_policy_h5_audit",
    "allowlist_only": True,
    "fixed_priority": True,
    "priority_order": "ascending",
    "one_change_per_pass": True,
    "stop_pass_after_first_changed": True,
    "reparse_after_change": True,
    "revalidate_after_change": True,
    "reevaluate_after_change_when_task_present": True,
    "repair_attempt_requires_changed": True,
    "max_passes_required": True,
    "default_max_passes": DEFAULT_MAX_PASSES,
    # Option A (frozen): exceed max_passes ⇒ transactional rollback to input source.
    "max_passes_semantics": "transactional_rollback",
    "fail_closed_on_max_passes_exceeded": True,
    "rollback_on_max_passes_exceeded": True,
    "consumer_may_use_output_when_max_passes_exceeded": False,
    "forbid_legacy_pipelines": True,
    "production_allowlist_only_approved_rules": True,
    # Chained repair (multi-rule, multi-pass). Default max_passes stays 1;
    # callers that intend a chain must set max_passes >= len(allowlist).
    "chained_repair": {
        "ordering": "fixed_priority_ascending_aligned_to_outer_gates",
        "gate_alignment": "G2_wiring_before_G3_G4_shape",
        "one_change_per_pass": True,
        "revalidate_after_each_change": True,
        "recommended_max_passes": "len(production_allowlist)",
        "chain_position_semantics": (
            "1-based index among passes that changed the source in this run; "
            "None when the pass did not apply a changing rule"
        ),
    },
}

ALLOWED_LAYERS: frozenset[str] = frozenset(
    {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "META"}
)

# Task-difficulty suffix in task_id (e.g. ce115_calc_*_l1) is NOT a failure layer.
TASK_DIFFICULTY_SUFFIX_PATTERN = "_l1"
TASK_DIFFICULTY_VS_FAILURE_LAYER_NOTE = (
    "task_id difficulty markers such as '_l1' name sampler difficulty rank; "
    "failure taxonomy layers are L0–L6/META and must not be inferred from task_id."
)

ALLOWED_STOP_REASONS: frozenset[str | None] = frozenset(
    {
        None,
        "not_applicable",
        "not_triggered",
        "guards_blocked",
        "no_change",
        "changed_stop_pass",
        "allowlist_empty",
        "no_candidate_selected",
        "validation_failed",
        "max_passes_exceeded",
        "stable_no_further_change",
        "transaction_rollback",
    }
)

# Producer (ce115_research_healer_runner) emits dynamic loop-fallback stop_reasons:
#   f"fallback_loop_detected_{loop_reason}"
# where loop_reason is one of:
#   - "compiler_loop_at_line_{lineno}"
#   - "evaluator_loop_with_verdict_{evaluator_outcome}"
# Accept the frozen prefix without enumerating every suffix (protocol consistency only;
# does not change repair / loop detection semantics).
FALLBACK_LOOP_STOP_REASON_PREFIX: str = "fallback_loop_detected_"


def is_allowed_stop_reason(stop_reason: str | None) -> bool:
    if stop_reason in ALLOWED_STOP_REASONS:
        return True
    return isinstance(stop_reason, str) and stop_reason.startswith(
        FALLBACK_LOOP_STOP_REASON_PREFIX
    )

FINAL_STATUSES: frozenset[str] = frozenset(
    {"no_op", "changed", "validation_failed", "max_passes_exceeded", "error"}
)


class RuleProtocolError(ValueError):
    """Raised when a rule outcome or provenance record violates protocol."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RuleOutcome:
    """One allowlisted rule's decision for one runner pass."""

    rule_id: str
    layer: str
    priority: int
    applicable: bool
    triggered: bool
    changed: bool
    guard_results: Mapping[str, Any]
    reason: str
    before_hash: str
    after_hash: str
    validation: Mapping[str, Any]
    stop_reason: str | None


@dataclass(frozen=True)
class PassProvenance:
    """Complete H5 provenance for one runner pass."""

    pass_index: int
    chain_position: int | None
    candidate_rules_checked: tuple[str, ...]
    selected_rule_id: str | None
    selection_priority: int | None
    applicable: bool
    triggered: bool
    changed: bool
    guard_results: Mapping[str, Any]
    before_hash: str
    after_hash: str
    validation: Mapping[str, Any]
    stop_reason: str | None
    stopped_after_change: bool
    final_status: str


@dataclass(frozen=True)
class ResearchHealerResult:
    """Full research-healer run result (zero model calls by construction)."""

    input_source: str
    output_source: str
    input_hash: str
    output_hash: str
    final_status: str
    rule_outcomes: tuple[RuleOutcome, ...]
    provenance: tuple[PassProvenance, ...]
    real_model_calls: int = 0
    protected_snapshot: Mapping[str, Any] = field(default_factory=dict)
    notes: tuple[str, ...] = ()
    max_passes: int = DEFAULT_MAX_PASSES
    execution_policy: Mapping[str, Any] = field(
        default_factory=lambda: dict(FROZEN_EXECUTION_POLICY)
    )
    rolled_back: bool = False
    consumer_may_use_output: bool = True


def rule_outcome_to_dict(outcome: RuleOutcome) -> dict[str, Any]:
    return {
        "rule_id": outcome.rule_id,
        "layer": outcome.layer,
        "priority": outcome.priority,
        "applicable": outcome.applicable,
        "triggered": outcome.triggered,
        "changed": outcome.changed,
        "guard_results": dict(outcome.guard_results),
        "reason": outcome.reason,
        "before_hash": outcome.before_hash,
        "after_hash": outcome.after_hash,
        "validation": dict(outcome.validation),
        "stop_reason": outcome.stop_reason,
    }


def provenance_to_dict(prov: PassProvenance) -> dict[str, Any]:
    return {
        "pass_index": prov.pass_index,
        "chain_position": prov.chain_position,
        "candidate_rules_checked": list(prov.candidate_rules_checked),
        "selected_rule_id": prov.selected_rule_id,
        "selection_priority": prov.selection_priority,
        "applicable": prov.applicable,
        "triggered": prov.triggered,
        "changed": prov.changed,
        "guard_results": dict(prov.guard_results),
        "before_hash": prov.before_hash,
        "after_hash": prov.after_hash,
        "validation": dict(prov.validation),
        "stop_reason": prov.stop_reason,
        "stopped_after_change": prov.stopped_after_change,
        "final_status": prov.final_status,
    }


def research_result_to_dict(result: ResearchHealerResult) -> dict[str, Any]:
    return {
        "input_hash": result.input_hash,
        "output_hash": result.output_hash,
        "final_status": result.final_status,
        "max_passes": result.max_passes,
        "execution_policy": dict(result.execution_policy),
        "rolled_back": result.rolled_back,
        "consumer_may_use_output": result.consumer_may_use_output,
        "rule_outcomes": [rule_outcome_to_dict(o) for o in result.rule_outcomes],
        "provenance": [provenance_to_dict(p) for p in result.provenance],
        "real_model_calls": result.real_model_calls,
        "protected_snapshot": dict(result.protected_snapshot),
        "notes": list(result.notes),
        "source_changed": result.input_hash != result.output_hash,
    }


def validate_rule_outcome(outcome: RuleOutcome) -> None:
    """Validate protocol fields and applicable/triggered/changed semantics."""
    for name in RULE_PROTOCOL_FIELDS:
        if not hasattr(outcome, name):
            raise RuleProtocolError(f"missing protocol field: {name}")

    if not isinstance(outcome.rule_id, str) or not outcome.rule_id.strip():
        raise RuleProtocolError("rule_id must be a non-empty string")
    if outcome.layer not in ALLOWED_LAYERS:
        raise RuleProtocolError(
            f"layer must be one of {sorted(ALLOWED_LAYERS)}, got {outcome.layer!r}"
        )
    if not isinstance(outcome.priority, int):
        raise RuleProtocolError("priority must be an int")
    for flag in ("applicable", "triggered", "changed"):
        if not isinstance(getattr(outcome, flag), bool):
            raise RuleProtocolError(f"{flag} must be a bool")
    if not isinstance(outcome.guard_results, Mapping):
        raise RuleProtocolError("guard_results must be a mapping")
    if not isinstance(outcome.reason, str) or not outcome.reason.strip():
        raise RuleProtocolError("reason must be a non-empty string")
    if not isinstance(outcome.before_hash, str) or not _SHA256_RE.match(outcome.before_hash):
        raise RuleProtocolError("before_hash must be 64-char lowercase hex SHA-256")
    if not isinstance(outcome.after_hash, str) or not _SHA256_RE.match(outcome.after_hash):
        raise RuleProtocolError("after_hash must be 64-char lowercase hex SHA-256")
    if not isinstance(outcome.validation, Mapping):
        raise RuleProtocolError("validation must be a mapping")
    if not is_allowed_stop_reason(outcome.stop_reason):
        allowed = sorted(r for r in ALLOWED_STOP_REASONS if r is not None) + [None]
        raise RuleProtocolError(
            f"stop_reason must be one of {allowed} or start with "
            f"{FALLBACK_LOOP_STOP_REASON_PREFIX!r}, got {outcome.stop_reason!r}"
        )

    # Semantic ladder: changed ⇒ triggered ⇒ applicable
    if outcome.changed and not outcome.triggered:
        raise RuleProtocolError("changed=True requires triggered=True")
    if outcome.triggered and not outcome.applicable:
        raise RuleProtocolError("triggered=True requires applicable=True")
    if outcome.changed and outcome.before_hash == outcome.after_hash:
        raise RuleProtocolError("changed=True requires before_hash != after_hash")
    if not outcome.changed and outcome.before_hash != outcome.after_hash:
        raise RuleProtocolError("before_hash != after_hash requires changed=True")

    # H5: never claim a repair attempt unless the source actually changed.
    if "repair_attempted" in outcome.validation:
        if bool(outcome.validation["repair_attempted"]) and not outcome.changed:
            raise RuleProtocolError(
                "validation.repair_attempted=True is forbidden when changed=False"
            )


def validate_provenance(prov: PassProvenance) -> None:
    for name in PROVENANCE_FIELDS:
        if not hasattr(prov, name):
            raise RuleProtocolError(f"missing provenance field: {name}")
    if not isinstance(prov.pass_index, int) or prov.pass_index < 0:
        raise RuleProtocolError("pass_index must be a non-negative int")
    if prov.chain_position is not None and (
        not isinstance(prov.chain_position, int) or prov.chain_position < 1
    ):
        raise RuleProtocolError("chain_position must be None or an int >= 1")
    if prov.changed and prov.chain_position is None:
        raise RuleProtocolError("changed=True requires chain_position >= 1")
    if (not prov.changed) and prov.chain_position is not None:
        raise RuleProtocolError("chain_position requires changed=True")
    if not isinstance(prov.candidate_rules_checked, tuple):
        raise RuleProtocolError("candidate_rules_checked must be a tuple")
    for rule_id in prov.candidate_rules_checked:
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise RuleProtocolError("candidate_rules_checked entries must be non-empty strings")
    if prov.selected_rule_id is not None and (
        not isinstance(prov.selected_rule_id, str) or not prov.selected_rule_id.strip()
    ):
        raise RuleProtocolError("selected_rule_id must be None or a non-empty string")
    if prov.selection_priority is not None and not isinstance(prov.selection_priority, int):
        raise RuleProtocolError("selection_priority must be None or an int")
    for flag in ("applicable", "triggered", "changed", "stopped_after_change"):
        if not isinstance(getattr(prov, flag), bool):
            raise RuleProtocolError(f"{flag} must be a bool")
    if not isinstance(prov.guard_results, Mapping):
        raise RuleProtocolError("guard_results must be a mapping")
    if not isinstance(prov.before_hash, str) or not _SHA256_RE.match(prov.before_hash):
        raise RuleProtocolError("before_hash must be 64-char lowercase hex SHA-256")
    if not isinstance(prov.after_hash, str) or not _SHA256_RE.match(prov.after_hash):
        raise RuleProtocolError("after_hash must be 64-char lowercase hex SHA-256")
    if not isinstance(prov.validation, Mapping):
        raise RuleProtocolError("validation must be a mapping")
    if not is_allowed_stop_reason(prov.stop_reason):
        allowed = sorted(r for r in ALLOWED_STOP_REASONS if r is not None) + [None]
        raise RuleProtocolError(
            f"stop_reason must be one of {allowed} or start with "
            f"{FALLBACK_LOOP_STOP_REASON_PREFIX!r}, got {prov.stop_reason!r}"
        )
    if prov.final_status not in FINAL_STATUSES:
        raise RuleProtocolError(
            f"final_status must be one of {sorted(FINAL_STATUSES)}, got {prov.final_status!r}"
        )
    if prov.stopped_after_change and prov.selected_rule_id is None:
        raise RuleProtocolError("stopped_after_change=True requires selected_rule_id")
    if prov.stopped_after_change and not prov.changed:
        raise RuleProtocolError("stopped_after_change=True requires changed=True")
    if prov.changed and not prov.triggered:
        raise RuleProtocolError("provenance changed=True requires triggered=True")
    if prov.triggered and not prov.applicable:
        raise RuleProtocolError("provenance triggered=True requires applicable=True")
    if prov.changed and prov.before_hash == prov.after_hash:
        raise RuleProtocolError("provenance changed=True requires before_hash != after_hash")
    if not prov.changed and prov.before_hash != prov.after_hash:
        raise RuleProtocolError("provenance hash delta requires changed=True")


def validate_research_result(result: ResearchHealerResult) -> None:
    if result.final_status not in FINAL_STATUSES:
        raise RuleProtocolError(
            f"final_status must be one of {sorted(FINAL_STATUSES)}, got {result.final_status!r}"
        )
    if result.real_model_calls != 0:
        raise RuleProtocolError("research healer must record real_model_calls=0")
    if not isinstance(result.max_passes, int) or result.max_passes < 1:
        raise RuleProtocolError("max_passes must be an int >= 1")
    if result.input_hash != sha256_text(result.input_source):
        raise RuleProtocolError("input_hash must match input_source")
    if result.output_hash != sha256_text(result.output_source):
        raise RuleProtocolError("output_hash must match output_source")
    if result.final_status == "no_op":
        if result.input_hash != result.output_hash:
            raise RuleProtocolError("no_op requires input_hash == output_hash")
        if any(o.changed for o in result.rule_outcomes):
            raise RuleProtocolError("no_op forbids any changed rule outcome")
    if result.final_status == "changed":
        if result.input_hash == result.output_hash:
            raise RuleProtocolError("changed status requires input_hash != output_hash")
        if not result.consumer_may_use_output:
            raise RuleProtocolError("changed status requires consumer_may_use_output=True")
        if result.rolled_back:
            raise RuleProtocolError("changed status forbids rolled_back=True")
    if result.final_status == "max_passes_exceeded":
        # Option A: transactional rollback — consumer must not use partial output.
        if result.input_hash != result.output_hash:
            raise RuleProtocolError(
                "max_passes_exceeded requires transactional rollback "
                "(input_hash == output_hash)"
            )
        if result.output_source != result.input_source:
            raise RuleProtocolError(
                "max_passes_exceeded requires output_source == input_source"
            )
        if not result.rolled_back:
            raise RuleProtocolError("max_passes_exceeded requires rolled_back=True")
        if result.consumer_may_use_output:
            raise RuleProtocolError(
                "max_passes_exceeded requires consumer_may_use_output=False"
            )
    for outcome in result.rule_outcomes:
        validate_rule_outcome(outcome)
    for prov in result.provenance:
        validate_provenance(prov)
    if result.provenance:
        if result.provenance[-1].final_status != result.final_status:
            raise RuleProtocolError(
                "last provenance.final_status must match result.final_status"
            )


def make_parse_validation(source: str) -> dict[str, Any]:
    """Lightweight re-parse validation used after every potential change."""
    import ast

    try:
        ast.parse(source)
    except SyntaxError as exc:
        return {
            "ast_parse_success": False,
            "parse_error": str(exc),
            "source_len": len(source),
        }
    return {
        "ast_parse_success": True,
        "parse_error": None,
        "source_len": len(source),
    }


def assert_protocol_field_coverage(record: Mapping[str, Any]) -> None:
    missing = [name for name in RULE_PROTOCOL_FIELDS if name not in record]
    if missing:
        raise RuleProtocolError(f"rule protocol missing fields: {missing}")


def assert_provenance_field_coverage(record: Mapping[str, Any]) -> None:
    missing = [name for name in PROVENANCE_FIELDS if name not in record]
    if missing:
        raise RuleProtocolError(f"provenance missing fields: {missing}")
