from __future__ import annotations

from typing import Any

from core.gencode.problem_type_spec import list_problem_types_for_skill, load_problem_type_spec
from core.gencode.spec_phase1_merge import spec_to_answer_contract_proposal, slot_generator_readiness


from core.gencode.pipeline_state import GENCODE_REPORT_DIR, read_json, sanitize_path_segment


def _resolve_phase3_source_specs(
    skill_id: str,
    phase2_usable: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build one ProblemTypeSpec draft per Phase-2 usable row (authoritative packaging source)."""
    phase1_path = GENCODE_REPORT_DIR / f"{sanitize_path_segment(skill_id)}_phase1_summary.json"
    phase1_candidates: list[dict[str, Any]] = []
    if phase1_path.exists():
        data = read_json(phase1_path)
        raw = data.get("candidate_problem_types")
        if isinstance(raw, list):
            phase1_candidates = [c for c in raw if isinstance(c, dict)]

    induced_by_pt: dict[str, dict[str, Any]] = {}
    for spec in list_problem_types_for_skill(skill_id, prefer="induced") or []:
        if not isinstance(spec, dict):
            continue
        pt = str(spec.get("problem_type_id", "")).strip()
        if pt:
            induced_by_pt[pt] = spec

    candidate_by_pt: dict[str, dict[str, Any]] = {}
    for candidate in phase1_candidates:
        pt = str(
            candidate.get("problem_type_id") or candidate.get("proposed_problem_type_id") or ""
        ).strip()
        draft = candidate.get("problem_type_spec_draft")
        if pt and isinstance(draft, dict):
            candidate_by_pt[pt] = draft

    resolved: list[dict[str, Any]] = []
    for row in phase2_usable:
        if not isinstance(row, dict):
            continue
        pt = str(row.get("problem_type_id", "")).strip()
        if not pt:
            continue
        base_spec = (
            induced_by_pt.get(pt)
            or candidate_by_pt.get(pt)
            or load_problem_type_spec(skill_id, pt, prefer="curated")
            or {}
        )
        spec = dict(base_spec) if isinstance(base_spec, dict) else {}
        spec["skill_id"] = skill_id
        spec["problem_type_id"] = pt
        if row.get("target_task"):
            spec["target_task"] = row.get("target_task")
        if row.get("template_slot"):
            spec["_resolved_template_slot"] = row.get("template_slot")
        if isinstance(row.get("answer_contract"), dict):
            spec["answer_contract"] = row.get("answer_contract")
        resolved.append(spec)
    return resolved


def build_generator_specs_for_phase3(skill_id: str, phase2_usable: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    """Prefer Phase 1 induced ProblemTypeSpec drafts; curated JSON is fallback.

    Canonicalization note: typed-prefix problem_type_ids (integer_/rational_/…)
    must use the canonicalized answer_contract (text_short_checker for fill_blank,
    choice_label_checker for *_choice slots), NOT a re-derived checker from the
    value-type prefix.  We call enrich_spec_with_canonicalization() here to ensure
    the output GENERATOR_SPECS rows always carry the correct contract.
    """
    from core.gencode.problem_type_canonicalizer import (
        enrich_spec_with_canonicalization,
        evaluate_typed_prefix_readiness,
    )
    from core.gencode.answer_format_hint import (
        HINT_EXPRESSION,
        HINT_INTEGER,
        HINT_INTERVAL,
        HINT_RATIONAL,
        answer_contract_from_hint,
    )
    from core.gencode.answer_contract_policy import (
        _FACTORING_TASKS,
        QUADRATIC_INEQUALITY_SOLUTION_TASKS,
        build_interval_answer_contract,
        build_quadratic_inequality_parameter_range_contract,
        build_quadratic_inequality_special_case_contract,
        build_reverse_quadratic_coefficients_integer_contract,
        is_quadratic_inequality_interval_semantic,
    )
    from core.gencode.packaging_policy import phase3_generator_spec_exclusion_reasons

    specs = _resolve_phase3_source_specs(skill_id, phase2_usable)
    if not specs:
        specs = list_problem_types_for_skill(skill_id, prefer="curated")
    if not specs:
        specs_out = [
            {
                "problem_type_id": str(x.get("problem_type_id", "")).strip(),
                "checker_key": str(x.get("checker_key", "") or x.get("answer_contract_proposal", {}).get("checker_key", "")).strip(),
                "equivalence_type": str(x.get("equivalence_type", "") or x.get("answer_contract_proposal", {}).get("equivalence_type", "")).strip(),
            }
            for x in phase2_usable
            if str(x.get("problem_type_id", "")).strip()
        ]
        keys = [str(x.get("generator_key", "")).strip() for x in phase2_usable if str(x.get("generator_key", "")).strip()]
        return specs_out, keys

    phase2_by_pt = {str(x.get("problem_type_id", "")).strip(): x for x in phase2_usable if isinstance(x, dict)}
    specs_out: list[dict[str, Any]] = []
    keys: list[str] = []
    for spec in specs:
        original_pt = str(spec.get("problem_type_id", "")).strip()
        if not original_pt:
            continue
        # Canonicalize spec to get correct answer_contract (not re-derived from prefix)
        enriched = enrich_spec_with_canonicalization(spec)
        pt = str(enriched.get("problem_type_id") or original_pt).strip()
        if original_pt.startswith("integer_"):
            pt = original_pt
            enriched = dict(enriched)
            enriched["problem_type_id"] = original_pt
        elif original_pt.startswith("rational_"):
            pt = original_pt
            enriched = dict(enriched)
            enriched["problem_type_id"] = original_pt
        canonical_ac = enriched.get("answer_contract") if isinstance(enriched.get("answer_contract"), dict) else {}
        target_task = str(enriched.get("target_task") or "").strip()
        base_task = str(
            enriched.get("canonical_base_problem_type_id")
            or enriched.get("base_problem_type_id")
            or target_task
        ).strip()
        if base_task == "solve_quadratic_inequality_special_cases":
            canonical_ac = build_quadratic_inequality_special_case_contract(existing_ac=canonical_ac)
            enriched["answer_contract"] = canonical_ac
            from core.gencode.answer_format_hint import HINT_TEXT_SHORT

            enriched["answer_format_hint"] = HINT_TEXT_SHORT
        elif base_task == "solve_quadratic_inequality_parameter_range":
            canonical_ac = build_quadratic_inequality_parameter_range_contract(existing_ac=canonical_ac)
            enriched["answer_contract"] = canonical_ac
            enriched["answer_format_hint"] = HINT_INTERVAL
        elif base_task == "reverse_quadratic_inequality_coefficients":
            canonical_ac = build_reverse_quadratic_coefficients_integer_contract(existing_ac=canonical_ac)
            enriched["answer_contract"] = canonical_ac
            enriched["answer_format_hint"] = HINT_INTEGER
        elif is_quadratic_inequality_interval_semantic(
            problem_type_id=pt,
            target_task=target_task,
            task_family=str(enriched.get("task_family", "")).strip(),
        ) or str(canonical_ac.get("answer_type", "")).strip() == "interval":
            canonical_ac = build_interval_answer_contract(existing_ac=canonical_ac)
            enriched["answer_contract"] = canonical_ac
            enriched["answer_format_hint"] = HINT_INTERVAL
        elif original_pt.startswith("integer_"):
            if str(canonical_ac.get("answer_type", "")).strip() == "text_short" or str(canonical_ac.get("checker_key", "")).strip() in {"text_short_checker", "structured_text_checker"}:
                pass
            elif str(canonical_ac.get("answer_type", "")).strip() == "single_choice" or str(canonical_ac.get("checker_key", "")).strip() == "choice_label_checker":
                pass
            elif target_task in _FACTORING_TASKS or canonical_ac.get("answer_type") == "expression":
                canonical_ac = answer_contract_from_hint(HINT_EXPRESSION, existing_ac=canonical_ac)
                enriched["answer_contract"] = canonical_ac
                enriched["answer_format_hint"] = HINT_EXPRESSION
            else:
                canonical_ac = answer_contract_from_hint(HINT_INTEGER, existing_ac=canonical_ac)
                enriched["answer_contract"] = canonical_ac
                enriched["answer_format_hint"] = HINT_INTEGER
        elif original_pt.startswith("rational_"):
            if str(canonical_ac.get("answer_type", "")).strip() == "text_short" or str(canonical_ac.get("checker_key", "")).strip() in {"text_short_checker", "structured_text_checker"}:
                pass
            elif str(canonical_ac.get("answer_type", "")).strip() == "single_choice" or str(canonical_ac.get("checker_key", "")).strip() == "choice_label_checker":
                pass
            elif target_task in QUADRATIC_INEQUALITY_SOLUTION_TASKS and base_task not in {
                "solve_quadratic_inequality_special_cases",
                "reverse_quadratic_inequality_coefficients",
            }:
                canonical_ac = build_interval_answer_contract(existing_ac=canonical_ac)
                enriched["answer_contract"] = canonical_ac
                enriched["answer_format_hint"] = HINT_INTERVAL
            else:
                canonical_ac = answer_contract_from_hint(HINT_RATIONAL, existing_ac=canonical_ac)
                enriched["answer_contract"] = canonical_ac
                enriched["answer_format_hint"] = HINT_RATIONAL
        resolved_slot = enriched.get("_resolved_template_slot", "") or str(
            (spec.get("generator_contract") or {}).get("template_slots", {}).get("stem", "")
        ).strip()
        checker_key = str(canonical_ac.get("checker_key") or canonical_ac.get("checker") or "").strip()
        equivalence_type = str(canonical_ac.get("equivalence_type") or canonical_ac.get("answer_equivalence") or "").strip()
        answer_type = str(canonical_ac.get("answer_type", "")).strip()
        # Fallback to spec_to_answer_contract_proposal ONLY when canonicalization returned nothing
        if not checker_key or not equivalence_type:
            contract = spec_to_answer_contract_proposal(spec)
            checker_key = checker_key or str(contract.get("checker_key", "")).strip()
            equivalence_type = equivalence_type or str(contract.get("equivalence_type", "")).strip()
        readiness, _, _ = evaluate_typed_prefix_readiness(enriched)
        if readiness not in {"runtime_ready", "runtime_ready_with_warning"}:
            readiness_fallback = slot_generator_readiness(enriched)
            if readiness_fallback in {"runtime_ready", "runtime_ready_with_warning"}:
                readiness = readiness_fallback
        g2 = phase2_by_pt.get(pt, phase2_by_pt.get(original_pt, {}))
        row: dict[str, Any] = {
            "problem_type_id": pt,
            "checker_key": checker_key,
            "equivalence_type": equivalence_type,
            "generator_readiness": readiness,
        }
        if answer_type:
            row["answer_type"] = answer_type
        if resolved_slot:
            row["template_slot"] = resolved_slot
        canonical_base = str(enriched.get("canonical_base_problem_type_id", "")).strip()
        value_prefix = str(enriched.get("value_type_prefix", "")).strip()
        if canonical_base:
            row["base_problem_type_id"] = canonical_base
        if value_prefix:
            row["value_type_prefix"] = value_prefix
        if target_task:
            row["target_task"] = target_task
        # Carry through presentation_mode and answer_shape for smoke validator
        if canonical_ac.get("presentation_mode"):
            row["presentation_mode"] = canonical_ac["presentation_mode"]
        if canonical_ac.get("answer_shape"):
            row["answer_shape"] = canonical_ac["answer_shape"]
        curated_spec = load_problem_type_spec(skill_id, original_pt, prefer="curated") or {}
        max_att = (
            enriched.get("max_attempts")
            or spec.get("max_attempts")
            or curated_spec.get("max_attempts")
        )
        if max_att is not None:
            row["max_attempts"] = max_att
        h_const = (
            enriched.get("hard_constraints")
            or spec.get("hard_constraints")
            or curated_spec.get("hard_constraints")
        )
        if h_const is not None:
            row["hard_constraints"] = h_const
        specs_out.append(row)
        keys.append(str(g2.get("generator_key", "")).strip() or f"{skill_id}:{pt}:spec_v1")
    filtered_specs: list[dict[str, Any]] = []
    filtered_keys: list[str] = []
    for row, key in zip(specs_out, keys):
        if phase3_generator_spec_exclusion_reasons(row):
            continue
        filtered_specs.append(row)
        filtered_keys.append(key)
    return filtered_specs, filtered_keys


def build_phase3_skill_module_code(skill_id: str, generator_specs: list[dict[str, Any]], generator_keys: list[str]) -> str:
    """Emit a thin skill wrapper; generation logic lives in core.gencode.runtime_skill_wrapper.

    Runs Phase 3 contract integrity check before emitting — blockers are logged
    but do not prevent code generation (callers may choose to block publish).
    """
    import logging
    from core.gencode.packaging_policy import validate_phase3_generator_spec_integrity
    logger = logging.getLogger(__name__)
    integrity_blockers: dict[str, list[str]] = {}
    for row in generator_specs:
        if not isinstance(row, dict):
            continue
        pt = str(row.get("problem_type_id", "")).strip()
        issues = validate_phase3_generator_spec_integrity(row)
        if issues:
            integrity_blockers[pt] = issues
            logger.warning(
                "[PHASE3 INTEGRITY] problem_type=%s blockers=%s spec=%s",
                pt,
                issues,
                row,
            )
    return (
        "from __future__ import annotations\n\n"
        "from typing import Any\n\n"
        "from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill\n\n"
        f"SKILL_ID = {skill_id!r}\n"
        f"GENERATOR_KEYS = {generator_keys!r}\n"
        f"GENERATOR_SPECS = {generator_specs!r}\n\n"
        "def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:\n"
        "    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)\n\n"
        "def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):\n"
        "    return check_answer(user_answer, correct_answer, payload=question_payload)\n"
    )
