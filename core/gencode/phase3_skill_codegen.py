from __future__ import annotations

from typing import Any

from core.gencode.problem_type_spec import list_problem_types_for_skill
from core.gencode.spec_phase1_merge import spec_to_answer_contract_proposal, slot_generator_readiness


from core.gencode.pipeline_state import GENCODE_REPORT_DIR, read_json, sanitize_path_segment


def _phase1_induced_specs(skill_id: str, phase2_usable: list[dict[str, Any]]) -> list[dict[str, Any]]:
    induced_file = list_problem_types_for_skill(skill_id, prefer="induced")
    if induced_file:
        return induced_file
    path = GENCODE_REPORT_DIR / f"{sanitize_path_segment(skill_id)}_phase1_summary.json"
    if path.exists():
        data = read_json(path)
        auto = data.get("auto_review_summary") if isinstance(data.get("auto_review_summary"), dict) else {}
        induced = auto.get("induced_problem_type_specs") or data.get("induced_problem_type_specs")
        if isinstance(induced, list) and induced:
            return [s for s in induced if isinstance(s, dict)]
    drafts = [c.get("problem_type_spec_draft") for c in phase2_usable if isinstance(c, dict)]
    return [d for d in drafts if isinstance(d, dict) and d.get("problem_type_id")]


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
        HINT_INTEGER,
        HINT_RATIONAL,
        answer_contract_from_hint,
    )

    specs = _phase1_induced_specs(skill_id, phase2_usable)
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
        if original_pt.startswith("integer_"):
            canonical_ac = answer_contract_from_hint(HINT_INTEGER, existing_ac=canonical_ac)
            enriched["answer_contract"] = canonical_ac
            enriched["answer_format_hint"] = HINT_INTEGER
        elif original_pt.startswith("rational_"):
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
        # Carry through presentation_mode and answer_shape for smoke validator
        if canonical_ac.get("presentation_mode"):
            row["presentation_mode"] = canonical_ac["presentation_mode"]
        if canonical_ac.get("answer_shape"):
            row["answer_shape"] = canonical_ac["answer_shape"]
        specs_out.append(row)
        keys.append(str(g2.get("generator_key", "")).strip() or f"{skill_id}:{pt}:spec_v1")
    return specs_out, keys


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
