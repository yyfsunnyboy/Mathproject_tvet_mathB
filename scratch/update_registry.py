import yaml
from pathlib import Path

registry_path = Path("configs/generated_registry/b1_section_1_1_verified_registry.v0.1.yaml")

with open(registry_path, "r", encoding="utf-8") as f:
    reg = yaml.safe_load(f)

# 1. Add to verified_problem_types
vpt_entry = {
    "problem_type_id": "integer_numeric_evaluate_function_notation",
    "skill_id": "vh_數學B1_LinearFunction",
    "subskill_id": "integer_numeric_evaluate_function_notation",
    "status": "verified",
    "candidate_path": "generated_candidates/vocational_math_b1/section_1_2/integer_numeric_evaluate_function_notation/candidate_v1.py",
    "function_name": "generate",
    "answer_type": "integer",
    "checker_type": "integer_checker",
    "wrapper_path": "skills/vh_數學B1_LinearFunction.py",
    "manual_review_exclusions": ["unknown"],
    "source": "gencode_runtime_binding",
    "phase2_report_path": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_phase2_build.json"
}

# Remove existing if any
reg["verified_problem_types"] = [
    item for item in reg["verified_problem_types"]
    if not (item.get("skill_id") == "vh_數學B1_LinearFunction" and item.get("problem_type_id") == "integer_numeric_evaluate_function_notation")
]
reg["verified_problem_types"].append(vpt_entry)

# 2. Add or update runtime_bindings
rb_entry = {
    "skill_id": "vh_數學B1_LinearFunction",
    "wrapper_path": "skills/vh_數學B1_LinearFunction.py",
    "verified_problem_types": ["integer_numeric_evaluate_function_notation"],
    "manual_review_exclusions": ["unknown"],
    "candidate_paths": {
        "integer_numeric_evaluate_function_notation": "generated_candidates/vocational_math_b1/section_1_2/integer_numeric_evaluate_function_notation/candidate_v1.py"
    },
    "answer_contract_summary": {
        "integer_numeric_evaluate_function_notation": {
            "answer_type": "integer",
            "equivalence_type": "numeric_exact",
            "checker_key": "integer_checker",
            "order_matters": True,
            "accepted_format_notes": ["single integer answer"],
            "canonical_answer_schema": {"type": "integer"}
        }
    },
    "source": "gencode_runtime_binding",
    "phase2_report_path": "D:\\Python\\Mathproject_tvet_mathB\\reports\\gencode_closed_loop\\vh_數學B1_LinearFunction_phase2_build.json"
}

# Remove existing if any
reg["runtime_bindings"] = [
    item for item in reg["runtime_bindings"]
    if item.get("skill_id") != "vh_數學B1_LinearFunction"
]
reg["runtime_bindings"].append(rb_entry)

with open(registry_path, "w", encoding="utf-8") as f:
    yaml.safe_dump(reg, f, allow_unicode=True, sort_keys=False)

print("Registry updated successfully!")
