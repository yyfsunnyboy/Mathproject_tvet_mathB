"""Sandbox gate for 普高數學2 Unit 8（一維數據分析）, revision_0004.

Every component is sampled on seeds 0-39. Answers are re-derived by an oracle in this file that does not import
the domain, stems must print every given, statistics tables are parsed cell by cell, and the generated bar charts
of 例題9／隨堂練習10 are decoded and measured pixel by pixel against the graded percentages.
"""

from __future__ import annotations

import base64
import importlib.util
import io
import json
import math
import re
import sqlite3
import statistics
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction as F
from pathlib import Path

import pytest

from agent_domains_candidate.univariate_statistics import build_sandbox as B
from agent_domains_candidate.univariate_statistics.sandbox_harness import register_candidate_in_memory
from agent_domains_candidate.univariate_statistics.univariate_statistics_domain import DOMAIN_KEY
from agent_domains_candidate.univariate_statistics.univariate_statistics_specs import (
    CHART_COMPONENTS,
    COMPONENTS,
    FAMILY,
    FIXED_CONCEPT,
    FIXED_ROWS,
    OP,
    SKILL_OPERATIONS,
    SKILLS,
    VISUAL_CAPABILITY_GAP,
)
from agent_domains_candidate.univariate_statistics.verification import grade, parts_of, verify_payload, wrong_value

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRYRUN = B.DRYRUN
FORMAL_DB = PROJECT_ROOT / "instance" / "kumon_math.db"
SEEDS = range(40)
UNIT_IDS = set(range(12912, 12947))
VARIABLE = sorted(UNIT_IDS - VISUAL_CAPABILITY_GAP - FIXED_CONCEPT)

register_candidate_in_memory()
B.build_all()


def _skill_of(cid: int) -> str:
    return SKILLS[COMPONENTS[cid][0]]


_MODULES: dict[int, object] = {}


def _gen(cid: int, seed: int = 0) -> dict:
    if cid not in _MODULES:
        path = DRYRUN / _skill_of(cid) / "components" / f"src_{cid}" / "generate.py"
        spec = importlib.util.spec_from_file_location(f"m2u8r3_{cid}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[cid] = module
    return _MODULES[cid].generate(seed=seed)


def _values(payload: dict) -> list:
    answer = payload["correct_answer"]
    if isinstance(answer, dict):
        return [answer[key] for key in sorted(answer, key=lambda item: int(item.split("_")[1]))]
    return [answer]


# --- independent oracle (no domain imports) -----------------------------------------------------------------------


def _pct(sorted_vals: list[F], p: int) -> F:
    pos = F(len(sorted_vals) * p, 100)
    if pos.denominator == 1:
        i = int(pos)
        return (sorted_vals[i - 1] + sorted_vals[i]) / 2
    return sorted_vals[math.ceil(pos) - 1]


def _expand(values, counts) -> list[F]:
    return [F(str(v)) for v, c in zip(values, counts) for _ in range(int(c))]


def _round(x: float | F, places: int) -> F:
    d = Decimal(x.numerator) / Decimal(x.denominator) if isinstance(x, F) else Decimal(repr(x))
    return F(str(d.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)))


def _sd_float(expected: str) -> float:
    text = str(expected)
    if "sqrt" not in text:
        return float(F(text))
    coef, _, rad = text.partition("sqrt(")
    return float(F(coef.rstrip("*") or "1")) * math.sqrt(float(F(rad.rstrip(")"))))


def _fs(values) -> list[F]:
    return [F(str(v)) for v in values]


def _grade_percentile(pcts, p) -> int:
    """Counted from grade 0 upward on the normalised distribution (the domain counts down from 15)."""
    w = [F(str(x)) for x in pcts]
    cum = F(0)
    for g, x in enumerate(w):
        cum += x
        if cum / sum(w) * 100 > p:
            return g
    raise AssertionError("percentile not reached")


def _grade_sd(pcts) -> float:
    w = [float(x) for x in pcts]
    mu = sum(g * x for g, x in enumerate(w)) / sum(w)
    return math.sqrt(sum((g - mu) ** 2 * x for g, x in enumerate(w)) / sum(w))


