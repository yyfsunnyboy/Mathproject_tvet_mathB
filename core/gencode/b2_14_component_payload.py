"""Registry-dispatched Phase-2 assembly for B2 section 1-4 components."""
from __future__ import annotations
from copy import deepcopy
import importlib
from typing import Any
import sympy as sp

from core.registry.domain_operation_registry import get_domain_spec, get_operation_spec

DOMAIN_KEY="trigonometry.function_graph"

def _canonical(value:Any)->str:
    return sp.sstr(sp.simplify(value)) if isinstance(value,sp.Basic) else str(value)

def _dispatch(call:dict[str,Any],seed:int|None)->tuple[dict[str,Any],dict[str,Any]]:
    operation=str(call["operation"]); domain=get_domain_spec(DOMAIN_KEY); op=get_operation_spec(DOMAIN_KEY,operation)
    if domain is None or op is None or not op.payload_adapter: raise ValueError(f"unregistered_b2_14_operation:{operation}")
    module=importlib.import_module(domain.domain_module); builder=getattr(module,op.handler)
    matrix=builder(seed=seed,domain_operation=operation,constraints=deepcopy(call.get("constraints") or {}))
    adapter_module,adapter_name=op.payload_adapter.rsplit(".",1)
    adapter_matrix={key:value for key,value in matrix.items() if key!="domain_result"}
    adapted=getattr(importlib.import_module(adapter_module),adapter_name)(adapter_matrix,domain_operation=operation,seed=seed)
    return matrix,adapted

def _part(call:dict[str,Any],matrix:dict[str,Any],source_key:str,key:str)->dict[str,Any]:
    operation=str(call["operation"]); result=matrix.get("domain_result") or {}
    value=result.get(source_key) if isinstance(result,dict) else None
    if value is None: value=(matrix.get("answer",{}).get("parts") or {}).get(source_key)
    if value is None: raise ValueError(f"missing_domain_output:{operation}:{source_key}")
    checker,equiv="expression_checker","algebraic_equivalent"
    extra:dict[str,Any]={}
    if operation=="compare_trig_values_by_monotonicity": checker,equiv="ordered_inequality_checker","ordered_inequality"; extra["required_form"]="ordered_inequality"
    elif operation=="evaluate_trig_decimal": checker,equiv="decimal_tolerance_checker","decimal_tolerance"; extra.update({"precision":6,"rounding_policy":"ROUND_HALF_UP","tolerance":"0.0000005"})
    elif operation=="count_sine_cosine_intersections": checker,equiv="expression_checker","algebraic_equivalent"
    if source_key=="period": extra["required_form"]="positive_minimum_period"
    return {"key":key,"field_key":key,"label":key,"expected_answer":_canonical(value),"checker":checker,"checker_key":checker,"equivalence_type":equiv,**extra}

