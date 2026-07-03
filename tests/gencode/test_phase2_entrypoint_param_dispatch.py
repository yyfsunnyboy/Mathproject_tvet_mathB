# -*- coding: utf-8 -*-
from __future__ import annotations

import pytest
from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint


def test_signature_style_1_division_point() -> None:
    # (skill_id, problem_type_id, spec, seed)
    called_with = {}

    def dummy_fn(skill_id, problem_type_id, spec, seed=None):
        called_with.update({
            "skill_id": skill_id,
            "problem_type_id": problem_type_id,
            "spec": spec,
            "seed": seed,
        })
        return {"ok": True}

    res = _v3_invoke_domain_entrypoint(
        dummy_fn,
        entrypoint_name="dummy_fn",
        domain_operation="op123",
        seed=42,
        curriculum_profile="cur1",
        difficulty_profile="diff1",
        constraints={"skill_id": "skill123", "val": "abc"},
    )
    assert res == {"ok": True}
    assert called_with == {
        "skill_id": "skill123",
        "problem_type_id": "op123",
        "spec": {"skill_id": "skill123", "val": "abc"},
        "seed": 42,
    }


def test_signature_style_2_legacy_line_equation() -> None:
    # (seed, line_type, curriculum_profile, difficulty_profile, constraints)
    called_with = {}

    def dummy_fn(seed, line_type, curriculum_profile, difficulty_profile, constraints=None):
        called_with.update({
            "seed": seed,
            "line_type": line_type,
            "curriculum_profile": curriculum_profile,
            "difficulty_profile": difficulty_profile,
            "constraints": constraints,
        })
        return {"ok": True}

    res = _v3_invoke_domain_entrypoint(
        dummy_fn,
        entrypoint_name="dummy_fn",
        domain_operation="op123",
        seed=42,
        curriculum_profile="cur1",
        difficulty_profile="diff1",
        constraints={"skill_id": "skill123"},
    )
    assert res == {"ok": True}
    assert called_with == {
        "seed": 42,
        "line_type": "op123",
        "curriculum_profile": "cur1",
        "difficulty_profile": "diff1",
        "constraints": {"skill_id": "skill123"},
    }


def test_signature_style_3_matrix_constraints() -> None:
    # (seed, domain_operation, curriculum_profile, difficulty_profile, constraints)
    called_with = {}

    def dummy_fn(seed, domain_operation, curriculum_profile, difficulty_profile, constraints=None):
        called_with.update({
            "seed": seed,
            "domain_operation": domain_operation,
            "curriculum_profile": curriculum_profile,
            "difficulty_profile": difficulty_profile,
            "constraints": constraints,
        })
        return {"ok": True}

    res = _v3_invoke_domain_entrypoint(
        dummy_fn,
        entrypoint_name="dummy_fn",
        domain_operation="op123",
        seed=42,
        curriculum_profile="cur1",
        difficulty_profile="diff1",
        constraints={"skill_id": "skill123"},
    )
    assert res == {"ok": True}
    assert called_with == {
        "seed": 42,
        "domain_operation": "op123",
        "curriculum_profile": "cur1",
        "difficulty_profile": "diff1",
        "constraints": {"skill_id": "skill123"},
    }


def test_signature_missing_required_argument() -> None:
    # Required argument 'missing_param' has no default and cannot be solved
    def dummy_fn(seed, missing_param):
        return {"ok": True}

    with pytest.raises(ValueError) as excinfo:
        _v3_invoke_domain_entrypoint(
            dummy_fn,
            entrypoint_name="dummy_fn",
            domain_operation="op123",
            seed=42,
            curriculum_profile="cur1",
            difficulty_profile="diff1",
            constraints={},
        )
    assert "domain_entrypoint_argument_missing" in str(excinfo.value)
