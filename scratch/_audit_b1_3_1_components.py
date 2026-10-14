# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
inv = json.loads((ROOT / "scratch/_b1_3_1_readonly_inventory.json").read_text(encoding="utf-8"))


def grab(pat: str, text: str) -> str | None:
    m = re.search(pat, text)
    return m.group(1) if m else None


ops = []
missing_prod = []
incomplete = []
for i in inv:
    eid = i["textbook_example_id"]
    skill = i["skill_id"]
    prod = i["filesystem"]["prod"]
    if not prod["exists"]:
        missing_prod.append({"id": eid, "skill": skill})
        continue
    p = Path(prod["path"])
    if not (prod["generate"] and prod["metadata"] and prod["get_hint"]):
        incomplete.append({"id": eid, "skill": skill, "files": prod})
    meta = (p / "metadata.py").read_text(encoding="utf-8") if (p / "metadata.py").exists() else ""
    gen = (p / "generate.py").read_text(encoding="utf-8") if (p / "generate.py").exists() else ""
    pt = (
        grab(r"PROBLEM_TYPE_ID:\s*Final\[str\]\s*=\s*'([^']+)'", meta)
        or grab(r'PROBLEM_TYPE_ID:\s*Final\[str\]\s*=\s*"([^"]+)"', meta)
        or grab(r"PROBLEM_TYPE_ID\s*=\s*'([^']+)'", gen)
        or grab(r'PROBLEM_TYPE_ID\s*=\s*"([^"]+)"', gen)
    )
    op = (
        grab(r"DOMAIN_OPERATION:\s*Final\[str\]\s*=\s*'([^']+)'", meta)
        or grab(r'domain_operation\s*=\s*"([^"]+)"', gen)
        or grab(r"domain_operation\s*=\s*'([^']+)'", gen)
        or grab(r'line_type\s*=\s*"([^"]+)"', gen)
        or grab(r"line_type\s*=\s*'([^']+)'", gen)
    )
    ans = grab(r"ANSWER_TYPE:\s*Final\[str\]\s*=\s*'([^']+)'", meta)
    checker = grab(r"'checker_key':\s*'([^']+)'", meta) or grab(r'"checker_key":\s*"([^"]+)"', meta)
    ops.append(
        {
            "id": eid,
            "skill": skill,
            "PROBLEM_TYPE_ID": pt,
            "DOMAIN_OPERATION": op,
            "ANSWER_TYPE": ans,
            "checker_key": checker,
            "has_build_polynomial": "build_polynomial_matrix" in gen,
            "has_slot_generators": "generate_from_problem_type_spec" in gen or "slot_generators" in gen,
            "has_adapter": "convert_domain_matrix_to_question_payload" in gen,
            "source_description": i.get("source_description"),
            "problem_text_preview": i.get("problem_text_preview"),
        }
    )

out = {
    "missing_prod": missing_prod,
    "incomplete": incomplete,
    "pt_counts": dict(Counter(o["PROBLEM_TYPE_ID"] for o in ops)),
    "op_counts": dict(Counter(o["DOMAIN_OPERATION"] for o in ops)),
    "ans_counts": dict(Counter(o["ANSWER_TYPE"] for o in ops)),
    "checker_counts": dict(Counter(o["checker_key"] for o in ops)),
    "build_poly": sum(1 for o in ops if o["has_build_polynomial"]),
    "slot": sum(1 for o in ops if o["has_slot_generators"]),
    "adapter": sum(1 for o in ops if o["has_adapter"]),
    "ops": ops,
}
(ROOT / "scratch/_b1_3_1_component_ops.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps({k: v for k, v in out.items() if k != "ops"}, ensure_ascii=False, indent=2))
print("---OPS---")
for o in ops:
    kind = "poly" if o["has_build_polynomial"] else ("slot" if o["has_slot_generators"] else "other")
    print(f"{o['id']}\t{o['skill'].split('_')[-1]}\t{o['PROBLEM_TYPE_ID']}\t{o['DOMAIN_OPERATION']}\t{o['ANSWER_TYPE']}\t{o['checker_key']}\t{kind}")
print("---MISSING---")
print(missing_prod)
