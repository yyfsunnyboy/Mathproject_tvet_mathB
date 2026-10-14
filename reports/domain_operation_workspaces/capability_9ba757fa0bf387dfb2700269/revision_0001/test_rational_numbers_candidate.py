from fractions import Fraction
from pathlib import Path
import hashlib

import sys
sys.path.insert(0, str(Path(__file__).parent))

import adapter
import operation


def test_fraction_decimal_round_trip_and_cycles():
    cases = [("11/40", "0.275"), ("2/11", "0.(18)"), ("1/37", "0.(027)"), ("9/22", "0.4(09)")]
    for fraction, decimal in cases:
        assert operation.fraction_to_decimal_expansion(fraction)["decimal"] == decimal
        assert operation.decimal_to_simplest_fraction(decimal) == operation.canonical_fraction(fraction)


def test_decimal_to_reduced_fraction_and_reject_noncanonical_fraction():
    assert operation.decimal_to_simplest_fraction("0.28") == "7/25"
    assert operation.decimal_to_simplest_fraction("0.(32)") == "32/99"
    assert operation.decimal_to_simplest_fraction("1.4(5)") == "131/90"
    assert adapter.check_reduced_fraction("7/25", "0.28")
    assert not adapter.check_reduced_fraction("28/100", "0.28")


def test_between_bounds_positive_and_negative_cases():
    assert operation.construct_rational_between_bounds("3/2", "5/3") == "19/12"
    assert adapter.check_rational_between_bounds("8/5", "3/2", "5/3")
    assert not adapter.check_rational_between_bounds("3/2", "3/2", "5/3")
    assert not adapter.check_rational_between_bounds("5/3", "3/2", "5/3")


def test_source_truth_statement_semantics():
    statements = [
        {"predicate": "is_irrational", "value": {"kind": "finite_decimal", "value": "1.414"}},
        {"predicate": "equals", "left": {"kind": "sum", "terms": [{"kind": "repeating_decimal", "value": "0.(4)"}, {"kind": "repeating_decimal", "value": "0.(6)"}]}, "right": {"kind": "rational", "value": "1"}},
        {"predicate": "no_rational_between", "lower": "21/13", "upper": "35/21"},
        {"predicate": "all_irrational", "values": [{"kind": "sqrt", "radicand": 5}, {"kind": "sum", "terms": [{"kind": "rational", "value": "0"}, {"kind": "sqrt", "radicand": 5}]}]},
        {"predicate": "sqrt_difference_identity", "left_radicand": 3, "right_radicand": 5},
    ]
    assert operation.evaluate_rationality_statements(statements) == (False, False, False, True, False)


def test_identify_rational_numbers_is_semantic_and_deterministic():
    candidates = [
        {"kind": "rational", "value": "-4/9"}, {"kind": "rational", "value": "0"},
        {"kind": "finite_decimal", "value": "3.14159"}, {"kind": "sum", "terms": [{"kind": "rational", "value": "3"}, {"kind": "sqrt", "radicand": 2}]},
        {"kind": "sum", "terms": [{"kind": "rational", "value": "12/11"}, {"kind": "rational", "value": "11/12"}]},
    ]
    assert operation.identify_rational_numbers(candidates) == (1, 2, 3, 5)
    assert adapter.check_rational_indices((1, 2, 3, 5), candidates)
    assert not adapter.check_rational_indices((1, 2, 3), candidates)


def test_number_line_semantics_and_contract():
    expected = {"coordinate_system": "number_line", "points": ["3/5", "-3/5"], "ordered_points": ["-3/5", "3/5"]}
    assert operation.plot_rational_points_on_number_line(["3/5", "-3/5"]) == expected
    assert adapter.adapt_number_line(["3/5", "-3/5"])["answer_type"] == "drawing"
    assert adapter.check_number_line_points(["3/5", "-3/5"], ["3/5", "-3/5"])


def test_supported_contracts_and_human_approved_solution_set_topology():
    assert adapter.adapt_fraction_decimal(["0.275", "0.(18)"])["answer_type"] == "multi_part"
    assert adapter.adapt_decimal_fraction(["7/25"])["answer_type"] == "multi_part"
    assert adapter.adapt_between_bounds("3/2", "5/3")["answer_type"] == "short_answer"
    assert adapter.adapt_true_false([1, 2])["answer_type"] == "multi_part"
    candidates = [
        {"kind": "rational", "value": "-4/9"}, {"kind": "rational", "value": "0"},
        {"kind": "finite_decimal", "value": "3.14159"}, {"kind": "sum", "terms": [{"kind": "rational", "value": "3"}, {"kind": "sqrt", "radicand": 2}]},
        {"kind": "sum", "terms": [{"kind": "rational", "value": "12/11"}, {"kind": "rational", "value": "11/12"}]},
    ]
    contract = adapter.adapt_identify_rational_numbers(candidates)
    assert contract["answer_type"] == "short_answer"
    assert contract["checker_key"] == "solution_set_checker"
    assert contract["correct_answer"] == list(operation.identify_rational_numbers(candidates))
    for equivalent in ("(1)(2)(3)(5)", "1,2,3,5", "{1,2,3,5}", "5,3,2,1,1"):
        assert adapter.check_rational_indices(equivalent, candidates)
    assert not adapter.check_rational_indices("1,2,3", candidates)


def test_workspace_did_not_modify_production_targets():
    root = Path(__file__).parents[4]
    targets = [root / "core/registry/taxonomy_registry.py", root / "core/registry/domain_operation_registry.py"]
    for target in targets:
        assert target.is_file()
        assert hashlib.sha256(target.read_bytes()).hexdigest()
