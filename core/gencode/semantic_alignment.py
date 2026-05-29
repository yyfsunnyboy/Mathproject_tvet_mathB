from __future__ import annotations

import re
from collections import Counter
from typing import Any

from core.gencode.main_skill_anchor import build_main_skill_anchor, example_skill_id_mismatch
from core.gencode.task_families import (
    DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    DISTANCE_BETWEEN_TWO_POINTS_TASKS,
    DIVISION_POINT_COORDINATES_FAMILY,
    DIVISION_POINT_COORDINATES_TASKS,
    answer_contract_supports_task,
    dominant_source_families,
    families_compatible,
    infer_skill_families,
    infer_skill_families_from_terms,
    source_family_distribution,
    task_family_for_task,
)

# Canonical task taxonomy -> indicative tokens (generic, not skill-specific).
TASK_TAXONOMY: dict[str, tuple[str, ...]] = {
    "classify_quadrant": (
        "象限",
        "quadrant",
        "classify_quadrant",
        "quadrant_classification",
        "第几象限",
        "第幾象限",
    ),
    "compute_distance_between_two_points": (
        "distance",
        "compute_distance",
        "two_point_distance",
        "point_distance",
        "兩點",
        "两点",
        "距離",
        "距离",
        "between_two_points",
        "平面上兩點",
        "平面上两点",
    ),
    "solve_unknown_coordinate_from_two_point_distance": (
        "unknown",
        "coordinate",
        "parameter",
        "segment",
        "overline",
        "反求",
        "求k",
        "求 k",
    ),
    "compute_distance": (
        "distance",
        "compute_distance",
        "兩點",
        "两点",
        "距離",
        "距离",
    ),
    "compute_axis_distance": (
        "axis_distance",
        "distance_to_axis",
        "到x軸",
        "到y軸",
        "到 x 軸",
        "到 y 軸",
    ),
    "solve_absolute_value_inequality": (
        "absolute_value",
        "inequality",
        "absolute_value_inequality",
        "絕對值",
        "绝对值",
        "不等式",
    ),
    "expand_absolute_value_inequality": (
        "expand",
        "geometric_meaning",
        "幾何意義",
        "几何意义",
    ),
    "interpret_number_line_interval": (
        "number_line",
        "數線",
        "数轴",
        "interval",
        "區間",
    ),
    "compute_slope": ("slope", "斜率", "gradient"),
    "find_intercepts": ("intercept", "截距", "x_intercept", "y_intercept"),
    "choose_correct_statement": ("choose_correct_statement", "敘述", "下列何者"),
    "choose_possible_coordinate": ("choose_possible_coordinate", "可能坐標", "可能坐标"),
    "compute_centroid_coordinates": ("重心", "centroid", "triangle", "三角形", "coordinate_average"),
    "compute_midpoint_coordinates": ("中點", "中点", "midpoint"),
    "compute_internal_division_point_coordinates": ("內分", "内分", "section", "ratio", "分點", "分点"),
    "compute_external_division_point_coordinates": ("外分", "external division"),
    "compute_coordinate_average": ("平均", "average", "coordinate_average"),
    "compute_numeric": ("compute", "計算", "求值", "numeric"),
}

_TASK_FROM_PROBLEM_TYPE_ID = re.compile(
    r"(classify_quadrant|compute_distance|solve_unknown_coordinate|distance_formula|axis_distance|"
    r"absolute_value|inequality|number_line|slope|intercept|geometric_meaning)"
)

_CAMEL_SPLIT = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Za-z])(?=[0-9])")


def _normalize_token(text: str) -> str:
    s = str(text or "").strip().lower()
    s = s.replace("（", "(").replace("）", ")")
    s = re.sub(r"[_\\-\\s]+", " ", s)
    s = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _tokenize(text: str) -> set[str]:
    norm = _normalize_token(text)
    if not norm:
        return set()
    tokens = {t for t in norm.split() if len(t) >= 2}
    for task, aliases in TASK_TAXONOMY.items():
        for alias in aliases:
            if alias in norm:
                tokens.add(task)
    for m in _TASK_FROM_PROBLEM_TYPE_ID.finditer(norm.replace(" ", "_")):
        tokens.add(m.group(1).replace("axis_distance", "compute_axis_distance"))
    return tokens


