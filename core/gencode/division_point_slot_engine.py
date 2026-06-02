# -*- coding: utf-8 -*-
"""Contract-driven runtime generators for division_point_coordinates_family tasks."""

from __future__ import annotations

import math
import random
import re
from fractions import Fraction
from typing import Any

from core.checkers.coordinate_pair_checker import parse_coordinate_pair_answer
from core.gencode.answer_payload import answer_type_family
from core.gencode.answer_contract_gate import coerce_single_choice_contract
from core.gencode.generator_contract_schema import DEFAULT_ANTI_REPETITION
from core.gencode.problem_type_spec import get_answer_contract, get_generator_contract

DIVISION_POINT_SLOT = "division_point_coordinates"

_TARGET_TASKS = frozenset(
    {
        "compute_internal_division_point_coordinates",
        "compute_centroid_coordinates",
        "compute_midpoint_coordinates",
        "solve_point_from_section_ratio",
    }
)


def is_division_point_target_task(target_task: str) -> bool:
    return str(target_task or "").strip() in _TARGET_TASKS


def _rng(seed: int | None, problem_type_id: str) -> random.Random:
    if seed is None:
        return random.Random()
    return random.Random(f"{seed}|division_point|{problem_type_id}")


def _gc(spec: dict[str, Any]) -> dict[str, Any]:
    return get_generator_contract(spec) if isinstance(spec, dict) else {}


def _schema(gc: dict[str, Any]) -> dict[str, Any]:
    ps = gc.get("parameter_schema")
    return ps if isinstance(ps, dict) else {}


def _enabled_variants(gc: dict[str, Any]) -> list[dict[str, Any]]:
    variants = gc.get("template_variants")
    if not isinstance(variants, list):
        return []
    return [v for v in variants if isinstance(v, dict) and v.get("enabled", True)]


def _weighted_variant(rng: random.Random, variants: list[dict[str, Any]]) -> dict[str, Any]:
    if not variants:
        return {"id": "default", "stem_pattern": ""}
    weights = [float(v.get("weight", 1.0) or 1.0) for v in variants]
    total = sum(weights) or 1.0
    r = rng.random() * total
    acc = 0.0
    for v, w in zip(variants, weights):
        acc += w
        if r <= acc:
            return v
    return variants[-1]


def _pick_names(rng: random.Random, schema: dict[str, Any], default: list[str]) -> list[str]:
    pn = schema.get("point_names") if isinstance(schema.get("point_names"), dict) else {}
    choices = pn.get("choices")
    if isinstance(choices, list) and choices:
        return [str(x) for x in rng.choice(choices)]
    return list(default)


def _coord_bounds(schema: dict[str, Any]) -> tuple[int, int, int, int]:
    cr = schema.get("coordinate_range") if isinstance(schema.get("coordinate_range"), dict) else {}
    return (
        int(cr.get("x_min", -10)),
        int(cr.get("x_max", 10)),
        int(cr.get("y_min", -10)),
        int(cr.get("y_max", 10)),
    )


def _rand_int(rng: random.Random, lo: int, hi: int, *, avoid_zero_prob: float = 0.0) -> int:
    for _ in range(50):
        v = rng.randint(lo, hi)
        if avoid_zero_prob and v == 0 and rng.random() < avoid_zero_prob:
            continue
        return v
    opts = [i for i in range(lo, hi + 1) if i != 0]
    return rng.choice(opts) if opts else 1


