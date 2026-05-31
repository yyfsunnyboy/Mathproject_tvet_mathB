from __future__ import annotations

from unittest.mock import patch

from core.gencode.ai_semantic_classifier import set_ai_semantic_classifier_mock
from core.gencode.classification_policy import build_classified_example_feature, merge_ai_and_rule_classification
from core.gencode.main_skill_anchor import build_main_skill_anchor
from core.gencode.problem_type_induction import induce_problem_types_from_examples
from core.gencode.source_structure_context import (
    enrich_examples_with_structure_context,
    parse_metadata_from_text,
    parse_structure_fields,
)
from core.gencode.task_families import (
    DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    DIVISION_POINT_COORDINATES_FAMILY,
)


def _ex(
    ex_id: int,
    title: str,
    stem: str,
    *,
    source_description: str = "",
    source_type: str = "",
    answer: str = "(1,2)",
) -> dict:
    return {
        "id": ex_id,
        "example_id": ex_id,
        "skill_id": "mock_skill",
        "title": title,
        "source_description": source_description or title,
        "source_type": source_type,
        "problem_text": stem,
        "correct_answer": answer,
        "section_order": ex_id,
    }


def test_parser_metadata_bracket_and_kv():
    meta = parse_metadata_from_text("隨堂練習8 [source_type=in_class_practice | linked_example=例題8]")
    assert meta["source_type"] == "in_class_practice"
    assert meta["linked_example"] == "例題8"
    fields = parse_structure_fields(
        {
            "title": "隨堂練習8",
            "source_description": "隨堂練習8 [source_type=in_class_practice | linked_example=例題8]",
        }
    )
    assert fields["practice_label"] == "隨堂練習8"
    assert fields["linked_example"] == "例題8"
    assert fields["source_type"] == "in_class_practice"
    ex_fields = parse_structure_fields({"title": "例題8 [source_type=textbook_example]"})
    assert ex_fields["example_label"] == "例題8"
    assert ex_fields["source_type"] == "worked_example"


def test_enrich_linked_example_index():
    examples = [
        _ex(1, "例題1", "求 AB 中點", source_type="textbook_example"),
        _ex(
            2,
            "隨堂練習1",
            "點 P 在 AB 上，AP=2PB，求 P 坐標",
            source_description="隨堂練習1 [source_type=in_class_practice | linked_example=例題1]",
            source_type="in_class_practice",
        ),
    ]
    enriched, report = enrich_examples_with_structure_context(examples)
    practice = next(e for e in enriched if e["id"] == 2)
    ctx = practice["source_structure_context"]
    assert ctx["linked_example"] == "例題1"
    assert ctx["linked_worked_example"]["example_id"] == 1
    assert len(report["example_practice_link_map"]) == 1


def test_practice_linked_consistent_with_worked_example():
    skill_id = "mock_structure_consistent"
    examples = [
        _ex(1, "例題1", "內分點坐標示範", source_type="textbook_example"),
        _ex(
            2,
            "隨堂練習1",
            "點 P 在 AB 上，AP=2PB，求 P 坐標",
            source_description="隨堂練習1 [source_type=in_class_practice | linked_example=例題1]",
            source_type="in_class_practice",
            answer="(2,3)",
        ),
    ]

    def _mock_ai(example, anchor):
        eid = example.get("id")
        if eid == 1:
            return {
                "target_task": "compute_internal_division_point_coordinates",
                "task_family": DIVISION_POINT_COORDINATES_FAMILY,
                "confidence": 0.9,
                "evidence": ["分點坐標例題"],
            }
        return {
            "target_task": "compute_internal_division_point_coordinates",
            "task_family": DIVISION_POINT_COORDINATES_FAMILY,
            "confidence": 0.88,
            "evidence": ["AP=2PB", "求 P 坐標"],
        }

    set_ai_semantic_classifier_mock(_mock_ai)
    try:
        with patch(
            "core.gencode.problem_type_induction.load_skill_metadata_from_db",
            return_value={"skill_ch_name": "分點坐標"},
        ):
            out = induce_problem_types_from_examples(skill_id, examples)
        row = next(r for r in out["semantic_classifications"] if r["example_id"] == 2)
        assert row["structure_context_used"] is True
        assert row["structure_consistency"] == "consistent"
        assert row["final_task_family"] == DIVISION_POINT_COORDINATES_FAMILY
    finally:
        set_ai_semantic_classifier_mock(None)


