# -*- coding: utf-8 -*-
"""Live division_point_coordinates slot generators and diversity sampling."""

from __future__ import annotations

import re

from core.checkers.coordinate_pair_checker import check_coordinate_pair_answer
from core.gencode.division_point_slot_engine import generate_division_point_payload
from core.gencode.generator_contract_schema import enrich_spec_generator_contract
from core.gencode.generator_diversity_sampling import (
    evaluate_diversity_metrics,
    plan_to_signature,
    run_diversity_sampling,
)
from core.gencode.slot_generators import generate_from_problem_type_spec


def _spec(target_task: str) -> dict:
    return enrich_spec_generator_contract(
        {
            "problem_type_id": f"pt_{target_task}",
            "skill_id": "mock_skill",
            "target_task": target_task,
            "task_family": "division_point_coordinates_family",
            "answer_contract": {
                "answer_type": "ordered_pair",
                "answer_shape": "coordinate_pair",
                "answer_equivalence": "coordinate_pair_equivalence",
                "checker": "coordinate_pair_checker",
            },
            "generator_contract": {},
        }
    )


def _sample_30(target_task: str, *, base_seed: int = 42) -> list[dict]:
    spec = _spec(target_task)
    out: list[dict] = []
    for i in range(30):
        payload = generate_from_problem_type_spec("mock_skill", spec, seed=base_seed + i * 17)
        out.append(payload)
    return out


def _diversity_metrics(payloads: list[dict], spec: dict) -> dict:
    gc = spec.get("generator_contract") or {}
    variant_ids = [
        str(v.get("id", ""))
        for v in (gc.get("template_variants") or [])
        if isinstance(v, dict) and v.get("enabled", True)
    ]
    signatures = []
    for p in payloads:
        meta = p.get("metadata") if isinstance(p.get("metadata"), dict) else {}
        plan = {
            "problem_type_id": str(spec.get("problem_type_id", "")),
            "template_variant": str(meta.get("template_variant", "")),
            "ratio_form": str(meta.get("ratio_form", "")),
            "ratio_values": str(meta.get("ratio_values", "")),
            "coordinate_pattern": str(meta.get("coordinate_pattern", "")),
            "answer": str(p.get("answer", "")),
        }
        signatures.append(plan_to_signature(plan))
    return evaluate_diversity_metrics(
        signatures,
        template_variant_ids=variant_ids,
        question_texts=[str(p.get("question_text", "")) for p in payloads],
        answers=[str(p.get("answer", "")) for p in payloads],
        sample_count=30,
    )


def _assert_payload_shape(payload: dict) -> None:
    for key in (
        "question_text",
        "answer",
        "correct_answer",
        "explanation",
        "problem_type_id",
        "answer_contract",
        "checker",
        "equivalence",
    ):
        assert key in payload, f"missing {key}"
    assert payload["checker"] == "coordinate_pair_checker"
    ac = payload["answer_contract"]
    assert ac.get("answer_type") in {"ordered_pair", "coordinate_pair"}
    assert ac.get("answer_shape") == "coordinate_pair"
    assert payload["equivalence"] == "coordinate_pair_equivalence"
    meta = payload.get("metadata") or {}
    assert isinstance(meta.get("generator_contract"), dict)
    assert meta.get("template_variant")


def _assert_coordinate_answer(answer: str) -> None:
    assert re.match(r"^\([^)]+\)$", answer.strip()), f"not coordinate pair: {answer}"


def test_internal_division_30_sample_diversity():
    spec = _spec("compute_internal_division_point_coordinates")
    payloads = _sample_30("compute_internal_division_point_coordinates")
    for p in payloads:
        _assert_payload_shape(p)
        _assert_coordinate_answer(str(p["answer"]))
        assert check_coordinate_pair_answer(str(p["answer"]), str(p["correct_answer"]))
    metrics = _diversity_metrics(payloads, spec)
    assert metrics["unique_signature_count"] >= 15
    assert len(metrics.get("template_variant_distribution") or {}) >= 2
    ratio_forms = {str((p.get("metadata") or {}).get("ratio_form", "")) for p in payloads}
    assert len(ratio_forms) >= 2
    point_sets = {tuple((p.get("metadata") or {}).get("point_names") or []) for p in payloads}
    assert len(point_sets) >= 2


def test_centroid_30_sample_diversity():
    spec = _spec("compute_centroid_coordinates")
    payloads = _sample_30("compute_centroid_coordinates", base_seed=99)
    for p in payloads:
        _assert_payload_shape(p)
        _assert_coordinate_answer(str(p["answer"]))
    metrics = _diversity_metrics(payloads, spec)
    assert metrics["unique_signature_count"] >= 15


def test_midpoint_30_sample_diversity():
    spec = _spec("compute_midpoint_coordinates")
    payloads = _sample_30("compute_midpoint_coordinates", base_seed=7)
    for p in payloads:
        _assert_payload_shape(p)
        _assert_coordinate_answer(str(p["answer"]))
    metrics = _diversity_metrics(payloads, spec)
    assert metrics["unique_signature_count"] >= 15


def test_section_ratio_live_generation():
    spec = _spec("solve_point_from_section_ratio")
    p = generate_from_problem_type_spec("mock_skill", spec, seed=123)
    _assert_payload_shape(p)
    assert "坐標" in p["question_text"]


def test_phase2_diversity_uses_live_slot_not_contract_fallback():
    spec = _spec("compute_internal_division_point_coordinates")
    metrics = run_diversity_sampling("mock_skill", spec, sample_count=30, base_seed=200)
    assert metrics.get("sampling_mode") == "live"
    assert metrics["unique_signature_count"] >= 15
    assert not metrics.get("generation_errors")


def test_coordinate_pair_checker_regression_formats():
    correct = "(0,-2)"
    for ua in ("(0,-2)", "0,-2", "（0，-2）", "x=0,y=-2", "(0, -2)"):
        assert check_coordinate_pair_answer(ua, correct)
    assert not check_coordinate_pair_answer("(1,-2)", correct)


def test_coordinate_pair_checker_fraction_coordinates():
    correct = "(3/2,-1)"
    for ua in ("(3/2,-1)", "3/2,-1", "x=3/2,y=-1"):
        assert check_coordinate_pair_answer(ua, correct)
    assert not check_coordinate_pair_answer("(1,-1)", correct)


def test_direct_engine_metadata():
    spec = _spec("compute_internal_division_point_coordinates")
    payload = generate_division_point_payload("mock_skill", "pt_test", spec, seed=1)
    assert payload["source"] == "gencode_slot_generator"
    meta = payload["metadata"]
    assert meta["template_variant"] in {
        "ratio_colon_form",
        "multiple_form",
        "linear_relation_form",
        "word_context_form",
    }
