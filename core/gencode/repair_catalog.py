from __future__ import annotations

VERIFIER_REPAIR_CATALOG = {
    "interval_verifier": {
        "equivalence_type": "interval_set",
        "module_path": "core/verifiers/interval_verifier.py",
        "test_path": "tests/test_interval_verifier.py",
        "depends_on_checkers": ["interval_checker"],
        "factory": "create_interval_verifier",
        "implemented": True,
    },
    "choice_verifier": {
        "equivalence_type": "choice_label",
        "module_path": "core/verifiers/choice_verifier.py",
        "test_path": "tests/test_choice_verifier.py",
        "depends_on_checkers": ["choice_label_checker"],
        "factory": "create_choice_verifier",
        "implemented": True,
    },
    "solution_set_verifier": {
        "equivalence_type": "unordered_solution_set",
        "module_path": "core/verifiers/solution_set_verifier.py",
        "test_path": "tests/test_solution_set_verifier.py",
        "depends_on_checkers": ["solution_set_checker"],
        "factory": "create_solution_set_verifier",
        "implemented": False,
    },
    "rational_verifier": {
        "equivalence_type": "rational_equivalent",
        "module_path": "core/verifiers/rational_verifier.py",
        "test_path": "tests/test_rational_verifier.py",
        "depends_on_checkers": ["rational_checker"],
        "factory": "create_rational_verifier",
        "implemented": False,
    },
}

DOMAIN_FUNCTION_REPAIR_CATALOG = {
    "interval_domain_function": {
        "equivalence_type": "interval_set",
        "module_path": "core/domain/interval_domain_function.py",
        "test_path": "tests/test_interval_domain.py",
        "factory": "create_interval_domain_function",
        "implemented": True,
    },
    "interval_formatter": {
        "equivalence_type": "interval_set",
        "module_path": "core/domain/interval_formatter.py",
        "test_path": "tests/test_interval_domain.py",
        "factory": "create_interval_domain_function",
        "implemented": True,
    },
    "choices_unique_validator": {
        "equivalence_type": "choice_label",
        "module_path": "core/domain/choices_unique_validator.py",
        "test_path": "tests/test_choice_domain.py",
        "factory": "create_choice_domain_function",
        "implemented": True,
    },
}

GENERATOR_REPAIR_CATALOG = {
    "absolute_value_inequality_zero_center_basic": {
        "module_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_inequality_zero_center_basic/candidate_v1.py",
        "test_path": "tests/test_b1_absolute_value_inequality_generators.py",
        "factory": "create_abs_ineq_zero_center_generator",
        "required_domain_functions": ["interval_domain_function", "interval_formatter"],
        "required_checkers": ["interval_checker"],
        "required_verifiers": ["interval_verifier"],
    },
    "absolute_value_inequality_shifted_basic": {
        "module_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_inequality_shifted_basic/candidate_v1.py",
        "test_path": "tests/test_b1_absolute_value_inequality_generators.py",
        "factory": "create_abs_ineq_shifted_generator",
        "required_domain_functions": ["interval_domain_function", "interval_formatter"],
        "required_checkers": ["interval_checker"],
        "required_verifiers": ["interval_verifier"],
    },
    "absolute_value_inequality_linear_expression_basic": {
        "module_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_inequality_linear_expression_basic/candidate_v1.py",
        "test_path": "tests/test_b1_absolute_value_inequality_generators.py",
        "factory": "create_abs_ineq_linear_expression_generator",
        "required_domain_functions": ["interval_domain_function", "interval_formatter"],
        "required_checkers": ["interval_checker"],
        "required_verifiers": ["interval_verifier"],
    },
    "absolute_value_inequality_integer_solution_count_choice": {
        "module_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_inequality_integer_solution_count_choice/candidate_v1.py",
        "test_path": "tests/test_b1_absolute_value_inequality_generators.py",
        "factory": "create_abs_ineq_integer_solution_count_choice_generator",
        "required_domain_functions": ["choices_unique_validator", "interval_domain_function"],
        "required_checkers": ["choice_label_checker"],
        "required_verifiers": ["choice_verifier"],
    },
}

