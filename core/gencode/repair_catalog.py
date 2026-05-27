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

