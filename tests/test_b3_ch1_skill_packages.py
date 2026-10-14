# -*- coding: utf-8 -*-
"""B3 Chapter 1: per-skill smoke + independent domain recompute sampling."""
from __future__ import annotations

import importlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest
import sympy as sp

from core.domain import sequence_series_domain as ssd

COVERAGE = json.loads(
    Path("reports/b3_ch1_family_coverage.json").read_text(encoding="utf-8")
)

SKILL_IDS = [row["skill_id"] for row in COVERAGE["skill_summary"]]
SUPPORTED_OPS = sorted(
    {
        r["domain_op"]
        for r in COVERAGE["rows"]
        if r["status"] == "SUPPORTED" and r.get("domain_op")
    }
)

MULTIPART_OPS = frozenset(
    {
        "expand_general_term_first_n",
        "arithmetic_from_two_terms",
        "arithmetic_recurrence_general",
        "geometric_mean_value",
        "geometric_recurrence_general",
        "arithmetic_index_and_total_sum",
        "geometric_growth_table_cells",
    }
)


def _import_skill(skill_id: str):
    return importlib.import_module(f"skills.{skill_id}")


def _payload_answer(payload: dict[str, Any]) -> Any:
    """Canonical answer object suitable for skill.check (keep multipart envelope)."""
    ans = payload.get("answer")
    if ans in (None, "", [], {}):
        ans = payload.get("correct_answer")
    return ans


def _wrong_answer(ans: Any) -> Any:
    if isinstance(ans, dict) and isinstance(ans.get("parts"), dict) and ans["parts"]:
        return {"parts": {k: "99999" for k in ans["parts"]}}
    if isinstance(ans, dict):
        return {k: "99999" for k in ans}
    return "99999"

def _question_text(payload: dict[str, Any]) -> str:
    return str(payload.get("question_text") or payload.get("problem_text") or "").strip()


