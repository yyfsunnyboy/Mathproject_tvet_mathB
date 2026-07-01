from __future__ import annotations

import re
from collections import Counter
from typing import Any

# Generic task families (not skill-specific).
DISTANCE_BETWEEN_TWO_POINTS_FAMILY = "distance_between_two_points_family"
DIVISION_POINT_COORDINATES_FAMILY = "division_point_coordinates_family"
CLASSIFY_QUADRANT_FAMILY = "classify_quadrant_family"
COORDINATE_SYSTEM_FAMILY = "coordinate_system_family"
ABSOLUTE_VALUE_INEQUALITY_FAMILY = "absolute_value_inequality_family"
AXIS_DISTANCE_FAMILY = "axis_distance_family"
FUNCTION_CONCEPT_FAMILY = "function_concept_family"
GENERIC_NUMERIC_FAMILY = "generic_numeric_family"
# K12 quadratic function graph family (Source Skill Binding Supremacy §8).
QUADRATIC_FUNCTION_GRAPH_FAMILY = "quadratic_function_graph_family"
# Quadratic inequality + factoring family (vocational math B1 §1-4).
QUADRATIC_INEQUALITY_FAMILY = "quadratic_inequality_family"
LINE_EQUATION_FAMILY = "line_equation_family"

FUNCTION_CONCEPT_TASKS = frozenset(
    {
        "judge_function_relation",
        "judge_function_from_mapping",
        "evaluate_function_value",
        "interpret_function_notation",
        "judge_domain_range_basic",
    }
)

DIVISION_POINT_COORDINATES_TASKS = frozenset(
    {
        "compute_midpoint_coordinates",
        "compute_centroid_coordinates",
        "compute_internal_division_point_coordinates",
        "compute_external_division_point_coordinates",
        "solve_point_from_section_ratio",
        "compute_coordinate_average",
    }
)

DISTANCE_BETWEEN_TWO_POINTS_TASKS = frozenset(
    {
        "compute_distance",
        "compute_distance_between_two_points",
        "solve_unknown_coordinate_from_two_point_distance",
        "compute_missing_coordinate_from_two_point_distance",
        "solve_parameter_from_distance_formula",
        "verify_distance_between_two_points",
        "compare_distances_between_points",
    }
)

CLASSIFY_QUADRANT_TASKS = frozenset({"classify_quadrant", "choose_correct_statement"})

# Quadratic function graph tasks (K12 taxonomy).
QUADRATIC_FUNCTION_GRAPH_TASKS = frozenset(
    {
        "quadratic_graph_translation",
        "quadratic_vertex_axis_identification",
        "quadratic_graph_properties_choice",
        "quadratic_standard_to_vertex_properties",
        "identify_quadratic_graph_shape",
        "compute_quadratic_vertex",
        "compute_quadratic_axis_of_symmetry",
        "quadratic_graph_vertex_axis_choice",
        "quadratic_graph_translation_fill_blank",
        "quadratic_graph_translation_short_answer",
        "quadratic_vertex_form_properties",
        "quadratic_vertex_or_parameter_computation",
        "quadratic_vertex_form_translation_to_new_function",
    }
)

LINE_EQUATION_TASKS = frozenset(
    {
        "write_line_equation_from_point_slope",
        "write_line_equation_from_two_points",
        "write_perpendicular_bisector_from_two_points",
        "write_line_equation_from_slope_and_intercept",
        "write_triangle_median_line_from_vertices",
    }
)

LINE_EQUATION_TASK_TO_SLOT: dict[str, str] = {
    "write_line_equation_from_point_slope": "line_equation_from_point_slope",
    "write_line_equation_from_two_points": "line_equation_from_two_points",
    "write_perpendicular_bisector_from_two_points": "perpendicular_bisector_from_two_points",
    "write_line_equation_from_slope_and_intercept": "line_equation_from_slope_and_intercept",
    "write_triangle_median_line_from_vertices": "triangle_median_line_from_vertices",
}

