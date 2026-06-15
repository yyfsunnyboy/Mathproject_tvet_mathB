# -*- coding: utf-8 -*-
"""Generic generator_contract blueprints, enrichment, and validation (task-driven, not skill-specific)."""

from __future__ import annotations

import copy
from typing import Any

from core.gencode.task_families import (
    DISTANCE_BETWEEN_TWO_POINTS_TASKS,
    DIVISION_POINT_COORDINATES_TASKS,
    LINE_EQUATION_TASKS,
    task_family_for_task,
)

DEFAULT_ANTI_REPETITION: dict[str, Any] = {
    "avoid_same_template_consecutive": True,
    "avoid_same_ratio_consecutive": True,
    "avoid_same_point_names_consecutive": True,
    "avoid_same_answer_consecutive": True,
    "recent_history_window": 5,
    "signature_fields": [
        "problem_type_id",
        "template_variant",
        "routing_track",
        "scenario_type",
        "ratio_form",
        "ratio_values",
        "coordinate_pattern",
        "answer",
    ],
}

DEFAULT_SAMPLING_STRATEGY = "weighted_random"

_REQUIRED_TOP_LEVEL = (
    "template_variants",
    "parameter_schema",
    "variation_dimensions",
    "validity_constraints",
    "answer_shape",
)

_COORD_RANGE_SCHEMA: dict[str, Any] = {
    "x_min": -10,
    "x_max": 10,
    "y_min": -10,
    "y_max": 10,
    "exclude_zero_probability": 0.2,
}

_RATIO_SCHEMA: dict[str, Any] = {
    "m_min": 1,
    "m_max": 5,
    "n_min": 1,
    "n_max": 5,
    "require_coprime": True,
    "allow_equal_ratio": False,
}

_POINT_NAMES_SCHEMA: dict[str, Any] = {
    "choices": [["A", "B", "P"], ["P", "Q", "R"], ["M", "N", "T"], ["C", "D", "E"]],
    "randomize": True,
}


def _variant(vid: str, label: str, stem_pattern: str, *, weight: float = 1.0, enabled: bool = True) -> dict[str, Any]:
    return {
        "id": vid,
        "label": label,
        "stem_pattern": stem_pattern,
        "weight": weight,
        "enabled": enabled,
    }


def _division_internal_variants() -> list[dict[str, Any]]:
    return [
        _variant(
            "ratio_colon_form",
            "AP:PB=m:n",
            "已知 {A}({ax},{ay})、{B}({bx},{by})，{P} 在 {AB} 上，且 {AP}:{PB}={m}:{n}，求 {P} 坐標。",
        ),
        _variant(
            "multiple_form",
            "AP=k·PB",
            "已知 {A}({ax},{ay})、{B}({bx},{by})，{P} 在 {AB} 上，且 {AP}={k}{PB}，求 {P} 坐標。",
        ),
        _variant(
            "linear_relation_form",
            "mAP=nPB",
            "已知 {A}({ax},{ay})、{B}({bx},{by})，{P} 在 {AB} 上，且 {m}{AP}={n}{PB}，求 {P} 坐標。",
        ),
        _variant(
            "word_context_form",
            "距離倍數語境",
            "甲地與乙地在坐標平面上，某點位於兩地連線上，且到甲地距離為到乙地的 {k} 倍，求該點坐標。",
        ),
        _variant(
            "reverse_given_point_find_ratio",
            "已知三點共線求比",
            "已知 {A}、{B}、{P} 三點共線，求 {AP}:{PB}。",
            weight=0.4,
            enabled=False,
        ),
    ]


def _centroid_variants() -> list[dict[str, Any]]:
    return [
        _variant(
            "direct_triangle_centroid",
            "直接求重心",
            "已知 {A}({ax},{ay})、{B}({bx},{by})、{C}({cx},{cy})，求 △{ABC} 重心坐標。",
        ),
        _variant(
            "worded_triangle_centroid",
            "文字敘述三角形重心",
            "三角形三頂點坐標如下，求其重心坐標。",
        ),
        _variant(
            "missing_vertex_from_centroid",
            "已知重心求頂點",
            "已知 {A}({ax},{ay})、{B}({bx},{by}) 與重心 {G}({gx},{gy})，求 {C} 坐標。",
            weight=0.5,
            enabled=False,
        ),
    ]