def test_linked_example_structure_mismatch_warning():
    enriched, _ = enrich_examples_with_structure_context(
        [
            _ex(1, "例題1", "示範", source_type="textbook_example"),
            _ex(
                2,
                "隨堂練習1",
                "題幹",
                source_description="隨堂練習1 [source_type=in_class_practice | linked_example=例題1]",
                source_type="in_class_practice",
            ),
        ]
    )
    ex = next(e for e in enriched if e["id"] == 2)
    anchor = build_main_skill_anchor("mock", {"skill_ch_name": "分點坐標"})
    classifications_by_id = {
        1: {"final_task_family": DIVISION_POINT_COORDINATES_FAMILY},
    }
    ai = {
        "available": True,
        "target_task": "compute_distance_between_two_points",
        "task_family": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
        "confidence": 0.8,
        "evidence": [],
    }
    rule = {
        "target_task": "compute_distance_between_two_points",
        "task_family": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
        "question_text": "",
    }
    from core.gencode.classification_policy import _attach_structure_fields

    trace = _attach_structure_fields(
        merge_ai_and_rule_classification(ai, rule, anchor),
        ex,
        ai,
        classifications_by_id=classifications_by_id,
    )
    assert trace["structure_consistency"] == "mismatch"
    assert trace["requires_human_action"] is True


def test_distance_pair_consistent():
    examples = [
        _ex(1, "例題2", "求 A、B 兩點距離", source_type="textbook_example", answer="5"),
        _ex(
            2,
            "隨堂練習2",
            "求 A(1,1) 與 B(4,5) 距離",
            source_description="隨堂練習2 [source_type=in_class_practice | linked_example=例題2]",
            source_type="in_class_practice",
            answer="5",
        ),
    ]

    def _mock_ai(example, anchor):
        return {
            "target_task": "compute_distance_between_two_points",
            "task_family": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
            "confidence": 0.9,
            "evidence": ["求距離"],
        }

    set_ai_semantic_classifier_mock(_mock_ai)
    try:
        with patch(
            "core.gencode.problem_type_induction.load_skill_metadata_from_db",
            return_value={"skill_ch_name": "兩點距離"},
        ):
            out = induce_problem_types_from_examples("mock_dist", examples)
        for row in out["semantic_classifications"]:
            assert row["final_task_family"] == DISTANCE_BETWEEN_TWO_POINTS_FAMILY
    finally:
        set_ai_semantic_classifier_mock(None)


def test_possible_mixed_source_context_flag():
    enriched, _ = enrich_examples_with_structure_context(
        [
            _ex(1, "例題1", "分點題", source_type="textbook_example"),
            _ex(2, "例題2", "分點題二", source_type="textbook_example"),
            _ex(3, "例題3", "求 AB 距離", source_type="textbook_example", answer="5"),
        ]
    )
    ex = next(e for e in enriched if e["id"] == 3)
    anchor = build_main_skill_anchor("mock", {"skill_ch_name": "分點坐標"})
    classifications_by_id = {
        1: {"final_task_family": DIVISION_POINT_COORDINATES_FAMILY},
        2: {"final_task_family": DIVISION_POINT_COORDINATES_FAMILY},
    }
    ai = {
        "available": True,
        "target_task": "compute_distance_between_two_points",
        "task_family": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
        "confidence": 0.9,
        "evidence": ["求 AB 長"],
    }
    rule = {
        "target_task": "compute_distance_between_two_points",
        "task_family": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
        "question_text": "求 AB 距離",
    }
    from core.gencode.classification_policy import _attach_structure_fields

    trace = _attach_structure_fields(
        merge_ai_and_rule_classification(ai, rule, anchor),
        ex,
        ai,
        classifications_by_id=classifications_by_id,
    )
    assert trace["final_task_family"] == DISTANCE_BETWEEN_TWO_POINTS_FAMILY
    assert trace.get("possible_mixed_source_context") is True


def test_no_linked_metadata_uses_sequence_only():
    examples = [_ex(1, "例題1", "題1", source_type="textbook_example")]
    enriched, report = enrich_examples_with_structure_context(examples)
    assert enriched[0]["source_structure_context"]["linked_example"] == ""
    assert report["example_practice_link_map"] == []
    anchor = build_main_skill_anchor("mock", {"skill_ch_name": "\u5206\u9ede\u5750\u6a19"})
    feat, trace = build_classified_example_feature(
        enriched[0],
        anchor,
        spec_mode="rule_first_induce_from_sources",
    )
    assert trace.get("structure_consistency") in {"not_applicable", "unknown", ""}
