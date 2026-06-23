# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re

from flask import jsonify, request, session, current_app
from flask_login import current_user, login_required

from core.adaptive.judge import judge_answer_with_feedback
from core.handwriting_ai_check import (
    HandwritingCheckContext,
    build_handwriting_check_response,
)
from . import practice_bp
from core.adaptive.session_engine import get_rag_hint, submit_and_get_next
from core.vocational_math_b4.adaptive.b4_chapter1_deterministic_allowlist import (
    ordered_b4_chapter1_skills,
)
# Phase 6N: B4 Chapter 2 chapter-mode handler
from core.vocational_math_b4.services.b4_chap2_chapter_mode import (
    build_b4_chap2_chapter_response,
    build_b4_chap2_chapter_runtime_store_entry,
)


_MAX_RUNTIME_SESSIONS = 2
_MAX_TEXT_LEN = 240
_MAX_ANSWER_LEN = 80
_MAX_SUBSKILLS = 6
_MAX_RECENT_RESULTS = 4
_ROUTING_STATE_ALLOWLIST = {
    "mode",
    "current_skill",
    "current_mode",
    "in_remediation",
    "origin_skill",
    "origin_family",
    "remediation_skill",
    "remediation_subskill",
    "bridge_remaining",
    "lock_min_steps",
    "steps_taken",
    "recent_results",
    "remediation_mastery",
    "last_result",
    "return_to_mainline",
    "scenario_stage",
    "demo_start_forced",
    "demo_first_remediation_forced",
    "demo_first_return_forced",
    "milestone_event",
    "milestone_flash_available",
    "unit_completed",
    "local_remediation_completed",
    "assessment_completed",
}


def _trim_text(value: object, *, max_len: int) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len]


def _to_bool_list(value: object, *, max_len: int) -> list[bool]:
    if not isinstance(value, list):
        return []
    out: list[bool] = []
    for item in value:
        out.append(bool(item))
    return out[-max_len:]


def _to_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _runtime_for_ai_handwriting(payload: dict[str, object]) -> dict[str, object]:
    runtime_store = _adaptive_runtime_store()
    session_id = str(payload.get("session_id") or "").strip()
    if session_id and isinstance(runtime_store.get(session_id), dict):
        return dict(runtime_store.get(session_id) or {})
    question_uid = str(payload.get("question_uid") or "").strip()
    if question_uid:
        for item in runtime_store.values():
            if isinstance(item, dict) and str(item.get("question_uid") or "").strip() == question_uid:
                return dict(item)
    return {}


def _call_ai_handwriting_checker(payload: dict[str, object], ctx: HandwritingCheckContext) -> dict[str, object]:
    from core.ai_analyzer import analyze
    from core.ai_wrapper import resolve_gemini_api_key

    return analyze(
        image_data_url=str(payload.get("image_base64") or payload.get("image_data_url") or ""),
        context=ctx.question_text,
        api_key=resolve_gemini_api_key(),
        prerequisite_skills=[],
        correct_answer=str(ctx.correct_answer or ctx.semantic_answer or ""),
    )


