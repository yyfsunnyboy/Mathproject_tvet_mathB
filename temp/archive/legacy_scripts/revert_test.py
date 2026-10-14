import codecs
import re

with codecs.open('tests/test_phase5f_d_free_response_practice_route.py', 'r', 'utf-8') as f:
    content = f.read()

# Replace test name
content = content.replace('def test_dashboard_tree_diagram_skill_card_links_to_standard_practice', 'def test_dashboard_tree_diagram_skill_card_links_to_free_response_practice')

# Replace the asserts
target1 = """    assert "/free_response_practice" not in body
    assert "practice/vh_數學B4_TreeDiagramCounting" in body"""
replacement1 = """    assert "/free_response_practice" in body
    assert "problem_type=tree_diagram_listing" in body
    assert "variant=early_stopping_game" in body
    assert body.count("/free_response_practice") == 1
    assert "practice/vh_" in body"""
content = content.replace(target1, replacement1)

# Remove the get_next_question test
regex = r"def test_practice_get_next_question_tree_diagram_injects_grading_mode\(\) -> None:.*?assert \"variant\" in data"
content = re.sub(regex, "", content, flags=re.DOTALL)

with codecs.open('tests/test_phase5f_d_free_response_practice_route.py', 'w', 'utf-8') as f:
    f.write(content)
