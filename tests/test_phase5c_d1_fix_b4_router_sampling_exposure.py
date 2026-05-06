# -*- coding: utf-8 -*-
"""Phase 5C-D1-Fix: B4 router sampling exposure calibration tests."""

from __future__ import annotations

import random
import uuid

from app import create_app
from core.routes.practice import _stable_b4_inner_seed
from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
    B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
    B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES,
    validate_b4_deterministic_adaptive_generator_payload,
)
from core.vocational_math_b4.services.question_router import generate_for_skill
from models import User, db


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


def _make_user() -> User:
    user = User(
        username=f"pf5c_d1_fix_{uuid.uuid4().hex[:10]}",
        password_hash="test-hash",
        role="student",
    )
    db.session.add(user)
    db.session.commit()
    return user


def _payload(skill_id: str, seed_used: int) -> dict:
    return {
        "question_text": f"seed={seed_used}",
        "answer": "1",
        "correct_answer": "1",
        "context_string": "",
        "image_base64": "",
        "visual_aids": [],
        "skill_id": skill_id,
        "subskill_id": "dummy_subskill",
        "problem_type_id": "combination_definition_basic",
        "generator_key": "b4.combination.combination_definition_basic",
        "router_trace": {
            "selection_reason": "seed_based_selection",
            "selected_problem_type_id": "combination_definition_basic",
            "selected_generator_key": "b4.combination.combination_definition_basic",
        },
    }


def test_stable_inner_seed_is_deterministic_and_changes_with_inputs() -> None:
    s1 = _stable_b4_inner_seed("vh_數學B4_BinomialTheorem", 101)
    s2 = _stable_b4_inner_seed("vh_數學B4_BinomialTheorem", 101)
    s3 = _stable_b4_inner_seed("vh_數學B4_BinomialTheorem", 102)
    s4 = _stable_b4_inner_seed("vh_數學B4_CombinationApplications", 101)
    assert s1 == s2
    assert s1 != s3
    assert s1 != s4


def test_pure_b4_generator_first_path_uses_derived_inner_seed(monkeypatch) -> None:
    captured: dict[str, int] = {}
    selected_skill = "vh_數學B4_CombinationDefinition"
    outer_seed = 73
    expected_inner = _stable_b4_inner_seed(selected_skill, outer_seed)

    class _FakeMod:
        @staticmethod
        def generate(level=1, **kwargs):
            captured["seed"] = kwargs.get("seed")
            return _payload(selected_skill, kwargs.get("seed"))

    monkeypatch.setattr("core.routes.practice.recommend_question", lambda _u, _s: None)
    monkeypatch.setattr("core.routes.practice.get_skill", lambda _sid: _FakeMod())

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    with client.session_transaction() as sess:
        sess["review_skill_pool"] = [selected_skill]

    resp = client.get(
        f"/get_adaptive_question?mode=review&curriculum=vocational&gen_seed={outer_seed}&adaptive_audit=1"
    )
    assert resp.status_code == 200
    assert captured["seed"] == expected_inner
    body = resp.get_json()
    assert body["adaptive_audit"]["outer_gen_seed"] == outer_seed
    assert body["adaptive_audit"]["inner_router_seed"] == expected_inner
    assert body["adaptive_audit"]["seed_derivation"] == "b4_stable_inner_seed"


def test_non_pure_b4_path_keeps_original_gen_seed(monkeypatch) -> None:
    captured: dict[str, int] = {}
    outer_seed = 37

    class _FakeMod:
        @staticmethod
        def generate(level=1, **kwargs):
            captured["seed"] = kwargs.get("seed")
            return _payload("vh_數學B4_CombinationDefinition", kwargs.get("seed"))

    monkeypatch.setattr("core.routes.practice.recommend_question", lambda _u, _s: None)
    monkeypatch.setattr("core.adaptive_engine.select_review_skill", lambda pool, stats, last_skill: pool[0])
    monkeypatch.setattr("core.routes.practice.get_skill", lambda _sid: _FakeMod())

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = _make_user()
        uid = user.id

    client = app.test_client()
    _login(client, uid)
    with client.session_transaction() as sess:
        sess["review_skill_pool"] = [
            "jh_數學1上_FourArithmeticOperationsOfIntegers",
            "vh_數學B4_CombinationDefinition",
        ]

    resp = client.get(
        f"/get_adaptive_question?mode=review&curriculum=vocational&gen_seed={outer_seed}&adaptive_audit=1"
    )
    assert resp.status_code == 200
    assert captured["seed"] == outer_seed
    body = resp.get_json()
    assert body["adaptive_audit"]["outer_gen_seed"] == outer_seed
    assert body["adaptive_audit"]["inner_router_seed"] == outer_seed
    assert body["adaptive_audit"]["seed_derivation"] == "identity"


def test_seed_sampling_makes_phase5c_targets_visible_and_preserves_validator() -> None:
    targets = {
        "binomial_two_variable_specific_coefficient",
        "binomial_laurent_specific_power_coefficient",
        "grid_shortest_path_count",
        "permutation_non_adjacent_arrangement",
        "factorial_equation_solve_n",
    }
    seen = {k: 0 for k in targets}
    excluded_hits = 0
    validator_failures = []
    pool = sorted(B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST)

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
        if pid in B4_EXCLUDED_DETERMINISTIC_ADAPTIVE_PROBLEM_TYPES:
            excluded_hits += 1
        ok, reason = validate_b4_deterministic_adaptive_generator_payload(skill_id, payload)
        if not ok:
            validator_failures.append((seed, skill_id, reason))

    for pid in targets:
        assert seen[pid] > 0, f"{pid} should be visible after D1-Fix sampling calibration."
    assert excluded_hits == 0
    assert validator_failures == []