@practice_bp.route("/api/practice/ai-check-handwriting", methods=["POST"])
@login_required
def ai_check_handwriting():
    payload = request.get_json(silent=True) or {}
    image_base64 = str(
        payload.get("image_base64")
        or payload.get("image_data_url")
        or payload.get("handwriting_image")
        or ""
    )
    runtime = _runtime_for_ai_handwriting(payload)

    answer_contract = runtime.get("answer_contract")
    if not isinstance(answer_contract, dict):
        answer_contract = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}

    correct_answer = runtime.get("correct_answer", runtime.get("answer"))
    if correct_answer in (None, ""):
        # Backward-compatible fallback for tests and non-adaptive callers. The frontend does not need this.
        correct_answer = payload.get("correct_answer")

    ctx = HandwritingCheckContext(
        question_uid=str(payload.get("question_uid") or runtime.get("question_uid") or ""),
        skill_id=str(payload.get("skill_id") or runtime.get("skill_id") or runtime.get("skill") or ""),
        question_text=str(payload.get("question_text") or runtime.get("question_text") or ""),
        problem_type_id=str(payload.get("problem_type_id") or runtime.get("problem_type_id") or ""),
        presentation_mode=str(payload.get("presentation_mode") or runtime.get("presentation_mode") or ""),
        answer_type=str(payload.get("answer_type") or runtime.get("answer_type") or answer_contract.get("answer_type", "")),
        correct_answer=correct_answer,
        semantic_answer=runtime.get("semantic_answer"),
        answer_contract=answer_contract,
        checker=str(runtime.get("checker") or runtime.get("checker_type") or answer_contract.get("checker", "")),
        equivalence=str(runtime.get("equivalence") or runtime.get("equivalence_type") or answer_contract.get("answer_equivalence", "")),
        choices=list(runtime.get("choices") or payload.get("choices") or []),
        rubric=str(runtime.get("rubric") or ""),
    )

    try:
        ai_result = _call_ai_handwriting_checker(payload, ctx)
    except Exception as exc:
        current_app.logger.warning("[AI handwriting check] failed: %s", exc)
        return jsonify(
            {
                "mode": "unrecognized",
                "is_correct": False,
                "final_answer_correct": None,
                "process_correct": None,
                "recognized_answer": "",
                "recognized_latex": "",
                "recognized_steps": [],
                "first_error_step": None,
                "error_type": "ai_timeout_or_error",
                "feedback": "目前無法清楚辨識，請重新書寫。",
                "confidence": 0.0,
                "should_record_attempt": False,
            }
        ), 200

    response = build_handwriting_check_response(
        image_base64=image_base64,
        ctx=ctx,
        ai_result=ai_result,
    )
    # Do not leak hidden answer/rubric/checker internals to the browser.
    for forbidden in ("correct_answer", "semantic_answer", "answer_contract", "rubric", "checker"):
        response.pop(forbidden, None)
    return jsonify(response), 200


def _normalize_str_list(value: object) -> list[str]:
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            text = str(item or "").strip()
            if text:
                out.append(text)
        return out
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        return [part.strip() for part in raw.replace(",", ";").split(";") if part.strip()]
    return []


def _strip_choice_leading_label(text: str) -> str:
    s = str(text or "").strip()
    s = re.sub(r"^\s*[（(]\s*([A-Za-z])\s*[)）]\s*", "", s)
    s = re.sub(r"^\s*([A-Za-z])\s*[.)．、]\s*", "", s)
    return s.strip()


def _choice_alias_to_index(token: str) -> int | None:
    t = str(token or "").strip()
    if not t:
        return None
    t = t.replace("（", "(").replace("）", ")")
    m = re.match(r"^\(?\s*([A-Za-z])\s*\)?[.)．、]?$", t)
    if m:
        return ord(m.group(1).upper()) - ord("A")
    m = re.match(r"^([1-9]\d*)$", t)
    if m:
        return int(m.group(1)) - 1
    return None


def _choice_display_label_and_text(correct_value: object, choices: list) -> str:
    idx = _choice_alias_to_index(str(correct_value or ""))
    if idx is not None and 0 <= idx < len(choices):
        text = _strip_choice_leading_label(str(choices[idx]))
        return f"({chr(ord('A') + idx)}) {text}"
    raw = _strip_choice_leading_label(str(correct_value or ""))
    for i, ch in enumerate(choices):
        text = _strip_choice_leading_label(str(ch))
        if raw == text:
            return f"({chr(ord('A') + i)}) {text}"
    return str(correct_value or "").strip()


def _slim_routing_state(raw: object) -> dict:
    if not isinstance(raw, dict):
        return {}
    slim: dict = {}
    for key in _ROUTING_STATE_ALLOWLIST:
        if key not in raw:
            continue
        value = raw.get(key)
        if key in {"mode", "current_skill", "origin_skill", "remediation_skill", "remediation_subskill", "origin_family", "scenario_stage", "current_mode", "milestone_event"}:
            slim[key] = _trim_text(value, max_len=96)
        elif key in {"in_remediation", "last_result", "return_to_mainline", "demo_start_forced", "demo_first_remediation_forced", "demo_first_return_forced", "milestone_flash_available", "unit_completed", "local_remediation_completed", "assessment_completed"}:
            slim[key] = bool(value)
        elif key in {"bridge_remaining", "lock_min_steps", "steps_taken"}:
            slim[key] = _to_int(value, 0)
        elif key == "recent_results":
            slim[key] = _to_bool_list(value, max_len=_MAX_RECENT_RESULTS)
        elif key == "remediation_mastery":
            slim[key] = _to_float(value, 0.0)
    return slim


