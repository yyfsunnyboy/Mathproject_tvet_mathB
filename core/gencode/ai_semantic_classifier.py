from __future__ import annotations

import json
import re
from typing import Any, Callable

from core.gencode.classification_candidates import apply_ai_candidate_selection
from core.gencode.gemini_json_parse import parse_ai_semantic_json
from core.gencode.gencode_ai_resolve import log_ai_semantic_classifier, resolve_gencode_ai_client
from core.gencode.phase1_anchor_contract import phase1_enforcement_assertion_block
from core.gencode.problem_type_canonicalizer import format_math_meta_tags_for_prompt
from core.gencode.source_structure_context import build_sequence_context_for_prompt
from core.gencode.task_families import task_family_for_task

PROMPT_VERSION = "gencode_ai_semantic_classifier_v5_skill_scoped_safe_json"

_AI_MOCK_HANDLER: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None = None

SemanticClassification = dict[str, Any]

AI_UNAVAILABLE_REASONS = frozenset(
    {
        "missing_api_key",
        "provider_not_configured",
        "model_not_configured",
        "ai_wrapper_error",
        "timeout",
        "provider_response_error",
        "disabled_by_config",
    }
)

AI_INVALID_RESPONSE_REASONS = frozenset(
    {
        "json_parse_error",
        "invalid_candidate_id",
        "schema_missing_fields",
        "empty_ai_response",
        "no_json_object",
        "json_root_not_object",
        "unknown_candidate_id",
    }
)


def set_ai_semantic_classifier_mock(handler: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]] | None) -> None:
    """Test hook: replace live AI calls with a deterministic handler."""
    global _AI_MOCK_HANDLER
    _AI_MOCK_HANDLER = handler


def _question_text(example: dict[str, Any]) -> str:
    for k in ("problem_text", "problem", "question", "stem", "content"):
        v = str(example.get(k, "")).strip()
        if v:
            return v
    return ""


