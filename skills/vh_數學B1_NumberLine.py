"""Bootstrap adapter for vocational B1 NumberLine using JH NumberLine generator."""

from __future__ import annotations

import random
from importlib import import_module

SKILL_ID = "vh_數學B1_NumberLine"
BOOTSTRAP_SOURCE = "jh_數學1上_NumberLine"
SOURCE_COVERAGE_STATUS = "INSUFFICIENT_OR_MISALIGNED_DB_EXAMPLES"
BOOTSTRAP_MODE = True

_JH_MODULE = import_module("skills.jh_數學1上_NumberLine")

_ANSWER_CONTRACTS = {
    "number_line_point_value_reading": {
        "answer_type": "integer",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "order_matters": False,
        "canonical_answer_schema": {"type": "integer"},
    },
    "number_line_distance_between_points": {
        "answer_type": "integer",
        "equivalence_type": "numeric_exact",
        "checker_key": "integer_checker",
        "order_matters": False,
        "canonical_answer_schema": {"type": "integer"},
    },
}


def _map_problem_type(level: int) -> str:
    if int(level or 1) <= 1:
        return "number_line_point_value_reading"
    return "number_line_distance_between_points"


def _to_payload(raw: dict, level: int) -> dict:
    problem_type_id = _map_problem_type(level)
    answer = str(raw.get("answer") or raw.get("correct_answer") or "").strip()
    question_text = str(raw.get("question_text") or raw.get("question") or "").strip()
    payload = {
        "skill_id": SKILL_ID,
        "problem_type_id": problem_type_id,
        "question_text": question_text,
        "question": question_text,
        "answer": answer,
        "correct_answer": answer,
        "answer_type": "integer",
        "answer_contract": _ANSWER_CONTRACTS[problem_type_id],
        "source_coverage_status": SOURCE_COVERAGE_STATUS,
        "bootstrap_mode": BOOTSTRAP_MODE,
        "bootstrap_source_skill_id": BOOTSTRAP_SOURCE,
        "metadata": {
            "bootstrap_mode": BOOTSTRAP_MODE,
            "bootstrap_source_skill_id": BOOTSTRAP_SOURCE,
            "bootstrap_runtime_status": "PASS",
            "source_coverage_status": SOURCE_COVERAGE_STATUS,
            "adapter_mode": "bootstrap_reference",
            "original_skill_id": str(raw.get("skill_id") or BOOTSTRAP_SOURCE),
            "original_problem_type_id": str(raw.get("problem_type_id") or ""),
        },
    }
    if raw.get("image_base64"):
        payload["image_base64"] = raw.get("image_base64")
    return payload


def generate(level=1, seed=None, difficulty=None):
    _ = difficulty
    requested_level = int(level or 1)
    if requested_level <= 1:
        rng = random.Random(seed)
        runtime_level = rng.choice([1, 2])
    else:
        runtime_level = requested_level

    raw = _JH_MODULE.generate(level=runtime_level)
    if not isinstance(raw, dict):
        raise RuntimeError("bootstrap NumberLine generator returned non-dict payload")
    return _to_payload(raw, runtime_level)


def generate_question(*args, **kwargs):
    return generate(*args, **kwargs)


def get_question(*args, **kwargs):
    return generate(*args, **kwargs)


def check(user_answer, correct_answer):
    user = str(user_answer).strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")
    if user == correct:
        return {"correct": True, "result": "答對了"}
    try:
        if abs(float(user) - float(correct)) < 1e-9:
            return {"correct": True, "result": "答對了"}
    except Exception:
        pass
    return {"correct": False, "result": f"答錯了，正確答案是 {correct_answer}"}

