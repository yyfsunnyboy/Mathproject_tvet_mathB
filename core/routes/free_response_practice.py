# -*- coding: utf-8 -*-
"""Isolated free-response practice routes for B4 tree diagram prototypes."""

from __future__ import annotations

from flask import current_app, jsonify, render_template, request
from flask_login import current_user, login_required

from core.vocational_math_b4.free_response.tree_diagram_judge import (
    build_tree_diagram_listing_payload,
    judge_tree_diagram_text_answer,
)

from . import practice_bp


DEFAULT_TREE_DIAGRAM_VARIANT = "early_stopping_game"
TREE_DIAGRAM_PROBLEM_TYPE = "tree_diagram_listing"


def _public_question_payload(payload: dict) -> dict:
    return {
        "problem_type_id": payload.get("problem_type_id"),
        "grading_mode": payload.get("grading_mode"),
        "variant": payload.get("variant"),
        "question_text": payload.get("question_text"),
        "expected_count": payload.get("expected_count"),
        "accept_text_listing": payload.get("accept_text_listing"),
        "accept_handwriting_tree": payload.get("accept_handwriting_tree"),
        "requires_listing_or_tree": payload.get("requires_listing_or_tree"),
    }


def _public_judge_result(result: dict) -> dict:
    return {
        "status": result.get("status"),
        "score": result.get("score"),
        "expected_count": result.get("expected_count"),
        "detected_count": result.get("detected_count"),
        "detected_paths": result.get("detected_paths", []),
        "missing_paths": result.get("missing_paths", []),
        "extra_paths": result.get("extra_paths", []),
        "duplicated_paths": result.get("duplicated_paths", []),
        "count_only_answer": result.get("count_only_answer", False),
        "main_issue": result.get("main_issue", ""),
        "feedback": result.get("feedback", ""),
        "teacher_review_needed": result.get("teacher_review_needed", False),
        "confidence": result.get("confidence"),
    }


@practice_bp.route("/free_response_practice", methods=["GET"])
@login_required
def free_response_practice_page():
    variant = request.args.get("variant", DEFAULT_TREE_DIAGRAM_VARIANT).strip() or DEFAULT_TREE_DIAGRAM_VARIANT
    problem_type = request.args.get("problem_type", TREE_DIAGRAM_PROBLEM_TYPE).strip() or TREE_DIAGRAM_PROBLEM_TYPE
    if problem_type != TREE_DIAGRAM_PROBLEM_TYPE:
        return jsonify({"ok": False, "error": "unsupported_problem_type"}), 400
    try:
        payload = build_tree_diagram_listing_payload(variant)
    except ValueError:
        return jsonify({"ok": False, "error": "unsupported_variant"}), 400

    return render_template(
        "free_response_practice.html",
        curriculum=request.args.get("curriculum", "vocational"),
        volume=request.args.get("volume", "數學B4"),
        chapter_id=request.args.get("chapter_id", "1"),
        problem_type=problem_type,
        variant=variant,
        question=_public_question_payload(payload),
    )


@practice_bp.route("/api/free_response/tree_diagram/question", methods=["GET"])
@login_required
def tree_diagram_question_api():
    variant = request.args.get("variant", DEFAULT_TREE_DIAGRAM_VARIANT).strip() or DEFAULT_TREE_DIAGRAM_VARIANT
    try:
        payload = build_tree_diagram_listing_payload(variant)
    except ValueError:
        return jsonify({"ok": False, "error": "unsupported_variant"}), 400
    return jsonify({"ok": True, "question": _public_question_payload(payload)})


@practice_bp.route("/api/free_response/tree_diagram/submit", methods=["POST"])
@login_required
def tree_diagram_submit_api():
    data = request.get_json(silent=True) or {}
    variant = str(data.get("variant") or DEFAULT_TREE_DIAGRAM_VARIANT).strip() or DEFAULT_TREE_DIAGRAM_VARIANT
    if "answer_text" not in data:
        return jsonify({"ok": False, "error": "missing_answer_text"}), 400
    answer_text = str(data.get("answer_text") or "")
    try:
        payload = build_tree_diagram_listing_payload(variant)
        result = judge_tree_diagram_text_answer(payload, answer_text)
    except ValueError:
        return jsonify({"ok": False, "error": "unsupported_variant"}), 400
    except Exception:
        current_app.logger.exception(
            "[Phase5F-D][tree_diagram_submit] failed user_id=%s variant=%s",
            getattr(current_user, "id", None),
            variant,
        )
        return jsonify({"ok": False, "error": "tree_diagram_grading_failed"}), 500
    return jsonify({"ok": True, "result": _public_judge_result(result)})