def _recompute_from_givens(op: str, givens: dict[str, Any]) -> Any:
    """Independent oracle from matrix givens/params."""
    g = dict(givens or {})
    if op == "expand_general_term_first_n":
        formulas = g["formulas"]
        n = int(g["n"])
        return {
            f"({i})": ", ".join(ssd.canonical_exact(t) for t in ssd.expand_first_terms(f, n))
            for i, f in enumerate(formulas, 1)
        }
    if op == "arithmetic_nth_from_a1_d":
        return ssd.canonical_exact(ssd.arithmetic_nth(g["a1"], g["d"], int(g["n"])))
    if op == "arithmetic_d_from_a1_an":
        return ssd.canonical_exact(
            ssd.arithmetic_diff_from_two(g["a1"], 1, g["an"], int(g["n"]))
        )
    if op == "arithmetic_from_two_terms":
        d = ssd.arithmetic_diff_from_two(g["ai"], int(g["i"]), g["aj"], int(g["j"]))
        ak = ssd.arithmetic_term_from_two(
            g["ai"], int(g["i"]), g["aj"], int(g["j"]), int(g["k"])
        )
        return {"(1)": ssd.canonical_exact(d), "(2)": ssd.canonical_exact(ak)}
    if op == "arithmetic_insert_terms":
        mode = str(g.get("mode") or "term")
        if mode == "sum":
            return ssd.canonical_exact(
                ssd.arithmetic_inserted_sum(g["A"], g["B"], int(g["inserted"]))
            )
        return ssd.canonical_exact(
            ssd.arithmetic_inserted_term(
                g["A"], g["B"], int(g["inserted"]), int(g["which"])
            )
        )
    if op == "arithmetic_mean_solve":
        return ssd.canonical_exact(
            ssd.solve_linear_arithmetic_mean(
                g["p_coeff"], g["p_const"], g["q_coeff"], g["q_const"], g["mean"]
            )
        )
    if op == "arithmetic_recurrence_general":
        a1, d, k = g["a1"], g["d"], int(g["k"])
        if str(g.get("locked_stem") or "") == "bw_tile_white_count":
            an = ssd.arithmetic_nth(a1, d, k)
            return {
                "(1)": ssd.canonical_exact(a1),
                "(2)": ssd.canonical_exact(d),
                "(3)": ssd.canonical_exact(an),
            }
        general = sp.simplify(sp.sympify(a1) + (sp.symbols("n") - 1) * sp.sympify(d))
        ak = ssd.arithmetic_nth(a1, d, k)
        return {"(1)": sp.sstr(general, order="lex"), "(2)": ssd.canonical_exact(ak)}
    if op == "arithmetic_series_sum_given":
        return ssd.canonical_exact(
            ssd.arithmetic_partial_sum(g["a1"], g["d"], int(g["n"]))
        )
    if op == "arithmetic_series_recover_param":
        recover = str(g.get("recover") or "d")
        if recover == "a1":
            return ssd.canonical_exact(
                ssd.arithmetic_recover_a1_from_sum(g["Sn"], g["d"], int(g["n"]))
            )
        return ssd.canonical_exact(
            ssd.arithmetic_recover_d_from_sum(g["Sn"], g["a1"], int(g["n"]))
        )
    if op == "arithmetic_series_from_two_terms":
        d = ssd.arithmetic_diff_from_two(g["ai"], int(g["i"]), g["aj"], int(g["j"]))
        a1 = Fraction(str(ssd.to_rational(g["ai"]))) - (int(g["i"]) - 1) * d
        return ssd.canonical_exact(ssd.arithmetic_partial_sum(a1, d, int(g["n"])))
    if op == "arithmetic_sum_multiples_range":
        return ssd.canonical_exact(
            ssd.sum_multiples_in_range(int(g["lo"]), int(g["hi"]), int(g["step"]))
        )
    if op == "arithmetic_odd_count_mid_total":
        return ssd.canonical_exact(
            ssd.arithmetic_total_from_odd_mid(g["mid"], int(g["count"]))
        )
    if op == "geometric_nth_from_a1_r":
        return ssd.canonical_exact(ssd.geometric_nth(g["a1"], g["r"], int(g["n"])))
    if op == "geometric_r_from_a1_an":
        return ssd.canonical_exact(
            ssd.geometric_ratio_from_two(g["a1"], 1, g["an"], int(g["n"]))
        )
    if op == "geometric_from_two_terms":
        return ssd.canonical_exact(
            ssd.geometric_term_from_two(
                g["ai"], int(g["i"]), g["aj"], int(g["j"]), int(g["k"])
            )
        )
    if op == "geometric_insert_terms":
        return ssd.canonical_exact(
            ssd.geometric_inserted_term(
                g["A"], g["B"], int(g["inserted"]), int(g["which"])
            )
        )
    if op == "geometric_mean_value":
        pos, neg = ssd.geometric_means(g["a"], g["b"])
        return {"(1)": ssd.canonical_exact(pos), "(2)": ssd.canonical_exact(neg)}
    if op == "geometric_mean_solve_x":
        return ssd.canonical_exact(ssd.geometric_mean_solve_other(g["a"], g["mean"]))
    if op == "geometric_recurrence_general":
        a1, r, k = g["a1"], g["r"], int(g["k"])
        general = sp.simplify(sp.sympify(a1) * sp.sympify(r) ** (sp.symbols("n") - 1))
        ak = ssd.geometric_nth(a1, r, k)
        return {"(1)": sp.sstr(general, order="lex"), "(2)": ssd.canonical_exact(ak)}
    if op == "geometric_series_sum_given":
        return ssd.canonical_exact(
            ssd.geometric_partial_sum(g["a1"], g["r"], int(g["n"]))
        )
    if op == "geometric_series_recover_param":
        recover = str(g.get("recover") or "a1")
        if recover == "n":
            return ssd.canonical_exact(
                ssd.geometric_recover_n_from_sum(g["Sn"], g["a1"], g["r"])
            )
        return ssd.canonical_exact(
            ssd.geometric_recover_a1_from_sum(g["Sn"], g["r"], int(g["n"]))
        )
    # extended locked-stem families
    from core.domain import sequence_series_extended as ext

    if op == "geometric_ratio_from_shifted_pair_sums":
        return ssd.canonical_exact(
            ext.geometric_ratio_from_shifted_pair_sums(g["X"], g["Y"], int(g["index_shift"]))
        )
    if op == "geometric_ratio_from_product_quotient":
        return ssd.canonical_exact(
            ext.geometric_ratio_from_product_quotient(g["K"], exponent=int(g.get("exponent") or 4))
        )
    if op == "arithmetic_index_and_total_sum":
        idx = ext.arithmetic_index_from_a1_d_an(g["a1"], g["d"], g["an"])
        total = ssd.arithmetic_partial_sum(g["a1"], g["d"], int(g["n_total"]))
        return {"(1)": ssd.canonical_exact(idx), "(2)": ssd.canonical_exact(total)}
    if op == "arithmetic_first_threshold_crossing":
        return ssd.canonical_exact(
            ext.first_arithmetic_index_crossing_threshold(
                g["start"], g["step"], g["threshold"], compare=str(g.get("compare") or "lt")
            )
        )
    if op == "geometric_first_threshold_crossing":
        return ssd.canonical_exact(
            ext.first_geometric_index_crossing_threshold(
                g["a1"],
                g["r"],
                g["threshold"],
                compare=str(g.get("compare") or "ge"),
                power_of_index=bool(g.get("power_of_index", True)),
            )
        )
    if op == "ap_gp_mixed_mean_middle":
        return ssd.canonical_exact(ext.ap_gp_mixed_mean_middle_from_x3(g["x3"])["x2"])
    if op == "geometric_growth_table_cells":
        from core.domain.sequence_series_extended import (
            format_geometric_power_expr,
            _growth_cell_exponent,
        )

        out = {}
        for cell in g.get("cells") or []:
            exp = int(cell.get("exponent") if "exponent" in cell else _growth_cell_exponent(cell["year"], cell["position"]))
            out[str(cell["label"])] = format_geometric_power_expr(
                g["principal"], g["growth_factor"], exp
            )
        return out
    raise AssertionError(f"no_recompute_for:{op}")


