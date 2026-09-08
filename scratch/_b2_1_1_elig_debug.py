# -*- coding: utf-8 -*-
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import Config
from core.gencode.services.v3_publish_eligibility import (
    component_publish_blockers,
    evaluate_v3_publish_eligibility,
    count_publish_eligible_components,
)
from core.gencode.skill_wrapper_compiler import _fetch_publish_eligible_components, _fetch_verified_components

conn = sqlite3.connect(Config.db_path)
conn.row_factory = sqlite3.Row
skill = "vh_數學B2_AngleMeasurementAndConversion"
print("eligibility", json.dumps(evaluate_v3_publish_eligibility(conn, skill), ensure_ascii=False, default=str, indent=2)[:2000])
print("counts", count_publish_eligible_components(conn, skill))
print("verified", len(_fetch_verified_components(conn, skill)))
print("eligible", len(_fetch_publish_eligible_components(conn, skill)))
row = conn.execute(
    "SELECT textbook_example_id, gencode_status, induced_spec_payload FROM gencode_component_tracker WHERE textbook_example_id=11606"
).fetchone()
print("status", row["gencode_status"])
payload = json.loads(row["induced_spec_payload"])
print("payload keys", sorted(payload))
print("blockers", component_publish_blockers(
    skill_id=skill,
    component_skill_id=skill,
    component_status="verified",
    spec=payload,
))
print("payload", json.dumps(payload, ensure_ascii=False, indent=2)[:1500])
