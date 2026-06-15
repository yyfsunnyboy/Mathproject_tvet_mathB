# -*- coding: utf-8 -*-
"""Minimal tests for generic line equation gencode support."""

from __future__ import annotations

from core.checkers.linear_equation_equivalent_checker import check_linear_equation_equivalent_answer
from core.gencode.answer_contract_gate import EQUIVALENCE_TYPE_WHITELIST, apply_runtime_gate_to_candidate
from core.gencode.answer_contract_policy import (
    build_line_equation_answer_contract,
    infer_answer_contract_from_problem_context,
)
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.generator_contract_schema import TASK_CONTRACT_BLUEPRINTS
from core.gencode.answer_format_hint import build_answer_format_suffix
from core.gencode.example_feature_extractor import detect_line_equation_routing
from core.gencode.problem_type_canonicalizer import typed_line_equation_problem_type_id
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.scenario_pool_manager import append_answer_format_suffix
from core.gencode.slot_generators import (
    SLOT_REGISTRY,
    _slot_line_equation_from_point_slope,
    _slot_line_equation_from_slope_and_intercept,
    _slot_line_equation_from_two_points,
    _slot_perpendicular_bisector_from_two_points,
    _slot_triangle_median_line_from_vertices,
)
from core.gencode.task_families import (
    LINE_EQUATION_FAMILY,
    LINE_EQUATION_TASKS,
    LINE_EQUATION_TASK_TO_SLOT,
    task_family_for_task,
)
from core.gencode.validators import validate_generator_payload
from validators.semantic_checker import SemanticChecker


def _line_equation_spec(target_task: str, problem_type_id: str | None = None) -> dict:
    pt = problem_type_id or typed_line_equation_problem_type_id(target_task, presentation_mode="short_answer")
    return {
        "problem_type_id": pt,
        "target_task": target_task,
        "task_family": LINE_EQUATION_FAMILY,
        "answer_contract": build_line_equation_answer_contract(),
    }


def _assert_line_equation_payload(payload: dict, *, target_task: str) -> None:
    question_text = str(payload.get("question_text") or "")
    answer = str(payload.get("answer") or "")
    ac = payload.get("answer_contract") or {}
    assert "答案範例：5" not in question_text
    assert "$" in question_text
    assert "$" not in answer
    assert payload.get("target_task") == target_task
    assert payload.get("task_family") == LINE_EQUATION_FAMILY
    assert ac.get("checker_key") == "linear_equation_equivalent_checker"
    assert ac.get("equivalence_type") == "linear_equation_equivalent"
    assert ac.get("answer_type") == "equation"
    assert ac.get("answer_shape") == "linear_equation"
    assert check_answer(answer, answer, answer_contract=ac)
    assert not check_answer("__WRONG__", answer, answer_contract=ac)
    finalized = append_answer_format_suffix(dict(payload), _line_equation_spec(target_task))
    assert "答案範例：5" not in str(finalized.get("question_text") or "")


def test_linear_equation_checker_equivalence_cases():
    canonical = "3x - y - 1 = 0"
    assert check_linear_equation_equivalent_answer("y - 2 = 3(x - 1)", canonical)
    assert check_linear_equation_equivalent_answer("y=3x-1", canonical)
    assert check_linear_equation_equivalent_answer("3x-y-1=0", canonical)
    assert check_linear_equation_equivalent_answer("6x-2y-2=0", canonical)
    assert not check_linear_equation_equivalent_answer("y = 3x + 2", canonical)
    assert not check_linear_equation_equivalent_answer("x^2+y=1", canonical)
    assert not check_linear_equation_equivalent_answer("5", canonical)
    assert not check_linear_equation_equivalent_answer("", canonical)


def test_runtime_wrapper_uses_linear_equation_checker():
    ac = build_line_equation_answer_contract()
    assert check_answer("y=3x-1", "3x - y - 1 = 0", answer_contract=ac)
    assert not check_answer("y=3x+2", "3x - y - 1 = 0", answer_contract=ac)


def test_slot_generator_template_diversity_and_contract():
    spec = {
        "target_task": "write_line_equation_from_point_slope",
        "task_family": LINE_EQUATION_FAMILY,
        "answer_contract": build_line_equation_answer_contract(),
    }
    variants: set[str] = set()
    for seed in range(10):
        payload = _slot_line_equation_from_point_slope(
            "mock_line_equation_skill",
            "write_line_equation_from_point_slope_v1",
            spec,
            seed,
        )
        variants.add(str(payload.get("template_variant", "")))
        ac = payload.get("answer_contract") or {}
        assert ac.get("checker") == "linear_equation_equivalent_checker"
        assert ac.get("checker_key") == "linear_equation_equivalent_checker"
        assert payload.get("checker") == "linear_equation_equivalent_checker"
        assert payload.get("target_task") == "write_line_equation_from_point_slope"
        assert payload.get("task_family") == LINE_EQUATION_FAMILY
        assert payload.get("question_text")
        assert payload.get("answer")
    assert len(variants) >= 2


