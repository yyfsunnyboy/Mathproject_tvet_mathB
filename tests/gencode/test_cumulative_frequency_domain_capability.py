# -*- coding: utf-8 -*-
"""Regression tests for cumulative-frequency domain capability and dispatch."""

from __future__ import annotations

import pytest

from core.domain.statistics.cumulative_frequency import (
    build_greater_than_cumulative_frequencies,
    build_less_than_cumulative_frequencies,
    read_interval_frequency_from_cumulative,
    recover_class_frequencies_from_cumulative,
    validate_cumulative_monotonicity,
)
from core.domain.statistics.frequency_distribution_domain import (
    build_cumulative_frequency_matrix,
    build_frequency_distribution_table_matrix,
)
from core.gencode.services.v3_example_semantic_classifier import (
    TextbookExampleSource,
    calculate_source_hash,
    classify_textbook_example,
)
from core.gencode.skill_fixed_domain_authority import (
    SkillFixedDomainError,
    build_classifier_taxonomy_entry,
    resolve_fixed_domain_context,
)
from core.gencode.v3_error_codes import DOMAIN_CAPABILITY_MISSING
from core.registry.taxonomy_registry import get_fixed_domain_key

SKILL_ID = "vh_數學B4_CumulativeFrequencyTablesAndGraphs"

CUMULATIVE_FIXTURES: list[tuple[int, str, str]] = [
    (
        3830,
        "已知某班數學期中考成績的以下累積次數分配折線圖如下，試問：(1)以60分為標準，不及格的人數有幾人？(2)至少70分的人數有幾人？（圖片待補）",
        "less_than_cumulative_frequency_reading",
    ),
    (
        3831,
        "試完成下方之累積次數分配表（數據略）。",
        "cumulative_frequency_table_construction",
    ),
    (
        3832,
        "已知某班英文期末考成績的以上累積次數分配折線圖如右，試問：(1)以60分為標準，不及格的人數有幾人？(2)80分以上的人數有幾人？（圖片待補）",
        "greater_than_cumulative_frequency_reading",
    ),
    (
        3833,
        "已知某班國文期中考成績的以下累積次數分配折線圖如右，試問：(1)以60分為標準，不及格的人數有幾人？(2)至少80分的人數有幾人？（圖片待補）",
        "less_than_cumulative_frequency_reading",
    ),
    (
        3834,
        "某班有40位同學，第一次期中考數學成績的次數分配表及以下累積次數分配表如下表，試求 a, b, c, d。成績：0~20(4人), 20~40(a人, 累積12), 40~60(10人, 累積b), 60~80(12人, 累積34), 80~100(c人, 累積d)。（圖片待補）",
        "class_frequency_from_cumulative_difference",
    ),
]


def _taxonomy_entry() -> dict:
    ctx = resolve_fixed_domain_context(SKILL_ID)
    return build_classifier_taxonomy_entry(ctx)


def _classify(example_id: int, problem_text: str) -> dict:
    source = TextbookExampleSource(
        skill_id=SKILL_ID,
        textbook_example_id=example_id,
        question_text=problem_text,
        answer="42",
        choices=[],
        explanation="",
        source_label="",
        source_type="",
        presentation_mode="short_answer",
        question_type="",
        source_hash=calculate_source_hash(problem_text, "42", ""),
    )
    return classify_textbook_example(source, _taxonomy_entry())


@pytest.mark.parametrize("example_id,problem_text,expected_operation", CUMULATIVE_FIXTURES)
def test_cumulative_fixtures_classify_to_domain_operations(
    example_id: int,
    problem_text: str,
    expected_operation: str,
):
    result = _classify(example_id, problem_text)
    assert result["selected_operation"] == expected_operation
    assert result["selected_operation"] != "frequency_polygon_reading"
    assert result["selected_operation"] != "frequency_table_construction_review"


def test_skill_fixed_domain_key_is_frequency_distribution():
    assert get_fixed_domain_key(SKILL_ID) == "statistics.frequency_distribution"


def test_cumulative_stem_never_matches_frequency_polygon():
    text = "已知以下累積次數分配折線圖，求不及格人數。"
    result = _classify(9999, text)
    assert result["selected_operation"] == "less_than_cumulative_frequency_reading"
    assert result["selected_operation"] != "frequency_polygon_reading"


def test_unresolved_cumulative_stem_raises_domain_capability_missing():
    source = TextbookExampleSource(
        skill_id=SKILL_ID,
        textbook_example_id=9998,
        question_text="閱讀統計資料並回答問題。",
        answer="1",
        choices=[],
        explanation="",
        source_label="",
        source_type="",
        presentation_mode="short_answer",
        question_type="",
        source_hash=calculate_source_hash("閱讀統計資料並回答問題。", "1", ""),
    )
    with pytest.raises(SkillFixedDomainError) as exc:
        classify_textbook_example(source, _taxonomy_entry())
    assert exc.value.code == DOMAIN_CAPABILITY_MISSING


def test_cumulative_domain_helpers_round_trip():
    class_freqs = [4, 8, 10, 12, 6]
    below = build_less_than_cumulative_frequencies(class_freqs)
    above = build_greater_than_cumulative_frequencies(class_freqs)
    assert validate_cumulative_monotonicity(below, direction="below")
    assert validate_cumulative_monotonicity(above, direction="above")
    assert recover_class_frequencies_from_cumulative(below, direction="below") == class_freqs
    assert read_interval_frequency_from_cumulative(below, 1, 2, direction="below") == class_freqs[2]


@pytest.mark.parametrize(
    "operation",
    [
        "cumulative_frequency_table_construction",
        "less_than_cumulative_frequency_reading",
        "greater_than_cumulative_frequency_reading",
        "class_frequency_from_cumulative_difference",
        "cumulative_frequency_graph_reading",
    ],
)
def test_cumulative_operations_build_matrix(operation: str):
    matrix = build_cumulative_frequency_matrix(seed=42, domain_operation=operation)
    assert matrix["validation_facts"]["domain_operation"] == operation
    assert matrix["visual_spec"]["type"] in {
        "cumulative_frequency_table",
        "cumulative_frequency_graph",
        "cumulative_frequency_polygon",
    }
    if operation != "cumulative_frequency_table_construction":
        assert matrix.get("image_base64")


def test_frequency_distribution_entrypoint_routes_cumulative_operations():
    matrix = build_frequency_distribution_table_matrix(
        seed=7,
        domain_operation="cumulative_frequency_table_construction",
    )
    assert matrix["validation_facts"]["domain_operation"] == "cumulative_frequency_table_construction"


def test_gated_resolve_uses_cumulative_operations_for_fixtures():
    from core.gencode.pipeline_orchestrator import _v3_resolve_gated_domain_operation

    for example_id, problem_text, expected_operation in CUMULATIVE_FIXTURES:
        selected, classification, ctx = _v3_resolve_gated_domain_operation(
            skill_id=SKILL_ID,
            textbook_row={
                "id": example_id,
                "problem_text": problem_text,
                "correct_answer": "42",
                "problem_type": "",
            },
            conn=None,
            extra={},
        )
        assert ctx.fixed_domain_key == "statistics.frequency_distribution"
        assert selected == expected_operation
        assert classification.get("problem_type_id") == expected_operation
        assert selected not in {"frequency_polygon_reading", "frequency_table_construction_review"}
