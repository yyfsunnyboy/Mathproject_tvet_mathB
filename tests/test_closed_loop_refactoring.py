# -*- coding: utf-8 -*-
import json
import unittest
from unittest.mock import MagicMock, patch
from validators.base_checker import BaseChecker
from validators.semantic_checker import SemanticChecker
from generators.base_generator import BaseGenerator
from gencode_closed_loop.controller import execute_phase_2
from gencode_closed_loop.pipeline import execute_phase_3

class TestGenCodeRefactoring(unittest.TestCase):

    # ─────────────────────────────────────────────────────────────────────────────
    # 1. Tests for BaseChecker & SemanticChecker
    # ─────────────────────────────────────────────────────────────────────────────

    def test_checker_choice_count_mismatch(self):
        checker = SemanticChecker()
        spec = {
            "answer_contract": {
                "answer_type": "single_choice",
                "choice_count": 4
            }
        }
        # Payload has only 3 choices -> mismatch
        payload = {
            "choices": ["A", "B", "C"],
            "answer": "A"
        }
        ok, err = checker.check_semantic(payload, spec)
        self.assertFalse(ok)
        self.assertEqual(err["error_type"], "choice_count_mismatch")
        self.assertEqual(err["expected"], 4)
        self.assertEqual(err["actual"], 3)

    def test_checker_answer_not_in_choices(self):
        checker = SemanticChecker()
        spec = {
            "answer_contract": {
                "answer_type": "single_choice",
                "choice_count": 4
            }
        }
        # Payload has 4 choices but correct answer is 'E' which is not in choices
        payload = {
            "choices": ["A", "B", "C", "D"],
            "answer": "E"
        }
        ok, err = checker.check_semantic(payload, spec)
        self.assertFalse(ok)
        self.assertEqual(err["error_type"], "answer_not_in_choices")

    def test_checker_sympy_parse_error(self):
        checker = SemanticChecker()
        spec = {
            "answer_contract": {
                "answer_type": "expression",
                "checker_key": "expression_checker"
            }
        }
        # Unparseable math expression e.g. mismatched parentheses
        payload = {
            "answer": "2 * x + (3"
        }
        ok, err = checker.check_semantic(payload, spec)
        self.assertFalse(ok)
        self.assertEqual(err["error_type"], "parse_error")

    def test_checker_sympy_parse_success(self):
        checker = SemanticChecker()
        spec = {
            "answer_contract": {
                "answer_type": "expression",
                "checker_key": "expression_checker"
            }
        }
        # Valid math expression
        payload = {
            "answer": "2 * x + 3"
        }
        ok, err = checker.check_semantic(payload, spec)
        self.assertTrue(ok)
        self.assertEqual(err, {})

    # ─────────────────────────────────────────────────────────────────────────────
    # 2. Tests for BaseGenerator (Low-Sample Adaptation)
    # ─────────────────────────────────────────────────────────────────────────────

    def test_generator_low_sample_scaling(self):
        # Only 1 source example -> triggers low sample adaptation
        gen = BaseGenerator(source_examples=[{"id": 1}])
        self.assertTrue(gen.low_source_examples)
        
        # Check parameters adapted by 1.5x
        params = {
            "x_min": -10,
            "x_max": 10,
            "ratio": {
                "m_max": 5
            }
        }
        adapted = gen.adapt_parameters(params)
        self.assertEqual(adapted["x_min"], -15.0)
        self.assertEqual(adapted["x_max"], 15.0)
        self.assertEqual(adapted["ratio"]["m_max"], 7.5)

    def test_generator_normal_sample_no_scaling(self):
        # 3 source examples -> normal, no adaptation
        gen = BaseGenerator(source_examples=[{"id": 1}, {"id": 2}, {"id": 3}])
        self.assertFalse(gen.low_source_examples)
        
        params = {"x_max": 10}
        adapted = gen.adapt_parameters(params)
        self.assertEqual(adapted["x_max"], 10)

    def test_generator_diversity_warning_exemption(self):
        gen = BaseGenerator(source_examples=[{"id": 1}])
        metrics = {
            "diversity_sampling_status": "generator_diversity_blocked",
            "diversity_blockers": ["generator_diversity_blocked", "some_other_blocker"]
        }
        adapted_metrics = gen.exempt_diversity_warning(metrics)
        self.assertNotIn("generator_diversity_blocked", adapted_metrics["diversity_blockers"])
        self.assertEqual(adapted_metrics["diversity_sampling_status"], "passed")

    # ─────────────────────────────────────────────────────────────────────────────
    # 3. Tests for Controller (Rollback & Retry State Machine)
    # ─────────────────────────────────────────────────────────────────────────────

    @patch("gencode_closed_loop.controller.run_gencode_phase2_raw")
    def test_controller_success_first_attempt(self, mock_run):
        mock_run.return_value = {
            "can_continue": True,
            "generator_results": [
                {"problem_type_id": "test_pt", "usable_for_phase3": True}
            ]
        }
        
        res = execute_phase_2("vh_math_test")
        self.assertTrue(res["can_continue"])
        self.assertEqual(mock_run.call_count, 1)

    @patch("gencode_closed_loop.controller.run_gencode_phase2_raw")
    @patch("gencode_closed_loop.controller._resolve_gencode_ai_client")
    def test_controller_rollback_retry_limit_exceeded(self, mock_ai, mock_run):
        # Mock run always returns failure
        mock_run.return_value = {
            "can_continue": False,
            "generator_results": [
                {"problem_type_id": "test_pt", "usable_for_phase3": False}
            ]
        }
        
        # Verify execute_phase_2 raises system interrupt after 3 attempts
        with self.assertRaises(RuntimeError) as excinfo:
            execute_phase_2("vh_math_test")
        
        self.assertIn("SYSTEM_INTERRUPT", str(excinfo.exception))
        self.assertEqual(mock_run.call_count, 3)

    # ─────────────────────────────────────────────────────────────────────────────
    # 4. Tests for Pipeline Scheduler (Try-Catch & Self-Healing)
    # ─────────────────────────────────────────────────────────────────────────────

    @patch("gencode_closed_loop.pipeline.run_gencode_phase3_package_raw")
    def test_pipeline_scheduler_success(self, mock_package):
        mock_package.return_value = {
            "ok": True,
            "phase": "phase3",
            "can_continue": True
        }
        
        res = execute_phase_3("vh_math_test")
        self.assertTrue(res["ok"])
        self.assertEqual(mock_package.call_count, 1)

    @patch("gencode_closed_loop.pipeline.run_gencode_phase3_package_raw")
    @patch("gencode_closed_loop.pipeline._resolve_gencode_ai_client")
    @patch("gencode_closed_loop.pipeline.phase_summary_path")
    def test_pipeline_scheduler_crash_and_self_heal(self, mock_path, mock_ai, mock_package):
        # Setup mock file paths
        mock_spec_path = MagicMock()
        mock_spec_path.exists.return_value = True
        mock_spec_path.read_text.return_value = '{"spec": "draft"}'
        mock_path.return_value = mock_spec_path
        
        # Packaging fails on first call (raises exception), succeeds on retry (second call)
        mock_package.side_effect = [
            RuntimeError("Mismatched local variables in templates"),
            {"ok": True, "phase": "phase3", "can_continue": True}
        ]
        
        # Mock AI response
        mock_client = MagicMock()
        mock_ai.return_value = (mock_client, {})
        
        res = execute_phase_3("vh_math_test")
        self.assertTrue(res["ok"])
        self.assertEqual(mock_package.call_count, 2)

if __name__ == "__main__":
    unittest.main()
