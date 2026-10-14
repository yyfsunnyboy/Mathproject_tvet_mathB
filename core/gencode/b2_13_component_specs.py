"""Declarative source topology for the 29 Math B2 section 1-3 components."""
from __future__ import annotations

from typing import Any

S1="vh_數學B2_SubSection_1_3_1"; S2="vh_數學B2_SubSection_1_3_2"; S4="vh_數學B2_SubSection_1_3_4"
S5="vh_數學B2_SubSection_1_3_5"; S6="vh_數學B2_SubSection_1_3_6"; S7="vh_數學B2_SubSection_1_3_7"
CLASSIFY="classify_standard_position_angle"; RATIOS="compute_terminal_ray_trig_ratios"
SIGNED="solve_signed_trig_constraints"; EXACT="evaluate_exact_arbitrary_angle_trig_expression"
REFERENCE="complete_reference_angle_conversion"; DERIVED="classify_trig_derived_point_quadrant"
PROJECTION="solve_arbitrary_angle_vertical_projection"; SIMPLIFY="simplify_fundamental_trig_expression"

def call(operation: str, constraints: dict[str, Any], outputs: list[dict[str, str]]|None=None) -> dict[str, Any]:
    row={"operation":operation,"constraints":constraints}
    if outputs is not None: row["outputs"]=outputs
    return row

def out(source: str="", key: str="", label: str="") -> dict[str,str]:
    return {k:v for k,v in {"source_key":source,"key":key,"label":label}.items() if v}

def trig(fn: str, angle: Any, unit: str="degree") -> dict[str,Any]:
    return {"trig":fn,"angle":angle,"unit":unit}

def op2(name: str,a: Any,b: Any) -> dict[str,Any]: return {"op":name,"args":[a,b]}
def expr_call(node: Any, key="value", label="") -> dict[str,Any]: return call(EXACT,{"expression":node},[out("",key,label or key)])
def class_calls(items: list[tuple[Any,str]]) -> list[dict[str,Any]]:
    return [call(CLASSIFY,{"angle":a,"unit":u},[out("",f"part_{i}",f"({i})")]) for i,(a,u) in enumerate(items,1)]

