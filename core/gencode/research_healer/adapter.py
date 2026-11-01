# -*- coding: utf-8 -*-
"""GenCode V3 adapter for the vendored MathProject AST Research Healer.

Scope: Python source written by an AI model (the capability AI fill coder
files).  System-built V3 scaffolds / Phase 3 wrappers are out of scope.

Pipeline per source (zero model calls):
  1. V3 preflight: extract the single fenced Markdown code block verbatim.
  2. Vendored research runner under the frozen H5 policy with
     ``V3_PRODUCTION_ALLOWLIST`` (currently empty: no research rule has a V3
     safety proof).
  3. Research rules outside the allowlist are probed for evidence only; their
     output is never used.
  4. Re-parse, safety scan and edit-scope guards; anything unproven abstains
     and the original source is returned unchanged.

Modes (``GENCODE_V3_HEALER_MODE``): off (default, never called), shadow
(evidence only), repair (an accepted repair is handed to the existing V3
validators, which still decide).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from core.gencode.research_healer.eligibility import (
    ELIGIBILITY_BY_ID,
    PREFLIGHT_FENCE_RULE_ID,
    RESEARCH_RULE_IDS,
    TIER_PREFLIGHT,
    V3_PRODUCTION_ALLOWLIST,
)
from core.gencode.research_healer.provenance import RESEARCH_COMMIT
from core.gencode.research_healer.structure import (
    grouping_alternatives,
    parse_status,
    safety_findings,
    structural_diff,
)
from core.gencode.research_healer.vendor.protocol import research_result_to_dict
from core.gencode.research_healer.vendor.runner import (
    EXPERIMENTAL_RULE_REGISTRY,
    RULE_REGISTRY,
    run_research_healer,
)

HEALER_MODE_ENV = "GENCODE_V3_HEALER_MODE"
MODE_OFF = "off"
MODE_SHADOW = "shadow"
MODE_REPAIR = "repair"
VALID_MODES = (MODE_OFF, MODE_SHADOW, MODE_REPAIR)

STATUS_UNCHANGED = "UNCHANGED"
STATUS_REPAIRED = "REPAIRED"
STATUS_ABSTAINED = "ABSTAINED"
STATUS_REJECTED = "REJECTED"

FAILURE_PARSES = "parses"
FAILURE_SYNTAX = "syntax_error"
FAILURE_EMPTY = "empty_source"

ADAPTER_VERSION = "v3.research_healer.adapter.1"
MAX_PROBE_SOURCE_CHARS = 50_000
EVIDENCE_FILE_NAME = "research_healer_evidence.jsonl"

_FENCE_LINE_RE = re.compile(r"^[ \t]*```[ \t]*([A-Za-z0-9_+.\-]*)[ \t]*$")
_PYTHON_FENCE_TAGS = frozenset({"", "python", "py", "python3"})
_CODE_LIKE_LINE_RE = re.compile(
    r"^\s*(def|class|import|from|return|if|elif|else|for|while|try|except|with|@)\b"
    r"|^\s*[A-Za-z_][\w.]*(\[[^\]]*\])?\s*(=|\+=|-=|\*=|/=)(?!=)"
)
_GUARD_KEYS = (
    "math_operator_changed",
    "control_flow_changed",
    "function_names_changed",
    "constants_changed",
    "code_deleted",
)


def resolve_healer_mode(env: Mapping[str, str] | None = None) -> str:
    raw = str((os.environ if env is None else env).get(HEALER_MODE_ENV, "") or "").strip().lower()
    return raw if raw in VALID_MODES else MODE_OFF


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def ruleset_version(allowlist: Sequence[str] = V3_PRODUCTION_ALLOWLIST) -> str:
    return f"ce115_h5_audit|v3_allowlist:{'+'.join(allowlist) or 'empty'}"


@dataclass
class ResearchHealerV3Result:
    status: str
    mode: str
    skill_id: str
    component_id: str
    original_sha256: str
    original_code: str = field(repr=False)
    textbook_example_id: int | None = None
    problem_type_id: str = ""
    repaired_code: str | None = field(default=None, repr=False)
    repaired_sha256: str | None = None
    failure_category: str = ""
    reason: str = ""
    rounds: int = 0
    rules_applied: list[dict[str, Any]] = field(default_factory=list)
    attempts: list[dict[str, Any]] = field(default_factory=list)
    certificates: list[dict[str, Any]] = field(default_factory=list)
    certificate_status: str = "none"
    validation: dict[str, Any] = field(default_factory=dict)
    safety_findings: list[str] = field(default_factory=list)
    probe: list[dict[str, Any]] = field(default_factory=list)
    research_run: dict[str, Any] = field(default_factory=dict)
    semantic_preservation_proven: bool = False
    duration_ms: float = 0.0
    real_model_calls: int = 0
    applied_to_pipeline: bool = False
    post_repair_gates: str = "not_run"
    evidence_path: str | None = None
    telemetry: dict[str, Any] = field(default_factory=dict)
    adapter_version: str = ADAPTER_VERSION
    ruleset_version: str = field(default_factory=ruleset_version)
    research_commit: str = RESEARCH_COMMIT

    @property
    def final_code(self) -> str:
        if self.status == STATUS_REPAIRED and self.repaired_code is not None:
            return self.repaired_code
        return self.original_code

    def summary(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("original_code", None)
        data.pop("repaired_code", None)
        return data

    def mark_post_repair_failure(self, stage: str, error: str) -> None:
        self.applied_to_pipeline = False
        self.post_repair_gates = f"failed:{stage}:{str(error)[:300]}"


# ---------------------------------------------------------------------------
# V3 preflight: unique Markdown fence extraction
# ---------------------------------------------------------------------------


def extract_unique_python_fence(source: str) -> tuple[str | None, str, dict[str, Any]]:
    """Return (inner code, reason, details); inner code is a verbatim substring of ``source``."""
    lines = source.splitlines(keepends=True)
    fences = [i for i, line in enumerate(lines) if _FENCE_LINE_RE.match(line.rstrip("\r\n"))]
    if not fences:
        return None, "no_markdown_fence", {}
    if len(fences) == 1:
        return None, "unterminated_markdown_fence", {"fence_lines": 1}
    if len(fences) > 2:
        return None, "multiple_markdown_fences", {"fence_lines": len(fences)}
    open_i, close_i = fences
    open_tag = _FENCE_LINE_RE.match(lines[open_i].rstrip("\r\n")).group(1).lower()
    close_tag = _FENCE_LINE_RE.match(lines[close_i].rstrip("\r\n")).group(1)
    if open_tag not in _PYTHON_FENCE_TAGS:
        return None, "non_python_fence", {"fence_tag": open_tag[:20]}
    if close_tag:
        return None, "malformed_closing_fence", {}
    inner = "".join(lines[open_i + 1 : close_i])
    if not inner.strip():
        return None, "empty_fenced_block", {}
    outside = lines[:open_i] + lines[close_i + 1 :]
    code_like = sum(1 for line in outside if line.strip() and _CODE_LIKE_LINE_RE.match(line))
    if code_like:
        return None, "code_like_text_outside_fence", {"code_like_lines": code_like}
    if inner not in source:
        return None, "extraction_not_verbatim", {}
    return inner, "unique_python_fence_extracted", {
        "open_line": open_i + 1,
        "close_line": close_i + 1,
        "outside_nonblank_lines": sum(1 for line in outside if line.strip()),
    }


# ---------------------------------------------------------------------------
# Research rules
# ---------------------------------------------------------------------------


def _registry() -> dict[str, Any]:
    return {**EXPERIMENTAL_RULE_REGISTRY, **RULE_REGISTRY}


def probe_research_rules(code: str, rule_ids: Sequence[str] = RESEARCH_RULE_IDS) -> list[dict[str, Any]]:
    """Evaluate research rules for evidence only; the proposed source is never returned."""
    registry = _registry()
    out: list[dict[str, Any]] = []
    for rule_id in rule_ids:
        rule = registry.get(rule_id)
        meta = ELIGIBILITY_BY_ID.get(rule_id)
        entry: dict[str, Any] = {
            "rule_id": rule_id,
            "tier": meta.tier if meta else "unknown",
            "v3_status": meta.v3_status if meta else "UNKNOWN",
            "applicable": False,
            "triggered": False,
            "would_change": False,
        }
        if rule is None:
            entry["reason"] = "rule_not_registered"
            out.append(entry)
            continue
        if len(code) > MAX_PROBE_SOURCE_CHARS:
            entry["reason"] = "probe_skipped_source_too_large"
            out.append(entry)
            continue
        try:
            applicable, _guards, reason = rule.is_applicable(code, {})
            entry["applicable"] = bool(applicable)
            entry["reason"] = str(reason)
            if applicable:
                triggered, reason = rule.is_triggered(code, {})
                entry["triggered"] = bool(triggered)
                entry["reason"] = str(reason)
                if triggered:
                    proposed, _extra, reason = rule.apply(code, {})
                    entry["reason"] = str(reason)
                    entry["would_change"] = proposed != code
                    if proposed != code:
                        entry["proposed_sha256"] = sha256_text(proposed)
                        entry["proposed_parses"] = parse_status(proposed)["parses"]
                        entry["diff"] = structural_diff(code, proposed)
                        entry["grouping_alternatives"] = grouping_alternatives(code, proposed)
        except Exception as exc:  # noqa: BLE001 - probe errors are evidence, never failures
            entry["reason"] = f"probe_error:{type(exc).__name__}"
        out.append(entry)
    return out


def _guard_research_change(before: str, after: str) -> tuple[bool, str, dict[str, Any]]:
    if not parse_status(after)["parses"]:
        return False, "repaired_source_does_not_parse", {}
    diff = structural_diff(before, after)
    for key in _GUARD_KEYS:
        if diff.get(key):
            return False, f"edit_scope_violation:{key}", diff
    alternatives = grouping_alternatives(before, after)
    if alternatives is not None and alternatives != 1:
        return False, "grouping_ambiguous", {**diff, "grouping_alternatives": alternatives}
    if alternatives is None and not diff.get("delimiter_only"):
        return False, "edit_not_single_delimiter_insert", diff
    return True, "edit_within_scope", {**diff, "grouping_alternatives": alternatives}


# ---------------------------------------------------------------------------
# Core entry point
# ---------------------------------------------------------------------------


def _finish(result: ResearchHealerV3Result, status: str, reason: str, started: float, repaired: str | None = None):
    result.status = status
    result.reason = reason
    if status == STATUS_REPAIRED and repaired is not None:
        result.repaired_code = repaired
        result.repaired_sha256 = sha256_text(repaired)
        result.certificate_status = "verified"
    else:
        result.repaired_code = None
        result.repaired_sha256 = None
        result.certificate_status = "none"
    result.duration_ms = round((time.perf_counter() - started) * 1000, 3)
    return result


def heal_ai_python_source(
    source: str,
    *,
    skill_id: str,
    component_id: str,
    mode: str = MODE_SHADOW,
    problem_type_id: str = "",
    textbook_example_id: int | None = None,
    allowlist: Sequence[str] = V3_PRODUCTION_ALLOWLIST,
    probe: bool = True,
) -> ResearchHealerV3Result:
    """Heal one AI-written Python source; returns the original unless every guard passes."""
    started = time.perf_counter()
    text = source if isinstance(source, str) else ""
    result = ResearchHealerV3Result(
        status=STATUS_ABSTAINED,
        mode=mode,
        skill_id=str(skill_id),
        component_id=str(component_id),
        original_sha256=sha256_text(text),
        original_code=text,
        textbook_example_id=textbook_example_id,
        problem_type_id=str(problem_type_id or ""),
        ruleset_version=ruleset_version(allowlist),
    )
    if not isinstance(source, str) or not source.strip():
        result.failure_category = FAILURE_EMPTY
        return _finish(result, STATUS_ABSTAINED, "empty_source", started)

    before_parse = parse_status(text)
    result.validation["before_parse"] = before_parse
    if before_parse["parses"]:
        result.failure_category = FAILURE_PARSES
        result.safety_findings = safety_findings(text)
        result.research_run = _research_run(text, allowlist)
        return _finish(result, STATUS_UNCHANGED, "source_already_parses", started)

    result.failure_category = FAILURE_SYNTAX
    result.rounds = 1
    current = text
    applied: list[str] = []

    inner, fence_reason, fence_details = extract_unique_python_fence(text)
    fence_attempt: dict[str, Any] = {
        "round": 1,
        "rule_id": PREFLIGHT_FENCE_RULE_ID,
        "research_tier": TIER_PREFLIGHT,
        "reason": fence_reason,
        "details": fence_details,
    }
    if inner is None:
        fence_attempt["decision"] = "ABSTAIN"
    else:
        fence_attempt.update(
            {
                "decision": "ACCEPT",
                "before_sha256": sha256_text(current),
                "after_sha256": sha256_text(inner),
                "verbatim_substring": True,
            }
        )
        result.certificates.append(
            {
                "rule_id": PREFLIGHT_FENCE_RULE_ID,
                "decision": "ACCEPT",
                "proof": "output_is_verbatim_substring_of_ai_response",
                "before_source_sha256": sha256_text(current),
                "after_source_sha256": sha256_text(inner),
                "expected_answer_not_read": True,
                "model_calls": 0,
            }
        )
        current = inner
        applied.append(PREFLIGHT_FENCE_RULE_ID)
    result.attempts.append(fence_attempt)

    research_input = current
    research_input_parses = parse_status(research_input)["parses"]
    if not research_input_parses:
        if probe:
            result.probe = probe_research_rules(research_input)
            for entry in result.probe:
                result.attempts.append(
                    {
                        "round": 1,
                        "rule_id": entry["rule_id"],
                        "research_tier": entry["tier"],
                        "decision": "DISABLED",
                        "reason": "rule_disabled_in_v3:" + ("would_change" if entry["would_change"] else "no_candidate"),
                    }
                )
        run = _research_run(research_input, allowlist)
        result.research_run = run
        if run.get("source_changed") and run.get("consumer_may_use_output"):
            candidate = run.pop("_output_source")
            ok, guard_reason, guard_diff = _guard_research_change(research_input, candidate)
            rule_id = run.get("selected_rule_id") or "unknown"
            attempt = {
                "round": 1,
                "rule_id": rule_id,
                "research_tier": ELIGIBILITY_BY_ID[rule_id].tier if rule_id in ELIGIBILITY_BY_ID else "unknown",
                "decision": "ACCEPT" if ok else "REJECT",
                "reason": guard_reason,
                "diff": guard_diff,
            }
            result.attempts.append(attempt)
            if not ok:
                result.rules_applied = [{"rule_id": r, "research_tier": ELIGIBILITY_BY_ID[r].tier} for r in applied]
                return _finish(result, STATUS_REJECTED, f"research_change_rejected:{guard_reason}", started)
            result.certificates.append(
                {
                    "rule_id": rule_id,
                    "decision": "ACCEPT",
                    "proof": "single_delimiter_insert_with_unique_grouping",
                    "before_source_sha256": sha256_text(research_input),
                    "after_source_sha256": sha256_text(candidate),
                    "expected_answer_not_read": True,
                    "model_calls": 0,
                }
            )
            current = candidate
            applied.append(rule_id)
        run.pop("_output_source", None)
    else:
        result.research_run = _research_run(research_input, allowlist)
        result.research_run.pop("_output_source", None)

    result.rules_applied = [
        {"rule_id": r, "research_tier": ELIGIBILITY_BY_ID[r].tier if r in ELIGIBILITY_BY_ID else "unknown"}
        for r in applied
    ]
    after_parse = parse_status(current)
    result.validation["after_parse"] = after_parse
    if current == text or not applied:
        return _finish(result, STATUS_ABSTAINED, "no_rule_produced_unique_safe_candidate", started)
    if not after_parse["parses"]:
        return _finish(result, STATUS_ABSTAINED, "residual_syntax_error_after_preflight", started)
    result.safety_findings = safety_findings(current)
    if result.safety_findings:
        return _finish(result, STATUS_REJECTED, f"unsafe_construct:{result.safety_findings[0]}", started)
    again, _, _ = extract_unique_python_fence(current)
    if again is not None:
        return _finish(result, STATUS_REJECTED, "non_idempotent_preflight", started)
    result.validation["structure"] = structural_diff(inner if inner is not None else text, current)
    result.semantic_preservation_proven = applied == [PREFLIGHT_FENCE_RULE_ID]
    return _finish(result, STATUS_REPAIRED, "repaired_pending_existing_v3_validation", started, repaired=current)


def _research_run(code: str, allowlist: Sequence[str]) -> dict[str, Any]:
    """Run the vendored runner under the frozen policy; ``_output_source`` is internal only."""
    try:
        res = run_research_healer(code, context={}, allowlist=tuple(allowlist), max_passes=max(1, len(allowlist)))
    except Exception as exc:  # noqa: BLE001 - fail closed
        return {"final_status": "error", "error": f"{type(exc).__name__}:{str(exc)[:200]}", "source_changed": False}
    data = research_result_to_dict(res)
    selected = next((p["selected_rule_id"] for p in data["provenance"] if p.get("changed")), None)
    summary = {
        "final_status": data["final_status"],
        "source_changed": bool(data["source_changed"]),
        "consumer_may_use_output": bool(data["consumer_may_use_output"]),
        "rolled_back": bool(data["rolled_back"]),
        "real_model_calls": data["real_model_calls"],
        "max_passes": data["max_passes"],
        "policy_id": data["execution_policy"].get("policy_id"),
        "input_hash": data["input_hash"],
        "output_hash": data["output_hash"],
        "selected_rule_id": selected,
        "stop_reasons": [p.get("stop_reason") for p in data["provenance"]],
        "notes": data["notes"],
    }
    if data["source_changed"] and data["consumer_may_use_output"]:
        summary["_output_source"] = res.output_source
    return summary


# ---------------------------------------------------------------------------
# Capability AI fill integration (coder files)
# ---------------------------------------------------------------------------


def _append_evidence(job_dir: Path, record: Mapping[str, Any]) -> str:
    path = Path(job_dir) / EVIDENCE_FILE_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return str(path)


def heal_coder_files(
    files: list[dict[str, Any]],
    *,
    skill_id: str,
    job_id: str,
    job_dir: str | Path,
    round_no: int,
    mode: str | None = None,
    conn: Any = None,
    telemetry_context: Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[ResearchHealerV3Result]]:
    """Return (files for the existing validator, results); off mode returns ``files`` untouched."""
    active = mode if mode in VALID_MODES else resolve_healer_mode()
    if active == MODE_OFF:
        return files, []
    from core.gencode.v3_healer_telemetry import now_iso, record_attempt_safely

    run_id = f"{job_id}:coder_round_{int(round_no)}"
    out: list[dict[str, Any]] = []
    results: list[ResearchHealerV3Result] = []
    for item in files:
        path = str(item.get("path") or "")
        if not path.endswith(".py"):
            out.append(item)
            continue
        content = str(item.get("content") or "")
        component_id = f"coder:{path}"
        started_at = now_iso()
        try:
            result = heal_ai_python_source(content, skill_id=skill_id, component_id=component_id, mode=active)
        except Exception as exc:  # noqa: BLE001 - adapter bugs never alter the AI output
            result = ResearchHealerV3Result(
                status=STATUS_REJECTED,
                mode=active,
                skill_id=skill_id,
                component_id=component_id,
                original_sha256=sha256_text(content),
                original_code=content,
                reason=f"adapter_internal_error:{type(exc).__name__}",
            )
        result.applied_to_pipeline = active == MODE_REPAIR and result.status == STATUS_REPAIRED
        try:
            result.evidence_path = _append_evidence(
                Path(job_dir),
                {"generation_run_id": run_id, "path": path, **result.summary()},
            )
        except Exception as exc:  # noqa: BLE001
            result.evidence_path = None
            if result.applied_to_pipeline:
                result.applied_to_pipeline = False
                result.post_repair_gates = f"not_applied:evidence_write_failed:{type(exc).__name__}"
        if conn is not None and result.status != STATUS_UNCHANGED:
            record_attempt_safely(
                conn,
                result,
                generation_run_id=run_id,
                context=telemetry_context,
                started_at=started_at,
                finished_at=now_iso(),
            )
        out.append({**item, "content": result.final_code} if result.applied_to_pipeline else item)
        results.append(result)
    return out, results


def record_coder_gate(conn: Any, results: Sequence[ResearchHealerV3Result], *, passed: bool, blockers: Sequence[str]) -> None:
    """Record the existing official-compatibility verdict for every applied repair."""
    from core.gencode.v3_healer_telemetry import record_gate_safely

    for result in results:
        if not result.applied_to_pipeline:
            continue
        if passed:
            result.post_repair_gates = "passed"
        else:
            result.mark_post_repair_failure("official_compatibility", ";".join(str(b) for b in blockers)[:300])
        record_gate_safely(conn, result, passed=passed, stage=None if passed else "official_compatibility")
