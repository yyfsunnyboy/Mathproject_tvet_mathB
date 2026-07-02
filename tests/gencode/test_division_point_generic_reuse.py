from __future__ import annotations

import math
from pathlib import Path

from core.checkers.coordinate_pair_checker import parse_coordinate_pair_answer
from core.gencode.classifiers import get_classifier_for_skill
from core.gencode.classifiers.coordinate_geometry_division_point import (
    CoordinateGeometryDivisionPointClassifier,
)
from core.gencode.classifiers.base import ClassifierContext
from core.gencode.generator_contract_schema import enrich_generator_contract
from core.gencode.slot_generators import TARGET_TASK_GENERATOR_REGISTRY
from core.gencode.template_slot_resolver import resolve_template_slot


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_SKILL_ID = "vh_測試_DivisionPointCoordinates"


def _contract(operation: str, *, choice: bool = False) -> dict:
    answer_contract = {
        "answer_type": "single_choice" if choice else "coordinate_pair",
        "answer_shape": "choice_label" if choice else "coordinate_pair",
        "answer_equivalence": "choice_label" if choice else "coordinate_pair_equivalence",
        "equivalence_type": "choice_label" if choice else "coordinate_pair_equivalence",
        "checker": "choice_label_checker" if choice else "coordinate_pair_checker",
        "checker_key": "choice_label_checker" if choice else "coordinate_pair_checker",
        "presentation_mode": "single_choice" if choice else "short_answer",
        "choices_required": choice,
    }
    return {
        "skill_id": SYNTHETIC_SKILL_ID,
        "problem_type_id": operation,
        "target_task": operation,
        "task_family": "division_point_coordinates_family",
        "answer_contract": answer_contract,
        "generator_contract": enrich_generator_contract(
            operation,
            answer_contract=answer_contract,
            problem_type_id=operation,
        ),
    }


def _generate(spec: dict, seed: int) -> dict:
    operation = spec["target_task"]
    assert operation in TARGET_TASK_GENERATOR_REGISTRY
    assert resolve_template_slot(spec, seed) == "division_point_coordinates"
    return TARGET_TASK_GENERATOR_REGISTRY[operation](
        SYNTHETIC_SKILL_ID,
        spec["problem_type_id"],
        spec,
        seed,
    )


def _validate_choice(payload: dict) -> None:
    choices = payload["choices"]
    assert len(choices) == 4
    assert len({choice["text"] for choice in choices}) == 4
    assert sum(choice["label"] == payload["correct_answer"] for choice in choices) == 1
    assert payload["checker"] == "choice_label_checker"
    assert payload["equivalence"] == "choice_label"


def test_generic_classifier_registry_accepts_another_skill() -> None:
    classifier = get_classifier_for_skill(SYNTHETIC_SKILL_ID)
    assert isinstance(classifier, CoordinateGeometryDivisionPointClassifier)
    examples = [
        {
            "id": 90001,
            "problem_text": "A(0,0)、B(6,3)，P 在線段 AB 上，AP:PB=1:2，求 P 坐標。",
        },
        {
            "id": 90002,
            "problem_text": "已知 A(0,0)、B(3,0)、C(0,3)，求三角形 ABC 的重心坐標。",
        },
        {
            "id": 90003,
            "problem_text": "A(1,1)、B(7,7)，P 在線段 AB 上且 AP:PB=1:2，求 OP。(A)1 (B)2 (C)3 (D)4",
        },
    ]
    result = classifier.classify_examples(
        examples,
        ClassifierContext(project_root=PROJECT_ROOT, skill_id=SYNTHETIC_SKILL_ID),
    )
    assert [row["problem_type_id"] for row in result.examples_map_entries] == [
        "compute_internal_division_point_coordinates",
        "compute_centroid_coordinates",
        "compute_section_point_distance_from_origin",
    ]


def test_synthetic_internal_division_ten_seeds() -> None:
    spec = _contract("compute_internal_division_point_coordinates")
    for seed in range(10):
        payload = _generate(spec, seed)
        assert payload["skill_id"] == SYNTHETIC_SKILL_ID
        assert payload["question_text"].strip()
        answer = parse_coordinate_pair_answer(payload["correct_answer"])
        assert answer is not None
        coords = payload["metadata"]["generation_coords"]
        m, n = [int(value) for value in payload["metadata"]["ratio_values"].split(":")]
        expected = (
            (n * coords["A"][0] + m * coords["B"][0]) / (m + n),
            (n * coords["A"][1] + m * coords["B"][1]) / (m + n),
        )
        assert math.isclose(float(answer[0]), expected[0])
        assert math.isclose(float(answer[1]), expected[1])


def test_synthetic_centroid_ten_seeds() -> None:
    spec = _contract("compute_centroid_coordinates")
    for seed in range(10):
        payload = _generate(spec, seed)
        answer = parse_coordinate_pair_answer(payload["correct_answer"])
        assert answer is not None
        coords = payload["metadata"]["generation_coords"]
        expected = (
            sum(coords[key][0] for key in ("A", "B", "C")) / 3,
            sum(coords[key][1] for key in ("A", "B", "C")) / 3,
        )
        assert math.isclose(float(answer[0]), expected[0])
        assert math.isclose(float(answer[1]), expected[1])
        assert payload["checker"] == "coordinate_pair_checker"


def test_synthetic_section_point_origin_distance_ten_seeds() -> None:
    spec = _contract("compute_section_point_distance_from_origin", choice=True)
    for seed in range(10):
        payload = _generate(spec, seed)
        _validate_choice(payload)
        px, py = payload["metadata"]["generation_coords"]["P"]
        distance = math.isqrt(int(px * px + py * py))
        assert distance > 0
        assert str(distance) == payload["correct_value"]
