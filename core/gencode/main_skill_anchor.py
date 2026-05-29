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
    GENERIC_NUMERIC_FAMILY,
    infer_skill_families_from_terms,
)

_CAMEL_SPLIT = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Za-z])(?=[0-9])")


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
    expected_tasks: set[str] = set()
    if DIVISION_POINT_COORDINATES_FAMILY in expected_families:
        expected_tasks |= set(DIVISION_POINT_COORDINATES_TASKS)
    if DISTANCE_BETWEEN_TWO_POINTS_FAMILY in expected_families:
        expected_tasks |= set(DISTANCE_BETWEEN_TWO_POINTS_TASKS)
    if CLASSIFY_QUADRANT_FAMILY in expected_families:
        expected_tasks.add("classify_quadrant")
    if AXIS_DISTANCE_FAMILY in expected_families:
        expected_tasks.add("choose_possible_coordinate")
    if COORDINATE_SYSTEM_FAMILY in expected_families:
        expected_tasks |= {"classify_quadrant", "choose_possible_coordinate", "compute_axis_distance"}

    subskill_candidates = sorted(expected_tasks) if expected_tasks else sorted(expected_families)

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
