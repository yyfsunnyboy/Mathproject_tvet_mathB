# -*- coding: utf-8 -*-
"""Presentation glue for trigonometry.angle components.

Mathematics stays in core.domain.trigonometry_angle_domain. This module only
invokes the shared Domain, runs the generic adapter, and patches answer_contract.
"""

from __future__ import annotations

from typing import Any

from core.domain.trigonometry_angle_domain import build_trigonometry_angle_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
from core.gencode.table_question_contract import normalize_table_question_payload

FIXED_DOMAIN_KEY = "trigonometry.angle"
DOMAIN_MODULE = "core.domain.trigonometry_angle_domain"
ENTRYPOINT = "build_trigonometry_angle_matrix"


def _needs_pi_form(value: Any) -> bool:
    text = str(value or "").strip().lower().replace("π", "pi")
    return "pi" in text


def _patch_pi_required_form(payload: dict[str, Any]) -> None:
    ac = dict(payload.get("answer_contract") or {})
    parts = ac.get("parts")
    if isinstance(parts, list):
        updated = []
        for part in parts:
            if not isinstance(part, dict):
                continue
            row = dict(part)
            expected = row.get("expected_answer")
            if _needs_pi_form(expected):
                row["checker"] = "expression_checker"
                row["checker_key"] = "expression_checker"
                row["equivalence_type"] = "algebraic_equivalent"
                row["required_form"] = "pi_expression"
            updated.append(row)
        ac["parts"] = updated
        payload["answer_contract"] = ac
        return
    expected = payload.get("answer")
    if _needs_pi_form(expected) and str(ac.get("checker") or "") in {
        "",
        "expression_checker",
        "expression_equivalence_checker",
        "integer_checker",
    }:
        ac["required_form"] = "pi_expression"
        ac["checker"] = "expression_checker"
        ac["checker_key"] = "expression_checker"
        ac["equivalence_type"] = "algebraic_equivalent"
        payload["answer_contract"] = ac
        payload["checker"] = "expression_checker"
        payload["checker_key"] = "expression_checker"


def _apply_table_fill(payload: dict[str, Any], matrix: dict[str, Any]) -> dict[str, Any]:
    givens = matrix.get("givens") if isinstance(matrix.get("givens"), dict) else {}
    visual = matrix.get("visual_spec") if isinstance(matrix.get("visual_spec"), dict) else {}
    rows = visual.get("rows") or givens.get("table_rows") or []
    blank_cells = visual.get("blank_cells") or givens.get("blank_cells") or []
    payload["table_data"] = {
        "type": "table_fill",
        "rows": rows,
        "blank_cells": blank_cells,
        "show_blank_labels": False,
        "blank_label_mode": "complete_table",
        "interaction_mode": "inline_input",
    }
    payload["answer_type"] = "table_fill"
    payload["presentation_mode"] = "inline_table_input"
    payload = normalize_table_question_payload(payload)
    ac = dict(payload.get("answer_contract") or {})
    ac["answer_type"] = "table_fill"
    ac["checker"] = "table_fill_checker"
    ac["checker_key"] = "table_fill_checker"
    ac["equivalence_type"] = "multi_part_answer"
    ui = dict(ac.get("ui_contract") or payload.get("ui_contract") or {})
    ui.update(
        {
            "response_mode": "table_fill",
            "text_input_enabled": True,
            "inline_table_inputs": True,
            "show_blank_labels": False,
            "blank_label_mode": "complete_table",
        }
    )
    ac["ui_contract"] = ui
    payload["answer_contract"] = ac
    payload["ui_contract"] = ui
    payload["answer_type"] = "table_fill"
    payload["checker"] = "table_fill_checker"
    payload["checker_key"] = "table_fill_checker"
    payload["presentation_mode"] = "inline_table_input"
    _patch_pi_required_form(payload)
    return payload


