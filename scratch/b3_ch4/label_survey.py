"""Survey every Ch4 family: multipart part labels vs stem items."""
import glob
import importlib
import json
import re
from collections import defaultdict

rows = defaultdict(set)
dup_ops = defaultdict(int)
box_ops = defaultdict(int)
samples = {}
seen_ops = set()
for comp in sorted(glob.glob("agent_skills_v3/vh_數學B3_SubSection_4_*/components/src_*/generate.py")):
    parts = comp.replace("\\", "/").split("/")
    mod = importlib.import_module(f"agent_skills_v3.{parts[1]}.components.{parts[3]}.generate")
    op = mod.PROBLEM_TYPE_ID
    for seed in range(4):
        p = mod.generate(seed=seed)
        contract = p.get("answer_contract") or {}
        cparts = contract.get("parts") or []
        if len(cparts) < 2:
            continue
        seen_ops.add(op)
        items = [str(i.get("text") or "") for i in (p.get("stem_structure") or {}).get("items") or []]
        for part in cparts:
            label = str(part.get("display_label") or part.get("label") or part.get("prompt") or "")
            rows[op].add((str(part.get("key")), label if len(label) < 30 else label[:30] + "…"))
            if label in items or (len(label) > 12 and any(label and label in it for it in items)):
                dup_ops[op] += 1
                samples.setdefault(op, (mod.TEXTBOOK_EXAMPLE_ID, part.get("key"), label))
            if "□" in label:
                box_ops[op] += 1
print("multipart ops:", len(seen_ops))
print("ops with duplicated stem in label:", len(dup_ops))
for op in sorted(seen_ops):
    flag = ("DUP " if op in dup_ops else "    ") + ("BOX " if op in box_ops else "    ")
    keys = sorted({k for k, _ in rows[op]})
    labels = sorted({l for _, l in rows[op]})[:4]
    print(flag, op, keys, json.dumps(labels, ensure_ascii=False)[:160])
