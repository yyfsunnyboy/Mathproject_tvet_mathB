"""Declarative textbook topology for the 31 Math B2 1-2 components."""

from __future__ import annotations

from typing import Any


RATIO = "vh_數學B2_RatioAndRatioValue"
ACUTE = "vh_數學B2_TrigonometricFunctionsOfAcuteAngles"
SPECIAL = "vh_數學B2_TrigonometricValuesOfSpecialAngles"
CALCULATOR = "vh_數學B2_CalculatingFunctionValuesUsingCalculator"
IDENTITY = "vh_數學B2_FundamentalTrigonometricIdentities"

SIMILAR = "solve_similar_triangle_proportion"
RIGHT = "compute_right_triangle_trig_ratios"
EXACT = "evaluate_exact_special_angle_expression"
COFUNCTION = "complete_cofunction_identity"
CONSTRAINT = "solve_acute_trig_constraints"
PROJECTION = "solve_right_triangle_projection"
DECIMAL = "evaluate_trig_decimal"
SIMPLIFY = "simplify_fundamental_trig_expression"
COLLINEAR = "collinear_three_points_parameter"
CHORD_ARC = "compute_chord_and_arc_length"


def _call(operation: str, constraints: dict[str, Any], outputs: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"operation": operation, "constraints": constraints}
    if outputs is not None:
        row["outputs"] = outputs
    return row


def _out(source_key: str = "", key: str = "", label: str = "") -> dict[str, str]:
    return {name: value for name, value in {"source_key": source_key, "key": key, "label": label}.items() if value}


def _term(function: str, angle: Any, *, coefficient: Any = 1, power: int = 1, unit: str = "degree") -> dict[str, Any]:
    return {"function": function, "angle": angle, "coefficient": coefficient, "power": power, "unit": unit}


