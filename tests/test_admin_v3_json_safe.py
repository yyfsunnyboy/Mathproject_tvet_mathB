# -*- coding: utf-8 -*-
"""Tests for the admin V3 JSON-safe serializer used by import progress API."""

from __future__ import annotations

from app import create_app
from core.routes.admin import _admin_v3_json_safe


def _with_app_context(fn):
    app = create_app()
    with app.app_context():
        return fn()


def test_admin_v3_json_safe_handles_circular_reference():
    def run():
        a = {}
        a["self"] = a
        result = _admin_v3_json_safe(a)
        assert isinstance(result, dict)
        assert result["self"] == "[Circular Reference]"

    _with_app_context(run)


def test_admin_v3_json_safe_allows_shared_references():
    def run():
        shared = {"x": 1}
        payload = {"a": shared, "b": shared}
        result = _admin_v3_json_safe(payload)
        assert result["a"] == {"x": 1}
        assert result["b"] == {"x": 1}
        assert result["a"] != "[Circular Reference]"
        assert result["b"] != "[Circular Reference]"

    _with_app_context(run)


def test_admin_v3_json_safe_handles_deeply_nested_structure():
    def run():
        payload = {"level": 0, "child": None}
        current = payload
        for i in range(1, 110):
            current["child"] = {"level": i, "child": None}
            current = current["child"]
        result = _admin_v3_json_safe(payload)
        assert isinstance(result, dict)

    _with_app_context(run)


def test_admin_v3_json_safe_handles_basic_types():
    def run():
        from datetime import datetime
        from pathlib import Path

        payload = {
            "none": None,
            "bool": True,
            "int": 42,
            "float": 3.14,
            "str": "hello",
            "datetime": datetime(2026, 9, 3, 12, 0, 0),
            "path": Path("/tmp/test"),
            "bytes_utf8": b"utf8",
            "bytearray": bytearray(b"ba"),
        }
        result = _admin_v3_json_safe(payload)
        assert result["none"] is None
        assert result["bool"] is True
        assert result["int"] == 42
        assert result["float"] == 3.14
        assert result["str"] == "hello"
        assert result["datetime"] == "2026-09-03T12:00:00"
        assert result["path"] == str(Path("/tmp/test"))
        assert result["bytes_utf8"] == "utf8"
        assert result["bytearray"] == "ba"

    _with_app_context(run)
