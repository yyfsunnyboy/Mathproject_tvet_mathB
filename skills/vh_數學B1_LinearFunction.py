from __future__ import annotations

from typing import Any
import math

from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill

SKILL_ID = 'vh_數學B1_LinearFunction'
GENERATOR_KEYS = ['vh_數學B1_LinearFunction:numeric_interpret_function_notation_short_answer:draft_v1']
GENERATOR_SPECS = [{'problem_type_id': 'numeric_interpret_function_notation_short_answer', 'checker_key': 'numeric_checker', 'equivalence_type': 'numeric_equivalence', 'generator_readiness': 'runtime_ready'}]

def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:
    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)


def _extract_answer_scalar(value: Any) -> Any:
    if isinstance(value, dict):
        for k in (
            "answer",
            "correct_answer",
            "gold_answer",
            "target_answer",
            "expected_answer",
            "canonical_answer",
            "value",
        ):
            if k in value and value.get(k) is not None:
                return value.get(k)
        ac = value.get("answer_contract") if isinstance(value.get("answer_contract"), dict) else {}
        for k in ("answer", "correct_answer", "value"):
            if k in ac and ac.get(k) is not None:
                return ac.get(k)
    if isinstance(value, (list, tuple)) and len(value) == 1:
        return _extract_answer_scalar(value[0])
    return value


def _normalize_numeric_text(value: Any) -> str:
    s = str(value).strip()
    s = s.replace("$", "").replace(",", "").replace(" ", "")
    s = s.replace("−", "-")
    return s


def _numeric_equal(a: Any, b: Any) -> bool | None:
    sa = _normalize_numeric_text(a)
    sb = _normalize_numeric_text(b)
    if not sa or not sb:
        return None
    try:
        fa = float(sa)
        fb = float(sb)
    except Exception:
        return None
    return math.isclose(fa, fb, rel_tol=0.0, abs_tol=1e-9)


def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None):
    ua = _extract_answer_scalar(user_answer)
    ca = _extract_answer_scalar(correct_answer)
    num_eq = _numeric_equal(ua, ca)
    if num_eq is not None:
        return num_eq
    payload = question_payload
    if payload is None and isinstance(user_answer, dict):
        payload = user_answer
    if ua is not None and ca is not None:
        return check_answer(ua, ca, payload=payload)
    return check_answer(user_answer, correct_answer, payload=payload)
