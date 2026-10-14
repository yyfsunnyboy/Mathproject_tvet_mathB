# -*- coding: utf-8 -*-
"""Tests for B3 Ch1 extended locked-stem families."""
from __future__ import annotations

from fractions import Fraction

import pytest

from core.domain.sequence_series_domain import build_sequence_series_matrix, validate_sequence_series_matrix
from core.domain.sequence_series_extended import (
    AP_GP_MIXED_MEAN_MIDDLE,
    ARITHMETIC_FIRST_THRESHOLD_CROSSING,
    ARITHMETIC_INDEX_AND_TOTAL_SUM,
    EXTENDED_OPS,
    GEOMETRIC_FIRST_THRESHOLD_CROSSING,
    GEOMETRIC_RATIO_FROM_PRODUCT_QUOTIENT,
    GEOMETRIC_RATIO_FROM_SHIFTED_PAIR_SUMS,
    ap_gp_mixed_mean_middle_from_x3,
    arithmetic_index_from_a1_d_an,
    first_arithmetic_index_crossing_threshold,
    first_geometric_index_crossing_threshold,
    geometric_ratio_from_product_quotient,
    geometric_ratio_from_shifted_pair_sums,
)


class TestPrimitives:
    def test_shifted_pair_sums_shift2(self):
        # textbook 11930: X=8,Y=72 → r=3
        assert geometric_ratio_from_shifted_pair_sums(8, 72, 2) == Fraction(3)
        assert geometric_ratio_from_shifted_pair_sums(6, 24, 2) == Fraction(2)

    def test_shifted_pair_sums_shift5(self):
        # a=1,r=3 → X=4, Y=3^5*4=972
        assert geometric_ratio_from_shifted_pair_sums(4, 972, 5) == Fraction(3)

    def test_product_quotient(self):
        assert geometric_ratio_from_product_quotient(81, exponent=4) == Fraction(3)
        assert geometric_ratio_from_product_quotient(16, exponent=4) == Fraction(2)

    def test_arith_index(self):
        assert arithmetic_index_from_a1_d_an(40, 2, 88) == 25

    def test_arith_threshold_boundary(self):
        # start=990, step=-20, thr=0 → after 49: 10>=0, after 50: -10<0
        assert first_arithmetic_index_crossing_threshold(990, -20, 0, compare="lt") == 50
        # exactly at threshold after k steps should not count for strict lt
        # start=100, step=-20: after 5 =0, not <0; after 6=-20
        assert first_arithmetic_index_crossing_threshold(100, -20, 0, compare="lt") == 6
        assert first_arithmetic_index_crossing_threshold(100, -20, 0, compare="le") == 5

    def test_geo_threshold_boundary(self):
        # 4^9=262144 < 1e6, 4^10=1048576 >= 1e6
        assert (
            first_geometric_index_crossing_threshold(1, 4, 1_000_000, compare="ge", power_of_index=True)
            == 10
        )
        # just above 4^9
        assert (
            first_geometric_index_crossing_threshold(1, 4, 262145, compare="ge", power_of_index=True)
            == 10
        )
        # equal to 4^9
        assert (
            first_geometric_index_crossing_threshold(1, 4, 262144, compare="ge", power_of_index=True)
            == 9
        )

    def test_ap_gp_mixed(self):
        sol = ap_gp_mixed_mean_middle_from_x3(27)
        assert sol["x2"] == Fraction(18)
        assert sol["d"] == Fraction(9)


@pytest.mark.parametrize("op", sorted(EXTENDED_OPS))
def test_extended_op_50_samples(op: str):
    crashes = 0
    invalid = 0
    for seed in range(50):
        kwargs = {}
        if op == GEOMETRIC_RATIO_FROM_SHIFTED_PAIR_SUMS and seed % 2 == 0:
            kwargs["index_shift"] = 5
        try:
            m = build_sequence_series_matrix(operation=op, seed=seed, **kwargs)
        except Exception:
            crashes += 1
            continue
        if not validate_sequence_series_matrix(m):
            invalid += 1
        assert m.get("question_text")
        assert m.get("answer")
        # locked stems should contain narrative anchors for word ops
        q = m["question_text"]
        if op == ARITHMETIC_INDEX_AND_TOTAL_SUM:
            assert "棒球場" in q and "阿民" in q
        if op == ARITHMETIC_FIRST_THRESHOLD_CROSSING:
            assert "悠遊卡" in q
        if op == GEOMETRIC_FIRST_THRESHOLD_CROSSING:
            assert "傳染" in q
    assert crashes == 0
    assert invalid == 0


def test_threshold_off_by_one_matrix_consistency():
    m = build_sequence_series_matrix(
        operation=ARITHMETIC_FIRST_THRESHOLD_CROSSING,
        seed=0,
        k=48,
        cost=20,
    )
    g = m["givens"]
    k = first_arithmetic_index_crossing_threshold(
        g["start"], g["step"], g["threshold"], compare="lt"
    )
    assert str(k) == str(m["answer"]["canonical_form"])
    # previous step not yet negative
    start = Fraction(str(g["start"]))
    step = Fraction(str(g["step"]))
    assert start + (k - 1) * step >= 0
    assert start + k * step < 0


def test_infection_rounds_recompute():
    m = build_sequence_series_matrix(
        operation=GEOMETRIC_FIRST_THRESHOLD_CROSSING,
        seed=1,
        r=4,
        k=10,
        threshold=1_000_000,
    )
    g = m["givens"]
    k = first_geometric_index_crossing_threshold(
        g["a1"], g["r"], g["threshold"], compare="ge", power_of_index=True
    )
    assert k == int(m["answer"]["canonical_form"])
