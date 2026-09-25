# -*- coding: utf-8 -*-
"""Post-MTEF LaTeX normalizers for MathType quirks."""

from __future__ import annotations

import re

# MathType often encodes ∥ as the trigraph: optional spacing cmd + "/" + U+EF01 + "/"
_MT_PARALLEL_TRIGRAPH = re.compile(r"(?:\\[ ,;!]*)?/\s*\uef01\s*/")
# After empty U+EF01 mapping the trigraph collapses to spacing + "//"
_MT_PARALLEL_SLASH_SLASH = re.compile(r"\\[ ,;!]+//")


def normalize_parallel_latex(text: str) -> str:
    """Normalize MathType / unicode parallel operators to ``\\parallel``.

    Does not hard-code specific textbook stems; only rewrites parallel encodings:
    - MathType trigraph ``/`` + U+EF01 + ``/`` (with optional MT spacing)
    - spacing + ``//`` left after empty U+EF01 mapping
    - unicode parallel ``∥`` (U+2225)

    Intentionally does **not** rewrite:
    - bare ``||``
    - norm / absolute bars (``\\|``, ``|x|``, ``\\Vert``, unicode ``‖`` U+2016)
    """
    if not text:
        return ""
    s = str(text)
    s = _MT_PARALLEL_TRIGRAPH.sub(r"\\parallel ", s)
    s = _MT_PARALLEL_SLASH_SLASH.sub(r"\\parallel ", s)
    s = s.replace("\u2225", r"\\parallel ")  # ∥ PARALLEL
    return s