def _split_skill_id(skill_id: str) -> set[str]:
    raw = str(skill_id or "").strip()
    parts = re.split(r"[_\\-]+", raw)
    expanded: list[str] = []
    for p in parts:
        p = p.strip()
        if not p or p.isdigit():
            continue
        expanded.append(p.lower())
        expanded.extend(_CAMEL_SPLIT.sub(" ", p).lower().split())
    return {x for x in expanded if len(x) >= 2}


def extract_skill_terms(skill_id: str, skill_metadata: dict[str, Any] | None = None) -> set[str]:
    meta = skill_metadata if isinstance(skill_metadata, dict) else {}
    chunks = [
        skill_id,
        meta.get("skill_ch_name", ""),
        meta.get("skill_en_name", ""),
        meta.get("chapter", ""),
        meta.get("section_code", ""),
        meta.get("unit_name", ""),
        meta.get("volume", ""),
        meta.get("curriculum", ""),
    ]
    terms: set[str] = set()
    for ch in chunks:
        terms |= _tokenize(str(ch))
        terms |= _split_skill_id(str(ch))
    return terms


def extract_source_terms_from_features(features: list[dict[str, Any]]) -> set[str]:
    terms: set[str] = set()
    for feat in features:
        if not isinstance(feat, dict):
            continue
        terms.add(str(feat.get("target_task", "")).strip())
        for mo in feat.get("math_objects", []) or []:
            terms.add(str(mo).strip())
        terms.add(str(feat.get("answer_type", "")).strip())
        terms |= _tokenize(str(feat.get("question_text", "")))
    return {t for t in terms if t}


def extract_problem_type_terms(spec: dict[str, Any]) -> set[str]:
    terms: set[str] = set()
    terms.add(str(spec.get("target_task", "")).strip())
    pt = str(spec.get("problem_type_id", "")).strip()
    terms |= _tokenize(pt)
    terms |= _split_skill_id(pt)
    terms.add(str(spec.get("display_name", "")).strip())
    gc = spec.get("generator_contract") if isinstance(spec.get("generator_contract"), dict) else {}
    for fam in gc.get("template_families", []) or []:
        terms.add(str(fam).strip())
    slot = gc.get("template_slots") if isinstance(gc.get("template_slots"), dict) else {}
    terms.add(str(slot.get("stem", "")).strip())
    sc = spec.get("semantic_contract") if isinstance(spec.get("semantic_contract"), dict) else {}
    for rt in sc.get("reasoning_type", []) or []:
        terms.add(str(rt).strip())
    ac = spec.get("answer_contract") if isinstance(spec.get("answer_contract"), dict) else {}
    terms.add(str(ac.get("answer_type", "")).strip())
    target = spec.get("target") if isinstance(spec.get("target"), dict) else {}
    terms.add(str(target.get("type", "")).strip())
    return {t for t in terms if t}


def infer_expected_tasks(skill_terms: set[str]) -> set[str]:
    expected: set[str] = set()
    for task, aliases in TASK_TAXONOMY.items():
        alias_tokens = {task, *_tokenize(" ".join(aliases))}
        if skill_terms & alias_tokens:
            expected.add(task)
    skill_families = infer_skill_families_from_terms(skill_terms)
    if DIVISION_POINT_COORDINATES_FAMILY in skill_families:
        expected |= set(DIVISION_POINT_COORDINATES_TASKS)
    if DISTANCE_BETWEEN_TWO_POINTS_FAMILY in skill_families:
        expected |= set(DISTANCE_BETWEEN_TWO_POINTS_TASKS)
    return expected


