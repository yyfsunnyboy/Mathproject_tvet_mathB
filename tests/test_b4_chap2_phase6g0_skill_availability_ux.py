# -*- coding: utf-8 -*-
"""Phase 6G-0: Chap2 skill availability / not-enabled public UX (SOP §8.1)."""

from __future__ import annotations

import importlib
import uuid

import pytest

from app import create_app
from models import User, db
from core.routes.practice import (
    B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR,
)

_FORBID_LEGACY_NOT_ENABLED = frozenset(
    {
        "skills.vh_數學B4_BasicConceptsOfSets",
        "skills.vh_數學B4_ProbabilityOperations",
        "skills.vh_數學B4_ApplicationsOfExpectation",
        "skills.vh_數學B4_MathematicalExpectation",
    }
)

# User-facing JSON must not echo internal phase labels or transport-encoding leaks (SOP §8.1).
_FORBIDDEN_IN_PUBLIC_RESPONSE = (
    "Phase 6C-1",
    "Phase 6D",
    "Phase 6E",
    "No module named",
    "Traceback",
    "vh_%E6",
    "vh_%2525",
)


def _login(client, user_id: int) -> None:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True


@pytest.fixture()
def logged_client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"b4_6g0_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


def _assert_no_forbidden_leaks(raw: str, error_field: str) -> None:
    for bad in _FORBIDDEN_IN_PUBLIC_RESPONSE:
        assert bad not in error_field, f"forbidden fragment in error: {bad!r}"
        assert bad not in raw, f"forbidden fragment in response body: {bad!r}"


def _patch_block_legacy_not_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    orig = importlib.import_module

    def _wrapped(name: str, package=None):
        if name in _FORBID_LEGACY_NOT_ENABLED:
            pytest.fail(f"legacy skills import must not run: {name}")
        return orig(name, package)

    monkeypatch.setattr(importlib, "import_module", _wrapped)


class TestEnabledChap2MainlineSkills:
    @pytest.mark.parametrize(
        "skill, gen_seed",
        [
            ("vh_數學B4_ProbabilityDefinition", 11),
            ("vh_數學B4_ProbabilityProperties", 22),
            ("vh_數學B4_ConditionalProbability", 12),
            ("vh_數學B4_IndependentEvents", 13),
            ("vh_數學B4_MathematicalExpectationDefinition", 14),
        ],
    )
    def test_get_next_question_200(self, logged_client, skill: str, gen_seed: int) -> None:
        r = logged_client.get(
            f"/get_next_question?skill={skill}&gen_seed={gen_seed}&level=1"
        )
        assert r.status_code == 200, r.get_data(as_text=True)
        body = r.get_json()
        assert body.get("new_question_text")
        assert body.get("problem_type_id")


class TestPhase6KOpenedSkillsNoLegacyImport:
    """Phase 6K closure: the four formerly not-enabled Chap2 skills are now
    enabled via deterministic generators. They must respond 200 AND must NOT
    import the legacy ``skills.<id>`` module path under any circumstance.
    """

    @pytest.mark.parametrize(
        "skill, gen_seed",
        [
            ("vh_數學B4_ProbabilityOperations", 31),
            ("vh_數學B4_ApplicationsOfExpectation", 32),
            ("vh_數學B4_MathematicalExpectation", 33),
            ("vh_數學B4_BasicConceptsOfSets", 34),
        ],
    )
    def test_phase6k_skills_now_200_no_legacy_import(
        self,
        logged_client,
        monkeypatch: pytest.MonkeyPatch,
        skill: str,
        gen_seed: int,
    ) -> None:
        _patch_block_legacy_not_enabled(monkeypatch)
        r = logged_client.get(
            f"/get_next_question?skill={skill}&gen_seed={gen_seed}&level=1"
        )
        assert r.status_code == 200, r.get_data(as_text=True)
        body = r.get_json() or {}
        assert body.get("new_question_text")
        assert body.get("problem_type_id")
        raw = r.get_data(as_text=True)
        _assert_no_forbidden_leaks(raw, "")

    def test_encoded_skill_id_resolves_through_deterministic(
        self, logged_client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_block_legacy_not_enabled(monkeypatch)
        enc = "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityOperations"
        r = logged_client.get(f"/get_next_question?skill={enc}&gen_seed=35&level=1")
        assert r.status_code == 200, r.get_data(as_text=True)
        body = r.get_json() or {}
        assert body.get("new_question_text")
        assert body.get("problem_type_id")
        raw = r.get_data(as_text=True)
        _assert_no_forbidden_leaks(raw, "")


class TestReservedListingProblemTypes:
    @pytest.mark.parametrize(
        "pid",
        ["sample_space_listing", "event_set_listing", "subset_listing"],
    )
    def test_public_reserved_message(self, logged_client, pid: str) -> None:
        r = logged_client.get(
            f"/get_next_question?skill=vh_數學B4_SampleSpaceAndEvents&problem_type={pid}"
        )
        assert r.status_code == 422
        body = r.get_json() or {}
        err = body.get("error") or ""
        assert err == B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR
        raw = r.get_data(as_text=True)
        _assert_no_forbidden_leaks(raw, err)
