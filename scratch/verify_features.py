import sys
from core.gencode.example_feature_extractor import extract_example_feature_rule_only

# Mock Example 4531
ex_4531 = {
    "id": 4531,
    "problem_text": "設$A\\left( -2,a \\right)$、$B\\left( 3,4 \\right)$、$C\\left( -2,8 \\right)$、$D\\left( 4,-2 \\right)$，若$\\overline{AB}$與$\\overline{CD}$垂直，試求a之值。",
    "correct_answer": None
}

feat_4531 = extract_example_feature_rule_only(ex_4531)
print("Example 4531 Extracted Features:")
print(f"  answer_type: {feat_4531.get('answer_type')}")
print(f"  target_task: {feat_4531.get('target_task')}")
print(f"  task_family: {feat_4531.get('task_family')}")
print(f"  checker: {feat_4531.get('checker')}")
print("-" * 50)

# Mock Keyword Rules
ex_keyword_acbc = {
    "id": 9991,
    "problem_text": "在坐標平面上，滿足 AC = BC 的點C...",
    "correct_answer": "5"
}

feat_acbc = extract_example_feature_rule_only(ex_keyword_acbc)
print("AC = BC Keyword Extracted Features:")
print(f"  answer_type: {feat_acbc.get('answer_type')}")
print(f"  target_task: {feat_acbc.get('target_task')}")
print(f"  task_family: {feat_acbc.get('task_family')}")
print(f"  checker: {feat_acbc.get('checker')}")
print("-" * 50)

ex_keyword_求x = {
    "id": 9992,
    "problem_text": "求 x = 的值...",
    "correct_answer": "3/2"
}

feat_求x = extract_example_feature_rule_only(ex_keyword_求x)
print("求 x = Keyword Extracted Features:")
print(f"  answer_type: {feat_求x.get('answer_type')}")
print(f"  target_task: {feat_求x.get('target_task')}")
print(f"  task_family: {feat_求x.get('task_family')}")
print(f"  checker: {feat_求x.get('checker')}")
print("-" * 50)

# Mock TVET Math B Hard Constraints on contract remapping
from core.gencode.phase1_report_contract import remap_legacy_fields

cand_mock = {
    "problem_type_id": "text_short_solve_unknown",
    "answer_type": "text_short",
    "answer_contract_proposal": {
        "answer_type": "text_short",
        "checker_key": "text_short_checker"
    },
    "problem_type_spec_draft": {
        "problem_type_id": "text_short_solve_unknown",
        "source_example_ids": [4531] # Example 4531 is in vh_數學B1_PropertiesOfPerpendicularLines (Linear Equations)
    }
}

remapped_cand = remap_legacy_fields(cand_mock, skill_id="vh_數學B1_PropertiesOfPerpendicularLines")
print("Remapped Candidate under TVET Math B constraints:")
print(f"  problem_type_id: {remapped_cand.get('problem_type_id')}")
print(f"  answer_type: {remapped_cand.get('answer_type')}")
print(f"  checker_key_proposal: {remapped_cand.get('checker_key_proposal')}")
print(f"  answer_contract_proposal: {remapped_cand.get('answer_contract_proposal')}")
print("-" * 50)
