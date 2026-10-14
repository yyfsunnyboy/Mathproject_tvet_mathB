# -*- coding: utf-8 -*-
"""Oblique-triangle measurement facade for Math B2 §2-2-4.

Reuses Law-of-Sines / Law-of-Cosines solvers via cross-domain delegation.
No duplicated trigonometry math — only measurement skill routing + stems.
"""

from __future__ import annotations

from typing import Any

from core.domain.trigonometry_law_of_cosines_domain import (
    SIDE_BY_COSINES_OP,
    build_trigonometry_law_of_cosines_matrix,
    validate_trigonometry_law_of_cosines_matrix,
)
from core.domain.trigonometry_law_of_sines_domain import (
    SIDE_BY_SINES_OP,
    build_trigonometry_law_of_sines_matrix,
    validate_trigonometry_law_of_sines_matrix,
)

OPS = frozenset({SIDE_BY_SINES_OP, SIDE_BY_COSINES_OP})

_DELEGATE = {
    SIDE_BY_SINES_OP: "trigonometry.law_of_sines",
    SIDE_BY_COSINES_OP: "trigonometry.law_of_cosines",
}


def _triangle_diagram_spec(operation: str, givens: dict[str, Any]) -> dict[str, Any]:
    if operation == SIDE_BY_SINES_OP:
        parameters = {
            "angles_deg": {
                "A": givens["known_angle_degrees"],
                "C": givens["target_angle_degrees"],
            },
            "sides": {"a": givens["known_side"]},
        }
        show = {"angles": ["A", "C"], "sides": ["a"], "unknown_sides": ["c"]}
    else:
        parameters = {
            "angles_deg": {"A": givens["included_angle_degrees"]},
            "sides": {"b": givens["side_b"], "c": givens["side_c"]},
        }
        show = {"angles": ["A"], "sides": ["b", "c"], "unknown_sides": ["a"]}
    return {
        "version": 1,
        "type": "triangle",
        "vertices": ["A", "B", "C"],
        "parameters": parameters,
        "side_vertices": {
            "a": ["B", "C"],
            "b": ["C", "A"],
            "c": ["A", "B"],
        },
        "show": show,
    }


def build_trigonometry_oblique_triangle_measurement_matrix(
    *,
    operation: str | None = None,
    domain_operation: str | None = None,
    constraints: dict[str, Any] | None = None,
    seed: int | None = None,
    curriculum_profile: str | None = None,
    difficulty_profile: str | None = None,
    **data: Any,
) -> dict[str, Any]:
    op = str(operation or domain_operation or "").strip()
    if op not in OPS:
        raise ValueError(f"unsupported_oblique_triangle_measurement_operation:{op}")

    raw = {**(constraints or {}), **data}
    # Drop facade-only hints so delegated validators stay pure.
    raw.pop("question_text_hint", None)
    raw.pop("composition_skill", None)

    if op == SIDE_BY_SINES_OP:
        matrix = build_trigonometry_law_of_sines_matrix(
            operation=op,
            seed=seed,
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
            **raw,
        )
    else:
        matrix = None
        for offset in range(24):
            candidate = build_trigonometry_law_of_cosines_matrix(
                operation=op,
                seed=None if seed is None else seed + offset,
                curriculum_profile=curriculum_profile,
                difficulty_profile=difficulty_profile,
                **raw,
            )
            if str((candidate.get("givens") or {}).get("included_angle_degrees")) != "90":
                matrix = candidate
                break
        if matrix is None:
            raise RuntimeError("oblique_triangle_non_right_sample_exhausted")

    facts = matrix.setdefault("validation_facts", {})
    facts["domain_operation"] = op
    facts["cross_domain_delegate"] = _DELEGATE[op]
    facts["composition_skill"] = "vh_數學B2_SubSection_2_2_4"
    matrix["diagram_spec"] = _triangle_diagram_spec(op, matrix["givens"])

    # Light stem rewrite for measurement context when still using generic △ABC stem.
    if not raw.get("question_text"):
        q = str(matrix.get("question_text") or matrix.get("question") or "")
        rewritten = (
            q.replace("已知△ABC中", "測量非直角△ABC，已知")
            .replace("在△ABC中，已知", "測量非直角△ABC，已知")
            .replace("設△ABC的三邊長", "測量非直角△ABC，三邊長")
        )
        if rewritten != q:
            matrix["question_text"] = rewritten
            matrix["question"] = rewritten
    return matrix


def validate_trigonometry_oblique_triangle_measurement_matrix(matrix: dict[str, Any]) -> bool:
    try:
        op = str((matrix.get("validation_facts") or {}).get("domain_operation") or "").strip()
        # Strip facade-only facts for delegate validate rebuild equality.
        # Delegate validators rebuild from givens+operation and compare answers.
        if op == SIDE_BY_SINES_OP:
            return validate_trigonometry_law_of_sines_matrix(matrix)
        if op == SIDE_BY_COSINES_OP:
            return validate_trigonometry_law_of_cosines_matrix(matrix)
        return False
    except (KeyError, TypeError, ValueError):
        return False
