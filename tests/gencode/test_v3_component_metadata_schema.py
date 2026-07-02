# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import pytest

from core.gencode.v3_component_metadata_migration import (
    rebuild_component_metadata_from_generator_specs,
)
from core.gencode.v3_component_scaffold_builder import (
    _build_metadata_py,
    build_component_files_from_domain_payload,
)
from core.gencode.v3_component_spec_validator import (
    assert_generator_specs_metadata_consistent,
    validate_generator_spec_against_metadata,
)


SKILL_ID = "vh_數學B1_GeneralFormOfLinearEquation"
DOMAIN_META = {
    "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
    "entrypoint": "build_line_equation_matrix",
}


def _spec(
    component_id: str,
    *,
    problem_type_id: str,
    presentation_mode: str = "short_answer",
    response_mode: str = "expression",
    answer_value_type: str = "linear_equation",
) -> dict[str, object]:
    return {
        "textbook_example_id": int(component_id.rsplit("_", 1)[-1]),
        "component_id": component_id,
        "generator_key": component_id,
        "presentation_mode": presentation_mode,
        "response_mode": response_mode,
        "interaction_type": response_mode,
        "answer_type": answer_value_type,
        "answer_value_type": answer_value_type,
        "problem_type_id": problem_type_id,
        "source_kind": f"ex_{component_id.rsplit('_', 1)[-1]}",
        "line_type": "general_form",
        "display_order": int(component_id.rsplit("_", 1)[-1]),
        "source_order": int(component_id.rsplit("_", 1)[-1]),
        "sampling_weight": 10,
    }


def _write_component_metadata(root: Path, spec: dict[str, object]) -> Path:
    component_id = str(spec["component_id"])
    comp_dir = root / SKILL_ID / "components" / component_id
    comp_dir.mkdir(parents=True)
    source = _build_metadata_py(
        skill_id=SKILL_ID,
        component_id=component_id,
        source_kind=str(spec.get("source_kind") or component_id),
        order_weight=10,
        difficulty_level="easy",
        domain_meta=DOMAIN_META,
        payload_meta={**spec, "target_task": spec["problem_type_id"]},
        textbook_example_id=int(spec["textbook_example_id"]),
    )
    path = comp_dir / "metadata.py"
    path.write_text(source, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("response_mode", "answer_value_type"),
    [
        ("single_choice", "linear_equation"),
        ("expression", "rational"),
        ("expression", "numeric_or_undefined"),
    ],
)
def test_response_mode_and_answer_value_type_are_independent(tmp_path: Path, response_mode: str, answer_value_type: str):
    presentation_mode = "single_choice" if response_mode == "single_choice" else "short_answer"
    spec = _spec(
        "src_4599",
        problem_type_id="perpendicular_bisector_application",
        presentation_mode=presentation_mode,
        response_mode=response_mode,
        answer_value_type=answer_value_type,
    )
    metadata_path = _write_component_metadata(tmp_path, spec)

    assert validate_generator_spec_against_metadata(spec, metadata_path) == []


def test_problem_type_id_mismatch_blocks(tmp_path: Path):
    spec = _spec("src_4566", problem_type_id="line_through_point_parallel_to_line")
    metadata_path = _write_component_metadata(tmp_path, {**spec, "problem_type_id": "wrong_problem_type"})

    errors = validate_generator_spec_against_metadata(spec, metadata_path)

    assert any("problem_type_id mismatch" in err for err in errors)
    assert "generator_spec.problem_type_id" in errors[0]
    assert "metadata problem_type_id" in errors[0]


