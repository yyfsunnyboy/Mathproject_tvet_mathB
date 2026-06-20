"""
core/gencode/problem_type_canonicalizer.py
==========================================
Typed-Prefix ProblemType Canonicalization.

Strips value/presentation prefixes (integer_, rational_, choice_, text_short_, …)
from problem_type_id so Phase 2 can resolve existing runtime slots and infer
correct answer_contract from presentation mode — not from the prefix alone.

Rules:
  - No skill_id hardcodes.  Canonicalization is problem_type-level / taxonomy-level.
  - Choice presentation → choice_label_checker, never integer_checker.
  - fill_blank / short_answer presentation → text_short_checker when slot outputs text.
  - If canonicalized slot exists in SLOT_REGISTRY → at least runtime_ready_with_warning.
  - contract_slot_mismatch → usable_for_phase3 = false.
"""
from __future__ import annotations

import re
from typing import Any

from core.gencode.answer_payload import answer_type_family
from core.gencode.answer_contract_policy import (
    infer_answer_contract_from_problem_context,
    is_line_equation_semantic,
    is_quadratic_inequality_semantic,
    is_quadratic_rational_scalar_semantic,
)
from core.gencode.problem_type_spec import get_answer_contract, get_generator_contract

# Prefixes stripped from the LEFT of problem_type_id (longest match first).
TYPED_PREFIXES: tuple[str, ...] = (
    "single_choice",
    "text_short",
    "text",
    "integer",
    "rational",
    "numeric",
    "choice",
    "expression",
)

VALUE_TYPE_PREFIXES = frozenset({"integer", "rational", "numeric", "expression"})
PRESENTATION_PREFIXES = frozenset({"choice", "single_choice", "text_short", "text"})

CHOICE_MARKERS: tuple[str, ...] = (
    "_choice",
    "properties_choice",
    "vertex_axis_choice",
    "graph_properties_choice",
    "single_choice",
)

TEXT_SHORT_MARKERS: tuple[str, ...] = (
    "fill_blank",
    "short_answer",
)

READINESS_RUNTIME_READY = "runtime_ready"
READINESS_RUNTIME_READY_WITH_WARNING = "runtime_ready_with_warning"
READINESS_CONTRACT_SLOT_MISMATCH = "contract_slot_mismatch"
READINESS_PENDING_TEMPLATE = "pending_template"
READINESS_GENERATOR_NOT_READY = "generator_not_ready"
READINESS_SLOT_NOT_REGISTERED = "slot_generator_not_registered"

PHASE3_BLOCKED_READINESS = frozenset(
    {
        READINESS_GENERATOR_NOT_READY,
        READINESS_CONTRACT_SLOT_MISMATCH,
        READINESS_SLOT_NOT_REGISTERED,
        READINESS_PENDING_TEMPLATE,
        "answer_contract_not_supported",
        "pending_problem_type_induction",
        "blocked_by_unresolved_skill_scoped_problem_type",
        "problem_type_bridge_missing",
        "pending_line_equation_mcq_slot",
    }
)


def _strip_typed_prefix(problem_type_id: str) -> tuple[str, str]:
    """Return (value_type_prefix, base_problem_type_id) without side effects."""
    original = str(problem_type_id or "").strip()
    value_type_prefix = ""
    base = original
    lower = base.lower()
    for prefix in TYPED_PREFIXES:
        token = f"{prefix}_"
        if lower.startswith(token):
            value_type_prefix = prefix
            base = base[len(token):]
            break
    return value_type_prefix, base


def canonicalize_problem_type_id(problem_type_id: str) -> dict[str, Any]:
    """Parse a typed-prefix problem_type_id into canonical components.

    Examples:
      integer_quadratic_graph_translation_fill_blank
        → base: quadratic_graph_translation_fill_blank
      rational_quadratic_graph_properties_choice
        → base: quadratic_graph_properties_choice
    """
    original = str(problem_type_id or "").strip()
    value_type_prefix, base = _strip_typed_prefix(original)
    base_target_task = _infer_base_target_task(base)
    return {
        "original_problem_type_id": original,
        "value_type_prefix": value_type_prefix,
        "base_problem_type_id": base,
        "base_target_task": base_target_task,
    }


def typed_line_equation_problem_type_id(
    target_task: str,
    *,
    presentation_mode: str = "short_answer",
) -> str:
    """Canonical typed id for line-equation family (always equation_ prefix)."""
    task = str(target_task or "").strip()
    mode = str(presentation_mode or "").strip() or "short_answer"
    if mode not in {"single_choice", "short_answer"}:
        mode = "short_answer"
    return f"equation_{task}_{mode}"


