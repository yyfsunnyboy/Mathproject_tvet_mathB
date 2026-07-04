from implementation_candidate import build_draw_linear_function_graph_matrix


def _evaluate_line_graph(recognized: dict, expected: dict) -> bool:
    line = recognized["line"]
    tolerance = expected["tolerance"]
    return (
        line["detected"]
        and line["spans_graph_width"]
        and abs(line["slope"] - expected["slope"]) <= tolerance["slope"]
        and abs(line["y_intercept"] - expected["y_intercept"])
        <= tolerance["y_intercept"]
    )


def test_operation_and_checker() -> None:
    for seed in (7, 42, 101):
        matrix = build_draw_linear_function_graph_matrix(seed=seed)
        spec = matrix["expected_drawing_spec"]
        slope = matrix["givens"]["slope"]
        intercept = matrix["givens"]["y_intercept"]
        assert slope != 0
        assert spec["slope"] == slope
        assert spec["y_intercept"] == intercept
        assert matrix["answer"] == matrix["semantic_answer"] == spec
        assert matrix["visual_spec"]["axis_range"] == spec["axis_range"]
        assert all(y == slope * x + intercept for x, y in spec["expected_line"]["points"])
        assert spec["equation"] in matrix["givens"]["linear_function_equation"]
        correct = {
            "line": {
                "detected": True,
                "slope": slope + 0.02,
                "y_intercept": intercept + 0.1,
                "spans_graph_width": True,
            }
        }
        wrong = {
            "line": {
                "detected": True,
                "slope": -slope,
                "y_intercept": intercept,
                "spans_graph_width": True,
            }
        }
        assert _evaluate_line_graph(correct, spec) is True
        assert _evaluate_line_graph(wrong, spec) is False
