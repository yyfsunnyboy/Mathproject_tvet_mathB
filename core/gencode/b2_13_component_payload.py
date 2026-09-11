"""Thin Phase-2 assembly for B2 1-3 components."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.domain.trigonometry_arbitrary_domain import build_trigonometry_arbitrary_matrix, canonical_exact, complete_reference_angle_conversion
from core.gencode.b2_12_capability_adapter import adapt_b2_12_batch1_matrix
from core.gencode.b2_13_capability_adapter import adapt_b2_13_arbitrary_matrix


def _build_call(call: dict[str, Any], seed: int | None) -> dict[str, Any]:
    operation = str(call["operation"])
    constraints = deepcopy(call.get("constraints") or {})
    matrix = build_trigonometry_arbitrary_matrix(seed=seed, domain_operation=operation, constraints=constraints)
    if operation == "simplify_fundamental_trig_expression":
        return adapt_b2_12_batch1_matrix(matrix, domain_operation=operation, seed=seed)
    return adapt_b2_13_arbitrary_matrix(matrix, domain_operation=operation, seed=seed)


def _parts(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    contract = payload.get("answer_contract") or {}
    rows = contract.get("parts") if isinstance(contract.get("parts"), list) else []
    return {str(row.get("key")): dict(row) for row in rows if isinstance(row, dict) and row.get("key")}


def _scalar(payload: dict[str, Any]) -> dict[str, Any]:
    contract = payload.get("answer_contract") or {}
    return {"expected_answer": payload.get("correct_answer", payload.get("answer")), "checker": contract.get("checker", "expression_checker"), "checker_key": contract.get("checker_key", contract.get("checker", "expression_checker")), "equivalence_type": contract.get("equivalence_type", "algebraic_equivalent")}


def _selected_parts(call: dict[str, Any], payload: dict[str, Any]) -> list[dict[str, Any]]:
    available = _parts(payload)
    outputs = list(call.get("outputs") or [])
    if not outputs:
        outputs = [{"source_key": key, "key": key, "label": key} for key in available] or [{"key": "value"}]
    selected = []
    for index, output in enumerate(outputs):
        source = str(output.get("source_key") or "")
        part = dict(available[source]) if source in available else _scalar(payload)
        key = str(output.get("key") or source or f"part_{index+1}")
        part.update({"key": key, "field_key": key, "label": str(output.get("label") or key)})
        if call.get("operation") == "classify_standard_position_angle":
            part.update({
                "checker": "text_checker",
                "checker_key": "text_checker",
                "equivalence_type": "exact_text",
            })
        selected.append(part)
    return selected


def _table_contract(items: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    rows = complete_reference_angle_conversion(items)
    parts, table_rows, canonical = [], [], {}
    for index, row in enumerate(rows, 1):
        ref_key, sign_key = f"reference_{index}", f"sign_{index}"
        reference, sign = canonical_exact(row["reference_degrees"]), str(row["sign"])
        parts.extend([
            {"key":ref_key,"field_key":ref_key,"label":f"第{index}列參考角","expected_answer":reference,"checker":"expression_checker","checker_key":"expression_checker","equivalence_type":"algebraic_equivalent"},
            {"key":sign_key,"field_key":sign_key,"label":f"第{index}列正負號","expected_answer":sign,"checker":"integer_checker","checker_key":"integer_checker","equivalence_type":"numeric_exact"},
        ])
        canonical.update({ref_key:reference,sign_key:sign})
        table_rows.append({"function":row["function"],"field_keys":[ref_key,sign_key]})
    contract = {"presentation_mode":"table_fill","answer_type":"table_fill","answer_shape":"table_fill","checker":"table_fill_checker","checker_key":"table_fill_checker","answer_equivalence":"multi_part_answer","equivalence_type":"multi_part_answer","parts":parts,"blank_cells":table_rows,"fixed_domain_key":"trigonometry.arbitrary_angle","required_form":"reference_angle_and_sign"}
    return canonical, contract


def generate_b2_13_component_payload(*, spec: dict[str, Any], textbook_example_id: int, seed: int | None, component_id: str) -> dict[str, Any]:
    answer_type, calls = str(spec["answer_type"]), list(spec["calls"])
    children = [_build_call(call, seed) for call in calls]
    payload = deepcopy(children[0])
    if answer_type == "table_fill":
        canonical, contract = _table_contract(list(calls[0]["constraints"]["items"]))
        mode = "table_fill"
    elif answer_type == "single_choice":
        canonical, mode = str(spec["semantic_answer"]), "single_choice"
        contract = {"presentation_mode":mode,"answer_type":answer_type,"answer_shape":"single_choice","checker":"choice_label_checker","checker_key":"choice_label_checker","answer_equivalence":"choice_label","equivalence_type":"choice_label","semantic_answer":canonical,"semantic_canonical_answer":canonical,"choices":deepcopy(spec["choices"]),"fixed_domain_key":"trigonometry.arbitrary_angle"}
        payload["choices"] = deepcopy(spec["choices"])
    else:
        parts = []
        for call, child in zip(calls, children):
            parts.extend(_selected_parts(call, child))
        if answer_type == "short_answer":
            if len(parts) != 1:
                raise ValueError("short_answer_requires_one_domain_output")
            canonical, mode = parts[0]["expected_answer"], "short_answer"
            contract = {"presentation_mode":mode,"answer_type":answer_type,"answer_shape":"scalar","checker":"expression_checker","checker_key":"expression_checker","answer_equivalence":"algebraic_equivalent","equivalence_type":"algebraic_equivalent","canonical_answer":canonical,"fixed_domain_key":"trigonometry.arbitrary_angle"}
        else:
            canonical, mode = {str(part["key"]):part["expected_answer"] for part in parts}, "multiple_inputs"
            contract = {"presentation_mode":mode,"answer_type":"multi_part","answer_shape":"multi_part","checker":"multi_part_answer_checker","checker_key":"multi_part_answer_checker","answer_equivalence":"multi_part_answer","equivalence_type":"multi_part_answer","parts":parts,"fixed_domain_key":"trigonometry.arbitrary_angle"}
    payload.update({"skill_id":str(spec["skill_id"]),"component_id":component_id,"generator_key":component_id,"textbook_example_id":textbook_example_id,"problem_type_id":str(spec["operation"]),"domain_operation":str(spec["operation"]),"source_kind":"example" if spec["oracle_source"]=="source_provided" else "exercise","question_text":str(spec["question"]),"question":str(spec["question"]),"answer":canonical,"correct_answer":canonical,"display_answer":str(canonical),"presentation_mode":mode,"answer_type":answer_type,"checker":contract["checker"],"checker_key":contract["checker_key"],"equivalence":contract["equivalence_type"],"equivalence_type":contract["equivalence_type"],"answer_contract":contract})
    metadata = dict(payload.get("metadata") or {})
    metadata.update({"skill_id":str(spec["skill_id"]),"component_id":component_id,"textbook_example_id":textbook_example_id,"domain_operation":str(spec["operation"]),"source_fidelity":"pass","oracle_source":str(spec["oracle_source"]),"exact_capability_readiness":"pass","generator_readiness":"verified"})
    payload["metadata"] = metadata
    return payload


def get_b2_13_hint(payload: dict[str, Any] | None = None, *, stage: int = 1, **_: Any) -> str:
    operation = str(((payload or {}).get("metadata") or {}).get("domain_operation") or "")
    hints = {"classify_standard_position_angle":"先將角正規化，再判斷終邊所在座標軸或象限。","compute_terminal_ray_trig_ratios":"由終邊點與原點的距離建立精確三角比。","solve_signed_trig_constraints":"先由符號確定唯一象限，再套用基本恆等式。","evaluate_exact_arbitrary_angle_trig_expression":"先化為同界角及參考角，再使用精確特殊角值。","complete_reference_angle_conversion":"逐列辨認參考角與該三角函數的正負號。","classify_trig_derived_point_quadrant":"先判斷衍生點兩座標的正負，再決定象限。","solve_arbitrary_angle_vertical_projection":"把任意角化為參考角，注意垂直投影的正負。","simplify_fundamental_trig_expression":"先用角度轉換關係，再以基本三角恆等式化簡。"}
    return hints.get(operation,"依題目條件呼叫共用精確三角運算，逐步整理結果。")
