# -*- coding: utf-8 -*-
"""Deterministic MathType MTEF parser (adapted from AndyQsmart/MTEF-py / mtef-go).

Pipeline:
  OLE bytes / Equation Native stream → records → MtAST → LaTeX
"""

from .latex_normalize import normalize_parallel_latex
from .mtef import MTEF, oleCbHdr
from .record import MtAST, RecordType, SelectorType

__all__ = [
    "MTEF",
    "MtAST",
    "RecordType",
    "SelectorType",
    "oleCbHdr",
    "mtef_bytes_to_latex",
    "equation_native_to_latex",
    "normalize_parallel_latex",
]


def _meta_from_eqn(eqn, err=None):
    meta = {
        "error": err,
        "valid": bool(eqn and eqn.Valid),
        "mtef_version": getattr(eqn, "mMtefVer", None) if eqn else None,
        "inline": getattr(eqn, "mInline", None) if eqn else None,
        "failure_stage": getattr(eqn, "_failure_stage", None) if eqn else None,
        "failure_reason": getattr(eqn, "_failure_reason", None) if eqn else None,
        "unknown_record": getattr(eqn, "_unknown_record", None) if eqn else None,
        "unknown_offset": getattr(eqn, "_unknown_offset", None) if eqn else None,
    }
    return meta


def _classify_empty(eqn, meta):
    """Distinguish parse/serializer failures from a truly empty equation."""
    if eqn is None:
        meta["error"] = meta.get("error") or "mtef_stream_missing"
        meta["failure_stage"] = meta.get("failure_stage") or "mtef_stream_missing"
        meta["valid"] = False
        return meta

    if not eqn.Valid:
        unk = getattr(eqn, "_unknown_record", None)
        if unk is not None:
            meta["error"] = f"mtef_unsupported_record:{unk}"
            meta["failure_stage"] = "mtef_unsupported_record"
            meta["failure_reason"] = getattr(eqn, "_failure_reason", None) or f"unsupported_record:{unk}"
        else:
            stage = getattr(eqn, "_failure_stage", None) or "mtef_parse_failed"
            meta["error"] = stage
            meta["failure_stage"] = stage
            meta["failure_reason"] = getattr(eqn, "_failure_reason", None) or stage
        meta["valid"] = False
        return meta

    stage = getattr(eqn, "_failure_stage", None)
    if stage == "mtef_serializer_empty":
        meta["error"] = "mtef_serializer_empty"
        meta["failure_stage"] = "mtef_serializer_empty"
        meta["failure_reason"] = getattr(eqn, "_failure_reason", None) or "serializer_produced_empty_latex"
        meta["valid"] = False
        return meta

    # Parsed successfully but produced no tokens / empty structure.
    meta["error"] = "empty_equation"
    meta["failure_stage"] = "empty_equation"
    meta["failure_reason"] = "equation_has_no_renderable_content"
    meta["valid"] = False
    return meta


def equation_native_to_latex(eqn_native_bytes: bytes) -> tuple[str, dict]:
    eqn, err = MTEF.OpenEquationNative(eqn_native_bytes)
    meta = _meta_from_eqn(eqn, err)
    if eqn is None:
        return "", _classify_empty(None, meta)
    if not eqn.Valid:
        return "", _classify_empty(eqn, meta)
    latex = (eqn.Translate() or "").strip()
    meta["latex"] = latex
    if not latex:
        return "", _classify_empty(eqn, meta)
    return latex, meta


def mtef_bytes_to_latex(ole_bytes: bytes) -> tuple[str, dict]:
    eqn, err = MTEF.OpenBytes(ole_bytes)
    meta = _meta_from_eqn(eqn, err)
    if eqn is None:
        # OpenBytes errors include missing Equation Native stream.
        if err and "Equation Native not found" in err:
            meta["error"] = "mtef_stream_missing"
            meta["failure_stage"] = "mtef_stream_missing"
        else:
            meta["error"] = err or "mtef_stream_missing"
            meta["failure_stage"] = "mtef_stream_missing"
        meta["valid"] = False
        return "", meta
    if not eqn.Valid:
        return "", _classify_empty(eqn, meta)
    latex = (eqn.Translate() or "").strip()
    meta["latex"] = latex
    if not latex:
        return "", _classify_empty(eqn, meta)
    return latex, meta
