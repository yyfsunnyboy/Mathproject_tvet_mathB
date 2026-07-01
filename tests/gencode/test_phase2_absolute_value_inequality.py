# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from pathlib import Path
import pytest

from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example, build_v3_component_draft_from_skill
from core.gencode.problem_type_canonicalizer import enrich_spec_with_canonicalization

SKILL_ID = "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"

@pytest.mark.skipif(not DB_PATH.exists(), reason="Production DB not found")
def test_phase2_absolute_value_inequality_contract() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Verify 4411, 4415
    for eid in [4411, 4415]:
        row = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone()
        assert row is not None
        row_dict = dict(row)
        
        phase1_spec = run_v3_no_llm_phase1_for_example(SKILL_ID, row_dict, conn=conn)
        enriched_spec = enrich_spec_with_canonicalization({**phase1_spec, "skill_id": SKILL_ID, "problem_type_id": phase1_spec.get("problem_type_id")})
        
        # Verify Phase 2 contract properties
        ac = enriched_spec.get("answer_contract") or {}
        assert ac.get("answer_type") == "interval"
        assert ac.get("checker_key") == "interval_checker"
        
        # Verify Phase 2 draft generation
        draft = build_v3_component_draft_from_skill(
            skill_id=SKILL_ID,
            textbook_example_id=eid,
            source_kind=f"ex_{eid}",
            conn=conn,
            constraints={"v3_induced_spec": enriched_spec, "phase1_classification": enriched_spec}
        )
        
        # Parse generate.py and verify execution
        gen_code = draft["files"]["generate.py"]
        namespace = {"__builtins__": __builtins__}
        exec(gen_code, namespace)
        payload = namespace["generate"](seed=42)
        
        assert payload["answer_type"] == "interval"
        assert payload["presentation_mode"] == "short_answer"
        assert payload["checker_key"] == "interval_checker"
        assert payload["correct_answer"] is not None
        
    # Verify 4416
    row = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (4416,)).fetchone()
    assert row is not None
    row_dict = dict(row)
    
    phase1_spec = run_v3_no_llm_phase1_for_example(SKILL_ID, row_dict, conn=conn)
    enriched_spec = enrich_spec_with_canonicalization({**phase1_spec, "skill_id": SKILL_ID, "problem_type_id": phase1_spec.get("problem_type_id")})
    
    ac = enriched_spec.get("answer_contract") or {}
    assert ac.get("answer_type") in ("choice", "single_choice")
    assert ac.get("checker_key") == "choice_label_checker"
    
    draft = build_v3_component_draft_from_skill(
        skill_id=SKILL_ID,
        textbook_example_id=4416,
        source_kind="ex_4416",
        conn=conn,
        constraints={"v3_induced_spec": enriched_spec, "phase1_classification": enriched_spec}
    )
    
    gen_code = draft["files"]["generate.py"]
    namespace = {"__builtins__": __builtins__}
    exec(gen_code, namespace)
    
    # Test 20 seeds
    for s in range(20):
        payload = namespace["generate"](seed=s)
        
        assert payload["answer_type"] == "single_choice"
        assert payload["presentation_mode"] == "single_choice"
        assert payload["checker_key"] == "choice_label_checker"
        assert payload["correct_answer"] in ("A", "B", "C", "D")
        assert len(payload["choices"]) == 4
        
        # Verify choices are the four unique quadrants
        choices_texts = {c["text"] for c in payload["choices"]}
        assert choices_texts == {"第一象限", "第二象限", "第三象限", "第四象限"}
        
        # Verify parameters and formula
        givens = payload["metadata"]["givens"]
        d = givens["d"]
        e = givens["e"]
        c = givens["c"]
        a = givens["a"]
        b = givens["b"]
        
        assert a == d * e - c
        assert b == e - 2 * (c // d)
        assert a != 0
        assert b != 0
        
        # Verify question_text format matches and contains parameters
        qtext = payload["question_text"]
        assert "若不等式" in qtext
        assert "屬於哪一象限？" in qtext
        assert str(d) in qtext
        assert str(c) in qtext
        assert str(e) in qtext
        
        # Verify quadrant match
        if b > 0 and a > 0:
            expected_quad = "第一象限"
        elif b < 0 and a > 0:
            expected_quad = "第二象限"
        elif b < 0 and a < 0:
            expected_quad = "第三象限"
        else:
            expected_quad = "第四象限"
            
        correct_choice_label = payload["correct_answer"]
        selected_choice = next(c for c in payload["choices"] if c["label"] == correct_choice_label)
        assert selected_choice["text"] == expected_quad
    
    conn.close()