def resolve_authoritative_problem_type_id(
    candidate: dict[str, Any] | None = None,
    *,
    spec: dict[str, Any] | None = None,
) -> str:
    """Resolve canonical problem_type_id; draft spec id wins over bootstrap top-level id."""
    cand = candidate if isinstance(candidate, dict) else {}
    draft = (
        spec
        if isinstance(spec, dict)
        else (cand.get("problem_type_spec_draft") if isinstance(cand.get("problem_type_spec_draft"), dict) else {})
    )
    top = str(cand.get("problem_type_id") or cand.get("proposed_problem_type_id") or "").strip()
    draft_id = str(draft.get("problem_type_id", "")).strip()
    target = str(
        draft.get("target_task") or cand.get("target_task") or cand.get("subskill_id") or ""
    ).strip()
    task_family = str(draft.get("task_family") or cand.get("task_family") or "").strip()
    if not task_family and target:
        from core.gencode.task_families import task_family_for_task

        task_family = task_family_for_task(target)

    if is_line_equation_semantic(
        problem_type_id=draft_id or top,
        target_task=target,
        task_family=task_family,
    ):
        ac = draft.get("answer_contract") if isinstance(draft.get("answer_contract"), dict) else {}
        presentation = str(
            cand.get("presentation_mode")
            or ac.get("presentation_mode")
            or ""
        ).strip()
        feature_sig = draft.get("feature_signature") if isinstance(draft.get("feature_signature"), list) else []
        if not presentation and "short_answer" in feature_sig:
            presentation = "short_answer"
        if not presentation and "single_choice" in feature_sig:
            presentation = "single_choice"
        if presentation != "single_choice":
            if draft_id.endswith("_short_answer") or top.endswith("_short_answer"):
                return draft_id if draft_id.endswith("_short_answer") else top
            return typed_line_equation_problem_type_id(target, presentation_mode="short_answer")
        if draft_id.endswith("_single_choice") or top.endswith("_single_choice"):
            return draft_id if draft_id.endswith("_single_choice") else top
        return typed_line_equation_problem_type_id(target, presentation_mode="single_choice")

    if draft_id:
        if top and top != draft_id:
            if draft_id.startswith("equation_") and top.startswith("expression_"):
                return draft_id
            if len(draft_id) > len(top) and target and target in draft_id:
                return draft_id
        if not top:
            return draft_id
    return top or draft_id


def sync_candidate_authoritative_identity(candidate: dict[str, Any]) -> dict[str, Any]:
    """Align top-level candidate id/contract with authoritative draft spec when present."""
    if not isinstance(candidate, dict):
        return candidate
    draft = candidate.get("problem_type_spec_draft")
    if not isinstance(draft, dict):
        return candidate
    pt = resolve_authoritative_problem_type_id(candidate, spec=draft)
    if not pt:
        return candidate
    candidate["problem_type_id"] = pt
    candidate["proposed_problem_type_id"] = pt
    draft["problem_type_id"] = pt
    from core.gencode.problem_type_spec import get_answer_contract

    enriched = enrich_spec_with_canonicalization({**draft, "problem_type_id": pt})
    draft.update(enriched)
    ac = get_answer_contract(enriched)
    if isinstance(ac, dict) and ac:
        candidate["answer_contract_proposal"] = dict(ac)
        candidate["checker_key_proposal"] = str(ac.get("checker_key") or ac.get("checker") or "").strip()
        candidate["equivalence_type_proposal"] = str(
            ac.get("equivalence_type") or ac.get("answer_equivalence") or ""
        ).strip()
        candidate["answer_shape"] = str(ac.get("answer_shape", "")).strip()
        candidate["answer_type"] = str(ac.get("answer_type", "")).strip()
        candidate["template_slot"] = str(
            enriched.get("_resolved_template_slot") or candidate.get("template_slot") or ""
        ).strip()
    candidate["problem_type_spec_draft"] = draft
    candidate["canonical_base_problem_type_id"] = str(
        enriched.get("canonical_base_problem_type_id") or draft.get("canonical_base_problem_type_id") or ""
    ).strip()
    return candidate


def _infer_base_target_task(base_problem_type_id: str) -> str:
    """Recover the registered target_task token from a base problem_type_id."""
    from core.gencode.template_slot_resolver import TASK_FAMILY_TO_SLOT

    base = str(base_problem_type_id or "").strip()
    if not base:
        return ""
    if base in TASK_FAMILY_TO_SLOT:
        return base
    lower = base.lower()
    matches = [task for task in TASK_FAMILY_TO_SLOT if task.lower() in lower]
    if matches:
        return max(matches, key=len)
    return base


def infer_presentation_mode(
    base_problem_type_id: str,
    base_target_task: str = "",
    *,
    source_has_choices: bool = False,
    slot: str = "",
) -> str:
    """Return 'single_choice', 'short_answer', or '' based on base id / task / slot.

    Priority order (highest to lowest):
      1. Slot-registry evidence  – most authoritative (slot generator always wins)
      2. source_has_choices flag
      3. Name-based CHOICE_MARKERS / TEXT_SHORT_MARKERS
    """
    # ── 1. Slot-registry evidence ────────────────────────────────────────────
    if slot:
        from core.gencode.template_slot_resolver import get_slot_primary_presentation_mode
        slot_mode = get_slot_primary_presentation_mode(slot)
        if slot_mode:
            return slot_mode
    # ── 2. Source choices flag ───────────────────────────────────────────────
    combined = f"{base_problem_type_id} {base_target_task}".lower()
    if source_has_choices or any(m in combined for m in CHOICE_MARKERS):
        return "single_choice"
    if any(m in combined for m in TEXT_SHORT_MARKERS):
        return "short_answer"
    return ""


def _slot_for_spec(spec: dict[str, Any]) -> str:
    """Resolve template slot: prefer explicit template_slots.stem, else resolver."""
    gc = get_generator_contract(spec)
    slots = gc.get("template_slots") if isinstance(gc.get("template_slots"), dict) else {}
    explicit = str(slots.get("stem", "")).strip()
    if explicit:
        from core.gencode.template_slot_resolver import _slot_compatible_with_contract, resolve_template_slot

        if _slot_compatible_with_contract(explicit, spec):
            return explicit
        resolved = str(resolve_template_slot(spec) or "").strip()
        if resolved:
            return resolved
    from core.gencode.template_slot_resolver import resolve_template_slot

    return str(resolve_template_slot(spec) or "").strip()


