# Gencode Phase3 Package Summary: vh_數學B1_DistanceBetweenTwoPointsInPlane

## phase3
```json
{
  "ok": true,
  "phase": "phase3",
  "skill_id": "vh_數學B1_DistanceBetweenTwoPointsInPlane",
  "sop_reference": {
    "sop_policy_version": "v0.3",
    "highest_sop": "docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md",
    "required_sop_files": [
      {
        "path": "docs/系統SOP/Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md",
        "exists": true,
        "readable": true,
        "mojibake_detected": false
      },
      {
        "path": "docs/系統SOP/Gencode_AgentSkillV2整合/AgentSkillV2_ProblemType規格包設計_v0.3.md",
        "exists": true,
        "readable": true,
        "mojibake_detected": false
      },
      {
        "path": "docs/系統SOP/Gencode_AgentSkillV2整合/AnswerContract_EquivalenceType_Gate_v0.3.md",
        "exists": true,
        "readable": true,
        "mojibake_detected": false
      }
    ],
    "sop_preflight_status": "PASS"
  },
  "remaining_todos": [
    "SOP v0.2 Verification: Verify that if a problem_type is verified, `/practice` must hit it within 50 rounds.",
    "SOP v0.2 Verification: Ensure Gencode runtime audit uses `generated_only` to prevent source_bank_pool masking generator distribution.",
    "SOP v0.2 Wrapper: Ensure wrapper state does not reload / reset state upon importlib.reload."
  ],
  "skill_file_path": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_DistanceBetweenTwoPointsInPlane.py",
  "package_status": "failed",
  "py_compile_status": "passed",
  "runtime_smoke_status": "failed",
  "runtime_smoke_raw": {
    "status": "failed",
    "blockers": [
      "runtime_smoke_generate_exception"
    ],
    "payload_preview": {
      "problem_type_id": null,
      "answer_type": null,
      "answer_contract_answer_type": null,
      "checker": null,
      "equivalence": null,
      "question_text_len": 0,
      "answer": null,
      "correct_answer": null,
      "choices_count": 0,
      "metadata_keys": []
    },
    "interface_check": {
      "generate_exists": true,
      "check_exists": true,
      "generate_returns_dict": false,
      "check_callable": true
    },
    "py_compile_status": "passed",
    "samples_tested": 0,
    "negative_semantic_smoke": "passed",
    "error": "generator_spec_not_found:empty_problem_type_id",
    "failed_seed": 0,
    "runtime_smoke_raw": {
      "exception_type": "RuntimeError",
      "exception_message": "generator_spec_not_found:empty_problem_type_id",
      "traceback_preview": "Traceback (most recent call last):\n  File \"e:\\Python/Mathproject_tvet_mathB\\core\\gencode\\runtime_smoke.py\", line 471, in _run_draft_runtime_smoke_impl\n    payload = gen(level=1, seed=seed)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_DistanceBetweenTwoPointsInPlane.py\", line 12, in generate\n    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)\n  File \"e:\\Python/Mathproject_tvet_mathB\\core\\gencode\\runtime_skill_wrapper.py\", line 175, in generate_for_skill\n    raise RuntimeError(\"generator_spec_not_found:empty_problem_type_id\")\nRuntimeError: generator_spec_not_found:empty_problem_type_id\n",
      "problem_type_id": null,
      "seed": 0
    }
  },
  "publish_check": {
    "draft_check_passed": false,
    "can_publish_draft": false,
    "can_publish_formal": false,
    "can_mark_runtime_ready": false,
    "formal_publish_blockers": [
      "draft_check_not_passed"
    ],
    "runtime_ready_blockers": [
      "runtime_ready_gate_not_allowed_or_not_verified"
    ],
    "warnings": [
      "draft_passed_but_runtime_ready_not_confirmed"
    ],
    "blockers": [
      "runtime_smoke_generate_exception"
    ],
    "py_compile_status": "passed",
    "interface_check": {
      "generate_exists": true,
      "check_exists": true,
      "generate_returns_dict": false,
      "check_callable": true
    },
    "runtime_smoke_status": "failed",
    "runtime_smoke_raw": {
      "status": "failed",
      "blockers": [
        "runtime_smoke_generate_exception"
      ],
      "payload_preview": {
        "problem_type_id": null,
        "answer_type": null,
        "answer_contract_answer_type": null,
        "checker": null,
        "equivalence": null,
        "question_text_len": 0,
        "answer": null,
        "correct_answer": null,
        "choices_count": 0,
        "metadata_keys": []
      },
      "interface_check": {
        "generate_exists": true,
        "check_exists": true,
        "generate_returns_dict": false,
        "check_callable": true
      },
      "py_compile_status": "passed",
      "samples_tested": 0,
      "negative_semantic_smoke": "passed",
      "error": "generator_spec_not_found:empty_problem_type_id",
      "failed_seed": 0,
      "runtime_smoke_raw": {
        "exception_type": "RuntimeError",
        "exception_message": "generator_spec_not_found:empty_problem_type_id",
        "traceback_preview": "Traceback (most recent call last):\n  File \"e:\\Python/Mathproject_tvet_mathB\\core\\gencode\\runtime_smoke.py\", line 471, in _run_draft_runtime_smoke_impl\n    payload = gen(level=1, seed=seed)\n  File \"E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_DistanceBetweenTwoPointsInPlane.py\", line 12, in generate\n    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)\n  File \"e:\\Python/Mathproject_tvet_mathB\\core\\gencode\\runtime_skill_wrapper.py\", line 175, in generate_for_skill\n    raise RuntimeError(\"generator_spec_not_found:empty_problem_type_id\")\nRuntimeError: generator_spec_not_found:empty_problem_type_id\n",
        "problem_type_id": null,
        "seed": 0
      }
    },
    "summary_message": "Draft is not ready for publish yet. Please resolve blockers first."
  },
  "generator_specs": [
    {
      "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "checker_key": "solution_set_checker",
      "equivalence_type": "unordered_solution_set",
      "generator_readiness": "runtime_ready",
      "answer_type": "solution_set",
      "template_slot": "two_point_distance_solution_set",
      "base_problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
      "target_task": "solve_unknown_coordinate_from_two_point_distance",
      "presentation_mode": "short_answer",
      "answer_shape": "unordered_set"
    },
    {
      "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "checker_key": "text_short_checker",
      "equivalence_type": "exact_string",
      "generator_readiness": "runtime_ready",
      "answer_type": "text_short",
      "template_slot": "two_point_distance_compute",
      "base_problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "target_task": "compute_distance_between_two_points",
      "presentation_mode": "short_answer",
      "answer_shape": "text_short"
    }
  ],
  "packaging_usable_count": 2,
  "packaging_diagnostics": {
    "candidate_count": 2,
    "included_count": 2,
    "excluded_count": 0,
    "included": [
      {
        "problem_type_id": "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2",
        "generator_key": "vh_數學B1_DistanceBetweenTwoPointsInPlane:short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2:draft_v1",
        "generator_status": "runtime_ready"
      },
      {
        "problem_type_id": "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
        "generator_key": "vh_數學B1_DistanceBetweenTwoPointsInPlane:short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2:draft_v1",
        "generator_status": "runtime_ready"
      }
    ],
    "excluded": [],
    "phase2_summary_exists": true,
    "generator_draft_spec_exists": true,
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase2_generator_summary.json",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_DistanceBetweenTwoPointsInPlane_generator_draft_spec.json",
    "runtime_spec_alignment": {
      "status": "skipped_no_aligned_draft_specs",
      "synced_spec_count": 0,
      "synced_problem_type_ids": [],
      "purged_induced_spec_path": "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_DistanceBetweenTwoPointsInPlane.json",
      "purged_induced_spec_paths": [
        "reports\\gencode_closed_loop\\induced_specs\\vh_數學B1_DistanceBetweenTwoPointsInPlane.json"
      ],
      "runtime_usable_problem_type_ids": [],
      "downgraded_historical_problem_type_ids": [],
      "canonical_filter_applied": false
    }
  },
  "reports": {
    "phase3_package_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase3_package_summary.json",
    "phase3_package_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase3_package_summary.md",
    "phase3_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase3_package_summary.json",
    "phase3_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase3_package_summary.md",
    "final_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase3_package_summary.json",
    "final_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_DistanceBetweenTwoPointsInPlane_phase3_package_summary.md",
    "draft_skill_file": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_DistanceBetweenTwoPointsInPlane.py"
  },
  "next_action": "review_phase3_publish_check",
  "error": "",
  "dry_run": true,
  "timestamp": "2026-07-01T16:09:59.345273+00:00",
  "generated_with_warning": true,
  "warnings": [
    "low_source_examples"
  ],
  "publish_gate_layers": {
    "technical_closed_loop": "FAIL",
    "runtime_quality": "FAIL",
    "web_runtime": "FAIL",
    "source_alignment": "PARTIAL"
  },
  "source_alignment_audit": {
    "status": "PARTIAL",
    "missing_source_aligned_problem_types": [
      "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
    ],
    "underrepresented_runtime_forms": [
      "short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2",
      "short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2"
    ]
  },
  "post_phase3_audit_scripts": [
    {
      "script": "gencode_choice_quality_audit.py",
      "exists": true,
      "py_compile_ok": true
    },
    {
      "script": "gencode_runtime_distribution_audit.py",
      "exists": true,
      "py_compile_ok": true
    },
    {
      "script": "gencode_web_runtime_audit.py",
      "exists": true,
      "py_compile_ok": true
    },
    {
      "script": "gencode_source_alignment_audit.py",
      "exists": true,
      "py_compile_ok": true
    }
  ],
  "summary_message": "Phase 3 packaged draft skill file, but draft runtime smoke did not pass. See publish_check / runtime_smoke_raw. usable_generators=2."
}
```
