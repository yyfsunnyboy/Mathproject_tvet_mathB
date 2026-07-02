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
    grade_numeric_contract_answer,
    is_coordinate_pair_contract,
    is_coordinate_pair_runtime_payload,
    resolve_answer_contract_for_runtime,
)
from core.gencode.problem_type_spec import get_answer_contract, list_problem_types_for_skill, load_problem_type_spec
from core.gencode.slot_generators import generate_from_problem_type_spec
from core.gencode.validators import validate_generator_payload
from core.gencode.generated_question_format_validator import validate_generated_question_format
from core.checkers.quadrant_checker import check_quadrant_answer
from core.exceptions import RetryableSamplingError
from core.gencode.constraint_evaluator import evaluate_hard_constraints

try:
    from core.vocational_math_b1.generated_candidate_loader import generate_from_verified_candidate
except Exception:  # pragma: no cover
    generate_from_verified_candidate = None  # type: ignore

logger = logging.getLogger(__name__)

_BLOCKED_READINESS = frozenset({"blocked", "disabled", "pending", "not_ready"})
_PT_SUFFIX = re.compile(r"_\d+$")


def _normalize_problem_type_id(problem_type_id: str) -> str:
    return _PT_SUFFIX.sub("", str(problem_type_id or "").strip())


def _known_component_ids(
    generator_specs: list[dict[str, Any]],
    generator_keys: list[str] | None = None,
) -> set[str]:
    ids: set[str] = set()
    if generator_keys:
        ids.update(str(k).strip() for k in generator_keys if str(k).strip())
    for row in generator_specs:
        if isinstance(row, dict):
            cid = str(row.get("component_id", "")).strip()
            if cid:
                ids.add(cid)
    return ids


def resolve_component_dispatch(
    generator_specs: list[dict[str, Any]],
    generator_keys: list[str] | None = None,
    *,
    component_id: str | None = None,
    problem_type_id: str | None = None,
    seed: int | None = None,
) -> str | None:
    """Resolve a concrete component_id from explicit id or problem_type_id."""
    known = _known_component_ids(generator_specs, generator_keys)
    cid = str(component_id or "").strip()
    if cid:
        if known and cid not in known:
            raise RuntimeError(f"unknown_component_id:{cid}")
        return cid

    pt = str(problem_type_id or "").strip()
    if not pt:
        return None

    norm_pt = _normalize_problem_type_id(pt)
    matches: list[dict[str, Any]] = []
    for row in generator_specs:
        if not isinstance(row, dict):
            continue
        row_pt = str(row.get("problem_type_id", "")).strip()
        if not row_pt:
            continue
        if row_pt == pt or _normalize_problem_type_id(row_pt) == norm_pt:
            matches.append(row)

    if not matches:
        raise RuntimeError(f"generator_spec_not_found:{pt}")
    if len(matches) == 1:
        return str(matches[0].get("component_id", "")).strip() or None
    idx = int(seed or 0) % len(matches)
    return str(matches[idx].get("component_id", "")).strip() or None


def _problem_type_for_component(
    generator_specs: list[dict[str, Any]],
    component_id: str,
) -> str:
    for row in generator_specs:
        if isinstance(row, dict) and str(row.get("component_id", "")).strip() == component_id:
            return str(row.get("problem_type_id", "")).strip()
    return ""


def _match_available_problem_type(
    available: list[dict[str, Any]],
    problem_type_id: str,
) -> str:
    target = str(problem_type_id or "").strip()
    if not target:
        return ""
    norm = _normalize_problem_type_id(target)
    for row in available:
        row_pt = str(row.get("problem_type_id", "")).strip()
        if row_pt == target or _normalize_problem_type_id(row_pt) == norm:
            return row_pt
    return ""


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
        if key not in merged:
            # Respect and preserve the exact original problem_type_id (pt) compile-time tag.
            # Do NOT overwrite it with a shorter problem_type_id loaded from problem type spec.
            merged[key] = {
                "problem_type_id": pt,
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
    component_id: str | None = None,
    problem_type_id: str | None = None,
) -> tuple[str, str, list[str]]:
    available = collect_available_runtime_problem_types(
        skill_id,
        generator_specs,
        level=level,
    )
    available_ids = [str(row.get("problem_type_id", "")).strip() for row in available if str(row.get("problem_type_id", "")).strip()]

    resolved_component_id = resolve_component_dispatch(
        generator_specs,
        component_id=component_id,
        problem_type_id=problem_type_id,
        seed=seed,
    )
    if resolved_component_id:
        pt_from_component = _problem_type_for_component(generator_specs, resolved_component_id)
        if pt_from_component:
            matched = _match_available_problem_type(available, pt_from_component)
            if matched:
                return matched, "component_id_override", available_ids
            return pt_from_component, "component_id_override", available_ids

    pt_req = str(problem_type_id or "").strip()
    if pt_req:
        matched = _match_available_problem_type(available, pt_req)
        if matched:
            return matched, "problem_type_id_override", available_ids
        raise RuntimeError(f"generator_spec_not_found:{pt_req}")

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