def _midpoint_variants() -> list[dict[str, Any]]:
    return [
        _variant("direct_midpoint", "直接求中點", "求 {A}({ax},{ay}) 與 {B}({bx},{by}) 的中點坐標。"),
        _variant(
            "missing_endpoint_from_midpoint",
            "已知中點求端點",
            "已知 {A}({ax},{ay}) 與中點 {M}({mx},{my})，求 {B} 坐標。",
            weight=0.5,
            enabled=False,
        ),
        _variant("word_context_midpoint", "語境中點", "兩地中間位置為 {M}，求其中點坐標。"),
    ]


def _distance_variants() -> list[dict[str, Any]]:
    return [
        _variant(
            "direct_distance",
            "直接求距離",
            "求 {A}({ax},{ay}) 與 {B}({bx},{by}) 的距離。",
        ),
        _variant(
            "missing_coordinate",
            "反求坐標",
            "已知 {A}({ax},{ay})、{B}({bx},{by}) 與距離 {d}，求未知坐標。",
            weight=0.6,
        ),
        _variant(
            "word_context_distance",
            "語境距離",
            "平面上兩地坐標如下，求兩地距離。",
        ),
        _variant(
            "compare_distance",
            "比較距離",
            "比較 {A} 到 {B} 與 {A} 到 {C} 的距離大小。",
            weight=0.4,
        ),
    ]


def _division_variation_dimensions() -> list[str]:
    return [
        "point_names",
        "coordinate_sign_pattern",
        "ratio_form",
        "ratio_values",
        "answer_integer_or_fraction",
        "direct_formula_or_word_context",
        "internal_or_external",
        "ask_target",
    ]


def _distance_variation_dimensions() -> list[str]:
    return [
        "point_names",
        "coordinate_sign_pattern",
        "distance_result_type",
        "coordinate_delta_pattern",
        "ask_target",
        "context_style",
    ]


def _absolute_value_variation_dimensions() -> list[str]:
    return [
        "inequality_symbol",
        "center_sign",
        "radius",
        "answer_format",
        "graph_interpretation_variant",
    ]


TASK_CONTRACT_BLUEPRINTS: dict[str, dict[str, Any]] = {}


def _register_blueprint(target_task: str, blueprint: dict[str, Any]) -> None:
    TASK_CONTRACT_BLUEPRINTS[target_task] = blueprint


