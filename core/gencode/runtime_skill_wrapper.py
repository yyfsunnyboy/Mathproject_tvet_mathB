from __future__ import annotations

import logging
import random
import re
from typing import Any

from core.gencode.answer_payload import (
    answer_type_family,
    apply_coordinate_pair_runtime_fields,
    coerce_correct_answer,
    finalize_generator_payload,
    is_coordinate_pair_contract,
    is_coordinate_pair_runtime_payload,
    resolve_answer_contract_for_runtime,
)
from core.gencode.problem_type_spec import get_answer_contract, list_problem_types_for_skill, load_problem_type_spec
from core.gencode.slot_generators import generate_from_problem_type_spec
from core.gencode.validators import validate_generator_payload
from core.gencode.generated_question_format_validator import validate_generated_question_format
from core.checkers.quadrant_checker import check_quadrant_answer

try:
    from core.vocational_math_b1.generated_candidate_loader import generate_from_verified_candidate
except Exception:  # pragma: no cover
    generate_from_verified_candidate = None  # type: ignore

logger = logging.getLogger(__name__)

_BLOCKED_READINESS = frozenset({"blocked", "disabled", "pending", "not_ready"})
_PT_SUFFIX = re.compile(r"_\d+$")


def _normalize_problem_type_id(problem_type_id: str) -> str:
    return _PT_SUFFIX.sub("", str(problem_type_id or "").strip())


def _dispatch_rng(seed: int | None, *scope: str) -> random.Random:
    if seed is None:
        return random.Random()
    return random.Random("|".join([str(seed), *scope]))


def _is_runtime_ready(row: dict[str, Any]) -> bool:
    readiness = str(row.get("generator_readiness", "runtime_ready")).strip().lower()
    return readiness not in _BLOCKED_READINESS


def _level_allowed(spec: dict[str, Any] | None, level: int) -> bool:
    if not spec:
        return True
    gc = spec.get("generator_contract")
    if not isinstance(gc, dict):
        return True
    min_level = gc.get("min_level")
    max_level = gc.get("max_level")
    if min_level is not None and level < int(min_level):
        return False
    if max_level is not None and level > int(max_level):
        return False
    return True


def collect_available_runtime_problem_types(
    skill_id: str,
    generator_specs: list[dict[str, Any]],
    *,
    level: int = 1,
) -> list[dict[str, Any]]:
    """Merge skill GENERATOR_SPECS with induced/curated registry entries."""
    merged: dict[str, dict[str, Any]] = {}

    def _add(row: dict[str, Any], source: str) -> None:
        pt = str(row.get("problem_type_id", "")).strip()
        if not pt or not _is_runtime_ready(row):
            return
        spec = load_problem_type_spec(skill_id, pt, prefer="auto")
        if spec is None or not _level_allowed(spec, level):
            return
        key = _normalize_problem_type_id(pt)
        canonical_pt = str(spec.get("problem_type_id", pt)).strip() or pt
        if key not in merged:
            merged[key] = {
                "problem_type_id": canonical_pt,
                "source": source,
                "generator_readiness": row.get("generator_readiness", "runtime_ready"),
            }

    for row in generator_specs:
        if isinstance(row, dict):
            _add(row, "generator_specs")

    for spec in list_problem_types_for_skill(skill_id, prefer="auto"):
        if isinstance(spec, dict):
            _add(
                {
                    "problem_type_id": spec.get("problem_type_id", ""),
                    "generator_readiness": "runtime_ready",
                },
                "problem_type_registry",
            )

    return list(merged.values())


def dispatch_problem_type(
    skill_id: str,
    generator_specs: list[dict[str, Any]],
    *,
    level: int = 1,
    seed: int | None = None,
) -> tuple[str, str, list[str]]:
    available = collect_available_runtime_problem_types(
        skill_id,
        generator_specs,
        level=level,
    )
    available_ids = [str(row.get("problem_type_id", "")).strip() for row in available if str(row.get("problem_type_id", "")).strip()]
    strategy = "uniform_random"
    if not available:
        return "", strategy, []
    picked = _dispatch_rng(seed, skill_id, "problem_type_dispatch").choice(available)
    return str(picked.get("problem_type_id", "")).strip(), strategy, available_ids


def _log_dispatch(
    skill_id: str,
    available_ids: list[str],
    selected_problem_type_id: str,
    selection_strategy: str,
) -> None:
    logger.info("[GENCODE DISPATCH] skill_id=%s", skill_id)
    logger.info("[GENCODE DISPATCH] available_problem_type_ids=%s", available_ids)
    logger.info("[GENCODE DISPATCH] selected_problem_type_id=%s", selected_problem_type_id)
    logger.info("[GENCODE DISPATCH] selection_strategy=%s", selection_strategy)


