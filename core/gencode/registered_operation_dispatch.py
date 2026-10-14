"""Generic registry-dispatched domain operation execution.

Resolves handler, matrix validator and payload adapter exclusively from
``domain_operation_registry``; no domain- or skill-specific routing lives here.
"""

from __future__ import annotations

import importlib
from copy import deepcopy
from typing import Any, Callable

from core.registry.domain_operation_registry import get_domain_spec, get_operation_spec


class RegisteredOperationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _resolve_callable(reference: str, *, default_module: str) -> Callable[..., Any]:
    module_name, _, attr = reference.rpartition(".") if "." in reference else (default_module, "", reference)
    target = getattr(importlib.import_module(module_name), attr, None)
    if not callable(target):
        raise RegisteredOperationError("operation_callable_missing", f"not callable: {module_name}.{attr}")
    return target


def resolve_operation_callables(domain_key: str, operation: str) -> dict[str, Callable[..., Any] | None]:
    domain = get_domain_spec(domain_key)
    op = get_operation_spec(domain_key, operation)
    if domain is None or op is None:
        raise RegisteredOperationError("operation_not_registered", f"{domain_key}:{operation}")
    if not op.payload_adapter:
        raise RegisteredOperationError("payload_adapter_missing", f"{domain_key}:{operation}")
    return {
        "handler": _resolve_callable(op.handler, default_module=domain.domain_module),
        "validator": _resolve_callable(op.validator, default_module=domain.domain_module) if op.validator else None,
        "payload_adapter": _resolve_callable(op.payload_adapter, default_module=domain.domain_module),
    }


def matrix_operation(matrix: dict[str, Any]) -> str:
    facts = matrix.get("validation_facts") if isinstance(matrix.get("validation_facts"), dict) else {}
    return str(matrix.get("domain_operation") or facts.get("domain_operation") or "").strip()


def dispatch_registered_operation(
    domain_key: str,
    operation: str,
    *,
    seed: int | None = None,
    constraints: dict[str, Any] | None = None,
    **adapter_kwargs: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build the domain matrix, validate it, and adapt it to a runtime payload."""
    callables = resolve_operation_callables(domain_key, operation)
    matrix = callables["handler"](seed=seed, domain_operation=operation, constraints=deepcopy(constraints or {}))
    if not isinstance(matrix, dict):
        raise RegisteredOperationError("matrix_invalid", f"{domain_key}:{operation}")
    if matrix_operation(matrix) != operation:
        raise RegisteredOperationError("operation_identity_mismatch", f"{domain_key}:{operation}")
    validator = callables["validator"]
    if validator is not None and not validator(matrix):
        raise RegisteredOperationError("matrix_validation_failed", f"{domain_key}:{operation}")
    payload = callables["payload_adapter"](deepcopy(matrix), domain_operation=operation, seed=seed, **adapter_kwargs)
    if not isinstance(payload, dict):
        raise RegisteredOperationError("payload_invalid", f"{domain_key}:{operation}")
    return matrix, payload