QUADRATIC_INEQUALITY_TASKS = frozenset(
    {
        "solve_quadratic_inequality",
        "factor_quadratic_by_cross_multiplication",
        "solve_quadratic_by_factoring",
        "interpret_quadratic_inequality_solution_set",
        "solve_quadratic_inequality_special_cases",
        "solve_quadratic_inequality_parameter_range",
        "reverse_quadratic_inequality_coefficients",
        "applied_quadratic_inequality_problem",
    }
)

TASK_TO_FAMILY: dict[str, str] = {
    "compute_distance": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    "compute_distance_between_two_points": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    "solve_unknown_coordinate_from_two_point_distance": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    "compute_missing_coordinate_from_two_point_distance": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    "solve_parameter_from_distance_formula": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    "verify_distance_between_two_points": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    "compare_distances_between_two_points": DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    "compute_midpoint_coordinates": DIVISION_POINT_COORDINATES_FAMILY,
    "compute_centroid_coordinates": DIVISION_POINT_COORDINATES_FAMILY,
    "compute_internal_division_point_coordinates": DIVISION_POINT_COORDINATES_FAMILY,
    "compute_external_division_point_coordinates": DIVISION_POINT_COORDINATES_FAMILY,
    "solve_point_from_section_ratio": DIVISION_POINT_COORDINATES_FAMILY,
    "compute_coordinate_average": DIVISION_POINT_COORDINATES_FAMILY,
    "classify_quadrant": CLASSIFY_QUADRANT_FAMILY,
    "choose_correct_statement": CLASSIFY_QUADRANT_FAMILY,
    "choose_possible_coordinate": AXIS_DISTANCE_FAMILY,
    "solve_absolute_value_inequality": ABSOLUTE_VALUE_INEQUALITY_FAMILY,
    "expand_absolute_value_inequality": ABSOLUTE_VALUE_INEQUALITY_FAMILY,
    "compute_axis_distance": AXIS_DISTANCE_FAMILY,
    "judge_function_relation": FUNCTION_CONCEPT_FAMILY,
    "judge_function_from_mapping": FUNCTION_CONCEPT_FAMILY,
    "evaluate_function_value": FUNCTION_CONCEPT_FAMILY,
    "interpret_function_notation": FUNCTION_CONCEPT_FAMILY,
    "judge_domain_range_basic": FUNCTION_CONCEPT_FAMILY,
    # Quadratic function graph tasks.
    "quadratic_graph_translation": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "quadratic_vertex_axis_identification": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "quadratic_graph_properties_choice": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "quadratic_standard_to_vertex_properties": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "identify_quadratic_graph_shape": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "compute_quadratic_vertex": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "compute_quadratic_axis_of_symmetry": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "quadratic_graph_vertex_axis_choice": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "quadratic_graph_translation_fill_blank": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "quadratic_graph_translation_short_answer": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "quadratic_vertex_form_properties": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "quadratic_vertex_or_parameter_computation": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "quadratic_vertex_form_translation_to_new_function": QUADRATIC_FUNCTION_GRAPH_FAMILY,
    "solve_quadratic_inequality": QUADRATIC_INEQUALITY_FAMILY,
    "interpret_quadratic_inequality_solution_set": QUADRATIC_INEQUALITY_FAMILY,
    "solve_quadratic_inequality_special_cases": QUADRATIC_INEQUALITY_FAMILY,
    "solve_quadratic_inequality_parameter_range": QUADRATIC_INEQUALITY_FAMILY,
    "reverse_quadratic_inequality_coefficients": QUADRATIC_INEQUALITY_FAMILY,
    "applied_quadratic_inequality_problem": QUADRATIC_INEQUALITY_FAMILY,
    "factor_quadratic_by_cross_multiplication": QUADRATIC_INEQUALITY_FAMILY,
    "solve_quadratic_by_factoring": QUADRATIC_INEQUALITY_FAMILY,
    "interpret_quadratic_inequality_solution_set": QUADRATIC_INEQUALITY_FAMILY,
    "write_line_equation_from_point_slope": LINE_EQUATION_FAMILY,
    "write_line_equation_from_two_points": LINE_EQUATION_FAMILY,
    "write_perpendicular_bisector_from_two_points": LINE_EQUATION_FAMILY,
    "write_line_equation_from_slope_and_intercept": LINE_EQUATION_FAMILY,
    "write_triangle_median_line_from_vertices": LINE_EQUATION_FAMILY,
}