def infer_answer_contract_for_canonical(
    canonical: dict[str, Any],
    *,
    source_has_choices: bool = False,
    slot: str = "",
    existing_ac: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Infer answer_contract from base presentation mode and slot — NOT from value prefix."""
    base_pt = str(canonical.get("base_problem_type_id", "")).strip()
    base_task = str(canonical.get("base_target_task", "")).strip()
    value_prefix = str(canonical.get("value_type_prefix", "")).strip()
    rational_scalar = is_quadratic_rational_scalar_semantic(
        problem_type_id=base_pt,
        target_task=base_task,
    )
    # Pass slot so SLOT_PRESENTATION_MODE takes precedence over name-based markers.
    presentation = infer_presentation_mode(
        base_pt, base_task, source_has_choices=source_has_choices, slot=slot
    )

    base_ac: dict[str, Any] = {
        "choices_required": False,
        "choice_count": None,
        "correct_choice_count": None,
        "frontend_render_choices": False,
        "source_has_choices": source_has_choices,
    }

    # ── Choice presentation ──────────────────────────────────────────────────
    if presentation == "single_choice":
        return {
            **base_ac,
            "answer_type": "single_choice",
            "answer_shape": "single_choice",
            "answer_semantics": "choice_label",
            "answer_equivalence": "choice_label",
            "equivalence_type": "choice_label",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "presentation_mode": "single_choice",
            "selected_checker": "choice_label_checker",
            "choices_required": True,
            "choice_count": 4,
            "correct_choice_count": 1,
            "frontend_render_choices": True,
            "accepted_formats": ["A", "B", "C", "D"],
        }

    # ── Text-short / fill-blank presentation ─────────────────────────────────
    if presentation == "short_answer":
        from core.gencode.answer_contract_policy import (
            QUADRATIC_INEQUALITY_SOLUTION_TASKS,
            build_interval_answer_contract,
            is_quadratic_inequality_interval_semantic,
        )

        if is_quadratic_inequality_interval_semantic(
            problem_type_id=base_pt,
            target_task=base_task,
        ) or base_task in QUADRATIC_INEQUALITY_SOLUTION_TASKS:
            return build_interval_answer_contract(existing_ac=base_ac)
        if is_quadratic_inequality_semantic(problem_type_id=base_pt, target_task=base_task):
            return {
                **base_ac,
                **infer_answer_contract_from_problem_context(
                    answer_type="expression",
                    target_task=base_task,
                    task_family="quadratic_inequality_family",
                ),
            }
        from core.gencode.task_families import SOLVE_UNKNOWN_COORDINATE_TASKS
        if (existing_ac and existing_ac.get("answer_type") == "solution_set") or base_task in SOLVE_UNKNOWN_COORDINATE_TASKS:
            return {
                **base_ac,
                "answer_type": "solution_set",
                "answer_shape": "unordered_set",
                "answer_equivalence": "unordered_solution_set",
                "equivalence_type": "unordered_solution_set",
                "checker": "solution_set_checker",
                "checker_key": "solution_set_checker",
                "presentation_mode": "short_answer",
                "accepted_formats": ["-3, 7", "7, -3", "{-3, 7}", "k=-3 或 k=7", "-3 或 7"],
            }
        # Slots that output text answers always use text_short_checker.
        text_slots = {
            "quadratic_graph_translation_fill_blank",
            "quadratic_graph_translation_short_answer",
            "quadratic_vertex_form_translation_to_new_function",
        }
        if slot in text_slots or any(m in f"{base_pt} {base_task}" for m in TEXT_SHORT_MARKERS):
            return {
                **base_ac,
                "answer_type": "text_short",
                "answer_shape": "text_short",
                "answer_semantics": "text_short",
                "answer_equivalence": "exact_string",
                "equivalence_type": "exact_string",
                "checker": "text_short_checker",
                "checker_key": "text_short_checker",
                "presentation_mode": "short_answer",
                "selected_checker": "text_short_checker",
            }
        # Numeric slot: typed prefix wins over rational_scalar capability.
        if value_prefix == "integer":
            return {
                **base_ac,
                "answer_type": "integer",
                "answer_shape": "scalar",
                "answer_equivalence": "numeric_exact",
                "equivalence_type": "numeric_exact",
                "checker": "integer_checker",
                "checker_key": "integer_checker",
                "presentation_mode": "short_answer",
                "selected_checker": "integer_checker",
                "checker_selection_reason": "typed_prefix_integer",
            }
        if value_prefix == "numeric":
            return {
                **base_ac,
                "answer_type": "numeric",
                "answer_shape": "scalar",
                "answer_equivalence": "numeric_exact",
                "equivalence_type": "numeric_exact",
                "checker": "numeric_checker",
                "checker_key": "numeric_checker",
                "presentation_mode": "short_answer",
                "selected_checker": "numeric_checker",
                "checker_selection_reason": "typed_prefix_numeric",
            }
        if value_prefix == "rational" or rational_scalar:
            return {
                **base_ac,
                "answer_type": "rational",
                "answer_shape": "scalar",
                "answer_equivalence": "rational_equivalent",
                "equivalence_type": "rational_equivalent",
                "checker": "rational_checker",
                "checker_key": "rational_checker",
                "presentation_mode": "short_answer",
                "selected_checker": "rational_checker",
                "checker_selection_reason": "quadratic_vertex_rational_capable" if rational_scalar else "typed_prefix_rational",
            }
        return {
            **base_ac,
            "answer_type": "text_short",
            "answer_shape": "text_short",
            "answer_equivalence": "exact_string",
            "equivalence_type": "exact_string",
            "checker": "text_short_checker",
            "checker_key": "text_short_checker",
            "presentation_mode": "short_answer",
            "selected_checker": "text_short_checker",
        }

    # ── Fallback: preserve existing if reasonable, else value-prefix numeric ─
    if rational_scalar:
        return {
            **base_ac,
            "answer_type": "rational",
            "answer_shape": "scalar",
            "answer_equivalence": "rational_equivalent",
            "equivalence_type": "rational_equivalent",
            "checker": "rational_checker",
            "checker_key": "rational_checker",
            "presentation_mode": "short_answer",
            "selected_checker": "rational_checker",
            "checker_selection_reason": "quadratic_vertex_rational_capable",
        }

    if isinstance(existing_ac, dict) and existing_ac.get("answer_type"):
        return dict(existing_ac)

    if value_prefix == "rational":
        return {
            **base_ac,
            "answer_type": "rational",
            "checker": "rational_checker",
            "checker_key": "rational_checker",
            "equivalence_type": "rational_equivalent",
            "presentation_mode": "short_answer",
        }
    if value_prefix in {"integer", "numeric"}:
        return {
            **base_ac,
            "answer_type": value_prefix,
            "checker": "integer_checker" if value_prefix == "integer" else "numeric_checker",
            "checker_key": "integer_checker" if value_prefix == "integer" else "numeric_checker",
            "equivalence_type": "numeric_exact",
            "presentation_mode": "short_answer",
        }
    return dict(existing_ac or base_ac)


def check_contract_slot_mismatch(spec: dict[str, Any], slot: str) -> list[str]:
    """Return blocker tokens when answer_contract conflicts with slot presentation."""
    if not slot:
        return []
    from core.gencode.template_slot_resolver import SLOT_COMPATIBLE_FAMILIES

    ac = get_answer_contract(spec)
    at = str(ac.get("answer_type", "")).strip()
    checker = str(ac.get("checker") or ac.get("checker_key") or "").strip()
    eq = str(ac.get("equivalence_type") or ac.get("answer_equivalence") or "").strip()
    presentation = str(ac.get("presentation_mode", "")).strip()
    allowed = SLOT_COMPATIBLE_FAMILIES.get(slot)

    blockers: list[str] = []

    # Choice slot + numeric checker → mismatch
    is_choice_slot = "choice" in slot or "properties" in slot
    is_choice_presentation = (
        presentation == "single_choice"
        or at in {"single_choice", "choice", "multi_choice"}
        or any(m in str(spec.get("problem_type_id", "")) for m in CHOICE_MARKERS)
    )
    is_numeric_checker = checker in {"integer_checker", "rational_checker", "numeric_checker"}
    is_numeric_eq = eq in {"numeric_exact", "rational_equivalent"}

    if is_choice_slot and (is_numeric_checker or (at in {"integer", "numeric", "rational"} and not is_choice_presentation)):
        if is_numeric_checker or is_numeric_eq:
            blockers.append("contract_slot_mismatch:choice_slot_numeric_checker")

    if at in {"integer", "numeric", "rational"} and is_choice_presentation:
        blockers.append("contract_slot_mismatch:numeric_type_choice_presentation")

    if allowed is not None:
        family = answer_type_family(at)
        # Normalize single_choice family
        check_family = "single_choice" if at in {"single_choice", "choice"} else family
        family_ok = check_family in allowed or at in allowed
        if not family_ok and check_family == "fraction" and "rational" in allowed:
            family_ok = True
        if not family_ok:
            # text_short slots accept text_short family
            if not (check_family in {"text_short", "short_answer"} and "text_short" in allowed):
                blockers.append(f"contract_slot_mismatch:{check_family}_not_compatible_with_{slot}")

    return sorted(set(blockers))


def enrich_spec_with_canonicalization(spec: dict[str, Any]) -> dict[str, Any]:
    """Return an enriched spec copy with canonical fields, slot, and corrected answer_contract.

    Canonicalization priority order (highest first):
      1. explicit answer_format_hint in spec            ← NEW: highest authority
      2. source_has_choices / choices_count             ← infer hint from choices evidence
      3. answer_fields in spec                          ← field-based hint inference
      4. template_slot registry (SLOT_PRESENTATION_MODE)← slot-based fallback
      5. base_problem_type_id name markers (CHOICE_MARKERS, TEXT_SHORT_MARKERS)
      6. value-type prefix (integer_/rational_/…)      ← last resort

    The value-type prefix NEVER overrides an explicit answer_format_hint.
    """
    from core.gencode.answer_format_hint import (
        HINT_UNKNOWN,
        answer_contract_from_hint,
        enrich_spec_with_answer_format_hint,
        naming_warning_if_prefix_contract_mismatch,
    )

    out = dict(spec)
    pt_id = str(spec.get("problem_type_id", "")).strip()
    canonical = canonicalize_problem_type_id(pt_id)

    out["canonical_base_problem_type_id"] = canonical["base_problem_type_id"]
    out["value_type_prefix"] = canonical["value_type_prefix"]

    # Ensure target_task points to base when typed prefix obscures it.
    current_task = str(spec.get("target_task", "")).strip()
    base_task = canonical["base_target_task"]
    if base_task and (not current_task or current_task == pt_id):
        out["target_task"] = base_task
    elif base_task and canonical["value_type_prefix"] and current_task == canonical["original_problem_type_id"]:
        out["target_task"] = base_task

    # Resolve slot via template_slot_resolver (uses canonical pt internally).
    slot = _slot_for_spec(out)
    out["_resolved_template_slot"] = slot

    gc = dict(get_generator_contract(out))
    slots = dict(gc.get("template_slots") or {})
    if slot and not slots.get("stem"):
        slots["stem"] = slot
        gc["template_slots"] = slots
        out["generator_contract"] = gc

    # ── Priority 1: answer_format_hint (highest authority) ──────────────────
    # Enrich hint from existing evidence (source_has_choices, answer_fields, etc.)
    out = enrich_spec_with_answer_format_hint(out)
    hint = str(out.get("answer_format_hint") or "").strip()
    existing_ac = get_answer_contract(spec)
    base_task = str(out.get("target_task") or canonical["base_target_task"] or "").strip()
    skill_id = str(out.get("skill_id") or spec.get("skill_id") or "").strip()
    from core.gencode.answer_contract_policy import (
        _FACTORING_TASKS,
        QUADRATIC_INEQUALITY_INTERVAL_SOLUTION_TASKS,
        QUADRATIC_INEQUALITY_SOLUTION_TASKS,
        build_interval_answer_contract,
        build_quadratic_inequality_special_case_contract,
        build_quadratic_inequality_parameter_range_contract,
        build_reverse_quadratic_coefficients_integer_contract,
        is_quadratic_inequality_interval_semantic,
    )

    if base_task in _FACTORING_TASKS:
        from core.gencode.answer_format_hint import HINT_EXPRESSION

        out["answer_format_hint"] = HINT_EXPRESSION
        out["answer_contract"] = answer_contract_from_hint(HINT_EXPRESSION, existing_ac=existing_ac)
        return out

    from core.gencode.task_families import LINE_EQUATION_TASKS, LINE_EQUATION_TASK_TO_SLOT
    from core.gencode.answer_contract_policy import build_line_equation_answer_contract

    if base_task in LINE_EQUATION_TASKS:
        pt_lower = pt_id.lower()
        presentation_from_spec = str(existing_ac.get("presentation_mode", "")).strip()
        if pt_lower.endswith("_short_answer") or presentation_from_spec == "short_answer":
            is_choice_presentation = False
        elif pt_lower.endswith("_single_choice") and presentation_from_spec != "short_answer":
            is_choice_presentation = True
        else:
            is_choice_presentation = (
                bool(existing_ac.get("source_has_choices"))
                or str(existing_ac.get("presentation_mode", "")).strip() == "single_choice"
            )
        if not is_choice_presentation:
            out["answer_contract"] = build_line_equation_answer_contract(existing_ac=existing_ac)
            out["problem_type_id"] = typed_line_equation_problem_type_id(
                base_task, presentation_mode="short_answer"
            )
            resolved_slot = LINE_EQUATION_TASK_TO_SLOT.get(base_task, "line_equation_from_point_slope")
            if slot != resolved_slot:
                slot = resolved_slot
                out["_resolved_template_slot"] = slot
                slots = dict(gc.get("template_slots") or {})
                slots["stem"] = slot
                gc["template_slots"] = slots
                out["generator_contract"] = gc
            return out
        out["problem_type_id"] = typed_line_equation_problem_type_id(
            base_task, presentation_mode="single_choice"
        )

    if base_task == "solve_quadratic_inequality_special_cases":
        from core.gencode.answer_format_hint import HINT_TEXT_SHORT

        out["answer_format_hint"] = HINT_TEXT_SHORT
        out["answer_contract"] = build_quadratic_inequality_special_case_contract(existing_ac=existing_ac)
        return out

    if base_task == "solve_quadratic_inequality_parameter_range":
        from core.gencode.answer_format_hint import HINT_INTERVAL

        out["answer_format_hint"] = HINT_INTERVAL
        out["answer_contract"] = build_quadratic_inequality_parameter_range_contract(
            existing_ac=existing_ac
        )
        return out

    if base_task == "reverse_quadratic_inequality_coefficients":
        from core.gencode.answer_format_hint import HINT_INTEGER

        out["answer_format_hint"] = HINT_INTEGER
        out["answer_contract"] = build_reverse_quadratic_coefficients_integer_contract(
            existing_ac=existing_ac
        )
        return out

    if (
        base_task in QUADRATIC_INEQUALITY_INTERVAL_SOLUTION_TASKS
        or (
            base_task in QUADRATIC_INEQUALITY_SOLUTION_TASKS
            and is_quadratic_inequality_interval_semantic(
                problem_type_id=canonical["base_problem_type_id"],
                target_task=base_task,
            )
        )
    ):
        from core.gencode.answer_format_hint import HINT_INTERVAL

        out["answer_format_hint"] = HINT_INTERVAL
        out["answer_contract"] = build_interval_answer_contract(existing_ac=existing_ac)
        if canonical["value_type_prefix"] in {"integer", "numeric", "rational"}:
            out["naming_warning"] = "naming_warning:interval_task_value_prefix_ignored"
        return out

    source_has_choices = bool(existing_ac.get("source_has_choices"))
    presentation = infer_presentation_mode(
        canonical["base_problem_type_id"],
        base_task,
        source_has_choices=source_has_choices,
        slot=slot
    )

    rational_scalar = is_quadratic_rational_scalar_semantic(
        problem_type_id=canonical["base_problem_type_id"],
        target_task=str(out.get("target_task") or canonical["base_target_task"] or ""),
    )

    if rational_scalar and canonical["value_type_prefix"] in {"integer", "numeric"}:
        out["problem_type_id"] = canonical["base_problem_type_id"]
        out["naming_warning"] = "naming_warning:quadratic_vertex_value_prefix_removed"

    if presentation == "single_choice" and canonical["value_type_prefix"] in {"integer", "rational", "numeric"}:
        out["problem_type_id"] = canonical["base_problem_type_id"]
        out["naming_warning"] = "naming_warning:choice_task_value_prefix_removed"

    if rational_scalar:
        if hint in {"integer", "numeric", ""} or canonical["value_type_prefix"] in {"integer", "numeric"}:
            out["answer_format_hint"] = "rational"
            hint = "rational"
            out["naming_warning"] = "naming_warning:quadratic_vertex_integer_hint_promoted_to_rational"
    if not hint or hint == HINT_UNKNOWN:
        if presentation == "single_choice":
            from core.gencode.answer_format_hint import HINT_CHOICE
            out["answer_format_hint"] = HINT_CHOICE
            hint = HINT_CHOICE
        elif slot in {
            "quadratic_graph_translation_fill_blank",
            "quadratic_graph_translation_short_answer",
            "quadratic_vertex_form_translation_to_new_function",
        } or any(m in f"{canonical['base_problem_type_id']} {base_task}" for m in TEXT_SHORT_MARKERS):
            from core.gencode.answer_format_hint import HINT_TEXT_SHORT
            out["answer_format_hint"] = HINT_TEXT_SHORT
            hint = HINT_TEXT_SHORT

    if hint and hint != HINT_UNKNOWN:
        pass
    elif slot in {
        "quadratic_graph_translation_fill_blank",
        "quadratic_graph_translation_short_answer",
        "quadratic_vertex_form_translation_to_new_function",
    }:
        pass
    elif canonical["value_type_prefix"] == "integer":
        from core.gencode.answer_format_hint import HINT_INTEGER

        if not (
            base_task in QUADRATIC_INEQUALITY_SOLUTION_TASKS
            or is_quadratic_inequality_interval_semantic(
                problem_type_id=canonical["base_problem_type_id"],
                target_task=base_task,
            )
        ):
            out["answer_format_hint"] = HINT_INTEGER
            hint = HINT_INTEGER
    elif canonical["value_type_prefix"] == "rational":
        from core.gencode.answer_format_hint import HINT_RATIONAL

        out["answer_format_hint"] = HINT_RATIONAL
        hint = HINT_RATIONAL

    if hint and hint != HINT_UNKNOWN:
        # Hint is known → use it as the authoritative contract
        corrected_ac = answer_contract_from_hint(hint, existing_ac=existing_ac)
        # Propagate answer_fields / answer_separator from hint template
        from core.gencode.answer_format_hint import _HINT_TO_CONTRACT
        hint_template = _HINT_TO_CONTRACT.get(hint, {})
        if "answer_fields" in hint_template:
            corrected_ac["answer_fields"] = hint_template["answer_fields"]
        if "answer_separator" in hint_template:
            corrected_ac["answer_separator"] = hint_template["answer_separator"]
        out["answer_contract"] = corrected_ac
        # Emit naming warning if prefix contradicts hint
        nw = naming_warning_if_prefix_contract_mismatch(pt_id, hint)
        if nw:
            out["naming_warning"] = nw
        return out

    # ── Fallback to slot + name markers + prefix ─────────────────────────────
    # (only reached when answer_format_hint is absent/unknown)
    source_has_choices = bool(existing_ac.get("source_has_choices"))
    corrected_ac = infer_answer_contract_for_canonical(
        canonical,
        source_has_choices=source_has_choices,
        slot=slot,
        existing_ac=existing_ac,
    )
    out["answer_contract"] = corrected_ac
    return out


LINE_EQUATION_MCQ_HOLD_BLOCKER = "line_equation_single_choice_slot_not_ready"


def line_equation_mcq_hold_applies(record: dict[str, Any]) -> bool:
    """True when line-equation single_choice lacks a registered MCQ slot."""
    from core.gencode.task_families import LINE_EQUATION_FAMILY, LINE_EQUATION_TASKS

    if not isinstance(record, dict):
        return False
    task_family = str(record.get("task_family", "")).strip()
    target_task = str(record.get("target_task", "")).strip()
    if task_family != LINE_EQUATION_FAMILY:
        return False
    if target_task not in LINE_EQUATION_TASKS:
        return False

    ac = record.get("answer_contract") if isinstance(record.get("answer_contract"), dict) else {}
    if not ac and isinstance(record.get("answer_contract_proposal"), dict):
        ac = record["answer_contract_proposal"]
    if not ac:
        ac = get_answer_contract(record)

    presentation = str(
        record.get("presentation_mode") or ac.get("presentation_mode") or ""
    ).strip()
    answer_type = str(ac.get("answer_type", "")).strip().lower()
    answer_shape = str(ac.get("answer_shape", "")).strip().lower()
    pt_id = str(record.get("problem_type_id", "")).strip().lower()

    if presentation == "single_choice":
        return True
    if answer_type in {"single_choice", "choice", "choice_label", "multi_choice"}:
        return True
    if answer_shape == "single_choice":
        return True
    if pt_id.endswith("_single_choice"):
        return True
    return False


def apply_line_equation_mcq_hold_policy(record: dict[str, Any]) -> dict[str, Any]:
    """Demote line-equation MCQ candidates until a dedicated slot exists."""
    if not line_equation_mcq_hold_applies(record):
        return record
    out = dict(record)
    out["usable_for_phase3"] = False
    out["generator_readiness"] = "pending_line_equation_mcq_slot"
    out["requires_human_action"] = True
    out["promote_recommendation"] = "hold_pending_line_equation_mcq_slot"
    for key in ("risk_flags", "promote_blockers", "blockers"):
        existing = [str(x).strip() for x in (out.get(key) or []) if str(x).strip()]
        if LINE_EQUATION_MCQ_HOLD_BLOCKER not in existing:
            existing.append(LINE_EQUATION_MCQ_HOLD_BLOCKER)
        out[key] = sorted(set(existing))
    return out


def evaluate_typed_prefix_readiness(spec: dict[str, Any]) -> tuple[str, bool, list[str]]:
    """Evaluate generator_readiness after canonicalization.

    Returns (readiness, usable_for_phase3, blockers).
    """
    if line_equation_mcq_hold_applies(spec):
        return (
            "pending_line_equation_mcq_slot",
            False,
            [LINE_EQUATION_MCQ_HOLD_BLOCKER],
        )

    from core.gencode.checker_registry import validate_answer_contract_capability
    from core.gencode.slot_generators import SLOT_REGISTRY
    from core.gencode.task_families import answer_contract_supports_task

    enriched = enrich_spec_with_canonicalization(spec)
    slot = enriched.get("_resolved_template_slot") or _slot_for_spec(enriched)
    blockers: list[str] = []
    warnings: list[str] = []

    mismatch = check_contract_slot_mismatch(enriched, slot)
    if mismatch:
        return READINESS_CONTRACT_SLOT_MISMATCH, False, mismatch

    ac = get_answer_contract(enriched)
    cap = validate_answer_contract_capability(ac)
    if cap.get("checker_capability_status") == "blocked":
        return "answer_contract_not_supported", False, list(cap.get("checker_contract_blockers") or [])

    contract_ok, contract_blockers = answer_contract_supports_task(enriched)
    if not contract_ok:
        return "answer_contract_not_supported", False, contract_blockers

    if slot and slot in SLOT_REGISTRY:
        if warnings:
            return READINESS_RUNTIME_READY_WITH_WARNING, True, blockers
        return READINESS_RUNTIME_READY, True, blockers

    if slot:
        return READINESS_SLOT_NOT_REGISTERED, False, [READINESS_SLOT_NOT_REGISTERED]

    at = str(ac.get("answer_type", "")).strip()
    if at in {"single_choice", "short_answer", "text_short"}:
        return READINESS_RUNTIME_READY_WITH_WARNING, True, ["no_registered_slot_but_presentation_known"]

    return READINESS_GENERATOR_NOT_READY, False, [READINESS_GENERATOR_NOT_READY]


def is_phase3_packaging_allowed(readiness: str, usable_for_phase3: bool) -> bool:
    """True when candidate may enter Phase 3 packaging."""
    if usable_for_phase3 is False:
        return False
    r = str(readiness or "").strip()
    if r in PHASE3_BLOCKED_READINESS:
        return False
    return r in {
        READINESS_RUNTIME_READY,
        READINESS_RUNTIME_READY_WITH_WARNING,
        "limited_runtime_ready",
        "ready",
        "passed",
    }


# ── Generic second-order math meta preflight (Phase 1 source examples) ────────

MATH_META_TAG_SPECIAL_CASES_D_NEG = "[Task: Special_Cases_D_Less_Than_Zero]"
MATH_META_TAG_PARAMETER_RANGE = "[Task: Parameter_Range_D_Less_Than_Zero]"
# Backward-compatible alias for older reports / prompts.
MATH_META_TAG_SPECIAL_CASES_PARAM = MATH_META_TAG_PARAMETER_RANGE
MATH_META_TAG_REVERSE_VIETA = "[Task: Reverse_Coefficient_Vieta]"
MATH_META_TAG_APPLIED_CONTEXT = "[Task: Applied_Context]"

MATH_META_TAG_TO_TARGET_TASK: dict[str, str] = {
    MATH_META_TAG_SPECIAL_CASES_D_NEG: "solve_quadratic_inequality_special_cases",
    MATH_META_TAG_PARAMETER_RANGE: "solve_quadratic_inequality_parameter_range",
    MATH_META_TAG_REVERSE_VIETA: "reverse_quadratic_inequality_coefficients",
    MATH_META_TAG_APPLIED_CONTEXT: "applied_quadratic_inequality_problem",
}

MATH_META_TAG_RESOLUTION_ORDER: tuple[str, ...] = (
    MATH_META_TAG_REVERSE_VIETA,
    MATH_META_TAG_APPLIED_CONTEXT,
    MATH_META_TAG_PARAMETER_RANGE,
    MATH_META_TAG_SPECIAL_CASES_D_NEG,
)

MATH_META_TAG_TO_ANSWER_HINT: dict[str, str] = {
    MATH_META_TAG_SPECIAL_CASES_D_NEG: "text_short",
    MATH_META_TAG_PARAMETER_RANGE: "interval",
    MATH_META_TAG_REVERSE_VIETA: "integer",
    MATH_META_TAG_APPLIED_CONTEXT: "interval",
}

MATH_META_TAG_TO_CHECKER: dict[str, str] = {
    MATH_META_TAG_SPECIAL_CASES_D_NEG: "text_short_checker",
    MATH_META_TAG_PARAMETER_RANGE: "interval_checker",
    MATH_META_TAG_REVERSE_VIETA: "integer_checker",
    MATH_META_TAG_APPLIED_CONTEXT: "interval_checker",
}

_RE_QUADRATIC_STEM = re.compile(
    r"x\}\^\{2\}|x\^2|x\s*\^\s*2|二次|不等式|inequality|[<>≤≥＜＞]|"
    r"拋物線|抛物线|判別式|判别式|恆正|恒正|恆負|恒负",
    re.I,
)
_RE_SPECIAL_D_NEG = re.compile(
    r"對於任意實數|对于任意实数|任意實數|任意实数|"
    r"無解|无解|D\s*[<＜]\s*0|判別式\s*[<＜]|判别式\s*[<＜]",
    re.I,
)
_RE_PARAMETER_RANGE = re.compile(
    r"求\s*[km]\s*的?\s*範圍|求\s*[km]\s*的?\s*范围|"
    r"求\s*[km]\s*之?\s*範圍|求\s*[km]\s*之?\s*范围|"
    r"(恆正|恒正|恆負|恒负).{0,24}(範圍|范围|求\s*[km])|"
    r"(使|對|对).{0,16}(恆正|恒正|恆負|恒负|均成立|恒成立|恆成立)|"
    r"參數\s*[km]|参数\s*[km]",
    re.I,
)
_RE_REVERSE_VIETA = re.compile(
    r"求\s*a\s*\+\s*b|求\s*[ab]\s*(\+|、|和|之值)|"
    r"求\s*[ab]\s*之值|求\s*[ab]\s*的值|"
    r"已知.{0,24}(解|解集|解為|解为)|"
    r"解為.{0,16}求|解为.{0,16}求|"
    r"若.{0,32}不等式.{0,24}解.{0,12}求",
    re.I,
)
_RE_APPLIED_CONTEXT = re.compile(
    r"不大於|不大于|至少|至多|矩形|面積|面积|三角形|利润|利潤|成本|收入|咖啡|"
    r"邊長|边长|三邊|三边|構成三角形|构成三角形|售出|獲利|获利|"
    r"周長|周长|長度|长度|寬|宽|高",
    re.I,
)


def _normalize_stem_for_meta_tags(stem_text: str) -> str:
    text = str(stem_text or "").strip()
    if not text:
        return ""
    text = text.replace("\\", "")
    text = re.sub(r"\s+", " ", text)
    return text


def extract_math_meta_tags(stem_text: str) -> list[str]:
    """
    Deterministic second-order math feature preflight from stem text.

    Returns hard tags such as ``[Task: Reverse_Coefficient_Vieta]`` that are
    injected into Phase 1 AI context and may force subskill selection.
    Skill-agnostic regex/keyword rules — extend patterns for new units.
    """
    text = _normalize_stem_for_meta_tags(stem_text)
    if not text:
        return []
    if not _RE_QUADRATIC_STEM.search(text) and not _RE_APPLIED_CONTEXT.search(text):
        return []

    tags: list[str] = []
    if _RE_REVERSE_VIETA.search(text):
        tags.append(MATH_META_TAG_REVERSE_VIETA)
    if _RE_APPLIED_CONTEXT.search(text):
        tags.append(MATH_META_TAG_APPLIED_CONTEXT)
    if _RE_PARAMETER_RANGE.search(text):
        tags.append(MATH_META_TAG_PARAMETER_RANGE)
    elif _RE_SPECIAL_D_NEG.search(text):
        tags.append(MATH_META_TAG_SPECIAL_CASES_D_NEG)
    return tags


def resolve_target_task_from_math_meta_tags(tags: list[str] | None) -> str:
    """Pick the highest-priority forced target_task from extracted meta tags."""
    tag_set = {str(t).strip() for t in (tags or []) if str(t).strip()}
    for tag in MATH_META_TAG_RESOLUTION_ORDER:
        if tag in tag_set:
            return MATH_META_TAG_TO_TARGET_TASK.get(tag, "")
    return ""


def resolve_answer_format_hint_from_math_meta_tags(tags: list[str] | None) -> str:
    tag_set = {str(t).strip() for t in (tags or []) if str(t).strip()}
    for tag in MATH_META_TAG_RESOLUTION_ORDER:
        if tag in tag_set:
            return MATH_META_TAG_TO_ANSWER_HINT.get(tag, "")
    return ""


def resolve_checker_from_math_meta_tags(tags: list[str] | None) -> str:
    tag_set = {str(t).strip() for t in (tags or []) if str(t).strip()}
    for tag in MATH_META_TAG_RESOLUTION_ORDER:
        if tag in tag_set:
            return MATH_META_TAG_TO_CHECKER.get(tag, "")
    return ""


def format_math_meta_tags_for_prompt(tags: list[str] | None) -> str:
    """Human/AI-readable block appended to Phase 1 classifier context."""
    clean = [str(t).strip() for t in (tags or []) if str(t).strip()]
    if not clean:
        return ""
    forced = resolve_target_task_from_math_meta_tags(clean)
    lines = [
        "Python math meta preflight (MANDATORY — do not override):",
        f"- math_meta_tags: {clean}",
    ]
    if forced:
        lines.append(f"- forced_target_task: {forced}")
        lines.append(
            "- You MUST select the candidate whose target_task equals forced_target_task "
            "when it appears in the candidate list."
        )
    return "\n".join(lines) + "\n"
