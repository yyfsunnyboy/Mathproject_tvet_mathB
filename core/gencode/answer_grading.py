from __future__ import annotations

import logging
from typing import Any

from core.gencode.answer_payload import (
    answer_type_family,
    coerce_correct_answer,
    format_coordinate_pair_display,
    grade_numeric_contract_answer,
    is_coordinate_pair_contract,
    is_coordinate_pair_runtime_payload,
    refresh_runtime_question_session,
    resolve_answer_contract_for_runtime,
)
from core.gencode.problem_type_spec import get_answer_contract, load_problem_type_spec
from core.gencode.runtime_skill_wrapper import check_answer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Grading result status schema
# ---------------------------------------------------------------------------
# Possible status values returned in grading result dicts:
#   "correct"         – answer is correct
#   "incorrect"       – answer is wrong but parseable
#   "parse_error"     – user input could not be parsed as a valid answer
#   "system_error"    – checker raised an exception or returned system_error
#
# Only "correct" and "incorrect" should count toward student answer records.
# "parse_error" and "system_error" MUST NOT be stored as student mistakes.
# ---------------------------------------------------------------------------

# Types that are never valid answer inputs regardless of checker
_UNPARSEABLE_TYPES = (dict, list, set, frozenset, tuple, bytearray, bytes, memoryview)


def _allows_structured_answer(answer_contract: dict[str, Any] | None) -> bool:
    contract = answer_contract if isinstance(answer_contract, dict) else {}
    answer_type = str(
        contract.get("answer_type") or contract.get("answer_shape") or ""
    ).strip().lower()
    checker = str(
        contract.get("checker") or contract.get("checker_key") or ""
    ).strip().lower()
    parts = contract.get("parts")
    return (
        answer_type in {"multi_part", "table_fill", "drawing", "multi_field", "multi_blank"}
        or checker in {"multi_part_answer_checker", "free_response_drawing_checker"}
        or "multi_part" in checker
        or (isinstance(parts, list) and len(parts) > 0)
    )


