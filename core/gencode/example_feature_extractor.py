from __future__ import annotations

import re
from fractions import Fraction
from typing import Any

from core.gencode.answer_contract_bridge import legacy_fields_from_answer_contract
from core.gencode.task_families import task_family_for_task
from core.gencode.validators.answer_contract_validator import CHOICE_EMBEDDED_PATTERN, LABEL_ONLY_PATTERN

_CHOICE_LINE = re.compile(r"[\(（]\s*([A-Da-d])\s*[\)）]")
_POINT_COORD = re.compile(r"([A-Z])\s*\(\s*([^)]+)\s*\)", re.I)
_SYMBOLIC_COND = re.compile(r"a\s*<\s*b|a\s*<\s*b\s*<\s*0|變數|符號", re.I)
_AXIS_DIST = re.compile(r"到\s*[xyXY]\s*軸|距離.*軸|axis", re.I)
_QUADRANT_EXPLICIT = re.compile(
    r"第[一二三四1-4ⅠⅡⅢⅣ]+象限|哪一[個个]?象限|何象限|位於.{0,8}象限|"
    r"判斷.{0,6}象限|判断.{0,6}象限|quadrant",
    re.I,
)
_SEGMENT_LENGTH = re.compile(
    r"\\overline\{\s*([A-Z]{2})\s*\}\s*=\s*([\d.]+)"
    r"|(?:^|[^\w])([A-Z]{2})\s*=\s*(\d+(?:\.\d+)?)"
    r"|兩點距離為|两点距离为|距離為|距离为|線段長|线段长",
    re.I,
)
_SOLVE_UNKNOWN_REQUEST = re.compile(
    r"求\s*(?:[kxyzmnab]\s*值|[kxyzmnab]|未知|參數|参数)|試求\s*[kxyzmnab]|求\s*未知",
    re.I,
)
_COMPUTE_SEGMENT_LENGTH = re.compile(
    r"求\s*(?:\\overline\{[A-Z]{2}\}|[A-Z]{2}\s*的?\s*(?:長|长|距離|距离))|求\s*兩點距離|求\s*两点距离",
    re.I,
)
_TWO_POINT_PHRASE = re.compile(r"坐標平面上兩點|坐标平面上两点|平面上兩點|平面上两点", re.I)
_CENTROID = re.compile(r"重心|centroid|形心", re.I)
_MIDPOINT = re.compile(r"中點|中点|midpoint", re.I)
_TRIANGLE = re.compile(r"△\s*[A-Z]{3}|[A-Z]{3}\s*三角形|triangle\s*[A-Z]{3}", re.I)
_INTERNAL_DIVISION = re.compile(r"內分|内分|AP\s*:\s*PB|AP:PB|分點|分点|section\s*ratio|m\s*:\s*n", re.I)
_EXTERNAL_DIVISION = re.compile(r"外分|external\s*division", re.I)
_EXPLICIT_DISTANCE = re.compile(
    r"距離|距离|distance|線段長|线段长|segment\s*length|"
    r"\\overline\{[A-Z]{2}\}|求\s*(?:\\overline\{[A-Z]{2}\}|[A-Z]{2})\s*的?\s*(?:長|长|距離|距离)",
    re.I,
)
_COORD_PAIR_ANSWER = re.compile(
    r"^\s*[\(（]?\s*-?\d+(?:\.\d+)?\s*[,，]\s*-?\d+(?:\.\d+)?\s*[\)）]?\s*$"
)
_PROB = re.compile(r"機率|樣本空間|probability", re.I)
_COMB = re.compile(r"排列|組合|選法|permutation|combination", re.I)
_STATS = re.compile(r"平均數|中位數|標準差|mean|median|std", re.I)
_GRAPH = re.compile(r"函數圖形|座標圖|graph", re.I)
_FUNCTION_RELATION = re.compile(r"是否為函數|是否为函数|對應關係|对应关系|一對一|一对一|多對一|多对一", re.I)
_FUNCTION_MAPPING = re.compile(r"箭頭圖|箭头图|對應圖|对应图|表格.{0,12}對應|集合.{0,8}對應", re.I)
_FUNCTION_VALUE = re.compile(r"函數值|函数值|代入|求\s*f\s*\(|求\s*g\s*\(", re.I)
_FUNCTION_NOTATION = re.compile(r"函數記號|函数记号|f\\left\s*\(|函數的定義|函数的定义", re.I)
_DOMAIN_RANGE = re.compile(r"定義域|定义域|值域", re.I)
_TABLE = re.compile(r"表格|table", re.I)
_VAR = re.compile(r"\b[a-zA-Z]\b")
_UNKNOWN_IN_COORD = re.compile(r"(?<![a-zA-Z])([kambntxyz])(?![a-zA-Z])", re.I)
_MOJIBAKE = re.compile(r"�|Ã|æ|ç|銝|嚙")
_BROKEN_FRAC = re.compile(r"\\frac(?!\{)")
_BROKEN_LEFT_RIGHT = re.compile(r"\\left(?!\s*[\(\[\{])|\\right(?!\s*[\)\]\}])")
_BROKEN_LATEX_BRACE = re.compile(r"\\(frac|sqrt|begin|end)\{[^}]*$")
_COMPOSITE_EXERCISE = re.compile(r"綜合|综合|章末|統測|统测|基礎題|基础题", re.I)


