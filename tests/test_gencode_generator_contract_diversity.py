from __future__ import annotations

from core.gencode.generator_contract_schema import (
    enrich_generator_contract,
    enrich_spec_generator_contract,
    validate_generator_contract,
)
from core.gencode.generator_diversity_sampling import (
    evaluate_diversity_metrics,
    run_diversity_sampling,
    sample_plan_from_contract,
    signature_key,
)
from core.gencode.problem_type_induction import _build_problem_type_spec_draft


def _minimal_spec(target_task: str, answer_type: str = "ordered_pair") -> dict:
    return enrich_spec_generator_contract(
        {
            "problem_type_id": f"pt_{target_task}",
            "skill_id": "mock_skill",
            "target_task": target_task,
            "task_family": "division_point_coordinates_family",
            "answer_contract": {"answer_type": answer_type, "answer_shape": "coordinate_pair"},
            "generator_contract": {},
        }
    )


def test_induced_spec_has_required_generator_contract_fields():
    cluster = {
        "answer_type": "ordered_pair",
        "features": [
            {
                "source_example_id": 1,
                "target_task": "compute_internal_division_point_coordinates",
                "task_family": "division_point_coordinates_family",
                "math_objects": ["section_ratio"],
                "semantic_classification": {
                    "selected_generator_contract": enrich_generator_contract(
                        "compute_internal_division_point_coordinates"
                    ),
                },
            }
        ],
        "signature": ("ordered_pair", "compute_internal_division_point_coordinates"),
        "merge_reason": "test",
    }
    spec, _ = _build_problem_type_spec_draft("mock_skill", cluster, set())
    gc = spec.get("generator_contract") or {}
    for key in (
        "template_variants",
        "parameter_schema",
        "variation_dimensions",
        "validity_constraints",
        "answer_shape",
    ):
        assert key in gc, f"missing {key}"


def test_division_internal_contract_has_ratio_and_coordinate_schema():
    gc = enrich_generator_contract("compute_internal_division_point_coordinates")
    ps = gc.get("parameter_schema") or {}
    assert "ratio" in ps
    assert "coordinate_range" in ps
    assert "answer_type_mode" in ps
    dims = gc.get("variation_dimensions") or []
    assert "ratio_form" in dims
    assert "ratio_values" in dims
    assert len(gc.get("template_variants") or []) >= 3


def test_centroid_contract_point_count_and_coordinate_range():
    gc = enrich_generator_contract("compute_centroid_coordinates")
    ps = gc.get("parameter_schema") or {}
    assert ps.get("point_count", {}).get("fixed") == 3
    assert "coordinate_range" in ps
    atm = ps.get("answer_type_mode") or {}
    assert "integer_centroid" in (atm.get("choices") or [])


def test_distance_contract_integer_radical_modes():
    gc = enrich_generator_contract("compute_distance_between_two_points")
    ps = gc.get("parameter_schema") or {}
    drt = ps.get("distance_result_type") or {}
    assert "integer" in (drt.get("choices") or [])
    assert "radical" in (drt.get("choices") or [])
    assert "coordinate_delta_pattern" in ps


def test_diversity_low_unique_signature_warning():
    sigs = [
        {
            "problem_type_id": "pt",
            "template_variant": "ratio_colon_form",
            "ratio_form": "AP:PB=m:n",
            "ratio_values": "2:3",
            "coordinate_pattern": "++",
            "answer": "(1,2)",
        }
    ] * 30
    metrics = evaluate_diversity_metrics(sigs, template_variant_ids=["ratio_colon_form", "multiple_form"])
    assert metrics["diversity_sampling_status"] in {
        "runtime_ready_with_diversity_warning",
        "generator_diversity_blocked",
    }
    assert metrics["unique_signature_count"] == 1
    assert "low_unique_signature_count" in metrics["repetition_warnings"]


def test_diversity_healthy_sampling_passes():
    spec = _minimal_spec("compute_internal_division_point_coordinates")
    metrics = run_diversity_sampling("mock_skill", spec, sample_count=30, base_seed=99)
    assert metrics["unique_signature_count"] >= 15
    assert metrics["diversity_sampling_status"] in {"passed", "runtime_ready_with_diversity_warning"}
    dist = metrics.get("template_variant_distribution") or {}
    assert len(dist) >= 2


def test_anti_repetition_signature_same_plan_same_key():
    spec = _minimal_spec("compute_internal_division_point_coordinates")
    p1 = sample_plan_from_contract(spec, 1)
    p2 = sample_plan_from_contract(spec, 1)
    assert signature_key(p1) == signature_key(p2)


def test_validate_contract_blockers_on_empty():
    blockers, _ = validate_generator_contract({})
    assert any("missing_generator_contract" in b for b in blockers)
