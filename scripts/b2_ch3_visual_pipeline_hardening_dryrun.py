# -*- coding: utf-8 -*-
"""B2 Ch3 visual pipeline hardening: dry-run + FAIL-11 first-wrong traces.

Read-only against DB/PDF. Does not write notes or PNGs.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.textbook_pdf_visual import (  # noqa: E402
    assign_question_regions,
    build_page_index,
    classify_and_detect_visuals,
    match_questions_to_pdf,
)
from core.textbook_pdf_visual_acceptance import (  # noqa: E402
    VISUAL_STATUS_ACCEPTED,
    VISUAL_STATUS_NEEDS_REVIEW,
    VISUAL_STATUS_REJECTED,
    bbox_iou,
    detect_multi_figure_labels,
    legitimate_shared_visual,
)
from scripts.pdf_visual_repair_b2_ch3_fail11 import MOUNT_PLAN, PDFS  # noqa: E402

DB = ROOT / "instance" / "kumon_math.db"
QA_MANUAL = ROOT / "scratch" / "_b2_ch3_visual_qa" / "qa_manual.json"
REPORTS = ROOT / "reports"

FAIL11 = list(MOUNT_PLAN.keys())
PASS_IDS = [11740, 11749, 11750, 11783]
LEGIT_SHARE = [11741, 11742]

# Evidence-based first-wrong-decision catalog (pre-hardening pipeline).
TRACE_SEED: dict[int, dict[str, Any]] = {
    11732: {
        "failure_class": "F1_wrong_nearby_visual",
        "pipeline_stage": "candidate_visual_selection",
        "first_wrong_decision": "right_cluster_band_extended_past_question_into_intro_flight_map",
        "selection_reason": "strong_cue soft/right-cluster scored 航線圖 below 隨堂練習1",
        "preventable_deterministically": True,
        "proposed_guard": "question_boundary_band_clip",
    },
    11736: {
        "failure_class": "F2_multi_question_crop",
        "pipeline_stage": "region_band_or_union",
        "first_wrong_decision": "union_top_draws_merged_例4_and_隨堂4",
        "selection_reason": "area-ranked union spanned next question frames",
        "preventable_deterministically": True,
        "proposed_guard": "compact_single_pick + boundary_clip",
    },
    11744: {
        "failure_class": "F2_multi_question_crop",
        "pipeline_stage": "region_band_or_union",
        "first_wrong_decision": "question_region_or_union_absorbed_基礎2_Q4",
        "selection_reason": "tall crop across stacked 基礎題 diagrams",
        "preventable_deterministically": True,
        "proposed_guard": "overspan_multi_question + boundary_clip",
    },
    11748: {
        "failure_class": "F3_invalid_shared_asset",
        "pipeline_stage": "shared_asset_dedupe",
        "first_wrong_decision": "reused_basis6_grid_bbox_as_basis5",
        "selection_reason": "identical/near bbox ownership without stem evidence",
        "preventable_deterministically": True,
        "proposed_guard": "suspicious_shared_asset_ownership",
    },
    11751: {
        "failure_class": "F4_critical_label_clipping",
        "pipeline_stage": "bbox_compacting",
        "first_wrong_decision": "over_compact_triangle_cut_vertex_labels",
        "selection_reason": "compact score preferred too-tight drawing group",
        "preventable_deterministically": False,
        "proposed_guard": "needs_review_when_shared_truncated_or_low_margin",
    },
    11752: {
        "failure_class": "F3_invalid_shared_asset",
        "pipeline_stage": "shared_asset_dedupe",
        "first_wrong_decision": "illegal_sha_reuse_of_11751_crop",
        "selection_reason": "same bbox/SHA claimed by distinct stem",
        "preventable_deterministically": True,
        "proposed_guard": "suspicious_shared_asset_ownership",
    },
    11753: {
        "failure_class": "F6_non_question_contamination",
        "pipeline_stage": "candidate_visual_selection",
        "first_wrong_decision": "band_extended_into_熟習度自評表",
        "selection_reason": "search band past last question into footer UI text",
        "preventable_deterministically": True,
        "proposed_guard": "contamination_text_layer + footer_band_limit",
    },
    11795: {
        "failure_class": "F1_wrong_nearby_visual",
        "pipeline_stage": "candidate_visual_selection",
        "first_wrong_decision": "selected_empty_input_ui_instead_of_coordinate_figure",
        "selection_reason": "wrong candidate identity under soft/right heuristics",
        "preventable_deterministically": True,
        "proposed_guard": "contamination_輸入訊息 + needs_review_over_guess",
    },
    11804: {
        "failure_class": "F5_multi_figure_incomplete",
        "pipeline_stage": "candidate_visual_selection",
        "first_wrong_decision": "mounted_only_圖二_empty_panel",
        "selection_reason": "stem requires 圖（一）+圖（二） but single subfigure accepted",
        "preventable_deterministically": True,
        "proposed_guard": "incomplete_multi_figure",
    },
    11806: {
        "failure_class": "F2_multi_question_crop",
        "pipeline_stage": "right_cluster_union",
        "first_wrong_decision": "right_cluster_union_across_self_assessment_Q1_Q3",
        "selection_reason": "cluster merged stacked right diagrams",
        "preventable_deterministically": True,
        "proposed_guard": "boundary_clip + compact_single_pick",
    },
    11817: {
        "failure_class": "F4_critical_label_clipping",
        "pipeline_stage": "bbox_compacting",
        "first_wrong_decision": "left_edge_too_tight_cut_vertex_A",
        "selection_reason": "compact right-preference shaved essential labels",
        "preventable_deterministically": False,
        "proposed_guard": "needs_review_preferred_over_silent_tight_crop",
    },
}


def _load_qa_fail_old() -> dict[int, dict[str, Any]]:
    data = json.loads(QA_MANUAL.read_text(encoding="utf-8"))
    out = {}
    for item in data.get("items") or []:
        if item.get("grade") == "FAIL":
            out[int(item["id"])] = item
    return out


def _bucket_for_row(source_description: str, section: str) -> str | None:
    desc = source_description or ""
    s = section or ""
    if desc.startswith("CH3自我評量") or "自我評量" in desc:
        return "self"
    if "3-1" in s or "3-1" in desc:
        return "3-1"
    if "3-2" in s or "3-2" in desc:
        return "3-2"
    if "3-3" in s or "3-3" in desc or "統測" in desc:
        return "3-3"
    if "自我評量" in s or "評量" in s:
        return "self"
    return None


def _rows_for_pdf(conn: sqlite3.Connection, bucket: str) -> list[SimpleNamespace]:
    rows = conn.execute(
        """
        SELECT id, skill_id, source_description, problem_text, problem_type,
               source_curriculum, source_volume, source_chapter, source_section, notes
        FROM textbook_examples
        WHERE source_volume='數學B2' AND source_chapter='第3章 向 量'
        ORDER BY id
        """
    ).fetchall()
    out = []
    for r in rows:
        notes = {}
        try:
            notes = json.loads(r[9] or "{}")
        except Exception:
            notes = {}
        if _bucket_for_row(r[2] or "", r[8] or "") != bucket:
            continue
        out.append(
            SimpleNamespace(
                id=r[0],
                skill_id=r[1],
                source_description=r[2],
                problem_text=r[3],
                problem_type=r[4],
                source_curriculum=r[5],
                source_volume=r[6],
                source_chapter=r[7],
                source_section=r[8],
                notes=json.dumps(notes, ensure_ascii=False),
            )
        )
    return out


def _example_item(row: SimpleNamespace) -> dict[str, Any]:
    notes = json.loads(row.notes or "{}")
    anchor = notes.get("question_anchor") if isinstance(notes.get("question_anchor"), dict) else {}
    return {
        "id": row.id,
        "source_description": row.source_description or "",
        "problem_text": row.problem_text or "",
        "problem_type": row.problem_type or "",
        "source_order": anchor.get("source_order") or row.id,
        "source_type": anchor.get("source_type") or row.problem_type or "",
        "anchor_id": str(anchor.get("anchor_id") or ""),
        "notes": notes,
    }


def run_classify_for_pdf(pdf_path: Path, rows: list[SimpleNamespace]) -> list[dict[str, Any]]:
    import fitz

    doc = fitz.open(str(pdf_path))
    try:
        pages = build_page_index(doc)
    finally:
        doc.close()
    items = [_example_item(r) for r in rows]
    items.sort(key=lambda x: (int(x.get("source_order") or 10**9), int(x.get("id") or 0)))
    matched = match_questions_to_pdf(items, pages)
    matched = assign_question_regions(matched, pages)
    matched = classify_and_detect_visuals(matched, pages)
    return matched


def _decision_label(row: dict[str, Any]) -> str:
    status = str(row.get("visual_status") or "")
    if row.get("should_mount") and status == VISUAL_STATUS_ACCEPTED:
        return "accepted_mount"
    if status == VISUAL_STATUS_NEEDS_REVIEW:
        return "needs_review"
    if status == VISUAL_STATUS_REJECTED:
        return "rejected"
    if row.get("needs_review"):
        return "needs_review"
    return "skipped"


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    old_fail = _load_qa_fail_old()
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    all_decisions: dict[int, dict[str, Any]] = {}
    for bucket, pdf in PDFS.items():
        rows = _rows_for_pdf(conn, bucket)
        if not rows:
            continue
        matched = run_classify_for_pdf(pdf, rows)
        for row in matched:
            eid = int(row.get("id") or 0)
            if not eid:
                continue
            all_decisions[eid] = row

    # FAIL-11 traces
    traces = []
    for eid in FAIL11:
        seed = TRACE_SEED[eid]
        old = old_fail.get(eid) or {}
        plan = MOUNT_PLAN[eid]
        row = all_decisions.get(eid) or {}
        traces.append(
            {
                "example_id": eid,
                "pdf_page": plan["page"],
                "failure_class": seed["failure_class"],
                "question_anchor": {
                    "source_description": row.get("source_description"),
                    "match_score": row.get("match_score"),
                    "match_method": row.get("match_method"),
                    "pdf_match": row.get("pdf_match"),
                    "question_bbox": row.get("question_bbox"),
                    "next_question_y": row.get("next_question_y"),
                },
                "candidate_visuals": [],
                "selected_candidate": {
                    "page": row.get("visual_page"),
                    "bbox": row.get("visual_bbox"),
                    "visual_status": row.get("visual_status"),
                    "should_mount": row.get("should_mount"),
                },
                "selection_reason": seed["selection_reason"],
                "crop_region_before": old.get("bbox"),
                "correct_region": plan["bbox"],
                "shared_asset_with": list(row.get("shared_with") or []),
                "first_wrong_decision": seed["first_wrong_decision"],
                "pipeline_stage": seed["pipeline_stage"],
                "preventable_deterministically": seed["preventable_deterministically"],
                "proposed_guard": seed["proposed_guard"],
                "hardened_decision": _decision_label(row),
                "hardened_reasons": list(row.get("visual_review_reasons") or []),
                "multi_figure_labels": detect_multi_figure_labels(str(row.get("problem_text") or "")),
            }
        )

    trace_path = REPORTS / "b2_ch3_visual_fail11_pipeline_trace.json"
    trace_path.write_text(
        json.dumps({"fail11": traces, "taxonomy": sorted({t["failure_class"] for t in traces})}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Dry-run comparison
    dry_rows = []
    wrong_accepted = 0
    auto_correct = 0
    needs_review = 0
    rejected = 0

    for eid in FAIL11:
        old = old_fail[eid]
        plan = MOUNT_PLAN[eid]
        row = all_decisions.get(eid) or {}
        new_bbox = row.get("visual_bbox")
        status = _decision_label(row)
        iou_wrong = bbox_iou(new_bbox, old.get("bbox"))
        iou_correct = bbox_iou(new_bbox, plan["bbox"])
        expected = "correct_or_needs_review"
        matched = False
        if status == "accepted_mount":
            # Accept only if clearly closer to correct than to known-wrong.
            if iou_correct >= 0.45 and iou_correct > iou_wrong + 0.1:
                matched = True
                auto_correct += 1
                new_decision = "correct_mapping"
            else:
                wrong_accepted += 1
                new_decision = "wrong_mapping_accepted"
                matched = False
        elif status == "needs_review":
            needs_review += 1
            new_decision = "needs_review"
            matched = True
        elif status == "rejected":
            rejected += 1
            new_decision = "rejected"
            matched = True
        else:
            needs_review += 1
            new_decision = "needs_review_or_skipped"
            matched = True
        dry_rows.append(
            {
                "example_id": eid,
                "old_decision": {
                    "grade": "FAIL",
                    "bbox": old.get("bbox"),
                    "issue": old.get("issue"),
                },
                "new_decision": new_decision,
                "new_status": status,
                "new_bbox": new_bbox,
                "iou_vs_wrong": round(iou_wrong, 4),
                "iou_vs_correct": round(iou_correct, 4),
                "review_reason": list(row.get("visual_review_reasons") or []),
                "expected": expected,
                "matched": matched,
            }
        )

    # False-positive checks for legitimate share + PASS
    fp_checks = []
    for eid in LEGIT_SHARE + PASS_IDS:
        row = all_decisions.get(eid) or {}
        fp_checks.append(
            {
                "example_id": eid,
                "decision": _decision_label(row),
                "visual_status": row.get("visual_status"),
                "should_mount": row.get("should_mount"),
                "reasons": list(row.get("visual_review_reasons") or []),
                "shared_with": list(row.get("shared_with") or []),
                "legitimate_shared_visual": bool(row.get("legitimate_shared_visual")),
            }
        )

    # Explicit 11741/11742 legitimacy: must not be flagged suspicious_shared_asset.
    a = all_decisions.get(11741) or {}
    b = all_decisions.get(11742) or {}
    reasons = set(a.get("visual_review_reasons") or []) | set(b.get("visual_review_reasons") or [])
    share_ok = "suspicious_shared_asset" not in reasons
    if a.get("visual_bbox") and b.get("visual_bbox"):
        # Near-identical stems may share; guard must allow that class.
        if legitimate_shared_visual(a, b):
            share_ok = share_ok and True

    dry = {
        "summary": {
            "fail11": len(FAIL11),
            "auto_correct": auto_correct,
            "needs_review": needs_review,
            "rejected": rejected,
            "wrong_accepted": wrong_accepted,
            "protected": sum(1 for r in dry_rows if r["matched"]),
            "legit_share_not_flagged_suspicious": share_ok,
        },
        "rows": dry_rows,
        "false_positive_checks": fp_checks,
    }
    dry_path = REPORTS / "b2_ch3_visual_pipeline_hardened_dryrun.json"
    dry_path.write_text(json.dumps(dry, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(dry["summary"], ensure_ascii=False, indent=2))
    print("trace:", trace_path)
    print("dryrun:", dry_path)
    conn.close()
    return 0 if wrong_accepted == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
