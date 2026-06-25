from __future__ import annotations

import base64
import json
import logging
import re
import tempfile
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

SUPPORTED_DRAWING_TYPES = frozenset(
    {
        "histogram",
        "frequency_polygon",
        "histogram_and_frequency_polygon",
        "bar_chart",
        "line_chart",
        "coordinate_point_plot",
        "line_graph",
    }
)

DRAWING_ANALYZER_REGISTRY: dict[str, str] = {
    key: "vision_json_analyzer" for key in SUPPORTED_DRAWING_TYPES
}

DRAWING_EVALUATOR_REGISTRY: dict[str, Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]] = {}

HISTOGRAM_POLYGON_EVALUATION_THRESHOLDS = {
    "value_tolerance_default": 0.8,
    "confidence_min": 0.60,
    "correct_score_min": 0.80,
    "wrong_score_max": 0.60,
    "missing_penalty": 0.18,
    "incorrect_penalty": 0.14,
}


def analyze_drawing(
    *,
    image_data_url: str,
    question_text: str,
    expected_drawing_spec: dict[str, Any],
    context: dict[str, Any] | None = None,
    answer_contract: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ctx = context if isinstance(context, dict) else {}
    spec = expected_drawing_spec if isinstance(expected_drawing_spec, dict) else {}
    drawing_type = str(spec.get("drawing_type") or "").strip()

    if not image_data_url:
        return _result("missing_image", None, feedback="missing_drawing_image", system_error=True)
    if not spec:
        return _result("missing_spec", None, feedback="本題圖形批改設定尚未完成，這次不計入答錯。", system_error=True)
    if drawing_type not in SUPPORTED_DRAWING_TYPES:
        return _result(
            "unsupported_drawing_type",
            None,
            feedback=f"unsupported_drawing_type:{drawing_type}",
            system_error=True,
            incorrect_features=[drawing_type] if drawing_type else [],
        )

    image_bytes = _decode_image_data_url(image_data_url)
    if not image_bytes:
        return _result("invalid_image", None, feedback="invalid_image", system_error=True)
    strokes_data_url = str(ctx.get("student_strokes_image_data_url") or "").strip()
    strokes_bytes = _decode_image_data_url(strokes_data_url) if strokes_data_url else None
    bg_data_url = str(ctx.get("background_image_data_url") or "").strip()
    bg_bytes = _decode_image_data_url(bg_data_url) if bg_data_url else None

    # Calculate hashes and dimensions for image trace diagnostic
    import hashlib
    def get_hash(b: bytes | None) -> str:
        return hashlib.sha256(b).hexdigest() if b else "none"

    def get_dimensions_and_nontransparent(b: bytes | None) -> tuple[int, int, int]:
        if not b:
            return 0, 0, 0
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(b)).convert("RGBA")
            pixels = img.getdata()
            nontransparent = sum(1 for p in pixels if p[3] > 0)
            return img.size[0], img.size[1], nontransparent
        except Exception:
            return 0, 0, 0

    bg_w, bg_h, bg_pixels = get_dimensions_and_nontransparent(bg_bytes)
    st_w, st_h, st_pixels = get_dimensions_and_nontransparent(strokes_bytes)
    cp_w, cp_h, _ = get_dimensions_and_nontransparent(image_bytes)

    bg_hash = get_hash(bg_bytes)
    st_hash = get_hash(strokes_bytes)
    cp_hash = get_hash(image_bytes)

    composite_equals_strokes = (cp_hash == st_hash) and (st_hash != "none")
    composite_equals_background = (cp_hash == bg_hash) and (bg_hash != "none")

    logger.info(
        "[DRAWING IMAGE TRACE] "
        "background_found=%s background_width=%d background_height=%d background_nontransparent_pixels=%d "
        "strokes_found=%s strokes_width=%d strokes_height=%d strokes_nontransparent_pixels=%d "
        "composite_width=%d composite_height=%d "
        "background_hash=%s strokes_hash=%s composite_hash=%s "
        "composite_equals_strokes=%s composite_equals_background=%s",
        bool(bg_bytes), bg_w, bg_h, bg_pixels,
        bool(strokes_bytes), st_w, st_h, st_pixels,
        cp_w, cp_h,
        bg_hash, st_hash, cp_hash,
        str(composite_equals_strokes), str(composite_equals_background)
    )

    if composite_equals_strokes:
        logger.warning("[DRAWING IMAGE] drawing_image_composition_error (strokes equals composite)")

    blank_source = "student_strokes_image_data_url" if strokes_bytes else "image_data_url"
    blank_bytes = strokes_bytes or image_bytes
    if _is_blank_png(blank_bytes):
        return _result("blank_drawing", False, feedback="請先在畫布作答。", missing_features=["drawing"])

    analyzer_status = _resolve_analyzer_role()
    if not analyzer_status.get("available"):
        return _result(
            "analysis_unavailable",
            None,
            feedback="圖形分析目前無法完成，這不是作答錯誤。",
            system_error=True,
            analyzer=str(analyzer_status.get("analyzer", "")),
        )

    prompt = build_drawing_analysis_prompt(
        question_text=question_text,
        expected_drawing_spec=spec,
        context={**ctx, "metadata": metadata or {}, "answer_contract": answer_contract or {}},
    )
    try:
        raw_text = _call_vision_analyzer(prompt, image_bytes, analyzer_status)
    except TimeoutError:
        return _result("analysis_timeout", None, feedback="vision_analysis_timeout", system_error=True)
    except Exception as exc:
        logger.warning("[DRAWING ANALYZER] analysis_failed=%s", type(exc).__name__)
        return _result("analysis_failed", None, feedback=f"vision_analysis_failed:{type(exc).__name__}", system_error=True)

    parsed = parse_analyzer_json(raw_text)
    if parsed is None:
        return _result("invalid_analyzer_response", None, feedback="invalid_analyzer_response", system_error=True)
    ok, normalized_or_errors = validate_analyzer_response(parsed, drawing_type=drawing_type)
    if not ok:
        return _result(
            "invalid_analyzer_response",
            None,
            feedback="invalid_analyzer_response",
            system_error=True,
            incorrect_features=normalized_or_errors if isinstance(normalized_or_errors, list) else [],
        )

    recognized = normalized_or_errors
    evaluator = DRAWING_EVALUATOR_REGISTRY.get(drawing_type)
    if evaluator is None:
        return _result("unsupported_drawing_type", None, feedback=f"unsupported_drawing_type:{drawing_type}", system_error=True)
    evaluation = evaluator(recognized, spec)
    status = str(evaluation.get("status") or "success")
    return _result(
        status,
        evaluation.get("is_correct"),
        score=evaluation.get("score", 0.0),
        confidence=evaluation.get("confidence", recognized.get("confidence", 0.0)),
        recognized_features=recognized,
        missing_features=evaluation.get("missing_features", recognized.get("missing_features", [])),
        incorrect_features=evaluation.get("incorrect_features", recognized.get("incorrect_features", [])),
        feedback=str(evaluation.get("feedback") or recognized.get("feedback") or ""),
        analyzer=str(analyzer_status.get("analyzer", "")),
        raw_analysis_available=True,
    )


