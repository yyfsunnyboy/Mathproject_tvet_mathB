from __future__ import annotations

import json
import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.checkers.coordinate_pair_checker import parse_coordinate_pair_answer
from core.gencode.division_point_slot_engine import generate_division_point_payload
from core.gencode.generator_contract_schema import enrich_generator_contract


SKILL_ID = "vh_數學B1_DivisionPointCoordinates"
SPEC_PATH = (
    PROJECT_ROOT
    / "reports"
    / "gencode_closed_loop"
    / "drafts"
    / f"{SKILL_ID}_phase2_generator_specs.json"
)


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


def _validate_choices(payload: dict) -> None:
    choices = payload.get("choices") or []
    values = [str(choice["text"]) for choice in choices]
    labels = [str(choice["label"]) for choice in choices]
    assert len(choices) == 4
    assert len(set(values)) == 4
    assert labels.count(str(payload["correct_answer"])) == 1
    assert payload["checker"] == "choice_label_checker"
    assert payload["equivalence"] == "choice_label"


def _validate_math(payload: dict, operation: str) -> None:
    metadata = payload["metadata"]
    coords = metadata["generation_coords"]
    if operation == "compute_section_point_distance_from_origin":
        px, py = coords["P"]
        squared = int(px * px + py * py)
        expected = math.isqrt(squared)
        assert expected > 0 and expected * expected == squared
        assert str(expected) == str(payload["correct_value"])
        return

    answer = metadata.get("semantic_answer") or payload["correct_answer"]
    parsed = parse_coordinate_pair_answer(answer)
    assert parsed is not None
    if operation == "compute_centroid_coordinates":
        points = [coords["A"], coords["B"], coords["C"]]
        expected = (
            sum(point[0] for point in points) / 3,
            sum(point[1] for point in points) / 3,
        )
    else:
        m, n = [int(value) for value in metadata["ratio_values"].split(":")]
        point_a, point_b = coords["A"], coords["B"]
        assert m + n != 0 and point_a != point_b
        expected = (
            (n * point_a[0] + m * point_b[0]) / (m + n),
            (n * point_a[1] + m * point_b[1]) / (m + n),
        )
    assert math.isclose(float(parsed[0]), float(expected[0]), abs_tol=1e-9)
    assert math.isclose(float(parsed[1]), float(expected[1]), abs_tol=1e-9)


def main() -> int:
    report = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    rows = report["generator_specs"]
    operations = {
        row["operation"]: row
        for row in rows
    }
    seed_results: dict[str, dict[str, int]] = {}
    for operation, row in sorted(operations.items()):
        spec = _runtime_spec(row)
        for seed in range(10):
            payload = generate_division_point_payload(
                SKILL_ID,
                row["problem_type_id"],
                spec,
                seed,
            )
            question = str(payload.get("question_text") or "").strip()
            assert question and "placeholder" not in question.lower()
            assert payload["answer_contract"]["checker"] == row["checker_key"]
            if payload.get("choices"):
                _validate_choices(payload)
            _validate_math(payload, operation)
        seed_results[operation] = {"seeds": 10, "passed": 10}

    choice_row = next(row for row in rows if row["source_id"] == 4512)
    choice_spec = _runtime_spec(choice_row)
    for seed in range(10):
        payload = generate_division_point_payload(
            SKILL_ID,
            choice_row["problem_type_id"],
            choice_spec,
            seed,
        )
        _validate_choices(payload)
        _validate_math(payload, choice_row["operation"])

    print(
        json.dumps(
            {
                "phase": "phase2",
                "skill_id": SKILL_ID,
                "dry_run": True,
                "ai_llm_used": False,
                "generator_specs_count": len(rows),
                "build_candidate_count": len(
                    [row for row in rows if row["status"] == "draft"]
                ),
                "verified_reference_source_id": 4421,
                "operation_seed_results": seed_results,
                "internal_choice_extra": {"seeds": 10, "passed": 10},
                "phase3_executed": False,
                "component_created": False,
                "tracker_modified": False,
                "published": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
