# -*- coding: utf-8 -*-
import unittest
from core.gencode.phase1_report_contract import validate_phase1_report_contract

class TestGencodePhase1ReportContract(unittest.TestCase):
    
    def test_source_quality_reject_examples_normalization(self):
        """
        Verify that rejected source example IDs are normalized into source_quality_reject_examples list.
        """
        mock_report = {
            "skill_id": "test_skill_abc",
            "rejected_source_examples": [101, 102],
            "source_quality_reject_examples": [],
            "per_example_classification": [
                {
                    "example_id": 101,
                    "source_quality_status": "rejected",
                    "included_in_core_induction": False
                },
                {
                    "example_id": 102,
                    "source_quality_reject": True,
                    "included_in_core_induction": False
                },
                {
                    "example_id": 103,
                    "source_quality_status": "usable",
                    "included_in_core_induction": True
                }
            ]
        }
        
        res = validate_phase1_report_contract(mock_report)
        self.assertIn("PASS_WITH_WARNINGS", res["report_contract_status"])
        self.assertIn("source_quality_reject_examples_normalized:101", res["report_contract_warnings"])
        self.assertIn("source_quality_reject_examples_normalized:102", res["report_contract_warnings"])
        
        norm_fields = res["normalized_fields"]
        self.assertEqual(norm_fields["source_quality_reject_examples"], [101, 102])

    def test_aggregate_alignment_score_normalization(self):
        """
        Verify that aggregate alignment_score is recalculated correctly
        and corrected when aggregate score is 0.0 but per-example scores are high.
        """
        mock_report = {
            "skill_id": "test_skill_xyz",
            "expected_subskill_candidates": ["task_a"],
            "expected_skill_families": ["family_a"],
            "alignment_score": 0.0,
            "per_example_classification": [
                {
                    "example_id": 201,
                    "final_target_task": "task_a",
                    "final_task_family": "family_a",
                    "source_quality_status": "usable",
                    "included_in_core_induction": True,
                    "alignment_score": 0.0  # Should be normalized to 0.8
                },
                {
                    "example_id": 202,
                    "final_target_task": "task_a",
                    "final_task_family": "family_a",
                    "source_quality_status": "usable",
                    "included_in_core_induction": True,
                    "alignment_score": 0.8
                }
            ]
        }
        
        res = validate_phase1_report_contract(mock_report)
        self.assertEqual(res["report_contract_status"], "PASS_WITH_WARNINGS")
        self.assertIn("aggregate_alignment_score_normalized", res["report_contract_warnings"])
        self.assertIn("per_example_alignment_score_corrected:201", res["report_contract_warnings"])
        
        norm_fields = res["normalized_fields"]
        self.assertEqual(norm_fields["alignment_score"], 0.8)
        self.assertEqual(norm_fields["per_example_classification"][0]["alignment_score"], 0.8)

    def test_disallowed_blocker_promotion(self):
        """
        Verify that disallowed blockers (like majority_needs_review) are demoted to warnings.
        """
        mock_report = {
            "skill_id": "test_skill_gate",
            "alignment_blockers": ["majority_needs_review"],
            "exception_review_gate": {
                "required": True,
                "reasons": ["majority_needs_review"]
            },
            "sop_gate_status": "PASS",
            "sop_gate_violation": False
        }
        
        res = validate_phase1_report_contract(mock_report)
        self.assertEqual(res["report_contract_status"], "FAIL")  # Due to violation presence
        self.assertTrue(res["normalized_fields"]["sop_gate_violation"])
        self.assertEqual(res["normalized_fields"]["sop_gate_status"], "FAIL")
        self.assertEqual(res["normalized_fields"]["alignment_blockers"], [])
        self.assertEqual(res["normalized_fields"]["exception_review_gate"]["reasons"], [])

    def test_candidate_problem_type_consistency(self):
        """
        Verify that if candidate specs exist, count is not 0, and final status is not blocked if blockers is empty.
        """
        mock_report = {
            "skill_id": "test_skill_cons",
            "candidate_problem_types": [{"problem_type_id": "pt_1"}, {"problem_type_id": "pt_2"}],
            "candidate_problem_type_count": 0,
            "phase_status": "phase1_blocked_semantic_alignment"
        }
        
        res = validate_phase1_report_contract(mock_report)
        self.assertEqual(res["normalized_fields"]["candidate_problem_type_count"], 2)
        self.assertEqual(res["normalized_fields"]["phase_status"], "phase1_completed")
        self.assertTrue(res["normalized_fields"]["ok"])

if __name__ == '__main__':
    unittest.main()