def _grade_claim_oracle(c, g) -> bool:
    data = {"cn": [F(str(x)) for x in g["cn_pct"]], "math": [F(str(x)) for x in g["math_pct"]]}
    if c["kind"] == "mode":
        p = data[c["subject"]]
        return p[c["grade"]] == max(p) and p.count(max(p)) == 1
    if c["kind"] == "share_below":
        return all(data[s][c["grade"]] < c["threshold"] for s in ("cn", "math"))
    if c["kind"] == "upper_half":
        return sum(data[c["subject"]][c["grade"]:]) > 50
    if c["kind"] == "sd_less":
        return _grade_sd(g[f"{c['first']}_pct"]) < _grade_sd(g[f"{c['second']}_pct"])
    raise AssertionError(c["kind"])


def _quartile_truth(sc, st) -> bool:
    n, mean = sc["n"], F(str(sc["mean"]))
    return {
        "median_between_quartiles": True,
        "median_is_quartile_midpoint": False,
        "count_above_q3": st.get("mode") == "at_most",
        "count_ge_q1": not st.get("strict"),
        "total_exceeds": n * mean > F(str(st.get("threshold", 0))),
    }[st["kind"]]


def _rescale_truth(sc, st) -> bool:
    mu_x, sd_x = 2 * (F(sc["mu_y"]) - F(sc["shift"])), 2 * F(sc["sd_y"])
    s = F(str(st["stated"]))
    return {
        "orig_mean_below": mu_x < s,
        "orig_sd_is": sd_x == s,
        "k_orig_below": s == 2 * (F(sc["low_y"]) - F(sc["shift"])),
        "nobody_orig_over": s >= 2 * F(sc["shift"]),
    }[st["kind"]]


def _percentile_truth(st) -> bool:
    if st["kind"] == "pct_scale":
        return F(str(st["c"])) > 0
    return {"pct_shift": True, "pct_square": False, "pct_merge_sum": False, "pct_lt_mean": False,
            "pct_within_range": True}[st["kind"]]


def _claim_truth(c) -> bool:
    kind = c["kind"]
    if kind == "adding_value_raises_mean_by":
        if "mean" not in c:
            return False
        n, mu = c["n"], F(str(c["mean"]))
        return (n * mu + F(str(c["added"]))) / (n + 1) - mu == F(str(c["delta"]))
    if kind == "equal_values_sd_zero":
        return True
    if kind == "constant_data_sd":
        return statistics.pvariance([F(c["value"])] * c["n"]) == 0 and F(str(c["stated"])) == 0
    if kind == "scaled_sd_signed":
        return F(str(c["stated_factor"])) == abs(F(str(c["a"])))
    if kind == "median_ge_mean_always":
        return False
    if kind == "median_ge_mean_data":
        vals = _fs(c["values"])
        return statistics.median(vals) >= statistics.mean(vals)
    raise AssertionError(kind)


