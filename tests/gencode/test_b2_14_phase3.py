# -*- coding: utf-8 -*-
from __future__ import annotations
import importlib
import json
import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import quote
import pytest

from app import create_app
from models import User
from core.gencode.answer_grading import attach_correct_answer_feedback
from core.gencode.b2_14_component_specs import SPECS, VIS
from core.gencode.services.gencode_status_query_service import (
    build_admin_skills_gencode_status_map,
    inspect_skill_runtime_publication,
)

ROOT = Path(__file__).resolve().parents[2]
COUNTS = {"vh_數學B2_SubSection_1_4_3": 8, "vh_數學B2_SubSection_1_4_4": 13}
ALL_SKILLS = [f"vh_數學B2_SubSection_1_4_{index}" for index in range(1, 5)]


def _wrapper(skill_id: str) -> Any:
    return importlib.import_module(f"skills.{skill_id}")


def _wrong(payload: dict[str, Any]) -> Any:
    correct = payload["correct_answer"]
    if isinstance(correct, dict):
        result = dict(correct)
        result[next(iter(result))] = "__wrong__"
        return result
    if payload["answer_type"] == "single_choice":
        return next(choice["value"] for choice in payload["choices"] if choice["value"] != correct)
    return "__wrong__"


@pytest.fixture()
def client() -> Any:
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User.query.order_by(User.id).first()
        assert user is not None
        user_id = user.id
    result = app.test_client()
    with result.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True
    return result


@pytest.mark.parametrize("skill_id,expected", COUNTS.items())
def test_manifest_wrapper_facade_and_runtime_selectability(skill_id: str, expected: int) -> None:
    package = importlib.import_module(f"agent_skills_v3.{skill_id}")
    facade = _wrapper(skill_id)
    manifest = json.loads((ROOT / "agent_skills_v3" / skill_id / "component_manifest.json").read_text(encoding="utf-8"))
    assert manifest["publish_status"] == "production_manifest_compiled"
    assert manifest["component_count"] == expected
    assert len(package.GENERATOR_KEYS) == len(package.GENERATOR_SPECS) == len(facade.GENERATOR_KEYS) == expected
    assert inspect_skill_runtime_publication(skill_id=skill_id)["runtime_ready"] is True
    source = (ROOT / "skills" / f"{skill_id}.py").read_text(encoding="utf-8").lower()
    assert "dispatch_generate" in source and "fallback" not in source and "nearest" not in source


@pytest.mark.parametrize("example_id", sorted(SPECS))
def test_all_published_components_runtime_checker_and_visual(example_id: int) -> None:
    spec = SPECS[example_id]
    wrapper = _wrapper(spec["skill_id"])
    payload = wrapper.generate(seed=19, component_id=f"src_{example_id}")
    assert payload["component_id"] == f"src_{example_id}"
    assert payload.get("fallback_used", False) is False
    assert payload["answer_contract"]
    assert wrapper.check(payload["correct_answer"], payload["correct_answer"], payload) is True
    assert wrapper.check(_wrong(payload), payload["correct_answer"], payload) is False
    if example_id in VIS:
        assert payload["visual_spec"]["asset_path"] == VIS[example_id]
        assert (ROOT / VIS[example_id]).is_file()
        assert payload["visual_spec"]["usage"] == "practice_scratchpad_background"
    else:
        assert not (payload.get("visual_spec") or {}).get("required")


def test_teacher_status_uses_complete_production_evidence() -> None:
    conn = sqlite3.connect("file:instance/kumon_math.db?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        status = build_admin_skills_gencode_status_map(conn, ALL_SKILLS)
    finally:
        conn.close()
    assert status[ALL_SKILLS[0]]["teacher_status"]["status_key"] == "not_generated"
    assert status[ALL_SKILLS[1]]["teacher_status"]["status_key"] == "not_generated"
    for skill_id in COUNTS:
        assert status[skill_id]["teacher_status"]["status_key"] == "published"
        assert status[skill_id]["manifest_complete"] is True
        assert status[skill_id]["published_count"] == COUNTS[skill_id]


@pytest.mark.parametrize("skill_id", COUNTS)
def test_practice_and_question_http_contract(client: Any, skill_id: str) -> None:
    encoded = quote(skill_id, safe="")
    assert client.get(f"/practice?skill={encoded}").status_code == 200
    response = client.get(f"/get_next_question?skill={encoded}&gen_seed=17&level=1")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["answer_contract"] and payload["correct_answer"] not in (None, "", {}, [])
    if (payload.get("visual_spec") or {}).get("required"):
        assert payload["visual_spec"]["asset_path"]


@pytest.mark.parametrize("example_id", [11657, 11665, 11659])
def test_wrong_feedback_and_correct_non_disclosure(example_id: int) -> None:
    spec = SPECS[example_id]
    payload = _wrapper(spec["skill_id"]).generate(seed=5, component_id=f"src_{example_id}")
    wrong = attach_correct_answer_feedback({"correct": False}, payload)
    right = attach_correct_answer_feedback({"correct": True}, payload)
    assert wrong.get("correct_answer_display")
    assert "correct_answer_display" not in right


def test_required_form_mismatch_feedback_contract() -> None:
    payload = _wrapper(SPECS[11663]["skill_id"]).generate(seed=5, component_id="src_11663")
    result = attach_correct_answer_feedback({"correct": False, "required_form_failed": True}, payload)
    assert result["mathematically_equivalent"] is True
    assert result["required_form_valid"] is False
    assert "格式不符合要求" in result["required_form_feedback"]
    assert result["correct_answer_display"]
