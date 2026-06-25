from __future__ import annotations

import base64
import logging
import re
from typing import Any

IMAGE_PAYLOAD_FIELDS = (
    "composite_image_data_url",
    "image_data_url",
    "student_strokes_image_data_url",
    "image_base64",
    "canvas_image",
    "drawing_image",
    "handwriting_image",
)

SUPPORTED_DRAWING_TYPES = frozenset(
    {
        "histogram",
        "frequency_polygon",
        "histogram_and_frequency_polygon",
        "bar_chart",
        "line_chart",
        "scatter_plot",
        "coordinate_point_plot",
        "line_graph",
        "function_graph",
        "number_line",
        "geometry_construction",
        "statistical_chart",
    }
)

_DATA_URL_RE = re.compile(r"^data:image/[a-zA-Z0-9.+-]+;base64,")
logger = logging.getLogger(__name__)


def find_answer_image(payload: dict[str, Any] | None) -> tuple[str | None, str]:
    """Return the canonical drawing image data URL from accepted payload aliases."""
    if not isinstance(payload, dict):
        return None, ""
    for field in IMAGE_PAYLOAD_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str):
            continue
        image = value.strip()
        if not image:
            continue
        if _DATA_URL_RE.match(image):
            return image, field
        if _looks_like_base64_image(image):
            return f"data:image/png;base64,{image}", field
    return None, ""


def normalize_answer_image(payload: dict[str, Any] | None) -> str | None:
    image, _field = find_answer_image(payload)
    return image


def find_student_strokes_image(payload: dict[str, Any] | None) -> tuple[str | None, str]:
    """Return strokes-only image for blank detection when available."""
    if not isinstance(payload, dict):
        return None, ""
    for field in ("student_strokes_image_data_url", "drawing_image", "canvas_image", "handwriting_image"):
        value = payload.get(field)
        if not isinstance(value, str):
            continue
        image = value.strip()
        if not image:
            continue
        if _DATA_URL_RE.match(image):
            return image, field
        if _looks_like_base64_image(image):
            return f"data:image/png;base64,{image}", field
    return None, ""


def is_drawing_answer_contract(
    answer_contract: dict[str, Any] | None,
    payload: dict[str, Any] | None = None,
) -> bool:
    ac = answer_contract if isinstance(answer_contract, dict) else {}
    ctx = payload if isinstance(payload, dict) else {}
    metadata = ctx.get("metadata") if isinstance(ctx.get("metadata"), dict) else {}
    checker = str(
        ac.get("checker")
        or ac.get("checker_key")
        or ctx.get("checker")
        or ctx.get("checker_type")
        or metadata.get("checker")
        or metadata.get("checker_key")
        or ""
    ).strip()
    equivalence = str(
        ac.get("answer_equivalence")
        or ac.get("equivalence_type")
        or ctx.get("equivalence")
        or ctx.get("equivalence_type")
        or metadata.get("equivalence")
        or metadata.get("equivalence_type")
        or ""
    ).strip()
    answer_type = str(
        ac.get("answer_type")
        or ctx.get("answer_type")
        or metadata.get("answer_type")
        or ""
    ).strip()
    presentation_mode = str(
        ac.get("presentation_mode")
        or ctx.get("presentation_mode")
        or metadata.get("presentation_mode")
        or ""
    ).strip()
    return (
        checker == "free_response_drawing_checker"
        or equivalence == "drawing_equivalence"
        or answer_type in {"drawing", "chart_drawing", "graph_drawing", "canvas_drawing"}
        or presentation_mode in {"canvas", "drawing", "drawing_answer", "canvas_drawing"}
    )


