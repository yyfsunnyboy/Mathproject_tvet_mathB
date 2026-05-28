from __future__ import annotations

import json
from pathlib import Path

from core.gencode.pipeline_orchestrator import run_gencode_phase1
from core.gencode.problem_type_induction import induce_problem_types_from_examples

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
FIXTURE = Path(__file__).parent / "fixtures" / "cartesian_source_examples.json"


def test_curated_first_still_loads_json_specs():
    from core.gencode.problem_type_spec import list_problem_types_for_skill

    curated = list_problem_types_for_skill(SKILL_ID, prefer="curated")
    assert len(curated) >= 1


def test_induce_from_sources_does_not_require_six_curated_types():
    examples = json.loads(FIXTURE.read_text(encoding="utf-8"))
    induced = induce_problem_types_from_examples(SKILL_ID, examples)
    assert len(induced.get("candidate_problem_types", [])) == 2
    phase1 = run_gencode_phase1(SKILL_ID, dry_run=True, spec_mode="induce_from_sources")
    assert phase1.get("spec_mode") == "induce_from_sources"
    cands = phase1.get("candidate_problem_types", [])
    assert len(cands) == 2
    for c in cands:
        assert c.get("spec_source") == "phase1_induced_draft"