def _slim_subskills(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        text = _trim_text(item, max_len=64)
        if text:
            out.append(text)
        if len(out) >= _MAX_SUBSKILLS:
            break
    return out


def _prune_runtime_store(runtime_store: dict, *, current_session_id: str) -> dict:
    if len(runtime_store) <= _MAX_RUNTIME_SESSIONS:
        return runtime_store
    pruned: dict = {}
    if current_session_id and current_session_id in runtime_store:
        pruned[current_session_id] = runtime_store[current_session_id]
    for key in reversed(list(runtime_store.keys())):
        if key in pruned:
            continue
        pruned[key] = runtime_store[key]
        if len(pruned) >= _MAX_RUNTIME_SESSIONS:
            break
    return pruned


def _adaptive_runtime_store() -> dict:
    store = session.get("adaptive_runtime", {})
    if not isinstance(store, dict):
        store = {}
    else:
        store = _prune_runtime_store(store, current_session_id="")
    return store


def _response_for_frontend(response: dict) -> dict:
    sanitized = dict(response)
    q = dict(sanitized.get("new_question_data", {}) or {})
    q.pop("answer", None)
    q.pop("correct_answer", None)
    sanitized["new_question_data"] = q
    return sanitized


def _pick_first_text(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _build_demo_route_msg(response: dict, payload: dict) -> str:
    """Build a teacher-friendly one-line routing explanation for demo display."""
    try:
        summary = response.get("summary") if isinstance(response.get("summary"), dict) else {}
        routing_state = response.get("routing_state") if isinstance(response.get("routing_state"), dict) else {}
        mode = str(response.get("mode") or payload.get("mode") or routing_state.get("mode") or "").strip().lower()

        target_family = _pick_first_text(
            response.get("display_family"),
            response.get("selected_family_for_render"),
            response.get("target_family_id"),
            routing_state.get("origin_family"),
            summary.get("origin_family"),
            summary.get("origin_family_id"),
        )
        target_subskill = _pick_first_text(
            response.get("display_subskill"),
            response.get("detected_subskill_node"),
            response.get("display_subskill_label"),
        )
        target_subskills = response.get("target_subskills")
        if not target_subskill and isinstance(target_subskills, list) and target_subskills:
            target_subskill = str(target_subskills[0] or "").strip()
        remediation_skill = _pick_first_text(
            response.get("display_skill"),
            response.get("remediation_skill"),
            summary.get("remediation_skill"),
            routing_state.get("remediation_skill"),
        )
        remediation_subskill = _pick_first_text(
            response.get("remediation_subskill"),
            summary.get("remediation_subskill"),
            routing_state.get("remediation_subskill"),
            target_subskill,
        )

        completed = bool(response.get("completed"))
        unit_completed = bool(response.get("unit_completed") or summary.get("unit_completed") or routing_state.get("unit_completed"))
        local_remediation_completed = bool(
            response.get("local_remediation_completed")
            or summary.get("local_remediation_completed")
            or routing_state.get("local_remediation_completed")
        )
        assessment_completed = bool(
            response.get("assessment_completed")
            or summary.get("assessment_completed")
            or routing_state.get("assessment_completed")
        )
        teaching_completed = bool(completed and mode == "teaching")
        display_mode = str(response.get("display_mode") or "").strip().lower()
        milestone_state = str(response.get("milestone_state") or "").strip().lower()
        current_mode = str(response.get("current_mode") or routing_state.get("current_mode") or "").strip().lower()
        post_mode = str(response.get("post_mode") or "").strip().lower()
        in_remediation = bool(response.get("in_remediation") or routing_state.get("in_remediation"))
        return_to_mainline = bool(
            response.get("return_to_mainline")
            or summary.get("return_to_mainline")
            or summary.get("has_returned_to_main")
            or routing_state.get("return_to_mainline")
            or milestone_state == "remediation_returned_success"
            or (current_mode == "remediation" and post_mode == "mainline")
        )

        if completed or unit_completed or assessment_completed or (local_remediation_completed and completed):
            if assessment_completed or mode == "assessment":
                return "本次診斷已完成，系統已整理出本單元掌握情況與後續建議。"
            if unit_completed or teaching_completed:
                return "本單元主線已完成，系統已結束本次教學流程。"
            if local_remediation_completed:
                return "本次補救階段已完成，系統已整理目前掌握情況與下一步建議。"
            return "本次流程已完成，系統已整理出本單元掌握情況與後續建議。"

        if return_to_mainline:
            if target_family:
                return f"補救題表現已穩定，系統現在返回主線，重新檢核【{target_family}】。"
            return "補救題表現已穩定，系統現在返回主線，重新檢核原本卡住的題型。"

        remediation_active = bool(
            display_mode == "remediation"
            or in_remediation
            or current_mode == "remediation"
            or post_mode == "remediation"
        )
        if remediation_active:
            family_text = f"【{target_family}】" if target_family else "主線題型"
            subskill_text = f"【{target_subskill}】" if target_subskill else "關鍵子技能"
            remed_text = remediation_skill or remediation_subskill
            if remed_text:
                return f"偵測到你在{family_text}持續失誤，系統判定卡在{subskill_text}；先切到補救模式加強【{remed_text}】。"
            return f"偵測到你在{family_text}持續失誤，系統判定卡在{subskill_text}；先切到補救模式加強相關前置能力。"

        if target_family:
            return f"目前主線表現穩定，系統維持在【{target_family}】持續檢核。"
        return "目前主線表現穩定，系統維持在本題型持續檢核。"
    except Exception:
        return "系統已更新目前學習狀態。"


@practice_bp.route("/api/adaptive/submit_and_get_next", methods=["POST"])
@login_required
def adaptive_submit_and_get_next():
    payload = request.get_json(silent=True) or {}
    if "student_id" not in payload:
        payload["student_id"] = current_user.id

    try:
        raw_mode = str(payload.get("mode") or "").strip().lower()
        raw_curriculum = str(payload.get("curriculum") or "").strip().lower()
        raw_volume = str(payload.get("volume") or "").strip()
        raw_chapter_id = str(payload.get("chapter_id") or "").strip()
        raw_chapter_name = str(payload.get("chapter_name") or payload.get("chapter") or "").strip()
        raw_entry_mode = str(payload.get("entry_mode") or "").strip().lower()
        raw_step_number = _to_int(payload.get("step_number"), 0)
        raw_session_id = str(payload.get("session_id") or "").strip()
        b4_chapter1_hit = raw_chapter_id == "1" or raw_chapter_name.startswith("1 排列組合")
        # Phase 6N: B4 Chapter 2 chapter-mode detection
        b4_chapter2_hit = raw_chapter_id == "2" or raw_chapter_name.startswith("2 機率")
        is_b4_chapter2_entry = (
            (raw_entry_mode == "chapter" or raw_mode == "chapter")
            and raw_curriculum == "vocational"
            and raw_volume == "數學B4"
            and b4_chapter2_hit
        )

        is_b4_chapter_entry = (
            (raw_entry_mode == "chapter" or raw_mode == "chapter")
            and raw_curriculum == "vocational"
            and raw_volume == "數學B4"
            and b4_chapter1_hit
        )
        is_b4_chapter_bootstrap = is_b4_chapter_entry and raw_step_number == 0 and not raw_session_id

        if is_b4_chapter_bootstrap:
            # Bootstrap first-question path: should not be treated as answer-submission path.
            payload.pop("session_id", None)
            payload.pop("user_answer", None)
            payload.pop("is_correct", None)
            payload.pop("answer_feedback", None)
            payload["entry_mode"] = "chapter"
            payload["mode"] = "teaching"
            if "learning_mode" not in payload:
                payload["learning_mode"] = "main"
            if "practice_kind" not in payload:
                payload["practice_kind"] = "unit_practice"
            if not str(payload.get("skill_id") or "").strip():
                payload["skill_id"] = str(payload.get("starter_skill_id") or "").strip()
            target_skill_ids = _normalize_str_list(payload.get("target_skill_ids"))
            skill_ids = _normalize_str_list(payload.get("skill_ids"))
            unit_skill_ids = _normalize_str_list(payload.get("unit_skill_ids"))
            if not target_skill_ids:
                target_skill_ids = skill_ids or unit_skill_ids
            if not skill_ids:
                skill_ids = target_skill_ids or unit_skill_ids
            if not unit_skill_ids:
                unit_skill_ids = target_skill_ids or skill_ids
            target_skill_ids = ordered_b4_chapter1_skills(target_skill_ids)
            skill_ids = ordered_b4_chapter1_skills(skill_ids)
            unit_skill_ids = ordered_b4_chapter1_skills(unit_skill_ids)
            payload["target_skill_ids"] = target_skill_ids
            payload["skill_ids"] = skill_ids
            payload["unit_skill_ids"] = unit_skill_ids
            try:
                current_app.logger.info(
                    "[Phase5B-FixC][b4_chapter_bootstrap] detected entry_mode=%s mode=%s step_number=%s session_id=%s skill_id=%s target_skill_ids_count=%s unit_skill_ids_count=%s received_keys=%s",
                    payload.get("entry_mode"),
                    payload.get("mode"),
                    payload.get("step_number"),
                    bool(raw_session_id),
                    payload.get("skill_id"),
                    len(target_skill_ids),
                    len(unit_skill_ids),
                    sorted(payload.keys()),
                )
            except Exception:
                pass

        if (
            raw_mode == "chapter"
            and raw_curriculum == "vocational"
            and raw_volume == "數學B4"
            and b4_chapter1_hit
        ):
            # Payload bridge: keep chapter context fields but normalize runtime mode for session_engine.
            payload["entry_mode"] = "chapter"
            payload["mode"] = "teaching"
            if "learning_mode" not in payload:
                payload["learning_mode"] = "main"
            if "practice_kind" not in payload:
                payload["practice_kind"] = "unit_practice"

        runtime_store = _adaptive_runtime_store()
        session_id = str(payload.get("session_id") or "")
        runtime = runtime_store.get(session_id, {}) if session_id else {}

        grading_analysis = None

        # ── Phase 6N: B4 Chapter 2 chapter mode — lightweight deterministic handler ──
        if is_b4_chapter2_entry:
            response = build_b4_chap2_chapter_response(payload, runtime=runtime)
            grading_analysis = response.get("grading_analysis")
            if grading_analysis is not None:
                # grading_analysis already embedded in response; also surface at top level
                response["grading_analysis"] = grading_analysis
            next_session_id = response["session_id"]
            chap2_step_index = int(response.get("chapter_current_step") or 0)
            if response.get("completed"):
                runtime_store.pop(next_session_id, None)
            else:
                runtime_store[next_session_id] = build_b4_chap2_chapter_runtime_store_entry(
                    response, chap2_step_index
                )
                runtime_store = _prune_runtime_store(runtime_store, current_session_id=next_session_id)
            session["adaptive_runtime"] = runtime_store
            session.modified = True
            try:
                current_app.logger.info(
                    "[Phase6N][b4_chap2_chapter_mode] chapter_id=2 step=%s session_id=%s completed=%s stage=%s",
                    chap2_step_index,
                    next_session_id,
                    response.get("completed"),
                    response.get("chapter_stage"),
                )
            except Exception:
                pass
            if not str(response.get("demo_route_msg") or "").strip():
                response["demo_route_msg"] = "B4 第二章診斷進行中。"
            return jsonify(_response_for_frontend(response))
        # ── End Phase 6N Chap2 branch ──

        if runtime:
            payload["last_family_id"] = runtime.get("family_id", payload.get("last_family_id"))
            payload["last_subskills"] = runtime.get("subskill_nodes", payload.get("last_subskills"))
            payload["routing_state"] = _slim_routing_state(runtime.get("routing_state", payload.get("routing_state")))
            payload["last_expected_answer"] = runtime.get("correct_answer", payload.get("last_expected_answer"))
            payload["last_question_text"] = runtime.get("question_text", payload.get("last_question_text"))
            if "user_answer" in payload and "is_correct" not in payload:
                judged = judge_answer_with_feedback(
                    payload.get("user_answer"),
                    runtime.get("correct_answer"),
                    question_text=runtime.get("question_text", ""),
                    family_id=runtime.get("family_id"),
                    choices=runtime.get("choices", []),
                    answer_type=runtime.get("answer_type", ""),
                    checker_type=runtime.get("checker_type", ""),
                )
                payload["is_correct"] = bool(judged.get("is_correct", False))
                payload["answer_feedback"] = str(judged.get("feedback") or "")
                choices = list(runtime.get("choices") or [])
                answer_type = str(runtime.get("answer_type") or "").strip().lower()
                checker_type = str(runtime.get("checker_type") or "").strip().lower()
                if (not payload["is_correct"]) and choices and (answer_type == "choice" or checker_type == "choice_checker"):
                    payload["answer_feedback"] = f"答錯了，正確答案是 {_choice_display_label_and_text(runtime.get('correct_answer'), choices)}"
                fam = _trim_text(runtime.get("family_id"), max_len=24)
                grading_analysis = {
                    "family_id": fam,
                    "error_mechanism": "unknown",
                    "step_focus": "",
                    "main_issue": str(payload.get("answer_feedback") or ""),
                    "status": "correct" if payload["is_correct"] else "incorrect",
                    "expected_answer": _trim_text(runtime.get("correct_answer"), max_len=_MAX_ANSWER_LEN),
                    "answer_feedback": str(payload.get("answer_feedback") or ""),
                    "analysis_source": str(judged.get("analysis_source") or "generic_text_answer_judge"),
                    "is_correct": bool(payload["is_correct"]),
                    "grading_step": int(payload.get("step_number") or 0),
                }
            payload["last_user_answer"] = payload.get("user_answer", payload.get("last_user_answer"))
        else:
            payload["routing_state"] = _slim_routing_state(payload.get("routing_state"))

        response = submit_and_get_next(payload)
        if grading_analysis is not None:
            response["grading_analysis"] = grading_analysis
            try:
                print(
                    f"[adaptive_submit] grading_analysis_source={grading_analysis.get('analysis_source')} "
                    f"family_id={grading_analysis.get('family_id')} status={grading_analysis.get('status')}",
                    flush=True,
                )
            except Exception:
                pass
        if payload.get("answer_feedback"):
            response["answer_feedback"] = str(payload.get("answer_feedback"))
        next_session_id = response["session_id"]
        if response.get("completed"):
            runtime_store.pop(next_session_id, None)
        else:
            runtime_store[next_session_id] = {
                "family_id": _trim_text(response.get("target_family_id"), max_len=24),
                "subskill_nodes": _slim_subskills(response.get("target_subskills")),
                "correct_answer": _trim_text(
                    response["new_question_data"].get("correct_answer") or response["new_question_data"].get("answer") or "",
                    max_len=_MAX_ANSWER_LEN,
                ),
                "question_text": _trim_text(
                    response["new_question_data"].get("question_text") or response["new_question_data"].get("question") or "",
                    max_len=_MAX_TEXT_LEN,
                ),
                "choices": list(response["new_question_data"].get("choices") or []),
                "answer_type": str(response["new_question_data"].get("answer_type") or ""),
                "checker_type": str(response["new_question_data"].get("checker_type") or ""),
                "routing_state": _slim_routing_state(response.get("routing_state", {})),
            }
            runtime_store = _prune_runtime_store(runtime_store, current_session_id=next_session_id)
        session["adaptive_runtime"] = runtime_store
        try:
            runtime_size = len(json.dumps(runtime_store, ensure_ascii=False))
            print(
                f"[adaptive_runtime_session] entries={len(runtime_store)} approx_json_bytes={runtime_size}",
                flush=True,
            )
        except Exception:
            pass
        session.modified = True
    except ValueError as exc:
        required_any_skill_scope = bool(
            str(payload.get("skill_id") or "").strip()
            or (isinstance(payload.get("unit_skill_ids"), list) and len(payload.get("unit_skill_ids")) > 0)
            or (isinstance(payload.get("target_skill_ids"), list) and len(payload.get("target_skill_ids")) > 0)
            or (isinstance(payload.get("skill_ids"), list) and len(payload.get("skill_ids")) > 0)
        )
        missing_fields: list[str] = []
        if "step_number" not in payload:
            missing_fields.append("step_number")
        if "student_id" not in payload:
            missing_fields.append("student_id")
        if not required_any_skill_scope:
            missing_fields.append("skill_scope(skill_id|unit_skill_ids|target_skill_ids|skill_ids)")
        return jsonify(
            {
                "error": str(exc),
                "received_keys": sorted(payload.keys()),
                "missing_fields": missing_fields,
                "mode": str(payload.get("mode") or ""),
                "entry_mode": str(payload.get("entry_mode") or ""),
                "step_number": payload.get("step_number"),
                "skill_id": str(payload.get("skill_id") or ""),
                "target_skill_ids_count": (
                    len(payload.get("target_skill_ids"))
                    if isinstance(payload.get("target_skill_ids"), list)
                    else 0
                ),
                "unit_skill_ids_count": (
                    len(payload.get("unit_skill_ids"))
                    if isinstance(payload.get("unit_skill_ids"), list)
                    else 0
                ),
                "internal_exception_type": type(exc).__name__,
                "internal_exception_message": str(exc),
            }
        ), 400
    except Exception as exc:
        return jsonify({"error": f"adaptive engine failure: {exc}"}), 500
    response["demo_route_msg"] = _build_demo_route_msg(response, payload)
    if not str(response.get("demo_route_msg") or "").strip():
        response["demo_route_msg"] = "系統已更新目前學習狀態。"
    return jsonify(_response_for_frontend(response))


@practice_bp.route("/api/adaptive/rag_settings", methods=["GET"])
@login_required
def api_adaptive_rag_settings():
    import os
    rag_path = os.path.join(current_app.root_path, '..', 'configs', 'rag_settings.json')
    if os.path.exists(rag_path):
        try:
            with open(rag_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Sync memory threshold when loading if it differs
                if 'threshold' in data:
                    current_app.config['ADVANCED_RAG_NAIVE_THRESHOLD'] = data['threshold']
                if 'enable_ai_chat' in data:
                    current_app.config['ADVANCED_RAG_ENABLE_AI_CHAT'] = data['enable_ai_chat']
                # ensure default if missing
                if 'enable_ai_chat' not in data:
                    data['enable_ai_chat'] = True
                return jsonify(data)
        except Exception as e:
            print(f"Error reading rag_settings: {e}")
            pass
    return jsonify({
        'threshold': current_app.config.get('ADVANCED_RAG_NAIVE_THRESHOLD', 0.40),
        'target_type': 'practice',
        'enable_ai_chat': current_app.config.get('ADVANCED_RAG_ENABLE_AI_CHAT', True)
    })


@practice_bp.route("/api/adaptive/rag_hint", methods=["GET"])
@login_required
def adaptive_rag_hint():
    nodes = request.args.getlist("subskill_nodes")
    if not nodes:
        raw = request.args.get("subskill_nodes", "")
        nodes = [part.strip() for part in raw.replace(",", ";").split(";") if part.strip()]
    skill_id = request.args.get("skill_id", "").strip()
    family_id = request.args.get("family_id", "").strip()
    question_context = request.args.get("question_context", "").strip()
    question_text = request.args.get("question_text", "").strip()
    unit_skill_ids = request.args.getlist("unit_skill_ids")
    if not unit_skill_ids:
        raw_unit_skill_ids = request.args.get("unit_skill_ids", "")
        unit_skill_ids = [part.strip() for part in raw_unit_skill_ids.replace(",", ";").split(";") if part.strip()]

    try:
        response = get_rag_hint(
            nodes,
            skill_id=skill_id,
            family_id=family_id,
            question_context=question_context,
            question_text=question_text,
            unit_skill_ids=unit_skill_ids,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"rag hint failure: {exc}"}), 500
    return jsonify(response)


@practice_bp.route('/api/adaptive/adv_rag_search', methods=['POST'])
@login_required
def api_adv_rag_search():
    """Advanced RAG hybrid search API."""
    data = request.get_json(silent=True) or {}
    query = (data.get('query') or '').strip()
    
    if not query:
        return jsonify({"results": [], "error": "請輸入問題"}), 400
        
    try:
        from core.advanced_rag_engine import adv_rag_search
        results = adv_rag_search(query, top_k=5)
        return jsonify({"results": results})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"results": [], "error": str(e)}), 500


