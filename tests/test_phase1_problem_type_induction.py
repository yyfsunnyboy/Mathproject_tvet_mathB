from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from core.gencode.problem_type_induction import induce_problem_types_from_examples

SKILL_ID = "vh_數學B1_CartesianCoordinateSystemEstablishment"
FIXTURE = Path(__file__).parent / "fixtures" / "cartesian_source_examples.json"


def test_cartesian_phase1_induction_smoke_with_source_quality_filtering():
    examples = json.loads(FIXTURE.read_text(encoding="utf-8"))
    meta = {
        "skill_ch_name": "平面坐標系",
        "skill_en_name": "CartesianCoordinateSystemEstablishment",
        "chapter": "1 坐標系與圖形",
        "section_code": "1-1 平面坐標系",
    }
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        result = induce_problem_types_from_examples(SKILL_ID, examples)
    cands = result.get("candidate_problem_types", [])
    assert isinstance(cands, list)
    ex_gate = result.get("exception_review_gate", {})
    assert ex_gate.get("required") is False
    assert str(result.get("source_alignment_status", "")) in {"pass", "warn"}
    rejected = result.get("rejected_source_examples") or []
    rejected_ids = {int(x.get("example_id")) for x in rejected if isinstance(x, dict) and str(x.get("example_id", "")).isdigit()}
    assert {4509, 4510}.issubset(rejected_ids)
    for c in cands:
        draft = c.get("problem_type_spec_draft", {})
        assert draft.get("answer_contract")
        assert draft.get("stem_contract")
        assert draft.get("generator_contract")
        assert c.get("spec_source") == "phase1_induced_draft"
