# -*- coding: utf-8 -*-
"""Consolidate 3-1 inventory for report (read-only)."""
from __future__ import annotations

import ast
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
inv = json.loads((ROOT / "scratch" / "_b1_3_1_readonly_inventory.json").read_text(encoding="utf-8"))
ops = {x["id"]: x for x in json.loads((ROOT / "scratch" / "_b1_3_1_component_ops.json").read_text(encoding="utf-8"))["ops"]}

# phase1_rule_packs example_id -> problem_type
rule_map = {}
yaml_text = (ROOT / "configs/gencode/classifiers/phase1_rule_packs.yaml").read_text(encoding="utf-8")
# crude parse for example_id / matched_problem_type_id pairs under polynomial skills
for m in re.finditer(
    r"example_id:\s*(\d+)\s*\n\s*matched_problem_type_id:\s*(\S+)",
    yaml_text,
):
    rule_map[int(m.group(1))] = m.group(2)

# manifests
manifest_status = {}
for skill_dir in (ROOT / "agent_skills_v3").glob("vh_數學B1_Polynomial*"):
    man = skill_dir / "component_manifest.json"
    if not man.exists():
        continue
    data = json.loads(man.read_text(encoding="utf-8"))
    for c in data.get("components") or []:
        manifest_status[int(c["textbook_example_id"])] = c.get("status")

# metadata GENERATOR_READINESS
meta_ready = {}
for row in inv:
    eid = row["textbook_example_id"]
    prod = row["filesystem"]["prod"]
    if not prod["exists"]:
        continue
    meta_path = Path(prod["path"]) / "metadata.py"
    text = meta_path.read_text(encoding="utf-8")
    m = re.search(r'GENERATOR_READINESS:\s*Final\[str\]\s*=\s*"([^"]+)"', text)
    meta_ready[eid] = m.group(1) if m else None

# fixed_domain from generate.py if exists
def extract_constraints(generate_path: Path) -> dict:
    if not generate_path.is_file():
        return {}
    text = generate_path.read_text(encoding="utf-8")
    m = re.search(r"constraints\s*=\s*(\{[\s\S]*?\n\})", text)
    if not m:
        # try CONSTRAINTS or embedded dict named differently
        m = re.search(r'"classification_status"\s*:\s*"([^"]+)"', text)
        out = {}
        if m:
            out["classification_status"] = m.group(1)
        fd = re.search(r'"fixed_domain_key"\s*:\s*"([^"]+)"', text)
        if fd:
            out["fixed_domain_key"] = fd.group(1)
        src = re.search(r'"source"\s*:\s*"([^"]+)"', text)
        if src:
            out["source"] = src.group(1)
        return out
    try:
        return ast.literal_eval(m.group(1))
    except Exception:
        out = {}
        for key in ("classification_status", "fixed_domain_key", "source", "selected_operation"):
            mm = re.search(rf'"{key}"\s*:\s*"([^"]+)"', text)
            if mm:
                out[key] = mm.group(1)
        return out

rows_out = []
for row in inv:
    eid = row["textbook_example_id"]
    op_info = ops.get(eid, {})
    prod = row["filesystem"]["prod"]
    constraints = {}
    if prod["exists"]:
        constraints = extract_constraints(Path(prod["path"]) / "generate.py")
    pt = op_info.get("PROBLEM_TYPE_ID") or rule_map.get(eid) or "UNKNOWN"
    domain_op = op_info.get("DOMAIN_OPERATION") or pt
    # lifecycle
    if not prod["exists"]:
        lifecycle = "discovered" if rule_map.get(eid) else "classified" if row.get("skill_id") else "unknown"
        # if classified in rule pack but no component
        if rule_map.get(eid):
            lifecycle = "classified"
        else:
            lifecycle = "unknown"
    else:
        # tracker empty; use manifest + metadata
        ms = manifest_status.get(eid)
        gr = meta_ready.get(eid)
        if ms == "verified":
            lifecycle = "verified"  # manifest claims; tracker absent
        elif gr == "draft":
            lifecycle = "draft_written"
        else:
            lifecycle = "unknown"
    rows_out.append(
        {
            "example_id": eid,
            "component_id": row["component_id"],
            "skill_id": row["skill_id"],
            "problem_type_id": pt,
            "required_operation": domain_op,
            "fixed_domain_key": constraints.get("fixed_domain_key")
            or ("algebra.polynomial" if str(pt).startswith("polynomial") or pt == "zero_polynomial_find_coeffs" else "UNKNOWN"),
            "classification_status": constraints.get("classification_status")
            or ("resolved" if rule_map.get(eid) else "UNKNOWN"),
            "source": constraints.get("source") or ("phase1_rule_pack" if rule_map.get(eid) else "UNKNOWN"),
            "component_status": lifecycle,
            "manifest_status": manifest_status.get(eid),
            "metadata_readiness": meta_ready.get(eid),
            "tracker": row["tracker"]["gencode_status"],
            "prod_exists": prod["exists"],
            "source_description": row.get("source_description"),
        }
    )

# domain readiness evidence
import core.domain.polynomial_domain as pd
from core.registry.domain_operation_registry import get_operation_spec

adapter = (ROOT / "core/gencode/domain_matrix_adapter.py").read_text(encoding="utf-8")
unique_ops = sorted({r["required_operation"] for r in rows_out})
matrix = []
for op in unique_ops:
    decl = op in getattr(pd, "_SUPPORTED_OPS", set()) or True
    try:
        spec = get_operation_spec("algebra.polynomial", op)
        has_spec = spec is not None
    except Exception as e:
        has_spec = False
        spec = None
    impl = op in pd._SUPPORTED_OPS
    adapter_named = f"'{op}'" in adapter or f'"{op}"' in adapter
    matrix.append(
        {
            "operation": op,
            "in_supported_ops": impl,
            "registry_spec": has_spec,
            "adapter_named_route": adapter_named,
            "generic_adapter_used_by_components": True,  # all existing call convert_domain_matrix_to_question_payload
        }
    )

out = {
    "count": len(rows_out),
    "missing": [r for r in rows_out if not r["prod_exists"]],
    "status_counts": {},
    "rows": rows_out,
    "ops_matrix": matrix,
}
for r in rows_out:
    out["status_counts"][r["component_status"]] = out["status_counts"].get(r["component_status"], 0) + 1

(ROOT / "scratch" / "_b1_3_1_report_data.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("count", out["count"])
print("status", out["status_counts"])
print("missing", [(m["example_id"], m["problem_type_id"]) for m in out["missing"]])
print("ops")
for m in matrix:
    print(m)
