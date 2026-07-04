from implementation_candidate import build_graph_based_linear_application_inverse_matrix


def test_inverse_linear_application_invariants() -> None:
    for seed in (7, 42, 101):
        matrix = build_graph_based_linear_application_inverse_matrix(seed=seed)
        facts = matrix["validation_facts"]
        assert facts["slope"] != 0
        assert facts["input_min"] <= facts["target_input"] <= facts["input_max"]
        assert facts["forward_output"] == facts["known_output"]
        assert facts["inverse_solution"] == facts["target_input"]
        assert facts["unique_solution"] is True
        assert matrix["answer"]["canonical_form"] == facts["target_input"]
        assert str(facts["known_output"]) in matrix["question"]
        assert all(
            y == facts["slope"] * x + facts["intercept"]
            for x, y in matrix["visual_spec"]["line"]["points"]
        )