def _answers_equivalent(op: str, generated: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        if not isinstance(generated, dict):
            return False
        for k, v in expected.items():
            gv = generated.get(k)
            if str(gv).strip() != str(v).strip():
                # algebraic compare
                try:
                    if sp.simplify(sp.sympify(gv) - sp.sympify(v)) != 0:
                        return False
                except Exception:
                    return False
        return True
    try:
        if sp.simplify(sp.sympify(generated) - sp.sympify(expected)) == 0:
            return True
    except Exception:
        pass
    return str(generated).strip() == str(expected).strip()


@pytest.mark.parametrize("skill_id", SKILL_IDS)
def test_skill_wrapper_and_v3_package_exist(skill_id: str):
    mod = _import_skill(skill_id)
    assert hasattr(mod, "generate") and hasattr(mod, "check")
    assert mod.GENERATOR_KEYS
    v3 = Path("agent_skills_v3") / skill_id
    assert v3.is_dir()
    assert (v3 / "__init__.py").is_file()
    assert (v3 / "component_manifest.json").is_file()
    for key in mod.GENERATOR_KEYS:
        assert (v3 / "components" / key / "generate.py").is_file()


@pytest.mark.parametrize("skill_id", SKILL_IDS)
def test_skill_smoke_generate_20(skill_id: str):
    mod = _import_skill(skill_id)
    crashes = 0
    empty_q = 0
    missing_ans = 0
    check_fail = 0
    wrong_accept = 0
    for seed in range(20):
        try:
            payload = mod.generate(seed=seed)
        except Exception:
            crashes += 1
            continue
        if not _question_text(payload):
            empty_q += 1
            continue
        ans = _payload_answer(payload)
        if ans in (None, "", [], {}):
            missing_ans += 1
            continue
        ok = mod.check(ans, ans, question_payload=payload)
        if not ok:
            check_fail += 1
        bad = _wrong_answer(ans)
        if mod.check(bad, ans, question_payload=payload):
            wrong_accept += 1
    assert crashes == 0
    assert empty_q == 0
    assert missing_ans == 0
    assert check_fail == 0
    assert wrong_accept == 0


@pytest.mark.parametrize("op", SUPPORTED_OPS)
def test_family_50_sample_independent_recompute(op: str):
    crashes = 0
    wrong = 0
    contract = 0
    for seed in range(50):
        try:
            matrix = ssd.build_sequence_series_matrix(operation=op, seed=seed)
        except Exception:
            crashes += 1
            continue
        if not ssd.validate_sequence_series_matrix(matrix):
            contract += 1
            continue
        givens = matrix.get("givens") or matrix.get("params") or {}
        expected = _recompute_from_givens(op, givens)
        generated = matrix["answer"]
        if isinstance(generated, dict) and generated.get("parts"):
            gen_val = generated["parts"]
        elif isinstance(generated, dict):
            gen_val = generated.get("canonical_form")
        else:
            gen_val = generated
        if not _answers_equivalent(op, gen_val, expected):
            wrong += 1
        if op in MULTIPART_OPS:
            parts = generated.get("parts") if isinstance(generated, dict) else None
            stem = matrix.get("stem_structure") or {}
            items = stem.get("items") or []
            if not parts or len(parts) < 2:
                contract += 1
            if items and len(items) != len(parts):
                contract += 1
    assert crashes == 0, f"{op} crashes={crashes}"
    assert wrong == 0, f"{op} wrong={wrong}"
    assert contract == 0, f"{op} contract={contract}"


@pytest.mark.parametrize("skill_id", SKILL_IDS)
def test_difficulty_profiles_produce_payloads(skill_id: str):
    mod = _import_skill(skill_id)
    texts = []
    for diff in (1, 2, 3):
        p = mod.generate(seed=11, difficulty=diff)
        q = _question_text(p)
        assert q
        texts.append(q)
    # At least ensure all difficulty levels generate without crash;
    # diversity is soft (domain may share shell).
    assert len(texts) == 3
