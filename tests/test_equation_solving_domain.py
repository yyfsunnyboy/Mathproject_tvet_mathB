# -*- coding: utf-8 -*-
"""B3 Ch2 equation.solving primitives and generator contracts."""
from __future__ import annotations

import importlib
from collections import defaultdict
from fractions import Fraction

import pytest

from core.domain.equation_solving_domain import (
    LEG_GAP_POOL,
    OPS,
    SOURCE_SPECS,
    VISUAL_UNSUPPORTED_IDS,
    build_equation_solving_matrix,
    discriminant,
    quadratic_real_roots,
    recompute_answer,
    root_count,
    solve_inequality,
    solve_linear,
    validate_equation_solving_matrix,
    vieta,
)
from core.gencode.multipart_answer_arity import (
    checker_answer_count,
    expected_answer_field_count,
    rendered_answer_field_count,
)


def test_linear_unique_and_reject_parallel():
    assert solve_linear(Fraction(2), Fraction(3), Fraction(1), Fraction(8)) == Fraction(5)
    with pytest.raises(ValueError):
        solve_linear(Fraction(2), Fraction(1), Fraction(2), Fraction(4))


def test_inequality_strict_boundary_flips_when_coefficient_negative():
    shown, boundary = solve_inequality(Fraction(-2), Fraction(1), Fraction(0), Fraction(5), ">")
    assert boundary == Fraction(-2)
    assert shown.startswith("x <") or shown.startswith("x <=")
    assert ">" not in shown.split("x", 1)[1][:3]
    inclusive, b2 = solve_inequality(Fraction(3), Fraction(0), Fraction(1), Fraction(6), ">=")
    assert b2 == Fraction(3)
    assert ">=" in inclusive


def test_quadratic_integer_roots_and_vieta():
    # (x-2)(x+3)= x^2 +x -6
    assert discriminant(Fraction(1), Fraction(1), Fraction(-6)) == 25
    assert root_count(Fraction(1), Fraction(1), Fraction(-6)) == 2
    s, p = vieta(Fraction(1), Fraction(1), Fraction(-6))
    assert s == -1 and p == -6


def test_every_supported_source_generates_and_checks():
    mods = {}
    for sid, spec in SOURCE_SPECS.items():
        mod = mods.get(spec["skill_id"])
        if mod is None:
            mod = importlib.import_module(f"skills.{spec['skill_id']}")
            mods[spec["skill_id"]] = mod
        payload = mod.generate(seed=11, component_id=f"src_{sid}")
        expected = expected_answer_field_count(payload)
        assert expected == checker_answer_count(payload) == rendered_answer_field_count(payload)
        assert expected >= 1
        assert mod.check(payload["answer"], payload["answer"], question_payload=payload)
        if payload.get("answer_type") == "single_choice":
            values = [c.get("value") for c in payload.get("choices") or []]
            assert len(values) == 4
            assert len(set(map(str, values))) == 4


def test_family_sampling_has_no_contract_failures():
    by_op = defaultdict(list)
    for sid, spec in SOURCE_SPECS.items():
        by_op[spec["op"]].append(sid)
    mods = {}
    crashes = wrong = 0
    for op, ids in by_op.items():
        sid = ids[0]
        spec = SOURCE_SPECS[sid]
        mod = mods.get(spec["skill_id"])
        if mod is None:
            mod = importlib.import_module(f"skills.{spec['skill_id']}")
            mods[spec["skill_id"]] = mod
        for seed in range(50):
            matrix = build_equation_solving_matrix(
                operation=op,
                constraints={"textbook_example_id": sid, "presentation_mode": spec["presentation"]},
                seed=seed,
            )
            assert validate_equation_solving_matrix(matrix)
            stored = (matrix.get("answer") or {}).get("canonical_form")
            assert recompute_answer(matrix) == stored
            payload = mod.generate(seed=seed, component_id=f"src_{sid}")
            if not mod.check(payload["answer"], payload["answer"], question_payload=payload):
                wrong += 1
    assert crashes == 0 and wrong == 0
    assert set(by_op) == set(OPS)
    assert not VISUAL_UNSUPPORTED_IDS
    assert 12013 in SOURCE_SPECS


def test_12013_textbook_gap_filters_negative_root():
    roots = quadratic_real_roots(Fraction(1), Fraction(-12), Fraction(-108))
    assert roots == (Fraction(-6), Fraction(18))
    matrix = build_equation_solving_matrix(
        operation="quadratic_right_triangle_side_relation",
        constraints={"textbook_example_id": 12013, "gap_d": 6},
        seed=0,
    )
    facts = matrix["validation_facts"]
    assert facts["algebraic_roots"] == ["-6", "18"]
    assert facts["valid_geometry_roots"] == ["18"]
    assert matrix["answer"]["canonical_form"] == "18"
    assert matrix["answer"]["parts"] == {}
    assert "(x+6)" in matrix["question_text"]
    assert "(x+12)" in matrix["question_text"]
    assert "18" not in matrix["question_text"].replace("(x+12)", "")
    assert recompute_answer(matrix) == "18"


def test_12013_sampling_keeps_single_positive_side():
    mod = importlib.import_module("skills.vh_數學B3_SubSection_2_2_2")
    seen_gaps = set()
    leaks = ("TODO", "FIXME", "placeholder", "DEBUG")
    for seed in range(50):
        matrix = build_equation_solving_matrix(
            operation="quadratic_right_triangle_side_relation",
            constraints={"textbook_example_id": 12013, "presentation_mode": "short_answer"},
            seed=seed,
        )
        gap = Fraction(matrix["givens"]["d"])
        assert gap in {Fraction(n) for n in LEG_GAP_POOL}
        assert gap != 6
        seen_gaps.add(gap)
        shortest = Fraction(matrix["answer"]["canonical_form"])
        longer = shortest + gap
        hypotenuse = shortest + 2 * gap
        assert shortest > 0 and longer > 0 and hypotenuse > 0
        assert shortest < longer < hypotenuse
        assert shortest ** 2 + longer ** 2 == hypotenuse ** 2
        assert shortest == 3 * gap
        algebraic = [Fraction(item) for item in matrix["validation_facts"]["algebraic_roots"]]
        assert Fraction(-gap) in algebraic
        assert matrix["validation_facts"]["valid_geometry_roots"] == [str(int(shortest))]
        assert matrix["answer"]["parts"] == {}
        assert recompute_answer(matrix) == matrix["answer"]["canonical_form"]
        assert "." not in str(matrix["answer"]["canonical_form"])
        payload = mod.generate(seed=seed, component_id="src_12013")
        assert expected_answer_field_count(payload) == 1
        assert checker_answer_count(payload) == 1
        assert rendered_answer_field_count(payload) == 1
        assert payload.get("answer_type") != "multi_part"
        assert mod.check(payload["answer"], payload["answer"], question_payload=payload)
        assert not mod.check("__WRONG__", payload["answer"], question_payload=payload)
        text = str(payload.get("question_text") or "")
        assert "兩股" in text
        assert str(int(shortest)) not in text
        blob = text.lower()
        for token in leaks:
            assert token.lower() not in blob
    assert len(seen_gaps) >= 2
