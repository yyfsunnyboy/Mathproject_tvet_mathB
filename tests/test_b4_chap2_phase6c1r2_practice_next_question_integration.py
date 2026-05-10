# -*- coding: utf-8 -*-
"""Phase 6C-1R2: /get_next_question + /check_answer HTTP integration (actual practice flow).

Simulates the same endpoints used by templates (e.g. fetch `/get_next_question?...`).
Guards must run *before* legacy `importlib.import_module("skills.<skill_id>")`.
"""

from __future__ import annotations

import importlib
import uuid

import pytest

from app import create_app
from models import User, db
from core.routes.practice import (
    B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR,
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
            username=f"b4_6c1r2_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    _login(client, uid)
    return client


# Legacy skills modules must not load for Chap2 Phase 6C-1 P0 deterministic path.
_LEGACY_CHAP2_P0_FORBIDDEN = frozenset(
    {
        "skills.vh_數學B4_ProbabilityDefinition",
        "skills.vh_數學B4_ProbabilityProperties",
        "skills.vh_數學B4_SampleSpaceAndEvents",
    }
)

_LEGACY_BASIC_CONCEPTS = "skills.vh_數學B4_BasicConceptsOfSets"


def _monkeypatch_forbid_legacy_chap2_p0(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail the test if any forbidden legacy Chap2 P0 skills module is imported."""
    orig = importlib.import_module

    def _wrapped(name: str, package=None):
        if name in _LEGACY_CHAP2_P0_FORBIDDEN:
            pytest.fail(f"unexpected legacy import (Phase 6C-1R2): {name}")
        return orig(name, package)

    monkeypatch.setattr(importlib, "import_module", _wrapped)


def _monkeypatch_forbid_basic_concepts(monkeypatch: pytest.MonkeyPatch) -> None:
    """BasicConceptsOfSets must return gate error without attempting skills module import."""
    orig = importlib.import_module

    def _wrapped(name: str, package=None):
        if name == _LEGACY_BASIC_CONCEPTS:
            pytest.fail("BasicConceptsOfSets must not trigger legacy skills import")
        return orig(name, package)

    monkeypatch.setattr(importlib, "import_module", _wrapped)


class TestGetNextQuestionChap2NoLegacyImport:
    @pytest.mark.parametrize(
        "skill, gen_seed, expect_pid",
        [
            ("vh_數學B4_ProbabilityDefinition", 11, "dice_coin_probability_count"),
            ("vh_數學B4_ProbabilityProperties", 22, "complement_probability"),
            ("vh_數學B4_SampleSpaceAndEvents", 33, "sample_space_count_numeric"),
        ],
    )
    def test_next_question_200_and_problem_type(
        self, logged_client, monkeypatch, skill, gen_seed, expect_pid
    ) -> None:
        _monkeypatch_forbid_legacy_chap2_p0(monkeypatch)
        r = logged_client.get(
            f"/get_next_question?skill={skill}&gen_seed={gen_seed}&level=1"
        )
        assert r.status_code == 200, r.get_data(as_text=True)
        body = r.get_json()
        assert body.get("new_question_text")
        assert body.get("problem_type_id") == expect_pid
        assert body.get("answer_type") in ("rational_fraction", "integer")

    def test_encoded_skill_id_decodes(self, logged_client, monkeypatch) -> None:
        _monkeypatch_forbid_legacy_chap2_p0(monkeypatch)
        enc = "vh_%E6%95%B8%E5%AD%B8B4_ProbabilityDefinition"
        r = logged_client.get(f"/get_next_question?skill={enc}&gen_seed=7&level=1")
        assert r.status_code == 200
        assert r.get_json().get("problem_type_id") == "dice_coin_probability_count"

    def test_complement_explicit_problem_type(self, logged_client, monkeypatch) -> None:
        _monkeypatch_forbid_legacy_chap2_p0(monkeypatch)
        r = logged_client.get(
            "/get_next_question?skill=vh_數學B4_ProbabilityProperties"
            "&problem_type=complement_probability&gen_seed=3&level=1"
        )
        assert r.status_code == 200
        assert r.get_json().get("problem_type_id") == "complement_probability"

    def test_sample_space_variety_visible_with_gen_seed(self, logged_client, monkeypatch) -> None:
        _monkeypatch_forbid_legacy_chap2_p0(monkeypatch)
        seen = {"coin": False, "dice": False, "seq": False}
        for seed in range(1, 31):
            r = logged_client.get(
                "/get_next_question?skill=vh_數學B4_SampleSpaceAndEvents"
                f"&gen_seed={seed}&level=1"
            )
            assert r.status_code == 200
            q = str(r.get_json().get("new_question_text", ""))
            if "硬幣" in q:
                seen["coin"] = True
            if "骰子" in q or "面骰" in q:
                seen["dice"] = True
            if "階段" in q or "步驟" in q:
                seen["seq"] = True
        assert all(seen.values()), f"missing variety from route flow: {seen}"


class TestGetNextQuestionChap2GatedSkills:
    def test_basic_concepts_now_enabled_no_legacy_import(self, logged_client, monkeypatch) -> None:
        # Phase 6K: BasicConceptsOfSets is now enabled via deterministic
        # generator. The route must return 200 AND must NOT import the
        # legacy ``skills.vh_數學B4_BasicConceptsOfSets`` module path.
        _monkeypatch_forbid_basic_concepts(monkeypatch)
        r = logged_client.get(
            "/get_next_question?skill=vh_數學B4_BasicConceptsOfSets&gen_seed=37&level=1"
        )
        assert r.status_code == 200, r.get_data(as_text=True)
        body = r.get_json() or {}
        assert body.get("new_question_text")
        assert body.get("problem_type_id")
        raw = r.get_data(as_text=True)
        assert "No module named" not in raw

    @pytest.mark.parametrize(
        "pid",
        ["sample_space_listing", "event_set_listing", "subset_listing"],
    )
    def test_listing_problem_types_remain_blocked(self, logged_client, pid: str) -> None:
        r = logged_client.get(
            f"/get_next_question?skill=vh_數學B4_SampleSpaceAndEvents&problem_type={pid}"
        )
        assert r.status_code == 422
        body = r.get_json()
        assert body.get("error") == B4_CHAP2_RESERVED_PROBLEM_TYPE_PUBLIC_ERROR
        txt = r.get_data(as_text=True)
        assert "handwriting" in txt or "reserved" in txt


class TestCheckAnswerChap2FlowUsesSessionNoLegacyImport:
    """Full round-trip via HTTP + session cookie."""

    def test_rational_equivalents(self, logged_client, monkeypatch) -> None:
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill

        seed = 9
        p = generate_for_chap2_skill(
            skill_id="vh_數學B4_ProbabilityDefinition",
            problem_type_id="classical_probability_fraction",
            level=1,
            seed=seed,
        )
        ca = str(p["correct_answer"])

        _monkeypatch_forbid_legacy_chap2_p0(monkeypatch)
        rq = logged_client.get(
            "/get_next_question?skill=vh_數學B4_ProbabilityDefinition"
            f"&problem_type=classical_probability_fraction&gen_seed={seed}&level=1"
        )
        assert rq.status_code == 200

        ok = logged_client.post("/check_answer", json={"answer": ca})
        assert ok.get_json().get("correct") is True

        if "/" in ca:
            num_str, den_str = ca.split("/", 1)
            unreduced = f"{int(num_str) * 2}/{int(den_str) * 2}"
            logged_client.get(
                "/get_next_question?skill=vh_數學B4_ProbabilityDefinition"
                f"&problem_type=classical_probability_fraction&gen_seed={seed}&level=1"
            )
            u = logged_client.post("/check_answer", json={"answer": unreduced})
            assert u.get_json().get("correct") is True

        logged_client.get(
            "/get_next_question?skill=vh_數學B4_ProbabilityDefinition"
            f"&problem_type=classical_probability_fraction&gen_seed={seed}&level=1"
        )
        from fractions import Fraction

        num_s, den_s = ca.split("/", 1)
        fra = Fraction(int(num_s), int(den_s))
        # Decimal round-trip is exact only for denominators with factors 2/5.
        tmp_den = fra.denominator
        while tmp_den % 2 == 0:
            tmp_den //= 2
        while tmp_den % 5 == 0:
            tmp_den //= 5
        if tmp_den == 1:
            dec_str = f"{float(fra):g}"
            assert (
                logged_client.post("/check_answer", json={"answer": dec_str}).get_json()[
                    "correct"
                ]
                is True
            )

        logged_client.get(
            "/get_next_question?skill=vh_數學B4_ProbabilityDefinition"
            f"&problem_type=classical_probability_fraction&gen_seed={seed}&level=1"
        )
        if tmp_den == 1:
            pct_str = f"{float(fra) * 100:g}%"
            assert (
                logged_client.post("/check_answer", json={"answer": pct_str}).get_json()[
                    "correct"
                ]
                is True
            )

        logged_client.get(
            f"/get_next_question?skill=vh_數學B4_ProbabilityDefinition&gen_seed={seed}&level=1"
        )
        bad = logged_client.post("/check_answer", json={"answer": "999/999"})
        assert bad.get_json().get("correct") is False

    def test_integer_strict_decimal_and_percent_false(self, logged_client, monkeypatch) -> None:
        from core.vocational_math_b4.services.question_router import generate_for_chap2_skill

        seed = 202
        p = generate_for_chap2_skill(
            skill_id="vh_數學B4_SampleSpaceAndEvents", level=1, seed=seed
        )
        ca = int(p["correct_answer"])

        _monkeypatch_forbid_legacy_chap2_p0(monkeypatch)

        logged_client.get(
            f"/get_next_question?skill=vh_數學B4_SampleSpaceAndEvents&gen_seed={seed}&level=1"
        )
        assert (
            logged_client.post("/check_answer", json={"answer": str(ca)}).get_json()[
                "correct"
            ]
            is True
        )

        logged_client.get(
            f"/get_next_question?skill=vh_數學B4_SampleSpaceAndEvents&gen_seed={seed}&level=1"
        )
        assert (
            logged_client.post(
                "/check_answer", json={"answer": f"{ca}.0"}
            ).get_json()["correct"]
            is False
        )

        logged_client.get(
            f"/get_next_question?skill=vh_數學B4_SampleSpaceAndEvents&gen_seed={seed}&level=1"
        )
        assert (
            logged_client.post("/check_answer", json={"answer": f"{ca}%"}).get_json()[
                "correct"
            ]
            is False
        )
