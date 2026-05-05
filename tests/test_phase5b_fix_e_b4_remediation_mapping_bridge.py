# -*- coding: utf-8 -*-
"""Phase 5B-Fix-E: B4 Chapter 1 remediation mapping bridge tests."""

from __future__ import annotations

import uuid

from app import create_app
from core.adaptive.session_engine import CatalogEntry, submit_and_get_next
from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
    B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST,
    synthetic_subskill_for_b4_skill,
)
from models import User, db

B4_VOLUME = "\u6578\u5b78B4"
S_COMBO_PROPERTIES = "vh_\u6578\u5b78B4_CombinationProperties"
S_COMBO_DEFINITION = "vh_\u6578\u5b78B4_CombinationDefinition"
S_BINOMIAL = "vh_\u6578\u5b78B4_BinomialTheorem"


def _make_user() -> User:
    user = User(
        username=f"pf5b_fix_e_{uuid.uuid4().hex[:10]}",
        password_hash="test-hash",
        role="student",
    )
    db.session.add(user)
    db.session.commit()
    return user


def _entry(skill_id: str, family_id: str, subskills: list[str] | None = None) -> CatalogEntry:
    return CatalogEntry(
        skill_id=skill_id,
        skill_name=skill_id,
        family_id=family_id,
        family_name=family_id,
        theme="phase5b_fix_e",
        subskill_nodes=list(subskills or []),
        notes="phase5b_fix_e test entry",
    )


def _step_payload(
    prev: dict,
    *,
    uid: int,
    step: int,
    correct: bool,
    mode: str = "teaching",
    skill_scope_ids: list[str] | None = None,
    skill_id: str = "",
) -> dict:
    payload = {
        "student_id": uid,
        "session_id": prev["session_id"],
        "step_number": step,
        "mode": mode,
        "entry_mode": "chapter" if mode == "teaching" else "",
        "practice_kind": "unit_practice" if mode == "teaching" else "",
        "learning_mode": "main" if mode == "teaching" else "",
        "curriculum": "vocational" if mode == "teaching" else "",
        "volume": "數學B4" if mode == "teaching" else "",
        "chapter_id": "1" if mode == "teaching" else "",
        "last_family_id": prev.get("target_family_id"),
        "last_subskills": prev.get("target_subskills", []),
        "is_correct": bool(correct),
        "user_answer": "wrong",
    }
    if mode == "teaching":
        if skill_id:
            payload["skill_id"] = skill_id
        if skill_scope_ids:
            payload["target_skill_ids"] = list(skill_scope_ids)
            payload["skill_ids"] = list(skill_scope_ids)
            payload["unit_skill_ids"] = list(skill_scope_ids)
    return payload


def test_fix_e_b4_repeated_wrong_produces_remediation_candidate_and_enters_remediation(monkeypatch) -> None:
    monkeypatch.setattr("core.adaptive.session_engine.load_textbook_progression", lambda skill_id: None)
    monkeypatch.setattr(
        "core.adaptive.session_engine.load_catalog",
        lambda path=None: [
            _entry(
                S_COMBO_PROPERTIES,
                "B4C1_SYN_01",
                [synthetic_subskill_for_b4_skill(S_COMBO_PROPERTIES)],
            ),
            _entry(
                S_COMBO_DEFINITION,
                "B4C1_SYN_02",
                [synthetic_subskill_for_b4_skill(S_COMBO_DEFINITION)],
            ),
        ],
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine.select_route_action_with_ppo",
        lambda route_state, action_mask, model=None: ("stay", [0.0, 0.0, 0.0], 0, "ppo"),
    )

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        uid = _make_user().id
        skill_scope = [
            S_COMBO_PROPERTIES,
            S_COMBO_DEFINITION,
        ]
        first = submit_and_get_next(
            {
                "student_id": uid,
                "step_number": 0,
                "mode": "teaching",
                "entry_mode": "chapter",
                "practice_kind": "unit_practice",
                "learning_mode": "main",
                "curriculum": "vocational",
                "volume": B4_VOLUME,
                "chapter_id": "1",
                "skill_id": S_COMBO_PROPERTIES,
                "target_skill_ids": skill_scope,
                "skill_ids": skill_scope,
                "unit_skill_ids": skill_scope,
            }
        )
        r1 = submit_and_get_next(
            _step_payload(
                first,
                uid=uid,
                step=1,
                correct=False,
                skill_scope_ids=skill_scope,
                skill_id=S_COMBO_PROPERTIES,
            )
        )
        r2 = submit_and_get_next(
            _step_payload(
                r1,
                uid=uid,
                step=2,
                correct=False,
                skill_scope_ids=skill_scope,
                skill_id=S_COMBO_PROPERTIES,
            )
        )
        r3 = submit_and_get_next(
            _step_payload(
                r2,
                uid=uid,
                step=3,
                correct=False,
                skill_scope_ids=skill_scope,
                skill_id=S_COMBO_PROPERTIES,
            )
        )

    assert r3.get("remediation_review_ready") is True
    assert r3.get("final_route_action") == "remediate"
    assert r3.get("in_remediation") is True
    assert str(r3.get("selected_prereq_skill") or "") == "polynomial_arithmetic"
    remediation_candidates = r3.get("remediation_candidates") or []
    assert remediation_candidates
    first_subskill = str(r3.get("selected_prereq_subskill") or "")
    assert first_subskill.startswith("b4_skill::vh_數學B4_")


