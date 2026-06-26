# -*- coding: utf-8 -*-
"""Capability-first domain resolver tests (abstract fixtures only)."""

from __future__ import annotations

import re
from pathlib import Path
from unittest import mock

import pytest

from core.gencode.skill_fixed_domain_authority import (
    DOMAIN_CAPABILITY_AMBIGUOUS,
    DOMAIN_CAPABILITY_PARTIAL,
    DOMAIN_CAPABILITY_UNRESOLVED,
    SkillFixedDomainError,
    merge_resolver_extra_with_induced_constraints,
    normalize_capability_list,
    normalize_induced_spec_to_resolver_constraints,
    resolve_dynamic_fixed_domain_context,
    resolve_fixed_domain_context,
)
from core.gencode.v3_error_codes import DOMAIN_BINDING_MISSING, error_code_from_message
from core.registry.taxonomy_registry import get_fixed_domain_key


_ABSTRACT_PROVIDERS = {
    "provider_1": {
        "domain_module": "tests.abstract.provider_one",
        "entrypoint": "generate",
        "capabilities": ["cap_a", "cap_b", "cap_extra"],
        "allowed_operations": ["op_x", "op_y"],
    },
    "provider_2": {
        "domain_module": "tests.abstract.provider_two",
        "entrypoint": "generate",
        "capabilities": ["cap_a", "cap_b", "cap_c", "cap_d"],
        "allowed_operations": ["op_z"],
    },
    "provider_3": {
        "domain_module": "tests.abstract.provider_three",
        "entrypoint": "generate",
        "capabilities": ["cap_a"],
        "allowed_operations": ["op_x"],
    },
}

_AMBIGUOUS_PROVIDERS = {
    "provider_alpha": {
        "domain_module": "tests.abstract.alpha",
        "entrypoint": "generate",
        "capabilities": ["cap_a", "cap_b"],
        "allowed_operations": ["op_other"],
    },
    "provider_beta": {
        "domain_module": "tests.abstract.beta",
        "entrypoint": "generate",
        "capabilities": ["cap_a", "cap_b"],
        "allowed_operations": ["op_other"],
    },
}


def _resolve_with_providers(skill_id: str, *, extra: dict | None = None, providers: dict | None = None):
    provider_map = providers or _ABSTRACT_PROVIDERS
    with mock.patch(
        "core.gencode.skill_fixed_domain_authority.DOMAIN_PROVIDERS",
        provider_map,
    ):
        return resolve_dynamic_fixed_domain_context(
            skill_id,
            original_exc=ValueError("test"),
            extra=extra,
        )


def test_capability_passing_from_induced_spec():
    induced = {
        "problem_type_id": "op_x",
        "required_capabilities": ["cap_a", "cap_b"],
        "classification_source": "test_induced_spec",
    }
    extra = merge_resolver_extra_with_induced_constraints({}, induced)
    ctx = _resolve_with_providers("abstract_skill_for_capability_passing", extra=extra)
    assert ctx.fixed_domain_key == "provider_1"


def test_normalization_dedupes_and_filters_invalid_capabilities():
    raw = {
        "problem_type_id": "op_x",
        "required_capabilities": ["cap_a", "cap_a", "", None, 42, "cap_b", "  cap_b  "],
        "classification_source": "test_induced_spec",
    }
    normalized = normalize_induced_spec_to_resolver_constraints(raw)
    assert normalized["required_capabilities"] == ["cap_a", "cap_b"]
    assert normalize_capability_list(raw["required_capabilities"]) == ["cap_a", "cap_b"]


def test_full_capability_coverage_selects_provider():
    extra = merge_resolver_extra_with_induced_constraints(
        {},
        {
            "problem_type_id": "op_x",
            "required_capabilities": ["cap_a", "cap_b"],
            "classification_source": "test_induced_spec",
        },
    )
    ctx = _resolve_with_providers("abstract_skill_full_match", extra=extra)
    assert ctx.fixed_domain_key == "provider_1"


def test_partial_capability_coverage_raises_partial_error():
    extra = merge_resolver_extra_with_induced_constraints(
        {},
        {
            "problem_type_id": "op_x",
            "required_capabilities": ["cap_a", "cap_b"],
            "classification_source": "test_induced_spec",
        },
    )
    with pytest.raises(SkillFixedDomainError) as exc:
        _resolve_with_providers(
            "abstract_skill_partial_match",
            extra=extra,
            providers={"provider_3": _ABSTRACT_PROVIDERS["provider_3"]},
        )
    assert exc.value.code == DOMAIN_CAPABILITY_PARTIAL
    assert exc.value.details["matched_capabilities"] == ["cap_a"]
    assert exc.value.details["missing_capabilities"] == ["cap_b"]
    assert exc.value.details["best_provider"] == "provider_3"
    assert exc.value.details.get("reason") == "partial_capability_coverage"
    best_candidate = next(
        c for c in exc.value.details["candidate_providers"] if c["domain_key"] == "provider_3"
    )
    assert best_candidate["coverage_ratio"] == 0.5