def analyze_drawing_answer(**kwargs: Any) -> dict[str, Any]:
    return analyze_drawing(**kwargs)


def build_drawing_analysis_prompt(
    *,
    question_text: str,
    expected_drawing_spec: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> str:
    drawing_type = str(expected_drawing_spec.get("drawing_type") or "").strip()
    schema = {
        "drawing_detected": True,
        "recognized_type": drawing_type,
        "required_elements": {
            "x_axis": True,
            "y_axis": True,
            "histogram_bars": True,
            "frequency_polygon": True,
        },
        "histogram": {
            "detected": True,
            "bar_count": 0,
            "estimated_values": [],
            "category_order_correct": True,
            "baseline_correct": True,
        },
        "frequency_polygon": {
            "detected": True,
            "point_count": 0,
            "estimated_values": [],
            "connected_in_order": True,
            "points_near_category_centers": True,
        },
        "missing_features": [],
        "incorrect_features": [],
        "score": 0.0,
        "confidence": 0.0,
        "is_correct": None,
        "feedback": "",
    }
    return (
        "You are a strict math drawing analyzer. Analyze the submitted image as a student drawing, "
        "not as handwriting OCR. Do not transcribe expressions. Extract visible chart/graph features "
        "against the expected drawing spec, then return JSON only. Do not decide final correctness; "
        "the local deterministic evaluator will decide from your extracted features.\n\n"
        "Analysis rules:\n"
        "- Analyze only dark student strokes. Ignore pale grid lines, axes, labels, text, and any background template.\n"
        "- Rectangle left/right boundaries are not a frequency polygon.\n"
        "- A frequency polygon connects the frequency points above category centers, in category order.\n"
        "- Estimate histogram bar heights from the y-axis scale.\n"
        "- Do not require perfectly closed shapes.\n"
        "- Ignore small stroke wobble, thick strokes, and minor horizontal offset when the mathematical values are clear.\n"
        "- Do not lower mathematical correctness because the drawing is unattractive.\n"
        "- If a value or feature cannot be estimated reliably, lower confidence instead of guessing.\n\n"
        f"Question:\n{question_text}\n\n"
        f"Drawing type: {drawing_type}\n\n"
        "Expected drawing spec:\n"
        f"{json.dumps(expected_drawing_spec, ensure_ascii=False, indent=2)}\n\n"
        "Context:\n"
        f"{json.dumps(context or {}, ensure_ascii=False, indent=2)}\n\n"
        "Return exactly this JSON shape, with numeric estimated_values where applicable:\n"
        f"{json.dumps(schema, ensure_ascii=False, indent=2)}"
    )


def parse_analyzer_json(raw_text: Any) -> dict[str, Any] | None:
    text = str(getattr(raw_text, "text", raw_text) or "").strip()
    if not text:
        return None
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S | re.I)
    if fence:
        text = fence.group(1).strip()
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
    try:
        parsed = json.loads(text)
    except Exception:
        return None
    return parsed if isinstance(parsed, dict) else None