def check_drawing_answer(
    *,
    image_data_url: str | None,
    question_text: str = "",
    answer_contract: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    expected_drawing_spec: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    spec = expected_drawing_spec if isinstance(expected_drawing_spec, dict) else {}
    drawing_type = str(spec.get("drawing_type") or "").strip()
    ctx = context if isinstance(context, dict) else {}
    _log_drawing_check(
        ctx,
        image_field=str(ctx.get("image_field") or ""),
        image_data_url=image_data_url,
        drawing_type=drawing_type,
        expected_spec_present=bool(spec),
        analyzer="drawing_answer_analysis_service.analyze_drawing",
        analysis_status="start",
        is_correct=None,
        score=None,
    )
    if not spec:
        result = _result(
            None,
            0.0,
            1.0,
            "expected_drawing_spec_missing",
            status="missing_spec",
            system_error=True,
        )
        _log_result(ctx, image_data_url, drawing_type, bool(spec), result)
        return result
    if not image_data_url:
        result = _result(
            None,
            0.0,
            1.0,
            "missing_drawing_image",
            status="missing_image",
            system_error=True,
            missing_features=["drawing_image"],
        )
        _log_result(ctx, image_data_url, drawing_type, bool(spec), result)
        return result
    if drawing_type and drawing_type not in SUPPORTED_DRAWING_TYPES:
        result = _result(
            None,
            0.0,
            1.0,
            "unsupported_drawing_type",
            status="unsupported_drawing_type",
            system_error=True,
            incorrect_features=[drawing_type],
        )
        _log_result(ctx, image_data_url, drawing_type, bool(spec), result)
        return result

    from core.services.drawing_answer_analysis_service import analyze_drawing

    try:
        analysis = analyze_drawing(
            image_data_url=image_data_url,
            question_text=question_text,
            answer_contract=answer_contract or {},
            metadata=metadata or {},
            context=ctx,
            expected_drawing_spec=spec,
        )
    except Exception as exc:
        result = _result(
            None,
            0.0,
            0.0,
            f"vision_analysis_failed:{type(exc).__name__}",
            status="analysis_failed",
            system_error=True,
        )
        _log_result(ctx, image_data_url, drawing_type, bool(spec), result)
        return result

    if not isinstance(analysis, dict):
        result = _result(
            None,
            0.0,
            0.0,
            "vision_analysis_failed:invalid_result",
            status="analysis_failed",
            system_error=True,
        )
        _log_result(ctx, image_data_url, drawing_type, bool(spec), result)
        return result

    score = _coerce_score(analysis.get("score"))
    raw_correct = analysis.get("is_correct")
    is_correct = raw_correct if raw_correct is None else bool(raw_correct)
    result = _result(
        is_correct,
        score,
        _coerce_score(analysis.get("confidence"), default=0.5),
        str(analysis.get("feedback") or ("correct" if is_correct else "incorrect")),
        status=str(analysis.get("status") or ("success" if is_correct is not None else "analysis_unavailable")),
        system_error=bool(analysis.get("system_error", False)),
        recognized_features=analysis.get("recognized_features") or analysis.get("elements") or {},
        missing_features=analysis.get("missing_features") or [],
        incorrect_features=analysis.get("incorrect_features") or [],
        analyzer=str(analysis.get("analyzer") or ""),
        raw_analysis_available=bool(analysis.get("raw_analysis_available", False)),
    )
    _log_result(ctx, image_data_url, drawing_type, bool(spec), result)
    return result


def _looks_like_base64_image(value: str) -> bool:
    if len(value) < 32:
        return False
    try:
        base64.b64decode(value, validate=True)
    except Exception:
        return False
    return True


def _coerce_score(value: Any, *, default: float = 0.0) -> float:
    try:
        score = float(value)
    except Exception:
        return default
    return max(0.0, min(1.0, score))


def _result(
    is_correct: bool | None,
    score: float,
    confidence: float,
    feedback: str,
    *,
    status: str = "success",
    system_error: bool = False,
    recognized_features: Any | None = None,
    missing_features: Any | None = None,
    incorrect_features: Any | None = None,
    analyzer: str = "",
    raw_analysis_available: bool = False,
) -> dict[str, Any]:
    return {
        "status": status,
        "is_correct": is_correct if is_correct is None else bool(is_correct),
        "score": _coerce_score(score),
        "confidence": _coerce_score(confidence),
        "feedback": feedback,
        "system_error": bool(system_error),
        "recognized_features": recognized_features if isinstance(recognized_features, dict) else {},
        "missing_features": missing_features if isinstance(missing_features, list) else [],
        "incorrect_features": incorrect_features if isinstance(incorrect_features, list) else [],
        "analyzer": analyzer,
        "raw_analysis_available": bool(raw_analysis_available),
        "checker": "free_response_drawing_checker",
    }


def _image_size(image_data_url: str | None) -> int:
    if not image_data_url:
        return 0
    return len(str(image_data_url).split(",", 1)[-1])


def _log_drawing_check(
    context: dict[str, Any],
    *,
    image_field: str,
    image_data_url: str | None,
    drawing_type: str,
    expected_spec_present: bool,
    analyzer: str,
    analysis_status: str,
    is_correct: bool | None,
    score: float | None,
) -> None:
    logger.info("[DRAWING CHECK] skill_id=%s", context.get("skill_id", ""))
    logger.info("[DRAWING CHECK] component_id=%s", context.get("component_id", ""))
    logger.info("[DRAWING CHECK] problem_type_id=%s", context.get("problem_type_id", ""))
    logger.info("[DRAWING CHECK] checker_key=%s", context.get("checker_key", "free_response_drawing_checker"))
    logger.info("[DRAWING CHECK] image_field=%s", image_field)
    logger.info("[DRAWING CHECK] image_present=%s", bool(image_data_url))
    logger.info("[DRAWING CHECK] image_size=%s", _image_size(image_data_url))
    logger.info("[DRAWING CHECK] drawing_type=%s", drawing_type)
    logger.info("[DRAWING CHECK] expected_spec_present=%s", expected_spec_present)
    logger.info("[DRAWING CHECK] analyzer=%s", analyzer)
    logger.info("[DRAWING CHECK] analysis_status=%s", analysis_status)
    logger.info("[DRAWING CHECK] is_correct=%s", is_correct)
    logger.info("[DRAWING CHECK] score=%s", "" if score is None else score)


def _log_result(
    context: dict[str, Any],
    image_data_url: str | None,
    drawing_type: str,
    expected_spec_present: bool,
    result: dict[str, Any],
) -> None:
    _log_drawing_check(
        context,
        image_field=str(context.get("image_field") or ""),
        image_data_url=image_data_url,
        drawing_type=drawing_type,
        expected_spec_present=expected_spec_present,
        analyzer="drawing_answer_analysis_service.analyze_drawing",
        analysis_status=str(result.get("status") or ""),
        is_correct=result.get("is_correct"),
        score=result.get("score"),
    )
