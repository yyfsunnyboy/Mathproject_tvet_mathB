"""Sealed source topology and Domain calls for B2 section 1-4 Phase 2."""
from __future__ import annotations
from typing import Any
import sympy as sp

S3="vh_數學B2_SubSection_1_4_3"; S4="vh_數學B2_SubSection_1_4_4"
CMP="compare_trig_values_by_monotonicity"; QUAD="solve_trig_value_quadratic_constraint"
GRAPH="analyze_affine_transformed_trig_graph"; PERIOD="calculate_trig_period_from_argument_scale"
SIGN="classify_trig_expression_sign_change"; FEAS="classify_trig_equation_feasibility"
TANABS="analyze_tangent_absolute_graph_period"; DEC="evaluate_trig_decimal"; INTER="count_sine_cosine_intersections"

def call(operation: str, constraints: dict[str,Any], outputs: list[tuple[str,str]]|None=None)->dict[str,Any]:
    return {"operation":operation,"constraints":constraints,"outputs":[{"source_key":a,"key":b} for a,b in (outputs or [])]}
def terms(rows): return [{"key":key,"function":fn,"angle":angle} for key,fn,angle in rows]
def graph(fn,A=1,B=1,C=0,D=0): return call(GRAPH,{"function":fn,"A":A,"B":B,"C":C,"D":D},[("period","period"),("maximum","maximum"),("minimum","minimum")])

VIS={
11659:"uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-4_正弦餘弦函數的圖形/textbook_example_例3_vocation_fig1.png",
11660:"uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-4_正弦餘弦函數的圖形/in_class_practice_隨堂練習3_vocation_fig1.png",
11661:"uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-4_正弦餘弦函數的圖形/textbook_example_例4_vocation_fig1.png",
11662:"uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-4_正弦餘弦函數的圖形/in_class_practice_隨堂練習4_vocation_fig1.png",
11669:"uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-4_正弦餘弦函數的圖形/textbook_exercise_1-4習題_基礎題4_vocation_fig1.png",
11670:"uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-4_正弦餘弦函數的圖形/textbook_exercise_1-4習題_基礎題5_vocation_fig1.png",
11671:"uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-4_正弦餘弦函數的圖形/textbook_exercise_1-4習題_基礎題6_vocation_fig1.png",
11675:"uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-4_正弦餘弦函數的圖形/advanced_exercise_1-4習題_進階題10_vocation_fig1.png"}