def generate_trigonometry_angle_payload(
    *,
    skill_id: str,
    domain_operation: str,
    presentation_mode: str,
    answer_type: str,
    problem_type_id: str,
    textbook_example_id: int,
    component_id: str,
    seed: int | None,
    extra_constraints: dict[str, Any] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from core.gencode.pipeline_orchestrator import _v3_invoke_domain_entrypoint
    from core.gencode.domain_matrix_adapter import normalize_domain_payload_to_v3_matrix

    kwargs = kwargs or {}
    constraints = dict(extra_constraints or {})
    constraints["skill_id"] = skill_id

    norm_context = {
        "skill_id": skill_id,
        "problem_type_id": problem_type_id,
        "seed": seed,
        "curriculum_profile": "vocational_high_b",
        "difficulty_profile": "easy",
        "answer_schema_key": "",
        "presentation_mode": presentation_mode,
        "answer_type": answer_type,
        "fixed_domain_key": FIXED_DOMAIN_KEY,
    }

    matrix = _v3_invoke_domain_entrypoint(
        build_trigonometry_angle_matrix,
        entrypoint_name=ENTRYPOINT,
        domain_operation=domain_operation,
        seed=seed,
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints=constraints,
    )
    matrix = normalize_domain_payload_to_v3_matrix(matrix, norm_context)

    cid = str(kwargs.get("component_id") or component_id or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=presentation_mode,
        answer_type=answer_type,
        problem_type_id=problem_type_id,
        component_id=cid or None,
        textbook_example_id=textbook_example_id or None,
        answer_schema_key="",
        domain_operation=domain_operation,
        seed=seed,
    )

    if str(constraints.get("variant") or "") == "special_angle_table" or answer_type == "table_fill":
        payload = _apply_table_fill(payload, matrix)
    elif answer_type in {"solution_set", "short_answer"} and not isinstance(payload.get("answer"), dict):
        ac = dict(payload.get("answer_contract") or {})
        if str(ac.get("checker") or payload.get("checker") or "") == "solution_set_checker" or answer_type == "solution_set":
            ac.update(
                {
                    "answer_type": "short_answer",
                    "checker": "solution_set_checker",
                    "checker_key": "solution_set_checker",
                    "answer_equivalence": "unordered_solution_set",
                    "equivalence_type": "unordered_solution_set",
                }
            )
            payload["answer_type"] = "short_answer"
            payload["answer_contract"] = ac
            payload["checker"] = "solution_set_checker"
            payload["checker_key"] = "solution_set_checker"
        else:
            _patch_pi_required_form(payload)
    elif str(payload.get("answer_type") or "") == "single_choice" or presentation_mode == "single_choice":
        payload["presentation_mode"] = "single_choice"
        payload["answer_type"] = "single_choice"
    else:
        if isinstance(payload.get("answer"), dict):
            ans = payload["answer"]
            parts = []
            for key, value in ans.items():
                text = str(value).strip()
                numeric = bool(text) and text.lstrip("+-").replace(".", "", 1).isdigit()
                needs_pi = _needs_pi_form(value)
                if needs_pi:
                    checker = "expression_checker"
                    equiv = "algebraic_equivalent"
                elif numeric:
                    checker = "integer_checker"
                    equiv = "numeric_exact"
                else:
                    checker = "expression_checker"
                    equiv = "algebraic_equivalent"
                row = {
                    "key": str(key),
                    "label": str(key),
                    "checker": checker,
                    "checker_key": checker,
                    "equivalence_type": equiv,
                    "expected_answer": value,
                }
                if needs_pi:
                    row["required_form"] = "pi_expression"
                parts.append(row)
            ac = dict(payload.get("answer_contract") or {})
            ac.update(
                {
                    "answer_type": "multi_part",
                    "checker": "multi_part_answer_checker",
                    "checker_key": "multi_part_answer_checker",
                    "equivalence_type": "multi_part_answer",
                    "parts": parts,
                }
            )
            payload["answer_type"] = "multi_part"
            payload["answer_contract"] = ac
            payload["checker"] = "multi_part_answer_checker"
            payload["checker_key"] = "multi_part_answer_checker"
        else:
            _patch_pi_required_form(payload)

    if cid:
        payload["component_id"] = cid
    payload["seed"] = seed
    payload["skill_id"] = skill_id
    payload["fixed_domain_key"] = FIXED_DOMAIN_KEY
    payload["domain_operation"] = domain_operation
    payload.setdefault("metadata", {})
    if isinstance(payload.get("metadata"), dict):
        payload["metadata"]["fixed_domain_key"] = FIXED_DOMAIN_KEY
        payload["metadata"]["domain_operation"] = domain_operation
        payload["metadata"]["domain_module"] = DOMAIN_MODULE
        payload["metadata"]["entrypoint"] = ENTRYPOINT
    return payload
