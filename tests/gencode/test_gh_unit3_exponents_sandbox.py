"""Sandbox gate for 普高數學1 Unit 3 (指數): per-component contract, oracle and grading checks.

Runs against ``reports/gencode_v3_dryrun`` with the candidate domain registered in memory only.
"""

from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import pytest

from agent_domains_candidate.algebra_exponent_laws.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.algebra_exponent_laws.unit3_specs import COMPONENTS, OP, SKILLS
from core.gencode.answer_payload import validate_answer_contract_consistency
from core.gencode.checker_registry import validate_answer_contract_capability
from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.services.v3_question_integrity_validator import validate_component_payload
from core.gencode.v3_component_scaffold_builder import _build_get_hint_py

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
SEEDS = range(20)
register_candidate_in_memory()

CASES = [(cid, SKILLS[spec[0]], OP[spec[1]]) for cid, spec in COMPONENTS.items()]


def _load(skill_id: str, cid: int, filename: str):
    path = DRYRUN / skill_id / "components" / f"src_{cid}" / filename
    spec = importlib.util.spec_from_file_location(f"u3_{cid}_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _grade(payload, answer, skill_id):
    return bool(check_answer(answer, payload["correct_answer"], payload=payload,
                             answer_contract=payload["answer_contract"], skill_id=skill_id))


def _wrong_value(part: dict) -> str:
    expected = part["expected_answer"]
    kind = part["answer_type"]
    if kind == "single_choice":
        labels = [str(c["label"]) for c in part["choices"]]
        if str(expected) in labels:
            return next(label for label in labels if label != str(expected))
        return next(str(c["value"]) for c in part["choices"] if str(c["value"]) != str(expected))
    if kind == "rational":
        return str(Fraction(expected) + 1)
    return f"{expected}+1"


def _parts(payload):
    contract = payload["answer_contract"]
    if contract["answer_type"] == "multi_part":
        return contract["parts"]
    return [{**contract, "key": None, "expected_answer": payload["correct_answer"]}]


@pytest.mark.parametrize(("cid", "skill_id", "operation"), CASES)
def test_component_contract_oracle_and_grading(cid, skill_id, operation):
    directory = DRYRUN / skill_id / "components" / f"src_{cid}"
    assert {p.name for p in directory.iterdir() if p.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    assert (directory / "get_hint.py").read_text(encoding="utf-8") == _build_get_hint_py()
    generator = _load(skill_id, cid, "generate.py")
    metadata = _load(skill_id, cid, "metadata.py")
    assert metadata.TEXTBOOK_EXAMPLE_ID == cid and metadata.DOMAIN_OPERATION == operation

    questions = set()
    for seed in SEEDS:
        payload = generator.generate(seed=seed)
        assert payload == generator.generate(seed=seed)  # deterministic
        assert payload["domain_operation"] == operation and payload["textbook_example_id"] == cid
        assert payload["fixed_domain_key"] == "algebra.exponent_laws"
        assert validate_answer_contract_capability(payload["answer_contract"])["checker_capability_status"] == "ok"
        assert validate_answer_contract_consistency(payload) == []
        integrity = validate_component_payload(payload, component_id=f"src_{cid}")
        assert integrity["passed"], integrity["blockers"]
        questions.add(payload["question_text"])

        # canonical answer accepted
        assert _grade(payload, payload["correct_answer"], skill_id)
        parts = _parts(payload)
        if payload["answer_contract"]["answer_type"] == "multi_part":
            for part in parts:
                bad = dict(payload["correct_answer"])
                bad[part["key"]] = _wrong_value(part)
                assert not _grade(payload, bad, skill_id), (seed, part["key"], bad)
        else:
            assert not _grade(payload, _wrong_value(parts[0]), skill_id)
    variants = json.loads(json.dumps(len(questions)))
    assert variants >= 9  # smallest natural input domain (digits 1-9) is 9
