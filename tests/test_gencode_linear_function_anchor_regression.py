from __future__ import annotations

from core.gencode.main_skill_anchor import build_main_skill_anchor
from core.gencode.pipeline_orchestrator import run_gencode_phase1


def test_linear_function_anchor_family_regression():
    meta = {
        "skill_ch_name": "線型函數",
        "skill_en_name": "LinearFunction",
        "chapter": "1 坐標系與函數圖形",
        "section_code": "1-2 平面坐標系與線型函數",
    }
    anchor = build_main_skill_anchor("vh_數學B1_LinearFunction", meta)
    fams = set(anchor.get("expected_task_families") or [])
    assert "function_concept_family" in fams
    assert fams != {"coordinate_system_family"}
    subs = set(anchor.get("expected_subskill_candidates") or [])
    assert {"evaluate_function_value", "interpret_function_notation"} <= subs


def test_linear_function_phase1_not_blocked_by_majority_needs_review():
    out = run_gencode_phase1("vh_數學B1_LinearFunction", dry_run=True)
    blockers = out.get("alignment_blockers") or []
    assert "majority_needs_review" not in blockers
    assert str(out.get("source_alignment_status", "")).strip() in {"warn", "pass"}
    assert bool(out.get("can_continue")) is True
    rows = out.get("source_example_alignment") or []
    targeted = [r for r in rows if r.get("example_id") in {4433, 4434, 4444, 4424, 4448, 4449, 4516}]
    assert targeted
    assert all(str(r.get("alignment_kind", "")) in {"rule_fallback_same_family", "same_as_main_skill", "anchor_subskill_match"} for r in targeted)
    sem = out.get("semantic_alignment") or {}
    sq = sem.get("source_quality_reject_examples") or []
    # Under database cleanup (4431 deleted) and Non-Destructive Salvage (4446 & 4515 salvaged), rejects are empty/reduced
    assert 4431 not in [r.get("example_id") for r in rows]
    assert len(sq) < 3
    specs = [s for s in (out.get("induced_problem_type_specs") or []) if isinstance(s, dict)]
    ids = [str(s.get("problem_type_id", "")) for s in specs]
    assert "numeric_numeric_evaluate_function_notation_short_answer" in ids
    assert not any("coordinate_point" in x for x in ids)
    ex_gate = out.get("exception_review_gate") or {}
    reasons = ex_gate.get("reasons") or []
    assert "majority_needs_review" not in reasons
    assert "semantic_alignment_blocked" not in reasons