for _task in DIVISION_POINT_COORDINATES_TASKS:
    if _task == "compute_internal_division_point_coordinates":
        _register_blueprint(
            _task,
            {
                "template_variants": _division_internal_variants(),
                "parameter_schema": {
                    "point_names": dict(_POINT_NAMES_SCHEMA),
                    "coordinate_range": dict(_COORD_RANGE_SCHEMA),
                    "ratio": dict(_RATIO_SCHEMA),
                    "answer_type_mode": {
                        "choices": ["integer_coordinate", "rational_coordinate"],
                        "weights": [0.7, 0.3],
                    },
                },
                "variation_dimensions": _division_variation_dimensions(),
                "difficulty_controls": {
                    "level_1": {
                        "coordinate_range": [-5, 5],
                        "integer_answer_only": True,
                        "simple_ratio_only": True,
                        "template_variants": ["ratio_colon_form", "direct_midpoint"],
                    },
                    "level_2": {
                        "coordinate_range": [-10, 10],
                        "allow_negative_coordinates": True,
                        "allow_rational_answer": True,
                    },
                    "level_3": {
                        "word_context_enabled": True,
                        "missing_endpoint_enabled": True,
                        "external_division_enabled": True,
                    },
                },
                "anti_repetition_rules": dict(DEFAULT_ANTI_REPETITION),
                "validity_constraints": [
                    "A != B",
                    "m, n positive integers",
                    "denominator != 0",
                    "internal point lies between A and B",
                    "coordinate answer matches ratio relation",
                    "no ambiguous wording",
                ],
                "answer_shape": "coordinate_pair",
                "explanation_variants": [
                    "section_formula_stepwise",
                    "ratio_substitution_short",
                ],
                "sampling_strategy": DEFAULT_SAMPLING_STRATEGY,
            },
        )
    elif _task == "compute_centroid_coordinates":
        _register_blueprint(
            _task,
            {
                "template_variants": _centroid_variants(),
                "parameter_schema": {
                    "point_names": {
                        "choices": [["A", "B", "C"], ["P", "Q", "R"], ["X", "Y", "Z"]],
                        "randomize": True,
                    },
                    "coordinate_range": dict(_COORD_RANGE_SCHEMA),
                    "point_count": {"fixed": 3},
                    "answer_type_mode": {
                        "choices": ["integer_centroid", "rational_centroid"],
                        "weights": [0.65, 0.35],
                    },
                },
                "variation_dimensions": [
                    "point_names",
                    "coordinate_sign_pattern",
                    "vertex_count",
                    "answer_integer_or_rational",
                    "word_context",
                    "ask_target",
                ],
                "difficulty_controls": {
                    "level_1": {"coordinate_range": [-5, 5], "integer_centroid": True},
                    "level_2": {"coordinate_range": [-9, 9], "allow_negative_coordinates": True},
                    "level_3": {"missing_vertex_from_centroid": True, "word_context_enabled": True},
                },
                "anti_repetition_rules": dict(DEFAULT_ANTI_REPETITION),
                "validity_constraints": [
                    "three vertices not all identical",
                    "centroid computed by coordinate average",
                    "if integer answer required, sum of coordinates divisible by 3",
                ],
                "answer_shape": "coordinate_pair",
                "explanation_variants": ["average_formula", "component_wise_average"],
                "sampling_strategy": DEFAULT_SAMPLING_STRATEGY,
            },
        )
    elif _task == "compute_midpoint_coordinates":
        _register_blueprint(
            _task,
            {
                "template_variants": _midpoint_variants(),
                "parameter_schema": {
                    "point_names": dict(_POINT_NAMES_SCHEMA),
                    "coordinate_range": dict(_COORD_RANGE_SCHEMA),
                    "answer_type_mode": {
                        "choices": ["integer_midpoint", "rational_midpoint"],
                        "weights": [0.75, 0.25],
                    },
                },
                "variation_dimensions": [
                    "point_names",
                    "coordinate_sign_pattern",
                    "answer_integer_or_fraction",
                    "word_context",
                    "ask_target",
                ],
                "difficulty_controls": {
                    "level_1": {"coordinate_range": [-5, 5], "integer_midpoint": True},
                    "level_2": {"coordinate_range": [-10, 10], "allow_rational_answer": True},
                    "level_3": {"missing_endpoint_enabled": True, "word_context_enabled": True},
                },
                "anti_repetition_rules": dict(DEFAULT_ANTI_REPETITION),
                "validity_constraints": ["A != B", "midpoint formula consistent with endpoints"],
                "answer_shape": "coordinate_pair",
                "explanation_variants": ["midpoint_formula"],
                "sampling_strategy": DEFAULT_SAMPLING_STRATEGY,
            },
        )
    elif _task in {"solve_point_from_section_ratio", "compute_external_division_point_coordinates", "compute_coordinate_average"}:
        _register_blueprint(
            _task,
            {
                "template_variants": _division_internal_variants()[:3],
                "parameter_schema": {
                    "point_names": dict(_POINT_NAMES_SCHEMA),
                    "coordinate_range": dict(_COORD_RANGE_SCHEMA),
                    "ratio": dict(_RATIO_SCHEMA),
                    "answer_type_mode": {
                        "choices": ["integer_coordinate", "rational_coordinate"],
                        "weights": [0.7, 0.3],
                    },
                },
                "variation_dimensions": _division_variation_dimensions(),
                "difficulty_controls": {
                    "level_1": {"coordinate_range": [-5, 5], "integer_answer_only": True},
                    "level_2": {"coordinate_range": [-10, 10], "allow_rational_answer": True},
                },
                "anti_repetition_rules": dict(DEFAULT_ANTI_REPETITION),
                "validity_constraints": ["A != B", "ratio values positive", "division formula valid"],
                "answer_shape": "coordinate_pair",
                "explanation_variants": ["section_formula_stepwise"],
                "sampling_strategy": DEFAULT_SAMPLING_STRATEGY,
            },
        )

