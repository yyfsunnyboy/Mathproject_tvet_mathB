from __future__ import annotations

import importlib
from types import ModuleType

from core.generator_route_resolver import resolve_generator_route, resolve_runtime_route_decision


def _module(name: str, file: str | None = None) -> ModuleType:
    mod = ModuleType(name)
    if file is not None:
        mod.__file__ = file
    return mod


def test_resolver_routes_plain_jh_skill_to_legacy() -> None:
    mod = _module(
        "skills.jh_test",
        r"D:\Python\Mathproject_tvet_mathB\skills\jh_test.py",
    )

    def generate(level=1):
        return {"question_text": "q", "answer": "1"}

    mod.generate = generate

    route = resolve_generator_route(skill_id="jh_test", loaded_module=mod)

    assert route["mode"] == "legacy"
    assert route["reason"] == "plain_jh_skill_module"
    assert route["module"] is mod


def test_resolver_routes_generator_specs_wrapper_to_modern() -> None:
    mod = _module(
        "skills.vh_test",
        r"D:\Python\Mathproject_tvet_mathB\skills\vh_test.py",
    )
    mod.GENERATOR_KEYS = ["src_1"]
    mod.GENERATOR_SPECS = [{"component_id": "src_1"}]

    def generate(level=1, seed=None, component_id=None):
        return {"question_text": "q", "answer": seed, "component_id": component_id}

    mod.generate = generate

    route = resolve_generator_route(skill_id="vh_test", loaded_module=mod)

    assert route["mode"] == "modern"
    assert route["reason"] == "existing_v3_runtime"


def test_existing_modern_route_source_wins_even_for_jh_name() -> None:
    mod = _module(
        "skills.jh_modern",
        r"D:\Python\Mathproject_tvet_mathB\skills\jh_modern.py",
    )

    def generate(level=1, seed=None):
        return {"question_text": "q", "answer": seed}

    mod.generate = generate

    route = resolve_generator_route(
        skill_id="jh_modern",
        loaded_module=mod,
        existing_route_source="gencode_wrapper",
    )

    assert route["mode"] == "modern"
    assert route["reason"] == "existing_route_source:gencode_wrapper"


def test_missing_generate_is_unavailable() -> None:
    mod = _module("skills.missing", r"D:\Python\Mathproject_tvet_mathB\skills\missing.py")

    route = resolve_generator_route(skill_id="missing", loaded_module=mod)

    assert route["mode"] == "unavailable"


def test_runtime_decision_prefers_v3_over_b4_phase7b_allowlist(monkeypatch) -> None:
    mod = _module(
        "skills.vh_b4_published",
        r"D:\Python\Mathproject_tvet_mathB\skills\vh_b4_published.py",
    )
    mod.GENERATOR_KEYS = ["src_1"]
    mod.GENERATOR_SPECS = [{"component_id": "src_1"}]

    def generate(level=1, seed=None, component_id=None):
        return {"question_text": "q", "answer": "1", "component_id": component_id}

    mod.generate = generate

    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(importlib, "import_module", lambda name: mod)

    decision = resolve_runtime_route_decision(
        skill_id="vh_b4_published",
        is_b4_phase7b_runtime_skill=True,
    )

    assert decision.mode == "v3"
    assert decision.reason == "published_v3_runtime_available"
    assert decision.module is mod
    assert decision.wrapper_loaded is True
    assert decision.legacy_fallback_used is False


def test_runtime_decision_b4_phase7b_only_when_v3_facade_missing(monkeypatch) -> None:
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)

    decision = resolve_runtime_route_decision(
        skill_id="vh_b4_legacy_only",
        is_b4_phase7b_runtime_skill=True,
    )

    assert decision.mode == "b4_phase7b"
    assert decision.reason == "b4_phase7b_legacy_available"
    assert decision.legacy_fallback_used is True
    assert decision.legacy_fallback_reason == "v3_facade_missing"


def test_runtime_decision_import_failure_is_not_missing(monkeypatch) -> None:
    def boom(name):
        raise RuntimeError("facade exploded")

    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(importlib, "import_module", boom)

    decision = resolve_runtime_route_decision(
        skill_id="vh_b4_import_failed",
        is_b4_phase7b_runtime_skill=True,
    )

    assert decision.mode == "b4_phase7b"
    assert decision.reason == "v3_facade_import_failed"
    assert decision.legacy_fallback_reason == "v3_facade_import_failed"
    assert decision.error_type == "RuntimeError"
    assert decision.error_message == "facade exploded"


def test_runtime_decision_missing_generate_is_explicit(monkeypatch) -> None:
    mod = _module(
        "skills.vh_b4_missing_generate",
        r"D:\Python\Mathproject_tvet_mathB\skills\vh_b4_missing_generate.py",
    )
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(importlib, "import_module", lambda name: mod)

    decision = resolve_runtime_route_decision(
        skill_id="vh_b4_missing_generate",
        is_b4_phase7b_runtime_skill=True,
    )

    assert decision.mode == "b4_phase7b"
    assert decision.reason == "v3_facade_missing_generate"
    assert decision.legacy_fallback_reason == "v3_facade_missing_generate"
