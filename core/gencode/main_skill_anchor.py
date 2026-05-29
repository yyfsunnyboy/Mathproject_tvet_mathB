from __future__ import annotations

import re
from typing import Any

from core.gencode.task_families import (
    ABSOLUTE_VALUE_INEQUALITY_FAMILY,
    AXIS_DISTANCE_FAMILY,
    CLASSIFY_QUADRANT_FAMILY,
    COORDINATE_SYSTEM_FAMILY,
    DIVISION_POINT_COORDINATES_FAMILY,
    DIVISION_POINT_COORDINATES_TASKS,
    DISTANCE_BETWEEN_TWO_POINTS_FAMILY,
    DISTANCE_BETWEEN_TWO_POINTS_TASKS,
    infer_skill_families_from_terms,
)

_CAMEL_SPLIT = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Za-z])(?=[0-9])")

# Exclusive skill titles → single subskill (narrow scope).
_EXCLUSIVE_SKILL_TITLE_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("compute_midpoint_coordinates", ("中點坐標", "中点坐标", "midpoint coordinates", "midpoint coordinate")),
    ("compute_centroid_coordinates", ("重心坐標", "重心坐标", "centroid coordinates", "centroid coordinate")),
    (
        "compute_internal_division_point_coordinates",
        ("內分點坐標", "内分点坐标", "內分坐標", "内分坐标", "internal division point"),
    ),
    (
        "compute_external_division_point_coordinates",
        ("外分點坐標", "外分点坐标", "外分坐標", "外分坐标", "external division point"),
    ),
)

# Umbrella division-point skill names (broad scope — multiple subskills allowed).
_BROAD_DIVISION_SKILL_PATTERNS: tuple[str, ...] = (
    "分點坐標",
    "分点坐标",
    "division point coordinates",
    "divisionpointcoordinates",
    "division point coordinate",
)

# Per-subskill hints when skill name mentions a concept without full title.
_DIVISION_SUBSKILL_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("compute_midpoint_coordinates", ("中點", "中点", "midpoint")),
    ("compute_centroid_coordinates", ("重心", "centroid", "形心")),
    ("compute_internal_division_point_coordinates", ("內分", "内分", "internal division", "section formula")),
    ("compute_external_division_point_coordinates", ("外分", "external division")),
)


def _expand_skill_id_tokens(skill_id: str) -> set[str]:
    raw = str(skill_id or "").strip()
    parts = re.split(r"[_\\-]+", raw)
    tokens: set[str] = set()
    for p in parts:
        p = p.strip()
        if not p or p.isdigit():
            continue
        tokens.add(p.lower())
        tokens.update(_CAMEL_SPLIT.sub(" ", p).lower().split())
    return {t for t in tokens if len(t) >= 2}


def _terms_blob(skill_terms: set[str]) -> str:
    return " ".join(sorted(skill_terms)).lower()


def _phrase_in_skill_terms(phrase: str, skill_terms: set[str]) -> bool:
    p = str(phrase or "").strip().lower()
    if not p:
        return False
    blob = _terms_blob(skill_terms)
    if p in blob:
        return True
    if len(p) >= 2 and p in skill_terms:
        return True
    return False


def infer_narrow_subskills_from_skill_terms(skill_terms: set[str]) -> set[str]:
    """Map skill naming tokens to specific subskills (no whole-family flood)."""
    found: set[str] = set()
    for task, phrases in _EXCLUSIVE_SKILL_TITLE_PATTERNS:
        if any(_phrase_in_skill_terms(ph, skill_terms) for ph in phrases):
            found.add(task)
    if found:
        return found
    for task, hints in _DIVISION_SUBSKILL_HINTS:
        if any(_phrase_in_skill_terms(h, skill_terms) for h in hints):
            found.add(task)
    return found


def infer_skill_anchor_scope(skill_terms: set[str], expected_families: set[str]) -> str:
    """
    narrow: skill title targets one subskill (e.g. 中點坐標).
    broad: umbrella skill (e.g. 分點坐標) allows multiple subskills in same family.
    default: inferred from taxonomy hits only.
    """
    if any(_phrase_in_skill_terms(p, skill_terms) for p in _BROAD_DIVISION_SKILL_PATTERNS):
        return "broad"
    div_narrow = infer_narrow_subskills_from_skill_terms(skill_terms) & set(DIVISION_POINT_COORDINATES_TASKS)
    if len(div_narrow) == 1:
        return "narrow"
    if len(div_narrow) > 1:
        return "broad"
    if DIVISION_POINT_COORDINATES_FAMILY in expected_families:
        blob = _terms_blob(skill_terms)
        if any(h in blob for _, hints in _DIVISION_SUBSKILL_HINTS for h in hints):
            return "narrow"
    return "default"


