"""Hard-coded bridge from administrative skill_id to domain entrypoints."""

from __future__ import annotations

from typing import Any

SKILL_TO_DOMAIN: dict[str, dict[str, Any]] = {
    "vh_數學B1_PointSlopeForm": {
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_line_equation_matrix",
        "default_curriculum_profile": "vocational_high_b",
    },
    "vh_數學B1_HorizontalAndVerticalLineEquations": {
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_line_equation_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": ["horizontal_line", "vertical_line"],
    },
    "vh_數學B1_SlopeInterceptForm": {
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_line_equation_matrix",
        "default_curriculum_profile": "vocational_high_b",
        "allowed_types": [
            "slope_intercept_equation",
            "slope_intercept_find_x_intercept",
            "slope_intercept_read_slope_and_intercept",
        ],
    },
}


def resolve_domain_for_skill(skill_id: str) -> dict[str, Any]:
    """Return domain mapping metadata for a registered skill_id."""
    key = str(skill_id or "").strip()
    if key not in SKILL_TO_DOMAIN:
        raise KeyError(f"Unregistered skill_id: {skill_id!r}")
    return dict(SKILL_TO_DOMAIN[key])