def generate_for_skill(
    skill_id: str,
    generator_specs: list[dict[str, Any]],
    *,
    level: int = 1,
    seed: int | None = None,
    difficulty: str | int | None = None,
) -> dict[str, Any]:
    if not generator_specs:
        raise RuntimeError("generator_specs_empty")

    spec_first = bool(list_problem_types_for_skill(skill_id, prefer="auto"))
    if not spec_first and generate_from_verified_candidate is not None:
        try:
            return generate_from_verified_candidate(
                skill_id,
                seed=seed,
                difficulty=str(difficulty or "easy"),
            )
        except RuntimeError:
            pass

    pt, strategy, available_ids = dispatch_problem_type(
        skill_id,
        generator_specs,
        level=level,
        seed=seed,
    )
    _log_dispatch(skill_id, available_ids, pt, strategy)
    if not pt:
        raise RuntimeError("generator_spec_not_found:empty_problem_type_id")

    problem_type_spec = load_problem_type_spec(skill_id, pt, prefer="auto")
    if not problem_type_spec:
        raise RuntimeError(f"generator_spec_not_found:{pt}")

    generation_seed = seed
    payload = generate_from_problem_type_spec(skill_id, problem_type_spec, seed=generation_seed)
    if str(payload.get("block_reason", "")).strip():
        raise RuntimeError(str(payload.get("block_reason")))

    payload["problem_type_id"] = pt
    payload.setdefault("question", payload.get("question_text", ""))
    payload.setdefault("correct_answer", payload.get("answer"))
    payload.setdefault("choices", payload.get("choices", []))
    payload.setdefault("explanation", payload.get("explanation", ""))
    payload.setdefault("metadata", payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {})

    answer_contract = get_answer_contract(problem_type_spec)
    if answer_contract:
        payload = finalize_generator_payload(payload, answer_contract)
        payload = apply_coordinate_pair_runtime_fields(payload, answer_contract)

    # ── Global format & localization validation (fail-fast, no repair) ───
    format_errors = validate_generated_question_format(
        payload,
        skill_id=skill_id,
        problem_type_spec=problem_type_spec,
    )
    if format_errors:
        raise RuntimeError(f"generator_format_unsafe:{','.join(format_errors)}")

    errors = validate_generator_payload(payload, problem_type_spec=problem_type_spec)
    if errors:
        raise RuntimeError(f"generator_semantically_unsafe:{','.join(errors)}")

    return payload


def _resolve_answer_contract(
    *,
    payload: dict[str, Any] | None = None,
    answer_contract: dict[str, Any] | None = None,
    skill_id: str = "",
) -> dict[str, Any]:
    if isinstance(answer_contract, dict) and answer_contract.get("answer_type"):
        return answer_contract
    if isinstance(payload, dict):
        embedded = payload.get("answer_contract")
        if isinstance(embedded, dict) and embedded.get("answer_type"):
            return embedded
        pt = str(payload.get("problem_type_id", "")).strip()
        sid = str(payload.get("skill_id", skill_id)).strip()
        if sid and pt:
            spec = load_problem_type_spec(sid, pt, prefer="auto")
            if spec:
                return get_answer_contract(spec)
    return {}


def check_answer(
    user_answer: Any,
    correct_answer: Any,
    *,
    payload: dict[str, Any] | None = None,
    answer_contract: dict[str, Any] | None = None,
    skill_id: str = "",
) -> bool:
    base = dict(payload) if isinstance(payload, dict) else {}
    ac = resolve_answer_contract_for_runtime(
        {**base, **({"answer_contract": answer_contract} if isinstance(answer_contract, dict) else {})},
        skill_id=skill_id or str(base.get("skill_id", "")).strip(),
    )
    if not ac:
        ac = _resolve_answer_contract(payload=payload, answer_contract=answer_contract, skill_id=skill_id)
    correct_answer = coerce_correct_answer(correct_answer, ac)
    checker = str(ac.get("checker") or (payload or {}).get("checker") or (payload or {}).get("checker_type") or "").strip()
    family = answer_type_family(str(ac.get("answer_type", "")))
    equiv = str(
        ac.get("answer_equivalence")
        or (payload or {}).get("equivalence")
        or (payload or {}).get("equivalence_type")
        or ""
    ).strip()
    coord_ctx = is_coordinate_pair_contract(ac) or (
        isinstance(payload, dict) and is_coordinate_pair_runtime_payload(payload)
    )

    if checker == "coordinate_pair_checker" or family == "coordinate_pair" or coord_ctx:
        from core.checkers.coordinate_pair_checker import check_coordinate_pair_answer

        return check_coordinate_pair_answer(user_answer, correct_answer)

    if not coord_ctx and (
        checker == "solution_set_checker"
        or family == "solution_set"
        or equiv == "unordered_solution_set"
    ):
        from core.checkers.solution_set_checker import check_solution_set_answer

        return check_solution_set_answer(user_answer, correct_answer)

    if checker == "interval_checker" or family == "interval":
        from core.checkers.interval_checker import check_interval_answer

        return check_interval_answer(user_answer, correct_answer)

    if checker in {"quadrant_checker", "classification_checker"} or family == "classification":
        quadrant_result = check_quadrant_answer(user_answer, correct_answer)
        if quadrant_result is not None:
            return quadrant_result
        return str(user_answer or "").strip() == str(correct_answer or "").strip()

    expression_equivs = {
        "expression_equivalence",
        "math_expression_equivalence",
        "radical_equivalence",
    }
    if (
        checker == "expression_equivalence_checker"
        or family == "numeric_or_radical"
        or equiv in expression_equivs
    ):
        from core.checkers.expression_equivalence_checker import check_expression_equivalence_answer

        return check_expression_equivalence_answer(user_answer, correct_answer)

    quadrant_result = check_quadrant_answer(user_answer, correct_answer)
    if quadrant_result is not None:
        return quadrant_result

    ua = str(user_answer or "").strip().upper()
    ca = str(correct_answer or "").strip().upper()
    if not ua or not ca:
        return False
    if ua[:1] in {"A", "B", "C", "D"} and ca[:1] in {"A", "B", "C", "D"}:
        return ua[:1] == ca[:1]
    return ua == ca