for _dtask in DISTANCE_BETWEEN_TWO_POINTS_TASKS:
    _register_blueprint(
        _dtask,
        {
            "template_variants": _distance_variants(),
            "parameter_schema": {
                "point_names": dict(_POINT_NAMES_SCHEMA),
                "coordinate_range": dict(_COORD_RANGE_SCHEMA),
                "distance_result_type": {
                    "choices": ["integer", "radical"],
                    "weights": [0.55, 0.45],
                },
                "coordinate_delta_pattern": {
                    "choices": ["axis_aligned", "mixed_sign", "general"],
                    "weights": [0.3, 0.4, 0.3],
                },
            },
            "variation_dimensions": _distance_variation_dimensions(),
            "difficulty_controls": {
                "level_1": {"coordinate_range": [-5, 5], "integer_distance_only": True},
                "level_2": {"coordinate_range": [-10, 10], "allow_radical": True},
                "level_3": {"word_context_enabled": True, "missing_coordinate_enabled": True},
            },
            "anti_repetition_rules": dict(DEFAULT_ANTI_REPETITION),
            "validity_constraints": [
                "A != B",
                "distance > 0",
                "if integer answer desired, dx^2+dy^2 must be perfect square",
                "if radical answer desired, simplify radical form",
            ],
            "answer_shape": "numeric_or_radical",
            "explanation_variants": ["distance_formula", "pythagorean_step"],
            "sampling_strategy": DEFAULT_SAMPLING_STRATEGY,
        },
    )

_register_blueprint(
    "solve_absolute_value_inequality",
    {
        "template_variants": [
            _variant("interval_notation", "區間表示", "解不等式 |x-{c}| {sym} {r}，以區間表示解。"),
            _variant("inequality_form", "不等式", "解 |x-{c}| {sym} {r}。"),
        ],
        "parameter_schema": {
            "inequality_symbol": {"choices": ["<=", "<", ">=", ">"], "randomize": True},
            "center": {"min": -8, "max": 8},
            "radius": {"min": 1, "max": 6},
            "answer_format": {"choices": ["interval", "inequality"], "weights": [0.6, 0.4]},
        },
        "variation_dimensions": _absolute_value_variation_dimensions(),
        "difficulty_controls": {
            "level_1": {"radius_max": 4, "center_range": [-5, 5]},
            "level_2": {"allow_open_closed_mix": True},
            "level_3": {"graph_interpretation": True},
        },
        "anti_repetition_rules": dict(DEFAULT_ANTI_REPETITION),
        "validity_constraints": ["radius positive", "interval endpoints consistent with symbol"],
        "answer_shape": "interval",
        "explanation_variants": ["distance_on_number_line", "case_split"],
        "sampling_strategy": DEFAULT_SAMPLING_STRATEGY,
    },
)

