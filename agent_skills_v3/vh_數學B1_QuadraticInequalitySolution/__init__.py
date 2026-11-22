from __future__ import annotations



import importlib.util

from pathlib import Path

from typing import Any



SKILL_ID = 'vh_數學B1_QuadraticInequalitySolution'

GENERATOR_KEYS = ['src_4474', 'src_4475', 'src_4476', 'src_4477', 'src_4478', 'src_4479', 'src_4481', 'src_4482', 'src_4483', 'src_4484', 'src_4485', 'src_4486', 'src_4487', 'src_4488', 'src_4489', 'src_4491', 'src_4492', 'src_4493', 'src_4494', 'src_4495', 'src_4496', 'src_4497', 'src_4498', 'src_4505', 'src_4506', 'src_4507', 'src_4508', 'src_4517', 'src_4518']

GENERATOR_SPECS = [{'textbook_example_id': 4474, 'component_id': 'src_4474', 'generator_key': 'src_4474', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'reverse_quadratic_inequality_coefficients', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_reverse_quadratic_inequality_coefficients', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4474, 'source_order': 4474, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4475, 'component_id': 'src_4475', 'generator_key': 'src_4475', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4475, 'source_order': 4475, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4476, 'component_id': 'src_4476', 'generator_key': 'src_4476', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'applied_quadratic_inequality_problem', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_applied_quadratic_inequality_problem', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4476, 'source_order': 4476, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4477, 'component_id': 'src_4477', 'generator_key': 'src_4477', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4477, 'source_order': 4477, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4478, 'component_id': 'src_4478', 'generator_key': 'src_4478', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4478, 'source_order': 4478, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4479, 'component_id': 'src_4479', 'generator_key': 'src_4479', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality_parameter_range', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality_parameter_range', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4479, 'source_order': 4479, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4481, 'component_id': 'src_4481', 'generator_key': 'src_4481', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4481, 'source_order': 4481, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4482, 'component_id': 'src_4482', 'generator_key': 'src_4482', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'reverse_quadratic_inequality_coefficients', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_reverse_quadratic_inequality_coefficients', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4482, 'source_order': 4482, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4483, 'component_id': 'src_4483', 'generator_key': 'src_4483', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4483, 'source_order': 4483, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4484, 'component_id': 'src_4484', 'generator_key': 'src_4484', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'applied_quadratic_inequality_problem', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_applied_quadratic_inequality_problem', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4484, 'source_order': 4484, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4485, 'component_id': 'src_4485', 'generator_key': 'src_4485', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4485, 'source_order': 4485, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4486, 'component_id': 'src_4486', 'generator_key': 'src_4486', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4486, 'source_order': 4486, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4487, 'component_id': 'src_4487', 'generator_key': 'src_4487', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality_parameter_range', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality_parameter_range', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4487, 'source_order': 4487, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4488, 'component_id': 'src_4488', 'generator_key': 'src_4488', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'applied_quadratic_inequality_problem', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_applied_quadratic_inequality_problem', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4488, 'source_order': 4488, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4489, 'component_id': 'src_4489', 'generator_key': 'src_4489', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4489, 'source_order': 4489, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4491, 'component_id': 'src_4491', 'generator_key': 'src_4491', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4491, 'source_order': 4491, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4492, 'component_id': 'src_4492', 'generator_key': 'src_4492', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4492, 'source_order': 4492, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4493, 'component_id': 'src_4493', 'generator_key': 'src_4493', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'reverse_quadratic_inequality_coefficients', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_reverse_quadratic_inequality_coefficients', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4493, 'source_order': 4493, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4494, 'component_id': 'src_4494', 'generator_key': 'src_4494', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4494, 'source_order': 4494, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4495, 'component_id': 'src_4495', 'generator_key': 'src_4495', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'applied_quadratic_inequality_problem', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_applied_quadratic_inequality_problem', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4495, 'source_order': 4495, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4496, 'component_id': 'src_4496', 'generator_key': 'src_4496', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4496, 'source_order': 4496, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4497, 'component_id': 'src_4497', 'generator_key': 'src_4497', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4497, 'source_order': 4497, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4498, 'component_id': 'src_4498', 'generator_key': 'src_4498', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality_parameter_range', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality_parameter_range', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4498, 'source_order': 4498, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4505, 'component_id': 'src_4505', 'generator_key': 'src_4505', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4505, 'source_order': 4505, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4506, 'component_id': 'src_4506', 'generator_key': 'src_4506', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_solve_quadratic_inequality', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4506, 'source_order': 4506, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4507, 'component_id': 'src_4507', 'generator_key': 'src_4507', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'reverse_quadratic_inequality_coefficients', 'answer_type': 'integer', 'answer_value_type': 'integer', 'problem_type_id': 'integer_reverse_quadratic_inequality_coefficients', 'checker_key': 'integer_checker', 'equivalence_type': 'numeric_exact', 'display_order': 4507, 'source_order': 4507, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4508, 'component_id': 'src_4508', 'generator_key': 'src_4508', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality_special_cases', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'rational_solve_quadratic_inequality_special_cases', 'checker_key': 'text_short_checker', 'equivalence_type': 'exact_string', 'display_order': 4508, 'source_order': 4508, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4517, 'component_id': 'src_4517', 'generator_key': 'src_4517', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'applied_quadratic_inequality_problem', 'answer_type': 'interval', 'answer_value_type': 'interval', 'problem_type_id': 'integer_applied_quadratic_inequality_problem', 'checker_key': 'interval_checker', 'equivalence_type': 'interval_equivalence', 'display_order': 4517, 'source_order': 4517, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}, {'textbook_example_id': 4518, 'component_id': 'src_4518', 'generator_key': 'src_4518', 'presentation_mode': 'short_answer', 'response_mode': 'short_answer', 'interaction_type': 'short_answer', 'source_kind': 'example', 'line_type': 'solve_quadratic_inequality_special_cases', 'answer_type': 'text_short', 'answer_value_type': 'text_short', 'problem_type_id': 'rational_solve_quadratic_inequality_special_cases', 'checker_key': 'text_short_checker', 'equivalence_type': 'exact_string', 'display_order': 4518, 'source_order': 4518, 'sampling_weight': 10.0, 'generator_readiness': 'runtime_ready'}]

_COMPONENT_DISPATCH = {'src_4474': 'components/src_4474/generate.py', 'src_4475': 'components/src_4475/generate.py', 'src_4476': 'components/src_4476/generate.py', 'src_4477': 'components/src_4477/generate.py', 'src_4478': 'components/src_4478/generate.py', 'src_4479': 'components/src_4479/generate.py', 'src_4481': 'components/src_4481/generate.py', 'src_4482': 'components/src_4482/generate.py', 'src_4483': 'components/src_4483/generate.py', 'src_4484': 'components/src_4484/generate.py', 'src_4485': 'components/src_4485/generate.py', 'src_4486': 'components/src_4486/generate.py', 'src_4487': 'components/src_4487/generate.py', 'src_4488': 'components/src_4488/generate.py', 'src_4489': 'components/src_4489/generate.py', 'src_4491': 'components/src_4491/generate.py', 'src_4492': 'components/src_4492/generate.py', 'src_4493': 'components/src_4493/generate.py', 'src_4494': 'components/src_4494/generate.py', 'src_4495': 'components/src_4495/generate.py', 'src_4496': 'components/src_4496/generate.py', 'src_4497': 'components/src_4497/generate.py', 'src_4498': 'components/src_4498/generate.py', 'src_4505': 'components/src_4505/generate.py', 'src_4506': 'components/src_4506/generate.py', 'src_4507': 'components/src_4507/generate.py', 'src_4508': 'components/src_4508/generate.py', 'src_4517': 'components/src_4517/generate.py', 'src_4518': 'components/src_4518/generate.py'}

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

        or payload.get("answer_value_type")

        or spec.get("answer_type")

        or spec.get("answer_value_type")

        or (payload.get("metadata") or {}).get("answer_type")

        or ("single_choice" if presentation_mode == "single_choice" else "expression")

    ).strip()

    semantic_answer = str(

        payload.get("semantic_answer")

        or (payload.get("metadata") or {}).get("semantic_answer")

        or payload.get("display_answer")

        or payload.get("correct_answer")

        or payload.get("answer")

        or ""

    ).strip()

    if presentation_mode == "single_choice" or answer_type in {"single_choice", "choice", "choice_label"}:

        return {

            "presentation_mode": "single_choice",

            "answer_type": "single_choice",

            "checker": "choice_label_checker",

            "checker_key": "choice_label_checker",

            "answer_equivalence": "choice_label",

            "equivalence": "choice_label",

            "semantic_answer": semantic_answer,

        }

    checker = str(

        spec.get("checker_key")

        or payload.get("checker_key")

        or payload.get("checker_type")

        or payload.get("checker")

        or (payload.get("metadata") or {}).get("checker_key")

        or ""

    ).strip()

    equivalence = str(

        spec.get("equivalence_type")

        or payload.get("equivalence_type")

        or payload.get("answer_equivalence")

        or payload.get("equivalence")

        or (payload.get("metadata") or {}).get("equivalence_type")

        or ""

    ).strip()

    try:

        from core.gencode.answer_contract_gate import _DEFAULT_CONTRACT_BY_ANSWER_TYPE



        default_eq, default_ck = _DEFAULT_CONTRACT_BY_ANSWER_TYPE.get(answer_type, ("", ""))

    except Exception:

        default_eq, default_ck = ("", "")

    if not equivalence:

        equivalence = str(default_eq or "").strip() or "exact_string"

    if not checker:

        checker = str(default_ck or "").strip() or "text_short_checker"

    # Guard: never keep equation checker for non-equation answer types.

    if checker == "linear_equation_equivalent_checker" and answer_type not in {

        "equation",

        "linear_equation",

        "expression",

    }:

        checker = str(default_ck or "").strip() or "text_short_checker"

        equivalence = str(default_eq or "").strip() or equivalence

    return {

        "presentation_mode": presentation_mode or "short_answer",

        "answer_type": answer_type,

        "checker": checker,

        "checker_key": checker,

        "answer_equivalence": equivalence,

        "equivalence": equivalence,

        "semantic_answer": semantic_answer,

    }





def _merge_generator_spec(payload: dict[str, Any], component_id: str) -> dict[str, Any]:

    if not isinstance(payload, dict):

        return payload

    spec = _spec_for_component(component_id)

    out = dict(payload)

    identity_keys = (

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

    contract_keys = (

        "answer_type",

        "answer_value_type",

        "checker_key",

        "equivalence_type",

    )

    for key in identity_keys:

        if spec.get(key) is not None:

            out[key] = spec[key]

    for key in contract_keys:

        if spec.get(key) is not None:

            out.setdefault(key, spec[key])

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

        "checker_key",

        "equivalence_type",

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