_QUADRATIC_FORM = re.compile(r"(二次函數|拋物線|抛物线|x\}\^\{2\}|x\^2|\\left\(\s*x|頂點|顶点|對稱軸|对称轴|開口方向|开口方向|最大值|最小值)")
_VERTEX_FORM_HINT = re.compile(r"(\\left\(\s*x|頂點式|顶点式|\(x[+-]|頂點|顶点|對稱軸|对称轴|最低點|最低点|最高點|最高点)")
_QUADRATIC_TRANSLATION = re.compile(r"(平移|水平向|鉛直向|铅直向|向左|向右|向上|向下)")
_QUADRATIC_NEW_FUNCTION = re.compile(r"(新頂點|新顶点|新函數|新函数|平移到新頂點|平移到新顶点|寫出.*函數|写出.*函数)")
_QUADRATIC_PROPERTIES = re.compile(r"(開口方向|开口方向|頂點坐標|顶点坐标|頂點座標|顶点座标|對稱軸|对称轴|最大值|最小值|概略圖形|概略图形)")
_QUADRATIC_PARAMETER_COMPUTE = re.compile(r"(p\s*\+\s*q|f\s*\\left\s*\(\s*3\s*\\right|f\s*\(\s*3\s*\)|交\s*y\s*軸|交\s*y\s*轴|最低點|最低点|最高點|最高点|求.*[abc pq]\s*之值|求.*參數|求.*参数)")


def _infer_quadratic_vertex_task(text: str, answer_type: str) -> str:
    """Classify quadratic vertex-form stems before generic function rules."""
    t = str(text or "")
    if not _QUADRATIC_FORM.search(t):
        return ""
    if _QUADRATIC_NEW_FUNCTION.search(t):
        return "quadratic_vertex_form_translation_to_new_function"
    if _QUADRATIC_PARAMETER_COMPUTE.search(t):
        return "quadratic_vertex_or_parameter_computation"
    if _QUADRATIC_TRANSLATION.search(t) and _VERTEX_FORM_HINT.search(t):
        return "quadratic_graph_translation_fill_blank"
    if _QUADRATIC_PROPERTIES.search(t):
        return "quadratic_vertex_form_properties"
    if _QUADRATIC_TRANSLATION.search(t):
        return "quadratic_graph_translation"
    return ""


def _source_text(ex: dict[str, Any]) -> str:
    for k in ("problem_text", "problem", "question", "stem", "content"):
        v = str(ex.get(k, "")).strip()
        if v:
            return v
    return ""


def _source_answer(ex: dict[str, Any]) -> str:
    return str(ex.get("correct_answer") or ex.get("answer") or "").strip()


def _parse_embedded_choices(question_text: str) -> list[str]:
    choices: list[str] = []
    for m in _CHOICE_LINE.finditer(question_text):
        label = m.group(1).upper()
        start = m.end()
        nxt = _CHOICE_LINE.search(question_text, start)
        end = nxt.start() if nxt else len(question_text)
        text = question_text[start:end].strip(" 　\r\n\t:：.")
        if text:
            choices.append(text)
    return choices


def _infer_answer_type(question_text: str, answer: str, choices: list[str], has_choices: bool) -> str:
    ans = answer.strip()
    if has_choices or LABEL_ONLY_PATTERN.match(ans) or (choices and ans in choices):
        return "single_choice"
    if re.fullmatch(r"-?\d+(\.\d+)?", ans):
        return "numeric"
    if re.fullmatch(r"-?\d+/\d+", ans):
        return "fraction"
    try:
        Fraction(ans)
        if "/" in ans:
            return "fraction"
    except Exception:
        pass
    if re.search(r"[+\-*/^]|\\frac|=", ans):
        return "expression"
    if re.search(r"[,、]|或|or\b|\{.*\}", ans, re.I):
        return "set"
    if _COORD_PAIR_ANSWER.match(ans) or re.search(r"x\s*=\s*-?\d+.*y\s*=\s*-?\d+", ans, re.I):
        return "ordered_pair"
    if ans and not has_choices:
        return "short_answer"
    if CHOICE_EMBEDDED_PATTERN.search(question_text):
        return "single_choice"
    return "short_answer"


