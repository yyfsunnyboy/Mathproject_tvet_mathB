# -*- coding: utf-8 -*-
"""Production V3 facade for vh_數學B4_NormalDistributionAndEmpiricalRule.

This wrapper file is the ONLY artefact required to switch the student runtime
from legacy to V3.  The resolver (core/generator_route_resolver.py) looks for
``skills.<skill_id>`` and requires a callable ``generate`` whose containing
module exports ``GENERATOR_SPECS`` / ``GENERATOR_KEYS``.

Components verified 2026-06-27 (6/6):
    src_3856  empirical_rule_population_count  multi_blank (3 blanks)
    src_3857  empirical_rule_population_count  multi_blank (3 blanks)
    src_3858  empirical_rule_population_count  multi_blank (2 blanks)
    src_3859  compare_distribution_spread      single_choice (image 31KB)
    src_3897  empirical_rule_population_count  single_choice answer=C
    src_3898  empirical_rule_population_count  single_choice answer=D
"""
from __future__ import annotations
from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import (
    dispatch_check,
    dispatch_generate,
    dispatch_get_hint,
)

SKILL_ID = "vh_數學B4_NormalDistributionAndEmpiricalRule"

GENERATOR_KEYS = [
    "src_3856",
    "src_3857",
    "src_3858",
    "src_3859",
    "src_3897",
    "src_3898",
]

GENERATOR_SPECS = [
    {
        "textbook_example_id": 3856,
        "component_id": "src_3856",
        "generator_key": "src_3856",
        "presentation_mode": "multi_blank",
        "response_mode": "multi_blank",
        "interaction_type": "multi_blank",
        "source_kind": "example",
        "line_type": "empirical_rule_population_count",
        "answer_type": "multi_part",
        "answer_value_type": "multi_part",
        "problem_type_id": "empirical_rule_population_count",
        "display_order": 3856,
        "source_order": 3856,
        "sampling_weight": 10.0,
    },
    {
        "textbook_example_id": 3857,
        "component_id": "src_3857",
        "generator_key": "src_3857",
        "presentation_mode": "multi_blank",
        "response_mode": "multi_blank",
        "interaction_type": "multi_blank",
        "source_kind": "quiz",
        "line_type": "empirical_rule_population_count",
        "answer_type": "multi_part",
        "answer_value_type": "multi_part",
        "problem_type_id": "empirical_rule_population_count",
        "display_order": 3857,
        "source_order": 3857,
        "sampling_weight": 10.0,
    },
    {
        "textbook_example_id": 3858,
        "component_id": "src_3858",
        "generator_key": "src_3858",
        "presentation_mode": "multi_blank",
        "response_mode": "multi_blank",
        "interaction_type": "multi_blank",
        "source_kind": "example",
        "line_type": "empirical_rule_population_count",
        "answer_type": "multi_part",
        "answer_value_type": "multi_part",
        "problem_type_id": "empirical_rule_population_count",
        "display_order": 3858,
        "source_order": 3858,
        "sampling_weight": 10.0,
    },
    {
        "textbook_example_id": 3859,
        "component_id": "src_3859",
        "generator_key": "src_3859",
        "presentation_mode": "single_choice",
        "response_mode": "single_choice",
        "interaction_type": "single_choice",
        "source_kind": "example",
        "line_type": "compare_distribution_spread",
        "answer_type": "choice_label",
        "answer_value_type": "choice_label",
        "problem_type_id": "compare_distribution_spread",
        "display_order": 3859,
        "source_order": 3859,
        "sampling_weight": 10.0,
    },
    {
        "textbook_example_id": 3897,
        "component_id": "src_3897",
        "generator_key": "src_3897",
        "presentation_mode": "single_choice",
        "response_mode": "single_choice",
        "interaction_type": "single_choice",
        "source_kind": "test",
        "line_type": "empirical_rule_population_count",
        "answer_type": "choice_label",
        "answer_value_type": "choice_label",
        "problem_type_id": "empirical_rule_population_count",
        "display_order": 3897,
        "source_order": 3897,
        "sampling_weight": 10.0,
    },
    {
        "textbook_example_id": 3898,
        "component_id": "src_3898",
        "generator_key": "src_3898",
        "presentation_mode": "single_choice",
        "response_mode": "single_choice",
        "interaction_type": "single_choice",
        "source_kind": "test",
        "line_type": "empirical_rule_population_count",
        "answer_type": "choice_label",
        "answer_value_type": "choice_label",
        "problem_type_id": "empirical_rule_population_count",
        "display_order": 3898,
        "source_order": 3898,
        "sampling_weight": 10.0,
    },
]


def _resolve_v3_package_root() -> str:
    """Resolve V3 house root: skills/ -> <project_root>/agent_skills_v3."""
    return str((Path(__file__).resolve().parent.parent / "agent_skills_v3").resolve())


def generate(
    level: int = 1,
    seed: int | None = None,
    difficulty: int | str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    return dispatch_generate(
        SKILL_ID,
        GENERATOR_KEYS,
        GENERATOR_SPECS,
        v3_package_root=_resolve_v3_package_root(),
        level=level,
        seed=seed,
        difficulty=difficulty,
        **kwargs,
    )


def check(
    user_answer: Any,
    correct_answer: Any,
    question_payload: dict[str, Any] | None = None,
) -> Any:
    return dispatch_check(
        user_answer,
        correct_answer,
        question_payload=question_payload,
        v3_package_root=_resolve_v3_package_root(),
        skill_id=SKILL_ID,
    )


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return dispatch_get_hint(
        step,
        question_payload=question_payload,
        v3_package_root=_resolve_v3_package_root(),
        skill_id=SKILL_ID,
    )
