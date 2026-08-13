# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(r"D:/Python/Mathproject_tvet_mathB")
DB = ROOT / "instance" / "kumon_math.db"
INV = ROOT / "reports" / "gencode_qwen_dryrun" / "_probe_preflight" / "b1_examples_inventory.json"

data = json.loads(INV.read_text(encoding="utf-8"))
ch2 = [x for x in data if str(x.get("chapter") or "").startswith("2 ")]
print("ch2_total", len(ch2))

# status summary
from collections import Counter
st = Counter()
for x in ch2:
    t = x.get("tracker") or {}
    status = t.get("gencode_status") if t else "no_tracker"
    key = f"{status}|prod={x['in_production']}|dry={x['in_dryrun']}"
    st[key] += 1
print("STATUS")
for k, v in st.most_common():
    print(v, k)

# Undeveloped: not production, not dryrun, tracker missing or not verified/published/generating done
skip_status = {
    "verified",
    "published",
    "ready_to_publish",
    "generating",
    "needs_human_review",  # maybe skip reconcile-ish
}
undeveloped = []
for x in ch2:
    t = x.get("tracker") or {}
    status = str((t or {}).get("gencode_status") or "").strip()
    if x["in_production"] or x["in_dryrun"]:
        continue
    if status in skip_status:
        continue
    # skip choice-like stems
    text = x.get("problem_text") or ""
    if any(tok in text for tok in ("(A)", "(B)", "（A）", "（B）", "下列何者", "哪個")):
        continue
    undeveloped.append(x)

print("undeveloped_count", len(undeveloped))
# group by skill
by_skill = {}
for x in undeveloped:
    by_skill.setdefault(x["skill_id"], []).append(x)
for sid, rows in sorted(by_skill.items(), key=lambda kv: len(kv[1])):
    print(f"\nSKILL {sid} n={len(rows)}")
    for r in rows[:5]:
        print(" ", r["id"], (r.get("tracker") or {}).get("gencode_status"), r["problem_text"][:100].replace("\n", " "))

# Domain capability check
from core.registry.taxonomy_registry import resolve_domain_for_skill

print("\nDOMAIN CHECK")
for sid in sorted(by_skill):
    try:
        d = resolve_domain_for_skill(sid)
        print(sid, "OK", d.get("fixed_domain_key"), "ops", len(d.get("allowed_operations") or []), d.get("domain_module"), d.get("entrypoint"))
    except Exception as e:
        print(sid, "FAIL", e)
