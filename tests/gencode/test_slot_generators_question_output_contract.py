# -*- coding: utf-8 -*-
"""
tests/gencode/test_slot_generators_question_output_contract.py
==============================================================
Slot Generator Question Output Contract 測試

涵蓋：5 個二次函數 slot，seed 0–9，共 50 個 payload。

驗收條件：
  - validate_generated_question_format 不含 localization_violation / formula_not_wrapped /
    choices_duplicate / answer_not_in_choices
  - 選擇題 choices 長度為 4，文字不重複，answer 為 A/B/C/D
  - text_short 平移題的 answer 使用中文，不含 left/right/up/down
  - question_text 與 explanation 中的二次函數公式有 $...$ 包裹
"""
from __future__ import annotations

import json
import os
import re
import sys

import pytest

# ─── 確保 project root 在 sys.path ────────────────────────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gencode.generated_question_format_validator import (
    validate_generated_question_format,
)
from core.gencode.slot_generators import (
    _slot_quadratic_graph_translation_fill_blank,
    _slot_quadratic_graph_translation_short_answer,
    _slot_quadratic_graph_vertex_axis_choice,
    _slot_quadratic_standard_to_vertex_properties,
    _slot_quadratic_vertex_form_properties,
)
from core.gencode.validators import validate_generator_payload

# ─── 讀取 induced spec ────────────────────────────────────────────────────────
_SPEC_PATH = os.path.join(
    ROOT,
    "reports",
    "gencode_closed_loop",
    "induced_specs",
    "vh_數學B1_QuadraticFunctionGraph.json",
)

with open(_SPEC_PATH, encoding="utf-8") as _f:
    _RAW_SPEC = json.load(_f)

_SPEC_BY_PT: dict[str, dict] = {
    item["problem_type_id"]: item for item in _RAW_SPEC["items"]
}

SKILL_ID = "vh_數學B1_QuadraticFunctionGraph"
SEEDS = list(range(10))

# ─── Slot 定義 ─────────────────────────────────────────────────────────────────
_SLOT_TABLE = [
    ("quadratic_graph_vertex_axis_choice",      _slot_quadratic_graph_vertex_axis_choice),
    ("quadratic_graph_translation_fill_blank",   _slot_quadratic_graph_translation_fill_blank),
    ("quadratic_graph_translation_short_answer", _slot_quadratic_graph_translation_short_answer),
    ("quadratic_vertex_form_properties",         _slot_quadratic_vertex_form_properties),
    ("quadratic_standard_to_vertex_properties",  _slot_quadratic_standard_to_vertex_properties),
]

_CHOICE_PTS = {
    "quadratic_graph_vertex_axis_choice",
    "quadratic_vertex_form_properties",
    "quadratic_standard_to_vertex_properties",
}

_TEXT_SHORT_PTS = {
    "quadratic_graph_translation_fill_blank",
    "quadratic_graph_translation_short_answer",
}

_BAD_FORMAT_BLOCKERS = {
    "localization_violation",
    "formula_not_wrapped",
    "choices_duplicate",
    "answer_not_in_choices",
}

_ENGLISH_SHIFT_WORDS = re.compile(r"\b(left|right|up|down)\b", re.IGNORECASE)
_DOLLAR_RE = re.compile(r"\$[^$\n]+?\$")


# ─── Parametrize 全部 50 組合 ──────────────────────────────────────────────────
_ALL_CASES = [
    (pt, fn, seed)
    for pt, fn in _SLOT_TABLE
    for seed in SEEDS
]


@pytest.mark.parametrize("pt,fn,seed", _ALL_CASES, ids=[f"{pt}_seed{s}" for pt, _, s in _ALL_CASES])
def test_slot_output_contract(pt: str, fn, seed: int) -> None:
    spec = _SPEC_BY_PT[pt]
    payload = fn(SKILL_ID, pt, spec, seed)

    # ── 1. 全域格式驗證 ────────────────────────────────────────────────────────
    format_blockers = validate_generated_question_format(
        payload, skill_id=SKILL_ID, problem_type_spec=spec
    )
    bad = set(format_blockers) & _BAD_FORMAT_BLOCKERS
    assert not bad, (
        f"[{pt} seed={seed}] format blockers: {sorted(bad)}\n"
        f"  question_text={payload.get('question_text','')!r}\n"
        f"  choices={payload.get('choices','')!r}\n"
        f"  explanation={payload.get('explanation','')!r}"
    )

    # ── 2. 語意契約驗證（semantic / answer contract）──────────────────────────
    semantic_blockers = validate_generator_payload(
        payload, skill_id=SKILL_ID, problem_type_spec=spec
    )
    sem_bad = set(semantic_blockers) & _BAD_FORMAT_BLOCKERS
    assert not sem_bad, (
        f"[{pt} seed={seed}] semantic blockers: {sorted(sem_bad)}"
    )

    # ── 3. 選擇題特定斷言 ──────────────────────────────────────────────────────
    if pt in _CHOICE_PTS:
        choices = payload.get("choices", [])
        assert len(choices) == 4, (
            f"[{pt} seed={seed}] choices length={len(choices)}, expected 4"
        )
        texts = [c["text"] for c in choices]
        assert len(texts) == len(set(texts)), (
            f"[{pt} seed={seed}] duplicate choice texts: {texts}"
        )
        ans = payload.get("correct_answer") or payload.get("answer", "")
        assert re.fullmatch(r"[A-D]", str(ans)), (
            f"[{pt} seed={seed}] answer={ans!r} is not A/B/C/D"
        )
        checker = payload.get("checker_type") or payload.get("checker", "")
        assert checker == "choice_label_checker", (
            f"[{pt} seed={seed}] checker={checker!r}"
        )
        # question_text 不得嵌入 (A)(B)(C)(D)
        qt = payload.get("question_text", "")
        assert not re.search(r"\(A\)|\(B\)|\(C\)|\(D\)", qt), (
            f"[{pt} seed={seed}] choices embedded in question_text: {qt!r}"
        )

    # ── 4. text_short 平移題特定斷言 ──────────────────────────────────────────
    if pt in _TEXT_SHORT_PTS:
        answer = str(payload.get("correct_answer") or payload.get("answer", ""))
        assert not _ENGLISH_SHIFT_WORDS.search(answer), (
            f"[{pt} seed={seed}] answer contains English shift word: {answer!r}"
        )
        # 必須包含中文字
        assert re.search(r"[\u4e00-\u9fff]", answer), (
            f"[{pt} seed={seed}] answer has no Chinese: {answer!r}"
        )

    # ── 5. 公式顯示斷言：question_text 與 explanation 含 $...$ ────────────────
    qt = payload.get("question_text", "")
    assert _DOLLAR_RE.search(qt), (
        f"[{pt} seed={seed}] question_text has no $...$ formula: {qt!r}"
    )
    expl = payload.get("explanation", "")
    assert _DOLLAR_RE.search(expl), (
        f"[{pt} seed={seed}] explanation has no $...$ formula: {expl!r}"
    )


