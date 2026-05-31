from __future__ import annotations

import json
from pathlib import Path

from core.gencode.phase3_skill_codegen import build_generator_specs_for_phase3
from core.gencode.problem_type_induction import induce_problem_types_from_examples
from core.gencode.problem_type_spec import save_induced_problem_type_specs
from core.gencode.slot_generators import generate_from_problem_type_spec

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
FIXTURE = Path(__file__).parent / "fixtures" / "cartesian_source_examples.json"


def test_phase2_generator_from_induced_spec_draft(tmp_path, monkeypatch):
    examples = json.loads(FIXTURE.read_text(encoding="utf-8"))
    induced = induce_problem_types_from_examples(SKILL_ID, examples)
    specs = induced.get("induced_problem_type_specs", [])
    assert len(specs) == 2
    save_induced_problem_type_specs(SKILL_ID, specs)

    phase2_usable = [
        {
            "problem_type_id": str(s.get("problem_type_id", "")),
            "generator_key": f"{SKILL_ID}:{s.get('problem_type_id')}:draft_v1",
            "problem_type_spec_draft": s,
            "spec_source": "phase1_induced_draft",
        }
        for s in specs
    ]
    gen_specs, keys = build_generator_specs_for_phase3(SKILL_ID, phase2_usable)
    assert len(gen_specs) == 2
    assert len(keys) == 2
    for spec in specs:
        payload = generate_from_problem_type_spec(SKILL_ID, spec, seed=7)
        assert payload.get("question_text")
        ac = spec.get("answer_contract", {})
        if ac.get("answer_type") == "single_choice":
            assert payload.get("choices")
            qt = payload["question_text"]
            assert "(A)" not in qt and "(B)" not in qt
        else:
            assert not payload.get("choices")
