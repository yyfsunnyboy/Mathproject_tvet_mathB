# -*- coding: utf-8 -*-
"""Regression tests for B2 Ch3 FAIL-11 visual pipeline hardening.

No example_id / chapter hardcodes in production code — fixtures live here only.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.textbook_pdf_visual_acceptance import (
    REASON_CROSSES_QUESTION_BOUNDARY,
    REASON_INCOMPLETE_MULTI_FIGURE,
    REASON_NON_QUESTION_CONTAMINATION,
    REASON_SUSPICIOUS_SHARED_ASSET,
    VISUAL_STATUS_ACCEPTED,
    VISUAL_STATUS_NEEDS_REVIEW,
    VISUAL_STATUS_REJECTED,
    annotate_shared_asset_ownership,
    bbox_iou,
    clip_bbox_to_question_boundary,
    detect_contamination,
    detect_multi_figure_labels,
    evaluate_visual_acceptance,
    legitimate_shared_visual,
    student_asset_is_accepted,
)
from core.question_image_assets import list_student_image_assets_from_notes

ROOT = Path(__file__).resolve().parents[1]
DRYRUN = ROOT / "reports" / "b2_ch3_visual_pipeline_hardened_dryrun.json"
TRACE = ROOT / "reports" / "b2_ch3_visual_fail11_pipeline_trace.json"
QA_MANUAL = ROOT / "scratch" / "_b2_ch3_visual_qa" / "qa_manual.json"

FAIL11 = [
    11732,
    11736,
    11744,
    11748,
    11751,
    11752,
    11753,
    11795,
    11804,
    11806,
    11817,
]


def test_clip_bbox_does_not_invert_when_next_boundary_above_crop():
    bbox = [100.0, 400.0, 200.0, 500.0]
    clipped = clip_bbox_to_question_boundary(
        bbox, question_bbox=[36.0, 100.0, 500.0, 390.0], next_question_y=395.0
    )
    # Small/no material overflow above stem of next Q — keep usable geometry.
    assert clipped[3] > clipped[1]


def test_material_cross_question_boundary_is_clipped():
    bbox = [100.0, 200.0, 200.0, 600.0]
    clipped = clip_bbox_to_question_boundary(
        bbox, question_bbox=[36.0, 100.0, 500.0, 350.0], next_question_y=360.0
    )
    assert clipped[3] <= 360.0


def test_multi_figure_labels_detected():
    labels = detect_multi_figure_labels("如圖（一）與圖（二）所示")
    assert len(labels) >= 2


def test_incomplete_multi_figure_needs_review():
    acc = evaluate_visual_acceptance(
        problem_text="如圖（一）與圖（二），求夾角",
        visual_bbox=[400.0, 300.0, 520.0, 400.0],
        question_bbox=[36.0, 200.0, 560.0, 500.0],
        next_question_y=520.0,
        page_words=[],
        match_score=0.95,
        strong_cue=True,
    )
    assert REASON_INCOMPLETE_MULTI_FIGURE in acc["visual_review_reasons"]
    assert acc["visual_status"] == VISUAL_STATUS_NEEDS_REVIEW


def test_contamination_self_assessment_rejected():
    words = [
        (400, 580, 520, 600, "熟習度自評表"),
    ]
    acc = evaluate_visual_acceptance(
        problem_text="如圖，平行四邊形",
        visual_bbox=[400.0, 570.0, 560.0, 640.0],
        question_bbox=[36.0, 450.0, 560.0, 700.0],
        next_question_y=None,
        page_words=words,
        match_score=0.95,
        strong_cue=True,
    )
    assert REASON_NON_QUESTION_CONTAMINATION in acc["visual_review_reasons"]
    assert acc["visual_status"] == VISUAL_STATUS_REJECTED
    assert detect_contamination("熟習度自評表") == "熟習度自評"


def test_input_ui_contamination_detected():
    assert detect_contamination("請在下方輸入訊息") == "輸入訊息"


def test_legitimate_shared_stem_allows_reuse():
    row_a = {
        "id": 11741,
        "problem_text": "如圖，△ABC中，D、E為AB的三等分點，F為AC的中點，試以a、b表示BF。",
        "visual_bbox": [85.0, 409.0, 524.0, 501.0],
        "visual_page": 13,
        "visual_status": VISUAL_STATUS_NEEDS_REVIEW,
        "visual_review_reasons": [REASON_CROSSES_QUESTION_BOUNDARY],
        "should_mount": False,
    }
    row_b = {
        "id": 11742,
        "problem_text": "如圖，△ABC中，D、E為AB的三等分點，F為AC的中點，試以a、b表示CE。",
        "visual_bbox": [85.0, 409.0, 524.0, 501.0],
        "visual_page": 13,
        "visual_status": VISUAL_STATUS_NEEDS_REVIEW,
        "visual_review_reasons": [REASON_CROSSES_QUESTION_BOUNDARY],
        "should_mount": False,
    }
    assert legitimate_shared_visual(row_a, row_b)
    annotate_shared_asset_ownership([row_a, row_b])
    assert row_a["legitimate_shared_visual"] is True
    assert row_b["visual_status"] == VISUAL_STATUS_ACCEPTED
    assert REASON_SUSPICIOUS_SHARED_ASSET not in (row_a.get("visual_review_reasons") or [])


def test_suspicious_shared_asset_demoted():
    row_a = {
        "id": 11751,
        "problem_text": "如圖，基礎題8 獨立三角形構形AAA",
        "visual_bbox": [452.0, 370.0, 504.0, 434.0],
        "question_bbox": [36.0, 200.0, 560.0, 360.0],  # does not own crop center
        "visual_page": 16,
        "visual_status": VISUAL_STATUS_ACCEPTED,
        "visual_review_reasons": [],
        "should_mount": True,
    }
    row_b = {
        "id": 11752,
        "problem_text": "如圖，進階題9 完全不同的構形BBB",
        "visual_bbox": [452.0, 370.0, 504.0, 434.0],
        "question_bbox": [36.0, 360.0, 560.0, 480.0],  # owns crop center
        "visual_page": 16,
        "visual_status": VISUAL_STATUS_ACCEPTED,
        "visual_review_reasons": [],
        "should_mount": True,
    }
    annotate_shared_asset_ownership([row_a, row_b])
    assert REASON_SUSPICIOUS_SHARED_ASSET in row_a["visual_review_reasons"]
    assert row_a["should_mount"] is False
    assert row_b["should_mount"] is True
    assert REASON_SUSPICIOUS_SHARED_ASSET not in (row_b.get("visual_review_reasons") or [])


def test_student_assets_skip_needs_review(tmp_path):
    rel = "static/question_assets/test_gate/fig.png"
    abs_path = tmp_path / rel.replace("/", "\\") if False else tmp_path / Path(rel)
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_bytes(b"\x89PNG\r\n\x1a\n")
    notes = {
        "image_assets": [
            {
                "path": rel,
                "display_path": rel,
                "visual_status": VISUAL_STATUS_NEEDS_REVIEW,
                "visual_review_reasons": ["suspicious_shared_asset"],
            }
        ],
        "needs_image_review": True,
        "visual_status": VISUAL_STATUS_NEEDS_REVIEW,
    }
    assert student_asset_is_accepted(notes["image_assets"][0], notes=notes) is False
    assert list_student_image_assets_from_notes(notes, root_path=str(tmp_path)) == []

    notes["image_assets"][0]["visual_status"] = VISUAL_STATUS_ACCEPTED
    notes["image_assets"][0]["needs_crop_review"] = False
    notes["needs_image_review"] = False
    assert list_student_image_assets_from_notes(notes, root_path=str(tmp_path))


def test_legacy_assets_without_visual_status_remain_student_ready(tmp_path):
    rel = "static/question_assets/test_gate/legacy.png"
    abs_path = tmp_path / Path(rel)
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_bytes(b"\x89PNG\r\n\x1a\n")
    notes = {"image_assets": [{"path": rel, "display_path": rel}]}
    assert student_asset_is_accepted(notes["image_assets"][0], notes=notes) is True
    assert len(list_student_image_assets_from_notes(notes, root_path=str(tmp_path))) == 1


@pytest.mark.skipif(not DRYRUN.is_file(), reason="hardening dry-run report missing")
def test_fail11_dryrun_wrong_accepted_is_zero():
    data = json.loads(DRYRUN.read_text(encoding="utf-8"))
    summary = data["summary"]
    assert summary["wrong_accepted"] == 0
    assert summary["protected"] == 11
    assert summary["legit_share_not_flagged_suspicious"] is True
    by_id = {int(r["example_id"]): r for r in data["rows"]}
    for eid in FAIL11:
        row = by_id[eid]
        assert row["matched"] is True
        assert row["new_decision"] != "wrong_mapping_accepted"


@pytest.mark.skipif(not TRACE.is_file(), reason="fail11 trace report missing")
def test_fail11_trace_has_first_wrong_decision_for_all():
    data = json.loads(TRACE.read_text(encoding="utf-8"))
    rows = {int(r["example_id"]): r for r in data["fail11"]}
    assert set(rows) == set(FAIL11)
    for eid, row in rows.items():
        assert row["first_wrong_decision"]
        assert row["pipeline_stage"]
        assert row["failure_class"]


@pytest.mark.skipif(not QA_MANUAL.is_file(), reason="qa_manual missing")
def test_known_wrong_bboxes_are_not_identical_to_correct_mount_plan():
    from scripts.pdf_visual_repair_b2_ch3_fail11 import MOUNT_PLAN

    qa = json.loads(QA_MANUAL.read_text(encoding="utf-8"))
    fails = {int(i["id"]): i for i in qa["items"] if i.get("grade") == "FAIL"}
    for eid in FAIL11:
        assert bbox_iou(fails[eid]["bbox"], MOUNT_PLAN[eid]["bbox"]) < 0.85


def test_shared_asset_ownership_matrix_expectations():
    """Structural ownership expectations from FAIL-11 / PASS cases."""
    # Illegal pairs must not be treated as legitimate solely by identical bbox.
    illegal = legitimate_shared_visual(
        {
            "problem_text": "如圖，線段AB等分",
            "visual_bbox": [400, 500, 560, 610],
            "visual_page": 15,
        },
        {
            "problem_text": "如圖，兩向量網格",
            "visual_bbox": [400, 500, 560, 610],
            "visual_page": 15,
        },
    )
    assert illegal is False
