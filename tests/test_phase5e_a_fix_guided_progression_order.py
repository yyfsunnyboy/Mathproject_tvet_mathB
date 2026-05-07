# -*- coding: utf-8 -*-
"""Phase 5E-A-Fix: B4 Chapter 1 guided progression order tests."""

from __future__ import annotations

import random
import json
import uuid

from app import create_app
from core.adaptive.session_engine import submit_and_get_next
from core.routes.practice import _resolve_b4_chapter_adaptive_entry, _stable_b4_inner_seed
from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
    B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
    B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER,
    B4_CHAPTER_1_GUIDED_PROGRESSION_STEPS,
    B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES,
    B4_MANUAL_REVIEW_OR_UNAVAILABLE_SKILL_IDS,
    ordered_b4_chapter1_skills,
)
from core.vocational_math_b4.services.question_router import generate_for_skill
from models import User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _make_user() -> User:
    user = User(
        username=f"pf5e_a_{uuid.uuid4().hex[:10]}",
        password_hash="test-hash",
        role="student",
    )
    db.session.add(user)
    db.session.commit()
    return user


def _b4_payload(*, user_id: int, step_number: int, unit_skill_ids: list[str] | None = None) -> dict:
    ordered_pool = list(unit_skill_ids or B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER)
    return {
        "student_id": user_id,
        "step_number": step_number,
        "mode": "teaching",
        "entry_mode": "chapter",
        "curriculum": "vocational",
        "volume": "數學B4",
        "chapter_id": "1",
        "learning_mode": "teaching",
        "practice_kind": "unit_practice",
        "skill_id": ordered_pool[0],
        "starter_skill_id": ordered_pool[0],
        "target_skill_ids": ordered_pool,
        "skill_ids": ordered_pool,
        "unit_skill_ids": ordered_pool,
    }


def test_progression_order_constant_is_allowlisted_and_excludes_manual_review() -> None:
    assert len(B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER) == 13
    assert set(B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER) == set(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST)
    assert not (set(B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER) & set(B4_MANUAL_REVIEW_OR_UNAVAILABLE_SKILL_IDS))
    assert "vh_數學B4_TreeDiagramCounting" not in B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER
    assert "vh_數學B4_PascalTriangle" not in B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER
    assert B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES == {
        "tree_diagram_listing",
        "binomial_expansion_basic",
        "pascal_triangle_derivation",
    }


def test_ordered_b4_chapter1_skills_orders_known_and_keeps_unknown_stable_last() -> None:
    unknown_a = "vh_數學B4_ExperimentalUnknownA"
    unknown_b = "not_a_b4_skill"
    shuffled = [
        "vh_數學B4_BinomialTheorem",
        unknown_a,
        "vh_數學B4_AdditionPrinciple",
        "vh_數學B4_PermutationOfDistinctObjects",
        unknown_b,
        "vh_數學B4_MultiplicationPrinciple",
        "vh_數學B4_TreeDiagramCounting",
    ]

    assert ordered_b4_chapter1_skills(shuffled) == [
        "vh_數學B4_AdditionPrinciple",
        "vh_數學B4_MultiplicationPrinciple",
        "vh_數學B4_PermutationOfDistinctObjects",
        "vh_數學B4_BinomialTheorem",
        unknown_a,
        unknown_b,
    ]


def test_chapter_entry_injects_progression_order_and_addition_starter() -> None:
    resolved, hit = _resolve_b4_chapter_adaptive_entry(
        mode="chapter",
        curriculum="vocational",
        volume="數學B4",
        chapter_id="1",
        skill_ids="",
    )
    assert hit is True
    assert resolved["unit_skill_ids"] == list(B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER)
    assert resolved["starter_skill_id"] == "vh_數學B4_AdditionPrinciple"
    assert resolved["bootstrap_unit_skill_ids"][:3] == [
        "vh_數學B4_AdditionPrinciple",
        "vh_數學B4_MultiplicationPrinciple",
        "vh_數學B4_FactorialNotation",
    ]


