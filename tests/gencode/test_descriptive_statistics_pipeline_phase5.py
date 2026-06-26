# -*- coding: utf-8 -*-
"""Phase 5 descriptive statistics pipeline E2E tests (synthetic fixtures only)."""

from __future__ import annotations

import ast
import importlib.util
import py_compile
import re
import sqlite3
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from core.checkers.solution_set_checker import check_solution_set_answer
from core.domain.statistics.descriptive_statistics_domain import (
    DOMAIN_KEY,
    ENTRYPOINT,
    build_descriptive_statistics_matrix,
)
from core.gencode.checker_registry import CHECKER_CAPABILITIES
from core.gencode.descriptive_statistics_answer_contract import (
    NO_MODE_SENTINEL,
    normalize_answer_contract,
)
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority
from core.gencode.v3_component_scaffold_builder import build_component_files_from_domain_payload
from core.gencode.validators.descriptive_statistics_validator import validate_descriptive_statistics_payload
from core.gencode.v3_error_codes import DOMAIN_CAPABILITY_PARTIAL, DOMAIN_CAPABILITY_UNRESOLVED
from core.registry.domain_operation_registry import get_domain_spec

ABSTRACT_SKILL = "abstract_descriptive_statistics_skill"
REPO = Path(__file__).resolve().parents[2]
DB_PATH = REPO / "instance" / "kumon_math.db"

DESCRIPTIVE_SKILLS = (
    "CentralTendencyMeasures",
    "WeightedMean",
    "DispersionMeasures",
    "VarianceAndStandardDeviation",
)


def _payload(operation: str, seed: int = 42, **constraints) -> dict:
    matrix = build_descriptive_statistics_matrix(
        seed=seed,
        domain_operation=operation,
        constraints=constraints or None,
    )
    return convert_domain_matrix_to_question_payload(matrix, domain_operation=operation)


def _domain_meta() -> dict:
    spec = get_domain_spec(DOMAIN_KEY)
    assert spec is not None
    return {
        "domain_module": spec.domain_module,
        "entrypoint": spec.entrypoint,
        "default_curriculum_profile": "vocational_high_b",
    }


def test_checker_registry_inventory() -> None:
    required = {
        "integer_checker",
        "rational_checker",
        "decimal_tolerance_checker",
        "expression_equivalence_checker",
        "unordered_set_checker",
        "text_short_checker",
        "multi_part_answer_checker",
        "table_fill_checker",
    }
    for key in required:
        cap = CHECKER_CAPABILITIES[key]
        assert cap.get("runtime_available") is True
        assert cap.get("answer_types")
        assert cap.get("equivalence_types")


def test_exact_integer_contract() -> None:
    contract = normalize_answer_contract(7, "single_numeric")
    assert contract["checker_key"] == "integer_checker"
    assert contract["equivalence_type"] == "numeric_exact"
    payload = _payload("compute_arithmetic_mean_from_raw_values", raw_values=[2, 4, 6, 8])
    assert payload["answer_contract"]["checker_key"] == "integer_checker"


def test_exact_rational_contract() -> None:
    contract = normalize_answer_contract("3/2", "single_numeric")
    assert contract["checker_key"] == "rational_checker"
    assert contract["equivalence_type"] == "rational_equivalent"


def test_decimal_tolerance_contract() -> None:
    contract = normalize_answer_contract(
        "79.8",
        "single_numeric",
        rounding_policy={"decimal_places": 1, "prefer_integer": False, "require_tolerance": True},
    )
    assert contract["checker_key"] == "decimal_tolerance_checker"
    assert contract["tolerance"] == pytest.approx(0.05)
    payload = _payload(
        "compute_weighted_mean",
        seed=3,
        weights=[(81, 3), (72, 2)],
        rounding_policy={"decimal_places": 1, "prefer_integer": False, "require_tolerance": True},
    )
    assert payload["answer_contract"]["checker_key"] == "decimal_tolerance_checker"
    assert "權重" in payload["question_text"]


def test_unordered_set_contract_and_checker() -> None:
    payload = _payload("compute_mode_from_raw_values", force_multi_mode=True)
    assert payload["answer_shape"] == "unordered_set"
    assert payload["answer_contract"]["checker_key"] == "unordered_set_checker"
    modes = payload["correct_answer"]
    assert check_solution_set_answer(", ".join(str(int(m)) for m in reversed(modes)), modes)
    assert check_answer(", ".join(str(int(m)) for m in modes), modes, payload=payload, answer_contract=payload["answer_contract"])


def test_short_text_no_mode_contract() -> None:
    payload = _payload("compute_mode_from_raw_values", force_no_mode=True)
    assert payload["answer_shape"] == "text_short"
    assert payload["answer"] == NO_MODE_SENTINEL
    assert payload["answer_contract"]["checker_key"] == "text_short_checker"


def test_table_fill_contract() -> None:
    payload = _payload("complete_descriptive_statistics_table")
    assert payload["answer_shape"] == "table_fill"
    assert payload["table_data"]["type"] == "table_fill"
    parts = payload["answer_contract"]["parts"]
    assert len(parts) == 5
    assert {part["field_key"] for part in parts} == {
        "field_mean",
        "field_median",
        "field_range",
        "field_variance",
        "field_standard_deviation",
    }


