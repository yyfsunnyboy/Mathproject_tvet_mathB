# -*- coding: utf-8 -*-
"""Deterministic MathType MTEF parser (adapted from AndyQsmart/MTEF-py / mtef-go).

Pipeline:
  OLE bytes / Equation Native stream → records → MtAST → LaTeX
"""

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
]


def equation_native_to_latex(eqn_native_bytes: bytes) -> tuple[str, dict]:
    eqn, err = MTEF.OpenEquationNative(eqn_native_bytes)
    meta = {
        "error": err,
        "valid": bool(eqn and eqn.Valid),
        "mtef_version": getattr(eqn, "mMtefVer", None) if eqn else None,
        "inline": getattr(eqn, "mInline", None) if eqn else None,
    }
    if eqn is None:
        return "", meta
    latex = (eqn.Translate() or "").strip()
    meta["latex"] = latex
    if not latex:
        meta["error"] = meta["error"] or "empty_latex"
        meta["valid"] = False
    return latex, meta


def mtef_bytes_to_latex(ole_bytes: bytes) -> tuple[str, dict]:
    eqn, err = MTEF.OpenBytes(ole_bytes)
    meta = {
        "error": err,
        "valid": bool(eqn and eqn.Valid),
        "mtef_version": getattr(eqn, "mMtefVer", None) if eqn else None,
        "inline": getattr(eqn, "mInline", None) if eqn else None,
    }
    if eqn is None:
        return "", meta
    latex = (eqn.Translate() or "").strip()
    meta["latex"] = latex
    if not latex:
        meta["error"] = meta["error"] or "empty_latex"
        meta["valid"] = False
    return latex, meta
