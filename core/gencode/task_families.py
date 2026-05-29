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
GENERIC_NUMERIC_FAMILY = "generic_numeric_family"

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
}

# Higher score wins when multiple families match skill terms (not generator availability).
FAMILY_SKILL_HINTS_SCORED: list[tuple[str, tuple[str, ...], int]] = [
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


def task_family_for_task(target_task: str) -> str:
    task = str(target_task or "").strip()
    if not task:
        return ""
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
    return GENERIC_NUMERIC_FAMILY


def infer_skill_families_from_terms(skill_terms: set[str]) -> set[str]:
    norm = " ".join(sorted(skill_terms)).lower()
    scored: list[tuple[int, str]] = []
    for family, hints, weight in FAMILY_SKILL_HINTS_SCORED:
        hits = sum(1 for h in hints if h.lower() in norm)
        if hits:
            scored.append((hits * weight, family))
    if not scored:
        return infer_skill_families(skill_terms)
    scored.sort(reverse=True)
    top_score = scored[0][0]
    return {fam for score, fam in scored if score >= top_score * 0.5}


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