def infer_expected_subskill_candidates(
    skill_terms: set[str],
    expected_families: set[str],
) -> tuple[list[str], str]:
    """Return (sorted subskill ids, skill_anchor_scope)."""
    scope = infer_skill_anchor_scope(skill_terms, expected_families)
    candidates: set[str] = set()
    narrow = infer_narrow_subskills_from_skill_terms(skill_terms)

    if scope == "narrow" and narrow:
        candidates |= narrow
    elif scope == "broad":
        if DIVISION_POINT_COORDINATES_FAMILY in expected_families:
            candidates |= set(DIVISION_POINT_COORDINATES_TASKS)
    else:
        candidates |= narrow
        if DIVISION_POINT_COORDINATES_FAMILY in expected_families and not (
            candidates & set(DIVISION_POINT_COORDINATES_TASKS)
        ):
            candidates |= set(DIVISION_POINT_COORDINATES_TASKS)
        if DISTANCE_BETWEEN_TWO_POINTS_FAMILY in expected_families and not (
            candidates & set(DISTANCE_BETWEEN_TWO_POINTS_TASKS)
        ):
            candidates |= set(DISTANCE_BETWEEN_TWO_POINTS_TASKS)

    if CLASSIFY_QUADRANT_FAMILY in expected_families:
        candidates.add("classify_quadrant")
    if AXIS_DISTANCE_FAMILY in expected_families:
        candidates.add("choose_possible_coordinate")
    if COORDINATE_SYSTEM_FAMILY in expected_families:
        candidates |= {"classify_quadrant", "choose_possible_coordinate", "compute_axis_distance"}

    if not candidates and expected_families:
        for fam in expected_families:
            candidates.add(fam)

    return sorted(candidates), scope


def build_main_skill_anchor(skill_id: str, skill_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build skill-scoped semantic anchor before subskill / problem_type induction."""
    from core.gencode.semantic_alignment import _split_skill_id, _tokenize, extract_skill_terms

    meta = skill_metadata if isinstance(skill_metadata, dict) else {}
    skill_terms = extract_skill_terms(skill_id, meta)
    skill_terms |= _expand_skill_id_tokens(skill_id)
    for ch in (
        meta.get("skill_ch_name", ""),
        meta.get("skill_en_name", ""),
        meta.get("chapter", ""),
        meta.get("section_code", ""),
        meta.get("unit_name", ""),
    ):
        skill_terms |= _tokenize(str(ch))
        skill_terms |= _split_skill_id(str(ch))

    expected_families = infer_skill_families_from_terms(skill_terms)
    subskill_candidates, skill_anchor_scope = infer_expected_subskill_candidates(skill_terms, expected_families)

    return {
        "skill_id": str(skill_id or "").strip(),
        "skill_ch_name": str(meta.get("skill_ch_name", "")).strip(),
        "skill_en_name": str(meta.get("skill_en_name", "")).strip(),
        "chapter": str(meta.get("chapter", "")).strip(),
        "section": str(meta.get("section_code", meta.get("section", ""))).strip(),
        "normalized_skill_terms": sorted(skill_terms),
        "expected_task_families": sorted(expected_families),
        "expected_math_objects": _expected_math_objects(expected_families),
        "expected_subskill_candidates": subskill_candidates,
        "skill_anchor_scope": skill_anchor_scope,
    }


def _expected_math_objects(families: set[str]) -> list[str]:
    objs: list[str] = []
    if DIVISION_POINT_COORDINATES_FAMILY in families:
        objs.extend(
            [
                "coordinate_point",
                "two_coordinate_points",
                "three_coordinate_points",
                "triangle",
                "centroid",
                "midpoint",
                "section_ratio",
                "coordinate_average",
            ]
        )
    if DISTANCE_BETWEEN_TWO_POINTS_FAMILY in families:
        objs.extend(["coordinate_point", "two_coordinate_points", "distance_formula", "segment_length"])
    if CLASSIFY_QUADRANT_FAMILY in families:
        objs.append("coordinate_point")
    return sorted(set(objs))


def example_skill_id_mismatch(example: dict[str, Any], skill_id: str) -> bool:
    ex_sid = str(example.get("skill_id") or example.get("skill") or "").strip()
    query = str(skill_id or "").strip()
    if not ex_sid or not query:
        return False
    return ex_sid != query
