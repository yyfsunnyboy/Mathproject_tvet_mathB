from __future__ import annotations

from unittest.mock import patch

from core.checkers.coordinate_pair_checker import check_coordinate_pair_answer
from core.gencode.example_feature_extractor import extract_example_feature
from core.gencode.main_skill_anchor import build_main_skill_anchor
from core.gencode.problem_type_induction import induce_problem_types_from_examples
from core.gencode.semantic_alignment import evaluate_source_example_alignment
from core.gencode.task_families import (
    DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    DIVISION_POINT_COORDINATES_FAMILY,
)


def _ex(ex_id: int, stem: str, answer: str = "(0,-2)", skill_id: str = "vh_數學B1_DivisionPointCoordinates") -> dict:
    return {
        "id": ex_id,
        "example_id": ex_id,
        "skill_id": skill_id,
        "problem_text": stem,
        "correct_answer": answer,
    }


STEM_4423 = "已知 A(-1,1)、B(-3,-3)、C(4,-4)，試求 △ABC 的重心坐標。"
STEM_MIDPOINT = "求 A(1,2)、B(5,6) 的中點坐標。"
STEM_INTERNAL = "P 內分 AB，AP:PB=2:3，求 P 坐標。"
STEM_DISTANCE = "求 A(1,2) 與 B(5,6) 的距離。"
STEM_CENTROID = STEM_4423


def test_main_skill_anchor_division_point_broad():
    meta = {"skill_ch_name": "分點坐標", "skill_en_name": "Division Point Coordinates"}
    anchor = build_main_skill_anchor("vh_數學B1_DivisionPointCoordinates", meta)
    assert DIVISION_POINT_COORDINATES_FAMILY in anchor["expected_task_families"]
    assert DISTANCE_BETWEEN_TWO_POINTS_FAMILY not in anchor["expected_task_families"]
    assert anchor["skill_anchor_scope"] == "broad"
    assert "compute_midpoint_coordinates" in anchor["expected_subskill_candidates"]
    assert "compute_centroid_coordinates" in anchor["expected_subskill_candidates"]


def test_main_skill_anchor_midpoint_narrow():
    meta = {"skill_ch_name": "中點坐標"}
    anchor = build_main_skill_anchor("vh_mock_MidpointCoordinates", meta)
    assert anchor["skill_anchor_scope"] == "narrow"
    assert anchor["expected_subskill_candidates"] == ["compute_midpoint_coordinates"]


def test_main_skill_anchor_centroid_narrow():
    meta = {"skill_ch_name": "重心坐標"}
    anchor = build_main_skill_anchor("vh_mock_CentroidCoordinates", meta)
    assert anchor["skill_anchor_scope"] == "narrow"
    assert anchor["expected_subskill_candidates"] == ["compute_centroid_coordinates"]


def test_4423_centroid_feature():
    feat = extract_example_feature(_ex(4423, STEM_4423, "(0,-2)"))
    assert feat["target_task"] == "compute_centroid_coordinates"
    assert feat["task_family"] == DIVISION_POINT_COORDINATES_FAMILY


def test_midpoint_and_internal_division_features():
    mid = extract_example_feature(_ex(1, STEM_MIDPOINT, "(3,4)"))
    assert mid["target_task"] == "compute_midpoint_coordinates"
    internal = extract_example_feature(_ex(2, STEM_INTERNAL, "(2,3)"))
    assert internal["target_task"] == "compute_internal_division_point_coordinates"


def test_midpoint_skill_midpoint_source_pass():
    meta = {"skill_ch_name": "中點坐標"}
    anchor = build_main_skill_anchor("vh_mock_Midpoint", meta)
    feat = extract_example_feature(_ex(1, STEM_MIDPOINT, "(3,4)"))
    row = evaluate_source_example_alignment(set(), feat, main_skill_anchor=anchor)
    assert row["alignment_kind"] == "same_family_match"
    assert row["subskill_match"] is True
    assert row["included_in_phase1"] is True
    assert row["exclude_reason"] != "source_example_skill_mismatch"


