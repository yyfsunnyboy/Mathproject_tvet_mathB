import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
summary_path = root / "reports" / "gencode_closed_loop" / "vh_數學B1_LinearFunction_phase1_summary.json"

if summary_path.exists():
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    print("candidate_problem_types:")
    for pt in data.get("candidate_problem_types", []):
        print(f" - problem_type_id: {pt.get('problem_type_id') or pt.get('proposed_problem_type_id')}")
        print(f"   checker_key_proposal: {pt.get('checker_key_proposal')}")
        print(f"   equivalence_type_proposal: {pt.get('equivalence_type_proposal')}")
        print(f"   answer_contract_proposal: {pt.get('answer_contract_proposal')}")
    
    print("\nanswer_contract_summary keys:")
    print(data.get("answer_contract_summary", {}).keys())
    print("\nobserved_problem_type_answer_contracts:")
    print(data.get("answer_contract_summary", {}).get("observed_problem_type_answer_contracts"))
else:
    print("Summary file not found.")