def _oracle_check(op: str, g: dict, payload: dict) -> None:
    got = _values(payload)
    if op == "arithmetic_mean":
        assert F(got[0]) == statistics.mean(_fs(g["values"]))
    elif op == "weighted_mean":
        v, w = _fs(g["values"]), _fs(g["weights"])
        assert F(got[0]) == sum(a * b for a, b in zip(v, w)) / sum(w)
        if g.get("scene") == "insurance":
            p = F(str(g["weights"][0]))
            assert F(got[0]) == g["premium"] - p * g["payout"]
    elif op == "weighted_mean_unknown":
        w = _fs(g["weights"])
        i = g["unknown_index"]
        known = sum(F(str(v)) * wt for j, (v, wt) in enumerate(zip(g["values"], w)) if j != i)
        assert F(got[0]) == (F(str(g["known_mean"])) * sum(w) - known) / w[i]
    elif op == "geometric_growth_mean":
        growth = math.prod(1 + float(F(r)) for r in g["rates"]) ** (1 / len(g["rates"])) - 1
        assert F(got[0]) == _round(growth, int(g["decimals"]))
    elif op == "geometric_growth_unknown":
        known = math.prod(1 + F(r) for k, r in enumerate(g["rates"]) if k != g["unknown_index"])
        x = (1 + F(g["known_mean"])) ** len(g["rates"]) / known - 1
        assert F(got[0]) == x
        assert Decimal(x.numerator) / Decimal(x.denominator) == Decimal(str(float(x)))  # exact decimal answer
    elif op == "median_lists":
        assert [F(a) for a in got] == [statistics.median(_fs(row)) for row in g["lists"]]
    elif op == "median_consecutive":
        assert [F(a) for a in got] == [F(statistics.median(range(1, n + 1))) for n in g["ends"]]
    elif op == "percentile_frequency":
        data = sorted(_expand(g["values"], g["counts"]))
        assert [F(a) for a in got] == [_pct(data, p) for p in g["percentiles"]]
    elif op == "quartile_frequency":
        data = sorted(_expand(g["values"], g["counts"]))
        assert [F(a) for a in got] == [_pct(data, p) for p in (25, 50, 75)]
    elif op == "list_summary_stats":
        vals = sorted(_fs(g["values"]))
        want = {"mean": statistics.mean(vals), "median": statistics.median(vals), "q3": _pct(vals, 75), "q1": _pct(vals, 25)}
        assert [F(a) for a in got] == [want[s] for s in g["stats"]]
    elif op == "mean_variance_sd":
        vals = _fs(g["values"])
        assert F(got[0]) == statistics.mean(vals) and F(got[1]) == statistics.pvariance(vals)
        assert math.isclose(_sd_float(got[2]), math.sqrt(statistics.pvariance(vals)), rel_tol=1e-12)
    elif op == "standard_deviation":
        for a, row in zip(got, g["lists"]):
            assert math.isclose(_sd_float(a), math.sqrt(statistics.pvariance(_fs(row))), rel_tol=1e-12)
    elif op == "compare_standard_deviation":
        variances = [statistics.pvariance(_fs(row)) for row in g["lists"]]
        assert got[0] == "ABC"[variances.index(max(variances))]
    elif op == "unknown_given_sd":
        x = F(got[0])
        full = _fs(g["prefix"]) + [x] + _fs(g["suffix"])
        assert full == sorted(full) and len(set(full)) == len(full)
        assert statistics.pvariance(full) == F(g["sd"]) ** 2
    elif op == "linear_mean_sd":
        a = F(str(g["a"]))
        assert [F(x) for x in got] == [a * F(str(g["mean"])) + F(str(g["b"])), abs(a) * F(str(g["sd"]))]
    elif op == "linear_find_scale_sd":
        a = (F(str(g["new_max"])) - F(str(g["new_mean"]))) / (F(g["old_max"]) - F(g["old_mean"]))
        assert F(got[0]) == abs(a) * F(g["old_sd"])
    elif op == "standardize_scores":
        zs = [(F(x) - F(m)) / F(s) for x, m, s in zip(g["scores"], g["means"], g["sds"])]
        assert [F(a) for a in got[:2]] == zs and got[2] == "AB"[zs.index(max(zs))]
    elif op == "monthly_mean_sd":
        vals = _fs(g["values"])
        assert F(got[0]) == _round(statistics.mean(vals), g["places"])
        assert F(got[1]) == _round(math.sqrt(statistics.pvariance(vals)), g["places"])
    elif op == "true_false_stat":
        assert got[0] == ("A" if _claim_truth(g["claim"]) else "B")
    elif op == "statement_selection":
        sc = g["scenario"]
        if "q1" in sc:
            truth = [_quartile_truth(sc, st) for st in g["statements"]]
        elif "div" in sc:
            truth = [_rescale_truth(sc, st) for st in g["statements"]]
        else:
            truth = [_percentile_truth(st) for st in g["statements"]]
        assert got[0] == [str(i) for i, t in enumerate(truth, 1) if t]
    elif op == "grade_distribution_read":
        for ask, a in zip(g["asks"], got):
            if ask == "multi_select_basic":
                truth = [_grade_claim_oracle(c, g) for c in g["claims"]]
                assert a == [str(i) for i, t in enumerate(truth, 1) if t]
            else:
                p = int(ask.split("_")[-1])
                c, m = _grade_percentile(g["cn_pct"], p), _grade_percentile(g["math_pct"], p)
                assert a == ("A" if c > m else "B" if m > c else "C")
    else:
        raise AssertionError(f"no oracle for {op}")


# --- stem ↔ givens ------------------------------------------------------------------------------------------------

_NUM = re.compile(r"\\frac\{(\d+)\}\{(\d+)\}|(\d+(?:\.\d+)?)(\s*\\?%)?")


