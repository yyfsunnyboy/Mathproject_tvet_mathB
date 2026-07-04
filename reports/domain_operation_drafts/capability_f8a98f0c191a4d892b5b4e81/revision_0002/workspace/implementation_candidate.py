import random

def graph_based_tiered_linear_application_multi_part(*, seed=None, constraints=None):
    r = random.Random(seed)
    tier1_rate = r.randint(2, 4)
    tier2_rate = r.randint(5, 8)
    limit = 10
    val1 = r.randint(1, limit - 1)
    val2 = r.randint(limit + 1, limit + 5)
    
    ans1 = val1 * tier1_rate
    ans2 = limit * tier1_rate + (val2 - limit) * tier2_rate
    
    parts = {
        "part_1": {
            "answer": str(ans1),
            "semantic_answer": ans1,
            "answer_type": "short_answer",
            "presentation_mode": "integer"
        },
        "part_2": {
            "answer": str(ans2),
            "semantic_answer": ans2,
            "answer_type": "short_answer",
            "presentation_mode": "integer"
        }
    }
    return {
        "question_text": f"A tiered pricing model charges {tier1_rate} dollars per unit up to {limit} units, and {tier2_rate} dollars per unit thereafter. (1) Find the cost of {val1} units. (2) Find the cost of {val2} units.",
        "answer": parts,
        "semantic_answer": parts,
        "answer_type": "multi_part",
        "presentation_mode": "multiple_inputs",
        "parts": parts,
        "metadata": {
            "parts": parts,
            "answer_dependencies": []
        }
    }
