"""Shared Domain Functions for Trigonometry and Angle Concepts.

Provides stable, reusable mathematical primitives across multiple components:
1. Degree <-> Radian conversions with exact rational representations.
2. Sector geometry calculations (radius, angle, arc length, area).
3. Coterminal angle generation and normalization (min-positive, max-negative).
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any


def format_pi_fraction_latex(f: Fraction) -> str:
    """Format a rational multiple of pi as canonical LaTeX."""
    p, q = f.numerator, f.denominator
    sign = "-" if p < 0 else ""
    abs_p = abs(p)
    if q == 1:
        if abs_p == 1:
            return rf"{sign}\pi"
        return rf"{sign}{abs_p}\pi"
    else:
        if abs_p == 1:
            return rf"{sign}\frac{{\pi}}{{{q}}}"
        return rf"{sign}\frac{{{abs_p}\pi}}{{{q}}}"


def degree_to_radian(deg: int | float | Fraction) -> dict[str, Any]:
    """Convert an angle in degrees to exact radian fraction of pi and LaTeX."""
    deg_frac = Fraction(deg) if not isinstance(deg, Fraction) else deg
    rad_multiple = deg_frac / 180
    latex_str = format_pi_fraction_latex(rad_multiple)
    return {
        "degree": deg,
        "pi_multiple": rad_multiple,
        "latex": latex_str,
        "float_value": float(rad_multiple * math.pi),
    }


def radian_to_degree(rad_multiple: int | float | Fraction) -> dict[str, Any]:
    """Convert an angle given as a multiple of pi to degrees and LaTeX."""
    m_frac = Fraction(rad_multiple) if not isinstance(rad_multiple, Fraction) else rad_multiple
    deg_frac = m_frac * 180
    deg_val = int(deg_frac) if deg_frac.denominator == 1 else float(deg_frac)
    return {
        "pi_multiple": m_frac,
        "degree": deg_val,
        "degree_latex": f"{deg_val}^\\circ",
    }


def calculate_sector_properties(
    radius: int | float | Fraction,
    *,
    degree: int | float | Fraction | None = None,
    radian_multiple: Fraction | None = None,
    radian_exact: float | Fraction | None = None,
    area_given: Fraction | float | None = None,
    arc_given: Fraction | float | None = None,
) -> dict[str, Any]:
    """Calculate missing sector properties given consistent parameters.

    Supports:
    - (radius, degree) -> theta, arc length S, area A
    - (radius, area) -> theta, arc length S
    - (radius, arc) -> theta, area A
    """
    r = Fraction(radius) if not isinstance(radius, Fraction) else radius

    if degree is not None:
        theta_multiple = Fraction(degree) / 180
        arc_multiple = r * theta_multiple
        area_multiple = Fraction(1, 2) * (r * r) * theta_multiple
        return {
            "radius": int(r) if r.denominator == 1 else float(r),
            "degree": degree,
            "theta_multiple": theta_multiple,
            "theta_latex": format_pi_fraction_latex(theta_multiple),
            "arc_multiple": arc_multiple,
            "arc_latex": format_pi_fraction_latex(arc_multiple),
            "area_multiple": area_multiple,
            "area_latex": format_pi_fraction_latex(area_multiple),
        }

    if area_given is not None and degree is None and radian_multiple is None:
        # Given radius and area: A = 1/2 * r^2 * theta
        # theta_multiple = A / (1/2 * r^2)
        a_m = Fraction(area_given) if not isinstance(area_given, Fraction) else area_given
        theta_multiple = a_m / (Fraction(1, 2) * r * r)
        arc_multiple = r * theta_multiple
        return {
            "radius": int(r) if r.denominator == 1 else float(r),
            "area_multiple": a_m,
            "area_latex": format_pi_fraction_latex(a_m),
            "theta_multiple": theta_multiple,
            "theta_latex": format_pi_fraction_latex(theta_multiple),
            "arc_multiple": arc_multiple,
            "arc_latex": format_pi_fraction_latex(arc_multiple),
        }

    if arc_given is not None and degree is None and radian_multiple is None:
        # Given radius and arc length (numerical or pi multiple)
        # S = r * theta => theta = S / r
        # Area = 1/2 * r * S
        arc_val = Fraction(arc_given) if not isinstance(arc_given, Fraction) else arc_given
        theta_val = arc_val / r
        area_val = Fraction(1, 2) * r * arc_val
        return {
            "radius": int(r) if r.denominator == 1 else float(r),
            "arc_length": int(arc_val) if arc_val.denominator == 1 else float(arc_val),
            "theta_value": int(theta_val) if theta_val.denominator == 1 else float(theta_val),
            "theta_str": str(int(theta_val) if theta_val.denominator == 1 else float(theta_val)),
            "area_value": int(area_val) if area_val.denominator == 1 else float(area_val),
            "area_str": str(int(area_val) if area_val.denominator == 1 else float(area_val)),
        }

    raise ValueError("Insufficient or unsupported parameter combination for sector calculation.")


def check_is_coterminal(angle1: int | Fraction, angle2: int | Fraction, unit: str = "degree") -> tuple[bool, int | Fraction]:
    """Determine if two angles are coterminal and return the step factor k."""
    if unit == "degree":
        diff = angle1 - angle2
        k = diff / 360
        is_int = (k == int(k))
        return (is_int, int(k) if is_int else k)
    else:
        # unit == 'radian', angles given as multiples of pi
        diff = angle1 - angle2
        k = diff / 2
        is_int = (k == int(k))
        return (is_int, int(k) if is_int else k)


def find_min_positive_max_negative(angle: int | Fraction, unit: str = "degree") -> dict[str, Any]:
    """Find the minimum positive and maximum negative coterminal angles."""
    if unit == "degree":
        deg = int(angle)
        rem = deg % 360
        min_pos = rem if rem != 0 else 360
        max_neg = min_pos - 360
        return {
            "unit": "degree",
            "angle": deg,
            "min_positive": min_pos,
            "max_negative": max_neg,
            "min_pos_latex": f"{min_pos}^\\circ",
            "max_neg_latex": f"{max_neg}^\\circ",
        }
    else:
        # Radian multiple of pi
        rad_f = Fraction(angle) if not isinstance(angle, Fraction) else angle
        p, q = rad_f.numerator, rad_f.denominator
        # angle in terms of 2pi = angle / 2
        rem_frac = rad_f % 2
        min_pos_f = rem_frac if rem_frac != 0 else Fraction(2, 1)
        max_neg_f = min_pos_f - 2
        return {
            "unit": "radian",
            "angle_multiple": rad_f,
            "min_positive": min_pos_f,
            "max_negative": max_neg_f,
            "min_pos_latex": format_pi_fraction_latex(min_pos_f),
            "max_neg_latex": format_pi_fraction_latex(max_neg_f),
        }