def test_fix_e_b4_remediation_target_is_allowlisted_and_deterministic(monkeypatch) -> None:
    monkeypatch.setattr("core.adaptive.session_engine.load_textbook_progression", lambda skill_id: None)
    monkeypatch.setattr(
        "core.adaptive.session_engine.load_catalog",
        lambda path=None: [
            _entry(
                S_BINOMIAL,
                "B4C1_SYN_01",
                [synthetic_subskill_for_b4_skill(S_BINOMIAL)],
            ),
            _entry(
                S_COMBO_DEFINITION,
                "B4C1_SYN_02",
                [synthetic_subskill_for_b4_skill(S_COMBO_DEFINITION)],
            ),
        ],
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine.select_route_action_with_ppo",
        lambda route_state, action_mask, model=None: ("remediate", [0.0, 0.0, 0.0], 1, "ppo"),
    )

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        uid = _make_user().id
        skill_scope = [S_BINOMIAL, S_COMBO_DEFINITION]
        first = submit_and_get_next(
            {
                "student_id": uid,
                "step_number": 0,
                "mode": "teaching",
                "entry_mode": "chapter",
                "practice_kind": "unit_practice",
                "learning_mode": "main",
                "curriculum": "vocational",
                "volume": B4_VOLUME,
                "chapter_id": "1",
                "skill_id": S_BINOMIAL,
                "target_skill_ids": skill_scope,
                "skill_ids": skill_scope,
                "unit_skill_ids": skill_scope,
            }
        )
        r1 = submit_and_get_next(
            _step_payload(
                first,
                uid=uid,
                step=1,
                correct=False,
                skill_scope_ids=skill_scope,
                skill_id=S_BINOMIAL,
            )
        )
        r2 = submit_and_get_next(
            _step_payload(
                r1,
                uid=uid,
                step=2,
                correct=False,
                skill_scope_ids=skill_scope,
                skill_id=S_BINOMIAL,
            )
        )
        response = submit_and_get_next(
            _step_payload(
                r2,
                uid=uid,
                step=3,
                correct=False,
                skill_scope_ids=skill_scope,
                skill_id=S_BINOMIAL,
            )
        )

    subskill = str(response.get("selected_prereq_subskill") or "")
    assert subskill.startswith("b4_skill::")
    target_skill_id = subskill.replace("b4_skill::", "", 1)
    assert target_skill_id in B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST
    assert str(response.get("selected_prereq_skill") or "") == "polynomial_arithmetic"


def test_fix_e_non_b4_behavior_unchanged_no_bridge_override(monkeypatch) -> None:
    monkeypatch.setattr("core.adaptive.session_engine.load_textbook_progression", lambda skill_id: None)
    monkeypatch.setattr(
        "core.adaptive.session_engine.load_catalog",
        lambda path=None: [_entry("jh_數學1上_FourArithmeticOperationsOfIntegers", "I1", ["add_sub"])],
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine._apply_demo_safe_family_filter",
        lambda entries, mode, system_skill_id: entries,
    )
    monkeypatch.setattr(
        "core.adaptive.session_engine.select_route_action_with_ppo",
        lambda route_state, action_mask, model=None: ("stay", [0.0, 0.0, 0.0], 0, "ppo"),
    )

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        uid = _make_user().id
        first = submit_and_get_next(
            {
                "student_id": uid,
                "step_number": 0,
                "mode": "teaching",
                "skill_id": "jh_數學1上_FourArithmeticOperationsOfIntegers",
                "unit_skill_ids": ["jh_數學1上_FourArithmeticOperationsOfIntegers"],
            }
        )
        response = submit_and_get_next(
            {
                "student_id": uid,
                "session_id": first["session_id"],
                "step_number": 1,
                "mode": "teaching",
                "last_family_id": first.get("target_family_id"),
                "last_subskills": first.get("target_subskills", []),
                "is_correct": False,
                "user_answer": "wrong",
            }
        )

    assert not bool(response.get("in_remediation"))
    assert str(response.get("final_route_action") or "") == "stay"
