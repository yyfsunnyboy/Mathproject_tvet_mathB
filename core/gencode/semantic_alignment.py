from __future__ import annotations

import re
from collections import Counter
from typing import Any

from core.gencode.classification_policy import apply_final_classification_to_features
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
    same_family_extension_allowed,
    task_family_for_task,
)

_NON_SEMANTIC_REVIEW_CANDIDATE_SOURCES = frozenset(
    {
        "ai_needs_review",
        "rule_fallback_ai_unavailable",
        "needs_review",
        "partial_unavailable",
        "unclassified",
        "low_confidence_ai",
    }
)

_NON_BLOCKING_ALIGNMENT_KINDS = frozenset(
    {
        "anchor_subskill_match",
        "rule_fallback_same_family",
        "same_as_main_skill",
        "same_family_extension",
        "section_scope_subskill_extension",
        "inherited_from_previous_context",
        "enrichment_source",
        "source_quality_reject",
    }
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
    "judge_function_relation": ("是否為函數", "是否为函数", "對應關係", "对应关系", "function relation"),
    "judge_function_from_mapping": ("箭頭圖", "箭头图", "表格", "集合", "mapping", "arrow diagram"),
    "evaluate_function_value": ("函數值", "函数值", "代入", "f(", "g("),
    "interpret_function_notation": ("函數記號", "函数记号", "f\\left", "函數的定義", "函数的定义"),
    "judge_domain_range_basic": ("定義域", "定义域", "值域", "domain", "range"),
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
    """Task-level expectations from skill terms (delegates to main_skill_anchor subskill inference)."""
    from core.gencode.main_skill_anchor import infer_expected_subskill_candidates

    skill_families = infer_skill_families_from_terms(skill_terms)
    candidates, _scope = infer_expected_subskill_candidates(skill_terms, skill_families)
    tasks = {c for c in candidates if not str(c).endswith("_family")}
    if tasks:
        return tasks
    for task, aliases in TASK_TAXONOMY.items():
        alias_tokens = {task, *_tokenize(" ".join(aliases))}
        if skill_terms & alias_tokens:
            tasks.add(task)
    return tasks


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


def _uniform_core_target_task(features: list[dict[str, Any]]) -> tuple[str, float, int]:
    valid_core_tasks = [
        str(f.get("target_task", "")).strip()
        for f in features
        if isinstance(f, dict)
        and str(f.get("induction_tier", "core")).strip() == "core"
        and not f.get("source_quality_reject")
        and str(f.get("target_task", "")).strip()
        and str(f.get("target_task", "")).strip() not in {"unknown", "needs_review"}
    ]
    if not valid_core_tasks:
        return "", 0.0, 0
    counter = Counter(valid_core_tasks)
    task, count = counter.most_common(1)[0]
    return task, count / len(valid_core_tasks), len(valid_core_tasks)


def evaluate_source_example_alignment(
    skill_terms: set[str],
    feature: dict[str, Any],
    *,
    main_skill_anchor: dict[str, Any] | None = None,
    for_core_induction: bool = True,
) -> dict[str, Any]:
    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else {}
    sc = feature.get("semantic_classification") if isinstance(feature.get("semantic_classification"), dict) else {}
    ex_terms = extract_source_terms_from_features([feature])
    score = _overlap_score(skill_terms, ex_terms)
    expected_families = set(anchor.get("expected_task_families") or []) or infer_skill_families_from_terms(skill_terms)
    task = str(sc.get("final_target_task") or feature.get("target_task", "")).strip()
    family = str(
        sc.get("final_task_family") or feature.get("task_family") or task_family_for_task(task)
    ).strip()
    raw_expected = anchor.get("expected_subskill_candidates") or []
    expected_tasks = {t for t in raw_expected if t and not str(t).endswith("_family")}
    if not expected_tasks:
        expected_tasks = infer_expected_tasks(skill_terms)
    scope = str(anchor.get("skill_anchor_scope", "default")).strip() or "default"
    cand_src = str(sc.get("candidate_source", "")).strip()
    classifier_source = str(sc.get("classifier_source", "")).strip()
    skill_scope_trusted = bool(sc.get("skill_scope_trusted", True))
    rule_task = str(sc.get("rule_target_task", "")).strip()
    rule_family = str(sc.get("rule_task_family", "")).strip() or task_family_for_task(rule_task)
    ai_status = str(sc.get("ai_semantic_status", "")).strip()

    exclude_reason = ""
    alignment_kind = ""
    aligned = False
    included_in_phase1 = False
    pass_with_warning = False
    requires_human_action = bool(sc.get("requires_human_action", False))
    task_family_match = bool(expected_families and family and family in expected_families)
    subskill_match = bool(expected_tasks and task and task in expected_tasks)

    induction_tier = str(feature.get("induction_tier", "core")).strip() or "core"
    if bool(feature.get("source_quality_reject")):
        alignment_kind = "source_quality_reject"
        aligned = False
        included_in_phase1 = False
        requires_human_action = True
        exclude_reason = "source_quality_reject"
    elif induction_tier == "enrichment":
        alignment_kind = "enrichment_source"
        aligned = False
        included_in_phase1 = False
        requires_human_action = False
        exclude_reason = "enrichment_not_core_induction"
    elif task in {"", "needs_review", "unknown"}:
        # SOP v0.2: Truly review-required classification only if final classification is not mapped.
        # AI/Registry/Parser raw results are only used as evidence, final classification is the only source.
        source_belongs_default = bool(anchor.get("source_belongs_to_current_skill_by_default", False))
        explicit_remap = str(sc.get("source_mapping_warning", "")).strip() in {"expected_family_mismatch"}
        has_outside_family_evidence = bool(rule_family and expected_families and rule_family not in expected_families)
        
        if source_belongs_default and not has_outside_family_evidence and not explicit_remap:
            if rule_task and expected_tasks and rule_task in expected_tasks:
                alignment_kind = "rule_fallback_same_family"
                task = rule_task
                family = rule_family
                aligned = True
                included_in_phase1 = True
                requires_human_action = True
                task_family_match = True
                subskill_match = True
            else:
                alignment_kind = "same_as_main_skill"
                aligned = True
                included_in_phase1 = True
                requires_human_action = True
                task_family_match = True
        else:
            alignment_kind = "needs_review"
            aligned = False
            included_in_phase1 = bool(for_core_induction)
            requires_human_action = True
            exclude_reason = ""
    elif cand_src == "outsider" or sc.get("classifier_source") == "ai_outsider_candidate":
        alignment_kind = "outsider_candidate_warning"
        aligned = True
        included_in_phase1 = True
        pass_with_warning = True
        requires_human_action = True
        task_family_match = False
    elif not task or task == "compute_numeric":
        exclude_reason = "unclassified_low_confidence"
        alignment_kind = "unclassified_low_confidence"
    elif subskill_match or (skill_scope_trusted and task_family_match):
        alignment_kind = "anchor_subskill_match"
        aligned = True
        included_in_phase1 = True
        subskill_match = bool(subskill_match or task in expected_tasks)
    elif task_family_match and expected_tasks and task and task not in expected_tasks:
        exclude_reason = ""
        if scope in {"medium", "broad"}:
            alignment_kind = "section_scope_subskill_extension"
            pass_with_warning = True
        else:
            alignment_kind = "same_family_subskill_mismatch"
        subskill_match = False
        aligned = True
        included_in_phase1 = True
        if scope == "narrow":
            requires_human_action = True
        else:
            pass_with_warning = True
    elif not expected_families and not expected_tasks:
        alignment_kind = "same_family_match"
        aligned = True
        included_in_phase1 = True
    else:
        if same_family_extension_allowed(expected_families, family, scope=scope):
            alignment_kind = "same_family_extension"
            aligned = True
            included_in_phase1 = True
            pass_with_warning = True
        elif skill_scope_trusted and cand_src in {"anchor", "structure", "rule"}:
            alignment_kind = "anchor_subskill_match"
            aligned = True
            included_in_phase1 = True
        else:
            exclude_reason = "unclassified_low_confidence"
            alignment_kind = "unclassified_low_confidence"

    # A trusted final classification is stronger evidence than lexical overlap.
    score_val = round(score, 4)
    if task in expected_tasks and family in expected_families and sc.get("source_quality_status") != "rejected":
        score_val = max(score_val, 0.8)
            
    return {
        "example_id": feature.get("source_example_id"),
        "target_task": task,
        "task_family": family,
        "alignment_score": score_val,
        "aligned_with_skill": aligned,
        "included_in_phase1": included_in_phase1,
        "exclude_reason": exclude_reason,
        "alignment_kind": alignment_kind,
        "skill_id_match": True,
        "task_family_match": task_family_match,
        "subskill_match": subskill_match,
        "pass_with_warning": pass_with_warning,
        "requires_human_action": requires_human_action,
        "induction_tier": induction_tier,
        "included_in_core_induction": induction_tier == "core" and bool(included_in_phase1),
        "enrichment_reasons": list(feature.get("enrichment_reasons") or []),
        "source_quality_issues": list(feature.get("source_quality_issues") or []),
        "source_quality_reject": bool(feature.get("source_quality_reject")),
        "candidate_only": bool(feature.get("candidate_only")),
        "classification_source": classifier_source or str(sc.get("classifier_source", "")).strip(),
        "induction_eligibility": (
            "excluded_source_quality_reject"
            if bool(feature.get("source_quality_reject"))
            else ("excluded_enrichment" if induction_tier == "enrichment" else ("eligible" if included_in_phase1 else "excluded"))
        ),
    }


def _features_for_alignment_blockers(source_features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Use core-tier examples for induction blockers; fall back when tiers are not annotated."""
    if not source_features:
        return []
    has_tier = any(
        isinstance(f, dict) and str(f.get("induction_tier", "")).strip()
        for f in source_features
    )
    if not has_tier:
        return list(source_features)
    core = [
        f
        for f in source_features
        if isinstance(f, dict) and str(f.get("induction_tier", "core")).strip() != "enrichment"
    ]
    return core


def evaluate_semantic_alignment(
    skill_id: str,
    *,
    skill_metadata: dict[str, Any] | None = None,
    source_features: list[dict[str, Any]],
    candidate_specs: list[dict[str, Any]],
    min_examples_block: int = 4,
    main_skill_anchor: dict[str, Any] | None = None,
    ai_semantic_status: str = "",
    examples: list[dict[str, Any]] | None = None,
    induction_source_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else build_main_skill_anchor(
        skill_id, skill_metadata
    )
    source_features = apply_final_classification_to_features(source_features)
    blocker_features = _features_for_alignment_blockers(source_features)
    enrichment_count = int((induction_source_report or {}).get("enrichment_example_count", 0) or 0)
    core_count = int((induction_source_report or {}).get("core_example_count", len(blocker_features)) or 0)
    ai_status = str(ai_semantic_status or "").strip()
    rule_fallback_only = ai_status == "unavailable"
    skill_terms = extract_skill_terms(skill_id, skill_metadata)
    source_terms = extract_source_terms_from_features(blocker_features or source_features)
    expected_tasks = set(anchor.get("expected_subskill_candidates") or []) or infer_expected_tasks(skill_terms)
    expected_families = set(anchor.get("expected_task_families") or []) or infer_skill_families_from_terms(skill_terms)
    dominant_task, dominant_ratio = _dominant_source_task(blocker_features or source_features)
    uniform_core_task, uniform_core_ratio, uniform_core_count = _uniform_core_target_task(blocker_features or source_features)
    src_family_dist = source_family_distribution(blocker_features or source_features)
    source_families = set(src_family_dist.keys())
    dom_families, dom_family_ratio = dominant_source_families(blocker_features or source_features)

    per_spec_scores: list[dict[str, Any]] = []
    spec_task_scores: list[float] = []
    candidate_families: set[str] = set()
    blockers: list[str] = []
    warnings: list[str] = []

    skill_id_mismatch_examples: list[int] = []
    source_quality_reject_examples: list[int] = []
    for ex in examples or []:
        if isinstance(ex, dict) and example_skill_id_mismatch(ex, skill_id):
            eid = ex.get("id") or ex.get("example_id")
            if isinstance(eid, int):
                skill_id_mismatch_examples.append(eid)
    for feat in source_features:
        if not isinstance(feat, dict):
            continue
        if feat.get("source_quality_reject") and isinstance(feat.get("source_example_id"), int):
            source_quality_reject_examples.append(int(feat.get("source_example_id")))
    if source_quality_reject_examples:
        warnings.append("source_quality_reject_examples_present")
    if skill_id_mismatch_examples:
        blockers.append("skill_id_mismatch")
        warnings.append("source_example_skill_id_mismatch")

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
    usable_features = [
        feat
        for feat in blocker_features
        if isinstance(feat, dict) and not feat.get("source_quality_reject")
    ]
    trusted_classification_count = sum(
        1
        for feat in usable_features
        if (
            str(
                (
                    feat.get("semantic_classification")
                    if isinstance(feat.get("semantic_classification"), dict)
                    else {}
                ).get("final_task_family")
                or feat.get("task_family")
                or task_family_for_task(str(feat.get("target_task", "")))
            ).strip()
            in expected_families
        )
    )
    if usable_features and trusted_classification_count:
        trusted_ratio = trusted_classification_count / len(usable_features)
        skill_source_score = max(skill_source_score, trusted_ratio * 0.8)
    skill_problem_type_score = min(spec_task_scores) if spec_task_scores else 0.0
    source_problem_type_score = max((x.get("source_problem_type_score", 0.0) for x in per_spec_scores), default=0.0)
    uniform_core_threshold_relaxed = bool(uniform_core_task and uniform_core_ratio >= 1.0 and uniform_core_count > 0)
    if uniform_core_threshold_relaxed:
        skill_source_score = max(skill_source_score, 0.8)
        skill_problem_type_score = max(skill_problem_type_score, 0.8)
        source_problem_type_score = max(source_problem_type_score, 0.8)
        warnings.append("uniform_core_target_task_alignment_threshold_relaxed")

    needs_review_count = 0
    outsider_count = 0
    anchor_scoped_count = 0
    fallback_same_main_count = 0
    source_belongs_default = bool(anchor.get("source_belongs_to_current_skill_by_default", False))
    for feat in blocker_features:
        if not isinstance(feat, dict):
            continue
        if feat.get("source_quality_reject"):
            continue
        sc = feat.get("semantic_classification") if isinstance(feat.get("semantic_classification"), dict) else {}
        src = str(sc.get("candidate_source", "")).strip()
        ai_status_row = str(sc.get("ai_semantic_status", "")).strip()
        ai_best = str(sc.get("ai_best_candidate_id", "")).strip()
        rule_task = str(sc.get("rule_target_task", "")).strip()
        rule_family = str(sc.get("rule_task_family") or task_family_for_task(rule_task) or feat.get("task_family") or "").strip()
        explicit_remap = str(sc.get("source_mapping_warning", "")).strip() in {"expected_family_mismatch"}
        has_outside_family_evidence = bool(rule_family and expected_families and rule_family not in expected_families)
        non_semantic_needs_review = (
            src in _NON_SEMANTIC_REVIEW_CANDIDATE_SOURCES
            or ai_status_row in {"partial_unavailable", "unavailable"}
        )
        if src == "needs_review" or ai_best == "needs_review":
            if non_semantic_needs_review and source_belongs_default and not has_outside_family_evidence and not explicit_remap:
                fallback_same_main_count += 1
                warnings.append("ai_unavailable_fallback_to_same_as_main")
                anchor_scoped_count += 1
                if rule_task and rule_task in expected_tasks:
                    warnings.append("rule_fallback_same_family_examples")
            else:
                needs_review_count += 1
        elif src == "outsider":
            outsider_count += 1
        elif sc.get("in_anchor_scope") or src in {"anchor", "structure", "rule"}:
            anchor_scoped_count += 1

    skill_scope_trusted = anchor_scoped_count > 0 or rule_fallback_only
    in_scope_families = {
        str(
            (f.get("semantic_classification") or {}).get("final_task_family")
            or f.get("task_family")
            or task_family_for_task(str(f.get("target_task", "")))
        ).strip()
        for f in blocker_features
        if isinstance(f, dict)
    }
    in_scope_families.discard("")

    if source_families and not families_compatible(source_families):
        if rule_fallback_only:
            warnings.append("ai_semantic_classifier_unavailable")
            warnings.append("rule_fallback_may_cause_false_mixed_source_families")
        elif skill_scope_trusted and (in_scope_families <= expected_families or in_scope_families & expected_families):
            warnings.append("multiple_subskills_in_skill_scope")
        else:
            blockers.append("mixed_source_families")
            blockers.append("source_examples_mismatch")
    elif expected_families and source_families and not (source_families <= expected_families or source_families & expected_families):
        if not skill_scope_trusted and dom_family_ratio >= 0.75:
            blockers.append("source_examples_mismatch")
    elif expected_families and dom_families and not (dom_families & expected_families):
        if not skill_scope_trusted and dom_family_ratio >= 0.75:
            blockers.append("source_examples_mismatch")
            warnings.append(
                "來源題多數與目前技能語意不一致，疑似 skill mapping 錯誤；請先檢查來源題歸屬，不建議進 Phase 2。"
            )

    outside_expected = [
        f
        for f in blocker_features
        if isinstance(f, dict)
        and str(
            (f.get("semantic_classification") or {}).get("candidate_source", "")
        ).strip()
        == "outsider"
    ]
    task_dist = Counter(
        str(f.get("target_task", "")).strip()
        for f in blocker_features
        if isinstance(f, dict) and str(f.get("target_task", "")).strip()
    )
    subskill_mismatch_rows: list[dict[str, Any]] = []
    unresolved_review_rows: list[dict[str, Any]] = []
    examples_outside_subskills: list[int] = []
    for feat in blocker_features:
        if not isinstance(feat, dict):
            continue
        row = evaluate_source_example_alignment(skill_terms, feat, main_skill_anchor=anchor)
        kind = str(row.get("alignment_kind", "")).strip()
        fam = str(row.get("task_family", "")).strip()
        if kind == "same_family_subskill_mismatch":
            subskill_mismatch_rows.append(row)
            ex_id = feat.get("source_example_id")
            if isinstance(ex_id, int):
                examples_outside_subskills.append(ex_id)
        if kind in _NON_BLOCKING_ALIGNMENT_KINDS:
            continue
        if kind in {"needs_review", "outside_family", "semantic_mismatch", "suspected_wrong_skill", "needs_remap", "explicit_wrong_skill", "unresolved_needs_review"}:
            unresolved_review_rows.append(row)
            continue
        if kind == "outsider_candidate_warning":
            # outside-family warning without same-family fallback should still count as unresolved.
            if fam and expected_families and fam in expected_families:
                continue
            unresolved_review_rows.append(row)
            continue
        if kind == "unclassified_low_confidence":
            unresolved_review_rows.append(row)
            continue

    # Final blocker counting must follow final row-level alignment kinds, not raw candidate_source.
    needs_review_count = len(unresolved_review_rows)
    outsider_count = sum(1 for r in unresolved_review_rows if str(r.get("alignment_kind", "")).strip() == "outsider_candidate_warning")
    if subskill_mismatch_rows:
        warnings.append("same_family_subskill_mismatch")
        narrow_scope = str(anchor.get("skill_anchor_scope", "")).strip() == "narrow"
        if narrow_scope or any(r.get("requires_human_action") for r in subskill_mismatch_rows):
            warnings.append(
                "來源題與技能屬於同一大類，但子技能不同；請確認是否要放在此技能底下。"
            )
    blocker_denominator = len(blocker_features) if blocker_features else len(source_features)
    if outsider_count >= max(1, blocker_denominator // 2) and blocker_denominator:
        warnings.append("majority_outsider_candidates_within_skill")

    effective_core_count = sum(
        1
        for f in blocker_features
        if isinstance(f, dict) and not f.get("source_quality_reject")
    )
    if core_count == 0 and enrichment_count > 0:
        blockers.append("low_core_source_examples")
        warnings.append("only_enrichment_examples_available_for_induction")
    elif effective_core_count < 3 and blocker_denominator > 0:
        warnings.append("low_source_examples")
    elif needs_review_count >= max(1, blocker_denominator // 2) and blocker_denominator:
        blockers.append("majority_needs_review")
        warnings.append("majority_sources_need_human_subskill_review")

    if (
        expected_families
        and blocker_denominator <= min_examples_block
        and dom_family_ratio >= 0.9
        and dom_families
        and not (dom_families & expected_families)
        and not skill_scope_trusted
    ):
        blockers.append("low_alignment_score")

    if candidate_families and source_families and not families_compatible(candidate_families | source_families):
        if not skill_scope_trusted and not rule_fallback_only:
            warnings.append("candidate_family_span_outside_skill_scope")

    unique_blockers = sorted(set(blockers))
    if uniform_core_threshold_relaxed:
        unique_blockers = [b for b in unique_blockers if b != "low_alignment_score"]
    if skill_scope_trusted or rule_fallback_only:
        unique_blockers = [
            b
            for b in unique_blockers
            if b not in {"mixed_source_families", "source_examples_mismatch", "expected_family_mismatch"}
        ]
    if rule_fallback_only:
        warnings.append("ai_first_mode_fell_back_to_rule_only")
    suggested_action = ""
    if subskill_mismatch_rows and not unique_blockers:
        suggested_action = "review_source_mapping_or_skill_scope"
    elif unique_blockers:
        suggested_action = "fix_skill_mapping_or_exclude_out_of_family_examples"
    if unique_blockers:
        decision = "block"
    elif subskill_mismatch_rows or warnings or skill_source_score < 0.25:
        decision = "warn"
        if skill_source_score < 0.25:
            warnings.append("alignment_score_below_recommended_threshold")
    else:
        decision = "pass"

    return {
        "main_skill_anchor": anchor,
        "ai_semantic_status": ai_status,
        "skill_terms": sorted(skill_terms),
        "source_terms": sorted(source_terms),
        "expected_subskill_candidates": sorted(expected_tasks),
        "observed_target_task_distribution": dict(task_dist),
        "same_family_subskill_mismatch_examples": subskill_mismatch_rows,
        "examples_outside_expected_subskills": sorted(set(examples_outside_subskills)),
        "suggested_action": suggested_action,
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
        "uniform_core_target_task": uniform_core_task,
        "uniform_core_target_task_ratio": round(uniform_core_ratio, 4),
        "uniform_core_target_task_count": uniform_core_count,
        "uniform_core_threshold_relaxed": uniform_core_threshold_relaxed,
        "dominant_source_family": sorted(dom_families),
        "dominant_source_family_ratio": round(dom_family_ratio, 4),
        "skill_source_score": round(skill_source_score, 4),
        "skill_problem_type_score": round(skill_problem_type_score, 4),
        "source_problem_type_score": round(source_problem_type_score, 4),
        "per_problem_type_scores": per_spec_scores,
        "decision": decision,
        "blockers": unique_blockers,
        "warnings": sorted(set(warnings)),
        "induction_core_example_count": core_count,
        "induction_enrichment_example_count": enrichment_count,
        "source_quality_reject_examples": sorted(set(source_quality_reject_examples)),
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