def test_task_family_and_blueprint_registered():
    expected_tasks = {
        "write_line_equation_from_point_slope",
        "write_line_equation_from_two_points",
        "write_perpendicular_bisector_from_two_points",
        "write_line_equation_from_slope_and_intercept",
        "write_triangle_median_line_from_vertices",
    }
    assert expected_tasks <= set(LINE_EQUATION_TASKS)
    for task in expected_tasks:
        assert task_family_for_task(task) == LINE_EQUATION_FAMILY
        assert task in TASK_CONTRACT_BLUEPRINTS
        assert TASK_CONTRACT_BLUEPRINTS[task]["answer_shape"] == "linear_equation"
    blueprint = TASK_CONTRACT_BLUEPRINTS["write_line_equation_from_point_slope"]
    variant_ids = {v["id"] for v in blueprint["template_variants"]}
    assert variant_ids == {
        "given_point_and_slope_find_point_slope_form",
        "given_point_and_slope_find_slope_intercept_form",
        "given_point_and_slope_find_general_form",
    }
    assert "point_coordinates" in blueprint["variation_dimensions"]


def test_answer_contract_policy_and_gate_whitelist():
    ac = infer_answer_contract_from_problem_context(
        answer_type="equation",
        target_task="write_line_equation_from_point_slope",
        task_family=LINE_EQUATION_FAMILY,
    )
    assert ac["answer_type"] == "equation"
    assert ac["answer_shape"] == "linear_equation"
    assert ac["checker"] == "linear_equation_equivalent_checker"
    assert ac["equivalence_type"] == "linear_equation_equivalent"
    cap = validate_answer_contract_capability(ac)
    assert cap["checker_capability_status"] == "ok"
    assert "linear_equation_equivalent" in EQUIVALENCE_TYPE_WHITELIST

    candidate = {
        "problem_type_id": "write_line_equation_from_point_slope_v1",
        "answer_contract_proposal": ac,
    }
    gated = apply_runtime_gate_to_candidate(candidate)
    assert gated["runtime_status"] == "runtime_ready_candidate"
    assert "invalid_equivalence_type_problem_type" not in gated.get("promote_blockers", [])


def test_linear_equation_answer_format_suffix_uses_equation_hint_not_numeric_five():
    ac = build_line_equation_answer_contract()
    suffix = build_answer_format_suffix(ac)
    assert "答案範例：5" not in suffix
    assert "可輸入等價方程式" in suffix
    assert "$y - 2 = 3(x - 1)$" in suffix
    assert "$y = 3x - 1$" in suffix
    assert "$3x - y - 1 = 0$" in suffix


def test_linear_equation_runtime_generate_question_text_suffix():
    from skills.vh_數學B1_PointSlopeForm import generate

    payload = generate(level=1, seed=3)
    target_task = str(payload.get("target_task") or "")
    assert target_task in {
        "write_line_equation_from_point_slope",
        "write_line_equation_from_two_points",
        "write_perpendicular_bisector_from_two_points",
        "write_line_equation_from_slope_and_intercept",
        "write_triangle_median_line_from_vertices",
    }
    _assert_line_equation_payload(payload, target_task=target_task)


def test_line_equation_source_routing_classification():
    cases = {
        "試求過點 (2,-1) 且斜率為 1/2 的直線方程式。": "write_line_equation_from_point_slope",
        "試求通過 A(-3,1)、B(2,4) 兩點的直線方程式。": "write_line_equation_from_two_points",
        "設 A(-1,1)、B(3,-1)，求 AB 之垂直平分線方程式。": "write_perpendicular_bisector_from_two_points",
        "試求斜率為 3 且 x 截距為 5 的直線方程式。": "write_line_equation_from_slope_and_intercept",
        "三角形 ABC 頂點給定，求過 B 點並將三角形面積平分的直線方程式。": "write_triangle_median_line_from_vertices",
        "兩鄉鎮距離相同，求車站所在直線道路方程式。": "write_perpendicular_bisector_from_two_points",
    }
    for stem, expected in cases.items():
        route = detect_line_equation_routing(stem)
        assert route is not None
        assert route["target_task"] == expected


