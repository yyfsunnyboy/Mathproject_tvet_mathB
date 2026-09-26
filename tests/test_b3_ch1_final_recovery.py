# -*- coding: utf-8 -*-
"""B3 Ch1 final recovery: 11922 tile recurrence + 11950 compound growth table."""
from __future__ import annotations

from fractions import Fraction

import sympy as sp

from core.domain.sequence_series_domain import (
    arithmetic_nth,
    build_sequence_series_matrix,
    canonical_exact,
    validate_sequence_series_matrix,
)
from core.domain.sequence_series_extended import (
    format_geometric_power_expr,
    geometric_year_end_expr,
    geometric_year_start_expr,
)

LEAK = ("TODO", "FIXME", "placeholder", "NoneType", "traceback", "DEBUG")


def _clean(m: dict) -> None:
    assert validate_sequence_series_matrix(m)
    blob = " ".join(
        [
            str(m.get("question_text") or ""),
            str(m.get("answer") or ""),
            str(m.get("explanation") or ""),
        ]
    ).lower()
    for tok in LEAK:
        assert tok.lower() not in blob


def test_source_model_11922_white_tiles():
    # a_n = 3(2n+1)-n = 5n+3; a1=8; a_n=a_{n-1}+5; a5=28
    for n in range(1, 12):
        assert 3 * (2 * n + 1) - n == 5 * n + 3
    assert arithmetic_nth(8, 5, 1) == 8
    assert arithmetic_nth(8, 5, 5) == 28
    assert arithmetic_nth(8, 5, 2) - arithmetic_nth(8, 5, 1) == 5


def test_source_model_11950_compound_cells():
    p, q = Fraction(10000), Fraction(203, 200)  # 1.015
    assert geometric_year_end_expr(p, q, 2) == "10000*(203/200)**2"
    assert geometric_year_start_expr(p, q, 4) == "10000*(203/200)**3"
    assert geometric_year_end_expr(p, q, 5) == "10000*(203/200)**5"
    for year, pos, exp in ((2, "end", 2), (4, "start", 3), (5, "end", 5)):
        expr = format_geometric_power_expr(p, q, exp)
        term = sp.simplify(sp.sympify(p) * sp.sympify(q) ** exp)
        assert sp.simplify(sp.sympify(expr) - term) == 0


def test_11922_locked_stem_50_samples():
    seen_n = set()
    for seed in range(50):
        m = build_sequence_series_matrix(
            operation="arithmetic_recurrence_general",
            seed=seed,
            locked_stem="bw_tile_white_count",
        )
        _clean(m)
        g = m["givens"]
        q = m.get("question_text") or ""
        assert "白色地磚" in q
        assert "黑磚" in q
        assert "image" not in q.lower()
        n = int(g["target_n"])
        seen_n.add(n)
        assert n != 5 or seed < 0  # default sampling avoids textbook n=5
        parts = (m.get("answer") or {}).get("parts") or {}
        assert parts["(1)"] == "8"
        assert parts["(2)"] == "5"
        assert parts["(3)"] == canonical_exact(Fraction(5 * n + 3))
        assert len(parts) == 3
    assert len(seen_n) >= 2


def test_11950_locked_stem_50_samples():
    fingerprints = set()
    for seed in range(50):
        m = build_sequence_series_matrix(
            operation="geometric_growth_table_cells",
            seed=seed,
        )
        _clean(m)
        g = m["givens"]
        q = m.get("question_text") or ""
        assert "複利" in q
        assert "①" in q and "②" in q and "③" in q
        p = Fraction(str(g["principal"]))
        rate = Fraction(str(g["annual_rate"]))
        years = int(g["years"])
        qf = Fraction(str(g["growth_factor"]))
        assert qf == 1 + rate
        fingerprints.add((int(p), str(rate), years))
        assert (int(p), rate, years) != (10000, Fraction(3, 200), 5)
        parts = (m.get("answer") or {}).get("parts") or {}
        assert set(parts) == {"①", "②", "③"}
        for cell in g["cells"]:
            label = cell["label"]
            exp = int(cell["exponent"])
            assert parts[label] == format_geometric_power_expr(p, qf, exp)
    assert len(fingerprints) >= 2


def test_11922_package_multipart_checker():
    from skills import vh_數學B3_SubSection_1_1_4 as mod

    payload = mod.generate(seed=9, component_id="src_11922")
    ans = payload.get("answer")
    assert mod.check(ans, ans, question_payload=payload)
    bad = {"(1)": "8", "(2)": "5", "(3)": "0"}
    assert not mod.check(bad, ans, question_payload=payload)


def test_11950_package_multipart_any_wrong_rejects():
    from skills import vh_數學B3_SubSection_1_2_1 as mod

    payload = mod.generate(seed=4, component_id="src_11950")
    ans = payload.get("answer")
    assert mod.check(ans, ans, question_payload=payload)
    if isinstance(ans, dict):
        bad = dict(ans)
        key = next(iter(bad))
        bad[key] = "0"
        assert not mod.check(bad, ans, question_payload=payload)
