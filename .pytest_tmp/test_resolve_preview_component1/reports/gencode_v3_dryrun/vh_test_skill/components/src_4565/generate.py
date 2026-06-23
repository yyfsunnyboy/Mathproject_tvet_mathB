def generate(seed=42):
    return {
        "question_text": f"What is 1 + 1? (seed={seed})",
        "choices": [],
        "answer_contract": {
            "answer_type": "short_answer",
            "checker_key": "exact_match",
        },
        "correct_answer": "2",
        "metadata": {"problem_type_id": "addition_test"}
    }
