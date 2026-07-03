from __future__ import annotations

from .base import SkillClassifier
from .coordinate_geometry_division_point import CoordinateGeometryDivisionPointClassifier
from .fallback_classifier import FallbackClassifier
from .vocational_math_b1_absolute_value import VocationalMathB1AbsoluteValueClassifier
from .vocational_math_b1_absolute_value_inequality import VocationalMathB1AbsoluteValueInequalityClassifier
from .vocational_math_b1_absolute_value_inequality_expansion import VocationalMathB1AbsoluteValueInequalityExpansionClassifier


def get_classifier_for_skill(skill_id: str) -> SkillClassifier:
    sid = str(skill_id or "").strip()

    # 1. Resolve from taxonomy domain key
    from core.registry.taxonomy_registry import resolve_domain_for_skill, SkillDomainNotRegisteredError
    try:
        routing = resolve_domain_for_skill(sid)
    except SkillDomainNotRegisteredError:
        routing = None

    if routing:
        domain_key = routing.get("fixed_domain_key")
        if domain_key == "coordinate_geometry.division_point_coordinates":
            return CoordinateGeometryDivisionPointClassifier()
        # Fallback to general generic classifier
        return FallbackClassifier()

    # 2. Existing explicit mappings (fallback for legacy/unregistered skills)
    if sid == "vh_數學B1_AbsoluteValue":
        return VocationalMathB1AbsoluteValueClassifier()
    if sid == "vh_數學B1_AbsoluteValueInequality":
        return VocationalMathB1AbsoluteValueInequalityClassifier()
    if sid == "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning":
        return VocationalMathB1AbsoluteValueInequalityExpansionClassifier()
    return FallbackClassifier()
