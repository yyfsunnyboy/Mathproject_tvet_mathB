import pytest

from implementation_candidate import (
    build_robust_budget_feasibility_choice_matrix,
)


@pytest.mark.parametrize("seed", [7, 42, 101])
def test_robust_budget_invariants(seed):
    matrix = build_robust_budget_feasibility_choice_matrix(seed=seed)
    facts = matrix["validation_facts"]
    budget = facts["budget_condition"]["limit"]
    candidates = facts["candidate_plans"]
    assert len({candidate["value"] for candidate in candidates}) == 4
    for candidate in candidates:
        assert candidate["worst_case_cost"] == max(
            candidate["assignment_costs"]
        )
        assert candidate["robust_feasible"] is (
            candidate["worst_case_cost"] <= budget
        )
    feasible = [
        candidate for candidate in candidates if candidate["robust_feasible"]
    ]
    assert len(feasible) == 1
    assert feasible[0]["value"] == matrix["semantic_answer"]
    assert (
        facts["choice_value_to_label"][matrix["semantic_answer"]]
        == facts["correct_label"]
    )
