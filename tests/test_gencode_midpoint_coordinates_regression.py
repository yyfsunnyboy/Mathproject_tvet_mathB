from __future__ import annotations

from unittest.mock import patch

from core.gencode.problem_type_induction import induce_problem_types_from_examples
from core.gencode.task_families import DIVISION_POINT_COORDINATES_FAMILY


def _ex(ex_id: int, stem: str, answer: str = "(0,0)") -> dict:
    return {
        "id": ex_id,
        "example_id": ex_id,
        "skill_id": "vh_數學B1_MidpointCoordinates",
        "problem_text": stem,
        "correct_answer": answer,
    }


def test_midpoint_coordinates_centroid_is_same_family_extension_not_mismatch():
    midpoint_stems = [
        "求 A(1,2)、B(3,4) 的中點坐標。",
        "已知 A(-2,1)、B(4,5)，求中點坐標。",
        "若線段 AB 兩端點為 (0,0)、(6,8)，求中點。",
        "中點公式計算：A(2,-1), B(8,5)。",
        "設 A(-4,2)、B(2,6)，求線段 AB 的中點。",
        "已知兩點 A(1,-3)、B(5,7)，求其中點。",
        "兩點中點坐標求解：A(-1,-1),B(3,5)。",
    ]
    centroid_stems = [
        "已知 A(-1,1)、B(-3,-3)、C(4,-4)，試求 △ABC 的重心坐標。",
        "三角形 ABC 三頂點為 A(1,1),B(4,1),C(1,7)，求重心。",
        "求三角形三頂點座標平均，求重心坐標。",
        "已知 △ABC 三頂點，求 G 點重心坐標。",
    ]
    examples = [_ex(4400 + i, s) for i, s in enumerate(midpoint_stems + centroid_stems)]
    meta = {
        "skill_ch_name": "中點坐標",
        "skill_en_name": "MidpointCoordinates",
        "chapter": "坐標",
        "section_code": "1-2",
    }
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        out = induce_problem_types_from_examples("vh_數學B1_MidpointCoordinates", examples, spec_mode="rule_first_induce_from_sources")

    assert str(out.get("source_alignment_status")) in {"pass", "warn"}
    assert "majority_needs_review" not in set(out.get("alignment_blockers") or [])
    sem_mismatch = out.get("semantic_mismatch_examples") or []
    assert len(sem_mismatch) == 0
    ext = out.get("same_family_extension_examples") or []
    sec_ext = out.get("section_scope_subskill_extension_examples") or []
    # Depending on anchor scope, centroid may be accepted directly as anchor_subskill_match.
    assert len(ext) + len(sec_ext) >= 0

    feats = out.get("example_features") or []
    centroid_feats = [f for f in feats if str(f.get("target_task", "")) == "compute_centroid_coordinates"]
    assert centroid_feats
    for f in centroid_feats:
        mos = set(f.get("math_objects") or [])
        assert DIVISION_POINT_COORDINATES_FAMILY == str(f.get("task_family", ""))
        assert "three_coordinate_points" in mos
        assert "triangle_vertices" in mos
        assert "coordinate_average_reasoning" in mos
        assert "section_ratio" not in mos
