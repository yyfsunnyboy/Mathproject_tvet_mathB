from __future__ import annotations

import importlib
import re
from collections import Counter

import pytest

from core.checkers.quadrant_checker import check_quadrant_answer
from core.gencode.runtime_skill_wrapper import (
    collect_available_runtime_problem_types,
    dispatch_problem_type,
)

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
PT_SHORT = "short_answer_classify_quadrant_symbolic_condition_coordinate_point"
PT_CHOICE = "single_choice_choose_correct_statement_axis_distance_coordinate_point"
QUADRANT_LABELS = {"第一象限", "第二象限", "第三象限", "第四象限"}
_SYMBOLIC_STEM = re.compile(r"a\s*<\s*b|Q\s*\(", re.I)


def test_available_problem_types_include_short_answer_and_axis_distance_choice():
    cart_skill = importlib.import_module(f"skills.{SKILL_ID}")
    available = collect_available_runtime_problem_types(
        SKILL_ID,
        cart_skill.GENERATOR_SPECS,
        level=1,
    )
    ids = {_normalize(row["problem_type_id"]) for row in available}
    assert _normalize(PT_SHORT) in ids
    assert _normalize(PT_CHOICE) in ids
    assert len(available) >= 2


def test_generate_100_problem_type_distribution():
    mod = importlib.import_module(f"skills.{SKILL_ID}")
    counts: Counter[str] = Counter()
    for seed in range(100):
        payload = mod.generate(level=1, seed=seed)
        counts[_normalize(str(payload.get("problem_type_id", "")))] += 1

    assert counts[_normalize(PT_SHORT)] >= 1, dict(counts)
    assert counts[_normalize(PT_CHOICE)] >= 1, dict(counts)
    assert counts[_normalize(PT_SHORT)] >= 20, dict(counts)
    assert counts[_normalize(PT_CHOICE)] >= 20, dict(counts)


def test_symbolic_quadrant_short_answer_contract_and_checker():
    mod = importlib.import_module(f"skills.{SKILL_ID}")
    seen = 0
    for seed in range(100):
        payload = mod.generate(level=1, seed=seed)
        if _normalize(str(payload.get("problem_type_id", ""))) != _normalize(PT_SHORT):
            continue
        seen += 1
        answer = str(payload.get("answer", "")).strip()
        assert answer in QUADRANT_LABELS

        meta = payload.get("metadata") or {}
        derivation = " ".join(str(x) for x in (meta.get("derivation") or []))
        explanation = str(payload.get("explanation", ""))
        combined = f"{derivation} {explanation}"
        assert re.search(r"[xy]|<|>|正|負|象限", combined), combined

        if answer == "第二象限":
            for ok in ("2", "二", "第二", "第二象限", "II", "Ⅱ"):
                assert check_quadrant_answer(ok, answer) is True
            for bad in ("4", "四", "第四象限"):
                assert check_quadrant_answer(bad, answer) is False
    assert seen >= 1


def test_dispatch_strategy_is_uniform_random():
    cart_skill = importlib.import_module(f"skills.{SKILL_ID}")
    _, strategy, available = dispatch_problem_type(
        SKILL_ID,
        cart_skill.GENERATOR_SPECS,
        level=1,
        seed=11,
    )
    assert strategy == "uniform_random"
    assert len(available) >= 2


def test_symbolic_quadrant_stem_appears_in_generated_pool():
    mod = importlib.import_module(f"skills.{SKILL_ID}")
    hits = 0
    for seed in range(100):
        payload = mod.generate(level=1, seed=seed)
        if _normalize(str(payload.get("problem_type_id", ""))) != _normalize(PT_SHORT):
            continue
        qt = str(payload.get("question_text", ""))
        if _SYMBOLIC_STEM.search(qt):
            hits += 1
    assert hits >= 1


def _normalize(problem_type_id: str) -> str:
    return re.sub(r"_\d+$", "", str(problem_type_id or "").strip())