def test_chapter_entry_template_context_uses_progression_order() -> None:
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    resp = client.get(
        "/adaptive_practice?mode=chapter&curriculum=vocational&volume=數學B4&chapter_id=1&learning_mode=teaching&practice_kind=unit_practice"
    )
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    first_skill = json.dumps("vh_數學B4_AdditionPrinciple")
    second_skill = json.dumps("vh_數學B4_MultiplicationPrinciple")
    third_skill = json.dumps("vh_數學B4_FactorialNotation")
    first = body.index(first_skill)
    second = body.index(second_skill)
    third = body.index(third_skill)
    assert first < second < third
    assert f"const starterSkillId = {first_skill};" in body


def test_guided_progression_early_stage_selects_textbook_order(monkeypatch) -> None:
    monkeypatch.setattr("core.adaptive.session_engine.load_catalog", lambda path=None: [])
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id
        expected = [
            "vh_數學B4_AdditionPrinciple",
            "vh_數學B4_MultiplicationPrinciple",
            "vh_數學B4_FactorialNotation",
        ]
        for step, skill_id in enumerate(expected):
            response = submit_and_get_next(_b4_payload(user_id=uid, step_number=step))
            q = response["new_question_data"]
            assert q["skill_id"] == skill_id
            audit = q.get("adaptive_audit") or {}
            assert audit.get("progression_mode") == "guided_progression"
            assert audit.get("selection_reason") == "b4_guided_progression_order"


def test_guided_progression_does_not_jump_to_binomial_in_first_steps(monkeypatch) -> None:
    monkeypatch.setattr("core.adaptive.session_engine.load_catalog", lambda path=None: [])
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id
        for step in range(3):
            response = submit_and_get_next(_b4_payload(user_id=uid, step_number=step))
            sid = response["new_question_data"]["skill_id"]
            assert sid not in {
                "vh_數學B4_BinomialTheorem",
                "vh_數學B4_BinomialCoefficientIdentities",
            }


def test_remediation_priority_skips_guided_progression(monkeypatch) -> None:
    monkeypatch.setattr("core.adaptive.session_engine.load_catalog", lambda path=None: [])
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine.choose_next_family",
        lambda **kwargs: kwargs["entries"][0],
    )

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id
        payload = _b4_payload(user_id=uid, step_number=1)
        payload["routing_state"] = {
            "in_remediation": True,
            "remediation_skill_id": "vh_數學B4_MultiplicationPrinciple",
            "steps_taken": 1,
            "recent_results": [False],
        }
        payload["post_mode"] = "remediation"
        response = submit_and_get_next(payload)
        q = response["new_question_data"]
        assert q["skill_id"] == "vh_數學B4_MultiplicationPrinciple"
        assert (q.get("adaptive_audit") or {}).get("progression_mode") == "adaptive_mixed"


def test_mixed_stage_after_guided_progression_preserves_seed_exposure() -> None:
    targets = {
        "binomial_two_variable_specific_coefficient",
        "binomial_laurent_specific_power_coefficient",
        "grid_shortest_path_count",
        "permutation_non_adjacent_arrangement",
        "factorial_equation_solve_n",
    }
    seen = {pid: 0 for pid in targets}
    pool = list(B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER)

    assert B4_CHAPTER_1_GUIDED_PROGRESSION_STEPS == 10
    for seed in range(1, 501):
        skill_id = random.Random(seed).choice(pool)
        inner_seed = _stable_b4_inner_seed(skill_id, seed)
        payload = generate_for_skill(
            skill_id=skill_id,
            level=1,
            seed=inner_seed,
            multiple_choice=True,
        )
        pid = payload.get("problem_type_id")
        if pid in seen:
            seen[pid] += 1

    for pid, count in seen.items():
        assert count > 0, f"{pid} should remain visible in wider mixed-stage sampling."


def test_excluded_problem_types_remain_blocked_in_wide_sampling() -> None:
    excluded_counts = {pid: 0 for pid in B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES}
    pool = list(B4_CHAPTER_1_CURRICULUM_PROGRESSION_ORDER)

    for seed in range(1, 501):
        skill_id = random.Random(seed).choice(pool)
        inner_seed = _stable_b4_inner_seed(skill_id, seed)
        payload = generate_for_skill(
            skill_id=skill_id,
            level=1,
            seed=inner_seed,
            multiple_choice=True,
        )
        pid = payload.get("problem_type_id")
        if pid in excluded_counts:
            excluded_counts[pid] += 1

    assert excluded_counts == {
        "tree_diagram_listing": 0,
        "binomial_expansion_basic": 0,
        "pascal_triangle_derivation": 0,
    }
