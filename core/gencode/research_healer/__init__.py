# -*- coding: utf-8 -*-
"""GenCode V3 Research Healer: the only automatic code repair mechanism in V3.

Replaces the legacy Regex / AST / UnifiedCleanup / AntiDuplication chain for
AI-written Python.  See ``adapter`` (entry points), ``eligibility`` (V3 rule
matrix) and ``provenance`` (research source hashes).
"""

from core.gencode.research_healer.adapter import (
    ADAPTER_VERSION,
    HEALER_MODE_ENV,
    MODE_OFF,
    MODE_REPAIR,
    MODE_SHADOW,
    ResearchHealerV3Result,
    heal_ai_python_source,
    heal_coder_files,
    record_coder_gate,
    resolve_healer_mode,
)
from core.gencode.research_healer.eligibility import RULE_ELIGIBILITY, V3_PRODUCTION_ALLOWLIST

__all__ = [
    "ADAPTER_VERSION",
    "HEALER_MODE_ENV",
    "MODE_OFF",
    "MODE_REPAIR",
    "MODE_SHADOW",
    "RULE_ELIGIBILITY",
    "ResearchHealerV3Result",
    "V3_PRODUCTION_ALLOWLIST",
    "heal_ai_python_source",
    "heal_coder_files",
    "record_coder_gate",
    "resolve_healer_mode",
]
