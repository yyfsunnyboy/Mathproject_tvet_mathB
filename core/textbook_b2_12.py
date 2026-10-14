"""Audited PDF visual regions for the B2 1-2 textbook source."""

from __future__ import annotations

import hashlib
from pathlib import Path

from core.textbook_question_anchor import normalize_question_label


SOURCE_STEM = "第一章 1-2 銳角三角函數-課本"
B2_12_PDF_SHA256 = "d523b32fed50ed8215786b1e9d059365741f8d432d9bf99570ed699a6baae05e"

# Coordinates are PDF points on 1-based physical pages.  A row may own more
# than one crop when its worked example continues onto the next page.
PDF_VISUAL_REGIONS = {
    "例2": {
        "question_regions": [(6, [36.0, 315.0, 573.0, 595.0])],
        "crops": [(6, [370.0, 392.0, 515.0, 485.0], "helpful", "solution_diagram")],
    },
    "隨堂練習2": {
        "question_regions": [(6, [36.0, 595.0, 573.0, 736.0])],
        "crops": [(6, [125.0, 655.0, 445.0, 725.0], "required", "question_diagram")],
    },
    "例3": {
        "question_regions": [(7, [36.0, 168.0, 573.0, 500.0])],
        "crops": [(7, [370.0, 255.0, 505.0, 355.0], "helpful", "solution_diagram")],
    },
    "例4": {
        "question_regions": [(9, [36.0, 85.0, 573.0, 490.0])],
        "crops": [(9, [140.0, 195.0, 470.0, 315.0], "helpful", "solution_diagram")],
    },
    "例6": {
        "question_regions": [
            (11, [36.0, 500.0, 573.0, 793.0]),
            (12, [36.0, 72.0, 573.0, 347.0]),
        ],
        "crops": [
            (11, [410.0, 570.0, 510.0, 742.0], "helpful", "calculator_workflow"),
            (12, [405.0, 78.0, 505.0, 250.0], "helpful", "calculator_workflow"),
        ],
    },
}


def is_b2_12(info):
    info = info or {}
    name = str(info.get("parse_filename") or info.get("original_filename") or "")
    stem = Path(name).stem
    return (
        info.get("curriculum") == "vocational"
        and info.get("volume") == "數學B2"
        and info.get("section_code") == "1-2"
        and info.get("source_scope", "section_textbook") == "section_textbook"
        and stem in (SOURCE_STEM, SOURCE_STEM + "_Latex", SOURCE_STEM + "_latex")
    )


def correct_pdf_visual_regions(matches, pages, pdf_path, info):
    """Apply reviewed crop ownership only to the exact audited PDF edition."""
    if not is_b2_12(info):
        return matches
    if hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest() != B2_12_PDF_SHA256:
        return matches

    for row in matches:
        label = normalize_question_label(row.get("source_description", ""))
        correction = PDF_VISUAL_REGIONS.get(label)
        if correction is None:
            continue
        regions = [
            {"page": page, "bbox": list(bbox)}
            for page, bbox in correction["question_regions"]
        ]
        crops = [
            {
                "page": page,
                "bbox": list(bbox),
                "classification": classification,
                "visual_type": visual_type,
            }
            for page, bbox, classification, visual_type in correction["crops"]
        ]
        first = crops[0]
        question_bbox = regions[0]["bbox"]
        row.update(
            pdf_match={
                "page": regions[0]["page"],
                "question_start_y": question_bbox[1],
                "question_bbox": question_bbox,
                "regions": regions,
            },
            match_score=1.0,
            match_method="audited_B2_1-2_pdf_sha256",
            regions=regions,
            question_bbox=question_bbox,
            cross_page_suspected=len(regions) > 1,
            visual_page=first["page"],
            visual_bbox=first["bbox"],
            visual_crops=crops,
            should_mount=True,
            needs_review=False,
            visual_type=first["visual_type"],
            visual_classification=(
                "required"
                if any(c["classification"] == "required" for c in crops)
                else "helpful"
            ),
            visual_reason="audited_B2_1-2_source_visual",
        )
    return matches
