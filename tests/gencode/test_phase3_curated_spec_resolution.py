from __future__ import annotations

import json

import pytest

import core.gencode.phase3_skill_codegen as phase3
from core.gencode.problem_type_canonicalizer import (
    enrich_spec_with_canonicalization,
    evaluate_typed_prefix_readiness,
)
from core.gencode.slot_generators import generate_from_problem_type_spec


SKILL_ID = "vh_數學B4_HistogramsAndFrequencyPolygons"
PROBLEM_TYPE_ID = "frequency_distribution_chart_construction"


def _row(problem_type_id: str = PROBLEM_TYPE_ID) -> dict:
    return {
        "problem_type_id": problem_type_id,
        "target_task": problem_type_id,
        "template_slot": problem_type_id,
        "answer_contract": {
            "answer_type": "drawing",
            "answer_shape": "drawing",
            "checker": "free_response_drawing_checker",
            "checker_key": "free_response_drawing_checker",
            "answer_equivalence": "drawing_equivalence",
        },
    }


def _source_spec(source: str, problem_type_id: str = PROBLEM_TYPE_ID) -> dict:
    return {
        "skill_id": SKILL_ID,
        "problem_type_id": problem_type_id,
        "source_marker": source,
        "generator_contract": {"template_slots": {"stem": f"{source}_slot"}},
        "hard_constraints": [{"left": {"value": 1}, "operator": "==", "right": {"value": 1}}],
        "max_attempts": 7,
    }


def _write_phase1(tmp_path, candidates: list[dict]) -> None:
    path = tmp_path / f"{phase3.sanitize_path_segment(SKILL_ID)}_phase1_summary.json"
    path.write_text(json.dumps({"candidate_problem_types": candidates}), encoding="utf-8")


@pytest.mark.parametrize(
    ("induced", "candidate", "curated", "expected"),
    [
        (True, True, True, "induced"),
        (False, True, True, "candidate"),
        (False, False, True, "curated"),
        (False, False, False, None),
    ],
)
def test_resolver_source_precedence(
    monkeypatch,
    tmp_path,
    induced,
    candidate,
    curated,
    expected,
):
    monkeypatch.setattr(phase3, "GENCODE_REPORT_DIR", tmp_path)
    monkeypatch.setattr(
        phase3,
        "list_problem_types_for_skill",
        lambda skill_id, prefer: [_source_spec("induced")] if induced else [],
    )
    _write_phase1(
        tmp_path,
        [
            {
                "problem_type_id": PROBLEM_TYPE_ID,
                "problem_type_spec_draft": _source_spec("candidate"),
            }
        ]
        if candidate
        else [],
    )

    def fake_load(skill_id, problem_type_id, *, prefer):
        assert prefer == "curated"
        assert skill_id == SKILL_ID
        assert problem_type_id == PROBLEM_TYPE_ID
        return _source_spec("curated") if curated else None

    monkeypatch.setattr(phase3, "load_problem_type_spec", fake_load)
    resolved = phase3._resolve_phase3_source_specs(SKILL_ID, [_row()])

    assert len(resolved) == 1
    if expected is None:
        assert "source_marker" not in resolved[0]
        assert "generator_contract" not in resolved[0]
    else:
        assert resolved[0]["source_marker"] == expected
        assert resolved[0]["generator_contract"]["template_slots"]["stem"] == f"{expected}_slot"


def test_curated_lookup_uses_skill_and_problem_type_compound_key(monkeypatch, tmp_path):
    monkeypatch.setattr(phase3, "GENCODE_REPORT_DIR", tmp_path)
    monkeypatch.setattr(phase3, "list_problem_types_for_skill", lambda skill_id, prefer: [])
    _write_phase1(tmp_path, [])
    calls = []

    def fake_load(skill_id, problem_type_id, *, prefer):
        calls.append((skill_id, problem_type_id, prefer))
        if skill_id == SKILL_ID and problem_type_id == PROBLEM_TYPE_ID:
            return _source_spec("curated")
        return _source_spec("wrong_skill")

    monkeypatch.setattr(phase3, "load_problem_type_spec", fake_load)
    resolved = phase3._resolve_phase3_source_specs(SKILL_ID, [_row()])

    assert resolved[0]["source_marker"] == "curated"
    assert calls == [(SKILL_ID, PROBLEM_TYPE_ID, "curated")]


def test_src_3826_curated_resolution_rebuild_and_compiled_execution():
    phase2_path = phase3.GENCODE_REPORT_DIR / (
        f"{phase3.sanitize_path_segment(SKILL_ID)}_phase2_generator_summary.json"
    )
    phase2 = json.loads(phase2_path.read_text(encoding="utf-8"))
    rows = phase2["generator_results"]

    resolved = phase3._resolve_phase3_source_specs(SKILL_ID, rows)
    assert len(resolved) == 1
    spec = resolved[0]
    assert spec["generator_contract"]["template_slots"]["stem"] == PROBLEM_TYPE_ID
    assert spec["hard_constraints"]
    assert spec["max_attempts"] == 10

    canonical = enrich_spec_with_canonicalization(spec)
    assert canonical["_resolved_template_slot"] == PROBLEM_TYPE_ID
    readiness, usable, blockers = evaluate_typed_prefix_readiness(canonical)
    assert readiness == "runtime_ready"
    assert usable is True
    assert blockers == []

    generator_specs, _ = phase3.build_generator_specs_for_phase3(SKILL_ID, rows)
    assert len(generator_specs) == 1
    rebuilt = generator_specs[0]
    assert rebuilt["problem_type_id"] == PROBLEM_TYPE_ID
    assert rebuilt["generator_readiness"] == "runtime_ready"
    assert rebuilt["hard_constraints"] == spec["hard_constraints"]
    assert rebuilt["max_attempts"] == 10

    payload = generate_from_problem_type_spec(SKILL_ID, spec, seed=0)
    assert payload["answer_type"] == "drawing"
    assert payload["metadata"]["givens"]["total_frequency"] >= 12
