from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from core.gencode.pipeline_orchestrator import (
    _reinforce_canonical_answer_contract,
    _sanitize_coordinate_pair_answer_contract,
    _sync_phase3_runtime_specs_from_draft,
)
from core.gencode import problem_type_spec


def test_phase3_runtime_alignment_syncs_only_usable_reinforced_drafts(tmp_path):
    draft_spec = {
        "phase1_payload": {
            "candidate_problem_types": [
                {
                    "problem_type_id": "numeric_usable",
                    "problem_type_spec_draft": {
                        "problem_type_id": "numeric_usable_legacy_suffix",
                        "answer_contract": {
                            "answer_type": "single_choice",
                            "checker": "choice_label_checker",
                            "choices_required": True,
                        },
                        "generator_contract": {
                            "problem_type_id": "numeric_usable_nested_legacy_suffix"
                        },
                    },
                },
                {
                    "problem_type_id": "numeric_blocked",
                    "problem_type_spec_draft": {
                        "problem_type_id": "numeric_blocked",
                        "generator_contract": {},
                    },
                },
                {
                    "problem_type_id": "numeric_usable",
                    "problem_type_spec_draft": {
                        "problem_type_id": "single_choice_legacy_suffix_single_choice",
                        "generator_contract": {},
                    },
                },
            ]
        }
    }
    historical_row = {"problem_type_id": "single_choice_legacy_suffix"}
    usable = [{"problem_type_id": "numeric_usable"}, historical_row]
    old_path = tmp_path / "skill.json"
    temp_path = tmp_path / "skill.tmp.json"
    backup_path = tmp_path / "skill.backup.json"
    other_skill_path = tmp_path / "other_skill.json"
    non_json_path = tmp_path / "skill.notes.txt"
    old_path.write_text('{"items": [{"problem_type_id": "stale"}]}', encoding="utf-8")
    temp_path.write_text("{}", encoding="utf-8")
    backup_path.write_text("{}", encoding="utf-8")
    other_skill_path.write_text("{}", encoding="utf-8")
    non_json_path.write_text("keep", encoding="utf-8")

    with patch.object(problem_type_spec, "INDUCED_DIR", tmp_path), patch.dict(
        problem_type_spec._INDUCED_BY_SKILL,
        {"skill": [{"problem_type_id": "stale"}]},
        clear=True,
    ), patch(
        "core.gencode.pipeline_orchestrator.save_induced_problem_type_specs",
        return_value=Path("induced_specs/skill.json"),
    ) as save_specs:
        result = _sync_phase3_runtime_specs_from_draft("skill", draft_spec, usable)
        assert problem_type_spec._INDUCED_BY_SKILL["skill"] == []

    assert not old_path.exists()
    assert not temp_path.exists()
    assert not backup_path.exists()
    assert other_skill_path.exists()
    assert non_json_path.exists()
    saved_skill_id, saved_specs = save_specs.call_args.args
    assert saved_skill_id == "skill"
    assert [spec["problem_type_id"] for spec in saved_specs] == ["numeric_usable"]
    assert saved_specs[0]["skill_id"] == "skill"
    assert saved_specs[0]["generator_contract"]["problem_type_id"] == "numeric_usable"
    assert saved_specs[0]["answer_contract"]["answer_type"] == "numeric"
    assert saved_specs[0]["answer_contract"]["checker"] == "integer_checker"
    assert saved_specs[0]["answer_contract"]["choices_required"] is False
    assert saved_specs[0]["derivation"] == [
        "Step 1: Automated derivation initialized from source spec."
    ]
    assert saved_specs[0]["generator_contract"]["contextual_application"] is True
    assert historical_row["generator_readiness"] == "source_bank_only"
    assert historical_row["usable_for_phase3"] is False
    assert "phase3_zombie_problem_type_downgraded" in historical_row["warnings"]
    assert result["status"] == "synced"
    assert result["synced_problem_type_ids"] == ["numeric_usable"]
    assert result["runtime_usable_problem_type_ids"] == ["numeric_usable"]
    assert result["downgraded_historical_problem_type_ids"] == [
        "single_choice_legacy_suffix",
        "single_choice_legacy_suffix_single_choice",
    ]
    assert sorted(result["purged_induced_spec_paths"]) == sorted(
        [str(old_path), str(temp_path), str(backup_path)]
    )


def test_phase3_runtime_alignment_skips_when_no_usable_draft_matches(tmp_path):
    old_path = tmp_path / "skill.json"
    old_path.write_text('{"items": [{"problem_type_id": "stale"}]}', encoding="utf-8")

    with patch.object(problem_type_spec, "INDUCED_DIR", tmp_path), patch.dict(
        problem_type_spec._INDUCED_BY_SKILL,
        {"skill": [{"problem_type_id": "stale"}]},
        clear=True,
    ), patch(
        "core.gencode.pipeline_orchestrator.save_induced_problem_type_specs"
    ) as save_specs:
        result = _sync_phase3_runtime_specs_from_draft(
            "skill",
            {"phase1_payload": {"candidate_problem_types": []}},
            [{"problem_type_id": "numeric_missing"}],
        )
        assert problem_type_spec._INDUCED_BY_SKILL["skill"] == []

    save_specs.assert_not_called()
    assert not old_path.exists()
    assert result["status"] == "skipped_no_aligned_draft_specs"


