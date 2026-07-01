# -*- coding: utf-8 -*-
"""Domain logic for distance between two points in a plane."""

from __future__ import annotations

import math
import random
from typing import Any


def _empty_visual() -> dict[str, object]:
    return {
        "kind": "coordinate_plane_spec",
        "points": [],
        "lines": [],
        "x_range": [-8, 8],
        "y_range": [-8, 8],
    }


def build_distance_between_two_points_matrix(
    *,
    seed: int | None,
    curriculum_profile: str,
    difficulty_profile: str,
    constraints: dict[str, object] | None = None,
    domain_operation: str | None = None,
    line_type: str | None = None,
) -> dict[str, object]:
    """Build Domain Matrix for distance between two points operations."""
    op = str(domain_operation or line_type or "").strip()
    rng = random.Random(0 if seed is None else seed)
    extra = dict(constraints or {})

    if "solve_unknown_coordinate" in op:
        # Choose which coordinate is the unknown parameter 'k'
        # 0: x1, 1: y1, 2: x2, 3: y2
        param_idx = rng.choice([0, 1, 2, 3])
        
        # dy = t, dx = other
        t = rng.randint(3, 8)
        other = rng.choice([4, 6, 8, 12])
        d2 = t * t + other * other
        d = math.isqrt(d2)
        while d * d != d2:
            t = rng.randint(3, 8)
            other = rng.choice([4, 6, 8, 12])
            d2 = t * t + other * other
            d = math.isqrt(d2)
            
        if param_idx in (0, 2):
            known_y1 = rng.randint(-5, 5)
            known_y2 = known_y1 + t
            mid = rng.randint(-5, 5)
            if param_idx == 0:
                x2 = mid
                k1, k2 = mid - other, mid + other
                givens = {
                    "x1": "k", "y1": known_y1,
                    "x2": x2, "y2": known_y2,
                    "distance": d,
                    "unknown_parameter": "k",
                }
            else:
                x1 = mid
                k1, k2 = mid - other, mid + other
                givens = {
                    "x1": x1, "y1": known_y1,
                    "x2": "k", "y2": known_y2,
                    "distance": d,
                    "unknown_parameter": "k",
                }
        else:
            known_x1 = rng.randint(-5, 5)
            known_x2 = known_x1 + other
            mid = rng.randint(-5, 5)
            if param_idx == 1:
                y2 = mid
                k1, k2 = mid - t, mid + t
                givens = {
                    "x1": known_x1, "y1": "k",
                    "x2": known_x2, "y2": y2,
                    "distance": d,
                    "unknown_parameter": "k",
                }
            else:
                y1 = mid
                k1, k2 = mid - t, mid + t
                givens = {
                    "x1": known_x1, "y1": y1,
                    "x2": known_x2, "y2": "k",
                    "distance": d,
                    "unknown_parameter": "k",
                }
        solutions = sorted({k1, k2})
        answer = {
            "solutions": solutions,
            "canonical_form": str(solutions),
            "general_form": str(solutions),
            "coefficients": {},
        }
        distractors = []
    else:
        # direct distance computation
        x1, y1 = rng.randint(-10, 10), rng.randint(-10, 10)
        x2, y2 = rng.randint(-10, 10), rng.randint(-10, 10)
        while x1 == x2 and y1 == y2:
            x2, y2 = rng.randint(-10, 10), rng.randint(-10, 10)
            
        dx, dy = x2 - x1, y2 - y1
        d2 = dx * dx + dy * dy
        d = math.isqrt(d2)
        if d * d == d2:
            dist_str = str(d)
        else:
            dist_str = f"sqrt({d2})"
            
        givens = {
            "x1": x1, "y1": y1,
            "x2": x2, "y2": y2,
            "point_a": f"({x1},{y1})",
            "point_b": f"({x2},{y2})",
        }
        answer = {
            "distance": dist_str,
            "canonical_form": dist_str,
            "general_form": dist_str,
            "coefficients": {},
        }
        distractors = []

    return {
        "givens": givens,
        "answer": answer,
        "distractors": distractors,
        "explanation_steps": [
            "Use the 2D Cartesian distance formula: AB = sqrt((x2 - x1)^2 + (y2 - y1)^2).",
            "For unknown coordinate problems, set up the quadratic equation and solve for all possible values of k."
        ],
        "validation_facts": {
            "domain_operation": op,
            "task_type": op,
            "line_type": op,
            "curriculum_profile": curriculum_profile,
            "difficulty_profile": difficulty_profile,
        },
        "visual_spec": _empty_visual(),
    }
