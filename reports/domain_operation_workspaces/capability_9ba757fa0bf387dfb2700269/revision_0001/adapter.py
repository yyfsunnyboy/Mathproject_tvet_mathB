"""Isolated answer contracts and exact checkers for the rational-number candidate."""

from operation import (
    canonical_fraction, fraction_to_decimal_expansion, identify_rational_numbers,
    is_strictly_between, parse_exact_rational, plot_rational_points_on_number_line,
)


def check_decimal_expansion(answer, expected):
    try:
        return parse_exact_rational(answer) == parse_exact_rational(expected)
    except (TypeError, ValueError, ZeroDivisionError):
        return False


def check_reduced_fraction(answer, expected):
    try:
        text = str(answer).strip()
        return "/" in text and canonical_fraction(text) == canonical_fraction(expected) and text.replace(" ", "") == canonical_fraction(text)
    except (TypeError, ValueError, ZeroDivisionError):
        return False


def check_rational_between_bounds(answer, lower, upper):
    try:
        return is_strictly_between(answer, lower, upper)
    except (TypeError, ValueError, ZeroDivisionError):
        return False


def check_boolean_sequence(answer, expected):
    return tuple(bool(value) for value in answer) == tuple(bool(value) for value in expected)


def check_rational_indices(answer, candidates):
    """Delegate unordered candidate-index grading to the production shared checker."""
    from core.checkers.solution_set_checker import check_solution_set_answer

    return check_solution_set_answer(answer, identify_rational_numbers(candidates))


def check_number_line_points(answer, expected_points):
    try:
        return tuple(canonical_fraction(point) for point in answer) == tuple(canonical_fraction(point) for point in expected_points)
    except (TypeError, ValueError, ZeroDivisionError):
        return False


def adapt_fraction_decimal(parts):
    return {"answer_type": "multi_part", "checker": "decimal_expansion", "parts": tuple(parts)}


def adapt_decimal_fraction(parts):
    return {"answer_type": "multi_part", "checker": "reduced_fraction", "parts": tuple(parts)}


def adapt_number_line(points):
    return {"answer_type": "drawing", "drawing_type": "number_line", "semantic_target": plot_rational_points_on_number_line(points)}


def adapt_between_bounds(lower, upper):
    return {"answer_type": "short_answer", "checker": "rational_between_bounds", "bounds": (canonical_fraction(lower), canonical_fraction(upper))}


def adapt_true_false(statements):
    return {"answer_type": "multi_part", "checker": "boolean_sequence", "statement_count": len(statements)}


def adapt_identify_rational_numbers(candidates):
    """Human-approved short-answer topology for textbook example 12280.

    The canonical set is derived from the shared domain operation; no textbook
    example ID or fixed answer labels are used as an oracle.
    """
    return {
        "answer_type": "short_answer",
        "presentation_mode": "short_answer",
        "checker_key": "solution_set_checker",
        "equivalence_type": "unordered_solution_set",
        "answer_shape": "selected_candidate_index_set",
        "correct_answer": list(identify_rational_numbers(candidates)),
    }
