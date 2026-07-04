from implementation_candidate import build_linear_graph_feasibility_choice_matrix


def test_feasibility_choice_invariants() -> None:
    for seed in (7, 42, 101):
        matrix = build_linear_graph_feasibility_choice_matrix(seed=seed)
        facts = matrix["validation_facts"]
        condition = facts["graph_condition"]
        candidates = facts["candidate_lines"]
        assert len(candidates) == 4
        assert len({candidate["equation"] for candidate in candidates}) == 4
        for candidate in candidates:
            expected = (
                candidate["slope"] != 0
                and candidate["y_intercept"] == condition["required_y_intercept"]
            )
            assert candidate["feasible"] is expected
        impossible = [candidate for candidate in candidates if not candidate["feasible"]]
        assert len(impossible) == 1
        assert impossible[0]["equation"] == matrix["semantic_answer"]
        assert facts["choice_value_to_label"][matrix["semantic_answer"]] == facts["correct_label"]
        assert matrix["answer"]["correct_label"] == facts["correct_label"]
