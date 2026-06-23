"""Legacy generator invocation helpers for practice runtime."""

from __future__ import annotations

from types import ModuleType
from typing import Any


def normalize_legacy_payload(payload: dict[str, Any], *, skill_id: str) -> dict[str, Any]:
    """Fill the minimal API fields expected by the current practice frontend."""

    if "question_text" in payload and "new_question_text" not in payload:
        payload["new_question_text"] = payload["question_text"]

    if "answer" in payload and "correct_answer" not in payload:
        payload["correct_answer"] = payload["answer"]
    if "correct_answer" in payload and "answer" not in payload:
        payload["answer"] = payload["correct_answer"]

    if payload.get("choices") is None:
        payload["choices"] = []

    if "answer_type" not in payload:
        payload["answer_type"] = "multiple_choice" if payload.get("choices") else "text"

    payload["generator_mode"] = "legacy"
    payload["route_source"] = "legacy_skill"
    payload["question_source"] = "legacy_skill"
    payload.setdefault("skill_id", skill_id)
    return payload


def invoke_legacy_generator(
    module: ModuleType,
    *,
    skill_id: str,
    level: int,
) -> dict[str, Any]:
    """Invoke a legacy skill without modern runtime kwargs."""

    generate = getattr(module, "generate", None)
    if not callable(generate):
        raise RuntimeError(f"legacy_generate_missing:{skill_id}")

    payload = generate(level=level)
    if not isinstance(payload, dict):
        raise RuntimeError(f"legacy_generate_non_dict:{skill_id}")

    return normalize_legacy_payload(payload, skill_id=skill_id)


import inspect
from fractions import Fraction
from decimal import Decimal
import logging

logger = logging.getLogger("runtime_adapter")

def format_math_value(value: Any, decimal_places: int | None = None, prefer_fraction: bool = True) -> str:
    """Format math values (Fraction, int, float, Decimal, sympy.Rational, etc.) safely and cleanly."""
    if value is None:
        return ""
    
    tname = type(value).__name__
    
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        if decimal_places is not None:
            return f"{float(value):.{decimal_places}f}"
        return f"{value.numerator}/{value.denominator}"
        
    if tname in ("Rational", "Integer"):
        try:
            numerator = int(value.p)
            denominator = int(value.q)
            if denominator == 1:
                return str(numerator)
            if decimal_places is not None:
                return f"{float(value):.{decimal_places}f}"
            return f"{numerator}/{denominator}"
        except:
            pass

    if isinstance(value, Decimal):
        if decimal_places is not None:
            return f"{value:.{decimal_places}f}"
        return str(value)

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if decimal_places is not None:
            return f"{value:.{decimal_places}f}"
        return str(value)

    if isinstance(value, str):
        return value

    if "numpy" in str(type(value)):
        try:
            return format_math_value(value.item(), decimal_places, prefer_fraction)
        except:
            pass

    return str(value)


def normalize_runtime_value(value: Any) -> Any:
    """Normalize Fractions, Decimals, Sympy and Numpy types recursively for JSON serialization."""
    if isinstance(value, dict):
        return {k: normalize_runtime_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [normalize_runtime_value(v) for v in value]
    
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return value.numerator
        return f"{value.numerator}/{value.denominator}"
    
    if isinstance(value, Decimal):
        return float(value)
        
    tname = type(value).__name__
    if tname in ("Rational", "Integer"):
        try:
            numerator = int(value.p)
            denominator = int(value.q)
            if denominator == 1:
                return numerator
            return f"{numerator}/{denominator}"
        except:
            pass
            
    if "numpy" in str(type(value)):
        try:
            return normalize_runtime_value(value.item())
        except:
            pass
            
    return value


def invoke_skill_generate(
    module: Any,
    *,
    level: int | None = None,
    component_id: str | None = None,
    problem_type_id: str | None = None,
    seed: int | None = None,
    skill_id: str = ""
) -> dict[str, Any]:
    """Dynamically invokes a skill module's generate function according to its signature."""
    generate_fn = getattr(module, "generate", None)
    if not callable(generate_fn):
        raise AttributeError(f"Module does not have a callable 'generate' function: {skill_id}")

    sig = inspect.signature(generate_fn)
    params = sig.parameters
    
    accepts_var_kw = any(
        p.kind == inspect.Parameter.VAR_KEYWORD
        for p in params.values()
    )

    candidate_kwargs = {
        "level": level,
        "component_id": component_id,
        "problem_type_id": problem_type_id,
        "seed": seed,
    }

    # Extract only accepted parameters or pass all if **kwargs is supported
    kwargs = {}
    ignored_kwargs = {}
    for key, val in candidate_kwargs.items():
        if val is not None:
            if accepts_var_kw or key in params:
                kwargs[key] = val
            else:
                ignored_kwargs[key] = val

    # Log invocation details for audit
    logger.info(
        f"[RUNTIME INVOKE] skill_id={skill_id} module={module.__name__} "
        f"generate_signature={sig} requested_kwargs={candidate_kwargs} "
        f"accepted_kwargs={kwargs} ignored_kwargs={ignored_kwargs}"
    )

    # Invoke
    result = generate_fn(**kwargs)
    
    if not isinstance(result, dict):
        raise TypeError(f"Generator for {skill_id} returned non-dict value: {type(result)}")

    return result
