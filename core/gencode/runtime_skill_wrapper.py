from __future__ import annotations

import random
from typing import Any

from core.gencode.problem_type_spec import list_problem_types_for_skill, load_problem_type_spec
from core.gencode.slot_generators import generate_from_problem_type_spec
from core.gencode.validators import validate_generator_payload

try:
    from core.vocational_math_b1.generated_candidate_loader import generate_from_verified_candidate
except Exception:  # pragma: no cover
    generate_from_verified_candidate = None  # type: ignore


def _pick_problem_type_id(generator_specs: list[dict[str, Any]], seed: int | None) -> str:
    if not generator_specs:
        return ""
    rng = random.Random(seed)
    spec_row = rng.choice(generator_specs)
    return str(spec_row.get("problem_type_id", "")).strip()


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

    pt = _pick_problem_type_id(generator_specs, seed)
    if not pt:
        raise RuntimeError("generator_spec_not_found:empty_problem_type_id")

    problem_type_spec = load_problem_type_spec(skill_id, pt, prefer="auto")
    if not problem_type_spec:
        raise RuntimeError(f"generator_spec_not_found:{pt}")

    payload = generate_from_problem_type_spec(skill_id, problem_type_spec, seed=seed)
    if str(payload.get("block_reason", "")).strip():
        raise RuntimeError(str(payload.get("block_reason")))

    payload["problem_type_id"] = pt
    payload.setdefault("question", payload.get("question_text", ""))
    payload.setdefault("correct_answer", payload.get("answer"))
    payload.setdefault("choices", payload.get("choices", []))
    payload.setdefault("explanation", payload.get("explanation", ""))
    payload.setdefault("metadata", payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {})

    errors = validate_generator_payload(payload, problem_type_spec=problem_type_spec)
    if errors:
        raise RuntimeError(f"contract_validation_failed:{','.join(errors)}")

    return payload


def check_answer(user_answer: Any, correct_answer: Any) -> bool:
    ua = str(user_answer or "").strip().upper()
    ca = str(correct_answer or "").strip().upper()
    if not ua or not ca:
        return False
    if ua[:1] in {"A", "B", "C", "D"} and ca[:1] in {"A", "B", "C", "D"}:
        return ua[:1] == ca[:1]
    return ua == ca
