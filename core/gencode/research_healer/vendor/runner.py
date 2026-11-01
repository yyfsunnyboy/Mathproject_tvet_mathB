"""Research-only allowlist Healer runner (H1+) / frozen multi-rule policy (H5+audit).

Frozen execution policy:
- allowlist only (production: approved L2 only; L1 paused/experimental)
- fixed priority (ascending)
- one change per pass; stop that pass after the first changed rule
- after any change: re-parse / re-validate / re-evaluate (when task present)
- never claim repair_attempted unless changed=True
- max_passes mandatory; exceed ⇒ transactional rollback to input (Option A)
- must not call legacy Regex / AST / AntiDuplication / UnifiedCleanup pipelines
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

from core.gencode.research_healer.vendor.protocol import (
    DEFAULT_MAX_PASSES,
    FROZEN_EXECUTION_POLICY,
    PassProvenance,
    ResearchHealerResult,
    RuleOutcome,
    RuleProtocolError,
    make_parse_validation,
    sha256_text,
    validate_research_result,
    validate_rule_outcome,
)
from core.gencode.research_healer.vendor.rules_l1 import (
    LAYER as _L1_LAYER,
    PRIORITY as _L1_PRIORITY,
    RULE_ID as L1_COMMENT_ONLY_IF_INSERT_PASS,
    apply as _l1_apply,
    is_applicable as _l1_is_applicable,
    is_triggered as _l1_is_triggered,
)
from core.gencode.research_healer.vendor.rules_l2 import (
    LAYER as _L2_LAYER,
    PRIORITY as _L2_PRIORITY,
    RULE_ID as L2_SINGLE_KEY_ORACLE_PAYLOAD_WRAP,
    apply as _l2_apply,
    is_applicable as _l2_is_applicable,
    is_triggered as _l2_is_triggered,
)
from core.gencode.research_healer.vendor.rules_l2_kwargs_bag_inline import (
    LAYER as _L2_KWARGS_LAYER,
    PRIORITY as _L2_KWARGS_PRIORITY,
    RULE_ID as L2_KWARGS_EMPTY_BAG_INLINE_UNIQUE_PARAM,
    apply as _l2_kwargs_apply,
    is_applicable as _l2_kwargs_is_applicable,
    is_triggered as _l2_kwargs_is_triggered,
)
from core.gencode.research_healer.vendor.rules_l2_json_dumps_unwrap import (
    LAYER as _L2_DUMPS_LAYER,
    PRIORITY as _L2_DUMPS_PRIORITY,
    RULE_ID as L2_CORRECT_ANSWER_JSON_DUMPS_UNWRAP,
    apply as _l2_dumps_apply,
    is_applicable as _l2_dumps_is_applicable,
    is_triggered as _l2_dumps_is_triggered,
)
from core.gencode.research_healer.vendor.rules_l1_paren_close import (
    LAYER as _L1_PAREN_LAYER,
    PRIORITY as _L1_PAREN_PRIORITY,
    RULE_ID as L1_CLOSE_UNBALANCED_PARENTHESIS,
    apply as _l1_paren_apply,
    is_applicable as _l1_paren_is_applicable,
    is_triggered as _l1_paren_is_triggered,
)
from core.gencode.research_healer.vendor.rules_l1_delimiter_extended import (
    LAYER as _L1_DELIM_EXT_LAYER,
    PRIORITY as _L1_DELIM_EXT_PRIORITY,
    RULE_ID as L1_CLOSE_UNBALANCED_DELIMITER_EXTENDED,
    apply as _l1_delim_ext_apply,
    is_applicable as _l1_delim_ext_is_applicable,
    is_triggered as _l1_delim_ext_is_triggered,
)
from core.gencode.research_healer.vendor.rules_l1_prose_narrow import (
    LAYER as _L1_PROSE_LAYER,
    PRIORITY as _L1_PROSE_PRIORITY,
    RULE_ID as L1_PROSE_RESIDUE_NARROW,
    apply as _l1_prose_apply,
    is_applicable as _l1_prose_is_applicable,
    is_triggered as _l1_prose_is_triggered,
)

# Production allowlist — audit-approved L2 only. L1 is paused.
# Order in this tuple is registration order; execution sorts by ascending priority.
# Gate-aligned priorities: payload-wrap(100) → kwargs-bag(110) → dumps-unwrap(120).
RULE_ALLOWLIST: tuple[str, ...] = (
    L1_CLOSE_UNBALANCED_PARENTHESIS,
    L1_CLOSE_UNBALANCED_DELIMITER_EXTENDED,
    L1_PROSE_RESIDUE_NARROW,
    L2_SINGLE_KEY_ORACLE_PAYLOAD_WRAP,
    L2_KWARGS_EMPTY_BAG_INLINE_UNIQUE_PARAM,
    L2_CORRECT_ANSWER_JSON_DUMPS_UNWRAP,
)

# Chained multi-rule repair budget (explicit; DEFAULT_MAX_PASSES remains 1 for single-pass Ab3).
RECOMMENDED_CHAIN_MAX_PASSES: int = len(RULE_ALLOWLIST)

FORBIDDEN_LEGACY_IMPORTS: frozenset[str] = frozenset(
    {
        "core.healers.unified_cleanup_healer",
        "core.healers.ast_healer",
        "core.healers.regex_healer",
        "core.healers.anti_duplication_healer",
        "UnifiedCleanupHealer",
        "ASTHealer",
        "RegexHealer",
        "AntiDuplicationHealer",
    }
)


class ResearchHealerRule(Protocol):
    """Contract for an allowlisted transform rule."""

    rule_id: str
    layer: str
    priority: int

    def is_applicable(self, source: str, context: Mapping[str, Any]) -> tuple[bool, Mapping[str, Any], str]:
        """Return (applicable, guard_results, reason)."""

    def is_triggered(self, source: str, context: Mapping[str, Any]) -> tuple[bool, str]:
        """Return (triggered, reason). Only called when applicable."""

    def apply(self, source: str, context: Mapping[str, Any]) -> tuple[str, Mapping[str, Any], str]:
        """Return (new_source, validation_extra, reason)."""


@dataclass(frozen=True)
class _RegisteredRule:
    rule_id: str
    layer: str
    priority: int
    is_applicable: Callable[[str, Mapping[str, Any]], tuple[bool, Mapping[str, Any], str]]
    is_triggered: Callable[[str, Mapping[str, Any]], tuple[bool, str]]
    apply: Callable[[str, Mapping[str, Any]], tuple[str, Mapping[str, Any], str]]


# Production registry: approved L2 only.
RULE_REGISTRY: dict[str, _RegisteredRule] = {
    L1_CLOSE_UNBALANCED_PARENTHESIS: _RegisteredRule(
        rule_id=L1_CLOSE_UNBALANCED_PARENTHESIS,
        layer=_L1_PAREN_LAYER,
        priority=_L1_PAREN_PRIORITY,
        is_applicable=_l1_paren_is_applicable,
        is_triggered=_l1_paren_is_triggered,
        apply=_l1_paren_apply,
    ),
    L1_CLOSE_UNBALANCED_DELIMITER_EXTENDED: _RegisteredRule(
        rule_id=L1_CLOSE_UNBALANCED_DELIMITER_EXTENDED,
        layer=_L1_DELIM_EXT_LAYER,
        priority=_L1_DELIM_EXT_PRIORITY,
        is_applicable=_l1_delim_ext_is_applicable,
        is_triggered=_l1_delim_ext_is_triggered,
        apply=_l1_delim_ext_apply,
    ),
    L1_PROSE_RESIDUE_NARROW: _RegisteredRule(
        rule_id=L1_PROSE_RESIDUE_NARROW,
        layer=_L1_PROSE_LAYER,
        priority=_L1_PROSE_PRIORITY,
        is_applicable=_l1_prose_is_applicable,
        is_triggered=_l1_prose_is_triggered,
        apply=_l1_prose_apply,
    ),
    L2_SINGLE_KEY_ORACLE_PAYLOAD_WRAP: _RegisteredRule(
        rule_id=L2_SINGLE_KEY_ORACLE_PAYLOAD_WRAP,
        layer=_L2_LAYER,
        priority=_L2_PRIORITY,
        is_applicable=_l2_is_applicable,
        is_triggered=_l2_is_triggered,
        apply=_l2_apply,
    ),
    L2_KWARGS_EMPTY_BAG_INLINE_UNIQUE_PARAM: _RegisteredRule(
        rule_id=L2_KWARGS_EMPTY_BAG_INLINE_UNIQUE_PARAM,
        layer=_L2_KWARGS_LAYER,
        priority=_L2_KWARGS_PRIORITY,
        is_applicable=_l2_kwargs_is_applicable,
        is_triggered=_l2_kwargs_is_triggered,
        apply=_l2_kwargs_apply,
    ),
    L2_CORRECT_ANSWER_JSON_DUMPS_UNWRAP: _RegisteredRule(
        rule_id=L2_CORRECT_ANSWER_JSON_DUMPS_UNWRAP,
        layer=_L2_DUMPS_LAYER,
        priority=_L2_DUMPS_PRIORITY,
        is_applicable=_l2_dumps_is_applicable,
        is_triggered=_l2_dumps_is_triggered,
        apply=_l2_dumps_apply,
    ),
}

# Experimental / paused rules — not on production allowlist.
EXPERIMENTAL_RULE_REGISTRY: dict[str, _RegisteredRule] = {
    L1_COMMENT_ONLY_IF_INSERT_PASS: _RegisteredRule(
        rule_id=L1_COMMENT_ONLY_IF_INSERT_PASS,
        layer=_L1_LAYER,
        priority=_L1_PRIORITY,
        is_applicable=_l1_is_applicable,
        is_triggered=_l1_is_triggered,
        apply=_l1_apply,
    ),
}


def _assert_no_legacy_pipeline() -> None:
    """Hard guard: research runner must not pull legacy healer pipelines."""
    for banned in (
        "UnifiedCleanupHealer",
        "ASTHealer",
        "RegexHealer",
        "AntiDuplicationHealer",
    ):
        if banned in globals():
            raise RuleProtocolError(f"research runner must not bind legacy healer {banned}")


def select_allowlisted_rules(
    allowlist: Sequence[str] = RULE_ALLOWLIST,
    registry: Mapping[str, _RegisteredRule] | None = None,
) -> list[_RegisteredRule]:
    """Return allowlisted rules sorted by fixed priority (then rule_id)."""
    if registry is None:
        reg: dict[str, _RegisteredRule] = {
            **EXPERIMENTAL_RULE_REGISTRY,
            **RULE_REGISTRY,
        }
    else:
        reg = dict(registry)
    selected: list[_RegisteredRule] = []
    missing: list[str] = []
    for rule_id in allowlist:
        rule = reg.get(rule_id)
        if rule is None:
            missing.append(rule_id)
            continue
        selected.append(rule)
    if missing:
        raise RuleProtocolError(f"allowlist references unregistered rules: {missing}")
    selected.sort(key=lambda r: (r.priority, r.rule_id))
    return selected


def _is_math16_task(task: Mapping[str, Any]) -> bool:
    """Route Math16 Pilot tasks to classify_math16_response; keep CE115 pilot on classify_response."""
    oracle_type = task.get("oracle_type")
    return isinstance(oracle_type, str) and oracle_type.startswith("math16_")


def _failure_signature(outcome: str | None, details: Mapping[str, Any]) -> str:
    """Stable fingerprint for loop detection beyond coarse outcome labels."""
    if not outcome:
        return "missing_outcome"
    if outcome == "passed":
        return "passed"
    for key in (
        "exception_message",
        "runtime_error",
        "error",
        "message",
        "exception_type",
    ):
        val = details.get(key)
        if val:
            return f"{outcome}|{key}|{val}"
    gates = details.get("evaluation_gates") or details.get("gates")
    if isinstance(gates, Mapping):
        return f"{outcome}|gates|{json.dumps(gates, sort_keys=True, default=str)}"
    return f"{outcome}|detail_keys|{','.join(sorted(str(k) for k in details.keys()))}"


def _maybe_reevaluate(source: str, context: Mapping[str, Any]) -> dict[str, Any]:
    """Re-run the scoring-equivalent evaluator when task+frozen are present.

    Math16 tasks (oracle_type ``math16_*``) use ``classify_math16_response``.
    CE115 pilot / other tasks keep ``math_boundary_pilot.classify_response``.
    Explicit ``context['reevaluator']`` in {``math16``, ``pilot``} overrides auto-route.
    Failures are returned as ``evaluator_error`` (fail-closed); never mutate evaluators.
    """
    task = context.get("task")
    frozen = context.get("frozen")
    if not isinstance(task, Mapping) or not isinstance(frozen, Mapping):
        return {"evaluator_rerun": False}
    override = context.get("reevaluator")
    use_math16 = override == "math16" or (
        override != "pilot" and _is_math16_task(task)
    )
    try:
        if use_math16:
            from core.gencode.research_healer.vendor.evaluator_unavailable import classify_math16_response

            audit_payload = task.get("oracle_payload")
            if not isinstance(audit_payload, Mapping):
                audit_payload = dict(frozen)
            outcome, _code, details = classify_math16_response(
                source,
                frozen_params=dict(frozen),
                audit_oracle_payload=dict(audit_payload),
                task=dict(task),
            )
            backend = "classify_math16_response"
        else:
            from core.gencode.research_healer.vendor.evaluator_unavailable import classify_response

            outcome, _code, details = classify_response(
                source,
                {"oracle_payload": dict(frozen)},
                dict(task),
            )
            backend = "classify_response"
    except Exception as exc:  # noqa: BLE001 — fail-closed to caller
        return {
            "evaluator_rerun": False,
            "evaluator_error": True,
            "evaluator_error_type": type(exc).__name__,
            "evaluator_error_message": str(exc),
            "evaluator_backend": "math16" if use_math16 else "pilot",
        }
    if not isinstance(details, Mapping):
        details = {}
    return {
        "evaluator_rerun": True,
        "evaluator_error": False,
        "evaluator_outcome": outcome,
        "evaluator_details_keys": sorted(details.keys()),
        "failure_signature": _failure_signature(str(outcome), details),
        "evaluator_backend": backend,
    }


def _is_phase_b_evaluator_loop(
    *,
    before_eval: Mapping[str, Any],
    after_eval: Mapping[str, Any],
    rule: _RegisteredRule,
    new_source: str,
    context: Mapping[str, Any],
) -> tuple[bool, str]:
    """True loop only when coarse outcome, failure signature, and rule churn agree.

    Same ``evaluator_outcome`` string alone is NOT sufficient (Math16 false-positive guard).
    """
    before_out = before_eval.get("evaluator_outcome")
    after_out = after_eval.get("evaluator_outcome")
    if before_out is None or after_out is None:
        return False, ""
    if before_out != after_out:
        return False, ""
    if before_out == "passed":
        return False, ""
    before_sig = before_eval.get("failure_signature")
    after_sig = after_eval.get("failure_signature")
    if before_sig is None or after_sig is None or before_sig != after_sig:
        return False, ""
    # True repair churn: the same allowlisted rule would still change the source.
    if not _rule_would_change(new_source, rule, context):
        return False, ""
    return True, f"evaluator_loop_with_verdict_{after_out}"


def _rule_would_change(
    source: str,
    rule: _RegisteredRule,
    context: Mapping[str, Any],
) -> bool:
    applicable, _guards, _reason = rule.is_applicable(source, context)
    if not applicable:
        return False
    triggered, _trig = rule.is_triggered(source, context)
    if not triggered:
        return False
    new_source, _extra, _apply_reason = rule.apply(source, context)
    return new_source != source


def _any_rule_would_change(
    source: str,
    rules: Sequence[_RegisteredRule],
    context: Mapping[str, Any],
) -> bool:
    return any(_rule_would_change(source, rule, context) for rule in rules)


def _build_pass_provenance(
    *,
    pass_index: int,
    chain_position: int | None,
    checked: Sequence[str],
    selected_id: str | None,
    selected_priority: int | None,
    selected_outcome: RuleOutcome | None,
    before_hash: str,
    after_hash: str,
    validation: Mapping[str, Any],
    stopped_after_change: bool,
    stop_reason: str | None,
    final_status: str,
) -> PassProvenance:
    if selected_outcome is not None:
        return PassProvenance(
            pass_index=pass_index,
            chain_position=chain_position,
            candidate_rules_checked=tuple(checked),
            selected_rule_id=selected_id,
            selection_priority=selected_priority,
            applicable=selected_outcome.applicable,
            triggered=selected_outcome.triggered,
            changed=selected_outcome.changed,
            guard_results=dict(selected_outcome.guard_results),
            before_hash=before_hash,
            after_hash=after_hash,
            validation=dict(validation),
            stop_reason=stop_reason if stop_reason is not None else selected_outcome.stop_reason,
            stopped_after_change=stopped_after_change,
            final_status=final_status,
        )
    return PassProvenance(
        pass_index=pass_index,
        chain_position=None,
        candidate_rules_checked=tuple(checked),
        selected_rule_id=None,
        selection_priority=None,
        applicable=False,
        triggered=False,
        changed=False,
        guard_results={},
        before_hash=before_hash,
        after_hash=after_hash,
        validation=dict(validation),
        stop_reason=stop_reason,
        stopped_after_change=False,
        final_status=final_status,
    )


def _finish(
    *,
    source: str,
    current: str,
    input_hash: str,
    final_status: str,
    outcomes: list[RuleOutcome],
    provenance: list[PassProvenance],
    notes: list[str],
    protected: Mapping[str, Any],
    max_passes: int,
    rolled_back: bool = False,
    consumer_may_use_output: bool | None = None,
) -> ResearchHealerResult:
    if consumer_may_use_output is None:
        consumer_may_use_output = final_status not in {"max_passes_exceeded", "error", "validation_failed"}
    # Stamp last provenance final_status to match run result.
    if provenance:
        last = provenance[-1]
        if last.final_status != final_status:
            provenance[-1] = PassProvenance(
                pass_index=last.pass_index,
                chain_position=last.chain_position,
                candidate_rules_checked=last.candidate_rules_checked,
                selected_rule_id=last.selected_rule_id,
                selection_priority=last.selection_priority,
                applicable=last.applicable,
                triggered=last.triggered,
                changed=last.changed,
                guard_results=dict(last.guard_results),
                before_hash=last.before_hash,
                after_hash=last.after_hash,
                validation=dict(last.validation),
                stop_reason=last.stop_reason,
                stopped_after_change=last.stopped_after_change,
                final_status=final_status,
            )
    result = ResearchHealerResult(
        input_source=source,
        output_source=current,
        input_hash=input_hash,
        output_hash=sha256_text(current),
        final_status=final_status,
        rule_outcomes=tuple(outcomes),
        provenance=tuple(provenance),
        real_model_calls=0,
        protected_snapshot=dict(protected),
        notes=tuple(notes),
        max_passes=max_passes,
        execution_policy=dict(FROZEN_EXECUTION_POLICY),
        rolled_back=rolled_back,
        consumer_may_use_output=consumer_may_use_output,
    )
    validate_research_result(result)
    return result


def _fail_closed_max_passes(
    *,
    source: str,
    input_hash: str,
    outcomes: list[RuleOutcome],
    provenance: list[PassProvenance],
    notes: list[str],
    protected: Mapping[str, Any],
    max_passes: int,
) -> ResearchHealerResult:
    """Option A: roll back to original source; consumer must not use partial output."""
    notes = list(notes) + [
        "fail_closed_max_passes_exceeded",
        "transaction_rollback_to_input",
        "consumer_may_use_output=false",
    ]
    return _finish(
        source=source,
        current=source,
        input_hash=input_hash,
        final_status="max_passes_exceeded",
        outcomes=outcomes,
        provenance=provenance,
        notes=notes,
        protected=protected,
        max_passes=max_passes,
        rolled_back=True,
        consumer_may_use_output=False,
    )


def run_research_healer(
    source: str,
    *,
    context: Mapping[str, Any] | None = None,
    allowlist: Sequence[str] = RULE_ALLOWLIST,
    registry: Mapping[str, _RegisteredRule] | None = None,
    protected_snapshot: Mapping[str, Any] | None = None,
    max_passes: int = DEFAULT_MAX_PASSES,
) -> ResearchHealerResult:
    """Run the research allowlist healer under the frozen H5 execution policy."""
    _assert_no_legacy_pipeline()
    if not isinstance(source, str):
        raise RuleProtocolError("source must be a str")
    if not isinstance(max_passes, int) or max_passes < 1:
        raise RuleProtocolError("max_passes must be an explicit int >= 1")

    ctx: dict[str, Any] = dict(context or {})
    protected = dict(protected_snapshot or {})
    input_hash = sha256_text(source)
    current = source
    outcomes: list[RuleOutcome] = []
    provenance: list[PassProvenance] = []
    notes: list[str] = [f"max_passes={max_passes}"]

    rules = select_allowlisted_rules(allowlist=allowlist, registry=registry)

    if not rules:
        empty_hash = sha256_text(current)
        empty_validation = make_parse_validation(current)
        provenance.append(
            _build_pass_provenance(
                pass_index=0,
                chain_position=None,
                checked=(),
                selected_id=None,
                selected_priority=None,
                selected_outcome=None,
                before_hash=empty_hash,
                after_hash=empty_hash,
                validation=empty_validation,
                stopped_after_change=False,
                stop_reason="allowlist_empty" if not allowlist else "no_candidate_selected",
                final_status="no_op",
            )
        )
        notes.append("allowlist_empty" if not allowlist else "no_registered_allowlist_rules")
        return _finish(
            source=source,
            current=current,
            input_hash=input_hash,
            final_status="no_op",
            outcomes=outcomes,
            provenance=provenance,
            notes=notes,
            protected=protected,
            max_passes=max_passes,
        )

    changed_any = False
    chain_change_count = 0
    for pass_index in range(max_passes):
        before = current
        before_hash = sha256_text(before)
        checked: list[str] = []
        selected_id: str | None = None
        selected_priority: int | None = None
        selected_outcome: RuleOutcome | None = None
        stopped_after_change = False
        pass_changed = False
        pass_chain_position: int | None = None
        pass_stop_reason: str | None = "no_candidate_selected"
        pass_validation: dict[str, Any] = make_parse_validation(before)

        # 1. Determine current Phase
        is_syntax_valid = False
        before_err_msg = ""
        before_err_lineno = None
        try:
            ast.parse(before)
            is_syntax_valid = True
        except SyntaxError as exc:
            before_err_msg = str(exc)
            before_err_lineno = exc.lineno

        current_phase = "Phase_B" if is_syntax_valid else "Phase_A"
        notes.append(f"pass_{pass_index}_phase_{current_phase}")

        # Get evaluator state of before (Phase B re-run support)
        before_eval = _maybe_reevaluate(before, ctx)

        for rule in rules:
            # Phase A only runs L1 rules. Phase B only runs L2 rules.
            is_l1 = (rule.layer == "L1")
            if current_phase == "Phase_A" and not is_l1:
                continue
            if current_phase == "Phase_B" and is_l1:
                continue

            checked.append(rule.rule_id)
            applicable, guards, app_reason = rule.is_applicable(before, ctx)
            if not applicable:
                outcome = RuleOutcome(
                    rule_id=rule.rule_id,
                    layer=rule.layer,
                    priority=rule.priority,
                    applicable=False,
                    triggered=False,
                    changed=False,
                    guard_results=dict(guards),
                    reason=app_reason,
                    before_hash=before_hash,
                    after_hash=before_hash,
                    validation={
                        **make_parse_validation(before),
                        "repair_attempted": False,
                    },
                    stop_reason="not_applicable",
                )
                validate_rule_outcome(outcome)
                outcomes.append(outcome)
                continue

            triggered, trig_reason = rule.is_triggered(before, ctx)
            if not triggered:
                outcome = RuleOutcome(
                    rule_id=rule.rule_id,
                    layer=rule.layer,
                    priority=rule.priority,
                    applicable=True,
                    triggered=False,
                    changed=False,
                    guard_results=dict(guards),
                    reason=trig_reason,
                    before_hash=before_hash,
                    after_hash=before_hash,
                    validation={
                        **make_parse_validation(before),
                        "repair_attempted": False,
                    },
                    stop_reason="not_triggered",
                )
                validate_rule_outcome(outcome)
                outcomes.append(outcome)
                continue

            # Triggered ⇒ attempt apply
            new_source, extra_validation, apply_reason = rule.apply(before, ctx)
            after_hash = sha256_text(new_source)
            validation = make_parse_validation(new_source)
            validation.update(dict(extra_validation))
            did_change = new_source != before
            validation["repair_attempted"] = did_change
            
            if did_change:
                after_eval = _maybe_reevaluate(new_source, ctx)
                validation.update(after_eval)
                validation["reparsed_after_change"] = True
            else:
                validation["reparsed_after_change"] = False

            if did_change:
                # Deadlock / Loop Check (Conditions for fallback)
                loop_detected = False
                loop_reason = ""

                # Fail-closed: required revalidator errored → do not accept change.
                if (
                    isinstance(ctx.get("task"), Mapping)
                    and isinstance(ctx.get("frozen"), Mapping)
                    and after_eval.get("evaluator_error")
                ):
                    loop_detected = True
                    loop_reason = (
                        f"revalidator_error_{after_eval.get('evaluator_error_type')}"
                    )
                
                # Check for compile loop (Phase A)
                new_err_msg = ""
                new_err_lineno = None
                try:
                    ast.parse(new_source)
                except SyntaxError as e_syntax:
                    new_err_msg = str(e_syntax)
                    new_err_lineno = e_syntax.lineno

                if (not loop_detected) and current_phase == "Phase_A":
                    if new_err_lineno is not None and new_err_lineno == before_err_lineno and new_err_msg == before_err_msg:
                        loop_detected = True
                        loop_reason = f"compiler_loop_at_line_{new_err_lineno}"
                
                # Check for runtime/contract loop (Phase B) — not outcome-string alone.
                if (
                    (not loop_detected)
                    and current_phase == "Phase_B"
                    and before_eval.get("evaluator_rerun")
                    and after_eval.get("evaluator_rerun")
                ):
                    is_loop, loop_reason = _is_phase_b_evaluator_loop(
                        before_eval=before_eval,
                        after_eval=after_eval,
                        rule=rule,
                        new_source=new_source,
                        context=ctx,
                    )
                    loop_detected = is_loop

                if loop_detected:
                    notes.append(f"pass_{pass_index}_loop_detected_fallback_to_prev_pass: {loop_reason}")
                    pass_validation = dict(validation)
                    pass_validation["loop_detected"] = True
                    pass_validation["phase"] = current_phase
                    provenance.append(
                        _build_pass_provenance(
                            pass_index=pass_index,
                            chain_position=None,
                            checked=checked,
                            selected_id=rule.rule_id,
                            selected_priority=rule.priority,
                            selected_outcome=None,
                            before_hash=before_hash,
                            after_hash=before_hash,
                            validation=pass_validation,
                            stopped_after_change=True,
                            stop_reason=f"fallback_loop_detected_{loop_reason}",
                            final_status="changed" if changed_any else "no_op",
                        )
                    )
                    return _finish(
                        source=source,
                        current=current,
                        input_hash=input_hash,
                        final_status="changed" if changed_any else "no_op",
                        outcomes=outcomes,
                        provenance=provenance,
                        notes=notes,
                        protected=protected,
                        max_passes=max_passes,
                    )

                # No loop: accept change
                current = new_source
                pass_changed = True
                changed_any = True
                chain_change_count += 1
                pass_chain_position = chain_change_count
                stopped_after_change = True
                selected_id = rule.rule_id
                selected_priority = rule.priority
                pass_stop_reason = "changed_stop_pass"
                outcome = RuleOutcome(
                    rule_id=rule.rule_id,
                    layer=rule.layer,
                    priority=rule.priority,
                    applicable=True,
                    triggered=True,
                    changed=True,
                    guard_results=dict(guards),
                    reason=apply_reason,
                    before_hash=before_hash,
                    after_hash=after_hash,
                    validation=validation,
                    stop_reason="changed_stop_pass",
                )
                validate_rule_outcome(outcome)
                outcomes.append(outcome)
                selected_outcome = outcome
                validation["phase"] = current_phase
                pass_validation = dict(validation)
                break

            outcome = RuleOutcome(
                rule_id=rule.rule_id,
                layer=rule.layer,
                priority=rule.priority,
                applicable=True,
                triggered=True,
                changed=False,
                guard_results=dict(guards),
                reason=apply_reason,
                before_hash=before_hash,
                after_hash=before_hash,
                validation=validation,
                stop_reason="no_change",
            )
            validate_rule_outcome(outcome)
            outcomes.append(outcome)
            pass_stop_reason = "stable_no_further_change"

        after_hash = sha256_text(current)
        if not pass_changed and selected_outcome is None:
            pass_stop_reason = "no_candidate_selected" if checked else "allowlist_empty"
            pass_validation = make_parse_validation(current)

        pass_validation = dict(pass_validation)
        pass_validation["phase"] = current_phase

        provisional_status = "changed" if changed_any else "no_op"
        provenance.append(
            _build_pass_provenance(
                pass_index=pass_index,
                chain_position=pass_chain_position,
                checked=checked,
                selected_id=selected_id,
                selected_priority=selected_priority,
                selected_outcome=selected_outcome,
                before_hash=before_hash,
                after_hash=after_hash,
                validation=pass_validation,
                stopped_after_change=stopped_after_change,
                stop_reason=pass_stop_reason,
                final_status=provisional_status,
            )
        )

        if pass_changed:
            notes.append(f"pass_{pass_index}_stopped_after_first_changed_rule")
            if pass_index + 1 >= max_passes:
                if _any_rule_would_change(current, rules, ctx):
                    return _fail_closed_max_passes(
                        source=source,
                        input_hash=input_hash,
                        outcomes=outcomes,
                        provenance=provenance,
                        notes=notes,
                        protected=protected,
                        max_passes=max_passes,
                    )
                return _finish(
                    source=source,
                    current=current,
                    input_hash=input_hash,
                    final_status="changed" if changed_any else "no_op",
                    outcomes=outcomes,
                    provenance=provenance,
                    notes=notes,
                    protected=protected,
                    max_passes=max_passes,
                )
            continue

        notes.append(f"pass_{pass_index}_stable_no_change")
        return _finish(
            source=source,
            current=current,
            input_hash=input_hash,
            final_status="changed" if changed_any else "no_op",
            outcomes=outcomes,
            provenance=provenance,
            notes=notes,
            protected=protected,
            max_passes=max_passes,
        )

    return _finish(
        source=source,
        current=current,
        input_hash=input_hash,
        final_status="changed" if changed_any else "no_op",
        outcomes=outcomes,
        provenance=provenance,
        notes=notes,
        protected=protected,
        max_passes=max_passes,
    )


class MathHealerRunner:
    """Allowlist-facing research runner entry point (H5 frozen policy)."""

    allowlist: tuple[str, ...] = RULE_ALLOWLIST

    def __init__(
        self,
        *,
        allowlist: Sequence[str] | None = None,
        registry: Mapping[str, _RegisteredRule] | None = None,
        max_passes: int = DEFAULT_MAX_PASSES,
    ) -> None:
        if not isinstance(max_passes, int) or max_passes < 1:
            raise RuleProtocolError("max_passes must be an explicit int >= 1")
        self.allowlist = tuple(RULE_ALLOWLIST if allowlist is None else allowlist)
        self.registry = registry
        self.max_passes = max_passes

    def run(
        self,
        source: str,
        *,
        context: Mapping[str, Any] | None = None,
        protected_snapshot: Mapping[str, Any] | None = None,
    ) -> ResearchHealerResult:
        return run_research_healer(
            source,
            context=context,
            allowlist=self.allowlist,
            registry=self.registry,
            protected_snapshot=protected_snapshot,
            max_passes=self.max_passes,
        )


def load_regression_manifest(path: str | Path) -> dict[str, Any]:
    """Load cumulative regression manifest JSON."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuleProtocolError("manifest must be a JSON object")
    required = ("manifest_id", "schema_version", "cases")
    missing = [k for k in required if k not in data]
    if missing:
        raise RuleProtocolError(f"manifest missing keys: {missing}")
    if not isinstance(data["cases"], list):
        raise RuleProtocolError("manifest.cases must be a list")
    return data


