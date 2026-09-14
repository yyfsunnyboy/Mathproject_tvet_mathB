from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Callable

LOW_CONFIDENCE_THRESHOLD = 0.70

HANDWRITING_MODES = {
    "final_answer_only",
    "solution_with_steps",
    "process_only",
    "unrecognized",
}


@dataclass(frozen=True)
class HandwritingCheckContext:
    question_uid: str = ""
    skill_id: str = ""
    question_text: str = ""
    problem_type_id: str = ""
    presentation_mode: str = ""
    answer_type: str = ""
    correct_answer: Any = None
    semantic_answer: Any = None
    answer_contract: dict[str, Any] | None = None
    checker: str = ""
    equivalence: str = ""
    choices: list[Any] | None = None
    rubric: str = ""


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _to_bool_or_none(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _clean_text(value).lower()
    if text in {"true", "1", "yes", "y", "correct"}:
        return True
    if text in {"false", "0", "no", "n", "incorrect"}:
        return False
    return None


BLANK_CANVAS_FEEDBACK = "請先在白板作答。"


def _decode_image_bytes(image_base64: str) -> bytes | None:
    text = _clean_text(image_base64)
    if not text:
        return None
    if "," in text and text.lower().startswith("data:image/"):
        text = text.split(",", 1)[1]
    try:
        import base64

        return base64.b64decode(text, validate=False)
    except Exception:
        return None


def _png_bytes_look_blank(image_bytes: bytes) -> bool:
    """Pixel-level blank check for captured handwriting images."""
    try:
        import io

        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        alpha_bbox = img.getchannel("A").getbbox()
        # Fully transparent canvas with no ink.
        if alpha_bbox is None:
            return True
        rgb = img.convert("RGB")
        dark_pixels = 0
        opaque_pixels = 0
        for r, g, b, a in img.getdata():
            if a < 8:
                continue
            opaque_pixels += 1
            if r <= 95 and g <= 95 and b <= 95:
                dark_pixels += 1
                if dark_pixels >= 12:
                    return False
            elif min(r, g, b) <= 210 and max(r, g, b) - min(r, g, b) >= 20:
                # Non-gray / colored ink also counts as strokes.
                dark_pixels += 1
                if dark_pixels >= 12:
                    return False
        if opaque_pixels == 0:
            return True
        colors = rgb.getcolors(maxcolors=256)
        if colors and len(colors) == 1 and colors[0][1] == (255, 255, 255):
            return True
        return dark_pixels < 12
    except Exception:
        # If decoding fails, do not pretend the canvas is blank.
        return False


def _looks_blank_image(image_base64: str) -> bool:
    text = _clean_text(image_base64)
    if not text:
        return True
    # Test-friendly sentinels; real canvas blank checks are also done in frontend.
    lowered = text.lower()
    if lowered in {"blank", "empty", "data:image/png;base64,"}:
        return True
    image_bytes = _decode_image_bytes(text)
    if image_bytes is None:
        # Non-decodable placeholders (unit-test ink markers) are not blank canvases.
        return False
    try:
        import io

        from PIL import Image

        Image.open(io.BytesIO(image_bytes)).load()
    except Exception:
        # Corrupt/non-image payloads should not short-circuit as blank canvas.
        return False
    return _png_bytes_look_blank(image_bytes)


def _answer_is_structurally_complete(answer: Any) -> bool:
    if isinstance(answer, dict):
        return bool(answer) and all(_answer_is_structurally_complete(v) for v in answer.values())
    if isinstance(answer, list):
        return bool(answer) and all(_answer_is_structurally_complete(v) for v in answer)
    text = _clean_text(answer)
    if not text:
        return False
    text = re.sub(r"(?:\\\)|\\\]|\$)+$", "", text).strip()
    # An answer ending at an operator/relation (for example ``x=``) is work in
    # progress. A compact answer such as ``x=±11`` is complete.
    if re.search(r"(?:=|≤|≥|<|>|\+|-|±|×|÷|\*|/|\^|,|;|:)\s*$", text):
        return False
    if re.search(r"(?:\bor\b|\band\b|或|且)\s*$", text, flags=re.IGNORECASE):
        return False
    # A numeric left boundary followed by a relation and a bare variable is an
    # unfinished chained inequality. Complete equations and bounded chains are
    # unaffected by this general mathematical-shape rule.
    if re.fullmatch(r"[+-]?(?:\d+(?:\.\d+)?|\d+/\d+)\s*(?:≤|≥|<|>)\s*[A-Za-z]", text):
        return False
    return True


def handwriting_completion_state(normalized: dict[str, Any]) -> str:
    answer = normalized.get("normalized_answer")
    steps = normalized.get("recognized_steps") or []
    mode = str(normalized.get("mode") or "").strip().lower()
    if not _clean_text(answer) and not steps:
        return "blank"
    if mode == "process_only" or not _answer_is_structurally_complete(answer):
        return "in_progress"
    return "completed"


def normalize_ai_handwriting_result(raw: dict[str, Any] | None) -> dict[str, Any]:
    data = raw if isinstance(raw, dict) else {}
    steps = data.get("recognized_steps")
    if not isinstance(steps, list):
        steps = data.get("steps") if isinstance(data.get("steps"), list) else []
    steps = [_clean_text(step) for step in steps if _clean_text(step)]

    mode = _clean_text(data.get("mode")).lower()
    raw_recognized_answer = (
        data.get("recognized_answer")
        if data.get("recognized_answer") not in (None, "")
        else data.get("recognized_expression")
        or data.get("answer")
        or data.get("final_answer")
        or data.get("recognized_text")
        or data.get("expression")
        or data.get("normalized_answer")
        or data.get("recognized_latex")
        or data.get("latex")
    )
    recognized_answer = (
        raw_recognized_answer
        if isinstance(raw_recognized_answer, (dict, list))
        else _clean_text(raw_recognized_answer)
    )
    if mode not in HANDWRITING_MODES:
        has_process = bool(steps) or bool(data.get("has_process") or data.get("contains_steps"))
        has_final = bool(recognized_answer) or bool(data.get("has_final_answer"))
        if has_process and has_final:
            mode = "solution_with_steps"
        elif has_process:
            mode = "process_only"
        elif has_final:
            mode = "final_answer_only"
        else:
            mode = "unrecognized"

    confidence = _to_float(data.get("confidence"), 0.0)
    first_error_step = data.get("first_error_step")
    try:
        first_error_step = int(first_error_step) if first_error_step is not None else None
    except Exception:
        first_error_step = None

    return {
        "mode": mode,
        "recognized_answer": recognized_answer,
        "normalized_answer": recognized_answer,
        "recognized_latex": _clean_text(data.get("recognized_latex") or data.get("latex")),
        "recognized_steps": steps,
        "first_error_step": first_error_step,
        "error_type": _clean_text(data.get("error_type")) or None,
        "process_correct": _to_bool_or_none(data.get("process_correct", data.get("is_process_correct"))),
        "final_answer_correct": _to_bool_or_none(data.get("final_answer_correct")),
        "feedback": _clean_text(data.get("feedback") or data.get("reply")),
        "confidence": confidence,
    }


def _multi_part_keys(ctx: HandwritingCheckContext) -> list[str]:
    contract = ctx.answer_contract if isinstance(ctx.answer_contract, dict) else {}
    parts = contract.get("parts")
    keys: list[str] = []
    if isinstance(parts, list):
        for part in parts:
            if isinstance(part, dict):
                key = _clean_text(part.get("key") or part.get("id") or part.get("name"))
                if key and key not in keys:
                    keys.append(key)
    expected = ctx.correct_answer if ctx.correct_answer not in (None, "") else ctx.semantic_answer
    if not keys and isinstance(expected, dict):
        keys = [_clean_text(key) for key in expected.keys() if _clean_text(key)]
    return keys


def normalize_multi_part_handwriting_answer(value: Any, ctx: HandwritingCheckContext) -> Any:
    """Map a fresh numbered transcription onto the current contract's part keys."""
    keys = _multi_part_keys(ctx)
    contract = ctx.answer_contract if isinstance(ctx.answer_contract, dict) else {}
    is_multi_part = (
        _clean_text(ctx.answer_type).lower() == "multi_part"
        or _clean_text(contract.get("answer_type")).lower() == "multi_part"
        or bool(keys)
    )
    if not is_multi_part or not keys:
        return value

    mapped: dict[str, Any] = {key: "" for key in keys}
    if isinstance(value, dict):
        for index, key in enumerate(keys, start=1):
            for candidate in (key, str(index), f"part_{index}", f"part{index}"):
                if candidate in value:
                    mapped[key] = value[candidate]
                    break
        return mapped
    if isinstance(value, (list, tuple)):
        for index, key in enumerate(keys):
            if index < len(value):
                mapped[key] = value[index]
        return mapped

    text = _clean_text(value)
    if not text:
        return mapped
    marker = re.compile(
        r"(?:^|[\s;；])(?:\(\s*(\d+)\s*\)|part[_\s-]*(\d+)|(\d+)[.、:：)])\s*",
        flags=re.IGNORECASE,
    )
    matches = list(marker.finditer(text))
    if not matches:
        return value
    for pos, match in enumerate(matches):
        number_text = next((group for group in match.groups() if group), "")
        try:
            part_index = int(number_text) - 1
        except (TypeError, ValueError):
            continue
        if not 0 <= part_index < len(keys):
            continue
        end = matches[pos + 1].start() if pos + 1 < len(matches) else len(text)
        segment = text[match.end():end].strip(" \t\r\n;；,")
        mapped[keys[part_index]] = segment
    return mapped


def _checker_payload(ctx: HandwritingCheckContext) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "skill_id": ctx.skill_id,
        "problem_type_id": ctx.problem_type_id,
        "presentation_mode": ctx.presentation_mode,
        "answer_type": ctx.answer_type,
        "checker": ctx.checker,
        "equivalence": ctx.equivalence,
        "choices": list(ctx.choices or []),
        "question_text": ctx.question_text,
    }
    if isinstance(ctx.answer_contract, dict):
        payload["answer_contract"] = dict(ctx.answer_contract)
    return payload


