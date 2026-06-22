# -*- coding: utf-8 -*-
"""Tests for canonical SOURCE_KIND resolution."""

from __future__ import annotations

from core.gencode.source_kind_resolver import (
    resolve_order_weight,
    resolve_source_kind_from_textbook_row,
)


def test_source_kind_from_source_description_not_component_id():
    assert resolve_source_kind_from_textbook_row({"source_description": "例題 3"}) == "example"
    assert resolve_source_kind_from_textbook_row({"source_description": "隨堂測驗 2"}) == "quiz"
    assert resolve_source_kind_from_textbook_row({"source_description": "自我評量"}) == "test"


def test_order_weight_from_source_kind_not_component_id_prefix():
    assert resolve_order_weight("example") == 10
    assert resolve_order_weight("quiz") == 20
    assert resolve_order_weight("test") == 30
