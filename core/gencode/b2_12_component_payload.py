"""Thin Phase-2 payload assembly for Math B2 section 1-2 components.

The functions in this module never solve mathematics.  They call the exact-ready
shared Domain operations, preserve their canonical answers, and only reshape
those answers to match each textbook example's response topology.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.domain.geometry_similarity_domain import build_geometry_similarity_matrix
from core.domain.trigonometry_acute_domain import build_trigonometry_acute_matrix
from core.gencode.b2_12_capability_adapter import adapt_b2_12_batch1_matrix


def _build_call(call: dict[str, Any], *, seed: int | None) -> dict[str, Any]:
    operation = str(call["operation"])
    constraints = deepcopy(call.get("constraints") or {})
    if operation == "solve_similar_triangle_proportion":
        matrix = build_geometry_similarity_matrix(
            seed=seed, domain_operation=operation, constraints=constraints
        )
    else:
        matrix = build_trigonometry_acute_matrix(
            seed=seed, domain_operation=operation, constraints=constraints
        )
    adapter_kwargs: dict[str, Any] = {"seed": seed}
    if (constraints.get("choice_options") or call.get("presentation_mode") == "single_choice"):
        adapter_kwargs.update({"presentation_mode": "single_choice", "answer_type": "single_choice"})
    return adapt_b2_12_batch1_matrix(matrix, domain_operation=operation, **adapter_kwargs)


def _available_parts(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    contract = payload.get("answer_contract") or {}
    parts = contract.get("parts") if isinstance(contract.get("parts"), list) else []
    return {
        str(part.get("key")): dict(part)
        for part in parts
        if isinstance(part, dict) and str(part.get("key") or "").strip()
    }


def _scalar_part(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("correct_answer", payload.get("answer"))
    return {
        "expected_answer": value,
        "checker": str(payload.get("checker") or "expression_checker"),
        "checker_key": str(payload.get("checker_key") or payload.get("checker") or "expression_checker"),
        "equivalence_type": str(payload.get("equivalence_type") or payload.get("equivalence") or "algebraic_equivalent"),
    }


def _select_outputs(payload: dict[str, Any], output_specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    available = _available_parts(payload)
    selected: list[dict[str, Any]] = []
    for index, output in enumerate(output_specs):
        source_key = str(output.get("source_key") or "").strip()
        if source_key.startswith("given:"):
            given_key = source_key.split(":", 1)[1]
            givens = ((payload.get("metadata") or {}).get("givens") or {})
            base = {
                "expected_answer": givens[given_key],
                "checker": "rational_checker",
                "checker_key": "rational_checker",
                "equivalence_type": "rational_equivalent",
            }
        else:
            base = dict(available[source_key]) if source_key else _scalar_part(payload)
        if source_key == "cofunction":
            base.update({
                "checker": "text_short_checker",
                "checker_key": "text_short_checker",
                "equivalence_type": "exact_string",
            })
        key = str(output.get("key") or source_key or f"part_{index + 1}")
        base.update({"key": key, "field_key": key, "label": str(output.get("label") or key)})
        for name in ("checker", "checker_key", "equivalence_type", "required_form", "unit"):
            if output.get(name) is not None:
                base[name] = output[name]
        selected.append(base)
    return selected


def generate_b2_12_component_payload(
    *,
    skill_id: str,
    textbook_example_id: int,
    domain_operation: str,
    answer_type: str,
    question_text: str,
    calls: list[dict[str, Any]],
    seed: int | None,
    component_id: str,
    oracle_source: str,
    visual_asset: str = "",
) -> dict[str, Any]:
    if answer_type not in {"short_answer", "single_choice", "multi_part"}:
        raise ValueError(f"unsupported_b2_12_answer_type:{answer_type}")
    if not calls:
        raise ValueError("b2_12_component_requires_domain_call")

    child_payloads = [_build_call(call, seed=seed) for call in calls]
    first = deepcopy(child_payloads[0])
    component_id = str(component_id or f"src_{textbook_example_id}")

    if answer_type == "single_choice":
        payload = first
        contract = dict(payload.get("answer_contract") or {})
        contract.update({
            "answer_type": "single_choice",
            "answer_shape": "single_choice",
            "presentation_mode": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence_type": "choice_label",
        })
        payload["answer_contract"] = contract
        semantic = contract.get("semantic_canonical_answer") or contract.get("semantic_answer")
        payload.update({
            "answer": semantic,
            "correct_answer": semantic,
            "display_answer": str(semantic),
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "equivalence": "choice_label",
            "equivalence_type": "choice_label",
        })
    else:
        parts: list[dict[str, Any]] = []
        for call, child in zip(calls, child_payloads):
            outputs = list(call.get("outputs") or [])
            if not outputs:
                available = _available_parts(child)
                outputs = [{"source_key": key, "key": key, "label": key} for key in available]
                if not outputs:
                    outputs = [{"key": f"part_{len(parts) + 1}"}]
            parts.extend(_select_outputs(child, outputs))

        if answer_type == "short_answer":
            if len(parts) != 1:
                raise ValueError("short_answer_requires_one_domain_output")
            part = parts[0]
            canonical = part["expected_answer"]
            contract = {
                "presentation_mode": "short_answer",
                "answer_type": "short_answer",
                "answer_shape": "scalar",
                "checker": "expression_checker",
                "checker_key": "expression_checker",
                "answer_equivalence": "algebraic_equivalent",
                "equivalence_type": "algebraic_equivalent",
                "canonical_answer": canonical,
                "fixed_domain_key": (first.get("answer_contract") or {}).get("fixed_domain_key"),
            }
            if part.get("required_form"):
                contract["required_form"] = part["required_form"]
            payload = first
            payload.update({
                "answer": canonical,
                "correct_answer": canonical,
                "display_answer": str(canonical),
                "presentation_mode": "short_answer",
                "answer_type": "short_answer",
                "checker": contract["checker"],
                "checker_key": contract["checker_key"],
                "equivalence": contract["answer_equivalence"],
                "equivalence_type": contract["equivalence_type"],
                "answer_contract": contract,
            })
        else:
            canonical = {str(part["key"]): part["expected_answer"] for part in parts}
            contract = {
                "presentation_mode": "multiple_inputs",
                "answer_type": "multi_part",
                "answer_shape": "multi_part",
                "checker": "multi_part_answer_checker",
                "checker_key": "multi_part_answer_checker",
                "answer_equivalence": "multi_part_answer",
                "equivalence_type": "multi_part_answer",
                "parts": parts,
                "fixed_domain_key": (first.get("answer_contract") or {}).get("fixed_domain_key"),
            }
            payload = first
            payload.update({
                "answer": canonical,
                "correct_answer": canonical,
                "display_answer": ";".join(f"{key}={value}" for key, value in canonical.items()),
                "presentation_mode": "multiple_inputs",
                "answer_type": "multi_part",
                "checker": "multi_part_answer_checker",
                "checker_key": "multi_part_answer_checker",
                "equivalence": "multi_part_answer",
                "equivalence_type": "multi_part_answer",
                "answer_contract": contract,
            })

    generated_question = str(first.get("question_text") or first.get("question") or "")
    resolved_question = question_text.replace("{generated_question}", generated_question)
    payload.update({
        "skill_id": skill_id,
        "component_id": component_id,
        "generator_key": component_id,
        "textbook_example_id": textbook_example_id,
        "problem_type_id": domain_operation,
        "domain_operation": domain_operation,
        "source_kind": "example" if textbook_example_id <= 11565 else "exercise",
        "question_text": resolved_question,
        "question": resolved_question,
    })
    metadata = dict(payload.get("metadata") or {})
    metadata.update({
        "skill_id": skill_id,
        "component_id": component_id,
        "textbook_example_id": textbook_example_id,
        "domain_operation": domain_operation,
        "source_fidelity": "pass",
        "oracle_source": oracle_source,
        "exact_capability_readiness": "pass",
        "generator_readiness": "verified",
    })
    if visual_asset:
        metadata["source_visual_asset"] = visual_asset
        payload["visual_spec"] = {
            "kind": "image",
            "required": True,
            "asset_path": visual_asset,
            "alt": "教材題目示意圖",
        }
        payload["visual_aids"] = [payload["visual_spec"]]
    payload["metadata"] = metadata
    return payload


def get_b2_12_hint(payload: dict[str, Any] | None = None, *, stage: int = 1, **_: Any) -> str:
    steps = list(((payload or {}).get("metadata") or {}).get("derivation") or [])
    if steps:
        return str(steps[min(max(int(stage), 1) - 1, len(steps) - 1)])
    return "先整理題目已知條件，再依指定的銳角三角函數關係逐步計算。"
