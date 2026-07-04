import random


def build_robust_budget_feasibility_choice_matrix(
    *,
    seed=None,
    constraints=None,
):
    normalized = dict(constraints or {})
    rng = random.Random(seed)
    lower_cost = int(normalized.get("lower_cost", rng.randrange(80, 151, 10)))
    higher_cost = int(
        normalized.get("higher_cost", lower_cost + rng.randrange(20, 81, 10))
    )
    first_quantity = int(normalized.get("first_quantity", rng.randint(8, 20)))
    second_quantity = int(normalized.get("second_quantity", rng.randint(8, 20)))

    def assignment_costs(first, second):
        return [
            lower_cost * first + higher_cost * second,
            higher_cost * first + lower_cost * second,
        ]

    baseline_costs = assignment_costs(first_quantity, second_quantity)
    budget = int(
        normalized.get("budget", max(baseline_costs) + rng.randrange(lower_cost))
    )
    quantity_pairs = [
        [first_quantity, second_quantity],
        [first_quantity + 1, second_quantity + 1],
        [first_quantity + 2, second_quantity + 2],
        [first_quantity + 3, second_quantity + 3],
    ]
    rng.shuffle(quantity_pairs)
    labels = ["A", "B", "C", "D"]
    candidates = []
    choices = []
    for label, pair in zip(labels, quantity_pairs):
        costs = assignment_costs(*pair)
        robust_feasible = max(costs) <= budget
        value = f"({pair[0]},{pair[1]})"
        candidates.append(
            {
                "quantities": pair,
                "assignment_costs": costs,
                "worst_case_cost": max(costs),
                "robust_feasible": robust_feasible,
                "value": value,
            }
        )
        choices.append({"label": label, "text": value, "value": value})
    correct_index = next(
        index
        for index, candidate in enumerate(candidates)
        if candidate["robust_feasible"]
    )
    correct_label = labels[correct_index]
    semantic_answer = candidates[correct_index]["value"]
    return {
        "question": (
            f"預算為 {budget} 元，兩種商品單價分別可能為 "
            f"{lower_cost} 元與 {higher_cost} 元，但尚不確定何者較貴。"
            "下列哪一組購買數量在兩種單價安排下都一定不超過預算？"
        ),
        "givens": {
            "budget": budget,
            "possible_unit_costs": [lower_cost, higher_cost],
            "cost_model": "c1*x+c2*y",
        },
        "answer": {"correct_label": correct_label},
        "semantic_answer": semantic_answer,
        "choices": choices,
        "distractors": [
            candidate["value"]
            for candidate in candidates
            if not candidate["robust_feasible"]
        ],
        "explanation_steps": [
            "每組數量都要計算兩種單價互換時的成本。",
            f"{semantic_answer} 的最壞情況成本仍不超過預算。",
        ],
        "validation_facts": {
            "budget_condition": {"operator": "<=", "limit": budget},
            "cost_model": {
                "possible_unit_costs": [lower_cost, higher_cost],
                "assignments": [
                    [lower_cost, higher_cost],
                    [higher_cost, lower_cost],
                ],
            },
            "candidate_plans": candidates,
            "feasibility_by_value": {
                candidate["value"]: candidate["robust_feasible"]
                for candidate in candidates
            },
            "correct_label": correct_label,
            "semantic_answer": semantic_answer,
            "choice_value_to_label": {
                choice["value"]: choice["label"] for choice in choices
            },
            "unique_choices": True,
            "unique_correct_choice": True,
        },
        "visual_spec": {"kind": "no_visual"},
        "answer_type": "single_choice",
        "presentation_mode": "single_choice",
        "topology_tags": [
            "linear_inequality",
            "uncertain_assignment",
            "robust_feasibility",
            "single_choice",
        ],
    }


robust_budget_feasibility_choice = build_robust_budget_feasibility_choice_matrix
