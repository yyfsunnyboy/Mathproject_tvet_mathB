"""Registry-driven operation selection from induced capabilities (no skill binding)."""

from __future__ import annotations

from typing import Any

from core.registry.domain_operation_registry import get_domain_spec

_FREQUENCY_TEXT_HINTS = ("次數", "頻率", "frequency", "分配表")
_WEIGHT_TEXT_HINTS = ("權重", "加權", "學分", "weight")
_TABLE_TEXT_HINTS = ("完成下表", "填寫", "統計量", "下表")


def _normalize_capability_tokens(values: Any) -> list[str]:
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    out: list[str] = []
    for item in values:
        token = str(item or "").strip()
        if token and token not in out:
            out.append(token)
    return out


def resolve_operation_for_capabilities(
    *,
    domain_key: str,
    required_capabilities: list[str] | tuple[str, ...] | None = None,
    problem_type_id: str = "",
    question_text: str = "",
    presentation_mode: str = "",
    answer_shape: str = "",
    field_specs: list[dict[str, Any]] | None = None,
) -> str | None:
    """Pick a registered domain operation that covers required capabilities."""
    domain = str(domain_key or "").strip()
    if domain == "statistics.descriptive_statistics":
        from core.domain.statistics.descriptive_statistics_analyzer import resolve_descriptive_operation

        return resolve_descriptive_operation(
            required_capabilities=list(required_capabilities or []),
            problem_type_id=problem_type_id,
            question_text=question_text,
            presentation_mode=presentation_mode,
            answer_shape=answer_shape,
            field_specs=field_specs,
        )

    spec = get_domain_spec(domain)
    if spec is None:
        return None

    required = _normalize_capability_tokens(required_capabilities)
    if not required:
        return None

    required_set = set(required)
    candidates: list[tuple[str, set[str]]] = []
    for op_key, op_spec in spec.operations.items():
        provided = set(op_spec.provided_capabilities or ())
        if not provided:
            continue
        if not required_set.issubset(provided):
            continue
        candidates.append((op_key, provided))

    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0][0]

    question = str(question_text or "")
    scored: list[tuple[int, str]] = []
    for op_key, provided in candidates:
        score = len(required_set & provided)
        if "frequency_table" in op_key and any(hint in question for hint in _FREQUENCY_TEXT_HINTS):
            score += 20
        if "from_raw_values" in op_key and not any(hint in question for hint in _FREQUENCY_TEXT_HINTS):
            score += 10
        if "weighted_mean" in op_key and any(hint in question for hint in _WEIGHT_TEXT_HINTS):
            score += 20
        if "table" in op_key and any(hint in question for hint in _TABLE_TEXT_HINTS):
            score += 20
        scored.append((score, op_key))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return scored[0][1]
