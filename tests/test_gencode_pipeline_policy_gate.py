# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest
from core.gencode.pipeline_policy import evaluate_pipeline_gates


class TestPipelinePolicyGate(unittest.TestCase):

    def test_single_item_defects_demoted(self):
        """
        Verify that single-item defects in risk flags do not block classifier or generator gates,
        and are successfully collected into warnings.
        """
        candidates = [
            {
                "problem_type_id": "linear_evaluate",
                "answer_shape": "integer",
                "answer_contract_proposal": {"type": "integer"},
                "checker_key_proposal": "integer_checker",
                "equivalence_type_proposal": "numeric_exact",
                "matched_example_count": 3,
                "risk_flags": ["small_number_source_quality_reject", "single_broken_latex"]
            }
        ]

        gates = evaluate_pipeline_gates(
            candidates,
            source_examples_count=3,
            checker_smoke_passed=True,
            dynamic_sampling_passed=True,
            contract_tests_passed=True,
        )

        self.assertTrue(gates["classifier_gate"]["allowed"])
        self.assertTrue(gates["generator_draft_gate"]["allowed"])
        self.assertTrue(gates["runtime_ready_gate"]["allowed"])
        self.assertFalse(gates["exception_review_gate"]["required"])
        self.assertIn("small_number_source_quality_reject", gates["runtime_ready_gate"]["warnings"])
        self.assertIn("single_broken_latex", gates["runtime_ready_gate"]["warnings"])

    def test_mixed_candidates_sufficiency(self):
        """
        Verify that as long as source_examples_count >= 1 and at least one valid, non-contradictory
        spec is inducted, the classifier and generator gates are allowed.
        """
        candidates = [
            {
                "problem_type_id": "linear_evaluate",
                "answer_shape": "integer",
                "answer_contract_proposal": {"type": "integer"},
                "checker_key_proposal": "integer_checker",
                "equivalence_type_proposal": "numeric_exact",
                "matched_example_count": 3,
            },
            {
                "problem_type_id": "linear_plot",
                "answer_shape": "unknown_answer_shape",
                "risk_flags": ["contradictory_concept"]
            }
        ]

        gates = evaluate_pipeline_gates(
            candidates,
            source_examples_count=3,
            checker_smoke_passed=True,
            dynamic_sampling_passed=True,
            contract_tests_passed=True,
        )
        self.assertTrue(gates["classifier_gate"]["allowed"])
        self.assertTrue(gates["generator_draft_gate"]["allowed"])
        self.assertFalse(gates["exception_review_gate"]["required"])

    def test_semantic_alignment_warning_demotion(self):
        """
        Verify that non-fatal structural alarms (like low semantic alignment score)
        are moved out of runtime blockers and appended exclusively to warnings.
        """
        candidates = [
            {
                "problem_type_id": "linear_evaluate",
                "answer_shape": "integer",
                "answer_contract_proposal": {"type": "integer"},
                "checker_key_proposal": "integer_checker",
                "equivalence_type_proposal": "numeric_exact",
                "matched_example_count": 3,
            }
        ]

        gates = evaluate_pipeline_gates(
            candidates,
            source_examples_count=3,
            checker_smoke_passed=True,
            dynamic_sampling_passed=True,
            contract_tests_passed=True,
            semantic_alignment_blocked=True
        )
        self.assertTrue(gates["runtime_ready_gate"]["allowed"])
        self.assertIn("semantic_alignment_blocked", gates["runtime_ready_gate"]["warnings"])
        self.assertNotIn("semantic_alignment_blocked", gates["runtime_ready_gate"]["blockers"])

    def test_exception_review_trigger_conditions(self):
        """
        Verify that exception review is only required when source_examples_count < 1 or
        a fatal cryptographic/execution safety risk is explicitly flagged.
        """
        candidates = [
            {
                "problem_type_id": "linear_evaluate",
                "answer_shape": "integer",
                "answer_contract_proposal": {"type": "integer"},
                "checker_key_proposal": "integer_checker",
                "equivalence_type_proposal": "numeric_exact",
                "matched_example_count": 3,
            }
        ]

        # Case A: Low examples count
        gates_no_source = evaluate_pipeline_gates(candidates, source_examples_count=0)
        self.assertTrue(gates_no_source["exception_review_gate"]["required"])

        # Case B: Fatal safety risk
        candidates_fatal = [
            {
                "problem_type_id": "linear_evaluate",
                "answer_shape": "integer",
                "answer_contract_proposal": {"type": "integer"},
                "checker_key_proposal": "integer_checker",
                "equivalence_type_proposal": "numeric_exact",
                "matched_example_count": 3,
                "risk_flags": ["fatal_execution_safety_risk"]
            }
        ]
        gates_fatal = evaluate_pipeline_gates(candidates_fatal, source_examples_count=3)
        self.assertTrue(gates_fatal["exception_review_gate"]["required"])
        self.assertIn("fatal_execution_safety_risk", gates_fatal["exception_review_gate"]["reasons"])


if __name__ == "__main__":
    unittest.main()