def _stem_numbers(text: str) -> set[F]:
    out: set[F] = set()
    for m in _NUM.finditer(text):
        if m.group(1):
            out.add(F(int(m.group(1)), int(m.group(2))))
        else:
            v = F(m.group(3))
            out.add(v / 100 if m.group(4) else v)
            out.add(v)
    return out


_NOT_PRINTED = {"unknown_index", "kind", "mode", "strict", "scene", "asks", "stats", "subjects"}


def _given_numbers(op: str, g: dict) -> list[F]:
    if op == "grade_distribution_read":
        # the percentages are in the chart (checked pixel by pixel below); the stem prints grades and percentile ranks
        return ([F(c["grade"]) for c in g.get("claims", []) if "grade" in c]
                + [F(a.rsplit("_", 1)[1]) for a in g["asks"] if a.startswith("higher_mark_")])
    g = dict(g)
    if op == "weighted_mean" and g.get("scene") == "insurance":
        g.pop("values")  # premium − payout and premium are printed instead
    if op == "geometric_growth_unknown":
        g["rates"] = [r for k, r in enumerate(g["rates"]) if k != g["unknown_index"]]
    if op == "true_false_stat" and g["claim"]["kind"] == "constant_data_sd":
        g["claim"] = {k: v for k, v in g["claim"].items() if k != "n"}  # shown as the length of the printed list
    out: list[F] = []

    def walk(key, value):
        if key in _NOT_PRINTED or isinstance(value, bool):
            return
        if isinstance(value, dict):
            for k, v in value.items():
                walk(k, v)
        elif isinstance(value, list):
            for v in value:
                walk(key, v)
        elif value != "x" and F(str(value)) != 0:  # a zero term (e.g. b = 0 in ax+b) is legitimately omitted
            out.append(abs(F(str(value))))

    for k, v in g.items():
        walk(k, v)
    return out


# --- tests --------------------------------------------------------------------------------------------------------


def test_component_coverage_matches_formal_unit8():
    assert set(COMPONENTS) == UNIT_IDS
    assert not FIXED_ROWS
    assert set(FAMILY) == UNIT_IDS
    assert VISUAL_CAPABILITY_GAP == set()
    assert CHART_COMPONENTS == {12926, 12930}
    for ops in SKILL_OPERATIONS.values():
        assert set(ops) <= set(OP)


def test_formal_db_binding_readonly():
    con = sqlite3.connect(f"file:{FORMAL_DB.as_posix()}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "select id, skill_id from textbook_examples where source_curriculum='general' "
            "and source_volume='數學2' and source_chapter='單元8 一維數據分析' order by id"
        ).fetchall()
    finally:
        con.close()
    assert [r[0] for r in rows] == sorted(UNIT_IDS)
    by_id = {cid: SKILLS[COMPONENTS[cid][0]] for cid in COMPONENTS}
    for tid, skill in rows:
        assert by_id[tid] == skill


@pytest.mark.parametrize("cid", sorted(COMPONENTS))
def test_component_seeds_0_39(cid: int):
    skill_id = _skill_of(cid)
    operation = OP[COMPONENTS[cid][1]]
    directory = DRYRUN / skill_id / "components" / f"src_{cid}"
    assert {path.name for path in directory.iterdir() if path.is_file()} == {"generate.py", "metadata.py", "get_hint.py"}
    surfaces, answers = set(), set()
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
        shown = _stem_numbers(text)
        missing = [v for v in _given_numbers(operation, payload["math_core"]["givens"]) if v not in shown]
        assert not missing, (cid, seed, missing)
        chart = payload.get("chart_data")
        surfaces.add(text + (json.dumps([p["percent"] for p in chart["panels"]]) if chart else ""))
        answers.add(json.dumps(payload["correct_answer"], sort_keys=True, ensure_ascii=False))
    assert len(surfaces) >= 20, (cid, len(surfaces))
    assert len(answers) >= 2, (cid, answers)


def test_choice_and_truth_answers_move():
    for cid in [12928, 12931, 12932, 12933, 12934]:
        labels = {_values(_gen(cid, s))[0] for s in SEEDS}
        assert len(labels) >= 2, (cid, labels)
    for cid in [12923, 12941, 12946]:
        sets = {tuple(_values(_gen(cid, s))[0]) for s in SEEDS}
        assert len(sets) >= 3, (cid, sets)
    for cid in [12940, 12919, 12920, 12922]:
        assert len({json.dumps(_gen(cid, s)["correct_answer"]) for s in SEEDS}) >= 10, cid