DEFAULT_GENERATION_MAX_ATTEMPTS = 10


def generate_for_skill(
    skill_id: str,
    generator_specs: list[dict[str, Any]],
    *,
    level: int = 1,
    seed: int | None = None,
    difficulty: str | int | None = None,
    component_id: str | None = None,
    problem_type_id: str | None = None,
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
        component_id=component_id,
        problem_type_id=problem_type_id,
    )
    _log_dispatch(skill_id, available_ids, pt, strategy)
    if not pt:
        raise RuntimeError("generator_spec_not_found:empty_problem_type_id")

    problem_type_spec = load_problem_type_spec(skill_id, pt, prefer="auto")
    if not problem_type_spec:
        raise RuntimeError(f"generator_spec_not_found:{pt}")

    # Find matching spec row in generator_specs to check max_attempts
    matched_spec = {}
    for spec_row in generator_specs:
        if isinstance(spec_row, dict) and str(spec_row.get("problem_type_id", "")).strip() == pt:
            matched_spec = spec_row
            break

    raw_max_attempts = matched_spec.get("max_attempts") or problem_type_spec.get("max_attempts")
    if raw_max_attempts is not None:
        if isinstance(raw_max_attempts, bool) or not isinstance(raw_max_attempts, int) or raw_max_attempts <= 0:
            raise ValueError(f"Invalid max_attempts: {raw_max_attempts!r}. Must be an integer > 0.")
        max_attempts = raw_max_attempts
    else:
        max_attempts = DEFAULT_GENERATION_MAX_ATTEMPTS

    raw_hard_constraints = matched_spec.get("hard_constraints") or problem_type_spec.get("hard_constraints")
    if raw_hard_constraints is not None:
        if not isinstance(raw_hard_constraints, list):
            raise ValueError(f"Invalid hard_constraints: {raw_hard_constraints!r}. Must be a list.")
        hard_constraints = raw_hard_constraints
    else:
        hard_constraints = None

    last_retryable_error = ""
    last_attempted_seed = None

    for attempt in range(max_attempts):
        if seed is not None:
            attempt_seed = seed + attempt
        else:
            attempt_seed = None if attempt == 0 else random.randint(1, 1000000)

        last_attempted_seed = attempt_seed

        try:
            payload = generate_from_problem_type_spec(skill_id, problem_type_spec, seed=attempt_seed)
            if str(payload.get("block_reason", "")).strip():
                raise RuntimeError(str(payload.get("block_reason")))

            payload["problem_type_id"] = pt
            payload.setdefault("question", payload.get("question_text", ""))
            payload.setdefault("correct_answer", payload.get("answer"))
            payload.setdefault("choices", payload.get("choices", []))
            payload.setdefault("explanation", payload.get("explanation", ""))
            payload.setdefault("metadata", payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {})

            # ── Hard Constraints Evaluation ───
            if hard_constraints is not None:
                metadata = payload.get("metadata")
                if not isinstance(metadata, dict):
                    raise ValueError("Payload missing metadata dict for hard constraints evaluation.")
                givens = metadata.get("givens")
                if givens is None or not isinstance(givens, dict):
                    raise ValueError("Payload missing metadata.givens dict for hard constraints evaluation.")

                ok, failures = evaluate_hard_constraints(hard_constraints, givens)
                if not ok:
                    failure_indices = [f["index"] for f in failures]
                    component_id = str(problem_type_spec.get("component_id") or "")
                    raise RetryableSamplingError(
                        f"Hard constraints not satisfied. "
                        f"component_id={component_id}, problem_type={pt}, "
                        f"failure_indices={failure_indices}, attempt_seed={attempt_seed}"
                    )

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

            # ── Semantic validation (retryable choices_duplicate) ───
            errors = validate_generator_payload(payload, problem_type_spec=problem_type_spec)
            if errors:
                if errors == ["choices_duplicate"]:
                    last_retryable_error = "choices_duplicate"
                    continue
                else:
                    raise RuntimeError(f"generator_semantically_unsafe:{','.join(errors)}")

            return payload

        except RetryableSamplingError as exc:
            last_retryable_error = str(exc)
            continue

        except RuntimeError as exc:
            msg = str(exc)
            if "generator_semantically_unsafe:" in msg:
                err_part = msg.split("generator_semantically_unsafe:")[1]
                errs = [x.strip() for x in err_part.split(",") if x.strip()]
                if errs == ["choices_duplicate"]:
                    last_retryable_error = "choices_duplicate"
                    continue
            raise

    component_id = str(problem_type_spec.get("component_id") or "")
    raise RuntimeError(
        f"SAMPLING_EXHAUSTED: skill_id={skill_id}, component_id={component_id}, "
        f"original_seed={seed}, attempts={max_attempts}, "
        f"last_attempted_seed={last_attempted_seed}, last_error={last_retryable_error}"
    )


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
    checker = str(
        ac.get("checker")
        or ac.get("checker_key")
        or (payload or {}).get("checker")
        or (payload or {}).get("checker_key")
        or (payload or {}).get("checker_type")
        or ""
    ).strip()
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

    try:
        from core.checkers.free_response_drawing_checker import (
            check_drawing_answer,
            find_answer_image,
            is_drawing_answer_contract,
        )
    except Exception:  # pragma: no cover
        check_drawing_answer = None  # type: ignore
        find_answer_image = None  # type: ignore
        is_drawing_answer_contract = None  # type: ignore

    drawing_ctx = bool(
        checker == "free_response_drawing_checker"
        or family == "drawing"
        or equiv == "drawing_equivalence"
        or (
            callable(is_drawing_answer_contract)
            and is_drawing_answer_contract(ac, payload if isinstance(payload, dict) else {})
        )
    )
    if drawing_ctx:
        drawing_payload = dict(payload) if isinstance(payload, dict) else {}
        if isinstance(user_answer, dict):
            drawing_payload = {**drawing_payload, **user_answer}
        if callable(find_answer_image):
            image_data_url, image_field = find_answer_image(drawing_payload)
        else:
            image_data_url, image_field = None, ""
        metadata = drawing_payload.get("metadata") if isinstance(drawing_payload.get("metadata"), dict) else {}
        expected_spec = (
            drawing_payload.get("expected_drawing_spec")
            or ac.get("expected_drawing_spec")
            or metadata.get("expected_drawing_spec")
            or {}
        )
        if not callable(check_drawing_answer):
            return False
        result = check_drawing_answer(
            image_data_url=image_data_url,
            question_text=str(drawing_payload.get("question_text") or drawing_payload.get("question") or ""),
            answer_contract=ac,
            metadata=metadata,
            expected_drawing_spec=expected_spec if isinstance(expected_spec, dict) else {},
            context={
                "skill_id": str(drawing_payload.get("skill_id") or skill_id or ""),
                "component_id": str(drawing_payload.get("component_id") or metadata.get("component_id") or ""),
                "problem_type_id": str(drawing_payload.get("problem_type_id") or metadata.get("problem_type_id") or ""),
                "checker_key": checker or "free_response_drawing_checker",
                "image_field": image_field,
                "student_strokes_image_data_url": drawing_payload.get("student_strokes_image_data_url"),
                "background_image_data_url": drawing_payload.get("background_image_data_url"),
            },
        )
        return bool(result.get("is_correct"))

    if checker == "multi_part_answer_checker" or family == "multi_part" or equiv == "multi_part_answer":
        from core.checkers.multi_part_answer_checker import check_multi_part_answer

        result = check_multi_part_answer(
            user_answer,
            correct_answer,
            answer_contract=ac,
            payload=payload,
        )
        return bool(result.get("overall_correct"))

    if (
        checker == "choice_label_checker"
        or family == "choice"
        or str(ac.get("presentation_mode", "")).strip() == "single_choice"
        or str((payload or {}).get("presentation_mode", "")).strip() == "single_choice"
    ):
        from core.checkers.choice_label_checker import check_choice_label

        choices = []
        if isinstance(payload, dict):
            raw_choices = payload.get("choices") or payload.get("options") or []
            if isinstance(raw_choices, list):
                choices = raw_choices
        return bool(check_choice_label(user_answer, correct_answer, choices))

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

    if checker == "line_label_checker" or equiv == "normalized_line_label":
        from core.checkers.line_label_checker import check_line_label_answer

        return check_line_label_answer(user_answer, correct_answer)

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

    if checker in {"integer_checker", "numeric_checker", "rational_checker", "decimal_tolerance_checker"}:
        numeric_result = grade_numeric_contract_answer(
            user_answer,
            correct_answer,
            ac,
            checker=checker,
        )
        if numeric_result.get("system_error"):
            raise RuntimeError(str(numeric_result.get("result") or "grading system error"))
        if numeric_result.get("invalid_input"):
            return False
        return bool(numeric_result.get("correct"))

    if checker == "linear_equation_equivalent_checker" or equiv == "linear_equation_equivalent":
        from core.checkers.linear_equation_equivalent_checker import check_linear_equation_equivalent_answer

        return check_linear_equation_equivalent_answer(user_answer, correct_answer)

    quadrant_result = check_quadrant_answer(user_answer, correct_answer)
    if quadrant_result is not None:
        return quadrant_result

    if user_answer is None or correct_answer is None:
        return False
    if isinstance(user_answer, bool) or isinstance(correct_answer, bool):
        return False
    ua = str(user_answer).strip().upper()
    ca = str(correct_answer).strip().upper()
    if not ua or not ca:
        return False
    if ua[:1] in {"A", "B", "C", "D"} and ca[:1] in {"A", "B", "C", "D"}:
        return ua[:1] == ca[:1]
    return ua == ca


