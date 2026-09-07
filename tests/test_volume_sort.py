# -*- coding: utf-8 -*-
"""Regression tests for volume sort key used in get_volumes_by_curriculum."""

from core.utils import _volume_sort_key


def test_volume_sort_b3_before_b4():
    result = sorted(["數學B4", "數學B3"], key=_volume_sort_key)
    assert result == ["數學B3", "數學B4"]


def test_volume_sort_mixed_order():
    result = sorted(["數學B2", "數學B1", "數學B4", "數學B3"], key=_volume_sort_key)
    assert result == ["數學B1", "數學B2", "數學B3", "數學B4"]


def test_volume_sort_b1_through_b6():
    vols = ["數學B6", "數學B3", "數學B1", "數學B5", "數學B2", "數學B4"]
    assert sorted(vols, key=_volume_sort_key) == [
        "數學B1", "數學B2", "數學B3", "數學B4", "數學B5", "數學B6"
    ]


def test_volume_sort_does_not_mix_chapter_indices():
    """Ensure B9 < B10 (numeric, not lexicographic)."""
    result = sorted(["數學B10", "數學B9"], key=_volume_sort_key)
    assert result == ["數學B9", "數學B10"]