_LINE_EQUATION_BLUEPRINTS: dict[str, dict[str, Any]] = {
    "write_line_equation_from_point_slope": {
        "template_variants": [
            _variant(
                "given_point_and_slope_find_point_slope_form",
                "點斜式",
                "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的點斜式方程式。",
            ),
            _variant(
                "given_point_and_slope_find_slope_intercept_form",
                "斜截式",
                "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的斜截式方程式（y = mx + b）。",
            ),
            _variant(
                "given_point_and_slope_find_general_form",
                "一般式",
                "已知直線過點 ({x1}, {y1})，斜率為 {m}，求此直線的一般式方程式（Ax + By + C = 0）。",
            ),
        ],
        "variation_dimensions": [
            "point_coordinates",
            "slope_type",
            "equation_form",
            "integer_or_fraction_slope",
            "coefficient_normalization",
        ],
        "explanation_variants": ["point_slope_to_general", "slope_intercept_to_general"],
    },
    "write_line_equation_from_two_points": {
        "template_variants": [
            _variant(
                "two_points_general_form",
                "兩點一般式",
                "已知直線通過兩點 A({x1}, {y1})、B({x2}, {y2})，請寫出此直線的一個方程式。",
            ),
        ],
        "variation_dimensions": ["point_pair", "coefficient_normalization"],
        "explanation_variants": ["two_point_slope_to_general"],
    },
    "write_perpendicular_bisector_from_two_points": {
        "template_variants": [
            _variant(
                "perpendicular_bisector_segment",
                "垂直平分線",
                "已知兩點 A({x1}, {y1})、B({x2}, {y2})，請寫出線段 AB 的垂直平分線方程式。",
            ),
        ],
        "variation_dimensions": ["point_pair", "integer_midpoint"],
        "explanation_variants": ["midpoint_and_normal_vector"],
    },
    "write_line_equation_from_slope_and_intercept": {
        "template_variants": [
            _variant(
                "slope_with_x_intercept",
                "斜率與 x 截距",
                "已知直線斜率為 {m}，且 x 截距為 {k}，請寫出此直線的一個方程式。",
            ),
            _variant(
                "slope_with_y_intercept",
                "斜率與 y 截距",
                "已知直線斜率為 {m}，且 y 截距為 {b}，請寫出此直線的一個方程式。",
            ),
        ],
        "variation_dimensions": ["slope_type", "intercept_axis", "intercept_value"],
        "explanation_variants": ["intercept_to_point_slope"],
    },
    "write_triangle_median_line_from_vertices": {
        "template_variants": [
            _variant(
                "triangle_median_through_vertex",
                "三角形中線",
                "已知三角形 ABC 頂點，求過某頂點且平分面積的直線方程式。",
            ),
            _variant(
                "triangle_median_area_bisector",
                "面積平分線",
                "設三角形 ABC 三頂點已知，求過指定頂點且將三角形面積平分的直線方程式。",
            ),
            _variant(
                "triangle_median_coordinate_plane",
                "坐標平面中線",
                "在坐標平面上，三角形 ABC 頂點坐標已知，請寫出平分三角形面積的直線方程式。",
            ),
        ],
        "variation_dimensions": ["triangle_vertices", "through_vertex", "integer_midpoint"],
        "explanation_variants": ["opposite_side_midpoint_to_line"],
    },
}

for _ltask in LINE_EQUATION_TASKS:
    _line_meta = _LINE_EQUATION_BLUEPRINTS.get(_ltask, {})
    _register_blueprint(
        _ltask,
        {
            "template_variants": _line_meta.get(
                "template_variants",
                [_variant("default", "default", "依題意寫出直線方程式。")],
            ),
            "parameter_schema": {
                "point_coordinates": {
                    "x_min": -8,
                    "x_max": 8,
                    "y_min": -8,
                    "y_max": 8,
                    "integer_only": True,
                },
                "slope": {
                    "choices": ["integer", "simple_fraction"],
                    "weights": [0.65, 0.35],
                    "integer_range": [-5, 5],
                    "exclude_zero": True,
                    "fraction_numerators": [1, 2, 3, -1, -2, -3],
                    "fraction_denominators": [2, 3],
                },
                "equation_form": {
                    "choices": [
                        "point_slope",
                        "slope_intercept",
                        "general",
                    ],
                    "weights": [0.34, 0.33, 0.33],
                },
            },
            "variation_dimensions": _line_meta.get(
                "variation_dimensions",
                ["point_coordinates", "slope_type", "equation_form"],
            ),
            "difficulty_controls": {
                "level_1": {
                    "coordinate_range": [-5, 5],
                    "integer_slope_only": True,
                },
                "level_2": {
                    "coordinate_range": [-8, 8],
                    "allow_fraction_slope": True,
                },
                "level_3": {
                    "allow_negative_slope": True,
                    "require_general_form": True,
                },
            },
            "anti_repetition_rules": dict(DEFAULT_ANTI_REPETITION),
            "validity_constraints": [
                "coordinates are integers",
                "generated equation is a non-degenerate line",
                "equivalent forms normalize to same Ax + By + C = 0",
            ],
            "answer_shape": "linear_equation",
            "explanation_variants": _line_meta.get("explanation_variants", ["stepwise"]),
            "sampling_strategy": DEFAULT_SAMPLING_STRATEGY,
        },
    )


