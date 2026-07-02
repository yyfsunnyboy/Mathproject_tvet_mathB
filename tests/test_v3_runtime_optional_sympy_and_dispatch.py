# -*- coding: utf-8 -*-
"""Generic V3 runtime: optional sympy + component/problem_type dispatch."""

from __future__ import annotations

import pytest

from core.gencode.runtime_skill_wrapper import (
    dispatch_problem_type,
    resolve_component_dispatch,
)
from core.gencode.validators import validate_generator_payload
from core.legacy_generator_adapter import invoke_skill_generate

SKILL_DISTANCE = "vh_數學B1_DistanceBetweenTwoPointsInPlane"
SKILL_DIVISION = "vh_數學B1_DivisionPointCoordinates"
SKILL_MIDPOINT = "vh_數學B1_MidpointCoordinates"
PT_DISTANCE = "compute_distance_between_two_points"
PT_DIVISION_SHORT = "compute_internal_division_point_coordinates"
PT_MIDPOINT = "text_short_compute_midpoint_coordinates"
COMPONENT_DISTANCE = "src_4436"
COMPONENT_DIVISION_SHORT = "src_4420"
COMPONENT_DIVISION_CHOICE = "src_4512"


def _non_symbolic_payload() -> dict:
    return {
        "skill_id": SKILL_MIDPOINT,
        "problem_type_id": PT_MIDPOINT,
        "question_text": "求 $A(1,2)$ 與 $B(5,8)$ 的中點座標。",
        "answer_type": "coordinate_pair",
        "choices": [],
        "answer": "(3,5)",
        "correct_answer": "(3,5)",
        "metadata": {
            "givens": {"A": [1, 2], "B": [5, 8]},
            "target": "(3,5)",
        },
    }


def _non_symbolic_spec() -> dict:
    return {
        "problem_type_id": PT_MIDPOINT,
        "answer_contract": {
            "answer_type": "coordinate_pair",
            "checker": "coordinate_pair_checker",
            "answer_equivalence": "ordered_tuple_exact",
        },
        "stem_contract": {"required_math_objects": ["coordinate_point"]},
    }


def _symbolic_spec() -> dict:
    return {
        "problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
        "answer_contract": {
            "answer_type": "expression",
            "checker": "expression_equivalence_checker",
            "answer_equivalence": "expression_equivalence",
        },
        "stem_contract": {
            "required_math_objects": ["symbolic_condition", "coordinate_point"],
        },
    }


class TestOptionalSympy:
    def test_non_symbolic_validate_without_sympy(self) -> None:
        errors = validate_generator_payload(
            _non_symbolic_payload(),
            problem_type_spec=_non_symbolic_spec(),
        )
        assert "sympy" not in " ".join(errors).lower()
        assert "system_error:sympy_dependency_missing" not in errors

    def test_symbolic_validate_fails_fast_without_sympy(self, monkeypatch) -> None:
        import builtins

        from core.gencode.validators import _run_semantic_checker

        real_import = builtins.__import__

        def blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "sympy" or str(name).startswith("sympy."):
                raise ModuleNotFoundError("No module named 'sympy'")
            return real_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr(builtins, "__import__", blocked_import)

        payload = {
            "question_text": "化簡 $2x+1$。",
            "answer_type": "expression",
            "choices": [],
            "answer": "2*x+1",
            "correct_answer": "2*x+1",
            "problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
            "metadata": {},
        }
        errors = _run_semantic_checker(payload, _symbolic_spec())
        assert any(e == "system_error:sympy_dependency_missing" for e in errors)

    def test_midpoint_generate_without_sympy(self) -> None:
        import skills.vh_數學B1_MidpointCoordinates as mod

        payload = invoke_skill_generate(
            mod,
            level=1,
            seed=17,
            problem_type_id=PT_MIDPOINT,
            skill_id=SKILL_MIDPOINT,
        )
        assert payload.get("problem_type_id")
        assert "sympy" not in str(payload).lower()