COMPONENT_SPECS: dict[int, dict[str, Any]] = {
    11556: {"skill_id": RATIO, "operation": SIMILAR, "answer_type": "short_answer", "question": "小華身高 1.6 公尺、影長 2 公尺；同時樹影長 5 公尺。利用相似三角形求樹高。", "calls": [_call(SIMILAR, {"terms": ["1.6", 2, None, 5]}, [_out(key="tree_height", label="樹高")])]},
    11557: {"skill_id": ACUTE, "operation": RIGHT, "answer_type": "multi_part", "question": "直角三角形 ABC 中，∠C=90°、AB=3、BC=2，求 sin A、cos A、tan A。", "calls": [_call(RIGHT, {"opposite": 2, "adjacent": "sqrt(5)", "hypotenuse": 3})]},
    11558: {"skill_id": ACUTE, "operation": CONSTRAINT, "answer_type": "multi_part", "question": "已知 θ 為銳角且 tan θ=3/4，求 sin θ 與 cos θ。", "calls": [_call(CONSTRAINT, {"known": {"tan": "3/4"}, "targets": {"sin": "sin_theta", "cos": "cos_theta"}})]},
    11559: {"skill_id": SPECIAL, "operation": EXACT, "answer_type": "multi_part", "question": "求下列各式的精確值：(1) sin(π/6)+cos(π/3)；(2) 2sin²45°−tan²60°。", "calls": [
        _call(EXACT, {"terms": [_term("sin", "1/6", unit="pi_coefficient"), _term("cos", "1/3", unit="pi_coefficient")]}, [_out(key="part_1", label="(1)")]),
        _call(EXACT, {"terms": [_term("sin", 45, coefficient=2, power=2), _term("tan", 60, coefficient=-1, power=2)]}, [_out(key="part_2", label="(2)")]),
    ]},
    11560: {"skill_id": SPECIAL, "operation": PROJECTION, "answer_type": "multi_part", "question": "登山列車行進 500 公尺且軌道仰角為 30°，求上升高度與水平前進距離。", "calls": [_call(PROJECTION, {"hypotenuse": 500, "angle": 30, "requested": ["vertical_projection", "horizontal_projection"], "length_unit": "m"}, [_out("vertical_projection", "rise", "上升高度"), _out("horizontal_projection", "horizontal", "水平距離")])]},
    11561: {"skill_id": CALCULATOR, "operation": DECIMAL, "answer_type": "multi_part", "question": "使用計算機求：(1) sin40°；(2) cos38°49′。", "calls": [_call(DECIMAL, {"requests": [{"function": "sin", "degrees": 40, "precision": 9}, {"function": "cos", "degrees": 38, "minutes": 49, "precision": 8}]})]},
    11562: {"skill_id": IDENTITY, "operation": SIMPLIFY, "answer_type": "multi_part", "question": "利用三角函數基本關係填空：(1) sin20°/cos20°；(2) tan25°·cos25°。", "calls": [_call(SIMPLIFY, {"expressions": {"part_1": "sin_theta/cos_theta", "part_2": "tan_theta*cos_theta"}})]},
    11563: {"skill_id": IDENTITY, "operation": COFUNCTION, "answer_type": "multi_part", "question": "利用餘函數關係完成 sin15° 與 cos80° 的等式。", "calls": [
        _call(COFUNCTION, {"function": "sin", "angle": 15}, [_out("given:angle", "given_angle_1", "(1) 原角"), _out("complement_degrees", "complement_1", "(1) 互餘角")]),
        _call(COFUNCTION, {"function": "cos", "angle": 80}, [_out("given:angle", "given_angle_2", "(2) 原角"), _out("complement_degrees", "complement_2", "(2) 互餘角")]),
    ]},
    11564: {"skill_id": IDENTITY, "operation": SIMPLIFY, "answer_type": "multi_part", "question": "求：(1) sin²45°+cos²45°；(2) sin²49°+cos²49°。", "calls": [_call(SIMPLIFY, {"expressions": {"part_1": "sin(pi/4)**2+cos(pi/4)**2", "part_2": "sin(49*pi/180)**2+cos(49*pi/180)**2"}})]},
    11565: {"skill_id": IDENTITY, "operation": CONSTRAINT, "answer_type": "multi_part", "question": "已知 θ 為銳角且 sinθ+cosθ=√7/2，求 sinθcosθ 與 sinθ−cosθ。", "calls": [_call(CONSTRAINT, {"relations": ["sin_theta+cos_theta=sqrt(7)/2"], "targets": {"product": "sin_theta*cos_theta", "difference": "sin_theta-cos_theta"}})]},
    11566: {"skill_id": RATIO, "operation": SIMILAR, "answer_type": "short_answer", "question": "身高 1.5 公尺者的影長為 3 公尺；同時旗桿高 3 公尺。求旗桿影長。", "calls": [_call(SIMILAR, {"terms": ["1.5", 3, 3, None]}, [_out(key="shadow_length", label="旗桿影長")])]},
    11567: {"skill_id": ACUTE, "operation": RIGHT, "answer_type": "multi_part", "question": "依題示兩個直角三角形的邊長，分別求 sin A、cos A、tan A。", "visual_asset": "uploads/question_assets/vocational/longteng/數學B2/ch01_unknown/sec_1-2_銳角三角函數/in_class_practice_隨堂練習2_vocation_fig1.png", "calls": [
        _call(RIGHT, {"opposite": "sqrt(2)", "adjacent": 1, "hypotenuse": "sqrt(3)"}, [_out("sin", "sin_1", "(1) sin A"), _out("cos", "cos_1", "(1) cos A"), _out("tan", "tan_1", "(1) tan A")]),
        _call(RIGHT, {"opposite": 8, "adjacent": 15, "hypotenuse": 17}, [_out("sin", "sin_2", "(2) sin A"), _out("cos", "cos_2", "(2) cos A"), _out("tan", "tan_2", "(2) tan A")]),
    ]},
    11568: {"skill_id": ACUTE, "operation": CONSTRAINT, "answer_type": "multi_part", "question": "已知 θ 為銳角且 cosθ=12/13，求 sinθ 與 tanθ。", "calls": [_call(CONSTRAINT, {"known": {"cos": "12/13"}, "targets": {"sin": "sin_theta", "tan": "tan_theta"}})]},
    11569: {"skill_id": SPECIAL, "operation": EXACT, "answer_type": "multi_part", "question": "求：(1) cos(π/6)+sin(π/3)；(2) √2cos45°−tan²45°。", "calls": [
        _call(EXACT, {"terms": [_term("cos", "1/6", unit="pi_coefficient"), _term("sin", "1/3", unit="pi_coefficient")]}, [_out(key="part_1", label="(1)")]),
        _call(EXACT, {"terms": [_term("cos", 45, coefficient="sqrt(2)"), _term("tan", 45, coefficient=-1, power=2)]}, [_out(key="part_2", label="(2)")]),
    ]},
    11570: {"skill_id": SPECIAL, "operation": PROJECTION, "answer_type": "multi_part", "question": "斜邊長 100 且仰角為 60°，求垂直高度與水平距離。", "calls": [_call(PROJECTION, {"hypotenuse": 100, "angle": 60, "requested": ["vertical_projection", "horizontal_projection"], "length_unit": "m"})]},
    11571: {"skill_id": CALCULATOR, "operation": DECIMAL, "answer_type": "multi_part", "question": "使用計算機求：(1) tan55°；(2) cos80°30′。", "calls": [_call(DECIMAL, {"requests": [{"function": "tan", "degrees": 55, "precision": 8}, {"function": "cos", "degrees": 80, "minutes": 30, "precision": 8}]})]},
    11572: {"skill_id": IDENTITY, "operation": SIMPLIFY, "answer_type": "multi_part", "question": "利用基本關係填空：(1) sin66°/cos66°；(2) tan55°·cos55°。", "calls": [_call(SIMPLIFY, {"expressions": {"part_1": "sin_theta/cos_theta", "part_2": "tan_theta*cos_theta"}})]},
    11573: {"skill_id": IDENTITY, "operation": COFUNCTION, "answer_type": "multi_part", "question": "利用餘函數關係完成 sin65° 與 cos77° 的等式。", "calls": [
        _call(COFUNCTION, {"function": "sin", "angle": 65}, [_out("given:angle", "given_angle_1", "(1) 原角"), _out("complement_degrees", "complement_1", "(1) 互餘角")]),
        _call(COFUNCTION, {"function": "cos", "angle": 77}, [_out("given:angle", "given_angle_2", "(2) 原角"), _out("complement_degrees", "complement_2", "(2) 互餘角")]),
    ]},
    11574: {"skill_id": IDENTITY, "operation": CONSTRAINT, "answer_type": "multi_part", "question": "已知 θ 為銳角且 sinθ−cosθ=1/√2，求 sinθcosθ 與 sinθ+cosθ。", "calls": [_call(CONSTRAINT, {"relations": ["sin_theta-cos_theta=1/sqrt(2)"], "targets": {"product": "sin_theta*cos_theta", "sum": "sin_theta+cos_theta"}})]},
    11575: {"skill_id": ACUTE, "operation": COLLINEAR, "answer_type": "short_answer", "question": "依三點共線條件求座標中的參數 m。{generated_question}", "calls": [_call(COLLINEAR, {"parameter_name": "m"}, [_out(key="m", label="m")])]},
    11576: {"skill_id": ACUTE, "operation": RIGHT, "answer_type": "multi_part", "question": "直角三角形 ABC 中，∠C=90°、BC=7、AC=24，求 sin A、cos A、tan A。", "calls": [_call(RIGHT, {"opposite": 7, "adjacent": 24, "hypotenuse": 25})]},
    11577: {"skill_id": ACUTE, "operation": CONSTRAINT, "answer_type": "multi_part", "question": "θ 為銳角：(1) 已知 sinθ=√3/2，求 cosθtanθ；(2) 已知 tanθ=√3，求 sinθcosθ。", "calls": [
        _call(CONSTRAINT, {"known": {"sin": "sqrt(3)/2"}, "targets": {"value": "cos_theta*tan_theta"}}, [_out("value", "part_1", "(1)")]),
        _call(CONSTRAINT, {"known": {"tan": "sqrt(3)"}, "targets": {"value": "sin_theta*cos_theta"}}, [_out("value", "part_2", "(2)")]),
    ]},
    11578: {"skill_id": SPECIAL, "operation": EXACT, "answer_type": "multi_part", "question": "求：(1) (1−sin²(π/4))/(1+sin²(π/4))；(2) sin²45°+2cos²30°+tan²60°。", "calls": [
        _call(EXACT, {"terms": [_term("cos", 60, coefficient="4/3", power=2)]}, [_out(key="part_1", label="(1)")]),
        _call(EXACT, {"terms": [_term("sin", 45, power=2), _term("cos", 30, coefficient=2, power=2), _term("tan", 60, power=2)]}, [_out(key="part_2", label="(2)")]),
    ]},
    11579: {"skill_id": ACUTE, "operation": CONSTRAINT, "answer_type": "multi_part", "question": "θ 為銳角且 sinθ=√3cosθ，求 tanθ 與 sinθ+cosθ。", "calls": [_call(CONSTRAINT, {"relations": ["sin_theta=sqrt(3)*cos_theta"], "targets": {"tan": "tan_theta", "sum": "sin_theta+cos_theta"}})]},
    11580: {"skill_id": IDENTITY, "operation": SIMPLIFY, "answer_type": "multi_part", "question": "利用基本關係填空：(1) sin88°/cos88°；(2) tan35°·cos35°；(3) sin²35°+cos²35°；(4) sin30°=cos(90°−＿)=cos＿；(5) cos45°=sin(90°−＿)=sin＿。", "calls": [
        _call(SIMPLIFY, {"expressions": {"part_1": "sin_theta/cos_theta", "part_2": "tan_theta*cos_theta", "part_3": "sin_theta**2+cos_theta**2"}}),
        _call(COFUNCTION, {"function": "sin", "angle": 30}, [_out("given:angle", "part_4a", "(4) 原角"), _out("complement_degrees", "part_4b", "(4) 互餘角")]),
        _call(COFUNCTION, {"function": "cos", "angle": 45}, [_out("given:angle", "part_5a", "(5) 原角"), _out("complement_degrees", "part_5b", "(5) 互餘角")]),
    ]},
    11581: {"skill_id": ACUTE, "operation": SIMPLIFY, "answer_type": "short_answer", "question": "θ 為銳角，求 (sinθ+cosθ)²+(sinθ−cosθ)²。", "calls": [_call(SIMPLIFY, {"expressions": {"value": "(sin_theta+cos_theta)**2+(sin_theta-cos_theta)**2"}}, [_out("value", "value", "值")])]},
    11582: {"skill_id": ACUTE, "operation": CONSTRAINT, "answer_type": "multi_part", "question": "θ 為銳角且 sinθ+cosθ=√2，求 sinθcosθ 與 sinθ−cosθ。", "calls": [_call(CONSTRAINT, {"relations": ["sin_theta+cos_theta=sqrt(2)"], "targets": {"product": "sin_theta*cos_theta", "difference": "sin_theta-cos_theta"}})]},
    11583: {"skill_id": ACUTE, "operation": CHORD_ARC, "answer_type": "multi_part", "question": "鞦韆繩長 2 公尺，向兩側擺動各 30° 至 A、B，求弦 AB 與弧 AB 的長。", "visual_asset": "uploads/question_assets/vocational/longteng/數學B2/ch01_unknown/sec_1-2_銳角三角函數/advanced_exercise_1-2習題_進階題9_vocation_fig1.png", "calls": [_call(CHORD_ARC, {"radius": 2, "central_angle": 60, "length_unit": "m"})]},
    11584: {"skill_id": SPECIAL, "operation": PROJECTION, "answer_type": "multi_part", "question": "纜車站 A 到山頂站 B 距離 900 公尺、仰角 45°，A 站海拔 500 公尺；求 B 站海拔與兩站水平距離。", "visual_asset": "uploads/question_assets/vocational/longteng/數學B2/ch01_unknown/sec_1-2_銳角三角函數/advanced_exercise_1-2習題_進階題10_vocation_fig1.png", "calls": [_call(PROJECTION, {"hypotenuse": 900, "angle": 45, "base_elevation": 500, "requested": ["elevation", "horizontal_projection"], "length_unit": "m"})]},
    11585: {"skill_id": IDENTITY, "operation": CONSTRAINT, "answer_type": "single_choice", "question": "已知 0<θ<π/2、tanθ=7/25，令 a=sinθcosθ，下列何者正確？", "calls": [_call(CONSTRAINT, {"known": {"tan": "7/25"}, "targets": {"a": "sin_theta*cos_theta"}, "choice_options": [
        {"label": "A", "semantic": "1/2<a<1", "lower": "1/2", "upper": "1"}, {"label": "B", "semantic": "0<a<1/2", "lower": "0", "upper": "1/2"},
        {"label": "C", "semantic": "-1/2<a<0", "lower": "-1/2", "upper": "0"}, {"label": "D", "semantic": "-1<a<-1/2", "lower": "-1", "upper": "-1/2"},
    ]})]},
    11586: {"skill_id": IDENTITY, "operation": SIMPLIFY, "answer_type": "multi_part", "question": "求：(1) sin²60°+cos²60°；(2) sin²85°+cos²85°。", "calls": [_call(SIMPLIFY, {"expressions": {"part_1": "sin(pi/3)**2+cos(pi/3)**2", "part_2": "sin(17*pi/36)**2+cos(17*pi/36)**2"}})]},
}


for _example_id, _spec in COMPONENT_SPECS.items():
    _spec["textbook_example_id"] = _example_id
    _spec["component_id"] = f"src_{_example_id}"
    _spec["oracle_source"] = "source_provided" if _example_id <= 11565 else "domain_operation"


def get_b2_12_component_spec(textbook_example_id: int) -> dict[str, Any]:
    try:
        return COMPONENT_SPECS[int(textbook_example_id)]
    except (KeyError, TypeError, ValueError) as exc:
        raise KeyError(f"unknown_b2_12_component:{textbook_example_id}") from exc
