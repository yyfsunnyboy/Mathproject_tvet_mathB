# -*- coding: utf-8 -*-
"""Phase 3 unified domain authority tests (abstract fixtures only)."""

from __future__ import annotations

import copy
import json
import re
import sqlite3
from pathlib import Path
from unittest import mock

import pytest

from core.gencode.services.v3_publish_eligibility import evaluate_v3_publish_eligibility
from core.gencode.skill_fixed_domain_authority import (
    DOMAIN_BINDING_CONFLICT,
    DOMAIN_EVIDENCE_INCOMPLETE,
    DOMAIN_PROVIDER_MISSING,
    SkillFixedDomainError,
    DOMAIN_PROVIDERS,
    resolve_domain_authority,
    validate_component_domain_evidence,
    validate_publish_component_record,
)
from core.registry import taxonomy_registry
from core.registry.taxonomy_registry import SkillDomainNotRegisteredError, get_fixed_domain_key


ABSTRACT_SKILL = "abstract_unbound_skill_alpha"
ABSTRACT_DOMAIN = "abstract.domain.alpha"
ABSTRACT_OPERATION = "op_alpha"


@pytest.fixture
def abstract_providers() -> dict[str, dict]:
    return {
        ABSTRACT_DOMAIN: {
            "domain_module": "tests.abstract.alpha_domain",
            "entrypoint": "build_alpha_matrix",
            "capabilities": ["cap_a", "cap_b"],
            "allowed_operations": [ABSTRACT_OPERATION, "op_beta"],
        },
        "abstract.domain.beta": {
            "domain_module": "tests.abstract.beta_domain",
            "entrypoint": "build_beta_matrix",
            "capabilities": ["cap_a"],
            "allowed_operations": ["op_other"],
        },
    }


def _derived_evidence(
    *,
    domain_key: str = ABSTRACT_DOMAIN,
    operation: str = ABSTRACT_OPERATION,
    matched: list[str] | None = None,
    required: list[str] | None = None,
) -> dict:
    provider = {
        ABSTRACT_DOMAIN: {
            "domain_module": "tests.abstract.alpha_domain",
            "entrypoint": "build_alpha_matrix",
            "capabilities": ["cap_a", "cap_b"],
            "allowed_operations": [ABSTRACT_OPERATION],
        }
    }.get(domain_key) or DOMAIN_PROVIDERS.get(domain_key) or {}
    return {
        "fixed_domain_key": domain_key,
        "domain_operation": operation,
        "problem_type_id": operation,
        "selected_operation": operation,
        "resolution_source": "derived_capability_match",
        "binding_status": "derived",
        "required_capabilities": required or ["cap_a", "cap_b"],
        "matched_capabilities": matched or ["cap_a", "cap_b"],
        "domain_module": provider.get("domain_module", "tests.abstract.alpha_domain"),
        "entrypoint": provider.get("entrypoint", "build_alpha_matrix"),
        "registry_revision": "test-revision",
        "integrity_gate_passed": True,
        "integrity_gate_version": "v1",
    }


def test_unbound_skill_uses_derived_binding(abstract_providers: dict[str, dict]) -> None:
    extra = {
        "problem_type_id": ABSTRACT_OPERATION,
        "required_capabilities": ["cap_a", "cap_b"],
        "classification_source": "test_induced_spec",
    }
    with mock.patch(
        "core.gencode.skill_fixed_domain_authority.DOMAIN_PROVIDERS",
        abstract_providers,
    ):
        result = resolve_domain_authority(ABSTRACT_SKILL, extra=extra)
    assert result.resolution_source == "derived_capability_match"
    assert result.binding_status == "derived"
    assert result.fixed_domain_key == ABSTRACT_DOMAIN


def test_confirmed_binding_regression() -> None:
    skill_id = "vh_數學B1_DistanceBetweenTwoParallelLines"
    result = resolve_domain_authority(skill_id)
    assert result.resolution_source == "confirmed_binding"
    assert result.binding_status == "confirmed"
    assert result.fixed_domain_key == get_fixed_domain_key(skill_id)


