from __future__ import annotations

from .base import SkillClassifier
from .coordinate_geometry_division_point import (
    CoordinateGeometryDivisionPointClassifier,
    is_division_point_coordinate_skill,
)
from .fallback_classifier import FallbackClassifier
from .vocational_math_b1_absolute_value import VocationalMathB1AbsoluteValueClassifier
from .vocational_math_b1_absolute_value_inequality import VocationalMathB1AbsoluteValueInequalityClassifier
from .vocational_math_b1_absolute_value_inequality_expansion import VocationalMathB1AbsoluteValueInequalityExpansionClassifier


def get_classifier_for_skill(skill_id: str) -> SkillClassifier:
    sid = str(skill_id or "").strip()
    if is_division_point_coordinate_skill(sid):
        return CoordinateGeometryDivisionPointClassifier()
    if sid == "vh_數學B1_AbsoluteValue":
        return VocationalMathB1AbsoluteValueClassifier()
    if sid == "vh_數學B1_AbsoluteValueInequality":
        return VocationalMathB1AbsoluteValueInequalityClassifier()
    if sid == "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning":
        return VocationalMathB1AbsoluteValueInequalityExpansionClassifier()
    return FallbackClassifier()