# Higher score wins when multiple families match skill terms (not generator availability).
FAMILY_SKILL_HINTS_SCORED: list[tuple[str, tuple[str, ...], int]] = [
    (
        QUADRATIC_FUNCTION_GRAPH_FAMILY,
        (
            "二次函數",
            "二次函数",
            "二次函數的圖形",
            "二次函数的图形",
            "quadraticfunctiongraph",
            "quadratic function graph",
            "拋物線",
            "抛物线",
            "頂點式",
            "顶点式",
            "二次函數圖形",
            "quadratic graph",
            "parabola",
            "最大值",
            "最小值",
            "對稱軸",
            "对称轴",
            "平移",
        ),
        150,
    ),
    (
        QUADRATIC_INEQUALITY_FAMILY,
        (
            "quadraticinequality",
            "quadratic inequality",
            "quadraticinequalityandfactoring",
            "一元二次不等式",
            "二次不等式",
            "十字交乘",
            "十字交乘法",
            "因式分解",
            "factoring",
        ),
        155,
    ),
    (
        LINE_EQUATION_FAMILY,
        (
            "lineequation",
            "line equation",
            "pointslopeform",
            "point slope",
            "point-slope",
            "點斜式",
            "点斜式",
            "直線方程式",
            "直线方程式",
            "斜截式",
            "slope intercept",
        ),
        145,
    ),
    (
        FUNCTION_CONCEPT_FAMILY,
        (
            "函數的概念",
            "函数的概念",
            "functionconcept",
            "function concept",
            "函數概念",
            "函数概念",
            "線型函數",
            "线型函数",
            "一次函數",
            "一次函数",
            "linear function",
            "linearfunction",
        ),
        130,
    ),
    (
        DIVISION_POINT_COORDINATES_FAMILY,
        (
            "分點坐標",
            "分点坐标",
            "分點",
            "分点",
            "中點",
            "中点",
            "內分",
            "内分",
            "外分",
            "重心",
            "座標平均",
            "坐标平均",
            "divisionpoint",
            "division point",
            "section formula",
            "midpoint",
            "centroid",
            "internal division",
            "external division",
        ),
        100,
    ),
    (
        DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
        (
            "兩點距離",
            "两点距离",
            "兩點間",
            "两点间",
            "距離公式",
            "距离公式",
            "distancebetweentwopoints",
            "distance between two points",
            "two point distance",
            "segment length",
        ),
        80,
    ),
    (
        CLASSIFY_QUADRANT_FAMILY,
        (
            "象限",
            "quadrant",
            "第几象限",
            "第幾象限",
        ),
        70,
    ),
    (
        COORDINATE_SYSTEM_FAMILY,
        (
            "直角坐標",
            "直角坐标",
            "坐標系",
            "坐标系",
            "coordinate system",
            "cartesian",
        ),
        60,
    ),
    (
        ABSOLUTE_VALUE_INEQUALITY_FAMILY,
        (
            "絕對值",
            "绝对值",
            "absolute",
            "不等式",
            "inequality",
        ),
        60,
    ),
    (
        AXIS_DISTANCE_FAMILY,
        (
            "到x軸",
            "到y軸",
            "到 x 軸",
            "到 y 軸",
            "axis distance",
        ),
        50,
    ),
]

