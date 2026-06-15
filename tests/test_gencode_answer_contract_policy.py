from __future__ import annotations

from unittest.mock import patch

from core.gencode.answer_contract_policy import infer_answer_contract_from_problem_context
from core.gencode.checker_registry import (
    CHECKER_CAPABILITIES,
    validate_answer_contract_capability,
)
from core.gencode.problem_type_induction import induce_problem_types_from_examples


def test_numeric_task_uses_numeric_checker_not_text():
    ac = infer_answer_contract_from_problem_context(
        answer_type="numeric",
        target_task="compute_value",
        math_objects=[],
    )
    assert ac["checker"] in {"integer_checker", "numeric_checker"}
    assert ac["checker"] != "text_checker"
    assert ac["answer_equivalence"] not in {"exact_text", "exact_string"}
    cap = validate_answer_contract_capability(ac)
    assert cap["checker_capability_status"] != "blocked"


def test_radical_distance_uses_expression_checker():
    ac = infer_answer_contract_from_problem_context(
        answer_type="short_answer",
        target_task="compute_distance_between_two_points",
        task_family="distance_between_two_points_family",
        math_objects=["distance_formula", "segment_length"],
        cluster_features=[{"answer": "\\sqrt{13}"}],
    )
    assert ac["answer_type"] == "numeric_or_radical"
    assert ac["checker"] == "expression_equivalence_checker"
    assert ac["answer_equivalence"] in {"math_expression_equivalence", "radical_equivalence"}
    cap = validate_answer_contract_capability(ac)
    assert cap["checker_capability_status"] == "ok"


def test_radical_checker_missing_blocks_when_requested():
    ac = {
        "answer_type": "numeric_or_radical",
        "answer_equivalence": "radical_equivalence",
        "checker": "radical_equivalence_checker",
    }
    cap = validate_answer_contract_capability(ac)
    assert cap["checker_capability_status"] == "blocked"
    assert "checker_contract_missing" in cap["checker_contract_blockers"]


def test_solution_set_contract():
    ac = infer_answer_contract_from_problem_context(
        answer_type="short_answer",
        target_task="solve_unknown_coordinate_from_two_point_distance",
        math_objects=["unknown_coordinate"],
    )
    assert ac["checker"] == "solution_set_checker"
    assert ac["answer_equivalence"] == "unordered_solution_set"
    assert ac["answer_type"] == "solution_set"


def test_interval_contract():
    ac = infer_answer_contract_from_problem_context(
        answer_type="short_answer",
        target_task="solve_absolute_value_inequality",
        task_family="absolute_value_inequality_family",
    )
    assert ac["checker"] == "interval_checker"
    assert ac["answer_type"] == "interval"


def test_classify_quadrant_uses_quadrant_checker():
    ac = infer_answer_contract_from_problem_context(
        answer_type="short_answer",
        target_task="classify_quadrant",
        task_family="classify_quadrant_family",
    )
    assert ac["checker"] == "quadrant_checker"
    assert ac["answer_equivalence"] == "normalized_label"
    assert ac["answer_equivalence"] != "exact_string"


def test_choice_contract():
    ac = infer_answer_contract_from_problem_context(
        answer_type="single_choice",
        target_task="choose_correct_statement",
        has_choices=True,
    )
    assert ac["checker"] == "choice_label_checker"


def test_distance_skill_induction_not_text_checker():
    skill_id = "mock_distance_contract"
    examples = [
        {
            "id": 1,
            "example_id": 1,
            "skill_id": skill_id,
            "problem_text": r"設 A(1,2)、B(4,6)，求 \overline{AB} 的長度。",
            "correct_answer": "5",
        },
        {
            "id": 2,
            "example_id": 2,
            "skill_id": skill_id,
            "problem_text": r"設 A(k,-5)、B(2,7) 為坐標平面上兩點，且 \overline{AB}=13，試求 k 值。",
            "correct_answer": "-3,7",
        },
    ]
    meta = {"skill_ch_name": "平面上兩點間的距離", "skill_en_name": "Distance"}
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        out = induce_problem_types_from_examples(skill_id, examples)
    for c in out.get("candidate_problem_types") or []:
        ck = c.get("checker_key_proposal", "")
        eq = c.get("equivalence_type_proposal", "")
        pt = c.get("problem_type_id", "")
        assert ck != "text_checker" or "classify" in pt
        if "compute_distance" in pt:
            assert ck in {"expression_equivalence_checker", "numeric_checker", "integer_checker"}
            assert eq not in {"exact_string"}
        if "solve_unknown" in pt:
            assert ck == "solution_set_checker"


def test_phase2_blocks_unsupported_radical_checker():
    from core.gencode import pipeline_orchestrator as po
    from core.gencode.pipeline_orchestrator import run_gencode_phase2
    import json
    import tempfile
    from pathlib import Path

    skill_id = "mock_radical_block"
    phase1 = {
        "source_alignment_status": "pass",
        "alignment_blockers": [],
        "candidate_problem_types": [
            {
                "problem_type_id": "short_answer_numeric_or_radical",
                "matched_example_count": 2,
                "answer_contract_proposal": {
                    "answer_type": "numeric_or_radical",
                    "checker": "radical_equivalence_checker",
                    "answer_equivalence": "radical_equivalence",
                },
                "checker_key_proposal": "radical_equivalence_checker",
                "equivalence_type_proposal": "radical_equivalence",
                "spec_source": "phase1_induced_draft",
                "generator_readiness": "runtime_ready",
                "problem_type_spec_draft": {
                    "answer_contract": {
                        "answer_type": "numeric_or_radical",
                        "checker": "radical_equivalence_checker",
                        "answer_equivalence": "radical_equivalence",
                    },
                },
            }
        ],
    }
    with tempfile.TemporaryDirectory() as td:
        report_dir = Path(td)
        (report_dir / f"{skill_id}_phase1_summary.json").write_text(
            json.dumps(phase1, ensure_ascii=False),
            encoding="utf-8",
        )
        from core.gencode import pipeline_state as ps
        with patch.object(po, "REPORT_DIR", report_dir), \
             patch.object(ps, "GENCODE_REPORT_DIR", report_dir), \
             patch.object(ps, "GENCODE_DRAFT_DIR", report_dir / "drafts"):
            out = run_gencode_phase2(skill_id, dry_run=True)
    row = (out.get("generator_results") or [{}])[0]
    assert row.get("generator_status") == "blocked"
    assert "checker_contract_missing" in (row.get("blockers") or [])


def test_registry_has_core_checkers():
    assert CHECKER_CAPABILITIES["solution_set_checker"]["runtime_available"]
    assert not CHECKER_CAPABILITIES["radical_equivalence_checker"]["runtime_available"]
