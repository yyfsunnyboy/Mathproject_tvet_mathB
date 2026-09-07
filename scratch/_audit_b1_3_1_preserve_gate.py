# -*- coding: utf-8 -*-
"""Read-only generation / contract audit for B1 3-1 existing components."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "scratch" / "_b1_3_1_preserve_audit.json"

ops_data = json.loads((ROOT / "scratch/_b1_3_1_component_ops.json").read_text(encoding="utf-8"))
existing = ops_data["ops"]

SKILL_PREFIX = {
    "polynomial_descending_power_properties": "vh_數學B1_PolynomialBasicConcepts",
    "polynomial_param_degree_constraint": "vh_數學B1_PolynomialBasicConcepts",
    "polynomial_descending_power_table": "vh_數學B1_PolynomialBasicConcepts",
    "zero_polynomial_find_coeffs": "vh_數學B1_PolynomialBasicConcepts",
    "polynomial_degree_product_sum": "vh_數學B1_PolynomialBasicConcepts",
    "polynomial_equality_identity": "vh_數學B1_PolynomialEquality",
}


def skill_for(row):
    return row.get("skill") or SKILL_PREFIX.get(row["PROBLEM_TYPE_ID"], "vh_數學B1_PolynomialArithmeticOperations")


def component_dir(skill: str, eid: int) -> Path:
    return ROOT / "agent_skills_v3" / skill / "components" / f"src_{eid}"


def git(*args: str) -> str:
    r = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return (r.stdout or "").strip()


def file_times(p: Path) -> dict:
    if not p.exists():
        return {}
    st = p.stat()
    return {
        "mtime": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
        "ctime": datetime.fromtimestamp(st.st_ctime).isoformat(timespec="seconds"),
        "size": st.st_size,
    }


def extract_literals(generate_text: str) -> dict:
    out = {
        "PROBLEM_TYPE_ID": None,
        "ANSWER_TYPE": None,
        "PRESENTATION_MODE": None,
        "selected_operation": None,
        "fixed_domain_key": None,
        "answer_contract": None,
        "checker_key": None,
        "equivalence_type": None,
        "classification_source": None,
        "has_placeholder": False,
        "has_NotImplemented": False,
        "has_pass_only": False,
        "uses_build_polynomial": "build_polynomial_matrix" in generate_text,
        "uses_adapter": "convert_domain_matrix_to_question_payload" in generate_text,
        "uses_slot_generators": "slot_generators" in generate_text or "from core.gencode.slot" in generate_text,
    }
    for key in ("PROBLEM_TYPE_ID", "ANSWER_TYPE", "PRESENTATION_MODE"):
        m = re.search(rf'^{key}\s*=\s*"([^"]*)"', generate_text, re.M)
        if m:
            out[key] = m.group(1)
    # embedded constraints
    for key in ("selected_operation", "fixed_domain_key", "classification_source"):
        # take first occurrence in generate
        ms = re.findall(rf"'{key}':\s*'([^']*)'", generate_text)
        if not ms:
            ms = re.findall(rf'"{key}":\s*"([^"]*)"', generate_text)
        if ms:
            # prefer non-empty if any
            nonempty = [x for x in ms if x.strip()]
            out[key] = nonempty[0] if nonempty else ms[0]
    # answer_contract blob
    m = re.search(r"'answer_contract':\s*(\{[^}]*\})", generate_text)
    if m:
        try:
            out["answer_contract"] = ast.literal_eval(m.group(1))
        except Exception:
            out["answer_contract"] = m.group(1)
    if isinstance(out["answer_contract"], dict):
        out["checker_key"] = out["answer_contract"].get("checker_key")
        out["equivalence_type"] = out["answer_contract"].get("equivalence_type")
        if not out["ANSWER_TYPE"]:
            out["ANSWER_TYPE"] = out["answer_contract"].get("answer_type")
    if "NotImplementedError" in generate_text:
        out["has_NotImplemented"] = True
    if re.search(r"\bTODO\b|FIXME|placeholder|PLACEHOLDER", generate_text, re.I):
        out["has_placeholder"] = True
    return out


def metadata_literals(meta_text: str) -> dict:
    out = {}
    for key in (
        "COMPONENT_ID",
        "TEXTBOOK_EXAMPLE_ID",
        "PROBLEM_TYPE_ID",
        "DOMAIN_OPERATION",
        "ANSWER_TYPE",
        "PRESENTATION_MODE",
        "GENERATOR_READINESS",
        "SKILL_ID",
    ):
        m = re.search(rf'^{key}:\s*Final\[[^\]]+\]\s*=\s*"([^"]*)"', meta_text, re.M)
        if not m:
            m = re.search(rf"^{key}:\s*Final\[[^\]]+\]\s*=\s*(\d+)", meta_text, re.M)
        if m:
            out[key] = m.group(1)
    m = re.search(r'"checker_key":\s*"([^"]+)"', meta_text)
    if m:
        out["checker_key"] = m.group(1)
    m = re.search(r'"equivalence_type":\s*"([^"]+)"', meta_text)
    if m:
        out["equivalence_type"] = m.group(1)
    return out


# --- age evidence ---
age_rows = []
for row in existing:
    eid = row["id"]
    skill = skill_for(row)
    cdir = component_dir(skill, eid)
    gen = cdir / "generate.py"
    meta = cdir / "metadata.py"
    hint = cdir / "get_hint.py"
    rel_gen = str(gen.relative_to(ROOT)).replace("\\", "/")
    first = git("log", "--diff-filter=A", "--format=%H|%ci|%s", "--", rel_gen)
    first_line = first.splitlines()[0] if first else ""
    last = git("log", "-1", "--format=%H|%ci|%s", "--", rel_gen)
    blame = git("blame", "-L", "1,5", "--line-porcelain", rel_gen)
    blame_sha = ""
    blame_date = ""
    for line in blame.splitlines():
        if line.startswith("author-time "):
            # skip
            pass
        if re.match(r"^[0-9a-f]{40}", line):
            blame_sha = line.split()[0]
        if line.startswith("author-time "):
            try:
                blame_date = datetime.fromtimestamp(int(line.split()[1])).isoformat(timespec="seconds")
            except Exception:
                pass
            break
    # dryrun
    dry = ROOT / "reports/gencode_v3_dryrun" / skill / "components" / f"src_{eid}" / "generate.py"
    age_rows.append(
        {
            "id": eid,
            "skill": skill,
            "pt": row["PROBLEM_TYPE_ID"],
            "fs_gen": file_times(gen),
            "fs_meta": file_times(meta),
            "git_first": first_line,
            "git_last": last,
            "blame_sha": blame_sha,
            "blame_date": blame_date,
            "dryrun_fs": file_times(dry) if dry.exists() else None,
            "gen_sha256": hashlib.sha256(gen.read_bytes()).hexdigest()[:12] if gen.exists() else None,
        }
    )

# sample one per problem_type
by_pt = defaultdict(list)
for row in existing:
    by_pt[row["PROBLEM_TYPE_ID"]].append(row)

samples = []
for pt, rows in sorted(by_pt.items()):
    row = rows[0]
    eid = row["id"]
    skill = skill_for(row)
    cdir = component_dir(skill, eid)
    gen_text = (cdir / "generate.py").read_text(encoding="utf-8")
    meta_text = (cdir / "metadata.py").read_text(encoding="utf-8")
    hint_text = (cdir / "get_hint.py").read_text(encoding="utf-8")
    g = extract_literals(gen_text)
    m = metadata_literals(meta_text)
    # smoke generate once
    smoke = {"ok": False, "error": None, "answer_type_runtime": None, "answer_topology": None, "seed_stable": None}
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(f"gen_{eid}", cdir / "generate.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        p1 = mod.generate(seed=42)
        p2 = mod.generate(seed=42)
        ans = p1.get("answer")
        if isinstance(ans, dict):
            topo = "dict_parts:" + ",".join(sorted(ans.keys()))
        elif isinstance(ans, list):
            topo = f"list_len_{len(ans)}"
        else:
            topo = type(ans).__name__
        smoke = {
            "ok": True,
            "error": None,
            "answer_type_runtime": p1.get("answer_type"),
            "presentation_mode_runtime": p1.get("presentation_mode"),
            "answer_topology": topo,
            "seed_stable": p1.get("answer") == p2.get("answer") and p1.get("question") == p2.get("question"),
            "has_question": bool(p1.get("question") or p1.get("question_text") or p1.get("stem")),
        }
        # checker quick
        try:
            from core.gencode.checker_registry import CHECKER_CAPABILITIES
            from core.checkers.structured_text_checker import check_expression  # may fail
        except Exception:
            pass
        checker_key = m.get("checker_key") or g.get("checker_key")
        smoke["checker_key_declared"] = checker_key
        # try validate_component_payload
        try:
            from core.gencode.services.v3_question_integrity_validator import validate_component_payload

            vr = validate_component_payload(p1, component_id=f"src_{eid}")
            smoke["integrity_ok"] = bool(vr.get("ok") if isinstance(vr, dict) else getattr(vr, "ok", None))
            if isinstance(vr, dict):
                smoke["integrity_errors"] = vr.get("errors") or vr.get("issues") or vr.get("reasons")
            else:
                smoke["integrity_errors"] = str(vr)[:200]
        except Exception as e:
            smoke["integrity_ok"] = False
            smoke["integrity_errors"] = f"validator_exception:{e}"
    except Exception as e:
        smoke = {"ok": False, "error": str(e)[:300]}

    # selected vs required
    required = m.get("DOMAIN_OPERATION") or m.get("PROBLEM_TYPE_ID") or g.get("PROBLEM_TYPE_ID")
    selected = g.get("selected_operation") or ""
    samples.append(
        {
            "problem_type_id": pt,
            "sample_id": eid,
            "skill": skill,
            "generate": g,
            "metadata": m,
            "hint_nonempty": bool(hint_text.strip()),
            "hint_has_NotImplemented": "NotImplementedError" in hint_text,
            "required_operation": required,
            "selected_operation": selected,
            "selected_matches_required": (selected == required) if selected else False,
            "selected_empty": not bool(selected),
            "answer_type_declared_generate": g.get("ANSWER_TYPE"),
            "answer_type_declared_metadata": m.get("ANSWER_TYPE"),
            "answer_contract": g.get("answer_contract"),
            "generator_readiness": m.get("GENERATOR_READINESS"),
            "component_id_ok": m.get("COMPONENT_ID") == f"src_{eid}" and str(m.get("TEXTBOOK_EXAMPLE_ID")) == str(eid),
            "smoke": smoke,
            "contract_vs_runtime": {
                "declared": g.get("ANSWER_TYPE") or m.get("ANSWER_TYPE"),
                "runtime": smoke.get("answer_type_runtime") if smoke.get("ok") else None,
                "topology": smoke.get("answer_topology") if smoke.get("ok") else None,
                "mismatch_expression_vs_multipart": (
                    (g.get("ANSWER_TYPE") == "expression" or m.get("ANSWER_TYPE") == "expression")
                    and isinstance(smoke.get("answer_topology"), str)
                    and smoke.get("answer_topology", "").startswith("dict_parts")
                )
                if smoke.get("ok")
                else None,
            },
        }
    )

# apply same static checks to ALL 31 (no smoke all to save time - but do smoke all for classification?)
# User wants classification of all 31 - need systematic checks. Smoke all 31.
all_class = []
for row in existing:
    eid = row["id"]
    skill = skill_for(row)
    cdir = component_dir(skill, eid)
    gen_text = (cdir / "generate.py").read_text(encoding="utf-8")
    meta_text = (cdir / "metadata.py").read_text(encoding="utf-8")
    g = extract_literals(gen_text)
    m = metadata_literals(meta_text)
    required = m.get("DOMAIN_OPERATION") or m.get("PROBLEM_TYPE_ID") or g["PROBLEM_TYPE_ID"]
    selected = g.get("selected_operation") or ""
    item = {
        "id": eid,
        "pt": row["PROBLEM_TYPE_ID"],
        "skill": skill,
        "component_id_ok": m.get("COMPONENT_ID") == f"src_{eid}",
        "one_to_one": (cdir / "generate.py").exists() and (cdir / "metadata.py").exists() and (cdir / "get_hint.py").exists(),
        "required": required,
        "selected": selected,
        "selected_empty": not bool(selected),
        "selected_match": selected == required if selected else False,
        "answer_type_gen": g.get("ANSWER_TYPE"),
        "answer_type_meta": m.get("ANSWER_TYPE"),
        "checker": m.get("checker_key") or g.get("checker_key"),
        "readiness": m.get("GENERATOR_READINESS"),
        "has_placeholder": g["has_placeholder"] or g["has_NotImplemented"],
        "uses_domain_adapter": g["uses_build_polynomial"] and g["uses_adapter"],
    }
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(f"gen_all_{eid}", cdir / "generate.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        p1 = mod.generate(seed=7)
        p2 = mod.generate(seed=7)
        ans = p1.get("answer")
        topo = (
            "dict_parts:" + ",".join(sorted(ans.keys()))
            if isinstance(ans, dict)
            else (f"list_{len(ans)}" if isinstance(ans, list) else type(ans).__name__)
        )
        declared = g.get("ANSWER_TYPE") or m.get("ANSWER_TYPE")
        runtime_at = p1.get("answer_type")
        mismatch = False
        if declared == "expression" and isinstance(ans, dict):
            mismatch = True
        if runtime_at and declared and runtime_at != declared:
            # runtime may upgrade to multi_part
            if not (declared == "expression" and runtime_at == "multi_part"):
                mismatch = True
            else:
                mismatch = True  # still topology mismatch vs declared expression
        from core.gencode.services.v3_question_integrity_validator import validate_component_payload

        vr = validate_component_payload(p1, component_id=f"src_{eid}")
        integrity_ok = bool(vr.get("ok")) if isinstance(vr, dict) else False
        item.update(
            {
                "smoke_ok": True,
                "seed_stable": p1.get("answer") == p2.get("answer"),
                "runtime_answer_type": runtime_at,
                "topology": topo,
                "contract_mismatch": mismatch,
                "integrity_ok": integrity_ok,
                "integrity_detail": (vr.get("errors") or vr.get("issues") or vr.get("failed_checks") or list(vr.keys())[:8])
                if isinstance(vr, dict)
                else None,
            }
        )
    except Exception as e:
        item.update({"smoke_ok": False, "smoke_error": str(e)[:250], "contract_mismatch": True, "integrity_ok": False})

    # classification heuristic for report (evidence-based)
    # KEEP only if nearly all preserve-gate items pass AND contract matches
    # Systemic issues: selected_empty, contract_mismatch, readiness draft vs manifest verified, no tracker
    fails = []
    if not item["one_to_one"]:
        fails.append("structure")
    if not item["component_id_ok"]:
        fails.append("component_id")
    if not item["required"]:
        fails.append("required_op")
    if item["selected_empty"] or not item["selected_match"]:
        fails.append("selected_operation")
    if item.get("contract_mismatch"):
        fails.append("answer_contract_topology")
    if not item.get("checker"):
        fails.append("checker")
    if item["has_placeholder"]:
        fails.append("placeholder")
    if not item.get("smoke_ok"):
        fails.append("smoke")
    if not item.get("seed_stable"):
        fails.append("seed")
    if not item.get("integrity_ok"):
        fails.append("validator")
    if item.get("readiness") == "draft":
        fails.append("lifecycle_draft_vs_verified_manifest")
    # mathematical invariant / wrong-answer reject: NOT proven this round -> mark as unproven
    item["unproven"] = ["correct_pass_wrong_reject", "mathematical_invariant", "tracker_record"]
    item["preserve_gate_fails"] = fails
    if not fails and not item["unproven"]:
        cls = "KEEP"
    elif "smoke" in fails or "structure" in fails or "component_id" in fails or "placeholder" in fails:
        cls = "REBUILD"
    elif any(
        x in fails
        for x in (
            "selected_operation",
            "answer_contract_topology",
            "validator",
            "lifecycle_draft_vs_verified_manifest",
        )
    ):
        # systemic contract generation issues -> REBUILD not KEEP
        cls = "REBUILD"
    else:
        cls = "UNKNOWN"
    # If core runtime works but contract systemic fail -> REBUILD
    # If evidence insufficient for invariant/checker polarity -> still REBUILD if contract fails; else UNKNOWN
    if cls == "KEEP":
        # cannot KEEP without proving §10.2 polarity — force UNKNOWN at best for unproven
        cls = "UNKNOWN"
    item["classification"] = cls
    all_class.append(item)

# manifests
manifests = {}
for skill in [
    "vh_數學B1_PolynomialBasicConcepts",
    "vh_數學B1_PolynomialArithmeticOperations",
    "vh_數學B1_PolynomialEquality",
]:
    p = ROOT / "agent_skills_v3" / skill / "component_manifest.json"
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        manifests[skill] = {
            "publish_status": data.get("publish_status"),
            "component_count": data.get("component_count"),
            "git": git("log", "-1", "--format=%H|%ci|%s", "--", str(p.relative_to(ROOT)).replace("\\", "/")),
            "fs": file_times(p),
            "has_generated_at": any(k for k in data.keys() if "time" in k.lower() or "at" in k.lower()),
            "keys": list(data.keys())[:20],
        }

# SOP v1.12 git
sop_flow = "docs/系統SOP/Gencode_AgentSkillV3整合/SOP_Gencode_AgentSkillV3_PipelineFlow.md"
sop_hist = git("log", "--format=%H|%ci|%s", "--", sop_flow)
# find when v1.12 appeared
v112 = git("log", "-S", "v1.12", "--format=%H|%ci|%s", "--", sop_flow)

payload = {
    "age_rows": age_rows,
    "unique_first_commits": sorted({(r["git_first"] or "").split("|")[0] for r in age_rows if r["git_first"]}),
    "samples": samples,
    "all_class": all_class,
    "counts": {
        "KEEP": sum(1 for x in all_class if x["classification"] == "KEEP"),
        "REBUILD": sum(1 for x in all_class if x["classification"] == "REBUILD"),
        "UNKNOWN": sum(1 for x in all_class if x["classification"] == "UNKNOWN"),
    },
    "manifests": manifests,
    "sop_v112_commits": v112.splitlines()[:10],
    "sop_recent": sop_hist.splitlines()[:8],
    "fail_freq": {},
}
for x in all_class:
    for f in x["preserve_gate_fails"]:
        payload["fail_freq"][f] = payload["fail_freq"].get(f, 0) + 1

OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print("counts", payload["counts"])
print("fail_freq", payload["fail_freq"])
print("first_commits", payload["unique_first_commits"])
print("sop_v112", payload["sop_v112_commits"][:5])
for s in samples:
    sm = s["smoke"]
    print(
        "SAMPLE",
        s["problem_type_id"],
        s["sample_id"],
        "sel_empty",
        s["selected_empty"],
        "mismatch",
        s["contract_vs_runtime"].get("mismatch_expression_vs_multipart"),
        "rt",
        sm.get("answer_type_runtime"),
        sm.get("answer_topology"),
        "integ",
        sm.get("integrity_ok"),
        "stable",
        sm.get("seed_stable"),
    )
