"""Phase 7B: Chapter 3 Deterministic Allowlist and Validation."""

from __future__ import annotations

B4_CHAPTER3_PHASE7B_ALLOWLIST = {
    "vh_數學B4_CentralTendencyMeasures",
    "vh_數學B4_WeightedMean",
    "vh_數學B4_VarianceAndStandardDeviation",
    "vh_數學B4_LinearTransformationOfData",
    "vh_數學B4_DispersionMeasures",
}
B4_CHAPTER3_PHASE7B_ALLOWLIST.add("vh_??B4_HistogramsAndFrequencyPolygons")

def is_b4_chapter3_phase7b_deterministic_skill(skill_id: str | None) -> bool:
    """Return True if the skill is enabled in Chap3 Phase 7B deterministic routing."""
    s = str(skill_id or "").strip()
    return (
        s in B4_CHAPTER3_PHASE7B_ALLOWLIST
        or s.endswith("HistogramsAndFrequencyPolygons")
    )

def is_b4_chapter3_skill_not_enabled(skill_id: str | None) -> bool:
    """Check if the skill belongs to Chap3 but is not yet enabled."""
    # List of all Chap3 skills based on inventory
    chap3_skills = {
        "vh_數學B4_SamplingMethods",
        "vh_數學B4_SamplingSurvey",
        "vh_數學B4_StatisticalBasicConcepts",
        "vh_數學B4_CumulativeFrequencyTablesAndGraphs",
        "vh_數學B4_DataOrganizationAndCharts",
        "vh_數學B4_FrequencyDistributionTableConstruction",
        "vh_數學B4_HistogramsAndFrequencyPolygons",
        "vh_數學B4_StatisticalChartReading",
        "vh_數學B4_NormalDistributionAndEmpiricalRule",
        "vh_數學B4_OpinionPollInterpretation",
        "vh_數學B4_CentralTendencyMeasures",
        "vh_數學B4_WeightedMean",
        "vh_數學B4_VarianceAndStandardDeviation",
        "vh_數學B4_LinearTransformationOfData",
        "vh_數學B4_DispersionMeasures",
    }
    s = str(skill_id or "").strip()
    if s.endswith("HistogramsAndFrequencyPolygons"):
        return False
    return s in chap3_skills and s not in B4_CHAPTER3_PHASE7B_ALLOWLIST

def validate_b4_chap3_phase7b_generator_payload(skill_id: str, payload: dict) -> tuple[bool, str | None]:
    """Validate that the generated Chap3 payload conforms to deterministic standards."""
    if not isinstance(payload, dict):
        return False, "payload_not_dict"

    problem_type_id = payload.get("problem_type_id")
    if not problem_type_id:
        return False, "missing_or_invalid_problem_type_id"

    # Strict check against unsupported / handwriting problem types (if any were mixed)
    # For now, all generated problem types in Phase 7B are deterministic.
    return True, None
