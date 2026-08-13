# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

ROOT = Path(r"D:/Python/Mathproject_tvet_mathB")
INV = json.loads((ROOT / "reports/gencode_qwen_dryrun/_probe_preflight/b1_examples_inventory.json").read_text(encoding="utf-8"))

import sys
sys.path.insert(0, str(ROOT))
from core.registry.taxonomy_registry import resolve_domain_for_skill

ch2 = [x for x in INV if str(x.get("chapter") or "").startswith("2 ")]
print("ch2", len(ch2))

with_domain = []
without_domain = []
for x in ch2:
    sid = x["skill_id"]
    try:
        d = resolve_domain_for_skill(sid)
        x = dict(x)
        x["domain"] = {
            "fixed_domain_key": d.get("fixed_domain_key"),
            "ops": d.get("allowed_operations"),
            "module": d.get("domain_module"),
            "entrypoint": d.get("entrypoint"),
        }
        with_domain.append(x)
    except Exception as e:
        x = dict(x)
        x["domain_error"] = str(e)
        without_domain.append(x)

print("with_domain", len(with_domain), "without", len(without_domain))

# Among with_domain, find any not fully developed
print("\nWITH_DOMAIN status breakdown:")
from collections import Counter
c = Counter()
for x in with_domain:
    t = x.get("tracker") or {}
    st = (t.get("gencode_status") if t else None) or "no_tracker"
    c[(st, x["in_production"], x["in_dryrun"], x["skill_id"])] += 1
for k,v in c.most_common():
    print(v, k)

print("\nCandidates with domain AND not verified/published AND not prod:")
for x in with_domain:
    t = x.get("tracker") or {}
    st = str((t or {}).get("gencode_status") or "")
    if x["in_production"]:
        continue
    if st in {"verified", "published"}:
        continue
    print(x["id"], x["skill_id"], st, "dry", x["in_dryrun"], x["problem_text"][:120].replace("\n"," "))

print("\nWithout domain skill ids:")
print(sorted({x['skill_id'] for x in without_domain}))
print("With domain skill ids:")
print(sorted({x['skill_id'] for x in with_domain}))
