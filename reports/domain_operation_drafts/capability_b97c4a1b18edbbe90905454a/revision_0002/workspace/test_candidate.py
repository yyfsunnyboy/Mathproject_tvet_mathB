from implementation_candidate import (
    build_draw_constant_function_graph_matrix,
    evaluate_constant_function_line_graph,
)


def test_operation_and_checker() -> None:
    for seed in (7, 42, 101):
        matrix = build_draw_constant_function_graph_matrix(seed=seed)
        spec = matrix["expected_drawing_spec"]
        constant = matrix["givens"]["constant"]
        assert matrix["answer"] == matrix["semantic_answer"] == spec
        assert spec["slope"] == 0
        assert spec["y_intercept"] == constant
        assert spec["expected_line"]["points"][0][1] == constant
        assert spec["expected_line"]["points"][1][1] == constant
        assert str(constant) in matrix["question"]
        assert matrix["presentation_mode"] == "canvas"
        correct = {
            "required_elements": {"x_axis": True, "y_axis": True, "function_line": True},
            "line": {
                "detected": True,
                "slope": 0.02,
                "y_intercept": constant + 0.1,
                "spans_graph_width": True,
            },
            "confidence": 0.95,
        }
        wrong = {
            "required_elements": {"x_axis": True, "y_axis": True, "function_line": True},
            "line": {
                "detected": True,
                "slope": 1,
                "y_intercept": constant,
                "spans_graph_width": True,
            },
            "confidence": 0.95,
        }
        assert evaluate_constant_function_line_graph(correct, spec)["is_correct"] is True
        assert evaluate_constant_function_line_graph(wrong, spec)["is_correct"] is False