def _coord_has_unknown_parameter(coord_body: str) -> bool:
    body = str(coord_body or "")
    if _UNKNOWN_IN_COORD.search(body):
        return True
    if re.search(r"[a-zA-Z]", body) and not re.fullmatch(r"\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?\s*", body):
        letters = re.findall(r"[a-zA-Z]+", body)
        for token in letters:
            if len(token) == 1 and token.lower() not in {"x", "y"}:
                return True
    return False


def _extract_labeled_points(text: str) -> list[tuple[str, str]]:
    return [(m.group(1).upper(), m.group(2).strip()) for m in _POINT_COORD.finditer(text)]


def _infer_division_point_task(text: str) -> str:
    points = _extract_labeled_points(text)
    if _CENTROID.search(text) and (len(points) >= 3 or _TRIANGLE.search(text)):
        return "compute_centroid_coordinates"
    if _MIDPOINT.search(text) and len(points) >= 2:
        return "compute_midpoint_coordinates"
    if _EXTERNAL_DIVISION.search(text) and len(points) >= 2:
        return "compute_external_division_point_coordinates"
    if _INTERNAL_DIVISION.search(text) and (len(points) >= 2 or re.search(r"[A-Z]\s*內分\s*[A-Z]{1,2}", text)):
        return "compute_internal_division_point_coordinates"
    if re.search(r"平均|average", text, re.I) and len(points) >= 2:
        return "compute_coordinate_average"
    return ""


def _infer_two_point_distance_task(text: str) -> str:
    if _infer_division_point_task(text):
        return ""
    if _CENTROID.search(text) or _MIDPOINT.search(text) or _INTERNAL_DIVISION.search(text):
        return ""
    points = _extract_labeled_points(text)
    if len(points) < 2:
        return ""
    has_unknown = any(_coord_has_unknown_parameter(body) for _, body in points[:2])
    has_segment = bool(_SEGMENT_LENGTH.search(text))
    asks_unknown = bool(_SOLVE_UNKNOWN_REQUEST.search(text))
    asks_length = bool(_COMPUTE_SEGMENT_LENGTH.search(text))
    two_point_context = bool(_TWO_POINT_PHRASE.search(text)) or has_segment

    if has_unknown and has_segment and (asks_unknown or two_point_context):
        return "solve_unknown_coordinate_from_two_point_distance"
    if has_unknown and has_segment:
        return "solve_unknown_coordinate_from_two_point_distance"
    if asks_length or (has_segment and not has_unknown):
        return "compute_distance_between_two_points"
    if two_point_context and not has_unknown and re.search(r"距離|距离|長|长", text):
        return "compute_distance_between_two_points"
    if two_point_context and has_unknown:
        return "solve_unknown_coordinate_from_two_point_distance"
    if len(points) >= 2 and _EXPLICIT_DISTANCE.search(text):
        if has_unknown:
            return "solve_unknown_coordinate_from_two_point_distance"
        return "compute_distance_between_two_points"
    return ""