def _generic_blueprint(target_task: str) -> dict[str, Any]:
    family = task_family_for_task(target_task)
    return {
        "template_variants": [
            _variant("default", "default", "依題意求解：{stem_hint}。"),
        ],
        "parameter_schema": {
            "seed": {"type": "integer", "randomize": True},
            "difficulty_level": {"choices": ["level_1", "level_2", "level_3"], "weights": [0.4, 0.4, 0.2]},
        },
        "variation_dimensions": ["seed", "difficulty_level", "context_style"],
        "difficulty_controls": {
            "level_1": {},
            "level_2": {},
            "level_3": {},
        },
        "anti_repetition_rules": dict(DEFAULT_ANTI_REPETITION),
        "validity_constraints": ["answer derivable from givens"],
        "answer_shape": "numeric",
        "explanation_variants": ["stepwise"],
        "sampling_strategy": DEFAULT_SAMPLING_STRATEGY,
        "template_families": [target_task] if target_task else [family or "generic"],
    }


def _answer_allows_ratio_output(answer_contract: dict[str, Any] | None) -> bool:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    at = str(ac.get("answer_type", "")).strip().lower()
    return at in {"ratio", "text", "short_answer", "single_choice"}


def _filter_variants_by_contract(
    variants: list[dict[str, Any]],
    answer_contract: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    at = str(ac.get("answer_type", "")).strip().lower()
    out: list[dict[str, Any]] = []
    for v in variants:
        if not isinstance(v, dict):
            continue
        vid = str(v.get("id", "")).strip()
        enabled = bool(v.get("enabled", True))
        if vid == "reverse_given_point_find_ratio" and not _answer_allows_ratio_output(ac):
            continue
        if vid == "missing_vertex_from_centroid" and at not in {"ordered_pair", "coordinate_pair", ""}:
            continue
        if vid == "missing_endpoint_from_midpoint" and at not in {"ordered_pair", "coordinate_pair", ""}:
            continue
        if enabled or vid == "default":
            row = dict(v)
            row["enabled"] = enabled
            out.append(row)
    return out or variants


def enrich_generator_contract(
    target_task: str,
    partial: dict[str, Any] | None = None,
    *,
    answer_contract: dict[str, Any] | None = None,
    problem_type_id: str = "",
) -> dict[str, Any]:
    """Merge task blueprint with Phase 1 partial contract; validate-supported fields only."""
    task = str(target_task or "").strip()
    base = copy.deepcopy(TASK_CONTRACT_BLUEPRINTS.get(task) or _generic_blueprint(task))
    merged: dict[str, Any] = {**base, **(partial if isinstance(partial, dict) else {})}
    variants = merged.get("template_variants")
    if isinstance(variants, list):
        merged["template_variants"] = _filter_variants_by_contract(variants, answer_contract)
    else:
        merged["template_variants"] = _filter_variants_by_contract(
            list(base.get("template_variants") or []), answer_contract
        )
    if not merged.get("anti_repetition_rules"):
        merged["anti_repetition_rules"] = dict(DEFAULT_ANTI_REPETITION)
    if not merged.get("sampling_strategy"):
        merged["sampling_strategy"] = DEFAULT_SAMPLING_STRATEGY
    if problem_type_id:
        merged["problem_type_id"] = problem_type_id
    if answer_contract and not merged.get("answer_shape"):
        merged["answer_shape"] = str(answer_contract.get("answer_shape") or answer_contract.get("answer_type", ""))
    
    # Force inject High School Math B variation dimensions
    is_math_b = problem_type_id and (
        "math_b" in problem_type_id.lower() or
        "perpendicular" in problem_type_id.lower() or
        "parallel" in problem_type_id.lower() or
        "slope" in problem_type_id.lower() or
        "midpoint" in problem_type_id.lower() or
        "coordinate" in problem_type_id.lower() or
        "vh_" in problem_type_id.lower()
    )
    if is_math_b:
        dims = list(merged.get("variation_dimensions") or [])
        mathb_dims = ["number_variation", "template_variant", "coordinate_sign_combination", "slope_type"]
        for d in mathb_dims:
            if d not in dims:
                dims.append(d)
        merged["variation_dimensions"] = dims

    return merged


def validate_generator_contract(
    contract: dict[str, Any],
    answer_contract: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    """Return (blockers, warnings) for generator_contract vs answer_contract support."""
    gc = contract if isinstance(contract, dict) else {}
    blockers: list[str] = []
    warnings: list[str] = []
    for key in _REQUIRED_TOP_LEVEL:
        if key not in gc or (isinstance(gc.get(key), (list, dict)) and not gc.get(key)):
            blockers.append(f"missing_generator_contract_{key}")
    pt_id = gc.get("problem_type_id") or ""
    is_math_b = pt_id and (
        "math_b" in str(pt_id).lower() or
        "perpendicular" in str(pt_id).lower() or
        "parallel" in str(pt_id).lower() or
        "slope" in str(pt_id).lower() or
        "midpoint" in str(pt_id).lower() or
        "coordinate" in str(pt_id).lower() or
        "vh_" in str(pt_id).lower()
    )
    variants = gc.get("template_variants")
    if isinstance(variants, list):
        enabled = [v for v in variants if isinstance(v, dict) and v.get("enabled", True)]
        if len(enabled) < 1:
            blockers.append("no_enabled_template_variants")
        elif len(enabled) < 2:
            if is_math_b:
                blockers.append("insufficient_template_variants_math_b")
            else:
                warnings.append("single_template_variant_only")
    dims = gc.get("variation_dimensions")
    if isinstance(dims, list) and len(dims) < 4:
        if is_math_b:
            blockers.append("insufficient_variation_dimensions_math_b")
        else:
            warnings.append("variation_dimensions_below_recommended_minimum")
    schema = gc.get("parameter_schema")
    if not isinstance(schema, dict) or not schema:
        blockers.append("parameter_schema_empty")
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    at = str(ac.get("answer_type", "")).strip()
    if at in {"ordered_pair", "coordinate_pair"} and str(gc.get("answer_shape", "")) not in {
        "coordinate_pair",
        "ordered_pair",
        "",
    }:
        warnings.append("answer_shape_mismatch_with_contract")
    return sorted(set(blockers)), sorted(set(warnings))


def enrich_spec_generator_contract(spec: dict[str, Any]) -> dict[str, Any]:
    """Enrich problem_type spec's generator_contract in place (returns spec copy)."""
    out = dict(spec)
    target = str(spec.get("target_task", "")).strip()
    ac = spec.get("answer_contract") if isinstance(spec.get("answer_contract"), dict) else {}
    partial = spec.get("generator_contract") if isinstance(spec.get("generator_contract"), dict) else {}
    gc = enrich_generator_contract(
        target,
        partial,
        answer_contract=ac,
        problem_type_id=str(spec.get("problem_type_id", "")).strip(),
    )
    blockers, warnings = validate_generator_contract(gc, ac)
    gc["contract_validation_blockers"] = blockers
    gc["contract_validation_warnings"] = warnings
    out["generator_contract"] = gc
    return out
