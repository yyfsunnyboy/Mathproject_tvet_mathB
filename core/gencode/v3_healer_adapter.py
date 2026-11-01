# -*- coding: utf-8 -*-
"""GenCode V3 component code healer (Aggressive Healer v2, V3-scoped port).

RETIRED FROM V3: no V3 pipeline calls this module; the only V3 repair
mechanism is ``core.gencode.research_healer``.  Physical deletion is pending
until its remaining test-only users migrate.

Former entry point for the V3 shadow bridge: only a component whose generate.py
failed the seed-42 integrity execution can reach this adapter.  The adapter
never mutates its input, never reads the expected answer, tries at most one
deterministic candidate per rule, and returns the original code unless every
guard and the isolated validation pass.

Modes (``GENCODE_V3_HEALER_MODE``):
  off     never called (default; unknown values fall back to off)
  shadow  heal + validate in isolation, record evidence, keep original outcome
  repair  as shadow, and hand an accepted repair back to the pipeline, which
          must re-run every V3 gate on it
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

from core.gencode.v3_healer_rules import (
    DISABLED_RULE_IDS,
    EXECUTABLE_RULE_ORDER,
    FAILURE_NAME,
    FAILURE_SYNTAX,
    FULLWIDTH_PUNCT_MAP,
    RESEARCH_COMMIT,
    RULES_BY_ID,
    SCOPE_INSERT_CLOSING_DELIMITER,
    SCOPE_INSERT_PASS_LINE,
    SCOPE_INSERT_STDLIB_IMPORT,
    SCOPE_REPLACE_FULLWIDTH,
    STDLIB_IMPORT_MAP,
    V3_RULESET_VERSION,
    V3HealerRuleSpec,
    split_line_comment,
    string_or_comment_mask,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HEALER_MODE_ENV = "GENCODE_V3_HEALER_MODE"
MODE_OFF = "off"
MODE_SHADOW = "shadow"
MODE_REPAIR = "repair"
VALID_MODES = (MODE_OFF, MODE_SHADOW, MODE_REPAIR)

STATUS_UNCHANGED = "UNCHANGED"
STATUS_REPAIRED = "REPAIRED"
STATUS_ABSTAINED = "ABSTAINED"
STATUS_REJECTED = "REJECTED"

ADAPTER_VERSION = "v3.healer.adapter.1"
DEFAULT_MAX_ROUNDS = 4
DEFAULT_MAX_VALIDATION_CALLS = 2
DEFAULT_VALIDATION_TIMEOUT_S = 240
ISOLATED_VALIDATION_SEEDS: tuple[int, ...] = (7, 42, 137, 256, 999)
NEGATIVE_CHECKER_PROBE = "__v3_healer_negative_probe__"

PROTECTED_COMPONENT_STATUSES = frozenset(
    {"verified", "publishable", "published", "runtime_ready", "promoted"}
)
_PRODUCTION_DIRS = (PROJECT_ROOT / "agent_skills_v3", PROJECT_ROOT / "skills")
_PROTECTED_LINE_RE = re.compile(
    r"\b(correct_answer|canonical_answer|semantic_answer|display_answer|expected_answer|answers?"
    r"|answer_contract|checker|checker_key|checker_type|equivalence|oracle\w*)\b",
    re.IGNORECASE,
)
_EXEC_ERROR_RE = re.compile(r"^execution_error:([A-Za-z_][\w.]*):(.*)$", re.DOTALL)
_NAME_ERROR_RE = re.compile(r"name '([^']+)' is not defined")
REQUIRED_CERT_FIELDS = (
    "rule_id",
    "decision",
    "contract_sha256",
    "candidate_count",
    "expected_answer_not_read",
    "evaluator_result_not_read",
    "candidate_trial_count",
    "before_source_sha256",
    "after_source_sha256",
)

Validator = Callable[[str], Mapping[str, Any]]


def resolve_healer_mode(env: Mapping[str, str] | None = None) -> str:
    raw = str((os.environ if env is None else env).get(HEALER_MODE_ENV, "") or "").strip().lower()
    return raw if raw in VALID_MODES else MODE_OFF


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)


@dataclass
class V3HealerRequest:
    component_id: str
    textbook_example_id: int
    candidate_code: str
    failure_diagnostics: Mapping[str, Any]
    operation_contract: Mapping[str, Any]
    allowed_rules: tuple[str, ...] | None = None
    component_status: str = "draft"
    source_path: str | None = None
    max_rounds: int = DEFAULT_MAX_ROUNDS
    max_validation_calls: int = DEFAULT_MAX_VALIDATION_CALLS


@dataclass
class V3HealerResult:
    status: str
    mode: str
    component_id: str
    textbook_example_id: int
    skill_id: str
    original_sha256: str
    contract_sha256: str
    original_code: str = field(repr=False)
    repaired_code: str | None = field(default=None, repr=False)
    repaired_sha256: str | None = None
    failure_category: str = ""
    reason: str = ""
    rules_applied: list[dict[str, Any]] = field(default_factory=list)
    attempts: list[dict[str, Any]] = field(default_factory=list)
    certificates: list[dict[str, Any]] = field(default_factory=list)
    validation_results: list[dict[str, Any]] = field(default_factory=list)
    sha_history: list[str] = field(default_factory=list)
    rounds: int = 0
    cycle_detected: bool = False
    retry_limit_hit: bool = False
    applied_to_pipeline: bool = False
    post_repair_gates: str = "not_run"
    evidence_path: str | None = None
    telemetry: dict[str, Any] = field(default_factory=dict)
    adapter_version: str = ADAPTER_VERSION
    ruleset_version: str = V3_RULESET_VERSION
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

    def evidence(self) -> dict[str, Any]:
        data = self.summary()
        data["original_code"] = self.original_code
        data["repaired_code"] = self.repaired_code
        return data

    def mark_post_repair_failure(self, stage: str, error: str) -> None:
        self.applied_to_pipeline = False
        self.post_repair_gates = f"failed:{stage}:{str(error)[:500]}"


# ---------------------------------------------------------------------------
# Classification / diagnostics
# ---------------------------------------------------------------------------


def parse_execution_error(execution_error: str) -> dict[str, Any]:
    text = str(execution_error or "")
    diag: dict[str, Any] = {"stage": "integrity_exec_seed_42", "execution_error": text}
    match = _EXEC_ERROR_RE.match(text)
    if match:
        diag["exception_type"] = match.group(1)
        diag["exception_message"] = match.group(2)
    elif text == "missing_generate_function":
        diag["exception_type"] = "MissingGenerateFunction"
    return diag


def classify_failure(code: str, diagnostics: Mapping[str, Any]) -> str:
    try:
        compile(code, "<v3_component_generate>", "exec")
    except SyntaxError:
        return FAILURE_SYNTAX
    except (ValueError, TypeError):
        return "not_compilable:other"
    exc_type = str(diagnostics.get("exception_type") or "").strip()
    if exc_type == "NameError":
        return FAILURE_NAME
    if exc_type:
        return f"runtime:{exc_type}"
    if diagnostics.get("blockers"):
        return "gate_blockers"
    return "compiles"


def _rule_context(diagnostics: Mapping[str, Any]) -> dict[str, Any]:
    name = None
    if str(diagnostics.get("exception_type") or "") == "NameError":
        match = _NAME_ERROR_RE.search(str(diagnostics.get("exception_message") or ""))
        name = match.group(1) if match else None
    return {"name_error_name": name}


def _diagnostics_from_validation(validation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "exception_type": validation.get("exception_type"),
        "exception_message": validation.get("exception_message"),
        "blockers": list(validation.get("blockers") or []),
    }


# ---------------------------------------------------------------------------
# Contract and protection guards
# ---------------------------------------------------------------------------

_CODE_ANCHORS: tuple[tuple[str, str, Callable[[str], Any]], ...] = (
    (r"^TEXTBOOK_EXAMPLE_ID\s*=\s*(\d+)\s*$", "textbook_example_id", int),
    (r"^SKILL_ID\s*=\s*\"([^\"]*)\"\s*$", "skill_id", str),
    (r"^FIXED_DOMAIN_KEY\s*=\s*\"([^\"]*)\"\s*$", "fixed_domain_key", str),
    (r"^DOMAIN_OPERATION\s*=\s*\"([^\"]*)\"\s*$", "domain_operation", str),
    (r"\"fixed_domain_key\":\s*\"([^\"]+)\"", "fixed_domain_key", str),
    (r"\bdomain_operation=\"([^\"]+)\"", "domain_operation", str),
)


def check_component_contract(code: str, request: V3HealerRequest) -> tuple[bool, str]:
    contract = request.operation_contract or {}
    for key in ("skill_id", "fixed_domain_key", "domain_operation"):
        if not str(contract.get(key) or "").strip():
            return False, f"contract_field_missing:{key}"
    if str(request.component_id) != f"src_{int(request.textbook_example_id)}":
        return False, "contract_mismatch:component_id"
    expected = {
        "textbook_example_id": int(request.textbook_example_id),
        "skill_id": str(contract["skill_id"]),
        "fixed_domain_key": str(contract["fixed_domain_key"]),
        "domain_operation": str(contract["domain_operation"]),
    }
    saw_example_anchor = False
    for pattern, key, cast in _CODE_ANCHORS:
        for match in re.finditer(pattern, code, re.MULTILINE):
            if key == "textbook_example_id":
                saw_example_anchor = True
            if cast(match.group(1)) != expected[key]:
                return False, f"contract_mismatch:{key}"
    if not saw_example_anchor:
        return False, "contract_anchor_missing:TEXTBOOK_EXAMPLE_ID"
    return True, "contract_ok"


def _is_production_path(path: str | None) -> bool:
    if not path:
        return False
    resolved = Path(os.path.abspath(path))
    for root in _PRODUCTION_DIRS:
        try:
            resolved.relative_to(Path(os.path.abspath(root)))
            return True
        except ValueError:
            continue
    return False


def _line_at(code: str, pos: int) -> str:
    start = code.rfind("\n", 0, pos) + 1
    end = code.find("\n", pos)
    return code[start : (len(code) if end < 0 else end)]


def verify_patch(before: str, after: str, edit_scope: str) -> tuple[bool, str, dict[str, Any]]:
    """Independent check that ``after`` differs from ``before`` only within ``edit_scope``."""
    changed: list[int] = []
    if edit_scope == SCOPE_INSERT_CLOSING_DELIMITER:
        if len(after) != len(before) + 1:
            return False, "scope_violation:length", {}
        i = next((k for k in range(len(before)) if before[k] != after[k]), len(before))
        if after[:i] != before[:i] or after[i + 1 :] != before[i:] or after[i] not in ")]}":
            return False, "scope_violation:not_single_closing_delimiter_insert", {}
        changed = [i]
    elif edit_scope == SCOPE_REPLACE_FULLWIDTH:
        if len(after) != len(before):
            return False, "scope_violation:length", {}
        for k, (a, b) in enumerate(zip(before, after)):
            if a == b:
                continue
            if FULLWIDTH_PUNCT_MAP.get(a) != b:
                return False, "scope_violation:non_fullwidth_replacement", {"pos": k}
            changed.append(k)
        if not changed:
            return False, "scope_violation:no_change", {}
    elif edit_scope in (SCOPE_INSERT_PASS_LINE, SCOPE_INSERT_STDLIB_IMPORT):
        bl = before.splitlines(keepends=True)
        al = after.splitlines(keepends=True)
        if len(al) != len(bl) + 1:
            return False, "scope_violation:line_count", {}
        k = next((j for j in range(len(bl)) if bl[j] != al[j]), len(bl))
        if al[:k] != bl[:k] or al[k + 1 :] != bl[k:]:
            return False, "scope_violation:not_single_line_insert", {}
        inserted = al[k]
        if edit_scope == SCOPE_INSERT_PASS_LINE and not re.fullmatch(r"[ \t]*pass\r?\n?", inserted):
            return False, "scope_violation:inserted_line_not_pass", {}
        if edit_scope == SCOPE_INSERT_STDLIB_IMPORT and inserted.strip() not in STDLIB_IMPORT_MAP.values():
            return False, "scope_violation:inserted_line_not_whitelisted_import", {}
        offset = sum(len(line) for line in al[:k])
        changed = [offset + j for j, ch in enumerate(inserted) if not ch.isspace()]
    else:
        return False, f"scope_violation:unknown_scope:{edit_scope}", {}

    mask = string_or_comment_mask(after)
    if mask is None:
        return False, "guard_failed:repaired_source_untokenizable", {}
    for pos in changed:
        if mask[pos]:
            return False, "guard_failed:edit_inside_string_or_comment", {"pos": pos}
        if edit_scope in (SCOPE_INSERT_CLOSING_DELIMITER, SCOPE_REPLACE_FULLWIDTH):
            if _PROTECTED_LINE_RE.search(split_line_comment(_line_at(after, pos))[0]):
                return False, "guard_failed:protected_answer_line_modified", {"pos": pos}
    return True, "patch_within_scope", {"changed_positions": changed[:50], "changed_count": len(changed)}


def verify_certificate(cert: Mapping[str, Any]) -> list[str]:
    errors = [f"missing_field:{f}" for f in REQUIRED_CERT_FIELDS if f not in cert]
    if cert.get("expected_answer_not_read") is not True:
        errors.append("expected_answer_read")
    if cert.get("evaluator_result_not_read") is not True:
        errors.append("evaluator_result_read")
    if cert.get("decision") == "ACCEPT":
        if cert.get("candidate_trial_count") != 1:
            errors.append("candidate_trial_count_not_1")
        if cert.get("candidate_count") != 1:
            errors.append("candidate_count_not_1")
    return errors


# ---------------------------------------------------------------------------
# Core healing loop
# ---------------------------------------------------------------------------


def _finish(result: V3HealerResult, status: str, reason: str, *, repaired: str | None = None) -> V3HealerResult:
    result.status = status
    result.reason = reason
    if status == STATUS_REPAIRED and repaired is not None:
        result.repaired_code = repaired
        result.repaired_sha256 = sha256_text(repaired)
    else:
        result.repaired_code = None
        result.repaired_sha256 = None
    return result


def _run_validator(validator: Validator, code: str) -> dict[str, Any]:
    try:
        raw = dict(validator(code) or {})
    except Exception as exc:  # noqa: BLE001 - fail closed
        raw = {"passed": False, "blockers": [f"validator_error:{type(exc).__name__}:{exc}"]}
    raw["passed"] = bool(raw.get("passed")) and not raw.get("blockers")
    raw["code_sha256"] = sha256_text(code)
    return raw


def _idempotence_violations(code: str, rules: list[V3HealerRuleSpec]) -> list[str]:
    violations = []
    for spec in rules:
        proposal = spec.apply(code, {"name_error_name": None})  # type: ignore[misc]
        if proposal.applied and proposal.source_out != code:
            violations.append(spec.rule_id)
    return violations


def heal_v3_component(
    request: V3HealerRequest,
    *,
    validator: Validator,
    mode: str = MODE_SHADOW,
) -> V3HealerResult:
    original = request.candidate_code
    contract = dict(request.operation_contract or {})
    result = V3HealerResult(
        status=STATUS_ABSTAINED,
        mode=mode,
        component_id=str(request.component_id),
        textbook_example_id=int(request.textbook_example_id),
        skill_id=str(contract.get("skill_id") or ""),
        original_sha256=sha256_text(original),
        contract_sha256=sha256_text(_stable_json(contract)),
        original_code=original,
        sha_history=[sha256_text(original)],
    )

    status = str(request.component_status or "").strip().lower()
    if status in PROTECTED_COMPONENT_STATUSES:
        return _finish(result, STATUS_ABSTAINED, f"protected_component_status:{status}")
    if _is_production_path(request.source_path):
        return _finish(result, STATUS_ABSTAINED, "production_path_protected")

    diagnostics = dict(request.failure_diagnostics or {})
    if not diagnostics or diagnostics.get("passed") is True:
        result.failure_category = "passed"
        return _finish(result, STATUS_UNCHANGED, "original_candidate_passed_identity_preserve")

    contract_ok, contract_reason = check_component_contract(original, request)
    if not contract_ok:
        return _finish(result, STATUS_ABSTAINED, contract_reason)

    allowed = tuple(request.allowed_rules) if request.allowed_rules is not None else EXECUTABLE_RULE_ORDER
    for rule_id in allowed:
        spec = RULES_BY_ID.get(rule_id)
        if spec is None:
            result.attempts.append({"round": 0, "rule_id": rule_id, "decision": "ABSTAIN", "reason": "unknown_rule"})
        elif rule_id in DISABLED_RULE_IDS:
            result.attempts.append(
                {
                    "round": 0,
                    "rule_id": rule_id,
                    "research_tier": spec.research_tier,
                    "decision": "ABSTAIN",
                    "reason": f"rule_disabled_in_v3:{spec.disabled_reason}",
                }
            )
    rules = [RULES_BY_ID[r] for r in EXECUTABLE_RULE_ORDER if r in allowed]

    category = classify_failure(original, diagnostics)
    result.failure_category = category
    if category not in (FAILURE_SYNTAX, FAILURE_NAME):
        return _finish(result, STATUS_ABSTAINED, f"failure_category_not_eligible:{category}")
    if not rules:
        return _finish(result, STATUS_ABSTAINED, "no_executable_rule_allowed")

    current = original
    current_diag: dict[str, Any] = diagnostics
    context = _rule_context(diagnostics)
    patches = 0
    validations = 0
    max_rounds = max(1, int(request.max_rounds))
    for round_index in range(1, max_rounds + 1):
        result.rounds = round_index
        category = classify_failure(current, current_diag)
        if category == "compiles":
            if validations >= int(request.max_validation_calls):
                return _finish(result, STATUS_REJECTED, "validation_budget_exhausted")
            validation = _run_validator(validator, current)
            validations += 1
            result.validation_results.append(validation)
            if validation["passed"]:
                if patches == 0:
                    return _finish(result, STATUS_UNCHANGED, "candidate_already_valid")
                violations = _idempotence_violations(current, rules)
                if violations:
                    return _finish(result, STATUS_REJECTED, f"non_idempotent:{','.join(violations)}")
                cert_errors = [e for cert in result.certificates for e in verify_certificate(cert)]
                if cert_errors:
                    return _finish(result, STATUS_REJECTED, f"certificate_verify_failed:{cert_errors}")
                return _finish(result, STATUS_REPAIRED, "repaired_and_isolated_validation_passed", repaired=current)
            current_diag = _diagnostics_from_validation(validation)
            category = classify_failure(current, current_diag)
            context = _rule_context(current_diag)
            if category not in (FAILURE_SYNTAX, FAILURE_NAME):
                blockers = ";".join(str(b) for b in validation.get("blockers") or [])[:500]
                return _finish(result, STATUS_REJECTED, f"isolated_validation_failed:{blockers}")

        proposal = None
        chosen: V3HealerRuleSpec | None = None
        for spec in rules:
            if category not in spec.eligibility:
                continue
            candidate = spec.apply(current, context)  # type: ignore[misc]
            if candidate.applied and candidate.source_out != current:
                proposal, chosen = candidate, spec
                break
            result.attempts.append(
                {
                    "round": round_index,
                    "rule_id": spec.rule_id,
                    "research_tier": spec.research_tier,
                    "decision": "ABSTAIN",
                    "reason": candidate.reason,
                    "candidate_count": candidate.candidate_count,
                }
            )
        if proposal is None or chosen is None:
            if patches == 0:
                return _finish(result, STATUS_ABSTAINED, "no_rule_produced_unique_candidate")
            return _finish(result, STATUS_REJECTED, "residual_failure_after_partial_repair")

        ok, guard_reason, guard_details = verify_patch(current, proposal.source_out, chosen.edit_scope)
        attempt = {
            "round": round_index,
            "rule_id": chosen.rule_id,
            "research_tier": chosen.research_tier,
            "layer_role": chosen.layer_role,
            "edit_scope": chosen.edit_scope,
            "before_sha256": sha256_text(current),
            "after_sha256": sha256_text(proposal.source_out),
            "candidate_count": proposal.candidate_count,
            "rule_reason": proposal.reason,
            "guard": guard_reason,
        }
        if not ok:
            attempt["decision"] = "REJECT"
            result.attempts.append(attempt)
            return _finish(result, STATUS_REJECTED, f"patch_guard_failed:{chosen.rule_id}:{guard_reason}")
        after_sha = sha256_text(proposal.source_out)
        if after_sha in result.sha_history:
            attempt["decision"] = "REJECT"
            result.attempts.append(attempt)
            result.cycle_detected = True
            return _finish(result, STATUS_REJECTED, "sha_cycle_detected")

        attempt["decision"] = "ACCEPT"
        result.attempts.append(attempt)
        result.certificates.append(
            {
                "rule_id": chosen.rule_id,
                "research_tier": chosen.research_tier,
                "layer_role": chosen.layer_role,
                "decision": "ACCEPT",
                "contract_id": f"{result.skill_id}:{result.component_id}",
                "contract_sha256": result.contract_sha256,
                "edit_scope": chosen.edit_scope,
                "rule_evidence": dict(proposal.evidence),
                "patch_guard": guard_details,
                "before_source_sha256": sha256_text(current),
                "after_source_sha256": after_sha,
                "candidate_count": proposal.candidate_count,
                "candidate_trial_count": 1,
                "expected_answer_not_read": True,
                "evaluator_result_not_read": True,
                "round": round_index,
            }
        )
        result.rules_applied.append(
            {"rule_id": chosen.rule_id, "research_tier": chosen.research_tier, "layer_role": chosen.layer_role}
        )
        result.sha_history.append(after_sha)
        current = proposal.source_out
        current_diag = {}
        context = {"name_error_name": None}
        patches += 1

    result.retry_limit_hit = True
    return _finish(result, STATUS_REJECTED, "retry_limit_exceeded")


# ---------------------------------------------------------------------------
# Isolated validation (subprocess, temp dir outside the repository)
# ---------------------------------------------------------------------------


def isolated_validate_in_process(
    code: str,
    *,
    component_id: str,
    induced_spec: Mapping[str, Any] | None = None,
    run_source_isomorphism: bool = False,
    seeds: tuple[int, ...] = ISOLATED_VALIDATION_SEEDS,
) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    blockers: list[str] = []
    out: dict[str, Any] = {"checks": checks, "blockers": blockers, "exception_type": None, "exception_message": None}
    try:
        compiled = compile(code, "<v3_healer_isolated_candidate>", "exec")
        checks["python_compile"] = "passed"
        namespace: dict[str, Any] = {"__name__": "v3_healer_isolated_candidate"}
        exec(compiled, namespace)  # noqa: S102 - isolated subprocess only
        generate = namespace.get("generate")
        if not callable(generate):
            blockers.append("missing_generate_function")
            return out
        payload = generate(seed=42)
        if not isinstance(payload, dict):
            blockers.append("generate_must_return_dict")
            return out
        checks["component_execution_seed_42"] = "passed"
        replay = generate(seed=42)
        checks["deterministic_replay_seed_42"] = _stable_json(payload) == _stable_json(replay)
        if not checks["deterministic_replay_seed_42"]:
            blockers.append("non_deterministic_seed_42")
        out["payload_sha256"] = sha256_text(_stable_json(payload))

        from core.gencode.services.v3_question_integrity_validator import validate_component_payload

        first = validate_component_payload(payload, component_id=component_id)
        blockers.extend(str(b) for b in first.get("blockers") or [])
        seed_results = {}
        for seed in seeds:
            sample = generate(seed=seed, component_id=component_id)
            verdict = validate_component_payload(sample, component_id=component_id)
            seed_results[str(seed)] = bool(verdict.get("passed", True))
            if not verdict.get("passed", True):
                blockers.extend(f"seed_{seed}:{b}" for b in verdict.get("blockers") or ["integrity_failed"])
        checks["multi_seed_integrity"] = seed_results

        from core.gencode.choice_contract_validator import validate_choice_contract

        checks["choice_contract_valid"] = bool(validate_choice_contract(payload).get("ok"))

        answer_contract = payload.get("answer_contract")
        if not isinstance(answer_contract, dict) or not answer_contract:
            blockers.append("answer_contract_missing")
        else:
            from core.gencode.checker_registry import validate_answer_contract_capability

            capability = validate_answer_contract_capability(answer_contract)
            checks["answer_contract_capability"] = capability.get("checker_capability_status") or (
                "blocked" if capability.get("checker_contract_blockers") else "ok"
            )
            blockers.extend(str(b) for b in capability.get("checker_contract_blockers") or [])

        from core.gencode.runtime_skill_wrapper import check_answer

        correct = payload.get("correct_answer", payload.get("answer"))
        if correct is None or (isinstance(correct, str) and not correct.strip()):
            blockers.append("correct_answer_missing")
        else:
            skill = str(payload.get("skill_id") or "")
            submitted = correct if not isinstance(correct, str) else correct.strip()
            positive = bool(check_answer(str(submitted), correct, payload=payload, skill_id=skill))
            negative = bool(check_answer(NEGATIVE_CHECKER_PROBE, correct, payload=payload, skill_id=skill))
            checks["shared_checker_positive"] = positive
            checks["shared_checker_negative_rejected"] = not negative
            if not positive:
                blockers.append("shared_checker_rejects_canonical_answer")
            if negative:
                blockers.append("shared_checker_accepts_negative_probe")

        if run_source_isomorphism and isinstance(induced_spec, Mapping):
            from core.gencode.validators.source_isomorphism_validator import validate_source_isomorphism

            iso = validate_source_isomorphism(payload, induced_spec=dict(induced_spec))
            checks["source_isomorphism"] = bool(iso.get("passed", True))
            blockers.extend(f"GENERATION_NOT_SOURCE_ISOMORPHIC:{b}" for b in iso.get("blockers") or [])
        else:
            checks["source_isomorphism"] = "not_required"
    except Exception as exc:  # noqa: BLE001 - reported as validation failure
        out["exception_type"] = type(exc).__name__
        out["exception_message"] = str(exc)[:1000]
        blockers.append(f"execution_error:{type(exc).__name__}:{str(exc)[:300]}")
    return out


def make_isolated_subprocess_validator(
    *,
    component_id: str,
    induced_spec: Mapping[str, Any] | None = None,
    run_source_isomorphism: bool = False,
    seeds: tuple[int, ...] = ISOLATED_VALIDATION_SEEDS,
    timeout_s: int = DEFAULT_VALIDATION_TIMEOUT_S,
) -> Validator:
    def _validate(code: str) -> dict[str, Any]:
        work_dir = Path(tempfile.mkdtemp(prefix="v3_healer_iso_"))
        try:
            request_path = work_dir / "request.json"
            result_path = work_dir / "result.json"
            request_path.write_text(
                _stable_json(
                    {
                        "code": code,
                        "component_id": component_id,
                        "induced_spec": dict(induced_spec or {}),
                        "run_source_isomorphism": bool(run_source_isomorphism),
                        "seeds": list(seeds),
                        "result_path": str(result_path),
                    }
                ),
                encoding="utf-8",
            )
            env = dict(os.environ)
            env[HEALER_MODE_ENV] = MODE_OFF
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "core.gencode.v3_healer_adapter", "--isolated-validate", str(request_path)],
                    cwd=str(PROJECT_ROOT),
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout_s,
                )
            except subprocess.TimeoutExpired:
                return {"passed": False, "blockers": ["isolated_validation_timeout"], "isolation": "subprocess"}
            if not result_path.is_file():
                return {
                    "passed": False,
                    "blockers": [f"isolated_validation_crashed:rc={proc.returncode}"],
                    "stderr_tail": (proc.stderr or "")[-800:],
                    "isolation": "subprocess",
                }
            data = json.loads(result_path.read_text(encoding="utf-8"))
            data["isolation"] = "subprocess"
            data["passed"] = not data.get("blockers")
            return data
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    return _validate


def _isolated_validate_cli(request_path: str) -> int:
    request = json.loads(Path(request_path).read_text(encoding="utf-8"))
    result = isolated_validate_in_process(
        request["code"],
        component_id=str(request["component_id"]),
        induced_spec=request.get("induced_spec") or None,
        run_source_isomorphism=bool(request.get("run_source_isomorphism")),
        seeds=tuple(int(s) for s in request.get("seeds") or ISOLATED_VALIDATION_SEEDS),
    )
    Path(request["result_path"]).write_text(_stable_json(result), encoding="utf-8")
    return 0


# ---------------------------------------------------------------------------
# Pipeline-facing wrapper
# ---------------------------------------------------------------------------


def write_healer_evidence(result: V3HealerResult, *, dryrun_path: str, skill_id: str) -> str:
    from core.gencode.skill_wrapper_compiler import assert_safe_sandbox_root

    assert_safe_sandbox_root(dryrun_path)
    target_dir = Path(dryrun_path) / skill_id / "v3_healer_evidence"
    if _is_production_path(str(target_dir)):
        raise ValueError("v3_healer_evidence_path_in_production")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{result.component_id}.json"
    target.write_text(json.dumps(result.evidence(), ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return str(target)


def heal_v3_component_after_exec_failure(
    *,
    draft: Mapping[str, Any],
    induced_spec: Mapping[str, Any],
    skill_id: str,
    textbook_example_id: int,
    component_id: str,
    execution_error: str,
    dryrun_path: str,
    run_source_isomorphism: bool = False,
    mode: str | None = None,
    validator: Validator | None = None,
    conn: Any = None,
    generation_run_id: str | None = None,
    telemetry_context: Mapping[str, Any] | None = None,
) -> V3HealerResult | None:
    """Return None in ``off`` mode; otherwise a result that never mutates ``draft``.

    With ``conn`` the attempt is appended to the healer telemetry table; telemetry
    failures are recorded on ``result.telemetry`` and never change the result.
    """
    active_mode = mode if mode in VALID_MODES else resolve_healer_mode()
    if active_mode == MODE_OFF:
        return None
    from core.gencode.v3_healer_telemetry import now_iso, record_attempt_safely

    started_at = now_iso()
    files = draft.get("files") if isinstance(draft.get("files"), Mapping) else {}
    code = str(files.get("generate.py") or "")
    contract = {
        "skill_id": skill_id,
        "component_id": component_id,
        "textbook_example_id": int(textbook_example_id),
        "fixed_domain_key": str(induced_spec.get("fixed_domain_key") or draft.get("fixed_domain_key") or ""),
        "domain_operation": str(induced_spec.get("domain_operation") or draft.get("domain_operation") or ""),
        "answer_schema_key": str(induced_spec.get("answer_schema_key") or ""),
        "checker_key": str(induced_spec.get("checker_key") or ""),
        "presentation_mode": str(induced_spec.get("presentation_mode") or ""),
        "registry_revision": str(induced_spec.get("registry_revision") or ""),
    }
    request = V3HealerRequest(
        component_id=component_id,
        textbook_example_id=int(textbook_example_id),
        candidate_code=code,
        failure_diagnostics=parse_execution_error(execution_error),
        operation_contract=contract,
        component_status="draft",
    )
    active_validator = validator or make_isolated_subprocess_validator(
        component_id=component_id,
        induced_spec=induced_spec,
        run_source_isomorphism=run_source_isomorphism,
    )
    try:
        result = heal_v3_component(request, validator=active_validator, mode=active_mode)
    except Exception as exc:  # noqa: BLE001 - adapter bugs must never alter the original failure
        result = V3HealerResult(
            status=STATUS_REJECTED,
            mode=active_mode,
            component_id=component_id,
            textbook_example_id=int(textbook_example_id),
            skill_id=skill_id,
            original_sha256=sha256_text(code),
            contract_sha256=sha256_text(_stable_json(contract)),
            original_code=code,
            reason=f"adapter_internal_error:{type(exc).__name__}:{exc}",
        )
    result.applied_to_pipeline = active_mode == MODE_REPAIR and result.status == STATUS_REPAIRED
    try:
        result.evidence_path = write_healer_evidence(result, dryrun_path=dryrun_path, skill_id=skill_id)
    except Exception as exc:  # noqa: BLE001
        result.evidence_path = None
        if result.applied_to_pipeline:
            result.applied_to_pipeline = False
            result.post_repair_gates = f"not_applied:evidence_write_failed:{type(exc).__name__}"
    if conn is not None:
        record_attempt_safely(
            conn,
            result,
            generation_run_id=str(generation_run_id or ""),
            context=telemetry_context,
            started_at=started_at,
            finished_at=now_iso(),
        )
    return result


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "--isolated-validate":
        return _isolated_validate_cli(argv[1])
    print("usage: python -m core.gencode.v3_healer_adapter --isolated-validate <request.json>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