def validate_analyzer_response(value: dict[str, Any], *, drawing_type: str) -> tuple[bool, dict[str, Any] | list[str]]:
    errors: list[str] = []
    out = dict(value)
    recognized_type = str(out.get("recognized_type") or "").strip()
    if recognized_type and recognized_type not in SUPPORTED_DRAWING_TYPES:
        errors.append("recognized_type_unsupported")
    if recognized_type and recognized_type != drawing_type:
        errors.append("recognized_type_mismatch")
    for key in ("score", "confidence"):
        try:
            out[key] = _clamp01(float(out.get(key, 0.0)))
        except Exception:
            errors.append(f"{key}_invalid")
    if out.get("is_correct") is not None and not isinstance(out.get("is_correct"), bool):
        errors.append("is_correct_invalid")
    for key in ("missing_features", "incorrect_features"):
        if not isinstance(out.get(key), list):
            errors.append(f"{key}_invalid")
            out[key] = []
    for section_key in ("histogram", "frequency_polygon"):
        section = out.get(section_key)
        if isinstance(section, dict) and "estimated_values" in section:
            vals = section.get("estimated_values")
            if not isinstance(vals, list):
                errors.append(f"{section_key}_estimated_values_invalid")
            else:
                normalized_vals = []
                for item in vals:
                    try:
                        normalized_vals.append(float(item))
                    except Exception:
                        errors.append(f"{section_key}_estimated_value_invalid")
                section["estimated_values"] = normalized_vals
    return (False, errors) if errors else (True, out)


def evaluate_histogram_and_frequency_polygon(
    recognized_features: dict[str, Any],
    expected_drawing_spec: dict[str, Any],
) -> dict[str, Any]:
    expected = [float(x) for x in expected_drawing_spec.get("expected_values", [])]
    tolerance = expected_drawing_spec.get("tolerance") if isinstance(expected_drawing_spec.get("tolerance"), dict) else {}
    thresholds = HISTOGRAM_POLYGON_EVALUATION_THRESHOLDS
    value_tol = float(tolerance.get("value", thresholds["value_tolerance_default"]))
    missing: list[str] = []
    incorrect: list[str] = []

    required = recognized_features.get("required_elements") if isinstance(recognized_features.get("required_elements"), dict) else {}
    for element in expected_drawing_spec.get("required_elements", []):
        if not bool(required.get(element)):
            missing.append(str(element))

    hist = recognized_features.get("histogram") if isinstance(recognized_features.get("histogram"), dict) else {}
    poly = recognized_features.get("frequency_polygon") if isinstance(recognized_features.get("frequency_polygon"), dict) else {}

    if not hist.get("detected"):
        missing.append("histogram")
    if not poly.get("detected"):
        missing.append("frequency_polygon")

    expected_count = len(expected)
    if hist.get("bar_count") is not None and int(hist.get("bar_count") or 0) != expected_count:
        incorrect.append("bar_count")
    if poly.get("point_count") is not None and int(poly.get("point_count") or 0) != expected_count:
        incorrect.append("point_count")
    if hist and not hist.get("category_order_correct", True):
        incorrect.append("category_order")
    if hist and not hist.get("baseline_correct", True):
        incorrect.append("baseline")
    if poly and not poly.get("connected_in_order", True):
        incorrect.append("polygon_connection_order")
    if poly and not poly.get("points_near_category_centers", True):
        incorrect.append("polygon_point_positions")

    hist_values = hist.get("estimated_values") if isinstance(hist.get("estimated_values"), list) else []
    poly_values = poly.get("estimated_values") if isinstance(poly.get("estimated_values"), list) else []
    if expected:
        if hist_values and not _values_within_tolerance(hist_values, expected, value_tol):
            incorrect.append("histogram_values")
        if poly_values and not _values_within_tolerance(poly_values, expected, value_tol):
            incorrect.append("polygon_values")
        if not hist_values and hist.get("detected"):
            incorrect.append("histogram_values_missing")
        if not poly_values and poly.get("detected"):
            incorrect.append("polygon_values_missing")

    confidence = _clamp01(float(recognized_features.get("confidence", 0.0) or 0.0))
    element_score = 1.0 - min(
        1.0,
        len(set(missing)) * thresholds["missing_penalty"]
        + len(set(incorrect)) * thresholds["incorrect_penalty"],
    )
    model_score = _clamp01(float(recognized_features.get("score", element_score) or element_score))
    score = round(min(model_score, element_score), 3)

    if confidence < thresholds["confidence_min"]:
        is_correct: bool | None = None
        status = "low_confidence"
    elif score >= thresholds["correct_score_min"] and not missing and not incorrect:
        is_correct = True
        status = "success"
    elif score < thresholds["wrong_score_max"] or missing or incorrect:
        is_correct = False
        status = "success"
    else:
        is_correct = None
        status = "low_confidence"

    feedback = _build_feedback(is_correct, missing, incorrect)
    return {
        "status": status,
        "is_correct": is_correct,
        "score": score,
        "confidence": confidence,
        "missing_features": sorted(set(missing)),
        "incorrect_features": sorted(set(incorrect)),
        "feedback": feedback,
    }


