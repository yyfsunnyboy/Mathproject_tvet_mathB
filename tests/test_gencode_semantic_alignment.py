from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from core.gencode.example_feature_extractor import extract_example_feature
from core.gencode.pipeline_orchestrator import _load_examples, run_gencode_phase2
from core.gencode.problem_type_induction import induce_problem_types_from_examples
from core.gencode.semantic_alignment import alignment_blocks_phase2, evaluate_semantic_alignment
from core.gencode.task_families import (
    DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    task_family_for_task,
)


def _ex(
    ex_id: int,
    stem: str,
    answer: str = "7",
    choices: list | None = None,
    skill_id: str = "",
) -> dict:
    row = {
        "id": ex_id,
        "example_id": ex_id,
        "skill_id": skill_id,
        "problem_text": stem,
        "correct_answer": answer,
    }
    if choices is not None:
        row["choices"] = choices
    return row


STEM_SOLVE_K_4419 = (
    r"設 A(k,-5)、B(2,7) 為坐標平面上兩點，且 \overline{AB}=13，試求 k 值。"
)
STEM_SOLVE_K_4437 = (
    r"設 A(-2,-6)、B(k,2) 為坐標平面上兩點，且 \overline{AB}=10，試求 k 值。"
)
STEM_COMPUTE_AB = r"設 A(1,2)、B(4,6)，求 \overline{AB} 的長度。"
STEM_QUADRANT = "點 P(-2,3) 位於第幾象限？"


def test_solve_unknown_coordinate_4419_style():
    feat = extract_example_feature(_ex(4419, STEM_SOLVE_K_4419, "-3,7"))
    assert feat.get("target_task") == "solve_unknown_coordinate_from_two_point_distance"
    assert feat.get("task_family") == DISTANCE_BETWEEN_TWO_POINTS_FAMILY
    assert feat.get("target_task") != "classify_quadrant"


def test_solve_unknown_coordinate_4437_style():
    feat = extract_example_feature(_ex(4437, STEM_SOLVE_K_4437, "7"))
    assert feat.get("target_task") == "solve_unknown_coordinate_from_two_point_distance"
    assert feat.get("task_family") == DISTANCE_BETWEEN_TWO_POINTS_FAMILY


def test_compute_distance_between_two_points():
    feat = extract_example_feature(_ex(1, STEM_COMPUTE_AB, "5"))
    assert feat.get("target_task") == "compute_distance_between_two_points"
    assert feat.get("task_family") == DISTANCE_BETWEEN_TWO_POINTS_FAMILY


def test_mixed_distance_family_tasks_pass():
    skill_id = "mock_TwoPointDistanceFamily"
    skill_id = "mock_TwoPointDistanceFamily"
    examples = [
        _ex(1, STEM_COMPUTE_AB, "5", skill_id=skill_id),
        _ex(2, STEM_SOLVE_K_4419, "-3,7", skill_id=skill_id),
    ]
    meta = {"skill_ch_name": "平面上兩點間的距離", "skill_en_name": "Distance Between Two Points"}
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        out = induce_problem_types_from_examples(skill_id, examples)
    assert str(out.get("source_alignment_status")) in {"pass", "warn"}
    assert not alignment_blocks_phase2(out.get("semantic_alignment"))
    dist = out.get("source_family_distribution") or {}
    assert dist.get(DISTANCE_BETWEEN_TWO_POINTS_FAMILY, 0) == 2
    tasks = {f.get("target_task") for f in out.get("example_features") or []}
    assert "compute_distance_between_two_points" in tasks
    assert "solve_unknown_coordinate_from_two_point_distance" in tasks


def test_mixed_distance_and_quadrant_block():
    skill_id = "mock_TwoPointDistanceMixedBad"
    examples = [
        _ex(1, STEM_COMPUTE_AB, "5"),
        _ex(2, STEM_QUADRANT, "第二象限"),
        _ex(3, "點 Q(1,-2) 在第幾象限？", "第四象限"),
        _ex(4, "坐標 (3,4) 位於哪一象限？", "第一象限"),
    ]
    meta = {"skill_ch_name": "平面上兩點間的距離", "skill_en_name": "Distance Between Two Points"}
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        out = induce_problem_types_from_examples(skill_id, examples, spec_mode="rule_first_induce_from_sources")
    assert str(out.get("source_alignment_status")) == "block"
    blockers = out.get("alignment_blockers") or []
    assert "mixed_source_families" in blockers or "source_examples_mismatch" in blockers


def test_quadrant_explicit_not_distance():
    feat = extract_example_feature(_ex(8, STEM_QUADRANT, "第二象限"))
    assert feat.get("target_task") == "classify_quadrant"
    assert task_family_for_task(feat.get("target_task")) != DISTANCE_BETWEEN_TWO_POINTS_FAMILY


def test_coordinate_points_without_quadrant_not_classify():
    feat = extract_example_feature(
        _ex(9, "設 A(1,2)、B(3,4) 為坐標平面上兩點。", "2")
    )
    assert feat.get("target_task") != "classify_quadrant"


