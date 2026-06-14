import json, sys
sys.stdout.reconfigure(encoding='utf-8')
path = 'reports/gencode_closed_loop/drafts/vh_數學B1_PropertiesOfPerpendicularLines_generator_draft_spec.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
p1 = data.get('phase1_payload', {})
print("candidate_problem_types:")
for pt in p1.get('candidate_problem_types', []):
    print(f"  ID: {pt.get('problem_type_id')}, Display: {pt.get('display_name')}, Checker: {pt.get('checker_type')}, Equivalence: {pt.get('answer_contract', {}).get('answer_equivalence')}")
