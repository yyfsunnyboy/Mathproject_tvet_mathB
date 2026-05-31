from __future__ import annotations

import json
from pathlib import Path

from core.gencode.problem_type_induction import induce_problem_types_from_examples

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
FIXTURE = Path(__file__).parent / "fixtures" / "cartesian_source_examples.json"


def test_cartesian_four_examples_induce_two_problem_types():
    examples = json.loads(FIXTURE.read_text(encoding="utf-8"))
    result = induce_problem_types_from_examples(SKILL_ID, examples)
    cands = result.get("candidate_problem_types", [])
    assert len(cands) == 2
    answer_types = sorted(
        {
            str((c.get("problem_type_spec_draft") or {}).get("answer_contract", {}).get("answer_type", ""))
            for c in cands
            if isinstance(c, dict)
        }
    )
    assert answer_types == ["short_answer", "single_choice"]
    ex_gate = result.get("exception_review_gate", {})
    assert ex_gate.get("required") is False
    for c in cands:
        draft = c.get("problem_type_spec_draft", {})
        assert draft.get("answer_contract")
        assert draft.get("stem_contract")
        assert draft.get("generator_contract")
        assert c.get("spec_source") == "phase1_induced_draft"
    short_ids = {
        int(x)
        for c in cands
        for x in (c.get("matched_example_ids") or [])
        if str((c.get("problem_type_spec_draft") or {}).get("answer_contract", {}).get("answer_type")) == "short_answer"
    }
    choice_ids = {
        int(x)
        for c in cands
        for x in (c.get("matched_example_ids") or [])
        if str((c.get("problem_type_spec_draft") or {}).get("answer_contract", {}).get("answer_type")) == "single_choice"
    }
    assert short_ids == {4417, 4435}
    assert choice_ids == {4509, 4510}
