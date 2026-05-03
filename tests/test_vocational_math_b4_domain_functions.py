import pytest

from core.vocational_math_b4.domain.binomial_domain_functions import (
    binomial_coefficient_sum,
    binomial_expansion_coefficients,
    binomial_term_coefficient,
    pascal_identity,
    pascal_triangle_row,
)
from core.vocational_math_b4.domain.b4_validators import (
    validate_answer_in_choices,
    validate_choices_unique,
    validate_expression_answer,
    validate_integer_answer,
    validate_n_ge_r,
    validate_no_unfilled_placeholder,
    validate_nonnegative_integer,
    validate_parameter_tuple_not_seen,
    validate_polynomial_answer,
    validate_positive_integer,
    validate_problem_payload_contract,
)
from core.vocational_math_b4.domain.counting_domain_functions import (
    addition_principle_count,
    adjacent_arrangement_count,
    combination,
    combination_equation_solve_n,
    digit_arrangement_count,
    divisor_count_from_prime_factorization,
    enumeration_count,
    factorial,
    factorial_ratio_solve_n,
    multiplication_principle_count,
    non_adjacent_arrangement_count,
    permutation,
    polygon_diagonal_count,
    polygon_triangle_count,
    repeated_assignment_count,
    repeated_choice_count,
    repeated_digit_arrangement_count,
)


def test_counting_domain_functions_happy_path() -> None:
    assert addition_principle_count([3, 4, 5]) == 12
    assert multiplication_principle_count([3, 4, 5]) == 60
    assert factorial(5) == 120
    assert factorial(0) == 1
    assert factorial_ratio_solve_n(0, -1, 6) == 6
    assert permutation(5, 2) == 20
    assert combination(5, 2) == 10
    assert repeated_choice_count(3, 4) == 81
    assert repeated_digit_arrangement_count(5, 3, True, None) == 125
    assert repeated_assignment_count(3, 4, True) == 64
    assert divisor_count_from_prime_factorization([2, 1, 3]) == 24
    assert digit_arrangement_count([1, 2, 3, 4, 5], 3, False, False, "odd") == 36
    assert adjacent_arrangement_count(5, 2, True) == 48
    assert non_adjacent_arrangement_count(5, 2, True) == 72
    assert polygon_diagonal_count(6) == 9
    assert polygon_triangle_count(6) == 20
    assert combination_equation_solve_n(2, 10) == 5
    assert enumeration_count([2, 2, 2]) == 8


def test_binomial_domain_functions_happy_path() -> None:
    assert pascal_identity(5, 2) == 20
    assert binomial_coefficient_sum(5) == 32
    assert binomial_expansion_coefficients(1, 2, 3) == [1, 6, 12, 8]
    assert binomial_term_coefficient(1, 2, 3, 2) == 6
    assert pascal_triangle_row(5) == [1, 5, 10, 10, 5, 1]


def test_validators_happy_path() -> None:
    valid_payload = {
        "question_text": "Q",
        "choices": ["A", "B", "C"],
        "answer": "A",
        "explanation": "E",
        "skill_id": "s",
        "subskill_id": "ss",
        "problem_type_id": "pt",
        "generator_key": "g",
        "difficulty": "easy",
        "diagnosis_tags": ["tag"],
        "remediation_candidates": ["cand"],
        "source_style_refs": ["ref"],
    }

    assert validate_positive_integer(3) is True
    assert validate_nonnegative_integer(0) is True
    assert validate_n_ge_r(5, 2) is True
    assert validate_choices_unique(["A", "B", "C"]) is True
    assert validate_answer_in_choices("A", ["A", "B", "C"]) is True
    assert validate_no_unfilled_placeholder("正常題目") is True
    assert validate_integer_answer("12") is True
    assert validate_expression_answer("2x+3") is True
    assert validate_polynomial_answer("x^2+2x+1") is True
    assert validate_parameter_tuple_not_seen((1, 2), {(2, 3)}) is True
    assert validate_problem_payload_contract(valid_payload) is True


def test_invalid_inputs_raise_value_error() -> None:
    with pytest.raises(ValueError):
        addition_principle_count([])
    with pytest.raises(ValueError):
        factorial(-1)
    with pytest.raises(ValueError):
        permutation(2, 5)
    with pytest.raises(ValueError):
        validate_no_unfilled_placeholder("題目有[BLANK]")
    with pytest.raises(ValueError):
        validate_problem_payload_contract({"question_text": "Q"})
    with pytest.raises(ValueError):
        validate_choices_unique(["A", "A"])
