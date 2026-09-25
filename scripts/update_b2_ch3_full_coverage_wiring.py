# -*- coding: utf-8 -*-
"""Wire B2 Ch3 full textbook coverage: registry + taxonomy + phase1 + adapter sets.

Replaces intentional_skip / blocked unsupported dispositions for the 47 gap
examples with faithful runtime operations from vector_plane_gap_coverage.
Does NOT commit. Safe to re-run (idempotent skill replace by skill_id).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "configs" / "gencode" / "classifiers" / "phase1_rule_packs.yaml"
GAP_AUDIT = ROOT / "reports" / "b2_ch3_gencode_gap_audit.json"
TAXONOMY = ROOT / "core" / "registry" / "taxonomy_registry.py"
REGISTRY = ROOT / "core" / "registry" / "domain_operation_registry.py"
ADAPTER = ROOT / "core" / "gencode" / "vector_plane_capability_adapter.py"

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

# Operation -> (display_name, answer_type, presentation, checker, equivalence)
OP_META = {
    # baseline
    "compute_vector_components_and_magnitude": ("分量與長度", "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer"),
    "solve_equal_vector_coordinates": ("向量相等求未知數", "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer"),
    "compute_directed_segment_and_magnitude": ("有向線段與長度", "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer"),
    "solve_parallelogram_fourth_vertex": ("平行四邊形第四頂點", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "compute_triangle_perimeter_from_two_vectors": ("兩向量求三角形周長", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "compute_vector_sum_difference": ("向量加減", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "compute_point_vectors_linear_combination": ("點向量線段組合", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "compute_triangle_chain_and_perimeter": ("兩邊向量求第三邊與周長", "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer"),
    "compute_vector_linear_combination": ("向量線性組合", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "compute_scalar_multiple_coordinates": ("實數積坐標", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "solve_parallel_vector_parameter": ("平行求參數", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "compute_unit_vector": ("單位向量", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "compute_scaled_direction_vector": ("指定長度方向向量", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "compute_cosine_of_angle_from_dot": ("由坐標求夾角餘弦", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "compute_dot_product_from_magnitudes_angle": ("由長度與夾角求內積", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "compute_dot_product_coordinates": ("坐標內積", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "solve_perpendicular_vector_parameter": ("垂直求參數", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    # gap
    "simplify_vector_path_expression": ("路徑向量化簡", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "express_named_vectors_in_given_basis": ("以基底表示向量", "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer"),
    "solve_scalar_multiple_relation_fill": ("圖上倍數關係填空", "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer"),
    "express_section_point_vector": ("分點向量表示", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "solve_section_coefficient_pair": ("分點係數對", "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer"),
    "identify_equal_vector_mcq": ("相等向量辨識", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "identify_resultant_path_mcq": ("合向量路徑辨識", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "construct_linear_combination_choice": ("線性組合作圖／終點選擇", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "express_linear_combination_from_givens": ("由已知向量式求組合", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "compute_directed_segment_mixed_multipart": ("有向線段混合多小題", "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer"),
    "compute_chain_closure_vector_mcq": ("封閉折線向量", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "solve_point_from_vector_combination": ("由組合求未知點", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "solve_collinear_ratio_mcq": ("共線比例選擇", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "solve_unknown_vector_linear_equation": ("向量方程求未知向量", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "solve_parallel_then_magnitude_mcq": ("平行後求長度", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "identify_unit_vector_mcq": ("單位向量辨識", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "solve_navigation_heading_correction": ("航向修正應用", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "classify_angle_quality_from_dot_mcq": ("夾角銳鈍直角判斷", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "compute_regular_polygon_edge_dot": ("正多邊形邊向量內積", "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer"),
    "compute_dot_identity_multipart": ("內積恆等式多小題", "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer"),
    "plot_navigation_points_coordinates": ("航標坐標標示", "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer"),
    "compute_midpoint_dot_product": ("中點複合內積", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "solve_dot_product_parameter_mcq": ("內積方程求參數", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "solve_perpendicular_composite_parameter": ("垂直複合求參數", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "classify_dot_sign_from_diagram_mcq": ("圖示內積正負判斷", "single_choice", "single_choice", "single_choice_checker", "choice_label"),
    "expand_perpendicular_dot_product": ("垂直向量展開求值", "expression", "short_answer", "expression_checker", "algebraic_equivalent"),
    "solve_angle_from_magnitude_identity": ("由長度恆等式反求夾角", "multi_part", "multiple_inputs", "multi_part_answer_checker", "multi_part_answer"),
}

SKILL_NAMES = {
    "vh_數學B2_SubSection_3_1_1": "向量定義",
    "vh_數學B2_SubSection_3_1_2": "向量的加法作圖",
    "vh_數學B2_SubSection_3_1_3": "向量的減法作圖",
    "vh_數學B2_SubSection_3_1_4": "向量的實數積作圖",
    "vh_數學B2_SubSection_3_2_1": "向量的坐標表示法",
    "vh_數學B2_SubSection_3_2_2": "向量加減的坐標表示法",
    "vh_數學B2_SubSection_3_2_3": "向量實數積的坐標表示法",
    "vh_數學B2_SubSection_3_2_4": "向量實數積的基本性質",
    "vh_數學B2_SubSection_3_2_5": "向量的平行",
    "vh_數學B2_SubSection_3_2_6": "單位向量",
    "vh_數學B2_SubSection_3_3_1": "向量的夾角",
    "vh_數學B2_SubSection_3_3_2": "向量內積的定義",
    "vh_數學B2_SubSection_3_3_3": "向量內積的坐標表示法",
    "vh_數學B2_SubSection_3_3_4": "兩向量的垂直",
    "vh_數學B2_SubSection_3_3_5": "向量內積的性質",
}

# Covered baseline mappings preserved from Phase1 (48 examples).
BASELINE_SOURCES: dict[str, list[tuple[int, str]]] = {
    "vh_數學B2_SubSection_3_2_1": [
        (11754, "compute_vector_components_and_magnitude"),
        (11755, "compute_vector_components_and_magnitude"),
        (11756, "solve_equal_vector_coordinates"),
        (11757, "solve_equal_vector_coordinates"),
        (11758, "compute_directed_segment_and_magnitude"),
        (11759, "compute_directed_segment_and_magnitude"),
        (11760, "solve_parallelogram_fourth_vertex"),
        (11761, "solve_parallelogram_fourth_vertex"),
        (11783, "compute_directed_segment_and_magnitude"),
        (11822, "compute_triangle_perimeter_from_two_vectors"),
    ],
    "vh_數學B2_SubSection_3_2_2": [
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
    ],
    "vh_數學B2_SubSection_3_2_4": [
        (11768, "compute_vector_linear_combination"),
        (11769, "compute_vector_linear_combination"),
    ],
    "vh_數學B2_SubSection_3_2_5": [
        (11770, "solve_parallel_vector_parameter"),
        (11771, "solve_parallel_vector_parameter"),
        (11781, "solve_parallel_vector_parameter"),
    ],
    "vh_數學B2_SubSection_3_2_6": [
        (11772, "compute_scaled_direction_vector"),
        (11773, "compute_scaled_direction_vector"),
        (11782, "compute_scaled_direction_vector"),
        (11810, "compute_scaled_direction_vector"),
    ],
    "vh_數學B2_SubSection_3_3_1": [
        (11799, "compute_cosine_of_angle_from_dot"),
        (11824, "compute_cosine_of_angle_from_dot"),
    ],
    "vh_數學B2_SubSection_3_3_2": [
        (11797, "compute_dot_product_from_magnitudes_angle"),
    ],
    "vh_數學B2_SubSection_3_3_3": [
        (11787, "compute_dot_product_coordinates"),
        (11788, "compute_dot_product_coordinates"),
        (11789, "compute_cosine_of_angle_from_dot"),
        (11790, "compute_cosine_of_angle_from_dot"),
        (11798, "compute_dot_product_coordinates"),
        (11811, "compute_dot_product_coordinates"),
    ],
    "vh_數學B2_SubSection_3_3_4": [
        (11791, "solve_perpendicular_vector_parameter"),
        (11792, "solve_perpendicular_vector_parameter"),
        (11800, "solve_perpendicular_vector_parameter"),
    ],
    "vh_數學B2_SubSection_3_3_5": [
        (11793, "compute_dot_product_from_magnitudes_angle"),
        (11794, "compute_dot_product_from_magnitudes_angle"),
        (11825, "compute_dot_product_from_magnitudes_angle"),
    ],
}


def runtime_pt(pid: str) -> dict:
    name, at, pm, checker, equiv = OP_META[pid]
    row = {
        "problem_type_id": pid,
        "display_name": name,
        "checker": checker,
        "equivalence": equiv,
        "runtime_candidate": True,
        "requires_human_action": False,
        "required_domain_capabilities": [pid],
        "answer_type": at,
        "presentation_mode": pm,
    }
    if at == "single_choice":
        row["runtime_category"] = "deterministic_choice"
    return row


def skill_pack(sid: str, pairs: list[tuple[int, str]]) -> dict:
    ops = sorted({pid for _, pid in pairs})
    return {
        "skill_id": sid,
        "skill_ch_name": SKILL_NAMES[sid],
        "classifier_source": "human_confirmed",
        "problem_types": [runtime_pt(pid) for pid in ops],
        "classification_rules": [
            {"if_contains": [pid.replace("_", " ")[:12]], "prefer_problem_type_id": pid}
            for pid in ops[:1]
        ],
        "source_examples": [{"example_id": eid, "matched_problem_type_id": pid} for eid, pid in pairs],
        "source_policy": POLICY,
    }


def build_skill_sources() -> dict[str, list[tuple[int, str]]]:
    gaps = json.loads(GAP_AUDIT.read_text(encoding="utf-8"))
    by_skill: dict[str, list[tuple[int, str]]] = {k: list(v) for k, v in BASELINE_SOURCES.items()}
    for g in gaps:
        sid = g["skill_id"]
        ops = g.get("required_operations") or []
        if not ops:
            raise SystemExit(f"gap missing ops: {g['example_id']}")
        by_skill.setdefault(sid, []).append((int(g["example_id"]), ops[0]))
    # sort each skill by example id
    for sid in by_skill:
        by_skill[sid] = sorted(by_skill[sid], key=lambda x: x[0])
    return by_skill


def update_phase1(by_skill: dict[str, list[tuple[int, str]]]) -> None:
    data = yaml.safe_load(PACKS.read_text(encoding="utf-8"))
    skills = data.get("skills") or []
    keep = [s for s in skills if "B2_SubSection_3_" not in str(s.get("skill_id") or "")]
    new_packs = [skill_pack(sid, pairs) for sid, pairs in sorted(by_skill.items())]
    data["skills"] = keep + new_packs
    PACKS.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    print(f"phase1: replaced {len(new_packs)} Ch3 skills; total_skills={len(data['skills'])}")


def update_taxonomy(by_skill: dict[str, list[tuple[int, str]]]) -> None:
    text = TAXONOMY.read_text(encoding="utf-8")
    # Rebuild _B2_CH3_SKILL_OPERATIONS dict content via targeted replace of diagram binding.
    # Replace the diagram skills line and 3_2_3 scalar-only binding.
    skill_ops_lines = ["_B2_CH3_SKILL_OPERATIONS = {"]
    for sid, pairs in sorted(by_skill.items()):
        ops = tuple(sorted({pid for _, pid in pairs}))
        skill_ops_lines.append(f'    "{sid}": {ops!r},')
    skill_ops_lines.append("}")
    block = "\n".join(skill_ops_lines)
    pattern = r"_B2_CH3_SKILL_OPERATIONS = \{.*?\n\}"
    new_text, n = re.subn(pattern, block, text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"taxonomy replace failed n={n}")
    # Drop obsolete diagram comment if present
    new_text = new_text.replace(
        "    # 3-1 diagram skills bind to the domain but Phase1 marks all examples as intentional skip.\n",
        "",
    )
    TAXONOMY.write_text(new_text, encoding="utf-8")
    print("taxonomy: updated _B2_CH3_SKILL_OPERATIONS")


def update_adapter() -> None:
    text = ADAPTER.read_text(encoding="utf-8")
    multi = sorted(
        pid
        for pid, meta in OP_META.items()
        if meta[1] == "multi_part"
    )
    choice = sorted(
        pid
        for pid, meta in OP_META.items()
        if meta[1] == "single_choice"
    )
    multi_block = "_MULTI_PART_OPS = frozenset(\n    {\n" + "".join(f'        "{p}",\n' for p in multi) + "    }\n)"
    choice_block = "_CHOICE_OPS = frozenset(\n    {\n" + "".join(f'        "{p}",\n' for p in choice) + "    }\n)"
    text2, n1 = re.subn(r"_MULTI_PART_OPS = frozenset\(\n    \{.*?\n    \}\n\)", multi_block, text, count=1, flags=re.S)
    text3, n2 = re.subn(r"_CHOICE_OPS = frozenset\(\{.*?\}\)", choice_block, text2, count=1, flags=re.S)
    if n2 == 0:
        text3, n2 = re.subn(r"_CHOICE_OPS = frozenset\(\n    \{.*?\n    \}\n\)", choice_block, text2, count=1, flags=re.S)
    if n1 != 1 or n2 != 1:
        # try simpler CHOICE replace
        if n1 == 1 and "_CHOICE_OPS = frozenset({\"compute_triangle_perimeter_from_two_vectors\"})" in text2:
            text3 = text2.replace(
                '_CHOICE_OPS = frozenset({"compute_triangle_perimeter_from_two_vectors"})',
                choice_block,
            )
            n2 = 1
        else:
            raise SystemExit(f"adapter replace failed n1={n1} n2={n2}")
    ADAPTER.write_text(text3, encoding="utf-8")
    print(f"adapter: multi={len(multi)} choice={len(choice)}")


def update_registry() -> None:
    text = REGISTRY.read_text(encoding="utf-8")
    gap_ops = [
        pid
        for pid in OP_META
        if pid
        not in {
            "compute_vector_components_and_magnitude",
            "solve_equal_vector_coordinates",
            "compute_directed_segment_and_magnitude",
            "solve_parallelogram_fourth_vertex",
            "compute_triangle_perimeter_from_two_vectors",
            "compute_vector_sum_difference",
            "compute_point_vectors_linear_combination",
            "compute_scalar_multiple_coordinates",
            "solve_parallel_vector_parameter",
            "compute_unit_vector",
            "compute_dot_product_coordinates",
            "compute_dot_product_from_magnitudes_angle",
            "solve_perpendicular_vector_parameter",
            "compute_cosine_of_angle_from_dot",
            "compute_vector_linear_combination",
            "compute_scaled_direction_vector",
            "compute_triangle_chain_and_perimeter",
        }
    ]
    # Extend capabilities frozenset
    if "simplify_vector_path_expression" in text:
        print("registry: gap ops already present")
        return
    # Insert into capabilities set before closing
    cap_insert = "".join(f'        "{op}",\n' for op in gap_ops)
    text = text.replace(
        '        "compute_triangle_chain_and_perimeter",\n    }),\n    operations={',
        '        "compute_triangle_chain_and_perimeter",\n'
        + cap_insert
        + "    }),\n    operations={",
    )
    # Append operations before closing of operations dict
    op_entries = []
    for op in gap_ops:
        _, at, pm, _, _ = OP_META[op]
        if at == "single_choice":
            at_t = '("single_choice", "expression")'
            pm_t = '("single_choice", "short_answer")'
        elif at == "multi_part":
            at_t = '("multi_part", "short_answer")'
            pm_t = '("multiple_inputs", "short_answer")'
        else:
            at_t = '("expression", "short_answer")'
            pm_t = '("short_answer",)'
        op_entries.append(
            f'        "{op}": _vector_op(\n'
            f'            "{op}",\n'
            f"            answer_types={at_t},\n"
            f"            presentation_modes={pm_t},\n"
            f'            features=("gap_coverage",),\n'
            f"        ),\n"
        )
    insert = "".join(op_entries)
    # Find the last vector op entry and append before `    },\n))`
    marker = (
        '        "compute_triangle_chain_and_perimeter": _vector_op(\n'
        '            "compute_triangle_chain_and_perimeter",\n'
        '            answer_types=("multi_part", "short_answer"),\n'
        '            presentation_modes=("multiple_inputs", "short_answer"),\n'
        '            features=("chain_sides", "perimeter"),\n'
        "        ),\n"
        "    },\n"
        "))"
    )
    if marker not in text:
        raise SystemExit("registry marker not found")
    text = text.replace(
        marker,
        '        "compute_triangle_chain_and_perimeter": _vector_op(\n'
        '            "compute_triangle_chain_and_perimeter",\n'
        '            answer_types=("multi_part", "short_answer"),\n'
        '            presentation_modes=("multiple_inputs", "short_answer"),\n'
        '            features=("chain_sides", "perimeter"),\n'
        "        ),\n"
        + insert
        + "    },\n"
        "))",
    )
    REGISTRY.write_text(text, encoding="utf-8")
    print(f"registry: added {len(gap_ops)} gap operations")


def main() -> None:
    by_skill = build_skill_sources()
    total = sum(len(v) for v in by_skill.values())
    print(f"sources total={total} skills={len(by_skill)}")
    assert total == 95, total
    update_phase1(by_skill)
    update_taxonomy(by_skill)
    update_adapter()
    update_registry()


if __name__ == "__main__":
    main()