# ─── 額外獨立測試 ──────────────────────────────────────────────────────────────

class TestChoiceDedup:
    """驗證 h=0 / k=0 邊界時不產生重複選項。"""

    def _run(self, pt: str, fn, seed: int) -> list[dict]:
        spec = _SPEC_BY_PT[pt]
        payload = fn(SKILL_ID, pt, spec, seed)
        return payload.get("choices", [])

    def test_vertex_axis_h_zero(self) -> None:
        """seed 使 h=0 時，vertex_axis_choice 選項仍不重複。"""
        spec = _SPEC_BY_PT["quadratic_graph_vertex_axis_choice"]
        # Try all seeds; at least one should produce h=0
        for seed in range(20):
            payload = _slot_quadratic_graph_vertex_axis_choice(
                SKILL_ID, "quadratic_graph_vertex_axis_choice", spec, seed
            )
            texts = [c["text"] for c in payload["choices"]]
            assert len(texts) == len(set(texts)), (
                f"seed={seed} duplicates: {texts}"
            )

    def test_vertex_form_properties_h_zero(self) -> None:
        spec = _SPEC_BY_PT["quadratic_vertex_form_properties"]
        for seed in range(20):
            payload = _slot_quadratic_vertex_form_properties(
                SKILL_ID, "quadratic_vertex_form_properties", spec, seed
            )
            texts = [c["text"] for c in payload["choices"]]
            assert len(texts) == len(set(texts)), (
                f"seed={seed} duplicates: {texts}"
            )

    def test_standard_to_vertex_h_zero(self) -> None:
        spec = _SPEC_BY_PT["quadratic_standard_to_vertex_properties"]
        for seed in range(20):
            payload = _slot_quadratic_standard_to_vertex_properties(
                SKILL_ID, "quadratic_standard_to_vertex_properties", spec, seed
            )
            texts = [c["text"] for c in payload["choices"]]
            assert len(texts) == len(set(texts)), (
                f"seed={seed} duplicates: {texts}"
            )


class TestDisplayFormula:
    """驗證 display formula $...$ 確實出現在學生可見欄位。"""

    def test_fill_blank_display_has_dollar(self) -> None:
        spec = _SPEC_BY_PT["quadratic_graph_translation_fill_blank"]
        for seed in range(10):
            payload = _slot_quadratic_graph_translation_fill_blank(
                SKILL_ID, "quadratic_graph_translation_fill_blank", spec, seed
            )
            qt = payload["question_text"]
            assert "$" in qt, f"seed={seed} no $ in question_text: {qt!r}"

    def test_short_answer_display_has_dollar(self) -> None:
        spec = _SPEC_BY_PT["quadratic_graph_translation_short_answer"]
        for seed in range(10):
            payload = _slot_quadratic_graph_translation_short_answer(
                SKILL_ID, "quadratic_graph_translation_short_answer", spec, seed
            )
            qt = payload["question_text"]
            assert "$" in qt, f"seed={seed} no $ in question_text: {qt!r}"

    def test_metadata_givens_raw_is_ok(self) -> None:
        """metadata.givens 的 raw formula（未包 $）不影響前台顯示驗證。"""
        spec = _SPEC_BY_PT["quadratic_graph_vertex_axis_choice"]
        payload = _slot_quadratic_graph_vertex_axis_choice(
            SKILL_ID, "quadratic_graph_vertex_axis_choice", spec, 0
        )
        givens = payload.get("metadata", {}).get("givens", [])
        # givens 是 raw string list — 格式驗證不會掃 metadata plain strings
        assert isinstance(givens, list)
        blockers = validate_generated_question_format(
            payload, skill_id=SKILL_ID, problem_type_spec=spec
        )
        assert "formula_not_wrapped" not in blockers, (
            f"formula_not_wrapped triggered unexpectedly: {blockers}"
        )