def test_confirmed_derived_capability_conflict() -> None:
    skill_id = "vh_數學B1_DistanceBetweenTwoParallelLines"
    extra = {
        "required_capabilities": ["cap_unknown_for_parallel_domain"],
        "classification_source": "test_induced_spec",
    }
    with pytest.raises(SkillFixedDomainError) as exc:
        resolve_domain_authority(skill_id, extra=extra)
    assert exc.value.code == DOMAIN_BINDING_CONFLICT
    assert exc.value.details.get("confirmed_domain")


@pytest.fixture
def memory_conn() -> sqlite3.Connection:
    from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE skills_info (
            skill_id TEXT PRIMARY KEY,
            skill_en_name TEXT,
            skill_ch_name TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE skill_curriculum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL
        )
        """
    )
    apply_tracker_ddl(conn)
    return conn


def _seed_derived_publish_fixture(conn: sqlite3.Connection) -> None:
    conn.execute(
        "INSERT INTO skills_info (skill_id, skill_en_name, skill_ch_name) VALUES (?, ?, ?)",
        (ABSTRACT_SKILL, ABSTRACT_SKILL, ABSTRACT_SKILL),
    )
    conn.execute("INSERT INTO skill_curriculum (skill_id) VALUES (?)", (ABSTRACT_SKILL,))
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (1, ?)",
        (ABSTRACT_SKILL,),
    )
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload
        ) VALUES (1, ?, 'src_1', 'verified', ?)
        """,
        (ABSTRACT_SKILL, json.dumps(_derived_evidence(), ensure_ascii=False)),
    )
    conn.commit()