SPECS: dict[int,dict[str,Any]] = {
11626:{"skill_id":S1,"answer_type":"multi_part","question":"試判斷下列標準位置角是象限角或是第幾象限角？ (1) 3π/2 (2) 855° (3) −135°","calls":class_calls([("3/2","pi_coefficient"),(855,"degree"),(-135,"degree")])},
11627:{"skill_id":S1,"answer_type":"multi_part","question":"試判斷下列標準位置角是象限角或是第幾象限角？ (1) π (2) 960° (3) −420°","calls":class_calls([(1,"pi_coefficient"),(960,"degree"),(-420,"degree")])},
11628:{"skill_id":S2,"answer_type":"multi_part","question":"設 P(−4,3) 為標準位置角 θ 終邊上的點，求 sinθ、cosθ、tanθ。","calls":[call(RATIOS,{"x":-4,"y":3})]},
11629:{"skill_id":S2,"answer_type":"multi_part","question":"設 P(−√3,−1) 為標準位置角 θ 終邊上的點，求 sinθ、cosθ、tanθ。","calls":[call(RATIOS,{"x":"-sqrt(3)","y":-1})]},
11630:{"skill_id":S4,"answer_type":"short_answer","question":"設 tanθ>0 且 cosθ<0，則 θ 為第幾象限角？","calls":[call(SIGNED,{"signs":{"tan":1,"cos":-1}},[out("quadrant","value","象限")])]},
11631:{"skill_id":S4,"answer_type":"short_answer","question":"設 sinθ<0 且 cosθ>0，則 θ 為第幾象限角？","calls":[call(SIGNED,{"signs":{"sin":-1,"cos":1}},[out("quadrant","value","象限")])]},
11632:{"skill_id":S4,"answer_type":"multi_part","question":"已知 sinθ=−5/13 且 tanθ>0，求 cosθ 與 tanθ。","calls":[call(SIGNED,{"known":{"sin":"-5/13"},"signs":{"tan":1},"targets":{"cos":"cos","tan":"tan"}})]},
11633:{"skill_id":S4,"answer_type":"multi_part","question":"已知 tanθ=−3/4 且 cosθ>0，求 sinθ 與 cosθ。","calls":[call(SIGNED,{"known":{"tan":"-3/4"},"signs":{"cos":1},"targets":{"sin":"sin","cos":"cos"}})]},
11634:{"skill_id":S5,"answer_type":"multi_part","question":"求值：(1) sin0°+cos0° (2) cos90°+tan²180° (3) cos360°/sin²270°","calls":[expr_call(op2("add",trig("sin",0),trig("cos",0)),"part_1","(1)"),expr_call(op2("add",trig("cos",90),op2("pow",trig("tan",180),2)),"part_2","(2)"),expr_call(op2("div",trig("cos",360),op2("pow",trig("sin",270),2)),"part_3","(3)")]},
11635:{"skill_id":S5,"answer_type":"multi_part","question":"求值：(1) sin90°−cos90° (2) cos²180° (3) tan²360°/sin270°","calls":[expr_call(op2("sub",trig("sin",90),trig("cos",90)),"part_1","(1)"),expr_call(op2("pow",trig("cos",180),2),"part_2","(2)"),expr_call(op2("div",op2("pow",trig("tan",360),2),trig("sin",270)),"part_3","(3)")]},
11636:{"skill_id":S6,"answer_type":"multi_part","question":"求 θ=120° 和 θ=210° 的 sin、cos、tan。","calls":[expr_call(trig(fn,a),f"{fn}_{a}",f"{fn}{a}°") for a in (120,210) for fn in ("sin","cos","tan")]},
11637:{"skill_id":S6,"answer_type":"multi_part","question":"求 θ=150° 和 θ=240° 的 sin、cos、tan。","calls":[expr_call(trig(fn,a),f"{fn}_{a}",f"{fn}{a}°") for a in (150,240) for fn in ("sin","cos","tan")]},
11638:{"skill_id":S6,"answer_type":"multi_part","question":"求 sin(−30°)、cos300°、tan(−135°)。","calls":[expr_call(trig("sin",-30),"part_1","sin(−30°)"),expr_call(trig("cos",300),"part_2","cos300°"),expr_call(trig("tan",-135),"part_3","tan(−135°)")]},
11639:{"skill_id":S6,"answer_type":"multi_part","question":"求 sin330°、cos(−45°)、tan(−240°)。","calls":[expr_call(trig("sin",330),"part_1","sin330°"),expr_call(trig("cos",-45),"part_2","cos(−45°)"),expr_call(trig("tan",-240),"part_3","tan(−240°)")]},
11640:{"skill_id":S7,"answer_type":"multi_part","question":"求值：(1) sin(−930°) (2) tan(19π/4)","calls":[expr_call(trig("sin",-930),"part_1","(1)"),expr_call(trig("tan","19/4","pi_coefficient"),"part_2","(2)")]},
11641:{"skill_id":S7,"answer_type":"multi_part","question":"求值：(1) cos(−495°) (2) tan(−17π/6)","calls":[expr_call(trig("cos",-495),"part_1","(1)"),expr_call(trig("tan","-17/6","pi_coefficient"),"part_2","(2)")]},
11642:{"skill_id":S7,"answer_type":"multi_part","question":"化簡：(1) cos(270°+θ)/sin(360°−θ) (2) sin(180°−θ)/sin(90°−θ)","calls":[call(SIMPLIFY,{"expressions":{"part_1":"cos(3*pi/2+theta)/sin(2*pi-theta)","part_2":"sin(pi-theta)/sin(pi/2-theta)"}})]},
11643:{"skill_id":S7,"answer_type":"multi_part","question":"化簡：(1) sin(270°−θ)/cos(180°+θ) (2) sin(360°−θ)/sin(90°+θ)","calls":[call(SIMPLIFY,{"expressions":{"part_1":"sin(3*pi/2-theta)/cos(pi+theta)","part_2":"sin(2*pi-theta)/sin(pi/2+theta)"}})]},
11644:{"skill_id":S7,"answer_type":"single_choice","question":"若 P(−99,87) 是 θ 終邊上一點，Q=(5sinθ−6cosθ, 7cosθ+8tanθ) 落在哪一象限？","calls":[call(DERIVED,{"source":{"kind":"terminal_point","x":-99,"y":87},"x_expression":op2("sub",op2("mul",5,"sin"),op2("mul",6,"cos")),"y_expression":op2("add",op2("mul",7,"cos"),op2("mul",8,"tan"))})],"choices":[{"label":"A","value":"第一象限"},{"label":"B","value":"第二象限"},{"label":"C","value":"第三象限"},{"label":"D","value":"第四象限"}],"semantic_answer":"第四象限"},
11645:{"skill_id":S1,"answer_type":"multi_part","question":"判斷：(1) 2π/3 (2) 630° (3) 1720° (4) −870° 的終邊位置。","calls":class_calls([("2/3","pi_coefficient"),(630,"degree"),(1720,"degree"),(-870,"degree")])},
11646:{"skill_id":S2,"answer_type":"multi_part","question":"設 P(2,−1) 為 θ 終邊上一點，求 sinθ、cosθ、tanθ。","calls":[call(RATIOS,{"x":2,"y":-1})]},
11647:{"skill_id":S4,"answer_type":"multi_part","question":"已知 cosθ=−4/5 且 tanθ<0，求 sinθ 與 tanθ。","calls":[call(SIGNED,{"known":{"cos":"-4/5"},"signs":{"tan":-1},"targets":{"sin":"sin","tan":"tan"}})]},
11648:{"skill_id":S5,"answer_type":"multi_part","question":"求值：(1) sin270°−cos270° (2) cos²360°+tan180° (3) sin²360°/cos0°+cos180°","calls":[expr_call(op2("sub",trig("sin",270),trig("cos",270)),"part_1","(1)"),expr_call(op2("add",op2("pow",trig("cos",360),2),trig("tan",180)),"part_2","(2)"),expr_call(op2("add",op2("div",op2("pow",trig("sin",360),2),trig("cos",0)),trig("cos",180)),"part_3","(3)")]},
11649:{"skill_id":S4,"answer_type":"multi_part","question":"θ 為第三象限角且 sinθ−cosθ=1/2，求 sinθcosθ 與 sinθ+cosθ。","calls":[call(SIGNED,{"quadrant":3,"relations":[{"lhs":op2("sub","sin","cos"),"rhs":{"value":"1/2"}}],"targets":{"product":op2("mul","sin","cos"),"sum":op2("add","sin","cos")}})]},
11650:{"skill_id":S6,"answer_type":"multi_part","question":"求 sin(−150°) 與 tan315°。","calls":[expr_call(trig("sin",-150),"part_1","sin(−150°)"),expr_call(trig("tan",315),"part_2","tan315°")]},
11651:{"skill_id":S7,"answer_type":"table_fill","question":"在各式填入適當角度或正負號。","calls":[call(REFERENCE,{"items":[{"function":"sin","angle":-30},{"function":"sin","angle":"4/3","unit":"pi_coefficient"},{"function":"cos","angle":-45},{"function":"cos","angle":135},{"function":"tan","angle":"5/3","unit":"pi_coefficient"},{"function":"tan","angle":"7/6","unit":"pi_coefficient"}]})]},
11652:{"skill_id":S7,"answer_type":"multi_part","question":"求 (1) sin(−945°) (2) cos840° (3) tan(−11π/6)。","calls":[expr_call(trig("sin",-945),"part_1","(1)"),expr_call(trig("cos",840),"part_2","(2)"),expr_call(trig("tan","-11/6","pi_coefficient"),"part_3","(3)")]},
11653:{"skill_id":S4,"answer_type":"short_answer","question":"點 P(sin833°,cos833°) 位於第幾象限？","calls":[call(DERIVED,{"source":{"kind":"angle","angle":833},"x_expression":trig("sin",833),"y_expression":trig("cos",833)},[out("quadrant","value","象限")])]},
11654:{"skill_id":S6,"answer_type":"short_answer","question":"摩天輪中心高100公尺、半徑50公尺，座艙逆時針轉120°後距地面多高？","calls":[call(PROJECTION,{"radius":50,"angle":120,"base_elevation":100},[out("","value","高度")])]},
}

SOURCE_PROVIDED_IDS=frozenset({11626,11628,11630,11632,11634,11636,11638,11640,11642})
for example_id,spec in SPECS.items():
    spec["operation"]=spec["calls"][0]["operation"]
    spec["oracle_source"]="source_provided" if example_id in SOURCE_PROVIDED_IDS else "domain_operation"

def get_b2_13_component_spec(example_id: int) -> dict[str,Any]:
    try: return SPECS[int(example_id)]
    except (KeyError,ValueError) as exc: raise KeyError(f"unknown_b2_13_component:{example_id}") from exc
