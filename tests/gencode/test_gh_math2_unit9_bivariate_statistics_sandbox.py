"""Sandbox gate for 普高數學2 Unit 9（二維數據分析）.

Every VERIFIED component is sampled on seeds 0-19. Answers are re-derived by an oracle in this file that does
not import the domain module. Deferred figure-only IDs are skipped.
"""

from __future__ import annotations

import importlib.util
import json
import math
import re
import sqlite3
from decimal import ROUND_HALF_UP, Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path

import pytest

from agent_domains_candidate.bivariate_statistics import build_sandbox as B
from agent_domains_candidate.bivariate_statistics.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.bivariate_statistics.bivariate_statistics_domain import DOMAIN_KEY
from agent_domains_candidate.bivariate_statistics.bivariate_statistics_specs import (
    COMPONENTS,
    DEFERRED_COMPONENTS,
    RETAINED_DEFERRED_COMPONENTS,
    RETAINED_DEFERRED_SOURCES,
    FAMILY,
    FIXED_CONCEPT,
    FIXED_ROWS,
    OP,
    SKILL_OPERATIONS,
    SKILLS,
    VISUAL_CAPABILITY_GAP,
)
from agent_domains_candidate.bivariate_statistics.verification import grade, parts_of, verify_payload, wrong_value

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = B.DRYRUN
FORMAL_DB = PROJECT_ROOT / "instance" / "kumon_math.db"
SEEDS = range(20)
UNIT_IDS = set(range(12947, 12973))
VERIFIED = sorted(set(COMPONENTS) - VISUAL_CAPABILITY_GAP)

register_candidate_in_memory()
B.build_all()


def _skill_of(cid: int) -> str:
    return SKILLS[COMPONENTS[cid][0]]


_MODULES: dict[int, object] = {}