FAMILY_SKILL_HINTS: dict[str, tuple[str, ...]] = {
    DIVISION_POINT_COORDINATES_FAMILY: FAMILY_SKILL_HINTS_SCORED[0][1],
    DISTANCE_BETWEEN_TWO_POINTS_FAMILY: (
        "兩點",
        "两点",
        "距離",
        "距离",
        "distance",
        "between",
        "平面上",
        "平面上兩點",
        "平面上两点",
        "two point",
        "segment",
    ),
    CLASSIFY_QUADRANT_FAMILY: (
        "象限",
        "quadrant",
        "第几象限",
        "第幾象限",
    ),
    ABSOLUTE_VALUE_INEQUALITY_FAMILY: (
        "絕對值",
        "绝对值",
        "absolute",
        "不等式",
        "inequality",
    ),
}

SOLVE_UNKNOWN_COORDINATE_TASKS = frozenset(
    {
        "solve_unknown_coordinate_from_two_point_distance",
        "compute_missing_coordinate_from_two_point_distance",
        "solve_parameter_from_distance_formula",
    }
)

_PARAM_NAME = re.compile(r"(?i)\b(k|m|n|a|b|t|x|y)\b")


def same_family_extension_allowed(
    expected_families: set[str],
    observed_family: str,
    *,
    scope: str = "default",
) -> bool:
    fam = str(observed_family or "").strip()
    if not fam:
        return False
    if fam in expected_families:
        return True
    if scope in {"medium", "broad"} and DIVISION_POINT_COORDINATES_FAMILY in expected_families:
        return fam == DIVISION_POINT_COORDINATES_FAMILY
    return False


def task_family_for_task(target_task: str) -> str:
    task = str(target_task or "").strip()
    if not task:
        return ""
    if "absolute_value_inequality" in task:
        return ABSOLUTE_VALUE_INEQUALITY_FAMILY
    if task in TASK_TO_FAMILY:
        return TASK_TO_FAMILY[task]
    for key, fam in TASK_TO_FAMILY.items():
        if key in task:
            return fam
    if task in DIVISION_POINT_COORDINATES_TASKS or "centroid" in task or "midpoint" in task:
        return DIVISION_POINT_COORDINATES_FAMILY
    if "quadrant" in task or "象限" in task:
        return CLASSIFY_QUADRANT_FAMILY
    if task in DISTANCE_BETWEEN_TWO_POINTS_TASKS:
        return DISTANCE_BETWEEN_TWO_POINTS_FAMILY
    if "distance" in task or "距離" in task or "距离" in task:
        return DISTANCE_BETWEEN_TWO_POINTS_FAMILY
    if task in FUNCTION_CONCEPT_TASKS or "function" in task:
        return FUNCTION_CONCEPT_FAMILY
    if task in QUADRATIC_FUNCTION_GRAPH_TASKS or "quadratic" in task:
        return QUADRATIC_FUNCTION_GRAPH_FAMILY
    if task in QUADRATIC_INEQUALITY_TASKS:
        return QUADRATIC_INEQUALITY_FAMILY
    if task in LINE_EQUATION_TASKS or "line_equation" in task:
        return LINE_EQUATION_FAMILY
    return GENERIC_NUMERIC_FAMILY


def _is_quadratic_inequality_skill_blob(norm: str, skill_terms: set[str]) -> bool:
    blob = norm.lower()
    has_quadratic = (
        "quadratic" in blob
        or "二次" in blob
        or any("quadratic" in t for t in skill_terms)
    )
    has_inequality = (
        "inequality" in blob
        or "不等式" in blob
        or any("inequality" in t for t in skill_terms)
    )
    has_factoring = (
        "factoring" in blob
        or "因式" in blob
        or "十字" in blob
        or any(tok in skill_terms for tok in {"factoring", "factor"})
    )
    return (has_quadratic and has_inequality) or (has_quadratic and has_factoring)


