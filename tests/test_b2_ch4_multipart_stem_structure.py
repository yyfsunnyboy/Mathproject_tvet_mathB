# -*- coding: utf-8 -*-
"""Regression: B2 Ch4 structured multipart stem (five confirmed topologies)."""

from __future__ import annotations

import re

from core.domain.circle_plane_domain import build_circle_plane_matrix
from core.domain.circle_plane_gap_coverage import build_gap_matrix
from core.gencode.circle_plane_capability_adapter import adapt_circle_plane_matrix
from core.gencode.multipart_stem_contract import extract_stem_structure


def _adapt(matrix, op: str, skill: str, example_id: int = 1):
    return adapt_circle_plane_matrix(
        matrix,
        domain_operation=op,
        skill_id=skill,
        component_id="src_test",
        textbook_example_id=example_id,
    )


def _assert_stem_items(payload, *, count: int, prompt_substr: str | None = None):
    stem = extract_stem_structure(payload)
    assert stem is not None, "stem_structure missing from payload"
    items = stem.get("items") or []
    assert len(items) == count
    assert [it["group_label"] for it in items] == [f"({i})" for i in range(1, count + 1)]
    for it in items:
        assert str(it.get("text") or "").strip()
        assert "$" in str(it["text"])
    if prompt_substr:
        assert prompt_substr in str(stem.get("prompt") or "")
    # Compatibility text keeps markers on separate lines.
    q = str(payload.get("question_text") or "")
    assert "\n" in q
    for i in range(1, count + 1):
        assert re.search(rf"[\(（]\s*{i}\s*[\)）]", q)


def _part_labels(payload):
    parts = ((payload.get("answer_contract") or {}).get("parts") or [])
    return [(p.get("group_label"), p.get("display_label")) for p in parts]


def test_case1_three_circles_center_radius_multi_seed():
    for seed in (11, 21, 33):
        matrix = build_circle_plane_matrix(
            operation="identify_center_radius_from_standard", seed=seed
        )
        before = dict(matrix["answer"]["parts"])
        payload = _adapt(
            matrix,
            "identify_center_radius_from_standard",
            "vh_數學B2_SubSection_4_1_1",
        )
        _assert_stem_items(payload, count=3, prompt_substr="圓心")
        labels = _part_labels(payload)
        assert [d for _, d in labels] == ["圓心", "半徑", "圓心", "半徑", "圓心", "半徑"]
        groups = ((payload.get("answer_contract") or {}).get("ui_contract") or {}).get(
            "field_groups"
        ) or []
        assert [g["group_label"] for g in groups] == ["(1)", "(2)", "(3)"]
        # Mathematical safety: adapter must not mutate expected parts.
        after_parts = {
            p["key"]: p["expected_answer"]
            for p in (payload.get("answer_contract") or {}).get("parts") or []
        }
        assert after_parts == before


def test_case2_graph_classification_labels():
    for seed in (7, 14, 28):
        matrix = build_circle_plane_matrix(
            operation="classify_general_circle_graph", seed=seed
        )
        before = dict(matrix["answer"]["parts"])
        payload = _adapt(
            matrix,
            "classify_general_circle_graph",
            "vh_數學B2_SubSection_4_1_2",
        )
        _assert_stem_items(payload, count=3, prompt_substr="圖形")
        labels = [d for _, d in _part_labels(payload)]
        assert len(labels) == 3
        assert all("圖形" in str(d) for d in labels)
        assert not any(re.fullmatch(r"\d+", str(d).strip()) for d in labels)
        after = {
            p["key"]: p["expected_answer"]
            for p in (payload.get("answer_contract") or {}).get("parts") or []
        }
        assert after == before


def test_case3_point_vs_two_circles():
    for seed in (5, 15, 25):
        matrix = build_gap_matrix(
            operation="classify_point_vs_circles_multipart", seed=seed
        )
        before = dict(matrix["answer"]["parts"])
        payload = _adapt(
            matrix,
            "classify_point_vs_circles_multipart",
            "vh_數學B2_SubSection_4_2_1",
        )
        _assert_stem_items(payload, count=2)
        labels = [d for _, d in _part_labels(payload)]
        assert labels == ["(1) C1 關係", "(2) C2 關係"]
        after = {
            p["key"]: p["expected_answer"]
            for p in (payload.get("answer_contract") or {}).get("parts") or []
        }
        assert after == before


def test_case4_circle_vs_three_lines():
    for seed in (5, 9, 17):
        matrix = build_gap_matrix(
            operation="classify_lines_vs_circle_multipart", seed=seed
        )
        before = dict(matrix["answer"]["parts"])
        payload = _adapt(
            matrix,
            "classify_lines_vs_circle_multipart",
            "vh_數學B2_SubSection_4_2_2",
        )
        _assert_stem_items(payload, count=3)
        labels = [d for _, d in _part_labels(payload)]
        assert labels == ["(1) L1 關係", "(2) L2 關係", "(3) L3 關係"]
        after = {
            p["key"]: p["expected_answer"]
            for p in (payload.get("answer_contract") or {}).get("parts") or []
        }
        assert after == before


def test_case5_two_tangent_segment_lengths():
    for seed in (3, 8, 19, 42):
        matrix = build_gap_matrix(
            operation="compute_tangent_segment_lengths", seed=seed
        )
        before = dict(matrix["answer"]["parts"])
        payload = _adapt(
            matrix,
            "compute_tangent_segment_lengths",
            "vh_數學B2_SubSection_4_2_4",
        )
        _assert_stem_items(payload, count=2, prompt_substr="切線段長")
        labels = [d for _, d in _part_labels(payload)]
        assert labels == ["(1) 切線段長", "(2) 切線段長"]
        after = {
            p["key"]: p["expected_answer"]
            for p in (payload.get("answer_contract") or {}).get("parts") or []
        }
        assert after == before