def generate_b2_14_component_payload(*,spec:dict[str,Any],textbook_example_id:int,seed:int|None,component_id:str)->dict[str,Any]:
    children=[_dispatch(call,seed) for call in spec["calls"]]
    payload=deepcopy(children[0][1]); parts=[]
    for call,(matrix,_adapted) in zip(spec["calls"],children):
        parts.extend(_part(call,matrix,str(row["source_key"]),str(row["key"])) for row in call.get("outputs") or [])
    answer_type=str(spec["answer_type"]); choices=deepcopy(spec.get("choices") or [])
    if answer_type=="single_choice":
        raw=parts[0]["expected_answer"]
        canonical=str((spec.get("choice_key_to_value") or {}).get(raw,raw))
        mode="single_choice"; contract={"presentation_mode":mode,"answer_type":"single_choice","answer_shape":"single_choice","checker":"choice_label_checker","checker_key":"choice_label_checker","answer_equivalence":"choice_label","equivalence_type":"choice_label","semantic_answer":canonical,"semantic_canonical_answer":canonical,"choices":choices,"fixed_domain_key":DOMAIN_KEY}
        payload["choices"]=choices
    elif answer_type=="short_answer":
        if len(parts)!=1: raise ValueError("short_answer_requires_one_domain_output")
        canonical=parts[0]["expected_answer"]; mode="short_answer"; contract={"presentation_mode":mode,"answer_type":"short_answer","answer_shape":"scalar","checker":parts[0]["checker"],"checker_key":parts[0]["checker_key"],"answer_equivalence":parts[0]["equivalence_type"],"equivalence_type":parts[0]["equivalence_type"],"canonical_answer":canonical,"fixed_domain_key":DOMAIN_KEY,**({"required_form":parts[0]["required_form"]} if parts[0].get("required_form") else {})}
    else:
        canonical={part["key"]:part["expected_answer"] for part in parts}; mode="multiple_inputs"; contract={"presentation_mode":mode,"answer_type":"multi_part","answer_shape":"multi_part","checker":"multi_part_answer_checker","checker_key":"multi_part_answer_checker","answer_equivalence":"multi_part_answer","equivalence_type":"multi_part_answer","parts":parts,"fixed_domain_key":DOMAIN_KEY}
    payload.update({"skill_id":str(spec["skill_id"]),"component_id":component_id,"generator_key":component_id,"textbook_example_id":textbook_example_id,"problem_type_id":str(spec["operation"]),"domain_operation":str(spec["operation"]),"source_kind":"example" if spec["oracle_source"]=="source_provided" else "exercise","question_text":str(spec["question"]),"question":str(spec["question"]),"answer":canonical,"correct_answer":canonical,"display_answer":str(canonical),"presentation_mode":mode,"answer_type":answer_type,"checker":contract["checker"],"checker_key":contract["checker_key"],"equivalence":contract["equivalence_type"],"equivalence_type":contract["equivalence_type"],"answer_contract":contract})
    metadata={"skill_id":str(spec["skill_id"]),"component_id":component_id,"textbook_example_id":textbook_example_id,"domain_operation":str(spec["operation"]),"source_fidelity":"pass","oracle_source":str(spec["oracle_source"]),"exact_capability_readiness":"pass","generator_readiness":"verified"}
    visual=str(spec.get("visual_asset") or "")
    if visual:
        metadata["source_visual_asset"]=visual
        payload["visual_spec"]={"kind":"image","required":True,"asset_path":visual,"alt":"教材作答必要圖形","usage":"practice_scratchpad_background"}
        payload["visual_aids"]=[payload["visual_spec"]]
        payload["visual_response_contract"]={"source_visual_required":True,"drawing_subtask":True,"reference_asset":visual,"rubric_authority":"source_visual_reference","auto_grade_drawing":False}
    payload["metadata"]=metadata
    return payload

def get_b2_14_hint(payload:dict[str,Any]|None=None,*,stage:int=1,**_:Any)->str:
    operation=str(((payload or {}).get("metadata") or {}).get("domain_operation") or "")
    hints={"compare_trig_values_by_monotonicity":"先將不同三角函數化為可在同一單調區間比較的形式。","solve_trig_value_quadratic_constraint":"令三角函數值為 t，解二次式後再套用函數值域。","analyze_affine_transformed_trig_graph":"依來源圖辨認平移或伸縮，再由共用圖形性質求週期與極值。","calculate_trig_period_from_argument_scale":"取基本週期除以參數係數的絕對值。","classify_trig_expression_sign_change":"先正規化角度區間，再判斷象限符號與單調方向。","classify_trig_equation_feasibility":"先檢查右側數值是否落在該三角函數值域。","analyze_tangent_absolute_graph_period":"保留正切函數定義域與漸近線，再判斷絕對值轉換後的最小正週期。","evaluate_trig_decimal":"先合併度、分，再按指定精度四捨五入。","count_sine_cosine_intersections":"使用精確通解並逐一篩選封閉區間端點。"}
    return hints.get(operation,"依題意呼叫共用精確三角函數能力。")
