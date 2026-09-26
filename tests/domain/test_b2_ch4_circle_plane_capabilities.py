# -*- coding: utf-8 -*-
"""B2 Ch4 circle.plane Phase 1 capability tests (4-1.1 / 4-1.2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import sympy as sp

from core.domain.circle_plane_domain import (
    OPS,
    build_circle_plane_matrix,
    center_radius_from_general,
    center_radius_from_standard,
    circle_from_center_radius,
    circle_from_diameter,
    circle_through_three_points,
    circle_validity_from_general,
    format_standard_equation,
    make_circle,
    solve_circle_parameter_range,
    standard_from_center_point,
    standard_to_general,
    validate_circle_plane_matrix,
)
from core.gencode.choice_contract_validator import choice_semantic_key
from core.gencode.circle_plane_capability_adapter import adapt_circle_plane_matrix
from core.registry.domain_operation_registry import check_registry_consistency, get_domain_spec
from core.registry.taxonomy_registry import resolve_domain_for_skill

ROOT = Path(__file__).resolve().parents[1]
SKILL_411 = "vh_數學B2_SubSection_4_1_1"
SKILL_412 = "vh_數學B2_SubSection_4_1_2"
MATRIX_PATH = ROOT / "reports" / "b2_ch4_41_source_capability_matrix.json"


def test_registry_and_taxonomy_bindings():
    for skill in (SKILL_411, SKILL_412):
        routing = resolve_domain_for_skill(skill)
        assert routing["fixed_domain_key"] == "circle.plane"
        assert routing["domain_module"] == "core.domain.circle_plane_domain"
        assert routing["allowed_operations"]
    spec = get_domain_spec("circle.plane")
    assert spec is not None
    assert set(spec.allowed_operations) == set(OPS)
    assert check_registry_consistency() == []


def test_standard_and_general_core_math():
    c = circle_from_center_radius(center=[3, -2], radius=5)
    assert c["standard_form"] == "(x-3)^2+(y+2)^2=25"
    assert format_standard_equation(3, -2, 25) == "(x-3)^2+(y+2)^2=25"
    gen = standard_to_general(h=3, k=-2, r2=25)
    assert gen["general_form"] == "x^2+y^2-6x+4y-12=0"
    back = center_radius_from_general(d=-6, e=4, f=-12)
    assert back["canonical"]["圓心"] == "(3, -2)"
    assert back["canonical"]["半徑"] == "5"
    scaled = center_radius_from_standard(h=3, k=0, r2=9, scale=4)
    assert scaled["canonical"]["圓心"] == "(3, 0)"
    assert scaled["r2"] == sp.Rational(9, 4)


def test_conversion_validity_conditions():
    assert circle_validity_from_general(d=-6, e=4, f=13)["label"] == "一點"
    assert circle_validity_from_general(d=3, e=-4, f=8)["label"] == "無圖形"
    assert circle_validity_from_general(d=-2, e=4, f=-11)["label"] == "圓"
    rng = solve_circle_parameter_range(d_expr=4, e_expr="2*k", f_expr=5, param="k")
    assert "k" in rng["canonical"]
    assert ">" in rng["canonical"] or "<" in rng["canonical"] or "le" in rng["canonical"] or "ge" in rng["canonical"]


def test_condition_based_construction():
    pt = standard_from_center_point(center=[1, -2], point=[3, -4])
    assert pt["r2"] == 8
    diam = circle_from_diameter(a=[2, 4], b=[-4, 2])
    assert diam["canonical"] == "(x+1)^2+(y-3)^2=10"
    circ = circle_through_three_points(a=[0, 3], b=[-1, 1], c=[2, 1])
    assert circ["validity"] == "circle"
    # Reverse: three points satisfy general form
    for x, y in ((0, 3), (-1, 1), (2, 1)):
        assert sp.simplify(x**2 + y**2 + circ["D"] * x + circ["E"] * y + circ["F"]) == 0


def test_exact_arithmetic_halves():
    c = make_circle(h=sp.Rational(1, 2), k=sp.Rational(-3, 2), r=sp.Rational(5, 2))
    assert "0.5" not in c["standard_form"]
    assert "1/2" in c["standard_form"] or "\\frac" in c["latex_standard"]


def test_circle_equation_semantic_key_equivalence():
    from core.domain.circle_plane_domain import circle_semantic_key, standard_to_general

    gen = standard_to_general(h=1, k=-2, r2=9)["general_form"]
    std = "(x-1)^2+(y+2)^2=9"
    assert choice_semantic_key(std) == choice_semantic_key(gen)
    assert circle_semantic_key(std) == circle_semantic_key(gen)
    assert circle_semantic_key("x^2+y^2-2x+4y-4=0") == circle_semantic_key(gen)

@pytest.mark.parametrize("operation", sorted(OPS))
def test_matrix_validate_and_adapter(operation: str):
    matrix = build_circle_plane_matrix(operation=operation, seed=21)
    assert validate_circle_plane_matrix(matrix)
    payload = adapt_circle_plane_matrix(matrix, domain_operation=operation, seed=21)
    assert isinstance(payload, dict)
    assert payload.get("answer") is not None
    q = str(payload.get("question_text") or payload.get("question") or "")
    assert q and "placeholder" not in q.lower()


@pytest.mark.parametrize("seed", list(range(8)))
def test_seed_reproducibility(seed: int):
    a = build_circle_plane_matrix(operation="identify_center_radius_from_general", seed=seed)
    b = build_circle_plane_matrix(operation="identify_center_radius_from_general", seed=seed)
    assert a["answer"] == b["answer"]
    assert a["question"] == b["question"]
    c = build_circle_plane_matrix(operation="identify_center_radius_from_general", seed=seed + 1)
    # Different seeds should usually change instance; allow rare collision by checking givens
    assert a["givens"] != c["givens"] or a["answer"] != c["answer"]


def test_randomized_family_validation():
    failures: list[str] = []
    samples = 0
    for op in sorted(OPS):
        for seed in range(10):
            samples += 1
            try:
                m = build_circle_plane_matrix(operation=op, seed=seed)
                if not validate_circle_plane_matrix(m):
                    failures.append(f"{op}:{seed}:validate")
                    continue
                adapt_circle_plane_matrix(m, domain_operation=op, seed=seed)
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{op}:{seed}:{exc}")
    assert not failures, failures
    assert samples == len(OPS) * 10


def test_coverage_matrix_35_of_35():
    if not MATRIX_PATH.is_file():
        pytest.skip("coverage matrix not generated yet")
    data = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    sources = data["sources"]
    assert len(sources) == 35
    assert all(r["status"] == "COVERED" for r in sources)
    assert data["totals"]["intentional_skip"] == 0
    assert data["totals"]["NEEDS_CAPABILITY"] == 0
    assert data["totals"]["BLOCKED"] == 0
    assert sum(1 for r in sources if r["skill_id"].endswith("4_1_1")) == 16
    assert sum(1 for r in sources if r["skill_id"].endswith("4_1_2")) == 19
    ops = {r["domain_op"] for r in sources}
    assert ops <= set(OPS)
