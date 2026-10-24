from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = 'gh_QuadraticFunctions'
GENERATOR_KEYS = ['src_12567', 'src_12569', 'src_12570', 'src_12571', 'src_12572', 'src_12573', 'src_12574', 'src_12575', 'src_12576', 'src_12577', 'src_12578', 'src_12579', 'src_12580', 'src_12581', 'src_12582', 'src_12583', 'src_12584', 'src_12585', 'src_12586', 'src_12587', 'src_12588', 'src_12589', 'src_12590', 'src_12591', 'src_12592', 'src_12593', 'src_12594', 'src_12595', 'src_12596', 'src_12597', 'src_12599', 'src_12600', 'src_12601', 'src_12602']
GENERATOR_SPECS = [{'textbook_example_id': 12567, 'component_id': 'src_12567', 'generator_key': 'src_12567', 'presentation_mode': 'canvas', 'response_mode': 'canvas', 'interaction_type': 'canvas', 'source_kind': 'example', 'line_type': 'graph_quadratic_functions', 'answer_type': 'drawing', 'answer_value_type': 'drawing', 'problem_type_id': 'graph_quadratic_functions', 'checker_key': 'free_response_drawing_checker', 'equivalence_type': None, 'display_order': 12567, 'source_order': 12567, 'sampling_weight': 10.0}, {'textbook_example_id': 12569, 'component_id': 'src_12569', 'generator_key': 'src_12569', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'complete_square_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'complete_square_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12569, 'source_order': 12569, 'sampling_weight': 10.0}, {'textbook_example_id': 12570, 'component_id': 'src_12570', 'generator_key': 'src_12570', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'graph_quadratic_functions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_quadratic_functions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12570, 'source_order': 12570, 'sampling_weight': 10.0}, {'textbook_example_id': 12571, 'component_id': 'src_12571', 'generator_key': 'src_12571', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'quadratic_extrema', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_extrema', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12571, 'source_order': 12571, 'sampling_weight': 10.0}, {'textbook_example_id': 12572, 'component_id': 'src_12572', 'generator_key': 'src_12572', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'quadratic_extrema', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_extrema', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12572, 'source_order': 12572, 'sampling_weight': 10.0}, {'textbook_example_id': 12573, 'component_id': 'src_12573', 'generator_key': 'src_12573', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_quadratic_applications', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_quadratic_applications', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12573, 'source_order': 12573, 'sampling_weight': 10.0}, {'textbook_example_id': 12574, 'component_id': 'src_12574', 'generator_key': 'src_12574', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_quadratic_applications', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_quadratic_applications', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12574, 'source_order': 12574, 'sampling_weight': 10.0}, {'textbook_example_id': 12575, 'component_id': 'src_12575', 'generator_key': 'src_12575', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_always_sign', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'quadratic_always_sign', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12575, 'source_order': 12575, 'sampling_weight': 10.0}, {'textbook_example_id': 12576, 'component_id': 'src_12576', 'generator_key': 'src_12576', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'graph_quadratic_functions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_quadratic_functions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12576, 'source_order': 12576, 'sampling_weight': 10.0}, {'textbook_example_id': 12577, 'component_id': 'src_12577', 'generator_key': 'src_12577', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_graph_transformations', 'answer_type': 'equation', 'answer_value_type': 'equation', 'problem_type_id': 'quadratic_graph_transformations', 'checker_key': 'equation_checker', 'equivalence_type': None, 'display_order': 12577, 'source_order': 12577, 'sampling_weight': 10.0}, {'textbook_example_id': 12578, 'component_id': 'src_12578', 'generator_key': 'src_12578', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'quadratic_graph_transformations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_graph_transformations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12578, 'source_order': 12578, 'sampling_weight': 10.0}, {'textbook_example_id': 12579, 'component_id': 'src_12579', 'generator_key': 'src_12579', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'complete_square_items', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'complete_square_items', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12579, 'source_order': 12579, 'sampling_weight': 10.0}, {'textbook_example_id': 12580, 'component_id': 'src_12580', 'generator_key': 'src_12580', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'quadratic_vertex_axis', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_vertex_axis', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12580, 'source_order': 12580, 'sampling_weight': 10.0}, {'textbook_example_id': 12581, 'component_id': 'src_12581', 'generator_key': 'src_12581', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_graph_transformations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_graph_transformations', 'checker_key': 'expression_checker', 'equivalence_type': None, 'display_order': 12581, 'source_order': 12581, 'sampling_weight': 10.0}, {'textbook_example_id': 12582, 'component_id': 'src_12582', 'generator_key': 'src_12582', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'quadratic_extrema', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_extrema', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12582, 'source_order': 12582, 'sampling_weight': 10.0}, {'textbook_example_id': 12583, 'component_id': 'src_12583', 'generator_key': 'src_12583', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_extrema', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'quadratic_extrema', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12583, 'source_order': 12583, 'sampling_weight': 10.0}, {'textbook_example_id': 12584, 'component_id': 'src_12584', 'generator_key': 'src_12584', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_quadratic_applications', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_quadratic_applications', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12584, 'source_order': 12584, 'sampling_weight': 10.0}, {'textbook_example_id': 12585, 'component_id': 'src_12585', 'generator_key': 'src_12585', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'quiz', 'line_type': 'solve_quadratic_applications', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_quadratic_applications', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12585, 'source_order': 12585, 'sampling_weight': 10.0}, {'textbook_example_id': 12586, 'component_id': 'src_12586', 'generator_key': 'src_12586', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'quiz', 'line_type': 'quadratic_always_sign', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'quadratic_always_sign', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12586, 'source_order': 12586, 'sampling_weight': 10.0}, {'textbook_example_id': 12587, 'component_id': 'src_12587', 'generator_key': 'src_12587', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'graph_quadratic_functions', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'graph_quadratic_functions', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12587, 'source_order': 12587, 'sampling_weight': 10.0}, {'textbook_example_id': 12588, 'component_id': 'src_12588', 'generator_key': 'src_12588', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'quadratic_graph_transformations', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_graph_transformations', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12588, 'source_order': 12588, 'sampling_weight': 10.0}, {'textbook_example_id': 12589, 'component_id': 'src_12589', 'generator_key': 'src_12589', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'quadratic_extrema', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'quadratic_extrema', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12589, 'source_order': 12589, 'sampling_weight': 10.0}, {'textbook_example_id': 12590, 'component_id': 'src_12590', 'generator_key': 'src_12590', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'quadratic_always_sign', 'answer_type': 'inequality', 'answer_value_type': 'inequality', 'problem_type_id': 'quadratic_always_sign', 'checker_key': 'inequality_solution_checker', 'equivalence_type': None, 'display_order': 12590, 'source_order': 12590, 'sampling_weight': 10.0}, {'textbook_example_id': 12591, 'component_id': 'src_12591', 'generator_key': 'src_12591', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'evaluate_function_statements', 'answer_type': 'solution_set', 'answer_value_type': 'solution_set', 'problem_type_id': 'evaluate_function_statements', 'checker_key': 'solution_set_checker', 'equivalence_type': None, 'display_order': 12591, 'source_order': 12591, 'sampling_weight': 10.0}, {'textbook_example_id': 12592, 'component_id': 'src_12592', 'generator_key': 'src_12592', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_quadratic_applications', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_quadratic_applications', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12592, 'source_order': 12592, 'sampling_weight': 10.0}, {'textbook_example_id': 12593, 'component_id': 'src_12593', 'generator_key': 'src_12593', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_quadratic_applications', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_quadratic_applications', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12593, 'source_order': 12593, 'sampling_weight': 10.0}, {'textbook_example_id': 12594, 'component_id': 'src_12594', 'generator_key': 'src_12594', 'presentation_mode': 'multiple_inputs', 'response_mode': 'multiple_inputs', 'interaction_type': 'multiple_inputs', 'source_kind': 'example', 'line_type': 'solve_quadratic_applications', 'answer_type': 'expression', 'answer_value_type': 'expression', 'problem_type_id': 'solve_quadratic_applications', 'checker_key': 'multi_part_answer_checker', 'equivalence_type': None, 'display_order': 12594, 'source_order': 12594, 'sampling_weight': 10.0}, {'textbook_example_id': 12595, 'component_id': 'src_12595', 'generator_key': 'src_12595', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_applications', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_quadratic_applications', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12595, 'source_order': 12595, 'sampling_weight': 10.0}, {'textbook_example_id': 12596, 'component_id': 'src_12596', 'generator_key': 'src_12596', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_applications', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_quadratic_applications', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12596, 'source_order': 12596, 'sampling_weight': 10.0}, {'textbook_example_id': 12597, 'component_id': 'src_12597', 'generator_key': 'src_12597', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_applications', 'answer_type': 'rational', 'answer_value_type': 'rational', 'problem_type_id': 'solve_quadratic_applications', 'checker_key': 'rational_checker', 'equivalence_type': None, 'display_order': 12597, 'source_order': 12597, 'sampling_weight': 10.0}, {'textbook_example_id': 12599, 'component_id': 'src_12599', 'generator_key': 'src_12599', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_function_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_function_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12599, 'source_order': 12599, 'sampling_weight': 10.0}, {'textbook_example_id': 12600, 'component_id': 'src_12600', 'generator_key': 'src_12600', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_function_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_function_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12600, 'source_order': 12600, 'sampling_weight': 10.0}, {'textbook_example_id': 12601, 'component_id': 'src_12601', 'generator_key': 'src_12601', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_function_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_function_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12601, 'source_order': 12601, 'sampling_weight': 10.0}, {'textbook_example_id': 12602, 'component_id': 'src_12602', 'generator_key': 'src_12602', 'presentation_mode': 'single_choice', 'response_mode': 'single_choice', 'interaction_type': 'single_choice', 'source_kind': 'example', 'line_type': 'evaluate_function_statements', 'answer_type': 'choice_label', 'answer_value_type': 'choice_label', 'problem_type_id': 'evaluate_function_statements', 'checker_key': 'choice_label_checker', 'equivalence_type': None, 'display_order': 12602, 'source_order': 12602, 'sampling_weight': 10.0}]
_COMPONENT_DISPATCH = {'src_12567': 'components/src_12567/generate.py', 'src_12569': 'components/src_12569/generate.py', 'src_12570': 'components/src_12570/generate.py', 'src_12571': 'components/src_12571/generate.py', 'src_12572': 'components/src_12572/generate.py', 'src_12573': 'components/src_12573/generate.py', 'src_12574': 'components/src_12574/generate.py', 'src_12575': 'components/src_12575/generate.py', 'src_12576': 'components/src_12576/generate.py', 'src_12577': 'components/src_12577/generate.py', 'src_12578': 'components/src_12578/generate.py', 'src_12579': 'components/src_12579/generate.py', 'src_12580': 'components/src_12580/generate.py', 'src_12581': 'components/src_12581/generate.py', 'src_12582': 'components/src_12582/generate.py', 'src_12583': 'components/src_12583/generate.py', 'src_12584': 'components/src_12584/generate.py', 'src_12585': 'components/src_12585/generate.py', 'src_12586': 'components/src_12586/generate.py', 'src_12587': 'components/src_12587/generate.py', 'src_12588': 'components/src_12588/generate.py', 'src_12589': 'components/src_12589/generate.py', 'src_12590': 'components/src_12590/generate.py', 'src_12591': 'components/src_12591/generate.py', 'src_12592': 'components/src_12592/generate.py', 'src_12593': 'components/src_12593/generate.py', 'src_12594': 'components/src_12594/generate.py', 'src_12595': 'components/src_12595/generate.py', 'src_12596': 'components/src_12596/generate.py', 'src_12597': 'components/src_12597/generate.py', 'src_12599': 'components/src_12599/generate.py', 'src_12600': 'components/src_12600/generate.py', 'src_12601': 'components/src_12601/generate.py', 'src_12602': 'components/src_12602/generate.py'}
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
