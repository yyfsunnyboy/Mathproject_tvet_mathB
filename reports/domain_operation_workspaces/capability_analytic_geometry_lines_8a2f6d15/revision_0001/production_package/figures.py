"""``coordinate_plane`` visual specs for the shared practice renderer (static/js/visual_spec.js).

Only data: primitives are points / lines / right-angle marks / an inequality ``shade`` probe.  The
renderer clips ``shade`` against every listed line, so every line passed together with a ``shade``
must be a region boundary.
"""

from __future__ import annotations

import re
from fractions import Fraction
from math import ceil, floor
from typing import Any, Iterable

from .line_geometry import fr


_SUB = {"0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉", "n": "ₙ", "-": "₋"}


def pretty_label(label: str) -> str:
    """Canvas text cannot typeset LaTeX: ``L_{n-1}`` -> ``Lₙ₋₁``."""
    def repl(match: re.Match[str]) -> str:
        return match.group(1) + "".join(_SUB.get(ch, ch) for ch in match.group(2))

    return re.sub(r"([A-Za-z])_\{?([0-9n\-]+)\}?", repl, label)


def _f(value: Any) -> float:
    return float(fr(value))


def fit_view(points: Iterable[Any], pad: int = 1, include_origin: bool = True, minimum: int = 3) -> tuple[list[int], list[int]]:
    xs = [_f(p[0]) for p in points]
    ys = [_f(p[1]) for p in points]
    if include_origin:
        xs += [0.0]
        ys += [0.0]
    x0, x1 = floor(min(xs)) - pad, ceil(max(xs)) + pad
    y0, y1 = floor(min(ys)) - pad, ceil(max(ys)) + pad
    if x1 - x0 < minimum:
        x1 = x0 + minimum
    if y1 - y0 < minimum:
        y1 = y0 + minimum
    return [x0, x1], [y0, y1]


def point_entry(p: Any, label: str = "") -> dict[str, Any]:
    entry: dict[str, Any] = {"x": _f(p[0]), "y": _f(p[1])}
    if label:
        entry["label"] = pretty_label(label)
    return entry


def through_line(p: Any, q: Any, label: str = "", extend: bool = True, dashed: bool = False) -> dict[str, Any]:
    line: dict[str, Any] = {"through_points": [[_f(p[0]), _f(p[1])], [_f(q[0]), _f(q[1])]], "extend": bool(extend)}
    if label:
        line["label"] = pretty_label(label)
    if dashed:
        line["style"] = "dashed"
    return line


def general_line(coefficients: Iterable[Any], label: str = "", dashed: bool = False) -> dict[str, Any]:
    a, b, c = (_f(v) for v in coefficients)
    line: dict[str, Any] = {"a": a, "b": b, "c": c}
    if label:
        line["label"] = pretty_label(label)
    if dashed:
        line["style"] = "dashed"
    return line


def plane(
    *,
    points: list[dict[str, Any]] | None = None,
    lines: list[dict[str, Any]] | None = None,
    view: tuple[list[int], list[int]],
    shade_probe: Any | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    spec: dict[str, Any] = {
        "kind": "coordinate_plane",
        "points": points or [],
        "lines": lines or [],
        "x_range": list(view[0]),
        "y_range": list(view[1]),
        "render_required": True,
    }
    if shade_probe is not None:
        spec["shade"] = {"test_point": [_f(shade_probe[0]), _f(shade_probe[1])]}
    if extra:
        spec.update(extra)
    return spec


def blank_canvas(view: Iterable[Any]) -> dict[str, Any]:
    x0, x1, y0, y1 = (int(fr(v)) for v in view)
    return {
        "kind": "cartesian_canvas",
        "axis_range": {"x_min": x0, "x_max": x1, "y_min": y0, "y_max": y1},
        "show_grid": True,
        "editable": True,
    }


def centroid(points: list[Any]) -> tuple[Fraction, Fraction]:
    n = len(points)
    return (sum(fr(p[0]) for p in points) / n, sum(fr(p[1]) for p in points) / n)