def validate_answer_input(user_answer: Any, answer_contract: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Return a parse_error result dict if user_answer cannot be a valid answer input.

    Returns None when the input looks valid (caller should proceed with grading).
    This does NOT validate mathematical correctness – only structural parseability.

    Unparseable cases:
    - None
    - dict / list / set / tuple (structured objects), unless answer_contract allows them
    - bytes / bytearray
    """
    parse_error = {
        "correct": False,
        "status": "parse_error",
        "error_code": "ANSWER_PARSE_FAILED",
        "invalid_input": True,
        "result": "invalid input",
        "message": "答案格式不正確",
    }
    if user_answer is None:
        return dict(parse_error)
    if isinstance(user_answer, _UNPARSEABLE_TYPES):
        if _allows_structured_answer(answer_contract) and isinstance(user_answer, (dict, list, tuple)):
            if isinstance(user_answer, dict) and not user_answer:
                return dict(parse_error)
            if isinstance(user_answer, (list, tuple)) and len(user_answer) == 0:
                return dict(parse_error)
            return None
        return dict(parse_error)
    # Empty string is technically parseable but semantically empty –
    # treat as parse_error (student has not entered anything).
    if isinstance(user_answer, str) and not user_answer.strip():
        return dict(parse_error)
    return None


def normalize_grading_result(result: dict[str, Any]) -> dict[str, Any]:
    """Ensure a grading result dict contains a canonical 'status' field.

    Idempotent: if 'status' is already set it is preserved.
    Maps legacy 'system_error'/'invalid_input' flags to canonical status.
    """
    if not isinstance(result, dict):
        return {"correct": False, "status": "system_error", "error_code": "CHECKER_EXECUTION_FAILED"}
    if "status" in result:
        return result
    out = dict(result)
    if out.get("system_error"):
        out["status"] = "system_error"
        out.setdefault("error_code", "CHECKER_EXECUTION_FAILED")
    elif out.get("invalid_input") or out.get("parse_error"):
        out["status"] = "parse_error"
        out.setdefault("error_code", "ANSWER_PARSE_FAILED")
        out.setdefault("message", "答案格式不正確")
    elif out.get("correct"):
        out["status"] = "correct"
    else:
        out["status"] = "incorrect"
    return out


_CONTRACT_CHECKERS = frozenset(
    {
        "solution_set_checker",
        "interval_checker",
        "inequality_solution_checker",
        "quadrant_checker",
        "classification_checker",
        "expression_equivalence_checker",
        "expression_checker",
        "equation_checker",
        "choice_label_checker",
        "coordinate_pair_checker",
        "linear_equation_equivalent_checker",
        "multi_part_answer_checker",
        "line_label_checker",
        "free_response_drawing_checker",
    }
)


def build_grading_payload(current: dict[str, Any], skill_id: str) -> dict[str, Any]:
    payload = dict(current)
    payload["skill_id"] = str(skill_id or current.get("skill", "")).strip()
    ac = payload.get("answer_contract")
    if not isinstance(ac, dict) or not ac.get("answer_type"):
        pt = str(payload.get("problem_type_id", "")).strip()
        if pt and payload["skill_id"]:
            spec = load_problem_type_spec(payload["skill_id"], pt, prefer="auto")
            if spec:
                ac = get_answer_contract(spec)
                payload["answer_contract"] = dict(ac)
    if isinstance(ac, dict):
        if ac.get("answer_type") and not payload.get("answer_type"):
            payload["answer_type"] = str(ac.get("answer_type"))
        if ac.get("checker") and not payload.get("checker"):
            payload["checker"] = str(ac.get("checker"))
            payload.setdefault("checker_type", str(ac.get("checker")))
        if ac.get("answer_equivalence") and not payload.get("equivalence"):
            payload["equivalence"] = str(ac.get("answer_equivalence"))
    return payload


def should_use_contract_aware_grading(current: dict[str, Any]) -> bool:
    skill_id = str(current.get("skill", current.get("skill_id", ""))).strip()
    refreshed = refresh_runtime_question_session(current, skill_id=skill_id)
    ac = resolve_answer_contract_for_runtime(refreshed, skill_id=skill_id)
    if isinstance(ac, dict) and ac.get("answer_type"):
        return True
    checker = str(refreshed.get("checker") or refreshed.get("checker_type") or "").strip()
    if checker in _CONTRACT_CHECKERS:
        return True
    equiv = str(refreshed.get("equivalence") or refreshed.get("equivalence_type") or "").strip()
    if equiv in {
        "unordered_solution_set",
        "interval_set",
        "interval_equivalence",
        "inequality_solution_equivalence",
        "math_expression_equivalence",
        "expression_equivalence",
        "radical_equivalence",
        "algebraic_equivalent",
        "equation_equivalent",
        "factorized_form",
        "coordinate_pair_equivalence",
        "linear_equation_equivalent",
        "multi_part_answer",
        "drawing_equivalence",
    }:
        return True
    if is_coordinate_pair_contract(ac) or is_coordinate_pair_runtime_payload(refreshed):
        return True
    family = answer_type_family(str(refreshed.get("answer_type", "")))
    if family == "multi_part":
        return True
    if family in {"solution_set", "interval", "classification", "numeric_or_radical", "coordinate_pair", "drawing"}:
        return True
    ca = coerce_correct_answer(refreshed.get("correct_answer", refreshed.get("answer")), ac)
    from core.gencode.inequality_solution_routing import is_inequality_solution_context

    if is_inequality_solution_context(refreshed, ac if isinstance(ac, dict) else {}, ca):
        return True
    if isinstance(ca, (list, tuple, set)) and not is_coordinate_pair_contract(ac):
        return True
    return False


def format_correct_answer_display(correct_answer: Any, current: dict[str, Any]) -> str:
    skill_id = str(current.get("skill", current.get("skill_id", ""))).strip()
    ctx = refresh_runtime_question_session(current, skill_id=skill_id)
    display = ctx.get("display_answer")
    if display:
        return str(display)
    ac = resolve_answer_contract_for_runtime(ctx, skill_id=skill_id)
    if is_coordinate_pair_contract(ac) or is_coordinate_pair_runtime_payload(ctx):
        text = format_coordinate_pair_display(correct_answer)
        if text:
            return text
    if answer_type_family(str(ac.get("answer_type", ""))) == "solution_set":
        if isinstance(correct_answer, (list, tuple, set)):
            return " 或 ".join(str(x) for x in correct_answer)
        return str(correct_answer)
    if isinstance(correct_answer, (list, tuple, set)):
        return " 或 ".join(str(x) for x in correct_answer)
    return str(correct_answer)


def build_correct_answer_display(current: dict[str, Any]) -> dict[str, Any] | None:
    """Build the student-safe, post-submit canonical-answer presentation contract.

    This intentionally exposes presentation values only. Checker configuration,
    oracle provenance, and other internal contract metadata are not returned.
    """
    skill_id = str(current.get("skill", current.get("skill_id", ""))).strip()
    ctx = refresh_runtime_question_session(current, skill_id=skill_id)
    ac = resolve_answer_contract_for_runtime(ctx, skill_id=skill_id)
    ac = ac if isinstance(ac, dict) else {}
    answer_type = str(ac.get("answer_type") or ctx.get("answer_type") or "short_answer").strip().lower()
    canonical = ac.get("canonical_answer")
    if canonical is None:
        canonical = ctx.get("correct_answer", ctx.get("answer"))

    if answer_type == "drawing":
        reference = ac.get("reference") or ac.get("reference_answer") or ac.get("expected_drawing_spec")
        rubric = ac.get("rubric") or ac.get("grading_rubric")
        if reference is None and rubric is None:
            return None
        return {"answer_type": "drawing", "reference": reference, "rubric": rubric}

    if answer_type in {"multi_part", "table_fill"} or isinstance(ac.get("parts"), list):
        values = canonical if isinstance(canonical, dict) else {}
        items: list[dict[str, str]] = []
        for index, part in enumerate(ac.get("parts") or []):
            if not isinstance(part, dict):
                continue
            key = str(part.get("key") or part.get("field_key") or index + 1)
            value = part.get("canonical_answer", part.get("expected_answer", values.get(key)))
            if value is None:
                continue
            items.append({"key": key, "label": str(part.get("label") or key), "value": str(value)})
        if not items and isinstance(canonical, dict):
            items = [{"key": str(k), "label": str(k), "value": str(v)} for k, v in canonical.items()]
        if not items:
            return None
        return {"answer_type": answer_type, "items": items}

    if answer_type in {"single_choice", "choice"}:
        choices = ctx.get("choices") or ctx.get("options") or []
        raw = str(canonical or "").strip()
        label = raw.upper() if len(raw) == 1 and raw.isalpha() else ""
        option_text = ""
        for index, choice in enumerate(choices if isinstance(choices, list) else []):
            choice_label = chr(65 + index)
            if isinstance(choice, dict):
                choice_label = str(choice.get("label") or choice_label).strip()
                choice_value = str(choice.get("value") or choice.get("text") or choice.get("content") or "").strip()
            else:
                choice_value = str(choice).strip()
            if raw in {choice_label, choice_value} or label == choice_label.upper():
                label, option_text = choice_label, choice_value
                break
        if not option_text and raw:
            option_text = raw
        if not label and option_text:
            for index, choice in enumerate(choices if isinstance(choices, list) else []):
                text = str(choice.get("text") or choice.get("content") or choice.get("value") or "") if isinstance(choice, dict) else str(choice)
                if text.strip() == option_text:
                    label = chr(65 + index)
                    break
        return {"answer_type": "single_choice", "label": label, "option_text": option_text}

    if canonical is None:
        return None
    return {"answer_type": answer_type or "short_answer", "value": format_correct_answer_display(canonical, ctx)}


def attach_correct_answer_feedback(result: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    """Attach canonical feedback only after an unsuccessful submit verdict."""
    out = dict(result)
    is_correct = out.get("all_correct", out.get("correct", out.get("is_correct")))
    out.setdefault("all_correct", is_correct is True)
    if is_correct is True or out.get("system_error") or out.get("state_lost"):
        return out
    display = build_correct_answer_display(current)
    if display is not None:
        out["correct_answer_display"] = display
    required_form_failed = bool(out.get("required_form_failed"))
    if required_form_failed:
        out["mathematically_equivalent"] = True
        out["required_form_valid"] = False
        out["required_form_feedback"] = "數值/數學內容可能正確，但答案格式不符合要求。"
        hint = ""
        ac = resolve_answer_contract_for_runtime(current, skill_id=str(current.get("skill_id") or current.get("skill") or ""))
        if isinstance(ac, dict):
            hint = str(ac.get("required_form_hint") or ac.get("format_hint") or ac.get("required_form") or "").strip()
        if hint:
            out["required_form_hint"] = hint
    return out


def log_check_answer_debug(
    *,
    skill_id: str,
    current: dict[str, Any],
    user_answer: Any,
    correct_answer: Any,
    check_result: bool,
    checker: str,
    log: Any | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    ac = current.get("answer_contract") if isinstance(current.get("answer_contract"), dict) else {}
    sink = log or logger
    msg = (
        "[CHECK ANSWER] skill_id=%s problem_type_id=%s checker=%s equivalence=%s "
        "answer_type=%s user_answer=%r correct_answer=%r correct_answer_type=%s check_result=%s"
    )
    args = [
        skill_id,
        current.get("problem_type_id", ""),
        checker or ac.get("checker", current.get("checker", "")),
        current.get("equivalence", ac.get("answer_equivalence", "")),
        current.get("answer_type", ac.get("answer_type", "")),
        user_answer,
        correct_answer,
        type(correct_answer).__name__,
        check_result,
    ]
    if extra:
        msg += " normalized_user_expression=%s normalized_correct_expression=%s parser_error=%s simplify_result=%s"
        args.extend(
            [
                extra.get("normalized_user_expression", ""),
                extra.get("normalized_correct_expression", ""),
                extra.get("parser_error", ""),
                extra.get("simplify_result", ""),
            ]
        )
    sink.info(msg, *args)


def grade_answer_for_current_question(
    user_answer: Any,
    current: dict[str, Any],
    skill_id: str,
    *,
    log: Any | None = None,
) -> dict[str, Any] | None:
    """Contract-aware grading for session current question. Returns None if not applicable.

    Result dict always contains a 'status' field:
        'correct'      – answer is correct
        'incorrect'    – wrong but parseable
        'parse_error'  – user input is structurally invalid (not a student mistake)
        'system_error' – checker raised an exception (not a student mistake)
    """
    if not should_use_contract_aware_grading(current):
        return None
    # --- Pre-flight: reject structurally invalid inputs before calling any checker ---
    contract_preview = (
        current.get("answer_contract")
        if isinstance(current.get("answer_contract"), dict)
        else None
    )
    parse_fail = validate_answer_input(user_answer, contract_preview)
    if parse_fail is not None:
        return parse_fail
    refreshed = refresh_runtime_question_session(current, skill_id=skill_id)
    payload = build_grading_payload(refreshed, skill_id)
    ac = resolve_answer_contract_for_runtime(payload, skill_id=skill_id)
    if ac:
        payload["answer_contract"] = ac
    correct_answer = ac.get("canonical_answer")
    if correct_answer is None:
        correct_answer = coerce_correct_answer(
            refreshed.get("correct_answer", refreshed.get("answer")),
            ac if isinstance(ac, dict) else None,
        )
    checker = str(
        ac.get("checker") or ac.get("checker_key") or payload.get("checker") or payload.get("checker_key") or payload.get("checker_type") or ""
    ).strip()
    family = answer_type_family(str(ac.get("answer_type", payload.get("answer_type", ""))))
    equiv = str(
        ac.get("answer_equivalence") or ac.get("equivalence") or payload.get("equivalence") or payload.get("equivalence_type") or ""
    ).strip()
    expr_debug: dict[str, Any] | None = None
    from core.gencode.inequality_solution_routing import (
        is_inequality_solution_context,
        try_grade_inequality_solution,
    )

    ineq_resolved = False
    interval_checker_locked = checker in {"interval_checker", "inequality_solution_checker"} or family == "interval"
    if is_inequality_solution_context(payload, ac if isinstance(ac, dict) else {}, correct_answer):
        ineq_verdict = try_grade_inequality_solution(user_answer, correct_answer)
        if ineq_verdict is not None:
            is_correct = ineq_verdict
            ineq_resolved = True
            checker = str(checker or "inequality_solution_checker")
    if ineq_resolved:
        pass
    elif checker == "free_response_drawing_checker" or answer_type_family(str(ac.get("answer_type", ""))) == "drawing":
        from core.checkers.free_response_drawing_checker import (
            check_drawing_answer,
            find_answer_image,
            find_student_strokes_image,
        )

        if isinstance(user_answer, dict):
            payload.update(user_answer)
        image_data_url, image_field = find_answer_image(payload)
        strokes_data_url, strokes_field = find_student_strokes_image(payload)
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        expected_spec = (
            payload.get("expected_drawing_spec")
            or ac.get("expected_drawing_spec")
            or metadata.get("expected_drawing_spec")
            or {}
        )
        drawing_result = check_drawing_answer(
            image_data_url=image_data_url,
            question_text=str(payload.get("question_text") or payload.get("question") or ""),
            answer_contract=ac if isinstance(ac, dict) else {},
            metadata=metadata,
            expected_drawing_spec=expected_spec if isinstance(expected_spec, dict) else {},
            context={
                "skill_id": skill_id,
                "component_id": str(payload.get("component_id") or metadata.get("component_id") or ""),
                "problem_type_id": str(payload.get("problem_type_id") or metadata.get("problem_type_id") or ""),
                "checker_key": checker or "free_response_drawing_checker",
                "image_field": image_field,
                "student_strokes_image_data_url": strokes_data_url,
                "student_strokes_image_field": strokes_field,
                "vision_image_mode": "dual" if image_data_url and strokes_data_url else ("composite_only" if image_data_url else "missing"),
            },
        )
        is_correct = drawing_result.get("is_correct")
        log_check_answer_debug(
            skill_id=skill_id,
            current=payload,
            user_answer="[drawing_image]" if image_data_url else "",
            correct_answer="[expected_drawing_spec]",
            check_result=bool(is_correct),
            checker=checker,
            log=log,
        )
        return {
            "correct": is_correct,
            "is_correct": is_correct,
            "result": str(drawing_result.get("feedback") or ""),
            "feedback": str(drawing_result.get("feedback") or ""),
            "status": drawing_result.get("status"),
            "system_error": bool(drawing_result.get("system_error", False)),
            "score": drawing_result.get("score"),
            "confidence": drawing_result.get("confidence"),
            "recognized_features": drawing_result.get("recognized_features", {}),
            "missing_features": drawing_result.get("missing_features", []),
            "incorrect_features": drawing_result.get("incorrect_features", []),
            "checker": "free_response_drawing_checker",
            "analyzer": drawing_result.get("analyzer", ""),
            "raw_analysis_available": bool(drawing_result.get("raw_analysis_available", False)),
        }
    elif (
        not interval_checker_locked
        and (
            checker in {"expression_equivalence_checker", "expression_checker"}
            or str(ac.get("answer_type", payload.get("answer_type", "")))
            in {"numeric_or_radical", "math_expression", "radical_number", "expression"}
        )
        and checker not in {"equation_checker", "linear_equation_equivalent_checker"}
    ):
        from core.checkers.expression_equivalence_checker import check_expression_equivalence_debug

        expr_debug = check_expression_equivalence_debug(
            user_answer,
            correct_answer,
            answer_contract=ac if isinstance(ac, dict) else None,
            payload=payload,
        )
        if expr_debug.get("error_code") == "ANSWER_PARSE_FAILED" or expr_debug.get("parser_error"):
            return normalize_grading_result({
                "correct": False,
                "invalid_input": True,
                "error_code": "ANSWER_PARSE_FAILED",
                "result": "答案格式不正確",
                "parser_error": expr_debug.get("parser_error"),
            })
        is_correct = bool(expr_debug.get("correct"))
    elif checker in {"equation_checker", "linear_equation_equivalent_checker"} or family == "linear_equation" or equiv in {"equation_equivalent", "linear_equation_equivalent"}:
        from core.checkers.expression_equivalence_checker import check_equation_equivalence_debug

        eq_debug = check_equation_equivalence_debug(user_answer, correct_answer)
        expr_debug = eq_debug
        if eq_debug.get("error_code") == "ANSWER_PARSE_FAILED" or eq_debug.get("parser_error"):
            return normalize_grading_result({
                "correct": False,
                "invalid_input": True,
                "error_code": "ANSWER_PARSE_FAILED",
                "result": "答案格式不正確",
                "parser_error": eq_debug.get("parser_error"),
            })
        is_correct = bool(eq_debug.get("correct"))
    elif checker == "multi_part_answer_checker" or family == "multi_part" or equiv == "multi_part_answer":
        from core.checkers.multi_part_answer_checker import check_multi_part_answer
        from core.gencode.table_question_contract import normalize_table_student_answer

        normalized_user_answer = normalize_table_student_answer(user_answer, payload)
        result = check_multi_part_answer(
            normalized_user_answer,
            correct_answer,
            answer_contract=ac,
            payload=payload,
        )
        overall = bool(result.get("overall_correct"))
        per_part = result.get("per_part_results") or []
        if overall:
            msg = "答對了！"
        elif per_part:
            lines = []
            for row in per_part:
                mark = "正確" if row.get("correct") else "錯誤"
                label = str(row.get("label") or row.get("key") or "")
                lines.append(f"{label}：{mark}")
            msg = "部分小題答錯。\n" + "\n".join(lines)
        else:
            msg = "答錯了。"
        log_check_answer_debug(
            skill_id=skill_id,
            current=payload,
            user_answer=user_answer,
            correct_answer=correct_answer,
            check_result=overall,
            checker=checker,
            log=log,
        )
        return {
            "correct": overall,
            "result": msg,
            "per_part_results": per_part,
            "failed_parts": result.get("failed_parts", []),
        }
    elif checker in {
        "decimal_tolerance_checker",
        "integer_checker",
        "numeric_checker",
        "rational_checker",
        "fraction_checker",
    } or (family == "numeric" and checker):
        try:
            numeric_result = grade_numeric_contract_answer(
                user_answer,
                correct_answer,
                ac if isinstance(ac, dict) else {},
                checker=checker,
            )
        except Exception as exc:
            sink = log or logger
            sink.error(
                "[CHECK ANSWER] numeric checker internal error skill_id=%s checker=%s err=%s",
                skill_id,
                checker,
                exc,
                exc_info=True,
            )
            return normalize_grading_result({
                "correct": False,
                "system_error": True,
                "error_code": "CHECKER_EXECUTION_FAILED",
                "result": f"批改系統錯誤：{exc}",
            })
        if numeric_result.get("system_error"):
            sink = log or logger
            sink.error(
                "[CHECK ANSWER] numeric checker system error skill_id=%s checker=%s msg=%s",
                skill_id,
                checker,
                numeric_result.get("result"),
            )
            return normalize_grading_result({
                "correct": False,
                "system_error": True,
                "error_code": "CHECKER_EXECUTION_FAILED",
                "result": str(numeric_result.get("result") or "批改系統錯誤"),
            })
        if numeric_result.get("invalid_input"):
            return normalize_grading_result({
                "correct": False,
                "invalid_input": True,
                "error_code": "ANSWER_PARSE_FAILED",
                "result": str(numeric_result.get("result") or "invalid input"),
            })
        is_correct = bool(numeric_result.get("correct"))
        log_check_answer_debug(
            skill_id=skill_id,
            current=payload,
            user_answer=user_answer,
            correct_answer=correct_answer,
            check_result=is_correct,
            checker=checker,
            log=log,
        )
        display = format_correct_answer_display(correct_answer, payload)
        return normalize_grading_result({
            "correct": is_correct,
            "result": "答對了！" if is_correct else f"答錯了，正確答案是 {display}",
        })
    else:
        try:
            is_correct = check_answer(
                user_answer,
                correct_answer,
                payload=payload,
                answer_contract=ac if isinstance(ac, dict) else None,
                skill_id=skill_id,
            )
        except Exception as exc:
            sink = log or logger
            sink.error(
                "[CHECK ANSWER] checker internal error skill_id=%s checker=%s err=%s",
                skill_id,
                checker,
                exc,
                exc_info=True,
            )
            return normalize_grading_result({
                "correct": False,
                "system_error": True,
                "error_code": "CHECKER_EXECUTION_FAILED",
                "result": f"批改系統錯誤：{exc}",
            })
    log_check_answer_debug(
        skill_id=skill_id,
        current=payload,
        user_answer=user_answer,
        correct_answer=correct_answer,
        check_result=is_correct,
        checker=checker,
        log=log,
        extra=expr_debug,
    )
    display = format_correct_answer_display(correct_answer, payload)
    final_result = normalize_grading_result({
        "correct": is_correct,
        "result": "答對了！" if is_correct else f"答錯了，正確答案是 {display}",
    })
    if expr_debug:
        final_result["required_form_failed"] = bool(expr_debug.get("required_form_failed"))
    return final_result