def test_line_equation_task_slot_registry_complete():
    for task, slot in LINE_EQUATION_TASK_TO_SLOT.items():
        assert task in LINE_EQUATION_TASKS
        assert SLOT_REGISTRY[slot] is not None


def test_line_equation_slot_generators_30_seed_smoke():
    slot_cases = [
        ("write_line_equation_from_point_slope", _slot_line_equation_from_point_slope),
        ("write_line_equation_from_two_points", _slot_line_equation_from_two_points),
        ("write_perpendicular_bisector_from_two_points", _slot_perpendicular_bisector_from_two_points),
        ("write_line_equation_from_slope_and_intercept", _slot_line_equation_from_slope_and_intercept),
        ("write_triangle_median_line_from_vertices", _slot_triangle_median_line_from_vertices),
    ]
    checker = SemanticChecker()
    for target_task, fn in slot_cases:
        spec = _line_equation_spec(target_task)
        for seed in range(30):
            payload = fn("mock_line_equation_skill", spec["problem_type_id"], spec, seed)
            _assert_line_equation_payload(payload, target_task=target_task)
            ok, err = checker.check_semantic(payload, spec)
            assert ok, f"{target_task} seed={seed}: {err}"
            assert validate_generator_payload(payload, problem_type_spec=spec) == []


def test_linear_equation_checker_vertical_and_horizontal_lines():
    assert check_linear_equation_equivalent_answer("x - 5 = 0", "x - 5 = 0")
    assert check_linear_equation_equivalent_answer("y + 2 = 0", "y + 2 = 0")


def test_semantic_checker_accepts_linear_equation_payload():
    spec = _line_equation_spec("write_line_equation_from_point_slope")
    payload = _slot_line_equation_from_point_slope(
        "mock_line_equation_skill",
        spec["problem_type_id"],
        spec,
        7,
    )
    checker = SemanticChecker()
    ok, err = checker.check_semantic(payload, spec)
    assert ok, err
    assert validate_generator_payload(payload, problem_type_spec=spec) == []


def test_line_equation_mcq_hold_demotes_single_choice():
    from core.gencode.problem_type_canonicalizer import (
        LINE_EQUATION_MCQ_HOLD_BLOCKER,
        apply_line_equation_mcq_hold_policy,
        line_equation_mcq_hold_applies,
    )

    row = {
        "problem_type_id": "equation_write_line_equation_from_point_slope_single_choice",
        "target_task": "write_line_equation_from_point_slope",
        "task_family": LINE_EQUATION_FAMILY,
        "answer_contract": {
            "answer_type": "single_choice",
            "answer_shape": "single_choice",
            "presentation_mode": "single_choice",
            "checker": "choice_label_checker",
        },
        "usable_for_phase3": True,
        "generator_readiness": "runtime_ready",
    }
    assert line_equation_mcq_hold_applies(row)
    demoted = apply_line_equation_mcq_hold_policy(row)
    assert demoted["usable_for_phase3"] is False
    assert demoted["generator_readiness"] == "pending_line_equation_mcq_slot"
    assert LINE_EQUATION_MCQ_HOLD_BLOCKER in demoted["promote_blockers"]


def test_point_slope_form_skill_pack_has_five_runtime_generators():
    import importlib

    from core.gencode.runtime_skill_wrapper import collect_available_runtime_problem_types, generate_for_skill

    mod = importlib.import_module("skills.vh_數學B1_PointSlopeForm")
    specs = getattr(mod, "GENERATOR_SPECS", [])
    available = collect_available_runtime_problem_types(mod.SKILL_ID, specs)
    available_ids = {row["problem_type_id"] for row in available}
    expected = {
        "equation_write_line_equation_from_point_slope_short_answer",
        "equation_write_line_equation_from_two_points_short_answer",
        "equation_write_perpendicular_bisector_from_two_points_short_answer",
        "equation_write_line_equation_from_slope_and_intercept_short_answer",
        "equation_write_triangle_median_line_from_vertices_short_answer",
    }
    assert expected <= available_ids
    seen: set[str] = set()
    for seed in range(50):
        payload = generate_for_skill(mod.SKILL_ID, specs, seed=seed)
        pt = str(payload.get("problem_type_id") or "")
        assert pt in expected
        _assert_line_equation_payload(payload, target_task=str(payload.get("target_task") or ""))
        seen.add(pt)
    assert len(seen) >= 3
