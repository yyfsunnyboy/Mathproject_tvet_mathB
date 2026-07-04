from implementation_candidate import build_graph_based_linear_model_equation_matrix


def test_graph_model_invariants() -> None:
    for seed in (7, 42, 101):
        matrix = build_graph_based_linear_model_equation_matrix(seed=seed)
        facts = matrix["validation_facts"]
        assert facts["slope"] < 0
        assert facts["intercept"] > 0
        assert all(
            y == facts["slope"] * x + facts["intercept"]
            for x, y in facts["graph_points"]
        )
        assert matrix["visual_spec"]["points"] == facts["graph_points"]
        assert matrix["visual_spec"]["line"] == {
            "slope": facts["slope"],
            "intercept": facts["intercept"],
        }
        assert matrix["semantic_answer"] == facts["equation"]
        assert matrix["answer"]["canonical_form"] == facts["equation"]