def _adv_rag_invoke_tutor(prompt: str, provider: str) -> dict:
    """與 advanced_rag_engine.adv_rag_chat 相同的 LLM 呼叫方式（不重複改 engine）。"""
    provider = (provider or "local").strip().lower()
    if provider == "local":
        from core.ai_client import call_ai

        response = call_ai("tutor", prompt)
        return {"reply": getattr(response, "text", str(response)), "provider": "local"}

    from core.ai_analyzer import gemini_model

    if not gemini_model:
        return {"reply": "目前 Google API 助教尚未啟用，請改用本地模型。", "provider": "google"}

    import google.generativeai as genai

    response = gemini_model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
        ),
    )
    return {"reply": response.text, "provider": "google"}


@practice_bp.route('/api/adaptive/adv_rag_chat', methods=['POST'])
@login_required
def api_adv_rag_chat():
    """RAG + LLM chat API for generating hints/short lessons from retrieved materials."""
    data = request.get_json(silent=True) or {}
    query = (data.get('query') or '').strip()
    question_text = (data.get('question_text') or '').strip()
    family_id = (data.get('family_id') or '').strip()
    retrieved_skills = data.get('retrieved_skills') or []
    # Auto-detect provider from ai_settings when frontend does not explicitly specify
    _raw_provider = (data.get('provider') or '').strip().lower()
    if not _raw_provider:
        try:
            from core.ai_settings import get_effective_model_config
            _cfg = get_effective_model_config("tutor")
            _raw_provider = str(_cfg.get("provider", "local")).strip().lower()
        except Exception:
            _raw_provider = 'local'
    provider = _raw_provider
    use_rag = data.get('use_rag', True)

    if not query:
        return jsonify({"reply": "請提供問題"}), 400

    try:
        if not current_app.config.get('ADVANCED_RAG_ENABLE_AI_CHAT', True):
            return jsonify({"reply": "目前 AI 助教已由老師關閉"})

        if not use_rag:
            raw_prompt = query
            if question_text:
                raw_prompt = f"以下是學生目前的題目：\n{question_text}\n\n學生的問題：\n{query}"
            print(f"[RAG PROMPT SELECT] Direct chat without RAG. prompt_key=direct")
            result = _adv_rag_invoke_tutor(raw_prompt, provider)
            return jsonify(result)

        is_learning_intent = any(
            kw in query
            for kw in (
                "不會",
                "不懂",
                "看不懂",
                "怎麼算",
                "怎麼做",
                "為什麼",
                "可以教",
                "教我",
            )
        )
        has_retrieved_skills = bool(retrieved_skills)
        # 自適應介面的 RAG 助教應與 admin/ai_prompt_settings 的知識庫助教 prompt 同步。
        # 只要目前已有檢索結果，就優先走 rag_tutor_prompt，避免被 tutor_hint_prompt 壓成單行提示。
        prompt_key = "rag_tutor_prompt" if has_retrieved_skills else "tutor_hint_prompt"

        print(
            f"[RAG PROMPT SELECT] intent={'learning' if is_learning_intent else 'hint'} "
            f"has_retrieved_skills={has_retrieved_skills} prompt={prompt_key}"
        )

        if prompt_key == "rag_tutor_prompt":
            from core.prompts.composer import compose_prompt
            from core.rag_engine import _label_node, _parse_subskill_nodes

            first = retrieved_skills[0]
            ch_name = (
                first.get("chinese_name")
                or first.get("ch_name")
                or first.get("skill_ch_name")
                or "（未命名技能）"
            )
            fam = first.get("family_name") or ""
            family_name_block = f"（{fam}）" if fam else ""
            subs = _parse_subskill_nodes(first.get("subskill_nodes"))
            subskill_text = "、".join(_label_node(n) for n in subs) if subs else "核心概念"
            if len(retrieved_skills) > 1:
                names = [
                    str(s.get("chinese_name") or s.get("ch_name") or s.get("skill_ch_name") or "").strip()
                    for s in retrieved_skills[1:6]
                ]
                names = [n for n in names if n]
                if names:
                    subskill_text = subskill_text + "\n（另含相關檢索：" + "、".join(names) + "）"
            uq = query
            if question_text:
                uq = f"[目前題目]\n{question_text}\n\n{uq}"
            if family_id:
                uq = f"[family_id: {family_id}]\n{uq}"
            prompt, _source = compose_prompt(
                task_key="rag_tutor_prompt",
                query=uq,
                ch_name=ch_name,
                family_name_block=family_name_block,
                subskill_text=subskill_text,
                route_label="Adaptive-AdvRAG",
            )
            result = _adv_rag_invoke_tutor(prompt, provider)
            return jsonify(result)

        from core.advanced_rag_engine import adv_rag_chat

        result = adv_rag_chat(
            query,
            retrieved_skills,
            provider=provider,
            question_text=question_text,
            family_id=family_id,
        )
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"reply": f"AI 發生錯誤: {e}"}), 500
