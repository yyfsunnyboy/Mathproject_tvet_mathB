"""Line equation domain operators — pure math, no administrative coupling."""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any

_SUPPORTED_LINE_TYPES = frozenset(
    {
        "two_points",
        "point_slope",
        "horizontal_line",
        "vertical_line",
        "oblique_line",
    }
)


def build_line_equation_matrix(
    *,
    seed: int | None,
    line_type: str,
    curriculum_profile: str,
    difficulty_profile: str,
    constraints: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build a full problem matrix for a line-equation scenario."""
    normalized_type = str(line_type or "").strip()
    if normalized_type not in _SUPPORTED_LINE_TYPES:
        raise ValueError(f"Unsupported line_type: {line_type!r}")

    rng = random.Random(0 if seed is None else seed)
    profile = str(curriculum_profile or "").strip()
    difficulty = str(difficulty_profile or "").strip()
    extra = dict(constraints or {})

    coord_min, coord_max = _resolve_coord_bounds(profile, difficulty, extra)
    x_range, y_range = _resolve_visual_ranges(profile, difficulty, extra)

    if normalized_type == "two_points":
        givens, answer, actual_type = _build_two_points(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "point_slope":
        givens, answer, actual_type = _build_point_slope(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "horizontal_line":
        givens, answer, actual_type = _build_horizontal_line(
            rng, coord_min, coord_max, extra
        )
    elif normalized_type == "vertical_line":
        givens, answer, actual_type = _build_vertical_line(
            rng, coord_min, coord_max, extra
        )
    else:
        givens, answer, actual_type = _build_oblique_line(
            rng, coord_min, coord_max, extra
        )

    coeffs = answer["coefficients"]
    assert isinstance(coeffs, dict)
    a_int = int(coeffs["A"])
    b_int = int(coeffs["B"])
    c_int = int(coeffs["C"])

    validation_facts: dict[str, object] = {
        "line_type": actual_type,
        "coefficients": {"A": a_int, "B": b_int, "C": c_int},
        "is_vertical": actual_type == "vertical_line",
        "is_horizontal": actual_type == "horizontal_line",
        "points_satisfy_line": _collect_points_on_line(givens, a_int, b_int, c_int),
    }

    visual_spec = _build_visual_spec(
        givens=givens,
        answer=answer,
        actual_type=actual_type,
        x_range=x_range,
        y_range=y_range,
    )
    distractors = _build_distractors(
        rng=rng,
        answer=answer,
        actual_type=actual_type,
        givens=givens,
        coord_min=coord_min,
        coord_max=coord_max,
    )
    explanation_steps = _build_explanation_steps(
        line_type=normalized_type,
        actual_type=actual_type,
        givens=givens,
        answer=answer,
    )

    return {
        "givens": givens,
        "answer": answer,
        "distractors": distractors,
        "explanation_steps": explanation_steps,
        "validation_facts": validation_facts,
        "visual_spec": visual_spec,
    }


def _resolve_coord_bounds(
    curriculum_profile: str,
    difficulty_profile: str,
    constraints: dict[str, object],
) -> tuple[int, int]:
    if curriculum_profile == "vocational_high_b":
        lo, hi = -8, 8
    else:
        lo, hi = -6, 6

    if difficulty_profile in {"hard", "advanced"}:
        lo, hi = lo - 2, hi + 2
    elif difficulty_profile in {"easy", "basic"}:
        lo, hi = max(lo, -6), min(hi, 6)

    if "coord_min" in constraints:
        lo = int(constraints["coord_min"])  # type: ignore[arg-type]
    if "coord_max" in constraints:
        hi = int(constraints["coord_max"])  # type: ignore[arg-type]
    return lo, hi


def _resolve_visual_ranges(
    curriculum_profile: str,
    difficulty_profile: str,
    constraints: dict[str, object],
) -> tuple[list[int], list[int]]:
    lo, hi = _resolve_coord_bounds(curriculum_profile, difficulty_profile, constraints)
    margin = 2 if difficulty_profile in {"hard", "advanced"} else 0
    x_range = [lo - margin, hi + margin]
    y_range = [lo - margin, hi + margin]
    if isinstance(constraints.get("x_range"), list) and len(constraints["x_range"]) == 2:
        x_range = [int(constraints["x_range"][0]), int(constraints["x_range"][1])]  # type: ignore[index]
    if isinstance(constraints.get("y_range"), list) and len(constraints["y_range"]) == 2:
        y_range = [int(constraints["y_range"][0]), int(constraints["y_range"][1])]  # type: ignore[index]
    return x_range, y_range


def _pick_slope(rng: random.Random, *, allow_fraction: bool = True) -> Fraction:
    if allow_fraction and rng.random() < 0.35:
        numerators = [1, 2, 3, -1, -2, -3]
        denominators = [2, 3]
        slope = Fraction(rng.choice(numerators), rng.choice(denominators))
        if slope == 0:
            return Fraction(1, 2)
        return slope
    candidates = [i for i in range(-5, 6) if i != 0]
    return Fraction(rng.choice(candidates), 1)


def _build_two_points(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    if _has_point_pair(constraints):
        x1, y1, x2, y2 = _read_point_pair(constraints)
    else:
        for _ in range(200):
            x1 = rng.randint(coord_min, coord_max)
            y1 = rng.randint(coord_min, coord_max)
            x2 = rng.randint(coord_min, coord_max)
            y2 = rng.randint(coord_min, coord_max)
            if x1 != x2 or y1 != y2:
                break
        else:
            x1, y1, x2, y2 = -3, 1, 2, 4

    givens: dict[str, object] = {
        "point_a": [x1, y1],
        "point_b": [x2, y2],
    }

    if x1 == x2:
        answer, actual_type = _line_from_vertical(x1)
    elif y1 == y2:
        answer, actual_type = _line_from_horizontal(y1)
    else:
        slope = Fraction(y2 - y1, x2 - x1)
        answer, actual_type = _line_from_point_slope(x1, y1, slope)
    return givens, answer, actual_type


def _build_point_slope(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    if _has_point_and_slope(constraints):
        x1, y1, slope = _read_point_and_slope(constraints)
        if slope is None:
            raise ValueError("point_slope requires a non-vertical slope.")
    else:
        x1 = rng.randint(coord_min, coord_max)
        y1 = rng.randint(coord_min, coord_max)
        slope = _pick_slope(rng)

    if slope is None:
        raise ValueError("point_slope cannot produce a vertical line.")

    givens: dict[str, object] = {
        "point": [x1, y1],
        "slope": _format_number(slope),
    }
    answer, actual_type = _line_from_point_slope(x1, y1, slope)
    return givens, answer, actual_type


def _build_horizontal_line(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    if "y_intercept" in constraints:
        y_val = int(constraints["y_intercept"])  # type: ignore[arg-type]
    elif "k" in constraints:
        y_val = int(constraints["k"])  # type: ignore[arg-type]
    else:
        y_val = rng.randint(coord_min, coord_max)

    x1 = rng.randint(coord_min, coord_max)
    for _ in range(200):
        x2 = rng.randint(coord_min, coord_max)
        if x2 != x1:
            break
    else:
        x2 = x1 + 1 if x1 < coord_max else x1 - 1

    givens: dict[str, object] = {
        "point_a": [x1, y_val],
        "point_b": [x2, y_val],
    }
    answer, actual_type = _line_from_horizontal(y_val)
    return givens, answer, actual_type


def _build_vertical_line(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    if "x_intercept" in constraints:
        x_val = int(constraints["x_intercept"])  # type: ignore[arg-type]
    elif "k" in constraints:
        x_val = int(constraints["k"])  # type: ignore[arg-type]
    else:
        x_val = rng.randint(coord_min, coord_max)

    y1 = rng.randint(coord_min, coord_max)
    for _ in range(200):
        y2 = rng.randint(coord_min, coord_max)
        if y2 != y1:
            break
    else:
        y2 = y1 + 1 if y1 < coord_max else y1 - 1

    givens: dict[str, object] = {
        "point_a": [x_val, y1],
        "point_b": [x_val, y2],
    }
    answer, actual_type = _line_from_vertical(x_val)
    return givens, answer, actual_type


def _build_oblique_line(
    rng: random.Random,
    coord_min: int,
    coord_max: int,
    constraints: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], str]:
    if _has_point_and_slope(constraints):
        x1, y1, slope = _read_point_and_slope(constraints)
        if slope is None or slope == 0:
            raise ValueError("oblique_line requires a non-zero, non-vertical slope.")
    else:
        x1 = rng.randint(coord_min, coord_max)
        y1 = rng.randint(coord_min, coord_max)
        slope = _pick_slope(rng, allow_fraction=True)
        while slope == 0:
            slope = _pick_slope(rng, allow_fraction=True)

    givens: dict[str, object] = {
        "point": [x1, y1],
        "slope": _format_number(slope),
    }
    answer, actual_type = _line_from_point_slope(x1, y1, slope)
    return givens, answer, actual_type


def _line_from_vertical(x_val: int) -> tuple[dict[str, object], str]:
    a_int, b_int, c_int = _normalize_coefficients(1, 0, -x_val)
    canonical = f"x = {x_val}"
    general = _format_general_form(a_int, b_int, c_int)
    return (
        {
            "canonical_form": canonical,
            "general_form": general,
            "coefficients": {"A": a_int, "B": b_int, "C": c_int},
            "slope": None,
            "intercept": None,
        },
        "vertical_line",
    )


def _line_from_horizontal(y_val: int) -> tuple[dict[str, object], str]:
    a_int, b_int, c_int = _normalize_coefficients(0, 1, -y_val)
    canonical = f"y = {y_val}"
    general = _format_general_form(a_int, b_int, c_int)
    return (
        {
            "canonical_form": canonical,
            "general_form": general,
            "coefficients": {"A": a_int, "B": b_int, "C": c_int},
            "slope": 0,
            "intercept": y_val,
        },
        "horizontal_line",
    )


def _line_from_point_slope(
    x1: int, y1: int, slope: Fraction
) -> tuple[dict[str, object], str]:
    if slope.denominator == 0:
        raise ValueError("Slope denominator must not be zero.")

    b_frac = Fraction(y1, 1) - slope * Fraction(x1, 1)
    a_int, b_int, c_int = _normalize_fraction_coefficients(
        slope, Fraction(-1, 1), b_frac
    )

    canonical = _format_slope_intercept(slope, b_frac)
    general = _format_general_form(a_int, b_int, c_int)
    intercept_value: str | int
    if b_frac.denominator == 1:
        intercept_value = b_frac.numerator
    else:
        intercept_value = _format_number(b_frac)

    slope_value: str | int
    if slope.denominator == 1:
        slope_value = slope.numerator
    else:
        slope_value = _format_number(slope)

    return (
        {
            "canonical_form": canonical,
            "general_form": general,
            "coefficients": {"A": a_int, "B": b_int, "C": c_int},
            "slope": slope_value,
            "intercept": intercept_value,
        },
        "oblique_line",
    )


def _normalize_fraction_coefficients(
    a: Fraction, b: Fraction, c: Fraction
) -> tuple[int, int, int]:
    denoms = [a.denominator, b.denominator, c.denominator]
    lcm = 1
    for d in denoms:
        lcm = lcm * d // math.gcd(lcm, d)
    a_int = int(a * lcm)
    b_int = int(b * lcm)
    c_int = int(c * lcm)
    return _normalize_coefficients(a_int, b_int, c_int)


def _normalize_coefficients(a: int, b: int, c: int) -> tuple[int, int, int]:
    g = math.gcd(math.gcd(abs(a), abs(b)), abs(c))
    if g:
        a //= g
        b //= g
        c //= g
    if a < 0:
        a, b, c = -a, -b, -c
    elif a == 0 and b < 0:
        b, c = -b, -c
    return a, b, c


def _format_general_form(a: int, b: int, c: int) -> str:
    terms: list[str] = []

    def append_term(coeff: int, var: str) -> None:
        if coeff == 0:
            return
        if not terms:
            if coeff == 1:
                terms.append(var)
            elif coeff == -1:
                terms.append(f"-{var}")
            else:
                terms.append(f"{coeff}{var}")
            return
        if coeff > 0:
            if coeff == 1:
                terms.append(f" + {var}")
            else:
                terms.append(f" + {coeff}{var}")
        elif coeff == -1:
            terms.append(f" - {var}")
        else:
            terms.append(f" - {abs(coeff)}{var}")

    append_term(a, "x")
    append_term(b, "y")
    if c != 0 or not terms:
        if not terms:
            terms.append(str(c))
        elif c > 0:
            terms.append(f" + {c}")
        else:
            terms.append(f" - {abs(c)}")
    return f"{''.join(terms)} = 0"


def _format_number(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _format_slope_intercept(slope: Fraction, intercept: Fraction) -> str:
    m_text = _format_slope_term(slope)
    if intercept == 0:
        return f"y = {m_text}x"
    sign = "+" if intercept > 0 else "-"
    b_abs = abs(intercept)
    if b_abs.denominator == 1:
        b_text = str(b_abs.numerator)
    else:
        b_text = _format_number(b_abs)
    return f"y = {m_text}x {sign} {b_text}"


def _format_slope_term(slope: Fraction) -> str:
    if slope == 1:
        return ""
    if slope == -1:
        return "-"
    if slope.denominator == 1:
        return str(slope.numerator)
    return _format_number(slope)


def _has_point_pair(constraints: dict[str, object]) -> bool:
    return "point_a" in constraints and "point_b" in constraints


def _read_point_pair(constraints: dict[str, object]) -> tuple[int, int, int, int]:
    pa = constraints["point_a"]
    pb = constraints["point_b"]
    if not isinstance(pa, (list, tuple)) or not isinstance(pb, (list, tuple)):
        raise ValueError("point_a and point_b must be coordinate pairs.")
    return int(pa[0]), int(pa[1]), int(pb[0]), int(pb[1])


def _has_point_and_slope(constraints: dict[str, object]) -> bool:
    return "point" in constraints and "slope" in constraints


def _read_point_and_slope(constraints: dict[str, object]) -> tuple[int, int, Fraction | None]:
    pt = constraints["point"]
    if not isinstance(pt, (list, tuple)):
        raise ValueError("point must be a coordinate pair.")
    x1, y1 = int(pt[0]), int(pt[1])
    slope_raw = constraints["slope"]
    if slope_raw is None:
        return x1, y1, None
    if isinstance(slope_raw, int) and not isinstance(slope_raw, bool):
        return x1, y1, Fraction(slope_raw, 1)
    if isinstance(slope_raw, str):
        text = slope_raw.strip()
        if "/" in text:
            num, den = text.split("/", 1)
            return x1, y1, Fraction(int(num), int(den))
        return x1, y1, Fraction(int(text), 1)
    raise ValueError("slope must be int, str, or None.")


def _collect_points_on_line(
    givens: dict[str, object],
    a: int,
    b: int,
    c: int,
) -> list[list[int]]:
    points: list[list[int]] = []
    for key in ("point_a", "point_b", "point"):
        raw = givens.get(key)
        if isinstance(raw, (list, tuple)) and len(raw) == 2:
            x_val, y_val = int(raw[0]), int(raw[1])
            if a * x_val + b * y_val + c == 0:
                points.append([x_val, y_val])
    return points


def _build_visual_spec(
    *,
    givens: dict[str, object],
    answer: dict[str, object],
    actual_type: str,
    x_range: list[int],
    y_range: list[int],
) -> dict[str, object]:
    points: list[dict[str, object]] = []
    lines: list[dict[str, object]] = []

    if "point_a" in givens and "point_b" in givens:
        pa = givens["point_a"]
        pb = givens["point_b"]
        if isinstance(pa, (list, tuple)) and isinstance(pb, (list, tuple)):
            points.append({"x": int(pa[0]), "y": int(pa[1]), "label": "A"})
            points.append({"x": int(pb[0]), "y": int(pb[1]), "label": "B"})
            lines.append({"through_points": ["A", "B"], "label": "L"})
    elif "point" in givens:
        pt = givens["point"]
        if isinstance(pt, (list, tuple)):
            points.append({"x": int(pt[0]), "y": int(pt[1]), "label": "P"})
            lines.append({"through_points": ["P"], "label": "L"})
    elif actual_type == "horizontal_line":
        y_val = int(givens.get("y_intercept", 0))  # type: ignore[arg-type]
        lines.append({"type": "horizontal", "y": y_val, "label": "L"})
    elif actual_type == "vertical_line":
        x_val = int(givens.get("x_intercept", 0))  # type: ignore[arg-type]
        lines.append({"type": "vertical", "x": x_val, "label": "L"})

    if actual_type == "oblique_line":
        slope = answer.get("slope")
        intercept = answer.get("intercept")
        line_entry: dict[str, object] = {"label": "L"}
        if isinstance(slope, int) and isinstance(intercept, int):
            line_entry.update({"type": "slope_intercept", "m": slope, "b": intercept})
        else:
            line_entry.update(
                {
                    "type": "slope_intercept",
                    "m": slope,
                    "b": intercept,
                }
            )
        if points:
            line_entry["through_points"] = [str(p.get("label", "")) for p in points]
        lines = [line_entry]

    return {
        "kind": "coordinate_plane_spec",
        "points": points,
        "lines": lines,
        "x_range": x_range,
        "y_range": y_range,
    }


def _build_distractors(
    *,
    rng: random.Random,
    answer: dict[str, object],
    actual_type: str,
    givens: dict[str, object],
    coord_min: int,
    coord_max: int,
) -> list[str]:
    canonical = str(answer["canonical_form"])
    candidates: list[str] = []

    if actual_type == "vertical_line":
        x_val = _extract_vertical_k(canonical)
        for delta in (-2, -1, 1, 2, 3):
            candidates.append(f"x = {x_val + delta}")
        candidates.extend([f"y = {rng.randint(coord_min, coord_max)}" for _ in range(3)])
    elif actual_type == "horizontal_line":
        y_val = _extract_horizontal_k(canonical)
        for delta in (-2, -1, 1, 2, 3):
            candidates.append(f"y = {y_val + delta}")
        candidates.extend([f"x = {rng.randint(coord_min, coord_max)}" for _ in range(3)])
    else:
        slope = answer.get("slope")
        intercept = answer.get("intercept")
        base_m = _parse_numeric_token(slope)
        base_b = _parse_numeric_token(intercept)
        perturbations = [
            (base_m + 1, base_b),
            (base_m - 1, base_b),
            (base_m, base_b + 1),
            (base_m, base_b - 1),
            (-base_m, base_b),
            (base_m, -base_b),
        ]
        for m_val, b_val in perturbations:
            candidates.append(_format_slope_intercept(Fraction(m_val), Fraction(b_val)))

        pt = givens.get("point")
        if isinstance(pt, (list, tuple)):
            x1, y1 = int(pt[0]), int(pt[1])
            wrong_b = y1 + 1
            candidates.append(_format_slope_intercept(Fraction(base_m), Fraction(wrong_b)))

    unique: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        text = item.strip()
        if not text or text == canonical or text in seen:
            continue
        seen.add(text)
        unique.append(text)
        if len(unique) >= 3:
            break

    attempt = 0
    while len(unique) < 3:
        attempt += 1
        fake = f"y = {rng.randint(coord_min, coord_max)}x + {rng.randint(coord_min, coord_max)}"
        if fake != canonical and fake not in seen:
            seen.add(fake)
            unique.append(fake)
        if attempt > 50:
            for filler in ("y = x + 99", "y = -x - 99", "y = 2x + 5"):
                if filler != canonical and filler not in seen:
                    seen.add(filler)
                    unique.append(filler)
            break

    return unique


def _extract_vertical_k(canonical: str) -> int:
    parts = canonical.split("=", 1)
    return int(parts[1].strip())


def _extract_horizontal_k(canonical: str) -> int:
    parts = canonical.split("=", 1)
    return int(parts[1].strip())


def _parse_numeric_token(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip()
        if "/" in text:
            num, den = text.split("/", 1)
            return int(Fraction(int(num), int(den)))
        return int(text)
    return 0


def _build_explanation_steps(
    *,
    line_type: str,
    actual_type: str,
    givens: dict[str, object],
    answer: dict[str, object],
) -> list[str]:
    canonical = str(answer["canonical_form"])
    if line_type == "two_points":
        return [
            "以兩點座標計算斜率或判斷是否為水平/鉛直線",
            "代入點斜式或特殊式整理",
            f"化簡得 {canonical}",
        ]
    if line_type == "point_slope":
        return [
            "寫出點斜式",
            "展開並移項整理",
            f"化簡得 {canonical}",
        ]
    if actual_type == "horizontal_line":
        return [
            "觀察兩點的 y 座標相同，判斷為水平線",
            "水平線斜率為 0",
            f"直接寫成 {canonical}",
        ]
    if actual_type == "vertical_line":
        return [
            "觀察兩點的 x 座標相同，判斷為鉛直線",
            "鉛直線斜率不存在",
            f"直接寫成 {canonical}",
        ]
    return [
        "確認斜率與截距",
        "寫成斜截式",
        f"化簡得 {canonical}",
    ]
