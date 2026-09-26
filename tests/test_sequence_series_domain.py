# -*- coding: utf-8 -*-
"""Unit tests for B3 sequence/series domain primitives + matrix smoke."""
from __future__ import annotations

from fractions import Fraction

import pytest
import sympy as sp

from core.domain.sequence_series_domain import (
    ARITHMETIC_FROM_TWO_TERMS,
    ARITHMETIC_NTH_FROM_A1_D,
    EXPAND_GENERAL_TERM_FIRST_N,
    GEOMETRIC_NTH_FROM_A1_R,
    GEOMETRIC_SERIES_SUM_GIVEN,
    OPS,
    arithmetic_diff_from_two,
    arithmetic_inserted_sum,
    arithmetic_inserted_term,
    arithmetic_mean,
    arithmetic_nth,
    arithmetic_partial_sum,
    arithmetic_recover_a1_from_sum,
    arithmetic_recover_d_from_sum,
    arithmetic_term_from_two,
    arithmetic_total_from_odd_mid,
    build_sequence_series_matrix,
    expand_first_terms,
    geometric_means,
    geometric_nth,
    geometric_partial_sum,
    geometric_ratio_from_two,
    geometric_recover_a1_from_sum,
    geometric_recover_n_from_sum,
    geometric_term_from_two,
    solve_linear_arithmetic_mean,
    sum_multiples_in_range,
    validate_sequence_series_matrix,
)


class TestArithmeticPrimitives:
    def test_nth_normal(self):
        assert arithmetic_nth(-10, 5, 10) == Fraction(35)

    def test_nth_negative_d(self):
        assert arithmetic_nth(12, -4, 14) == Fraction(-40)

    def test_nth_fraction(self):
        assert arithmetic_nth(Fraction(1, 2), Fraction(1, 3), 4) == Fraction(1, 2) + Fraction(1)

    def test_nth_invalid_n(self):
        with pytest.raises(ValueError):
            arithmetic_nth(1, 1, 0)

    def test_diff_from_two_roundtrip(self):
        a1, d, i, j = Fraction(-2), Fraction(-3), 3, 8
        ai = arithmetic_nth(a1, d, i)
        aj = arithmetic_nth(a1, d, j)
        assert arithmetic_diff_from_two(ai, i, aj, j) == d
        assert arithmetic_term_from_two(ai, i, aj, j, 15) == arithmetic_nth(a1, d, 15)

    def test_insert_term_and_sum(self):
        # -2 .. 22 insert 5 → 7 terms, d=4; 3rd inserted = -2+3*4=10
        assert arithmetic_inserted_term(-2, 22, 5, 3) == Fraction(10)
        # sum of 5 inserted = 5*(-2) + 5*(22-(-2))/2 = -10 + 60 = 50
        assert arithmetic_inserted_sum(-2, 22, 5) == Fraction(50)

    def test_mean_and_solve(self):
        assert arithmetic_mean(4, 10) == Fraction(7)
        # (x+2) and (-2x+5), mean 10 → ( -x + 7 )/2 = 10 → -x+7=20 → x=-13
        assert solve_linear_arithmetic_mean(1, 2, -2, 5, 10) == Fraction(-13)

    def test_partial_sum_roundtrip(self):
        # Textbook: a1=5, Sn=365, n=10 → d=8
        a1, d, n = Fraction(5), Fraction(8), 10
        sn = arithmetic_partial_sum(a1, d, n)
        assert sn == Fraction(410)  # 10/2*(10+72)=410; 365 uses d=7 in another item
        assert arithmetic_partial_sum(5, 7, 10) == Fraction(365)
        assert arithmetic_recover_d_from_sum(sn, a1, n) == d
        assert arithmetic_recover_a1_from_sum(sn, d, n) == a1

    def test_sum_multiples(self):
        # 4+8+...+152
        assert sum_multiples_in_range(1, 153, 4) == arithmetic_partial_sum(4, 4, 38)

    def test_odd_mid_total(self):
        assert arithmetic_total_from_odd_mid(88, 11) == Fraction(968)

    def test_expand_first_terms(self):
        terms = expand_first_terms("2*n+1", 3)
        assert [int(sp.Integer(sp.simplify(t))) for t in terms] == [3, 5, 7]


