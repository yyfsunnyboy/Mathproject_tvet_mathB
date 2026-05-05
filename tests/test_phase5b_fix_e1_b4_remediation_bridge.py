# -*- coding: utf-8 -*-
"""Phase 5B-Fix-E1: B4-to-B4 remediation bridge tests."""

from __future__ import annotations

import uuid

from app import create_app
from core.adaptive.session_engine import CatalogEntry, submit_and_get_next
from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
    B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
    B4_CHAPTER_1_REMEDIATION_BRIDGE,
    B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES,
    B4_MANUAL_REVIEW_OR_UNAVAILABLE_SKILL_IDS,
    get_b4_chapter1_remediation_targets,
    validate_b4_deterministic_adaptive_generator_payload,
)
from models import User, db


def _make_user() -> User:
    user = User(
        username=f"pf5b_fix_e1_{uuid.uuid4().hex[:10]}",
        password_hash="test-hash",
        role="student",
    )
    db.session.add(user)
    db.session.commit()
    return user


def _entry(skill_id: str, family_id: str) -> CatalogEntry:
    return CatalogEntry(
        skill_id=skill_id,
        skill_name=skill_id,
        family_id=family_id,
        family_name=family_id,
        theme="phase5b_fix_e1",
        subskill_nodes=["b4_chapter1_bridge_remediation"],
        notes="phase5b_fix_e1 test entry",
    )


def test_b4_bridge_targets_are_allowlisted_and_not_manual_review() -> None:
    assert B4_CHAPTER_1_REMEDIATION_BRIDGE
    for source_skill, targets in B4_CHAPTER_1_REMEDIATION_BRIDGE.items():
        assert source_skill in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST
        assert targets
        for target in targets:
            assert target in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST
            assert target not in B4_MANUAL_REVIEW_OR_UNAVAILABLE_SKILL_IDS


def test_b4_bridge_targets_never_include_excluded_problem_types() -> None:
    # Bridge output is skill_id-only; excluded problem types remain guarded by payload validator.
    for source_skill in B4_CHAPTER_1_REMEDIATION_BRIDGE:
        for target in get_b4_chapter1_remediation_targets(source_skill):
            ok, reason = validate_b4_deterministic_adaptive_generator_payload(
                target,
                {"problem_type_id": "combination_basic"},
            )
            assert ok is True
            assert reason is None
            bad_ok, bad_reason = validate_b4_deterministic_adaptive_generator_payload(
                target,
                {"problem_type_id": "tree_diagram_listing"},
            )
            assert bad_ok is False
            assert str(bad_reason or "").startswith("excluded_problem_type:")
            assert "tree_diagram_listing" in B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES


def test_b4_repeated_wrong_enters_remediation_and_routes_to_bridge_target(monkeypatch) -> None:
    current_skill = "vh_數學B4_BinomialTheorem"
    expected_seed_target = "vh_數學B4_BinomialCoefficientIdentities"
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine.load_catalog",
        lambda path=None: [
            _entry(current_skill, "B4_F13"),
            _entry(expected_seed_target, "B4_F12"),
            _entry("vh_數學B4_CombinationDefinition", "B4_F08"),
        ],
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine.select_route_action_with_ppo",
        lambda **kwargs: ("stay", [0.0, 0.0, 0.0], 0, "mock_stay"),
    )
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id
        first = submit_and_get_next(
            {
                "student_id": uid,
                "step_number": 0,
                "mode": "teaching",
                "entry_mode": "chapter",
                "curriculum": "vocational",
                "volume": "數學B4",
                "chapter_id": "1",
                "practice_kind": "unit_practice",
                "learning_mode": "teaching",
                "skill_id": current_skill,
                "unit_skill_ids": [current_skill, expected_seed_target, "vh_數學B4_CombinationDefinition"],
            }
        )
        second = submit_and_get_next(
            {
                "student_id": uid,
                "session_id": first["session_id"],
                "step_number": 1,
                "mode": "teaching",
                "entry_mode": "chapter",
                "curriculum": "vocational",
                "volume": "數學B4",
                "chapter_id": "1",
                "practice_kind": "unit_practice",
                "learning_mode": "teaching",
                "last_family_id": first.get("target_family_id"),
                "last_subskills": first.get("target_subskills", []),
                "is_correct": False,
            }
        )
        third = submit_and_get_next(
            {
                "student_id": uid,
                "session_id": second["session_id"],
                "step_number": 2,
                "mode": "teaching",
                "entry_mode": "chapter",
                "curriculum": "vocational",
                "volume": "數學B4",
                "chapter_id": "1",
                "practice_kind": "unit_practice",
                "learning_mode": "teaching",
                "last_family_id": second.get("target_family_id"),
                "last_subskills": second.get("target_subskills", []),
                "is_correct": False,
            }
        )
    second_skill = str(second.get("new_question_data", {}).get("skill_id") or "")
    expected_targets = get_b4_chapter1_remediation_targets(second_skill)
    assert expected_targets
    expected_target = expected_targets[0]
    assert third.get("post_mode") == "remediation"
    assert third.get("in_remediation") is True
    assert third.get("route_action") == "remediate"
    assert third.get("remediation_skill") == expected_target
    assert third.get("remediation_subskill") == "b4_chapter1_bridge_remediation"
    assert third.get("remediation_review_ready") is True
    assert third.get("new_question_data", {}).get("skill_id") == expected_target
    assert third.get("why_remediate_masked") == "b4_bridge_safety_override"
    assert third.get("remediation_candidates")


def test_non_b4_behavior_unchanged_under_same_mock(monkeypatch) -> None:
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine.load_catalog",
        lambda path=None: [
            _entry("jh_數學1上_FourArithmeticOperationsOfIntegers", "I1"),
        ],
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine.select_route_action_with_ppo",
        lambda **kwargs: ("stay", [0.0, 0.0, 0.0], 0, "mock_stay"),
    )
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id
        response = submit_and_get_next(
            {
                "student_id": uid,
                "step_number": 0,
                "mode": "teaching",
                "skill_id": "jh_數學1上_FourArithmeticOperationsOfIntegers",
                "unit_skill_ids": ["jh_數學1上_FourArithmeticOperationsOfIntegers"],
            }
        )
    assert response.get("in_remediation") is False
    assert response.get("post_mode") != "remediation"
    assert response.get("why_remediate_masked") != "b4_bridge_safety_override"