@pytest.mark.parametrize(
    "operation",
    [
        "compute_arithmetic_mean_from_raw_values",
        "compute_mode_from_raw_values",
        "complete_descriptive_statistics_table",
    ],
)
def test_runtime_scaffold_artifact(operation: str) -> None:
    payload = _payload(operation)
    payload_meta = dict(payload.get("scaffold_payload_meta") or {})
    payload_meta.setdefault("fixed_domain_key", DOMAIN_KEY)
    files = build_component_files_from_domain_payload(
        skill_id=ABSTRACT_SKILL,
        component_id="synthetic_component",
        source_kind="example",
        domain_meta=_domain_meta(),
        payload_meta=payload_meta,
    )
    assert set(files.keys()) == {"metadata.py", "generate.py", "get_hint.py"}
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name, content in files.items():
            path = root / name
            path.write_text(content, encoding="utf-8")
            py_compile.compile(str(path), doraise=True)
        for content in files.values():
            ast.parse(content)
        spec = importlib.util.spec_from_file_location("generate_mod", root / "generate.py")
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        generated = module.generate(seed=42)
        assert generated["question_text"]
        assert generated["answer_contract"]["checker_key"]
        hint_mod_spec = importlib.util.spec_from_file_location("hint_mod", root / "get_hint.py")
        assert hint_mod_spec and hint_mod_spec.loader
        hint_mod = importlib.util.module_from_spec(hint_mod_spec)
        hint_mod_spec.loader.exec_module(hint_mod)
        hint = hint_mod.get_hint(1, generated)
        assert hint
        assert "依序思考" not in hint
        errors = validate_descriptive_statistics_payload(generated)
        assert errors == [], errors


def test_domain_evidence_in_payload() -> None:
    payload = _payload("compute_range")
    resolution = payload["domain_resolution"]
    for key in (
        "fixed_domain_key",
        "selected_operation",
        "required_capabilities",
        "matched_capabilities",
        "resolution_source",
        "binding_status",
        "registry_revision",
    ):
        assert resolution.get(key) not in (None, "", [])


def test_capability_gap_unresolved() -> None:
    extra = {"required_capabilities": ["interquartile_range"], "classification_source": "test_induced_spec"}
    with mock.patch(
        "core.gencode.skill_fixed_domain_authority.get_confirmed_skill_binding",
        return_value=None,
    ):
        with pytest.raises(Exception) as exc:
            resolve_domain_authority(ABSTRACT_SKILL, extra=extra)
    code = getattr(exc.value, "code", "")
    assert code in {DOMAIN_CAPABILITY_PARTIAL, DOMAIN_CAPABILITY_UNRESOLVED}


def test_seed_reproducibility_and_variability() -> None:
    op = "compute_median_from_raw_values"
    p1 = _payload(op, seed=11)
    p2 = _payload(op, seed=11)
    p3 = _payload(op, seed=12)
    assert p1["answer"] == p2["answer"]
    assert p1["question_text"] != p3["question_text"] or p1["answer"] != p3["answer"]


def test_no_skill_or_example_literals_in_phase5_production_code() -> None:
    targets = [
        REPO / "core/gencode/descriptive_statistics_answer_contract.py",
        REPO / "core/gencode/domain_matrix_adapter.py",
        REPO / "core/domain/statistics/descriptive_statistics_domain.py",
        REPO / "core/gencode/validators/descriptive_statistics_validator.py",
    ]
    forbidden = (
        re.compile(r"vh_[\w\u4e00-\u9fff]+"),
        re.compile(r"src_\d+"),
        re.compile(r"textbook_example_id\s*=\s*\d+"),
    )
    for path in targets:
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden:
            assert not pattern.search(text), f"forbidden literal in {path.name}"


@pytest.mark.skipif(not DB_PATH.is_file(), reason="local DB unavailable")
def test_textbook_integration_fixtures_by_capability() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    placeholders = ",".join("?" for _ in DESCRIPTIVE_SKILLS)
    rows = conn.execute(
        f"""
        SELECT id, skill_id, problem_text, correct_answer
        FROM textbook_examples
        WHERE {' OR '.join(f"skill_id LIKE '%{name}'" for name in DESCRIPTIVE_SKILLS)}
        ORDER BY id
        LIMIT 40
        """
    ).fetchall()
    conn.close()
    assert rows

    covered: set[str] = set()
    for row in rows:
        skill = str(row["skill_id"])
        if "CentralTendency" in skill:
            caps = ["arithmetic_mean"]
            operation = "compute_arithmetic_mean_from_raw_values"
            shape = "single_numeric"
        elif "WeightedMean" in skill:
            caps = ["weighted_mean"]
            operation = "compute_weighted_mean"
            shape = "single_numeric"
        elif "Variance" in skill:
            caps = ["standard_deviation"]
            operation = "compute_population_standard_deviation"
            shape = "single_numeric"
        else:
            continue
        if shape in covered:
            continue
        extra = {
            "required_capabilities": caps,
            "classification_source": "integration_fixture",
            "problem_type_id": operation,
        }
        result = resolve_domain_authority(skill, textbook_example=dict(row), extra=extra)
        assert result.fixed_domain_key == DOMAIN_KEY
        matrix = build_descriptive_statistics_matrix(seed=int(row["id"]) % 100, domain_operation=operation)
        payload = convert_domain_matrix_to_question_payload(matrix, domain_operation=operation)
        assert validate_descriptive_statistics_payload(payload) == []
        covered.add(shape)
        if len(covered) >= 2:
            break
    assert covered
