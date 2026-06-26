# -*- coding: utf-8 -*-
"""Tests for canonical single-choice contract validation."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator

import pytest

from core.gencode.choice_contract_validator import (
    normalize_canonical_choices,
    validate_choice_contract,
)
from core.gencode.single_choice_contract import build_single_choice_contract
from core.gencode.single_choice_payload_normalizer import normalize_single_choice_payload
from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.v3_publish_eligibility import evaluate_v3_publish_eligibility
from core.gencode.services.v3_question_integrity_validator import validate_component_payload
from core.gencode.v3_error_codes import CHOICE_CONTRACT_INCOMPLETE


def _valid_choice_payload() -> dict:
    return {
        "presentation_mode": "single_choice",
        "question_text": "下列何者正確？",
        "answer": "A",
        "choices": [
            {"key": "A", "text": "選項甲"},
            {"key": "B", "text": "選項乙"},
            {"key": "C", "text": "選項丙"},
            {"key": "D", "text": "選項丁"},
        ],
        "checker": "choice_label_checker",
        "answer_contract": {
            "answer_type": "single_choice",
            "checker_key": "choice_label_checker",
            "presentation_mode": "single_choice",
        },
    }


def test_build_single_choice_contract_from_distractors() -> None:
    bundle = build_single_choice_contract(
        "65",
        ["64", "71", "74"],
        seed=42,
    )
    payload = {
        **_valid_choice_payload(),
        "choices": bundle["choices"],
        "answer": bundle["correct_answer"],
    }
    result = validate_choice_contract(payload)
    assert result["ok"] is True
    assert len(bundle["choices"]) >= 2


def test_build_single_choice_contract_preserves_source_choices() -> None:
    bundle = build_single_choice_contract(
        "65",
        [],
        source_choices=["64", "65", "71", "74"],
        source_answer_label="B",
        preserve_source_choices=True,
    )
    assert bundle["correct_answer"] == "B"
    assert [item["text"] for item in bundle["choices"]] == ["64", "65", "71", "74"]


def test_valid_single_choice_passes() -> None:
    result = validate_choice_contract(_valid_choice_payload())
    assert result["ok"] is True
    assert result["error_code"] == ""
    assert len(result["choices"]) == 4

    integrity = validate_component_payload(_valid_choice_payload(), component_id="src_test")
    assert integrity["passed"] is True


def test_empty_choices_fails() -> None:
    payload = _valid_choice_payload()
    payload["choices"] = []
    result = validate_choice_contract(payload)
    assert result["ok"] is False
    assert result["error_code"] == CHOICE_CONTRACT_INCOMPLETE
    assert any("choices_empty" in blocker for blocker in result["blockers"])

    integrity = validate_component_payload(payload, component_id="src_test")
    assert integrity["passed"] is False


def test_duplicate_choice_keys_fail() -> None:
    payload = _valid_choice_payload()
    payload["choices"] = [
        {"key": "A", "text": "甲"},
        {"key": "A", "text": "乙"},
        {"key": "C", "text": "丙"},
        {"key": "D", "text": "丁"},
    ]
    result = validate_choice_contract(payload)
    assert result["ok"] is False
    assert any("duplicate_choice_keys" in blocker for blocker in result["blockers"])


def test_answer_not_in_choices_fails() -> None:
    payload = _valid_choice_payload()
    payload["answer"] = "Z"
    result = validate_choice_contract(payload)
    assert result["ok"] is False
    assert any("answer_not_in_choices" in blocker for blocker in result["blockers"])


def test_short_answer_not_affected() -> None:
    payload = {
        "presentation_mode": "short_answer",
        "question_text": "（1）求平均數。（2）求全距。",
        "answer": "12",
        "choices": [],
        "answer_type": "numeric",
        "checker": "numeric_checker",
    }
    result = validate_choice_contract(payload)
    assert result["ok"] is True
    assert result["details"]["applicable"] is False

    normalized = normalize_single_choice_payload(payload)
    assert normalized["question_text"] == "（1）求平均數。（2）求全距。"


def test_normalize_accepts_label_legacy_shape() -> None:
    normalized = normalize_canonical_choices(
        [{"label": "A", "text": "第一象限"}, {"label": "B", "text": "第二象限"}]
    )
    assert normalized[0]["key"] == "A"
    assert normalized[0]["text"] == "第一象限"


@pytest.fixture
def memory_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL
        )
        """
    )
    apply_tracker_ddl(conn)
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, "vh_test_choice_publish_skill"),
    )
    conn.commit()
    try:
        yield conn
    finally:
        conn.close()


def test_publish_eligibility_rejects_invalid_choice_contract(memory_conn: sqlite3.Connection) -> None:
    memory_conn.execute(
        """
        INSERT INTO gencode_component_tracker
            (textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            1,
            "vh_test_choice_publish_skill",
            "src_1",
            "verified",
            json.dumps(
                {
                    "presentation_mode": "single_choice",
                    "integrity_gate_passed": True,
                    "integrity_gate_version": "v1",
                    "choice_contract_valid": False,
                    "fixed_domain_key": "statistics.descriptive_statistics",
                    "resolution_source": "derived_capability_match",
                    "binding_status": "derived",
                    "required_capabilities": ["arithmetic_mean"],
                    "matched_capabilities": ["arithmetic_mean"],
                    "selected_operation": "compute_arithmetic_mean_from_raw_values",
                    "domain_module": "core.domain.statistics.descriptive_statistics_domain",
                    "entrypoint": "build_descriptive_statistics_matrix",
                },
                ensure_ascii=False,
            ),
        ),
    )
    memory_conn.commit()

    eligibility = evaluate_v3_publish_eligibility(memory_conn, "vh_test_choice_publish_skill")
    assert eligibility["allowed"] is False
    assert int(eligibility.get("eligible_component_count") or 0) == 0


def test_short_answer_regression_still_passes_integrity() -> None:
    payload = {
        "presentation_mode": "short_answer",
        "question_text": "已知 1, 2, 3，求平均數。",
        "answer": "2",
        "answer_type": "numeric",
        "checker": "numeric_checker",
        "problem_type_id": "compute_arithmetic_mean_from_raw_values",
        "fixed_domain_key": "statistics.descriptive_statistics",
    }
    integrity = validate_component_payload(payload, component_id="src_short")
    assert integrity["passed"] is True
