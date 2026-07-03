# -*- coding: utf-8 -*-
from __future__ import annotations

import pytest
from unittest.mock import patch
from core.gencode.classifiers import get_classifier_for_skill
from core.gencode.classifiers.coordinate_geometry_division_point import CoordinateGeometryDivisionPointClassifier
from core.gencode.classifiers.fallback_classifier import FallbackClassifier
from core.gencode.pipeline_orchestrator import run_v3_no_llm_phase1_for_example, PHASE1_CLASSIFICATION_UNRESOLVED


def test_dynamic_lookup_for_registered_skills() -> None:
    # 1. Midpoint coordinates has taxonomy and maps to division point domain
    clf_mid = get_classifier_for_skill("vh_數學B1_MidpointCoordinates")
    assert isinstance(clf_mid, CoordinateGeometryDivisionPointClassifier)

    # 2. Division point coordinates has taxonomy and maps to division point domain
    clf_div = get_classifier_for_skill("vh_數學B1_DivisionPointCoordinates")
    assert isinstance(clf_div, CoordinateGeometryDivisionPointClassifier)

    # 3. Distance between two parallel lines has taxonomy but maps to parallel lines domain (which uses fallback)
    clf_parallel = get_classifier_for_skill("vh_數學B1_DistanceBetweenTwoParallelLines")
    assert isinstance(clf_parallel, FallbackClassifier)


def test_unregistered_skill_fails_classification() -> None:
    skill_id = "vh_Unregistered_Dummy_Skill_123"
    clf = get_classifier_for_skill(skill_id)
    assert isinstance(clf, FallbackClassifier)

    # Classification should fail with phase1_classifier_not_registered
    row = {
        "id": 99999,
        "skill_id": skill_id,
        "problem_text": "A(1,1), B(2,2). Find midpoint.",
        "correct_answer": "",
        "detailed_solution": "",
    }
    res = run_v3_no_llm_phase1_for_example(skill_id, row)
    assert res.get("classification_status") == "unresolved"
    assert res.get("reason") == "phase1_classifier_not_registered"


def test_taxonomy_registered_but_no_classifier_fails_with_not_available() -> None:
    skill_id = "vh_數學B1_MockUnimplementedDomainSkill"
    
    with patch("core.registry.taxonomy_registry.is_confirmed_skill_binding", return_value=True), \
         patch("core.registry.taxonomy_registry.resolve_domain_for_skill", return_value={
             "fixed_domain_key": "algebra.unimplemented_domain",
             "allowed_types": ["dummy_op"],
         }):
         
        # Verify it has no custom python classifier
        clf = get_classifier_for_skill(skill_id)
        assert isinstance(clf, FallbackClassifier)
        
        # Verify it has no rule pack
        from core.gencode.pipeline_orchestrator import _load_registered_classifier_rulepack
        pack = _load_registered_classifier_rulepack(skill_id)
        assert pack is None
        
        # Classification should fail with phase1_classifier_not_available
        row = {
            "id": 99998,
            "skill_id": skill_id,
            "problem_text": "This is a dummy problem text.",
            "correct_answer": "",
            "detailed_solution": "",
        }
        res = run_v3_no_llm_phase1_for_example(skill_id, row)
        assert res.get("classification_status") == "unresolved"
        assert res.get("reason") == "phase1_classifier_not_available"


def test_parallelogram_refinement_rule() -> None:
    # Text with ONLY "平行四邊形" should NOT be classified as midpoint coordinates
    # unless it has diagonal/midpoint/flat-parallel context keywords.
    from core.gencode.classifiers.coordinate_geometry_division_point import _classify_example

    # Case A: Only parallelogram (unmatched midpoint context)
    example_unmatched = {
        "id": 8801,
        "problem_text": "求平行四邊形的面積大小。",
        "correct_answer": "10",
        "detailed_solution": "",
    }
    res_a = _classify_example(example_unmatched, "vh_數學B1_MidpointCoordinates")
    assert res_a.get("problem_type_id") == "unknown"

    # Case B: Parallelogram with midpoint context (vertices & D coordinate search)
    example_matched = {
        "id": 8802,
        "problem_text": "設 A(1,2), B(3,4), C(5,6) 為平行四邊形之頂點，求 D 點坐標。",
        "correct_answer": "(3,4)",
        "detailed_solution": "",
    }
    res_b = _classify_example(example_matched, "vh_數學B1_MidpointCoordinates")
    assert res_b.get("problem_type_id") == "compute_midpoint_coordinates"
