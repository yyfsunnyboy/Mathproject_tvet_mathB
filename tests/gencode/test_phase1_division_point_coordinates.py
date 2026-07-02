from __future__ import annotations

import sqlite3
from pathlib import Path

from core.gencode.classifiers import get_classifier_for_skill
from core.gencode.classifiers.fallback_classifier import FallbackClassifier
from core.gencode.pipeline_orchestrator import (
    PHASE1_CLASSIFICATION_UNRESOLVED,
    run_v3_no_llm_phase1_for_example,
)


SKILL_ID = "vh_數學B1_DivisionPointCoordinates"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"


def _load_examples(skill_id: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        return [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM textbook_examples WHERE skill_id = ? ORDER BY id",
                (skill_id,),
            ).fetchall()
        ]
    finally:
        conn.close()


def test_all_division_point_sources_resolve_with_complete_contracts() -> None:
    examples = _load_examples(SKILL_ID)
    assert len(examples) == 7

    expected_operations = {
        4420: "compute_internal_division_point_coordinates",
        4421: "compute_internal_division_point_coordinates",
        4423: "compute_centroid_coordinates",
        4427: "compute_internal_division_point_coordinates",
        4438: "compute_internal_division_point_coordinates",
        4512: "compute_internal_division_point_coordinates",
        4513: "compute_section_point_distance_from_origin",
    }
    conn = sqlite3.connect(DB_PATH)
    try:
        results = [
            run_v3_no_llm_phase1_for_example(SKILL_ID, example, conn=conn)
            for example in examples
        ]
    finally:
        conn.close()

    assert {result["problem_type_id"] for result in results} == set(expected_operations.values())
    for result in results:
        assert result["classification_status"] == "resolved"
        assert result["problem_type_id"] != "unknown"
        assert result["problem_type_id"] == expected_operations[result["source_example_id"]]
        assert result["classification_source"] == "python_skill_classifier"
        assert result["required_capabilities"]
        assert result["presentation_mode"] in {"short_answer", "single_choice"}
        contract = result["answer_contract"]
        assert contract["answer_type"]
        assert contract["checker_key"]
        assert contract["equivalence_type"]


def test_unknown_skill_still_fails_fast() -> None:
    skill_id = "vh_Unknown_Coordinate_Skill"
    result = run_v3_no_llm_phase1_for_example(
        skill_id,
        {
            "id": 99999,
            "skill_id": skill_id,
            "problem_text": "A(0,0), B(2,2), AP:PB=1:1",
            "correct_answer": "",
            "detailed_solution": "",
        },
    )
    assert result["classification_status_code"] == PHASE1_CLASSIFICATION_UNRESOLVED
    assert result["reason"] == "phase1_classifier_not_registered"


def test_other_coordinate_skill_dispatch_is_unchanged() -> None:
    classifier = get_classifier_for_skill("vh_數學B1_DistanceBetweenTwoPointsInPlane")
    assert isinstance(classifier, FallbackClassifier)