def _detect_math_objects(text: str, target_task: str) -> list[str]:
    objs: list[str] = []
    points = _extract_labeled_points(text)
    if len(points) >= 3 or _TRIANGLE.search(text):
        objs.append("three_coordinate_points")
        objs.append("triangle")
    if len(points) >= 2:
        objs.append("two_coordinate_points")
    if target_task == "compute_centroid_coordinates":
        objs.extend(["centroid", "triangle_vertices", "coordinate_average_reasoning"])
        # Centroid uses 3-point average; avoid midpoint/section tags.
        objs = [x for x in objs if x not in {"two_coordinate_points", "section_ratio"}]
    if target_task == "compute_midpoint_coordinates":
        objs.append("midpoint")
    if target_task in {
        "compute_internal_division_point_coordinates",
        "compute_external_division_point_coordinates",
        "solve_point_from_section_ratio",
    }:
        objs.append("section_ratio")
    if _COORD_POINT.search(text) or "坐標" in text or "座標" in text:
        objs.append("coordinate_point")
    if target_task in {
        "solve_unknown_coordinate_from_two_point_distance",
        "compute_missing_coordinate_from_two_point_distance",
        "solve_parameter_from_distance_formula",
    }:
        objs.extend(["distance_formula", "segment_length", "unknown_coordinate", "parameter"])
    if target_task in {"compute_distance_between_two_points", "compute_distance"}:
        objs.extend(["distance_formula", "segment_length"])
    if _SYMBOLIC_COND.search(text):
        objs.append("symbolic_condition")
    if _AXIS_DIST.search(text):
        objs.append("axis_distance")
    if re.search(r"代數|expression|多項式", text, re.I):
        objs.append("expression")
    if _TABLE.search(text):
        objs.append("table")
    if _GRAPH.search(text):
        objs.append("graph")
    if _PROB.search(text):
        objs.append("probability_context")
    if _COMB.search(text):
        objs.append("combinatorics_context")
    if _STATS.search(text):
        objs.append("statistics_context")
    if task_family_for_task(target_task) == "quadratic_function_graph_family" or _QUADRATIC_FORM.search(text):
        objs.append("quadratic_equation")
        if _VERTEX_FORM_HINT.search(text):
            objs.append("quadratic_vertex_form")
        if _QUADRATIC_TRANSLATION.search(text):
            objs.append("quadratic_translation")
        if "頂點" in text or "顶点" in text:
            objs.append("quadratic_vertex")
        if "對稱軸" in text or "对称轴" in text:
            objs.append("quadratic_axis")
    return sorted(set(objs))


_COORD_POINT = re.compile(r"[PQABCD]\s*\\?\s*\(?\s*[^)\n]{1,40}\)?", re.I)


def _infer_target_task(text: str, math_objects: list[str], answer_type: str) -> str:
    if re.search(r"絕對值|绝对值|absolute\s*value", text, re.I) and re.search(
        r"不等式|inequality|[<>≤≥]=?", text, re.I
    ):
        return "solve_absolute_value_inequality"
    division_pt = _infer_division_point_task(text)
    if division_pt:
        return division_pt
    two_pt = _infer_two_point_distance_task(text)
    if two_pt:
        return two_pt
    quadratic_task = _infer_quadratic_vertex_task(text, answer_type)
    if quadratic_task:
        return quadratic_task
    if _QUADRANT_EXPLICIT.search(text) and answer_type == "short_answer":
        return "classify_quadrant"
    if _AXIS_DIST.search(text):
        return "choose_possible_coordinate"
    if answer_type == "single_choice" and _QUADRANT_EXPLICIT.search(text):
        return "choose_correct_statement"
    if _PROB.search(text):
        return "compute_probability"
    if _COMB.search(text):
        return "count_arrangements"
    if _STATS.search(text):
        return "read_table"
    if _FUNCTION_RELATION.search(text):
        return "judge_function_relation"
    if _FUNCTION_MAPPING.search(text):
        return "judge_function_from_mapping"
    if _FUNCTION_VALUE.search(text):
        return "evaluate_function_value"
    if _DOMAIN_RANGE.search(text):
        return "judge_domain_range_basic"
    if _FUNCTION_NOTATION.search(text) or re.search(r"\\frac\{1\}\{2\}g.*t\^2|f\s*\(\s*x\s*\)\s*=", text):
        return "interpret_function_notation"
    if _GRAPH.search(text):
        return "read_graph"
    if _TABLE.search(text):
        return "read_table"
    if re.search(r"化簡|因式|expand|simplify", text, re.I):
        return "simplify_expression"
    if re.search(r"解方程式|solve", text, re.I):
        return "solve_equation"
    if "coordinate_point" in math_objects:
        return "compute_numeric"
    return "compute_numeric"


def _infer_reasoning_type(text: str, math_objects: list[str], target_task: str) -> list[str]:
    types: list[str] = []
    if target_task in {
        "compute_centroid_coordinates",
        "compute_midpoint_coordinates",
        "compute_internal_division_point_coordinates",
        "compute_external_division_point_coordinates",
        "compute_coordinate_average",
    }:
        types.append("coordinate_average_reasoning")
    if target_task in {
        "solve_unknown_coordinate_from_two_point_distance",
        "compute_distance_between_two_points",
        "compute_distance",
    }:
        types.append("distance_formula_reasoning")
    if _AXIS_DIST.search(text) or target_task == "choose_possible_coordinate":
        types.append("axis_distance_reasoning")
    if _QUADRANT_EXPLICIT.search(text) or "symbolic_condition" in math_objects:
        types.append("sign_reasoning")
    if _PROB.search(text):
        types.append("probability_reasoning")
    if _COMB.search(text):
        types.append("combinatorics_counting")
    if _STATS.search(text):
        types.append("statistics_computation")
    if task_family_for_task(target_task) == "quadratic_function_graph_family":
        if target_task == "quadratic_vertex_or_parameter_computation":
            types.append("quadratic_vertex_parameter_reasoning")
        elif target_task == "quadratic_vertex_form_translation_to_new_function":
            types.append("quadratic_vertex_translation_reasoning")
        elif target_task == "quadratic_graph_translation_fill_blank":
            types.append("quadratic_vertex_form_translation")
        else:
            types.append("quadratic_vertex_form_properties")
    if _GRAPH.search(text):
        types.append("graph_reading")
    if _TABLE.search(text):
        types.append("table_reading")
    if re.search(r"代數|符號", text):
        types.append("symbolic_algebra")
    if not types:
        types.append("numeric_computation")
    return sorted(set(types))


