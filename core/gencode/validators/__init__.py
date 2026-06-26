from __future__ import annotations

from typing import Any

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.validators.answer_contract_validator import validate_answer_contract
from core.gencode.validators.condition_target_dependency import validate_condition_target_dependency
from core.gencode.validators.semantic_validator import (
    validate_dependency_contract,
    validate_semantic_and_dependency,
    validate_semantic_contract,
)


def validate_generator_payload(
    payload: dict[str, Any],
    *,
    skill_id: str | None = None,
    problem_type_spec: dict[str, Any] | None = None,
) -> list[str]:
    spec = problem_type_spec
    if spec is None:
        sid = str(skill_id or payload.get("skill_id", "")).strip()
        pt = str(payload.get("problem_type_id", "")).strip()
        spec = load_problem_type_spec(sid, pt, prefer="auto")
    if not spec:
        return ["problem_type_spec_missing"]
    errors = validate_answer_contract(payload, spec)
    from core.gencode.answer_payload import validate_answer_contract_consistency
    errors.extend(validate_answer_contract_consistency(payload.get("answer_contract") or {}))
    errors.extend(validate_dependency_contract(payload, spec))
    errors.extend(validate_semantic_contract(payload, spec))

    # --- Six Generic Verification Gates ---
    # 1. SOURCE_FIDELITY: Graph drawing tasks must not be degraded to value reading
    problem_type_id = str(payload.get("problem_type_id") or "").strip()
    question_text = str(payload.get("question_text") or "").strip()
    if problem_type_id == "frequency_distribution_chart_construction":
        is_degraded = False
        if payload.get("answer_type") == "integer":
            is_degraded = True
        elif str(payload.get("correct_answer") or "").isdigit():
            is_degraded = True
        elif "求" in question_text and "次數" in question_text:
            is_degraded = True
        if is_degraded:
            errors.append("SOURCE_FIDELITY: chart construction task must not be degraded to value reading")

    # 2. ANSWER_DEPENDENCY_COMPLETENESS: Visual payload must be present when required
    requires_visual = bool(spec.get("requires_visual", False) or spec.get("metadata", {}).get("requires_visual", False) or "chart" in problem_type_id or "histogram" in problem_type_id or "polygon" in problem_type_id)
    if requires_visual:
        visual_aids = payload.get("visual_aids", [])
        image_base64 = payload.get("image_base64", "")
        if not visual_aids and not image_base64:
            errors.append("ANSWER_DEPENDENCY_COMPLETENESS: visual payload (visual_aids/image_base64) must be generated")

    # 3. EXISTING_VISUAL_CONTRACT_COMPLIANCE: Check image format compliance
    if requires_visual:
        visual_aids = payload.get("visual_aids", [])
        image_base64 = payload.get("image_base64", "")
        has_b64 = False
        if isinstance(image_base64, str) and image_base64.strip():
            has_b64 = True
        elif isinstance(visual_aids, list):
            has_b64 = any(isinstance(x, dict) and x.get("type") == "image/png" and x.get("value") for x in visual_aids)
        if not has_b64:
            errors.append("EXISTING_VISUAL_CONTRACT_COMPLIANCE: visual payload must comply with image_base64/png base64 payload format")

    # 4. SCAFFOLD_NOT_PUBLISHABLE: Do not publish generic AST scaffolds
    metadata = payload.get("metadata", {})
    givens = metadata.get("givens", {})
    categories = givens.get("categories", [])
    is_generic = False
    if categories == ["A組", "B組", "C組", "D組"]:
        is_generic = True
    elif "A組" in question_text and "B組" in question_text and "C組" in question_text and "D組" in question_text:
        background_keywords = ["模擬考", "體重", "國貿", "會計", "女中", "成績", "班"]
        if not any(k in question_text for k in background_keywords):
            is_generic = True
    if is_generic:
        errors.append("SCAFFOLD_NOT_PUBLISHABLE: generic scaffold with placeholder categories ['A組', 'B組', 'C組', 'D組'] cannot be published")

    # 5. MISSING_SOURCE_ASSET: Reject if missing asset and cannot be reconstructed
    if spec.get("missing_docx_image_asset") and not image_base64 and not visual_aids:
         errors.append("MISSING_SOURCE_ASSET: missing textbook image and cannot reconstruct")

    # 6. CHART_DATA_CONSISTENCY: Verify table categories/frequencies match between givens and visual_spec
    visual_spec = payload.get("visual_spec", {})
    if isinstance(visual_spec, dict) and visual_spec.get("type") == "table":
        rows = visual_spec.get("rows", [])
        givens_map = givens.get("frequency_map", {})
        givens_categories = list(givens.get("categories") or [])
        visual_categories = [row[0] for row in rows if len(row) >= 1]
        if givens_categories and visual_categories != givens_categories:
            errors.append("CHART_DATA_CONSISTENCY: visual table categories do not match givens categories")
        if givens_map:
            for row in rows:
                if len(row) == 2:
                    k, v = row[0], row[1]
                    import re
                    normalized_v = int(re.search(r'\d+', str(v)).group()) if re.search(r'\d+', str(v)) else None
                    if k in givens_map and normalized_v is not None and givens_map[k] != normalized_v:
                        errors.append("CHART_DATA_CONSISTENCY: visual table frequency does not match givens frequency map")

    # 7. REQUIRED_VISUAL_ASSET_MISSING: cumulative freq polygon ops MUST carry at least one visual asset
    _CUMULATIVE_POLYGON_OPS = frozenset({
        "cumulative_above_fail_count",
        "cumulative_above_interval_count",
        "cumulative_below_interval_count",
        "cumulative_frequency_graph_reading",
        "less_than_cumulative_frequency_reading",
        "greater_than_cumulative_frequency_reading",
    })
    if problem_type_id in _CUMULATIVE_POLYGON_OPS:
        has_any_visual = (
            bool(payload.get("image_base64", ""))
            or bool(payload.get("image_url", ""))
            or bool(payload.get("visual_spec"))
            or bool(payload.get("visual_aids"))
        )
        if not has_any_visual:
            errors.append(
                "REQUIRED_VISUAL_ASSET_MISSING: cumulative frequency polygon question must provide "
                "image_base64, image_url, visual_spec, or visual_aids"
            )

    # 8. CUMULATIVE_SEMANTIC_MISMATCH: cumulative stems must not map to frequency polygon
    _CUMULATIVE_STEM_MARKERS = ("累積", "累積次數", "cumulative")
    if any(marker in question_text for marker in _CUMULATIVE_STEM_MARKERS):
        if problem_type_id == "frequency_polygon_reading":
            errors.append(
                "CUMULATIVE_SEMANTIC_MISMATCH: cumulative frequency stem cannot use frequency_polygon_reading"
            )
        if problem_type_id == "frequency_table_construction_review" and "累積" in question_text:
            errors.append(
                "CUMULATIVE_SEMANTIC_MISMATCH: cumulative frequency stem cannot use frequency_table_construction_review"
            )

    from core.gencode.validators.cumulative_frequency_validator import validate_cumulative_frequency_payload

    _CUMULATIVE_FREQ_OPS = frozenset(
        {
            "cumulative_frequency_graph_reading",
            "less_than_cumulative_frequency_reading",
            "greater_than_cumulative_frequency_reading",
            "class_frequency_from_cumulative_difference",
            "cumulative_frequency_table_construction",
            "cumulative_above_fail_count",
            "cumulative_above_interval_count",
            "cumulative_below_interval_count",
        }
    )
    if problem_type_id in _CUMULATIVE_FREQ_OPS or str(payload.get("domain_operation") or "") in _CUMULATIVE_FREQ_OPS:
        errors.extend(validate_cumulative_frequency_payload(payload))

    from core.gencode.validators.descriptive_statistics_validator import validate_descriptive_statistics_payload

    errors.extend(validate_descriptive_statistics_payload(payload))

    # Run SemanticChecker Base check
    import json
    from validators.semantic_checker import SemanticChecker
    checker = SemanticChecker()
    ok, err_detail = checker.check_semantic(payload, spec)
    if not ok:
        errors.append(f"generator_semantically_unsafe:{json.dumps(err_detail, ensure_ascii=False)}")
        
    return sorted(set(errors))


from core.gencode.validators.source_isomorphism_validator import validate_source_isomorphism


__all__ = [
    "validate_answer_contract",
    "validate_condition_target_dependency",
    "validate_dependency_contract",
    "validate_semantic_and_dependency",
    "validate_semantic_contract",
    "validate_generator_payload",
    "validate_source_isomorphism",
]
