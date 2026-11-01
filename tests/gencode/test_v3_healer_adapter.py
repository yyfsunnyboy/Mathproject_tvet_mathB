# -*- coding: utf-8 -*-
"""Unit / regression tests for the GenCode V3 component code healer adapter."""

from __future__ import annotations

import dataclasses
import inspect
import subprocess
from pathlib import Path

import pytest

import core.gencode.v3_healer_adapter as adapter
from core.gencode.v3_healer_adapter import (
    MODE_OFF,
    MODE_REPAIR,
    MODE_SHADOW,
    STATUS_ABSTAINED,
    STATUS_REJECTED,
    STATUS_REPAIRED,
    STATUS_UNCHANGED,
    V3HealerRequest,
    heal_v3_component,
    heal_v3_component_after_exec_failure,
    resolve_healer_mode,
    sha256_text,
    verify_certificate,
)
from core.gencode.v3_healer_rules import (
    DISABLED_RULE_IDS,
    EXECUTABLE_RULE_ORDER,
    RESEARCH_COMMIT,
    RULE_A_L1_PAREN,
    RULE_B1_FULLWIDTH,
    RULE_B2_DELIMITER,
    RULE_B3_EMPTY_SUITE,
    RULE_B4_IMPORT,
    RULES_BY_ID,
    RuleProposal,
    SCOPE_INSERT_CLOSING_DELIMITER,
)

GOOD_CODE = '''from __future__ import annotations

from typing import Any

TEXTBOOK_EXAMPLE_ID = 5
DEFAULT_COMPONENT_ID = "src_5" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    norm_context = {
        "skill_id": "demo_skill",
        "fixed_domain_key": "algebra.demo",
    }
    values = [3, 4]
    constraints = {"skill_id": "demo_skill"}
    constraints["label"] = "求（1，2）的和"
    total = sum(values)
    payload = build_payload(total, domain_operation="demo_op")
    if kwargs.get("component_id"):
        payload["component_id"] = kwargs["component_id"]
    return payload


def build_payload(total: int, domain_operation: str) -> dict[str, Any]:
    return {"question_text": "3 + 4 = ?", "correct_answer": str(total), "domain_operation": domain_operation}
'''

CONTRACT = {"skill_id": "demo_skill", "fixed_domain_key": "algebra.demo", "domain_operation": "demo_op"}
SYNTAX_DIAG = {"exception_type": "SyntaxError", "exception_message": "corrupted"}


def _corrupt(old: str, new: str, code: str = GOOD_CODE) -> str:
    assert code.count(old) == 1
    return code.replace(old, new)


class FakeValidator:
    """Stands in for the isolated V3 gates; never compares against an expected answer."""

    def __init__(self, fail: bool = False):
        self.calls: list[str] = []
        self.fail = fail

    def __call__(self, code: str) -> dict:
        self.calls.append(code)
        if self.fail:
            return {"passed": False, "blockers": ["forced_gate_failure"]}
        namespace: dict = {}
        try:
            exec(compile(code, "<fake>", "exec"), namespace)  # noqa: S102
            payload = namespace["generate"](seed=42)
        except Exception as exc:  # noqa: BLE001
            return {
                "passed": False,
                "blockers": [f"execution_error:{type(exc).__name__}"],
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            }
        blockers = [] if payload.get("correct_answer") and payload.get("question_text") else ["payload_incomplete"]
        return {"passed": not blockers, "blockers": blockers}


def _request(code: str, diag=None, **overrides) -> V3HealerRequest:
    fields = {
        "component_id": "src_5",
        "textbook_example_id": 5,
        "candidate_code": code,
        "failure_diagnostics": SYNTAX_DIAG if diag is None else diag,
        "operation_contract": CONTRACT,
    }
    fields.update(overrides)
    return V3HealerRequest(**fields)


# 1. PASS Identity Preserve
def test_pass_identity_preserve_returns_original_object_without_validation():
    validator = FakeValidator()
    result = heal_v3_component(_request(GOOD_CODE, {"passed": True}), validator=validator)
    assert result.status == STATUS_UNCHANGED
    assert result.final_code is GOOD_CODE
    assert result.repaired_code is None and result.attempts == [] and validator.calls == []
    assert result.original_sha256 == sha256_text(GOOD_CODE)