def _gen(cid: int, seed: int = 0) -> dict:
    if cid not in _MODULES:
        path = DRYRUN / _skill_of(cid) / "components" / f"src_{cid}" / "generate.py"
        spec = importlib.util.spec_from_file_location(f"m2u9_{cid}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[cid] = module
    return _MODULES[cid].generate(seed=seed)


def _values(payload: dict) -> list:
    answer = payload["correct_answer"]
    if isinstance(answer, dict):
        return [answer[key] for key in sorted(answer, key=lambda item: int(item.split("_")[1]))]
    return [answer]


# --- independent oracle (does NOT import bivariate_statistics_domain) -------------------------------------------------


def _fs(values) -> list[F]:
    return [F(str(v)) for v in values]


def _stats(xs: list[F], ys: list[F]) -> tuple[F, F, F, F, F]:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return mx, my, sxx, syy, sxy


def _sqrt_exact(f: F) -> F:
    sn, sd = math.isqrt(f.numerator), math.isqrt(f.denominator)
    assert sn * sn == f.numerator and sd * sd == f.denominator
    return F(sn, sd)


def _r_exact(xs, ys) -> F:
    _mx, _my, sxx, syy, sxy = _stats(_fs(xs), _fs(ys))
    if sxy == 0:
        return F(0)
    return sxy / _sqrt_exact(sxx * syy)


def _signed_sq(xs, ys) -> F:
    _mx, _my, sxx, syy, sxy = _stats(_fs(xs), _fs(ys))
    sign = (sxy > 0) - (sxy < 0)
    return sign * sxy * sxy / (sxx * syy)


def _round_hu(f: F, places: int) -> F:
    with localcontext() as ctx:
        ctx.prec = 60
        d = (Decimal(f.numerator) / Decimal(f.denominator)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
    return F(str(d))


def _r_rounded(xs, ys, places: int) -> F:
    _mx, _my, sxx, syy, sxy = _stats(_fs(xs), _fs(ys))
    with localcontext() as ctx:
        ctx.prec = 60
        r = (Decimal(sxy.numerator) / Decimal(sxy.denominator)) / (
            (Decimal(sxx.numerator) / Decimal(sxx.denominator)).sqrt()
            * (Decimal(syy.numerator) / Decimal(syy.denominator)).sqrt()
        )
        return F(str(r.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)))


def _line(xs, ys) -> tuple[F, F]:
    mx, my, sxx, _syy, sxy = _stats(_fs(xs), _fs(ys))
    m = sxy / sxx
    return m, my - m * mx


def _general(m: F, b: F) -> str:
    d = math.lcm(m.denominator, b.denominator)
    a_, b_, c_ = -int(m * d), d, -int(b * d)
    g = math.gcd(math.gcd(abs(a_), abs(b_)), abs(c_)) or 1
    a_, b_, c_ = a_ // g, b_ // g, c_ // g

    def coef(v: int) -> str:
        return {1: "", -1: "-"}.get(v, str(v))

    text = ""
    if a_:
        text += f"{coef(a_)}x"
    text += ("+" if text and b_ > 0 else "") + f"{coef(b_)}y"
    if c_:
        text += ("+" if c_ > 0 else "") + str(c_)
    return text + "=0"


def _claim_truth(c: dict) -> bool:
    kind = c["kind"]
    if kind == "points_vs_correlation":
        return c["stated"] == "unrelated"
    if kind == "slope_sign":
        return c["r_rel"] == c["m_rel"]
    if kind == "slope_sigma":
        return F(str(c["k"])) == F(str(c["c"]))
    if kind == "r_range":
        lo, hi = F(str(c["lo"])), F(str(c["hi"]))
        lo_ok = lo < -1 or (c["lo_closed"] and lo == -1)
        hi_ok = 1 < hi or (c["hi_closed"] and hi == 1)
        # need -1,0,1 all inside
        def inside(v):
            left = lo < v or (c["lo_closed"] and lo == v)
            right = v < hi or (c["hi_closed"] and hi == v)
            return left and right
        return all(inside(v) for v in (F(-1), F(0), F(1)))
    if kind == "points_on_line":
        a = F(str(c["a"]))
        return F(str(c["stated"])) == ((a > 0) - (a < 0))
    raise AssertionError(kind)


def _stmt_truth(st: dict, mx: F, my: F, r: F, px: F, py: F) -> bool:
    m = (py - my) / (px - mx)
    kind = st["kind"]
    if kind == "passes_point":
        return F(str(st["y"])) == my + m * (F(str(st["x"])) - mx)
    if kind == "slope_is":
        return F(str(st["stated"])) == m
    if kind == "sigma_less":
        ratio = r / m  # σx/σy
        sx_less = ratio < 1
        return sx_less if st["first"] == "x" else not sx_less
    raise AssertionError(kind)


def _oracle_check(op: str, g: dict, payload: dict) -> None:
    got = _values(payload)
    if op == "correlation_from_table":
        assert F(got[0]) == _r_exact(g["x"], g["y"])
    elif op == "correlation_remove_point":
        scores = []
        xs, ys = _fs(g["x"]), _fs(g["y"])
        for i in range(len(xs)):
            scores.append(_signed_sq(xs[:i] + xs[i + 1 :], ys[:i] + ys[i + 1 :]))
        best = scores.index(max(scores))
        assert got[0] == str(g["labels"][best])
    elif op == "correlation_change_add_point":
        before = _signed_sq(g["x"], g["y"])
        after = _signed_sq(list(g["x"]) + [g["new_point"][0]], list(g["y"]) + [g["new_point"][1]])
        assert got[0] == ("A" if after > before else "B")
    elif op == "correlation_rescale":
        assert [F(a) for a in got] == [F(str(g["r"])), F(1)]
    elif op == "regression_from_summary":
        m = F(str(g["r"])) * F(str(g["sy"])) / F(str(g["sx"]))
        b = F(str(g["my"])) - m * F(str(g["mx"]))
        assert got[0] == _general(m, b)
    elif op == "regression_from_table":
        m, b = _line(g["x"], g["y"])
        assert got[0] == _general(m, b)
        assert F(got[1]) == m * F(str(g["x0"])) + b
    elif op == "regression_rounded_from_table":
        m, b = _line(g["x"], g["y"])
        assert F(got[0]) == _r_rounded(g["x"], g["y"], int(g["r_places"]))
        assert F(got[1]) == _round_hu(m, int(g["coef_places"]))
        assert F(got[2]) == _round_hu(b, int(g["coef_places"]))
    elif op == "regression_predict_given_line":
        y0 = F(str(g["m_r"])) * F(str(g["x0"])) + F(str(g["b_r"]))
        assert F(got[0]) == _round_hu(y0, int(g["places"]))
    elif op == "correlation_from_regression_point":
        px, py = F(str(g["point"][0])), F(str(g["point"][1]))
        m = (py - F(str(g["my"]))) / (px - F(str(g["mx"])))
        assert F(got[0]) == m * F(str(g["sx"])) / F(str(g["sy"]))
    elif op == "regression_line_unknown_intercept":
        a = F(str(g["slope"]))
        k = F(str(g["my"])) - a * F(str(g["mx"]))
        r = a * F(str(g["sx"])) / F(str(g["sy"]))
        assert [F(v) for v in got] == [k, r]
    elif op == "regression_statement_selection":
        mx, my, r = F(str(g["mx"])), F(str(g["my"])), F(str(g["r"]))
        px, py = F(str(g["line_point"][0])), F(str(g["line_point"][1]))
        truth = [_stmt_truth(st, mx, my, r, px, py) for st in g["statements"]]
        assert got[0] == [str(i) for i, t in enumerate(truth, 1) if t]
    elif op == "true_false_bivariate":
        assert got[0] == ("A" if _claim_truth(g["claim"]) else "B")
    else:
        raise AssertionError(f"no oracle for {op}")


# --- stem ↔ givens ----------------------------------------------------------------------------------------------------

_NUM = re.compile(r"\\frac\{(\d+)\}\{(\d+)\}|(-?\d+(?:\.\d+)?)")


def _stem_numbers(text: str) -> set[F]:
    out: set[F] = set()
    for m in _NUM.finditer(text.replace("−", "-")):
        if m.group(1):
            out.add(F(int(m.group(1)), int(m.group(2))))
        else:
            out.add(F(m.group(3)))
    return out


_NOT_PRINTED = {
    "kind", "scene", "r_rel", "m_rel", "lo_closed", "hi_closed", "eq_places", "places",
    "r_places", "coef_places", "first", "second", "ids",
}


def _appears(value: F, shown: set[F]) -> bool:
    """Accept the signed value, its absolute value, or a terminating-decimal twin."""
    if value in shown or -value in shown or abs(value) in shown:
        return True
    if value.denominator == 1:
        return False
    # e.g. stem prints -0.8 while givens store -4/5
    try:
        text = format(Decimal(value.numerator) / Decimal(value.denominator), "f").rstrip("0").rstrip(".")
        return F(text) in shown or abs(F(text)) in shown
    except Exception:
        return False


def _given_numbers(op: str, g: dict) -> list[F]:
    """Numeric values that must appear in the student-facing stem (signs optional)."""
    out: list[F] = []
    claim = g.get("claim") if isinstance(g.get("claim"), dict) else None

    def walk(key, value):
        if key in _NOT_PRINTED or isinstance(value, bool):
            return
        if isinstance(value, dict):
            for k, v in value.items():
                walk(k, v)
            return
        if isinstance(value, list):
            for v in value:
                walk(key, v)
            return
        try:
            f = F(str(value))
        except (ValueError, ZeroDivisionError):
            return
        if f == 0 and key not in ("b", "stated", "r", "slope"):
            return
        out.append(f)

    # true/false wording may hide k=c=1 ("標準差相等") or only print the line / stated r
    if op == "true_false_bivariate" and claim:
        kind = claim["kind"]
        if kind == "points_vs_correlation":
            return []
        if kind == "slope_sign":
            return []
        if kind == "slope_sigma":
            k, c = F(str(claim["k"])), F(str(claim["c"]))
            if k == 1 and c == 1:
                return []  # textbook wording: 標準差相等…斜率也相等
            if k == 1:
                return [c]  # 「標準差相等」略去 k=1，只印倍數 c
            return [k, c]
        if kind == "r_range":
            return [F(str(claim["lo"])), F(str(claim["hi"]))]
        if kind == "points_on_line":
            vals = [F(str(claim["a"])), F(str(claim["stated"]))]
            b = F(str(claim["b"]))
            if b != 0:
                vals.append(b)  # b=0 is omitted from y=ax
            return vals

    for k, v in g.items():
        if op == "regression_from_table" and k == "x0" and g.get("scene") == "price_demand":
            out.append(F(str(v)) * 1000)  # stem prints 元, not 千元
            continue
        walk(k, v)
    return out


# --- tests ------------------------------------------------------------------------------------------------------------


def test_component_coverage_matches_unit9_plan():
    assert VISUAL_CAPABILITY_GAP == frozenset({12947, 12948, 12954, 12960, 12963})
    assert set(DEFERRED_COMPONENTS) == VISUAL_CAPABILITY_GAP
    assert set(COMPONENTS) | VISUAL_CAPABILITY_GAP == UNIT_IDS
    assert set(COMPONENTS).isdisjoint(VISUAL_CAPABILITY_GAP)
    assert set(FAMILY) == set(COMPONENTS)
    assert RETAINED_DEFERRED_COMPONENTS <= VISUAL_CAPABILITY_GAP
    assert set(RETAINED_DEFERRED_SOURCES) == RETAINED_DEFERRED_COMPONENTS
    assert not FIXED_ROWS
    assert FIXED_CONCEPT <= set(COMPONENTS)
    assert len(COMPONENTS) == 21
    for ops in SKILL_OPERATIONS.values():
        assert set(ops) <= set(OP)
    assert "scatter" not in SKILL_OPERATIONS


def test_formal_db_binding_readonly():
    con = sqlite3.connect(f"file:{FORMAL_DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "select id, skill_id from textbook_examples where source_curriculum='general' "
            "and source_volume='數學2' and source_chapter like '%單元9%' order by id"
        ).fetchall()
    finally:
        con.close()
    assert [r[0] for r in rows] == sorted(UNIT_IDS)
    by_id = {cid: SKILLS[COMPONENTS[cid][0]] for cid in COMPONENTS}
    for tid, skill in rows:
        if tid in VISUAL_CAPABILITY_GAP:
            continue
        assert by_id[tid] == skill


@pytest.mark.parametrize("cid", VERIFIED)
def test_verified_component_seeds_0_19(cid: int):
    skill_id = _skill_of(cid)
    operation = OP[COMPONENTS[cid][1]]
    directory = DRYRUN / skill_id / "components" / f"src_{cid}"
    assert {path.name for path in directory.iterdir() if path.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    for seed in SEEDS:
        payload = _gen(cid, seed)
        assert payload["domain_operation"] == operation and payload["fixed_domain_key"] == DOMAIN_KEY
        assert not payload["answer_contract"].get("answer_format_example")
        assert verify_payload(payload, skill_id, f"src_{cid}") == [], (cid, seed)
        assert grade(payload, payload["correct_answer"], skill_id) is True
        for part in parts_of(payload):
            bad = wrong_value(part)
            if isinstance(payload["correct_answer"], dict):
                bad = {**payload["correct_answer"], part["key"]: bad}
            assert grade(payload, bad, skill_id) is False, (cid, seed, part.get("key"))
        _oracle_check(operation, payload["math_core"]["givens"], payload)
        text = payload["question_text"]
        assert "承例題" not in text, (cid, seed)
        shown = _stem_numbers(text.replace("−", "-"))
        missing = [v for v in _given_numbers(operation, payload["math_core"]["givens"]) if not _appears(v, shown)]
        assert not missing, (cid, seed, missing, text[:240])


def test_deferred_ids_have_no_publish_generators():
    for cid in sorted(VISUAL_CAPABILITY_GAP - RETAINED_DEFERRED_COMPONENTS):
        assert cid not in COMPONENTS
        for skill in SKILLS.values():
            assert not (DRYRUN / skill / "components" / f"src_{cid}").exists()
    for cid in sorted(RETAINED_DEFERRED_COMPONENTS):
        assert cid not in COMPONENTS  # excluded from Publish list; dry-run may remain as retained evidence


def test_retained_deferred_12963_prediction_operation_still_computes():
    """12963 is DEFERRED for Publish, but the prediction half stays as retained operation evidence."""
    from agent_domains_candidate.bivariate_statistics.sandbox_harness import register_candidate_in_memory
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    register_candidate_in_memory()
    _skill, op, source = RETAINED_DEFERRED_SOURCES[12963]
    _m, payload = dispatch_registered_operation(DOMAIN_KEY, op, seed=0, constraints=dict(source))
    assert str(payload["correct_answer"]) in {"168", "168.0"} or list(payload["correct_answer"].values()) == ["168"]
    assert "承例題" not in payload["question_text"]


def test_textbook_seed0_anchors():
    anchors = {
        12950: ["-4/5"],
        12951: ["1"],
        12961: ["4x+3y-51=0"],
        12962: ["-4x+5y+65=0", "11"],
        12959: ["D"],
        12965: ["5/12"],
        12966: ["-3x+2y+4=0", "13"],
        12969: ["4x+5y-112=0", "42/5"],
        12970: ["3", "3/4"],
        12971: [["1", "2", "3"]],
        12972: ["73/100", "1"],
        12949: ["B"],
        12955: ["A"],
        12956: ["A"],
        12957: ["A"],
        12958: ["A"],
        12964: ["7/10", "1629/2500", "8249/5000"],
        12967: ["B"],
        12952: ["29/40"],
        12953: ["-1"],
        12968: ["5/6"],
    }
    for cid, expected in anchors.items():
        assert _values(_gen(cid, 0)) == expected, cid


def test_r_display_rule_documented_in_domain_docstring():
    import agent_domains_candidate.bivariate_statistics.bivariate_statistics_domain as mod

    doc = mod.__doc__ or ""
    assert "terminating decimal" in doc
    assert "reduced fraction" in doc or "exact fraction" in doc.lower() or "fraction" in doc