def test_scaffold_default_target_task_does_not_override_component_spec():
    files = build_component_files_from_domain_payload(
        skill_id=SKILL_ID,
        component_id="src_4566",
        source_kind="ex_4566",
        domain_meta=DOMAIN_META,
        payload_meta={
            "problem_type_id": "line_through_point_parallel_to_line",
            "presentation_mode": "short_answer",
            "response_mode": "expression",
            "answer_value_type": "linear_equation",
            "answer_type": "linear_equation",
        },
        textbook_example_id=4566,
    )

    metadata = files["metadata.py"]
    assert 'TARGET_TASK: Final[str] = "line_through_point_parallel_to_line"' in metadata
    assert 'PROBLEM_TYPE_ID: Final[str] = "line_through_point_parallel_to_line"' in metadata
    assert "write_line_equation_from_point_slope" not in metadata


def test_legacy_metadata_rebuilds_from_generator_spec(tmp_path: Path):
    spec = _spec("src_4567", problem_type_id="line_through_point_perpendicular_to_line")
    comp_dir = tmp_path / SKILL_ID / "components" / "src_4567"
    comp_dir.mkdir(parents=True)
    (comp_dir / "metadata.py").write_text(
        'COMPONENT_ID = "src_4567"\nTARGET_TASK = "write_line_equation_from_point_slope"\nANSWER_TYPE = "expression"\n',
        encoding="utf-8",
    )

    result = rebuild_component_metadata_from_generator_specs(
        sandbox_root=tmp_path,
        skill_id=SKILL_ID,
        generator_specs=[spec],
        domain_meta=DOMAIN_META,
        write=True,
    )

    assert result["written"] == 1
    assert validate_generator_spec_against_metadata(spec, comp_dir / "metadata.py") == []
    rebuilt = (comp_dir / "metadata.py").read_text(encoding="utf-8")
    assert 'PROBLEM_TYPE_ID: Final[str] = "line_through_point_perpendicular_to_line"' in rebuilt
    assert 'ANSWER_VALUE_TYPE: Final[str] = "linear_equation"' in rebuilt


def test_general_form_representative_components_validate_after_rebuild(tmp_path: Path):
    rows = [
        ("src_4566", "line_through_point_parallel_to_line", "expression", "linear_equation"),
        ("src_4567", "line_through_point_perpendicular_to_line", "expression", "linear_equation"),
        ("src_4572", "slope_of_horizontal_or_vertical_line", "expression", "numeric_or_undefined"),
        ("src_4592", "parallel_line_slope", "single_choice", "numeric_or_undefined"),
        ("src_4593", "perpendicular_condition_parameter", "expression", "rational"),
        ("src_4594", "line_through_point_perpendicular_to_line", "single_choice", "linear_equation"),
        ("src_4599", "perpendicular_bisector_application", "single_choice", "linear_equation"),
    ]
    specs = []
    for component_id, problem_type_id, response_mode, answer_value_type in rows:
        spec = _spec(
            component_id,
            problem_type_id=problem_type_id,
            presentation_mode="single_choice" if response_mode == "single_choice" else "short_answer",
            response_mode=response_mode,
            answer_value_type=answer_value_type,
        )
        specs.append(spec)
        comp_dir = tmp_path / SKILL_ID / "components" / component_id
        comp_dir.mkdir(parents=True)
        (comp_dir / "metadata.py").write_text('TARGET_TASK = "write_line_equation_from_point_slope"\n', encoding="utf-8")

    result = rebuild_component_metadata_from_generator_specs(
        sandbox_root=tmp_path,
        skill_id=SKILL_ID,
        generator_specs=specs,
        domain_meta=DOMAIN_META,
        write=True,
    )

    assert result["errors"] == []
    assert_generator_specs_metadata_consistent(
        sandbox_root=str(tmp_path),
        skill_id=SKILL_ID,
        generator_specs=specs,
    )