def test_derived_binding_publish_eligibility_without_skill_registry(
    memory_conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_derived_publish_fixture(memory_conn)
    monkeypatch.setattr(
        "core.gencode.services.v3_publish_eligibility._load_v3_taxonomy_mvp_scope",
        lambda _path: {ABSTRACT_SKILL},
    )
    with mock.patch(
        "core.gencode.skill_fixed_domain_authority.DOMAIN_PROVIDERS",
        {
            ABSTRACT_DOMAIN: {
                "domain_module": "tests.abstract.alpha_domain",
                "entrypoint": "build_alpha_matrix",
                "capabilities": ["cap_a", "cap_b"],
                "allowed_operations": [ABSTRACT_OPERATION],
            }
        },
    ):
        eligibility = evaluate_v3_publish_eligibility(memory_conn, ABSTRACT_SKILL)
    assert eligibility["allowed"] is True
    assert eligibility["domain_binding_status"] == "derived_binding"
    assert eligibility["resolved_domain_key"] == ABSTRACT_DOMAIN


def test_publish_does_not_require_resolve_domain_for_skill(
    memory_conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _seed_derived_publish_fixture(memory_conn)
    monkeypatch.setattr(
        "core.gencode.services.v3_publish_eligibility._load_v3_taxonomy_mvp_scope",
        lambda _path: {ABSTRACT_SKILL},
    )

    def _fail_registry(*_args, **_kwargs):
        raise SkillDomainNotRegisteredError("skill_domain_not_registered")

    monkeypatch.setattr(
        "core.registry.taxonomy_registry.resolve_domain_for_skill",
        _fail_registry,
    )
    monkeypatch.setattr(
        "core.registry.taxonomy_registry.get_fixed_domain_key",
        _fail_registry,
    )
    with mock.patch(
        "core.gencode.skill_fixed_domain_authority.DOMAIN_PROVIDERS",
        {
            ABSTRACT_DOMAIN: {
                "domain_module": "tests.abstract.alpha_domain",
                "entrypoint": "build_alpha_matrix",
                "capabilities": ["cap_a", "cap_b"],
                "allowed_operations": [ABSTRACT_OPERATION],
            }
        },
    ):
        eligibility = evaluate_v3_publish_eligibility(memory_conn, ABSTRACT_SKILL)
    assert eligibility["allowed"] is True


def test_incomplete_derived_evidence_blocks_publish(memory_conn: sqlite3.Connection) -> None:
    incomplete = _derived_evidence()
    incomplete.pop("matched_capabilities")
    conn = memory_conn
    conn.execute(
        "INSERT INTO skills_info (skill_id, skill_en_name, skill_ch_name) VALUES (?, ?, ?)",
        (ABSTRACT_SKILL, ABSTRACT_SKILL, ABSTRACT_SKILL),
    )
    conn.execute("INSERT INTO skill_curriculum (skill_id) VALUES (?)", (ABSTRACT_SKILL,))
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (1, ?)",
        (ABSTRACT_SKILL,),
    )
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload
        ) VALUES (1, ?, 'src_1', 'verified', ?)
        """,
        (ABSTRACT_SKILL, json.dumps(incomplete, ensure_ascii=False)),
    )
    conn.commit()
    blockers = validate_publish_component_record(
        skill_id=ABSTRACT_SKILL,
        component_skill_id=ABSTRACT_SKILL,
        component_fixed_domain_key=ABSTRACT_DOMAIN,
        component_operation=ABSTRACT_OPERATION,
        component_status="verified",
        spec=incomplete,
    )
    assert any(str(b).startswith(DOMAIN_EVIDENCE_INCOMPLETE) for b in blockers)
    assert DOMAIN_BINDING_CONFLICT not in blockers


def test_missing_provider_blocks_publish() -> None:
    spec = _derived_evidence(domain_key="abstract.domain.removed")
    blockers = validate_component_domain_evidence(spec)
    assert DOMAIN_PROVIDER_MISSING in blockers


def test_derived_resolution_does_not_mutate_registry(
    abstract_providers: dict[str, dict],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before_domain = copy.deepcopy(taxonomy_registry.SKILL_TO_DOMAIN)
    before_profile = copy.deepcopy(taxonomy_registry.SKILL_DOMAIN_PROFILE)
    extra = {
        "required_capabilities": ["cap_a", "cap_b"],
        "problem_type_id": ABSTRACT_OPERATION,
    }
    with mock.patch(
        "core.gencode.skill_fixed_domain_authority.DOMAIN_PROVIDERS",
        abstract_providers,
    ):
        resolve_domain_authority(ABSTRACT_SKILL, extra=extra)
    assert taxonomy_registry.SKILL_TO_DOMAIN == before_domain
    assert taxonomy_registry.SKILL_DOMAIN_PROFILE == before_profile


def test_status_query_reports_derived_binding(memory_conn: sqlite3.Connection) -> None:
    from core.gencode.services.gencode_status_query_service import build_admin_skill_gencode_status_view

    _seed_derived_publish_fixture(memory_conn)
    with mock.patch(
        "core.gencode.skill_fixed_domain_authority.DOMAIN_PROVIDERS",
        {
            ABSTRACT_DOMAIN: {
                "domain_module": "tests.abstract.alpha_domain",
                "entrypoint": "build_alpha_matrix",
                "capabilities": ["cap_a", "cap_b"],
                "allowed_operations": [ABSTRACT_OPERATION],
            }
        },
    ):
        view = build_admin_skill_gencode_status_view(memory_conn, skill_id=ABSTRACT_SKILL)
    assert view.get("domain_binding_status") == "derived_binding"
    assert view.get("resolved_domain_key") == ABSTRACT_DOMAIN
    assert view.get("publish_ineligible_reason") != "DOMAIN_BINDING_MISSING"


_PHASE3_FILES = (
    "core/gencode/skill_fixed_domain_authority.py",
    "core/gencode/services/v3_publish_eligibility.py",
    "core/gencode/services/gencode_status_query_service.py",
    "core/registry/taxonomy_registry.py",
)


def test_phase3_production_changes_have_no_skill_or_example_literals() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    markers = (
        "resolve_domain_authority",
        "validate_component_domain_evidence",
        "summarize_skill_domain_binding",
        "get_confirmed_skill_binding",
        "domain_binding_status",
    )
    forbidden_topic_literals = ("CentralTendencyMeasures", "arithmetic_mean")
    skill_pattern = re.compile(r"vh_[\w\u4e00-\u9fff]+")
    example_pattern = re.compile(r"textbook_example_id\s*=\s*\d+")

    for rel_path in _PHASE3_FILES:
        text = (repo_root / rel_path).read_text(encoding="utf-8")
        blocks: list[str] = []
        for marker in markers:
            start = text.find(marker)
            if start == -1:
                continue
            blocks.append(text[start : start + 5000])
        combined = "\n".join(blocks)
        if not combined:
            continue
        for literal in forbidden_topic_literals:
            assert literal not in combined, f"forbidden literal in {rel_path}"
        if rel_path.endswith("taxonomy_registry.py"):
            continue
        assert not example_pattern.search(combined), f"example id literal in {rel_path} phase3 block"