def deterministic_final_answer_check(
    recognized_answer: Any,
    ctx: HandwritingCheckContext,
    checker: Callable[..., bool] | None = None,
) -> bool | None:
    expected = ctx.correct_answer if ctx.correct_answer not in (None, "") else ctx.semantic_answer
    if expected in (None, "") or not _clean_text(recognized_answer):
        return None
    if checker is None:
        from core.gencode.runtime_skill_wrapper import check_answer as checker

    return bool(
        checker(
            recognized_answer,
            expected,
            payload=_checker_payload(ctx),
            answer_contract=ctx.answer_contract if isinstance(ctx.answer_contract, dict) else None,
            skill_id=ctx.skill_id,
        )
    )


def build_handwriting_check_response(
    *,
    image_base64: str,
    ctx: HandwritingCheckContext,
    ai_result: dict[str, Any] | None,
    checker: Callable[..., bool] | None = None,
) -> dict[str, Any]:
    if _looks_blank_image(image_base64):
        return {
            "completion_state": "blank",
            "mode": "unrecognized",
            "is_correct": False,
            "final_answer_correct": None,
            "process_correct": None,
            "recognized_answer": "",
            "normalized_answer": "",
            "recognized_latex": "",
            "recognized_steps": [],
            "first_error_step": None,
            "error_type": "blank",
            "feedback": BLANK_CANVAS_FEEDBACK,
            "confidence": 0.0,
            "should_record_attempt": False,
            "is_blank": True,
            "vision_invoked": False,
        }

    normalized = normalize_ai_handwriting_result(ai_result)
    normalized["normalized_answer"] = normalize_multi_part_handwriting_answer(
        normalized.get("recognized_answer"), ctx
    )
    if isinstance(ai_result, dict) and ai_result.get("recognition_uncertain") is True:
        return {
            **normalized,
            "mode": "unrecognized",
            "completion_state": "recognition_uncertain",
            "is_correct": False,
            "final_answer_correct": None,
            "process_correct": None,
            "error_type": "recognition_uncertain",
            "feedback": normalized["feedback"] or "辨識結果不一致，請確認或重寫。",
            "should_record_attempt": False,
            "is_blank": False,
            "vision_invoked": True,
        }
    mode = normalized["mode"]
    confidence = float(normalized["confidence"])
    completion_state = handwriting_completion_state(normalized)
    if completion_state == "blank":
        # Image itself has strokes; empty recognition must not be treated as blank canvas.
        return {
            **normalized,
            "mode": "unrecognized",
            "completion_state": "in_progress",
            "is_correct": False,
            "final_answer_correct": None,
            "process_correct": None,
            "feedback": normalized["feedback"] or "目前無法清楚辨識，請重新書寫。",
            "should_record_attempt": False,
            "is_blank": False,
            "vision_invoked": True,
        }

    process_correct = normalized["process_correct"]
    if completion_state == "in_progress" or confidence < LOW_CONFIDENCE_THRESHOLD:
        feedback = normalized["feedback"]
        if process_correct is True:
            feedback = feedback or "目前過程到這裡是正確的，但尚未寫出最後答案。"
        return {
            **normalized,
            "completion_state": "in_progress",
            "is_correct": False,
            "final_answer_correct": None,
            "process_correct": process_correct,
            "feedback": feedback or "目前還在作答中；下一步可以先確認等號右邊應寫什麼嗎？",
            "should_record_attempt": False,
            "is_blank": False,
            "vision_invoked": True,
        }

    final_correct = deterministic_final_answer_check(
        normalized["normalized_answer"], ctx, checker=checker
    )
    if final_correct is None:
        return {
            **normalized,
            "completion_state": "completed",
            "is_correct": False,
            "final_answer_correct": None,
            "feedback": normalized["feedback"] or "AI 助教已提供辨識結果，請使用正式提交完成批改。",
            "should_record_attempt": False,
            "is_blank": False,
            "vision_invoked": True,
        }
    if mode == "final_answer_only":
        feedback = "答對了。" if final_correct is True else normalized["feedback"] or "答錯了，請重新檢查。"
        return {
            **normalized,
            "completion_state": "completed",
            "is_correct": bool(final_correct),
            "final_answer_correct": final_correct,
            "process_correct": None,
            "feedback": feedback,
            "should_record_attempt": final_correct is not None,
            "is_blank": False,
            "vision_invoked": True,
        }

    if mode == "solution_with_steps":
        if process_correct is None:
            process_correct = bool(normalized["first_error_step"] is None)
        is_correct = final_correct is True
        feedback = normalized["feedback"]
        if process_correct is True and final_correct is False:
            feedback = feedback or "方法正確，但最後一步計算有誤。"
        elif is_correct:
            feedback = "答對了。"
        return {
            **normalized,
            "completion_state": "completed",
            "is_correct": is_correct,
            "final_answer_correct": final_correct,
            "process_correct": process_correct,
            "feedback": feedback or "請檢查你的推導過程。",
            "should_record_attempt": final_correct is not None,
            "is_blank": False,
            "vision_invoked": True,
        }

    return {
        **normalized,
        "mode": "unrecognized",
        "completion_state": "in_progress",
        "is_correct": False,
        "final_answer_correct": None,
        "process_correct": None,
        "feedback": "目前無法清楚辨識，請重新書寫。",
        "should_record_attempt": False,
        "is_blank": False,
        "vision_invoked": True,
    }