def evaluate_histogram(recognized_features: dict[str, Any], expected_drawing_spec: dict[str, Any]) -> dict[str, Any]:
    adapted = dict(recognized_features)
    req = dict(adapted.get("required_elements") or {})
    req.setdefault("frequency_polygon", True)
    adapted["required_elements"] = req
    adapted.setdefault("frequency_polygon", {"detected": True, "point_count": len(expected_drawing_spec.get("expected_values", [])), "estimated_values": expected_drawing_spec.get("expected_values", []), "connected_in_order": True, "points_near_category_centers": True})
    return evaluate_histogram_and_frequency_polygon(adapted, expected_drawing_spec)


def evaluate_frequency_polygon(recognized_features: dict[str, Any], expected_drawing_spec: dict[str, Any]) -> dict[str, Any]:
    adapted = dict(recognized_features)
    req = dict(adapted.get("required_elements") or {})
    req.setdefault("histogram_bars", True)
    adapted["required_elements"] = req
    adapted.setdefault("histogram", {"detected": True, "bar_count": len(expected_drawing_spec.get("expected_values", [])), "estimated_values": expected_drawing_spec.get("expected_values", []), "category_order_correct": True, "baseline_correct": True})
    return evaluate_histogram_and_frequency_polygon(adapted, expected_drawing_spec)


def evaluate_not_implemented(recognized_features: dict[str, Any], expected_drawing_spec: dict[str, Any]) -> dict[str, Any]:
    _ = recognized_features
    _ = expected_drawing_spec
    return _result("analysis_unavailable", None, feedback="drawing_evaluator_not_implemented", system_error=True)


DRAWING_EVALUATOR_REGISTRY.update(
    {
        "histogram": evaluate_histogram,
        "frequency_polygon": evaluate_frequency_polygon,
        "histogram_and_frequency_polygon": evaluate_histogram_and_frequency_polygon,
        "bar_chart": evaluate_not_implemented,
        "line_chart": evaluate_not_implemented,
        "coordinate_point_plot": evaluate_not_implemented,
        "line_graph": evaluate_not_implemented,
    }
)


def _resolve_analyzer_role() -> dict[str, Any]:
    requested_role = "drawing_analyzer"
    resolved_role = "vision_analyzer"
    try:
        from core.ai_settings import get_effective_model_config
        from core.ai_wrapper import resolve_gemini_api_key

        cfg = get_effective_model_config(resolved_role)
        provider = str(cfg.get("provider", "")).strip().lower()
        model = str(cfg.get("model", "")).strip()
        api_key, key_source = resolve_gemini_api_key()
        logger.info(
            "[AI CONFIG RESOLVE] requested_role=%s resolved_role=%s provider=%s model=%s api_key_source=%s",
            requested_role,
            resolved_role,
            provider,
            model,
            key_source or "",
        )
        if provider in {"google", "gemini"} and not api_key:
            return {"available": False, "analyzer": f"{resolved_role}:{provider}:{model}", "reason": "missing_api_key"}
        return {"available": True, "analyzer": f"{resolved_role}:{provider}:{model}", "role": resolved_role}
    except Exception as exc:
        logger.warning("[DRAWING ANALYZER] role_resolution_failed=%s", type(exc).__name__)
        return {"available": False, "analyzer": resolved_role, "reason": type(exc).__name__}


