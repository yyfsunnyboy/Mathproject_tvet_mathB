# -*- coding: utf-8 -*-
"""Multi-field range/IQR answer contract for descriptive statistics."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.domain.statistics.descriptive_statistics_domain import build_descriptive_statistics_matrix

REPO = Path(__file__).resolve().parents[2]


def _generate(component_id: str, seed: int = 3845) -> dict:
    path = REPO / f"agent_skills_v3/vh_數學B4_DispersionMeasures/components/{component_id}/generate.py"
    spec = importlib.util.spec_from_file_location(f"gen_{component_id}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(REPO))
    spec.loader.exec_module(mod)
    return mod.generate(seed=seed)


def test_3845_has_four_numeric_fields() -> None:
    payload = _generate("src_3845", seed=3845)
    ac = payload["answer_contract"]
    parts = ac["parts"]
    assert len(parts) == 4
    keys = [p["field_key"] for p in parts]
    assert keys == ["group_1_range", "group_1_iqr", "group_2_range", "group_2_iqr"]
    assert all(p["checker_key"] == "integer_checker" for p in parts)
    assert payload["answer"] == [75, 23, 24, 15]
    assert len(payload["subquestions"]) == 4
    assert payload["ui_contract"].get("field_groups")


def test_numeric_answers_accept_without_r_iqr_prefix() -> None:
    payload = _generate("src_3845", seed=3845)
    ac = payload["answer_contract"]
    good = check_multi_part_answer([75, 23, 24, 15], payload["answer"], answer_contract=ac, payload=payload)
    assert good["overall_correct"] is True
    bad = check_multi_part_answer(["R=75", "IQR=23", "R=24", "IQR=15"], payload["answer"], answer_contract=ac, payload=payload)
    assert bad["overall_correct"] is False


def test_compare_dispersion_3846_3847_four_fields() -> None:
    for component_id in ("src_3846", "src_3847"):
        payload = _generate(component_id, seed=3846)
        parts = payload["answer_contract"]["parts"]
        assert len(parts) == 4
        assert all(p["checker_key"] in {"integer_checker", "numeric_checker"} for p in parts)


def test_table_fill_unaffected() -> None:
    matrix = build_descriptive_statistics_matrix(
        seed=42,
        domain_operation="complete_descriptive_statistics_table",
    )
    payload = convert_domain_matrix_to_question_payload(matrix, domain_operation="complete_descriptive_statistics_table")
    assert payload["presentation_mode"] == "table_fill"
    assert payload["answer_contract"]["checker_key"] == "multi_part_answer_checker"
