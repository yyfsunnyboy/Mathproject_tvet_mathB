# -*- coding: utf-8 -*-
"""50-sample smoke per B3 sequence/series family (domain matrix level)."""
from __future__ import annotations

import pytest

from core.domain.sequence_series_domain import (
    OPS,
    build_sequence_series_matrix,
    validate_sequence_series_matrix,
)
from core.gencode.sequence_series_capability_adapter import adapt_sequence_series_matrix
from core.registry.domain_operation_registry import (
    list_registered_domains,
    operation_is_registered,
)

# Phase-1 representative families (full OPS covered lightly; deep sample on core)
_CORE_SAMPLE_OPS = (
    "arithmetic_nth_from_a1_d",
    "arithmetic_from_two_terms",
    "arithmetic_series_sum_given",
    "arithmetic_series_recover_param",
    "geometric_nth_from_a1_r",
    "geometric_from_two_terms",
    "geometric_series_sum_given",
    "geometric_series_recover_param",
    "expand_general_term_first_n",
)


@pytest.mark.parametrize("op", sorted(OPS))
def test_operation_registered(op: str):
    assert "sequence.series" in list_registered_domains()
    assert operation_is_registered("sequence.series", op)


@pytest.mark.parametrize("op", _CORE_SAMPLE_OPS)
def test_50_sample_core_family(op: str):
    crashes = 0
    invalid = 0
    empty_q = 0
    for seed in range(50):
        try:
            matrix = build_sequence_series_matrix(operation=op, seed=seed)
        except Exception:
            crashes += 1
            continue
        if not validate_sequence_series_matrix(matrix):
            invalid += 1
            continue
        if not str(matrix.get("question_text") or "").strip():
            empty_q += 1
            continue
        # Adapter must accept
        payload = adapt_sequence_series_matrix(matrix, domain_operation=op)
        assert payload.get("question_text") or payload.get("problem_text")
        ans = payload.get("answer")
        assert ans not in (None, "", [], {})
        # Shell answer is always a structured dict after adapter
        if isinstance(ans, dict):
            assert ans.get("canonical_form") not in (None, "") or ans.get("parts") or ans.get("value") not in (None, "")
    assert crashes == 0
    assert invalid == 0
    assert empty_q == 0


@pytest.mark.parametrize("op", sorted(set(OPS) - set(_CORE_SAMPLE_OPS)))
def test_10_sample_remaining_family(op: str):
    for seed in range(10):
        matrix = build_sequence_series_matrix(operation=op, seed=seed)
        assert validate_sequence_series_matrix(matrix)
        adapt_sequence_series_matrix(matrix, domain_operation=op)
