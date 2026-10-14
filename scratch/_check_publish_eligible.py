# -*- coding: utf-8 -*-
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path('.').resolve()))

from core.gencode.services.v3_production_publish_service import count_publish_eligible_components

conn = sqlite3.connect("instance/kumon_math.db")
conn.row_factory = sqlite3.Row

for eid in [4706, 4716, 4717, 4718, 4719, 4720, 4612]:
    r = conn.execute(
        "SELECT textbook_example_id, skill_id, gencode_status, gencode_error_log, induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id=?",
        (eid,),
    ).fetchone()
    d = dict(r)
    payload = d.get("induced_spec_payload")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception:
            pass
    print("=" * 40, eid, d["gencode_status"])
    if isinstance(payload, dict):
        print({k: payload.get(k) for k in sorted(payload.keys()) if k in {
            "component_id","integrity_gate_passed","fixed_domain_key","domain_operation","selected_operation",
            "problem_type_id","answer_type","presentation_mode","generator_readiness","rebuild_decision"
        }})
    else:
        print("payload", type(payload), str(payload)[:200])

for skill in [
    "vh_數學B1_PolynomialArithmeticOperations",
    "vh_數學B1_PolynomialBasicConcepts",
    "vh_數學B1_PolynomialEquality",
]:
    try:
        c = count_publish_eligible_components(conn, skill)
        print("ELIGIBLE", skill, c)
    except Exception as e:
        print("ELIGIBLE_ERR", skill, e)
        # fallback list verified
        rows = conn.execute(
            "SELECT textbook_example_id, gencode_status FROM gencode_component_tracker WHERE skill_id=? ORDER BY textbook_example_id",
            (skill,),
        ).fetchall()
        print([(r["textbook_example_id"], r["gencode_status"]) for r in rows])
