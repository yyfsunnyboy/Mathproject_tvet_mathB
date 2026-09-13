from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from core.gencode.services.gencode_status_query_service import inspect_skill_runtime_publication


ROOT = Path(__file__).resolve().parents[1]


def _published_components() -> list[tuple[str, dict]]:
    rows: list[tuple[str, dict]] = []
    for manifest_path in sorted((ROOT / "agent_skills_v3").glob("vh_數學B1_*/component_manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        if manifest.get("publish_status") != "production_manifest_compiled":
            continue
        rows.extend((str(manifest["skill_id"]), dict(row)) for row in manifest["components"])
    return rows


PUBLISHED_COMPONENTS = _published_components()
PUBLISHED_SKILLS = sorted({skill_id for skill_id, _ in PUBLISHED_COMPONENTS})


def _verdict(value):
    return value.get("correct") if isinstance(value, dict) else value


def test_b1_production_inventory_is_runtime_selectable() -> None:
    formal_skills = list((ROOT / "skills").glob("vh_數學B1_*.py"))
    assert len(formal_skills) == 33
    assert len(PUBLISHED_SKILLS) == 23
    assert len(PUBLISHED_COMPONENTS) == 233
    for skill_id in PUBLISHED_SKILLS:
        publication = inspect_skill_runtime_publication(skill_id=skill_id, project_root=ROOT)
        assert publication["manifest_valid"] is True
        assert publication["package_wrapper_loadable"] is True
        assert publication["runtime_wrapper_loadable"] is True
        assert publication["runtime_ready"] is True


@pytest.mark.parametrize(
    ("skill_id", "component"),
    PUBLISHED_COMPONENTS,
    ids=[f"{skill_id}:{row['component_id']}" for skill_id, row in PUBLISHED_COMPONENTS],
)
def test_each_b1_published_component_runtime_contract(skill_id: str, component: dict) -> None:
    wrapper = importlib.import_module(f"skills.{skill_id}")
    component_id = str(component["component_id"])
    payload = wrapper.generate(
        level=1,
        seed=int(component["textbook_example_id"]),
        component_id=component_id,
    )

    assert payload["skill_id"] == skill_id
    assert payload["component_id"] == component_id
    assert payload.get("problem_type_id")
    assert payload.get("question_text")
    assert payload.get("answer_contract")
    assert payload.get("legacy_fallback_used") is not True
    assert (payload.get("metadata") or {}).get("fallback_used") is not True

    contract = payload["answer_contract"]
    answer_type = str(contract.get("answer_type") or payload.get("answer_type") or "")
    if answer_type == "drawing":
        assert contract.get("checker_key") == "free_response_drawing_checker"
        assert contract.get("expected_drawing_spec")
        assert payload.get("ui_contract") or contract.get("ui_contract")
        return

    correct_answer = payload.get("correct_answer", payload.get("answer"))
    assert _verdict(wrapper.check(correct_answer, correct_answer, payload)) is True
    assert _verdict(wrapper.check("__B1_PRODUCTION_WRONG__", correct_answer, payload)) is False


def test_b1_answer_type_and_required_form_coverage() -> None:
    observed: set[str] = set()
    for skill_id, component in PUBLISHED_COMPONENTS:
        wrapper = importlib.import_module(f"skills.{skill_id}")
        payload = wrapper.generate(
            seed=int(component["textbook_example_id"]),
            component_id=str(component["component_id"]),
        )
        contract = payload.get("answer_contract") or {}
        answer_type = str(contract.get("answer_type") or payload.get("answer_type") or "")
        presentation = str(payload.get("presentation_mode") or contract.get("presentation_mode") or "")
        if "choice" in answer_type or "choice" in presentation:
            observed.add("single_choice")
        elif answer_type == "multi_part" or contract.get("parts"):
            observed.add("multi_part")
        elif answer_type == "drawing":
            observed.add("drawing")
        elif answer_type == "table_fill":
            observed.add("table_fill")
        else:
            observed.add("short_answer")
    assert {"short_answer", "single_choice", "multi_part", "drawing"} <= observed
    assert "table_fill" not in observed

    factoring = importlib.import_module("skills.vh_數學B1_PolynomialFactoring")
    payload = factoring.generate(seed=4672, component_id="src_4672")
    assert payload["answer_contract"]["required_form"] == "factorized"
    expanded = {
        "part_1": "x^2-8*x+16",
        "part_2": "4*a^2+16*a*b+16*b^2",
        "part_3": "5*x^2-20",
    }
    assert _verdict(factoring.check(expanded, payload["correct_answer"], payload)) is False


def test_b1_question_required_physical_asset_integrity() -> None:
    required_assets: list[str] = []
    for skill_id, component in PUBLISHED_COMPONENTS:
        wrapper = importlib.import_module(f"skills.{skill_id}")
        payload = wrapper.generate(
            seed=int(component["textbook_example_id"]),
            component_id=str(component["component_id"]),
        )
        visual = payload.get("visual_spec") or {}
        if not isinstance(visual, dict) or visual.get("required") is not True:
            continue
        if visual.get("kind") != "image":
            continue
        asset_path = str(visual.get("asset_path") or "").lstrip("/")
        required_assets.append(asset_path)
        assert asset_path.startswith("static/question_assets/")
        assert (ROOT / asset_path).is_file()

    # Current B1 production uses runtime-rendered graph specifications; no
    # textbook physical image is classified QUESTION_REQUIRED.
    assert required_assets == []
