"""Question-text typography contracts for shared coordinate generators."""

from __future__ import annotations

import re

import pytest

from agent_skills_v3 import vh_數學B1_DivisionPointCoordinates as division_skill
from core.gencode.coordinate_math_formatter import inline_math
from core.gencode.division_point_slot_engine import _gen_internal_stem
from core.gencode.midpoint_source_fidelity import (
    SOURCE_SPECS,
    generate_source_faithful_payload,
)


INLINE_MATH_RE = re.compile(r"\$([^$]+)\$")
PLAIN_COORDINATE_RE = re.compile(r"\b[A-Z]\s*\(\s*-?\d")
PLAIN_POINT_RE = re.compile(r"\b[A-Z]\b")


def _assert_inline_coordinate_typography(question_text: str) -> None:
    assert question_text
    assert "$$" not in question_text
    assert r"\[" not in question_text
    assert r"\]" not in question_text
    assert r"\(" not in question_text
    assert r"\)" not in question_text
    assert question_text.count("$") % 2 == 0

    math_spans = INLINE_MATH_RE.findall(question_text)
    assert math_spans
    plain_text = INLINE_MATH_RE.sub("", question_text)
    assert not PLAIN_COORDINATE_RE.search(plain_text), question_text
    assert not PLAIN_POINT_RE.search(plain_text), question_text


def test_shared_inline_formatter_rejects_display_or_unbalanced_delimiters() -> None:
    assert inline_math("M(0,-8)") == "$M(0,-8)$"
    assert inline_math("$M(0,-8)$") == "$M(0,-8)$"
    with pytest.raises(ValueError, match="display_math_not_allowed"):
        inline_math("$$M(0,-8)$$")
    with pytest.raises(ValueError, match="nested_or_unbalanced_inline_math"):
        inline_math("$M(0,-8)")


@pytest.mark.parametrize(
    ("variant", "expected_relation"),
    [
        ("ratio_colon_form", r"$\overline{PR}:\overline{RQ}=1:2$"),
        ("multiple_form", r"$\overline{PR}=1\overline{RQ}$"),
        ("linear_relation_form", r"$1\overline{PR}=2\overline{RQ}$"),
        ("word_context_form", r"$\overline{PQ}$"),
    ],
)
def test_each_internal_division_template_uses_inline_math(
    variant: str,
    expected_relation: str,
) -> None:
    question, _ = _gen_internal_stem(
        variant,
        ["P", "Q", "R"],
        3,
        -6,
        -24,
        21,
        -6,
        3,
        1,
        2,
    )
    _assert_inline_coordinate_typography(question)
    assert "$P(3,-6)$" in question
    assert "$Q(-24,21)$" in question
    assert expected_relation in question
    if variant != "word_context_form":
        assert "$R$ 在線段 $\\overline{PQ}$ 上" in question
        assert "求 $R$ 坐標" in question


@pytest.mark.parametrize("component_id", division_skill.GENERATOR_KEYS)
def test_all_seven_division_point_components_preserve_answer_and_checker(
    component_id: str,
) -> None:
    expected_variants = {
        "src_4423": {"direct_triangle_centroid", "worded_triangle_centroid"},
        "src_4513": {
            "linear_ratio_origin_distance_choice",
            "section_point_origin_distance_choice",
        },
    }.get(
        component_id,
        {"ratio_colon_form", "multiple_form", "linear_relation_form", "word_context_form"},
    )
    variants_seen: set[str] = set()
    for seed in range(40):
        payload = division_skill.generate(seed=seed, component_id=component_id)
        question = str(payload["question_text"])
        _assert_inline_coordinate_typography(question)
        assert PLAIN_COORDINATE_RE.search(
            INLINE_MATH_RE.sub(lambda match: match.group(1), question)
        )
        assert division_skill.check(
            payload["correct_answer"],
            payload["correct_answer"],
            payload,
        )
        variants_seen.add(
            str(payload.get("template_variant") or payload["metadata"]["template_variant"])
        )
    assert variants_seen == expected_variants


@pytest.mark.parametrize("source_id", sorted(SOURCE_SPECS))
def test_midpoint_source_routes_share_inline_coordinate_formatter(source_id: int) -> None:
    payload = generate_source_faithful_payload(source_id, seed=23)
    _assert_inline_coordinate_typography(str(payload["question_text"]))
