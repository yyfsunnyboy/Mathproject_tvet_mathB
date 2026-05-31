# -*- coding: utf-8 -*-
import unittest
from core.gencode.problem_type_grouping_contract import validate_problem_type_grouping_contract

class TestGencodeProblemTypeGroupingContract(unittest.TestCase):
    
    def test_numeric_evaluate_function_value_formation(self):
        """
        Verify that a group with numeric and evaluate_function_value forms numeric_evaluate_function_value.
        """
        mock_report = {
            "skill_id": "test_skill_generic",
            "candidate_problem_types": [
                {
                    "problem_type_id": "mixed_type_pt",
                    "matched_example_ids": [1, 2]
                }
            ],
            "per_example_classification": [
                {
                    "example_id": 1,
                    "target_task": "evaluate_function_value",
                    "answer_type": "numeric",
                    "presentation_mode": "short_answer"
                },
                {
                    "example_id": 2,
                    "target_task": "evaluate_function_value",
                    "answer_type": "numeric",
                    "presentation_mode": "short_answer"
                }
            ]
        }
        
        res = validate_problem_type_grouping_contract(mock_report)
        self.assertEqual(res["problem_type_grouping_contract_status"], "PASS")
        norm_fields = res["normalized_fields"]
        candidates = norm_fields["candidate_problem_types"]
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["problem_type_id"], "numeric_evaluate_function_value_short_answer")

    def test_short_answer_interpret_function_notation_formation(self):
        """
        Verify that short_answer and interpret_function_notation forms short_answer_interpret_function_notation.
        """
        mock_report = {
            "skill_id": "test_skill_generic",
            "candidate_problem_types": [
                {
                    "problem_type_id": "mixed_type_pt",
                    "matched_example_ids": [3, 4]
                }
            ],
            "per_example_classification": [
                {
                    "example_id": 3,
                    "target_task": "interpret_function_notation",
                    "answer_type": "short_answer",
                    "presentation_mode": "short_answer"
                },
                {
                    "example_id": 4,
                    "target_task": "interpret_function_notation",
                    "answer_type": "short_answer",
                    "presentation_mode": "short_answer"
                }
            ]
        }
        
        res = validate_problem_type_grouping_contract(mock_report)
        self.assertEqual(res["problem_type_grouping_contract_status"], "PASS")
        norm_fields = res["normalized_fields"]
        candidates = norm_fields["candidate_problem_types"]
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["problem_type_id"], "short_answer_interpret_function_notation")

    def test_numeric_interpret_function_notation_no_mixture(self):
        """
        Verify that numeric and interpret_function_notation is NOT merged with evaluate_function_value.
        Mixed target tasks must be split into separate candidates.
        """
        mock_report = {
            "skill_id": "test_skill_generic",
            "candidate_problem_types": [
                {
                    "problem_type_id": "mixed_pt",
                    "matched_example_ids": [5, 6],
                    "answer_contract_proposal": {}
                }
            ],
            "per_example_classification": [
                {
                    "example_id": 5,
                    "target_task": "interpret_function_notation",
                    "answer_type": "numeric",
                    "presentation_mode": "short_answer"
                },
                {
                    "example_id": 6,
                    "target_task": "evaluate_function_value",
                    "answer_type": "numeric",
                    "presentation_mode": "short_answer"
                }
            ]
        }
        
        res = validate_problem_type_grouping_contract(mock_report)
        self.assertEqual(res["problem_type_grouping_contract_status"], "FAIL")
        self.assertIn("mixed_group_split_required:mixed_pt", res["problem_type_grouping_contract_warnings"])
        
        candidates = res["normalized_fields"]["candidate_problem_types"]
        self.assertEqual(len(candidates), 2)
        pt_ids = {c["problem_type_id"] for c in candidates}
        self.assertIn("numeric_interpret_function_notation_short_answer", pt_ids)
        self.assertIn("numeric_evaluate_function_value_short_answer", pt_ids)

    def test_different_final_target_task_not_merged(self):
        """
        Verify that different final target tasks in a single candidate proposal list
        are successfully split into separate candidates and grouping contract fails.
        """
        mock_report = {
            "skill_id": "test_skill_generic",
            "candidate_problem_types": [
                {
                    "problem_type_id": "conflicting_pt",
                    "matched_example_ids": [7, 8],
                    "answer_contract_proposal": {}
                }
            ],
            "per_example_classification": [
                {
                    "example_id": 7,
                    "target_task": "interpret_function_notation",
                    "answer_type": "numeric",
                    "presentation_mode": "short_answer"
                },
                {
                    "example_id": 8,
                    "target_task": "judge_domain_range_basic",
                    "answer_type": "numeric",
                    "presentation_mode": "short_answer"
                }
            ]
        }
        
        res = validate_problem_type_grouping_contract(mock_report)
        self.assertEqual(res["problem_type_grouping_contract_status"], "FAIL")
        
        candidates = res["normalized_fields"]["candidate_problem_types"]
        self.assertEqual(len(candidates), 2)
        pt_ids = {c["problem_type_id"] for c in candidates}
        self.assertIn("numeric_interpret_function_notation_short_answer", pt_ids)
        self.assertIn("numeric_judge_domain_range_basic_short_answer", pt_ids)

    def test_no_specific_skill_id_dependency(self):
        """
        Verify that the contract validation is fully generic and works for other skills.
        """
        mock_report = {
            "skill_id": "other_unrelated_skill_id_123",
            "candidate_problem_types": [
                {
                    "problem_type_id": "some_pt",
                    "matched_example_ids": [9]
                }
            ],
            "per_example_classification": [
                {
                    "example_id": 9,
                    "target_task": "some_arbitrary_task",
                    "answer_type": "choice",
                    "presentation_mode": "single_choice"
                }
            ]
        }
        
        res = validate_problem_type_grouping_contract(mock_report)
        self.assertEqual(res["problem_type_grouping_contract_status"], "PASS")
        self.assertEqual(res["normalized_fields"]["candidate_problem_types"][0]["problem_type_id"], "choice_some_arbitrary_task")

if __name__ == '__main__':
    unittest.main()