def infer_skill_families_from_terms(skill_terms: set[str]) -> set[str]:
    norm = " ".join(sorted(skill_terms)).lower()
    if _is_quadratic_inequality_skill_blob(norm, skill_terms):
        return {QUADRATIC_INEQUALITY_FAMILY}
    if "functionconcept" in skill_terms or "function concept" in norm or "函數的概念" in norm or "函数的概念" in norm:
        return {FUNCTION_CONCEPT_FAMILY}
    scored: list[tuple[int, str]] = []
    for family, hints, weight in FAMILY_SKILL_HINTS_SCORED:
        hits = sum(1 for h in hints if h.lower() in norm)
        if hits:
            scored.append((hits * weight, family))
    if not scored:
        families: set[str] = set()
        if "classify_quadrant" in skill_terms:
            families.add(CLASSIFY_QUADRANT_FAMILY)
        return families
    scored.sort(reverse=True)
    top_score = scored[0][0]
    result = {fam for score, fam in scored if score >= top_score * 0.5}
    if QUADRATIC_INEQUALITY_FAMILY in result:
        result.discard(ABSOLUTE_VALUE_INEQUALITY_FAMILY)
    # Source Skill Binding Supremacy §8: when quadratic family is the dominant match,
    # discard coordinate_system_family which is only a background chapter term.
    if QUADRATIC_FUNCTION_GRAPH_FAMILY in result and COORDINATE_SYSTEM_FAMILY in result:
        quad_score = next((s for s, f in scored if f == QUADRATIC_FUNCTION_GRAPH_FAMILY), 0)
        coord_score = next((s for s, f in scored if f == COORDINATE_SYSTEM_FAMILY), 0)
        if quad_score >= coord_score:
            result.discard(COORDINATE_SYSTEM_FAMILY)
    return result


def infer_skill_families(skill_terms: set[str]) -> set[str]:
    families = infer_skill_families_from_terms(skill_terms)
    if not families:
        if "classify_quadrant" in skill_terms:
            families.add(CLASSIFY_QUADRANT_FAMILY)
    return families


def source_family_distribution(features: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for feat in features:
        if not isinstance(feat, dict):
            continue
        fam = str(feat.get("task_family") or task_family_for_task(str(feat.get("target_task", "")))).strip()
        if fam:
            counter[fam] += 1
    return dict(counter)


def dominant_source_families(features: list[dict[str, Any]]) -> tuple[set[str], float]:
    dist = source_family_distribution(features)
    if not dist:
        return set(), 0.0
    total = sum(dist.values())
    top_count = max(dist.values())
    top_fams = {fam for fam, c in dist.items() if c == top_count}
    return top_fams, top_count / total if total else 0.0


def families_compatible(families: set[str]) -> bool:
    fams = {f for f in families if f and f != GENERIC_NUMERIC_FAMILY}
    if len(fams) <= 1:
        return True
    # Multiple distinct pedagogical families in one skill batch => mismatch.
    incompatible_pairs = {
        frozenset({DISTANCE_BETWEEN_TWO_POINTS_FAMILY, CLASSIFY_QUADRANT_FAMILY}),
        frozenset({DISTANCE_BETWEEN_TWO_POINTS_FAMILY, ABSOLUTE_VALUE_INEQUALITY_FAMILY}),
        frozenset({DISTANCE_BETWEEN_TWO_POINTS_FAMILY, DIVISION_POINT_COORDINATES_FAMILY}),
        frozenset({CLASSIFY_QUADRANT_FAMILY, ABSOLUTE_VALUE_INEQUALITY_FAMILY}),
        frozenset({DIVISION_POINT_COORDINATES_FAMILY, CLASSIFY_QUADRANT_FAMILY}),
    }
    fam_set = frozenset(fams)
    return not any(fam_set >= pair for pair in incompatible_pairs)


def requires_set_answer_contract(target_task: str) -> bool:
    return str(target_task or "").strip() in SOLVE_UNKNOWN_COORDINATE_TASKS


def answer_contract_supports_task(spec: dict[str, Any]) -> tuple[bool, list[str]]:
    from core.gencode.checker_registry import validate_answer_contract_capability

    ac = spec.get("answer_contract") if isinstance(spec.get("answer_contract"), dict) else {}
    cap = validate_answer_contract_capability(ac)
    blockers = list(cap.get("checker_contract_blockers", []) or [])
    return cap.get("checker_capability_status") != "blocked", blockers