def iter_manifest_cases(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return production cases in stable order (excludes exploratory drafts)."""
    cases = list(manifest["cases"])
    case_fields = (
        "case_id",
        "source_artifact",
        "expected_applicable_rules",
        "expected_triggered_rules",
        "expected_changed_rules",
        "expected_final_status",
        "protected_fields",
    )
    for case in cases:
        missing = [k for k in case_fields if k not in case]
        if missing:
            raise RuleProtocolError(
                f"case {case.get('case_id')!r} missing fields: {missing}"
            )
    return cases


def iter_exploratory_cases(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return paused/exploratory cases (not production allowlist expectations)."""
    cases = list(manifest.get("exploratory_cases") or [])
    for case in cases:
        if "case_id" not in case or "source_artifact" not in case:
            raise RuleProtocolError(
                f"exploratory case missing case_id/source_artifact: {case!r}"
            )
        if case.get("production_approved") is True:
            raise RuleProtocolError(
                f"exploratory case {case['case_id']!r} must not set production_approved=True"
            )
    return cases


def experimental_allowlist() -> tuple[str, ...]:
    """Explicit allowlist for paused experimental rules (tests / probes only)."""
    return (L1_COMMENT_ONLY_IF_INSERT_PASS, *RULE_ALLOWLIST)