def test_phase3_runtime_alignment_refreshes_auto_preferred_induced_cache(tmp_path):
    draft_spec = {
        "phase1_payload": {
            "candidate_problem_types": [
                {
                    "problem_type_id": "numeric_runtime_latest",
                    "problem_type_spec_draft": {
                        "problem_type_id": "numeric_runtime_latest",
                        "generator_contract": {},
                    },
                }
            ]
        }
    }

    with patch.object(problem_type_spec, "INDUCED_DIR", tmp_path), patch.dict(
        problem_type_spec._INDUCED_BY_SKILL,
        {},
        clear=True,
    ):
        result = _sync_phase3_runtime_specs_from_draft(
            "skill",
            draft_spec,
            [{"problem_type_id": "numeric_runtime_latest"}],
        )
        loaded = problem_type_spec.load_problem_type_spec(
            "skill",
            "numeric_runtime_latest",
            prefer="auto",
        )

    assert result["status"] == "synced"
    assert (tmp_path / "skill.json").exists()
    assert loaded is not None
    assert loaded["derivation"] == [
        "Step 1: Automated derivation initialized from source spec."
    ]
    assert loaded["generator_contract"]["contextual_application"] is True


def test_coordinate_pair_sanitizer_repairs_midpoint_text_contract():
    spec = {
        "target_task": "compute_midpoint_coordinates",
        "answer_contract": {
            "answer_type": "short_answer",
            "answer_equivalence": "exact_string",
            "equivalence_type": "exact_string",
            "checker": "text_short_checker",
            "checker_key": "text_short_checker",
            "fallback_checker": "text_short_checker",
        },
    }

    assert _sanitize_coordinate_pair_answer_contract(
        spec, "short_answer_compute_midpoint_coordinates"
    )
    ac = spec["answer_contract"]
    assert ac["answer_type"] == "coordinate_pair"
    assert ac["equivalence_type"] == "ordered_tuple_exact"
    assert ac["checker"] == "coordinate_pair_checker"
    assert ac["presentation_mode"] == "short_answer"
    assert "fallback_checker" not in ac


def test_coordinate_pair_sanitizer_keeps_single_choice_presentation_contract():
    spec = {
        "target_task": "compute_centroid_coordinates",
        "answer_contract": {
            "answer_type": "short_answer",
            "answer_equivalence": "exact_string",
            "checker": "text_short_checker",
        },
    }

    assert _sanitize_coordinate_pair_answer_contract(
        spec, "single_choice_compute_centroid_coordinates"
    )
    ac = spec["answer_contract"]
    assert ac["answer_type"] == "single_choice"
    assert ac["semantic_answer_shape"] == "coordinate_pair"
    assert ac["equivalence_type"] == "choice_label"
    assert ac["checker"] == "choice_label_checker"
    assert ac["presentation_mode"] == "single_choice"


def test_coordinate_pair_sanitizer_does_not_retype_scalar_median_length():
    spec = {
        "target_task": "compute_triangle_median_line",
        "answer_contract": {
            "answer_type": "numeric_or_radical",
            "answer_shape": "scalar",
            "checker": "expression_equivalence_checker",
        },
    }

    assert not _sanitize_coordinate_pair_answer_contract(
        spec, "numeric_or_radical_compute_triangle_median_line"
    )
    assert spec["answer_contract"]["answer_type"] == "numeric_or_radical"


def test_phase3_runtime_alignment_sanitizes_midpoint_contract_before_save(tmp_path):
    problem_type_id = "short_answer_compute_midpoint_coordinates"
    draft_spec = {
        "phase1_payload": {
            "candidate_problem_types": [
                {
                    "problem_type_id": problem_type_id,
                    "problem_type_spec_draft": {
                        "problem_type_id": problem_type_id,
                        "target_task": "compute_midpoint_coordinates",
                        "answer_contract": {
                            "answer_type": "short_answer",
                            "answer_equivalence": "exact_string",
                            "checker": "text_short_checker",
                        },
                        "generator_contract": {},
                    },
                }
            ]
        }
    }

    with patch.object(problem_type_spec, "INDUCED_DIR", tmp_path), patch.dict(
        problem_type_spec._INDUCED_BY_SKILL,
        {},
        clear=True,
    ), patch(
        "core.gencode.pipeline_orchestrator.save_induced_problem_type_specs",
        return_value=Path("induced_specs/skill.json"),
    ) as save_specs:
        result = _sync_phase3_runtime_specs_from_draft(
            "skill",
            draft_spec,
            [{"problem_type_id": problem_type_id}],
        )

    assert result["status"] == "synced"
    _, saved_specs = save_specs.call_args.args
    ac = saved_specs[0]["answer_contract"]
    assert ac["answer_type"] == "coordinate_pair"
    assert ac["equivalence_type"] == "ordered_tuple_exact"
    assert ac["checker"] == "coordinate_pair_checker"


def test_canonical_contract_reinforcement_repairs_linear_expression_checker():
    spec = {
        "problem_type_id": "linear_function_application",
        "target_task": "evaluate_function_value",
        "answer_contract": {
            "answer_type": "expression",
            "equivalence_type": "exact_string",
            "checker": "text_short_checker",
        },
    }

    assert _reinforce_canonical_answer_contract(spec) is spec
    ac = spec["answer_contract"]
    assert ac["equivalence_type"] == "algebraic_equivalent"
    assert ac["checker"] == "expression_checker"


def test_canonical_contract_reinforcement_applies_choice_shape_last():
    spec = {
        "problem_type_id": "expression_linear_function_choice",
        "target_task": "evaluate_function_value",
        "answer_contract": {
            "answer_type": "expression",
            "answer_shape": "choice_label",
            "equivalence_type": "exact_string",
            "checker": "text_short_checker",
        },
    }

    _reinforce_canonical_answer_contract(spec)
    ac = spec["answer_contract"]
    assert ac["answer_type"] == "single_choice"
    assert ac["equivalence_type"] == "choice_label"
    assert ac["checker"] == "choice_label_checker"
