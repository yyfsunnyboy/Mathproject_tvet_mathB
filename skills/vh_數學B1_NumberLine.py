"""B1 NumberLine runtime adapter.

Textbook source ``src_4401`` is an inequality operation table
(multiply/divide both sides by positive/negative constants).

As of 2026-11-22 incremental closeout, this adapter ships a *native*
``inequality_operation_table`` generator with a deterministic oracle.
JH bootstrap (point reading / distance) remains available only when
``bootstrap=True`` is explicitly requested; it is **not** textbook-faithful
coverage of ``src_4401`` and must not be reported as B1-native PASS.
"""

from __future__ import annotations

from typing import Any

from core.checkers.multi_part_answer_checker import check_multi_part_answer
from core.gencode.numberline_inequality_table import generate_inequality_operation_table

SKILL_ID = "vh_數學B1_NumberLine"
BOOTSTRAP_SOURCE = "jh_數學1上_NumberLine"
SOURCE_COVERAGE_STATUS = "COVERED_BY_NATIVE_GENERATOR"
BOOTSTRAP_MODE = False
TEXTBOOK_SOURCE_IDS = (4401,)
TEXTBOOK_FIDELITY_STATUS = "NATIVE_COVERED"
TEXTBOOK_FIDELITY_NOTES = (
    "src_4401 inequality operation table covered by native generator; "
    "JH bootstrap retained only as explicit non-faithful fallback."
)

GENERATOR_KEYS = ["src_4401"]
GENERATOR_SPECS = [
    {
        "textbook_example_id": 4401,
        "component_id": "src_4401",
        "generator_key": "src_4401",
        "problem_type_id": "inequality_operation_table",
        "generator_readiness": "runtime_ready",
        "presentation_mode": "short_answer",
        "answer_type": "multi_part",
        "checker_key": "multi_part_answer_checker",
        "equivalence_type": "multi_part_answer",
        "source_coverage_status": SOURCE_COVERAGE_STATUS,
        "textbook_fidelity_status": TEXTBOOK_FIDELITY_STATUS,
        "sampling_weight": 10.0,
        "display_order": 4401,
        "source_order": 4401,
    },
]


def generate(
    level: int = 1,
    seed: int | None = None,
    difficulty: int | str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    _ = (level, difficulty)
    if bool(kwargs.get("bootstrap")):
        # Explicit non-faithful fallback — never the default student path.
        from importlib import import_module
        import random

        jh = import_module("skills.jh_數學1上_NumberLine")
        runtime_level = 1 if int(level or 1) <= 1 else int(level or 1)
        if int(level or 1) <= 1:
            runtime_level = random.Random(seed).choice([1, 2])
        raw = jh.generate(level=runtime_level)
        return {
            "skill_id": SKILL_ID,
            "problem_type_id": (
                "number_line_point_value_reading"
                if runtime_level <= 1
                else "number_line_distance_between_points"
            ),
            "question_text": str(raw.get("question_text") or raw.get("question") or ""),
            "question": str(raw.get("question_text") or raw.get("question") or ""),
            "answer": str(raw.get("answer") or raw.get("correct_answer") or ""),
            "correct_answer": str(raw.get("answer") or raw.get("correct_answer") or ""),
            "answer_type": "integer",
            "bootstrap_mode": True,
            "textbook_fidelity_status": "DEFERRED_MISALIGNED_BOOTSTRAP",
            "source_coverage_status": "BOOTSTRAP_ONLY_NOT_TEXTBOOK_FAITHFUL",
            "metadata": {
                "bootstrap_mode": True,
                "bootstrap_source_skill_id": BOOTSTRAP_SOURCE,
                "textbook_fidelity_status": "DEFERRED_MISALIGNED_BOOTSTRAP",
            },
        }

    return generate_inequality_operation_table(
        seed,
        skill_id=SKILL_ID,
        problem_type_id="inequality_operation_table",
        component_id=str(kwargs.get("component_id") or "src_4401"),
        textbook_example_id=4401,
    )


def generate_question(*args, **kwargs):
    return generate(*args, **kwargs)


def get_question(*args, **kwargs):
    return generate(*args, **kwargs)


def check(user_answer, correct_answer, question_payload=None):
    payload = question_payload or {}
    if str(payload.get("answer_type") or "") == "multi_part" or isinstance(correct_answer, dict):
        ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else None
        return check_multi_part_answer(
            user_answer,
            correct_answer,
            answer_contract=ac,
            payload=payload,
        )
    from importlib import import_module

    return import_module("skills.jh_數學1上_NumberLine").check(user_answer, correct_answer)