@pytest.mark.parametrize(
    ("metadata_override", "expected"),
    [
        ({"response_mode": "single_choice"}, "response_mode mismatch"),
        ({"answer_value_type": "linear_equation"}, "answer_value_type mismatch"),
    ],
)
def test_true_response_or_answer_value_mismatch_blocks(tmp_path: Path, metadata_override: dict[str, str], expected: str):
    spec = _spec(
        "src_4593",
        problem_type_id="perpendicular_condition_parameter",
        response_mode="expression",
        answer_value_type="rational",
    )
    metadata_spec = {**spec, **metadata_override}
    metadata_path = _write_component_metadata(tmp_path, metadata_spec)

    errors = validate_generator_spec_against_metadata(spec, metadata_path)

    assert any(expected in err for err in errors)


DIVISION_SKILL = "vh_數學B1_DivisionPointCoordinates"


def _write_legacy_division_metadata(tmp_path: Path, component_id: str, *, presentation_mode: str, answer_value_type: str) -> Path:
    comp_dir = tmp_path / DIVISION_SKILL / "components" / component_id
    comp_dir.mkdir(parents=True)
    response_mode = "single_choice" if presentation_mode == "single_choice" else "short_answer"
    metadata = f'''COMPONENT_ID = "{component_id}"
PRESENTATION_MODE = "{presentation_mode}"
RESPONSE_MODE = "{response_mode}"
INTERACTION_TYPE = "{response_mode}"
ANSWER_VALUE_TYPE = "{answer_value_type}"
ANSWER_TYPE = "{answer_value_type}"
PROBLEM_TYPE_ID = "compute_internal_division_point_coordinates"
TARGET_TASK = PROBLEM_TYPE_ID
SOURCE_KIND = "example"
'''
    path = comp_dir / "metadata.py"
    path.write_text(metadata, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("component_id", "presentation_mode", "legacy_answer_type", "metadata_value_type"),
    [
        ("src_4420", "short_answer", "coordinate_pair", "coordinate_pair"),
        ("src_4512", "single_choice", "single_choice", "single_choice"),
        ("src_4513", "single_choice", "single_choice", "single_choice"),
    ],
)
def test_division_point_tracker_shape_normalizes_consistently(
    tmp_path: Path,
    component_id: str,
    presentation_mode: str,
    legacy_answer_type: str,
    metadata_value_type: str,
):
    spec = {
        "textbook_example_id": int(component_id.rsplit("_", 1)[-1]),
        "component_id": component_id,
        "presentation_mode": presentation_mode,
        "answer_type": legacy_answer_type,
        "problem_type_id": "compute_internal_division_point_coordinates",
        "source_kind": "example",
    }
    metadata_path = _write_legacy_division_metadata(
        tmp_path,
        component_id,
        presentation_mode=presentation_mode,
        answer_value_type=metadata_value_type,
    )
    assert validate_generator_spec_against_metadata(spec, metadata_path) == []


def test_staging_component_source_sync_includes_production_package(tmp_path: Path):
    from core.gencode.v3_production_publish_service import _sync_staging_v3_component_sources

    project = tmp_path / "project"
    staging = tmp_path / "staging"
    skill = DIVISION_SKILL
    component_id = "src_4420"
    prod_component = project / "agent_skills_v3" / skill / "components" / component_id
    prod_component.mkdir(parents=True)
    (prod_component / "generate.py").write_text("def generate(**kwargs):\n    return {}\n", encoding="utf-8")
    (prod_component / "metadata.py").write_text('COMPONENT_ID = "src_4420"\n', encoding="utf-8")
    (prod_component / "get_hint.py").write_text("def get_hint(*_a, **_k):\n    return ''\n", encoding="utf-8")
    (project / "agent_skills_v3" / skill / "component_runtime.py").write_text("# runtime\n", encoding="utf-8")

    result = _sync_staging_v3_component_sources(staging, skill, project_path=project)

    dest_generate = staging / "agent_skills_v3" / skill / "components" / component_id / "generate.py"
    dest_runtime = staging / "agent_skills_v3" / skill / "component_runtime.py"
    assert dest_generate.is_file()
    assert dest_runtime.is_file()
    assert component_id in result["synced_component_ids"]
