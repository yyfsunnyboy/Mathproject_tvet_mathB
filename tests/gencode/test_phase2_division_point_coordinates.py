from __future__ import annotations

import json
import math
from pathlib import Path

from core.checkers.coordinate_pair_checker import parse_coordinate_pair_answer
from core.gencode.division_point_slot_engine import generate_division_point_payload
from core.gencode.generator_contract_schema import enrich_generator_contract


SKILL_ID = "vh_數學B1_DivisionPointCoordinates"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = (
    PROJECT_ROOT
    / "reports"
    / "gencode_closed_loop"
    / "drafts"
    / f"{SKILL_ID}_phase2_generator_specs.json"
)


def _load_specs() -> list[dict]:
    payload = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    assert payload["generator_specs_count"] == 7
    assert payload["build_candidate_count"] == 6
    return payload["generator_specs"]


def _runtime_spec(row: dict) -> dict:
    is_choice = row["presentation_mode"] == "single_choice"
    answer_contract = {
        "answer_type": "single_choice" if is_choice else row["answer_type"],
        "answer_shape": "choice_label" if is_choice else "coordinate_pair",
        "answer_equivalence": row["equivalence_type"],
        "equivalence_type": row["equivalence_type"],
        "checker": row["checker_key"],
        "checker_key": row["checker_key"],
        "presentation_mode": row["presentation_mode"],
        "choices_required": is_choice,
    }
    return {
        "skill_id": SKILL_ID,
        "problem_type_id": row["problem_type_id"],
        "target_task": row["target_task"],
        "task_family": "division_point_coordinates_family",
        "answer_contract": answer_contract,
        "generator_contract": enrich_generator_contract(
            row["target_task"],
            answer_contract=answer_contract,
            problem_type_id=row["problem_type_id"],
        ),
    }


def _generate(row: dict, seed: int) -> dict:
    return generate_division_point_payload(
        SKILL_ID,
        row["problem_type_id"],
        _runtime_spec(row),
        seed,
    )


def _assert_choice(payload: dict) -> None:
    choices = payload["choices"]
    assert len(choices) == 4
    values = [str(choice["text"]) for choice in choices]
    assert len(set(values)) == 4
    labels = [choice["label"] for choice in choices]
    assert payload["correct_answer"] in labels
    assert labels.count(payload["correct_answer"]) == 1
    assert payload["checker"] == "choice_label_checker"
    assert payload["equivalence"] == "choice_label"


def _assert_coordinate_math(payload: dict, operation: str) -> None:
    answer = payload.get("correct_value") or payload["correct_answer"]
    if payload.get("choices"):
        answer = payload["metadata"]["semantic_answer"]
    parsed = parse_coordinate_pair_answer(answer)
    assert parsed is not None
    coords = payload["metadata"]["generation_coords"]
    if operation == "compute_centroid_coordinates":
        points = [coords["A"], coords["B"], coords["C"]]
        expected = (
            sum(point[0] for point in points) / 3,
            sum(point[1] for point in points) / 3,
        )
    else:
        m, n = [int(value) for value in payload["metadata"]["ratio_values"].split(":")]
        point_a, point_b = coords["A"], coords["B"]
        expected = (
            (n * point_a[0] + m * point_b[0]) / (m + n),
            (n * point_a[1] + m * point_b[1]) / (m + n),
        )
    assert math.isclose(float(parsed[0]), float(expected[0]), abs_tol=1e-9)
    assert math.isclose(float(parsed[1]), float(expected[1]), abs_tol=1e-9)


def test_phase2_specs_cover_seven_sources_but_build_only_six() -> None:
    specs = _load_specs()
    assert len(specs) == 7
    assert len([row for row in specs if row["status"] == "draft"]) == 6
    verified = [row for row in specs if row["status"] != "draft"]
    assert [row["source_id"] for row in verified] == [4421]
    assert len({row["operation"] for row in specs}) == 3


def test_each_operation_passes_ten_seed_draft_smoke() -> None:
    rows = _load_specs()
    representative = {
        operation: next(row for row in rows if row["operation"] == operation)
        for operation in {
            "compute_internal_division_point_coordinates",
            "compute_centroid_coordinates",
            "compute_section_point_distance_from_origin",
        }
    }
    for operation, row in representative.items():
        for seed in range(10):
            payload = _generate(row, seed)
            question = str(payload.get("question_text") or "")
            assert question.strip()
            assert "placeholder" not in question.lower()
            assert payload["answer_contract"]["checker"] == row["checker_key"]
            if operation == "compute_section_point_distance_from_origin":
                _assert_choice(payload)
                point = payload["metadata"]["generation_coords"]["P"]
                expected = math.isqrt(int(point[0] ** 2 + point[1] ** 2))
                assert str(expected) == payload["correct_value"]
                assert expected > 0
            else:
                _assert_coordinate_math(payload, operation)


def test_internal_choice_spec_has_unique_correct_option_for_ten_seeds() -> None:
    row = next(
        row for row in _load_specs()
        if row["source_id"] == 4512
    )
    for seed in range(10):
        payload = _generate(row, seed)
        _assert_choice(payload)
        _assert_coordinate_math(payload, row["operation"])
