import pytest
from implementation_candidate import graph_based_tiered_linear_application_multi_part

def check_answer(student_ans, correct_ans, answer_type):
    if answer_type == "single_choice":
        return student_ans == correct_ans
    elif answer_type == "multi_part":
        return all(student_ans[k]["answer"] == correct_ans[k]["answer"] for k in correct_ans)
    elif answer_type == "drawing":
        return student_ans == correct_ans
    else:
        return str(student_ans).strip() == str(correct_ans).strip()

def test_operation_and_checker():
    for seed in [7, 42, 101]:
        payload = graph_based_tiered_linear_application_multi_part(seed=seed)
        assert "question_text" in payload
        assert "answer" in payload
        assert "semantic_answer" in payload
        assert "answer_type" in payload
        assert "presentation_mode" in payload
        
        ans_type = payload["answer_type"]
        correct = payload["answer"]
        
        # Positive assertion
        assert check_answer(correct, correct, ans_type) is True
        
        # Negative assertion (incorrect grading check)
        if ans_type == "single_choice":
            incorrect = "B" if correct == "A" else "A"
        elif ans_type == "multi_part":
            incorrect = dict(correct)
            for k in incorrect:
                incorrect[k] = dict(incorrect[k])
                incorrect[k]["answer"] = str(int(incorrect[k]["answer"]) + 1)
        elif ans_type == "drawing":
            incorrect = {"type": "wrong_line"}
        else:
            incorrect = str(int(correct) + 1) if correct.isdigit() else correct + "_wrong"
            
        assert check_answer(incorrect, correct, ans_type) is False