_TABLES = {
    12913: (["", "平常成績", "第一次期中考", "第二次期中考", "期末考"], ["分數", "比重"]),
    12936: (["", "平常成績", "第一次期中考", "第二次期中考", "期末考"], ["分數", "比重"]),
    12916: (["顧客狀況", "被隔離", "不被隔離"], ["機率"]),
    12919: (["進球數（次）"], ["人數（人）"]),
    12922: (["呼吸次數"], ["人數"]),
    12920: (["薪資（千元）"], ["員工數（人）"]),
    12943: (["", "數學", "英文"], ["平均數", "標準差"]),
    12944: (["月份", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"], ["氣溫（°C）"]),
}
_ARRAY = re.compile(r"\\\(\\begin\{array\}\{([|c]+)\}(.*?)\\end\{array\}\\\)", re.S)


def _cell_text(cell: str) -> str:
    cell = cell.strip()
    m = re.fullmatch(r"\\text\{([^{}]*)\}(?:\(\\%\))?", cell)
    return m.group(1) if m else cell


def _cell_value(cell: str) -> F:
    cell = cell.strip()
    if cell.endswith(r"\%"):
        return F(cell[:-2]) / 100
    return F(cell)


def test_table_latex_structure_and_semantics():
    affected = {cid for cid in COMPONENTS if "begin{array}" in _gen(cid, 0)["question_text"]}
    assert affected == set(_TABLES)
    for cid, (header_labels, row_labels) in _TABLES.items():
        for seed in SEEDS:
            payload = _gen(cid, seed)
            text, g = payload["question_text"], payload["math_core"]["givens"]
            tables = _ARRAY.findall(text)
            assert len(tables) == 1 and text.count("begin{array}") == 1, cid
            spec, body = tables[0]
            inner = text[text.index(r"\(\begin{array}"): text.index(r"\end{array}\)")]
            assert "$" not in inner and inner.count(r"\(") == 1, (cid, "nested math")
            cols = spec.count("c")
            assert spec == "|" + "|".join("c" * cols) + "|"
            body = body.strip()
            assert body.startswith(r"\hline") and body.endswith(r"\\ \hline")
            rows = [r.replace(r"\hline", "").strip() for r in body.split(r"\\")]
            rows = [r for r in rows if r]
            cells = [[c for c in r.split("&")] for r in rows]
            assert len(cells) == 1 + len(row_labels) and all(len(r) == cols for r in cells), (cid, seed)
            assert [_cell_text(c) for c in cells[0][: len(header_labels)]] == header_labels, (cid, seed)
            assert [_cell_text(r[0]) for r in cells[1:]] == row_labels, (cid, seed)
            data = [[c.strip() for c in r[1:]] for r in cells[1:]]
            op = COMPONENTS[cid][1]
            if op in ("weighted_mean", "weighted_mean_unknown") and g.get("scene") != "insurance":
                assert data[0] == [str(v) if v != "x" else "x" for v in g["values"]]
                assert [_cell_value(c) for c in data[1]] == _fs(g["weights"])
            elif g.get("scene") == "insurance":
                assert [_cell_value(c) for c in data[0]] == _fs(g["weights"])
            elif op in ("percentile_frequency", "quartile_frequency"):
                assert [F(_cell_text(c)) for c in cells[0][1:]] == _fs(g["values"])
                assert [int(c) for c in data[0]] == list(g["counts"])
                assert f"{sum(g['counts'])}" in text
            elif op == "standardize_scores":
                assert [_cell_value(c) for c in data[0]] == _fs(g["means"])
                assert [_cell_value(c) for c in data[1]] == _fs(g["sds"])
                assert [_cell_text(c) for c in cells[0][1:]] == list(g["subjects"])
            elif op == "monthly_mean_sd":
                assert [_cell_value(c) for c in data[0]] == _fs(g["values"])


def test_precision_is_stated_and_matches_answer():
    for cid in (12914, 12937):
        for seed in SEEDS:
            payload = _gen(cid, seed)
            places = int(payload["math_core"]["givens"]["decimals"])
            assert f"四捨五入至小數點後第 ${places}$ 位" in payload["question_text"]
            ans = F(payload["correct_answer"])
            assert ans == _round(ans, places)
    for seed in SEEDS:
        payload = _gen(12917, seed)
        assert "以小數表示" in payload["question_text"]
        x = F(payload["correct_answer"])
        assert Decimal(x.numerator) / Decimal(x.denominator) == Decimal(str(float(x)))


def test_textbook_seed0_answers():
    anchors = {
        12912: ["196"], 12913: ["781/10"], 12914: ["7/500"], 12937: ["21/100"], 12917: ["3/5"], 12936: ["69"],
        12924: ["6", "16", "4"], 12925: ["5/2"], 12927: ["90", "10", "sqrt(10)"], 12940: ["15"],
        12942: ["86", "117/10"], 12944: ["11/2", "14/5"], 12939: ["14"], 12943: ["1", "5/4", "B"],
        12923: [["1", "3"]], 12941: [["1", "2", "4"]], 12946: [["1", "2"]],
        12931: ["B"], 12932: ["A"], 12933: ["B"], 12934: ["B"], 12928: ["B"],
    }
    for cid, expected in anchors.items():
        assert _values(_gen(cid, 0)) == expected, cid


def test_grade_distribution_textbook_anchors():
    payload = _gen(12926, 0)
    g = payload["math_core"]["givens"]
    assert g["dataset"] == "gsat_109"
    assert payload["correct_answer"] == {"part_1": ["1", "2", "4"], "part_2": "B"}
    assert (_grade_percentile(g["cn_pct"], 88), _grade_percentile(g["math_pct"], 88)) == (13, 14)
    assert "國文 13 級分、數學 14 級分" in payload["explanation_steps"][1]
    follow = _gen(12930, 0)
    assert follow["correct_answer"] == "C"
    assert (_grade_percentile(g["cn_pct"], 75), _grade_percentile(g["math_pct"], 75)) == (13, 13)
    assert "國文 13 級分、數學 13 級分" in follow["explanation_steps"][0]


_CLAIM_TEXT = {
    "mode": "{s}得 ${grade}$ 級分的人數是該科中最多",
    "share_below": "兩科 ${grade}$ 級分的人數比例都小於百分之{t}",
    "upper_half": "{s}得 ${grade}$ 級分以上（含）的人數超過該科人數的一半",
    "sd_less": "{a}的標準差小於{b}的標準差",
}
_SUBJECT = {"cn": "國文科", "math": "數學科"}
_RGB_FILL = (0xF5, 0x9E, 0x0B)
_RGB_EDGE = (0xB4, 0x53, 0x09)


def _bar_pixels(image, x: float, height: int) -> int:
    """Length of the bar-coloured run above the x axis in one pixel column of the PNG."""
    col = int(round(x))
    run, best, seen = 0, 0, False
    for y in range(height - 1, -1, -1):
        r, g, b = image.getpixel((col, y))[:3]
        barish = any(abs(r - c[0]) + abs(g - c[1]) + abs(b - c[2]) < 60 for c in (_RGB_FILL, _RGB_EDGE))
        if barish:
            run += 1
            seen = True
            best = max(best, run)
        elif seen:
            break
    return best


@pytest.mark.parametrize("cid", sorted(CHART_COMPONENTS))
def test_grade_charts_match_data_and_render(cid: int):
    from PIL import Image

    truths: dict[int, set] = {}
    labels, selections, datasets = set(), set(), set()
    for seed in SEEDS:
        payload = _gen(cid, seed)
        g, text = payload["math_core"]["givens"], payload["question_text"]
        datasets.add(g["dataset"])
        assert "begin{array}" not in text and "承例題" not in text
        assert text.startswith("以下為") and "國文科與數學科級分的人數百分比分布圖" in text
        if g["dataset"] == "gsat_109":
            assert seed % 20 == 0 and "$109$ 學年度學測" in text
        else:
            assert "某次學測模擬測驗" in text and "109" not in text
            for key in ("cn_pct", "math_pct"):
                assert sum(F(v) for v in g[key]) == 100, (seed, key)
        for key in ("cn_pct", "math_pct"):
            assert len(g[key]) == 16 and abs(sum(F(str(v)) for v in g[key]) - 100) <= F(5, 100)
        assert payload["visual_backed"] is True and payload["visual_asset_type"] == "grade_percentage_bar_chart_png"
        panels, aids = payload["chart_data"]["panels"], payload["visual_aids"]
        assert [p["subject"] for p in panels] == ["國文科", "數學科"] and len(aids) == 2
        assert payload.get("visual_spec") in (None, {}) and not payload.get("image_base64")
        scale = None
        for panel, aid, key in zip(panels, aids, ("cn_pct", "math_pct")):
            assert panel["title"] == f"{panel['subject']}級分人數百分比分布圖" == aid["label"]
            assert panel["x_label"] == f"{panel['subject']}級分" and panel["y_label"] == "人數百分比（%）"
            assert panel["grades"] == list(range(16))
            assert [F(v) for v in panel["percent"]] == [F(str(v)) for v in g[key]]
            assert panel["y_max"] > max(F(v) for v in panel["percent"])
            raw = base64.b64decode(aid["value"])
            assert raw[:8] == b"\x89PNG\r\n\x1a\n"
            image = Image.open(io.BytesIO(raw)).convert("RGB")
            assert list(image.size) == panel["size_px"]
            if scale is None:
                top = max(range(16), key=lambda i: F(panel["percent"][i]))
                scale = panel["bar_heights_px"][top] / float(panel["percent"][top])
            for pct, h, x in zip(panel["percent"], panel["bar_heights_px"], panel["bar_centers_px"]):
                assert abs(h - float(pct) * scale) <= 0.01, (seed, "bar height not proportional on the shared axis")
                measured = _bar_pixels(image, x, image.size[1])
                assert abs(measured - h) <= 2.5, (cid, seed, panel["subject"], pct, measured, h)
        for i, c in enumerate(g.get("claims", [])):
            line = "①②③④"[i] + _CLAIM_TEXT[c["kind"]].format(
                s=_SUBJECT.get(c.get("subject")), grade=c.get("grade"), t="零一二三四五六七八九十"[c.get("threshold", 0)],
                a=_SUBJECT.get(c.get("first")), b=_SUBJECT.get(c.get("second")))
            assert line in text, (seed, line)
            truths.setdefault(i, set()).add(_grade_claim_oracle(c, g))
        answer = payload["correct_answer"]
        if isinstance(answer, dict):
            selections.add(tuple(answer["part_1"]))
            labels.add(answer["part_2"])
        else:
            labels.add(answer)
    assert datasets == {"gsat_109", "simulated"}
    assert len(labels) >= 2, (cid, labels)
    if cid == 12926:
        assert all(truths[i] == {True, False} for i in range(4)), truths  # no statement is always right or wrong
        assert len(selections) >= 5, selections


# CSS canvas sizes measured on the student practice page (scratchpad background canvas) at 430 px and 1280 px
_STUDENT_CANVASES = {"w430": (392, 500), "w1280": (754, 526)}


def _student_image_scale(canvas: tuple[int, int], size: tuple[int, int]) -> float:
    """computeImageGrid + computeContainRect of static/js/scratchpad_layers.js for two images."""
    region_w, region_h = canvas[0] - 2 * 14, canvas[1] - 2 * 14
    cols = 1 if region_w < 520 else 2
    rows = 2 // cols
    cell_w, cell_h = (region_w - 12 * (cols - 1)) / cols, (region_h - 12 * (rows - 1)) / rows
    return min((cell_w - 12) / size[0], (cell_h - 12) / size[1])


def test_grade_chart_missing_glyph_is_an_error():
    import warnings

    from agent_domains_candidate.univariate_statistics import univariate_statistics_chart as C

    filters = list(warnings.filters)
    with pytest.raises(ValueError, match="chart_glyph_missing"):
        C._render_panel.__wrapped__("\U0001F600科", tuple(["6.25"] * 16), 10)
    assert list(warnings.filters) == filters


def test_grade_chart_text_readable_on_student_canvas():
    from agent_domains_candidate.univariate_statistics import univariate_statistics_chart as C

    payload = _gen(12930, 1)
    size = tuple(payload["chart_data"]["panels"][0]["size_px"])
    for name, canvas in _STUDENT_CANVASES.items():
        scale = _student_image_scale(canvas, size)
        value_px = C.VALUE_PT * C.DPI / 72 * scale
        assert value_px >= 11, (name, size, round(scale, 3), round(value_px, 1))
