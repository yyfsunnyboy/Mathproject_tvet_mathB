from __future__ import annotations

from unittest.mock import patch

from core.gencode.induction_source_policy import (
    classify_induction_source_tier,
    detect_enrichment_reasons,
    split_induction_source_features,
)
from core.gencode.main_skill_anchor import build_main_skill_anchor
from core.gencode.problem_type_induction import induce_problem_types_from_examples
from core.gencode.task_families import FUNCTION_CONCEPT_FAMILY


def _ex(ex_id: int, stem: str, skill_id: str = "vh_數學B1_FunctionConcept") -> dict:
    return {
        "id": ex_id,
        "example_id": ex_id,
        "skill_id": skill_id,
        "problem_text": stem,
        "correct_answer": "1",
    }


STEM_GALILEO = (
    "伽利略（Galileo，1564−1642）研究自由落體運動發現自由落體公式："
    "$S\\left( t \\right)=\\frac{1}{2}g{{t}^{2}}$，當時間t改變時，落下距離S也跟著改變，所以距離S是時間t的函數。"
)

STEM_MIXED_SDG = (
    "英國科學家虎克（Robert Hooke，1635−1703）於1678年發現虎克定律：$F\\left( x \\right)=kx$。"
    "▲圖21\n數學檔案\n尤拉（Leonhard Euler，1707-1783）是最早使用函數記號的數學家。"
    "SDG 7可負擔的潔淨能源\n電費分為「夏季電費」和「非夏季電費」，"
    "$f\\left( x \\right)=\\left\\{ \\begin{align} & 1.63x,x\\le 120 \\end{align} \\right.$"
    "試求小蕙的電費9月比8月省下多少元。"
)

STEM_CORE_FUNCTION = "下列對應關係中，何者為函數？A→1，B→2，C→2，D→3"


def test_galileo_and_sdg_stems_detected_as_enrichment():
    assert "historical_narrative" in detect_enrichment_reasons(example=_ex(4430, STEM_GALILEO))
    reasons = detect_enrichment_reasons(example=_ex(4431, STEM_MIXED_SDG))
    assert "sdgs" in reasons
    assert "math_file" in reasons
    assert "piecewise_application" in reasons


def test_function_concept_anchor_uses_function_family():
    anchor = build_main_skill_anchor(
        "vh_數學B1_FunctionConcept",
        {"skill_ch_name": "函數的概念", "skill_en_name": "FunctionConcept", "chapter": "1 坐標系與函數圖形"},
    )
    assert FUNCTION_CONCEPT_FAMILY in anchor.get("expected_task_families", [])
    assert "judge_function_relation" in anchor.get("expected_subskill_candidates", [])


def test_only_enrichment_examples_yield_low_core_not_majority_needs_review():
    examples = [_ex(4430, STEM_GALILEO), _ex(4431, STEM_MIXED_SDG)]
    meta = {"skill_ch_name": "函數的概念", "skill_en_name": "FunctionConcept", "chapter": "1 坐標系與函數圖形"}
    with patch("core.gencode.problem_type_induction.load_skill_metadata_from_db", return_value=meta):
        with patch("core.gencode.classification_policy.classify_example_semantics_with_ai") as mock_ai:
            mock_ai.return_value = {
                "best_candidate_id": "needs_review",
                "target_task": "",
                "task_family": "",
                "candidate_source": "needs_review",
                "confidence": 0.0,
                "available": False,
                "requires_human_action": True,
            }
            out = induce_problem_types_from_examples(
                "vh_數學B1_FunctionConcept",
                examples,
                spec_mode="ai_first_induce_from_sources",
            )
    blockers = out.get("alignment_blockers") or []
    assert "low_core_source_examples" in blockers
    assert "majority_needs_review" not in blockers
    skipped = out.get("skipped_enrichment_examples") or []
    ids = {row.get("example_id") for row in skipped}
    assert ids == {4430, 4431}
    assert len(out.get("future_ai_judged_candidates") or []) >= 1
    assert len(out.get("contextual_application_sources") or []) >= 1


def test_core_short_example_not_enrichment():
    tier = classify_induction_source_tier(example=_ex(99, STEM_CORE_FUNCTION))
    assert tier["induction_tier"] == "core"
    core, report = split_induction_source_features(
        [{"source_example_id": 99, "question_text": STEM_CORE_FUNCTION}],
        examples=[_ex(99, STEM_CORE_FUNCTION)],
    )
    assert len(core) == 1
    assert report["core_example_count"] == 1