def _call_vision_analyzer(prompt: str, image_bytes: bytes, analyzer_status: dict[str, Any]) -> str:
    from core.ai_wrapper import call_ai_with_retry, get_ai_client

    suffix = ".png"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = Path(tmp.name)
    try:
        client = get_ai_client(str(analyzer_status.get("role") or "vision_analyzer"))
        response = call_ai_with_retry(client, prompt, image_path=str(tmp_path), max_retries=1, retry_delay=0, timeout=90)
        return str(getattr(response, "text", response) or "")
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


def _decode_image_data_url(image_data_url: str) -> bytes | None:
    text = str(image_data_url or "").strip()
    if not text:
        return None
    if "," in text and text.lower().startswith("data:image/"):
        text = text.split(",", 1)[1]
    try:
        return base64.b64decode(text, validate=True)
    except Exception:
        return None


def _is_blank_png(image_bytes: bytes) -> bool:
    try:
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        alpha_bbox = img.getchannel("A").getbbox()
        if alpha_bbox is None:
            return True
        rgb = img.convert("RGB")
        colors = rgb.getcolors(maxcolors=256)
        if colors and len(colors) == 1 and colors[0][1] == (255, 255, 255):
            return True
        dark_pixels = 0
        for r, g, b in rgb.getdata():
            if r <= 95 and g <= 95 and b <= 95:
                dark_pixels += 1
                if dark_pixels >= 30:
                    return False
        return True
    except Exception:
        return False


def _values_within_tolerance(values: list[Any], expected: list[float], tolerance: float) -> bool:
    if len(values) != len(expected):
        return False
    for got, exp in zip(values, expected):
        try:
            if abs(float(got) - float(exp)) > tolerance:
                return False
        except Exception:
            return False
    return True


DRAWING_FEATURE_LABELS = {
    "frequency_polygon": "折線圖",
    "histogram": "直方圖",
    "histogram_bars": "直方圖",
    "x_axis": "橫軸",
    "y_axis": "縱軸",
    "category_labels": "組別標籤",
    "data_points": "資料點",
}


def translate_drawing_features(features: list[str]) -> list[str]:
    translated = []
    for f in features:
        label = DRAWING_FEATURE_LABELS.get(f)
        if label:
            translated.append(label)
        else:
            translated.append(f)
    seen = set()
    deduped = []
    for t in translated:
        if t not in seen:
            seen.add(t)
            deduped.append(t)
    return deduped


def _build_feedback(is_correct: bool | None, missing: list[str], incorrect: list[str]) -> str:
    if is_correct is True:
        return "圖形作答正確，直方圖與折線圖的主要元素和數值都符合題目。"
    if is_correct is None:
        return "圖形分析信心不足，這不是作答錯誤。"
    
    translated_missing = translate_drawing_features(missing)
    translated_incorrect = translate_drawing_features(incorrect)
    
    if translated_missing:
        return "圖形缺少必要元素：" + "、".join(translated_missing)
    if translated_incorrect:
        return "圖形有不符合題目資料的部分：" + "、".join(translated_incorrect)
    return "圖形與題目資料不一致。"


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _result(
    status: str,
    is_correct: bool | None,
    *,
    score: Any = 0.0,
    confidence: Any = 0.0,
    recognized_features: dict[str, Any] | None = None,
    missing_features: list[Any] | None = None,
    incorrect_features: list[Any] | None = None,
    feedback: str = "",
    system_error: bool = False,
    analyzer: str = "",
    raw_analysis_available: bool = False,
) -> dict[str, Any]:
    return {
        "status": status,
        "is_correct": is_correct,
        "score": _clamp01(float(score or 0.0)),
        "confidence": _clamp01(float(confidence or 0.0)),
        "recognized_features": recognized_features or {},
        "missing_features": missing_features or [],
        "incorrect_features": incorrect_features or [],
        "feedback": feedback,
        "system_error": bool(system_error),
        "analyzer": analyzer,
        "raw_analysis_available": bool(raw_analysis_available),
    }
