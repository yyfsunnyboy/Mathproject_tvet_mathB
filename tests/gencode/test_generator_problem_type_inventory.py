# -*- coding: utf-8 -*-
"""Unit tests for Generator problem-type inventory counting rules."""
from __future__ import annotations

from pathlib import Path

from core.gencode.services.generator_problem_type_inventory import (
    build_generator_problem_type_count_map,
    format_problem_type_count_display,
    inventory_skill_generator_problem_types,
    normalize_problem_type_id,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_skill_tree(
    root: Path,
    skill_id: str,
    *,
    specs: list[dict],
    keys: list[str] | None = None,
    with_facade: bool = True,
    with_package: bool = True,
    generate_components: list[str] | None = None,
    facade_specs: list[dict] | None = None,
    package_specs: list[dict] | None = None,
    facade_keys: list[str] | None = None,
    package_keys: list[str] | None = None,
) -> None:
    keys = keys if keys is not None else [str(s["component_id"]) for s in specs]
    facade_specs = facade_specs if facade_specs is not None else specs
    package_specs = package_specs if package_specs is not None else specs
    facade_keys = facade_keys if facade_keys is not None else keys
    package_keys = package_keys if package_keys is not None else keys
    generate_components = generate_components if generate_components is not None else keys

    if with_facade:
        _write(
            root / "skills" / f"{skill_id}.py",
            (
                f"SKILL_ID = {skill_id!r}\n"
                f"GENERATOR_KEYS = {facade_keys!r}\n"
                f"GENERATOR_SPECS = {facade_specs!r}\n"
            ),
        )
    if with_package:
        pkg = root / "agent_skills_v3" / skill_id
        _write(
            pkg / "__init__.py",
            (
                f"SKILL_ID = {skill_id!r}\n"
                f"GENERATOR_KEYS = {package_keys!r}\n"
                f"GENERATOR_SPECS = {package_specs!r}\n"
            ),
        )
        for cid in generate_components:
            _write(pkg / "components" / cid / "generate.py", "def generate(**kwargs):\n    return {}\n")


def test_normalize_strips_numeric_variant_only() -> None:
    assert normalize_problem_type_id("slope_from_two_points_2") == "slope_from_two_points"
    assert normalize_problem_type_id("slope_from_two_points_special") == "slope_from_two_points_special"


def test_format_display_labels() -> None:
    assert format_problem_type_count_display(5) == "5 種"
    assert format_problem_type_count_display(0) == "0 種"
    assert format_problem_type_count_display(None) == "—"


def test_legacy_problem_type_specs_without_component_still_count(tmp_path: Path) -> None:
    skill_id = "vh_數學B1_LegacyTypes"
    specs = [
        {
            "problem_type_id": "legacy_a",
            "generator_readiness": "runtime_ready",
            "presentation_mode": "short_answer",
        },
        {
            "problem_type_id": "legacy_b",
            "generator_readiness": "runtime_ready",
            "presentation_mode": "short_answer",
        },
    ]
    _write(
        tmp_path / "skills" / f"{skill_id}.py",
        f"SKILL_ID = {skill_id!r}\nGENERATOR_KEYS = []\nGENERATOR_SPECS = {specs!r}\n",
    )
    inv = inventory_skill_generator_problem_types(skill_id, project_root=tmp_path)
    assert inv["usable_problem_type_count"] == 2
    assert inv["display_label"] == "2 種"


def test_one_generator_one_problem_type(tmp_path: Path) -> None:
    skill_id = "vh_數學B1_OneType"
    specs = [
        {
            "component_id": "src_1",
            "generator_key": "src_1",
            "problem_type_id": "type_a",
            "line_type": "type_a",
        }
    ]
    _make_skill_tree(tmp_path, skill_id, specs=specs)
    inv = inventory_skill_generator_problem_types(skill_id, project_root=tmp_path)
    assert inv["generator_impl_count"] == 1
    assert inv["usable_problem_type_count"] == 1
    assert inv["usable_problem_type_ids"] == ["type_a"]
    assert inv["display_label"] == "1 種"
    assert inv["health"] == "PASS"


def test_one_generator_multiple_problem_types_via_specs(tmp_path: Path) -> None:
    """Same generate.py registered under multiple specs still dedupes by problem_type_id;
    here one impl can appear with multiple type rows only if multiple components share types —
    this case: one component declares one type; multi-type comes from multiple components
    that intentionally map distinct types (one generator module can still expose one type).
    """
    skill_id = "vh_數學B1_MultiType"
    specs = [
        {"component_id": "src_1", "problem_type_id": "type_a", "line_type": "fam_a"},
        {"component_id": "src_2", "problem_type_id": "type_b", "line_type": "fam_b"},
        {"component_id": "src_3", "problem_type_id": "type_c", "line_type": "fam_c"},
    ]
    _make_skill_tree(tmp_path, skill_id, specs=specs)
    inv = inventory_skill_generator_problem_types(skill_id, project_root=tmp_path)
    assert inv["generator_impl_count"] == 3
    assert inv["usable_problem_type_count"] == 3
    assert inv["family_count"] == 3
    assert inv["display_label"] == "3 種"


def test_multiple_generators_same_problem_type_deduped(tmp_path: Path) -> None:
    skill_id = "vh_數學B1_SharedType"
    specs = [
        {"component_id": "src_1", "problem_type_id": "shared_type", "line_type": "shared_type"},
        {"component_id": "src_2", "problem_type_id": "shared_type", "line_type": "shared_type"},
        {"component_id": "src_3", "problem_type_id": "shared_type_1", "line_type": "shared_type"},
    ]
    _make_skill_tree(tmp_path, skill_id, specs=specs)
    inv = inventory_skill_generator_problem_types(skill_id, project_root=tmp_path)
    assert inv["generator_impl_count"] == 3
    # shared_type and shared_type_1 normalize to the same identity
    assert inv["usable_problem_type_count"] == 1
    assert inv["display_label"] == "1 種"


def test_random_variants_do_not_inflate_type_count(tmp_path: Path) -> None:
    skill_id = "vh_數學B1_Variants"
    specs = [
        {"component_id": "src_1", "problem_type_id": "pt_main"},
        {"component_id": "src_2", "problem_type_id": "pt_main_2"},
        {"component_id": "src_3", "problem_type_id": "pt_main_3"},
    ]
    _make_skill_tree(tmp_path, skill_id, specs=specs)
    inv = inventory_skill_generator_problem_types(skill_id, project_root=tmp_path)
    assert inv["usable_problem_type_count"] == 1


def test_registry_without_generator_impl(tmp_path: Path) -> None:
    skill_id = "vh_數學B1_RegistryOnly"
    specs = [{"component_id": "src_1", "problem_type_id": "type_a"}]
    _make_skill_tree(
        tmp_path,
        skill_id,
        specs=specs,
        generate_components=[],  # no generate.py
    )
    inv = inventory_skill_generator_problem_types(skill_id, project_root=tmp_path)
    assert inv["generator_impl_count"] == 0
    assert inv["usable_problem_type_count"] == 0
    assert inv["defined_problem_type_count"] == 1
    assert inv["not_runtime_problem_type_count"] == 1
    assert inv["display_label"] == "0 種"
    assert inv["health"] == "WARN"


def test_outline_skill_counts_zero(tmp_path: Path) -> None:
    skill_id = "outline_vocational_數學B1_11"
    specs = [{"component_id": "src_1", "problem_type_id": "should_not_count"}]
    _make_skill_tree(tmp_path, skill_id, specs=specs)
    inv = inventory_skill_generator_problem_types(
        skill_id, project_root=tmp_path, category="outline"
    )
    assert inv["is_outline"] is True
    assert inv["usable_problem_type_count"] == 0
    assert inv["display_label"] == "0 種"
    assert "outline_skill_excluded_from_executable_types" in inv["anomalies"]


def test_defined_but_unpublished_not_counted_as_usable(tmp_path: Path) -> None:
    skill_id = "vh_數學B1_Unpublished"
    package_only = [
        {"component_id": "src_1", "problem_type_id": "type_a"},
        {"component_id": "src_2", "problem_type_id": "type_b"},
    ]
    _make_skill_tree(
        tmp_path,
        skill_id,
        specs=package_only,
        with_facade=False,
        with_package=True,
    )
    inv = inventory_skill_generator_problem_types(skill_id, project_root=tmp_path)
    assert inv["generator_impl_count"] == 2
    assert inv["usable_problem_type_count"] == 0
    assert inv["defined_problem_type_count"] == 2
    assert inv["not_runtime_problem_type_count"] == 2
    assert inv["display_label"] == "0 種"
    assert "facade_missing_package_only_not_runtime" in inv["anomalies"]


def test_facade_non_literal_specs_fallback_to_package(tmp_path: Path) -> None:
    skill_id = "vh_數學B1_CartesianLike"
    package_specs = [
        {"component_id": "src_1", "problem_type_id": "type_a", "line_type": "type_a"},
        {"component_id": "src_2", "problem_type_id": "type_b", "line_type": "type_b"},
    ]
    keys = ["src_1", "src_2"]
    _write(
        tmp_path / "skills" / f"{skill_id}.py",
        (
            f"SKILL_ID = {skill_id!r}\n"
            f"GENERATOR_KEYS = {keys!r}\n"
            "GENERATOR_SPECS = [\n"
            "  {'component_id': cid, 'problem_type_id': pt}\n"
            "  for cid, pt in (('src_1', 'type_a'), ('src_2', 'type_b'))\n"
            "]\n"
        ),
    )
    _make_skill_tree(
        tmp_path,
        skill_id,
        specs=package_specs,
        keys=keys,
        with_facade=False,
        with_package=True,
    )
    inv = inventory_skill_generator_problem_types(skill_id, project_root=tmp_path)
    assert inv["usable_problem_type_count"] == 2
    assert inv["display_label"] == "2 種"
    assert "facade_generator_specs_not_literal_using_package" in inv["anomalies"]


def test_missing_or_unreadable_metadata_is_em_dash(tmp_path: Path) -> None:
    skill_id = "vh_數學B1_BrokenMeta"
    _write(
        tmp_path / "skills" / f"{skill_id}.py",
        "SKILL_ID = 'vh_數學B1_BrokenMeta'\nGENERATOR_SPECS = [broken]\n",
    )
    _write(
        tmp_path / "agent_skills_v3" / skill_id / "__init__.py",
        "SKILL_ID = 'vh_數學B1_BrokenMeta'\nGENERATOR_SPECS = [broken]\n",
    )
    inv = inventory_skill_generator_problem_types(skill_id, project_root=tmp_path)
    assert inv["usable_problem_type_count"] is None
    assert inv["display_label"] == "—"
    assert inv["health"] == "UNKNOWN"


def test_batch_map_and_admin_display_consistency(tmp_path: Path) -> None:
    skill_a = "vh_數學B1_A"
    skill_b = "outline_vocational_數學B1_x"
    _make_skill_tree(
        tmp_path,
        skill_a,
        specs=[
            {"component_id": "src_1", "problem_type_id": "a1"},
            {"component_id": "src_2", "problem_type_id": "a2"},
        ],
    )
    mapping = build_generator_problem_type_count_map(
        [skill_a, skill_b],
        project_root=tmp_path,
        categories={skill_b: "outline"},
    )
    assert mapping[skill_a]["display_label"] == "2 種"
    assert mapping[skill_b]["display_label"] == "0 種"


def test_src_4584_static_regression_binding() -> None:
    """Static regression: src_4584 belongs to point-line skill, not parallel-lines."""
    point = inventory_skill_generator_problem_types("vh_數學B1_DistanceBetweenPointAndLine")
    parallel = inventory_skill_generator_problem_types("vh_數學B1_DistanceBetweenTwoParallelLines")
    from core.gencode.services.gencode_status_query_service import load_v3_skill_generator_specs

    point_specs = load_v3_skill_generator_specs(skill_id="vh_數學B1_DistanceBetweenPointAndLine")
    parallel_specs = load_v3_skill_generator_specs(skill_id="vh_數學B1_DistanceBetweenTwoParallelLines")
    point_ids = {str(r.get("component_id")) for r in point_specs}
    parallel_ids = {str(r.get("component_id")) for r in parallel_specs}
    assert "src_4584" in point_ids
    assert "src_4584" not in parallel_ids
    assert point["usable_problem_type_count"] is not None
    assert parallel["usable_problem_type_count"] is not None


def test_slope_of_a_line_static_has_usable_types() -> None:
    inv = inventory_skill_generator_problem_types("vh_數學B1_SlopeOfALine")
    assert inv["generator_impl_count"] >= 1
    assert inv["usable_problem_type_count"] is not None
    assert inv["usable_problem_type_count"] >= 1
    assert inv["display_label"].endswith("種")
