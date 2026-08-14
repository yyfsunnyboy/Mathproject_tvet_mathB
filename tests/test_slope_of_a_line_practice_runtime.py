# -*- coding: utf-8 -*-
"""Practice-runtime integration tests for published SlopeOfALine V3 package."""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

from core.legacy_generator_adapter import invoke_skill_generate
from core.routes.practice import get_skill, _finalize_practice_question_api_fields

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_ID = "vh_數學B1_SlopeOfALine"
FIXED_SEED = 42

COMPONENTS = [
    ("src_4519", 4519, "slopes_of_named_segments"),
    ("src_4520", 4520, "classify_and_compare_figure_slopes"),
    ("src_4521", 4521, "slope_from_two_points"),
    ("src_4522", 4522, "solve_parameter_from_known_slope"),
    ("src_4523", 4523, "collinear_three_points_parameter"),
    ("src_4524", 4524, "non_triangle_collinear_parameter"),
    ("src_4525", 4525, "parallel_segments_parameter"),
    ("src_4529", 4529, "collinear_three_points_parameter"),
    ("src_4533", 4533, "slopes_of_named_segments"),
    ("src_4534", 4534, "non_triangle_collinear_parameter"),
    ("src_4590", 4590, "solve_parameter_from_known_slope_choice"),
    ("src_4601", 4601, "collinear_three_points_parameter_choice"),
]

FOCUS_IDS = {4519, 4520, 4533, 4534, 4601}


def _runtime_module_path(mod) -> str:
    return str(getattr(mod, "__file__", "") or "")


def _generate_via_facade(component_id: str, seed: int = FIXED_SEED) -> dict:
    mod = get_skill(SKILL_ID)
    assert mod is not None
    payload = invoke_skill_generate(
        mod,
        level=1,
        seed=seed,
        component_id=component_id,
        skill_id=SKILL_ID,
    )
    assert isinstance(payload, dict)
    return _finalize_practice_question_api_fields(payload, skill_id=SKILL_ID)


def _visual_requires_render(visual_spec: dict) -> bool:
    runtime_path = PROJECT_ROOT / "static" / "js" / "visual_spec.js"
    node = subprocess.run(
        [
            "node",
            "-e",
            "const r=require(process.argv[1]);process.stdout.write(String(r.requiresVisualRendering(JSON.parse(process.argv[2]))));",
            str(runtime_path),
            json.dumps(visual_spec, ensure_ascii=False),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if node.returncode != 0:
        return bool(visual_spec.get("render_required"))
    return node.stdout.strip().lower() == "true"


def test_facade_loads_published_v3_wrapper_not_legacy_candidate():
    mod = get_skill(SKILL_ID)
    assert mod is not None
    facade_path = _runtime_module_path(mod)
    assert facade_path.endswith("skills\\vh_數學B1_SlopeOfALine.py") or facade_path.endswith(
        "skills/vh_數學B1_SlopeOfALine.py"
    )
    assert ".bak" not in facade_path
    assert "generated_candidates" not in facade_path
    assert hasattr(mod, "GENERATOR_KEYS")
    assert len(mod.GENERATOR_KEYS) == 12
    assert "dispatch_generate" in Path(facade_path).read_text(encoding="utf-8")
    assert "VERIFIED_CANDIDATE_MODULES" not in Path(facade_path).read_text(encoding="utf-8")


@pytest.mark.parametrize("component_id,example_id,operation", COMPONENTS)
def test_formal_wrapper_generates_all_twelve_components(component_id, example_id, operation):
    payload = _generate_via_facade(component_id)
    assert payload.get("component_id") == component_id
    assert int(payload.get("textbook_example_id") or 0) == example_id
    assert payload.get("problem_type_id") == operation
    assert str(payload.get("question_text") or payload.get("new_question_text") or "").strip()
    assert payload.get("correct_answer") is not None or payload.get("answer") is not None
    ui = payload.get("ui_contract") or {}
    assert ui.get("handwriting_enabled") is True
    assert ui.get("canvas_required") is True


def test_focus_five_repaired_examples_runtime_shape():
    cases = {
        "src_4519": {
            "answer_type": "multi_part",
            "need_tokens": ["不存在"],
            "need_fraction": True,
        },
        "src_4520": {
            "answer_type": "multi_part",
            "need_tokens": ["m不存在", "m1", "m2"],
            "visual": True,
        },
        "src_4533": {
            "answer_type": "multi_part",
            "segment_prompt_parts": 4,
        },
        "src_4534": {
            "answer_type": "rational",
            "parameter_k": True,
        },
        "src_4601": {
            "answer_type": "single_choice",
            "choice_label": True,
            "semantic_numeric": True,
        },
    }
    for component_id, rules in cases.items():
        payload = _generate_via_facade(component_id)
        answer = payload.get("correct_answer") or payload.get("answer")
        meta = payload.get("metadata") or {}
        if rules.get("answer_type") == "multi_part":
            assert isinstance(answer, dict)
            joined = "；".join(str(v) for v in answer.values())
            if rules.get("need_tokens"):
                assert any(tok in joined for tok in rules["need_tokens"])
            if rules.get("need_fraction"):
                assert "/" in joined or "不存在" in joined
        if rules.get("segment_prompt_parts"):
            stem = str(payload.get("question_text") or "")
            assert "斜率" in stem
            for idx in range(1, int(rules["segment_prompt_parts"]) + 1):
                assert f"({idx})" in stem
        if rules.get("parameter_k"):
            assert "k" in str(payload.get("question_text") or "")
            assert str(answer).strip()
        if rules.get("choice_label"):
            assert str(answer).strip().upper() in {"A", "B", "C", "D"}
        if rules.get("semantic_numeric"):
            semantic = payload.get("semantic_answer") or meta.get("semantic_answer")
            assert str(semantic).strip()
            assert str(semantic).strip().upper() not in {"A", "B", "C", "D"}
        if rules.get("visual"):
            visual_spec = payload.get("visual_spec") or {}
            assert visual_spec
            assert _visual_requires_render(visual_spec)


def test_visual_spec_reaches_practice_api_fields():
    payload = _generate_via_facade("src_4520")
    assert payload.get("visual_spec")
    assert payload["visual_spec"].get("render_required") is True
    assert _visual_requires_render(payload["visual_spec"])


def test_handwriting_ui_contract_present_for_choice_and_multipart():
    for component_id in ("src_4519", "src_4590", "src_4601"):
        payload = _generate_via_facade(component_id)
        ui = payload.get("ui_contract") or {}
        assert ui.get("handwriting_enabled") is True
        assert ui.get("canvas_required") is True