def _pick_ratio(rng: random.Random, schema: dict[str, Any]) -> tuple[int, int]:
    ratio = schema.get("ratio") if isinstance(schema.get("ratio"), dict) else {}
    m = rng.randint(int(ratio.get("m_min", 1)), int(ratio.get("m_max", 5)))
    n = rng.randint(int(ratio.get("n_min", 1)), int(ratio.get("n_max", 5)))
    if ratio.get("require_coprime", True):
        g = math.gcd(m, n)
        m, n = max(1, m // g), max(1, n // g)
    if not ratio.get("allow_equal_ratio", False) and m == n:
        n = min(int(ratio.get("n_max", 5)), m + 1)
    return m, n


def _answer_mode(rng: random.Random, schema: dict[str, Any]) -> str:
    atm = schema.get("answer_type_mode") if isinstance(schema.get("answer_type_mode"), dict) else {}
    choices = atm.get("choices")
    weights = atm.get("weights")
    if isinstance(choices, list) and choices:
        if isinstance(weights, list) and len(weights) == len(choices):
            total = sum(float(w) for w in weights) or 1.0
            r = rng.random() * total
            acc = 0.0
            for c, w in zip(choices, weights):
                acc += float(w)
                if r <= acc:
                    return str(c)
        return str(rng.choice(choices))
    return "integer_coordinate"


def _fmt_num(val: float | Fraction | int) -> str:
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        return f"{val.numerator}/{val.denominator}"
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    if isinstance(val, int):
        return str(val)
    text = f"{val:.4f}".rstrip("0").rstrip(".")
    return text or "0"


def _fmt_pair(x: float | Fraction | int, y: float | Fraction | int) -> str:
    return f"({_fmt_num(x)},{_fmt_num(y)})"


def _overline_segment(p1: str, p2: str) -> str:
    return f"$\\overline{{{p1}{p2}}}$"


def _overline_seg_name(seg: str) -> str:
    """Two-letter segment name inside a math block, e.g. AP -> \\overline{AP}."""
    name = str(seg or "").strip().upper()
    if len(name) != 2 or not name.isalpha():
        return str(seg)
    return f"\\overline{{{name}}}"


def _ratio_relation_latex(
    variant_id: str,
    left: str,
    mid: str,
    right: str,
    m: int,
    n: int,
) -> str:
    """
    LaTeX for segment ratio on collinear points left—mid—right.
    Covers ratio_colon_form, multiple_form, linear_relation_form.
    """
    seg_left = _overline_seg_name(f"{left}{mid}")
    seg_right = _overline_seg_name(f"{mid}{right}")
    if variant_id == "ratio_colon_form":
        inner = f"{seg_left}:{seg_right}={m}:{n}"
    elif variant_id == "multiple_form":
        inner = f"{seg_left}={m}{seg_right}"
    elif variant_id == "linear_relation_form":
        inner = f"{m}{seg_left}={n}{seg_right}"
    else:
        inner = f"{seg_left}:{seg_right}={m}:{n}"
    return f"${inner}$"


def _on_segment_phrase(point: str, a: str, b: str) -> str:
    return f"{point} 在線段 {_overline_segment(a, b)} 上"


def _assert_core_answer_matches_generation_context(core: dict[str, Any]) -> None:
    """Ensure question_text coords/ratio and correct_answer share one sampled context."""
    meta = core.get("metadata") if isinstance(core.get("metadata"), dict) else {}
    gcoords = meta.get("generation_coords") if isinstance(meta.get("generation_coords"), dict) else {}
    answer = str(core.get("answer", "")).strip()
    ratio = _parse_ratio_values(str(meta.get("ratio_values", "")))
    a_raw = gcoords.get("A")
    b_raw = gcoords.get("B")
    if not ratio or not isinstance(a_raw, (list, tuple)) or not isinstance(b_raw, (list, tuple)):
        return
    if len(a_raw) != 2 or len(b_raw) != 2:
        return
    ax, ay, bx, by = int(a_raw[0]), int(a_raw[1]), int(b_raw[0]), int(b_raw[1])
    m, n = ratio
    px, py = _internal_point(ax, ay, bx, by, m, n)
    expected = _fmt_pair(px, py)
    if _coord_dedupe_key(expected) != _coord_dedupe_key(answer):
        raise RuntimeError(
            f"division_point_answer_context_mismatch:expected={expected} actual={answer}"
        )


def _resolve_forward_coordinate_target_task(spec: dict[str, Any]) -> str:
    """Point-on-segment coordinate problems use internal division, not ratio-reverse / dual-x."""
    target = str(spec.get("target_task", "")).strip()
    if target != "solve_point_from_section_ratio":
        return target
    ac = get_answer_contract(spec)
    at = str(ac.get("answer_type", "")).strip()
    shape = str(ac.get("answer_shape", "")).strip()
    if at in {"ordered_pair", "coordinate_pair", "single_choice"} or shape == "coordinate_pair":
        return "compute_internal_division_point_coordinates"
    if answer_type_family(at) == "coordinate_pair":
        return "compute_internal_division_point_coordinates"
    return target


def _resolve_presentation_mode(spec: dict[str, Any], ac: dict[str, Any]) -> str:
    pm = str(ac.get("presentation_mode", "")).strip().lower()
    if pm in {"single_choice", "short_answer"}:
        return pm
    raw_type = str(ac.get("answer_type", "")).strip().lower()
    if raw_type == "single_choice" or str(ac.get("answer_shape", "")).strip() == "choice_label":
        return "single_choice"
    if answer_type_family(raw_type) == "single_choice":
        return "single_choice"
    return "short_answer"


def _parse_ratio_values(ratio_values: str) -> tuple[int, int] | None:
    m = re.match(r"^\s*(\d+)\s*:\s*(\d+)\s*$", str(ratio_values or "").strip())
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def _coord_dedupe_key(text: str) -> str | None:
    parsed = parse_coordinate_pair_answer(text)
    if parsed is None:
        return str(text).strip() or None
    return f"{parsed[0]:.6g},{parsed[1]:.6g}"


def _coords_snapshot(coords: dict[str, Any]) -> dict[str, Any]:
    snap: dict[str, Any] = {}
    for key, val in coords.items():
        if isinstance(val, tuple) and len(val) == 2:
            fx, fy = _to_float_pair(val[0], val[1])
            snap[key] = [fx, fy]
        else:
            snap[key] = val
    return snap


def _wrong_internal_swap(ax: int, ay: int, bx: int, by: int, m: int, n: int) -> tuple[Fraction, Fraction]:
    den = m + n
    return Fraction(m * ax + n * bx, den), Fraction(m * ay + n * by, den)


def _external_division_point(ax: int, ay: int, bx: int, by: int, m: int, n: int) -> tuple[Fraction, Fraction] | None:
    if n == m:
        return None
    return Fraction(n * ax - m * bx, n - m), Fraction(n * ay - m * by, n - m)


def _make_coordinate_distractors(
    rng: random.Random,
    correct_value: str,
    core: dict[str, Any],
    spec: dict[str, Any],
) -> list[str]:
    correct_key = _coord_dedupe_key(correct_value)
    seen: set[str] = set()
    if correct_key:
        seen.add(correct_key)
    candidates: list[str] = []

    def _try_add(x: float | Fraction | int, y: float | Fraction | int) -> None:
        text = _fmt_pair(x, y)
        key = _coord_dedupe_key(text)
        if not key or key in seen:
            return
        seen.add(key)
        candidates.append(text)

    meta = core.get("metadata") if isinstance(core.get("metadata"), dict) else {}
    gcoords = meta.get("generation_coords") if isinstance(meta.get("generation_coords"), dict) else {}
    ratio = _parse_ratio_values(str(meta.get("ratio_values", "")))
    target = str(spec.get("target_task", "")).strip()

    a_raw = gcoords.get("A")
    b_raw = gcoords.get("B")
    if isinstance(a_raw, (list, tuple)) and len(a_raw) == 2 and isinstance(b_raw, (list, tuple)) and len(b_raw) == 2:
        ax, ay = int(a_raw[0]), int(a_raw[1])
        bx, by = int(b_raw[0]), int(b_raw[1])
        if ratio and target in {"compute_internal_division_point_coordinates", "solve_point_from_section_ratio"}:
            m, n = ratio
            wx, wy = _wrong_internal_swap(ax, ay, bx, by, m, n)
            _try_add(wx, wy)
            ext = _external_division_point(ax, ay, bx, by, m, n)
            if ext:
                _try_add(ext[0], ext[1])
            _try_add(Fraction(ax + bx, 2), Fraction(ay + by, 2))
        elif target == "compute_midpoint_coordinates":
            _try_add(ax, ay)
            _try_add(bx, by)
        elif target == "compute_centroid_coordinates":
            c_raw = gcoords.get("C")
            if isinstance(c_raw, (list, tuple)) and len(c_raw) == 2:
                cx, cy = int(c_raw[0]), int(c_raw[1])
                _try_add(Fraction(ax + bx, 2), Fraction(ay + by, 2))
                _try_add(Fraction(ax + cx, 2), Fraction(ay + cy, 2))
                _try_add(ax, ay)

    parsed = parse_coordinate_pair_answer(correct_value)
    if parsed:
        cx, cy = parsed
        _try_add(cx + 1, cy)
        _try_add(cx, cy + 1)
        _try_add(cy, cx)

    for _ in range(60):
        if len(candidates) >= 3:
            break
        if not parsed:
            break
        ox = parsed[0] + rng.randint(-6, 6)
        oy = parsed[1] + rng.randint(-6, 6)
        if ox == parsed[0] and oy == parsed[1]:
            continue
        _try_add(ox, oy)

    if len(candidates) < 3:
        raise RuntimeError("coordinate_single_choice_distractor_generation_failed")
    return candidates[:3]


def _build_division_point_single_choice_payload(
    skill_id: str,
    problem_type_id: str,
    spec: dict[str, Any],
    core: dict[str, Any],
    ac: dict[str, Any],
    rng: random.Random,
) -> dict[str, Any]:
    correct_value = str(core.get("answer", "")).strip()
    distractors = _make_coordinate_distractors(rng, correct_value, core, spec)
    option_pool = [{"is_correct": True, "text": correct_value}] + [
        {"is_correct": False, "text": text} for text in distractors
    ]
    rng.shuffle(option_pool)
    choices: list[dict[str, str]] = []
    answer_label = "A"
    for idx, opt in enumerate(option_pool):
        label = chr(ord("A") + idx)
        text = str(opt.get("text", ""))
        choices.append({"label": label, "text": text, "value": text})
        if opt.get("is_correct"):
            answer_label = label

    ac_out = dict(ac)
    coerce_single_choice_contract(ac_out)
    ac_out.setdefault("semantic_answer_shape", "coordinate_pair")
    checker = str(ac_out.get("checker", "choice_label_checker")).strip() or "choice_label_checker"
    eq = str(ac_out.get("answer_equivalence", ac_out.get("equivalence_type", "choice_label"))).strip() or "choice_label"
    meta = dict(core.get("metadata") or {})
    meta["presentation_mode"] = "single_choice"
    meta["semantic_answer"] = correct_value

    return {
        "skill_id": skill_id,
        "problem_type_id": problem_type_id,
        "question_text": core["question_text"],
        "question": core["question_text"],
        "choices": choices,
        "options": [str(c["text"]) for c in choices],
        "answer": answer_label,
        "correct_answer": answer_label,
        "correct_value": correct_value,
        "answer_type": "single_choice",
        "checker_type": checker,
        "explanation": core["explanation"],
        "diagnosis_tags": [
            "division_point_coordinates",
            str(spec.get("target_task", "")),
            f"template_{core.get('template_variant', '')}",
        ],
        "metadata": meta,
        "answer_contract": ac_out,
        "checker": checker,
        "equivalence": eq,
        "source": "gencode_slot_generator",
    }


def _to_float_pair(x: float | Fraction | int, y: float | Fraction | int) -> tuple[float, float]:
    fx = float(x) if not isinstance(x, Fraction) else float(x.numerator) / float(x.denominator)
    fy = float(y) if not isinstance(y, Fraction) else float(y.numerator) / float(y.denominator)
    return fx, fy


def _internal_point(ax: int, ay: int, bx: int, by: int, m: int, n: int) -> tuple[Fraction, Fraction]:
    den = m + n
    px = Fraction(n * ax + m * bx, den)
    py = Fraction(n * ay + m * by, den)
    return px, py


def _gen_ab_for_internal_integer(
    rng: random.Random,
    bounds: tuple[int, int, int, int],
    m: int,
    n: int,
    *,
    rational_ok: bool,
) -> tuple[int, int, int, int, Fraction, Fraction] | None:
    xmin, xmax, ymin, ymax = bounds
    den = m + n
    cr = {"exclude_zero_probability": 0.15}
    for _ in range(150):
        px = _rand_int(rng, xmin, xmax)
        py = _rand_int(rng, ymin, ymax)
        ax = _rand_int(rng, xmin, xmax)
        ay = _rand_int(rng, ymin, ymax)
        bx_num = den * px - n * ax
        by_num = den * py - n * ay
        if bx_num % m != 0 or by_num % m != 0:
            continue
        bx, by = bx_num // m, by_num // m
        if (ax, ay) == (bx, by):
            continue
        pxf, pyf = Fraction(px, 1), Fraction(py, 1)
        if not rational_ok and (pxf.denominator != 1 or pyf.denominator != 1):
            continue
        return ax, ay, bx, by, pxf, pyf
    return None


def _gen_internal_stem(
    variant_id: str,
    names: list[str],
    ax: int,
    ay: int,
    bx: int,
    by: int,
    px: Fraction,
    py: Fraction,
    m: int,
    n: int,
) -> tuple[str, str]:
    a, b, p = names[0], names[1], names[2]
    ans = _fmt_pair(px, py)
    seg = _on_segment_phrase(p, a, b)
    if variant_id == "word_context_form":
        k = max(m, n) // max(1, min(m, n))
        q = (
            f"平面上甲地坐標為 {a}({ax},{ay})，乙地坐標為 {b}({bx},{by})。"
            f"某點在 {_overline_segment(a, b)} 上，且到甲地距離是到乙地距離的 {k} 倍，求該點坐標。"
        )
    else:
        rel = _ratio_relation_latex(variant_id, a, p, b, m, n)
        q = f"已知 {a}({ax},{ay})、{b}({bx},{by})，{seg}，且 {rel}，求 {p} 坐標。"
    expl = (
        f"內分點公式：{p}=(({n}·{a}+{m}·{b})/({m}+{n}))，"
        f"得 {p}={ans}。"
    )
    return q, expl


def _gen_section_ratio(spec: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    gc = _gc(spec)
    schema = _schema(gc)
    variant = _weighted_variant(rng, _enabled_variants(gc))
    vid = str(variant.get("id", "ratio_colon_form"))
    names = _pick_names(rng, schema, ["A", "B", "C"])
    m, n = _pick_ratio(rng, schema)
    rational = "rational" in _answer_mode(rng, schema)
    bounds = _coord_bounds(schema)
    row = _gen_ab_for_internal_integer(rng, bounds, m, n, rational_ok=rational)
    if row is None:
        raise RuntimeError("section_ratio_generation_failed")
    ax, ay, bx, by, px, py = row
    a, b, c = names[0], names[1], names[2]
    ans = _fmt_pair(px, py)
    seg = _on_segment_phrase(c, a, b)
    if vid == "word_context_form":
        k = max(m, n) // max(1, min(m, n))
        q = (
            f"已知 {a}({ax},{ay})、{b}({bx},{by})，"
            f"某點在 {_overline_segment(a, b)} 上，且到 {a} 距離是到 {b} 距離的 {k} 倍，求 {c} 坐標。"
        )
    else:
        rel = _ratio_relation_latex(vid, a, c, b, m, n)
        q = f"已知 {a}({ax},{ay})、{b}({bx},{by})，{seg}，且 {rel}，求 {c} 坐標。"
    expl = f"由內分點公式，{c}=(({n}·{a}+{m}·{b})/({m}+{n}))={ans}。"
    return _pack(
        spec,
        q,
        ans,
        expl,
        template_variant=vid,
        ratio_form=f"{a}{c}:{c}{b}={m}:{n}",
        ratio_values=f"{m}:{n}",
        point_names=names,
        coords={"A": (ax, ay), "B": (bx, by), "target": _to_float_pair(px, py)},
    )


def _gen_internal_division(spec: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    gc = _gc(spec)
    schema = _schema(gc)
    variant = _weighted_variant(rng, _enabled_variants(gc))
    vid = str(variant.get("id", "ratio_colon_form"))
    names = _pick_names(rng, schema, ["A", "B", "P"])
    m, n = _pick_ratio(rng, schema)
    rational = "rational" in _answer_mode(rng, schema)
    bounds = _coord_bounds(schema)
    row = _gen_ab_for_internal_integer(rng, bounds, m, n, rational_ok=rational)
    if row is None:
        raise RuntimeError("internal_division_generation_failed")
    ax, ay, bx, by, px, py = row
    q, expl = _gen_internal_stem(vid, names, ax, ay, bx, by, px, py, m, n)
    ratio_form = {"ratio_colon_form": f"AP:PB={m}:{n}", "multiple_form": f"AP={m}PB", "linear_relation_form": f"{m}AP={n}PB"}.get(
        vid, f"AP:PB={m}:{n}"
    )
    return _pack(
        spec,
        q,
        _fmt_pair(px, py),
        expl,
        template_variant=vid,
        ratio_form=ratio_form,
        ratio_values=f"{m}:{n}",
        point_names=names,
        coords={"A": (ax, ay), "B": (bx, by), "P": _to_float_pair(px, py)},
    )


def _gen_centroid(spec: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    gc = _gc(spec)
    schema = _schema(gc)
    variant = _weighted_variant(rng, _enabled_variants(gc))
    vid = str(variant.get("id", "direct_triangle_centroid"))
    names = _pick_names(rng, schema, ["A", "B", "C"])
    xmin, xmax, ymin, ymax = _coord_bounds(schema)
    rational = "rational" in _answer_mode(rng, schema)

    if vid == "missing_vertex_from_centroid":
        for _ in range(150):
            ax = _rand_int(rng, xmin, xmax)
            ay = _rand_int(rng, ymin, ymax)
            bx = _rand_int(rng, xmin, xmax)
            by = _rand_int(rng, ymin, ymax)
            gx = _rand_int(rng, xmin, xmax)
            gy = _rand_int(rng, ymin, ymax)
            cx, cy = 3 * gx - ax - bx, 3 * gy - ay - by
            if abs(cx) > max(abs(xmin), abs(xmax)) * 2 or abs(cy) > max(abs(ymin), abs(ymax)) * 2:
                continue
            if (cx, cy) == (ax, ay) or (cx, cy) == (bx, by):
                continue
            if not rational and (cx % 3 != 0 or cy % 3 != 0):
                continue
            ans = _fmt_pair(cx, cy)
            q = f"已知 {names[0]}({ax},{ay})、{names[1]}({bx},{by}) 與重心 G({gx},{gy})，求 {names[2]} 坐標。"
            expl = f"重心 {names[2]}=((A+B+G)/3) 反推：{names[2]}=3G-A-B={ans}。"
            return _pack(
                spec,
                q,
                ans,
                expl,
                template_variant=vid,
                ratio_form="centroid_missing_vertex",
                ratio_values="n/a",
                point_names=names,
                coords={"G": (gx, gy), "target": (float(cx), float(cy))},
            )

    for _ in range(150):
        coords = [
            (_rand_int(rng, xmin, xmax), _rand_int(rng, ymin, ymax)),
            (_rand_int(rng, xmin, xmax), _rand_int(rng, ymin, ymax)),
            (_rand_int(rng, xmin, xmax), _rand_int(rng, ymin, ymax)),
        ]
        if len({c for c in coords}) < 3:
            continue
        sx = sum(c[0] for c in coords)
        sy = sum(c[1] for c in coords)
        if sx % 3 != 0 or sy % 3 != 0:
            if rational:
                gx, gy = Fraction(sx, 3), Fraction(sy, 3)
            else:
                continue
        else:
            gx, gy = Fraction(sx, 3), Fraction(sy, 3)
        if not rational and (gx.denominator != 1 or gy.denominator != 1):
            continue
        a, b, c = names
        (ax, ay), (bx, by), (cx, cy) = coords
        ans = _fmt_pair(gx, gy)
        if vid == "worded_triangle_centroid":
            q = (
                f"三角形頂點 {a}({ax},{ay})、{b}({bx},{by})、{c}({cx},{cy})，"
                f"求此三角形重心坐標。"
            )
        else:
            q = f"已知 {a}({ax},{ay})、{b}({bx},{by})、{c}({cx},{cy})，求 △{a}{b}{c} 重心坐標。"
        expl = f"重心 G=(({ax}+{bx}+{cx})/3, ({ay}+{by}+{cy})/3)={ans}。"
        return _pack(
            spec,
            q,
            ans,
            expl,
            template_variant=vid,
            ratio_form="centroid",
            ratio_values="n/a",
            point_names=names,
            coords={"A": coords[0], "B": coords[1], "C": coords[2], "G": _to_float_pair(gx, gy)},
        )
    raise RuntimeError("centroid_generation_failed")


def _gen_midpoint(spec: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    gc = _gc(spec)
    schema = _schema(gc)
    variant = _weighted_variant(rng, _enabled_variants(gc))
    vid = str(variant.get("id", "direct_midpoint"))
    names = _pick_names(rng, schema, ["A", "B", "M"])
    xmin, xmax, ymin, ymax = _coord_bounds(schema)
    rational = "rational" in _answer_mode(rng, schema)

    if vid == "missing_endpoint_from_midpoint":
        for _ in range(150):
            ax = _rand_int(rng, xmin, xmax)
            ay = _rand_int(rng, ymin, ymax)
            mx = _rand_int(rng, xmin, xmax)
            my = _rand_int(rng, ymin, ymax)
            bx, by = 2 * mx - ax, 2 * my - ay
            if abs(bx) > max(abs(xmin), abs(xmax)) * 2 or abs(by) > max(abs(ymin), abs(ymax)) * 2:
                continue
            if (ax, ay) == (bx, by):
                continue
            ans = _fmt_pair(bx, by)
            q = f"已知 {names[0]}({ax},{ay}) 與中點 {names[2]}({mx},{my})，求 {names[1]} 坐標。"
            expl = f"中點公式反推：{names[1]}=2{names[2]}-{names[0]}={ans}。"
            return _pack(
                spec,
                q,
                ans,
                expl,
                template_variant=vid,
                ratio_form="midpoint_missing_endpoint",
                ratio_values="1:1",
                point_names=names,
                coords={"A": (ax, ay), "M": (mx, my), "target": (float(bx), float(by))},
            )

    for _ in range(150):
        ax = _rand_int(rng, xmin, xmax)
        ay = _rand_int(rng, ymin, ymax)
        bx = _rand_int(rng, xmin, xmax)
        by = _rand_int(rng, ymin, ymax)
        if (ax, ay) == (bx, by):
            continue
        if rational:
            mx, my = Fraction(ax + bx, 2), Fraction(ay + by, 2)
        else:
            if (ax + bx) % 2 != 0 or (ay + by) % 2 != 0:
                continue
            mx, my = Fraction(ax + bx, 2), Fraction(ay + by, 2)
        a, b, m = names[0], names[1], names[2] if len(names) > 2 else "M"
        ans = _fmt_pair(mx, my)
        if vid == "word_context_midpoint":
            q = f"平面上兩點 {a}({ax},{ay}) 與 {b}({bx},{by})，其中點為 {m}，求 {m} 坐標。"
        else:
            q = f"求 {a}({ax},{ay}) 與 {b}({bx},{by}) 的中點坐標。"
        expl = f"中點 {m}=(({ax}+{bx})/2, ({ay}+{by})/2)={ans}。"
        return _pack(
            spec,
            q,
            ans,
            expl,
            template_variant=vid,
            ratio_form="midpoint",
            ratio_values="1:1",
            point_names=names,
            coords={"A": (ax, ay), "B": (bx, by), "M": _to_float_pair(mx, my)},
        )
    raise RuntimeError("midpoint_generation_failed")


def _pack(
    spec: dict[str, Any],
    question_text: str,
    answer: str,
    explanation: str,
    *,
    template_variant: str,
    ratio_form: str,
    ratio_values: str,
    point_names: list[str],
    coords: dict[str, Any],
) -> dict[str, Any]:
    ac = get_answer_contract(spec)
    gc = _gc(spec)
    sign = "++"
    if coords:
        tgt = coords.get("target") or coords.get("P") or coords.get("G") or coords.get("M")
        if isinstance(tgt, tuple) and len(tgt) == 2:
            tx, ty = tgt
            sign = ("+" if tx >= 0 else "-") + ("+" if ty >= 0 else "-")
    meta = {
        "givens": [str(k) for k in coords.keys() if k != "target"],
        "target": answer,
        "derivation": [explanation],
        "template_variant": template_variant,
        "template_id": template_variant,
        "ratio_form": ratio_form,
        "ratio_values": ratio_values,
        "coordinate_pattern": sign,
        "point_names": list(point_names),
        "generation_coords": _coords_snapshot(coords),
        "generator_contract": {
            "sampling_strategy": gc.get("sampling_strategy", "weighted_random"),
            "template_variant": template_variant,
        },
    }
    return {
        "question_text": question_text,
        "answer": answer,
        "correct_answer": answer,
        "explanation": explanation,
        "template_variant": template_variant,
        "ratio_form": ratio_form,
        "ratio_values": ratio_values,
        "coordinate_pattern": sign,
        "point_names": list(point_names),
        "metadata": meta,
        "answer_contract": dict(ac),
        "checker": str(ac.get("checker", "coordinate_pair_checker")),
        "equivalence": str(ac.get("answer_equivalence", ac.get("equivalence_type", "coordinate_pair_equivalence"))),
    }


def generate_division_point_payload(
    skill_id: str,
    problem_type_id: str,
    spec: dict[str, Any],
    seed: int | None,
) -> dict[str, Any]:
    """Generate one problem payload from spec.generator_contract."""
    target = _resolve_forward_coordinate_target_task(spec)
    rng = _rng(seed, problem_type_id)
    if target == "compute_centroid_coordinates":
        core = _gen_centroid(spec, rng)
    elif target == "compute_midpoint_coordinates":
        core = _gen_midpoint(spec, rng)
    elif target == "solve_point_from_section_ratio":
        core = _gen_section_ratio(spec, rng)
    else:
        core = _gen_internal_division(spec, rng)

    _assert_core_answer_matches_generation_context(core)

    ac = get_answer_contract(spec)
    presentation = _resolve_presentation_mode(spec, ac)
    if presentation == "single_choice":
        return _build_division_point_single_choice_payload(skill_id, problem_type_id, spec, core, ac, rng)

    at = str(ac.get("answer_type", "ordered_pair")).strip() or "ordered_pair"
    checker = str(ac.get("checker", "coordinate_pair_checker")).strip() or "coordinate_pair_checker"
    eq = str(ac.get("answer_equivalence", ac.get("equivalence_type", "coordinate_pair_equivalence"))).strip()
    meta = dict(core.get("metadata") or {})
    meta.setdefault("presentation_mode", "short_answer")
    return {
        "skill_id": skill_id,
        "problem_type_id": problem_type_id,
        "question_text": core["question_text"],
        "question": core["question_text"],
        "choices": [],
        "answer": core["answer"],
        "correct_answer": core["correct_answer"],
        "answer_type": at,
        "checker_type": checker,
        "explanation": core["explanation"],
        "diagnosis_tags": [
            "division_point_coordinates",
            str(spec.get("target_task", "")),
            f"template_{core.get('template_variant', '')}",
        ],
        "metadata": meta,
        "answer_contract": dict(ac),
        "checker": checker,
        "equivalence": eq,
        "source": "gencode_slot_generator",
    }
