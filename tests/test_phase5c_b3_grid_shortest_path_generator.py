"""Phase 5C-B3-B: grid shortest path (right/up) deterministic generator."""

from __future__ import annotations

import pytest

from core.vocational_math_b4.adaptive import b4_chapter1_deterministic_allowlist as allow
from core.vocational_math_b4.domain.counting_domain_functions import combination
from core.vocational_math_b4.generators import combination as combination_generators
from core.vocational_math_b4.services.question_router import generate_for_skill

COMB_APP_SKILL = "vh_數學B4_CombinationApplications"
GRID_PT = "grid_shortest_path_count"
EXCLUDED = frozenset(
    {
        "binomial_expansion_basic",
        "tree_diagram_listing",
        "pascal_triangle_derivation",
    }
)


def test_basic_variant_formula_preset_seed_1() -> None:
    payload = combination_generators.grid_shortest_path_count(
        skill_id=COMB_APP_SKILL,
        subskill_id="b4_ch1_grid_shortest_path_01",
        difficulty=1,
        seed=1,
        multiple_choice=False,
    )
    assert payload["parameters"]["variant"] == "basic"
    w, h = payload["parameters"]["width"], payload["parameters"]["height"]
    assert payload["answer"] == combination(w + h, w)


def test_via_point_variant_formula_preset_seed_2() -> None:
    payload = combination_generators.grid_shortest_path_count(
        skill_id=COMB_APP_SKILL,
        subskill_id="b4_ch1_grid_shortest_path_01",
        difficulty=1,
        seed=2,
        multiple_choice=False,
    )
    assert payload["parameters"]["variant"] == "via_point"
    w, h = payload["parameters"]["width"], payload["parameters"]["height"]
    mx, my = payload["parameters"]["mid_x"], payload["parameters"]["mid_y"]
    assert mx is not None and my is not None
    expected = combination(mx + my, mx) * combination((w - mx) + (h - my), w - mx)
    assert payload["answer"] == expected


def test_avoid_point_variant_formula_preset_seed_3() -> None:
    payload = combination_generators.grid_shortest_path_count(
        skill_id=COMB_APP_SKILL,
        subskill_id="b4_ch1_grid_shortest_path_01",
        difficulty=1,
        seed=3,
        multiple_choice=False,
    )
    assert payload["parameters"]["variant"] == "avoid_point"
    total = payload["parameters"]["total_paths"]
    via = payload["parameters"]["via_paths"]
    assert payload["answer"] == total - via
    assert payload["answer"] > 0


@pytest.mark.parametrize("seed", range(1, 101))
def test_seed_sampling_contract(seed: int) -> None:
    payload = combination_generators.grid_shortest_path_count(
        skill_id=COMB_APP_SKILL,
        subskill_id="b4_ch1_grid_shortest_path_01",
        difficulty=2,
        seed=seed,
        multiple_choice=True,
    )
    assert payload["problem_type_id"] == GRID_PT
    assert isinstance(payload["answer"], int)
    assert payload["answer"] > 0
    par = payload["parameters"]
    w, h = par["width"], par["height"]
    total = combination(w + h, w)
    assert par["total_paths"] == total
    v = par["variant"]
    if v == "basic":
        assert par["via_paths"] == 0
        assert par["mid_x"] is None
        assert payload["answer"] == total
    elif v == "via_point":
        mx, my = par["mid_x"], par["mid_y"]
        via = combination(mx + my, mx) * combination((w - mx) + (h - my), w - mx)
        assert par["via_paths"] == via
        assert payload["answer"] == via
    else:
        assert v == "avoid_point"
        mx, my = par["mid_x"], par["mid_y"]
        via = combination(mx + my, mx) * combination((w - mx) + (h - my), w - mx)
        assert par["via_paths"] == via
        assert payload["answer"] == total - via

    assert "畫圖" not in payload["question_text"]
    assert "圖片" not in payload["question_text"]
    assert "請畫" not in payload["question_text"]
    assert "$" in payload["explanation"] or "\\" in payload["explanation"]
    assert "C^{" in payload["explanation"] or "C_{" in payload["explanation"]

    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(COMB_APP_SKILL, payload)
    assert ok, reason


def test_variants_all_appear_in_seed_range() -> None:
    found = set()
    for seed in range(1, 101):
        payload = combination_generators.grid_shortest_path_count(
            skill_id=COMB_APP_SKILL,
            subskill_id="b4_ch1_grid_shortest_path_01",
            difficulty=2,
            seed=seed,
            multiple_choice=False,
        )
        found.add(payload["parameters"]["variant"])
    assert found == {"basic", "via_point", "avoid_point"}


def test_router_explicit_grid_problem_type() -> None:
    payload = generate_for_skill(
        skill_id=COMB_APP_SKILL,
        level=1,
        seed=42,
        problem_type_id=GRID_PT,
    )
    assert payload["problem_type_id"] == GRID_PT
    ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(COMB_APP_SKILL, payload)
    assert ok, reason


def test_router_sampling_includes_grid_type() -> None:
    seen: set[str] = set()
    for seed in range(1, 1200):
        payload = generate_for_skill(skill_id=COMB_APP_SKILL, level=1, seed=seed)
        seen.add(payload["problem_type_id"])
        assert payload["problem_type_id"] not in EXCLUDED
    assert GRID_PT in seen


def test_validator_still_blocks_excluded_problem_types() -> None:
    for pid in EXCLUDED:
        ok, reason = allow.validate_b4_deterministic_adaptive_generator_payload(
            COMB_APP_SKILL,
            {"problem_type_id": pid, "generator_key": "x"},
        )
        assert ok is False
        assert reason is not None