def test_midpoint_skill_centroid_source_subskill_mismatch():
    meta = {"skill_ch_name": "中點坐標"}
    anchor = build_main_skill_anchor("vh_mock_Midpoint", meta)
    feat = extract_example_feature(_ex(4423, STEM_CENTROID, "(0,-2)"))
    row = evaluate_source_example_alignment(set(), feat, main_skill_anchor=anchor)
    assert row["alignment_kind"] == "same_family_subskill_mismatch"
    assert row["exclude_reason"] == "same_family_subskill_mismatch"
    assert row["requires_human_action"] is True
    assert row["included_in_phase1"] is True
    assert feat["target_task"] == "compute_centroid_coordinates"
    assert feat["target_task"] != "compute_midpoint_coordinates"


def test_division_point_skill_mixed_subskills_pass_or_warn_not_block():
    skill_id = "vh_數學B1_DivisionPointCoordinates"
    meta = {"skill_ch_name": "分點坐標"}
    examples = [
        _ex(1, STEM_MIDPOINT, "(3,4)", skill_id=skill_id),
        _ex(2, STEM_CENTROID, "(0,-2)", skill_id=skill_id),
        _ex(3, STEM_INTERNAL, "(2,3)", skill_id=skill_id),
    ]
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        out = induce_problem_types_from_examples(skill_id, examples)
    assert str(out.get("source_alignment_status")) in {"pass", "warn"}
    tasks = {f.get("target_task") for f in out.get("example_features") or []}
    assert "compute_midpoint_coordinates" in tasks
    assert "compute_centroid_coordinates" in tasks
    cands = out.get("candidate_problem_types") or []
    families = {
        str((c.get("problem_type_spec_draft") or {}).get("task_family", "")).strip()
        for c in cands
        if isinstance(c, dict)
    }
    assert DISTANCE_BETWEEN_TWO_POINTS_FAMILY not in families


def test_division_point_skill_distance_family_mismatch_blocks_distance_generator():
    skill_id = "vh_數學B1_DivisionPointCoordinates"
    meta = {"skill_ch_name": "分點坐標"}
    examples = [
        _ex(10, STEM_DISTANCE, "5", skill_id=skill_id),
        _ex(11, STEM_DISTANCE, "6", skill_id=skill_id),
        _ex(12, STEM_DISTANCE, "7", skill_id=skill_id),
        _ex(13, STEM_DISTANCE, "8", skill_id=skill_id),
    ]
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        out = induce_problem_types_from_examples(skill_id, examples, spec_mode="rule_first_induce_from_sources")
    cands = out.get("candidate_problem_types") or []
    families = {
        str((c.get("problem_type_spec_draft") or {}).get("task_family", "")).strip()
        for c in cands
        if isinstance(c, dict)
    }
    assert not any(f == DISTANCE_BETWEEN_TWO_POINTS_FAMILY for f in families)
    assert str(out.get("source_alignment_status")) in {"block", "warn"}
    assert out.get("alignment_blockers") or out.get("excluded_source_examples")


def test_centroid_skill_centroid_source_match():
    meta = {"skill_ch_name": "重心坐標"}
    anchor = build_main_skill_anchor("vh_mock_Centroid", meta)
    feat = extract_example_feature(_ex(4423, STEM_CENTROID, "(0,-2)"))
    row = evaluate_source_example_alignment(set(), feat, main_skill_anchor=anchor)
    assert row["alignment_kind"] == "same_family_match"
    assert feat["target_task"] == "compute_centroid_coordinates"


def test_4423_not_source_example_skill_mismatch():
    meta = {"skill_ch_name": "分點坐標"}
    anchor = build_main_skill_anchor("vh_數學B1_DivisionPointCoordinates", meta)
    feat = extract_example_feature(_ex(4423, STEM_4423))
    row = evaluate_source_example_alignment(set(), feat, main_skill_anchor=anchor)
    assert row["included_in_phase1"] is True
    assert row["exclude_reason"] != "source_example_skill_mismatch"


def test_coordinate_pair_checker_formats():
    ca = "(0,-2)"
    for ua in ["0,-2", "(0,-2)", "（0，-2）", "x=0,y=-2"]:
        assert check_coordinate_pair_answer(ua, ca)
    assert not check_coordinate_pair_answer("(1,-2)", ca)
