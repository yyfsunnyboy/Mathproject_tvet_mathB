import yaml
from pathlib import Path

# Path to the catalog source file
yaml_path = Path("agent_skills_v2/_generated/vh_數學B1_LinearFunction/examples_map_absolute_value.yaml")

# Load existing content
with open(yaml_path, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

target_ids = {4424, 4433, 4434, 4441, 4444, 4448, 4449, 4516}

for entry in data.get("examples", []):
    if entry.get("example_id") in target_ids:
        entry["problem_type_id"] = "integer_numeric_evaluate_function_notation"
        entry["subskill_id"] = "integer_numeric_evaluate_function_notation"
        entry["runtime_category"] = "deterministic"
        entry["semantic_audit_status"] = "pass"
        entry["generator_status"] = "production"
        entry["semantic_risk_flags"] = []
        entry["manual_review_reason"] = ""

# Save updated content
with open(yaml_path, "w", encoding="utf-8") as f:
    yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

print("examples_map_absolute_value.yaml updated successfully!")