# 2. Eligible Syntax Failure
def test_missing_bracket_is_repaired_byte_identically_and_certified():
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')
    validator = FakeValidator()
    result = heal_v3_component(_request(broken), validator=validator)
    assert result.status == STATUS_REPAIRED, result.reason
    assert result.repaired_code == GOOD_CODE
    assert result.repaired_sha256 == sha256_text(GOOD_CODE)
    assert [r["rule_id"] for r in result.rules_applied] == [RULE_B2_DELIMITER]
    assert len(validator.calls) == 1
    assert all(verify_certificate(cert) == [] for cert in result.certificates)
    assert result.certificates[0]["expected_answer_not_read"] is True


def test_fullwidth_colon_outside_strings_is_normalized_and_string_literals_untouched():
    broken = _corrupt('if kwargs.get("component_id"):', 'if kwargs.get("component_id")：')
    result = heal_v3_component(_request(broken), validator=FakeValidator())
    assert result.status == STATUS_REPAIRED, result.reason
    assert result.repaired_code == GOOD_CODE
    assert "求（1，2）的和" in result.repaired_code
    assert [r["rule_id"] for r in result.rules_applied] == [RULE_B1_FULLWIDTH]


def test_unclosed_call_at_line_end_uses_tier_a_paren_rule():
    broken = _corrupt("total = sum(values)", "total = sum(values")
    result = heal_v3_component(_request(broken), validator=FakeValidator())
    assert result.status == STATUS_REPAIRED, result.reason
    assert result.repaired_code == GOOD_CODE
    assert result.rules_applied[0]["rule_id"] == RULE_A_L1_PAREN


def test_name_error_import_is_inserted_after_future_import():
    code = _corrupt("total = sum(values)", "total = Fraction(sum(values))")
    diag = {"exception_type": "NameError", "exception_message": "name 'Fraction' is not defined"}
    result = heal_v3_component(_request(code, diag), validator=FakeValidator())
    assert result.status == STATUS_REPAIRED, result.reason
    lines = result.repaired_code.splitlines()
    assert lines[0] == "from __future__ import annotations"
    assert lines[1] == "from fractions import Fraction"
    compile(result.repaired_code, "<check>", "exec")
    assert result.rules_applied[0]["rule_id"] == RULE_B4_IMPORT


def test_name_error_without_matching_static_gap_abstains():
    code = _corrupt("total = sum(values)", "total = Fraction(sum(values))")
    diag = {"exception_type": "NameError", "exception_message": "name 'Decimal' is not defined"}
    result = heal_v3_component(_request(code, diag), validator=FakeValidator())
    assert result.status == STATUS_ABSTAINED
    assert result.final_code is code


# 3. Contract Mismatch -> ABSTAIN
@pytest.mark.parametrize(
    "overrides, reason",
    [
        ({"operation_contract": {**CONTRACT, "fixed_domain_key": ""}}, "contract_field_missing:fixed_domain_key"),
        ({"operation_contract": {**CONTRACT, "domain_operation": "other_op"}}, "contract_mismatch:domain_operation"),
        ({"textbook_example_id": 6, "component_id": "src_6"}, "contract_mismatch:textbook_example_id"),
        ({"component_id": "src_99"}, "contract_mismatch:component_id"),
    ],
)
def test_contract_mismatch_abstains_without_validation(overrides, reason):
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')
    validator = FakeValidator()
    result = heal_v3_component(_request(broken, **overrides), validator=validator)
    assert result.status == STATUS_ABSTAINED
    assert result.reason == reason
    assert result.final_code is broken and validator.calls == []


def test_disabled_research_rules_only_abstain():
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')
    allowed = ("PC-R01", "TIER_D_SYNTAX_RESIDUE_QUARANTINE_V1", "TIER_B_DOMAIN_SIGNATURE_FORM_REPAIR_V1")
    allowed = tuple(r for r in allowed if r in RULES_BY_ID) or DISABLED_RULE_IDS[:3]
    result = heal_v3_component(_request(broken, allowed_rules=allowed), validator=FakeValidator())
    assert result.status == STATUS_ABSTAINED
    assert result.reason == "no_executable_rule_allowed"
    assert all(a["reason"].startswith("rule_disabled_in_v3:") for a in result.attempts)


