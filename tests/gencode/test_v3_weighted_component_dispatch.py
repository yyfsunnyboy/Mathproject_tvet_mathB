# -*- coding: utf-8 -*-
"""Tests for weighted component dispatch in compiled V3 skill router."""

from __future__ import annotations

import importlib.util
from types import SimpleNamespace
from pathlib import Path

from core.gencode.skill_wrapper_compiler import _render_new_house_init_py


from types import SimpleNamespace


def _load_generated_router(source: str):
    module = SimpleNamespace()
    namespace = module.__dict__
    namespace["__name__"] = "v3_weighted_router_test"
    namespace["__file__"] = "generated_router.py"
    exec(source, namespace)
    return module


def test_weighted_choice_prefers_heavier_component():
    generator_keys = ["src_a", "src_b"]
    generator_specs = [
        {
            "textbook_example_id": 1,
            "component_id": "src_a",
            "generator_key": "src_a",
            "display_order": 1,
            "source_order": 1,
            "sampling_weight": 1,
        },
        {
            "textbook_example_id": 2,
            "component_id": "src_b",
            "generator_key": "src_b",
            "display_order": 2,
            "source_order": 2,
            "sampling_weight": 99,
        },
    ]
    source = _render_new_house_init_py(
        skill_id="skill_weight_test",
        generator_keys=generator_keys,
        generator_specs=generator_specs,
    )
    module = _load_generated_router(source)
    picks = [module._pick_component_id(seed=seed) for seed in range(20)]
    assert picks.count("src_b") > picks.count("src_a")


def test_specs_without_weight_still_dispatch():
    generator_keys = ["src_only"]
    generator_specs = [
        {
            "textbook_example_id": 9,
            "component_id": "src_only",
            "generator_key": "src_only",
        }
    ]
    source = _render_new_house_init_py(
        skill_id="skill_default_weight",
        generator_keys=generator_keys,
        generator_specs=generator_specs,
    )
    module = _load_generated_router(source)
    assert module._pick_component_id(seed=7) == "src_only"
    assert module._pick_component_id(seed=None) == "src_only"
