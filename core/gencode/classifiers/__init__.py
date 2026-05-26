from __future__ import annotations

from .base import SkillClassifier
from .fallback_classifier import FallbackClassifier
from .vocational_math_b1_absolute_value import VocationalMathB1AbsoluteValueClassifier
from .vocational_math_b1_absolute_value_inequality import VocationalMathB1AbsoluteValueInequalityClassifier


def get_classifier_for_skill(skill_id: str) -> SkillClassifier:
    sid = str(skill_id or "").strip()
    if sid == "vh_數學B1_AbsoluteValue":
        return VocationalMathB1AbsoluteValueClassifier()
    if sid == "vh_數學B1_AbsoluteValueInequality":
        return VocationalMathB1AbsoluteValueInequalityClassifier()
    return FallbackClassifier()