def _build_prompt(
    example: dict[str, Any],
    main_skill_anchor: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> str:
    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else {}
    struct_ctx = example.get("source_structure_context") if isinstance(example.get("source_structure_context"), dict) else {}
    seq_ctx = example.get("source_sequence_context") if isinstance(example.get("source_sequence_context"), dict) else {}
    structure_block = build_sequence_context_for_prompt(struct_ctx, seq_ctx) if struct_ctx else ""
    meta_tags = example.get("math_meta_tags")
    if not isinstance(meta_tags, list):
        meta_tags = []
    meta_block = format_math_meta_tags_for_prompt(meta_tags)
    cand_lines = []
    for c in candidates:
        if not isinstance(c, dict):
            continue
        cand_lines.append(
            {
                "candidate_id": c.get("candidate_id"),
                "target_task": c.get("target_task"),
                "task_family": c.get("task_family"),
                "candidate_source": c.get("candidate_source"),
                "in_anchor_scope": c.get("in_anchor_scope"),
                "label": c.get("label"),
            }
        )

    return (
        phase1_enforcement_assertion_block(anchor, include_anchor_fields=False)
        + "You are a math subskill selector for a skill that is ALREADY confirmed by teachers.\n"
        "Do NOT decide whether the example belongs to this skill_id.\n"
        "Do NOT question whether examples belong to a different family.\n"
        "Pick the best subskill candidate_id ONLY from the provided list.\n"
        "Do NOT invent new target_task or task_family values.\n"
        "Choosing needs_review is FORBIDDEN unless the stem is truly unreadable.\n"
        "Prefer anchor-scoped candidates over outsider candidates.\n"
        "Segment-ratio / on-segment / find point coordinate stems belong to division-point subskills, "
        "NOT distance-between-two-points, when those subskills are in the candidate list.\n"
        "Quadratic inequality / factoring skills: prefer factor_quadratic_by_cross_multiplication "
        "or solve_quadratic_inequality over contextual_application, compute_numeric, or absolute-value tasks.\n"
        "When the stem asks to factor a quadratic trinomial (e.g. cross multiplication / 十字交乘法), "
        "choose factor_quadratic_by_cross_multiplication.\n\n"
        "Skill anchor (trusted):\n"
        f"- skill_id: {anchor.get('skill_id', '')}\n"
        f"- skill_ch_name: {anchor.get('skill_ch_name', '')}\n"
        f"- skill_anchor_scope: {anchor.get('skill_anchor_scope', '')}\n"
        f"- expected_task_families: {anchor.get('expected_task_families', [])}\n"
        f"- expected_subskill_candidates: {anchor.get('expected_subskill_candidates', [])}\n\n"
        f"{meta_block}"
        f"{structure_block}\n\n"
        "Current example:\n"
        f"- example_id: {example.get('id') or example.get('example_id', '')}\n"
        f"- question_text: {_question_text(example)}\n"
        f"- answer: {str(example.get('correct_answer') or example.get('answer', '')).strip()}\n"
        f"- source_type: {str(example.get('source_type', '')).strip()}\n\n"
        "Candidates (choose exactly one best_candidate_id):\n"
        f"{json.dumps(cand_lines, ensure_ascii=False, indent=2)}\n\n"
        "Output ONLY a single JSON object (no markdown fences, no prose before/after).\n"
        "Required keys: best_candidate_id, confidence (0-1), evidence (array of plain-text strings), "
        "rejected_candidates (object), requires_human_action (bool), notes (string).\n"
        "In evidence and notes use plain language only — do NOT include raw LaTeX such as \\overline{AB}.\n"
        "Prefer descriptions like「線段 AB 長度」or「2AC 等於 3BC」.\n"
        "If you must mention a backslash in JSON strings, escape it as \\\\ (double backslash).\n"
    )


def _normalize_classification(raw: dict[str, Any]) -> SemanticClassification:
    target = str(raw.get("target_task", "")).strip()
    family = str(raw.get("task_family", "")).strip() or task_family_for_task(target)
    try:
        conf = float(raw.get("confidence", 0.0) or 0.0)
    except Exception:
        conf = 0.0
    conf = max(0.0, min(1.0, conf))
    evidence = raw.get("evidence", [])
    if not isinstance(evidence, list):
        evidence = [str(evidence)] if evidence else []
    neg = raw.get("negative_evidence", {})
    if not isinstance(neg, dict):
        neg = {}
    mos = raw.get("math_objects", [])
    if not isinstance(mos, list):
        mos = []
    return {
        "target_task": target,
        "task_family": family,
        "math_objects": [str(m).strip() for m in mos if str(m).strip()],
        "answer_type": str(raw.get("answer_type", "")).strip(),
        "answer_shape": str(raw.get("answer_shape", "")).strip(),
        "confidence": conf,
        "evidence": [str(e).strip() for e in evidence if str(e).strip()],
        "negative_evidence": {str(k): str(v) for k, v in neg.items()},
        "requires_human_action": bool(raw.get("requires_human_action", False)),
        "possible_structure_mismatch": bool(raw.get("possible_structure_mismatch", False)),
        "notes": str(raw.get("notes", "")).strip(),
        "available": True,
        "error": "",
        "ai_unavailable_reason": "",
        "prompt_version": PROMPT_VERSION,
    }


def categorize_ai_unavailability(error: str, *, error_type: str = "") -> str:
    explicit = str(error_type or "").strip()
    if explicit in AI_UNAVAILABLE_REASONS:
        return explicit
    msg = str(error or "").strip().lower()
    if not msg:
        return ""
    if "missing_api_key" in msg or "api_key_missing" in msg or ("api" in msg and "key" in msg and "missing" in msg):
        return "missing_api_key"
    if "model_not_configured" in msg or ("model" in msg and "not configured" in msg):
        return "model_not_configured"
    if "provider_not_configured" in msg or "no_google_role" in msg:
        return "provider_not_configured"
    if "timeout" in msg or "timed out" in msg:
        return "timeout"
    if "disabled" in msg:
        return "disabled_by_config"
    if any(tok in msg for tok in ("error:", "google ai", "gemini", "permission", "unauthorized", "429", "503", "provider_response_error")):
        return "provider_response_error"
    if "wrapper" in msg or "client init" in msg:
        return "ai_wrapper_error"
    return "ai_wrapper_error"


def _exception_reason(exc: BaseException) -> str:
    from concurrent.futures import TimeoutError as FuturesTimeoutError

    if isinstance(exc, (TimeoutError, FuturesTimeoutError)):
        return "timeout"
    msg = str(exc).lower()
    if "timeout" in msg or "timed out" in msg:
        return "timeout"
    if "provider_response_error" in msg or msg.startswith("error:"):
        return "provider_response_error"
    if isinstance(exc, json.JSONDecodeError) or (
        isinstance(exc, ValueError) and any(tok in msg for tok in ("no_json", "empty_ai", "json_decode", "json_root"))
    ):
        return "json_parse_error"
    if any(tok in msg for tok in ("error:", "google ai", "gemini", "api key", "permission", "provider_response_error")):
        return "provider_response_error"
    return categorize_ai_unavailability(str(exc))


def _unavailable_result(
    *,
    error: str,
    reason: str,
    skill_id: str = "",
    example_id: Any = "",
    client_meta: dict[str, Any] | None = None,
) -> SemanticClassification:
    meta = client_meta if isinstance(client_meta, dict) else {}
    log_ai_semantic_classifier(
        skill_id=skill_id,
        example_id=example_id,
        provider=str(meta.get("provider", "")),
        model=str(meta.get("model", "")),
        has_api_key=bool(meta.get("has_api_key", False)),
        status="unavailable",
        error_type=reason,
        error_message=error,
    )
    return {
        "target_task": "",
        "task_family": "",
        "math_objects": [],
        "answer_type": "",
        "answer_shape": "",
        "confidence": 0.0,
        "evidence": [],
        "negative_evidence": {},
        "requires_human_action": False,
        "possible_structure_mismatch": False,
        "notes": "",
        "available": False,
        "error": error,
        "ai_unavailable_reason": reason,
        "ai_semantic_status": "unavailable",
        "ai_invalid_response_reason": "",
        "prompt_version": PROMPT_VERSION,
    }


def _invalid_response_result(
    *,
    error: str,
    reason: str,
    skill_id: str = "",
    example_id: Any = "",
    client_meta: dict[str, Any] | None = None,
    parse_diagnostics: dict[str, Any] | None = None,
) -> SemanticClassification:
    meta = client_meta if isinstance(client_meta, dict) else {}
    diag = parse_diagnostics if isinstance(parse_diagnostics, dict) else {}
    inv_reason = reason if reason in AI_INVALID_RESPONSE_REASONS else "json_parse_error"
    log_ai_semantic_classifier(
        skill_id=skill_id,
        example_id=example_id,
        provider=str(meta.get("provider", "")),
        model=str(meta.get("model", "")),
        has_api_key=bool(meta.get("has_api_key", True)),
        status="invalid_response",
        error_type=inv_reason,
        error_message=error,
    )
    return {
        "target_task": "",
        "task_family": "",
        "math_objects": [],
        "answer_type": "",
        "answer_shape": "",
        "confidence": 0.0,
        "evidence": [],
        "negative_evidence": {},
        "requires_human_action": True,
        "possible_structure_mismatch": False,
        "notes": "",
        "available": False,
        "error": error,
        "ai_unavailable_reason": "",
        "ai_semantic_status": "invalid_response",
        "ai_invalid_response_reason": inv_reason,
        "parser_error": str(diag.get("parser_error", error)),
        "raw_response_preview": str(diag.get("raw_response_preview", "")),
        "sanitized_response_preview": str(diag.get("sanitized_response_preview", "")),
        "failed_stage": str(diag.get("failed_stage", "ai_json_parse")),
        "prompt_version": PROMPT_VERSION,
    }


def _parse_ai_json(text: str) -> tuple[dict[str, Any], dict[str, Any]]:
    return parse_ai_semantic_json(text)


def _is_invalid_response_exception(exc: BaseException) -> bool:
    if isinstance(exc, json.JSONDecodeError):
        return True
    if isinstance(exc, ValueError):
        msg = str(exc).lower()
        return any(
            tok in msg
            for tok in (
                "empty_ai",
                "no_json",
                "json_root",
                "unknown_candidate",
                "schema_missing",
                "invalid_candidate",
            )
        )
    return _exception_reason(exc) == "json_parse_error"


def classify_example_semantics_with_ai(
    example: dict[str, Any],
    main_skill_anchor: dict[str, Any] | None = None,
    *,
    client: Any = None,
    force_unavailable: bool = False,
    skill_scoped_candidates: list[dict[str, Any]] | None = None,
) -> SemanticClassification:
    """
    AI-first semantic classification for a single source example.
    Expects example to carry source_structure_context / source_sequence_context when available.
    """
    anchor = main_skill_anchor if isinstance(main_skill_anchor, dict) else {}
    skill_id = str(anchor.get("skill_id") or example.get("skill_id") or "").strip()
    example_id = example.get("id") or example.get("example_id", "")

    candidates = skill_scoped_candidates
    if candidates is None:
        candidates = example.get("_skill_scoped_candidates") if isinstance(example.get("_skill_scoped_candidates"), list) else []

    if _AI_MOCK_HANDLER is not None:
        try:
            raw = _AI_MOCK_HANDLER(example, anchor)
            out = apply_ai_candidate_selection(raw, candidates) if candidates else _normalize_classification(raw)
            out["ai_semantic_status"] = "ok"
            out["ai_invalid_response_reason"] = ""
            out["prompt_version"] = PROMPT_VERSION
            log_ai_semantic_classifier(
                skill_id=skill_id,
                example_id=example_id,
                provider="mock",
                model="mock",
                has_api_key=True,
                status="ok",
                error_type="",
                error_message="",
            )
            return out
        except Exception as ex:
            reason = _exception_reason(ex)
            return _unavailable_result(
                error=str(ex),
                reason=reason,
                skill_id=skill_id,
                example_id=example_id,
            )

    if force_unavailable:
        return _unavailable_result(
            error="ai_unavailable_forced",
            reason="disabled_by_config",
            skill_id=skill_id,
            example_id=example_id,
        )

    client_meta: dict[str, Any] = {}
    try:
        from core.ai_wrapper import call_ai_with_retry, resolve_gemini_api_key

        api_key, key_source = resolve_gemini_api_key()
        has_api_key = bool(str(api_key or "").strip())
        if client is None:
            client, client_meta = resolve_gencode_ai_client()
            client_meta["api_key_source"] = key_source or client_meta.get("api_key_source", "")
            client_meta["has_api_key"] = has_api_key
        else:
            client_meta = {"provider": "injected", "model": getattr(client, "model_name", ""), "has_api_key": has_api_key}

        if not has_api_key:
            return _unavailable_result(
                error="ai_api_key_missing",
                reason="missing_api_key",
                skill_id=skill_id,
                example_id=example_id,
                client_meta={**client_meta, "has_api_key": False},
            )

        if client is None:
            reason = str(client_meta.get("error_type") or categorize_ai_unavailability(str(client_meta.get("failure_reason", ""))))
            if reason not in AI_UNAVAILABLE_REASONS:
                reason = "provider_not_configured"
            return _unavailable_result(
                error=str(client_meta.get("failure_reason") or reason),
                reason=reason,
                skill_id=skill_id,
                example_id=example_id,
                client_meta=client_meta,
            )

        if not candidates:
            raise ValueError("skill_scoped_candidates_missing")
        prompt = _build_prompt(example, anchor, candidates)
        resp = call_ai_with_retry(client, prompt, max_retries=1, retry_delay=1, timeout=60)
        raw_text = str(getattr(resp, "text", "") or "")
        if raw_text.strip().lower().startswith("error:"):
            return _unavailable_result(
                error=raw_text[:200],
                reason="provider_response_error",
                skill_id=skill_id,
                example_id=example_id,
                client_meta=client_meta,
            )
        try:
            parsed, parse_diag = _parse_ai_json(raw_text)
        except (json.JSONDecodeError, ValueError) as parse_ex:
            from core.gencode.gemini_json_parse import sanitize_gemini_json_text

            inv_reason = "json_parse_error"
            msg = str(parse_ex).lower()
            if "empty_ai" in msg:
                inv_reason = "empty_ai_response"
            elif "no_json" in msg:
                inv_reason = "no_json_object"
            elif "schema_missing" in msg:
                inv_reason = "schema_missing_fields"
            return _invalid_response_result(
                error=str(parse_ex),
                reason=inv_reason,
                skill_id=skill_id,
                example_id=example_id,
                client_meta=client_meta,
                parse_diagnostics={
                    "raw_response_preview": raw_text[:400],
                    "sanitized_response_preview": sanitize_gemini_json_text(raw_text)[:400],
                    "parser_error": str(parse_ex),
                    "failed_stage": "ai_json_parse",
                },
            )
        if not str(parsed.get("best_candidate_id", "")).strip():
            return _invalid_response_result(
                error="schema_missing_fields:best_candidate_id",
                reason="schema_missing_fields",
                skill_id=skill_id,
                example_id=example_id,
                client_meta=client_meta,
                parse_diagnostics=parse_diag,
            )
        out = apply_ai_candidate_selection(parsed, candidates)
        if str(out.get("error", "")).strip() == "unknown_candidate_id":
            return _invalid_response_result(
                error="unknown_candidate_id",
                reason="invalid_candidate_id",
                skill_id=skill_id,
                example_id=example_id,
                client_meta=client_meta,
                parse_diagnostics={
                    **parse_diag,
                    "raw_response_preview": parse_diag.get("raw_response_preview") or raw_text[:400],
                },
            )
        out["ai_semantic_status"] = "ok"
        out["ai_invalid_response_reason"] = ""
        out["prompt_version"] = PROMPT_VERSION
        log_ai_semantic_classifier(
            skill_id=skill_id,
            example_id=example_id,
            provider=str(client_meta.get("provider", "google")),
            model=str(client_meta.get("model", getattr(client, "model_name", ""))),
            has_api_key=True,
            status="ok",
            error_type="",
            error_message="",
        )
        return out
    except Exception as ex:
        msg = str(ex).lower()
        if "provider_response_error" in msg:
            return _unavailable_result(
                error=str(ex),
                reason="provider_response_error",
                skill_id=skill_id,
                example_id=example_id,
                client_meta=client_meta,
            )
        if _is_invalid_response_exception(ex):
            reason = _exception_reason(ex)
            if reason not in AI_INVALID_RESPONSE_REASONS:
                reason = "json_parse_error"
            return _invalid_response_result(
                error=str(ex),
                reason=reason,
                skill_id=skill_id,
                example_id=example_id,
                client_meta=client_meta,
            )
        reason = _exception_reason(ex)
        return _unavailable_result(
            error=str(ex),
            reason=reason,
            skill_id=skill_id,
            example_id=example_id,
            client_meta=client_meta,
        )
