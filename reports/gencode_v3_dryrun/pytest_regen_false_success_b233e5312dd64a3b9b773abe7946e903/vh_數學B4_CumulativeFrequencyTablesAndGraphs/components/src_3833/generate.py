
def generate(seed=42, component_id=None, **kwargs):
    return {
        "question": f"Q{seed}-{component_id}-3833",
        "answer": "42",
        "problem_type_id": "frequency_table_construction_review",
        "domain_operation": "frequency_table_construction_review",
        "skill_id": "vh_數學B4_CumulativeFrequencyTablesAndGraphs",
        "component_id": component_id or "src_3833",
        "metadata": {"seed": seed},
    }