def test_no_provider_match_raises_unresolved():
    extra = merge_resolver_extra_with_induced_constraints(
        {},
        {
            "problem_type_id": "op_x",
            "required_capabilities": ["cap_x"],
            "classification_source": "test_induced_spec",
        },
    )
    with pytest.raises(SkillFixedDomainError) as exc:
        _resolve_with_providers("abstract_skill_no_match", extra=extra)
    assert exc.value.code == DOMAIN_CAPABILITY_UNRESOLVED
    assert exc.value.details["matched_capabilities"] == []
    assert exc.value.details["missing_capabilities"] == ["cap_x"]


def test_ambiguous_full_coverage_does_not_pick_arbitrarily():
    extra = merge_resolver_extra_with_induced_constraints(
        {},
        {
            "problem_type_id": "op_x",
            "required_capabilities": ["cap_a", "cap_b"],
            "classification_source": "test_induced_spec",
        },
    )
    with pytest.raises(SkillFixedDomainError) as exc:
        _resolve_with_providers(
            "abstract_skill_ambiguous",
            extra=extra,
            providers=_AMBIGUOUS_PROVIDERS,
        )
    assert exc.value.code == DOMAIN_CAPABILITY_AMBIGUOUS
    assert set(exc.value.details.get("ambiguous_providers") or []) == {"provider_alpha", "provider_beta"}


def test_operation_exact_match_breaks_tie_between_full_providers():
    extra = merge_resolver_extra_with_induced_constraints(
        {},
        {
            "problem_type_id": "op_x",
            "required_capabilities": ["cap_a", "cap_b"],
            "classification_source": "test_induced_spec",
        },
    )
    ctx = _resolve_with_providers("abstract_skill_operation_tiebreak", extra=extra)
    assert ctx.fixed_domain_key == "provider_1"


def test_registry_fast_path_unchanged():
    key = get_fixed_domain_key("vh_數學B1_DistanceBetweenTwoParallelLines")
    ctx = resolve_fixed_domain_context("vh_數學B1_DistanceBetweenTwoParallelLines")
    assert ctx.fixed_domain_key == key
    assert "distance_between_parallel_lines" in ctx.allowed_operations


def test_error_code_precedence_capability_unresolved_over_not_registered():
    message = (
        "SkillDomainNotRegisteredError:skill not registered; "
        "DOMAIN_CAPABILITY_UNRESOLVED: cannot resolve domain"
    )
    assert error_code_from_message(message) == DOMAIN_CAPABILITY_UNRESOLVED
    assert error_code_from_message(message) != DOMAIN_BINDING_MISSING


def test_trace_contract_on_failure_includes_required_fields():
    extra = merge_resolver_extra_with_induced_constraints(
        {},
        {
            "problem_type_id": "op_x",
            "required_capabilities": ["cap_a", "cap_b"],
            "classification_source": "test_induced_spec",
        },
    )
    with pytest.raises(SkillFixedDomainError) as exc:
        _resolve_with_providers(
            "abstract_skill_trace_contract",
            extra=extra,
            providers={"provider_3": _ABSTRACT_PROVIDERS["provider_3"]},
        )
    details = exc.value.details
    assert details["resolution_source"] == "dynamic_capability_match"
    assert details["problem_type_id"] == "op_x"
    assert details["required_capabilities"] == ["cap_a", "cap_b"]
    assert details["classification_source"] == "test_induced_spec"
    assert isinstance(details["candidate_providers"], list)
    assert details["candidate_providers"]


def test_no_required_capabilities_reason():
    with pytest.raises(SkillFixedDomainError) as exc:
        _resolve_with_providers(
            "abstract_skill_without_any_capability_signal",
            extra={},
            providers=_ABSTRACT_PROVIDERS,
        )
    assert exc.value.code == DOMAIN_CAPABILITY_UNRESOLVED
    assert exc.value.details.get("reason") == "no_required_capabilities"


_FORBIDDEN_LITERALS = (
    "CentralTendencyMeasures",
    "arithmetic_mean",
    "3835",
)


def test_phase2_resolver_blocks_have_no_skill_or_example_specific_literals():
    repo_root = Path(__file__).resolve().parents[2]
    targets = [
        repo_root / "core" / "gencode" / "skill_fixed_domain_authority.py",
        repo_root / "core" / "gencode" / "pipeline_orchestrator.py",
    ]
    phase2_markers = (
        "normalize_induced_spec_to_resolver_constraints",
        "merge_resolver_extra_with_induced_constraints",
        "_select_provider_by_capability_coverage",
        "_compute_provider_coverage",
        "induced_spec_capabilities",
        "capability_coverage_full_match",
    )
    skill_id_pattern = re.compile(r"vh_[\w\u4e00-\u9fff]+")
    example_id_pattern = re.compile(r"textbook_example_id\s*=\s*\d+")

    for path in targets:
        text = path.read_text(encoding="utf-8")
        blocks: list[str] = []
        for marker in phase2_markers:
            start = text.find(f"def {marker}")
            if start == -1:
                start = text.find(marker)
            if start == -1:
                continue
            blocks.append(text[start : start + 4000])
        assert blocks, f"expected phase2 markers in {path.name}"
        combined = "\n".join(blocks)
        for literal in _FORBIDDEN_LITERALS:
            assert literal not in combined, f"forbidden literal {literal!r} in phase2 block of {path.name}"
        assert not skill_id_pattern.search(combined), f"unexpected skill_id literal in phase2 block of {path.name}"
        assert not example_id_pattern.search(combined), (
            f"unexpected textbook_example_id literal in phase2 block of {path.name}"
        )