def test_distance_skill_quadrant_sources_blocked():
    skill_id = "mock_TwoPointDistance"
    examples = [
        _ex(1, STEM_QUADRANT, "第二象限", skill_id=skill_id),
        _ex(2, "點 Q(4, -1) 位於哪一象限？", "第四象限", skill_id=skill_id),
        _ex(3, "坐標 (-2, 5) 在第幾象限？", "第二象限", skill_id=skill_id),
        _ex(4, "點 R(1, -3) 在第幾象限？", "第四象限", skill_id=skill_id),
    ]
    meta = {"skill_ch_name": "平面上兩點間的距離", "skill_en_name": "Two Point Distance"}
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        out = induce_problem_types_from_examples(skill_id, examples, spec_mode="rule_first_induce_from_sources")
    assert str(out.get("source_alignment_status")) == "block"


def test_quadrant_skill_quadrant_sources_pass():
    skill_id = "mock_QuadrantClassification"
    examples = [
        _ex(1, STEM_QUADRANT, "第二象限", skill_id=skill_id),
        _ex(2, "點 Q(4, -1) 位於哪一象限？", "第四象限", skill_id=skill_id),
    ]
    meta = {"skill_ch_name": "象限判斷", "skill_en_name": "Quadrant Classification"}
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        out = induce_problem_types_from_examples(skill_id, examples)
    assert str(out.get("source_alignment_status")) in {"pass", "warn"}
    assert not alignment_blocks_phase2(out.get("semantic_alignment"))


def test_phase2_blocks_when_phase1_alignment_blocked():
    skill_id = "mock_phase2_block"
    phase1 = {
        "source_alignment_status": "block",
        "alignment_blockers": ["mixed_source_families"],
        "candidate_problem_types": [
            {
                "problem_type_id": "short_answer_classify_quadrant_coordinate_point",
                "matched_example_count": 3,
                "answer_contract_proposal": {"answer_type": "short_answer"},
                "checker_key_proposal": "text_checker",
                "equivalence_type_proposal": "string_equivalence",
                "spec_source": "phase1_induced_draft",
                "generator_readiness": "runtime_ready",
                "problem_type_spec_draft": {
                    "problem_type_id": "short_answer_classify_quadrant_coordinate_point",
                    "target_task": "classify_quadrant",
                    "answer_contract": {"answer_type": "short_answer"},
                    "generator_contract": {"template_families": ["classify_quadrant"]},
                },
            }
        ],
    }
    from core.gencode import pipeline_orchestrator as po

    with tempfile.TemporaryDirectory() as td:
        report_dir = Path(td)
        (report_dir / f"{skill_id}_phase1_summary.json").write_text(
            json.dumps(phase1, ensure_ascii=False),
            encoding="utf-8",
        )
        from core.gencode import pipeline_state as ps
        with patch.object(po, "REPORT_DIR", report_dir), \
             patch.object(ps, "GENCODE_REPORT_DIR", report_dir), \
             patch.object(ps, "GENCODE_DRAFT_DIR", report_dir / "drafts"):
            out = run_gencode_phase2(skill_id, dry_run=True)
    statuses = [r.get("generator_status") for r in out.get("generator_results") or []]
    assert statuses and all(s == "blocked" for s in statuses)


def test_solve_unknown_induced_set_contract_blocks_runtime_if_no_checker():
    skill_id = "mock_solve_unknown_contract"
    examples = [
        _ex(1, STEM_SOLVE_K_4419, "-3,7", skill_id=skill_id),
        _ex(2, STEM_SOLVE_K_4437, "7", skill_id=skill_id),
    ]
    meta = {"skill_ch_name": "平面上兩點間的距離", "skill_en_name": "Distance"}
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        out = induce_problem_types_from_examples(skill_id, examples)
    specs = out.get("induced_problem_type_specs") or []
    solve_specs = [s for s in specs if s.get("target_task") == "solve_unknown_coordinate_from_two_point_distance"]
    assert solve_specs
    ac = solve_specs[0].get("answer_contract") or {}
    assert ac.get("answer_type") == "solution_set"
    assert ac.get("checker") == "solution_set_checker"
    assert ac.get("answer_equivalence") == "unordered_solution_set"


def test_load_examples_strict_skill_id_filter():
    skill_id = "mock_strict_query"
    rows = [
        {"id": 1, "skill_id": skill_id, "problem_text": "ok"},
        {"id": 2, "skill_id": "", "problem_text": "missing sid"},
        {"id": 3, "skill_id": "other_skill", "problem_text": "wrong"},
    ]

    class FakeCursor:
        def fetchall(self):
            return rows

    class FakeConn:
        row_factory = None

        def execute(self, sql, params):
            assert "WHERE skill_id=?" in sql
            assert params == (skill_id,)
            return FakeCursor()

        def close(self):
            return None

    with patch("core.gencode.pipeline_orchestrator.sqlite3.connect", return_value=FakeConn()):
        loaded = _load_examples(skill_id)
    assert len(loaded) == 1
