# -*- coding: utf-8 -*-
"""Backward-compatible import path; component now lives under PointAndLine."""

from __future__ import annotations

from tests.test_src_4584_point_line_distance_mapping import (
    test_src_4584_all_parameter_pool_variants_are_valid,
    test_src_4584_is_bound_to_point_line_skill_only,
    test_src_4584_reported_cases_are_in_family_pool,
    test_src_4584_seed_samples_cover_reported_isomorphs,
)

__all__ = [
    "test_src_4584_is_bound_to_point_line_skill_only",
    "test_src_4584_reported_cases_are_in_family_pool",
    "test_src_4584_all_parameter_pool_variants_are_valid",
    "test_src_4584_seed_samples_cover_reported_isomorphs",
]
