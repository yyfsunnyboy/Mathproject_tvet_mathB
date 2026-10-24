from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_PolynomialInequalities'
GENERATOR_KEYS = ['src_12631', 'src_12632', 'src_12633', 'src_12634', 'src_12635', 'src_12636', 'src_12637', 'src_12638', 'src_12639', 'src_12640', 'src_12641', 'src_12642', 'src_12643', 'src_12644', 'src_12645', 'src_12646', 'src_12647', 'src_12648', 'src_12649', 'src_12650', 'src_12651', 'src_12652', 'src_12653', 'src_12654', 'src_12655', 'src_12656', 'src_12657', 'src_12658', 'src_12659', 'src_12660', 'src_12661', 'src_12662', 'src_12663', 'src_12664', 'src_12665', 'src_12666']
GENERATOR_SPECS = [{'textbook_example_id': 12631, 'component_id': 'src_12631', 'generator_key': 'src_12631', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12631, 'source_order': 12631, 'sampling_weight': 10.0}, {'textbook_example_id': 12632, 'component_id': 'src_12632', 'generator_key': 'src_12632', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12632, 'source_order': 12632, 'sampling_weight': 10.0}, {'textbook_example_id': 12633, 'component_id': 'src_12633', 'generator_key': 'src_12633', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12633, 'source_order': 12633, 'sampling_weight': 10.0}, {'textbook_example_id': 12634, 'component_id': 'src_12634', 'generator_key': 'src_12634', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12634, 'source_order': 12634, 'sampling_weight': 10.0}, {'textbook_example_id': 12635, 'component_id': 'src_12635', 'generator_key': 'src_12635', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_applications', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'polynomial_applications', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12635, 'source_order': 12635, 'sampling_weight': 10.0}, {'textbook_example_id': 12636, 'component_id': 'src_12636', 'generator_key': 'src_12636', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12636, 'source_order': 12636, 'sampling_weight': 10.0}, {'textbook_example_id': 12637, 'component_id': 'src_12637', 'generator_key': 'src_12637', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12637, 'source_order': 12637, 'sampling_weight': 10.0}, {'textbook_example_id': 12638, 'component_id': 'src_12638', 'generator_key': 'src_12638', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12638, 'source_order': 12638, 'sampling_weight': 10.0}, {'textbook_example_id': 12639, 'component_id': 'src_12639', 'generator_key': 'src_12639', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_inequality_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_inequality_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12639, 'source_order': 12639, 'sampling_weight': 10.0}, {'textbook_example_id': 12640, 'component_id': 'src_12640', 'generator_key': 'src_12640', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_applications', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_applications', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12640, 'source_order': 12640, 'sampling_weight': 10.0}, {'textbook_example_id': 12641, 'component_id': 'src_12641', 'generator_key': 'src_12641', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12641, 'source_order': 12641, 'sampling_weight': 10.0}, {'textbook_example_id': 12642, 'component_id': 'src_12642', 'generator_key': 'src_12642', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12642, 'source_order': 12642, 'sampling_weight': 10.0}, {'textbook_example_id': 12643, 'component_id': 'src_12643', 'generator_key': 'src_12643', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12643, 'source_order': 12643, 'sampling_weight': 10.0}, {'textbook_example_id': 12644, 'component_id': 'src_12644', 'generator_key': 'src_12644', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12644, 'source_order': 12644, 'sampling_weight': 10.0}, {'textbook_example_id': 12645, 'component_id': 'src_12645', 'generator_key': 'src_12645', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_applications', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'polynomial_applications', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12645, 'source_order': 12645, 'sampling_weight': 10.0}, {'textbook_example_id': 12646, 'component_id': 'src_12646', 'generator_key': 'src_12646', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12646, 'source_order': 12646, 'sampling_weight': 10.0}, {'textbook_example_id': 12647, 'component_id': 'src_12647', 'generator_key': 'src_12647', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12647, 'source_order': 12647, 'sampling_weight': 10.0}, {'textbook_example_id': 12648, 'component_id': 'src_12648', 'generator_key': 'src_12648', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12648, 'source_order': 12648, 'sampling_weight': 10.0}, {'textbook_example_id': 12649, 'component_id': 'src_12649', 'generator_key': 'src_12649', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'polynomial_inequality_parameters', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'polynomial_inequality_parameters', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12649, 'source_order': 12649, 'sampling_weight': 10.0}, {'textbook_example_id': 12650, 'component_id': 'src_12650', 'generator_key': 'src_12650', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'polynomial_applications', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_applications', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12650, 'source_order': 12650, 'sampling_weight': 10.0}, {'textbook_example_id': 12651, 'component_id': 'src_12651', 'generator_key': 'src_12651', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12651, 'source_order': 12651, 'sampling_weight': 10.0}, {'textbook_example_id': 12652, 'component_id': 'src_12652', 'generator_key': 'src_12652', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12652, 'source_order': 12652, 'sampling_weight': 10.0}, {'textbook_example_id': 12653, 'component_id': 'src_12653', 'generator_key': 'src_12653', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12653, 'source_order': 12653, 'sampling_weight': 10.0}, {'textbook_example_id': 12654, 'component_id': 'src_12654', 'generator_key': 'src_12654', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12654, 'source_order': 12654, 'sampling_weight': 10.0}, {'textbook_example_id': 12655, 'component_id': 'src_12655', 'generator_key': 'src_12655', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'polynomial_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'polynomial_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12655, 'source_order': 12655, 'sampling_weight': 10.0}, {'textbook_example_id': 12656, 'component_id': 'src_12656', 'generator_key': 'src_12656', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12656, 'source_order': 12656, 'sampling_weight': 10.0}, {'textbook_example_id': 12657, 'component_id': 'src_12657', 'generator_key': 'src_12657', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12657, 'source_order': 12657, 'sampling_weight': 10.0}, {'textbook_example_id': 12658, 'component_id': 'src_12658', 'generator_key': 'src_12658', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_inequality_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_inequality_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12658, 'source_order': 12658, 'sampling_weight': 10.0}, {'textbook_example_id': 12659, 'component_id': 'src_12659', 'generator_key': 'src_12659', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_inequality_parameters', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'polynomial_inequality_parameters', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12659, 'source_order': 12659, 'sampling_weight': 10.0}, {'textbook_example_id': 12660, 'component_id': 'src_12660', 'generator_key': 'src_12660', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_polynomial_inequality', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'solve_polynomial_inequality', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12660, 'source_order': 12660, 'sampling_weight': 10.0}, {'textbook_example_id': 12661, 'component_id': 'src_12661', 'generator_key': 'src_12661', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_statements', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'polynomial_statements', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12661, 'source_order': 12661, 'sampling_weight': 10.0}, {'textbook_example_id': 12662, 'component_id': 'src_12662', 'generator_key': 'src_12662', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_inequality_parameters', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_inequality_parameters', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12662, 'source_order': 12662, 'sampling_weight': 10.0}, {'textbook_example_id': 12663, 'component_id': 'src_12663', 'generator_key': 'src_12663', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_applications', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'polynomial_applications', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12663, 'source_order': 12663, 'sampling_weight': 10.0}, {'textbook_example_id': 12664, 'component_id': 'src_12664', 'generator_key': 'src_12664', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_applications', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'polynomial_applications', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12664, 'source_order': 12664, 'sampling_weight': 10.0}, {'textbook_example_id': 12665, 'component_id': 'src_12665', 'generator_key': 'src_12665', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'polynomial_applications', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'polynomial_applications', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12665, 'source_order': 12665, 'sampling_weight': 10.0}, {'textbook_example_id': 12666, 'component_id': 'src_12666', 'generator_key': 'src_12666', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'polynomial_applications', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'polynomial_applications', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12666, 'source_order': 12666, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12631': 'components/src_12631/generate.py', 'src_12632': 'components/src_12632/generate.py', 'src_12633': 'components/src_12633/generate.py', 'src_12634': 'components/src_12634/generate.py', 'src_12635': 'components/src_12635/generate.py', 'src_12636': 'components/src_12636/generate.py', 'src_12637': 'components/src_12637/generate.py', 'src_12638': 'components/src_12638/generate.py', 'src_12639': 'components/src_12639/generate.py', 'src_12640': 'components/src_12640/generate.py', 'src_12641': 'components/src_12641/generate.py', 'src_12642': 'components/src_12642/generate.py', 'src_12643': 'components/src_12643/generate.py', 'src_12644': 'components/src_12644/generate.py', 'src_12645': 'components/src_12645/generate.py', 'src_12646': 'components/src_12646/generate.py', 'src_12647': 'components/src_12647/generate.py', 'src_12648': 'components/src_12648/generate.py', 'src_12649': 'components/src_12649/generate.py', 'src_12650': 'components/src_12650/generate.py', 'src_12651': 'components/src_12651/generate.py', 'src_12652': 'components/src_12652/generate.py', 'src_12653': 'components/src_12653/generate.py', 'src_12654': 'components/src_12654/generate.py', 'src_12655': 'components/src_12655/generate.py', 'src_12656': 'components/src_12656/generate.py', 'src_12657': 'components/src_12657/generate.py', 'src_12658': 'components/src_12658/generate.py', 'src_12659': 'components/src_12659/generate.py', 'src_12660': 'components/src_12660/generate.py', 'src_12661': 'components/src_12661/generate.py', 'src_12662': 'components/src_12662/generate.py', 'src_12663': 'components/src_12663/generate.py', 'src_12664': 'components/src_12664/generate.py', 'src_12665': 'components/src_12665/generate.py', 'src_12666': 'components/src_12666/generate.py'}
_V3_ROOT = Path(__file__).resolve().parent
_RR_CURSOR = 0
_SHUFFLED_CYCLE = None


def _component_sampling_weight(component_id: str) -> float:
    for row in GENERATOR_SPECS:
        if isinstance(row, dict) and str(row.get("component_id") or "") == component_id:
            return float(row.get("sampling_weight", 1) or 1)
    return 1.0


def _ordered_generator_keys() -> list[str]:
    specs_by_id = {
        str(row.get("component_id") or ""): row
        for row in GENERATOR_SPECS
        if isinstance(row, dict) and str(row.get("component_id") or "")
    }
    return sorted(
        GENERATOR_KEYS,
        key=lambda key: (
            int((specs_by_id.get(key) or {}).get("display_order", 0)),
            int((specs_by_id.get(key) or {}).get("textbook_example_id", 0)),
            key,
        ),
    )


def _load_component_module(component_id: str, module_filename: str) -> Any:
    path = _V3_ROOT / "components" / component_id / module_filename
    module_name = f"v3_{SKILL_ID}_{component_id}_{module_filename.replace('.py', '')}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"component_module_not_found:{component_id}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pick_component_id(
    seed: int | None = None,
    component_id: str | None = None,
) -> str:
    if component_id and component_id in _COMPONENT_DISPATCH:
        return component_id
    ordered_keys = _ordered_generator_keys()
    if not ordered_keys:
        raise RuntimeError("generator_keys_empty")
    
    import math
    from functools import reduce
    
    raw_weights = []
    for key in ordered_keys:
        w = int(_component_sampling_weight(key) or 1)
        raw_weights.append(max(1, w))
        
    g = reduce(math.gcd, raw_weights) if raw_weights else 1
    normalized_weights = [w // g for w in raw_weights]
    
    cycle = []
    for key, w in zip(ordered_keys, normalized_weights):
        cycle.extend([key] * w)

    if seed is None:
        global _RR_CURSOR, _SHUFFLED_CYCLE
        if _SHUFFLED_CYCLE is None or _RR_CURSOR >= len(_SHUFFLED_CYCLE):
            import random
            _SHUFFLED_CYCLE = list(cycle)
            random.shuffle(_SHUFFLED_CYCLE)
            _RR_CURSOR = 0
        picked = _SHUFFLED_CYCLE[_RR_CURSOR]
        _RR_CURSOR += 1
        return picked
    else:
        import random
        cycle_len = len(cycle)
        cycle_seed = int(seed) // cycle_len
        shuffled = list(cycle)
        random.Random(cycle_seed).shuffle(shuffled)
        return shuffled[int(seed) % cycle_len]



def _spec_for_component(component_id: str) -> dict[str, Any]:
    for row in GENERATOR_SPECS:
        if isinstance(row, dict) and str(row.get("component_id") or "") == component_id:
            return dict(row)
    return {}


def _minimal_answer_contract(payload: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    embedded = payload.get("answer_contract")
    if isinstance(embedded, dict) and embedded.get("answer_type"):
        return dict(embedded)
    presentation_mode = str(
        payload.get("presentation_mode")
        or spec.get("presentation_mode")
        or (payload.get("metadata") or {}).get("presentation_mode")
        or "short_answer"
    ).strip()
    answer_type = str(
        payload.get("answer_type")
        or spec.get("answer_type")
        or (payload.get("metadata") or {}).get("answer_type")
        or ("single_choice" if presentation_mode == "single_choice" else "expression")
    ).strip()
    semantic_answer = str(
        payload.get("semantic_answer")
        or (payload.get("metadata") or {}).get("semantic_answer")
        or payload.get("display_answer")
        or payload.get("correct_answer")
        or ""
    ).strip()
    if presentation_mode == "single_choice":
        return {
            "presentation_mode": "single_choice",
            "answer_type": "single_choice",
            "checker": "choice_label_checker",
            "checker_key": "choice_label_checker",
            "answer_equivalence": "choice_label",
            "equivalence": "choice_label",
            "semantic_answer": semantic_answer,
        }
    return {
        "presentation_mode": "short_answer",
        "answer_type": answer_type,
        "checker": "linear_equation_equivalent_checker",
        "checker_key": "linear_equation_equivalent_checker",
        "answer_equivalence": "linear_equation_equivalent",
        "equivalence": "linear_equation_equivalent",
        "semantic_answer": semantic_answer,
    }


def _merge_generator_spec(payload: dict[str, Any], component_id: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return payload
    spec = _spec_for_component(component_id)
    out = dict(payload)
    merge_keys = (
        "textbook_example_id",
        "component_id",
        "generator_key",
        "presentation_mode",
        "problem_type_id",
        "source_kind",
        "line_type",
        "display_order",
        "source_order",
        "sampling_weight",
    )
    for key in merge_keys:
        if spec.get(key) is not None:
            out[key] = spec[key]
    out.setdefault("component_id", component_id)
    out.setdefault("generator_key", component_id)
    meta = dict(out.get("metadata") or {}) if isinstance(out.get("metadata"), dict) else {}
    for key in (
        "textbook_example_id",
        "component_id",
        "presentation_mode",
        "answer_type",
        "problem_type_id",
        "source_kind",
        "line_type",
        "semantic_answer",
    ):
        if out.get(key) is not None:
            meta.setdefault(key, out.get(key))
        elif spec.get(key) is not None:
            meta.setdefault(key, spec.get(key))
    if out.get("semantic_answer") is not None:
        meta.setdefault("semantic_answer", out.get("semantic_answer"))
    out["metadata"] = meta
    if not isinstance(out.get("answer_contract"), dict) or not out.get("answer_contract"):
        out["answer_contract"] = _minimal_answer_contract(out, spec)
    if out["answer_contract"].get("checker"):
        out["checker"] = out["answer_contract"].get("checker")
        out.setdefault("checker_type", out["answer_contract"].get("checker"))
    if out["answer_contract"].get("answer_equivalence"):
        out["equivalence"] = out["answer_contract"].get("answer_equivalence")
    return out


def generate(
    level: int = 1,
    seed: int | None = None,
    component_id: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    picked = _pick_component_id(seed=seed, component_id=component_id)
    module = _load_component_module(picked, "generate.py")
    generate_fn = getattr(module, "generate", None)
    if not callable(generate_fn):
        raise RuntimeError(f"component_generate_missing:{picked}")
    payload = generate_fn(level=level, seed=seed, component_id=picked, **kwargs)
    if isinstance(payload, dict):
        if not payload.get("component_id"):
            payload["component_id"] = picked
        return _merge_generator_spec(payload, picked)
    return payload


def check(
    user_answer: Any,
    correct_answer: Any,
    question_payload: dict[str, Any] | None = None,
) -> Any:
    payload = dict(question_payload or {})
    component_id = str(payload.get("component_id") or "")
    if component_id and component_id in _COMPONENT_DISPATCH:
        module = _load_component_module(component_id, "generate.py")
        check_fn = getattr(module, "check", None)
        if callable(check_fn):
            return check_fn(user_answer, correct_answer, payload)
    from core.gencode.runtime_skill_wrapper import check_answer

    return check_answer(user_answer, correct_answer, payload=payload)


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    payload = dict(question_payload or {})
    component_id = str(payload.get("component_id") or "")
    if component_id and component_id in _COMPONENT_DISPATCH:
        module = _load_component_module(component_id, "get_hint.py")
        hint_fn = getattr(module, "get_hint", None)
        if callable(hint_fn):
            from inspect import signature

            parameters = signature(hint_fn).parameters
            if "stage" in parameters and "question_payload" not in parameters:
                return str(hint_fn(payload, stage=step) or "")
            return str(hint_fn(step, payload) or "")
    return ""
