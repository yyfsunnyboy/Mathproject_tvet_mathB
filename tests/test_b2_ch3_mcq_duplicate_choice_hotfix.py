# -*- coding: utf-8 -*-
"""Regression: vector MCQ choices must be semantically distinct without technical suffixes."""

from __future__ import annotations

import re

from core.domain.vector_plane_domain import build_vector_plane_matrix
from core.gencode.choice_contract_validator import (
    choice_semantic_key,
    has_technical_choice_suffix,
    validate_vocational_multiple_choice,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload


def _choice_texts(payload: dict) -> list[str]:
    return [str(c.get("text") or c.get("value") or "") for c in (payload.get("choices") or [])]


def test_scaled_direction_mcq_no_technical_suffix_or_duplicates():
    matrix = build_vector_plane_matrix(
        operation="compute_scaled_direction_vector",
        seed=1,
        vector=[6, 0],
        length=5,
        direction="opposite",
    )
    assert matrix["answer"]["value"] == "(-5, 0)"
    assert len(matrix.get("distractors") or []) >= 3
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode="single_choice",
        answer_type="choice",
        problem_type_id="compute_scaled_direction_vector",
        domain_operation="compute_scaled_direction_vector",
        seed=1,
        curriculum_profile="vocational_high_b",
    )
    texts = _choice_texts(payload)
    assert len(texts) == 4
    assert not any(has_technical_choice_suffix(t) for t in texts)
    assert not any(re.search(r"_+\d+", t) for t in texts)
    keys = [choice_semantic_key(t) for t in texts]
    assert len(set(keys)) == 4
    correct = "(-5, 0)"
    matches = [t for t in texts if choice_semantic_key(t) == choice_semantic_key(correct)]
    assert len(matches) == 1
    assert payload.get("answer") in {"A", "B", "C", "D"}
    # Pedagogical distinctness: wrong direction / wrong magnitude present.
    blob = " ".join(texts)
    assert "(5, 0)" in blob or "(5,0)" in blob.replace(" ", "")
    assert "(6, 0)" in blob or "(-6, 0)" in blob


def test_build_choice_options_rejects_technical_suffix_path():
    from core.gencode.domain_matrix_adapter import _build_choice_options

    choices, label = _build_choice_options(
        "(-5, 0)",
        ["(-5, 0)", "(-5,0)", "(-5, 0)_1"],  # duplicates / suffix junk
        seed_text="vector|(-5, 0)",
        allow_technical_suffix=False,
    )
    texts = [c["text"] for c in choices]
    assert len(texts) == 4
    assert not any(has_technical_choice_suffix(t) for t in texts)
    assert len({choice_semantic_key(t) for t in texts}) == 4
    assert label in {"A", "B", "C", "D"}


def test_vocational_validator_flags_suffix_and_semantic_dup():
    bad = {
        "answer_type": "single_choice",
        "curriculum_profile": "vocational_high_b",
        "choices": [
            {"label": "A", "text": "(-5, 0)", "value": "(-5, 0)"},
            {"label": "B", "text": "(-5, 0)_1", "value": "(-5, 0)_1"},
            {"label": "C", "text": "(-5,0)", "value": "(-5,0)"},
            {"label": "D", "text": "(5, 0)", "value": "(5, 0)"},
        ],
        "answer": "A",
        "canonical_answer": "(-5, 0)",
    }
    errors = validate_vocational_multiple_choice(bad, skill_id="vh_數學B2_SubSection_3_2_6")
    assert "vocational_choice_technical_suffix" in errors or "vocational_choice_semantic_duplicate" in errors


def test_all_b2_ch3_runtime_mcq_families_clean():
    import importlib
    from collections import defaultdict

    skills = [
        f"vh_數學B2_SubSection_3_{a}_{b}"
        for a, bs in [(1, range(1, 5)), (2, range(1, 7)), (3, range(1, 6))]
        for b in bs
    ]
    families = defaultdict(list)
    for skill in skills:
        mod = importlib.import_module(f"skills.{skill}")
        for spec in getattr(mod, "GENERATOR_SPECS", []):
            if str(spec.get("presentation_mode") or "") == "single_choice" or "mcq" in str(
                spec.get("problem_type_id") or ""
            ).lower():
                families[str(spec.get("problem_type_id"))].append(
                    (skill, str(spec.get("component_id") or ""))
                )
    assert len(families) >= 10
    suffix_leaks = 0
    semantic_dups = 0
    missing = 0
    multi_correct = 0
    for family, comps in families.items():
        skill, component = comps[0]
        mod = importlib.import_module(f"skills.{skill}")
        for seed in range(8):
            payload = mod.generate(seed=seed, component_id=component)
            choices = payload.get("choices") or []
            if len(choices) != 4:
                missing += 1
                continue
            texts = _choice_texts(payload)
            if any(has_technical_choice_suffix(t) for t in texts):
                suffix_leaks += 1
            keys = [choice_semantic_key(t) for t in texts]
            if len(set(keys)) != 4:
                semantic_dups += 1
            expected = str(payload.get("display_answer") or "")
            if expected and expected.upper() not in {"A", "B", "C", "D"}:
                if sum(1 for t in texts if choice_semantic_key(t) == choice_semantic_key(expected)) > 1:
                    multi_correct += 1
    assert suffix_leaks == 0
    assert semantic_dups == 0
    assert missing == 0
    assert multi_correct == 0
