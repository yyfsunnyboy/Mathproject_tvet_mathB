# -*- coding: utf-8 -*-
"""Final Phase-3 seal checks for Math B2 section 1-3."""

from __future__ import annotations

import importlib
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import quote

import pytest

from core.gencode.b2_13_component_specs import SPECS
from app import create_app
from models import User


ROOT = Path(__file__).resolve().parents[2]
SKILL_COUNTS = {
    "vh_數學B2_SubSection_1_3_1": 3,
    "vh_數學B2_SubSection_1_3_2": 3,
    "vh_數學B2_SubSection_1_3_4": 7,
    "vh_數學B2_SubSection_1_3_5": 3,
    "vh_數學B2_SubSection_1_3_6": 6,
    "vh_數學B2_SubSection_1_3_7": 7,
}


def _wrapper(skill_id: str) -> Any:
    return importlib.import_module(f"skills.{skill_id}")


def _wrong(payload: dict[str, Any]) -> Any:
    correct = payload["correct_answer"]
    if isinstance(correct, dict):
        result = dict(correct)
        result[next(iter(result))] = "__wrong__"
        return result
    if payload["answer_type"] == "single_choice":
        return next(row["value"] for row in payload["choices"] if row["value"] != correct)
    return "__wrong__"


@pytest.fixture()
def logged_client() -> Any:
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User.query.order_by(User.id).first()
        assert user is not None
        user_id = user.id
    client = app.test_client()
    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True
    return client


@pytest.mark.parametrize("skill_id,expected", SKILL_COUNTS.items())
def test_wrapper_import_count_manifest_and_no_fallback(skill_id: str, expected: int) -> None:
    wrapper = _wrapper(skill_id)
    assert len(wrapper.GENERATOR_KEYS) == expected
    assert len(wrapper.GENERATOR_SPECS) == expected
    assert len(set(wrapper.GENERATOR_KEYS)) == expected
    manifest = ROOT / "agent_skills_v3" / skill_id / "component_manifest.json"
    assert manifest.is_file()
    source = (ROOT / "skills" / f"{skill_id}.py").read_text(encoding="utf-8")
    assert "dispatch_generate" in source
    assert "fallback" not in source.lower()
    assert "nearest" not in source.lower()


@pytest.mark.parametrize("example_id", sorted(SPECS))
def test_published_component_runtime_and_shared_grading(example_id: int) -> None:
    spec = SPECS[example_id]
    wrapper = _wrapper(str(spec["skill_id"]))
    payload = wrapper.generate(seed=17, component_id=f"src_{example_id}")
    assert payload["component_id"] == f"src_{example_id}"
    assert payload["answer_type"] == spec["answer_type"]
    assert payload["correct_answer"] not in (None, "", {}, [])
    assert isinstance(payload["answer_contract"], dict)
    assert wrapper.check(payload["correct_answer"], payload["correct_answer"], payload) is True
    assert wrapper.check(_wrong(payload), payload["correct_answer"], payload) is False
    assert payload.get("fallback_used", False) is False


@pytest.mark.parametrize("skill_id", SKILL_COUNTS)
def test_practice_and_question_http_200(logged_client: Any, skill_id: str) -> None:
    encoded = quote(skill_id, safe="")
    assert logged_client.get(f"/practice?skill={encoded}").status_code == 200
    response = logged_client.get(f"/get_next_question?skill={encoded}&gen_seed=17&level=1")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["correct_answer"] not in (None, "", {}, [])
    assert isinstance(payload["answer_contract"], dict)


def test_special_runtime_contracts() -> None:
    wrapper = _wrapper("vh_數學B2_SubSection_1_3_7")
    table = wrapper.generate(seed=11, component_id="src_11651")
    assert table["answer_type"] == "table_fill"
    assert table["answer_contract"]["checker_key"] == "table_fill_checker"
    assert wrapper.check(table["correct_answer"], table["correct_answer"], table) is True

    choice = wrapper.generate(seed=11, component_id="src_11644")
    assert choice["answer_type"] == "single_choice"
    assert choice["correct_answer"] == choice["answer_contract"]["semantic_canonical_answer"]
    label = next(row["label"] for row in choice["choices"] if row["value"] == choice["correct_answer"])
    assert wrapper.check(label, choice["correct_answer"], choice) is True

    assert Counter(spec["operation"] for spec in SPECS.values())["compute_terminal_ray_trig_ratios"] == 3
    assert Counter(spec["operation"] for spec in SPECS.values())["complete_reference_angle_conversion"] == 1
    assert Counter(spec["operation"] for spec in SPECS.values())["solve_signed_trig_constraints"] == 6