SPECS={
11655:{"skill_id":S3,"answer_type":"multi_part","question":"(1)試比較 sin10°、sin50°、sin80° 之大小。(2)試比較 cos10°、sin40°、cos80° 之大小。","calls":[call(CMP,{"terms":terms([("sin10°","sin",10),("sin50°","sin",50),("sin80°","sin",80)])},[("canonical_inequality","part_1")]),call(CMP,{"terms":terms([("cos10°","cos",10),("sin40°","sin",40),("cos80°","cos",80)])},[("canonical_inequality","part_2")])]},
11656:{"skill_id":S3,"answer_type":"multi_part","question":"(1)試比較 sin15°、sin47°、sin88° 之大小。(2)試比較 cos20°、cos40°、sin20° 之大小。","calls":[call(CMP,{"terms":terms([("sin15°","sin",15),("sin47°","sin",47),("sin88°","sin",88)])},[("canonical_inequality","part_1")]),call(CMP,{"terms":terms([("cos20°","cos",20),("cos40°","cos",40),("sin20°","sin",20)])},[("canonical_inequality","part_2")])]},
11657:{"skill_id":S3,"answer_type":"short_answer","question":"若 2sin²θ−5sinθ+2=0，求 sinθ。","calls":[call(QUAD,{"function":"sin","coefficients":[2,-5,2]},[("unique_root","value")])]},
11658:{"skill_id":S3,"answer_type":"short_answer","question":"若 2cos²θ−5cosθ−3=0，求 cosθ。","calls":[call(QUAD,{"function":"cos","coefficients":[2,-5,-3]},[("unique_root","value")])]},
11659:{"skill_id":S3,"answer_type":"multi_part","question":"依來源圖描繪 y=sinx+1，並求週期、最大值與最小值。","calls":[graph("sin",D=1)]},
11660:{"skill_id":S3,"answer_type":"multi_part","question":"依來源圖描繪 y=sinx−1，並求週期、最大值與最小值。","calls":[graph("sin",D=-1)]},
11661:{"skill_id":S3,"answer_type":"multi_part","question":"依來源圖描繪 y=2cosx，並求週期、最大值與最小值。","calls":[graph("cos",A=2)]},
11662:{"skill_id":S3,"answer_type":"multi_part","question":"依來源圖描繪 y=3cosx，並求週期、最大值與最小值。","calls":[graph("cos",A=3)]},
11663:{"skill_id":S4,"answer_type":"multi_part","question":"求 y=−sin2x+1 與 y=3cos(−x/2−5) 的週期。","calls":[call(PERIOD,{"function":"sin","B":2,"C":0},[("period","part_1")]),call(PERIOD,{"function":"cos","B":sp.Rational(-1,2),"C":-5},[("period","part_2")])]},
11664:{"skill_id":S4,"answer_type":"multi_part","question":"求 y=−3sin(−2x+π/4) 與 y=5cos(x/2)−3 的週期。","calls":[call(PERIOD,{"function":"sin","B":-2,"C":sp.pi/4},[("period","part_1")]),call(PERIOD,{"function":"cos","B":sp.Rational(1,2),"C":0},[("period","part_2")])]},
11665:{"skill_id":S4,"answer_type":"single_choice","question":"θ由50°增至100°時，sin(2θ−360°) 的正負變化何者正確？","calls":[call(SIGN,{"function":"sin","B":2,"C":-360,"interval":[50,100],"unit":"degree"},[("classification","value")])],"choices":[{"label":"A","value":"從正遞減到負"},{"label":"B","value":"從負遞增到正"},{"label":"C","value":"遞減但全為正"},{"label":"D","value":"遞增但全為負"}],"choice_key_to_value":{"positive_to_negative":"從正遞減到負"}},
11666:{"skill_id":S4,"answer_type":"multi_part","question":"(1)比較 sin23°、sin48°、sin77°。(2)比較 sin65°、cos37°、cos66°。","calls":[call(CMP,{"terms":terms([("sin23°","sin",23),("sin48°","sin",48),("sin77°","sin",77)])},[("canonical_inequality","part_1")]),call(CMP,{"terms":terms([("sin65°","sin",65),("cos37°","cos",37),("cos66°","cos",66)])},[("canonical_inequality","part_2")])]},
11667:{"skill_id":S4,"answer_type":"single_choice","question":"下列何者有解？","calls":[call(FEAS,{"options":[{"key":"A","function":"sin","value":sp.Rational(7,5)},{"key":"B","function":"cos","value":sp.Rational(-3,2)},{"key":"C","function":"tan","value":-100}]},[("canonical_option","value")])],"choices":[{"label":"A","value":"sinx=7/5"},{"label":"B","value":"cosx=-3/2"},{"label":"C","value":"tanx=-100"}],"choice_key_to_value":{"C":"tanx=-100"}},
11668:{"skill_id":S4,"answer_type":"short_answer","question":"若 2cos²θ+5sinθ−4=0，求 sinθ。","calls":[call(QUAD,{"function":"sin","coefficients":[-2,5,-2]},[("unique_root","value")])]},
11669:{"skill_id":S4,"answer_type":"multi_part","question":"依來源圖描繪 y=2sinx，並求週期、最大值與最小值。","calls":[graph("sin",A=2)]},
11670:{"skill_id":S4,"answer_type":"multi_part","question":"依來源圖描繪 y=−cosx，並求週期、最大值與最小值。","calls":[graph("cos",A=-1)]},
11671:{"skill_id":S4,"answer_type":"multi_part","question":"依來源圖描繪 y=|tanx|，並求其週期。","calls":[call(TANABS,{"A":1,"B":1,"C":0,"D":0},[("period","period")])]},
11672:{"skill_id":S4,"answer_type":"multi_part","question":"求 y=−sin3x+2 與 y=3cos(−2x−1) 的週期。","calls":[call(PERIOD,{"function":"sin","B":3,"C":0},[("period","part_1")]),call(PERIOD,{"function":"cos","B":-2,"C":-1},[("period","part_2")])]},
11673:{"skill_id":S4,"answer_type":"multi_part","question":"利用計算機求 sin224° 與 tan185°25′。","calls":[call(DEC,{"requests":[{"function":"sin","degrees":224,"precision":6},{"function":"tan","degrees":185,"minutes":25,"precision":6}]},[("part_1","part_1"),("part_2","part_2")])]},
11674:{"skill_id":S4,"answer_type":"short_answer","question":"−π≤x≤2π 時，y=sinx 與 y=cosx 共有幾個交點？","calls":[call(INTER,{"B":1,"C":0,"interval":[-sp.pi,2*sp.pi]},[("count","value")])]},
11675:{"skill_id":S4,"answer_type":"multi_part","question":"依來源圖描繪 y=sin(x−π)，並求週期、最大值與最小值。","calls":[graph("sin",C=-sp.pi)]},
}
SOURCE_PROVIDED_IDS=frozenset({11655,11657,11659,11661,11663,11665})
for _id,_spec in SPECS.items():
    _spec.update({"operation":_spec["calls"][0]["operation"],"oracle_source":"source_provided" if _id in SOURCE_PROVIDED_IDS else "domain_operation","visual_asset":VIS.get(_id,"")})

def get_b2_14_component_spec(example_id:int)->dict[str,Any]:
    try:return SPECS[int(example_id)]
    except (KeyError,ValueError) as exc:raise KeyError(f"unknown_b2_14_component:{example_id}") from exc