class TestPreciseDispatch:
    def test_resolve_component_from_problem_type(self) -> None:
        import skills.vh_數學B1_DistanceBetweenTwoPointsInPlane as mod

        cid = resolve_component_dispatch(
            mod.GENERATOR_SPECS,
            mod.GENERATOR_KEYS,
            problem_type_id=PT_DISTANCE,
            seed=3,
        )
        assert cid == COMPONENT_DISTANCE

    def test_component_id_not_replaced_by_random(self) -> None:
        import skills.vh_數學B1_DistanceBetweenTwoPointsInPlane as mod

        payload = mod.generate(level=1, seed=99, component_id=COMPONENT_DISTANCE)
        assert payload.get("component_id") == COMPONENT_DISTANCE
        assert payload.get("problem_type_id") == PT_DISTANCE

    def test_problem_type_id_routes_generate_for_skill(self) -> None:
        import skills.vh_數學B1_MidpointCoordinates as mod

        payload = invoke_skill_generate(
            mod,
            level=1,
            seed=5,
            problem_type_id=PT_MIDPOINT,
            skill_id=SKILL_MIDPOINT,
        )
        assert payload.get("problem_type_id") == PT_MIDPOINT

    def test_random_when_unspecified(self) -> None:
        import skills.vh_數學B1_DistanceBetweenTwoPointsInPlane as mod

        seen: set[str] = set()
        for seed in range(12):
            payload = mod.generate(level=1, seed=seed)
            seen.add(str(payload.get("component_id") or ""))
        assert len(seen) > 1

    def test_dispatch_problem_type_override(self) -> None:
        import skills.vh_數學B1_MidpointCoordinates as mod

        pt, strategy, _ = dispatch_problem_type(
            SKILL_MIDPOINT,
            mod.GENERATOR_SPECS,
            level=1,
            seed=1,
            problem_type_id=PT_MIDPOINT,
        )
        assert pt == PT_MIDPOINT
        assert strategy == "problem_type_id_override"

    def test_short_answer_and_single_choice_components(self) -> None:
        import skills.vh_數學B1_DivisionPointCoordinates as mod

        short_payload = mod.generate(level=1, seed=11, component_id=COMPONENT_DIVISION_SHORT)
        choice_payload = mod.generate(level=1, seed=11, component_id=COMPONENT_DIVISION_CHOICE)
        assert short_payload.get("component_id") == COMPONENT_DIVISION_SHORT
        assert choice_payload.get("component_id") == COMPONENT_DIVISION_CHOICE
        assert short_payload.get("presentation_mode") == "short_answer"
        assert choice_payload.get("presentation_mode") == "single_choice"


@pytest.fixture()
def logged_client():
    pytest.importorskip("sqlalchemy")
    import uuid
    from urllib.parse import quote

    from app import create_app
    from models import User, db

    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"rt_sympy_{uuid.uuid4().hex[:10]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client


class TestRouteSmoke:
    def test_short_answer_component_route_200(self, logged_client) -> None:
        from urllib.parse import quote

        resp = logged_client.get(
            f"/get_next_question?skill={quote(SKILL_DIVISION)}"
            f"&component_id={COMPONENT_DIVISION_SHORT}&gen_seed=41&level=1"
        )
        assert resp.status_code == 200, resp.get_json()
        data = resp.get_json() or {}
        assert not data.get("error"), data.get("error")
        assert data.get("component_id") == COMPONENT_DIVISION_SHORT
        assert data.get("presentation_mode") == "short_answer"

    def test_single_choice_component_route_200(self, logged_client) -> None:
        from urllib.parse import quote

        resp = logged_client.get(
            f"/get_next_question?skill={quote(SKILL_DIVISION)}"
            f"&component_id={COMPONENT_DIVISION_CHOICE}&gen_seed=43&level=1"
        )
        assert resp.status_code == 200, resp.get_json()
        data = resp.get_json() or {}
        assert not data.get("error"), data.get("error")
        assert data.get("component_id") == COMPONENT_DIVISION_CHOICE
        assert data.get("presentation_mode") == "single_choice"

    def test_unspecified_component_route_200(self, logged_client) -> None:
        from urllib.parse import quote

        resp = logged_client.get(
            f"/get_next_question?skill={quote(SKILL_DISTANCE)}&gen_seed=47&level=1"
        )
        assert resp.status_code == 200, resp.get_json()
        data = resp.get_json() or {}
        assert not data.get("error"), data.get("error")
        assert data.get("component_id")
        assert "No module named 'sympy'" not in str(data)