def test_runtime_failure_category_is_not_eligible():
    result = heal_v3_component(
        _request(GOOD_CODE, {"exception_type": "ZeroDivisionError", "exception_message": "division by zero"}),
        validator=FakeValidator(),
    )
    assert result.status == STATUS_ABSTAINED
    assert result.reason == "failure_category_not_eligible:runtime:ZeroDivisionError"


# 4. Math Semantic Drift -> reject / abstain
def test_ambiguous_paren_positions_abstain_instead_of_guessing():
    code = _corrupt("total = sum(values)", "total = sum(values[0] + values[1])")
    broken = _corrupt("total = sum(values[0] + values[1])", "total = sum(values[0] + values[1]", code)
    result = heal_v3_component(_request(broken), validator=FakeValidator())
    assert result.status == STATUS_ABSTAINED
    assert result.final_code is broken
    assert any("ambiguous" in a.get("reason", "") for a in result.attempts)


def test_misindented_loop_body_is_not_filled_with_pass():
    code = _corrupt("    total = sum(values)\n", "    total = 0\n    for v in values:\n    total += v\n")
    research_style = code.replace("    for v in values:\n", "    for v in values:\n        pass\n")
    ns: dict = {}
    exec(compile(research_style, "<drift>", "exec"), ns)  # noqa: S102
    assert ns["generate"](seed=42)["correct_answer"] != "7"
    result = heal_v3_component(_request(code), validator=FakeValidator())
    assert result.status == STATUS_ABSTAINED
    assert any("misindented" in a.get("reason", "") for a in result.attempts)


def test_comment_only_suite_gets_pass():
    code = _corrupt(
        "    total = sum(values)\n",
        "    total = sum(values)\n    if level > 99:\n        # reserved\n",
    )
    result = heal_v3_component(_request(code), validator=FakeValidator())
    assert result.status == STATUS_REPAIRED, result.reason
    assert "        pass\n" in result.repaired_code
    assert result.rules_applied[0]["rule_id"] == RULE_B3_EMPTY_SUITE


def _install_rule(monkeypatch, apply, edit_scope=SCOPE_INSERT_CLOSING_DELIMITER):
    spec = dataclasses.replace(RULES_BY_ID[RULE_B2_DELIMITER], rule_id="TEST_MALICIOUS", apply=apply, edit_scope=edit_scope)
    monkeypatch.setitem(adapter.RULES_BY_ID, "TEST_MALICIOUS", spec)
    monkeypatch.setattr(adapter, "EXECUTABLE_RULE_ORDER", ("TEST_MALICIOUS",))


def test_rule_changing_numeric_literal_is_rejected_by_patch_guard(monkeypatch):
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')

    def malicious(code, context):
        fixed = code.replace('constraints["label" =', 'constraints["label"] =').replace("[3, 4]", "[3, 5]")
        return RuleProposal("TEST_MALICIOUS", True, fixed, SCOPE_INSERT_CLOSING_DELIMITER, "drift", 1)

    _install_rule(monkeypatch, malicious)
    validator = FakeValidator()
    result = heal_v3_component(_request(broken), validator=validator)
    assert result.status == STATUS_REJECTED
    assert result.reason.startswith("patch_guard_failed:TEST_MALICIOUS:scope_violation")
    assert result.final_code is broken and validator.calls == []


# 5. Oracle Independence
def test_answer_line_cannot_be_modified_even_by_a_legitimate_rule():
    broken = _corrupt('"correct_answer": str(total)', '"correct_answer": str（total)')
    result = heal_v3_component(_request(broken), validator=FakeValidator())
    assert result.status == STATUS_REJECTED
    assert result.reason.endswith("guard_failed:protected_answer_line_modified")
    assert result.final_code is broken


def test_healer_api_has_no_expected_answer_input():
    params = set(inspect.signature(heal_v3_component).parameters)
    request_fields = {f.name for f in dataclasses.fields(V3HealerRequest)}
    for forbidden in ("expected_answer", "correct_answer", "oracle_payload", "evaluator_result"):
        assert forbidden not in params and forbidden not in request_fields


def test_validator_failure_is_not_used_to_pick_alternative_candidates():
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')
    validator = FakeValidator(fail=True)
    result = heal_v3_component(_request(broken), validator=validator)
    assert result.status == STATUS_REJECTED
    assert len(validator.calls) == 1
    assert all(a.get("candidate_count", 1) <= 1 for a in result.attempts if a.get("decision") == "ACCEPT")


