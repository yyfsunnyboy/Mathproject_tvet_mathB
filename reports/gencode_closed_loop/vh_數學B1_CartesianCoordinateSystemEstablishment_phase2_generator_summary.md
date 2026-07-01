# Gencode Phase2 Generator Summary: vh_數學B1_CartesianCoordinateSystemEstablishment

## phase2
```json
{
  "ok": true,
  "phase": "phase2",
  "skill_id": "vh_數學B1_CartesianCoordinateSystemEstablishment",
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
  "phase1_alignment_blocked": false,
  "alignment_blockers": [],
  "generator_results": [
    {
      "problem_type_id": "evaluate_function_value",
      "source_example_count": 0,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "answer_equivalence": "algebraic_equivalent",
        "equivalence_type": "algebraic_equivalent",
        "checker": "expression_checker",
        "checker_key": "expression_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "expression_checker",
        "checker_selection_reason": "quadratic_factoring_expression",
        "accepted_formats": [
          "(x-5)(x+3)",
          "(2x-1)(x+5)",
          "2(x-1)(3x+2)"
        ],
        "answer_semantics": "algebraic_expression"
      },
      "answer_type": "expression",
      "answer_shape": "factored_expression",
      "equivalence_type": "algebraic_equivalent",
      "selected_checker": "expression_checker",
      "checker_key": "expression_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_CartesianCoordinateSystemEstablishment:evaluate_function_value:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "runtime_ready_with_diversity_warning",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 30,
        "unique_question_text_count": 14,
        "template_variant_distribution": {
          "default": 30
        },
        "answer_shape_distribution": {
          "(-8,-2)": 1,
          "(9,8)": 1,
          "(-4,12)": 1,
          "(2,12)": 1,
          "(-1,-6)": 2,
          "(8,-2)": 1,
          "(7,2)": 1,
          "(10,7)": 1,
          "(3,0)": 1,
          "(4,-1)": 1,
          "(0,1)": 1,
          "(-2,1)": 1,
          "(-2,5)": 1,
          "(1,15)": 1,
          "(9,6)": 1,
          "(10,9)": 1,
          "(7,-4)": 1,
          "(-9,8)": 1,
          "(0,5)": 1,
          "(-1,8)": 1,
          "(7,-9)": 1,
          "(15,9)": 1,
          "(-5,-5)": 1,
          "(1,-4)": 1,
          "(3,-5)": 1,
          "(12,2)": 1,
          "(0,-8)": 1,
          "(3,6)": 1,
          "(1,-6)": 1
        },
        "variable_coverage_report": {
          "ratio_forms": [
            "AP:PB=m:n",
            "AP=mPB",
            "mAP=nPB"
          ],
          "coordinate_patterns": [
            "++",
            "+-",
            "-+",
            "--",
            "mixed"
          ],
          "answer_type_modes": [
            ""
          ]
        },
        "repetition_warnings": [
          "consecutive_same_template_variant"
        ],
        "diversity_blockers": [],
        "max_consecutive_same_template": 30,
        "generation_errors": [
          "'list' object has no attribute 'get'",
          "'list' object has no attribute 'get'",
          "'list' object has no attribute 'get'",
          "'list' object has no attribute 'get'",
          "'list' object has no attribute 'get'"
        ],
        "sampling_mode": "contract_simulation"
      },
      "unique_signature_count": 30,
      "template_variant_distribution": {
        "default": 30
      },
      "variable_coverage_report": {
        "ratio_forms": [
          "AP:PB=m:n",
          "AP=mPB",
          "mAP=nPB"
        ],
        "coordinate_patterns": [
          "++",
          "+-",
          "-+",
          "--",
          "mixed"
        ],
        "answer_type_modes": [
          ""
        ]
      },
      "repetition_warnings": [
        "consecutive_same_template_variant",
        "low_sample_diversity_tolerance_applied",
        "low_source_examples",
        "no_matched_source_examples"
      ],
      "requires_human_action": false,
      "blockers": [],
      "warnings": [
        "consecutive_same_template_variant",
        "low_sample_diversity_tolerance_applied",
        "low_source_examples",
        "no_matched_source_examples"
      ],
      "usable_for_phase3": true,
      "target_task": "evaluate_function_value",
      "task_family": "function_concept_family",
      "base_problem_type_id": "evaluate_function_value",
      "value_type_prefix": "",
      "template_slot": "factor_quadratic_by_cross_multiplication",
      "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
    },
    {
      "problem_type_id": "interpret_function_notation",
      "source_example_count": 0,
      "answer_contract": {
        "choices_required": false,
        "choice_count": null,
        "correct_choice_count": null,
        "frontend_render_choices": false,
        "answer_type": "expression",
        "answer_shape": "factored_expression",
        "answer_equivalence": "algebraic_equivalent",
        "equivalence_type": "algebraic_equivalent",
        "checker": "expression_checker",
        "checker_key": "expression_checker",
        "presentation_mode": "short_answer",
        "selected_checker": "expression_checker",
        "checker_selection_reason": "quadratic_factoring_expression",
        "accepted_formats": [
          "(x-5)(x+3)",
          "(2x-1)(x+5)",
          "2(x-1)(3x+2)"
        ],
        "answer_semantics": "algebraic_expression"
      },
      "answer_type": "expression",
      "answer_shape": "factored_expression",
      "equivalence_type": "algebraic_equivalent",
      "selected_checker": "expression_checker",
      "checker_key": "expression_checker",
      "checker_capability_status": "ok",
      "checker_contract_blockers": [],
      "checker_contract_warnings": [],
      "generator_key": "vh_數學B1_CartesianCoordinateSystemEstablishment:interpret_function_notation:draft_v1",
      "generator_status": "runtime_ready_with_warning",
      "checker_smoke_status": "passed",
      "dynamic_sampling_status": "runtime_ready_with_diversity_warning",
      "diversity_sampling": {
        "diversity_sampling_status": "runtime_ready_with_diversity_warning",
        "diversity_healthy": true,
        "sample_count": 30,
        "unique_signature_count": 30,
        "unique_question_text_count": 14,
        "template_variant_distribution": {
          "default": 30
        },
        "answer_shape_distribution": {
          "(-8,-2)": 1,
          "(9,8)": 1,
          "(-4,12)": 1,
          "(2,12)": 1,
          "(-1,-6)": 2,
          "(8,-2)": 1,
          "(7,2)": 1,
          "(10,7)": 1,
          "(3,0)": 1,
          "(4,-1)": 1,
          "(0,1)": 1,
          "(-2,1)": 1,
          "(-2,5)": 1,
          "(1,15)": 1,
          "(9,6)": 1,
          "(10,9)": 1,
          "(7,-4)": 1,
          "(-9,8)": 1,
          "(0,5)": 1,
          "(-1,8)": 1,
          "(7,-9)": 1,
          "(15,9)": 1,
          "(-5,-5)": 1,
          "(1,-4)": 1,
          "(3,-5)": 1,
          "(12,2)": 1,
          "(0,-8)": 1,
          "(3,6)": 1,
          "(1,-6)": 1
        },
        "variable_coverage_report": {
          "ratio_forms": [
            "AP:PB=m:n",
            "AP=mPB",
            "mAP=nPB"
          ],
          "coordinate_patterns": [
            "++",
            "+-",
            "-+",
            "--",
            "mixed"
          ],
          "answer_type_modes": [
            ""
          ]
        },
        "repetition_warnings": [
          "consecutive_same_template_variant"
        ],
        "diversity_blockers": [],
        "max_consecutive_same_template": 30,
        "generation_errors": [
          "'list' object has no attribute 'get'",
          "'list' object has no attribute 'get'",
          "'list' object has no attribute 'get'",
          "'list' object has no attribute 'get'",
          "'list' object has no attribute 'get'"
        ],
        "sampling_mode": "contract_simulation"
      },
      "unique_signature_count": 30,
      "template_variant_distribution": {
        "default": 30
      },
      "variable_coverage_report": {
        "ratio_forms": [
          "AP:PB=m:n",
          "AP=mPB",
          "mAP=nPB"
        ],
        "coordinate_patterns": [
          "++",
          "+-",
          "-+",
          "--",
          "mixed"
        ],
        "answer_type_modes": [
          ""
        ]
      },
      "repetition_warnings": [
        "consecutive_same_template_variant",
        "low_sample_diversity_tolerance_applied",
        "low_source_examples",
        "no_matched_source_examples"
      ],
      "requires_human_action": false,
      "blockers": [],
      "warnings": [
        "consecutive_same_template_variant",
        "low_sample_diversity_tolerance_applied",
        "low_source_examples",
        "no_matched_source_examples"
      ],
      "usable_for_phase3": true,
      "target_task": "interpret_function_notation",
      "task_family": "function_concept_family",
      "base_problem_type_id": "interpret_function_notation",
      "value_type_prefix": "",
      "template_slot": "factor_quadratic_by_cross_multiplication",
      "_resolved_template_slot": "factor_quadratic_by_cross_multiplication"
    }
  ],
  "failed_generators": [],
  "accepted_generators": [
    "vh_數學B1_CartesianCoordinateSystemEstablishment:evaluate_function_value:draft_v1",
    "vh_數學B1_CartesianCoordinateSystemEstablishment:interpret_function_notation:draft_v1"
  ],
  "foundation_preflight": {
    "foundation_ready": true,
    "foundation_status": "PASS",
    "missing_checker": [],
    "missing_verifier": [],
    "missing_domain_function": [],
    "missing_generator": [],
    "missing_runtime_binding": [],
    "missing_registry_binding": [],
    "missing_answer_contract_problem_types": [],
    "repair_plan": [],
    "next_action": "phase3_package_draft"
  },
  "foundation_ready": true,
  "phase2_status": "PASS",
  "repair_plan": [],
  "reports": {
    "phase2_generator_summary_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CartesianCoordinateSystemEstablishment_phase2_generator_summary.json",
    "phase2_generator_summary_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CartesianCoordinateSystemEstablishment_phase2_generator_summary.md",
    "phase2_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CartesianCoordinateSystemEstablishment_phase2_generator_summary.json",
    "phase2_md": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_CartesianCoordinateSystemEstablishment_phase2_generator_summary.md",
    "generator_draft_spec_json": "E:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\drafts\\vh_數學B1_CartesianCoordinateSystemEstablishment_generator_draft_spec.json"
  },
  "next_action": "phase3_package_draft",
  "timestamp": "2026-07-01T04:39:49.444420+00:00",
  "dry_run": true
}
```