def infer_tasks_from_problem_type_spec(spec: dict[str, Any]) -> set[str]:
    tasks: set[str] = set()
    pt = str(spec.get("problem_type_id", "")).replace("-", "_").lower()
    target = str(spec.get("target_task", "")).strip()
    if target:
        tasks.add(target)
    for task in TASK_TAXONOMY:
        if task in pt:
            tasks.add(task)
    for task in DISTANCE_BETWEEN_TWO_POINTS_TASKS:
        if task in pt:
            tasks.add(task)
    gc = spec.get("generator_contract") if isinstance(spec.get("generator_contract"), dict) else {}
    for fam in gc.get("template_families", []) or []:
        fam_s = str(fam).strip()
        if fam_s:
            tasks.add(fam_s)
    return tasks


def infer_task_family_from_spec(spec: dict[str, Any]) -> str:
    explicit = str(spec.get("task_family", "")).strip()
    if explicit:
        return explicit
    target = str(spec.get("target_task", "")).strip()
    if target:
        return task_family_for_task(target)
    for task in infer_tasks_from_problem_type_spec(spec):
        fam = task_family_for_task(task)
        if fam:
            return fam
    return task_family_for_task(str(spec.get("problem_type_id", "")))


def _overlap_score(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _dominant_source_task(features: list[dict[str, Any]]) -> tuple[str, float]:
    tasks = [str(f.get("target_task", "")).strip() for f in features if isinstance(f, dict)]
    tasks = [t for t in tasks if t]
    if not tasks:
        return "", 0.0
    counter = Counter(tasks)
    top_task, count = counter.most_common(1)[0]
    return top_task, count / len(tasks)


def evaluate_source_example_alignment(
    skill_terms: set[str],
    feature: dict[str, Any],
    *,
    main_skill_anchor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else {}
    ex_terms = extract_source_terms_from_features([feature])
    score = _overlap_score(skill_terms, ex_terms)
    expected_families = set(anchor.get("expected_task_families") or []) or infer_skill_families_from_terms(skill_terms)
    task = str(feature.get("target_task", "")).strip()
    family = str(feature.get("task_family") or task_family_for_task(task)).strip()
    expected_tasks = set(anchor.get("expected_subskill_candidates") or []) or infer_expected_tasks(skill_terms)
    exclude_reason = ""
    aligned = False
    if not task or task == "compute_numeric":
        exclude_reason = "unclassified_low_confidence"
    elif expected_families and family and family not in expected_families:
        exclude_reason = "expected_family_mismatch"
    elif expected_tasks and task and task not in expected_tasks and family not in expected_families:
        exclude_reason = "task_family_mismatch"
    elif family and expected_families and family in expected_families:
        aligned = True
    elif task and task in expected_tasks:
        aligned = True
    elif not expected_families and not expected_tasks:
        aligned = True
    else:
        exclude_reason = "unclassified_low_confidence"
    return {
        "example_id": feature.get("source_example_id"),
        "target_task": task,
        "task_family": family,
        "alignment_score": round(score, 4),
        "aligned_with_skill": aligned,
        "included_in_phase1": aligned,
        "exclude_reason": exclude_reason,
    }


def evaluate_semantic_alignment(
    skill_id: str,
    *,
    skill_metadata: dict[str, Any] | None = None,
    source_features: list[dict[str, Any]],
    candidate_specs: list[dict[str, Any]],
    min_examples_block: int = 4,
    main_skill_anchor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else build_main_skill_anchor(
        skill_id, skill_metadata
    )
    skill_terms = extract_skill_terms(skill_id, skill_metadata)
    source_terms = extract_source_terms_from_features(source_features)
    expected_tasks = set(anchor.get("expected_subskill_candidates") or []) or infer_expected_tasks(skill_terms)
    expected_families = set(anchor.get("expected_task_families") or []) or infer_skill_families_from_terms(skill_terms)
    dominant_task, dominant_ratio = _dominant_source_task(source_features)
    src_family_dist = source_family_distribution(source_features)
    source_families = set(src_family_dist.keys())
    dom_families, dom_family_ratio = dominant_source_families(source_features)

    per_spec_scores: list[dict[str, Any]] = []
    spec_task_scores: list[float] = []
    candidate_families: set[str] = set()
    blockers: list[str] = []
    warnings: list[str] = []

    for spec in candidate_specs:
        if not isinstance(spec, dict):
            continue
        pt_terms = extract_problem_type_terms(spec)
        pt = str(spec.get("problem_type_id", "")).strip()
        gc = spec.get("generator_contract") if isinstance(spec.get("generator_contract"), dict) else {}
        template_families = [str(f).strip() for f in (gc.get("template_families") or []) if str(f).strip()]
        target_task = str(spec.get("target_task", "")).strip() or (template_families[0] if template_families else "")
        if not target_task:
            stem = gc.get("template_slots") if isinstance(gc.get("template_slots"), dict) else {}
            target_task = str(stem.get("stem", "")).strip().replace("_choice", "").replace("_", "")
        pt_family = infer_task_family_from_spec(spec)
        candidate_families.add(pt_family)
        skill_pt_score = _overlap_score(skill_terms, pt_terms)
        source_pt_score = _overlap_score(source_terms, pt_terms)
        spec_task_scores.append(skill_pt_score)
        pt_tasks = infer_tasks_from_problem_type_spec(spec)
        pt_task_families = {task_family_for_task(t) for t in pt_tasks} | {pt_family}
        pt_task_families.discard("")
        family_ok = (not expected_families) or bool(pt_task_families & expected_families)
        task_ok = (not expected_tasks) or bool(pt_tasks & expected_tasks) or family_ok
        contract_ok, contract_blockers = answer_contract_supports_task(spec)
        if not contract_ok:
            warnings.extend(contract_blockers)
        per_spec_scores.append(
            {
                "problem_type_id": pt,
                "target_task": target_task,
                "task_family": pt_family,
                "inferred_tasks": sorted(pt_tasks),
                "skill_problem_type_score": round(skill_pt_score, 4),
                "source_problem_type_score": round(source_pt_score, 4),
                "task_consistent_with_skill": task_ok,
                "family_consistent_with_skill": family_ok,
                "answer_contract_supported": contract_ok,
            }
        )
        if expected_families and pt_family and pt_family not in expected_families and pt_family not in source_families:
            blockers.append("skill_problem_type_semantic_mismatch")

    skill_source_score = _overlap_score(skill_terms, source_terms)
    skill_problem_type_score = min(spec_task_scores) if spec_task_scores else 0.0
    source_problem_type_score = max((x.get("source_problem_type_score", 0.0) for x in per_spec_scores), default=0.0)

    if source_families and not families_compatible(source_families):
        blockers.append("mixed_source_families")
        blockers.append("source_examples_mismatch")
    elif expected_families and source_families and not (source_families <= expected_families or source_families & expected_families):
        if dom_family_ratio >= 0.75:
            blockers.append("source_examples_mismatch")
    elif expected_families and dom_families and not (dom_families & expected_families):
        if dom_family_ratio >= 0.75:
            blockers.append("source_examples_mismatch")
            blockers.append("expected_family_mismatch")
            warnings.append(
                "來源題多數與目前技能語意不一致，疑似 skill mapping 錯誤；請先檢查來源題歸屬，不建議進 Phase 2。"
            )

    outside_expected = [
        f
        for f in source_features
        if isinstance(f, dict)
        and str(f.get("task_family") or task_family_for_task(str(f.get("target_task", "")))).strip()
        not in expected_families
        and expected_families
    ]
    if expected_families and len(outside_expected) >= max(1, len(source_features) // 2):
        blockers.append("mixed_source_families")
        warnings.append("majority_source_family_conflicts_with_skill_anchor")

    if (
        expected_families
        and len(source_features) <= min_examples_block
        and dom_family_ratio >= 0.9
        and dom_families
        and not (dom_families & expected_families)
    ):
        blockers.append("low_alignment_score")

    # Multiple problem types in the same family is allowed.
    if candidate_families and source_families and not families_compatible(candidate_families | source_families):
        blockers.append("mixed_source_families")

    unique_blockers = sorted(set(blockers))
    if unique_blockers:
        decision = "block"
    elif warnings or skill_source_score < 0.25:
        decision = "warn"
        if skill_source_score < 0.25:
            warnings.append("alignment_score_below_recommended_threshold")
    else:
        decision = "pass"

    return {
        "main_skill_anchor": anchor,
        "skill_terms": sorted(skill_terms),
        "source_terms": sorted(source_terms),
        "examples_outside_expected_family": [
            int(f.get("source_example_id"))
            for f in outside_expected
            if isinstance(f.get("source_example_id"), int)
        ],
        "problem_type_terms": sorted(
            {t for spec in candidate_specs if isinstance(spec, dict) for t in extract_problem_type_terms(spec)}
        ),
        "expected_task_candidates": sorted(expected_tasks),
        "expected_skill_families": sorted(expected_families),
        "observed_source_family_distribution": src_family_dist,
        "source_family_distribution": src_family_dist,
        "candidate_problem_type_families": sorted(candidate_families),
        "dominant_source_task": dominant_task,
        "dominant_source_task_ratio": round(dominant_ratio, 4),
        "dominant_source_family": sorted(dom_families),
        "dominant_source_family_ratio": round(dom_family_ratio, 4),
        "skill_source_score": round(skill_source_score, 4),
        "skill_problem_type_score": round(skill_problem_type_score, 4),
        "source_problem_type_score": round(source_problem_type_score, 4),
        "per_problem_type_scores": per_spec_scores,
        "decision": decision,
        "blockers": unique_blockers,
        "warnings": sorted(set(warnings)),
    }


def apply_alignment_gate_to_candidates(
    candidates: list[dict[str, Any]],
    alignment: dict[str, Any],
) -> list[dict[str, Any]]:
    decision = str(alignment.get("decision", "pass")).strip()
    blockers = list(alignment.get("blockers", []) or [])
    per_scores = {
        str(x.get("problem_type_id", "")): x
        for x in (alignment.get("per_problem_type_scores") or [])
        if isinstance(x, dict)
    }
    out: list[dict[str, Any]] = []
    for cand in candidates:
        if not isinstance(cand, dict):
            continue
        row = dict(cand)
        pt = str(row.get("problem_type_id", "")).strip()
        score_row = per_scores.get(pt, {})
        row["semantic_alignment"] = {
            "skill_problem_type_score": score_row.get("skill_problem_type_score", 0.0),
            "source_problem_type_score": score_row.get("source_problem_type_score", 0.0),
            "task_consistent_with_skill": score_row.get("task_consistent_with_skill", True),
        }
        promote_blockers = list(row.get("promote_blockers", []) or [])
        if decision == "block":
            promote_blockers.extend(blockers)
            promote_blockers.append("semantic_alignment_blocked")
            row["promote_recommendation"] = "conservative_hold_for_that_candidate"
            row["generator_readiness"] = "alignment_blocked"
            row["confidence"] = "low"
            row["risk_flags"] = sorted(set(list(row.get("risk_flags", []) or []) + blockers))
        elif decision == "warn":
            row["risk_flags"] = sorted(set(list(row.get("risk_flags", []) or []) + list(alignment.get("warnings", []) or [])))
        out.append(row)
    return out


def alignment_blocks_phase2(alignment: dict[str, Any] | None) -> bool:
    if not isinstance(alignment, dict):
        return False
    return str(alignment.get("decision", "")).strip() == "block"


def load_skill_metadata_from_db(skill_id: str, db_path: str = "instance/kumon_math.db") -> dict[str, Any]:
    import sqlite3
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    con = sqlite3.connect(str(root / db_path))
    con.row_factory = sqlite3.Row
    meta: dict[str, Any] = {"skill_id": skill_id}
    row = con.execute(
        "SELECT skill_id, skill_ch_name, skill_en_name, category, description FROM skills_info WHERE skill_id=?",
        (skill_id,),
    ).fetchone()
    if row:
        meta.update(dict(row))
    cur = con.execute(
        "SELECT chapter, section, volume, curriculum, grade FROM skill_curriculum WHERE skill_id=? ORDER BY display_order LIMIT 1",
        (skill_id,),
    ).fetchone()
    if cur:
        cur_d = dict(cur)
        meta["chapter"] = cur_d.get("chapter", "")
        meta["section_code"] = cur_d.get("section", "")
        meta["volume"] = cur_d.get("volume", "")
        meta["curriculum"] = cur_d.get("curriculum", "")
        meta["grade"] = cur_d.get("grade", "")
    con.close()
    if not meta.get("skill_ch_name"):
        meta["skill_ch_name"] = skill_id
    return meta


def _stem_preview(feature: dict[str, Any], limit: int = 80) -> str:
    text = str(feature.get("question_text", "")).strip()
    text = re.sub(r"\s+", " ", text)
    return text[:limit] + ("..." if len(text) > limit else "")


def build_source_example_alignment_report(
    skill_id: str,
    skill_metadata: dict[str, Any] | None,
    features: list[dict[str, Any]],
    *,
    examples: list[dict[str, Any]] | None = None,
    main_skill_anchor: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else build_main_skill_anchor(
        skill_id, skill_metadata
    )
    skill_terms = extract_skill_terms(skill_id, skill_metadata)
    ex_by_id = {}
    for ex in examples or []:
        if isinstance(ex, dict):
            eid = ex.get("id") or ex.get("example_id")
            if eid is not None:
                ex_by_id[eid] = ex
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for feat in features:
        if not isinstance(feat, dict):
            continue
        ex_id = feat.get("source_example_id")
        ex_row = ex_by_id.get(ex_id, {})
        if example_skill_id_mismatch(ex_row, skill_id):
            excluded.append(
                {
                    "example_id": ex_id,
                    "target_task": feat.get("target_task", ""),
                    "task_family": feat.get("task_family", ""),
                    "alignment_score": 0.0,
                    "aligned_with_skill": False,
                    "included_in_phase1": False,
                    "exclude_reason": "skill_id_mismatch",
                    "skill_id": skill_id,
                    "title_stem_preview": _stem_preview(feat),
                }
            )
            continue
        row = evaluate_source_example_alignment(skill_terms, feat, main_skill_anchor=anchor)
        row["skill_id"] = skill_id
        row["title_stem_preview"] = _stem_preview(feat)
        if row.get("included_in_phase1"):
            included.append(feat)
        else:
            excluded.append(row)
    return included, excluded


def merge_alignment_into_gates(gates: dict[str, Any], alignment: dict[str, Any]) -> dict[str, Any]:
    out = dict(gates)
    if not alignment_blocks_phase2(alignment):
        return out
    blockers = list(alignment.get("blockers", []) or [])
    runtime = out.get("runtime_ready_gate", {}) if isinstance(out.get("runtime_ready_gate"), dict) else {}
    runtime["status"] = "blocked_semantic_alignment"
    runtime["allowed"] = False
    runtime["blockers"] = sorted(set(list(runtime.get("blockers", []) or []) + blockers + ["semantic_alignment_blocked"]))
    out["runtime_ready_gate"] = runtime
    gen = out.get("generator_draft_gate", {}) if isinstance(out.get("generator_draft_gate"), dict) else {}
    gen["status"] = "generator_draft_blocked"
    gen["allowed"] = False
    gen["warnings"] = sorted(set(list(gen.get("warnings", []) or []) + list(alignment.get("warnings", []) or [])))
    out["generator_draft_gate"] = gen
    cls = out.get("classifier_gate", {}) if isinstance(out.get("classifier_gate"), dict) else {}
    cls["warnings"] = sorted(set(list(cls.get("warnings", []) or []) + ["semantic_alignment_blocked"]))
    out["classifier_gate"] = cls
    ex = out.get("exception_review_gate", {}) if isinstance(out.get("exception_review_gate"), dict) else {}
    reasons = list(ex.get("reasons", []) or [])
    reasons.extend(blockers)
    ex["reasons"] = sorted(set(reasons))
    ex["required"] = True
    out["exception_review_gate"] = ex
    return out