# 6. Multi-component isolation (unit level)
def test_components_are_healed_independently():
    good_b = GOOD_CODE.replace("TEXTBOOK_EXAMPLE_ID = 5", "TEXTBOOK_EXAMPLE_ID = 6").replace('"src_5"', '"src_6"')
    broken_a = _corrupt('constraints["label"] =', 'constraints["label" =')
    result_a = heal_v3_component(_request(broken_a), validator=FakeValidator())
    result_b = heal_v3_component(
        _request(good_b, {"passed": True}, textbook_example_id=6, component_id="src_6"),
        validator=FakeValidator(),
    )
    assert result_a.status == STATUS_REPAIRED and result_b.status == STATUS_UNCHANGED
    assert result_b.final_code is good_b
    assert result_a.contract_sha256 == result_b.contract_sha256 or result_a.component_id != result_b.component_id


# 7. Idempotence
def test_rerunning_on_repaired_code_produces_no_new_modification():
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')
    first = heal_v3_component(_request(broken), validator=FakeValidator())
    second = heal_v3_component(_request(first.repaired_code), validator=FakeValidator())
    third = heal_v3_component(_request(first.repaired_code, {"passed": True}), validator=FakeValidator())
    assert first.status == STATUS_REPAIRED
    assert second.final_code == first.repaired_code and second.rules_applied == []
    assert third.status == STATUS_UNCHANGED


# 8. Retry / cycle limit
def test_sha_cycle_is_detected(monkeypatch):
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')
    other = broken + ")"

    def toggler(code, context):
        return RuleProposal("TEST_MALICIOUS", True, other if code == broken else broken, SCOPE_INSERT_CLOSING_DELIMITER, "t", 1)

    _install_rule(monkeypatch, toggler)
    monkeypatch.setattr(adapter, "verify_patch", lambda before, after, scope: (True, "patched_for_test", {}))
    result = heal_v3_component(_request(broken), validator=FakeValidator())
    assert result.status == STATUS_REJECTED and result.reason == "sha_cycle_detected"
    assert result.cycle_detected and result.final_code is broken


def test_retry_limit_is_bounded(monkeypatch):
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')

    def grower(code, context):
        return RuleProposal("TEST_MALICIOUS", True, code + ")", SCOPE_INSERT_CLOSING_DELIMITER, "g", 1)

    _install_rule(monkeypatch, grower)
    monkeypatch.setattr(adapter, "verify_patch", lambda before, after, scope: (True, "patched_for_test", {}))
    result = heal_v3_component(_request(broken, max_rounds=3), validator=FakeValidator())
    assert result.status == STATUS_REJECTED and result.reason == "retry_limit_exceeded"
    assert result.retry_limit_hit and result.rounds == 3 and result.final_code is broken


# 9. Rollback
def test_failed_isolated_validation_keeps_original_code():
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')
    snapshot = str(broken)
    result = heal_v3_component(_request(broken), validator=FakeValidator(fail=True))
    assert result.status == STATUS_REJECTED
    assert result.reason.startswith("isolated_validation_failed")
    assert result.repaired_code is None and result.final_code == snapshot == broken


def test_raising_validator_fails_closed():
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')

    def boom(code):
        raise RuntimeError("validator crashed")

    result = heal_v3_component(_request(broken), validator=boom)
    assert result.status == STATUS_REJECTED and result.final_code is broken


# 10. Production protection
@pytest.mark.parametrize("status", ["verified", "published", "publishable", "runtime_ready"])
def test_protected_component_status_is_never_modified(status):
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')
    validator = FakeValidator()
    result = heal_v3_component(_request(broken, component_status=status), validator=validator)
    assert result.status == STATUS_ABSTAINED and result.final_code is broken and validator.calls == []


def test_production_path_is_never_modified():
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')
    path = str(adapter.PROJECT_ROOT / "agent_skills_v3" / "x" / "components" / "src_5" / "generate.py")
    result = heal_v3_component(_request(broken, source_path=path), validator=FakeValidator())
    assert result.status == STATUS_ABSTAINED and result.reason == "production_path_protected"


def test_evidence_writer_refuses_production_roots(tmp_path):
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')
    result = heal_v3_component(_request(broken), validator=FakeValidator())
    with pytest.raises(ValueError):
        adapter.write_healer_evidence(result, dryrun_path=str(adapter.PROJECT_ROOT / "agent_skills_v3"), skill_id="x")