def extract_example_feature_rule_only(ex: dict[str, Any]) -> dict[str, Any]:
    """Rule-based feature extraction (fallback / validator only; not AI-first)."""
    ex_id = ex.get("id") or ex.get("example_id")
    question_text = _source_text(ex)
    answer = _source_answer(ex)
    embedded = _parse_embedded_choices(question_text)
    raw_choices = ex.get("choices") or ex.get("options")
    choices_list: list[str] = []
    if isinstance(raw_choices, list):
        for ch in raw_choices:
            if isinstance(ch, dict):
                choices_list.append(str(ch.get("text", "")).strip())
            else:
                choices_list.append(str(ch).strip())
    if embedded:
        choices_list = embedded
    has_choices = len(choices_list) >= 2
    stem_embeds_choices = bool(CHOICE_EMBEDDED_PATTERN.search(question_text)) or bool(embedded)
    answer_type = _infer_answer_type(question_text, answer, choices_list, has_choices)
    target_task = _infer_target_task(question_text, [], answer_type)
    math_objects = _detect_math_objects(question_text, target_task)
    target_task = _infer_target_task(question_text, math_objects, answer_type)
    task_family = task_family_for_task(target_task)
    reasoning_type = _infer_reasoning_type(question_text, math_objects, target_task)
    if target_task == "compute_centroid_coordinates" and "coordinate_average_reasoning" not in reasoning_type:
        reasoning_type.append("coordinate_average_reasoning")
    reasoning_type = sorted(set(reasoning_type))
    source_quality_issues: list[str] = []
    if not question_text:
        source_quality_issues.append("missing_question_text")
    if _MOJIBAKE.search(question_text):
        source_quality_issues.append("ocr_or_mojibake_pollution")
    if _BROKEN_FRAC.search(question_text) or _BROKEN_LATEX_BRACE.search(question_text):
        source_quality_issues.append("broken_latex_fraction")
    if _BROKEN_LEFT_RIGHT.search(question_text):
        source_quality_issues.append("broken_latex_left_right")
    if answer_type == "single_choice" and has_choices and answer and answer not in choices_list and not LABEL_ONLY_PATTERN.match(answer):
        source_quality_issues.append("choice_answer_not_in_options")
    if not answer and answer_type not in {"short_answer"}:
        source_quality_issues.append("missing_answer")
    source_quality_reject = bool(source_quality_issues)
    candidate_only = bool(_COMPOSITE_EXERCISE.search(question_text))
    variables = sorted(set(_VAR.findall(question_text)))
    givens = [v for v in variables if v.isalpha()]
    eq = "set_equal" if answer_type == "set" else ("choice_label" if answer_type == "single_choice" else "exact_text")
    bridge = legacy_fields_from_answer_contract({"answer_type": answer_type, "answer_equivalence": eq})
    return {
        "source_example_id": ex_id,
        "question_text": question_text,
        "answer": answer,
        "choices": choices_list,
        "has_choices": has_choices,
        "stem_embeds_choices": stem_embeds_choices,
        "answer_type": answer_type,
        "answer_shape": bridge["answer_shape"],
        "checker": bridge["checker_key"],
        "equivalence": bridge["equivalence_type"],
        "math_objects": math_objects,
        "target_task": target_task,
        "task_family": task_family,
        "reasoning_type": reasoning_type,
        "required_derivation": True,
        "source_quality_issues": source_quality_issues,
        "source_quality_reject": source_quality_reject,
        "candidate_only": candidate_only,
        "variables": variables,
        "givens": givens,
        "target": target_task,
        "classifier_source": "rule_only",
    }


def extract_example_feature(ex: dict[str, Any]) -> dict[str, Any]:
    """Backward-compatible alias: rule-only extraction (use build_classified_example_feature for AI-first)."""
    return extract_example_feature_rule_only(ex)
