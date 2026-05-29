# -*- coding: utf-8 -*-
"""Phase 2 generator readiness: warnings vs blockers vs validation_failed."""

from __future__ import annotations

from core.gencode.generator_diversity_sampling import evaluate_diversity_metrics
from core.gencode.packaging_policy import (
    is_generator_usable_for_packaging,
    resolve_phase2_generator_status,
)


def _healthy_signatures(n: int = 30) -> list[dict]:
    sigs = []
    variants = ["direct_triangle_centroid", "worded_triangle_centroid"]
    for i in range(n):
        sigs.append(
            {
                "problem_type_id": "pt_centroid",
                "template_variant": variants[i % 2],
                "ratio_form": "centroid",
                "ratio_values": "n/a",
                "coordinate_pattern": "+-",
                "answer": f"({i},{i + 1})",
            }
        )
    return sigs


def test_healthy_diversity_28_unique_two_templates_no_blockers():
    metrics = evaluate_diversity_metrics(
        _healthy_signatures(30),
        template_variant_ids=["direct_triangle_centroid", "worded_triangle_centroid"],
        sample_count=30,
    )
    assert metrics["unique_signature_count"] == 30
    assert len(metrics.get("template_variant_distribution") or {}) == 2
    assert metrics.get("diversity_healthy") is True
    assert not metrics.get("diversity_blockers")
    assert metrics["diversity_sampling_status"] in {"passed", "runtime_ready_with_diversity_warning"}


def test_resolve_status_warnings_only_not_validation_failed():
    status, usable = resolve_phase2_generator_status(
        blockers=[],
        warnings=["low_source_examples", "consecutive_same_template_variant"],
        checker_smoke_status="passed",
        dynamic_sampling_status="runtime_ready_with_diversity_warning",
        base_status="runtime_ready",
    )
    assert status == "runtime_ready_with_warning"
    assert usable is True


def test_resolve_status_blockers_validation_failed():
    status, usable = resolve_phase2_generator_status(
        blockers=["generator_diversity_blocked"],
        warnings=["low_source_examples"],
        checker_smoke_status="passed",
        dynamic_sampling_status="generator_diversity_blocked",
        base_status="runtime_ready",
    )
    assert status == "validation_failed"
    assert usable is False


def test_usable_for_phase3_with_warnings_only():
    ok, reasons = is_generator_usable_for_packaging(
        {
            "problem_type_id": "pt_centroid",
            "generator_status": "runtime_ready_with_warning",
            "checker_smoke_status": "passed",
            "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
            "blockers": [],
            "warnings": ["low_source_examples", "consecutive_same_template_variant"],
            "usable_for_phase3": True,
        }
    )
    assert ok is True
    assert reasons == []


def test_centroid_like_metrics_simulation():
    """Simulate DivisionPointCoordinates centroid row: unique_sig=28, 2 templates, diversity warnings only."""
    sigs = _healthy_signatures(30)[:28] + _healthy_signatures(2)
    metrics = evaluate_diversity_metrics(
        sigs,
        template_variant_ids=["direct_triangle_centroid", "worded_triangle_centroid"],
        sample_count=30,
    )
    assert metrics["unique_signature_count"] >= 28
    assert len(metrics.get("template_variant_distribution") or {}) >= 2
    assert not metrics.get("diversity_blockers")

    status, usable = resolve_phase2_generator_status(
        blockers=list(metrics.get("diversity_blockers") or []),
        warnings=["low_source_examples"] + list(metrics.get("repetition_warnings") or []),
        checker_smoke_status="passed",
        dynamic_sampling_status=str(metrics.get("diversity_sampling_status", "passed")),
        base_status="runtime_ready",
    )
    assert status == "runtime_ready_with_warning"
    assert usable is True
    assert status != "validation_failed"
