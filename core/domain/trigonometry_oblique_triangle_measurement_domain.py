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
        matrix = build_trigonometry_law_of_cosines_matrix(
            operation=op,
            seed=seed,
            curriculum_profile=curriculum_profile,
            difficulty_profile=difficulty_profile,
            **raw,
        )

    facts = matrix.setdefault("validation_facts", {})
    facts["domain_operation"] = op
    facts["cross_domain_delegate"] = _DELEGATE[op]
    facts["composition_skill"] = "vh_數學B2_SubSection_2_2_4"

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