class TestGeometricPrimitives:
    def test_nth(self):
        assert geometric_nth(3, -2, 6) == sp.Integer(3 * ((-2) ** 5))

    def test_ratio_roundtrip(self):
        a1, r, n = Fraction(3), Fraction(-2), 6
        an = geometric_nth(a1, r, n)
        assert geometric_ratio_from_two(a1, 1, an, n) == sp.Integer(-2)

    def test_term_from_two(self):
        # a3=128, a6=16 → r=1/2, a9=2
        assert geometric_term_from_two(128, 3, 16, 6, 9) == sp.Integer(2)

    def test_means(self):
        pos, neg = geometric_means(4, 25)
        assert pos == sp.Integer(10)
        assert neg == sp.Integer(-10)

    def test_means_negative_product(self):
        with pytest.raises(ValueError):
            geometric_means(-4, 25)

    def test_partial_sum_r_not_1(self):
        sn = geometric_partial_sum(-2, Fraction(-1, 2), 8)
        # manual: a=-2,r=-1/2
        expected = sp.simplify(sp.sympify(-2) * (1 - (sp.Rational(-1, 2) ** 8)) / (1 - sp.Rational(-1, 2)))
        assert sp.simplify(sn - expected) == 0

    def test_partial_sum_r_eq_1(self):
        assert geometric_partial_sum(5, 1, 10) == sp.Integer(50)

    def test_recover_n_and_a1(self):
        a1, r, n = Fraction(2), Fraction(5), 5
        sn = geometric_partial_sum(a1, r, n)
        assert geometric_recover_n_from_sum(sn, a1, r) == 5
        assert geometric_recover_a1_from_sum(sn, r, n) == sp.Integer(2)

    def test_zero_first_invalid_ratio(self):
        with pytest.raises(ValueError):
            geometric_ratio_from_two(0, 1, 2, 3)


class TestMatrixBuilder:
    @pytest.mark.parametrize("op", sorted(OPS))
    def test_each_op_builds_valid_matrix(self, op: str):
        matrix = build_sequence_series_matrix(operation=op, seed=42)
        assert validate_sequence_series_matrix(matrix)
        assert matrix["operation"] == op
        assert matrix["question_text"].strip()
        assert matrix["answer"] not in (None, "", [], {})

    def test_seed_reproducible(self):
        a = build_sequence_series_matrix(operation=ARITHMETIC_NTH_FROM_A1_D, seed=7)
        b = build_sequence_series_matrix(operation=ARITHMETIC_NTH_FROM_A1_D, seed=7)
        assert a["answer"] == b["answer"]
        assert a["question_text"] == b["question_text"]

    def test_multipart_two_terms(self):
        m = build_sequence_series_matrix(
            operation=ARITHMETIC_FROM_TWO_TERMS,
            seed=1,
            ai=-2,
            i=3,
            d=-3,
            j=8,
            k=15,
        )
        assert m["answer_type"] == "multi_part"
        assert m["stem_structure"]["items"]
        assert m["answer"]["parts"]["(1)"] == "-3"
        # a15 from a3=-2, d=-3 → -2 + 12*(-3) = -38
        assert m["answer"]["parts"]["(2)"] == "-38"

    def test_expand_multipart(self):
        m = build_sequence_series_matrix(
            operation=EXPAND_GENERAL_TERM_FIRST_N,
            seed=0,
            formulas=["2*n+1", "1/(n*(n+1))"],
            n=3,
        )
        assert "(1)" in m["answer"]["parts"]
        assert "(2)" in m["answer"]["parts"]

    def test_geo_sum_matrix(self):
        m = build_sequence_series_matrix(
            operation=GEOMETRIC_SERIES_SUM_GIVEN,
            seed=3,
            a1=2,
            r=-2,
            n=10,
        )
        expected = geometric_partial_sum(2, -2, 10)
        assert m["answer"]["canonical_form"] == canonical_from(expected)


def canonical_from(value):
    from core.domain.sequence_series_domain import canonical_exact

    return canonical_exact(value)
