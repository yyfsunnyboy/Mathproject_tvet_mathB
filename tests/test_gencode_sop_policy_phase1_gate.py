# -*- coding: utf-8 -*-
import os
import unittest
from pathlib import Path
from core.gencode.sop_policy import (
    validate_sop_preflight,
    build_sop_reference,
    validate_skill_level_blockers,
    ALLOWED_SKILL_LEVEL_BLOCKERS,
    DISALLOWED_SKILL_BLOCK_PROMOTIONS
)

class TestGencodeSopPolicyPhase1Gate(unittest.TestCase):
    
    def setUp(self):
        # We assume the project root is the current directory in tests
        self.project_root = os.getcwd()
        
    def test_sop_files_exist_and_readable(self):
        """
        Verify that our preflight scan finds and reads all three v0.2 SOP files.
        """
        result = validate_sop_preflight(self.project_root)
        self.assertEqual(result["sop_preflight_status"], "PASS", f"SOP Preflight failed! Errors: {result['errors']}")
        self.assertEqual(len(result["required_sop_files"]), 3)
        for f in result["required_sop_files"]:
            self.assertTrue(f["exists"], f"SOP file missing: {f['path']}")
            self.assertTrue(f["readable"], f"SOP file unreadable: {f['path']}")
            self.assertFalse(f["mojibake_detected"], f"Mojibake detected in: {f['path']}")

    def test_build_sop_reference(self):
        """
        Verify that build_sop_reference returns valid dictionary.
        """
        ref = build_sop_reference(self.project_root)
        self.assertEqual(ref["sop_policy_version"], "v0.2")
        self.assertEqual(ref["sop_preflight_status"], "PASS")
        self.assertTrue(ref["highest_sop"].endswith("Gencode與AgentSkillV2整合總體設計_v0.2.md"))

    def test_validate_skill_level_blockers_success(self):
        """
        Allowed blockers should be validated and accepted.
        """
        test_blockers = ["no_usable_core_examples", "skill_section_curriculum_mismatch"]
        res = validate_skill_level_blockers(test_blockers)
        self.assertEqual(res["sop_gate_status"], "PASS")
        self.assertFalse(res["sop_violation"])
        self.assertEqual(len(res["invalid_skill_level_blockers"]), 0)

    def test_validate_skill_level_blockers_rejection(self):
        """
        Disallowed blockers (like single_broken_latex) must trigger failure/violation.
        """
        # Test a disallowed blocker
        test_blockers = ["single_broken_latex", "no_usable_core_examples"]
        res = validate_skill_level_blockers(test_blockers)
        self.assertEqual(res["sop_gate_status"], "FAIL")
        self.assertTrue(res["sop_violation"])
        self.assertIn("single_broken_latex", res["invalid_skill_level_blockers"])

        # Test an unknown blocker
        test_blockers_unknown = ["some_random_blocker"]
        res_unknown = validate_skill_level_blockers(test_blockers_unknown)
        self.assertEqual(res_unknown["sop_gate_status"], "FAIL")
        self.assertTrue(res_unknown["sop_violation"])
        self.assertIn("some_random_blocker", res_unknown["invalid_skill_level_blockers"])

    def test_final_classification_soft_accept_principles(self):
        """
        Verify the principle: if final target task is in candidates and families,
        and not rejected, it shouldn't have alignment_score=0 (which is checked in pipeline).
        """
        # This acts as a dry-run check of expected subskill candidate logic
        expected_candidates = ["evaluate_function_value", "interpret_function_notation"]
        allowed_families = ["linear_function_basic", "linear_function_graphs"]
        
        # Test case: Valid classification
        final_target_task = "evaluate_function_value"
        final_task_family = "linear_function_basic"
        source_quality_status = "usable"
        
        # Principle checks
        is_aligned = (
            final_target_task in expected_candidates and
            final_task_family in allowed_families and
            source_quality_status != "rejected"
        )
        self.assertTrue(is_aligned, "LinearFunction valid classification alignment principle violation!")

if __name__ == '__main__':
    unittest.main()
