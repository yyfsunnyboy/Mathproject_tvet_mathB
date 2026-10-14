# -*- coding: utf-8 -*-
import json
import sqlite3
from pathlib import Path

rows = json.loads(Path("scratch/_b2_1_1_reclassify_report.json").read_text(encoding="utf-8"))
print("source_provided", sum(1 for r in rows if r.get("oracle_source") == "source"))
print("domain_operation", sum(1 for r in rows if r.get("oracle_source") == "domain_operation"))
print("sf_pass", sum(1 for r in rows if r.get("source_fidelity") == "PASS"))
print("verified", sum(1 for r in rows if r.get("final_status") == "verified"))
print("old_mgt", sum(1 for r in rows if "missing_ground_truth" in str(r.get("old_error") or "")))
for r in rows:
    print(
        r["example_id"],
        r["source_fidelity"],
        r["oracle_source"],
        r["oracle_operation"],
        r["exact_ready"],
        r["answer_type"],
        r["checker"],
        r["20_seed"],
        r["final_status"],
        r["reason"],
        r["old_status"],
    )
conn = sqlite3.connect("instance/kumon_math.db")
print("---tracker---")
for rec in conn.execute(
    "SELECT textbook_example_id, gencode_status, gencode_error_log FROM gencode_component_tracker "
    "WHERE textbook_example_id BETWEEN 11606 AND 11625 ORDER BY 1"
):
    print(rec)
