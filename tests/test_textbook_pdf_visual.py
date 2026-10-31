# -*- coding: utf-8 -*-
"""Tests for generic PDF visual enrichment (no B2/1-1 production hardcodes)."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.textbook_pdf_visual import (
    assign_question_regions,
    classify_and_detect_visuals,
    extract_match_phrases,
    match_questions_to_pdf,
    merge_notes_preserve_image_assets,
    normalize_pdf_text,
    pdf_text_layer_usable,
    upsert_notes_image_asset,
)


def test_normalize_and_usable_text_layer():
    assert "135c" in normalize_pdf_text("135°")
    pages = [
        {"char_count": 100},
        {"char_count": 80},
        {"char_count": 10},
    ]
    assert pdf_text_layer_usable(pages) is True
    assert pdf_text_layer_usable([{"char_count": 10}] * 5) is False


def test_extract_match_phrases_from_problem_text():
    phrases = extract_match_phrases("林媽媽製作了一個半徑為16公分的圓形披薩，並將其切成八塊。", "例2")
    assert phrases
    assert any("林媽媽" in p for p in phrases)


def test_match_questions_to_pdf_basic():
    pages = [
        {
            "page": 1,
            "width": 500,
            "height": 700,
            "norm_text": normalize_pdf_text("試將135度化為弧度"),
            "words": [],
            "images": [],
            "drawings": [],
            "char_count": 40,
        },
        {
            "page": 2,
            "width": 500,
            "height": 700,
            "norm_text": normalize_pdf_text("林媽媽製作了一個半徑為16公分的圓形披薩"),
            "words": [],
            "images": [],
            "drawings": [],
            "char_count": 40,
        },
    ]
    items = [
        {"source_description": "例1", "problem_text": "試將135度化為弧度", "source_order": 1},
        {
            "source_description": "例2",
            "problem_text": "林媽媽製作了一個半徑為16公分的圓形披薩",
            "source_order": 2,
        },
    ]
    matched = match_questions_to_pdf(items, pages)
    assert matched[0]["pdf_match"]["page"] == 1
    assert matched[1]["pdf_match"]["page"] == 2
    assert matched[0]["match_score"] >= 0.9


def _text_page(page_no: int, text: str, y: float) -> dict:
    norm = normalize_pdf_text(text)
    return {
        "page": page_no,
        "width": 500,
        "height": 700,
        "norm_text": norm,
        "words": [(80.0, y, 400.0, y + 12.0, norm)] if norm else [],
        "images": [],
        "drawings": [],
        "char_count": 40,
    }


def test_shared_phrase_consumed_by_previous_question_moves_to_next_page():
    shared = "在右圖中分別標出P,Q,R三點所在的位置"
    pages = [_text_page(1, "前言", 100), _text_page(2, shared, 300), _text_page(3, shared, 150)]
    items = [
        {"source_description": "例題2", "problem_text": shared, "source_order": 1},
        {"source_description": "隨堂練習2", "problem_text": shared, "source_order": 2},
    ]
    matched = match_questions_to_pdf(items, pages)
    assert matched[0]["pdf_match"]["page"] == 2
    assert matched[1]["pdf_match"]["page"] == 3


def test_shared_opening_keeps_distinctive_continuation_on_the_same_page():
    """A later page that only repeats the opening must not beat the real continuation."""
    opening = "袋中有5顆大小相同的球其中紅球3顆白球2顆設每球被取出的機會均等"
    example = opening + "。取一球後不放回再取一球兩球都是紅球。"
    continuation = "取一球後不放回再取一球兩球是1紅球1白球"
    practice = opening + "。" + continuation + "。"
    shared_only = "設每球被取出的機會均等求下列各事件的機率"
    pages = [
        _text_page(1, example + continuation, 120),
        _text_page(8, shared_only, 200),
    ]
    pages[0]["words"] = [
        (80.0, 120.0, 400.0, 132.0, normalize_pdf_text(example)),
        (80.0, 420.0, 400.0, 432.0, normalize_pdf_text(continuation)),
    ]
    items = [
        {"source_description": "例題9", "problem_text": example, "source_order": 1},
        {"source_description": "隨堂練習9", "problem_text": practice, "source_order": 2},
    ]
    matched = match_questions_to_pdf(items, pages)
    assert matched[0]["pdf_match"]["page"] == 1
    assert matched[1]["pdf_match"]["page"] == 1
    assert matched[1]["match_method"] == "unique_phrase+order"
    assert "1紅球1白球" in matched[1]["pdf_match"]["hits"][0]


def test_similar_wording_does_not_jump_to_the_other_question():
    first = "同時擲兩粒公正骰子觀察所出現的點數和求點數和為七的機率"
    second = "同時擲三粒公正骰子觀察所出現的點數求三粒點數均不相同的機率"
    pages = [_text_page(4, first, 180), _text_page(9, second, 200)]
    items = [
        {"source_description": "例題8", "problem_text": first, "source_order": 1},
        {"source_description": "例題10", "problem_text": second, "source_order": 2},
    ]
    matched = match_questions_to_pdf(items, pages)
    assert matched[0]["pdf_match"]["page"] == 4
    assert matched[1]["pdf_match"]["page"] == 9


def test_unique_stem_beats_a_later_shared_phrase_behind_the_previous_page():
    anchor = "前言題目用來把上一題錨在較後面的頁碼所以題幹要夠長"
    stem = "甲乙兩人各擲一粒骰子一次設A表示甲出現偶數且乙出現六點求事件A的機率"
    shared = "甲乙兩人各擲一粒骰子"
    pages = [_text_page(2, stem, 200), _text_page(6, anchor, 100), _text_page(8, shared, 180)]
    items = [
        {"source_description": "例題1", "problem_text": anchor, "source_order": 1},
        {"source_description": "例題2", "problem_text": stem, "source_order": 2},
    ]
    matched = match_questions_to_pdf(items, pages)
    assert matched[1]["pdf_match"]["page"] == 2
    assert matched[1]["match_method"] == "unique_phrase+order"


def test_latex_stem_matches_the_pdf_text_layer_not_a_short_symbol():
    stem = r"設A,B為樣本空間的兩個事件，且\(P\left(A\right)=\frac{1}{3}\)。"
    pages = [
        _text_page(3, "設AB為樣本空間的兩個事件且PA=13求補事件機率", 160),
        _text_page(7, "PA", 160),
    ]
    items = [{"source_description": "例題11", "problem_text": stem, "source_order": 1}]
    matched = match_questions_to_pdf(items, pages)
    assert matched[0]["pdf_match"]["page"] == 3
    assert matched[0]["match_method"] == "unique_phrase+order"


def test_missing_stem_stays_unmatched():
    pages = [_text_page(1, "完全無關的其他單元內容", 100), _text_page(2, "仍然沒有這一題", 100)]
    items = [{"source_description": "例題1", "problem_text": "袋中有五顆白球同時取出兩球求同色機率", "source_order": 1}]
    matched = match_questions_to_pdf(items, pages)
    assert matched[0]["pdf_match"] is None
    assert matched[0]["match_method"] == "unmatched"
    assert matched[0]["needs_review"] is True


def test_equal_shared_evidence_prefers_forward_page():
    shared = "解下列各不等式並寫出解集合"
    pages = [_text_page(1, shared, 200), _text_page(2, "林媽媽製作了一個半徑為16公分的圓形披薩", 200),
             _text_page(3, shared, 200)]
    items = [
        {"source_description": "例1", "problem_text": "林媽媽製作了一個半徑為16公分的圓形披薩", "source_order": 1},
        {"source_description": "例2", "problem_text": shared, "source_order": 2},
    ]
    matched = match_questions_to_pdf(items, pages)
    assert matched[1]["pdf_match"]["page"] == 3


def test_no_visual_when_text_only():
    pages = [
        {
            "page": 1,
            "width": 500,
            "height": 700,
            "norm_text": normalize_pdf_text("試求3加5"),
            "words": [],
            "images": [],
            "drawings": [],
            "char_count": 20,
        }
    ]
    items = [{"source_description": "例1", "problem_text": "試求3加5", "source_order": 1}]
    matched = match_questions_to_pdf(items, pages)
    matched = assign_question_regions(matched, pages)
    matched = classify_and_detect_visuals(matched, pages)
    assert matched[0]["should_mount"] is False


def test_decorative_embedded_image_without_figure_cue():
    """AI_REFERENCE policy: high-confidence owned image is kept even if photo-like."""
    pages = [
        {
            "page": 1,
            "width": 500,
            "height": 700,
            "norm_text": normalize_pdf_text("林媽媽製作了一個半徑為16公分的圓形披薩並切成八塊"),
            "words": [],
            "images": [{"bbox": [100, 200, 300, 400], "area": 40000, "xref": 1}],
            "drawings": [],
            "char_count": 40,
        }
    ]
    items = [
        {
            "source_description": "例2",
            "problem_text": "林媽媽製作了一個半徑為16公分的圓形披薩，並將其切成八塊大小一樣的扇形披薩，試求面積。",
            "source_order": 1,
        }
    ]
    matched = match_questions_to_pdf(items, pages)
    matched = assign_question_regions(matched, pages)
    matched = classify_and_detect_visuals(matched, pages)
    assert matched[0]["should_mount"] is True
    assert matched[0]["visual_classification"] == "helpful"


def test_photo_and_diagram_mounts_diagram_as_helpful():
    pages = [
        {
            "page": 1,
            "width": 500,
            "height": 700,
            "norm_text": normalize_pdf_text("爺爺收藏的古典時鐘是一個下方有鐘擺的掛鐘若鐘擺長為12公分"),
            "words": [],
            "images": [{"bbox": [320, 180, 460, 360], "area": 25000, "xref": 1}],
            "drawings": [{"bbox": [80, 200, 260, 400], "area": 36000}],
            "char_count": 50,
        }
    ]
    items = [
        {
            "source_description": "基礎題5",
            "problem_text": "爺爺收藏的古典時鐘，是一個下方有鐘擺的掛鐘，若鐘擺長為12公分，左右最大擺角各為15°，試求面積。",
            "source_order": 1,
        }
    ]
    matched = match_questions_to_pdf(items, pages)
    matched = assign_question_regions(matched, pages)
    matched = classify_and_detect_visuals(matched, pages)
    assert matched[0]["should_mount"] is True
    assert matched[0]["visual_classification"] == "helpful"


def test_required_vector_with_figure_keyword():
    pages = [
        {
            "page": 1,
            "width": 500,
            "height": 700,
            "norm_text": normalize_pdf_text("如圖所示校門口有一個半徑6公尺的圓形花圃"),
            "words": [],
            "images": [],
            "drawings": [{"bbox": [80, 220, 280, 420], "area": 40000}],
            "char_count": 40,
        }
    ]
    items = [
        {
            "source_description": "進階題9",
            "problem_text": "如圖所示：校門口有一個半徑6公尺的圓形花圃，請問扇形面積？",
            "source_order": 1,
        }
    ]
    matched = match_questions_to_pdf(items, pages)
    matched = assign_question_regions(matched, pages)
    matched = classify_and_detect_visuals(matched, pages)
    assert matched[0]["should_mount"] is True
    assert matched[0]["visual_classification"] == "required"
    assert matched[0]["visual_bbox"] is not None


def test_required_large_vector_with_figure_keyword():
    """B2 Ch3-style vector diagrams: prefer compact right-side groups over page frames."""
    pages = [
        {
            "page": 1,
            "width": 595,
            "height": 842,
            "norm_text": normalize_pdf_text("如圖為一正六邊形ABCDEF"),
            "words": [],
            "images": [],
            "drawings": [
                {"bbox": [86.0, 86.0, 523.0, 485.0], "area": 174876},  # page-ish frame
                {"bbox": [360.0, 140.0, 520.0, 300.0], "area": 25600},  # right diagram
            ],
            "char_count": 40,
        }
    ]
    items = [
        {
            "source_description": "例1",
            "problem_text": "如圖為一正六邊形ABCDEF，若向量AB=a，試求。",
            "source_order": 1,
        }
    ]
    matched = match_questions_to_pdf(items, pages)
    matched = assign_question_regions(matched, pages)
    matched = classify_and_detect_visuals(matched, pages)
    assert matched[0]["should_mount"] is True
    assert matched[0]["visual_classification"] == "required"
    assert matched[0]["visual_bbox"] is not None
    # Must prefer the compact right diagram, not the half-page frame.
    assert matched[0]["visual_bbox"][0] >= 300


def test_normalize_query_text_strips_latex_commands():
    from core.textbook_pdf_visual import normalize_query_text

    q = r"如圖，△ABC中，D、E為\({\overline{ AB }}\)的三等分點"
    n = normalize_query_text(q)
    assert "三等分點" in n
    assert "overline" not in n
    phrases = extract_match_phrases(q, "例6")
    assert any("三等分點" in p for p in phrases)



def test_low_confidence_skip():
    pages = [
        {
            "page": 1,
            "width": 500,
            "height": 700,
            "norm_text": "zzzzzzzzzzzzzzzz",
            "words": [],
            "images": [],
            "drawings": [{"bbox": [80, 220, 280, 420], "area": 40000}],
            "char_count": 40,
        }
    ]
    items = [{"source_description": "例1", "problem_text": "完全找不到的題幹內容XYZ", "source_order": 1}]
    matched = match_questions_to_pdf(items, pages)
    matched = assign_question_regions(matched, pages)
    matched = classify_and_detect_visuals(matched, pages)
    assert matched[0]["visual_classification"] == "skipped_low_confidence"
    assert matched[0]["should_mount"] is False


def test_upsert_image_asset_idempotent():
    notes = {}
    asset1 = {"asset_slot": "pdf_visual_01", "source": "pdf", "path": "uploads/a.png"}
    asset2 = {"asset_slot": "pdf_visual_01", "source": "pdf", "path": "uploads/a.png", "sha256": "x"}
    notes = upsert_notes_image_asset(notes, asset1)
    notes = upsert_notes_image_asset(notes, asset2)
    assert len(notes["image_assets"]) == 1
    assert notes["image_assets"][0]["sha256"] == "x"


def test_merge_notes_preserve_image_assets():
    existing = json.dumps(
        {"question_anchor": {"anchor_id": "a"}, "image_assets": [{"path": "uploads/x.png"}]},
        ensure_ascii=False,
    )
    incoming = json.dumps({"question_anchor": {"anchor_id": "a", "source_order": 3}}, ensure_ascii=False)
    merged = json.loads(merge_notes_preserve_image_assets(existing, incoming))
    assert merged["question_anchor"]["source_order"] == 3
    assert merged["image_assets"][0]["path"] == "uploads/x.png"


def test_pdf_failure_does_not_raise_on_missing_pdf(tmp_path):
    from core.textbook_pdf_visual import enrich_textbook_examples_with_pdf_visuals

    summary = enrich_textbook_examples_with_pdf_visuals(
        pdf_path=tmp_path / "missing.pdf",
        examples=[],
        curriculum_info={"curriculum": "vocational", "volume": "數學BX"},
        project_root=tmp_path,
        write_notes=False,
    )
    assert summary["ok"] is False or summary["warnings"]


def test_anchor_attach_all_source_types_normalized_labels():
    from core.textbook_importer_v3_pipeline import _attach_anchor_notes_to_phase3

    block_meta = {
        "例1": {
            "anchor": "例1",
            "source_type": "textbook_example",
            "problem_text": "a",
            "section_code": "1-9",
        },
        "隨堂練習1": {
            "anchor": "隨堂練習1",
            "source_type": "in_class_practice",
            "problem_text": "b",
            "section_code": "1-9",
        },
        "1-9習題 基礎題1": {
            "anchor": "1-9習題 基礎題1",
            "source_type": "textbook_exercise",
            "problem_text": "c",
            "section_code": "1-9",
        },
        "1-9習題 進階題2": {
            "anchor": "1-9習題 進階題2",
            "source_type": "advanced_exercise",
            "problem_text": "d",
            "section_code": "1-9",
        },
        "108統測B": {
            "anchor": "108統測B",
            "source_type": "exam_practice",
            "problem_text": "e",
            "section_code": "1-9",
        },
        "自我評量 題1": {
            "anchor": "自我評量 題1",
            "source_type": "self_assessment",
            "problem_text": "f",
            "section_code": "1-9",
        },
    }
    parsed = {
        "chapters": [
            {
                "sections": [
                    {
                        "concepts": [
                            {
                                "examples": [{"title": "例 1"}],
                                "practice_questions": [
                                    {"title": "隨堂練習 1"},
                                    {"title": "1-9習題 基礎題 1"},
                                    {"title": "1-9習題 進階題 2"},
                                    {"title": "108統測B"},
                                    {"title": "自我評量 題 1"},
                                ],
                            }
                        ]
                    }
                ]
            }
        ]
    }
    curriculum_info = {
        "curriculum": "vocational",
        "publisher": "longteng",
        "volume": "數學BX",
        "section_code": "1-9",
    }
    anchors, summary = _attach_anchor_notes_to_phase3(parsed, block_meta, curriculum_info)
    assert len(anchors) == 6
    assert summary["phase3_attached"] == 6
    assert summary["phase3_missing"] == 0
    for bucket in ("examples", "practice_questions"):
        for item in parsed["chapters"][0]["sections"][0]["concepts"][0][bucket]:
            notes = json.loads(item["notes"])
            assert notes["question_anchor"]["anchor_id"]
