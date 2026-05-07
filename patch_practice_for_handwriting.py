import re
import codecs

with codecs.open('core/routes/practice.py', 'r', 'utf-8') as f:
    content = f.read()

# 1. Remove vh_數學B4_TreeDiagramCounting from MANUAL_REVIEW_SKILLS
regex1 = r"\"vh_數學B4_TreeDiagramCounting\":\s*\{.*?\},\s*(?=\"vh_數學B4_PascalTriangle\")"
content = re.sub(regex1, '', content, flags=re.DOTALL)

# 2. Intercept mod.generate in get_next_question (around line 738)
regex2 = r"(for attempt in range\(max_retries\):\s*try:\s*# \[.*?\] .*?\s*)(data = mod\.generate\(level=difficulty_level\))"
replacement2 = r"""\1if skill_id == "vh_數學B4_TreeDiagramCounting":
                    from core.vocational_math_b4.free_response.tree_diagram_judge import build_tree_diagram_listing_payload
                    import random
                    variant = random.choice(["fixed_stage_binary_tree", "early_stopping_game"])
                    payload = build_tree_diagram_listing_payload(variant)
                    data = {
                        "question_text": payload["question_text"],
                        "correct_answer": "",
                        "expected_paths": payload["expected_paths"],
                        "answer_type": "handwriting",
                        "problem_type": payload["problem_type_id"],
                        "grading_mode": payload["grading_mode"],
                        "variant": payload["variant"],
                        "path_labels": payload.get("path_labels", [])
                    }
                else:
                    \2"""
content = re.sub(regex2, replacement2, content, count=1, flags=re.DOTALL)

# Also ensure get_adaptive_question is intercepted similarly (if it's used)
regex3 = r"(try:\s*)(data = mod\.generate\(\*\*gen_kwargs\))"
replacement3 = r"""\1if skill_id_for_generate == "vh_數學B4_TreeDiagramCounting":
            from core.vocational_math_b4.free_response.tree_diagram_judge import build_tree_diagram_listing_payload
            import random
            variant = random.choice(["fixed_stage_binary_tree", "early_stopping_game"])
            payload = build_tree_diagram_listing_payload(variant)
            data = {
                "question_text": payload["question_text"],
                "correct_answer": "",
                "expected_paths": payload["expected_paths"],
                "answer_type": "handwriting",
                "problem_type": payload["problem_type_id"],
                "grading_mode": payload["grading_mode"],
                "variant": payload["variant"],
                "path_labels": payload.get("path_labels", [])
            }
        else:
            \2"""
content = re.sub(regex3, replacement3, content, count=1, flags=re.DOTALL)

with codecs.open('core/routes/practice.py', 'w', 'utf-8') as f:
    f.write(content)
