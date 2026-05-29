# -*- coding: utf-8 -*-
"""single_choice presentation for division_point_coordinates slot + Phase 2/3 parity."""

from __future__ import annotations

from pathlib import Path

from core.gencode.division_point_slot_engine import generate_division_point_payload
from core.gencode.generator_contract_schema import enrich_spec_generator_contract
from core.gencode.generator_diversity_sampling import run_diversity_sampling
from core.gencode.runtime_smoke import run_draft_runtime_smoke
from core.gencode.runtime_skill_wrapper import generate_for_skill
from core.gencode.slot_generators import generate_from_problem_type_spec
from core.gencode.validators import validate_generator_payload


def _short_answer_spec(target_task: str = "compute_internal_division_point_coordinates") -> dict:
    return enrich_spec_generator_contract(
        {
            "problem_type_id": f"ordered_pair_{target_task}_short_answer",
            "skill_id": "mock_skill",
            "target_task": target_task,
            "task_family": "division_point_coordinates_family",
            "answer_contract": {
                "answer_type": "ordered_pair",
                "answer_shape": "coordinate_pair",
                "answer_equivalence": "coordinate_pair_equivalence",
                "checker": "coordinate_pair_checker",
                "presentation_mode": "short_answer",
            },
            "generator_contract": {},
        }
    )


def _single_choice_spec(target_task: str = "compute_internal_division_point_coordinates") -> dict:
    return enrich_spec_generator_contract(
        {
            "problem_type_id": f"single_choice_{target_task}",
            "skill_id": "mock_skill",
            "target_task": target_task,
            "task_family": "division_point_coordinates_family",
            "answer_contract": {
                "answer_type": "single_choice",
                "answer_shape": "choice_label",
                "answer_equivalence": "choice_label",
                "checker": "choice_label_checker",
                "presentation_mode": "single_choice",
                "choice_count": 4,
                "correct_choice_count": 1,
                "choices_required": True,
            },
            "generator_contract": {},
        }
    )


def _choice_labels(payload: dict) -> list[str]:
    return [str(c.get("label", "")).strip() for c in (payload.get("choices") or []) if isinstance(c, dict)]


def _choice_texts(payload: dict) -> list[str]:
    return [str(c.get("text", c.get("value", ""))).strip() for c in (payload.get("choices") or []) if isinstance(c, dict)]


def test_division_point_single_choice_payload_complete():
    spec = _single_choice_spec()
    for i in range(30):
        payload = generate_from_problem_type_spec("mock_skill", spec, seed=100 + i * 13)
        choices = payload.get("choices") or []
        labels = _choice_labels(payload)
        texts = _choice_texts(payload)
        assert len(choices) == 4
        assert payload.get("answer") in {"A", "B", "C", "D"}
        assert payload.get("correct_answer") in labels
        assert payload.get("correct_value") in texts
        assert len(set(texts)) == 4
        assert validate_generator_payload(payload, problem_type_spec=spec) == []


def test_division_point_short_answer_not_polluted_by_single_choice():
    spec = _short_answer_spec()
    for i in range(10):
        payload = generate_from_problem_type_spec("mock_skill", spec, seed=200 + i * 11)
        assert payload.get("checker") == "coordinate_pair_checker"
        assert payload.get("choices") in (None, [])
        assert payload.get("answer") not in {"A", "B", "C", "D"}
        assert validate_generator_payload(payload, problem_type_spec=spec) == []


def test_validate_generator_payload_single_choice_missing_choices():
    spec = _single_choice_spec()
    bad = {
        "question_text": "test",
        "choices": [],
        "answer": None,
        "correct_answer": None,
        "problem_type_id": spec["problem_type_id"],
    }
    errors = validate_generator_payload(bad, problem_type_spec=spec)
    assert "choices_missing" in errors


def test_phase2_phase3_same_payload_schema_for_single_choice():
    spec = _single_choice_spec()
    phase2_payload = generate_from_problem_type_spec("mock_skill", spec, seed=777)
    phase3_payload = generate_division_point_payload("mock_skill", spec["problem_type_id"], spec, seed=777)
    for key in ("choices", "answer", "correct_answer", "checker", "answer_type"):
        assert phase2_payload.get(key) == phase3_payload.get(key)
    assert len(phase2_payload.get("choices") or []) == len(phase3_payload.get("choices") or []) == 4


def test_phase2_diversity_sampling_live_single_choice():
    spec = _single_choice_spec()
    out = run_diversity_sampling("mock_skill", spec, sample_count=12, base_seed=42)
    assert out.get("sampling_mode") == "live"
    assert not out.get("generation_errors")
    assert out.get("diversity_sampling_status") == "passed"


def test_phase3_draft_runtime_smoke_division_point_coordinates():
    draft = Path("reports/gencode_closed_loop/drafts/vh_數學B1_DivisionPointCoordinates.py")
    if not draft.is_file():
        return
    result = run_draft_runtime_smoke("vh_數學B1_DivisionPointCoordinates", str(draft), sample_count=30)
    assert result.get("status") == "passed", result
    assert result.get("interface_check", {}).get("generate_returns_dict") is True
    preview = result.get("payload_preview") or {}
    assert int(preview.get("choices_count") or 0) in {0, 4}
    assert int(preview.get("question_text_len") or 0) > 0


def test_runtime_skill_wrapper_generate_for_skill_single_choice():
    draft_specs = [
        {
            "problem_type_id": "single_choice_compute_internal_division_point_coordinates_two_coordinate_points_",
            "generator_readiness": "runtime_ready",
        }
    ]
    skill_id = "vh_數學B1_DivisionPointCoordinates"
    for seed in range(5):
        payload = generate_for_skill(skill_id, draft_specs, seed=seed)
        if payload.get("answer") in {"A", "B", "C", "D"}:
            assert len(payload.get("choices") or []) == 4
            return
    raise AssertionError("expected at least one single_choice payload from generate_for_skill")