def _load_v3_skill_router(skill_id: str, v3_package_root: str) -> Any:
    import importlib.util
    from pathlib import Path

    init_path = Path(v3_package_root) / skill_id / "__init__.py"
    if not init_path.is_file():
        raise RuntimeError(f"v3_skill_router_missing:{skill_id}")
    module_name = f"_v3_skill_router_{abs(hash((skill_id, str(init_path.resolve()))))}"
    spec = importlib.util.spec_from_file_location(module_name, init_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"v3_skill_router_load_failed:{skill_id}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dispatch_generate(
    skill_id: str,
    generator_keys: list[str],
    generator_specs: list[dict[str, Any]],
    *,
    v3_package_root: str,
    level: int = 1,
    seed: int | None = None,
    difficulty: str | int | None = None,
    component_id: str | None = None,
    problem_type_id: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Thin-facade entry: delegate generate to sandbox V3 skill router."""
    _ = difficulty
    resolved_component_id = resolve_component_dispatch(
        generator_specs,
        generator_keys,
        component_id=component_id or kwargs.pop("component_id", None),
        problem_type_id=problem_type_id or kwargs.pop("problem_type_id", None),
        seed=seed,
    )
    router = _load_v3_skill_router(skill_id, v3_package_root)
    generate_fn = getattr(router, "generate", None)
    if not callable(generate_fn):
        raise RuntimeError(f"v3_skill_generate_missing:{skill_id}")
    router_kwargs = dict(kwargs)
    if resolved_component_id:
        router_kwargs["component_id"] = resolved_component_id
    effective_problem_type_id = str(problem_type_id or router_kwargs.pop("problem_type_id", "") or "").strip()
    if effective_problem_type_id:
        router_kwargs["problem_type_id"] = effective_problem_type_id
    payload = generate_fn(level=level, seed=seed, **router_kwargs)
    if isinstance(payload, dict):
        selected_component_id = str(payload.get("component_id") or "")
        selected_problem_type_id = str(payload.get("problem_type_id") or "")
        selected_index = -1
        for index, row in enumerate(generator_specs):
            if isinstance(row, dict) and str(row.get("component_id") or "") == selected_component_id:
                selected_index = index
                break
        module_path = (
            f"components/{selected_component_id}/generate.py"
            if selected_component_id
            else ""
        )
        logger.info(
            "[V3 RUNTIME DISPATCH] skill_id=%s generator_spec_count=%s "
            "selected_index=%s selected_component_id=%s "
            "selected_problem_type_id=%s module_path=%s fallback_used=%s",
            skill_id,
            len(generator_specs),
            selected_index,
            selected_component_id,
            selected_problem_type_id,
            module_path,
            bool(payload.get("fallback_used", False)),
        )
    return payload


def dispatch_check(
    user_answer: Any,
    correct_answer: Any,
    *,
    question_payload: dict[str, Any] | None = None,
    v3_package_root: str,
    skill_id: str,
) -> Any:
    """Thin-facade entry: delegate check to sandbox V3 skill router."""
    router = _load_v3_skill_router(skill_id, v3_package_root)
    check_fn = getattr(router, "check", None)
    if callable(check_fn):
        return check_fn(user_answer, correct_answer, question_payload)
    return check_answer(user_answer, correct_answer, payload=question_payload)


def dispatch_get_hint(
    step: int,
    question_payload: dict[str, Any] | None = None,
    *,
    v3_package_root: str,
    skill_id: str,
) -> str:
    """Thin-facade entry: delegate get_hint to sandbox V3 skill router."""
    router = _load_v3_skill_router(skill_id, v3_package_root)
    hint_fn = getattr(router, "get_hint", None)
    if not callable(hint_fn):
        return ""
    result = hint_fn(step, question_payload)
    return str(result or "")
