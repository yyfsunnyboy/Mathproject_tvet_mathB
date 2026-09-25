# -*- coding: utf-8 -*-
"""Append B2 Ch3 phase1 rule packs with safe YAML quoting."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "configs" / "gencode" / "classifiers" / "phase1_rule_packs.yaml"

POLICY = {
    "source_count_threshold_for_split": 2,
    "small_skill_merge_allowed": False,
    "min_source_examples": 1,
    "allow_single_problem_type": False,
    "allow_skill_default_problem_type": False,
    "default_problem_type_used": False,
    "single_primary_problem_type": False,
    "split_only_when_checker_or_answer_contract_differs": True,
    "do_not_create_student_subskills": True,
}


def runtime_pt(pid: str, name: str, **extra):
    row = {
        "problem_type_id": pid,
        "display_name": name,
        "checker": extra.pop("checker", "expression_checker"),
        "equivalence": extra.pop("equivalence", "algebraic_equivalent"),
        "runtime_candidate": True,
        "requires_human_action": False,
        "required_domain_capabilities": [pid],
    }
    row.update(extra)
    return row


def blocked_pt(pid: str, name: str, reason: str):
    return {
        "problem_type_id": pid,
        "display_name": name,
        "checker": "manual_review_checker",
        "equivalence": "manual_review_or_ai_judged",
        "runtime_candidate": False,
        "requires_human_action": True,
        "notes": reason,
        "block_reason": reason,
    }


def src(pairs):
    return [{"example_id": eid, "matched_problem_type_id": pid} for eid, pid in pairs]


def skill(sid, name, problem_types, rules, sources):
    return {
        "skill_id": sid,
        "skill_ch_name": name,
        "classifier_source": "human_confirmed",
        "problem_types": problem_types,
        "classification_rules": rules,
        "source_examples": sources,
        "source_policy": POLICY,
    }


skills = []

# 3-1 diagram
for i, name in [
    (1, "向量定義"),
    (2, "向量的加法作圖"),
    (3, "向量的減法作圖"),
    (4, "向量的實數積作圖"),
]:
    skills.append(
        skill(
            f"vh_數學B2_SubSection_3_1_{i}",
            name,
            [blocked_pt("vector_diagram_construction_unsupported", "作圖／圖示向量（暫不自動生成）", "diagram_vector_construction_unsupported")],
            [{"if_contains": ["如圖"], "prefer_problem_type_id": "vector_diagram_construction_unsupported"}],
            [],
        )
    )

skills.append(
    skill(
        "vh_數學B2_SubSection_3_2_1",
        "向量的坐標表示法",
        [
            runtime_pt(
                "compute_vector_components_and_magnitude",
                "分量與長度",
                checker="multi_part_answer_checker",
                equivalence="multi_part_answer",
                answer_type="multi_part",
                presentation_mode="multiple_inputs",
            ),
            runtime_pt(
                "solve_equal_vector_coordinates",
                "向量相等求未知數",
                checker="multi_part_answer_checker",
                equivalence="multi_part_answer",
                answer_type="multi_part",
                presentation_mode="multiple_inputs",
            ),
            runtime_pt(
                "compute_directed_segment_and_magnitude",
                "有向線段與長度",
                checker="multi_part_answer_checker",
                equivalence="multi_part_answer",
                answer_type="multi_part",
                presentation_mode="multiple_inputs",
            ),
            runtime_pt("solve_parallelogram_fourth_vertex", "平行四邊形第四頂點"),
            runtime_pt(
                "compute_triangle_perimeter_from_two_vectors",
                "兩向量求三角形周長（選擇）",
                checker="single_choice_checker",
                equivalence="choice_label",
                answer_type="single_choice",
                presentation_mode="single_choice",
                runtime_category="deterministic_choice",
            ),
            blocked_pt(
                "vector_mixed_unknown_endpoint_unsupported",
                "含未知終點的混合題",
                "mixed_unknown_endpoint_composite_unsupported",
            ),
        ],
        [
            {"if_contains": ["周長"], "prefer_problem_type_id": "compute_triangle_perimeter_from_two_vectors"},
            {"if_contains": ["平行四邊形"], "prefer_problem_type_id": "solve_parallelogram_fourth_vertex"},
            {"if_contains": ["兩點"], "prefer_problem_type_id": "compute_directed_segment_and_magnitude"},
            {"if_contains": ["試求x", "試求x、y"], "prefer_problem_type_id": "solve_equal_vector_coordinates"},
            {"if_contains": ["x分量", "y分量"], "prefer_problem_type_id": "compute_vector_components_and_magnitude"},
        ],
        src(
            [
                (11754, "compute_vector_components_and_magnitude"),
                (11755, "compute_vector_components_and_magnitude"),
                (11756, "solve_equal_vector_coordinates"),
                (11757, "solve_equal_vector_coordinates"),
                (11758, "compute_directed_segment_and_magnitude"),
                (11759, "compute_directed_segment_and_magnitude"),
                (11760, "solve_parallelogram_fourth_vertex"),
                (11761, "solve_parallelogram_fourth_vertex"),
                (11775, "vector_mixed_unknown_endpoint_unsupported"),
                (11783, "compute_directed_segment_and_magnitude"),
                (11822, "compute_triangle_perimeter_from_two_vectors"),
            ]
        ),
    )
)

skills.append(
    skill(
        "vh_數學B2_SubSection_3_2_2",
        "向量加減的坐標表示法",
        [
            runtime_pt("compute_vector_sum_difference", "向量加減"),
            runtime_pt("compute_point_vectors_linear_combination", "點向量線段組合"),
            runtime_pt(
                "compute_triangle_chain_and_perimeter",
                "兩邊向量求第三邊與周長",
                checker="multi_part_answer_checker",
                equivalence="multi_part_answer",
                answer_type="multi_part",
                presentation_mode="multiple_inputs",
            ),
            runtime_pt("solve_parallelogram_fourth_vertex", "平行四邊形第四頂點"),
            runtime_pt("compute_vector_linear_combination", "向量線性組合"),
            blocked_pt(
                "vector_chain_closure_mcq_unsupported",
                "封閉折線向量選擇題",
                "vector_chain_closure_mcq_unsupported",
            ),
        ],
        [
            {"if_contains": ["平行四邊形"], "prefer_problem_type_id": "solve_parallelogram_fourth_vertex"},
            {"if_contains": ["周長"], "prefer_problem_type_id": "compute_triangle_chain_and_perimeter"},
            {"if_contains": ["四點"], "prefer_problem_type_id": "compute_point_vectors_linear_combination"},
            {"if_contains": ["SP"], "prefer_problem_type_id": "vector_chain_closure_mcq_unsupported"},
        ],
        src(
            [
                (11762, "compute_vector_sum_difference"),
                (11763, "compute_vector_sum_difference"),
                (11764, "compute_point_vectors_linear_combination"),
                (11765, "compute_point_vectors_linear_combination"),
                (11766, "compute_triangle_chain_and_perimeter"),
                (11767, "compute_triangle_chain_and_perimeter"),
                (11776, "solve_parallelogram_fourth_vertex"),
                (11777, "compute_vector_sum_difference"),
                (11778, "compute_point_vectors_linear_combination"),
                (11779, "compute_triangle_chain_and_perimeter"),
                (11780, "compute_vector_linear_combination"),
                (11807, "compute_vector_sum_difference"),
                (11808, "compute_vector_linear_combination"),
                (11819, "compute_vector_sum_difference"),
                (11821, "vector_chain_closure_mcq_unsupported"),
            ]
        ),
    )
)

skills.append(
    skill(
        "vh_數學B2_SubSection_3_2_3",
        "向量實數積的坐標表示法",
        [
            runtime_pt("compute_vector_linear_combination", "實數積線性組合"),
            runtime_pt("compute_scalar_multiple_coordinates", "實數積坐標"),
            blocked_pt(
                "vector_collinear_ratio_mcq_unsupported",
                "共線比例選擇題",
                "vector_collinear_ratio_mcq_unsupported",
            ),
            blocked_pt(
                "vector_solve_point_from_combo_unsupported",
                "由線性組合解未知點",
                "vector_solve_point_from_combo_unsupported",
            ),
        ],
        [{"if_contains": ["共線"], "prefer_problem_type_id": "vector_collinear_ratio_mcq_unsupported"}],
        src(
            [
                (11784, "vector_solve_point_from_combo_unsupported"),
                (11820, "vector_collinear_ratio_mcq_unsupported"),
            ]
        ),
    )
)

skills.append(
    skill(
        "vh_數學B2_SubSection_3_2_4",
        "向量實數積的基本性質",
        [
            runtime_pt("compute_vector_linear_combination", "實數積線性組合"),
            blocked_pt(
                "vector_solve_unknown_vector_equation_unsupported",
                "向量方程求解未知向量",
                "vector_solve_unknown_vector_equation_unsupported",
            ),
        ],
        [{"if_contains": ["坐標表示"], "prefer_problem_type_id": "compute_vector_linear_combination"}],
        src(
            [
                (11768, "compute_vector_linear_combination"),
                (11769, "compute_vector_linear_combination"),
                (11823, "vector_solve_unknown_vector_equation_unsupported"),
            ]
        ),
    )
)

skills.append(
    skill(
        "vh_數學B2_SubSection_3_2_5",
        "向量的平行",
        [
            runtime_pt("solve_parallel_vector_parameter", "平行求參數"),
            blocked_pt(
                "vector_parallel_then_magnitude_mcq_unsupported",
                "平行後求長度選擇題",
                "vector_parallel_then_magnitude_mcq_unsupported",
            ),
        ],
        [{"if_contains": ["平行"], "prefer_problem_type_id": "solve_parallel_vector_parameter"}],
        src(
            [
                (11770, "solve_parallel_vector_parameter"),
                (11771, "solve_parallel_vector_parameter"),
                (11781, "solve_parallel_vector_parameter"),
                (11809, "vector_parallel_then_magnitude_mcq_unsupported"),
            ]
        ),
    )
)

skills.append(
    skill(
        "vh_數學B2_SubSection_3_2_6",
        "單位向量",
        [
            runtime_pt("compute_unit_vector", "單位向量"),
            runtime_pt("compute_scaled_direction_vector", "指定長度方向向量"),
            blocked_pt(
                "vector_unit_identification_mcq_unsupported",
                "辨識單位向量選擇題",
                "vector_unit_identification_mcq_unsupported",
            ),
        ],
        [
            {"if_contains": ["不是單位向量"], "prefer_problem_type_id": "vector_unit_identification_mcq_unsupported"},
            {"if_contains": ["長度為"], "prefer_problem_type_id": "compute_scaled_direction_vector"},
            {"if_contains": ["單位向量"], "prefer_problem_type_id": "compute_unit_vector"},
        ],
        src(
            [
                (11772, "compute_scaled_direction_vector"),
                (11773, "compute_scaled_direction_vector"),
                (11774, "vector_unit_identification_mcq_unsupported"),
                (11782, "compute_scaled_direction_vector"),
                (11810, "compute_scaled_direction_vector"),
            ]
        ),
    )
)

skills.append(
    skill(
        "vh_數學B2_SubSection_3_3_1",
        "向量的夾角",
        [
            runtime_pt("compute_cosine_of_angle_from_dot", "由坐標求夾角餘弦"),
            blocked_pt(
                "vector_angle_application_narrative_unsupported",
                "航向修正應用敘事題",
                "vector_angle_application_narrative_unsupported",
            ),
            blocked_pt(
                "vector_angle_quality_mcq_unsupported",
                "夾角銳鈍直角判斷",
                "vector_angle_quality_mcq_unsupported",
            ),
        ],
        [{"if_contains": ["夾角"], "prefer_problem_type_id": "compute_cosine_of_angle_from_dot"}],
        src(
            [
                (11799, "compute_cosine_of_angle_from_dot"),
                (11805, "vector_angle_application_narrative_unsupported"),
                (11815, "vector_angle_quality_mcq_unsupported"),
                (11824, "compute_cosine_of_angle_from_dot"),
            ]
        ),
    )
)

skills.append(
    skill(
        "vh_數學B2_SubSection_3_3_2",
        "向量內積的定義",
        [
            runtime_pt("compute_dot_product_from_magnitudes_angle", "由長度與夾角求內積"),
            blocked_pt(
                "vector_regular_polygon_dot_unsupported",
                "正多邊形邊向量內積",
                "vector_regular_polygon_dot_unsupported",
            ),
            blocked_pt(
                "vector_dot_identity_multipart_unsupported",
                "內積恆等式多小題",
                "vector_dot_identity_multipart_unsupported",
            ),
        ],
        [{"if_contains": ["夾角"], "prefer_problem_type_id": "compute_dot_product_from_magnitudes_angle"}],
        src(
            [
                (11785, "vector_regular_polygon_dot_unsupported"),
                (11786, "vector_regular_polygon_dot_unsupported"),
                (11796, "vector_regular_polygon_dot_unsupported"),
                (11797, "compute_dot_product_from_magnitudes_angle"),
                (11802, "vector_dot_identity_multipart_unsupported"),
            ]
        ),
    )
)

skills.append(
    skill(
        "vh_數學B2_SubSection_3_3_3",
        "向量內積的坐標表示法",
        [
            runtime_pt("compute_dot_product_coordinates", "坐標內積"),
            runtime_pt("compute_cosine_of_angle_from_dot", "內積求夾角餘弦"),
            blocked_pt(
                "vector_dot_diagram_plot_unsupported",
                "航標坐標標示圖題",
                "vector_dot_diagram_plot_unsupported",
            ),
            blocked_pt(
                "vector_dot_parameter_equation_mcq_unsupported",
                "內積方程求參數選擇",
                "vector_dot_parameter_equation_mcq_unsupported",
            ),
            blocked_pt(
                "vector_dot_midpoint_composite_unsupported",
                "中點複合內積",
                "vector_dot_midpoint_composite_unsupported",
            ),
        ],
        [{"if_contains": ["內積"], "prefer_problem_type_id": "compute_dot_product_coordinates"}],
        src(
            [
                (11787, "compute_dot_product_coordinates"),
                (11788, "compute_dot_product_coordinates"),
                (11789, "compute_cosine_of_angle_from_dot"),
                (11790, "compute_cosine_of_angle_from_dot"),
                (11798, "compute_dot_product_coordinates"),
                (11804, "vector_dot_diagram_plot_unsupported"),
                (11811, "compute_dot_product_coordinates"),
                (11812, "vector_dot_midpoint_composite_unsupported"),
                (11813, "vector_dot_parameter_equation_mcq_unsupported"),
            ]
        ),
    )
)

skills.append(
    skill(
        "vh_數學B2_SubSection_3_3_4",
        "兩向量的垂直",
        [
            runtime_pt("solve_perpendicular_vector_parameter", "垂直求參數"),
            blocked_pt(
                "vector_perp_composite_expression_unsupported",
                "垂直複合表達式求參數",
                "vector_perp_composite_expression_unsupported",
            ),
        ],
        [{"if_contains": ["垂直"], "prefer_problem_type_id": "solve_perpendicular_vector_parameter"}],
        src(
            [
                (11791, "solve_perpendicular_vector_parameter"),
                (11792, "solve_perpendicular_vector_parameter"),
                (11800, "solve_perpendicular_vector_parameter"),
                (11814, "vector_perp_composite_expression_unsupported"),
            ]
        ),
    )
)

skills.append(
    skill(
        "vh_數學B2_SubSection_3_3_5",
        "向量內積的性質",
        [
            runtime_pt("compute_dot_product_from_magnitudes_angle", "由長度夾角求內積／長度"),
            blocked_pt(
                "vector_dot_exam_diagram_unsupported",
                "統測圖示內積題",
                "vector_dot_exam_diagram_unsupported",
            ),
            blocked_pt(
                "vector_dot_identity_solve_angle_unsupported",
                "由長度恆等式反求夾角",
                "vector_dot_identity_solve_angle_unsupported",
            ),
            blocked_pt(
                "vector_perp_dot_expand_unsupported",
                "垂直向量展開求值",
                "vector_perp_dot_expand_unsupported",
            ),
        ],
        [{"if_contains": ["夾角"], "prefer_problem_type_id": "compute_dot_product_from_magnitudes_angle"}],
        src(
            [
                (11793, "compute_dot_product_from_magnitudes_angle"),
                (11794, "compute_dot_product_from_magnitudes_angle"),
                (11795, "vector_dot_exam_diagram_unsupported"),
                (11801, "vector_perp_dot_expand_unsupported"),
                (11803, "vector_dot_identity_solve_angle_unsupported"),
                (11825, "compute_dot_product_from_magnitudes_angle"),
            ]
        ),
    )
)

data = yaml.safe_load(PACKS.read_text(encoding="utf-8"))
existing = data.get("skills") or []
existing_ids = {str(x.get("skill_id")) for x in existing if isinstance(x, dict)}
added = 0
for item in skills:
    if item["skill_id"] in existing_ids:
        continue
    existing.append(item)
    added += 1
data["skills"] = existing
PACKS.write_text(
    yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120),
    encoding="utf-8",
)
print(f"added={added} total_skills={len(existing)}")
