# -*- coding: utf-8 -*-
"""Isolated dry-run tests for V3 component draft hook."""

from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from core.gencode.pipeline_orchestrator import build_v3_component_draft_from_skill

FORBIDDEN_GENERATE_TOKENS = (
    "import sympy",
    "import matplotlib",
    "Flask",
    "db.session",
    "textbook_examples",
    "SkillInfo",
)

FORBIDDEN_MATH_HELPER_TOKENS = (
    "_compute_slope",
    "_build_distractors",
    "gcd(",
    "Fraction(",
)

POINT_SLOPE_TEXTBOOK_ROW = {
    "id": 1,
    "skill_id": "vh_數學B1_PointSlopeForm",
    "problem_text": "已知點 $(1,2)$ 與斜率 $3$，求直線方程式。",
    "correct_answer": "$y-2=3(x-1)$",
    "source_description": "例題1",
    "problem_type": "point_slope",
}
POINT_SLOPE_CONSTRAINTS = {
    "line_type": "point_slope",
    "problem_type_id": "point_slope",
    "domain_operation": "point_slope",
}


def test_build_v3_component_draft_from_skill_ex_example():
    result = build_v3_component_draft_from_skill(
        skill_id="vh_數學B1_PointSlopeForm",
        textbook_example_id=1,
        source_kind="ex_1",
        seed=42,
        textbook_row=POINT_SLOPE_TEXTBOOK_ROW,
        constraints=POINT_SLOPE_CONSTRAINTS,
    )

    assert result["status"] == "draft_built"
    assert result["line_type"] == "point_slope"
    assert result["skill_id"] == "vh_數學B1_PointSlopeForm"
    assert result["textbook_example_id"] == 1
    assert result["source_kind"] in {"ex_1", "example"}
    assert result["domain_module"] == (
        "core.domain.coordinate_geometry.line_equation_domain"
    )
    assert result["entrypoint"] == "build_line_equation_matrix"

    files = result["files"]
    assert isinstance(files, dict)
    assert set(files.keys()) == {"metadata.py", "generate.py", "get_hint.py"}
    for content in files.values():
        assert isinstance(content, str)
        assert content.strip()


def test_generate_py_string_is_porter_safe():
    result = build_v3_component_draft_from_skill(
        skill_id="vh_數學B1_PointSlopeForm",
        textbook_example_id=1,
        source_kind="ex_1",
        seed=42,
        textbook_row=POINT_SLOPE_TEXTBOOK_ROW,
        constraints=POINT_SLOPE_CONSTRAINTS,
    )
    generate_source = result["files"]["generate.py"]

    assert "build_line_equation_matrix" in generate_source
    assert "convert_domain_matrix_to_question_payload" in generate_source

    for token in FORBIDDEN_GENERATE_TOKENS:
        assert token not in generate_source

    for token in FORBIDDEN_MATH_HELPER_TOKENS:
        assert token not in generate_source


def test_metadata_py_injects_ex_source_kind_profile():
    result = build_v3_component_draft_from_skill(
        skill_id="vh_數學B1_PointSlopeForm",
        textbook_example_id=1,
        source_kind="ex_1",
        seed=42,
        textbook_row=POINT_SLOPE_TEXTBOOK_ROW,
        constraints=POINT_SLOPE_CONSTRAINTS,
    )
    metadata_source = result["files"]["metadata.py"]
    assert "ORDER_WEIGHT: Final[int] = 10" in metadata_source
    assert 'DIFFICULTY_LEVEL: Final[str] = "easy"' in metadata_source


def test_dry_run_hook_does_not_write_to_disk(monkeypatch: pytest.MonkeyPatch):
    write_calls: list[tuple[str, str]] = []

    def _blocked_open(file, mode="r", *args, **kwargs):  # type: ignore[no-untyped-def]
        mode_text = str(mode)
        if "w" in mode_text or "a" in mode_text or "+" in mode_text:
            write_calls.append((str(file), mode_text))
            raise AssertionError(f"unexpected disk write via open(): {file!r} mode={mode_text!r}")
        return builtins.open(file, mode, *args, **kwargs)

    def _blocked_write_text(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        write_calls.append((str(self), "write_text"))
        raise AssertionError(f"unexpected disk write via Path.write_text(): {self!r}")

    monkeypatch.setattr(builtins, "open", _blocked_open)
    monkeypatch.setattr(Path, "write_text", _blocked_write_text)

    result = build_v3_component_draft_from_skill(
        skill_id="vh_數學B1_PointSlopeForm",
        textbook_example_id=1,
        source_kind="ex_1",
        seed=42,
        textbook_row=POINT_SLOPE_TEXTBOOK_ROW,
        constraints=POINT_SLOPE_CONSTRAINTS,
    )
    assert result["status"] == "draft_built"
    assert write_calls == []


def test_unregistered_skill_raises_domain_unresolved():
    with pytest.raises(ValueError, match="DOMAIN_CAPABILITY_UNRESOLVED|no_required_capabilities|domain_capability|Unregistered"):
        build_v3_component_draft_from_skill(
            skill_id="vh_數學B1_NotRegisteredSkill",
            textbook_example_id=99,
            source_kind="ex_9",
            seed=1,
            textbook_row={
                **POINT_SLOPE_TEXTBOOK_ROW,
                "id": 99,
                "skill_id": "vh_數學B1_NotRegisteredSkill",
            },
        )


@pytest.mark.parametrize(
    ("source_kind", "expected_line_type"),
    [
        ("quiz_3", "two_points"),
        ("test_4", "two_points"),
    ],
)
def test_source_kind_line_type_mapping(source_kind: str, expected_line_type: str):
    result = build_v3_component_draft_from_skill(
        skill_id="vh_數學B1_PointSlopeForm",
        textbook_example_id=2,
        source_kind=source_kind,
        seed=7,
        textbook_row={
            **POINT_SLOPE_TEXTBOOK_ROW,
            "id": 2,
            "problem_text": "已知兩點 $(0,0)$ 與 $(2,4)$，求直線方程式。",
        },
        constraints={
            "line_type": expected_line_type,
            "problem_type_id": expected_line_type,
            "domain_operation": expected_line_type,
        },
    )
    assert result["line_type"] == expected_line_type


def test_constraints_line_type_override():
    result = build_v3_component_draft_from_skill(
        skill_id="vh_數學B1_PointSlopeForm",
        textbook_example_id=3,
        source_kind="quiz_1",
        seed=5,
        constraints={"line_type": "horizontal_line"},
        textbook_row={
            **POINT_SLOPE_TEXTBOOK_ROW,
            "id": 3,
            "problem_text": "求通過點 $(1,2)$ 的水平線方程式。",
        },
    )
    assert result["line_type"] == "horizontal_line"