# 11. Feature flag off / shadow / repair
@pytest.mark.parametrize(
    "raw, expected",
    [(None, MODE_OFF), ("", MODE_OFF), ("bogus", MODE_OFF), ("OFF", MODE_OFF), ("shadow", MODE_SHADOW), (" Repair ", MODE_REPAIR)],
)
def test_resolve_healer_mode(raw, expected):
    env = {} if raw is None else {adapter.HEALER_MODE_ENV: raw}
    assert resolve_healer_mode(env) == expected


def _wrapper(mode, tmp_path, validator):
    broken = _corrupt('constraints["label"] =', 'constraints["label" =')
    draft = {"files": {"generate.py": broken}}
    before = dict(draft["files"])
    result = heal_v3_component_after_exec_failure(
        draft=draft,
        induced_spec=CONTRACT,
        skill_id="demo_skill",
        textbook_example_id=5,
        component_id="src_5",
        execution_error="execution_error:SyntaxError:'[' was never closed",
        dryrun_path=str(tmp_path),
        mode=mode,
        validator=validator,
    )
    assert draft["files"] == before
    return result


def test_feature_flag_off_never_calls_healer(tmp_path, monkeypatch):
    monkeypatch.delenv(adapter.HEALER_MODE_ENV, raising=False)
    validator = FakeValidator()
    assert _wrapper(None, tmp_path, validator) is None
    assert validator.calls == [] and not any(tmp_path.iterdir())


def test_feature_flag_shadow_records_but_does_not_apply(tmp_path):
    result = _wrapper(MODE_SHADOW, tmp_path, FakeValidator())
    assert result.status == STATUS_REPAIRED and result.applied_to_pipeline is False
    assert Path(result.evidence_path).is_file()


def test_feature_flag_repair_marks_applied(tmp_path):
    result = _wrapper(MODE_REPAIR, tmp_path, FakeValidator())
    assert result.status == STATUS_REPAIRED and result.applied_to_pipeline is True
    assert Path(result.evidence_path).is_file()


def test_adapter_internal_error_is_fail_closed(tmp_path, monkeypatch):
    def broken_rule(code, context):
        raise RuntimeError("rule bug")

    _install_rule(monkeypatch, broken_rule)
    result = _wrapper(MODE_REPAIR, tmp_path, FakeValidator())
    assert result.status == STATUS_REJECTED and result.applied_to_pipeline is False
    assert result.reason.startswith("adapter_internal_error:")


# Rule registry / provenance
def test_rule_registry_metadata_is_complete():
    assert set(EXECUTABLE_RULE_ORDER) == {
        RULE_A_L1_PAREN, RULE_B1_FULLWIDTH, RULE_B2_DELIMITER, RULE_B3_EMPTY_SUITE, RULE_B4_IMPORT,
    }
    tiers_disabled = [RULES_BY_ID[r].research_tier for r in DISABLED_RULE_IDS]
    assert {"Tier C1", "Tier C2"} <= set(tiers_disabled)
    assert tiers_disabled.count("Tier D") == 4
    assert sum(1 for r in DISABLED_RULE_IDS if r.startswith("PC-R0")) == 4
    for spec in RULES_BY_ID.values():
        assert spec.trigger and spec.eligibility is not None and spec.forbidden_semantics
        assert spec.validation_requirements and spec.abstain_conditions
        assert spec.provenance.git_blob_sha1
        if not spec.executable:
            assert spec.disabled_reason and spec.apply is None


def test_provenance_blob_shas_match_research_commit():
    repo = Path(__file__).resolve().parents[3] / "MathProject_AST_Research_HealerBoundary"
    if not (repo / ".git").exists():
        pytest.skip("research repository checkout not available")
    for spec in RULES_BY_ID.values():
        paths = [p.strip() for p in spec.provenance.source_path.split("+")]
        shas = [s.strip() for s in spec.provenance.git_blob_sha1.replace("/", "+").split("+")]
        for path, sha in zip(paths, shas):
            got = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", f"{RESEARCH_COMMIT}:{path}"],
                capture_output=True, text=True, check=False,
            ).stdout.strip()
            assert got == sha, (spec.rule_id, path)
